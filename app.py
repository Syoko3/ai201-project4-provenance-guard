"""
app.py

Provenance Guard — Flask API skeleton.

Implements the submission flow from planning.md:

    POST /submit
        -> Rate Limiter
        -> Detection Pipeline
              -> Groq            -> Score 1   (signals.groq_signal)        [M3]
              -> Stylometric     -> Score 2   (signals.stylometric_signal) [M4]
        -> Combined Confidence Score                                       [M4]
        -> Transparency Label                                             [M5]
        -> Audit Log (text, scores, label)
        -> Response (confidence score, label)

Milestone status:
    M3 (this file): Flask skeleton, rate-limited /submit wired to Signal 1,
                    structured audit log (JSONL, persisted) + GET /log.
    M4: second signal + confidence scoring (combine Score 1 and Score 2).
    M5: transparency label generation + POST /appeal.

Run:  python app.py   (serves on http://127.0.0.1:5000)
"""

import os
import json
import uuid
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from signals import groq_signal, stylometric_signal

app = Flask(__name__)


def _utc_timestamp() -> str:
    """Current UTC time as ISO 8601 with milliseconds and a 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _attribution_from_score(score: float) -> str:
    """
    Map a 0.0–1.0 AI-likelihood score (0.0 = human, 1.0 = AI) to a provisional
    attribution label, using the thresholds from planning.md's label table.

    M3 note: this runs on Signal 1 alone. In M4 it will run on the combined
    confidence score instead.
    """
    if score < 0.4:
        return "likely_human"
    if score < 0.7:
        return "uncertain"
    return "likely_ai"

# ── Rate limiting ────────────────────────────────────────────────────────────
# Keyed by client IP. Defaults are documented in the README; per-route limits
# are set with the @limiter.limit decorator below. Final values are tuned in M5.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"],
)

# ── Audit log ────────────────────────────────────────────────────────────────
# Every attribution decision and appeal is recorded as a structured entry, kept
# both in memory (for fast GET /log) and appended to an on-disk JSON Lines file
# so entries survive restarts and content_ids stay resolvable for appeals (M5).
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "audit_log.jsonl")
AUDIT_LOG = []


def _load_audit_log() -> None:
    """Load existing audit entries from disk into memory at startup."""
    if not os.path.exists(AUDIT_LOG_PATH):
        return
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                AUDIT_LOG.append(json.loads(line))


def _log_decision(entry: dict) -> None:
    """Append one structured entry to the audit log (memory + disk)."""
    AUDIT_LOG.append(entry)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


_load_audit_log()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute")  # per-route submission cap (reasoning in README)
def submit():
    """
    Accept a piece of text content and return its attribution result.

    Request JSON:
        { "text": "<content to analyze>", "creator_id": "<creator id>" }

    Response JSON (M3 shape — confidence/label filled in M4/M5):
        {
            "content_id":      int,
            "signals":         { "groq": {...}, "stylometric": {...} },
            "confidence_score": float | null,   # M4
            "label":           str | null,      # M5
            "status":          "Public"
        }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    creator_id = data.get("creator_id")

    # Input validation
    if not text or not text.strip():
        return jsonify({"error": "Field 'text' is required and cannot be empty."}), 400

    # ── Detection pipeline ───────────────────────────────────────────────────
    # Signal 1 (M3): Groq — fully implemented.
    groq_result = groq_signal(text)

    # Signal 2 (M4): Stylometric heuristics — currently a neutral stub.
    stylometric_result = stylometric_signal(text)

    llm_score = groq_result["score"]

    # ── Confidence scoring (M4 — STUB) ───────────────────────────────────────
    # TODO (M4): combine Score 1 and Score 2 per planning.md:
    #   weighted_mean - (0.5 * abs(groq_score - stylometric_score))
    confidence = None

    # Provisional attribution from Signal 1 alone (M4 recomputes from confidence).
    attribution = _attribution_from_score(llm_score)

    # ── Transparency label (M5 — STUB) ───────────────────────────────────────
    # TODO (M5): map the confidence score to one of three label variants.
    label = None

    content_id = str(uuid.uuid4())

    # ── Audit log ────────────────────────────────────────────────────────────
    entry = {
        "type": "submission",
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": _utc_timestamp(),
        "attribution": attribution,
        "confidence": confidence,   # filled in M4
        "llm_score": llm_score,     # Signal 1 (Groq)
        "label": label,             # filled in M5
        "status": "classified",
        "text": text,               # retained for the M5 appeal review view
        "signals": {
            "groq": groq_result,
            "stylometric": stylometric_result,
        },
    }
    _log_decision(entry)

    # ── Response ─────────────────────────────────────────────────────────────
    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": entry["timestamp"],
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "label": label,
        "status": "classified",
        "signals": {
            "groq": groq_result,
            "stylometric": stylometric_result,
        },
    }), 200


@app.route("/appeal", methods=["POST"])
def appeal():
    """POST /appeal — creator contests a classification. Implemented in M5."""
    return jsonify({"error": "Not implemented yet (M5)."}), 501


@app.route("/log", methods=["GET"])
def get_log():
    """
    Return the audit log as JSON, most recent first.

    Optional query param:
        ?limit=N  -> return only the N most recent entries (handy for README
                     snippets). Omit to return all entries.
    """
    entries = list(reversed(AUDIT_LOG))  # newest first

    limit = request.args.get("limit", type=int)
    if limit is not None and limit >= 0:
        entries = entries[:limit]

    return jsonify({"entries": entries}), 200


@app.route("/health", methods=["GET"])
def health():
    """Lightweight liveness check."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "5000")))
