# Prospective decision-resolution supplement

**Version:** `DECISION_RESOLUTION_POLICY/v1-proposed`

**Status:** proposed until normal owner acceptance and merge.

**Task:** VAL-INFRA-DECISION-RESOLUTION-001; T03 follow-on to SCI-MD-MASS-UNCERTAINTY-001.

**Classification:** G1 scientific decision-policy semantics under
[SCI-GOV-001](MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md), with ordinary engineering
controls for implementation; `NO_GOVERNING_PHYSICS_CHANGE`;
`SYNTHETIC_VERIFICATION_ONLY`.

This is a narrow supplement to the
[Validation Operating Standard v1](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/validation/VALIDATION_OPERATING_STANDARD_V1.md)
and its [review checklist](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/validation/VALIDATION_REVIEW_CHECKLIST_V1.md).
It retains `SCIENTIFIC_RESULT_DISPOSITION`, `VALIDATION_FRAMEWORK_DISPOSITION`
and `CLAIM_CEILING` as separate case-level reports. The helper's small internal
comparison statuses do not replace those dispositions or the public GateStatus.

## Authority and use

The [October 9 review](../research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md),
especially §6 and T02–T05, motivates this extension. Disclosed retrospective
[T02 findings accepted through #334](https://github.com/trbrewer/puckworks/blob/7975fbc39a649cb757702131e2b91b13439c7192/docs/analysis/sci_md_mass_uncertainty_001/RESULTS.md)
inform its design: MASS-006 retains its success with shot-sensitive gain
magnitude; MASS-007 retains comparative improvement alongside absolute/count
adequacy failure; MASS-008 retains adequate adaptation without earned increments.
These are motivation, never inputs to the new helper. This is neither target-blind
calibration nor independent empirical validation. T02's unresolved uncertainty
components remain unresolved; T04/T05 are separate, unauthorized follow-ons.

Future scientific cases must declare a controlling policy version, requirements,
evidence uses and intended claim through the existing process. Acceptance of this
supplement does not migrate historical contracts, rewrite authorizations, change
thresholds or authorize adoption. A frozen threshold may lack practical
justification; that omission is disclosed without inventing a replacement or
retroactively invalidating a completed task merely for missing documentation.

`PHYSICAL_VALIDATION=NOT_ESTABLISHED`; `MERGE_AUTHORIZED=false`;
`PRODUCTION_ADOPTION_AUTHORIZED=false`; `NATIVE_EWP_RUNS=0`;
`NO_AUTOMATIC_SUCCESSOR`. Synthetic verification requires no G3 prediction or
scoring lifecycle. Frozen Paper A assurance and Insight Foundry remain untouched.

## Declare the requirement before interpreting evidence

Each controlling or diagnostic requirement has a stable identity and an explicit
role: mathematical invariant/integrity, numerical approximation/precision budget,
publication reproduction, empirical prediction adequacy, incremental practical
value, finite-cohort count, or coverage. Its declaration retains:

- observable, canonical units, domain, estimand, aggregation, information available
  to the predictor, scored member identities and their physical grouping;
- eligibility/exclusions, operator and threshold, including strict/inclusive
  boundary, purpose, threshold basis and approval status;
- contractual decision basis, required resolution components, required counts or
  support, comparator for incremental value, and claim limits.

Legitimate threshold bases include analytical identities, allocated numerical
error, publication/source precision and intended-use loss. A practical margin
must not be selected from a residual, SD, deletion range or desired reversal.
An absent or unapproved practical basis permits descriptive comparison; it
does not establish practical value, earned complexity or adoption. All example
numbers here are synthetic design inputs, never espresso defaults.

Only explicitly declared controlling components govern a conjunction. Diagnostics
remain visible but neither rescue nor defeat it. Available count metadata is not
implicitly controlling. In particular, MASS-008's generic `required_adequate_pairs`
was not its overall adequacy gate; this supplement does not evaluate MASS-008.

## Three different answers

1. **Mathematical relation:** how the supplied numbers relate to the requirement.
2. **Contractual compliance:** whether the explicitly declared decision rule is
   met, on admissible compatible evidence.
3. **Evidence resolution:** what is supported about the assessed quantity,
   under which components, scope and assumptions.

A point-based `q <= 10` contract fails for point 11 even when an applicable
interval [9,12] overlaps the boundary. Report FAIL and unresolved evidence
together. Conversely, point 9 can pass that contract with measurement uncertainty
unknown; missing uncertainty does not erase the descriptive comparison and is
not manufactured into [9,9]. An explicitly bound-based contract cannot be decided
from a point or empirical range. Unspecified decision bases are rejected.

For finite ordered endpoints `L <= U`, closed-interval relations are:

| Requirement | All supplied values satisfy | All supplied values violate |
|---|---|---|
| q <= T | U <= T | L > T |
| q < T | U < T | L >= T |
| q >= T | L >= T | U < T |
| q > T | L > T | U <= T |

Otherwise the interval overlaps. At [T,T], inclusive requirements satisfy and
strict requirements violate. These are mathematical relations, not claims about
what the endpoints represent. Wider intervals with fixed other inputs cannot
create a newly resolved satisfaction or violation. The helper makes no
equivalence decision.

The implementation accepts finite built-in Python `int`, `float` and `Decimal`
without coercion. Integers remain exact; floats retain their supplied binary
value; Decimal retains its supplied precision (including its serialization as
`{"decimal": "..."}`). Comparisons use exact rational representations internally,
preserving supplied values and avoiding ambient Decimal context flags/traps;
a decimal 0.1 need not equal binary float 0.1. No rounding,
`isclose`, hidden epsilon, inward/outward padding or error propagation occurs.
Booleans, numeric strings, complex/numpy values, nonfinite values and inverted
intervals are rejected. Construct Decimal explicitly for decimal inputs.

All scope fields, including units, must match exactly. The caller supplies
canonical units for points, endpoints and thresholds. There are **no unit
conversions or aliases**: a kg/g or percent/fraction mismatch is unavailable
for reliance rather than guessed. Integer, float and Decimal representations
of exactly representable values in the same canonical unit agree.

## Evidence applicability and trust boundary

The compact records distinguish applicable bounds, finite empirical sensitivities,
points, unavailable evidence, counts and coverage. Every supplied record includes
scope, observed support, a basis, assumptions, covered and unknown uncertainty
components, and separate admissibility/source/payload/numerical-integrity checks.

An applicable bound requires a compatible analytical, numerical or allowance
basis, not just an interval label. Its basis must name the same scope and cover
every explicitly requested resolution component. A numerical-reduction bound
cannot become a measurement, training, population or cross-source bound. Unknown
components remain visible even when a narrower declared question is resolved.
Allowance conclusions remain conditional on their explicit assumptions; they are
not described as rigorously certified numerical accuracy.

The helper checks **declared compatibility**. It does not independently verify
source identity, authenticate an external method, prove a certificate, or detect
a caller inventing a false mathematical argument. Basis, quality and success
declarations require appropriate review in a future case. Synthetic bound fixtures
give transparent affine inequalities; a free-text “certified” label supplies no
proof. Merely changing a sensitivity record's kind cannot pass the bound-basis
checks. There is no proof or receipt registry.

Finite sensitivity ranges support only stability or boundary crossing under the
named tested changes. They do not supply confidence coverage, population
reliability, a continuum bound, physical validation or replacement historical
decisions. A contrast 2.0 with tested range [1.97,2.03] is stable against >=0.10;
its reported allowance 0.03 nevertheless fails a separate <=0.02 precision
contract. Range [0.07,0.13] crosses that boundary and still fails the precision
contract. Precision failure alone is not numerical corruption.

Invalid source identity, inadmissibility, corrupted payload or material numerical
integrity failure blocks reliance regardless of apparent margin. Raw arithmetic
may remain as an explicitly unsupported diagnostic, never a supported stable
effect or scientific success. Quality defects in an affected controlling
component prevent whole-case success; sound unrelated component results remain.

A subset point statistic cannot decide a full-support requirement. A separately
justified full-scope bound can establish failure despite missing observations;
the full-scope justification and incomplete coverage must both remain visible.
The synthetic demonstration uses `q=(12+x)/2`, `0<=x<=2`: q is in [6,7], so <=5
fails while x is unobserved. No empirical full-support bound is constructed here.
A valid supplied full-scope bound can also resolve a metric positively without
satisfying a separately required complete-observation gate.

Missing uncertainty is not zero uncertainty; between-shot SD is not analytical
repeatability; zero observed SD is not zero total uncertainty; deletion ranges
are not confidence intervals. Statistical metadata/inference, joint confidence,
RSS, standard errors, bootstrap, normal approximations and universal coverage
factors are unsupported. Statistical/equivalence/adoption requests are explicitly
rejected; no favorable fallback is supplied.

## Counts, coverage and conjunctions

Finite-cohort counts retain fixed N, definite successes D, possible successes P
**including D and missing/unresolved eligible members**, and explicit integer k.
Every eligible member has an identity, physical grouping and state: definite,
possible, failure or missing. Exclusions and their reasons remain outside N.
The helper verifies `0 <= D <= P <= N`, `0 <= k <= N`, and exact member/missing
accounting. Empty cohorts, duplicate identities and Boolean counts are rejected.
In this limited helper, count and coverage roles require explicitly declared
`finite_count` and `complete_support` bases respectively; scalar bases cannot
bypass member accounting. The basis is checked, never inferred.
There is no percentage option, floating `ceil`, or default fraction.

- D >= k resolves the count positively under its declared success interpretation.
- P < k resolves it negatively.
- Otherwise it is unresolved.

The count declares what “definite” means: point-contract compliance, applicable
bound satisfaction, or stability under named tested sensitivities. The last two
are not interchangeable. Point/sensitivity count compliance is reported without
promoting it to bound-resolved adequacy. Bound counts also require compatible
scope and covered components. Supplied member classifications are reviewed
declarations, not inferred from whichever fields are available.

At N=8, k=6: D/P=5/5 fails; 5/7 is unresolved; 6/8 succeeds even with two missing
members. A separately declared complete-support requirement still fails in that
last case. Counts describe the finite cohort, not population reliability.
Fractions, aliases, repeated evaluations and calibrator-target pairs do not
become independent physical experiments.

Every declared component is retained and evaluated, including missing components.
Only controlling results enter separate contractual and resolution conjunctions:
an applicable FAIL witnesses conjunction failure; otherwise all must PASS to
pass; unavailable/unresolved required components prevent success. Reporting
never short-circuits, averages scores or drops adverse components. Empty composites
and duplicate identities are rejected. Failure can be resolved while assessment
completeness is false. A coverage failure is a coverage failure, not a claim that
the model's physical behavior is false.

`support_complete` requires every declared member to be observed. Component
`assessment_complete` additionally requires an available contractual assessment
and evidence interpretation; overlap or point-only uncertainty may be fully
reported without being resolved. Whole-case completeness covers controlling
components; diagnostics retain their own flags. Neither completeness flag is a
scientific verdict.

## Adequacy and practical value

For lower-is-better metrics, `gain = control_metric - candidate_metric`. Retain
the declared comparator(s), information privileges and aggregation; do not pick
the most favorable control later. Adequate error [3.9,4.1] against <=5.0 and gain
[0.20,0.30] against >=0.50 yield satisfied adequacy and failed incremental margin.
Positive gain is insufficient for the declared practical increment. Adequacy
does not justify extra assays, calibration or complexity. Failure to establish
superiority does not prove equivalence or uselessness. Even satisfied, justified
requirements are not automatic authorization for adoption.

## Implementation and review

The internal [helper](../../puckworks/validation/decision_resolution.py) is opt-in
and side-effect-free; it has no public export or default gate wiring. It reuses
the existing scorers' closed-bound, conjunction and definite/possible semantics
without importing their fitting/source dependencies or refactoring history.
It does not use `GateSuiteResult.passed` as a scientific verdict. Software PASS,
SKIP or absence of errors has no such implication.

Run `python -m examples.decision_resolution` for deterministic SYNTHETIC JSON;
`--output <new-file>` writes only the requested file, exclusively. The
[focused tests](../../tests/test_decision_resolution.py) cover the discriminating
matrix, strict endpoints, applicability, counts, monotonic weakening, ordering,
serialization and side effects. The [handoff](../analysis/val_infra_decision_resolution_001/HANDOFF.md)
records commands, readable outputs, actual QA/review/CI and limitations. Review
uses the existing checklist's materiality and non-retroactivity rules; synthetic
tests do not score governed evidence or establish physical validation.
