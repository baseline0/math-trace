"""End-to-end test configuration.

Every test under tests/e2e/ gets the `e2e` marker at collection time, so
`pytest -m e2e` selects this folder. Without it these tests belong to no tier,
and neither `pytest -m unit` nor `pytest -m integration` would select them.
"""

from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

E2E_DIR = REPO_ROOT / "tests" / "e2e"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every collected test that lives under tests/e2e/."""
    for item in items:
        if Path(item.path).is_relative_to(E2E_DIR):
            item.add_marker(pytest.mark.e2e)
