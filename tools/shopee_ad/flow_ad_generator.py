"""Google Flow Ad Generator: Method 2 (Hybrid Google Flow AI Video + Real Product Photos).

Completely data-driven: loads or generates storyboard dynamically for ANY product,
submits human lifestyle scenes to Google Flow Omni 1.1 Flash, and pairs them with
authentic product photos from Shopee zip (Ken Burns 9:16).
"""
import json
import logging
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from tools.shopee_ad.config import (
    FLOWKIT_API_URL,
    OUTPUT_ROOT,
    SHOPEE_DOWNLOADS_DIR,
    list_available_zips,
)
from tools.shopee_ad.product_parser import ProductInfo, parse_product_zip
from tools.shopee_ad.storyboard import SceneDefinition, load_or_create_storyboard
from tools.shopee_ad.omnivoice_client import generate_speech
from tools.shopee_ad.asset_extractor import extract_zip, create_image_slide_clip
from tools.shopee_ad.video_assembler import assemble_scene_clip, concat_scenes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def http_json(url: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """Helper to perform HTTP requests returning parsed JSON."""
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_flow_ready() -> bool:
    """Check if FlowKit server is running and extension is connected."""
    try:
        data = http_json(f"{FLOWKIT_API_URL}/health")
        return data.get("status") == "ok" and data.get("extension_connected") is True
    except Exception:
        return False


def get_or_create_flow_project(product: ProductInfo) -> str:
    """Create a FlowKit project for this product."""
    payload = {
        "name": f"Shopee Ad - {product.name[:35]}",
        "story": f"Dynamic TikTok/Shopee Video ad for {product.name}. High conversion lifestyle showcase.",
        "material": "realistic",
        "language": "vi",
    }
    res = http_json(f"{FLOWKIT_API_URL}/api/projects", method="POST", data=payload)
    project_id = res["id"]
    logger.info(f"FlowKit project ready: {project_id} ('{res['name']}')")
    return project_id


def poll_omni_workflows(
    project_id: str,
    workflows: list[dict],
    poll_interval_s: int = 6,
    timeout_s: int = 300,
) -> dict[str, str]:
    """Poll Omni workflows until all are COMPLETED and return mapping primary_media_id -> url."""
    if not workflows:
        return {}

    start_time = time.time()
    url = f"{FLOWKIT_API_URL}/api/flow/check-omni-status"
    req_body = {"workflows": workflows, "project_id": project_id}

    while time.time() - start_time < timeout_s:
        try:
            status = http_json(url, method="POST", data=req_body)
            done = status.get("done", False)
            wf_list = status.get("workflows", [])

            completed = sum(1 for w in wf_list if w.get("done") is True)
            total = len(wf_list)
            logger.info(f"[Omni Video] Tiến độ: {completed}/{total} video hoàn thành...")

            if done or completed == total:
                logger.info(f"🎉 Tất cả {total} video Omni đã hoàn thành!")
                urls = {}
                for w in wf_list:
                    media_id = w.get("primary_media_id")
                    media_data = w.get("media") or {}
                    video_url = media_data.get("url")
                    if media_id and video_url:
                        urls[media_id] = video_url
                return urls

        except Exception as e:
            logger.warning(f"Lỗi kiểm tra tiến độ Omni: {e}")

        time.sleep(poll_interval_s)

    raise TimeoutError(f"Quá thời gian ({timeout_s}s) chờ sinh video Omni!")


def generate_flow_ad(
    zip_path: Optional[Path] = None,
    speed: Optional[float] = None,
    profile_id: Optional[str] = None,
    cta_mode: str = "none",
    style: str = "flow_cinematic",
    regen: bool = False,
    force_storyboard: bool = False,
    custom_idea: Optional[str] = None,
) -> Path:
    """Execute Method 2 (Google Flow Omni 1.1 Flash AI Video + Real Product Photos)."""
    if not check_flow_ready():
        raise RuntimeError("FlowKit server chưa chạy hoặc Chrome Extension chưa kết nối!")

    # 1. Resolve zip file
    if zip_path is None:
        available = list_available_zips()
        if not available:
            raise RuntimeError(f"Không có file zip nào trong: {SHOPEE_DOWNLOADS_DIR}")
        zip_path = available[0]
    zip_path = Path(zip_path)

    product = parse_product_zip(zip_path)
    print("\n" + "=" * 65)
    print("🚀 BẮT ĐẦU SẢN XUẤT VIDEO AI HYBRID (GOOGLE FLOW + ẢNH THẬT SẢN PHẨM)")
    print(f"📦 Sản phẩm: {product.name}")
    print(f"📁 Slug thư mục: {product.slug}")
    print("=" * 65 + "\n")

    # 2. Setup product output directories
    product_dir = OUTPUT_ROOT / product.slug
    assets_dir = product_dir / "assets"
    audio_dir = product_dir / "audio"
    clips_dir = product_dir / "clips"
    scenes_dir = product_dir / "scenes"
    final_dir = product_dir / "final"
    for d in [product_dir, assets_dir, audio_dir, clips_dir, scenes_dir, final_dir]:
        d.mkdir(parents=True, exist_ok=True)

    dest_zip = product_dir / zip_path.name
    if zip_path.resolve() != dest_zip.resolve() and not dest_zip.exists():
        shutil.copy2(zip_path, dest_zip)
        logger.info(f"Đã sao chép zip vào thư mục sản phẩm: {dest_zip.name}")

    # Extract assets from zip if not already done
    assets = extract_zip(zip_path, assets_dir)
    images = assets["images"]

    # 3. Create Flow Project and Upload Product Reference Images
    print("🌐 [Bước 1/5] Tạo Project & nạp ảnh tham chiếu lên Google Flow...")
    project_id = get_or_create_flow_project(product)

    ref_media_ids = []
    if images:
        print("📸 [Tham Chiếu] Tải ảnh sản phẩm từ ZIP lên Google Flow làm hình ảnh tham chiếu...")
        for img in images[:2]:
            try:
                res_up = http_json(
                    f"{FLOWKIT_API_URL}/api/flow/upload-image",
                    method="POST",
                    data={
                        "file_path": str(img.resolve()),
                        "project_id": project_id,
                    },
                )
                m_id = res_up.get("media_id")
                if m_id:
                    ref_media_ids.append(m_id)
                    logger.info(f"Đã upload ảnh tham chiếu: {img.name} -> {m_id}")
            except Exception as e:
                logger.warning(f"Không thể upload ảnh tham chiếu {img.name}: {e}")

    # 4. Load or create dynamic storyboard
    print("\n📋 [Bước 2/5] Nạp hoặc tạo kịch bản động (storyboard.json)...")
    storyboard_file = product_dir / "storyboard.json"
    scenes = load_or_create_storyboard(
        product,
        storyboard_file,
        style=style,
        cta_mode=cta_mode,
        force=force_storyboard or regen,
        custom_idea=custom_idea,
    )

    # 5. Generate Voiceover via OmniVoice
    print(f"\n🎙️ [Bước 3/5] Sinh giọng đọc OmniVoice cho {len(scenes)} phân cảnh...")
    audio_files = {}
    audio_durations = {}
    for sc in scenes:
        idx = sc.id
        out_wav = audio_dir / f"scene_{idx:02d}.wav"
        print(f"  • Scene {idx}: {sc.overlay_title}")
        dur = generate_speech(
            text=sc.narrator_text,
            output_path=out_wav,
            speed=speed,
            profile_id=profile_id,
        )
        audio_files[idx] = out_wav
        audio_durations[idx] = dur

    # 6. Generate AI Video for Human Scenes via Google Flow
    print("\n🎬 [Bước 4/5] Gửi yêu cầu sinh Video AI tới Google Flow...")
    ai_workflows = []
    ai_scene_media_map = {}

    for sc in scenes:
        if sc.kind in ("FLOW_AI", "AI"):
            idx = sc.id
            raw_clip_path = clips_dir / f"hybrid_raw_{idx:02d}.mp4"
            if not regen and raw_clip_path.exists() and raw_clip_path.stat().st_size > 100000:
                print(f"  • Scene {idx} (AI): Đã có clip sẵn ({raw_clip_path.name}), bỏ qua gửi yêu cầu.")
                continue

            print(f"  • Đang gửi Scene {idx} (AI): {sc.overlay_title}...")
            payload = {
                "prompt": sc.prompt,
                "project_id": "",  # Empty to bind to active Google Flow session project
                "duration_s": 6,
                "aspect_ratio": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "resolution": "720p",
            }
            res = http_json(f"{FLOWKIT_API_URL}/api/flow/generate-video-omni-text", method="POST", data=payload)
            wf = res.get("workflows", [{}])[0]
            media_id = wf.get("primary_media_id")
            ai_workflows.append(wf)
            ai_scene_media_map[idx] = media_id
            logger.info(f"Scene {idx} submitted: media_id={media_id}")
            time.sleep(2.5)

    # Poll for completion if any AI scenes were requested
    ai_video_urls = {}
    if ai_workflows:
        print("\n⏳ Đang theo dõi tiến độ sinh video AI từ Google Cloud (~40-60s)...")
        flow_pid = ai_workflows[0].get("project_id") or ""
        ai_video_urls = poll_omni_workflows(flow_pid, ai_workflows, poll_interval_s=6, timeout_s=300)

    # 7. Prepare Clips & Assemble with Fixed Audio Mapping
    print("\n✨ [Bước 5/5] Ráp video, ghép giọng thuyết minh tiếng Việt và chèn Text Overlay...")
    assembled_scenes = []

    for sc in scenes:
        idx = sc.id
        raw_clip_path = clips_dir / f"hybrid_raw_{idx:02d}.mp4"
        dur = audio_durations[idx] + 0.4

        if sc.kind in ("FLOW_AI", "AI"):
            if regen or not (raw_clip_path.exists() and raw_clip_path.stat().st_size > 100000):
                media_id = ai_scene_media_map.get(idx)
                if not media_id:
                    raise RuntimeError(f"Scene {idx} chưa có media_id được submit!")
                video_url = ai_video_urls.get(media_id)
                if not video_url:
                    raise RuntimeError(f"Scene {idx} không tìm thấy video URL từ Google Flow!")
                print(f"  • Đang tải AI clip Scene {idx} từ Google Flow...")
                urllib.request.urlretrieve(video_url, raw_clip_path)

        elif sc.kind in ("PRODUCT_PHOTO", "IMAGE_SLIDE"):
            img_idx = sc.image_index % len(images) if images else 0
            img_path = images[img_idx]
            print(f"  • Tạo shot sản phẩm thật từ ảnh {img_path.name} (Scene {idx})...")
            create_image_slide_clip(img_path, dur, raw_clip_path)

        scene_out = scenes_dir / f"scene_{idx:02d}_hybrid_assembled.mp4"
        print(f"  • Ráp Scene {idx}: {sc.overlay_title} (OmniVoice: {audio_durations[idx]:.2f}s)...")
        assemble_scene_clip(
            video_path=raw_clip_path,
            audio_path=audio_files[idx],
            output_path=scene_out,
            title_text=sc.overlay_title,
            subtitle_text=sc.overlay_subtitle,
            audio_duration=audio_durations[idx],
            remove_watermark=(sc.kind in ("FLOW_AI", "AI")),
        )
        assembled_scenes.append(scene_out)

    final_output = final_dir / f"{product.slug}_hybrid_final.mp4"
    print("\n🎞️ Đang ghép toàn bộ các phân cảnh thành video cuối cùng...")
    concat_scenes(assembled_scenes, final_output)

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH XUẤT SẮC! Video AI Hybrid đã lưu tại:")
    print(f"👉 {final_output.resolve()}")
    print("=" * 65 + "\n")
    return final_output


if __name__ == "__main__":
    generate_flow_ad()
