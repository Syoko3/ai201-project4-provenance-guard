"""
test_calibration.py

Calibration check for the confidence-scoring pipeline (Milestone 4).

Runs four deliberately chosen inputs — one clearly AI, one clearly human, and
two borderline cases — through both signals and the combined confidence score,
printing each signal separately so a miscalibrated signal is easy to spot.

Run:  python test_calibration.py
"""

from signals import groq_signal, stylometric_signal, combine_signals


def category(score: float) -> str:
    """Map a combined confidence score to its transparency-label category."""
    if score < 0.4:
        return "Human-Authored Content"
    if score < 0.7:
        return "Attribution Uncertain"
    return "AI-Generated Content"


# (label, expected_direction, text)
CASES = [
    (
        "Clearly AI-generated",
        "high (AI)",
        "Artificial intelligence represents a transformative paradigm shift in "
        "modern society. It is important to note that while the benefits of AI "
        "are numerous, it is equally essential to consider the ethical "
        "implications. Furthermore, stakeholders across various sectors must "
        "collaborate to ensure responsible deployment.",
    ),
    (
        "Clearly human-written",
        "low (human)",
        "ok so i finally tried that new ramen place downtown and honestly? "
        "underwhelming. the broth was fine but they put WAY too much sodium in "
        "it and i was thirsty for like three hours after. my friend got the "
        "spicy version and said it was better. probably won't go back unless "
        "someone drags me there",
    ),
    (
        "Borderline: formal human writing",
        "mid (uncertain)",
        "The relationship between monetary policy and asset price inflation has "
        "been extensively studied in the literature. Central banks face a "
        "fundamental tension between their mandate for price stability and the "
        "unintended consequences of prolonged low interest rates on equity and "
        "real estate valuations.",
    ),
    (
        "Borderline: lightly edited AI output",
        "mid (uncertain)",
        "I've been thinking a lot about remote work lately. There are genuine "
        "tradeoffs — flexibility and no commute on one side, isolation and "
        "blurred work-life boundaries on the other. Studies show productivity "
        "varies widely by individual and role type.",
    ),
]


def generate_audit_entries() -> None:
    """
    Drive the Flask app end-to-end to populate the audit log with 3 submissions
    (one per confidence band) and 1 appeal, then print the resulting entries.

    This produces structured audit-log evidence for the README. Each run appends
    to audit_log.jsonl, so delete that file first if you want a clean set.
    """
    import app  # imported here so the calibration check can run without Flask

    client = app.app.test_client()

    # Three submissions chosen to land in different confidence bands.
    submissions = [
        ("creator-human", CASES[1][2]),  # casual review -> Human-Authored
        ("creator-uncertain",
         "Honestly, I think sustainable living is more achievable than people "
         "assume. You dont have to overhaul everything at once. Small changes, "
         "such as reducing single-use plastics, can collectively make a "
         "meaningful difference over time."),  # lightly edited AI -> Uncertain
        ("creator-ai", CASES[0][2]),     # polished paragraph -> AI-Generated
    ]

    print("\n" + "=" * 70)
    print("AUDIT LOG: 3 submissions + 1 appeal")
    print("=" * 70)

    content_ids = []
    for creator_id, text in submissions:
        r = client.post("/submit", json={"text": text, "creator_id": creator_id}).get_json()
        content_ids.append(r["content_id"])
        print(f"submit  {creator_id:<18} conf={r['confidence']:<7} -> {r['label']['variant']}")

    # File an appeal on the last submission (the clearly-AI one).
    appealed_id = content_ids[-1]
    ap = client.post("/appeal", json={
        "content_id": appealed_id,
        "creator_reasoning": "I wrote this for a class essay; the formal tone is intentional.",
    }).get_json()
    print(f"appeal  content_id={appealed_id[:8]}... -> {ap['status']}")

    print("\n--- GET /log (newest first) ---")
    for e in client.get("/log").get_json()["entries"]:
        if e["type"] == "submission":
            print(f"  [submission] {e['content_id'][:8]}.. ts={e['timestamp']} "
                  f"attr='{e['attribution']}' conf={e['confidence']} "
                  f"llm={e['llm_score']} stylo={e['stylometric_score']} appealed={e['appealed']}")
        else:
            print(f"  [appeal]     {e['content_id'][:8]}.. ts={e['timestamp']} "
                  f"status={e['status']} reasoning='{e['appeal_reasoning'][:40]}...'")


def main() -> None:
    header = f"{'case':<38}{'GROQ':>6}{'STYLO':>7}{'CONF':>7}   category"
    print(header)
    print("-" * len(header))

    for label, expected, text in CASES:
        groq = groq_signal(text)
        stylo = stylometric_signal(text)
        combo = combine_signals(groq, stylo)
        conf = combo["combined_score"]

        print(f"{label:<38}{groq['score']:>6}{stylo['score']:>7}{conf:>7}   {category(conf)}")
        print(f"    expected: {expected}")
        print(f"    stylometric detail: {stylo['reasoning']}")
        print()

    generate_audit_entries()


if __name__ == "__main__":
    main()
