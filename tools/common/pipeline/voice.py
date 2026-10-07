"""Narration step: one TTS file per scene, reusing untouched scenes on partial runs."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Sequence

from tools.common.ffmpeg import file_is_ready, probe_duration
from tools.common.models import SceneDefinition
from tools.common.pipeline.selection import SceneSelection

logger = logging.getLogger(__name__)

# Smallest WAV that can hold any speech; anything below is a failed/truncated write.
MIN_NARRATION_BYTES = 1000

# (text, output_path) -> duration in seconds
SpeechSynthesizer = Callable[[str, Path], float]


@dataclass
class NarrationResult:
    files: dict[int, Optional[Path]] = field(default_factory=dict)
    durations: dict[int, float] = field(default_factory=dict)


def narration_path(audio_dir: Path, variant: str, scene_id: int) -> Path:
    return Path(audio_dir) / f"{variant}_scene_{scene_id:02d}.wav"


def synthesize_narration(
    scenes: Sequence[SceneDefinition],
    audio_dir: Path,
    variant: str,
    synthesize: SpeechSynthesizer,
    selection: SceneSelection = SceneSelection(),
) -> NarrationResult:
    """Voice every scene. On a partial run, scenes outside the selection keep their audio."""
    result = NarrationResult()
    for scene in scenes:
        out_wav = narration_path(audio_dir, variant, scene.id)
        # A full run always re-voices: narrator text may have been edited in the storyboard.
        if selection.keep_existing(scene.id, file_is_ready(out_wav, MIN_NARRATION_BYTES), force_rebuild=True):
            duration = probe_duration(out_wav)
            print(f"  • Scene {scene.id}: Đã có audio sẵn ({duration:.2f}s), giữ nguyên.")
        else:
            print(f"  • Scene {scene.id}: {scene.overlay_title}")
            duration = synthesize(scene.narrator_text, out_wav)
        result.files[scene.id] = out_wav
        result.durations[scene.id] = duration
    return result


def silent_timing(scenes: Sequence[SceneDefinition], seconds_per_scene: float) -> NarrationResult:
    """Fixed per-scene timing for voiceless (POV) cuts."""
    result = NarrationResult()
    for scene in scenes:
        result.files[scene.id] = None
        result.durations[scene.id] = seconds_per_scene
    return result


__all__ = [
    "MIN_NARRATION_BYTES",
    "NarrationResult",
    "SpeechSynthesizer",
    "narration_path",
    "silent_timing",
    "synthesize_narration",
]
