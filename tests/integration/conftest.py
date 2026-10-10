"""Integration test configuration.

Every test under tests/integration/ gets the `integration` marker at collection
time, so `pytest -m integration` selects this folder. Integration tests may need
sibling repos, local MCP servers, or cross-package contracts.
"""

import sys
from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

INTEGRATION_DIR = REPO_ROOT / "tests" / "integration"
SRC_DIR = REPO_ROOT / "src"


def pytest_configure(config: pytest.Config) -> None:
    """Make the source tree importable for tests that import math_trace directly."""
    sys.path.insert(0, str(SRC_DIR))


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every collected test that lives under tests/integration/."""
    for item in items:
        if Path(item.path).is_relative_to(INTEGRATION_DIR):
            item.add_marker(pytest.mark.integration)
