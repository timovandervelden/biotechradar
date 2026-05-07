# FRAMEWORK.md — Analytisch Kader

Definitie van scope, weging en methode voor de Biotech Radar.

---

## 🎯 Scope

**Definitie:** Groene en witte biotechnologie (nieuwe genomische technieken/NGT, biobased verwerking, precision fermentation en cellulaire landbouw) toegepast op de Nederlandse voedseltransitie, met nadruk op de verwerkende foodsector: verwerking, opschaling en marktontwikkeling.

**Sub-thema’s die absoluut mee moeten:**
- Biobased ingrediënten uit reststromen
- Eiwittransitie via groene en witte biotech
- Opschaling van verwerkende producenten
- Biosecurity in biomanufacturing
- Markttoetreding en consumentenacceptatie

**Geografische scope:**
- Nederland primair (ondernemend Nederland, foodsector, verwerkende industrie)
- Internationaal alleen als concurrentie-benchmark/referentie (EU Farm-to-Fork, VS/China biotech-soevereiniteit)

**Tijdshorizon:**
- **Kort (0-2 jaar):** Operationele signalen — investeringen, marktlanceringen, regelgeving
- **Middellang (2-10 jaar):** Technologische en marktontwikkelingen
- **Lang (10-20 jaar):** Structurele verschuivingen, beleidsprecedenten

**Niet in scope:**
- Rode biotech (farmaceutisch, medisch) zonder food-link
- Witte biotech (industriële chemie) zonder food-link
- Bekende NL overheidsplannen die ambtenaren al kennen

---

## 📊 PESTLE-weging

| Categorie | Weging | Rationale |
|---|---|---|
| **Policy** | 35% | Regelgeving (EFSA, Novel Food, NGT) is de directe bottleneck voor opschaling |
| **Economic** | 30% | Financieringskloof bepaalt of NL-bedrijven blijven of naar VS/Zwitserland gaan |
| **Social** | 20% | Consumentenacceptatie bepaalt politieke bereidheid om te investeren |
| **Technology** | 25% | Tech-doorbraken zijn vroege signalen voor toekomstige beleidskeuzes |
| **Environmental** | 5% | Duurzaamheid is randvoorwaarde, niet de primaire driver |
| **Policy_early** ⭐ | 40% | Bonus voor beleidsprecedenten en regelvrije experimenten (first in EU, pre-approval) |

> Noot: Policy_early is een bonus-categorie bovenop de standaard PESTLE — signalen die een nieuw beleidspad openen worden extra gewogen.

---

## 🔑 Keyword Taxonomie

**Runtime truth:** `config/rubric.yaml` is de enige bron van waarheid voor filtering en scoring. Dit document beschrijft de scope; de pipeline leest de keywords uit YAML.

### High-priority (directe match = relevant)
`groene biotechnologie` · `witte biotechnologie` · `NGT` · `new genomic techniques` · `biobased economy` · `voedseltransitie` · `verwerkende foodindustrie` · `eiwittransitie` · `sustainable protein` · `plant protein` · `precision fermentation` · `novel protein` · `opschaling biomanufacturing` · `reststromen verwerking` · `cell-based ingredients` · `cell-based foods` · `biomassa fermentatie` · `groene biotech beleid` · `witte biotech beleid`

### Synoniemen / medium-priority
`plant biotechnology` · `biobased verwerking` · `cellular agriculture` · `biobased ingrediënten` · `circulaire verwerking` · `verwerkende producenten` · `metabolic engineering` · `sleuteltechnologie` · `enabling technology` · `dwarsdoorsnijdende technologie` · `biotech booster food` · `rapport wennink biotech domein` · `groene biotech soevereiniteit` · `verwerkende keten eiwittransitie` · `biomanufacturing` · `fermentation` · `biobased` · `scale-up` · `verwerkende industrie` · `food tech`

### Vroeg-signaal (change signals)
`first in EU` · `first in europe` · `precedent` · `paves way` · `pre-approval` · `regulatory sandbox` · `experimenteerruimte` · `regelvrije zone` · `ahead of regulation` · `policy gap` · `tasting event` · `proefsmaken`

### Scope-exclusies
- Pure rode biotech (geneeskunde)
- Witte biotech zonder food-link
- Bekende overheidsplannen als enig signaal

---

## 📡 Bronprotocol

**Tier 1 — buiten zichtsveld overheid (prioriteit):**
- vegconomist.com, protein-trends.com, gfi.org
- proteinproductiontechnology.com, greenqueen.com.hk
- PubMed (wetenschappelijke vroeg-signalen)
- Brave Search op gerichte queries

**Tier 2 — brancheorganisaties (eerder dan overheid):**
- eiwittrends.nl, hollandbio.nl, venturecapital.nl

**Bewust overgeslagen:**
- rvo.nl, rijksoverheid.nl, nationaalgroeifonds.nl
- Fierce Biotech, STAT News (farma-gedomineerd, login vereist)

---

## 📤 Output definitie

Een signaal telt alleen als het:
1. **Buiten het zichtsveld** van standaard overheidscommunicatie valt
2. **Een keuze-implicatie** heeft — niet beschrijvend nieuws
3. **Koppelbaar is** aan de voedseltransitie (opschaling, markt, regulering)

Output format per briefing:
- Wat is het signaal (bron, datum)
- Waarom relevant voor voedseltransitie
- Strategische "so what" of actiepunt

---

## 🗓 Log

| Datum | Update |
|---|---|
| 2026-03-18 | FRAMEWORK.md aangemaakt op basis van rubric.yaml + MISSION.md |
| 2026-05-07 | Keyword-scope aangescherpt; runtime truth expliciet gecentraliseerd in `config/rubric.yaml` |
