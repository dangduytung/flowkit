"""Unit tests for the non-invasive Omni 1.2 Flash (macaron_cookie) hook."""
from __future__ import annotations

from agent.services import flow_batch as fb
from tools.common.omni_v12 import (
    OMNI_V11_FAMILY,
    OMNI_V12_FAMILY,
    configured_omni_family,
    install_omni_v12_patch,
    upgrade_omni_model_key,
)

PROJECT = "594758cc-11f5-4f92-8b3c-1213686591f4"
MEDIA_A = "73377e56-6f10-4c9a-b79d-1a2cb3b00bc1"
MEDIA_B = "93377e56-6f10-4c9a-b79d-1a2cb3b00bc2"


def test_upgrade_omni_model_key_translates_all_omni_1_1_modes():
    assert upgrade_omni_model_key("abra_t2v_6s", OMNI_V12_FAMILY) == "macaron_cookie_t2v_6s"
    assert upgrade_omni_model_key("abra_t2v_6s_360p", OMNI_V12_FAMILY) == "macaron_cookie_t2v_6s_360p"
    assert upgrade_omni_model_key("abra_i2v_8s", OMNI_V12_FAMILY) == "macaron_cookie_i2v_8s"
    assert upgrade_omni_model_key("abra_i2v_8s_360p", OMNI_V12_FAMILY) == "macaron_cookie_i2v_8s_360p"
    assert upgrade_omni_model_key("abra_r2v_6s", OMNI_V12_FAMILY) == "macaron_cookie_r2v_6s"
    assert upgrade_omni_model_key("abra_r2v_10s_360p", OMNI_V12_FAMILY) == "macaron_cookie_r2v_10s_360p"
    assert upgrade_omni_model_key("omni_flash_i2v_6s_first_last", OMNI_V12_FAMILY) == "macaron_cookie_i2v_fl_6s"
    assert (
        upgrade_omni_model_key("omni_flash_i2v_8s_first_last_360p", OMNI_V12_FAMILY)
        == "macaron_cookie_i2v_fl_8s_360p"
    )


def test_upgrade_omni_model_key_is_idempotent_and_preserves_veo():
    assert upgrade_omni_model_key("macaron_cookie_r2v_6s", OMNI_V12_FAMILY) == "macaron_cookie_r2v_6s"
    assert upgrade_omni_model_key("veo_3_1_i2v_lite", OMNI_V12_FAMILY) == "veo_3_1_i2v_lite"
    assert upgrade_omni_model_key("GEM_PIX_2", OMNI_V12_FAMILY) == "GEM_PIX_2"
    assert upgrade_omni_model_key("abra_r2v_6s", OMNI_V11_FAMILY) == "abra_r2v_6s"


def test_patched_build_envelope_upgrades_omni_requests_when_forced(monkeypatch):
    install_omni_v12_patch()
    monkeypatch.setenv("OMNI_V12_FORCE_IN_TESTS", "1")
    monkeypatch.setenv("OMNI_VIDEO_FAMILY", "macaron_cookie")

    assert configured_omni_family() == "macaron_cookie"

    t2v = fb.text_video_request("prompt", PROJECT, model="abra_t2v_6s")
    assert "macaron_cookie_t2v_6s" in t2v
    assert "abra_t2v_6s" not in t2v

    r2v = fb.omni_reference_video_request("prompt", PROJECT, [MEDIA_A], duration_s=6)
    assert "macaron_cookie_r2v_6s" in r2v
    assert "abra_r2v_6s" not in r2v

    i2v = fb.omni_first_frame_request("prompt", PROJECT, MEDIA_A, duration_s=6)
    assert "macaron_cookie_i2v_6s" in i2v
    assert "abra_i2v_6s" not in i2v

    fl = fb.omni_first_last_request("prompt", PROJECT, MEDIA_A, MEDIA_B, duration_s=6)
    assert "macaron_cookie_i2v_fl_6s" in fl
    assert "omni_flash_i2v_6s_first_last" not in fl
