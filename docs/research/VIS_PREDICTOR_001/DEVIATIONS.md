# Preserved execution repairs

The plan/corpus/folds were committed at
`24593a21bd7faf9a8aac84526c96424e98a711cb` before fitting and before any held-out
scoring. PLAN.md and FROZEN_MANIFEST.json remain unchanged.

## Large-array sort failure, before scoring

The first fitting attempt used NumPy 2.5.4's default `unique(...,
return_inverse=True)` sort. Constructing fold 2's pressure operator failed with
`IndexError: index 149726304 is out of bounds for axis 0 with size 24345200`.
The batch was stopped; source, logs, completed artifacts and active-process CPU
accounting were preserved privately. No shape fit had completed, and no held-out
prediction/score had been generated. Five designs had completed T0/R0/L0R fits
(four outer folds and deployment); fold 2 failed before fitting.

Repair: request indices as well as the inverse from `numpy.unique`, selecting its
stable mergesort path, and assert exact reconstruction of every original pressure
node. Every fold and deployment design then passed the full actual-covariate
check. Sparse mean pressure agreed with direct native quadrature within
1.60e-14 bar. All fifteen completed scalar-model training objectives replayed
with **zero difference**; those artifacts are reused with their original source
hashes. Interrupted shape starts are rerun under the same scheduled starts and
settings. This is continuation of the declared fits, not another scientific
campaign, added model or outcome-selected setting. The failed default-sort
attempt remains part of the reported cost.

## Numerical audit correction, before scoring

The fresh read-only reviewer supplied a synthetic M0R example where using h(P)
alone in the audit's calibration floor passed 4.37e-6 relative error, whereas
using the full basis including R(M) yielded 1.07e-5 and correctly failed the
frozen 1e-5 threshold. Apply the same start-mass recovery factor to both integrated
bases before computing that floor/error. The threshold and prediction/fit
operators are unchanged. A regression test reproduces the example. No actual
audit, held-out score or recommendation had run before this correction.

Focused verification after both corrections: **27 passed**; Ruff passed.
The original full offline suite passed **8,089 tests**, with 33 skipped and 97
excluded by the repository's ordinary quick selector. Final required hosted CI
will test the completed head. EWP, snapshot bytes and historical results are
unchanged. Individual data, interrupted starts and process details remain private.

Two concurrent stable-sort design builds subsequently failed the new exact-inverse
assertion (folds 2 and 3), before any fitting in those invocations. The serial
six-design checks remained successful. Serialize Design construction using a
private POSIX file lock; retain parallel independent optimizer starts. Both retry
builds then passed. The observed failure depends on the concurrent execution
context; its lower-level cause is not established. All admitted designs enforce
exact inverse reconstruction. No guard was weakened and no corpus, fold, model,
start, bound, metric or audit threshold changed. Failed-startup logs are retained.

The serial retry for fold 3 then failed sparse construction with
`axis 0 index 1073768329 exceeds matrix dimension 114667`. Thus stable sorting
alone was insufficient in that runtime. All remaining fitting was stopped again;
completed models, source/logs and active-process CPU were preserved. Move execution
to an isolated environment with the repository's declared minimum dependency lane:
**NumPy 2.0.2 / SciPy 1.13.1**, replacing NumPy 2.5.4 / SciPy 1.18.1.
No claim about the underlying library/hardware cause is established.

In the minimum-dependency environment all six designs pass exact pressure-node
reconstruction, native/sparse pressure means (<=1.60e-14 bar), and equality of
flow, start mass, time and shot-index arrays with their inputs. All **22 completed
shared fits** replay their training objective with zero difference; retain them,
including their original artifact/source hashes. ENVIRONMENT.json identifies
those artifacts and both runtimes. Remaining scheduled fits use the continuation
runtime; model metadata records it. Starts, optimizer method/options, bounds,
corpus, folds, target operator and all scoring rules stay fixed. Native/sparse
pressure agreement and intact window arrays are now checked on every Design build.
No actual numerical audit or held-out scoring occurred during either failed run.
