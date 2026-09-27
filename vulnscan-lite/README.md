# VulnScan Lite

> Only scan websites you own. This tool performs passive analysis only.

Put in a url, get back a security score (0-100), a letter grade, and a list
of what's wrong with fixes for each thing.

## What it checks

- missing security headers (CSP, X-Frame-Options, HSTS)
- SSL cert validity/expiry, weak ciphers, old TLS versions
- what CMS the site is running and whether the version looks outdated

Full breakdown of the checks is in `docs/SCANNING_LOGIC.md`.

## Project layout

```
scanner/      the actual scanning logic, no web stuff in here
backend/      flask api + celery worker + sqlite db + pdf generator
frontend/     react app
docs/         scanning logic writeup
```

## Running it locally

You need: python 3.10+, node, and redis running somewhere.

### 1. redis

```
redis-server
```

(if you don't have it: `sudo apt install redis-server` or run it in docker,
`docker run -p 6379:6379 redis`)

### 2. backend

```
cd backend
pip install -r requirements.txt
python app.py
```

this starts the flask api on port 5000. In a separate terminal, start the
celery worker (this is what actually runs the scans in the background):

```
cd backend
celery -A celery_app worker --loglevel=info
```

Without the worker running, scans will just sit in "pending" forever since
nothing is picking them up off the queue.

### 3. frontend

```
cd frontend
npm install
npm start
```

opens on port 3000, talks to the backend on port 5000 (see `src/api.js` if
you need to point it somewhere else).

## How the async part works

1. user hits scan, frontend POSTs to `/api/scan`
2. backend makes a scan_id, saves a "pending" row in sqlite, pushes the job
   onto the redis queue via `run_scan_task.delay(...)`, and immediately
   returns the scan_id (doesn't wait around for the scan to finish)
3. frontend polls `GET /api/scan/<id>/status` every 2 seconds
4. meanwhile the celery worker (running separately) picks the job off the
   queue, actually runs the scan (this is the slow part, 10-30 sec), and
   writes the result back into sqlite
5. next time the frontend polls, status comes back "done" with the full result

This is why we needed celery/redis at all -- doing this scan synchronously
inside the flask request would mean the browser just hangs for 30 seconds,
and if a bunch of people scan at once the whole server would choke.

## Auth / history

Registering/logging in is just flask sessions + a sqlite users table
(passwords hashed with werkzeug, nothing fancy). If you're logged in when
you kick off a scan, it gets tied to your user_id and shows up under
History. If you're not logged in, the scan still works fine, it just isn't
saved to any account.

## PDF reports

Once a scan is done, `/api/scan/<id>/pdf` builds a pdf on the fly using
reportlab and sends it back. Nothing is cached, it just regenerates from the
result_json stored in sqlite every time you hit the endpoint.

## Rate limiting / safety

- one scan request per IP every 5 seconds (backend/app.py, `is_rate_limited`)
- can't scan localhost / private IP ranges / link-local addresses, so people
  can't point this at internal infra or the server it's running on (see
  `is_safe_target` in app.py)
- everything is read-only http requests + a normal tls handshake, nothing
  here sends malformed input or tries to exploit anything it finds

## Deploying

Included a `Procfile` for Render/Heroku-style platforms:

```
web: cd backend && gunicorn app:app
worker: cd backend && celery -A celery_app worker --loglevel=info
```

You'd also need a managed redis addon and to point `REDIS_URL` in
`backend/celery_app.py` at it instead of localhost. Frontend can be built
with `npm run build` and hosted as a static site (Netlify/Vercel/etc), just
update `BASE_URL` in `src/api.js` to the deployed backend url.

sqlite is fine for this project size but if this ever needs multiple backend
instances running at once, sqlite is the wrong choice (file locking issues)
and it'd need to move to postgres.

## Known limitations / stuff I'd fix with more time

- CMS outdated-version cutoffs are hardcoded, should pull from a real feed
- no https enforcement between frontend and backend locally (fine for a
  school project, not fine for prod)
- rate limiter is just an in-memory dict, resets on server restart and
  doesn't work if you run more than one backend process
- no tests written, everything above was checked manually
