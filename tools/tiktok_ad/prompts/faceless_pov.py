"""TikTok ``faceless_pov`` scenes: hands-only demos from the shop's own footage/photos.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, spoken_name
from tools.common.product import ProductInfo


def build_faceless_pov_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    social_proof_title: str,
    custom_idea: Optional[str] = None,
    product: Optional[ProductInfo] = None,
) -> List[SceneDefinition]:
    """Generate 4 100% Faceless First-Person POV scenes (hands/feet only, macro close-ups)."""
    has_video = bool(product and product.video_name)
    num_images = len(product.image_names) if product and product.image_names else 1
    archetype = resolve_product_archetype(clean_title)
    short_name = spoken_name(clean_title)

    # Archetype-specific copy takes precedence over the broader category copy.
    if archetype == ProductArchetype.COMPRESSION_STORAGE:
        pov_summary_text = "Đồ cất cả mùa không lo ẩm mốc, kéo khóa vali nhẹ tênh, đi chơi thảnh thơi."
        pov_summary_title = "KÉO KHÓA NHẸ TÊNH"
        pov_summary_sub = "Bảo Vệ Chống Ẩm Mốc"
        pov_summary_prompt = (
            "Vertical 9:16 RAW POV shot of closed suitcase with zipper neatly pulled, neat luggage ready for travel. "
            "Warm natural morning light. Completely faceless."
        )
    elif archetype == ProductArchetype.VACUUM_CLEANER:
        pov_summary_text = "Bụi với tóc rụng hút cái là sạch, nhà cửa với xe lúc nào cũng gọn gàng."
        pov_summary_title = "SẠCH BÓNG TINH TƯƠM"
        pov_summary_sub = "Hút Sạch Mọi Góc Nhỏ"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of immaculate cozy living space with {clean_title} placed neatly on minimalist holder. "
            f"Sunlit warm atmosphere, spotless floor. Completely faceless."
        )
    elif category == "HEALTH_FITNESS":
        pov_summary_text = "Đầu tư nhỏ cho sức khỏe thôi mà ngày nào cũng thấy dễ chịu."
        pov_summary_title = "SỐNG KHỎE MỖI NGÀY"
        pov_summary_sub = "Lựa Chọn Hoàn Hảo"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of clean modern relaxation space with {clean_title} in its spot. "
            f"Warm natural sunlight, peaceful atmosphere, comfortable lifestyle. Completely faceless."
        )
    elif category == "BEAUTY_SKINCARE":
        pov_summary_text = "Thêm một bước chăm da đơn giản thôi mà ra đường tự tin hẳn."
        pov_summary_title = "NÂNG TẦM VẺ ĐẸP"
        pov_summary_sub = "Tự Tin Rạng Rỡ"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of aesthetic vanity table with {clean_title} neatly arranged. "
            f"Soft glowing lighting, clean minimalist beauty setup. Completely faceless."
        )
    elif category == "TECH_GADGETS":
        pov_summary_text = "Món nhỏ thôi mà góc làm việc gọn hẳn, làm việc cũng trơn tru hơn."
        pov_summary_title = "TỐI ƯU HIỆU SUẤT"
        pov_summary_sub = "Góc Setup Đẳng Cấp"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of clean tidy modern desk with {clean_title} in its perfect spot. "
            f"Warm morning sunlight, minimalist aesthetic, cozy workspace. Completely faceless."
        )
    elif category == "KITCHEN_HOME":
        pov_summary_text = "Có món này, nhà cửa gọn gàng, việc nhà nhàn hẳn."
        pov_summary_title = "TIỆN ÍCH GIA ĐÌNH"
        pov_summary_sub = "Không Gian Tinh Tươm"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of neat modern home setting with {clean_title} placed nicely. "
            f"Warm inviting ambient light, organized living space. Completely faceless."
        )
    elif category == "FASHION_APPAREL":
        pov_summary_text = "Mặc lên gọn dáng, đi đâu cũng thấy tự tin."
        pov_summary_title = "TỰ TIN TỎA SÁNG"
        pov_summary_sub = "Phong Cách Thời Thượng"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV mirror shot or flat-lay outfit presentation with {clean_title}. "
            f"Chic aesthetic room lighting, stylish wardrobe background. Completely faceless."
        )
    else:
        pov_summary_text = "Món nhỏ thôi mà xài mỗi ngày tiện lắm luôn."
        pov_summary_title = "NÂNG TẦM TRẢI NGHIỆM"
        pov_summary_sub = "Lựa Chọn Hoàn Hảo"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of modern aesthetic room with {clean_title} in its ideal place. "
            f"Warm natural sunlight, cozy minimalist atmosphere. Completely faceless."
        )

    sc3_prompt = (
        "Vertical 9:16 RAW macro POV shot. A sleek handheld vacuum cleaner with the brush nozzle already securely attached, sweeping smoothly across textured sofa fabric, picking up crumbs cleanly. Sharp 4K detail, studio lighting. NO faces visible."
        if archetype == ProductArchetype.VACUUM_CLEANER
        else (
            f"Vertical 9:16 RAW macro POV pan over texture, material finish and joints of {clean_title}. "
            f"Sharp 4K detail, studio commercial lighting. NO faces visible."
        )
    )

    return [
        SceneDefinition(
            id=1,
            name="POV Unboxing & Ấn tượng ban đầu",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=f"Mở hộp {short_name} ra coi nè. Cầm lên thấy đầm tay, làm kỹ lắm.",
            overlay_title="TRẢI NGHIỆM THỰC TẾ",
            overlay_subtitle=clean_title[:28],
            real_start_sec=0.0,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW POV shot from chest-down angle. Two hands holding and rotating {clean_title} on clean aesthetic desk, showcasing sleek finish. NO attaching parts, NO assembly. NO faces visible, completely faceless, mouth closed."
                if archetype == ProductArchetype.VACUUM_CLEANER
                else (
                    f"Vertical 9:16 RAW POV shot from chest-down angle. Two hands holding and unboxing {clean_title} on clean aesthetic surface. "
                    f"Crisp texture, premium packaging, shallow depth of field. NO faces visible, completely faceless, mouth closed."
                )
            ),
        ),
        SceneDefinition(
            id=2,
            name="POV Thao tác sử dụng trực tiếp",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=feature_line(feat1_title, feat1_desc, "Thao tác êm, mượt lắm."),
            overlay_title=feat1_title[:24].upper(),
            overlay_subtitle="Thao Tác Cực Êm",
            real_start_sec=4.0 if has_video else 0.0,
            image_index=min(1, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW macro POV shot. Close-up hands or feet interacting smoothly with {clean_title}. "
                f"Smooth mechanical action, tactile feedback, clean modern aesthetic surface. NO faces, completely faceless."
            ),
        ),
        SceneDefinition(
            id=3,
            name="POV Chi tiết công năng & Chất liệu",
            kind="PRODUCT_PHOTO",
            narrator_text=feature_line(feat2_title, feat2_desc, "Từng góc cạnh làm kỹ, đáng tiền."),
            overlay_title=feat2_title[:24].upper(),
            overlay_subtitle="Chất Liệu Bền Bỉ",
            real_start_sec=8.0 if has_video else 0.0,
            image_index=min(2, num_images - 1),
            prompt=sc3_prompt,
        ),
        SceneDefinition(
            id=4,
            name="POV Tổng kết hoàn thiện",
            kind="REAL_FOOTAGE" if has_video else "PRODUCT_PHOTO",
            narrator_text=pov_summary_text,
            overlay_title=pov_summary_title,
            overlay_subtitle=pov_summary_sub,
            real_start_sec=10.0 if has_video else 0.0,
            image_index=min(3, num_images - 1),
            prompt=pov_summary_prompt,
        ),
    ]


__all__ = ["build_faceless_pov_scenes"]
