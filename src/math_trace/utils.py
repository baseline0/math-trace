"""Shared utilities for math-trace.

Centralizes common operations to avoid duplication:
- Path handling (cache directories, file creation)
- JSON/YAML serialization with proper error handling
- Safe imports with fallbacks
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import CACHE_DIR
from .logging import get_logger

logger = get_logger(__name__)


def ensure_cache_dir(paper_id: str | None = None) -> Path:
    """Ensure cache directory exists.

    Args:
        paper_id: Optional paper ID to create subdirectory for

    Returns:
        Path to cache directory (or paper subdirectory if paper_id provided)

    Raises:
        OSError: If directory creation fails
    """
    cache_path = CACHE_DIR / "papers" / paper_id if paper_id else CACHE_DIR

    try:
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    except OSError as e:
        logger.error(f"Failed to create cache directory {cache_path}: {e}")
        raise


def safe_json_load(file_path: Path) -> dict | None:
    """Safely load JSON from file with error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON dict, or None if loading fails

    Logs errors without raising (graceful degradation).
    """
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.debug(f"JSON file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except OSError as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None


def safe_json_dump(data: Any, file_path: Path, indent: int = 2) -> bool:
    """Safely write JSON to file with error handling.

    Args:
        data: Object to serialize
        file_path: Path to write to
        indent: JSON indentation level

    Returns:
        True if write succeeded, False otherwise

    Logs errors without raising.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=indent), encoding="utf-8")
        return True
    except (TypeError, ValueError) as e:
        logger.error(f"Cannot serialize data for {file_path}: {e}")
        return False
    except OSError as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


def safe_import(module_name: str, fallback: Any = None) -> Any:
    """Safely import a module with graceful fallback.

    Args:
        module_name: Full module name (e.g., "typst")
        fallback: Value to return if import fails

    Returns:
        Imported module, or fallback value if import fails

    Logs warning if import fails.
    """
    try:
        return __import__(module_name, fromlist=[""])
    except ImportError:
        logger.warning(f"Optional dependency not available: {module_name}")
        return fallback


def format_latex_preview(latex: str, max_length: int = 50) -> str:
    """Format LaTeX string for UI preview.

    Args:
        latex: LaTeX expression
        max_length: Maximum length before truncating

    Returns:
        Formatted preview string (truncated if needed)
    """
    if not latex:
        return "(empty)"

    # Remove common LaTeX delimiters for cleaner display
    preview = latex.strip()
    for delim in ["$", "$$", "\\(", "\\)", "\\[", "\\]"]:
        preview = preview.replace(delim, "")

    preview = preview.strip()

    if len(preview) > max_length:
        return preview[:max_length] + "…"

    return preview
