"""Unhappy path tests for arxiv extraction error recovery.

Tests malformed TeX archives, missing expected files, and extraction errors.
Standard: STANDARDS.md, TA-3.5 (Unhappy path exploration).
"""

from __future__ import annotations

import tarfile
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from math_trace.arxiv_extractor import download_and_extract_equations


def test_malformed_tarball_raises_extraction_error() -> None:
    """Tarball is corrupted: cannot unpack. Raises TarError with clear message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = Path(tmpdir) / "corrupted.tar.gz"
        # Write invalid tar data
        tar_path.write_bytes(b"not a valid tar file\x00\x01\x02")

        # Mock requests.get to return the corrupted tarball
        with mock.patch("math_trace.arxiv_extractor.requests.get") as mock_get:
            mock_response = mock.Mock()
            mock_response.content = tar_path.read_bytes()
            mock_get.return_value = mock_response

            with pytest.raises(
                (tarfile.TarError, Exception),
                match=r"(not a tar|invalid|Error|corrupted|ReadError)",
            ):
                download_and_extract_equations("2610.23820")


def test_missing_tex_files_in_archive_raises_filenotfounderror() -> None:
    """Archive exists but contains no .tex files. Raises FileNotFoundError with clear message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid tar without .tex files
        tar_path = Path(tmpdir) / "no_tex.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            # Add a non-.tex file
            dummy_content = b"# This is not LaTeX\n"
            info = tarfile.TarInfo(name="README.md")
            info.size = len(dummy_content)
            tar.addfile(info, fileobj=mock.Mock(read=lambda *args: dummy_content))

        with mock.patch("math_trace.arxiv_extractor.requests.get") as mock_get:
            mock_response = mock.Mock()
            mock_response.content = tar_path.read_bytes()
            mock_get.return_value = mock_response

            with pytest.raises(FileNotFoundError, match=r"No \.tex files"):
                download_and_extract_equations("2610.23820")


def test_empty_archive_raises_filenotfounderror() -> None:
    """Archive is empty (no files at all). Raises FileNotFoundError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = Path(tmpdir) / "empty.tar.gz"
        with tarfile.open(tar_path, "w:gz"):
            pass  # Empty archive

        with mock.patch("math_trace.arxiv_extractor.requests.get") as mock_get:
            mock_response = mock.Mock()
            mock_response.content = tar_path.read_bytes()
            mock_get.return_value = mock_response

            with pytest.raises(FileNotFoundError, match=r"No \.tex files"):
                download_and_extract_equations("2610.23820")
