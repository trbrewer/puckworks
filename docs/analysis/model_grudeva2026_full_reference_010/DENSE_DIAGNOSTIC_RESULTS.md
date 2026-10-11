# 010 dense-capture diagnostic and handoff

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE.** Both declared solver-free resident
dense-capture replays pass with identical capture records. A new source-to-file
byte discrepancy was independently observed during input extraction and remains
unexplained. **No new full-case scientific trajectory or matrix row ran.**
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Separate findings

| Question | Result |
|---|---|
| Historical archive root cause | HISTORICAL_ROOT_CAUSE_UNESTABLISHED; previous 19-entry diagnosis reused, not repeated |
| Replacement capture mechanism | UNESTABLISHED; missing historical digests/operands/states cannot be recovered from this diagnostic |
| Demonstrated software defect | Information-losing short-circuit/exception path corrected; no numerical-method or commitment-arithmetic defect demonstrated |
| Commitment/checker correctness | PASS on independent bounded canonical references and the two declared resident workloads |
| Durable failure witnesses | PASS on source-only, target-only, simultaneous, metadata/order/padding, checker-only, write-failure and process-exit controls |
| Representative dense capture | PASS_ON_DECLARED_DIAGNOSTIC_WORKLOADS; exact fresh-process capture-record repeat |
| New extraction integrity | FAILED: original member matches its producer identity; extracted copy differs at 54 bytes/54 float entries; mechanism UNESTABLISHED |
| Numerical/reference qualification | INCOMPLETE; zero audited/qualified full rows and all full-case precision/uncertainty gates unavailable |
| Software QA, hosted CI, independent review | Separate exact-candidate receipts; old-head CI is not new-head evidence |

## Actual workload and outcome

Original individually committed dense coefficients, times, orders, shifts and
denominators supply 7,825 and 18,002 intervals with 24,834 state variables. The
actual capture path allocates padded targets `(7825,6,24834)` and
`(18002,6,24834)`, totaling **30,786,610,464 bytes**. Both segments' source pieces
are resident, independently owned and writable; segment 0's capture remains
resident while segment 1 is captured. The source dense arrays occupy
23,457,486,800 bytes at their actual variable orders. Synthetic accepted-state
buffers reproduce the inspected F-contiguous/view layout, not original y values.
Neither solve_ivp nor the full-case integrator is called.

| Execution | Supervisor seconds | Sampled peak RSS (KiB) | Minimum available memory (bytes) | Exit |
|---|---:|---:|---:|---:|
| Primary | 208.4094 | 63,266,952 | 194,594,140,160 | 0 |
| Fresh process | 208.4086 | 63,267,596 | 194,419,675,136 | 0 |

Both completed capture records have SHA256
`306322854dd2e5630a713da9cd6177fe95792bc32b10ca94037f9c91102afd96`.
This includes per-piece prospective commitments and all completed-source/target
checks. Their full canonical `t/D/shift/denom/order` identities also match the
original individually verified inputs. This is exact diagnostic copying and
repeatability, not numerical evaluation of interpolants or the scientific repeat
row. D[0] is never used as an exact accepted-state oracle.

The frozen environment is unchanged. The installed SciPy source and one bounded
existing fixture confirm owned C-order dense pieces and F-contiguous non-owning
accepted y. Source mappings are used only during preparation, then released;
capture is not a streamed or memory-mapped substitute. Solver/Jacobian/history
allocation lifetimes and the replacement's lost coefficient values are not
reproduced. No resource-safety stop, resource purchase, administrative change,
hardware stress campaign or machine/dependency change occurred. Accessible
kernel records returned no entries; this is not a hardware-health certificate.

## New input failure and bounded amendment

The prospective plan first extracted ten original numeric members into exclusive
diagnostic inputs. Nine verified; post-wetting D failed before any resident
replay. This failure and the extracted file remain preserved. One targeted
independent raw ZIP/copy comparison then found:

- Original D payload: `dde6342fe349b2c33890c66d8316c2535f993121fcddeee4cc1b58a08292ae3a`, matching the producer.
- Extracted D payload: `e461a67c1e5e347dbd57c2440fa332280b11b376399e1fb7c900624b2bdb64ca`.
- Same shape `(18002,6,24834)`, dtype `<f8`, C ordering; 54 differing bytes/entries.
- First witness: segment 1, D index `[12071,1,8521]`, interval
  `[4.536169207907627,4.536423337469096]`; payload byte `14389285115`.
  Source float bytes `c5433771aa48bcbe`; copy `c5433733aa48bcbe`.

The first 32 exact witnesses are retained in JSON and safely loaded numeric NPZ;
both complete payloads remain available. Offsets describe serialized payloads,
not process-memory or physical-memory addresses. This is an observed byte
disagreement, not a diagnosis of hardware, storage, NumPy or a shared historical
mechanism. The comparison does not establish when or how the bytes changed.

