"""Cairo Transport · Layla · Masari — main Streamlit entry."""
from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from chapters.chapters_config import CHAPTERS
from components.chapter_nav import render_chapter_nav, render_question_nav
from components.map_component import build_deck, resolve_layla_position
from components.metric_counter import render_progress_bar
from components.mode_switch import render_top_nav
from components.narrative_panel import render_panel
from data.paths import APP_ROOT, STYLE_DIR
from pages_evidence.question_config import QUESTIONS_BY_PHASE
from pages_evidence.renderer import render_question_page


# ═══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG (must be first Streamlit call)
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cairo · Layla · Masari",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════════
#  CSS + FONTS (injected once)
# ═══════════════════════════════════════════════════════════════════════
def _inject_styles():
    fonts = (STYLE_DIR / "fonts.html").read_text()
    css = (STYLE_DIR / "dark_theme.css").read_text(encoding='utf-8')
    st.markdown(fonts, unsafe_allow_html=True)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_inject_styles()


# ═══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "mode": "story",                        # 'story' | 'phase1' | 'phase2' | 'hypothesis'
        "chapter": 0,
        "chapter_entered_at": time.time(),
        "last_chapter": -1,
        "question_idx": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ═══════════════════════════════════════════════════════════════════════
#  TOP NAV
# ═══════════════════════════════════════════════════════════════════════
render_top_nav()


# ═══════════════════════════════════════════════════════════════════════
#  STORY MODE · high-end cinematic React + MapLibre experience
# ═══════════════════════════════════════════════════════════════════════
STORY_HTML_PATH = APP_ROOT / "story" / "index.html"


def _load_story_html() -> str:
    """Read the standalone story HTML. Injects a small helper script at the end so
    CTA buttons inside the iframe can post back to Streamlit to switch mode.
    """
    html = STORY_HTML_PATH.read_text(encoding="utf-8")
    # inject postMessage → parent listener (parent is Streamlit's own frame)
    bridge = """
    <script>
      // If a CTA is clicked, bubble up via window.top
      window.addEventListener('message', (e) => {
        if (e.data && e.data.type === 'cairo-story-cta') {
          try { window.top.postMessage(e.data, '*'); } catch(_) {}
        }
      });
    </script>
    """
    return html.replace("</body>", bridge + "</body>")


def render_story_mode():
    """Story = full-bleed cinematic React+MapLibre experience inside an iframe.

    The story HTML owns its own navigation (keyboard + click + autoplay). The
    Streamlit layer provides only the container.
    """
    # Load fonts/chrome-kill CSS so the area around the iframe still matches
    html = _load_story_html()
    # Shrink the Streamlit padding around the iframe and give it the full viewport
    st.markdown(
        """
        <style>
          .main .block-container { padding: 0 !important; max-width: 100% !important; }
          iframe[title="streamlit_components.v1.html.html"] { border: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Render the full-bleed cinematic map.  `scrolling=False` keeps the iframe
    # fixed; the story app uses fixed positioning for all chrome so no scroll
    # is needed inside.  The parent page height is set by Streamlit's viewport.
    components.html(html, height=900, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════
#  EVIDENCE MODE (phase1 / phase2 / hypothesis)
# ═══════════════════════════════════════════════════════════════════════
def render_evidence_mode(phase_key: str):
    questions = QUESTIONS_BY_PHASE.get(phase_key, [])
    if not questions:
        st.warning(f"No questions configured for phase `{phase_key}`.")
        return

    # Clamp index
    idx = st.session_state.question_idx
    idx = max(0, min(idx, len(questions) - 1))
    st.session_state.question_idx = idx
    q = questions[idx]

    # Progress bar
    render_progress_bar(
        current=idx,
        total=len(questions),
        kicker_text=f"EVIDENCE · {phase_key.upper()} · {q.nav_label}",
    )

    # Two-column: nav | content
    col_nav, col_content = st.columns([2, 12])

    with col_nav:
        render_question_nav(questions, phase_key)

    with col_content:
        render_question_page(q)

        # Prev/next
        nav_l, nav_mid, nav_r = st.columns([1, 6, 1])
        with nav_l:
            if st.button("← PREV", key=f"ev_prev_{phase_key}", width="stretch"):
                if idx > 0:
                    st.session_state.question_idx = idx - 1
                    st.rerun()
        with nav_mid:
            st.markdown(
                f'<div style="text-align:center;padding-top:6px;" class="cairo-counter">'
                f"{idx + 1:02d} / {len(questions):02d}"
                f" · {q.id}</div>",
                unsafe_allow_html=True,
            )
        with nav_r:
            if st.button("NEXT →", key=f"ev_next_{phase_key}", width="stretch"):
                if idx < len(questions) - 1:
                    st.session_state.question_idx = idx + 1
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════════════
mode = st.session_state.get("mode", "story")
if mode == "story":
    render_story_mode()
elif mode in ("phase1", "phase2", "hypothesis"):
    render_evidence_mode(mode)
else:
    st.error(f"Unknown mode: {mode}")
