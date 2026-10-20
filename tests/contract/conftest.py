"""Contract test configuration.

Every test under tests/contract/ gets the `integration` marker at collection
time, so `pytest -m integration` selects this folder. Contract tests check
artifacts against schemas owned by a sibling repo (equations-history), so they
require that checkout and are not part of the CI-safe unit tier.
"""

from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

CONTRACT_DIR = REPO_ROOT / "tests" / "contract"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every collected test that lives under tests/contract/."""
    for item in items:
        if Path(item.path).is_relative_to(CONTRACT_DIR):
            item.add_marker(pytest.mark.integration)
