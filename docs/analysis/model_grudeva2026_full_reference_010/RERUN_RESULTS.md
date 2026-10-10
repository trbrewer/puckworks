# Controlled rerun result — 010

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The owner-authorized fresh anchor completed its solver and preserved accepted-state checkpoints and provisional science before dense capture. The archive writer then stopped at its existing pre-write source check: `ValueError: Source commitment mismatch or nonfinite source`. No full trajectory manifest was published. The repeat and twelve remaining refinements were **NOT_RUN**. No retry, new diagnostic sequence, downstream comparison or publication rescoring followed.

The combined error does not distinguish a source-identity mismatch from a nonfinite array, and does not identify the member or a mechanism. The stage/traceback, source commitments, partial archive and early checkpoints remain external. This ValueError does not produce the separate CaptureMismatch quarantine witnesses; no additional witness was invented.

## Preserved numerical information

**PROVISIONAL — NOT FULL_REFERENCE_QUALIFICATION**

Two successful BDF segments reached t=1 and t=8, with 7,826 and 18,003 accepted entries (25,829 total; t=1 occurs twice). The fresh checkpoint reader verified exact accepted t/y payloads before dense capture. The following values were computed from those checkpoints using the existing inventory and boundary routines. They are diagnostic evidence, not an admitted full reference.

- Maximum accepted-state accumulator-based balance residual: **5.240252676230739e-14** normalized mass. This is not the required independent final flux/quadrature conservation audit.
- Native aqueous range: **0 to 1.0000000000000007**. Native grain range: **4.164197798828082e-15 to 1.3881944087925513**. Minimum phase inventory: **0**. These native values lie within the existing bounds; full required-observation bounds remain unassessed. There is no imposed grain upper cap.
- At t=8, signed inlet accumulator is **-0.05879587041145987**, cup accumulator **5.485260031561004**, and remaining liquid/fines/boulder inventories are **0.0013439528036428632 / 0.004465061000911067 / 0.002135084223013909**. Dry inventory is zero.

Concentrations are saturation ratios; inventories and boundary accumulators use the contract's normalized mass units, with initial inventory M0=5.552. Negative inlet flux/integral denotes loss through the inlet. The sampled evolution below uses actual accepted times, without interpolation or substituted values.

| Accepted t | Outlet | Liquid inventory | Fines inventory | Boulder inventory | Dry inventory |
|---:|---:|---:|---:|---:|---:|
| 0.105546554 | unavailable | 0.0819628369 | 0.353212044 | 0.110179176 | 4.96600553 |
| 0.536413078 | unavailable | 0.447732956 | 1.9468569 | 0.527063352 | 2.57383459 |
| 1 | 1 | 0.842699232 | 3.6870443 | 0.963835046 | 0 |
| 2.01564545 | 1 | 0.690163899 | 2.99623105 | 0.791171831 | 0 |
| 4.02940288 | 1 | 0.384654078 | 1.62962306 | 0.449524119 | 0 |
| 6.00640557 | 0.975572462 | 0.0836925829 | 0.29026745 | 0.1143737 | 0 |
| 8 | 0.017043541 | 0.0013439528 | 0.004465061 | 0.00213508422 | 0 |

Wet phase inventories grow while the front advances. Following full wetting, the sampled inventories decline; outlet concentration remains near one through t≈4, is about 0.976 at t≈6, then falls to 0.01704 at t=8. The complete early summary retains 82 samples plus extrema over every accepted entry. This description establishes neither continuum accuracy nor physical validity.

## Integrity, missing requirements and accounting

Checkpoint readback passed at the recorded boundary. Dense capture returned without an exception. Archive writing failed before the full reader, interpolant audit, common observations and independent flux audit could run. Thus no complete archive, final conservation gate, required observation-support gate or full numerical qualification is admitted. Repeatability, individual/combined refinements and uncertainty remain unestablished. Finite tolerances were not changed or reinterpreted; the continuation stopped on the source-admission failure.

Historical accounting remains **two previous full trajectories / four previous BDF segments**. This attempt adds **one separate solver-complete anchor / two BDF segments**. The cumulative solver-complete total is therefore **three trajectories / six segments**, with zero admitted full reference rows. The repeat is unexecuted, not replaced by the new anchor.

The supervisor reports no safety stop: minimum available memory was 190,899,798,016 bytes and minimum free disk was 1,241,497,530,368 bytes. Accessible kernel evidence showed no new uncorrected hardware or I/O error. Denied dmesg access, old CPU-frequency-driver startup errors and unresolved historical environment concerns remain disclosed. Matching checkpoint reads are evidence for the declared boundary only, not hardware-health certification. SciPy Jacobian-step overflow/invalid warnings remain in the log; solver completion and accepted-state finiteness were separately checked.

## Reproduction, QA and delivery

[Rerun binding](RERUN.json) · [Reproduction](RERUN_REPRODUCE.md) · [Machine-readable result and evidence identities](RERUN_RESULTS.json) · [QA receipt](RERUN_QA.json). The original MATRIX, all 48 preceding 010 documents and all historical failure outcomes remain unchanged. The equations/case/settings/support/limits/error budget and mathematical review are reused by exact identities.

Only three implementation files changed: checkpoint/archive I/O, the existing runner and its affected tests. The final focused run passed 60 tests, including the existing paired capture/no-capture fixture through t=1.01 with unchanged accepted times and states. Unchanged large diagnostics were reused. The initial ordinary suite had 6,535 passes, 67 skips and two invocation failures; both affected tests passed with the checkout supplied on PYTHONPATH, without code/dependency changes. The initial failure records remain retained. Exact candidate hosted CI and the final scoped independent nonhuman review are reported in PR #333; historical receipts are not presented as certification of the new candidate.

PR #333 remains draft and unmerged, auto-merge disabled; #67 remains open. No EWP, production, default, lock, governing-physics or dependency change. No automatic successor or recommendation for another trajectory follows this stop.
