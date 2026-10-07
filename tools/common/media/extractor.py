"""Turn a product zip's raw photos and shop video into 9:16 scene clips."""
from __future__ import annotations

import logging
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from tools.common.constants import IMAGE_SUFFIXES, TEXT_SUFFIXES, VERTICAL_720P, VIDEO_SUFFIXES, VideoSpec
from tools.common.ffmpeg import DEFAULT_ENCODE, EncodeProfile, delogo_filter, probe_dimensions, run_ffmpeg

logger = logging.getLogger(__name__)

# Source is treated as already vertical when height >= width * this ratio.
VERTICAL_ASPECT_THRESHOLD = 1.3
# Subclips never shrink below this when stopped short of a glitch zone.
MIN_GLITCH_CAPPED_SECONDS = 1.5
GLITCH_SAFETY_MARGIN_SECONDS = 0.2

# Still-photo slide: blurred backdrop + inset product photo with a slow push-in.
SLIDE_INSET_MARGIN_X = 60
SLIDE_INSET_MARGIN_Y = 380
KEN_BURNS_ZOOM_STEP = 0.0008
KEN_BURNS_MAX_ZOOM = 1.06


@dataclass
class ExtractedAssets:
    images: list[Path] = field(default_factory=list)
    video: Optional[Path] = None
    description: Optional[Path] = None


def extract_zip(zip_path: Path, dest_dir: Path) -> ExtractedAssets:
    """Unpack photos, the first video and the description text from a product zip."""
    src_zip = Path(zip_path)
    if not src_zip.exists():
        raise FileNotFoundError(f"Product zip not found: {src_zip}")

    target_dir = Path(dest_dir)
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    assets = ExtractedAssets()

    with zipfile.ZipFile(src_zip) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if lower.endswith(IMAGE_SUFFIXES):
                out_file = images_dir / Path(name).name
                assets.images.append(out_file)
            elif lower.endswith(VIDEO_SUFFIXES):
                out_file = target_dir / "raw_video.mp4"
                assets.video = out_file
            elif lower.endswith(TEXT_SUFFIXES):
                out_file = target_dir / "description.txt"
                assets.description = out_file
            else:
                continue
            out_file.write_bytes(archive.read(name))

    print(f"[Extractor] Extracted {len(assets.images)} images, video: {assets.video}, text: {assets.description}")
    return assets


def _is_vertical(video: Path) -> bool:
    try:
        width, height = probe_dimensions(video)
    except Exception as exc:  # unreadable header: fall back to the landscape path
        logger.warning("Cannot probe %s: %s", video, exc)
        return False
    return height >= width * VERTICAL_ASPECT_THRESHOLD


def _source_duration_before_glitch(
    start_sec: float, duration: float, glitch_intervals: Sequence[tuple[float, float]]
) -> float:
    """Shorten the source read so the slice stops before the first glitch zone it would enter."""
    for glitch_start, _ in glitch_intervals:
        if start_sec < glitch_start < start_sec + duration:
            return max(MIN_GLITCH_CAPPED_SECONDS, glitch_start - GLITCH_SAFETY_MARGIN_SECONDS - start_sec)
    return duration


def vertical_filter(mode: str, is_vertical: bool, spec: VideoSpec, prefix: str, tail: str) -> str:
    """Filter graph that fits any source into ``spec`` (blurred backdrop or centre crop)."""
    w, h = spec.width, spec.height
    if is_vertical:
        return f"{prefix}scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},{tail}"
    if mode == "blur_bg":
        return (
            f"[0:v]{prefix}split=2[v1][v2];"
            f"[v1]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=25:5[bg];"
            f"[v2]scale={w}:-1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,{tail}"
        )
    # Centre crop to the output aspect ratio, sized from the *source* height.
    crop_w = f"trunc(in_h*{w}/{h}/2)*2"
    return f"{prefix}crop={crop_w}:in_h:(in_w-{crop_w})/2:0,scale={w}:{h},{tail}"


