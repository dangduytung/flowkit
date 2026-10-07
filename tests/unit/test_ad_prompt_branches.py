"""Branch-coverage tests for ad prompt builders.

Every (builder, category, archetype) combination must build without error, and a
category's own copy must not be overwritten by the generic fallback.
"""
import inspect
from pathlib import Path

import pytest

from tools.common.archetypes import ProductArchetype, resolve_product_archetype
from tools.shopee_ad.product_parser import ProductInfo as ShopeeProductInfo
from tools.shopee_ad.storyboard import generate_default_storyboard
from tools.tiktok_ad.product_parser import ProductInfo as TikTokProductInfo
from tools.tiktok_ad.prompts import (
    build_faceless_pov_scenes,
    build_flow_cinematic_scenes,
    build_lifestyle_edc_scenes,
    build_problem_solution_scenes,
    build_viral_hook_scenes,
)
from tools.tiktok_ad.storyboard import generate_dynamic_storyboard

CATEGORIES = [
    "HEALTH_FITNESS",
    "BEAUTY_SKINCARE",
    "TECH_GADGETS",
    "KITCHEN_HOME",
    "FASHION_APPAREL",
    "GENERAL_LIFESTYLE",
]

TITLES = {
    "generic": "giá đỡ điện thoại đa năng",
    "vacuum": "máy hút bụi cầm tay không dây",
    "compression": "túi hút chân không đựng chăn màn",
}

TIKTOK_BUILDERS = [
    build_viral_hook_scenes,
    build_faceless_pov_scenes,
    build_problem_solution_scenes,
    build_flow_cinematic_scenes,
    build_lifestyle_edc_scenes,
]

FEATURES = dict(
    feat1_title="TÍNH NĂNG 1",
    feat1_desc="Mô tả tính năng 1",
    feat2_title="TÍNH NĂNG 2",
    feat2_desc="Mô tả tính năng 2",
)

GENERIC_FALLBACK_TITLES = {"NÂNG TẦM TRẢI NGHIỆM", "BẤT TIỆN HÀNG NGÀY?", "BẠN ĐANG TÌM GIẢI PHÁP?"}


def _tiktok_product(name: str) -> TikTokProductInfo:
    return TikTokProductInfo(zip_path=Path("dummy.zip"), slug="dummy", name=name, description_text="")


def _call_tiktok_builder(builder, category: str, title: str):
    available = dict(
        category=category,
        clean_title=title,
        product=_tiktok_product(title),
        social_proof_title="ĐÁNH GIÁ 5 SAO",
        **FEATURES,
    )
    accepted = inspect.signature(builder).parameters
    return builder(**{k: v for k, v in available.items() if k in accepted})


class TestArchetypeResolution:
    @pytest.mark.parametrize(
        "title,expected",
        [
            (TITLES["vacuum"], ProductArchetype.VACUUM_CLEANER),
            (TITLES["compression"], ProductArchetype.COMPRESSION_STORAGE),
            ("vali kéo du lịch 24 inch", ProductArchetype.COMPRESSION_STORAGE),
            (TITLES["generic"], ProductArchetype.GENERIC),
        ],
    )
    def test_resolves_expected_archetype(self, title, expected):
        assert resolve_product_archetype(title) == expected

    def test_vacuum_wins_over_compression(self):
        """Narrower archetypes are matched before broader ones."""
        assert resolve_product_archetype("máy hút bụi kèm túi nén") == ProductArchetype.VACUUM_CLEANER


class TestTikTokBuilderMatrix:
    @pytest.mark.parametrize("builder", TIKTOK_BUILDERS, ids=lambda b: b.__name__)
    @pytest.mark.parametrize("category", CATEGORIES)
    @pytest.mark.parametrize("title_key", list(TITLES))
    def test_builds_every_combination(self, builder, category, title_key):
        scenes = _call_tiktok_builder(builder, category, TITLES[title_key])
        assert scenes
        for sc in scenes:
            assert sc.narrator_text and sc.overlay_title

    @pytest.mark.parametrize("category", [c for c in CATEGORIES if c != "GENERAL_LIFESTYLE"])
    @pytest.mark.parametrize("builder", [build_faceless_pov_scenes, build_problem_solution_scenes, build_viral_hook_scenes])
    def test_category_copy_not_overwritten_by_generic_fallback(self, builder, category):
        scenes = _call_tiktok_builder(builder, category, TITLES["generic"])
        titles = {sc.overlay_title for sc in scenes}
        assert not titles & GENERIC_FALLBACK_TITLES

    @pytest.mark.parametrize("builder", [build_faceless_pov_scenes, build_problem_solution_scenes])
    def test_archetype_copy_takes_precedence_over_category(self, builder):
        scenes = _call_tiktok_builder(builder, "KITCHEN_HOME", TITLES["vacuum"])
        assert any("BỤI" in sc.overlay_title or "SẠCH" in sc.overlay_title for sc in scenes)


@pytest.mark.parametrize("style", ["viral_hook", "faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid"])
@pytest.mark.parametrize("title_key", list(TITLES))
def test_tiktok_storyboard_styles(style, title_key):
    scenes = generate_dynamic_storyboard(_tiktok_product(TITLES[title_key]), style=style)
    assert scenes


@pytest.mark.parametrize("style", ["faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid", "local"])
@pytest.mark.parametrize("cta_mode", ["none", "follow", "shopee"])
@pytest.mark.parametrize("title_key", list(TITLES))
def test_shopee_storyboard_styles(style, cta_mode, title_key):
    product = ShopeeProductInfo(zip_path=Path("dummy.zip"), slug="dummy", name=TITLES[title_key], description_text="")
    scenes = generate_default_storyboard(product, style=style, cta_mode=cta_mode)
    assert scenes
