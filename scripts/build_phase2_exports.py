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
NB_VISUALS = EXPORTS / "notebook_visuals"
NB_VISUALS.mkdir(exist_ok=True, parents=True)


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


# ─── notebook_visuals/ filename → builder ───────────────────────────
# These are the 48 granular per-cell exports the streamlit Q-pages
# reference (e.g. q18_01_q18_informal_transport_share_vs_hex_population_0_025
# .html). Each one is aliased to the closest builder in components/charts.py
# so a single script run regenerates the full set the streamlit app expects.

NOTEBOOK_VISUALS_MAP: dict[str, callable] = {
    # ── Q13 · metro coverage × density (3 views) ──
    "q13_01_q13_metro_opening_year_vs_district_population_at_the_closest.html": charts.q13_coverage_vs_density,
    "q13_02_q13_add_on_distribution_of_station_adjacent_district_populat.html": charts.q13_coverage_vs_density,
    "q13_03_q13_add_on_population_observation_year_used_for_each_line.html":    charts.q13_coverage_vs_density,

    # ── Q14 · ghost terminals × new metro (2 views) ──
    "q14_01_q14_ghost_terminals_by_distance_to_nearest_post_2014_metro_s.html": charts.q14_distance_buckets,
    "q14_02_q14_add_on_stranded_ghost_terminals_vs_post_2014_line_3_geog.html": charts.q14_spatial_diagnostic,

    # ── Q15 · metro–terminal integration (3 views) ──
    "q15_01_q15_did_new_metro_openings_land_near_the_existing_terminal_b.html": charts.q15_metro_over_time,
    "q15_02_q15_transfer_distance_distribution_by_metro_line.html":             charts.q15_metro_over_time,
    "q15_03_q15_add_on_where_metro_can_act_as_the_bridge_into_system_b.html":   charts.q15_metro_over_time,

    # ── Q16 · CAGR vs new-mode coverage (2 views) ──
    "q16_01_q16_top_15_fastest_growing_districts_cagr_vs_new_mode_covera.html": charts.q16_cagr_slope,
    "q16_02_q16_add_on_fast_growth_population_at_risk_when_coverage_is_z.html": charts.q16_cagr_slope,

    # ── Q17 · density × underserved (3 views) ──
    "q17_01_q17_population_density_underserved_score_spearman_0_548_p_1e.html": charts.q17_density_underserved,
    "q17_02_q17_add_on_dense_and_underserved_target_zone_by_decile.html":       charts.q17_target_tier_heatmap,
    "q17_03_q17_map.html":                                                       charts.q17_density_underserved,

    # ── Q18 · informal share + Q18b gap-closure matrix (4 views) ──
    "q18_01_q18_informal_transport_share_vs_hex_population_0_025.html":         charts.q18_informal_share,
    "q18_02_q18_add_on_informal_share_distribution_across_density_tiers.html":  charts.q18_per_tier_box,
    "q18_03_q18b_do_the_new_modes_close_phase_1_gaps.html":                     charts.q18b_matrix,
    "q18_04_q18b_add_on_percent_of_each_phase_1_gap_still_uncovered_by_e.html": charts.q18b_matrix,

    # ── Q19 · GTFS coverage (3 views) ──
    "q19_01_q19_published_gtfs_vs_phase_1_formal_informal_reality.html":        charts.q19_gtfs_coverage,
    "q19_02_q19_informal_heavy_stops_beyond_an_800m_gtfs_catchment.html":       charts.q19_gtfs_coverage,
    "q19_03_q19_add_on_published_gtfs_formal_routes_by_agency.html":            charts.q19_agency_pie,

    # ── Q20 · BRT corridor (2 views) ──
    "q20_01_q20_informal_phase_1_transit_demand_within_500_m_of_each_brt.html": charts.q20_brt_corridor,
    "q20_02_q20_add_on_pareto_curve_of_informal_demand_near_brt_stations.html": charts.q20_brt_corridor,

    # ── Q21 · fare per km (2 views) ──
    "q21_01_q21_fare_per_km_gtfs_derived_formal_blue_vs_phase_1_informal.html": charts.q21_fare_per_km,
    "q21_02_q21_add_on_median_fare_km_formal_vs_informal.html":                 charts.q21_fare_per_km,

    # ── Q22 · metro coverage residual (3 views) ──
    "q22_01_q22_metro_coverage_residual_by_district_negative_under_serve.html": charts.q22_residual_ranked,
    "q22_02_q22_top_15_under_served_districts_by_metro_coverage_residual.html": charts.q22_residual_ranked,
    "q22_03_q22_add_on_distribution_of_metro_coverage_residuals_by_gover.html": charts.q22_governorate_box,

    # ── Q23 · Adly Mansour (3 views) ──
    "q23_01_q23_map.html":                                                       charts.q23_modal_pie,
    "q23_02_q23_adly_mansour_rank_vs_random_cairo_2_5_km_clusters_p21.html":    charts.q23_percentile_histogram,
    "q23_03_q23_add_on_what_makes_adly_mansour_multimodal.html":                charts.q23_modal_pie,

    # ── Q24 · K-Means segmentation (5 views) ──
    "q24_01_k_means_model_selection_selected_k_4_policy_granularity.html":      charts.q24_cluster_sizes,
    "q24_02_q24_k_means_segmentation_k_4_mean_ari_1_00.html":                   charts.q24_cluster_choropleth,
    "q24_03_q24_add_on_cluster_opportunity_score_informal_stops_minus_fo.html": charts.q24_priority_bar,
    "q24_04_q24_parallel_coordinates_of_district_features_colored_by_k_m.html": charts.q24_parallel_coords,
    "q24_05_q24_radar_feature_z_score_signatures_per_cluster.html":             charts.q24_radar,

    # ── Q25 · Masari bridge (2 views) ──
    "q25_01_q25_masari_bridge_map_informal_demand_stops_connected_to_for.html": charts.q25_bridge_schematic,
    "q25_02_q25_how_much_informal_demand_is_already_bridgeable.html":           charts.q25_bridge_schematic,

    # ── H1 · coverage-need mismatch (2 views) ──
    "h1_01_h1_coverage_need_mismatch_global_moran_s_i_0_214_p_0_002.html":      charts.h1_moran_bar,
    "h1_02_h1_add_on_continuous_density_penalty_population_vs_stations_.html":  charts.h1_continuous_scatter,

    # ── H2 · LRT catchment deficit (3 views) ──
    "h2_01_h2_2_km_catchment_population_mann_whitney_p_0_000_cliff_0_99.html":  charts.h2_bar,
    "h2_02_h2_every_station_s_2_km_catchment_population_lrt_coral_vs_me.html":  charts.h2_ranked_bar,
    "h2_03_h2_add_on_cumulative_catchment_population_curves.html":              charts.h2_cumulative_curves,

    # ── H3 · BRT corridor match (6 views, includes synthesis tail) ──
    "h3_01_h3_pre_brt_informal_demand_in_500_m_buffers_p_0_000_cliff_0_.html":  charts.h3_bar,
    "h3_02_h3_add_on_individual_buffer_demand_brt_stations_vs_random_co.html":  charts.h3_violin,
    "h3_03_h3_map.html":                                                         charts.h3_bar,
    "h3_04_cairo_metro_expansion_1987_2026.html":                                charts.metro_animation,
    "h3_05_masari_cluster_populations_primary_market_formal_served_core.html":  charts.market_sizing_bar,
    "h3_06_sunburst_governorate_cluster_district_arc_2023_population.html":     charts.sunburst_market,
}


