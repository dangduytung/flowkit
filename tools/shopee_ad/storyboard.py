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
    Removes spam tags, bracketed codes, repetitive capacity/size listings, shop warranties,
    and foreign apparel buzzwords (e.g. PERFORMANCE PANTS, SLIMFIT) that cause rushed speech.
    """
    name = re.sub(r"^(Tên sản phẩm:|\s*\[.*?\]|\s*\(.*?\))\s*", "", raw_name, flags=re.I).strip()
    name = re.sub(r"\[.*?\]|\(.*?\)|\【.*?\】", " ", name)
    name = re.sub(r"[\-–—]\s*(?:bảo hành|chính hãng|full box|freeship|sẵn hàng|chất lượng).*", "", name, flags=re.I).strip()

    # Strip model/SKU codes at word boundaries or ends (e.g. FABK001, HPW-CM01, EJF357BLK)
    name = re.sub(r"\b[A-Z0-9]*\d{2,}[A-Z0-9]*\b", "", name)
    name = re.sub(r"\s+[A-Z0-9]{2,}[\-\d]+[A-Z0-9]*$", "", name).strip()

    # Remove repetitive specs (capacities, volumes, sizes, wattages)
    name = re.sub(r"(?:\b\d+[\.,]?\d*\s*(?:TB|GB|MB|ml|g|kg|L|W|w|spf|pa[\+]*)\b[\s,/]*)+", " ", name, flags=re.I)
    name = re.sub(r"(?:\b(?:size\s*)?[SMLX]+\b[\s,/]*){2,}", " ", name, flags=re.I)

    # Strip redundant foreign apparel/marketing buzzwords that hurt Vietnamese TTS pacing
    buzzwords = [
        "PERFORMANCE PANTS", "PERFORMANCE", "PANTS", "BASIC", "PREMIUM", "SLIMFIT", "SLIM FIT",
        "REGULAR FIT", "OVERSIZED", "OVERSIZE", "COLLECTION", "OFFICIAL STORE", "OFFICIAL",
        "AUTHENTIC", "HIGH QUALITY", "BEST QUALITY", "NEW ARRIVAL", "HOT TREND",
        "TONE UP NO SEBUM SUNSCREEN", "SUNSCREEN", "TONE UP", "NO SEBUM"
    ]
    for bw in buzzwords:
        name = re.sub(r"\b" + bw + r"\b", "", name, flags=re.I)

    # Remove duplicate 'usb' suffixes if 'usb' already appears earlier
    if re.search(r"\busb\b", name[:10], flags=re.I):
        name = re.sub(r"\s+usb\s*[\d\.]*$", "", name, flags=re.I)

    name = re.sub(r"\s+", " ", name).strip()

    # Strip SEO keyword stuffing after comma or spec words
    name = re.sub(r",\s*(?:form chuẩn|dáng đẹp|giá rẻ|hàng đẹp|túi lé).*", "", name, flags=re.I)
    name = re.sub(r"\s+(?:dài|ngắn|lửng)?\s*(?:basic|cạp tender|túi lé|form chuẩn|kẹp bàn|kim loại cao cấp|công suất).*", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()

    parts = re.split(r"[_|\-–—,]", name)
    short = parts[0].strip()

    # If title is longer than 5 words, keep core noun + brand for clean spoken rhythm
    words = short.split()
    if len(words) > 5:
        brand = None
        for w in words[3:7]:
            if (w.isupper() and len(w) >= 3 and w not in ["NAM", "NỮ", "PRO", "MAX"]) or any(c.isupper() for c in w[1:]):
                brand = w
                break
        if brand:
            core_words = [w for w in words[:3] if w.upper() != brand.upper()]
            short = " ".join(core_words) + " " + brand
        else:
            if len(words) >= 5 and words[3].lower() in ["văn", "công", "tiện", "đa", "thông", "chống", "siêu"]:
                short = " ".join(words[:5])
            else:
                short = " ".join(words[:4])

    # Capitalize brand nicely if all-caps
    res_words = []
    for w in short.split():
        if w.isupper() and len(w) > 3 and w not in ["USB", "SSD", "HDD", "LED", "RGB", "TYPE-C"]:
            res_words.append(w.capitalize())
        else:
            res_words.append(w)

    return " ".join(res_words).strip()


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
        "ghế kê chân", "kê chân", "đệm kê chân", "bàn kê chân", "footrest", "công thái học",
        "đi dây", "desk setup", "hyperwork"
    ]
    if _matches(tech_kw):
        return "TECH_GADGETS"

    return "GENERAL_LIFESTYLE"


from tools.shopee_ad.prompts import (
    _get_character_persona,
    _build_flow_cinematic_scenes,
    _build_problem_solution_scenes,
    _build_lifestyle_edc_scenes,
    _build_faceless_pov_scenes,
    _build_cta_scene,
)



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
      - 'faceless_pov' / 'hands_on_demo': Video POV cận cảnh bàn tay/tương tác thực tế, 100% không lộ mặt (chuẩn TikTok Review).
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

    if style in ("faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov"):
        scenes = _build_faceless_pov_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
        )
    elif style in ("problem_solution", "drama"):
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
                name="Hook - Nhu cầu & Trải nghiệm thực tế",
                kind="FLOW_AI",
                narrator_text=f"Bạn đang tìm một món đồ thật ưng ý và tiện dụng mỗi ngày? Cùng mình trải nghiệm {clean_title} này nhé!",
                overlay_title="TRẢI NGHIỆM THỰC TẾ",
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
                narrator_text=f"Đây là {clean_title}, thiết kế nhỏ gọn, cầm đầm tay và hoàn thiện cực kỳ chỉn chu.",
                overlay_title=clean_title[:28].upper(),
                overlay_subtitle="Chính hãng - Hoàn thiện tỉ mỉ",
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
                name="Tính năng nổi bật 2 & Đánh giá tốt",
                kind="PRODUCT_PHOTO",
                narrator_text=f"{feat2_desc}. Sản phẩm được rất nhiều người dùng đánh giá tốt và tin tưởng sử dụng.",
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
                name="Hook - Nhu cầu thực tế",
                kind=kind_default,
                narrator_text=f"Bạn đang tìm một món đồ vừa chất lượng vừa tiện lợi cho {clean_title}? Cùng mình khám phá trải nghiệm thực tế ngay trong video này nhé!",
                overlay_title="TRẢI NGHIỆM THỰC TẾ",
                overlay_subtitle=clean_title,
                real_start_sec=0.0,
                image_index=0,
            ),
            SceneDefinition(
                id=2,
                name="Hero - Giới thiệu sản phẩm",
                kind=kind_default,
                narrator_text=f"Đây là chiếc {clean_title}, thiết kế tối giản thông minh, cầm đầm tay chắc chắn và cực kỳ tiện dụng mỗi ngày.",
                overlay_title=clean_title[:28].upper(),
                overlay_subtitle="Nhỏ gọn - Cực kỳ tiện dụng",
                real_start_sec=5.0,
                image_index=min(1, num_images - 1),
            ),
            SceneDefinition(
                id=3,
                name="Tính năng nổi bật 1",
                kind=kind_default,
                narrator_text=f"{feat1_desc}. Mọi chi tiết hoàn thiện chỉn chu, mang lại cảm giác an tâm và hài lòng tuyệt đối khi sử dụng.",
                overlay_title=feat1_title,
                overlay_subtitle="Hiệu năng mượt mà",
                real_start_sec=15.0,
                image_index=min(2, num_images - 1),
            ),
            SceneDefinition(
                id=4,
                name="Tính năng nổi bật 2",
                kind=kind_default,
                narrator_text=f"{feat2_desc}. Sản phẩm được rất nhiều bạn đánh giá cao và tin dùng sau khi trực tiếp trải nghiệm.",
                overlay_title=social_proof_title,
                overlay_subtitle=feat2_title[:28],
                real_start_sec=25.0,
                image_index=min(3, num_images - 1),
            ),
        ]

    # Optional CTA Scene 5
    cta_scene = _build_cta_scene(
        scene_id=len(scenes) + 1,
        cta_mode=cta_mode,
        category=category,
        style=style,
        clean_title=clean_title,
        channel_name=channel_name,
        is_local=(style == "local"),
        has_video=has_video,
    )
    if cta_scene:
        scenes.append(cta_scene)

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
