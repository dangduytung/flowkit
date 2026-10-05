"""Orchestrator for TikTok Video Ad Production Pipeline."""
import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tiktok_ad.config import (
    DEFAULT_CHANNEL_HANDLE,
    DEFAULT_CHANNEL_NAME,
    FLOWKIT_API_URL,
    OUTPUT_ROOT,
    TIKTOK_DOWNLOADS_DIR,
    list_available_zips,
)
from tools.tiktok_ad.product_parser import parse_product_zip
from tools.tiktok_ad.storyboard import load_or_create_storyboard
from tools.tiktok_ad.omnivoice_client import generate_speech
from tools.tiktok_ad.asset_extractor import (
    extract_zip,
    extract_vertical_subclip,
    create_image_slide_clip,
    calculate_smart_subclip_starts,
)
from tools.tiktok_ad.video_assembler import (
    assemble_scene_clip,
    concat_scenes,
    concat_audio_files,
    export_voiceover_script,
    create_silent_version,
)
from tools.tiktok_ad.caption_generator import generate_all_platform_captions
from tools.tiktok_ad.cover_generator import create_cover_image
from tools.tiktok_ad.publish_guide import create_publish_guide


def check_flowkit_health() -> bool:
    """Check if local FlowKit server is running and extension is connected."""
    try:
        req = urllib.request.Request(f"{FLOWKIT_API_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return data.get("status") == "ok" and data.get("extension_connected") is True
    except Exception:
        return False


def build_variant_suffix(
    style: str = "viral_hook",
    no_overlay: bool = False,
    cta_mode: str = "yellow_cart",
    default_cta: str = "yellow_cart",
    tag: Optional[str] = None,
) -> str:
    """Build a descriptive, collision-free variant suffix for multi-style export."""
    parts = [style]
    if no_overlay:
        parts.append("clean")
    if cta_mode and cta_mode != default_cta and cta_mode != "none":
        parts.append(f"cta-{cta_mode}")
    elif cta_mode == "none" and default_cta != "none":
        parts.append("no-cta")
    if tag:
        clean_tag = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in tag
        ).strip("-_")
        if clean_tag:
            parts.append(clean_tag)
    return "_".join(parts)


