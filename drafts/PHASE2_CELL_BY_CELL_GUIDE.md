# Phase 2 · Cell-by-Cell Guide

A walkthrough of every code cell in both Phase 2 notebooks, in the order they run.
For each cell you get:

- **Why** - the problem the cell solves in one line
- **What** - the technique or library used
- **Output** - what the cell prints, displays, or saves
- **How to read it** - what a reader / TA should take away

---

## Notebook 1 · Scraping, Cleaning, Integration

### Section 01 · Environment setup

#### `cell[5]` · imports
- **Why:** every library used downstream lives in one place so the notebook is easy to audit and reproduce.
- **What:** `pandas`, `geopandas`, `scrapling` (Fetcher / AsyncFetcher / DynamicFetcher for scraping), `rapidfuzz`, `sentence-transformers`, `sklearn`, `plotly`, and one helper line that prints the versions.
- **Output:** one status line, e.g. `pandas 2.2 · geopandas 0.14 · scrapling + sentence-transformers loaded`.
- **How to read it:** if this line prints, the environment is complete. If it raises an `ImportError` the whole notebook stops here.

#### `cell[7]` · paths + constants
- **Why:** fix the three working folders, the CRS conventions, the Cairo bounding box, and the HTTP User-Agent once so every later cell shares them.
- **What:** creates `RawData/`, `CleanedData/`, `Integrated/` if missing, asserts Phase 1 `CleanedData/` exists, sets `CRS_METERS=EPSG:32636` and `CRS_MAP=EPSG:4326`.
- **Output:** one line, e.g. `CRS_METERS=EPSG:32636 · Phase-1 CleanedData accessible`.
- **How to read it:** confirms the folder layout is right. If Phase 1 data is missing, `assert` fires.

---

### Section 02 · S1 · TfC GTFS

#### `cell[11]` · download two GTFS bundles
- **Why:** TfC splits its GTFS feed into two bundles (bus+metro, paratransit). We cache both zips locally so re-runs do not hit GitHub.
- **What:** iterates `GTFS_SETS`, calls `Fetcher.get` per file in each bundle, zips results, writes to `RawData/gtfs_*.zip`. Skip if cached.
- **Output:** one summary line, e.g. `S1 GTFS: 2 bundles cached in RawData`.
- **How to read it:** quick check that both zips are present. Actual file-level detail comes next.

#### `cell[13]` · unzip + load GTFS tables
- **Why:** GTFS is a set of CSVs inside a zip. We need them as pandas tables for the next cell to filter.
- **What:** unzip bus+metro bundle, read each `.txt` into a dict keyed by short name (`gtfs['stops']`, `gtfs['routes']`, etc.).
- **Output:** counts, e.g. `S1 GTFS: 10 tables loaded; stops=1,490 routes=217 trips=736`.
- **How to read it:** gives the reader a sense of scale before we filter.

#### `cell[15]` · bbox filter + reproject + persist
- **Why:** the full GTFS file includes stops outside Cairo. Downstream questions only need Cairo stops, in meters, and only the tables NB2 actually reads.
- **What:** masks `stops` to `CAIRO_BBOX`, builds a `GeoDataFrame`, reprojects to EPSG:32636, writes 5 cleaned CSVs (`gtfs_stops`, `gtfs_routes`, `gtfs_trips`, `gtfs_shapes`, `gtfs_fare_attributes`).
- **Output:** one line, e.g. `S1 cleaned: 1,210 stops in Cairo bbox · reprojected EPSG:32636 · 5 CSVs written`.
- **How to read it:** the first real cleaned artifact lands on disk here.

---

### Section 04 · S3 · Wikipedia metro master list

#### `cell[19]` · fetch + locate station tables
- **Why:** S3 is the single best source for Cairo Metro stations (EN + AR + coords + opening dates all in one table).
- **What:** `Fetcher.get` on `List_of_Cairo_Metro_stations`, parse with `scrapling.parser.Selector`, locate the 3 `wikitable`s whose header includes "Arabic".
- **Output:** one line, e.g. `S3 master list: 3 station tables (one per metro line)`.
- **How to read it:** we expect 3 tables. If the count differs, Wikipedia changed the page layout.

#### `cell[21]` · parse rows → `metro_stations.csv`
- **Why:** turn 89 HTML rows into a structured dataframe we can analyze.
- **What:** strip `[n]` footnotes, convert DMS coords to decimal degrees, parse opening years with `dateutil` (regex fallback), assign a phase label, flag interchanges (station name appears on multiple lines).
- **Output:** one line with 89 stations and the phase list. File: `CleanedData/metro_stations.csv`.
- **How to read it:** this file drives Q13, Q14, Q15, Q22, Q24, H1, the hero map, and the animated expansion.

---

### Section 05 · S4 · Wikipedia LRT

#### `cell[25]` · fetch + parse 3 LRT wikitables
- **Why:** LRT is the system with the highest story weight (H2). We need its stations.
- **What:** `Fetcher.get` on `Cairo_Light_Rail_Transit`, parse tables, flag first table as `is_operational=True`.
- **Output:** `S4 LRT: 20 stations (11 operational)` → `CleanedData/lrt_stations.csv`.
- **How to read it:** 20 stations is the combined list. Coordinates come later, in Section 09.

