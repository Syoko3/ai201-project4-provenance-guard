# ai201-project4-provenance-guard

Short Portfolio Walkthrough Video Link: 

---

## Rate Limiting

The submission endpoint (`POST /submit`) is rate limited with Flask-Limiter,
keyed by client IP (`get_remote_address`), using in-memory storage
(`storage_uri="memory://"`).

**Chosen limits:** `10 per minute; 100 per day`

**Reasoning:**

- **10 requests per minute** — A legitimate writer submits their own work
  occasionally, and even when iterating on drafts or re-checking edits they
  rarely exceed a handful of submissions in a minute. A ceiling of 10/minute
  leaves comfortable headroom for real human bursts (e.g., re-submitting after
  small tweaks) while immediately stopping a script that fires dozens or
  hundreds of requests per minute.
- **100 requests per day** — This is a generous daily allowance for even a
  prolific individual creator, but it caps sustained automated abuse from a
  single IP that stays under the per-minute limit. It also bounds cost: every
  submission triggers a Groq API call, so the daily cap puts a hard ceiling on
  per-IP API spend.

The two limits work together: the per-minute limit blocks rapid floods, and the
per-day limit blocks slow, sustained scraping that would otherwise slip under a
minute-only limit. Exceeding either returns HTTP `429 Too Many Requests`.

**Test evidence** — sending 12 rapid requests (more than the 10/minute limit):

```
 1: 200
 2: 200
 3: 200
 4: 200
 5: 200
 6: 200
 7: 200
 8: 200
 9: 200
10: 200
11: 429
12: 429
```

The first 10 requests succeed (`200`); requests 11 and 12 are rejected with
`429 Too Many Requests`, confirming the limit is enforced.

---

