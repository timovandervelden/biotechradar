#!/usr/bin/env python3
"""
2_filteren.py — Ruis eruit filteren op basis van rubric keywords
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


def main():
    with open(RUBRIC) as f:
        rubric = yaml.safe_load(f)

    domain = rubric["domain_keywords"]
    signal = rubric["signal_keywords"]

    core = [k.lower() for k in domain["core"]]
    supporting = [k.lower() for k in domain.get("supporting", [])]
    weak = [k.lower() for k in domain.get("weak", [])]
    food_scope = [k.lower() for k in domain.get("food_scope", [])]
    exclude = [k.lower() for k in domain.get("exclude_if_only", [])]
    known_gov = [k.lower() for k in domain.get("known_to_government", [])]
    change_signals = [k.lower() for k in signal.get("change_signals", [])]

    all_domain_keywords = core + supporting + weak
    secondary_relevance = supporting + weak

    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE signals SET filtered = 0, score = 0")
    rows = conn.execute("SELECT id, title, snippet FROM signals WHERE is_canonical = 1 OR is_canonical IS NULL").fetchall()

    kept = 0
    dropped = 0

    for sid, title, snippet in rows:
        text = re.sub('<[^>]+>', '', f"{title} {snippet}").lower()

        has_domain = contains_any(text, all_domain_keywords)
        has_change = contains_any(text, change_signals)
        has_secondary_relevance = contains_any(text, secondary_relevance)
        has_exclude = contains_any(text, exclude)
        has_core = contains_any(text, core)
        has_food_scope = contains_any(text, food_scope)
        is_only_gov = contains_any(text, known_gov) and not has_core and not has_change

        is_relevant = has_domain or (has_change and has_secondary_relevance)

        if is_relevant and not (has_exclude and not has_core) and not is_only_gov and has_food_scope:
            conn.execute("UPDATE signals SET filtered = 1 WHERE id = ? OR canonical_id = ?", (sid, sid))
            kept += 1
        else:
            conn.execute("UPDATE signals SET filtered = -1 WHERE id = ? OR canonical_id = ?", (sid, sid))
            dropped += 1

    conn.commit()
    conn.close()
    print(f"✅ Filter klaar — {kept} relevant, {dropped} verwijderd")


if __name__ == "__main__":
    main()
