#!/usr/bin/env python3
"""Worker for the FlowKit provider-job queue backed by google-flow-mcp.

This script implements the *worker side* of the provider-job protocol against
the FlowKit HTTP API (``/api/provider-jobs``). It is the counterpart to
``AssistantProvider.run()`` (the producer side), which inserts QUEUED rows and
blocks until a worker finishes them.

It routes generation tasks (image, edit_image, i2v, r2v, upscale) to
Google Flow via the ``google-flow-mcp`` Playwright automation layer.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import aiohttp

from agent.config import (
    FLOW_MCP_ACCOUNT,
    FLOW_MCP_CLI,
    FLOW_MCP_IMAGE_MODEL,
    FLOW_MCP_PROJECT,
    FLOW_MCP_VIDEO_MODEL,
    OUTPUT_DIR,
)
from agent.utils.paths import file_url_to_path, project_dir, scene_filename
from agent.utils.slugify import slugify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("assistant_worker")


class ProviderJobClient:
    """Thin async client for the /api/provider-jobs worker endpoints."""

    def __init__(self, api_base: str, worker_id: str, lease_ttl_s: float = 300):
        self.api_base = api_base.rstrip("/")
        self.worker_id = worker_id
        self.lease_ttl_s = lease_ttl_s
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *exc):
        if self._session:
            await self._session.close()
            self._session = None

    def _url(self, path: str) -> str:
        return f"{self.api_base}/provider-jobs{path}"

    async def wait_next(self, provider: str, timeout_s: float = 60) -> dict | None:
        """Long-poll for the next claimable job; returns the claimed row or None."""
        assert self._session is not None
        params = {
            "provider": provider,
            "worker_id": self.worker_id,
            "lease_ttl_s": self.lease_ttl_s,
            "timeout_s": timeout_s,
        }
        async with self._session.get(self._url("/wait-next"), params=params) as resp:
            if resp.status == 204:
                return None
            resp.raise_for_status()
            return await resp.json()

    async def heartbeat(self, job_id: str) -> dict:
        assert self._session is not None
        async with self._session.post(
            self._url(f"/{job_id}/heartbeat"),
            json={"worker_id": self.worker_id, "lease_ttl_s": self.lease_ttl_s},
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def progress(self, job_id: str, pct: int, message: str | None = None) -> None:
        assert self._session is not None
        async with self._session.post(
            self._url(f"/{job_id}/progress"),
            json={"worker_id": self.worker_id, "progress": pct, "message": message},
        ) as resp:
            resp.raise_for_status()

    async def complete(
        self, job_id: str, output_url: str, media_id: str | None = None
    ) -> dict:
        assert self._session is not None
        result = {"output_url": output_url}
        if media_id:
            result["media_id"] = media_id
        async with self._session.post(
            self._url(f"/{job_id}/complete"),
            json={"worker_id": self.worker_id, "result": result},
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def fail(self, job_id: str, error: str) -> dict:
        assert self._session is not None
        async with self._session.post(
            self._url(f"/{job_id}/fail"),
            json={"worker_id": self.worker_id, "error": error},
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


# ---------------------------------------------------------------------------
# Flow MCP Generation Backend
# ---------------------------------------------------------------------------

def _resolve_local_file(url_or_path: str | None) -> Path | None:
    if not url_or_path:
        return None
    p = file_url_to_path(url_or_path)
    if p is not None and p.is_file():
        return p
    direct = Path(url_or_path)
    if direct.is_file():
        return direct
    return None


def _get_project_context(extra: dict) -> tuple[str, str, Path]:
    project_name = extra.get("project_name") or FLOW_MCP_PROJECT or "FlowKit Project"
    proj_slug = slugify(project_name) or "flowkit-project"
    p_dir = project_dir(proj_slug)
    return project_name, proj_slug, p_dir


def _run_flow_mcp_generate(payload: dict) -> dict:
    if not FLOW_MCP_CLI or not Path(FLOW_MCP_CLI).exists():
        raise RuntimeError(
            f"FLOW_MCP_CLI executable not found at '{FLOW_MCP_CLI}'. "
            "Please build google-flow-mcp or set FLOW_MCP_CLI in the environment."
        )

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(payload, tf, ensure_ascii=False)
        tf_path = tf.name

    account = FLOW_MCP_ACCOUNT or "chromium"
    timeout_s = (payload.get("maxWaitSeconds") or 360) + 60
    cmd = ["node", str(FLOW_MCP_CLI), "account", "generate", account, "--payload", tf_path]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"flow-mcp-cli failed (exit code {proc.returncode}): {proc.stderr or proc.stdout}"
            )
        data = json.loads(proc.stdout.strip())
        files = data.get("downloadedFiles") or []
        if not files:
            raise RuntimeError(f"flow-mcp-cli returned no downloadedFiles: {proc.stdout}")
        return data
    finally:
        try:
            os.remove(tf_path)
        except OSError:
            pass


def _generate_image_sync(job: dict) -> dict:
    extra = job.get("extra") or {}
    orientation = (job.get("orientation") or "HORIZONTAL").upper()
    aspect_enum = extra.get("aspect", "")
    if "PORTRAIT" in aspect_enum or orientation == "VERTICAL":
        aspect_ratio = "9:16"
    else:
        aspect_ratio = "16:9"

    mid = str(uuid.uuid4())
    project_name, _, p_dir = _get_project_context(extra)
    sub = "refs" if extra.get("kind") == "reference_image" else "images"
    out_dir = (p_dir / sub).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_files: list[str] = []
    if job.get("source_url"):
        lp = _resolve_local_file(job["source_url"])
        if lp:
            ref_files.append(str(lp.resolve()))
    for ref_u in (extra.get("reference_urls") or []):
        lp = _resolve_local_file(ref_u)
        if lp and str(lp.resolve()) not in ref_files:
            ref_files.append(str(lp.resolve()))

    prompt_text = (job.get("prompt") or "").strip()
    ref_names = extra.get("reference_names") or []
    if ref_names and ref_files:
        prompt_text = (
            f"Use the attached reference images for character and environment consistency "
            f"({', '.join(ref_names)}). {prompt_text}"
        )

    if extra.get("kind") == "reference_image" and extra.get("entity_name"):
        stem = f"ref_{slugify(extra['entity_name'])}_{mid[:8]}"
    elif extra.get("scene_id"):
        order = int(extra.get("display_order") or 0)
        stem = f"scene_{order:03d}_{extra['scene_id'][:8]}_{mid[:8]}"
    else:
        stem = f"img_{mid[:8]}"

    payload = {
        "mediaType": "image",
        "prompt": prompt_text,
        "model": FLOW_MCP_IMAGE_MODEL or "ui-default",
        "aspectRatio": aspect_ratio,
        "outputs": 1,
        "referenceFiles": ref_files[:6],
        "upscale": "none",
        "outputDirectory": str(out_dir),
        "fileName": stem,
        "download": True,
        "timeoutSeconds": 45,
        "maxWaitSeconds": 240,
    }
    if project_name:
        payload["flowProject"] = project_name

    data = _run_flow_mcp_generate(payload)
    downloaded = Path(data["downloadedFiles"][0]).resolve()

    if downloaded.suffix.lower() != ".jpg":
        try:
            from PIL import Image

            jpg_path = downloaded.with_suffix(".jpg")
            with Image.open(downloaded) as im:
                im.convert("RGB").save(jpg_path, "JPEG", quality=95)
            downloaded = jpg_path
        except ImportError:
            pass

    return {"output_url": downloaded.as_uri(), "media_id": mid}


def _generate_video_sync(job: dict) -> dict:
    extra = job.get("extra") or {}
    orientation = (job.get("orientation") or "HORIZONTAL").upper()
    aspect_ratio = "9:16" if orientation == "VERTICAL" else "16:9"

    ref_files: list[str] = []
    start_local = _resolve_local_file(job.get("start_url") or job.get("source_url"))
    if start_local:
        ref_files.append(str(start_local.resolve()))
    end_local = _resolve_local_file(job.get("end_url"))
    if end_local and str(end_local.resolve()) not in ref_files:
        ref_files.append(str(end_local.resolve()))
    if not ref_files:
        for ref_u in (extra.get("reference_urls") or []):
            lp = _resolve_local_file(ref_u)
            if lp and str(lp.resolve()) not in ref_files:
                ref_files.append(str(lp.resolve()))

    mid = str(uuid.uuid4())
    project_name, proj_slug, p_dir = _get_project_context(extra)
    out_dir = (p_dir / "scenes").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    order = int(extra.get("display_order") or 0)
    scene_id = extra.get("scene_id") or mid
    stem = scene_filename(order, scene_id[:8], ext="").rstrip(".")

    prompt_text = (job.get("prompt") or "").strip()
    material = extra.get("material")
    if start_local and material:
        prompt_text = f"Animate from the provided start frame in {material} style: {prompt_text}"

    duration = extra.get("duration_s") or job.get("duration")

    payload = {
        "mediaType": "video",
        "prompt": prompt_text,
        "model": FLOW_MCP_VIDEO_MODEL or "omni-1-2-flash",
        "aspectRatio": aspect_ratio,
        "outputs": 1,
        "referenceFiles": ref_files[:6],
        "upscale": "none",
        "outputDirectory": str(out_dir),
        "fileName": stem,
        "download": True,
        "timeoutSeconds": 60,
        "maxWaitSeconds": 600,
    }
    if project_name:
        payload["flowProject"] = project_name
    if duration:
        payload["durationSeconds"] = int(duration)

    data = _run_flow_mcp_generate(payload)
    downloaded = Path(data["downloadedFiles"][0]).resolve()

    canonical_name = scene_filename(order, scene_id, ext="mp4")
    target_path = (out_dir / canonical_name).resolve()
    if downloaded != target_path:
        shutil.copy2(downloaded, target_path)

    return {"output_url": target_path.as_uri(), "media_id": mid}


def _generate_upscale_sync(job: dict) -> dict:
    extra = job.get("extra") or {}
    project_name, proj_slug, p_dir = _get_project_context(extra)
    out_dir = (p_dir / "4k").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    order = int(extra.get("display_order") or 0)
    scene_id = extra.get("scene_id") or str(uuid.uuid4())
    target_name = scene_filename(order, scene_id, ext="mp4")
    target_path = (out_dir / target_name).resolve()

    src_local = _resolve_local_file(job.get("source_url"))
    if not src_local:
        raise ValueError(f"Upscale requires a valid source_url, got {job.get('source_url')}")

    payload = {
        "mediaType": "video",
        "prompt": "",
        "referenceFiles": [str(src_local.resolve())],
        "upscale": "2x",
        "outputDirectory": str(out_dir),
        "fileName": target_name.replace(".mp4", ""),
        "download": True,
        "timeoutSeconds": 120,
        "maxWaitSeconds": 900,
    }
    if project_name:
        payload["flowProject"] = project_name

    data = _run_flow_mcp_generate(payload)
    downloaded = Path(data["downloadedFiles"][0]).resolve()
    if downloaded != target_path:
        shutil.copy2(downloaded, target_path)

    return {"output_url": target_path.as_uri(), "media_id": str(uuid.uuid4())}


async def process_job(job: dict, client: ProviderJobClient) -> dict:
    """Generate the media for *job* via Flow MCP."""
    kind = (job.get("kind") or "").lower()
    if kind in ("image", "edit_image"):
        await client.progress(job["id"], 20, f"Generating image via Flow MCP ({FLOW_MCP_IMAGE_MODEL})")
        return await asyncio.to_thread(_generate_image_sync, job)
    if kind in ("i2v", "r2v", "video", "video_refs"):
        await client.progress(job["id"], 15, f"Generating video via Flow MCP ({FLOW_MCP_VIDEO_MODEL})")
        return await asyncio.to_thread(_generate_video_sync, job)
    if kind == "upscale":
        await client.progress(job["id"], 10, "Upscaling video via Flow MCP")
        return await asyncio.to_thread(_generate_upscale_sync, job)
    raise NotImplementedError(f"Unsupported job kind '{kind}' in assistant_worker")


# ---------------------------------------------------------------------------
# Worker loop
# ---------------------------------------------------------------------------

async def _heartbeat_loop(
    client: ProviderJobClient, job_id: str, stop: asyncio.Event
) -> None:
    """Extend the lease until the job is done."""
    interval = max(5.0, client.lease_ttl_s / 3)
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass
        if stop.is_set():
            break
        try:
            await client.heartbeat(job_id)
            logger.debug("heartbeat ok for %s", job_id[:12])
        except Exception as e:
            logger.warning("heartbeat failed for %s: %s", job_id[:12], e)


async def _handle_one(client: ProviderJobClient, job: dict) -> None:
    job_id = job["id"]
    logger.info(
        "claimed job %s kind=%s prompt=%r",
        job_id[:12],
        job.get("kind"),
        job.get("prompt", "")[:80],
    )
    stop = asyncio.Event()
    hb = asyncio.ensure_future(_heartbeat_loop(client, job_id, stop))
    try:
        result = await process_job(job, client)
        await client.complete(job_id, result["output_url"], result.get("media_id"))
        logger.info("job %s completed: %s", job_id[:12], result.get("output_url", "")[:80])
    except Exception as e:
        logger.exception("job %s failed", job_id[:12])
        try:
            await client.fail(job_id, f"{type(e).__name__}: {e}")
        except Exception:
            logger.warning("could not report failure for %s", job_id[:12])
    finally:
        stop.set()
        await hb


async def run_worker(
    api_base: str, provider: str, worker_id: str, lease_ttl_s: float, once: bool = False
) -> None:
    async with ProviderJobClient(api_base, worker_id, lease_ttl_s) as client:
        logger.info(
            "worker %s listening for provider=%s at %s", worker_id, provider, api_base
        )
        while True:
            job = await client.wait_next(provider, timeout_s=60)
            if job is None:
                if once:
                    logger.info("no job available, exiting (--once)")
                    return
                continue
            await _handle_one(client, job)
            if once:
                return


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Worker for FlowKit provider jobs via Flow MCP")
    p.add_argument(
        "--api",
        default="http://localhost:8100/api",
        help="FlowKit API base (default: http://localhost:8100/api)",
    )
    p.add_argument(
        "--provider",
        default="assistant",
        help="provider queue to consume (default: assistant)",
    )
    p.add_argument(
        "--worker-id",
        default="worker-1",
        help="unique id for this worker (used for lease ownership)",
    )
    p.add_argument(
        "--lease-ttl",
        type=float,
        default=300,
        help="lease seconds per heartbeat (default: 300)",
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="process a single job (or none) then exit",
    )
    args = p.parse_args(argv)
    try:
        asyncio.run(
            run_worker(args.api, args.provider, args.worker_id, args.lease_ttl, args.once)
        )
    except KeyboardInterrupt:
        logger.info("interrupted, exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
