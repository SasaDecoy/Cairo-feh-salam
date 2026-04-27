"""
Live computations from the cleaned CSVs — never hard-code.

This module mirrors the exact analytical operations in
`Phase2/Phase2_Analysis_Hypothesis.ipynb` so the Streamlit app shows the same
numbers a fresh notebook run would produce. If a CSV is missing the
functions fall back to the published `data.findings` constants.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from data.paths import PHASE1_CLEAN, PHASE2_CLEAN
from data import findings


# ─── Q18b · gap-closure matrix ────────────────────────────────────────

@st.cache_data(show_spinner=False)
def compute_q18b_matrix() -> dict:
    """Recompute the Q18b gap-closure matrix live from the CSVs.

    Mirrors notebook cell 83: for each Phase 1 gap (G1 ghosts, G2 empty-return,
    G3 vehicle mismatch, G4 top-quartile underserved) and each post-2014 mode
    (Metro L3, LRT, BRT), compute the % of gap sites within 2 km of any
    station of that mode.

    Returns the same shape as `findings.Q18B`:
        dict(modes=[...], gaps=[...], values=[[...], ...], note=str, source=str)

    Falls back to `findings.Q18B` if any required CSV is missing.
    """
    try:
        import geopandas as gpd
        from shapely import wkt
    except ImportError:
        return {**findings.Q18B, "source": "fallback (geopandas missing)"}

    P1 = PHASE1_CLEAN
    P2 = PHASE2_CLEAN

    needed = [
        P1 / "cleaned_population.csv",
        P1 / "merged_G_underused_terminals.csv",
        P1 / "merged_B_terminals_population.csv",
        P1 / "merged_D_terminal_flow_ratios.csv",
        P1 / "merged_F_routes_per_terminal.csv",
        P1 / "q9_underserved.csv",
        P2 / "metro_stations.csv",
        P2 / "lrt_stations.csv",
        P2 / "brt_stations.csv",
    ]
    if not all(p.exists() for p in needed):
        return {**findings.Q18B, "source": "fallback (CSV missing)"}

    # ── Phase 1 population hexes (G4) ──
    p1_pop = pd.read_csv(P1 / "cleaned_population.csv")
    geom_col = next((c for c in p1_pop.columns if "geom" in c.lower()), None)
    if geom_col is None:
        return {**findings.Q18B, "source": "fallback (no geom column)"}
    p1_pop_gdf = gpd.GeoDataFrame(
        p1_pop, geometry=p1_pop[geom_col].apply(wkt.loads), crs="EPSG:32636"
    )

    # ── Helper to load a Phase-1 terminal-set as a GeoDataFrame ──
    tb = pd.read_csv(P1 / "merged_B_terminals_population.csv")

    def _terminal_subset(ids):
        sub = tb[tb["Terminal_ID"].isin(ids)][["Terminal_ID", "geometry"]].drop_duplicates("Terminal_ID")
        return gpd.GeoDataFrame(sub, geometry=sub["geometry"].apply(wkt.loads), crs="EPSG:32636")

    # G1 ghost terminals
    g1_src = pd.read_csv(P1 / "merged_G_underused_terminals.csv")
    g1_gdf = _terminal_subset(g1_src.loc[g1_src["Underused"] == True, "Terminal_ID"])

    # G2 empty-return (Empty_Return_Index >= 0.9 in the latest notebook)
    g2_flow = pd.read_csv(P1 / "merged_D_terminal_flow_ratios.csv")
    g2_gdf = _terminal_subset(g2_flow.loc[g2_flow["Empty_Return_Index"] >= 0.9, "Terminal_ID"])

    # G3 vehicle mismatch (route length > 50 km)
    g3_src = pd.read_csv(P1 / "merged_F_routes_per_terminal.csv")
    g3_gdf = _terminal_subset(g3_src.loc[g3_src["Avg_Route_Len_Origin"] > 50, "Terminal_ID"])

    # G4 top-quartile underserved hexes
    q9 = pd.read_csv(P1 / "q9_underserved.csv")
    q9_top = q9[q9["Underserved_Score"] >= q9["Underserved_Score"].quantile(0.75)]
    g4_gdf = p1_pop_gdf[p1_pop_gdf["H3_Hex_ID"].isin(q9_top["H3_Hex_ID"])].copy()

    # ── Mode stations ──
    def _to_metric(df: pd.DataFrame) -> "gpd.GeoDataFrame":
        df = df.dropna(subset=["lat", "lon"]).copy()
        if df.empty:
            return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy([], []), crs="EPSG:32636")
        return gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326"
        ).to_crs("EPSG:32636")

    metro = pd.read_csv(P2 / "metro_stations.csv")
    metro_g = _to_metric(metro)
    new_metro = metro_g[
        (metro_g.get("line", "") == "Line 3") & (metro_g.get("opening_year", 0) >= 2014)
    ]
    lrt_g = _to_metric(pd.read_csv(P2 / "lrt_stations.csv"))
    brt_g = _to_metric(pd.read_csv(P2 / "brt_stations.csv"))

    def pct_within(gap_gdf, mode_gdf, buffer_m=2000):
        """Match the Phase 2 notebook (cell 81) exactly: centroid-to-station
        nearest-neighbour distance < buffer_m. Using `within` on the raw
        polygon under-counts G4 hexes that straddle the 2 km boundary."""
        if len(gap_gdf) == 0 or len(mode_gdf) == 0:
            return 0.0
        try:
            from sklearn.neighbors import NearestNeighbors
            import numpy as np
        except ImportError:
            # Fallback: centroid within union of buffered stations
            union = mode_gdf.geometry.buffer(buffer_m).union_all()
            return float(gap_gdf.geometry.centroid.within(union).sum()) / len(gap_gdf) * 100

        gap_centroids = gap_gdf.geometry.centroid
        G = np.column_stack([gap_centroids.x.values, gap_centroids.y.values])
        M = np.column_stack([mode_gdf.geometry.x.values, mode_gdf.geometry.y.values])
        nn = NearestNeighbors(n_neighbors=1).fit(M)
        dist, _ = nn.kneighbors(G)
        return float((dist[:, 0] < buffer_m).sum()) / len(gap_gdf) * 100

    gaps_order = ["GHOSTS", "EMPTY-RETURN", "VEHICLE MISMATCH", "UNDER-SERVED"]
    modes_order = ["METRO L3", "LRT", "BRT"]
    gap_gdfs = [g1_gdf, g2_gdf, g3_gdf, g4_gdf]
    mode_gdfs = [new_metro, lrt_g, brt_g]

    values = []
    for mg in mode_gdfs:
        row = []
        for gg in gap_gdfs:
            row.append(round(pct_within(gg, mg), 1))
        values.append(row)

    return dict(
        modes=modes_order,
        gaps=gaps_order,
        values=values,
        note=("Live from CSVs · gap site counts: "
              f"G1={len(g1_gdf)} · G2={len(g2_gdf)} · "
              f"G3={len(g3_gdf)} · G4={len(g4_gdf)} · "
              f"mode counts: Metro L3 post-2014={len(new_metro)} · "
              f"LRT={len(lrt_g)} · BRT={len(brt_g)}"),
        source="live (CSV recomputation)",
    )


# ─── Q14 · ghost-terminal distance buckets (live) ─────────────────────

@st.cache_data(show_spinner=False)
def compute_q14_buckets() -> dict:
    """Recompute Q14: distance from every Phase 1 ghost to the nearest
    post-2014 metro station. Bucket counts in (0–1, 1–2, 2–5, 5–10, >10 km).
    """
    try:
        import geopandas as gpd
        import numpy as np
        from shapely import wkt
    except ImportError:
        return {**findings.Q14, "source": "fallback (geopandas missing)"}

    P1 = PHASE1_CLEAN
    P2 = PHASE2_CLEAN
    needed = [
        P1 / "merged_G_underused_terminals.csv",
        P1 / "merged_B_terminals_population.csv",
        P2 / "metro_stations.csv",
    ]
    if not all(p.exists() for p in needed):
        return {**findings.Q14, "source": "fallback (CSV missing)"}

    g1 = pd.read_csv(P1 / "merged_G_underused_terminals.csv")
    g1 = g1[g1["Underused"] == True]
    tb = pd.read_csv(P1 / "merged_B_terminals_population.csv")
    g1_geom = tb[tb["Terminal_ID"].isin(g1["Terminal_ID"])][["Terminal_ID", "geometry"]].drop_duplicates("Terminal_ID")
    g1_gdf = gpd.GeoDataFrame(g1_geom, geometry=g1_geom["geometry"].apply(wkt.loads), crs="EPSG:32636")
    g1_gdf["x"] = g1_gdf.geometry.centroid.x
    g1_gdf["y"] = g1_gdf.geometry.centroid.y

    metro = pd.read_csv(P2 / "metro_stations.csv").dropna(subset=["lat", "lon"])
    metro_g = gpd.GeoDataFrame(
        metro, geometry=gpd.points_from_xy(metro["lon"], metro["lat"]), crs="EPSG:4326"
    ).to_crs("EPSG:32636")
    new_metro = metro_g[(metro_g["line"] == "Line 3") & (metro_g["opening_year"] >= 2014)]
    if len(new_metro) == 0:
        return {**findings.Q14, "source": "fallback (no new metro)"}

    G = np.column_stack([g1_gdf["x"], g1_gdf["y"]])
    M = np.column_stack([new_metro.geometry.x, new_metro.geometry.y])
    dists = []
    for x, y in G:
        d = np.sqrt(((M - [x, y]) ** 2).sum(axis=1)).min()
        dists.append(d)
    import numpy as np
    dists = np.array(dists)
    bins = [0, 1000, 2000, 5000, 10000, np.inf]
    labels = ["0-1 km", "1-2 km", "2-5 km", "5-10 km", ">10 km"]
    cuts = pd.cut(dists, bins=bins, labels=labels, include_lowest=True)
    counts = cuts.value_counts().reindex(labels, fill_value=0).tolist()

    total = len(dists)
    within_1km = int((dists < 1000).sum())
    beyond_2km = int((dists > 2000).sum())
    return dict(
        total_ghosts=total,
        within_1km=within_1km,
        within_1km_pct=round(within_1km / total * 100),
        beyond_2km=beyond_2km,
        beyond_2km_pct=round(beyond_2km / total * 100),
        buckets=list(zip(labels, counts)),
        source="live (CSV recomputation)",
    )


# ─── Q21 · Fare per km · informal medians (live), formal from notebook ─

@st.cache_data(show_spinner=False)
def compute_q21_fares() -> dict:
    """Microbus and Tomnaya fare-per-km medians live from cleaned_routes.csv.

    Bus and Metro fares stay on the notebook-reported values because the
    GTFS fare_attributes feed only carries 3 zone-level prices, which is
    not enough to derive a per-km median naively.
    """
    P1 = PHASE1_CLEAN
    out = dict(**findings.Q21)
    out["source"] = "fallback (no informal route data)"

    cr = P1 / "cleaned_routes.csv"
    if not cr.exists():
        return out
    try:
        routes = pd.read_csv(cr)
        if "Vehicle_Type" not in routes.columns or "Fare" not in routes.columns or "Route_Length_km" not in routes.columns:
            return out
        for vname, key in [("Microbus", "microbus"), ("Tomnaya", "tomnaya")]:
            sub = routes[routes["Vehicle_Type"].astype(str).str.contains(vname, case=False, na=False)]
            if len(sub):
                valid = sub.dropna(subset=["Fare", "Route_Length_km"])
                valid = valid[valid["Route_Length_km"] > 0]
                if len(valid):
                    per_km = (valid["Fare"] / valid["Route_Length_km"]).median()
                    out["fares_egp_per_km"] = {**out["fares_egp_per_km"], key: round(float(per_km), 2)}
                    out["n_routes"] = {**out.get("n_routes", {}), key: int(len(valid))}
        out["source"] = "live (informal medians from cleaned_routes.csv) + notebook (formal)"
    except Exception:
        pass
    return out


# ─── Q22 · Most-under-served residuals (live OLS) ─────────────────────

@st.cache_data(show_spinner=False)
def compute_q22_residuals() -> dict:
    """Recompute Q22: OLS of metro stations on population per district;
    return ranked residuals."""
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
    except ImportError:
        return {**findings.Q22, "source": "fallback (sklearn missing)"}

    P2 = PHASE2_CLEAN
    needed = [P2 / "districts_wide.csv", P2 / "metro_stations.csv"]
    if not all(p.exists() for p in needed):
        return {**findings.Q22, "source": "fallback (CSV missing)"}

    try:
        districts = pd.read_csv(P2 / "districts_wide.csv")
        metro = pd.read_csv(P2 / "metro_stations.csv").dropna(subset=["lat", "lon"])

        # Skip if no centroid columns
        lat_col = next((c for c in districts.columns if "lat" in c.lower() and "centroid" in c.lower()), None)
        lon_col = next((c for c in districts.columns if ("lon" in c.lower() or "lng" in c.lower()) and "centroid" in c.lower()), None)
        pop_col = next((c for c in districts.columns if c.lower() in ("pop_2023", "pop_2017")), None)
        if not (lat_col and lon_col and pop_col):
            return {**findings.Q22, "source": "fallback (schema mismatch)"}

        d = districts.dropna(subset=[lat_col, lon_col, pop_col]).copy()
        if d.empty:
            return {**findings.Q22, "source": "fallback (no data)"}

        # For each district: count metro stations within ~3 km haversine
        def km(lat1, lon1, lat2, lon2):
            R = 6371.0
            d2r = np.pi / 180
            a = np.sin((lat2-lat1)*d2r/2)**2 + np.cos(lat1*d2r)*np.cos(lat2*d2r)*np.sin((lon2-lon1)*d2r/2)**2
            return 2*R*np.arcsin(np.sqrt(a))

        m_lat = metro["lat"].values
        m_lon = metro["lon"].values
        counts = []
        for _, row in d.iterrows():
            dists = km(row[lat_col], row[lon_col], m_lat, m_lon)
            counts.append(int((dists < 3.0).sum()))
        d["n_stations"] = counts

        # OLS: stations ~ population
        X = d[[pop_col]].values
        y = d["n_stations"].values
        reg = LinearRegression().fit(X, y)
        d["predicted"] = reg.predict(X)
        d["residual"] = d["n_stations"] - d["predicted"]

        name_col = next((c for c in d.columns if c.lower() == "name"), d.columns[0])
        worst = d.nsmallest(10, "residual")[[name_col, "residual"]]
        worst_pairs = [(str(r[name_col]), round(float(r["residual"]), 2)) for _, r in worst.iterrows()]

        return dict(
            method="OLS regression of metro stations on population (3 km buffer per district centroid)",
            most_under_served=worst_pairs[:4],
            most_under_served_full=worst_pairs,
            slope=float(reg.coef_[0]),
            intercept=float(reg.intercept_),
            n_districts=len(d),
            source="live (CSV recomputation)",
        )
    except Exception as e:
        return {**findings.Q22, "source": f"fallback ({type(e).__name__})"}


# ─── Q19 · Live GTFS agency route counts ──────────────────────────────

@st.cache_data(show_spinner=False)
def compute_q19_counts() -> dict:
    """Live GTFS agency route counts split by formal/informal."""
    P2 = PHASE2_CLEAN
    routes_path = P2 / "gtfs_routes.csv"
    if not routes_path.exists():
        return dict(formal_count=0, informal_count=0, semi_count=0, total=0,
                    source="fallback (CSV missing)")
    try:
        routes = pd.read_csv(routes_path)
        if "agency_id" not in routes.columns:
            return dict(formal_count=0, informal_count=0, semi_count=0, total=0,
                        source="fallback (no agency_id)")
        FORMAL = {"CTA", "NAT"}
        SEMI = {"CTA_M"}
        formal = routes["agency_id"].isin(FORMAL).sum()
        semi   = routes["agency_id"].isin(SEMI).sum()
        informal = len(routes) - formal - semi
        return dict(
            formal_count=int(formal),
            semi_count=int(semi),
            informal_count=int(informal),
            total=int(len(routes)),
            source="live (CSV recomputation)",
        )
    except Exception:
        return dict(formal_count=0, informal_count=0, semi_count=0, total=0,
                    source="fallback (parse error)")


# ─── Source counts (used in cleaning section + KPIs) ──────────────────

@st.cache_data(show_spinner=False)
def compute_source_counts() -> dict:
    """Live row counts per scraped source — used by the cleaning pages."""
    out = {}
    for key, path in [
        ("metro",      PHASE2_CLEAN / "metro_stations.csv"),
        ("lrt",        PHASE2_CLEAN / "lrt_stations.csv"),
        ("brt",        PHASE2_CLEAN / "brt_stations.csv"),
        ("districts",  PHASE2_CLEAN / "districts.csv"),
        ("districts_wide", PHASE2_CLEAN / "districts_wide.csv"),
        ("gtfs_stops", PHASE2_CLEAN / "gtfs_stops.csv"),
        ("gtfs_routes", PHASE2_CLEAN / "gtfs_routes.csv"),
        ("gtfs_fares", PHASE2_CLEAN / "gtfs_fare_attributes.csv"),
    ]:
        if path.exists():
            try:
                df = pd.read_csv(path)
                with_coords = None
                if "lat" in df.columns and ("lon" in df.columns or "lng" in df.columns):
                    lon_col = "lon" if "lon" in df.columns else "lng"
                    with_coords = int(df.dropna(subset=["lat", lon_col]).shape[0])
                out[key] = dict(rows=int(len(df)), with_coords=with_coords)
            except Exception:
                out[key] = dict(rows=None, with_coords=None)
        else:
            out[key] = dict(rows=None, with_coords=None)
    out["source"] = "live (CSV recomputation)"
    return out


# ─── Phase 1 gap counts (live) ────────────────────────────────────────

@st.cache_data(show_spinner=False)
def compute_gap_counts() -> dict:
    """Live counts for the four Phase 1 structural gaps."""
    P1 = PHASE1_CLEAN
    out = dict(source="live (CSV recomputation)")

    # G1
    if (P1 / "merged_G_underused_terminals.csv").exists():
        g1 = pd.read_csv(P1 / "merged_G_underused_terminals.csv")
        out["G1_count"] = int((g1["Underused"] == True).sum())
    # G2
    if (P1 / "merged_D_terminal_flow_ratios.csv").exists():
        g2 = pd.read_csv(P1 / "merged_D_terminal_flow_ratios.csv")
        out["G2_count_60"] = int((g2["Empty_Return_Index"] >= 0.60).sum())
        out["G2_count_90"] = int((g2["Empty_Return_Index"] >= 0.90).sum())
    # G3
    if (P1 / "merged_F_routes_per_terminal.csv").exists():
        g3 = pd.read_csv(P1 / "merged_F_routes_per_terminal.csv")
        out["G3_count_long_50km"] = int((g3["Avg_Route_Len_Origin"] > 50).sum())
    # G4
    if (P1 / "q9_underserved.csv").exists():
        q9 = pd.read_csv(P1 / "q9_underserved.csv")
        out["G4_count_strict"] = int((q9["Underserved_Score"] > 0.5).sum())
        out["G4_count_top_quartile"] = int(
            (q9["Underserved_Score"] >= q9["Underserved_Score"].quantile(0.75)).sum()
        )
    return out
