"""The Lean claim records in lean/claims.toml must match the Lean sources and pins they cite.

Offline and file-level: no git, no lake, no network. A changed theorem file with an unchanged record fails the
SHA-256 check (the drift check).
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path
from typing import Any

from math_trace.constants import REPO_ROOT

CLAIMS_PATH = REPO_ROOT / "lean" / "claims.toml"
LEAN_TOOLCHAIN_PATH = REPO_ROOT / "lean" / "lean-toolchain"
LAKE_MANIFEST_PATH = REPO_ROOT / "lean" / "lake-manifest.json"
CLAIM_ID = "C-guarded-policy-expressiveness"
FORBIDDEN_TOKENS = re.compile(r"\b(sorry|admit|native_decide|axiom)\b")


def _claim() -> dict[str, Any]:
    data = tomllib.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    matches = [claim for claim in data.get("claim", []) if claim.get("id") == CLAIM_ID]
    assert len(matches) == 1, f"expected exactly one claim with id {CLAIM_ID}, found {len(matches)}"
    return matches[0]


def _theorem_path(claim: dict[str, Any]) -> Path:
    return REPO_ROOT / claim["theorem_path"]


def test_claim_exists_by_id() -> None:
    claim = _claim()
    assert claim["verification"] == "formally_verified"


def test_theorem_file_exists() -> None:
    assert _theorem_path(_claim()).is_file()


def test_theorem_name_last_component_appears_in_theorem_file() -> None:
    claim = _claim()
    last = claim["theorem_name"].rsplit(".", 1)[-1]
    text = _theorem_path(claim).read_text(encoding="utf-8")
    assert re.search(rf"\b{re.escape(last)}\b", text), f"{last} does not appear in {claim['theorem_path']}"


def test_theorem_file_has_no_forbidden_tokens() -> None:
    text = _theorem_path(_claim()).read_text(encoding="utf-8")
    found = sorted(set(FORBIDDEN_TOKENS.findall(text)))
    assert not found, f"forbidden tokens in the theorem file: {found}"


def test_theorem_sha256_matches_file() -> None:
    """The drift check: a changed proof with an unchanged record fails here."""
    claim = _claim()
    digest = hashlib.sha256(_theorem_path(claim).read_bytes()).hexdigest()
    assert digest == claim["theorem_sha256"], (
        f"{claim['theorem_path']} changed: sha256 is {digest}, the record says {claim['theorem_sha256']}"
    )


def test_lean_toolchain_matches_file() -> None:
    recorded = LEAN_TOOLCHAIN_PATH.read_text(encoding="utf-8").strip()
    assert _claim()["lean_toolchain"] == recorded


def test_mathlib_revision_matches_manifest() -> None:
    manifest = json.loads(LAKE_MANIFEST_PATH.read_text(encoding="utf-8"))
    revs = [package["rev"] for package in manifest["packages"] if package["name"] == "mathlib"]
    assert len(revs) == 1, f"expected one mathlib entry in the lake manifest, found {len(revs)}"
    assert _claim()["mathlib_revision"] == revs[0]
