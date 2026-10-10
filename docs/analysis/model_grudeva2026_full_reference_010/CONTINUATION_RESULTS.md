# 010 continuation results

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE**

PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is the unchanged single synthetic finite-rate case, with an independently identified replacement anchor. The historical failed attempt remains incomplete; its root cause is unestablished.

New execution: **1 trajectory started; 1 completed; 0 audited rows**. Original execution remains one completed trajectory/two BDF segments, zero audited or qualified rows. No full trajectory was recovered or reused. The frozen matrix and all numerical limits are unchanged.

## Row dispositions

| Row | Solver | Archive | Observations | Numerical row gates |
|---|---|---|---|---|
| anchor | COMPLETE | FAILED_BEFORE_PUBLICATION | UNAVAILABLE_CAPTURE_PREREQUISITE | NOT_AUDITED |
| axial_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| axial_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| fines_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| fines_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| boulders_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| boulders_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| startup_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| startup_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| time_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| time_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| combined_coarse | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| combined_medium | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |
| repeat | NOT_RUN | NOT_RUN | UNAVAILABLE | UNAVAILABLE |

## Exact stopping point

Both BDF segments reached their requested endpoints (7,826 and 18,003 accepted
entries). Capture then raised `Dense source/target mutation after an earlier
capture copy`. The combined dense-chain check failed **before serialization**;
no replacement trajectory arrays or successful archive manifest were produced.
The process returned exit code 1, and the supervisor stopped before axial_coarse.
There was no machine-safety stop: peak sampled RSS was 67,069,992 KiB and minimum
available memory was 190,566,535,168 bytes.

The receipt does not retain the compared digest values or distinguish which of
the combined source-after/target comparisons failed. Those in-memory states did
not survive process exit. This limits diagnosis; it is not evidence identifying
a hardware mechanism or a demonstrated numerical-method defect. The new failure
mechanism remains UNESTABLISHED. No second replacement, format cycle, environment
change or further full simulation was attempted.

This is a capture-integrity failure, **not a numerical gate failure**. Required
conservation, bounds, state inventories, boundary integrals, reconstruction,
refinement, repeatability, temporal-effectiveness and combined-budget metrics
are unavailable. No numerical worst-case coordinate or uncertainty estimate can
be reported. No full-case output-specific precision claim is earned.

## Required observation support

| Observable | Requested | Required support | Structurally absent | Qualified available |
|---|---:|---:|---:|---:|
| liquid | 44310 | 35612 | 8698 | 0 |
| outlet | 211 | 146 | 65 | 0 |
| grain_means | 88620 | 88620 | 0 | 0 |
| grain_radial | 1240680 | 1240680 | 0 | 0 |
| inventories | 844 | 844 | 0 | 0 |
| integrals | 422 | 422 | 0 | 0 |

Dry liquid/zero wetted volume and pre-drip beverage concentration explain the
structurally absent entries. Every required supported entry is unavailable
because capture failed; none passes by omission. The four-column boundary-flux
support and fixed-position history subsets are likewise unavailable and counted
in the JSON.

## Qualified partial capability

The 54 focused controls and the one solver-free large serialization test pass.
The fixed-settings end-to-end fixture preserves its numerical trajectory exactly
through capture, write, safe reload and observation/audit. These qualify their
small/control workloads only. The full-scale capture failed, so neither a
reusable full-reference archive nor full-case numerical qualification is earned.
The original historical failure and all its evidence remain unchanged.

## Evidence and reproduction

[CONTINUATION_RESULTS.json](CONTINUATION_RESULTS.json) records the exact failure, execution counts/settings, support counts, and explicitly unavailable numerical gates, extrema, witnesses and refinement diagnostics. [Diagnosis](CONTINUATION_DIAGNOSIS.md), [controls](CONTINUATION_CONTROLS.json), [binding](CONTINUATION.json), [pre-execution review](CONTINUATION_PRE_REVIEW.json), and [reproduction](CONTINUATION_REPRODUCE.md) separate historical failure, capture integrity and scientific qualification. Final QA, archive identities and independent review are recorded separately in the continuation handoff.

Issue #67 stays open. PR #333 stays draft and unmerged, with auto-merge disabled. No automatic successor or downstream full-versus-reduced comparison. CORROBORATED_PUBLICATION_DISCREPANCY and FIG5_REFERENCE_INCOMPLETE are unchanged.
