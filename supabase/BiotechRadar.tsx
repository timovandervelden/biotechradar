// BiotechRadar.tsx
// Importeer in Lovable: src/components/BiotechRadar.tsx
// Vereist: Tailwind CSS (standaard in Lovable)

import { useState } from 'react';

interface Signal {
  title: string;
  url: string;
  source: string;
  score: number;
  snippet: string;
  tier: number;
}

const SIGNALS: Signal[] = [{"title": "Dutch Govt Paves Way for Pre-Approval Tastings of Precison-Fermented Foods", "url": "https://www.greenqueen.com.hk/precision-fermentation-netherlands-food-tasting-approval/", "source": "BioPharma Trend", "score": 3.65, "snippet": "# Dutch Govt Paves Way for Pre-Approval Tastings of Precison-Fermented Foods  4 Mins Read  ## The Netherlands has become the first EU country to approve public tastings of foods derived from novel fermentation processes before they’re cleared for sal", "tier": 1}, {"title": "Evenementen over eiwittransitie: noteer in je agenda", "url": "https://www.eiwittrends.nl/evenementen-eiwittransitie/", "source": "Eiwittrends NL", "score": 3.4, "snippet": "# Evenementen over eiwittransitie: noteer in je agenda  **Gedurende het jaar organiseren verschillende organisaties en bedrijven evenementen over de eiwittransitie. Eiwit Trends zet een aantal mogelijk interessante events op een rij.**  ## Plant FWD ", "tier": 2}, {"title": "Verley Secures $38 Million Series A to Commercialize Precision-Fermented Dairy Proteins", "url": "https://vegconomist.com/investments-finance/verley-secures-38-million-series-a-to-commercialize-precision-fermented-dairy-proteins/", "source": "Vegconomist — Fermentation", "score": 2.25, "snippet": "# Verley Secures $38 Million Series A to Commercialize Precision-Fermented Dairy Proteins - vegconomist - the vegan business magazine  French precision fermentation company Verley has secured an oversubscribed $38 million Series A financing round, fo", "tier": 1}, {"title": "Netherlands invests in future of food with two cellular agriculture facilities", "url": "https://ioplus.nl/en/posts/netherlands-invests-in-future-of-food-with-two-cellular-agriculture-facilities", "source": "Brave - precision fermentation NL scale-up", "score": 2.25, "snippet": "# Netherlands invests in future of food with two cellular agriculture facilities  The Netherlands is strengthening its position as a global leader in cellular agriculture by launching two independent open-access scale-up facilities. These facilities,", "tier": 1}, {"title": "Fermentation: Latest News 2026 - vegconomist: the vegan business magazine", "url": "https://vegconomist.com/category/fermentation/", "source": "BioPharma Trend", "score": 2.2, "snippet": "# Fermentation: Latest News 2026 - vegconomist: the vegan business magazine  Dutch precision fermentation specialist Vivici has announced the U.S. launch of its lactoferrin ingredient, Vivitein™ LF. The company will showcase its portfolio of function", "tier": 1}, {"title": "Vivici Debuts Precision-Fermented Lactoferrin in the US Market", "url": "https://vegconomist.com/ingredients/vivici-debuts-precision-fermented-lactoferrin-in-the-us-market/", "source": "Vegconomist — Fermentation", "score": 1.8, "snippet": "# Vivici Debuts Precision-Fermented Lactoferrin in the US Market - vegconomist - the vegan business magazine  Dutch precision fermentation specialist [Vivici](https://cultivated-x.com/organisations_and_brands/vivici/) has announced the U.S. launch of", "tier": 1}, {"title": "Met Karin Löwik aan het roer zet Rival Foods koers naar de markt", "url": "https://www.eiwittrends.nl/met-karin-lowik-aan-het-roer-zet-rival-foods-koers-naar-de-markt/", "source": "Eiwittrends NL", "score": 1.7, "snippet": "# Met Karin Löwik aan het roer zet Rival Foods koers naar de markt  Het is tijd voor de volgende stap van Rival Foods, dat plantaardige ‘hele spier’-vleesalternatieven maakt. Om dat te laten slagen heeft het bedrijf het zeer ervaren nieuw gezicht bin", "tier": 2}, {"title": "Biotechnology Fermentation Factory (BFF) Gives First Look at the Future of (Precision)Fermentation i", "url": "https://www.nizo.com/news/biotechnology-fermentation-factory-bff-gives-first-look-at-the-future-of-precisionfermentation-in-the-netherlands/", "source": "BioPharma Trend", "score": 1.65, "snippet": "# Biotechnology Fermentation Factory (BFF) Gives First Look at the Future of (Precision)Fermentation in the Netherlands | NIZO  **Ede, The Netherlands – June 6, 2025 – Today, the Biotechnology Fermentation Factory (BFF), empowered by NIZO Food Resear", "tier": 1}, {"title": "Reimagining protein for a future under pressure", "url": "https://gfi.org/blog/reimagining-protein-for-a-future-under-pressure/", "source": "GFI (Good Food Institute)", "score": 1.65, "snippet": "# Reimagining protein for a future under pressure - The Good Food Institute  ## Opportunity in every pressure point  The forces that sustain life on Earth—soil, water, biodiversity, and a habitable climate—are under growing strain from the way we pro", "tier": 1}, {"title": "Hoe AH de eiwittransitie verdrinkt in een klein bakje suiker", "url": "https://www.eiwittrends.nl/hoe-ah-de-eiwittransitie-verdrinkt-in-een-klein-bakje-suiker/", "source": "Eiwittrends NL", "score": 1.55, "snippet": "# Hoe AH de eiwittransitie verdrinkt in een klein bakje suiker  De eiwittransitie klinkt bijna vanzelfsprekend, alsof het een kwestie is van even overstappen. Maar kijk je wat beter, dan zie je hoe taai die overstap werkelijk is.  Neem het nieuwe soj", "tier": 2}, {"title": "Eiwitmonitor 2025: eiwittransitie stagneert", "url": "https://www.eiwittrends.nl/eiwitmonitor-eiwittransitie-stagneert/", "source": "Eiwittrends NL", "score": 1.5, "snippet": "# Eiwitmonitor 2025: eiwittransitie stagneert  De eiwittransitie is gestagneerd, blijkt uit de [Eiwitmonitor 2025](https://edepot.wur.nl/711209). Het aandeel plantaardig in het Nederlandse voedingspatroon blijft steken op 39%. Onderzoekers van Wageni", "tier": 2}, {"title": "Time Travelling Milkman gaat nieuwe samenwerking aan", "url": "https://www.eiwittrends.nl/time-travelling-milkman-gaat-nieuwe-samenwerking-aan/", "source": "Eiwittrends NL", "score": 1.5, "snippet": "# Time Travelling Milkman gaat nieuwe samenwerking aan  De Nederlandse start-up Time Travelling Milkman werkt samen met het Finse onderzoekscentrum VTT Technical Research Centre of Finland aan een nieuw plantaardig eiwit uit reststromen van zonnebloe", "tier": 2}, {"title": "Alle sprekers Eiwit Congres 2026 bekend", "url": "https://www.eiwittrends.nl/alle-sprekers-eiwit-congres-2026-bekend/", "source": "Eiwittrends NL", "score": 1.5, "snippet": "# Alle sprekers Eiwit Congres 2026 bekend  Inzicht in cijfers, strategieën en innovaties. Dat kun je verwachten op het Eiwit Congres 2026. Zo geeft Jumbo supermarkten een kijkje in de keuken en ook The Vegetarian Butcher Collective komt vertellen ove", "tier": 2}, {"title": "Ingrediënt The Protein Brewery veilig verklaard door Efsa", "url": "https://www.eiwittrends.nl/ingredient-the-protein-brewery-veilig-verklaard-door-efsa/", "source": "Eiwittrends NL", "score": 1.4, "snippet": "# Ingrediënt The Protein Brewery veilig verklaard door Efsa  Het ingrediënt Fermotein van [The Protein Brewery](https://www.eiwittrends.nl/fermotein-duurzame-eiwitbron-met-hoge-nutritionele-waarde/) krijgt een positief oordeel van de Europese voedsel", "tier": 2}, {"title": "Is het tijd voor een boete in de eiwittransitie?", "url": "https://www.eiwittrends.nl/is-het-tijd-voor-een-boete-in-de-eiwittransitie/", "source": "Eiwittrends NL", "score": 1.3, "snippet": "# Is het tijd voor een boete in de eiwittransitie?  Volgens Milieudefensie is het tijd voor boetes in de eiwittransitie. De organisatie waarschuwt dat de transitie veel te traag gaat door terughoudende supermarktketens. Consumenten blijven trouw aan ", "tier": 2}, {"title": "Fermentation-derived ingredients are powering the next wave of alternative protein innovation", "url": "https://gfi.org/blog/fermentation-derived-ingredients-are-powering-the-next-wave-of-alternative-protein-innovation/", "source": "GFI (Good Food Institute)", "score": 1.25, "snippet": "# Fermentation-derived ingredients are powering the next wave of alternative protein innovation - GFI India  If the future of meat is plant-based and cultivated, then fermentation is the stock that quietly adds a depth of flavour—holding the secret t", "tier": 1}, {"title": "Hybride als hefboom in de voedseltransitie", "url": "https://www.eiwittrends.nl/hybride-als-hefboom-in-de-voedseltransitie/", "source": "Eiwittrends NL", "score": 1.25, "snippet": "# Hybride als hefboom in de voedseltransitie  **Brabant combineert een volwassen voedselwaardeketen met een innovatieve maakindustrie en nabijheid van kennisinstellingen als HAS en Wageningen University & Research. Die combinatie maakt het mogelijk i", "tier": 2}, {"title": "Happy Plant Protein Outlines New Value Creation Strategy for Mills and Agricultural Co-Ops", "url": "https://vegconomist.com/manufacturing-technology/happy-plant-protein-outlines-new-value-creation-strategy-for-mills-and-agricultural-co-ops/", "source": "Vegconomist — Fermentation", "score": 1.15, "snippet": "# Happy Plant Protein Outlines New Value Creation Strategy for Mills and Agricultural Co-Ops - vegconomist - the vegan business magazine  Finnish foodtech company [Happy Plant Protein](https://vegconomist.com/organisations-and-brands/happy-plant-prot", "tier": 1}, {"title": "Precision Fermentation Takes Off in the Netherlands: Vivici and the Rise of Next-Gen Whey Protein", "url": "https://protein-trends.com/2025/06/08/precision-fermentation-takes-off-in-the-netherlands-vivici-and-the-rise-of-next-gen-whey-protein/", "source": "Protein Trends NL", "score": 1.15, "snippet": "# Precision Fermentation Takes Off in the Netherlands: Vivici and the Rise of Next-Gen Whey Protein  In Ede, the Netherlands, a symbolic shift is underway. Once home to dairy innovation, the town is now laying the foundation for a future where protei", "tier": 1}, {"title": "Vivici lanceert precisiefermentatie-lactoferrine in de VS", "url": "https://www.eiwittrends.nl/vivici-lanceert-precisiefermentatie-lactoferrine-in-de-vs/", "source": "Eiwittrends NL", "score": 1.1, "snippet": "# Vivici lanceert precisiefermentatie-lactoferrine in de VS  **De Nederlandse start-up Vivici brengt diervrij lactoferrine op de Amerikaanse markt, na zelf de Generally Recognized as Safe (GRAS) te hebben vastgesteld.**  Het is het tweede eiwit dat h", "tier": 2}];

