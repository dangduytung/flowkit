"""Backward-compatible import path; the implementation lives in tools.common.media."""
from tools.common.media.cutplanner import calculate_smart_subclip_starts
from tools.common.media.extractor import (
    ExtractedAssets,
    create_hybrid_subclip,
    create_image_slide_clip,
    extract_vertical_subclip,
    extract_zip,
)

__all__ = [
    "ExtractedAssets",
    "calculate_smart_subclip_starts",
    "create_hybrid_subclip",
    "create_image_slide_clip",
    "extract_vertical_subclip",
    "extract_zip",
]
