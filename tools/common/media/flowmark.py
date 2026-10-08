"""Removal of Google Flow's sparkle watermark with a star-shaped mask.

A rectangular ``delogo`` box smears a visible blurred patch over the corner; ``removelogo``
with a mask of just the sparkle only repaints those pixels. The mark sits at the same
place on every Flow render (measured across 27 clips), so the mask is drawn analytically
and cached per frame size.
"""
from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path

from tools.common.constants import FLOW_WATERMARK_SPARKLE, VERTICAL_720P
from tools.common.ffmpeg import filter_path, probe_dimensions

logger = logging.getLogger(__name__)

# Fatter than the true astroid (exponent 2/3) and a few pixels wider, so the soft
# anti-aliased rim of the mark is repainted too.
_SHAPE_EXPONENT = 0.85
_MARGIN_PX = 6
_CACHE_DIR = Path(tempfile.gettempdir()) / "flowkit_masks"


def _inside(dx: float, dy: float, radius: float) -> bool:
    if radius <= 0:
        return False
    return (abs(dx) / radius) ** _SHAPE_EXPONENT + (abs(dy) / radius) ** _SHAPE_EXPONENT <= 1.0


def flow_watermark_mask(width: int, height: int, cache_dir: Path = _CACHE_DIR) -> Path:
    """PGM mask (white = watermark) for a ``width`` x ``height`` Flow render."""
    path = cache_dir / f"flow_sparkle_{width}x{height}_m{_MARGIN_PX}_e{_SHAPE_EXPONENT}.pgm"
    if path.exists():
        return path
    mark = FLOW_WATERMARK_SPARKLE
    sx, sy = width / VERTICAL_720P.width, height / VERTICAL_720P.height
    cx, cy = mark.cx * sx, mark.cy * sy
    radius = (mark.radius + _MARGIN_PX) * min(sx, sy)
    row_range = range(max(0, int(cy - radius) - 1), min(height, int(cy + radius) + 2))
    col_range = range(max(0, int(cx - radius) - 1), min(width, int(cx + radius) + 2))
    pixels = bytearray(width * height)
    for y in row_range:
        for x in col_range:
            if _inside(x + 0.5 - cx, y + 0.5 - cy, radius):
                pixels[y * width + x] = 255
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(f"P5\n{width} {height}\n255\n".encode("ascii") + bytes(pixels))
    tmp.replace(path)
    return path


def flow_watermark_filter(width: int = VERTICAL_720P.width, height: int = VERTICAL_720P.height) -> str:
    """``removelogo`` filter for the sparkle on a ``width`` x ``height`` frame."""
    return f"removelogo=f='{filter_path(flow_watermark_mask(width, height))}'"


def flow_watermark_filter_for(video: Path) -> str:
    """Same, sized to ``video`` (falls back to 720x1280 when it cannot be probed)."""
    try:
        width, height = probe_dimensions(video)
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        logger.warning("Không đọc được kích thước %s, dùng mặt nạ 720x1280: %s", Path(video).name, exc)
        width, height = VERTICAL_720P.width, VERTICAL_720P.height
    return flow_watermark_filter(width, height)


__all__ = ["flow_watermark_filter", "flow_watermark_filter_for", "flow_watermark_mask"]
