# Biotech Radar

Geautomatiseerde pipeline + interactieve agent voor NL biotech signalen.

## Structuur

```
pipeline/
  1_ophalen.py     → Brave Search → SQLite
  2_filteren.py    → keyword filter
  3_prioriteren.py → PESTLE scoring
  4_synthese.py    → LLM briefing
  5_publiceren.py  → Telegram
agent/
  agent.py         → interactieve queries op DB
config/
  rubric.yaml      → PESTLE weging + thema's
  sources.yaml     → Tier 1/2 bronnen
data/
  signals.db       → gedeeld geheugen
  briefing_latest.md
```

## Eerste run

```bash
pip install pyyaml openai
python3 pipeline/1_ophalen.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/4_synthese.py   # vereist OPENAI_API_KEY
```

## Interactief

```bash
python3 agent/agent.py "Wat weet je over EFSA deze week?"
python3 agent/agent.py "Vergelijk dit met vorige maand"
python3 agent/agent.py "Wat betekent dit voor mijn dossier Novel Food?"
```

## Cron (dagelijks 06:00)

```
0 6 * * * /home/brewuser/projects/biotech-radar/cron.sh
```

## Bronprotocol

Zie `~/.openclaw/workspace/RADAR.md` — Tier 1 eerst, geen rijksoverheid als primaire bron.
