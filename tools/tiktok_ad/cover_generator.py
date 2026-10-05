"""Cover / Thumbnail Generator for TikTok Ads."""
import subprocess
from pathlib import Path
from typing import List, Optional

from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.storyboard import SceneDefinition, clean_product_title


def _format_ffmpeg_path(path: Path) -> str:
    """Format a Path for FFmpeg filter argument (handling Windows colons)."""
    p = path.resolve().as_posix()
    if len(p) >= 2 and p[1] == ":":
        p = p[0] + r"\:" + p[2:]
    return p


def _format_cover_text(text: str, max_chars: int = 38) -> str:
    """Format and safely trim text to fit cover banner without cutting words in half."""
    text = text.strip()
    if len(text) <= max_chars:
        return text.upper()
    truncated = text[:max_chars]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated.upper().strip()


def create_cover_image(
    source_clip_or_video: Path,
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_cover_path: Path,
    time_offset_s: float = 1.2,
    delogo: Optional[str] = None,
) -> Path:
    """
    Extract a high-impact 9:16 frame from the video/scene and burn an eye-catching
    thumbnail banner (Hook Title + Product Name/Subtitle) for TikTok grid.
    """
    output_cover_path = Path(output_cover_path)
    output_cover_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_cover_path.parent

    # Determine title & subtitle
    clean_title = clean_product_title(product.name)
    hook_title = "SIÊU PHẨM TIỆN ÍCH"
    if scenes and scenes[0].overlay_title:
        hook_title = scenes[0].overlay_title

    hook_title = _format_cover_text(hook_title, max_chars=26)
    subtitle = _format_cover_text(clean_title, max_chars=38)

    if len(hook_title) > 22:
        hook_fontsize = 44
    elif len(hook_title) > 16:
        hook_fontsize = 50
    else:
        hook_fontsize = 54

    if len(subtitle) > 32:
        sub_fontsize = 26
    elif len(subtitle) > 24:
        sub_fontsize = 28
    else:
        sub_fontsize = 32

    font_path = Path("C:/Windows/Fonts/arialbd.ttf")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/segoeui.ttf")
    font_spec = (
        f"fontfile='{_format_ffmpeg_path(font_path)}'"
        if font_path.exists()
        else "font='Arial'"
    )

    title_file = temp_dir / f"{output_cover_path.stem}_title.txt"
    title_file.write_text(hook_title.strip(), encoding="utf-8")
    title_ff = _format_ffmpeg_path(title_file)

    sub_file = temp_dir / f"{output_cover_path.stem}_sub.txt"
    sub_file.write_text(subtitle.strip(), encoding="utf-8")
    sub_ff = _format_ffmpeg_path(sub_file)

    filters = []
    if delogo:
        filters.append(delogo)
    filters.extend([
        f"drawtext=textfile='{title_ff}':{font_spec}:fontsize={hook_fontsize}:fontcolor=yellow:borderw=4:bordercolor=black:box=1:boxcolor=black@0.75:boxborderw=16:x=(w-text_w)/2:y=180",
        f"drawtext=textfile='{sub_ff}':{font_spec}:fontsize={sub_fontsize}:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=280",
    ])

    vf_str = ",".join(filters)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{time_offset_s:.2f}",
        "-i",
        str(source_clip_or_video),
        "-vf",
        vf_str,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_cover_path),
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)

    for tf in [title_file, sub_file]:
        if tf.exists():
            tf.unlink()

    print(f"[Cover] Đã tạo ảnh bìa TikTok Ads: {output_cover_path.name}")
    return output_cover_path
