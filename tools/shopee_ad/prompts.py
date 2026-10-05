"""Shopee Ad Prompts & AI Scene Generator Templates.
Dedicated exclusively to physical product categories, macro POV B-roll, KOC personas, and CTA prompts.
"""
from typing import List, Optional

from tools.common.models import SceneDefinition

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
    elif category == "HEALTH_FITNESS":
        return {
            "intro": "an athletic 25-year-old Vietnamese young man with short trim black hair, fit build, wearing a dark grey athletic crew-neck tee",
            "cont": "the same athletic 25-year-old Vietnamese young man with short trim black hair and dark grey tee",
        }
    elif category == "KITCHEN_HOME":
        return {
            "intro": "a friendly 26-year-old Vietnamese homemaker with neat ponytail black hair, warm smile, wearing a casual white t-shirt under a light beige apron",
            "cont": "the same friendly 26-year-old Vietnamese homemaker with neat ponytail black hair and beige apron",
        }
    else:  # TECH_GADGETS and GENERAL_LIFESTYLE
        return {
            "intro": "a stylish 25-year-old Vietnamese professional young man with neat short black side-part hair, wearing a crisp light-blue collared Oxford shirt and dark slacks",
            "cont": "the same 25-year-old Vietnamese professional young man with neat short black side-part hair and light-blue Oxford shirt",
        }


