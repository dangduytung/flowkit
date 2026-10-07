"""Unit and integration tests for Shopee Ad Production Pipeline.

Tests cover:
1. BGM configuration resolution (opt-in, auto/random, style-matching, fallbacks).
2. Cover generator text formatting, punctuation preservation, and dynamic layout.
3. De-AI realism constraints in prompt generators (no uncanny gestures, hand constraints).
4. Video assembler FFmpeg rendering (sensor grain filter, Foley audio mixing, BGM concat).
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.common.models import SceneDefinition
from tools.shopee_ad.config import BGM_DIR, resolve_bgm_path
from tools.shopee_ad.cover_generator import _format_cover_text, create_cover_image
from tools.shopee_ad.product_parser import ProductInfo
from tools.shopee_ad.prompts import (
    build_cta_scene,
    build_faceless_pov_scenes,
    build_flow_cinematic_scenes,
    build_problem_solution_scenes,
)
from tools.shopee_ad.asset_extractor import (
    calculate_smart_subclip_starts,
    create_image_slide_clip,
)
from tools.shopee_ad.video_assembler import (
    assemble_scene_clip,
    concat_audio_files,
    concat_scenes,
    create_silent_version,
)

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None


def _make_test_clip(path: Path, duration: float = 0.5, with_audio: bool = True) -> Path:
    """Generate a lightweight synthetic 9:16 vertical test clip using ffmpeg lavfi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=navy:s=720x1280:d={duration}:r=30"]
    if with_audio:
        cmd.extend(["-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}"])
        cmd.extend([
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "64k", "-ar", "48000",
            "-shortest", str(path),
        ])
    else:
        cmd.extend([
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-an", str(path),
        ])
    subprocess.run(cmd, capture_output=True, check=True, timeout=30)
    return path


def _make_test_audio(path: Path, duration: float = 0.5) -> Path:
    """Generate a lightweight synthetic audio file using WAV PCM to ensure universal compatibility."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=880:duration={duration}",
        "-c:a", "pcm_s16le", "-ar", "48000",
        str(path),
    ], capture_output=True, check=True, timeout=30)
    return path


def _make_test_image(path: Path) -> Path:
    """Generate a synthetic test image."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=orange:s=400x400:d=1",
        "-frames:v", "1", str(path),
    ], capture_output=True, check=True, timeout=30)
    return path


# ===========================================================================
# 1. Test BGM Configuration Resolution
# ===========================================================================
class TestBgmConfig:
    def test_resolve_bgm_none_by_default(self):
        """Default behavior must be None (no background music)."""
        assert resolve_bgm_path(None) is None
        assert resolve_bgm_path("") is None

    @pytest.mark.parametrize("off_val", ["none", "false", "0", "no", "off"])
    def test_resolve_bgm_explicit_off(self, off_val):
        """Passing explicit negation flags must always return None."""
        assert resolve_bgm_path(off_val) is None

    def test_resolve_bgm_auto_picks_valid_track(self):
        """Passing 'auto' or 'random' should pick an existing track from assets/bgm/."""
        track = resolve_bgm_path("auto")
        assert track is not None
        assert track.exists()
        assert track.is_file()
        assert track.suffix.lower() in [".mp3", ".wav", ".m4a"]

    def test_resolve_bgm_by_style(self):
        """Passing style should match a track containing the style name if available."""
        track = resolve_bgm_path("auto", style="lifestyle")
        assert track is not None
        assert "lifestyle" in track.name.lower()

    def test_resolve_bgm_direct_filename(self):
        """Passing an exact filename in assets/bgm/ should resolve properly."""
        filename = "01_Cheerful_Glow_general_household_ad.mp3"
        track = resolve_bgm_path(filename)
        assert track is not None
        assert track.exists()
        assert track.name == filename

    def test_resolve_bgm_custom_file(self, tmp_path):
        """Passing a direct absolute Path should resolve that specific file."""
        custom_audio = tmp_path / "custom.mp3"
        custom_audio.write_bytes(b"ID3_fake_audio_bytes")
        resolved = resolve_bgm_path(custom_audio)
        assert resolved == custom_audio

    def test_resolve_bgm_nonexistent_returns_none(self):
        """Nonexistent paths or filenames return None."""
        assert resolve_bgm_path("completely_imaginary_audio_file.mp3") is None


