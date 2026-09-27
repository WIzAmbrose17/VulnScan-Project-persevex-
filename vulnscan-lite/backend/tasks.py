import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from celery_app import celery_app
from scanner.scan import run_scan
import db


@celery_app.task(name="run_scan_task")
def run_scan_task(scan_id, url):
    try:
        result = run_scan(url)
        db.update_scan_result(scan_id, result)
    except Exception as e:
        db.mark_scan_failed(scan_id, str(e))
