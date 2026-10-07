"""Backward-compatible import path; the implementation lives in tools.common.tts."""
from tools.common.tts import TTSError, generate_speech, probe_audio_duration

__all__ = ["TTSError", "generate_speech", "probe_audio_duration"]
