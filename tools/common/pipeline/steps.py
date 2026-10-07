"""Steps both pipelines run identically: storyboard, narration, assembly, packaging."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

from tools.common import storyboard_io
from tools.common.bgm import resolve_bgm_path
from tools.common.media.assembler import assemble_scene_clip, concat_audio_files, concat_scenes
from tools.common.models import SceneDefinition
from tools.common.pipeline.context import PlatformHooks, ProductWorkspace, RunOptions
from tools.common.pipeline.selection import warn_unknown_scene_ids
from tools.common.pipeline.voice import NarrationResult, silent_timing, synthesize_narration
from tools.common.tts import generate_speech

logger = logging.getLogger(__name__)


def load_storyboard(hooks: PlatformHooks, workspace: ProductWorkspace, opts: RunOptions) -> list[SceneDefinition]:
    """Load (or build) the storyboard and refresh any ``--scene`` targets from the builders."""
    path = workspace.storyboard_path(opts.style)
    scenes = hooks.load_storyboard(
        workspace.product,
        path,
        style=opts.style,
        cta_mode=opts.cta_mode,
        force=opts.force_storyboard,
        custom_idea=opts.custom_idea,
        channel_name=opts.channel_name,
    )
    selection = opts.selection
    warn_unknown_scene_ids(selection, (s.id for s in scenes))
    storyboard_io.refresh_targeted_scenes(
        scenes,
        selection.target_ids,
        path,
        regenerate=lambda: hooks.generate_storyboard(
            workspace.product,
            style=opts.style,
            cta_mode=opts.cta_mode,
            custom_idea=opts.custom_idea,
            channel_name=opts.channel_name,
        ),
    )
    return scenes


def narrate(scenes: Sequence[SceneDefinition], workspace: ProductWorkspace, opts: RunOptions, silent_seconds: float, step: str) -> NarrationResult:
    if opts.no_voice:
        print(f"\n🔇 [{step}] Chế độ Không Voiceover (Silent POV) - Nhịp cắt chuẩn {silent_seconds}s/cảnh...")
        return silent_timing(scenes, silent_seconds)
    print(f"\n🎙️ [{step}] Sinh giọng đọc thuyết minh qua OmniVoice API cho {len(scenes)} phân cảnh...")
    return synthesize_narration(
        scenes,
        workspace.audio_dir,
        workspace.variant,
        synthesize=lambda text, out: generate_speech(text=text, output_path=out, speed=opts.speed, profile_id=opts.voice_profile_id),
        selection=opts.selection,
    )


def assemble_scenes(
    scenes: Sequence[SceneDefinition],
    clips: Mapping[int, Path],
    narration: NarrationResult,
    workspace: ProductWorkspace,
    opts: RunOptions,
    silent_seconds: float,
    output_name: str,
    watermarked_kinds: Sequence[str] = (),
) -> list[Path]:
    """Fit each clip to its narration and burn overlays. ``output_name`` is formatted with ``id``."""
    assembled = []
    for scene in scenes:
        out = workspace.scenes_dir / output_name.format(variant=workspace.variant, id=scene.id)
        timing = f"Silent: {silent_seconds}s" if opts.no_voice else f"OmniVoice: {narration.durations[scene.id]:.2f}s"
        print(f"  • Ráp Scene {scene.id}: {scene.overlay_title} ({timing})")
        assemble_scene_clip(
            video_path=clips[scene.id],
            audio_path=narration.files[scene.id],
            output_path=out,
            title_text=None if opts.no_overlay else scene.overlay_title,
            subtitle_text=None if opts.no_overlay else scene.overlay_subtitle,
            audio_duration=narration.durations[scene.id],
            target_duration=silent_seconds if opts.no_voice else None,
            remove_watermark=scene.kind in watermarked_kinds,
        )
        assembled.append(out)
    return assembled


@dataclass
class Deliverables:
    video: Path
    videos: dict[str, Path]
    cover: Path
    script: Path
    guide: Path
    voiceover: Optional[Path] = None
    captions: dict[str, Path] = field(default_factory=dict)


def package_outputs(
    method: str,
    other_method: str,
    assembled: Sequence[Path],
    cover_source: Path,
    scenes: Sequence[SceneDefinition],
    narration: NarrationResult,
    workspace: ProductWorkspace,
    hooks: PlatformHooks,
    opts: RunOptions,
) -> Deliverables:
    """Final video (+BGM), captions, cover, script, full voiceover and publish guide."""
    final_video = workspace.final_video(method, silent=opts.no_voice)
    bgm = resolve_bgm_path(custom_bgm=opts.bgm, style=opts.style, product_assets_dir=workspace.assets_dir)
    if bgm:
        print(f"🎵 [Nhạc Nền BGM] Tự động kích hoạt: {bgm.name}...")
    print(f"\n🎞️ Đang ghép toàn bộ các phân cảnh thành video {final_video.name}...")
    concat_scenes(list(assembled), final_video, bgm_path=bgm)
    videos = {method if not opts.no_voice else f"{method}_silent": final_video}

    print("📝 Đang tạo bộ caption & metadata đa nền tảng...")
    captions = hooks.write_captions(
        workspace.product, list(scenes), workspace.final_dir,
        channel_name=opts.channel_name, channel_handle=opts.channel_handle, variant_suffix=workspace.variant,
    )

    cover = workspace.final_file("cover.jpg")
    print("🖼️ Đang tạo ảnh bìa (Cover / Thumbnail) 9:16...")
    try:
        hooks.create_cover(cover_source, workspace.product, list(scenes), cover)
    except Exception as exc:  # a missing cover must not cost the finished video
        logger.warning("Lỗi tạo ảnh bìa: %s", exc)

    print("🎙️ Đang xuất file kịch bản text lời thoại...")
    script = workspace.final_file("script.txt")
    hooks.export_script(list(scenes), narration.durations, script, product_name=workspace.product.name)
    voiced = [p for p in (narration.files.get(s.id) for s in scenes) if p and Path(p).exists()]
    voiceover = concat_audio_files(voiced, workspace.final_file("voiceover.mp3")) if voiced else None

    other = workspace.final_video(other_method, silent=False)
    if other.exists():
        videos[other_method] = other
    guide = workspace.final_file("publish_guide.txt")
    hooks.write_publish_guide(
        product=workspace.product, scenes=list(scenes), video_paths=videos, cover_path=cover,
        caption_files=captions, output_guide_path=guide, channel_handle=opts.channel_handle,
        script_path=script, voiceover_path=voiceover,
    )
    return Deliverables(video=final_video, videos=videos, cover=cover, script=script, guide=guide, voiceover=voiceover, captions=captions)


def print_summary(deliverables: Deliverables, storyboard: Path) -> None:
    rows = [("Video thành phẩm", deliverables.video)]
    rows += [(f"Video {name}", path) for name, path in deliverables.videos.items() if path != deliverables.video]
    if deliverables.voiceover:
        rows.append(("Audio lời thoại đầy đủ", deliverables.voiceover))
    rows += [
        ("Text kịch bản & time", deliverables.script),
        ("Ảnh bìa thu nhỏ", deliverables.cover),
        ("Hướng dẫn xuất bản", deliverables.guide),
    ]
    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH BỘ OUTPUT SẢN PHẨM:")
    for i, (label, path) in enumerate(rows, 1):
        print(f"👉 {i}. {label + ':':<24}{Path(path).resolve()}")
    print(f"📝 Kịch bản có thể tùy chỉnh tại: {storyboard.resolve()}")
    print("=" * 65 + "\n")


__all__ = [
    "Deliverables",
    "assemble_scenes",
    "load_storyboard",
    "narrate",
    "package_outputs",
    "print_summary",
]
