from __future__ import annotations

from pathlib import Path

from .model import Design
from .validate import Finding


def write_markdown(design: Design, findings: list[Finding], path: str | Path) -> None:
    lines = [
        f"# Design report: {design.network.name}",
        "",
        design.network.description or "",
        "",
        "## Sites",
    ]
    for s in design.sites:
        lines.append(f"- `{s.id}` ({s.role}) — {s.location or 'n/a'}")
    lines += ["", "## Links"]
    for ln in design.links:
        lines.append(
            f"- `{ln.id}` {ln.a}↔{ln.z}: {ln.length_km} km, "
            f"est. loss {ln.span_loss_db():.2f} dB"
        )
    lines += ["", "## Findings"]
    for f in findings:
        lines.append(f"- **{f.severity}** `{f.code}`: {f.message}")
    Path(path).write_text("\n".join(lines) + "\n")
