"""
SafeX Solutions Chatbot - Module 2 Part B: Roman Urdu Normalization
----------------------------------------------------------------------
Purpose: Convert common Roman Urdu words/phrases into their English
equivalents BEFORE sending the query to Module 1's matching engine.

Why this matters even though Module 1 already indexes Roman Urdu
questions directly: Module 1's TF-IDF only knows the exact Roman Urdu
phrasing already present in faqs.json (question_ur + question_ur_variants).
If a user types a Roman Urdu word/synonym that isn't in the dataset at
all (e.g. "qeemat" instead of "price", or "rabta" instead of "contact"),
TF-IDF has literally never seen that token, so it can't match it to
anything. Normalizing these into their English equivalents means the
query lines up with the English side of the dataset (question_en),
which widens recall significantly.

The dictionary below is built by going through Member 1's FAQ dataset
(faqs.json) topic by topic - service names, contact info, pricing,
location, hours, portfolio, cybersecurity, digital marketing, mobile
apps, international clients, internships, blog - and mapping the
Roman Urdu ways SafeX's users are likely to ask about each, to the
matching English keyword(s) used in question_en.

NOTE for the team: this dictionary should be extended any time Member 1
adds a new FAQ category/keyword, so it always stays in sync.
"""

import re

# --------------------------------------------------------------------
# PHRASE-LEVEL map: multi-word Roman Urdu phrases -> English equivalent.
# Checked FIRST, longest phrase first, before single-word replacement,
# so more specific/contextual matches win over generic word-by-word ones.
# --------------------------------------------------------------------
PHRASE_MAP = {
    "kya deti hai": "what does it offer",
    "kya karti hai": "what does it do",
    "kya offer karti hai": "what does it offer",
    "kya karte hain": "what do you do",
    "kitne ka": "price of",
    "kitne ki": "price of",
    "kitna paisa": "how much price",
    "kitna kharcha": "how much cost",
    "kaam kaise karte hain": "how does it work",
    "kaam kar sakte ho": "can you work",
    "kaam kar saktay ho": "can you work",
    "rabta kaise karoon": "how can i contact",
    "rabta kaise karein": "how can i contact",
    "contact kaise karoon": "how can i contact",
    "office kahan hai": "where is the office located",
    "office kis waqt khulta hai": "what are the working hours",
    "khulne ka waqt": "working hours",
    "band hone ka waqt": "closing hours",
    "dusray mulk": "other countries",
    "bahar ke mulk": "other countries",
    "mulk ke bahar": "outside the country",
    "job ya internship": "internship opportunity",
    "naukri mil sakti hai": "job opportunity",
    "free mein consultation": "free consultation",
    "pehli consultation": "first consultation",

    # pricing vs timeline disambiguation - kept as specific, longer phrases
    # (checked before single words) so "lagta hai" isn't blindly translated
    # to "cost" in a timeline question or vice versa.
    "kitna paisa lagta hai": "how much does the price cost",
    "kitni paisa lagti hai": "how much does the price cost",
    "kitna kharcha ayega": "how much will the cost be",
    "rate kya hain": "what are the price rates",
    "kitna time lagta hai": "how much time does the project take",
    "kitna waqt lagta hai": "how much time does the project take",
    "kitne dinon mein": "in how many days is it ready",
    "kitne din mein": "in how many days is it ready",

    # revisions
    "kitni dafa": "how many times",
    "kitni martaba": "how many times",
    "dafa free": "times free",

    # mission / trust
    "maqsad kya hai": "what is the mission",
    "baare mein bata do": "tell me about",

    # hiring
    "staff hire": "hiring staff",
    "job mil sakti hai": "is a job available",
}

# --------------------------------------------------------------------
# WORD_MAP additions
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# WORD-LEVEL map: single Roman Urdu words -> English equivalent.
# Applied after phrase-level replacement, on remaining tokens.
# --------------------------------------------------------------------
WORD_MAP = {
    # pricing / quote
    "qeemat": "price",
    "qimat": "price",
    "daam": "price",
    "paisa": "price",
    "paise": "price",
    "kharcha": "cost",
    "rate": "price",

    # services / general
    "kaam": "work services",
    "khidmat": "services",
    "khidmaat": "services",

    # company / identity
    "cheez": "thing",
    "asal": "actually",

    # contact
    "rabta": "contact",
    "sampark": "contact",
    "batao": "tell me",
    "batayein": "tell me",

    # location / hours
    "jaga": "location",
    "waqt": "time",

    # portfolio
    "dikhao": "show",
    "dikha": "show",
    "namoona": "sample",

    # cybersecurity
    "hifazat": "security",
    "tahaffuz": "protection",

    # digital marketing
    "tashheer": "marketing advertising",
    "mashoori": "promotion",

    # mobile / web
    "banwani": "build",
    "banwana": "build",
    "banate": "build",
    "banati": "build",

    # international
    "mulk": "country",
    "bahar": "abroad",
    "andar": "within",

    # internships
    "naukri": "job",
    "sikhna": "learn training",

    # trust / confidence
    "yaqeen": "trust confidence",
    "bharosa": "trust",

    # mission
    "maqsad": "mission purpose",

    # revisions / counts
    "dafa": "times",
    "martaba": "times",

    # timeline
    "dinon": "days",

    # build / make (logo, content, etc.)
    "banana": "build make",
    "bananay": "to build make",

    # availability
    "milta": "available",
    "milti": "available",
}


def _build_phrase_pattern():
    # Sort longest-first so "kya offer karti hai" matches before "kya".
    phrases = sorted(PHRASE_MAP.keys(), key=len, reverse=True)
    escaped = [re.escape(p) for p in phrases]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b")


_PHRASE_PATTERN = _build_phrase_pattern() if PHRASE_MAP else None


def normalize_query(text: str) -> str:
    """
    Converts Roman Urdu words/phrases in `text` into their English
    equivalents using PHRASE_MAP then WORD_MAP. Words/phrases not found
    in either map are left untouched (so English text passes through
    unchanged, and Roman Urdu words already covered by Module 1's own
    dataset - e.g. "hai", "kya" - are also left as-is, since Module 1
    already understands those directly).
    """
    if not text:
        return text

    working = text.lower()

    # Step 1: phrase-level replacement
    if _PHRASE_PATTERN:
        working = _PHRASE_PATTERN.sub(lambda m: PHRASE_MAP[m.group(0)], working)

    # Step 2: word-level replacement
    tokens = working.split()
    replaced_tokens = [WORD_MAP.get(tok, tok) for tok in tokens]
    working = " ".join(replaced_tokens)

    return working