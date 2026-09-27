# Scanning Logic

This doc explains what the scanner actually checks. All checks are passive,
meaning we just send normal requests and read what comes back, we don't try
to break anything.

## Header checks (scanner/headers.py)

One GET request to the target URL. We look for 3 headers:

- Content-Security-Policy - stops the browser loading scripts from random places
- X-Frame-Options - stops the site being put in an iframe on another site (clickjacking)
- Strict-Transport-Security - forces https

Each one present = +10, each one missing = -10.

## SSL/TLS checks (scanner/ssl_check.py)

Opens a normal TLS connection using Python's ssl module (same thing your
browser does when it connects to a https site). We check:

- is the certificate actually valid right now (not expired, not before start date)
- is it expiring in less than 30 days (warning, -5)
- is the cipher one of the old broken ones (RC4, 3DES, MD5, etc), -10 if so
- is the TLS version old (1.0/1.1), -10 if so
- if we can't connect over https at all, thats -20, worst finding

## CMS detection (scanner/cms.py)

We read the HTML that comes back and look for:

- the `<meta name="generator">` tag, most CMS's put their name + version here
- if that's not there, we fall back to checking for known file paths like
  /wp-content/ which only wordpress uses
- X-Powered-By header, just recorded, not scored on its own

If we find a version number we compare it against a hardcoded "old version"
cutoff (this is just for the demo, a real product would pull this from
something like the WPScan vulnerability database instead of a hardcoded dict).

If the site is running an old version: -10.
If the generator tag reveals the exact version at all: -5 (its an info leak,
gives attackers a starting point).

## Scoring

Start at 100. Add up all the +/- from the three modules above. Clamp to
0-100. Grade letter:

- 90+ = A
- 80-89 = B
- 70-79 = C
- 60-69 = D
- below 60 = F

## What this does NOT do

- no login brute forcing
- no sending malformed/fuzzed requests
- no exploiting anything it finds
- no scanning of internal/private IP ranges (not currently blocked in code,
  should probably add a check for that before letting random users scan
  whatever url they want)
