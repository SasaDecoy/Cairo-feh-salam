"""
Notebook-verified findings.

All numbers extracted from:
  - Phase 1 · Cleaning Data (1).ipynb + Visual Analysis (1).ipynb
  - Phase 2 · Phase2_Scraping_Cleaning.ipynb + Phase2_Analysis_Hypothesis.ipynb

If a notebook changes, update the corresponding dict here.
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
            vehicle_mix=dict(box=18, bus=503, microbus=861, minibus=287, tomnaya=115),
        ),
        G4=dict(
            name="Underserved hexes",
            underserved_count=79,
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
# ═══════════════════════════════════════════════════════════════════════

H1 = dict(
    test="Kruskal-Wallis",
    H=12.506, p=0.00192, eps_sq=0.162,
    n_by_tertile=dict(low=23, med=22, high=23),
    tertile_medians=dict(low=19.6, med=4.08, high=1.47),
    morans_I=0.087, morans_p=0.0500, morans_perms=999,
    interpretation=(
        "Coverage per 100k differs significantly across density tertiles "
        "(p<0.01). Effect size is small-to-medium. Moran's I indicates "
        "weak spatial clustering of under-served districts at the edge "
        "of significance."
    ),
)

H2 = dict(
    test="Mann-Whitney U",
    U=2, p=0.0000, cliffs_delta=-0.993,
    medians=dict(lrt=0, metro_l3_post_2012=634_333),
    n_by_group=dict(lrt=16, metro_l3=27),
    interpretation=(
        "LRT median 2-km catchment is effectively zero residents; "
        "post-2012 Metro L3 median is ~634k. Cliff's delta = -0.993 is "
        "very close to the theoretical maximum of -1."
    ),
)

H3 = dict(
    test="Wilcoxon signed-rank (matched pairs)",
    U=132, p=0.0001, cliffs_delta=0.826,
    medians=dict(brt=1576, control=0),
    n_pairs=12,
    interpretation=(
        "BRT corridor stations coincide with pre-existing informal demand "
        "(median 1,576 daily boardings); matched controls see zero. "
        "Cliff's delta = +0.826. BRT is the single planning success of "
        "the $10B Phase 2 infrastructure."
    ),
)

Q14 = dict(
    total_ghosts=115,
    within_1km=9, within_1km_pct=8,
    beyond_2km=97, beyond_2km_pct=84,
    buckets=[("0-1 km", 3), ("1-2 km", 6), ("2-5 km", 9), ("5-10 km", 27), (">10 km", 70)],
)

Q18B = dict(
    modes=["METRO L3", "LRT", "BRT"],
    gaps=["GHOSTS", "EMPTY-RETURN", "VEHICLE MISMATCH", "UNDER-SERVED"],
    values=[
        [15.7, 5.3, 0.0, 9.7],   # Metro L3
        [3.5,  5.3, 25.0, 2.6],  # LRT
        [4.3, 10.5, 25.0, 13.6], # BRT
    ],
    note="No Monorail row — the Cairo Monorail is not operational yet.",
)

Q22_ADLY = dict(
    total_stations_within_1km=9,
    modes_within_2_5km=4,
    percentile=83,
)

Q24 = dict(
    k=4, ARI=1.00,
    clusters=dict(
        hot_growth=dict(n=4, cagr_pct=10.78, pop_mean=122_000, label="Hot Growth (New Cairo / 6th October)"),
        established_core=dict(n=23, cagr_pct=0.95, pop_mean=290_000, label="Established Cairo Core"),
        peripheral_growth=dict(n=22, cagr_pct=4.20, pop_mean=95_000, label="Peripheral Growth"),
        outlier=dict(n=19, cagr_pct=None, pop_mean=None, label="Low-Activity Outskirts"),
    ),
)

MARKET = dict(
    target_clusters=["established_core", "peripheral_growth"],
    target_districts=45,
    target_population_millions=18,
)

COMMUTE = dict(
    imbaba_density_per_km2=63_000,
    home_to_office_crow_km=11,
    one_way_minutes=83,
    fare_ratio_microbus_vs_metro=3.0,
    daily_commuters_national=1_400_000,
    home_coords=[31.2083, 30.0866],
    office_coords=[31.2581, 29.9601],
)

# Scraping methodology shorthand (used in methodology expanders)
SCRAPE = dict(
    metro=dict(source="Wikipedia List_of_Cairo_Metro_stations", n=89,
               method="DMS->decimal; opening-phase derived from year thresholds"),
    lrt=dict(source="Wikipedia Cairo_Light_Rail_Transit", n=20,
             coords_on_page=0, rescued_overpass=9, rescued_gmaps=7, remaining=4),
    brt=dict(source="Google Maps (playwright)", n=12,
             method="10 viewport queries + regex aria-labels + uroman romanization + 3-tier dedup"),
    sbert=dict(model="paraphrase-multilingual-MiniLM-L12-v2", dim=384,
               tau=0.65, gold_set_pairs=5),
    moran=dict(perms=999, weights="Queen-contiguity on district centroids"),
)
