from urllib.parse import urlparse

REDFIN_DOMAINS = {"www.redfin.com", "redfin.com", "ratelimited.redfin.com"}

def classify_redfin_url(path: str) -> str:
    if path == "/":
        return "HOME"

    if path == "/houses-near-me":
        return "SEARCH_LANDING"

    if path.startswith("/city/"):
        return "CITY_PAGE"

    if path.startswith("/home/"):
        return "LISTING_PAGE"

    if path.startswith("/mortgage-get-pre-approved"):
        return "MORTGAGE_FUNNEL"

    if path.startswith("/tours/checkout"):
        return "CHECKOUT_FLOW"

    if "/filter/" in path:
        return "SEARCH_RESULTS"

    return "UNKNOWN"

def is_redfin_domain(url: str) -> bool:
    return urlparse(url).netloc in REDFIN_DOMAINS
