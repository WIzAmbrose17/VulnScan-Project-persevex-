import requests

SECURITY_HEADERS = ["Content-Security-Policy", "X-Frame-Options", "Strict-Transport-Security"]


def check_headers(url):
    result = {"passed": [], "failed": [], "score": 0, "reachable": True}

    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "VulnScanLite/1.0"})
    except requests.exceptions.RequestException as e:
        result["reachable"] = False
        result["error"] = str(e)
        return result

    result["status_code"] = r.status_code
    result["raw_headers"] = dict(r.headers)

    for h in SECURITY_HEADERS:
        if h in r.headers:
            result["passed"].append(h)
            result["score"] += 10
        else:
            result["failed"].append(h)
            result["score"] -= 10

    return result


if __name__ == "__main__":
    import sys
    import json
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(json.dumps(check_headers(url), indent=2))
