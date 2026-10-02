"""Centralized logging configuration for math-trace.

Provides consistent logging setup across all modules.
"""

import logging
from pathlib import Path

from .constants import LOG_FORMAT, LOG_LEVEL

# Cache directory for logs
LOG_DIR: Path = Path.home() / ".math-trace" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already done
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

        # File handler (optional, for debugging)
        file_handler = logging.FileHandler(LOG_DIR / f"{name.replace('.', '_')}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    return logger
