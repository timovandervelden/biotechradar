# Biotech Radar — Aanpak & Rationale

**Datum:** 18-19 maart 2026  
**Auteur:** Timo van der Velden  
**Status:** Werkend prototype

---

## Wat is dit?

Een geautomatiseerde signaalradar die ontwikkelingen in **groene biotech en de voedseltransitie** monitort — specifiek gericht op signalen die overheidsmensen *niet* vanzelf tegenkomen.

De radar haalt dagelijks artikelen op uit internationale bronnen, filtert op relevantie, scoort op beleidsimpact en genereert een briefing met inzichten voor beleidsmakers en innovatieconsultants.

---

## Waarom dit bouwen?

De uitdaging bij beleidswerk in de voedseltransitie:
- Relevante ontwikkelingen komen uit internationale bronnen, niet uit beleidsstukken
- Overheidsmensen lezen dezelfde bekende bronnen — het nieuwe zit elders
- Handmatig monitoren kost te veel tijd voor structureel gebruik

**De oplossing:** Een pipeline die automatisch breed zoekt, filtert op relevantie en prioriteert op beleidsimpact — zodat je elke ochtend alleen de signalen ziet die er toe doen.

---

## De architectuur in drie lagen

```
[Databronnen]         [Pipeline op server]      [Dashboard / Briefing]
RSS feeds       →     Ophalen                →   Supabase (database)
Brave Search    →     Full-text verrijken    →   Lovable (web app)
                      Filteren op scope      →   Telegram briefing
                      PESTLE-scoring         
```

---

## Stap 1 — Databronnen

**Twee kanalen:**

**RSS feeds (continu, automatisch)**
Directe feeds van food-specifieke bronnen die dagelijks publiceren:
- vegconomist.com — precision fermentation markt
- eiwittrends.nl — NL eiwittransitie
- gfi.org (Good Food Institute) — alt protein wereldwijd
- protein-trends.com — markt en technologie
- hollandbio.nl — NL biotech brancheorganisatie

**Brave Search (gericht zoeken)**
Dagelijkse zoekopdrachten op specifieke thema's die buiten feeds vallen:
- "precision fermentation Netherlands scale-up 2026"
- "EFSA Novel Food approval alternative protein"
- "NGT new genomic techniques food Netherlands"
- "cellular agriculture cultivated protein Netherlands"

**Waarom beide?** RSS geeft breedte en continuïteit. Brave Search geeft diepte op specifieke thema's en pikt bronnen op zonder RSS-feed.

---

## Stap 2 — Filteren en scoren

**Filter (wat gaat eruit):**
- Rode biotech (farma, medisch) zonder food-link
- Bekende overheidspublicaties die ambtenaren al kennen
- Artikelen zonder relevante food/voedseltransitie-keywords

**PESTLE-scoring (wat wordt geprioriteerd):**

| Categorie | Weging | Rationale |
|---|---|---|
| Policy | 35% | Regelgeving is de directe bottleneck voor opschaling |
| Economic | 30% | Financieringskloof bepaalt of NL-bedrijven blijven |
| Social | 20% | Consumentenacceptatie bepaalt politieke bereidheid |
| Technology | 25% | Tech-doorbraken zijn vroege beleidssignalen |
| Environmental | 5% | Randvoorwaarde, niet de primaire driver |
| **Policy_early** | **40%** | **Bonus: beleids-precedenten en regelvrije experimenten** |

De Policy_early bonus is bewust hoog: signalen als "eerste EU-land dat X doet" of "pre-approval tasting toegestaan" zijn precies de vroegtijdige signalen die beleidsmakers nodig hebben.

**Full-text scoring:** De pipeline haalt de volledige artikeltekst op (niet alleen de RSS-samenvatting) voor accuratere scoring. Resultaat: van 7 naar 49 relevante signalen na introductie van food-specifieke bronnen.

---

## Stap 3 — Toolkeuzes

### Supabase — waarom?

Supabase is gekozen als database omdat:
- **Gratis tier** voldoende voor dit gebruik (500MB, 50k calls/maand)
- **Publieke REST API** — Lovable kan direct uitlezen zonder extra backend
- **SQL Editor** — rubric en bronnen aanpasbaar zonder code
- **Real-time** — wijzigingen in dashboard zijn direct zichtbaar in de pipeline
- **Schaalbaar** — werkt ook als het naar productie gaat

Alternatief was SQLite (lokaal op de server), maar dat is niet deelbaar met anderen.

### Lovable — waarom?

Lovable is gekozen voor het dashboard omdat:
- **No-code UI bouw** — dashboard gebouwd via chat-instructies, geen handmatige React-code
- **Directe Supabase-integratie** — één klik koppeling
- **Publieke URL** — direct deelbaar met stakeholders
- **Aanpasbaar** — rubric-wegingen en bronnen aanpassen via sliders in het dashboard

Alternatief was een statische HTML-pagina (werkt, maar niet aanpasbaar).

### Pipeline (Python op server) — waarom local?

De data-pipeline draait op een server omdat:
- RSS-feeds en web-scraping vereisen een server-omgeving
- Dagelijkse cron-job (06:00) zonder handmatig ingrijpen
- Supabase-keys worden server-side bewaard (niet in de browser)

---

## Stap 4 — Resultaten eerste run

| Metriek | Waarde |
|---|---|
| Totaal opgehaalde signalen | 275 |
| Relevant na filter | 49 |
| Full-text geanalyseerd | 48 |
| Hoogste score | 3.65 (NL pre-approval tastings) |
| Bronnen actief | 9 RSS + 13 Brave queries |

**Top 3 signalen (18 maart 2026):**

1. **score 3.65** — *Dutch Govt Paves Way for Pre-Approval Tastings of Precision-Fermented Foods* (greenqueen.com.hk) — NL eerste EU-land dat publieke tastings toestaat vóór Novel Food-goedkeuring
2. **score 2.25** — *Netherlands invests in two cellular agriculture facilities* — BFF Ede + tweede open-access faciliteit
3. **score 2.25** — *Verley $38M Series A* — Europees precision fermentation bedrijf haalt schaal

---

## Vervolgstappen

- [ ] Google Alerts RSS-feeds instellen voor precision fermentation NL
- [ ] Dashboard live via Lovable voor stakeholder-validatie
- [ ] Rubric verfijnen op basis van feedback domeinexpert
- [ ] Dagelijkse briefing via Telegram (pipeline → synthese → publiceren)
- [ ] FRAMEWORK.md als formeel referentiedocument voor aanpak

---

## Technische stack (samenvatting)

| Component | Tool | Reden |
|---|---|---|
| Data ophalen | Python + feedparser + Brave Search | Gratis, flexibel, serverless |
| Opslag | Supabase (PostgreSQL) | Cloud, deelbaar, gratis tier |
| Dashboard | Lovable (React + Tailwind) | No-code, publieke URL |
| Scoring | PESTLE rubric in YAML | Aanpasbaar zonder code |
| Briefing | Markdown → Telegram | Direct bij de gebruiker |
| Cron | cron.sh op server | Dagelijks automatisch |
