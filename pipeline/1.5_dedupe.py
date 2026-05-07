#!/usr/bin/env python3
"""
1.5_dedupe.py — Detecteer near-duplicates tussen opgehaalde signalen.

Aanpak:
- werk op schoongemaakte title + snippet
- gebruik de eerste 500 tokens
- vergelijk token sets via Jaccard similarity
- threshold > 0.85 = duplicate
- bewaar de eerst-binnengekomen versie als canonical
- verrijk canonical record met lijst van bronnen waarop hetzelfde signaal ook gezien is

Doel:
- minder dubbele ruis in filter en shortlist
- basis leggen voor latere cross-bron versterking
"""

import json
import re
import sqlite3
from datetime import datetime, UTC
from html import unescape
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
TOKEN_LIMIT = 500
JACCARD_THRESHOLD = 0.85


def init_db(conn):
    migrations = [
        "ALTER TABLE signals ADD COLUMN canonical_id TEXT",
        "ALTER TABLE signals ADD COLUMN duplicate_of TEXT",
        "ALTER TABLE signals ADD COLUMN is_canonical INTEGER DEFAULT 1",
        "ALTER TABLE signals ADD COLUMN dedupe_tokens TEXT",
        "ALTER TABLE signals ADD COLUMN dedupe_sources_json TEXT",
        "ALTER TABLE signals ADD COLUMN dedupe_source_count INTEGER DEFAULT 1",
        "ALTER TABLE signals ADD COLUMN duplicate_count INTEGER DEFAULT 0",
        "ALTER TABLE signals ADD COLUMN dedupe_updated_at TEXT",
    ]
    for sql in migrations:
        try:
            conn.execute(sql)
        except Exception:
            pass
    conn.commit()


def clean_text(text):
    text = text or ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\w\s-]", " ", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenise(title, snippet):
    text = clean_text(f"{title} {snippet}")
    tokens = text.split()[:TOKEN_LIMIT]
    return tokens


def jaccard(a, b):
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    union = sa | sb
    if not union:
        return 0.0
    return len(sa & sb) / len(union)


def parse_dt(value):
    if not value:
        return None
    value = value.strip()
    formats = [
        None,
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            if fmt is None:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC)
        except Exception:
            continue
    return None


def fetch_rows(conn):
    rows = conn.execute(
        """
        SELECT id, title, snippet, source_name, fetched_at, published_at
        FROM signals
        ORDER BY COALESCE(fetched_at, published_at, '') ASC, id ASC
        """
    ).fetchall()
    out = []
    for row in rows:
        sid, title, snippet, source_name, fetched_at, published_at = row
        tokens = tokenise(title, snippet)
        out.append(
            {
                "id": sid,
                "title": title or "",
                "snippet": snippet or "",
                "source_name": source_name or "unknown",
                "fetched_at": fetched_at,
                "published_at": published_at,
                "dt": parse_dt(fetched_at) or parse_dt(published_at) or datetime.now(UTC),
                "tokens": tokens,
            }
        )
    return out


def reset_dedupe_fields(conn):
    conn.execute(
        """
        UPDATE signals
        SET canonical_id = id,
            duplicate_of = NULL,
            is_canonical = 1,
            dedupe_sources_json = json_array(source_name),
            dedupe_source_count = 1,
            duplicate_count = 0,
            dedupe_updated_at = ?
        """,
        (datetime.now(UTC).isoformat(),),
    )
    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    reset_dedupe_fields(conn)
    rows = fetch_rows(conn)

    canonicals = []
    duplicate_pairs = 0
    canonical_meta = {}

    for row in rows:
        matched = None
        best_score = 0.0
        for canon in canonicals:
            score = jaccard(row["tokens"], canon["tokens"])
            if score > JACCARD_THRESHOLD and score > best_score:
                matched = canon
                best_score = score

        if matched is None:
            canonicals.append(row)
            canonical_meta[row["id"]] = {
                "sources": [row["source_name"]],
                "member_ids": [row["id"]],
                "tokens": row["tokens"],
            }
            conn.execute(
                "UPDATE signals SET dedupe_tokens = ? WHERE id = ?",
                (json.dumps(row["tokens"], ensure_ascii=False), row["id"]),
            )
        else:
            duplicate_pairs += 1
            meta = canonical_meta[matched["id"]]
            if row["source_name"] not in meta["sources"]:
                meta["sources"].append(row["source_name"])
            meta["member_ids"].append(row["id"])
            conn.execute(
                """
                UPDATE signals
                SET canonical_id = ?,
                    duplicate_of = ?,
                    is_canonical = 0,
                    dedupe_tokens = ?
                WHERE id = ?
                """,
                (
                    matched["id"],
                    matched["id"],
                    json.dumps(row["tokens"], ensure_ascii=False),
                    row["id"],
                ),
            )

    updated_at = datetime.now(UTC).isoformat()
    for canonical_id, meta in canonical_meta.items():
        conn.execute(
            """
            UPDATE signals
            SET dedupe_sources_json = ?,
                dedupe_source_count = ?,
                duplicate_count = ?,
                dedupe_updated_at = ?
            WHERE id = ?
            """,
            (
                json.dumps(meta["sources"], ensure_ascii=False),
                len(meta["sources"]),
                max(len(meta["member_ids"]) - 1, 0),
                updated_at,
                canonical_id,
            ),
        )

    conn.commit()
    canonical_count = conn.execute("SELECT COUNT(*) FROM signals WHERE is_canonical = 1").fetchone()[0]
    duplicate_count = conn.execute("SELECT COUNT(*) FROM signals WHERE is_canonical = 0").fetchone()[0]
    conn.close()

    print(f"✅ Dedupe klaar — canonical: {canonical_count} | duplicates: {duplicate_count} | pairs matched: {duplicate_pairs}")


if __name__ == "__main__":
    main()
