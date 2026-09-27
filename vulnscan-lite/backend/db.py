import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "vulnscan.db")


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            url TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            score INTEGER,
            grade TEXT,
            result_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def create_user(email, password_hash):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_scan(scan_id, url, user_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO scans (id, url, user_id, status) VALUES (?, ?, ?, 'pending')",
              (scan_id, url, user_id))
    conn.commit()
    conn.close()


def update_scan_result(scan_id, result):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE scans SET status = 'done', score = ?, grade = ?, result_json = ? WHERE id = ?",
        (result["score"], result["grade"], json.dumps(result), scan_id)
    )
    conn.commit()
    conn.close()


def mark_scan_failed(scan_id, error):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE scans SET status = 'failed', result_json = ? WHERE id = ?",
              (json.dumps({"error": error}), scan_id))
    conn.commit()
    conn.close()


def get_scan(scan_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_history_for_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, url, status, score, grade, created_at FROM scans WHERE user_id = ? ORDER BY created_at DESC",
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
