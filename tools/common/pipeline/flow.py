"""Flow pipeline: AI scenes rendered by Google Flow (Omni), product shots from real photos."""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Optional, Sequence

from tools.common.constants import MIN_FLOW_CLIP_BYTES, SCENE_TAIL_PAD_SECONDS
from tools.common.ffmpeg import file_is_ready, try_probe_duration
from tools.common.flow_client import FlowJob, FlowKitClient, PollResult, download, extract_frame
from tools.common.media.extractor import create_image_slide_clip, extract_vertical_subclip
from tools.common.models import SceneDefinition
from tools.common.pipeline.context import PlatformHooks, ProductWorkspace, RunOptions, open_workspace, print_banner
from tools.common.pipeline.local import pick_image, resolve_delogo
from tools.common.pipeline.selection import SceneSelection
from tools.common.pipeline.steps import assemble_scenes, load_storyboard, narrate, package_outputs, print_summary
from tools.common.settings import PlatformProfile

logger = logging.getLogger(__name__)

AI_KINDS = ("FLOW_AI", "AI")
PHOTO_KINDS = ("PRODUCT_PHOTO", "IMAGE_SLIDE")

# Omni render request
OMNI_CLIP_SECONDS = 6
OMNI_ASPECT_RATIO = "VIDEO_ASPECT_RATIO_PORTRAIT"
OMNI_RESOLUTION = "720p"
SUBMIT_SPACING_SECONDS = 2.0  # pause between submissions so Flow does not throttle
POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 600
MAX_REFERENCE_UPLOADS = 2
ANCHOR_FRAME_SECONDS = 1.2

# Styles whose AI scenes never show a face.
FACELESS_STYLES = frozenset({"faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov"})
# Prompt phrases marking a scene as faceless (the first three also mark a whole storyboard).
FACELESS_MARKERS = ("no face", "hands only", "no human face")
CLOSEUP_MARKERS = ("macro", "top-down", "overhead")
PRODUCT_MARKERS = ("hands", "product")
HUMAN_WORDS = ("person", "professional", "creator", "homemaker", "model", "man", "woman", "same", "persona", "actor", "traveler")
_HUMAN_RE = re.compile(r"\b(" + "|".join(map(re.escape, HUMAN_WORDS)) + r")\b")


def _prompt(scene: SceneDefinition) -> str:
    return (scene.prompt or "").lower()


def is_faceless_storyboard(style: str, ai_scenes: Sequence[SceneDefinition]) -> bool:
    if style in FACELESS_STYLES:
        return True
    return bool(ai_scenes) and all(any(m in _prompt(s) for m in FACELESS_MARKERS) for s in ai_scenes)


def is_faceless_scene(scene: SceneDefinition, faceless_storyboard: bool) -> bool:
    prompt = _prompt(scene)
    return faceless_storyboard or any(m in prompt for m in FACELESS_MARKERS + CLOSEUP_MARKERS)


def is_human_scene(scene: SceneDefinition, faceless_storyboard: bool) -> bool:
    return not is_faceless_scene(scene, faceless_storyboard) and bool(_HUMAN_RE.search(_prompt(scene)))


def wants_product_reference(scene: SceneDefinition, faceless_storyboard: bool) -> bool:
    if not scene.use_product_ref or scene.image_index is None or scene.image_index < 0:
        return False
    return is_faceless_scene(scene, faceless_storyboard) or any(m in _prompt(scene) for m in PRODUCT_MARKERS)


def _render_request(prompt: str, project_id: str, reference: Optional[str] = None) -> dict:
    payload = {
        "prompt": prompt,
        "project_id": project_id,
        "duration_s": OMNI_CLIP_SECONDS,
        "aspect_ratio": OMNI_ASPECT_RATIO,
        "resolution": OMNI_RESOLUTION,
    }
    if reference:
        payload["reference_media_ids"] = [reference]
    return payload