# ===========================================================================
# 2. Test Cover Generator & Text Formatting
# ===========================================================================
class TestCoverGenerator:
    def test_format_cover_text_short(self):
        """Short text stays unchanged but uppercase."""
        res = _format_cover_text("móc dán tường", max_chars=34)
        assert res == "MÓC DÁN TƯỜNG"

    def test_format_cover_text_truncates_at_word_boundary(self):
        """Long text should truncate without cutting words in the middle."""
        long_text = "Combo 50 móc dán tường siêu dính chịu lực 10kg đa năng"
        res = _format_cover_text(long_text, max_chars=25)
        assert len(res) <= 25
        assert not res.endswith("DÍNH CH")  # Did not cut inside word

    def test_format_cover_text_preserves_question_mark(self):
        """Questions must retain their '?' after word truncation."""
        question_text = "Bạn có đang gặp khó khăn khi treo đồ nặng trong nhà bếp?"
        res = _format_cover_text(question_text, max_chars=30)
        assert res.endswith("?")

    def test_format_cover_text_preserves_exclamation_mark(self):
        """Exclamations must retain their '!' after word truncation."""
        exclaim_text = "Giải pháp hoàn hảo giúp nhà tắm luôn gọn gàng ngăn nắp!"
        res = _format_cover_text(exclaim_text, max_chars=30)
        assert res.endswith("!")

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_cover_image_from_video(self, tmp_path):
        """create_cover_image should extract a clean frame and generate a valid JPG."""
        video_clip = _make_test_clip(tmp_path / "test_clip.mp4", duration=1.0)
        product = ProductInfo(
            zip_path=tmp_path / "prod.zip",
            slug="test_product",
            name="Móc Dán Tường Đa Năng",
        )
        scene = SceneDefinition(
            id=1,
            name="Hook",
            kind="FLOW_AI",
            narrator_text="Intro",
            overlay_title="TIỆN LỢI BẤT NGỜ?",
            overlay_subtitle="Móc dán tường",
        )
        out_cover = tmp_path / "cover.jpg"

        res = create_cover_image(
            source_clip_or_video=video_clip,
            product=product,
            scenes=[scene],
            output_cover_path=out_cover,
            time_offset_s=0.2,
        )

        assert res.exists()
        assert res.stat().st_size > 1000  # Non-trivial image file


# ===========================================================================
# 3. Test Prompt Constraints & De-AI Realism
# ===========================================================================
class TestPromptConstraints:
    def test_no_uncanny_gestures_in_cinematic_prompts(self):
        """Ensure no thumbs-up or peace sign gestures are requested in prompts."""
        categories = ["BEAUTY_SKINCARE", "HEALTH_FITNESS", "KITCHEN_HOME", "TECH_GADGETS"]
        for cat in categories:
            scenes = build_flow_cinematic_scenes(
                category=cat,
                clean_title="Bộ Nồi Đa Năng",
                feat1_title="Chống dính",
                feat1_desc="Lớp men bền bỉ",
                feat2_title="Tiết kiệm dầu",
                feat2_desc="Tốt cho sức khỏe",
                social_proof_title="Hơn 10k người mua",
            )
            for sc in scenes:
                p_lower = (sc.prompt or "").lower()
                # Positive forbidden gestures
                assert "thumbs-up" not in p_lower.replace("no thumbs-up", "")
                assert "thumbs up" not in p_lower.replace("no thumbs up", "")
                assert "peace sign" not in p_lower.replace("no peace sign", "")

    def test_enforced_negative_constraints_in_problem_solution(self):
        """Problem-solution prompts must explicitly include finger & gesture safety constraints."""
        scenes = build_problem_solution_scenes(
            category="GENERAL_LIFESTYLE",
            clean_title="Túi Nén Hút Chân Không",
            feat1_title="Gấp gọn thông minh",
            feat1_desc="Chứa trọn 10 bộ đồ",
            feat2_title="Chống nước",
            feat2_desc="Bền bỉ chắc chắn",
        )
        outcome_scene = scenes[-1]
        p_lower = (outcome_scene.prompt or "").lower()
        assert "no thumbs-up" in p_lower
        assert "no distorted fingers" in p_lower

    def test_faceless_pov_enforces_hand_realism(self):
        """Faceless POV prompts must enforce no face and natural hand resting."""
        scenes = build_faceless_pov_scenes(
            category="TECH_GADGETS",
            clean_title="Túi Nén Du Lịch",
            feat1_title="Nén gọn 3 lần",
            feat1_desc="Tiết kiệm nửa vali",
            feat2_title="Khóa kéo kín",
            feat2_desc="Chống ẩm mốc",
        )
        for sc in scenes:
            p_lower = (sc.prompt or "").lower()
            assert "no face" in p_lower or "hands only" in p_lower or "no human face" in p_lower

    def test_cta_scenes_finger_constraints(self):
        """CTA scenes must explicitly forbid thumbs-up and enforce exactly 5 fingers."""
        faceless_cta = build_cta_scene(
            scene_id=5,
            cta_mode="follow",
            category="TECH_GADGETS",
            style="faceless_pov",
            clean_title="Túi Nén Du Lịch",
        )
        assert faceless_cta is not None
        assert "strictly exactly 5 fingers" in (faceless_cta.prompt or "")
        assert "no thumbs-up" in (faceless_cta.prompt or "").lower()

        human_cta = build_cta_scene(
            scene_id=5,
            cta_mode="shopee",
            category="TECH_GADGETS",
            style="flow_cinematic",
            clean_title="Túi Nén Du Lịch",
        )
        assert human_cta is not None
        assert "no thumbs-up" in (human_cta.prompt or "").lower()

    def test_scene_definition_product_ref_default(self):
        """SceneDefinition.use_product_ref must default to True."""
        scene = SceneDefinition(
            id=1,
            name="Test",
            kind="FLOW_AI",
            narrator_text="Text",
            overlay_title="Title",
            overlay_subtitle="Subtitle",
        )
        assert scene.use_product_ref is True


