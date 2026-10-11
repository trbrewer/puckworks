# Remaining 010 qualification — stopped at independent-repeat crash

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The recovered anchor passed current admission. The one newly authorized
independent repeat then exited **SIGSEGV during integration**, before returning
a trajectory. Scientific expansion stopped: no retry, replacement, new anchor,
repeatability calculation or refinement was launched. This is a process failure,
not a measured numerical discrepancy or a demonstrated change in physics.

## Actual execution and preserved evidence

The live draft PR #333 head was verified as
`c18b8675d4563b58b77379a4c938ba06d4df300a`. An isolated working directory preserved
that head and owner work. The reviewed implementation is commit
`61bdcd89da1e235d93b1d7618adceb7735e3ed0c`; [REMAINING.json](REMAINING.json)
binds the immutable original matrix, current executable/source identities,
recovered-anchor receipts and exactly thirteen prospective non-anchor rows.
Its SHA256 is
`eb0d3f42cfb51cd62ab069d2e4c07ce3cd99ca145483605311684b79e4dc77e2`.

| Operation | Actual disposition |
|---|---|
| Current anchor byte-only check | All 28 members PASS; fresh isolated stdlib reader, exit 0 |
| Recovered-anchor adapter admission | Another fresh 28-member read, both saved bundles, support and actual admission identities PASS; exit 0, 44.166 s |
| Independent original repeat | One fresh integration attempted; process exit −11 after 114.408 s |
| Repeat archive, observations and audits | Unavailable; solver did not return a trajectory |
| Scientific-array/observation/mask repeatability | NOT_COMPUTABLE; no repeat payloads, differences or witnesses |
| Twelve refinements | NOT_RUN under the crash stop |

Repeat integration began at **2026-10-10 22:07:22.037415 UTC**. Its external
supervisor recorded PID 3205376 exiting −11 at **22:09:14.711396 UTC**.
Faulthandler retained `scipy/integrate/_ivp/bdf.py:227, solve_lu`, called by
`solve_bdf_system`, `_step_impl`, `step`, `solve_ivp`, `integrate` and `run_row`.
This locates execution when the signal occurred; the cause remains unresolved.
The three prior SIGSEGV incidents remain preserved and unresolved as well.

The repeat directory contains only `start.json` and `solver-start.json`.
There is no `solver-end.json`, checkpoint, provisional summary, prospective
capture commitment, archive, observation bundle or audit result for this repeat.
The accepted-state safeguard runs immediately after solver return; that point
was not reached. No last accepted time or completed internal segment count can
be recovered from these records. No successful end or capture record was invented.

The supervisor retained stderr, stdout, actual exit and one-second resource
samples outside the failed child. Sampled peak RSS was **706,612 KiB**; minimum
available memory was **259,521,003,520 bytes**, and minimum free disk was
**1,237,928,218,624 bytes**. `safety_stop: null` means the supervisor did not
terminate the process; the unexpected crash itself is the mandatory stop.
These samples do not diagnose the fault or establish environment health.

## Recovered-anchor science remains available

Current checks verified all 28 members against original prospective commitments
and verified the saved observation/diagnostic bundles. They did **not** repeat
anchor interpolation, quadrature or numerical audits. The results below reuse
the admitted [recovered-anchor results](BYTE_RECOVERY.md), with their original
scope and numerical limits.

| Original anchor gate | Retained result |
|---|---|
| Complete horizon | PASS, through t=8 |
| Required support | PASS, all 211 original times under availability rules |
| Conservation | PASS, independent maximum 4.0683758584236784e-9 at t=7.996908331931376; limit 1e-6 |
| Aqueous bounds | PASS; native minimum 0, maximum 1.0000000000000007 |
| Grain bounds | PASS; native minimum 4.164197798828082e-15 |
| Phase bounds | PASS; native inventory minimum 0 |
| Independent spatial inventory quadrature | PASS; maximum difference 1.3322676295501878e-15 |
| Boundary time quadrature | PASS; 3-vs-5 differences [6.938893903907228e-18, 1.7763568394002505e-15] |
| Boundary accumulator consistency | PASS; differences [1.2078574251894736e-10, 4.0039260795765585e-9] |
| Zero pre-drip cup | PASS |
| Transition continuity | PASS |

