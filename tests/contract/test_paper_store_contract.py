"""Contract test: the paper store reader against the v1 sample store owned by fleet-coordination.

The format is contracts/paper-store/FORMAT.md in the fleet-coordination checkout beside this repo. The sample in
its sample/ folder is the fixture. If that checkout is absent, the whole module skips with the path it looked for.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from math_trace.constants import REPO_ROOT
from math_trace.paper_store import (
    ALLOWED_LICENCES,
    PaperBrokenError,
    PaperRestrictedError,
    PaperStatus,
    PaperStore,
)

SAMPLE_DIR = REPO_ROOT.parent / "fleet-coordination" / "contracts" / "paper-store" / "sample"

if not SAMPLE_DIR.is_dir():
    pytest.skip(
        f"fleet-coordination checkout not found; expected the paper-store sample at {SAMPLE_DIR}",
        allow_module_level=True,
    )

PAPER_DIR = SAMPLE_DIR / "papers" / "2610.23820"
MANIFEST_PATH = PAPER_DIR / "v1.json"

# Every manifest field the contract's table lists, with the Python types the contract allows. None means
# string-or-null.
MANIFEST_FIELD_TYPES: dict[str, type | None] = {
    "schema_version": int,
    "arxiv_id": str,
    "version": str,
    "title": str,
    "doi": None,
    "licence": str,
    "pdf_sha256": None,
    "tex_sha256": None,
    "status": str,
    "fetched_at": str,
}
MEMBERSHIP_FIELDS = ("topic", "arxiv_id", "query", "added_at")


def _sample_manifest() -> dict[str, Any]:
    manifest: dict[str, Any] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest


def _membership_lines() -> list[dict[str, Any]]:
    path = SAMPLE_DIR / "catalog" / "membership.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _copy_sample(tmp_path: Path) -> Path:
    """Copy the sample store so a test can break it without touching the checkout."""
    target = tmp_path / "store"
    shutil.copytree(SAMPLE_DIR, target)
    return target


def test_manifest_has_every_contract_field_with_its_type() -> None:
    manifest = _sample_manifest()

    assert set(MANIFEST_FIELD_TYPES) <= set(manifest), "the sample manifest is missing a contract field"
    for field, expected in MANIFEST_FIELD_TYPES.items():
        value = manifest[field]
        if expected is None:
            assert value is None or isinstance(value, str), f"{field} must be a string or null"
        else:
            assert isinstance(value, expected), f"{field} must be {expected.__name__}"
    assert manifest["schema_version"] == 1
    assert manifest["status"] in {s.value for s in PaperStatus}
    datetime.fromisoformat(manifest["fetched_at"])


def test_manifest_arxiv_id_and_version_match_the_layout() -> None:
    manifest = _sample_manifest()

    assert manifest["arxiv_id"] == PAPER_DIR.name
    assert MANIFEST_PATH.name == f"{manifest['version']}.json"
    assert (PAPER_DIR / "latest").read_text(encoding="utf-8").strip() == MANIFEST_PATH.name


def test_sample_licence_is_on_the_allowed_list() -> None:
    assert _sample_manifest()["licence"] in ALLOWED_LICENCES


def test_blob_hash_matches_its_content() -> None:
    manifest = _sample_manifest()
    pdf_sha = manifest["pdf_sha256"]
    assert pdf_sha is not None, "the sample is expected to carry a PDF blob"

    blob = SAMPLE_DIR / "blobs" / pdf_sha[:2] / pdf_sha
    assert blob.is_file(), f"blob named by pdf_sha256 is absent: {blob}"
    assert hashlib.sha256(blob.read_bytes()).hexdigest() == pdf_sha


def test_reader_returns_the_manifest_the_file_holds() -> None:
    manifest = PaperStore(SAMPLE_DIR).read_manifest("2610.23820")
    raw = _sample_manifest()

    assert manifest.arxiv_id == raw["arxiv_id"]
    assert manifest.version == raw["version"]
    assert manifest.title == raw["title"]
    assert manifest.doi == raw["doi"]
    assert manifest.licence == raw["licence"]
    assert manifest.pdf_sha256 == raw["pdf_sha256"]
    assert manifest.tex_sha256 == raw["tex_sha256"]
    assert manifest.status.value == raw["status"]
    assert manifest.fetched_at == raw["fetched_at"]


def test_membership_lines_have_every_field_and_resolve_to_a_paper() -> None:
    lines = _membership_lines()
    assert lines, "the sample membership file has no lines"
    store = PaperStore(SAMPLE_DIR)

    for line in lines:
        for field in MEMBERSHIP_FIELDS:
            assert isinstance(line.get(field), str), f"membership field {field} must be a string"
        assert (SAMPLE_DIR / "papers" / line["arxiv_id"]).is_dir(), f"no paper directory for {line['arxiv_id']}"
        assert line["arxiv_id"] in store.list_papers(line["topic"])


def test_restricted_licence_is_refused(tmp_path: Path) -> None:
    store_root = _copy_sample(tmp_path)
    manifest_path = store_root / "papers" / "2610.23820" / "v1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["licence"] = "https://creativecommons.org/licenses/by-nc/4.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(PaperRestrictedError):
        PaperStore(store_root).read_paper("2610.23820")


def test_sample_paper_is_read_with_its_blob_verified() -> None:
    record = PaperStore(SAMPLE_DIR).read_paper("2610.23820")

    assert record.manifest.status is PaperStatus.SAVED
    assert record.tex is None, "the sample has no tex_sha256, so no TeX bytes are returned"


def test_missing_pdf_blob_is_reported_broken(tmp_path: Path) -> None:
    store_root = _copy_sample(tmp_path)
    pdf_sha = _sample_manifest()["pdf_sha256"]
    (store_root / "blobs" / pdf_sha[:2] / pdf_sha).unlink()

    with pytest.raises(PaperBrokenError, match="pdf blob"):
        PaperStore(store_root).read_paper("2610.23820")
