"""Phone-footage realism layer applied to every Flow video prompt just before submission.

Ad templates (and storyboards saved by older versions) describe *what* happens; this
module makes the model render it the way a regular person's phone would record it:
plain wording, one handheld camera, real-world physics, room sound, and an explicit
list of AI tells to avoid. It is idempotent, so a finalized prompt can be finalized again.
"""
from __future__ import annotations

import logging
import re
import unicodedata

from tools.common.archetypes import ProductArchetype, resolve_product_archetype

logger = logging.getLogger(__name__)

PHONE_HEADER = (
    "Vertical 9:16 smartphone video, filmed handheld by a regular person, "
    "natural real-time speed, phone auto-exposure, slight focus breathing."
)
CAMERA_HANDHELD = "Camera: handheld phone at chest height, mostly steady with slight natural hand shake, no zoom, no orbit, no dolly, no gimbal glide."
CAMERA_ABOVE = "Camera: phone held above the surface looking down, small natural hand sway, no zoom, no orbit."
PRODUCT_NOTE = (
    "Product: exactly the item in the reference photo, same colour, material, shape, lid and handles; "
    "ignore any text, logos or banners printed on that photo."
)
HUMAN_NOTE = "Real person: natural skin texture with pores, relaxed unposed expression, not talking."
AUDIO = "Audio: real room tone and the natural handling sounds of the objects only, no music, no voice, no narration."
AVOID = (
    "Avoid: on-screen text, letters, logos, brand names, price tags, watermarks, subtitles, app UI, "
    "slow motion, floating or gliding camera, glossy CGI look, plastic skin, extra or merged fingers, "
    "objects morphing or appearing from nowhere."
)
_TAIL_PREFIXES = ("Product:", "Camera:", "Real person:", "Audio:", "Avoid:")

_OVERHEAD_RE = re.compile(r"\b(top-down|overhead|flat-lay|from above|bird's-eye)\b", re.IGNORECASE)
_NOT_TALKING_RE = re.compile(r"\b(no speaking|no talking|not talking|no dialogue)\b", re.IGNORECASE)

# (pattern, replacement) applied in order. Studio/cinema vocabulary pulls Omni toward a
# glossy stock-ad look; "instant" physics and named defects are classic AI tells.
_REWRITES: tuple[tuple[str, str], ...] = (
    # Old openers and camera-spec boilerplate.
    (r"\bVertical 9:16\b,?\s*", ""),
    (r"\bauthentic mobile video shot on iPhone[^.]*\.\s*", ""),
    (r"\bauthentic fast-paced commercial ad video\.\s*", ""),
    (r"\b(?:RAW\s+)?cinematic video\.\s*", ""),
    (r"\bRAW\b\s*", ""),
    (r"\b(?:shot on |sharp )?35mm lens\b[,.]?\s*", ""),
    (r"\b60\s?fps\b[^,.]*,?\s*", ""),
    (r"\b(?:crisp |sharp )?4K(?: resolution| detail| textures)?\b[,.]?\s*", ""),
    (r"\b(?:shallow|cinematic) depth of field\b[,.]?\s*", ""),
    # Studio lighting -> what a living room actually has.
    (r"(?:\b(?:premium|crisp|dramatic|soft|modern|creative)\s+)*(?:\b(?:texture|cinematic|commercial|studio|food|tech|fashion|B-roll)\s+)+lighting\b", "ordinary indoor daylight"),
    (r"\b(?:premium\s+)?(?:fashion\s+|tech\s+)?(?:real-time\s+)?commercial (?:look|B-roll)\b[,.]?\s*", ""),
    (r"\bB-roll\b,?\s*", ""),
    (r"\bgolden hour sunlight\b", "late afternoon window light"),
    (r"\bin dynamic light\b", ""),
    # Impossible or edited-looking motion.
    (r"\b(?:fast-forward|time-?lapse)\b[^,.]*[,.]?\s*", ""),
    (r"\binstantly\b", "gradually"),
    (r"\b(?:in|within) (?:one|a single) second\b", "in a few seconds"),
    (r"(?:,\s*)?\b(?:effortless(?:ly)?|heroic|epic)\b(?:,(?=\s))?\s*", " "),
    # Naming a defect primes it; the Avoid line covers fingers.
    (r",?\s*\b(?:with\s+)?strictly(?: exactly)? 5 fingers\b", ""),
    # Frozen grins and posed eye contact.
    (r"\bmouth closed,?\s*", ""),
    (r"\blooks directly at (?:the )?camera\b", "glances briefly toward the camera"),
    (r"\blooking directly at (?:the )?camera\b", "glancing briefly toward the camera"),
    (r"\blook directly at (?:the )?camera\b", "glance briefly toward the camera"),
    (r"\bbeaming,?\s*", ""),
    (r"\b(?:subtle |soft )?radiant smile\b", "small relaxed smile"),
    # Showroom adjectives.
    (r"\bperfectly spotless\b", "clean"),
    (r"\bspotless(?:ly)?\b", "clean"),
    (r"\bimmaculate\b", "tidy"),
    (r"\bflawless(?:ly)?\b", "neat"),
    (r"(?:,\s*)?\b(?:cinematic|dramatic|premium|aesthetic|sleek|elegant|stylish|chic|stunning|gorgeous|beautiful|luxurious|perfectly|perfect)\b(?:,(?=\s))?\s*", " "),
)
_COMPILED = tuple((re.compile(p, re.IGNORECASE), r) for p, r in _REWRITES)


