# MEMORY.md — Biotech Radar Agent

_Projectgeheugen voor de Biotech Radar. Gescheiden van Clawdius' persoonlijk geheugen._

---

## Wat de radar is

Geautomatiseerde signaalradar voor **groene biotech + voedseltransitie**, gericht op signalen die buiten het standaard zichtsveld van overheidsmensen vallen.

## Scope

**Wél:** precision fermentation, alternative proteins, NGT, biobased food, reststromen, opschaling, marktintroductie, verwerkende foodindustrie
**Niet:** rode biotech, farma, medisch zonder food-link, bekende NL-overheidsartikelen als primair signaal

## Technische stack

- **Pipeline:** Python (RSS + Brave → filter → PESTLE-score → briefing)
- **Database:** SQLite lokaal + Supabase cloud
- **Supabase:** `https://bnjrmfqqonkjkuelmtpl.supabase.co`
- **Dashboard:** Lovable (nog niet live)
- **275 signalen** gemigreerd naar Supabase (stand maart 2026)

## Status (maart 2026)

- Pipeline werkt, cron draait dagelijks 06:00
- Supabase gevuld met 275 signalen
- Lovable-koppeling in progress (RLS policy + dashboard prompt klaar)
- Domeinvalidatie nog niet gedaan — **dit is de volgende prioriteit**

## Architectuur

- **Clawdius** = main agent / persoonlijk assistent (geen projectinhoud)
- **Biotech Agent** = specialist voor radar-runs (`biotech-agent/`)
- **Pipeline** = automatische cron-scripts (`~/projects/biotech-radar/`)
- **Supabase** = gedeelde cloud-database
- **Lovable** = publiek dashboard (nog niet live)

## Beslissingen

- Biotech radar wordt uiteindelijk losgekoppeld naar eigen VPS + eigen main agent
- Nu nog niet — eerst domeinvalidatie
- Scheiding Clawdius / Biotech Agent is leidend principe

## Open TODOs

- [ ] Domeinvalidatie — `validatie_v2.html` delen met expert
- [ ] Lovable dashboard live zetten
- [ ] Pipeline laten schrijven naar Supabase (nu nog alleen SQLite lokaal)
- [ ] Datumfiltering Brave-resultaten verbeteren
- [ ] Losse VPS + eigen main agent opzetten (later)
