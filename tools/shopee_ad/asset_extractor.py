"""Asset Extractor and Preprocessor for Shopee Video & Images."""
import zipfile
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

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
    glitch_intervals: Optional[list[tuple[float, float]]] = None,
    delogo: Optional[str] = None,
) -> Path:
    """
    Slice a sub-clip and format it into 9:16 vertical video.
    Safely avoids cutting through detected glitch / rapid-flash intervals.
    Applies delogo filter if delogo parameter string is provided (e.g. 'x=30:y=545:w=140:h=60').
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if delogo:
        delogo_clean = delogo[7:] if delogo.startswith("delogo=") else delogo
        delogo_prefix = f"delogo={delogo_clean},"
    else:
        delogo_prefix = ""

    # Detect source orientation to avoid redundant blur on vertical videos
    is_vertical = False
    try:
        cmd_p = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0", str(src_video)
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
        vf = f"{delogo_prefix}scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},{pts_filter}"
    elif mode == "blur_bg":
        vf = (
            f"[0:v]{delogo_prefix}split=2[v1][v2];"
            f"[v1]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=25:5[bg];"
            f"[v2]scale={width}:-1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,{pts_filter}"
        )
    else:  # center_crop
        crop_w = int(height * 9 / 16)
        vf = f"{delogo_prefix}crop={crop_w}:in_h:(in_w-{crop_w})/2:0,scale={width}:{height},{pts_filter}"

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-t", str(cap_src_dur),
        "-i", str(src_video),
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
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


def create_hybrid_subclip(
    image_path: Path,
    video_path: Path,
    img_duration: float,
    vid_start_sec: float,
    vid_duration: float,
    output_path: Path,
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
    mode: str = "blur_bg",
    delogo: Optional[str] = None,
) -> Path:
    """
    Seamlessly combines an animated Ken Burns product still slide with an authentic video subclip.
    Used when raw video footage is shorter than narration to prevent repetitive looping.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_path.parent / "_temp_hybrid"
    temp_dir.mkdir(parents=True, exist_ok=True)

    part1 = temp_dir / f"{output_path.stem}_slide.mp4"
    part2 = temp_dir / f"{output_path.stem}_vid.mp4"

    create_image_slide_clip(image_path, img_duration, part1, width=width, height=height, fps=fps)
    extract_vertical_subclip(
        video_path,
        vid_start_sec,
        vid_duration,
        part2,
        width=width,
        height=height,
        fps=fps,
        mode=mode,
        delogo=delogo,
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(part1),
        "-i", str(part2),
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    try:
        part1.unlink(missing_ok=True)
        part2.unlink(missing_ok=True)
        if not any(temp_dir.iterdir()):
            temp_dir.rmdir()
    except Exception:
        pass

    return output_path


def calculate_smart_subclip_starts(
    video_path: Path,
    num_scenes: int,
    total_dur: float,
    scene_durations: Optional[List[float]] = None,
) -> tuple[list[float], list[tuple[float, float]]]:
    """
    Detect shot transitions in the source video and select stable, distinct starting points.
    Guarantees that each scene receives a UNIQUE start point spaced across the entire video,
    preventing any scene from repeating footage (0% overlap).
    Returns (starts, glitch_intervals).
    """
    if total_dur <= 0 or num_scenes <= 0:
        return [0.0] * num_scenes, []
    if num_scenes == 1:
        return [0.0], []

    glitch_intervals: list[tuple[float, float]] = []
    cuts = [0.0]
    try:
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vf", r"select=gt(scene\,0.25),metadata=print",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        for line in res.stderr.splitlines():
            if "pts_time:" in line:
                try:
                    t = float(line.split("pts_time:")[1].strip())
                    if t > cuts[-1] + 0.3:
                        cuts.append(t)
                except Exception:
                    pass
        cuts.append(total_dur)
    except Exception:
        pass

    # If scene_durations are provided and fit within total_dur
    total_required = sum(scene_durations) if scene_durations else 0.0
    if scene_durations and len(scene_durations) == num_scenes and total_required <= total_dur:
        selected_starts = []
        current_cursor = 0.0
        for idx in range(num_scenes):
            if idx == 0:
                selected_starts.append(0.0)
                current_cursor += scene_durations[0]
                continue
            valid_cuts = [c for c in cuts if current_cursor - 0.8 <= c <= current_cursor + 1.2 and c + scene_durations[idx] <= total_dur]
            if valid_cuts:
                chosen = min(valid_cuts, key=lambda c: abs(c - current_cursor))
            else:
                chosen = current_cursor
            selected_starts.append(round(chosen, 2))
            current_cursor = chosen + scene_durations[idx]
        return selected_starts[:num_scenes], glitch_intervals

    # If total_dur is shorter than required narration, partition total_dur proportionally
    # across num_scenes to strictly avoid overlapping footage
    interval = total_dur / num_scenes
    selected_starts = [0.0]
    for idx in range(1, num_scenes):
        target_t = idx * interval
        min_bound = selected_starts[-1] + max(1.0, interval * 0.4)
        max_bound = min(total_dur - 0.5, (idx + 1) * interval if idx + 1 < num_scenes else total_dur)
        valid_cuts = [c for c in cuts if min_bound <= c <= max_bound]
        if valid_cuts:
            best_cut = min(valid_cuts, key=lambda c: abs(c - target_t))
        else:
            best_cut = min(max_bound, max(min_bound, target_t))
        selected_starts.append(round(best_cut, 2))

    return selected_starts[:num_scenes], glitch_intervals