def _tidy(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*(?=[.;])", "", text)  # ", ." -> "."
    text = re.sub(r"([.;])\s*[,.;]+", r"\1", text)  # ". ," / ".." -> "."
    text = re.sub(r"^[\s,.;]+", "", text)
    text = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text.strip()


def _strip_finalized(prompt: str) -> str:
    """Drop a header/tail added by an earlier finalize so the result stays idempotent."""
    if PHONE_HEADER not in prompt:
        return prompt
    body = prompt.replace(PHONE_HEADER, "")
    cuts = [i for i in (body.find(p) for p in _TAIL_PREFIXES) if i >= 0]
    return body[: min(cuts)] if cuts else body


def sanitize_prompt(prompt: str) -> str:
    """Rewrite glossy/impossible wording into plain, physically plausible language."""
    text = _strip_finalized(prompt or "")
    for pattern, repl in _COMPILED:
        text = pattern.sub(repl, text)
    return _tidy(text)


def has_vietnamese(text: str) -> bool:
    return any(ord(ch) > 127 and unicodedata.category(ch).startswith("L") for ch in text or "")


def finalize_video_prompt(prompt: str, *, faceless: bool, human: bool, product_reference: bool = False) -> str:
    """Return the prompt Flow should receive: phone header + cleaned body + camera/audio/avoid lines."""
    body = sanitize_prompt(prompt)
    if has_vietnamese(body):
        logger.warning("Prompt still contains Vietnamese text (Omni may render it as packaging text): %s", body[:80])
    parts = [PHONE_HEADER, body]
    if product_reference:
        parts.append(PRODUCT_NOTE)
    parts.append(CAMERA_ABOVE if _OVERHEAD_RE.search(body) else CAMERA_HANDHELD)
    if human and not faceless:
        parts.append(HUMAN_NOTE if not _NOT_TALKING_RE.search(body) else HUMAN_NOTE.replace(", not talking", ""))
    parts.extend((AUDIO, AVOID))
    return " ".join(p for p in parts if p)


# English noun for the product, so Vietnamese listing titles never reach a prompt
# (Omni tends to print prompt text onto packaging). First keyword match wins.
_ARCHETYPE_NOUNS: dict[ProductArchetype, str] = {
    ProductArchetype.VACUUM_CLEANER: "cordless handheld vacuum",
    ProductArchetype.COMPRESSION_STORAGE: "clear vacuum storage bag",
    ProductArchetype.APPAREL_BOTTOMS: "pair of trousers",
    ProductArchetype.SKINCARE: "small skincare bottle",
    ProductArchetype.STORAGE_DEVICE: "small metal USB flash drive",
    ProductArchetype.FOOTREST: "under-desk footrest",
}
_KEYWORD_NOUNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("bình giữ nhiệt", "ly giữ nhiệt", "cốc giữ nhiệt"), "insulated steel bottle"),
    (("giá đỡ điện thoại", "kẹp điện thoại"), "phone stand"),
    (("tai nghe",), "pair of wireless earbuds"),
    (("sạc dự phòng", "pin dự phòng"), "power bank"),
    (("củ sạc", "cáp sạc", "dây sạc"), "phone charger"),
    (("chuột",), "computer mouse"),
    (("bàn phím",), "keyboard"),
    (("đèn",), "small lamp"),
    (("quạt",), "small fan"),
    (("chảo",), "frying pan"),
    (("nồi",), "cooking pot"),
    (("dao",), "kitchen knife"),
    (("thớt",), "cutting board"),
    (("hộp đựng", "hộp cơm"), "food container"),
    (("son",), "lipstick"),
    (("kem chống nắng",), "sunscreen tube"),
    (("sữa rửa mặt",), "face cleanser tube"),
    (("máy massage", "súng massage", "massage"), "handheld massager"),
    (("thảm yoga", "thảm tập"), "yoga mat"),
    (("gối",), "pillow"),
    (("giày", "dép"), "pair of shoes"),
    (("túi xách", "balo", "ba lô"), "bag"),
    (("váy", "đầm"), "dress"),
    (("áo",), "top"),
    (("quần",), "pair of pants"),
)
_CATEGORY_NOUNS = {
    "BEAUTY_SKINCARE": "small skincare bottle",
    "KITCHEN_HOME": "kitchen tool",
    "FASHION_APPAREL": "piece of clothing",
    "TECH_GADGETS": "small gadget",
    "HEALTH_FITNESS": "fitness accessory",
}


