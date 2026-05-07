# Biotech Radar

Biotech Radar is een zelfstandige projectrepo voor het signaleren, filteren en duiden van biotech-signalen met relevantie voor:
- Nederlandse voedseltransitie
- verwerkende foodsector
- opschaling
- markttoetreding
- beleidskeuzes

## Huidige architectuur

```text
config/
  sources.yaml      -> centraal bronregister
  rubric.yaml       -> scope, keywords, policy markers, scoringlogica
  prompts.yaml      -> prompts voor LLM-duiding

pipeline/
  1_ophalen.py         -> ingest van RSS/API-bronnen
  1.5_dedupe.py        -> canonicaliseert doublures + bewaart cross-bron referenties
  2_filteren.py        -> scopefilter op basis van keywords en food-link
  3_prioriteren.py     -> rule-based scoring (PESTLE + policy/market markers)
  3.5_cluster.py       -> cross-bron clustering op entiteit + tijd + brontype
  4_select_shortlist.py-> shortlist met recency, source diversity en cluster-boost
  5_analyse_llm.py     -> LLM-duiding op shortlist of cluster
  6_weekbriefing.py    -> weekly briefing-output

exports/
  html/             -> browserklare demo-HTML
  lovable/          -> copy-paste HTML voor Lovable
  runbooks/         -> runvolgorde en migratie-instructies

legacy/
  oude pipeline- en artefactbestanden, bewaard voor referentie
```

## Runvolgorde

### Machine-run

```bash
python3 pipeline/1_ophalen.py
python3 pipeline/1.5_dedupe.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/3.5_cluster.py
python3 pipeline/4_select_shortlist.py
```

### Met LLM-duiding erbij

```bash
python3 pipeline/5_analyse_llm.py
python3 pipeline/6_weekbriefing.py
```

## Waar zit de intelligentie?

De intelligentie zit in lagen:
1. **Bronkeuze** — welke bronnen mogen de radar voeden
2. **Scope** — welke keywords, food-link en uitsluitingen bepalen wat relevant is
3. **Rule-based scoring** — welke signalen meer gewicht krijgen
4. **Cross-bron clustering** — wat begint samen te komen over meerdere bronnen en tijd
5. **LLM-duiding** — welk patroon of welke beleidsimplicatie zit in de shortlist of cluster

## Demo-assets

Kijk in:
- `exports/html/`
- `exports/lovable/`
- `exports/runbooks/`

## Belangrijke notitie

Deze repo is bewust portable opgebouwd onder:
`/home/brewuser/projects/biotech-radar`

Dus niet verweven met de main OpenClaw-workspace. Dat maakt migratie naar GitHub, Lovable of een andere server veel eenvoudiger.
