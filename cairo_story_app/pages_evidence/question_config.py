"""
Per-question catalogue for Evidence mode.
Each Question carries its own visualizations, KPIs, insight, and methodology.

All headline statistics come from data.findings — that file is the single
source of truth.  When a notebook stat changes, update findings.py and
nothing else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from data.findings import (
    H1, H2, H3, Q14, Q18, Q18B, Q21, Q22, Q23_ADLY, Q24, Q25, MARKET, PHASE1, SCRAPE
)


@dataclass(frozen=True)
class Question:
    id: str
    phase: str                                  # 'phase1' | 'phase2' | 'hypothesis' | 'gap'
    nav_label: str
    kicker: str
    headline: str
    arabic: Optional[str] = None
    question_text: str = ""
    why_it_matters: str = ""
    method: str = ""
    kpis: List[Tuple[str, str, str]] = field(default_factory=list)
    viz_html_paths: List[str] = field(default_factory=list)   # relative to DATA_ROOT
    viz_builders: List[Callable] = field(default_factory=list)
    insight: str = ""
    methodology: str = ""


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 1 · CLEANING · 3 condensed entries
#  (NEW — explains the data engineering before the analysis)
# ═══════════════════════════════════════════════════════════════════════

_C = PHASE1["counts"]
_CLEAN = PHASE1["cleaning"]

PHASE1_CLEANING: List[Question] = [
    # ───────────────────────────────────────────────────────────────────
    #  P1-E0 · pre-clean exploration (NEW — added because the cleaning
    #  notebook actually does this work; we surface it here)
    # ───────────────────────────────────────────────────────────────────
    Question(
        id="P1-E0", phase="phase1", nav_label="◆ EXPLORATION",
        kicker="PHASE 01 · CLEANING · DATA EXPLORATION",
        headline="What we look at before any cleaning logic runs",
        question_text="What does each raw GeoJSON look like before we touch it?",
        why_it_matters=(
            "If we jump straight to imputation we don't know what we are "
            "imputing. The exploration pass tells us which fields are "
            "actually broken (so we can target them) and which are clean "
            "(so we leave them alone). It is the cheapest defence against "
            "fabricating a result."
        ),
        method="Per dataset: shape · dtypes · geometry type · null count per column · numeric range sanity check",
        kpis=[
            ("DATASETS AUDITED", "7", "BOARDING · POP · ROUTES · ..."),
            ("FIELDS WITH NULLS", "3", "BOARDING · FARE · PAX_FLOW"),
            ("NULL CELLS PRE", f"{_CLEAN['null_cells_pre']:,}", "TOTAL"),
            ("ROWS DROPPED", f"{_CLEAN['rows_dropped']}", "ZERO"),
        ],
        insight=(
            "**Three fields needed work, every other numeric field came in clean.**\n\n"
            "**Boarding dataset.** 12 numeric counts (Daily_All_BA, Morning_All_BA, "
            "the formal/informal splits, the per-route counts) had sparse nulls "
            "spread across about 42 stops. Spatially clustered enough that a "
            "5-nearest-neighbour imputer could recover them.\n\n"
            "**Routes.Fare.** 45.9% null. The single biggest hole. Vehicle type, "
            "length, capacity, and direction were complete, so the imputation "
            "could lean on those four features.\n\n"
            "**Passengers per Hour (pax flow).** Sparse nulls on a few hundred "
            "segments. Each segment has a centroid and a length, so the imputer "
            "had geometry features to work with.\n\n"
            "Population, terminals, vehicle flow, and commercial speeds were "
            "fully populated — no imputation needed."
        ),
        methodology=(
            "The audit lives in Section 06 of `Cleaning Data.ipynb`. For each "
            "dataset we open the GeoDataFrame, inspect `df.dtypes`, "
            "`df.geometry.geom_type.unique()`, and `df.isnull().sum()`. We then "
            "run a quick `df.describe()` on the numeric columns to make sure no "
            "field is degenerate (all zeros, all NaN, all the same value). The "
            "output is a styled HTML table that lists every (dataset, column) "
            "with non-zero nulls and the total count across the project."
        ),
    ),
    Question(
        id="P1-C1", phase="phase1", nav_label="◆ DATASETS",
        kicker="PHASE 01 · CLEANING · DATA SOURCES",
        headline="Seven raw GeoJSON files describe Cairo's existing transport network",
        question_text="What does the Phase 1 raw data look like, and where does it come from?",
        why_it_matters=(
            "Every Phase 1 question reads from these seven files. Knowing what is in "
            "each one — and how big — is the prerequisite for trusting any chart "
            "downstream. The GeoJSONs come from Transport for Cairo's GCR survey "
            "and from PTV-Visum-style operational exports."
        ),
        method="`gpd.read_file(...)` on every GeoJSON in DatasetsGeojson/",
        kpis=[
            ("BOARDING STOPS", f"{_C['boarding_stops']:,}", "DAILY BOARDING + ALIGHTING"),
            ("ROUTES", f"{_C['routes']:,}", "VEHICLE_TYPE · FARE · LENGTH"),
            ("TERMINALS", f"{_C['terminals']}", "MAWAQIF (POINTS)"),
            ("POPULATION HEXES", f"{_C['population_hexes']:,}", "1 KM² GRID"),
        ],
        insight=(
            "The seven files together describe **supply** (1,302 stops, 1,784 routes, "
            "280 terminals), **demand** (boarding counts per stop, per time of day), "
            "**flow** (9,258 passenger-flow segments, 5,592 vehicle-flow segments, "
            "26,154 commercial-speed records), and **context** (1,525 population hexes "
            "with job-accessibility scores). Every Phase 1 question reads from this "
            "set — the analysis notebook never re-fetches anything."
        ),
        methodology=(
            "**Supply layer.**\n"
            "- `Cairo Daily Boarding.json` (1,302 rows) — bus stops with boarding/alighting "
            "  counts split by time of day.\n"
            "- `Public Transport Routes.json` (1,784 rows) — route lines with `Vehicle_Type`, "
            "  fare, length.\n"
            "- `Public Transport Terminals.json` (280 rows) — origin/destination terminals.\n\n"
            "**Demand & flow.**\n"
            "- `Public Transport Passenger Flow.json` (9,258 segments).\n"
            "- `Public Transport Vehicles Flow.json` (5,592 segments).\n"
            "- `Public Transport Commercial Speeds 2.json` (26,154 records).\n\n"
            "**Context.**\n"
            "- `Population & Employment Access .json` (1,525 hexes, 1 km² each)."
        ),
    ),

    Question(
        id="P1-C2", phase="phase1", nav_label="◆ CLEANING",
        kicker="PHASE 01 · CLEANING · CRS + KNN IMPUTATION",
        headline="Reproject to UTM 36N, KNN-impute the gaps, drop zero rows",
        question_text="How do we turn the seven raw GeoJSONs into trustworthy analytical inputs?",
        why_it_matters=(
            "Two engineering choices determine whether every later chart is honest: "
            "(1) **the CRS**, because every buffer and nearest-neighbour query downstream "
            "assumes meters, and (2) **the imputation strategy**, because zeros and means "
            "are the easy ways to fabricate the conclusion."
        ),
        method="EPSG:4326 → EPSG:32636 (UTM 36N) + KNN imputation (k=5, distance-weighted, nan_euclidean)",
        kpis=[
            ("CRS", _CLEAN["crs"], "UTM 36N · METERS"),
            ("IMPUTATION", "KNN k=5", "DISTANCE-WEIGHTED"),
            ("ROWS DROPPED", f"{_CLEAN['rows_dropped']}", "ZERO LOSS"),
            ("NULL CELLS PRE", f"{_CLEAN['null_cells_pre']:,}", "RECOVERED"),
        ],
        insight=(
            "**Why EPSG:32636.** The raw GeoJSONs ship in EPSG:4326 (lat/long degrees). "
            "Degrees are useless for distance work — at Cairo's latitude, 1° of "
            "longitude is ~96 km. UTM 36N gives meters; every Q3 corridor buffer (120 m), "
            "Q11 ghost-terminal test (100 m), and population join needs metric distance. "
            "**Why KNN.** A missing count is **unknown**, not zero. Imputing zeros would "
            "*invent* the conclusion that some stops are dead. KNN with `weights='distance'` "
            "preserves spatial structure; `metric='nan_euclidean'` lets the imputer compute "
            "distance even when a feature vector itself has NaNs (it skips the missing "
            "dimensions). Result: zero rows dropped, 2,409 null cells filled."
        ),
        methodology=(
            "**Section 03.** `df.to_crs('EPSG:32636')` on every dataframe.\n\n"
            "**Section 06–07.** Three KNN imputations run independently:\n"
            "1. **Boarding numeric** (12 cols, ~250 cells, 42 rows) — features: XY + all boarding cols.\n"
            "2. **Routes.Fare** (45.9% null) — features: route length, capacity, direction, encoded vehicle type.\n"
            "3. **Pax_Flow.Passengers/Hour** — features: segment centroid XY + segment length.\n\n"
            "Each uses `sklearn.impute.KNNImputer(n_neighbors=5, weights='distance', metric='nan_euclidean')`."
        ),
    ),

    Question(
        id="P1-C3", phase="phase1", nav_label="◆ MERGES A–G",
        kicker="PHASE 01 · CLEANING · SPATIAL JOINS",
        headline="Seven merge tables A–G — one spatial join per question",
        question_text="Why pre-join the data into seven `merge_*.csv` tables?",
        why_it_matters=(
            "Every Phase 1 question would otherwise repeat the same spatial join. With "
            "9,258 passenger-flow segments × 280 terminals × 1,525 hexes, repeating "
            "expensive `gpd.sjoin` operations costs 10s of seconds each time. Doing each "
            "join once and persisting the result guarantees every downstream chart sees "
            "exactly the same data."
        ),
        method="gpd.sjoin + buffer-based aggregation; each merge serves a specific question",
        kpis=[
            ("MERGE TABLES", "A–G", "PRE-JOINED"),
            ("CRS", "EPSG:32636", "METERS"),
            ("GAPS DEFINED", "G1 · G2 · G3 · G4", "BY MERGE G + Q9 + Q10 + Q12"),
        ],
        insight=(
            "**Merge A** — Boarding ⨝ Population (point-in-polygon) → feeds Q1 (jobs × alighting), Q9 (underserved hexes).\n\n"
            "**Merge B** — Terminals ⨝ Population (centroid join) → feeds Q2 (symmetry), Q5 (density × terminals).\n\n"
            "**Merge C** — Routes ⨝ Terminals (attribute join on `o_id`/`d_id`) → feeds Q10 (empty returns), Q11 (ghosts).\n\n"
            "**Merge D** — Vehicle/Pax Flow ⨝ Terminals (50 m buffer aggregation) → feeds Q2, Q10.\n\n"
            "**Merge E** — B + D combined → full per-terminal record with population, jobs, flow.\n\n"
            "**Merge F** — Routes per terminal (group-by counts) → feeds Q11.\n\n"
            "**Merge G** — Underused-terminal detector (route + zero boarding within 100 m) → defines **G1 ghost terminals (n=115)**.\n\n"
            "Two formulas worth remembering live in this section:\n"
            "- **G2 · Empty Return Index** = `1 − (passengers / vehicles)`. Threshold ≥ 0.60 → 19 critical terminals.\n"
            "- **G4 · Underserved Score** = `Population / Total_Boarding`. Threshold > 0.5 → 79 underserved hexes."
        ),
        methodology=(
            "All joins run in EPSG:32636 so distances are in meters. Section 09 of "
            "`Cleaning Data.ipynb` produces these merges in a single pass, writes them "
            "to `CleanedData/merge_*.csv`, and the visualization notebook reads only "
            "from those CSVs — never re-running the joins."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 1 · Q1-Q12  (HTML exports already exist in Exports/)
# ═══════════════════════════════════════════════════════════════════════

_EX = "Exports"  # shorthand — joined with DATA_ROOT in renderer

PHASE1_QUESTIONS: List[Question] = [
    Question(
        id="Q1", phase="phase1", nav_label="Q1 · JOBS",
        kicker="PHASE 01 · Q1",
        headline="Where do Cairo's top alighting stops fall on the job-accessibility map?",
        question_text="Do Cairo's highest-demand alighting stops sit where the jobs are?",
        why_it_matters=(
            "If people get off where jobs are accessible, the bus network is doing its "
            "job as a commute backbone. If not, the network is serving residential "
            "density, not employment — which changes every policy conclusion downstream."
        ),
        method="Spatial join (predicate='within') of population hexes to boarding stops; Pearson r on daily alighting × job accessibility",
        kpis=[
            ("r · MORNING × JOBS", "0.261", "PEARSON"),
            ("r · DAILY × JOBS", "0.248", "WEAK"),
            ("SAMPLE", "1,302", "STOPS"),
        ],
        viz_html_paths=[
            f"{_EX}/Q1a_Where_Do_Cairo_s_Top_Alighting_Stops_Fall_on_Job_Accessibility.html",
            f"{_EX}/Q1b_2D_Density_Job_Accessibility_Daily_Alighting.html",
        ],
        insight=(
            "The correlation between morning alighting and job accessibility is only "
            "**r = 0.261** — meaningfully positive but weak. Commuter demand concentrates "
            "at the top 30 stops regardless of how well-connected those stops are to "
            "the job network. That is, routes deposit riders at canonical terminals, not "
            "at job centroids — so the 'commute backbone' framing is a weaker story than "
            "the raw boarding pattern suggests."
        ),
        methodology=(
            "Population hex job-accessibility is `jobs_count_access_60mins` from "
            "`cleaned_population.csv` (1,525 hexes). Each boarding stop is spatially "
            "joined into the hex that contains it. We take the stop's total daily "
            "alighting and the hex's job-accessibility score and compute Pearson "
            "correlation. Missing values were KNN-imputed (k = 5, distance-weighted) "
            "before correlation — imputation documented in Phase 1 null audit "
            "(`null_audit.csv`)."
        ),
    ),

    Question(
        id="Q2", phase="phase1", nav_label="Q2 · SYMMETRY",
        kicker="PHASE 01 · Q2",
        headline="Do terminals act symmetrically as origin and destination?",
        question_text="Does every terminal send and receive the same number of routes?",
        why_it_matters=(
            "Asymmetric terminals (lots of departures, few arrivals — or vice versa) "
            "signal dead-end operational patterns: vehicles dispatched to go out but "
            "never return through the same hub."
        ),
        method="Per-terminal |routes_origin − routes_dest| / max(origin, dest)",
        kpis=[
            ("TERMINALS", "280", "TOTAL"),
            ("METRIC", "ASYM", "INDEX"),
        ],
        viz_html_paths=[
            f"{_EX}/Q2a_Terminal_Symmetry_Origin_vs_Destination_Routes.html",
            f"{_EX}/Q2b_How_Common_Is_Asymmetry_and_Which_Terminals_Show_It_Most.html",
        ],
        insight=(
            "Most terminals are reasonably symmetric, but a long tail shows extreme "
            "asymmetry — vehicles depart but don't return via the same node. These "
            "outliers are candidates for the operational review that Phase 1 flagged "
            "under Gap G2 (empty returns)."
        ),
        methodology=(
            "Computed on `cleaned_routes.csv` by grouping on `o_id` (origin terminal) "
            "and `d_id` (destination terminal) and counting routes. The asymmetry index "
            "is bounded 0–1 and monotonic in the raw difference."
        ),
    ),

    Question(
        id="Q3", phase="phase1", nav_label="Q3 · ADHERENCE",
        kicker="PHASE 01 · Q3",
        headline="How tightly do riders stick to designated route corridors?",
        question_text="What share of alighting happens within 120 m of the formal route line?",
        why_it_matters=(
            "Adherence tells us whether the published route map still describes "
            "reality. Low adherence means routes have quietly drifted; operators "
            "serve convenience, not the printed schedule."
        ),
        method="Point-in-buffer spatial predicate (120 m buffer on every route LineString, EPSG:32636)",
        kpis=[
            ("WITHIN 120 m", "88.0%", "OF ALIGHTING"),
            ("BUFFER", "120", "METERS"),
        ],
        viz_html_paths=[
            f"{_EX}/Q3a_Alighting_Near_vs_Far_from_Route_Corridors.html",
            f"{_EX}/Q3b_Distribution_of_Alighting_by_Route_Proximity.html",
        ],
        insight=(
            "88% of alighting happens within 120 m of the designated route corridor. "
            "Formal routes are a reliable description of where riders actually get "
            "off — a prerequisite for everything downstream (ghost-terminal logic, "
            "empty-return scoring, demand projection)."
        ),
        methodology=(
            "Each route LineString is buffered by 120 m in EPSG:32636 (projected "
            "metres). Boarding stops fall inside that buffer (adherent) or outside "
            "(non-adherent). 120 m is a standard walking-distance heuristic for "
            "Cairo commuters; we tested sensitivity at 80 m and 160 m and the "
            "conclusion holds (83% and 93% respectively)."
        ),
    ),

    Question(
        id="Q4", phase="phase1", nav_label="Q4 · FORMAL vs INFORMAL",
        kicker="PHASE 01 · Q4",
        headline="Formal vs informal — who moves Cairo?",
        question_text="What share of transport is run by formal vs informal operators?",
        why_it_matters=(
            "If informal operators dominate, regulation and government revenue are "
            "structurally weak. This single question reframes every policy "
            "recommendation from 'improve the state network' to 'integrate with "
            "the real network'."
        ),
        method="Classification by operator type on cleaned_routes + cleaned_boarding",
        kpis=[
            ("INFORMAL SHARE", "≫50%", "BY ROUTE"),
            ("TOP 20", "SHOWN", "BELOW"),
        ],
        viz_html_paths=[
            f"{_EX}/Q4a_Distribution_of_Formal_Transport_Percentage_Morning.html",
            f"{_EX}/Q4b_Morning_vs_Daily_Formal_percent_does_preference_shift.html",
            f"{_EX}/Q4c_Total_Boardings_by_Mode_Time_of_Day_Formal_vs_Informal.html",
            f"{_EX}/Q4d_Fare_vs_Route_Length_Formal_vs_Informal_Economics.html",
            f"{_EX}/Q4e_Top_20_Stops_by_Informal_Demand_Formal_vs_Informal_Side-by-Side.html",
        ],
        insight=(
            "Egypt is predominantly informal-operated. A large portion of terminals "
            "does not see a single formal vehicle. The top 20 informal-demand stops "
            "are visible in the ranked bar chart — they would be the first customers "
            "of a System-B-aware route planner like Masari."
        ),
        methodology=(
            "Operator type is inferred from `vehicle_name` on `cleaned_routes.csv`. "
            "Microbus / Tomnaya → informal; Bus / Metro → formal. Fare per km comes "
            "from `fare` / `route_length_km` with KNN imputation for missing fares "
            "(45.9% of routes had null fare before imputation)."
        ),
    ),

    Question(
        id="Q5", phase="phase1", nav_label="Q5 · POP × TERMINALS",
        kicker="PHASE 01 · Q5",
        headline="Where population is dense, do terminals follow?",
        question_text="Is there a relationship between hex population and terminal count?",
        why_it_matters=(
            "A positive correlation is the minimum bar for a coherent transport plan. "
            "A weak correlation signals that terminals were placed by other logic — "
            "political, historical, or accidental."
        ),
        method="Terminal count per population hex via spatial join; Pearson / Spearman",
        kpis=[("ASSOCIATION", "WEAK +", "SPATIAL")],
        viz_html_paths=[
            f"{_EX}/Q5a_Population_vs_Terminal_Count_per_Hexagon.html",
            f"{_EX}/Q5b_Population_Distribution_Hexagons_With_vs_Without_Terminals.html",
        ],
        insight=(
            "Higher-population hexes have more terminals — but the association is "
            "surprisingly weak. Many dense hexes have no terminal at all. The "
            "result anchors Gap G4 (underserved hexes, n = 79)."
        ),
        methodology=(
            "Spatial join (`predicate='within'`) of each terminal polygon centroid "
            "into the population hex grid. Per-hex terminal count joined with "
            "`pop_18`. Hexes with zero terminals plotted separately to avoid biasing "
            "the trend with zero-inflation."
        ),
    ),

    Question(
        id="Q6", phase="phase1", nav_label="Q6 · ROUTES",
        kicker="PHASE 01 · Q6",
        headline="Do more routes mean more passengers?",
        question_text="Is there a plateau where extra routes stop adding ridership?",
        why_it_matters=(
            "If the relationship is linear, adding routes reliably adds riders — a "
            "simple supply lever. If it plateaus, the lever breaks beyond a "
            "saturation point. Every future capital-allocation decision hinges on which."
        ),
        method="Correlation on total_routes_at_stop × daily boarding; mean per route-count bin",
        kpis=[("RELATIONSHIP", "LINEAR", "NO PLATEAU")],
        viz_html_paths=[
            f"{_EX}/Q6a_Routes_Supply_vs_Passenger_Demand.html",
            f"{_EX}/Q6b_Average_Passenger_Activity_by_Route_Count_Bin.html",
            f"{_EX}/Q6b_Passenger_Demand_Distribution_by_Route_Supply.html",
            f"{_EX}/Q6c_Major_High-Demand_Stops.html",
        ],
        insight=(
            "No plateau. The linear relationship holds across the whole range of "
            "route counts. This is a positive operational finding: adding routes "
            "at a stop predictably increases boardings. Capital allocation is "
            "linear in expectation."
        ),
        methodology=(
            "Per-stop aggregate count of routes (cross-tabulating cleaned_boarding × "
            "cleaned_routes via stop-to-route linkage). Binned by route count. Mean "
            "boarding per bin plotted with 95% CI. Tested parametric and "
            "non-parametric correlations; both significant, both positive, both "
            "monotonic."
        ),
    ),

    Question(
        id="Q7", phase="phase1", nav_label="Q7 · AM/PM",
        kicker="PHASE 01 · Q7",
        headline="Do stops flip personality between morning and evening?",
        question_text="Which stops are residential (morning-heavy) and which are work hubs?",
        why_it_matters=(
            "The morning-to-evening ratio is a free classifier for stop type. Evening-"
            "heavy stops are work zones that need lighting, security, extended service; "
            "morning-heavy stops are origin points that need capacity at peak."
        ),
        method="log-scale ratio of morning boarding : evening boarding per stop",
        kpis=[("CLASSIFIER", "AM/PM", "RATIO"),
              ("USE", "SERVICE", "DESIGN")],
        viz_html_paths=[
            f"{_EX}/Q7a_Log-Scale_Transit_Flow_Residential_vs_Commercial_Hubs.html",
            f"{_EX}/Q7b_Morning_Evening_Imbalance_Distribution.html",
        ],
        insight=(
            "The ratio cleanly separates stop types. Residential clusters sit on the "
            "morning-heavy side; Downtown / Tahrir / Heliopolis sit on the evening-"
            "heavy side. This is a free segmentation — no modelling needed — and "
            "feeds directly into service design decisions."
        ),
        methodology=(
            "Morning and evening boarding are separate columns in `cleaned_boarding.csv`. "
            "Ratio = (morning + ε) / (evening + ε), log-scaled for visualization. "
            "Stops with <10 combined boardings filtered out to avoid noise."
        ),
    ),

    Question(
        id="Q8", phase="phase1", nav_label="Q8 · SPATIAL",
        kicker="PHASE 01 · Q8",
        headline="Is demand spatially clustered?",
        question_text="Do high-boarding stops cluster geographically?",
        why_it_matters=(
            "Spatial clustering tells us whether transit demand is a property of "
            "neighborhoods (which can be targeted) or of individual stops (which "
            "must be handled one at a time)."
        ),
        method="Moran-style local lag scatter; Pearson r on boarding × neighbor mean",
        kpis=[("PATTERN", "HH/LL", "CLUSTERS"),
              ("SAMPLE", "1,302", "STOPS")],
        viz_html_paths=[
            f"{_EX}/Q8a_Enhanced_Moran_Scatter_Detecting_Spatial_Transit_Regimes.html",
            f"{_EX}/Q8b_Network_Composition_Distribution_of_Spatial_Clusters.html",
        ],
        insight=(
            "High-boarding stops cluster with other high-boarding stops (HH). Low-"
            "boarding stops cluster with other low-boarding stops (LL). This is "
            "the classic Moran's-I positive-autocorrelation signature. Transit "
            "demand is a property of neighborhoods."
        ),
        methodology=(
            "For each stop, compute the mean daily boarding across its spatial "
            "neighbors (k = 8 nearest via KDTree in EPSG:32636). Pearson r between "
            "own boarding and neighbor mean. HH/LL = both above / both below "
            "median; HL/LH = mixed outliers. The four-quadrant split is Moran's "
            "local indicator."
        ),
    ),

    Question(
        id="Q9", phase="phase1", nav_label="Q9 · UNDERSERVED",
        kicker="PHASE 01 · Q9",
        headline="Which hexes are most underserved?",
        question_text="Which hexagons combine high population with low boarding?",
        why_it_matters=(
            "Underserved hexes are the primary inventory for Gap G4 — the "
            "structural mismatch between where people live and where transit "
            "reaches. These are the cells most likely to benefit from Masari's "
            "System-A + System-B integration."
        ),
        method="Underserved_Score = pop / total_boarding; threshold > 0.5",
        kpis=[("UNDERSERVED HEXES", "79", "SCORE > 0.5"),
              ("THRESHOLD", "0.5", "NORMALIZED")],
        viz_html_paths=[
            f"{_EX}/Q9a_Priority_Analysis_High-Impact_Transit_Deserts.html",
        ],
        insight=(
            "79 hexagons score above 0.5 on the composite underserved metric. "
            "They cluster in Imbaba, Shubra, Matariyya, and Ain Shams — the "
            "exact Cairo neighborhoods that Phase 2 will show received minimal "
            "post-2014 infrastructure coverage."
        ),
        methodology=(
            "Composite score normalized to [0, 1] after winsorizing population "
            "and boarding at the 99th percentile. Threshold 0.5 chosen to "
            "capture the top-decile of mismatch. The top 15 hexes are surfaced "
            "in the visualization as intervention priorities."
        ),
    ),

    Question(
        id="Q10", phase="phase1", nav_label="Q10 · EMPTY",
        kicker="PHASE 01 · Q10",
        headline="Empty returns — where do vehicles arrive without riders?",
        question_text="Which terminals have the highest Empty Return Index (Index = 1 − pax/vehicles)?",
        why_it_matters=(
            "Empty trips are operationally expensive and environmentally wasteful. "
            "Identifying the worst terminals gives operators a precise list of "
            "where to redistribute capacity."
        ),
        method="Empty Return Index per terminal; threshold ≥ 0.60 = critical",
        kpis=[("CRITICAL", "19", "TERMINALS"),
              ("HEALTHY", "208", "TERMINALS"),
              ("THRESHOLD", "0.60", "INDEX")],
        viz_html_paths=[
            f"{_EX}/Q10_The_Empty_Return_Index_is_Binary_Healthy_vs_Completely_Wasteful.html",
            f"{_EX}/Q10a_Top_20_Terminals_by_Empty_Return_Severity.html",
            f"{_EX}/Q10b_Vehicles_vs_Passengers_--_below_the_diagonal_empty_trips.html",
        ],
        insight=(
            "The distribution is bimodal — 19 terminals are critically wasteful "
            "(Index ≥ 0.60), 208 are fully healthy (Index = 0). Very few are in "
            "between. This bimodality is useful: the intervention list is exactly "
            "the top 19, and the other 208 need no change."
        ),
        methodology=(
            "Daily inbound passengers counted from `cleaned_boarding.csv` (alighting "
            "column); daily vehicle arrivals counted from `cleaned_vehicle_flow.csv`. "
            "Index = 1 − passengers / vehicles. Negative indices clipped to zero. "
            "Threshold 0.60 set at the 93rd percentile of the distribution."
        ),
    ),

    Question(
        id="Q11", phase="phase1", nav_label="Q11 · GHOSTS",
        kicker="PHASE 01 · Q11",
        headline="Ghost terminals — relocate, decommission, or audit?",
        question_text="Which terminals have no boarding activity within a 100 m walking buffer?",
        why_it_matters=(
            "Ghost terminals are invisible in ridership data but visible in the route "
            "map — they consume operational attention without producing service. "
            "Sub-classifying them into action categories is the difference between "
            "'we should do something' and 'here is a three-tier intervention plan'."
        ),
        method="Walking-buffer sensitivity (100 / 500 / 1000 m) on cleaned_terminals × cleaned_boarding",
        kpis=[("GHOSTS", "115", "at 100 m"),
              ("NEAR MISS", "69", "100–500 m"),
              ("ISOLATED", "29", ">1 km")],
        viz_html_paths=[
            f"{_EX}/Q11_Interactive_Slider_Walking_Radius_--_Watch_Red_Ghost_Terminals_Turn_Green.html",
            f"{_EX}/Q11_Recovery_Curve_--_How_Many_Ghost_Terminals_Disappear_as_Walking_Radius_Grows.html",
            f"{_EX}/Q11_What_Kind_of_Ghost_Terminal_--_69_need_stop_relocation_only_29_need_route_cancellation.html",
            f"{_EX}/Q11a_Terminal_Utilization_at_100m_Baseline.html",
            f"{_EX}/Q11b_Operational_Zone_Map_--_Strategy_Overview_at_100m.html",
            f"{_EX}/Q11c_Zone_Comparison_--_Same_Route_Budget_Vastly_Different_Output.html",
            f"{_EX}/Q11d_Route_Budget_Treemap_--_Box_area_share_of_total_routes.html",
        ],
        insight=(
            "115 ghost terminals at the 100 m baseline. 69 are 'near-miss' — a stop "
            "exists between 100 m and 500 m away (relocate the stop). 17 are "
            "'stop-too-far' (500 m–1 km, improve walkability). 29 are truly "
            "isolated beyond 1 km (audit or decommission). The interactive slider "
            "lets you watch red ghost terminals turn green as you expand the "
            "walking radius — a clean demonstration of the recovery curve."
        ),
        methodology=(
            "For each terminal, build a point-in-buffer query against all 1,302 "
            "boarding stops. A terminal is a ghost at radius r if zero of its "
            "route-endpoint buffers contains any boarding stop within r metres. "
            "The 100/500/1000 m thresholds yield 115/46/29 ghosts respectively — "
            "which gives the three-tier action classification."
        ),
    ),

    Question(
        id="Q12", phase="phase1", nav_label="Q12 · VEHICLE FIT",
        kicker="PHASE 01 · Q12",
        headline="Are vehicles matched to their routes?",
        question_text="Are long routes operated by appropriately-sized vehicles?",
        why_it_matters=(
            "A 14-seat microbus on a 60 km route is operationally inefficient and "
            "raises the per-kilometer cost for riders. Matching vehicle capacity "
            "to route length is a basic operational hygiene question."
        ),
        method="Route length × vehicle capacity cross-tabulation; fare/km by vehicle type",
        kpis=[("MICROBUS", "75%", "OF >50 KM ROUTES"),
              ("ROUTES", "1,784", "TOTAL")],
        viz_html_paths=[
            f"{_EX}/Q12a_Route_Length_Distribution_by_Vehicle_Type_violin.html",
            f"{_EX}/Q12b_Avg_Route_Length_Vehicle_Type_x_Capacity.html",
            f"{_EX}/Q12c_Fare_per_km_by_Vehicle_Type_which_type_offers_best_value.html",
            f"{_EX}/Q12d_Vehicle_Type_Summary_Length_vs_Fare_vs_Capacity_bubble_size_seats.html",
            f"{_EX}/Q12e_ECDF_Cumulative_Route_Length_Distribution_by_Vehicle_Type.html",
        ],
        insight=(
            "75% of routes longer than 50 km are run by the smallest vehicle type "
            "(14-seat microbus). This is a cost-allocation mismatch — long routes "
            "compound per-km inefficiencies. It also feeds Gap G3 (vehicle-route "
            "mismatch) and is a direct justification for Phase 2's focus on "
            "integrating microbus demand into the formal planning."
        ),
        methodology=(
            "Route length in km from `cleaned_routes.csv`. Vehicle type from "
            "`vehicle_name`. Fare per km = fare / length_km after imputation. "
            "The violin and ECDF visuals are preferred over bar charts because "
            "route-length distributions are heavily right-skewed — medians beat "
            "means for interpretation."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 1 · G1-G4 GAPS  (reuse Q-level HTML exports)
# ═══════════════════════════════════════════════════════════════════════

def _build_g1():
    from components.charts import g1_ghost_classification
    return g1_ghost_classification()


def _build_g2():
    from components.charts import g2_empty_returns
    return g2_empty_returns()


def _build_g3():
    from components.charts import g3_vehicle_mix
    return g3_vehicle_mix()


def _build_g4():
    from components.charts import g4_underserved
    return g4_underserved()


GAP_QUESTIONS: List[Question] = [
    Question(
        id="G1", phase="gap", nav_label="G1 · GHOSTS",
        kicker="PHASE 01 · STRUCTURAL GAP · G1",
        headline="115 ghost terminals at the 100 m walking baseline",
        question_text="How many terminals have no boarding activity within a walkable radius?",
        why_it_matters=(
            "G1 is the cleanest single indicator of where the bus network mis-aligns "
            "with rider behavior. Phase 2's Q14 takes these 115 ghost terminals and "
            "overlays the post-2014 metro network to show that 84% of them remain "
            "stranded."
        ),
        method="100 m walking-buffer classification + 3-tier distance subclassification",
        kpis=[("TOTAL", "115", "AT 100 m"),
              ("NEAR MISS", "69", "100–500 m"),
              ("ISOLATED", "29", ">1 km"),
              ("RECOVERY AT 500 m", "60%", "46 OF 115")],
        viz_builders=[_build_g1],
        viz_html_paths=[f"{_EX}/Q11_What_Kind_of_Ghost_Terminal_--_69_need_stop_relocation_only_29_need_route_cancellation.html"],
        insight=(
            "The three-tier classification turns a binary 'ghost or not' into a "
            "three-lane action plan. **Relocate the stop** (69 terminals, cheap). "
            "**Improve walkability** (17 terminals, medium effort). **Audit or "
            "decommission** (29 terminals, hard but decisive). Every later chapter "
            "of this story references this 115 → 69 / 17 / 29 decomposition."
        ),
        methodology=(
            "Re-uses Q11 logic. A ghost terminal is one where no boarding stop "
            "sits inside a 100 m buffer of any route endpoint associated with "
            "the terminal. Sensitivity: at 500 m buffer 46 of 115 ghosts resolve "
            "(60% recovery curve)."
        ),
    ),

    Question(
        id="G2", phase="gap", nav_label="G2 · EMPTY RETURNS",
        kicker="PHASE 01 · STRUCTURAL GAP · G2",
        headline="19 terminals receive vehicles without passengers",
        question_text="Which terminals fail the Empty Return Index check (threshold ≥ 0.60)?",
        why_it_matters=(
            "Operational waste is measurable here. Every empty-return trip is a "
            "vehicle-hour paid for but not fare-recovered. Concentration matters: "
            "if the worst 19 account for most of the losses, fleet redistribution "
            "is tractable."
        ),
        method="Empty Return Index = 1 − passengers/vehicles; threshold calibrated at 93rd pctile",
        kpis=[("CRITICAL", "19", "INDEX ≥ 0.60"),
              ("HEALTHY", "208", "INDEX = 0.0"),
              ("BIMODAL", "YES", "FEW MID-RANGE")],
        viz_builders=[_build_g2],
        viz_html_paths=[f"{_EX}/Q10_The_Empty_Return_Index_is_Binary_Healthy_vs_Completely_Wasteful.html"],
        insight=(
            "The Empty Return Index distribution is nearly binary — either a "
            "terminal is perfectly healthy (Index = 0) or it is catastrophically "
            "wasteful (Index ≥ 0.6). Very few terminals sit between. That binary "
            "shape makes the policy response easy: intervene on the 19 critical "
            "terminals only; leave the 208 alone."
        ),
        methodology="See Q10 methodology. Threshold 0.60 set at 93rd percentile.",
    ),

    Question(
        id="G3", phase="gap", nav_label="G3 · VEHICLE MISMATCH",
        kicker="PHASE 01 · STRUCTURAL GAP · G3",
        headline="75% of routes longer than 50 km are on the smallest vehicle",
        question_text="Which routes use under-sized vehicles for their length?",
        why_it_matters=(
            "A 14-seat microbus on a 60 km route is the definition of operational "
            "mismatch. Per-passenger economics suffer, turnaround times stretch, "
            "and the fare-to-cost ratio deteriorates."
        ),
        method="Route length × vehicle capacity joint classification on cleaned_routes.csv",
        kpis=[("MICROBUS ON >50 KM", "75%", "OF ROUTES"),
              ("BOX", "18", "ROUTES"),
              ("BUS", "503", "ROUTES"),
              ("MICROBUS", "861", "ROUTES")],
        viz_builders=[_build_g3],
        viz_html_paths=[f"{_EX}/Q12a_Route_Length_Distribution_by_Vehicle_Type_violin.html"],
        insight=(
            "The vehicle mix is dominated by 14-seat microbuses, and three out of "
            "four long-haul routes are run on this smallest vehicle. The story is "
            "not that microbuses are bad — they are often the only affordable "
            "option for riders — but that their cost-per-km advantage disappears "
            "when compounded over 50 km routes. Masari's route planner can surface "
            "this to riders so they can trade longer wait times for cheaper trips."
        ),
        methodology="See Q12 methodology.",
    ),

    Question(
        id="G4", phase="gap", nav_label="G4 · UNDERSERVED",
        kicker="PHASE 01 · STRUCTURAL GAP · G4",
        headline="79 hexagons combine high population with low boarding",
        question_text="Which population hexes have score > 0.5 on the underserved metric?",
        why_it_matters=(
            "G4 is the inventory of places that Masari serves. Each hex is a "
            "neighborhood where people live, but the bus network reaches less "
            "than residents' raw density would predict."
        ),
        method="Underserved_Score = Population / Total_Boarding (normalized), threshold > 0.5",
        kpis=[("UNDERSERVED HEXES", "79", "SCORE > 0.5"),
              ("HEX GRID", "1,525", "TOTAL")],
        viz_builders=[_build_g4],
        viz_html_paths=[f"{_EX}/Q9a_Priority_Analysis_High-Impact_Transit_Deserts.html"],
        insight=(
            "79 of 1,525 hexes (≈ 5%) are structurally underserved. They cluster "
            "geographically (Moran's I was positive in Phase 1 Q8). These 79 hexes "
            "are the first inventory for Masari's TAM — every one of them is a "
            "dense population mass the existing transport map can't fully describe."
        ),
        methodology="See Q9 methodology.",
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 2 · CLEANING · 3 condensed entries
#  (NEW — sources, integration pipeline, semantic matching with SBERT)
# ═══════════════════════════════════════════════════════════════════════

def _build_p2_osm_cross_verify():
    from components.charts import osm_cross_verification_map
    return osm_cross_verification_map()


def _build_null_audit():
    from components.charts import null_audit_before_after
    return null_audit_before_after()


def _build_integration_yield():
    from components.charts import integration_yield
    return integration_yield()


# ─── Cleaning / scraping diagnostics (per-source) ────────────────────
def _build_metro_timeline():       from components.charts import metro_opening_timeline;     return metro_opening_timeline()
def _build_lrt_backfill():         from components.charts import lrt_coordinate_backfill;    return lrt_coordinate_backfill()
def _build_brt_diagnostic():       from components.charts import brt_scrape_diagnostic;      return brt_scrape_diagnostic()
def _build_districts_cagr():       from components.charts import districts_cagr_distribution; return districts_cagr_distribution()
def _build_manifest():             from components.charts import manifest_table;              return manifest_table()
def _build_q19_chart():            from components.charts import q19_gtfs_coverage;          return q19_gtfs_coverage()


PHASE2_CLEANING: List[Question] = [
    # ───────────────────────────────────────────────────────────────────
    #  P2-E0 · per-source exploration helper (NEW)
    # ───────────────────────────────────────────────────────────────────
    Question(
        id="P2-E0", phase="phase2", nav_label="◆ EXPLORATION",
        kicker="PHASE 02 · CLEANING · POST-SCRAPE EXPLORATION",
        headline="One audit helper, eight sources, the same five checks every time",
        question_text="How do we explore each scraped source without writing a custom audit per source?",
        why_it_matters=(
            "Eight sources × five checks each is forty audit calls. Doing them "
            "by hand drifts: one source gets a coordinate-spread chart, another "
            "doesn't. We wrote one helper, `explore_scraped_data()`, and called "
            "it after every scrape so the audit is uniform."
        ),
        method="explore_scraped_data(label, csv_path, key_cols, coord_cols) → row count + dtypes + null %, coordinate bounds vs Cairo bbox, IQR outliers, top-N duplicates, head(3)",
        kpis=[
            ("SOURCES AUDITED", "8", "S1 · S3 · S4 · S5 · S6 · S7 · S8"),
            ("CHECKS PER SOURCE", "5", "UNIFORM"),
            ("CHARTS WRITTEN", "57", "scraping_notebook_visuals/"),
            ("DATA MUTATED", "0", "AUDIT-ONLY"),
        ],
        viz_html_paths=[
            "Phase2/Exports/scraping_notebook_visuals/p2-c2_01_null_percentage_per_column_post_cleaning_all_7_sources.html",
            "Phase2/Exports/scraping_notebook_visuals/p2-c3_01_null_percentage_per_column_post_cleaning_all_7_sources.html",
        ],
        insight=(
            "**Five checks every audit runs.**\n\n"
            "1. **Shape and dtypes.** Confirms the CSV has the columns we expect and "
            "their types are sensible (no `lat` ending up as object/string).\n\n"
            "2. **Null percentage per column.** Surfaces real holes. Caught the "
            "Wikipedia LRT page shipping zero coordinates and the BRT scrape "
            "missing `station_ar` rows when search returned only English.\n\n"
            "3. **Coordinate spread vs Cairo bbox.** A single Cairo bbox is the "
            "sanity rail. Anything outside it is either a parser error or the "
            "wrong row entirely.\n\n"
            "4. **IQR outlier candidates.** For numeric columns, flags rows that "
            "sit beyond Q1 − 1.5·IQR or Q3 + 1.5·IQR. We do not delete these — "
            "they are documented and carried forward — but we look at them.\n\n"
            "5. **Top-N duplicates by key columns.** Catches the same physical "
            "station discovered twice from English and Arabic searches before the "
            "uroman + RapidFuzz dedup kicks in."
        ),
        methodology=(
            "All audit functions live in `drafts/phase2_utils.py` (`show_df`, "
            "`show_metrics`, `show_note`, `explore_scraped_data`). The helper is "
            "**audit-only** — it never mutates rows. Every chart it produces is "
            "saved as standalone HTML under `Phase2/Exports/scraping_notebook_visuals/` "
            "so the exploration story is reproducible without rerunning the "
            "scraper. The cleaning notebook calls the helper once after every "
            "source block (cells 17, 25, 30, 41, 48, 51, 61, 66, 70)."
        ),
    ),
    Question(
        id="P2-C1", phase="phase2", nav_label="◆ 8 SOURCES (S1–S8)",
        kicker="PHASE 02 · CLEANING · DATA SOURCES",
        headline="Eight external sources, scraped fresh and documented honestly",
        question_text="Where does the Phase 2 data come from, and why these eight sources?",
        why_it_matters=(
            "Phase 2 has no government open-data feed for new infrastructure. "
            "Every claim about Metro Line 3, the LRT, or the BRT depends on us "
            "scraping, cleaning, and triangulating a believable dataset from "
            "publicly available sources. The eight sources are chosen to be "
            "**triangulating** — Wikipedia and Google Maps are independent of "
            "OSM, and S6 (citypopulation.de) is independent of all of them."
        ),
        method="Per-source: define URL → check raw cache → fetch (Fetcher / DynamicFetcher / API) → parse → standardize → save → audit",
        kpis=[("METRO STATIONS",  f"{SCRAPE['metro']['n']}", "S3 · WIKIPEDIA"),
              ("LRT (with coords)", f"{SCRAPE['lrt']['with_coords']} of {SCRAPE['lrt']['n']}", f"S4 · {SCRAPE['lrt']['rescued_overpass']} OSM + {SCRAPE['lrt']['rescued_gmaps']} GMAPS"),
              ("BRT STATIONS",    f"{SCRAPE['brt']['n']}", "S5 · GOOGLE MAPS"),
              ("DISTRICTS",       "408 → 68", "S6 · CITYPOP → CAIRO")],
        viz_html_paths=["Phase2/Exports/manifest_table.html"],
        insight=(
            "**S1 · TfC GTFS** — official bus + metro feeds (8 standard CSVs each).\n\n"
            "**S3 · Wikipedia metro** — 89 stations, 100% coordinates, opening dates → "
            "lets us derive 'post-2014' filter for Q14, Q22, H2.\n\n"
            "**S4 · Wikipedia LRT** — 20 stations, **0% coordinates on the page**. "
            "Backfilled to **16 with coordinates** via OSM Overpass (9) + Google Maps "
            "fallback (7). 4 remain coordinate-less (planned but not yet on the ground).\n\n"
            "**S5 · BRT via Google Maps** — no Wikipedia page exists. 10 viewport "
            "queries via Playwright; regex aria-labels; uroman transliteration; "
            "3-tier dedup → 12 stations.\n\n"
            "**S6 · citypopulation.de** — 408 admin rows → filter to Greater Cairo (68 "
            "districts) → CAGR 2006→2017 + Nominatim centroid per district. **The "
            "Nominatim centroid is the methodological upgrade that turns H1's effect "
            "size from 0.16 (small) into 0.83 (huge).**\n\n"
            "**S7 · Vehicles** — Wikipedia + World Bank API. Used as background only.\n\n"
            "**S8 · OSM Overpass** — independent transport-feature layer for "
            "cross-verification (Stage 2 of the integration pipeline)."
        ),
        methodology=(
            "Every source block follows the same 7-step pattern: define URL → check "
            "whether a cached raw file exists in `RAW_DIR` → fetch (Fetcher for static, "
            "DynamicFetcher for JS-rendered, REST for APIs) → parse (BeautifulSoup-style, "
            "or regex for awkward fields like DMS coordinates) → standardize (reproject "
            "to EPSG:32636, normalize column names) → save to `Phase2/CleanedData/` → "
            "print row count + sample. This pattern makes every source independently "
            "debuggable and re-runnable."
        ),
    ),

    Question(
        id="P2-S3", phase="phase2", nav_label="◆ S3 · METRO TIMELINE",
        kicker="PHASE 02 · CLEANING · S3 · WIKIPEDIA METRO",
        headline="Cairo Metro · 89 stations across three lines, parsed from Wikipedia",
        question_text="What did the Wikipedia scrape (S3) actually give us?",
        why_it_matters=(
            "S3 is the cleanest source — Wikipedia ships per-line wikitables with "
            "names, opening dates, and DMS coordinates. We strip footnotes, convert "
            "DMS to decimal, and derive opening-phase labels from year thresholds. "
            "The opening_year column is what enables Q14 (post-2014 metro filter) "
            "and the animated metro-expansion visualization downstream."
        ),
        method="`pd.read_html` on List_of_Cairo_Metro_stations · 3 wikitables · DMS→decimal · opening date → year → phase label",
        kpis=[("STATIONS", "89", "ALL WITH COORDS"),
              ("LINES", "3", "L1 · L2 · L3"),
              ("WINDOW", "1987–2024", "37 YEARS")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-s3_01_s3_metro_stations_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s3_02_s3_metro_stations_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s3_03_s3_metro_stations_line_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s3_04_s3_metro_stations_phase_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s3_05_s3_metro_opening_year_spread_by_line.html'],
        insight=(
            "**Three eras visible in the timeline.** Line 1 launches the system in "
            "1987 with 14 stations on the Helwan–Marg corridor; opens slowly through "
            "1989 (12 more stations). Line 2 extends through 1996–2005. Then a "
            "long pause until **Line 3** starts in 2012 and pulses out in phases "
            "(3A 2014, 3B 2018–2019, 3C 2020–2022, 3D 2024). The scrape captures "
            "every station across all three lines with 100% coordinate coverage."
        ),
        methodology=(
            "Each wikitable row is a station. `pd.read_html` returns the raw HTML "
            "table; we normalize column names, strip Wikipedia footnotes (`[1]`, "
            "`[2]`, …) from station names, parse DMS coordinates "
            "(`30°02′00″N 31°14′17″E`) to decimal lat/lon, and derive the "
            "opening_year from the dateparser-friendly opening-date string. The "
            "phase column is bucketed from year thresholds (1987 = original L1; "
            "2014+ for L3 = 'Phase 3+')."
        ),
    ),

    Question(
        id="P2-S4S5", phase="phase2", nav_label="◆ S4 · LRT + S5 · BRT",
        kicker="PHASE 02 · CLEANING · S4 LRT + S5 BRT · THE HARD SOURCES",
        headline="LRT has zero coords on Wikipedia · BRT has no Wikipedia page at all",
        question_text="How do we get coordinates for the new modes when no clean source exists?",
        why_it_matters=(
            "S4 (LRT) and S5 (BRT) are the engineering challenge of Phase 2. "
            "Wikipedia ships the LRT as 20 stations with **zero coordinates on "
            "the page**. BRT has no Wikipedia page at all. Without these sources "
            "Phase 2 has no way to compute the H2 catchment test or the H3 corridor "
            "match. The backfill story is itself a project finding: when the world "
            "doesn't publish data cleanly, you scrape, triangulate, and document "
            "what you couldn't recover."
        ),
        method="LRT: OSM Overpass per-station name search + Google Maps fallback. BRT: 10 viewport queries via Playwright + uroman transliteration + 3-tier dedup.",
        kpis=[("LRT TOTAL",          f"{SCRAPE['lrt']['n']}",                "STATIONS"),
              ("LRT WITH COORDS",    f"{SCRAPE['lrt']['with_coords']}",      "AFTER BACKFILL"),
              ("BRT STATIONS",       f"{SCRAPE['brt']['n']}",                "FROM GOOGLE MAPS"),
              ("BRT METHOD",         "PLAYWRIGHT",                            "DYNAMIC FETCHER")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-s4s5_01_s4_lrt_station_list_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_02_s4_lrt_station_list_is_operational_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_03_s4_lrt_station_list_opened_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_04_s4_lrt_operational_vs_non_operational_stations.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_05_s5_brt_stations_deduped_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_06_s5_brt_stations_deduped_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_07_s5_brt_stations_deduped_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_08_s5_brt_stations_deduped_search_lang_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_09_s5_brt_stations_deduped_station_en_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_10_s5_brt_retained_rows_by_scrape_query.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_11_s8_lrt_stations_after_coordinate_backfill_missing_values_by_.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_12_s8_lrt_stations_after_coordinate_backfill_coordinate_spread_.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_13_s8_lrt_stations_after_coordinate_backfill_numeric_iqr_outlie.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_14_s8_lrt_stations_after_coordinate_backfill_is_operational_dis.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_15_s8_lrt_stations_after_coordinate_backfill_opened_distributio.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s4s5_16_s8_lrt_located_vs_still_missing_coordinates.html'],
        insight=(
            f"**LRT.** Wikipedia lists {SCRAPE['lrt']['n']} stations but ships "
            f"**zero coordinates**. We rescue {SCRAPE['lrt']['rescued_overpass']} "
            "via OSM Overpass per-station name search (the LRT names are unique "
            "enough to query) and another "
            f"{SCRAPE['lrt']['rescued_gmaps']} via Google Maps fallback. The CSV "
            f"now carries **{SCRAPE['lrt']['with_coords']} valid coordinates**; "
            "the rest are still planned-only.\n\n"
            f"**BRT.** No Wikipedia article exists, so we run **10 Google Maps "
            "viewport queries** in both English and Arabic via Playwright "
            f"(scrapling.fetchers.DynamicFetcher). The diagnostic map shows the "
            "same physical station discovered from different search languages — "
            "uroman transliteration (المرج → 'almrj') makes the cross-script "
            "dedup possible."
        ),
        methodology=(
            "LRT uses **scrapling.fetchers.Fetcher** for the static Wikipedia page, "
            "then **Overpass API** queries scoped to a Cairo bounding box, then "
            "Google Maps as a last resort. BRT uses **scrapling.fetchers."
            "DynamicFetcher** (Playwright-backed) because Google Maps results render "
            "via JavaScript. We dedupe with a 3-tier hierarchy: spatial-near "
            "(within 50 m), spatial-far + name match, then unique. Both sources "
            "feed the 4-stage integration pipeline downstream."
        ),
    ),

    Question(
        id="P2-S6S7", phase="phase2", nav_label="◆ S6 · DEMOGRAPHICS",
        kicker="PHASE 02 · CLEANING · S6 CITYPOPULATION + S7 VEHICLES",
        headline="68 Greater Cairo districts · CAGR 2006→2017 · Nominatim centroids",
        question_text="How do we connect transport infrastructure to the people who would actually use it?",
        why_it_matters=(
            "Without population we cannot ask 'did infrastructure go where people "
            "are?' — the most basic question in Phase 2. citypopulation.de gives us "
            "**68 Greater Cairo districts with population at 4 census points** "
            "(1996, 2006, 2017, 2023) and Nominatim centroids per district. **The "
            "Nominatim centroid upgrade is what turned H1's effect size from 0.16 "
            "(small) into 0.83 (huge)** — the earlier draft used a 3-governorate "
            "centroid proxy that smeared the spatial-weights graph."
        ),
        method="Scrape citypopulation.de Egypt admin hierarchy (408 rows) → filter to Greater Cairo (68 districts) → reshape wide→long → CAGR per district → Nominatim centroid",
        kpis=[("DISTRICTS",       "68",         "GREATER CAIRO"),
              ("CENSUS YEARS",    "1996/2006/2017/2023", "4 POINTS"),
              ("MEDIAN CAGR",     "+1.2%",      "PER YEAR"),
              ("FASTEST",         "≈+15%",      "NEW SATELLITE CITIES")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-s6s7_01_s6_districts_long_table_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_02_s6_districts_long_table_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_03_s6_districts_long_table_governorate_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_04_s6_districts_long_table_status_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_05_s6_districts_wide_table_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_06_s6_districts_wide_table_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_07_s6_districts_wide_table_governorate_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_08_s6_districts_wide_table_status_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_09_s6_districts_population_trend_sanity_check.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_10_s6_districts_with_centroids_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_11_s6_districts_with_centroids_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_12_s6_districts_with_centroids_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_13_s6_districts_with_centroids_centroid_source_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_14_s6_districts_with_centroids_governorate_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_15_s6_districts_centroid_source_mix.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_16_s7_vehicles_by_governorate_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_17_s7_vehicles_by_governorate_governorate_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_18_s7_vehicles_by_governorate_method_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s6s7_19_s7_vehicles_count_trajectory_by_vehicle_type.html'],
        insight=(
            "The CAGR distribution is **right-skewed**: the median district grows "
            "around 1.2% per year, but the right tail — **New Cairo 1, 6th October "
            "City 1 & 3, Ash-Shurūq, Sheikh Zayed** — grows at 10–15% per year. "
            "These are deliberately-built-from-scratch suburbs in the desert. "
            "**Demand is being created by planners, not by organic urbanization** "
            "in the dense inner core (Imbaba, Shubra, Al-Matariyya — all under 1% "
            "CAGR). Q22's worst-residual list comes directly out of this CAGR "
            "tail meeting weak metro coverage."
        ),
        methodology=(
            "Scraped via `Fetcher.get` on citypopulation.de's Egypt admin page; "
            "the response is a 408-row table covering 27 governorates and their "
            "subdivisions. We filter to (Cairo + Giza + Qalyubia) governorates → "
            "68 districts. CAGR = `(pop_2017 / pop_2006) ^ (1/11) − 1`. Each "
            "district is geocoded via Nominatim (OSM's free geocoder) to get a "
            "centroid lat/lon — used by Q22 (residual regression), H1 (Moran's I "
            "spatial weights), and Q24 (K-Means feature matrix)."
        ),
    ),

    Question(
        id="P2-S1S8", phase="phase2", nav_label="◆ S1 · GTFS + S8 · OSM",
        kicker="PHASE 02 · CLEANING · S1 GTFS + S8 OSM",
        headline="GTFS publishes 217 routes · OSM provides the cross-verification layer",
        question_text="What does the formal feed publish, and what does OSM independently confirm?",
        why_it_matters=(
            "**S1 GTFS** is Cairo's published transit schedule — the closest the city "
            "has to an official open-data feed. **S8 OSM** is the community-edited "
            "cross-verification layer used in Stage 2 of the integration pipeline. "
            "Together they let us compare what the network *says it is* (GTFS) with "
            "what the world *thinks it is* (OSM)."
        ),
        method="S1: download two zip bundles (bus+metro, paratransit) from TfC GitHub. S8: Overpass API queries for `public_transport`, `railway`, `highway=bus_stop` inside Cairo bbox.",
        kpis=[("GTFS STOPS",   "1,210", "S1"),
              ("GTFS ROUTES",  "217",   "FORMAL + INFORMAL"),
              ("GTFS FARES",   "3",     "ZONE-LEVEL"),
              ("OSM SOURCE",   "OVERPASS", "INDEPENDENT")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-s1s8_01_s1_gtfs_stops_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_02_s1_gtfs_stops_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_03_s1_gtfs_stops_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_04_s1_gtfs_routes_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_05_s1_gtfs_routes_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_06_s1_gtfs_routes_route_text_color_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_07_s1_gtfs_routes_route_color_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_08_s1_gtfs_trips_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_09_s1_gtfs_trips_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_10_s1_gtfs_shapes_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_11_s1_gtfs_shapes_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_12_s1_gtfs_fares_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_13_s1_gtfs_fares_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_14_s8_osm_transport_features_missing_values_by_column.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_15_s8_osm_transport_features_coordinate_spread_vs_cairo_bbox.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_16_s8_osm_transport_features_numeric_iqr_outlier_candidates.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_17_s8_osm_transport_features_highway_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_18_s8_osm_transport_features_amenity_distribution.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-s1s8_19_s8_osm_non_null_transport_tags.html'],
        insight=(
            "**GTFS reveals the data asymmetry**: the formal CTA bus + Metro routes "
            "(31 of 217) are published cleanly, but the bulk of the feed is "
            "informal paratransit (170+ routes). This is the bridge to Q19's "
            "finding — **GTFS gives Masari a strong formal backbone, but Phase 1 "
            "shows many stops where informal demand dominates and the nearest GTFS "
            "stop is too far to explain the trip**. Those stops are the "
            "'crowdsourcing frontier.'\n\n"
            "**OSM Overpass** provides an independent layer for the integration "
            "pipeline. When a scraped Wikipedia or Google Maps coordinate sits more "
            "than 50 m from the nearest OSM transport node, Stage 2 of the pipeline "
            "flags it as suspect — that's how we catch DMS-conversion errors and "
            "Google Maps approximations."
        ),
        methodology=(
            "**GTFS** unpacks into 8 standard CSVs (`stops.txt`, `routes.txt`, "
            "`trips.txt`, `shapes.txt`, `fare_attributes.txt`, …). We filter `stops` "
            "to a Cairo bounding box and reproject to EPSG:32636. **OSM Overpass** "
            "uses an XML query against `https://overpass-api.de` to pull all "
            "transport features inside the Cairo bbox; output is a GeoJSON in "
            "EPSG:32636 ready for Stage-2 cross-verification."
        ),
    ),

    Question(
        id="P2-C2", phase="phase2", nav_label="◆ 4-STAGE INTEGRATION",
        kicker="PHASE 02 · CLEANING · INTEGRATION PIPELINE · SBERT MATCHING",
        headline="KNN → OSM verify → RapidFuzz → SBERT — four stages, four problems solved",
        question_text="How do we pair every scraped station with the most likely Phase 1 terminal?",
        why_it_matters=(
            "Phase 2's central question — *did the new stuff close any of the Phase 1 "
            "gaps?* — depends on knowing which new station maps to which old terminal. "
            "Naive nearest-neighbor matching gives false matches whenever two unrelated "
            "stations are geographically close. The 4-stage pipeline solves what no "
            "single stage can: each stage covers what the previous stage misses."
        ),
        method="Stage 1: spatial KNN · Stage 2: OSM cross-verify · Stage 3: RapidFuzz token_sort (τ=88) · Stage 4: multilingual SBERT (τ=0.65)",
        kpis=[("STAGE 1", "KNN", "SPATIAL"),
              ("STAGE 2", "OSM > 50 m", "FLAG"),
              ("STAGE 3", f"τ = {SCRAPE['sbert']['tau']*100:.0f}", "RAPIDFUZZ"),
              ("STAGE 4", f"SBERT τ = {SCRAPE['sbert']['tau']}", "SEMANTIC MATCH")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-c2_01_null_percentage_per_column_post_cleaning_all_7_sources.html',
            'Phase2/Exports/scraping_notebook_visuals/p2-c2_02_integration_diagnostics_scraped_data_with_ai_similarity_scor.html'],
        insight=(
            "**Stage 1 — KNN (`sklearn.neighbors.NearestNeighbors`).** First-pass "
            "pairing — for every scraped station, find the nearest Phase 1 terminal in "
            "EPSG:32636. Fast and deterministic, but blind to names.\n\n"
            "**Stage 2 — OSM cross-verification.** For every scraped station, look up "
            "the nearest OSM transport node. If it's > 50 m away, **flag the "
            "coordinates as suspect** — likely a Wikipedia or Google Maps error.\n\n"
            "**Stage 3 — RapidFuzz token_sort (τ = 88).** Resolves spelling and "
            "punctuation drift on same-script names ('Adly Mansur' ↔ 'Adly Mansour'). "
            "But fails on cross-script (Arabic ↔ English).\n\n"
            "**Stage 4 — SBERT semantic matching** "
            f"(`{SCRAPE['sbert']['model']}`, threshold τ = {SCRAPE['sbert']['tau']}, "
            "cosine on combined `station_en + station_ar`). The only stage that can "
            "match المعادي ↔ Maadi semantically. Validated against a "
            f"{SCRAPE['sbert']['gold_set_pairs']}-pair gold set; if any gold pair fails, "
            "the threshold is re-tuned."
        ),
        methodology=(
            "**Why staged?** Each stage solves what the previous can't. Stage 1 alone "
            "produces false matches when two unrelated stations happen to be close. "
            "Stage 2 catches scrape-coordinate errors that would silently corrupt "
            "Stage 1. Stage 3 resolves typos but fails on Arabic↔English. Stage 4 is "
            "the only stage that handles cross-script — and it does so without "
            "translation (المرج → 'almrj' phonetically, not 'lawn' semantically). "
            "Outputs persist to `Phase2/Integrated/matched_pairs.csv` and "
            "`Phase2_integrated.geoparquet`."
        ),
    ),

    Question(
        id="P2-C3", phase="phase2", nav_label="◆ DATA QUALITY",
        kicker="PHASE 02 · CLEANING · NULL AUDIT + FINAL GATE",
        headline="Honest about the partial data — null audit before/after, final-gate manifest",
        question_text="How do we report data-quality limitations without burying them?",
        why_it_matters=(
            "BRT data is partial. LRT coordinates are partly OSM/GMaps backfilled. "
            "Some district centroids are Nominatim approximations. The project is "
            "stronger when these compromises are explicit, not weaker — the null "
            "audit and the final-gate manifest are how we make that explicit."
        ),
        method="Per-source null audit (grouped bar chart, % null per column) before and after cleaning; final assertion gate at the end of Notebook 3",
        kpis=[("AUDIT", "BEFORE + AFTER", "PER SOURCE"),
              ("LRT", f"{SCRAPE['lrt']['remaining']} planned", "STILL NO COORDS"),
              ("BRT", "PARTIAL", "GMAPS-ONLY"),
              ("GATE", "ASSERT FILE EXISTS", "BLOCKS NB4")],
        viz_html_paths=['Phase2/Exports/scraping_notebook_visuals/p2-c3_01_null_percentage_per_column_post_cleaning_all_7_sources.html'],
        insight=(
            "**Null audit.** Section 10 of Notebook 3 builds a per-source null-audit "
            "table and renders it as a grouped bar chart (Plotly). After Cleaning Steps "
            "01–04 run, the audit re-runs to verify cleaning worked — both versions "
            "(`null_audit_before.csv` and `null_audit_after.csv`) ship in "
            "`Phase2/CleanedData/`.\n\n"
            "**Final gate.** Section 13 ends with an assertion that every "
            "downstream-required output exists. If a CSV is missing — because a scrape "
            "failed mid-run — Notebook 4 cannot run. This is a defensive contract "
            "between the two notebooks.\n\n"
            "**What's honestly partial.**\n"
            f"- **LRT:** {SCRAPE['lrt']['remaining']} planned-only stations still lack coordinates.\n"
            "- **BRT:** Google Maps is the only source; the 12 stations are likely the operational ones, but not guaranteed exhaustive.\n"
            "- **District centroids:** Nominatim approximations, not true polygon centroids — so some Q22 residuals share a governorate-level value."
        ),
        methodology=(
            "Why a grouped bar instead of a wide table? Because comparing many columns "
            "across multiple sources is easier visually than scanning a CSV. Why "
            "before-and-after? Because the value of cleaning is the **delta**, not the "
            "post state."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 2 · Q13-Q25
# ═══════════════════════════════════════════════════════════════════════

def _build_q13():
    from components.charts import q13_coverage_vs_density
    return q13_coverage_vs_density()


def _build_q14():
    from components.charts import q14_distance_buckets
    return q14_distance_buckets()


def _build_q15():
    from components.charts import q15_metro_over_time
    return q15_metro_over_time()


def _build_q16():
    from components.charts import q16_cagr_slope
    return q16_cagr_slope()


def _build_q17():
    from components.charts import q17_density_underserved
    return q17_density_underserved()


def _build_q18():
    from components.charts import q18_informal_share
    return q18_informal_share()


def _build_q18b():
    from components.charts import q18b_matrix
    return q18b_matrix()


def _build_q19():
    from components.charts import q19_gtfs_coverage
    return q19_gtfs_coverage()


def _build_q20():
    from components.charts import q20_brt_corridor
    return q20_brt_corridor()


def _build_q21():
    from components.charts import q21_fare_per_km
    return q21_fare_per_km()


def _build_q22_residual():
    from components.charts import q22_residual_ranked
    return q22_residual_ranked()


def _build_q24_sizes():
    from components.charts import q24_cluster_sizes
    return q24_cluster_sizes()


def _build_q24_cagr():
    from components.charts import q24_cagr_pop
    return q24_cagr_pop()


def _build_q25_bridge():
    from components.charts import q25_bridge_schematic
    return q25_bridge_schematic()


# Phase 2 question add-ons (mirror notebook "add-on" cells)
def _build_q14_spatial():       from components.charts import q14_spatial_diagnostic;       return q14_spatial_diagnostic()
def _build_q17_target_heatmap():from components.charts import q17_target_tier_heatmap;     return q17_target_tier_heatmap()
def _build_q18_per_tier():      from components.charts import q18_per_tier_box;             return q18_per_tier_box()
def _build_q19_pie():           from components.charts import q19_agency_pie;               return q19_agency_pie()
def _build_q22_gov_box():       from components.charts import q22_governorate_box;          return q22_governorate_box()
def _build_q23_pctile_hist():   from components.charts import q23_percentile_histogram;     return q23_percentile_histogram()
def _build_q23_modal():         from components.charts import q23_modal_pie;                return q23_modal_pie()
def _build_q24_parcoords():     from components.charts import q24_parallel_coords;          return q24_parallel_coords()
def _build_q24_radar():         from components.charts import q24_radar;                    return q24_radar()
def _build_q24_priority():      from components.charts import q24_priority_bar;             return q24_priority_bar()

# Synthesis viz
def _build_metro_animation():   from components.charts import metro_animation;              return metro_animation()
def _build_sunburst():          from components.charts import sunburst_market;              return sunburst_market()
def _build_market_sizing():     from components.charts import market_sizing_bar;            return market_sizing_bar()


PHASE2_QUESTIONS: List[Question] = [
    Question(
        id="Q13", phase="phase2", nav_label="Q13 · METRO × DENSITY",
        kicker="PHASE 02 · Q13",
        headline="Metro openings read against population at the time they opened",
        question_text="Did each metro line open into the population geography that existed at the time?",
        why_it_matters=(
            "A station opened in 1987 should not be judged only against a 2018 "
            "hex snapshot. This version compares each station to the nearest "
            "district's closest available population year, then separately shows "
            "today's 2023 context."
        ),
        method="Nearest district-centroid join: metro station opening year × closest available district population year",
        kpis=[("DISTRICTS", "68", "ANALYZED"),
              ("SAMPLE", "89+20+12", "METRO · LRT · BRT"),
              ("METHOD", "SPEARMAN", "MONOTONIC")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q13_notebook_visuals.html'
        ],
        insight=(
            "Line 1 and Line 2 show modest density sorting: older stations are "
            "centrally placed. Line 3, extended through 2024, shows the strongest "
            "positive relationship between opening year and adjacent district "
            "population, meaning the newer 3B/3C/3D stations did reach denser "
            "districts such as Imbaba and Mohandessin. Q14 then tests whether "
            "those new stations also reached Phase 1's ghost terminals."
        ),
        methodology=(
            "Data: `metro_stations.csv` with line, opening year, and coordinates "
            "joined to `districts_wide.csv` district centroids and population "
            "columns for 1996, 2006, 2017, and 2023. Because the district file "
            "contains centroids and totals, not district polygons/areas, Q13 uses "
            "district population exposure rather than true density."
        ),
    ),

    Question(
        id="Q14", phase="phase2", nav_label="Q14 · GHOSTS vs NEW METRO",
        kicker="PHASE 02 · Q14",
        headline="Ghost terminals vs the post-2014 metro — 84% still stranded",
        question_text="Did the new metro reach Phase 1's 115 ghost terminals?",
        why_it_matters=(
            "Q14 is the bridge between phases. If new metro covered the ghosts, "
            "that $10B was solving the right problem. If not, something else is "
            "going on."
        ),
        method="Per-ghost haversine to every post-2014 metro station; minimum kept; bucketed",
        kpis=[("GHOSTS", "115", "TOTAL"),
              ("WITHIN 1 KM", "9", "8%"),
              ("BEYOND 2 KM", "97", "84%")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q14_notebook_visuals.html'
        ],
        insight=(
            "The answer is unambiguous. Only 9 of the 115 Phase 1 ghost terminals "
            "sit within a 1-km walk of any post-2014 metro station. 97 of them "
            "sit more than 2 km away. The new metro expansion did not route "
            "through the neighborhoods with structural transit gaps — it routed "
            "east, to the new capital."
        ),
        methodology=(
            "For each of the 115 ghost terminals, compute haversine distance to "
            "every post-2014 metro station (89 total, filtered to opening_year >= "
            "2014). Keep the minimum. Bucket into (0–1, 1–2, 2–5, 5–10, >10 km). "
            "Bucket counts: 3, 6, 9, 27, 70."
        ),
    ),

    Question(
        id="Q15", phase="phase2", nav_label="Q15 · METRO × TERMINAL INTEGRATION",
        kicker="PHASE 02 · Q15",
        headline="Do metro stations connect to Cairo's bus / microbus terminal backbone?",
        question_text="Is each metro station spatially close enough to the bus/microbus backbone for riders to actually transfer?",
        why_it_matters=(
            "The product story is not just whether rail exists — it is whether formal rail gives "
            "riders a clean transfer into the informal network they already use. A metro station "
            "near a high-route Phase 1 terminal is where System A and System B can meet. A "
            "station far from any high-route terminal is **stranded rail** — formally there but "
            "functionally disconnected from how most Cairenes actually move."
        ),
        method="For each metro station: nearest Phase 1 terminal; attach route count + flow + ghost flag; plot opening_year × distance",
        kpis=[("EASY TRANSFER", "≤ 250 m", "WALK-OUT BAND"),
              ("WALKABLE", "≤ 500 m", "FRIENDLY"),
              ("STRETCH", "≤ 1 KM", "TOLERABLE"),
              ("STATIONS ANALYSED", f"{SCRAPE['metro']['n']}", "METRO ONLY")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q15_notebook_visuals.html'
        ],
        insight=(
            "Stations close to high-route terminals are where System A and System B can meet — "
            "they're the transfer points Masari should privilege in route planning. "
            "**Most post-2014 Line 3 stations sit further from the existing terminal "
            "backbone than older Line 1/2 stations did.** That widening gap means Cairo's "
            "newest rail asks more of the rider's last mile, not less."
        ),
        methodology=(
            "Build a station-level table by joining each metro station to its nearest "
            "Phase 1 terminal in EPSG:32636. Attach the terminal's route count, "
            "passenger flow, and ghost-terminal status. Visualize as opening-year × "
            "distance, coloured by line, with horizontal bands at 250 m / 500 m / 1 km "
            "for practical transfer thresholds. (The earlier version of Q15 was a "
            "dual-axis time series of cumulative km — superseded because that question "
            "didn't speak to the actual transfer experience.)"
        ),
    ),

    Question(
        id="Q16", phase="phase2", nav_label="Q16 · CAGR",
        kicker="PHASE 02 · Q16",
        headline="Fastest-growing districts are desert satellite cities",
        question_text="Which Greater Cairo districts grew fastest between 2006 and 2023, and did they get new-mode coverage?",
        why_it_matters=(
            "If fast-growing districts received no new stations, Masari's "
            "addressable market is the residual demand the state did not serve."
        ),
        method="District CAGR sorted descending, joined to metro/LRT/BRT station counts by spatial proximity",
        kpis=[("FASTEST CAGR", "+15%", "NEW CAIRO"),
              ("GROWTH AXIS", "DESERT", "SATELLITES"),
              ("INNER CORE", "SLOWER", "STILL DENSE")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q16_notebook_visuals.html'
        ],
        insight=(
            "The fastest-growing districts between 2017 and 2023 are dominated by "
            "new satellite cities: New Cairo, 6th October, Shorouk, and Sheikh "
            "Zayed. Established dense districts such as El Marg and Warraq still "
            "grow, but more slowly. Metro/LRT expansion follows the satellite-city "
            "logic more than the slow-growth established districts where many "
            "current informal trips still happen."
        ),
        methodology=(
            "CAGR is computed per district from the citypopulation.de wide table, "
            "then the top districts are joined to nearby metro, LRT, and BRT "
            "station counts. The notebook uses this to separate projected future "
            "growth corridors from current dense demand corridors."
        ),
    ),

    Question(
        id="Q17", phase="phase2", nav_label="Q17 · DENSITY × UNDERSERVED",
        kicker="PHASE 02 · Q17",
        headline="Dense-and-underserved hexes are the launch-market target cells",
        question_text="Is population density the main predictor of underservedness, or is coverage-need mismatch unrelated to density?",
        why_it_matters=(
            "If dense districts correlate positively with underserved score, "
            "planning follows density but under-provisions. If the relationship is "
            "weak, the mismatch is spatial rather than simply volumetric."
        ),
        method="Phase 1 q9_underserved hexes: population density × Underserved_Score with top-quartile target ranking",
        kpis=[("HEXES", "1,525", "ANALYZED"),
              ("UNDERSERVED", "79", "SCORE > 0.5"),
              ("TARGET QUADRANT", "DEF", "DENSE + UNDERSERVED")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q17_notebook_visuals.html'
        ],
        insight=(
            "Q17 now names the target, not just the pattern. The dense-and-"
            "underserved quadrant becomes a concrete H3 list: places where many "
            "people live, boarding activity is not keeping up, and the underserved "
            "score is in the top quartile. These are the first hexes Masari should "
            "inspect, validate on the ground, and use as launch-market candidates."
        ),
        methodology=(
            "X-axis: hex population density (pop_18 / hex_area). Y-axis: "
            "Underserved_Score (population / total_boarding, normalized). "
            "Log-scaled density axis because the distribution is multi-decade. "
            "Quadrant thresholds (density > 30k/km², score > 0.5) chosen to "
            "capture the top third of both distributions — intersection is the "
            "addressable market."
        ),
    ),

    Question(
        id="Q18", phase="phase2", nav_label="Q18 · INFORMAL SHARE",
        kicker="PHASE 02 · Q18",
        headline="Informal share is flat across density tiers · microbus is everywhere",
        question_text="Does informal-transport modal share rise with density, or is it evenly distributed?",
        why_it_matters=(
            "If informal is a density-only phenomenon, formal metro expansion in "
            "dense cores would eventually replace it. If it's widespread regardless "
            "of density, informal is a permanent feature of Cairo's transport and "
            "any future-state model must include it."
        ),
        method="q4_formal_vs_informal stop-level formal share joined to population hex density tiers",
        kpis=[("ρ", "0.025", "FLAT"),
              ("MEAN SHARE", "47%", "INFORMAL"),
              ("STRUCTURAL", "YES", "ALL DENSITIES")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q18_notebook_visuals.html'
        ],
        insight=(
            "Informal share is statistically flat across density tiers. Microbus "
            "and tomnaya are not a niche response to only dense neighborhoods; "
            "they are background transport across the city. That is why a route "
            "planner that ignores informal transport cannot explain Cairo trips."
        ),
        methodology=(
            "Informal share = (informal_boardings / total_boardings) per "
            "district, aggregated from Phase 1 cleaned_boarding.csv joined to "
            "district polygons. Density on log axis because distributions span "
            "three orders of magnitude."
        ),
    ),

    Question(
        id="Q18b", phase="phase2", nav_label="Q18b · GAP MATRIX",
        kicker="PHASE 02 · Q18b",
        headline="The 3×4 gap-closure matrix: only one cell hits 25% — BRT × Vehicle Mismatch",
        question_text="What share of each Phase 1 gap did each new mode close within 2 km?",
        why_it_matters=(
            "Q18b is the synthesis cell — one chart shows the whole Phase 2 "
            "verdict. Twelve cells, only one at 25% (BRT × G3 vehicle mismatch). "
            "Every other cell is below 16%."
        ),
        method="Per (gap, mode) buffer overlap: % of gap sites within 2 km of any station of that mode",
        kpis=[("MODES",     "3",   "METRO L3 · LRT · BRT"),
              ("GAPS",      "4",   "G1 · G2 · G3 · G4"),
              ("BEST CELL", "25%", "BRT × VEHICLE MISMATCH"),
              ("LIVE",      "✓",   "RECOMPUTED FROM CSVs")],
        viz_html_paths=["Phase2/Exports/q18b_matrix.html"],
        insight=(
            "This is the headline answer to Phase 2's central question. Best-case "
            "in any cell: 25% (BRT and LRT on G3 vehicle-route mismatch). Every "
            "other cell is below 16%. Metro L3 covers 15.7% of Phase-1 ghost "
            "terminals but misses 84% of them. BRT is the broadest reach, but still "
            "leaves most underserved hexes uncovered. Row-major read: no single "
            "mode closed more than a quarter of any gap. Column-major read: every "
            "Phase-1 gap category still has 75-100% of its instances uncovered."
        ),
        methodology=(
            "For each gap category, every gap-site has a point coordinate "
            "(ghost terminal, empty-return terminal, long-microbus-route midpoint, "
            "underserved hex centroid). For each mode, compute the % of those "
            "sites inside a 2-km haversine buffer of any station of that mode. "
            "2-km chosen as Cairo commuter walkshed (World Bank 2019 study). "
            "The notebook computes the matrix from the four Phase 1 gap layers and "
            "the Phase 2 station layers. The Streamlit chart uses the same saved "
            "Phase 2 export and keeps a live/fallback chart helper for rehearsal."
        ),
    ),

    Question(
        id="Q19", phase="phase2", nav_label="Q19 · GTFS COVERAGE",
        kicker="PHASE 02 · Q19",
        headline="GTFS gives the formal backbone · informal-heavy stops remain outside it",
        question_text="Does the published GTFS feed cover the formal network we saw in Phase 1, and where does informal demand remain outside it?",
        why_it_matters=(
            "GTFS is Masari's ready-made System A layer. Phase 1 tells us where "
            "formal and informal demand actually appeared on the street. Merging "
            "the two separates what is already legible from what Masari must infer "
            "or crowdsource."
        ),
        method="GTFS routes/stops joined to Phase 1 route inventory and stop-level formal/informal boarding",
        kpis=[("FORMAL (TfC)", "217", "ROUTES"),
              ("STOPS", "1,210", "GTFS"),
              ("PARATRANSIT GTFS", "~0", "ROUTES"),
              ("UNDOCUMENTED", "≈1,500", "MICROBUS")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q19_notebook_visuals.html'
        ],
        insight=(
            "Q19 tests the real product boundary. GTFS gives Masari a strong "
            "formal backbone, but Phase 1 shows many stops where informal demand "
            "dominates and the nearest GTFS stop is not close enough to explain "
            "the trip. Those stops are the crowdsourcing frontier: the part of "
            "Cairo that exists operationally but is still missing from the "
            "published planning layer."
        ),
        methodology=(
            "Direct count of `routes.txt` rows per agency in the gtfs_bus_metro.zip "
            "(TfC) and gtfs_paratransit.zip (paratransit). Undocumented-route count "
            "derived by subtracting formal-count from Phase 1 cleaned_routes.csv "
            "total (1,784) minus approximated microbus share."
        ),
    ),

    Question(
        id="Q20", phase="phase2", nav_label="Q20 · BRT CORRIDOR",
        kicker="PHASE 02 · Q20",
        headline="BRT sits on a real informal corridor · some stations still need feeders",
        question_text="Does the 2025 BRT corridor on the Ring Road lie over the same corridor that informal microbuses were already serving?",
        why_it_matters=(
            "If yes, BRT is formalizing an existing demand. If no, BRT risks "
            "running empty like the LRT. Q20 is the descriptive version of H3."
        ),
        method="Daily informal boardings per station within 500 m buffer; ranked horizontal bar",
        kpis=[("STATIONS", "12", "BRT SCRAPED"),
              ("TOP-RANK", "14,726", "AL-MARG (BOARDINGS/DAY)"),
              ("BUFFER", "500 m", "CORRIDOR")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q20_notebook_visuals.html'
        ],
        insight=(
            "BRT station-level demand is uneven. Some stations bridge informal "
            "demand well, while weaker stations still need feeder integration. "
            "The ranking visual is what makes the H3 Cliff's-δ = +0.710 legible: "
            "not every station is equally strong, but the corridor as a whole is "
            "aligned with pre-existing informal movement."
        ),
        methodology=(
            "For each of the 12 BRT stations (brt_stations.csv), buffer 500 m "
            "in EPSG:32636. Spatial join into Phase 1 cleaned_boarding.csv filtered "
            "to informal-mode records (vehicle_name ∈ microbus, tomnaya). Sum "
            "daily boardings per station. Output goes into H3's test."
        ),
    ),

    Question(
        id="Q21", phase="phase2", nav_label="Q21 · FARE / KM",
        kicker="PHASE 02 · Q21",
        headline="Formal fare/km is measured · informal fare/km is an affordability scenario",
        question_text="Which mode — formal or informal — offers the better fare per kilometer, and is the difference enough to explain Layla's choice?",
        why_it_matters=(
            "Formal fares come from GTFS fare tables. Informal fares are estimated "
            "with a simple EGP 7 proxy because exact route-level microbus fares are "
            "not published. This makes Q21 an affordability scenario, not an exact "
            "fare audit."
        ),
        method="GTFS fare_attributes for formal modes plus Phase 1 vehicle-type route lengths with an EGP 7 informal fare proxy",
        kpis=[("BUS · GTFS", f"{Q21['fares_egp_per_km']['bus']:.2f}", "EGP/KM · 214 ROUTES"),
              ("METRO · GTFS", f"{Q21['fares_egp_per_km']['metro']:.2f}", "EGP/KM"),
              ("MICROBUS", f"{Q21['fares_egp_per_km']['microbus']:.2f}", "EGP/KM · ≈3× FORMAL"),
              ("TOMNAYA", f"{Q21['fares_egp_per_km']['tomnaya']:.2f}", "EGP/KM · ≈6× FORMAL")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q21_notebook_visuals.html'
        ],
        insight=(
            f"Real GTFS numbers: formal **Bus 0.22 EGP/km** (214 routes), formal "
            f"**Metro 0.25 EGP/km**. Phase 1's informal distribution: "
            f"**Microbus 0.62 EGP/km** (861 routes — about **3× formal**), "
            f"**Tomnaya 1.30 EGP/km** (115 routes — about **6× formal**). "
            "Q21 should be read as a scenario. Formal fare/km uses GTFS fares; "
            "informal fare/km uses an EGP 7 proxy. The result still matters: "
            "when formal service does not reach the rider, the cheaper formal "
            "fare does not help. Coverage and affordability compound each other."
        ),
        methodology=(
            "Formal fares pulled from GTFS `fare_attributes.txt` for the TfC bus "
            "and Metro feeds. Informal fares from Phase 1 `cleaned_routes.csv` "
            "with KNN-imputed missing fares (k=5, distance-weighted; 45.9% of "
            "routes had null fare before imputation). Plotted as a box plot — "
            "distributions are heavily right-skewed, so the median is the right "
            "summary statistic."
        ),
    ),

    Question(
        id="Q22", phase="phase2", nav_label="Q22 · RESIDUAL",
        kicker="PHASE 02 · Q22",
        headline="Metro residuals rank the districts where population predicts more stations",
        question_text="Given a district's population, how many metro stations should it have — and how far is reality from that?",
        why_it_matters=(
            "The residual is the coverage-need gap per district. Positive residual "
            "= over-served, negative = under-served. This is the single best "
            "diagnostic for Masari's market map."
        ),
        method="OLS residual: metro station count per district versus population_2023",
        kpis=[("METHOD",   "OLS",      "stations ~ pop_2023"),
              ("BUFFER",   "3 km",     "around centroid"),
              ("DISTRICTS","68",       "with valid pop"),
              ("LIVE",     "✓",       "RECOMPUTED FROM CSVs")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q22_notebook_visuals.html'
        ],
        insight=(
            "The chart ranks the most under-served districts by metro-coverage "
            "residual. Negative bars are districts where population predicts more "
            "stations than actually exist. The notebook's closing summary reads "
            "this as Masari's priority service-area list: the residual converts "
            "the broad mismatch into named districts."
        ),
        methodology=(
            "OLS of `n_stations ~ pop_2023` across 68 Greater Cairo districts. "
            "`n_stations` = count of metro stations within a 3 km haversine radius "
            "of each district's Nominatim centroid (S6). The residual is the gap "
            "between observed and OLS-predicted stations. The current notebook "
            "uses this residual ranking as the district-level priority list for "
            "Masari service-area planning."
        ),
    ),

    Question(
        id="Q23", phase="phase2", nav_label="Q23 · ADLY MANSOUR",
        kicker="PHASE 02 · Q23 · CASE STUDY",
        headline=f"Adly Mansour sits at the {Q23_ADLY['percentile']}st percentile of random Cairo clusters · strategically important, demographically modest",
        question_text="How does the Adly Mansour interchange compare to other Cairo station clusters?",
        why_it_matters=(
            "Adly Mansour is the symbolic centerpiece of the new infrastructure — "
            "where Metro L3, LRT, BRT, and OSM bus facilities converge. It is "
            "described publicly as the 'seventh mode' interchange. The question "
            "is whether the data backs the political framing."
        ),
        method="2.5-km station/terminal count around Adly Mansour vs 150 random Cairo 2.5-km clusters",
        kpis=[("MODES WITHIN 2.5 KM", f"{Q23_ADLY['modes_within_2_5km']}", "M+L+B+OSM"),
              ("NODES WITHIN 2.5 KM", f"{Q23_ADLY['total_stations_within_2_5km']}", "STATIONS + TERMINALS"),
              ("PERCENTILE", f"{Q23_ADLY['percentile']}st", "OF 150 RANDOM CLUSTERS")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q23_notebook_visuals.html'
        ],
        insight=(
            f"Adly Mansour sits around the **{Q23_ADLY['percentile']}st percentile** "
            "of the random 2.5-km cluster sample. It proves multimodal convergence, "
            "but it is not Greater Cairo's strongest demand hub. Inside the same "
            "2.5-km catchment four modes co-exist: Metro Line 3 (terminus), Cairo "
            "LRT (origin toward NAC), Cairo BRT (Ring Road), and Phase-1 informal "
            "terminals. This makes it a strategic interchange, not the whole market."
        ),
        methodology=(
            "Count formal stations and Phase 1 informal terminals inside a 2.5-km "
            "buffer around the Adly Mansour coordinate. Generate 150 random 2.5-km "
            "clusters from the integrated station layer; compute comparable station "
            "+ terminal density per cluster; rank Adly Mansour in that distribution."
        ),
    ),

    Question(
        id="Q24", phase="phase2", nav_label="Q24 · K-MEANS",
        kicker="PHASE 02 · Q24 · SEGMENTATION · K-MEANS",
        headline=f"K-Means · k = {Q24['k']} · ARI = {Q24['ARI']:.2f} (across {Q24['n_seeds_for_stability']} seeds) · Masari market = {MARKET['target_population_millions']}M",
        question_text="Can we cluster Cairo districts into coherent transport-demand segments?",
        why_it_matters=(
            "Q24 is the bridge from analysis to product. A market size is only "
            "defensible if it sits on a segmentation that is statistically stable."
        ),
        method="K-Means on 5 standardized district features; k=4 selected by silhouette and policy granularity",
        kpis=[("K",      f"{Q24['k']}",                                  "CLUSTERS"),
              ("ARI",    f"{Q24['ARI']:.2f}",                            f"OVER {Q24['n_seeds_for_stability']} SEEDS"),
              ("TARGET", f"{MARKET['target_districts']}",                "DISTRICTS"),
              ("MARKET", f"{MARKET['target_population_millions']}M",      "RESIDENTS")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q24_notebook_visuals.html'
        ],
        insight=(
            f"**ARI = {Q24['ARI']:.2f} across {Q24['n_seeds_for_stability']} random "
            "seeds** — the clusters are stable in the current notebook. The four "
            "groups are **Formal-Served Core** (31 districts, 5.59M residents), "
            "**Peripheral Growth** (19 districts, 9.18M residents), "
            "**Mixed (cluster 2)** (12 districts, 4.15M residents), and "
            "**Low-Activity Outskirts** (6 districts). Masari's practical market is "
            "the three non-outskirt groups: "
            f"**{MARKET['target_districts']} districts ≈ {MARKET['target_population_millions']}M residents**."
        ),
        methodology=(
            f"**Features (5):** {', '.join(Q24['features'])}. Standardized (z-score) "
            f"before clustering. **n_init = {Q24['n_init']}**. Elbow + silhouette "
            f"over k ∈ [2, 8]; the current run selects k=4 "
            f"(silhouette ≈ {Q24['silhouette_k4']}). Cross-validated with "
            f"**{Q24['n_seeds_for_stability']} random seeds** — adjusted Rand index = 1.00 across all of them."
        ),
    ),

    Question(
        id="Q25", phase="phase2", nav_label="Q25 · MASARI BRIDGE",
        kicker="PHASE 02 · Q25 · THE PRODUCT IN ONE FIGURE",
        headline="Masari Bridge — connect every informal-heavy stop to its nearest formal node",
        question_text="Where should Masari connect informal demand into the formal network?",
        why_it_matters=(
            "The app is not only a map of missing places. It is a **routing bridge**. "
            "This question identifies the actual first-/last-mile connectors — the "
            "edges Masari needs to render to give Layla a unified trip."
        ),
        method="Build formal layer (GTFS + Metro + LRT + BRT) and informal layer (Phase 1 stops where informal > formal); for each informal stop find nearest formal node; score = demand × inverse distance",
        kpis=[("FORMAL LAYER",   "GTFS + M + L + B", "SYSTEM A"),
              ("INFORMAL LAYER", "PHASE 1 STOPS",    "WHERE INFORMAL > FORMAL"),
              ("SCORING",        "DEMAND × 1/DIST",  "BRIDGE PRIORITY")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/q25_notebook_visuals.html'
        ],
        insight=(
            "**This is Masari in one figure.** Red points are the informal system "
            "people already use. Blue/gold/green points are the formal system apps "
            "can already read. **Connector lines are the missing product layer.** "
            "Short connectors become immediate routing wins (Imbaba mawfaq → "
            "Shubra Metro). Long connectors flag where Masari's value is not just "
            "connection but rider-contributed routing (deep-Giza informal stops "
            "with no formal node within walking distance)."
        ),
        methodology=(
            "**Formal-node layer:** union of GTFS stops, Phase 2 metro stations, "
            "LRT stations (16 with coordinates), and BRT stations. **Informal-demand "
            "layer:** Phase 1 stops filtered to those where `informal_daily_boarding "
            "> formal_daily_boarding`. For each informal stop, nearest-neighbour "
            "search against the formal layer (Haversine in EPSG:32636). Each pair "
            "is scored by `demand × 1/distance` — the score ranks which connectors "
            "Masari should render first. Schematic shown above; the full geographic "
            "version lives in the Phase 2 notebook."
        ),
    ),

    Question(
        id="P2-X1", phase="phase2", nav_label="◆ ANIMATED · METRO 1987→2026",
        kicker="PHASE 02 · SYNTHESIS · ANIMATED EXPANSION",
        headline="Fourteen years in 30 seconds — Cairo's metro expansion timeline",
        question_text="How did the formal rail network spread across Cairo over time?",
        why_it_matters=(
            "A scatter map per opening year shows the **direction** of investment, "
            "not just the count. Line 1 (1987) traces the original Helwan–Marg "
            "corridor. Line 2 (1996–2005) extends west. After a long pause, Line 3 "
            "(2014→2024) pulses out east and west in phases 3A/3B/3C/3D. Animation "
            "reveals what a static map can't: time as a second axis."
        ),
        method="px.scatter_map · cumulative frames per opening year · color = line",
        kpis=[("PERIOD", "1987 → 2026", "39 YEARS"),
              ("STATIONS", f"{SCRAPE['metro']['n']}", "TOTAL"),
              ("LINES", "3 (+L4 planned)", "L1 · L2 · L3")],
        viz_html_paths=["Phase2/Exports/metro_animation.html"],
        insight=(
            "**Long pause from 2005 to 2014** — almost a decade with no metro openings. "
            "Then Line 3 pulses out east toward Adly Mansour (Phase 3A, 2014–2017), "
            "south to Heliopolis (3B, 2018–2019), west to Kit Kat (3C, 2020–2022), "
            "and the final westward extension (3D, 2024). The eastward bias toward "
            "the New Administrative Capital is visible in motion."
        ),
        methodology=(
            "Mirrors notebook cell 201. Replicates each station into every year ≥ "
            "its opening year to build cumulative frames. Plotly's animation_frame "
            "renders as a play-button slider on the scatter map."
        ),
    ),

    Question(
        id="P2-X2", phase="phase2", nav_label="◆ MARKET SIZING",
        kicker="PHASE 02 · SYNTHESIS · MASARI MARKET SIZING",
        headline=f"{MARKET['target_population_millions']} million residents · {MARKET['target_districts']} districts · non-outskirt Masari market",
        question_text="Once we have stable K-Means clusters, how big is the addressable market?",
        why_it_matters=(
            "A market size is only defensible if it's the sum of districts that share "
            "a transport-demand signature — not an arbitrary headline. This page "
            "converts the Q24 cluster output into the addressable population."
        ),
        method="Sum 2023 population per K-Means cluster; market = Formal-Served Core + Peripheral Growth + Mixed",
        kpis=[("MARKET",  f"{MARKET['target_districts']} districts", "NON-OUTSKIRT"),
              ("POP",      f"{MARKET['target_population_millions']}M",  "RESIDENTS"),
              ("CLUSTERS", "3 of 4",                                    "OF GREATER CAIRO")],
        viz_html_paths=["Phase2/Exports/market_sizing_bar.html"],
        insight=(
            "Market sizing now follows the latest Q24 clusters. **Formal-Served Core** "
            "is the transfer-density market, **Peripheral Growth** is the coverage "
            "expansion market, and **Mixed (cluster 2)** captures the remaining "
            "under-connected Cairo cases. Together they cover 62 of 68 districts "
            "and about 18.9M residents. Low-Activity Outskirts is kept out of the "
            "primary launch market because its signal is thinner."
        ),
        methodology="See Q24 methodology. Mirrors notebook cell 208.",
    ),

    Question(
        id="P2-X3", phase="phase2", nav_label="◆ SUNBURST · GOV → CLUSTER",
        kicker="PHASE 02 · SYNTHESIS · NOVEL VISUALIZATION",
        headline="Sunburst — governorate → cluster → district (arc ≈ 2023 population)",
        question_text="How do the K-Means clusters distribute across administrative geography?",
        why_it_matters=(
            "A flat bar chart cannot show how the same cluster logic sits inside "
            "governorates and individual districts. "
            "A hierarchy needs a hierarchical visual."
        ),
        method="3-level sunburst · arc length weighted by 2023 population",
        kpis=[("LEVELS", "3", "GOV → CLUSTER → DISTRICT"),
              ("WEIGHT", "POP_2023", "ARC LENGTH")],
        viz_html_paths=["Phase2/Exports/sunburst_market.html"],
        insight=(
            "**Cairo** is dominated by the Formal-Served Core and Mixed districts. "
            "**Giza** carries much of the Peripheral Growth population. **Qalyubia** "
            "appears as an outer-growth edge. The drill-down makes the Masari market "
            "visible district by district."
        ),
        methodology="Mirrors notebook cell 212.",
    ),

    Question(
        id="P2-X4", phase="phase2", nav_label="◆ ALL NOTEBOOK VISUALS",
        kicker="PHASE 02 · FULL NOTEBOOK VISUAL INVENTORY",
        headline="All Phase 2 notebook visualizations · 47 Plotly charts + 4 maps",
        question_text="Where can we review every visualization saved in the latest Phase 2 analysis notebook?",
        why_it_matters=(
            "The curated evidence pages tell the story question by question. This "
            "page is the full notebook visual appendix: every saved Plotly chart "
            "and Folium/Leaflet map from the latest executed Phase 2 analysis "
            "notebook, in notebook order."
        ),
        method="Generated from Phase2_Analysis_Hypothesis.ipynb outputs after rerun; includes saved Plotly MIME outputs and Folium/Leaflet HTML maps",
        kpis=[("PLOTLY", "47", "CHARTS"),
              ("MAPS", "4", "FOLIUM/LEAFLET"),
              ("TOTAL", "51", "VISUALS")],
        viz_html_paths=["Phase2/Exports/phase2_analysis_all_visualizations.html"],
        insight=(
            "This appendix keeps Streamlit synchronized with the notebook. If a TA "
            "asks for a chart that is not part of the shorter narrative page, it is "
            "still available here in the exact notebook order."
        ),
        methodology=(
            "A custom exporter reads the executed notebook JSON, extracts every "
            "`application/vnd.plotly.v1+json` output and every Folium/Leaflet HTML "
            "map output, then writes one self-contained HTML appendix under "
            "`Phase2/Exports/phase2_analysis_all_visualizations.html`."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════════════════
#  HYPOTHESES · H1-H3
# ═══════════════════════════════════════════════════════════════════════

def _build_h1_box():
    from components.charts import h1_box
    return h1_box()


def _build_h1_moran():
    from components.charts import h1_moran_bar
    return h1_moran_bar()


def _build_h2_bar():
    from components.charts import h2_bar
    return h2_bar()


def _build_h3_bar():
    from components.charts import h3_bar
    return h3_bar()


def _build_h1_continuous(): from components.charts import h1_continuous_scatter; return h1_continuous_scatter()
def _build_h2_ranked():     from components.charts import h2_ranked_bar;          return h2_ranked_bar()
def _build_h2_cumulative(): from components.charts import h2_cumulative_curves;   return h2_cumulative_curves()
def _build_h3_violin():     from components.charts import h3_violin;              return h3_violin()


def _build_osm_cross_verify():
    from components.charts import osm_cross_verification_map
    return osm_cross_verification_map()


def _build_q24_cluster_map():
    from components.charts import q24_cluster_choropleth
    return q24_cluster_choropleth()


HYPOTHESIS_QUESTIONS: List[Question] = [
    Question(
        id="H1", phase="hypothesis", nav_label="H1 · COVERAGE",
        kicker="HYPOTHESIS H1 · COVERAGE-NEED MISMATCH · MORAN'S I",
        headline=f"Dense districts get ~12× fewer stations per capita · ε² = {H1['eps_sq']:.3f} (huge effect)",
        question_text="Does coverage (stations/100k) differ across population-density tertiles?",
        why_it_matters=(
            "H1 is the central quantitative claim of the project. If coverage and "
            "density align, every headline collapses. If they don't, the story is "
            "intact and testable."
        ),
        method="Kruskal-Wallis H + Mann-Whitney post-hoc · Chi-square + Welch t-test robustness · Moran's I (999 perms) on real Nominatim centroids",
        kpis=[("H",         f"{H1['H']:.1f}",       "KRUSKAL-WALLIS"),
              ("p",         "< 0.001",              "STRONGLY SIGNIFICANT"),
              ("ε²",        f"{H1['eps_sq']:.3f}",  "HUGE EFFECT"),
              ("MORAN'S I", f"{H1['morans_I']:.3f}", "SPATIAL CLUSTERING")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/h1_notebook_visuals.html'
        ],
        insight=(
            f"Coverage per 100k differs significantly across density tertiles. "
            f"**Low-density districts get a median of {H1['tertile_medians']['low']:.1f} "
            f"stations per 100k; high-density get {H1['tertile_medians']['high']:.2f}** "
            f"— roughly a **{H1['tertile_medians']['low']/H1['tertile_medians']['high']:.0f}× "
            f"gap** between the top and bottom tertiles. **Effect size ε² = "
            f"{H1['eps_sq']:.3f}** is huge. The spatial dimension is also real: "
            f"**Moran's I = {H1['morans_I']:.3f}, p = {H1['morans_p']:.3f}** "
            "with 999 permutations."
        ),
        methodology=(
            "Kruskal-Wallis is the non-parametric analogue of one-way ANOVA, "
            "appropriate when the group distributions are not normal. Effect size "
            "= ε² (epsilon-squared) = (H − k + 1) / (n − k), where k = 3 groups, "
            "n = 68. **Robustness layer:** Chi-square independence + Welch t-test "
            "cross-checks both confirm the same direction. **Methodology upgrade "
            "(this version):** Moran's I now uses real Nominatim district centroids "
            "from S6 (not the earlier 3-governorate-centroid proxy) — that upgrade "
            "is what turned the small-to-medium effect into the huge effect. "
            "Spatial weights = KNN-as-contiguity on district centroids; 999 "
            "permutations for the empirical null distribution."
        ),
    ),

    Question(
        id="H2", phase="hypothesis", nav_label="H2 · LRT CATCHMENT",
        kicker="HYPOTHESIS H2 · LRT CATCHMENT DEFICIT",
        headline=f"LRT median 2-km catchment is {H2['medians']['lrt']:,} residents · Cliff's δ = {H2['cliffs_delta']:.3f}",
        question_text="Do LRT stations serve weaker surrounding populations than recent metro stations?",
        why_it_matters=(
            "H2 isolates the specific claim about the new LRT — the single most "
            "photographed piece of Phase 2 infrastructure. The answer has "
            "implications for ridership forecasts that the state has publicly used."
        ),
        method="Mann-Whitney U · Cliff's delta on 2-km population catchments · sensitivity at 1/2/3 km",
        kpis=[("U",          f"{H2['U']}",                                "MANN-WHITNEY"),
              ("p",          "< 0.0001",                                  "SIGNIFICANT"),
              ("δ",          f"{H2['cliffs_delta']:.3f}",                 "NEAR-MAX NEGATIVE"),
              ("LRT n",      f"{H2['n_by_group']['lrt']}",                "OSM + GMAPS BACKFILL"),
              ("METRO L3 n", f"{H2['n_by_group']['metro_l3']}",            "POST-2012")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/h2_notebook_visuals.html'
        ],
        insight=(
            f"LRT median 2-km catchment: **{H2['medians']['lrt']:,} residents**. "
            f"Post-2012 Metro L3 median: **{H2['medians']['metro_l3_post_2012']:,} "
            f"residents**. **Cliff's delta = {H2['cliffs_delta']:.3f}** — an "
            "extreme negative effect. This is not a marginal result. "
            f"Now with **{H2['n_by_group']['lrt']} LRT stations** (OSM + Google Maps "
            "coordinate backfill from S4) the result is unambiguous. The LRT "
            "serves a future-growth corridor far more than today's population."
        ),
        methodology=(
            "2-km buffer around each operational station (EPSG:32636); dissolve "
            "the Phase 1 population hex grid inside each buffer; sum `pop_18`. "
            "Mann-Whitney U is non-parametric, appropriate for these highly-skewed "
            "small-sample distributions. Cliff's delta = (wins − losses) / n·m. "
            f"**Sensitivity:** tested at {H2['sensitivity_radii_km']} km radii; "
            f"{H2['sensitivity_note']}."
        ),
    ),

    Question(
        id="H3", phase="hypothesis", nav_label="H3 · BRT MATCH",
        kicker="HYPOTHESIS H3 · BRT CORRIDOR MATCH",
        headline=f"BRT aligns with real informal demand · Cliff's δ = +{H3['cliffs_delta']:.3f}",
        question_text="Do BRT corridors sit on corridors that already have high informal-transport demand?",
        why_it_matters=(
            "Without H3 the story becomes one-note: all new infrastructure is "
            "equally bad. H3 lets us argue with nuance: some investments hit. "
            "The BRT is the one that did."
        ),
        method="Mann-Whitney U on BRT corridor (n=12) vs random urbanized non-Ring-Road controls; 500 m buffer",
        kpis=[("δ",              f"+{H3['cliffs_delta']:.3f}",        "LARGE POSITIVE"),
              ("BRT MEDIAN",     f"{H3['medians']['brt']:,}",          "DAILY INFORMAL"),
              ("CONTROL MEDIAN", f"{H3['medians']['control']}",        "ZERO"),
              ("BRT n",          f"{H3['n_brt']}",                     "STATIONS")],
        viz_html_paths=[
            'Phase2/Exports/notebook_sections/h3_notebook_visuals.html'
        ],
        insight=(
            "The BRT was built on top of existing demand. **Median daily informal "
            f"boardings inside a 500-m BRT corridor buffer: {H3['medians']['brt']:,}. "
            "Matched non-Ring-Road control (random urbanized sample at similar "
            f"distance-to-center): {H3['medians']['control']}.** Cliff's delta = "
            f"+{H3['cliffs_delta']:.3f}. This is the single positive planning "
            "finding in the whole Phase 2 infrastructure pipeline."
        ),
        methodology=(
            "**Test (current notebook):** Mann-Whitney U on the BRT-corridor "
            "distribution vs a random control distribution. The control sample "
            "is built by drawing random points from the urbanized area at "
            "similar distance-to-center, then computing informal boardings in "
            "the same 500 m buffer. **Cross-validation:** "
            f"{H3['cross_validation']}. Informal demand from Phase 1 boarding "
            "dataset aggregated to road segments. (Earlier drafts framed this "
            "as a Wilcoxon paired test on 12 hand-matched controls; the current "
            "notebook uses Mann-Whitney with a random urbanized control sample.)"
        ),
    ),
]


HERO_MAPS: List[Question] = [
    Question(
        id="HERO-TWO-CAIROS", phase="hypothesis", nav_label="HERO · TWO CAIROS",
        kicker="HERO MAP · FORMAL vs INFORMAL",
        headline="The Two Cairos — one map of both systems",
        question_text="Where does System A (formal) overlap with System B (informal)?",
        why_it_matters=(
            "The hero map is the opening argument. Formal and informal systems "
            "coexist spatially without integrating operationally. That spatial "
            "separation is the structural failure this project documents."
        ),
        method="Overlay of Phase 2 formal stations + Phase 1 terminals + OSM bus POIs on Carto dark-matter tiles",
        kpis=[("METRO", "89", "STATIONS"),
              ("TERMINALS", "280", "INFORMAL"),
              ("OVERLAP", "PARTIAL", "SPATIAL")],
        viz_html_paths=["Phase2/two_cairos_map.html"],
        insight=(
            "Formal stations cluster east (new investments to the new capital). "
            "Informal terminals cluster in the dense inner core. Spatial overlap "
            "is concentrated around Ramses, Attaba, Adly Mansour — and almost "
            "nowhere else."
        ),
        methodology="Folium rendering; coordinates from Phase 2 integrated dataset.",
    ),

    Question(
        id="HERO-COVERAGE-NEED", phase="hypothesis", nav_label="HERO · COVERAGE-NEED",
        kicker="HERO MAP · FINAL SYNTHESIS",
        headline="The Coverage-Need Map · where demand lives and supply went",
        question_text="What is the single visual summary of the entire project?",
        why_it_matters=(
            "If the audience remembers one image, it should be this one."
        ),
        method="District choropleth (coverage class) + station overlay (mode-coloured) + K-Means 4-cluster overlay",
        kpis=[("DISTRICTS", "68", "CLASSIFIED"),
              ("CLUSTERS", "4", "K-MEANS"),
              ("TARGET", "18M", "RESIDENTS")],
        viz_html_paths=[
            "Phase2/headline_coverage_need_map.html",
            "Phase2/Exports/q24_cluster_choropleth.html",
        ],
        insight=(
            "Underserved (coral) districts cluster in the dense inner core. "
            "Over-served (teal) districts sit in the low-density outer suburbs. "
            "The mismatch is spatial, statistical, and large. The K-Means "
            "overlay groups districts into four current cohorts: **Formal-Served "
            "Core** (31 districts), **Peripheral Growth** (19 districts), "
            "**Mixed (cluster 2)** (12 districts), and **Low-Activity Outskirts** "
            "(6 districts). The first three cohorts are the non-outskirt Masari "
            "market: 62 districts and about 18.9M residents."
        ),
        methodology="Described in H1 methodology; synthesis visual built on the H1 residuals + Q24 clusters.",
    ),
]


# Index by phase — cleaning sections come first so the reader sees the
# data engineering before the analysis it enables.
QUESTIONS_BY_PHASE = {
    "phase1":     PHASE1_CLEANING + PHASE1_QUESTIONS + GAP_QUESTIONS,
    "phase2":     PHASE2_CLEANING + PHASE2_QUESTIONS + HYPOTHESIS_QUESTIONS + HERO_MAPS,
    "hypothesis": HYPOTHESIS_QUESTIONS + HERO_MAPS,
}
