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
        cta_phrase = "Bấm vô giỏ hàng màu vàng góc trái để săn ưu đãi nha!"
        if "giỏ hàng màu vàng" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "GIỎ HÀNG GÓC TRÁI"
        s4.overlay_subtitle = "Bấm Săn Deal Hôm Nay"
    elif cta_mode in ("profile_bio", "bio"):
        cta_phrase = "Link chi tiết mình để ở Bio trang cá nhân nha."
        if "Bio" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "LINK TRÊN BIO"
        s4.overlay_subtitle = "Bấm Vào Trang Cá Nhân"
    elif cta_mode == "follow":
        cta_phrase = "Follow kênh nha, mỗi ngày đều có deal với mẹo hay."
        if "follow" not in original.lower():
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "FOLLOW KÊNH NHA"
        s4.overlay_subtitle = "Cập Nhật Deal Mỗi Ngày"

    return scenes


__all__ = ["append_call_to_action"]
