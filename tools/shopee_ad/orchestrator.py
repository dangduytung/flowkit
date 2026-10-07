import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.shopee_ad.config import (
    DEFAULT_CHANNEL_HANDLE,
    DEFAULT_CHANNEL_NAME,
    FLOWKIT_API_URL,
    OUTPUT_ROOT,
    SHOPEE_DOWNLOADS_DIR,
    list_available_zips,
    resolve_bgm_path,
)
from tools.shopee_ad.product_parser import parse_product_zip
from tools.shopee_ad.storyboard import load_or_create_storyboard
from tools.shopee_ad.omnivoice_client import generate_speech
from tools.shopee_ad.asset_extractor import (
    extract_zip,
    extract_vertical_subclip,
    create_image_slide_clip,
    create_hybrid_subclip,
    calculate_smart_subclip_starts,
)
from tools.shopee_ad.video_assembler import (
    assemble_scene_clip,
    concat_scenes,
    concat_audio_files,
    export_voiceover_script,
    create_silent_version,
)
from tools.shopee_ad.caption_generator import generate_all_platform_captions
from tools.shopee_ad.cover_generator import create_cover_image
from tools.shopee_ad.publish_guide import create_publish_guide
from tools.common.naming import build_variant_suffix as _build_variant_suffix
from tools.common.watermarks import resolve_delogo_for_product
from tools.shopee_ad.flow_ad_generator import generate_flow_ad


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
    style: str = "problem_solution",
    no_overlay: bool = False,
    cta_mode: str = "none",
    default_cta: str = "shopee",
    tag: Optional[str] = None,
) -> str:
    """Build a descriptive, collision-free variant suffix for multi-style export."""
    return _build_variant_suffix(
        style=style,
        no_overlay=no_overlay,
        cta_mode=cta_mode,
        default_cta=default_cta,
        tag=tag,
    )