def run_pipeline(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    mode_9_16: str = "blur_bg",
    cta_mode: str = "yellow_cart",
    channel_name: Optional[str] = None,
    channel_handle: Optional[str] = None,
    style: str = "viral_hook",
    force_storyboard: bool = False,
    custom_idea: Optional[str] = None,
    no_voice: bool = False,
    no_overlay: bool = False,
    tag: Optional[str] = None,
) -> Path:
    """
    Execute the entire TikTok Ad production pipeline dynamically for ANY product zip.
    """
    channel_name = channel_name or DEFAULT_CHANNEL_NAME
    channel_handle = channel_handle or DEFAULT_CHANNEL_HANDLE

    variant = build_variant_suffix(
        style=style,
        no_overlay=no_overlay,
        cta_mode=cta_mode,
        default_cta="yellow_cart",
        tag=tag,
    )

    # 1. Resolve Zip File strictly from TIKTOK_DOWNLOADS_DIR if zip_path is None
    if zip_path is None:
        if not TIKTOK_DOWNLOADS_DIR or not TIKTOK_DOWNLOADS_DIR.exists():
            raise RuntimeError(
                f"Chưa cấu hình TIKTOK_DOWNLOADS_DIR hợp lệ trong .env! (Hiện tại: '{TIKTOK_DOWNLOADS_DIR}')"
            )
        available = list_available_zips()
        if not available:
            raise RuntimeError(
                f"Không tìm thấy file zip nào trong thư mục: {TIKTOK_DOWNLOADS_DIR}"
            )
        zip_path = available[0]
        print(f"[Orchestrator] Quét thư mục TikTok Downloads ({TIKTOK_DOWNLOADS_DIR})")
        print(f"[Orchestrator] Tự động chọn file zip mới nhất: {zip_path.name}")
    else:
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file zip tại: {zip_path}")

    # 2. Phân tích thông tin sản phẩm từ zip
    product = parse_product_zip(zip_path)
    print("\n" + "=" * 60)
    print("🚀 BẮT ĐẦU QUY TRÌNH SẢN XUẤT VIDEO QUẢNG CÁO TIKTOK ADS")
    print(f"📦 Sản phẩm: {product.name}")
    if product.price:
        print(f"💰 Giá bán: {product.price}")
    if product.sold_count:
        print(f"🔥 Đã bán: {product.sold_count} | Đánh giá: {product.rating} sao")
    print(f"📁 Slug thư mục: {product.slug}")
    print("=" * 60 + "\n")

    # 3. Tạo cấu trúc thư mục riêng cho sản phẩm này
    product_dir = OUTPUT_ROOT / product.slug
    assets_dir = product_dir / "assets"
    audio_dir = product_dir / "audio"
    clips_dir = product_dir / "clips"
    scenes_dir = product_dir / "scenes"
    final_dir = product_dir / "final"

    for d in [product_dir, assets_dir, audio_dir, clips_dir, scenes_dir, final_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Lưu bản sao file zip gốc vào thư mục riêng của sản phẩm
    dest_zip = product_dir / zip_path.name
    if zip_path.resolve() != dest_zip.resolve() and not dest_zip.exists():
        shutil.copy2(zip_path, dest_zip)
        print(f"📥 [Lưu trữ] Đã copy file zip vào thư mục sản phẩm: {dest_zip.name}")
    elif dest_zip.exists():
        print(f"📥 [Lưu trữ] File zip đã có sẵn trong thư mục sản phẩm: {dest_zip.name}")

    # 4. Trích xuất tư liệu từ file zip TikTok
    print("📦 [Bước 1/5] Trích xuất hình ảnh và video từ file zip TikTok...")
    assets = extract_zip(zip_path, assets_dir)
    raw_video = assets["video"]
    images = assets["images"]

    # 5. Nạp hoặc tự động sinh Storyboard độc lập theo style (tránh ghi đè khi thử nghiệm nhiều style)
    storyboard_file = product_dir / f"storyboard_{style}.json"

    scenes = load_or_create_storyboard(
        product,
        storyboard_file,
        style=style,
        cta_mode=cta_mode,
        force=force_storyboard,
        custom_idea=custom_idea,
        channel_name=channel_name,
    )

    # 6. Sinh giọng đọc thuyết minh qua OmniVoice API cho từng phân cảnh
    audio_files = {}
    audio_durations = {}

    if not no_voice:
        print(
            f"\n🎙️ [Bước 2/5] Sinh giọng đọc thuyết minh qua OmniVoice API cho {len(scenes)} phân cảnh..."
        )
        for sc in scenes:
            out_wav = audio_dir / f"{variant}_scene_{sc.id:02d}.wav"
            print(f"  • Scene {sc.id}: {sc.name}")
            dur = generate_speech(
                text=sc.narrator_text,
                output_path=out_wav,
                speed=speed,
                profile_id=profile_id,
            )
            audio_files[sc.id] = out_wav
            audio_durations[sc.id] = dur
    else:
        print(
            f"\n🔇 [Bước 2/5] Chế độ Không Voiceover (Silent POV) - Nhịp cắt chuẩn 4.0s/cảnh..."
        )
        for sc in scenes:
            audio_files[sc.id] = None
            audio_durations[sc.id] = 4.0

    # 7. Chuẩn bị các đoạn video clip cho từng cảnh
    print("\n🎬 [Bước 3/5] Chuẩn bị video clip 9:16 cho từng phân cảnh...")
    video_clips = {}
    has_raw_video = raw_video and raw_video.exists()

    raw_video_dur = 0.0
    smart_starts = []
    glitch_intervals = []
    if has_raw_video:
        try:
            cmd_probe = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(raw_video),
            ]
            res_p = subprocess.run(
                cmd_probe, capture_output=True, text=True, check=True
            )
            raw_video_dur = float(res_p.stdout.strip())
            smart_starts, glitch_intervals = calculate_smart_subclip_starts(
                raw_video, len(scenes), raw_video_dur
            )
            print(
                f"  [Video Gốc] Tìm thấy video mẫu từ TikTok ({raw_video_dur:.1f}s), sẵn sàng biên tập sub-clips."
            )
            print(
                f"  [Smart Cuts] Phân bổ mốc thời gian mượt mà (tránh giật hình): {smart_starts}"
            )
            if glitch_intervals:
                print(
                    f"  [Vùng Tránh Giật] Danh sách khoảng chớp/nháy được né: {glitch_intervals}"
                )
        except Exception as e:
            print(f"  [Video Gốc] Không thể đo thời lượng video gốc: {e}")

    curr_raw_time = 0.0
    for idx_sc, sc in enumerate(scenes):
        clip_out = clips_dir / f"{variant}_clip_{sc.id:02d}.mp4"
        dur = audio_durations[sc.id] + 0.4

        # Dựng kết hợp thông minh: Nếu là PRODUCT_PHOTO hoặc không có video gốc thì dùng Pan & Zoom ảnh
        if sc.kind == "PRODUCT_PHOTO" or (not has_raw_video):
            img_idx = sc.image_index % len(images) if images else 0
            img_path = images[img_idx] if images else None
            if img_path and img_path.exists():
                print(
                    f"  • Scene {sc.id} (Ảnh chi tiết): Hiệu ứng Pan & Zoom từ {img_path.name} (dài {dur:.1f}s)..."
                )
                create_image_slide_clip(img_path, dur, clip_out)
            elif has_raw_video:
                extract_vertical_subclip(
                    raw_video,
                    0.0,
                    dur,
                    clip_out,
                    mode=mode_9_16,
                    glitch_intervals=glitch_intervals,
                )
            else:
                raise RuntimeError(
                    f"Scene {sc.id} không có video lẫn hình ảnh để dựng!"
                )
        else:
            # Biên tập cắt lát trực tiếp từ video gốc của Shop
            if sc.real_start_sec and sc.real_start_sec > 0:
                start_sec = sc.real_start_sec
            elif smart_starts and idx_sc < len(smart_starts):
                start_sec = smart_starts[idx_sc]
            else:
                start_sec = curr_raw_time
                if raw_video_dur > 0 and start_sec + dur > raw_video_dur:
                    start_sec = max(
                        0.0, (curr_raw_time % max(1.0, raw_video_dur - dur))
                    )
                curr_raw_time += dur

            print(
                f"  • Scene {sc.id} (Video shop): Cắt từ {start_sec:.1f}s đến {start_sec + dur:.1f}s (dài {dur:.1f}s)..."
            )
            extract_vertical_subclip(
                raw_video,
                start_sec,
                dur,
                clip_out,
                mode=mode_9_16,
                glitch_intervals=glitch_intervals,
            )

        video_clips[sc.id] = clip_out

    # 8. Ráp từng Scene (Video + Audio + Text Overlay)
    print(
        "\n✨ [Bước 4/5] Ráp âm thanh, căn chỉnh độ dài và chèn Text Overlay TikTok..."
    )
    assembled_scenes = []
    for sc in scenes:
        scene_out = scenes_dir / f"{variant}_scene_{sc.id:02d}_assembled.mp4"
        title_to_burn = None if no_overlay else sc.overlay_title
        subtitle_to_burn = None if no_overlay else sc.overlay_subtitle
        timing_info = (
            f"OmniVoice: {audio_durations[sc.id]:.2f}s"
            if not no_voice
            else "Silent: 4.0s"
        )
        print(f"  • Ráp Scene {sc.id}: {sc.overlay_title} ({timing_info})")
        assemble_scene_clip(
            video_path=video_clips[sc.id],
            audio_path=audio_files[sc.id],
            output_path=scene_out,
            title_text=title_to_burn,
            subtitle_text=subtitle_to_burn,
            audio_duration=audio_durations[sc.id],
            target_duration=4.0 if no_voice else None,
        )
        assembled_scenes.append(scene_out)

    # 9. Ghép toàn bộ thành video thành phẩm theo định danh variant độc lập
    print("\n🎞️ [Bước 5/5] Ghép các phân cảnh thành video cuối cùng...")
    if not no_voice:
        final_output = final_dir / f"{product.slug}_local_{variant}.mp4"
        concat_scenes(assembled_scenes, final_output)
        video_map = {"local": final_output}
    else:
        final_output = final_dir / f"{product.slug}_local_{variant}_silent.mp4"
        concat_scenes(assembled_scenes, final_output)
        video_map = {"local_silent": final_output}

    print("📝 Đang tạo bộ caption & metadata đa nền tảng (TikTok, Facebook, Shorts)...")
    caption_files = generate_all_platform_captions(
        product,
        scenes,
        final_dir,
        channel_name=channel_name,
        channel_handle=channel_handle,
        variant_suffix=variant,
    )

    cover_source = video_clips.get(1, final_output)
    cover_path = final_dir / f"{product.slug}_{variant}_cover.jpg"
    print("🖼️ Đang tạo ảnh bìa (Cover / Thumbnail) 9:16 chuẩn TikTok...")
    try:
        create_cover_image(cover_source, product, scenes, cover_path)
    except Exception as e:
        print(f"Cảnh báo: Lỗi tạo ảnh bìa: {e}")

    # 10. Xuất file audio thuyết minh đầy đủ và text kịch bản lời thoại
    print("🎙️ Đang xuất file kịch bản text lời thoại...")
    script_path = final_dir / f"{product.slug}_{variant}_script.txt"
    voiceover_path = final_dir / f"{product.slug}_{variant}_voiceover.mp3"
    export_voiceover_script(
        scenes, audio_durations, script_path, product_name=product.name
    )

    valid_audios = [
        audio_files[s.id]
        for s in scenes
        if audio_files.get(s.id) and Path(audio_files[s.id]).exists()
    ]
    if valid_audios:
        print("🎙️ Đang xuất file audio thuyết minh đầy đủ...")
        concat_audio_files(valid_audios, voiceover_path)
    else:
        voiceover_path = None

    guide_path = final_dir / f"{product.slug}_{variant}_publish_guide.txt"
    create_publish_guide(
        product=product,
        scenes=scenes,
        video_paths=video_map,
        cover_path=cover_path,
        caption_files=caption_files,
        output_guide_path=guide_path,
        channel_handle=channel_handle,
        script_path=script_path,
        voiceover_path=voiceover_path,
    )

    print("\n" + "=" * 60)
    print("🎉 HOÀN THÀNH XUẤT SẮC BỘ OUTPUT TIKTOK ADS:")
    print(f"👉 1. Video thành phẩm:       {final_output.resolve()}")
    if voiceover_path:
        print(f"👉 2. Audio lời thoại đầy đủ: {voiceover_path.resolve()}")
    print(f"👉 3. Text kịch bản & time:   {script_path.resolve()}")
    print(f"👉 4. Ảnh bìa thu nhỏ:        {cover_path.resolve()}")
    print(f"👉 5. Cẩm nang xuất bản:      {guide_path.resolve()}")
    print(f"📝 Kịch bản có thể tùy chỉnh tại: {storyboard_file.resolve()}")
    print("=" * 60 + "\n")
    return final_output


