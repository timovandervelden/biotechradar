#!/usr/bin/env python3
"""
1_ophalen.py — Data verzamelen uit een centraal bronregister.

Primair:
  A) RSS/API-achtige feeds uit config/sources.yaml
Fallback:
  B) Search-bronnen (bijv. Brave), alleen als bron status=active is
"""

import hashlib
import sqlite3
import subprocess
import time
from datetime import datetime, UTC
from pathlib import Path

import feedparser
import yaml

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
SOURCES = BASE / "config" / "sources.yaml"
BRAVE_SCRIPT = Path.home() / ".openclaw/workspace/skills/brave-search/search.js"


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signals (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            snippet TEXT,
            source_name TEXT,
            tier INTEGER,
            fetched_at TEXT,
            published_at TEXT,
            source_type TEXT DEFAULT 'search',
            filtered INTEGER DEFAULT 0,
            score REAL DEFAULT 0,
            summary TEXT
        )
    """
    )
    try:
        conn.execute("ALTER TABLE signals ADD COLUMN published_at TEXT")
        conn.execute("ALTER TABLE signals ADD COLUMN source_type TEXT DEFAULT 'search'")
    except Exception:
        pass
    conn.commit()


def signal_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]


def load_sources():
    with open(SOURCES) as f:
        config = yaml.safe_load(f)
    return config.get("sources", []), set(config.get("skip_domains", []))


def fetch_rss(feed_url, source_name, tier, conn):
    new = 0
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.get("link", "")
            title = entry.get("title", "")
            snippet = entry.get("summary", "")[:400]
            published = entry.get("published", "") or entry.get("updated", "")

            if not url or not title:
                continue

            sid = signal_id(url)
            if not conn.execute("SELECT 1 FROM signals WHERE id=?", (sid,)).fetchone():
                conn.execute(
                    """
                    INSERT INTO signals
                    (id, title, url, snippet, source_name, tier, fetched_at, published_at, source_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'rss')
                """,
                    (
                        sid,
                        title,
                        url,
                        snippet,
                        source_name,
                        tier,
                        datetime.now(UTC).isoformat(),
                        published,
                    ),
                )
                new += 1
    except Exception as e:
        print(f"  ⚠️  RSS fout ({source_name}): {e}")
    return new


def fetch_brave(query, source_name, tier, conn):
    time.sleep(3)
    new = 0
    try:
        result = subprocess.run(
            ["node", str(BRAVE_SCRIPT), query, "-n", "6"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        current = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("--- Result"):
                if current.get("title") and current.get("url"):
                    sid = signal_id(current["url"])
                    if not conn.execute("SELECT 1 FROM signals WHERE id=?", (sid,)).fetchone():
                        conn.execute(
                            """
                            INSERT INTO signals
                            (id, title, url, snippet, source_name, tier, fetched_at, source_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'search')
                        """,
                            (
                                sid,
                                current["title"],
                                current["url"],
                                current.get("snippet", ""),
                                source_name,
                                tier,
                                datetime.now(UTC).isoformat(),
                            ),
                        )
                        new += 1
                current = {}
            elif line.startswith("Title:"):
                current["title"] = line[6:].strip()
            elif line.startswith("Link:"):
                current["url"] = line[5:].strip()
            elif line.startswith("Snippet:"):
                current["snippet"] = line[8:].strip()
        if current.get("title") and current.get("url"):
            sid = signal_id(current["url"])
            if not conn.execute("SELECT 1 FROM signals WHERE id=?", (sid,)).fetchone():
                conn.execute(
                    """
                    INSERT INTO signals
                    (id, title, url, snippet, source_name, tier, fetched_at, source_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'search')
                """,
                    (
                        sid,
                        current["title"],
                        current["url"],
                        current.get("snippet", ""),
                        source_name,
                        tier,
                        datetime.now(UTC).isoformat(),
                    ),
                )
                new += 1
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Brave timeout ({source_name})")
    except Exception as e:
        print(f"  ⚠️  Brave fout ({source_name}): {e}")
    return new


def should_run(source):
    return source.get("enabled", True) and source.get("status", "test") == "active"


def main():
    sources, skip_domains = load_sources()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    rss_new = 0
    search_new = 0

    print("📡 RSS/API-bronnen ophalen...")
    for source in sources:
        if not should_run(source):
            continue
        if source.get("type") != "rss":
            continue
        url = source.get("url", "")
        if not url or "PLACEHOLDER" in url:
            print(f"  [skip] {source['name']} — URL ontbreekt of placeholder")
            continue
        if any(domain in url for domain in skip_domains):
            print(f"  [skip] {source['name']} — domein in skip list")
            continue
        print(f"  [T{source.get('tier', '?')}] {source['name']}")
        rss_new += fetch_rss(url, source["name"], source.get("tier", 2), conn)
        conn.commit()

    print("\n🔍 Search fallback-bronnen ophalen...")
    for source in sources:
        if not should_run(source):
            continue
        if source.get("type") != "search":
            continue
        if source.get("provider") != "brave":
            print(f"  [skip] {source['name']} — onbekende search provider")
            continue
        query = source.get("query", "").strip()
        if not query:
            print(f"  [skip] {source['name']} — query ontbreekt")
            continue
        print(f"  [T{source.get('tier', '?')}] {source['name']}: \"{query}\"")
        search_new += fetch_brave(query, source["name"], source.get("tier", 2), conn)
        conn.commit()

    conn.close()
    total = rss_new + search_new
    print(f"\n✅ Klaar — RSS/API: {rss_new} nieuw | Search: {search_new} nieuw | Totaal nieuw: {total}")


if __name__ == "__main__":
    main()
