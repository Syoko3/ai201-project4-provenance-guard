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


if __name__ == "__main__":
    main()
