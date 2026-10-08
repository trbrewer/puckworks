# 005 results after the owner persistence amendment

**OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED.**
G1 / NO_GOVERNING_PHYSICS_CHANGE; bounded G0 persistence/identity/failure-reporting
correction. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The corrective full combined capture is trustworthy on its declared persistence,
array-fidelity and replay checks, and its complete observation passes all 22
individual gates. The subsequent normal run also captures and replays completely,
but its diagnostic inlet error at t=.2,z=0 is **2.046100506994386e-5 > 2e-5**.
The unchanged reporter classifies that endpoint check as an observer failure.
Normal/combined grain profiles and fixed-z histories also exceed their inherited
refinement allowances. These are retained discrepancies, without a governing-
physics or production-solver defect attribution while observer qualification and
real-run neutrality remain unresolved. No reconstruction or threshold changed.

Execution stopped after normal. The control, observed repeat, bed_fine,
modes_fine and time_fine were not run. Their unavailable evidence cannot pass.
A same-environment exact complete public-Result comparison between the new combined
capture and the historical failed probe passes; it is repeat consistency, not the
missing normal observed/unobserved neutrality pair. REDUCED-001 and 004 conclusions
remain unchanged. No production-versus-004 comparison or publication rescore.

## Historical evidence and demonstrated persistence defect

The original 2 GiB pilot failure remains resource evidence only. The successful
8 GiB short pilot and failed full combined capture remain separate immutable
attempts. The latter's public Result was COMPLETED, with three returns, but its
third expected file hash and live replay metadata were discarded when Segment
raised and execute retained only an error string. That loss of diagnostic evidence
is the demonstrated implementation defect corrected here.

The bounded archive check found the first two files equal to their original
hashes and readable. Segment 3's surviving arrays span [6.504306141250696,8];
D_97.npy raises a CRC-32 error. Existing SHA-256 and independent sha256sum agree
on every current file; size/inode/device/mtime/ctime were stable during inspection.
The third current hash matches the previously recorded post-failure inventory
hash, which never becomes an expected capture binding. Missing original hash,
pre-failure reference arrays and live replay receipt make recovery **INELIGIBLE**.
Duplicate filename, overwrite, path mismatch or incomplete write is not demonstrated.
Historical mismatch root cause: **UNRESOLVED**. The first diagnosis invocation
stopped at CRC before writing its summary; its failure remains charged. A bounded
completion retained the per-file/member findings; no further hash-search ladder.

## Corrected path and exact scientific preservation

Expected named-array dtype/shape/content manifests are retained before writing.
The NPZ is finalized and fsynced in the same directory, expected file identity is
recorded durably, and publication refuses an existing destination. File integrity,
exact decoded-array comparison against returned states/events/dense coefficients,
and live/offline replay remain separate required checks. Structured append-only
segment receipts retain both identities and original failures even if later
loading/replay or receipt writing fails. Complete public Results are checkpointed
before diagnostic persistence. No retry or hash substitution is implemented.

The whole observer file changed; it is not described as byte-identical.
PERSISTENCE_SOURCE_DELTA.json binds the exact delta and unchanged scientific
functions/dependencies, including the production calls, state extraction,
interpolation evaluator, fixed-z reconstruction, activation, endpoints,
inventories and quadrature. All 50 protected production/001–004 paths pass the
original hashes; controls, requests, masks and numerical allocations are unchanged.

Old observer SHA256: `fcd260462e1f51a55c31743d2e7f4283c61147b344b17255abae536cbe53279d`.
New observer SHA256: `71985ef5c0c1d1680ef1ee211527359532d2b911e85ed3230a709ddd4ffe38da`.
Source delta SHA256: `e861d333e44e3654103cd2b723f06146f237028a0e4722cc3678670b0ff4a57c`.

## New full execution evidence

| Quantity | Combined corrective capture | Normal |
|---|---:|---:|
| Invocation seconds | 142.27878846699605 | 30.401547679997748 |
| Peak RSS bytes | 3765407744 | 1000345600 |
| Peak virtual bytes | 4082462720 | 1270878208 |
| Returned segments | 3 | 3 |
| Accepted states | 3262 | 1514 |
| Dense intervals | 3259 | 1511 |
| Retained numerical bytes | 2684875008 | 333279792 |
| Full evidence bytes at controller end | 2837048383 | 413725287 |
| Live replay points | 6527 | 3031 |
| Live/offline maximum absolute difference | 0 | 0 |
| Accepted-state interpolation difference | 9.492406860545088e-14 | 3.652633751016765e-14 |

All three segments in each run pass file identity, direct array fidelity and
live replay. Accepted-state interpolation differences are distinct from exact
saved-array fidelity and fit the unchanged 256*eps*8 replay allowance. Both
runs retain the complete public Result and restore the patched symbol. Combined
public Result SHA256 is exactly the historical `8b810378a3e1d9b976ae1dc3311500274e63e56e2d03797278c8a30a1fb7348b`.
The old third segment is not repaired or concatenated into the new trajectory.

## Individual audits

