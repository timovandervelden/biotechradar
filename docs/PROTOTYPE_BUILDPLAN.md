# Biotech Radar — Prototype Buildplan

## Besluit: waar hoort deze agent te staan?

**Beste plek:**
`/home/brewuser/projects/biotech-radar`

Dus **niet** in de main OpenClaw workspace als volwaardig project, behalve eventueel een verwijzing of archiefnotitie.

### Waarom dit de beste plek is
- project blijft gescheiden van Clawdius' main geheugen en identity files
- eigen pipeline, config, data en agentlogica blijven bij elkaar
- minder kans op contextvervuiling
- makkelijker schaalbaar naar cron, database, frontend en aparte iteraties

## Kan de dir zelf gebouwd worden?
Ja.

Sterker nog: dat moet gecontroleerd en expliciet gebeuren. Niet organisch laten ontsporen.

---

# Doel van het prototype

Bewijzen dat we uit een beperkte set gestructureerde bronnen een bruikbare radar kunnen maken met:
- lage tokenkosten
- hoge relevantie
- duidelijke beleidswaarde
- dagelijkse ingest + wekelijkse synthese

---

# Prototype-scope

## Fase 1: smal en bewijsbaar
Start met **5–8 bronnen**.

Bronmix:
- 2 vakmedia
- 1 wetenschappelijke feed
- 1 sector/feed
- 1 EU/policy-achtige bron
- 1 investerings/marktbron (optioneel)

## Nog niet bouwen
- vector DB
- live dashboard-logica als kern
- complexe semantische retrieval als primaire motor
- 30+ bronnen tegelijk
- AI op elk item

---

# Doelarchitectuur (prototype)

## Dagelijks
1. ingest
2. dedupe
3. scope filter
4. signal markers
5. priority scoring
6. shortlist opslaan

## Wekelijks
7. AI-analyse op shortlist
8. briefing genereren

---

# Gewenste projectstructuur

```text
/home/brewuser/projects/biotech-radar/
├── agent/
│   ├── AGENTS.md
│   ├── MISSION.md
│   ├── FRAMEWORK.md
│   ├── MEMORY.md
│   └── agent.py
├── config/
│   ├── sources.yaml
│   ├── rubric.yaml
│   └── prompts.yaml              # nieuw
├── data/
│   ├── signals.db
│   ├── runs/
│   ├── shortlist/
│   └── briefings/
├── docs/
│   ├── ARCHITECTUUR.md
│   ├── PROTOTYPE_BUILDPLAN.md
│   └── SOURCE_REVIEW.md          # nieuw
├── pipeline/
│   ├── 1_ophalen.py
│   ├── 2_filteren.py
│   ├── 3_prioriteren.py
│   ├── 4_select_shortlist.py     # nieuw
│   ├── 5_analyse_llm.py          # nieuw
│   ├── 6_weekbriefing.py         # nieuw
│   └── utils.py                  # nieuw
└── tests/
    ├── test_filtering.py         # nieuw
    ├── test_keyword_matching.py  # nieuw
    └── test_shortlist.py         # nieuw
```

---

# Bouwvolgorde

## Stap 1 — Bronnenregister strak maken
**Bestand:** `config/sources.yaml`

### Doel
Alle bronnen op één plek beheren.

### Per bron opnemen
- `name`
- `type` (`rss`, `api`)
- `url`
- `tier`
- `status` (`test`, `active`, `paused`)
- `cadence` (`daily`, `weekly`)
- `tags`
- `geo`
- `language`
- `notes`
- `expected_signal_density`

### Output
Een beheersbaar bronregister dat later naar 30 bronnen kan groeien.

---

## Stap 2 — Scope en keywordlogica centraliseren
**Bestand:** `config/rubric.yaml`

### Doel
Één bron van waarheid voor:
- domeinkeywords
- signal keywords
- policy relevance markers
- exclusions
- food-scope
- PESTLE- of policy-gewichten

### Toevoegen
Nieuwe secties:
- `domain_keywords`
- `signal_keywords`
- `policy_markers`
- `action_markers`

### Output
Keywords krijgen elk een duidelijke functie.

---

## Stap 3 — Ingest stabiel maken
**Bestand:** `pipeline/1_ophalen.py`

### Doel
Alleen gestructureerde bronnen ophalen.

### Taken
- RSS/API uit `sources.yaml` lezen
- per item standaard velden opslaan
- duplicate check op URL/hash
- `source_type`, `source_name`, `published_at` goed vullen
- run-statistieken loggen

### Output
Stabiele daily inputlaag zonder AI.

---

## Stap 4 — Filterlaag opschonen
**Bestand:** `pipeline/2_filteren.py`

### Doel
Bepalen wat in scope valt.

### Taken
- woordgrensmatching gebruiken
- domeinkeywords toepassen
- food-link hard checken
- exclusions toepassen
- false positives minimaliseren

