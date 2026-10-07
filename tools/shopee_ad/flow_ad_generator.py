"""Google Flow Ad Generator: Method 2 (Hybrid Google Flow AI Video + Real Product Photos).

Completely data-driven: loads or generates storyboard dynamically for ANY product,
submits human lifestyle scenes to Google Flow Omni 1.1 Flash, and pairs them with
authentic product photos from Shopee zip (Ken Burns 9:16).
"""
import base64
import json
import logging
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict
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
from tools.shopee_ad.product_parser import ProductInfo, parse_product_zip
from tools.shopee_ad.storyboard import (
    SceneDefinition,
    load_or_create_storyboard,
    generate_default_storyboard,
)
from tools.shopee_ad.omnivoice_client import generate_speech
from tools.shopee_ad.asset_extractor import extract_zip, create_image_slide_clip
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
from tools.common.naming import build_variant_suffix

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


def upload_image_to_flow(image_path: Path, project_id: str = "") -> str:
    """Upload a local image file to Google Flow via Base64 and return its media_id (UUID)."""
    image_bytes = image_path.read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "image_base64": b64,
        "file_name": image_path.name,
        "project_id": project_id,
    }
    res = http_json(f"{FLOWKIT_API_URL}/api/flow/upload-image", method="POST", data=payload)
    media_id = res.get("media_id")
    if not media_id:
        raise RuntimeError(f"Upload ảnh thất bại, không nhận được media_id: {res}")
    return media_id


def extract_character_anchor(video_path: Path, output_image: Path, time_sec: float = 1.2) -> Path:
    """Extract a sharp, stable anchor portrait frame of the character from the first video clip."""
    output_image.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(time_sec),
        "-i", str(video_path),
        "-frames:v", "1",
        "-update", "1",
        str(output_image),
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_image


