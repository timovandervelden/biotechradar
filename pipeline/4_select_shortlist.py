#!/usr/bin/env python3
"""
4_select_shortlist.py — Selecteer een compacte shortlist voor AI-analyse.

Principes:
- alleen filtered=1 items
- recent-first binnen een begrensd tijdvenster
- hoogste score daarna
- brondiversiteit bewaken
- simpele near-duplicate onderdrukking op titel-normalisatie
- search-items standaard lager gewogen dan rss-items
- output naar JSON en Markdown
"""

import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, UTC, timedelta
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
OUT_DIR = BASE / "data" / "shortlist"
DEFAULT_LIMIT = 15
PER_SOURCE_LIMIT = 3
LOOKBACK_DAYS = 21
SEARCH_PENALTY = 0.35
MIN_SCORE = 0.20
CLUSTER_BOOST = 0.45


def init_db(conn):
    try:
        conn.execute("ALTER TABLE signals ADD COLUMN shortlisted INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE signals ADD COLUMN shortlist_batch TEXT")
    except Exception:
        pass
    conn.commit()


def normalize_title(title):
    text = title.lower().strip()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_signature(title):
    norm = normalize_title(title)
    words = [w for w in norm.split() if len(w) > 2]
    return " ".join(words[:12])


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


def effective_date(published_at, fetched_at):
    return parse_dt(published_at) or parse_dt(fetched_at) or datetime.now(UTC)


def fetch_candidates(conn):
    return conn.execute(
        """
        SELECT id, title, url, snippet, source_name, source_type, tier, score, published_at, fetched_at,
               dedupe_sources_json, dedupe_source_count, duplicate_count,
               cluster_id, cluster_size, cluster_source_type_count, cluster_signal_strength, cluster_entity_json
        FROM signals
        WHERE filtered = 1 AND (is_canonical = 1 OR is_canonical IS NULL)
        """
    ).fetchall()


def rank_candidates(rows, lookback_days=LOOKBACK_DAYS):
    cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
    ranked = []

    for row in rows:
        (
            sid,
            title,
            url,
            snippet,
            source_name,
            source_type,
            tier,
            score,
            published_at,
            fetched_at,
            dedupe_sources_json,
            dedupe_source_count,
            duplicate_count,
            cluster_id,
            cluster_size,
            cluster_source_type_count,
            cluster_signal_strength,
            cluster_entity_json,
        ) = row

        eff_dt = effective_date(published_at, fetched_at)
        if eff_dt < cutoff:
            continue
        if (score or 0) < MIN_SCORE:
            continue

        effective_score = float(score or 0)
        if source_type == "search":
            effective_score -= SEARCH_PENALTY
        if (cluster_size or 0) >= 3 and (cluster_source_type_count or 0) >= 2:
            effective_score += CLUSTER_BOOST

        recency_days = max((datetime.now(UTC) - eff_dt).total_seconds() / 86400, 0)
        ranked.append(
            {
                "id": sid,
                "title": title,
                "url": url,
                "snippet": snippet,
                "source_name": source_name,
                "source_type": source_type,
                "tier": tier,
                "score": score,
                "effective_score": round(effective_score, 3),
                "published_at": published_at,
                "fetched_at": fetched_at,
                "effective_date": eff_dt,
                "recency_days": round(recency_days, 2),
                "dedupe_sources_json": dedupe_sources_json,
                "dedupe_source_count": dedupe_source_count or 1,
                "duplicate_count": duplicate_count or 0,
                "cluster_id": cluster_id,
                "cluster_size": cluster_size or 1,
                "cluster_source_type_count": cluster_source_type_count or 1,
                "cluster_signal_strength": cluster_signal_strength or 0,
                "cluster_entity_json": cluster_entity_json,
            }
        )

    ranked.sort(
        key=lambda x: (
            x["effective_date"],
            x["effective_score"],
            -(x["tier"] or 99),
        ),
        reverse=True,
    )
    return ranked


def select_shortlist(rows, limit=DEFAULT_LIMIT, per_source_limit=PER_SOURCE_LIMIT):
    selected = []
    source_counts = Counter()
    seen_signatures = set()

    for item in rows:
        source_name = item["source_name"]
        if source_counts[source_name] >= per_source_limit:
            continue

        signature = title_signature(item["title"])
        if signature in seen_signatures:
            continue

        item = dict(item)
        item["title_signature"] = signature
        item["effective_date"] = item["effective_date"].isoformat()
        try:
            item["dedupe_sources"] = json.loads(item.get("dedupe_sources_json") or "[]")
        except Exception:
            item["dedupe_sources"] = []
        try:
            item["cluster_entities"] = json.loads(item.get("cluster_entity_json") or "[]")
        except Exception:
            item["cluster_entities"] = []
        selected.append(item)
        source_counts[source_name] += 1
        seen_signatures.add(signature)

        if len(selected) >= limit:
            break

    return selected


def store_shortlist(conn, items, batch_id):
    conn.execute("UPDATE signals SET shortlisted = 0")
    for item in items:
        conn.execute(
            "UPDATE signals SET shortlisted = 1, shortlist_batch = ? WHERE id = ?",
            (batch_id, item["id"]),
        )
    conn.commit()


def write_outputs(items, batch_id):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUT_DIR / f"shortlist_{batch_id}.json"
    md_path = OUT_DIR / f"shortlist_{batch_id}.md"
    latest_json = OUT_DIR / "shortlist_latest.json"
    latest_md = OUT_DIR / "shortlist_latest.md"

    payload = {
        "batch_id": batch_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "count": len(items),
        "lookback_days": LOOKBACK_DAYS,
        "items": items,
    }
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    json_path.write_text(json_text)
    latest_json.write_text(json_text)

    lines = [
        f"# Shortlist {batch_id}",
        "",
        f"Gegenereerd: {payload['generated_at']}",
        f"Aantal items: {len(items)}",
        f"Lookback: laatste {LOOKBACK_DAYS} dagen",
        "",
    ]
    for i, item in enumerate(items, start=1):
        lines.extend(
            [
                f"## {i}. {item['title']}",
                f"- Bron: {item['source_name']} ({item['source_type']}, T{item['tier']})",
                f"- Score: {item['score']} (effective: {item['effective_score']})",
                f"- Datum: {item['published_at'] or item['fetched_at']}",
                f"- Ouderdom: {item['recency_days']} dagen",
                f"- Cross-bron: {item['dedupe_source_count']} bron(nen) — {', '.join(item.get('dedupe_sources', [])) or item['source_name']}",
                f"- Cluster: {item['cluster_id']} · size {item['cluster_size']} · source types {item['cluster_source_type_count']} · boost {'ja' if item['cluster_signal_strength'] else 'nee'}",
                f"- URL: {item['url']}",
                f"- Snippet: {item['snippet'][:400].strip()}",
                "",
            ]
        )
    md_text = "\n".join(lines)
    md_path.write_text(md_text)
    latest_md.write_text(md_text)

    return json_path, md_path


def main():
    batch_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    rows = fetch_candidates(conn)
    ranked = rank_candidates(rows)
    items = select_shortlist(ranked)
    store_shortlist(conn, items, batch_id)
    json_path, md_path = write_outputs(items, batch_id)
    conn.close()

    print(f"✅ Shortlist klaar — {len(items)} items")
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")


if __name__ == "__main__":
    main()
