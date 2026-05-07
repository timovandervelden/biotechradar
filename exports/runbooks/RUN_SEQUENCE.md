# Run Sequence — current prototype

## Machine-only run

```bash
python3 pipeline/1_ophalen.py
python3 pipeline/1.5_dedupe.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/3.5_cluster.py
python3 pipeline/4_select_shortlist.py
```

## Full run with interpretation

```bash
python3 pipeline/1_ophalen.py
python3 pipeline/1.5_dedupe.py
python3 pipeline/2_filteren.py
python3 pipeline/3_prioriteren.py
python3 pipeline/3.5_cluster.py
python3 pipeline/4_select_shortlist.py
python3 pipeline/5_analyse_llm.py
python3 pipeline/6_weekbriefing.py
```

## What each step adds

1. `1_ophalen.py` → haalt bronnen op
2. `1.5_dedupe.py` → canonicaliseert doublures en bewaart cross-bron referenties
3. `2_filteren.py` → scopefilter
4. `3_prioriteren.py` → rule-based scoring
5. `3.5_cluster.py` → patroon/clustervorming over bronnen en tijd
6. `4_select_shortlist.py` → selectie van signalen/clusters voor aandacht
7. `5_analyse_llm.py` → beleidsduiding via LLM
8. `6_weekbriefing.py` → wekelijkse output
