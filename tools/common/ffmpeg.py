"""Thin, typed wrappers around the ffmpeg / ffprobe CLIs and their argument conventions."""
from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

logger = logging.getLogger(__name__)

FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"


# --------------------------------------------------------------------------- running


def _run(cmd: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    # ffmpeg echoes filter args (Vietnamese drawtext) in UTF-8; the Windows default
    # codepage cannot decode that and would silently drop stderr.
    return subprocess.run(list(cmd), capture_output=True, text=True, encoding="utf-8", errors="replace", check=check)


def run_ffmpeg(args: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run ``ffmpeg -y <args>``; raises CalledProcessError (stderr attached) on failure."""
    return _run([FFMPEG_BIN, "-y", *args], check=check)


# --------------------------------------------------------------------------- probing


def _probe(path: Path, *args: str) -> str:
    return _run([FFPROBE_BIN, "-v", "error", *args, str(path)]).stdout.strip()


def probe_duration(path: Path) -> float:
    """Container duration in seconds. Raises if ffprobe fails or reports nothing."""
    return float(_probe(Path(path), "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1"))


def try_probe_duration(path: Path) -> Optional[float]:
    """Like ``probe_duration`` but returns None for unreadable media."""
    try:
        return probe_duration(path)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None


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


# --------------------------------------------------------------------------- arguments


@dataclass(frozen=True)
class EncodeProfile:
    """Codec settings shared by every rendered artifact."""

    video_codec: str = "libx264"
    preset: str = "fast"
    pix_fmt: str = "yuv420p"
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"
    sample_rate: int = 48000
    # Drop container tags (encoder strings, creation time) and write deterministic headers.
    strip_metadata: bool = True

    def video_args(self, preset: Optional[str] = None) -> list[str]:
        return ["-c:v", self.video_codec, "-preset", preset or self.preset, "-pix_fmt", self.pix_fmt]

    def audio_args(self) -> list[str]:
        return ["-c:a", self.audio_codec, "-b:a", self.audio_bitrate, "-ar", str(self.sample_rate)]

    def container_args(self) -> list[str]:
        return ["-map_metadata", "-1", "-fflags", "+bitexact"] if self.strip_metadata else []


DEFAULT_ENCODE = EncodeProfile()


def delogo_filter(spec: Optional[str]) -> Optional[str]:
    """Normalise ``"x=..:y=..:w=..:h=.."`` or ``"delogo=x=..."`` into a ``delogo=`` filter."""
    if not spec or not spec.strip():
        return None
    body = spec.strip()
    if body.startswith("delogo="):
        body = body[len("delogo="):]
    return f"delogo={body}"


def filter_path(path: Path) -> str:
    """Escape a filesystem path for use inside an ffmpeg filter argument (Windows drive colon)."""
    posix = Path(path).resolve().as_posix()
    if len(posix) >= 2 and posix[1] == ":":
        posix = posix[0] + r"\:" + posix[2:]
    return posix


def concat_list_line(path: Path) -> str:
    """One entry of an ffmpeg concat-demuxer list file."""
    return f"file '{Path(path).resolve().as_posix()}'\n"


__all__ = [
    "DEFAULT_ENCODE",
    "EncodeProfile",
    "FFMPEG_BIN",
    "FFPROBE_BIN",
    "concat_list_line",
    "delogo_filter",
    "file_is_ready",
    "filter_path",
    "has_audio_stream",
    "probe_dimensions",
    "probe_duration",
    "run_ffmpeg",
    "try_probe_duration",
]
