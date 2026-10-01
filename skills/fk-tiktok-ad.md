# `/fk-tiktok-ad` — TikTok Video Ad Generator (Viral Hooks & Trend Remix)

Dedicated skill for **TikTok Video Ads & TikTok Shop**. Processes TikTok video URLs, trending TikTok audio/video assets, and TikTok Shop product links into high-conversion vertical (9:16) video ads.

> **Namespace & Separation Notice:**
> - `/fk-tiktok-ad` (this skill): Strictly processes **TikTok video URLs / TikTok Shop links** via `tools.tiktok_ad`.
> - `/fk-shopee-ad`: Dedicated to **Shopee Product ZIPs** (local shop media & specifications) via `tools.shopee_ad`.

Usage:
```bash
# Generate TikTok Ad from a TikTok video URL / trend link
python -m tools.tiktok_ad.orchestrator --url "https://vt.tiktok.com/..." --style viral_hook

# TikTok Shop product showcase with yellow-cart CTA
python -m tools.tiktok_ad.orchestrator --url "..." --style product_showcase --cta yellow_cart

# Silent / Trend audio sync mode (clean video for in-app CapCut / TikTok sound pairing)
python -m tools.tiktok_ad.orchestrator --url "..." --style fast_cut --silent --clean
```

## Modes (`--mode`)
- `flow`: AI video generation with TikTok viral pacing (fast-cuts, dynamic transitions).
- `remix`: Scrapes and re-edits public TikTok video clips with smart speed ramping and hook replacement.
- `hybrid`: Combines viral hook intro (0-3s) with AI product demonstration (3-15s).

## Styles (`--style`)
- `viral_hook`: High-retention question/problem hook in the first 2 seconds.
- `hands_on_pov`: First-person hands-only POV demonstration.
- `fast_cut`: 1-2s quick transitions synced to trending audio beats.
- `reaction_duet`: Split or PIP reaction format.

## Key Flags
- `--silent` / `--no-voice`: Mutes narration; exports 9:16 silent video with stereo silence track ready for TikTok sound library.
- `--clean` / `--no-overlay`: Exports clean video without hardcoded text overlays.
- `--cta {yellow_cart, profile_bio, follow, none}`:
  - `yellow_cart`: Outro pointing to the bottom-left yellow cart icon.
  - `profile_bio`: Outro pointing to link in channel Bio.
  - `follow`: Outro encouraging viewers to tap follow.
  - `none`: Neutral 4-scene video without outro CTA.

Full documentation: `docs/TIKTOK_AD_GUIDE.md` (Web dashboard: `docs/ECOMMERCE_AD_GUIDE.html`).
