"""Video Assembler: binds TTS audio, burns text overlays, and stitches scenes."""
import subprocess
from pathlib import Path
from typing import List, Optional


def assemble_scene_clip(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    title_text: Optional[str] = None,
    subtitle_text: Optional[str] = None,
    audio_duration: Optional[float] = None,
    pad_tail: float = 0.4,
) -> Path:
    """
    Combines video clip with audio, trims/loops video to fit audio, and burns text overlays.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine duration
    if audio_duration is None:
        cmd_probe = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
        ]
        res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        audio_duration = float(res.stdout.strip())

    total_duration = audio_duration + pad_tail

    # Filters for text overlays
    filters = []
    # Loop video if shorter than audio
    filters.append(f"loop=loop=-1:size=3000:start=0")
    filters.append(f"trim=duration={total_duration:.2f}")

    # Text overlays (Top badge & feature tag)
    # Using Arial/Segoe UI with clean box styling
    if title_text:
        safe_title = title_text.replace(":", "\\:").replace("'", "\\'")
        filters.append(
            f"drawtext=text='{safe_title}':font='Segoe UI':fontsize=38:fontcolor=yellow:"
            f"box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=140"
        )
    if subtitle_text:
        safe_sub = subtitle_text.replace(":", "\\:").replace("'", "\\'")
        filters.append(
            f"drawtext=text='{safe_sub}':font='Segoe UI':fontsize=26:fontcolor=white:"
            f"box=1:boxcolor=black@0.5:boxborderw=8:x=(w-text_w)/2:y=210"
        )

    vf_str = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-vf", vf_str,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def concat_scenes(clip_paths: List[Path], output_path: Path, bgm_path: Optional[Path] = None) -> Path:
    """
    Concatenate all assembled scene clips into the final video, with optional background music.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    concat_list_file = output_path.parent / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            # Format path for ffmpeg concat
            f.write(f"file '{p.resolve().as_posix()}'\n")

    temp_concat = output_path.parent / "temp_concat.mp4"

    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(temp_concat)
    ]
    subprocess.run(cmd_concat, capture_output=True, text=True, check=True)

    if bgm_path and Path(bgm_path).exists():
        # Mix background music at low volume (ducked)
        cmd_bgm = [
            "ffmpeg", "-y",
            "-i", str(temp_concat),
            "-i", str(bgm_path),
            "-filter_complex",
            "[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];"
            "[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ]
        subprocess.run(cmd_bgm, capture_output=True, text=True, check=True)
        if temp_concat.exists():
            temp_concat.unlink()
    else:
        temp_concat.replace(output_path)

    print(f"[Assembler] Video successfully assembled to: {output_path}")
    return output_path
