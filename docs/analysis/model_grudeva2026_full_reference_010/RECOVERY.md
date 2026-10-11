# Retained-anchor recovery — 010

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The owner authorized inspection and recovery of the completed anchor on reviewed
head `6a241e5578426c10ff5609e85a637ff92f64eed3`, with no new anchor. Current
checkpoint and partial-file reads passed against their **pre-existing**
commitments. Twenty-four of 28 numeric archive members are now available in an
exclusive partial-recovery directory. Four essential segment-1 dense members
are absent, so no full archive is admitted and no repeat/refinement is launched.

## Member-level finding

The bound writer inserts geometry first, then each segment in this order:
`D, shift, denom, order, t, y, concentrations, boundary_accumulators,
physical_z_faces, physical_z_centers`. All segment-0 members are retained;
no segment-1 archive member is retained. The traceback points to the pre-write
source check. Thus **`segment-1-D.npy` is the first unwritten member and the
order-inferred rejected member**, not an original filename-bearing witness.
Its committed shape is `[18002, 6, 24834]`, dtype `<f8`.

The old combined exception cannot retrospectively distinguish identity mismatch
from nonfiniteness: the original live segment-1 coefficient buffer no longer
exists and no copy of that member was retained. No cause or nonfinite count is
invented. A digest does not recover its source bytes.

| Expected members | Original retained state | Recovery result |
|---|---|---|
| Eight geometry arrays | Present, verified, finite | Reused |
| All ten segment-0 arrays | Present, verified, finite | Reused |
| Segment-1 `t`, `y` | Archive paths missing; original checkpoints present and verified | Reused from those checkpoints |
| Segment-1 concentrations, boundary accumulators, physical faces/centers | Missing; deterministically derivable | Regenerated with unchanged formulas; all four match their original prospective hashes exactly |
| Segment-1 `D`, `shift`, `denom`, `order` | Missing | Essential solver information unavailable; not reconstructed |
| Present mismatched/nonfinite numeric members | None observed in current inspection | No replacement or checksum repair |

The reused members are hardlinks, explicitly the **same underlying files**, not
independent backups. No original payload was modified in place. The recovery
receipt connects every reused/derived member to the original trajectory
`SOURCE_COMMITMENT.json`, and connects accepted states to their original
checkpoint manifest, prospective identities and readback receipt. A new process
revalidated all 24 recovered members. No successful trajectory manifest exists.

Case/settings, segment success/motion/counts and execution identity are supported
by retained records. Original successful-capture dense-chain/per-piece receipts,
work counters and the original-live-interpolant comparison were not separately
persisted. They are unavailable; no equivalent replacement verification or PASS
is asserted. Missing segment-1 coefficients also prevent the required full
observation support, full-horizon independent flux audit and final qualification.

## Numerical information retained

**PROVISIONAL — NOT FULL_REFERENCE_QUALIFICATION**

Both accepted checkpoints revalidated before use, with 25,829 entries (t=1
appears in both segments). Recomputed provisional values reconcile exactly with
the earlier summary (zero evaluation-allowance fraction). The native aqueous
range remains 0 to 1.0000000000000007, grain range
4.164197798828082e-15 to 1.3881944087925513, and minimum inventory 0.
The accumulator-based balance residual remains 5.240252676230739e-14.
That small residual does not substitute for independent flux integration.

Independent Gaussian **spatial inventory** quadrature was computed for every
accepted entry using the unchanged routine. Maximum difference from model phase
inventories is **1.3322676295501878e-15**, at t=0.785601637834479 in the fines
inventory, within the original `1e-11 * max(1, M0)` limit. At t=8 the independently
computed liquid/fines/boulder/dry inventories are
`0.001343952803642863 / 0.004465061000911067 / 0.002135084223013909 / 0`.
Terminal outlet concentration remains **0.01704354100746934**. Spatial inventory
quadrature is not time integration of boundary flux.

Verified original segment-0 coefficients support the existing observer and
3-/5-point boundary quadrature through first drip, including the unchanged
startup contribution. These are diagnostic calculations with the original
live-interpolant fidelity check still unavailable:

