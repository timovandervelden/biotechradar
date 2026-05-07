#!/usr/bin/env python3
"""
4_synthese.py — LLM-duiding via OpenClaw (geen aparte API key nodig)
Gebruikt het geconfigureerde model in OpenClaw.
"""

import sqlite3
import subprocess
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"
OUTPUT = BASE / "data" / "briefing_latest.md"

TOP_N = 7

def get_top_signals(conn):
    rows = conn.execute("""
        SELECT id, title, url, snippet, source_name, score
        FROM signals
        WHERE filtered = 1 AND score > 0
        ORDER BY score DESC
        LIMIT ?
    """, (TOP_N,)).fetchall()
    return [
        {"id": r[0], "title": r[1], "url": r[2],
         "snippet": r[3], "source_name": r[4], "score": r[5]}
        for r in rows
    ]

def build_prompt(signals):
    items = "\n".join([
        f"- {s['title']} (score: {s['score']}, bron: {s['source_name']})\n  {s['snippet'][:200]}\n  {s['url']}"
        for s in signals
    ])
    return f"""Analyseer deze biotech-signalen en schrijf een beknopte briefing in het Nederlands (max 350 woorden):

1. Wat zijn de 2-3 meest urgente ontwikkelingen voor NL biotech / precision fermentation?
2. Wat betekent dit voor opschaling in Nederland?
3. Concreet actiepunt voor iemand bij RVO?

Toon: zakelijk, to-the-point, geen beleidspoëzie.

SIGNALEN:
{items}

BRIEFING:"""

def synthesize_via_openclaw(prompt):
    """Roept OpenClaw aan als subproces voor LLM-synthese"""
    try:
        result = subprocess.run(
            ["openclaw", "ask", "--no-stream", prompt],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        # Fallback: geen LLM, gewoon de top signalen formatteren
        return None
    except Exception:
        return None

def format_without_llm(signals):
    """Simpele briefing zonder LLM als fallback"""
    lines = [f"**Top signalen deze run:**\n"]
    for i, s in enumerate(signals, 1):
        lines.append(f"{i}. **{s['title']}**")
        lines.append(f"   Bron: {s['source_name']} | Score: {s['score']}")
        lines.append(f"   {s['snippet'][:200]}")
        lines.append(f"   [{s['url']}]({s['url']})\n")
    return "\n".join(lines)

def main():
    conn = sqlite3.connect(DB_PATH)
    signals = get_top_signals(conn)

    if not signals:
        print("Geen signalen gevonden voor synthese")
        return

    prompt = build_prompt(signals)
    briefing = synthesize_via_openclaw(prompt)

    if not briefing:
        print("⚠️  LLM niet beschikbaar — fallback naar gestructureerde lijst")
        briefing = format_without_llm(signals)

    date = datetime.utcnow().strftime("%Y-%m-%d")
    content = f"""# Biotech Radar Briefing — {date}

## Top {len(signals)} signalen

{chr(10).join([f"**{i+1}.** [{s['title']}]({s['url']}) — score {s['score']} ({s['source_name']})" for i, s in enumerate(signals)])}

## Duiding

{briefing}

---
*Gegenereerd: {datetime.utcnow().isoformat()} UTC*
"""

    OUTPUT.write_text(content)

    for s in signals:
        conn.execute("UPDATE signals SET summary = ? WHERE id = ?",
                     (briefing[:500], s["id"]))
    conn.commit()
    conn.close()

    print(f"✅ Briefing opgeslagen: {OUTPUT}")
    print(f"\n--- Preview ---\n{briefing[:500]}")

if __name__ == "__main__":
    main()
