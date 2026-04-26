"""Phase 2 reusable display utilities — Phase-1-styled HTML tables + info boxes.

Palette (shared with Phase 1 cell [0] CSS theme):
  bg panel   #161B22   border  #30363D
  title      #58A6FF   muted   #8B949E   body  #C9D1D9
  accent hi  #E9C46A   success #2A9D8F   alert #E86F51

Usage from a notebook:
    sys.path.insert(0, '../drafts')
    from phase2_utils import show_df, show_metrics, show_note

    show_df(matrix, title="Q18b · gap coverage matrix",
            caption="% of each Phase-1 gap within 2 km of a new-mode station")
    show_metrics({"p-value": 0.002, "Cliff delta": 0.83}, title="H3 result")
"""
from __future__ import annotations
import html as _html
from IPython.display import display, HTML
import pandas as pd

_PANEL_BG    = "rgba(22,27,34,0.45)"     # semi-transparent to blend with Phase 1 theme
_PANEL_BG_2  = "rgba(13,17,23,0.4)"
_BORDER      = "rgba(88,166,255,0.18)"
_TITLE       = "#58A6FF"
_SUBTITLE    = "#2A9D8F"
_MUTED       = "#8B949E"
_BODY        = "#C9D1D9"
_ACCENT      = "#E9C46A"
_ALERT       = "#E86F51"


def _format_cell(v, fmt=None):
    """Format a scalar for HTML display."""
    if fmt is not None:
        try:
            return fmt(v) if callable(fmt) else format(v, fmt)
        except Exception:
            pass
    if isinstance(v, float):
        if pd.isna(v):
            return '<span style="color:#666;">—</span>'
        if abs(v) < 0.01 and v != 0:
            return f"{v:.3e}"
        return f"{v:,.3f}" if abs(v) < 1000 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}"
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<span style="color:#666;">—</span>'
    return _html.escape(str(v))


def show_df(df: pd.DataFrame, title: str | None = None, caption: str | None = None,
            max_rows: int = 25, formatters: dict | None = None,
            highlight_col: str | None = None):
    """Render a DataFrame as a Phase-1-styled HTML table.

    Args:
        df: the DataFrame to render.
        title: bold blue header above the table.
        caption: small italic muted line under the title.
        max_rows: trim the DataFrame with a `… N more rows` footer if exceeded.
        formatters: {column_name: format_str_or_callable}.
        highlight_col: name of a column whose values get accent-yellow coloring.
    """
    df_show = df.reset_index(drop=True)
    trimmed = False
    if max_rows and len(df_show) > max_rows:
        df_show = df_show.head(max_rows)
        trimmed = True

    formatters = formatters or {}

    # Header
    hdr_cells = "".join(
        f'<th style="padding:6px 12px;color:{_TITLE};text-align:left;font-weight:600;'
        f'border-bottom:1px solid {_BORDER};font-size:12px;letter-spacing:.08em;'
        f'text-transform:uppercase;">{_html.escape(str(c))}</th>'
        for c in df_show.columns
    )

    # Rows
    rows_html = []
    for ri, row in df_show.iterrows():
        bg = "rgba(255,255,255,0.02)" if ri % 2 else "transparent"
        cells = []
        for col in df_show.columns:
            v = row[col]
            fmt = formatters.get(col)
            rendered = _format_cell(v, fmt)
            color = _ACCENT if col == highlight_col else _BODY
            cells.append(
                f'<td style="padding:5px 12px;color:{color};'
                f'border-bottom:1px solid rgba(48,54,61,0.4);font-family:\'Share Tech Mono\',monospace;'
                f'font-size:12px;">{rendered}</td>'
            )
        rows_html.append(f'<tr style="background:{bg};">{"".join(cells)}</tr>')

    title_html = (f'<div style="color:{_TITLE};font-weight:700;margin-bottom:6px;'
                  f'letter-spacing:.2em;font-size:11px;text-transform:uppercase;">{_html.escape(title)}</div>'
                  if title else "")
    cap_html = (f'<div style="color:{_MUTED};font-size:11px;margin-bottom:10px;font-style:italic;">'
                f'{_html.escape(caption)}</div>' if caption else "")
    footer = (f'<div style="color:{_MUTED};font-size:10px;padding:6px 12px;">'
              f'… {len(df) - max_rows:,} more rows (showing first {max_rows})</div>' if trimmed else "")

    display(HTML(f"""
<div style="background:{_PANEL_BG};border:1px solid {_BORDER};border-radius:8px;
padding:14px 16px;margin:12px 0;font-family:'Share Tech Mono',monospace;">
  {title_html}{cap_html}
  <table style="border-collapse:collapse;width:100%;">
    <thead><tr>{hdr_cells}</tr></thead>
    <tbody>{''.join(rows_html)}</tbody>
  </table>
  {footer}
</div>
"""))


def show_metrics(metrics: dict, title: str | None = None, highlight: set | None = None):
    """Render a key-value box (one row per metric). Use for test-statistic summaries."""
    highlight = highlight or set()
    rows = []
    for k, v in metrics.items():
        rendered = _format_cell(v)
        color = _ACCENT if k in highlight else _BODY
        weight = "600" if k in highlight else "400"
        rows.append(
            f'<tr>'
            f'<td style="color:{_MUTED};padding:4px 18px 4px 0;font-size:12px;">{_html.escape(str(k))}</td>'
            f'<td style="color:{color};font-weight:{weight};font-size:13px;font-family:\'Share Tech Mono\',monospace;">{rendered}</td>'
            f'</tr>'
        )
    title_html = (f'<div style="color:{_TITLE};font-weight:700;margin-bottom:10px;'
                  f'letter-spacing:.2em;font-size:11px;text-transform:uppercase;">{_html.escape(title)}</div>'
                  if title else "")
    display(HTML(f"""
<div style="background:{_PANEL_BG};border:1px solid {_BORDER};border-radius:8px;
padding:14px 18px;margin:12px 0;font-family:'Share Tech Mono',monospace;max-width:620px;">
  {title_html}
  <table style="border-collapse:collapse;">{''.join(rows)}</table>
</div>
"""))


def show_note(body_html: str, kind: str = "info", title: str | None = None):
    """Generic styled note box. kind ∈ {info, success, warn, accent}."""
    palette = {
        "info":    (_TITLE,    "88,166,255"),
        "success": (_SUBTITLE, "42,157,143"),
        "warn":    (_ALERT,    "232,111,81"),
        "accent":  (_ACCENT,   "233,196,106"),
    }
    border_color, rgb = palette.get(kind, palette["info"])
    title_html = (f'<div style="color:{border_color};font-weight:700;margin-bottom:8px;'
                  f'letter-spacing:.2em;font-size:11px;text-transform:uppercase;">{_html.escape(title)}</div>'
                  if title else "")
    display(HTML(f"""
<div style="background:rgba({rgb},0.06);border-left:3px solid {border_color};border-radius:0 8px 8px 0;
padding:14px 18px;margin:12px 0;color:{_BODY};font-size:13px;line-height:1.65;">
  {title_html}{body_html}
</div>
"""))
