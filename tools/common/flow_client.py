"""Client for the local FlowKit API (``:8100``) as used by the ad pipelines."""
from __future__ import annotations

import base64
import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, TypedDict

from tools.common.ffmpeg import run_ffmpeg
from tools.common.settings import service_settings

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_S = 30
HEALTH_TIMEOUT_S = 3
STATUS_SUCCESS = "MEDIA_GENERATION_STATUS_SUCCESSFUL"
STATUS_FAILED = "MEDIA_GENERATION_STATUS_FAILED"


class FlowJob(TypedDict, total=False):
    """A submitted video generation, tracked per scene.

    ``type == "workflow"``: Omni text/ref-to-video, matched by ``primary_media_id``.
    ``type == "operation"``: Veo-style operation, matched by ``op_name``.
    """

    scene_id: int
    type: str
    workflow: dict
    primary_media_id: Optional[str]
    op_name: str
    project_id: str


class FlowGenerationError(RuntimeError):
    pass


@dataclass
class PollResult:
    urls: dict[int, str] = field(default_factory=dict)
    failed: dict[int, str] = field(default_factory=dict)
    timed_out: list[int] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed and not self.timed_out

    def raise_for_failures(self) -> None:
        """Raise one error naming every failed / timed-out scene (rerun them with --scene)."""
        if self.ok:
            return
        parts = [f"scene {sid}: {msg}" for sid, msg in sorted(self.failed.items())]
        if self.timed_out:
            parts.append(f"timed out: scenes {sorted(self.timed_out)}")
        raise FlowGenerationError("Google Flow video generation incomplete — " + "; ".join(parts))


class FlowKitClient:
    def __init__(self, base_url: Optional[str] = None, timeout_s: int = REQUEST_TIMEOUT_S):
        self.base_url = (base_url or service_settings().flowkit_api_url).rstrip("/")
        self.timeout_s = timeout_s

    # ------------------------------------------------------------------ transport

    def request(self, path: str, method: str = "GET", data: Optional[dict] = None, timeout_s: Optional[int] = None) -> Any:
        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(
            f"{self.base_url}{path}", data=body, headers={"Content-Type": "application/json"}, method=method
        )
        with urllib.request.urlopen(req, timeout=timeout_s or self.timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def post(self, path: str, data: dict) -> Any:
        return self.request(path, method="POST", data=data)

    # ------------------------------------------------------------------ endpoints

    def is_ready(self) -> bool:
        """Server up and the Chrome extension connected."""
        try:
            health = self.request("/health", timeout_s=HEALTH_TIMEOUT_S)
        except (urllib.error.URLError, OSError, ValueError):
            return False
        return health.get("status") == "ok" and health.get("extension_connected") is True

    def create_project(self, name: str, story: str, material: str = "realistic", language: str = "vi") -> str:
        """Create a FlowKit project (the server pins it to FLOW_PROJECT_ID) and return its id."""
        res = self.post("/api/projects", {"name": name, "story": story, "material": material, "language": language})
        logger.info("FlowKit project ready: %s ('%s')", res["id"], res.get("name"))
        return res["id"]

    def upload_image(self, image_path: Path, project_id: str = "") -> str:
        """Upload a local image; returns its media_id (UUID)."""
        payload = {
            "image_base64": base64.b64encode(Path(image_path).read_bytes()).decode("ascii"),
            "file_name": Path(image_path).name,
            "project_id": project_id,
        }
        res = self.post("/api/flow/upload-image", payload)
        media_id = res.get("media_id")
        if not media_id:
            raise FlowGenerationError(f"Upload ảnh thất bại, không nhận được media_id: {res}")
        return media_id

    def submit_text_video(self, payload: dict) -> dict:
        return self.post("/api/flow/generate-video-omni-text", payload)

    def submit_reference_video(self, payload: dict) -> dict:
        return self.post("/api/flow/generate-video-omni", payload)

    # ------------------------------------------------------------------ polling

    def _poll_workflows(self, jobs: Sequence[FlowJob], pending: dict[int, FlowJob], result: PollResult) -> None:
        project_id = jobs[0]["workflow"].get("project_id") or ""
        res = self.post("/api/flow/check-omni-status", {"workflows": [j["workflow"] for j in jobs], "project_id": project_id})
        by_media = {j.get("primary_media_id"): j["scene_id"] for j in jobs}
        for wf in res.get("workflows", []):
            sid = by_media.get(wf.get("primary_media_id"))
            if sid not in pending:
                continue
            url = (wf.get("media") or {}).get("url")
            if wf.get("done") is True and url:
                result.urls[sid] = url
                del pending[sid]
                logger.info("🎉 Scene %s (Text-to-Video) hoàn thành!", sid)
            elif wf.get("status") == STATUS_FAILED or wf.get("error"):
                result.failed[sid] = str(wf.get("error") or "generation failed")
                del pending[sid]

    def _poll_operations(self, jobs: Sequence[FlowJob], pending: dict[int, FlowJob], result: PollResult) -> None:
        res = self.post(
            "/api/flow/check-status",
            {"operations": [{"name": j["op_name"]} for j in jobs], "project_id": jobs[0]["project_id"]},
        )
        by_op = {j["op_name"]: j["scene_id"] for j in jobs}
        for op in res.get("operations", []):
            data = op.get("operation") or {}
            sid = by_op.get(data.get("name") or op.get("name"))
            if sid not in pending:
                continue
            if op.get("status") == STATUS_SUCCESS:
                video = data.get("metadata", {}).get("video", {})
                url = video.get("fifeUrl") or video.get("url")
                if url:
                    result.urls[sid] = url
                    del pending[sid]
                    logger.info("🎉 Scene %s (Consistent Ref-to-Video) hoàn thành!", sid)
            elif op.get("status") == STATUS_FAILED:
                result.failed[sid] = str(op.get("error") or "Unknown generation error")
                del pending[sid]

    def poll_jobs(
        self,
        jobs: Sequence[FlowJob],
        poll_interval_s: float = 5,
        timeout_s: float = 600,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> PollResult:
        """Poll until every job succeeded, failed or ``timeout_s`` elapsed.

        Never raises for a generation failure: inspect the result (or call
        ``raise_for_failures``) so finished scenes can still be downloaded first.
        Transient HTTP errors are logged and retried on the next tick.
        """
        result = PollResult()
        pending = {j["scene_id"]: j for j in jobs}
        deadline = clock() + timeout_s
        while pending and clock() < deadline:
            for kind, poll in (("workflow", self._poll_workflows), ("operation", self._poll_operations)):
                batch = [j for j in pending.values() if j.get("type") == kind]
                if not batch:
                    continue
                try:
                    poll(batch, pending, result)
                except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
                    logger.warning("Lỗi kiểm tra tiến độ %s: %s", kind, exc)
            if pending:
                sleep(poll_interval_s)
        for sid, msg in result.failed.items():
            logger.error("Scene %s thất bại: %s", sid, msg)
        result.timed_out = sorted(pending)
        return result


def download(url: str, destination: Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)
    return destination


def extract_frame(video_path: Path, output_image: Path, time_sec: float = 1.2) -> Path:
    """Save one frame (e.g. a character anchor portrait) as an image."""
    output_image = Path(output_image)
    output_image.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(["-ss", str(time_sec), "-i", str(video_path), "-frames:v", "1", "-update", "1", str(output_image)])
    return output_image


__all__ = [
    "FlowGenerationError",
    "FlowJob",
    "FlowKitClient",
    "PollResult",
    "download",
    "extract_frame",
]