def run_pipeline(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    mode_9_16: str = "blur_bg",
    cta_mode: str = "none",
    channel_name: Optional[str] = None,
    channel_handle: Optional[str] = None,
    style: str = "problem_solution",
    force_storyboard: bool = False,
    custom_idea: Optional[str] = None,
    no_voice: bool = False,
    no_overlay: bool = False,
    tag: Optional[str] = None,
    delogo: Optional[str] = "auto",
    bgm: Optional[Path | str] = None,
    target_scenes: Optional[List[int]] = None,
) -> Path:
    """
    Execute the entire Shopee Ad production pipeline dynamically for ANY product zip.
    """
    channel_name = channel_name or DEFAULT_CHANNEL_NAME
    channel_handle = channel_handle or DEFAULT_CHANNEL_HANDLE

    variant = build_variant_suffix(
        style=style,
        no_overlay=no_overlay,
        cta_mode=cta_mode,
        default_cta="shopee",
        tag=tag,
    )
    # 1. Resolve Zip File strictly from SHOPEE_DOWNLOADS_DIR if zip_path is None
    if zip_path is None:
        if not SHOPEE_DOWNLOADS_DIR or not SHOPEE_DOWNLOADS_DIR.exists():
            raise RuntimeError(
                f"Chưa cấu hình SHOPEE_DOWNLOADS_DIR hợp lệ trong .env! (Hiện tại: '{SHOPEE_DOWNLOADS_DIR}')"
            )
        available = list_available_zips()
        if not available:
            raise RuntimeError(f"Không tìm thấy file zip nào trong thư mục: {SHOPEE_DOWNLOADS_DIR}")
        zip_path = available[0]
        print(f"[Orchestrator] Quét thư mục Shopee ({SHOPEE_DOWNLOADS_DIR})")
        print(f"[Orchestrator] Tự động chọn file zip mới nhất: {zip_path.name}")
    else:
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file zip tại: {zip_path}")

    # 2. Phân tích thông tin sản phẩm từ zip
    product = parse_product_zip(zip_path)
    print("\n" + "=" * 60)
    print("🚀 BẮT ĐẦU QUY TRÌNH SẢN XUẤT VIDEO QUẢNG CÁO SHOPEE")
    print(f"📦 Sản phẩm: {product.name}")
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

    # 3b. Lưu bản sao file zip gốc vào thư mục riêng của sản phẩm
    dest_zip = product_dir / zip_path.name
    if zip_path.resolve() != dest_zip.resolve() and not dest_zip.exists():
        shutil.copy2(zip_path, dest_zip)
        print(f"📥 [Lưu trữ] Đã copy file zip vào thư mục sản phẩm: {dest_zip.name}")
    elif dest_zip.exists():
        print(f"📥 [Lưu trữ] File zip đã có sẵn trong thư mục sản phẩm: {dest_zip.name}")

    # 4. Trích xuất tư liệu từ file zip Shopee
    print("📦 [Bước 1/5] Trích xuất hình ảnh và video từ file zip...")
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

    # 6. Sinh giọng đọc thuyết minh qua OmniVoice API cho từng phân cảnh (hoặc nhịp POV silent)
    audio_files = {}
    audio_durations = {}

    if not no_voice:
        print(f"\n🎙️ [Bước 2/5] Sinh giọng đọc thuyết minh qua OmniVoice API cho {len(scenes)} phân cảnh...")
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
        print(f"\n🔇 [Bước 2/5] Chế độ Không Voiceover (Silent POV) - Nhịp cắt chuẩn 5.0s/cảnh...")
        for sc in scenes:
            audio_files[sc.id] = None
            audio_durations[sc.id] = 5.0

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
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(raw_video)
            ]
            res_p = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
            raw_video_dur = float(res_p.stdout.strip())
            scene_req_durs = [audio_durations[sc.id] + 0.4 for sc in scenes]
            smart_starts, glitch_intervals = calculate_smart_subclip_starts(
                raw_video, len(scenes), raw_video_dur, scene_durations=scene_req_durs
            )
            print(f"  [Video Gốc] Tìm thấy video mẫu từ Shopee ({raw_video_dur:.1f}s), sẵn sàng biên tập sub-clips.")
            print(f"  [Smart Cuts] Phân bổ mốc thời gian mượt mà (tránh giật hình): {smart_starts}")
            if glitch_intervals:
                print(f"  [Vùng Tránh Giật] Danh sách khoảng chớp/nháy được né: {glitch_intervals}")
        except Exception as e:
            print(f"  [Video Gốc] Không thể đo thời lượng video gốc: {e}")

    active_delogo = None
    if delogo == "auto":
        resolved, rule_name = resolve_delogo_for_product(product.url, video_path=raw_video if has_raw_video else None)
        if resolved:
            print(f"  [Delogo] Áp dụng quy tắc xóa logo ('{rule_name}'): {resolved}")
            active_delogo = resolved
        else:
            print("  [Delogo] Không phát hiện quy tắc xóa logo nào cho sản phẩm này trong config/watermark_rules.json")
    elif delogo and delogo.lower() != "none":
        active_delogo = delogo

    curr_raw_time = 0.0
    for idx_sc, sc in enumerate(scenes):
        clip_out = clips_dir / f"{variant}_clip_{sc.id:02d}.mp4"
        dur = audio_durations[sc.id] + 0.4  # Đảm bảo video dài hơn audio 0.4s để chuyển cảnh êm

        if sc.kind == "PRODUCT_PHOTO" or (not has_raw_video):
            # Dùng hiệu ứng Ken Burns Pan & Zoom từ ảnh sản phẩm
            img_idx = sc.image_index % len(images) if images else 0
            img_path = images[img_idx] if images else None
            if img_path and img_path.exists():
                print(f"  • Scene {sc.id}: Tạo hiệu ứng chuyển động ảnh Pan & Zoom từ {img_path.name} (dài {dur:.1f}s)...")
                create_image_slide_clip(img_path, dur, clip_out)
            elif has_raw_video:
                extract_vertical_subclip(raw_video, 0.0, dur, clip_out, mode=mode_9_16, glitch_intervals=glitch_intervals, delogo=active_delogo)
            else:
                raise RuntimeError(f"Scene {sc.id} không có video lẫn hình ảnh để dựng!")
        else:
            # Biên tập cắt lát trực tiếp từ video mẫu của Shop (đảm bảo 100% không trùng lặp cảnh)
            if smart_starts and idx_sc < len(smart_starts):
                start_sec = smart_starts[idx_sc]
                next_sec = smart_starts[idx_sc + 1] if idx_sc + 1 < len(smart_starts) else raw_video_dur
                avail_slice = max(0.0, next_sec - start_sec)
            elif sc.real_start_sec is not None and sc.real_start_sec >= 0:
                start_sec = sc.real_start_sec
                avail_slice = dur
            else:
                start_sec = curr_raw_time
                avail_slice = dur
                curr_raw_time += dur

            # Nếu lát cắt video ngắn hơn lời đọc (từ 0.5s trở lên) và có ảnh sản phẩm:
            # Tự động ghép chuyển động ảnh Ken Burns vào đầu cảnh để không bị lặp lại video hay giật khung hình
            if images and avail_slice > 0 and avail_slice < dur - 0.5:
                img_idx = sc.image_index % len(images) if sc.image_index is not None else (idx_sc % len(images))
                img_path = images[img_idx]
                slide_dur = dur - avail_slice
                print(f"  • Scene {sc.id}: Ghép linh hoạt (Ảnh {img_path.name} {slide_dur:.1f}s + Video mẫu {avail_slice:.1f}s từ {start_sec:.1f}s)...")
                create_hybrid_subclip(
                    image_path=img_path,
                    video_path=raw_video,
                    img_duration=slide_dur,
                    vid_start_sec=start_sec,
                    vid_duration=avail_slice,
                    output_path=clip_out,
                    mode=mode_9_16,
                    delogo=active_delogo,
                )
            else:
                cut_dur = min(dur, avail_slice) if avail_slice > 0 else dur
                print(f"  • Scene {sc.id}: Cắt video mẫu từ {start_sec:.1f}s (dài {cut_dur:.1f}s, mode {mode_9_16})...")
                extract_vertical_subclip(
                    raw_video,
                    start_sec,
                    cut_dur,
                    clip_out,
                    mode=mode_9_16,
                    glitch_intervals=glitch_intervals,
                    delogo=active_delogo,
                )

        video_clips[sc.id] = clip_out

    # 8. Ráp từng Scene (Video + Audio + Text Overlay)
    print("\n✨ [Bước 4/5] Ráp âm thanh, căn chỉnh độ dài và chèn Text Overlay...")
    assembled_scenes = []
    for sc in scenes:
        scene_out = scenes_dir / f"{variant}_scene_{sc.id:02d}_assembled.mp4"
        title_to_burn = None if no_overlay else sc.overlay_title
        subtitle_to_burn = None if no_overlay else sc.overlay_subtitle
        timing_info = f"OmniVoice: {audio_durations[sc.id]:.2f}s" if not no_voice else "Silent: 5.0s"
        print(f"  • Ráp Scene {sc.id}: {sc.overlay_title} ({timing_info})")
        assemble_scene_clip(
            video_path=video_clips[sc.id],
            audio_path=audio_files[sc.id],
            output_path=scene_out,
            title_text=title_to_burn,
            subtitle_text=subtitle_to_burn,
            audio_duration=audio_durations[sc.id],
            target_duration=5.0 if no_voice else None,
            remove_watermark=False,
        )
        assembled_scenes.append(scene_out)

    # 9. Ghép toàn bộ thành video thành phẩm theo định danh variant độc lập
    print("\n🎞️ [Bước 5/5] Ghép các phân cảnh thành video cuối cùng...")
    effective_bgm = resolve_bgm_path(custom_bgm=bgm, style=style, product_assets_dir=assets_dir)
    if effective_bgm:
        print(f"🎵 [Nhạc Nền BGM] Tự động kích hoạt: {effective_bgm.name}...")

    if not no_voice:
        final_output = final_dir / f"{product.slug}_local_{variant}.mp4"
        concat_scenes(assembled_scenes, final_output, bgm_path=effective_bgm)
        video_map = {"local": final_output}
    else:
        final_output = final_dir / f"{product.slug}_local_{variant}_silent.mp4"
        concat_scenes(assembled_scenes, final_output, bgm_path=effective_bgm)
        video_map = {"local_silent": final_output}

    print("📝 Đang tạo bộ caption & metadata đa nền tảng (Facebook, TikTok, YouTube Shorts)...")
    caption_files = generate_all_platform_captions(
        product, scenes, final_dir, channel_name=channel_name, channel_handle=channel_handle, variant_suffix=variant
    )

    cover_source = video_clips.get(1, final_output)
    cover_path = final_dir / f"{product.slug}_{variant}_cover.jpg"
    print("🖼️ Đang tạo ảnh bìa (Cover / Thumbnail) 9:16 chuẩn đa nền tảng...")
    try:
        create_cover_image(cover_source, product, scenes, cover_path)
    except Exception as e:
        print(f"Cảnh báo: Lỗi tạo ảnh bìa: {e}")

    # 10. Xuất file audio thuyết minh đầy đủ và text kịch bản lời thoại
    print("🎙️ Đang xuất file kịch bản text lời thoại...")
    script_path = final_dir / f"{product.slug}_{variant}_script.txt"
    voiceover_path = final_dir / f"{product.slug}_{variant}_voiceover.mp3"
    export_voiceover_script(scenes, audio_durations, script_path, product_name=product.name)

    valid_audios = [audio_files[s.id] for s in scenes if audio_files.get(s.id) and Path(audio_files[s.id]).exists()]
    if valid_audios:
        print("🎙️ Đang xuất file audio thuyết minh đầy đủ...")
        concat_audio_files(valid_audios, voiceover_path)
    else:
        voiceover_path = None

    guide_path = final_dir / f"{product.slug}_{variant}_publish_guide.txt"
    flow_output = final_dir / f"{product.slug}_flow_{variant}.mp4"
    if flow_output.exists():
        video_map["flow"] = flow_output
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
    print("🎉 HOÀN THÀNH XUẤT SẮC BỘ OUTPUT SẢN PHẨM:")
    print(f"👉 1. Video chuẩn Local:      {final_output.resolve()}")
    if "flow" in video_map and video_map["flow"]:
        print(f"👉 2. Video chuẩn Flow:       {video_map['flow'].resolve()}")
    if voiceover_path:
        print(f"👉 3. Audio lời thoại đầy đủ: {voiceover_path.resolve()}")
    print(f"👉 4. Text kịch bản & time:   {script_path.resolve()}")
    print(f"👉 5. Ảnh bìa thu nhỏ:        {cover_path.resolve()}")
    print(f"👉 6. Hướng dẫn chi tiết:     {guide_path.resolve()}")
    print(f"📝 Kịch bản có thể tùy chỉnh tại: {storyboard_file.resolve()}")
    print("=" * 60 + "\n")
    return final_output


