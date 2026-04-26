"""PyDeck map renderer — Carto dark-matter + glow layers + Layla node."""
from __future__ import annotations

import math
import time
from pathlib import Path
from typing import List, Optional

import pandas as pd
import pydeck as pdk

from data import loader
from data.paths import ASSETS_DIR, ROUTES_DIR
from utils.assets import layla_icon_data
from utils.geo import interpolate_polyline, load_geojson_polyline


_LAYLA_ICON: Optional[dict] = None
_ROUTES_CACHE: Optional[dict] = None


def _layla_icon() -> dict:
    global _LAYLA_ICON
    if _LAYLA_ICON is None:
        _LAYLA_ICON = layla_icon_data(ASSETS_DIR / "layla_portrait.png")
    return _LAYLA_ICON


def _load_routes() -> dict:
    global _ROUTES_CACHE
    if _ROUTES_CACHE is None:
        _ROUTES_CACHE = {
            "chaos":           load_geojson_polyline(ROUTES_DIR / "chaos.geojson"),
            "masari_microbus": load_geojson_polyline(ROUTES_DIR / "masari_microbus.geojson"),
            "masari_metro":    load_geojson_polyline(ROUTES_DIR / "masari_metro.geojson"),
            "masari_return":   load_geojson_polyline(ROUTES_DIR / "masari_return.geojson"),
        }
    return _ROUTES_CACHE


# ─── layer builders ──────────────────────────────────────────────────

def _path_layer_pair(coords: List[List[float]], rgb: List[int], name: str, opacity: float = 1.0) -> List[pdk.Layer]:
    """Outer glow + inner sharp line — the 'dark + lighten' route look."""
    if not coords or len(coords) < 2:
        return []
    alpha_glow = int(40 * opacity)
    alpha_inner = int(255 * opacity)
    data = [{"path": coords}]
    return [
        pdk.Layer(
            "PathLayer", data=data, get_path="path",
            get_color=rgb + [alpha_glow], width_min_pixels=12,
            rounded=True, pickable=False, id=f"{name}_glow",
        ),
        pdk.Layer(
            "PathLayer", data=data, get_path="path",
            get_color=rgb + [alpha_inner], width_min_pixels=3,
            rounded=True, pickable=False, id=f"{name}_inner",
        ),
    ]


def _station_layers(df: pd.DataFrame, rgb: List[int], name: str, opacity: float = 1.0,
                    dot_radius: int = 60, glow_radius: int = 180) -> List[pdk.Layer]:
    if df.empty:
        return []
    alpha_glow = int(30 * opacity)
    alpha_dot = int(230 * opacity)
    return [
        pdk.Layer(
            "ScatterplotLayer", data=df,
            get_position=["lng", "lat"],
            get_radius=glow_radius, radius_units="meters",
            get_fill_color=rgb + [alpha_glow], stroked=False,
            pickable=False, id=f"{name}_glow",
        ),
        pdk.Layer(
            "ScatterplotLayer", data=df,
            get_position=["lng", "lat"],
            get_radius=dot_radius, radius_units="meters",
            get_fill_color=rgb + [alpha_dot], stroked=True,
            get_line_color=[13, 17, 23, 255], line_width_min_pixels=1,
            pickable=True, id=f"{name}_dot",
            tooltip={"text": "{name}"} if "name" in df.columns else None,
        ),
    ]


def _layla_layers(position: List[float], brightness: float = 1.0) -> List[pdk.Layer]:
    pulse_base = 60 + 40 * math.sin(time.time() * 2.4)
    pulse_alpha = max(0, int(pulse_base * brightness))
    icon = _layla_icon()
    return [
        pdk.Layer(
            "ScatterplotLayer",
            data=[{"coordinates": position}],
            get_position="coordinates",
            get_radius=220, radius_units="meters",
            get_fill_color=[232, 111, 81, pulse_alpha], stroked=False,
            pickable=False, id="layla_pulse",
        ),
        pdk.Layer(
            "IconLayer",
            data=[{"coordinates": position, "icon": icon}],
            get_position="coordinates",
            get_icon="icon",
            get_size=3, size_scale=18 * brightness,
            pickable=True, id="layla_icon",
        ),
    ]


def _home_office_markers(chapter) -> List[pdk.Layer]:
    from data.findings import COMMUTE
    data = []
    if "home" in chapter.emphasize_layers:
        data.append({"lng": COMMUTE["home_coords"][0], "lat": COMMUTE["home_coords"][1], "kind": "HOME"})
    if "office" in chapter.emphasize_layers:
        data.append({"lng": COMMUTE["office_coords"][0], "lat": COMMUTE["office_coords"][1], "kind": "OFFICE"})
    if "crow_line" in chapter.emphasize_layers:
        coords = [COMMUTE["home_coords"], COMMUTE["office_coords"]]
        crow_layer = pdk.Layer(
            "PathLayer", data=[{"path": coords}], get_path="path",
            get_color=[233, 196, 106, 200], width_min_pixels=2,
            get_dash_array=[4, 4], id="crow_line",
        )
        return [crow_layer]
    if not data:
        return []
    df = pd.DataFrame(data)
    return _station_layers(df, [232, 111, 81], "home_office", dot_radius=100, glow_radius=300)


