# RP-D-LC-001b reference process parallelism v1

```
IMPLEMENTATION ONLY · PRODUCTION DEAUTHORIZED
PERFORMANCE_BENCHMARK_ONLY_NOT_SCIENTIFIC_EVIDENCE
PENDING EXACT-HEAD IMPLEMENTATION REVIEW
```

## Objective and boundary

The Linux reference benchmark measured about 12 lattice steps/s on one logical CPU and projected
about 443 hours for P0–P2a. This tranche adds process-level concurrency across independent existing
reference-solver rows. It changes no solver kernel, backend, geometry, mask, forcing, convergence
setting, fixed-step target, tolerance, matrix row, case identity, scientific payload, control,
admission rule, decision rule, or claim ceiling.

This branch has empty solving and assembly allowlists and retains `POST_FREEZE_EXECUTOR_READY =
False`. No production phase or benchmark is authorized by implementation.

## Architecture

`jobs=1` remains the existing serial orchestrator and creates no pool. `jobs>1` selects
`PROCESS_POOL_V1`, using one `ProcessPoolExecutor` per solving phase with an explicit `spawn`
context. Workers receive canonical row tasks, reconstruct deterministic inputs, call the existing
guarded reference path, and return a strict internal result containing case ID, PID, monotonic
timing, payload or structured failure. They receive no runtime path and make no durable write.

The parent owns authority and predecessor validation, adaptive eligibility, readiness, exact resume,
official record construction and validation, diagnostic-envelope construction, canonical atomic
persistence, role-aware classification, phase state, manifest construction, and P2b assembly.

## Deterministic bounded waves

At each barrier the parent computes the complete ready set, in canonical matrix order, and dispatches
the first `min(jobs, ready)` rows. It waits for the whole wave, rejects malformed/duplicate/wrong-ID
results, then consumes results in canonical order. A fixed-step audit waits for its explicit
`audit_of_case_id`; an assurance replicate waits for `replicate_of_case_id`. No filename or wall
clock implies a dependency.

A stopping adjudicative or assurance failure prevents later waves. Already dispatched results are
collected and valid current-wave records are retained; never-dispatched rows receive the explicit
parallel-stop refusal. Overshoot is bounded by the remainder of one wave. Tau diagnostics retain
their frozen nonblocking role.

## Interruption, resume, and thread policy

The parent owns `SIGINT`, dispatches no later wave, cancels pending futures, shuts down the pool, and
writes neither partial records nor a fabricated manifest. Existing atomic records remain untouched.
Before dispatch, exact records are reopened through the canonical validator and reused with no worker
call; mismatches fail closed before dispatch. Accounting requires worker calls to equal newly
dispatched rows.

Before spawn and again in each worker, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, and `BLIS_NUM_THREADS` are set to `1` in the process
environment only. No persistent shell configuration changes.

Execution authority binds engine version, serial/process-pool mode, requested workers, `spawn`, the
thread-limit map, and scheduler policy. Worker count never enters a case ID, matrix row, candidate
identity, or scientific payload. Exact resume requires exact authority and therefore the same engine
configuration.

## Scaling corpus and review gate

The dormant module `rp_d_lc_001b_scaling_benchmark` is separate from production authority and writes
no production artifact. Its frozen corpus is 32 independent 600-step reference-blocked central-
forcing tasks: 16 at S=2 and 16 at S=3, tau-plus 2.0, check 200, and the production return fields.
Valid counts are 1, 4, 8, 16, and 32. It hashes compact deterministic outputs independently of
timing and task identity. The benchmark extraction uses the frozen P0 fixture-record semantics but
creates no P0 authority, record, or manifest. Its payload identity binds the benchmark schema,
reference backend, resolution, exact and runtime forcing, solver settings, return fields, compact
science, and mask while excluding task/case/source identity. The one-thread nested-library policy
is applied before the fixture and driver imports and reasserted at benchmark entry, including for
the jobs=1 baseline.

The harness must not run until the exact implementation head and tree are explicitly approved. A
source change after review requires a new review. Benchmark output must be a fresh absolute external
directory and is labelled `PERFORMANCE_BENCHMARK_ONLY_NOT_SCIENTIFIC_EVIDENCE`.

The accepted exact-head scaling run measured 3304.13, 1297.31, 1198.53, 1231.36, and 1286.03
seconds at jobs 1, 4, 8, 16, and 32. Every correctness gate passed. Under the frozen selection rule,
jobs=4 achieved `1198.53 / 1297.31 = 92.4%` of maximum throughput and is the smallest count above
90%. Therefore `RECOMMENDED_PRODUCTION_JOBS = 4`. Four is an explicit future command choice, not a
new default; execution authority binds the requested count. The benchmark is accepted and will not
be rerun for this integration tranche.

