"""Phase 2 notebook builder helpers. Lives in drafts/ so the Phase2/ folder
stays clean. Importable by inline scripts that extend the two notebooks.

Exports:
- md(src), code(src)   : make a notebook cell dict
- CODE_EXPL(body)      : ⟐ blue code-explanation block
- SEC_BANNER(n, title) : ── SECTION NN ── banner
- INSIGHT(body)        : ✦ coral visualization-insight block
- INTEGRATION(body)    : ◈ teal-purple integration block
- METHOD(body)         : ⟁ purple-dashed methodology-enhancement block
- append_cells(path, cells)  : load, append, save
- run_notebook(path, timeout): execute clean-kernel in place
"""
from pathlib import Path
import json
import subprocess
import uuid


def _cell_id():
    return uuid.uuid4().hex[:12]


def md(src: str) -> dict:
    return {"cell_type": "markdown", "id": _cell_id(), "metadata": {},
            "source": src.splitlines(keepends=True)}


def code(src: str) -> dict:
    return {"cell_type": "code", "id": _cell_id(), "execution_count": None,
            "metadata": {}, "outputs": [], "source": src.splitlines(keepends=True)}


def CODE_EXPL(body: str) -> dict:
    return md(f"""<div style="background:rgba(88,166,255,0.06);border-left:3px solid #58A6FF;padding:14px 20px;border-radius:0 6px 6px 0;margin:16px 0;">
  <span style="font-family:'Share Tech Mono',monospace;color:#58A6FF;font-size:.85em;letter-spacing:.15em;">⟐ CODE EXPLANATION</span>
  <p style="margin:8px 0 0;color:#C9D1D9;line-height:1.6;">{body}</p>
</div>
""")


def SEC_BANNER(n: str, title: str) -> dict:
    return md(f"""<div style="margin:32px 0 16px;border-top:1.5px solid rgba(88,166,255,0.18);padding-top:22px;">
  <span style="font-family:'Orbitron',monospace;font-size:.6em;color:#58A6FF;letter-spacing:.4em;">── SECTION {n} ──</span>
  <h2 style="font-family:'Orbitron',monospace;font-size:1.6em;color:#E9C46A;margin:6px 0;">{title}</h2>
</div>
""")


def INSIGHT(body: str) -> dict:
    return md(f"""<div style="background:rgba(42,157,143,.06);border-left:3px solid #E86F51;border-radius:0 8px 8px 0;padding:18px 22px;margin:18px 0;">
  <span style="font-family:'Share Tech Mono',monospace;color:#E86F51;font-size:.85em;letter-spacing:.15em;">✦ VISUALIZATION INSIGHT</span>
  <p style="margin:10px 0 0;color:#C9D1D9;line-height:1.65;">{body}</p>
</div>
""")


def INTEGRATION(body: str) -> dict:
    return md(f"""<div style="background:linear-gradient(135deg,rgba(88,166,255,.045),rgba(42,157,143,.045));border-left:3px solid #2A9D8F;padding:16px 22px;border-radius:0 6px 6px 0;margin:18px 0;">
  <span style="font-family:'Share Tech Mono',monospace;color:#2A9D8F;font-size:.85em;letter-spacing:.15em;">◈ INTEGRATION</span>
  <p style="margin:8px 0 0;color:#C9D1D9;line-height:1.6;">{body}</p>
</div>
""")


def METHOD(body: str) -> dict:
    return md(f"""<div style="background:rgba(123,45,142,0.08);border:1.5px dashed #7B2D8E;padding:22px 24px;border-radius:8px;margin:20px 0;">
  <span style="font-family:'Share Tech Mono',monospace;color:#7B2D8E;font-size:.85em;letter-spacing:.15em;">⟁ METHODOLOGY ENHANCEMENT</span>
  <p style="margin:10px 0 0;color:#C9D1D9;line-height:1.65;">{body}</p>
</div>
""")


def QCARD(qnum: str, question: str, why: str, data_path: str) -> dict:
    return md(f"""<div style="background:rgba(88,166,255,.04);border:1px solid rgba(88,166,255,.18);border-radius:10px;padding:18px 22px;margin:14px 0;">
  <span style="font-family:'Orbitron',monospace;color:#58A6FF;font-size:.7em;letter-spacing:.3em;">Q{qnum}</span>
  <h3 style="font-family:'Orbitron',monospace;color:#E9C46A;margin:4px 0 12px;font-size:1.15em;">{question}</h3>
  <p style="margin:6px 0;color:#C9D1D9;line-height:1.55;"><strong style="color:#2A9D8F;">Why it matters:</strong> {why}</p>
  <p style="margin:6px 0;color:#C9D1D9;line-height:1.55;"><strong style="color:#E86F51;">Data path:</strong> {data_path}</p>
</div>
""")


def HCARD(hnum: str, h0: str, h1: str, test: str, effect: str) -> dict:
    return md(f"""<div style="background:rgba(123,45,142,.06);border:1.5px solid rgba(123,45,142,.35);border-radius:10px;padding:18px 22px;margin:14px 0;">
  <span style="font-family:'Orbitron',monospace;color:#7B2D8E;font-size:.7em;letter-spacing:.3em;">HYPOTHESIS H{hnum}</span>
  <p style="margin:8px 0;color:#C9D1D9;line-height:1.6;"><strong style="color:#58A6FF;">H₀:</strong> {h0}</p>
  <p style="margin:8px 0;color:#C9D1D9;line-height:1.6;"><strong style="color:#2A9D8F;">H₁:</strong> {h1}</p>
  <p style="margin:8px 0;color:#C9D1D9;line-height:1.6;"><strong style="color:#E9C46A;">Test:</strong> {test}</p>
  <p style="margin:8px 0;color:#C9D1D9;line-height:1.6;"><strong style="color:#E86F51;">Effect size:</strong> {effect}</p>
</div>
""")


def append_cells(nb_path, cells):
    p = Path(nb_path)
    nb = json.loads(p.read_text())
    # Ensure ids exist on all cells so nbformat doesn't warn
    for c in nb["cells"]:
        c.setdefault("id", _cell_id())
    nb["cells"].extend(cells)
    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    return len(nb["cells"])


def run_notebook(nb_path, timeout=300):
    """Execute the notebook clean-kernel, in place."""
    r = subprocess.run(
        ["python3", "-m", "nbconvert", "--to", "notebook", "--execute",
         str(nb_path), "--output", Path(nb_path).name,
         f"--ExecutePreprocessor.timeout={timeout}"],
        capture_output=True, text=True, cwd=str(Path(nb_path).parent),
    )
    return r
