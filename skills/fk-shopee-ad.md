# `/fk-shopee-ad` — Shopee Video Ad Generator (Dynamic & Watermark-Free)

Dedicated skill for **Shopee E-Commerce Ads**. Automatically parses Shopee product ZIPs (product images, raw shop video, specs, reviews) into high-conversion vertical (9:16) video ads.

> **Architecture & Platform Separation:**
> - `/fk-shopee-ad` (this skill): Strictly processes **Shopee Product ZIPs** via `tools.shopee_ad`.
> - `/fk-tiktok-ad`: Dedicated to **TikTok Product ZIPs / TikTok Shop** via `tools.tiktok_ad`.

Usage:
```bash
# Faceless First-Person POV (hands-only, silent, clean — ideal for organic & affiliate showcase)
python -m tools.shopee_ad.orchestrator --style faceless_pov --no-voice --no-overlay

# Fast local cut from shop raw video (10-15s, offline)
python -m tools.shopee_ad.orchestrator --mode local --style faceless_pov --no-voice --no-overlay

# Export with custom tag for side-by-side comparison:
python -m tools.shopee_ad.orchestrator --style faceless_pov --tag v1
python -m tools.shopee_ad.orchestrator --style flow_cinematic --tag v2

# Full Google Flow AI KOC video (OmniVoice Vietnamese voiceover + text overlays)
python -m tools.shopee_ad.orchestrator --mode flow --style flow_cinematic

# Problem-Solution Drama style with Shopee / TikTok Shop CTA
python -m tools.shopee_ad.orchestrator --style problem_solution --cta shopee
python -m tools.shopee_ad.orchestrator --style problem_solution --cta tiktok
```

## Modes (`--mode`)
- `flow`: 100% Google Flow AI video (auto delogo watermark, auto-uploads product photo as reference).
- `local`: Edits shop raw video (auto avoids flash cuts/glitches) or Ken Burns pan & zoom slides.
- `hybrid`: Combines AI video (scenes 1 & 3) with real product photos (scenes 2 & 4).
- `auto` (default): Produces both `_local_<variant>.mp4` and `_flow_<variant>.mp4` if shop video exists.

## Styles (`--style`)
- `faceless_pov`: 100% Faceless. First-person POV, macro close-up of hands, neck-down angles. Unbox -> Setup/demo -> Practical test -> Clean finish.
- `flow_cinematic`: Cinematic KOC review with consistent character persona.
- `problem_solution`: Urgent pain point -> Product rescue -> Relief and satisfaction.
- `lifestyle_edc`: Active everyday carry lifestyle.

## Key Flags
- `--no-voice` / `--silent`: Silent 20s video with stereo silent audio track for trending audio pairing.
- `--no-overlay` / `--clean`: 100% clean footage without burned text overlays.
- `--tag <name>`: Optional custom tag suffix (e.g. `--tag v2`, `--tag test1`) to isolate output deliverables for A/B testing.
- `--cta {none, follow, shopee, tiktok}`:
  - `none`: Neutral 4-scene video without forced outro.
  - `follow`: Soft outro inviting viewers to follow channel.
  - `shopee`: Calls to check pinned comment / Shopee store.
  - `tiktok`: Calls to tap the yellow cart icon on bottom-left.
- `--idea "..."`: Custom creative context injection into prompts.
- `--zip <path>`: Specify target ZIP (defaults to newest in `SHOPEE_DOWNLOADS_DIR`).

## Multi-Variant Export Architecture
Outputs are saved into `output/shopee_ads/<slug>/final/` using collision-free semantic names:
- Format: `{slug}_{mode}_{style}[_clean][_cta-<name>][_tag].mp4`
- Companion assets: `{slug}_{variant}_cover.jpg`, `{slug}_{variant}_script.txt`, `{slug}_{variant}_voiceover.mp3`, `{slug}_{variant}_publish_guide.txt`.
- Intermediate files (storyboard & clips) are isolated by style (`storyboard_{style}.json`, `{variant}_scene_{id}.wav`) so you can generate multiple styles/options and pick the best video without overwriting.

Full visual interactive dashboard: `docs/ECOMMERCE_AD_GUIDE.html` or `docs/SHOPEE_AD_GUIDE.md`.
