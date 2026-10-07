"""Multi-Platform Caption & Metadata Generator (Facebook Reels, TikTok, YouTube Shorts)."""
from pathlib import Path
from typing import Dict, List, Optional

from tools.common.captions import feature_bullets, write_caption, write_caption_set
from tools.common.categories import category_meta
from tools.shopee_ad.config import DEFAULT_CHANNEL_NAME, DEFAULT_CHANNEL_HANDLE
from tools.shopee_ad.product_parser import ProductInfo
from tools.shopee_ad.storyboard import SceneDefinition, clean_product_title, detect_product_category


def create_facebook_caption(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_path: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> str:
    """Generate anti-reach-suppression Facebook Reels copy (caption + pinned comment)."""
    clean_title = clean_product_title(product.name)
    category = detect_product_category(product.name, product.description_text)
    icon, theme = category_meta(category)
    bullets_text = feature_bullets(scenes)

    if product.rating:
        social_proof = f"⭐ Đánh giá uy tín {product.rating} sao từ người tiêu dùng!"
    else:
        social_proof = "⭐ Sản phẩm chất lượng được đông đảo khách hàng tin dùng!"

    channel_header = f"[{channel_name.upper()}] " if channel_name else ""
    follow_target = f" {channel_handle}" if channel_handle else " kênh"
    bio_target = f" trang {channel_handle}" if channel_handle else " trang"

    caption = f"""======================================================================
📘 FACEBOOK REELS & WATCH POST
======================================================================
📌 PHẦN 1: DÁN VÀO PHẦN MÔ TẢ (CAPTION) KHI ĐĂNG BÀI
(Không chứa link ngoài -> Giữ 100% phân phối thuật toán Reels, không bị bóp reach)
----------------------------------------------------------------------
{icon} {channel_header}{clean_title.upper()} - {theme.upper()}! 💡

Bạn đang tìm kiếm giải pháp giúp cuộc sống tiện nghi, ngăn nắp và tiết kiệm thời gian hơn? Xem ngay món đồ cực hot này nhé!

✨ Điểm nổi bật không thể bỏ qua:
{bullets_text}
{f'{social_proof}' if social_proof else ''}

👉 Link tham khảo và săn deal chính hãng mình để dưới phần BÌNH LUẬN (Comment ghim) nhé cả nhà!
👉 Bấm Follow{follow_target} để bỏ túi thêm nhiều món đồ tiện ích thông minh và mẹo hay cho không gian sống mỗi ngày!

#giadungthongminh #meovatcuocsong #decorphong #review #lifestyle #xuhuong #reelsvn #tienich


----------------------------------------------------------------------
📌 PHẦN 2: DÁN VÀO BÌNH LUẬN ĐẦU TIÊN (VÀ BẤM GHIM BÌNH LUẬN / PIN COMMENT)
(Cách chuẩn của các KOC triệu view để điều hướng mua hàng an toàn)
----------------------------------------------------------------------
👉 Link sản phẩm chính hãng và mã giảm giá hôm nay ở đây nhé cả nhà:
🔗 {product.url or 'Đang cập nhật link Shopee...'}
(Nếu link không bấm được trên điện thoại, các bạn có thể vào Bio{bio_target} để lấy link nha!)
"""
    return write_caption(output_path, caption)


def create_tiktok_caption(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_path: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> str:
    """Generate high-CTR TikTok video description and hashtags (under 150 chars for mobile fit)."""
    clean_title = clean_product_title(product.name)
    category = detect_product_category(product.name, product.description_text)
    icon, theme = category_meta(category)

    bio_target = f"Bio {channel_handle}" if channel_handle else "Bio kênh"

    caption = f"""======================================================================
🎵 TIKTOK VIDEO & TIKTOK SHOP
======================================================================
📌 PHẦN 1: DÁN VÀO PHẦN MÔ TẢ (CAPTION TIKTOK)
(Ngắn gọn, giật tít, kích thích bấm vào xem và vào Bio)
----------------------------------------------------------------------
{icon} {clean_title} - Món đồ tiện ích cứu cánh không thể thiếu! 💡 Xem chi tiết và săn deal tại link {bio_target} nhé cả nhà! #review #gocreview #learnontiktok #giadungthongminh #tienich #xuhuong #fyp #dcgr


----------------------------------------------------------------------
📌 PHẦN 2: BÌNH LUẬN ĐẦU TIÊN (GHIM COMMENT HOẶC GẮN GIỎ HÀNG)
----------------------------------------------------------------------
👉 Link săn sale chính hãng: {product.url or 'Xem tại link Bio đầu trang nha cả nhà!'}
(Nếu có TikTok Shop: Bấm nút 'Thêm liên kết sản phẩm' vào giỏ hàng màu vàng ở góc dưới video)
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
    category = detect_product_category(product.name, product.description_text)
    icon, theme = category_meta(category)
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
{icon} Khám phá {clean_title} - {theme}!

✨ Tính năng nổi bật:
{bullets_text}

🛒 Mua hàng chính hãng kèm mã giảm giá hôm nay:
🔗 {product.url or 'Xem link mua hàng tại bình luận ghim bên dưới!'}

Đừng quên bấm LIKE và ĐĂNG KÝ KÊNH để cập nhật thêm nhiều video review đồ gia dụng & công nghệ tiện ích mỗi ngày nhé!

#Shorts #Review #GiaDungThongMinh #TienIch #CongNghe


----------------------------------------------------------------------
📌 PHẦN 3: BÌNH LUẬN GHIM (PINNED COMMENT)
----------------------------------------------------------------------
👉 Link mua sản phẩm chính hãng và nhận ưu đãi ở đây nhé cả nhà:
🔗 {product.url or 'Đang cập nhật link mua hàng...'}


----------------------------------------------------------------------
📌 PHẦN 4: THẺ TAGS YOUTUBE (COPY DÁN VÀO Ô TAGS)
----------------------------------------------------------------------
review, review đồ gia dụng, đồ gia dụng thông minh, tiện ích đời sống, {clean_title.lower()}, mua hàng shopee, review shopee, shorts
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
        {"facebook": create_facebook_caption, "tiktok": create_tiktok_caption, "youtube": create_youtube_shorts_caption},
        product, scenes, final_dir, channel_name, channel_handle, variant_suffix,
    )
