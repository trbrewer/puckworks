# VAL-CASE-RHEOLOGY-DECISION-RESOLUTION-001: frozen interpretation

G1; NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY; RETROSPECTIVE;
TARGET_EXPOSED; EXPLORATORY. Owner authority is this task's explicit instruction.
This specification precedes the new 32-row evaluation, but the historical results,
including SW_UP/TR_UP fraction-TDS unresolved outcomes, are already known.
There is no blind validation, parameter fitting or new scientific scoring.

## Question, authority and population

Separate (a) the contractual adequacy of E2 versus C, (b) compliance with the
original numerical precision rule, and (c) which side of the original engineering
threshold the retained empirical envelope occupies. The secondary NEW-C versus
OLD-C delivery magnitude is a different question, never an E2 transfer gate.

Live main was verified at Puckworks `882584d110e1356091435ab8b002fb9abdd35ad6`
and EWP `4284e9460c8057053e95de7cfa2fb3590e68e9db`; no newer main was reset.
No recent/open task or purpose duplicate was found. The isolated branch starts
at Puckworks main, without unmerged #321/#333 or unrelated work.

The policy's historical version remains `DECISION_RESOLUTION_POLICY/v1-proposed`.
Authority to use it is the later [owner acceptance](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145),
[actual merge](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192974851)
and [post-merge receipt](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6193554365).
Accepted head `8cd54290f4a927b046f2da43447c1d864e95b2dd`, tree
`7741920d87c813658941ebc26869c2af19807fad`, actual merge as above.
The historical proposed/unapproved wording in policy, CURRENT and handoff is
preserved. This separately authorized case does not rewrite any prior contract.
INPUT_MANIFEST.json pins exact policy/helper and historical source hashes.
SCI-GOV-001 and EWP Validation Operating Standard v1 govern this bounded case;
the October 9 review §6.4/T05 motivates it. T04's empirical case families are
outside scope. PR #335 infrastructure qualification is reused, not repeated.

Include exactly four law/history pairs: SW_WATER_ANCHORED_90C and TR_LINEAR,
each DOWN and UP. Primary includes E_Qint, E_Qpeak, D_share_mean_pp,
D_share_peak_pp, E_Spath, D_TDS_pp (24); secondary includes E_Spath, D_TDS_pp (8).
The manifest enumerates every identity and locator prospectively; no exclusions.
Missing rows remain explicit unresolved records; duplicate/extra identities are
structural errors that cannot produce a successful report. Preserve all adverse
results. Original expected counts (verification expectations, never tuning goals):
primary 24 PASS; secondary six MATERIAL_MODELED_DELIVERY_CONTRAST and two UNRESOLVED.

## Numerical representation and exact historical mapping

Load retained JSON numbers as binary64, as the historical Python observers did.
No rounding, epsilon, isclose, padding, RSS or decimal reinterpretation of metric
values. JSON output uses round-trippable floats; B_star retains its decimal string.
Checks reproduce aggregate arithmetic from recorded variants/discrepancies only;
they do not rerun the original observer or its 50-digit arithmetic campaign.

