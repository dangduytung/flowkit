"""Multi-Platform Publishing Guide Generator (Facebook Reels, TikTok, YouTube Shorts)."""
from pathlib import Path
from typing import Dict, List, Optional

from tools.shopee_ad.config import DEFAULT_CHANNEL_HANDLE
from tools.shopee_ad.product_parser import ProductInfo
from tools.shopee_ad.storyboard import SceneDefinition, clean_product_title


def create_publish_guide(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    video_paths: Dict[str, Path],  # e.g. {"flow": path_flow, "local": path_local} or single path
    cover_path: Path,
    caption_files: Dict[str, Path],  # {"facebook": fb_path, "tiktok": tt_path, "youtube": yt_path}
    output_guide_path: Path,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
    script_path: Optional[Path] = None,
    voiceover_path: Optional[Path] = None,
) -> Path:
    """Generate a comprehensive multi-platform publishing checklist (Facebook Reels, TikTok, YouTube Shorts)."""
    clean_title = clean_product_title(product.name)

    # Format video file listings
    video_lines = []
    if isinstance(video_paths, dict):
        for mode, p in video_paths.items():
            if p and p.exists():
                mode_desc = "AI Cinematic Hybrid (Google Flow + Ảnh thật)" if mode == "flow" else "100% Video gốc từ ZIP (Cắt ghép tối ưu)"
                video_lines.append(f"   • [{mode.upper()}]: {p.name} ({mode_desc})")
    elif isinstance(video_paths, (Path, str)):
        p = Path(video_paths)
        video_lines.append(f"   • {p.name}")

    video_list_str = "\n".join(video_lines) if video_lines else f"   • {product.slug}_flow.mp4"

    # Caption files listing
    caption_lines = []
    for platform, p in caption_files.items():
        caption_lines.append(f"   • {platform.capitalize()}: {p.name}")
    caption_list_str = "\n".join(caption_lines)

    # Audio & Script listing
    audio_script_lines = []
    if voiceover_path and Path(voiceover_path).exists():
        audio_script_lines.append(f"   • File Audio thuyết minh: {Path(voiceover_path).name} (MP3 48kHz, ghép liền mạch các cảnh)")
    if script_path and Path(script_path).exists():
        audio_script_lines.append(f"   • File Text kịch bản:      {Path(script_path).name} (Văn bản lời thoại & Timecode từng phân cảnh)")
    audio_script_str = "\n".join(audio_script_lines) if audio_script_lines else "   • (Đã tích hợp trong video)"

    header_title = f"HƯỚNG DẪN XUẤT BẢN ĐA NỀN TẢNG CHO KÊNH {channel_handle.upper()}" if channel_handle else "HƯỚNG DẪN XUẤT BẢN ĐA NỀN TẢNG"

    content = f"""======================================================================
🚀 {header_title}
(Facebook Reels • TikTok • YouTube Shorts)
======================================================================

📦 Sản phẩm: {clean_title}
📁 Các file thành phẩm sẵn sàng trong thư mục 'final/':

🎬 VIDEO THÀNH PHẨM (CHUẨN DỌC 9:16, 30FPS, DELOGO 100%):
{video_list_str}

🖼️ ẢNH BÌA CHUẨN THU NHỎ (THUMBNAIL / COVER 9:16):
   • {cover_path.name} (Hook nổi bật, không tên kênh, dùng chung mọi nền tảng)

🎙️ FILE AUDIO THUYẾT MINH & KỊCH BẢN LỜI THOẠI:
{audio_script_str}

📝 FILE NỘI DUNG & CAPTION ĐÃ SOẠN SẴN:
{caption_list_str}

----------------------------------------------------------------------
⏰ KHUNG GIỜ VÀNG ĐỀ XUẤT ĐĂNG BÀI:
   • Buổi trưa: 11:30 – 12:30 (Dân văn phòng & học sinh nghỉ trưa lướt feed)
   • Buổi tối:  19:30 – 20:30 (Khung giờ vàng lưu lượng cao nhất trong ngày)

----------------------------------------------------------------------
💡 CHIẾN LƯỢC A/B TESTING KHI CÓ CẢ 2 BẢN VIDEO (_FLOW & _LOCAL):
   • Bản [_FLOW]: Hình ảnh điện ảnh, tương tác cảm xúc ➔ Cực kỳ hút view trên Facebook Reels & Shorts.
   • Bản [_LOCAL]: Hình ảnh 100% người thật việc thật từ hãng ➔ Rất uy tín trên TikTok & giỏ hàng.
   👉 Bạn có thể đăng bản _FLOW lên Facebook Reels và bản _LOCAL lên TikTok để kiểm tra nguồn view!

======================================================================
📘 1. QUY TRÌNH ĐĂNG FACEBOOK REELS (CHỈ 1 PHÚT):
======================================================================
1. Mở Facebook hoặc Meta Business Suite ➔ Bấm "Tạo thước phim" (Create Reel).
2. Tải file Video (`..._flow.mp4` hoặc `..._local.mp4`) và chọn Ảnh bìa (`..._cover.jpg`).
3. Mở file caption `{caption_files.get('facebook', Path()).name}`:
   • Copy PHẦN 1 dán vào ô mô tả (TUYỆT ĐỐI không dán link ngoài vào đây để giữ 100% reach).
   • Bấm Đăng ngay.
4. Sau khi video lên sóng:
   • Copy PHẦN 2 (link Shopee Affiliate) dán vào bình luận đầu tiên ➔ Bấm "Ghim bình luận".

======================================================================
🎵 2. QUY TRÌNH ĐĂNG TIKTOK (CHỈ 1 PHÚT):
======================================================================
1. Mở TikTok trên điện thoại ➔ Bấm nút [+] đăng video.
2. Chọn file Video và chọn Ảnh bìa (Cover) ở phần đầu video.
3. Mở file caption `{caption_files.get('tiktok', Path()).name}`:
   • Copy nội dung ngắn gọn và bộ hashtag dán vào phần mô tả.
4. Điều hướng mua hàng:
   • Nếu có TikTok Shop: Bấm 'Thêm liên kết' ➔ Chọn sản phẩm gắn vào giỏ hàng vàng.
   • Nếu làm Shopee Affiliate: Hướng dẫn người xem bấm vào link Bio đầu trang.
5. Mẹo đẩy view: Thêm 1 bài nhạc đang thịnh hành (Trending Sound) trên TikTok, chỉnh âm lượng bài hát xuống 5-10% để giữ tiếng thuyết minh rõ ràng.

======================================================================
🔴 3. QUY TRÌNH ĐĂNG YOUTUBE SHORTS (CHỈ 1 PHÚT):
======================================================================
1. Mở YouTube Studio / App YouTube ➔ Bấm Tạo ➔ "Tạo video ngắn" / Tải video lên.
2. Mở file `{caption_files.get('youtube', Path()).name}`:
   • Copy TIÊU ĐỀ dán vào ô Tiêu đề (bắt buộc giữ thẻ #Shorts).
   • Copy MÔ TẢ dán vào ô Mô tả (có thể dán trực tiếp link Shopee ở đây).
   • Copy THẺ TAGS dán vào mục Thẻ từ khóa (Tags) trong cài đặt nâng cao.
3. Bình luận ghim: Dán link Shopee vào bình luận đầu tiên và bấm Ghim để người xem dễ click.

======================================================================
Chúc bạn phân phối đa nền tảng bùng nổ view và ngập tràn đơn hàng! 🎉
"""
    output_guide_path = Path(output_guide_path)
    output_guide_path.parent.mkdir(parents=True, exist_ok=True)
    output_guide_path.write_text(content.strip(), encoding="utf-8")
    return output_guide_path