def _build_flow_cinematic_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    social_proof_title: str,
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """Generate 4 cinematic AI scenes tailored to the product's physical category."""
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    persona = _get_character_persona(category)

    if category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi lo da khô mốc mỗi sáng",
                kind="FLOW_AI",
                narrator_text=f"Mỗi lần trang điểm hay ra đường, da khô mốc khó chịu thực sự. Mình thử dùng {clean_title} này thì bất ngờ luôn!",
                overlay_title="DA KHÔ MỐC MỖI SÁNG?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Beautiful young Vietnamese woman sitting in front of a sunlit vanity mirror in a bright modern aesthetic bedroom. "
                    f"She is holding an elegant skincare bottle ({clean_title}) in her hands, admiring its premium packaging with a subtle radiant smile. "
                    f"Calm confident expression, glowing healthy clear skin, mouth closed, no speaking, no dialogue{idea_ctx}. Soft morning sunlight, shallow depth of field. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Thao tác dưỡng da mỏng nhẹ",
                kind="FLOW_AI",
                narrator_text="Chất kem mỏng nhẹ, vỗ lên da cái là thấm ngay, không hề bết rít. Cảm giác mát lạnh, da ẩm mượt thích lắm.",
                overlay_title="THẤM NHANH KHÔNG BẾT",
                overlay_subtitle="Mỏng nhẹ - Mát lạnh",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of gentle hands dispensing smooth silky drops of the product onto skin, gently patting and blending it smoothly. "
                    f"Dewy glowing skin reflection, water droplet moisture, crisp texture commercial B-roll lighting, 4K resolution. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Hiệu quả căng bóng mịn màng",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Da căng bóng tự nhiên suốt cả ngày, không lo đổ dầu hay xuống tông.",
                overlay_title=feat1_title,
                overlay_subtitle="Căng bóng rạng ngời",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. The young woman looks at her reflection in the mirror with pure satisfaction, gently touching her glowing smooth cheek. "
                    f"Natural radiant dewy complexion, subtle satisfied smile, mouth closed, no speaking. Soft warm indoor vanity lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Nhỏ gọn tự tin mỗi ngày",
                kind="FLOW_AI",
                narrator_text="Chai nhỏ gọn, tiện bỏ túi xách mang theo đi làm hay đi chơi. Đơn giản mà tự tin hơn hẳn mỗi khi ra ngoài!",
                overlay_title="GỌN NHẸ TỰ TIN",
                overlay_subtitle="Đồng hành mỗi ngày",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Woman slipping the sleek cosmetic bottle into her stylish leather handbag, standing up and smiling warmly before heading out. "
                    f"Calm confident posture, mouth closed, no speaking, vibrant natural aesthetic. NO text overlays."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi ngán ngẩm chùi rửa bếp núc",
                kind="FLOW_AI",
                narrator_text=f"Ai nấu ăn mà ghét nhất cảnh chảo dính chặt, chùi rửa cực hình thì xem ngay cái này nha!",
                overlay_title="CHÙI RỬA PHÁT NGÁN?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Modern aesthetic kitchen with white marble countertops and warm ambient lighting. "
                    f"A young Vietnamese homemaker holding and admiring the sleek modern {clean_title} with an appreciative smile. "
                    f"Mouth closed, no speaking, calm satisfied expression{idea_ctx}. 35mm lens, warm inviting atmosphere. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Thao tác chiên rán mượt mà",
                kind="FLOW_AI",
                narrator_text=f"Đổi sang {clean_title} này xem, tráng trứng hay chiên cá lướt vèo vèo. Đáy chảo bắt nhiệt nhanh, chiên rán cực kỳ nhàn.",
                overlay_title="CHIÊN XÀO SIÊU MƯỢT",
                overlay_subtitle="Bắt nhiệt nhanh - Không dính",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Dramatic macro close-up shot of hands cooking or operating {clean_title} on the countertop. "
                    f"Appetizing fresh colorful ingredients, gentle sizzle and steam, smooth effortless movement. Commercial food B-roll lighting, shallow depth of field. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Món ngon tròn vị đầm ấm",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Món ăn chín đều vàng giòn, bữa cơm gia đình nấu nhanh mà ngon hơn hẳn.",
                overlay_title=feat1_title,
                overlay_subtitle="Chín đều thơm ngon",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Plating a mouth-watering delicious hot meal onto a ceramic dish, creator leaning back with a genuine satisfied smile. "
                    f"Mouth closed, no speaking, cozy warm home ambiance, cinematic lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Vệ sinh nhẹ nhàng thảnh thơi",
                kind="FLOW_AI",
                narrator_text="Nấu xong lấy khăn giấy lau nhẹ là sạch bong, không phải kỳ cọ vất vả. Gian bếp gọn gàng, nấu nướng thảnh thơi thực sự!",
                overlay_title="LAU NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Nấu nướng thảnh thơi",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Quick effortless swipe of a soft cloth cleaning {clean_title} perfectly spotless on the sparkling counter. "
                    f"Clean bright minimalist kitchen, satisfied calm vibe, mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Đau đầu chọn đồ mỗi sáng",
                kind="FLOW_AI",
                narrator_text=f"Sáng nào đứng trước tủ đồ cũng đau đầu không biết mặc gì cho gọn gàng, tôn dáng? Thử ngay {clean_title} này nhé!",
                overlay_title="ĐAU ĐẦU CHỌN ĐỒ?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Stylish young Vietnamese model standing in a modern boutique or sunlit loft, holding up {clean_title} with genuine admiration. "
                    f"Fashion editorial aesthetic, calm confident expression, mouth closed, no speaking{idea_ctx}. Soft cinematic lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Vải mềm mát co giãn tốt",
                kind="FLOW_AI",
                narrator_text="Vải mềm mịn, sờ mát tay và co giãn cực kỳ dễ chịu. Đường kim mũi chỉ may rất kỹ, giặt máy thoải mái không lo nhão xù.",
                overlay_title="VẢI MÁT CO GIÃN TỐT",
                overlay_subtitle="Đường may tỉ mỉ - Bền đẹp",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands gently touching and stretching the premium fabric of {clean_title}. "
                    f"Crisp weave texture, flawless stitching, soft natural drape in dynamic light. Premium fashion commercial look. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Lên form vừa vặn tôn dáng",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Lên form vừa vặn, mặc đi làm hay đi cà phê cả ngày vẫn thoải mái.",
                overlay_title=feat1_title,
                overlay_subtitle="Thoải mái vận động cả ngày",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person checking their look in a full-length mirror, adjusting outfit naturally with an appreciative smile of confidence. "
                    f"Flattering fit, modern silhouette, mouth closed, no speaking. Chic indoor aesthetic. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Dễ phối đồ tự tin dạo phố",
                kind="FLOW_AI",
                narrator_text="Chiếc áo đơn giản mà phối quần jean hay chân váy đều xinh. Mặc lên tự tin hơn hẳn mỗi khi ra ngoài!",
                overlay_title="DỄ PHỐI MỌI OUTFIT",
                overlay_subtitle="Đi làm, dạo phố cực xinh",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. The model walking confidently down a trendy sunlit city street or outdoor cafe, with natural poise and chic energy. "
                    f"Golden hour sunlight, shallow depth of field. Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "HEALTH_FITNESS":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Cổ vai gáy cứng đờ ê ẩm",
                kind="FLOW_AI",
                narrator_text=f"Ngồi làm việc cả ngày, cổ vai gáy cứng đờ ê ẩm phát mệt đúng không? Mình chỉ cho cách này nha!",
                overlay_title="CỔ VAI GÁY CỨNG ĐỜ?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young Vietnamese person in athletic wear in a modern wellness room or gym, holding {clean_title} with an eager appreciative look. "
                    f"Calm focused expression, mouth closed, no speaking{idea_ctx}. Natural soft light, wellness vibe. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lực rung đầm chắc êm ái",
                kind="FLOW_AI",
                narrator_text=f"Dùng thử {clean_title} này xem. Lực rung đầm chắc, tác động sâu vào từng bó cơ mà máy chạy êm ru.",
                overlay_title="XUNG LỰC ĐẦM ÊM",
                overlay_subtitle="Giảm đau mỏi sâu tức thì",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands operating {clean_title}, smoothly demonstrating its powerful vibration and ergonomic grip. "
                    f"Crisp metallic accents, clean modern design, cinematic B-roll lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Người nhẹ bẫng sảng khoái",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Xoa dịu cơn nhức mỏi tức thì, người nhẹ nhõm và sảng khoái hẳn ra.",
                overlay_title=feat1_title,
                overlay_subtitle="Thư giãn sâu từng tế bào",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person leaning back on comfortable mat, feeling tension melt away, taking a deep breath of relief with a peaceful smile. "
                    f"Mouth closed, no speaking, calm zen lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Bỏ túi tiện lợi mọi nơi",
                kind="FLOW_AI",
                narrator_text="Máy nhỏ gọn, bỏ túi mang lên công ty hay đi du lịch đều tiện. Tan ca mệt mỏi có em này là khỏe liền!",
                overlay_title="NHỎ GỌN TIỆN LỢI",
                overlay_subtitle="Chăm sóc cơ thể mỗi ngày",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person zipping up their sports bag with {clean_title} neatly packed inside, walking out energized and refreshed. "
                    f"Active vibrant lifestyle, mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "TECH_GADGETS":
        is_storage = any(k in clean_title.lower() for k in ["usb", "ổ đĩa", "flash drive", "thẻ nhớ", "ổ cứng", "ssd"])
        if is_storage:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Ức chế vì đầy ổ cứng giữa deadline",
                    kind="FLOW_AI",
                    narrator_text=f"Laptop đang làm việc gấp mà cứ báo đầy bộ nhớ đỏ lòm, nhìn ức chế thật sự đúng không?",
                    overlay_title="BÁO ĐỘNG ĐẦY Ổ CỨNG?",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. A stylish young Vietnamese professional sitting at a minimalist modern wooden desk with a slim silver laptop. "
                        f"The person is holding a sleek metallic {clean_title} in their hand, inspecting its compact elegant metal finish with a subtle satisfied smile. "
                        f"Calm focused expression, mouth closed, no speaking, no dialogue{idea_ctx}. Crisp 4K textures, warm natural morning cafe lighting. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Cắm là nhận ngay tức thì",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm thử cái {clean_title} này xem. Vỏ kim loại nhỏ xíu như móc khóa, cắm vào nhận ngay, giải phóng hàng trăm gigabyte tức thì.",
                    overlay_title="CẮM VÀO NHẬN NGAY",
                    overlay_subtitle="Kim loại nguyên khối - Siêu bền",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands plugging the metallic {clean_title} into the side USB port of a slim laptop on a clean wooden desk. "
                        f"Smooth precise insertion motion, tiny soft blue LED indicator illuminates. Crisp metallic reflection, commercial tech lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Sao chép siêu tốc nhẹ cả đầu",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Sao chép video tài liệu nặng vèo cái là xong, nhẹ cả đầu.",
                    overlay_title=feat1_title,
                    overlay_subtitle="Tốc độ sao chép siêu tốc",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Young Vietnamese creator working smoothly on their laptop with {clean_title} plugged into the side port next to iced coffee. "
                        f"Types naturally on the keyboard, looking at the screen with an appreciative nod of satisfaction as large files transfer instantly. "
                        f"Calm focused expression, mouth closed, no speaking, no dialogue. Aesthetic modern workspace. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Móc khóa an tâm mang theo mọi nơi",
                    kind="FLOW_AI",
                    narrator_text="Móc gọn cùng chìa khóa xe hay balo, mang theo bên mình mọi lúc mọi nơi, không bao giờ lo mất dữ liệu!",
                    overlay_title="MÓC KHÓA TIỆN LỢI",
                    overlay_subtitle="Gọn nhẹ - An tâm tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Cinematic close-up of hands attaching {clean_title} onto a modern car keychain, slipping keys into pocket and closing the laptop. "
                        f"Modern dynamic tech lifestyle, warm natural lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Nâng cấp góc làm việc gọn gàng",
                    kind="FLOW_AI",
                    narrator_text=f"Góc làm việc mà thiếu món này thì quả là thiếu sót. Cùng mình trải nghiệm {clean_title} nhé!",
                    overlay_title="GÓC SETUP TIỆN ÍCH",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Young Vietnamese tech enthusiast sitting at an aesthetic minimalist workspace, holding and admiring {clean_title}. "
                        f"Calm focused expression, subtle genuine smile, mouth closed, no speaking{idea_ctx}. Modern desk setup with warm ambient LED light. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Kết nối nhanh nhạy chắc chắn",
                    kind="FLOW_AI",
                    narrator_text="Cầm trên tay thấy đầm chắc, kết nối siêu nhanh và nhạy. Thiết kế tối giản, đặt lên bàn nhìn hiện đại hẳn.",
                    overlay_title="KẾT NỐI NHANH NHẠY",
                    overlay_subtitle="Đầm chắc - Siêu mượt mà",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands interacting with and activating {clean_title}. "
                        f"Satisfying click or indicator light glowing, sleek matte finish reflections, premium commercial tech lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Thao tác mượt mà tập trung",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Mọi thao tác mượt mà, giúp mình tập trung làm việc hiệu quả hơn rất nhiều.",
                    overlay_title=feat1_title,
                    overlay_subtitle="Hiệu năng vượt trội",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Person operating their tech setup with maximum efficiency, smiling approvingly at the smooth performance. "
                        f"Calm focused expression, mouth closed, no speaking. Modern creative studio lighting. NO text overlays."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Nhỏ gọn trơn tru mỗi ngày",
                    kind="FLOW_AI",
                    narrator_text=f"{feat2_desc}. Đơn giản, nhỏ gọn mà giải quyết công việc cực kỳ trơn tru!",
                    overlay_title="TỐI ƯU CÔNG VIỆC",
                    overlay_subtitle="Tiện lợi tối đa",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Hands sliding {clean_title} into everyday carry sling bag, standing up ready for meetings. "
                        f"Dynamic urban professional vibe, mouth closed, no speaking. NO text overlays."
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
                name="Hook - Giải pháp hành lý gọn gàng",
                kind="FLOW_AI",
                narrator_text=f"Chuẩn bị hành lý du lịch hay dọn tủ đồ mà chăn màn quần áo quá cồng kềnh? Trải nghiệm ngay {clean_title} này nhé!",
                overlay_title="HÀNH LÝ GỌN GÀNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Shot on 35mm lens, 60fps real-time commercial look, crisp realistic motion. "
                    f"Featuring {persona['intro']} in a modern bright bedroom, standing beside an open suitcase with a bulky pile of coats. "
                    f"They energetically hold up the transparent vacuum compression bag with a confident, bright smile toward camera{idea_ctx}. "
                    f"Fast snappy movement, brisk natural human speed, not slow motion, not floaty. Realistic natural daylight. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Hút xẹp 80% chỉ trong 10 giây",
                kind="FLOW_AI",
                narrator_text="Khóa zip đôi miết chặt, van silicon một chiều hút khí xẹp lép phẳng lì chỉ sau 10 giây, giảm ngay 80% diện tích!",
                overlay_title="GIẢM 80% DIỆN TÍCH",
                overlay_subtitle="Khóa zip đôi - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up B-roll, 60fps crisp commercial lighting. "
                    f"Hands briskly sliding a thick puffy down jacket into the transparent vacuum compression bag, swiftly running the sealing clip along the double-track yellow zip lock. "
                    f"Hands attach the suction nozzle to the circular one-way silicon valve; the bag instantly deflates in a fast satisfying compression, flattening down into a thin, firm, solid slab. "
                    f"Brisk snappy hand movements, fast-forward deflation effect, natural real-life speed, not floaty. NO face, hands only. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Xếp vừa in, rộng thêm nửa vali",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Đống đồ cồng kềnh xếp gọn vào một góc, vali vẫn còn dư nửa khoảng trống tha hồ mang thêm đồ.",
                overlay_title="VALI RỘNG THÊM 50%",
                overlay_subtitle="Chất liệu dẻo dai - Tái sử dụng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Medium close-up, sharp 35mm lens, 60fps real-time look. "
                    f"Featuring {persona['cont']} in the sunlit room, excitedly holding up the ultra-thin, rock-firm compressed vacuum slab vertically toward the camera like a thin laptop to show how completely flat it is. "
                    f"With a confident bright smile, they effortlessly slide the flat slab into one side of the open suitcase using just two fingers, revealing the rest of the suitcase completely spacious and empty. "
                    f"Snappy confident gestures, natural brisk human motion, not slow motion, not floaty. Mouth closed, no dialogue. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Kéo khóa nhẹ tênh, tự tin lên đường",
                kind="FLOW_AI",
                narrator_text=f"{feat2_desc}. Kéo khóa vali nhẹ tênh, thảnh thơi lên đường tận hưởng trọn vẹn chuyến đi!",
                overlay_title="TỰ TIN LÊN ĐƯỜNG",
                overlay_subtitle="Bảo vệ chống ẩm mốc",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 authentic fast-paced commercial ad video. Medium shot, bright natural morning sunlight, 60fps real-time commercial look. "
                    f"Featuring {persona['cont']}, standing beside the sleek, fully packed upright suitcase. In one swift, effortless motion, they glide the exterior zipper completely shut, "
                    f"give the top of the suitcase a satisfied proud pat with their hand, and pull up the aluminum handle with a crisp click. "
                    f"They look directly at camera with a beaming, confident smile and give a cheerful thumbs-up, ready to travel. "
                    f"Crisp energetic movement, natural human speed, stable physics, not floaty. Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Trải nghiệm món đồ bất ngờ",
            kind="FLOW_AI",
            narrator_text=f"Lướt thấy món này hay quá, mình đặt về dùng thử và thực sự bất ngờ với {clean_title} này luôn!",
            overlay_title="BẤT NGỜ TIỆN DỤNG",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young Vietnamese person sitting at a modern desk, holding and admiring {clean_title} with great appreciation. "
                f"Subtle satisfied smile, calm focused expression, mouth closed, no speaking, no dialogue{idea_ctx}. Warm natural lighting, 35mm lens. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Thao tác dễ dàng chắc chắn",
            kind="FLOW_AI",
            narrator_text="Hoàn thiện chắc chắn, thao tác sử dụng dễ dàng chỉ trong vài giây, cực kỳ tiện lợi.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Chắc chắn - Dễ sử dụng",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using and demonstrating the features of {clean_title}. "
                f"Smooth confident hand movement, premium commercial B-roll lighting, shallow depth of field. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Tiện ích thực tế đời thường",
            kind="FLOW_AI",
            narrator_text=feat1_desc,
            overlay_title=feat1_title,
            overlay_subtitle="Tiện lợi tối đa",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young Vietnamese person using {clean_title} in daily workflow, "
                f"appreciative nod of satisfaction, smooth productive vibe. Calm expression, mouth closed, no speaking, no dialogue. Aesthetic modern workspace. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Cuộc sống thảnh thơi hơn",
            kind="FLOW_AI",
            narrator_text="Một món đồ nhỏ nhưng giúp cuộc sống tiện nghi và thảnh thơi hơn rất nhiều!",
            overlay_title="TIỆN NGHI THẢNH THƠI",
            overlay_subtitle="Tiện ích mỗi ngày",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Dynamic lifestyle shot of hands packing {clean_title} conveniently into everyday carry bag, ready for travel or work. "
                f"Clean modern aesthetic, soft natural lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
            ),
        ),
    ]


