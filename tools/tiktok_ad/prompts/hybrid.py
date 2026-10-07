"""TikTok ``hybrid`` scenes: Flow AI mood shots alternating with the shop's real photos."""
from typing import List

from tools.common.models import SceneDefinition
from tools.common.prompts.registry import StoryContext


def build_hybrid_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    clean_title = ctx.clean_title
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu & Trải nghiệm thực tế",
            kind="FLOW_AI",
            narrator_text=f"Bạn đang tìm một món đồ thật ưng ý và tiện dụng mỗi ngày? Cùng mình trải nghiệm {clean_title} này nhé!",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title[:28],
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Two stylish young Vietnamese friends discovering {clean_title} with genuine curiosity and excitement. "
                f"Warm cozy ambient lighting, shot on 35mm lens. Mouth closed, no speaking. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm thật",
            kind="PRODUCT_PHOTO",
            narrator_text=f"Đây là {clean_title}, thiết kế thông minh, hoàn thiện cực kỳ chỉn chu.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Chính Hãng - Hoàn Thiện Tỉ Mỉ",
            image_index=0,
        ),
        SceneDefinition(
            id=3,
            name="Tính năng nổi bật 1",
            kind="FLOW_AI",
            narrator_text=ctx.feat1_desc,
            overlay_title=ctx.feat1_title[:24].upper(),
            overlay_subtitle="Trải Nghiệm Vượt Trội",
            image_index=min(1, ctx.num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young expressive person smiling happily while using {clean_title} in modern setting. "
                f"Natural cinematic lighting. Mouth closed, no speaking. NO fake packaging."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2 & Đánh giá tốt",
            kind="PRODUCT_PHOTO",
            narrator_text=f"{ctx.feat2_desc}. Sản phẩm được rất nhiều người dùng đánh giá tốt và tin tưởng sử dụng.",
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:24],
            image_index=min(2, ctx.num_images - 1),
        ),
    ]


__all__ = ["build_hybrid_scenes"]
