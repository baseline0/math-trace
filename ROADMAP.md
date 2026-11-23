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
- **Coverage/quick-win hardening (agent/math-trace-coverage-quickwin, agent/math-trace-formula-routes-quickwin, agent/math-trace-downloader-hardening)**:
  - Added characterization coverage for `services` (downloader/extractor/builder paths) and formula routes (API/browser success, empty, and error branches).
  - Fixed formula API behavior: `get_formulas` now re-raises `HTTPException` before broad exception mapping, preserving intended 404 responses.
  - Hardened `PaperDownloader.download` with explicit `http/https` scheme validation and a 30s `urlopen` timeout; preserved public API and cache behavior.

## Next

- **Task 6 (deferred, do when UI work is planned)**: split `src/math_trace/server/ui.py` into template/static-oriented modules; keep route behavior and HTML contracts stable.
- **Coverage follow-up**: add targeted characterization tests for remaining low-coverage public paths in extraction/presentation flows (`arxiv_extractor`, `formula_browser`, selected server routes) where behavior is stable; avoid coverage-only churn.
- **Formula route error-contract audit**: review broad exception-to-HTML/500 behavior in formula browser/API routes for accidental status drift; keep intentional user-facing HTML fragments stable.
- **Reference/reproducibility**: continue expanding reviewer-facing reference checks and recorded evidence; keep claims scoped to what `just reference-check` establishes.
- **Release readiness**: complete external reproducibility review, tag/release process, and v1.0.0 criteria before claiming release stability.
