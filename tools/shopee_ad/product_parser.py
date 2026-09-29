"""Parser for Shopee product zip files and description metadata."""
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from agent.utils.slugify import slugify


@dataclass
class ProductInfo:
    zip_path: Path
    slug: str
    name: str
    url: str = ""
    rating: str = ""
    review_count: str = ""
    sold_count: str = ""
    description_text: str = ""
    image_names: List[str] = field(default_factory=list)
    video_name: Optional[str] = None


def parse_product_zip(zip_path: Path) -> ProductInfo:
    """
    Inspect a Shopee zip file and extract product metadata and asset list.
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    image_names = []
    video_name = None
    desc_content = ""

    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            lower = name.lower()
            if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_names.append(name)
            elif lower.endswith(".mp4"):
                video_name = name
            elif lower.endswith(".txt"):
                try:
                    desc_content = z.read(name).decode("utf-8")
                except UnicodeDecodeError:
                    desc_content = z.read(name).decode("utf-8", errors="replace")

    # Parse metadata from description.txt
    product_name = zip_path.stem
    url = ""
    rating = ""
    reviews = ""
    sold = ""
    clean_desc = desc_content

    for line in desc_content.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("Tên sản phẩm:"):
            product_name = line_clean.replace("Tên sản phẩm:", "").strip()
        elif line_clean.startswith("Link sản phẩm:"):
            url = line_clean.replace("Link sản phẩm:", "").strip()
        elif line_clean.startswith("Số sao:"):
            rating = line_clean.replace("Số sao:", "").strip()
        elif line_clean.startswith("Lượt đánh giá:"):
            reviews = line_clean.replace("Lượt đánh giá:", "").strip()
        elif line_clean.startswith("Đã bán:"):
            sold = line_clean.replace("Đã bán:", "").strip()

    # Generate clean filesystem slug
    slug = slugify(product_name[:60])
    if not slug:
        slug = slugify(zip_path.stem[:40])

    return ProductInfo(
        zip_path=zip_path,
        slug=slug,
        name=product_name,
        url=url,
        rating=rating,
        review_count=reviews,
        sold_count=sold,
        description_text=clean_desc,
        image_names=sorted(image_names),
        video_name=video_name,
    )
