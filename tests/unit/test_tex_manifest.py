"""Tests for the TeX manifest loader (DOWNSTREAM-TEX-001). Offline: the fixture is a copy of a crawl-smoke manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from math_trace.constants import REPO_ROOT
from math_trace.tex_manifest import TexManifestError, load_tex_sources

FIXTURE_MANIFEST = REPO_ROOT / "tests" / "fixtures" / "tex_manifest" / "2610.22341v1" / "manifest.json"
CC_BY_NC_LICENCE = "https://creativecommons.org/licenses/by-nc/4.0/"


def _stage_bundle(tmp_path: Path, edits: dict[str, Any] | None = None) -> Path:
    """Copy the fixture manifest into tmp_path, apply field edits, and create every listed file under src/."""
    bundle = tmp_path / "2610.22341v1"
    bundle.mkdir()
    manifest = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    manifest.update(edits or {})
    manifest_path = bundle / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    for entry in manifest["extracted"]:
        target = bundle / "src" / entry
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    return manifest_path


def test_saved_cc_by_manifest_loads_tex_sources(tmp_path: Path) -> None:
    manifest_path = _stage_bundle(tmp_path)

    sources = load_tex_sources(manifest_path)

    expected = sorted(
        (manifest_path.parent / "src" / entry)
        for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["extracted"]
        if entry.endswith(".tex")
    )
    assert sorted(sources) == expected
    assert len(sources) > 0
    assert all(path.suffix == ".tex" and path.is_file() for path in sources)


def test_non_saved_manifest_is_refused(tmp_path: Path) -> None:
    manifest_path = _stage_bundle(tmp_path, {"status": "rejected"})

    with pytest.raises(TexManifestError, match="status is 'rejected', expected 'saved'"):
        load_tex_sources(manifest_path)


def test_cc_by_nc_manifest_is_refused(tmp_path: Path) -> None:
    manifest_path = _stage_bundle(tmp_path, {"licence": CC_BY_NC_LICENCE})

    with pytest.raises(TexManifestError, match="is not on the allowed list"):
        load_tex_sources(manifest_path)


def test_missing_listed_file_is_refused(tmp_path: Path) -> None:
    manifest_path = _stage_bundle(tmp_path)
    (manifest_path.parent / "src" / "main.tex").unlink()

    with pytest.raises(TexManifestError, match="listed file is missing"):
        load_tex_sources(manifest_path)


def test_missing_manifest_is_refused(tmp_path: Path) -> None:
    with pytest.raises(TexManifestError, match="manifest file does not exist"):
        load_tex_sources(tmp_path / "absent" / "manifest.json")


def test_extracted_entry_escaping_src_is_refused(tmp_path: Path) -> None:
    manifest_path = _stage_bundle(tmp_path, {"extracted": ["../outside.tex"]})

    with pytest.raises(TexManifestError, match="escapes src/"):
        load_tex_sources(manifest_path)
