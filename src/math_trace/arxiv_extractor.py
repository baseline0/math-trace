"""Extract equations from arXiv papers.

Workflow:
1. /api/arxiv/extract → download .tex, extract equations (fast, ~2 sec)
2. Save to disk with paper metadata
3. Dispatch conversion task to Ollama agent (overnight batch)
4. Results available via /api/arxiv/papers/{paper_id}
"""

from __future__ import annotations

import json
import re
import tarfile
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

from .constants import CACHE_DIR
from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class Equation:
    """Extracted equation from paper."""

    index: int
    latex: str
    context: str
    sympy_expr: str | None = None
    conversion_status: str = "pending"  # pending, converted, failed, manual


@dataclass
class ExtractedPaper:
    """Paper with extracted equations."""

    paper_id: str
    title: str
    authors: str
    arxiv_url: str
    equations: list[dict]  # List of equation dicts
    extraction_timestamp: str
    total_equations: int


def extract_arxiv_id(url_or_id: str) -> str:
    """Extract arXiv ID from URL or pass-through if already ID."""
    # Format: 2301.13848 or https://arxiv.org/abs/2301.13848
    match = re.search(r"(\d{4}\.\d{4,5})", url_or_id)
    if match:
        return match.group(1)
    raise ValueError(f"Invalid arXiv URL or ID: {url_or_id}")


def fetch_paper_metadata(paper_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    url = f"http://export.arxiv.org/api/query?id_list={paper_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    # Parse minimal XML
    import xml.etree.ElementTree as ET

    root = ET.fromstring(response.content)

    # Extract from entry
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)

    if entry is None:
        raise ValueError(f"Paper not found: {paper_id}")

    title = entry.find("atom:title", ns).text.strip()
    authors = ", ".join([a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)])

    return {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "arxiv_url": f"https://arxiv.org/abs/{paper_id}",
    }


def download_and_extract_equations(paper_id: str, max_equations: int = 50) -> tuple[str, list[Equation]]:
    """Download arXiv source and extract equations.

    Returns: (tex_content, list of Equation objects)
    """
    # Download .tar.gz
    url = f"https://arxiv.org/e-print/{paper_id}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    equations = []

    # Extract and parse
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = Path(tmpdir) / "source.tar.gz"
        tar_path.write_bytes(response.content)

        with tarfile.open(tar_path) as tar:
            tar.extractall(tmpdir)

        # Find main .tex file
        tex_files = list(Path(tmpdir).glob("*.tex"))
        if not tex_files:
            raise FileNotFoundError("No .tex files in arXiv source")

        main_tex = max(tex_files, key=lambda p: p.stat().st_size)
        tex_content = main_tex.read_text(encoding="utf-8", errors="ignore")

    # Extract equations from raw LaTeX
    patterns = [
        (r"\\\[(.+?)\\\]", "displayed"),
        (r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", "inline"),
        (r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}", "equation"),
        (r"\\begin\{align\*?\}(.+?)\\end\{align\*?\}", "align"),
        (r"\\begin\{multline\*?\}(.+?)\\end\{multline\*?\}", "multline"),
    ]

    for pattern, env_type in patterns:
        matches = re.finditer(pattern, tex_content, re.DOTALL)
        for match in matches:
            if len(equations) >= max_equations:
                break

            latex_str = match.group(1).strip()

            # Skip trivial matches
            if len(latex_str) < 5:
                continue

            # Skip pure formatting/metadata
            if all(cmd in latex_str for cmd in ["\\text{", "label", "ref"]):
                continue

            # Get context
            start = max(0, match.start() - 150)
            end = min(len(tex_content), match.end() + 150)
            context = tex_content[start:end]
            context = re.sub(r"\\[a-z]+\{[^}]*\}", "", context)[:120]

            equations.append(
                Equation(
                    index=len(equations),
                    latex=latex_str,
                    context=context,
                )
            )

    return tex_content, equations


def save_extracted_paper(paper_id: str, output_dir: Path = None) -> Path:
    """Extract paper and save to disk.

    Structure:
    output_dir/
      papers/
        {paper_id}/
          metadata.json
          equations.jsonl  (one equation per line)
    """
    if output_dir is None:
        output_dir = CACHE_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    paper_dir = output_dir / "papers" / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)

    # Fetch metadata
    metadata = fetch_paper_metadata(paper_id)

    # Extract equations
    tex_content, equations = download_and_extract_equations(paper_id)

    # Save metadata
    metadata["extraction_timestamp"] = __import__("datetime").datetime.utcnow().isoformat()
    metadata["total_equations"] = len(equations)

    metadata_path = paper_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    # Save equations (JSONL format for streaming)
    equations_path = paper_dir / "equations.jsonl"
    with open(equations_path, "w") as f:
        for eq in equations:
            f.write(json.dumps(asdict(eq)) + "\n")

    # Save raw TeX for reference
    tex_path = paper_dir / "source.tex"
    tex_path.write_text(tex_content[:100000])  # First 100k chars

    return paper_dir


def load_extracted_paper(paper_id: str, cache_dir: Path = None) -> dict:
    """Load previously extracted paper from cache."""
    if cache_dir is None:
        cache_dir = CACHE_DIR

    paper_dir = cache_dir / "papers" / paper_id

    if not paper_dir.exists():
        raise FileNotFoundError(f"Paper not cached: {paper_id}")

    # Load metadata
    metadata = json.loads((paper_dir / "metadata.json").read_text())

    # Load equations
    equations = []
    for line in (paper_dir / "equations.jsonl").read_text().strip().split("\n"):
        if line:
            equations.append(json.loads(line))

    metadata["equations"] = equations
    return metadata
