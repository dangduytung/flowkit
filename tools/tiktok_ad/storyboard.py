"""Storyboard management: dynamically extracts features and generates scene scripts for TikTok Ads."""
import logging
import re
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple

from tools.common import storyboard_io
from tools.common.models import SceneDefinition
from tools.tiktok_ad.config import DEFAULT_CHANNEL_NAME
from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.prompts import (
    build_viral_hook_scenes,
    build_faceless_pov_scenes,
    build_problem_solution_scenes,
    build_flow_cinematic_scenes,
    build_lifestyle_edc_scenes,
)

logger = logging.getLogger(__name__)

# A stored TikTok storyboard with fewer scenes is treated as incomplete and rebuilt.
MIN_STORYBOARD_SCENES = 4

__all__ = [
    "SceneDefinition",
    "clean_product_title",
    "detect_product_category",
    "extract_top_features",
    "generate_dynamic_storyboard",
    "load_or_create_storyboard",
]


def clean_product_title(raw_name: str) -> str:
    """
    Extract a concise, clean product name suitable for spoken audio and overlay titles.
    Removes spam tags, bracketed codes, repetitive capacity/size listings, warranties,
    and foreign buzzwords that hurt Vietnamese TTS pacing.
    """
    name = re.sub(
        r"^(Tên sản phẩm:|\s*\[.*?\]|\s*\(.*?\))\s*", "", raw_name, flags=re.I
    ).strip()
    name = re.sub(r"\[.*?\]|\(.*?\)|\【.*?\】", " ", name)
    name = re.sub(
        r"[\-–—]\s*(?:bảo hành|chính hãng|full box|freeship|sẵn hàng|chất lượng).*",
        "",
        name,
        flags=re.I,
    ).strip()

    # If title has comma-separated clauses, prioritize the main first clause
    if "," in name:
        parts = [p.strip() for p in name.split(",") if p.strip()]
        if parts:
            name = parts[0]

    # Strip model/SKU codes at word boundaries or ends
    name = re.sub(r"\b[A-Z0-9]*\d{2,}[A-Z0-9]*\b", "", name)
    name = re.sub(r"\s+[A-Z0-9]{2,}[\-\d]+[A-Z0-9]*$", "", name).strip()

    # Remove repetitive specs (capacities, volumes, sizes, dimensions)
    name = re.sub(
        r"(?:\b\d+[\.,]?\d*\s*(?:TB|GB|MB|ml|g|kg|L|W|w|spf|pa[\+]*)\b[\s,/]*)+",
        " ",
        name,
        flags=re.I,
    )
    name = re.sub(r"(?:\b(?:size\s*)?[SMLX]+\b[\s,/]*){2,}", " ", name, flags=re.I)
    name = re.sub(r"\b\d+x\d+x\d+\b", "", name, flags=re.I)

    # Clean whitespace
    name = re.sub(r"\s+", " ", name).strip(" ,.-–—")
    if len(name) > 65:
        # Truncate at word boundary safely without cutting mid-word
        truncated = name[:65]
        if " " in truncated:
            name = truncated.rsplit(" ", 1)[0].strip()
        else:
            name = truncated

    return name if name else "Sản phẩm tiện ích"


