"""Asset Extractor and Preprocessor for TikTok Video & Images."""
import subprocess
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple


def extract_zip(zip_path: Path, dest_dir: Path) -> dict:
    """
    Extract images, video, and description from the TikTok product zip.
    Returns a dictionary of extracted file paths.
    """
    src_zip = Path(zip_path)
    if not src_zip.exists():
        raise FileNotFoundError(f"TikTok zip file not found at: {src_zip}")

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

    print(
        f"[Extractor] Extracted {len(extracted['images'])} images, video: {extracted['video']}, text: {extracted['description']}"
    )
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
    glitch_intervals: Optional[List[Tuple[float, float]]] = None,
) -> Path:
    """
    Slice a sub-clip and format it into 9:16 vertical video.
    Safely avoids cutting through detected glitch / rapid-flash intervals.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Detect source orientation to avoid redundant blur on vertical videos
    is_vertical = False
    try:
        cmd_p = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(src_video),
        ]
        res_p = subprocess.run(cmd_p, capture_output=True, text=True, check=True)
        w_s, h_s = [int(x) for x in res_p.stdout.strip().split(",")]
        if h_s >= w_s * 1.3:
            is_vertical = True
    except Exception:
        is_vertical = False

    # Check if this slice would enter a known glitch / rapid flash cut zone
    cap_src_dur = duration
    if glitch_intervals:
        for gs, ge in glitch_intervals:
            if start_sec < gs and start_sec + duration > gs:
                cap_src_dur = max(1.5, gs - 0.2 - start_sec)
                break

    # Determine PTS speed adjustment if capped before a glitch zone
    if cap_src_dur < duration - 0.1:
        pts_factor = duration / cap_src_dur
        pts_filter = f"setpts={pts_factor:.4f}*PTS,fps={fps}"
    else:
        pts_filter = f"fps={fps},setpts=PTS-STARTPTS"

    if is_vertical:
        vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},{pts_filter}"
    elif mode == "blur_bg":
        vf = (
            f"[0:v]split=2[v1][v2];"
            f"[v1]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=25:5[bg];"
            f"[v2]scale={width}:-1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,{pts_filter}"
        )
    else:  # center_crop
        crop_w = int(height * 9 / 16)
        vf = f"crop={crop_w}:in_h:(in_w-{crop_w})/2:0,scale={width}:{height},{pts_filter}"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_sec),
        "-t",
        str(cap_src_dur),
        "-i",
        str(src_video),
        "-avoid_negative_ts",
        "make_zero",
        "-fflags",
        "+genpts",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-an",  # strip original audio, narrator TTS will be added
        str(output_path),
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
        "ffmpeg",
        "-y",
        "-i",
        str(image_path),
        "-filter_complex",
        vf,
        "-map",
        "[v]",
        "-t",
        f"{duration:.2f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def calculate_smart_subclip_starts(
    video_path: Path, num_scenes: int, total_dur: float
) -> Tuple[List[float], List[Tuple[float, float]]]:
    """
    Detect shot transitions in the source video and select stable, clean starting points.
    Identifies and blacklists micro-cut clusters (adjacent cuts < 1.8s apart, such as rapid flashes),
    allocating scene clips strictly inside clean, steady continuous segments.
    Returns (starts, glitch_intervals).
    """
    if total_dur <= 0 or num_scenes <= 0:
        return [0.0] * num_scenes, []

    glitch_intervals: List[Tuple[float, float]] = []
    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            r"select=gt(scene\,0.25),metadata=print",
            "-f",
            "null",
            "-",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        cuts = [0.0]
        for line in res.stderr.splitlines():
            if "pts_time:" in line:
                try:
                    t = float(line.split("pts_time:")[1].strip())
                    if t > cuts[-1] + 0.1:
                        cuts.append(t)
                except Exception:
                    pass
        cuts.append(total_dur)

        # Detect glitch/flash clusters where adjacent cuts are closer than 1.8s
        in_glitch = False
        glitch_start = 0.0

        for i in range(len(cuts) - 1):
            d = cuts[i + 1] - cuts[i]
            if d < 1.8:
                if not in_glitch:
                    glitch_start = cuts[i]
                    in_glitch = True
            else:
                if in_glitch:
                    glitch_intervals.append((glitch_start, cuts[i]))
                    in_glitch = False
        if in_glitch:
            glitch_intervals.append((glitch_start, cuts[-1]))

        # Find clean continuous segments outside glitch intervals
        clean_segments = []
        prev_end = 0.0
        for gs, ge in glitch_intervals:
            if gs - prev_end >= 2.0:
                clean_segments.append((prev_end, gs))
            prev_end = ge
        if total_dur - prev_end >= 2.0:
            clean_segments.append((prev_end, total_dur))

        if clean_segments:
            starts = [round(clean_segments[0][0], 2)]
            remaining = num_scenes - 1
            if remaining > 0:
                large_segs = [
                    seg for seg in clean_segments if (seg[1] - seg[0]) >= 3.0
                ]
                target_seg = (
                    large_segs[1]
                    if len(large_segs) > 1
                    else (large_segs[0] if large_segs else clean_segments[-1])
                )
                s_base, e_base = target_seg
                step = max(2.5, (e_base - s_base - 3.0) / max(1, remaining - 1))
                for i in range(remaining):
                    starts.append(
                        round(min(s_base + i * step, max(0.0, total_dur - 5.0)), 2)
                    )
            return starts[:num_scenes], glitch_intervals
    except Exception:
        pass

    # Fallback: even distribution across duration
    step = max(1.0, (total_dur - 5.0) / max(1, num_scenes - 1))
    return [
        round(min(i * step, max(0.0, total_dur - 5.0)), 2)
        for i in range(num_scenes)
    ], glitch_intervals
