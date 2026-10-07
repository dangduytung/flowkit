"""Shopee closing call-to-action scene (follow / Shopee cart / TikTok cart).
"""
from typing import List, Optional

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

    if cta_mode == "follow":
        persona = character_persona(category)
        overlay_t = f"FOLLOW {channel_name.upper()}" if channel_name else "BẤM FOLLOW KÊNH"
        if category == "FASHION_APPAREL":
            cta_txt = "Bạn nào cũng mê phong cách chỉn chu, gọn gàng thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"
        elif category == "BEAUTY_SKINCARE":
            cta_txt = "Bạn nào cũng mê chăm sóc bản thân, làm đẹp thảnh thơi thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"
        else:
            cta_txt = "Bạn nào cũng mê không gian ngăn nắp, thảnh thơi thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"

        if is_faceless:
            follow_prompt = (
                "Vertical 9:16 RAW cinematic video. First-person POV looking down at clean aesthetic table, hands resting calmly beside the neat setup. "
                "Warm modern ambient lighting. NO human face, NO head in frame, hands only. NO thumbs-up, NO peace sign, strictly exactly 5 fingers. NO text overlays."
            )
        else:
            follow_prompt = (
                f"Vertical 9:16 RAW cinematic video. Featuring {persona['cont']}, giving a gentle wave and warm genuine smile to camera in a modern tidy aesthetic room. "
                f"Natural modern aesthetic lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
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
                "Vertical 9:16 RAW cinematic video. Macro POV shot looking down at product neatly displayed on desk, hand pointing down toward comments. "
                "Bright commercial aesthetic lighting. NO human face, hands only. NO thumbs-up, strictly 5 fingers. NO text overlays."
            )
        else:
            shopee_prompt = (
                "Vertical 9:16 RAW cinematic video. Happy young Vietnamese creator smiling warmly at the camera, giving a polite welcoming nod. "
                "Mouth closed, no speaking, bright vibrant ambient lighting. NO thumbs-up. NO text overlays."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động Shopee (CTA)",
            kind=kind,
            narrator_text="Món này tiện lợi thực sự! Mình để link chính hãng dưới phần bình luận cho các bạn tham khảo nhé!",
            overlay_title="LINK Ở BÌNH LUẬN GHIM",
            overlay_subtitle="Chính hãng - Giá cực tốt",
            image_index=0,
            prompt=shopee_prompt,
        )

    elif cta_mode in ("tiktok", "tiktok_shop"):
        if is_faceless:
            tiktok_prompt = (
                "Vertical 9:16 RAW cinematic video. Macro POV shot looking down at product, hand gesturing toward the lower left corner. "
                "Bright commercial aesthetic lighting. NO human face, hands only. NO text overlays."
            )
        else:
            tiktok_prompt = (
                "Vertical 9:16 RAW cinematic video. Young Vietnamese creator pointing enthusiastically toward lower-left corner with friendly smile. "
                "Mouth closed, no speaking, bright vibrant lighting. NO text overlays."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động TikTok Shop (CTA)",
            kind=kind,
            narrator_text="Món này tiện lợi thực sự! Các bạn bấm ngay vào giỏ hàng màu vàng góc trái để nhận ưu đãi hôm nay nhé!",
            overlay_title="GIỎ HÀNG GÓC TRÁI",
            overlay_subtitle="Bấm nhận ưu đãi hôm nay",
            image_index=0,
            prompt=tiktok_prompt,
        )

    return None


__all__ = ["build_cta_scene"]
