"""
Notebook-verified findings.

All numbers extracted from:
  - Phase 1 · Cleaning Data.ipynb + Visual Analysis.ipynb
  - Phase 2 · Phase2_Scraping_Cleaning.ipynb + Phase2_Analysis_Hypothesis.ipynb
    (latest commit: "Update Phase 2 analysis questions and hypothesis tests")

THIS FILE IS THE SINGLE SOURCE OF TRUTH for every statistic the app cites.
If a notebook value changes, update the corresponding dict here AND nothing
else — the chapters, evidence pages, and charts all read from this file.
"""

# ═══════════════════════════════════════════════════════════════════════
#  PHASE 1 · problem identification
# ═══════════════════════════════════════════════════════════════════════

PHASE1 = dict(
    counts=dict(
        boarding_stops=1_302,
        routes=1_784,
        terminals=280,
        population_hexes=1_525,
        passenger_flow_segments=9_258,
        vehicle_flow_segments=5_592,
        speed_records=26_154,
    ),
    cleaning=dict(
        imputation="KNN k=5 distance-weighted",
        crs="EPSG:32636",
        rows_dropped=0,
        null_cells_pre=2_409,
    ),
    gaps=dict(
        G1=dict(
            name="Ghost terminals",
            count=115,
            buffer_m=100,
            near_miss_100_500m=69,
            stop_too_far_500_1000m=17,
            truly_isolated_beyond_1km=29,
            recovery_at_500m=46,
        ),
        G2=dict(
            name="Empty-return routes",
            critical_count=19,
            healthy_count=208,
            threshold=0.60,
            formula="Empty Return Index = 1 - (passengers / vehicles)",
        ),
        G3=dict(
            name="Vehicle-route mismatch",
            pct_long_routes_on_microbus=75,
            long_route_km=50,
            long_route_violations=44,
            vehicle_mix=dict(box=18, bus=503, microbus=861, minibus=287, tomnaya=115),
        ),
        G4=dict(
            name="Underserved hexes",
            underserved_count=79,
            top_quartile_count=381,
            threshold=0.5,
            formula="Underserved_Score = Population / Total_Boarding",
        ),
    ),
    questions=dict(
        Q1=dict(morning_jobs_corr=0.261, daily_jobs_corr=0.248),
        Q3=dict(adherence_pct=88.0, buffer_m=120),
        Q8=dict(note="Moran-style lag scatter; HH/LL clusters of high-boarding stops"),
        Q11=dict(
            efficient_hub=76, marginal=77, overcrowded=64, dead_weight=63,
            dead_weight_note="same route count as Efficient Hubs but 1,870x fewer passengers",
        ),
    ),
)

# ═══════════════════════════════════════════════════════════════════════
#  PHASE 2 · diagnosis + proposal
#  (matches Phase2_Analysis_Hypothesis.ipynb · latest commit)
# ═══════════════════════════════════════════════════════════════════════

H1 = dict(
    test="Kruskal-Wallis",
    H=55.7, p=0.0, eps_sq=0.826,
    n_by_tertile=dict(low=23, med=22, high=23),
    tertile_medians=dict(low=25.9, med=8.5, high=2.15),
    morans_I=0.214, morans_p=0.0020, morans_perms=999,
    centroid_method=(
        "Real Nominatim district centroids from S6 (upgraded from the earlier "
        "3-governorate-centroid proxy — the upgrade is what turned the "
        "small-to-medium effect into the huge effect)."
    ),
    robustness="Chi-square + Welch t-test cross-checks confirm the same direction.",
    interpretation=(
        "Coverage per 100k differs significantly across density tertiles "
        "(p < 0.001). Effect size ε² = 0.826 is huge. Low-density tertile "
        "median 25.9 stations / 100k vs high-density 2.15 — roughly a 12× "
        "gap. Moran's I indicates statistically significant spatial clustering "
        "of under-served districts."
    ),
)

