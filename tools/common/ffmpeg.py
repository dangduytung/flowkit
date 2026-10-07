"""Thin, typed wrappers around the ffmpeg / ffprobe CLIs."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)

FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"


def _run(cmd: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    # ffmpeg echoes filter args (Vietnamese drawtext) in UTF-8; the Windows default
    # codepage cannot decode that and would silently drop stderr.
    return subprocess.run(list(cmd), capture_output=True, text=True, encoding="utf-8", errors="replace", check=check)


def run_ffmpeg(args: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run ``ffmpeg -y <args>``; raises CalledProcessError (stderr attached) on failure."""
    return _run([FFMPEG_BIN, "-y", *args], check=check)


def _probe(path: Path, *args: str) -> str:
    return _run([FFPROBE_BIN, "-v", "error", *args, str(path)]).stdout.strip()


def probe_duration(path: Path) -> float:
    """Container duration in seconds. Raises if ffprobe fails or reports nothing."""
    return float(_probe(Path(path), "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1"))


def probe_dimensions(path: Path) -> tuple[int, int]:
    """(width, height) of the first video stream."""
    out = _probe(Path(path), "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0")
    width, height = (int(x) for x in out.split(",")[:2])
    return width, height


def has_audio_stream(path: Path) -> bool:
    """True when the file carries at least one audio stream."""
    try:
        return bool(_probe(Path(path), "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0"))
    except (subprocess.CalledProcessError, OSError):
        return False


def file_is_ready(path: Path, min_bytes: int) -> bool:
    """A previously rendered artifact counts as usable once it exists with a plausible size."""
    path = Path(path)
    return path.is_file() and path.stat().st_size >= min_bytes


__all__ = [
    "FFMPEG_BIN",
    "FFPROBE_BIN",
    "file_is_ready",
    "has_audio_stream",
    "probe_dimensions",
    "probe_duration",
    "run_ffmpeg",
]
