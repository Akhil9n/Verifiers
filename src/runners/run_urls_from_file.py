import sys
import os
import json
from dataclasses import asdict

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from runners.run_url_tests import run

def load_urls(file_path: str) -> list[str]:
    """
    Reads URLs from a text file.
    Ignores empty lines and comments (#).
    """
    urls = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def run_batch(file_path: str):
    urls = load_urls(file_path)
    results = []

    for url in urls:
        print(f"\n Testing: {url}")
        try:
            result = run(url)
            results.append(asdict(result))
        except Exception as e:
            results.append({
                "original_url": url,
                "error": str(e)
            })

    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_urls_from_file.py <path_to_urls.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    results = run_batch(file_path)

    # Pretty print final summary
    # print("\n====== FINAL RESULTS ======")
    # print(json.dumps(results, indent=2, default=str))
