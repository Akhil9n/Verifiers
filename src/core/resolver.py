import requests

def resolve_redirects(url: str, timeout=10):
    chain = []
    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        for r in response.history:
            chain.append(r.url)

        return {
            "final_url": response.url,
            "status_code": response.status_code,
            "redirect_chain": chain
        }
    except Exception as e:
        return {
            "final_url": None,
            "status_code": None,
            "redirect_chain": chain,
            "error": str(e)
        }
