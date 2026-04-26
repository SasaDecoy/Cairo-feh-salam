# ── Color palette ──
COLORS = ["#58A6FF","#2A9D8F","#E9C46A","#E86F51","#F4A261","#7B2D8E","#FF6B6B","#4ECDC4"]
BG = "#0D1117"
PANEL = "#161B22"
TXT = "#C9D1D9"
ACCENT = "#58A6FF"
WARN = "#E86F51"
OK = "#2A9D8F"

# ── CRS: all analysis in UTM 36N (meters); web maps only use WGS84 via to_map_crs() ──
CRS_METERS = "EPSG:32636"
CRS_MAP = "EPSG:4326"

def to_map_crs(gdf):
    """Project to WGS84 for Folium / web basemaps. Keep analysis in CRS_METERS everywhere else."""
    if gdf is None or not hasattr(gdf, "to_crs"):
        return gdf
    if gdf.crs is None:
        return gdf
    if str(gdf.crs) == CRS_MAP:
        return gdf
    return gdf.to_crs(CRS_MAP)

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = COLORS

import os, re
os.makedirs("Exports", exist_ok=True)

def style(fig, title, h=500):
    """Apply consistent dark styling to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#E6EDF3")),
        paper_bgcolor=BG, plot_bgcolor=PANEL,
        font=dict(family="Segoe UI, sans-serif", color=TXT, size=12),
        margin=dict(l=50, r=30, t=65, b=50),
        height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
    )
    fig.update_xaxes(gridcolor="#21262D", zerolinecolor="#30363D")
    fig.update_yaxes(gridcolor="#21262D", zerolinecolor="#30363D")
    
    # Auto-export the figure
    safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)
    safe_title = re.sub(r'_+', '_', safe_title).strip('_')
    try:
        fig.write_html(f"Exports/{safe_title}.html", include_plotlyjs="cdn")
    except Exception as e:
        print(f"Warning: Could not export {safe_title} -> {e}")
        
    return fig

def trend(fig, x, y, color=WARN, name="Trend"):
    """Add OLS trendline."""
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3: return fig
    a, b = np.polyfit(x[m], y[m], 1)
    xx = np.linspace(np.nanmin(x[m]), np.nanmax(x[m]), 100)
    fig.add_trace(go.Scatter(x=xx, y=a*xx+b, mode="lines",
        line=dict(color=color, width=2, dash="dot"), name=name, showlegend=True))
    return fig

def corr(df, x, y):
    d = df[[x,y]]
    return round(d[x].corr(d[y]), 3) if d[x].notna().sum() >= 3 else np.nan

def load_geo(path, crs=None):
    if crs is None:
        crs = CRS_METERS
    df = pd.read_csv(path)
    if "geometry" in df.columns:
        def _p(v):
            if pd.isna(v): return None
            t = str(v).strip()
            if not t or t.lower() in {"nan","none"}: return None
            try: return shapely_wkt.loads(t)
            except: return None
        return gpd.GeoDataFrame(df, geometry=df["geometry"].map(_p), crs=crs)
    return gpd.GeoDataFrame(df)

def quintile_labels(s, labels=None):
    """Bin a series into 5 groups."""
    if labels is None:
        labels = ["Very Low","Low","Medium","High","Very High"]
    return pd.qcut(s.rank(method="first"), 5, labels=labels)
