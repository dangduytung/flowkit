"""TikTok entry points for scene assembly; the implementation lives in tools.common.media."""
from functools import partial

from tools.common.media import assembler as _assembler
from tools.common.media.assembler import (
    assemble_scene_clip,
    concat_audio_files,
    concat_scenes,
    create_silent_version,
)

export_voiceover_script = partial(_assembler.export_voiceover_script, heading="KỊCH BẢN LỜI THOẠI & PHỤ ĐỀ TIKTOK")

__all__ = [
    "assemble_scene_clip",
    "concat_audio_files",
    "concat_scenes",
    "create_silent_version",
    "export_voiceover_script",
]
