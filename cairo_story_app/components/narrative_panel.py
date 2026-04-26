"""Right-column story panel (Story mode)."""
from __future__ import annotations

import streamlit as st

from components.frosted_card import (
    render_arabic,
    render_body,
    render_kicker,
    render_metric,
    render_shimmer_headline,
)


def render_panel(chapter):
    render_kicker(chapter.kicker)
    if chapter.arabic:
        render_arabic(chapter.arabic)
    render_shimmer_headline(chapter.headline)
    render_body(chapter.body)

    if chapter.metric_value:
        render_metric(chapter.metric_label, chapter.metric_value, chapter.metric_unit)

    # Methodology expander
    if chapter.methodology:
        with st.expander("▸ HOW WE BUILT THIS"):
            st.markdown(chapter.methodology)
