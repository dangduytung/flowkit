"""On-camera persona engine: 60+ curated profiles, combinatorial trait generator, and custom prompt parser.

Supports:
1. Large curated pools (10 distinct everyday Vietnamese personas per category = 60 profiles).
2. Combinatorial/procedural persona synthesis (``--persona random`` or ``random:<seed>``)
   mixing age, gender, face structure, hairstyle, eyewear, and casual home/daily wardrobe.
3. Free-form custom character prompts (``--persona "..."``) in English or Vietnamese,
   automatically converting Vietnamese character descriptions to clean English so Google Flow
   never prints Vietnamese words onto product packaging, and building both ``intro`` and ``cont``.
"""
from __future__ import annotations

import hashlib
import re
import secrets
import unicodedata
from typing import Optional

_PERSONA_POOLS: dict[str, tuple[dict[str, str], ...]] = {
    "BEAUTY_SKINCARE": (
        {
            "intro": "an ordinary 24-year-old Vietnamese woman with shoulder-length black hair loosely tucked behind one ear, natural skin texture with a few small blemishes, wearing a plain oversized beige t-shirt",
            "cont": "the same 24-year-old Vietnamese woman with shoulder-length black hair and plain beige t-shirt",
        },
        {
            "intro": "an ordinary 27-year-old Vietnamese woman with long wavy dark brown hair clipped half-up with a matte claw clip, round face, wearing a soft sage-green ribbed cardigan over a white tank top",
            "cont": "the same 27-year-old Vietnamese woman with half-up wavy brown hair and sage-green cardigan",
        },
        {
            "intro": "an ordinary 22-year-old Vietnamese woman with a short chin-length bob haircut and wispy bangs, wearing thin wire-frame glasses and a pastel lavender cotton pajama shirt",
            "cont": "the same 22-year-old Vietnamese woman with short bob hair, wire-frame glasses and lavender pajama shirt",
        },
        {
            "intro": "an ordinary 29-year-old Vietnamese woman with straight black hair tied in a low braid over one shoulder, high cheekbones, wearing a cream linen button-down shirt with rolled sleeves",
            "cont": "the same 29-year-old Vietnamese woman with a low side braid and cream linen shirt",
        },
        {
            "intro": "an ordinary 25-year-old Vietnamese woman with curtain bangs and medium-length chestnut hair, warm tan skin, wearing a dusty pink crewneck sweatshirt",
            "cont": "the same 25-year-old Vietnamese woman with chestnut hair and dusty pink sweatshirt",
        },
        {
            "intro": "an ordinary 21-year-old Vietnamese woman with twin low braided pigtails and a small beauty mark near her left eye, wearing a butter-yellow cotton camisole with a white cardigan",
            "cont": "the same 21-year-old Vietnamese woman with low braided pigtails and yellow camisole with white cardigan",
        },
        {
            "intro": "an ordinary 32-year-old Vietnamese woman with a neat low chignon bun and soft dimples, wearing a powder-blue satin lounge shirt",
            "cont": "the same 32-year-old Vietnamese woman with a low bun and powder-blue lounge shirt",
        },
        {
            "intro": "an ordinary 23-year-old Vietnamese man with a clean two-block Korean-style haircut, clear natural skin, wearing a plain white waffle-knit tee",
            "cont": "the same 23-year-old Vietnamese man with a two-block haircut and white waffle-knit tee",
        },
        {
            "intro": "an ordinary 26-year-old Vietnamese woman with long straight jet-black hair held back by a wide fabric headband, oval face, wearing a grey melange zip hoodie",
            "cont": "the same 26-year-old Vietnamese woman with a fabric headband and grey zip hoodie",
        },
        {
            "intro": "an ordinary 35-year-old Vietnamese woman with shoulder-skimming layered hair and subtle smile lines, wearing an oatmeal linen v-neck blouse",
            "cont": "the same 35-year-old Vietnamese woman with shoulder-skimming layered hair and oatmeal blouse",
        },
    ),
    "FASHION_APPAREL": (
        {
            "intro": "an ordinary 24-year-old Vietnamese woman with shoulder-length black hair loosely tucked behind one ear, natural skin texture, wearing a fitted white ribbed tee",
            "cont": "the same 24-year-old Vietnamese woman with shoulder-length black hair and white ribbed tee",
        },
        {
            "intro": "an ordinary 26-year-old Vietnamese man with a clean tapered fade haircut, slim build, wearing a casual oatmeal-colored polo shirt",
            "cont": "the same 26-year-old Vietnamese man with a tapered haircut and oatmeal polo shirt",
        },
        {
            "intro": "an ordinary 23-year-old Vietnamese woman with long layered dark brown hair and oval glasses, slim build, wearing a striped navy-and-white cotton shirt",
            "cont": "the same 23-year-old Vietnamese woman with layered brown hair, oval glasses and striped shirt",
        },
        {
            "intro": "an ordinary 28-year-old Vietnamese man with medium-length parted black hair and light stubble, wearing an olive-green casual overshirt over a white tee",
            "cont": "the same 28-year-old Vietnamese man with parted black hair and olive overshirt",
        },
        {
            "intro": "an ordinary 25-year-old Vietnamese woman with a high ponytail and side-swept bangs, wearing a butter-yellow knit top",
            "cont": "the same 25-year-old Vietnamese woman with a high ponytail and butter-yellow knit top",
        },
        {
            "intro": "an ordinary 22-year-old Vietnamese woman with a trendy wolf-cut hairstyle in dark espresso brown, wearing a cropped grey cardigan and silver hoop earrings",
            "cont": "the same 22-year-old Vietnamese woman with an espresso-brown wolf-cut and grey cardigan",
        },
        {
            "intro": "an ordinary 30-year-old Vietnamese man with short wavy hair and tortoiseshell glasses, medium build, wearing a light blue chambray shirt with rolled cuffs",
            "cont": "the same 30-year-old Vietnamese man with tortoiseshell glasses and blue chambray shirt",
        },
        {
            "intro": "an ordinary 27-year-old Vietnamese woman with a French twist updo held by a wooden hairpin, angular jawline, wearing a terracotta linen top",
            "cont": "the same 27-year-old Vietnamese woman with a hairpin updo and terracotta linen top",
        },
        {
            "intro": "an ordinary 21-year-old Vietnamese man with fluffy curtain-parted black hair, tall lanky build, wearing an oversized vintage wash charcoal tee",
            "cont": "the same 21-year-old Vietnamese man with curtain-parted hair and charcoal tee",
        },
        {
            "intro": "an ordinary 33-year-old Vietnamese woman with a neat chin-length bob tucked behind one ear, wearing a classic beige trench-style vest over a black top",
            "cont": "the same 33-year-old Vietnamese woman with a chin-length bob and beige vest",
        },
    ),
    "HEALTH_FITNESS": (
        {
            "intro": "an ordinary 25-year-old Vietnamese man with short slightly messy black hair, average fit build, wearing a faded dark grey t-shirt and shorts",
            "cont": "the same 25-year-old Vietnamese man with short black hair and faded dark grey t-shirt",
        },
        {
            "intro": "an ordinary 29-year-old Vietnamese woman with black hair tied in a high sporty ponytail, toned build, wearing a dusty rose athletic zip jacket",
            "cont": "the same 29-year-old Vietnamese woman with a high ponytail and dusty rose athletic jacket",
        },
        {
            "intro": "an ordinary 34-year-old Vietnamese man with a short buzz-cut and rectangular glasses, office-worker build, wearing a light blue polo shirt",
            "cont": "the same 34-year-old Vietnamese man with a buzz-cut, glasses and light blue polo shirt",
        },
        {
            "intro": "an ordinary 26-year-old Vietnamese woman with a shoulder-length lob tied half-back, wearing a heather-grey sweatshirt and black joggers",
            "cont": "the same 26-year-old Vietnamese woman with half-tied hair and heather-grey sweatshirt",
        },
        {
            "intro": "an ordinary 40-year-old Vietnamese man with short salt-and-pepper hair at the temples, broad shoulders, wearing a navy cotton henley shirt",
            "cont": "the same 40-year-old Vietnamese man with salt-and-pepper temples and navy henley shirt",
        },
        {
            "intro": "an ordinary 23-year-old Vietnamese woman with a braided ponytail and sweatband, energetic expression, wearing a mint-green workout tank top",
            "cont": "the same 23-year-old Vietnamese woman with a braided ponytail and mint-green tank top",
        },
        {
            "intro": "an ordinary 31-year-old Vietnamese woman with short pixie-bob black hair and wire-rimmed glasses, wearing a relaxed cream knit sweater",
            "cont": "the same 31-year-old Vietnamese woman with pixie-bob hair, glasses and cream sweater",
        },
        {
            "intro": "an ordinary 28-year-old Vietnamese man with a short undercut and trim goatee, athletic build, wearing a burgundy raglan t-shirt",
            "cont": "the same 28-year-old Vietnamese man with an undercut and burgundy raglan shirt",
        },
        {
            "intro": "an ordinary 37-year-old Vietnamese woman with hair tied in a low knot, gentle tired eyes, wearing a soft olive home cardigan",
            "cont": "the same 37-year-old Vietnamese woman with a low hair knot and olive cardigan",
        },
        {
            "intro": "an ordinary 24-year-old Vietnamese man with curly top black hair and clear-frame glasses, wearing a sage-green hoodie",
            "cont": "the same 24-year-old Vietnamese man with curly top hair, clear glasses and sage hoodie",
        },
    ),
    "KITCHEN_HOME": (
        {
            "intro": "an ordinary 30-year-old Vietnamese woman with black hair in a loose ponytail with a few stray strands, wearing a plain cotton house t-shirt",
            "cont": "the same 30-year-old Vietnamese woman with a loose ponytail and plain cotton house t-shirt",
        },
        {
            "intro": "an ordinary 35-year-old Vietnamese woman with short neat shoulder-skimming black hair tucked behind her ears, warm friendly face, wearing a terracotta cotton blouse and a simple canvas apron",
            "cont": "the same 35-year-old Vietnamese woman with short black hair and terracotta blouse with canvas apron",
        },
        {
            "intro": "an ordinary 32-year-old Vietnamese man with short parted black hair and round glasses, wearing a checkered short-sleeve home shirt",
            "cont": "the same 32-year-old Vietnamese man with round glasses and checkered short-sleeve shirt",
        },
        {
            "intro": "an ordinary 27-year-old Vietnamese woman with long dark hair pinned up with a tortoiseshell claw clip, wearing a soft mint-green cotton lounge set",
            "cont": "the same 27-year-old Vietnamese woman with claw-clipped hair and mint-green lounge top",
        },
        {
            "intro": "an ordinary 38-year-old Vietnamese woman with a low braided bun and gentle smile lines, wearing a floral cream house shirt",
            "cont": "the same 38-year-old Vietnamese woman with a low braided bun and floral cream shirt",
        },
        {
            "intro": "an ordinary 29-year-old Vietnamese man with a neat crew cut, friendly round face, wearing a mustard-yellow t-shirt and a dark denim kitchen apron",
            "cont": "the same 29-year-old Vietnamese man with a crew cut and mustard tee under a denim apron",
        },
        {
            "intro": "an ordinary 25-year-old Vietnamese woman with medium wavy brown hair in a half-bun, wearing a pastel peach oversized t-shirt",
            "cont": "the same 25-year-old Vietnamese woman with a wavy half-bun and pastel peach t-shirt",
        },
        {
            "intro": "an ordinary 42-year-old Vietnamese woman with short curled bob hair and thin reading glasses, wearing a dusty blue button-front house blouse",
            "cont": "the same 42-year-old Vietnamese woman with a curled bob, glasses and dusty blue blouse",
        },
        {
            "intro": "an ordinary 33-year-old Vietnamese woman with long straight hair tied with a scrunchy, wearing a striped beige-and-white linen apron over a grey tee",
            "cont": "the same 33-year-old Vietnamese woman with scrunchy-tied hair and striped linen apron",
        },
        {
            "intro": "an ordinary 28-year-old Vietnamese man with side-swept black hair, wearing an olive-drab waffle cotton long-sleeve shirt with sleeves pushed up",
            "cont": "the same 28-year-old Vietnamese man with side-swept hair and olive waffle shirt",
        },
    ),
    "TECH_GADGETS": (
        {
            "intro": "an ordinary 25-year-old Vietnamese man with short slightly messy black hair, wearing a plain navy t-shirt",
            "cont": "the same 25-year-old Vietnamese man with short black hair and plain navy t-shirt",
        },
        {
            "intro": "an ordinary 27-year-old Vietnamese man with thin black-rimmed glasses and a neat side-part haircut, wearing a heather-charcoal hoodie with sleeves pushed up",
            "cont": "the same 27-year-old Vietnamese man with black-rimmed glasses and charcoal hoodie",
        },
        {
            "intro": "an ordinary 24-year-old Vietnamese woman with straight dark brown hair and round metal glasses, wearing an oversized olive crewneck sweater",
            "cont": "the same 24-year-old Vietnamese woman with round metal glasses and olive sweater",
        },
        {
            "intro": "an ordinary 31-year-old Vietnamese man with short cropped hair and a light beard shadow, wearing a casual beige oxford button-down shirt with rolled sleeves",
            "cont": "the same 31-year-old Vietnamese man with cropped hair and beige oxford shirt",
        },
        {
            "intro": "an ordinary 22-year-old Vietnamese woman with a short layered bob with auburn highlights and clear-frame glasses, wearing a cream knitted vest over a white tee",
            "cont": "the same 22-year-old Vietnamese woman with a bob haircut, clear glasses and cream vest",
        },
        {
            "intro": "an ordinary 29-year-old Vietnamese man with medium wavy parted hair and silver wire glasses, wearing a burgundy zip-up fleece jacket",
            "cont": "the same 29-year-old Vietnamese man with wire glasses and burgundy fleece jacket",
        },
        {
            "intro": "an ordinary 26-year-old Vietnamese woman with a high messy bun held by a pencil and wispy bangs, wearing a slate-blue sweatshirt",
            "cont": "the same 26-year-old Vietnamese woman with a high bun and slate-blue sweatshirt",
        },
        {
            "intro": "an ordinary 34-year-old Vietnamese man with a buzz fade and thick dark eyebrows, wearing a forest-green polo shirt",
            "cont": "the same 34-year-old Vietnamese man with a buzz fade and forest-green polo shirt",
        },
        {
            "intro": "an ordinary 23-year-old Vietnamese man with tousled comma bangs and a small mole on his cheek, wearing a black-and-white raglanshirt",
            "cont": "the same 23-year-old Vietnamese man with comma bangs and black-and-white raglan shirt",
        },
        {
            "intro": "an ordinary 28-year-old Vietnamese woman with long braided black hair and rectangular glasses, wearing a warm camel cardigan",
            "cont": "the same 28-year-old Vietnamese woman with braided hair, glasses and camel cardigan",
        },
    ),
    "GENERAL_LIFESTYLE": (
        {
            "intro": "an ordinary 26-year-old Vietnamese woman with long soft dark brown waves resting over her shoulders, gentle oval face, wearing a cozy cream-white cotton pajama shirt",
            "cont": "the same 26-year-old Vietnamese woman with soft dark brown waves and cream-white pajama shirt",
        },
        {
            "intro": "an ordinary 31-year-old Vietnamese man with short neat black hair and wire-rimmed glasses, wearing a warm oatmeal waffle-knit long-sleeve shirt",
            "cont": "the same 31-year-old Vietnamese man with wire-rimmed glasses and oatmeal waffle-knit shirt",
        },
        {
            "intro": "an ordinary 23-year-old Vietnamese woman with a collar-length layered haircut and wispy bangs, wearing a soft pastel blue oversized lounge sweater",
            "cont": "the same 23-year-old Vietnamese woman with collar-length hair and pastel blue lounge sweater",
        },
        {
            "intro": "an ordinary 33-year-old Vietnamese woman with dark hair clipped up with a claw clip and a few loose curls framing her cheeks, wearing a warm caramel-brown knit cardigan over a white tee",
            "cont": "the same 33-year-old Vietnamese woman with claw-clipped hair and caramel-brown cardigan",
        },
        {
            "intro": "an ordinary 28-year-old Vietnamese woman with black hair in a loose bun, wearing a plain light grey house t-shirt and shorts",
            "cont": "the same 28-year-old Vietnamese woman with black hair in a loose bun and plain light grey t-shirt",
        },
        {
            "intro": "an ordinary 25-year-old Vietnamese man with a relaxed two-block haircut and round tortoiseshell glasses, wearing a sage-green cotton lounge shirt",
            "cont": "the same 25-year-old Vietnamese man with tortoiseshell glasses and sage-green lounge shirt",
        },
        {
            "intro": "an ordinary 29-year-old Vietnamese woman with a low side ponytail and soft curtain bangs, dimples on her cheeks, wearing a dusty rose linen pajama top",
            "cont": "the same 29-year-old Vietnamese woman with a side ponytail and dusty rose pajama top",
        },
        {
            "intro": "an ordinary 36-year-old Vietnamese woman with a neat shoulder-length bob and warm smile, wearing a butter-cream ribbed lounge cardigan",
            "cont": "the same 36-year-old Vietnamese woman with a shoulder-length bob and butter-cream cardigan",
        },
        {
            "intro": "an ordinary 27-year-old Vietnamese man with short textured black hair and light facial stubble, wearing a heather-grey henley shirt",
            "cont": "the same 27-year-old Vietnamese man with short textured hair and heather-grey henley",
        },
        {
            "intro": "an ordinary 22-year-old Vietnamese woman with long straight black hair and thin silver glasses, wearing a lavender cotton sweatshirt",
            "cont": "the same 22-year-old Vietnamese woman with long straight hair, silver glasses and lavender sweatshirt",
        },
    ),
}

