"""Types, constants, and errors for the paper store contract.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Schema version is 1; manifest/status/allowed-licence sets are fixed by contract | paper-store FORMAT contract | `SCHEMA_VERSION`, `PaperStatus`, `ALLOWED_LICENCES`; `tests/unit/test_paper_store.py::test_reads_manifest_and_tex_blob`, `test_non_allowed_licence_is_refused` |
| Only exact canonical open licences are allowed; anything else is restricted | paper-store FORMAT contract | `ALLOWED_LICENCES`; `tests/unit/test_paper_store.py::test_non_allowed_licence_is_refused`, `test_restricted_paper_is_refused_before_its_blob_is_read` |
| Error types distinguish not-found, restricted, and broken store states | paper-store FORMAT contract | `PaperStoreError`, `PaperNotFoundError`, `PaperRestrictedError`, `PaperBrokenError`; `tests/unit/test_paper_store.py::test_missing_latest_pointer_is_not_found`, `test_non_allowed_licence_is_refused`, `test_manifest_with_missing_blob_is_reported_broken` |
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

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
