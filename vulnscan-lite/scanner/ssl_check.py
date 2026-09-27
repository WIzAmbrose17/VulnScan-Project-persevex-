import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse

WEAK_CIPHERS = ["RC4", "3DES", "DES", "MD5", "NULL", "EXPORT"]
DATE_FMT = "%b %d %H:%M:%S %Y %Z"


def check_ssl(host, port=443):
    if "://" in host:
        host = urlparse(host).hostname

    result = {"reachable": False, "passed": [], "failed": [], "score": 0}

    ctx = ssl.create_default_context()
    try:
        sock = socket.create_connection((host, port), timeout=8)
        wrapped = ctx.wrap_socket(sock, server_hostname=host)
        cert = wrapped.getpeercert()
        cipher_name, tls_version, bits = wrapped.cipher()
        wrapped.close()
    except Exception as e:
        result["error"] = str(e)
        result["failed"].append("https_available")
        result["score"] -= 20
        return result

    result["reachable"] = True
    result["cipher"] = cipher_name
    result["tls_version"] = tls_version

    not_before = datetime.strptime(cert["notBefore"], DATE_FMT)
    not_after = datetime.strptime(cert["notAfter"], DATE_FMT)
    now = datetime.utcnow()
    days_left = (not_after - now).days

    result["not_after"] = str(not_after)
    result["days_left"] = days_left

    if not_before <= now <= not_after:
        result["passed"].append("certificate_valid")
        result["score"] += 10
    else:
        result["failed"].append("certificate_valid")
        result["score"] -= 10

    if days_left < 30:
        result["failed"].append("certificate_expiring_soon")
        result["score"] -= 5

    weak = False
    for w in WEAK_CIPHERS:
        if w in cipher_name:
            weak = True
    if weak:
        result["failed"].append("weak_cipher_suite")
        result["score"] -= 10
    else:
        result["passed"].append("strong_cipher_suite")
        result["score"] += 5

    if tls_version in ("TLSv1", "TLSv1.1", "SSLv3"):
        result["failed"].append("outdated_tls_version")
        result["score"] -= 10
    else:
        result["passed"].append("modern_tls_version")

    return result


if __name__ == "__main__":
    import sys
    import json
    host = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    print(json.dumps(check_ssl(host), indent=2))
