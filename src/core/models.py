from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class URLResolutionResult:
    original_url: str
    normalized_url: str
    decoded_url: str
    redirect_chain: List[str]
    final_url: Optional[str]
    status_code: Optional[int]
    domain: Optional[str]
    is_internal: bool
    classification: Optional[str]
    errors: List[str]
