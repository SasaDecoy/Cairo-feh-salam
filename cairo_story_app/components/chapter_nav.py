"""Left-column chapter nav (Story mode)."""
from __future__ import annotations

import streamlit as st


def render_chapter_nav(chapters):
    current = st.session_state.get("chapter", 0)
    st.markdown('<div class="cairo-nav-list">', unsafe_allow_html=True)
    for idx, ch in enumerate(chapters):
        btn_type = "primary" if idx == current else "secondary"
        label = f"{idx + 1:02d}  {ch.title_short}"
        if st.button(label, key=f"nav_chapter_{idx}", type=btn_type, width="stretch"):
            if idx != current:
                st.session_state.chapter = idx
                import time
                st.session_state.chapter_entered_at = time.time()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_question_nav(questions, phase_key: str):
    """Left-column question nav (Evidence mode)."""
    current = st.session_state.get("question_idx", 0)
    st.markdown('<div class="cairo-nav-list">', unsafe_allow_html=True)
    for idx, q in enumerate(questions):
        btn_type = "primary" if idx == current else "secondary"
        if st.button(q.nav_label, key=f"nav_q_{phase_key}_{idx}", type=btn_type, width="stretch"):
            if idx != current:
                st.session_state.question_idx = idx
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
