"""Read-only paper store implementation.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Store root must be a directory; reads are read-only | paper-store FORMAT contract | `PaperStore.__init__`; `tests/unit/test_paper_store.py::test_store_root_must_be_a_directory` |
| `get_blob` verifies bytes hash to requested sha256; missing/corrupt blobs are broken | paper-store FORMAT contract | `PaperStore.get_blob`; `tests/unit/test_paper_store.py::test_blob_whose_bytes_do_not_match_its_name_is_reported_broken`, `test_manifest_with_missing_blob_is_reported_broken` |
| `read_manifest` resolves `latest` pointer, validates manifest name/file, parses and validates fields | paper-store FORMAT contract | `PaperStore.read_manifest`; `tests/unit/test_paper_store.py::test_reads_manifest_and_tex_blob`, `test_missing_latest_pointer_is_not_found`, `test_manifest_version_must_match_file_name`, `test_latest_pointer_with_bad_name_is_broken`, `test_latest_pointer_naming_missing_manifest_is_broken` |
| `read_paper` checks licence before blob access, requires named blobs present, returns verified TeX bytes | paper-store FORMAT contract | `PaperStore.read_paper`; `tests/unit/test_paper_store.py::test_non_allowed_licence_is_refused`, `test_restricted_paper_is_refused_before_its_blob_is_read`, `test_manifest_with_missing_blob_is_reported_broken` |
| Missing membership file means no topics; membership lines validated; listed paper dir must exist | paper-store FORMAT contract | `PaperStore.read_memberships`, `PaperStore.list_papers`; `tests/unit/test_paper_store.py::test_missing_membership_file_means_no_topics`, `test_topic_lists_its_papers`, `test_paper_in_two_topics_appears_under_both`, `test_membership_line_for_missing_paper_is_broken` |
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .types import (
    ALLOWED_LICENCES,
    BLOBS_DIRNAME,
    CATALOG_DIRNAME,
    LATEST_NAME,
    MANIFEST_NAME_PATTERN,
    MEMBERSHIP_NAME,
    PAPERS_DIRNAME,
    Membership,
    PaperBrokenError,
    PaperManifest,
    PaperNotFoundError,
    PaperRecord,
    PaperRestrictedError,
    PaperStoreError,
)
from .validation import check_arxiv_id, check_sha256, parse_manifest, parse_membership


class PaperStore:
    """A read-only view of a paper store rooted at `root`."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        if not self.root.is_dir():
            raise PaperStoreError(f"paper store root is not a directory: {self.root}")

    def get_blob(self, sha256: str) -> bytes:
        """Return the bytes stored under `sha256`, after checking they hash to that name."""
        check_sha256(sha256)
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
        check_sha256(sha256)
        return self.blob_path(sha256).is_file()

    def blob_path(self, sha256: str) -> Path:
        """Return where the blob with this hash lives: `blobs/<sha[0:2]>/<sha>`."""
        check_sha256(sha256)
        return self.root / BLOBS_DIRNAME / sha256[:2] / sha256

    def read_manifest(self, arxiv_id: str) -> PaperManifest:
        """Read `papers/<arxiv-id>/latest`, then the manifest it names, and validate every field."""
        check_arxiv_id(arxiv_id)
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
        return parse_manifest(raw, arxiv_id=arxiv_id, file_name=pointer, where=manifest_path)

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
        return [parse_membership(line, number, path) for number, line in enumerate(lines, start=1)]

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
