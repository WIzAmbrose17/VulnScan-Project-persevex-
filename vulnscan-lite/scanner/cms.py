import re
import requests
from bs4 import BeautifulSoup

GENERATOR_MAP = {
    "wordpress": "WordPress",
    "drupal": "Drupal",
    "joomla": "Joomla",
    "wix.com": "Wix",
    "squarespace": "Squarespace",
    "shopify": "Shopify",
}

PATH_MAP = {
    "/wp-content/": "WordPress",
    "/wp-includes/": "WordPress",
    "/sites/default/files/": "Drupal",
    "/media/jui/": "Joomla",
}

OLD_VERSIONS = {
    "WordPress": (6, 4),
    "Drupal": (10, 0),
    "Joomla": (5, 0),
}


def detect_cms(url):
    result = {"cms": None, "version": None, "passed": [], "failed": [], "score": 0, "reachable": True}

    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "VulnScanLite/1.0"})
    except requests.exceptions.RequestException as e:
        result["reachable"] = False
        result["error"] = str(e)
        return result

    result["powered_by"] = r.headers.get("X-Powered-By")

    soup = BeautifulSoup(r.text, "html.parser")
    gen_tag = soup.find("meta", attrs={"name": "generator"})

    if gen_tag and gen_tag.get("content"):
        content = gen_tag["content"].lower()
        for key in GENERATOR_MAP:
            if key in content:
                result["cms"] = GENERATOR_MAP[key]
                match = re.search(r"(\d+\.\d+(\.\d+)?)", content)
                if match:
                    result["version"] = match.group(1)
                break

    if not result["cms"]:
        for path in PATH_MAP:
            if path in r.text:
                result["cms"] = PATH_MAP[path]
                break

    if result["cms"] and result["version"]:
        cutoff = OLD_VERSIONS.get(result["cms"])
        if cutoff:
            parts = result["version"].split(".")
            major = int(parts[0])
            minor = int(parts[1])
            if (major, minor) < cutoff:
                result["failed"].append("cms_up_to_date")
                result["score"] -= 10
            else:
                result["passed"].append("cms_up_to_date")
                result["score"] += 5
        result["failed"].append("cms_version_hidden")
        result["score"] -= 5

    return result


if __name__ == "__main__":
    import sys
    import json
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(json.dumps(detect_cms(url), indent=2))
