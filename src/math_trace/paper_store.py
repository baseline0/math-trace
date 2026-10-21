"""Read the paper store v1 under the format in fleet-coordination/contracts/paper-store/FORMAT.md.

The store is written by tool-lit-review. This module reads it and never imports tool_lit_review: the on-disk
layout, the manifest fields and the membership lines are the only interface. The store root is a parameter, never a
constant. The licence rule is applied again here as a second check, so a restricted paper's TeX is never returned
even if a writer let its manifest through.

Every lookup is by arXiv ID without a version suffix. A manifest that names a blob which is not on disk, or whose
bytes do not hash to the name they are stored under, is reported as PaperBrokenError. Nothing is guessed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

SCHEMA_VERSION: Final = 1
PAPERS_DIRNAME: Final = "papers"
BLOBS_DIRNAME: Final = "blobs"
CATALOG_DIRNAME: Final = "catalog"
LATEST_NAME: Final = "latest"
MEMBERSHIP_NAME: Final = "membership.jsonl"

ARXIV_ID_PATTERN: Final = re.compile(r"\d{4}\.\d{4,5}")
MANIFEST_NAME_PATTERN: Final = re.compile(r"v\d+\.json")
SHA256_PATTERN: Final = re.compile(r"[0-9a-f]{64}")

# The only licences a reader may treat as open. Exact canonical URLs, as the contract lists them. Anything else,
# including a missing licence, is restricted.
ALLOWED_LICENCES: Final[frozenset[str]] = frozenset(
    {
        "https://creativecommons.org/licenses/by/4.0",
        "https://creativecommons.org/licenses/by-sa/4.0",
        "https://creativecommons.org/publicdomain/zero/1.0",
    }
)


class PaperStatus(StrEnum):
    """The finite set of manifest statuses the contract defines."""

    SAVED = "saved"
    CACHED = "cached"
    SKIPPED = "skipped"
    FAILED = "failed"


class PaperStoreError(ValueError):
    """Base error for a store read that cannot be completed."""


class PaperNotFoundError(PaperStoreError):
    """The store has no `papers/<arxiv-id>/latest` pointer for the requested paper."""


class PaperRestrictedError(PaperStoreError):
    """The paper's licence is not on the contract's allowed list, so its content may not be read."""


class PaperBrokenError(PaperStoreError):
    """The store is inconsistent: a manifest is malformed, or a blob it names is missing or corrupt."""


@dataclass(frozen=True, slots=True)
class PaperManifest:
    """One immutable manifest, field for field as the contract's table lists them."""

    schema_version: int
    arxiv_id: str
    version: str
    title: str
    doi: str | None
    licence: str
    pdf_sha256: str | None
    tex_sha256: str | None
    status: PaperStatus
    fetched_at: str


@dataclass(frozen=True, slots=True)
class PaperRecord:
    """A paper whose licence is open and whose referenced blobs are present and verified.

    `tex` is the TeX bundle bytes, or None when the manifest has no `tex_sha256`.
    """

    manifest: PaperManifest
    tex: bytes | None


@dataclass(frozen=True, slots=True)
class Membership:
    """One line of `catalog/membership.jsonl`: a paper found under a topic by a query."""

    topic: str
    arxiv_id: str
    query: str
    added_at: str