def main():
    parser = argparse.ArgumentParser(description="TikTok Product Video Ad Generator")
    parser.add_argument(
        "--zip",
        type=str,
        default=None,
        help="Đường dẫn đến file zip sản phẩm TikTok Downloads",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Liệt kê danh sách các file zip TikTok đang có",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=None,
        help="Tốc độ đọc giọng nói OmniVoice (mặc định từ .env)",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="Profile ID giọng nói trên VoiceStudio",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "both", "flow", "local", "zip"],
        help="Chế độ tạo video: 'auto' (MẶC ĐỊNH: nếu có FlowKit tạo cả _local và _flow), 'flow', hoặc 'local'",
    )
    parser.add_argument(
        "--crop",
        type=str,
        default="blur_bg",
        choices=["blur_bg", "center_crop"],
        help="Chế độ crop 9:16 cho video/ảnh (mặc định: blur_bg)",
    )
    parser.add_argument(
        "--cta",
        type=str,
        default="yellow_cart",
        choices=["yellow_cart", "profile_bio", "follow", "none"],
        help="Chế độ kết thúc: 'yellow_cart' (MẶC ĐỊNH: giỏ hàng màu vàng góc trái màn hình TikTok Shop), 'profile_bio', 'follow', 'none'",
    )
    parser.add_argument(
        "--style",
        type=str,
        default="viral_hook",
        help="Phong cách video: 'viral_hook' (MẶC ĐỊNH), 'faceless_pov', 'problem_solution', 'lifestyle_edc', 'flow_cinematic', 'hybrid', hoặc 'all' (xuất tất cả 4 style chính), hoặc danh sách phân tách bằng dấu phẩy (vd: 'viral_hook,faceless_pov')",
    )
    parser.add_argument(
        "--flow",
        action="store_true",
        help="Viết tắt cho --mode flow (chỉ tạo video Google Flow AI)",
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="Bắt buộc tạo lại video clip AI từ Google Flow",
    )
    parser.add_argument(
        "--idea",
        "--story",
        type=str,
        default=None,
        help="Ý tưởng kịch bản tùy chỉnh",
    )
    parser.add_argument(
        "--force-storyboard",
        action="store_true",
        help="Bắt buộc tạo lại kịch bản storyboard.json từ đầu",
    )
    parser.add_argument(
        "--channel-name",
        type=str,
        default=DEFAULT_CHANNEL_NAME,
        help=f"Tên kênh xuất bản (mặc định từ .env TIKTOK_AD_CHANNEL_NAME: '{DEFAULT_CHANNEL_NAME}')",
    )
    parser.add_argument(
        "--channel-handle",
        type=str,
        default=DEFAULT_CHANNEL_HANDLE,
        help=f"Handle/ID kênh (mặc định từ .env TIKTOK_AD_CHANNEL_HANDLE: '{DEFAULT_CHANNEL_HANDLE}')",
    )
    parser.add_argument(
        "--no-voice",
        "--silent",
        dest="no_voice",
        action="store_true",
        help="Không tạo voiceover thuyết minh (video thuần hình ảnh)",
    )
    parser.add_argument(
        "--no-overlay",
        "--clean",
        dest="no_overlay",
        action="store_true",
        help="Không chèn chữ Text Overlay",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default=None,
        help="Gắn nhãn/tag tùy chỉnh cho video xuất bản (ví dụ: --tag v2, --tag test1) để phân biệt các lần chạy",
    )

    args = parser.parse_args()

    if args.list:
        print("\n📂 Các file zip TikTok tìm thấy trong máy:")
        zips = list_available_zips()
        if not zips:
            print(f"  (Không có file zip nào trong {TIKTOK_DOWNLOADS_DIR})")
        for i, z in enumerate(zips, 1):
            print(f"  [{i}] {z.name} ({z.stat().st_size / 1024 / 1024:.1f} MB)")
        return

    target_zip = Path(args.zip) if args.zip else None
    if target_zip is None:
        if not TIKTOK_DOWNLOADS_DIR or not TIKTOK_DOWNLOADS_DIR.exists():
            raise RuntimeError(
                f"Chưa cấu hình TIKTOK_DOWNLOADS_DIR hợp lệ trong .env! (Hiện tại: '{TIKTOK_DOWNLOADS_DIR}')"
            )
        available = list_available_zips()
        if not available:
            raise RuntimeError(
                f"Không tìm thấy file zip nào trong thư mục: {TIKTOK_DOWNLOADS_DIR}"
            )
        target_zip = available[0]
        print(f"[Orchestrator] Quét thư mục TikTok ({TIKTOK_DOWNLOADS_DIR})")
        print(f"[Orchestrator] Tự động chọn file zip mới nhất: {target_zip.name}")

    selected_mode = args.mode
    if args.flow:
        selected_mode = "flow"

    run_local = False
    run_flow = False

    if selected_mode == "auto":
        run_local = True
        if check_flowkit_health():
            print("💡 Phát hiện FlowKit server đang kết nối: Tự động kích hoạt CẢ HAI CHẾ ĐỘ (_local.mp4 & _flow.mp4)!")
            run_flow = True
        else:
            print("💡 Đang sản xuất chế độ Local (_local.mp4). Để sinh thêm bản Flow AI (_flow.mp4), hãy kết nối FlowKit.")
    elif selected_mode == "both":
        run_local = True
        run_flow = True
    elif selected_mode in ("local", "zip"):
        run_local = True
    elif selected_mode == "flow":
        run_flow = True

    raw_styles = [s.strip() for s in (args.style or "viral_hook").split(",") if s.strip()]
    styles_to_run = []
    ALL_TIKTOK_STYLES = ["viral_hook", "faceless_pov", "problem_solution", "lifestyle_edc"]
    for s in raw_styles:
        if s == "all":
            for st in ALL_TIKTOK_STYLES:
                if st not in styles_to_run:
                    styles_to_run.append(st)
        elif s in ("faceless", "pov", "hands_on_pov"):
            if "faceless_pov" not in styles_to_run:
                styles_to_run.append("faceless_pov")
        else:
            if s not in styles_to_run:
                styles_to_run.append(s)
    if not styles_to_run:
        styles_to_run = ["viral_hook"]

    if len(styles_to_run) > 1:
        print(f"\n🎬 KÍCH HOẠT XUẤT HÀNG LOẠT {len(styles_to_run)} PHONG CÁCH: {', '.join(styles_to_run)}")

    for idx_style, cur_style in enumerate(styles_to_run, 1):
        if len(styles_to_run) > 1:
            print(f"\n{'=' * 65}")
            print(f"▶ [{idx_style}/{len(styles_to_run)}] TIẾN HÀNH XUẤT PHONG CÁCH: {cur_style.upper()}")
            print(f"{'=' * 65}")

        if run_local:
            print("\n" + "▶" * 25 + f" SẢN XUẤT VIDEO LOCAL ({cur_style}) " + "◀" * 25)
            run_pipeline(
                zip_path=target_zip,
                speed=args.speed,
                profile_id=args.profile,
                mode_9_16=args.crop,
                cta_mode=args.cta,
                channel_name=args.channel_name,
                channel_handle=args.channel_handle,
                style=cur_style,
                force_storyboard=args.force_storyboard or bool(args.idea),
                custom_idea=args.idea,
                no_voice=args.no_voice,
                no_overlay=args.no_overlay,
                tag=args.tag,
            )

        if run_flow:
            print("\n" + "▶" * 25 + f" SẢN XUẤT VIDEO GOOGLE FLOW AI ({cur_style}) " + "◀" * 25)
            from tools.tiktok_ad.flow_ad_generator import generate_flow_ad
            generate_flow_ad(
                zip_path=target_zip,
                speed=args.speed,
                profile_id=args.profile,
                cta_mode=args.cta,
                style=cur_style,
                regen=args.regen,
                force_storyboard=args.force_storyboard or bool(args.idea),
                custom_idea=args.idea,
                channel_name=args.channel_name,
                channel_handle=args.channel_handle,
                no_voice=args.no_voice,
                no_overlay=args.no_overlay,
                tag=args.tag,
            )


if __name__ == "__main__":
    main()
