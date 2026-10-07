"""Tests for shared pipeline building blocks: scene selection, storyboard IO, narration."""
import json
from pathlib import Path

import pytest

from tools.common import storyboard_io
from tools.common.models import SceneDefinition
from tools.common.pipeline import voice
from tools.common.pipeline.selection import SceneSelection, warn_unknown_scene_ids


def _scene(scene_id: int, **overrides) -> SceneDefinition:
    data = dict(
        id=scene_id,
        name=f"Scene {scene_id}",
        kind="FLOW_AI",
        narrator_text=f"text {scene_id}",
        overlay_title=f"TITLE {scene_id}",
        overlay_subtitle=f"sub {scene_id}",
        prompt=f"prompt {scene_id}",
    )
    data.update(overrides)
    return SceneDefinition(**data)


class TestSceneSelection:
    def test_empty_ids_mean_full_run(self):
        for ids in (None, [], ()):
            sel = SceneSelection.from_ids(ids)
            assert not sel.is_partial
            assert sel.is_targeted(7)

    def test_full_run_reuses_unless_forced(self):
        sel = SceneSelection()
        assert sel.keep_existing(1, artifact_ready=True)
        assert not sel.keep_existing(1, artifact_ready=True, force_rebuild=True)
        assert not sel.keep_existing(1, artifact_ready=False)

    def test_partial_run_rebuilds_only_targets(self):
        sel = SceneSelection.from_ids([2])
        assert sel.keep_existing(1, artifact_ready=True, force_rebuild=True)
        assert not sel.keep_existing(2, artifact_ready=True)
        assert not sel.keep_existing(1, artifact_ready=False)

    def test_unknown_ids_are_reported(self, caplog):
        sel = SceneSelection.from_ids([2, 9])
        with caplog.at_level("WARNING", logger="tools"):
            assert warn_unknown_scene_ids(sel, [1, 2, 3]) == [9]
        assert "[9]" in caplog.text
        assert SceneSelection().unknown_ids([1]) == []


class TestStoryboardIO:
    def test_round_trip_keeps_metadata(self, tmp_path):
        path = tmp_path / "sb.json"
        storyboard_io.write_storyboard(path, [_scene(1)], {"style": "pov"})
        assert storyboard_io.read_storyboard(path)[0].overlay_title == "TITLE 1"
        # Rewriting without metadata keeps what is on disk.
        storyboard_io.write_storyboard(path, [_scene(1, overlay_title="NEW")])
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["style"] == "pov"
        assert data["scenes"][0]["overlay_title"] == "NEW"

    def test_reads_legacy_bare_list_and_ignores_unknown_keys(self, tmp_path):
        path = tmp_path / "legacy.json"
        legacy = [{**_scene(1).__dict__, "obsolete_field": 1}]
        path.write_text(json.dumps(legacy), encoding="utf-8")
        scenes = storyboard_io.read_storyboard(path)
        assert [s.id for s in scenes] == [1]

    def test_unreadable_file_returns_none(self, tmp_path):
        path = tmp_path / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        assert storyboard_io.read_storyboard(path) is None
        assert storyboard_io.read_storyboard(tmp_path / "missing.json") is None

    def test_load_or_create_preserves_hand_edits(self, tmp_path):
        path = tmp_path / "sb.json"
        calls = []

        def generate():
            calls.append(1)
            return [_scene(1), _scene(2)]

        storyboard_io.load_or_create(path, generate)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["scenes"][0]["overlay_title"] = "HAND EDIT"
        path.write_text(json.dumps(data), encoding="utf-8")

        scenes = storyboard_io.load_or_create(path, generate)
        assert scenes[0].overlay_title == "HAND EDIT"
        assert len(calls) == 1

        storyboard_io.load_or_create(path, generate, force=True)
        assert len(calls) == 2

    def test_load_or_create_rebuilds_when_too_short(self, tmp_path):
        path = tmp_path / "sb.json"
        storyboard_io.write_storyboard(path, [_scene(1)])
        scenes = storyboard_io.load_or_create(path, lambda: [_scene(1), _scene(2)], min_scenes=2)
        assert len(scenes) == 2

    def test_refresh_targeted_scenes_only_touches_targets(self, tmp_path):
        path = tmp_path / "sb.json"
        scenes = [_scene(1, overlay_title="KEEP", image_index=3), _scene(2, overlay_title="OLD", image_index=4)]
        fresh = [_scene(1, overlay_title="FRESH1"), _scene(2, overlay_title="FRESH2")]

        refreshed = storyboard_io.refresh_targeted_scenes(scenes, {2, 5}, path, lambda: fresh)

        assert refreshed == [2]
        assert scenes[0].overlay_title == "KEEP"
        assert scenes[1].overlay_title == "FRESH2"
        assert scenes[1].image_index == 4  # asset/timing fields are not refreshed
        assert storyboard_io.read_storyboard(path)[1].overlay_title == "FRESH2"

    def test_refresh_without_targets_is_a_no_op(self, tmp_path):
        path = tmp_path / "sb.json"
        assert storyboard_io.refresh_targeted_scenes([_scene(1)], None, path, lambda: pytest.fail("called")) == []
        assert not path.exists()


class TestNarration:
    @pytest.fixture
    def fake_tts(self, monkeypatch):
        calls = []

        def synthesize(text, out):
            calls.append(Path(out).name)
            Path(out).write_bytes(b"\0" * (voice.MIN_NARRATION_BYTES + 1))
            return 2.0

        monkeypatch.setattr(voice, "probe_duration", lambda path: 1.5)
        return synthesize, calls

    def test_full_run_voices_every_scene(self, tmp_path, fake_tts):
        synthesize, calls = fake_tts
        result = voice.synthesize_narration([_scene(1), _scene(2)], tmp_path, "v", synthesize)
        assert len(calls) == 2
        assert result.durations == {1: 2.0, 2: 2.0}

    def test_full_run_revoices_even_if_audio_exists(self, tmp_path, fake_tts):
        synthesize, calls = fake_tts
        voice.synthesize_narration([_scene(1)], tmp_path, "v", synthesize)
        voice.synthesize_narration([_scene(1)], tmp_path, "v", synthesize)
        assert len(calls) == 2

    def test_partial_run_reuses_untargeted_audio(self, tmp_path, fake_tts):
        synthesize, calls = fake_tts
        scenes = [_scene(1), _scene(2)]
        voice.synthesize_narration(scenes, tmp_path, "v", synthesize)
        calls.clear()

        result = voice.synthesize_narration(scenes, tmp_path, "v", synthesize, SceneSelection.from_ids([2]))

        assert calls == ["v_scene_02.wav"]
        assert result.durations == {1: 1.5, 2: 2.0}
        assert result.files[1] == voice.narration_path(tmp_path, "v", 1)

    def test_partial_run_voices_missing_untargeted_audio(self, tmp_path, fake_tts):
        synthesize, calls = fake_tts
        voice.synthesize_narration([_scene(1)], tmp_path, "v", synthesize, SceneSelection.from_ids([2]))
        assert calls == ["v_scene_01.wav"]

    def test_silent_timing(self):
        result = voice.silent_timing([_scene(1), _scene(2)], 4.0)
        assert result.files == {1: None, 2: None}
        assert result.durations == {1: 4.0, 2: 4.0}
