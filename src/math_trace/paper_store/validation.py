"""Validation and parsing for paper store manifests and membership lines."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    ARXIV_ID_PATTERN,
    SCHEMA_VERSION,
    SHA256_PATTERN,
    Membership,
    PaperBrokenError,
    PaperManifest,
    PaperStatus,
    PaperStoreError,
)


def check_sha256(value: str) -> None:
    """Reject anything that is not a lowercase hex sha256, so a bad value never becomes a path."""
    if not SHA256_PATTERN.fullmatch(value):
        raise PaperStoreError(f"not a sha256 hex digest: {value!r}")


def check_arxiv_id(value: str) -> None:
    """Reject anything that is not a new-style arXiv ID without version, so a bad value never becomes a path."""
    if not ARXIV_ID_PATTERN.fullmatch(value):
        raise PaperStoreError(f"not an arXiv ID without version (e.g. 2610.23820): {value!r}")


def _text(data: dict[str, Any], key: str, where: Path) -> str:
    """Return data[key], which must be a string, else raise PaperBrokenError."""
    if key not in data:
        raise PaperBrokenError(f"{where}: field {key!r} is missing")
    value = data[key]
    if not isinstance(value, str):
        raise PaperBrokenError(f"{where}: field {key!r} must be a string, got {type(value).__name__}")
    return value


def _text_or_null(data: dict[str, Any], key: str, where: Path) -> str | None:
    """Return data[key], which must be a string or null, else raise PaperBrokenError."""
    if key not in data:
        raise PaperBrokenError(f"{where}: field {key!r} is missing")
    value = data[key]
    if value is None or isinstance(value, str):
        return value
    raise PaperBrokenError(f"{where}: field {key!r} must be a string or null, got {type(value).__name__}")


def parse_manifest(raw: object, *, arxiv_id: str, file_name: str, where: Path) -> PaperManifest:
    """Validate a decoded manifest against the contract's field table and build a PaperManifest."""
    if not isinstance(raw, dict):
        raise PaperBrokenError(f"{where}: manifest must be a JSON object")
    schema_version = raw.get("schema_version")
    if type(schema_version) is not int or schema_version != SCHEMA_VERSION:
        raise PaperBrokenError(f"{where}: schema_version must be {SCHEMA_VERSION}, got {schema_version!r}")
    manifest_arxiv_id = _text(raw, "arxiv_id", where)
    if manifest_arxiv_id != arxiv_id:
        raise PaperBrokenError(f"{where}: arxiv_id {manifest_arxiv_id!r} does not match directory {arxiv_id!r}")
    version = _text(raw, "version", where)
    if f"{version}.json" != file_name:
        raise PaperBrokenError(f"{where}: version {version!r} does not match the file name {file_name!r}")
    title = _text(raw, "title", where)
    doi = _text_or_null(raw, "doi", where)
    licence = _text(raw, "licence", where)
    pdf_sha256 = _text_or_null(raw, "pdf_sha256", where)
    tex_sha256 = _text_or_null(raw, "tex_sha256", where)
    for key, sha in (("pdf_sha256", pdf_sha256), ("tex_sha256", tex_sha256)):
        if sha is not None and not SHA256_PATTERN.fullmatch(sha):
            raise PaperBrokenError(f"{where}: field {key!r} is not a sha256 hex digest")
    status_text = _text(raw, "status", where)
    try:
        status = PaperStatus(status_text)
    except ValueError as exc:
        allowed = ", ".join(s.value for s in PaperStatus)
        raise PaperBrokenError(f"{where}: status {status_text!r} is not one of {allowed}") from exc
    fetched_at = _text(raw, "fetched_at", where)
    try:
        datetime.fromisoformat(fetched_at)
    except ValueError as exc:
        raise PaperBrokenError(f"{where}: fetched_at {fetched_at!r} is not ISO 8601") from exc
    return PaperManifest(
        schema_version=SCHEMA_VERSION,
        arxiv_id=arxiv_id,
        version=version,
        title=title,
        doi=doi,
        licence=licence,
        pdf_sha256=pdf_sha256,
        tex_sha256=tex_sha256,
        status=status,
        fetched_at=fetched_at,
    )


def parse_membership(line: str, number: int, where: Path) -> Membership:
    """Decode one membership line, or raise PaperBrokenError with its line number."""
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        raise PaperBrokenError(f"{where}:{number}: line is not JSON ({exc})") from exc
    if not isinstance(raw, dict):
        raise PaperBrokenError(f"{where}:{number}: line must be a JSON object")
    fields: dict[str, str] = {}
    for key in ("topic", "arxiv_id", "query", "added_at"):
        value = _text(raw, key, where)
        if not value:
            raise PaperBrokenError(f"{where}:{number}: field {key!r} is empty")
        fields[key] = value
    if not ARXIV_ID_PATTERN.fullmatch(fields["arxiv_id"]):
        raise PaperBrokenError(f"{where}:{number}: arxiv_id {fields['arxiv_id']!r} is not an arXiv ID")
    return Membership(
        topic=fields["topic"],
        arxiv_id=fields["arxiv_id"],
        query=fields["query"],
        added_at=fields["added_at"],
    )
