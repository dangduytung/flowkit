"""Every Flow AI prompt the ad pipelines can send must read like ordinary phone footage."""
import re
from pathlib import Path

import pytest

from tools.common.pipeline.flow import AI_KINDS, is_faceless_scene, is_human_scene
from tools.common.prompts import build_flow_cinematic_scenes
from tools.common.prompts.realism import PHONE_HEADER, finalize_video_prompt, has_vietnamese, product_noun, sanitize_prompt
from tools.shopee_ad.product_parser import ProductInfo as ShopeeProductInfo
from tools.shopee_ad.prompts import build_cta_scene, build_faceless_pov_scenes, build_problem_solution_scenes
from tools.shopee_ad.storyboard import generate_default_storyboard
from tools.tiktok_ad.product_parser import ProductInfo as TikTokProductInfo
from tools.tiktok_ad.storyboard import generate_dynamic_storyboard

CATEGORIES = ["HEALTH_FITNESS", "BEAUTY_SKINCARE", "TECH_GADGETS", "KITCHEN_HOME", "FASHION_APPAREL", "GENERAL_LIFESTYLE"]
TITLES = [
    "serum dưỡng ẩm cấp nước",
    "chảo chống dính đáy từ",
    "quần jean nam ống suông",
    "USB 64GB vỏ kim loại",
    "giá đỡ điện thoại để bàn",
    "máy massage cầm tay",
    "Combo Túi Hút Chân Không đựng chăn màn",
    "máy hút bụi cầm tay không dây",
    "kê chân văn phòng",
    "bình giữ nhiệt inox",
]
FEATURES = dict(feat1_title="T1", feat1_desc="Mô tả 1", feat2_title="T2", feat2_desc="Mô tả 2")
BANNED = (
    "cinematic", "4k", "60fps", "35mm", "commercial", "b-roll", "instantly", "fast-forward", "time-lapse", "timelapse",
    "flawless", "spotless", "immaculate", "aesthetic", "sleek", "premium", "dramatic", "heroic", "5 fingers",
    "shallow depth of field", "lower-left", "lower left", "pointing toward comments", "beaming",
)


def _flow_prompts():
    """(label, scene, faceless_storyboard) for every AI scene any style can produce."""
    for title in TITLES:
        shopee = ShopeeProductInfo(zip_path=Path("x.zip"), slug="x", name=title, description_text="")
        for style in ("faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid"):
            for cta in ("follow", "shopee"):
                for sc in generate_default_storyboard(shopee, style=style, cta_mode=cta):
                    yield f"shopee/{style}/{cta}/{title}", sc, style == "faceless_pov"
        tiktok = TikTokProductInfo(zip_path=Path("x.zip"), slug="x", name=title, description_text="")
        for style in ("viral_hook", "faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid"):
            for sc in generate_dynamic_storyboard(tiktok, style=style):
                yield f"tiktok/{style}/{title}", sc, style == "faceless_pov"
        for category in CATEGORIES:
            for sc in build_flow_cinematic_scenes(category, title, social_proof_title="S", **FEATURES):
                yield f"cinematic/{category}/{title}", sc, False
            for sc in build_faceless_pov_scenes(category, title, **FEATURES):
                yield f"faceless/{category}/{title}", sc, True
            for sc in build_problem_solution_scenes(category, title, **FEATURES):
                yield f"problem/{category}/{title}", sc, False
            for mode in ("follow", "shopee", "tiktok"):
                for style in ("faceless_pov", "flow_cinematic"):
                    sc = build_cta_scene(9, mode, category, style, title)
                    if sc:
                        yield f"cta/{mode}/{style}/{category}", sc, style == "faceless_pov"


AI_PROMPTS = [(label, sc, faceless) for label, sc, faceless in _flow_prompts() if sc.kind in AI_KINDS and sc.prompt]


def test_matrix_is_not_empty():
    assert len(AI_PROMPTS) > 300


def test_templates_never_embed_vietnamese_titles():
    """Listing titles in the prompt get printed onto packaging; templates use product_noun instead."""
    offenders = [label for label, sc, _ in AI_PROMPTS if has_vietnamese(sc.prompt)]
    assert not offenders, offenders[:5]


