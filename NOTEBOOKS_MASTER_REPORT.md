# Master Report — Cairo Transport Project, Notebook by Notebook

> A self-contained guide for someone who has never seen this project. Reading
> this end-to-end is enough to understand every notebook: what goes in, what
> each cell does, what comes out, why each library and visualization was chosen,
> and what we learned from each research question.
>
> **This version reflects the current state of `Phase2/Phase2_Analysis_Hypothesis.ipynb`** — including the rewritten Q15, the new Q25, the upgraded H1 numbers (real Nominatim centroids, ε² = 0.826), and the three explicitly-named AI techniques.

---

## Part 0 — The Project in One Page

**The question.**
Cairo runs on two parallel transport systems:

- **System A (formal)** — the Metro, the new LRT to the New Administrative
  Capital, the Ring-Road BRT, and Transport-for-Cairo's published bus network.
  This is the system the state has been investing $10B+ in since 2014.
- **System B (lived)** — 1,302 informal microbus stops, 280 mawaqif (terminals),
  and the rider memory that keeps Cairo moving every morning.

The project asks: **where is the gap between what Cairo built and where Cairo lives?**

**The answer is built in four notebooks.**

| # | Notebook | Role | Output |
|---|---|---|---|
| 1 | [Cleaning Data.ipynb](Cleaning%20Data.ipynb) | Phase 1 cleaning — turn 7 raw GeoJSON files into 7 clean CSVs + 7 merged tables | `CleanedData/*.csv` |
| 2 | [Visual Analysis.ipynb](Visual%20Analysis.ipynb) | Phase 1 analysis — answer 12 research questions about the existing transport network | 40 Plotly HTML exports + 4 structural gaps (G1–G4) |
| 3 | [Phase2/Phase2_Scraping_Cleaning.ipynb](Phase2/Phase2_Scraping_Cleaning.ipynb) | Phase 2 ingestion — scrape 8 new sources, clean them, integrate them in a 4-stage matching pipeline (includes **AI Technique 1: SBERT**) | `Phase2/CleanedData/*.csv` + `Phase2/Integrated/*.geoparquet` |
| 4 | [Phase2/Phase2_Analysis_Hypothesis.ipynb](Phase2/Phase2_Analysis_Hypothesis.ipynb) | Phase 2 analysis — **13 trend questions (Q13–Q25)**, three formal hypotheses (H1, H2, H3), plus **AI Technique 2: K-Means** and **AI Technique 3: Moran's I** | Plotly figures + Folium maps + statistical tests + final headline map |

**Read order.** Each notebook depends on the previous one's output. Notebook 2
cannot run without Notebook 1's CSVs. Notebook 4 cannot run without Notebook 3's
CSVs **and** Notebook 1's CSVs (since Phase 2 cross-refers Phase 1's terminals
and ghosts).

**The three AI techniques** are explicitly enumerated across Notebooks 3 and 4:

| # | Technique | Where it lives | What it solves |
|---|---|---|---|
| 1 | **SBERT semantic matching** | Notebook 3 · Stage 4 of the integration pipeline | Cross-script (Arabic ↔ English) station-name matching that fuzzy text matching alone cannot do |
| 2 | **K-Means clustering** | Notebook 4 · Q24 | Groups districts into transport-demand segments → defines Masari's addressable market |
| 3 | **Moran's I spatial autocorrelation** | Notebook 4 · H1 robustness | Tests whether under-served districts cluster geographically rather than being randomly scattered |

---

