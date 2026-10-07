"""TikTok cover: hook title from scene 1 over a frame of the video."""
from pathlib import Path
from typing import List, Optional

from tools.common.media.cover import CoverStyle, create_cover_frame, format_cover_text
from tools.common.models import SceneDefinition
from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.storyboard import clean_product_title

COVER_STYLE = CoverStyle(hook_max_chars=26, hook_font_tiers=((23, 44), (17, 50), (0, 54)))
DEFAULT_HOOK_TITLE = "SIÊU PHẨM TIỆN ÍCH"

# Kept for callers/tests that used the module-private name.
_format_cover_text = format_cover_text


def create_cover_image(
    source_clip_or_video: Path,
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_cover_path: Path,
    time_offset_s: float = 1.2,
    delogo: Optional[str] = None,
) -> Path:
    """Cover with scene 1's overlay title as the hook and the cleaned product name below."""
    hook = scenes[0].overlay_title if scenes and scenes[0].overlay_title else DEFAULT_HOOK_TITLE
    return create_cover_frame(
        source_clip_or_video,
        hook_title=hook,
        subtitle=clean_product_title(product.name),
        output_path=output_cover_path,
        style=COVER_STYLE,
        time_offset_s=time_offset_s,
        delogo=delogo,
    )


__all__ = ["COVER_STYLE", "create_cover_image"]
