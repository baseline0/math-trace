"""Hermetic unit tests for scripts/render_literature_lean.py."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import render_literature_lean

runner = CliRunner()
pytestmark = pytest.mark.unit

SAMPLE_CLAIMS = [
    {
        "paperId": "quant-ph-9605043",
        "claimId": "C-steane-1996-code",
        "title": "Error Correcting Codes in Quantum Theory (Steane)",
        "codeN": 7,
        "codeK": 1,
        "codeDistance": 3,
        "thresholdPpm": 10000,
        "assumptions": ["depolarizing_channel", "css_structure"],
    },
    {
        "paperId": "quant-ph-9508027",
        "claimId": "C-shor-1995-code",
        "title": "Scheme for reducing decoherence in quantum computer memory (Shor)",
        "codeN": 9,
        "codeK": 1,
        "codeDistance": 3,
        "thresholdPpm": 11000,
        "assumptions": ["single_qubit_arbitrary_error"],
    },
]


def test_render_literature_lean(tmp_path: Path) -> None:
    lit_json = tmp_path / "lit_claims.json"
    lean_out = tmp_path / "Literature.lean"
    claims_toml = tmp_path / "claims.toml"

    # Copy real claims.toml to tmp_path
    original_toml = (REPO_ROOT / "lean" / "claims.toml").read_text(encoding="utf-8")
    claims_toml.write_text(original_toml, encoding="utf-8")

    # Write sample JSON
    lit_json.write_text(json.dumps(SAMPLE_CLAIMS, indent=2), encoding="utf-8")

    # Run the rendering script via CliRunner
    result = runner.invoke(
        render_literature_lean.app,
        ["--json", str(lit_json), "--out", str(lean_out), "--toml", str(claims_toml)],
    )
    assert result.exit_code == 0
    assert lean_out.is_file()

    lean_text = lean_out.read_text(encoding="utf-8")
    for claim in SAMPLE_CLAIMS:
        ident = claim["claimId"].replace("-", "_")
        assert f"def {ident}_bound : QECBound" in lean_text
        assert f"theorem {ident}_theorem : True" in lean_text

    # Compute SHA256 of the generated Lean file
    sha256 = hashlib.sha256(lean_out.read_bytes()).hexdigest()

    toml_text = claims_toml.read_text(encoding="utf-8")
    for claim in SAMPLE_CLAIMS:
        ident = claim["claimId"].replace("-", "_")
        assert f'id = "{claim["claimId"]}"' in toml_text
        assert f'theorem_name = "GraphPolicy.Literature.{ident}_theorem"' in toml_text
        assert f'theorem_sha256 = "{sha256}"' in toml_text
