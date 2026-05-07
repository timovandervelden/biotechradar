#!/usr/bin/env python3
"""
3.5_cluster.py — Cluster relevante signalen op entiteitsoverlap + tijdsvenster + bronspreiding.

Prototype-aanpak:
- alleen canonical, filtered=1 signalen
- entiteiten via lichte extractie: keyword-phrases + acronyms + title-case phrases
- 14-daags tijdsvenster
- clustercomponenten op entity overlap + temporal proximity
- cluster metadata opslaan per item

Doel:
- van losse signalen naar samenkomende patronen
- basis voor shortlist-boost en cluster-level LLM-duiding
"""

import json
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, UTC, timedelta
from html import unescape
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
RUBRIC = BASE / "config" / "rubric.yaml"
WINDOW_DAYS = 14
MIN_CLUSTER_SIZE_FOR_SIGNAL = 3
MIN_SOURCE_TYPES_FOR_SIGNAL = 2

STOP_PHRASES = {
    "the", "and", "for", "with", "from", "this", "that", "food", "news", "update",
    "de", "het", "een", "van", "met", "voor", "nieuws", "artikel"
}


def init_db(conn):
    migrations = [
        "ALTER TABLE signals ADD COLUMN cluster_id TEXT",
        "ALTER TABLE signals ADD COLUMN cluster_size INTEGER DEFAULT 1",
        "ALTER TABLE signals ADD COLUMN cluster_source_count INTEGER DEFAULT 1",
        "ALTER TABLE signals ADD COLUMN cluster_source_type_count INTEGER DEFAULT 1",
        "ALTER TABLE signals ADD COLUMN cluster_entity_json TEXT",
        "ALTER TABLE signals ADD COLUMN cluster_member_ids_json TEXT",
        "ALTER TABLE signals ADD COLUMN cluster_signal_strength INTEGER DEFAULT 0",
        "ALTER TABLE signals ADD COLUMN cluster_updated_at TEXT",
    ]
    for sql in migrations:
        try:
            conn.execute(sql)
        except Exception:
            pass
    conn.commit()


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


