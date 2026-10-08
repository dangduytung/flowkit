"""Shopee ``faceless_pov`` scenes: hands-only first-person demos, no faces.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype, title_matches
from tools.common.models import SceneDefinition
from tools.common.prompts.realism import feature_line, product_noun, spoken_name


def build_vacuum_faceless_pov_scenes(
    clean_title: str,
    feat1_title: str = "",
    feat1_desc: str = "",
    feat2_title: str = "",
    feat2_desc: str = "",
    idea_ctx: str = "",
) -> List[SceneDefinition]:
    """Build 4 authentic faceless POV scenes for handheld/cordless vacuum cleaners dynamically."""
    short_name = spoken_name(clean_title)
    sc2_title = feat1_title if feat1_title else "LỰC HÚT MẠNH MẼ"
    sc2_sub = feat1_desc if feat1_desc else "Sạch bóng mọi khe kẹt"
    sc3_title = feat2_title if feat2_title else "ĐẦU HÚT ĐA NĂNG"
    sc3_sub = feat2_desc if feat2_desc else "Sofa - Bàn phím - Giường nệm"

    return [
        SceneDefinition(
            id=1,
            name="POV 1 - Mở hộp trên tay & Đầu hút đa năng",
            kind="FLOW_AI",
            narrator_text=f"Mở hộp {short_name} ra coi nè. Không dây, cầm nhẹ hều, kèm theo đủ bộ đầu hút luôn.",
            overlay_title="TRẢI NGHIỆM TRÊN TAY",
            overlay_subtitle="Không dây mini - Đa năng",
            image_index=0,
            prompt=(
                f"First-person view looking down at a wooden desk with a few cables and a mug. "
                f"Two hands hold the cordless handheld vacuum and turn it slowly to show its body and handle; a thumb presses the power button and a small LED lights up. "
                f"The spare nozzles lie loose on the desk beside it. Hands keep holding the vacuum body, NO attaching parts, NO plugging nozzles, NO assembly{idea_ctx}. "
                f"No face, hands only."
            ),
        ),
        SceneDefinition(
            id=2,
            name="POV 2 - Lực hút lốc xoáy khe ghế ô tô",
            kind="FLOW_AI",
            narrator_text="Gắn đầu hút dẹt vô, luồn xuống khe ghế xe với hộc để đồ, vụn bánh với cát hút sạch trơn.",
            overlay_title=sc2_title,
            overlay_subtitle=sc2_sub,
            image_index=0,
            prompt=(
                "First-person view inside an ordinary used car, no face: a hand pushes the cordless handheld vacuum, slim crevice nozzle already attached, along the gap between the seat and the center console. "
                "Crumbs and grains of sand get sucked into the nozzle where it passes. Worn seat fabric, daylight through the window, normal speed. Hands only."
            ),
        ),
        SceneDefinition(
            id=3,
            name="POV 3 - Đổi đầu chải hút sạch sofa & giường nệm",
            kind="FLOW_AI",
            narrator_text="Đổi qua đầu chổi là hút được bàn phím, ghế sofa, nệm, lông chó mèo cũng sạch luôn.",
            overlay_title=sc3_title,
            overlay_subtitle=sc3_sub,
            image_index=0,
            prompt=(
                "Close-up of a fabric sofa, no face: a hand moves the handheld vacuum with the brush nozzle already securely attached in short back-and-forth strokes across the textured couch cushion. "
                "Pet hair and crumbs lift off only where the brush touches. Real lint and wrinkles in the fabric, normal speed. Hands only."
            ),
        ),
        SceneDefinition(
            id=4,
            name="POV 4 - Đổ rác 1 chạm & Màng lọc xả nước",
            kind="FLOW_AI",
            narrator_text="Cốc bụi tháo ra đổ cái là xong. Màng lọc thì xả dưới vòi nước, phơi khô là xài lại được.",
            overlay_title="MÀNG LỌC RỬA NƯỚC",
            overlay_subtitle="Vệ sinh nhanh gọn",
            image_index=0,
            prompt=(
                "Close-up at a home kitchen sink, no face: hands hold the small round white filter under a gentle stream of fresh tap water, rinsing grey dust out of its pleats while dirty water drips off. "
                "NO twisting, NO disassembly, NO pulling parts apart. Steel sink with a few water spots. Hands only."
            ),
        ),
    ]


def build_faceless_pov_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    social_proof_title: str = "TIỆN ÍCH THỰC TẾ",
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """
    Generate 4 Faceless First-Person POV (Hands-on / ASMR / Tutorial) scenes.
    Crucial rules:
    - 100% Faceless: absolutely NO human face or head visible in any scene.
    - Camera angle: First-person POV, macro close-up of hands, top-down desk view, or neck-down angle.
    - Demonstrations: hands-on unboxing, assembling, adjusting, practical stress test, satisfying clean finish.
    - Designed specifically for silent TikTok/Reels upload (user adds trending BGM & native TikTok text in post).
    """
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    noun = product_noun(category, clean_title)
    short_name = spoken_name(clean_title)

    archetype = resolve_product_archetype(clean_title)
    if archetype == ProductArchetype.VACUUM_CLEANER:
        return build_vacuum_faceless_pov_scenes(
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            idea_ctx=idea_ctx,
        )

    if category == "TECH_GADGETS":
        is_footrest = title_matches(clean_title, ProductArchetype.FOOTREST)
        is_desk_setup = title_matches(clean_title, ProductArchetype.DESK_ORGANIZER)

        if is_footrest:
            return [
                SceneDefinition(
                    id=1,
                    name="POV 1 - Mở hộp & Cận cảnh con lăn",
                    kind="FLOW_AI",
                    narrator_text=f"Mở hộp {short_name} ra coi nè. Làm cứng cáp, mấy con lăn massage lăn đã chân lắm.",
                    overlay_title="GHẾ KÊ CHÂN DƯỚI 100K",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"First-person view looking down at a rug beside a desk, no face: hands lift the {noun} out of its plain cardboard box, showing the massage rollers on top{idea_ctx}. "
                        f"Torn tape and packing paper on the floor. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Chỉnh nấc & Xoay con lăn massage",
                    kind="FLOW_AI",
                    narrator_text="Chỉnh độ nghiêng được mấy nấc, con lăn xoay êm ru, thư giãn ghê.",
                    overlay_title="CON LĂN MASSAGE ĐIỀU CHỈNH",
                    overlay_subtitle="Nhiều nấc độ nghiêng",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: fingertips spin the textured massage rollers of the {noun} and they turn with a soft rattle. "
                        f"Floor under a desk, daylight. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Trải nghiệm thực tế dưới gầm bàn",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Ngồi làm lâu mà lưng với đùi đỡ mỏi hẳn."),
                    overlay_title="ĐỠ MỎI CHÂN HẲN",
                    overlay_subtitle="Ngồi làm việc cả ngày êm ái",
                    image_index=0,
                    prompt=(
                        f"View down from a desk chair, no face: feet in socks rest on the {noun} under the desk and slowly roll the massage rollers back and forth. "
                        f"Desk legs, a power strip and a bag on the floor nearby, daylight. Feet and lower legs only."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Góc làm việc thư thái gọn gàng",
                    kind="FLOW_AI",
                    narrator_text="Góc làm việc gọn hơn, ngồi cả ngày cũng thấy dễ chịu.",
                    overlay_title="SETUP GỌN GÀNG THƯ THÁI",
                    overlay_subtitle="Món đồ văn phòng 10 điểm",
                    image_index=0,
                    prompt=(
                        f"Low view under a home desk, no face: the {noun} sits on the floor between the desk legs as a pair of feet in socks settle onto it. "
                        f"Some cables and a backpack nearby, warm lamp light. Feet and lower legs only."
                    ),
                ),
            ]
        elif is_desk_setup:
            return [
                SceneDefinition(
                    id=1,
                    name="POV 1 - Mở hộp khay kẹp bàn",
                    kind="FLOW_AI",
                    narrator_text=f"Mở hộp {short_name} ra coi nè. Kim loại sơn tĩnh điện, cầm đầm tay lắm.",
                    overlay_title="KẸP BÀN GIẤU DÂY",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"First-person view looking down at a wooden desk, no face: hands lift the {noun} out of its plain box and turn it over once{idea_ctx}. "
                        f"Packaging scraps on the desk. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Vặn ốc kẹp bàn không khoan đục",
                    kind="FLOW_AI",
                    narrator_text="Vặn ốc kẹp vô mép bàn là xong, chắc nịch, khỏi khoan khỏi đục.",
                    overlay_title="KẸP BÀN TRONG 10 GIÂY",
                    overlay_subtitle="Không khoan đục - Siêu chắc",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: hands clamp the {noun} onto the edge of a wooden desk and turn the tightening knob a few times until it holds firm. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Giấu trọn ổ cắm dây điện",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Ổ cắm, củ sạc gom hết vô khay, dưới sàn hết dây nhợ."),
                    overlay_title="GIẤU TRỌN MỌI DÂY CÁP",
                    overlay_subtitle="Dưới sàn sạch bong",
                    image_index=0,
                    prompt=(
                        f"Close-up under a desk edge, no face: hands tuck a power strip and a bundle of cables into the {noun} one by one, so the cables stop hanging toward the floor. "
                        f"A few dust bunnies on the floor. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Mặt bàn thông thoáng sạch sẽ",
                    kind="FLOW_AI",
                    narrator_text="Mặt bàn với gầm bàn gọn hẳn, nhìn góc setup mà mê.",
                    overlay_title="GÓC SETUP MƠ ƯỚC",
                    overlay_subtitle="Gọn gàng - Tinh tế",
                    image_index=0,
                    prompt=(
                        "Neck-down view at a desk, no face: a hand sets a glass of iced coffee down on the wooden desk, which now has no cables hanging over its edge. "
                        "A laptop and a notebook on the desk, morning window light. Hands only."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="POV 1 - Mở hộp thiết bị trên tay",
                    kind="FLOW_AI",
                    narrator_text=f"Mở hộp {short_name} ra coi nè. Nhỏ gọn, làm kỹ lắm.",
                    overlay_title=clean_title[:28].upper(),
                    overlay_subtitle="Mở hộp trên tay",
                    image_index=0,
                    prompt=(
                        f"First-person view looking down at a desk, no face: hands open a plain box and lift the {noun} out{idea_ctx}. Fingerprints and dust on the desk. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Thao tác kết nối & Tính năng",
                    kind="FLOW_AI",
                    narrator_text="Cắm vô là nhận, nút bấm với cổng kết nối ăn khớp, nhạy.",
                    overlay_title="KẾT NỐI NHANH NHẠY",
                    overlay_subtitle="Cắm là nhận ngay",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: a hand plugs in the {noun} and switches it on with a single press, and a small indicator light turns on. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Trải nghiệm thực tế mượt mà",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Làm việc hay giải trí gì cũng trơn tru."),
                    overlay_title="HIỆU NĂNG MƯỢT MÀ",
                    overlay_subtitle="Xử lý nhanh chóng",
                    image_index=0,
                    prompt=(
                        f"First-person view at a desk, no face: hands type on a laptop keyboard while the {noun} sits working next to it. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Gọn nhẹ bỏ túi đồng hành",
                    kind="FLOW_AI",
                    narrator_text="Nhỏ gọn, bỏ túi mang đi làm đi cà phê đều tiện.",
                    overlay_title="GỌN NHẸ TIỆN LỢI",
                    overlay_subtitle="Đồng hành mỗi ngày",
                    image_index=0,
                    prompt=(
                        f"Close-up, no face: a hand slides the {noun} into the front pocket of a sling bag and zips it closed. Hands only."
                    ),
                ),
            ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở gói & Trải phẳng chất vải",
                kind="FLOW_AI",
                narrator_text=f"Mở gói {short_name} ra coi nè. Vải mềm, sờ mát tay, đường may đều lắm.",
                overlay_title="MỞ GÓI TRẢI NGHIỆM THẬT",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"First-person view looking down at a bed, no face: hands unfold the {noun} and smooth the fabric flat with both palms, showing the weave and a few soft creases{idea_ctx}. "
                    f"Daylight from the window. Hands only."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Cận cảnh cạp chun & Túi lé tiện lợi",
                kind="FLOW_AI",
                narrator_text="Lưng thun co giãn dễ chịu, túi sâu, bỏ điện thoại với ví vô thoải mái.",
                overlay_title="CẠP CHUN & TÚI LÉ SÂU",
                overlay_subtitle="Co giãn êm ái - Tiện dụng",
                image_index=0,
                prompt=(
                    f"Close-up of hands, no face: hands stretch the elastic waistband of the {noun} outwards and let it spring back. Bed sheet in the background, daylight. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Test co giãn & Đàn hồi vải",
                kind="FLOW_AI",
                narrator_text="Kéo căng ra thả là về form liền, giặt máy cũng không nhão.",
                overlay_title="CO GIÃN ĐÀN HỒI CỰC TỐT",
                overlay_subtitle="Không nhăn xù - Thoáng mát",
                image_index=0,
                prompt=(
                    f"Close-up of hands, no face: hands pull the fabric of the {noun} diagonally and release it, and the cloth settles back with only small creases. Hands only."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Thao tác đút tay túi quần lấy điện thoại",
                kind="FLOW_AI",
                narrator_text="Bỏ điện thoại vô túi mà quần vẫn phẳng, không bị cộm.",
                overlay_title="TÚI SÂU TIỆN LỢI",
                overlay_subtitle="Không lo cộm - Đứng form",
                image_index=0,
                prompt=(
                    f"Waist-to-thigh close-up of a person wearing the {noun}, no face: a hand slides a smartphone into the front pocket and pulls it back out. "
                    f"Ordinary bedroom, daylight. Neck-down only."
                ),
            ),
            SceneDefinition(
                id=5,
                name="POV 5 - Lên form thực tế & Vận động thoải mái",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Đứng lên ngồi xuống cả ngày vẫn thoải mái."),
                overlay_title="LÊN FORM TÔN DÁNG VỪA VẶN",
                overlay_subtitle="Đứng lên ngồi xuống thoải mái",
                image_index=0,
                prompt=(
                    f"Lower-body view of a person wearing the {noun}, no face: they bend their knees into a slow comfortable squat and stand back up. Tiled floor, daylight. Neck-down only."
                ),
            ),
            SceneDefinition(
                id=6,
                name="POV 6 - Đứng trước gương ngắm form & Sải bước",
                kind="FLOW_AI",
                narrator_text="Phối với áo thun hay sơ mi gì cũng hợp, đi làm đi chơi đều gọn gàng.",
                overlay_title="DỄ PHỐI MỌI OUTFIT",
                overlay_subtitle="Chỉn chu đi làm, dạo phố",
                image_index=0,
                prompt=(
                    f"Lower-body view of a person wearing the {noun} with white sneakers, no face: they turn slightly in front of a full-length mirror to check the fit. "
                    f"Bedroom floor with a few things on it, daylight. Neck-down only."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở hộp trên mặt bếp đá",
                kind="FLOW_AI",
                narrator_text=f"Mở hộp {short_name} ra coi nè. Nhìn trang nhã, cầm đầm tay.",
                overlay_title="ĐẬP HỘP ĐỒ GIA DỤNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"First-person view looking down at a home kitchen counter, no face: hands take the {noun} out of its plain box and set it down on the counter{idea_ctx}. "
                    f"A dish rack and a few sauce bottles nearby. Hands only."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Thao tác tương tác chi tiết",
                kind="FLOW_AI",
                narrator_text="Mặt chống dính láng mịn, mấy chỗ khớp nối với nút vặn làm kỹ lắm.",
                overlay_title="HOÀN THIỆN CHỈN CHU",
                overlay_subtitle="Láng mịn - Chắc chắn",
                image_index=0,
                prompt=(
                    f"Close-up of hands, no face: a hand turns the dial or runs a finger along the surface of the {noun}. Ordinary kitchen counter, ceiling light. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Thử nghiệm nấu nướng thực tế",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Nấu nhanh mà món chín đều."),
                overlay_title="NẤU NƯỚNG SIÊU MƯỢT",
                overlay_subtitle="Bắt nhiệt nhanh - Tiện lợi",
                image_index=0,
                prompt=(
                    f"Close-up of hands cooking with the {noun} at a home gas stove, no face: chopped vegetables sizzle gently and light steam rises. "
                    f"A splash of oil on the stovetop. Hands only."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Lau sạch nhẹ nhàng thảnh thơi",
                kind="FLOW_AI",
                narrator_text="Nấu xong lau nhẹ cái là sạch, khỏi chà khỏi cọ. Nhàn ghê luôn!",
                overlay_title="LAU NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Nấu nướng thảnh thơi",
                image_index=0,
                prompt=(
                    f"Close-up at the kitchen sink, no face: a hand wipes the {noun} with a damp yellow sponge and a film of oil comes off. A few dishes in the rack. Hands only."
                ),
            ),
        ]

    elif category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở hộp chai dưỡng trên bàn",
                kind="FLOW_AI",
                narrator_text=f"Mở hộp {short_name} ra coi nè. Chai thủy tinh cầm đầm tay, vòi bơm xịn lắm.",
                overlay_title="MỞ HỘP DƯỠNG DA",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"First-person view looking down at a cluttered vanity table, no face: hands take a {noun} in plain unbranded packaging out of its box and twist off the cap{idea_ctx}. "
                    f"Hair ties and cotton pads nearby, morning window light. Hands only."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Cận cảnh texture dưỡng chất",
                kind="FLOW_AI",
                narrator_text="Chất kem mỏng, vỗ nhẹ là thấm, mát mát mà không bết.",
                overlay_title="THẤM NHANH KHÔNG BẾT",
                overlay_subtitle="Mỏng nhẹ mát lạnh",
                image_index=0,
                prompt=(
                    "Close-up of hands, no face: a hand squeezes a few drops of the product onto the back of the other hand and spreads them in small circles. "
                    "Real skin with pores and fine lines. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Thẩm thấu căng bóng da",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Da ẩm mượt, căng căng tự nhiên cả ngày."),
                overlay_title="CĂNG MỌNG ẨM MƯỢT",
                overlay_subtitle="Cấp ẩm sâu tức thì",
                image_index=0,
                prompt=(
                    "Close-up of a cheek and fingertips only, no face, mouth not visible: fingertips gently pat the product into the skin of the cheek. "
                    "Real skin texture with pores, soft window light."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Gọn gàng trong túi xách",
                kind="FLOW_AI",
                narrator_text="Chai nhỏ gọn, bỏ túi xách đi làm đi chơi lúc nào cũng có.",
                overlay_title="NHỎ GỌN TIỆN LỢI",
                overlay_subtitle="Cấp ẩm mọi lúc mọi nơi",
                image_index=0,
                prompt=(
                    f"Close-up, no face: a hand drops the {noun} into a canvas tote bag on the bed. Hands only."
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
                name="POV 1 - Mở hộp trên tay & Test chất liệu",
                kind="FLOW_AI",
                narrator_text=f"Mở hộp {short_name} ra coi nè. Túi dày, dẻo, có van một chiều với khóa zip đôi.",
                overlay_title="TRẢI NGHIỆM TRÊN TAY",
                overlay_subtitle="Chất liệu PA+PE dẻo dai",
                image_index=0,
                prompt=(
                    f"First-person view looking down at a bed, no face: hands unfold an empty clear vacuum storage bag and run a finger along its double zip track{idea_ctx}. "
                    f"Creased bedsheet, daylight, normal speed. Hands only."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Khóa zip miết chặt & Hút xẹp 80%",
                kind="FLOW_AI",
                narrator_text="Kéo khóa zip lại, hút hơi qua van, túi xẹp xuống còn có chút xíu, đỡ cả đống chỗ.",
                overlay_title="HÚT XẸP 80% DIỆN TÍCH",
                overlay_subtitle="Van 1 chiều - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    "Close-up of a bed, no face: hands hold a small electric pump on the round valve of a clear vacuum storage bag stuffed with a puffer jacket; "
                    "with a steady hum the bag slowly shrinks and wrinkles tightly around the jacket over a few seconds. Normal speed. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Gọn gàng tủ quần áo",
                kind="FLOW_AI",
                narrator_text="Túi dẻo, xài lại được nhiều lần, cất đồ cả mùa không lo ẩm mốc. Tủ đồ gọn hẳn.",
                overlay_title="GỌN GÀNG TỦ QUẦN ÁO",
                overlay_subtitle="Chống ẩm mốc suốt 6-8 tháng",
                image_index=0,
                prompt=(
                    "First-person view facing an open wardrobe, no face: hands slide a flattened, wrinkled vacuum bag of clothes onto a shelf next to two others. "
                    "Clothes on hangers beside it, room light. Hands only."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Xếp gọn vali du lịch",
                kind="FLOW_AI",
                narrator_text="Soạn đồ đi chơi hay về quê đều nhàn, đồ cồng kềnh gom gọn, vali còn dư chỗ.",
                overlay_title="VALI RỘNG THÊM 50%",
                overlay_subtitle="Thảnh thơi lên đường",
                image_index=0,
                prompt=(
                    "Top-down view of an open suitcase on the floor, no face: hands lay two flattened vacuum bags of clothes into one half, leaving the other half free. "
                    "Normal speed. Hands only."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="POV 1 - Mở hộp trên tay trải nghiệm",
            kind="FLOW_AI",
            narrator_text=f"Mở hộp {short_name} ra coi nè. Nhỏ gọn mà làm chắc chắn hơn mình tưởng.",
            overlay_title="TRẢI NGHIỆM TRÊN TAY",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"First-person view looking down at a desk, no face: hands open a plain box and lift out the {noun}{idea_ctx}. Hands only."
            ),
        ),
        SceneDefinition(
            id=2,
            name="POV 2 - Thao tác tương tác thực tế",
            kind="FLOW_AI",
            narrator_text="Dùng dễ lắm, vài giây là xong, mấy chi tiết ăn khớp chắc chắn.",
            overlay_title="TIỆN LỢI DỄ SỬ DỤNG",
            overlay_subtitle="Chắc chắn - Nhanh chóng",
            image_index=0,
            prompt=(
                f"Close-up of hands at a home table, no face: hands use the {noun} once, slowly and simply, the way it is normally used. "
                f"Real fingerprints and small scratches on the table. Hands only."
            ),
        ),
        SceneDefinition(
            id=3,
            name="POV 3 - Thử nghiệm ứng dụng đời thường",
            kind="FLOW_AI",
            narrator_text=feature_line(feat1_title, feat1_desc, "Nhà cửa gọn gàng hơn hẳn."),
            overlay_title=feat1_title,
            overlay_subtitle="Hiệu quả bất ngờ",
            image_index=0,
            prompt=(
                f"First-person view, no face: hands use the {noun} during an ordinary moment at home. Lived-in room, daylight. Hands only."
            ),
        ),
        SceneDefinition(
            id=4,
            name="POV 4 - Hoàn thiện gọn gàng ưng ý",
            kind="FLOW_AI",
            narrator_text="Món đơn giản vậy thôi mà xài mỗi ngày tiện lắm luôn.",
            overlay_title="ĐẮC LỰC MỖI NGÀY",
            overlay_subtitle="Tiện ích 10 điểm",
            image_index=0,
            prompt=(
                f"Close-up, no face: a hand sets the {noun} down in its usual place on a shelf at home and straightens it. Hands only."
            ),
        ),
    ]


__all__ = ["build_faceless_pov_scenes", "build_vacuum_faceless_pov_scenes"]
