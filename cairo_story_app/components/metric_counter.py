"""Small top-bar progress indicator."""
from __future__ import annotations

import streamlit as st


def render_progress_bar(current: int, total: int, kicker_text: str = ""):
    pct = 100 * (current + 1) / max(1, total)
    html = (
        '<div class="cairo-topnav" style="padding-top:4px;padding-bottom:4px;">'
        f'<div class="cairo-panel-kicker" style="margin:0">{kicker_text}</div>'
        '<div class="cairo-progress-wrap" style="margin-left:auto;">'
        f'<div class="cairo-progress-track"><div class="cairo-progress-fill" style="width:{pct}%"></div></div>'
        f'<div class="cairo-counter">{current + 1:02d} / {total:02d}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
