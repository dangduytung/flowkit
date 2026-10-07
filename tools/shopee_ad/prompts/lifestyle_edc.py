"""Shopee ``lifestyle_edc`` scenes: the product in an active everyday-carry routine.
"""
from typing import List, Optional

from tools.common.models import SceneDefinition


def build_lifestyle_edc_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """Generate 4 Aesthetic Lifestyle / Everyday Carry AI scenes tailored to category."""
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    return [
        SceneDefinition(
            id=1,
            name="Hook - Món đồ bất ly thân",
            kind="FLOW_AI",
            narrator_text=f"Một món đồ nhỏ gọn nhưng cực kỳ đắc lực mà bạn nhất định phải có bên mình mỗi ngày! Khám phá ngay {clean_title} nhé!",
            overlay_title="MÓN ĐỒ BẤT LY THÂN",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young stylish Vietnamese creator packing everyday essentials into a minimalist leather bag at a sunlit aesthetic coffee shop. "
                f"Holding up {clean_title} with an appreciative smile. Mouth closed, no speaking, relaxed aesthetic lifestyle{idea_ctx}, 35mm lens. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Hoàn thiện tinh tế bền bỉ",
            kind="FLOW_AI",
            narrator_text="Chất liệu cao cấp chống va đập, chống hao mòn hoàn hảo. Thiết kế thông minh, luôn sẵn sàng khi bạn cần.",
            overlay_title="HOÀN THIỆN TINH TẾ",
            overlay_subtitle="Chất liệu cao cấp - Bền bỉ",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using {clean_title} with smooth confident motions. "
                f"Crisp texture reflections, natural sunlight, premium commercial details. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Đồng hành mọi khoảnh khắc",
            kind="FLOW_AI",
            narrator_text=f"{feat1_desc}. Đáp ứng hoàn hảo mọi nhu cầu, mang lại sự tiện nghi và tự tin tuyệt đối.",
            overlay_title=feat1_title,
            overlay_subtitle="Tiện lợi vượt trội",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Creator happily enjoying their daily routine at an outdoor terrace with a scenic view, using {clean_title} with a peaceful focused expression. "
                f"Mouth closed, no speaking. Soft natural golden hour light. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Tự do & Năng động",
            kind="FLOW_AI",
            narrator_text="Gọn gàng trong lòng bàn tay, người bạn đồng hành hoàn hảo cho phong cách sống hiện đại và năng động!",
            overlay_title="ĐỒNG HÀNH MỌI NƠI",
            overlay_subtitle="Gọn nhẹ - An tâm tuyệt đối",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Person zipping up their bag, holding {clean_title} gleaming in ambient light, walking away with upbeat dynamic energy. "
                f"Mouth closed, natural lighting, modern aesthetic. NO text overlays."
            ),
        ),
    ]


__all__ = ["build_lifestyle_edc_scenes"]
