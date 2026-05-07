#!/usr/bin/env python3
"""
1b_verrijken.py — Full-text ophalen voor relevante signalen
Haalt de volledige artikeltekst op via content.js (Brave scraper)
en slaat op in signals.full_text voor betere scoring.

Draait na 1_ophalen.py, vóór 2_filteren.py en 3_prioriteren.py
"""

import subprocess
import sqlite3
import time
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
CONTENT_SCRIPT = Path.home() / ".openclaw/workspace/skills/brave-search/content.js"

MAX_CHARS = 3000       # max tekens uit artikel
DELAY = 3              # seconden tussen requests (rate limit)
BATCH_SIZE = 20        # max artikelen per run (voorkom lange sessies)

# Domeinen die vaak blokkeren of niet nuttig zijn
SKIP_DOMAINS = [
    "pubmed.ncbi.nlm.nih.gov",
    "twitter.com", "x.com", "linkedin.com",
    "fiercebiotech.com",  # vereist login
    "statnews.com",       # vereist login
]

def fetch_content(url):
    """Haal volledige artikeltekst op via content.js"""
    try:
        result = subprocess.run(
            ["node", str(CONTENT_SCRIPT), url],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and len(result.stdout.strip()) > 100:
            return result.stdout[:MAX_CHARS]
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return None

def extract_url(raw):
    """Haal URL op uit mogelijke HTML anchor tag"""
    import re
    m = re.search(r'href=["\']([^"\']+)["\']', raw)
    return m.group(1) if m else raw

def should_skip(url):
    return any(domain in url for domain in SKIP_DOMAINS)

def main():
    conn = sqlite3.connect(DB_PATH)

    # Haal signalen op zonder full_text, gesorteerd op score DESC
    rows = conn.execute("""
        SELECT id, url, title, score FROM signals
        WHERE full_text IS NULL
        ORDER BY filtered DESC, score DESC
        LIMIT ?
    """, (BATCH_SIZE,)).fetchall()

    if not rows:
        print("✅ Alle signalen al verrijkt")
        return

    print(f"🔍 {len(rows)} artikelen verrijken...")
    enriched = 0
    skipped = 0
    failed = 0

    for sid, raw_url, title, score in rows:
        url = extract_url(raw_url)
        if should_skip(url):
            conn.execute("UPDATE signals SET full_text = 'SKIP' WHERE id = ?", (sid,))
            skipped += 1
            continue

        print(f"  [{score}] {title[:60]}...")
        content = fetch_content(url)

        if content:
            conn.execute("UPDATE signals SET full_text = ? WHERE id = ?", (content, sid))
            enriched += 1
            print(f"    ✓ {len(content)} tekens")
        else:
            conn.execute("UPDATE signals SET full_text = 'FAILED' WHERE id = ?", (sid,))
            failed += 1
            print(f"    ✗ niet opgehaald")

        conn.commit()
        time.sleep(DELAY)

    conn.close()
    total = len(rows)
    print(f"\n✅ Verrijking klaar — {enriched}/{total} geslaagd | {skipped} overgeslagen | {failed} mislukt")
    print("→ Draai nu 2_filteren.py en 3_prioriteren.py opnieuw voor betere scores")

if __name__ == "__main__":
    main()
