"""TikTok content plugged into the shared ad pipelines."""
from tools.common.pipeline.context import PlatformHooks
from tools.tiktok_ad.caption_generator import generate_all_platform_captions
from tools.tiktok_ad.config import PROFILE
from tools.tiktok_ad.cover_generator import create_cover_image
from tools.tiktok_ad.publish_guide import create_publish_guide
from tools.tiktok_ad.storyboard import generate_dynamic_storyboard, load_or_create_storyboard
from tools.tiktok_ad.video_assembler import export_voiceover_script

HOOKS = PlatformHooks(
    load_storyboard=load_or_create_storyboard,
    generate_storyboard=generate_dynamic_storyboard,
    write_captions=generate_all_platform_captions,
    create_cover=create_cover_image,
    write_publish_guide=create_publish_guide,
    export_script=export_voiceover_script,
)

__all__ = ["HOOKS", "PROFILE"]
