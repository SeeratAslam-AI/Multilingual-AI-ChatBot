"""
SafeX Solutions Chatbot - Module 2 Part C: Response Manager
----------------------------------------------------------------------
Purpose: This is the "glue" module. It combines:
  1. Language detection      (language_detector.py)
  2. Roman Urdu normalization (urdu_normalizer.py)
  3. Module 1's FAQ matching  (chatbot_engine.py, built by Member 1)
  4. Confidence-based fallback handling (this file)

...into a single function that Module 3 (the chat UI) can call with
just the raw user message, and get back one final response string -
no need for Module 3 to know anything about language detection or
confidence thresholds internally.

FALLBACK THRESHOLD NOTE:
Module 1 already has its own internal CONFIDENCE_THRESHOLD (0.25) that
it uses to decide whether a matched FAQ is even relevant at all - below
that, Module 1 assumes we probably matched pure noise and won't even
surface the underlying answer.
Module 2's threshold (0.5, per this task's brief) sits ABOVE that: it's
a UX-level decision about whether the bot sounds fully confident or
hedges. So the two thresholds serve different purposes and are kept
separate (not just reusing Module 1's constant).
"""

from chatbot_engine import FAQMatchingEngine
from language_detector import detect_language
from urdu_normalizer import normalize_query

CONTACT_INFO = "contact@safexsolutions.com / +92 327 5781580"

# Module 2's own confidence threshold for hedged vs confident replies,
# as specified in the task brief (different from Module 1's internal
# 0.25 "is this even relevant" threshold).
FALLBACK_THRESHOLD = 0.5


class SafeXResponseManager:
    """
    Wraps Module 1's FAQMatchingEngine with bilingual handling and
    confidence-based fallback, per Module 2 spec.
    """

    def __init__(self, faq_path: str):
        self.engine = FAQMatchingEngine(faq_path)

    # ------------------------------------------------------------
    def get_response(self, user_message: str) -> dict:
        """
        Input : raw user message (English or Roman Urdu, possibly mixed)
        Output: dict with the final bot response string plus useful
                debug fields (detected language, normalized query,
                confidence score, matched FAQ id) so Module 3 can log
                or display extra info if it wants to.
        """
        if not user_message or not user_message.strip():
            return {
                "user_message": user_message,
                "detected_language": "en",
                "normalized_query": "",
                "confidence": 0.0,
                "faq_id": -1,
                "category": "N/A",
                "response_type": "fallback",
                "final_response": "Please type a question so I can help you.",
            }

        # Step 1: detect language
        detected_lang = detect_language(user_message)

        # Step 2: normalize only if Roman Urdu was detected - normalizing
        # pure English text is a harmless no-op anyway, but skipping it
        # keeps behavior explicit and easy to reason about/debug.
        if detected_lang == "ur":
            query_for_matching = normalize_query(user_message)
        else:
            query_for_matching = user_message

        # Step 3: send the (possibly normalized) query to Module 1
        match_result = self.engine.get_best_answer(query_for_matching)

        # Step 4: apply Module 2's confidence fallback logic
        final_response = self._build_final_response(match_result)

        return {
            "user_message": user_message,
            "detected_language": detected_lang,
            "normalized_query": query_for_matching,
            "confidence": match_result.confidence,
            "faq_id": match_result.faq_id,
            "category": match_result.category,
            "response_type": self._classify_response_type(match_result),
            "final_response": final_response,
        }

    # ------------------------------------------------------------
    def _classify_response_type(self, match_result) -> str:
        """
        Labels each interaction for Module 3's logging/analytics:
          - "answered": confident, direct answer (>= 0.5)
          - "hedged":   closest-match answer shown, but hedged (0.25-0.5)
          - "fallback": no relevant match at all (< 0.25)
        This mirrors _build_final_response's own tiering exactly, so the
        label always matches what the user actually saw.
        """
        if match_result.confidence >= FALLBACK_THRESHOLD:
            return "answered"
        if match_result.is_confident:
            return "hedged"
        return "fallback"

    # ------------------------------------------------------------
    def _build_final_response(self, match_result) -> str:
        """
        Three-tier confidence handling:

        1. confidence >= 0.5 (FALLBACK_THRESHOLD)
           -> answer directly and confidently.

        2. Module1's own relevance floor <= confidence < 0.5
           -> hedge, but still SHOW the closest matched answer (per brief).
           We reuse Module 1's `is_confident` flag (its 0.25 threshold) as
           the floor here, since that already tells us "this match is at
           least plausibly relevant, just not a strong match".

        3. confidence < Module1's relevance floor (e.g. gibberish input)
           -> do NOT show a closest answer at all, since at this point the
           "closest match" is essentially noise and showing it makes the
           bot look like it's guessing randomly. Just say we didn't
           understand, and point to contact info.
        """
        if match_result.confidence >= FALLBACK_THRESHOLD:
            return match_result.answer

        if match_result.is_confident:
            return (
                "Mujhe pura yaqeen nahi, lekin ye closest info hai: "
                f"{match_result.answer} "
                f"Agar aapko aur madad chahiye to humari team se contact karein: {CONTACT_INFO}"
            )

        return (
            "Mujhe maaf kijiye, main ye samajh nahi payi. Barah-e-meherbani thora "
            "clear kar ke dobara poochein, ya humari team se seedha contact karein: "
            f"{CONTACT_INFO}"
        )
