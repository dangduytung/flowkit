"""Storyboard persistence shared by every ad pipeline.

On disk a storyboard is a JSON envelope ``{"scenes": [...], **metadata}``. Older Shopee
files are a bare list of scenes; both shapes are read transparently.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from tools.common.models import SceneDefinition

logger = logging.getLogger(__name__)

# Scene fields that are regenerated from the prompt builders on a targeted refresh.
# Timing/asset fields (kind, image_index, real_start_sec, ...) stay as the user left them.
REFRESHABLE_SCENE_FIELDS: tuple[str, ...] = (
    "prompt",
    "video_prompt",
    "narrator_text",
    "overlay_title",
    "overlay_subtitle",
)

_SCENE_FIELD_NAMES = frozenset(f.name for f in fields(SceneDefinition))


def scene_from_dict(data: Mapping[str, Any]) -> SceneDefinition:
    """Build a SceneDefinition, ignoring keys this version does not know about."""
    return SceneDefinition(**{k: v for k, v in data.items() if k in _SCENE_FIELD_NAMES})


def read_storyboard(path: Path) -> Optional[list[SceneDefinition]]:
    """Return the scenes stored at ``path``, or None if missing or unreadable."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("scenes", []) if isinstance(data, dict) else data
        return [scene_from_dict(item) for item in items]
    except (OSError, ValueError, TypeError) as exc:
        logger.warning("Cannot read storyboard %s: %s", path.name, exc)
        return None


def _read_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: v for k, v in data.items() if k != "scenes"} if isinstance(data, dict) else {}


def write_storyboard(
    path: Path,
    scenes: Sequence[SceneDefinition],
    metadata: Optional[Mapping[str, Any]] = None,
) -> Path:
    """Persist scenes as a JSON envelope.

    With ``metadata=None`` the metadata already stored in the file (if any) is kept.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if metadata is None:
        metadata = _read_metadata(path)
    payload = {**metadata, "scenes": [asdict(s) for s in scenes]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_or_create(
    path: Path,
    generate: Callable[[], list[SceneDefinition]],
    force: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
    min_scenes: int = 1,
) -> list[SceneDefinition]:
    """Return the stored storyboard, or build one with ``generate`` and persist it.

    A stored file is ignored when ``force`` is set or it holds fewer than ``min_scenes``.
    Hand edits to the JSON therefore survive every non-forced run.
    """
    if not force:
        stored = read_storyboard(path)
        if stored is not None and len(stored) >= min_scenes:
            logger.info("Loaded storyboard (%d scenes) from %s", len(stored), Path(path).name)
            return stored

    scenes = generate()
    write_storyboard(path, scenes, metadata)
    logger.info("Generated storyboard (%d scenes) -> %s", len(scenes), Path(path).name)
    return scenes


def refresh_scenes(
    scenes: Sequence[SceneDefinition],
    fresh_scenes: Iterable[SceneDefinition],
    scene_ids: Iterable[int],
    field_names: Sequence[str] = REFRESHABLE_SCENE_FIELDS,
) -> list[int]:
    """Copy regenerated copy/prompt fields onto the targeted scenes in place.

    Returns the ids that were actually refreshed (ids with no fresh counterpart are skipped).
    """
    wanted = set(scene_ids)
    fresh_by_id = {s.id: s for s in fresh_scenes}
    refreshed: list[int] = []
    for scene in scenes:
        fresh = fresh_by_id.get(scene.id)
        if scene.id not in wanted or fresh is None:
            continue
        for name in field_names:
            setattr(scene, name, getattr(fresh, name))
        refreshed.append(scene.id)
    return refreshed


def refresh_targeted_scenes(
    scenes: Sequence[SceneDefinition],
    scene_ids: Optional[Iterable[int]],
    path: Path,
    regenerate: Callable[[], list[SceneDefinition]],
) -> list[int]:
    """Re-derive copy/prompts for ``scene_ids`` from the builders and persist the storyboard.

    Used by ``--scene``: a targeted scene picks up prompt improvements while the
    rest of the (possibly hand-edited) storyboard is left untouched.
    """
    if not scene_ids:
        return []
    refreshed = refresh_scenes(scenes, regenerate(), scene_ids)
    for scene in scenes:
        if scene.id in refreshed:
            print(f"  • Cập nhật kịch bản chuẩn cho Scene {scene.id}: {scene.overlay_title}")
    write_storyboard(path, scenes)
    return refreshed


__all__ = [
    "REFRESHABLE_SCENE_FIELDS",
    "load_or_create",
    "read_storyboard",
    "refresh_scenes",
    "refresh_targeted_scenes",
    "scene_from_dict",
    "write_storyboard",
]
