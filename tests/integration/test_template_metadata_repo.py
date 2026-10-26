"""The equation-metadata guard passes on every template in this repository."""

from math_trace.constants import REPO_ROOT
from math_trace.template_metadata import check_all


def test_every_template_follows_the_metadata_pattern():
    problems = check_all(REPO_ROOT / "templates")

    assert [p.render() for p in problems] == []