# Combinatorial building blocks for procedural persona synthesis (thousands of combinations)
_FEMALE_HAIRSTYLES: tuple[tuple[str, str], ...] = (
    ("long soft dark brown waves resting over her shoulders", "soft dark brown waves"),
    ("a short chin-length bob haircut with wispy bangs", "short bob hair"),
    ("straight black hair clipped half-up with a matte claw clip", "claw-clipped black hair"),
    ("chestnut-brown hair with curtain bangs", "chestnut hair and curtain bangs"),
    ("a high ponytail with a few loose strands framing her temples", "a high ponytail"),
    ("a low braided ponytail resting over one shoulder", "a low side braid"),
    ("collar-length layered black hair tucked behind one ear", "collar-length layered hair"),
    ("medium wavy hair tied in a relaxed half-bun", "a wavy half-bun"),
)
_MALE_HAIRSTYLES: tuple[tuple[str, str], ...] = (
    ("a clean two-block haircut", "a two-block haircut"),
    ("short neat side-parted black hair", "side-parted black hair"),
    ("a short tapered fade haircut", "a tapered haircut"),
    ("slightly messy wavy black hair", "wavy black hair"),
    ("a short crew cut", "a crew cut"),
    ("medium curtain-parted black hair", "curtain-parted hair"),
)
_FACE_TRAITS: tuple[str, ...] = (
    "natural skin texture, gentle oval face",
    "warm tan skin and soft dimples",
    "round friendly face with natural pores",
    "high cheekbones and a small beauty mark near the eye",
    "thin wire-rimmed glasses and a relaxed expression",
    "round tortoiseshell glasses and natural skin texture",
    "clear-frame glasses and a warm unposed look",
    "expressive dark eyes and natural unmade skin",
)
_OUTFITS: tuple[tuple[str, str], ...] = (
    ("a cozy cream-white cotton pajama shirt", "cream-white pajama shirt"),
    ("a soft sage-green ribbed cardigan over a white tee", "sage-green cardigan"),
    ("an oatmeal waffle-knit long-sleeve shirt", "oatmeal waffle-knit shirt"),
    ("a dusty rose oversized cotton sweatshirt", "dusty rose sweatshirt"),
    ("a light blue linen button-down shirt with rolled sleeves", "light blue linen shirt"),
    ("a warm caramel-brown knit sweater", "caramel-brown sweater"),
    ("a pastel lavender cotton lounge top", "lavender lounge top"),
    ("a heather-charcoal hoodie", "charcoal hoodie"),
    ("a terracotta cotton shirt", "terracotta shirt"),
    ("a butter-yellow knit tee", "butter-yellow knit tee"),
)

