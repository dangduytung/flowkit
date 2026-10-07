"""Style registry: maps ``--style`` names (and aliases) to scene builders."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo


@dataclass(frozen=True)
class StoryContext:
    """Everything a style builder may draw on, derived once per storyboard."""

    product: ProductInfo
    category: str
    clean_title: str
    feat1_title: str
    feat1_desc: str
    feat2_title: str
    feat2_desc: str
    social_proof_title: str
    custom_idea: Optional[str] = None

    @property
    def has_video(self) -> bool:
        return bool(self.product.video_name)

    @property
    def num_images(self) -> int:
        return len(self.product.image_names) if self.product.image_names else 1


StyleBuilder = Callable[[StoryContext], list[SceneDefinition]]


class StyleRegistry:
    """Named scene builders with aliases and an optional fallback for unknown names."""

    def __init__(self, fallback: Optional[str] = None):
        self._builders: dict[str, StyleBuilder] = {}
        self._fallback = fallback

    def register(self, names: Iterable[str], builder: StyleBuilder) -> StyleBuilder:
        for name in names:
            if name in self._builders:
                raise ValueError(f"Style {name!r} registered twice")
            self._builders[name] = builder
        return builder

    def get(self, style: str) -> StyleBuilder:
        builder = self._builders.get(style)
        if builder is None and self._fallback is not None:
            builder = self._builders[self._fallback]
        if builder is None:
            raise KeyError(f"Unknown style {style!r}; known: {sorted(self._builders)}")
        return builder

    def build(self, style: str, ctx: StoryContext) -> list[SceneDefinition]:
        return self.get(style)(ctx)

    @property
    def names(self) -> list[str]:
        return sorted(self._builders)


__all__ = ["StoryContext", "StyleBuilder", "StyleRegistry"]
