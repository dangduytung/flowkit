"""Multi-Platform Caption & Metadata Generator for TikTok Ads (TikTok, Facebook Reels, YouTube Shorts)."""
from pathlib import Path
from typing import Dict, List, Optional

from tools.common.captions import feature_bullets, write_caption, write_caption_set
from tools.common.categories import category_meta
from tools.tiktok_ad.config import DEFAULT_CHANNEL_NAME, DEFAULT_CHANNEL_HANDLE
from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.storyboard import (
    SceneDefinition,
    clean_product_title,
    detect_product_category,
)


def create_tiktok_caption(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_path: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> str:
    """Generate high-CTR TikTok video description and hashtags for TikTok Shop."""
    clean_title = clean_product_title(product.name)
    category = detect_product_category(product.name, product.description_text)
    icon, theme = category_meta(category)

    price_str = f" với giá chỉ {product.price}" if product.price else ""
    bio_target = f"Bio {channel_handle}" if channel_handle else "Bio kênh"

    caption = f"""======================================================================
🎵 TIKTOK VIDEO & TIKTOK SHOP
======================================================================
📌 PHẦN 1: DÁN VÀO PHẦN MÔ TẢ (CAPTION TIKTOK)
(Ngắn gọn, giật tít, kích thích bấm vào giỏ hàng màu vàng)
----------------------------------------------------------------------
{icon} {clean_title}{price_str} - {theme}! 💡 Bấm ngay vào giỏ hàng màu vàng góc trái màn hình hoặc xem thêm tại {bio_target} nhé cả nhà! #TikTokShop #review #gocreview #learnontiktok #tienich #xuhuong #fyp #dcgr


----------------------------------------------------------------------
📌 PHẦN 2: BÌNH LUẬN ĐẦU TIÊN (GHIM COMMENT HOẶC GẮN GIỎ HÀNG)
----------------------------------------------------------------------
👉 Link sản phẩm chính hãng: {product.url or 'Xem tại link Bio đầu trang nha cả nhà!'}
(Khi đăng video: Nhớ bấm nút 'Thêm liên kết sản phẩm' để hiện Giỏ Hàng Màu Vàng ở góc dưới bên trái)
"""
    return write_caption(output_path, caption)


def create_facebook_caption(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_path: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> str:
    """Generate anti-reach-suppression Facebook Reels copy."""
    clean_title = clean_product_title(product.name)
    category = detect_product_category(product.name, product.description_text)
    icon, theme = category_meta(category)
    bullets_text = feature_bullets(scenes)

    follow_target = f" {channel_handle}" if channel_handle else " kênh"
    bio_target = f" trang {channel_handle}" if channel_handle else " trang"

    caption = f"""======================================================================
📘 FACEBOOK REELS & WATCH POST
======================================================================
📌 PHẦN 1: NỘI DUNG BÀI ĐĂNG (CAPTION BÀI VIẾT)
----------------------------------------------------------------------
{icon} {clean_title.upper()} - {theme.upper()}!

Khám phá trải nghiệm thực tế với món đồ tiện ích không thể thiếu:
{bullets_text}

👉 Chi tiết sản phẩm mình để ở phần BÌNH LUẬN ĐẦU TIÊN phía dưới bài viết nhé!
(Follow{follow_target} để săn thêm nhiều món đồ tiện ích mỗi ngày)
#reels #review #tienich #cuocsong

----------------------------------------------------------------------
📌 PHẦN 2: BÌNH LUẬN ĐẦU TIÊN (COMMENT GHIM)
----------------------------------------------------------------------
👉 Link sản phẩm và ưu đãi hôm nay ở đây nhé cả nhà:
🔗 {product.url or 'Đang cập nhật link...'}
(Hoặc xem tại link Bio{bio_target} nha!)
"""
    return write_caption(output_path, caption)


def create_youtube_shorts_caption(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_path: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> str:
    """Generate SEO-rich YouTube Shorts title, description, tags, and pinned comment."""
    clean_title = clean_product_title(product.name)
    bullets_text = feature_bullets(scenes)

    caption = f"""======================================================================
🔴 YOUTUBE SHORTS
======================================================================
📌 PHẦN 1: TIÊU ĐỀ VIDEO (TITLE - DƯỚI 100 KÝ TỰ, CÓ #SHORTS)
----------------------------------------------------------------------
{clean_title} - Món Đồ Tiện Ích Đáng Mua Nhất! #Shorts #Review


----------------------------------------------------------------------
📌 PHẦN 2: MÔ TẢ VIDEO (DESCRIPTION)
----------------------------------------------------------------------
Review trải nghiệm thực tế {clean_title} - Giải pháp cực kỳ tiện lợi cho cuộc sống và không gian của bạn.

Điểm nổi bật:
{bullets_text}

👉 Link sản phẩm chính hãng: Xem ở bình luận đã ghim phía dưới nhé!

#shorts #review #tienich #{clean_title.replace(' ', '').lower()}

----------------------------------------------------------------------
📌 PHẦN 3: BÌNH LUẬN GHIM (PINNED COMMENT)
----------------------------------------------------------------------
👉 Mọi người xem chi tiết sản phẩm và săn sale tại link này nha:
🔗 {product.url or 'Xem tại link mô tả kênh nha!'}

----------------------------------------------------------------------
📌 PHẦN 4: THẺ TAGS YOUTUBE
----------------------------------------------------------------------
review, review đồ tiện ích, tiện ích đời sống, {clean_title.lower()}, tiktok shop, shorts
"""
    return write_caption(output_path, caption)


def generate_all_platform_captions(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    final_dir: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
    variant_suffix: Optional[str] = None,
) -> Dict[str, Path]:
    """Write the Facebook Reels, TikTok and YouTube Shorts captions; returns their paths."""
    return write_caption_set(
        {"tiktok": create_tiktok_caption, "facebook": create_facebook_caption, "youtube": create_youtube_shorts_caption},
        product, scenes, final_dir, channel_name, channel_handle, variant_suffix,
    )
