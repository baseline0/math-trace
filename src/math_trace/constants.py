"""Central configuration and constants for math-trace.

This module centralizes all hardcoded paths, names, and magic values
to reduce duplication and make configuration changes easier.
"""

from pathlib import Path

# Cache directory for arXiv papers and extracted equations
CACHE_DIR: Path = Path.home() / ".math-trace" / "arxiv-cache"
EQUATIONS_SUBDIR: str = "equations"
METADATA_FILE: str = "metadata.json"
EQUATIONS_FILE: str = "equations.jsonl"

# Formula naming conventions
FORMULA_NAME_PREFIX: str = "eq"
DEFAULT_LATEX_DELIMITER: str = "$"

# Presentation defaults
DEFAULT_PRESENTATION_FORMAT: str = "talk"
DEFAULT_SLIDE_THEME: str = "default"

# Typing/conversion defaults
MAX_EQUATIONS_PER_PAPER: int = 100
CONVERSION_TIMEOUT_SECONDS: int = 30

# API response constants
API_STATUS_SUCCESS: str = "success"
API_STATUS_ERROR: str = "error"

# File search patterns
ARXIV_PAPER_GLOB: str = "examples/*/model.py"
LOCAL_MODEL_PATTERN: str = "model.py"

# Error messages
ERROR_ARXIV_INVALID_ID: str = "Invalid arXiv ID format"
ERROR_EXTRACTION_FAILED: str = "Failed to extract equations from paper"
ERROR_CACHE_NOT_FOUND: str = "Paper not found in cache"
ERROR_CONVERSION_FAILED: str = "Failed to convert LaTeX to SymPy"
ERROR_PATTERN_NOT_FOUND: str = "No model files matching pattern"

# Logging configuration
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
