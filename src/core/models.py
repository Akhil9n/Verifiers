from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class URLResolutionResult:
    original_url: str
    normalized_url: str | None
    decoded_url: str | None
    redirect_chain: List[str]
    final_url: Optional[str]
    status_code: Optional[int]
    domain: Optional[str]
    is_internal: bool
    classification: Optional[str]
    canonical: Optional[Dict[str, Any]]
    errors: List[str]
