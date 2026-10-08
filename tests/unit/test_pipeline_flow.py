"""Flow pipeline decisions and CLI mode selection, with a fake FlowKit client."""
from pathlib import Path

import pytest

from tools.common import flow_client
from tools.common.models import SceneDefinition
from tools.common.pipeline import flow as flow_pipeline
from tools.common.pipeline.cli import build_parser, select_runs
from tools.common.pipeline.context import ProductWorkspace, RunOptions
from tools.common.product import ProductInfo
from tools.common.prompts.realism import PHONE_HEADER
from tools.shopee_ad.config import PROFILE as SHOPEE
from tools.tiktok_ad.config import PROFILE as TIKTOK


def _scene(sid, prompt, kind="FLOW_AI", image_index=0):
    return SceneDefinition(id=sid, name=f"S{sid}", kind=kind, narrator_text="t", overlay_title=f"T{sid}",
                           overlay_subtitle="", prompt=prompt, image_index=image_index)


class TestSelectRuns:
    @pytest.mark.parametrize("mode,expected", [("both", (True, True)), ("local", (True, False)), ("zip", (True, False)), ("flow", (False, True))])
    def test_explicit_modes(self, mode, expected):
        assert select_runs(mode, SHOPEE, zip_has_video=False, flowkit_ready=lambda: pytest.fail("not probed")) == expected

    def test_auto_by_assets(self):
        assert select_runs("auto", SHOPEE, True, lambda: False) == (True, True)
        assert select_runs("auto", SHOPEE, False, lambda: True) == (False, True)

    def test_auto_by_flowkit(self):
        assert select_runs("auto", TIKTOK, False, lambda: True) == (True, True)
        assert select_runs("auto", TIKTOK, True, lambda: False) == (True, False)

    def test_parser_uses_platform_choices(self):
        assert build_parser(TIKTOK).parse_args([]).cta == "yellow_cart"
        with pytest.raises(SystemExit):
            build_parser(TIKTOK).parse_args(["--cta", "shopee"])
        assert build_parser(SHOPEE).parse_args(["--scene", "2", "3"]).scene == [2, 3]


class TestPromptHeuristics:
    def test_faceless_storyboard(self):
        assert flow_pipeline.is_faceless_storyboard("pov", [])
        assert flow_pipeline.is_faceless_storyboard("x", [_scene(1, "hands only"), _scene(2, "NO human face")])
        assert not flow_pipeline.is_faceless_storyboard("x", [_scene(1, "hands only"), _scene(2, "a woman smiles")])
        assert not flow_pipeline.is_faceless_storyboard("x", [])

    def test_human_scene_needs_a_whole_word(self):
        assert flow_pipeline.is_human_scene(_scene(1, "A woman unboxes it"), False)
        assert not flow_pipeline.is_human_scene(_scene(1, "the manual on a table"), False)  # "man" inside "manual"
        assert not flow_pipeline.is_human_scene(_scene(1, "macro shot of a woman's hand"), False)

    def test_product_reference_respects_opt_out(self):
        assert flow_pipeline.wants_product_reference(_scene(1, "hands hold the product"), False)
        opted_out = _scene(1, "hands hold the product")
        opted_out.use_product_ref = False
        assert not flow_pipeline.wants_product_reference(opted_out, False)


class FakeClient(flow_client.FlowKitClient):
    def __init__(self, fail_ids=()):
        super().__init__(base_url="http://fake")
        self.submitted = []
        self.reference_sets = []
        self.fail_ids = set(fail_ids)

    def submit_text_video(self, payload):
        self.submitted.append(("t2v", payload["prompt"], None))
        return {"workflows": [{"primary_media_id": payload["prompt"]}]}

    def submit_reference_video(self, payload):
        self.submitted.append(("r2v", payload["prompt"], payload["reference_media_ids"][0]))
        self.reference_sets.append(payload["reference_media_ids"])
        return {"operations": [{"operation": {"name": payload["prompt"]}}]}

    def upload_image(self, image_path, project_id=""):
        return "anchor-media"

    def poll_jobs(self, jobs, poll_interval_s=5, timeout_s=600, **_):
        result = flow_client.PollResult()
        for job in jobs:
            if job["scene_id"] in self.fail_ids:
                result.failed[job["scene_id"]] = "UNSAFE_GENERATION"
            else:
                result.urls[job["scene_id"]] = f"https://flow/{job['scene_id']}"
        return result