def _render_map(fmap: dict, out_dir: Path, label: str) -> tuple[list, list]:
    """Render every (filename, builder) pair into out_dir. Returns (ok, fail)."""
    print(f"\nExporting {len(fmap)} {label} → {out_dir}")
    print("=" * 70)
    out_dir.mkdir(exist_ok=True, parents=True)
    ok, fail = [], []
    for fname, builder in fmap.items():
        try:
            fig = builder()
            out_path = out_dir / fname
            fig.write_html(
                str(out_path),
                include_plotlyjs="cdn",
                full_html=True,
                config={"displayModeBar": False, "responsive": True},
            )
            size_kb = out_path.stat().st_size // 1024
            label_short = fname if len(fname) <= 64 else fname[:61] + "..."
            print(f"  ✓ {label_short:64s}  ({size_kb} KB)")
            ok.append(fname)
        except Exception as e:
            label_short = fname if len(fname) <= 64 else fname[:61] + "..."
            print(f"  ✗ {label_short:64s}  → {type(e).__name__}: {e}")
            fail.append((fname, str(e)))
    return ok, fail


def main() -> int:
    canon_ok, canon_fail = _render_map(
        EXPORT_MAP, EXPORTS, "canonical Phase 2 charts"
    )
    nb_ok, nb_fail = _render_map(
        NOTEBOOK_VISUALS_MAP, NB_VISUALS, "notebook_visuals/ aliases"
    )

    succeeded = canon_ok + nb_ok
    failed = canon_fail + nb_fail
    print("\n" + "=" * 70)
    print(f"  Total exported {len(succeeded)} · failed {len(failed)}")
    if failed:
        print("\n  Failures:")
        for fname, err in failed:
            print(f"    - {fname}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
