"""Integration test configuration.

All tests in this directory are marked as @pytest.mark.integration.
May require sibling repos, local MCP servers, or cross-package contracts.
Skipped in CI; developers run locally before push with 'just test-integration'.
"""

import sys
from pathlib import Path

import pytest


def pytest_configure(config):
    """Setup path and apply integration marker to all tests in this directory."""
    # Add src/ to path for imports
    src_path = Path(__file__).parent.parent.parent / "src"
    sys.path.insert(0, str(src_path))

    config.addinivalue_line("markers", "integration: test requiring sibling repos or local setup")


@pytest.fixture(scope="session", autouse=True)
def _mark_integration_tests(request):
    """Auto-mark all tests in integration/ as @pytest.mark.integration."""
    for item in request.session.items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
