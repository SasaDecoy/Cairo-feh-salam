"""
Re-render every Phase 2 chart and save as standalone HTML in Phase2/Exports/.

The streamlit app embeds these HTMLs verbatim, so what users see IS what the
notebook would produce on a fresh run. Re-run this script after re-running
the notebook (or after the cleaned CSVs change) to refresh the exports.

Usage:
    python3 scripts/build_phase2_exports.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

# Add the streamlit app directory so `from components import charts` works
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cairo_story_app"))

warnings.filterwarnings("ignore")

from components import charts  # noqa: E402

EXPORTS = ROOT / "Phase2" / "Exports"
EXPORTS.mkdir(exist_ok=True, parents=True)


# ─── Question → builder mapping ─────────────────────────────────────
# Each entry is (output filename, builder callable, optional title override).
# The streamlit app's question_config.py points to these filenames.

EXPORT_MAP: dict[str, callable] = {
    # ── Phase 2 cleaning · per-source diagnostics ──
    "manifest_table.html":              charts.manifest_table,
    "metro_opening_timeline.html":      charts.metro_opening_timeline,
    "lrt_coordinate_backfill.html":     charts.lrt_coordinate_backfill,
    "brt_scrape_diagnostic.html":       charts.brt_scrape_diagnostic,
    "districts_cagr_distribution.html": charts.districts_cagr_distribution,

    # ── Phase 2 cleaning · integration + quality ──
    "integration_yield.html":           charts.integration_yield,
    "osm_cross_verification_map.html":  charts.osm_cross_verification_map,
    "null_audit_before_after.html":     charts.null_audit_before_after,

    # ── Phase 2 questions Q13 — Q25 ──
    "q13_coverage_vs_density.html":     charts.q13_coverage_vs_density,
    "q14_distance_buckets.html":        charts.q14_distance_buckets,
    "q14_spatial_diagnostic.html":      charts.q14_spatial_diagnostic,
    "q15_metro_terminal_integration.html": charts.q15_metro_over_time,
    "q16_cagr_slope.html":              charts.q16_cagr_slope,
    "q17_density_underserved.html":     charts.q17_density_underserved,
    "q17_target_tier_heatmap.html":     charts.q17_target_tier_heatmap,
    "q18_informal_share.html":          charts.q18_informal_share,
    "q18_per_tier_box.html":            charts.q18_per_tier_box,
    "q18b_matrix.html":                 charts.q18b_matrix,
    "q19_gtfs_coverage.html":           charts.q19_gtfs_coverage,
    "q19_agency_pie.html":              charts.q19_agency_pie,
    "q20_brt_corridor.html":            charts.q20_brt_corridor,
    "q21_fare_per_km.html":             charts.q21_fare_per_km,
    "q22_residual_ranked.html":         charts.q22_residual_ranked,
    "q22_governorate_box.html":         charts.q22_governorate_box,
    "q23_percentile_histogram.html":    charts.q23_percentile_histogram,
    "q23_modal_pie.html":               charts.q23_modal_pie,
    "q24_cluster_sizes.html":           charts.q24_cluster_sizes,
    "q24_cagr_pop.html":                charts.q24_cagr_pop,
    "q24_priority_bar.html":            charts.q24_priority_bar,
    "q24_parallel_coords.html":         charts.q24_parallel_coords,
    "q24_radar.html":                   charts.q24_radar,
    "q25_bridge_schematic.html":        charts.q25_bridge_schematic,

    # ── Phase 2 hypotheses ──
    "h1_box.html":                      charts.h1_box,
    "h1_continuous_scatter.html":       charts.h1_continuous_scatter,
    "h1_moran_bar.html":                charts.h1_moran_bar,
    "h2_bar.html":                      charts.h2_bar,
    "h2_ranked_bar.html":               charts.h2_ranked_bar,
    "h2_cumulative_curves.html":        charts.h2_cumulative_curves,
    "h3_bar.html":                      charts.h3_bar,
    "h3_violin.html":                   charts.h3_violin,

    # ── Synthesis (animation, sunburst, market sizing) ──
    "metro_animation.html":             charts.metro_animation,
    "sunburst_market.html":             charts.sunburst_market,
    "market_sizing_bar.html":           charts.market_sizing_bar,
    "q24_cluster_choropleth.html":      charts.q24_cluster_choropleth,
}


def main() -> int:
    print(f"Exporting {len(EXPORT_MAP)} Phase 2 charts → {EXPORTS}")
    print("=" * 70)

    succeeded, failed = [], []
    for fname, builder in EXPORT_MAP.items():
        try:
            fig = builder()
            out_path = EXPORTS / fname
            fig.write_html(
                str(out_path),
                include_plotlyjs="cdn",
                full_html=True,
                config={"displayModeBar": False, "responsive": True},
            )
            size_kb = out_path.stat().st_size // 1024
            print(f"  ✓ {fname:48s}  ({size_kb} KB)")
            succeeded.append(fname)
        except Exception as e:
            print(f"  ✗ {fname:48s}  → {type(e).__name__}: {e}")
            failed.append((fname, str(e)))

    print("=" * 70)
    print(f"  Exported {len(succeeded)} · failed {len(failed)}")
    if failed:
        print("\n  Failures:")
        for fname, err in failed:
            print(f"    - {fname}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
