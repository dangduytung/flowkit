"""Unit and integration tests for TikTok Ad Production Pipeline.

Tests cover:
1. BGM configuration resolution (opt-in, auto/random, style-matching, fallbacks).
2. Cover generator text formatting, punctuation preservation, and dynamic layout.
3. Prompt constraints and de-AI realism in TikTok storyboard / prompts.
4. Video assembler FFmpeg rendering with De-AI engine (camera breathing, room tone dither, delogo normalization, metadata scrubbing, silent exports).
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.common.models import SceneDefinition
from tools.tiktok_ad.config import BGM_DIR, resolve_bgm_path
from tools.tiktok_ad.cover_generator import _format_cover_text, create_cover_image
from tools.tiktok_ad.product_parser import ProductInfo
from tools.tiktok_ad.prompts import (
    build_faceless_pov_scenes,
    build_flow_cinematic_scenes,
    build_lifestyle_edc_scenes,
    build_problem_solution_scenes,
    build_viral_hook_scenes,
)
from tools.tiktok_ad.asset_extractor import (
    calculate_smart_subclip_starts,
    create_image_slide_clip,
)
from tools.tiktok_ad.video_assembler import (
    assemble_scene_clip,
    concat_audio_files,
    concat_scenes,
    create_silent_version,
)

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None


def _make_test_clip(path: Path, duration: float = 0.5, with_audio: bool = True) -> Path:
    """Generate a lightweight synthetic 9:16 vertical test clip using ffmpeg lavfi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=darkgreen:s=720x1280:d={duration}:r=30"]
    if with_audio:
        cmd.extend(["-f", "lavfi", "-i", f"sine=frequency=520:duration={duration}"])
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
    """Generate a lightweight synthetic audio file using WAV PCM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=950:duration={duration}",
        "-c:a", "pcm_s16le", "-ar", "48000",
        str(path),
    ], capture_output=True, check=True, timeout=30)
    return path


def _make_test_image(path: Path) -> Path:
    """Generate a synthetic test image."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=darkblue:s=400x400:d=1",
        "-frames:v", "1", str(path),
    ], capture_output=True, check=True, timeout=30)
    return path


# ===========================================================================
# 1. Test BGM Configuration Resolution
# ===========================================================================
class TestTikTokBgmConfig:
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
        custom_audio = tmp_path / "custom_tiktok.mp3"
        custom_audio.write_bytes(b"ID3_fake_audio_bytes")
        resolved = resolve_bgm_path(custom_audio)
        assert resolved == custom_audio

    def test_resolve_bgm_nonexistent_returns_none(self):
        """Nonexistent paths or filenames return None."""
        assert resolve_bgm_path("completely_imaginary_audio_file.mp3") is None