---

### Section 06 · S5 · BRT via Google Maps

#### `cell[30]` · Google Maps scrape
- **Why:** Cairo BRT opened July 2025 and is not well-indexed in OSM or Wikipedia tables. Google Maps has real user-contributed places we can pull.
- **What:** async scrape with `DynamicFetcher.async_fetch` (playwright-backed). Queries: `BRT` and `الترددي`. Parses `aria-label` + `!3d<lat>!4d<lon>` from each result card, plus canonical-URL redirects.
- **Output:** one line, e.g. `S5 BRT scrape: 13 raw rows from 2 queries (wider Ring Road viewport)`.
- **How to read it:** 13 raw rows is before dedup. We expect around 10 unique real stations after the next two cells.

#### `cell[33]` · franko transliteration (uroman)
- **Why:** Arabic station names need to match their English-form duplicates. We need letter-for-letter phonetic Latin, not semantic translation.
- **What:** installs `uroman` if missing, runs every Arabic station name through the romanizer (e.g. `المرج` → `almrj`).
- **Output:** a sample Arabic → franko mapping.
- **How to read it:** this is the "AI-friendly" dedup key. It feeds the fuzzy match in the next cell.

#### `cell[35]` · three-tier dedup → `brt_stations.csv`
- **Why:** the same station often appears multiple times across queries with slightly different coords and names.
- **What:** dedup rule - spatial <80 m = always merge, 80 m to 1.2 km + shared franko core = same station, >1.2 km even if names match = different station.
- **Output:** `S5 BRT dedup: 13 raw → 10 unique stations (TfC Phase 1 plan: 14)`.
- **How to read it:** 10 of 14 TfC-planned stations were locatable from Google Maps today. The caveats box in NB2 admits this gap.

---

### Section 07 · S6 · citypopulation.de

#### `cell[39]` · fetch + walk the admin table
- **Why:** population counts per district over 4 years (1996, 2006, 2017, 2023) — the demographic half of every per-district question.
- **What:** `Fetcher.get` on `/egypt/admin/`, parse first table with `scrapling.Selector`, walk rows linearly carrying the governorate context forward, filter to Greater Cairo.
- **Output:** `S6 districts: 408 rows Egypt-wide · 68 Greater Cairo districts`.
- **How to read it:** 68 districts is our universe for Q16, Q17, Q22, Q24, H1.

#### `cell[41]` · wide → long + CAGR
- **Why:** a district-year long table is easier to query (`year=2017`), and a CAGR column lets Q16 rank by growth.
- **What:** `pd.melt`, add CAGR 2006 → 2017, save two files (long form + wide form).
- **Output:** `S6 cleaned: districts.csv (272 district-year rows) + districts_wide.csv (68 districts)`.
- **How to read it:** the `cagr_2006_2017` column is what Q16 sorts by. Long form drives any time-sliced question.

#### `cell[43]` · Nominatim geocoding of per-district centroids
- **Why:** earlier versions used one gov centroid for all districts - which collapsed every per-district feature to 3 unique values. We upgrade to real centroids.
- **What:** per district, strip diacritics + alias map (`Dokki`, `Agouza`, `Sheikh Zayed`, etc.), query Nominatim with a Greater-Cairo bbox gate. Fallback to gov centroid if not found. Cache to `RawData/nominatim_districts.json`.
- **Output:** `Geocoded 68 districts · 42 via Nominatim (62%) · 26 gov-centroid fallback`.
- **How to read it:** 37 unique centroids vs 3 before. Q22, Q24, H1 all gain real per-district variation from this upgrade.

---

### Section 08 · S7 · Vehicle counts

#### `cell[48]` · Wikipedia 2023 national vehicle total
- **Why:** the only source with a current national total we can scrape.
- **What:** `Fetcher.get` on `List_of_countries_by_vehicles_per_capita`, parse the big wikitable, pick Egypt's row.
- **Output:** `S7 Egypt 2023: 9,950,000 vehicles · 87/1k people · pop 114,535,772`.
- **How to read it:** these 3 numbers (national total, per-capita, pop) drive the governorate apportionment in cell 52.

#### `cell[50]` · World Bank API for historical per-capita
- **Why:** Wikipedia gives one year, we want a time series. WB has `IS.VEH.NVEH.P3` and `IS.VEH.PCAR.P3`.
- **What:** `Fetcher.get` on the WB JSON endpoint, cache locally, flatten observations.
- **Output:** `S7 WB historical: 13 observations across 2 indicators`.
- **How to read it:** sparse (6-7 years) but still useful for long-run trends.

#### `cell[52]` · apportion to governorates
- **Why:** we need vehicle counts per governorate but the national total is the only thing published. Best available method: proportional to population share.
- **What:** for each (governorate, year, indicator), `national_count × gov_pop_share`. Document the method in the `method` column.
- **Output:** `S7 apportioned: N rows across 3 Greater Cairo governorates` → `CleanedData/vehicles_by_governorate.csv`.
- **How to read it:** every row declares its source + method, so a grader can audit the derivation.