class FlowRenderer:
    """Submits AI scenes to Flow, keeps a consistent character, downloads the clips."""

    def __init__(self, client: FlowKitClient, workspace: ProductWorkspace, opts: RunOptions, project_id: str):
        self.client = client
        self.workspace = workspace
        self.opts = opts
        self.project_id = project_id
        self.selection: SceneSelection = opts.selection
        self.force = opts.regen or opts.force_storyboard

    def clip_path(self, scene_id: int) -> Path:
        return self.workspace.clips_dir / f"{self.opts.style}_raw_{scene_id:02d}.mp4"

    def _needs_render(self, scene_id: int) -> bool:
        ready = file_is_ready(self.clip_path(scene_id), MIN_FLOW_CLIP_BYTES)
        return not self.selection.keep_existing(scene_id, ready, force_rebuild=self.force)

    def _submit(self, scene: SceneDefinition, reference: Optional[str]) -> FlowJob:
        payload = _render_request(scene.prompt, self.project_id, reference)
        if reference:
            res = self.client.submit_reference_video(payload)
            op_name = res.get("operations", [{}])[0].get("operation", {}).get("name")
            logger.info("Scene %s submitted (r2v): op_name=%s", scene.id, op_name)
            return {"scene_id": scene.id, "type": "operation", "op_name": op_name, "project_id": self.project_id}
        res = self.client.submit_text_video(payload)
        workflow = res.get("workflows", [{}])[0]
        logger.info("Scene %s submitted (t2v): media_id=%s", scene.id, workflow.get("primary_media_id"))
        return {"scene_id": scene.id, "type": "workflow", "workflow": workflow, "primary_media_id": workflow.get("primary_media_id")}

    def _collect(self, jobs: Sequence[FlowJob]) -> PollResult:
        result = self.client.poll_jobs(jobs, poll_interval_s=POLL_INTERVAL_SECONDS, timeout_s=POLL_TIMEOUT_SECONDS)
        for sid, url in sorted(result.urls.items()):
            logger.info("  ⬇️ Đang tải AI clip Scene %s (%s)...", sid, self.clip_path(sid).name)
            download(url, self.clip_path(sid))
        return result

    def render_character_anchor(self, scene: SceneDefinition) -> Optional[str]:
        """Render scene 1 first and upload a frame of it as the identity reference for later scenes."""
        if self._needs_render(scene.id):
            logger.info("  • Đang gửi Scene %s (Anchor Nhân Vật): %s...", scene.id, scene.overlay_title)
            logger.info("  ⏳ Chờ sinh video Scene 1 để trích xuất khuôn mặt nhân vật chuẩn (~35s)...")
            self._collect([self._submit(scene, reference=None)]).raise_for_failures()
        try:
            logger.info("  🎯 [Nhân Vật Nhất Quán] Đang trích xuất frame chân dung nhân vật từ Scene 1...")
            anchor = extract_frame(self.clip_path(scene.id), self.workspace.clips_dir / f"{self.opts.style}_character_anchor.jpg", ANCHOR_FRAME_SECONDS)
            media_id = self.client.upload_image(anchor, project_id=self.project_id)
            logger.info("  ✅ [Nhân Vật Nhất Quán] Đã upload Anchor Frame lên Flow -> media_id: %s", media_id)
            return media_id
        except Exception as exc:  # anchor is best-effort: scenes still render without it
            logger.warning("Không thể trích xuất / upload character anchor: %s", exc)
            return None

    def render(self, ai_scenes: Sequence[SceneDefinition], product_refs: Sequence[str]) -> None:
        faceless = is_faceless_storyboard(self.opts.style, ai_scenes)
        mode = "Phong cách POV / Hands-On 100% Không Lộ Mặt" if faceless else "Bảo đảm nhân vật nhất quán"
        logger.info("\n🎬 [Bước 4/5] Gửi yêu cầu sinh Video AI tới Google Flow (%s)...", mode)

        anchor_scene = next((s for s in ai_scenes if s.id == 1), ai_scenes[0] if ai_scenes else None)
        character = self.render_character_anchor(anchor_scene) if anchor_scene and not faceless else None

        jobs: list[FlowJob] = []
        for scene in ai_scenes:
            if not faceless and scene is anchor_scene:
                continue
            if not self._needs_render(scene.id):
                logger.info("  • Scene %s (AI): Đã có clip sẵn (%s), bỏ qua.", scene.id, self.clip_path(scene.id).name)
                continue
            if character and is_human_scene(scene, faceless):
                logger.info("  • Đang gửi Scene %s (AI - Reference Nhân Vật Nhất Quán): %s...", scene.id, scene.overlay_title)
                jobs.append(self._submit(scene, reference=character))
            elif product_refs and wants_product_reference(scene, faceless):
                logger.info("  • Đang gửi Scene %s (AI - Reference Sản Phẩm ZIP): %s...", scene.id, scene.overlay_title)
                jobs.append(self._submit(scene, reference=product_refs[scene.image_index % len(product_refs)]))
            else:
                logger.info("  • Đang gửi Scene %s (AI Text-to-Video): %s...", scene.id, scene.overlay_title)
                jobs.append(self._submit(scene, reference=None))
            time.sleep(SUBMIT_SPACING_SECONDS)

        if jobs:
            logger.info("\n⏳ Đang theo dõi tiến độ sinh %s AI clips từ Google Flow...", len(jobs))
            result = self._collect(jobs)
            if not result.ok:
                ids = sorted([*result.failed, *result.timed_out])
                logger.warning("⚠️ Đã lưu các clip hoàn thành. Chạy lại riêng các cảnh lỗi với: --scene %s", ' '.join(map(str, ids)))
            result.raise_for_failures()