def extract_vertical_subclip(
    src_video: Path,
    start_sec: float,
    duration: float,
    output_path: Path,
    mode: str = "blur_bg",
    width: int = VERTICAL_720P.width,
    height: int = VERTICAL_720P.height,
    fps: int = VERTICAL_720P.fps,
    glitch_intervals: Optional[Sequence[tuple[float, float]]] = None,
    delogo: Optional[str] = None,
    encode: EncodeProfile = DEFAULT_ENCODE,
) -> Path:
    """Cut ``duration`` seconds from ``start_sec`` and format them as a silent 9:16 clip.

    ``mode`` is ``"blur_bg"`` (letterbox over a blurred copy) or ``"center_crop"``.
    If the slice would run into a glitch interval, less source is read and slowed down
    to fill ``duration``.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    spec = VideoSpec(width, height, fps)

    logo = delogo_filter(delogo)
    prefix = f"{logo}," if logo else ""
    source_duration = _source_duration_before_glitch(start_sec, duration, glitch_intervals or ())
    if source_duration < duration - 0.1:
        tail = f"setpts={duration / source_duration:.4f}*PTS,fps={fps}"
    else:
        tail = f"fps={fps},setpts=PTS-STARTPTS"

    vf = vertical_filter(mode, _is_vertical(src_video), spec, prefix, tail)
    run_ffmpeg([
        "-ss", str(start_sec),
        "-t", str(source_duration),
        "-i", str(src_video),
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts",
        "-vf", vf,
        *encode.video_args(),
        "-an",  # narration is mixed in later
        str(output_path),
    ])
    return output_path


def create_image_slide_clip(
    image_path: Path,
    duration: float,
    output_path: Path,
    width: int = VERTICAL_720P.width,
    height: int = VERTICAL_720P.height,
    fps: int = VERTICAL_720P.fps,
    encode: EncodeProfile = DEFAULT_ENCODE,
) -> Path:
    """Animate a still product photo into a 9:16 Ken Burns clip of ``duration`` seconds."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(fps, int(duration * fps))

    graph = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},boxblur=15:2[bg];"
        f"[0:v]scale={width - SLIDE_INSET_MARGIN_X}:{height - SLIDE_INSET_MARGIN_Y}:force_original_aspect_ratio=decrease[fg_img];"
        f"[bg][fg_img]overlay=(W-w)/2:(H-h)/2[merged];"
        f"[merged]zoompan=z='min(zoom+{KEN_BURNS_ZOOM_STEP},{KEN_BURNS_MAX_ZOOM})':d={frames}:s={width}x{height}:fps={fps}[v]"
    )
    run_ffmpeg([
        "-i", str(image_path),
        "-filter_complex", graph,
        "-map", "[v]",
        "-t", f"{duration:.2f}",
        *encode.video_args(preset="veryfast"),
        str(output_path),
    ])
    return output_path


def create_hybrid_subclip(
    image_path: Path,
    video_path: Path,
    img_duration: float,
    vid_start_sec: float,
    vid_duration: float,
    output_path: Path,
    width: int = VERTICAL_720P.width,
    height: int = VERTICAL_720P.height,
    fps: int = VERTICAL_720P.fps,
    mode: str = "blur_bg",
    delogo: Optional[str] = None,
    encode: EncodeProfile = DEFAULT_ENCODE,
) -> Path:
    """A Ken Burns photo lead-in followed by real footage.

    Used when the shop video has less unused footage than the narration needs,
    so the scene is filled without looping or reusing another scene's footage.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=output_path.parent, prefix="_hybrid_") as tmp:
        slide = Path(tmp) / "slide.mp4"
        footage = Path(tmp) / "footage.mp4"
        create_image_slide_clip(image_path, img_duration, slide, width=width, height=height, fps=fps, encode=encode)
        extract_vertical_subclip(
            video_path, vid_start_sec, vid_duration, footage,
            mode=mode, width=width, height=height, fps=fps, delogo=delogo, encode=encode,
        )
        run_ffmpeg([
            "-i", str(slide),
            "-i", str(footage),
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]",
            *encode.video_args(),
            str(output_path),
        ])
    return output_path


__all__ = [
    "ExtractedAssets",
    "create_hybrid_subclip",
    "create_image_slide_clip",
    "extract_vertical_subclip",
    "extract_zip",
    "vertical_filter",
]
