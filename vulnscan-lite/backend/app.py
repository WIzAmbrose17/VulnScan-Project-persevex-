import sys
import os
import uuid
import time
import socket
import ipaddress
from urllib.parse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

import db
from tasks import run_scan_task
from pdf_report import make_pdf

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deploying"

db.init_db()

# super basic rate limiting, just an in-memory dict, resets if server restarts
last_request_times = {}
RATE_LIMIT_SECONDS = 5


def is_rate_limited(ip):
    now = time.time()
    last = last_request_times.get(ip)
    if last and now - last < RATE_LIMIT_SECONDS:
        return True
    last_request_times[ip] = now
    return False


def is_safe_target(url):
    # block scans of internal/private/loopback stuff so people can't use
    # this to probe their own network or the server it runs on
    if not url.startswith("http"):
        url = "https://" + url
    host = urlparse(url).hostname
    if not host:
        return False
    try:
        ip = socket.gethostbyname(host)
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            return False
    except socket.gaierror:
        return False
    return True


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    existing = db.get_user_by_email(email)
    if existing:
        return jsonify({"error": "user already exists"}), 400

    password_hash = generate_password_hash(password)
    user_id = db.create_user(email, password_hash)
    session["user_id"] = user_id
    return jsonify({"message": "registered", "user_id": user_id})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid email or password"}), 401

    session["user_id"] = user["id"]
    return jsonify({"message": "logged in"})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "logged out"})


@app.route("/api/scan", methods=["POST"])
def start_scan():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "slow down, try again in a few seconds"}), 429

    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "url is required"}), 400

    if not is_safe_target(url):
        return jsonify({"error": "that url can't be scanned (private/internal address or not resolvable)"}), 400

    scan_id = str(uuid.uuid4())
    user_id = session.get("user_id")

    db.create_scan(scan_id, url, user_id)
    run_scan_task.delay(scan_id, url)

    return jsonify({"scan_id": scan_id})


@app.route("/api/scan/<scan_id>/status", methods=["GET"])
def scan_status(scan_id):
    scan = db.get_scan(scan_id)
    if not scan:
        return jsonify({"error": "not found"}), 404

    response = {"status": scan["status"]}
    if scan["status"] == "done":
        import json
        response["result"] = json.loads(scan["result_json"])
    elif scan["status"] == "failed":
        import json
        response["error"] = json.loads(scan["result_json"]).get("error")

    return jsonify(response)


@app.route("/api/history", methods=["GET"])
def history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "must be logged in"}), 401

    scans = db.get_history_for_user(user_id)
    return jsonify(scans)


@app.route("/api/scan/<scan_id>/pdf", methods=["GET"])
def scan_pdf(scan_id):
    scan = db.get_scan(scan_id)
    if not scan or scan["status"] != "done":
        return jsonify({"error": "report not ready"}), 400

    pdf_bytes = make_pdf(scan)
    buf = BytesIO(bytes(pdf_bytes))
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                      download_name="vulnscan_report_" + scan_id + ".pdf")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