const ScoreBadge = ({ score }: { score: number }) => {
  const color =
    score >= 2.0 ? 'bg-green-100 text-green-800' :
    score >= 0.8 ? 'bg-yellow-100 text-yellow-800' :
    'bg-gray-100 text-gray-600';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${color}`}>
      {score.toFixed(2)}
    </span>
  );
};

const TierBadge = ({ tier }: { tier: number }) => (
  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
    tier === 1 ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'
  }`}>
    T{tier}
  </span>
);

export default function BiotechRadar() {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'high' | 'tier1'>('all');

  const filtered = SIGNALS.filter(s => {
    const matchQuery =
      query === '' ||
      s.title.toLowerCase().includes(query.toLowerCase()) ||
      s.source.toLowerCase().includes(query.toLowerCase());
    const matchFilter =
      filter === 'all' ||
      (filter === 'high' && s.score >= 1.5) ||
      (filter === 'tier1' && s.tier === 1);
    return matchQuery && matchFilter;
  });

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-slate-900 text-white px-8 py-5">
        <h1 className="text-xl font-bold">Biotech Radar — Voedseltransitie</h1>
        <p className="text-sm opacity-60 mt-1">
          {SIGNALS.length} signalen · {SIGNALS.filter(s => s.score >= 1.0).length} hoog-relevant
        </p>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold">{SIGNALS.length}</div>
            <div className="text-xs text-gray-500 mt-1">Totaal signalen</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold text-green-700">{SIGNALS.filter(s => s.score >= 1.5).length}</div>
            <div className="text-xs text-gray-500 mt-1">Score ≥ 1.5</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold">{SIGNALS.filter(s => s.tier === 1).length}</div>
            <div className="text-xs text-gray-500 mt-1">Tier 1 bronnen</div>
          </div>
        </div>

        <div className="flex gap-3 mb-4 flex-wrap items-center">
          <input
            type="text"
            placeholder="Zoek in signalen..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="border border-gray-200 rounded-full px-4 py-1.5 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-slate-300"
          />
          {(['all', 'high', 'tier1'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                filter === f
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
              }`}
            >
              {f === 'all' ? 'Alle' : f === 'high' ? 'Score ≥ 1.5' : 'Tier 1'}
            </button>
          ))}
          <span className="text-xs text-gray-400 ml-auto">{filtered.length} resultaten</span>
        </div>

        <div className="space-y-3">
          {filtered.map((signal, i) => (
            <div
              key={i}
              className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:border-slate-300 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <a
                    href={signal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-blue-700 hover:underline line-clamp-2"
                  >
                    {signal.title}
                  </a>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <span className="text-xs text-gray-500">{signal.source}</span>
                    <TierBadge tier={signal.tier} />
                  </div>
                  {signal.snippet && (
                    <p className="text-xs text-gray-500 mt-2 line-clamp-2 leading-relaxed">
                      {signal.snippet}
                    </p>
                  )}
                </div>
                <div className="flex-shrink-0">
                  <ScoreBadge score={signal.score} />
                </div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-sm">Geen signalen gevonden</div>
          )}
        </div>
      </div>
    </div>
  );
}
