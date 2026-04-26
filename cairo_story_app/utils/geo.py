"""Geometry utilities: haversine + polyline interpolation."""
from __future__ import annotations

import math
from typing import List, Sequence


def haversine(a: Sequence[float], b: Sequence[float]) -> float:
    """Great-circle distance between two [lng, lat] points, in metres."""
    R = 6_371_000.0
    lng1, lat1 = math.radians(a[0]), math.radians(a[1])
    lng2, lat2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def interpolate_polyline(points: List[List[float]], progress: float) -> List[float]:
    """Interpolate along a polyline by cumulative distance. `progress` in [0, 1]."""
    if not points:
        return [0.0, 0.0]
    if progress <= 0:
        return list(points[0])
    if progress >= 1:
        return list(points[-1])

    seg_lens = [haversine(points[i], points[i + 1]) for i in range(len(points) - 1)]
    total = sum(seg_lens)
    if total == 0:
        return list(points[0])

    target = progress * total
    covered = 0.0
    for i, seg in enumerate(seg_lens):
        if covered + seg >= target:
            t = (target - covered) / seg if seg > 0 else 0.0
            a, b = points[i], points[i + 1]
            return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
        covered += seg
    return list(points[-1])


def load_geojson_polyline(path) -> List[List[float]]:
    """Load a single-feature LineString GeoJSON into a list of [lng, lat] points."""
    import json
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return []
    with p.open() as f:
        gj = json.load(f)

    if gj.get("type") == "FeatureCollection":
        features = gj.get("features", [])
        if not features:
            return []
        geom = features[0].get("geometry", {})
    elif gj.get("type") == "Feature":
        geom = gj.get("geometry", {})
    else:
        geom = gj

    if geom.get("type") == "LineString":
        return [list(pt) for pt in geom.get("coordinates", [])]
    return []
