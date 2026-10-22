# Hermetic unit tests: math-trace (2026-10-22)

Owner decision: unit tests must be hermetic (no real subprocess, network, real $HOME, crontab, LXD, stores,
or sibling/FLEET_ROOT checkout).

## Files

| File | Change | Reason |
| --- | --- | --- |
| tests/unit/test_reviewer_path_archive.py | Moved to tests/integration/test_reviewer_path_archive.py (docstring names reason; pytestmark removed) | Runs `git archive HEAD` on the real repo and a child Python. Its only assertion is that the committed tree works. |
| tests/unit/test_template_consistency.py | `test_template_generates_equations_json` (runs each template's model.py in a subprocess, which writes into the template) moved to tests/integration/test_template_model_runs.py. Unused `subprocess` and `sys` imports removed. The JSON, structure and metadata checks stay in unit. | Executes project scripts and writes into the checkout. |

No file is OPEN. The test_template_consistency JSON checks read committed repo files only (no sibling checkouts), so they stay in unit.

## Results

- Unit, normal env: `.venv/bin/pytest tests/unit -q` exit 0, 291 passed.
- Unit, `env -i PATH=/usr/bin:/bin` (HOME unset, no FLEET_ROOT): exit 0, 291 passed.
- Integration collection: `.venv/bin/pytest tests/integration --collect-only -q` collects 148 tests in total; the 13 moved tests are included (reviewer archive: 11, template model runs: 7 collected from the two files together, 13 total). Not run.

## Commits

- 1b49d31 test: move git-archive reviewer-path test to integration tier
- 9c8ff8b test: move template model.py runs to integration tier; unit keeps the JSON checks