### Output
`filtered = 1/-1`

---

## Stap 5 — Prioritering versmallen
**Bestand:** `pipeline/3_prioriteren.py`

### Doel
Goedkope rule-based score maken vóór AI.

### Taken
Scoren op:
- source tier
- signaalwoorden
- NL/EU-relevantie
- markt/opschalingswoorden
- beleidswoorden
- recency
- cross-source overlap (later eenvoudig toevoegen)

### Output
`priority_score`

---

## Stap 6 — Shortlistlaag bouwen
**Bestand:** `pipeline/4_select_shortlist.py`

### Doel
Alleen de beste items naar AI sturen.

### Taken
- top-N per dag of week selecteren
- duplicates/near-duplicates onderdrukken
- brondiversiteit bewaken
- shortlist exporteren naar JSON/Markdown

### Output
Bijv. 10–20 items per dag of 30–40 per week.

---

## Stap 7 — AI-analyse pas hier inzetten
**Bestand:** `pipeline/5_analyse_llm.py`
**Config:** `config/prompts.yaml`

### Doel
Alleen shortlist-items laten duiden.

### AI-vragen per item
- wat is hier het signaal?
- waarom relevant?
- type: `weak_signal | trend | hype | beleidsimpuls`
- actiecategorie: `keuze | interventie | monitoring | escalatie`
- korte rationale

### Output opslaan
In DB of JSON:
- `signal_type`
- `policy_relevance_score`
- `action_type`
- `summary`
- `rationale`

---

## Stap 8 — Weekly radar bouwen
**Bestand:** `pipeline/6_weekbriefing.py`

### Doel
Van losse analyses naar redactionele output.

### Structuur briefing
1. belangrijkste bewegingen van de week
2. beleidsimpulsen
3. trends om te monitoren
4. hype/ruis
5. implicaties voor NL / RVO / verwerkende foodsector

### Output
Markdown-bestand in:
- `data/briefings/`

---

## Stap 9 — Kwaliteitscontrole toevoegen
**Bestanden:**
- `docs/SOURCE_REVIEW.md`
- `tests/test_filtering.py`
- `tests/test_keyword_matching.py`
- `tests/test_shortlist.py`

### Doel
Niet blind vertrouwen op de pipeline.

### Wat meten
- hoeveel items per bron
- hoeveel items overleven filter
- hoeveel shortlist-hits echt goed zijn
- welke false positives steeds terugkomen
- welke bronnen structureel zwak zijn

---

# Minimale database-uitbreiding

## `signals`
Bestaand, uitbreiden waar nodig met:
- `raw_text`
- `week_key`
- `priority_score`
- `shortlisted`
- `analysis_status`

## `signal_analysis`
Nieuw:
- `signal_id`
- `signal_type`
- `policy_relevance_score`
- `action_type`
- `summary`
- `rationale`
- `analysed_at`

## `source_runs`
Nieuw:
- `run_at`
- `source_name`
- `items_fetched`
- `items_kept`
- `errors`

---

# Tokenstrategie

## Daily
Geen AI op alle items.
Alleen AI op shortlist.

## Richtlijn
- 0 AI voor ingest/filtering/prioritering
- AI alleen voor topitems
- weekly synthesis in 1 of enkele calls

Dat houdt het prototype betaalbaar en controleerbaar.

---

# Wat eerst af moet

## Sprint 1
- `sources.yaml` normaliseren
- ingest stabiel
- filtering stabiel
- priority score rule-based

## Sprint 2
- shortlistscript
- prompts.yaml
- LLM-analyse op shortlist

## Sprint 3
- weekly briefing
- source review
- tests op false positives

---

# Harde ontwerpkeuze

## Beste plek voor de agent
**In het bestaande project:**
`/home/brewuser/projects/biotech-radar`

## Niet doen
- nieuwe volwaardige agent in de main workspace wortelen
- projectlogica verspreiden over meerdere losse mappen
- identity- en projectfiles vermengen

## Wel doen
- biotech-radar houden als aparte projectdir
- Clawdius gebruiken als orkestrator / editor / reviewer
- projectagent binnen `agent/` laten leven

---

# Eerstvolgende concrete bouwstappen

1. `config/sources.yaml` herstructureren naar bronregister
2. `config/rubric.yaml` opdelen in domain/signal/policy markers
3. `pipeline/4_select_shortlist.py` toevoegen
4. `pipeline/5_analyse_llm.py` toevoegen
5. `pipeline/6_weekbriefing.py` toevoegen
6. `source_runs` en `signal_analysis` tabel toevoegen
7. eerste 5–8 bronnen testen

---

# Succescriterium prototype

Geslaagd als:
- daily run stabiel draait
- AI-kosten laag blijven
- weekly briefing leesbaar en scherp is
- output leidt tot echte beleidsvragen of handelingsopties
- bronkwaliteit zichtbaar wordt
