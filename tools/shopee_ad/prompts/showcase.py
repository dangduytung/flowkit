"""Shopee ``hybrid`` (Flow AI mood shots + real photos) and ``local`` (shop footage only) scenes."""
from typing import List

from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, spoken_name
from tools.common.prompts.registry import StoryContext


def build_hybrid_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    """Flow AI for the emotional beats, the shop's real photos for the product itself."""
    clean_title = ctx.clean_title
    short_name = spoken_name(clean_title)
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu & Trải nghiệm thực tế",
            kind="FLOW_AI",
            narrator_text=f"Đang kiếm một món xài hằng ngày cho tiện thì coi thử {short_name} này nè.",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                "Three young Vietnamese friends sit around a small table in an ordinary coffee shop; one puts her phone down and the others lean in to look at something on the table. "
                "Glasses of iced tea, bags on the chairs, daylight from the street, people chatting in the background. No speaking. NO packaging, NO cards."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm thật",
            kind="PRODUCT_PHOTO",
            narrator_text=f"Đây là {short_name}, nhỏ gọn, cầm đầm tay, làm kỹ lắm.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Chính hãng - Hoàn thiện tỉ mỉ",
            image_index=0,
        ),
        SceneDefinition(
            id=3,
            name="Tính năng nổi bật 1",
            kind="FLOW_AI",
            narrator_text=ctx.feat1_desc,
            overlay_title=ctx.feat1_title,
            overlay_subtitle="Trải nghiệm tiện lợi vượt trội",
            image_index=min(1, ctx.num_images - 1),
            prompt=(
                "The same young Vietnamese friends laugh at something one of them said, one covering her mouth, another leaning back in his chair. "
                "Ordinary coffee shop, daylight, natural candid moment. No speaking. NO packaging."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2 & Đánh giá tốt",
            kind="PRODUCT_PHOTO",
            narrator_text=feature_line(ctx.feat2_title, ctx.feat2_desc, "Xài hằng ngày tiện lắm luôn."),
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:28],
            image_index=min(2, ctx.num_images - 1),
        ),
    ]


def build_local_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    """Everything from the zip: shop footage when there is a video, photo slides otherwise."""
    clean_title = ctx.clean_title
    short_name = spoken_name(clean_title)
    kind = "REAL_FOOTAGE" if ctx.has_video else "IMAGE_SLIDE"
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu thực tế",
            kind=kind,
            narrator_text=f"Đang kiếm một món vừa tốt vừa tiện thì coi thử {short_name} này nè.",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title,
            image_index=0,
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm",
            kind=kind,
            narrator_text=f"Đây là {short_name}, kiểu dáng gọn gàng, cầm chắc tay, xài hằng ngày tiện lắm.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Nhỏ gọn - Cực kỳ tiện dụng",
            image_index=min(1, ctx.num_images - 1),
        ),
        SceneDefinition(
            id=3,
            name="Tính năng nổi bật 1",
            kind=kind,
            narrator_text=feature_line(ctx.feat1_title, ctx.feat1_desc, "Mấy chi tiết làm kỹ, cầm lên là thấy yên tâm."),
            overlay_title=ctx.feat1_title,
            overlay_subtitle="Hiệu năng mượt mà",
            image_index=min(2, ctx.num_images - 1),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2",
            kind=kind,
            narrator_text=feature_line(ctx.feat2_title, ctx.feat2_desc, "Xài hằng ngày tiện lắm luôn."),
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:28],
            image_index=min(3, ctx.num_images - 1),
        ),
    ]


__all__ = ["build_hybrid_scenes", "build_local_scenes"]