def main():
    parser = argparse.ArgumentParser(description="Shopee Product Video Ad Generator")
    parser.add_argument("--zip", type=str, default=None, help="Đường dẫn đến file zip sản phẩm Shopee")
    parser.add_argument("--list", action="store_true", help="Liệt kê danh sách các file zip Shopee đang có")
    parser.add_argument("--speed", type=float, default=None, help="Tốc độ đọc giọng nói OmniVoice (mặc định 0.86)")
    parser.add_argument("--profile", type=str, default=None, help="Profile ID giọng nói trên VoiceStudio")
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "both", "flow", "local", "zip"],
        help="Chế độ tạo video: 'auto' (MẶC ĐỊNH: nếu ZIP có video sẽ sinh CẢ HAI '_local.mp4' & '_flow.mp4'; nếu chỉ có ảnh sẽ sinh '_flow.mp4'), 'both', 'flow', hoặc 'local'",
    )
    parser.add_argument(
        "--crop",
        type=str,
        default="blur_bg",
        choices=["blur_bg", "center_crop"],
        help="Chế độ crop 9:16 cho ảnh/video local (mặc định: blur_bg)",
    )
    parser.add_argument(
        "--method",
        type=str,
        default=None,
        choices=["flow", "local", "zip", "ken_burns"],
        help="Alias cho --mode (tương thích ngược)",
    )
    parser.add_argument("--flow", action="store_true", help="Viết tắt cho --mode flow")
    parser.add_argument(
        "--cta",
        type=str,
        default="none",
        choices=["none", "follow", "shopee", "tiktok"],
        help="Chế độ kết thúc: 'none' (4 cảnh tự nhiên), 'follow' (kêu gọi follow kênh), 'shopee' (link giỏ hàng/bình luận Shopee), 'tiktok' (giỏ hàng màu vàng góc trái)",
    )
    parser.add_argument(
        "--style",
        type=str,
        default="flow_cinematic",
        help="Phong cách video: 'flow_cinematic' (MẶC ĐỊNH), 'faceless_pov', 'problem_solution', 'lifestyle_edc', 'hybrid', hoặc 'all' (xuất tất cả 4 style chính), hoặc danh sách phân tách bằng dấu phẩy (vd: 'faceless_pov,flow_cinematic')",
    )
    parser.add_argument(
        "--idea",
        "--story",
        type=str,
        default=None,
        help="Ý tưởng / tình huống kịch bản tùy chỉnh (ví dụ: 'laptop hết bộ nhớ trước giờ nộp báo cáo')",
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="Bắt buộc tạo lại video clip AI từ Google Flow (bỏ qua clip cũ)",
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
        help=f"Tên kênh xuất bản (mặc định lấy từ .env SHOPEE_AD_CHANNEL_NAME: '{DEFAULT_CHANNEL_NAME}')",
    )
    parser.add_argument(
        "--channel-handle",
        type=str,
        default=DEFAULT_CHANNEL_HANDLE,
        help=f"Handle/ID kênh (mặc định lấy từ .env SHOPEE_AD_CHANNEL_HANDLE: '{DEFAULT_CHANNEL_HANDLE}')",
    )
    parser.add_argument(
        "--no-voice",
        "--silent",
        dest="no_voice",
        action="store_true",
        help="Không tạo voiceover thuyết minh (video thuần hình ảnh, thích hợp tự chèn nhạc trend TikTok)",
    )
    parser.add_argument(
        "--no-overlay",
        "--clean",
        dest="no_overlay",
        action="store_true",
        help="Không chèn chữ Text Overlay (video sạch để tự chèn text font TikTok)",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default=None,
        help="Gắn nhãn/tag tùy chỉnh cho video xuất bản (ví dụ: --tag v2, --tag test1) để phân biệt các lần chạy",
    )
    parser.add_argument(
        "--delogo",
        type=str,
        default="auto",
        help="Chế độ xóa logo shop: 'auto' (tự động phát hiện logo như Pi home và xóa sạch), 'none' (tắt), hoặc tọa độ thủ công (ví dụ 'x=30:y=545:w=140:h=60')",
    )
    parser.add_argument(
        "--scene",
        nargs="+",
        type=int,
        default=None,
        help="Chỉ định ID phân cảnh cần tạo lại (ví dụ: --scene 3)",
    )
    parser.add_argument(
        "--bgm",
        nargs="?",
        const="auto",
        default=None,
        help="Bật nhạc nền BGM (MẶC ĐỊNH LÀ TẮT): gõ --bgm để tự chọn ngẫu nhiên từ assets/bgm/; hoặc --bgm <path> để chỉ định file",
    )

    args = parser.parse_args()

    if args.list:
        print("\n📂 Các file zip Shopee tìm thấy trong máy:")
        zips = list_available_zips()
        if not zips:
            print(f"  (Không có file zip nào trong {SHOPEE_DOWNLOADS_DIR})")
        for i, z in enumerate(zips, 1):
            print(f"  [{i}] {z.name} ({z.stat().st_size / 1024 / 1024:.1f} MB)")
        return

    target_zip = Path(args.zip) if args.zip else None
    if target_zip is None:
        if not SHOPEE_DOWNLOADS_DIR or not SHOPEE_DOWNLOADS_DIR.exists():
            raise RuntimeError(
                f"Chưa cấu hình SHOPEE_DOWNLOADS_DIR hợp lệ trong .env! (Hiện tại: '{SHOPEE_DOWNLOADS_DIR}')"
            )
        available = list_available_zips()
        if not available:
            raise RuntimeError(f"Không tìm thấy file zip nào trong thư mục: {SHOPEE_DOWNLOADS_DIR}")
        target_zip = available[0]
        print(f"[Orchestrator] Quét thư mục Shopee ({SHOPEE_DOWNLOADS_DIR})")
        print(f"[Orchestrator] Tự động chọn file zip mới nhất: {target_zip.name}")

    product = parse_product_zip(target_zip)
    has_video = bool(product.video_name)

    # Resolve mode
    selected_mode = args.mode
    if args.method:
        selected_mode = "local" if args.method in ("local", "zip", "ken_burns") else args.method
    if args.flow:
        selected_mode = "flow"

    run_local = False
    run_flow = False

    if selected_mode == "auto":
        if has_video:
            print("💡 File ZIP có chứa video gốc: Tự động kích hoạt CẢ HAI CHẾ ĐỘ (_local.mp4 & _flow.mp4)!")
            run_local = True
            run_flow = True
        else:
            print("💡 File ZIP chỉ có hình ảnh: Kích hoạt chế độ Google Flow AI (_flow.mp4)!")
            run_flow = True
    elif selected_mode == "both":
        run_local = True
        run_flow = True
    elif selected_mode in ("local", "zip"):
        run_local = True
    elif selected_mode == "flow":
        run_flow = True

    raw_styles = [s.strip() for s in (args.style or "flow_cinematic").split(",") if s.strip()]
    styles_to_run = []
    ALL_SHOPEE_STYLES = ["flow_cinematic", "faceless_pov", "problem_solution", "lifestyle_edc"]
    for s in raw_styles:
        if s == "all":
            for st in ALL_SHOPEE_STYLES:
                if st not in styles_to_run:
                    styles_to_run.append(st)
        elif s in ("faceless", "pov"):
            if "faceless_pov" not in styles_to_run:
                styles_to_run.append("faceless_pov")
        else:
            if s not in styles_to_run:
                styles_to_run.append(s)
    if not styles_to_run:
        styles_to_run = ["flow_cinematic"]

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
                delogo=args.delogo,
                bgm=args.bgm,
                target_scenes=args.scene,
            )

        if run_flow:
            print("\n" + "▶" * 25 + f" SẢN XUẤT VIDEO GOOGLE FLOW AI ({cur_style}) " + "◀" * 25)
            generate_flow_ad(
                zip_path=target_zip,
                speed=args.speed,
                profile_id=args.profile,
                cta_mode=args.cta,
                style=cur_style,
                regen=args.regen,
                force_storyboard=args.force_storyboard or bool(args.idea),
                target_scenes=args.scene,
                custom_idea=args.idea,
                channel_name=args.channel_name,
                channel_handle=args.channel_handle,
                no_voice=args.no_voice,
                no_overlay=args.no_overlay,
                tag=args.tag,
                bgm_path=args.bgm,
            )


if __name__ == "__main__":
    main()
