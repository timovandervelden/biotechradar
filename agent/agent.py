#!/usr/bin/env python3
"""
agent.py — Interactieve Biotech Radar Agent
Beantwoordt vragen op basis van de signals DB
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "data" / "signals.db"

SYSTEM_PROMPT = """Je bent de Biotech Radar Agent voor precision fermentation en NL biotech.

Je hebt toegang tot een database van gescoorde signalen opgehaald uit Tier 1 bronnen.
Beantwoord vragen op basis van deze data — niet vanuit eigen kennis.

Regels:
- Altijd bronvermelding (url + datum)
- Geen overheidsbronnen als primaire input
- Kort en concreet, geen beleidspoëzie
- Als je iets niet weet: zeg het

Context: je spreekt met Timo, AI Consultant bij RVO/Sopra Steria.
Focus: precision fermentation opschaling, Novel Food, EFSA, NL industriebeleid.
"""

def get_context(question, days_back=14):
    """Haal relevante signalen op uit DB als context"""
    conn = sqlite3.connect(DB_PATH)
    since = (datetime.utcnow() - timedelta(days=days_back)).isoformat()

    rows = conn.execute("""
        SELECT title, url, snippet, source_name, score, fetched_at
        FROM signals
        WHERE filtered = 1
          AND fetched_at > ?
        ORDER BY score DESC
        LIMIT 15
    """, (since,)).fetchall()
    conn.close()

    if not rows:
        return "Geen recente signalen in database. Draai eerst 1_ophalen.py."

    context = f"BESCHIKBARE SIGNALEN (laatste {days_back} dagen):\n\n"
    for r in rows:
        context += f"- **{r[0]}**\n  Bron: {r[3]} | Score: {r[4]} | {r[5][:10]}\n  {r[2]}\n  URL: {r[1]}\n\n"
    return context

def ask_llm(question, context):
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
                {"role": "user", "content": question}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except ImportError:
        return "[OpenAI niet beschikbaar — installeer: pip install openai]"
    except Exception as e:
        return f"[Fout: {e}]"

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Vraag: ").strip()

    if not question:
        print("Geen vraag opgegeven")
        return

    print(f"\n🔍 Zoek context voor: {question}\n")
    context = get_context(question)
    answer = ask_llm(question, context)
    print(f"🧬 Biotech Radar Agent:\n\n{answer}\n")

if __name__ == "__main__":
    main()
