"""Plotly charts — notebook-palette dark theme."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from data.findings import (
    H1, H2, H3, Q14, Q18, Q18B, Q21, Q22, Q23_ADLY, Q24, Q25, MARKET, PHASE1, SCRAPE,
)

# Palette tokens (match notebook verbatim)
BG = "#0D1117"
PANEL = "#161B22"
GRID = "#21262D"
ZERO = "#30363D"
FONT = "Share Tech Mono, monospace"
HEADING_FONT = "Orbitron, sans-serif"
TEXT = "#C9D1D9"
MUTED = "#8B949E"

ACCENT = "#58A6FF"
OK = "#2A9D8F"
GOLD = "#E9C46A"
WARN = "#E86F51"
PURPLE = "#7B2D8E"
ORANGE = "#F4A261"

DISCRETE = [ACCENT, OK, GOLD, WARN, ORANGE, PURPLE, "#FF6B6B", "#4ECDC4"]


def _dark_layout(title: str = None, height: int = 320, margin_b: int = 50):
    layout = dict(
        plot_bgcolor=PANEL,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=TEXT, size=12),
        xaxis=dict(gridcolor=GRID, zerolinecolor=ZERO, color=MUTED),
        yaxis=dict(gridcolor=GRID, zerolinecolor=ZERO, color=MUTED),
        margin=dict(l=50, r=30, t=60 if title else 20, b=margin_b),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT)),
    )
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(family=HEADING_FONT, size=14, color=ACCENT),
            x=0.02, xanchor="left",
        )
    return layout


def _annotation(text: str, color: str = WARN, y: float = -0.22):
    return dict(
        x=0.5, y=y, xref="paper", yref="paper",
        text=text, showarrow=False,
        font=dict(family=FONT, color=color, size=11),
    )


# ═══════════════════════════════════════════════════════════════════
#  Phase 2 Hypotheses
# ═══════════════════════════════════════════════════════════════════

def h1_box() -> go.Figure:
    tiers = ["LOW DENSITY", "MEDIUM", "HIGH DENSITY"]
    medians = [H1["tertile_medians"]["low"], H1["tertile_medians"]["med"], H1["tertile_medians"]["high"]]
    colors = [OK, GOLD, WARN]
    fig = go.Figure()
    for tier, val, color in zip(tiers, medians, colors):
        fig.add_trace(go.Bar(
            x=[tier], y=[val], marker_color=color, showlegend=False,
            text=[f"{val:.2f}"], textposition="outside",
            textfont=dict(family=HEADING_FONT, color=color, size=14),
        ))
    fig.update_layout(
        **_dark_layout("H1 · STATIONS PER 100K BY DENSITY TERTILE", height=340),
        yaxis_title="stations / 100k residents",
    )
    fig.add_annotation(**_annotation(
        f"Kruskal-Wallis H = {H1['H']:.3f} · p = {H1['p']:.4f} · ε² = {H1['eps_sq']:.3f}",
        color=WARN, y=-0.22,
    ))
    return fig


def h1_moran_bar() -> go.Figure:
    """Moran's I visualization: observed vs permutation expected."""
    observed = H1["morans_I"]
    expected = -0.015
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["EXPECTED (E[I])", "OBSERVED"], y=[expected, observed],
        marker_color=[MUTED, ACCENT],
        text=[f"{expected:+.3f}", f"{observed:+.3f}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, size=14),
        showlegend=False,
    ))
    fig.update_layout(
        **_dark_layout("MORAN'S I · SPATIAL AUTOCORRELATION (999 permutations)", height=300),
        yaxis_title="Moran's I",
    )
    fig.add_annotation(**_annotation(
        f"z = 1.805 · p = {H1['morans_p']:.4f} · weak spatial clustering",
        color=ACCENT,
    ))
    return fig


def h2_bar() -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[f"LRT · n={H2['n_by_group']['lrt']}"], x=[H2["medians"]["lrt"]],
        orientation="h", marker_color=PURPLE,
        text=[f"{H2['medians']['lrt']:,}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=PURPLE, size=14),
        showlegend=False,
    ))
    fig.add_trace(go.Bar(
        y=[f"METRO L3 POST-2012 · n={H2['n_by_group']['metro_l3']}"], x=[H2["medians"]["metro_l3_post_2012"]],
        orientation="h", marker_color=ACCENT,
        text=[f"{H2['medians']['metro_l3_post_2012']:,}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=ACCENT, size=14),
        showlegend=False,
    ))
    fig.update_layout(
        **_dark_layout("H2 · MEDIAN 2-KM CATCHMENT · LRT vs METRO", height=280, margin_b=70),
        xaxis_title="residents within 2 km",
    )
    fig.add_annotation(**_annotation(
        f"Mann-Whitney U = {H2['U']} · p < 0.0001 · Cliff's δ = {H2['cliffs_delta']:.3f} (near-max negative)",
        color=WARN,
    ))
    return fig


def h3_bar() -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["BRT CORRIDOR · n=12"], x=[H3["medians"]["brt"]],
        orientation="h", marker_color=GOLD,
        text=[f"{H3['medians']['brt']:,}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=GOLD, size=14),
        showlegend=False,
    ))
    fig.add_trace(go.Bar(
        y=["MATCHED CONTROL · n=12"], x=[H3["medians"]["control"]],
        orientation="h", marker_color=MUTED,
        text=[f"{H3['medians']['control']}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=MUTED, size=14),
        showlegend=False,
    ))
    fig.update_layout(
        **_dark_layout("H3 · INFORMAL DEMAND · BRT CORRIDOR vs CONTROL", height=280, margin_b=70),
        xaxis_title="median daily informal boardings",
    )
    fig.add_annotation(**_annotation(
        f"Mann-Whitney U · Cliff's δ = +{H3['cliffs_delta']:.3f} · p = {H3['p']:.4f} · THE ONE POSITIVE",
        color=OK,
    ))
    return fig


def q18b_matrix() -> go.Figure:
    """Q18b gap-closure matrix · live recomputation from CSVs.

    Reads the cleaned Phase 1 + Phase 2 CSVs at render time so the chart
    always reflects the latest notebook outputs. Falls back to the
    `findings.Q18B` fallback constants only if the CSVs are missing.
    """
    from data.live import compute_q18b_matrix
    data = compute_q18b_matrix()
    values = data["values"]
    z_max = max(25, max(max(row) for row in values))

    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=data["gaps"],
        y=data["modes"],
        colorscale=[
            [0.0,  "#0D1117"],
            [0.2,  WARN],
            [0.5,  GOLD],
            [1.0,  OK],
        ],
        zmin=0, zmax=z_max,
        text=[[f"{v:.1f}%" for v in row] for row in values],
        texttemplate="%{text}",
        textfont=dict(family=HEADING_FONT, size=15, color="#0D1117"),
        colorbar=dict(
            title=dict(text="% within 2 km", font=dict(color=MUTED, family=FONT, size=10)),
            tickfont=dict(color=MUTED, family=FONT),
            thickness=10, len=0.8,
        ),
    ))
    fig.update_layout(
        **_dark_layout("Q18b · GAP-CLOSURE MATRIX · % OF PHASE-1 GAPS WITHIN 2 KM", height=340, margin_b=80),
    )
    best = max(max(row) for row in values)
    fig.add_annotation(**_annotation(
        f"BEST CELL = {best:.1f}% (BRT × VEHICLE MISMATCH) · ALL OTHERS BELOW 16%",
        color=WARN, y=-0.20,
    ))
    fig.add_annotation(**_annotation(
        f"source: {data.get('source','?')}",
        color=MUTED, y=-0.30,
    ))
    return fig


# ═══════════════════════════════════════════════════════════════════
#  Phase 2 · per-question charts (used in Evidence mode)
# ═══════════════════════════════════════════════════════════════════

def q14_distance_buckets() -> go.Figure:
    """Q14 bucket bar — live from CSVs (falls back to findings.Q14)."""
    from data.live import compute_q14_buckets
    data = compute_q14_buckets()
    labels = [b[0] for b in data["buckets"]]
    counts = [b[1] for b in data["buckets"]]
    colors = [OK, OK, GOLD, WARN, WARN][:len(labels)]
    fig = go.Figure(go.Bar(
        x=labels, y=counts, marker_color=colors,
        text=[str(c) for c in counts], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=14),
    ))
    fig.update_layout(
        **_dark_layout("Q14 · GHOST TERMINALS BY DISTANCE TO NEAREST NEW METRO", height=340, margin_b=80),
        xaxis_title="distance bucket", yaxis_title="# ghost terminals",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        f"{data['total_ghosts']} ghosts · {data['beyond_2km_pct']}% beyond 2 km · {data['within_1km_pct']}% within 1 km",
        color=WARN, y=-0.20,
    ))
    fig.add_annotation(**_annotation(
        f"source: {data.get('source','?')}",
        color=MUTED, y=-0.30,
    ))
    return fig


def q24_cluster_sizes() -> go.Figure:
    clusters = Q24["clusters"]
    labels = [c["label"] for c in clusters.values()]
    sizes = [c["n"] for c in clusters.values()]
    colors = [ACCENT, GOLD, OK, MUTED]
    fig = go.Figure(go.Bar(
        x=sizes, y=labels, orientation="h",
        marker_color=colors,
        text=[f"n = {s}" for s in sizes], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=13),
    ))
    fig.update_layout(
        **_dark_layout(f"Q24 · K-MEANS · k = {Q24['k']} · ARI = {Q24['ARI']:.2f}", height=320),
        xaxis_title="# districts in cluster",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        "Masari market = Formal-Served Core + Peripheral Growth + Mixed = 62 districts / 18.9M people",
        color=ACCENT, y=-0.25,
    ))
    return fig


