"""Commercial product categories and a keyword classifier.

Platforms tune *which* keywords map to *which* category (and in what order) as data —
a ``CategoryRules`` table — while matching itself lives here once.
"""
from __future__ import annotations

import re
from enum import Enum
from functools import lru_cache
from typing import Sequence


class Category(str, Enum):
    """Broad product category; values are the strings stored in storyboards."""

    BEAUTY_SKINCARE = "BEAUTY_SKINCARE"
    KITCHEN_HOME = "KITCHEN_HOME"
    FASHION_APPAREL = "FASHION_APPAREL"
    TECH_GADGETS = "TECH_GADGETS"
    HEALTH_FITNESS = "HEALTH_FITNESS"
    GENERAL_LIFESTYLE = "GENERAL_LIFESTYLE"

    def __str__(self) -> str:  # f"{category}" renders the plain value
        return self.value


# Ordered (category, keywords): the first category with a matching keyword wins.
CategoryRules = Sequence[tuple[Category, Sequence[str]]]

# Caption icon + tagline per category.
CATEGORY_META: dict[Category, tuple[str, str]] = {
    Category.BEAUTY_SKINCARE: ("💄", "Chăm sóc làn da rạng ngời & Tươi tắn"),
    Category.KITCHEN_HOME: ("🍳", "Gian bếp tinh tươm & Tiện nghi gia đình"),
    Category.FASHION_APPAREL: ("👗", "Thời trang thanh lịch & Tôn dáng tự nhiên"),
    Category.TECH_GADGETS: ("⚡", "Góc setup tối giản & Công nghệ đỉnh cao"),
    Category.HEALTH_FITNESS: ("🧘", "Chăm sóc sức khỏe & Thư giãn mỗi ngày"),
    Category.GENERAL_LIFESTYLE: ("🏠", "Giải pháp thông minh cho không gian sống"),
}
_FALLBACK_META = ("🏠", "Giải pháp tiện ích mỗi ngày")


@lru_cache(maxsize=None)
def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    # Whole-word match so "bàn là" (iron) does not fire inside "bàn làm việc" (desk).
    return re.compile(r"(?:\b|\s|^)" + re.escape(keyword) + r"(?:\b|\s|$)", re.IGNORECASE)


def classify(text: str, rules: CategoryRules, default: Category = Category.GENERAL_LIFESTYLE) -> Category:
    """First category in ``rules`` with a keyword found in ``text`` as a whole word."""
    haystack = text.lower()
    for category, keywords in rules:
        if any(_keyword_pattern(kw).search(haystack) for kw in keywords):
            return category
    return default


def category_meta(category: str) -> tuple[str, str]:
    """(emoji, tagline) used in captions."""
    try:
        return CATEGORY_META[Category(category)]
    except ValueError:
        return _FALLBACK_META


__all__ = ["CATEGORY_META", "Category", "CategoryRules", "category_meta", "classify"]