def upload_product_references(client: FlowKitClient, images: Sequence[Path], project_id: str) -> list[str]:
    refs = []
    if images:
        logger.info("📸 [Tham Chiếu] Tải ảnh sản phẩm từ ZIP lên Google Flow làm hình ảnh tham chiếu...")
    for image in images[:MAX_REFERENCE_UPLOADS]:
        try:
            refs.append(client.upload_image(image, project_id=project_id))
        except Exception as exc:  # a missing reference only degrades to text-to-video
            logger.warning("Không thể upload ảnh tham chiếu %s: %s", image.name, exc)
    return refs


def build_non_ai_clip(scene: SceneDefinition, position: int, duration: float, out: Path, workspace: ProductWorkspace, opts: RunOptions, delogo: Optional[str]) -> None:
    """Photo slide for product shots; the shop's footage for REAL_FOOTAGE scenes."""
    images = workspace.assets.images
    video = workspace.assets.video
    image = pick_image(images, scene, position)
    if scene.kind not in PHOTO_KINDS and video and video.exists():
        video_len = try_probe_duration(video) or 0.0
        start = min(max(scene.real_start_sec or 0.0, 0.0), max(0.0, video_len - duration))
        logger.info("  • Scene %s: Cắt video thật của shop từ %.1fs (dài %.1fs)...", scene.id, start, duration)
        extract_vertical_subclip(video, start, duration, out, mode=opts.crop_mode, delogo=delogo)
    elif image:
        logger.info("  • Tạo shot sản phẩm thật từ ảnh %s (Scene %s)...", image.name, scene.id)
        create_image_slide_clip(image, duration, out)
    else:
        raise RuntimeError(f"Scene {scene.id} ({scene.kind}) cần ảnh hoặc video sản phẩm nhưng file zip không có.")


def run_flow_pipeline(
    profile: PlatformProfile,
    hooks: PlatformHooks,
    opts: RunOptions,
    client: Optional[FlowKitClient] = None,
) -> Path:
    """Render ``<slug>_flow_<variant>.mp4`` and its publishing kit; returns the video path."""
    opts = opts.resolved(profile)
    client = client or FlowKitClient()
    if not client.is_ready():
        raise RuntimeError("FlowKit server chưa chạy hoặc Chrome Extension chưa kết nối! (cần http://127.0.0.1:8100/health)")

    workspace = open_workspace(profile, opts)
    print_banner(f"BẮT ĐẦU SẢN XUẤT VIDEO {profile.display_name.upper()} FLOW AI (HYBRID AI + ẢNH THẬT)", workspace, opts.selection)

    logger.info("🌐 [Bước 1/5] Tạo Project & nạp ảnh tham chiếu lên Google Flow...")
    project_id = client.create_project(
        name=f"{profile.display_name} Ad - {workspace.product.name[:35]}",
        story=f"Dynamic {profile.display_name} video ad for {workspace.product.name}. High conversion lifestyle showcase.",
    )
    product_refs = upload_product_references(client, workspace.assets.images, project_id)

    logger.info("\n📋 [Bước 2/5] Nạp hoặc tạo kịch bản động (storyboard_%s.json)...", opts.style)
    scenes = load_storyboard(hooks, workspace, opts)
    silent_seconds = profile.flow_silent_seconds
    narration = narrate(scenes, workspace, opts, silent_seconds, "Bước 3/5")

    renderer = FlowRenderer(client, workspace, opts, project_id)
    renderer.render([s for s in scenes if s.kind in AI_KINDS], product_refs)

    logger.info("\n✨ [Bước 5/5] Ráp video, ghép giọng thuyết minh và chèn Text Overlay...")
    delogo = resolve_delogo(opts.delogo, workspace, workspace.assets.video)
    clips: dict[int, Path] = {}
    for position, scene in enumerate(scenes):
        clips[scene.id] = renderer.clip_path(scene.id)
        if scene.kind not in AI_KINDS:
            duration = narration.durations[scene.id] + SCENE_TAIL_PAD_SECONDS
            build_non_ai_clip(scene, position, duration, clips[scene.id], workspace, opts, delogo)
    assembled = assemble_scenes(
        scenes, clips, narration, workspace, opts, silent_seconds,
        output_name="{variant}_flow_assembled_{id:02d}.mp4", watermarked_kinds=AI_KINDS,
    )

    first_clip = clips.get(scenes[0].id) if scenes else None
    cover_source = first_clip if first_clip and file_is_ready(first_clip, 1000) else (assembled[0] if assembled else workspace.final_video("flow", opts.no_voice))
    deliverables = package_outputs("flow", "local", assembled, cover_source, scenes, narration, workspace, hooks, opts)
    print_summary(deliverables, workspace.storyboard_path(opts.style))
    return deliverables.video


__all__ = [
    "FlowRenderer",
    "is_faceless_scene",
    "is_faceless_storyboard",
    "is_human_scene",
    "run_flow_pipeline",
    "wants_product_reference",
]