# Vietnamese -> English dictionary for free-form custom character prompts
_VI_TO_EN_RULES: tuple[tuple[str, str], ...] = (
    (r"\bcô gái\b|\bạn nữ\b|\bphụ nữ\b|\bnữ\b|\bchị\b", "Vietnamese woman"),
    (r"\bchàng trai\b|\bbạn nam\b|\bđàn ông\b|\bnam\b|\banh\b", "Vietnamese man"),
    (r"\btrung niên\b", "40-year-old"),
    (r"\bsinh viên\b|\bgen\s*z\b|\btrẻ\b", "22-year-old"),
    (r"(\d{2})\s*tuổi", r"\1-year-old"),
    (r"\btóc ngắn ngang vai\b|\btóc ngang vai\b", "with shoulder-length hair"),
    (r"\btóc ngắn\b|\btóc bob\b", "with a short bob haircut"),
    (r"\btóc dài uốn sóng\b|\btóc xoăn sóng\b|\btóc uốn\b|\btóc xoăn\b", "with long wavy hair"),
    (r"\btóc dài thẳng\b|\btóc thẳng\b", "with long straight hair"),
    (r"\btóc dài\b", "with long hair"),
    (r"\btóc buộc cao\b|\btóc đuôi ngựa\b", "with hair in a high ponytail"),
    (r"\btóc búi\b|\bbúi tóc\b", "with hair in a loose bun"),
    (r"\bkẹp càng cua\b|\btóc kẹp\b", "with hair clipped up with a claw clip"),
    (r"\btóc tết\b|\bbím tóc\b", "with braided hair"),
    (r"\bmái bay\b|\bmái thưa\b", "and wispy bangs"),
    (r"\bđầu đinh\b|\btóc húi cua\b", "with a short crew cut"),
    (r"\btóc rẽ ngôi\b|\btóc hai mái\b", "with side-parted hair"),
    (r"\bmàu nâu hạt dẻ\b|\bnâu hạt dẻ\b|\btóc nâu\b", "in warm chestnut brown"),
    (r"\btóc đen\b", "in natural black"),
    (r"\bđeo kính tròn\b|\bkính tròn\b", "wearing round wire-frame glasses"),
    (r"\bđeo kính\b|\bkính cận\b", "wearing thin eyeglasses"),
    (r"\bkhông đeo kính\b", "without glasses"),
    (r"\bmặt tròn\b|\bmặt bầu bĩnh\b", "with a friendly round face"),
    (r"\bmặt trái xoan\b", "with a gentle oval face"),
    (r"\bmá lúm đồng tiền\b|\bmá lúm\b", "with soft dimples"),
    (r"\brâu nhẹ\b|\brâu quai nón\b", "with light facial stubble"),
    (r"\bmặc đồ ngủ\b|\bđồ bộ\b|\bpijama\b|\bpyjama\b", "wearing a cozy cotton pajama shirt"),
    (r"\báo len\b|\bsweater\b", "wearing a soft knit sweater"),
    (r"\báo khoác mỏng\b|\bcardigan\b", "wearing a casual knit cardigan"),
    (r"\báo sơ mi\b", "wearing a casual cotton button-down shirt"),
    (r"\báo thun\b|\báo phông\b", "wearing a plain cotton t-shirt"),
    (r"\báo polo\b", "wearing a casual polo shirt"),
    (r"\báo hoodie\b|\bhoodie\b", "wearing a relaxed hoodie"),
    (r"\btạp dề\b", "and a simple kitchen apron"),
    (r"\bmàu trắng kem\b|\bmàu kem\b|\bbeige\b|\bmàu be\b", "in warm cream-beige"),
    (r"\bmàu trắng\b|\btrắng\b", "in clean white"),
    (r"\bmàu đen\b|\bđen\b", "in matte black"),
    (r"\bmàu xám\b|\bxám\b", "in heather grey"),
    (r"\bmàu hồng\b|\bhồng pastel\b", "in dusty rose pink"),
    (r"\bmàu xanh rêu\b|\bxanh lá\b", "in sage green"),
    (r"\bmàu xanh dương\b|\bxanh pastel\b|\bxanh\b", "in soft slate blue"),
    (r"\bmàu nâu\b|\bnâu\b", "in warm caramel brown"),
    (r"\bmàu vàng\b|\bvàng bơ\b", "in butter yellow"),
    (r"\bmàu tím\b|\btím\b", "in pastel lavender"),
)


