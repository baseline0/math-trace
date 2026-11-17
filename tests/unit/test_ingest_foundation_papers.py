"""Hermetic unit tests for scripts/ingest_foundation_papers.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import ingest_foundation_papers

runner = CliRunner()
pytestmark = pytest.mark.unit

MOCK_HERMES_RESPONSE = """```json
[
  {
    "paperId": "quant-ph-9605043",
    "claimId": "C-steane-1996-code",
    "title": "Error Correcting Codes in Quantum Theory (Steane)",
    "codeN": 7,
    "codeK": 1,
    "codeDistance": 3,
    "thresholdPpm": 10000,
    "assumptions": ["depolarizing_channel", "css_structure"]
  },
  {
    "paperId": "quant-ph-9508027",
    "claimId": "C-shor-1995-code",
    "title": "Scheme for reducing decoherence in quantum computer memory (Shor)",
    "codeN": 9,
    "codeK": 1,
    "codeDistance": 3,
    "thresholdPpm": 11000,
    "assumptions": ["single_qubit_arbitrary_error"]
  }
]
```"""


def test_ingest_foundation_papers_mocked(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Mock prompt", encoding="utf-8")
    out_file = tmp_path / "lit_claims.json"

    with (
        patch.object(ingest_foundation_papers, "_run_hermes", return_value=MOCK_HERMES_RESPONSE),
        patch("subprocess.run") as mock_sub,
    ):
        result = runner.invoke(
            ingest_foundation_papers.app,
            ["--prompt", str(prompt_file), "--out", str(out_file)],
        )
        assert result.exit_code == 0
        assert out_file.is_file()

        data = json.loads(out_file.read_text(encoding="utf-8"))
        assert len(data) == 2
        assert data[0]["claimId"] == "C-steane-1996-code"
        assert data[1]["claimId"] == "C-shor-1995-code"
        assert mock_sub.call_count == 2  # render_literature_lean and just lean-verify
