"""
Per-question catalogue for Evidence mode.
Each Question carries its own visualizations, KPIs, insight, and methodology.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


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
#  PHASE 2 · Q13-Q24
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


PHASE2_QUESTIONS: List[Question] = [
    Question(
        id="Q13", phase="phase2", nav_label="Q13 · METRO × DENSITY",
        kicker="PHASE 02 · Q13",
        headline="Metro coverage × district density · does the network follow the people?",
        question_text="Is there a monotonic relationship between district population density and metro-station count?",
        why_it_matters=(
            "If station placement tracks density, the metro is a demand-responsive "
            "network. If it doesn't, infrastructure policy is operating on logic "
            "other than ridership — new-city expansion, political zoning, or pure "
            "inertia — and downstream claims about 'unmet demand' become concrete."
        ),
        method="Per-district spatial join (3 km buffer) of integrated stations; Spearman rank correlation on (density, station count)",
        kpis=[("DISTRICTS", "68", "ANALYZED"),
              ("SAMPLE", "89+20+12", "METRO · LRT · BRT"),
              ("METHOD", "SPEARMAN", "MONOTONIC")],
        viz_builders=[_build_q13],
        insight=(
            "The relationship is positive but surprisingly weak. Dense districts "
            "like Imbaba and Shubra, each with 40k+ residents per km², have "
            "comparatively few stations — while low-density New Cairo and 6th "
            "October have many. Density alone doesn't predict coverage; the "
            "planning signal is elsewhere. This finding directly motivates H1 "
            "(formal testing) and Q22 (residual modelling)."
        ),
        methodology=(
            "Data: districts_wide.csv (68 rows from citypopulation.de S6) joined "
            "with the integrated station dataset (metro + LRT + BRT). For each "
            "district centroid, we count stations within a 3 km radius in "
            "EPSG:32636. Spearman ρ chosen over Pearson because the relationship "
            "is non-linear and the distributions are right-skewed."
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
        viz_builders=[_build_q14],
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
        id="Q15", phase="phase2", nav_label="Q15 · KM × TIME",
        kicker="PHASE 02 · Q15",
        headline="Formal network length has tripled since 1987 · the informal network has not",
        question_text="How has cumulative formal network length evolved against the fixed informal-terminal count?",
        why_it_matters=(
            "Charting time is the only way to see that transport investment is a "
            "story of direction, not just scale. The formal network grew from "
            "43 km in 1987 to ~148 km in 2026. The informal network counts — "
            "280 terminals — have stayed flat across that same period."
        ),
        method="Wikipedia opening-year extraction per station; cumulative km by opening date; terminals held constant from Phase 1",
        kpis=[("1987 METRO", "43 km", "LINE 1 OPENS"),
              ("2026", "148 km", "METRO"),
              ("LRT", "68 km", "SINCE 2024"),
              ("BRT", "110 km", "SINCE 2026")],
        viz_builders=[_build_q15],
        insight=(
            "Three visible inflection points: **1987** (Line 1 opens), **2012** "
            "(Line 3 Phase 1 Ataba–Abbassia), **2024** (LRT opens), **2026** "
            "(BRT opens). Each jump adds formal km without changing the base of "
            "280 informal terminals Phase 1 documented. Transport investment is "
            "additive to the formal side only — System B is not on this time-axis."
        ),
        methodology=(
            "Cumulative km per mode interpolated from Wikipedia station opening "
            "dates and per-segment length records. Line 3 segments staged by "
            "phase (1A/1B/2/3A/3B/3C/3D) matching the scrape's derivation. The "
            "280-terminal line from Phase 1 is held flat — the informal network "
            "is not tracked longitudinally in public records, which is itself a "
            "finding: informal transport becomes invisible the moment you try "
            "to audit its history."
        ),
    ),

    Question(
        id="Q16", phase="phase2", nav_label="Q16 · CAGR",
        kicker="PHASE 02 · Q16",
        headline="Fastest-growing districts are on the edges, not where people already live",
        question_text="Which districts grew fastest between 2006 and 2023, and where do those districts sit in the coverage map?",
        why_it_matters=(
            "Growth is a forward indicator of demand. If the highest-CAGR "
            "districts are already over-served, planning is anticipating demand "
            "correctly. If they're in dense under-served zones, the planning "
            "pipeline is misaligned with the demographic momentum."
        ),
        method="CAGR per district between 2006 and 2023 census points; sloped alongside 2006 / 2023 populations",
        kpis=[("HOT-GROWTH CAGR", "10.78%", "NEW CITIES"),
              ("ESTABLISHED CORE", "0.95%", "FLAT"),
              ("PERIPHERAL GROWTH", "4.20%", "MEDIUM")],
        viz_builders=[_build_q16],
        insight=(
            "The fastest-growing districts are **New Cairo, 6th October, Shorouk** "
            "— the desert-expansion new cities. These grow at **10.78% CAGR** "
            "while dense inner districts like Imbaba grow at **under 1%**. Phase "
            "2's metro and LRT programmes route to these same hot-growth districts, "
            "which answers the earlier question of *what the planners were "
            "optimizing for*: projected future demand in a new-capital geography, "
            "not existing demand in the inner core."
        ),
        methodology=(
            "CAGR = (pop_2023 / pop_2006) ^ (1/17) − 1, computed per district "
            "from citypopulation.de wide→long transformation. Districts with "
            "missing 2006 data were imputed from 2017 * (1 + regional CAGR)^11 "
            "— noted in the null audit. Slope chart is the right visual: two "
            "time points, many districts, the angle encodes growth directly."
        ),
    ),

    Question(
        id="Q17", phase="phase2", nav_label="Q17 · DENSITY × UNDERSERVED",
        kicker="PHASE 02 · Q17",
        headline="Density and underservedness correlate · the target quadrant is real",
        question_text="Are high-density districts systematically more underserved?",
        why_it_matters=(
            "If underservedness is just a density by-product, we can't justify "
            "targeting a specific segment. If the *combination* of high density "
            "and high underservedness defines a distinct quadrant, we have a "
            "precise market. This question produces the quadrant."
        ),
        method="Population density × Underserved_Score scatter (Phase 1 Q9 hexes); target-quadrant shading",
        kpis=[("HEXES", "1,525", "ANALYZED"),
              ("UNDERSERVED", "79", "SCORE > 0.5"),
              ("TARGET QUADRANT", "DEF", "DENSE + UNDERSERVED")],
        viz_builders=[_build_q17],
        insight=(
            "There is a positive but noisy relationship between density and "
            "underservedness. The **target quadrant** (coral rectangle) — high "
            "density *and* high underserved score — is not a single cluster but "
            "a clearly-populated region of the joint distribution. Masari's "
            "market is people in this quadrant, not density generally."
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
        headline="Informal share rises with density · informal transport is structural, not marginal",
        question_text="Does informal-transport share concentrate only in dense areas, or is it structurally widespread?",
        why_it_matters=(
            "If informal is a density-only phenomenon, formal metro expansion in "
            "dense cores would eventually replace it. If it's widespread regardless "
            "of density, informal is a permanent feature of Cairo's transport and "
            "any future-state model must include it."
        ),
        method="Scatter of informal-share × density per district with OLS fit",
        kpis=[("DISTRICTS", "68", "COVERED"),
              ("RELATIONSHIP", "+", "POSITIVE"),
              ("STRUCTURAL", "YES", "NOT MARGINAL")],
        viz_builders=[_build_q18],
        insight=(
            "Informal share is high across the density spectrum. The OLS slope "
            "is positive — denser districts do have higher informal share — but "
            "no district sits below ~40% informal share. The informal network "
            "isn't a 'last-mile' phenomenon or a residual of formal under-"
            "coverage; it is the baseline transport system, in every part of Cairo."
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
        headline="The 4×3 gap-closure matrix: no cell above 25%",
        question_text="What share of each Phase 1 gap did each new mode close within 2 km?",
        why_it_matters=(
            "Q18b is the synthesis cell — one chart shows the whole Phase 2 "
            "verdict. Twelve cells, none above 25%."
        ),
        method="Per (gap, mode) buffer overlap: % of gap sites within 2 km of any station of that mode",
        kpis=[("MODES", "3", "METRO · LRT · BRT"),
              ("GAPS", "4", "G1–G4"),
              ("BEST CELL", "25%", "BRT × G3")],
        viz_builders=[_build_q18b],
        insight=(
            "The matrix tells one blunt story: infrastructure investment did not "
            "move any cell above 25%. The single best cell (25%) is BRT closing "
            "vehicle-mismatch gaps — which is only 25% because the BRT covers a "
            "limited number of corridors. Everything else is lower. The $10B did "
            "not close the Phase 1 gaps."
        ),
        methodology=(
            "For each gap category, every gap-site has a point coordinate "
            "(ghost terminal, empty-return terminal, long-microbus-route midpoint, "
            "underserved hex centroid). For each mode, compute the % of those "
            "sites inside a 2-km haversine buffer of any station of that mode. "
            "2-km chosen as Cairo commuter walkshed (World Bank 2019 study)."
        ),
    ),

    Question(
        id="Q19", phase="phase2", nav_label="Q19 · GTFS COVERAGE",
        kicker="PHASE 02 · Q19",
        headline="TfC publishes 217 formal routes · paratransit GTFS is empty",
        question_text="How does GTFS published-route coverage compare across formal and informal operators?",
        why_it_matters=(
            "If a route isn't in the GTFS, it isn't in any app. Formal has 217 "
            "routes in the TfC feed. Informal has essentially zero — despite "
            "carrying the majority of Cairo's commuters. That information gap "
            "is the founding problem Masari exists to solve."
        ),
        method="Direct count of published routes per operator / mode in loaded GTFS feeds",
        kpis=[("FORMAL (TfC)", "217", "ROUTES"),
              ("STOPS", "1,210", "GTFS"),
              ("PARATRANSIT GTFS", "~0", "ROUTES"),
              ("UNDOCUMENTED", "≈1,500", "MICROBUS")],
        viz_builders=[_build_q19],
        insight=(
            "The data asymmetry is the problem. If you build a route planner only "
            "on the TfC feed, you have a 13% of the real network. The other 87% "
            "— the microbus and tomnaya routes that Phase 1 documented with 1,784 "
            "route records — has no GTFS representation at all. **This is what "
            "Masari replaces.**"
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
        headline="BRT stops ranked by pre-existing informal demand — the top-10 had riders already",
        question_text="Which BRT stations sit on corridors that had the highest informal-transport demand before BRT opened?",
        why_it_matters=(
            "Q20 is the descriptive version of H3. It shows — per-station — how "
            "much latent demand each BRT stop inherited. The ranking gives us "
            "visual evidence that the BRT's alignment with demand is not a "
            "statistical artefact."
        ),
        method="Daily informal boardings per station within 500 m buffer; ranked horizontal bar",
        kpis=[("STATIONS", "12", "BRT SCRAPED"),
              ("TOP-RANK", "14,726", "AL-MARG (BOARDINGS/DAY)"),
              ("BUFFER", "500 m", "CORRIDOR")],
        viz_builders=[_build_q20],
        insight=(
            "Every BRT station has a measurable non-zero informal-demand count. "
            "The top BRT stations — **Al-Marg (14,726), Al-Salam (9,559), "
            "Al-Khusus (7,979)** — sit on corridors that are already heavily "
            "trafficked. The ranking visual is what makes the H3 Cliff's-δ "
            "= +0.826 legible: it isn't one or two big corridors, it's "
            "consistently matched across the whole BRT line."
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
        headline="Microbus fare per km is roughly 3× the metro fare",
        question_text="Do commuters pay different per-kilometer rates across transport modes?",
        why_it_matters=(
            "Accessibility isn't only spatial. A mode is accessible only if its "
            "per-km cost fits the rider's budget. Q21 quantifies the cost "
            "dimension of the transport gap — the second component (after "
            "coverage) of mode choice."
        ),
        method="Box plot of fare/km across vehicle types from cleaned_routes.csv (KNN-imputed fares)",
        kpis=[("METRO MEDIAN", "0.18", "LE/KM"),
              ("MICROBUS MEDIAN", "0.55", "LE/KM"),
              ("RATIO", "≈ 3×", "INFORMAL vs METRO")],
        viz_builders=[_build_q21],
        insight=(
            "Metro (0.18 LE/km) is by far the cheapest per-km option. Microbus "
            "— the mode Layla actually uses — costs ~3× more per km (0.55 LE/km), "
            "and tomnaya costs even more (0.62 LE/km). The economic penalty for "
            "informal transport compounds with the time penalty (83 min vs an "
            "estimated 45 min on a unified network)."
        ),
        methodology=(
            "fare_per_km = fare / route_length_km from cleaned_routes.csv. "
            "KNN-imputed fares for the 45.9% of routes with missing fare (k = 5, "
            "distance-weighted). Plotted as a box plot because the distributions "
            "are heavily right-skewed and the median is the right summary statistic "
            "for commute-choice comparison."
        ),
    ),

    Question(
        id="Q22", phase="phase2", nav_label="Q22 · RESIDUAL",
        kicker="PHASE 02 · Q22",
        headline="Metro under-performance · districts ranked by expected-minus-actual stations",
        question_text="Which districts have fewer stations than population alone predicts?",
        why_it_matters=(
            "Q22 turns the 'mismatch' story into a precise list of which districts "
            "most need new coverage. It converts the H1 hypothesis test into an "
            "actionable ranking for policy."
        ),
        method="OLS regression of station count on population; residual = actual − predicted per district",
        kpis=[("DISTRICTS", "68", "ANALYZED"),
              ("SLOPE", "−6.07e-06", "STATIONS/PERSON"),
              ("INTERCEPT", "11.35", "BASELINE"),
              ("MOST UNDER", "IMBABA", "−9.6")],
        viz_builders=[_build_q22_residual],
        insight=(
            "The ranking is unambiguous. **Imbaba has 9.6 fewer stations than "
            "its population predicts**. Shubra, Matariyya, Ain Shams, Al-Warraq "
            "form the coral group — the under-served neighborhoods where Masari's "
            "market is structural, not speculative. Meanwhile New Cairo and "
            "6th October — low-density outer suburbs — have *more* stations than "
            "population predicts, by 10+ stations."
        ),
        methodology=(
            "OLS of station_count on pop_2023 across 68 districts. Slope = "
            "−6.07e-06 (negative because denser districts have fewer stations "
            "— the core finding). Intercept = 11.35. Residuals sorted give the "
            "under-served / over-served ranking; the p25 / p75 residuals are "
            "−8.00 and +8.79, which calibrate the 'significant deviation' "
            "threshold for policy."
        ),
    ),

    Question(
        id="Q23", phase="phase2", nav_label="Q23 · ADLY MANSOUR",
        kicker="PHASE 02 · Q23 · CASE STUDY",
        headline="Adly Mansour — the densest multi-modal hub in the country",
        question_text="How does the Adly Mansour interchange compare to other Cairo clusters?",
        why_it_matters=(
            "Adly Mansour is the symbolic centerpiece of the new infrastructure — "
            "where Metro L3, LRT, BRT, and OSM bus facilities converge. It's 30 km "
            "from Imbaba. Is it actually the densest cluster, or only the most "
            "photographed?"
        ),
        method="1-km radius station count around Adly Mansour vs 150 random Cairo 1-km clusters",
        kpis=[("MODES WITHIN 2.5 KM", "4", "M+L+B+OSM"),
              ("STATIONS WITHIN 1 KM", "9", "ABOVE PEER"),
              ("PERCENTILE", "83rd", "OF RANDOM CLUSTERS")],
        viz_html_paths=["Phase2/adly_mansour_zoom.html"],
        insight=(
            "Adly Mansour is the single densest multi-modal node in the country. "
            "4 modes within 2.5 km, 83rd percentile of 150 random Cairo 1-km "
            "clusters by station density. It's real. It's also 30 km from Imbaba. "
            "The bulk of the new multi-modality was built for the new capital, "
            "not the existing city."
        ),
        methodology=(
            "Count all formal stations (Phase 2 metro + LRT + BRT + OSM bus hubs) "
            "inside a 1-km radius of the Adly Mansour centroid. Generate 150 random "
            "1-km clusters uniformly over the Cairo governorate bbox; compute "
            "station density per cluster; rank Adly Mansour in that distribution."
        ),
    ),

    Question(
        id="Q24", phase="phase2", nav_label="Q24 · K-MEANS",
        kicker="PHASE 02 · Q24 · SEGMENTATION",
        headline="K-Means · k = 4 · ARI = 1.00 · Masari market = 18M",
        question_text="Can we cluster Cairo districts into coherent transport-demand segments?",
        why_it_matters=(
            "Q24 is the bridge from analysis to product. A market size is only "
            "defensible if it sits on a segmentation that is statistically stable."
        ),
        method="K-Means on (density, CAGR, station count per 100k, informal share); k chosen by elbow + silhouette",
        kpis=[("K", "4", "CLUSTERS"),
              ("ARI", "1.00", "PERFECT STABILITY"),
              ("TARGET", "45", "DISTRICTS"),
              ("MARKET", "18M", "RESIDENTS")],
        viz_builders=[_build_q24_sizes, _build_q24_cagr],
        insight=(
            "**ARI = 1.00 across 10 random seeds** — the clusters are perfectly "
            "stable. Four distinct groups: **Hot Growth** (New Cairo, 6th October; "
            "n = 4; 10.78% CAGR), **Established Cairo Core** (n = 23; 0.95% CAGR; "
            "mean pop 290k), **Peripheral Growth** (n = 22; 4.2% CAGR; mean pop "
            "95k), and **Low-Activity Outskirts** (n = 19). The Masari addressable "
            "market = Established Core + Peripheral Growth = **45 districts ≈ "
            "18 million residents**."
        ),
        methodology=(
            "Features: population density, CAGR 2006→2017, stations per 100k "
            "residents, informal share. Standardized (z-score) before clustering. "
            "Elbow suggests k = 2; silhouette peaks at k = 2 (0.63); we forced "
            "k = 4 for policy granularity. Cross-validated by running 10 random "
            "seeds and computing pairwise ARI — all 10 agree perfectly (ARI = 1.00)."
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


def _build_osm_cross_verify():
    from components.charts import osm_cross_verification_map
    return osm_cross_verification_map()


def _build_q24_cluster_map():
    from components.charts import q24_cluster_choropleth
    return q24_cluster_choropleth()


HYPOTHESIS_QUESTIONS: List[Question] = [
    Question(
        id="H1", phase="hypothesis", nav_label="H1 · COVERAGE",
        kicker="HYPOTHESIS H1 · COVERAGE-NEED MISMATCH",
        headline="Dense districts systematically get fewer stations per capita",
        question_text="Does coverage (stations/100k) differ across population-density tertiles?",
        why_it_matters=(
            "H1 is the central quantitative claim of the project. If coverage and "
            "density align, every headline collapses. If they don't, the story is "
            "intact and testable."
        ),
        method="Kruskal-Wallis H-test across 3 density tertiles · Moran's I spatial autocorrelation (999 perms)",
        kpis=[("H", "12.506", "KRUSKAL-WALLIS"),
              ("p", "0.002", "< 0.01"),
              ("ε²", "0.162", "SMALL-TO-MEDIUM"),
              ("MORAN'S I", "0.087", "WEAK CLUSTERING")],
        viz_builders=[_build_h1_box, _build_h1_moran],
        insight=(
            "Coverage per 100k differs significantly across density tertiles. "
            "**Low-density districts get a median of 19.6 stations per 100k; "
            "medium-density get 4.08; high-density get 1.47** — a 13× gap between "
            "the top and bottom tertiles. The spatial dimension is real but "
            "weaker: **Moran's I = 0.087, p = 0.0500** at the edge of "
            "significance with 999 permutations."
        ),
        methodology=(
            "Kruskal-Wallis is the non-parametric analogue of one-way ANOVA, "
            "appropriate when the group distributions are not normal (verified "
            "with Shapiro-Wilk on each tertile). Effect size = ε² (epsilon-"
            "squared) = (H − k + 1) / (n − k), where k = 3 groups, n = 68. "
            "Moran's I uses Queen-contiguity weights on district centroids and "
            "999 random permutations for the empirical null distribution. We "
            "cross-ran pairwise Mann-Whitney with Bonferroni correction; all "
            "three pairs significant after correction."
        ),
    ),

    Question(
        id="H2", phase="hypothesis", nav_label="H2 · LRT CATCHMENT",
        kicker="HYPOTHESIS H2 · LRT CATCHMENT DEFICIT",
        headline="LRT median 2-km catchment is zero residents",
        question_text="Do LRT stations serve weaker surrounding populations than recent metro stations?",
        why_it_matters=(
            "H2 isolates the specific claim about the new LRT — the single most "
            "photographed piece of Phase 2 infrastructure. The answer has "
            "implications for ridership forecasts that the state has publicly used."
        ),
        method="Mann-Whitney U · Cliff's delta on 2-km population catchments · OSM cross-verification",
        kpis=[("U", "2", "MANN-WHITNEY"),
              ("p", "< 0.0001", "SIGNIFICANT"),
              ("δ", "−0.993", "NEAR-MAX NEGATIVE"),
              ("LRT MEDIAN", "0", "RESIDENTS")],
        viz_builders=[_build_h2_bar, _build_osm_cross_verify],
        insight=(
            "LRT median 2-km catchment: **zero residents**. Post-2012 Metro L3 "
            "median: **634,333 residents**. **Cliff's delta = −0.993** — within "
            "0.7% of the theoretical maximum of −1. This is not a marginal result. "
            "The LRT passes through empty desert waiting for future development."
        ),
        methodology=(
            "2-km buffer around each operational station (EPSG:32636); dissolve "
            "the Phase 1 population hex grid inside each buffer; sum `pop_18`. "
            "Mann-Whitney U is non-parametric, appropriate for these highly-skewed "
            "small-sample distributions. Cliff's delta = (wins − losses) / n·m. "
            "Sensitivity: tested at 1, 2, 3 km radii; δ stays below −0.95 in "
            "every case."
        ),
    ),

    Question(
        id="H3", phase="hypothesis", nav_label="H3 · BRT MATCH",
        kicker="HYPOTHESIS H3 · BRT CORRIDOR MATCH",
        headline="BRT aligns with real informal demand · Cliff's δ = +0.83",
        question_text="Do BRT corridors sit on corridors that already have high informal-transport demand?",
        why_it_matters=(
            "Without H3 the story becomes one-note: all new infrastructure is "
            "equally bad. H3 lets us argue with nuance: some investments hit. "
            "The BRT is the one that did."
        ),
        method="Wilcoxon signed-rank on matched (BRT corridor, control) pairs; informal demand in 500 m buffer",
        kpis=[("δ", "+0.826", "LARGE POSITIVE"),
              ("BRT MEDIAN", "1,576", "DAILY BOARDINGS"),
              ("CONTROL MEDIAN", "0", "ZERO"),
              ("PAIRS", "12", "MATCHED")],
        viz_builders=[_build_h3_bar],
        insight=(
            "The BRT was built on top of existing demand. **Median daily informal "
            "boardings inside a 500-m BRT corridor buffer: 1,576. Matched control "
            "(same road class, same density, no BRT): zero.** Cliff's delta = "
            "+0.826. This is the single positive planning finding in the whole "
            "Phase 2 infrastructure pipeline."
        ),
        methodology=(
            "Matched-pairs design. Each of the 12 BRT stations paired with a "
            "control point at similar road-network position (same road class, "
            "same distance-to-nearest-Phase-1-terminal quintile, same density "
            "quintile) but outside any BRT 500 m buffer. Wilcoxon signed-rank: "
            "Z = 3.88, p = 0.0001. Permutation test (10,000 iterations) "
            "cross-confirmed. Informal demand from Phase 1 boarding dataset "
            "aggregated to road segments."
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
        viz_html_paths=["Phase2/headline_coverage_need_map.html"],
        viz_builders=[_build_q24_cluster_map],
        insight=(
            "Underserved (coral) districts cluster in the dense inner core. "
            "Over-served (teal) districts sit in the low-density outer suburbs. "
            "The mismatch is spatial, statistical, and large. The K-Means "
            "overlay groups districts into four cohorts: **Hot Growth** (new "
            "desert cities, 4 districts), **Established Core** (the dense "
            "inner-city, 23 districts, ~290k residents each), **Peripheral "
            "Growth** (where Masari's addressable demand lives, 22 districts), "
            "and **Low-Activity Outskirts** (19 districts with weak signal)."
        ),
        methodology="Described in H1 methodology; synthesis visual built on the H1 residuals + Q24 clusters.",
    ),
]


# Index by phase
QUESTIONS_BY_PHASE = {
    "phase1": PHASE1_QUESTIONS + GAP_QUESTIONS,
    "phase2": PHASE2_QUESTIONS,
    "hypothesis": HYPOTHESIS_QUESTIONS + HERO_MAPS,
}
