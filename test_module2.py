from response_manager import SafeXResponseManager

manager = SafeXResponseManager("faqs.json")

sample_questions = [
    # Original demo batch
    "What services does SafeX offer?",
    "SafeX ki qeemat kya hai for a website?",
    "Aap log kya kaam karte hain",
    "mujhe apka rabta number chahiye",
    "Bahar ke mulk ke clients ke liye bhi kaam karte hain aap?",
    "office kis waqt khulta hai",
    "kitna paisa lagta hai website banwane ka",
    "Can I see your past projects?",
    "asdkjaslkdj random gibberish text",

    # New batch - added after extending urdu_normalizer.py based on the
    # real 45-FAQ dataset (timeline, revisions, mission, trust, hiring,
    # branding). These specifically test the pricing-vs-timeline
    # disambiguation fix and the other gaps found in faqs.csv.
    "Ek project complete hone mein kitna time lagta hai",
    "Design mein changes kitni dafa free hote hain",
    "SafeX ka maqsad kya hai",
    "Trust ke baare mein bata do",
    "Aap log staff hire kar rahe hain?",
    "Job mil sakti hai kya SafeX mein?",
    "Logo aur branding banwani hai, kya aap karte hain?",
]

low = 0
for q in sample_questions:
    r = manager.get_response(q)
    if r["confidence"] < 0.5:
        low += 1
    print("=" * 90)
    print(f"User            : {q}")
    print(f"Detected Lang   : {r['detected_language']}")
    print(f"Normalized Query: {r['normalized_query']}")
    print(f"Confidence      : {r['confidence']}")
    print(f"Final Response  : {r['final_response']}")

print("=" * 90)
print(f"\n{len(sample_questions) - low}/{len(sample_questions)} answered confidently (>= 0.5)")