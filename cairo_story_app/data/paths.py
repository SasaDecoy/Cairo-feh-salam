"""Cross-machine path resolver. Finds the Phase 1 + Phase 2 data folders."""
from __future__ import annotations

import os
from pathlib import Path


def resolve_data_root() -> Path:
    if "DATA_ROOT" in os.environ:
        env_path = Path(os.environ["DATA_ROOT"])
        if env_path.exists():
            return env_path

    app_dir = Path(__file__).resolve().parent.parent
    candidates = [
        app_dir.parent,
        app_dir,
    ]
    for candidate in candidates:
        if (candidate / "Phase2" / "CleanedData").exists() or (candidate / "CleanedData").exists():
            return candidate
    return app_dir


DATA_ROOT = resolve_data_root()
APP_ROOT = Path(__file__).resolve().parent.parent

PHASE2_CLEAN = DATA_ROOT / "Phase2" / "CleanedData"
PHASE2_INTEGRATED = DATA_ROOT / "Phase2" / "Integrated"
PHASE2_EXPORTS_DIR = DATA_ROOT / "Phase2"
PHASE1_CLEAN = DATA_ROOT / "CleanedData"
EXPORTS = DATA_ROOT / "Exports"

ROUTES_DIR = APP_ROOT / "routes"
ASSETS_DIR = APP_ROOT / "assets"
STYLE_DIR = APP_ROOT / "style"