def detect_product_category(name: str, description_text: str = "") -> str:
    """Intelligently classify ANY product into core commercial categories."""
    text = f"{name} {description_text}".lower()

    def _matches(keywords: list[str]) -> bool:
        for kw in keywords:
            pattern = r"(?:\b|\s|^)" + re.escape(kw) + r"(?:\b|\s|$)"
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    # 1. Health & Fitness
    health_kw = [
        "kê chân", "gác chân", "massage", "công thái học", "ergonomic", "thư giãn", "sức khỏe", "súng massage"
    ]
    if _matches(health_kw):
        return "HEALTH_FITNESS"

    # 2. Storage & Home Organization & Travel (Checked before apparel/general to avoid collision)
    storage_kw = [
        "túi hút chân không", "túi nén hút chân không", "túi nén", "túi đựng", "hộp đựng đồ",
        "giá treo", "tủ vải", "kệ để giày", "vali", "sắp xếp tủ", "chăn màn"
    ]
    if _matches(storage_kw):
        return "GENERAL_LIFESTYLE"

    # 3. Beauty & Skincare
    beauty_kw = [
        "son", "serum", "kem dưỡng", "skincare", "kem chống nắng", "trang điểm", "nước hoa", "sữa rửa mặt"
    ]
    if _matches(beauty_kw):
        return "BEAUTY_SKINCARE"

    # 4. Tech & Gadgets
    tech_kw = [
        "chuột", "bàn phím", "usb", "tai nghe", "cáp sạc", "giá đỡ", "kẹp bàn"
    ]
    if _matches(tech_kw):
        return "TECH_GADGETS"

    # 5. Kitchen & Home
    kitchen_kw = [
        "bếp", "nồi", "chảo", "hộp đựng thực phẩm", "dao", "máy hút chân không", "hút chân không thực phẩm"
    ]
    if _matches(kitchen_kw):
        return "KITCHEN_HOME"

    # 6. Fashion & Apparel
    fashion_kw = [
        "áo thun", "áo sơ mi", "quần kaki", "quần jean", "váy", "giày", "dép", "túi xách", "ví"
    ]
    if _matches(fashion_kw):
        return "FASHION_APPAREL"

    return "GENERAL_LIFESTYLE"


def extract_top_features(
    description_text: str,
    product_name: str = "",
) -> List[Tuple[str, str]]:
    """Extract top highlight feature bullet points from product description."""

    lines = [line.strip() for line in description_text.splitlines() if line.strip()]
    candidates = []

    title_words = (
        set(re.findall(r"\w+", product_name.lower())) if product_name else set()
    )

    for line in lines:
        cleaned = re.sub(r"^[\-\*\•\d\.\+\=\>\:\~]+\s*", "", line).strip()
        cleaned_norm = unicodedata.normalize("NFC", cleaned)
        low_norm = cleaned_norm.lower()

        if len(cleaned_norm) < 10 or len(cleaned_norm) > 130:
            continue

        # Skip headers, metadata and section titles
        if cleaned_norm.endswith(":") or any(
            x in low_norm
            for x in [
                "thông tin chi tiết",
                "thông tin chi tiết",
                "đặc điểm",
                "mô tả sản phẩm",
                "kích thước như ảnh",
                "thông số",
                "lưu ý",
                "tên sản phẩm",
                "link sản phẩm",
                "ngày tải",
                "giá",
                "số sao",
                "lượt đánh giá",
                "đã bán",
                "người bán",
            ]
        ):
            continue

        # Skip line if it's practically a repetition of the product title
        line_words = set(re.findall(r"\w+", low_norm))
        if title_words and len(line_words) > 3:
            overlap = len(line_words & title_words) / len(line_words)
            if overlap >= 0.7:
                continue

        candidates.append(cleaned_norm)

    results = []
    for b in candidates:
        if " - " in b:
            t, d = b.split(" - ", 1)
            t, d = t.strip(), d.strip()
            if len(d) > 10:
                results.append((t[:24].upper(), d))
                if len(results) >= 2:
                    break
                continue
        elif ":" in b:
            t, d = b.split(":", 1)
            t, d = t.strip(), d.strip()
            if len(d) > 10:
                results.append((t[:24].upper(), d))
                if len(results) >= 2:
                    break
                continue

        low = b.lower()
        if len(b) < 25:
            continue

        if "massage" in low or "con lăn" in low or "trục lăn" in low or "matxa" in low:
            title = "TRỤC LĂN MASSAGE"
        elif "nhựa abs" in low or "chịu lực" in low or "bền bỉ" in low:
            title = "NHỰA ABS CHỊU LỰC"
        elif "chống trượt" in low or "đệm" in low:
            title = "CHÂN ĐỆM CHỐNG TRƯỢT"
        elif "thẳng lưng" in low or "tư thế" in low or "công thái học" in low:
            title = "CHUẨN TƯ THẾ NGỒI"
        else:
            words = b.split()
            title = " ".join(words[:3]).upper()[:22]

        if any(r[0] == title for r in results):
            continue

        results.append((title, b))

        if len(results) >= 2:
            break

    # Prioritize interactive / massage features as Feature 1
    if len(results) >= 2 and results[1][0] in ("TRỤC LĂN MASSAGE", "TÍNH NĂNG NỔI BẬT"):
        results[0], results[1] = results[1], results[0]

    # Defaults if no clean bullets found
    if len(results) == 0:
        results.append(
            ("TÍNH NĂNG NỔI BẬT", "Thiết kế thông minh, hoàn thiện tỉ mỉ và bền chắc.")
        )
    if len(results) == 1:
        results.append(
            ("TRẢI NGHIỆM TIỆN LỢI", "Sử dụng đơn giản, mang lại sự thoải mái tối đa.")
        )

    return results