def _build_problem_solution_scenes(
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
    persona = _get_character_persona(category)

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
        is_storage = any(k in clean_title.lower() for k in ["usb", "ổ đĩa", "flash drive", "thẻ nhớ", "ổ cứng", "ssd"])
        is_desk_setup = any(k in clean_title.lower() for k in ["khay", "giấu dây", "kẹp bàn", "kệ", "giá đỡ", "cáp", "đi dây"])
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
                    f"and give an energetic cheerful thumbs-up, looking excited for vacation. Stable realistic physics, crisp human gestures, natural speed, not floaty. Mouth closed, no speaking. NO text overlays."
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


def _build_lifestyle_edc_scenes(
    category: str,
    clean_title: str,
    feat1_title: str,
    feat1_desc: str,
    feat2_title: str,
    feat2_desc: str,
    custom_idea: Optional[str] = None,
) -> List[SceneDefinition]:
    """Generate 4 Aesthetic Lifestyle / Everyday Carry AI scenes tailored to category."""
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    return [
        SceneDefinition(
            id=1,
            name="Hook - Món đồ bất ly thân",
            kind="FLOW_AI",
            narrator_text=f"Một món đồ nhỏ gọn nhưng cực kỳ đắc lực mà bạn nhất định phải có bên mình mỗi ngày! Khám phá ngay {clean_title} nhé!",
            overlay_title="MÓN ĐỒ BẤT LY THÂN",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young stylish Vietnamese creator packing everyday essentials into a minimalist leather bag at a sunlit aesthetic coffee shop. "
                f"Holding up {clean_title} with an appreciative smile. Mouth closed, no speaking, relaxed aesthetic lifestyle{idea_ctx}, 35mm lens. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Hoàn thiện tinh tế bền bỉ",
            kind="FLOW_AI",
            narrator_text="Chất liệu cao cấp chống va đập, chống hao mòn hoàn hảo. Thiết kế thông minh, luôn sẵn sàng khi bạn cần.",
            overlay_title="HOÀN THIỆN TINH TẾ",
            overlay_subtitle="Chất liệu cao cấp - Bền bỉ",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using {clean_title} with smooth confident motions. "
                f"Crisp texture reflections, natural sunlight, premium commercial details. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Đồng hành mọi khoảnh khắc",
            kind="FLOW_AI",
            narrator_text=f"{feat1_desc}. Đáp ứng hoàn hảo mọi nhu cầu, mang lại sự tiện nghi và tự tin tuyệt đối.",
            overlay_title=feat1_title,
            overlay_subtitle="Tiện lợi vượt trội",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Creator happily enjoying their daily routine at an outdoor terrace with a scenic view, using {clean_title} with a peaceful focused expression. "
                f"Mouth closed, no speaking. Soft natural golden hour light. NO text overlays."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Tự do & Năng động",
            kind="FLOW_AI",
            narrator_text="Gọn gàng trong lòng bàn tay, người bạn đồng hành hoàn hảo cho phong cách sống hiện đại và năng động!",
            overlay_title="ĐỒNG HÀNH MỌI NƠI",
            overlay_subtitle="Gọn nhẹ - An tâm tuyệt đối",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Person zipping up their bag, holding {clean_title} gleaming in ambient light, walking away with upbeat dynamic energy. "
                f"Mouth closed, natural lighting, modern aesthetic. NO text overlays."
            ),
        ),
    ]


