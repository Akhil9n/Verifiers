# URL Intent & Canonicalization Framework

Instead of directly comparing two URLs as strings, it **decodes each URL into structured semantic information**, extracts intent and parameters, and then compares those structures. This makes it possible to **pinpoint exactly where an AI agent failed**, *what it misunderstood*, and *what information was missing or incorrect*.

---

## Why This Exists

Direct URL comparison fails in real systems because:

- URLs can differ syntactically but represent the same intent
- Filters may appear in different orders or formats
- Parameters may be encoded in the path instead of the query
- Infrastructure redirects (rate limits, CDNs) distort final URLs
- Agents often generate “almost correct” URLs

This framework solves that by comparing **meaning**, not strings.

---

## Core Idea

Instead of:
**agent_url == ground_truth_url**

This is done:
decode(agent_url) → structured intent + parameters
decode(ground_truth_url) → structured intent + parameters
compare(structures)


This allows to identify:
- ❌ Wrong intent (search vs mortgage vs listing)
- ❌ Missing or incorrect filters
- ❌ Incorrect entity (property, city, etc.)
- ❌ Partially correct URLs with missing constraints

---

## High-Level Pipeline
URL
↓
Parse & Normalize
↓
Intent Detection
↓
Entity / Location Extraction
↓
Filter & Parameter Decoding
↓
Canonical Representation
↓
Explainable Comparison


---

## Intent-First Decoding

Every URL is first classified by **intent**, such as:

- `search` — city searches, filtered listings
- `listing` — individual property pages
- `seller_funnel` — seller consultation flows
- `mortgage` — financing flows
- `checkout` — tour scheduling / contact flows

Intent is derived from the **URL path**, not redirects or final landing pages.

This ensures that:
- Mortgage pages are never treated as searches
- Checkout flows don’t accidentally match listing pages
- Redirects (e.g. rate limiting) don’t overwrite intent

---

## Canonical Representation

Each URL is transformed into a **canonical semantic object**, for example:

```json
{
  "domain": "redfin.com",
  "intent": "search",
  "entity": null,
  "location": {
    "type": "city",
    "id": "3258",
    "state": "ca",
    "name": "ceres"
  },
  "filters": {
    "property_type": ["condo", "multifamily"],
    "beds": { "min": 2, "max": 3 },
    "baths": { "min": 2 },
    "price": { "min": 1000, "max": 3500 }
  }
}

### Key Structure Properties
- **Order-independent**: Structure remains valid regardless of parameter sequence.
- **Noise-tolerant**: Handles irrelevant or extraneous data without breaking.
- **Comparable**: Enables direct side-by-side evaluation of outputs.
- **Explainable**: Provides clear reasoning for matches or failures.

### Parameter Extraction (Key Advantage)
Filters and constraints are automatically extracted from multiple sources:

- Query parameters (e.g., `?min-beds=2`)
- Path-based filter DSLs (e.g., `/filter/min-beds=2,max-beds=3`)
- Boolean flags (e.g., `cats-allowed`, `has-deal`)

This extraction powers precise failure detection, such as:
- Agent forgot a filter (e.g., `min-beds`)
- Agent used wrong range (e.g., `max-price`)
- Agent used wrong entity (e.g., `city` vs `property`)
- Agent chose the wrong intent entirely

### Explainable Failure Analysis
Instead of vague feedback like “The URLs do not match,” this approach delivers specific diagnostics:

| Failure Type          | Example Explanation                  |
|-----------------------|--------------------------------------|
| Intent mismatch      | `search` vs `mortgage`              |
| Missing filter       | `min-baths`                         |
| Incorrect entity ID  | Wrong property identifier           |
| Wrong property type  | `apartment` vs `house`              |
| Extra/hallucinated constraints | Unrequested `pool` filter          |


### Comparison Strategy (Conceptual)

| Field    | Comparison                     |
| -------- | ------------------------------ |
| intent   | must match                     |
| entity   | must match if present          |
| location | must match for search          |
| filters  | diffable (missing / incorrect) |
| flags    | set comparison                 |


### What This Framework Is NOT
- ❌ **A scraper**: Does not extract data from web pages.
- ❌ **A ranking engine**: Does not score or prioritize results.
- ❌ **A DOM verifier**: Does not inspect or validate HTML structure.
- ❌ **A string matcher**: Does not rely on simple text similarity.

It is a **URL understanding and explanation system**.

### Why This Matters for AI Evaluation
AI agents frequently generate URLs that are:

- **Almost correct**: Close but missing key details.
- **Structurally valid**: Parse correctly but lack semantics.
- **Semantically incomplete**: Fail to capture full intent.

This framework provides precise answers like:

> "What exactly did the agent get wrong?"

Instead of vague feedback like:

> "The answer is wrong."
