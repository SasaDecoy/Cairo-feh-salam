# Cairo Transport · Layla · Masari

Interactive data-science story and product pitch for Cairo transport accessibility.

The project combines Phase 1 transport-demand analysis with Phase 2 scraped and integrated datasets to ask one question:

> Where is the gap between what Cairo built and where Cairo lives?

The Streamlit app presents the answer as a cinematic story about Layla, an Imbaba-to-Maadi commuter, then lets viewers inspect the evidence question by question.

## Live App Entry Point

Run the Streamlit app from:

```bash
streamlit run cairo_story_app/streamlit_app.py
```

## Repository Structure

- `cairo_story_app/` - Streamlit app, story page, evidence pages, and app assets.
- `CleanedData/` - Phase 1 processed datasets used by the app.
- `Phase2/CleanedData/` - Phase 2 scraped/cleaned outputs.
- `Phase2/Integrated/` - Phase 2 integrated matching outputs.
- `Phase2/*.ipynb` - scraping/cleaning and analysis notebooks.
- `Exports/` - Plotly HTML evidence exports used in the app.
- `drafts/MASARI_PHASE2_STORY_SCENES.md` - polished story/narrative source.

Raw scrape caches and notebook backups are intentionally ignored to keep the GitHub repository deployable.

## Local Setup

Python 3.11 is recommended.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run cairo_story_app/streamlit_app.py
```

On macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run cairo_story_app/streamlit_app.py
```

## Deploy On Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Choose the GitHub repository.
4. Set the main file path to:

```text
cairo_story_app/streamlit_app.py
```

5. Deploy.

The app auto-discovers the project root and reads `CleanedData/`, `Phase2/`, and `Exports/` from the repository.

## Rebuild Story Data

The cinematic story uses a generated JavaScript data bundle:

```bash
python cairo_story_app/story/build_story_data.py
```

This reads the processed CSV artifacts and writes:

```text
cairo_story_app/story/story_data.js
```

## Notes

- The app is designed for presentation mode, preferably in Chrome.
- Raw scraping caches under `Phase2/RawData/` are excluded from GitHub.
- Some notebook cells require geospatial packages and network access if rerun from scratch.
