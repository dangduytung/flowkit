"""Shopee entry points for scene assembly; the implementation lives in tools.common.media."""
from functools import partial

from tools.common.media import assembler as _assembler
from tools.common.media.assembler import (
    assemble_scene_clip,
    concat_audio_files,
    concat_scenes,
    create_silent_version,
)

export_voiceover_script = partial(_assembler.export_voiceover_script, default_scene_seconds=6.0)

__all__ = [
    "assemble_scene_clip",
    "concat_audio_files",
    "concat_scenes",
    "create_silent_version",
    "export_voiceover_script",
]
