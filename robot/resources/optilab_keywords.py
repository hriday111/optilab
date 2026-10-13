import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate_design(design_rel: str) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "optilab.cli", "validate", str(ROOT / design_rel)],
        cwd=ROOT,
        env=env,
    ).returncode


def error_count() -> int:
    findings = json.loads((ROOT / "reports" / "findings.json").read_text())
    return sum(1 for f in findings if f["severity"] == "ERROR")
