"""
Cached loaders. Prefer Phase 2 / Phase 1 CSVs; fall back to inline constants.
All loaders return pandas DataFrames with columns [name, lng, lat, mode, ...]
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import fallback
from data.paths import PHASE1_CLEAN, PHASE2_CLEAN, PHASE2_INTEGRATED


# ─── helpers ─────────────────────────────────────────────────────────

def _normalize_lnglat(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce any (lng, lat) / (longitude, latitude) / (x, y) pair into lng/lat cols."""
    pairs = [
        ("lng", "lat"),
        ("longitude", "latitude"),
        ("lon", "lat"),
        ("x", "y"),
    ]
    for lng_col, lat_col in pairs:
        if lng_col in df.columns and lat_col in df.columns:
            if (lng_col, lat_col) != ("lng", "lat"):
                df = df.rename(columns={lng_col: "lng", lat_col: "lat"})
            return df
    return df


def _normalize_name(df: pd.DataFrame) -> pd.DataFrame:
    """Promote the first available English-name column to `name`."""
    if "name" in df.columns:
        return df
    for c in ("station_en", "Terminal_Name", "translated_en", "raw_name", "name_en"):
        if c in df.columns:
            return df.rename(columns={c: "name"})
    return df


# ─── Phase 2 stations ────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_metro_stations() -> pd.DataFrame:
    path = PHASE2_CLEAN / "metro_stations.csv"
    if path.exists():
        df = pd.read_csv(path)
        df = _normalize_lnglat(_normalize_name(df))
        if "lng" in df.columns and "lat" in df.columns:
            df = df.dropna(subset=["lng", "lat"]).copy()
            keep = [c for c in ["name", "lng", "lat", "line", "opening_year", "phase",
                                "is_interchange"] if c in df.columns]
            df = df[keep].copy()
            df["mode"] = "metro"
            return df
    return pd.DataFrame(fallback.METRO_POST_2014)


@st.cache_data(show_spinner=False)
def load_lrt_stations() -> pd.DataFrame:
    path = PHASE2_CLEAN / "lrt_stations.csv"
    if path.exists():
        df = pd.read_csv(path)
        df = _normalize_lnglat(_normalize_name(df))
        if "lng" in df.columns and "lat" in df.columns:
            df = df.dropna(subset=["lng", "lat"]).copy()
            df["mode"] = "lrt"
            keep = [c for c in ["name", "lng", "lat", "is_operational", "line",
                                "status"] if c in df.columns] + ["mode"]
            return df[keep]
    return pd.DataFrame(fallback.LRT_STATIONS)


@st.cache_data(show_spinner=False)
def load_brt_stations() -> pd.DataFrame:
    path = PHASE2_CLEAN / "brt_stations.csv"
    if path.exists():
        df = pd.read_csv(path)
        df = _normalize_lnglat(_normalize_name(df))
        if "lng" in df.columns and "lat" in df.columns:
            df = df.dropna(subset=["lng", "lat"]).copy()
            df["mode"] = "brt"
            if "demand" not in df.columns and "passenger_count" in df.columns:
                df["demand"] = df["passenger_count"]
            keep = [c for c in ["name", "lng", "lat", "demand"] if c in df.columns] + ["mode"]
            return df[keep]
    return pd.DataFrame(fallback.BRT_STATIONS)


@st.cache_data(show_spinner=False)
def load_all_stations() -> pd.DataFrame:
    return pd.concat(
        [load_metro_stations(), load_lrt_stations(), load_brt_stations()],
        ignore_index=True,
    )


# ─── Phase 2 districts ───────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_districts() -> pd.DataFrame:
    wide = PHASE2_CLEAN / "districts_wide.csv"
    if wide.exists():
        df = pd.read_csv(wide)
        df = _normalize_lnglat(df)
        return df
    path = PHASE2_CLEAN / "districts.csv"
    if path.exists():
        df = pd.read_csv(path)
        df = _normalize_lnglat(df)
        return df
    return pd.DataFrame(fallback.DISTRICTS)


# ─── Phase 1 terminals / boarding ────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_phase1_terminals() -> pd.DataFrame:
    path = PHASE1_CLEAN / "cleaned_terminals.csv"
    if path.exists():
        df = pd.read_csv(path)
        return _normalize_lnglat(df)
    return pd.DataFrame(columns=["name", "lng", "lat"])