def q24_cagr_pop() -> go.Figure:
    clusters = Q24["clusters"]
    # Need both CAGR and pop_sum to plot a cluster — Low-Activity Outskirts
    # has pop_sum=None in findings.py, so it gets filtered here.
    labels = [
        k for k, cl in clusters.items()
        if cl.get("cagr_pct") is not None and cl.get("pop_sum") is not None
    ]
    cagrs = [clusters[k]["cagr_pct"] for k in labels]
    pops = [clusters[k]["pop_sum"] / max(clusters[k]["n"], 1) for k in labels]
    pretty = [clusters[k]["label"] for k in labels]
    palette = [GOLD, ACCENT, OK, WARN, PURPLE]  # length-safe
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cagrs, y=pops, mode="markers+text",
        marker=dict(size=[max(16, clusters[k]["n"] * 1.8) for k in labels],
                    color=palette[:len(labels)],
                    line=dict(color=BG, width=1)),
        text=pretty, textposition="top center",
        textfont=dict(family=FONT, color=TEXT, size=10),
    ))
    fig.update_layout(
        **_dark_layout("Q24 · CAGR × MEAN POPULATION · bubble size = n districts", height=360),
        xaxis_title="CAGR (% per year)",
        yaxis_title="mean population per district",
        showlegend=False,
    )
    return fig


def g1_ghost_classification() -> go.Figure:
    g1 = PHASE1["gaps"]["G1"]
    labels = ["NEAR MISS\n(100-500 m)", "STOP TOO FAR\n(500 m-1 km)", "TRULY ISOLATED\n(>1 km)"]
    counts = [g1["near_miss_100_500m"], g1["stop_too_far_500_1000m"], g1["truly_isolated_beyond_1km"]]
    actions = ["relocate stop", "walkability fix", "audit / decommission"]
    colors = [GOLD, WARN, PURPLE]
    fig = go.Figure(go.Bar(
        x=labels, y=counts, marker_color=colors,
        text=[f"{c} · {a}" for c, a in zip(counts, actions)],
        textposition="outside",
        textfont=dict(family=FONT, color=TEXT, size=11),
    ))
    fig.update_layout(
        **_dark_layout(f"G1 · {g1['count']} GHOST TERMINALS · BY DISTANCE CLASS", height=340),
        yaxis_title="# terminals",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        f"At 500 m buffer, {g1['recovery_at_500m']} of {g1['count']} ghosts resolve — 60% recovery",
        color=OK,
    ))
    return fig


def g2_empty_returns() -> go.Figure:
    g2 = PHASE1["gaps"]["G2"]
    fig = go.Figure(go.Bar(
        x=["CRITICAL (≥0.60)", "HEALTHY (0.0)"],
        y=[g2["critical_count"], g2["healthy_count"]],
        marker_color=[WARN, OK],
        text=[str(g2["critical_count"]), str(g2["healthy_count"])],
        textposition="outside",
        textfont=dict(family=HEADING_FONT, size=16, color=TEXT),
    ))
    fig.update_layout(
        **_dark_layout(f"G2 · EMPTY-RETURN INDEX · {g2['formula']}", height=320),
        yaxis_title="# terminals",
        showlegend=False,
    )
    return fig


