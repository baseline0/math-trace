"""Shared pytest configuration: each test gets its tier marker from its folder.

Tier folders are tests/unit, tests/integration, tests/contract, tests/host and tests/e2e. The marker comes from the
folder, so test files must not declare the tier marker themselves. Files outside a tier folder get no tier marker.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

TESTS_ROOT = REPO_ROOT / "tests"
DIRECTORY_MARKERS = {"unit": "unit", "integration": "integration", "contract": "contract", "host": "host", "e2e": "e2e"}


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Add the marker that matches each test's top-level tier folder."""
    for item in items:
        try:
            relative = Path(str(item.fspath)).resolve().relative_to(TESTS_ROOT)
        except ValueError:
            continue
        if relative.parts and relative.parts[0] in DIRECTORY_MARKERS:
            item.add_marker(getattr(pytest.mark, DIRECTORY_MARKERS[relative.parts[0]]))
