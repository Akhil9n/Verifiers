import json
from pathlib import Path

from runners.run_url_tests import run

CASES = json.loads(
    Path("sample_urls/redfin_cases.json").read_text()
)

def test_redfin_urls():
    for case in CASES:
        result = run(case["url"])

        if "expected_domain" in case:
            assert result.domain == case["expected_domain"]

        if "expected_internal" in case:
            assert result.is_internal == case["expected_internal"]

        if "expected_classification" in case:
            assert result.classification == case["expected_classification"]
