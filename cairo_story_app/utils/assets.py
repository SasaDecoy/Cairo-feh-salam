"""Asset helpers: base64-encode PNGs as data URLs for PyDeck IconLayer."""
from __future__ import annotations

import base64
from pathlib import Path


# 1x1 coral PNG placeholder — used if the actual portrait is missing.
_PLACEHOLDER_DATAURL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAH0lEQVQYV2P8z8DwnwEPYBxV"
    "SIRCIv5BqMKRWjGqEAQACIsY/35cQlsAAAAASUVORK5CYII="
)


def image_to_data_url(path: Path) -> str:
    """PNG file -> data URL.

    PyDeck IconLayer fetches the icon from the browser (not Python). Regular
    relative paths fail inside Streamlit's dev server. Data URLs avoid the
    issue entirely.
    """
    p = Path(path)
    if not p.exists():
        return _PLACEHOLDER_DATAURL
    try:
        data = p.read_bytes()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except Exception:
        return _PLACEHOLDER_DATAURL


def layla_icon_data(portrait_path: Path) -> dict:
    """Icon spec consumed by PyDeck IconLayer."""
    return {
        "url": image_to_data_url(portrait_path),
        "width": 128,
        "height": 128,
        "anchorY": 64,
        "anchorX": 64,
        "mask": False,
    }
