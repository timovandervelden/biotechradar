# Architectuur — Wie doet wat?

## De drie lagen

```
┌─────────────────────────────────────────────────────────────┐
│  JIJ (Timo)                                                 │
│  Telegram → vraag, opdracht, feedback                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  CLAWDIUS — Main Agent                                      │
│  Jouw persoonlijke assistent                                │
│                                                             │
│  • Voert taken uit op jouw verzoek                          │
│  • Beheert geheugen (MEMORY.md, BIOTECH.md, etc.)           │
│  • Kan de Biotech Agent inschakelen voor radar-runs         │
│  • Communiceert resultaten terug naar jou                   │
└───────────┬─────────────────────────────┬───────────────────┘
            │ spawnt indien nodig         │ leest/schrijft
            ▼                             ▼
┌───────────────────────┐     ┌───────────────────────────────┐
│  BIOTECH RADAR AGENT  │     │  PIPELINE (cron, dagelijks)   │
│  Subagent             │     │  Automatisch, geen AI         │
│                       │     │                               │
│  • Radar-runs op      │     │  1_ophalen.py   → RSS + Brave │
│    verzoek            │     │  1b_verrijken.py → full-text  │
│  • Analyseert         │     │  2_filteren.py  → scope       │
│    signalen           │     │  3_prioriteren.py → PESTLE    │
│  • Rapporteert aan    │     │  4_synthese.py  → briefing    │
│    Clawdius           │     │  5_publiceren.py → Telegram   │
│                       │     │                               │
│  Instructies in:      │     │  Draait elke ochtend 06:00    │
│  biotech-agent/       │     │  Schrijft naar Supabase       │
│  AGENTS.md            │     │                               │
│  MISSION.md           │     └───────────────┬───────────────┘
│  RADAR.md             │                     │
└───────────────────────┘                     │ schrijft
                                              ▼
                              ┌───────────────────────────────┐
                              │  SUPABASE (database)          │
                              │  Cloud, publiek leesbaar      │
                              │                               │
                              │  • signals (275+)             │
                              │  • rubric (PESTLE wegingen)   │
                              │  • feeds (RSS bronnen)        │
                              │  • brave_queries              │
                              └───────────────┬───────────────┘
                                              │ leest
                                              ▼
                              ┌───────────────────────────────┐
                              │  LOVABLE DASHBOARD            │
                              │  Publieke URL                 │
                              │                               │
                              │  • Signalen bekijken          │
                              │  • Rubric aanpassen           │
                              │  • Feeds beheren              │
                              │  • Deelbaar met stakeholders  │
                              └───────────────────────────────┘
```

---

## Wie praat je mee?

| Situatie | Met wie |
|---|---|
| Jij stuurt een bericht in Telegram | Clawdius |
| "Draai een radar-run" | Clawdius → schakelt Biotech Agent in |
| Dagelijkse briefing om 06:00 | Pipeline → Clawdius → Telegram |
| Dashboard openen in browser | Lovable (geen agent, gewoon UI) |
| Rubric aanpassen in dashboard | Lovable → Supabase (direct) |

---

## Geheugen & bestanden

| Bestand | Eigenaar | Doel |
|---|---|---|
| MEMORY.md | Clawdius | Langetermijngeheugen over jou |
| memory/2026-03-XX.md | Clawdius | Dagelijkse notities |
| biotech-agent/MISSION.md | Biotech Agent | Wat monitoren we en waarom |
| biotech-agent/RADAR.md | Biotech Agent | Bronprotocol en keywords |
| biotech-agent/BIOTECH.md | Biotech Agent | Cumulatieve bevindingen |
| biotech-agent/FRAMEWORK.md | Biotech Agent | PESTLE-weging en scope |
| projects/biotech-radar/ | Pipeline | Code en database |

---

## Korte samenvatting

- **Clawdius** = jouw aanspreekpunt voor alles
- **Biotech Agent** = specialist die radar-runs uitvoert op verzoek
- **Pipeline** = de robot die elke ochtend automatisch werkt
- **Supabase** = de gedeelde database die alles verbindt
- **Lovable** = het dashboard voor mensen zonder terminal
