"""Local pipeline: build every scene from the shop's own video and photos (no Flow)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from tools.common.constants import SCENE_TAIL_PAD_SECONDS
from tools.common.ffmpeg import try_probe_duration
from tools.common.media.cutplanner import calculate_smart_subclip_starts
from tools.common.media.extractor import create_hybrid_subclip, create_image_slide_clip, extract_vertical_subclip
from tools.common.models import SceneDefinition
from tools.common.pipeline.context import PlatformHooks, ProductWorkspace, RunOptions, open_workspace, print_banner
from tools.common.pipeline.steps import assemble_scenes, load_storyboard, narrate, package_outputs, print_summary
from tools.common.settings import PlatformProfile
from tools.common.watermarks import resolve_delogo_for_product

# Scenes built from photos rather than footage.
PHOTO_KINDS = ("PRODUCT_PHOTO",)
# Lead in with a photo when the footage left for a scene is this much shorter than it needs.
HYBRID_SHORTFALL_SECONDS = 0.5


def resolve_delogo(spec: Optional[str], workspace: ProductWorkspace, raw_video: Optional[Path]) -> Optional[str]:
    """``auto``: look the shop up in watermark_rules.json; ``none``: off; otherwise a manual box."""
    if not spec or spec.lower() == "none":
        return None
    if spec != "auto":
        return spec
    resolved, rule_name = resolve_delogo_for_product(workspace.product.url, video_path=raw_video)
    if resolved:
        print(f"  [Delogo] Áp dụng quy tắc xóa logo ('{rule_name}'): {resolved}")
    else:
        print("  [Delogo] Không phát hiện quy tắc xóa logo nào cho sản phẩm này trong config/watermark_rules.json")
    return resolved


def pick_image(images: Sequence[Path], scene: SceneDefinition, position: int) -> Optional[Path]:
    if not images:
        return None
    index = scene.image_index if scene.image_index is not None else position
    return images[index % len(images)]


@dataclass
class FootagePlan:
    """Where each scene's slice of the shop video starts and how much footage it owns."""

    video: Path
    duration: float
    starts: list[float]

    def slice_for(self, position: int, scene: SceneDefinition, needed: float) -> tuple[float, float]:
        if position < len(self.starts):
            start = self.starts[position]
            end = self.starts[position + 1] if position + 1 < len(self.starts) else self.duration
            return start, max(0.0, end - start)
        start = scene.real_start_sec if scene.real_start_sec is not None and scene.real_start_sec >= 0 else 0.0
        return start, needed


def plan_footage(raw_video: Optional[Path], needed: Sequence[float], source_label: str) -> Optional[FootagePlan]:
    if not raw_video or not raw_video.exists():
        return None
    duration = try_probe_duration(raw_video)
    if not duration:
        print("  [Video Gốc] Không thể đo thời lượng video gốc, chuyển sang dựng từ ảnh.")
        return None
    starts, _ = calculate_smart_subclip_starts(raw_video, len(needed), duration, scene_durations=list(needed))
    print(f"  [Video Gốc] Tìm thấy video mẫu từ {source_label} ({duration:.1f}s), sẵn sàng biên tập sub-clips.")
    print(f"  [Smart Cuts] Phân bổ mốc thời gian không trùng lặp: {starts}")
    return FootagePlan(video=raw_video, duration=duration, starts=starts)


def build_local_clips(
    scenes: Sequence[SceneDefinition],
    durations: dict[int, float],
    workspace: ProductWorkspace,
    opts: RunOptions,
    source_label: str,
) -> dict[int, Path]:
    images = workspace.assets.images
    raw_video = workspace.assets.video
    needed = [durations[s.id] + SCENE_TAIL_PAD_SECONDS for s in scenes]
    footage = plan_footage(raw_video, needed, source_label)
    delogo = resolve_delogo(opts.delogo, workspace, footage.video if footage else None)

    clips: dict[int, Path] = {}
    for position, (scene, dur) in enumerate(zip(scenes, needed)):
        out = workspace.clips_dir / f"{workspace.variant}_clip_{scene.id:02d}.mp4"
        image = pick_image(images, scene, position)
        if footage is None or scene.kind in PHOTO_KINDS:
            if image and image.exists():
                print(f"  • Scene {scene.id}: Hiệu ứng Pan & Zoom từ ảnh {image.name} (dài {dur:.1f}s)...")
                create_image_slide_clip(image, dur, out)
            elif footage is not None:
                start, _ = footage.slice_for(position, scene, dur)
                extract_vertical_subclip(footage.video, start, dur, out, mode=opts.crop_mode, delogo=delogo)
            else:
                raise RuntimeError(f"Scene {scene.id} không có video lẫn hình ảnh để dựng!")
        else:
            start, available = footage.slice_for(position, scene, dur)
            if image and 0 < available < dur - HYBRID_SHORTFALL_SECONDS:
                print(f"  • Scene {scene.id}: Ghép ảnh {image.name} {dur - available:.1f}s + video mẫu {available:.1f}s từ {start:.1f}s...")
                create_hybrid_subclip(
                    image_path=image, video_path=footage.video, img_duration=dur - available,
                    vid_start_sec=start, vid_duration=available, output_path=out, mode=opts.crop_mode, delogo=delogo,
                )
            else:
                cut = min(dur, available) if available > 0 else dur
                print(f"  • Scene {scene.id}: Cắt video mẫu từ {start:.1f}s (dài {cut:.1f}s, mode {opts.crop_mode})...")
                extract_vertical_subclip(footage.video, start, cut, out, mode=opts.crop_mode, delogo=delogo)
        clips[scene.id] = out
    return clips


def run_local_pipeline(profile: PlatformProfile, hooks: PlatformHooks, opts: RunOptions) -> Path:
    """Render ``<slug>_local_<variant>.mp4`` and its publishing kit; returns the video path."""
    opts = opts.resolved(profile)
    workspace = open_workspace(profile, opts)
    print_banner(f"BẮT ĐẦU SẢN XUẤT VIDEO QUẢNG CÁO {profile.display_name.upper()} (LOCAL)", workspace, opts.selection)

    print("📋 [Bước 1/5] Nạp hoặc tạo kịch bản...")
    scenes = load_storyboard(hooks, workspace, opts)
    narration = narrate(scenes, workspace, opts, profile.silent_scene_seconds, "Bước 2/5")

    print("\n🎬 [Bước 3/5] Chuẩn bị video clip 9:16 cho từng phân cảnh...")
    clips = build_local_clips(scenes, narration.durations, workspace, opts, profile.display_name)

    print("\n✨ [Bước 4/5] Ráp âm thanh, căn chỉnh độ dài và chèn Text Overlay...")
    assembled = assemble_scenes(
        scenes, clips, narration, workspace, opts, profile.silent_scene_seconds,
        output_name="{variant}_scene_{id:02d}_assembled.mp4",
    )

    print("\n🎞️ [Bước 5/5] Ghép các phân cảnh thành video cuối cùng...")
    cover_source = clips.get(scenes[0].id) if scenes else None
    deliverables = package_outputs(
        "local", "flow", assembled, cover_source or workspace.final_video("local", opts.no_voice),
        scenes, narration, workspace, hooks, opts,
    )
    print_summary(deliverables, workspace.storyboard_path(opts.style))
    return deliverables.video


__all__ = ["build_local_clips", "plan_footage", "resolve_delogo", "run_local_pipeline"]