@pytest.fixture
def renderer_factory(tmp_path, monkeypatch):
    downloaded = []

    def fake_download(url, dest):
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_bytes(b"\0" * (flow_pipeline.MIN_FLOW_CLIP_BYTES + 1))
        downloaded.append(Path(dest).name)
        return dest

    monkeypatch.setattr(flow_pipeline, "download", fake_download)
    monkeypatch.setattr(flow_pipeline, "extract_frame", lambda video, out, t: out)
    monkeypatch.setattr(flow_pipeline.time, "sleep", lambda s: None)

    def make(client, **opts):
        product = ProductInfo(zip_path=Path("x.zip"), slug="x", name="X")
        ws = ProductWorkspace(product=product, root=tmp_path, variant="v")
        ws.create_dirs()
        return flow_pipeline.FlowRenderer(client, ws, RunOptions(style="flow_cinematic", **opts), "proj"), downloaded

    return make


class TestFlowRenderer:
    SCENES = [
        _scene(1, "A young woman introduces the gadget"),
        _scene(2, "The same woman uses it at her desk"),
        _scene(3, "macro shot, hands only, of the product"),
        _scene(4, "sunset skyline"),
    ]

    def test_character_mode_routes_each_scene(self, renderer_factory):
        client = FakeClient()
        renderer, downloaded = renderer_factory(client)
        renderer.render(self.SCENES, product_refs=["ref-a"])
        def sent(scene):
            return next((kind, ref) for kind, prompt, ref in client.submitted if scene.prompt.lower() in prompt.lower())

        assert sent(self.SCENES[0]) == ("r2v", "ref-a")  # anchor first, drawn from the real product
        assert sent(self.SCENES[1]) == ("r2v", "anchor-media")  # consistent character
        assert sent(self.SCENES[2]) == ("r2v", "ref-a")  # product reference
        assert sent(self.SCENES[3]) == ("t2v", None)
        assert all(prompt.startswith(PHONE_HEADER) and "Camera:" in prompt for _, prompt, _ in client.submitted)
        assert ["anchor-media", "ref-a"] in client.reference_sets  # character scenes also carry the product photo
        assert all(("Product:" in prompt) == (ref == "ref-a" or kind == "r2v") for kind, prompt, ref in client.submitted)
        assert sorted(downloaded) == [f"flow_cinematic_raw_0{i}.mp4" for i in range(1, 5)]

    def test_existing_clips_are_reused_and_scene_flag_targets_one(self, renderer_factory):
        client = FakeClient()
        renderer, _ = renderer_factory(client)
        renderer.render(self.SCENES, product_refs=[])
        client.submitted.clear()

        renderer.render(self.SCENES, product_refs=[])
        assert client.submitted == []

        targeted, _ = renderer_factory(client, target_scenes=[3])
        targeted.render(self.SCENES, product_refs=[])
        assert len(client.submitted) == 1 and self.SCENES[2].prompt.lower() in client.submitted[0][1].lower()

    def test_failures_keep_finished_clips_and_name_the_scenes(self, renderer_factory, caplog):
        client = FakeClient(fail_ids={2, 4})
        renderer, downloaded = renderer_factory(client)
        with pytest.raises(flow_client.FlowGenerationError, match="scene 2.*scene 4"):
            renderer.render(self.SCENES, product_refs=[])
        assert "flow_cinematic_raw_03.mp4" in downloaded
        assert "--scene 2 4" in caplog.text


class TestPlatformDefaults:
    """CLI defaults and file naming must match what each platform shipped with."""

    def test_shopee_defaults_to_no_cta_but_names_files_against_shopee_cta(self):
        from tools.shopee_ad.orchestrator import build_variant_suffix

        assert build_parser(SHOPEE).parse_args([]).cta == "none"
        assert build_variant_suffix(style="flow_cinematic", cta_mode="none") == "flow_cinematic_no-cta"
        assert build_variant_suffix(style="flow_cinematic", cta_mode="shopee") == "flow_cinematic"

    def test_tiktok_defaults_to_yellow_cart(self):
        from tools.tiktok_ad.orchestrator import build_variant_suffix

        assert build_parser(TIKTOK).parse_args([]).cta == "yellow_cart"
        assert build_variant_suffix(style="viral_hook") == "viral_hook"
