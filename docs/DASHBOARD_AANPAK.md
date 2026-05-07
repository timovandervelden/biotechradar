# Dashboard Aanpak — Supabase + Lovable

**Vraag:** Hoe maak ik een dashboard waarin ik live de radar-informatie kan aanpassen?

---

## Het probleem

De Biotech Radar sloeg alles op in een lokale SQLite-database op de server. Dat werkt voor de pipeline, maar heeft twee beperkingen:

1. **Niet deelbaar** — alleen toegankelijk via SSH of de server zelf
2. **Niet aanpasbaar** — keywords, wegingen en bronnen aanpassen vereist toegang tot bestanden op de server

De wens: een interface waarmee je (en anderen) live kunnen aanpassen **zonder code of servertoegang**.

---

## De aanpak: drie componenten

```
Server (pipeline)  →  Supabase (database)  →  Lovable (dashboard)
```

### 1. Supabase — de database in de cloud

**Wat:** Supabase is een open-source database-service (PostgreSQL) die in de cloud draait op supabase.com.

**Waarom Supabase:**
- Gratis tier voldoende (500MB, 50k API-calls/maand)
- Genereert automatisch een REST API — Lovable kan er direct bij zonder extra code
- Heeft een ingebouwde tabeleditor (als spreadsheet) voor handmatige aanpassingen
- Publiek leesbaar, beveiligd schrijven — juiste rechtenstructuur out-of-the-box

**Wat er in staat:**
- `signals` — alle opgehaalde en gescoorde artikelen
- `rubric` — de PESTLE-wegingen (aanpasbaar via dashboard)
- `feeds` — welke RSS-bronnen actief zijn (aan/uit via dashboard)
- `brave_queries` — de zoekqueries voor Brave Search

**Wat er is gedaan:**
1. Schema aangemaakt via SQL Editor in Supabase
2. 275 signalen gemigreerd vanuit lokale SQLite via `migrate.py`
3. Pipeline geconfigureerd om voortaan naar Supabase te schrijven

---

### 2. Lovable — het dashboard

**Wat:** Lovable is een no-code tool die React-dashboards bouwt via chat-instructies. Je beschrijft wat je wil, Lovable schrijft de code en host het op een publieke URL.

**Waarom Lovable:**
- Geen React-kennis nodig — beschrijven in gewone taal volstaat
- Heeft ingebouwde Supabase-integratie (één klik koppeling)
- Publieke URL — direct deelbaar met stakeholders of domeinexperts
- Aanpasbaar via chat: "voeg een kolom toe" of "maak de score rood als hij onder 0.5 is"

**Wat het dashboard kan:**
- Signalen bekijken, zoeken en filteren op score/tier/bron
- PESTLE-wegingen aanpassen via sliders (direct opgeslagen in Supabase)
- RSS-feeds aan/uitzetten
- Alles live — wijzigingen zijn direct zichtbaar

---

### 3. De koppeling

De pipeline op de server schrijft dagelijks nieuwe signalen naar Supabase. Lovable leest uit dezelfde database. Wijzigingen die je in het dashboard maakt (rubric, feeds) worden direct opgepikt door de volgende pipeline-run.

```
Dagelijkse cron (06:00)
  → 1_ophalen.py haalt RSS + Brave op
  → 1b_verrijken.py haalt full-text op
  → 2_filteren.py filtert op keywords (uit Supabase rubric)
  → 3_prioriteren.py scoort (op basis van Supabase rubric)
  → schrijft resultaten naar Supabase signals-tabel
  → Lovable dashboard toont bijgewerkte signalen
```

---

## Status

- ✅ Supabase database aangemaakt
- ✅ Schema ingericht (signals, rubric, feeds, queries)
- ✅ 275 signalen gemigreerd
- ✅ Lovable component gegenereerd (BiotechRadarReady.tsx)
- ⏳ Lovable dashboard live zetten (jouw actie)
- ⏳ Pipeline aanpassen om voortaan naar Supabase te schrijven

---

## Kosten

| Component | Kosten |
|---|---|
| Supabase | Gratis (tot 500MB en 50k calls/maand) |
| Lovable | Gratis tier beschikbaar |
| Server (pipeline) | Bestaande OpenClaw server |
| **Totaal** | **€0** voor prototype |
