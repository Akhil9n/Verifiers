from urllib.parse import urlparse, parse_qs

# -----------------------------
# Intent classification rules
# -----------------------------
INTENT_RULES = {
    "mortgage": [
        "/mortgage",
        "/mortgage-get-pre-approved",
    ],
    "checkout": [
        "/tours/checkout",
        "/tours/schedule",
    ],
    "listing": [
        "/home/",
    ],
    "search": [
        "/city/",
        "/houses-near-me",
        "/filter/",
    ],
}

# -----------------------------
# Noise / ignored query params
# -----------------------------
IGNORED_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign",
    "io", "spex_v", "context", "epc"
}

# -----------------------------
# Feature token normalization
# -----------------------------
def normalize_feature_tokens(raw: str) -> list[str]:
    tokens = []
    raw = raw.lower()
    raw = raw.replace("_", "-").replace(",", "-")

    for part in raw.split("-"):
        part = part.strip()
        if part:
            tokens.append(part)

    return sorted(set(tokens))

# -------------------------------------------------
# Page intent detection
# -------------------------------------------------
def detect_page_intent(parsed) -> str:
    """
    Determines high-level intent of the page.
    """
    path = parsed.path.lower()

    for intent, prefixes in INTENT_RULES.items():
        for prefix in prefixes:
            if path.startswith(prefix):
                return intent

    return "unknown"


# -----------------------------
# Location extraction
# -----------------------------
def extract_location(parsed):
    """
    Extract location from path or query.
    Supports:
    - /city/{id}/{state}/{name}
    - ?location_id=XXX
    """
    path_parts = parsed.path.lower().strip("/").split("/")

    # Path-based city
    if len(path_parts) >= 4 and path_parts[0] == "city":
        return {
            "type": "city",
            "id": path_parts[1],
            "state": path_parts[2],
            "name": path_parts[3]
        }

    # Query-based location
    query = parse_qs(parsed.query)
    if "location_id" in query:
        return {
            "type": "query_location",
            "id": query["location_id"][0],
            "state": None,
            "name": None
        }

    return None


# -------------------------------------------------
# Canonical Redfin URL representation
# -------------------------------------------------
def canonicalize_redfin_url(url: str) -> dict:
    """
    Produces a canonical, intent-aware representation of a Redfin URL.
    This does NOT perform equivalence checks.
    """
    parsed = urlparse(url.lower())

    # ---- domain normalization ----
    domain = parsed.netloc.replace("www.", "")

    # ---- intent detection ----
    intent = detect_page_intent(parsed)

    # ---- query cleanup ----
    raw_query = parse_qs(parsed.query)
    clean_query = {
        k: v for k, v in raw_query.items()
        if k not in IGNORED_QUERY_PARAMS
    }

    # ---- feature extraction (search-only) ----
    features = set()
    if intent == "search":
        for key, values in clean_query.items():
            if key in {"features", "amenities"}:
                for val in values:
                    features.update(normalize_feature_tokens(val))

    # ---- location (search-only) ----
    location = extract_location(parsed) if intent == "search" else None

    return {
        "domain": domain,
        "intent": intent,
        "location": location,
        "features": sorted(features),
    }
