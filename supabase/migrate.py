#!/usr/bin/env python3
"""
migrate.py — Migreer SQLite data naar Supabase
Gebruik: SUPABASE_URL=https://xxx.supabase.co SUPABASE_KEY=xxx python3 migrate.py
"""

import sqlite3
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Stel SUPABASE_URL en SUPABASE_KEY in als omgevingsvariabelen")
    exit(1)

def supabase_insert(table, rows, batch_size=100):
    """Insereer rijen in Supabase via REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=ignore-duplicates"
    }
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        data = json.dumps(batch).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                inserted += len(batch)
                print(f"  ✓ Batch {i//batch_size + 1}: {len(batch)} rijen")
        except urllib.error.HTTPError as e:
            print(f"  ✗ Batch {i//batch_size + 1} fout: {e.code} {e.read().decode()[:200]}")
    return inserted

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Signalen migreren
    print("📤 Signalen migreren...")
    rows = conn.execute("""
        SELECT id, title, url, snippet, source_name, tier, fetched_at,
               published_at, source_type, filtered, score, full_text, summary
        FROM signals
    """).fetchall()

    signals = []
    for r in rows:
        ft = r["full_text"]
        if ft in ("SKIP", "FAILED"):
            ft = None
        signals.append({
            "id": r["id"],
            "title": r["title"],
            "url": r["url"],
            "snippet": r["snippet"],
            "source_name": r["source_name"],
            "tier": r["tier"],
            "fetched_at": r["fetched_at"],
            "published_at": r["published_at"],
            "source_type": r["source_type"],
            "filtered": r["filtered"],
            "score": r["score"],
            "full_text": ft,
            "summary": r["summary"]
        })

    n = supabase_insert("signals", signals)
    print(f"✅ {n} signalen gemigreerd")

    conn.close()
    print("\n🎉 Migratie klaar. Controleer je Supabase dashboard.")

if __name__ == "__main__":
    main()
