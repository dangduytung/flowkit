"""TikTok ``problem_solution`` / ``drama`` scenes.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo


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
        prob_text = "Cả ngày làm việc căng thẳng, cơ thể đau mỏi uể oải không tập trung nổi? Đừng chủ quan nữa!"
        sol_text = f"Chiếc {clean_title} này chính là giải pháp cứu cánh. Trải nghiệm là cảm nhận ngay sự nhẹ nhõm và thư giãn."
        satisfaction_text = "Làm việc năng suất hơn hẳn, tạm biệt hoàn toàn cảm giác nhức mỏi mỗi khi tan ca!"
    elif category == "BEAUTY_SKINCARE":
        prob_title = "LÀN DA THIẾU TỰ TIN?"
        prob_text = "Mỗi lần ra ngoài hay trang điểm, làn da kém tươi tắn làm bạn thiếu tự tin? Đừng lo lắng nữa!"
        sol_text = f"Sản phẩm {clean_title} này chính là bí quyết cứu cánh, giúp nuôi dưỡng làn da căng tràn sức sống."
        satisfaction_text = "Tự tin rạng rỡ suốt cả ngày, không còn nỗi lo da xuống tông hay khô ráp!"
    elif category == "TECH_GADGETS":
        prob_title = "GÓC SETUP BẤT TIỆN?"
        prob_text = "Bàn làm việc bừa bộn hay thao tác gián đoạn làm giảm hiệu suất công việc? Đã đến lúc nâng cấp rồi!"
        sol_text = f"Chiếc {clean_title} này chính là giải pháp cứu cánh, sắp xếp tối ưu và nâng tầm góc làm việc."
        satisfaction_text = "Thao tác mượt mà chuẩn công nghệ, cảm hứng sáng tạo tăng vọt mỗi ngày!"
    elif category == "KITCHEN_HOME":
        prob_title = "VIỆC BẾP QUÁ MỆT MỎI?"
        prob_text = "Nấu nướng hay dọn dẹp mất cả tiếng đồng hồ mệt nhoài mỗi tối? Đừng để việc nhà làm bạn kiệt sức!"
        sol_text = f"Món đồ {clean_title} này chính là vị cứu tinh, giúp mọi công việc nội trợ trở nên nhàn tênh."
        satisfaction_text = "Gian bếp gọn gàng tinh tươm, tận hưởng trọn vẹn những bữa cơm gia đình đầm ấm!"
    elif category == "FASHION_APPAREL":
        prob_title = "LOAY HOAY CHỌN ĐỒ?"
        prob_text = "Mỗi sáng đứng trước tủ đồ không biết mặc gì vừa vặn, chỉn chu? Đừng tốn thời gian loay hoay nữa!"
        sol_text = f"Chiếc {clean_title} này chính là cứu tinh, form chuẩn tôn dáng, phối đồ nào cũng hợp."
        satisfaction_text = "Ra đường tự tin chỉn chu, đi làm hay đi chơi đều gọn gàng thời thượng!"
    else:
        prob_title = "BẤT TIỆN HÀNG NGÀY?"
        prob_text = "Những phiền toái nhỏ trong cuộc sống làm bạn mất thời gian và khó chịu? Đừng để kéo dài nữa!"
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


__all__ = ["build_problem_solution_scenes"]