| Scoped quantity, through t=1 only | Result | Unchanged limit |
|---|---:|---:|
| Independent balance, maximum absolute residual | 1.2078515965185943e-10 | 1e-6 |
| Inlet quadrature, 3 versus 5 points | 6.938893903907228e-18 | 2e-7 |
| Inlet quadrature versus evolved accumulator | 1.2078574251894736e-10 | 2e-7 |
| Cup quadrature differences | 0 | 2e-7 |

All these scoped checks pass; none is a full-horizon gate result. The independently
integrated inlet/cup totals at first drip are `-0.05842142441975782 / 0`.
There is no time-flux audit for t>1 and no full conservation conclusion.

The original observation coordinates are unchanged. Sixty-six of 211 required
times through t=1 were evaluated using retained segment-0 data; t=8 was evaluated
as an exact accepted state, without interpolation. Thus **67 times have diagnostic
observations; 144 later arbitrary times lack required dense support**. Accepted
states throughout t<=8 remain available, but are not arbitrary-time observations.
The earlier segment-0-only count of 145 unprocessed later times is clarified in
the availability receipt by this separately computed exact endpoint. All numeric
bundles passed fresh-process validation. Refinements, repeatability, full error
budgets and uncertainty qualification remain NOT_RUN/unestablished.

## Narrow correction and verification

`write_numeric` now evaluates identity and finiteness independently, including
simultaneous failures and check errors. Its structured failure records exact
path/member/group, expected/observed shape/dtype/hash and both outcomes. The
runner persists the primary failure before optional nonfinite count/location and
bounded byte/numeric witnesses. Secondary diagnostic failures cannot replace the
primary failure. Hash semantics, admission requirements and tolerances are unchanged.

Fifteen targeted writer controls passed. The broader affected selection had 51
passes and **two child SIGSEGV exits** in existing solver-free failure fixtures.
Their artifacts/logs remain preserved; the two cases passed once with Python's
fault handler enabled and otherwise unchanged code/environment. Their cause is
unestablished. The corrected UTC-scoped kernel query confirms those same crashes;
passing later checks do not resolve them or certify environment health.

One post-processing wrapper error passed a `moving` metadata key to an arrays-only
validator. Its failure and original script were retained. The corrected call
resumed from revalidated saved members; no integration or derived-member rewrite
was performed. A journal query initially omitted UTC; its incorrect interval
interpretation is explicitly superseded, while both records remain retained.

Unchanged mathematical review and large diagnostics are reused. The exact final
candidate's required CI and scoped independent nonhuman review are reported in
PR #333 and the external delivery receipt, without a receipt-only commit loop.

## Reproduction and identities

[Machine-readable transition, inventory and evidence hashes](RECOVERY.json).
The existing evidence configuration resolves `controlled-rerun-20261010`; this
continuation writes only its exclusive `recovery-20261010` child. Original MATRIX,
RERUN/CONTINUATION bindings and all 53 prior 010 documents remain unchanged.

The retained `inspect_retained.py` uses the original reviewed implementation and
verifies the bound evidence path, old compact index, checkpoint lineage and every
present member. `recover_partial.py` records the initial partial-member recovery;
its wrapper failure is retained. `postprocess_resume.py` records the corrected
post-processing and fresh-reader path. Scripts and their executed implementation
hashes are preserved externally. Existing output paths are exclusive: inspect
receipts rather than rerunning writers over them. To reproduce in another fresh
directory, preserve the original input locators/commitments, redirect only outputs,
and use the recorded implementation/executable with:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. \
  "$FULL010_PYTHON" <retained-inspection-or-postprocessing-script>
```

The exact endpoint observation uses the unchanged `observe` routine only at
original required times that compare exactly equal to accepted segment-1 times;
here that set is `[8.0]`. Its executed command text, including the fresh-reader
subprocess, was retained after execution as `accepted_common_executed.py`; no
prospective script-hash claim is made for that command. No missing state/coefficient, replacement interpolator,
different execution's data or D[0]-for-y substitution is permitted.

Recovery adds **zero solver executions**. Cumulative accounting remains **three
completed full trajectories / six BDF segments; zero admitted full reference
rows**. Repeat and twelve refinements remain NOT_RUN. PR #333 stays draft and
unmerged, auto-merge disabled, #67 open. No EWP/production/default/lock change,
hardware/transfer investigation, downstream comparison or automatic new anchor.
**EXECUTION_ENVIRONMENT_INTEGRITY_UNRESOLVED. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