---

### Section 09 · S8 · OSM + LRT coord sourcing

#### `cell[56]` · OSM Overpass transport features
- **Why:** independent cross-verification layer. Does OSM agree with Wikipedia's metro/LRT coords?
- **What:** `Fetcher.post` to Overpass API with an Overpass QL query for `public_transport=station`, `railway=station`, `subway_entrance`, `bus_stop`, `bus_station` inside the Cairo bbox. Returns named nodes in EPSG:32636.
- **Output:** `S8 OSM: 235 named transport nodes (cross-verification layer)` → `CleanedData/osm_features.geojson`.
- **How to read it:** this layer is also used for the hero map OSM overlay.

#### `cell[59]` · LRT step A · per-station Overpass
- **Why:** S4 LRT had no coordinates. Step one to fix that: ask OSM per station name.
- **What:** for each LRT station, POST an Overpass `name~` regex query. Rank results by transport tag quality, keep the best.
- **Output:** `LRT step A (Overpass): 9 / 20 stations located`.
- **How to read it:** 9 is honest. The remaining 11 are either under-construction or not yet mapped in OSM.

#### `cell[61]` · LRT step B · Google Maps fallback
- **Why:** pick up what Overpass missed.
- **What:** async Google Maps search per missing station, two query variants (`<name> Cairo LRT`, `<name> Cairo`). Chrome-label blocklist (`Sign in`, `Menu`, etc.).
- **Output:** `LRT step B (Google Maps fallback): +7 stations located · total 16 / 20`.
- **How to read it:** we end at 16 of 20 LRT coords. Caveats box in NB2 names this limit.

---

### Section 10 · data quality audit

#### `cell[65]` · per-source null audit
- **Why:** every grader wants to know how clean the data is.
- **What:** load every file in `CleanedData/`, count nulls per column, write `null_audit.csv`.
- **Output:** console table per source: rows, columns, total nulls.
- **How to read it:** small numbers good, zeros best. BRT has some nulls where Google Maps didn't supply fields (still fine).

#### `cell[67]` · null-audit chart
- **Why:** visual is faster to scan than a table.
- **What:** Plotly grouped bar, null percentage per column per source, dark theme.
- **Output:** interactive chart.
- **How to read it:** any bar near 100% is a problem column. Most bars are near zero.

---

### Section 11 · integration pipeline

#### `cell[72]` · load terminals + build GeoDataFrames
- **Why:** set up inputs for the 4-stage matching pipeline.
- **What:** reads Phase 1 terminals (WKT strings → Shapely), builds `metro_g`, `lrt_g`, `brt_g`, `osm` GeoDataFrames with per-row `source` tags.
- **Output:** `Integration inputs · Phase-1 terminals: 280 · metro: 89 · lrt: 16 · brt: 10 · osm: 235`.
- **How to read it:** these are the universe sizes for each stage.

#### `cell[75]` · Stage 1 · KNN spatial matching
- **Why:** the cheapest first-pass "is this scraped station near an existing Phase 1 terminal?" test.
- **What:** `sklearn.neighbors.NearestNeighbors` on terminal centroids. For each scraped station returns its nearest terminal + distance in meters.
- **Output:** `Stage 1 · KNN: N pairs · median dist Xm · (Y within 200m)`.
- **How to read it:** pairs within 200 m are the easy wins. Pairs >2 km are flagged for Stage 3/4.

#### `cell[78]` · Stage 2 · OSM cross-verify
- **Why:** sanity check Wikipedia coordinates against OSM.
- **What:** nearest OSM feature for each scraped station. Flag any >50 m discrepancy.
- **Output:** `Stage 2 · OSM verify: N pairs · X within 50m · Y flagged`.
- **How to read it:** flags list is the audit sheet - a human should eyeball these before trusting them.

#### `cell[81]` · Stage 3 · RapidFuzz token_sort
- **Why:** names differ by punctuation, transliteration spelling. Fast fuzzy match handles English-only variants.
- **What:** `process.extractOne` with `fuzz.token_sort_ratio` at τ=88.
- **Output:** `Stage 3 · fuzzy: N pairs · X matched at τ=88`.
- **How to read it:** this catches "Al-Shohadaa" vs "Al Shohada". It cannot bridge Arabic ↔ English - that's Stage 4.

#### `cell[84]` · Stage 4 · multilingual SBERT (the AI technique)
- **Why:** Arabic script and Latin script share zero characters. Fuzzy match fails on `Heliopolis` vs `مصر الجديدة`. Sentence embeddings project them into the same space.
- **What:** `paraphrase-multilingual-MiniLM-L12-v2` (384-dim), encode each concatenated `station_en + station_ar`, cosine similarity matrix, accept at τ=0.75 AND spatial distance <2 km (both gates required after the audit).
- **Output:** `Stage 4 · SBERT: N pairs · X ≥0.75 cosine · Y upgraded beyond fuzzy`.
- **How to read it:** the upgraded count is where the AI technique adds real value over fuzzy.

