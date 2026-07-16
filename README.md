# SafeX Solutions Chatbot — Module 1: Core NLP / FAQ Matching Engine

This is the "brain" of the SafeX chatbot. It takes any user question (English or Roman
Urdu), compares it against a bilingual FAQ dataset, and returns the best-matching
answer along with a confidence score (0–1).

## Files

| File | Purpose |
|---|---|
| `faqs.json` | 45 FAQs, sourced from safexsolutions.com (Home, About, Services, Contact, Blog pages). Each entry has `id`, `category`, `question_en`, `question_ur` (primary Roman Urdu phrasing), `question_ur_variants` (1–3 extra Roman Urdu phrasing variations), `answer`, and an optional `keywords` list used only to widen matching. |
| `faqs.csv` | Same dataset in CSV format, for easy viewing in Excel/Sheets or for Module 2/3 to consume. |
| `chatbot_engine.py` | The matching engine itself (`FAQMatchingEngine` class). |
| `demo_test.py` | Run this to see the engine answer a batch of 21 sample English + Roman Urdu questions, including deliberately casual/spelling-variant Roman Urdu that isn't literally in the dataset. |
| `build_dataset.py` | The script used to (re)generate `faqs.json` / `faqs.csv` — edit this file to add or change FAQs rather than hand-editing the JSON. |

## How it works

1. **Dataset**: 45 FAQs across 15 categories — General/Company, Contact, Web
   Development, Cybersecurity, Cloud Solutions, AI Automation, Data Insights, Digital
   Marketing, Creative Media, Training/Skill Development, Pricing, Company/Mission,
   Company/Trust, Company/Careers, and Company/International — built from real content
   on the SafeX Solutions website. (The live Cybersecurity sub-page is still "under
   construction" on the site, so those FAQs were written from what *is* published on
   the Home/Services pages, not copied from a dedicated cybersecurity page. A few
   process-related FAQs — payment methods, revisions, timelines, NDAs — are answered
   generically with a pointer to contact the team directly, since those specifics
   aren't published on the website.)
2. **Bilingual indexing with variation**: for every FAQ, the English question, the
   primary Roman Urdu question, and 1–3 extra Roman Urdu phrasing variants (different
   word order, casual spelling, regional phrasing) are all added to one TF-IDF corpus,
   all pointing back to the same answer. This is what makes matching noticeably more
   robust — real users rarely type Roman Urdu the same way twice, so having multiple
   phrasings per question significantly widens what the engine can recognize. A
   handful of FAQs also carry short `keywords` (e.g. "pricing", "SDC", "mulk") to catch
   single-word or acronym-style queries.
3. **Matching**: `TfidfVectorizer` (unigrams + bigrams, English stopwords removed) +
   `cosine_similarity` scores the user's question against every FAQ variant (English +
   Urdu + variants + keywords). The highest-scoring match wins.
4. **Confidence score**: the cosine similarity score (0–1) is returned as-is.
   Anything ≥ 0.25 is treated as "confident"; below that, the bot returns a polite
   fallback message pointing the user to direct contact instead of guessing.

## Usage

```python
from chatbot_engine import FAQMatchingEngine

engine = FAQMatchingEngine("faqs.json")

result = engine.answer("Aap web development karte hain?")
# {
#   "question": "Aap web development karte hain?",
#   "answer": "Yes, SafeX Solutions builds responsive, fast-loading corporate websites...",
#   "confidence": 0.52,
#   "matched_faq_question": "Does SafeX Solutions offer web development services?",
#   "category": "Web Development",
#   "faq_id": 15
# }
```

Run `python3 demo_test.py` to see it in action on 21 sample questions (9 English, 6
direct Roman Urdu, 6 deliberately casual/alternate-spelling Roman Urdu).

## Testing results

On the current 21-question test set, 18/21 (86%) are answered with confidence ≥ 0.25.
The 3 misses are all extremely casual, heavily-abbreviated Roman Urdu (e.g. dropped
vowels like "bnate" instead of "banate") — a known limitation of a keyword/TF-IDF
matcher, documented below.

## Notes for Module 2 & Module 3

- `matched_language` (in `MatchResult` / via `get_best_answer`) tells you whether the
  English or Roman Urdu phrasing scored higher — useful for deciding what language to
  reply in.
- `get_top_matches(question, k=3)` returns the top-k distinct FAQ matches — handy for a
  "did you mean...?" suggestion UI when confidence is low.
- `CONFIDENCE_THRESHOLD` (currently `0.25`) is a class constant — tune it once real
  user queries start coming in.
- Since this is a **keyword/TF-IDF based** matcher (not semantic embeddings), it works
  best when Module 2/3 do light preprocessing (e.g. fixing common spelling shortcuts
  like "kia"→"kya", "h"→"hai") before calling `engine.answer()`. If deeper semantic
  understanding is needed later, this can be swapped for `sentence-transformers`
  without changing the `answer()` interface.
- To add more FAQs or Roman Urdu variants later, edit `build_dataset.py` and re-run it
  — this regenerates both `faqs.json` and `faqs.csv` consistently, instead of editing
  either file by hand.
