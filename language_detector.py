"""
SafeX Solutions Chatbot - Module 2 Part A: Language Detection
----------------------------------------------------------------
Purpose: Given a raw user message, decide if it's written in English
or Roman Urdu, using a simple marker-word approach (as per the task
brief): common Roman Urdu function words like "kya", "hai", "aap",
"kaise", "chahiye" etc. If the message contains one or more of these,
we classify it as Roman Urdu. Otherwise, English.

This is intentionally simple (word-list based) rather than a full
statistical language model, because:
- Roman Urdu doesn't have its own script (it borrows Latin letters),
  so language ID models trained on real Urdu script don't apply well.
- A user's message is often a MIX of both (e.g. "aap web development
  karte hain?") - so instead of a strict binary classifier, we check
  which language's "signal words" are present and let Roman Urdu
  words act as a strong signal even in a mostly-English-looking sentence.
"""

import re

# Common Roman Urdu function/marker words. These are words that are
# distinctly Roman Urdu and don't collide with common English words -
# this avoids false positives on plain English sentences.
ROMAN_URDU_MARKERS = {
    "kya", "hai", "hain", "aap", "ap", "kaise", "kahan", "kab", "kyun",
    "kyu", "kitna", "kitne", "kitni", "karte", "karti", "karo", "karein",
    "chahiye", "mujhe", "humein", "hamein", "humko", "mera", "meri",
    "mere", "apka", "apki", "apke", "uska", "uski", "iska", "iski",
    "bhi", "nahi", "nhi", "sakte", "sakta", "sakti", "deti", "deta",
    "milta", "milti", "milta hai", "wala", "wali", "walay", "kaam",
    "paisa", "paise", "rupay", "qeemat", "rabta", "batao", "batayein",
    "dikhao", "dikha", "krna", "krte", "krti", "hoon", "tha", "thi",
    "thay", "mulk", "bahar", "andar", "yaqeen", "madad", "pura",
    "asal", "cheez", "dar", "saath", "liye", "waqt", "bata",
    "ke", "ki", "ka", "mein", "se", "ko", "par", "aur", "ho",
}


def normalize_for_detection(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_language(text: str) -> str:
    """
    Returns "ur" if the message shows Roman Urdu markers, else "en".

    Approach: tokenize the (normalized) message, count how many tokens
    are Roman Urdu marker words. If at least one marker word is found,
    classify the message as Roman Urdu - because in practice, SafeX
    users write in mixed Roman Urdu/English, and even a single strong
    marker word ("kya", "hai", "aap"...) is a reliable signal that the
    reply should be framed in Roman Urdu, or that normalization should
    be attempted before matching.
    """
    if not text or not text.strip():
        return "en"

    normalized = normalize_for_detection(text)
    tokens = normalized.split()

    marker_hits = sum(1 for tok in tokens if tok in ROMAN_URDU_MARKERS)

    return "ur" if marker_hits >= 1 else "en"