def append_call_to_action(
    scenes: List[SceneDefinition],
    cta_mode: str,
    channel_name: str = DEFAULT_CHANNEL_NAME,
) -> List[SceneDefinition]:
    """Dynamically modify Scene 4 to include a high-converting CTA."""
    if not scenes or cta_mode == "none":
        return scenes

    s4 = scenes[-1]
    original = s4.narrator_text.strip()
    if cta_mode in ("yellow_cart", "cart", "tiktok"):
        cta_phrase = "Bấm ngay vào giỏ hàng màu vàng ở góc dưới bên trái màn hình để săn ưu đãi nhé!"
        if "giỏ hàng màu vàng" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "GIỎ HÀNG GÓC TRÁI"
        s4.overlay_subtitle = "Bấm Săn Deal Hôm Nay"
    elif cta_mode in ("profile_bio", "bio"):
        cta_phrase = "Xem ngay link chi tiết sản phẩm tại link Bio trên trang cá nhân nha cả nhà!"
        if "Bio" not in original:
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "LINK TRÊN BIO"
        s4.overlay_subtitle = "Bấm Vào Trang Cá Nhân"
    elif cta_mode == "follow":
        cta_phrase = "Bấm follow kênh để săn thêm nhiều deal hời và mẹo hay mỗi ngày nhé!"
        if "follow" not in original.lower():
            s4.narrator_text = f"{original} {cta_phrase}" if original else cta_phrase
        s4.overlay_title = "FOLLOW KÊNH NHA"
        s4.overlay_subtitle = "Cập Nhật Deal Mỗi Ngày"

    return scenes


