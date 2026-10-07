"""Output-file naming shared by every pipeline."""
from typing import Optional


def build_variant_suffix(
    style: str = "flow_cinematic",
    no_overlay: bool = False,
    cta_mode: str = "none",
    default_cta: str = "none",
    tag: Optional[str] = None,
) -> str:
    """
    Build a descriptive, collision-free variant suffix for multi-style ad exports.
    Example output: 'flow_cinematic_clean_cta-shopee_v2'
    """
    parts = [style]
    if no_overlay:
        parts.append("clean")
    if cta_mode and cta_mode != default_cta and cta_mode != "none":
        parts.append(f"cta-{cta_mode}")
    elif cta_mode == "none" and default_cta != "none":
        parts.append("no-cta")
    if tag:
        clean_tag = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in tag
        ).strip("-_")
        if clean_tag:
            parts.append(clean_tag)
    return "_".join(parts)
