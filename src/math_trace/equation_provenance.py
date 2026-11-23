"""Stable equation identity and code/proof provenance for math-trace.

The catalog (``catalogs/quantum_formulas.json``) is the shape equations-history ingests and must stay
contract-compatible. This module publishes a separate artifact, ``artifacts/equation_provenance.json``,
with additive fields: a stable id, a hash of the canonical symbolic expression, the source file and
line, and the formal-claim records that point at Lean theorems. Nothing here rewrites the catalog.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from collections.abc import Sequence
from typing import Any

import sympy as sp

from math_trace.constants import REPO_ROOT
from math_trace.equation_identity import canonical_srepr
from math_trace.quantum_formulas import FORMULAS, QuantumFormula

PROVENANCE_PATH = REPO_ROOT / "artifacts" / "equation_provenance.json"
CLAIMS_TOML_PATH = REPO_ROOT / "lean" / "claims.toml"
LIT_CLAIMS_PATH = REPO_ROOT / "artifacts" / "lit_claims.json"
SOURCE_FILE = "src/math_trace/quantum_formulas.py"


def git_commit() -> str | None:
    """Short HEAD commit, or None outside a git checkout. Informational; not part of the hash."""
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def formula_expr_hash(formula: QuantumFormula) -> str:
    """Hash of the canonical residual expression; source text and comments do not change it."""
    value = formula.residual()
    text = sp.srepr(value) if isinstance(value, sp.MatrixBase) else canonical_srepr(value)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _formal_claims() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if CLAIMS_TOML_PATH.is_file():
        with CLAIMS_TOML_PATH.open("rb") as handle:
            data = tomllib.load(handle)
        for claim in data.get("claim", []):
            records.append(
                {
                    "claim_id": claim.get("id"),
                    "verification": claim.get("verification"),
                    "theorem_path": claim.get("theorem_path"),
                    "theorem_name": claim.get("theorem_name"),
                    "theorem_sha256": claim.get("theorem_sha256"),
                    "source_commit": claim.get("source_commit"),
                }
            )
    return records


def export_equation_provenance(
    formulas: Sequence[QuantumFormula] = FORMULAS,
    *,
    commit: str | None = None,
) -> dict[str, Any]:
    """Build the provenance artifact for the given formulas."""
    equations: dict[str, Any] = {}
    for formula in formulas:
        equations[formula.name] = {
            "id": f"math-trace/{formula.name}",
            "expr_hash": formula_expr_hash(formula),
            "source_file": SOURCE_FILE,
            "line": formula.source_line,
            "function": None,
            "latex": formula.latex,
            "source": formula.source,
            "holds": formula.holds(),
        }
    literature: list[dict[str, Any]] = []
    if LIT_CLAIMS_PATH.is_file():
        literature = json.loads(LIT_CLAIMS_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "source_commit": commit if commit is not None else git_commit(),
        "source_repo": "math-trace",
        "equations": equations,
        "formal_claims": _formal_claims(),
        "literature_claims": literature,
    }


def main() -> None:
    payload = export_equation_provenance()
    PROVENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Exported provenance for {len(payload['equations'])} equations to {PROVENANCE_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
