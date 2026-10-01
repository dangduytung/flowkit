"""Storyboard management: dynamically extracts features and generates scene scripts for ANY product."""
import json
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from tools.shopee_ad.config import DEFAULT_CHANNEL_NAME
from tools.shopee_ad.product_parser import ProductInfo

logger = logging.getLogger(__name__)


@dataclass
class SceneDefinition:
    id: int
    name: str
    kind: str  # "FLOW_AI", "PRODUCT_PHOTO", "REAL_FOOTAGE", or "IMAGE_SLIDE"
    narrator_text: str
    overlay_title: str
    overlay_subtitle: str
    real_start_sec: float = 0.0
    image_index: int = 0
    prompt: Optional[str] = None
    video_prompt: Optional[str] = None


def clean_product_title(raw_name: str) -> str:
    """
    Extract a concise, clean product name suitable for spoken audio and overlay titles.
    Removes spam tags, bracketed codes, repetitive capacity/size listings, and shop warranties.
    """
    name = re.sub(r"^(Tên sản phẩm:|\s*\[.*?\]|\s*\(.*?\))\s*", "", raw_name, flags=re.I).strip()
    # Strip common bracketed marketing noise like [Chính Hãng], (HOT), [Freeship Xtra]
    name = re.sub(r"\[.*?\]|\(.*?\)|\【.*?\】", " ", name)
    # Strip warranty/official store noise from end
    name = re.sub(r"[\-–—]\s*(?:bảo hành|chính hãng|full box|freeship|sẵn hàng|chất lượng).*", "", name, flags=re.I).strip()
    # Strip model code at the end like HPW-CM01
    name = re.sub(r"\s+[A-Z0-9]{2,}[\-\d]+[A-Z0-9]*$", "", name).strip()
    # Remove repetitive capacity listings (e.g. '2TB 1TB 128GB 64GB 32GB 16GB 8GB 4GB 1GB')
    name = re.sub(r"(?:\b\d+\s*(?:TB|GB|MB)\b[\s,/]*){2,}", " ", name, flags=re.I)
    # Remove repetitive size/volume listings (e.g. '50ml/100ml', 'Size S M L XL')
    name = re.sub(r"(?:\b\d+\s*(?:ml|g|kg)\b[\s,/]*){2,}", " ", name, flags=re.I)
    name = re.sub(r"(?:\b(?:size\s*)?[SMLX]+\b[\s,/]*){3,}", " ", name, flags=re.I)
    # Remove trailing duplicate 'usb 2.0', 'usb 3.0' if 'usb' already appears earlier
    if re.search(r"\busb\b", name[:10], flags=re.I):
        name = re.sub(r"\s+usb\s*[\d\.]*$", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()
    parts = re.split(r"[_|\-–—]", name)
    short = parts[0].strip()
    if len(short) < 14 and len(parts) > 1:
        short = f"{short} {parts[1].strip()}"
    return short[:38].strip()


def extract_product_features(description_text: str) -> List[Tuple[str, str]]:
    """
    Extract key selling points / features from Shopee description text.
    Returns list of (badge_title, full_sentence).
    """
    lines = [l.strip() for l in description_text.splitlines() if l.strip()]
    spec_blacklist = (
        "thông số", "kích thước", "trong hộp", "màu sắc", "xuất xứ",
        "lưu ý", "bảo hành", "cam kết", "hướng dẫn", "liên hệ", "vat", "hóa đơn",
        "tải trọng", "trọng lượng", "khối lượng", "chất liệu", "hastag", "link",
        "ghi chú", "chính sách",
    )

    # Pass 0: Prioritize lines under 'ĐẶC ĐIỂM NỔI BẬT' / 'TÍNH NĂNG NỔI BẬT' / 'ƯU ĐIỂM'
    in_feature_section = False
    candidates = []
    for l in lines:
        low = l.lower()
        if any(h in low for h in ["đặc điểm nổi bật", "tính năng nổi bật", "ưu điểm nổi bật", "công dụng nổi bật"]):
            in_feature_section = True
            continue
        if any(h in low for h in ["thông số kỹ thuật", "thông số", "hướng dẫn", "lưu ý", "chính sách", "cam kết"]):
            in_feature_section = False
            continue
        if in_feature_section:
            clean = re.sub(r"^[✅⭐👉🔹✔\-\*\•\d\.\)]+\s*", "", l).strip()
            if 12 <= len(clean) <= 100 and not any(clean.lower().startswith(b) for b in spec_blacklist):
                candidates.append(clean)

    # Pass 1: Prioritize lines with checkmarks or bullet symbols
    if len(candidates) < 2:
        for l in lines:
            if re.match(r"^[✅⭐👉🔹✔]\s*", l):
                clean = re.sub(r"^[✅⭐👉🔹✔\s]+", "", l).strip()
                if 12 <= len(clean) <= 100 and not any(clean.lower().startswith(b) for b in spec_blacklist):
                    candidates.append(clean)

    # Pass 2: Lines formatted as 'Title: Description' or bulleted with dash
    if len(candidates) < 2:
        for l in lines:
            if any(l.lower().startswith(p) for p in spec_blacklist) or l.startswith("---"):
                continue
            clean = re.sub(r"^[\-\*\•\d\.\)]+\s*", "", l).strip()
            if len(clean) < 14 or clean.startswith("#") or clean.startswith("http"):
                continue
            if ":" in clean:
                t, d = clean.split(":", 1)
                t, d = t.strip(), d.strip()
                if 3 <= len(t) <= 28 and len(d) >= 12 and not any(h in t.lower() for h in spec_blacklist):
                    candidates.append(f"{t}: {d}")

    # Format into (badge_title, sentence)
    results = []
    for b in candidates:
        if " - " in b:
            t, d = b.split(" - ", 1)
            t_clean = re.sub(r"[^\w\s\d]", "", t).strip().upper()[:22]
            results.append((t_clean, d.strip()))
        elif ":" in b:
            t, d = b.split(":", 1)
            t_clean = re.sub(r"[^\w\s\d]", "", t).strip().upper()[:22]
            results.append((t_clean, d.strip()))
        else:
            low_b = b.lower()
            if "gọn gàng" in low_b or "đi dây" in low_b:
                badge = "SẮP XẾP GỌN GÀNG"
            elif "nhôm" in low_b or "chắc chắn" in low_b:
                badge = "NHÔM NGUYÊN KHỐI"
            elif "kẹp bàn" in low_b or "lắp đặt" in low_b:
                badge = "LẮP ĐẶT ĐƠN GIẢN"
            elif "tương thích" in low_b:
                badge = "TƯƠNG THÍCH ĐA NĂNG"
            else:
                words = b.split()
                badge = " ".join(words[:3]).upper()[:20]
                badge = re.sub(r"[^\w\s\d]", "", badge).strip()
            results.append((badge or "TÍNH NĂNG NỔI BẬT", b))

        if len(results) >= 3:
            break

    return results


def detect_product_category(name: str, description_text: str = "") -> str:
    """
    Intelligently classify ANY Shopee product into one of 6 core commercial categories.
    Uses word boundaries to prevent substring collisions (e.g. 'bàn làm việc' vs 'bàn là').
    """
    text = f"{name} {description_text}".lower()

    def _matches(keywords: list[str]) -> bool:
        for kw in keywords:
            pattern = r"(?:\b|\s|^)" + re.escape(kw) + r"(?:\b|\s|$)"
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    # 1. Beauty & Skincare
    beauty_kw = [
        "son", "son môi", "lipstick", "lip tint", "son dưỡng", "serum", "kem dưỡng",
        "kem trị", "kem nám", "kem chống nắng", "sunscreen", "toner", "nước hoa hồng",
        "nước hoa", "perfume", "sữa rửa mặt", "tẩy trang", "cleanser", "mặt nạ",
        "sheet mask", "dầu gội", "dầu xả", "ủ tóc", "dưỡng tóc", "máy sấy tóc",
        "máy uốn", "phấn phủ", "cushion", "mascara", "chì mày", "kẻ mắt", "trang điểm",
        "makeup", "phục hồi da", "cấp ẩm", "dưỡng trắng", "mịn môi", "skincare", "mỹ phẩm"
    ]
    if _matches(beauty_kw):
        return "BEAUTY_SKINCARE"

    # 2. Kitchen & Home Appliances
    kitchen_kw = [
        "chảo", "chảo chống dính", "nồi", "nồi chiên", "nồi cơm", "nồi áp suất",
        "bếp từ", "bếp ga", "bếp hồng ngoại", "dao bếp", "thớt", "máy xay",
        "máy ép", "máy làm sữa hạt", "ấm đun", "ấm siêu tốc", "bình giữ nhiệt",
        "cốc giữ nhiệt", "hộp cơm", "hộp giữ nhiệt", "máy hút bụi", "robot hút bụi",
        "cây lau nhà", "bàn ủi", "bàn là", "máy lọc không khí", "quạt tích điện",
        "quạt mini", "ga trải giường", "khăn tắm", "đồ gia dụng"
    ]
    if _matches(kitchen_kw):
        return "KITCHEN_HOME"

    # 3. Fashion & Apparel
    fashion_kw = [
        "áo thun", "áo phông", "áo sơ mi", "sơ mi", "áo khoác", "hoodie", "sweater",
        "cardigan", "polo", "croptop", "quần jean", "quần bò", "quần jogger",
        "quần âu", "quần short", "quần đùi", "váy", "đầm", "chân váy", "jumpsuit",
        "giày sneaker", "giày thể thao", "giày cao gót", "giày lười", "dép", "sandal",
        "túi xách", "túi đeo chéo", "ví da", "balo", "thắt lưng", "dây nịt",
        "kính mát", "kính râm", "nón", "mũ", "đồng hồ đeo tay", "trang sức", "vòng tay"
    ]
    if _matches(fashion_kw):
        return "FASHION_APPAREL"

    # 4. Health & Fitness
    health_kw = [
        "súng massage", "máy massage", "đệm massage", "gối massage", "thảm tập",
        "yoga", "tạ tay", "dây kháng lực", "con lăn tập bụng", "đai lưng tập gym",
        "bình shaker", "đau mỏi vai gáy", "thể thao", "fitness"
    ]
    if _matches(health_kw):
        return "HEALTH_FITNESS"

    # 5. Tech & Gadgets & Desk Setup
    tech_kw = [
        "usb", "ổ đĩa", "o dia", "flash drive", "thẻ nhớ", "thẻ sd", "micro sd",
        "ổ cứng", "ssd", "hdd", "box ổ cứng", "củ sạc", "cáp sạc", "dây sạc",
        "pin dự phòng", "sạc dự phòng", "sạc không dây", "tai nghe", "bluetooth",
        "earbuds", "headphone", "chuột không dây", "chuột gaming", "bàn phím",
        "loa bluetooth", "soundbar", "micro thu âm", "webcam", "giá đỡ điện thoại",
        "kẹp điện thoại", "gimbal", "tripod", "ốp lưng", "kính cường lực",
        "laptop", "máy tính", "ipad", "màn hình", "hub type c", "smartwatch",
        "khay giấu dây", "kẹp bàn", "quản lý cáp", "giá treo tai nghe", "kệ nâng màn hình",
        "đi dây", "desk setup", "hyperwork"
    ]
    if _matches(tech_kw):
        return "TECH_GADGETS"

    return "GENERAL_LIFESTYLE"


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
                name="Hook - Nâng niu làn da rạng rỡ",
                kind="FLOW_AI",
                narrator_text=f"Bí quyết để sở hữu làn da tươi tắn, căng mọng đầy sức sống mỗi ngày chính là đây! Khám phá ngay siêu phẩm {clean_title} cực hot này nhé!",
                overlay_title="BÍ QUYẾT DA TƯƠI TẮN",
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
                name="Hero Action - Thao tác dưỡng da chuyên sâu",
                kind="FLOW_AI",
                narrator_text="Kết cấu mỏng nhẹ, thẩm thấu tức thì vào từng tế bào da mà không hề gây bết dính. Cảm giác mát lành, sảng khoái và nuôi dưỡng làn da căng mướt.",
                overlay_title="THẨM THẤU TỨC THÌ",
                overlay_subtitle="Mỏng nhẹ - Không nhờn rít",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of gentle hands dispensing smooth silky drops of the product onto skin, gently patting and blending it smoothly. "
                    f"Dewy glowing skin reflection, water droplet moisture, crisp texture commercial B-roll lighting, 4K resolution. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Hiệu quả căng bóng vượt trội",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Làn da được cấp ẩm sâu, mềm mịn tự nhiên và rạng ngời dưới ánh nắng.",
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
                name="Lifestyle - Tự tin tỏa sáng mọi khoảnh khắc",
                kind="FLOW_AI",
                narrator_text="Thiết kế tinh tế, dễ dàng mang theo trong túi xách mỗi khi đi làm, đi chơi. Tự tin tỏa sáng với vẻ đẹp rạng rỡ suốt cả ngày dài!",
                overlay_title="TỰ TIN TỎA SÁNG",
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
                name="Hook - Giải pháp tiện nghi cho gian bếp",
                kind="FLOW_AI",
                narrator_text=f"Nấu ăn ngon và giữ cho gian bếp luôn tinh tươm chưa bao giờ dễ dàng đến thế! Cùng xem ngay siêu phẩm {clean_title} này nhé!",
                overlay_title="TIỆN NGHI GIAN BẾP",
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
                name="Hero Action - Thao tác nấu nướng/sử dụng mượt mà",
                kind="FLOW_AI",
                narrator_text="Hoàn thiện từ chất liệu cao cấp, khả năng chống dính và chịu nhiệt vượt trội. Sử dụng tiện lợi, giúp bạn tiết kiệm tối đa thời gian chuẩn bị.",
                overlay_title="CHỐNG DÍNH VƯỢT TRỘI",
                overlay_subtitle="Chất liệu cao cấp - Bền bỉ",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Dramatic macro close-up shot of hands cooking or operating {clean_title} on the countertop. "
                    f"Appetizing fresh colorful ingredients, gentle sizzle and steam, smooth effortless movement. Commercial food B-roll lighting, shallow depth of field. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Thành phẩm thơm ngon hấp dẫn",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Món ăn chín đều thơm lừng, giữ trọn vẹn dinh dưỡng cho bữa cơm gia đình thêm đầm ấm.",
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
                name="Lifestyle - Vệ sinh dễ dàng & Gọn gàng",
                kind="FLOW_AI",
                narrator_text="Đặc biệt là cực kỳ dễ vệ sinh, chỉ cần lau nhẹ là sáng bóng như mới. Món đồ gia dụng không thể thiếu cho một cuộc sống hiện đại và thảnh thơi!",
                overlay_title="VỆ SINH SIÊU DỄ DÀNG",
                overlay_subtitle="Nâng tầm không gian sống",
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
                name="Hook - Nâng tầm phong cách cá nhân",
                kind="FLOW_AI",
                narrator_text=f"Một thiết kế vừa trẻ trung, vừa tôn dáng mà bạn có thể dễ dàng diện trong mọi hoàn cảnh! Cùng khám phá {clean_title} cực chất này nhé!",
                overlay_title="PHONG CÁCH THỜI THƯỢNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Stylish young Vietnamese model standing in a modern boutique or sunlit loft, holding up {clean_title} with genuine admiration. "
                    f"Fashion editorial aesthetic, calm confident expression, mouth closed, no speaking{idea_ctx}. Soft cinematic lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Cận cảnh chất liệu cao cấp",
                kind="FLOW_AI",
                narrator_text="Chất vải mềm mịn thoáng khí, từng đường kim mũi chỉ được may chỉn chu và chắc chắn. Khả năng co giãn và giữ form dáng cực kỳ ấn tượng.",
                overlay_title="CHẤT LIỆU CAO CẤP",
                overlay_subtitle="Đường may tỉ mỉ - Chuẩn form",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands gently touching and stretching the premium fabric of {clean_title}. "
                    f"Crisp weave texture, flawless stitching, soft natural drape in dynamic light. Premium fashion commercial look. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Lên form tôn dáng tự nhiên",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Mặc vào nhẹ nhàng, thoải mái vận động suốt cả ngày dài mà không lo nhăn nhúm.",
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
                name="Lifestyle - Tự tin sải bước dạo phố",
                kind="FLOW_AI",
                narrator_text="Dễ dàng phối cùng nhiều trang phục khác nhau để đi làm hay dạo phố. Lựa chọn hoàn hảo để bạn luôn tự tin khẳng định phong cách riêng!",
                overlay_title="TỰ TIN SẢI BƯỚC",
                overlay_subtitle="Dễ phối đồ - Đi làm, dạo phố",
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
                name="Hook - Đánh tan đau mỏi & Thư giãn",
                kind="FLOW_AI",
                narrator_text=f"Sau một ngày dài làm việc căng thẳng, hãy để cơ thể bạn được thả lỏng và phục hồi năng lượng tức thì cùng {clean_title}!",
                overlay_title="PHỤC HỒI NĂNG LƯỢNG",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young Vietnamese person in athletic wear in a modern wellness room or gym, holding {clean_title} with an eager appreciative look. "
                    f"Calm focused expression, mouth closed, no speaking{idea_ctx}. Natural soft light, wellness vibe. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Thao tác tác động sâu vào cơ bắp",
                kind="FLOW_AI",
                narrator_text="Động cơ vận hành êm ái, xung lực mạnh mẽ len lỏi sâu vào từng nhóm cơ. Giải tỏa cơn nhức mỏi và kích thích tuần hoàn máu hiệu quả.",
                overlay_title="GIẢM ĐAU MỎI TỨC THÌ",
                overlay_subtitle="Xung lực mạnh mẽ - Êm ái",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands operating {clean_title}, smoothly demonstrating its powerful vibration and ergonomic grip. "
                    f"Crisp metallic accents, clean modern design, cinematic B-roll lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Cảm giác thư thái nhẹ nhõm",
                kind="FLOW_AI",
                narrator_text=f"{feat1_desc}. Cơ bắp được thả lỏng hoàn toàn, mang lại cảm giác nhẹ nhõm và sảng khoái tức thì.",
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
                name="Lifestyle - Gọn nhẹ đồng hành mọi nơi",
                kind="FLOW_AI",
                narrator_text="Thiết kế nhỏ gọn, dễ dàng bỏ vào túi tập hoặc vali mang theo khi đi công tác, du lịch. Trợ thủ sức khỏe đắc lực không thể thiếu của bạn!",
                overlay_title="ĐỒNG HÀNH MỌI NƠI",
                overlay_subtitle="Chăm sóc sức khỏe mỗi ngày",
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
                    name="Hook - Thiết kế kim loại sang trọng",
                    kind="FLOW_AI",
                    narrator_text=f"Bạn đang cần một thiết bị lưu trữ vừa nhỏ gọn bền bỉ, vừa sang xịn để mang theo mọi lúc mọi nơi? Xem ngay {clean_title} này nhé!",
                    overlay_title="NHỎ GỌN - SANG TRỌNG",
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
                    narrator_text="Vỏ hợp kim nguyên khối chống va đập, cắm vào là nhận ngay không cần cài đặt rườm rà. Tương thích mượt mà từ laptop, máy tính cho đến loa và tivi.",
                    overlay_title="CẮM LÀ NHẬN NGAY",
                    overlay_subtitle="Hợp kim nguyên khối - Chống va đập",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands plugging the metallic {clean_title} into the side USB port of a slim laptop on a clean wooden desk. "
                        f"Smooth precise insertion motion, tiny soft blue LED indicator illuminates. Crisp metallic reflection, commercial tech lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Truyền dữ liệu siêu tốc",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Tốc độ truyền tải nhanh chóng, sao chép trọn vẹn tài liệu và video nặng chỉ trong chớp mắt.",
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
                    name="Lifestyle - Móc khóa tiện lợi chống thất lạc",
                    kind="FLOW_AI",
                    narrator_text="Đặc biệt là móc treo tiện lợi, móc gọn cùng chìa khóa xe hay balo là không lo thất lạc. Thiết bị hoàn hảo đồng hành cùng bạn mỗi ngày!",
                    overlay_title="TIỆN LỢI MỌI HÀNH TRÌNH",
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
                    name="Hook - Trải nghiệm công nghệ thông minh",
                    kind="FLOW_AI",
                    narrator_text=f"Nâng cấp không gian làm việc, đưa trải nghiệm công nghệ lên tầm cao mới cùng {clean_title}!",
                    overlay_title="CÔNG NGHỆ ĐỈNH CAO",
                    overlay_subtitle=clean_title,
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Young Vietnamese tech enthusiast sitting at an aesthetic minimalist workspace, holding and admiring {clean_title}. "
                        f"Calm focused expression, subtle genuine smile, mouth closed, no speaking{idea_ctx}. Modern desk setup with warm ambient LED light. NO text overlays, NO talking."
                    ),
                ),
                SceneDefinition(
                    id=2,
                    name="Hero Action - Thao tác tương tác mượt mà",
                    kind="FLOW_AI",
                    narrator_text="Thiết kế hiện đại, kết nối tức thì với độ trễ cực thấp. Hoàn thiện tinh xảo, mang lại cảm giác cầm nắm và sử dụng vô cùng chắc chắn.",
                    overlay_title="KẾT NỐI TỨC THÌ",
                    overlay_subtitle="Độ trễ thấp - Siêu mượt mà",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands interacting with and activating {clean_title}. "
                        f"Satisfying click or indicator light glowing, sleek matte finish reflections, premium commercial tech lighting. NO text overlays, NO face."
                    ),
                ),
                SceneDefinition(
                    id=3,
                    name="Feature - Hiệu năng mạnh mẽ ổn định",
                    kind="FLOW_AI",
                    narrator_text=f"{feat1_desc}. Vận hành bền bỉ và ổn định, giúp mọi thao tác công việc và giải trí luôn mượt mà.",
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
                    name="Lifestyle - Gọn nhẹ đồng hành mỗi ngày",
                    kind="FLOW_AI",
                    narrator_text=f"{feat2_desc}. Sản phẩm nhỏ gọn, tiện lợi bỏ túi mang theo mọi lúc mọi nơi!",
                    overlay_title="ĐỒNG HÀNH MỖI NGÀY",
                    overlay_subtitle="Tiện lợi tối đa",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Hands sliding {clean_title} into everyday carry sling bag, standing up ready for meetings. "
                        f"Dynamic urban professional vibe, mouth closed, no speaking. NO text overlays."
                    ),
                ),
            ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Trải nghiệm thực tế trên tay",
            kind="FLOW_AI",
            narrator_text=f"Bạn đang tìm một sản phẩm thật ưng ý và tiện lợi cho nhu cầu hàng ngày? Xem ngay siêu phẩm {clean_title} cực hot này nhé!",
            overlay_title="BẠN ĐANG TÌM KIẾM?",
            overlay_subtitle=clean_title,
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Young Vietnamese person sitting at a modern desk, holding and admiring {clean_title} with great appreciation. "
                f"Subtle satisfied smile, calm focused expression, mouth closed, no speaking, no dialogue{idea_ctx}. Warm natural lighting, 35mm lens. NO text overlays, NO talking."
            ),
        ),
        SceneDefinition(
            id=2,
            name="Hero Action - Thao tác tương tác trực tiếp",
            kind="FLOW_AI",
            narrator_text=f"Thiết kế hiện đại, hoàn thiện tỉ mỉ từng chi tiết, mang lại trải nghiệm sử dụng vô cùng chắc chắn và thoải mái.",
            overlay_title=clean_title[:28].upper(),
            overlay_subtitle="Thiết kế cao cấp - Hoàn thiện tỉ mỉ",
            image_index=0,
            prompt=(
                f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands using and demonstrating the features of {clean_title}. "
                f"Smooth confident hand movement, premium commercial B-roll lighting, shallow depth of field. NO text overlays, NO face."
            ),
        ),
        SceneDefinition(
            id=3,
            name="Feature - Trải nghiệm tiện ích vượt trội",
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
            name="Lifestyle - Tiện dụng hàng ngày",
            kind="FLOW_AI",
            narrator_text=feat2_desc,
            overlay_title="LỰA CHỌN HOÀN HẢO",
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
                name="Hook - Nỗi lo da khô sạm trước sự kiện quan trọng",
                kind="FLOW_AI",
                narrator_text="Sắp đến buổi hẹn quan trọng mà làn da lại khô sạm, thiếu sức sống khiến bạn mất tự tin? Đừng lo lắng!",
                overlay_title="LÀN DA THIẾU SỨC SỐNG?",
                overlay_subtitle="Mất tự tin trước sự kiện?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young woman looking in vanity mirror with a concerned, slightly frustrated expression at her dry, dull facial skin. "
                    f"Mouth closed, no speaking, no dialogue{idea_ctx}. Cinematic moody lighting, shallow depth of field. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Cứu nguy làn da tức thì",
                kind="FLOW_AI",
                narrator_text=f"Đã có giải pháp phục hồi tức thì cùng {clean_title}! Tinh chất thẩm thấu sâu, cấp ẩm và nuôi dưỡng làn da căng mướt chỉ sau vài giọt.",
                overlay_title="CỨU CÁNH LÀN DA",
                overlay_subtitle="Cấp ẩm tức thì - Phục hồi sâu",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of gentle hands applying the silky formula onto cheek and forehead, soothing absorbing motion. "
                    f"Luminous moisture reflection, glowing aesthetic commercial lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Da căng bóng & Thở phào nhẹ nhõm",
                kind="FLOW_AI",
                narrator_text="Làn da lập tức bừng sáng, căng mọng mịn màng. Lớp nền tệp sâu và tự nhiên, mang lại cảm giác sảng khoái tuyệt vời.",
                overlay_title="CĂNG BÓNG MỊN MÀNG",
                overlay_subtitle="Bừng sáng vẻ đẹp rạng rỡ",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. The woman smiles radiant with sheer relief and joy, admiring her glowing dewy face in the sunlit mirror. "
                    f"Mouth closed, no speaking, warm golden lighting. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Tự tin tỏa sáng mọi sự kiện",
                kind="FLOW_AI",
                narrator_text="Bỏ túi mang theo mọi lúc mọi nơi để luôn sẵn sàng tỏa sáng với vẻ đẹp rạng ngời và cuốn hút nhất!",
                overlay_title="TỎA SÁNG MỌI LÚC",
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
                name="Hook - Nấu nướng dính khét & Mệt mỏi",
                kind="FLOW_AI",
                narrator_text="Đi làm về mệt mỏi mà chảo nấu thì dính khét, thức ăn cháy xém khiến việc bếp núc trở thành nỗi ám ảnh? Đã có giải pháp cứu nguy!",
                overlay_title="ÁM ẢNH BẾP NÚC?",
                overlay_subtitle="Dính khét - Tốn thời gian?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person standing by stove looking tired and frustrated at an old scratched sticky pan with burnt food. "
                    f"Mouth closed, no speaking, moody kitchen lighting{idea_ctx}. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Đổi ngay sang dụng cụ thông minh",
                kind="FLOW_AI",
                narrator_text=f"Chuyển ngay sang {clean_title}! Lớp chống dính cao cấp giúp nguyên liệu lướt nhẹ nhàng, chiên xào cực đỉnh mà không lo bám dính.",
                overlay_title="LƯỚT NHẸ ÊM ÁI",
                overlay_subtitle="Chống dính tuyệt đối",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Macro close-up shot of hands cooking with {clean_title}, fresh egg and meat gliding effortlessly on surface without sticking. "
                    f"Crisp steam sizzle, bright appetizing commercial lighting. NO text overlays, NO face."
                ),
            ),
            SceneDefinition(
                id=3,
                name="Feature - Bữa ăn ngon nóng hổi trong tích tắc",
                kind="FLOW_AI",
                narrator_text="Chỉ trong vài phút là đã có ngay món ăn thơm ngon, vàng giòn hấp dẫn. Thảnh thơi tận hưởng bữa tối mà không tốn công sức.",
                overlay_title="THƠM NGON NÓNG HỔI",
                overlay_subtitle="Nấu nhanh trong vài phút",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person smiling warmly as they place a steaming appetizing meal on table, leaning back with immense satisfaction. "
                    f"Mouth closed, no speaking, warm cozy dining ambiance. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Lau một lần là sạch bóng",
                kind="FLOW_AI",
                narrator_text="Dọn rửa siêu nhanh chỉ bằng một lần lau nhẹ. Gian bếp luôn tinh tươm, cho bạn trọn vẹn thời gian thư giãn bên gia đình!",
                overlay_title="LAU LÀ SẠCH BÓNG",
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
                name="Hook - Áo quần bí bách & Khó phối đồ",
                kind="FLOW_AI",
                narrator_text="Tủ đồ chật ních nhưng mỗi sáng lại không biết mặc gì, trang phục cũ thì bí bách và gò bó? Đừng lo!",
                overlay_title="KHÔNG BIẾT MẶC GÌ?",
                overlay_subtitle="Bí bách - Khó phối đồ?",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person standing before a wardrobe looking indecisive and frustrated, holding uncomfortable wrinkled clothes. "
                    f"Mouth closed, no speaking{idea_ctx}. Moody indoor lighting. NO text overlays, NO talking."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero Action - Cứu cánh phong cách với thiết kế mới",
                kind="FLOW_AI",
                narrator_text=f"Diện ngay {clean_title}! Form dáng chuẩn đẹp, chất liệu mềm mát và cực kỳ tôn dáng, giải quyết trọn vẹn bài toán phối đồ hàng ngày.",
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
                name="Feature - Nhẹ nhõm & Tự tin trước gương",
                kind="FLOW_AI",
                narrator_text="Mặc vào thoải mái vận động suốt cả ngày mà không lo nhăn nhúm. Cảm giác tự tin và tràn đầy năng lượng tích cực.",
                overlay_title="THOẢI MÁI VẬN ĐỘNG",
                overlay_subtitle="Tự tin tràn đầy năng lượng",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Person smiling genuinely into a full-length mirror, turning with confidence and effortless style. "
                    f"Mouth closed, no speaking, chic interior light. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Lifestyle - Thu hút mọi ánh nhìn trên phố",
                kind="FLOW_AI",
                narrator_text="Dễ dàng kết hợp đi làm, đi chơi hay gặp gỡ bạn bè. Món đồ must-have nâng tầm phong cách sống của bạn!",
                overlay_title="MUST-HAVE TRONG TỦ ĐỒ",
                overlay_subtitle="Tự tin sải bước",
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
                name="Hook - Căng thẳng & Đau mỏi ê ẩm",
                kind="FLOW_AI",
                narrator_text="Ngồi làm việc cả ngày khiến cổ vai gáy cứng đờ, cơ thể mệt mỏi rã rời làm giảm sút năng suất? Cần giải pháp ngay!",
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
                name="Hero Action - Cứu nguy cơ bắp tức thì",
                kind="FLOW_AI",
                narrator_text=f"Sử dụng ngay {clean_title}! Lực tác động sâu giúp xoa dịu các bó cơ căng cứng, kích hoạt lưu thông máu chỉ sau vài phút.",
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
                name="Feature - Nhẹ bẫng & Sảng khoái",
                kind="FLOW_AI",
                narrator_text="Cơn đau nhức tan biến hoàn toàn, trả lại sự sảng khoái và tinh thần phấn chấn để tiếp tục làm việc hiệu quả.",
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
                name="Lifestyle - Chăm sóc sức khỏe mỗi ngày",
                kind="FLOW_AI",
                narrator_text="Nhỏ gọn, mang theo văn phòng hay đi du lịch đều cực kỳ tiện lợi. Trợ thủ bảo vệ sức khỏe không thể thiếu!",
                overlay_title="BẢO VỆ SỨC KHỎE",
                overlay_subtitle="Tiện lợi mọi lúc mọi nơi",
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
                    narrator_text="Laptop liên tục báo động đầy bộ nhớ giữa lúc công việc đang vô cùng gấp gáp? Đừng lo, đã có giải pháp cứu nguy siêu tiện lợi!",
                    overlay_title="BÁO ĐỘNG ĐẦY BỘ NHỚ",
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
                    narrator_text=f"Rút ngay chiếc {clean_title}, thiết kế nhỏ gọn như móc khóa. Cắm nhẹ vào cổng máy là nhận ngay, giải phóng hàng trăm gigabyte dữ liệu tức thì.",
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
                    narrator_text="Chuẩn tốc độ cao giúp sao chép toàn bộ dự án nặng chỉ trong vài giây. Mọi tài liệu và video quan trọng đều được lưu trữ an toàn tuyệt đối.",
                    overlay_title="TRUYỀN TẢI SIÊU TỐC",
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
                    narrator_text="Móc gọn gàng cùng chìa khóa xe, mang theo cả kho dữ liệu khổng lồ bên mình mọi lúc mọi nơi. Nhỏ gọn, bền bỉ và an tâm cho mọi chuyến đi!",
                    overlay_title="CỨU TINH MỌI LÚC MỌI NƠI",
                    overlay_subtitle="Móc khóa tiện lợi - Siêu bền bỉ",
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
                    narrator_text="Dây nguồn, ổ cắm lòng thòng bừa bộn dưới chân bàn, làm bạn ngột ngạt và mất tập trung? Đừng lo lắng!",
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
                    narrator_text=f"Lắp ngay {clean_title}! Thiết kế kẹp bàn thông minh, không cần khoan đục. Giấu trọn mọi ổ cắm và dây nhợ, gọn gàng chỉ trong tích tắc!",
                    overlay_title="KẸP BÀN THÔNG MINH",
                    overlay_subtitle="Không cần khoan - Lắp cực nhanh",
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
                    narrator_text=f"{feat1_desc}. Toàn bộ góc làm việc bỗng trở nên thông thoáng, ngăn nắp và hiện đại hơn bao giờ hết.",
                    overlay_title=feat1_title,
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
                    narrator_text="Chất liệu nhôm cao cấp chịu lực cực tốt. Giải phóng tối đa không gian, cho bạn thỏa sức sáng tạo và làm việc mỗi ngày!",
                    overlay_title="KHÔNG GIAN LÝ TƯỞNG",
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
                    narrator_text="Thiết bị chập chờn, pin tụt nhanh giữa lúc công việc đang cao điểm? Đừng để sự cố làm gián đoạn ngày làm việc của bạn!",
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
                    narrator_text=f"Rút ngay {clean_title}! Kết nối nhanh chóng, đường truyền siêu ổn định giúp đưa mọi thiết bị trở lại hoạt động với 100% công suất.",
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
                    narrator_text=f"{feat1_desc}. Hiệu suất mạnh mẽ, giúp bạn hoàn thành mọi deadline nhẹ nhàng không chút lo âu.",
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
                    narrator_text="Nhỏ gọn trong lòng bàn tay, người bạn đồng hành tin cậy cho mọi người làm việc hiện đại!",
                    overlay_title="TỰ DO MỌI NƠI",
                    overlay_subtitle="Nhỏ gọn - An tâm tuyệt đối",
                    image_index=0,
                    prompt=(
                        f"Vertical 9:16 RAW cinematic video. Hands slipping {clean_title} into jacket pocket, walking confidently out of cafe into city. "
                        f"Mouth closed, no speaking. NO text overlays."
                    ),
                ),
            ]

    # GENERAL_LIFESTYLE Fallback
    return [
        SceneDefinition(
            id=1,
            name="Hook - Rắc rối vụn vặt thường ngày",
            kind="FLOW_AI",
            narrator_text="Những sự cố bất tiện trong sinh hoạt hàng ngày làm bạn tốn thời gian và mệt mỏi? Đã đến lúc nâng cấp cuộc sống!",
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
            narrator_text=f"Sử dụng ngay {clean_title}! Thiết kế thông minh xử lý mọi vấn đề chỉ trong tích tắc, cực kỳ tiện lợi và dễ dàng.",
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
            narrator_text=f"{feat1_desc}. Mọi thứ trở nên ngăn nắp, dễ dàng hơn bao giờ hết, mang lại sự thảnh thơi cho cả gia đình.",
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
            narrator_text=f"{feat2_desc}. Món đồ tiện ích xứng đáng có mặt trong mọi gia đình hiện đại!",
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


def generate_default_storyboard(
    info: ProductInfo,
    style: str = "flow_cinematic",
    cta_mode: str = "none",
    custom_idea: Optional[str] = None,
    channel_name: Optional[str] = None,
) -> List[SceneDefinition]:
    """
    Generate a smart, data-driven ad template tailored to ANY product and category.
    cta_mode:
      - 'none': 4 scenes (Hook, Hero, Feature 1, Feature 2 / Social Proof). Best for Facebook Page branding.
      - 'follow': 5 scenes with a soft outro inviting viewers to follow the page.
      - 'shopee': 5 scenes with a direct call-to-action to check cart / buy on Shopee/TikTok.
    style:
      - 'flow_cinematic' / 'tech_minimal': Video AI điện ảnh, tương tác thật trên tay, không lệch khẩu hình.
      - 'problem_solution' / 'drama': Tình huống cấp bách theo ngành hàng -> Sản phẩm giải cứu ngoạn mục.
      - 'lifestyle_edc': Phong cách sống năng động, thẩm mỹ, tiện lợi mang theo hàng ngày.
      - 'hybrid': Kết hợp video AI cảm xúc + ảnh thật sản phẩm từ Shopee ZIP.
      - 'local': Dùng video/ảnh gốc từ ZIP.
    """
    channel_name = channel_name or DEFAULT_CHANNEL_NAME
    clean_title = clean_product_title(info.name)
    category = detect_product_category(info.name, info.description_text)
    logger.info(f"[Storyboard] Đã phát hiện ngành hàng: {category} cho sản phẩm '{clean_title}'")

    has_video = bool(info.video_name)
    features = extract_product_features(info.description_text)

    # Defaults for features if description doesn't have clear bullets
    feat1_title, feat1_desc = (
        features[0] if len(features) > 0
        else ("THIẾT KẾ TIỆN DỤNG", "Trang bị công nghệ hiện đại, đáp ứng trọn vẹn mọi nhu cầu với hiệu năng vượt trội.")
    )
    feat2_title, feat2_desc = (
        features[1] if len(features) > 1
        else ("CHẤT LƯỢNG HÀNG ĐẦU", "Chất liệu cao cấp, độ bền bỉ dài lâu và được đông đảo khách hàng đánh giá cao.")
    )

    # Trust badge overlay text (Do NOT use raw sold count in video overlays)
    social_proof_title = "LỰA CHỌN HOÀN HẢO"
    if info.rating:
        try:
            r_val = float(str(info.rating).replace(",", ".").strip())
            if r_val >= 4.5:
                social_proof_title = f"ĐÁNH GIÁ {info.rating} SAO"
            elif r_val >= 4.0:
                social_proof_title = "ĐƯỢC ĐÁNH GIÁ CAO"
        except (ValueError, AttributeError):
            pass

    num_images = len(info.image_names) if info.image_names else 1

    if style in ("problem_solution", "drama"):
        scenes = _build_problem_solution_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            custom_idea=custom_idea,
        )
    elif style in ("lifestyle_edc", "lifestyle"):
        scenes = _build_lifestyle_edc_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            custom_idea=custom_idea,
        )
    elif style in ("flow_cinematic", "flow", "tech_minimal"):
        scenes = _build_flow_cinematic_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
        )
    elif style == "hybrid":
        # Hybrid: Flow AI for lifestyle/human emotional scenes + Real photos for authentic product display
        scenes = [
            SceneDefinition(
                id=1,
                name="Hook - Nhu cầu & Sự tò mò",
                kind="FLOW_AI",
                narrator_text=f"Bạn đang tìm một sản phẩm thật ưng ý và tiện lợi cho nhu cầu hàng ngày? Xem ngay siêu phẩm {clean_title} cực hot này nhé!",
                overlay_title="BẠN ĐANG TÌM KIẾM?",
                overlay_subtitle=clean_title,
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Three stylish young Vietnamese friends hanging out in a modern cafe, "
                    f"putting phones down and showing great curiosity and energetic excitement. "
                    f"Warm cozy ambient lighting, shot on 35mm lens. Mouth closed, no speaking. NO fake packaging, NO cards."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero - Giới thiệu sản phẩm thật",
                kind="PRODUCT_PHOTO",
                narrator_text=f"Đây là {clean_title}, thiết kế hiện đại, hoàn thiện tinh tế và đáp ứng hoàn hảo mọi kỳ vọng của bạn.",
                overlay_title=clean_title[:28].upper(),
                overlay_subtitle="Chính hãng - Thiết kế cao cấp",
                image_index=0,
            ),
            SceneDefinition(
                id=3,
                name="Tính năng nổi bật 1",
                kind="FLOW_AI",
                narrator_text=feat1_desc,
                overlay_title=feat1_title,
                overlay_subtitle="Trải nghiệm tiện lợi vượt trội",
                image_index=min(1, num_images - 1),
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young expressive Vietnamese friends laughing and smiling happily, "
                    f"enjoying a fun moment together in a modern stylish setting. Natural cinematic lighting. Mouth closed, no speaking. NO fake packaging."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Tính năng nổi bật 2 & Uy tín",
                kind="PRODUCT_PHOTO",
                narrator_text=f"{feat2_desc}. Sản phẩm đã nhận được hàng ngàn đánh giá tích cực và sự tin yêu trên Shopee.",
                overlay_title=social_proof_title,
                overlay_subtitle=feat2_title[:28],
                image_index=min(2, num_images - 1),
            ),
        ]
    else:
        # Local video / Image slide pipeline
        kind_default = "REAL_FOOTAGE" if has_video else "IMAGE_SLIDE"
        scenes = [
            SceneDefinition(
                id=1,
                name="Hook - Nhu cầu / Vấn đề",
                kind=kind_default,
                narrator_text=f"Bạn đang tìm một giải pháp hoàn hảo cho {clean_title}? Xem ngay sản phẩm cực hot này nhé!",
                overlay_title="SIÊU PHẨM CỰC HOT",
                overlay_subtitle=clean_title,
                real_start_sec=0.0,
                image_index=0,
            ),
            SceneDefinition(
                id=2,
                name="Hero - Giới thiệu sản phẩm",
                kind=kind_default,
                narrator_text=f"Đây là {clean_title}, thiết kế cao cấp, hoàn thiện tỉ mỉ và cực kỳ tiện lợi khi sử dụng hàng ngày.",
                overlay_title=clean_title[:28].upper(),
                overlay_subtitle="Hoàn thiện tỉ mỉ - Tiện lợi",
                real_start_sec=5.0,
                image_index=min(1, num_images - 1),
            ),
            SceneDefinition(
                id=3,
                name="Tính năng nổi bật 1",
                kind=kind_default,
                narrator_text=feat1_desc,
                overlay_title=feat1_title,
                overlay_subtitle="Hiệu năng vượt trội",
                real_start_sec=15.0,
                image_index=min(2, num_images - 1),
            ),
            SceneDefinition(
                id=4,
                name="Tính năng nổi bật 2",
                kind=kind_default,
                narrator_text=f"{feat2_desc}. Sản phẩm được đánh giá rất cao bởi đông đảo khách hàng trên Shopee.",
                overlay_title=social_proof_title,
                overlay_subtitle=feat2_title[:28],
                real_start_sec=25.0,
                image_index=min(3, num_images - 1),
            ),
        ]

    # Optional CTA Scene 5
    if cta_mode == "follow":
        persona = _get_character_persona(category)
        follow_text = f"Follow ngay {channel_name}" if channel_name else "Follow ngay kênh"
        overlay_t = f"FOLLOW {channel_name.upper()}" if channel_name else "FOLLOW KÊNH NGAY"
        name_t = f"Outro - Kêu gọi Follow {channel_name}" if channel_name else "Outro - Kêu gọi Follow Kênh"
        scenes.append(
            SceneDefinition(
                id=len(scenes) + 1,
                name=name_t,
                kind="FLOW_AI" if style != "local" else ("REAL_FOOTAGE" if has_video else "IMAGE_SLIDE"),
                narrator_text=f"{follow_text} để khám phá thêm nhiều món đồ thông minh và giải pháp tiện ích mỗi ngày nhé!",
                overlay_title=overlay_t,
                overlay_subtitle="Mẹo hay & Tiện ích mỗi ngày",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Featuring {persona['cont']}, giving a gentle wave and warm genuine smile to camera in a modern tidy aesthetic room. "
                    f"Natural modern aesthetic lighting. Mouth closed, no speaking, no dialogue. NO text overlays."
                ),
            )
        )
    elif cta_mode == "shopee":
        scenes.append(
            SceneDefinition(
                id=len(scenes) + 1,
                name="Kêu gọi hành động (CTA)",
                kind="FLOW_AI" if style != "local" else ("REAL_FOOTAGE" if has_video else "IMAGE_SLIDE"),
                narrator_text="Đừng bỏ lỡ ưu đãi cực hời hôm nay! Bấm ngay vào giỏ hàng bên dưới để săn sale giá tốt và nhận bảo hành chính hãng nhé!",
                overlay_title="BẤM GIỎ HÀNG SĂN SALE!",
                overlay_subtitle="Giá cực hời - Đặt mua ngay",
                image_index=0,
                prompt=(
                    "Vertical 9:16 RAW cinematic video. Happy young Vietnamese creator smiling warmly at the camera, raising a cheerful thumbs-up. "
                    "Mouth closed, no speaking, bright vibrant ambient lighting. NO text overlays."
                ),
            )
        )

    return scenes


def load_or_create_storyboard(
    info: ProductInfo,
    json_path: Path,
    style: str = "flow_cinematic",
    cta_mode: str = "none",
    force: bool = False,
    custom_idea: Optional[str] = None,
    channel_name: Optional[str] = None,
) -> List[SceneDefinition]:
    """
    Load an existing storyboard.json or create a new one from ProductInfo.
    Allows manual customization per product without editing code.
    """
    json_path = Path(json_path)
    if json_path.exists() and not force:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            scenes = [SceneDefinition(**item) for item in data]
            print(f"[Storyboard] Nạp kịch bản hiện có ({len(scenes)} scenes) từ {json_path.name}")
            return scenes
        except Exception as e:
            print(f"[Storyboard] Cảnh báo: Không đọc được {json_path}, tạo mới kịch bản: {e}")

    scenes = generate_default_storyboard(info, style=style, cta_mode=cta_mode, custom_idea=custom_idea, channel_name=channel_name)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in scenes], f, ensure_ascii=False, indent=2)
    print(f"[Storyboard] Đã tự động tạo và lưu kịch bản động mới ({len(scenes)} cảnh, style='{style}', cta='{cta_mode}') tại {json_path.name}")
    return scenes
