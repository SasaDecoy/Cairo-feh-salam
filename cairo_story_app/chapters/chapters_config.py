"""
14-chapter narrative — Layla's commute.
Chapter 0: title. Chapters 1-3: Act I (Layla). Chapters 4-11: Act II (diagnosis).
Chapters 12-13: Act III (Masari + arrival).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class LaylaPos:
    kind: str
    coords: Optional[List[float]] = None
    route: Optional[str] = None
    progress: Optional[float] = None
    brightness: float = 1.0
    show_image: bool = False


@dataclass(frozen=True)
class Chapter:
    id: int
    act: str
    title_short: str
    kicker: str
    headline: str
    arabic: str
    body: str
    methodology: str
    metric_label: str
    metric_value: str
    metric_unit: str
    center: List[float]
    zoom: float
    pitch: float
    bearing: float
    emphasize_layers: List[str] = field(default_factory=list)
    dim_layers: List[str] = field(default_factory=list)
    chart: Optional[str] = None
    layla: LaylaPos = field(default_factory=lambda: LaylaPos(kind="fixed", coords=[31.2083, 30.0866]))


IMBABA = [31.2083, 30.0866]
MAADI = [31.2581, 29.9601]


CHAPTERS: List[Chapter] = [
    # ══════ CHAPTER 0 · TITLE ══════
    Chapter(
        id=0, act="—", title_short="TITLE",
        kicker="PHASE 02 · THE ARGUMENT",
        headline="A story about what Cairo built and who was left out",
        arabic="القاهرة · نظامان",
        body=(
            "Every morning 1.4 million Cairenes commute by bus or microbus. "
            "Most make trips the state's $10 billion post-2014 transport programme "
            "was never designed to serve. This presentation tells one of those "
            "stories — Layla's — and the data behind it."
        ),
        methodology=(
            "This app is built from four Jupyter notebooks. **Phase 1** cleans "
            "and analyses the existing transport reality (1,302 bus stops, 1,784 "
            "routes, 280 terminals, 9,258 road segments, 1,525 population hexes) "
            "and identifies four structural gaps. **Phase 2** scrapes the new "
            "post-2014 infrastructure (89 metro · 20 LRT · 12 BRT), integrates it "
            "with Phase 1 terminals, and tests three formal hypotheses. Press → "
            "or click any chapter on the left. The top nav switches to the "
            "per-question evidence mode."
        ),
        metric_label="ONE MORNING · ONE CITY",
        metric_value="1.4M",
        metric_unit="CAIRENES COMMUTE LIKE LAYLA",
        center=[31.30, 30.05], zoom=9.8, pitch=0, bearing=0,
        emphasize_layers=[], dim_layers=[],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.6),
    ),

    # ══════ CHAPTER 1 · HOME ══════
    Chapter(
        id=1, act="I", title_short="HOME",
        kicker="STAGE 01 · HOME",
        headline="Layla lives in Imbaba",
        arabic="ليلى · إمبابة · ٦:١٥ صباحاً",
        body=(
            "One of the densest neighborhoods on Earth — 63,000 people per "
            "square kilometer. No metro ran through Imbaba until 2024. None "
            "run at a useful walking distance from her apartment today."
        ),
        methodology=(
            "Imbaba's density figure comes from **citypopulation.de** (Phase 2 "
            "source S6). We scraped the `egypt/admin` page (408 rows covering "
            "27 governorates) and filtered to Greater Cairo (Cairo + Giza + "
            "Qalyubia). Layla is a composite persona — a fictional commuter who "
            "stands for the 1.4 million Cairenes whose commutes the state's "
            "formal transport map does not describe. Her 83-minute commute "
            "time is derived from **explorecity.life** crowdsourced data and "
            "the **World Bank Cairo Traffic Congestion Study**."
        ),
        metric_label="DENSITY · IMBABA",
        metric_value="63,000",
        metric_unit="PEOPLE PER SQ KM",
        center=IMBABA, zoom=13.2, pitch=55, bearing=-15,
        emphasize_layers=["home"], dim_layers=[],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=1.0, show_image=True),
    ),

    # ══════ CHAPTER 2 · OFFICE ══════
    Chapter(
        id=2, act="I", title_short="OFFICE",
        kicker="STAGE 02 · WORKPLACE",
        headline="Her office is in Maadi · 11 km away",
        arabic="المعادي · ١١ كيلومتر",
        body=(
            "Across the city. South of the Nile. On paper, a short trip. In reality, "
            "Layla must cross two transport systems that were never designed to "
            "connect — the formal state-built network (System A) and the informal "
            "microbus network (System B)."
        ),
        methodology=(
            "The 11 km is haversine crow-flies from Imbaba centroid (31.2083°, "
            "30.0866°) to Maadi office (31.2581°, 29.9601°) — great-circle with "
            "Earth radius 6,371 km. Both coordinates sourced from Phase 1's "
            "integrated terminal dataset and cross-checked against OSM Nominatim "
            "geocodes. The dashed yellow line on the map is this haversine path; "
            "Layla's real route (Chapter 3 onwards) diverges by kilometres."
        ),
        metric_label="STRAIGHT-LINE DISTANCE",
        metric_value="11",
        metric_unit="KM · AS THE CROW FLIES",
        center=[31.22, 30.02], zoom=10.8, pitch=40, bearing=-15,
        emphasize_layers=["home", "office", "crow_line"], dim_layers=[],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.9),
    ),

    # ══════ CHAPTER 3 · REAL TRIP ══════
    Chapter(
        id=3, act="I", title_short="REAL TRIP",
        kicker="STAGE 03 · THE REAL JOURNEY",
        headline="The real route is 83 minutes each way",
        arabic="الرحلة الحقيقية · ٨٣ دقيقة",
        body=(
            "Three vehicles. Two transfers. No single app that can plan the trip "
            "end to end. Layla does this twice a day — over 720 hours a year "
            "sitting in transit. Roughly 30 working days, annually, lost to a "
            "city that cannot route her."
        ),
        methodology=(
            "The 83-minute figure sums explorecity.life's Cairo bus wait (8.5 min), "
            "microbus ride (25 min), metro ride (30 min), and two walking legs "
            "(8 + 12 min). Each component traces to the S15 dataset; we "
            "cross-validated against the World Bank study's mode-specific "
            "averages (S12). 720 hours assumes 260 commuting days × 166 minutes "
            "round-trip. The coral polyline (`chaos.geojson`) is the sketched "
            "real path — 14 hand-digitized waypoints across 26th July Street "
            "and the Corniche."
        ),
        metric_label="TYPICAL TRIP",
        metric_value="83",
        metric_unit="MIN · EACH WAY",
        center=[31.24, 30.05], zoom=10.6, pitch=45, bearing=0,
        emphasize_layers=["home", "office", "chaos_route"], dim_layers=["crow_line"],
        chart=None,
        layla=LaylaPos(kind="route", route="chaos", progress=0.15, brightness=1.0),
    ),

    # ══════ CHAPTER 4 · STATE BUILT ══════
    Chapter(
        id=4, act="II", title_short="STATE BUILT",
        kicker="STAGE 04 · THE $10B SYSTEM",
        headline="What Cairo built since 2014",
        arabic="١٠ مليار دولار · البنية الجديدة",
        body=(
            "Metro Line 3 — Ataba to Adly Mansour, then Kit Kat westward. The "
            "Cairo LRT to the New Administrative Capital. The Ring Road BRT. "
            "Ten billion dollars of rail, bus-rapid, and light-rail infrastructure. "
            "Here is where every dollar went."
        ),
        methodology=(
            "Three Wikipedia pages were scraped for formal-network coordinates. "
            "**List_of_Cairo_Metro_stations** (89 rows, 100% coordinates, DMS→decimal "
            "parsed, opening phase derived from year thresholds). **Cairo_Light_Rail_Transit** "
            "(20 rows, 0% coordinates on page — rescued 9 via OSM Overpass + 7 via "
            "Google Maps fallback; 4 remain planned-only). **BRT** — no Wikipedia page "
            "exists, so 10 viewport queries against Google Maps with playwright-backed "
            "scraping. Arabic station names romanized via `uroman` (franko transliteration), "
            "not MarianMT — because MarianMT translates المرج semantically to 'lawn' "
            "instead of phonetically to 'almrj', which breaks deduplication."
        ),
        metric_label="INVESTMENT · 2014–2026",
        metric_value="$10B",
        metric_unit="NEW INFRASTRUCTURE",
        center=[31.32, 30.07], zoom=10.0, pitch=45, bearing=-5,
        emphasize_layers=["metro", "lrt", "brt"],
        dim_layers=["home", "office"],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 5 · GHOSTS ══════
    Chapter(
        id=5, act="II", title_short="GHOSTS",
        kicker="STAGE 05 · GHOSTS · Q14",
        headline="84% of Phase-1 ghost terminals are beyond 2 km of any new station",
        arabic="المحطات المنسيّة · ٨٤٪ بعيدة",
        body=(
            "In Phase 1 we identified 115 'ghost' terminals — bus terminals that "
            "appear on route maps but see essentially no boarding. Of those 115, "
            "only 9 sit within a kilometer of any post-2014 metro station. "
            "Ninety-seven — 84% — sit beyond two kilometers. The $10B of new "
            "infrastructure did not reach them."
        ),
        methodology=(
            "Phase 1 defined a **ghost terminal** as one with no boarding within "
            "a 100 m buffer of its route endpoints. 115 matched. Sub-classification "
            "by distance to nearest stop: **69 near-miss** (100–500 m — relocate "
            "the stop), **17 stop-too-far** (500 m–1 km — walkability fix), "
            "**29 truly isolated** (>1 km — audit or decommission). **Phase 2's Q14** "
            "takes that 115 and asks: how many were resolved by the post-2014 metro? "
            "For each ghost, haversine to every new metro station, keep the minimum. "
            "Bucket distribution (0–1, 1–2, 2–5, 5–10, >10 km) = 3, 6, 9, 27, 70. "
            "The 70 most distant terminals are the story — they never got a station."
        ),
        metric_label="STRANDED",
        metric_value="84%",
        metric_unit="GHOSTS OVER 2 KM",
        center=[31.22, 30.08], zoom=11.0, pitch=50, bearing=-10,
        emphasize_layers=["informal_ghost", "metro"],
        dim_layers=["lrt", "brt"],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.5),
    ),

    # ══════ CHAPTER 6 · DENSITY ══════
    Chapter(
        id=6, act="II", title_short="DENSITY",
        kicker="STAGE 06 · TWO DENSITIES",
        headline="Cairo is a city of two densities",
        arabic="القاهرة · مدينتان مختلفتان",
        body=(
            "Imbaba: 63,000 people per square kilometer. New Cairo: fewer than "
            "3,000. The state's new stations favor the empty outer suburbs — "
            "land where growth is expected — over the already-dense inner core "
            "where people already live."
        ),
        methodology=(
            "Population data comes from **citypopulation.de** (S6) scraped for "
            "68 Cairo Governorate districts. Growth rate data from the same "
            "source's CAGR tables (computed 2006→2017). Station counts come "
            "from a 3-km-radius spatial join between each district centroid and "
            "our integrated station dataset. The coverage ratio (stations per "
            "100k residents) was binned into three tertiles; the under-served "
            "(coral) vs over-served (teal) classification you see is the "
            "bottom and top tertile."
        ),
        metric_label="DENSITY RATIO",
        metric_value="21×",
        metric_unit="IMBABA vs NEW CAIRO",
        center=[31.25, 30.05], zoom=10.0, pitch=0, bearing=0,
        emphasize_layers=["districts"],
        dim_layers=["metro", "lrt", "brt"],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 7 · MAWFAQ ══════
    Chapter(
        id=7, act="I", title_short="MAWFAQ",
        kicker="STAGE 07 · THE MAWFAQ",
        headline="At 6:15 AM she stands at the mawfaq",
        arabic="الموقف · الساعة ٦:١٥",
        body=(
            "Five microbuses. Five destinations written in Arabic on taped "
            "cardboard. Drivers shouting competing routes. No schedule. No app. "
            "No driver who knows her specific trip. She picks one by guessing "
            "which direction it starts in."
        ),
        methodology=(
            "The mawfaq (موقف · informal terminal) is the physical expression "
            "of Phase 1's 280 terminals — Arabic plural *mawaqif*. Phase 1 "
            "identified 19 terminals with an Empty Return Index ≥ 0.60 "
            "(Index = 1 − passengers/vehicles) — vehicles arriving without "
            "riders. The mawfaq on the map is one of them. On our integrated "
            "dataset (Stage 1 KNN spatial matching + Stage 4 SBERT multilingual "
            "reconciliation) we can see that this specific mawfaq is not linked "
            "to any post-2014 metro station within its 2-km walkshed."
        ),
        metric_label="DEPARTURES PER HOUR",
        metric_value="60+",
        metric_unit="MICROBUSES · NO SCHEDULE",
        center=IMBABA, zoom=15.2, pitch=55, bearing=5,
        emphasize_layers=["home", "informal"],
        dim_layers=[],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=1.0, show_image=True),
    ),

    # ══════ CHAPTER 8 · H1 COVERAGE MISMATCH ══════
    Chapter(
        id=8, act="II", title_short="H1 · COVERAGE",
        kicker="STAGE 08 · HYPOTHESIS H1",
        headline="Dense districts get 12× fewer stations per capita",
        arabic="عدم التوافق · ح١",
        body=(
            "We divided Cairo's 68 districts into three density tertiles and counted "
            "stations per 100,000 residents in each. Low-density districts (the "
            "empty outer ring) get a median of 19.6 stations per 100k. High-density "
            "districts (where Layla lives) get 1.47. That's a 13× gap and the "
            "Kruskal-Wallis test rejects the null at p < 0.01."
        ),
        methodology=(
            "**Kruskal-Wallis** (non-parametric ANOVA) because station counts "
            "per-capita are not normally distributed and we have three groups. "
            "Result: **H = 12.506, p = 0.00192, ε² = 0.162** (small-to-medium effect). "
            "Cross-validated with pairwise Mann-Whitney U tests. **Moran's I** "
            "(Queen-contiguity weights, 999 permutations) on the residuals: "
            "**I = 0.087, z = 1.805, p = 0.0500** — weak spatial clustering "
            "of under-served districts. Under-served cluster: Imbaba, Shubra, "
            "Matariyya (LISA coldspots)."
        ),
        metric_label="EFFECT SIZE",
        metric_value="ε² = 0.16",
        metric_unit="KW H = 12.5 · p = 0.002",
        center=[31.25, 30.05], zoom=10.4, pitch=30, bearing=0,
        emphasize_layers=["districts", "metro", "lrt", "brt"],
        dim_layers=["informal"],
        chart="h1_box",
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 9 · H2 LRT ══════
    Chapter(
        id=9, act="II", title_short="H2 · LRT",
        kicker="STAGE 09 · HYPOTHESIS H2",
        headline="The LRT median catchment is zero residents",
        arabic="قطار خفيف في الصحراء · ح٢",
        body=(
            "We drew 2-kilometer circles around each operational LRT station and "
            "asked: how many people live inside? The median answer is zero. For "
            "the post-2012 Metro Line 3 stations the median is 634,333. Cliff's "
            "delta — the effect size — is −0.993, within a hair of the theoretical "
            "maximum. This is not marginal. This is planning built for a city "
            "that does not yet exist."
        ),
        methodology=(
            "**Mann-Whitney U** (appropriate for non-normal, small-sample "
            "distributions). U = 2, p < 0.0001. **Cliff's delta = −0.993** "
            "(Cliff's δ ranges from −1 to +1; this is essentially the maximum "
            "possible negative effect). We tested sensitivity at 1 km, 2 km, "
            "and 3 km radii — delta stays below −0.95 in all three. Population "
            "catchment uses Phase 1's 1,525-row hexagon-level population dataset "
            "(cleaned_population.csv), dissolved within each station's 2-km "
            "buffer in EPSG:32636."
        ),
        metric_label="CLIFF'S DELTA",
        metric_value="δ = −0.99",
        metric_unit="NEAR-MAX NEGATIVE",
        center=[31.55, 30.10], zoom=9.2, pitch=50, bearing=20,
        emphasize_layers=["lrt"],
        dim_layers=["metro", "districts"],
        chart="h2_bar",
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 10 · H3 BRT ══════
    Chapter(
        id=10, act="II", title_short="H3 · BRT",
        kicker="STAGE 10 · HYPOTHESIS H3",
        headline="The BRT is the one thing they got right",
        arabic="النقل السريع · ح٣",
        body=(
            "Not all of the $10B missed. The Ring Road BRT was routed directly "
            "through the busiest informal microbus corridors. Median daily informal "
            "boardings inside a 500-meter BRT corridor buffer: 1,576. For matched "
            "control points picked at similar road-network positions: zero. Cliff's "
            "delta: +0.826. A large, positive effect. The demand was already there "
            "— they met it instead of inventing it."
        ),
        methodology=(
            "**Matched-pairs Wilcoxon signed-rank**. For each of the 12 BRT stations, "
            "we paired a control point at similar road-network position — matched on "
            "road-class, distance to nearest Phase 1 terminal, and approximate "
            "density — but outside any BRT buffer. Z = 3.88, p = 0.0001. "
            "**Cliff's delta = +0.826** (large positive). We also cross-ran the "
            "permutation equivalent (10,000 iterations) and got the same conclusion. "
            "Data source for informal demand: Phase 1 boarding dataset, 1,302 rows, "
            "aggregated to road segments."
        ),
        metric_label="CLIFF'S DELTA",
        metric_value="δ = +0.83",
        metric_unit="THE ONE PLANNING WIN",
        center=[31.33, 30.14], zoom=10.8, pitch=45, bearing=-10,
        emphasize_layers=["brt", "informal"],
        dim_layers=["metro", "lrt"],
        chart="h3_bar",
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 11 · Q18B VERDICT ══════
    Chapter(
        id=11, act="II", title_short="Q18B · VERDICT",
        kicker="STAGE 11 · VERDICT · Q18b",
        headline="No cell in this matrix is above 25%",
        arabic="الحُكم · ١٨ب",
        body=(
            "We cross-tabulated Phase 1's four gaps against Phase 2's three new "
            "modes: metro, LRT, BRT. Each cell is the percentage of that gap "
            "resolved — the share of G-X sites sitting within 2 km of a new "
            "station. Zero of the 12 cells is above 25%. Most are below 16%. "
            "The single best cell is BRT × vehicle-mismatch (25%). The $10B "
            "closed almost none of the Phase 1 gaps."
        ),
        methodology=(
            "For each (gap, mode) cell: count the gap-category sites (G1 ghosts "
            "n=115, G2 empty-return terminals n=19, G3 vehicle-mismatch routes "
            "n=~1,340, G4 underserved hexes n=79), compute the % within a 2-km "
            "haversine buffer of any station of that mode. **Why 2 km?** Standard "
            "walkshed for a Cairo commuter per the World Bank transport study. "
            "The Monorail would be a 4th row but it is not operational yet, so "
            "the matrix is 3 × 4."
        ),
        metric_label="BEST CELL",
        metric_value="25%",
        metric_unit="BRT × VEHICLE MISMATCH · ALL OTHERS LOWER",
        center=[31.25, 30.05], zoom=10.0, pitch=20, bearing=0,
        emphasize_layers=["metro", "lrt", "brt", "informal"],
        dim_layers=["districts"],
        chart="q18b_matrix",
        layla=LaylaPos(kind="fixed", coords=IMBABA, brightness=0.4),
    ),

    # ══════ CHAPTER 12 · MASARI JOURNEY ══════
    Chapter(
        id=12, act="III", title_short="MASARI",
        kicker="STAGE 12 · THE SOFTWARE ANSWER",
        headline="Masari · one route planner for both systems",
        arabic="مَسَارِي · تطبيق واحد",
        body=(
            "The infrastructure failed her. The software can still succeed. "
            "Masari ingests TfC's GTFS for System A and crowdsources System B "
            "from microbus passengers. The first product is a planner that "
            "finally shows Layla her entire journey in one screen. The "
            "addressable market is 18 million residents across the Established "
            "Core and Peripheral Growth clusters."
        ),
        methodology=(
            "The 18M comes from Phase 2 Q24 **K-Means segmentation**. k = 4, "
            "selected by elbow + silhouette (peaks at k=2 = 0.63, but we forced "
            "k = 4 for policy granularity). **Stability: ARI = 1.00 across 10 "
            "random seeds** — the clusters are robust. Target = Cluster 1 "
            "(Established Cairo Core, n = 23, 0.95% CAGR, 290k mean population) + "
            "Cluster 2 (Peripheral Growth, n = 22, 4.2% CAGR, 95k mean population). "
            "Total = 45 districts ≈ 18 million residents. The polyline Layla is "
            "travelling right now is the Masari microbus→metro→return leg, "
            "rendered as a `TripsLayer` over 10 seconds."
        ),
        metric_label="MASARI · ADDRESSABLE MARKET",
        metric_value="18M",
        metric_unit="ESTABLISHED CORE + PERIPHERAL",
        center=[31.22, 30.02], zoom=10.6, pitch=50, bearing=-5,
        emphasize_layers=["masari_route", "metro", "home", "office"],
        dim_layers=["lrt", "brt"],
        chart=None,
        layla=LaylaPos(kind="animated", route="masari_microbus", brightness=1.0),
    ),

    # ══════ CHAPTER 13 · ARRIVAL ══════
    Chapter(
        id=13, act="III", title_short="ARRIVAL",
        kicker="STAGE 13 · ARRIVAL",
        headline="08:55 — she arrives on time",
        arabic="وصلت في الموعد",
        body=(
            "One app. One integrated system. Forty minutes instead of eighty-three. "
            "Today Layla and 1.4 million Cairenes like her pay three times the "
            "per-kilometer cost of the metro for a commute that takes more than "
            "an hour longer than it should. The infrastructure did not reach them. "
            "The software can."
        ),
        methodology=(
            "The 40-minute projection uses the GTFS route graph for System A and "
            "the crowdsourced microbus graph for System B, run through a standard "
            "Dijkstra shortest-path with transfer penalties calibrated from "
            "explorecity.life wait-time distributions. The 3× per-km fare ratio: "
            "metro = 0.18 LE/km (TfC fare_attributes), microbus = 0.55 LE/km "
            "(Phase 1 cleaned_routes.csv). Masari's value is not route invention — "
            "it is route visibility across both systems simultaneously."
        ),
        metric_label="LAYLA · MORNING",
        metric_value="08:55",
        metric_unit="ARRIVED ON TIME",
        center=MAADI, zoom=13.6, pitch=55, bearing=20,
        emphasize_layers=["office", "metro"],
        dim_layers=["lrt", "brt", "informal"],
        chart=None,
        layla=LaylaPos(kind="fixed", coords=MAADI, brightness=1.0, show_image=True),
    ),
]
