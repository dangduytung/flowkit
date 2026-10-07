"""Shopee scene builders and the ``--style`` registry that selects them.

Add a style by writing a builder module here and registering it in ``STYLES``.
"""
from tools.common.prompts import StoryContext, StyleRegistry, build_flow_cinematic_scenes
from tools.shopee_ad.prompts.cta import build_cta_scene
from tools.shopee_ad.prompts.faceless_pov import build_faceless_pov_scenes, build_vacuum_faceless_pov_scenes
from tools.shopee_ad.prompts.lifestyle_edc import build_lifestyle_edc_scenes
from tools.shopee_ad.prompts.problem_solution import build_problem_solution_scenes
from tools.shopee_ad.prompts.showcase import build_hybrid_scenes, build_local_scenes


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


# Unknown styles render the plain local storyboard.
STYLES = StyleRegistry(fallback="local")
STYLES.register(
    ("faceless_pov", "faceless", "hands_on_demo", "pov_demo", "pov"),
    lambda ctx: build_faceless_pov_scenes(social_proof_title=ctx.social_proof_title, **_features(ctx)),
)
STYLES.register(("problem_solution", "drama"), lambda ctx: build_problem_solution_scenes(**_features(ctx)))
STYLES.register(("lifestyle_edc", "lifestyle"), lambda ctx: build_lifestyle_edc_scenes(**_features(ctx)))
STYLES.register(
    ("flow_cinematic", "flow", "tech_minimal"),
    lambda ctx: build_flow_cinematic_scenes(social_proof_title=ctx.social_proof_title, **_features(ctx)),
)
STYLES.register(("hybrid",), build_hybrid_scenes)
STYLES.register(("local",), build_local_scenes)

__all__ = [
    "STYLES",
    "build_cta_scene",
    "build_faceless_pov_scenes",
    "build_flow_cinematic_scenes",
    "build_hybrid_scenes",
    "build_lifestyle_edc_scenes",
    "build_local_scenes",
    "build_problem_solution_scenes",
    "build_vacuum_faceless_pov_scenes",
]
