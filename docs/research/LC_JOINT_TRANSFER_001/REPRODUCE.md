# Reproduction

Use the repository development environment with NumPy, SciPy, Numba and
Matplotlib. Keep original inputs and large trial/prediction artifacts outside Git.
`SOURCE_AUDIT.json` authenticates the inputs; `MC_PROVENANCE.csv` identifies each
fixed C2 T2-F entry. The EWP reference checkout's FORM_A files must match
`67bead2a25bd7e61c16c4fe2c104d885d8d26dd9`. EWP is only read.

Set these local paths without committing them:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
LC_PYTHON=/path/to/environment/bin/python
LC_WORK=/path/to/external/task-artifacts
lc_inputs=(
  --ewp /path/to/read-only/ewp-reference
  --native /path/to/retained/FORM_A/campaign
  --raw /path/to/authenticated/waszkiewicz/upstream
  --screen /path/to/WETTING_SCREEN_001/artifacts
  --joint /path/to/JOINT_CLOCK_001/artifacts
  --work "$LC_WORK"
)

"$LC_PYTHON" -m pytest -q tests/test_lc_joint_transfer_001.py
"$LC_PYTHON" -m puckworks.analysis.lc_joint_transfer_001_run replay "${lc_inputs[@]}" --workers 24
"$LC_PYTHON" -m puckworks.analysis.lc_joint_transfer_001_run fit "${lc_inputs[@]}" --workers 96
"$LC_PYTHON" -m puckworks.analysis.lc_joint_transfer_001_evaluate "${lc_inputs[@]}" --workers 32
"$LC_PYTHON" -m puckworks.analysis.lc_joint_transfer_001_report "${lc_inputs[@]}"
"$LC_PYTHON" -m puckworks.analysis.lc_joint_transfer_001_cor15 --work "$LC_WORK"
```

The plan must be committed before `fit`. Replay uses saved A-J1 parameters and
compares original objective, detector state, trace scores and retained arrays at
rtol=1e-12, atol=0. It performs no optimization. Fitting has exactly 48 problems
and 912 starts. Independent starts execute in parallel; submission and collected
records preserve the declared 19-start order. No start depends on another start.
Artifact start indices are zero-based: 0 is embedded A-J1, 1 is historical LC
with matching A-J1 tau0, 2 is historical LC with tau0=0, and 3–18 are the sixteen
Latin-hypercube starts. Execution logs display the corresponding numbers 1–19.
The optimizer and evaluator identities prevent accidental reuse after code changes.
`collect` only aggregates completed scheduled starts; it performs no fitting.

The evaluation command first saves `FROZEN_EXTERNAL_SHAPES.json`, then generates
the .005/.02-s predictions and frozen f=0 diagnostics. The external command
requires that freeze and matches it to `FIT_FREEZE.json`. Its only target-fitted
parameters are positive series amplitudes. It also replays the historical D0 FA
central/reading contrasts, without running COR15's other fitted families.

`starts/*.json`, `trials/*.json.gz`, `fits/*.json`, prediction `.npz` arrays,
`NEAR_OBJECTIVE_VECTORS.json.gz`, matched resamples and external reading draws
remain outside Git. Compact tables retain hashes and all scheduled start outcomes.
Near-objective vectors use the inherited 1e-6*max(1,Jbest) diagnostic, not a new
identification threshold. Their capacity envelopes describe sampled alternatives,
not confidence limits or proof of global optimality.

Required checks are the offline quick lane on supported interpreters, Ruff and
the repository generated-artifacts workflow. Locally:

```bash
"$LC_PYTHON" -m pytest -q -m 'not slow and not live and not gpu and not external_data'
"$LC_PYTHON" -c 'from puckworks.registry import run_all_gates; run_all_gates()'
ruff check puckworks/ tests/
git diff --check
```

These commands reuse the original campaigns. They do not invoke EWP, CFD,
bootstrap refits, additional capacity laws or a successor task.
