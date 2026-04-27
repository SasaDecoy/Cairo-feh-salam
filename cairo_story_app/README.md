# Cairo Transport · Layla · Masari

Interactive Streamlit presentation of the BUE Phase 1 + Phase 2 data-science project on Cairo public transport. The app walks examiners through the scraping, cleaning, hypothesis testing, and insights via a commuter persona (Layla · Imbaba → Maadi) and a full per-question evidence mode.

## Run

Python 3.11 required (geopandas 1.0 wheels).

```bash
cd "cairo_story_app"
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open <http://localhost:8501>.

## Layout

- **Story mode** — 14-chapter narrative with animated PyDeck map and Layla node
- **Evidence mode** — one page per research question (Phase 1 Q1–Q12 + gaps, Phase 2 cleaning + Q13–Q25 + H1–H3 + synthesis maps)

Top nav: `[ STORY ] [ PHASE 1 ] [ PHASE 2 ]`.

## Data sources

The app auto-discovers the project data root (sibling `Phase2/`, `CleanedData/`, `Exports/` folders). Override with `DATA_ROOT=...` env var.

## Presentation rehearsal

1. Open the app on the presentation laptop 10 min early to pre-cache Carto tiles in the browser
2. Walk through every chapter once to pre-warm; every Phase 1 evidence page loads a Plotly HTML from `Exports/`
3. Full-screen Chrome (F11); hide bookmarks bar
4. Check projector resolution; adjust column ratios if needed

## Troubleshooting

| Symptom | Fix |
|---|---|
| Carto tiles don't load | Check wifi; `map_style="dark_no_labels"` preset is the fallback |
| Arabic shows tofu boxes | Google Fonts blocked by firewall; bundle `NotoSansArabic.woff2` locally |
| App crashes on chapter 12 | Disable `streamlit-autorefresh`; render Layla at static progress = 1.0 |
| Frosted cards look flat | Firefox doesn't fully support `backdrop-filter`; use Chrome for presentation |

## Known limitations

- LRT coordinates: 4 of 20 stations lack geocoded points (Overpass + Google fallback rescued 16)
- BRT scrape is partial (Google Maps is the only public source; 12 stations confirmed)
- Q18b matrix has 3 rows (no Monorail — the Cairo Monorail is not operational yet)
- SBERT gold set is 5 hand-labelled pairs — a small validation sample, noted in Phase 2 methodology