# ===========================================================================
# 2. Test Cover Generator & Text Formatting
# ===========================================================================
class TestTikTokCoverGenerator:
    def test_format_cover_text_short(self):
        """Short text stays unchanged but uppercase."""
        res = _format_cover_text("túi nén du lịch", max_chars=34)
        assert res == "TÚI NÉN DU LỊCH"

    def test_format_cover_text_truncates_at_word_boundary(self):
        """Long text truncates cleanly at word boundary."""
        long_text = "Bí quyết sắp xếp đồ đạc cực nhanh gọn cho người bận rộn"
        res = _format_cover_text(long_text, max_chars=25)
        assert len(res) <= 25
        assert not res.endswith("NGƯỜI B")

    def test_format_cover_text_preserves_question_mark(self):
        """Questions must keep their '?' after word truncation."""
        question_text = "Bạn đã biết cách gấp gọn vali chỉ trong năm phút chưa?"
        res = _format_cover_text(question_text, max_chars=30)
        assert res.endswith("?")

    def test_format_cover_text_preserves_exclamation_mark(self):
        """Exclamations must keep their '!' after word truncation."""
        exclaim_text = "Giải pháp thần thánh cứu cánh chiếc vali quá tải!"
        res = _format_cover_text(exclaim_text, max_chars=30)
        assert res.endswith("!")

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_cover_image_from_video(self, tmp_path):
        """create_cover_image extracts frame, burns typography and sensor grain."""
        video_clip = _make_test_clip(tmp_path / "tiktok_clip.mp4", duration=1.0)
        product = ProductInfo(
            zip_path=tmp_path / "tiktok_prod.zip",
            slug="tiktok_gadget",
            name="Bộ Cắt Rau Củ Đa Năng",
        )
        scene = SceneDefinition(
            id=1,
            name="Viral Hook",
            kind="FLOW_AI",
            narrator_text="Intro hook",
            overlay_title="CẮT CỰC NHANH?",
            overlay_subtitle="Bộ cắt rau củ",
        )
        out_cover = tmp_path / "tiktok_cover.jpg"

        res = create_cover_image(
            source_clip_or_video=video_clip,
            product=product,
            scenes=[scene],
            output_cover_path=out_cover,
            time_offset_s=0.2,
        )

        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_cover_image_with_unprefixed_delogo(self, tmp_path):
        """create_cover_image safely handles delogo string without 'delogo=' prefix."""
        video_clip = _make_test_clip(tmp_path / "tiktok_clip_delogo.mp4", duration=1.0)
        product = ProductInfo(
            zip_path=tmp_path / "tiktok_prod.zip",
            slug="tiktok_gadget",
            name="Bộ Cắt Rau Củ Đa Năng",
        )
        out_cover = tmp_path / "tiktok_cover_delogo.jpg"

        res = create_cover_image(
            source_clip_or_video=video_clip,
            product=product,
            scenes=[],
            output_cover_path=out_cover,
            time_offset_s=0.2,
            delogo="x=40:y=60:w=120:h=80",
        )
        assert res.exists()
        assert res.stat().st_size > 1000


# ===========================================================================
# 3. Test Prompt Constraints & Safety
# ===========================================================================
class TestTikTokPromptConstraints:
    def test_faceless_pov_enforces_faceless_consistency(self):
        """Faceless POV scenes must strictly specify faceless / hands only."""
        scenes = build_faceless_pov_scenes(
            category="KITCHEN_HOME",
            clean_title="Bộ Nồi Đa Năng",
            feat1_title="Chống dính",
            feat1_desc="Lớp men bền bỉ",
            feat2_title="Dễ rửa",
            feat2_desc="Tiết kiệm thời gian",
            social_proof_title="Hơn 10k người mua",
        )
        for sc in scenes:
            p_lower = (sc.prompt or "").lower()
            assert "faceless" in p_lower or "no face" in p_lower or "hands only" in p_lower or "no human face" in p_lower

    def test_viral_hook_scenes_generated(self):
        """Viral hook generates minimum 3 scenes with non-empty prompts."""
        scenes = build_viral_hook_scenes(
            category="TECH_GADGETS",
            clean_title="Cáp Sạc Nhanh",
            feat1_title="Sạc siêu tốc",
            feat1_desc="Đầy pin trong 30 phút",
            feat2_title="Dây dù bền bỉ",
            feat2_desc="Chống đứt gãy",
            social_proof_title="Hơn 5k đánh giá 5 sao",
        )
        assert len(scenes) >= 3
        for sc in scenes:
            assert sc.prompt and len(sc.prompt) > 20

    def test_problem_solution_scenes_generated(self):
        """Problem solution generates minimum 3 scenes with structured pain & rescue."""
        scenes = build_problem_solution_scenes(
            category="HOME_CLEANING",
            clean_title="Cây Lau Nhà Thông Minh",
            feat1_title="Xoay 360 độ",
            feat1_desc="Lau sạch mọi góc ngách",
            feat2_title="Tự vắt thông minh",
            feat2_desc="Không bẩn tay",
        )
        assert len(scenes) >= 3
        for sc in scenes:
            assert sc.narrator_text and len(sc.narrator_text) > 10
            assert sc.overlay_title and len(sc.overlay_title) > 0

    def test_lifestyle_edc_scenes_generated(self):
        """Lifestyle EDC generates valid scenes."""
        scenes = build_lifestyle_edc_scenes(
            category="FASHION_ACCESSORIES",
            clean_title="Ví Da Nam Mini",
            feat1_title="Nhỏ gọn",
            feat1_desc="Để vừa mọi túi áo",
            feat2_title="Da bò thật",
            feat2_desc="Bền đẹp theo năm tháng",
        )
        assert len(scenes) >= 3
        for sc in scenes:
            assert sc.prompt and len(sc.prompt) > 20

    def test_flow_cinematic_scenes_generated(self):
        """Flow cinematic scenes maintain consistent character persona prompts."""
        scenes = build_flow_cinematic_scenes(
            category="BEAUTY_SKINCARE",
            clean_title="Serum Dưỡng Trắng",
            feat1_title="Sáng da mờ thâm",
            feat1_desc="Hiệu quả sau 7 ngày",
            feat2_title="Thẩm thấu nhanh",
            feat2_desc="Không bết dính",
            social_proof_title="100k người đã trải nghiệm",
        )
        assert len(scenes) >= 3
        for sc in scenes:
            assert sc.prompt and len(sc.prompt) > 20