#### `cell[86]` · gold-set validation
- **Why:** we need to know if Stage 3 or Stage 4 is actually right. A tiny manually curated set is the truth.
- **What:** load 5-pair `gold_set.csv`, check fuzzy vs semantic accuracy per `match_type`.
- **Output:** accuracy per technique.
- **How to read it:** 5 pairs is a sanity check, not validation. The caveats box says this honestly.

#### `cell[89]` · integration Sankey
- **Why:** one image that shows how much data survives each stage.
- **What:** per source (metro, LRT, BRT, OSM), count `n_in → Stage 1 near → Stage 3 fuzzy → Stage 4 semantic → unmatched`. Plot as `plotly.graph_objects.Sankey`.
- **Output:** Sankey diagram.
- **How to read it:** thick flows are high-confidence matches. Right-side "Unmatched" = residual data-loss we accept.

#### `cell[92]` · persist integration outputs
- **Why:** NB2 depends on two files.
- **What:** write `Integrated/matched_pairs.csv` (one row per scraped ↔ terminal pair with fuzzy + semantic scores) and `Integrated/Phase2_integrated.geoparquet` (all features in one GeoDataFrame).
- **Output:** two file paths with row counts.
- **How to read it:** these are the NB1 → NB2 handoff artifacts.

---

### Section 13 · output manifest

#### `cell[96]` · file manifest
- **Why:** show every artifact produced so a grader can see the deliverables at a glance.
- **What:** walk `CleanedData/` and `Integrated/`, count rows per file, save as `Integrated/manifest.csv`.
- **Output:** printed table.
- **How to read it:** quick reference. Each row is a deliverable.

#### `cell[98]` · final gate
- **Why:** stops NB2 from running if any required file is missing.
- **What:** `assert` that 16 required paths exist.
- **Output:** `✓ All 16 required outputs present - Notebook 2 can run`.
- **How to read it:** if the assert fails, re-run the failing section in NB1 before touching NB2.

---

## Notebook 2 · Analysis, Questions, Hypotheses

### Section 00 · environment

#### `cell[5]` · imports
- **Why:** same idea as NB1 - one import cell for everything.
- **What:** adds `scipy.stats`, `sklearn.cluster.KMeans`, `libpysal.weights.KNN`, `esda.moran.Moran`, `folium`, `plotly`, and pulls the `show_df` / `show_metrics` / `show_note` utilities from `drafts/phase2_utils.py`.
- **Output:** one line confirming versions loaded.
- **How to read it:** if this line runs, every downstream cell can use the styled-table helpers.

---

### Section 01 · palette + Cliff's δ

#### `cell[8]` · palette + helpers
- **Why:** define one palette so all charts share colors with NB1 and Phase 1. Also define `cliffs_delta`, a non-parametric effect size we reuse in H2 and H3.
- **What:** color constants (`BG`, `TXT`, `ACCENT`), Plotly template, `cliffs_delta(x, y)` function.
- **Output:** `palette + cliffs_delta ready`.
- **How to read it:** reference colors via `BG` / `TXT` throughout the notebook.

---

### Section 02 · data load

#### `cell[12]` · load every NB1 output + Phase 1 files
- **Why:** bring all data into one namespace. Downstream cells should never re-read from disk.
- **What:** reads 10 cleaned CSVs + 1 geoparquet + 3 Phase 1 CSVs, prints every shape. Also builds `p1_pop_gdf` once here to avoid the 5 rebuilds downstream.
- **Output:** list of dataset shapes, e.g. `metro (89, 10)`, `districts_w (68, 12)`.
- **How to read it:** confirms every file loaded. If a shape is wrong, NB1 needs re-running.

#### `cell[14]` · CRS + non-null assertions
- **Why:** catch silent regressions at load time.
- **What:** `assert osm.crs == 'EPSG:32636'`, assert critical columns have no nulls, assert non-empty.
- **Output:** `✓ CRS checks passed / ✓ non-null checks passed`.
- **How to read it:** if the asserts fire, something upstream changed schema.

---

### Section 03 · Phase 1 recap

#### `cell[19]` · load G1-G4 gap counts
- **Why:** Phase 2 is about the 4 Phase 1 gaps. Reader needs their magnitude before we continue.
- **What:** reload `merged_G_underused_terminals.csv`, `merged_D_terminal_flow_ratios.csv`, `q12_vehicle_type_route_length.csv`, `q9_underserved.csv`, compute G1/G2/G3/G4 counts, render with `show_df`.
- **Output:** styled table with 4 rows: `G1=115, G2=19, G3=44, G4=381`.
- **How to read it:** these 4 numbers are Phase 2's target. Every later question asks whether new infrastructure reached any of them.

#### `cell[21]` · 4-panel gap dashboard
- **Why:** the 4 numbers also deserve a visual.
- **What:** 2×2 Plotly `Indicator` grid, one big number per gap with color.
- **Output:** dashboard.
- **How to read it:** use this as the first thing you show a reader. Sets up every later insight.

---

### Section 04 · hero two-Cairos map