The smaller native accumulator balance, **5.240252676230739e-14**, remains
separate from independent boundary-flux integration. The available outlet evolves
from 1 at first drip to **0.01704354100746934** at t=8. Terminal liquid/fines/
boulder/dry inventories are respectively **0.0013439528036428632,
0.004465061000911067, 0.002135084223013909, 0**; terminal signed inlet/cup
integrals are **−0.05879587041145987, 5.485260031561004**.

Required liquid support has 35,612 available slots and 8,698 structurally
unavailable dry/zero-volume slots. Outlet support has 146 available values and
65 pre-drip unavailable values. Grain means, radial grain values, inventories
and integrals have all required values. Unavailable values retain the original
masks and conventions.

The original live-source comparison remains **UNAVAILABLE**. Admission uses the
previously reviewed equivalent frozen-BDF committed-coefficient assessment,
including direct polynomial evaluation at endpoints against this anchor's
accepted checkpoints. Its original failed write remains failed. Original work
counters and missing live-source observations remain unavailable. Restored bytes
and diagnostic replays are not independent scientific repeats.

## Outstanding qualification and accounting

All coarse/medium axial, fines, boulder, startup, temporal and combined refinement
rows remain NOT_RUN, in their original frozen order. Therefore refinement changes,
worst-change coordinates, convergence/trend assessments, temporal effectiveness,
combined and summed budgets, and refinement-based uncertainty are **not
computable**. Repeatability is unestablished, rather than a demonstrated array or
observation mismatch. No numerical threshold was changed or finite failure hidden.
Anchor observations and audits remain useful on their declared support; they do
not establish campaign qualification, a rigorous continuum bound or physical
validation.

Entering accounting was **three completed full trajectories / six completed
BDF segments**. This continuation reused one recovered anchor and made **one new,
interrupted repeat integration attempt**, with **zero new completed full
trajectories and zero additionally documented completed BDF segments**. Internal
progress before the crash is unavailable. The cumulative documented completion
count remains **three trajectories / six segments**. No refinement was executed.

## Software, review and reproduction

The narrow G0 adapter recognizes actual recovered admission records without
fabricating an ordinary original manifest, successful end, work counters or
live-source PASS. Exact comparisons include all scientific member identities and
all observation bytes/masks; provenance formats and receipt hashes are separate.
The runner preserves the original model, formulas, matrix, settings, support,
limits and error budgets. Original hash-guarded reproduction paths remain intact.

Affected controls: **22 PASS, 64 unchanged tests deselected, 2.70 s**, external
exit 0; lint and diff checks PASS. Two earlier fixture failures remain recorded:
an attempted exclusive-write reuse and an incomplete synthetic combined-axis
matrix. Correcting the fixtures did not loosen production assumptions. Scoped
review required and verified full archive checks before final qualification and
explicit rejection of nonfinite interpolant values before error reduction.
Pre-execution scoped review passed with no remaining finding. Unchanged
mathematical/recovery reviews and large diagnostics are reused under SCI-GOV-001.
Final exact-candidate CI and scoped-result review are separately identified in
the PR and external final delivery receipts; they do not resolve a crash cause.

[REMAINING_RESULTS.json](REMAINING_RESULTS.json) gives actual statuses, numerical
values, commands, accounting and key receipt SHA256 identities. Existing evidence
locators resolve `controlled-rerun-20261010/remaining-20261010`; `CAMPAIGN_STOP.json`
and the original external logs are retained there. The recorded command form is:

```bash
"$FULL010_PYTHON" -I -S -X faulthandler "$FULL010_EVIDENCE/supervise.py" \
  row-repeat "$FULL010_PYTHON" -I -S -X faulthandler \
  tools/run_grudeva2026_full_reference_010.py run --remaining \
  --archive-root "$FULL010_EVIDENCE/campaign" --row repeat
```

This documents the **already attempted** command, not authorization to retry it.
`admit-anchor` was run first with the same fault-enabled interpreter and explicit
binding. The existing supervisor supplies single-thread settings and the serial
execution lock. Byte checking stays in the stdlib-only child; scientific runtime
admission directly verifies the resolved interpreter, two dependency RECORDs,
their installed files and frozen BDF source, without broad metadata enumeration.
No dependency was installed and no resource limit or environment changed.

PR #333 remains draft/unmerged with auto-merge disabled; issue #67 remains open.
No EWP, production/default/lock, release, publication-rescoring or downstream
full-versus-reduced change. No additional forensic or hardware investigation.