Both runs include horizon 8, first drip/exit, all 220 activation positions,
seven histories, 614 required/activation records plus both sides of the two
physical events, every accepted state and the one localized event state.
Diagnostic bounds audit 135960 liquid values, 135960 grain means and 4326
history values per run; all requested values are included, with zero exclusions
or unavailability. These counts include additional activation and event support;
the unchanged comparison grid remains 395 times by 220 physical positions.

| Audit | Normal | Combined | Unchanged allowance |
|---|---:|---:|---:|
| max_normalized_conservation | 1.3102289026388825e-09 | 4.349706633942076e-11 | 1e-6 |
| cup_state_integral_max | 3.6763392330385614e-09 | 6.4770233620947693e-10 | 5e-5 including quadrature |
| cup_quadrature_refinement_max | 0 | 0 | 1e-10 |
| independent_sum_allowance_fraction | 6.103515625e-05 | 0.0001220703125 | 1 |
| public_inventory_allowance_fraction | 0.00093810038435603157 | 0.00093810038424591751 | 1 |
| public_profile_reconstruction_error | 3.3306690738754696e-16 | 6.6613381477509392e-16 | 256*eps*4 |
| public_cup_error | 0 | 0 | 256*eps*4 |
| public_outlet_error | 0 | 0 | 256*eps*4 |
| diagnostic_inlet_mean_error | 2.0461005069943861e-05 | 5.5130604425107643e-06 | 2e-5 |
| front_wet_excess | 0 | 0 | 1e-10 |
| front_decrease | 0 | 0 | 1e-10 |

Cell and diagnostic aqueous bounds, grain nonnegativity, phase nonnegativity,
modal weights/rates, public reconstruction, status, complete horizon/events and
activation/time support all pass in both runs. No unit grain cap is imposed.
The inlet gate is the sole failed individual gate, in normal.

At t=8, normal inventories [liquid,fines,boulders] are `[9.825157731846446e-08, 3.144050476155665e-07, 2.310140907092343e-07]`, cup `5.551999349061818`. These finite residuals are not replaced by assumed depletion.

At t=8, combined inventories [liquid,fines,boulders] are `[9.778062004528465e-08, 3.1289798396047257e-07, 2.3033232357794226e-07]`, cup `5.551999359129192`. These finite residuals are not replaced by assumed depletion.

## Physical-coordinate refinement: normal versus combined

| Observable | Maximum absolute error | Allowance | Location | Requested / included / excluded / unavailable | Pass |
|---|---:|---:|---|---|---|
| activation | 1.4624018952247297e-05 | 0.001 | `{'index': [84], 'z': 0.405}` | 220 / 220 / 0 / 0 | True |
| arrival | 3.1463881873250443e-06 | 0.001 | `{'normal_t': 6.5043092876388835, 'refined_t': 6.504306141250696, 'z': 1.0}` | 1 / 1 / 0 / 0 | True |
| boulder_inventory | 1.2379364434491127e-06 | 5e-05 | `{'index': [329], 't': 6.65}` | 395 / 395 / 0 / 0 | True |
| cup | 9.5394497234835285e-06 | 5e-05 | `{'index': [317], 't': 6.595}` | 395 / 395 / 0 / 0 | True |
| fines_inventory | 6.4300314637985578e-06 | 5e-05 | `{'index': [316], 't': 6.59}` | 395 / 395 / 0 / 0 | True |
| front | 2.2334260599277123e-06 | 0.001 | `{'index': [106], 't': 2.6}` | 395 / 395 / 0 / 0 | True |
| grain_histories | 0.00043238725012884061 | 0.00023 | `{'index': [237, 5], 't': 5.875, 'z': 0.9}` | 2765 / 1794 / 971 / 0 | False |
| grain_profiles | 0.00060001917800156512 | 0.00023 | `{'index': [299, 218], 't': 6.51, 'z': 0.995}` | 86900 / 56541 / 30359 / 0 | False |
| liquid_inventory | 2.0093848325242192e-06 | 5e-05 | `{'index': [316], 't': 6.59}` | 395 / 395 / 0 / 0 | True |
| liquid_profiles | 0.00017578337656656839 | 0.001 | `{'index': [302, 213], 't': 6.525, 'z': 0.98}` | 86900 / 85676 / 1224 / 0 | True |
| outlet | 0.00011547549619722597 | 0.001 | `{'index': [303], 't': 6.53}` | 395 / 381 / 14 / 0 | True |

The inherited event/displaced-front/age masks are unchanged; z=1 remains
eligible after legitimate event/age exclusions. There are no blanket added masks.
For EACH unexecuted normal/bed_fine, normal/modes_fine and normal/time_fine pair,
all eleven metrics have zero included/excluded and requested=unavailable:
outlet/front/cup/each phase 395; liquid/grain profiles 86900; activation 220;
exit 1; histories 2765. Their maximum errors and locations are unavailable.

## Resource accounting and stop

Cumulative: **3 full, 19 short, 551.7639391399425 numerical seconds**. No unresolved starts or limit violation.