#### `cell[26]` · Folium hero map
- **Why:** the project's central image. Shows System A (formal) and System B (informal) co-existing on one map.
- **What:** Folium with 2 FeatureGroups: `Formal new modes` (metro / LRT / BRT) colored by line, `Phase-1 informal terminals` in coral. 6-item legend HTML embedded.
- **Output:** interactive Folium map, saved to `two_cairos_map.html`.
- **How to read it:** overlap is visible but operationally disjoint. That's the story.

---

### Section 05 · Q13 metro density

#### `cell[31]` · build metro_pts with nearby population
- **Why:** to ask "did metro go where people are?" we need each station + nearby density.
- **What:** project metro to EPSG:32636, take 5-nearest Phase 1 population hexes per station, attach their mean population.
- **Output:** sample with `station_en`, `opening_year`, `hex_pop_2018`.
- **How to read it:** ready for correlation in the next cell.

#### `cell[33]` · Spearman per line + permutation test
- **Why:** test whether OPENING YEAR is correlated with LOCAL POPULATION within each line.
- **What:** Spearman ρ per line (non-parametric because distributions are skewed), 2000-permutation test on Line 3 vs Line 1 mean density.
- **Output:** styled table with ρ, p, n, mean_pop per line + a permutation p-value.
- **How to read it:** Line 3 shows ρ=0.45 p=0.007 - only the newest line actually reaches denser areas.

#### `cell[35]` · 3-panel scatter
- **Why:** show the correlation visually.
- **What:** `make_subplots(1,3)` - one subplot per line, annotate each with its ρ / p.
- **Output:** 3 scatter panels.
- **How to read it:** look for upward slope on Line 3. Lines 1 and 2 show flat clouds.

---

### Section 06 · Q14 ghost terminals vs new metro

#### `cell[40]` · find ghost terminals + post-2014 metro
- **Why:** test whether new metro reached Phase 1's 115 underused terminals.
- **What:** filter `merged_G_underused` to `Underused==True`, attach geometries from `merged_B`, filter metro to Line 3 post-2014.
- **Output:** counts (115 ghosts, 27 new metro).
- **How to read it:** sets up the distance computation in the next cell.

#### `cell[42]` · KNN + distance buckets
- **Why:** the answer is a distance distribution.
- **What:** nearest new-metro distance per ghost terminal, binned into `<500m`, `500-1000m`, `1-2km`, `2-5km`, `5km+`. Summary: `reached` (<1km) vs `stranded` (>2km).
- **Output:** `show_df` of bucket counts + `show_metrics` summary.
- **How to read it:** 84% of ghosts are >2 km from any new-metro station. The $10 B missed the Phase 1 pain points.

#### `cell[44]` · distance-bucket bar chart
- **Why:** visualize the distribution.
- **What:** Plotly horizontal bar with bucket colors.
- **Output:** chart.
- **How to read it:** the `5 km+` bar is the tallest. That's the story in one image.

---

### Section 07 · Q15 metro km over time

#### `cell[49]` · build timeline
- **Why:** compute cumulative metro km per year using station counts × average stop spacing.
- **What:** sort stations by opening year, cumulative count × 1.2 km per stop.
- **Output:** 19-row yearly dataframe.
- **How to read it:** intermediate data. The chart comes next.

#### `cell[51]` · cumulative metro km chart
- **Why:** show metro growth 1987 → 2024 with phase-opening markers.
- **What:** one-series area chart + vertical dashed lines at key phase openings. (Simpler than the earlier dual-axis version which drew the same shape twice.)
- **Output:** chart.
- **How to read it:** metro grew 6 × from 17 km to 107 km. Ghost-terminal count held at 115 over the same period.

---

### Section 08 · Q16 fast-growing districts + coverage

#### `cell[56]` · compute per-district coverage
- **Why:** answer the real question - did the fastest growers get any new infrastructure?
- **What:** for each top-15 CAGR district, count new-mode stations within 3 km of its Nominatim centroid.
- **Output:** `show_df` of top 15 + `show_metrics` with coverage summary.
- **How to read it:** **New Cairo 1 (+15% CAGR) and 6th of October (+13%) both have 0 new-mode stations within 3 km**. Fast growth with zero coverage is Masari's forward pipeline.

#### `cell[58]` · CAGR × coverage scatter
- **Why:** one image that answers "growth without coverage".
- **What:** 15 dots, x=CAGR, y=n_new_modes, color-coded (coral=0 coverage, yellow=<5, green=≥5).
- **Output:** scatter.
- **How to read it:** dots clustered along y=0 are the gap.

---

### Section 09 · Q17 density × underservedness

#### `cell[63]` · correlation of population × underserved score
- **Why:** test if density is just a proxy for underservedness or if the two are orthogonal.
- **What:** Spearman ρ on Phase-1 Q9 hexes (1,525 rows). Also count hexes in top quartile of both (density AND underserved) - Masari's hex-level target.
- **Output:** `Hex obs: 1525 · Spearman ρ = 0.548 · p < 1e-120 · 150 hexes dense AND underserved`.
- **How to read it:** 150 dense-and-underserved hexes is roughly 10% of Greater Cairo. That's the addressable market at hex resolution.

