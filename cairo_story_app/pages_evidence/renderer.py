"""Unified per-question page renderer (Evidence mode)."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from components.frosted_card import (
    frosted_card,
    render_arabic,
    render_body,
    render_h2,
    render_hr,
    render_kicker,
    render_kpi_row,
    render_shimmer_headline,
)
from data.paths import DATA_ROOT
from pages_evidence.question_config import Question


def _viz_height(path: str) -> int:
    if "notebook_visuals/" in path:
        return 760 if "_map" in path else 680
    if "notebook_sections/" in path or "phase2_analysis_all_visualizations" in path:
        return 920
    return 560


def _viz_scroll(path: str) -> bool:
    return not ("notebook_visuals/" in path)


def _resolve_viz(path: str):
    """Join a viz path against DATA_ROOT if not absolute."""
    from pathlib import Path
    p = Path(path)
    if p.is_absolute():
        return p
    return DATA_ROOT / path


def render_question_page(q: Question):
    # ── Header block
    render_kicker(q.kicker)
    if q.arabic:
        render_arabic(q.arabic)
    render_shimmer_headline(q.headline)

    # ── Question + why + method (frosted card)
    with frosted_card():
        if q.question_text:
            st.markdown(f"**Question.** {q.question_text}")
        if q.why_it_matters:
            st.markdown(f"**Why it matters.** {q.why_it_matters}")
        if q.method:
            st.markdown(f"**Method.** `{q.method}`")

    # ── KPI strip
    if q.kpis:
        render_kpi_row(q.kpis)

    # ── Visualizations
    if q.viz_html_paths or q.viz_builders:
        render_h2("VISUALIZATIONS")

    for path in q.viz_html_paths:
        full = _resolve_viz(path)
        if full.exists():
            with frosted_card():
                try:
                    html = full.read_text(encoding="utf-8")
                    components.html(html, height=_viz_height(path), scrolling=_viz_scroll(path))
                except Exception as exc:
                    st.warning(f"Failed to render {path}: {exc}")
        else:
            with frosted_card():
                st.warning(
                    f"Missing export: `{path}`. "
                    "Re-run the Phase 1 notebook or disable this viz."
                )

    for builder in q.viz_builders:
        with frosted_card():
            try:
                fig = builder()
                st.plotly_chart(fig, width="stretch", theme=None)
            except Exception as exc:
                st.warning(f"Builder failed: {exc}")

    # ── Insight
    if q.insight:
        render_h2("INSIGHT")
        with frosted_card():
            st.markdown(q.insight)

    # ── Methodology expander
    if q.methodology:
        with st.expander("▸ HOW WE BUILT THIS"):
            st.markdown(q.methodology)

    render_hr()
