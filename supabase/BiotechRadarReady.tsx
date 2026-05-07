// BiotechRadarLive.tsx
// Lovable component met live Supabase koppeling
//
// Setup in Lovable:
// 1. Klik "Connect Supabase" in Lovable
// 2. Of: npm install @supabase/supabase-js
// 3. Plak je SUPABASE_URL en SUPABASE_ANON_KEY in .env

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  "https://bnjrmfqqonkjkuelmtpl.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuanJtZnFxb25ramt1ZWxtdHBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NDMzNDUsImV4cCI6MjA4OTQxOTM0NX0.fwOQZPgt4BEJOmc03q9-KuFIDJe0PyYbOBmBjMQMknw"
);

interface Signal {
  id: string;
  title: string;
  url: string;
  source_name: string;
  score: number;
  snippet: string;
  tier: number;
  filtered: number;
  fetched_at: string;
}

interface RubricRow {
  id: number;
  category: string;
  weight: number;
  keywords: string[];
}

interface Feed {
  id: number;
  name: string;
  url: string;
  tier: number;
  active: boolean;
}

const ScoreBadge = ({ score }: { score: number }) => {
  const color =
    score >= 2.0 ? 'bg-green-100 text-green-800 ring-1 ring-green-200' :
    score >= 0.8 ? 'bg-yellow-100 text-yellow-800' :
    'bg-gray-100 text-gray-500';
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

// ── Tab: Signalen ────────────────────────────────────────────────────────
function SignalsTab() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'high' | 'tier1'>('all');

  useEffect(() => {
    supabase
      .from('signals')
      .select('*')
      .eq('filtered', 1)
      .order('score', { ascending: false })
      .limit(50)
      .then(({ data }) => {
        setSignals(data || []);
        setLoading(false);
      });
  }, []);

  const filtered = signals.filter(s => {
    const matchQ = query === '' ||
      s.title?.toLowerCase().includes(query.toLowerCase()) ||
      s.source_name?.toLowerCase().includes(query.toLowerCase());
    const matchF =
      filter === 'all' ||
      (filter === 'high' && s.score >= 1.5) ||
      (filter === 'tier1' && s.tier === 1);
    return matchQ && matchF;
  });

  if (loading) return <div className="text-center py-12 text-gray-400">Laden...</div>;

  return (
    <div>
      <div className="flex gap-3 mb-4 flex-wrap items-center">
        <input
          type="text"
          placeholder="Zoek..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="border border-gray-200 rounded-full px-4 py-1.5 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-slate-300"
        />
        {(['all', 'high', 'tier1'] as const).map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              filter === f ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-gray-600 border-gray-200'
            }`}>
            {f === 'all' ? 'Alle' : f === 'high' ? 'Score ≥ 1.5' : 'Tier 1'}
          </button>
        ))}
        <span className="text-xs text-gray-400 ml-auto">{filtered.length} resultaten</span>
      </div>

      <div className="space-y-2">
        {filtered.map(s => (
          <div key={s.id} className="bg-white rounded-xl p-4 border border-gray-100 hover:border-slate-300 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <a href={s.url} target="_blank" rel="noopener noreferrer"
                  className="text-sm font-semibold text-blue-700 hover:underline line-clamp-2">
                  {s.title}
                </a>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span className="text-xs text-gray-400">{s.source_name}</span>
                  <TierBadge tier={s.tier} />
                  <span className="text-xs text-gray-300">{s.fetched_at?.slice(0,10)}</span>
                </div>
                {s.snippet && (
                  <p className="text-xs text-gray-400 mt-1.5 line-clamp-2 leading-relaxed">
                    {s.snippet.replace(/<[^>]+>/g, '').slice(0, 180)}
                  </p>
                )}
              </div>
              <ScoreBadge score={s.score} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Tab: Rubric aanpassen ────────────────────────────────────────────────
function RubricTab() {
  const [rubric, setRubric] = useState<RubricRow[]>([]);
  const [saving, setSaving] = useState<number | null>(null);
  const [saved, setSaved] = useState<number | null>(null);

  useEffect(() => {
    supabase.from('rubric').select('*').order('id').then(({ data }) => setRubric(data || []));
  }, []);

  const updateWeight = async (id: number, weight: number) => {
    setSaving(id);
    await supabase.from('rubric').update({ weight, updated_at: new Date().toISOString() }).eq('id', id);
    setRubric(r => r.map(row => row.id === id ? { ...row, weight } : row));
    setSaving(null);
    setSaved(id);
    setTimeout(() => setSaved(null), 1500);
  };

  const CATEGORY_COLORS: Record<string, string> = {
    Policy: 'bg-blue-100 text-blue-800',
    Economic: 'bg-green-100 text-green-800',
    Social: 'bg-purple-100 text-purple-800',
    Technology: 'bg-orange-100 text-orange-800',
    Environmental: 'bg-teal-100 text-teal-800',
    Policy_early: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500">Pas de PESTLE-wegingen aan. Wijzigingen worden direct opgeslagen en gebruikt bij de volgende pipeline-run.</p>
      {rubric.map(row => (
        <div key={row.id} className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${CATEGORY_COLORS[row.category] || 'bg-gray-100 text-gray-700'}`}>
              {row.category}
            </span>
            <div className="flex items-center gap-3">
              <span className="text-sm font-bold text-slate-900">{Math.round(row.weight * 100)}%</span>
              {saving === row.id && <span className="text-xs text-gray-400">Opslaan...</span>}
              {saved === row.id && <span className="text-xs text-green-600">✓ Opgeslagen</span>}
            </div>
          </div>
          <input
            type="range" min={0} max={100} step={5}
            value={Math.round(row.weight * 100)}
            onChange={e => updateWeight(row.id, parseInt(e.target.value) / 100)}
            className="w-full accent-slate-900"
          />
          <div className="mt-2 flex flex-wrap gap-1">
            {row.keywords.slice(0, 8).map(kw => (
              <span key={kw} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{kw}</span>
            ))}
            {row.keywords.length > 8 && (
              <span className="text-xs text-gray-400">+{row.keywords.length - 8}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Tab: Feeds beheren ───────────────────────────────────────────────────
function FeedsTab() {
  const [feeds, setFeeds] = useState<Feed[]>([]);

  useEffect(() => {
    supabase.from('feeds').select('*').order('tier').then(({ data }) => setFeeds(data || []));
  }, []);

  const toggleFeed = async (id: number, active: boolean) => {
    await supabase.from('feeds').update({ active }).eq('id', id);
    setFeeds(f => f.map(feed => feed.id === id ? { ...feed, active } : feed));
  };

  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-500 mb-4">Beheer welke RSS-feeds actief zijn in de pipeline.</p>
      {feeds.map(feed => (
        <div key={feed.id} className="bg-white rounded-xl p-4 border border-gray-100 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{feed.name}</span>
              <TierBadge tier={feed.tier} />
            </div>
            <a href={feed.url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-gray-400 hover:text-blue-600 truncate block max-w-xs">
              {feed.url}
            </a>
          </div>
          <button
            onClick={() => toggleFeed(feed.id, !feed.active)}
            className={`relative inline-flex h-6 w-11 rounded-full transition-colors ${feed.active ? 'bg-green-500' : 'bg-gray-300'}`}>
            <span className={`inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform mt-0.5 ${feed.active ? 'translate-x-5' : 'translate-x-0.5'}`} />
          </button>
        </div>
      ))}
    </div>
  );
}

// ── Hoofdcomponent ───────────────────────────────────────────────────────
export default function BiotechRadarLive() {
  const [tab, setTab] = useState<'signals' | 'rubric' | 'feeds'>('signals');
  const [stats, setStats] = useState({ total: 0, relevant: 0 });

  useEffect(() => {
    Promise.all([
      supabase.from('signals').select('id', { count: 'exact', head: true }),
      supabase.from('signals').select('id', { count: 'exact', head: true }).eq('filtered', 1),
    ]).then(([total, relevant]) => {
      setStats({ total: total.count || 0, relevant: relevant.count || 0 });
    });
  }, []);

  const tabs = [
    { key: 'signals', label: '📋 Signalen' },
    { key: 'rubric', label: '⚖️ Rubric' },
    { key: 'feeds', label: '📡 Feeds' },
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-slate-900 text-white px-8 py-5">
        <h1 className="text-xl font-bold">🧬 Biotech Radar — Voedseltransitie</h1>
        <p className="text-sm opacity-60 mt-1">
          {stats.total} signalen · {stats.relevant} relevant · Live via Supabase
        </p>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
                tab === t.key ? 'bg-slate-900 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}>
              {t.label}
            </button>
          ))}
        </div>

        {tab === 'signals' && <SignalsTab />}
        {tab === 'rubric' && <RubricTab />}
        {tab === 'feeds' && <FeedsTab />}
      </div>
    </div>
  );
}