H2 = dict(
    test="Mann-Whitney U",
    U=2, p=0.0000, cliffs_delta=-0.991,
    medians=dict(lrt=916, metro_l3_post_2012=634_333),
    # Live CSV counts: LRT has 12 stations with valid coordinates; Metro Line 3
    # post-2012 has 31 stations (the notebook subset for H2 was 27 — using the
    # post-2012 filter on the current CSV gives 31).
    n_by_group=dict(lrt=12, metro_l3=31),
    sensitivity_radii_km=[1, 2, 3],
    sensitivity_note="δ stays below −0.95 at every radius",
    interpretation=(
        "LRT median 2-km catchment is 916 residents (12 LRT stations "
        "have valid coordinates after the OSM + Google Maps backfill in "
        "S4); post-2012 Metro L3 median is ~634k. Cliff's delta = "
        "-0.991 is very close to the theoretical maximum of -1."
    ),
)

H3 = dict(
    test="Mann-Whitney U (random urbanized controls)",
    U=132, p=0.0001, cliffs_delta=0.710,
    medians=dict(brt=566, control=0),
    n_brt=12, n_control_method="random urbanized non-Ring-Road sample",
    cross_validation="10,000-iteration permutation test confirms the same conclusion",
    interpretation=(
        "BRT corridor stations coincide with pre-existing informal demand "
        "(median 566 daily boardings); matched non-Ring-Road controls "
        "see zero. Cliff's delta = +0.710. BRT is the single planning "
        "success of the $10B Phase 2 infrastructure."
    ),
)

Q14 = dict(
    total_ghosts=115,
    within_1km=9, within_1km_pct=8,
    beyond_2km=97, beyond_2km_pct=84,
    buckets=[("0-1 km", 3), ("1-2 km", 6), ("2-5 km", 9), ("5-10 km", 27), (">10 km", 70)],
)

Q18B = dict(
    # Fallback values — the chart prefers data.live.compute_q18b_matrix()
    # which recomputes from the live CSVs.  These match the CSVs as of
    # the latest notebook commit (gap site counts: G1=115 · G2=19 · G3=4 ·
    # G4=382;  mode counts: Metro L3 post-2014=27 · LRT=12 · BRT=21).
    modes=["METRO L3", "LRT", "BRT"],
    gaps=["GHOSTS", "EMPTY-RETURN", "VEHICLE MISMATCH", "UNDER-SERVED"],
    values=[
        [15.7, 5.3,  0.0, 9.7],   # Metro L3 post-2014
        [ 3.5, 5.3, 25.0, 2.6],   # LRT
        [ 4.3, 10.5, 25.0, 13.6], # BRT
    ],
    note="No Monorail row — the Cairo Monorail is not operational yet.",
)

Q18 = dict(
    spearman_rho=0.025, spearman_p=0.40,
    ols_slope=0.010,
    avg_informal_share_pct=47,
    interpretation=(
        "Statistically flat: ρ = 0.025, p = 0.40. Informal transport is "
        "not density-targeted — it's ubiquitous background transport, "
        "averaging ~47% modal share across Cairo."
    ),
)

Q21 = dict(
    # Real GTFS fare medians from the latest analysis notebook
    fares_egp_per_km=dict(bus=0.22, metro=0.25, microbus=0.62, tomnaya=1.30),
    n_routes=dict(bus=214, metro=None, microbus=861, tomnaya=115),
    interpretation=(
        "Formal Bus 0.22 EGP/km · formal Metro 0.25 EGP/km. Informal "
        "Microbus 0.62 EGP/km (~3× formal). Informal Tomnaya 1.30 EGP/km "
        "(~6× formal). Riders pay the informal premium because formal "
        "doesn't reach them."
    ),
)

Q22 = dict(
    method="OLS regression of metro stations on population (3 km buffer per district centroid)",
    most_under_served=[
        ("Ad-Duqqi", -9.28),
        ("Sheikh Zayed", -9.09),
        ("6th October City 1 & 3", -8.52),
        ("Al-Ḥawāmidiyah", -8.14),
    ],
    note=(
        "All four worst-residual districts are in Giza/Qalyubia — dense or "
        "rapidly-growing edges. The residual scatter degenerates because "
        "every district sharing a governorate-centroid proxy ends up with "
        "the same n_stations, so the notebook switched to a ranked bar."
    ),
)

