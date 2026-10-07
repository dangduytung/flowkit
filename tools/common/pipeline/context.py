"""Inputs shared by the local and Flow pipelines: run options, platform hooks, workspace."""
from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Sequence, Union

from tools.common.media.extractor import ExtractedAssets, extract_zip
from tools.common.models import SceneDefinition
from tools.common.naming import build_variant_suffix
from tools.common.pipeline.selection import SceneSelection
from tools.common.product import ProductInfo, parse_product_zip
from tools.common.settings import PlatformProfile

logger = logging.getLogger(__name__)


@dataclass
class RunOptions:
    """One pipeline run, as requested on the command line."""

    zip_path: Optional[Path] = None
    style: Optional[str] = None  # None -> profile.default_style
    cta_mode: Optional[str] = None  # None -> profile.default_cta
    speed: Optional[float] = None
    voice_profile_id: Optional[str] = None
    crop_mode: str = "blur_bg"
    channel_name: Optional[str] = None
    channel_handle: Optional[str] = None
    custom_idea: Optional[str] = None
    force_storyboard: bool = False
    regen: bool = False
    no_voice: bool = False
    no_overlay: bool = False
    tag: Optional[str] = None
    delogo: Optional[str] = "auto"
    bgm: Optional[Union[str, Path]] = None
    target_scenes: Optional[Sequence[int]] = None

    def resolved(self, profile: PlatformProfile) -> "RunOptions":
        """Fill platform defaults so downstream code never sees None for them."""
        return RunOptions(**{
            **self.__dict__,
            "style": self.style or profile.default_style,
            "cta_mode": self.cta_mode or profile.default_cta,
            "channel_name": self.channel_name or profile.channel_name,
            "channel_handle": self.channel_handle or profile.channel_handle,
        })

    @property
    def selection(self) -> SceneSelection:
        return SceneSelection.from_ids(self.target_scenes)


@dataclass(frozen=True)
class PlatformHooks:
    """Platform-specific content plugged into the shared pipelines.

    Each callable keeps the signature of the platform module it comes from.
    """

    load_storyboard: Callable[..., list[SceneDefinition]]
    generate_storyboard: Callable[..., list[SceneDefinition]]
    write_captions: Callable[..., dict[str, Path]]
    create_cover: Callable[..., Path]
    write_publish_guide: Callable[..., Path]
    export_script: Callable[..., Path]


@dataclass
class ProductWorkspace:
    """Folder layout of one product under the platform's output root."""

    product: ProductInfo
    root: Path
    variant: str
    assets: ExtractedAssets = field(default_factory=ExtractedAssets)

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    @property
    def audio_dir(self) -> Path:
        return self.root / "audio"

    @property
    def clips_dir(self) -> Path:
        return self.root / "clips"

    @property
    def scenes_dir(self) -> Path:
        return self.root / "scenes"

    @property
    def final_dir(self) -> Path:
        return self.root / "final"

    def storyboard_path(self, style: str) -> Path:
        return self.root / f"storyboard_{style}.json"

    def final_video(self, method: str, silent: bool) -> Path:
        return self.final_dir / f"{self.product.slug}_{method}_{self.variant}{'_silent' if silent else ''}.mp4"

    def final_file(self, suffix: str) -> Path:
        return self.final_dir / f"{self.product.slug}_{self.variant}_{suffix}"

    def create_dirs(self) -> None:
        for directory in (self.root, self.assets_dir, self.audio_dir, self.clips_dir, self.scenes_dir, self.final_dir):
            directory.mkdir(parents=True, exist_ok=True)


def resolve_zip(profile: PlatformProfile, zip_path: Optional[Path]) -> Path:
    """The requested zip, or the newest one in the platform's downloads folder."""
    if zip_path is not None:
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file zip tại: {zip_path}")
        return zip_path
    directory = profile.downloads_dir
    if not directory or not directory.exists():
        raise RuntimeError(
            f"Chưa cấu hình {profile.env_prefix}_DOWNLOADS_DIR hợp lệ trong .env! (Hiện tại: '{directory}')"
        )
    available = profile.list_zips()
    if not available:
        raise RuntimeError(f"Không tìm thấy file zip nào trong thư mục: {directory}")
    logger.info("[Orchestrator] Quét thư mục %s (%s)", profile.display_name, directory)
    logger.info("[Orchestrator] Tự động chọn file zip mới nhất: %s", available[0].name)
    return available[0]


def open_workspace(profile: PlatformProfile, opts: RunOptions) -> ProductWorkspace:
    """Parse the zip, create the product folders, archive the zip and unpack its assets."""
    zip_path = resolve_zip(profile, opts.zip_path)
    product = parse_product_zip(zip_path)
    variant = build_variant_suffix(
        style=opts.style, no_overlay=opts.no_overlay, cta_mode=opts.cta_mode, default_cta=profile.naming_baseline_cta, tag=opts.tag
    )
    workspace = ProductWorkspace(product=product, root=profile.output_root / product.slug, variant=variant)
    workspace.create_dirs()

    archived = workspace.root / zip_path.name
    if not archived.exists():
        shutil.copy2(zip_path, archived)
        logger.info("📥 [Lưu trữ] Đã copy file zip vào thư mục sản phẩm: %s", archived.name)
    workspace.assets = extract_zip(zip_path, workspace.assets_dir)
    return workspace


def print_banner(title: str, workspace: ProductWorkspace, selection: SceneSelection) -> None:
    product = workspace.product
    logger.info("%s", "\n" + "=" * 65)
    logger.info("🚀 %s", title)
    logger.info("📦 Sản phẩm: %s", product.name)
    if product.price:
        logger.info("💰 Giá bán: %s", product.price)
    if product.sold_count:
        logger.info("🔥 Đã bán: %s | Đánh giá: %s sao", product.sold_count, product.rating)
    logger.info("📁 Slug thư mục: %s", product.slug)
    if selection.is_partial:
        logger.info("🎯 Chế độ tái tạo phân cảnh chọn lọc: Scenes %s", sorted(selection.target_ids))
    logger.info("%s", "=" * 65 + "\n")


__all__ = [
    "PlatformHooks",
    "ProductWorkspace",
    "RunOptions",
    "open_workspace",
    "print_banner",
    "resolve_zip",
]