def generate_dynamic_storyboard(
    product: ProductInfo,
    style: str = "viral_hook",
    cta_mode: str = "yellow_cart",
    custom_idea: Optional[str] = None,
    channel_name: str = DEFAULT_CHANNEL_NAME,
) -> List[SceneDefinition]:
    """Generate high-CTR TikTok storyboard tailored to product and style."""
    clean_title = clean_product_title(product.name)
    category = detect_product_category(product.name, product.description_text)
    features = extract_top_features(product.description_text, product_name=product.name)

    feat1_title, feat1_desc = features[0]
    feat2_title, feat2_desc = features[1]

    social_proof_title = "ĐƯỢC TIN DÙNG"
    if product.rating:
        try:
            r_val = float(str(product.rating).replace(",", ".").strip())
            if r_val >= 4.5:
                social_proof_title = f"ĐÁNH GIÁ {product.rating} SAO"
            elif r_val >= 4.0:
                social_proof_title = "ĐÁNH GIÁ CỰC TỐT"
        except Exception:
            pass

    if style in ("viral_hook", "hook", "viral"):
        scenes = build_viral_hook_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
            product=product,
        )
    elif style in ("faceless_pov", "hands_on_pov", "pov"):
        scenes = build_faceless_pov_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
            product=product,
        )
    elif style in ("problem_solution", "drama"):
        scenes = build_problem_solution_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            custom_idea=custom_idea,
            product=product,
        )
    elif style in ("flow_cinematic", "flow", "tech_minimal"):
        scenes = build_flow_cinematic_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
        )
    elif style in ("lifestyle_edc", "lifestyle"):
        scenes = build_lifestyle_edc_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            custom_idea=custom_idea,
            product=product,
        )
    elif style == "hybrid":
        num_images = len(product.image_names) if product.image_names else 1
        scenes = [
            SceneDefinition(
                id=1,
                name="Hook - Nhu cầu & Trải nghiệm thực tế",
                kind="FLOW_AI",
                narrator_text=f"Bạn đang tìm một món đồ thật ưng ý và tiện dụng mỗi ngày? Cùng mình trải nghiệm {clean_title} này nhé!",
                overlay_title="TRẢI NGHIỆM THỰC TẾ",
                overlay_subtitle=clean_title[:28],
                image_index=0,
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Two stylish young Vietnamese friends discovering {clean_title} with genuine curiosity and excitement. "
                    f"Warm cozy ambient lighting, shot on 35mm lens. Mouth closed, no speaking. NO text overlays."
                ),
            ),
            SceneDefinition(
                id=2,
                name="Hero - Giới thiệu sản phẩm thật",
                kind="PRODUCT_PHOTO",
                narrator_text=f"Đây là {clean_title}, thiết kế thông minh, hoàn thiện cực kỳ chỉn chu.",
                overlay_title=clean_title[:28].upper(),
                overlay_subtitle="Chính Hãng - Hoàn Thiện Tỉ Mỉ",
                image_index=0,
            ),
            SceneDefinition(
                id=3,
                name="Tính năng nổi bật 1",
                kind="FLOW_AI",
                narrator_text=feat1_desc,
                overlay_title=feat1_title[:24].upper(),
                overlay_subtitle="Trải Nghiệm Vượt Trội",
                image_index=min(1, num_images - 1),
                prompt=(
                    f"Vertical 9:16 RAW cinematic video. Young expressive person smiling happily while using {clean_title} in modern setting. "
                    f"Natural cinematic lighting. Mouth closed, no speaking. NO fake packaging."
                ),
            ),
            SceneDefinition(
                id=4,
                name="Tính năng nổi bật 2 & Đánh giá tốt",
                kind="PRODUCT_PHOTO",
                narrator_text=f"{feat2_desc}. Sản phẩm được rất nhiều người dùng đánh giá tốt và tin tưởng sử dụng.",
                overlay_title=social_proof_title,
                overlay_subtitle=feat2_title[:24],
                image_index=min(2, num_images - 1),
            ),
        ]
    else:
        scenes = build_viral_hook_scenes(
            category=category,
            clean_title=clean_title,
            feat1_title=feat1_title,
            feat1_desc=feat1_desc,
            feat2_title=feat2_title,
            feat2_desc=feat2_desc,
            social_proof_title=social_proof_title,
            custom_idea=custom_idea,
            product=product,
        )

    return append_call_to_action(scenes, cta_mode, channel_name)


def load_or_create_storyboard(
    product: ProductInfo,
    storyboard_path: Path,
    style: str = "viral_hook",
    cta_mode: str = "yellow_cart",
    force: bool = False,
    custom_idea: Optional[str] = None,
    channel_name: str = DEFAULT_CHANNEL_NAME,
) -> List[SceneDefinition]:
    """Load existing storyboard JSON or generate a fresh one."""
    return storyboard_io.load_or_create(
        storyboard_path,
        generate=lambda: generate_dynamic_storyboard(
            product=product,
            style=style,
            cta_mode=cta_mode,
            custom_idea=custom_idea,
            channel_name=channel_name,
        ),
        force=force,
        metadata={"product_name": product.name, "slug": product.slug, "style": style, "cta_mode": cta_mode},
        min_scenes=MIN_STORYBOARD_SCENES,
    )