#### `cell[65]` · scatter + marginal histograms
- **Why:** show the distribution - not just the correlation number.
- **What:** `make_subplots` with top + right marginal histograms, a quadrant highlight showing Masari's primary market.
- **Output:** 2D scatter with marginals.
- **How to read it:** the coral quadrant in the upper-right is where Layla lives.

---

### Section 10 · Q18 informal share + Q18b gap-coverage matrix

#### `cell[70]` · load Q4 formal vs informal + join to hex population
- **Why:** compute informal modal share per stop, tie it to local density.
- **What:** load `q4_formal_vs_informal.csv`, spatial-join to nearest hex, add `hex_pop`.
- **Output:** `Stops with pop+share: 1,144 · Mean informal share: 0.47 · Spearman ρ = 0.025 · p=0.40`.
- **How to read it:** informal transport is not density-targeted. 47% informal share is the city-wide average.

#### `cell[72]` · density-tier scatter with regression
- **Why:** show the (flat) relationship.
- **What:** Plotly scatter colored by density quartile + OLS regression line.
- **Output:** scatter.
- **How to read it:** regression line is nearly horizontal - microbus is everywhere.

#### `cell[74]` · Q18b · 3-modes × 4-gaps coverage matrix
- **Why:** the single clearest answer to Phase 2's thesis question.
- **What:** for each (mode, gap) pair count what % of gap instances are within 2 km of a mode station. Render as a Plotly heatmap.
- **Output:** styled table + 3×4 heatmap with %.
- **How to read it:** best cell is 25% (LRT and BRT on G3). Every other cell <16%. After $10 B of new rail, every Phase-1 gap still has 75-100% uncovered.

---

### Section 11 · Q19 GTFS coverage per agency

#### `cell[80]` · load and compare the two GTFS bundles
- **Why:** show the formal-vs-informal data asymmetry at the source.
- **What:** load both zip bundles separately, count routes per agency in each.
- **Output:** `show_df` with `bus_metro_routes` and `paratransit_routes` per agency.
- **How to read it:** National Authority for Tunnels (metro) has 3 formal routes. Paratransit has 186. A 6:1 data gap between formal and informal before analysis even begins.

#### `cell[82]` · stacked bar per agency
- **Why:** visualize the asymmetry.
- **What:** Plotly stacked bar: bus/metro (blue) + paratransit (coral) per agency.
- **Output:** chart.
- **How to read it:** one agency (NAT) is purely formal, everyone else is purely paratransit.

---

### Section 12 · Q20 BRT corridor × informal demand

