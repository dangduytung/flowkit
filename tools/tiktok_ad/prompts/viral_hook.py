"""TikTok ``viral_hook`` scenes: an instant hook in the first 2-3 seconds.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo


def build_viral_hook_scenes(
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
    """Generate 4 fast-paced viral TikTok scenes with an instant hook in the first 2-3 seconds."""
    has_video = bool(product and product.video_name)
    num_images = len(product.image_names) if product and product.image_names else 1

    archetype = resolve_product_archetype(clean_title)

    # Hook question: archetype-specific copy first, then the broader category copy.
    if archetype == ProductArchetype.COMPRESSION_STORAGE:
        hook_text = f"Chuẩn bị đi du lịch hay dọn tủ mà quần áo cồng kềnh nhét mãi không vừa vali? Dùng ngay {clean_title} này xẹp 80% nha!"
        hook_title = "VALI CHẬT NÍCH?"
        hook_sub = "Hút Xẹp 80% Diện Tích"
    elif category == "HEALTH_FITNESS":
        hook_text = f"Cả ngày làm việc căng thẳng, cơ thể uể oải đau nhức khó chịu? Trải nghiệm ngay {clean_title} này đi, cảm giác khác biệt hoàn toàn luôn!"
        hook_title = "CƠ THỂ ĐAU NHỨC UỂ OẢI?"
        hook_sub = "Cứu Cánh Cho Bạn"
    elif category == "BEAUTY_SKINCARE":
        hook_text = f"Mặt mộc cứ sần sùi khô mốc làm bạn thiếu tự tin? Xem ngay bí quyết chăm da với {clean_title} này nhé!"
        hook_title = "DA KHÔ MỐC THIẾU TỰ TIN?"
        hook_sub = "Bí Quyết Căng Mịn"
    elif category == "TECH_GADGETS":
        hook_text = f"Bàn làm việc bừa bộn hoặc phụ kiện bất tiện làm giảm cảm hứng? Khám phá ngay giải pháp cực hay với {clean_title}!"
        hook_title = "BÀN SETUP QUÁ BỪA BỘN?"
        hook_sub = "Nâng Tầm Không Gian"
    elif category == "KITCHEN_HOME":
        hook_text = f"Gian bếp lộn xộn, dọn dẹp mất cả tiếng đồng hồ? Món đồ thông minh {clean_title} này sẽ cứu rỗi bạn!"
        hook_title = "DỌN DẸP MẤT THỜI GIAN?"
        hook_sub = "Tiện Lợi Gấp Đôi"
    elif category == "FASHION_APPAREL":
        hook_text = f"Mỗi sáng đứng trước tủ đồ không biết mặc gì vừa đẹp vừa tôn dáng? Khám phá ngay mẫu {clean_title} này nhé!"
        hook_title = "ĐAU ĐẦU CHỌN OUTFIT?"
        hook_sub = "Phối Đồ Cực Chuẩn"
    else:
        hook_text = f"Ai đang gặp phiền toái mỗi ngày mà chưa tìm được cách xử lý? Trải nghiệm ngay {clean_title} cực kỳ hữu ích này nhé!"
        hook_title = "BẠN ĐANG TÌM GIẢI PHÁP?"
        hook_sub = "Trải Nghiệm Đỉnh Cao"

    if category == "HEALTH_FITNESS":
        closing_phrase = "cho sức khỏe và tinh thần hàng ngày!"
    elif category == "BEAUTY_SKINCARE":
        closing_phrase = "cho nhan sắc và sự tự tin mỗi ngày!"
    elif category == "TECH_GADGETS":
        closing_phrase = "cho hiệu suất và trải nghiệm công nghệ mỗi ngày!"
    elif category == "KITCHEN_HOME":
        closing_phrase = "cho gian bếp và tổ ấm gia đình mỗi ngày!"
    elif category == "FASHION_APPAREL":
        closing_phrase = "cho phong cách và diện mạo mỗi ngày!"
    else:
        closing_phrase = "cho trải nghiệm và cuộc sống mỗi ngày!"

    scenes = [
        SceneDefinition(
            id=1,
            name="Hook - Nỗi đau & Thu hút 3s đầu",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=hook_text,
            overlay_title=hook_title,
            overlay_subtitle=hook_sub,
            real_start_sec=0.0,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW dynamic TikTok video. Close-up action demonstrating the daily frustration or immediate relief with {clean_title}. "
                f"Fast camera push-in, energetic pacing, sharp focus, vibrant natural indoor lighting. Mouth closed, no dialogue, NO text overlays."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Feature 1 - Trực diện thao tác giải pháp",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=f"{feat1_desc}. Cảm nhận sự thư giãn và tiện lợi ngay tức thì!",
            overlay_title=feat1_title[:24].upper(),
            overlay_subtitle="Thao Tác Cực Êm",
            real_start_sec=4.0 if has_video else 0.0,
            image_index=min(1, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW dynamic video. Macro close-up hands-on demonstration showing key feature in active use. "
                f"Crisp texture details, smooth movement, commercial B-roll lighting, 4K resolution. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature 2 - Cấu tạo & Độ bền công thái học",
            kind="PRODUCT_PHOTO",  # Use photo pan/zoom for rich visual variety
            narrator_text=f"{feat2_desc}. Hoàn thiện chắc chắn, thiết kế thông minh nâng tầm chất lượng sống.",
            overlay_title=feat2_title[:24].upper(),
            overlay_subtitle="Bền Chắc - Hoàn Thiện Tỉ Mỉ",
            real_start_sec=8.0 if has_video else 0.0,
            image_index=min(2, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW video. Smooth cinematic turntable rotation of {clean_title} in modern minimalist room. "
                f"High-end product showcase lighting, clean aesthetic background, shallow depth of field. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Social Proof & Chốt đơn",
            kind="REAL_FOOTAGE" if has_video else "PRODUCT_PHOTO",
            narrator_text=f"Sản phẩm nhận được rất nhiều phản hồi tích cực và đánh giá cao. Món đồ cực kỳ đáng đầu tư {closing_phrase}",
            overlay_title=social_proof_title,
            overlay_subtitle="Được Tin Dùng Hàng Đầu",
            real_start_sec=10.0 if has_video else 0.0,
            image_index=min(3, num_images - 1),
            prompt=(
                f"Vertical 9:16 RAW video. Happy user relaxing comfortably, smiling with pure satisfaction while using {clean_title}. "
                f"Warm inviting natural light, modern aesthetic space, confident peaceful vibe. Mouth closed, no dialogue. NO text overlays."
            ),
        ),
    ]
    return scenes


__all__ = ["build_viral_hook_scenes"]
