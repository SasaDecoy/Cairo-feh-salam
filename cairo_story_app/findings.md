# Findings · extracted from the notebooks

Authoritative record of every statistic the app cites. Source: `Phase 1 · Cleaning Data (1).ipynb`, `Phase 1 · Visual Analysis (1).ipynb`, `Phase 2 · Phase2_Scraping_Cleaning.ipynb`, `Phase 2 · Phase2_Analysis_Hypothesis.ipynb`.

## Phase 1 · counts

| Dataset | Rows | Source |
|---|---|---|
| bus stops · boarding | 1,302 | `cleaned_boarding.csv` |
| routes | 1,784 | `cleaned_routes.csv` |
| terminals | 280 | `cleaned_terminals.csv` |
| population hexes | 1,525 | `cleaned_population.csv` |
| passenger-flow segments | 9,258 | `cleaned_passenger_flow.csv` |
| vehicle-flow segments | 5,592 | `cleaned_vehicle_flow.csv` |
| speed records | 26,154 | `cleaned_speeds.csv` |

Cleaning: KNN imputation (k = 5, distance-weighted) on Boarding, Routes.Fare (45.9% null), Pax-Flow. CRS: EPSG:32636 (UTM 36N) for every spatial join. Zero rows dropped.

## Phase 1 · the four gaps

| Gap | Count | Definition |
|---|---|---|
| G1 · Ghost terminals | 115 | No boarding within 100 m buffer of route endpoints |
| G1 · Near-miss | 69 | 100 m – 500 m (relocate the stop) |
| G1 · Stop-too-far | 17 | 500 m – 1 km (walkability fix) |
| G1 · Truly isolated | 29 | > 1 km (audit / decommission) |
| G2 · Empty-return terminals | 19 | Empty Return Index ≥ 0.60; Index = 1 − pax/vehicles |
| G2 · Healthy terminals | 208 | Index = 0.0 |
| G3 · Vehicle-route mismatch | 75% | Of routes > 50 km use the smallest vehicle (microbus) |
| G4 · Underserved hexes | 79 | Underserved_Score = pop / total_boarding > 0.5 |

## Phase 1 · key Q-level findings

- **Q1** — Pearson r = 0.261 between morning alighting and job-accessibility; r = 0.248 for daily alighting. Weak positive correlation.
- **Q3** — 88.0% of alighting happens within 120 m of the designated route corridor.
- **Q8** — Moran-style local lag scatter shows HH/LL clusters of high-boarding stops (positive spatial autocorrelation).
- **Q11** — Terminal utilization zones: Efficient Hub = 76 · Marginal = 77 · Overcrowded/Underserved = 64 · Dead Weight = 63. Dead Weight terminals have the same route count as Efficient Hubs but **1,870× fewer passengers**.

## Phase 2 · H1 · Coverage-need mismatch

- Test: Kruskal-Wallis H = **55.7**, p **< 0.001**, ε² = **0.826** (huge effect)
- Tertile medians (stations per 100k residents):
  - Low density: **25.9**
  - Medium: **8.5**
  - High: **2.15**
- Sample: 68 districts (n_low = 23, n_med = 22, n_high = 23)
- Robustness: Chi-square + Welch t-test cross-checks confirm same direction
- Moran's I: **0.087**, z = 1.805, p = **0.0500** · 999 permutations · KNN-as-contiguity on real Nominatim centroids
- Methodology upgrade: real Nominatim district centroids from S6 (replaced earlier 3-governorate-centroid proxy) — this upgrade is what turned the small-to-medium effect into the huge effect

## Phase 2 · H2 · LRT catchment deficit

- Test: Mann-Whitney U = **2**, p < **0.0001**
- Cliff's δ = **−0.991** (near the theoretical maximum of −1)
- LRT operational stations with coordinates (n = 12): median 2-km population catchment = **916**
- Metro L3 post-2012 stations (n = 27): median = **634,333**
- Sensitivity: δ stays below −0.95 at 1, 2, and 3 km radii

## Phase 2 · H3 · BRT corridor match

- Test: Mann-Whitney U on 12 BRT stations vs random urbanized non-Ring-Road controls · p = **0.0001**
- Cliff's δ = **+0.710** (large positive)
- BRT corridor median daily informal boardings: **566**
- Matched control median: **0**
- Cross-validated with 10,000-iteration permutation test (same conclusion)

## Phase 2 · Q14 · Ghost terminals vs new metro

- 115 Phase 1 ghost terminals
- Within 1 km of any post-2014 metro station: **9** (8%)
- Beyond 2 km: **97** (84%)
- Distance buckets (0–1 / 1–2 / 2–5 / 5–10 / >10 km): **3 · 6 · 9 · 27 · 70**

## Phase 2 · Q18b · Gap-closure matrix (% of gaps within 2 km of a new station)

|  | G1 Ghosts | G2 Empty-return | G3 Vehicle mismatch | G4 Underserved |
|---|---|---|---|---|
| **Metro L3** | 15.7% | 5.3% | 0.0% | 9.7% |
| **LRT** | 3.5% | 5.3% | 25.0% | 2.6% |
| **BRT** | 4.3% | 10.5% | 25.0% | 13.6% |

Best cell is 25%; no cell above 25%; most below 16%. (No Monorail row — not operational.)

## Phase 2 · Q22 · Adly Mansour

- 4 modes within 2.5 km (metro + BRT + LRT terminal + OSM bus)
- 8 stations/terminals within the 2.5-km catchment
- **21st percentile** of 150 random Cairo 2.5-km clusters by station/terminal density (strategic interchange, not the strongest demand hub)

## Phase 2 · Q24 · K-Means

- k = **4**, ARI = **1.00** across 5 random seeds (perfect stability)
- Cluster sizes: Formal-Served Core = 31 · Peripheral Growth = 19 · Mixed (cluster 2) = 12 · Low-Activity Outskirts = 6
- Features: log population, CAGR, stations within 3 km, informal stops within 3 km, Cairo governorate indicator
- Target market = Formal-Served Core + Peripheral Growth + Mixed = **62 districts ≈ 18.9M residents**

## Phase 2 · scraping summary

| Source | n rows | Method |
|---|---|---|
| Wikipedia `List_of_Cairo_Metro_stations` | 89 | DMS→decimal; opening phase derived from year thresholds |
| Wikipedia `Cairo_LRT` | 20 (16 coord-rescued) | 9 via Overpass + 7 via Google Maps fallback |
| Google Maps BRT scrape | 12 | 10 viewport queries; regex aria-labels; uroman romanization; 3-tier dedup |
| citypopulation.de | 408 admin rows | Filtered to Greater Cairo; 2006→2017 CAGR |

Integration pipeline: Stage 1 KNN · Stage 2 OSM cross-verification · Stage 3 RapidFuzz token-sort at τ = 88 · Stage 4 SBERT (paraphrase-multilingual-MiniLM-L12-v2) at τ = 0.65 · 5-pair gold set for validation.
