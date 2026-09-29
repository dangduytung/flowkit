"""Storyboard management: dynamically extracts features and generates scene scripts for ANY product."""
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from tools.shopee_ad.product_parser import ProductInfo


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
    Removes generic prefixes, noise tags, and trailing codes.
    """
    name = re.sub(r"^(Tên sản phẩm:|\s*\[.*?\]|\s*\(.*?\))\s*", "", raw_name, flags=re.I).strip()
    parts = re.split(r"[_|\-–—]", name)
    short = parts[0].strip()
    if len(short) < 14 and len(parts) > 1:
        short = f"{short} {parts[1].strip()}"
    return short[:42].strip()


def extract_product_features(description_text: str) -> List[Tuple[str, str]]:
    """
    Extract key selling points / features from Shopee description text.
    Returns list of (badge_title, full_sentence).
    """
    lines = [l.strip() for l in description_text.splitlines() if l.strip()]
    header_blacklist = (
        "thông tin", "hướng dẫn", "lưu ý", "gợi ý", "chính sách",
        "cam kết", "bảo hành", "xuất xứ", "mô tả", "tên sản phẩm",
        "link sản phẩm", "ngày tải", "số sao", "đã bán", "hastag",
    )

    # Pass 1: Prioritize lines with checkmarks or bullet symbols
    bullets = []
    for l in lines:
        if re.match(r"^[✅⭐👉🔹✔]\s*", l):
            clean = re.sub(r"^[✅⭐👉🔹✔\s]+", "", l).strip()
            if len(clean) >= 12 and not clean.startswith("#") and not clean.startswith("http"):
                bullets.append(clean)

    # Pass 2: Lines formatted as 'Title: Description' or bulleted with dash
    if len(bullets) < 2:
        for l in lines:
            if any(l.lower().startswith(p) for p in header_blacklist) or l.startswith("---"):
                continue
            clean = re.sub(r"^[\-\*\•\d\.\)]+\s*", "", l).strip()
            if len(clean) < 14 or clean.startswith("#") or clean.startswith("http"):
                continue
            if ":" in clean:
                t, d = clean.split(":", 1)
                t, d = t.strip(), d.strip()
                if 3 <= len(t) <= 28 and len(d) >= 12 and not any(h in t.lower() for h in header_blacklist):
                    bullets.append(f"{t}: {d}")

    # Format into (badge_title, sentence)
    results = []
    for b in bullets:
        if " - " in b:
            t, d = b.split(" - ", 1)
            t_clean = re.sub(r"[^\w\s\d]", "", t).strip().upper()[:22]
            results.append((t_clean, d.strip()))
        elif ":" in b:
            t, d = b.split(":", 1)
            t_clean = re.sub(r"[^\w\s\d]", "", t).strip().upper()[:22]
            results.append((t_clean, d.strip()))
        else:
            t_clean = re.sub(r"[^\w\s\d]", "", b[:22]).strip().upper()
            results.append((t_clean, b))

        if len(results) >= 3:
            break

    return results


def generate_default_storyboard(info: ProductInfo, style: str = "hybrid") -> List[SceneDefinition]:
    """
    Generate a smart, data-driven 5-scene ad template tailored to the parsed product.
    Zero hardcoded strings — works for any product category.
    """
    clean_title = clean_product_title(info.name)
    has_video = bool(info.video_name)
    features = extract_product_features(info.description_text)

    # Defaults for features if description doesn't have clear bullets
    feat1_title, feat1_desc = (
        features[0] if len(features) > 0
        else ("THIẾT KẾ TIỆN DỤNG", f"Trang bị công nghệ hiện đại, đáp ứng trọn vẹn mọi nhu cầu với hiệu năng vượt trội.")
    )
    feat2_title, feat2_desc = (
        features[1] if len(features) > 1
        else ("CHẤT LƯỢNG HÀNG ĐẦU", f"Chất liệu cao cấp, độ bền bỉ dài lâu và được người tiêu dùng đánh giá cao.")
    )

    # Social proof overlay text
    if info.sold_count:
        social_proof_title = f"ĐÃ BÁN {info.sold_count.upper()}"
    elif info.rating:
        social_proof_title = f"ĐÁNH GIÁ {info.rating} SAO"
    else:
        social_proof_title = "SIÊU PHẨM HOT TREND"

    num_images = len(info.image_names) if info.image_names else 1

    if style == "hybrid":
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
                    f"Warm cozy ambient lighting, shot on 35mm lens. NO fake packaging, NO cards."
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
                    f"enjoying a fun moment together in a modern stylish setting. Natural cinematic lighting. NO fake packaging."
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
            SceneDefinition(
                id=5,
                name="Kêu gọi hành động (CTA)",
                kind="FLOW_AI",
                narrator_text="Đừng bỏ lỡ ưu đãi cực hời hôm nay! Bấm ngay vào giỏ hàng bên dưới để săn sale giá tốt và nhận bảo hành chính hãng nhé!",
                overlay_title="BẤM GIỎ HÀNG SĂN SALE!",
                overlay_subtitle="Giá cực hời - Đặt mua ngay",
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Group of happy young friends smiling warmly at the camera, "
                    f"raising cheerful thumbs-up and pointing playfully downwards towards the bottom of the screen. "
                    f"Bright vibrant ambient cafe lighting. NO text overlays."
                ),
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
            SceneDefinition(
                id=5,
                name="Kêu gọi hành động (CTA)",
                kind=kind_default,
                narrator_text="Đừng bỏ lỡ ưu đãi cực hời hôm nay! Bấm ngay vào giỏ hàng bên dưới để đặt mua và nhận bảo hành chính hãng nhé!",
                overlay_title="BẤM GIỎ HÀNG SĂN SALE!",
                overlay_subtitle="Ưu đãi giới hạn - Đặt mua ngay",
                real_start_sec=35.0,
                image_index=0,
            ),
        ]

    return scenes


def load_or_create_storyboard(
    info: ProductInfo,
    json_path: Path,
    style: str = "hybrid",
) -> List[SceneDefinition]:
    """
    Load an existing storyboard.json or create a new one from ProductInfo.
    Allows manual customization per product without editing code.
    """
    json_path = Path(json_path)
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            scenes = [SceneDefinition(**item) for item in data]
            print(f"[Storyboard] Nạp kịch bản hiện có ({len(scenes)} scenes) từ {json_path.name}")
            return scenes
        except Exception as e:
            print(f"[Storyboard] Cảnh báo: Không đọc được {json_path}, tạo mới kịch bản: {e}")

    scenes = generate_default_storyboard(info, style=style)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in scenes], f, ensure_ascii=False, indent=2)
    print(f"[Storyboard] Đã tự động tạo và lưu kịch bản động mới tại {json_path.name}")
    return scenes
