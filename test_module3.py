from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Simulate a batch of real user interactions - deliberately repeating a
# few questions (in slightly different casing) so top-questions grouping
# has something meaningful to show, and including some fallback-worthy
# gibberish so the fallback list isn't empty.
simulated_chats = [
    "What services does SafeX offer?",
    "what services does safex offer?",
    "What services does SafeX offer?",
    "SafeX ki qeemat kya hai for a website?",
    "kitna paisa lagta hai website banwane ka",
    "Aap log kya kaam karte hain",
    "mujhe apka rabta number chahiye",
    "office kis waqt khulta hai",
    "Kya SafeX Solutions cybersecurity services deti hai?",
    "Cyber security ka kaam karte hain aap?",
    "Kya SafeX Solutions digital marketing ki services deti hai?",
    "Trust ke baare mein bata do",
    "asdkjaslkdj random gibberish text",
    "zzz123 blah blah nonsense",
]

print("Sending simulated chat requests...")
for msg in simulated_chats:
    r = client.post("/chat", json={"message": msg})
    assert r.status_code == 200, r.text
print(f"Sent {len(simulated_chats)} requests.\n")

print("=" * 70)
print("GET /analytics/summary")
print("=" * 70)
summary = client.get("/analytics/summary").json()
print("Total queries   :", summary["total_queries"])
print("Answered        :", summary["answered_count"])
print("Hedged          :", summary["hedged_count"])
print("Fallback        :", summary["fallback_count"])

print("\nTop questions:")
for q in summary["top_questions"]:
    print(f"  ({q['times_asked']}x) {q['question']}")

print("\nCategory interest:")
for c in summary["category_interest"]:
    print(f"  {c['category']}: {c['query_count']}")

print("\nFallback queries:")
for f in summary["fallback_queries"]:
    print(f"  [{f['detected_language']}] {f['user_question']}  (conf={f['confidence']})")
