"""Pure Python services for paper ingestion and presentation generation.

Public API preserved for existing imports.
"""

from .builder import PresentationBuilder
from .downloader import PaperDownloader
from .extractor import ExtractedEquation, FormulaExtractor, PaperMetadata

__all__ = [
    "ExtractedEquation",
    "FormulaExtractor",
    "PaperDownloader",
    "PaperMetadata",
    "PresentationBuilder",
]
