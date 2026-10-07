"""TikTok Ad Prompts & AI Scene Generator Templates.
Dedicated to viral hooks, physical product categories, macro POV B-roll, KOC personas, and TikTok Shop CTAs.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.common.models import SceneDefinition
from tools.shopee_ad.prompts import _build_flow_cinematic_scenes
from tools.tiktok_ad.product_parser import ProductInfo


def _get_character_persona(category: str) -> dict:
    """
    Return consistent, explicit physical character personas (intro, continuation)
    for each product category to enforce visual continuity across Google Flow scenes.
    """
    if category in ("BEAUTY_SKINCARE", "FASHION_APPAREL"):
        return {
            "intro": "a stylish 24-year-old Vietnamese young woman with shoulder-length soft straight black hair, clear radiant skin, wearing an aesthetic beige knit top",
            "cont": "the same 24-year-old Vietnamese young woman with shoulder-length soft black hair, clear skin, and beige knit top",
        }
    elif category in ("HEALTH_FITNESS", "TECH_GADGETS"):
        return {
            "intro": "a modern 25-year-old Vietnamese office worker with neat short black hair, fit build, wearing a clean casual navy polo and dark chinos",
            "cont": "the same 25-year-old Vietnamese office worker with short black hair and navy polo",
        }
    elif category == "KITCHEN_HOME":
        return {
            "intro": "a friendly 26-year-old Vietnamese homemaker with neat ponytail black hair, warm smile, wearing a casual white t-shirt under a light beige apron",
            "cont": "the same friendly 26-year-old Vietnamese homemaker with neat ponytail black hair and beige apron",
        }
    else:  # GENERAL_LIFESTYLE
        return {
            "intro": "a dynamic 25-year-old Vietnamese creator with neat short black hair, friendly expressive face, wearing a comfortable heather grey crew-neck tee",
            "cont": "the same 25-year-old Vietnamese creator with short black hair and heather grey tee",
        }


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

    # Archetype-specific copy takes precedence over the broader category copy.
    if archetype == ProductArchetype.COMPRESSION_STORAGE:
        pov_summary_text = "Bảo vệ quần áo chống ẩm mốc bụi bẩn suốt 6-8 tháng, kéo khóa vali nhẹ tênh, đi du lịch cực kỳ thảnh thơi!"
        pov_summary_title = "KÉO KHÓA NHẸ TÊNH"
        pov_summary_sub = "Bảo Vệ Chống Ẩm Mốc"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV shot of closed suitcase with zipper neatly pulled, neat luggage ready for travel. "
            f"Warm natural morning light. Completely faceless."
        )
    elif archetype == ProductArchetype.VACUUM_CLEANER:
        pov_summary_text = "Hút sạch mọi bụi mịn và tóc rụng trong tích tắc, nhà cửa và xe hơi lúc nào cũng sạch bóng tinh tươm!"
        pov_summary_title = "SẠCH BÓNG TINH TƯƠM"
        pov_summary_sub = "Hút Sạch Mọi Góc Nhỏ"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of immaculate cozy living space with {clean_title} placed neatly on minimalist holder. "
            f"Sunlit warm atmosphere, spotless floor. Completely faceless."
        )
    elif category == "HEALTH_FITNESS":
        pov_summary_text = "Một sự đầu tư nhỏ cho sức khỏe nhưng mang lại sự thoải mái và năng lượng tích cực mỗi ngày!"
        pov_summary_title = "SỐNG KHỎE MỖI NGÀY"
        pov_summary_sub = "Lựa Chọn Hoàn Hảo"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of clean modern relaxation space with {clean_title} in its spot. "
            f"Warm natural sunlight, peaceful atmosphere, comfortable lifestyle. Completely faceless."
        )
    elif category == "BEAUTY_SKINCARE":
        pov_summary_text = "Một bước chăm sóc đơn giản nhưng nâng tầm vẻ đẹp tự nhiên và sự tự tin rạng ngời mỗi ngày!"
        pov_summary_title = "NÂNG TẦM VẺ ĐẸP"
        pov_summary_sub = "Tự Tin Rạng Rỡ"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of aesthetic vanity table with {clean_title} neatly arranged. "
            f"Soft glowing lighting, clean minimalist beauty setup. Completely faceless."
        )
    elif category == "TECH_GADGETS":
        pov_summary_text = "Một món đồ công nghệ đáng giá, giúp tối ưu hiệu suất và nâng tầm góc làm việc hiện đại!"
        pov_summary_title = "TỐI ƯU HIỆU SUẤT"
        pov_summary_sub = "Góc Setup Đẳng Cấp"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of clean tidy modern desk with {clean_title} in its perfect spot. "
            f"Warm morning sunlight, minimalist aesthetic, cozy workspace. Completely faceless."
        )
    elif category == "KITCHEN_HOME":
        pov_summary_text = "Một trợ thủ đắc lực giúp không gian sống gọn gàng và việc nhà trở nên nhàn tênh mỗi ngày!"
        pov_summary_title = "TIỆN ÍCH GIA ĐÌNH"
        pov_summary_sub = "Không Gian Tinh Tươm"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of neat modern home setting with {clean_title} placed nicely. "
            f"Warm inviting ambient light, organized living space. Completely faceless."
        )
    elif category == "FASHION_APPAREL":
        pov_summary_text = "Một item hoàn hảo tôn dáng và giúp bạn tự tin toả sáng trong mọi khoảnh khắc thường nhật!"
        pov_summary_title = "TỰ TIN TỎA SÁNG"
        pov_summary_sub = "Phong Cách Thời Thượng"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV mirror shot or flat-lay outfit presentation with {clean_title}. "
            f"Chic aesthetic room lighting, stylish wardrobe background. Completely faceless."
        )
    else:
        pov_summary_text = "Một món đồ nhỏ nhưng mang lại tiện ích vượt trội, nâng cấp chất lượng cuộc sống mỗi ngày!"
        pov_summary_title = "NÂNG TẦM TRẢI NGHIỆM"
        pov_summary_sub = "Lựa Chọn Hoàn Hảo"
        pov_summary_prompt = (
            f"Vertical 9:16 RAW POV wide shot of modern aesthetic room with {clean_title} in its ideal place. "
            f"Warm natural sunlight, cozy minimalist atmosphere. Completely faceless."
        )

    sc3_prompt = (
        f"Vertical 9:16 RAW macro POV shot. A sleek handheld vacuum cleaner with the brush nozzle already securely attached, sweeping smoothly across textured sofa fabric, picking up crumbs cleanly. Sharp 4K detail, studio lighting. NO faces visible."
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
            narrator_text=f"Cùng mình unbox và trải nghiệm thực tế chiếc {clean_title} này nhé. Cầm trên tay đầm chắc và hoàn thiện rất xịn.",
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
            narrator_text=f"{feat1_desc}. Mọi thao tác đều cực kỳ mượt mà và êm ái.",
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
            narrator_text=f"{feat2_desc}. Từng góc cạnh được chăm chút tỉ mỉ, rất đáng tiền.",
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


def build_problem_solution_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    custom_idea: Optional[str] = None,
    product: Optional[ProductInfo] = None,
) -> List[SceneDefinition]:
    """Generate 4 Problem-Solution drama scenes."""
    has_video = bool(product and product.video_name)
    num_images = len(product.image_names) if product and product.image_names else 1
    archetype = resolve_product_archetype(clean_title)

    # Archetype-specific copy takes precedence over the broader category copy.
    if archetype == ProductArchetype.COMPRESSION_STORAGE:
        prob_title = "ĐỒ CỒNG KỀNH CHẬT CHỖ?"
        prob_text = "Mỗi lần chuyển mùa hay chuẩn bị đi xa, nhìn đống chăn màn, áo phao cồng kềnh chất đống chiếm hết cả phòng mà phát ngợp đúng không? Thử ngay cách này nha!"
        sol_text = f"Dùng {clean_title} này xem. Khóa zip đôi kín khít, van silicon một chiều hút sạch không khí, nén xẹp phẳng lì chỉ sau 10 giây, giảm ngay 80% diện tích!"
        satisfaction_text = "Chất liệu PA PE dẻo dai dày dặn, dọn tủ hay xếp vali đều gọn gàng, thảnh thơi lên đường tận hưởng chuyến đi!"
    elif archetype == ProductArchetype.VACUUM_CLEANER:
        prob_title = "BỤI BẨN KẼ HẸP KHÓ LAU?"
        prob_text = "Vụn bánh trên sofa, bụi mịn kẽ bàn phím hay góc hẹp trong xe hơi cứ lau hoài không sạch làm bạn khó chịu? Đừng lo!"
        sol_text = f"Chiếc {clean_title} lực hút cực mạnh này xử lý gọn lẹ chỉ trong 3 giây. Đầu hút đa năng len lỏi mọi ngóc ngách!"
        satisfaction_text = "Góc làm việc, sofa hay xe hơi lúc nào cũng tinh tươm sạch bóng, nhẹ nhàng thảnh thơi mỗi ngày!"
    elif category == "HEALTH_FITNESS":
        prob_title = "ĐAU MỎI CƠ THỂ?"
        prob_text = f"Cả ngày làm việc căng thẳng, cơ thể đau mỏi uể oải không tập trung nổi? Đừng chủ quan nữa!"
        sol_text = f"Chiếc {clean_title} này chính là giải pháp cứu cánh. Trải nghiệm là cảm nhận ngay sự nhẹ nhõm và thư giãn."
        satisfaction_text = "Làm việc năng suất hơn hẳn, tạm biệt hoàn toàn cảm giác nhức mỏi mỗi khi tan ca!"
    elif category == "BEAUTY_SKINCARE":
        prob_title = "LÀN DA THIẾU TỰ TIN?"
        prob_text = f"Mỗi lần ra ngoài hay trang điểm, làn da kém tươi tắn làm bạn thiếu tự tin? Đừng lo lắng nữa!"
        sol_text = f"Sản phẩm {clean_title} này chính là bí quyết cứu cánh, giúp nuôi dưỡng làn da căng tràn sức sống."
        satisfaction_text = "Tự tin rạng rỡ suốt cả ngày, không còn nỗi lo da xuống tông hay khô ráp!"
    elif category == "TECH_GADGETS":
        prob_title = "GÓC SETUP BẤT TIỆN?"
        prob_text = f"Bàn làm việc bừa bộn hay thao tác gián đoạn làm giảm hiệu suất công việc? Đã đến lúc nâng cấp rồi!"
        sol_text = f"Chiếc {clean_title} này chính là giải pháp cứu cánh, sắp xếp tối ưu và nâng tầm góc làm việc."
        satisfaction_text = "Thao tác mượt mà chuẩn công nghệ, cảm hứng sáng tạo tăng vọt mỗi ngày!"
    elif category == "KITCHEN_HOME":
        prob_title = "VIỆC BẾP QUÁ MỆT MỎI?"
        prob_text = f"Nấu nướng hay dọn dẹp mất cả tiếng đồng hồ mệt nhoài mỗi tối? Đừng để việc nhà làm bạn kiệt sức!"
        sol_text = f"Món đồ {clean_title} này chính là vị cứu tinh, giúp mọi công việc nội trợ trở nên nhàn tênh."
        satisfaction_text = "Gian bếp gọn gàng tinh tươm, tận hưởng trọn vẹn những bữa cơm gia đình đầm ấm!"
    elif category == "FASHION_APPAREL":
        prob_title = "LOAY HOAY CHỌN ĐỒ?"
        prob_text = f"Mỗi sáng đứng trước tủ đồ không biết mặc gì vừa vặn, chỉn chu? Đừng tốn thời gian loay hoay nữa!"
        sol_text = f"Chiếc {clean_title} này chính là cứu tinh, form chuẩn tôn dáng, phối đồ nào cũng hợp."
        satisfaction_text = "Ra đường tự tin chỉn chu, đi làm hay đi chơi đều gọn gàng thời thượng!"
    else:
        prob_title = "BẤT TIỆN HÀNG NGÀY?"
        prob_text = f"Những phiền toái nhỏ trong cuộc sống làm bạn mất thời gian và khó chịu? Đừng để kéo dài nữa!"
        sol_text = f"Chiếc {clean_title} này chính là giải pháp cứu cánh, giải quyết triệt để và mang lại tiện ích tối đa."
        satisfaction_text = "Nâng cấp chất lượng cuộc sống mỗi ngày, thảnh thơi và an tâm tuyệt đối!"

    return [
        SceneDefinition(
            id=1,
            name="Vấn đề - Nỗi đau thực tế",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=prob_text,
            overlay_title=prob_title,
            overlay_subtitle="Đừng Chủ Quan",
            real_start_sec=0.0,
            image_index=0,
        ),
        SceneDefinition(
            id=2,
            name="Giải pháp - Vị cứu tinh xuất hiện",
            kind="REAL_FOOTAGE" if has_video else "IMAGE_SLIDE",
            narrator_text=sol_text,
            overlay_title="GIẢI PHÁP CỨU CÁNH",
            overlay_subtitle=clean_title[:28],
            real_start_sec=4.0 if has_video else 0.0,
            image_index=min(1, num_images - 1),
        ),
        SceneDefinition(
            id=3,
            name="Hiệu năng - Trải nghiệm vượt trội",
            kind="PRODUCT_PHOTO",
            narrator_text=f"{feat1_desc}. {feat2_desc}.",
            overlay_title=feat1_title[:24].upper(),
            overlay_subtitle=feat2_title[:24],
            real_start_sec=8.0 if has_video else 0.0,
            image_index=min(2, num_images - 1),
        ),
        SceneDefinition(
            id=4,
            name="Thỏa mãn - Kết quả tuyệt vời",
            kind="REAL_FOOTAGE" if has_video else "PRODUCT_PHOTO",
            narrator_text=satisfaction_text,
            overlay_title="TRẢI NGHIỆM TUYỆT VỜI",
            overlay_subtitle="Tạm Biệt Mệt Mỏi",
            real_start_sec=10.0 if has_video else 0.0,
            image_index=min(3, num_images - 1),
        ),
    ]


def build_flow_cinematic_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    social_proof_title: str,
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """Generate 4 cinematic AI scenes tailored to category with character consistency."""
    return _build_flow_cinematic_scenes(
        category=category,
        clean_title=clean_title,
        feat1_title=feat1_title,
        feat1_desc=feat1_desc,
        feat2_title=feat2_title,
        feat2_desc=feat2_desc,
        social_proof_title=social_proof_title,
        custom_idea=custom_idea,
    )


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

