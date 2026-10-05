"""Configuration settings for Shopee Ad Production."""
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Base directories
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ENV_FILE = REPO_ROOT / ".env"

def _load_env_file(path: Path):
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val

_load_env_file(DEFAULT_ENV_FILE)

# OmniVoice Settings
OMNIVOICE_URL = os.environ.get("OMNIVOICE_URL", "").strip()
OMNIVOICE_API_KEY = os.environ.get("OMNIVOICE_API_KEY", "").strip()
OMNIVOICE_PROFILE_ID = os.environ.get("OMNIVOICE_PROFILE_ID", "").strip()
OMNIVOICE_SPEED = float(os.environ.get("OMNIVOICE_SPEED", "1.03"))

# FlowKit API
FLOWKIT_API_URL = os.environ.get("FLOWKIT_API_URL", "http://127.0.0.1:8100")

# Input & Output Paths
_shopee_dir_env = os.environ.get("SHOPEE_DOWNLOADS_DIR", "").strip()
if _shopee_dir_env:
    SHOPEE_DOWNLOADS_DIR = Path(_shopee_dir_env)
else:
    _default_dl = Path.home() / "Downloads" / "Shopee Downloads"
    SHOPEE_DOWNLOADS_DIR = _default_dl if _default_dl.exists() else None
OUTPUT_ROOT = REPO_ROOT / "output" / "shopee_ads"

# Channel Branding (Optional - empty by default for 100% white-label multi-channel distribution)
DEFAULT_CHANNEL_NAME = os.environ.get("SHOPEE_AD_CHANNEL_NAME", "").strip()
DEFAULT_CHANNEL_HANDLE = os.environ.get("SHOPEE_AD_CHANNEL_HANDLE", "").strip()
DEFAULT_CHANNEL_BIO_LINK = os.environ.get("SHOPEE_AD_BIO_LINK", "").strip()


def list_available_zips(directory: Optional[Path] = None) -> list:
    """List all available Shopee zip files from SHOPEE_DOWNLOADS_DIR sorted by newest first."""
    target = directory or SHOPEE_DOWNLOADS_DIR
    if not target or not target.exists():
        return []
    return sorted(list(target.glob("*.zip")), key=lambda p: p.stat().st_mtime, reverse=True)
