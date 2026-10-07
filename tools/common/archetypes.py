"""Product archetype taxonomy and keyword classifier.

An archetype is a narrower product type than a category (e.g. VACUUM_CLEANER inside
KITCHEN_HOME) for which a pipeline ships dedicated storytelling. Keywords live in one
registry here so prompt builders never carry their own inline keyword lists.
"""
from __future__ import annotations

import unicodedata
from enum import Enum


class ProductArchetype(str, Enum):
    """Product types that have dedicated scene playbooks."""

    VACUUM_CLEANER = "vacuum_cleaner"
    COMPRESSION_STORAGE = "compression_storage"
    APPAREL_BOTTOMS = "apparel_bottoms"
    SKINCARE = "skincare"
    GENERIC = "generic"


# Matched in insertion order: put narrower archetypes before broader ones.
ARCHETYPE_KEYWORDS: dict[ProductArchetype, tuple[str, ...]] = {
    ProductArchetype.VACUUM_CLEANER: (
        "máy hút bụi",
        "hút bụi cầm tay",
        "hút bụi mini",
        "hút bụi ô tô",
        "hút bụi không dây",
        "robot hút bụi",
    ),
    ProductArchetype.COMPRESSION_STORAGE: (
        "túi hút chân không",
        "túi nén",
        "hút chân không",
        "bơm hút chân không",
        "vali",
        "chăn màn",
        "tủ quần áo",
        "gấp gọn",
        "nén",
    ),
    ProductArchetype.APPAREL_BOTTOMS: (
        "quần âu",
        "quần tây",
        "quần kaki",
        "quần jean",
        "quần bò",
        "quần jogger",
    ),
    ProductArchetype.SKINCARE: (
        "serum",
        "kem dưỡng",
        "toner",
        "nước hoa hồng",
        "sữa rửa mặt",
        "tinh chất",
    ),
}


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def resolve_product_archetype(title: str, description: str = "") -> ProductArchetype:
    """Return the first archetype whose keywords appear in the title or description."""
    haystack = _normalize(f"{title} {description}")
    for archetype, keywords in ARCHETYPE_KEYWORDS.items():
        if any(_normalize(kw) in haystack for kw in keywords):
            return archetype
    return ProductArchetype.GENERIC


__all__ = ["ARCHETYPE_KEYWORDS", "ProductArchetype", "resolve_product_archetype"]