class PaperStore:
    """A read-only view of a paper store rooted at `root`."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        if not self.root.is_dir():
            raise PaperStoreError(f"paper store root is not a directory: {self.root}")

    def get_blob(self, sha256: str) -> bytes:
        """Return the bytes stored under `sha256`, after checking they hash to that name."""
        _check_sha256(sha256)
        path = self.blob_path(sha256)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise PaperBrokenError(f"blob {sha256} is missing: {path}") from exc
        except OSError as exc:
            raise PaperBrokenError(f"blob {sha256} is not readable: {path} ({exc})") from exc
        actual = hashlib.sha256(data).hexdigest()
        if actual != sha256:
            raise PaperBrokenError(f"blob {path} hashes to {actual}, not {sha256}")
        return data

    def has_blob(self, sha256: str) -> bool:
        """Return True when a blob named `sha256` is on disk. Does not verify its bytes."""
        _check_sha256(sha256)
        return self.blob_path(sha256).is_file()

    def blob_path(self, sha256: str) -> Path:
        """Return where the blob with this hash lives: `blobs/<sha[0:2]>/<sha>`."""
        _check_sha256(sha256)
        return self.root / BLOBS_DIRNAME / sha256[:2] / sha256

    def read_manifest(self, arxiv_id: str) -> PaperManifest:
        """Read `papers/<arxiv-id>/latest`, then the manifest it names, and validate every field."""
        _check_arxiv_id(arxiv_id)
        paper_dir = self.root / PAPERS_DIRNAME / arxiv_id
        latest = paper_dir / LATEST_NAME
        try:
            pointer = latest.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise PaperNotFoundError(f"no latest pointer for {arxiv_id}: {latest}") from exc
        except (OSError, UnicodeDecodeError) as exc:
            raise PaperBrokenError(f"latest pointer is not readable: {latest} ({exc})") from exc
        if not MANIFEST_NAME_PATTERN.fullmatch(pointer):
            raise PaperBrokenError(f"{latest} names {pointer!r}, which is not a manifest file name")

        manifest_path = paper_dir / pointer
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise PaperBrokenError(f"{latest} names a manifest that is missing: {manifest_path}") from exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PaperBrokenError(f"manifest is not readable JSON: {manifest_path} ({exc})") from exc
        return _parse_manifest(raw, arxiv_id=arxiv_id, file_name=pointer, where=manifest_path)

    def read_paper(self, arxiv_id: str) -> PaperRecord:
        """Return the paper's manifest and TeX bytes, refusing restricted licences and broken blobs.

        Order: the licence gate runs first, so a restricted paper never reaches blob access. Then every blob the
        manifest names must be present, and the TeX bundle's bytes are verified against its hash.
        """
        manifest = self.read_manifest(arxiv_id)
        if manifest.licence not in ALLOWED_LICENCES:
            raise PaperRestrictedError(
                f"{arxiv_id} {manifest.version}: licence {manifest.licence!r} is not on the allowed list"
            )
        for label, sha in (("pdf", manifest.pdf_sha256), ("tex", manifest.tex_sha256)):
            if sha is not None and not self.has_blob(sha):
                raise PaperBrokenError(f"{arxiv_id} {manifest.version}: {label} blob {sha} is missing")
        tex = self.get_blob(manifest.tex_sha256) if manifest.tex_sha256 is not None else None
        return PaperRecord(manifest=manifest, tex=tex)

    def read_memberships(self) -> list[Membership]:
        """Return every line of `catalog/membership.jsonl`. A missing file means no topics yet."""
        path = self.root / CATALOG_DIRNAME / MEMBERSHIP_NAME
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            raise PaperBrokenError(f"membership file is not readable: {path} ({exc})") from exc
        return [_parse_membership(line, number, path) for number, line in enumerate(lines, start=1)]

    def list_papers(self, topic: str) -> list[str]:
        """Return the arXiv IDs filed under `topic`, in file order, each once.

        A membership line whose paper has no `papers/<arxiv-id>/` directory is reported as broken.
        """
        ids: list[str] = []
        for membership in self.read_memberships():
            if membership.topic != topic or membership.arxiv_id in ids:
                continue
            paper_dir = self.root / PAPERS_DIRNAME / membership.arxiv_id
            if not paper_dir.is_dir():
                raise PaperBrokenError(
                    f"topic {topic!r} lists {membership.arxiv_id}, which has no {paper_dir} directory"
                )
            ids.append(membership.arxiv_id)
        return ids


def _check_sha256(value: str) -> None:
    """Reject anything that is not a lowercase hex sha256, so a bad value never becomes a path."""
    if not SHA256_PATTERN.fullmatch(value):
        raise PaperStoreError(f"not a sha256 hex digest: {value!r}")


def _check_arxiv_id(value: str) -> None:
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


def _parse_manifest(raw: object, *, arxiv_id: str, file_name: str, where: Path) -> PaperManifest:
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


def _parse_membership(line: str, number: int, where: Path) -> Membership:
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
