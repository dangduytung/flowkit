import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Optional

from tools.shopee_ad.config import (
    FLOWKIT_API_URL,
    OUTPUT_ROOT,
    SHOPEE_DOWNLOADS_DIR,
    list_available_zips,
)
from tools.shopee_ad.product_parser import parse_product_zip
from tools.shopee_ad.storyboard import load_or_create_storyboard
from tools.shopee_ad.omnivoice_client import generate_speech
from tools.shopee_ad.asset_extractor import (
    extract_zip,
    extract_vertical_subclip,
    create_image_slide_clip,
)
from tools.shopee_ad.video_assembler import assemble_scene_clip, concat_scenes


def check_flowkit_health() -> bool:
    """Check if local FlowKit server is running and extension is connected."""
    try:
        req = urllib.request.Request(f"{FLOWKIT_API_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return data.get("status") == "ok" and data.get("extension_connected") is True
    except Exception:
        return False


def run_pipeline(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    mode_9_16: str = "blur_bg",
) -> Path:
    """
    Execute the entire Shopee Ad production pipeline dynamically for ANY product zip.
    """
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

    # 5. Nạp hoặc tự động sinh Storyboard (kịch bản 5 cảnh)
    storyboard_file = product_dir / "storyboard.json"
    scenes = load_or_create_storyboard(product, storyboard_file)

    # 6. Sinh giọng đọc thuyết minh qua OmniVoice API cho từng phân cảnh
    print("\n🎙️ [Bước 2/5] Sinh giọng đọc thuyết minh qua OmniVoice API...")
    audio_files = {}
    audio_durations = {}

    for sc in scenes:
        out_wav = audio_dir / f"scene_{sc.id:02d}.wav"
        print(f"  • Scene {sc.id}: {sc.name}")
        dur = generate_speech(
            text=sc.narrator_text,
            output_path=out_wav,
            speed=speed,
            profile_id=profile_id,
        )
        audio_files[sc.id] = out_wav
        audio_durations[sc.id] = dur

    # 7. Chuẩn bị các đoạn video clip cho từng cảnh
    print("\n🎬 [Bước 3/5] Chuẩn bị video clip 9:16 cho từng phân cảnh...")
    video_clips = {}
    has_raw_video = raw_video and raw_video.exists()

    for sc in scenes:
        clip_out = clips_dir / f"clip_raw_{sc.id:02d}.mp4"
        dur = audio_durations[sc.id] + 0.4  # Đảm bảo video dài hơn audio 0.4s để chuyển cảnh êm

        if sc.kind == "REAL_FOOTAGE" and has_raw_video:
            print(f"  • Scene {sc.id}: Cắt lát từ video gốc (bắt đầu {sc.real_start_sec:.1f}s, dài {dur:.1f}s)...")
            extract_vertical_subclip(raw_video, sc.real_start_sec, dur, clip_out, mode=mode_9_16)
        else:
            # Dùng hiệu ứng Ken Burns Pan & Zoom từ ảnh sản phẩm
            img_idx = sc.image_index % len(images) if images else 0
            img_path = images[img_idx] if images else None
            if img_path and img_path.exists():
                print(f"  • Scene {sc.id}: Tạo hiệu ứng chuyển động ảnh Pan & Zoom từ {img_path.name} (dài {dur:.1f}s)...")
                create_image_slide_clip(img_path, dur, clip_out)
            elif has_raw_video:
                print(f"  • Scene {sc.id}: Fallback cắt từ video gốc...")
                extract_vertical_subclip(raw_video, sc.real_start_sec, dur, clip_out, mode=mode_9_16)
            else:
                raise RuntimeError(f"Scene {sc.id} không có video lẫn hình ảnh để dựng!")

        video_clips[sc.id] = clip_out

    # 8. Ráp từng Scene (Video + Audio + Text Overlay)
    print("\n✨ [Bước 4/5] Ráp âm thanh, căn chỉnh độ dài và chèn Text Overlay...")
    assembled_scenes = []
    for sc in scenes:
        scene_out = scenes_dir / f"scene_{sc.id:02d}_assembled.mp4"
        print(f"  • Ráp Scene {sc.id}: {sc.overlay_title} ({audio_durations[sc.id]:.2f}s)")
        assemble_scene_clip(
            video_path=video_clips[sc.id],
            audio_path=audio_files[sc.id],
            output_path=scene_out,
            title_text=sc.overlay_title,
            subtitle_text=sc.overlay_subtitle,
            audio_duration=audio_durations[sc.id],
        )
        assembled_scenes.append(scene_out)

    # 9. Ghép toàn bộ thành video thành phẩm
    print("\n🎞️ [Bước 5/5] Ghép các phân cảnh thành video cuối cùng...")
    final_output = final_dir / f"{product.slug}_final.mp4"
    concat_scenes(assembled_scenes, final_output)

    print("\n" + "=" * 60)
    print("🎉 HOÀN THÀNH XUẤT SẮC! Video đã được lưu tại:")
    print(f"👉 {final_output.resolve()}")
    print(f"📝 Kịch bản có thể tùy chỉnh tại: {storyboard_file.resolve()}")
    print("=" * 60 + "\n")
    return final_output


def main():
    parser = argparse.ArgumentParser(description="Shopee Product Video Ad Generator")
    parser.add_argument("--zip", type=str, default=None, help="Đường dẫn đến file zip sản phẩm Shopee")
    parser.add_argument("--list", action="store_true", help="Liệt kê danh sách các file zip Shopee đang có")
    parser.add_argument("--speed", type=float, default=None, help="Tốc độ đọc giọng nói OmniVoice (mặc định 0.86)")
    parser.add_argument("--profile", type=str, default=None, help="Profile ID giọng nói trên VoiceStudio")
    parser.add_argument("--mode", type=str, default="blur_bg", choices=["blur_bg", "center_crop"], help="Chế độ crop 9:16")
    parser.add_argument("--method", type=str, default="ken_burns", choices=["ken_burns", "flow"], help="Phương pháp sinh video: ken_burns (ảnh gốc + chuyển động) hoặc flow (Google Flow AI Video)")
    parser.add_argument("--flow", action="store_true", help="Viết tắt cho --method flow (dùng Google Flow AI)")

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
    use_flow = args.flow or args.method == "flow"

    if use_flow:
        from tools.shopee_ad.flow_ad_generator import generate_flow_ad
        generate_flow_ad(zip_path=target_zip, speed=args.speed, profile_id=args.profile)
    else:
        run_pipeline(zip_path=target_zip, speed=args.speed, profile_id=args.profile, mode_9_16=args.mode)


if __name__ == "__main__":
    main()
