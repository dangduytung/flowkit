"""Shared, platform-neutral constants for the ad pipelines.

Anything that differs between Shopee and TikTok belongs in that package's config,
not here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoSpec:
    """Output frame geometry and rate of every rendered clip."""

    width: int = 720
    height: int = 1280
    fps: int = 30

    @property
    def size(self) -> str:
        return f"{self.width}x{self.height}"


@dataclass(frozen=True)
class DelogoBox:
    """A rectangle for ffmpeg's ``delogo`` filter, in output pixels."""

    x: int
    y: int
    w: int
    h: int

    def to_spec(self) -> str:
        return f"x={self.x}:y={self.y}:w={self.w}:h={self.h}"


# Portrait 9:16 at 720p — the format Flow renders and every short-video platform accepts.
VERTICAL_720P = VideoSpec()

# Google Flow's sparkle mark, bottom-right of a 720x1280 render.
FLOW_WATERMARK_BOX = DelogoBox(x=546, y=1120, w=68, h=104)

# A Flow/Omni clip smaller than this is a failed or partial download, not a video.
MIN_FLOW_CLIP_BYTES = 100_000

# Extra video held after the narration ends so cuts between scenes do not clip speech.
SCENE_TAIL_PAD_SECONDS = 0.4

__all__ = [
    "DelogoBox",
    "FLOW_WATERMARK_BOX",
    "MIN_FLOW_CLIP_BYTES",
    "SCENE_TAIL_PAD_SECONDS",
    "VERTICAL_720P",
    "VideoSpec",
]
