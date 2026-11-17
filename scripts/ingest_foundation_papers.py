"""Ingest foundational quantum code claims via Hermes.

This script reads the Hermes prompt contract from ``docs/hermes_prompt_contract.txt``,
executes the local ``hermes-fleet`` or ``hermes`` CLI with ``--query-file`` to obtain the JSON payload,
validates it against the ``LitClaim`` schema, writes the result to ``artifacts/lit_claims.json``,
and then runs the rendering pipeline followed by a Lean verification.
"""

# ruff: noqa: N815
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, Field

from math_trace.constants import REPO_ROOT

app = typer.Typer(help="Ingest foundation papers via Hermes and render Literature.lean")

DEFAULT_PROMPT = REPO_ROOT / "docs" / "hermes_prompt_contract.txt"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "lit_claims.json"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render_literature_lean.py"


class LitClaim(BaseModel):
    paperId: str
    claimId: str
    title: str
    codeN: int = Field(gt=0)
    codeK: int = Field(gt=0)
    codeDistance: int = Field(gt=0)
    thresholdPpm: int = Field(ge=0)
    assumptions: list[str] = Field(default_factory=list)


def _get_hermes_bin() -> str:
    candidates = [
        os.environ.get("HERMES_BIN"),
        shutil.which("hermes-fleet"),
        shutil.which("hermes"),
        "/home/mark/.local/bin/hermes-fleet",
        "/home/mark/.local/bin/hermes",
    ]
    for candidate in candidates:
        if candidate and (shutil.which(candidate) or Path(candidate).is_file()):
            return candidate
    raise RuntimeError("Neither `hermes-fleet` nor `hermes` binary found. Ensure ~/.local/bin is in PATH.")


def _run_hermes(prompt_path: Path) -> str:
    """Execute Hermes CLI using --query-file and --quiet to obtain the raw JSON payload."""
    hermes_bin = _get_hermes_bin()
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")

    # Use hermes chat --query-file ... -Q (--quiet) to get pure JSON stdout
    result = subprocess.run(
        [hermes_bin, "chat", "--query-file", str(prompt_path), "-Q"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Hermes execution failed with exit code {result.returncode}:\n{result.stderr}")
    return result.stdout.strip()


@app.command()
def ingest(
    prompt: Annotated[
        Path,
        typer.Option("--prompt", "-p", help="Path to Hermes prompt contract"),
    ] = DEFAULT_PROMPT,  # typer-explicit: allow-optional: default prompt path
    out: Annotated[
        Path,
        typer.Option("--out", "-o", help="Destination JSON file"),
    ] = DEFAULT_OUT,  # typer-explicit: allow-optional: default output json path
) -> None:
    """Fetch claims via Hermes, validate, write JSON, render Lean, and verify."""
    typer.echo(f"Dispatching ingestion prompt from {prompt} to Hermes...")
    raw = _run_hermes(prompt)

    # Attempt to locate a JSON array in the output. Hermes may include surrounding
    # explanatory text, so we search for the first '[' and parse until the matching ']'.
    import re

    json_str: str | None = None
    # Simple heuristic: find the first '[' and the last ']' after it.
    start = raw.find("[")
    if start != -1:
        end = raw.rfind("]")
        if end != -1 and end > start:
            json_str = raw[start : end + 1]
    # Fallback: look for a fenced code block containing JSON.
    if json_str is None:
        m = re.search(r"```json\s*(\[.*?\])\s*```", raw, re.DOTALL)
        if m:
            json_str = m.group(1)
    if json_str is None:
        raise RuntimeError(f"Hermes output does not contain a JSON array: {raw[:200]}...")
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON from Hermes output:\n{json_str}") from exc

    claims = [LitClaim(**item) for item in data]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([c.model_dump() for c in claims], indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Validated and wrote {len(claims)} claims to {out}")

    # Step 3: Run the rendering pipeline
    subprocess.run([sys.executable, str(RENDER_SCRIPT), f"--json={out}"], check=True)
    typer.echo("Rendered Literature.lean and updated claims.toml")

    # Step 4: Verify Lean compilation
    subprocess.run(["just", "lean-verify"], cwd=REPO_ROOT, check=True)
    typer.echo("Lean compilation gate passed successfully.")


if __name__ == "__main__":
    app()