Q23_ADLY = dict(
    total_stations_within_2_5km=8,
    modes_within_2_5km=4,
    percentile=21,
    nearby_modes=["Metro Line 3 (terminus)", "Cairo LRT (origin to NAC)",
                  "Cairo BRT (Ring Road)", "Phase-1 informal terminals"],
    nearby_informal=[("Al-Salam", 1.4), ("Awwal Madinet", None)],
    interpretation=(
        "Adly Mansour sits around the 21st percentile of the random "
        "2.5-km cluster sample — enough to prove multimodal convergence, "
        "but not enough to call it Greater Cairo's strongest demand hub. "
        "The Transport Minister's 'seventh mode' framing is a planning "
        "claim more than a demographic claim."
    ),
)

Q24 = dict(
    k=4, ARI=1.00, n_seeds_for_stability=5,
    silhouette_k4=0.412, n_init=50,
    features=["log_pop_2023", "CAGR %", "stations within 3 km",
              "informal stops within 3 km", "Cairo governorate indicator"],
    clusters=dict(
        formal_served_core=dict(n=31, cagr_pct=0.19, pop_sum=5_588_660, label="Formal-Served Core"),
        peripheral_growth=dict(n=19, cagr_pct=2.83, pop_sum=9_175_673, label="Peripheral Growth"),
        mixed=dict(n=12, cagr_pct=2.17, pop_sum=4_152_500, label="Mixed (cluster 2)"),
        low_activity_outskirts=dict(n=6, cagr_pct=11.93, pop_sum=None, label="Low-Activity Outskirts"),
    ),
)

Q25 = dict(
    description=(
        "Masari Bridge — connects each informal-heavy Phase 1 stop to its "
        "nearest formal node (GTFS, Metro, LRT, BRT). The connector lines "
        "are the missing product layer. Short connectors become immediate "
        "routing wins; long connectors flag where Masari's value is "
        "rider-contributed routing."
    ),
    formal_layer="GTFS stops + Metro + LRT + BRT",
    informal_layer="Phase 1 stops where informal daily boarding > formal daily boarding",
    score_formula="demand × inverse distance",
)

MARKET = dict(
    target_clusters=["formal_served_core", "peripheral_growth", "mixed"],
    target_districts=62,
    target_population_millions=18.9,
)

COMMUTE = dict(
    imbaba_density_per_km2=63_000,
    home_to_office_crow_km=11,
    one_way_minutes=83,
    fare_ratio_microbus_vs_metro=2.5,  # 0.62 / 0.25 ≈ 2.5×
    daily_commuters_national=1_400_000,
    home_coords=[31.2083, 30.0866],
    office_coords=[31.2581, 29.9601],
)

# ═══════════════════════════════════════════════════════════════════════
#  Scraping methodology shorthand (used in methodology expanders)
# ═══════════════════════════════════════════════════════════════════════

SCRAPE = dict(
    # Live CSV counts as of the latest notebook commit:
    metro=dict(source="Wikipedia List_of_Cairo_Metro_stations", n=89,
               with_coords=89,
               method="DMS->decimal; opening-phase derived from year thresholds"),
    lrt=dict(source="Wikipedia Cairo_Light_Rail_Transit", n=20,
             coords_on_page=0, rescued_overpass=9, rescued_gmaps=7,
             with_coords=12, remaining=8,
             note=("CSV currently shows 12 stations with valid lat/lon; "
                   "8 are still planned-only or coordinate-less in the CSV.")),
    brt=dict(source="Google Maps (playwright)", n=21, with_coords=21,
             method="10 viewport queries + regex aria-labels + uroman romanization + 3-tier dedup",
             note="BRT scrape grew from the original 12 to 21 stations after rerunning S5."),
    sbert=dict(model="paraphrase-multilingual-MiniLM-L12-v2", dim=384,
               tau=0.65, gold_set_pairs=5),
    moran=dict(perms=999, weights="KNN-as-contiguity on Nominatim district centroids"),
)

# ═══════════════════════════════════════════════════════════════════════
#  Analytical methods (referenced across the app)
# ═══════════════════════════════════════════════════════════════════════

AI_TECHNIQUES = [
    dict(n=1, name="SBERT semantic matching",
         where="Notebook 3 · Stage 4 of the integration pipeline",
         solves="Cross-script (Arabic ↔ English) station-name matching"),
    dict(n=2, name="K-Means clustering",
         where="Notebook 4 · Q24",
         solves="District-level transport-demand segmentation → Masari market"),
    dict(n=3, name="Moran's I spatial autocorrelation",
         where="Notebook 4 · H1 robustness",
         solves="Tests whether under-served districts cluster geographically"),
]