For each row, verify M equals the base variant; time/axial/radial/property terms
are absolute changes from base, property is zero for TR, and arithmetic is the
maximum retained independent discrepancy over every required variant. Validate
finite nonnegative magnitudes/terms, original units/budgets and complete keys.
Sum in ORIGINAL order: time, axial, radial, property, arithmetic. Secondary's
radial key was renamed from Cradial to both_C_radial AFTER summation; sorted JSON
key order is not the arithmetic order. The historical environment was CPython
3.12.3: explicitly reproduce its compensated float-sum convention on supported
Python versions (see [CPython 3.12.3 sum](https://github.com/python/cpython/blob/v3.12.3/Python/bltinmodule.c#L2444)).
Require exact binary64 equality of reproduced components and total. A mismatch
has no new tolerance: retain it, disclose the difference and mark interpretation
unavailable, with historical reproduction unresolved. Native evidence is not
reverified. Any alternative arithmetic diagnostics cannot replace retained u.

Eligibility = complete valid compatible mandatory aggregate evidence AND
u <= 0.20*b, inclusively. The multiplication is the historical binary64 operation;
for decimal budget 0.1, its binary64 ceiling serializes as 0.020000000000000004.
That representation fact is not an extra tolerance. Record the actual ceiling.

For eligible primary rows: M+u < b gives PASS; M-u > b gives FAIL; otherwise
UNRESOLVED. For eligible secondary rows: M-u > b gives
MATERIAL_MODELED_DELIVERY_CONTRAST; M+u < b gives
BELOW_DECLARED_MATERIALITY_BUDGET; otherwise UNRESOLVED. Equality at either
boundary, missing/incompatible evidence, nonfinite/negative inputs or excessive
allowance gives UNRESOLVED. A valid primary FAIL takes precedence over unresolved
siblings; all 24 PASS gives E2_CONDUCTANCE_MATCHED_REVERSAL_SUFFICIENT_FOR_TESTED_OUTPUTS;
otherwise aggregate unresolved. Secondary counts remain separate, with no invented
universal materiality or null aggregate.

L=M-u and U=M+u form the closed empirical sensitivity envelope. U<b is entirely
below, L>b entirely above, otherwise overlaps or touches. Never clip L to zero.
Precision headroom = 0.20*b-u; below-budget headroom = b-(M+u);
above-budget headroom = (M-u)-b. These signed diagnostics are not new thresholds.
Record primary satisfaction/failure and secondary above/below headroom explicitly.

Use the accepted helper independently with compatible scope and `sensitivity`
evidence/basis, operator `<` primary and `>` secondary. Declare the bound-based
requirement only to expose lack of an applicable bound: its contractual result
may be UNAVAILABLE and bound resolution UNRESOLVED, while the sensitivity relation
is informative. These helper outputs never replace the case-local historical
mapping. The generic comparator can call boundary equality a violation while
historical decisions remain unresolved. Precision failure alone is not numerical
corruption. Missing source/support or component inconsistencies block scientific
reliance. Record unknown measurement, training, source-model, parameter and
untested discretization/continuum uncertainty; never invent zero uncertainty.

## Support, construction and data-use limits

Primary radial refinement changes C only, E2 fixed at base; secondary changes
BOTH C configurations together. Temporal/axial/SW property refinements are paired.
Hydraulic/allocation metrics use every native interval over 0–30 s. E_Spath uses
the union of native mass breakpoints, zero and endpoint, normalized by reference
S(B_star); D_TDS_pp uses five conservative equal-beverage-mass fractions including
the first increment. Secondary reference normalization is OLD-C.

Common B_star: UP 0.015983191 kg; DOWN 0.016114389 kg. Original rule is decimal
floor to 1e-9 kg of 0.95 times the minimum of all 18 qualified C terminals per
history (old/new, both laws, every refinement). Preserve all 50 coverage rows,
terminal masses, ratios and deliberately unscored tails. Verify retained aggregate
support arithmetic/receipt and per-row relevant coverage; never shorten support.
Hydraulic rows are not invalidated merely by unavailable delivery support.

Read retained public repository METRICS/COVERAGE/SUPPORT and qualification,
REUSE/AUDIT/artifact receipts. All source accesses are read-only. Relevant property
lineages are g10_liquor_rheology/telisromero2001_tables and sobolik2002/rheology;
only guide metadata and historical source-use receipts are inspected in this task,
not restricted original tables. Original source limitations persist: industrial
extract transfer, TR dilute continuation, SW water anchoring and 90 C extrapolation.
No private corpus, external archive, native trace, physical measurement or native
solver environment is required or newly verified. Missing external material is
not a claim of nonexistence/exhaustion. No new experimental claim or fit.

C is a source-conditioned computational reference, not measured truth. E2 has two
radial cells at EACH axial station, not two globally lumped states. The 010
conductance-matched reversal changes weighted permeability distribution and
residence times as well as radial position; it does not isolate a unique lateral
mechanism. Historical context only: 007 retains 22 PASS, one TR/9-bar TDS FAIL,
one SW/9-bar TDS UNRESOLVED for its non-exchanging P construction; useful hydraulic,
allocation and path results do not prove full sufficiency. 011 retains
NO_MATERIAL_ARRANGEMENT_CONTRAST_FOR_TESTED_DELIVERY for all eight distribution-
preserving contrasts; full conditional E2 was not triggered. Neither is rescored.

Budgets are engineering thresholds, not validated consumer/taste tolerances.
Empirical sensitivity is not a certified bound, confidence/population interval,
total physical uncertainty or proof of every-discretization convergence.
No whole-shot fidelity, unique mechanism, arbitrary scenario transfer, extra E2
capability, physical validation or production eligibility follows.

## Execution, review and report

Freeze this specification, input manifest and independently authored synthetic
expectations; obtain independent nonhuman pre-analysis review before real-row
evaluation. Report reviewer unavailability honestly; never self-approve. Run
focused synthetic tests separately, then one bounded retained aggregate evaluation
with reproducibility checks. No original preparation/run/analyze/report entry
point or legacy scorer import. Output only to a chosen directory outside EWP.
Final independent review checks actual 32-row crosswalk, arithmetic, support,
provenance and scientific limits. Relevant ordinary QA and candidate hosted CI
remain separate from scientific outcomes. No helper/policy/scorer changes.

RESULTS.json: all 32 original/reproduced rows, inputs/locators/terms/refinements,
precision states, envelope/headrooms, support, helper results and limitations;
complete separate counts and discrepancies. RESULTS.md: executive conclusion,
original/new interpretation, 24+8 full matrices, detailed UP TDS, separate 007/011
context, unsupported claims and reproduction/review evidence. HANDOFF.md gives
commands, exact identities, tests, operational blockers and draft PR disposition.
Review records bind direct file hashes, not a recursive receipt system.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; MERGE_AUTHORIZED=false;
PRODUCTION_ADOPTION_AUTHORIZED=false; NEW_NATIVE_SIMULATIONS=0;
NATIVE_EWP_RUNS=0; NO_AUTOMATIC_SUCCESSOR.
