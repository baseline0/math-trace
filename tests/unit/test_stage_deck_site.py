"""The published deck site is the reviewed deck, the figures it links to, and .nojekyll, and nothing else.

Built from fake files under tmp_path, so the reviewed deck is never touched.
"""

import sys
from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import stage_deck_site as deck

HTML = (
    "<html><body>"
    '<img src="figures/sir_trajectory.png">'
    '<img src="figures/r0_comparison.png">'
    '<a href="https://arxiv.org/abs/1">paper</a>'
    "</body></html>"
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    gen = tmp_path / "examples" / "epidemiology-sir" / "generated"
    (gen / "figures").mkdir(parents=True)
    (gen / "presentation.html").write_text(HTML, encoding="utf-8")
    (gen / "figures" / "sir_trajectory.png").write_bytes(b"a")
    (gen / "figures" / "r0_comparison.png").write_bytes(b"b")
    (gen / "sir_equations.json").write_text("{}", encoding="utf-8")  # an input, never published
    return tmp_path


def test_stage_publishes_the_deck_its_figures_and_nojekyll_only(repo: Path) -> None:
    written = deck.stage(repo, repo / "site")

    assert written == ["index.html", "figures/r0_comparison.png", "figures/sir_trajectory.png", ".nojekyll"]
    assert deck.check(repo / "site") == []
    assert not (repo / "site" / "sir_equations.json").exists()


def test_check_refuses_a_file_that_was_not_staged(repo: Path) -> None:
    deck.stage(repo, repo / "site")
    (repo / "site" / "notes.md").write_text("draft", encoding="utf-8")

    assert deck.check(repo / "site") == ["unexpected file in site: notes.md"]


def test_check_refuses_a_figure_that_is_missing(repo: Path) -> None:
    deck.stage(repo, repo / "site")
    (repo / "site" / "figures" / "r0_comparison.png").unlink()

    assert any("missing file in site: figures/r0_comparison.png" in p for p in deck.check(repo / "site"))


def test_check_refuses_a_broken_local_link(repo: Path) -> None:
    deck.stage(repo, repo / "site")
    (repo / "site" / "index.html").write_text(HTML + '<img src="figures/gone.png">', encoding="utf-8")

    problems = deck.check(repo / "site")
    assert any("broken local link" in p and "figures/gone.png" in p for p in problems)


def test_check_refuses_a_site_with_no_index(repo: Path) -> None:
    (repo / "site").mkdir()

    assert deck.check(repo / "site") == ["site/index.html is missing"]
