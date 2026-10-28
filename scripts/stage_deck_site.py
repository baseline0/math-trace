"""Stage the reviewed SIR deck as the GitHub Pages site: index.html, the figures it links to, and .nojekyll. Nothing else.

The deck and its figures are gitignored outputs, so the publish workflow builds them first (build_paper.py, then
build_presentation.py). stage copies only what the deck links to, and check refuses any other file in the site folder
or any link that does not resolve.

    uv run python scripts/stage_deck_site.py stage --root . --site site
    uv run python scripts/stage_deck_site.py check --site site
"""

import re
import shutil
from pathlib import Path
from typing import Annotated

import typer

DECK = Path("examples/epidemiology-sir/generated/presentation.html")
FIGURE_LINK = re.compile(r'(?:src|href)="(figures/[^"]+)"')
NOJEKYLL = ".nojekyll"

app = typer.Typer(no_args_is_help=True, add_completion=False)


def linked_figures(html: str) -> list[str]:
    """The figure paths the deck links to, relative to the deck folder, in order and without duplicates."""
    return sorted(set(FIGURE_LINK.findall(html)))


def stage(root: Path, site: Path) -> list[str]:
    """Replace site with the deck as index.html, the figures it links to, and .nojekyll. Returns the files written."""
    html = (root / DECK).read_text(encoding="utf-8")
    figures = linked_figures(html)
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    (site / "index.html").write_text(html, encoding="utf-8")
    for figure in figures:
        target = site / figure
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / DECK.parent / figure, target)
    (site / NOJEKYLL).touch()
    return ["index.html", *figures, NOJEKYLL]


def check(site: Path) -> list[str]:
    """Every problem with the site folder: a file that should not be there, a missing file, or a broken local link."""
    if not (site / "index.html").is_file():
        return ["site/index.html is missing"]
    html = (site / "index.html").read_text(encoding="utf-8")
    figures = linked_figures(html)
    expected = {"index.html", NOJEKYLL, *figures}
    present = {str(path.relative_to(site)) for path in site.rglob("*") if path.is_file()}
    problems = [f"unexpected file in site: {name}" for name in sorted(present - expected)]
    problems += [f"missing file in site: {name}" for name in sorted(expected - present)]
    for link in re.findall(r'(?:src|href)="([^"#?]+)"', html):
        if "://" not in link and not link.startswith(("mailto:", "data:")) and not (site / link).is_file():
            problems.append(f"broken local link in index.html: {link}")
    return problems


@app.command("stage")
def stage_command(
    root: Annotated[Path, typer.Option("--root", help="The math-trace checkout.")],
    site: Annotated[Path, typer.Option("--site", help="The folder to publish.")],
) -> None:
    """Stage the deck. The deck and its figures must already be built."""
    written = stage(root, root / site)
    typer.echo("staged: " + ", ".join(written))


@app.command("check")
def check_command(
    site: Annotated[Path, typer.Option("--site", help="The folder to publish.")],
) -> None:
    """Exit 1 unless the site holds exactly the deck, its figures and .nojekyll, with every local link resolving."""
    problems = check(site)
    for problem in problems:
        typer.echo(problem)
    if problems:
        raise typer.Exit(1)
    typer.echo("site OK")


if __name__ == "__main__":
    app()
