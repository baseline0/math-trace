"""Load mined TeX sources for one paper, by path, under the DOWNSTREAM-TEX-001 contract.

tool-lit-review writes `papers/<topic>/tex/<paper_id>/manifest.json` beside a `src/` tree. This module reads
that manifest and the files it lists. It never imports tool_lit_review: the path and the manifest fields are the
only interface. The licence gate here is a second copy of the gate on purpose, so a bad manifest cannot pass both.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

SRC_DIRNAME = "src"
SAVED_STATUS = "saved"
TEX_SUFFIX = ".tex"

# Canonical licence URLs (https, no trailing slash) that a consumer will read. CC-BY-SA is pinned to 4.0.
ALLOWED_LICENCES: frozenset[str] = frozenset(
    {
        "https://creativecommons.org/licenses/by/4.0",
        "https://creativecommons.org/licenses/by-sa/4.0",
        "https://creativecommons.org/publicdomain/zero/1.0",
    }
)


class TexManifestError(ValueError):
    """A TeX manifest was refused: unreadable, not saved, unlicensed, malformed, or missing a listed file."""


def normalise_licence(url: str) -> str:
    """Return the canonical form of a licence URL for comparison with ALLOWED_LICENCES.

    Why: the manifest may carry http or a trailing slash for the same licence; both must compare equal.
    """
    cleaned = url.strip().lower()
    if cleaned.startswith("http://"):
        cleaned = "https://" + cleaned[len("http://") :]
    return cleaned.rstrip("/")


def _read_manifest(manifest_path: Path) -> dict[str, Any]:
    """Parse the manifest JSON object, or raise TexManifestError with the path in the message."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TexManifestError(f"{manifest_path}: manifest file does not exist") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise TexManifestError(f"{manifest_path}: manifest is not readable JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise TexManifestError(f"{manifest_path}: manifest must be a JSON object")
    return data


def load_tex_sources(manifest_path: Path) -> list[Path]:
    """Return the .tex source files a saved, allowed-licence manifest lists, as paths under its src/ tree.

    Refuses (TexManifestError) when the manifest is missing or malformed, when status is not "saved", when the
    licence is not in ALLOWED_LICENCES, when an extracted entry escapes src/, or when any listed file is missing.
    Checks run in that order, and no file is returned unless all of them pass.
    """
    manifest = _read_manifest(manifest_path)

    status = manifest.get("status")
    if status != SAVED_STATUS:
        raise TexManifestError(
            f"{manifest_path}: status is {status!r}, expected {SAVED_STATUS!r}; this bundle is not usable"
        )

    licence = manifest.get("licence")
    if not isinstance(licence, str) or normalise_licence(licence) not in ALLOWED_LICENCES:
        raise TexManifestError(
            f"{manifest_path}: licence {licence!r} is not on the allowed list ({', '.join(sorted(ALLOWED_LICENCES))})"
        )

    extracted = manifest.get("extracted")
    if not isinstance(extracted, list) or not all(isinstance(entry, str) for entry in extracted):
        raise TexManifestError(f"{manifest_path}: 'extracted' must be a list of path strings")

    src_root = manifest_path.parent / SRC_DIRNAME
    listed: list[Path] = []
    for entry in extracted:
        relative = PurePosixPath(entry)
        if relative.is_absolute() or ".." in relative.parts:
            raise TexManifestError(f"{manifest_path}: extracted entry {entry!r} escapes {SRC_DIRNAME}/")
        path = src_root.joinpath(*relative.parts)
        if not path.is_file():
            raise TexManifestError(f"{manifest_path}: listed file is missing: {path}")
        listed.append(path)

    return [path for path in listed if path.suffix == TEX_SUFFIX]
