"""Frosted glassmorphism card wrappers — notebook signature aesthetic."""
from __future__ import annotations

from contextlib import contextmanager

import streamlit as st


@contextmanager
def frosted_card():
    """Context manager that wraps its contents in a frosted-glass card.

    Uses a sentinel + `:has()` CSS trick so the card styling applies to a
    real Streamlit container (which is the only way to contain Streamlit
    widgets in a custom visual wrapper).
    """
    container = st.container()
    with container:
        # Sentinel — CSS targets any stVerticalBlock that contains this
        st.markdown(
            '<div class="cairo-card-sentinel"></div>'
            '<div class="bl" style="position:absolute;left:0;bottom:0;width:32px;height:32px;'
            'border-bottom:2px solid #2A9D8F;border-left:2px solid #2A9D8F;border-radius:0 0 0 14px;opacity:0.7;pointer-events:none"></div>'
            '<div class="br" style="position:absolute;right:0;bottom:0;width:32px;height:32px;'
            'border-bottom:2px solid #58A6FF;border-right:2px solid #58A6FF;border-radius:0 0 14px 0;opacity:0.7;pointer-events:none"></div>',
            unsafe_allow_html=True,
        )
        yield container


def render_card_html(inner_html: str):
    """Render a static frosted card (no Streamlit widgets inside)."""
    html = (
        '<div class="cairo-card">'
        '<div class="bl"></div><div class="br"></div>'
        f'{inner_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_hr():
    st.markdown('<hr class="cairo-hr" />', unsafe_allow_html=True)


def render_h2(text: str):
    st.markdown(f'<div class="cairo-h2">{text}</div>', unsafe_allow_html=True)


def render_kicker(text: str):
    st.markdown(f'<div class="cairo-panel-kicker">{text}</div>', unsafe_allow_html=True)


def render_shimmer_headline(text: str):
    st.markdown(f'<h1 class="cairo-title-shimmer">{text}</h1>', unsafe_allow_html=True)


def render_arabic(text: str):
    st.markdown(f'<div class="cairo-panel-arabic">{text}</div>', unsafe_allow_html=True)


def render_body(text: str):
    st.markdown(f'<div class="cairo-panel-body">{text}</div>', unsafe_allow_html=True)


def render_metric(label: str, value: str, unit: str):
    html = (
        '<div class="cairo-metric">'
        f'<div class="cairo-metric-label">{label}</div>'
        f'<div class="cairo-metric-value">{value}</div>'
        f'<div class="cairo-metric-unit">{unit}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_row(kpis):
    """kpis: list of (label, value, unit) tuples."""
    palette = ["#58A6FF", "#2A9D8F", "#E9C46A", "#E86F51", "#7B2D8E", "#4ECDC4"]
    cells = []
    for i, item in enumerate(kpis):
        label, value, unit = item if len(item) == 3 else (item[0], item[1], "")
        color = palette[i % len(palette)]
        cells.append(
            '<div class="cairo-kpi">'
            f'<div class="cairo-kpi-val" style="color:{color};'
            f'text-shadow:0 0 18px {color}66;">{value}</div>'
            f'<div class="cairo-kpi-lbl">{label}</div>'
            f'<div class="cairo-kpi-unit">{unit}</div>'
            '</div>'
        )
    st.markdown(f'<div class="cairo-kpi-row">{"".join(cells)}</div>', unsafe_allow_html=True)
