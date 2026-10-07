"""Pure-function tests for tools.common.media and tools.common.ffmpeg (no rendering)."""
import random

import pytest

from tools.common.constants import FLOW_WATERMARK_BOX, VERTICAL_720P
from tools.common.ffmpeg import EncodeProfile, delogo_filter
from tools.common.media import assembler
from tools.common.media.cover import format_cover_text
from tools.common.media.cutplanner import MIN_SLICE_SECONDS, plan_subclip_starts
from tools.common.models import SceneDefinition


class TestPlanSubclipStarts:
    @staticmethod
    def _assert_invariants(starts, total, n):
        assert len(starts) == n
        assert starts[0] == 0.0
        assert all(b > a for a, b in zip(starts, starts[1:])), starts
        assert all(0.0 <= s < total for s in starts), starts

    def test_degenerate_inputs(self):
        assert plan_subclip_starts([], 10.0, 0) == []
        assert plan_subclip_starts([], 0.0, 3) == [0.0, 0.0, 0.0]
        assert plan_subclip_starts([0.0, 10.0], 10.0, 1) == [0.0]

    def test_fitting_narration_gets_full_slices(self):
        durations = [5.4, 5.4, 5.4, 5.4]
        starts = plan_subclip_starts([0.0, 5.8, 10.9, 16.2, 23.0], 23.0, 4, durations)
        self._assert_invariants(starts, 23.0, 4)
        ends = starts[1:] + [23.0]
        assert all(end - start >= d - 1e-6 for start, end, d in zip(starts, ends, durations))

    def test_fitting_narration_snaps_forward_to_cuts(self):
        starts = plan_subclip_starts([0.0, 4.5, 9.2, 30.0], 30.0, 3, [4.0, 4.0, 4.0])
        assert starts == [0.0, 4.5, 9.2]

    def test_snapping_never_starves_later_scenes(self):
        # A cut just inside the window would leave no room for scene 3; it must be skipped.
        starts = plan_subclip_starts([0.0, 4.9, 12.0], 12.0, 3, [4.0, 4.0, 4.0])
        assert starts == [0.0, 4.0, 8.0]

    def test_regression_short_video_never_repeats_start(self):
        """Old fallback could return a start <= the previous one (zero-length slice)."""
        # The previous planner returned [0.0, 1.0, 1.5, 2.0, 2.0] here.
        starts = plan_subclip_starts([0.0, 2.5], 2.5, 5, [5.0] * 5)
        self._assert_invariants(starts, 2.5, 5)

    @pytest.mark.parametrize("seed", range(200))
    def test_random_inputs_keep_invariants(self, seed):
        rng = random.Random(seed)
        total = rng.uniform(1.0, 60.0)
        n = rng.randint(2, 8)
        cuts = sorted({0.0, total, *(rng.uniform(0, total) for _ in range(rng.randint(0, 25)))})
        durations = [rng.uniform(1.0, 9.0) for _ in range(n)] if rng.random() < 0.8 else None
        starts = plan_subclip_starts(cuts, total, n, durations)
        self._assert_invariants(starts, total, n)
        if durations is None or sum(durations) > total:
            min_slice = min(MIN_SLICE_SECONDS, total / n)
            slices = [b - a for a, b in zip(starts, starts[1:] + [total])]
            assert min(slices) >= min_slice - 0.011  # rounding to 2 decimals
        else:
            ends = starts[1:] + [total]
            assert all(e - s >= d - 0.011 for s, e, d in zip(starts, ends, durations))


