"""Tests for the paper store reader (contracts/paper-store/FORMAT.md). Offline: each test builds its own store in tmp_path."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

from math_trace.paper_store import (
    PaperBrokenError,
    PaperNotFoundError,
    PaperRestrictedError,
    PaperStatus,
    PaperStore,
)

PAPER = "2610.23820"
CC_BY = "https://creativecommons.org/licenses/by/4.0"
TEX_BYTES = b"\\documentclass{article}\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_blob(root: Path, data: bytes) -> str:
    digest = _sha(data)
    path = root / "blobs" / digest[:2] / digest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return digest


def _manifest(**edits: Any) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "arxiv_id": PAPER,
        "version": "v1",
        "title": "A test paper",
        "doi": None,
        "licence": CC_BY,
        "pdf_sha256": None,
        "tex_sha256": None,
        "status": "saved",
        "fetched_at": "2026-10-20T00:00:00Z",
    }
    manifest.update(edits)
    return manifest


def _make_store(root: Path, manifest: dict[str, Any], *, file_name: str = "v1.json") -> Path:
    """Write a paper directory with a latest pointer to `file_name`, and return the store root."""
    paper_dir = root / "papers" / manifest.get("arxiv_id", PAPER)
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / file_name).write_text(json.dumps(manifest), encoding="utf-8")
    (paper_dir / "latest").write_text(file_name + "\n", encoding="utf-8")
    return root


def _add_membership(root: Path, *lines: dict[str, str]) -> None:
    catalog = root / "catalog"
    catalog.mkdir(exist_ok=True)
    with (catalog / "membership.jsonl").open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line) + "\n")


def test_reads_manifest_and_tex_blob(tmp_path: Path) -> None:
    tex_sha = _write_blob(tmp_path, TEX_BYTES)
    root = _make_store(tmp_path, _manifest(tex_sha256=tex_sha, status="saved"))

    record = PaperStore(root).read_paper(PAPER)

    assert record.tex == TEX_BYTES
    assert record.manifest.version == "v1"
    assert record.manifest.status is PaperStatus.SAVED
    assert record.manifest.tex_sha256 == tex_sha


def test_manifest_with_missing_blob_is_reported_broken(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest(tex_sha256=_sha(TEX_BYTES)))

    with pytest.raises(PaperBrokenError, match=r"tex blob .* is missing"):
        PaperStore(root).read_paper(PAPER)


def test_blob_whose_bytes_do_not_match_its_name_is_reported_broken(tmp_path: Path) -> None:
    tex_sha = _sha(TEX_BYTES)
    path = tmp_path / "blobs" / tex_sha[:2] / tex_sha
    path.parent.mkdir(parents=True)
    path.write_bytes(b"tampered")
    root = _make_store(tmp_path, _manifest(tex_sha256=tex_sha))

    with pytest.raises(PaperBrokenError, match="hashes to"):
        PaperStore(root).read_paper(PAPER)


@pytest.mark.parametrize(
    "licence",
    [
        "https://creativecommons.org/licenses/by-nc/4.0",
        "http://creativecommons.org/licenses/by/4.0",
        "https://creativecommons.org/licenses/by/4.0/",
        "",
    ],
)
def test_non_allowed_licence_is_refused(tmp_path: Path, licence: str) -> None:
    tex_sha = _write_blob(tmp_path, TEX_BYTES)
    root = _make_store(tmp_path, _manifest(licence=licence, tex_sha256=tex_sha))

    with pytest.raises(PaperRestrictedError):
        PaperStore(root).read_paper(PAPER)


def test_restricted_paper_is_refused_before_its_blob_is_read(tmp_path: Path) -> None:
    root = _make_store(
        tmp_path,
        _manifest(
            licence="https://creativecommons.org/licenses/by-nc/4.0", status="skipped", tex_sha256=_sha(TEX_BYTES)
        ),
    )

    with pytest.raises(PaperRestrictedError):
        PaperStore(root).read_paper(PAPER)


def test_missing_latest_pointer_is_not_found(tmp_path: Path) -> None:
    (tmp_path / "papers" / PAPER).mkdir(parents=True)

    with pytest.raises(PaperNotFoundError):
        PaperStore(tmp_path).read_manifest(PAPER)


def test_manifest_field_with_wrong_type_is_broken(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest(title=42))

    with pytest.raises(PaperBrokenError, match="'title' must be a string"):
        PaperStore(root).read_manifest(PAPER)


def test_manifest_version_must_match_file_name(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest(version="v2"), file_name="v1.json")

    with pytest.raises(PaperBrokenError, match="does not match the file name"):
        PaperStore(root).read_manifest(PAPER)


@pytest.mark.parametrize("arxiv_id", ["../etc", "2610.23820v1", "2610/23820", ""])
def test_arxiv_id_that_is_not_a_plain_id_is_rejected(tmp_path: Path, arxiv_id: str) -> None:
    with pytest.raises(ValueError, match="arXiv ID"):
        PaperStore(tmp_path).read_manifest(arxiv_id)


def test_topic_lists_its_papers(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest(arxiv_id="2610.00001", version="v1"), file_name="v1.json")
    _make_store(root, _manifest(arxiv_id="2610.00002"))
    _add_membership(
        root,
        {"topic": "alpha", "arxiv_id": "2610.00001", "query": "q", "added_at": "2026-10-20T00:00:00Z"},
        {"topic": "beta", "arxiv_id": "2610.00002", "query": "q", "added_at": "2026-10-20T00:00:00Z"},
    )

    assert PaperStore(root).list_papers("alpha") == ["2610.00001"]
    assert PaperStore(root).list_papers("beta") == ["2610.00002"]
    assert PaperStore(root).list_papers("gamma") == []


def test_paper_in_two_topics_appears_under_both(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest())
    _add_membership(
        root,
        {"topic": "alpha", "arxiv_id": PAPER, "query": "q1", "added_at": "2026-10-20T00:00:00Z"},
        {"topic": "beta", "arxiv_id": PAPER, "query": "q2", "added_at": "2026-10-20T00:00:00Z"},
    )
    store = PaperStore(root)

    assert store.list_papers("alpha") == [PAPER]
    assert store.list_papers("beta") == [PAPER]


def test_membership_line_for_missing_paper_is_broken(tmp_path: Path) -> None:
    root = _make_store(tmp_path, _manifest())
    _add_membership(
        root, {"topic": "alpha", "arxiv_id": "2610.99999", "query": "q", "added_at": "2026-10-20T00:00:00Z"}
    )

    with pytest.raises(PaperBrokenError, match=re.escape("2610.99999")):
        PaperStore(root).list_papers("alpha")


def test_missing_membership_file_means_no_topics(tmp_path: Path) -> None:
    assert PaperStore(tmp_path).list_papers("anything") == []


def test_store_root_must_be_a_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a directory"):
        PaperStore(tmp_path / "absent")
