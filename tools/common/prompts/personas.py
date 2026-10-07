"""On-camera persona per product category, shared by cinematic and drama scenes.
"""



def character_persona(category: str) -> dict:
    """
    Return consistent, explicit physical character personas (intro, continuation)
    for each product category to enforce visual continuity across Google Flow scenes.
    """
    if category in ("BEAUTY_SKINCARE", "FASHION_APPAREL"):
        return {
            "intro": "a stylish 24-year-old Vietnamese young woman with shoulder-length soft straight black hair, clear radiant skin, wearing an aesthetic beige knit top",
            "cont": "the same 24-year-old Vietnamese young woman with shoulder-length soft black hair, clear skin, and beige knit top",
        }
    elif category == "HEALTH_FITNESS":
        return {
            "intro": "an athletic 25-year-old Vietnamese young man with short trim black hair, fit build, wearing a dark grey athletic crew-neck tee",
            "cont": "the same athletic 25-year-old Vietnamese young man with short trim black hair and dark grey tee",
        }
    elif category == "KITCHEN_HOME":
        return {
            "intro": "a friendly 26-year-old Vietnamese homemaker with neat ponytail black hair, warm smile, wearing a casual white t-shirt under a light beige apron",
            "cont": "the same friendly 26-year-old Vietnamese homemaker with neat ponytail black hair and beige apron",
        }
    else:  # TECH_GADGETS and GENERAL_LIFESTYLE
        return {
            "intro": "a stylish 25-year-old Vietnamese professional young man with neat short black side-part hair, wearing a crisp light-blue collared Oxford shirt and dark slacks",
            "cont": "the same 25-year-old Vietnamese professional young man with neat short black side-part hair and light-blue Oxford shirt",
        }


__all__ = ["character_persona"]
