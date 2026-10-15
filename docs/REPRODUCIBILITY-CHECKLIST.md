# Reproducibility Verification Checklist

**For External Reviewers**

This checklist verifies that a registered reference of math-trace rebuilds from a fresh checkout and passes its
checks. It covers every reference registered in `REFERENCES` in `src/math_trace/reference_check.py`:

| Reference | Role | Section |
| --- | --- | --- |
| `sidorenko-turan` | Flagship reference | [sidorenko-turan](#reference-sidorenko-turan) |
| `epidemiology-sir` | Secondary example | [epidemiology-sir](#reference-epidemiology-sir) |

A future reference is covered by registering it in `REFERENCES`, then adding a section here in the same form.

The reviewer runs one command per reference, `just reference-check <name>`, and reads its exit status and report.

---

## Environment Requirements

- **Python**: 3.13 or later (`.python-version` pins 3.13; `pyproject.toml` requires `>=3.13`)
- **OS**: Linux, macOS, or Windows (WSL2)
- **Tools**: `uv` (dependency and Python manager) and `just` (task runner)
- **Network**: Needed for the initial `uv sync` only. The reference builds do not fetch anything.

Typst is not needed to reproduce the registered references. Their builds do not invoke it.

---

## Shared Procedure

Run these steps for each reference. The reference section gives the reference's own commands and status.

### Step 1: Fresh Checkout

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
git checkout <tag-under-review>
```

**Acceptance**: The clone succeeds, and the checkout is the tag under review. The report's `tag` field shows that tag,
and `dirty` is `false`.

### Step 2: Install

```bash
uv sync
```

**Acceptance**: `uv sync` completes. Then `uv run python --version` prints `3.13.x`.

### Step 3: Run the Reference Check

```bash
just reference-check <name>
```

The check does the following, in order:

1. Confirms the reference's required files exist.
2. Runs the reference's build twice and hashes every output after each run.
3. Runs the reference's contract tests.
4. Records provenance: the source revision, the tag if any, whether the tree is dirty, and the Python version.
5. If the reference registers an expected-hashes file, compares the outputs, the `uv.lock` hash, and the Python version with it.

It writes a JSON report to `examples/<name>/generated/reference-report.json`.

**Acceptance**: Exit status `0`, and the report's `result` field is `"pass"`.

### Step 4: Regenerate and Compare

The check in Step 3 regenerates the outputs itself. To rebuild by hand, run the reference's build commands from its
section, inside its directory.

Compare the results with the recorded state:

- **References with an expected-hashes file**: the report's `expected` field is not `null`, and `expected_problem` is
  `null`. Every output hash matches, and the Python version and `uv.lock` hash match.
- **References without one**: the report's `expected` field is `null`. The evidence is that two builds from the same
  checkout produce identical outputs (`deterministic` is `true`) and the contract tests pass (`tests_returncode` is `0`).
  The recorded hashes are not available for these references.

### Step 5: README

The repository README explains the reference's assumptions, its limitations, and how to read its results.

**Acceptance**: The reviewer finds each assumption and limitation listed in the reference's section stated in the README,
and finds nothing in the README that contradicts the report.

### Step 6: Failure Messages

A failed check exits `1`. The output names each reason on its own line, and the report's `failures` field holds the same
list. Examples of the reasons the check can name:

- `required files missing: ...`
- `build step exited <code>: <command>`
- `contract tests exited <code>`
- `two builds from the same checkout produced different outputs`
- `output differs from the recorded hash: <file>`
- `python version changed: ...`
- `uv.lock changed: ...`

**Acceptance**: A failure prints named reasons and writes the report. A raw traceback from the check is a finding to
report.

---

## Reference: sidorenko-turan

The flagship reference: a computable companion to a Turán-density theorem, with its Lean statement recorded in
`formalization.json`.

- **Directory**: `examples/sidorenko-turan`
- **Build command** (run in the directory): `uv run python build_table.py`
- **Output**: `generated/gap_table.json`
- **Required files**: `build_table.py`, `lean_statement.lean`, `formalization.json`
- **Expected hashes**: `examples/sidorenko-turan/expected-hashes.json` is present. It records the Python version, the
  `uv.lock` hash, and the hash of `generated/gap_table.json`. The check compares against it.
- **Contract tests**: `tests/integration/test_sidorenko_turan_contract.py` (5 tests)

**What the check establishes**: The displayed constant and gap are reproduced by exact symbolic arithmetic.

**What it does not establish**: That the Lean statement matches the paper's claim. `build_table.py` says so in its
docstring. The statement-match evidence is recorded in `formalization.json`. That run used network access, so the
file says it is not Phase B evidence.

---

## Reference: epidemiology-sir

A SIR epidemic model, with a COVID scenario, a generated paper, and a presentation.

- **Directory**: `examples/epidemiology-sir`
- **Build commands** (run in the directory, in this order):
  1. `uv run python build_paper.py`
  2. `uv run python build_presentation.py --output generated/presentation.html`
- **Outputs**: `generated/sir_equations.json`, `generated/covid_scenario.json`, `generated/figures/*.png`,
  `generated/presentation.html`
- **Required files**: `build_paper.py`, `build_presentation.py`, `presentation_config.yaml`, `src/model.py`,
  `src/simulate.py`
- **Expected hashes**: none registered. The check compares two builds with each other and runs the contract tests.
- **Contract tests**:
  - `tests/integration/test_epidemiology_sir_contract.py` (17 tests)
  - `tests/unit/test_build_presentation.py` (10 tests)
  - `tests/unit/test_sir_presentation_config.py` (1 test)

**What the check establishes**: The build is deterministic and the contract tests pass.

**What it does not establish**: That the model is a valid epidemiological model, or that its parameters fit any data.

---

## Repository Gates

These are repository-wide, not specific to a reference. Run them from the checkout.

```bash
just check                                                # ruff lint; exits 0 when lint passes
uv run ruff format --check src tests examples templates   # format check without rewriting files
just typecheck                                            # mypy; see the note below
```

**Note**: `just typecheck` runs mypy and exits with its status, currently `1` with 45 errors. It is not a gate; `just check-types` (pyright ratchet) is the gate.

**Acceptance**: `just check`, the format check, and `just check-types` exit `0`.

---

## Release Artifacts

Verify these exist at the repository root:

- [ ] `LICENSE`
- [ ] `pyproject.toml` (version `0.1.0`, `requires-python = ">=3.13"`)
- [ ] `CITATION.cff`
- [ ] `CHANGELOG.md`
- [ ] `justfile`
- [ ] `.pre-commit-config.yaml`
- [ ] `README.md`, `CONTRIBUTING.md`, `AGMAI-READY.md`
- [ ] `docs/adr/` (architecture decision records)
- [ ] `docs/guides/getting-started-external.md`

---

## Sign-Off

**Reviewer**: ________________
**Date**: ________________
**Environment**: macOS / Linux / WSL2 | Python version: ______
**Tag reviewed**: ________________

### Results

| Reference | `just reference-check` exit | Report `result` | Notes |
| --- | --- | --- | --- |
| `sidorenko-turan` | | | |
| `epidemiology-sir` | | | |

- [ ] Each reference's section above was followed
- [ ] Each registered reference passes Step 3
- [ ] Each reference's limitations are stated in the README
- [ ] Repository gates pass (`just check`, format check, `just check-types`)
- [ ] Release artifacts are present

### Known Limitations Acknowledged

- [ ] The check verifies that a build reproduces its outputs and passes its contract tests. It does not verify
      scientific validity.
- [ ] A reference without an expected-hashes file is checked for determinism and contract tests only.
- [ ] Each reference's own limitations, as listed in its section above.

### Recommendation

**☐ APPROVED**
Reproducibility verified for the references listed above.

**☐ CONDITIONAL** (list issues below)
Reproducibility verified with minor issues:

```
[List any issues found]
```

**☐ NOT APPROVED** (list blockers below)
Reproducibility blocked by:

```
[List blocking issues]
```

---

## Questions or Issues?

Open an issue at https://github.com/baseline0/math-trace/issues or email the maintainer.