## Part 1 — The Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│  RAW DATA                                                              │
│  • DatasetsGeojson/*.json     (7 Phase-1 GeoJSON files)                │
│  • Wikipedia, OSM, citypopulation.de, GoogleMaps, GTFS, World Bank     │
└──────────┬───────────────────────────────────┬─────────────────────────┘
           │                                   │
           ▼                                   ▼
┌─────────────────────────┐       ┌────────────────────────────────────┐
│  NOTEBOOK 1             │       │  NOTEBOOK 3                        │
│  Cleaning Data.ipynb    │       │  Phase2_Scraping_Cleaning.ipynb    │
│                         │       │                                    │
│  • Reproject EPSG:32636 │       │  • Scrape 8 sources (S1–S8)        │
│  • KNN-impute missing   │       │  • Clean each independently        │
│  • 7 merge tables A–G   │       │  • 4-stage integration pipeline    │
│                         │       │    (KNN → OSM verify → RapidFuzz   │
│  Outputs CleanedData/   │       │     → SBERT) ← AI Technique 1      │
└──────────┬──────────────┘       │  Outputs Phase2/CleanedData/ +     │
           │                      │  Phase2/Integrated/                │
           │                      └──────────────┬─────────────────────┘
           │                                     │
           ▼                                     ▼
┌─────────────────────────┐       ┌────────────────────────────────────┐
│  NOTEBOOK 2             │       │  NOTEBOOK 4                        │
│  Visual Analysis.ipynb  │       │  Phase2_Analysis_Hypothesis.ipynb  │
│                         │       │                                    │
│  • 12 research questions│       │  • 13 questions (Q13–Q25)          │
│  • 4 structural gaps    │◀──────│  • 3 hypotheses (H1, H2, H3)       │
│    G1 Ghosts (115)      │       │  • K-Means → AI Technique 2        │
│    G2 Empty Returns (19)│       │  • Moran's I → AI Technique 3      │
│    G3 Vehicle Mismatch  │       │  • Hero maps + market sizing       │
│    G4 Underserved (79)  │       │  • Masari Bridge (Q25, NEW)        │
└─────────────────────────┘       └────────────────────────────────────┘
                                                 │
                                                 ▼
                                  ┌────────────────────────────────────┐
                                  │  cairo_story_app/ (Streamlit)      │
                                  │  Cinematic story + 25 evidence     │
                                  │  pages.                            │
                                  └────────────────────────────────────┘
```

**Why two phases?**
- Phase 1 audits the system *as it exists today* and produces the four
  structural gaps that justify why Cairo needs an analysis at all.
- Phase 2 evaluates the *new* infrastructure built since 2014 and asks whether
  it fixed any of those gaps. The answer (built rigorously) is "almost none of
  them" — which is the opening of the Masari product story.

**Why two notebooks per phase?**
- Cleaning + scraping has different libraries, different failure modes, and
  different reproducibility concerns than analysis. Splitting prevents one
  broken scrape from hiding analytical bugs and lets the analysis notebook
  treat its inputs as stable.
- Standard data-science discipline: **engineering before analysis**.

---

## Part 2 — Notebook 1 · `Cleaning Data.ipynb`

**Purpose.** Take Cairo's seven raw transport GeoJSON files, fix their CRS,
impute missing values, build the seven merged tables that downstream
questions need, and write everything to `CleanedData/`.

### 2.1 Inputs

Located in `DatasetsGeojson/`:

| File | Rows (after) | What it is |
|---|---|---|
| `Cairo Daily Boarding.json` | 1,302 | Bus stops with daily boarding/alighting counts per time-of-day |
| `Public Transport Routes.json` | 1,784 | Route lines with `Vehicle_Type`, fare, length |
| `Public Transport Terminals.json` | 280 | Terminal points (mawaqif) — origin/destination of routes |
| `Public Transport Passenger Flow.json` | 9,258 | Road segments with passengers/hour |
| `Public Transport Vehicles Flow.json` | 5,592 | Road segments with vehicles/hour |
| `Public Transport Commercial Speeds 2.json` | 26,154 | Road segments with average bus speed |
| `Population & Employment Access .json` | 1,525 | 1 km² hexagonal grid with population + job-accessibility scores |

### 2.2 Outputs

Written to `CleanedData/`:

- 7 cleaned single-dataset CSVs (`cleaned_boarding.csv`,
  `cleaned_routes.csv`, ...).
- 7 merged tables `merge_A.csv` … `merge_G.csv` plus question-specific helpers
  (`q4_formal_vs_informal.csv`, `q9_underserved.csv`, `q11_ghosts.csv`, …).
- A null-audit summary used in Notebook 2 (`null_audit.csv`).

### 2.3 Libraries

```python
geopandas, pandas, numpy        # tabular + geo I/O
sklearn.impute.KNNImputer       # missing-value imputation
plotly.graph_objects, plotly.subplots   # before/after audit charts
shapely (via geopandas)         # geometry ops (buffer, sjoin, dissolve)
IPython.display.HTML            # styled inline tables in the notebook
```

These are the *only* libraries this notebook uses.

### 2.4 Cell-by-cell walkthrough (12 sections)

**SECTION 01 · Imports and display settings.**
Loads the libraries, suppresses warnings (KNNImputer is noisy), and widens
pandas's display so wide tables render cleanly.

**SECTION 02 · Load raw GeoJSON files.**
`gpd.read_file(...)` on each of the 7 raw files. Output: `boarding_raw`,
`routes_raw`, `terminals_raw`, `pax_flow_raw`, `veh_flow_raw`, `speeds_raw`,
`population_raw`. Prints a styled HTML table of row counts and geometry types
so the load is sanity-checked before continuing.

**SECTION 03 · Reproject to EPSG:32636.**

```python
CRS_METERS = "EPSG:32636"   # UTM Zone 36N
boarding   = boarding_raw.to_crs(CRS_METERS)
# … same for the other 6 datasets
```

**Why.** The raw files come in EPSG:4326 (lat/long in degrees). Degrees are
useless for distance work — at Cairo's latitude 1° of longitude is ~96 km
while 1° of latitude is ~111 km. Every analysis using a buffer (Q3 = 120 m
corridor, Q11 = 100 m ghost test), a nearest-neighbor join, or an area
calculation must be in *meters*. UTM Zone 36N is the right projected CRS for
Egypt — distances and areas come out correct without manual scaling.
**All downstream code assumes meters.**

**SECTION 04 · Rename columns.**
Maps raw source field names (often inconsistent, sometimes Arabic, often
inherited from PTV Visum exports) into a clean vocabulary — `Stop_Name`,
`Total_Routes_At_Stop`, `Daily_All_BA`, `Vehicle_Type`, `Route_Length_km`,
`Population_2018`, `Jobs_In_Hex`, etc.

**SECTION 05 · Cast numeric types.**
`pd.to_numeric(..., errors="coerce")` on every numeric column. Anything that
fails to parse becomes `NaN`. We choose `coerce` rather than `raise` because
the raw data has dirty cells (text like "n/a", "?", commas in thousands) that
we want to handle systematically rather than crash on.

**SECTION 06 · Null audit BEFORE imputation.**
Counts nulls per column per dataset. Three fields are imputable: `Boarding`
numeric counts, `Routes.Fare`, `Pax_Flow.Passengers_Per_Hour`. Snapshot is
reused later for the before/after visualization in Section 7d.

**SECTION 07 · KNN Imputation.**
The most important methodological section. Uses
`sklearn.impute.KNNImputer(n_neighbors=5, weights="distance",
metric="nan_euclidean")`.

Three sub-imputations run independently:

| Imputation | Features used | Why |
|---|---|---|
| Boarding numeric (12 cols, 42 rows, ~250 cells) | XY coords + all boarding numeric cols | Spatially close stops with similar counts inform each other |
| Routes.Fare (45.9% null) | Route length, capacity, direction, encoded vehicle type | Routes with similar physical attributes get similar fare estimates |
| Pax_Flow (Passengers/Hour) | Segment centroid XY + segment length | Geometrically similar segments inform each other |

**Why KNN, not mean / zero / drop?**
- A missing count is **unknown**, not proof of zero activity. Imputing zeros
  would *invent* the conclusion that some stops are dead.
- Mean imputation collapses spatial structure. KNN preserves it.
- Dropping rows would lose 42 stops out of 1,302 — small in count but
  potentially the most interesting ones (incomplete fields often mark new or
  edge-case stops).
- `weights="distance"` so closer neighbors count more.
- `metric="nan_euclidean"` lets the imputer compute distance even when the
  feature vector itself has missing entries (skips the missing dimensions).

**Result.** Zero null rows after this step. **Zero rows dropped.**

**SECTION 08 · Sanity checks + engineered fields.**
Adds derived columns the later questions need:
- `Total_Routes_At_Stop` (sum of all `routes_*` columns).
- `Daily_All_BA` (total daily boarding across all modes).
- `Transport_Class` for routes (formal vs informal — used by Q4).

**SECTION 09 · Spatial and attribute joins (Merges A–G).**

The heart of the notebook. Each merge is built once here so every question
downstream can read a pre-joined CSV instead of re-running expensive spatial
operations.

| Merge | Operation | Serves |
|---|---|---|
| **A** Boarding ⨝ Population | `gpd.sjoin(predicate="within")` — point-in-polygon | Q1 (jobs × alighting), Q9 (underserved hexes) |
| **B** Terminals ⨝ Population | Spatial centroid join | Q2 (terminal symmetry), Q5 (density × terminals) |
| **C** Routes ⨝ Terminals | Attribute join on `o_id` and `d_id` | Q10 (empty returns), Q11 (ghosts) |
| **D** Vehicle/Pax Flow ⨝ Terminals | 50 m buffer aggregation | Q2, Q10 |
| **E** B + D | Full per-terminal record | Q2 |
| **F** Routes per terminal | Group-by counts | Q11 |
| **G** Underused-terminal detector | Terminal flagged "underused" if it has routes but **zero** boarding within a 100 m buffer of route endpoints | Q11 (the core "ghost terminal" definition) |

**Why pre-merge?** Every question would otherwise repeat the same `sjoin`. With
~9,000 segments × 280 terminals × 1,500 hexes, repeating spatial joins is
expensive. Doing it once and persisting saves time and guarantees every
question sees the *same* joined data.

**Embedded formulas worth knowing.**

```text
G2 · Empty Return Index = 1 − (passengers / vehicles)
   0  = every vehicle carries passengers
   1  = every vehicle departs empty
   ≥ 0.60 → critical (this defines the 19 G2 terminals)

G4 · Underserved Score = Population / Total_Boarding
   > 0.5 → underserved (this defines the 79 G4 hexes)
```

**SECTION 10 · Single-dataset analyses.**
Per-question lookup CSVs from one cleaned dataset each. No spatial joins.
Examples: Q4 mode classification, Q6 routes×passengers, Q7 morning/evening
ratios, Q12 vehicle-fit, Q3 corridor adherence, Q5 density flag, Q8 NN-mean
neighbor (k=8), Q9 underserved score.

**SECTION 11 · Export cleaned outputs.**
`df.to_csv(...)` for everything. The visualization notebook reads only from
`CleanedData/`.

**SECTION 12 · Final summary.**
Prints the KNN imputation summary table and the merge-to-question mapping.

### 2.5 Why this notebook works

- It is **sectioned** (12 sections, each one job).
- It is **idempotent** (running again gives the same output).
- It is **reproducible** (zero rows dropped, every imputation documented).
- It **separates engineering from analysis** — the visualization notebook
  doesn't even know what KNN is.

---

## Part 3 — Notebook 2 · `Visual Analysis.ipynb`

**Purpose.** Answer 12 research questions about Cairo's existing transport
network and produce the four structural gaps (G1–G4) that justify the whole
project.

### 3.1 Inputs

Reads only from `CleanedData/` (Notebook 1's outputs). It does *not* re-clean
or re-impute — the contract with Notebook 1 is "you produce, I consume."

### 3.2 Outputs

- 40 standalone Plotly HTML files in `Exports/` (Q1a, Q1b, Q2a, Q2b, …).
- The four structural gaps:
  - **G1 — 115 ghost terminals** (no boarding within 100 m).
  - **G2 — 19 empty-return terminals** (Empty Return Index ≥ 0.60).
  - **G3 — vehicle/route mismatch** (75% of routes > 50 km use the smallest
    vehicle, the microbus; 44 long-route violations specifically).
  - **G4 — 79 underserved hexes** at the > 0.5 threshold (Phase 2 also
    reports a broader 381-hex top-quartile cohort for product-sizing context).
- Two interactive Folium maps embedded in the notebook (Q1 jobs and Q9
  underserved).

### 3.3 Libraries

```python
geopandas, pandas, numpy
plotly.express as px, plotly.graph_objects as go, plotly.subplots.make_subplots
folium, folium.plugins.HeatMap        # interactive maps
sklearn.neighbors.NearestNeighbors    # k-NN for Q8 spatial autocorrelation
IPython.display.HTML                  # inline rich-text panels
```

`sklearn` here is used *only* for nearest-neighbor lookup, not for any
modelling. Plotly is used because every figure must export to standalone HTML
to be embeddable in the Streamlit app.

### 3.4 Sections 01–04 · setup

- **01 Imports** — load libraries.
- **02 Theme & helpers** — define an 8-color palette and a reusable
  `_dark_layout` helper so every figure inherits the same dark theme. Also
  defines the two CRS constants (`CRS_METERS = EPSG:32636`,
  `CRS_MAP = EPSG:4326`) and `to_map_crs()`.
- **03 Load cleaned datasets** — `pd.read_csv` / `gpd.read_file` from
  `CleanedData/`.
- **04 Shared references** — Cairo map center, pre-computed terminal centroids.

### 3.5 The 12 research questions

#### Q1 · Morning alighting × job accessibility

- **Question.** Do people get off the bus near where the jobs are?
- **Method.** Pearson r between morning alighting and job-accessibility score.
- **Charts.** Top-30 stops paired-subplot (rank-driven story); 2D density
  heatmap (1,302 points are too dense for raw scatter).
- **Insight.** **r = 0.261 (morning), r = 0.248 (daily)** — meaningfully
  positive but weak. Routes deposit riders at canonical terminals, not at job
  centroids.

#### Q2 · Terminal route symmetry

- **Question.** Are some terminals one-way dead ends?
- **Method.** Per-terminal `|routes_origin − routes_dest| / max(origin, dest)`.
- **Charts.** Top-25 paired bars (asymmetry visually obvious); histogram
  + most-asymmetric callouts.
- **Insight.** Most are symmetric, but a long tail of extreme asymmetry feeds
  the G2 (empty-return) analysis.

#### Q3 · Designated drop points

- **Question.** What share of alighting happens within 120 m of the formal
  route line?
- **Method.** `routes.geometry.buffer(120).unary_union` then point-in-polygon
  test.
- **Insight.** **88.0% of alighting** falls within 120 m of a formal route
  corridor.

#### Q4 · Formal vs informal mode choice

- **Question.** When do commuters switch from the formal system to informal?
- **Charts (5).** Histogram of formal share, morning vs daily scatter,
  absolute volumes formal vs informal, fare vs route length, top-20 stops by
  informal boarding.
- **Insight.** Informal transport dominates absolute volume across the city.
  Microbuses are the spine of the lived network.

#### Q5 · Population density vs terminal locations

- **Question.** Does Cairo place its terminals where the people are?
- **Charts.** Scatter, distribution WITH vs WITHOUT terminals, Folium hex map.
- **Insight.** Terminals correlate weakly with population. Many densely
  populated hexes have no terminal at all.

#### Q6 · Routes per stop vs passenger volume

- **Question.** Does adding more routes to a stop bring more passengers?
- **Charts.** Scatter with trendline, avg by route-count bins, per-route
  demand, major-stops bar.
- **Insight.** The relationship is **linear with no plateau** — coverage
  expansion is a real lever.

#### Q7 · Morning vs evening boarding symmetry

- **Charts.** Log-log scatter (data spans orders of magnitude); refined
  ratio histogram.
- **Insight.** Most stops symmetric, meaningful asymmetric tail anchors
  commute-corridor stops.

#### Q8 · Spatial autocorrelation

- **Method.** For each stop compute mean boarding of its 8 nearest neighbors;
  Moran-style lag scatter.
- **Charts.** Enhanced Moran scatter (log-log); quadrant distribution bar.
- **Insight.** Positive spatial autocorrelation: high-boarding clusters
  (HH) and low-boarding clusters (LL) — demand has clear spatial structure.

#### Q9 · Underserved areas (G4 gap)

- **Method.** `Underserved_Score = Population / Total_Boarding`.
  Hexes > 0.5 → underserved.
- **Charts.** Folium choropleth; log-log scatter (population vs boarding).
- **Insight (Gap G4).** **79 hexes** at the > 0.5 threshold. They cluster
  around Imbaba, Shubra, and other dense informal-housing zones — exactly
  where Phase 2 will later show that new metro/LRT/BRT did not reach.

#### Q10 · Empty return problem (G2 gap)

- **Method.** `Empty_Return_Index = 1 − (passengers / vehicles)` per terminal.
  Index ≥ 0.60 → critical.
- **Charts.** Top-20 worst (ranked bar); vehicles-vs-passengers scatter with
  diagonal; Folium map (size = vehicles, color = empty index, heatmap =
  passenger boardings).
- **Insight (Gap G2).** **19 critical terminals** vs 208 healthy.

#### Q11 · Ghost terminals (G1 gap)

- **Method.** Buffer each terminal by 100 m; check for any nonzero boarding
  inside. Then expand the buffer (200 m, 300 m, …, 1 km) and watch how many
  ghosts "recover" — distinguishes measurement artifact from real abandonment.
- **Charts (7).** Recovery curve with slider; bar by recovery category;
  routes-vs-boarding scatter; quadrant chart (4 operational zones); zone
  bars; treemap of route budget by zone; Folium map.
- **Insight (Gap G1).** **115 ghosts at 100 m**: 69 near-miss (100–500 m),
  17 stop-too-far (500 m–1 km), 29 truly isolated (> 1 km). At 500 m, only
  46 ghosts remain → **60% recovery** at a 6-minute walk. Dead-Weight zone:
  same route count as Efficient Hubs but **1,870× fewer passengers**.

#### Q12 · Vehicle–route fit (G3 gap)

- **Charts (5).** Violin (per vehicle type), heatmap (length × capacity),
  box plot (fare per km), bubble (length × fare × capacity), ECDF (% of
  routes < X km).
- **Insight (Gap G3).** **75% of routes > 50 km use the smallest vehicle**
  (microbus). 44 specific long-route violations. Microbuses are doing the
  work that buses *should* be doing.

### 3.6 Conclusion of Notebook 2

Cairo has a working bus network on top of an even larger informal microbus
system, and the two are structurally entangled. This is the bridge to Phase 2.

---

## Part 4 — Notebook 3 · `Phase2/Phase2_Scraping_Cleaning.ipynb`

**Purpose.** Build a credible, multi-source dataset of *new* transport
infrastructure and integrate it with Phase 1's terminals so the analysis
notebook can ask: "did the new stuff close the gaps?"

### 4.1 Inputs

Eight external sources, each scraped or downloaded fresh:

| Code | Source | What it gives us |
|---|---|---|
| **S1** | Transport-for-Cairo GTFS feed (TfC GitHub) | Formal published bus + metro stops, routes, trips, shapes, fares |
| **S3** | Wikipedia `List_of_Cairo_Metro_stations` | 89 metro stations with names, coordinates, opening dates |
| **S4** | Wikipedia `Cairo_Light_Rail_Transit` | 20 LRT stations (operational + planned + extension) |
| **S5** | Google Maps (Playwright scrape) | 12 BRT stations |
| **S6** | citypopulation.de | 408 admin rows, filtered to Greater Cairo |
| **S7** | Wikipedia + World Bank API | National vehicle totals + per-capita series |
| **S8** | OpenStreetMap Overpass | Independent transport-feature layer for cross-verification |

### 4.2 Outputs

In `Phase2/CleanedData/`:
- `gtfs_stops.csv`, `gtfs_routes.csv`, `gtfs_trips.csv`, `gtfs_shapes.csv`,
  `gtfs_fare_attributes.csv`
- `metro_stations.csv`, `lrt_stations.csv`, `brt_stations.csv`
- `districts.csv`, `districts_wide.csv`
- `vehicles_by_governorate.csv`
- `osm_features.geojson`
- `null_audit_before.csv`, `null_audit_after.csv`

In `Phase2/Integrated/`:
- `matched_pairs.csv` — each scraped station paired with the nearest Phase 1
  terminal plus match confidence.
- `Phase2_integrated.geoparquet` — all integrated geometries in one parquet.

### 4.3 Libraries

```python
# core
pathlib, datetime, re, json, zipfile, time, asyncio, subprocess, sys
numpy, pandas, geopandas
shapely.wkt
dateutil.parser

# scraping
scrapling.fetchers.Fetcher, DynamicFetcher    # static + JS-rendered HTML
scrapling.parser.Selector
playwright.async_api.async_playwright          # browser automation for Google Maps

# matching
sklearn.neighbors.NearestNeighbors             # spatial KNN
sklearn.linear_model.LinearRegression          # used in Stage 4 baseline
sklearn.metrics.pairwise.cosine_similarity     # cosine on SBERT vectors
rapidfuzz.process, rapidfuzz.fuzz              # Stage 3 fuzzy text matching
sentence_transformers.SentenceTransformer      # Stage 4 multilingual SBERT
uroman                                         # Arabic → Latin transliteration

# visualization
plotly.graph_objects                           # null-audit + integration Sankey
IPython.display.display
phase2_utils (local)                           # show_df / show_metrics / show_note
```

**Why these specifically.**
- **scrapling + playwright**: Wikipedia is static HTML (Fetcher); Google Maps
  requires a real browser to render search results (DynamicFetcher / Playwright).
- **uroman, not MarianMT**: we want *transliteration* (المرج → "almrj") not
  *translation* (المرج → "lawn"). Translating semantically would break the
  station-name matching downstream.
- **rapidfuzz**: Levenshtein-based fuzzy matching, ~10× faster than
  python-Levenshtein.
- **sentence_transformers**: gives us multilingual embeddings so we can match
  "المعادي" against "Maadi" semantically — fuzzy matching alone fails on
  cross-script comparisons.

### 4.4 Cell-by-cell flow

The notebook is 13 sections — each is one source or one integration stage.
Every source block follows the same 7-step pattern: define URL → check cache →
fetch → parse → standardize → save → print summary.

#### S1 · TfC GTFS

Downloads two zip bundles (bus+metro, paratransit), unzips, loads each of the
8 standard GTFS CSVs, filters `stops` to a Cairo bounding box, reprojects to
EPSG:32636.

#### S3 · Wikipedia metro master list

`pd.read_html` on `List_of_Cairo_Metro_stations`, 3 wikitables (one per line).
Custom parser: strips footnotes, converts DMS coordinates to decimal, parses
opening dates to year, derives the "phase" label from year thresholds.
89 stations, 100% coordinates, dual-language names.

#### S4 · Wikipedia LRT

3 wikitables — 20 stations total. **0% have coordinates on the page.**
Two-stage backfill: OSM Overpass per-station name search recovers 9
coordinates; Google Maps fallback recovers another 7. **16 of 20 LRT stations
have coordinates** (used in H2). 4 remain coordinate-less (planned but not
yet on the ground).

#### S5 · BRT via Google Maps

BRT has no Wikipedia page. 10 viewport queries against Google Maps using
Playwright; regex parses `aria-label` attributes; uroman transliterates Arabic
names; three-tier dedup → 12 stations.

#### S6 · citypopulation.de

408 admin rows, filtered to Greater Cairo. Reshape wide → long, compute
**CAGR 2006 → 2017** per district. Per-district centroid via Nominatim — a
**critical methodological upgrade** because H1 in Notebook 4 now uses these
real centroids instead of a 3-governorate-centroid proxy.

#### S7 · Vehicles

National total from Wikipedia + per-capita from World Bank Open Data API.
Apportion to governorates by population share. Used only as background context.

#### S8 · OSM Overpass

All `public_transport`, `railway`, `highway=bus_stop` features inside a Cairo
bounding box. Used for Stage 2 of the integration pipeline.

#### Section 10 · Data quality audit

Per-source null-audit table. **Grouped bar chart** (Plotly) showing
null-percentage per column per source.

#### Cleaning steps 01–04

After all sources are loaded, four explicit cleaning steps run, then a
final null re-audit verifies cleaning worked.

#### Section 11 · The 4-stage integration pipeline

Goal: pair each scraped station with the most likely Phase 1 terminal.

| Stage | Method | What it solves |
|---|---|---|
| **1** | `sklearn.neighbors.NearestNeighbors` (k=1 in EPSG:32636) | First-pass spatial pairing |
| **2** | OSM cross-verification (flag if nearest OSM node > 50 m away) | Catches scraped-coordinate errors |
| **3** | `rapidfuzz.process.extractOne` (token_sort, threshold τ = 88) | Resolves spelling/punctuation drift |
| **4** | **AI Technique 1: SBERT** (`paraphrase-multilingual-MiniLM-L12-v2`, threshold τ = 0.65) on combined `station_en + station_ar` | Cross-script semantic matching (Arabic ↔ English) |

A 5-pair gold set validates Stage 4 — if SBERT misses any of those 5, the
threshold gets re-tuned.

#### Section 12 · Source → question mapping
Reference table linking S1–S8 to Q13–Q25 / H1–H3.

#### Section 13 · Output manifest + final gate

Defensive contract: every downstream-required output must exist before
Notebook 4 is allowed to run.

---

## Part 5 — Notebook 4 · `Phase2/Phase2_Analysis_Hypothesis.ipynb`

**Purpose.** Answer 13 trend questions (Q13–Q25), test 3 formal hypotheses
(H1, H2, H3), and use two more AI techniques (K-Means clustering, Moran's I
spatial autocorrelation). The notebook explicitly opens by saying it delivers
"twelve trend questions, three hypothesis tests, and three AI-technique
enhancements."

### 5.1 Inputs

- All Notebook 3 outputs (`Phase2/CleanedData/*`, `Phase2/Integrated/*`).
- All Notebook 1 outputs (`CleanedData/*`) — in particular the 4 gaps
  (G1 ghosts, G2 empty returns, G3 vehicle mismatch, G4 underserved hexes).

### 5.2 Outputs

- ~30+ Plotly figures.
- 3 standalone Folium maps in `Phase2/`:
  - `two_cairos_map.html` — the hero map.
  - `headline_coverage_need_map.html` — the final synthesis.
  - `adly_mansour_zoom.html` — the Q23 case study.
- A K-Means segmentation (k = 4) and a market-sizing chart.
- A closing one-line-per-question summary table.

### 5.3 Libraries

```python
# data + geo
pandas, numpy, geopandas, shapely.geometry.Point, shapely.wkt

# stats
scipy.stats          # Kruskal-Wallis, Mann-Whitney, Wilcoxon, Pearson,
                     #   Spearman, Chi-square, Welch t-test
libpysal.weights.Queen, KNN
esda.moran.Moran, Moran_Local      # AI Technique 3: Moran's I + LISA

# ML
sklearn.preprocessing.StandardScaler
sklearn.cluster.KMeans              # AI Technique 2: K-Means
sklearn.metrics.silhouette_score, adjusted_rand_score
sklearn.neighbors.NearestNeighbors
sklearn.linear_model.LinearRegression
rapidfuzz.process, fuzz             # name re-matching for source lookups

# viz
plotly.graph_objects, plotly.express, plotly.subplots.make_subplots
folium, folium.plugins.HeatMap
matplotlib.pyplot, seaborn          # only for a few diagnostic plots

# misc
itertools.combinations, random
phase2_utils                        # styled output helpers
```

The `cliffs_delta()` helper for non-parametric effect size lives in
Section 01 and is reused by all three hypothesis sections.

### 5.4 The 13 research questions

#### Q13 · Metro coverage × density (Section 05)

- **Question.** Did each metro line open into the population geography that
  *existed at the time*?
- **Why this version.** A station opened in 1987 should not be judged only
  against 2018 hex population. This version compares each station to the
  nearest district's **closest available population year** (1996 / 2006 /
  2017 / 2023) — avoiding the all-years-vs-2018-hex mismatch the earlier
  version had.
- **Method.** Spearman rank correlation per metro line between opening year
  and average nearby population.
- **Charts.** 3-panel scatter (one per line), opening year × adjacent
  population, Spearman ρ annotated.
- **Insight.** Lines 1 and 2 (pre-2005) show modest density sorting; **Line 3
  (extended through 2024) shows the strongest positive correlation between
  opening year and adjacent density** — meaning the newer Phase 3B/3C/3D
  stations *did* sort into denser eastern corridors when those districts had
  grown enough by their opening year.

#### Q14 · Ghost terminals near new metro (Section 06)

- **Question.** Do Phase 1's 115 ghost terminals sit close to the new Phase-3
  metro stations?
- **Method.** Distance from each ghost to nearest post-2014 metro station;
  bucket: 0–1 / 1–2 / 2–5 / 5–10 / >10 km.
- **Chart.** Bar chart of distance buckets.
- **Insight.** **The most damning chart in the project.** **97 of 115 ghost
  terminals (84%) sit 2+ km from any post-2014 metro station.** Only 9 (8%)
  within 1 km. The $10B in new rail missed the structural pain point
  Phase 1 documented.

#### Q15 · Metro × bus/microbus terminal integration (Section 07) **[REWRITTEN]**

- **Question.** Do metro stations connect to Cairo's bus and microbus
  terminal backbone? Can riders actually transfer?
- **Why it matters.** The product story is not just whether rail exists. It
  is whether formal rail gives riders a clean transfer into the informal
  network they already use. A metro station near a high-route terminal is
  where System A and System B can meet.
- **Method.** For each metro station, find the nearest Phase 1 bus/microbus
  terminal; attach that terminal's route count, passenger flow, and
  ghost-terminal status.
- **Charts.** Two views:
  - **Timeline of station openings colored by metro line, y-axis =
    distance to nearest terminal.** Why: shows whether *recent* expansions are
    closer or farther from the existing terminal backbone than older ones.
  - **Distribution by line.** Why: per-line summary.
  - Horizontal bands mark practical transfer thresholds (250 m, 500 m, 1 km).
- **Insight.** Stations close to high-route terminals are where System A and
  System B can meet — they're the transfer points Masari should privilege
  in route planning. Stations far from any high-route terminal are
  "stranded rail" — formally there but functionally disconnected from how
  most Cairenes actually move.
- **Note.** This question previously asked "metro km vs bus-terminal ratio
  over time" with a dual-axis time series. The current version is a much
  cleaner spatial-integration question.

#### Q16 · Fastest-growing districts 2006→2023 (Section 08)

- **Question.** Which districts grew fastest, and did they get new-mode
  coverage?
- **Method.** Top 15 by `cagr_2006_2017`. For each, count nearest stations
  in a 2 km buffer around its population centroid.
- **Charts.** Slope chart (2006 population on left, 2023 on right, lines
  colored by CAGR tier).
- **Insight.** Top 15 are **dominated by new satellite cities**:
  - **New Cairo 1 (+15.4%)**
  - **6th October City 1 & 3 (+13.3%)**
  - **Ash-Shurūq (+13.1%)**
  - **Sheikh Zayed (+10.8%)**
  - These are deliberately-built-from-scratch suburbs in the desert. Demand is
    being created by planners, not by organic urbanization in dense cores.

#### Q17 · Population density vs underserved score (Section 09)

- **Question.** Is density the main predictor of underservedness, or is
  coverage-need mismatch unrelated to density?
- **Method.** Spearman correlation on per-hex (density, underserved score).
- **Charts.** Hex-bin scatter (x = log population, y = underserved score)
  with a highlighted "dense + underserved" red zone.
- **Insight.** Q17 now **names the target, not just the pattern**. The
  dense-and-underserved quadrant produces a concrete list of hexes — places
  where many people live, boarding activity is not keeping up, and underserved
  score is in the top quartile. **These are the hexes Masari should prioritize.**

#### Q18 · Informal-transport share by density (Section 10)

- **Question.** Does informal modal share rise with density, or is informal
  ubiquitous?
- **Method.** Compute informal share = 1 − formal_share per hex. Spearman ρ
  + OLS slope of log-population → informal share. Q18b extends with the
  gap-closure matrix.
- **Charts.** Scatter with regression line, colored by hex_pop quartile;
  per-governorate motorization × informal share scatter (S7); 3 × 4 gap-closure
  heatmap.
- **Insight (Q18 main).** **Spearman ρ = 0.025, p = 0.40, slope ≈ 0.010 →
  statistically flat.** Informal transport is **not density-targeted**; it's
  ubiquitous background transport, averaging **~47% modal share** across
  Cairo. This refutes the assumption that "informal = poor neighborhoods."
- **Insight (Q18b · gap-closure matrix · the verdict).** **Best cell = 25%
  (BRT and LRT on G3 vehicle-route mismatch). Every other cell below 16%.**

  | | G1 Ghosts | G2 Empty-return | G3 Vehicle mismatch | G4 Underserved |
  |---|---|---|---|---|
  | **Metro L3** | 15.7% | 5.3% | 0.0% | 9.7% |
  | **LRT** |  3.5% | 5.3% | 25.0% | 2.6% |
  | **BRT** |  4.3% | 10.5% | 25.0% | 13.6% |

  Ten billion dollars closed almost none of the Phase 1 gaps.

#### Q19 · GTFS coverage vs Phase 1 formal/informal reality (Section 11)

- **Question.** Does the published GTFS feed cover the formal network we saw
  in Phase 1, and where does informal demand remain outside it?
- **Method.** Compare route inventories (GTFS formal, Phase 1 formal, Phase 1
  informal). Spatially merge GTFS stops with Phase 1 stops by nearest-neighbor
  distance; classify each Phase 1 stop as formal-dominant or informal-dominant.
- **Charts.** Route-inventory comparison + stop-proximity distribution.
- **Insight.** Q19 now tests **the real product boundary**. GTFS gives Masari
  a strong formal backbone, but Phase 1 shows many stops where informal demand
  dominates *and* the nearest GTFS stop is too far to explain the trip. **Those
  stops are the crowdsourcing frontier** — where Masari needs rider-contributed
  data because no published feed covers them.

#### Q20 · Ring-Road BRT vs informal (Section 12)

- **Question.** Does the 2025 BRT corridor lie on the same corridor that
  informal microbuses were already serving?
- **Method.** Buffer each BRT station 500 m; count Phase 1 stops inside; sum
  daily-informal boardings.
- **Chart.** Horizontal ranked bar — per-BRT-station informal demand served.
- **Insight.** A BRT station with thousands of informal boardings in its
  500 m buffer was built onto **existing demand** — successful formalization.
  A station with near-zero informal nearby is repeating the LRT's mistake.

#### Q21 · Fare per km · formal vs informal (Section 13)

- **Question.** Which mode offers better fare per km — formal or informal?
- **Method.** Real GTFS fare tables for formal modes; Phase 1 vehicle-type
  fares for informal.
- **Charts.** Box plot by vehicle type with strip overlay; two-tone
  (formal blue, informal coral).
- **Insight (real GTFS numbers).**
  - Formal **Bus**: median **0.22 EGP/km** (214 routes).
  - Formal **Subway (Metro)**: median **0.25 EGP/km**.
  - Informal **Microbus**: median **0.62 EGP/km** (861 routes) — **3× formal**.
  - Informal **Tomnaya**: median **1.30 EGP/km** (115 routes) — **6× formal**.
  - **Formal transport is meaningfully cheaper per km.** Riders pay an
    informal premium because formal does not reach them.

#### Q22 · Where metro underperforms its density prediction (Section 14)

- **Question.** Given a district's population, how many metro stations
  *should* it have, and how far is reality from that?
- **Method.** OLS regression: population → number of metro stations within a
  3 km buffer of the district centroid. Residual = observed − predicted.
- **Chart honesty note.** The residual scatter degenerates because every
  district sharing a governorate-centroid proxy ends up with the same
  station count. The notebook switches to a **horizontal ranked bar of the
  top-15 most-under-served districts** by residual — which conveys the
  finding without the proxy artifact.
- **Insight.** Worst residuals (most under-served):
  - **Ad-Duqqi (−9.28)**
  - **Sheikh Zayed (−9.09)**
  - **6th October City 1 & 3 (−8.52)**
  - **Al-Ḥawāmidiyah (−8.14)**
  - All dense or rapidly-growing **Giza/Qalyubia** districts. Closing this
    gap is a state function in the long run; meeting it now is Masari's
    short-run job.

#### Q23 · Adly Mansour · the "seventh mode" convergence (Section 15)

- **Question.** How many distinct transport modes terminate at Adly Mansour,
  and how does its station density compare with Greater Cairo's median
  cluster?
- **Method.** Find the Adly Mansour node; buffer 1 km; count stations per
  source. Then sample 150 random Cairo clusters of the same radius; plot a
  histogram with Adly Mansour as a reference line.
- **Charts.** Folium zoom + percentile histogram.
- **Insight.** **Adly Mansour sits around the 17th percentile of the random
  cluster sample** — noticeably denser than average but **not an extreme
  outlier**. The Transport Minister's "seventh mode" framing is a political
  declaration, not a demographic phenomenon. *(This is a major revision —
  the earlier draft put it at the 83rd percentile.)*
- **Bonus finding.** Inside the 2.5 km meeting-point buffer, four modes
  co-exist: Metro Line 3 (terminus), Cairo LRT (origin toward NAC), Cairo BRT
  (Ring Road stop), and Phase-1 informal terminals — Al-Salam (1.4 km),
  Awwal Madinet, etc.

#### Q24 · Coverage-need synthesis · K-Means segmentation (Section 16)

**This is AI Technique 2.**

- **Question.** If we cluster Greater Cairo districts by coverage, density,
  and growth, which cluster is Masari's primary market?
- **Method.** **5 features per district**: pop_2023, CAGR, nearest-station
  count from Q22, informal demand intensity (from Q4 stops), governorate
  share encoded. `StandardScaler` → `KMeans(n_init=50)`.
- **Model selection.** Elbow + silhouette over k ∈ [2, 8]. Stability check:
  `adjusted_rand_score` across **5 random seeds**. ARI > 0.6 = stable.
- **Charts (the K-Means visual set is the largest in the notebook).**
  Elbow + silhouette charts; cluster size bar; feature z-score heatmap;
  parallel coordinates (`go.Parcoords`); radar/scatterpolar of cluster
  centroids; cluster priority bar (informal intensity − formal coverage).
- **Insight.** Silhouette peaks at k = 2 (0.63), but **k = 4 is forced for
  policy granularity**. **ARI = 1.00 across 5 seeds (perfect stability).**
  The four clusters:
  - **Cluster 1 — Established Cairo Core** (n = 23): 290k median pop,
    0.95% CAGR, ~20 stations, ~96 informal stops. **Masari's primary target.**
  - Cluster 2 — Peripheral Growth (~22 districts).
  - Cluster 3 — Hot Growth (new satellite cities).
  - Cluster 4 — Low-Activity Outskirts.

#### Q25 · Masari Bridge · informal demand → formal access (Section 17) **[NEW]**

- **Question.** Where should Masari connect informal demand into the formal
  network?
- **Why it matters.** The app is not only a map of missing places. It is a
  **routing bridge**. This question identifies the actual first/last-mile
  connectors.
- **Method.** Build one *formal-node layer* from GTFS stops + Metro + LRT +
  BRT. Build one *informal-demand layer* from Phase 1 stops where
  informal daily boarding exceeds formal daily boarding. For each informal
  stop, find the nearest formal node; score the bridge by demand × inverse
  distance.
- **Chart.** Map with red points (informal demand), multi-color points
  (formal nodes), and connector lines joining each informal stop to its
  nearest formal node.
- **Insight.** **This is Masari in one figure.** Red = informal system
  people already use. Blue/gold/green/orange = formal system apps can
  already read. **Connector lines = the missing product layer.** Short
  connectors become immediate routing wins; long connectors flag where
  Masari's value is not just connection but rider-contributed routing.

### 5.5 The three formal hypotheses

Each transforms an intuition from the questions into a defensible test.
Every hypothesis section includes **robustness checks** (Chi-square, Welch
t-test, permutation) alongside the primary non-parametric test.

#### H1 · Coverage-need mismatch + Moran's I (Section 17/18) **[UPGRADED]**

**This section also runs AI Technique 3 (Moran's I).**

- **H₀.** Districts in every density tertile receive the same rate of
  new-mode stations per capita.
- **H₁.** Dense districts receive systematically fewer new-mode stations per
  capita.
- **Primary test.** Kruskal-Wallis H across density tertiles, with post-hoc
  Mann-Whitney U.
- **Robustness.** Chi-square + Welch t-test as cross-checks.
- **Methodology upgrade.** **Now uses real Nominatim district centroids from
  S6**, not the earlier 3-governorate-centroid proxy — this makes the KNN
  spatial-weights graph meaningful for the first time.
- **Effect size.** ε² (epsilon-squared).
- **Spatial check (AI Technique 3).** Moran's I with KNN-as-contiguity
  spatial weights and 999 permutations.
- **Result.** **Kruskal-Wallis H = 55.7, p < 0.001, ε² = 0.826** (huge
  effect — formerly small-to-medium before the centroid upgrade).
  - Low-density tertile: **median 25.9 stations per 100k residents**.
  - High-density tertile: **median 2.15 stations per 100k**.
  - **A ~12× gap.** Coverage scales **inversely** with need.
- **Charts.** Box plot per tertile (K-W p annotated) + LISA cluster map on a
  Folium basemap.

#### H2 · LRT catchment deficit (Section 18/19)

- **H₀.** LRT stations have the same median 2 km catchment as post-2012
  metro stations.
- **H₁.** LRT stations have systematically smaller catchments.
- **Primary test.** Mann-Whitney U.
- **Effect size.** Cliff's δ.
- **Method.** For each LRT and each post-2012 metro station, spatial-join
  Phase 1 population hexes within 2 km, sum `Population_2018`.
- **Sensitivity.** δ tested at 1 km, 2 km, 3 km radii — stays below −0.95
  in all three.
- **Methodology note.** **Now with 16 LRT station coordinates** (OSM +
  Google Maps backfill from Notebook 3 S4) — up from 9 in earlier drafts. The
  result is **unambiguous**.
- **Result.** **Mann-Whitney p < 0.001, Cliff's δ = −0.993** (effectively
  the maximum negative).
  - LRT operational stations (n = 16): median 2 km catchment = **0** residents.
  - Post-2012 Metro L3 stations (n = 27): median = **634,333**.
- **Charts.** Box plot per group + per-station ranked bar (every LRT
  station's coral bar visibly below almost every metro station's blue bar).
- **Insight.** The LRT is **structurally sited in low-demand land** — not
  "sometimes empty" but built ahead of demand.

#### H3 · BRT corridor match (Section 19/20)

- **H₀.** The Ring Road BRT corridor carries the same pre-BRT informal
  demand density as an equivalent-length non-Ring-Road corridor.
- **H₁.** Ring Road BRT corridor has higher pre-BRT informal demand,
  indicating BRT correctly formalized existing demand.
- **Primary test.** **Mann-Whitney U** (two-sample, non-normal). *(Earlier
  drafts framed this as Wilcoxon paired; the current notebook uses a random
  non-Ring-Road urbanized control sample, which makes Mann-Whitney correct.)*
- **Effect size.** Cliff's δ.
- **Method.** For each BRT station's 500 m buffer, sum informal boardings.
  Construct matched non-Ring-Road controls by sampling random points from
  the urbanized area at similar distance-to-center.
- **Result.** **Mann-Whitney p ≪ 0.05, Cliff's δ = +0.826** (large positive).
  - BRT corridor median informal demand: **1,576 daily boardings**.
  - Matched non-Ring-Road control median: **0**.
- **Charts.** Violin plot — BRT corridor vs control.
- **Insight.** BRT is the **single planning success** of the post-2014
  infrastructure. It saves the project from being one-note: "not all new
  infrastructure is wrong — only the parts built ahead of demand are."

### 5.6 Final synthesis sections

- **Section 20 · Headline coverage-need map** (`headline_coverage_need_map.html`).
  Folium overlay of K-Means cluster colors on Greater Cairo districts with
  new-mode stations on top. Cluster 2 (Peripheral Growth, 22 Giza/Qalyubia
  districts, 9.5M residents) and Cluster 1 (Established Cairo Core) carry the
  highest informal-to-station gap — Masari's market.
- **Section 21 · Animated metro expansion 1987 → 2026.** Plotly animated
  scatter, one frame per opening year. Fourteen years in 30 seconds: Line 1
  (1987) → Line 2 (1996–2005) → long pause → Line 3 (2014, then phases 3A/3B/3C/3D
  through 2024).
- **Section 22 · Masari market sizing.** Sum 2023 population per cluster.
  Bar chart with primary market highlighted in coral.
- **Sunburst (governorate → cluster → district)** as a closing
  novel visualization.
- **Closing summary.** A one-line answer per question (Q13 through Q25)
  followed by a "Project complete" note that explicitly enumerates the
  three AI techniques: SBERT (semantic matching), K-Means (segmentation),
  Moran's I (spatial autocorrelation).

### 5.7 Why this notebook is rigorous

- **Non-parametric tests everywhere.** Cairo's distributions are skewed
  and small-sample.
- **Effect sizes alongside every p-value.**
- **Robustness layer per hypothesis.** Each hypothesis runs a primary
  non-parametric test plus Chi-square + Welch t-test cross-checks.
- **Sensitivity analysis on H2.** Tested at 1/2/3 km buffer radii.
- **Real centroids for H1.** The Nominatim upgrade in S6 turned a
  small-to-medium-effect result into the **ε² = 0.826** finding.
- **K-Means stability check (ARI = 1.00 across 5 seeds).** Clusters aren't
  random-init artifacts.
- **Honesty about proxy artifacts (Q22).** When the residual scatter
  degenerated due to governorate-centroid proxies, the notebook switched to
  a ranked bar instead of pretending the scatter was clean.

---

## Part 6 — The Visualization Vocabulary

Why each chart type appears where it does:

| Chart type | Used for | Why this and not something else |
|---|---|---|
| **Bar chart (vertical)** | Top-N rankings, before/after, distribution by group | Direct, scannable, reads left-to-right naturally |
| **Bar chart (horizontal)** | Long category labels (station names, district names) | Labels stay readable; ranking still works |
| **Stacked bar** | Composition (formal vs informal share by agency) | Shows part-of-whole *and* total at once |
| **Grouped bar** | Comparing many columns across multiple sources (null audit) | Easier visual scan than a wide table |
| **Histogram** | Distribution shape, identifying tails | Best primitive for "how is X distributed?" |
| **Density heatmap** | Crowded scatter (1,000+ points) | Avoids overplotting |
| **2D heatmap (matrix)** | Two categorical axes + one numeric (Q18b gap-closure) | Natural for tabular data with a value cell |
| **Scatter** | Two continuous variables, correlation, outlier hunt | The fundamental relationship view |
| **Scatter with trendline** | Q6 (routes vs passengers) | Adds linearity test visually |
| **Log-log scatter** | Q7, Q8, Q9 (data spans 3+ orders of magnitude) | Without logs the chart compresses 99% of points into a corner |
| **Joint plot with marginals** | Q17 (density × underserved) | Joint relationship + univariate distributions in one figure |
| **Hexbin** | Q17 alternative — dense scatter | Same logic as density heatmap; uses hex tiles for clean tessellation |
| **Box plot** | Group comparison emphasizing median + IQR + outliers | When you care about spread and outliers, not just mean |
| **Violin plot** | Distribution *shape* per group (Q12 routes by vehicle, H3) | Reveals multimodality that a box plot would hide |
| **Quadrant chart** | Q11 ghost terminals (routes × boarding) | Naturally splits into 4 operational zones |
| **Treemap** | Q11 route budget allocation | Shows allocation by area; better than pie for >5 groups |
| **Bubble chart** | Q12 (length × fare × capacity) | Encodes 3 variables on 2 axes |
| **ECDF** | Q12 ("what % of routes are < X km?") | Gives an exact cumulative answer |
| **Slope chart** | Q16 (district growth between two years) | Emphasizes change between two specific points |
| **Time series (single axis)** | Q21 metro km over time (where used) | Standard for one variable over time |
| **Timeline scatter (Q15)** | Station openings × distance to nearest terminal | Combines time and a continuous spatial metric |
| **Animated scatter / map** | Metro expansion 1987–2026 | Time is a sequence, not a snapshot |
| **Choropleth map** | Q9 underserved hexes, district-level data | The natural primitive when geography matters |
| **Heatmap (Folium tile)** | Q10 passenger boarding density on a map | Smooths point data into a continuous surface |
| **Parallel coordinates** | Q24 K-Means clusters | Shows individual cluster members across many features |
| **Radar chart** | Q24 K-Means cluster signatures | Memorable comparison of group profiles |
| **Sunburst** | K-Means hierarchy (governorate → cluster → district) | Hierarchical relationship a bar chart can't show |
| **Sankey** | Notebook 3 integration pipeline yield | Shows flow between stages |
| **Indicator panels (KPIs)** | Phase 1 recap dashboard | Headline numbers, no distribution needed |
| **CDF / cumulative curve** | H2 LRT catchment | Cumulative coverage without losing distribution shape |
| **LISA scatter / cluster map** | H1 spatial autocorrelation | The standard local-Moran visualization |
| **Bridge map (Q25)** | Informal stops connected to nearest formal node by line | The product story made literal — connectors *are* the value |

**The unifying principle.** Every chart type is chosen to match the *shape of
the question*. We never use a chart because it looks impressive — we use it
because it answers the question better than the alternatives.

---

## Part 7 — Library Reference

### Notebook 1 (Cleaning)

| Library | Why |
|---|---|
| `geopandas` | Read GeoJSON, reproject CRS, spatial joins |
| `pandas` | Tabular ops |
| `numpy` | Numeric primitives |
| `sklearn.impute.KNNImputer` | Spatial KNN imputation of missing values |
| `plotly.graph_objects`, `plotly.subplots` | Before/after audit charts |
| `IPython.display.HTML` | Styled inline tables |

### Notebook 2 (Phase 1 Visual Analysis)

| Library | Why |
|---|---|
| `geopandas`, `pandas`, `numpy` | Same as Notebook 1 |
| `plotly.express`, `plotly.graph_objects`, `plotly.subplots` | All static figures |
| `folium`, `folium.plugins.HeatMap` | Interactive Leaflet maps in-notebook |
| `sklearn.neighbors.NearestNeighbors` | k-NN for Q8 spatial autocorrelation |
| `IPython.display.HTML` | Inline rich-text panels |

### Notebook 3 (Phase 2 Scraping/Cleaning)

| Library | Why |
|---|---|
| Standard library: `pathlib`, `datetime`, `re`, `json`, `zipfile`, `time`, `asyncio`, `subprocess`, `sys`, `textwrap`, `importlib` | Scraping plumbing |
| `pandas`, `numpy`, `geopandas` | Tables + geo |
| `shapely.wkt` | Parse WKT geometries |
| `dateutil.parser` | Parse human-written dates from Wikipedia |
| `scrapling.fetchers.Fetcher`, `DynamicFetcher` | Static + JS-rendered HTML scraping |
| `scrapling.parser.Selector` | CSS / XPath HTML parsing |
| `playwright.async_api` | Browser automation for Google Maps |
| `sklearn.neighbors.NearestNeighbors` | Stage 1 spatial KNN integration |
| `sklearn.linear_model.LinearRegression` | Auxiliary stage diagnostics |
| `sklearn.metrics.pairwise.cosine_similarity` | Cosine on SBERT vectors |
| `rapidfuzz.process`, `fuzz` | Stage 3 fuzzy text matching |
| **`sentence_transformers.SentenceTransformer`** | **AI Technique 1 · Stage 4 multilingual SBERT** |
| `uroman` | Arabic → Latin transliteration |
| `plotly.graph_objects` | Null-audit and integration charts |
| `IPython.display.display` + `phase2_utils` | Styled output panels |

### Notebook 4 (Phase 2 Analysis)

| Library | Why |
|---|---|
| `pandas`, `numpy`, `geopandas` | Tables + geo |
| `shapely.geometry.Point`, `shapely.wkt` | Geometry construction |
| `scipy.stats` | Kruskal-Wallis, Mann-Whitney, Wilcoxon, Spearman, Pearson, Chi-square, Welch t-test |
| `libpysal.weights.Queen`, `KNN` | Spatial-weights matrices |
| **`esda.moran.Moran`, `Moran_Local`** | **AI Technique 3 · Moran's I + LISA** |
| `sklearn.preprocessing.StandardScaler` | Standardize features for K-Means |
| **`sklearn.cluster.KMeans`** | **AI Technique 2 · Q24 K-Means** |
| `sklearn.metrics.silhouette_score`, `adjusted_rand_score` | K-Means model selection + stability |
| `sklearn.neighbors.NearestNeighbors` | NN lookups in Q14, Q22, Q25 |
| `sklearn.linear_model.LinearRegression` | Q22 OLS residual regression |
| `rapidfuzz.process`, `fuzz` | Cross-source name matching |
| `plotly.graph_objects`, `plotly.express`, `plotly.subplots` | All static figures |
| `folium`, `folium.plugins.HeatMap` | Hero maps + Adly Mansour zoom + Q25 bridge |
| `matplotlib.pyplot`, `seaborn` | A few diagnostic plots only |
| `IPython.display.display`, `HTML` + `phase2_utils` | Styled output panels |

---

## Part 8 — Reading-Order Cheat Sheet

If you're new to the project and want to master it, read in this order:

1. **`README.md`** — 5 minutes, project at-a-glance.
2. **This document, Parts 0–1** — 10 minutes, workflow + the 3 AI techniques.
3. **`Cleaning Data.ipynb`** — 30 minutes, the cleanest notebook to start with.
4. **`Visual Analysis.ipynb`** — 60 minutes, work through Q1 → Q12 in order.
5. **`Phase2/Phase2_Scraping_Cleaning.ipynb`** — 45 minutes, follow S1 → S8
   then the 4-stage integration pipeline.
6. **`Phase2/Phase2_Analysis_Hypothesis.ipynb`** — 90 minutes, the densest
   notebook. Read Q13–Q25 then H1/H2/H3 then the K-Means.
7. **`Phase2/PHASE2_METHODS_AND_STORY_DOCUMENTATION.md`** — for the
   explanation of *why* each method was chosen.
8. **`drafts/MASARI_PHASE2_STORY_SCENES.md`** — for the narrative arc that
   ties analysis to product.
9. **`cairo_story_app/`** — the Streamlit app (run with
   `streamlit run cairo_story_app/streamlit_app.py`).

---

## Part 9 — One-Page Cheat Sheet (Numbers You Should Know)

| Number | What it means |
|---|---|
| **EPSG:32636** | UTM 36N — Cairo's correct projected CRS |
| **k = 5** | KNN imputation neighbor count, distance-weighted |
| **0** | Rows dropped during cleaning |
| **1,302** | Phase 1 boarding stops |
| **1,784** | Phase 1 routes |
| **280** | Phase 1 terminals |
| **1,525** | Phase 1 population hexes |
| **115** | G1 Ghost terminals (no boarding within 100 m) |
| **19** | G2 Empty-return terminals (Empty Return Index ≥ 0.60) |
| **44 / 75%** | G3 Specific long-route violations / share of routes > 50 km on microbus |
| **79 / 381** | G4 Underserved hexes at > 0.5 threshold / broader top-quartile cohort |
| **88.0%** | Q3 alighting within 120 m of the formal corridor |
| **r = 0.261** | Q1 morning alighting × job-accessibility correlation |
| **89 / 16 / 12** | Phase 2 metro / LRT (with coordinates) / BRT stations scraped |
| **τ = 0.65** | SBERT cosine threshold for Stage 4 matching |
| **τ = 88** | RapidFuzz token-sort threshold for Stage 3 matching |
| **84%** | Q14 ghost terminals beyond 2 km of any new metro station |
| **47%** | Q18 average informal modal share across Cairo (statistically flat with density) |
| **25%** | Q18b best gap-closure cell (BRT × Vehicle Mismatch) |
| **0.22 / 0.25 / 0.62 / 1.30 EGP/km** | Q21 fares: Bus / Metro / Microbus / Tomnaya |
| **−9.28 (Ad-Duqqi)** | Q22 worst metro-coverage residual |
| **17th percentile** | Q23 Adly Mansour station-density rank vs random Cairo clusters |
| **k = 4, ARI = 1.00 (5 seeds)** | Q24 K-Means cluster count and stability |
| **n = 23, Cluster 1** | Established Cairo Core — Masari's primary target |
| **H = 55.7, p < 0.001, ε² = 0.826** | H1 Kruskal-Wallis result (real Nominatim centroids) |
| **25.9 vs 2.15 stations / 100k** | H1 low-density vs high-density tertile medians (~12× gap) |
| **δ = −0.993** | H2 Cliff's δ (LRT catchment vs Metro L3) |
| **0 vs 634,333 residents** | H2 LRT vs Metro L3 median 2 km catchment |
| **δ = +0.826** | H3 Cliff's δ (BRT corridor vs control) |
| **1,576 vs 0 daily boardings** | H3 BRT corridor vs matched control medians |

---

## Part 10 — Glossary

Every technical term in this report, defined in plain English. If you've never
heard a term before, look it up here first.

### Geospatial / data-engineering

**CRS (Coordinate Reference System).** A rule that maps numbers (like 31.24,
30.05) to a real point on Earth. Different CRSs are tuned for different
purposes.

**EPSG:4326.** The "lat/long in degrees" CRS that GPS, Google Maps, and most
GeoJSON files use. Good for storage and display, **bad for distance**.

**EPSG:32636 (UTM Zone 36N).** A *projected* CRS for Egypt. Coordinates are
in **meters from a chosen origin**. Distances and areas are accurate to
centimeters in Cairo. **Every spatial calculation in this project uses
EPSG:32636.**

**Reproject.** Convert geometry from one CRS to another. Code:
`df.to_crs("EPSG:32636")`.

**Spatial join (`sjoin`).** Like a SQL join, but the matching condition is
geometry — "this point lies inside this polygon," etc.

**Predicate.** The geometric matching rule in a spatial join (`within`,
`intersects`, `contains`).

**Buffer.** Grow a geometry outward by a fixed distance.

**Centroid.** The geometric center of a polygon. Used as a single point to
represent a district. For Phase 2 H1, **Nominatim-derived district centroids**
replaced an earlier governorate-centroid proxy — a key methodological upgrade.

**Hexagon (in Cairo data).** Phase 1 ships population data on a 1 km²
hexagonal grid (1,525 hexes). Hexes are used because every neighbor is the
same distance away.

**Haversine distance.** "As the crow flies" distance between two lat/long
points on a sphere.

**KNN (k-Nearest Neighbors).** Find the *k* points in a dataset closest to a
query. Used for imputation (Notebook 1) and spatial integration (Notebook 3).

**KNN imputation.** Filling missing values by looking at *k* similar rows.
"Distance-weighted" means closer neighbors count more. "nan_euclidean" handles
missing entries by skipping the missing dimensions.

**GeoJSON.** Standard JSON-based format for geospatial data.

**GeoParquet.** Binary, columnar version of GeoJSON. Faster, smaller.

**WKT (Well-Known Text).** Human-readable string format for geometry, e.g.
`POINT(31.24 30.05)`.

**GTFS.** International standard for publishing public-transport schedules
(stops, routes, trips, shapes, fares).

**OSM (OpenStreetMap).** Community-edited world map. Used as an *independent*
source to cross-check Wikipedia-scraped station coordinates.

**Overpass API.** Query language and HTTP API for pulling features out of OSM.

**Bounding box (bbox).** A rectangle (min_lng, min_lat, max_lng, max_lat).

### Statistics

**Pearson r.** Linear correlation, range −1 to +1.

**Spearman ρ.** Monotonic correlation on ranks. Use when distributions are
skewed or non-linear.

**Non-parametric test.** Doesn't assume normality. We use these *everywhere*
in Phase 2.

**Kruskal-Wallis (H).** Non-parametric ANOVA for 3+ groups. Used in H1.

**Mann-Whitney U.** Non-parametric two-sample test. Used in H2 and H3.

**Wilcoxon signed-rank.** Non-parametric *paired* test.

**Welch t-test.** Parametric two-sample test that doesn't assume equal
variance. Used as a robustness check in H1.

**Chi-square test.** Tests independence of categorical variables. Used as a
robustness check in H1.

**Permutation test.** Significance via shuffling labels thousands of times.
Used for Moran's I (999 permutations) and as cross-validation for H3.

**p-value.** Probability of the observed effect under the null hypothesis.
Smaller = stronger evidence.

**Effect size.** *How big* the difference is. Always report alongside p.

**Cliff's δ.** Non-parametric effect size for two groups, range −1 to +1.
**|δ| > 0.474** is "large." H2 = −0.993 (max negative); H3 = +0.826.

**ε² (epsilon-squared).** Effect size for Kruskal-Wallis, range 0 to 1.
H1 = 0.826 → "huge effect."

**Moran's I.** **AI Technique 3 in this project.** Spatial autocorrelation
statistic.
- I > 0: similar values cluster together.
- I = 0: spatially random.

**LISA (Local Indicators of Spatial Association).** Per-point local Moran
— labels places HH / LL / HL / LH.

**Queen-contiguity weights.** Spatial-weights matrix where two regions are
"neighbors" if they share *any* boundary.

**KNN-as-contiguity.** When polygon adjacency isn't available (our case for
districts), use k-nearest neighbors as a proxy for contiguity.

**Tertile / decile.** Dataset split into thirds / tenths.

**CDF / ECDF.** Cumulative distribution function / its empirical version.

### Machine learning

**StandardScaler.** Subtract mean and divide by SD per feature. Required
before K-Means.

**K-Means.** **AI Technique 2 in this project.** Unsupervised clustering. We
force k = 4, n_init = 50.

**Elbow method.** Heuristic for choosing k.

**Silhouette score.** Clustering quality metric, range −1 to +1. Peaked at
k = 2 (0.63) for our Q24 — but k = 4 forced for policy granularity.

**ARI (Adjusted Rand Index).** Compares two cluster assignments. Range −1 to
+1. Used for stability — **ARI = 1.00 across 5 seeds** = perfect stability.

**SBERT (Sentence-BERT).** **AI Technique 1 in this project.** Multilingual
sentence-embedding model. Specific model: `paraphrase-multilingual-MiniLM-L12-v2`.
Lets us match "Maadi" against "المعادي" semantically.

**Embedding.** Vector representation of an item. Embeddings let you measure
similarity numerically.

**Cosine similarity.** Angle between two vectors, range −1 to +1. Threshold
τ = 0.65 for Stage 4.

**RapidFuzz.** Fast fuzzy-string-matching library. Threshold τ = 88 for Stage 3.

**Transliteration vs translation.** Transliteration converts characters
phonetically ("المرج" → "almrj"); translation converts meaning ("المرج" →
"lawn"). For matching place names, transliteration is correct.

**OLS (Ordinary Least Squares).** Standard linear regression. Used in Q22.

**Residual.** Actual minus predicted. Negative residuals in Q22 = districts
with less metro than density predicts.

### Visualization terms

**Choropleth.** Map where regions are colored by a numeric variable.

**Hexbin.** 2D histogram tiled with hexagons.

**Density heatmap.** 2D-binned color map.

**Marginal distribution.** The univariate distribution along each axis of a
2D plot.

**Violin plot.** Box plot + kernel density. Reveals multimodality.

**Box plot.** 5-number summary (min, Q1, median, Q3, max).

**IQR.** Interquartile range = Q3 − Q1.

**Quadrant chart.** Scatter divided into 4 regions by reference lines.

**Treemap.** Rectangular space-filling chart where area encodes quantity.

**Sankey.** Flow chart where band width encodes quantity.

**Sunburst.** Radial treemap showing hierarchy.

**Slope chart.** Two points connected by a line; emphasizes change between
two time points.

**ECDF.** Empirical cumulative distribution function.

**LISA scatter / cluster map.** Standard local-Moran visualization.

**Folium.** Python wrapper around Leaflet.js for interactive web maps.

**Plotly.** Interactive plotting library; figures export as standalone HTML.

**Parallel coordinates (`go.Parcoords`).** Each row drawn as a polyline
across many features. Reveals cluster *shape*, not just centroid.

**Radar / scatterpolar.** Centroid signatures on a circular axis. Used in
Q24 to make cluster identity kinesthetic.

### Project-specific terms

**System A.** The formal, state-built network: Metro, LRT, BRT, GTFS-published
buses. The "$10B since 2014" infrastructure.

**System B.** The lived, informal network: 1,302 microbus stops, 280 mawaqif,
rider memory.

**Mawfaq / mawaqif (موقف · مواقف).** Arabic for "stopping place" — Cairo's
informal microbus terminals.

**Ghost terminal (Gap G1).** A terminal with zero recorded boarding within a
100 m buffer of its route endpoints. **115 in Phase 1.**

**Empty Return Index (Gap G2).** `1 − (passengers / vehicles)` per terminal.
Threshold ≥ 0.60. **19 critical terminals.**

**Vehicle-Route Mismatch (Gap G3).** Microbuses on routes > 50 km. 75% of
long routes; 44 specific violations.

**Underserved Score (Gap G4).** `population / total_boarding`. Threshold > 0.5.
**79 hexes** at the strict threshold; **381 hexes** in the broader top-quartile
cohort cited in Phase 2.

**Dead-weight terminal.** Q11 zone label: same route count as an Efficient
Hub but **1,870× fewer passengers**.

**Recovery curve.** Q11 chart showing how many ghost terminals "recover" as
the search buffer expands from 100 m to 1 km.

**Catchment.** Population within walking distance of a station. Defined here
as 2 km buffer (with H2 sensitivity at 1 km and 3 km).

**CAGR.** Compound Annual Growth Rate. Computed 2006 → 2017 per district;
used as a feature in K-Means.

**Crowdsourcing frontier (Q19).** Phase 1 stops where informal demand
dominates *and* GTFS coverage is too far away to explain the trip. The places
Masari needs rider-contributed data.

**Bridge connector (Q25).** A line drawn from each informal-heavy Phase 1
stop to its nearest formal node (GTFS / Metro / LRT / BRT). The connectors
**are** the missing product layer.

**Masari (مَسَارِي).** Arabic for "my routes." The product the project's
analysis points to: a route planner that combines System A's published
network with System B's crowdsourced microbus data.

---

*End of report. If anything in this document is unclear, the original notebook
section is named in the header — go straight there.*