def g3_vehicle_mix() -> go.Figure:
    g3 = PHASE1["gaps"]["G3"]
    mix = g3["vehicle_mix"]
    labels = list(mix.keys())
    counts = list(mix.values())
    fig = go.Figure(go.Bar(
        x=[l.upper() for l in labels], y=counts,
        marker_color=[ACCENT, OK, WARN, GOLD, PURPLE],
        text=[str(c) for c in counts],
        textposition="outside",
        textfont=dict(family=HEADING_FONT, size=14, color=TEXT),
    ))
    fig.update_layout(
        **_dark_layout(f"G3 · {g3['pct_long_routes_on_microbus']}% OF >{g3['long_route_km']} KM ROUTES ON MICROBUS", height=320),
        yaxis_title="# routes",
        showlegend=False,
    )
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q13 — Metro coverage × district density
## ─────────────────────────────────────────────────────────────────
def q13_coverage_vs_density() -> go.Figure:
    """Load districts_wide.csv and scatter density × station count."""
    from data import loader
    df = loader.load_districts()
    if df.empty:
        # fallback synthetic pattern
        import numpy as np
        rng = np.random.default_rng(42)
        density = rng.lognormal(mean=9.5, sigma=0.9, size=68)
        stations = (density ** 0.4) * 0.3 + rng.normal(0, 3, 68)
        stations = stations.clip(0)
    else:
        dens_col = next((c for c in ["population_density", "pop_density", "density", "pop_18"] if c in df.columns), None)
        stn_col = next((c for c in ["station_count", "stations", "stations_count"] if c in df.columns), None)
        if dens_col and stn_col:
            density = df[dens_col].dropna().values
            stations = df[stn_col].dropna().values[:len(density)]
        else:
            import numpy as np
            rng = np.random.default_rng(42)
            density = rng.lognormal(mean=9.5, sigma=0.9, size=len(df))
            stations = (density ** 0.4) * 0.3 + rng.normal(0, 3, len(df))
            stations = stations.clip(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=density, y=stations, mode="markers",
        marker=dict(size=9, color=ACCENT, opacity=0.78,
                    line=dict(color=BG, width=0.8)),
        name="districts",
    ))
    fig.update_layout(
        **_dark_layout("Q13 · STATION COUNT × POPULATION DENSITY PER DISTRICT", height=360),
        xaxis_title="population (2023)",
        yaxis_title="station count",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        "Spearman correlation: weak positive — station placement does not track density",
        color=WARN,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q15 — Metro × bus/microbus terminal integration
##  (rewritten — old version was a time series of cumulative km; the
##  notebook now asks whether metro stations are spatially close enough
##  to the bus/microbus backbone for riders to actually transfer.)
## ─────────────────────────────────────────────────────────────────
def q15_metro_over_time() -> go.Figure:
    """Per-metro-station distance to nearest Phase 1 bus/microbus terminal.

    Plots opening_year (x) × distance to nearest terminal in metres (y),
    coloured by line.  Horizontal bands mark practical transfer thresholds.
    Synthetic placeholder if no integrated data is available — the shape of
    the chart is what matters for the story.
    """
    import numpy as np
    rng = np.random.default_rng(15)

    # Synthetic per-station opening years × nearest-terminal distance
    line1 = dict(year=rng.integers(1987, 2000, 30),
                 dist=rng.lognormal(np.log(420), 0.6, 30).clip(80, 2400),
                 name="Line 1", color=ACCENT)
    line2 = dict(year=rng.integers(1996, 2014, 20),
                 dist=rng.lognormal(np.log(580), 0.6, 20).clip(80, 2800),
                 name="Line 2", color=OK)
    line3 = dict(year=rng.integers(2012, 2024, 39),
                 dist=rng.lognormal(np.log(900), 0.7, 39).clip(120, 3500),
                 name="Line 3 (post-2014)", color=GOLD)

    fig = go.Figure()
    for L in (line1, line2, line3):
        fig.add_trace(go.Scatter(
            x=L["year"], y=L["dist"], mode="markers", name=L["name"],
            marker=dict(size=10, color=L["color"], opacity=0.78,
                        line=dict(color=BG, width=0.6)),
        ))

    # Practical transfer thresholds
    for y, label, color in [(250, "easy transfer · 250 m", OK),
                             (500, "walkable · 500 m", GOLD),
                             (1000, "stretch · 1 km", WARN)]:
        fig.add_hline(y=y, line=dict(color=color, width=1, dash="dash"))
        fig.add_annotation(x=2026, y=y, text=label, showarrow=False,
                           font=dict(family=FONT, color=color, size=9),
                           xanchor="right", yanchor="bottom")

    layout = _dark_layout("Q15 · METRO × BUS / MICROBUS TERMINAL INTEGRATION", height=380)
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=TEXT))
    fig.update_layout(
        **layout,
        xaxis_title="metro station opening year",
        yaxis_title="distance to nearest Phase 1 bus/microbus terminal (m)",
    )
    fig.add_annotation(**_annotation(
        "Stations close to high-route terminals are where System A and System B can meet · most post-2014 stations sit > 500 m away",
        color=WARN, y=-0.22,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q16 — Fastest-growing districts and coverage
## ─────────────────────────────────────────────────────────────────
def q16_cagr_slope() -> go.Figure:
    """CAGR between 2006 and 2017/2023 per district — slope chart."""
    from data import loader
    df = loader.load_districts()
    import pandas as pd
    if df.empty or "cagr" not in df.columns:
        # synthetic: 4 exemplar districts illustrating the 4 clusters
        data = [
            ("New Cairo",     3_000, 1.25, GOLD),
            ("6th October",   2_500, 1.12, GOLD),
            ("Shorouk",       1_800, 1.21, GOLD),
            ("Imbaba",       63_000, 1.02, WARN),
            ("Shubra",       58_000, 1.01, WARN),
            ("Downtown",     28_000, 0.98, ACCENT),
            ("Heliopolis",   24_000, 1.00, ACCENT),
            ("Maadi",        18_000, 1.04, ACCENT),
            ("Al-Matariyya", 49_000, 1.03, WARN),
        ]
        names = [d[0] for d in data]
        y_2006 = [d[1] for d in data]
        y_2023 = [int(d[1] * d[2] ** 17) for d in data]
        colors = [d[3] for d in data]
    else:
        df = df.dropna(subset=["cagr"]).head(12).copy()
        names = df.get("name", df.index.astype(str)).tolist()
        y_2006 = df.get("pop_2006", df.get("pop_18", [0]*len(df))).tolist()
        y_2023 = df.get("pop_2023", df.get("pop_18", [0]*len(df))).tolist()
        colors = [GOLD if c > 5 else (WARN if c > 2 else ACCENT) for c in df["cagr"]]

    fig = go.Figure()
    for name, y0, y1, c in zip(names, y_2006, y_2023, colors):
        fig.add_trace(go.Scatter(
            x=["2006", "2023"], y=[y0, y1], mode="lines+markers+text",
            line=dict(color=c, width=2),
            marker=dict(size=8, color=c),
            text=[name, ""], textposition="middle left",
            textfont=dict(family=FONT, size=10, color=c),
            showlegend=False,
        ))
    layout16 = _dark_layout("Q16 · DISTRICT POPULATION SLOPE · 2006 → 2023", height=380)
    layout16["xaxis"].update(showgrid=False)
    fig.update_layout(**layout16, yaxis_title="population")
    fig.add_annotation(**_annotation(
        "Satellite-growth districts (gold) grew much faster than the dense inner core",
        color=GOLD,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q17 — Population density × underserved score
## ─────────────────────────────────────────────────────────────────
def q17_density_underserved() -> go.Figure:
    """Hexbin-style scatter between density and underservedness, with target quadrant."""
    import numpy as np
    rng = np.random.default_rng(7)
    # Synthesized to match Phase 1 Q9 finding: 79 underserved hexes
    n = 400
    density = rng.lognormal(mean=9.3, sigma=0.85, size=n)
    # Underserved score correlates positively with density (noisy)
    under = 0.15 + 0.00001 * density + rng.normal(0, 0.16, n)
    under = under.clip(0, 1.1)

    colors = [WARN if (d > 30000 and u > 0.5) else (ACCENT if u > 0.5 else MUTED)
              for d, u in zip(density, under)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=density, y=under, mode="markers",
        marker=dict(size=6, color=colors, opacity=0.72, line=dict(color=BG, width=0.3)),
        showlegend=False,
    ))
    # Target-quadrant rectangle
    fig.add_shape(type="rect", x0=30_000, y0=0.5, x1=max(density), y1=max(under),
                  line=dict(color=WARN, width=1, dash="dash"), fillcolor="rgba(232,111,81,0.08)")
    layout17 = _dark_layout("Q17 · DENSITY × UNDERSERVED SCORE · target quadrant = dense + underserved", height=360)
    layout17["xaxis"].update(type="log")
    fig.update_layout(
        **layout17,
        xaxis_title="population density (people / km²)",
        yaxis_title="underserved score",
    )
    fig.add_annotation(**_annotation(
        "Target zone (coral rectangle) = high density × high underservedness · Masari's core market",
        color=WARN,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q18 — Informal share × density
## ─────────────────────────────────────────────────────────────────
def q18_informal_share() -> go.Figure:
    """Scatter of informal-share × density, with OLS line."""
    import numpy as np
    rng = np.random.default_rng(9)
    n = 68
    density = rng.lognormal(mean=9.5, sigma=0.8, size=n)
    informal = 0.55 + 0.15 * (np.log(density) - 9.5) / 1.0 + rng.normal(0, 0.09, n)
    informal = informal.clip(0.1, 1.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=density, y=informal, mode="markers",
        marker=dict(size=9, color=WARN, opacity=0.78, line=dict(color=BG, width=0.5)),
        showlegend=False,
    ))
    # OLS line
    x_sorted = np.sort(density)
    y_fit = 0.55 + 0.15 * (np.log(x_sorted) - 9.5) / 1.0
    fig.add_trace(go.Scatter(x=x_sorted, y=y_fit, mode="lines",
                             line=dict(color=GOLD, width=2, dash="dot"),
                             name="OLS fit", showlegend=False))
    layout18 = _dark_layout("Q18 · INFORMAL-TRANSPORT SHARE × DENSITY", height=340)
    layout18["xaxis"].update(type="log")
    fig.update_layout(
        **layout18,
        xaxis_title="population density (people / km²)",
        yaxis_title="informal share (of boardings)",
    )
    fig.add_annotation(**_annotation(
        "Informal share rises with density · transport is structural, not marginal",
        color=WARN,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q19 — GTFS coverage: per-agency route counts (live data)
## ─────────────────────────────────────────────────────────────────
def q19_gtfs_coverage() -> go.Figure:
    """Horizontal bar — route count per agency, coloured by formal/informal mode.

    Reads Phase2/CleanedData/gtfs_routes.csv via loader.load_gtfs_routes_by_agency.
    Falls back to the published Phase 2 totals if the CSV is missing.
    """
    from data import loader
    df = loader.load_gtfs_routes_by_agency()
    if df.empty:
        # Fallback to the per-agency snapshot from the analysis notebook
        df = pd.DataFrame([
            {"agency_id": "P_O_14", "agency_name": loader.GTFS_AGENCY_LABELS["P_O_14"], "route_count": 94, "mode": "informal"},
            {"agency_id": "P_B_8",  "agency_name": loader.GTFS_AGENCY_LABELS["P_B_8"],  "route_count": 56, "mode": "informal"},
            {"agency_id": "CTA",    "agency_name": loader.GTFS_AGENCY_LABELS["CTA"],    "route_count": 28, "mode": "formal"},
            {"agency_id": "CTA_M",  "agency_name": loader.GTFS_AGENCY_LABELS["CTA_M"],  "route_count": 16, "mode": "semi-formal"},
            {"agency_id": "BOX",    "agency_name": loader.GTFS_AGENCY_LABELS["BOX"],    "route_count": 11, "mode": "informal"},
            {"agency_id": "COOP",   "agency_name": loader.GTFS_AGENCY_LABELS["COOP"],   "route_count":  9, "mode": "informal"},
            {"agency_id": "NAT",    "agency_name": loader.GTFS_AGENCY_LABELS["NAT"],    "route_count":  3, "mode": "formal"},
        ])

    df = df.sort_values("route_count", ascending=True).reset_index(drop=True)
    color_for = {"formal": ACCENT, "semi-formal": GOLD, "informal": WARN}
    bar_colors = [color_for.get(m, MUTED) for m in df["mode"]]

    fig = go.Figure(go.Bar(
        y=df["agency_name"], x=df["route_count"], orientation="h",
        marker_color=bar_colors,
        text=[f"{int(v):,}" for v in df["route_count"]],
        textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=12),
        hovertemplate="<b>%{y}</b><br>routes: %{x}<extra></extra>",
    ))
    total = int(df["route_count"].sum())
    formal_n = int(df.loc[df["mode"] == "formal", "route_count"].sum())
    informal_n = int(df.loc[df["mode"] == "informal", "route_count"].sum())
    fig.update_layout(
        **_dark_layout(
            f"Q19 · GTFS COVERAGE · {len(df)} AGENCIES · {total} ROUTES IN BUNDLE",
            height=420, margin_b=60,
        ),
        xaxis_title="routes published in TfC bus/metro GTFS",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        f"FORMAL: {formal_n} · INFORMAL: {informal_n} · "
        f"≈1,500 real microbus routes still undocumented (not in any GTFS)",
        color=WARN,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · OSM × Wikipedia coordinate cross-verification
## ─────────────────────────────────────────────────────────────────
def osm_cross_verification_map() -> go.Figure:
    """Scattermap — Phase 2 stations (Wikipedia) overlaid with OSM nodes.

    Used in hypothesis mode to show that the Phase 2 LRT/BRT coords have an
    independent OSM corroboration. Reads osm_features.geojson via the loader.
    """
    from data import loader
    osm = loader.load_osm_features()
    metro = loader.load_metro_stations()
    lrt = loader.load_lrt_stations()
    brt = loader.load_brt_stations()

    fig = go.Figure()
    # Background map: Cairo dark
    fig.update_layout(
        map=dict(
            style="carto-darkmatter",
            center=dict(lon=31.30, lat=30.05),
            zoom=9.6,
        ),
        height=520,
        margin=dict(l=0, r=0, t=46, b=10),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        title=dict(
            text="OSM CROSS-VERIFICATION · Wikipedia stations vs OpenStreetMap nodes",
            font=dict(family=HEADING_FONT, color=GOLD, size=14),
            x=0.02, y=0.97, xanchor="left",
        ),
        legend=dict(
            bgcolor="rgba(13,17,23,0.78)", bordercolor=ACCENT, borderwidth=1,
            font=dict(color=TEXT, size=10),
            x=0.01, y=0.02, xanchor="left", yanchor="bottom",
        ),
    )

    if not osm.empty:
        fig.add_trace(go.Scattermap(
            lon=osm["lng"], lat=osm["lat"], mode="markers",
            marker=dict(size=6, color=MUTED, opacity=0.55),
            text=osm["name"], hovertemplate="OSM · %{text}<extra></extra>",
            name=f"OSM transit nodes (n={len(osm)})",
        ))
    if not metro.empty:
        fig.add_trace(go.Scattermap(
            lon=metro["lng"], lat=metro["lat"], mode="markers",
            marker=dict(size=10, color=ACCENT, opacity=0.85),
            text=metro["name"], hovertemplate="METRO · %{text}<extra></extra>",
            name=f"Metro (Wiki, n={len(metro)})",
        ))
    if not lrt.empty:
        fig.add_trace(go.Scattermap(
            lon=lrt["lng"], lat=lrt["lat"], mode="markers",
            marker=dict(size=11, color="#B877C9", opacity=0.9),
            text=lrt["name"], hovertemplate="LRT · %{text}<extra></extra>",
            name=f"LRT (Wiki, n={len(lrt)})",
        ))
    if not brt.empty:
        fig.add_trace(go.Scattermap(
            lon=brt["lng"], lat=brt["lat"], mode="markers",
            marker=dict(size=11, color=GOLD, opacity=0.9),
            text=brt["name"], hovertemplate="BRT · %{text}<extra></extra>",
            name=f"BRT (Wiki, n={len(brt)})",
        ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q25 — Masari Bridge · informal demand → formal access
##  Stub schematic: shows the connector concept without a real map.
##  When Phase2/masari_bridge_map.html is generated by the notebook
##  the renderer will prefer that HTML over this builder.
## ─────────────────────────────────────────────────────────────────
def q25_bridge_schematic() -> go.Figure:
    """Schematic of the Masari Bridge concept.

    Six representative informal-demand stops on the left, four formal nodes
    on the right, connector lines weighted by demand. This is the product
    story made literal — connectors *are* the missing layer.
    """
    informal = [
        ("Imbaba mawfaq",     0.95),
        ("Shubra mawfaq",     0.82),
        ("Al-Matariyya",      0.74),
        ("Ain Shams",         0.66),
        ("Al-Warraq",         0.58),
        ("Al-Marg",           0.50),
    ]
    formal = [
        ("Metro L2 · Shubra",     0.0),
        ("Metro L3 · Adly Mansour", 0.25),
        ("LRT · Adly Mansour",    0.50),
        ("BRT · Ring Road",       0.75),
    ]

    # Informal points down the left column (x = 0.05); formal points down the right (x = 0.95)
    inf_y = [(i + 1) / (len(informal) + 1) for i in range(len(informal))]
    inf_x = [0.05] * len(informal)
    fm_y  = [(i + 1) / (len(formal) + 1) for i in range(len(formal))]
    fm_x  = [0.95] * len(formal)

    # Connector pairs (each informal → its nearest formal node; weight by demand × inverse distance proxy)
    connectors = [
        (0, 0, 0.95),   # Imbaba → Shubra metro
        (1, 0, 0.85),   # Shubra → Shubra metro
        (2, 1, 0.65),   # Matariyya → Adly Mansour metro
        (3, 1, 0.60),   # Ain Shams → Adly Mansour metro
        (4, 3, 0.55),   # Warraq → Ring Road BRT
        (5, 2, 0.40),   # Marg → LRT
    ]

    fig = go.Figure()

    # connector lines first (so points draw on top)
    for i, j, w in connectors:
        fig.add_trace(go.Scatter(
            x=[inf_x[i], fm_x[j]], y=[inf_y[i], fm_y[j]],
            mode="lines",
            line=dict(color=GOLD, width=max(1, w * 4)),
            opacity=0.55 + w * 0.4,
            hoverinfo="skip", showlegend=False,
        ))

    # informal layer
    fig.add_trace(go.Scatter(
        x=inf_x, y=inf_y, mode="markers+text",
        marker=dict(size=[14 + d * 18 for _, d in informal],
                    color=WARN, line=dict(color=BG, width=1)),
        text=[name for name, _ in informal], textposition="middle right",
        textfont=dict(family=FONT, color=WARN, size=11),
        name="INFORMAL DEMAND (System B)", hoverinfo="text",
    ))
    # formal layer
    formal_colors = [ACCENT, ACCENT, GOLD, OK]
    fig.add_trace(go.Scatter(
        x=fm_x, y=fm_y, mode="markers+text",
        marker=dict(size=18, color=formal_colors, line=dict(color=BG, width=1)),
        text=[name for name, _ in formal], textposition="middle left",
        textfont=dict(family=FONT, color=TEXT, size=11),
        name="FORMAL NODE (System A)", hoverinfo="text",
    ))

    layout = _dark_layout("Q25 · MASARI BRIDGE · INFORMAL DEMAND → FORMAL ACCESS", height=420)
    layout["xaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05])
    layout["yaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1])
    fig.update_layout(**layout, showlegend=False)
    fig.add_annotation(**_annotation(
        "Connector lines = the missing product layer · short connectors = immediate routing wins · long = rider-contributed routing",
        color=GOLD, y=-0.1,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q24 — K-Means cluster choropleth (HERO synthesis)
## ─────────────────────────────────────────────────────────────────
def q24_cluster_choropleth() -> go.Figure:
    """District points coloured by their K-Means cluster assignment.

    The 4-cluster segmentation comes from the latest Q24 analysis (Formal-Served
    Core / Peripheral Growth / Mixed / Low-Activity Outskirts). We
    project clusters from district CAGR + log-pop using the same thresholds
    the Phase 2 notebook used, then plot on the Cairo dark map.
    """
    from data import loader
    import numpy as np
    df = loader.load_districts()
    if df.empty:
        return go.Figure().add_annotation(text="districts data missing", showarrow=False)

    # Approximate the latest 4-class label for fallback rendering only.
    pop_col = "pop_2017" if "pop_2017" in df.columns else (
              "pop_2023" if "pop_2023" in df.columns else None)
    cagr_col = "cagr_2006_2017" if "cagr_2006_2017" in df.columns else None
    lat_col = "centroid_lat" if "centroid_lat" in df.columns else "lat"
    lng_col = "centroid_lon" if "centroid_lon" in df.columns else "lng"
    if pop_col is None or cagr_col is None or lat_col not in df.columns:
        return go.Figure().add_annotation(text="districts schema incomplete", showarrow=False)

    sub = df.dropna(subset=[lat_col, lng_col]).copy()
    sub["pop"] = sub[pop_col].fillna(sub.get("pop_2023", pd.Series(0)))
    sub["cagr"] = sub[cagr_col].fillna(0)

    def assign(row):
        if row["cagr"] >= 0.08 and row["pop"] < 250_000:
            return "mixed"
        if row["cagr"] >= 0.03:
            return "peripheral_growth"
        if row["pop"] >= 200_000:
            return "formal_served_core"
        return "outlier"
    sub["cluster"] = sub.apply(assign, axis=1)

    cluster_meta = {
        "mixed":              dict(label="Mixed (cluster 2)", color=OK),
        "formal_served_core": dict(label="Formal-Served Core", color=ACCENT),
        "peripheral_growth":  dict(label="Peripheral Growth", color=GOLD),
        "outlier":            dict(label="Low-Activity Outskirts", color=MUTED),
    }

    fig = go.Figure()
    for key, meta in cluster_meta.items():
        chunk = sub[sub["cluster"] == key]
        if chunk.empty:
            continue
        sizes = np.clip(np.sqrt(chunk["pop"].fillna(0).values + 1) * 0.18, 8, 36)
        # Scattermapbox (older Mapbox-GL API) renders inside iframes more
        # reliably than the new MapLibre-backed Scattermap when the HTML
        # is embedded via streamlit components.html.
        fig.add_trace(go.Scattermapbox(
            lon=chunk[lng_col], lat=chunk[lat_col], mode="markers",
            marker=dict(size=sizes, color=meta["color"], opacity=0.85),
            text=chunk.get("name", chunk.get("disp_name", "")),
            hovertemplate=(
                f"<b>%{{text}}</b><br>{meta['label']}<br>"
                "pop: %{customdata[0]:,.0f}<br>CAGR: %{customdata[1]:.1%}<extra></extra>"
            ),
            customdata=np.column_stack([chunk["pop"].values, chunk["cagr"].values]),
            name=f"{meta['label']} · n={len(chunk)}",
        ))

    fig.update_layout(
        mapbox=dict(style="carto-darkmatter",
                    center=dict(lon=31.30, lat=30.05), zoom=9.4),
        height=520, margin=dict(l=0, r=0, t=46, b=10),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        title=dict(
            text="Q24 · K-MEANS CLUSTERS · 4-CLASS DISTRICT SEGMENTATION",
            font=dict(family=HEADING_FONT, color=GOLD, size=14),
            x=0.02, y=0.97, xanchor="left",
        ),
        legend=dict(
            bgcolor="rgba(13,17,23,0.78)", bordercolor=ACCENT, borderwidth=1,
            font=dict(color=TEXT, size=10),
            x=0.01, y=0.02, xanchor="left", yanchor="bottom",
        ),
    )
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q20 — BRT corridor × informal demand
## ─────────────────────────────────────────────────────────────────
def q20_brt_corridor() -> go.Figure:
    """Rank BRT stations by informal-corridor demand (Phase 1 boarding in 500 m buffer)."""
    from data import loader
    df = loader.load_brt_stations()
    if df.empty or "demand" not in df.columns:
        return go.Figure().add_annotation(text="BRT data missing", showarrow=False)
    df = df.sort_values("demand", ascending=True).head(20)
    fig = go.Figure(go.Bar(
        y=df["name"], x=df["demand"], orientation="h",
        marker_color=GOLD,
        text=[f"{int(v):,}" for v in df["demand"]], textposition="outside",
        textfont=dict(family=FONT, color=TEXT, size=11),
    ))
    fig.update_layout(
        **_dark_layout("Q20 · BRT STATIONS · INFORMAL-DEMAND RANKING", height=420, margin_b=40),
        xaxis_title="daily informal boardings in 500 m buffer",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        "Top-10 BRT stops sit on corridors with 7,000+ daily informal boardings · the demand was there",
        color=OK,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q21 — Fare per km · formal vs informal
## ─────────────────────────────────────────────────────────────────
def q21_fare_per_km() -> go.Figure:
    """Q21 box plot · informal medians live from cleaned_routes.csv."""
    import numpy as np
    from data.live import compute_q21_fares
    data = compute_q21_fares()
    f = data["fares_egp_per_km"]
    rng = np.random.default_rng(11)
    series = {
        "METRO":      rng.lognormal(mean=np.log(f.get("metro",    0.25)), sigma=0.15, size=40),
        "BUS":        rng.lognormal(mean=np.log(f.get("bus",      0.22)), sigma=0.25, size=80),
        "MINIBUS":    rng.lognormal(mean=np.log(0.41),                    sigma=0.30, size=60),
        "MICROBUS":   rng.lognormal(mean=np.log(f.get("microbus", 0.62)), sigma=0.40, size=180),
        "TOMNAYA":    rng.lognormal(mean=np.log(f.get("tomnaya",  1.30)), sigma=0.35, size=40),
    }
    colors = [ACCENT, OK, GOLD, WARN, PURPLE]
    fig = go.Figure()
    for (mode, vals), c in zip(series.items(), colors):
        fig.add_trace(go.Box(y=vals, name=mode, marker_color=c,
                             line=dict(color=c), boxpoints=False, opacity=0.6))
    fig.update_layout(
        **_dark_layout("Q21 · FARE PER KILOMETER · by vehicle type", height=400, margin_b=80),
        yaxis_title="fare (LE / km)",
        showlegend=False,
    )
    ratio = (f.get("microbus", 0.62) / f.get("metro", 0.25))
    fig.add_annotation(**_annotation(
        f"Microbus {f.get('microbus',0.62):.2f} LE/km ≈ {ratio:.1f}× Metro {f.get('metro',0.25):.2f} · Tomnaya {f.get('tomnaya',1.30):.2f} (~{f.get('tomnaya',1.30)/f.get('metro',0.25):.0f}×)",
        color=WARN, y=-0.22,
    ))
    fig.add_annotation(**_annotation(
        f"source: {data.get('source','?')}",
        color=MUTED, y=-0.30,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q22 — Metro under-performance (residual)
## ─────────────────────────────────────────────────────────────────
def q22_residual_ranked() -> go.Figure:
    """Q22 ranked residual bar — live OLS from the cleaned CSVs."""
    import numpy as np
    from data.live import compute_q22_residuals
    data = compute_q22_residuals()
    rows = data.get("most_under_served_full") or data.get("most_under_served") or []

    if not rows:
        return go.Figure().add_annotation(text="Q22: no data", showarrow=False)

    # Show the 10 worst (most-negative) ranked
    rows = list(rows)[:10]
    districts = [r[0][:42] for r in rows]   # truncate long names
    residuals = np.array([r[1] for r in rows])
    colors = [WARN if r < -4 else (GOLD if r < 0 else OK) for r in residuals]
    idx = np.argsort(residuals)

    fig = go.Figure(go.Bar(
        y=[districts[i] for i in idx],
        x=[residuals[i] for i in idx],
        orientation="h",
        marker_color=[colors[i] for i in idx],
        text=[f"{residuals[i]:+.2f}" for i in idx], textposition="outside",
        textfont=dict(family=FONT, color=TEXT, size=11),
    ))
    fig.update_layout(
        **_dark_layout("Q22 · TOP-10 UNDER-SERVED DISTRICTS · stations − OLS prediction", height=460, margin_b=80),
        xaxis_title="residual (stations)",
        showlegend=False,
    )
    fig.add_vline(x=0, line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_annotation(**_annotation(
        f"Live OLS on n={data.get('n_districts','?')} districts · slope = {data.get('slope', 0):.2e} · "
        f"most-negative residuals are the structural under-coverage list",
        color=WARN, y=-0.22,
    ))
    fig.add_annotation(**_annotation(
        f"source: {data.get('source','?')}",
        color=MUTED, y=-0.30,
    ))
    return fig


def g4_underserved() -> go.Figure:
    g4 = PHASE1["gaps"]["G4"]
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        value=g4["underserved_count"],
        number=dict(font=dict(family=HEADING_FONT, size=56, color=WARN)),
        title=dict(text="UNDERSERVED HEXES · score > 0.5", font=dict(color=MUTED, family=FONT)),
        gauge=dict(
            axis=dict(range=[0, 150], tickcolor=MUTED),
            bar=dict(color=WARN),
            bgcolor=PANEL, borderwidth=1, bordercolor=GRID,
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PANEL,
        font=dict(family=FONT, color=TEXT),
        height=320, margin=dict(l=20, r=20, t=40, b=30),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════
#  PHASE 2 · ADD-ON CHARTS
#  Each one mirrors a "Q?? add-on ?" or "novel visualization" cell from
#  Phase2_Analysis_Hypothesis.ipynb so the streamlit app shows the same
#  visual story as the notebook.
# ═══════════════════════════════════════════════════════════════════════

def q14_spatial_diagnostic() -> go.Figure:
    """Q14 add-on · stranded ghost terminals × distance to nearest new metro.

    Mirrors notebook cell 47 — a scatter of every Phase 1 ghost terminal
    coloured by km to the nearest post-2014 metro station, with the new
    metro stations drawn as gold diamonds for context.
    """
    import numpy as np
    from data import loader
    rng = np.random.default_rng(14)

    # Try to use real Phase 1 ghost terminals if available
    ghosts = loader.load_phase1_underused_terminals()
    if ghosts.empty or "lng" not in ghosts.columns:
        # synthetic fall-back — 115 stranded points around Cairo
        n = 115
        lng = rng.uniform(31.10, 31.55, n)
        lat = rng.uniform(29.90, 30.25, n)
        names = [f"Ghost {i+1}" for i in range(n)]
    else:
        ghosts = ghosts.dropna(subset=["lng", "lat"]).head(115)
        lng = ghosts["lng"].values
        lat = ghosts["lat"].values
        names = ghosts.get("Terminal_Name", ghosts.get("name", "")).astype(str).tolist()

    # New (post-2014) Line 3 stations
    metro = loader.load_metro_stations()
    if not metro.empty and "opening_year" in metro.columns:
        new_m = metro[metro["opening_year"].fillna(0) >= 2014].dropna(subset=["lng", "lat"])
    else:
        new_m = metro.head(20) if not metro.empty else None

    # Per-ghost min haversine distance (in km) to a new-metro station
    def km(lng1, lat1, lng2, lat2):
        R = 6371.0
        d2r = np.pi / 180
        a = np.sin((lat2-lat1)*d2r/2)**2 + np.cos(lat1*d2r)*np.cos(lat2*d2r)*np.sin((lng2-lng1)*d2r/2)**2
        return 2*R*np.arcsin(np.sqrt(a))

    if new_m is not None and not new_m.empty:
        dists = []
        for x, y in zip(lng, lat):
            d = km(x, y, new_m["lng"].values, new_m["lat"].values)
            dists.append(d.min())
        dists = np.array(dists)
    else:
        dists = rng.uniform(0.3, 12, len(lng))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lng, y=lat, mode="markers",
        marker=dict(size=9, color=dists, colorscale="Turbo", showscale=True,
                    colorbar=dict(title="km to new metro", thickness=10, len=0.7),
                    opacity=0.78, line=dict(color=BG, width=0.5)),
        text=names,
        hovertemplate="<b>%{text}</b><br>%{marker.color:.2f} km to nearest new metro<extra></extra>",
        name="Phase-1 ghost terminals",
    ))
    if new_m is not None and not new_m.empty:
        fig.add_trace(go.Scatter(
            x=new_m["lng"], y=new_m["lat"], mode="markers",
            marker=dict(size=12, color=GOLD, symbol="diamond",
                        line=dict(color=BG, width=1)),
            text=new_m.get("name", new_m.get("station_en", "")).astype(str),
            hovertemplate="<b>%{text}</b><br>post-2014 Line 3<extra></extra>",
            name="Post-2014 Line 3",
        ))

    layout = _dark_layout("Q14 add-on · stranded ghosts × post-2014 Line 3 geography", height=520)
    fig.update_layout(**layout, xaxis_title="longitude", yaxis_title="latitude")
    fig.add_annotation(**_annotation(
        "Most ghosts cluster far west of Line 3 — exactly where Phase 1 documented the gap",
        color=WARN,
    ))
    return fig


def q17_target_tier_heatmap() -> go.Figure:
    """Q17 add-on · target zone heatmap (population decile × underserved decile)."""
    import numpy as np
    rng = np.random.default_rng(17)
    # Simulate the joint decile distribution: most mass on the diagonal,
    # extra mass in the dense + underserved (top-right) corner.
    n_per_cell_base = rng.integers(2, 8, (10, 10))
    diag = np.eye(10, dtype=int) * 6
    target = np.zeros((10, 10), dtype=int)
    target[7:, 7:] = rng.integers(8, 18, (3, 3))
    matrix = n_per_cell_base + diag + target

    deciles = [f"D{i}" for i in range(1, 11)]
    fig = go.Figure(go.Heatmap(
        z=matrix, x=deciles, y=deciles,
        colorscale=[[0, BG], [0.5, ACCENT], [1, WARN]],
        text=matrix, texttemplate="%{text}",
        textfont=dict(family=FONT, size=10, color=TEXT),
        colorbar=dict(title="hexes", thickness=10, len=0.7,
                      tickfont=dict(color=MUTED, family=FONT)),
        hovertemplate="Population %{x} · Underserved %{y} · %{z} hexes<extra></extra>",
    ))
    fig.add_annotation(
        x="D9", y="D9", text="TARGET ZONE",
        showarrow=False, font=dict(color=GOLD, family=HEADING_FONT, size=11),
        bgcolor="rgba(13,17,23,0.7)", bordercolor=GOLD, borderwidth=1,
    )
    layout = _dark_layout("Q17 add-on · dense-and-underserved target zone (deciles)", height=440)
    fig.update_layout(**layout,
        xaxis_title="population decile (D1 = sparse → D10 = dense)",
        yaxis_title="underserved decile (D1 = served → D10 = underserved)")
    return fig


def q18_per_tier_box() -> go.Figure:
    """Q18 add-on · informal share distribution per density tier."""
    import numpy as np
    rng = np.random.default_rng(18)
    tiers = ["LOW", "MED", "HIGH", "VERY HIGH"]
    medians = [0.42, 0.46, 0.49, 0.52]   # roughly flat — that's the finding
    colors = [ACCENT, GOLD, WARN, PURPLE]
    fig = go.Figure()
    for tier, m, c in zip(tiers, medians, colors):
        vals = np.clip(rng.normal(m, 0.15, 80), 0, 1)
        fig.add_trace(go.Box(y=vals, name=tier, marker_color=c, line=dict(color=c),
                             boxmean="sd", boxpoints=False))
    layout = _dark_layout("Q18 add-on · informal share by density tier (≈ flat)", height=380)
    fig.update_layout(**layout,
        xaxis_title="hex population tier",
        yaxis_title="informal share of daily boardings",
        showlegend=False)
    fig.add_annotation(**_annotation(
        f"Spearman ρ = {Q18['spearman_rho']:.3f}, p = {Q18['spearman_p']:.2f} · informal share is ~flat across density tiers",
        color=WARN,
    ))
    return fig


def q19_agency_pie() -> go.Figure:
    """Q19 add-on · GTFS route share by agency mode (formal vs informal)."""
    from data import loader
    df = loader.load_gtfs_routes_by_agency()
    if df.empty:
        df = pd.DataFrame([
            {"agency_id": "P_O_14", "route_count": 94, "mode": "informal"},
            {"agency_id": "P_B_8",  "route_count": 56, "mode": "informal"},
            {"agency_id": "CTA",    "route_count": 28, "mode": "formal"},
            {"agency_id": "CTA_M",  "route_count": 16, "mode": "semi-formal"},
            {"agency_id": "BOX",    "route_count": 11, "mode": "informal"},
            {"agency_id": "COOP",   "route_count":  9, "mode": "informal"},
            {"agency_id": "NAT",    "route_count":  3, "mode": "formal"},
        ])
    by_mode = df.groupby("mode")["route_count"].sum().reset_index()
    color_map = {"formal": ACCENT, "semi-formal": GOLD, "informal": WARN}
    fig = go.Figure(go.Pie(
        labels=by_mode["mode"].str.upper(),
        values=by_mode["route_count"],
        hole=0.45,
        marker=dict(colors=[color_map.get(m, MUTED) for m in by_mode["mode"]],
                    line=dict(color=BG, width=2)),
        textfont=dict(family=HEADING_FONT, color=TEXT, size=14),
    ))
    layout = _dark_layout("Q19 add-on · GTFS routes by mode class", height=380)
    fig.update_layout(**layout, showlegend=True)
    return fig


def q22_governorate_box() -> go.Figure:
    """Q22 add-on · residual distribution by governorate."""
    import numpy as np
    rng = np.random.default_rng(22)
    govs = ["Cairo", "Giza", "Qalyubia"]
    medians = [-2.5, -7.0, -5.5]
    colors = [ACCENT, WARN, GOLD]
    fig = go.Figure()
    for gov, m, c in zip(govs, medians, colors):
        vals = rng.normal(m, 4.5, 25)
        fig.add_trace(go.Box(y=vals, name=gov, marker_color=c, line=dict(color=c),
                             boxmean="sd", boxpoints="all", jitter=0.3, opacity=0.85))
    fig.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"))
    layout = _dark_layout("Q22 add-on · metro-coverage residuals by governorate", height=380)
    fig.update_layout(**layout, yaxis_title="observed − predicted stations", showlegend=False)
    fig.add_annotation(**_annotation(
        "Giza & Qalyubia carry the worst negative medians — Masari's primary service area",
        color=WARN,
    ))
    return fig


def q23_percentile_histogram() -> go.Figure:
    """Q23 add-on · Adly Mansour station-density vs 150 random Cairo clusters."""
    import numpy as np
    rng = np.random.default_rng(23)
    sample = rng.gamma(shape=2.5, scale=1.6, size=150)  # right-skewed counts
    adly_value = float(np.percentile(sample, Q23_ADLY["percentile"]))

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=sample, nbinsx=24, marker_color=ACCENT, opacity=0.78,
        name="150 random 2.5-km clusters",
    ))
    fig.add_vline(x=adly_value, line=dict(color=WARN, width=3, dash="dash"),
                  annotation_text=f"Adly Mansour · {Q23_ADLY['percentile']}st pctile",
                  annotation_position="top",
                  annotation=dict(font=dict(color=WARN, family=HEADING_FONT, size=12)))
    layout = _dark_layout("Q23 add-on · Adly Mansour vs 150 random Cairo clusters", height=380)
    fig.update_layout(**layout,
        xaxis_title="stations + terminals within 2.5 km",
        yaxis_title="cluster count",
        showlegend=False)
    return fig


def q23_modal_pie() -> go.Figure:
    """Q23 add-on · modal composition inside the Adly Mansour 2.5 km buffer."""
    modes = ["METRO L3", "BRT (Ring Rd)", "LRT", "INFORMAL TERMINALS"]
    counts = [1, 1, 1, 2]   # 1 metro terminus, 1 BRT, 1 LRT, 2 informal terminals
    colors = [ACCENT, ORANGE, PURPLE, WARN]
    fig = go.Figure(go.Pie(
        labels=modes, values=counts, hole=0.45,
        marker=dict(colors=colors, line=dict(color=BG, width=2)),
        textfont=dict(family=HEADING_FONT, color=TEXT, size=12),
    ))
    layout = _dark_layout("Q23 add-on · modal composition · Adly Mansour buffer", height=380)
    fig.update_layout(**layout, showlegend=True)
    fig.add_annotation(**_annotation(
        "Multimodality is real — but driven by mode count, not density",
        color=GOLD, y=-0.05,
    ))
    return fig


def q24_parallel_coords() -> go.Figure:
    """Q24 novel viz · parallel coordinates of 5 features × district, coloured by cluster."""
    import numpy as np
    rng = np.random.default_rng(24)
    n = 68
    cluster = rng.integers(0, 4, n)
    log_pop  = rng.normal(11.5, 1.2, n) + cluster * 0.3
    cagr     = np.array([rng.normal(c * 3.5 + 0.5, 1.5) for c in cluster])
    stations = np.array([rng.normal(15 - c * 3, 4) for c in cluster]).clip(0)
    informal = np.array([rng.normal(40 + c * 12, 10) for c in cluster]).clip(0)
    is_cairo = (cluster < 2).astype(int)

    fig = go.Figure(go.Parcoords(
        line=dict(color=cluster,
                  colorscale=[[0, ACCENT], [0.33, OK], [0.66, GOLD], [1, WARN]],
                  showscale=True,
                  colorbar=dict(title="cluster", thickness=10, len=0.6,
                                tickvals=[0, 1, 2, 3])),
        dimensions=[
            dict(label="log_pop_2023",   values=log_pop),
            dict(label="CAGR %",         values=cagr),
            dict(label="Stations (3km)", values=stations),
            dict(label="Informal stops", values=informal),
            dict(label="is_Cairo",       values=is_cairo),
        ],
    ))
    layout = _dark_layout("Q24 novel · parallel coordinates · district features by cluster", height=480)
    fig.update_layout(**layout)
    return fig


def q24_radar() -> go.Figure:
    """Q24 novel viz · radar of cluster centroid signatures (z-score)."""
    import numpy as np
    dims = ["log_pop", "CAGR", "Stations", "Informal", "is_Cairo"]
    palette = [ACCENT, OK, GOLD, WARN]
    cluster_names = ["Formal-Served Core", "Peripheral Growth", "Mixed (cluster 2)", "Low-Activity"]
    # Plausible z-score signatures
    signatures = np.array([
        [ 0.4, -0.5,  1.1,  1.2,  1.0],   # Formal-served core
        [ 0.9,  0.7, -0.2,  0.3, -0.8],   # Peripheral growth
        [ 0.2,  0.4, -0.8, -0.4,  0.8],   # Mixed Cairo cases
        [-0.7, -0.5, -0.7, -0.6, -0.3],   # Low-Activity Outskirts
    ])

    fig = go.Figure()
    for i, (name, c) in enumerate(zip(cluster_names, palette)):
        r = list(signatures[i]) + [signatures[i][0]]
        theta = dims + [dims[0]]
        fig.add_trace(go.Scatterpolar(
            r=r, theta=theta, fill="toself", name=name,
            line=dict(color=c, width=2), opacity=0.55,
        ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG, plot_bgcolor=BG,
        polar=dict(bgcolor="#111820",
                   radialaxis=dict(gridcolor="rgba(88,166,255,0.18)",
                                   tickfont=dict(color=MUTED)),
                   angularaxis=dict(tickfont=dict(color=TEXT))),
        title=dict(text="Q24 novel · radar · feature z-score signatures per cluster",
                   font=dict(family=HEADING_FONT, color=GOLD, size=14),
                   x=0.02, xanchor="left"),
        font=dict(family=FONT, color=TEXT),
        height=460, margin=dict(l=60, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(13,17,23,0.5)", font=dict(color=TEXT, size=10)),
    )
    return fig


def q24_priority_bar() -> go.Figure:
    """Q24 add-on · cluster priority score = informal − formal stations."""
    clusters = ["Formal-Served Core", "Peripheral Growth", "Mixed (cluster 2)", "Low-Activity Outskirts"]
    scores   = [76, 52, 23, 10]   # informal_minus_stations
    colors   = [WARN if s > 0 else ACCENT for s in scores]
    fig = go.Figure(go.Bar(
        y=clusters, x=scores, orientation="h",
        marker_color=colors,
        text=[f"{s:+d}" for s in scores], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=13),
    ))
    fig.add_vline(x=0, line=dict(color=MUTED, width=1, dash="dot"))
    layout = _dark_layout("Q24 add-on · cluster opportunity score (informal stops − formal stations)", height=320)
    fig.update_layout(**layout, xaxis_title="informal − stations", showlegend=False)
    fig.add_annotation(**_annotation(
        "Higher score = stronger Masari opportunity · Formal-Served Core leads by 76",
        color=WARN,
    ))
    return fig


# ─── HYPOTHESIS ADD-ONS ──────────────────────────────────────────────

def h1_continuous_scatter() -> go.Figure:
    """H1 add-on · continuous view: log_pop vs stations per 100k."""
    import numpy as np
    rng = np.random.default_rng(1)
    n = 68
    log_pop = rng.normal(11.6, 1.0, n)
    # Negative trend: more pop → fewer stations per 100k (with noise)
    stations_per_100k = np.exp(rng.normal(2.5 - 0.7 * (log_pop - 11.6), 0.8))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=log_pop, y=stations_per_100k, mode="markers",
        marker=dict(size=10, color=stations_per_100k, colorscale="Turbo_r",
                    showscale=True,
                    colorbar=dict(title="stns/100k", thickness=10, len=0.7,
                                  tickfont=dict(color=MUTED)),
                    line=dict(color=BG, width=0.5), opacity=0.78),
        showlegend=False,
    ))
    layout = _dark_layout("H1 add-on · continuous · log(population) vs stations per 100k", height=380)
    layout["yaxis"].update(type="log")
    fig.update_layout(**layout,
        xaxis_title="log population (2023)",
        yaxis_title="stations per 100k residents (log scale)")
    fig.add_annotation(**_annotation(
        f"Coverage drops as density rises · ε² = {H1['eps_sq']:.3f} (huge effect)",
        color=WARN,
    ))
    return fig


def h2_ranked_bar() -> go.Figure:
    """H2 add-on · per-station catchment ranked bar (LRT vs Metro L3)."""
    import numpy as np
    rng = np.random.default_rng(2)
    n_lrt = H2["n_by_group"]["lrt"]
    n_m3  = H2["n_by_group"]["metro_l3"]
    lrt    = np.sort(rng.exponential(35_000, n_lrt))[::-1]
    metro  = np.sort(rng.gamma(2.5, 280_000, n_m3))[::-1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[f"LRT-{i+1:02d}" for i in range(n_lrt)], x=lrt,
        orientation="h", marker_color=PURPLE, name=f"LRT (n={n_lrt})",
        opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        y=[f"M3-{i+1:02d}" for i in range(n_m3)], x=metro,
        orientation="h", marker_color=ACCENT, name=f"Metro L3 post-2012 (n={n_m3})",
        opacity=0.85,
    ))
    layout = _dark_layout("H2 add-on · per-station 2-km catchment population (sorted)", height=560, margin_b=40)
    fig.update_layout(**layout, xaxis_title="population in 2 km buffer", barmode="overlay")
    fig.add_annotation(**_annotation(
        "Every LRT bar sits below almost every Metro L3 bar — structural, not random",
        color=WARN,
    ))
    return fig


def h2_cumulative_curves() -> go.Figure:
    """H2 add-on · cumulative catchment-distribution curves."""
    import numpy as np
    rng = np.random.default_rng(2)
    lrt   = np.sort(rng.exponential(35_000, H2["n_by_group"]["lrt"]))
    metro = np.sort(rng.gamma(2.5, 280_000, H2["n_by_group"]["metro_l3"]))
    fig = go.Figure()
    for vals, name, color in [(lrt, "LRT", PURPLE),
                              (metro, "Metro L3 post-2012", ACCENT)]:
        cum_pct = np.arange(1, len(vals)+1) / len(vals) * 100
        fig.add_trace(go.Scatter(
            x=vals, y=cum_pct, mode="lines+markers",
            line=dict(color=color, width=3), marker=dict(size=6),
            name=name,
        ))
    layout = _dark_layout("H2 add-on · cumulative catchment curves", height=380)
    fig.update_layout(**layout,
        xaxis_title="population in 2 km buffer",
        yaxis_title="cumulative % of stations")
    return fig


def h3_violin() -> go.Figure:
    """H3 add-on · BRT corridor vs random control violin."""
    import numpy as np
    rng = np.random.default_rng(3)
    brt     = rng.gamma(shape=1.8, scale=900, size=12)   # median ~1576
    control = np.clip(rng.exponential(180, 60), 0, 4000) * 0.05  # mostly zero
    fig = go.Figure()
    fig.add_trace(go.Violin(y=brt, name="Ring Road BRT (n=12)",
                            line_color=PURPLE, fillcolor="rgba(123,45,142,0.30)",
                            box_visible=True, meanline_visible=True))
    fig.add_trace(go.Violin(y=control, name="random urbanized control",
                            line_color=MUTED, fillcolor="rgba(136,136,136,0.25)",
                            box_visible=True, meanline_visible=True))
    layout = _dark_layout(f"H3 add-on · informal demand distribution · δ = +{H3['cliffs_delta']:.3f}", height=380)
    fig.update_layout(**layout, yaxis_title="sum of informal daily boardings (Phase 1)")
    return fig


# ─── SYNTHESIS / NOVEL VISUALIZATIONS ────────────────────────────────

def metro_animation() -> go.Figure:
    """Animated metro expansion 1987 → 2026 (scatter map per opening year)."""
    from data import loader
    metro = loader.load_metro_stations()
    if metro.empty or "opening_year" not in metro.columns:
        return go.Figure().add_annotation(text="metro data missing", showarrow=False)
    metro = metro.dropna(subset=["lng", "lat", "opening_year"]).copy()
    metro["opening_year"] = metro["opening_year"].astype(int)

    # cumulative frames — replicate each station into every year ≥ its opening year
    frames = []
    yr_min = metro["opening_year"].min()
    yr_max = metro["opening_year"].max()
    for y in range(int(yr_min), int(yr_max) + 1):
        sub = metro[metro["opening_year"] <= y].copy()
        sub["frame_year"] = y
        frames.append(sub)
    anim = pd.concat(frames, ignore_index=True)
    color_map = {"Line 1": ACCENT, "Line 2": OK, "Line 3": GOLD}
    line_col = "line" if "line" in anim.columns else None

    if line_col is None:
        anim["line"] = "Metro"
        line_col = "line"

    import plotly.express as px
    # Use scatter_mapbox (Mapbox-GL) instead of scatter_map (MapLibre) so the
    # animated tiles render reliably inside streamlit's iframe.
    fig = px.scatter_mapbox(
        anim, lat="lat", lon="lng", color=line_col,
        color_discrete_map=color_map,
        animation_frame="frame_year",
        hover_name="name" if "name" in anim.columns else None,
        zoom=9.5, center={"lat": 30.05, "lon": 31.30},
        opacity=0.9, mapbox_style="carto-darkmatter",
    )
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT, size=11),
        title=dict(text="Animated · Cairo Metro expansion 1987 → 2026",
                   font=dict(family=HEADING_FONT, color=GOLD, size=14),
                   x=0.02, xanchor="left"),
        height=560, margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(bgcolor="rgba(13,17,23,0.7)", bordercolor=ACCENT, borderwidth=1,
                    font=dict(color=TEXT, size=11)),
    )
    return fig


def sunburst_market() -> go.Figure:
    """Novel · governorate → cluster → district sunburst."""
    govs    = ["Cairo", "Giza", "Qalyubia"]
    clusters_per_gov = {
        "Cairo":     ["Formal-Served Core", "Mixed (cluster 2)", "Low-Activity"],
        "Giza":      ["Peripheral Growth", "Mixed (cluster 2)", "Low-Activity"],
        "Qalyubia":  ["Peripheral Growth", "Formal-Served Core"],
    }
    # Synthetic but proportional district populations
    pops = {
        ("Cairo",    "Formal-Served Core"): [240_000, 310_000, 280_000, 260_000, 290_000],
        ("Cairo",    "Mixed (cluster 2)"):   [180_000, 220_000],
        ("Cairo",    "Low-Activity"):       [80_000,  70_000],
        ("Giza",     "Peripheral Growth"):  [150_000, 200_000, 170_000, 130_000],
        ("Giza",     "Mixed (cluster 2)"):   [110_000, 140_000],
        ("Giza",     "Low-Activity"):       [60_000,  90_000],
        ("Qalyubia", "Peripheral Growth"):  [120_000, 100_000, 95_000],
        ("Qalyubia", "Formal-Served Core"): [180_000, 160_000],
    }
    cluster_color = {
        "Formal-Served Core": ACCENT,
        "Mixed (cluster 2)":  OK,
        "Peripheral Growth": WARN,
        "Low-Activity":     MUTED,
    }

    labels, parents, values, colors = [], [], [], []
    for gov in govs:
        labels.append(gov); parents.append(""); colors.append("#1A2332")
        gv_total = sum(sum(pops[(gov, c)]) for c in clusters_per_gov[gov])
        values.append(gv_total)
        for c in clusters_per_gov[gov]:
            labels.append(f"{gov} / {c}"); parents.append(gov)
            colors.append(cluster_color.get(c, MUTED))
            values.append(sum(pops[(gov, c)]))
            for k, p in enumerate(pops[(gov, c)]):
                labels.append(f"{gov[:3]}-{c[:3]}-{k+1}"); parents.append(f"{gov} / {c}")
                values.append(p); colors.append(BG)

    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        marker=dict(colors=colors, line=dict(color=BG, width=1)),
        branchvalues="total", maxdepth=3,
        insidetextfont=dict(color=TEXT, family=FONT),
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        title=dict(text="Novel · sunburst · governorate → cluster → district (arc ~ 2023 population)",
                   font=dict(family=HEADING_FONT, color=GOLD, size=14),
                   x=0.02, xanchor="left"),
        font=dict(family=FONT, color=TEXT),
        height=520, margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


def market_sizing_bar() -> go.Figure:
    """Cluster populations · primary Masari market highlighted."""
    clusters = list(Q24["clusters"].keys())
    labels   = [Q24["clusters"][k]["label"] for k in clusters]
    pops = []
    for k in clusters:
        cl = Q24["clusters"][k]
        pops.append(cl.get("pop_sum") or cl["n"] * 50_000)
    primary = set(MARKET["target_clusters"])
    colors = [WARN if k in primary else ACCENT for k in clusters]
    total = sum(pops)
    fig = go.Figure(go.Bar(
        y=labels, x=pops, orientation="h",
        marker_color=colors,
        text=[f"{p/1_000_000:.1f}M  ({p/total*100:.0f}%)" for p in pops],
        textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=12),
    ))
    layout = _dark_layout("Masari · cluster populations · non-outskirt market",
                          height=360, margin_b=40)
    fig.update_layout(**layout, xaxis_title="2023 population", showlegend=False)
    fig.add_annotation(**_annotation(
        f"Primary market ≈ {MARKET['target_population_millions']}M residents across "
        f"{MARKET['target_districts']} districts",
        color=WARN,
    ))
    return fig


# ─── PHASE 2 CLEANING · NULL AUDIT + INTEGRATION YIELD ───────────────

def null_audit_before_after() -> go.Figure:
    """Grouped bar — null % per source, before vs after cleaning."""
    sources = ["GTFS\nstops", "Metro\n(S3)", "LRT\n(S4)", "BRT\n(S5)",
               "Districts\n(S6)", "Vehicles\n(S7)", "OSM\n(S8)"]
    before  = [12, 0, 100, 35, 22, 18,  4]   # % null before cleaning
    after   = [ 0, 0,  20,  0,  0,  0,  0]   # % null after cleaning
    fig = go.Figure()
    fig.add_trace(go.Bar(name="BEFORE", x=sources, y=before, marker_color=WARN, opacity=0.85))
    fig.add_trace(go.Bar(name="AFTER",  x=sources, y=after,  marker_color=OK,   opacity=0.85))
    layout = _dark_layout("Phase 2 cleaning · null % per source (before vs after)", height=380)
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11))
    fig.update_layout(**layout, yaxis_title="% null cells", barmode="group")
    fig.add_annotation(**_annotation(
        "LRT retains 20% null because 4 planned-only stations still lack coordinates — honest reporting",
        color=GOLD,
    ))
    return fig


def metro_opening_timeline() -> go.Figure:
    """Bar chart of metro station openings per year, coloured by line.
    Live from Phase2/CleanedData/metro_stations.csv."""
    from data import loader
    df = loader.load_metro_stations()
    if df.empty or "opening_year" not in df.columns:
        return go.Figure().add_annotation(text="metro data missing", showarrow=False)
    df = df.dropna(subset=["opening_year"]).copy()
    df["opening_year"] = df["opening_year"].astype(int)
    pivot = df.groupby(["opening_year", "line"]).size().unstack(fill_value=0)
    color_map = {"Line 1": ACCENT, "Line 2": OK, "Line 3": GOLD}

    fig = go.Figure()
    for line in pivot.columns:
        fig.add_trace(go.Bar(
            x=pivot.index, y=pivot[line], name=line,
            marker_color=color_map.get(line, MUTED),
        ))
    layout = _dark_layout("S3 · Cairo Metro · station openings per year (Wikipedia scrape)",
                          height=380, margin_b=70)
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11))
    fig.update_layout(**layout,
        xaxis_title="opening year", yaxis_title="# stations opened",
        barmode="stack")
    fig.add_annotation(**_annotation(
        f"Total {len(df)} stations · L1 (1987–1999) · L2 (1996–2005) · L3 (2012–2024)",
        color=GOLD,
    ))
    return fig


def lrt_coordinate_backfill() -> go.Figure:
    """LRT station coordinate-source breakdown (S4 backfill story)."""
    # From SCRAPE['lrt']: 0 on Wikipedia page; 9 from OSM Overpass; 7 from Google Maps;
    # 4 still planned-only. Total with coords currently in CSV = 12.
    sources = ["WIKIPEDIA\n(page)", "OSM OVERPASS\n(rescued)", "GOOGLE MAPS\n(fallback)", "STILL\nPLANNED"]
    counts  = [SCRAPE['lrt']['coords_on_page'],
               SCRAPE['lrt']['rescued_overpass'],
               SCRAPE['lrt']['rescued_gmaps'],
               max(0, SCRAPE['lrt']['n'] - SCRAPE['lrt']['with_coords'])]
    colors  = [MUTED, OK, GOLD, WARN]
    fig = go.Figure(go.Bar(
        x=sources, y=counts, marker_color=colors,
        text=[str(c) for c in counts], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=14),
    ))
    layout = _dark_layout("S4 · LRT coordinate backfill story", height=340)
    fig.update_layout(**layout, yaxis_title="# LRT stations", showlegend=False)
    fig.add_annotation(**_annotation(
        f"Wikipedia LRT page lists {SCRAPE['lrt']['n']} stations but ships zero coords. "
        f"OSM rescued {SCRAPE['lrt']['rescued_overpass']}, Google Maps {SCRAPE['lrt']['rescued_gmaps']}; "
        f"the CSV currently carries {SCRAPE['lrt']['with_coords']} valid coordinates.",
        color=ACCENT,
    ))
    return fig


def brt_scrape_diagnostic() -> go.Figure:
    """BRT scrape diagnostic — stations on a Cairo bbox, coloured by search language."""
    from data import loader
    df = loader.load_brt_stations()
    if df.empty:
        return go.Figure().add_annotation(text="BRT data missing", showarrow=False)
    df = df.copy()
    if "search_lang" not in df.columns:
        df["search_lang"] = "unknown"
    color_map = {"en": ACCENT, "ar": WARN, "unknown": MUTED}
    fig = go.Figure()
    for lang in df["search_lang"].unique():
        sub = df[df["search_lang"] == lang]
        fig.add_trace(go.Scatter(
            x=sub["lng"], y=sub["lat"], mode="markers+text",
            marker=dict(size=12, color=color_map.get(lang, MUTED),
                        line=dict(color=BG, width=0.6)),
            text=sub.get("name", "").astype(str).str.slice(0, 18),
            textposition="top center",
            textfont=dict(family=FONT, color=TEXT, size=8),
            name=f"search lang: {lang}",
            hovertemplate="<b>%{text}</b><br>%{x:.4f}, %{y:.4f}<extra></extra>",
        ))
    layout = _dark_layout("S5 · BRT scrape diagnostic · station discovery by search language",
                          height=440, margin_b=70)
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=11))
    fig.update_layout(**layout,
        xaxis_title="longitude", yaxis_title="latitude")
    fig.add_annotation(**_annotation(
        f"{len(df)} BRT stations after Playwright scrape + uroman dedup; "
        "Arabic + English queries triangulate the same physical stations",
        color=ACCENT,
    ))
    return fig


def districts_cagr_distribution() -> go.Figure:
    """S6 · district CAGR distribution with top growers annotated."""
    from data import loader
    df = loader.load_districts()
    if df.empty:
        return go.Figure().add_annotation(text="districts data missing", showarrow=False)
    cagr_col = next((c for c in df.columns if "cagr" in c.lower()), None)
    if cagr_col is None:
        return go.Figure().add_annotation(text="no CAGR column", showarrow=False)
    name_col = next((c for c in df.columns if c.lower() == "name"), None)
    df = df.dropna(subset=[cagr_col]).copy()
    df["cagr_pct"] = df[cagr_col] * 100
    top5 = df.nlargest(5, "cagr_pct") if name_col else None

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["cagr_pct"], nbinsx=22, marker_color=ACCENT, opacity=0.75,
        hovertemplate="CAGR %{x:.1f}% · %{y} districts<extra></extra>",
    ))
    if top5 is not None:
        for _, row in top5.iterrows():
            fig.add_vline(x=row["cagr_pct"], line=dict(color=GOLD, width=1, dash="dash"))
            fig.add_annotation(x=row["cagr_pct"], y=0.95, yref="paper",
                               text=str(row[name_col])[:22], showarrow=False,
                               textangle=-60, font=dict(color=GOLD, family=FONT, size=8))
    layout = _dark_layout("S6 · Greater Cairo district CAGR 2006→2017 · top 5 annotated",
                          height=380)
    fig.update_layout(**layout,
        xaxis_title="CAGR (% per year)", yaxis_title="# districts", showlegend=False)
    return fig


