"""Background-music selection. Music is opt-in: nothing plays unless asked for."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Optional, Union

from tools.common.settings import DEFAULT_BGM_DIR

AUDIO_SUFFIXES = (".mp3", ".wav", ".m4a")
_OFF_VALUES = frozenset({"none", "false", "0", "no", "off"})
_AUTO_VALUES = frozenset({"auto", "random", "true", "1"})


def _audio_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_SUFFIXES)


def resolve_bgm_path(
    custom_bgm: Optional[Union[str, Path]] = None,
    style: Optional[str] = None,
    product_assets_dir: Optional[Path] = None,
    bgm_dir: Path = DEFAULT_BGM_DIR,
    rng: Optional[random.Random] = None,
) -> Optional[Path]:
    """Resolve ``--bgm`` into a file.

    - empty / ``none`` / ``off``: no music (default)
    - a path, or a file name inside ``bgm_dir``: that file
    - ``auto`` / ``random``: ``bgm.*`` shipped with the product, else a random track from
      ``bgm_dir``, preferring tracks whose name contains the style
    """
    if not custom_bgm:
        return None
    value = str(custom_bgm).strip().lower()
    if value in _OFF_VALUES:
        return None

    direct = Path(custom_bgm)
    if direct.is_file():
        return direct
    in_library = bgm_dir / str(custom_bgm)
    if in_library.is_file():
        return in_library

    if value not in _AUTO_VALUES:
        return None

    if product_assets_dir:
        for suffix in AUDIO_SUFFIXES:
            shipped = product_assets_dir / f"bgm{suffix}"
            if shipped.is_file():
                return shipped

    tracks = _audio_files(bgm_dir)
    if not tracks:
        return None
    if style:
        wanted = style.lower().replace("-", "_")
        matching = [t for t in tracks if wanted in t.stem.lower()]
        tracks = matching or tracks
    return (rng or random).choice(tracks)


__all__ = ["AUDIO_SUFFIXES", "resolve_bgm_path"]
