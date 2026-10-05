import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from urllib.parse import urlparse

import os

logger = logging.getLogger(__name__)


def get_watermark_rules_path() -> Path:
    """Return the absolute path to config/watermark_rules.json, configurable via env."""
    env_path = os.getenv("WATERMARK_RULES_PATH")
    if env_path:
        return Path(env_path)

    # Try traversing upwards from this file's location to the repo root
    current = Path(__file__).resolve().parent
    for _ in range(4):
        candidate = current / "config" / "watermark_rules.json"
        if candidate.exists():
            return candidate
        if (current / ".git").exists():
            return current / "config" / "watermark_rules.json"
        current = current.parent
    return Path("config/watermark_rules.json")


def load_watermark_rules() -> List[Dict[str, Any]]:
    """Load list of watermark rules from config/watermark_rules.json."""
    path = get_watermark_rules_path()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning(f"Không thể đọc file cấu hình watermark {path}: {e}")
        return []


def _normalize_product_url(url: str) -> str:
    """Strip protocol, query parameters, and trailing slashes for stable matching."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        netloc = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.rstrip("/")
        return f"{netloc}{path}"
    except Exception:
        clean = url.split("?")[0].strip().rstrip("/").lower()
        clean = re.sub(r"^https?://(?:www\.)?", "", clean)
        return clean


def _get_video_dimensions(video_path: Path) -> Tuple[int, int]:
    """Retrieve (width, height) of video using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0",
            str(video_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        w, h = [int(x) for x in res.stdout.strip().split(",")]
        return w, h
    except Exception:
        return 720, 720


def resolve_delogo_for_product(
    product_url: str,
    video_path: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Look up watermark rules in config/watermark_rules.json matching the product_url.
    Returns (delogo_filter_string, rule_name) or (None, None).
    Automatically adapts coordinates if video resolution differs from standard reference (720x720).
    """
    if not product_url:
        return None, None

    norm_target = _normalize_product_url(product_url)
    if not norm_target:
        return None, None

    rules = load_watermark_rules()
    matched_rule = None
    for r in rules:
        rule_url = r.get("product_url", "")
        norm_rule = _normalize_product_url(rule_url)
        if norm_rule and (norm_rule == norm_target or norm_rule in norm_target or norm_target in norm_rule):
            matched_rule = r
            break

    if not matched_rule:
        return None, None

    rule_name = matched_rule.get("name", "Quy tắc không tên")
    raw_delogo = matched_rule.get("delogo")
    if not raw_delogo:
        return None, rule_name

    # If delogo is specified as a direct string like "x=30:y=545:w=140:h=60"
    if isinstance(raw_delogo, str):
        # Check if resolution scaling is required
        coords = {}
        for part in raw_delogo.split(":"):
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    coords[k.strip()] = float(v.strip())
                except ValueError:
                    pass

        if video_path and video_path.exists() and len(coords) == 4 and all(k in coords for k in ["x", "y", "w", "h"]):
            vw, vh = _get_video_dimensions(video_path)
            ref_w = matched_rule.get("ref_width", 720)
            ref_h = matched_rule.get("ref_height", 720)
            if (vw != ref_w or vh != ref_h) and ref_w > 0 and ref_h > 0:
                sx = vw / ref_w
                sy = vh / ref_h
                scaled_x = int(coords["x"] * sx)
                scaled_y = int(coords["y"] * sy)
                scaled_w = int(coords["w"] * sx)
                scaled_h = int(coords["h"] * sy)
                return f"x={scaled_x}:y={scaled_y}:w={scaled_w}:h={scaled_h}", rule_name

        return raw_delogo, rule_name

    # If delogo is specified as a dictionary
    if isinstance(raw_delogo, dict):
        vw, vh = _get_video_dimensions(video_path) if (video_path and video_path.exists()) else (720, 720)
        if "ratio" in raw_delogo:
            # [x_ratio, y_ratio, w_ratio, h_ratio]
            rx, ry, rw, rh = raw_delogo["ratio"]
            return f"x={int(rx*vw)}:y={int(ry*vh)}:w={int(rw*vw)}:h={int(rh*vh)}", rule_name
        if all(k in raw_delogo for k in ["x", "y", "w", "h"]):
            return f"x={int(raw_delogo['x'])}:y={int(raw_delogo['y'])}:w={int(raw_delogo['w'])}:h={int(raw_delogo['h'])}", rule_name

    return None, rule_name
