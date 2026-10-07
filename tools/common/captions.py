"""Caption building blocks; the copy itself stays in each platform package."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo

# Scenes whose overlay text summarises a feature (1 is the hook, 5 the CTA).
FEATURE_SCENE_IDS = (2, 3, 4)
MAX_BULLETS = 3
FALLBACK_BULLETS = (
    "• Thiết kế thông minh, hoàn thiện cao cấp",
    "• Tiện lợi, bền bỉ và nâng tầm chất lượng sống",
)

# (product, scenes, output_path, channel_name, channel_handle) -> caption text
CaptionWriter = Callable[[ProductInfo, Sequence[SceneDefinition], Path, str, str], str]

# Platform key -> file suffix of its caption in the final folder.
CAPTION_FILES = {
    "facebook": "facebook_caption.txt",
    "tiktok": "tiktok_caption.txt",
    "youtube": "youtube_shorts.txt",
}


def feature_bullets(scenes: Sequence[SceneDefinition]) -> str:
    """Up to three "• title: subtitle" lines taken from the feature scenes."""
    lines = [
        f"• {s.overlay_title}: {s.overlay_subtitle}"
        for s in scenes
        if s.overlay_title and s.overlay_subtitle and s.id in FEATURE_SCENE_IDS
    ]
    return "\n".join((lines or list(FALLBACK_BULLETS))[:MAX_BULLETS])


def write_caption(output_path: Path, caption: str) -> str:
    """Save a caption (trimmed) and return it."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = caption.strip()
    output_path.write_text(text, encoding="utf-8")
    return text


def write_caption_set(
    writers: Mapping[str, CaptionWriter],
    product: ProductInfo,
    scenes: Sequence[SceneDefinition],
    final_dir: Path,
    channel_name: str,
    channel_handle: str,
    variant_suffix: Optional[str] = None,
) -> dict[str, Path]:
    """Run each platform writer into ``<slug>[_<variant>]_<suffix>``; returns the paths."""
    prefix = f"{product.slug}_{variant_suffix}" if variant_suffix else product.slug
    paths = {}
    for key, writer in writers.items():
        path = Path(final_dir) / f"{prefix}_{CAPTION_FILES[key]}"
        writer(product, scenes, path, channel_name, channel_handle)
        paths[key] = path
    return paths


__all__ = ["CAPTION_FILES", "CaptionWriter", "feature_bullets", "write_caption", "write_caption_set"]
