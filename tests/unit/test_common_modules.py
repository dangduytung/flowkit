"""Unit tests for tools/common modules (watermarks and naming).

Tests cover:
1. Watermark rules resolution, normalization, and coordinate scaling.
2. Semantic variant naming and tag sanitization.
"""
import json
import subprocess
from pathlib import Path

import pytest

from tools.common.naming import build_variant_suffix
from tools.common.watermarks import (
    _get_video_dimensions,
    _normalize_product_url,
    get_watermark_rules_path,
    load_watermark_rules,
    resolve_delogo_for_product,
)


# ===========================================================================
# 1. Test Watermarks Module
# ===========================================================================
class TestWatermarks:
    def test_normalize_product_url(self):
        """Should strip protocol, www, query parameters, and trailing slashes."""
        assert _normalize_product_url("https://shopee.vn/product/25032641/29165023288?sp_atk=123") == "shopee.vn/product/25032641/29165023288"
        assert _normalize_product_url("http://www.shopee.vn/item/123/") == "shopee.vn/item/123"
        assert _normalize_product_url("https://tiktok.com/@shop/video/999?is_from_webapp=1") == "tiktok.com/@shop/video/999"
        assert _normalize_product_url("") == ""
        assert _normalize_product_url(None) == ""

    def test_resolve_delogo_for_empty_url(self):
        """Empty or None URL returns (None, None)."""
        delogo, name = resolve_delogo_for_product("")
        assert delogo is None
        assert name is None

        delogo, name = resolve_delogo_for_product(None)
        assert delogo is None
        assert name is None

    def test_resolve_delogo_unmatched_url(self):
        """Unmatched product URL returns (None, None)."""
        delogo, name = resolve_delogo_for_product("https://shopee.vn/unmatched-random-product-url-999")
        assert delogo is None
        assert name is None

    def test_resolve_delogo_from_bundled_rules(self):
        """Bundled Pi home rule matches exact or normalized URL from config/watermark_rules.json."""
        target_url = "https://shopee.vn/product/25032641/29165023288"
        delogo, name = resolve_delogo_for_product(target_url)
        assert delogo is not None
        assert "x=30:y=545:w=140:h=60" in delogo
        assert "Pi home" in name

    def test_resolve_delogo_custom_rules_file(self, tmp_path, monkeypatch):
        """Custom watermark rules file with env override should be loaded properly."""
        custom_rules = [
            {
                "name": "Custom Shop Logo",
                "product_url": "https://shopee.vn/custom-item-12345",
                "delogo": "x=10:y=20:w=100:h=50",
            }
        ]
        rules_path = tmp_path / "custom_watermarks.json"
        rules_path.write_text(json.dumps(custom_rules), encoding="utf-8")

        monkeypatch.setenv("WATERMARK_RULES_PATH", str(rules_path))
        assert get_watermark_rules_path() == rules_path
        loaded = load_watermark_rules()
        assert len(loaded) == 1

        delogo, name = resolve_delogo_for_product("https://shopee.vn/custom-item-12345?query=abc")
        assert delogo == "x=10:y=20:w=100:h=50"
        assert name == "Custom Shop Logo"

    def test_resolve_delogo_ratio_dictionary(self, tmp_path, monkeypatch):
        """Ratio-based delogo dictionary should scale to video resolution."""
        custom_rules = [
            {
                "name": "Ratio Logo",
                "product_url": "https://shopee.vn/ratio-product",
                "delogo": {"ratio": [0.1, 0.2, 0.3, 0.4]},
            }
        ]
        rules_path = tmp_path / "ratio_watermarks.json"
        rules_path.write_text(json.dumps(custom_rules), encoding="utf-8")
        monkeypatch.setenv("WATERMARK_RULES_PATH", str(rules_path))

        # Default fallback resolution is 720x720: x=72, y=144, w=216, h=288
        delogo, name = resolve_delogo_for_product("https://shopee.vn/ratio-product")
        assert delogo == "x=72:y=144:w=216:h=288"
        assert name == "Ratio Logo"

    def test_resolve_delogo_scales_with_video_resolution(self, tmp_path, monkeypatch):
        """Coordinates scale proportionally if video dimensions differ from ref_width/ref_height."""
        custom_rules = [
            {
                "name": "Scale Test",
                "product_url": "https://shopee.vn/scale-item",
                "delogo": "x=100:y=100:w=50:h=50",
                "ref_width": 500,
                "ref_height": 500,
            }
        ]
        rules_path = tmp_path / "scale_watermarks.json"
        rules_path.write_text(json.dumps(custom_rules), encoding="utf-8")
        monkeypatch.setenv("WATERMARK_RULES_PATH", str(rules_path))

        # Generate a synthetic 1000x1000 test video (scale factor 2.0x)
        test_vid = tmp_path / "test_1000x1000.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1000x1000:d=0.1:r=10",
            "-c:v", "libx264", "-preset", "ultrafast", str(test_vid),
        ], capture_output=True, check=True)

        delogo, name = resolve_delogo_for_product("https://shopee.vn/scale-item", video_path=test_vid)
        assert delogo == "x=200:y=200:w=100:h=100"


# ===========================================================================
# 2. Test Naming Module
# ===========================================================================
class TestNaming:
    def test_build_variant_suffix_default(self):
        """Default arguments should return base style."""
        assert build_variant_suffix() == "flow_cinematic"

    def test_build_variant_suffix_with_clean_flag(self):
        """no_overlay=True appends 'clean'."""
        assert build_variant_suffix(style="viral_hook", no_overlay=True) == "viral_hook_clean"

    def test_build_variant_suffix_custom_cta(self):
        """Custom CTA mode different from default_cta should append 'cta-<name>'."""
        res = build_variant_suffix(
            style="problem_solution",
            cta_mode="shopee",
            default_cta="none",
        )
        assert res == "problem_solution_cta-shopee"

    def test_build_variant_suffix_no_cta_when_default_has_cta(self):
        """Setting cta_mode='none' when default_cta is active should append 'no-cta'."""
        res = build_variant_suffix(
            style="viral_hook",
            cta_mode="none",
            default_cta="yellow_cart",
        )
        assert res == "viral_hook_no-cta"

    def test_build_variant_suffix_tag_sanitization(self):
        """Tags with spaces or special symbols should be sanitized cleanly."""
        res = build_variant_suffix(
            style="faceless_pov",
            tag="v2.1 final test!",
        )
        assert res == "faceless_pov_v2_1_final_test"

    def test_build_variant_suffix_composite(self):
        """Full combination of clean, custom CTA, and tag."""
        res = build_variant_suffix(
            style="flow_cinematic",
            no_overlay=True,
            cta_mode="tiktok",
            default_cta="none",
            tag="A/B-1",
        )
        assert res == "flow_cinematic_clean_cta-tiktok_A_B-1"
