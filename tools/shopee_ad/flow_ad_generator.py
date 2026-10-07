"""Shopee Google Flow ad: AI scenes from Flow (Omni) + real product photos.

    python -m tools.shopee_ad.flow_ad_generator --zip <product.zip> [--style ...]

Same flags as the orchestrator, always in flow mode.
"""
import sys
from pathlib import Path
from typing import Optional, Sequence, Union

from tools.common.pipeline.cli import run_cli
from tools.common.pipeline.context import RunOptions
from tools.common.pipeline.flow import run_flow_pipeline
from tools.shopee_ad.platform import HOOKS, PROFILE


def generate_flow_ad(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    cta_mode: Optional[str] = None,
    style: str = "flow_cinematic",
    regen: bool = False,
    force_storyboard: bool = False,
    custom_idea: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_handle: Optional[str] = None,
    no_voice: bool = False,
    no_overlay: bool = False,
    tag: Optional[str] = None,
    bgm_path: Optional[Union[Path, str]] = None,
    target_scenes: Optional[Sequence[int]] = None,
    mode_9_16: str = "blur_bg",
    delogo: Optional[str] = "auto",
) -> Path:
    """Flow Shopee ad; returns the final video."""
    return run_flow_pipeline(PROFILE, HOOKS, RunOptions(
        zip_path=zip_path, speed=speed, voice_profile_id=profile_id, cta_mode=cta_mode, style=style, regen=regen,
        force_storyboard=force_storyboard, custom_idea=custom_idea, channel_name=channel_name,
        channel_handle=channel_handle, no_voice=no_voice, no_overlay=no_overlay, tag=tag, bgm=bgm_path,
        target_scenes=target_scenes, crop_mode=mode_9_16, delogo=delogo,
    ))


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    run_cli(PROFILE, HOOKS, [*args, "--mode", "flow"])


__all__ = ["generate_flow_ad", "main"]

if __name__ == "__main__":
    main()