The original 2 GiB and authorized 8 GiB policies are separately verified against
actual enforcement code and attempt bindings. Every new numerical process used
exactly 8589934592 bytes RLIMIT_AS and at most 300 seconds. Real host/cgroup,
inherited limit and storage checks passed with the original operating margin.
No restriction was raised externally. Current enforcement SHA256:
`911ba0d24569b4d832cc1e1ba12b4a86ecee30a22d52ad08b5c740e7ab1c8c99`.

Before recapture, 322.6962052669696 seconds were used; the frozen 220-second
recapture +335-second remaining rows +60-second report estimate totaled
937.6962052669696 seconds (1017.6962052669696 with a 300-second recapture).
After measured combined success, the remaining-panel estimate was
867.1251329539664 cumulative seconds. Distinct row estimates retained historical
single-axis cost context and uncertainty; no monotonic cell/mode-cost guarantee.
Resource feasibility passed. The subsequent stop is the observer inlet gate.

The recapture consumed one correction full slot and 142.27878846699605 seconds;
including the earlier 3.6217310409992933 correction seconds, correction spending
is 145.90051950799534 seconds. Two original correction slots and
154.09948049200466 reserve seconds remain notionally available. Five mandatory
full runs remain unexecuted; unused capacity authorizes no additional candidate.

| Attempt | Kind / phase | Seconds | Exit |
|---|---|---:|---:|
| fixtures-initial | short / development | 0.8171941109903855 | 0 |
| pilot-combined | short / development | 87.53527537699847 | 1 |
| fixtures-final | short / development | 0.5683679179928731 | 0 |
| fixtures-bound | short / development | 0.5670600829907926 | 0 |
| example | short / development | 0.41725147899705917 | 0 |
| fixtures-freeze | short / development | 0.5666131720063277 | 0 |
| fixtures-retention | short / development | 0.5675947020063177 | 0 |
| fixtures-correction | short / correction | 3.6217310409992933 | 0 |
| pilot-combined-8gib | short / development | 96.1511100079806 | 2 |
| combined-feasibility-8gib | full / development | 108.11789934101398 | 1 |
| archive-persistence-diagnosis | short / final | 4.942981554981088 | 1 |
| archive-persistence-diagnosis-completion | short / final | 5.146550296019996 | 0 |
| persistence-fixtures | short / final | 1.517925424996065 | 1 |
| persistence-fixtures-qualified | short / final | 1.466550915996777 | 0 |
| persistence-fixtures-minimum | short / final | 1.4189887460088357 | 0 |
| persistence-final-fixtures | short / final | 4.73970111500239 | 0 |
| persistence-final-minimum | short / final | 4.53340998198837 | 0 |
| combined-persistence-recapture | full / correction | 142.27878846699605 | 2 |
| combined-persistence-evaluation | short / final | 7.15013922000071 | 0 |
| normal-persistence | full / final | 30.401547679997748 | 2 |
| persistence-offline-report | short / final | 24.206018283002777 | 1 |
| persistence-offline-report-completion | short / final | 25.03124022297561 | 0 |

The first new fixture attempt failed two manufactured control inputs below
production's existing minimum; corrected fixtures pass without modifying that
validation. The first offline report produced its raw-recomputed report, then
failed an auxiliary exact-equality assertion comparing two BLAS summation layouts
for the inlet location (difference about 1.4e-17). Its charged replacement used
the unchanged endpoint evaluation and reproduced the report error exactly at
t=.2,z=0. No scientific error or allowance was changed. Both failures remain.

Raw-evidence reporting itself ran under the controller, whose own start was
necessarily pending until child completion. The preliminary report is retained.
After its successful end, only accounting and that pending-start reason/block
were refreshed from the closed original ledger. All scientific fields and the
incomplete disposition remain unchanged. The standard offline reporter against
the closed ledger reproduces the final result; no solver or archived code is
needed. Closure and worker hashes remain external.

## QA, review and boundaries

New persistence/replay and affected tests: 62 passed at current and supported
minimum NumPy/SciPy versions. The final additional resource/reporting checks
pass 28 tests; Ruff, configured mypy, 15 integrity/generated checks and seven
packaging checks pass. The normal repository suite passed 6144 tests (67 skipped,63 deselected);
141 focused inherited/new tests passed. The last failure-block annotation is
covered by the separate28 affected checks. Exact-head hosted CI and the
same independent review addendum have separate final receipts on PR #327;
pending checks are not represented as passed. The starting reviewed head's
25 hosted checks passed. Two preliminary software-QA invocations were interrupted
and their partial results are not counted as a completed suite; normal selectors
and dependency versions are unchanged.

The fixture arrays reproduce the prior analytical values exactly under the new
capture-source identity; old fixtures and all original artifacts remain intact.
EWP is clean and read-only, remote main `16eec1dda24ebf658965eddcf1a6fffa81903b32`;
lock SHA256 `52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`
is unchanged. Leave #327 draft, auto-merge disabled and #67 open. No comparison
readiness, production repair/adoption, merge or successor is established.
