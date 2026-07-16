"""
SafeX Solutions Chatbot - Module 1: Core NLP / FAQ Matching Engine
--------------------------------------------------------------------
This is the "brain" of the chatbot. It loads a bilingual (English + Roman Urdu)
FAQ dataset (now 45 FAQs, each with an English question, a primary Roman Urdu
question, and 1-2 extra Roman Urdu phrasing variants for stronger matching),
and for any incoming user question, finds the closest matching FAQ using
TF-IDF vectorization + Cosine Similarity, and returns the best answer along
with a confidence score (0-1).

This module is designed to be a clean foundation for Module 2 (bilingual /
language detection logic) and Module 3 (chat UI / integration layer) to be
built on top of.

Author: Sania Shaheen
"""

import json
import re
import csv
from dataclasses import dataclass, field
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

@dataclass
class MatchResult:
    """Represents the chatbot's best-matching answer for a user query."""
    answer: str
    confidence: float
    matched_question: str
    matched_language: str          # "en" or "ur" (which version matched best)
    category: str
    faq_id: int
    is_confident: bool             # True if confidence passes the threshold


# --------------------------------------------------------------------------
# Text normalization
# --------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Lowercases, strips punctuation/extra whitespace so that TF-IDF matches
    are not thrown off by casing or punctuation differences. Works fine for
    both English and Roman Urdu since both use the Latin alphabet.
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # collapse whitespace
    return text.strip()


# --------------------------------------------------------------------------
# Core Engine
# --------------------------------------------------------------------------

