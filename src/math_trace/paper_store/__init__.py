"""Paper store v1 reader (fleet-coordination contracts/paper-store/FORMAT.md).

Public API preserved for callers and tests.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Store root must exist as a directory | paper-store FORMAT contract | `store.PaperStore.__init__`; `tests/unit/test_paper_store.py::test_store_root_must_be_a_directory` |
| Only canonical allowed licences are open; restricted papers are refused before blob access | paper-store FORMAT contract | `types.ALLOWED_LICENCES`, `store.PaperStore.read_paper`; `tests/unit/test_paper_store.py::test_non_allowed_licence_is_refused`, `test_restricted_paper_is_refused_before_its_blob_is_read` |
| Manifest identified by `papers/<arxiv-id>/latest` must exist, name a valid manifest, and match schema/field/version rules | paper-store FORMAT contract | `store.PaperStore.read_manifest`, `validation.parse_manifest`; `tests/unit/test_paper_store.py::test_reads_manifest_and_tex_blob`, `test_missing_latest_pointer_is_not_found`, `test_manifest_field_with_wrong_type_is_broken`, `test_manifest_version_must_match_file_name` |
| Blob bytes must exist and hash to their sha256 name; missing/corrupt blobs are broken | paper-store FORMAT contract | `store.PaperStore.get_blob/read_paper`; `tests/unit/test_paper_store.py::test_manifest_with_missing_blob_is_reported_broken`, `test_blob_whose_bytes_do_not_match_its_name_is_reported_broken` |
| Membership catalog is optional; missing file means no topics; bad/missing-member lines are broken | paper-store FORMAT contract | `store.PaperStore.read_memberships/list_papers`; `tests/unit/test_paper_store.py::test_topic_lists_its_papers`, `test_paper_in_two_topics_appears_under_both`, `test_membership_line_for_missing_paper_is_broken`, `test_missing_membership_file_means_no_topics` |
| arXiv ID/sha256 inputs are validated before use as paths | path-safety contract | `validation.check_arxiv_id/check_sha256`; `tests/unit/test_paper_store.py::test_arxiv_id_that_is_not_a_plain_id_is_rejected` |
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
