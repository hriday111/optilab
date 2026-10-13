from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .model import load_design
from .render_clab import write_clab
from .report import write_markdown
from .validate import has_errors, validate_design


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="optilab")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate design YAML")
    v.add_argument("design")
    v.add_argument("--report", default="reports/design-report.md")

    r = sub.add_parser("render", help="Render containerlab topology")
    r.add_argument("design")
    r.add_argument("-o", "--out", default="lab/demo-ring.clab.yml")

    args = p.parse_args(argv)
    design = load_design(args.design)

    if args.cmd == "render":
        out = write_clab(design, args.out)
        print(f"Wrote {out}")
        return 0

    if args.cmd == "validate":
        findings = validate_design(design)
        Path("reports").mkdir(exist_ok=True)
        write_markdown(design, findings, args.report)
        findings_path = Path("reports/findings.json")
        findings_path.write_text(
            json.dumps([f.__dict__ for f in findings], indent=2) + "\n"
        )
        print(json.dumps([f.__dict__ for f in findings], indent=2))
        print(f"Report: {args.report}")
        print(f"Findings: {findings_path}")
        return 1 if has_errors(findings) else 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
