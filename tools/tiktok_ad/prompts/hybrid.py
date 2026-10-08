"""TikTok ``hybrid`` scenes: Flow AI mood shots alternating with the shop's real photos."""
from typing import List

from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, product_noun, spoken_name
from tools.common.prompts.registry import StoryContext


def build_hybrid_scenes(ctx: StoryContext) -> List[SceneDefinition]:
    clean_title = ctx.clean_title
    short_name = spoken_name(clean_title)
    return [
        SceneDefinition(
            id=1,
            name="Hook - Nhu cầu & Trải nghiệm thực tế",
            kind="FLOW_AI",
            narrator_text=f"Đang kiếm một món xài hằng ngày cho tiện thì coi thử {short_name} này nè.",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title[:28],
            image_index=0,
            prompt=(
                f"Two young Vietnamese friends sit at a small table in an ordinary coffee shop; one takes the {product_noun(ctx.category, clean_title)} out of a tote bag and the other leans in to look. "
                f"Iced drinks on the table, people in the background, daylight from the street. No speaking. NO packaging text."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero - Giới thiệu sản phẩm thật",
            kind="PRODUCT_PHOTO",
            narrator_text=f"Đây là {short_name}, làm gọn gàng, kỹ lắm.",
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
                f"The same young Vietnamese person uses the {product_noun(ctx.category, clean_title)} at home on the sofa, glances at it, then relaxes back with a small smile. "
                f"Lived-in living room, daylight. No speaking."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Tính năng nổi bật 2 & Đánh giá tốt",
            kind="PRODUCT_PHOTO",
            narrator_text=feature_line(ctx.feat2_title, ctx.feat2_desc, "Xài hằng ngày tiện lắm luôn."),
            overlay_title=ctx.social_proof_title,
            overlay_subtitle=ctx.feat2_title[:24],
            image_index=min(2, ctx.num_images - 1),
        ),
    ]


__all__ = ["build_hybrid_scenes"]
