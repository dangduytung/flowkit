"""Shop-logo removal rules (``config/watermark_rules.json``), matched by product URL.

A rule's ``delogo`` is either a ``"x=..:y=..:w=..:h=.."`` string measured on a
``ref_width`` x ``ref_height`` frame, or a dict with absolute ``x/y/w/h`` or a
``ratio`` list of fractions. Boxes are rescaled to the actual video size.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from tools.common.ffmpeg import probe_dimensions

logger = logging.getLogger(__name__)

RULES_PATH_ENV = "WATERMARK_RULES_PATH"
RULES_RELATIVE_PATH = Path("config") / "watermark_rules.json"
# Scraped shop videos are square 720p unless a rule says otherwise.
DEFAULT_REFERENCE_SIZE = (720, 720)
_REPO_SEARCH_DEPTH = 4
_BOX_KEYS = ("x", "y", "w", "h")


def get_watermark_rules_path() -> Path:
    """``$WATERMARK_RULES_PATH``, else ``config/watermark_rules.json`` at the repo root."""
    env_path = os.getenv(RULES_PATH_ENV)
    if env_path:
        return Path(env_path)
    current = Path(__file__).resolve().parent
    for _ in range(_REPO_SEARCH_DEPTH):
        candidate = current / RULES_RELATIVE_PATH
        if candidate.exists() or (current / ".git").exists():
            return candidate
        current = current.parent
    return RULES_RELATIVE_PATH


def load_watermark_rules() -> list[dict[str, Any]]:
    """All rules, or an empty list when the file is missing or malformed."""
    path = get_watermark_rules_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Không thể đọc file cấu hình watermark %s: %s", path, exc)
        return []
    return data if isinstance(data, list) else []


def _normalize_product_url(url: Optional[str]) -> str:
    """Host (without www) + path, lower-cased, without scheme, query or trailing slash."""
    if not url:
        return ""
    parsed = urlparse(url.strip() if "://" in url else f"//{url.strip()}")
    host = parsed.netloc.lower().removeprefix("www.")
    return f"{host}{parsed.path.rstrip('/')}"


def _urls_match(rule_url: str, target_url: str) -> bool:
    """Equal, or one is a path-prefix of the other on a ``/`` boundary.

    Plain substring matching let ``.../product/1`` match ``.../product/12345``.
    """
    if not rule_url or not target_url:
        return False
    shorter, longer = sorted((rule_url, target_url), key=len)
    return longer == shorter or longer.startswith(shorter + "/")


def _get_video_dimensions(video_path: Path) -> tuple[int, int]:
    """(width, height), or the reference size when the video cannot be probed."""
    try:
        return probe_dimensions(video_path)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return DEFAULT_REFERENCE_SIZE


def _parse_box(spec: str) -> dict[str, float]:
    box = {}
    for part in spec.split(":"):
        key, sep, value = part.partition("=")
        if sep:
            try:
                box[key.strip()] = float(value)
            except ValueError:
                continue
    return box


def _format_box(x: float, y: float, w: float, h: float) -> str:
    return f"x={int(x)}:y={int(y)}:w={int(w)}:h={int(h)}"


def _find_rule(product_url: str) -> Optional[dict[str, Any]]:
    target = _normalize_product_url(product_url)
    return next((r for r in load_watermark_rules() if _urls_match(_normalize_product_url(r.get("product_url", "")), target)), None)


def resolve_delogo_for_product(
    product_url: Optional[str],
    video_path: Optional[Path] = None,
) -> tuple[Optional[str], Optional[str]]:
    """``(delogo_spec, rule_name)`` for the product, scaled to ``video_path``; ``(None, None)`` if no rule."""
    if not product_url or not _normalize_product_url(product_url):
        return None, None
    rule = _find_rule(product_url)
    if rule is None:
        return None, None

    name = rule.get("name", "Quy tắc không tên")
    raw = rule.get("delogo")
    has_video = bool(video_path and Path(video_path).exists())

    if isinstance(raw, str):
        box = _parse_box(raw)
        if has_video and all(k in box for k in _BOX_KEYS):
            vw, vh = _get_video_dimensions(video_path)
            ref_w = rule.get("ref_width", DEFAULT_REFERENCE_SIZE[0])
            ref_h = rule.get("ref_height", DEFAULT_REFERENCE_SIZE[1])
            if (vw, vh) != (ref_w, ref_h) and ref_w > 0 and ref_h > 0:
                sx, sy = vw / ref_w, vh / ref_h
                return _format_box(box["x"] * sx, box["y"] * sy, box["w"] * sx, box["h"] * sy), name
        return raw, name

    if isinstance(raw, dict):
        vw, vh = _get_video_dimensions(video_path) if has_video else DEFAULT_REFERENCE_SIZE
        if "ratio" in raw:
            rx, ry, rw, rh = raw["ratio"]
            return _format_box(rx * vw, ry * vh, rw * vw, rh * vh), name
        if all(k in raw for k in _BOX_KEYS):
            return _format_box(*(raw[k] for k in _BOX_KEYS)), name

    return None, name


__all__ = ["get_watermark_rules_path", "load_watermark_rules", "resolve_delogo_for_product"]
