"""Shopee ``lifestyle_edc`` scenes: the product in an active everyday-carry routine.
"""
from typing import List, Optional

from tools.common.models import SceneDefinition
from tools.common.prompts.personas import character_persona
from tools.common.prompts.realism import feature_line, product_noun, spoken_name


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
    persona = character_persona(category)
    noun = product_noun(category, clean_title)
    short_name = spoken_name(clean_title)
    return [
        SceneDefinition(
            id=1,
            name="Hook - Món đồ bất ly thân",
            kind="FLOW_AI",
            narrator_text=f"Món nhỏ gọn mà ngày nào cũng cần tới, coi thử {short_name} này nè.",
            overlay_title="MÓN ĐỒ BẤT LY THÂN",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"{persona['intro']} sits at a small table in a busy Vietnamese coffee shop, takes the {noun} out of a canvas tote bag and sets it on the table{idea_ctx}. "
                f"Iced coffee glass sweating on the table, people blurred in the background, daylight from the street, not talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Hoàn thiện tinh tế bền bỉ",
            kind="FLOW_AI",
            narrator_text="Làm chắc chắn, va chạm nhẹ cũng không sao, cần là lấy ra xài liền.",
            overlay_title="HOÀN THIỆN TINH TẾ",
            overlay_subtitle="Chất liệu cao cấp - Bền bỉ",
            image_index=0,
            prompt=(
                f"Close-up of hands at the coffee shop table, no face: hands use the {noun} once, slowly and simply, the way it is normally used. "
                f"A coffee ring and a phone on the table. Hands only."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Đồng hành mọi khoảnh khắc",
            kind="FLOW_AI",
            narrator_text=feature_line(feat1_title, feat1_desc, "Đi đâu mang theo cũng tiện."),
            overlay_title=feat1_title,
            overlay_subtitle="Tiện lợi vượt trội",
            image_index=0,
            prompt=(
                f"{persona['cont']} uses the {noun} while sitting on a plastic stool at a street-side table, glancing at it and then out at the street. Overcast daylight, not talking."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Tự do & Năng động",
            kind="FLOW_AI",
            narrator_text="Gọn vừa lòng bàn tay, bỏ túi mang theo cả ngày.",
            overlay_title="ĐỒNG HÀNH MỌI NƠI",
            overlay_subtitle="Gọn nhẹ - An tâm tuyệt đối",
            image_index=0,
            prompt=(
                f"{persona['cont']} puts the {noun} back into the tote bag, stands up and walks out of the coffee shop. Daylight, not talking."
            ),
        ),
    ]


__all__ = ["build_lifestyle_edc_scenes"]
