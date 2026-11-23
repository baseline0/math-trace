# math-trace roadmap

Status: pre-release (`0.1.0`). This roadmap tracks near-term engineering work; items move only when merged and verified.

## Done (2026-05)

- **Modularity / tech-debt refactor (agent/math-trace-next-tasks)**: split large modules into packages while preserving public APIs/import seams.
  - `server.py` -> `server/` package (`app`, routes, ui, hardness routes, `__main__`), preserving `math_trace.server` exports and monkeypatch seams.
  - `generators.py` -> `generators/` package (`sympy_typst`, latex-to-typst helpers, typst env builder).
  - `reference_check.py` -> `reference_check/` package with preserved CLI/API/module entrypoint behavior.
  - `formula_records.py` -> `formula_records/` package (models, normalize, tags, io, builder).
  - `services.py` -> `services/` package (downloader, extractor, presentation builder).
  - `paper_store.py` -> `paper_store/` package (types, validation, store) with preserved errors/constants/API.
  - Hardened arXiv tar extraction against unsafe archive members (path traversal/symlinks/device entries).
  - Added characterization tests for refactor facades/public API seams.

## Next

- **Task 6 (deferred, do when UI work is planned)**: split `src/math_trace/server/ui.py` into template/static-oriented modules; keep route behavior and HTML contracts stable.
- **Coverage/quality follow-up**: add targeted characterization tests for remaining low-coverage public paths touched by extraction/presentation flows; avoid coverage-only churn.
- **Reference/reproducibility**: continue expanding reviewer-facing reference checks and recorded evidence; keep claims scoped to what `just reference-check` establishes.
- **Release readiness**: complete external reproducibility review, tag/release process, and v1.0.0 criteria before claiming release stability.
