"""OmniVoice Client for calling custom VoiceStudio endpoint for TikTok Ads."""
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from tools.tiktok_ad.config import (
    OMNIVOICE_URL,
    OMNIVOICE_API_KEY,
    OMNIVOICE_PROFILE_ID,
    OMNIVOICE_SPEED,
)


def probe_audio_duration(file_path: Path) -> float:
    """Return the duration of an audio file in seconds via ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        print(f"[OmniVoice] Warning: ffprobe duration check failed for {file_path}: {e}")
        return 0.0


def generate_speech(
    text: str,
    output_path: Path,
    profile_id: Optional[str] = None,
    speed: Optional[float] = None,
    api_key: Optional[str] = None,
    url: Optional[str] = None,
    timeout: int = 45,
) -> float:
    """
    Generate speech using VoiceStudio / OmniVoice endpoint.
    Returns the duration of the generated audio in seconds.
    """
    endpoint = url or OMNIVOICE_URL
    token = api_key or OMNIVOICE_API_KEY
    profile = profile_id or OMNIVOICE_PROFILE_ID
    sp = speed if speed is not None else OMNIVOICE_SPEED

    if not endpoint:
        raise ValueError("OMNIVOICE_URL is not set. Please provide it in .env or pass as argument.")
    if not token:
        raise ValueError("OMNIVOICE_API_KEY is not set. Please provide it in .env or pass as argument.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    parts = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="text"',
        "",
        text,
    ]
    if profile:
        parts.extend([
            f"--{boundary}",
            'Content-Disposition: form-data; name="profile_id"',
            "",
            profile,
        ])
    if sp:
        parts.extend([
            f"--{boundary}",
            'Content-Disposition: form-data; name="speed"',
            "",
            str(sp),
        ])
    parts.extend([f"--{boundary}--", ""])

    body_bytes = "\r\n".join(parts).encode("utf-8")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FlowKit/1.0",
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(endpoint, data=body_bytes, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            with open(output_path, "wb") as f:
                f.write(data)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OmniVoice API error ({e.code} {e.reason}): {err_msg}") from e
    except Exception as e:
        raise RuntimeError(f"OmniVoice request failed: {e}") from e

    duration = probe_audio_duration(output_path)
    print(f"[OmniVoice] Generated {output_path.name} ({duration:.2f}s) for text: '{text[:40]}...'")
    return duration
