"""TikTok scene builders and the ``--style`` registry that selects them.

Add a style by writing a builder module here and registering it in ``STYLES``.
"""
from tools.common.prompts import StoryContext, StyleRegistry, build_flow_cinematic_scenes
from tools.tiktok_ad.prompts.cta import append_call_to_action
from tools.tiktok_ad.prompts.faceless_pov import build_faceless_pov_scenes
from tools.tiktok_ad.prompts.hybrid import build_hybrid_scenes
from tools.tiktok_ad.prompts.lifestyle_edc import build_lifestyle_edc_scenes
from tools.tiktok_ad.prompts.problem_solution import build_problem_solution_scenes
from tools.tiktok_ad.prompts.viral_hook import build_viral_hook_scenes


def _features(ctx: StoryContext) -> dict:
    return dict(
        category=ctx.category,
        clean_title=ctx.clean_title,
        feat1_title=ctx.feat1_title,
        feat1_desc=ctx.feat1_desc,
        feat2_title=ctx.feat2_title,
        feat2_desc=ctx.feat2_desc,
        custom_idea=ctx.custom_idea,
    )


# Unknown styles fall back to the platform's signature viral hook.
STYLES = StyleRegistry(fallback="viral_hook")
STYLES.register(
    ("viral_hook", "hook", "viral"),
    lambda ctx: build_viral_hook_scenes(social_proof_title=ctx.social_proof_title, product=ctx.product, **_features(ctx)),
)
STYLES.register(
    ("faceless_pov", "hands_on_pov", "pov"),
    lambda ctx: build_faceless_pov_scenes(social_proof_title=ctx.social_proof_title, product=ctx.product, **_features(ctx)),
)
STYLES.register(("problem_solution", "drama"), lambda ctx: build_problem_solution_scenes(product=ctx.product, **_features(ctx)))
STYLES.register(
    ("flow_cinematic", "flow", "tech_minimal"),
    lambda ctx: build_flow_cinematic_scenes(social_proof_title=ctx.social_proof_title, **_features(ctx)),
)
STYLES.register(("lifestyle_edc", "lifestyle"), lambda ctx: build_lifestyle_edc_scenes(product=ctx.product, **_features(ctx)))
STYLES.register(("hybrid",), build_hybrid_scenes)

__all__ = [
    "STYLES",
    "append_call_to_action",
    "build_faceless_pov_scenes",
    "build_flow_cinematic_scenes",
    "build_hybrid_scenes",
    "build_lifestyle_edc_scenes",
    "build_problem_solution_scenes",
    "build_viral_hook_scenes",
]
