"""Environment-backed settings shared by the ad pipelines, and the per-platform profile.

``.env`` at the repo root is loaded once (real environment variables win). Platform
packages describe themselves with a ``PlatformProfile``; everything else reads from
``service_settings()``.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = REPO_ROOT / ".env"
DEFAULT_BGM_DIR = REPO_ROOT / "assets" / "bgm"
OUTPUT_DIR = REPO_ROOT / "output"


def load_env_file(path: Path = DEFAULT_ENV_FILE) -> None:
    """Populate ``os.environ`` from a KEY=VALUE file without overriding existing variables."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_float(name: str, default: float) -> float:
    raw = env_str(name)
    try:
        return float(raw) if raw else default
    except ValueError:
        raise ValueError(f"{name} must be a number, got {raw!r}") from None


def ensure_utf8_console() -> None:
    """Let Vietnamese log lines print on a Windows console; call from CLI entry points."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


@dataclass(frozen=True)
class ServiceSettings:
    """External services every platform talks to."""

    omnivoice_url: str
    omnivoice_api_key: str
    omnivoice_profile_id: str
    omnivoice_speed: float
    flowkit_api_url: str

    @classmethod
    def from_env(cls) -> "ServiceSettings":
        return cls(
            omnivoice_url=env_str("OMNIVOICE_URL"),
            omnivoice_api_key=env_str("OMNIVOICE_API_KEY"),
            omnivoice_profile_id=env_str("OMNIVOICE_PROFILE_ID"),
            omnivoice_speed=env_float("OMNIVOICE_SPEED", 1.03),
            flowkit_api_url=env_str("FLOWKIT_API_URL", "http://127.0.0.1:8100"),
        )


@lru_cache(maxsize=1)
def service_settings() -> ServiceSettings:
    return ServiceSettings.from_env()


class AutoModePolicy(str, Enum):
    """What ``--mode auto`` renders."""

    BY_ASSETS = "by_assets"  # local + Flow when the zip has a video, Flow only otherwise
    BY_FLOWKIT = "by_flowkit"  # always local, plus Flow when the FlowKit server is up


@dataclass(frozen=True)
class PlatformProfile:
    """Everything that distinguishes one ad platform's pipeline from another."""

    key: str  # "shopee" / "tiktok": used in output paths and logs
    display_name: str
    env_prefix: str
    output_root: Path
    downloads_dir: Optional[Path]
    silent_scene_seconds: float
    default_cta: str
    cta_choices: tuple[str, ...]
    default_style: str
    batch_styles: tuple[str, ...]  # what ``--style all`` expands to
    style_aliases: Mapping[str, str] = field(default_factory=dict)
    auto_mode: AutoModePolicy = AutoModePolicy.BY_ASSETS
    # Flow clips run ~6s, so voiceless Flow scenes may use more of them than local cuts.
    flow_silent_scene_seconds: Optional[float] = None
    channel_name: str = ""
    channel_handle: str = ""
    channel_bio_link: str = ""

    @classmethod
    def from_env(cls, key: str, display_name: str, env_prefix: str, default_downloads_folder: str, **fields: Any) -> "PlatformProfile":
        """Build a profile; ``<PREFIX>_DOWNLOADS_DIR``, ``<PREFIX>_OUTPUT_DIR`` and
        ``<PREFIX>_AD_CHANNEL_*`` come from the environment."""
        downloads_env = env_str(f"{env_prefix}_DOWNLOADS_DIR")
        if downloads_env:
            downloads_dir: Optional[Path] = Path(downloads_env)
        else:
            candidate = Path.home() / "Downloads" / default_downloads_folder
            downloads_dir = candidate if candidate.exists() else None
        return cls(
            key=key,
            display_name=display_name,
            env_prefix=env_prefix,
            output_root=Path(env_str(f"{env_prefix}_OUTPUT_DIR") or OUTPUT_DIR / f"{key}_ads"),
            downloads_dir=downloads_dir,
            channel_name=env_str(f"{env_prefix}_AD_CHANNEL_NAME"),
            channel_handle=env_str(f"{env_prefix}_AD_CHANNEL_HANDLE"),
            channel_bio_link=env_str(f"{env_prefix}_AD_BIO_LINK"),
            **fields,
        )

    @property
    def flow_silent_seconds(self) -> float:
        return self.flow_silent_scene_seconds or self.silent_scene_seconds

    def list_zips(self, directory: Optional[Path] = None) -> list[Path]:
        """Product zips in ``directory`` (default: the downloads dir), newest first."""
        target = directory or self.downloads_dir
        if not target or not target.exists():
            return []
        return sorted(target.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)

    def resolve_styles(self, raw: Optional[str]) -> list[str]:
        """Expand ``--style`` ("a,b", "all", aliases) into an ordered, de-duplicated list."""
        styles: list[str] = []
        for token in (t.strip() for t in (raw or self.default_style).split(",")):
            if not token:
                continue
            expanded = self.batch_styles if token == "all" else (self.style_aliases.get(token, token),)
            styles.extend(s for s in expanded if s not in styles)
        return styles or [self.default_style]


__all__ = [
    "AutoModePolicy",
    "DEFAULT_BGM_DIR",
    "PlatformProfile",
    "REPO_ROOT",
    "ServiceSettings",
    "ensure_utf8_console",
    "env_float",
    "env_str",
    "load_env_file",
    "service_settings",
]