# ===========================================================================
# 4. Test Video Assembler (FFmpeg De-AI Realism & Audio Processing)
# ===========================================================================
class TestTikTokVideoAssembler:
    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_with_foley_and_de_ai(self, tmp_path):
        """assemble_scene_clip mixes Foley with voiceover, brown noise room tone, and handheld breathing."""
        video_clip = _make_test_clip(tmp_path / "tt_foley.mp4", duration=0.5, with_audio=True)
        voice_clip = _make_test_audio(tmp_path / "tt_voice.wav", duration=0.5)
        out_clip = tmp_path / "tt_assembled.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=voice_clip,
            output_path=out_clip,
            target_duration=0.5,
            title_text="TIKTOK HOOK",
            subtitle_text="Test Subtitle",
            de_ai=True,
        )

        assert res.exists()
        assert res.stat().st_size > 1000

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(res)],
            capture_output=True, text=True, check=True,
        )
        assert bool(probe.stdout.strip())

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_silent_mode(self, tmp_path):
        """assemble_scene_clip with no voice audio produces valid silent stereo container."""
        video_clip = _make_test_clip(tmp_path / "tt_raw.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "tt_assembled_silent.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=None,
            output_path=out_clip,
            target_duration=0.5,
            de_ai=True,
        )

        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_unprefixed_delogo(self, tmp_path):
        """assemble_scene_clip handles unprefixed delogo parameter string."""
        video_clip = _make_test_clip(tmp_path / "tt_delogo.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "tt_delogo_out.mp4"

        res = assemble_scene_clip(
            video_path=video_clip,
            audio_path=None,
            output_path=out_clip,
            target_duration=0.5,
            delogo="x=30:y=50:w=100:h=70",
        )

        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_concat_scenes_without_bgm(self, tmp_path):
        """concat_scenes without BGM concatenates clips cleanly."""
        clip1 = _make_test_clip(tmp_path / "tt_c1.mp4", duration=0.5, with_audio=True)
        clip2 = _make_test_clip(tmp_path / "tt_c2.mp4", duration=0.5, with_audio=True)
        out_concat = tmp_path / "tt_final.mp4"

        res = concat_scenes([clip1, clip2], out_concat, bgm_path=None)
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_concat_scenes_with_bgm(self, tmp_path):
        """concat_scenes with BGM mixes looped audio at ducked volume."""
        clip1 = _make_test_clip(tmp_path / "tt_c1.mp4", duration=0.5, with_audio=True)
        clip2 = _make_test_clip(tmp_path / "tt_c2.mp4", duration=0.5, with_audio=True)
        out_concat = tmp_path / "tt_final_bgm.mp4"

        bgm_track = BGM_DIR / "01_Cheerful_Glow_general_household_ad.mp3"
        assert bgm_track.exists()

        res = concat_scenes([clip1, clip2], out_concat, bgm_path=bgm_track)
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_silent_version(self, tmp_path):
        """create_silent_version exports clean silent copy with stereo null stream."""
        clip = _make_test_clip(tmp_path / "tt_master.mp4", duration=0.5, with_audio=True)
        out_silent = tmp_path / "tt_silent_copy.mp4"

        res = create_silent_version(clip, out_silent)
        assert res.exists()
        assert res.stat().st_size > 1000

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_assemble_clip_with_de_ai_disabled(self, tmp_path):
        """assemble_scene_clip with de_ai=False should bypass breathing and room tone filters."""
        video_clip = _make_test_clip(tmp_path / "tt_plain.mp4", duration=0.5, with_audio=False)
        out_clip = tmp_path / "tt_assembled_plain.mp4"

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
    def test_concat_audio_files(self, tmp_path):
        """concat_audio_files combines individual scene audios into a master mp3."""
        a1 = _make_test_audio(tmp_path / "tt_a1.wav", duration=0.3)
        a2 = _make_test_audio(tmp_path / "tt_a2.wav", duration=0.3)
        out_master = tmp_path / "tt_master_voice.mp3"

        res = concat_audio_files([a1, a2], out_master)
        assert res.exists()
        assert res.stat().st_size > 1000


# ===========================================================================
# 5. Test Asset Extractor (Image Animation & Smart Subclip Cutting)
# ===========================================================================
class TestTikTokAssetExtractor:
    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="FFmpeg not installed")
    def test_create_image_slide_clip(self, tmp_path):
        """create_image_slide_clip converts still image into Ken-Burns animated vertical video."""
        img_path = _make_test_image(tmp_path / "product.jpg")
        out_clip = tmp_path / "tt_slide.mp4"

        res = create_image_slide_clip(img_path, duration=0.5, output_path=out_clip)
        assert res.exists()
        assert res.stat().st_size > 1000

    def test_calculate_smart_subclip_starts_basic(self, tmp_path):
        """calculate_smart_subclip_starts generates valid start times."""
        video_clip = _make_test_clip(tmp_path / "tt_raw.mp4", duration=4.0, with_audio=False)
        starts, glitches = calculate_smart_subclip_starts(video_clip, num_scenes=3, total_dur=4.0)
        assert len(starts) == 3
        assert starts[0] == 0.0

    def test_vacuum_cleaner_archetype_prompts_tiktok(self):
        """TikTok vacuum cleaner archetype should produce specialized prompts with attached nozzle."""
        from tools.tiktok_ad.prompts import build_faceless_pov_scenes
        from tools.tiktok_ad.product_parser import ProductInfo

        prod = ProductInfo(
            zip_path=Path("dummy.zip"),
            slug="may-hut-bui",
            name="Máy Hút Bụi Cầm Tay Không Dây Tamashio",
            description_text="Lực hút mạnh 12000Pa",
        )
        scenes = build_faceless_pov_scenes(
            category="KITCHEN_HOME",
            clean_title="máy hút bụi cầm tay tamashio",
            feat1_title="LỰC HÚT MẠNH MẼ",
            feat1_desc="Lực hút 12000Pa",
            feat2_title="ĐẦU HÚT ĐA NĂNG",
            feat2_desc="6 đầu hút thông minh",
            social_proof_title="ĐÁNH GIÁ 5 SAO",
            product=prod,
        )
        assert len(scenes) == 4
        assert "NO attaching parts" in scenes[0].prompt
        sc3 = scenes[2]
        assert "already securely attached" in sc3.prompt


