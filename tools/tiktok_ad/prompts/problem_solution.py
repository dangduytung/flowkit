"""TikTok ``problem_solution`` / ``drama`` scenes.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, spoken_name
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
    short_name = spoken_name(clean_title)

    # Archetype-specific copy takes precedence over the broader category copy.
    if archetype == ProductArchetype.COMPRESSION_STORAGE:
        prob_title = "ĐỒ CỒNG KỀNH CHẬT CHỖ?"
        prob_text = "Chuyển mùa hay soạn đồ đi xa, nhìn đống chăn mền, áo phao chất đống mà ngợp luôn. Coi cái này nè."
        sol_text = f"Xài {short_name} này thử coi. Kéo khóa zip, hút hơi qua van, túi xẹp xuống còn có chút xíu."
        satisfaction_text = "Túi dày, dẻo, dọn tủ hay xếp vali đều gọn, đi chơi thảnh thơi."
    elif archetype == ProductArchetype.VACUUM_CLEANER:
        prob_title = "BỤI BẨN KẼ HẸP KHÓ LAU?"
        prob_text = "Vụn bánh trên sofa, bụi trong kẽ bàn phím, góc xe hơi lau hoài không sạch. Coi cái này nè."
        sol_text = f"Có {short_name} này là xử lý gọn lẹ, đầu hút luồn vô được mấy góc hẹp luôn."
        satisfaction_text = "Bàn làm việc, sofa hay xe hơi lúc nào cũng sạch, nhẹ nhàng hẳn."
    elif category == "HEALTH_FITNESS":
        prob_title = "ĐAU MỎI CƠ THỂ?"
        prob_text = "Làm cả ngày mỏi nhừ, ngồi hoài không tập trung nổi. Đừng ráng chịu nữa, coi cái này nè."
        sol_text = f"Xài thử {short_name} này coi, vài phút là người nhẹ nhõm hẳn."
        satisfaction_text = "Làm việc hăng hơn hẳn, tan ca cũng không còn mỏi như trước."
    elif category == "BEAUTY_SKINCARE":
        prob_title = "LÀN DA THIẾU TỰ TIN?"
        prob_text = "Ra đường hay trang điểm mà da xỉn, không tươi, thấy thiếu tự tin ghê. Coi cái này nè."
        sol_text = f"Xài thử {short_name} này coi, da ẩm mượt, tươi tắn hơn hẳn."
        satisfaction_text = "Cả ngày tự tin, không lo da xuống tông hay khô ráp."
    elif category == "TECH_GADGETS":
        prob_title = "GÓC SETUP BẤT TIỆN?"
        prob_text = "Bàn làm việc bừa bộn, làm cái gì cũng vướng. Tới lúc dọn lại rồi, coi cái này nè."
        sol_text = f"Có {short_name} này là bàn làm việc gọn hẳn, đồ nào chỗ nấy."
        satisfaction_text = "Thao tác trơn tru, ngồi vô là muốn làm liền."
    elif category == "KITCHEN_HOME":
        prob_title = "VIỆC BẾP QUÁ MỆT MỎI?"
        prob_text = "Nấu nướng dọn dẹp mỗi tối mất cả tiếng, mệt muốn xỉu. Coi cái này nè."
        sol_text = f"Có {short_name} này là việc bếp núc nhàn hẳn ra."
        satisfaction_text = "Bếp gọn gàng, ăn bữa cơm cũng thấy thảnh thơi hơn."
    elif category == "FASHION_APPAREL":
        prob_title = "LOAY HOAY CHỌN ĐỒ?"
        prob_text = "Sáng nào cũng loay hoay không biết mặc gì cho gọn, cho vừa. Coi cái này nè."
        sol_text = f"Thử {short_name} này coi, lên form gọn, phối gì cũng hợp."
        satisfaction_text = "Ra đường gọn gàng, đi làm đi chơi đều tự tin."
    else:
        prob_title = "BẤT TIỆN HÀNG NGÀY?"
        prob_text = "Mấy cái phiền phức nhỏ mỗi ngày mà để hoài thì mệt lắm. Coi cái này nè."
        sol_text = f"Xài thử {short_name} này coi, xử lý gọn lẹ, tiện ghê."
        satisfaction_text = "Mỗi ngày nhẹ nhàng, thảnh thơi hơn hẳn."

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
            narrator_text=feature_line(feat1_title, feat1_desc, feature_line(feat2_title, feat2_desc)),
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
