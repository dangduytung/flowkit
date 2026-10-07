"""Product metadata read from a shop-scraper zip (photos, one video, description.txt)."""
from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from agent.utils.slugify import slugify
from tools.common.constants import IMAGE_SUFFIXES, TEXT_SUFFIXES, VIDEO_SUFFIXES

SLUG_SOURCE_MAX_CHARS = 60
FALLBACK_SLUG_SOURCE_MAX_CHARS = 40

# "Label:" prefixes in description.txt -> ProductInfo field. Shopee and TikTok
# scrapers use slightly different labels for the same fact.
DESCRIPTION_LABELS: dict[str, tuple[str, ...]] = {
    "name": ("Tên sản phẩm:",),
    "url": ("Link sản phẩm:",),
    "price": ("Giá:", "Giá bán:"),
    "seller": ("Shop:", "Người bán:"),
    "rating": ("Số sao:",),
    "review_count": ("Lượt đánh giá:",),
    "sold_count": ("Đã bán:",),
}


@dataclass
class ProductInfo:
    zip_path: Path
    slug: str
    name: str
    url: str = ""
    price: str = ""
    rating: str = ""
    review_count: str = ""
    sold_count: str = ""
    seller: str = ""
    description_text: str = ""
    image_names: list[str] = field(default_factory=list)
    video_name: Optional[str] = None


def parse_description(text: str) -> dict[str, str]:
    """Pick labelled fields out of description.txt; later lines win."""
    fields: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        for field_name, labels in DESCRIPTION_LABELS.items():
            label = next((lb for lb in labels if line.startswith(lb)), None)
            if label:
                fields[field_name] = line[len(label):].strip()
                break
    return fields


def parse_product_zip(zip_path: Path) -> ProductInfo:
    """Inspect a product zip and return its metadata and asset names."""
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    image_names: list[str] = []
    video_name: Optional[str] = None
    description = ""
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if lower.endswith(IMAGE_SUFFIXES):
                image_names.append(name)
            elif lower.endswith(VIDEO_SUFFIXES):
                video_name = name
            elif lower.endswith(TEXT_SUFFIXES):
                description = archive.read(name).decode("utf-8", errors="replace")

    fields = parse_description(description)
    name = fields.pop("name", zip_path.stem)
    slug = slugify(name[:SLUG_SOURCE_MAX_CHARS]) or slugify(zip_path.stem[:FALLBACK_SLUG_SOURCE_MAX_CHARS])
    return ProductInfo(
        zip_path=zip_path,
        slug=slug,
        name=name,
        description_text=description,
        image_names=sorted(image_names),
        video_name=video_name,
        **fields,
    )


__all__ = ["DESCRIPTION_LABELS", "ProductInfo", "parse_description", "parse_product_zip"]
