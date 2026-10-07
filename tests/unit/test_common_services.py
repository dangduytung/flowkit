"""Tests for tools.common settings, bgm, product parsing, TTS and the FlowKit client."""
import random
import zipfile
from pathlib import Path

import pytest

from tools.common import flow_client, tts
from tools.common.bgm import resolve_bgm_path
from tools.common.product import parse_description, parse_product_zip
from tools.common.settings import AutoModePolicy, PlatformProfile, ServiceSettings, load_env_file


def _profile(**overrides) -> PlatformProfile:
    fields = dict(
        key="demo",
        display_name="Demo",
        env_prefix="DEMO",
        output_root=Path("out"),
        downloads_dir=None,
        silent_scene_seconds=4.0,
        default_cta="none",
        cta_choices=("none",),
        default_style="viral_hook",
        batch_styles=("viral_hook", "faceless_pov"),
        style_aliases={"pov": "faceless_pov"},
    )
    fields.update(overrides)
    return PlatformProfile(**fields)


class TestPlatformProfile:
    def test_from_env_reads_prefixed_variables(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DEMO_DOWNLOADS_DIR", str(tmp_path))
        monkeypatch.setenv("DEMO_AD_CHANNEL_NAME", " Kênh Demo ")
        profile = PlatformProfile.from_env(
            "demo", "Demo", "DEMO", "Nope",
            silent_scene_seconds=4.0, default_cta="none", cta_choices=("none",),
            default_style="x", batch_styles=("x",),
        )
        assert profile.downloads_dir == tmp_path
        assert profile.channel_name == "Kênh Demo"
        assert profile.output_root.name == "demo_ads"
        assert profile.auto_mode is AutoModePolicy.BY_ASSETS

    @pytest.mark.parametrize(
        "raw,expected",
        [
            (None, ["viral_hook"]),
            ("", ["viral_hook"]),
            ("pov", ["faceless_pov"]),
            ("all", ["viral_hook", "faceless_pov"]),
            ("faceless_pov, all ,hybrid", ["faceless_pov", "viral_hook", "hybrid"]),
        ],
    )
    def test_resolve_styles(self, raw, expected):
        assert _profile().resolve_styles(raw) == expected

    def test_flow_silent_seconds_falls_back(self):
        assert _profile().flow_silent_seconds == 4.0
        assert _profile(flow_silent_scene_seconds=5.5).flow_silent_seconds == 5.5

    def test_list_zips_newest_first(self, tmp_path):
        old, new = tmp_path / "a.zip", tmp_path / "b.zip"
        old.write_bytes(b"")
        new.write_bytes(b"")
        import os
        os.utime(old, (1, 1))
        assert _profile(downloads_dir=tmp_path).list_zips() == [new, old]
        assert _profile().list_zips() == []


def test_load_env_file_does_not_override(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("# comment\nFK_TEST_A='one'\nFK_TEST_B=two\nbroken line\n", encoding="utf-8")
    monkeypatch.setenv("FK_TEST_B", "kept")
    monkeypatch.delenv("FK_TEST_A", raising=False)
    load_env_file(env)
    import os
    assert os.environ["FK_TEST_A"] == "one"
    assert os.environ["FK_TEST_B"] == "kept"
    monkeypatch.delenv("FK_TEST_A")


class TestBgm:
    @pytest.fixture
    def library(self, tmp_path):
        lib = tmp_path / "bgm"
        lib.mkdir()
        for name in ("calm_viral_hook.mp3", "upbeat.wav", "notes.txt"):
            (lib / name).write_bytes(b"x")
        return lib

    @pytest.mark.parametrize("value", [None, "", "off", "NONE", "0"])
    def test_off_values(self, value, library):
        assert resolve_bgm_path(value, bgm_dir=library) is None

    def test_file_name_in_library(self, library):
        assert resolve_bgm_path("upbeat.wav", bgm_dir=library) == library / "upbeat.wav"

    def test_auto_prefers_style_match(self, library):
        assert resolve_bgm_path("auto", style="viral-hook", bgm_dir=library) == library / "calm_viral_hook.mp3"

    def test_auto_prefers_track_shipped_with_product(self, library, tmp_path):
        assets = tmp_path / "assets"
        assets.mkdir()
        (assets / "bgm.m4a").write_bytes(b"x")
        assert resolve_bgm_path("random", product_assets_dir=assets, bgm_dir=library) == assets / "bgm.m4a"

    def test_auto_ignores_non_audio_and_is_seedable(self, library):
        picks = {resolve_bgm_path("auto", bgm_dir=library, rng=random.Random(i)).name for i in range(20)}
        assert picks <= {"calm_viral_hook.mp3", "upbeat.wav"}

    def test_unknown_name_is_none(self, library):
        assert resolve_bgm_path("missing.mp3", bgm_dir=library) is None


class TestProduct:
    def test_parse_description_accepts_both_scraper_labels(self):
        fields = parse_description("Tên sản phẩm: Máy hút bụi\nGiá bán: 199.000đ\nNgười bán: Shop A\nĐã bán: 1k\n")
        assert fields == {"name": "Máy hút bụi", "price": "199.000đ", "seller": "Shop A", "sold_count": "1k"}
        assert parse_description("Giá: 10đ\nShop: B")["seller"] == "B"

    def test_parse_product_zip(self, tmp_path):
        zip_path = tmp_path / "sp.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("b.jpg", b"x")
            z.writestr("a.png", b"x")
            z.writestr("clip.mp4", b"x")
            z.writestr("info.txt", "Tên sản phẩm: Túi nén chân không\nLink sản phẩm: https://shopee.vn/x\n".encode("utf-8"))
        info = parse_product_zip(zip_path)
        assert info.name == "Túi nén chân không"
        assert info.url == "https://shopee.vn/x"
        assert info.image_names == ["a.png", "b.jpg"]
        assert info.video_name == "clip.mp4"
        assert info.slug


class TestTts:
    def test_missing_config_raises(self, monkeypatch, tmp_path):
        empty = ServiceSettings(omnivoice_url="", omnivoice_api_key="", omnivoice_profile_id="", omnivoice_speed=1.0, flowkit_api_url="")
        monkeypatch.setattr(tts, "service_settings", lambda: empty)
        with pytest.raises(ValueError, match="OMNIVOICE_URL"):
            tts.generate_speech("xin chào", tmp_path / "a.wav")

    def test_non_audio_response_is_an_error(self, monkeypatch, tmp_path):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return b'{"error": "quota"}'

        monkeypatch.setattr(tts.urllib.request, "urlopen", lambda req, timeout: FakeResponse())
        with pytest.raises(tts.TTSError, match="unreadable audio"):
            tts.generate_speech("xin chào", tmp_path / "a.wav", url="http://tts", api_key="k")


class FakeFlow(flow_client.FlowKitClient):
    """Replays scripted /check-* responses."""

    def __init__(self, responses):
        super().__init__(base_url="http://fake")
        self.responses = responses
        self.calls = []

    def post(self, path, data):
        self.calls.append(path)
        return self.responses[path].pop(0) if self.responses[path] else {}


class TestPollJobs:
    def _clock(self):
        t = [0.0]

        def clock():
            return t[0]

        def sleep(s):
            t[0] += s

        return clock, sleep

    def test_success_failure_and_timeout_are_reported_separately(self):
        jobs = [
            {"scene_id": 1, "type": "workflow", "workflow": {"name": "w1"}, "primary_media_id": "m1"},
            {"scene_id": 2, "type": "operation", "op_name": "op2", "project_id": "p"},
            {"scene_id": 3, "type": "workflow", "workflow": {"name": "w3"}, "primary_media_id": "m3"},
        ]
        client = FakeFlow({
            "/api/flow/check-omni-status": [
                {"workflows": [{"primary_media_id": "m1", "done": True, "media": {"url": "u1"}}, {"primary_media_id": "m3", "done": False}]},
            ],
            "/api/flow/check-status": [
                {"operations": [{"name": "op2", "status": flow_client.STATUS_FAILED, "error": "UNSAFE_GENERATION"}]},
            ],
        })
        clock, sleep = self._clock()
        result = client.poll_jobs(jobs, poll_interval_s=5, timeout_s=12, sleep=sleep, clock=clock)

        assert result.urls == {1: "u1"}
        assert result.failed == {2: "UNSAFE_GENERATION"}
        assert result.timed_out == [3]
        with pytest.raises(flow_client.FlowGenerationError, match="scene 2: UNSAFE_GENERATION.*timed out: scenes \\[3\\]"):
            result.raise_for_failures()

    def test_failed_operation_does_not_wait_for_timeout(self):
        """Old poller swallowed its own failure exception and waited the full timeout."""
        jobs = [{"scene_id": 2, "type": "operation", "op_name": "op2", "project_id": "p"}]
        client = FakeFlow({"/api/flow/check-status": [{"operations": [{"name": "op2", "status": flow_client.STATUS_FAILED}]}]})
        clock, sleep = self._clock()
        result = client.poll_jobs(jobs, poll_interval_s=5, timeout_s=600, sleep=sleep, clock=clock)
        assert clock() == 0.0
        assert result.failed and not result.timed_out

    def test_transient_errors_are_retried(self):
        jobs = [{"scene_id": 1, "type": "workflow", "workflow": {"name": "w1"}, "primary_media_id": "m1"}]

        class Flaky(FakeFlow):
            def post(self, path, data):
                if not self.calls:
                    self.calls.append(path)
                    raise OSError("connection reset")
                return super().post(path, data)

        client = Flaky({"/api/flow/check-omni-status": [{"workflows": [{"primary_media_id": "m1", "done": True, "media": {"url": "u"}}]}]})
        clock, sleep = self._clock()
        assert client.poll_jobs(jobs, sleep=sleep, clock=clock).urls == {1: "u"}
