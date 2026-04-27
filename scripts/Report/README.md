# Cairo Public Transport · Formal Report

Comprehensive LaTeX/PDF report covering Phase 1 (existing transport reality, 12 questions, 4 structural gaps) and Phase 2 (post-2014 infrastructure, 13 questions, 3 hypothesis tests, 3 AI techniques).

## Build

```bash
cd Report
bash build.sh        # runs pdflatex twice
open main.pdf        # macOS
```

## Layout

```
Report/
├── main.tex                # master file
├── preamble.tex            # dark Plotly palette + helpers
├── build.sh                # pdflatex wrapper
├── sections/               # 19 .tex chapter files
├── figures/                # ~160 PNGs (auto-rendered from HTML)
├── datasets/               # CSV summary tables
└── scripts/
    └── htmls_to_pngs.py    # selenium-based HTML → PNG converter
```

## Regenerate figures

If any visualization HTML is updated, re-run:

```bash
python3 scripts/htmls_to_pngs.py
```

This walks `Exports/`, `Phase2/Exports/`, `Phase2/*.html` and writes PNGs to `Report/figures/`.

## Dependencies

- TeX Live (pdflatex, ≥ 2022 recommended)
- Python 3.10+
- `pip install kaleido selenium webdriver-manager`
- Google Chrome (selenium uses headless Chromium)
