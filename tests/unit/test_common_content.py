"""tools.common text/categories/captions, plus architecture fences for the ad packages."""
import re
from pathlib import Path

import pytest

from tools.common.captions import FALLBACK_BULLETS, feature_bullets, write_caption_set
from tools.common.categories import Category, category_meta, classify
from tools.common.models import SceneDefinition
from tools.common.product import ProductInfo
from tools.common.text import slugify

TOOLS = Path(__file__).resolve().parents[2] / "tools"
AD_PACKAGES = ("common", "shopee_ad", "tiktok_ad")


def _py_files(*packages):
    for pkg in packages:
        yield from (TOOLS / pkg).rglob("*.py")


class TestArchitectureFences:
    def test_ad_packages_do_not_import_upstream_agent(self):
        """Keeps the fork's code merge-safe: upstream may refactor agent/ freely."""
        for path in _py_files(*AD_PACKAGES):
            assert not re.search(r"^\s*(from|import)\s+agent\b", path.read_text(encoding="utf-8"), re.M), path

    def test_common_does_not_depend_on_any_platform(self):
        for path in _py_files("common"):
            assert not re.search(r"\btools\.(shopee|tiktok)_ad\b", path.read_text(encoding="utf-8")), path


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Đồ ĐẸP — 100% (Mới)!", "do_dep_100_moi"),
        ("Chiến dịch giải cứu F-15E", "chien_dich_giai_cuu_f_15e"),
        ("  ", ""),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


class TestCategories:
    RULES = (
        (Category.KITCHEN_HOME, ("bàn là",)),
        (Category.TECH_GADGETS, ("bàn làm việc", "usb")),
    )

    def test_whole_word_matching(self):
        assert classify("Kệ bàn làm việc gỗ", self.RULES) is Category.TECH_GADGETS
        assert classify("Bàn là hơi nước", self.RULES) is Category.KITCHEN_HOME

    def test_rule_order_and_default(self):
        assert classify("bàn là kèm usb", self.RULES) is Category.KITCHEN_HOME
        assert classify("bình giữ nhiệt", self.RULES) is Category.GENERAL_LIFESTYLE

    def test_category_values_are_plain_strings(self):
        assert Category.TECH_GADGETS == "TECH_GADGETS"
        assert f"{Category.TECH_GADGETS}" == "TECH_GADGETS"

    def test_meta_fallback(self):
        assert category_meta("TECH_GADGETS")[0] == "⚡"
        assert category_meta("UNKNOWN") == ("🏠", "Giải pháp tiện ích mỗi ngày")


class TestCaptions:
    @staticmethod
    def _scene(sid, title="T", sub="S"):
        return SceneDefinition(id=sid, name="n", kind="FLOW_AI", narrator_text="x", overlay_title=title, overlay_subtitle=sub)

    def test_feature_bullets_use_scenes_2_to_4(self):
        scenes = [self._scene(i, f"T{i}", f"S{i}") for i in range(1, 6)]
        assert feature_bullets(scenes) == "• T2: S2\n• T3: S3\n• T4: S4"

    def test_feature_bullets_fallback(self):
        assert feature_bullets([self._scene(1)]) == "\n".join(FALLBACK_BULLETS)

    def test_write_caption_set_names_and_order(self, tmp_path):
        product = ProductInfo(zip_path=Path("x.zip"), slug="sp", name="SP")
        calls = []

        def writer(name):
            def write(prod, scenes, path, channel_name, channel_handle):
                calls.append(name)
                Path(path).write_text(name, encoding="utf-8")
            return write

        paths = write_caption_set({"tiktok": writer("tt"), "facebook": writer("fb")}, product, [], tmp_path, "", "", "v1")
        assert calls == ["tt", "fb"]
        assert paths["tiktok"].name == "sp_v1_tiktok_caption.txt"
        assert paths["facebook"].read_text(encoding="utf-8") == "fb"
