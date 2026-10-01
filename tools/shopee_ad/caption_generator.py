"""Multi-Platform Caption & Metadata Generator (Facebook Reels, TikTok, YouTube Shorts)."""
from pathlib import Path
from typing import Dict, List
from tools.shopee_ad.config import DEFAULT_CHANNEL_NAME, DEFAULT_CHANNEL_HANDLE
from tools.shopee_ad.product_parser import ProductInfo
from tools.shopee_ad.storyboard import SceneDefinition, clean_product_title, detect_product_category


def _get_category_meta(category: str):
    category_meta = {
        "BEAUTY_SKINCARE": ("💄", "Chăm sóc làn da rạng ngời & Tươi tắn"),
        "KITCHEN_HOME": ("🍳", "Gian bếp tinh tươm & Tiện nghi gia đình"),
        "FASHION_APPAREL": ("👗", "Thời trang thanh lịch & Tôn dáng tự nhiên"),
        "TECH_GADGETS": ("⚡", "Góc setup tối giản & Công nghệ đỉnh cao"),
        "HEALTH_FITNESS": ("🧘", "Chăm sóc sức khỏe & Thư giãn mỗi ngày"),
        "GENERAL_LIFESTYLE": ("🏠", "Giải pháp thông minh cho không gian sống"),
    }
    return category_meta.get(category, ("🏠", "Giải pháp tiện ích mỗi ngày"))


def _extract_bullets(scenes: List[SceneDefinition]) -> str:
    feat_lines = []
    for sc in scenes:
        if sc.overlay_title and sc.overlay_subtitle and sc.id in (2, 3, 4):
            feat_lines.append(f"• {sc.overlay_title}: {sc.overlay_subtitle}")
    if not feat_lines:
        feat_lines.append("• Thiết kế thông minh, hoàn thiện cao cấp")
        feat_lines.append("• Tiện lợi, bền bỉ và nâng tầm chất lượng sống")
    return "\n".join(feat_lines[:3])


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
    icon, theme = _get_category_meta(category)
    bullets_text = _extract_bullets(scenes)

    social_proof = ""
    has_strong_sales = False
    if product.sold_count:
        sold_clean = product.sold_count.lower().replace("+", "").replace(",", ".").strip()
        if "k" in sold_clean:
            has_strong_sales = True
        else:
            try:
                has_strong_sales = float(sold_clean) >= 50
            except ValueError:
                has_strong_sales = False

    if has_strong_sales:
        social_proof = f"⭐ Đã bán hơn {product.sold_count} lượt trên Shopee với đánh giá cực tốt!"
    elif product.rating:
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
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(caption.strip(), encoding="utf-8")
    return caption.strip()


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
    icon, theme = _get_category_meta(category)

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
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(caption.strip(), encoding="utf-8")
    return caption.strip()


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
    icon, theme = _get_category_meta(category)
    bullets_text = _extract_bullets(scenes)

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
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(caption.strip(), encoding="utf-8")
    return caption.strip()


def generate_all_platform_captions(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    final_dir: Path,
    channel_name: str = DEFAULT_CHANNEL_NAME,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
) -> Dict[str, Path]:
    """Generate all captions for Facebook Reels, TikTok, and YouTube Shorts."""
    final_dir = Path(final_dir)
    fb_path = final_dir / f"{product.slug}_facebook_caption.txt"
    tt_path = final_dir / f"{product.slug}_tiktok_caption.txt"
    yt_path = final_dir / f"{product.slug}_youtube_shorts.txt"

    create_facebook_caption(product, scenes, fb_path, channel_name, channel_handle)
    create_tiktok_caption(product, scenes, tt_path, channel_name, channel_handle)
    create_youtube_shorts_caption(product, scenes, yt_path, channel_name, channel_handle)

    return {
        "facebook": fb_path,
        "tiktok": tt_path,
        "youtube": yt_path,
    }