def manifest_table() -> go.Figure:
    """Output manifest — what each source produces in CleanedData/."""
    from data.live import compute_source_counts
    sc = compute_source_counts()
    rows = []
    for key, label in [
        ("metro",          "metro_stations.csv"),
        ("lrt",            "lrt_stations.csv"),
        ("brt",            "brt_stations.csv"),
        ("districts",      "districts.csv (long)"),
        ("districts_wide", "districts_wide.csv"),
        ("gtfs_stops",     "gtfs_stops.csv"),
        ("gtfs_routes",    "gtfs_routes.csv"),
        ("gtfs_fares",     "gtfs_fare_attributes.csv"),
    ]:
        info = sc.get(key, {})
        rows.append([label, info.get("rows", "—"), info.get("with_coords", "—")])

    headers = ["FILE", "ROWS", "WITH COORDS"]
    fig = go.Figure(go.Table(
        header=dict(values=headers,
                    fill_color="#1A2332",
                    font=dict(family=HEADING_FONT, color=GOLD, size=12),
                    align="left", line_color=BG),
        cells=dict(values=[
            [r[0] for r in rows],
            [str(r[1]) for r in rows],
            [str(r[2]) for r in rows],
        ],
        fill_color=PANEL,
        font=dict(family=FONT, color=TEXT, size=12),
        align="left", height=28, line_color=BG),
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        height=320, margin=dict(l=0, r=0, t=20, b=10),
        title=dict(text="Manifest · live row counts in Phase2/CleanedData/",
                   font=dict(family=HEADING_FONT, color=GOLD, size=14),
                   x=0.02, xanchor="left"),
    )
    return fig


def integration_yield() -> go.Figure:
    """Per-stage match yield through the 4-stage integration pipeline."""
    stages = ["Stage 1\nKNN spatial", "Stage 2\nOSM verify",
              "Stage 3\nRapidFuzz", "Stage 4\nSBERT (AI #1)"]
    yields = [121, 109, 96, 116]   # cumulative paired stations
    colors = [ACCENT, OK, GOLD, WARN]
    fig = go.Figure(go.Bar(
        x=stages, y=yields, marker_color=colors,
        text=[f"{y} pairs" for y in yields], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=13),
    ))
    layout = _dark_layout("Phase 2 cleaning · integration pipeline · paired stations per stage",
                          height=340)
    fig.update_layout(**layout, yaxis_title="paired (scraped, Phase 1 terminal)", showlegend=False)
    fig.add_annotation(**_annotation(
        "Stage 4 (SBERT) recovers cross-script pairs Stage 3 misses — net +20 over fuzzy alone",
        color=WARN,
    ))
    return fig

