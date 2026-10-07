"""Command line shared by every platform's ``orchestrator`` module."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Optional, Sequence

from tools.common.flow_client import FlowKitClient
from tools.common.pipeline.context import PlatformHooks, RunOptions, resolve_zip
from tools.common.pipeline.flow import run_flow_pipeline
from tools.common.pipeline.local import run_local_pipeline
from tools.common.product import parse_product_zip
from tools.common.settings import AutoModePolicy, PlatformProfile, ensure_utf8_console

MODES = ("auto", "both", "flow", "local", "zip")
CROP_MODES = ("blur_bg", "center_crop")
# --method predates --mode; its values map onto modes.
LEGACY_METHODS = {"flow": "flow", "local": "local", "zip": "local", "ken_burns": "local"}


def build_parser(profile: PlatformProfile) -> argparse.ArgumentParser:
    name = profile.display_name
    p = argparse.ArgumentParser(description=f"{name} Product Video Ad Generator")
    p.add_argument("--zip", type=str, default=None, help=f"Đường dẫn file zip sản phẩm (mặc định: zip mới nhất trong {profile.env_prefix}_DOWNLOADS_DIR)")
    p.add_argument("--list", action="store_true", help=f"Liệt kê các file zip {name} đang có")
    p.add_argument("--mode", choices=MODES, default="auto", help=(
        "Chế độ: 'auto' (mặc định), 'both', 'flow', 'local'. "
        + ("auto = có video trong zip thì làm cả local + flow, chỉ có ảnh thì làm flow"
           if profile.auto_mode is AutoModePolicy.BY_ASSETS
           else "auto = luôn làm local, thêm flow khi FlowKit đang kết nối")
    ))
    p.add_argument("--method", choices=sorted(LEGACY_METHODS), default=None, help="Alias cũ của --mode")
    p.add_argument("--flow", action="store_true", help="Viết tắt cho --mode flow")
    p.add_argument("--crop", choices=CROP_MODES, default="blur_bg", help="Cách đưa video/ảnh về 9:16 (mặc định: blur_bg)")
    p.add_argument("--cta", choices=profile.cta_choices, default=profile.default_cta, help=f"Cảnh kêu gọi hành động cuối video (mặc định: {profile.default_cta})")
    p.add_argument("--style", type=str, default=profile.default_style, help=(
        f"Phong cách kịch bản (mặc định: {profile.default_style}); 'all' = {', '.join(profile.batch_styles)}; "
        "hoặc nhiều style phân tách bằng dấu phẩy"
    ))
    p.add_argument("--idea", "--story", type=str, default=None, help="Ý tưởng / tình huống kịch bản tùy chỉnh (tự tạo lại storyboard)")
    p.add_argument("--scene", nargs="+", type=int, default=None, help="Chỉ tạo lại các phân cảnh này (ví dụ: --scene 2 3)")
    p.add_argument("--regen", action="store_true", help="Tạo lại toàn bộ clip AI từ Google Flow (giữ nguyên storyboard)")
    p.add_argument("--force-storyboard", action="store_true", help="Tạo lại storyboard từ đầu (mất chỉnh sửa tay trong JSON)")
    p.add_argument("--speed", type=float, default=None, help="Tốc độ đọc OmniVoice (mặc định: OMNIVOICE_SPEED trong .env)")
    p.add_argument("--profile", type=str, default=None, help="Profile ID giọng đọc trên VoiceStudio")
    p.add_argument("--no-voice", "--silent", dest="no_voice", action="store_true", help="Không tạo giọng thuyết minh")
    p.add_argument("--no-overlay", "--clean", dest="no_overlay", action="store_true", help="Không chèn chữ lên video")
    p.add_argument("--channel-name", type=str, default=profile.channel_name, help=f"Tên kênh (mặc định: {profile.env_prefix}_AD_CHANNEL_NAME)")
    p.add_argument("--channel-handle", type=str, default=profile.channel_handle, help=f"Handle kênh (mặc định: {profile.env_prefix}_AD_CHANNEL_HANDLE)")
    p.add_argument("--tag", type=str, default=None, help="Nhãn phân biệt lần xuất (ví dụ: --tag v2)")
    p.add_argument("--delogo", type=str, default="auto", help="Xóa logo shop: 'auto' (theo config/watermark_rules.json), 'none', hoặc 'x=..:y=..:w=..:h=..'")
    p.add_argument("--bgm", nargs="?", const="auto", default=None, help="Bật nhạc nền (mặc định tắt): --bgm = ngẫu nhiên từ assets/bgm/, --bgm <file> = chỉ định")
    return p


def options_from_args(args: argparse.Namespace, zip_path: Path, style: str) -> RunOptions:
    return RunOptions(
        zip_path=zip_path,
        style=style,
        cta_mode=args.cta,
        speed=args.speed,
        voice_profile_id=args.profile,
        crop_mode=args.crop,
        channel_name=args.channel_name,
        channel_handle=args.channel_handle,
        custom_idea=args.idea,
        # A new idea only takes effect in a freshly generated storyboard.
        force_storyboard=args.force_storyboard or bool(args.idea),
        regen=args.regen,
        no_voice=args.no_voice,
        no_overlay=args.no_overlay,
        tag=args.tag,
        delogo=args.delogo,
        bgm=args.bgm,
        target_scenes=args.scene,
    )


def select_runs(
    mode: str,
    profile: PlatformProfile,
    zip_has_video: bool,
    flowkit_ready: Callable[[], bool],
) -> tuple[bool, bool]:
    """(run_local, run_flow) for the requested mode."""
    if mode == "both":
        return True, True
    if mode in ("local", "zip"):
        return True, False
    if mode == "flow":
        return False, True
    if profile.auto_mode is AutoModePolicy.BY_ASSETS:
        if zip_has_video:
            print("💡 File ZIP có video gốc: tạo CẢ HAI bản (_local.mp4 & _flow.mp4).")
            return True, True
        print("💡 File ZIP chỉ có hình ảnh: tạo bản Google Flow AI (_flow.mp4).")
        return False, True
    if flowkit_ready():
        print("💡 FlowKit đang kết nối: tạo CẢ HAI bản (_local.mp4 & _flow.mp4).")
        return True, True
    print("💡 Tạo bản Local (_local.mp4). Kết nối FlowKit để tạo thêm bản Flow AI (_flow.mp4).")
    return True, False


def _print_zip_list(profile: PlatformProfile) -> None:
    print(f"\n📂 Các file zip {profile.display_name} tìm thấy trong máy:")
    zips = profile.list_zips()
    if not zips:
        print(f"  (Không có file zip nào trong {profile.downloads_dir})")
    for i, z in enumerate(zips, 1):
        print(f"  [{i}] {z.name} ({z.stat().st_size / 1024 / 1024:.1f} MB)")


def run_cli(profile: PlatformProfile, hooks: PlatformHooks, argv: Optional[Sequence[str]] = None) -> None:
    ensure_utf8_console()
    args = build_parser(profile).parse_args(argv)
    if args.list:
        _print_zip_list(profile)
        return

    zip_path = resolve_zip(profile, Path(args.zip) if args.zip else None)
    mode = args.mode
    if args.method:
        mode = LEGACY_METHODS[args.method]
    if args.flow:
        mode = "flow"
    run_local, run_flow = select_runs(
        mode, profile, bool(parse_product_zip(zip_path).video_name), lambda: FlowKitClient().is_ready()
    )

    styles = profile.resolve_styles(args.style)
    if len(styles) > 1:
        print(f"\n🎬 XUẤT HÀNG LOẠT {len(styles)} PHONG CÁCH: {', '.join(styles)}")
    for i, style in enumerate(styles, 1):
        if len(styles) > 1:
            print(f"\n{'=' * 65}\n▶ [{i}/{len(styles)}] PHONG CÁCH: {style.upper()}\n{'=' * 65}")
        opts = options_from_args(args, zip_path, style)
        if run_local:
            print("\n" + "▶" * 25 + f" SẢN XUẤT VIDEO LOCAL ({style}) " + "◀" * 25)
            run_local_pipeline(profile, hooks, opts)
        if run_flow:
            print("\n" + "▶" * 25 + f" SẢN XUẤT VIDEO GOOGLE FLOW AI ({style}) " + "◀" * 25)
            run_flow_pipeline(profile, hooks, opts)


__all__ = ["build_parser", "options_from_args", "run_cli", "select_runs"]
