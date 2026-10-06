"""Unit test configuration.

All tests in this directory are marked as @pytest.mark.unit.
No external services, network calls, or sibling repos required.
"""

import pytest


def pytest_configure(config):
    """Apply unit marker to all tests in this directory."""
    config.addinivalue_line("markers", "unit: deterministic test with no external dependencies")


@pytest.fixture(scope="session", autouse=True)
def _mark_unit_tests(request):
    """Auto-mark all tests in unit/ as @pytest.mark.unit."""
    for item in request.session.items:
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
