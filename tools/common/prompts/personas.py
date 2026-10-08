"""On-camera persona per product category, shared by cinematic and drama scenes.
"""



def character_persona(category: str) -> dict:
    """
    Return consistent, explicit physical character personas (intro, continuation)
    for each product category to enforce visual continuity across Google Flow scenes.
    """
    if category in ("BEAUTY_SKINCARE", "FASHION_APPAREL"):
        return {
            "intro": "an ordinary 24-year-old Vietnamese woman with shoulder-length black hair loosely tucked behind one ear, natural skin texture with a few small blemishes, wearing a plain oversized beige t-shirt",
            "cont": "the same 24-year-old Vietnamese woman with shoulder-length black hair and plain beige t-shirt",
        }
    elif category == "HEALTH_FITNESS":
        return {
            "intro": "an ordinary 25-year-old Vietnamese man with short slightly messy black hair, average fit build, wearing a faded dark grey t-shirt and shorts",
            "cont": "the same 25-year-old Vietnamese man with short black hair and faded dark grey t-shirt",
        }
    elif category == "KITCHEN_HOME":
        return {
            "intro": "an ordinary 30-year-old Vietnamese woman with black hair in a loose ponytail with a few stray strands, wearing a plain cotton house t-shirt",
            "cont": "the same 30-year-old Vietnamese woman with a loose ponytail and plain cotton house t-shirt",
        }
    elif category == "TECH_GADGETS":
        return {
            "intro": "an ordinary 25-year-old Vietnamese man with short slightly messy black hair, wearing a plain navy t-shirt",
            "cont": "the same 25-year-old Vietnamese man with short black hair and plain navy t-shirt",
        }
    else:  # GENERAL_LIFESTYLE: everyday household products, filmed at home
        return {
            "intro": "an ordinary 28-year-old Vietnamese woman with black hair in a loose bun, wearing a plain light grey house t-shirt and shorts",
            "cont": "the same 28-year-old Vietnamese woman with black hair in a loose bun and plain light grey t-shirt",
        }


__all__ = ["character_persona"]
