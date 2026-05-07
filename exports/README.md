# Exports — portable demo & migration assets

Deze map is de overdraagbare laag van Biotech Radar.

## Structuur

- `html/` → demo-HTML bestanden zoals ze direct in browser te openen zijn
- `lovable/` → HTML bestanden bedoeld om te copy-pasten/importeren in Lovable of vergelijkbare builders
- `runbooks/` → overdrachtsinstructies, run-commando's en migratienotities

## Doel

Deze map moet zoveel mogelijk zelfstandig bruikbaar zijn bij migratie naar:
- eigen repo
- andere server
- Lovable
- andere app- of demo-omgeving

## Huidige assets

### html/
- `DEMO_AGENT_FLOW.html`
- `DEMO_AGENT_FLOW_DETAILED.html`
- `DEMO_LIVE_RUN.html`

### lovable/
- `DEMO_AGENT_FLOW_DETAILED_LOVABLE.html`
- `DEMO_LIVE_RUN_LOVABLE.html`

## Belangrijke notitie

Deze exports zijn presentatielaag / demo-assets.
De werkende logica blijft in:
- `config/`
- `pipeline/`
- `data/`

Dus:
- `exports/` = draagbare output
- `pipeline/` = werkende motor
