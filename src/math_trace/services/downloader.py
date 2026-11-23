"""Paper download service."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import ClassVar
from urllib.parse import urlparse
from urllib.request import urlopen


class PaperDownloader:
    """Download papers from various sources."""

    _DOWNLOAD_TIMEOUT_SECONDS = 30
    _ALLOWED_SCHEMES: ClassVar[set[str]] = {"http", "https"}

    @staticmethod
    def _parse_arxiv_url(url: str) -> str | None:
        """Convert arXiv page URL to PDF URL.

        Examples:
            https://arxiv.org/abs/2609.21904 → https://arxiv.org/pdf/2609.21904.pdf
            https://arxiv.org/pdf/2609.21904.pdf → https://arxiv.org/pdf/2609.21904.pdf
        """
        arxiv_pattern = r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)"
        match = re.search(arxiv_pattern, url)
        if match:
            arxiv_id = match.group(1)
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return None

    @staticmethod
    def _parse_pubmed_url(url: str) -> str | None:
        """Convert PubMed page URL to PDF URL (if available)."""
        # PubMed URLs typically don't have direct PDF links
        # Would need to scrape or use API
        return None

    @staticmethod
    def download(url: str, cache_dir: Path | None = None) -> Path:
        """Download paper PDF from URL.

        Supports:
        - arXiv URLs (abs or pdf)
        - PubMed URLs (experimental)
        - Direct PDF links

        Args:
            url: Paper URL or direct PDF link
            cache_dir: Directory to cache downloads (default: temp)

        Returns:
            Path to downloaded PDF

        Raises:
            ValueError: If URL format not recognized
            URLError: If download fails
        """
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "math-trace-papers"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Try to parse URL to get PDF link
        pdf_url = url
        if "arxiv.org" in url:
            parsed_url = PaperDownloader._parse_arxiv_url(url)
            if not parsed_url:
                raise ValueError(f"Cannot parse arXiv URL: {url}")
            pdf_url = parsed_url

        parsed_pdf_url = urlparse(pdf_url)
        if parsed_pdf_url.scheme not in PaperDownloader._ALLOWED_SCHEMES:
            raise ValueError(f"Unsupported URL scheme: {parsed_pdf_url.scheme or '<missing>'}")

        # Generate cache filename from URL
        cache_name = parsed_pdf_url.path.split("/")[-1]
        if not cache_name.endswith(".pdf"):
            cache_name = cache_name.replace("abs", "pdf") + ".pdf"
        cache_path = cache_dir / cache_name

        # Return cached if exists
        if cache_path.exists():
            return cache_path

        # Download
        with urlopen(pdf_url, timeout=PaperDownloader._DOWNLOAD_TIMEOUT_SECONDS) as response:
            cache_path.write_bytes(response.read())

        return cache_path
