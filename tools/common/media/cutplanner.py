"""Choose where each scene starts inside the shop's source video.

Planning is a pure function of the detected shot cuts so it can be tested without
ffmpeg; ``calculate_smart_subclip_starts`` wires detection and planning together.

Guarantees of ``plan_subclip_starts``:
- the first scene starts at 0 and starts are strictly increasing;
- consecutive slices never overlap (scene *i* owns ``[start_i, start_{i+1})``);
- when the narration fits in the video, every slice is at least as long as its scene.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional, Sequence

from tools.common.ffmpeg import run_ffmpeg

logger = logging.getLogger(__name__)

# ffmpeg scene-change score above which a frame counts as a shot cut.
SCENE_CHANGE_THRESHOLD = 0.25
# Cuts closer together than this are one transition (flash frames, dissolves).
MIN_CUT_SPACING_SECONDS = 0.3
# How far past the ideal start we may slide to land on a real shot cut.
SNAP_WINDOW_SECONDS = 1.2
# Shortest slice handed to a scene when the video is shorter than the narration.
MIN_SLICE_SECONDS = 1.0

_PTS_TIME = re.compile(r"pts_time:([0-9.]+)")


def detect_scene_cuts(video_path: Path, total_dur: float) -> list[float]:
    """Shot-change timestamps, bracketed by 0 and ``total_dur``. Never raises."""
    cuts = [0.0]
    try:
        result = run_ffmpeg(
            ["-i", str(video_path), "-vf", rf"select=gt(scene\,{SCENE_CHANGE_THRESHOLD}),metadata=print", "-f", "null", "-"],
            check=False,
        )
        for match in _PTS_TIME.finditer(result.stderr or ""):
            t = float(match.group(1))
            if t > cuts[-1] + MIN_CUT_SPACING_SECONDS and t < total_dur:
                cuts.append(t)
    except OSError as exc:
        logger.warning("Scene detection failed for %s: %s", video_path, exc)
    cuts.append(total_dur)
    return cuts


def _nearest(candidates: Sequence[float], target: float) -> Optional[float]:
    return min(candidates, key=lambda c: abs(c - target)) if candidates else None


def _plan_sequential(cuts: Sequence[float], total_dur: float, durations: Sequence[float]) -> list[float]:
    """Narration fits: lay scenes end to end, nudging each start forward onto a shot cut
    while leaving enough room for every scene that follows."""
    starts = [0.0]
    cursor = durations[0]
    for i in range(1, len(durations)):
        latest = total_dur - sum(durations[i:])
        window = [c for c in cuts if cursor <= c <= min(cursor + SNAP_WINDOW_SECONDS, latest)]
        start = window[0] if window else cursor
        starts.append(start)
        cursor = start + durations[i]
    return starts


def _plan_proportional(
    cuts: Sequence[float], total_dur: float, num_scenes: int, durations: Optional[Sequence[float]]
) -> list[float]:
    """Narration is longer than the video: split the video in proportion to each scene's
    length, snapping to nearby cuts, with every slice at least ``min_slice`` long."""
    weights = list(durations) if durations else [1.0] * num_scenes
    total_weight = sum(weights) or float(num_scenes)
    min_slice = min(MIN_SLICE_SECONDS, total_dur / num_scenes)

    starts = [0.0]
    elapsed = 0.0
    for i in range(1, num_scenes):
        elapsed += weights[i - 1]
        target = total_dur * elapsed / total_weight
        lo = starts[-1] + min_slice
        hi = total_dur - (num_scenes - i) * min_slice  # leave room for the remaining scenes
        near = [c for c in cuts if max(lo, target - SNAP_WINDOW_SECONDS) <= c <= min(hi, target + SNAP_WINDOW_SECONDS)]
        snapped = _nearest(near, target)
        starts.append(snapped if snapped is not None else min(hi, max(lo, target)))
    return starts


def plan_subclip_starts(
    cuts: Sequence[float],
    total_dur: float,
    num_scenes: int,
    scene_durations: Optional[Sequence[float]] = None,
) -> list[float]:
    """Start time of each scene's slice (see module docstring for guarantees)."""
    if num_scenes <= 0:
        return []
    if total_dur <= 0:
        return [0.0] * num_scenes
    if num_scenes == 1:
        return [0.0]

    cuts = sorted(c for c in cuts if 0.0 <= c <= total_dur)
    durations = list(scene_durations) if scene_durations and len(scene_durations) == num_scenes else None
    if durations and sum(durations) <= total_dur:
        starts = _plan_sequential(cuts, total_dur, durations)
    else:
        starts = _plan_proportional(cuts, total_dur, num_scenes, durations)
    return [round(s, 2) for s in starts]


def calculate_smart_subclip_starts(
    video_path: Path,
    num_scenes: int,
    total_dur: float,
    scene_durations: Optional[Sequence[float]] = None,
) -> tuple[list[float], list[tuple[float, float]]]:
    """Detect shot cuts in ``video_path`` and plan scene starts.

    Returns ``(starts, glitch_intervals)``. Glitch detection is not implemented, so the
    second item is always empty; it is kept for callers that pass it through to
    ``extract_vertical_subclip``.
    """
    if num_scenes <= 1 or total_dur <= 0:
        return plan_subclip_starts([], total_dur, num_scenes, scene_durations), []
    cuts = detect_scene_cuts(video_path, total_dur)
    return plan_subclip_starts(cuts, total_dur, num_scenes, scene_durations), []


__all__ = [
    "calculate_smart_subclip_starts",
    "detect_scene_cuts",
    "plan_subclip_starts",
]
