from urllib.parse import urlparse, parse_qs, unquote

def parse_and_decode(url: str) -> dict:
    parsed = urlparse(url)
    
    decoded_path = unquote(parsed.path)
    decoded_query = {
        k: [unquote(v) for v in vals]
        for k, vals in parse_qs(parsed.query).items()
    }

    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc.lower(),
        "path": decoded_path,
        "query": decoded_query,
        "fragment": parsed.fragment
    }