def test_finalized_prompts_are_plain_phone_footage():
    for label, sc, faceless_board in AI_PROMPTS:
        final = finalize_video_prompt(
            sc.prompt, faceless=is_faceless_scene(sc, faceless_board), human=is_human_scene(sc, faceless_board)
        )
        lower = final.lower()
        hits = [w for w in BANNED if w in lower.replace("no thumbs-up", "")]
        assert not hits, (label, hits, final)
        assert final.startswith(PHONE_HEADER), label
        for tag in ("Camera:", "Audio:", "Avoid:"):
            assert final.count(tag) == 1, (label, tag)
        body = sanitize_prompt(sc.prompt)
        assert len(body.split()) <= 90, (label, len(body.split()), body)


def test_finalize_is_idempotent():
    once = finalize_video_prompt("A woman unboxes it on a desk.", faceless=False, human=True)
    assert finalize_video_prompt(once, faceless=False, human=True) == once


def test_legacy_storyboard_wording_is_rewritten():
    """Saved storyboards from older versions still carry the glossy/impossible wording."""
    legacy = (
        "Vertical 9:16 authentic fast-paced commercial ad video. Macro close-up B-roll, 60fps crisp commercial studio lighting. "
        "Hands attach the nozzle; the bag instantly deflates into a rock-firm slab. Fast-forward deflation effect, not floaty. "
        "They look directly at camera with a beaming, confident smile. Mouth closed, no speaking. "
        "Completely faceless, hands only, strictly exactly 5 fingers. NO text overlays."
    )
    out = sanitize_prompt(legacy).lower()
    for word in ("instantly", "fast-forward", "60fps", "commercial", "b-roll", "5 fingers", "beaming", "mouth closed", "vertical 9:16"):
        assert word not in out, word
    assert "gradually deflates" in out
    assert "glance briefly toward the camera" in out
    assert not re.search(r"\s[,.]", out)


def test_overhead_scenes_get_overhead_camera():
    final = finalize_video_prompt("Top-down view of hands on a bed, no face.", faceless=True, human=False)
    assert "looking down" in final.split("Camera:")[1]


@pytest.mark.parametrize(
    "category,title,expected",
    [
        ("GENERAL_LIFESTYLE", "Combo Túi Hút Chân Không", "clear vacuum storage bag"),
        ("KITCHEN_HOME", "chảo chống dính", "frying pan"),
        ("KITCHEN_HOME", "máy hút bụi cầm tay", "cordless handheld vacuum"),
        ("GENERAL_LIFESTYLE", "bình giữ nhiệt inox", "insulated steel bottle"),
        ("TECH_GADGETS", "thiết bị lạ", "small gadget"),
        ("UNKNOWN", "đồ gì đó", "household item"),
    ],
)
def test_product_noun(category, title, expected):
    assert product_noun(category, title) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Nồi phủ sứ chống dính Elmich Olive EL-5532OV size 18,20cm", "nồi phủ sứ chống dính"),
        ("máy hút bụi cầm tay không dây Nhật Bản Tamashio 6 đầu hút", "máy hút bụi cầm tay"),
        ("chảo chống dính đáy từ Sunhouse 26cm", "chảo chống dính đáy từ"),
        ("", "món này"),
    ],
)
def test_spoken_name(title, expected):
    from tools.common.prompts.realism import spoken_name

    assert spoken_name(title) == expected


LONG_TITLE = "Nồi phủ sứ chống dính Elmich Olive EL-5532OV size 18,20cm"


def test_narration_reads_like_speech():
    """Narration never reads the full listing title, never stutters "..", stays short enough for one clip."""
    shopee = ShopeeProductInfo(zip_path=Path("x.zip"), slug="x", name=LONG_TITLE, description_text="")
    tiktok = TikTokProductInfo(zip_path=Path("x.zip"), slug="x", name=LONG_TITLE, description_text="")
    scenes = [
        *(sc for style in ("faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid", "local")
          for sc in generate_default_storyboard(shopee, style=style, cta_mode="shopee")),
        *(sc for style in ("viral_hook", "faceless_pov", "problem_solution", "flow_cinematic", "lifestyle_edc", "hybrid")
          for sc in generate_dynamic_storyboard(tiktok, style=style)),
    ]
    for category in CATEGORIES:
        scenes += build_flow_cinematic_scenes(category, LONG_TITLE, social_proof_title="S", **FEATURES)
        scenes += build_faceless_pov_scenes(category, LONG_TITLE, **FEATURES)
        scenes += build_problem_solution_scenes(category, LONG_TITLE, **FEATURES)
    for sc in scenes:
        text = sc.narrator_text
        assert "EL-5532OV" not in text and "18,20cm" not in text, text
        assert ".." not in text, text
        assert "mình đặt về dùng thử" not in text.lower() and "mình thử dùng" not in text.lower(), text
        assert len(text) <= 160, (len(text), text)
