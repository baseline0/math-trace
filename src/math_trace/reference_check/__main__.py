"""Module entrypoint for `python -m math_trace.reference_check`.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| `python -m math_trace.reference_check` invokes the Typer app | reviewer-path CLI contract | `__main__`; exercised by package entrypoint convention |
"""

from . import app

if __name__ == "__main__":
    app()