def _build_faceless_pov_scenes(
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

    if category == "TECH_GADGETS":
        is_footrest = any(k in clean_title.lower() for k in ["kê chân", "ke chan", "footrest"])
        is_desk_setup = any(k in clean_title.lower() for k in ["khay", "giấu dây", "kẹp bàn", "kệ", "giá đỡ", "cáp", "đi dây"])

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
                    f"Hands smoothly fold the suitcase lid shut with a crisp satisfying click, then give a quick energetic thumbs-up over the closed luggage. "
                    f"Fast snappy motions, natural commercial ad speed, stable realistic physics. "
                    f"Completely faceless, NO human face, hands only. NO text overlays."
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
                f"Hand giving a subtle gesture of satisfaction, neck-down angle. Warm natural light. NO face. NO text overlays."
            ),
        ),
    ]


def _build_cta_scene(
    scene_id: int,
    cta_mode: str,
    category: str,
    style: str,
    clean_title: str,
    channel_name: Optional[str] = None,
    is_local: bool = False,
    has_video: bool = False,
) -> Optional[SceneDefinition]:
    """Build CTA / Outro scene tailored to platform and style."""
    is_faceless = style in ("faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov")
    kind = "FLOW_AI" if not is_local else ("REAL_FOOTAGE" if has_video else "IMAGE_SLIDE")

    if cta_mode == "follow":
        persona = _get_character_persona(category)
        overlay_t = f"FOLLOW {channel_name.upper()}" if channel_name else "BẤM FOLLOW KÊNH"
        if category == "FASHION_APPAREL":
            cta_txt = "Bạn nào cũng mê phong cách chỉn chu, gọn gàng thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"
        elif category == "BEAUTY_SKINCARE":
            cta_txt = "Bạn nào cũng mê chăm sóc bản thân, làm đẹp thảnh thơi thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"
        else:
            cta_txt = "Bạn nào cũng mê không gian ngăn nắp, thảnh thơi thì bấm follow kênh mình để gom thêm nhiều mẹo hay ho mỗi ngày nhé!"

        if is_faceless:
            follow_prompt = (
                "Vertical 9:16 RAW cinematic video. First-person POV looking down at clean aesthetic table, hand giving a subtle thumbs-up or peace sign. "
                "Warm modern ambient lighting. NO human face, NO head in frame, hands only. NO text overlays."
            )
        else:
            follow_prompt = (
                f"Vertical 9:16 RAW cinematic video. Featuring {persona['cont']}, giving a gentle wave and warm genuine smile to camera in a modern tidy aesthetic room. "
                f"Natural modern aesthetic lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
            )

        return SceneDefinition(
            id=scene_id,
            name="Outro - Kêu gọi Follow Kênh",
            kind=kind,
            narrator_text=cta_txt,
            overlay_title=overlay_t,
            overlay_subtitle="Mẹo hay & Tiện ích mỗi ngày",
            image_index=0,
            prompt=follow_prompt,
        )

    elif cta_mode == "shopee":
        if is_faceless:
            shopee_prompt = (
                "Vertical 9:16 RAW cinematic video. Macro POV shot looking down at product neatly displayed on desk, hand pointing down toward comments. "
                "Bright commercial aesthetic lighting. NO human face, hands only. NO text overlays."
            )
        else:
            shopee_prompt = (
                "Vertical 9:16 RAW cinematic video. Happy young Vietnamese creator smiling warmly at the camera, raising a cheerful thumbs-up. "
                "Mouth closed, no speaking, bright vibrant ambient lighting. NO text overlays."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động Shopee (CTA)",
            kind=kind,
            narrator_text="Món này tiện lợi thực sự! Mình để link chính hãng dưới phần bình luận cho các bạn tham khảo nhé!",
            overlay_title="LINK Ở BÌNH LUẬN GHIM",
            overlay_subtitle="Chính hãng - Giá cực tốt",
            image_index=0,
            prompt=shopee_prompt,
        )

    elif cta_mode in ("tiktok", "tiktok_shop"):
        if is_faceless:
            tiktok_prompt = (
                "Vertical 9:16 RAW cinematic video. Macro POV shot looking down at product, hand gesturing toward the lower left corner. "
                "Bright commercial aesthetic lighting. NO human face, hands only. NO text overlays."
            )
        else:
            tiktok_prompt = (
                "Vertical 9:16 RAW cinematic video. Young Vietnamese creator pointing enthusiastically toward lower-left corner with friendly smile. "
                "Mouth closed, no speaking, bright vibrant lighting. NO text overlays."
            )

        return SceneDefinition(
            id=scene_id,
            name="Kêu gọi hành động TikTok Shop (CTA)",
            kind=kind,
            narrator_text="Món này tiện lợi thực sự! Các bạn bấm ngay vào giỏ hàng màu vàng góc trái để nhận ưu đãi hôm nay nhé!",
            overlay_title="GIỎ HÀNG GÓC TRÁI",
            overlay_subtitle="Bấm nhận ưu đãi hôm nay",
            image_index=0,
            prompt=tiktok_prompt,
        )

    return None
