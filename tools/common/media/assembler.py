"""Scene assembly: fit a clip to its narration, burn overlays, mix audio, stitch scenes.

The ``*_filters`` / ``*_graph`` helpers are pure string builders so the ffmpeg
graphs can be unit-tested without rendering anything.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

from tools.common.constants import SCENE_TAIL_PAD_SECONDS, VERTICAL_720P, VideoSpec
from tools.common.ffmpeg import (
    DEFAULT_ENCODE,
    EncodeProfile,
    concat_list_line,
    delogo_filter,
    has_audio_stream,
    probe_duration,
    run_ffmpeg,
    try_probe_duration,
)
from tools.common.media.flowmark import flow_watermark_filter, flow_watermark_filter_for
from tools.common.media.text import TextStyle, drawtext_filter, text_files
from tools.common.models import SceneDefinition

logger = logging.getLogger(__name__)

# Used when neither audio, a target, nor the clip itself says how long a scene is.
DEFAULT_SCENE_SECONDS = 5.0
# A clip shorter than its narration is slowed down up to this factor; beyond it the
# last frame is held instead, because heavier slow-motion looks artificial.
MAX_STRETCH_FACTOR = 1.30

TITLE_STYLE = TextStyle(fontsize=38, fontcolor="yellow", y=140, bold=True, box_opacity=0.65, box_border=12)
SUBTITLE_STYLE = TextStyle(fontsize=26, fontcolor="white", y=210, bold=False, box_opacity=0.5, box_border=8)


@dataclass(frozen=True)
class FinishingLook:
    """Camera-like finishing applied to every scene (opt-out with ``de_ai=False``).

    Slow sub-pixel drift imitates a handheld camera, a gentle colour curve and film
    grain replace the flat digital look, and quiet brown noise fills the dead air
    between TTS phrases.
    """

    drift_crop_x: int = 16
    drift_crop_y: int = 28
    contrast: float = 1.02
    brightness: float = 0.01
    saturation: float = 1.03
    grain: int = 5
    plain_grain: int = 4  # grain when the look is disabled; also softens delogo edges
    room_tone_amplitude: float = 0.003
    room_tone_volume: float = 0.20
    voice_presence_cut_db: float = -1.8


LOOK = FinishingLook()
# Level of a clip's own audio (Flow foley/ambience) under the narration.
AMBIENT_VOLUME = 0.45
BGM_VOLUME = 0.15


# --------------------------------------------------------------------------- pure builders


def scene_duration(
    audio_duration: Optional[float],
    has_narration: bool,
    target_duration: Optional[float],
    video_duration: float,
    pad_tail: float,
) -> float:
    """How long the assembled scene runs."""
    if has_narration and audio_duration is not None:
        return audio_duration + pad_tail
    if target_duration is not None:
        return float(target_duration)
    if audio_duration is not None:
        return float(audio_duration)
    if video_duration > 0:
        return video_duration
    return DEFAULT_SCENE_SECONDS


def fit_duration_filters(video_duration: float, total_duration: float, fps: int) -> list[str]:
    """Stretch slightly or hold the last frame so the clip covers ``total_duration`` (never loops)."""
    filters: list[str] = []
    if 0 < video_duration < total_duration:
        factor = total_duration / video_duration
        if factor <= MAX_STRETCH_FACTOR:
            filters.append(f"setpts={factor:.4f}*(PTS-STARTPTS)")
        else:
            filters.append("setpts=PTS-STARTPTS")
            # Hold for the whole gap (plus a frame of margin); trim below cuts the excess.
            filters.append(f"tpad=stop_mode=clone:stop_duration={total_duration - video_duration + 1.0 / fps:.3f}")
    else:
        filters.append("setpts=PTS-STARTPTS")
    filters.append(f"trim=duration={total_duration:.2f}")
    filters.append(f"fps=fps={fps}")
    return filters


def delogo_filters(remove_flow_watermark: bool, delogo: Optional[str], flow_filter: Optional[str] = None) -> list[str]:
    """Flow sparkle removal (``flow_filter`` sized to the clip) plus an optional shop-logo box."""
    filters = []
    if remove_flow_watermark:
        filters.append(flow_filter or flow_watermark_filter())
    custom = delogo_filter(delogo)
    if custom:
        filters.append(custom)
    return filters


def look_filters(spec: VideoSpec, look: FinishingLook = LOOK) -> list[str]:
    dx, dy = look.drift_crop_x, look.drift_crop_y
    return [
        f"crop=in_w-{dx}:in_h-{dy}:"
        f"{dx // 2}+4*sin(2*PI*t*0.8)+2*sin(2*PI*t*1.5):"
        f"{dy // 2}+5*cos(2*PI*t*0.6)+2*cos(2*PI*t*1.2),"
        f"scale={spec.width}:{spec.height}",
        f"eq=contrast={look.contrast}:brightness={look.brightness}:saturation={look.saturation}",
    ]


def audio_mix_graph(video_graph: str, ambient: bool, finishing: bool, sample_rate: int, look: FinishingLook = LOOK) -> str:
    """filter_complex mixing narration (input 1) with optional clip ambience (0:a) and room tone (2:a)."""
    voice_eq = f",equalizer=f=3400:t=q:w=1.5:g={look.voice_presence_cut_db}" if finishing else ""
    chains = [f"[0:v]{video_graph}[v]"]
    # Narration goes first: amix duration=first ends the mix with the voice, not with the
    # (shorter) clip ambience, which used to cut sentences off at the clip's 6 s.
    chains.append(f"[1:a]volume=1.0{voice_eq},aresample={sample_rate}[voc]")
    inputs = ["[voc]"]
    if ambient:
        chains.append(f"[0:a]volume={AMBIENT_VOLUME},aresample={sample_rate}[amb]")
        inputs.append("[amb]")
    if finishing:
        chains.append(f"[2:a]volume={look.room_tone_volume},aresample={sample_rate}[room]")
        inputs.append("[room]")
    # apad covers the tail pad after the voice; the caller's -t ends the scene.
    chains.append(f"{''.join(inputs)}amix=inputs={len(inputs)}:duration=first:dropout_transition=2:normalize=0,apad[aout]")
    return ";".join(chains)


# --------------------------------------------------------------------------- rendering


def assemble_scene_clip(
    video_path: Path,
    audio_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    title_text: Optional[str] = None,
    subtitle_text: Optional[str] = None,
    audio_duration: Optional[float] = None,
    target_duration: Optional[float] = None,
    pad_tail: float = SCENE_TAIL_PAD_SECONDS,
    remove_watermark: bool = True,
    delogo: Optional[str] = None,
    de_ai: bool = True,
    spec: VideoSpec = VERTICAL_720P,
    encode: EncodeProfile = DEFAULT_ENCODE,
) -> Path:
    """Render one finished scene: clip fitted to narration, overlays burnt in, audio mixed.

    Without narration a silent stereo track is added (platforms reject video-only files)
    and the scene lasts ``target_duration`` (or the clip length).
    ``de_ai`` toggles the camera-like ``FinishingLook``.
    """
    if output_path is None:
        raise ValueError("output_path is required")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    has_narration = audio_path is not None and Path(audio_path).exists()
    if has_narration and audio_duration is None:
        audio_duration = probe_duration(audio_path)
    video_duration = try_probe_duration(video_path) or 0.0
    total = scene_duration(audio_duration, has_narration, target_duration, video_duration, pad_tail)

    filters = fit_duration_filters(video_duration, total, spec.fps)
    flow_filter = flow_watermark_filter_for(video_path) if remove_watermark else None
    filters += delogo_filters(remove_watermark, delogo, flow_filter)
    if de_ai:
        filters += look_filters(spec)

    with text_files(output_path.parent, output_path.stem, {"title": title_text, "sub": subtitle_text}) as files:
        if "title" in files:
            filters.append(drawtext_filter(files["title"], TITLE_STYLE))
        if "sub" in files:
            filters.append(drawtext_filter(files["sub"], SUBTITLE_STYLE))
        filters.append(f"noise=alls={LOOK.grain if de_ai else LOOK.plain_grain}:allf=t")
        video_graph = ",".join(filters)

        args = ["-i", str(video_path)]
        if has_narration:
            args += ["-i", str(audio_path)]
            if de_ai:
                args += ["-f", "lavfi", "-i", f"anoisesrc=d={total:.2f}:c=brown:r={encode.sample_rate}:a={LOOK.room_tone_amplitude}"]
            ambient = has_audio_stream(video_path)
            if ambient or de_ai:
                graph = audio_mix_graph(video_graph, ambient=ambient, finishing=de_ai, sample_rate=encode.sample_rate)
                args += ["-filter_complex", graph, "-map", "[v]", "-map", "[aout]"]
            else:
                args += ["-vf", video_graph, "-map", "0:v:0", "-map", "1:a:0"]
        else:
            args += ["-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={encode.sample_rate}"]
            args += ["-vf", video_graph, "-map", "0:v:0", "-map", "1:a:0"]

        args += [
            "-t", f"{total:.2f}",
            *encode.video_args(),
            *encode.audio_args(),
            *encode.container_args(),
            "-shortest",
            str(output_path),
        ]
        run_ffmpeg(args)
    return output_path


def _write_concat_list(paths: Sequence[Path], list_file: Path) -> Path:
    list_file.write_text("".join(concat_list_line(p) for p in paths), encoding="utf-8")
    return list_file


def concat_scenes(
    clip_paths: Sequence[Path],
    output_path: Path,
    bgm_path: Optional[Path] = None,
    spec: VideoSpec = VERTICAL_720P,
    encode: EncodeProfile = DEFAULT_ENCODE,
) -> Path:
    """Join assembled scenes into the final video, optionally under looping background music."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    list_file = _write_concat_list(clip_paths, output_path.parent / "concat_list.txt")
    joined = output_path.parent / "temp_concat.mp4"

    try:
        run_ffmpeg([
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c:v", encode.video_codec, "-r", str(spec.fps), "-pix_fmt", encode.pix_fmt,
            *encode.audio_args(),
            *encode.container_args(),
            str(joined),
        ])
        if bgm_path and Path(bgm_path).exists():
            run_ffmpeg([
                "-i", str(joined),
                "-i", str(bgm_path),
                "-filter_complex",
                f"[1:a]volume={BGM_VOLUME},aloop=loop=-1:size=2e+09[bgm];"
                "[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", encode.audio_codec, "-b:a", encode.audio_bitrate,
                *encode.container_args(),
                str(output_path),
            ])
        else:
            joined.replace(output_path)
    finally:
        joined.unlink(missing_ok=True)
        list_file.unlink(missing_ok=True)

    logger.info("[Assembler] Video successfully assembled to: %s", output_path)
    return output_path