#### `cell[87]` · buffer each BRT station, count Phase 1 informal stops
- **Why:** did BRT formalize real demand or build into an empty corridor?
- **What:** 500 m buffer per BRT station (using `display_name` that prefers English but falls back to Arabic so Arabic-only stations aren't dropped). Spatial-join Phase 1 informal stops.
- **Output:** `show_df` with one row per BRT station and its `informal_daily_sum`.
- **How to read it:** El Marg has 14,726 informal daily boardings in its buffer. Ibrahim Orabi has 0. The northern 8 BRT stations are on top of real demand; the southern 4 are greenfield.

#### `cell[89]` · horizontal ranked bar
- **Why:** make the corridor demand visible.
- **What:** horizontal bar sorted by `informal_daily_sum`.
- **Output:** chart.
- **How to read it:** long bars = corridors that already had the demand. Short bars = stations Masari routes commuters INTO rather than around.

---

### Section 13 · Q21 fare per km

#### `cell[94]` · compute fare/km per route per vehicle type
- **Why:** is informal transport more expensive per km than formal? The audit of the affordability claim.
- **What:** merge `gtfs_fare_attributes.csv` (formal fares) with Phase 1 `q12_vehicle_type_route_length.csv` (informal lengths + typical fares), compute fare/km per route, group by `source_bucket` + `vehicle_type`.
- **Output:** `show_df` summary - median fare/km per mode.
- **How to read it:** Formal metro: 0.25 EGP/km. Informal microbus: 0.62 EGP/km. People pay 2.5x more for the informal option because the metro doesn't reach them. Coverage, not price.

#### `cell[96]` · box plot formal vs informal
- **Why:** show the distributions, not just medians.
- **What:** box plot per vehicle type, colored by formal/informal.
- **Output:** chart.
- **How to read it:** informal boxes sit above formal boxes. Microbus has the longest whisker - prices are negotiated, not fixed.

---

### Section 14 · Q22 coverage residual per district

#### `cell[101]` · OLS regression on real Nominatim centroids
- **Why:** which districts get LESS metro than their population predicts? That's the residual ranking.
- **What:** for each district, count metro stations within 3 km of its real centroid. OLS fit population → station count. Residual = observed - predicted.
- **Output:** `show_metrics` with slope / intercept / p25-p75 residual + `show_df` of top-10 most-negative residuals.
- **How to read it:** Al-Duqqi, Sheikh Zayed, 6th of October, Al-Hawamidiya are the worst-served dense districts. Masari's priority list.

#### `cell[103]` · residual scatter
- **Why:** visual form of the residual distribution.
- **What:** scatter colored by residual sign (coral = under-served, teal = over-served).
- **Output:** scatter.
- **How to read it:** coral dots in the top-right are the problem districts.

#### `cell[105]` · top-15 under-served bar
- **Why:** clean ranked view for the deck.
- **What:** horizontal bar of the 15 most-negative residuals.
- **Output:** chart.
- **How to read it:** this is the ranked Masari pipeline geography.

---

### Section 15 · Q23 Adly Mansour convergence

#### `cell[111]` · count modes within 2.5 km buffer
- **Why:** how many transport modes actually meet at Adly Mansour?
- **What:** 2.5 km buffer (a reasonable walking / microbus hop). Count formal stations in `integrated` per source_label + Phase 1 informal terminals within the buffer.
- **Output:** `show_metrics` with the 4 mode counts + a styled table of the informal terminals.
- **How to read it:** 4 modes converge - Metro L3 + LRT + BRT + Phase-1 informal (Al-Salam, Awwel Gamal). Real intermodal node.

#### `cell[113]` · Folium zoom map
- **Why:** give the reader a geographic picture of the convergence.
- **What:** Folium zoom at z=13 with 4-mode legend (blue metro, orange LRT, purple BRT, coral informal).
- **Output:** `adly_mansour_zoom.html`.
- **How to read it:** all 4 modes are plotted within the dashed 2.5 km circle.

#### `cell[115]` · density percentile vs random sample
- **Why:** is Adly Mansour actually special or average?
- **What:** compare its station count to 150 random 2.5 km cluster samples from across Cairo.
- **Output:** histogram with a red line at Adly Mansour's count + percentile annotation.
- **How to read it:** 17th percentile - Adly Mansour is actually less station-dense than 83% of random Cairo clusters. It's a political convergence (4 modes picked to meet there), not a demand convergence.

---

### Section 16 · Q24 K-Means segmentation (AI Technique 2)

#### `cell[122]` · build feature matrix on real centroids
- **Why:** per-district features drive the clustering. Proxy centroids would collapse the clustering.
- **What:** features per district - `log(pop_2023)`, `cagr`, `n_new_modes`, `n_informal_stops_within_3km`, `is_cairo` dummy. Uses real Nominatim centroids.
- **Output:** `show_metrics` with matrix shape + `show_df` of per-feature stats.
- **How to read it:** 37 unique centroids → meaningful per-district variation (vs 3 before).

#### `cell[124]` · elbow + silhouette
- **Why:** pick a k.
- **What:** fit KMeans for k=2..8, plot inertia + silhouette.
- **Output:** 2-panel chart + printed k recommendation.
- **How to read it:** k=2 maximizes silhouette. We force k=4 for policy granularity (4 market segments, not 2).

#### `cell[126]` · stability check (ARI) + profile clusters
- **Why:** is the clustering stable across random seeds, and what are the clusters like?
- **What:** run KMeans 5 times with different seeds, compute Adjusted Rand Index. Profile the 4 clusters.
- **Output:** ARI list + per-cluster median profile.
- **How to read it:** mean ARI should be >0.6 for stability. Per-cluster profile names the segments.

#### `cell[128]` · cluster name + overview chart
- **Why:** turn raw cluster IDs into human labels.
- **What:** label clusters as `Hot Growth / Established Core / Peripheral Growth / Low-Activity Outskirts` based on profile signs. 2-panel chart (cluster size + feature z-score heatmap).
- **Output:** labeled cluster chart.
- **How to read it:** compare clusters row-by-row. Masari's target combines Established Core + Peripheral Growth = ~18 M residents.

#### `cell[132]` · parallel coordinates
- **Why:** see where each district sits along every feature.
- **What:** Plotly parallel_coordinates colored by cluster.
- **Output:** interactive parallel-coordinates plot.
- **How to read it:** traces from different clusters follow different profiles. Good for TAs who want to inspect individual districts.

#### `cell[136]` · radar per cluster
- **Why:** another way to compare profiles.
- **What:** one radar polygon per cluster with normalized feature values.
- **Output:** radar chart.
- **How to read it:** overlapping polygons show where clusters are distinct.

---

### Section 17 · H1 coverage-need + Moran's I (AI Technique 3)

#### `cell[141]` · Kruskal-Wallis + pairwise Mann-Whitney
- **Why:** formally test whether dense districts get fewer stations per capita.
- **What:** tertile-split by population, Kruskal-Wallis (non-parametric ANOVA), pairwise Mann-Whitney with Bonferroni, Cliff's δ per pair, epsilon² for the overall test.
- **Output:** `show_metrics` overall + `show_df` tertile stats + `show_df` pairwise Bonferroni.
- **How to read it:** ε²=0.83 (large), all Cliff's δ ≥ 0.94. High-density districts get 12x fewer stations per 100k residents. Decisive statistical evidence.

#### `cell[144]` · build KNN-5 spatial weights
- **Why:** Moran's I needs a spatial weights graph.
- **What:** `libpysal.weights.KNN` with k=5 on district centroids.
- **Output:** a weights object.
- **How to read it:** intermediate step. Matters only for Moran's I next.

#### `cell[146]` · Global + Local Moran's I
- **Why:** is the mismatch clustered geographically or random?
- **What:** `esda.Moran` (global I with 999 permutations) + `Moran_Local` (LISA classification HH/LL/HL/LH per district).
- **Output:** 2-panel chart: tertile box plot (left) + LISA cluster map (right).
- **How to read it:** global I=0.16 p=0.004 (clustered). 21 LL clusters = contiguous bands of low-coverage districts. That's the rollout geography for Masari.

---

### Section 18 · H2 LRT catchment deficit

#### `cell[151]` · compute 2 km catchment population
- **Why:** does the LRT serve actual people?
- **What:** for each LRT station and each post-2012 metro station, spatial-join to Phase 1 hexes within 2 km, sum `Population_2018`. Mann-Whitney U + Cliff's δ.
- **Output:** `show_metrics` with LRT vs metro medians + test statistics.
- **How to read it:** **LRT median = 0. Metro median = 634,333. Cliff's δ = -0.993.** The LRT's corridor is effectively empty land. ARIJ's "empty trains" finding quantified.

#### `cell[153]` · box plot
- **Why:** show both distributions on one axis.
- **What:** Plotly boxes side by side.
- **Output:** chart.
- **How to read it:** LRT box hugs zero. Metro box sits way above.

#### `cell[155]` · per-station sorted bar
- **Why:** the box plot hides individual stations.
- **What:** horizontal bar, one row per station (LRT coral, metro blue), sorted by catchment.
- **Output:** chart.
- **How to read it:** every LRT station sits below every metro station. The gap is structural, not a few outliers.

---

### Section 19 · H3 BRT corridor match

#### `cell[161]` · corridor demand vs matched controls
- **Why:** did BRT formalize real demand (unlike the LRT)?
- **What:** 500 m buffer per BRT station, sum Phase 1 informal boardings inside. Random non-BRT controls sampled from the same bbox. Mann-Whitney U + Cliff's δ.
- **Output:** `show_metrics` with BRT median vs control median + p-value + δ.
- **How to read it:** **BRT median = 1,576 informal daily boardings. Control median = 0. Cliff's δ = +0.83.** BRT WAS put on real demand corridors. The one positive planning finding in Phase 2.

#### `cell[163]` · violin plot
- **Why:** show the distribution shape, not just the median.
- **What:** Plotly violin with both groups overlaid.
- **Output:** chart.
- **How to read it:** BRT violin is shifted right of control. Clean visual effect.

---

### Section 20 · headline coverage-need map

#### `cell[167]` · final synthesis Folium map
- **Why:** the deck's headline visual. Everything Phase 2 learned in one image.
- **What:** Folium with district centroids colored by K-Means cluster + new-mode station overlay + Adly Mansour (planning axis) and Imbaba (demand axis) marker.
- **Output:** `headline_coverage_need_map.html`.
- **How to read it:** eastward chain of stations = planning axis. Western and southern clusters = demand axis. They don't overlap. That's the headline.

---

### Section 21 · animated metro expansion

#### `cell[171]` · animated scatter_mapbox 1987 → 2026
- **Why:** temporal story of where the state chose to invest.
- **What:** Plotly `scatter_mapbox` with `animation_frame='frame_year'`, cumulative stations by year.
- **Output:** animated map.
- **How to read it:** watch the eastward extension through 2014, 2019, 2022, 2024. Line 3 Phases finally reach Imbaba in the last few frames.

---

### Section 22 · Masari market sizing

#### `cell[176]` · population per cluster
- **Why:** how many residents Masari can address.
- **What:** sum `pop_2023` per K-Means cluster, identify primary-market cluster (highest informal-to-station gap).
- **Output:** `show_df` with cluster populations + primary share.
- **How to read it:** primary-market cluster has N residents; that's Masari's addressable universe.

#### `cell[178]` · horizontal bar highlight
- **Why:** visual of the market sizing.
- **What:** horizontal bar with primary cluster in coral, others in blue.
- **Output:** chart.
- **How to read it:** the coral bar is Masari's first market.

#### `cell[182]` · sunburst cluster hierarchy
- **Why:** a second view of the cluster breakdown.
- **What:** Plotly sunburst - outer ring = individual districts, inner ring = cluster.
- **Output:** sunburst chart.
- **How to read it:** drill into a cluster to see its districts.

---

## How to use this guide with a TA

1. **Walk top to bottom.** The cells run in order; the guide does too. Open it beside the notebook.
2. **For each cell the 4-item check is enough for a viva.** Why → what → output → how to read.
3. **When asked "why this method?":** the **Why** line answers it in one sentence.
4. **When asked "what does this chart show?":** the **How to read it** line answers.
5. **When asked "what if this fails?":** if it's a scraping cell, the cached RawData file is the audit trail. If it's an integration cell, Stage 1 KNN is the first fallback. If it's an analysis cell, the caveats box in NB2 names the limits.