class TestAssemblerBuilders:
    def test_scene_duration_precedence(self):
        assert assembler.scene_duration(3.0, True, 9.0, 7.0, 0.4) == pytest.approx(3.4)
        assert assembler.scene_duration(None, False, 9.0, 7.0, 0.4) == 9.0
        assert assembler.scene_duration(None, False, None, 7.0, 0.4) == 7.0
        assert assembler.scene_duration(None, False, None, 0.0, 0.4) == assembler.DEFAULT_SCENE_SECONDS

    def test_short_clip_is_stretched_not_looped(self):
        filters = assembler.fit_duration_filters(4.0, 5.0, 30)
        assert filters[0] == "setpts=1.2500*(PTS-STARTPTS)"
        assert not any("loop" in f or "tpad" in f for f in filters)

    def test_much_shorter_clip_holds_last_frame_for_the_whole_gap(self):
        """tpad used to be capped at 10s, leaving long scenes short."""
        filters = assembler.fit_duration_filters(2.0, 20.0, 30)
        tpad = next(f for f in filters if f.startswith("tpad"))
        assert float(tpad.split("stop_duration=")[1]) >= 18.0
        assert "trim=duration=20.00" in filters

    def test_long_clip_is_trimmed(self):
        assert assembler.fit_duration_filters(9.0, 5.0, 30) == ["setpts=PTS-STARTPTS", "trim=duration=5.00", "fps=fps=30"]

    def test_delogo_filters_combine_flow_and_custom(self):
        assert assembler.delogo_filters(True, "delogo=x=1:y=2:w=3:h=4") == [
            f"delogo={FLOW_WATERMARK_BOX.to_spec()}",
            "delogo=x=1:y=2:w=3:h=4",
        ]
        assert assembler.delogo_filters(False, None) == []

    def test_look_filters_follow_output_spec(self):
        crop = assembler.look_filters(VERTICAL_720P)[0]
        assert crop.endswith(f"scale={VERTICAL_720P.width}:{VERTICAL_720P.height}")

    @pytest.mark.parametrize(
        "ambient,finishing,expected_inputs",
        [(True, True, "[amb][room][voc]amix=inputs=3"), (False, True, "[room][voc]amix=inputs=2"), (True, False, "[amb][voc]amix=inputs=2")],
    )
    def test_audio_mix_graph(self, ambient, finishing, expected_inputs):
        graph = assembler.audio_mix_graph("null", ambient=ambient, finishing=finishing, sample_rate=48000)
        assert expected_inputs in graph
        assert ("equalizer" in graph) == finishing

    def test_voiceover_script_timecodes(self):
        scenes = [
            SceneDefinition(id=1, name="A", kind="FLOW_AI", narrator_text="Một", overlay_title="T1", overlay_subtitle=""),
            SceneDefinition(id=2, name="B", kind="FLOW_AI", narrator_text="Hai", overlay_title="", overlay_subtitle="S2"),
        ]
        text = assembler.render_voiceover_script(scenes, {1: 61.0}, "SP", heading="HEAD", default_scene_seconds=4.0)
        assert "🎙️ HEAD (VOICEOVER SCRIPT)" in text
        assert "[00:00 - 01:01] (61.00s) — A" in text
        assert "[01:01 - 01:05] (4.00s) — B" in text
        assert "Tổng thời lượng: 01:05 (65.0s)" in text


class TestFfmpegHelpers:
    @pytest.mark.parametrize(
        "spec,expected",
        [
            ("x=1:y=2:w=3:h=4", "delogo=x=1:y=2:w=3:h=4"),
            ("delogo=x=1:y=2:w=3:h=4", "delogo=x=1:y=2:w=3:h=4"),
            ("  ", None),
            (None, None),
        ],
    )
    def test_delogo_filter(self, spec, expected):
        assert delogo_filter(spec) == expected

    def test_encode_profile_metadata_toggle(self):
        assert EncodeProfile().container_args() == ["-map_metadata", "-1", "-fflags", "+bitexact"]
        assert EncodeProfile(strip_metadata=False).container_args() == []


class TestCoverText:
    @pytest.mark.parametrize("max_chars", [10, 15, 20, 26, 34])
    def test_never_exceeds_limit_and_keeps_question_mark(self, max_chars):
        res = format_cover_text("Bạn có đang gặp phiền toái với đống quần áo cồng kềnh mỗi ngày?", max_chars)
        assert len(res) <= max_chars
        assert res.endswith("?")
        assert not res[:-1].endswith(" ")

    def test_short_text_unchanged_but_upper(self):
        assert format_cover_text("móc dán tường", 34) == "MÓC DÁN TƯỜNG"
