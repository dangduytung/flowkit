"""Which scenes a pipeline run should (re)build."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SceneSelection:
    """A run either covers every scene (``target_ids is None``) or a subset (``--scene``).

    In a partial run, scenes outside the subset keep their existing artifacts
    (audio, clips) so their timing and look stay stable.
    """

    target_ids: Optional[frozenset[int]] = None

    @classmethod
    def from_ids(cls, ids: Optional[Iterable[int]]) -> "SceneSelection":
        ids = list(ids or [])
        return cls(frozenset(ids) if ids else None)

    @property
    def is_partial(self) -> bool:
        return self.target_ids is not None

    def is_targeted(self, scene_id: int) -> bool:
        return self.target_ids is None or scene_id in self.target_ids

    def keep_existing(self, scene_id: int, artifact_ready: bool, force_rebuild: bool = False) -> bool:
        """Whether an already-built artifact for ``scene_id`` should be reused.

        Partial run: reuse everything that is not targeted. Full run: reuse unless forced.
        """
        if not artifact_ready:
            return False
        if self.is_partial:
            return not self.is_targeted(scene_id)
        return not force_rebuild

    def unknown_ids(self, known_ids: Iterable[int]) -> list[int]:
        """Targeted ids that do not exist in the storyboard (for user-facing warnings)."""
        if self.target_ids is None:
            return []
        return sorted(self.target_ids - set(known_ids))


def warn_unknown_scene_ids(selection: SceneSelection, scene_ids: Iterable[int]) -> list[int]:
    """Tell the user about ``--scene`` ids the storyboard does not have; returns them."""
    unknown = selection.unknown_ids(scene_ids)
    if unknown:
        logger.warning("⚠️ --scene: không có phân cảnh %s trong storyboard, bỏ qua.", unknown)
    return unknown


__all__ = ["SceneSelection", "warn_unknown_scene_ids"]