def concat_audio_files(audio_paths: Sequence[Path], output_path: Path, encode: EncodeProfile = DEFAULT_ENCODE) -> Path:
    """Join per-scene narration into one MP3 voiceover."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    list_file = _write_concat_list(audio_paths, output_path.parent / "concat_voice_list.txt")
    try:
        run_ffmpeg([
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c:a", "libmp3lame", "-b:a", encode.audio_bitrate, "-ar", str(encode.sample_rate),
            str(output_path),
        ])
    finally:
        list_file.unlink(missing_ok=True)
    logger.info("[Assembler] Exported full narration audio: %s", output_path.name)
    return output_path


def create_silent_version(video_path: Path, silent_output_path: Path, encode: EncodeProfile = DEFAULT_ENCODE) -> Path:
    """Same video with a silent stereo track, for creators who add a trending sound in-app."""
    silent_output_path = Path(silent_output_path)
    silent_output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg([
        "-i", str(video_path),
        "-f", "lavfi", "-i", f"anullsrc=r={encode.sample_rate}:cl=stereo",
        "-c:v", "copy",
        *encode.audio_args(),
        *encode.container_args(),
        "-shortest",
        str(silent_output_path),
    ])
    logger.info("[Assembler] Exported silent version: %s", silent_output_path.name)
    return silent_output_path


def _mmss(seconds: float) -> str:
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


def render_voiceover_script(
    scenes: Sequence[SceneDefinition],
    audio_durations: Mapping[int, float],
    product_name: str = "",
    heading: str = "KỊCH BẢN LỜI THOẠI & PHỤ ĐỀ",
    default_scene_seconds: float = DEFAULT_SCENE_SECONDS,
) -> str:
    """Plain-text narration + per-scene timecode sheet for editors and caption tools."""
    continuous_speech = "\n\n".join(t for t in (getattr(s, "narrator_text", "").strip() for s in scenes) if t)

    lines: list[str] = []
    clock = 0.0
    for scene in scenes:
        idx = getattr(scene, "id", 0)
        dur = audio_durations.get(idx, default_scene_seconds)
        start, clock = clock, clock + dur
        lines.append(f"▶ PHÂN CẢNH {idx} [{_mmss(start)} - {_mmss(clock)}] ({dur:.2f}s) — {getattr(scene, 'name', f'Phân cảnh {idx}')}")
        lines.append(f"  • Lời thoại thuyết minh: \"{getattr(scene, 'narrator_text', '')}\"")
        if getattr(scene, "overlay_title", ""):
            lines.append(f"  • Text Overlay (Tiêu đề): {scene.overlay_title}")
        if getattr(scene, "overlay_subtitle", ""):
            lines.append(f"  • Text Overlay (Phụ đề):  {scene.overlay_subtitle}")
        lines.append("")

    rule = "=" * 70
    sub_rule = "-" * 70
    return f"""{rule}
