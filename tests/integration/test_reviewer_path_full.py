"""The full reviewer path, run from a clean export of the committed tree. Slow (a minute or more), so it runs only
when asked: `MATH_TRACE_FULL_REVIEW=1 uv run pytest tests/integration/test_reviewer_path_full.py -m integration`.
"""

from __future__ import annotations

import io
import os
import subprocess
import tarfile
from pathlib import Path

import pytest

from math_trace import reference_check as rc
from math_trace.constants import REPO_ROOT

pytestmark = [
    pytest.mark.skipif(os.environ.get("MATH_TRACE_FULL_REVIEW") != "1", reason="set MATH_TRACE_FULL_REVIEW=1 to run"),
]

REPO = REPO_ROOT


def test_the_epidemiology_reference_passes_from_a_clean_export(tmp_path: Path) -> None:
    listing = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", "HEAD"], capture_output=True, check=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(listing)) as tar:
        tar.extractall(tmp_path, filter="data")

    result = rc.check("epidemiology-sir", tmp_path)

    assert result.result == "pass", result.failures
    assert result.deterministic
    assert result.tests_returncode == 0
