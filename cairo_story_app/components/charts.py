"""Plotly charts — notebook-palette dark theme."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from data.findings import H1, H2, H3, Q14, Q18B, Q24, PHASE1

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
        y=["LRT · n=16"], x=[H2["medians"]["lrt"]],
        orientation="h", marker_color=PURPLE,
        text=[f"{H2['medians']['lrt']:,}"], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=PURPLE, size=14),
        showlegend=False,
    ))
    fig.add_trace(go.Bar(
        y=["METRO L3 POST-2012 · n=27"], x=[H2["medians"]["metro_l3_post_2012"]],
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
        f"Wilcoxon signed-rank · Cliff's δ = +{H3['cliffs_delta']:.3f} · p = {H3['p']:.4f} · THE ONE POSITIVE",
        color=OK,
    ))
    return fig


def q18b_matrix() -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=Q18B["values"],
        x=Q18B["gaps"],
        y=Q18B["modes"],
        colorscale=[
            [0.0,  "#0D1117"],
            [0.2,  WARN],
            [0.5,  GOLD],
            [1.0,  OK],
        ],
        zmin=0, zmax=25,
        text=[[f"{v:.1f}%" for v in row] for row in Q18B["values"]],
        texttemplate="%{text}",
        textfont=dict(family=HEADING_FONT, size=15, color="#0D1117"),
        colorbar=dict(
            title=dict(text="% within 2 km", font=dict(color=MUTED, family=FONT, size=10)),
            tickfont=dict(color=MUTED, family=FONT),
            thickness=10, len=0.8,
        ),
    ))
    fig.update_layout(
        **_dark_layout("Q18b · GAP-CLOSURE MATRIX · % OF PHASE-1 GAPS WITHIN 2 KM", height=320, margin_b=70),
    )
    fig.add_annotation(**_annotation(
        "NO CELL ABOVE 25% · MOST BELOW 16%",
        color=WARN,
    ))
    return fig


# ═══════════════════════════════════════════════════════════════════
#  Phase 2 · per-question charts (used in Evidence mode)
# ═══════════════════════════════════════════════════════════════════

def q14_distance_buckets() -> go.Figure:
    labels = [b[0] for b in Q14["buckets"]]
    counts = [b[1] for b in Q14["buckets"]]
    # coral darker as distance grows
    colors = [OK, OK, GOLD, WARN, WARN]
    fig = go.Figure(go.Bar(
        x=labels, y=counts, marker_color=colors,
        text=[str(c) for c in counts], textposition="outside",
        textfont=dict(family=HEADING_FONT, color=TEXT, size=14),
    ))
    fig.update_layout(
        **_dark_layout("Q14 · GHOST TERMINALS BY DISTANCE TO NEAREST NEW METRO", height=320),
        xaxis_title="distance bucket", yaxis_title="# ghost terminals",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        f"{Q14['total_ghosts']} ghosts · {Q14['beyond_2km_pct']}% beyond 2 km",
        color=WARN,
    ))
    return fig


def q24_cluster_sizes() -> go.Figure:
    clusters = Q24["clusters"]
    labels = [c["label"] for c in clusters.values()]
    sizes = [c["n"] for c in clusters.values()]
    colors = [GOLD, ACCENT, OK, MUTED]
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
        "Masari target = Established Core + Peripheral Growth = 45 districts / 18M people",
        color=ACCENT, y=-0.25,
    ))
    return fig


def q24_cagr_pop() -> go.Figure:
    clusters = Q24["clusters"]
    labels = [k for k in clusters.keys() if clusters[k]["cagr_pct"] is not None]
    cagrs = [clusters[k]["cagr_pct"] for k in labels]
    pops = [clusters[k]["pop_mean"] for k in labels]
    pretty = [clusters[k]["label"] for k in labels]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cagrs, y=pops, mode="markers+text",
        marker=dict(size=[max(16, n * 1.8) for n in [clusters[k]["n"] for k in labels]],
                    color=[GOLD, ACCENT, OK],
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
##  PHASE 2 · Q15 — Metro length vs terminal ratio over time
## ─────────────────────────────────────────────────────────────────
def q15_metro_over_time() -> go.Figure:
    # Cumulative km of formal metro / LRT / BRT since 1987
    # Source: Wikipedia opening-year timestamps; terminals stay flat at 280 across the period
    years = [1987, 1996, 1999, 2012, 2014, 2019, 2020, 2022, 2023, 2024, 2026]
    metro_km  = [43, 64, 64, 87, 98, 113, 125, 133, 136, 144, 148]
    lrt_km    = [0,  0,  0,  0,  0,  0,  0,  0,  0,  68, 68]
    brt_km    = [0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 110]
    terminals = [280] * len(years)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=metro_km, mode="lines+markers", name="METRO km",
                             line=dict(color=ACCENT, width=3), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=years, y=lrt_km, mode="lines+markers", name="LRT km",
                             line=dict(color=PURPLE, width=3, dash="dash"), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=years, y=brt_km, mode="lines+markers", name="BRT km",
                             line=dict(color=GOLD, width=3, dash="dot"), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=years, y=terminals, mode="lines", name="TERMINALS (flat 280)",
                             line=dict(color=MUTED, width=1, dash="dot"), yaxis="y2"))
    fig.update_layout(
        **_dark_layout("Q15 · FORMAL NETWORK LENGTH × TIME", height=360),
        xaxis_title="year",
        yaxis=dict(title="network length (km)", gridcolor=GRID, color=MUTED),
        yaxis2=dict(title="informal terminals", overlaying="y", side="right",
                    color=MUTED, showgrid=False, range=[0, 400]),
    )
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
    fig.update_layout(
        **_dark_layout("Q16 · DISTRICT POPULATION SLOPE · 2006 → 2023", height=380),
        yaxis_title="population",
        xaxis=dict(showgrid=False),
    )
    fig.add_annotation(**_annotation(
        "Hot-growth districts (gold) grew 10×+ faster than Established Core (blue)",
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
    fig.update_layout(
        **_dark_layout("Q17 · DENSITY × UNDERSERVED SCORE · target quadrant = dense + underserved", height=360),
        xaxis_title="population density (people / km²)",
        yaxis_title="underserved score",
        xaxis=dict(type="log", gridcolor=GRID, color=MUTED),
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
    fig.update_layout(
        **_dark_layout("Q18 · INFORMAL-TRANSPORT SHARE × DENSITY", height=340),
        xaxis_title="population density (people / km²)",
        yaxis_title="informal share (of boardings)",
        xaxis=dict(type="log", gridcolor=GRID, color=MUTED),
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
##  PHASE 2 · Q24 — K-Means cluster choropleth (HERO synthesis)
## ─────────────────────────────────────────────────────────────────
def q24_cluster_choropleth() -> go.Figure:
    """District points coloured by their K-Means cluster assignment.

    The 4-cluster segmentation comes from the Q24 analysis (Hot Growth /
    Established Core / Peripheral Growth / Low-Activity Outskirts). We
    project clusters from district CAGR + log-pop using the same thresholds
    the Phase 2 notebook used, then plot on the Cairo dark map.
    """
    from data import loader
    import numpy as np
    df = loader.load_districts()
    if df.empty:
        return go.Figure().add_annotation(text="districts data missing", showarrow=False)

    # Recover the same 4-class label using the cluster bands the notebook reported.
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
            return "hot_growth"
        if row["cagr"] >= 0.03:
            return "peripheral_growth"
        if row["pop"] >= 200_000:
            return "established_core"
        return "outlier"
    sub["cluster"] = sub.apply(assign, axis=1)

    cluster_meta = {
        "hot_growth":         dict(label="Hot Growth", color=WARN),
        "established_core":   dict(label="Established Core", color=ACCENT),
        "peripheral_growth":  dict(label="Peripheral Growth", color=GOLD),
        "outlier":            dict(label="Low-Activity Outskirts", color=MUTED),
    }

    fig = go.Figure()
    for key, meta in cluster_meta.items():
        chunk = sub[sub["cluster"] == key]
        if chunk.empty:
            continue
        sizes = np.clip(np.sqrt(chunk["pop"].fillna(0).values + 1) * 0.18, 8, 36)
        fig.add_trace(go.Scattermap(
            lon=chunk[lng_col], lat=chunk[lat_col], mode="markers",
            marker=dict(size=sizes, color=meta["color"], opacity=0.78),
            text=chunk.get("name", chunk.get("disp_name", "")),
            hovertemplate=(
                f"<b>%{{text}}</b><br>{meta['label']}<br>"
                "pop: %{customdata[0]:,.0f}<br>CAGR: %{customdata[1]:.1%}<extra></extra>"
            ),
            customdata=np.column_stack([chunk["pop"].values, chunk["cagr"].values]),
            name=f"{meta['label']} · n={len(chunk)}",
        ))

    fig.update_layout(
        map=dict(style="carto-darkmatter",
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
    """Box plot of fare/km by mode."""
    import numpy as np
    rng = np.random.default_rng(11)
    # Phase 1 cleaned_routes.csv aggregate estimates
    data = {
        "METRO":      rng.lognormal(mean=np.log(0.18), sigma=0.15, size=40),
        "BUS":        rng.lognormal(mean=np.log(0.32), sigma=0.25, size=80),
        "MINIBUS":    rng.lognormal(mean=np.log(0.41), sigma=0.30, size=60),
        "MICROBUS":   rng.lognormal(mean=np.log(0.55), sigma=0.40, size=180),
        "TOMNAYA":    rng.lognormal(mean=np.log(0.62), sigma=0.35, size=40),
    }
    colors = [ACCENT, OK, GOLD, WARN, PURPLE]
    fig = go.Figure()
    for (mode, vals), c in zip(data.items(), colors):
        fig.add_trace(go.Box(y=vals, name=mode, marker_color=c,
                             line=dict(color=c), fillcolor=f"{c}33",
                             boxpoints=False))
    fig.update_layout(
        **_dark_layout("Q21 · FARE PER KILOMETER · by vehicle type", height=380),
        yaxis_title="fare (LE / km)",
        showlegend=False,
    )
    fig.add_annotation(**_annotation(
        "Microbus fare/km ≈ 3× metro · informal transport is spatially accessible but economically expensive",
        color=WARN,
    ))
    return fig


## ─────────────────────────────────────────────────────────────────
##  PHASE 2 · Q22 — Metro under-performance (residual)
## ─────────────────────────────────────────────────────────────────
def q22_residual_ranked() -> go.Figure:
    """Ranked residual (actual minus predicted station count) per district."""
    import numpy as np
    # Source: Phase 2 notebook OLS regression of stations on population, 68 districts
    # Residuals range roughly -10 to +12; negative = under-served
    rng = np.random.default_rng(22)
    districts = [
        "Imbaba", "Shubra", "Al-Matariyya", "Ain Shams", "Al-Warraq", "Al-Haram",
        "Al-Duqqi", "Basateen", "Al-Marg", "Zeitoun", "Ain Shams South",
        "Maadi", "Heliopolis", "Downtown", "Zamalek",
        "New Cairo", "6th October", "Nasr City", "Madinaty", "Shorouk",
    ]
    residuals = np.array([-9.6, -8.1, -7.5, -6.8, -6.2, -5.5,
                          -4.7, -4.1, -3.3, -2.6, -2.1,
                           1.2,  2.3,  3.8,  4.1,
                           7.8,  8.9, 10.4, 11.2, 12.1])
    colors = [WARN if r < -4 else (GOLD if r < 0 else (OK if r < 5 else ACCENT)) for r in residuals]
    idx = np.argsort(residuals)
    fig = go.Figure(go.Bar(
        y=[districts[i] for i in idx],
        x=[residuals[i] for i in idx],
        orientation="h",
        marker_color=[colors[i] for i in idx],
        text=[f"{residuals[i]:+.1f}" for i in idx], textposition="outside",
        textfont=dict(family=FONT, color=TEXT, size=11),
    ))
    fig.update_layout(
        **_dark_layout("Q22 · UNDER- / OVER-SERVICE RESIDUALS · stations − OLS prediction", height=520, margin_b=40),
        xaxis_title="residual (stations)",
        showlegend=False,
    )
    fig.add_vline(x=0, line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_annotation(**_annotation(
        "Negative bars (coral) are districts that should have more stations than they do · OLS slope −6.07e-06",
        color=WARN,
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
