# External Review Guide: the Sidorenko Flagship Gate

**What we are asking you to do**

Run one command on a fresh clone of the release tag, read the report it writes, and sign off on that report. The command is `just reference-check`, which defaults to the flagship reference `sidorenko-turan`. Passing it is the v1.0.0 gate.

The reference reproduces one result: a Turán-density bound for r-uniform hypergraphs with r ≥ 3. The paper proves that bound. It is not a proof of Sidorenko's conjecture. The [README](../README.md) gives the statement and the background.

---

## What the gate checks

`just reference-check` runs the registry entry for `sidorenko-turan` in [`src/math_trace/reference_check.py`](../src/math_trace/reference_check.py). It establishes the following, all from one checkout:

1. The required files exist: [`build_table.py`](../examples/sidorenko-turan/build_table.py), [`lean_statement.lean`](../examples/sidorenko-turan/lean_statement.lean), and [`formalization.json`](../examples/sidorenko-turan/formalization.json).
2. The build runs twice. Every output (`generated/gap_table.json`) is hashed with SHA-256. The two runs must give identical hashes, and the output must not be empty.
3. The contract tests pass: [`tests/integration/test_sidorenko_turan_contract.py`](../tests/integration/test_sidorenko_turan_contract.py). They compare each displayed constant and gap with an independent float evaluation, and check that the gap is positive and decreases in m.
4. The outputs match the recorded hashes in [`expected-hashes.json`](../examples/sidorenko-turan/expected-hashes.json). That file records the Python version (3.13.15), the SHA-256 of `uv.lock`, and the hash of `gap_table.json`.
5. Provenance is written to the report: the source revision, the tag if HEAD has one, whether the tree is dirty, the Python version, and the hash of each required input.

The gate passes only if all five hold. A dirty tree is recorded but does not fail the check, so review a clean clone (`git status` empty).

## What the gate does not check

The gate does not rebuild the Lean project and does not re-run the Comparator. The following results are recorded in [`formalization.json`](../examples/sidorenko-turan/formalization.json). They are not reproduced by this command, and you do not need to reproduce them to sign off.

- **Lean build and axioms** (`build`, `axioms`): recorded from run `20261013T213113Z`. The upstream project `xliu2022/improved-sidorenko-lean` at commit `ba6f109`, toolchain `leanprover/lean4:v4.35.0-rc2`, Mathlib `065356127`. The three main theorems depend only on `propext`, `Classical.choice`, and `Quot.sound`.
- **Lean statement match** (`statement_match`): recorded from run `20261015T204628Z`. The upstream repository's own Comparator judge printed "Your solution is okay!". **That run used network access** (`--allow-network`), so it is not offline (Phase B) evidence. Do not report it as an offline result. Re-running it is a separate task, not part of this gate.
- **Scientific content**: the gate checks transcription and arithmetic. Whether the paper's mathematics is right is for peer review.

---

## Steps

### 1. Fresh clone of the tag

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
git checkout <tag>        # the release tag under review
git status                # should print nothing
```

### 2. Install the locked dependencies

```bash
uv sync --frozen
```

`uv` fetches Python 3.13 from `.python-version`. The expected hashes were recorded on Python 3.13.15. A different 3.13 patch version makes the gate fail with `python version changed`. That is a finding to report, not a reason to edit `expected-hashes.json`.

### 3. Run the gate

```bash
just reference-check
echo $?                   # 0 = pass, 1 = fail
```

On success the last line names the report. On failure the command prints one line per failed check, for example `contract tests exited 1`, and exits 1. The report is written in both cases.

### 4. Read the report

Open `examples/sidorenko-turan/generated/reference-report.json`. Its `result` field is `pass` or `fail`, and `failures` lists each reason. The possible reasons are: missing required files, a build step that exited non-zero, failing contract tests, no outputs, outputs that differ between two builds, and a mismatch with the recorded hashes.

### 5. Sign off

Send your sign-off on the report (the `result`, the `failures` list, and the `source_revision` it records) by email or as a PR comment to the maintainer. The v1.0.0 tag is cut only after this sign-off.

---

## If something fails

- **The command exits 1.** Keep the report and the full terminal output. Send both. Do not edit files to make the check pass.
- **Python version or `uv.lock` mismatch.** The report names the recorded and the running value. Report it. Re-recording the hashes is the maintainer's decision.
- **Contract tests fail.** The report's `failures` names the failing test file. Send the pytest output with the report.
- **Setup fails** (`uv` cannot install Python 3.13): report the error and your OS. Do not change `.python-version`.

---

## Optional: the secondary example

`epidemiology-sir` is a registered secondary example. It is not part of the v1.0.0 gate.

```bash
just reference-check epidemiology-sir
```

An unknown name exits 2 and lists the registered names.

---

## What we are not asking you to do

- Verify scientific validity or empirical adequacy.
- Re-run the Lean build, the axiom check, or the Comparator. Those are recorded, as described above.
- Run performance benchmarks.
- Test on Python versions other than the one recorded in `expected-hashes.json`, unless the gate requires it.
- Modify code, hashes, or the formalization record, or commit changes.

---

## Questions

- **Technical**: open an issue at https://github.com/baseline0/math-trace/issues
- **Scope**: email the maintainer, Mark Alexiuk, malexiuk@gmail.com
- **Logistics**: tag in a PR or discussion
