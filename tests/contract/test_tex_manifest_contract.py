"""Contract tests: TeX manifests against the equations-history consumer schema.

The schema at equations-history/contracts/tex_manifest.schema.json is owned by the consumer. This repo must
conform to it. The manifest.json files are written by tool-lit-review; this repo only reads them, so the
writer-side check is limited to the keys the loader in math_trace.tex_manifest reads.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from math_trace.constants import REPO_ROOT

SCHEMA_PATH = REPO_ROOT.parent / "equations-history" / "contracts" / "tex_manifest.schema.json"
FIXTURE_GLOB = "tests/fixtures/tex_manifest/*/manifest.json"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# Keys that src/math_trace/tex_manifest.py reads (status, licence, extracted). Must stay a subset of the schema's
# required keys; if the loader starts reading another key, add it here.
LOADER_READ_KEYS: frozenset[str] = frozenset({"status", "licence", "extracted"})

FIXTURE_MANIFESTS = sorted(REPO_ROOT.glob(FIXTURE_GLOB))


def _load_schema() -> dict[str, Any]:
    """Return the consumer schema, or fail the test with the expected path if it is missing."""
    assert SCHEMA_PATH.is_file(), (
        f"consumer schema not found at {SCHEMA_PATH}; the equations-history checkout must sit beside math-trace"
    )
    schema: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema


def _load_manifest(path: Path) -> dict[str, Any]:
    """Return one manifest object from disk."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def test_fixture_manifests_exist() -> None:
    """The contract has something to check: at least one fixture manifest is present."""
    assert FIXTURE_MANIFESTS, f"no fixture manifests matched {FIXTURE_GLOB} under {REPO_ROOT}"


@pytest.mark.parametrize("manifest_path", FIXTURE_MANIFESTS, ids=lambda p: p.parent.name)
def test_fixture_manifest_validates_against_schema(manifest_path: Path) -> None:
    """Every fixture manifest validates against the equations-history schema."""
    schema = _load_schema()
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(_load_manifest(manifest_path)), key=lambda e: list(e.path))
    messages = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
    assert not messages, f"{manifest_path} violates {SCHEMA_PATH.name}:\n" + "\n".join(messages)


def test_loader_read_keys_are_required_by_schema() -> None:
    """The keys the loader reads from manifest.json are all required by the schema.

    This repo has no manifest writer, so this is the producer-side surface it can check.
    """
    schema = _load_schema()
    required = set(schema["required"])
    missing = LOADER_READ_KEYS - required
    assert not missing, f"loader reads keys the schema does not require: {sorted(missing)}"


@pytest.mark.parametrize("manifest_path", FIXTURE_MANIFESTS, ids=lambda p: p.parent.name)
def test_fixture_sha256_is_lowercase_hex_digest(manifest_path: Path) -> None:
    """sha256 is a 64-character lowercase hex string in every fixture manifest."""
    sha256 = _load_manifest(manifest_path).get("sha256")
    assert isinstance(sha256, str), f"{manifest_path}: sha256 must be a string, got {sha256!r}"
    assert SHA256_PATTERN.fullmatch(sha256), f"{manifest_path}: sha256 is not 64 lowercase hex chars: {sha256!r}"
