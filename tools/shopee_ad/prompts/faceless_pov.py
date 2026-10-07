"""Shopee ``faceless_pov`` scenes: hands-only first-person demos, no faces.
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, resolve_product_archetype, title_matches
from tools.common.models import SceneDefinition


def build_vacuum_faceless_pov_scenes(
    clean_title: str,
    feat1_title: str = "",
    feat1_desc: str = "",
    feat2_title: str = "",
    feat2_desc: str = "",
    idea_ctx: str = "",
) -> List[SceneDefinition]:
    """Build 4 authentic faceless POV scenes for handheld/cordless vacuum cleaners dynamically."""
    sc2_title = feat1_title if feat1_title else "LỰC HÚT MẠNH MẼ"
    sc2_sub = feat1_desc if feat1_desc else "Sạch bóng mọi khe kẹt"
    sc3_title = feat2_title if feat2_title else "ĐẦU HÚT ĐA NĂNG"
    sc3_sub = feat2_desc if feat2_desc else "Sofa - Bàn phím - Giường nệm"

    return [
        SceneDefinition(
            id=1,
            name="POV 1 - Mở hộp trên tay & Đầu hút đa năng",
            kind="FLOW_AI",
            narrator_text=f"Mở hộp chiếc {clean_title}, thiết kế không dây mini cầm nhẹ tênh, đi kèm trọn bộ đầu hút chuyên dụng cực kỳ tiện lợi.",
            overlay_title="TRẢI NGHIỆM TRÊN TAY",
            overlay_subtitle="Không dây mini - Đa năng",
            image_index=0,
            prompt=(
                f"Vertical 9:16 authentic commercial ad video. First-person POV looking down at a tidy modern wooden desk. "
                f"Two hands hold and rotate the sleek compact cordless handheld vacuum cleaner, showcasing its minimalist cylindrical body, premium matte texture, and ergonomic handle. "
                f"Thumb gently presses the power button, a subtle modern blue LED light glows. "
                f"Beside it on the desk, the various nozzle accessories rest neatly in background. "
                f"Hands keep holding the vacuum body smoothly, NO attaching parts, NO plugging nozzles, NO assembly. "
                f"Crisp studio lighting, smooth natural movement, sharp 4K detail{idea_ctx}. "
                f"Completely faceless, NO human face, NO head in frame, hands only, strictly 5 fingers. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="POV 2 - Lực hút lốc xoáy khe ghế ô tô",
            kind="FLOW_AI",
            narrator_text="Lực hút lốc xoáy cực mạnh, gắn đầu hút dẹt luồn sâu vào khe ghế ô tô và hộc để đồ, cuốn sạch vụn bánh đất cát trong một đường lia!",
            overlay_title=sc2_title,
            overlay_subtitle=sc2_sub,
            image_index=0,
            prompt=(
                f"Vertical 9:16 authentic fast-paced commercial ad video. First-person POV looking down inside a sleek modern car interior. "
                f"Hand holds the compact cordless handheld vacuum with a slim flat crevice nozzle attached, gliding firmly along the deep seat crevice and center console cup holder. "
                f"Satisfying cleaning effect, debris instantly vanishes into nozzle. "
                f"Crisp natural daylight through car window, snappy real-time motion, not slow motion, not floaty. "
                f"Completely faceless, NO human face, hands only, strictly 5 fingers. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=3,
            name="POV 3 - Đổi đầu chải hút sạch sofa & giường nệm",
            kind="FLOW_AI",
            narrator_text="Dễ dàng đổi sang đầu chải lông để vệ sinh bàn phím máy tính, hút sạch lông thú cưng và bụi mịn bám chặt trên ghế sofa hay giường nệm.",
            overlay_title=sc3_title,
            overlay_subtitle=sc3_sub,
            image_index=0,
            prompt=(
                f"Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up POV. "
                f"Hand firmly holds the compact handheld vacuum with the brush nozzle already securely attached, sweeping smoothly across an aesthetic textured fabric sofa and a mechanical computer keyboard, effortlessly picking up dust and pet hairs in one clean glide. "
                f"Bright commercial aesthetic lighting, realistic stable physics, crisp suction action. "
                f"Completely faceless, NO human face, hands only, strictly 5 fingers. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="POV 4 - Đổ rác 1 chạm & Màng lọc xả nước",
            kind="FLOW_AI",
            narrator_text="Pin dùng bền bỉ tiện lợi. Cốc bụi tháo rời đổ một chạm sạch sẽ, màng lọc xả sạch dưới vòi nước tái sử dụng bền bỉ nhiều năm!",
            overlay_title="MÀNG LỌC RỬA NƯỚC",
            overlay_subtitle="Vệ sinh nhanh gọn",
            image_index=0,
            prompt=(
                f"Vertical 9:16 authentic commercial ad video. Satisfying macro POV shot over a clean modern sink. "
                f"Hands hold the small circular white HEPA filter directly under a gentle stream of fresh tap water, washing it completely spotless and clean, water droplets splashing smoothly. "
                f"Then pan smoothly to the sleek clean handheld vacuum resting neatly upright on a minimalist charging dock on a sunny desk. "
                f"NO twisting, NO disassembly, NO pulling parts apart. "
                f"Bright airy natural lighting, crisp 4K texture, realistic water physics. "
                f"Completely faceless, NO human face, hands only, strictly exactly 5 fingers. NO thumbs-up, NO text overlays."
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
                    narrator_text=f"Mở hộp chiếc ghế kê chân {clean_title}, hoàn thiện cứng cáp và bề mặt con lăn massage rất đã tay.",
                    overlay_title="GHẾ KÊ CHÂN DƯỚI 100K",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. First-person POV looking down at a clean modern wooden floor or rug beside a desk. "
                        f"Hands unboxing and lifting the ergonomic footrest ({clean_title}) out of packaging. "
                        f"Macro focus on textured massage rollers and sturdy matte frame{idea_ctx}. Soft natural indoor lighting. "
                        f"NO human face, NO head in frame, hands only. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Chỉnh nấc & Xoay con lăn massage",
                    kind="FLOW_AI",
                    narrator_text="Điều chỉnh độ nghiêng nhiều nấc mượt mà, con lăn massage xoay êm ru cực kỳ thư giãn.",
                    overlay_title="CON LĂN MASSAGE ĐIỀU CHỈNH",
                    overlay_subtitle="Nhiều nấc độ nghiêng",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands pressing the angle adjustment tabs and spinning the central textured massage rollers of {clean_title}. "
                        f"Tactile smooth mechanical motion, satisfying clicks. Crisp commercial studio lighting. NO face, hands only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Trải nghiệm thực tế dưới gầm bàn",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Kê chân thoải mái, đỡ mỏi lưng và mỏi đùi hẳn khi ngồi làm việc lâu.",
                    overlay_title="ĐỠ MỎI CHÂN HẲN",
                    overlay_subtitle="Ngồi làm việc cả ngày êm ái",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. High-angle POV shot sitting at office desk, feet resting comfortably on {clean_title} under the desk. "
                        f"Feet gently rolling the massage rollers back and forth, demonstrating ergonomic comfort. Natural daylight under desk. "
                        f"NO face, feet and lower legs only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Góc làm việc thư thái gọn gàng",
                    kind="FLOW_AI",
                    narrator_text="Góc làm việc gọn gàng, ngồi học hay làm việc cả ngày đều dễ chịu và thư thái hơn hẳn!",
                    overlay_title="SETUP GỌN GÀNG THƯ THÁI",
                    overlay_subtitle="Món đồ văn phòng 10 điểm",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Aesthetic satisfying wide pan under the minimalist wooden desk, showing {clean_title} perfectly positioned next to desk legs. "
                        f"Clean spotless floor, warm ambient light, cozy relaxed vibe. NO face, completely faceless. NO text overlays."
                    ),
                ),
            ]
        elif is_desk_setup:
            return [
                SceneDefinition(
                    id=1,
                    name="POV 1 - Mở hộp khay kẹp bàn",
                    kind="FLOW_AI",
                    narrator_text=f"Mở hộp chiếc {clean_title}, kim loại nguyên khối sơn tĩnh điện rất đầm tay.",
                    overlay_title="KẸP BÀN GIẤU DÂY",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. First-person POV looking down at a modern wooden desk. "
                        f"Hands lifting {clean_title} out of box, showing solid metal build and smooth finish{idea_ctx}. Natural light. "
                        f"NO face, NO head in frame, hands only. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Vặn ốc kẹp bàn không khoan đục",
                    kind="FLOW_AI",
                    narrator_text="Chỉ cần vặn ốc kẹp vào mép bàn trong mười giây, chắc nịch không cần khoan đục.",
                    overlay_title="KẸP BÀN TRONG 10 GIÂY",
                    overlay_subtitle="Không khoan đục - Siêu chắc",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands clamping {clean_title} securely onto the edge of a clean wooden desk, turning the tightening knob smoothly. "
                        f"Firm solid grip, crisp commercial lighting. NO face, hands only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Giấu trọn ổ cắm dây điện",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Đặt gọn toàn bộ ổ cắm củ sạc vào lòng khay, dưới sàn sạch bong không còn sợi dây nào.",
                    overlay_title="GIẤU TRỌN MỌI DÂY CÁP",
                    overlay_subtitle="Dưới sàn sạch bong",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. POV shot of hands neatly organizing power strips and cables inside {clean_title} under desk edge. "
                        f"All tangled cables instantly disappear from the floor. Satisfying tidy transformation. NO face, hands only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Mặt bàn thông thoáng sạch sẽ",
                    kind="FLOW_AI",
                    narrator_text="Mặt bàn và gầm bàn sạch bong ngăn nắp, nhìn ngắm góc setup mà mê luôn!",
                    overlay_title="GÓC SETUP MƠ ƯỚC",
                    overlay_subtitle="Gọn gàng - Tinh tế",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Wide aesthetic pan across the spotless minimalist desk setup, zero dangling wires. "
                        f"Hand gently placing an iced coffee cup on the clean wooden desk, neck-down angle only. Warm morning sunlight. NO face in frame. NO text overlays."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="POV 1 - Mở hộp thiết bị trên tay",
                    kind="FLOW_AI",
                    narrator_text=f"Mở hộp {clean_title}, thiết kế nhỏ gọn tinh tế và hoàn thiện rất sắc sảo.",
                    overlay_title=clean_title[:28].upper(),
                    overlay_subtitle="Mở hộp trên tay",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. First-person POV looking down at hands unboxing {clean_title} onto a sleek wooden desk. "
                        f"Macro focus on product texture, tactile edges, and premium build{idea_ctx}. Natural daylight. "
                        f"NO face, NO head in frame, hands only. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="POV 2 - Thao tác kết nối & Tính năng",
                    kind="FLOW_AI",
                    narrator_text="Cắm vào nhận ngay tức thì, các nút bấm và cổng kết nối phản hồi cực kỳ chuẩn xác.",
                    overlay_title="KẾT NỐI NHANH NHẠY",
                    overlay_subtitle="Cắm là nhận ngay",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands plugging in or operating {clean_title}. "
                        f"Satisfying click motion, subtle LED glow, crisp high-tech commercial B-roll lighting. NO face, hands only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="POV 3 - Trải nghiệm thực tế mượt mà",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Tốc độ mượt mà, xử lý trơn tru mọi nhu cầu làm việc và giải trí.",
                    overlay_title="HIỆU NĂNG MƯỢT MÀ",
                    overlay_subtitle="Xử lý nhanh chóng",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. First-person POV shot hands typing naturally on keyboard with {clean_title} operating seamlessly beside laptop. "
                        f"Smooth productive workspace, warm aesthetic ambiance. NO face, hands only. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="POV 4 - Gọn nhẹ bỏ túi đồng hành",
                    kind="FLOW_AI",
                    narrator_text="Nhỏ gọn tiện lợi, bỏ túi mang theo đi làm hay đi cà phê cực kỳ tiện dụng mỗi ngày.",
                    overlay_title="GỌN NHẸ TIỆN LỢI",
                    overlay_subtitle="Đồng hành mỗi ngày",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Hands sliding {clean_title} into everyday carry sling bag or pocket, clean minimalist aesthetic. "
                        f"Warm natural lighting. NO face, hands and bag only. NO text overlays."
                    ),
                ),
            ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở gói & Trải phẳng chất vải",
                kind="FLOW_AI",
                narrator_text=f"Mở gói trải nghiệm chiếc {clean_title}, chất vải sờ mềm mát tay và đường kim mũi chỉ rất đều đẹp.",
                overlay_title="MỞ GÓI TRẢI NGHIỆM THẬT",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic mobile video shot on iPhone 15 Pro, natural 1x speed, handheld camera feel. "
                    f"First-person POV looking down at a clean wooden table or bed. Hands smoothly unfolding {clean_title}, "
                    f"running palms flat across the fabric to show crisp weave, matte texture, and zero wrinkles. Natural soft daylight. "
                    f"NO human face, NO head in frame, hands only. NO text overlays, NO slow motion."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Cận cảnh cạp chun & Túi lé tiện lợi",
                kind="FLOW_AI",
                narrator_text="Chi tiết cạp chun co giãn cực kỳ dễ chịu, kết hợp túi lé sâu tiện lợi đựng điện thoại hay ví tiền.",
                overlay_title="CẠP CHUN & TÚI LÉ SÂU",
                overlay_subtitle="Co giãn êm ái - Tiện dụng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic mobile video shot on iPhone 15 Pro, real-time natural speed. "
                    f"Macro close-up shot of hands inspecting the flexible elastic waistband of {clean_title}, stretching it outwards to show comfort, "
                    f"then slipping hand deep into the slanted front pocket smoothly. Crisp lighting, authentic smartphone focus. "
                    f"NO face, hands only. NO text overlays, NOT slow motion."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Test co giãn & Đàn hồi vải",
                kind="FLOW_AI",
                narrator_text="Co giãn đàn hồi cực tốt, kéo căng thả ra là về form ngay, giặt máy thoải mái không lo nhão xù.",
                overlay_title="CO GIÃN ĐÀN HỒI CỰC TỐT",
                overlay_subtitle="Không nhăn xù - Thoáng mát",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic mobile video shot on iPhone 15 Pro, natural brisk speed. "
                    f"Macro close-up shot of hands firmly stretching the fabric of {clean_title} horizontally and diagonally, "
                    f"releasing it to show instant snappy recovery without wrinkling. Crisp commercial fashion B-roll lighting. "
                    f"NO face, hands only. NO text overlays, NOT slow motion."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Thao tác đút tay túi quần lấy điện thoại",
                kind="FLOW_AI",
                narrator_text="Đút điện thoại hay ví vào túi sâu thoải mái, form quần vẫn phẳng phiu đứng dáng không hề bị cộm.",
                overlay_title="TÚI SÂU TIỆN LỢI",
                overlay_subtitle="Không lo cộm - Đứng form",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic smartphone footage, real-time 1x speed, subtle handheld motion. "
                    f"Waist-to-thigh close-up of person wearing {clean_title}, smoothly sliding a smartphone into the front slanted pocket, "
                    f"then pulling it out effortlessly. Clean tailored pocket silhouette, no bulging. Natural modern room light. "
                    f"Neck-down only, NO face, NO head in frame. NO text overlays, NOT slow motion."
                ),
            ),
            SceneDefinition(
                id=5,
                name="POV 5 - Lên form thực tế & Vận động thoải mái",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Lên form đứng dáng vừa vặn, đứng lên ngồi xuống hay vận động cả ngày vẫn cực kỳ thoải mái.",
                overlay_title="LÊN FORM TÔN DÁNG VỪA VẶN",
                overlay_subtitle="Đứng lên ngồi xuống thoải mái",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic mobile camera shot on iPhone 15 Pro, real-time normal human speed. "
                    f"Lower-body POV angle of person wearing {clean_title}, taking two firm steps forward, bending knees and doing a comfortable squat, "
                    f"then standing up smoothly. Demonstrates stretch flexibility and sharp tailored leg shape. Natural room daylight. "
                    f"Neck-down only, NO face, NO head visible. NO text overlays, NOT slow motion."
                ),
            ),
            SceneDefinition(
                id=6,
                name="POV 6 - Đứng trước gương ngắm form & Sải bước",
                kind="FLOW_AI",
                narrator_text="Chiếc quần dễ phối đồ, kết hợp cùng áo thun hay sơ mi đi làm, đi chơi đều rất chỉn chu và bảnh bao.",
                overlay_title="DỄ PHỐI MỌI OUTFIT",
                overlay_subtitle="Chỉn chu đi làm, dạo phố",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic mobile video, real-time 1x speed, brisk confident movement. "
                    f"Lower-body shot of person wearing {clean_title} paired with clean white sneakers, standing in front of a modern full-length mirror, "
                    f"turning 45 degrees to check the neat straight-leg fit, then taking two crisp brisk walking steps. "
                    f"Realistic floor-contact footsteps, natural indoor daylight. NO face visible, neck-down only. "
                    f"NO text overlays, NOT slow motion, NOT floaty."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở hộp trên mặt bếp đá",
                kind="FLOW_AI",
                narrator_text=f"Mở hộp chiếc {clean_title} trên bàn bếp, thiết kế trang nhã và cầm đầm tay chắc chắn.",
                overlay_title="ĐẬP HỘP ĐỒ GIA DỤNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. First-person POV looking down at a bright white marble kitchen countertop. "
                    f"Hands unboxing {clean_title} and placing it cleanly on the counter. Macro view of sleek surface finish{idea_ctx}. "
                    f"NO face, NO head in frame, hands only. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Thao tác tương tác chi tiết",
                kind="FLOW_AI",
                narrator_text="Bề mặt chống dính láng mịn, các khớp nối và nút vặn hoàn thiện rất chỉn chu.",
                overlay_title="HOÀN THIỆN CHỈN CHU",
                overlay_subtitle="Láng mịn - Chắc chắn",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands turning control dial or touching the smooth surface of {clean_title}. "
                    f"Clean tactile interaction, crisp kitchen commercial lighting. NO face, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Thử nghiệm nấu nướng thực tế",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Nấu nướng siêu mượt mà, món ăn chín đều vàng giòn mà tiết kiệm thời gian.",
                overlay_title="NẤU NƯỚNG SIÊU MƯỢT",
                overlay_subtitle="Bắt nhiệt nhanh - Tiện lợi",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. POV shot of hands operating or cooking with {clean_title}, fresh ingredients sizzling gently with light steam. "
                    f"Appetizing food commercial B-roll. NO face, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Lau sạch nhẹ nhàng thảnh thơi",
                kind="FLOW_AI",
                narrator_text="Nấu xong lấy khăn lau nhẹ là sạch bong, căn bếp gọn gàng và việc nội trợ thảnh thơi hơn rất nhiều!",
                overlay_title="LAU NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Nấu nướng thảnh thơi",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Quick effortless swipe of a soft cloth cleaning {clean_title} perfectly spotless on the sparkling counter. "
                    f"Clean bright minimalist kitchen, peaceful vibe. NO face in frame. NO text overlays."
                ),
            ),
        ]

    elif category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="POV 1 - Mở hộp chai dưỡng trên bàn",
                kind="FLOW_AI",
                narrator_text=f"Mở hộp {clean_title}, thiết kế chai thủy tinh cầm đầm tay và vòi pump rất xịn.",
                overlay_title="MỞ HỘP DƯỠNG DA",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. First-person POV looking down at hands unboxing an elegant skincare bottle ({clean_title}) on a sunlit vanity table. "
                    f"Macro focus on dropper/pump and glass bottle reflections{idea_ctx}. Soft morning sunlight. "
                    f"NO face, NO head in frame, hands only. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Cận cảnh texture dưỡng chất",
                kind="FLOW_AI",
                narrator_text="Chất kem mỏng nhẹ, vỗ lên da cái là thấm ngay, mát lạnh và không hề bết rít.",
                overlay_title="THẤM NHANH KHÔNG BẾT",
                overlay_subtitle="Mỏng nhẹ mát lạnh",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands dispensing silky translucent drops of {clean_title} onto the back of hand. "
                    f"Smooth blending texture, dewy water-burst effect, pristine cosmetic commercial lighting. NO face, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Thẩm thấu căng bóng da",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Cấp ẩm sâu tức thì, làn da căng mọng rạng rỡ tự nhiên suốt cả ngày dài.",
                overlay_title="CĂNG MỌNG ẨM MƯỢT",
                overlay_subtitle="Cấp ẩm sâu tức thì",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Close-up hands gently patting product onto cheekbone and jawline, showing instant radiant glow and hydration. "
                    f"Cheek and hands close-up only, NO full face, mouth not visible. Soft warm lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Gọn gàng trong túi xách",
                kind="FLOW_AI",
                narrator_text="Chai nhỏ gọn, tiện mang theo túi xách đi làm hay du lịch, sẵn sàng cấp ẩm mọi lúc mọi nơi!",
                overlay_title="NHỎ GỌN TIỆN LỢI",
                overlay_subtitle="Cấp ẩm mọi lúc mọi nơi",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Hands slipping the sleek bottle into an aesthetic leather bag, aesthetic vanity setup in background. "
                    f"Warm natural light. NO face in frame. NO text overlays."
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
                narrator_text=f"Mở hộp {clean_title}, chất liệu PA PE dày dặn dẻo dai, van silicon một chiều và khóa zip đôi cực kỳ chắc chắn.",
                overlay_title="TRẢI NGHIỆM TRÊN TAY",
                overlay_subtitle="Chất liệu PA+PE dẻo dai",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. First-person POV looking down at a clean modern wooden desk. "
                    f"Two hands briskly unpack the clear transparent vacuum compression bag, unfolding it smoothly across the tabletop. "
                    f"Macro focus on the thick tear-resistant PA PE material texture, the bright double-track zip lock, and the circular one-way silicone valve. "
                    f"Hands firmly stretch the edge to demonstrate supreme flexibility and durability{idea_ctx}. "
                    f"Brisk snappy movements, crisp commercial studio lighting, natural real-time speed, not slow motion, not floaty. "
                    f"Completely faceless, NO human face, NO head in frame, hands only. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="POV 2 - Khóa zip miết chặt & Hút xẹp 80%",
                kind="FLOW_AI",
                narrator_text="Khóa zip đôi miết chặt kín khít, van hút một chiều xẹp lép phẳng lì chỉ sau mười giây, giảm ngay 80% diện tích!",
                overlay_title="HÚT XẸP 80% DIỆN TÍCH",
                overlay_subtitle="Van 1 chiều - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up B-roll, 60fps crisp commercial studio lighting. "
                    f"Hands briskly slide a thick puffy winter down jacket inside the transparent compression bag, then swiftly glide the white sealing clip firmly along the double-track yellow zip lock in one smooth motion. "
                    f"Hands attach a compact electric pump to the round one-way valve; the bulky coat instantly deflates and flattens down into a rock-firm, paper-thin, rigid flat slab in seconds. "
                    f"Fast-forward deflation effect, brisk snappy hand movements, natural real-life speed, not floaty. "
                    f"Completely faceless, NO human face, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=3,
                name="POV 3 - Gọn gàng tủ quần áo",
                kind="FLOW_AI",
                narrator_text="Chất liệu dẻo dai tái sử dụng nhiều năm, bảo vệ chống ẩm mốc bụi bẩn suốt sáu đến tám tháng. Tủ quần áo gia đình luôn ngăn nắp gọn gàng!",
                overlay_title="GỌN GÀNG TỦ QUẦN ÁO",
                overlay_subtitle="Chống ẩm mốc suốt 6-8 tháng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. First-person POV facing an open modern wooden wardrobe closet with warm interior lighting. "
                    f"Two hands lift a neat vertical stack of 4 ultra-thin compressed flat vacuum slabs and slide them smoothly onto a wooden closet shelf, lined up neatly like books on a bookshelf. "
                    f"The camera reveals the closet shelf is now 80 percent completely empty, spacious, and spotlessly organized. "
                    f"Brisk confident hand movements, crisp natural lighting, real-time speed, not slow motion. "
                    f"Completely faceless, NO human face, NO head in frame, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="POV 4 - Xếp gọn vali du lịch",
                kind="FLOW_AI",
                narrator_text="Chuẩn bị hành lý du lịch hay về quê đều nhàn tênh. Đồ đạc cồng kềnh xếp gọn trong nháy mắt, vali rộng thênh thang tự tin lên đường!",
                overlay_title="VALI RỘNG THÊM 50%",
                overlay_subtitle="Thảnh thơi lên đường",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Top-down POV flat-lay looking directly down at a sleek open suitcase on the floor. "
                    f"Hands effortlessly drop two ultra-thin compressed flat slabs into the bottom compartment in one second, taking up barely any room. "
                    f"The other half remains completely spacious and free for sneakers and travel pouches. "
                    f"Hands smoothly fold the suitcase lid shut with a crisp satisfying click, resting palms flat on the luggage with a calm satisfied feel. "
                    f"Fast snappy motions, natural commercial ad speed, stable realistic physics. "
                    f"Completely faceless, NO human face, hands only. NO thumbs-up, NO distorted fingers. NO text overlays."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="POV 1 - Mở hộp trên tay trải nghiệm",
            kind="FLOW_AI",
            narrator_text=f"Mở hộp {clean_title}, món đồ nhỏ gọn với độ hoàn thiện cứng cáp hơn mong đợi rất nhiều.",
            overlay_title="TRẢI NGHIỆM TRÊN TAY",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. First-person POV looking down at hands unboxing {clean_title} on a tidy desk. "
                f"Macro focus on product details, texture, and clean packaging{idea_ctx}. Natural soft light. "
                f"NO face, NO head in frame, hands only. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="POV 2 - Thao tác tương tác thực tế",
            kind="FLOW_AI",
            narrator_text="Thao tác sử dụng dễ dàng chỉ trong vài giây, các chi tiết ăn khớp chắc chắn và tiện lợi.",
            overlay_title="TIỆN LỢI DỄ SỬ DỤNG",
            overlay_subtitle="Chắc chắn - Nhanh chóng",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using and demonstrating the features of {clean_title}. "
                f"Smooth confident hand movement, clean commercial B-roll lighting. NO face, hands only. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=3,
            name="POV 3 - Thử nghiệm ứng dụng đời thường",
            kind="FLOW_AI",
            narrator_text=f"{feat1_desc}. Giải quyết công việc nhanh gọn, giúp không gian sống ngăn nắp hơn.",
            overlay_title=feat1_title,
            overlay_subtitle="Hiệu quả bất ngờ",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. First-person POV hands using {clean_title} in practical daily routine. "
                f"Smooth satisfying result, aesthetic cozy room ambiance. NO face, hands only. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="POV 4 - Hoàn thiện gọn gàng ưng ý",
            kind="FLOW_AI",
            narrator_text="Một món đồ đơn giản nhưng cực kỳ đắc lực, rất đáng để trải nghiệm mỗi ngày!",
            overlay_title="ĐẮC LỰC MỖI NGÀY",
            overlay_subtitle="Tiện ích 10 điểm",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Aesthetic shot of {clean_title} resting neatly in place in a clean modern room. "
                f"Hand resting naturally beside the product, neck-down angle. Warm natural light. NO face, NO thumbs-up, NO distorted fingers. NO text overlays."
            ),
        ),
    ]


__all__ = ["build_faceless_pov_scenes", "build_vacuum_faceless_pov_scenes"]