# ===========================================================================
# 4. Test Video Assembler (FFmpeg Audio & Video Processing)
# ===========================================================================
class TestVideoAssembler:
    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_with_foley_and_voice(self, tmp_path):
        """assemble_scene_clip should mix native Foley with voiceover and apply sensor grain."""
        video_clip = _make_test_clip(tmp_path / "scene_with_foley.mp4", duration=0.5, with_audio=True)
        voice_clip = _make_test_audio(tmp_path / "voice.wav", duration=0.5)
        out_clip = tmp_path / "assembled_foley.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=voice_clip,
            output_path=out_clip,
            target_duration=0.5,
            title_text="TEST TITLE",
            subtitle_text="Test Subtitle",
        )

        assert res.exists()
        assert res.stat().st_size > 1000

        # Check audio stream exists in output
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(res)],
            capture_output=True, text=True, check=True,
        )
        assert bool(probe.stdout.strip())

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_silent_no_voice(self, tmp_path):
        """assemble_scene_clip without voice audio should produce a silent stereo track."""
        video_clip = _make_test_clip(tmp_path / "scene_raw.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "assembled_silent.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=None,
            output_path=out_clip,
            target_duration=0.5,
        )

        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_concat_scenes_without_bgm(self, tmp_path):
        """concat_scenes without BGM should concatenate clips correctly."""
        clip1 = _make_test_clip(tmp_path / "c1.mp4", duration=0.5, with_audio=True)
        clip2 = _make_test_clip(tmp_path / "c2.mp4", duration=0.5, with_audio=True)
        out_concat = tmp_path / "final_no_bgm.mp4"

        res = concat_scenes([clip1, clip2], out_concat, bgm_path=None)
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_concat_scenes_with_bgm(self, tmp_path):
        """concat_scenes with BGM should loop BGM and mix at ducked volume."""
        clip1 = _make_test_clip(tmp_path / "c1.mp4", duration=0.5, with_audio=True)
        clip2 = _make_test_clip(tmp_path / "c2.mp4", duration=0.5, with_audio=True)
        out_concat = tmp_path / "final_with_bgm.mp4"

        # Use the actual bundled BGM track from assets/bgm/
        bgm_track = BGM_DIR / "01_Cheerful_Glow_general_household_ad.mp3"
        assert bgm_track.exists(), "Bundled BGM track should exist"

        res = concat_scenes([clip1, clip2], out_concat, bgm_path=bgm_track)
        assert res.exists()
        assert res.stat().st_size > 1000

        # Verify output has both video and audio
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", str(res)],
            capture_output=True, text=True, check=True,
        )
        stream_types = probe.stdout.strip().splitlines()
        assert "video" in stream_types
        assert "audio" in stream_types

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_with_unprefixed_delogo(self, tmp_path):
        """assemble_scene_clip should safely handle delogo string without 'delogo=' prefix."""
        video_clip = _make_test_clip(tmp_path / "scene_delogo.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "assembled_delogo.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=None,
            output_path=out_clip,
            target_duration=0.5,
            delogo="x=20:y=30:w=40:h=50",
        )
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_cover_image_with_unprefixed_delogo(self, tmp_path):
        """create_cover_image should safely handle delogo string without 'delogo=' prefix."""
        video_clip = _make_test_clip(tmp_path / "cover_raw.mp4", duration=0.5, with_audio=False)
        product = ProductInfo(
            zip_path=tmp_path / "prod.zip",
            slug="test_product",
            name="Móc Dán Tường",
        )
        out_cover = tmp_path / "cover_delogo.jpg"

        res = create_cover_image(
            source_clip_or_video=video_clip,
            product=product,
            scenes=[],
            output_cover_path=out_cover,
            time_offset_s=0.1,
            delogo="x=20:y=30:w=40:h=50",
        )
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_with_de_ai_disabled(self, tmp_path):
        """assemble_scene_clip with de_ai=False should bypass breathing and room tone filters."""
        video_clip = _make_test_clip(tmp_path / "scene_plain.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "assembled_plain.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=None,
            output_path=out_clip,
            target_duration=0.5,
            de_ai=False,
        )
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_silent_version(self, tmp_path):
        """create_silent_version should produce a silent vertical video with stereo null track."""
        video_clip = _make_test_clip(tmp_path / "master.mp4", duration=0.5, with_audio=True)
        out_silent = tmp_path / "master_silent.mp4"

        res = create_silent_version(video_clip, out_silent)
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_concat_audio_files(self, tmp_path):
        """concat_audio_files should combine individual audio tracks into a master mp3."""
        a1 = _make_test_audio(tmp_path / "a1.wav", duration=0.3)
        a2 = _make_test_audio(tmp_path / "a2.wav", duration=0.3)
        out_master = tmp_path / "master_voice.mp3"

        res = concat_audio_files([a1, a2], out_master)
        assert res.exists()
        assert res.stat().st_size > 1000


