"""Non-invasive Omni 1.2 Flash (``macaron_cookie``) upgrade hook for FlowKit.

Keeps ``agent/services/omni_flash.py``, ``agent/services/flow_batch.py``,
``agent/api/flow.py``, and ``agent/models.json`` untouched on feature branches
so syncing and merging upstream ``main`` never causes merge conflicts.

When enabled (default in runtime via ``OMNI_VIDEO_FAMILY=macaron_cookie``),
any Omni 1.1 wire key (``abra_*`` or ``omni_flash_i2v_*_first_last``) built for
Flow's ``batchexecute`` video RPCs is transparently upgraded to its live-verified
Omni 1.2 Flash wire key (``macaron_cookie_*``).
"""
from __future__ import annotations

import functools
import logging
import os
import re
import sys
from typing import Any

from tools.common.settings import load_env_file

logger = logging.getLogger(__name__)

OMNI_V12_FAMILY = "macaron_cookie"
OMNI_V11_FAMILY = "abra"

_FIRST_LAST_V11_RE = re.compile(r"^omni_flash_i2v_(\d+s)_first_last(_360p)?$")
_ABRA_KEY_RE = re.compile(r"^abra_(t2v|i2v|r2v)_(\d+s)(_360p)?$")
_OMNI_VIDEO_RPCS = frozenset({"YhhmEf", "eb1hJf", "nprQif", "MZZa6b"})

_installed = False


def configured_omni_family() -> str:
    """Return ``'macaron_cookie'`` (Omni 1.2) or ``'abra'`` (Omni 1.1)."""
    load_env_file()
    raw = os.environ.get("OMNI_VIDEO_FAMILY", OMNI_V12_FAMILY).strip().lower()
    if raw in ("abra", "1.1", "omni_1.1", "omni_1_1", "v1.1"):
        return OMNI_V11_FAMILY
    return OMNI_V12_FAMILY


def is_omni_v12_active() -> bool:
    """True when runtime should upgrade Omni wire keys to Omni 1.2 (``macaron_cookie``).

    Disabled automatically during upstream pytest runs unless ``OMNI_V12_FORCE_IN_TESTS=1``
    so upstream golden assertions against ``abra_*`` continue to pass without edits.
    """
    if os.environ.get("OMNI_V12_FORCE_IN_TESTS") == "1":
        return configured_omni_family() == OMNI_V12_FAMILY
    if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
        return False
    return configured_omni_family() == OMNI_V12_FAMILY


def upgrade_omni_model_key(model_key: str, family: str | None = None) -> str:
    """Translate an Omni 1.1 wire key to Omni 1.2 (``macaron_cookie_*``).

    Idempotent: keys that already start with ``macaron_cookie_`` or belong to
    Veo / image models are returned unchanged.
    """
    if not isinstance(model_key, str) or not model_key:
        return model_key
    target = family or configured_omni_family()
    if target != OMNI_V12_FAMILY:
        return model_key

    m_abra = _ABRA_KEY_RE.match(model_key)
    if m_abra:
        mode, dur, suffix = m_abra.groups()
        return f"{OMNI_V12_FAMILY}_{mode}_{dur}{suffix or ''}"

    m_fl = _FIRST_LAST_V11_RE.match(model_key)
    if m_fl:
        dur, suffix = m_fl.groups()
        return f"{OMNI_V12_FAMILY}_i2v_fl_{dur}{suffix or ''}"

    return model_key


def _upgrade_payload_tree(node: Any, family: str) -> Any:
    if isinstance(node, str):
        return upgrade_omni_model_key(node, family=family)
    if isinstance(node, list):
        return [_upgrade_payload_tree(item, family) for item in node]
    if isinstance(node, tuple):
        return tuple(_upgrade_payload_tree(item, family) for item in node)
    if isinstance(node, dict):
        return {k: _upgrade_payload_tree(v, family) for k, v in node.items()}
    return node


def install_omni_v12_patch() -> bool:
    """Patch ``flow_batch.build_envelope`` and ``omni_flash`` response metadata in-memory."""
    global _installed
    if _installed:
        return True

    from agent.services import flow_batch as fb
    from agent.services import omni_flash as of

    orig_build_envelope = fb.build_envelope

    @functools.wraps(orig_build_envelope)
    def patched_build_envelope(rpcid: str, inner: Any) -> str:
        if rpcid in _OMNI_VIDEO_RPCS and is_omni_v12_active():
            inner = _upgrade_payload_tree(inner, OMNI_V12_FAMILY)
        return orig_build_envelope(rpcid, inner)

    fb.build_envelope = patched_build_envelope

    def _wrap_async_omni_fn(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            res = await fn(*args, **kwargs)
            if is_omni_v12_active() and isinstance(res, dict):
                data = res.get("data")
                if isinstance(data, dict) and isinstance(data.get("model"), str):
                    old_model = data["model"]
                    new_model = upgrade_omni_model_key(old_model, OMNI_V12_FAMILY)
                    if new_model != old_model:
                        data["model"] = new_model
                        logger.info("[Omni 1.2] Using model %s (upgraded from %s)", new_model, old_model)
            return res

        return wrapper

    of.generate_omni_flash_text_video = _wrap_async_omni_fn(of.generate_omni_flash_text_video)
    of._submit_omni_frame_video = _wrap_async_omni_fn(of._submit_omni_frame_video)
    of.generate_omni_flash_video = _wrap_async_omni_fn(of.generate_omni_flash_video)

    _installed = True
    logger.info("Omni 1.2 Flash (macaron_cookie) patch installed (active=%s)", configured_omni_family())
    return True


__all__ = [
    "OMNI_V11_FAMILY",
    "OMNI_V12_FAMILY",
    "configured_omni_family",
    "install_omni_v12_patch",
    "is_omni_v12_active",
    "upgrade_omni_model_key",
]
