# Migration Runbook — Biotech Radar

## Beste migratiestrategie

Migreer Biotech Radar als zelfstandige projectmap, niet als afhankelijk onderdeel van de main OpenClaw workspace.

## Projectdelen

### Verplicht meenemen
- `config/`
- `pipeline/`
- `data/` *(of een schone variant zonder runtimehistorie als je clean wilt starten)*
- `docs/`
- `exports/`

### Optioneel meenemen
- `agent/`
- `supabase/`

## Minimale runvolgorde

```bash
python3 pipeline/1_ophalen.py
python3 pipeline/1.5_dedupe.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/3.5_cluster.py
python3 pipeline/4_select_shortlist.py
```

## Met LLM-duiding erbij

```bash
python3 pipeline/5_analyse_llm.py
python3 pipeline/6_weekbriefing.py
```

## Wat is portable?

### Zeer portable
- `config/sources.yaml`
- `config/rubric.yaml`
- `config/prompts.yaml`
- `exports/lovable/*.html`
- `exports/html/*.html`

### Minder portable / omgeving-afhankelijk
- API keys
- OpenAI quota
- lokale Python packages
- eventuele browser- of OpenClaw-specifieke tooling

## Aanbevolen vervolgstap voor echte productisering

Maak later expliciet onderscheid tussen:
- `app/` → frontend/demo
- `pipeline/` → backend signal processing
- `exports/` → portability layer
- `tests/` → regressiechecks

## Demo-bestanden

Voor demo of snelle import:
- `exports/lovable/DEMO_AGENT_FLOW_DETAILED_LOVABLE.html`
- `exports/lovable/DEMO_LIVE_RUN_LOVABLE.html`