def _has_non_ascii_letters(text: str) -> bool:
    return any(ord(ch) > 127 and unicodedata.category(ch).startswith("L") for ch in text or "")


def synthesize_persona(seed_bytes: bytes, gender: Optional[str] = None) -> dict[str, str]:
    """Procedurally build a unique persona from combinatorial trait tables."""
    b = seed_bytes if len(seed_bytes) >= 8 else hashlib.sha256(seed_bytes).digest()
    is_female = (b[0] % 3 != 0) if gender is None else (gender.lower() in ("f", "female", "woman", "girl", "nu", "nữ"))
    if is_female:
        age = 21 + (b[1] % 17)  # 21..37
        noun = "Vietnamese woman"
        hair_intro, hair_short = _FEMALE_HAIRSTYLES[b[2] % len(_FEMALE_HAIRSTYLES)]
    else:
        age = 22 + (b[1] % 18)  # 22..39
        noun = "Vietnamese man"
        hair_intro, hair_short = _MALE_HAIRSTYLES[b[2] % len(_MALE_HAIRSTYLES)]

    face = _FACE_TRAITS[b[3] % len(_FACE_TRAITS)]
    outfit_intro, outfit_short = _OUTFITS[b[4] % len(_OUTFITS)]
    return {
        "intro": f"an ordinary {age}-year-old {noun} with {hair_intro}, {face}, wearing {outfit_intro}",
        "cont": f"the same {age}-year-old {noun} with {hair_short} and {outfit_short}",
    }


