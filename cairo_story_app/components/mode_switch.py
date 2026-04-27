"""Top-nav mode switch: STORY · PHASE 1 · PHASE 2."""
from __future__ import annotations

import streamlit as st


MODES = [
    ("story",      "STORY"),
    ("phase1",     "PHASE 1"),
    ("phase2",     "PHASE 2"),
]


def render_top_nav():
    """Render the brand + mode toggle + progress indicator."""
    current = st.session_state.get("mode", "story")

    # Top row: brand + progress + counter
    header_col, *btn_cols = st.columns([4, 1, 1, 1])
    with header_col:
        st.markdown(
            '<div class="cairo-brand">CAIRO · LAYLA · MASARI</div>',
            unsafe_allow_html=True,
        )

    for (mode_key, label), col in zip(MODES, btn_cols):
        with col:
            btn_type = "primary" if mode_key == current else "secondary"
            if st.button(label, key=f"mode_{mode_key}", type=btn_type, width="stretch"):
                if st.session_state.get("mode") != mode_key:
                    st.session_state.mode = mode_key
                    st.session_state.chapter = 0
                    st.session_state.question_idx = 0
                    st.rerun()