## Official production integration

The public source gates remain load-bearing and empty. If a later exact-head authorization admits a
pre-freeze solving phase, jobs=1 retains the existing serial orchestrator and jobs 2–32 enter the
official parent-only `PROCESS_POOL_V1` orchestrator. P2b remains single-process arithmetic and P3/P4
remain independently unavailable.

Workers receive a canonical ready row and its frozen audit plan when applicable, reconstruct the
reference fixture, call the unchanged guarded reference solver once, and return raw result fields
plus bounded PID/timing metadata. They receive no runtime path and make no authority, verdict,
manifest, persistence, candidate, or scientific-policy decision. The parent reconstructs geometry
and applies the same result contract, compact extraction, effective configuration, payload hash,
official record constructor, case validator, verdict, ledgers, aggregate science, assurance checks,
manifest constructor, and manifest validator used by serial execution. Exactly one durable writer
exists.

Complete deterministic waves are persisted in canonical order. A canonical stopping result blocks
all later waves; valid records from the already dispatched wave remain durable, while never-
dispatched rows receive `REFUSED_AFTER_PHASE_STOP`. Such bounded overshoot cannot alter a decision
after the first canonical stopping row. Exact records and diagnostic envelopes are reopened and
validated before dispatch; authority or jobs mismatch fails closed, and worker calls equal newly
persisted artifacts. Parent SIGINT closes the pool, writes no partial record or fabricated manifest,
and leaves existing atomic records exactly resumable. Parent-only progress lines after each wave
report case IDs, counts, failures, elapsed time, worker calls, and continuation state; telemetry
enters no scientific artifact or hash.

## Future Production Commissioning and Scientific Checkpoints

This is an execution plan, not a new scientific protocol. One invocation executes one named phase;
there is no automatic phase chaining.

### Checkpoint 0 — parallel production canary

After a later exact-head authorization, use a fresh external bundle and run P0 explicitly with
`--jobs 4` only until the Linux-baseline reference normal row and its fixed-step audit complete.
Send normal SIGINT, validate every complete record, and compare the pair with the serial baseline:
case IDs, compact science, applicable recomputed payload identity, status, audit target, and verdict.
Verify no duplicate/missing write, clean repository, and exact resume. A mismatch stops. No partial
P0 phase verdict is claimed.

### Checkpoint 1 — P0 completion

Resume the same bundle, complete P0 only, then stop. Require validated `PHASE_COMPLETE`, complete P0
aggregate science, passing forcing and S=2/S=3 consistency controls, passing decision-bearing rows
and assurance replicate, and valid authority/audit/manifest chain. Review observed jobs=4 throughput,
remaining-duration projection, numerical discrepancies, and explicitly non-adjudicative tau
diagnostics. Do not launch P1a until accepted.

### Checkpoint 2 — P1a completion

Run P1a only, then stop. Report terminal status, every candidate, central artifact point estimate,
point-budget verdict, represented resolutions, survivors/rejections and exact reasons, projected P1b
rows, and revised compute. P1a is triage-only and admits nothing; a frozen rejection cannot be
manually restored. If fewer than four candidates remain non-rejected, report that the frozen
four-slot endpoint is unreachable and stop before P1b without inventing another disposition.
Otherwise stop for a pragmatic continue/stop decision.

### Checkpoint 3 — P1b completion

After Checkpoint 2 approval, run P1b only and stop. For every candidate report complete artifact R
evidence, fixed-step/node-offset uncertainty, artifact upper bound, lateral mass-flux and pressure
verdicts, forcing/resolution verdicts, audit lineage, final eligibility, and exact rejection reason.
Report adaptive P2a rows and revised compute. If fewer than four pass, stop before P2a because the
four-slot endpoint cannot be filled.

### Checkpoint 4 — P2a and P2b

Only after Checkpoint 3 approval, execute and validate P2a, execute arithmetic-only P2b, and stop
with `SELECTED` or `DESIGN_BLOCKED`. Do not execute P3/P4. These are the only intended checkpoints;
there is no human stop after each case or wave.

## Non-goals

No CUDA, Taichi, GPU backend, MPI, Dask, Ray, distributed scheduling, worker writes, LB-kernel work,
vectorization, tuning, scientific rerun, protocol correction, P3/P4 enablement, or production
authorization belongs to this tranche.
