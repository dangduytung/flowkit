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



# Portrait 9:16 at 720p — the format Flow renders and every short-video platform accepts.
VERTICAL_720P = VideoSpec()

@dataclass(frozen=True)
class SparkleMark:
    """Centre and half-size of Flow's four-point sparkle, in 720x1280 pixels."""

    cx: float
    cy: float
    radius: float


# Measured on 27 Flow renders: the sparkle spans x 576-623, y 1136-1183.
FLOW_WATERMARK_SPARKLE = SparkleMark(cx=599.5, cy=1159.5, radius=24.0)

# File types found in a scraped product zip.
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
VIDEO_SUFFIXES = (".mp4",)
TEXT_SUFFIXES = (".txt",)

# A Flow/Omni clip smaller than this is a failed or partial download, not a video.
MIN_FLOW_CLIP_BYTES = 100_000

# Extra video held after the narration ends so cuts between scenes do not clip speech.
SCENE_TAIL_PAD_SECONDS = 0.4

__all__ = [
    "FLOW_WATERMARK_SPARKLE",
    "SparkleMark",
    "IMAGE_SUFFIXES",
    "MIN_FLOW_CLIP_BYTES",
    "SCENE_TAIL_PAD_SECONDS",
    "TEXT_SUFFIXES",
    "VERTICAL_720P",
    "VIDEO_SUFFIXES",
    "VideoSpec",
]
