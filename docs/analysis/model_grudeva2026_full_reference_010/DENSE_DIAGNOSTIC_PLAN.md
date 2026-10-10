# 010 dense-capture diagnostic plan (prospective)

Same G2 task and draft PR #333. ZERO new full-case trajectories or matrix rows
are authorized. Original MATRIX.json, CONTINUATION.json and both historical
failure bundles remain immutable. FULL_REFERENCE_QUALIFICATION_INCOMPLETE;
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The diagnosed defect is loss of failure evidence: a short-circuit combined
comparison can omit the completed-target pass and retains neither operand
digests nor per-piece commitments. It does not establish the mechanism of the
replacement failure. Historical 19-entry diagnosis is reused without repetition;
HISTORICAL_ROOT_CAUSE_UNESTABLISHED. Replacement mechanism: UNESTABLISHED.

The changed capture path independently records prospective, source-after and
completed-target commitments; keeps per-piece commitments and metadata; and
raises a structured, neutrally labelled mismatch. The runner writes its essential
failure record first, then a separate quarantine containing the full commitment
record, up to eight bounded source/target witnesses and independently checked
accepted t/y snapshots. A current-buffer byte comparison is distinguished from
comparison with prior bytes. Missing prior bytes are not invented. Secondary
write failures are reported without replacing the original exception. Quarantine
never contains a successful reference manifest. No archive-format migration.

## Inputs and finite executions

One read-only diagnostic extraction of original segment 0/1 `t`, `order`,
`D`, `shift` and `denom`; verify all ten individual producer identities using
the extracted raw NPY payload. Original manifest SHA256:
`e78201cceb99c773ccbe7d2d3359841d939c39734d99c03775b62569722d290e`.
These coefficients previously matched their individual identities. Their parent
archive remains FAILED/QUARANTINED. No accepted-state recovery or numerical
admission follows. The failed y and redundant concentrations are not read.

Execute precisely one primary resident replay and one fresh-process replay of
the same inputs. Both call the real `capture`/`capture_dense` path, including
per-piece copy, final source pass, completed-target pass and exact padding checks.
No solve_ivp, full-case integrator, observation audit or interpolant evaluation.
The command disables integrator entry points in its process. No scientific hash
guard is removed; this is a separate diagnostic command, not a campaign bypass.

Input NPY mappings are used only to reconstruct each source piece into an owned,
writable C-order resident allocation. Close the mappings before capture. Retain
both source segments concurrently and retain segment 0's completed capture during
segment 1 capture. Exact source orders/coefficients/shifts/denominators/times come
from the individually verified inputs. Padded target shapes are
`(7825,6,24834)` and `(18002,6,24834)`: 9,327,650,400 and 21,458,960,064 bytes.
All source-piece orders present are reported. Bounded controls exercise orders
1–5, padding, C/transpose/strided layouts and signed zero.

Accepted-state buffers are explicitly synthetic finite values:
`base[k,i]=i/32768+(k+1)/1048576`, `base[0,0]=-0`, `y=base.T`.
This reproduces the inspected SciPy F-contiguous, non-owning y layout without
claiming exact solver states or using D[0] as an oracle. Shapes are
`(24834,7826)` and `(24834,18003)`. Times and source dense pieces are owned and
writable as observed in the installed hash-bound SciPy and the one existing
bounded fixture used for layout inspection. The fixture's one trajectory/two
BDF segments is ordinary QA, separate from solver-free replay.

## Memory, environment and checks

Preserve Python/NumPy/SciPy/BDF/thread identities from the frozen environment.
The accompanying DENSE_DIAGNOSTIC_PLAN.json binds exact implementation hashes,
environment, unchanged scientific identities and execution plan before extraction
or large replay. It is not a new scientific continuation binding.

Resident upper estimate: source dense pieces <=30.79 GB, source accepted buffers
5.14 GB, captured dense targets 30.79 GB, captured accepted buffers 5.14 GB;
small times/shifts/denominators, Python records and bounded hashing scratch add
overhead. Input file page cache may coexist and is reclaimable. No solver history,
Jacobian, solver allocator lifetime or entire original integration is reproduced.
Reserve 160 GiB actually available memory and 80 GiB disk before starting; these
are conservative admission estimates, not measured peaks. Inspect host/cgroup
limits and monitor RSS, available memory and disk each second. A real critical
headroom condition (<2 GiB) stops the owned child; no wall-time quota, resource
expansion, machine/dependency change or administrative action.

Passing requires exact source/target commitments, metadata and padding on both
segments and matching primary/replay canonical identities. Preserve compact
per-piece commitments, start/end/resource records, all failures and safe numeric
witnesses. No multi-gigabyte target archive is written on pass. On mismatch,
preserve/localize first; one smallest useful reproducer and a correction are
permitted only for a demonstrated defect, followed by affected controls and the
relevant declared replay. No repeated blind retries. An unresolved environment
integrity observation is separate from mathematics and does not authorize a solve.

If both replays pass: PASS_ON_DECLARED_DIAGNOSTIC_WORKLOADS, with both earlier
mechanisms still unestablished. This is evidence for considering a separately
authorized instrumented anchor, never a guarantee or authorization to run one.
The passing old 3.58 GB / 4 GiB serialization controls are reused at their
original identities and are not repeated as substitutes for dense capture.
