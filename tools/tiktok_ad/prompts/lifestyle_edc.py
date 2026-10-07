"""TikTok ``lifestyle_edc`` scenes.
"""
from typing import List, Optional

from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo


def build_lifestyle_edc_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    custom_idea: Optional[str] = None,
    product: Optional[ProductInfo] = None,
) -> List[SceneDefinition]:
    """Generate 4 active lifestyle scenes tailored to category."""
    has_video = bool(product and product.video_name)
    num_images = len(product.image_names) if product and product.image_names else 1
    idea_ctx = f" ({custom_idea})" if custom_idea else ""

    if category == "TECH_GADGETS":
        hook_sub = "Góc Làm Việc Hiện Đại"
        lifestyle_sub = "Nâng Tầm Không Gian"
    elif category == "HEALTH_FITNESS":
        hook_sub = "Sống Khỏe Mỗi Ngày"
        lifestyle_sub = "Thư Giãn Tối Đa"
    elif category == "BEAUTY_SKINCARE":
        hook_sub = "Tự Tin Rạng Rỡ"
        lifestyle_sub = "Đẹp Chuẩn Phong Cách"
    elif category == "KITCHEN_HOME":
        hook_sub = "Tổ Ấm Tiện Nghi"
        lifestyle_sub = "Không Gian Tinh Tươm"
    else:
        hook_sub = "Phong Cách Hiện Đại"
        lifestyle_sub = "Gọn Nhẹ Đồng Hành"

    return [
        SceneDefinition(
            id=1,
            name="Hook - Món đồ bất ly thân",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=f"Một món đồ nhỏ gọn nhưng cực kỳ đắc lực mà bạn nhất định phải có bên mình mỗi ngày! Khám phá ngay {clean_title} nhé!",
            overlay_title="MÓN ĐỒ BẤT LY THÂN",
            overlay_subtitle=hook_sub,
            real_start_sec=0.0,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young stylish Vietnamese creator packing everyday essentials into a minimalist leather bag at a sunlit aesthetic coffee shop. "
                f"Holding up {clean_title} with an appreciative smile. Mouth closed, no speaking, relaxed aesthetic lifestyle{idea_ctx}, 35mm lens. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Hoàn thiện tinh tế bền bỉ",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text="Chất liệu cao cấp chống va đập, chống hao mòn hoàn hảo. Thiết kế thông minh, luôn sẵn sàng khi bạn cần.",
            overlay_title="HOÀN THIỆN TINH TẾ",
            overlay_subtitle="Chất Liệu Cao Cấp - Bền Bỉ",
            real_start_sec=4.0 if has_video else 0.0,
            image_index=min(1, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using {clean_title} with smooth confident motions. "
                f"Crisp texture reflections, natural sunlight, premium commercial details. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Đồng hành mọi khoảnh khắc",
            kind="PRODUCT_PHOTO",
            narrator_text=f"{feat1_desc}. Đáp ứng hoàn hảo mọi nhu cầu, mang lại sự tiện nghi và tự tin tuyệt đối.",
            overlay_title=feat1_title[:24].upper(),
            overlay_subtitle="Tiện Lợi Vượt Trội",
            real_start_sec=8.0 if has_video else 0.0,
            image_index=min(2, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Creator happily enjoying their daily routine at an outdoor terrace with a scenic view, using {clean_title} with a peaceful focused expression. "
                f"Mouth closed, no speaking. Soft natural golden hour light. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Tự do & Năng động",
            kind="REAL_FOOTAGE" if has_video else "PRODUCT_PHOTO",
            narrator_text="Gọn gàng trong lòng bàn tay, người bạn đồng hành hoàn hảo cho phong cách sống hiện đại và năng động!",
            overlay_title="ĐỒNG HÀNH MỌI NƠI",
            overlay_subtitle=lifestyle_sub,
            real_start_sec=10.0 if has_video else 0.0,
            image_index=min(3, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Person zipping up their bag, holding {clean_title} gleaming in ambient light, walking away with upbeat dynamic energy. "
                f"Mouth closed, natural lighting, modern aesthetic. NO text overlays."
            ),
        ),
    ]


__all__ = ["build_lifestyle_edc_scenes"]