def clean_text(text):
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_phrase(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s&+\-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_phrase_hints():
    rubric = yaml.safe_load(RUBRIC.read_text())
    phrases = set()
    for group in rubric.get("domain_keywords", {}).values():
        if isinstance(group, list):
            phrases.update(normalize_phrase(x) for x in group if len(normalize_phrase(x)) >= 3)
    for group in rubric.get("policy_markers", {}).values():
        if isinstance(group, list):
            phrases.update(normalize_phrase(x) for x in group if len(normalize_phrase(x)) >= 3)
    for group in rubric.get("signal_keywords", {}).values():
        if isinstance(group, list):
            phrases.update(normalize_phrase(x) for x in group if len(normalize_phrase(x)) >= 3)
    return sorted(phrases, key=len, reverse=True)


def extract_entities(title, snippet, phrase_hints):
    raw = clean_text(f"{title} {snippet}")
    lower = raw.lower()
    entities = set()

    for phrase in phrase_hints:
        if phrase and phrase in lower and len(phrase) >= 4:
            entities.add(phrase)

    for match in re.findall(r"\b[A-Z]{2,}\b", raw):
        entities.add(match.lower())

    for match in re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b", raw):
        norm = normalize_phrase(match)
        if norm and norm not in STOP_PHRASES and len(norm) >= 4:
            entities.add(norm)

    tokens = [t for t in re.findall(r"[a-z0-9][a-z0-9&+\-/]*", lower) if len(t) >= 4]
    for token in tokens:
        if token not in STOP_PHRASES and token in lower:
            if token in {"efsa", "novel", "food", "biotech", "fermentation", "protein", "netherlands", "hollandbio", "eic", "eu"}:
                entities.add(token)

    return sorted(entities)


def fetch_items(conn):
    rows = conn.execute(
        """
        SELECT id, title, snippet, source_name, source_type, published_at, fetched_at
        FROM signals
        WHERE filtered = 1 AND (is_canonical = 1 OR is_canonical IS NULL)
        ORDER BY COALESCE(published_at, fetched_at) ASC, id ASC
        """
    ).fetchall()
    items = []
    phrase_hints = load_phrase_hints()
    for row in rows:
        sid, title, snippet, source_name, source_type, published_at, fetched_at = row
        dt = parse_dt(published_at) or parse_dt(fetched_at) or datetime.now(UTC)
        entities = extract_entities(title or "", snippet or "", phrase_hints)
        items.append({
            "id": sid,
            "title": title or "",
            "snippet": snippet or "",
            "source_name": source_name or "unknown",
            "source_type": source_type or "unknown",
            "dt": dt,
            "entities": entities,
        })
    return items


def overlap(a, b):
    return bool(set(a) & set(b))


def close_in_time(a, b, days=WINDOW_DAYS):
    return abs((a - b).total_seconds()) <= days * 86400


def union_find(items):
    parent = {item["id"]: item["id"] for item in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(items):
        if not a["entities"]:
            continue
        for b in items[i + 1:]:
            if not b["entities"]:
                continue
            if not close_in_time(a["dt"], b["dt"]):
                if b["dt"] - a["dt"] > timedelta(days=WINDOW_DAYS):
                    break
                continue
            if overlap(a["entities"], b["entities"]):
                union(a["id"], b["id"])

    clusters = defaultdict(list)
    for item in items:
        clusters[find(item["id"])] .append(item)
    return clusters


def store_clusters(conn, clusters):
    updated_at = datetime.now(UTC).isoformat()
    conn.execute(
        """
        UPDATE signals
        SET cluster_id = id,
            cluster_size = 1,
            cluster_source_count = 1,
            cluster_source_type_count = 1,
            cluster_entity_json = NULL,
            cluster_member_ids_json = json_array(id),
            cluster_signal_strength = 0,
            cluster_updated_at = ?
        WHERE filtered = 1 AND (is_canonical = 1 OR is_canonical IS NULL)
        """,
        (updated_at,),
    )

    for root_id, members in clusters.items():
        member_ids = [m["id"] for m in members]
        source_names = sorted({m["source_name"] for m in members})
        source_types = sorted({m["source_type"] for m in members})
        all_entities = sorted({e for m in members for e in m["entities"]})
        cluster_size = len(member_ids)
        source_type_count = len(source_types)
        signal_strength = 1 if cluster_size >= MIN_CLUSTER_SIZE_FOR_SIGNAL and source_type_count >= MIN_SOURCE_TYPES_FOR_SIGNAL else 0

        for member in members:
            conn.execute(
                """
                UPDATE signals
                SET cluster_id = ?,
                    cluster_size = ?,
                    cluster_source_count = ?,
                    cluster_source_type_count = ?,
                    cluster_entity_json = ?,
                    cluster_member_ids_json = ?,
                    cluster_signal_strength = ?,
                    cluster_updated_at = ?
                WHERE id = ?
                """,
                (
                    root_id,
                    cluster_size,
                    len(source_names),
                    source_type_count,
                    json.dumps(all_entities, ensure_ascii=False),
                    json.dumps(member_ids, ensure_ascii=False),
                    signal_strength,
                    updated_at,
                    member["id"],
                ),
            )
    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    items = fetch_items(conn)
    clusters = union_find(items)
    store_clusters(conn, clusters)

    total_clusters = len(clusters)
    boosted_clusters = sum(1 for members in clusters.values() if len(members) >= MIN_CLUSTER_SIZE_FOR_SIGNAL and len({m['source_type'] for m in members}) >= MIN_SOURCE_TYPES_FOR_SIGNAL)
    conn.close()
    print(f"✅ Clustering klaar — clusters: {total_clusters} | boost-waardige clusters: {boosted_clusters}")


if __name__ == "__main__":
    main()
