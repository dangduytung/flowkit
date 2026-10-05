"""Shared data models for advertising pipelines."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SceneDefinition:
    id: int
    name: str
    kind: str  # "FLOW_AI", "PRODUCT_PHOTO", "REAL_FOOTAGE", or "IMAGE_SLIDE"
    narrator_text: str
    overlay_title: str
    overlay_subtitle: str
    real_start_sec: float = 0.0
    image_index: int = 0
    prompt: Optional[str] = None
    video_prompt: Optional[str] = None
