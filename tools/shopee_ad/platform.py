"""Shopee content plugged into the shared ad pipelines."""
from tools.common.pipeline.context import PlatformHooks
from tools.shopee_ad.caption_generator import generate_all_platform_captions
from tools.shopee_ad.config import PROFILE
from tools.shopee_ad.cover_generator import create_cover_image
from tools.shopee_ad.publish_guide import create_publish_guide
from tools.shopee_ad.storyboard import generate_default_storyboard, load_or_create_storyboard
from tools.shopee_ad.video_assembler import export_voiceover_script

HOOKS = PlatformHooks(
    load_storyboard=load_or_create_storyboard,
    generate_storyboard=generate_default_storyboard,
    write_captions=generate_all_platform_captions,
    create_cover=create_cover_image,
    write_publish_guide=create_publish_guide,
    export_script=export_voiceover_script,
)

__all__ = ["HOOKS", "PROFILE"]