class FAQMatchingEngine:
    """
    TF-IDF + Cosine Similarity based FAQ matching engine.

    Both the English and Roman Urdu phrasing of every FAQ question are added
    to the same searchable corpus. This means a user can type in English,
    Roman Urdu, or a mix of both, and still get matched to the right FAQ,
    without needing a separate translation step. Module 2 can later use the
    `matched_language` field to decide which language to reply in.
    """

    CONFIDENCE_THRESHOLD = 0.25  # below this, treat the bot as "unsure"

    def __init__(self, faq_path: str):
        self.faq_path = faq_path
        self.faqs: List[dict] = []
        self.corpus: List[str] = []       # normalized text used for matching
        self.corpus_meta: List[dict] = [] # parallel metadata for each corpus entry
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        self._load_faqs()
        self._build_index()

    # ---------------------------------------------------------------
    def _load_faqs(self):
        if self.faq_path.endswith(".json"):
            with open(self.faq_path, encoding="utf-8") as f:
                self.faqs = json.load(f)
        elif self.faq_path.endswith(".csv"):
            with open(self.faq_path, encoding="utf-8") as f:
                self.faqs = list(csv.DictReader(f))
        else:
            raise ValueError("faq_path must be a .json or .csv file")

    # ---------------------------------------------------------------
    def _build_index(self):
        """
        Builds one TF-IDF corpus entry per language variant of each FAQ,
        so English queries match English phrasing and Roman Urdu queries
        match Roman Urdu phrasing, while both point back to the same answer.
        """
        self.corpus = []
        self.corpus_meta = []

        for faq in self.faqs:
            faq_id = int(faq["id"])
            category = faq["category"]
            answer = faq["answer"]

            en_q = faq.get("question_en", "")
            ur_q = faq.get("question_ur", "")

            if en_q:
                self.corpus.append(normalize_text(en_q))
                self.corpus_meta.append({
                    "faq_id": faq_id,
                    "question": en_q,
                    "language": "en",
                    "category": category,
                    "answer": answer,
                })
            if ur_q:
                self.corpus.append(normalize_text(ur_q))
                self.corpus_meta.append({
                    "faq_id": faq_id,
                    "question": ur_q,
                    "language": "ur",
                    "category": category,
                    "answer": answer,
                })

            # Extra Roman Urdu phrasing variations (different word order,
            # spelling, or a more casual/regional way of asking the same
            # question). Each variant is indexed as its own searchable entry
            # pointing back to the same answer, which is what makes matching
            # more robust to how differently people actually type Roman Urdu.
            ur_variants = faq.get("question_ur_variants")
            if ur_variants:
                if isinstance(ur_variants, str):
                    ur_variants = [v.strip() for v in ur_variants.split(";") if v.strip()]
                for variant_q in ur_variants:
                    self.corpus.append(normalize_text(variant_q))
                    self.corpus_meta.append({
                        "faq_id": faq_id,
                        "question": ur_q or variant_q,
                        "language": "ur",
                        "category": category,
                        "answer": answer,
                    })

            # Optional extra keyword synonyms (e.g. "pricing", "cost", "quote")
            # widen recall for common alternate phrasings without cluttering
            # the main question text shown back to the user.
            keywords = faq.get("keywords")
            if keywords:
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(";") if k.strip()]
                if keywords:
                    self.corpus.append(normalize_text(" ".join(keywords)))
                    self.corpus_meta.append({
                        "faq_id": faq_id,
                        "question": en_q or ur_q,
                        "language": "en",
                        "category": category,
                        "answer": answer,
                    })

        # ngram_range=(1,2) lets the vectorizer capture short phrases
        # (e.g. "web development", "kitna paisa") not just single words.
        # English stopwords are removed so generic words like "help", "with",
        # "do", "you" don't drown out the meaningful keywords (works fine for
        # Roman Urdu too, since those words aren't in the English stopword list
        # and simply get treated as regular tokens).
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            stop_words="english",
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    # ---------------------------------------------------------------
    def get_best_answer(self, user_question: str, top_n: int = 1) -> MatchResult:
        """
        Main entry point.

        Input:  user_question (str) - raw text typed by the user
        Output: MatchResult with best matching answer + confidence score (0-1)
        """
        if not user_question or not user_question.strip():
            return MatchResult(
                answer="Please type a question so I can help you.",
                confidence=0.0,
                matched_question="",
                matched_language="en",
                category="N/A",
                faq_id=-1,
                is_confident=False,
            )

        query_norm = normalize_text(user_question)
        query_vec = self.vectorizer.transform([query_norm])

        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])
        best_meta = self.corpus_meta[best_idx]

        result = MatchResult(
            answer=best_meta["answer"],
            confidence=round(best_score, 4),
            matched_question=best_meta["question"],
            matched_language=best_meta["language"],
            category=best_meta["category"],
            faq_id=best_meta["faq_id"],
            is_confident=best_score >= self.CONFIDENCE_THRESHOLD,
        )
        return result

    # ---------------------------------------------------------------
    def get_top_matches(self, user_question: str, k: int = 3) -> List[MatchResult]:
        """
        Returns the top-k matches instead of just the best one. Useful for
        debugging matching quality, or for Module 3 to show 'did you mean'
        suggestions when confidence is low.
        """
        query_norm = normalize_text(user_question)
        query_vec = self.vectorizer.transform([query_norm])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = similarities.argsort()[::-1][:k]
        results = []
        seen_faq_ids = set()
        for idx in top_indices:
            meta = self.corpus_meta[idx]
            if meta["faq_id"] in seen_faq_ids:
                continue  # avoid showing the same FAQ twice (en + ur dupes)
            seen_faq_ids.add(meta["faq_id"])
            results.append(MatchResult(
                answer=meta["answer"],
                confidence=round(float(similarities[idx]), 4),
                matched_question=meta["question"],
                matched_language=meta["language"],
                category=meta["category"],
                faq_id=meta["faq_id"],
                is_confident=similarities[idx] >= self.CONFIDENCE_THRESHOLD,
            ))
        return results

    # ---------------------------------------------------------------
    def answer(self, user_question: str) -> dict:
        """
        Convenience wrapper matching the exact spec from the task brief:
        Input: user's question (str)
        Output: dict with best matching answer + confidence score
        """
        result = self.get_best_answer(user_question)
        fallback_msg = (
            "Sorry, I'm not fully sure I understood that. Could you rephrase, "
            "or contact our team directly at contact@safexsolutions.com / "
            "+92 327 5781580?"
        )
        return {
            "question": user_question,
            "answer": result.answer if result.is_confident else fallback_msg,
            "confidence": result.confidence,
            "matched_faq_question": result.matched_question,
            "category": result.category,
            "faq_id": result.faq_id,
        }


# --------------------------------------------------------------------------
# Quick manual test when running this file directly
# --------------------------------------------------------------------------
if __name__ == "__main__":
    engine = FAQMatchingEngine("faqs.json")

    test_questions = [
        "What services do you guys offer?",
        "Aap web development karte hain?",
        "how much does it cost",
        "SafeX ka phone number kya hai",
        "do you make mobile apps",
        "trust ke baare mein bata do",
        "Bahar ke mulk ke clients ke liye bhi kaam karte hain aap?",
        "asdkjaslkdj random gibberish text",
    ]

    for q in test_questions:
        res = engine.answer(q)
        print("-" * 70)
        print(f"User: {q}")
        print(f"Bot : {res['answer']}")
        print(f"Confidence: {res['confidence']}  |  Matched FAQ: '{res['matched_faq_question']}'  |  Category: {res['category']}")