# Words after which a listing title stops being what people call the product
# (brand, model codes, sizes, marketing tails).
_SPOKEN_STOP_RE = re.compile(r"(?<!\w)(?:size|sz|cao cấp|chính hãng|hàng|loại|model|bảo hành|bh|freeship)(?!\w)|\d", re.IGNORECASE)
SPOKEN_NAME_MAX_WORDS = 5


def spoken_name(title: str) -> str:
    """What a person would say out loud: "Nồi phủ sứ chống dính Elmich Olive EL-5532OV size 18,20cm" -> "nồi phủ sứ chống dính"."""
    title = (title or "").strip()
    stop = _SPOKEN_STOP_RE.search(title)
    words = (title[: stop.start()] if stop else title).split()
    # Drop a trailing brand/model word written with capitals ("Elmich", "Olive").
    while len(words) > 2 and words[-1][:1].isupper():
        words.pop()
    words = words[:SPOKEN_NAME_MAX_WORDS] or ["món", "này"]
    return " ".join(words).lower()


def feature_line(title: str, desc: str, tail: str = "") -> str:
    """Spoken feature sentence: "An toàn tuyệt đối nữa nha, từ nguyên liệu tự nhiên. <tail>"."""
    title = (title or "").strip().capitalize()
    desc = (desc or "").strip().rstrip(" .!;,:")
    if desc:
        desc = desc[:1].lower() + desc[1:]
    head = f"{title} nữa nha, {desc}." if title and desc else f"{title or desc}."
    return f"{head} {tail}".strip()


def product_noun(category: str, title: str) -> str:
    """Short plain English noun for the product (e.g. "clear vacuum storage bag")."""
    archetype = resolve_product_archetype(title)
    if archetype in _ARCHETYPE_NOUNS:
        return _ARCHETYPE_NOUNS[archetype]
    haystack = unicodedata.normalize("NFC", title or "").lower()
    for keywords, noun in _KEYWORD_NOUNS:
        if any(re.search(rf"(?:^|\s){re.escape(unicodedata.normalize('NFC', kw))}(?:\s|$)", haystack) for kw in keywords):
            return noun
    return _CATEGORY_NOUNS.get(str(category), "household item")


__all__ = ["feature_line", "finalize_video_prompt", "has_vietnamese", "product_noun", "sanitize_prompt", "spoken_name"]
