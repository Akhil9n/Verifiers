from urllib.parse import urlunparse

def normalize_url(parsed: dict) -> str:
    netloc = parsed["netloc"]
    path = parsed["path"].rstrip("/") or "/"

    return urlunparse((
        "https",
        netloc,
        path,
        "",
        "",
        ""
    ))
