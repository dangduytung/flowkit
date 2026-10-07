"""Shopee ``problem_solution`` / ``drama`` scenes: a relatable problem, then the product as the fix.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, title_matches
from tools.common.models import SceneDefinition
from tools.common.prompts.personas import character_persona


def build_problem_solution_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """Generate 4 Problem-Solution / Drama AI scenes tailored to the product category."""
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    persona = character_persona(category)

    if category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi lo da khô mốc trước buổi hẹn",
                kind="FLOW_AI",
                narrator_text="Sắp đi tiệc hay gặp khách mà da khô sần, đánh nền bị mốc meo nhìn phát chán đúng không? Đừng lo, xem ngay giải pháp phục hồi da cực xịn này nhé!",
                overlay_title="NỀN MỐC DA KHÔ SẦN?",
                overlay_subtitle="Mất tự tin trước sự kiện?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young woman looking in vanity mirror with a concerned, slightly frustrated expression at her dry, dull facial skin. "
                    f"Mouth closed, no speaking, no dialogue{idea_ctx}. Cinematic moody lighting, shallow depth of field. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Cấp ẩm phục hồi tức thì",
                kind="FLOW_AI",
                narrator_text=f"Chấm thử vài giọt {clean_title} này lên xem. Tinh chất thấm sâu, cấp ẩm tức thì giúp làn da căng bóng mịn màng trông thấy rõ.",
                overlay_title="CẤP ẨM TỨC THÌ",
                overlay_subtitle="Thấm sâu - Căng mọng da",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of gentle hands applying the silky formula onto cheek and forehead, soothing absorbing motion. "
                    f"Luminous moisture reflection, glowing aesthetic commercial lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Da căng bóng mịn màng thở phào",
                kind="FLOW_AI",
                narrator_text="Lớp nền tệp mịn màng vào da, không hề bết rít hay đổ dầu, nhìn tươi tắn tự nhiên rạng rỡ suốt cả ngày dài.",
                overlay_title="CĂNG BÓNG MỊN MÀNG",
                overlay_subtitle="Tươi tắn rạng rỡ",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. The woman smiles radiant with sheer relief and joy, admiring her glowing dewy face in the sunlit mirror. "
                    f"Mouth closed, no speaking, warm golden lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin tỏa sáng mọi nơi",
                kind="FLOW_AI",
                narrator_text="Chăm da khỏe đẹp thế này thì tự tin bước ra ngoài tỏa sáng, chẳng ngại bất kỳ góc máy hay ống kính nào luôn!",
                overlay_title="TỰ TIN TỎA SÁNG",
                overlay_subtitle="Tự tin - Rạng ngời",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Confident woman stepping into an evening party or sunny street, glowing skin turning heads with natural elegance. "
                    f"Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nấu nướng dính khét ám ảnh",
                kind="FLOW_AI",
                narrator_text="Nấu nướng xong mà chảo dính chặt, thức ăn cháy xém chùi rửa toát mồ hôi? Xem ngay giải pháp nấu nướng tiện lợi giải phóng đôi tay này nhé!",
                overlay_title="ÁM ẢNH BẾP NÚC?",
                overlay_subtitle="Dính khét - Toát mồ hôi?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person standing by stove looking tired and frustrated at an old scratched sticky pan with burnt food. "
                    f"Mouth closed, no speaking, moody kitchen lighting{idea_ctx}. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Đổi sang chảo chống dính siêu mượt",
                kind="FLOW_AI",
                narrator_text=f"Đổi sang dùng {clean_title} này xem. Lớp chống dính siêu mượt, tráng trứng hay xào nấu lướt êm ru không dính một tí nào luôn.",
                overlay_title="CHỐNG DÍNH SIÊU MƯỢT",
                overlay_subtitle="Lướt êm ru - Không dính",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands cooking with {clean_title}, fresh egg and meat gliding effortlessly on surface without sticking. "
                    f"Crisp steam sizzle, bright appetizing commercial lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Bữa ăn ngon nóng hổi vàng giòn",
                kind="FLOW_AI",
                narrator_text="Nhiệt tỏa đều nhanh chóng, món ăn chín vàng giòn thơm nức mũi mà lại tiết kiệm dầu ăn và thời gian nấu nướng mỗi ngày.",
                overlay_title="CHÍN ĐỀU THƠM NGON",
                overlay_subtitle="Nấu nhanh trong vài phút",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person smiling warmly as they place a steaming appetizing meal on table, leaning back with immense satisfaction. "
                    f"Mouth closed, no speaking, warm cozy dining ambiance. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Lau nhẹ là sạch bong thảnh thơi",
                kind="FLOW_AI",
                narrator_text="Nấu xong chỉ cần lấy khăn giấy lau nhẹ qua là sạch bong. Bếp núc thảnh thơi, nấu nướng mỗi ngày tràn đầy niềm vui!",
                overlay_title="LAU NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Thảnh thơi yêu việc bếp",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Gentle wipe of soft sponge cleans the pan completely sparkling clean in one second. "
                    f"Bright aesthetic kitchen, calm peaceful vibe, mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Áo quần luộm thuộm khó phối",
                kind="FLOW_AI",
                narrator_text="Sáng nào cũng đắn đo chọn đồ mà vẫn chưa ưng ý? Cùng mình trải nghiệm chiếc quần kaki này nhé!",
                overlay_title="LUỘM THUỘM THIẾU TỰ TIN?",
                overlay_subtitle="Khó phối đồ mỗi sáng?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person standing before a wardrobe looking indecisive and frustrated, holding uncomfortable wrinkled clothes. "
                    f"Mouth closed, no speaking{idea_ctx}. Moody indoor lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lên form tôn dáng chuẩn đẹp",
                kind="FLOW_AI",
                narrator_text=f"Mặc thử chiếc {clean_title} này lên xem. Form đứng tôn dáng cực chuẩn, vải mềm mát co giãn nhẹ nhàng thoải mái cả ngày dài.",
                overlay_title="LÊN FORM TÔN DÁNG",
                overlay_subtitle="Mềm mát - Thoáng khí",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands buttoning or smoothing {clean_title}, showing clean seams and premium drape. "
                    f"Crisp fashion commercial lighting, dynamic angles. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Vận động thoải mái không nhăn nhúm",
                kind="FLOW_AI",
                narrator_text="Vận động đứng lên ngồi xuống thoải mái, vải không hề nhăn nhúm hay xù lông, nhìn tổng thể thon gọn và chỉn chu hơn hẳn.",
                overlay_title="CHỈN CHU THON GỌN",
                overlay_subtitle="Tự tin tràn đầy năng lượng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person smiling genuinely into a full-length mirror, turning with confidence and effortless style. "
                    f"Mouth closed, no speaking, chic interior light. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin sải bước mọi nơi",
                kind="FLOW_AI",
                narrator_text="Chiếc quần này phối cùng áo thun hay sơ mi đi làm, đi cà phê dạo phố đều cực kỳ bảnh bao, tự tin sải bước mọi nơi.",
                overlay_title="TỰ TIN SẢI BƯỚC",
                overlay_subtitle="Đi làm, dạo phố cực xinh",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person stepping confidently down a vibrant modern sunlit street with stylish energy. "
                    f"Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "HEALTH_FITNESS":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Đau mỏi ê ẩm cổ vai gáy",
                kind="FLOW_AI",
                narrator_text="Ngồi làm việc cả ngày, cổ vai gáy cứng đờ, đau nhức ê ẩm làm giảm năng suất? Đừng chịu đựng nữa, thử ngay mẹo thư giãn này nha!",
                overlay_title="CỔ VAI GÁY CỨNG ĐỜ?",
                overlay_subtitle="Mệt mỏi - Đau nhức ê ẩm?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Office worker rubbing their sore neck and shoulders with a wincing pained expression at desk. "
                    f"Mouth closed, no speaking{idea_ctx}. Moody office lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lực rung đầm êm giải tỏa tức thì",
                kind="FLOW_AI",
                narrator_text=f"Dùng thử chiếc {clean_title} này xem. Lực rung đầm êm tác động sâu vào từng bó cơ căng cứng, giải tỏa nhức mỏi chỉ sau vài phút.",
                overlay_title="GIẢM ĐAU MỎI SÂU",
                overlay_subtitle="Tác động sâu - Êm ái",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of {clean_title} smoothly massaging shoulder/back, rhythmic soothing pulses. "
                    f"Crisp commercial lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Người nhẹ bẫng tràn năng lượng",
                kind="FLOW_AI",
                narrator_text="Cơn nhức mỏi tan biến ngay lập tức, người nhẹ bẫng sảng khoái và tràn đầy năng lượng để tập trung xử lý công việc hiệu quả.",
                overlay_title="SẢNG KHOÁI PHẤN CHẤN",
                overlay_subtitle="Lấy lại 100% năng lượng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person rolling shoulders back with a huge smile of relief, stretching arms with renewed vitality. "
                    f"Mouth closed, no speaking, bright natural sunlight. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tiện mang theo văn phòng",
                kind="FLOW_AI",
                narrator_text="Thiết kế nhỏ gọn bỏ túi mang theo văn phòng hay đi du lịch, mỏi lúc nào dùng lúc đó, cực kỳ tiện lợi mỗi ngày!",
                overlay_title="TIỆN LỢI MỌI NƠI",
                overlay_subtitle="Chăm sóc cơ thể mỗi ngày",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person packing {clean_title} into sleek backpack, walking with upright energized posture. "
                    f"Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "TECH_GADGETS":
        is_storage = title_matches(clean_title, ProductArchetype.STORAGE_DEVICE)
        is_desk_setup = title_matches(clean_title, ProductArchetype.DESK_ORGANIZER)
        if is_storage:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Báo động đầy bộ nhớ giữa deadline",
                    kind="FLOW_AI",
                    narrator_text="Laptop liên tục báo đầy bộ nhớ giữa lúc deadline gấp gáp khiến bạn bối rối? Đừng hoảng, có cách cứu nguy cực nhanh và an toàn nhé!",
                    overlay_title="BÁO ĐỘNG ĐẦY Ổ CỨNG?",
                    overlay_subtitle="Công việc bị gián đoạn?",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Young Vietnamese professional sitting at an office desk looking concerned and stressed at their laptop screen. "
                        f"A red storage full alert is reflected on their glasses. Mouth closed, no speaking, serious anxious expression{idea_ctx}, looking for a quick solution. "
                        f"Cinematic moody lighting, shallow depth of field. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Cắm cứu nguy tức thì",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm ngay chiếc {clean_title} này vào. Nhỏ xíu như móc khóa, cắm là nhận ngay, giải phóng hàng trăm gigabyte dữ liệu quan trọng tức thì.",
                    overlay_title="CẮM LÀ NHẬN NGAY",
                    overlay_subtitle="Giải phóng dung lượng khủng",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Dramatic macro close-up shot of hands confidently plugging {clean_title} into the side USB port of the laptop. "
                        f"A vibrant blue LED light flashes to life, smooth heroic motion, crisp metallic finish, premium cinematic commercial lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Sao chép siêu tốc & Nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text="Tốc độ sao chép siêu nhanh, copy cả thư mục nặng chỉ trong vài giây chớp mắt, trút bỏ hoàn toàn gánh nặng lưu trữ.",
                    overlay_title="SAO CHÉP SIÊU TỐC",
                    overlay_subtitle="Lưu trữ an toàn tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. The young professional leans back in their chair with a huge smile of relief and satisfaction as file transfer finishes instantly. "
                        f"Taking a relaxed sip from their coffee cup, smooth productive vibe, mouth closed, no speaking, no dialogue. Warm bright ambient sunlight. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Móc khóa cứu tinh đồng hành",
                    kind="FLOW_AI",
                    narrator_text="Móc luôn cùng chùm chìa khóa mang theo bên mình mọi lúc mọi nơi, dữ liệu luôn sẵn sàng, an tâm tuyệt đối trên từng cây số!",
                    overlay_title="MÓC KHÓA TIỆN LỢI",
                    overlay_subtitle="Gọn nhẹ - Siêu bền bỉ",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Cinematic close-up of hands clipping {clean_title} onto car keys with a confident gesture, ready to head out for meetings. "
                        f"Modern dynamic professional lifestyle, warm natural lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
                    ),
                ),
            ]
        elif is_desk_setup:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Dây điện bừa bộn dưới chân bàn",
                    kind="FLOW_AI",
                    narrator_text="Dây nguồn, ổ cắm lòng thòng bừa bộn dưới chân bàn, nhìn vừa ngột ngạt vừa bực mình đúng không? Mình chỉ cho cách này!",
                    overlay_title="DÂY ĐIỆN BỪA BỘN?",
                    overlay_subtitle="Mất tập trung - Ngột ngạt?",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Featuring {persona['intro']}, sitting at an office desk looking annoyed and stressed at a tangle of messy black cables and power strips cluttering the floor under the desk. "
                        f"Mouth closed, no speaking, serious frustrated expression{idea_ctx}. Cinematic moody lighting, shallow depth of field. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Lắp khay kẹp bàn giấu trọn dây",
                    kind="FLOW_AI",
                    narrator_text=f"Gắn thử cái {clean_title} này lên xem. Chỉ mất mười giây vặn ốc, không cần khoan đục. Giấu trọn mọi ổ cắm củ sạc xuống dưới, sạch bong!",
                    overlay_title="KẸP BÀN 10 GIÂY",
                    overlay_subtitle="Không khoan đục - Giấu trọn dây",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Dramatic macro close-up shot of hands clamping the sleek minimalist metallic cable management tray securely onto the edge of a clean wooden desk, routing power cables neatly inside. "
                        f"Smooth confident action, commercial tech interior lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Bàn làm việc thông thoáng nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Toàn bộ góc bàn tự nhiên thông thoáng gọn gàng, nhìn ngắm mà mê luôn.",
                    overlay_title="MẶT BÀN SẠCH BONG",
                    overlay_subtitle="Góc làm việc thông thoáng",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Featuring {persona['cont']}, leaning back in their office chair with a huge smile of relief and satisfaction looking at their clean, aesthetic, cable-free modern desk setup. "
                        f"Taking a relaxed sip of coffee, mouth closed, no speaking, no dialogue. Warm morning sunlight. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Không gian làm việc tràn đầy cảm hứng",
                    kind="FLOW_AI",
                    narrator_text="Chất liệu kim loại chắc nịch, chịu tải ngon lành. Góc làm việc ngăn nắp thế này thì ngồi cả ngày không thấy chán!",
                    overlay_title="GÓC SETUP MƠ ƯỚC",
                    overlay_subtitle="Thẩm mỹ - Hiện đại",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Wide aesthetic hero pan of the stylish minimalist desk setup with modern laptop, plant, and spotless floor without a single dangling cable. "
                        f"Featuring {persona['cont']} working peacefully, mouth closed, no speaking. Warm natural lighting. NO text overlays."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Gián đoạn kết nối & Pin yếu",
                    kind="FLOW_AI",
                    narrator_text="Thiết bị chập chờn, pin tụt nhanh giữa lúc công việc cao điểm? Đừng để sự cố làm gián đoạn ngày làm việc của bạn nha!",
                    overlay_title="SỰ CỐ GIÁN ĐOẠN?",
                    overlay_subtitle="Pin yếu - Kết nối chập chờn?",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Tech professional looking annoyed at a dead battery icon or tangled broken cables on desk. "
                        f"Mouth closed, no speaking{idea_ctx}. Moody office lighting. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Kết nối tức thì giải cứu tình thế",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm ngay {clean_title} này vào! Kết nối siêu nhanh, đường truyền ổn định đưa thiết bị trở lại hoạt động một trăm phần trăm.",
                    overlay_title="KẾT NỐI TỨC THÌ",
                    overlay_subtitle="Ổn định - Tốc độ cao",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up of hands plugging in {clean_title}, satisfying click and vibrant LED power light turning on. "
                        f"Commercial high-tech lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Năng suất mượt mà & Nụ cười nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Hiệu suất mượt mà, giúp bạn hoàn thành deadline nhẹ nhàng không chút lo âu.",
                    overlay_title=feat1_title,
                    overlay_subtitle="Năng suất đỉnh cao",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Professional smiling with satisfaction, typing swiftly and sipping coffee peacefully. "
                        f"Mouth closed, no speaking, bright natural sunlight. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Tự do làm việc mọi nơi",
                    kind="FLOW_AI",
                    narrator_text="Nhỏ gọn trong lòng bàn tay, người bạn đồng hành tin cậy cho góc làm việc hiện đại!",
                    overlay_title="TỰ DO MỌI NƠI",
                    overlay_subtitle="Nhỏ gọn - An tâm tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Hands slipping {clean_title} into jacket pocket, walking confidently out of cafe into city. "
                        f"Mouth closed, no speaking. NO text overlays."
                    ),
                ),
            ]

    # Storage, Compression Bags, Travel Organization
    is_storage = any(
        k in clean_title.lower()
        for k in [
            "túi hút chân không",
            "túi nén",
            "hút chân không",
            "vali",
            "chăn màn",
            "tủ quần áo",
            "gấp gọn",
            "vali gia đình",
            "nén",
        ]
    )
    if is_storage:
        return [
            SceneDefinition(
                id=1,
                name="Hook - Đồ cồng kềnh chật chỗ",
                kind="FLOW_AI",
                narrator_text="Mỗi lần chuyển mùa hay chuẩn bị đi xa, nhìn đống chăn màn, áo phao cồng kềnh chất đống chiếm hết cả phòng mà phát ngợp đúng không? Thử ngay cách này nha!",
                overlay_title="ĐỒ CỒNG KỀNH CHẬT CHỖ?",
                overlay_subtitle="Tủ quần áo quá tải?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Medium shot, 35mm lens, 60fps real-time look, bright modern bedroom. "
                    f"Featuring {persona['intro']} sitting on the edge of the bed. In front of them, an enormous messy mountain of bulky winter puffer coats and thick folded blankets is piled high on the bed, overflowing everywhere. "
                    f"The actor looks overwhelmed at the massive pile, looks directly into the camera, and shakes their head with an exasperated funny reaction{idea_ctx}. "
                    f"Natural brisk human speed, crisp real-time movement, not slow motion, not floaty. Realistic morning natural lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Hút xẹp 80% diện tích",
                kind="FLOW_AI",
                narrator_text=f"Dùng {clean_title} này xem. Khóa zip đôi kín khít, van silicon một chiều hút sạch không khí, nén xẹp phẳng lì chỉ sau 10 giây, giảm ngay 80% diện tích!",
                overlay_title="HÚT XẸP 80% DIỆN TÍCH",
                overlay_subtitle="Van silicon 1 chiều - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up B-roll, 60fps crisp commercial studio lighting. "
                    f"A clear transparent vacuum compression bag rests flat on a modern wooden table, containing a thick puffy winter jacket. "
                    f"A mini electric suction pump is attached to the circular one-way silicon valve on the bag. In a fast satisfying time-lapse compression, the air is rapidly sucked out, "
                    f"and the puffy bag instantly deflates and flattens down into a rock-firm, paper-thin, rigid flat slab. "
                    f"Crisp texture, bright clean studio lighting, natural speed, not floaty. NO face, NO hands in frame. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Gọn gàng tủ quần áo",
                kind="FLOW_AI",
                narrator_text="Chất liệu PA PE dẻo dai dày dặn, tái sử dụng thoải mái. Đống chăn màn cồng kềnh giờ xếp gọn gàng trong ngăn tủ, vừa sạch sẽ chống ẩm mốc, vừa tiết kiệm không gian tối đa!",
                overlay_title="GỌN GÀNG TỦ QUẦN ÁO",
                overlay_subtitle="Chống ẩm mốc suốt 6-8 tháng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Eye-level medium shot, sharp 35mm lens, 60fps real-time commercial look. "
                    f"Featuring {persona['cont']} standing in front of a modern aesthetic wooden wardrobe closet. With a bright proud smile, "
                    f"they place a neat stack of 4 ultra-thin compressed flat vacuum bags like books onto a closet shelf, leaving 80 percent of the wardrobe shelf completely open, spacious, and spotless. "
                    f"Crisp confident movement, natural human speed, not slow motion, not floaty. Warm natural indoor daylight. Mouth closed, no dialogue. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin lên đường",
                kind="FLOW_AI",
                narrator_text="Dù dọn tủ gia đình hay chuẩn bị vali du lịch đều nhàn tênh. Hành lý gọn nhẹ, thảnh thơi lên đường tận hưởng chuyến đi thôi!",
                overlay_title="TỰ TIN LÊN ĐƯỜNG",
                overlay_subtitle="Hành lý gọn gàng - Thảnh thơi du lịch",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Medium hero shot, bright natural morning sunlight, 60fps real-time commercial look. "
                    f"Featuring {persona['cont']} standing proudly in a stylish travel outfit beside a sleek, closed suitcase sitting neatly on a luggage rack. "
                    f"They give the top of the suitcase a confident, satisfied double pat with their hand, look directly at the camera with a beaming warm smile, "
                    f"and look directly into camera with a beaming confident smile, feeling completely ready for vacation. Stable realistic physics, crisp human gestures, natural speed, not floaty. Mouth closed, no speaking. NO thumbs-up, NO distorted fingers. NO text overlays."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Rắc rối vụn vặt thường ngày",
            kind="FLOW_AI",
            narrator_text="Mấy việc vặt trong nhà làm bạn tốn thời gian và bực mình? Thử ngay cách này xem sao nha!",
            overlay_title="BẤT TIỆN HÀNG NGÀY?",
            overlay_subtitle="Tốn thời gian & Công sức?",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Person looking frustrated at a common daily annoyance or messy clutter on table. "
                f"Mouth closed, no speaking{idea_ctx}. Moody indoor light. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Giải pháp thông minh giải quyết triệt để",
            kind="FLOW_AI",
            narrator_text=f"Dùng thử {clean_title} này xem. Thiết kế thông minh xử lý gọn gàng chỉ trong vài giây, cực kỳ tiện lợi.",
            overlay_title="GIẢI PHÁP THÔNG MINH",
            overlay_subtitle="Tiện lợi - Dễ sử dụng",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using {clean_title} smoothly and effectively. "
                f"Flawless satisfying action, clean commercial B-roll lighting. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Cuộc sống tiện nghi nhẹ nhàng",
            kind="FLOW_AI",
            narrator_text=f"{feat1_desc}. Mọi thứ trở nên ngăn nắp nhẹ nhàng, thảnh thơi hơn rất nhiều.",
            overlay_title=feat1_title,
            overlay_subtitle="Thảnh thơi tiện nghi",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Person smiling with genuine relief, enjoying clean tidy comfortable space. "
                f"Mouth closed, no speaking, warm sunny ambiance. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Nâng tầm chất lượng sống",
            kind="FLOW_AI",
            narrator_text=f"{feat2_desc}. Một món đồ nhỏ nhưng giúp cuộc sống thoải mái và tiện nghi hơn mỗi ngày!",
            overlay_title="NÂNG TẦM CUỘC SỐNG",
            overlay_subtitle="Hiện đại - Tiện ích",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Neat aesthetic shot of {clean_title} placed elegantly in room, creator stepping out with a happy smile. "
                f"Mouth closed, no speaking. NO text overlays."
            ),
        ),
    ]


__all__ = ["build_problem_solution_scenes"]
