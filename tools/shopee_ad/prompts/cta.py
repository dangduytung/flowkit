"""Shopee closing call-to-action scene (follow / Shopee cart / TikTok cart).
"""
from typing import Optional

from tools.common.models import SceneDefinition
from tools.common.prompts.personas import character_persona


def build_cta_scene(
    scene_id: int,
    cta_mode: str,
    category: str,
    style: str,
    clean_title: str,
    channel_name: Optional[str] = None,
    is_local: bool = False,
    has_video: bool = False,
) -> Optional[SceneDefinition]:
    """Build CTA / Outro scene tailored to platform and style."""
    is_faceless = style in ("faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov")
    kind = "FLOW_AI" if not is_local else ("REAL_FOOTAGE" if has_video else "IMAGE_SLIDE")
    persona = character_persona(category)

    if cta_mode == "follow":
        overlay_t = f"FOLLOW {channel_name.upper()}" if channel_name else "BẤM FOLLOW KÊNH"
        if category == "FASHION_APPAREL":
            cta_txt = "Ai thích ăn mặc gọn gàng thì follow kênh nha, mỗi ngày đều có mẹo hay."
        elif category == "BEAUTY_SKINCARE":
            cta_txt = "Ai mê chăm da, làm đẹp nhẹ nhàng thì follow kênh nha, mỗi ngày đều có mẹo hay."
        else:
            cta_txt = "Ai thích nhà cửa gọn gàng thì follow kênh nha, mỗi ngày đều có mẹo hay."

        if is_faceless:
            follow_prompt = (
                "First-person view looking down at a home table, no face: a hand sets the product down next to a mug and rests flat on the table beside it. "
                "Daylight from the window. Hands only. NO thumbs-up, NO peace sign."
            )
        else:
            follow_prompt = (
                f"{persona['cont']} glances up toward the camera, gives a small casual wave and a relaxed smile, then looks away. "
                f"Lived-in room at home, daylight, not talking."
            )

        return SceneDefinition(
            id=scene_id,
            name="Outro - Kêu gọi Follow Kênh",
            kind=kind,
            narrator_text=cta_txt,
            overlay_title=overlay_t,
            overlay_subtitle="Mẹo hay & Tiện ích mỗi ngày",
            image_index=0,
            prompt=follow_prompt,
        )

    elif cta_mode == "shopee":
        if is_faceless:
            shopee_prompt = (
                "First-person view looking down at a desk, no face: a hand picks up the product, holds it toward the camera for a moment and sets it back down. "
                "Daylight. Hands only. NO thumbs-up."
            )
        else:
            shopee_prompt = (
                f"{persona['cont']} holds the product up toward the camera for a moment, gives a small nod and lowers it. "
                f"Room at home, daylight, not talking. NO thumbs-up."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động Shopee (CTA)",
            kind=kind,
            narrator_text="Món này xài tiện thiệt sự. Link mình để dưới bình luận nha.",
            overlay_title="LINK Ở BÌNH LUẬN GHIM",
            overlay_subtitle="Chính hãng - Giá cực tốt",
            image_index=0,
            prompt=shopee_prompt,
        )

    elif cta_mode in ("tiktok", "tiktok_shop"):
        if is_faceless:
            tiktok_prompt = (
                "First-person view looking down at a desk, no face: a hand picks up the product, holds it toward the camera for a moment and sets it back down. "
                "Daylight. Hands only. NO thumbs-up."
            )
        else:
            tiktok_prompt = (
                f"{persona['cont']} holds the product up toward the camera for a moment, gives a small nod and lowers it. "
                f"Room at home, daylight, not talking. NO thumbs-up."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động TikTok Shop (CTA)",
            kind=kind,
            narrator_text="Món này xài tiện thiệt sự. Bấm vô giỏ hàng màu vàng góc trái để coi ưu đãi hôm nay nha.",
            overlay_title="GIỎ HÀNG GÓC TRÁI",
            overlay_subtitle="Bấm nhận ưu đãi hôm nay",
            image_index=0,
            prompt=tiktok_prompt,
        )

    return None


__all__ = ["build_cta_scene"]
