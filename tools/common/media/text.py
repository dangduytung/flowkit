"""Font resolution and ``drawtext`` overlays.

Text is always passed to ffmpeg through a UTF-8 ``textfile`` so Vietnamese diacritics
survive the Windows command line.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Sequence

from tools.common.ffmpeg import filter_path

# Env overrides let a deployment pin fonts without code changes.
FONT_BOLD_ENV = "AD_FONT_BOLD"
FONT_REGULAR_ENV = "AD_FONT_REGULAR"

_BOLD_CANDIDATES: tuple[str, ...] = (
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
_REGULAR_CANDIDATES: tuple[str, ...] = (
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
# Fontconfig family used when no font file is found.
FALLBACK_FONT_FAMILY = "Arial"


def _first_existing(env_var: str, candidates: Sequence[str]) -> Optional[Path]:
    override = os.getenv(env_var)
    for raw in ([override] if override else []) + list(candidates):
        path = Path(raw)
        if path.is_file():
            return path
    return None


def font_spec(bold: bool) -> str:
    """The ``fontfile=...`` (or ``font=...``) fragment of a drawtext filter."""
    path = _first_existing(FONT_BOLD_ENV, _BOLD_CANDIDATES) if bold else _first_existing(FONT_REGULAR_ENV, _REGULAR_CANDIDATES)
    return f"fontfile='{filter_path(path)}'" if path else f"font='{FALLBACK_FONT_FAMILY}'"


@dataclass(frozen=True)
class TextStyle:
    fontsize: int
    fontcolor: str
    y: int
    bold: bool = True
    box_opacity: float = 0.65
    box_border: int = 12
    border_width: int = 0


def drawtext_filter(textfile: Path, style: TextStyle) -> str:
    parts = [
        f"drawtext=textfile='{filter_path(textfile)}'",
        font_spec(style.bold),
        f"fontsize={style.fontsize}",
        f"fontcolor={style.fontcolor}",
    ]
    if style.border_width:
        parts += [f"borderw={style.border_width}", "bordercolor=black"]
    parts += [
        "box=1",
        f"boxcolor=black@{style.box_opacity}",
        f"boxborderw={style.box_border}",
        "x=(w-text_w)/2",
        f"y={style.y}",
    ]
    return ":".join(parts)


@contextmanager
def text_files(directory: Path, stem: str, texts: dict[str, Optional[str]]) -> Iterator[dict[str, Path]]:
    """Write each non-empty text to ``<stem>_<key>.txt`` for drawtext; removed afterwards."""
    written: dict[str, Path] = {}
    try:
        for key, text in texts.items():
            if text and text.strip():
                path = Path(directory) / f"{stem}_{key}.txt"
                path.write_text(text.strip(), encoding="utf-8")
                written[key] = path
        yield written
    finally:
        for path in written.values():
            path.unlink(missing_ok=True)


__all__ = ["TextStyle", "drawtext_filter", "font_spec", "text_files"]
