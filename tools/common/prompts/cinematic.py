"""Cinematic Flow AI scenes (used by every platform's ``flow_cinematic`` style).
"""
from typing import List, Optional

from tools.common.archetypes import ProductArchetype, title_matches
from tools.common.models import SceneDefinition
from tools.common.prompts.personas import character_persona
from tools.common.prompts.realism import feature_line, product_noun, spoken_name


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
    noun = product_noun(category, clean_title)
    short_name = spoken_name(clean_title)

    if category == "BEAUTY_SKINCARE":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi lo da khô mốc mỗi sáng",
                kind="FLOW_AI",
                narrator_text=f"Sáng nào trang điểm da cũng khô, mốc lên từng mảng, nhìn mà nản luôn á. Ai bị vậy thì coi {short_name} này nè.",
                overlay_title="DA KHÔ MỐC MỖI SÁNG?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"{persona['intro']} sits at a cluttered bedroom vanity by the window, a few makeup items and a hair tie lying around. "
                    f"She picks up a {noun} in plain unbranded packaging, turns it once in her fingers to look at it, then glances at her reflection{idea_ctx}. "
                    f"Medium shot from beside the mirror, soft morning window light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Thao tác dưỡng da mỏng nhẹ",
                kind="FLOW_AI",
                narrator_text="Chất kem mỏng lắm, vỗ nhẹ cái là thấm, không bết rít gì hết. Mát mát, ẩm ẩm, thích ghê.",
                overlay_title="THẤM NHANH KHÔNG BẾT",
                overlay_subtitle="Mỏng nhẹ - Mát lạnh",
                image_index=0,
                prompt=(
                    "Close-up of a woman's hands, no face: she squeezes two drops of clear serum from a plain unbranded dropper bottle onto her fingertips, "
                    "then dabs them onto the back of her other hand and spreads them in small circles. Real skin with fine lines and pores, the liquid catches the window light. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Hiệu quả căng bóng mịn màng",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Da căng bóng tự nhiên cả ngày, không lo xuống tông."),
                overlay_title=feat1_title,
                overlay_subtitle="Căng bóng rạng ngời",
                image_index=0,
                prompt=(
                    f"{persona['cont']} leans toward the bathroom mirror and lightly presses her fingertips along her cheek, checking how her skin feels, then looks away with a small relaxed smile. "
                    f"Real bathroom with a towel on the rail and a toothbrush cup, warm ceiling bulb light, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Nhỏ gọn tự tin mỗi ngày",
                kind="FLOW_AI",
                narrator_text="Chai nhỏ xíu, bỏ túi xách đi làm đi chơi gì cũng tiện. Đơn giản vậy thôi mà tự tin hơn hẳn.",
                overlay_title="GỌN NHẸ TỰ TIN",
                overlay_subtitle="Đồng hành mỗi ngày",
                image_index=0,
                prompt=(
                    f"{persona['cont']} slips the {noun} into the inner pocket of an open canvas tote bag on the bed and pulls the zip closed. "
                    f"Lived-in bedroom with an unmade blanket, daylight from the window, not talking."
                ),
            ),
        ]

    elif category == "KITCHEN_HOME":
        # Narration and visuals must describe the same cookware: frying an egg in a pot reads as AI.
        # Narration is written as speech (short clauses, particles), not ad copy; the listing title
        # is cut to its first words because nobody says a full Shopee title out loud.
        if noun == "frying pan":
            hook_txt = "Chiên cái trứng thôi mà chảo cứ dính, cạy muốn rách luôn á. Ai bị vậy thì coi cái này nè."
            hero_txt = f"Đổi qua {short_name} này thử coi, trứng trượt một phát là ra. Chảo nóng nhanh, chiên rán nhàn hẳn."
            hero_title, hero_sub = "CHIÊN XÀO SIÊU MƯỢT", "Bắt nhiệt nhanh - Không dính"
            hero_action = "a spatula turns a frying egg while oil bubbles softly at the edges and light steam rises"
            meal = "slides a fried egg onto a plate of rice at a small kitchen table, then sits down to eat"
            clean_txt = "Nấu xong lấy tờ giấy lau một cái là sạch, khỏi chà khỏi cọ. Nhàn ghê luôn!"
            clean_action = "a hand wipes the inside of the frying pan once with a folded paper towel and the thin film of oil comes off"
        elif noun == "cooking pot":
            hook_txt = "Nấu nồi canh thôi mà đáy cứ cháy, cứ dính, rửa muốn xỉu luôn á. Ai bị vậy thì coi cái này nè."
            hero_txt = f"Đổi qua {short_name} này thử coi. Nấu canh, kho thịt gì cũng chín đều, mà đáy không dính chút nào."
            hero_title, hero_sub = "NẤU KHO KHÔNG BÁM DÍNH", "Bắt nhiệt nhanh - Chín đều"
            hero_action = "a ladle slowly stirs a simmering vegetable soup in the pot while small bubbles rise and steam drifts up"
            meal = "ladles soup from the pot into a small bowl at the kitchen table, then sits down to eat with rice"
            clean_txt = "Nấu xong rửa nhẹ bằng miếng mút là sạch trơn, khỏi chà khỏi cọ. Nhàn ghê luôn!"
            clean_action = "a hand rinses the empty cooking pot under the tap and wipes the inside once with a soft yellow sponge, and nothing is stuck to the bottom"
        else:
            hook_txt = "Vô bếp mà đồ đạc lỉnh kỉnh, nấu một bữa mất cả tiếng. Ai bị vậy thì coi cái này nè."
            hero_txt = f"Đổi qua {short_name} này thử coi, sơ chế hay nấu nướng gì cũng nhanh gọn hơn hẳn."
            hero_title, hero_sub = "NẤU NƯỚNG NHANH GỌN", "Dễ dùng - Tiện lợi"
            hero_action = f"hands use the {noun} once, slowly and simply, to prepare fresh vegetables on a worn wooden cutting board"
            meal = "sets a plate of home-cooked food on a small kitchen table, then sits down to eat"
            clean_txt = "Dùng xong rửa nhẹ là sạch, khỏi chà khỏi cọ. Nhàn ghê luôn!"
            clean_action = f"a hand rinses the {noun} under the tap and wipes it once with a soft yellow sponge"
        return [
            SceneDefinition(
                id=1,
                name="Hook - Nỗi ngán ngẩm chùi rửa bếp núc",
                kind="FLOW_AI",
                narrator_text=hook_txt,
                overlay_title="CHÙI RỬA PHÁT NGÁN?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"{persona['intro']} stands at an ordinary home kitchen counter with a dish rack and a few sauce bottles in the background. "
                    f"She lifts the {noun} off the counter, feels its weight in one hand and gives a small approving nod{idea_ctx}. "
                    f"Medium shot, daylight from a small window mixed with the ceiling light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Thao tác nấu nướng mượt mà",
                kind="FLOW_AI",
                narrator_text=hero_txt,
                overlay_title=hero_title,
                overlay_subtitle=hero_sub,
                image_index=0,
                prompt=(
                    f"Close-up of hands cooking with the {noun} at a home gas stove, no face: {hero_action}. "
                    f"A few drops of oil on the stovetop, a bowl of chopped scallions nearby. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Món ngon tròn vị đầm ấm",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Nấu cho cả nhà ăn cũng yên tâm hơn."),
                overlay_title=feat1_title,
                overlay_subtitle="Chín đều thơm ngon",
                image_index=0,
                prompt=(
                    f"{persona['cont']} {meal}. "
                    f"Ordinary plates, a glass of water and chopsticks on the table, ceiling light, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Vệ sinh nhẹ nhàng thảnh thơi",
                kind="FLOW_AI",
                narrator_text=clean_txt,
                overlay_title="RỬA NHẸ LÀ SẠCH BONG",
                overlay_subtitle="Nấu nướng thảnh thơi",
                image_index=0,
                prompt=(
                    f"Close-up at the kitchen sink, no face: {clean_action}. "
                    f"An unlabeled dish soap bottle and a few dishes in the rack. Hands only."
                ),
            ),
        ]

    elif category == "FASHION_APPAREL":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Đau đầu chọn đồ mỗi sáng",
                kind="FLOW_AI",
                narrator_text=f"Sáng nào đứng trước tủ đồ cũng không biết mặc gì cho gọn, cho đẹp. Coi thử {short_name} này nè.",
                overlay_title="ĐAU ĐẦU CHỌN ĐỒ?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"{persona['intro']} stands in her bedroom in front of an open wardrobe with clothes on hangers, holding the {noun} up against herself and looking down at it{idea_ctx}. "
                    f"Medium shot, daylight from the window, a chair with clothes draped over it behind her, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Vải mềm mát co giãn tốt",
                kind="FLOW_AI",
                narrator_text="Vải mềm, sờ mát tay, co giãn thoải mái. Đường may kỹ lắm, giặt máy cũng không nhão.",
                overlay_title="VẢI MÁT CO GIÃN TỐT",
                overlay_subtitle="Đường may tỉ mỉ - Bền đẹp",
                image_index=0,
                prompt=(
                    f"Close-up of hands, no face: fingers pinch and stretch the fabric of the {noun} laid on a bed, then let go so it springs back. "
                    f"Visible weave, a loose thread, slight creases in the cloth, daylight from the side. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Lên form vừa vặn tôn dáng",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Mặc đi làm hay đi cà phê cả ngày vẫn thoải mái."),
                overlay_title=feat1_title,
                overlay_subtitle="Thoải mái vận động cả ngày",
                image_index=0,
                prompt=(
                    f"{persona['cont']}, now wearing the {noun}, turns slightly in front of a full-length mirror in a small bedroom and smooths the fabric with one hand. "
                    f"Filmed from beside the mirror, ordinary room light, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Dễ phối đồ tự tin dạo phố",
                kind="FLOW_AI",
                narrator_text="Phối với quần jean hay chân váy đều xinh hết. Mặc vô tự tin hẳn luôn.",
                overlay_title="DỄ PHỐI MỌI OUTFIT",
                overlay_subtitle="Đi làm, dạo phố cực xinh",
                image_index=0,
                prompt=(
                    f"{persona['cont']}, wearing the {noun}, walks along a busy Vietnamese sidewalk past parked motorbikes and a street food stall, filmed by a friend walking a few steps ahead. "
                    f"Overcast daylight, natural walking pace, not talking."
                ),
            ),
        ]

    elif category == "HEALTH_FITNESS":
        return [
            SceneDefinition(
                id=1,
                name="Hook - Cổ vai gáy cứng đờ ê ẩm",
                kind="FLOW_AI",
                narrator_text="Ngồi máy tính cả ngày, cổ vai gáy cứng đơ, mỏi muốn rã ra luôn. Ai bị vậy thì coi cái này nè.",
                overlay_title="CỔ VAI GÁY CỨNG ĐỜ?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"{persona['intro']} sits on the edge of a sofa in a small living room, rolls one stiff shoulder and rubs the back of his neck, then reaches for the {noun} on the coffee table{idea_ctx}. "
                    f"Medium shot, evening lamp light, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Lực rung đầm chắc êm ái",
                kind="FLOW_AI",
                narrator_text=f"Đổi qua {short_name} này thử coi. Rung đầm tay mà chạy êm ru, đè vô chỗ mỏi là đã liền.",
                overlay_title="XUNG LỰC ĐẦM ÊM",
                overlay_subtitle="Giảm đau mỏi sâu tức thì",
                image_index=0,
                prompt=(
                    f"Close-up of a hand pressing the {noun} against the muscle of the other forearm, no face; the skin ripples slightly with the vibration. "
                    f"Real arm hair and skin texture, sofa fabric in the background. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Người nhẹ bẫng sảng khoái",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Bớt mỏi hẳn, người nhẹ nhõm ra liền."),
                overlay_title=feat1_title,
                overlay_subtitle="Thư giãn sâu từng tế bào",
                image_index=0,
                prompt=(
                    f"{persona['cont']} leans back on the sofa, lets his shoulders drop and breathes out slowly with his eyes half closed. "
                    f"Living room with a few things on the coffee table, warm lamp light, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Bỏ túi tiện lợi mọi nơi",
                kind="FLOW_AI",
                narrator_text="Máy nhỏ gọn, bỏ túi mang lên công ty hay đi chơi đều tiện. Tan ca mỏi là lấy ra dùng liền.",
                overlay_title="NHỎ GỌN TIỆN LỢI",
                overlay_subtitle="Chăm sóc cơ thể mỗi ngày",
                image_index=0,
                prompt=(
                    f"{persona['cont']} puts the {noun} into a gym backpack on the floor next to a water bottle and zips the bag closed. "
                    f"Small apartment hallway with shoes by the door, daylight, not talking."
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
                    narrator_text="Đang làm gấp mà laptop báo đầy bộ nhớ, đỏ lòm luôn, ức chế thiệt chớ.",
                    overlay_title="BÁO ĐỘNG ĐẦY Ổ CỨNG?",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"{persona['intro']} sits at a wooden desk with an open laptop, a mug and a few cables around. "
                        f"He picks up the {noun} and looks at it between two fingers{idea_ctx}. Medium shot, daylight from the window, not talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Cắm là nhận ngay tức thì",
                    kind="FLOW_AI",
                    narrator_text=f"Cắm {short_name} này vô coi. Nhỏ xíu như cái móc khóa, cắm vô là nhận liền.",
                    overlay_title="CẮM VÀO NHẬN NGAY",
                    overlay_subtitle="Kim loại nguyên khối - Siêu bền",
                    image_index=0,
                    prompt=(
                        f"Close-up of a hand plugging the {noun} into the side USB port of a laptop on a wooden desk, no face; it takes a small push to seat it and a tiny LED on the drive starts blinking. "
                        f"Fingerprints on the laptop edge, a coffee ring on the desk. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Sao chép siêu tốc nhẹ cả đầu",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Chép video với tài liệu nặng vèo cái là xong."),
                    overlay_title=feat1_title,
                    overlay_subtitle="Tốc độ sao chép siêu tốc",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} types on the laptop with the {noun} plugged into the side port, glances at the screen and nods slightly. "
                        f"The screen faces away from the camera. Desk lamp and window light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Móc khóa an tâm mang theo mọi nơi",
                    kind="FLOW_AI",
                    narrator_text="Móc chung với chìa khóa hay balo, đi đâu cũng mang theo được, khỏi lo quên.",
                    overlay_title="MÓC KHÓA TIỆN LỢI",
                    overlay_subtitle="Gọn nhẹ - An tâm tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: a hand clips the {noun} onto a key ring with a few house keys and drops the bunch into a jacket pocket. Hands only."
                    ),
                ),
            ]
        else:
            return [
                SceneDefinition(
                    id=1,
                    name="Hook - Nâng cấp góc làm việc gọn gàng",
                    kind="FLOW_AI",
                    narrator_text=f"Góc làm việc mà thiếu món này là thấy thiếu thiếu liền. Coi thử {short_name} này nè.",
                    overlay_title="GÓC SETUP TIỆN ÍCH",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"{persona['intro']} sits at a home desk with a laptop, a mug and a tangle of cables, and lifts the {noun} out of its plain opened box{idea_ctx}. "
                        f"Medium shot, window light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Kết nối nhanh nhạy chắc chắn",
                    kind="FLOW_AI",
                    narrator_text="Cầm lên thấy chắc tay, kết nối nhanh, nhạy. Để trên bàn nhìn gọn hẳn.",
                    overlay_title="KẾT NỐI NHANH NHẠY",
                    overlay_subtitle="Đầm chắc - Siêu mượt mà",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands on a wooden desk, no face: a hand switches on the {noun} with a single press and a small indicator light turns on. "
                        f"Dust specks and fingerprints visible on the surface. Hands only."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Thao tác mượt mà tập trung",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat1_title, feat1_desc, "Làm việc trơn tru, tập trung hơn hẳn."),
                    overlay_title=feat1_title,
                    overlay_subtitle="Hiệu năng vượt trội",
                    image_index=0,
                    prompt=(
                        f"{persona['cont']} uses the {noun} at his desk while working on the laptop, screen turned away from the camera, then leans back slightly. "
                        f"Desk lamp and window light, not talking."
                    ),
                ),
                SceneDefinition(
                    id=4,
                    name="Lifestyle - Nhỏ gọn trơn tru mỗi ngày",
                    kind="FLOW_AI",
                    narrator_text=feature_line(feat2_title, feat2_desc, "Nhỏ gọn mà xài được việc lắm luôn."),
                    overlay_title="TỐI ƯU CÔNG VIỆC",
                    overlay_subtitle="Tiện lợi tối đa",
                    image_index=0,
                    prompt=(
                        f"Close-up of hands, no face: a hand puts the {noun} into the front pocket of a backpack resting on a chair and pulls the zip closed. Hands only."
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
                narrator_text=f"Soạn đồ đi du lịch mà chăn mền, áo phao cồng kềnh, nhét hoài không vô. Coi thử {short_name} này nè.",
                overlay_title="HÀNH LÝ GỌN GÀNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"{persona['intro']} stands in a lived-in bedroom next to an open suitcase on the bed with a bulky pile of puffer jackets and a blanket. "
                    f"She holds up an empty {noun} and gives it a quick shake to open it{idea_ctx}. Medium shot, daylight from the window, normal speed, not talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Hút xẹp 80% chỉ trong 10 giây",
                kind="FLOW_AI",
                narrator_text="Kéo khóa zip lại, hút hơi qua cái van, túi xẹp lép xuống còn có chút xíu. Đỡ được cả đống chỗ luôn.",
                overlay_title="GIẢM 80% DIỆN TÍCH",
                overlay_subtitle="Khóa zip đôi - Kín tuyệt đối",
                image_index=0,
                prompt=(
                    f"Top-down close-up of hands on a bed, no face: a hand holds a small pump nozzle on the round valve of a {noun} stuffed with a puffer jacket; "
                    f"air hisses out and the bag slowly shrinks and wrinkles tightly around the jacket over a few seconds. Creased bedsheet, normal speed. Hands only."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Xếp vừa in, rộng thêm nửa vali",
                kind="FLOW_AI",
                narrator_text=feature_line(feat1_title, feat1_desc, "Đống đồ cồng kềnh gom gọn một góc, vali còn dư cả nửa."),
                overlay_title="VALI RỘNG THÊM 50%",
                overlay_subtitle="Chất liệu dẻo dai - Tái sử dụng",
                image_index=0,
                prompt=(
                    f"{persona['cont']} lifts a flattened, wrinkled bag of clothes with both hands and lays it into the open suitcase, where it fills only one side. "
                    f"Medium shot, bedroom daylight, normal speed, not talking."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Kéo khóa nhẹ tênh, tự tin lên đường",
                kind="FLOW_AI",
                narrator_text=feature_line(feat2_title, feat2_desc, "Kéo khóa vali nhẹ tênh, đi chơi thảnh thơi."),
                overlay_title="TỰ TIN LÊN ĐƯỜNG",
                overlay_subtitle="Bảo vệ chống ẩm mốc",
                image_index=0,
                prompt=(
                    f"{persona['cont']} zips the packed suitcase closed around the last corner and stands it upright on its wheels beside the bed. "
                    f"Medium shot, bedroom daylight, normal speed, not talking."
                ),
            ),
        ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Trải nghiệm món đồ bất ngờ",
            kind="FLOW_AI",
            narrator_text=f"Món này nhìn đơn giản vậy thôi mà xài tiện dữ lắm. Coi thử {short_name} này nè.",
            overlay_title="BẤT NGỜ TIỆN DỤNG",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"{persona['intro']} sits on the sofa at home with the {noun} in its plain opened box on her lap, lifts it out and looks it over{idea_ctx}. "
                f"Medium shot, living room daylight, a few things on the coffee table, not talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Thao tác dễ dàng chắc chắn",
            kind="FLOW_AI",
            narrator_text="Làm chắc chắn, dùng cũng dễ, vài giây là xong, tiện ghê.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Chắc chắn - Dễ sử dụng",
            image_index=0,
            prompt=(
                f"Close-up of hands at a home table, no face: hands use the {noun} once, slowly and simply, the way it is normally used. "
                f"Real fingerprints and small scratches on the table, daylight from the side. Hands only."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Tiện ích thực tế đời thường",
            kind="FLOW_AI",
            narrator_text=feature_line(feat1_title, feat1_desc, "Dùng hằng ngày tiện lắm luôn."),
            overlay_title=feat1_title,
            overlay_subtitle="Tiện lợi tối đa",
            image_index=0,
            prompt=(
                f"{persona['cont']} uses the {noun} during an ordinary moment at home, then sets it down on the table. Lived-in room, daylight, not talking."
            ),
        ),
        SceneDefinition(
            id=4,
            name="Lifestyle - Cuộc sống thảnh thơi hơn",
            kind="FLOW_AI",
            narrator_text="Món nhỏ thôi mà nhà cửa gọn gàng, mỗi ngày nhàn hơn hẳn.",
            overlay_title="TIỆN NGHI THẢNH THƠI",
            overlay_subtitle="Tiện ích mỗi ngày",
            image_index=0,
            prompt=(
                f"Close-up of hands, no face: a hand puts the {noun} into a canvas tote bag hanging on a chair. Hands only."
            ),
        ),
    ]


__all__ = ["build_flow_cinematic_scenes"]
