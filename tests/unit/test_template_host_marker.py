"""A unit test that reads the repo's templates/ must carry the host marker, because templates are not in the image."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

UNIT_DIR = REPO_ROOT / "tests" / "unit"
READS_REPO_TEMPLATES = re.compile(r'REPO_ROOT\s*/\s*"templates"')
HOST_PYTESTMARK = re.compile(r"^pytestmark\s*=\s*pytest\.mark\.host\b", re.MULTILINE)


def _unit_files_reading_repo_templates() -> list[Path]:
    return sorted(path for path in UNIT_DIR.glob("test_*.py") if READS_REPO_TEMPLATES.search(path.read_text("utf-8")))


def test_the_unit_tier_finds_the_template_readers() -> None:
    """The scan must see the known template readers, or the rule below would pass vacuously."""
    names = {path.name for path in _unit_files_reading_repo_templates()}
    assert {"test_gnns_model.py", "test_thermodynamics_model.py", "test_template_consistency.py"} <= names


@pytest.mark.parametrize("path", _unit_files_reading_repo_templates(), ids=lambda path: path.name)
def test_a_unit_test_reading_repo_templates_is_marked_host(path: Path) -> None:
    """Template reads depend on the host checkout, so the file opts into the host tier rather than running as unit."""
    assert HOST_PYTESTMARK.search(path.read_text("utf-8")), (
        f"{path.name} reads REPO_ROOT/'templates' and needs pytestmark = pytest.mark.host"
    )
