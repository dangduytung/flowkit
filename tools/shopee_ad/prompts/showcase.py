"""Shopee ``hybrid`` (Flow AI mood shots + real photos) and ``local`` (shop footage only) scenes."""
from typing import List

from tools.common.models import SceneDefinition
from tools.common.prompts.registry import StoryContext


def build_hybrid_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    """Flow AI for the emotional beats, the shop's real photos for the product itself."""
    clean_title = ctx.clean_title
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu & Trải nghiệm thực tế",
            kind="FLOW_AI",
            narrator_text=f"Bạn đang tìm một món đồ thật ưng ý và tiện dụng mỗi ngày? Cùng mình trải nghiệm {clean_title} này nhé!",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                "Vertical 9:16 RAW cinematic video. Three stylish young Vietnamese friends hanging out in a modern cafe, "
                "putting phones down and showing great curiosity and energetic excitement. "
                "Warm cozy ambient lighting, shot on 35mm lens. Mouth closed, no speaking. NO fake packaging, NO cards."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm thật",
            kind="PRODUCT_PHOTO",
            narrator_text=f"Đây là {clean_title}, thiết kế nhỏ gọn, cầm đầm tay và hoàn thiện cực kỳ chỉn chu.",
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
                "Vertical 9:16 RAW cinematic video. Young expressive Vietnamese friends laughing and smiling happily, "
                "enjoying a fun moment together in a modern stylish setting. Natural cinematic lighting. Mouth closed, no speaking. NO fake packaging."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2 & Đánh giá tốt",
            kind="PRODUCT_PHOTO",
            narrator_text=f"{ctx.feat2_desc}. Sản phẩm được rất nhiều người dùng đánh giá tốt và tin tưởng sử dụng.",
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:28],
            image_index=min(2, ctx.num_images - 1),
        ),
    ]


def build_local_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    """Everything from the zip: shop footage when there is a video, photo slides otherwise."""
    clean_title = ctx.clean_title
    kind = "REAL_FOOTAGE" if ctx.has_video else "IMAGE_SLIDE"
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu thực tế",
            kind=kind,
            narrator_text=f"Bạn đang tìm một món đồ vừa chất lượng vừa tiện lợi cho {clean_title}? Cùng mình khám phá trải nghiệm thực tế ngay trong video này nhé!",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title,
            image_index=0,
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm",
            kind=kind,
            narrator_text=f"Đây là chiếc {clean_title}, thiết kế tối giản thông minh, cầm đầm tay chắc chắn và cực kỳ tiện dụng mỗi ngày.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Nhỏ gọn - Cực kỳ tiện dụng",
            image_index=min(1, ctx.num_images - 1),
        ),
        SceneDefinition(
            id=3,
            name="Tính năng nổi bật 1",
            kind=kind,
            narrator_text=f"{ctx.feat1_desc}. Mọi chi tiết hoàn thiện chỉn chu, mang lại cảm giác an tâm và hài lòng tuyệt đối khi sử dụng.",
            overlay_title=ctx.feat1_title,
            overlay_subtitle="Hiệu năng mượt mà",
            image_index=min(2, ctx.num_images - 1),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2",
            kind=kind,
            narrator_text=f"{ctx.feat2_desc}. Sản phẩm được rất nhiều bạn đánh giá cao và tin dùng sau khi trực tiếp trải nghiệm.",
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:28],
            image_index=min(3, ctx.num_images - 1),
        ),
    ]


__all__ = ["build_hybrid_scenes", "build_local_scenes"]
