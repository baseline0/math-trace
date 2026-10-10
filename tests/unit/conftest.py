"""Unit test configuration.

Every test under tests/unit/ gets the `unit` marker at collection time, so
`pytest -m unit` selects this folder. Unit tests are deterministic and need no
external services, network access, or sibling repos.
"""

from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

UNIT_DIR = REPO_ROOT / "tests" / "unit"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every collected test that lives under tests/unit/."""
    for item in items:
        if Path(item.path).is_relative_to(UNIT_DIR):
            item.add_marker(pytest.mark.unit)