[DENSE_DIAGNOSTIC_AMENDMENT.json](DENSE_DIAGNOSTIC_AMENDMENT.json) was bound
before either resident replay. It preserves the original failed plan/extraction,
uses nine read-only verified input files, and directly decodes/verifies the
original segment-1 D member. The additional 21.46 GB preparation buffer is
released before capture. No bad-copy repair, new extraction write or blind retry
was performed. The two originally unexecuted replays then ran once each.

Independent review identified a replay-only final-check evidence gap. Its bounded
correction retains available input/target witnesses, per-piece records and checked
snapshots; direct-ZIP witnesses use bounded streaming instead of another whole
dense-array copy. An extraction mismatch now also records expected/observed
identities explicitly. The replay-final-check correction has focused negative
controls; no additional large extraction retry was run.

After the passing replays, review identified a secondary witness-read error that
could conceal an already detected final-input mismatch. The delivery corrects
only that failure branch and adds two negative controls. All 16 solver-free
diagnostic tests pass. [Delivery identities and scoped reuse](DENSE_DIAGNOSTIC_DELIVERY.json)
preserve the executed replay hashes and demonstrate unchanged code outside that
branch; no large workload was repeated or silently rebound to the new code.

## Preservation and accounting

Capture now records all three commitments independently, with per-piece
prospective metadata. `CaptureMismatch` carries diagnostic context and bounded
source/target pairs to the runner. Essential failure JSON is written before safe
numeric witnesses and already checked t/y snapshots; secondary failures remain
explicit and do not replace the original exception. Quarantine is never admitted
by the qualified-reference loader. Current-buffer agreement is not presented as
proof that prior bytes were unchanged.

Scientific accounting remains **two historical full trajectories / four BDF
segments; zero new full trajectories; zero reused full trajectories; zero
audited/qualified full rows; thirteen frozen rows NOT_RUN**. Diagnostic executions:
one failed extraction, one targeted source/copy comparison, two successful
resident replays, zero diagnostic integrators. Old large serialization tests and
old full-case campaigns were not rerun.

Five focused invocations are retained: 65 passes/one test-hook signature failure,
then 66 passes, then 13, 14 and 16 solver-free passes after the replay evidence-path
corrections. The first failure was an injection-hook calling-convention mismatch,
corrected without changing the scientific method. The first two invocations use
34 bounded trajectories/38 segments in total; layout inspection adds 1/2.
The ordinary quick suite passes 6,496 tests (67 skipped, 64 deselected);
78 documentation regressions, static/generated/registered checks and packaging
pass. The final failure-only correction additionally passes all 16 solver-free
controls. [QA and fixture accounting](DENSE_DIAGNOSTIC_QA.json) distinguish the
quick collection version, final bounded controls and later exact-head hosted CI.
Local 010 ordinary fixtures total 50 trajectories/55 segments; hosted counts are
recorded separately in delivery receipts. An initial unused-import Ruff finding was corrected and retained in
the development accounting. No failure is silently relabelled a pass.

## Identity, scope and recommendation

Selected base `3cd308ac5bed39acff3d995108b5178a53c982ee`, tree
`96ad0b033c070a99416209828b5780034f438dba`; starting head
`ab23c050ba359a984e6106fb25d1073d81911386`, tree
`797f3c0cf78ca4e0746506c5806ac808958fd223`. Exact delivery head/tree and hosted
receipts are recorded in PR #333 and the external diagnostic closeout.

Original matrix SHA256 remains
`092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3`;
CONTINUATION.json remains
`64d92c5f87c46fad02aa7a2c078b7c473492d04d2d9296d12044af529c333b0a`.
All 30 preceding 010 documents and 206 historical scientific-file hashes match.
The new [machine-readable result](DENSE_DIAGNOSTIC_RESULTS.json),
[external evidence manifest](DENSE_DIAGNOSTIC_EXTERNAL_EVIDENCE.json),
[prospective plan](DENSE_DIAGNOSTIC_PLAN.json), amendment and
[reproduction instructions](DENSE_DIAGNOSTIC_REPRODUCE.md) bind the diagnostic
inputs, code/environment, failures, resource records and limits.

Changed scope: 010 I/O/capture and runner error handling, focused tests, one
solver-free diagnostic command, compact diagnostic records and narrow living
status/navigation. The mathematical contract and review, solver, case, settings,
support, thresholds, budgets, production/defaults/locks, historical 001–009,
source cards, October 9 review and read-only EWP remain unchanged.

**Recommendation: not yet another instrumented anchor.** The resident replay
supports the tested capture/checker implementation, but the newly observed
source-to-file discrepancy remains unresolved. Its evidence/infrastructure
disposition should precede any separately authorized scientific execution. No
anchor, matrix row, downstream comparison or automatic successor is authorized
or launched here. Keep PR #333 draft/unmerged, auto-merge disabled and issue #67
open. FULL_REFERENCE_QUALIFICATION_INCOMPLETE; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
