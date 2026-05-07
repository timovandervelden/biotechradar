#!/usr/bin/env python3
"""
5_analyse_llm.py — Analyseer shortlist-items met een compacte LLM-call.

Prototype-keuzes:
- leest shortlist_latest.json
- één batch-call voor lage tokenkosten
- kan veilig draaien met --dry-run
- schrijft output naar data/analyses/
- slaat resultaten op in SQLite
"""

import argparse
import json
import sqlite3
from datetime import datetime, UTC
from pathlib import Path

import yaml
from openai import OpenAI

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
SHORTLIST_PATH = BASE / "data" / "shortlist" / "shortlist_latest.json"
PROMPTS_PATH = BASE / "config" / "prompts.yaml"
OUT_DIR = BASE / "data" / "analyses"


def load_shortlist():
    if not SHORTLIST_PATH.exists():
        raise FileNotFoundError(f"Geen shortlist gevonden: {SHORTLIST_PATH}")
    return json.loads(SHORTLIST_PATH.read_text())


def load_prompt_config():
    data = yaml.safe_load(PROMPTS_PATH.read_text())
    return data["analysis"]


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_analysis (
            signal_id TEXT PRIMARY KEY,
            shortlist_batch TEXT,
            analysis_batch TEXT,
            signal_type TEXT,
            policy_relevance_score INTEGER,
            action_type TEXT,
            summary TEXT,
            rationale TEXT,
            uncertainty TEXT,
            analysed_at TEXT
        )
        """
    )
    try:
        conn.execute("ALTER TABLE signals ADD COLUMN analysis_status TEXT")
    except Exception:
        pass
    conn.commit()


def build_user_prompt(template, shortlist_items):
    cluster_map = {}
    singletons = []

    for item in shortlist_items:
        cluster_id = item.get("cluster_id")
        cluster_size = item.get("cluster_size", 1) or 1
        cluster_source_type_count = item.get("cluster_source_type_count", 1) or 1

        if cluster_id and cluster_size >= 3 and cluster_source_type_count >= 2:
            cluster = cluster_map.setdefault(cluster_id, {
                "id": f"cluster::{cluster_id}",
                "kind": "cluster",
                "cluster_id": cluster_id,
                "cluster_size": cluster_size,
                "cluster_source_type_count": cluster_source_type_count,
                "cluster_entities": item.get("cluster_entities", []),
                "items": [],
            })
            cluster["items"].append({
                "id": item["id"],
                "title": item["title"],
                "source_name": item["source_name"],
                "source_type": item["source_type"],
                "tier": item["tier"],
                "score": item["score"],
                "published_at": item["published_at"],
                "snippet": item["snippet"][:400],
                "url": item["url"],
            })
        else:
            singletons.append({
                "id": item["id"],
                "kind": "item",
                "title": item["title"],
                "source_name": item["source_name"],
                "source_type": item["source_type"],
                "tier": item["tier"],
                "score": item["score"],
                "published_at": item["published_at"],
                "snippet": item["snippet"][:700],
                "url": item["url"],
                "cluster_id": item.get("cluster_id"),
                "cluster_size": cluster_size,
                "cluster_source_type_count": cluster_source_type_count,
                "cluster_entities": item.get("cluster_entities", []),
            })

    compact_items = list(cluster_map.values()) + singletons
    return template.replace("{items_json}", json.dumps(compact_items, ensure_ascii=False, indent=2))


def fake_analysis(shortlist):
    items = []
    for item in shortlist["items"]:
        score = item.get("score", 0) or 0
        title = item.get("title") or item.get("id", "cluster")
        items.append(
            {
                "id": item["id"],
                "signal_type": "beleidsimpuls" if score >= 1.0 else "monitoring",
                "policy_relevance_score": 4 if score >= 1.0 else 2,
                "action_type": "monitoring" if score < 1.2 else "keuze",
                "summary": f"Prototype-analyse voor: {title}",
                "rationale": "Dry-run placeholder; nog geen echte modelduiding.",
                "uncertainty": "",
            }
        )
    return {
        "batch_summary": "Dry-run output; bedoeld om pipeline en opslag te testen.",
        "items": items,
    }


def call_model(config, user_prompt):
    client = OpenAI()
    response = client.responses.create(
        model=config.get("model", "gpt-4.1-mini"),
        temperature=config.get("temperature", 0.2),
        max_output_tokens=config.get("max_output_tokens", 2500),
        input=[
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = getattr(response, "output_text", "")
    if not text:
        raise ValueError("Model gaf geen output_text terug")
    return json.loads(text)


def store_results(conn, shortlist, analysis_batch, result):
    analysed_at = datetime.now(UTC).isoformat()
    shortlist_batch = shortlist.get("batch_id")

    for item in result.get("items", []):
        conn.execute(
            """
            INSERT INTO signal_analysis (
                signal_id, shortlist_batch, analysis_batch, signal_type,
                policy_relevance_score, action_type, summary, rationale,
                uncertainty, analysed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(signal_id) DO UPDATE SET
                shortlist_batch=excluded.shortlist_batch,
                analysis_batch=excluded.analysis_batch,
                signal_type=excluded.signal_type,
                policy_relevance_score=excluded.policy_relevance_score,
                action_type=excluded.action_type,
                summary=excluded.summary,
                rationale=excluded.rationale,
                uncertainty=excluded.uncertainty,
                analysed_at=excluded.analysed_at
            """,
            (
                item["id"],
                shortlist_batch,
                analysis_batch,
                item["signal_type"],
                item["policy_relevance_score"],
                item["action_type"],
                item["summary"],
                item.get("rationale", ""),
                item.get("uncertainty", ""),
                analysed_at,
            ),
        )
        conn.execute(
            "UPDATE signals SET analysis_status = ? WHERE id = ?",
            (analysis_batch, item["id"]),
        )
    conn.commit()


def write_outputs(shortlist, analysis_batch, result, dry_run=False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "analysis_batch": analysis_batch,
        "shortlist_batch": shortlist.get("batch_id"),
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": dry_run,
        "batch_summary": result.get("batch_summary", ""),
        "items": result.get("items", []),
    }
    json_path = OUT_DIR / f"analysis_{analysis_batch}.json"
    md_path = OUT_DIR / f"analysis_{analysis_batch}.md"
    latest_json = OUT_DIR / "analysis_latest.json"
    latest_md = OUT_DIR / "analysis_latest.md"

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    json_path.write_text(text)
    latest_json.write_text(text)

    lines = [
        f"# Analyse {analysis_batch}",
        "",
        f"Shortlist batch: {payload['shortlist_batch']}",
        f"Dry run: {dry_run}",
        f"Samenvatting: {payload['batch_summary']}",
        "",
    ]
    for i, item in enumerate(payload["items"], start=1):
        lines.extend(
            [
                f"## {i}. {item['id']}",
                f"- Type: {item['signal_type']}",
                f"- Policy relevance: {item['policy_relevance_score']}/5",
                f"- Actie: {item['action_type']}",
                f"- Summary: {item['summary']}",
                f"- Rationale: {item['rationale']}",
                f"- Uncertainty: {item.get('uncertainty', '')}",
                "",
            ]
        )
    md_text = "\n".join(lines)
    md_path.write_text(md_text)
    latest_md.write_text(md_text)
    return json_path, md_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Geen echte LLM-call; alleen pipeline testen")
    args = parser.parse_args()

    shortlist = load_shortlist()
    config = load_prompt_config()
    user_prompt = build_user_prompt(config["user_prompt_template"], shortlist["items"])
    analysis_batch = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if args.dry_run:
        result = fake_analysis(shortlist)
    else:
        result = call_model(config, user_prompt)

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    store_results(conn, shortlist, analysis_batch, result)
    conn.close()

    json_path, md_path = write_outputs(shortlist, analysis_batch, result, dry_run=args.dry_run)
    print(f"✅ Analyse klaar — {len(result.get('items', []))} items")
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")


if __name__ == "__main__":
    main()