🎙️ {heading} (VOICEOVER SCRIPT)
📦 Sản phẩm: {product_name}
⏱️ Tổng thời lượng: {_mmss(clock)} ({clock:.1f}s)
{rule}

{sub_rule}
1. VĂN BẢN ĐỌC LIỀN MẠCH (DÙNG CHO CAPCUT AUTO-CAPTION / ĐỌC VOICE):
{sub_rule}
{continuous_speech}

{sub_rule}
2. CHI TIẾT TỪNG PHÂN CẢNH & TEXT OVERLAY (THEO TIMECODE):
{sub_rule}
{chr(10).join(lines)}
""".strip()


def export_voiceover_script(
    scenes: Sequence[SceneDefinition],
    audio_durations: Mapping[int, float],
    output_path: Path,
    product_name: str = "",
    heading: str = "KỊCH BẢN LỜI THOẠI & PHỤ ĐỀ",
    default_scene_seconds: float = DEFAULT_SCENE_SECONDS,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_voiceover_script(scenes, audio_durations, product_name, heading, default_scene_seconds),
        encoding="utf-8",
    )
    logger.info("[Assembler] Exported script & timecode text: %s", output_path.name)
    return output_path


__all__ = [
    "FinishingLook",
    "assemble_scene_clip",
    "audio_mix_graph",
    "concat_audio_files",
    "concat_scenes",
    "create_silent_version",
    "export_voiceover_script",
    "fit_duration_filters",
    "render_voiceover_script",
    "scene_duration",
]
