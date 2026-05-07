-- Biotech Radar — Supabase Schema
-- Uitvoeren via: Supabase dashboard → SQL Editor → Run

-- ── Signalen tabel ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY,
  title TEXT,
  url TEXT,
  snippet TEXT,
  source_name TEXT,
  tier INTEGER DEFAULT 1,
  fetched_at TIMESTAMPTZ DEFAULT NOW(),
  published_at TEXT,
  source_type TEXT DEFAULT 'rss',
  filtered INTEGER DEFAULT 0,
  score REAL DEFAULT 0,
  full_text TEXT,
  summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index voor snelle queries
CREATE INDEX IF NOT EXISTS idx_signals_filtered ON signals(filtered);
CREATE INDEX IF NOT EXISTS idx_signals_score ON signals(score DESC);
CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source_name);

-- ── Rubric tabel (PESTLE weging — aanpasbaar via dashboard) ───────────────
CREATE TABLE IF NOT EXISTS rubric (
  id SERIAL PRIMARY KEY,
  category TEXT NOT NULL,        -- Policy, Economic, Social, Technology, Environmental, Policy_early
  weight REAL NOT NULL,          -- 0.0 - 1.0
  keywords TEXT[] NOT NULL,      -- array van zoekwoorden
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO rubric (category, weight, keywords) VALUES
  ('Policy',       0.35, ARRAY['regulation','EFSA','Novel Food','NGT','new genomic techniques','vergunning','approval','beleid','industriebeleid']),
  ('Economic',     0.30, ARRAY['funding','investering','scale-up','groeifonds','venture','markt','financiering','opschaling','commercialisatie','series']),
  ('Social',       0.20, ARRAY['consument','acceptatie','voedseltransitie','eiwittransitie','consumer','adoption','gezondheid']),
  ('Technology',   0.25, ARRAY['precision fermentation','fermentation','cellular agriculture','novel protein','alternative protein','plant protein','biobased','cultivated','synthetic biology']),
  ('Environmental',0.05, ARRAY['circulair','duurzaam','CO2','reststromen','klimaat','circular economy']),
  ('Policy_early', 0.40, ARRAY['first in EU','first in europe','precedent','paves way','pre-approval','regulatory sandbox','tasting event','proefsmaken','experimenteerruimte'])
ON CONFLICT DO NOTHING;

-- ── Feeds tabel (RSS bronnen — aanpasbaar via dashboard) ──────────────────
CREATE TABLE IF NOT EXISTS feeds (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  tier INTEGER DEFAULT 1,
  active BOOLEAN DEFAULT TRUE,
  last_fetched TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO feeds (name, url, tier, active) VALUES
  ('Vegconomist — Fermentation', 'https://vegconomist.com/feed/', 1, TRUE),
  ('Protein Trends NL', 'https://protein-trends.com/feed/', 1, TRUE),
  ('GFI (Good Food Institute)', 'https://gfi.org/feed/', 1, TRUE),
  ('Eiwittrends NL', 'https://www.eiwittrends.nl/feed/', 2, TRUE),
  ('BioPharma Trend', 'https://www.biopharmatrend.com/rss/', 1, TRUE),
  ('HollandBIO', 'https://www.hollandbio.nl/feed/', 2, TRUE),
  ('PubMed - precision fermentation', 'https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=precision+fermentation+food&format=abstract&limit=10', 1, TRUE)
ON CONFLICT DO NOTHING;

-- ── Brave queries tabel ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS brave_queries (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  query TEXT NOT NULL,
  tier INTEGER DEFAULT 1,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO brave_queries (name, query, tier) VALUES
  ('Precision fermentation NL', 'precision fermentation Netherlands scale-up food 2026', 1),
  ('EFSA Novel Food', 'EFSA Novel Food approval precision fermentation alternative protein 2026', 1),
  ('NGT food EU', 'new genomic techniques NGT food Netherlands EU regulation 2026', 1),
  ('Eiwittransitie NL', 'eiwittransitie sustainable protein opschaling Nederland 2026', 1),
  ('Cellular agriculture NL', 'cellular agriculture cultivated protein food Netherlands 2026', 1),
  ('Biobased food ingredients', 'biobased food ingredients fermentation Netherlands scale-up', 1),
  ('Novel protein EU market', 'novel protein alternative protein Europe market launch 2026', 1),
  ('BFF Ede fermentation', 'BFF Biotechnology Fermentation Factory Ede Netherlands 2026', 1)
ON CONFLICT DO NOTHING;

-- ── Briefings tabel ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS briefings (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  signal_ids TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Row Level Security (publiek leesbaar, alleen server schrijft) ─────────
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE rubric ENABLE ROW LEVEL SECURITY;
ALTER TABLE feeds ENABLE ROW LEVEL SECURITY;
ALTER TABLE brave_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;

-- Iedereen mag lezen (voor het dashboard)
CREATE POLICY "Public read signals" ON signals FOR SELECT USING (TRUE);
CREATE POLICY "Public read rubric" ON rubric FOR SELECT USING (TRUE);
CREATE POLICY "Public read feeds" ON feeds FOR SELECT USING (TRUE);
CREATE POLICY "Public read queries" ON brave_queries FOR SELECT USING (TRUE);
CREATE POLICY "Public read briefings" ON briefings FOR SELECT USING (TRUE);

-- Authenticated users mogen schrijven (voor dashboard-aanpassingen)
CREATE POLICY "Auth write signals" ON signals FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Auth write rubric" ON rubric FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Auth write feeds" ON feeds FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Auth write queries" ON brave_queries FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Auth write briefings" ON briefings FOR ALL USING (auth.role() = 'authenticated');
