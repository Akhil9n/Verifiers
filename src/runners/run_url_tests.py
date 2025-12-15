from urllib.parse import urlparse
from dataclasses import  asdict
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser import parse_and_decode
from core.normalizer import normalize_url
from core.resolver import resolve_redirects
from verifiers.redfin import is_redfin_domain, classify_redfin_url
from core.models import URLResolutionResult

def run(url: str) -> URLResolutionResult:
    errors = []

    parsed = parse_and_decode(url)
    normalized = normalize_url(parsed)
    decoded = parsed["path"]

    resolution = resolve_redirects(normalized)

    final_url = resolution.get("final_url")
    status = resolution.get("status_code")

    is_internal = final_url and is_redfin_domain(final_url)
    classification = classify_redfin_url(parsed["path"])

    result =  URLResolutionResult(
        original_url=url,
        normalized_url=normalized,
        decoded_url=decoded,
        redirect_chain=resolution.get("redirect_chain", []),
        final_url=final_url,
        status_code=status,
        domain=urlparse(final_url).netloc if final_url else None,
        is_internal=is_internal,
        classification=classification,
        errors=errors
    )

    print(json.dumps(asdict(result), indent=2, default=str))
    return result

res = run("https://www.redfin.com")
run("https://www.redfin.com/city/245/NY/Albany/newest-listings")
run("https://www.redfin.com/mortgage-get-pre-approved?context=86&location_id=35948&location_type=2&spex_v=1")
run("https://www.redfin.com/tours/checkout/contact?listingId=209901519&date=undefined&inquirySource=589&agentId=50490&epc=undefined&isRequestingForPartner=true")
# print(json.dumps(res, indent=2))