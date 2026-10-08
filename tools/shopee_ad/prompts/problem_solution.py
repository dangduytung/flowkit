"""Shopee ``problem_solution`` / ``drama`` scenes: a relatable problem, then the product as the fix.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, title_matches
from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, product_noun, spoken_name
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
    noun = product_noun(category, clean_title)
    short_name = spoken_name(clean_title)

    if category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi lo da khô mốc trước buổi hẹn",
                kind="FLOW_AI",
                narrator_text="Sắp đi gặp khách mà da khô sần, đánh nền lên mốc hết trơn, nhìn chán ghê. Ai bị vậy thì coi cái này nè.",
                overlay_title="NỀN MỐC DA KHÔ SẦN?",
                overlay_subtitle="Mất tự tin trước sự kiện?",
                image_index=0,
                prompt=(
                    f"{persona['intro']} leans toward the bathroom mirror and touches a dry, flaky patch on her cheek, frowning slightly{idea_ctx}. "
                    f"Real bathroom with a towel on the rail, flat ceiling light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Cấp ẩm phục hồi tức thì",
                kind="FLOW_AI",
                narrator_text=f"Chấm vài giọt {short_name} này lên thử coi. Thấm nhanh lắm, da ẩm lên thấy rõ.",
                overlay_title="CẤP ẨM TỨC THÌ",
                overlay_subtitle="Thấm sâu - Căng mọng da",
                image_index=0,
                prompt=(
                    "Close-up of a woman's fingertips, no face: she dabs a little cream onto her cheek and spreads it in small circles until it sinks in. "
                    "Real skin with pores and fine lines, window light. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Da căng bóng mịn màng thở phào",
                kind="FLOW_AI",
                narrator_text="Lớp nền ăn vô da, không bết, không đổ dầu, nhìn tươi tắn tự nhiên cả ngày.",
                overlay_title="CĂNG BÓNG MỊN MÀNG",
                overlay_subtitle="Tươi tắn rạng rỡ",
                image_index=0,
                prompt=(
                    f"{persona['cont']} looks at her skin in the mirror, turns her cheek toward the window light, then gives a small relaxed smile and looks away. "
                    f"Ordinary bedroom, morning daylight, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin tỏa sáng mọi nơi",
                kind="FLOW_AI",
                narrator_text="Da ổn rồi thì ra đường tự tin hẳn, chụp hình gần cũng không ngại.",
                overlay_title="TỰ TIN TỎA SÁNG",
                overlay_subtitle="Tự tin - Rạng ngời",
                image_index=0,
                prompt=(
                    f"{persona['cont']} picks up her bag and keys from a shelf by the apartment door and steps out. Daylight from the hallway, not talking."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nấu nướng dính khét ám ảnh",
                kind="FLOW_AI",
                narrator_text="Nấu xong mà đồ ăn dính đáy, cháy xém, rửa muốn toát mồ hôi luôn á. Ai bị vậy thì coi cái này nè.",
                overlay_title="ÁM ẢNH BẾP NÚC?",
                overlay_subtitle="Dính khét - Toát mồ hôi?",
                image_index=0,
                prompt=(
                    f"{persona['intro']} stands at a home stove scraping at burnt egg stuck to an old scratched pan with a spatula, sighing{idea_ctx}. "
                    f"Ordinary kitchen, ceiling light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Đổi sang chảo chống dính siêu mượt",
                kind="FLOW_AI",
                narrator_text=f"Đổi qua {short_name} này thử coi. Đồ ăn không dính chút nào, đảo một cái là lên.",
                overlay_title="CHỐNG DÍNH SIÊU MƯỢT",
                overlay_subtitle="Lướt êm ru - Không dính",
                image_index=0,
                prompt=(
                    f"Close-up of hands cooking with the {noun} at a home gas stove, no face: a wooden spatula stirs sliced pork and vegetables and nothing sticks to the bottom. "
                    f"Light steam rises, a few drops of oil on the stovetop. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Bữa ăn ngon nóng hổi vàng giòn",
                kind="FLOW_AI",
                narrator_text="Nóng đều, nhanh, món chín ngon mà đỡ tốn dầu, đỡ tốn thời gian.",
                overlay_title="CHÍN ĐỀU THƠM NGON",
                overlay_subtitle="Nấu nhanh trong vài phút",
                image_index=0,
                prompt=(
                    f"{persona['cont']} sets a plate of stir-fried pork and vegetables next to a bowl of rice on a small kitchen table and sits down to eat. Chopsticks and a glass of water on the table, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Lau nhẹ là sạch bong thảnh thơi",
                kind="FLOW_AI",
                narrator_text="Nấu xong rửa nhẹ cái là sạch, khỏi chà khỏi cọ. Nhàn ghê luôn!",
                overlay_title="LAU NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Thảnh thơi yêu việc bếp",
                image_index=0,
                prompt=(
                    f"Close-up at the kitchen sink, no face: a hand wipes the {noun} once with a damp yellow sponge and a film of oil comes off under running water. "
                    f"A few dishes in the rack. Hands only."
                ),
            ),
        ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Áo quần luộm thuộm khó phối",
                kind="FLOW_AI",
                narrator_text=f"Sáng nào cũng đứng lựa đồ hoài mà mặc vô vẫn chưa ưng. Coi thử {short_name} này nè.",
                overlay_title="LUỘM THUỘM THIẾU TỰ TIN?",
                overlay_subtitle="Khó phối đồ mỗi sáng?",
                image_index=0,
                prompt=(
                    f"{persona['intro']} stands in front of an open wardrobe holding up a wrinkled shirt, looks at it and tosses it onto the bed{idea_ctx}. "
                    f"Clothes piled on a chair, daylight from the window, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lên form tôn dáng chuẩn đẹp",
                kind="FLOW_AI",
                narrator_text=f"Mặc {short_name} này lên thử coi. Lên form gọn, vải mềm mát, mặc cả ngày vẫn thoải mái.",
                overlay_title="LÊN FORM TÔN DÁNG",
                overlay_subtitle="Mềm mát - Thoáng khí",
                image_index=0,
                prompt=(
                    f"Close-up of hands, no face: hands do up the button of the {noun} and smooth the fabric flat. Visible stitching and weave, daylight. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Vận động thoải mái không nhăn nhúm",
                kind="FLOW_AI",
                narrator_text="Đứng lên ngồi xuống thoải mái, vải không nhăn, không xù, nhìn gọn gàng hẳn.",
                overlay_title="CHỈN CHU THON GỌN",
                overlay_subtitle="Tự tin tràn đầy năng lượng",
                image_index=0,
                prompt=(
                    f"{persona['cont']}, now wearing the {noun}, turns slightly in front of a full-length mirror in a small bedroom and smooths the fabric. Filmed from beside the mirror, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin sải bước mọi nơi",
                kind="FLOW_AI",
                narrator_text="Phối với áo thun hay sơ mi gì cũng hợp, đi làm đi cà phê đều đẹp.",
                overlay_title="TỰ TIN SẢI BƯỚC",
                overlay_subtitle="Đi làm, dạo phố cực xinh",
                image_index=0,
                prompt=(
                    f"{persona['cont']}, wearing the {noun}, walks along a Vietnamese street past parked motorbikes, filmed by a friend walking a few steps ahead. Overcast daylight, not talking."
                ),
            ),
        ]

    elif category == "HEALTH_FITNESS":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Đau mỏi ê ẩm cổ vai gáy",
                kind="FLOW_AI",
                narrator_text="Ngồi làm cả ngày, cổ vai gáy cứng đơ, mỏi muốn rã ra luôn. Đừng ráng chịu nữa, coi cái này nè.",
                overlay_title="CỔ VAI GÁY CỨNG ĐỜ?",
                overlay_subtitle="Mệt mỏi - Đau nhức ê ẩm?",
                image_index=0,
                prompt=(
                    f"{persona['intro']} sits at a desk rubbing his stiff neck and rolling one shoulder, wincing slightly{idea_ctx}. Laptop and papers on the desk, office ceiling light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lực rung đầm êm giải tỏa tức thì",
                kind="FLOW_AI",
                narrator_text=f"Xài thử {short_name} này coi. Rung đầm mà êm, đè vô chỗ mỏi vài phút là đỡ liền.",
                overlay_title="GIẢM ĐAU MỎI SÂU",
                overlay_subtitle="Tác động sâu - Êm ái",
                image_index=0,
                prompt=(
                    f"Close-up, no face: a hand holds the {noun} against the top of the shoulder, and the shirt fabric and muscle shift slightly with each pulse. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Người nhẹ bẫng tràn năng lượng",
                kind="FLOW_AI",
                narrator_text="Người nhẹ nhõm hẳn ra, ngồi làm tiếp cũng tập trung hơn.",
                overlay_title="SẢNG KHOÁI PHẤN CHẤN",
                overlay_subtitle="Lấy lại 100% năng lượng",
                image_index=0,
                prompt=(
                    f"{persona['cont']} rolls his shoulders back slowly and stretches both arms up, then lets out a breath. Living room, daylight, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tiện mang theo văn phòng",
                kind="FLOW_AI",
                narrator_text="Nhỏ gọn, bỏ túi mang lên công ty hay đi chơi, mỏi lúc nào xài lúc đó.",
                overlay_title="TIỆN LỢI MỌI NƠI",
                overlay_subtitle="Chăm sóc cơ thể mỗi ngày",
                image_index=0,
                prompt=(
                    f"{persona['cont']} puts the {noun} into a backpack on a chair and zips it closed. Small apartment, daylight, not talking."
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
                    narrator_text="Đang chạy deadline mà laptop báo đầy bộ nhớ, rối muốn xỉu. Bình tĩnh, coi cái này nè.",
                    overlay_title="BÁO ĐỘNG ĐẦY Ổ CỨNG?",
                    overlay_subtitle="Công việc bị gián đoạn?",
                    image_index=0,
                    prompt=(
                        f"{persona['intro']} sits at a desk frowning at his laptop, the screen turned away from the camera, and rubs his forehead{idea_ctx}. "
                        f"A mug and a few cables on the desk, evening lamp light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Cắm cứu nguy tức thì",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm {short_name} này vô coi. Nhỏ xíu như cái móc khóa, cắm vô là nhận liền.",
                    overlay_title="CẮM LÀ NHẬN NGAY",
                    overlay_subtitle="Giải phóng dung lượng khủng",
                    image_index=0,
                    prompt=(
                        f"Close-up of a hand plugging the {noun} into the side USB port of a laptop, no face; it takes a small push to seat it and a tiny LED on the drive starts blinking. "
                        f"Fingerprints on the laptop edge. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Sao chép siêu tốc & Nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text="Chép cả thư mục nặng mà nhanh lắm, laptop nhẹ hẳn.",
                    overlay_title="SAO CHÉP SIÊU TỐC",
                    overlay_subtitle="Lưu trữ an toàn tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} leans back in his chair, lets out a breath and takes a sip from a mug while the laptop screen stays turned away from the camera. Desk lamp light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Móc khóa cứu tinh đồng hành",
                    kind="FLOW_AI",
                    narrator_text="Móc chung với chùm chìa khóa, đi đâu cũng mang theo được, dữ liệu lúc nào cũng có sẵn.",
                    overlay_title="MÓC KHÓA TIỆN LỢI",
                    overlay_subtitle="Gọn nhẹ - Siêu bền bỉ",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: a hand clips the {noun} onto a key ring with a few house keys and drops them into a jacket pocket. Hands only."
                    ),
                ),
            ]
        elif is_desk_setup:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Dây điện bừa bộn dưới chân bàn",
                    kind="FLOW_AI",
                    narrator_text="Dây nguồn với ổ cắm lòng thòng dưới chân bàn, nhìn rối mắt mà bực mình ghê. Coi cái này nè.",
                    overlay_title="DÂY ĐIỆN BỪA BỘN?",
                    overlay_subtitle="Mất tập trung - Ngột ngạt?",
                    image_index=0,
                    prompt=(
                        f"{persona['intro']} sits at a desk and looks down at a tangle of black cables and power strips on the floor under it, shaking his head slightly{idea_ctx}. "
                        f"Ordinary room, lamp light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Lắp khay kẹp bàn giấu trọn dây",
                    kind="FLOW_AI",
                    narrator_text=f"Gắn {short_name} này lên thử coi. Vặn ốc mười giây là xong, khỏi khoan, ổ cắm củ sạc giấu hết xuống dưới.",
                    overlay_title="KẸP BÀN 10 GIÂY",
                    overlay_subtitle="Không khoan đục - Giấu trọn dây",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: hands clamp the {noun} onto the edge of a wooden desk and turn the knob until it holds firm. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Bàn làm việc thông thoáng nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Góc bàn thoáng hẳn, nhìn mà mê."),
                    overlay_title="MẶT BÀN SẠCH BONG",
                    overlay_subtitle="Góc làm việc thông thoáng",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} tucks the last cable into the tray under the desk edge, sits back in his chair and takes a sip of coffee. Daylight from the window, not talking."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Không gian làm việc tràn đầy cảm hứng",
                    kind="FLOW_AI",
                    narrator_text="Kim loại chắc nịch, để đồ nặng cũng không sao. Bàn gọn vậy ngồi cả ngày cũng không chán.",
                    overlay_title="GÓC SETUP MƠ ƯỚC",
                    overlay_subtitle="Thẩm mỹ - Hiện đại",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} types on the laptop at the desk, with no cables hanging over its edge. Plant and a notebook on the desk, daylight, not talking."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Gián đoạn kết nối & Pin yếu",
                    kind="FLOW_AI",
                    narrator_text="Đang làm mà thiết bị chập chờn, pin tụt vèo vèo, bực ghê chớ. Coi cái này nè.",
                    overlay_title="SỰ CỐ GIÁN ĐOẠN?",
                    overlay_subtitle="Pin yếu - Kết nối chập chờn?",
                    image_index=0,
                    prompt=(
                        f"{persona['intro']} sits at a desk untangling a knot of old cables with a frown{idea_ctx}. Laptop with the screen turned away from the camera, lamp light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Kết nối tức thì giải cứu tình thế",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm {short_name} này vô coi. Kết nối nhanh, ổn định, chạy lại bình thường liền.",
                    overlay_title="KẾT NỐI TỨC THÌ",
                    overlay_subtitle="Ổn định - Tốc độ cao",
                    image_index=0,
                    prompt=(
                        f"Close-up of a hand, no face: it plugs in the {noun} with a small push and a small indicator light turns on. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Năng suất mượt mà & Nụ cười nhẹ nhõm",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Làm deadline nhẹ nhàng hơn hẳn."),
                    overlay_title=feat1_title,
                    overlay_subtitle="Năng suất đỉnh cao",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} types on the laptop, then picks up a mug and takes a sip. Screen turned away from the camera, daylight, not talking."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Tự do làm việc mọi nơi",
                    kind="FLOW_AI",
                    narrator_text="Nhỏ gọn vừa lòng bàn tay, để trên bàn làm việc lúc nào cũng tiện.",
                    overlay_title="TỰ DO MỌI NƠI",
                    overlay_subtitle="Nhỏ gọn - An tâm tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Close-up, no face: a hand slips the {noun} into a jacket pocket. Hands only."
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
                narrator_text="Chuyển mùa hay soạn đồ đi xa, nhìn đống chăn mền, áo phao chất đống mà ngợp luôn. Coi cái này nè.",
                overlay_title="ĐỒ CỒNG KỀNH CHẬT CHỖ?",
                overlay_subtitle="Tủ quần áo quá tải?",
                image_index=0,
                prompt=(
                    f"{persona['intro']} sits on the edge of the bed next to a tall pile of puffer jackets and thick blankets, looks at it and lets out a tired sigh{idea_ctx}. "
                    f"Lived-in bedroom, morning daylight, normal speed, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Hút xẹp 80% diện tích",
                kind="FLOW_AI",
                narrator_text=f"Xài {short_name} này thử coi. Kéo khóa zip, hút hơi qua van, túi xẹp xuống còn có chút xíu.",
                overlay_title="HÚT XẸP 80% DIỆN TÍCH",
                overlay_subtitle="Van silicon 1 chiều - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    "Close-up of a clear vacuum storage bag on a wooden table, no hands in frame, no face: a small electric pump sits on its round valve and with a steady hum "
                    "the bag slowly shrinks and wrinkles tightly around the puffer jacket inside over a few seconds. Normal speed."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Gọn gàng tủ quần áo",
                kind="FLOW_AI",
                narrator_text="Túi dày, dẻo, xài lại được hoài. Chăn mền gom gọn một ngăn tủ, đỡ ẩm mốc mà đỡ chỗ.",
                overlay_title="GỌN GÀNG TỦ QUẦN ÁO",
                overlay_subtitle="Chống ẩm mốc suốt 6-8 tháng",
                image_index=0,
                prompt=(
                    f"{persona['cont']} slides a flattened, wrinkled vacuum bag of clothes onto a wardrobe shelf next to two others, then steps back. Room light, normal speed, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin lên đường",
                kind="FLOW_AI",
                narrator_text="Dọn tủ hay soạn vali đi chơi đều nhàn, hành lý gọn nhẹ hẳn.",
                overlay_title="TỰ TIN LÊN ĐƯỜNG",
                overlay_subtitle="Hành lý gọn gàng - Thảnh thơi du lịch",
                image_index=0,
                prompt=(
                    f"{persona['cont']} pulls the handle up on the closed suitcase by the bed and gives the top a light pat. Bedroom daylight, normal speed, not talking. "
                    f"NO thumbs-up, NO distorted fingers."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Rắc rối vụn vặt thường ngày",
            kind="FLOW_AI",
            narrator_text="Mấy việc vặt trong nhà làm hoài không xong, mất thời gian ghê. Coi cái này nè.",
            overlay_title="BẤT TIỆN HÀNG NGÀY?",
            overlay_subtitle="Tốn thời gian & Công sức?",
            image_index=0,
            prompt=(
                f"{persona['intro']} sits at a cluttered table at home, pushes a few things aside and sighs{idea_ctx}. Lived-in room, daylight, not talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Giải pháp thông minh giải quyết triệt để",
            kind="FLOW_AI",
            narrator_text=f"Xài thử {short_name} này coi. Vài giây là xong việc, tiện lắm.",
            overlay_title="GIẢI PHÁP THÔNG MINH",
            overlay_subtitle="Tiện lợi - Dễ sử dụng",
            image_index=0,
            prompt=(
                f"Close-up of hands at a home table, no face: hands use the {noun} once, slowly and simply, the way it is normally used. Real fingerprints and scratches on the table. Hands only."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Cuộc sống tiện nghi nhẹ nhàng",
            kind="FLOW_AI",
            narrator_text=feature_line(feat1_title, feat1_desc, "Nhà cửa gọn gàng, nhẹ nhàng hơn hẳn."),
            overlay_title=feat1_title,
            overlay_subtitle="Thảnh thơi tiện nghi",
            image_index=0,
            prompt=(
                f"{persona['cont']} sits back on the sofa and looks around the tidied room. Daylight, not talking."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Nâng tầm chất lượng sống",
            kind="FLOW_AI",
            narrator_text=feature_line(feat2_title, feat2_desc, "Món nhỏ thôi mà mỗi ngày tiện hơn nhiều."),
            overlay_title="NÂNG TẦM CUỘC SỐNG",
            overlay_subtitle="Hiện đại - Tiện ích",
            image_index=0,
            prompt=(
                f"{persona['cont']} sets the {noun} down in its usual place on a shelf and walks out of the room. Daylight, not talking."
            ),
        ),
    ]


__all__ = ["build_problem_solution_scenes"]
