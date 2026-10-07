"""Shared, platform-neutral constants for the ad pipelines.

Anything that differs between Shopee and TikTok belongs in that package's config,
not here.
"""
from __future__ import annotations

# A Flow/Omni clip smaller than this is a failed or partial download, not a video.
MIN_FLOW_CLIP_BYTES = 100_000

# Extra video held after the narration ends so cuts between scenes do not clip speech.
SCENE_TAIL_PAD_SECONDS = 0.4

__all__ = ["MIN_FLOW_CLIP_BYTES", "SCENE_TAIL_PAD_SECONDS"]
