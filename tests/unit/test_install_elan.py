"""The elan installer must refuse anything it cannot verify. These tests cover those refusals without the network."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
import tarfile
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def installer(request: pytest.FixtureRequest) -> ModuleType:
    script = Path(request.config.rootpath) / "scripts" / "install_elan.py"
    spec = importlib.util.spec_from_file_location("install_elan", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_the_asset_for_this_platform_is_chosen(installer: ModuleType) -> None:
    assert installer.asset_name_for("Linux", "x86_64") == "elan-x86_64-unknown-linux-gnu.tar.gz"
    assert installer.asset_name_for("Darwin", "arm64") == "elan-aarch64-apple-darwin.tar.gz"


def test_an_unsupported_platform_is_refused(installer: ModuleType) -> None:
    with pytest.raises(installer.InstallError, match="no elan build"):
        installer.asset_name_for("Plan9", "mips")


def test_the_published_digest_is_read(installer: ModuleType) -> None:
    release = {"assets": [{"name": "elan-x.tar.gz", "digest": "sha256:" + "ab" * 32}]}

    assert installer.published_digest(release, "elan-x.tar.gz") == "ab" * 32


def test_an_asset_without_a_digest_is_refused_rather_than_trusted(installer: ModuleType) -> None:
    release = {"assets": [{"name": "elan-x.tar.gz", "digest": None}]}

    with pytest.raises(installer.InstallError, match="no sha256 digest"):
        installer.published_digest(release, "elan-x.tar.gz")


def test_a_missing_asset_is_refused(installer: ModuleType) -> None:
    with pytest.raises(installer.InstallError, match="no asset named"):
        installer.published_digest({"assets": []}, "elan-x.tar.gz")


def test_a_matching_digest_passes_and_a_changed_archive_fails(installer: ModuleType, tmp_path: Path) -> None:
    archive = tmp_path / "elan.tar.gz"
    archive.write_bytes(b"genuine bytes")
    good = hashlib.sha256(b"genuine bytes").hexdigest()

    installer.check_digest(archive, good)
    archive.write_bytes(b"tampered bytes")
    with pytest.raises(installer.InstallError, match="SHA-256 mismatch"):
        installer.check_digest(archive, good)


def _tarball(members: list[tuple[str, bytes | None, str | None]]) -> bytes:
    """Build a tar.gz. A member with data None is a link to `link_target`."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, data, link_target in members:
            info = tarfile.TarInfo(name)
            if data is None:
                info.type = tarfile.SYMTYPE
                info.linkname = link_target or ""
                tar.addfile(info)
            else:
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def test_a_normal_archive_extracts(installer: ModuleType, tmp_path: Path) -> None:
    archive = tmp_path / "ok.tar.gz"
    archive.write_bytes(_tarball([("elan-init", b"#!/bin/sh\n", None)]))
    dest = tmp_path / "out"
    dest.mkdir()

    installer.extract_safely(archive, dest)

    assert (dest / "elan-init").read_bytes() == b"#!/bin/sh\n"


def test_an_archive_that_escapes_its_folder_is_refused(installer: ModuleType, tmp_path: Path) -> None:
    archive = tmp_path / "evil.tar.gz"
    archive.write_bytes(_tarball([("../escape.txt", b"x", None)]))
    dest = tmp_path / "out"
    dest.mkdir()

    with pytest.raises(installer.InstallError, match="escapes"):
        installer.extract_safely(archive, dest)
    assert not (tmp_path / "escape.txt").exists()


def test_an_archive_with_a_link_is_refused(installer: ModuleType, tmp_path: Path) -> None:
    archive = tmp_path / "link.tar.gz"
    archive.write_bytes(_tarball([("elan-init", None, "/etc/passwd")]))
    dest = tmp_path / "out"
    dest.mkdir()

    with pytest.raises(installer.InstallError, match="link"):
        installer.extract_safely(archive, dest)
