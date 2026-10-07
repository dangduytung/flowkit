# `/fk-tiktok-ad` — TikTok Video Ad Generator (Viral Hooks & Trend Remix)

Dedicated skill for **TikTok Video Ads & TikTok Shop**. Automatically processes **TikTok Product ZIPs** (downloaded product media, shop raw video, specs, customer reviews from `TikTok Downloads`) into high-conversion vertical (9:16) video ads.

> **Architecture & Platform Separation:**
> - `/fk-tiktok-ad` (this skill): Dedicated to **TikTok Product ZIPs / TikTok Shop** via `tools.tiktok_ad`.
> - `/fk-shopee-ad`: Dedicated to **Shopee Product ZIPs** via `tools.shopee_ad`.

## Usage Examples

```bash
# Auto-detect newest ZIP in TikTok Downloads, default viral_hook with Yellow Cart CTA:
python -m tools.tiktok_ad.orchestrator

# Fast local cut from shop raw video & product photos:
python -m tools.tiktok_ad.orchestrator --mode local --style viral_hook --cta yellow_cart

# Faceless First-Person POV (hands/feet demo, unboxing, clean):
python -m tools.tiktok_ad.orchestrator --style faceless_pov --cta yellow_cart

# Silent / Trend audio sync mode (produces clean video for in-app TikTok sound pairing):
python -m tools.tiktok_ad.orchestrator --silent --clean

# Export with custom tag for side-by-side comparison:
python -m tools.tiktok_ad.orchestrator --style viral_hook --tag v1
python -m tools.tiktok_ad.orchestrator --style faceless_pov --tag v2

# 100% Google Flow AI cinematic video:
python -m tools.tiktok_ad.orchestrator --mode flow --style flow_cinematic

# List available TikTok ZIP files:
python -m tools.tiktok_ad.orchestrator --list
```

## Modes (`--mode`)
- `auto` (default): Automatically produces narrated video (`_local_<variant>.mp4`) with OmniVoice Vietnamese TTS. If FlowKit is connected, also renders `_flow_<variant>.mp4` (bản tắt tiếng chỉ sinh khi truyền `--silent`).
- `local`: Edits shop raw video and animates product photos locally via FFmpeg (10-15s execution).
- `flow`: AI video generation with Google Flow (character consistency via Anchor Frame, automatic watermark removal).
- `both`: Runs both local assembler and Google Flow AI pipelines.

## Styles (`--style`)
- `viral_hook` (default): High-retention question/problem hook in the first 2-3 seconds addressing pain points.
- `faceless_pov` / `hands_on_pov`: First-person POV demonstration (hands/feet only, 100% faceless, unboxing & usage).
- `problem_solution`: Urgent pain point -> Product rescue -> Relief and satisfaction.
- `flow_cinematic`: Cinematic KOC review with character face consistency across scenes.
- `lifestyle_edc`: Active everyday carry lifestyle scenes.
- `hybrid`: Alternating Flow AI video scenes and real shop product photos.

## Key Flags
- `--silent` / `--no-voice`: Mutes narration; exports 9:16 video with stereo silence track ready for TikTok sound library.
- `--clean` / `--no-overlay`: Exports clean video without hardcoded text overlays for custom typography.
- `--tag <name>`: Optional custom tag suffix (e.g. `--tag v2`, `--tag testA`) to isolate output deliverables for A/B testing.
- `--cta {yellow_cart, profile_bio, follow, none}`:
  - `yellow_cart` (default): Outro pointing to the bottom-left yellow cart icon.
  - `profile_bio`: Outro pointing to link in channel Bio.
  - `follow`: Outro encouraging viewers to tap follow.
  - `none`: Neutral 4-scene video without outro CTA.
- `--speed <float>`: OmniVoice narration speed (default: `1.03`).
- `--profile <id>`: OmniVoice voice profile ID.
- `--crop {blur_bg, center_crop}`: 9:16 canvas framing mode (default: `blur_bg`).
- `--bgm [path]`: Background music, **off by default**. `--bgm` picks a random track from `assets/bgm/` (preferring one named after the style); `--bgm <file>` uses that file.
- `--scene <id> [<id> ...]`: Re-render only these scenes (their prompts/copy are refreshed from the builders; every other scene keeps its narration and clips). After a Flow failure the run prints the exact `--scene ...` command to retry.
- `--regen`: Re-render all Flow AI clips; the storyboard (including hand edits) is kept.
- `--force-storyboard`: Rebuild `storyboard_{style}.json` from scratch (discards hand edits). `--idea` implies it.
- `--zip <path>`: Specify target ZIP (defaults to newest in `TIKTOK_DOWNLOADS_DIR`).
- Output root: `output/tiktok_ads/` unless `TIKTOK_OUTPUT_DIR` is set in `.env`.

## Multi-Variant Export Architecture
Outputs are saved into `output/tiktok_ads/<slug>/final/` using collision-free semantic names:
- Format: `{slug}_{mode}_{style}[_clean][_cta-<name>][_tag].mp4`
- Companion assets: `{slug}_{variant}_cover.jpg`, `{slug}_{variant}_script.txt`, `{slug}_{variant}_voiceover.mp3`, `{slug}_{variant}_publish_guide.txt`.
- Intermediate files (storyboard & clips) are isolated by style (`storyboard_{style}.json`, `{variant}_scene_{id}.wav`) so you can generate multiple styles/options and pick the best video without overwriting.

Full documentation: `docs/TIKTOK_AD_GUIDE.md` (Web dashboard: `docs/ECOMMERCE_AD_GUIDE.html`).
