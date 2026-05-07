#!/usr/bin/env python3
"""
3_prioriteren.py — Scoren op PESTLE-rubric
"""

import re
import sqlite3
import yaml
from pathlib import Path

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
RUBRIC = BASE / "config" / "rubric.yaml"


def contains_term(text, term):
    pattern = rf"(?<!\w){re.escape(term.lower())}(?!\w)"
    return re.search(pattern, text) is not None


def contains_any(text, terms):
    return any(contains_term(text, term) for term in terms)


def score_signal(text, weights, keyword_map, bonus_rules=None):
    text = text.lower()
    total = 0.0
    for category, keywords in keyword_map.items():
        hits = sum(1 for kw in keywords if contains_term(text, kw))
        weight = weights.get(category, 0)
        total += hits * weight
    if bonus_rules:
        for rule in bonus_rules:
            if contains_any(text, rule["terms"]):
                total += rule["weight"]
    return round(min(total, 10.0), 2)


def main():
    with open(RUBRIC) as f:
        rubric = yaml.safe_load(f)

    weights = dict(rubric["pestle"])
    weights["Policy_early"] = 0.40
    weights["Technology"] = 0.25
    weights["Economic"] = 0.30

    keyword_map = rubric.get("pestle_keywords", {})
    if not keyword_map:
        raise ValueError("rubric.yaml mist 'pestle_keywords'; scoring heeft één bron van waarheid nodig.")

    policy_markers = rubric.get("policy_markers", {})
    signal_keywords = rubric.get("signal_keywords", {})

    bonus_rules = []
    if policy_markers.get("regulatory"):
        bonus_rules.append({"terms": policy_markers["regulatory"], "weight": 0.15})
    if policy_markers.get("strategic"):
        bonus_rules.append({"terms": policy_markers["strategic"], "weight": 0.15})
    if signal_keywords.get("market_signals"):
        bonus_rules.append({"terms": signal_keywords["market_signals"], "weight": 0.10})

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, title, snippet, full_text FROM signals WHERE filtered = 1 AND (is_canonical = 1 OR is_canonical IS NULL)"
    ).fetchall()

    enriched_count = 0
    for sid, title, snippet, full_text in rows:
        if full_text and full_text not in ('SKIP', 'FAILED', None):
            text = f"{title} {full_text}"
            enriched_count += 1
        else:
            text = f"{title} {snippet}"
        score = score_signal(text, weights, keyword_map, bonus_rules)
        conn.execute("UPDATE signals SET score = ? WHERE id = ?", (score, sid))

    conn.commit()
    conn.close()
    print(f"✅ Prioritering klaar — {len(rows)} signalen gescoord ({enriched_count} op full-text)")


if __name__ == "__main__":
    main()