def poll_omni_jobs(
    jobs: list[dict],
    poll_interval_s: int = 5,
    timeout_s: int = 600,
) -> dict[int, str]:
    """Poll both workflow jobs (text-to-video) and operation jobs (ref-to-video) until all complete."""
    if not jobs:
        return {}

    pending = {j["scene_id"]: j for j in jobs}
    results = {}
    start_time = time.time()

    while pending and (time.time() - start_time < timeout_s):
        # 1. Poll workflow jobs
        wf_jobs = [j for j in pending.values() if j.get("type") == "workflow"]
        if wf_jobs:
            try:
                wf_list = [j["workflow"] for j in wf_jobs]
                pid = wf_jobs[0]["workflow"].get("project_id") or ""
                res = http_json(
                    f"{FLOWKIT_API_URL}/api/flow/check-omni-status",
                    method="POST",
                    data={"workflows": wf_list, "project_id": pid},
                )
                returned_wfs = res.get("workflows", [])
                for rw in returned_wfs:
                    if rw.get("done") is True:
                        m_id = rw.get("primary_media_id")
                        v_url = (rw.get("media") or {}).get("url")
                        for j in wf_jobs:
                            if j.get("primary_media_id") == m_id:
                                sid = j["scene_id"]
                                if v_url and sid in pending:
                                    results[sid] = v_url
                                    del pending[sid]
                                    logger.info(f"🎉 Scene {sid} (Text-to-Video) hoàn thành!")
            except Exception as e:
                logger.warning(f"Lỗi kiểm tra tiến độ workflow: {e}")

        # 2. Poll operation jobs (Reference-to-Video abra_r2v)
        op_jobs = [j for j in pending.values() if j.get("type") == "operation"]
        if op_jobs:
            try:
                ops_payload = [{"name": j["op_name"]} for j in op_jobs]
                pid = op_jobs[0]["project_id"]
                res = http_json(
                    f"{FLOWKIT_API_URL}/api/flow/check-status",
                    method="POST",
                    data={"operations": ops_payload, "project_id": pid},
                )
                returned_ops = res.get("operations", [])
                for rop in returned_ops:
                    op_data = rop.get("operation") or {}
                    op_name = op_data.get("name") or rop.get("name")
                    status = rop.get("status")

                    if status == "MEDIA_GENERATION_STATUS_SUCCESSFUL":
                        v_meta = op_data.get("metadata", {}).get("video", {})
                        v_url = v_meta.get("fifeUrl") or v_meta.get("url")
                        for j in op_jobs:
                            if j.get("op_name") == op_name:
                                sid = j["scene_id"]
                                if v_url and sid in pending:
                                    results[sid] = v_url
                                    del pending[sid]
                                    logger.info(f"🎉 Scene {sid} (Consistent Ref-to-Video) hoàn thành!")
                    elif status == "MEDIA_GENERATION_STATUS_FAILED":
                        err_msg = rop.get("error") or "Unknown generation error"
                        raise RuntimeError(f"Google Flow video gen failed for op {op_name}: {err_msg}")
            except Exception as e:
                logger.warning(f"Lỗi kiểm tra tiến độ operation: {e}")

        if pending:
            time.sleep(poll_interval_s)

    if pending:
        raise TimeoutError(f"Quá thời gian ({timeout_s}s) chờ các scenes: {list(pending.keys())}")

    return results


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
    channel_name: Optional[str] = None,
    channel_handle: Optional[str] = None,
    no_voice: bool = False,
    no_overlay: bool = False,
    tag: Optional[str] = None,
    bgm_path: Optional[Path | str] = None,
    target_scenes: Optional[List[int]] = None,
) -> Path:
    """Execute Method 2 (Google Flow Omni 1.1 Flash AI Video + Real Product Photos)."""
    channel_name = channel_name or DEFAULT_CHANNEL_NAME
    channel_handle = channel_handle or DEFAULT_CHANNEL_HANDLE

    variant = build_variant_suffix(
        style=style,
        no_overlay=no_overlay,
        cta_mode=cta_mode,
        default_cta="shopee",
        tag=tag,
    )

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
    if target_scenes:
        print(f"🎯 Chế độ tái tạo phân cảnh chọn lọc: Scenes {target_scenes}")
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
                m_id = upload_image_to_flow(img, project_id=project_id)
                if m_id:
                    ref_media_ids.append(m_id)
                    logger.info(f"Đã upload ảnh tham chiếu sản phẩm: {img.name} -> {m_id}")
            except Exception as e:
                logger.warning(f"Không thể upload ảnh tham chiếu {img.name}: {e}")

    # 4. Load or create dynamic storyboard
    print(f"\n📋 [Bước 2/5] Nạp hoặc tạo kịch bản động (storyboard_{style}.json)...")
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

    # If targeting specific scenes, refresh prompt definitions for target scenes from default builder
    if target_scenes:
        fresh_scenes = generate_default_storyboard(
            product,
            style=style,
            cta_mode=cta_mode,
            custom_idea=custom_idea,
            channel_name=channel_name,
        )
        fresh_by_id = {fs.id: fs for fs in fresh_scenes}
        for sc in scenes:
            if sc.id in target_scenes and sc.id in fresh_by_id:
                fs = fresh_by_id[sc.id]
                sc.prompt = fs.prompt
                sc.video_prompt = fs.video_prompt
                sc.narrator_text = fs.narrator_text
                sc.overlay_title = fs.overlay_title
                sc.overlay_subtitle = fs.overlay_subtitle
                print(f"  • Cập nhật kịch bản chuẩn cho Scene {sc.id}: {sc.overlay_title}")
        with open(storyboard_file, "w", encoding="utf-8") as f:
            json.dump([asdict(s) for s in scenes], f, ensure_ascii=False, indent=2)

    # 5. Generate Voiceover via OmniVoice (or Silent POV timing)
    audio_files = {}
    audio_durations = {}
    if not no_voice:
        print(f"\n🎙️ [Bước 3/5] Sinh giọng đọc OmniVoice cho {len(scenes)} phân cảnh...")
        for sc in scenes:
            idx = sc.id
            out_wav = audio_dir / f"{variant}_scene_{idx:02d}.wav"
            is_target_scene = bool(target_scenes and idx in target_scenes)
            if out_wav.exists() and out_wav.stat().st_size > 1000 and (target_scenes and not is_target_scene):
                dur = float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_wav)],
                    capture_output=True, text=True, check=True
                ).stdout.strip())
                audio_files[idx] = out_wav
                audio_durations[idx] = dur
                print(f"  • Scene {idx}: Đã có audio sẵn ({dur:.2f}s), giữ nguyên.")
                continue

            print(f"  • Scene {idx}: {sc.overlay_title}")
            dur = generate_speech(
                text=sc.narrator_text,
                output_path=out_wav,
                speed=speed,
                profile_id=profile_id,
            )
            audio_files[idx] = out_wav
            audio_durations[idx] = dur
    else:
        print(f"\n🔇 [Bước 3/5] Chế độ Không Voiceover (Silent POV) - Nhịp cắt chuẩn 5.0s/cảnh...")
        for sc in scenes:
            audio_files[sc.id] = None
            audio_durations[sc.id] = 5.0

    ai_scenes = [sc for sc in scenes if sc.kind in ("FLOW_AI", "AI")]

    # 6. Generate AI Video with Character Consistency via Google Flow
    is_faceless = (
        style in ("faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov")
        or (
            bool(ai_scenes)
            and all(
                (
                    "no face" in (s.prompt or "").lower()
                    or "hands only" in (s.prompt or "").lower()
                    or "no human face" in (s.prompt or "").lower()
                )
                for s in ai_scenes
            )
        )
    )
    if is_faceless:
        print("\n🎬 [Bước 4/5] Gửi yêu cầu sinh Video AI tới Google Flow (Phong cách POV / Hands-On 100% Không Lộ Mặt)...")
    else:
        print("\n🎬 [Bước 4/5] Gửi yêu cầu sinh Video AI tới Google Flow (Bảo đảm nhân vật nhất quán)...")

    # Find Scene 1 (the anchor scene that establishes the human character)
    scene_1 = next((sc for sc in ai_scenes if sc.id == 1), (ai_scenes[0] if ai_scenes else None))
    char_media_id = None

    if scene_1 and not is_faceless:
        s1_clip = clips_dir / f"{style}_raw_{scene_1.id:02d}.mp4"
        anchor_img = clips_dir / f"{style}_character_anchor.jpg"

        # Check if Scene 1 video already exists and is valid
        need_s1_gen = regen or force_storyboard or (not s1_clip.exists()) or (s1_clip.stat().st_size < 100000)

        if need_s1_gen:
            print(f"  • Đang gửi Scene {scene_1.id} (Anchor Nhân Vật): {scene_1.overlay_title}...")
            payload = {
                "prompt": scene_1.prompt,
                "project_id": project_id,
                "duration_s": 6,
                "aspect_ratio": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "resolution": "720p",
            }
            res_s1 = http_json(f"{FLOWKIT_API_URL}/api/flow/generate-video-omni-text", method="POST", data=payload)
            wf_s1 = res_s1.get("workflows", [{}])[0]
            s1_job = {
                "scene_id": scene_1.id,
                "type": "workflow",
                "workflow": wf_s1,
                "primary_media_id": wf_s1.get("primary_media_id"),
            }
            print("  ⏳ Chờ sinh video Scene 1 để trích xuất khuôn mặt nhân vật chuẩn (~35s)...")
            s1_urls = poll_omni_jobs([s1_job], poll_interval_s=5, timeout_s=300)
            v_url = s1_urls.get(scene_1.id)
            if not v_url:
                raise RuntimeError(f"Scene {scene_1.id} không lấy được video URL từ Google Flow!")
            print(f"  ⬇️ Đang tải video Scene 1 về: {s1_clip.name}...")
            urllib.request.urlretrieve(v_url, s1_clip)

        # Trích xuất khung hình chân dung nhân vật từ Scene 1 để neo mặt cho các cảnh sau
        try:
            print("  🎯 [Nhân Vật Nhất Quán] Đang trích xuất frame chân dung nhân vật từ Scene 1...")
            extract_character_anchor(s1_clip, anchor_img, time_sec=1.2)
            char_media_id = upload_image_to_flow(anchor_img, project_id=project_id)
            print(f"  ✅ [Nhân Vật Nhất Quán] Đã upload Anchor Frame lên Flow -> media_id: {char_media_id}")
        except Exception as e:
            logger.warning(f"Không thể trích xuất / upload character anchor: {e}")

    # Gửi các phân cảnh AI còn lại
    pending_jobs = []
    for sc in ai_scenes:
        idx = sc.id
        raw_clip_path = clips_dir / f"{style}_raw_{idx:02d}.mp4"

        # Nếu là scene 1 (chế độ có mặt) thì đã xử lý ở trên
        if not is_faceless and scene_1 and idx == scene_1.id and raw_clip_path.exists() and raw_clip_path.stat().st_size > 100000:
            continue

        is_targeted = target_scenes is None or idx in target_scenes
        clip_exists = raw_clip_path.exists() and raw_clip_path.stat().st_size > 100000
        if clip_exists:
            if target_scenes is not None:
                if not is_targeted:
                    print(f"  • Scene {idx} (AI): Đã có clip sẵn ({raw_clip_path.name}), bỏ qua (không trong danh sách --scene).")
                    continue
            else:
                if not (regen or force_storyboard):
                    print(f"  • Scene {idx} (AI): Đã có clip sẵn ({raw_clip_path.name}), bỏ qua.")
                    continue

        p_lower = (sc.prompt or "").lower()
        is_faceless_scene = (
            is_faceless
            or "no face" in p_lower
            or "hands only" in p_lower
            or "no human face" in p_lower
            or "macro" in p_lower
            or "top-down" in p_lower
            or "overhead" in p_lower
        )
        has_human_words = any(
            re.search(r"\b" + re.escape(w) + r"\b", p_lower)
            for w in ["person", "professional", "creator", "homemaker", "model", "man", "woman", "same", "persona", "actor", "traveler"]
        )
        is_human_scene = (not is_faceless_scene) and has_human_words

        if is_human_scene and char_media_id:
            print(f"  • Đang gửi Scene {idx} (AI - Reference Nhân Vật Nhất Quán): {sc.overlay_title}...")
            payload = {
                "reference_media_ids": [char_media_id],
                "prompt": sc.prompt,
                "project_id": project_id,
                "duration_s": 6,
                "aspect_ratio": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "resolution": "720p",
            }
            res = http_json(f"{FLOWKIT_API_URL}/api/flow/generate-video-omni", method="POST", data=payload)
            op = res.get("operations", [{}])[0].get("operation", {})
            op_name = op.get("name")
            pending_jobs.append({
                "scene_id": idx,
                "type": "operation",
                "op_name": op_name,
                "project_id": project_id,
            })
            logger.info(f"Scene {idx} submitted (abra_r2v consistent character): op_name={op_name}")
        elif (
            ref_media_ids
            and getattr(sc, "use_product_ref", True)
            and getattr(sc, "image_index", 0) is not None
            and getattr(sc, "image_index", 0) >= 0
            and (is_faceless_scene or "hands" in p_lower or "product" in p_lower)
        ):
            print(f"  • Đang gửi Scene {idx} (AI - Reference Sản Phẩm ZIP): {sc.overlay_title}...")
            ref_idx = sc.image_index % len(ref_media_ids) if ref_media_ids else 0
            payload = {
                "reference_media_ids": [ref_media_ids[ref_idx]],
                "prompt": sc.prompt,
                "project_id": project_id,
                "duration_s": 6,
                "aspect_ratio": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "resolution": "720p",
            }
            res = http_json(f"{FLOWKIT_API_URL}/api/flow/generate-video-omni", method="POST", data=payload)
            op = res.get("operations", [{}])[0].get("operation", {})
            op_name = op.get("name")
            pending_jobs.append({
                "scene_id": idx,
                "type": "operation",
                "op_name": op_name,
                "project_id": project_id,
            })
            logger.info(f"Scene {idx} submitted (abra_r2v product): op_name={op_name}")
        else:
            print(f"  • Đang gửi Scene {idx} (AI Text-to-Video): {sc.overlay_title}...")
            payload = {
                "prompt": sc.prompt,
                "project_id": project_id,
                "duration_s": 6,
                "aspect_ratio": "VIDEO_ASPECT_RATIO_PORTRAIT",
                "resolution": "720p",
            }
            res = http_json(f"{FLOWKIT_API_URL}/api/flow/generate-video-omni-text", method="POST", data=payload)
            wf = res.get("workflows", [{}])[0]
            pending_jobs.append({
                "scene_id": idx,
                "type": "workflow",
                "workflow": wf,
                "primary_media_id": wf.get("primary_media_id"),
            })
            logger.info(f"Scene {idx} submitted (abra_t2v): media_id={wf.get('primary_media_id')}")

        time.sleep(2.0)

    # Chờ hoàn thành và tải về toàn bộ AI clips
    if pending_jobs:
        print(f"\n⏳ Đang theo dõi tiến độ sinh {len(pending_jobs)} AI clips từ Google Flow...")
        download_urls = poll_omni_jobs(pending_jobs, poll_interval_s=5, timeout_s=600)
        for job in pending_jobs:
            sid = job["scene_id"]
            url = download_urls.get(sid)
            clip_dst = clips_dir / f"{style}_raw_{sid:02d}.mp4"
            if url:
                print(f"  ⬇️ Đang tải AI clip Scene {sid} từ Google Flow ({clip_dst.name})...")
                urllib.request.urlretrieve(url, clip_dst)

    # 7. Prepare Clips & Assemble with Fixed Audio Mapping
    print("\n✨ [Bước 5/5] Ráp video, ghép giọng thuyết minh tiếng Việt và chèn Text Overlay...")
    assembled_scenes = []

    for sc in scenes:
        idx = sc.id
        raw_clip_path = clips_dir / f"{style}_raw_{idx:02d}.mp4"
        dur = audio_durations[idx] + 0.4

        if sc.kind in ("PRODUCT_PHOTO", "IMAGE_SLIDE"):
            img_idx = sc.image_index % len(images) if images else 0
            img_path = images[img_idx]
            print(f"  • Tạo shot sản phẩm thật từ ảnh {img_path.name} (Scene {idx})...")
            create_image_slide_clip(img_path, dur, raw_clip_path)

        scene_out = scenes_dir / f"{variant}_flow_assembled_{idx:02d}.mp4"
        title_to_burn = None if no_overlay else sc.overlay_title
        subtitle_to_burn = None if no_overlay else sc.overlay_subtitle
        timing_info = f"OmniVoice: {audio_durations[idx]:.2f}s" if not no_voice else "Silent: 5.0s"
        print(f"  • Ráp Scene {idx}: {sc.overlay_title} ({timing_info})...")
        assemble_scene_clip(
            video_path=raw_clip_path,
            audio_path=audio_files.get(idx),
            output_path=scene_out,
            title_text=title_to_burn,
            subtitle_text=subtitle_to_burn,
            audio_duration=audio_durations[idx],
            target_duration=5.5 if no_voice else None,
            remove_watermark=(sc.kind in ("FLOW_AI", "AI")),
        )
        assembled_scenes.append(scene_out)

    effective_bgm = resolve_bgm_path(custom_bgm=bgm_path, style=style, product_assets_dir=assets_dir)
    if effective_bgm:
        print(f"🎵 [Nhạc Nền BGM] Tự động kích hoạt: {effective_bgm.name}...")

    if not no_voice:
        final_output = final_dir / f"{product.slug}_flow_{variant}.mp4"
        print(f"\n🎞️ Đang ghép toàn bộ các phân cảnh thành video {final_output.name}...")
        concat_scenes(assembled_scenes, final_output, bgm_path=effective_bgm)
        video_map = {"flow": final_output}
    else:
        final_output = final_dir / f"{product.slug}_flow_{variant}_silent.mp4"
        print(f"\n🎞️ Đang ghép toàn bộ các phân cảnh thành video {final_output.name}...")
        concat_scenes(assembled_scenes, final_output, bgm_path=effective_bgm)
        video_map = {"flow_silent": final_output}

    print("📝 Đang tạo bộ caption & metadata đa nền tảng (Facebook, TikTok, YouTube Shorts)...")
    caption_files = generate_all_platform_captions(
        product,
        scenes,
        final_dir,
        channel_name=channel_name,
        channel_handle=channel_handle,
        variant_suffix=variant,
    )

    # 8. Generate 9:16 Cover Image (Thumbnail)
    raw_s1 = clips_dir / f"{style}_raw_01.mp4"
    cover_source = raw_s1 if (raw_s1.exists() and raw_s1.stat().st_size > 1000) else (assembled_scenes[0] if assembled_scenes else final_output)
    if not cover_source.exists() or cover_source.stat().st_size < 1000:
        cover_source = final_output
    cover_path = final_dir / f"{product.slug}_{variant}_cover.jpg"
    print("🖼️ Đang tạo ảnh bìa (Cover / Thumbnail) 9:16 chuẩn đa nền tảng...")
    try:
        create_cover_image(cover_source, product, scenes, cover_path)
    except Exception as e:
        logger.warning(f"Lỗi tạo ảnh bìa: {e}")

    # 9. Xuất file audio thuyết minh đầy đủ và text kịch bản lời thoại
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

    # 10. Generate Publishing Guide for all 3 platforms
    guide_path = final_dir / f"{product.slug}_{variant}_publish_guide.txt"
    local_output = final_dir / f"{product.slug}_local_{variant}.mp4"
    if local_output.exists():
        video_map["local"] = local_output
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

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH XUẤT SẮC BỘ OUTPUT SẢN PHẨM:")
    print(f"👉 1. Video chuẩn Flow:       {final_output.resolve()}")
    if "local" in video_map:
        print(f"👉 2. Video chuẩn Local:      {local_output.resolve()}")
    if voiceover_path:
        print(f"👉 3. Audio lời thoại đầy đủ: {voiceover_path.resolve()}")
    print(f"👉 4. Text kịch bản & time:   {script_path.resolve()}")
    print(f"👉 5. Ảnh bìa thu nhỏ:        {cover_path.resolve()}")
    print(f"👉 6. Hướng dẫn chi tiết:     {guide_path.resolve()}")
    print("=" * 65 + "\n")
    return final_output


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Google Flow AI Ad Generator for Shopee Products")
    parser.add_argument("--zip", type=str, default=None, help="Đường dẫn đến file zip sản phẩm Shopee")
    parser.add_argument("--speed", type=float, default=None, help="Tốc độ đọc giọng nói OmniVoice")
    parser.add_argument("--profile", type=str, default=None, help="Profile ID giọng nói trên VoiceStudio")
    parser.add_argument("--cta", type=str, default="none", choices=["none", "follow", "shopee", "tiktok"], help="Chế độ kết thúc kêu gọi hành động")
    parser.add_argument("--style", type=str, default="flow_cinematic", help="Phong cách kịch bản (flow_cinematic, faceless_pov, problem_solution, lifestyle_edc)")
    parser.add_argument("--no-voice", "--silent", dest="no_voice", action="store_true", help="Không tạo voiceover thuyết minh (video thuần hình ảnh)")
    parser.add_argument("--no-overlay", "--clean", dest="no_overlay", action="store_true", help="Không chèn chữ Text Overlay (video sạch để tự chèn trên TikTok)")
    parser.add_argument("--regen", action="store_true", help="Bắt buộc tạo lại video AI mới")
    parser.add_argument("--force-storyboard", action="store_true", help="Bắt buộc nạp kịch bản mới")
    parser.add_argument("--idea", type=str, default=None, help="Ý tưởng kịch bản tùy chỉnh")
    parser.add_argument("--channel-name", type=str, default=DEFAULT_CHANNEL_NAME, help="Tên kênh xuất bản")
    parser.add_argument("--channel-handle", type=str, default=DEFAULT_CHANNEL_HANDLE, help="Handle/ID kênh")
    parser.add_argument("--tag", type=str, default=None, help="Gắn nhãn/tag tùy chỉnh cho video xuất bản (ví dụ: --tag v2)")
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
        help="Bật nhạc nền BGM (mặc định tắt): gõ --bgm để ngẫu nhiên từ assets/bgm/ hoặc --bgm <path> chỉ định file",
    )

    args = parser.parse_args()
    target_zip = Path(args.zip) if args.zip else None

    generate_flow_ad(
        zip_path=target_zip,
        speed=args.speed,
        profile_id=args.profile,
        cta_mode=args.cta,
        style=args.style,
        no_voice=args.no_voice,
        no_overlay=args.no_overlay,
        regen=args.regen,
        force_storyboard=args.force_storyboard or bool(args.idea),
        target_scenes=args.scene,
        custom_idea=args.idea,
        channel_name=args.channel_name,
        channel_handle=args.channel_handle,
        tag=args.tag,
        bgm_path=args.bgm,
    )


if __name__ == "__main__":
    main()
