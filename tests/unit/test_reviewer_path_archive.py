"""The reviewer path must work from a clean export of the committed tree, not only from a working copy.

The archive is `git archive HEAD`, so it holds exactly what a reviewer clones: no generated outputs, no local
state. These checks run in CI. The full build is in tests/integration/test_reviewer_path_full.py.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from math_trace import reference_check as rc
from math_trace.constants import REPO_ROOT

pytestmark = pytest.mark.unit

REPO = REPO_ROOT


@pytest.fixture(scope="module")
def archive(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The committed tree, exported with git archive into a folder of its own."""
    target = tmp_path_factory.mktemp("reviewer-archive")
    listing = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", "HEAD"],
        capture_output=True,
        check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(listing)) as tar:
        tar.extractall(target, filter="data")
    return target


@pytest.mark.parametrize("name", sorted(rc.REFERENCES))
def test_each_registered_reference_is_complete_in_the_archive(archive: Path, name: str) -> None:
    reference = rc.REFERENCES[name]

    assert rc.missing_required(reference, archive) == []
    for test_file in reference.contract_tests:
        assert (archive / test_file).is_file(), f"contract test missing from the archive: {test_file}"


@pytest.mark.parametrize("name", sorted(rc.REFERENCES))
def test_each_build_command_names_a_script_in_the_archive(archive: Path, name: str) -> None:
    reference = rc.REFERENCES[name]

    for argv in reference.build:
        scripts = [part for part in argv if part.endswith(".py")]
        assert scripts, f"build step has no script: {argv}"
        for script in scripts:
            assert (archive / reference.directory / script).is_file(), f"missing build script: {script}"


def test_the_reviewer_recipe_is_committed(archive: Path) -> None:
    justfile = (archive / "justfile").read_text(encoding="utf-8")

    assert "reference-check reference=" in justfile
    assert "math_trace.reference_check" in justfile


def test_the_reviewer_command_loads_from_the_archive(archive: Path) -> None:
    """Import the module from the exported tree, so the check sees what the reviewer's clone would."""
    env = {**os.environ, "PYTHONPATH": str(archive / "src")}
    done = subprocess.run(
        [sys.executable, "-c", "import math_trace.reference_check as m; print(m.__file__)"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(archive))
