#!/usr/bin/env python3
"""
6_weekbriefing.py — Bouw een compacte weekly radar briefing op basis van analyse-output.

Prototype-keuzes:
- gebruikt signal_analysis + signals
- maakt een leesbare markdown briefing
- groepeert op actiecategorie en signaaltype
- geen extra AI-call; eerst deterministische briefing
"""

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, UTC
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
OUT_DIR = BASE / "data" / "briefings"


def fetch_rows(conn):
    return conn.execute(
        """
        SELECT
            sa.signal_id,
            sa.signal_type,
            sa.policy_relevance_score,
            sa.action_type,
            sa.summary,
            sa.rationale,
            sa.uncertainty,
            sa.analysed_at,
            s.title,
            s.url,
            s.source_name,
            s.source_type,
            s.score,
            s.published_at,
            s.snippet
        FROM signal_analysis sa
        JOIN signals s ON s.id = sa.signal_id
        ORDER BY sa.policy_relevance_score DESC, s.score DESC, sa.analysed_at DESC
        """
    ).fetchall()


def row_to_item(row):
    (
        signal_id,
        signal_type,
        policy_relevance_score,
        action_type,
        summary,
        rationale,
        uncertainty,
        analysed_at,
        title,
        url,
        source_name,
        source_type,
        score,
        published_at,
        snippet,
    ) = row
    return {
        "signal_id": signal_id,
        "signal_type": signal_type,
        "policy_relevance_score": policy_relevance_score,
        "action_type": action_type,
        "summary": summary,
        "rationale": rationale,
        "uncertainty": uncertainty,
        "analysed_at": analysed_at,
        "title": title,
        "url": url,
        "source_name": source_name,
        "source_type": source_type,
        "score": score,
        "published_at": published_at,
        "snippet": snippet,
    }


def build_overview(items):
    signal_counts = Counter(item["signal_type"] for item in items)
    action_counts = Counter(item["action_type"] for item in items)
    source_counts = Counter(item["source_name"] for item in items)
    return {
        "total_items": len(items),
        "signal_counts": dict(signal_counts),
        "action_counts": dict(action_counts),
        "source_counts": dict(source_counts),
    }


def group_items(items):
    by_action = defaultdict(list)
    by_signal = defaultdict(list)
    for item in items:
        by_action[item["action_type"]].append(item)
        by_signal[item["signal_type"]].append(item)
    return by_action, by_signal


def top_items(items, n=5):
    return sorted(
        items,
        key=lambda x: (x["policy_relevance_score"] or 0, x["score"] or 0),
        reverse=True,
    )[:n]


def write_outputs(items):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    batch_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    overview = build_overview(items)
    by_action, by_signal = group_items(items)

    payload = {
        "briefing_batch": batch_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "overview": overview,
        "top_items": top_items(items, n=5),
        "by_action": by_action,
        "by_signal": by_signal,
    }

    json_path = OUT_DIR / f"weekly_briefing_{batch_id}.json"
    md_path = OUT_DIR / f"weekly_briefing_{batch_id}.md"
    latest_json = OUT_DIR / "weekly_briefing_latest.json"
    latest_md = OUT_DIR / "weekly_briefing_latest.md"

    serializable = {
        **payload,
        "by_action": {k: v for k, v in by_action.items()},
        "by_signal": {k: v for k, v in by_signal.items()},
    }
    json_text = json.dumps(serializable, ensure_ascii=False, indent=2)
    json_path.write_text(json_text)
    latest_json.write_text(json_text)

    lines = [
        "# Weekly Biotech Radar Briefing",
        "",
        f"Gegenereerd: {payload['generated_at']}",
        f"Aantal geanalyseerde signalen: {overview['total_items']}",
        "",
        "## Overzicht",
        f"- Signaaltypes: {overview['signal_counts']}",
        f"- Actiecategorieën: {overview['action_counts']}",
        f"- Bronnen: {overview['source_counts']}",
        "",
        "## Belangrijkste bewegingen",
        "",
    ]

    for i, item in enumerate(payload["top_items"], start=1):
        lines.extend(
            [
                f"### {i}. {item['title']}",
                f"- Type: {item['signal_type']}",
                f"- Actie: {item['action_type']}",
                f"- Policy relevance: {item['policy_relevance_score']}/5",
                f"- Bron: {item['source_name']} ({item['source_type']})",
                f"- Samenvatting: {item['summary']}",
                f"- Waarom relevant: {item['rationale']}",
                f"- URL: {item['url']}",
                "",
            ]
        )

    section_order = ["keuze", "interventie", "monitoring", "escalatie"]
    lines.append("## Actiegericht overzicht")
    lines.append("")
    for section in section_order:
        lines.append(f"### {section.capitalize()}")
        lines.append("")
        entries = by_action.get(section, [])
        if not entries:
            lines.append("- Geen signalen in deze categorie.")
            lines.append("")
            continue
        for item in entries:
            lines.append(f"- **{item['title']}** — {item['summary']} ({item['source_name']})")
        lines.append("")

    signal_order = ["beleidsimpuls", "trend", "weak_signal", "hype"]
    lines.append("## Type signalen")
    lines.append("")
    for section in signal_order:
        lines.append(f"### {section}")
        lines.append("")
        entries = by_signal.get(section, [])
        if not entries:
            lines.append("- Geen signalen in deze categorie.")
            lines.append("")
            continue
        for item in entries:
            lines.append(f"- **{item['title']}** — {item['summary']} ({item['action_type']})")
        lines.append("")

    lines.append("## Ruwe observatie")
    lines.append("")
    if not items:
        lines.append("- Geen geanalyseerde signalen beschikbaar.")
    else:
        dominant_action = overview['action_counts'] and max(overview['action_counts'], key=overview['action_counts'].get)
        dominant_signal = overview['signal_counts'] and max(overview['signal_counts'], key=overview['signal_counts'].get)
        lines.append(f"- Dominante actiecategorie nu: **{dominant_action}**")
        lines.append(f"- Dominant signaaltype nu: **{dominant_signal}**")
        lines.append("- Dit is nog een deterministische prototype-briefing; redactionele LLM-synthese kan hier later overheen.")

    md_text = "\n".join(lines)
    md_path.write_text(md_text)
    latest_md.write_text(md_text)
    return json_path, md_path, payload


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = fetch_rows(conn)
    conn.close()
    items = [row_to_item(row) for row in rows]
    json_path, md_path, payload = write_outputs(items)
    print(f"✅ Weekly briefing klaar — {len(items)} items")
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")


if __name__ == "__main__":
    main()
