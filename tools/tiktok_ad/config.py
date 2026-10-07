"""TikTok ad pipeline configuration.

Platform specifics live in ``PROFILE``; the module-level names below are kept for
existing imports.
"""
from pathlib import Path
from typing import Optional

from tools.common.bgm import resolve_bgm_path
from tools.common.settings import (
    DEFAULT_BGM_DIR,
    REPO_ROOT,
    AutoModePolicy,
    PlatformProfile,
    service_settings,
)

PROFILE = PlatformProfile.from_env(
    key="tiktok",
    display_name="TikTok",
    env_prefix="TIKTOK",
    default_downloads_folder="TikTok Downloads",
    silent_scene_seconds=4.0,
    default_cta="yellow_cart",
    cta_choices=("yellow_cart", "profile_bio", "follow", "none"),
    default_style="viral_hook",
    batch_styles=("viral_hook", "faceless_pov", "problem_solution", "lifestyle_edc"),
    style_aliases={"faceless": "faceless_pov", "pov": "faceless_pov", "hands_on_pov": "faceless_pov"},
    auto_mode=AutoModePolicy.BY_FLOWKIT,
)

_services = service_settings()
OMNIVOICE_URL = _services.omnivoice_url
OMNIVOICE_API_KEY = _services.omnivoice_api_key
OMNIVOICE_PROFILE_ID = _services.omnivoice_profile_id
OMNIVOICE_SPEED = _services.omnivoice_speed
FLOWKIT_API_URL = _services.flowkit_api_url

TIKTOK_DOWNLOADS_DIR = PROFILE.downloads_dir
OUTPUT_ROOT = PROFILE.output_root
BGM_DIR = DEFAULT_BGM_DIR
SILENT_SCENE_SECONDS = PROFILE.silent_scene_seconds
DEFAULT_CHANNEL_NAME = PROFILE.channel_name
DEFAULT_CHANNEL_HANDLE = PROFILE.channel_handle
DEFAULT_CHANNEL_BIO_LINK = PROFILE.channel_bio_link


def list_available_zips(directory: Optional[Path] = None) -> list[Path]:
    """TikTok product zips, newest first."""
    return PROFILE.list_zips(directory)


__all__ = [
    "BGM_DIR",
    "DEFAULT_CHANNEL_BIO_LINK",
    "DEFAULT_CHANNEL_HANDLE",
    "DEFAULT_CHANNEL_NAME",
    "FLOWKIT_API_URL",
    "OUTPUT_ROOT",
    "PROFILE",
    "REPO_ROOT",
    "SILENT_SCENE_SECONDS",
    "TIKTOK_DOWNLOADS_DIR",
    "list_available_zips",
    "resolve_bgm_path",
]
