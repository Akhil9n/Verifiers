from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import re

# -------------------------------------------------
# Query params that do NOT affect logical intent
# -------------------------------------------------
IGNORED_QUERY_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "io",
    "spex_v",
    "context",
    "epc",
}

# -------------------------------------------------
# Intent classification rules
# -------------------------------------------------
INTENT_RULES = {
    "mortgage": [
        "/mortgage",
        "/mortgage-get-pre-approved",
        "/mortgage-rates",
    ],
    "checkout": [
        "/tours/checkout",
        "/tours/schedule",
    ],
    "seller_funnel": [
        "/sell-a-home",
        "/seller-consultation",
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


# -------------------------------------------------
# Feature normalization
# -------------------------------------------------
def normalize_feature_tokens(raw: str) -> list[str]:
    raw = raw.lower().replace("_", "-").replace(",", "-")
    return sorted({p.strip() for p in raw.split("-") if p.strip()})


# -------------------------------------------------
# Intent detection
# -------------------------------------------------
def detect_page_intent(parsed) -> str:
    path = parsed.path.lower()

    for intent, prefixes in INTENT_RULES.items():
        for prefix in prefixes:
            if prefix in path:
                return intent

    return "unknown"


# -------------------------------------------------
# Location extraction (search only)
# -------------------------------------------------
def extract_location(parsed):
    path_parts = parsed.path.lower().strip("/").split("/")
    query = parse_qs(parsed.query)

    if len(path_parts) >= 4 and path_parts[0] == "city":
        return {
            "type": "city",
            "id": path_parts[1],
            "state": path_parts[2],
            "name": path_parts[3],
        }

    if "location_id" in query:
        return {
            "type": "query_location",
            "id": query["location_id"][0],
            "state": None,
            "name": None,
        }

    return None


# -------------------------------------------------
# Entity extraction (generalized)
# -------------------------------------------------
def extract_entity(parsed, intent: str):
    path_parts = parsed.path.lower().strip("/").split("/")
    query = parse_qs(parsed.query)

    # Listing page → property entity from path
    if intent == "listing":
        if "home" in path_parts:
            try:
                idx = path_parts.index("home")
                return {
                    "type": "property",
                    "id": path_parts[idx + 1],
                }
            except Exception:
                return None

    # Seller funnel → property entity
    if intent == "seller_funnel":
        # Query-based
        if "propertyid" in query:
            return {
                "type": "property",
                "id": query["propertyid"][0],
            }

        # Path-based: /seller-consultation/{id}
        if "seller-consultation" in path_parts:
            try:
                idx = path_parts.index("seller-consultation")
                return {
                    "type": "property",
                    "id": path_parts[idx + 1],
                }
            except Exception:
                return None

    return None


def parse_redfin_filters_general(filter_segment: str) -> dict:
    filters = {}
    flags = []

    tokens = filter_segment.split(",")

    for token in tokens:
        token = unquote(token.strip().lower())

        if "=" not in token:
            flags.append(token)
            continue

        key, value = token.split("=", 1)

        values = value.split("+")

        # ---- property type ----
        if key == "property-type":
            filters["property_type"] = sorted(values)

        # ---- beds / baths / sqft ----
        elif re.match(r"(min|max)-(beds|baths|sqft)", key):
            bound, field = key.split("-", 1)
            filters.setdefault(field, {})[bound] = int(values[0])

        # ---- fallback ----
        else:
            filters[key] = values if len(values) > 1 else values[0]

    if flags:
        filters["flags"] = sorted(flags)

    return filters

# -------------------------------------------------
# Canonical URL representation
# -------------------------------------------------
def canonicalize_redfin_url(url: str) -> dict:
    parsed = urlparse(url.lower())

    domain = parsed.netloc.replace("www.", "")
    intent = detect_page_intent(parsed)
    entity = extract_entity(parsed, intent)

    raw_query = parse_qs(parsed.query)
    clean_query = {
        k: v for k, v in raw_query.items()
        if k not in IGNORED_QUERY_PARAMS
    }

    features = set()
    if intent == "search":
        for key, values in clean_query.items():
            if key in {"features", "amenities"}:
                for val in values:
                    features.update(normalize_feature_tokens(val))

    filters = {}
    # Search intent → extract from path after "filter/"
    if intent == "search" and "/filter/" in parsed.path:
        filter_segment = parsed.path.split("/filter/", 1)[1]
        filter_segment = filter_segment.strip("/")
        if filter_segment:
            filters = parse_redfin_filters_general(filter_segment)

    
    location = extract_location(parsed) if intent == "search" else None

    return {
        "domain": domain,
        "intent": intent,
        "entity": entity,
        "location": location,
        "features": sorted(features),
        "filters": filters, 
    }
