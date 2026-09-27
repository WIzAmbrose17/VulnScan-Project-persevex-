from urllib.parse import urlparse

from .headers import check_headers
from .ssl_check import check_ssl
from .cms import detect_cms
from .remediation import get_tip

DISCLAIMER = "Only scan websites you own. This tool performs passive analysis only."


def grade_from_score(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def run_scan(target):
    if not target.startswith("http"):
        target = "https://" + target

    host = urlparse(target).hostname

    header_result = check_headers(target)
    ssl_result = check_ssl(host)
    cms_result = detect_cms(target)

    score = 100
    passed = []
    failed = []

    for module in [header_result, ssl_result, cms_result]:
        score += module.get("score", 0)
        passed += module.get("passed", [])
        for f in module.get("failed", []):
            tip = get_tip(f)
            failed.append({"check": f, "why": tip["why"], "nginx": tip["nginx"], "apache": tip["apache"]})

    if score > 100:
        score = 100
    if score < 0:
        score = 0

    report = {
        "url": target,
        "disclaimer": DISCLAIMER,
        "score": score,
        "grade": grade_from_score(score),
        "passed_checks": passed,
        "failed_checks": failed,
        "headers": header_result,
        "ssl": ssl_result,
        "cms": cms_result,
    }
    return report


if __name__ == "__main__":
    import sys
    import json
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    print(json.dumps(run_scan(target), indent=2))