@st.cache_data(show_spinner=False)
def load_phase1_underserved() -> pd.DataFrame:
    path = PHASE1_CLEAN / "q9_underserved.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_phase1_underused_terminals() -> pd.DataFrame:
    path = PHASE1_CLEAN / "merged_G_underused_terminals.csv"
    if path.exists():
        df = pd.read_csv(path)
        return _normalize_lnglat(df)
    return pd.DataFrame()


# ─── Phase 2 integration ─────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_matched_pairs() -> pd.DataFrame:
    path = PHASE2_INTEGRATED / "matched_pairs.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


# ─── informal point overlay ──────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_informal_terminals() -> pd.DataFrame:
    """Informal/ghost terminal points — fallback to inline list."""
    phase1 = load_phase1_underused_terminals()
    if not phase1.empty and "lng" in phase1.columns:
        return phase1[["lng", "lat"]].copy()
    return pd.DataFrame(fallback.INFORMAL_TERMINALS, columns=["lng", "lat"])


# ─── Phase 2 GTFS routes (Q19 visualization) ─────────────────────────

# agency_id → human-readable name (resolved against the bundle's agency.txt
# in Phase2_Scraping_Cleaning.ipynb cell 80). Hard-mapped here because the
# saved CSV stores agency_id only.
GTFS_AGENCY_LABELS = {
    "P_O_14": "Paratransit · 14-seater microbus (orange plates)",
    "P_B_8":  "Paratransit · 8-seater Suzuki/Chevy (blue plates)",
    "CTA":    "Cairo Transport Authority (formal bus)",
    "CTA_M":  "Minibus licensed by CTA",
    "BOX":    "Box paratransit (microbus minibus)",
    "COOP":   "Cooperative paratransit · 29-seater (grey plates)",
    "NAT":    "National Authority for Tunnels (Metro)",
}

# Mode classification per agency_id — used by Q19 to colour formal vs informal.
GTFS_AGENCY_MODE = {
    "CTA":    "formal",
    "NAT":    "formal",
    "CTA_M":  "semi-formal",
    "P_O_14": "informal",
    "P_B_8":  "informal",
    "COOP":   "informal",
    "BOX":    "informal",
}


@st.cache_data(show_spinner=False)
def load_gtfs_routes_by_agency() -> pd.DataFrame:
    """Q19 source: GTFS route counts per agency, sorted by route_count desc.

    Returns columns: agency_id, agency_name, route_count, mode.
    """
    path = PHASE2_CLEAN / "gtfs_routes.csv"
    if not path.exists():
        return pd.DataFrame(columns=["agency_id", "agency_name", "route_count", "mode"])
    routes = pd.read_csv(path)
    if "agency_id" not in routes.columns:
        return pd.DataFrame(columns=["agency_id", "agency_name", "route_count", "mode"])
    counts = (routes.groupby("agency_id").size()
              .rename("route_count").reset_index()
              .sort_values("route_count", ascending=False))
    counts["agency_name"] = counts["agency_id"].map(GTFS_AGENCY_LABELS).fillna(counts["agency_id"])
    counts["mode"] = counts["agency_id"].map(GTFS_AGENCY_MODE).fillna("informal")
    return counts.reset_index(drop=True)


# ─── Phase 2 OSM cross-verification ──────────────────────────────────

@st.cache_data(show_spinner=False)
def load_osm_features() -> pd.DataFrame:
    """Phase 2 OSM features for cross-verification overlay.

    Returns columns: name, lng, lat, transport_type (best-effort).
    """
    path = PHASE2_CLEAN / "osm_features.geojson"
    if not path.exists():
        return pd.DataFrame(columns=["name", "lng", "lat", "transport_type"])
    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            gj = json.load(f)
        rows = []
        for feat in gj.get("features", []):
            props = feat.get("properties") or {}
            # The geojson is in EPSG:32636, but the original lat/lon are
            # preserved in the properties — use those directly.
            lat = props.get("lat")
            lon = props.get("lon") or props.get("lng") or props.get("longitude")
            if lat is None or lon is None:
                continue
            try:
                lat = float(lat); lon = float(lon)
            except (TypeError, ValueError):
                continue
            rows.append({
                "name": props.get("name_en") or props.get("name") or "(unnamed)",
                "lng": lon, "lat": lat,
                "transport_type": props.get("public_transport") or props.get("railway")
                                  or props.get("highway") or props.get("amenity") or "transport",
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df[(df["lng"].between(31.0, 31.9)) & (df["lat"].between(29.7, 30.4))].reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame(columns=["name", "lng", "lat", "transport_type"])
