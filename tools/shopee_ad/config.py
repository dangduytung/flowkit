"""Shopee ad pipeline configuration.

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
    key="shopee",
    display_name="Shopee",
    env_prefix="SHOPEE",
    default_downloads_folder="Shopee Downloads",
    silent_scene_seconds=5.0,
    flow_silent_scene_seconds=5.5,
    default_cta="shopee",
    cta_choices=("none", "follow", "shopee", "tiktok"),
    default_style="flow_cinematic",
    batch_styles=("flow_cinematic", "faceless_pov", "problem_solution", "lifestyle_edc"),
    style_aliases={"faceless": "faceless_pov", "pov": "faceless_pov"},
    auto_mode=AutoModePolicy.BY_ASSETS,
)

_services = service_settings()
OMNIVOICE_URL = _services.omnivoice_url
OMNIVOICE_API_KEY = _services.omnivoice_api_key
OMNIVOICE_PROFILE_ID = _services.omnivoice_profile_id
OMNIVOICE_SPEED = _services.omnivoice_speed
FLOWKIT_API_URL = _services.flowkit_api_url

SHOPEE_DOWNLOADS_DIR = PROFILE.downloads_dir
OUTPUT_ROOT = PROFILE.output_root
BGM_DIR = DEFAULT_BGM_DIR
SILENT_SCENE_SECONDS = PROFILE.silent_scene_seconds
DEFAULT_CHANNEL_NAME = PROFILE.channel_name
DEFAULT_CHANNEL_HANDLE = PROFILE.channel_handle
DEFAULT_CHANNEL_BIO_LINK = PROFILE.channel_bio_link


def list_available_zips(directory: Optional[Path] = None) -> list[Path]:
    """Shopee product zips, newest first."""
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
    "SHOPEE_DOWNLOADS_DIR",
    "SILENT_SCENE_SECONDS",
    "list_available_zips",
    "resolve_bgm_path",
]
