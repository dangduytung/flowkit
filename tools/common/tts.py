"""OmniVoice (VoiceStudio) text-to-speech client."""
from __future__ import annotations

import logging
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Optional

from tools.common.ffmpeg import try_probe_duration
from tools.common.settings import service_settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_S = 45
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FlowKit/1.0"


class TTSError(RuntimeError):
    pass


def _multipart(fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----FlowKitBoundary{uuid.uuid4().hex}"
    lines: list[str] = []
    for name, value in fields.items():
        lines += [f"--{boundary}", f'Content-Disposition: form-data; name="{name}"', "", value]
    lines += [f"--{boundary}--", ""]
    return "\r\n".join(lines).encode("utf-8"), boundary


def probe_audio_duration(file_path: Path) -> float:
    """Duration in seconds, or 0.0 when the file is not readable audio."""
    return try_probe_duration(file_path) or 0.0


def generate_speech(
    text: str,
    output_path: Path,
    profile_id: Optional[str] = None,
    speed: Optional[float] = None,
    api_key: Optional[str] = None,
    url: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT_S,
) -> float:
    """Synthesize ``text`` to ``output_path`` and return its duration in seconds.

    Unset arguments fall back to the OMNIVOICE_* environment settings.
    """
    settings = service_settings()
    endpoint = url or settings.omnivoice_url
    token = api_key or settings.omnivoice_api_key
    profile = profile_id or settings.omnivoice_profile_id
    rate = speed if speed is not None else settings.omnivoice_speed
    if not endpoint:
        raise ValueError("OMNIVOICE_URL is not set. Please provide it in .env or pass as argument.")
    if not token:
        raise ValueError("OMNIVOICE_API_KEY is not set. Please provide it in .env or pass as argument.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fields = {"text": text}
    if profile:
        fields["profile_id"] = profile
    if rate:
        fields["speed"] = str(rate)
    body, boundary = _multipart(fields)
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            output_path.write_bytes(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise TTSError(f"OmniVoice API error ({exc.code} {exc.reason}): {detail}") from exc
    except (urllib.error.URLError, OSError) as exc:
        raise TTSError(f"OmniVoice request failed: {exc}") from exc

    duration = probe_audio_duration(output_path)
    if duration <= 0:
        # A 200 response that is not audio (e.g. a JSON error) would otherwise yield a 0s scene.
        raise TTSError(f"OmniVoice returned unreadable audio for {output_path.name}")
    logger.info("[OmniVoice] Generated %s (%.2fs) for text: '%s...'", output_path.name, duration, text[:40])
    return duration


__all__ = ["TTSError", "generate_speech", "probe_audio_duration"]
