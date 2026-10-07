"""TikTok call-to-action: folded into the last scene (yellow cart / bio link / follow)."""
from typing import List, Optional

from tools.common.models import SceneDefinition


def append_call_to_action(
    scenes: List[SceneDefinition],
    cta_mode: str,
    channel_name: Optional[str] = None,
) -> List[SceneDefinition]:
    """Dynamically modify Scene 4 to include a high-converting CTA."""
    if not scenes or cta_mode == "none":
        return scenes

    s4 = scenes[-1]
    original = s4.narrator_text.strip()
    if cta_mode in ("yellow_cart", "cart", "tiktok"):
        cta_phrase = "Bấm ngay vào giỏ hàng màu vàng ở góc dưới bên trái màn hình để săn ưu đãi nhé!"
        if "giỏ hàng màu vàng" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "GIỎ HÀNG GÓC TRÁI"
        s4.overlay_subtitle = "Bấm Săn Deal Hôm Nay"
    elif cta_mode in ("profile_bio", "bio"):
        cta_phrase = "Xem ngay link chi tiết sản phẩm tại link Bio trên trang cá nhân nha cả nhà!"
        if "Bio" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "LINK TRÊN BIO"
        s4.overlay_subtitle = "Bấm Vào Trang Cá Nhân"
    elif cta_mode == "follow":
        cta_phrase = "Bấm follow kênh để săn thêm nhiều deal hời và mẹo hay mỗi ngày nhé!"
        if "follow" not in original.lower():
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "FOLLOW KÊNH NHA"
        s4.overlay_subtitle = "Cập Nhật Deal Mỗi Ngày"

    return scenes


__all__ = ["append_call_to_action"]