def parse_custom_persona(raw: str, category: str = "GENERAL_LIFESTYLE", seed: Optional[str] = None) -> dict[str, str]:
    """Convert a user-supplied ``--persona`` string (preset keyword, index, Vietnamese, or English) into ``{intro, cont}``."""
    cleaned = (raw or "").strip()
    low = cleaned.lower()
    pool = _PERSONA_POOLS.get(category, _PERSONA_POOLS["GENERAL_LIFESTYLE"])

    # 1. Numeric index into category pool (e.g. --persona 0 .. 9)
    if low.isdigit():
        return dict(pool[int(low) % len(pool)])

    # 2. Random / procedural keywords
    if low in ("random", "ngẫu nhiên", "auto_random"):
        return synthesize_persona(secrets.token_bytes(8))
    if low.startswith("random:"):
        return synthesize_persona(hashlib.sha256(low.encode("utf-8")).digest())
    if low in ("male", "nam", "man"):
        base_seed = hashlib.sha256((seed or "male").encode("utf-8")).digest()
        return synthesize_persona(base_seed, gender="male")
    if low in ("female", "nu", "nữ", "woman"):
        base_seed = hashlib.sha256((seed or "female").encode("utf-8")).digest()
        return synthesize_persona(base_seed, gender="female")

    # 3. Free-form Vietnamese or mixed Vietnamese/English prompt -> translate to clean English
    if _has_non_ascii_letters(cleaned):
        text = unicodedata.normalize("NFC", cleaned)
        for pattern, repl in _VI_TO_EN_RULES:
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        # Strip any remaining Vietnamese diacritic words so Flow never renders packaging text
        ascii_words = [
            w for w in re.split(r"[\s,;]+", text)
            if w and not _has_non_ascii_letters(w)
        ]
        desc = " ".join(ascii_words).strip()
        desc = re.sub(r"\b(Vietnamese (?:woman|man|person))\s+(\d{2}-year-old)\b", r"\2 \1", desc)
        if "Vietnamese" not in desc:
            desc = f"Vietnamese person {desc}".strip()
        if not re.search(r"\b\d{2}-year-old\b", desc):
            desc = f"26-year-old {desc}"
        if "wearing" not in desc:
            desc = f"{desc}, wearing a casual cotton home shirt"
        intro = f"an ordinary {desc}"
    else:
        # 4. Already English custom prompt
        desc = cleaned.rstrip(".")
        if desc.lower().startswith(("a ", "an ")):
            intro = desc
            desc = re.sub(r"^(?:an?\s+)?(?:ordinary\s+)?", "", desc, flags=re.IGNORECASE)
        else:
            intro = f"an ordinary {desc}"

    # Build a concise continuation phrase ("the same ...")
    short_clauses = [c.strip() for c in desc.split(",") if c.strip()]
    cont_body = ", ".join(short_clauses[:2]) if len(short_clauses) > 1 else short_clauses[0]
    cont_body = re.sub(r"^(?:an?\s+)?(?:ordinary\s+)?(?:the\s+same\s+)?", "", cont_body, flags=re.IGNORECASE)
    return {
        "intro": intro,
        "cont": f"the same {cont_body}",
    }


def character_persona(
    category: str,
    seed: Optional[str] = None,
    custom_persona: Optional[str] = None,
) -> dict[str, str]:
    """
    Return a consistent physical character persona (``intro``, ``cont``) for ``category``.

    - If ``custom_persona`` is provided (via ``--persona``), parses presets, random synthesis,
      or free-form Vietnamese/English character descriptions.
    - Otherwise, when ``seed`` (e.g. ``clean_title``) is provided, deterministically selects
      from the 10-persona category pool so different products get distinct faces and outfits
      while all scenes of the same product share the exact same character.
    """
    if custom_persona and custom_persona.strip():
        return parse_custom_persona(custom_persona, category=category, seed=seed)

    pool = _PERSONA_POOLS.get(category, _PERSONA_POOLS["GENERAL_LIFESTYLE"])
    if not seed:
        return dict(pool[0])
    digest = hashlib.sha256(seed.strip().lower().encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "big") % len(pool)
    return dict(pool[idx])


__all__ = ["character_persona", "parse_custom_persona", "synthesize_persona"]
