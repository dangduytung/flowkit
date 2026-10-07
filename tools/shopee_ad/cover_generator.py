"""Cover / Thumbnail Generator for Facebook Reels."""
import subprocess
from pathlib import Path
from typing import List, Optional

from tools.shopee_ad.product_parser import ProductInfo
from tools.shopee_ad.storyboard import SceneDefinition, clean_product_title


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
    has_question = text.endswith("?")
    has_exclamation = text.endswith("!")
    truncated = text[:max_chars]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    res = truncated.upper().strip()
    if has_question and not res.endswith("?"):
        res += "?"
    elif has_exclamation and not res.endswith("!"):
        res += "!"
    return res


def create_cover_image(
    source_clip_or_video: Path,
    product: ProductInfo,
    scenes: List[SceneDefinition],
    output_cover_path: Path,
    channel_badge: str = "",
    time_offset_s: float = 1.2,
    delogo: Optional[str] = None,
) -> Path:
    """
    Extract a high-impact 9:16 frame from the video/scene and burn an eye-catching
    thumbnail banner (Hook Title + Product Name/Subtitle) for Facebook Reels grid.
    """
    output_cover_path = Path(output_cover_path)
    output_cover_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_cover_path.parent

    # Determine title & subtitle
    clean_title = clean_product_title(product.name)
    hook_title = "SIÊU PHẨM TIỆN ÍCH"
    if scenes and scenes[0].overlay_title:
        hook_title = scenes[0].overlay_title

    # Keep text concise for bold cover typography without cutting words mid-spelling
    hook_title = _format_cover_text(hook_title, max_chars=34)
    subtitle = _format_cover_text(clean_title, max_chars=38)

    # Dynamic font sizing to ensure text never overflows 720px width
    if len(hook_title) > 26:
        hook_fontsize = 40
    elif len(hook_title) > 20:
        hook_fontsize = 46
    elif len(hook_title) > 14:
        hook_fontsize = 50
    else:
        hook_fontsize = 54

    if len(subtitle) > 32:
        sub_fontsize = 26
    elif len(subtitle) > 24:
        sub_fontsize = 28
    else:
        sub_fontsize = 32

    # Font detection (Arial Bold preferred, Segoe UI fallback)
    font_path = Path("C:/Windows/Fonts/arialbd.ttf")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/segoeui.ttf")
    font_spec = f"fontfile='{_format_ffmpeg_path(font_path)}'" if font_path.exists() else "font='Arial'"

    title_file = temp_dir / f"{output_cover_path.stem}_title.txt"
    title_file.write_text(hook_title.strip(), encoding="utf-8")
    title_ff = _format_ffmpeg_path(title_file)

    sub_file = temp_dir / f"{output_cover_path.stem}_sub.txt"
    sub_file.write_text(subtitle.strip(), encoding="utf-8")
    sub_ff = _format_ffmpeg_path(sub_file)

    filters = []
    if delogo:
        delogo_clean = delogo[7:] if delogo.startswith("delogo=") else delogo
        filters.append(f"delogo={delogo_clean}")
    else:
        filters.append("delogo=x=546:y=1120:w=68:h=104")

    # Add subtle sensor grain to cover delogo boundary and match realistic photography
    filters.append("noise=alls=5:allf=t")

    filters.extend([
        f"drawtext=textfile='{title_ff}':{font_spec}:fontsize={hook_fontsize}:fontcolor=yellow:borderw=4:bordercolor=black:box=1:boxcolor=black@0.75:boxborderw=16:x=(w-text_w)/2:y=180",
        f"drawtext=textfile='{sub_ff}':{font_spec}:fontsize={sub_fontsize}:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=280",
    ])

    vf_str = ",".join(filters)
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{time_offset_s:.2f}",
        "-i", str(source_clip_or_video),
        "-vf", vf_str,
        "-frames:v", "1",
        "-q:v", "2",
        "-map_metadata", "-1",
        str(output_cover_path),
    ]

    subprocess.run(cmd, capture_output=True, check=True)

    # Clean up temporary text files
    for f in [title_file, sub_file]:
        try:
            f.unlink()
        except Exception:
            pass

    return output_cover_path
