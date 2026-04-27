"""
Universal HTML → PNG converter for the Cairo report.

Renders every standalone HTML visualization (Plotly charts, Folium maps,
hero maps) at high resolution using a headless Chromium driver, then saves
PNGs into Report/figures/ with a stable, predictable naming scheme.

Usage:
    python3 Report/scripts/htmls_to_pngs.py
"""

import os
import sys
import time
import shutil
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ROOT = Path(__file__).resolve().parents[2]
P1_EXPORTS = ROOT / "Exports"
P2_EXPORTS = ROOT / "Phase2" / "Exports"
P2_ROOT = ROOT / "Phase2"
FIGURES = ROOT / "Report" / "figures"

VIEWPORT_W = 1600
VIEWPORT_H = 1000
PLOTLY_WAIT_S = 2.2
FOLIUM_WAIT_S = 5.0


def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={VIEWPORT_W},{VIEWPORT_H}")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_window_size(VIEWPORT_W, VIEWPORT_H)
    return drv


def is_folium(html_path: Path) -> bool:
    """Quick heuristic: Folium HTMLs include leaflet.js."""
    try:
        head = html_path.read_text(errors="ignore")[:8000]
    except Exception:
        return False
    return "leaflet" in head.lower() or "folium" in head.lower()


DARK_CSS = (
    "html, body { background-color: #0D1117 !important; "
    "margin: 0 !important; padding: 0 !important; color: #C9D1D9 !important; } "
    "div.plotly-graph-div { background-color: #0D1117 !important; } "
)


def inject_dark_theme(driver):
    """Inject CSS so the HTML body matches the dark report theme.

    IMPORTANT: only targets html/body and the outer Plotly container — never
    .main-svg, .plot-container or .svg-container, which would clobber the
    chart's own SVG fill attributes."""
    js = (
        "var s=document.createElement('style');"
        "s.type='text/css';"
        "s.appendChild(document.createTextNode(arguments[0]));"
        "document.head.appendChild(s);"
    )
    try:
        driver.execute_script(js, DARK_CSS)
    except Exception:
        pass


def screenshot_element_or_page(driver, out_path: Path, prefer_selector: str | None) -> bool:
    """Try to screenshot the chart container directly so we don't capture
    the dark-but-empty padding below. Fall back to full-page if the
    element isn't found or the element screenshot fails."""
    if prefer_selector:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, prefer_selector)
            png = elem.screenshot_as_png
            if png and len(png) > 4_000:
                out_path.write_bytes(png)
                return True
        except Exception:
            pass
    try:
        driver.save_screenshot(str(out_path))
        return True
    except Exception as exc:
        print(f"  ! full-page screenshot failed: {exc}")
        return False


def shoot(driver, html_path: Path, out_path: Path) -> bool:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = "file://" + str(html_path.resolve())
    try:
        driver.get(url)
    except Exception as exc:
        print(f"  ! load failed: {html_path.name} -> {exc}")
        return False
    inject_dark_theme(driver)
    folium = is_folium(html_path)
    time.sleep(FOLIUM_WAIT_S if folium else PLOTLY_WAIT_S)
    inject_dark_theme(driver)  # re-inject after JS finishes
    time.sleep(0.5)
    selector = ".folium-map" if folium else "div.plotly-graph-div"
    return screenshot_element_or_page(driver, out_path, selector)


def safe_stem(stem: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in stem)[:120]


JOBS: list[tuple[Path, Path]] = []

# ---- Phase 1 Exports/ (40 HTMLs) -> figures/phase1/<safe>.png
for html in sorted(P1_EXPORTS.glob("*.html")):
    JOBS.append((html, FIGURES / "phase1" / f"{safe_stem(html.stem)}.png"))

# ---- Phase 2 Exports/ root (48 HTMLs) -> figures/phase2/<safe>.png
for html in sorted(P2_EXPORTS.glob("*.html")):
    JOBS.append((html, FIGURES / "phase2" / f"{safe_stem(html.stem)}.png"))

# ---- Phase 2 hero maps (3) -> figures/hero/
for name in ("two_cairos_map.html", "headline_coverage_need_map.html", "adly_mansour_zoom.html"):
    p = P2_ROOT / name
    if p.exists():
        JOBS.append((p, FIGURES / "hero" / f"{safe_stem(p.stem)}.png"))

# ---- Phase 2 Exports/notebook_visuals (granular per-question, 71 files) -> figures/phase2/notebook/
nb_visuals = P2_EXPORTS / "notebook_visuals"
if nb_visuals.exists():
    for html in sorted(nb_visuals.glob("*.html")):
        JOBS.append((html, FIGURES / "phase2" / "notebook" / f"{safe_stem(html.stem)}.png"))


def main():
    if shutil.which("google-chrome") is None and shutil.which("chromium") is None:
        # webdriver-manager will fetch a chromedriver but the OS still needs
        # a real Chrome/Chromium binary; macOS usually has Google Chrome
        # installed at /Applications/. webdriver-manager finds it via system
        # discovery, so this is informational only.
        pass

    driver = make_driver()
    ok, fail = 0, 0
    try:
        for i, (html, out) in enumerate(JOBS, 1):
            if out.exists() and out.stat().st_size > 5_000:
                print(f"[{i}/{len(JOBS)}] skip (exists): {out.name}")
                ok += 1
                continue
            print(f"[{i}/{len(JOBS)}] {html.parent.name}/{html.name} -> {out.relative_to(ROOT)}")
            if shoot(driver, html, out):
                ok += 1
            else:
                fail += 1
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print(f"\nDone. ok={ok} fail={fail} total={len(JOBS)}")
    sys.exit(0 if fail == 0 else 2)


if __name__ == "__main__":
    main()
