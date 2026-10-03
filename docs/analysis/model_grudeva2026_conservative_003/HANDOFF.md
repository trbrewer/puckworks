# MODEL-GRUDEVA2026-CONSERVATIVE-003 handoff

One analysis-only branch/draft Puckworks PR referencing #67. No merge,
auto-merge, issue closure, production adoption, EWP write, OpenFOAM execution,
new laboratory work or automatic successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The conservative repair adds information beyond #309: actual paired state
exchange, continuous admission histories, a matching discrete front/transport
balance, and state-integrated global conservation through t=8. The declared
bed refinement still fails; this is not a qualified independent baseline
comparison. Baseline raw observation is prepared and tested only with synthetic
return objects. No new task-local coupled baseline observation was executed.
Original Figures 3/4 FAIL/FAIL and Figure 5 incomplete remain unchanged.

## Reproduction

Use this repository checkout and its declared NumPy/SciPy dependencies. Set
`GRUDEVA_EVIDENCE` to an external output directory and `GRUDEVA_308_ARCHIVE` to
the hash-bound six-run 001 archive. Never place full arrays, logs or PDFs in Git.
The following document reproduction; they do not authorize additional runs in
this closed bounded task. Every numerical invocation needs an external
start/end ledger, a 900-second timeout and a 2-GiB memory limit. The actual task
controller's identity and complete timing ledger are in RESULTS.json.

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m puckworks.analysis.grudeva2026_conservative_003_report --local --output "$GRUDEVA_EVIDENCE/local-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 32 --shells 16 --dt .01 --horizon 8 --diffusivity 0 --output "$GRUDEVA_EVIDENCE/limit-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 512 --shells 3200 --dt .002 --horizon 8 --output "$GRUDEVA_EVIDENCE/normal-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 1024 --shells 3200 --dt .002 --horizon 8 --output "$GRUDEVA_EVIDENCE/bed_fine-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 512 --shells 6400 --dt .002 --horizon 8 --output "$GRUDEVA_EVIDENCE/radial_fine-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 512 --shells 3200 --dt .001 --horizon 8 --output "$GRUDEVA_EVIDENCE/time_fine-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003 --bed 1024 --shells 6400 --dt .001 --horizon 8 --output "$GRUDEVA_EVIDENCE/combined-compat-final.json"
python -m puckworks.analysis.grudeva2026_conservative_003_report --runs-directory "$GRUDEVA_EVIDENCE" --matrix docs/analysis/model_grudeva2026_conservative_003/MATRIX.json --baseline-directory "$GRUDEVA_308_ARCHIVE" --output "$GRUDEVA_EVIDENCE/replayed-report.json"
```

Single coupled-run CLI calls intentionally exit **2**, including successfully
integrated trajectories: execution alone is not qualification. The saved-run
report also exits 2 for this incomplete outcome. Local analytical qualification
exits zero only on its own gates. No dimensional EY/TDS is invented; the
production failure-first CLI and unavailable dimensional quantities are unchanged.

The offline reporter consumes the retained `invocations.jsonl`, `environment.json`
and task controller `invoke.py` beside the raw artifacts, as well as the plan and
baseline archive. It performs no new coupled execution. Historical core versions
were recovered from the development edits and verified byte-for-byte against
their execution hashes; each is retained externally under its SHA256. Earlier
results keep their original hashes and are never restamped as final evidence.

## Acceptance checks and review

```bash
python -m pytest -q tests/test_grudeva2026_conservative_003.py tests/test_grudeva2026_reference_002.py tests/test_grudeva2026.py tests/test_grudeva2026_cli.py -m 'not slow'
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/
mypy
python -m build --outdir "$GRUDEVA_EVIDENCE/dist"
python tools/packaging_check.py "$GRUDEVA_EVIDENCE/dist"
python -m puckworks.insights verify
```

Existing software regression and hosted CI are separate QA; no new full-horizon
run or numerical sweep is hidden in the added tests. The current card changes
require the existing Insight Foundry generator; only its dependent snapshot is
regenerated. Historical numerical reports and source fixtures are unchanged.

One independent nonhuman exact-head review and required hosted checks are
recorded in the draft PR receipt after a candidate commit exists. Pending checks
are never implied by the numerical or software result. Required hosted contexts
were read from the active ruleset: quick (3.10), quick (3.12), verify-generated,
paper3-scope-strict and all-scope-strict. The PR must remain draft with auto-merge
disabled. No automatic successor is selected.
