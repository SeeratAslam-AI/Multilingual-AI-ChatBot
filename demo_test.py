"""
Quick demo / test harness for Module 1 - FAQ Matching Engine.
Run this file to see the engine answer a batch of sample questions
(English + Roman Urdu, including casual/regional phrasing variants
that are NOT verbatim in the dataset) with confidence scores.
"""

from chatbot_engine import FAQMatchingEngine

engine = FAQMatchingEngine("faqs.json")

sample_questions = [
    # English
    "What services does SafeX offer?",
    "Can you build me an online store?",
    "I need help with cybersecurity",
    "What's your email?",
    "Where are you located?",
    "Do you offer internships?",
    "What is your pricing?",
    "Do you work with clients outside Pakistan?",
    "Can I see your past projects?",

    # Roman Urdu - direct phrasing from the dataset
    "Aap log kya kaam karte hain",
    "Mujhe website chahiye kya bana sakte hain",
    "digital marketing ki service hai kya",
    "email address batao",
    "office kahan hai aapka",
    "job ya internship mil sakti hai kya",

    # Roman Urdu - casual / alternate spelling, NOT literally in the dataset,
    # to check that the added variants genuinely widen matching
    "price kitni hogi",
    "ap ka whatsapp number kya h",
    "kia ap log logo bhi bnate ho",
    "mera business dusray mulk mein bhi hai, kaam kar saktay ho?",
    "SDC mein admission kaise ho",
    "trust wala kaam kya hai",
]

print("=" * 80)
print("SAFEX SOLUTIONS CHATBOT - MODULE 1 DEMO (TF-IDF + Cosine Similarity)")
print(f"Dataset size: {len(engine.faqs)} FAQs")
print("=" * 80)

low_confidence_count = 0
for q in sample_questions:
    result = engine.answer(q)
    if result["confidence"] < engine.CONFIDENCE_THRESHOLD:
        low_confidence_count += 1
    print(f"\nUser Question   : {q}")
    print(f"Bot Answer      : {result['answer']}")
    print(f"Confidence      : {result['confidence']}")
    print(f"Matched FAQ     : {result['matched_faq_question']}")
    print(f"Category        : {result['category']}")
    print("-" * 80)

print(f"\n{len(sample_questions) - low_confidence_count}/{len(sample_questions)} questions answered with confidence >= {engine.CONFIDENCE_THRESHOLD}")
