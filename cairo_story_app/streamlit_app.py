"""Cairo Transport · Layla · Masari — main Streamlit entry."""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import streamlit as st

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
STORY_STATIC_URL = "app/static/story_assets/index.html?returnTo=/"


def _ensure_story_static_assets() -> bool:
    """Expose the standalone story through Streamlit static serving."""
    source_dir = APP_ROOT / "story"
    if not STORY_HTML_PATH.exists():
        return False

    static_roots = [
        Path.cwd() / "static" / "story_assets",
        APP_ROOT / "static" / "story_assets",
    ]
    unique_roots: list[Path] = []
    for root in static_roots:
        if root.resolve() not in [p.resolve() for p in unique_roots]:
            unique_roots.append(root)

    for target_dir in unique_roots:
        target_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("index.html", "density3d.html"):
            src = source_dir / filename
            if not src.exists():
                continue
            dst = target_dir / filename
            if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)
    return True


def render_story_mode():
    """Launch the standalone cinematic HTML instead of embedding it.

    The Streamlit app stays as the evidence dashboard; the story opens as its
    own full-screen static page.
    """
    assets_ready = _ensure_story_static_assets()
    st.markdown(
        """
        <style>
          .main .block-container {
            max-width: 1180px !important;
            padding-top: 5.5rem !important;
          }
          .story-launch-card {
            position: relative;
            overflow: hidden;
            min-height: 520px;
            border-radius: 28px;
            border: 1px solid rgba(88,166,255,0.24);
            background:
              radial-gradient(circle at 20% 18%, rgba(88,166,255,0.22), transparent 34%),
              radial-gradient(circle at 82% 24%, rgba(42,157,143,0.20), transparent 30%),
              linear-gradient(135deg, rgba(13,17,23,0.96), rgba(7,9,12,0.98));
            box-shadow: 0 28px 90px rgba(0,0,0,0.45), inset 0 0 70px rgba(88,166,255,0.05);
            padding: 64px;
          }
          .story-launch-card::before {
            content: "";
            position: absolute;
            inset: -2px;
            background: linear-gradient(110deg, transparent 0%, rgba(233,196,106,0.10) 45%, transparent 70%);
            transform: translateX(-55%);
            animation: story-scan 5s linear infinite;
            pointer-events: none;
          }
          @keyframes story-scan {
            from { transform: translateX(-70%); }
            to { transform: translateX(70%); }
          }
          .story-launch-kicker {
            color: #58A6FF;
            font-family: 'Share Tech Mono', monospace;
            letter-spacing: 0.42em;
            text-transform: uppercase;
            font-size: 0.78rem;
            margin-bottom: 18px;
          }
          .story-launch-title {
            max-width: 780px;
            font-size: clamp(2.4rem, 6vw, 5.2rem);
            line-height: 0.96;
            font-weight: 900;
            letter-spacing: -0.05em;
            color: #E6EDF3;
            margin: 0 0 24px;
          }
          .story-launch-body {
            max-width: 720px;
            color: rgba(201,209,217,0.86);
            font-size: 1.06rem;
            line-height: 1.8;
            margin-bottom: 36px;
          }
          .story-launch-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 18px 28px;
            border-radius: 999px;
            color: #071018 !important;
            background: linear-gradient(90deg, #E9C46A, #58A6FF, #2A9D8F);
            font-weight: 900;
            letter-spacing: 0.16em;
            text-decoration: none !important;
            text-transform: uppercase;
            box-shadow: 0 16px 44px rgba(88,166,255,0.28);
          }
          .story-launch-note {
            margin-top: 22px;
            color: rgba(139,148,158,0.88);
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.86rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if not assets_ready:
        st.error("Story HTML was not found at `cairo_story_app/story/index.html`.")
        return

    st.markdown(
        f"""
        <section class="story-launch-card">
          <div class="story-launch-kicker">Cinematic Story · Standalone HTML</div>
          <h1 class="story-launch-title">Launch the Cairo · Layla · Masari experience</h1>
          <p class="story-launch-body">
            The Streamlit app now keeps the evidence dashboard separate from the cinematic story.
            Click below to leave Streamlit and open the original <code>story/index.html</code>
            as its own full-screen page.
          </p>
          <a class="story-launch-button" href="{STORY_STATIC_URL}" target="_self">
            Open Story
          </a>
          <div class="story-launch-note">
            Route: <code>{STORY_STATIC_URL}</code> · standalone static page.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


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
