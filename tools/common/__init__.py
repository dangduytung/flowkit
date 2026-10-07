"""Shared utilities and models for advertising pipelines."""
from tools.common.models import SceneDefinition
from tools.common.naming import build_variant_suffix
from tools.common.watermarks import (
    load_watermark_rules,
    resolve_delogo_for_product,
)
from tools.common.archetypes import (
    ProductArchetype,
    resolve_product_archetype,
)

__all__ = [
    "SceneDefinition",
    "build_variant_suffix",
    "load_watermark_rules",
    "resolve_delogo_for_product",
    "ProductArchetype",
    "resolve_product_archetype",
]
