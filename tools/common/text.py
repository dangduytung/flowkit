"""Text helpers owned by the ad pipelines (kept here so tools/ never imports agent/)."""
from __future__ import annotations

import re
import unicodedata

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_REPEATED_UNDERSCORE = re.compile(r"_+")


def slugify(text: str) -> str:
    """ASCII, lower-case, ``_``-separated directory name ("Đồ Đẹp 100%" -> "do_dep_100").

    Same output as ``agent.utils.slugify`` so existing product folders keep their names.
    """
    # Vietnamese Đ/đ has no NFKD decomposition.
    text = text.replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    return _REPEATED_UNDERSCORE.sub("_", _NON_ALNUM.sub("_", text)).strip("_")


__all__ = ["slugify"]
