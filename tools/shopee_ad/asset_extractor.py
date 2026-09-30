"""Asset Extractor and Preprocessor for Shopee Video & Images."""
import zipfile
import subprocess
from pathlib import Path

def extract_zip(zip_path: Path, dest_dir: Path) -> dict:
    """
    Extract images, video, and description from the Shopee product zip.
    Returns a dictionary of extracted file paths.
    """
    src_zip = Path(zip_path)
    if not src_zip.exists():
        raise FileNotFoundError(f"Shopee zip file not found at: {src_zip}")

    target_dir = Path(dest_dir)
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    extracted = {"images": [], "video": None, "description": None}

    with zipfile.ZipFile(src_zip) as z:
        for name in z.namelist():
            lower = name.lower()
            if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
                out_file = images_dir / Path(name).name
                with open(out_file, "wb") as f:
                    f.write(z.read(name))
                extracted["images"].append(out_file)
            elif lower.endswith(".mp4"):
                out_file = target_dir / "raw_video.mp4"
                with open(out_file, "wb") as f:
                    f.write(z.read(name))
                extracted["video"] = out_file
            elif lower.endswith(".txt"):
                out_file = target_dir / "description.txt"
                with open(out_file, "wb") as f:
                    f.write(z.read(name))
                extracted["description"] = out_file

    print(f"[Extractor] Extracted {len(extracted['images'])} images, video: {extracted['video']}, text: {extracted['description']}")
    return extracted


def extract_vertical_subclip(
    src_video: Path,
    start_sec: float,
    duration: float,
    output_path: Path,
    mode: str = "blur_bg",  # "blur_bg" or "center_crop"
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
) -> Path:
    """
    Slice a sub-clip and format it into 9:16 vertical video.
    Modes:
      - 'blur_bg': Centered 16:9 clip with blurred top/bottom background (E-commerce standard).
      - 'center_crop': Direct center crop to 9:16.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if mode == "blur_bg":
        vf = (
            f"[0:v]split=2[v1][v2];"
            f"[v1]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=25:5[bg];"
            f"[v2]scale={width}:-1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )
    else:  # center_crop
        crop_w = int(height * 9 / 16)
        vf = f"crop={crop_w}:in_h:(in_w-{crop_w})/2:0,scale={width}:{height}"

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-t", str(duration),
        "-i", str(src_video),
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-an",  # strip original audio, narrator TTS will be added
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def create_image_slide_clip(
    image_path: Path,
    duration: float,
    output_path: Path,
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
) -> Path:
    """
    Convert a still product photo into a subtle Ken-Burns animated 9:16 vertical clip.
    Used when a product has no video or for showcase stills.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames = max(30, int(duration * fps))

    # Fast blurred 9:16 background + centered product image + smooth Ken Burns zoompan
    vf = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},boxblur=15:2[bg];"
        f"[0:v]scale={width-60}:{height-380}:force_original_aspect_ratio=decrease[fg_img];"
        f"[bg][fg_img]overlay=(W-w)/2:(H-h)/2[merged];"
        f"[merged]zoompan=z='min(zoom+0.0008,1.06)':d={frames}:s={width}x{height}:fps={fps}[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(image_path),
        "-filter_complex", vf,
        "-map", "[v]",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path
