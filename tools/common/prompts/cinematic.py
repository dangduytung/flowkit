"""Cinematic Flow AI scenes (used by every platform's ``flow_cinematic`` style).
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, title_matches
from tools.common.models import SceneDefinition
from tools.common.prompts.personas import character_persona


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
    """Generate 4 cinematic AI scenes tailored to the product's physical category."""
    idea_ctx = f" ({custom_idea})" if custom_idea else ""
    persona = character_persona(category)

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
                    "Vertical 9:16 RAW cinematic video. Macro close-up shot of gentle hands dispensing smooth silky drops of the product onto skin, gently patting and blending it smoothly. "
                    "Dewy glowing skin reflection, water droplet moisture, crisp texture commercial B-roll lighting, 4K resolution. NO text overlays, NO face."
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
                    "Vertical 9:16 RAW cinematic video. The young woman looks at her reflection in the mirror with pure satisfaction, gently touching her glowing smooth cheek. "
                    "Natural radiant dewy complexion, subtle satisfied smile, mouth closed, no speaking. Soft warm indoor vanity lighting. NO text overlays."
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
                    "Vertical 9:16 RAW cinematic video. Woman slipping the sleek cosmetic bottle into her stylish leather handbag, standing up and smiling warmly before heading out. "
                    "Calm confident posture, mouth closed, no speaking, vibrant natural aesthetic. NO text overlays."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi ngán ngẩm chùi rửa bếp núc",
                kind="FLOW_AI",
                narrator_text="Ai nấu ăn mà ghét nhất cảnh chảo dính chặt, chùi rửa cực hình thì xem ngay cái này nha!",
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
                    "Vertical 9:16 RAW cinematic video. Plating a mouth-watering delicious hot meal onto a ceramic dish, creator leaning back with a genuine satisfied smile. "
                    "Mouth closed, no speaking, cozy warm home ambiance, cinematic lighting. NO text overlays."
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
                    "Vertical 9:16 RAW cinematic video. Person checking their look in a full-length mirror, adjusting outfit naturally with an appreciative smile of confidence. "
                    "Flattering fit, modern silhouette, mouth closed, no speaking. Chic indoor aesthetic. NO text overlays."
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
                    "Vertical 9:16 RAW cinematic video. The model walking confidently down a trendy sunlit city street or outdoor cafe, with natural poise and chic energy. "
                    "Golden hour sunlight, shallow depth of field. Mouth closed, no speaking. NO text overlays."
                ),
            ),
        ]

    elif category == "HEALTH_FITNESS":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Cổ vai gáy cứng đờ ê ẩm",
                kind="FLOW_AI",
                narrator_text="Ngồi làm việc cả ngày, cổ vai gáy cứng đờ ê ẩm phát mệt đúng không? Mình chỉ cho cách này nha!",
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
                    "Vertical 9:16 RAW cinematic video. Person leaning back on comfortable mat, feeling tension melt away, taking a deep breath of relief with a peaceful smile. "
                    "Mouth closed, no speaking, calm zen lighting. NO text overlays."
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
        is_storage = title_matches(clean_title, ProductArchetype.STORAGE_DEVICE)
        if is_storage:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Ức chế vì đầy ổ cứng giữa deadline",
                    kind="FLOW_AI",
                    narrator_text="Laptop đang làm việc gấp mà cứ báo đầy bộ nhớ đỏ lòm, nhìn ức chế thật sự đúng không?",
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
                        "Vertical 9:16 RAW cinematic video. Person operating their tech setup with maximum efficiency, smiling approvingly at the smooth performance. "
                        "Calm focused expression, mouth closed, no speaking. Modern creative studio lighting. NO text overlays."
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
                    "Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up B-roll, 60fps crisp commercial lighting. "
                    "Hands briskly sliding a thick puffy down jacket into the transparent vacuum compression bag, swiftly running the sealing clip along the double-track yellow zip lock. "
                    "Hands attach the suction nozzle to the circular one-way silicon valve; the bag instantly deflates in a fast satisfying compression, flattening down into a thin, firm, solid slab. "
                    "Brisk snappy hand movements, fast-forward deflation effect, natural real-life speed, not floaty. NO face, hands only. NO text overlays."
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
                    f"They look directly at camera with a beaming, confident smile and relaxed nod, ready to travel. "
                    f"Crisp energetic movement, natural human speed, stable physics, not floaty. Mouth closed, no speaking. NO thumbs-up, NO distorted fingers. NO text overlays."
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


__all__ = ["build_flow_cinematic_scenes"]
