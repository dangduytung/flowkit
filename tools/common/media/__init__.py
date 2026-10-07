"""ffmpeg-based media building blocks shared by every ad pipeline."""
from tools.common.media.assembler import (
    assemble_scene_clip,
    concat_audio_files,
    concat_scenes,
    create_silent_version,
    export_voiceover_script,
)
from tools.common.media.cover import CoverStyle, create_cover_frame, format_cover_text
from tools.common.media.cutplanner import calculate_smart_subclip_starts, plan_subclip_starts
from tools.common.media.extractor import (
    ExtractedAssets,
    create_hybrid_subclip,
    create_image_slide_clip,
    extract_vertical_subclip,
    extract_zip,
)

__all__ = [
    "CoverStyle",
    "ExtractedAssets",
    "assemble_scene_clip",
    "calculate_smart_subclip_starts",
    "concat_audio_files",
    "concat_scenes",
    "create_cover_frame",
    "create_hybrid_subclip",
    "create_image_slide_clip",
    "create_silent_version",
    "export_voiceover_script",
    "extract_vertical_subclip",
    "extract_zip",
    "format_cover_text",
    "plan_subclip_starts",
]