# ─── main deck builder ───────────────────────────────────────────────

def build_deck(chapter, layla_coords: Optional[List[float]] = None) -> pdk.Deck:
    """Build a PyDeck map for the given chapter state."""
    emph = set(chapter.emphasize_layers or [])
    dim = set(chapter.dim_layers or [])

    def vis(key: str) -> float:
        if key in emph:
            return 1.0
        if key in dim:
            return 0.3
        return 0.0

    layers: List[pdk.Layer] = []

    # Informal terminal overlay (coral dots)
    if vis("informal") > 0 or vis("informal_ghost") > 0:
        inf = loader.load_informal_terminals()
        if not inf.empty:
            op = max(vis("informal"), vis("informal_ghost"))
            layers.extend(_station_layers(inf, [232, 111, 81], "informal",
                                          opacity=op, dot_radius=80, glow_radius=160))

    # Metro
    if vis("metro") > 0:
        metro = loader.load_metro_stations()
        layers.extend(_station_layers(metro, [88, 166, 255], "metro", opacity=vis("metro")))

    # LRT
    if vis("lrt") > 0:
        lrt = loader.load_lrt_stations()
        layers.extend(_station_layers(lrt, [123, 45, 142], "lrt", opacity=vis("lrt")))

    # BRT
    if vis("brt") > 0:
        brt = loader.load_brt_stations()
        layers.extend(_station_layers(brt, [233, 196, 106], "brt", opacity=vis("brt"),
                                      dot_radius=90, glow_radius=220))

    # Districts (simple circle overlay)
    if vis("districts") > 0:
        districts = loader.load_districts()
        if "coverage" in districts.columns:
            under = districts[districts["coverage"] == "under"]
            over = districts[districts["coverage"] == "over"]
            layers.extend(_station_layers(under, [232, 111, 81], "districts_under",
                                          opacity=vis("districts"), dot_radius=400, glow_radius=1200))
            layers.extend(_station_layers(over, [42, 157, 143], "districts_over",
                                          opacity=vis("districts"), dot_radius=400, glow_radius=1200))

    # Chaos route
    if vis("chaos_route") > 0:
        routes = _load_routes()
        layers.extend(_path_layer_pair(routes["chaos"], [232, 111, 81],
                                       "chaos_route", opacity=vis("chaos_route")))

    # Masari triple-leg route (Chapter 12)
    if vis("masari_route") > 0:
        routes = _load_routes()
        layers.extend(_path_layer_pair(routes["masari_microbus"], [232, 111, 81],
                                       "masari_microbus", opacity=vis("masari_route")))
        layers.extend(_path_layer_pair(routes["masari_metro"], [88, 166, 255],
                                       "masari_metro", opacity=vis("masari_route")))
        layers.extend(_path_layer_pair(routes["masari_return"], [42, 157, 143],
                                       "masari_return", opacity=vis("masari_route")))

    # Home/office markers + crow line
    layers.extend(_home_office_markers(chapter))

    # Layla node — rendered on every map unless explicitly hidden
    if chapter.layla and layla_coords:
        brightness = getattr(chapter.layla, "brightness", 1.0)
        layers.extend(_layla_layers(layla_coords, brightness=brightness))

    # View state — linear transition between chapters
    view_state = pdk.ViewState(
        longitude=chapter.center[0],
        latitude=chapter.center[1],
        zoom=chapter.zoom,
        pitch=chapter.pitch,
        bearing=chapter.bearing,
    )

    deck = pdk.Deck(
        map_style="dark_no_labels",
        map_provider="carto",
        initial_view_state=view_state,
        layers=layers,
        parameters={"clearColor": [13 / 255, 17 / 255, 23 / 255, 1]},
        tooltip={"text": "{name}"},
    )
    return deck


def resolve_layla_position(chapter, session_state) -> List[float]:
    """Compute Layla's current [lng, lat] based on chapter + state."""
    from data.findings import COMMUTE

    lay = chapter.layla
    if lay is None:
        return COMMUTE["home_coords"]

    if lay.kind == "fixed":
        return list(lay.coords) if lay.coords else COMMUTE["home_coords"]

    if lay.kind == "route":
        routes = _load_routes()
        polyline = routes.get(lay.route, [])
        if polyline:
            return interpolate_polyline(polyline, lay.progress or 0.0)
        return COMMUTE["home_coords"]

    if lay.kind == "animated":
        routes = _load_routes()
        elapsed = time.time() - session_state.get("chapter_entered_at", time.time())
        total = 10.0
        progress = max(0.0, min(1.0, elapsed / total))

        if progress < 0.3:
            seg = progress / 0.3
            poly = routes.get(lay.route or "masari_microbus", [])
        elif progress < 0.7:
            seg = (progress - 0.3) / 0.4
            poly = routes.get("masari_metro", [])
        else:
            seg = (progress - 0.7) / 0.3
            poly = routes.get("masari_return", [])

        if poly:
            return interpolate_polyline(poly, seg)
        return COMMUTE["home_coords"]

    return COMMUTE["home_coords"]
