"""9:16 cover/thumbnail: one frame from the video with a hook title and product line burnt in."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tools.common.media.flowmark import flow_watermark_filter_for
from tools.common.ffmpeg import delogo_filter, run_ffmpeg
from tools.common.media.text import TextStyle, drawtext_filter, text_files

# (minimum text length, font size) tiers, longest first, so text never overflows 720px.
FontTiers = tuple[tuple[int, int], ...]

COVER_GRAIN = 5
COVER_JPEG_QUALITY = 2  # ffmpeg -q:v scale, 2 = near-lossless
_TRAILING_PUNCTUATION = "?!"


@dataclass(frozen=True)
class CoverStyle:
    hook_max_chars: int = 34
    subtitle_max_chars: int = 38
    hook_font_tiers: FontTiers = ((27, 40), (21, 46), (15, 50), (0, 54))
    subtitle_font_tiers: FontTiers = ((33, 26), (25, 28), (0, 32))
    hook_y: int = 180
    subtitle_y: int = 280


DEFAULT_COVER_STYLE = CoverStyle()


def _font_size(text: str, tiers: FontTiers) -> int:
    return next(size for min_len, size in tiers if len(text) >= min_len)


def format_cover_text(text: str, max_chars: int = 38) -> str:
    """Upper-case and shorten ``text`` to ``max_chars`` at a word boundary.

    A trailing ``?`` or ``!`` is kept (the hook usually is a question), and the result
    never exceeds ``max_chars``.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text.upper()
    suffix = text[-1] if text[-1] in _TRAILING_PUNCTUATION else ""
    truncated = text[: max_chars - len(suffix)]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return (truncated.rstrip(" ,.;:-") + suffix).upper()


def create_cover_frame(
    source_video: Path,
    hook_title: str,
    subtitle: str,
    output_path: Path,
    style: CoverStyle = DEFAULT_COVER_STYLE,
    time_offset_s: float = 1.2,
    delogo: Optional[str] = None,
) -> Path:
    """Grab the frame at ``time_offset_s`` and burn the hook + subtitle banner onto it.

    Without an explicit ``delogo`` the Flow watermark corner is cleaned.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    hook = format_cover_text(hook_title, style.hook_max_chars)
    sub = format_cover_text(subtitle, style.subtitle_max_chars)
    hook_style = TextStyle(
        fontsize=_font_size(hook, style.hook_font_tiers), fontcolor="yellow", y=style.hook_y,
        box_opacity=0.75, box_border=16, border_width=4,
    )
    sub_style = TextStyle(
        fontsize=_font_size(sub, style.subtitle_font_tiers), fontcolor="white", y=style.subtitle_y,
        box_opacity=0.65, box_border=12, border_width=3,
    )

    filters = [delogo_filter(delogo) or flow_watermark_filter_for(Path(source_video)), f"noise=alls={COVER_GRAIN}:allf=t"]
    with text_files(output_path.parent, output_path.stem, {"title": hook, "sub": sub}) as files:
        if "title" in files:
            filters.append(drawtext_filter(files["title"], hook_style))
        if "sub" in files:
            filters.append(drawtext_filter(files["sub"], sub_style))
        run_ffmpeg([
            "-ss", f"{time_offset_s:.2f}",
            "-i", str(source_video),
            "-vf", ",".join(filters),
            "-frames:v", "1",
            "-q:v", str(COVER_JPEG_QUALITY),
            "-map_metadata", "-1",
            str(output_path),
        ])
    return output_path


__all__ = ["CoverStyle", "create_cover_frame", "format_cover_text"]
