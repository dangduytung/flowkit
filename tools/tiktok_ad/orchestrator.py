"""TikTok ad pipeline entry point.

    python -m tools.tiktok_ad.orchestrator --zip <product.zip> [--mode local|flow|both] [--style ...]

The pipeline itself lives in tools.common.pipeline; this module binds it to TikTok.
"""
from pathlib import Path
from typing import Optional, Sequence, Union

from tools.common.flow_client import FlowKitClient
from tools.common.naming import build_variant_suffix as _build_variant_suffix
from tools.common.pipeline.cli import run_cli
from tools.common.pipeline.context import RunOptions
from tools.common.pipeline.local import run_local_pipeline
from tools.tiktok_ad.flow_ad_generator import generate_flow_ad
from tools.tiktok_ad.platform import HOOKS, PROFILE


def check_flowkit_health() -> bool:
    """FlowKit server up and the Chrome extension connected."""
    return FlowKitClient().is_ready()


def build_variant_suffix(
    style: Optional[str] = None,
    no_overlay: bool = False,
    cta_mode: Optional[str] = None,
    tag: Optional[str] = None,
) -> str:
    return _build_variant_suffix(
        style=style or PROFILE.default_style,
        no_overlay=no_overlay,
        cta_mode=cta_mode or PROFILE.default_cta,
        default_cta=PROFILE.naming_baseline_cta,
        tag=tag,
    )


def run_pipeline(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    mode_9_16: str = "blur_bg",
    cta_mode: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_handle: Optional[str] = None,
    style: Optional[str] = None,
    force_storyboard: bool = False,
    custom_idea: Optional[str] = None,
    no_voice: bool = False,
    no_overlay: bool = False,
    tag: Optional[str] = None,
    delogo: Optional[str] = "auto",
    bgm: Optional[Union[Path, str]] = None,
    target_scenes: Optional[Sequence[int]] = None,
) -> Path:
    """Local TikTok ad from the zip's own footage and photos; returns the final video."""
    return run_local_pipeline(PROFILE, HOOKS, RunOptions(
        zip_path=zip_path, speed=speed, voice_profile_id=profile_id, crop_mode=mode_9_16, cta_mode=cta_mode,
        channel_name=channel_name, channel_handle=channel_handle, style=style, force_storyboard=force_storyboard,
        custom_idea=custom_idea, no_voice=no_voice, no_overlay=no_overlay, tag=tag, delogo=delogo, bgm=bgm,
        target_scenes=target_scenes,
    ))


def main(argv: Optional[Sequence[str]] = None) -> None:
    run_cli(PROFILE, HOOKS, argv)


__all__ = ["build_variant_suffix", "check_flowkit_health", "generate_flow_ad", "main", "run_pipeline"]

if __name__ == "__main__":
    main()
