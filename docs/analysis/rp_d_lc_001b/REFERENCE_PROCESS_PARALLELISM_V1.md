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
timing and task identity.

The harness must not run until the exact implementation head and tree are explicitly approved. A
source change after review requires a new review. Benchmark output must be a fresh absolute external
directory and is labelled `PERFORMANCE_BENCHMARK_ONLY_NOT_SCIENTIFIC_EVIDENCE`.

## Non-goals

No CUDA, Taichi, GPU backend, MPI, Dask, Ray, distributed scheduling, worker writes, LB-kernel work,
vectorization, tuning, scientific rerun, protocol correction, P3/P4 enablement, or production
authorization belongs to this tranche.
