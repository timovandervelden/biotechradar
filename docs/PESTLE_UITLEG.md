# Biotech Radar — PESTLE Uitleg

Dit document legt uit welke categorieën de radar gebruikt voor prioritering, welke keywords daar nu onder vallen, wat de gewichten zijn, en waarom die categorie relevant is binnen de scope **groene biotech + voedseltransitie**.

## Bronnen van deze lijst

- **Keywords per categorie** komen uit `pipeline/3_prioriteren.py` (`PESTLE_KEYWORDS`).
- **Basisgewichten** komen uit `config/rubric.yaml`.
- In de huidige code worden twee gewichten expliciet verzwaard:
  - **Technology = 0.25**
  - **Economic = 0.30**
- Daarnaast krijgt **Policy_early** een extra bonusgewicht van **0.40**.

Kort gezegd: dit is niet een abstract PESTLE-model, maar de daadwerkelijke scoringlogica van de huidige radar.

---

## Policy

**Gewicht:** uit `rubric.yaml`

**Waarom relevant?**  
In deze radar is beleid geen achtergrondruis maar vaak de doorslaggevende factor voor markttoegang. Zeker bij Novel Food, NGT en precision fermentation bepaalt regelgeving of innovatie in Nederland en Europa echt kan landen.

**Keywords:**
- regulation
- EFSA
- Novel Food
- EU Biotech Act
- NGT
- new genomic techniques
- vergunning
- regelgeving
- kamerbrief
- kabinet
- beleid
- voedselveiligheid
- toelating
- approval
- wetgeving
- EU food law
- industriebeleid

---

## Economic

**Gewicht:** `0.30` in code

**Waarom relevant?**  
Veel food-biotech ontwikkelingen mislukken niet op idee of labniveau, maar op schaal, kapitaal en commercialisatie. Daarom kijkt de radar expliciet naar funding, cost parity, venture-activiteit en marktontwikkeling.

**Keywords:**
- funding
- investering
- series
- scale-up
- groeifonds
- venture
- capital
- markt
- financiering
- opschaling
- marktontwikkeling
- food market
- alternative protein market
- cost parity
- commercialisatie

---

## Social

**Gewicht:** uit `rubric.yaml`

**Waarom relevant?**  
Voedselinnovatie is nooit alleen technisch. Acceptatie, maatschappelijk sentiment, consumentengedrag en framing bepalen of iets bestuurlijk en commercieel tractie krijgt.

**Keywords:**
- consument
- acceptatie
- voedseltransitie
- eiwittransitie
- maatschappij
- gezondheid
- sustainability
- voedselzekerheid
- consumer
- public opinion
- adoption

---

## Technology

**Gewicht:** `0.25` in code

**Waarom relevant?**  
De radar wil vroeg zien waar technische doorbraken of nieuwe productieroutes ontstaan die gevolgen hebben voor de voedseltransitie. Daarom ligt hier nadruk op precision fermentation, bioreactors, cellular agriculture en biobased verwerking.

**Keywords:**
- precision fermentation
- fermentation
- NGT
- cellular agriculture
- bioreactor
- novel protein
- alternative protein
- plant protein
- biobased
- reststromen
- circulaire verwerking
- biorefinery
- fermentation-derived
- cultivated
- synthetic biology

---

## Environmental

**Gewicht:** uit `rubric.yaml`

**Waarom relevant?**  
Deze categorie speelt mee, maar is in de huidige radar minder dominant dan policy, economics en technology. Milieu-impact is belangrijk, maar niet de primaire driver voor prioritering in deze versie.

**Keywords:**
- circulair
- duurzaam
- CO2
- emissie
- waste
- reststromen
- klimaat
- biodiversiteit
- land use
- water footprint
- circular economy
- biobased economy

---

## Policy_early

**Bonusgewicht:** `0.40`

**Waarom relevant?**  
Dit is de vroeg-signaalbonus. De radar beloont expliciet signalen die duiden op precedenten, experimenteerruimte of nieuwe regelruimte. Dat zijn precies de ontwikkelingen die overheidsmensen vaak te laat zien als ze alleen klassieke beleidsbronnen volgen.

**Keywords:**
- first in EU
- first in europe
- precedent
- paves way
- pre-approval
- regulatory sandbox
- experimenteerruimte
- regelvrije zone
- ahead of regulation
- policy gap
- tasting event
- proefsmaken
- eerste in europa

---

## Belangrijke interpretatie

De huidige PESTLE-lijst is een werkende eerste versie. De selectie is dus niet puur theoretisch, maar pragmatisch opgebouwd vanuit de vraag:

> **welke signalen willen we vroeg zien als we groene biotech en voedseltransitie beleidsmatig en strategisch willen volgen?**

Daarmee is dit overzicht tegelijk bruikbaar als:
- uitlegdocument voor stakeholders
- startpunt voor validatie met domeinexperts
- checklist voor verdere aanscherping van de radarlogica
