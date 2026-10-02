"""Multi-Platform Publishing Guide Generator for TikTok Ads (TikTok, Facebook Reels, YouTube Shorts)."""
from pathlib import Path
from typing import Dict, List, Optional

from tools.tiktok_ad.config import DEFAULT_CHANNEL_HANDLE
from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.storyboard import SceneDefinition, clean_product_title


def create_publish_guide(
    product: ProductInfo,
    scenes: List[SceneDefinition],
    video_paths: Dict[str, Path],
    cover_path: Path,
    caption_files: Dict[str, Path],
    output_guide_path: Path,
    channel_handle: str = DEFAULT_CHANNEL_HANDLE,
    script_path: Optional[Path] = None,
    voiceover_path: Optional[Path] = None,
) -> Path:
    """Generate a comprehensive multi-platform publishing checklist."""
    clean_title = clean_product_title(product.name)

    # Format video file listings
    video_lines = []
    if isinstance(video_paths, dict):
        for mode, p in video_paths.items():
            if p and p.exists():
                if mode == "local":
                    desc = "Bản có thuyết minh OmniVoice (KOC Việt)"
                elif mode == "silent":
                    desc = "Bản tắt tiếng (Tự lồng nhạc trend trên TikTok)"
                elif mode == "flow":
                    desc = "AI Video Google Flow"
                else:
                    desc = "Video thành phẩm"
                video_lines.append(f"   • [{mode.upper()}]: {p.name} ({desc})")
    elif isinstance(video_paths, (Path, str)):
        p = Path(video_paths)
        video_lines.append(f"   • {p.name}")

    video_list_str = (
        "\n".join(video_lines) if video_lines else f"   • {product.slug}_local.mp4"
    )

    caption_lines = []
    for platform, p in caption_files.items():
        caption_lines.append(f"   • {platform.capitalize()}: {p.name}")
    caption_list_str = "\n".join(caption_lines)

    audio_script_lines = []
    if voiceover_path and Path(voiceover_path).exists():
        audio_script_lines.append(
            f"   • File Audio thuyết minh: {Path(voiceover_path).name} (MP3 48kHz)"
        )
    if script_path and Path(script_path).exists():
        audio_script_lines.append(
            f"   • File Text kịch bản:      {Path(script_path).name} (Lời thoại & Timecode)"
        )
    audio_script_str = (
        "\n".join(audio_script_lines)
        if audio_script_lines
        else "   • (Đã tích hợp trong video)"
    )

    header_title = (
        f"HƯỚNG DẪN XUẤT BẢN TIKTOK ADS CHO KÊNH {channel_handle.upper()}"
        if channel_handle
        else "HƯỚNG DẪN XUẤT BẢN TIKTOK ADS & TIKTOK SHOP"
    )

    content = f"""======================================================================
🚀 {header_title}
(TikTok Shop • Facebook Reels • YouTube Shorts)
======================================================================

📦 Sản phẩm: {clean_title}
📁 Các file thành phẩm sẵn sàng trong thư mục 'final/':

🎬 VIDEO THÀNH PHẨM (CHUẨN DỌC 9:16, 30FPS):
{video_list_str}

🖼️ ẢNH BÌA CHUẨN THU NHỎ (THUMBNAIL / COVER 9:16):
   • {cover_path.name} (Hook giữ chân, typography nổi bật)

🎙️ FILE AUDIO THUYẾT MINH & KỊCH BẢN LỜI THOẠI:
{audio_script_str}

📝 FILE NỘI DUNG & CAPTION ĐÃ SOẠN SẴN:
{caption_list_str}

----------------------------------------------------------------------
⏰ KHUNG GIỜ VÀNG ĐỀ XUẤT ĐĂNG TIKTOK:
   • Buổi trưa: 11:30 – 12:45 (Nghỉ trưa, lượng mua sắm TikTok Shop cao)
   • Buổi tối:  19:30 – 21:30 (Khung giờ vàng giải trí & chốt đơn cao nhất)

----------------------------------------------------------------------
💡 LỰA CHỌN BẢN VIDEO PHÙ HỢP:
   • Bản [_LOCAL]: Đã có sẵn giọng đọc thuyết minh KOC truyền cảm, đăng ngay không cần chỉnh sửa.
   • Bản [_SILENT]: Video tắt tiếng, dùng để chọn nhạc thịnh hành (Trending Sound) trực tiếp trên TikTok để kéo đề xuất thuật toán!

======================================================================
🎵 QUY TRÌNH ĐĂNG TIKTOK SHOP (CHỈ 1 PHÚT):
======================================================================
1. Mở app TikTok ➔ Bấm nút [+] đăng video.
2. Chọn file Video (`..._local.mp4` hoặc `..._silent.mp4`) và chọn Ảnh bìa (`..._cover.jpg`).
3. Mở file caption `{caption_files.get('tiktok', Path()).name}`:
   • Copy phần Caption dán vào ô mô tả video.
4. GẮN GIỎ HÀNG VÀNG TIKTOK SHOP:
   • Trước khi bấm Đăng, bấm vào "Thêm liên kết" (Add link) ➔ Chọn "Sản phẩm" (Product).
   • Tìm sản phẩm `{clean_title}` từ cửa hàng của bạn hoặc chiến dịch Affiliate ➔ Bấm "Thêm".
   • Đặt tên hiển thị ngắn gọn (ví dụ: {clean_title[:30]}).
5. Bấm Đăng video!
"""
    output_guide_path.write_text(content.strip(), encoding="utf-8")
    print(f"[PublishGuide] Đã tạo cẩm nang xuất bản: {output_guide_path.name}")
    return output_guide_path
