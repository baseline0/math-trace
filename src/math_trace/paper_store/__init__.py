"""Paper store v1 reader (fleet-coordination contracts/paper-store/FORMAT.md).

Public API preserved for callers and tests.
"""

from .store import PaperStore
from .types import (
    ALLOWED_LICENCES,
    ARXIV_ID_PATTERN,
    BLOBS_DIRNAME,
    CATALOG_DIRNAME,
    LATEST_NAME,
    MANIFEST_NAME_PATTERN,
    MEMBERSHIP_NAME,
    PAPERS_DIRNAME,
    SCHEMA_VERSION,
    SHA256_PATTERN,
    Membership,
    PaperBrokenError,
    PaperManifest,
    PaperNotFoundError,
    PaperRecord,
    PaperRestrictedError,
    PaperStatus,
    PaperStoreError,
)
from .validation import check_arxiv_id, check_sha256, parse_manifest, parse_membership

# Back-compat private names used by older code/tests (if any).
_check_sha256 = check_sha256
_check_arxiv_id = check_arxiv_id
_parse_manifest = parse_manifest
_parse_membership = parse_membership

__all__ = [
    "ALLOWED_LICENCES",
    "ARXIV_ID_PATTERN",
    "BLOBS_DIRNAME",
    "CATALOG_DIRNAME",
    "LATEST_NAME",
    "MANIFEST_NAME_PATTERN",
    "MEMBERSHIP_NAME",
    "PAPERS_DIRNAME",
    "SCHEMA_VERSION",
    "SHA256_PATTERN",
    "Membership",
    "PaperBrokenError",
    "PaperManifest",
    "PaperNotFoundError",
    "PaperRecord",
    "PaperRestrictedError",
    "PaperStatus",
    "PaperStore",
    "PaperStoreError",
    "_check_arxiv_id",
    "_check_sha256",
    "_parse_manifest",
    "_parse_membership",
    "check_arxiv_id",
    "check_sha256",
    "parse_manifest",
    "parse_membership",
]