# ===========================================================================
# 5. Test Asset Extractor (Image Animation & Smart Subclip Cutting)
# ===========================================================================
class TestAssetExtractor:
    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_image_slide_clip(self, tmp_path):
        """create_image_slide_clip converts still image into Ken-Burns animated vertical video."""
        img_path = _make_test_image(tmp_path / "product.jpg")
        out_clip = tmp_path / "slide.mp4"

        res = create_image_slide_clip(img_path, duration=0.5, output_path=out_clip)
        assert res.exists()
        assert res.stat().st_size > 1000

    def test_calculate_smart_subclip_starts_basic(self, tmp_path):
        """calculate_smart_subclip_starts generates valid start times."""
        video_clip = _make_test_clip(tmp_path / "raw.mp4", duration=4.0, with_audio=False)
        starts, glitches = calculate_smart_subclip_starts(video_clip, num_scenes=3, total_dur=4.0)
        assert len(starts) == 3
        assert starts[0] == 0.0

    def test_vacuum_cleaner_archetype_prompts(self):
        """Vacuum cleaner archetype should produce specialized prompts with attached nozzle."""
        from tools.shopee_ad.prompts import build_faceless_pov_scenes
        from tools.shopee_ad.product_parser import ProductInfo

        scenes = build_faceless_pov_scenes(
            category="KITCHEN_HOME",
            clean_title="máy hút bụi cầm tay tamashio",
            feat1_title="LỰC HÚT MẠNH MẼ",
            feat1_desc="Lực hút 12000Pa",
            feat2_title="ĐẦU HÚT ĐA NĂNG",
            feat2_desc="6 đầu hút thông minh",
        )
        assert len(scenes) == 4
        # Scene 1 must avoid attaching/plugging parts
        assert "NO attaching parts" in scenes[0].prompt
        # Scene 3 must specify nozzle is already attached (avoiding AI mechanical snap glitch)
        sc3 = scenes[2]
        assert "already securely attached" in sc3.prompt
        assert "couch cushion" in sc3.prompt or "textured" in sc3.prompt
        # Scene 4 must avoid twisting/pulling parts and show filter under running water
        assert "NO twisting" in scenes[3].prompt
        assert "gentle stream of fresh tap water" in scenes[3].prompt



