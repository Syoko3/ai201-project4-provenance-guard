# ai201-project4-provenance-guard

Short Portfolio Walkthrough Video Link: 

---

## Architecture Overview

When the user submits the content, the raw text and creator_id arrive at POST /submit. The request first passes the rate limiter, then input validation rejects empty text. The validated text then enters the detection pipeline, where it is scored by two independent signals, which are Groq and Stylometric Heuristics. Both signal scores flow into combine_signals function in signals.py by taking the weighted mean for 80% Groq and 20% Stylometric to produce the combined confidence score between 0 and 1. This score is mapped by threshold into one of three transparency-label variants. Finally, a unique content_id is assigned and the full decision that includes text, both signal scores, combined confidence, label, timestamp is written to the audit log. The response is returned to the user by showing the content_id, confidence, and the transparency label.

---

## Detection Signals

| Signal | What does the signal measure | Reason of Choice | What It Misses |
|--------|------------------------------|------------------|----------------|
| Groq | "Vibe" and semantic coherence of the text |  |  |
| Stylometric Heuristics | Type-Token Ratio, Sentence Length Variance, Punctuation Density |  |  |

---

## Confidence Scoring



---

## Transparency Label

| Transparency Label | Confidence Score Range | Display Text |
|--------------------|------------------------|--------------|
| High-Confidence Human | 0.0 <= Score < 0.4 | Human-Authored Content |
| Uncertain Result | 0.4 <= Score < 0.7 | Attribution Uncertain |
| High-Confidence AI | 0.7 <= Score <= 1.0 | AI-Generated Content |

---

## Rate Limiting

**Chosen limits:** 10 per minute, 100 per day

**Reasoning:**

- 10 requests per minute: A legitimate writer submits their own work occasionally, and even when iterating on drafts or rechecking edits they rarely exceed a handful of submissions in a minute. A ceiling of 10/minute blocks rapid floods and immediately stops a script that prevents hundreds of requests per minute.
- 100 requests per day: This is a generous daily allowance for even a prolific individual creator, but it caps sustained automated abuse from a single IP that stays under the per-minute limit. It blocks slow, sustained scraping that would otherwise slip under a minute-only limit.

**Test evidence** — sending 12 rapid requests (more than the 10/minute limit)(Exceeding either returns HTTP `429 Too Many Requests`):

```
200
200
200
200
200
200
200
200
200
200
429
429
```

---

## Known Limitations



---

## Spec Reflection

**One way the spec helped you during implementation:**


**One way your implementation diverged from the spec, and why:**


---

## AI Usage Section

**Instance 1**

- *What I gave the AI:* 
- *What it produced:* 
- *What I changed or overrode:* 

**Instance 2**

- *What I gave the AI:* 
- *What it produced:* 
- *What I changed or overrode:* 
