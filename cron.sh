#!/bin/bash
# cron.sh — Dagelijkse pipeline runner
# Voeg toe aan crontab: 0 6 * * * /home/brewuser/projects/biotech-radar/cron.sh

set -e
cd "$(dirname "$0")"

echo "🧬 Biotech Radar pipeline — $(date)"

python3 pipeline/1_ophalen.py
python3 pipeline/1b_verrijken.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/4_synthese.py
python3 pipeline/5_publiceren.py

echo "✅ Pipeline klaar"
