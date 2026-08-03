# Paper 1 P0-G0 Protocol-Freeze Adjudication

**Date:** 2 August 2026  
**Repository:** `trbrewer/puckworks`  
**Reviewed snapshot:** merge commit [`9c52c94edb27b461b6e7a4d471d29f3cef9d053e`](https://github.com/trbrewer/puckworks/commit/9c52c94edb27b461b6e7a4d471d29f3cef9d053e)  
**Trigger:** merger of PR #223, *Paper 1 v2.2.1: repair the control that claimed more than it enforced*  
**Review mode:** read-only; no repository file was modified and no scientific analysis was run

---

## 1. Disposition

> # **P0-G0 FREEZE WITHHELD**
>
> **The V2.2.1 assurance-control repair is accepted, but the current analytical protocol is not scientifically freeze-ready. P0-G8 and every other P0 scientific gate remain unauthorized.**

Machine-readable disposition:

```text
PAPER_1_P0_G0_FREEZE_WITHHELD
SCIENTIFIC_GATE_EXECUTION_NOT_AUTHORIZED
NEXT_ALLOWED_CYCLE=PROTOCOL_COMPLETION_AND_ACTIVATION_REPAIR
FIRST_SCIENTIFIC_GATE_AFTER_ACTIVATION=P0-G8
REVIEWED_COMMIT=9c52c94edb27b461b6e7a4d471d29f3cef9d053e
```

This is a **no-go on the current freeze**, not a rejection of the pivot. The thesis—

> **prediction is not kinetic identification**

—is strong, coherent, and materially more interesting than the superseded headline comparison. The V2.2.1 repair also represents real progress: it corrects the claim-surface scanner, gate-evidence binding, baseline preservation, and several active overclaims.

The reason for withholding the freeze is narrower and decisive: **the bundle itself records that load-bearing, outcome-sensitive scientific choices remain unspecified**, including the choices that determine the P0-G8 classification. Freezing now would either freeze an incomplete protocol or leave discretion to select those choices after observing the result. Neither is acceptable.

---

## 2. Sources reviewed

The decision is based principally on these files at the reviewed commit:

1. [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md)
2. [`PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md)
3. [`PAPER_A_PLAN_MANIFEST_V1.json`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json)
4. [`PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json)
5. [`PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md)
6. [`PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/docs/paper1_resource/PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md)
7. [`tests/test_paper1_plan_integrity.py`](https://github.com/trbrewer/puckworks/blob/9c52c94edb27b461b6e7a4d471d29f3cef9d053e/tests/test_paper1_plan_integrity.py)
8. [PR #223](https://github.com/trbrewer/puckworks/pull/223)

The merged PR itself states that P0-G0 is not frozen and that PRO-01…08, SCI-01…04, TAX-01, and LED-01/02 remain accepted but unimplemented. The operative plan repeats this and expressly says those items block P0-G0 and every scientific gate.

---

## 3. What is approved

### 3.1 The scientific pivot

The paper should proceed on the distinction among:

1. predictive performance under declared target-side information;
2. practical localization of the model-specific mass-transfer-rate multiplier `κ`; and
3. the observation and input channels that support each task.

That distinction gives Paper 1 a defensible scientific spine. It allows a useful result even if P0-G8 does **not** support a broad weak-localization headline: the finite model-response limit, exact production-MAPE profiling, threshold dependence, and observation-operator analysis can still form a coherent paper.

### 3.2 The V2.2.1 assurance repair

The following repairs are accepted as completed Phase A work:

- JSON rather than an optional YAML parser for the manifest;
- discovery and classification of candidate claim surfaces;
- format-aware claim scanning;
- adversarial scanner probes;
- evidence-bound closure records for already passed numerical gates;
- separation of initial and final ledger/scope artefacts;
- correction of active categorical or causal overclaims;
- explicit recognition that a single commit cannot contain its own commit SHA;
- separation of R0a and R0b;
- explicit statement that same-campaign frozen reanalysis is not independent confirmation.

These controls improve the programme. They do not, however, substitute for completing the scientific protocol.

---

## 4. Blocking findings

## B1 — The operative plan explicitly says the protocol is incomplete

**Severity:** critical  
**Disposition:** blocks P0-G0

Section 12 of V2.2.1 identifies all of the following as accepted but unimplemented and says they block P0-G0:

- P0-G8 domain, threshold formulas, verified error intervals, global-topology algorithm, response-shoulder threshold family, and extension of the limiting derivation beyond one centre condition;
- P0-G6 RSI formula, weights, designs, `κ` locations, profile-width and censoring definitions, concordance statistic, effect criterion, and controls;
- P0-G9 map families, exclusion unit—including upstream fitted polynomials—adaptation design, and impossibility rule;
- P0-G5 regularization coordinate, objective scaling, tuning branch, dominance definition, and envelope construction;
- P0-G7 generator, true-parameter grid, covariance, mismatch magnitudes, resource costs, replicate count, and success criterion;
- P0-G4 factorial and expected run count;
- the revised taxonomy and claim-binding schema;
- map-uncertainty propagation and outcome-conditional H4 wording.

This is conclusive. A protocol cannot be frozen while the controlling plan says that the result-changing decisions it must freeze are still open.

### Required disposition

Complete these scientific specifications before P0-G0 can pass. Do not reclassify them as implementation details: several determine the estimand, classification, or interpretation.

---

## B2 — P0-G8 remains underdetermined in precisely the places that can change H1

**Severity:** critical  
**Disposition:** blocks P0-G8 and therefore P0-G0

The current protocol says to compute `f_inf` by a route that is “derived or rigorously converged,” calculate `J_inf`, use an error band `ε`, report all connected components, and identify a response shoulder using a “declared threshold.” Those are correct requirements, but they are not yet an executable specification.

At least the following decisions remain open:

1. **Asymptotic domain.** The protocol defines finite PUB and WIDE grids but does not formally define the classification domain as a compactified interval including `κ = ∞`, or state the role of the lower boundary.
2. **Limit construction.** “Derived or rigorously converged” leaves two materially different routes available after results are seen.
3. **Coverage of the derivation.** The existing numerical verification is scoped to one centre condition and three solutes; P0-G8 concerns all declared groups and calibration conditions.
4. **`J_min` computation.** A finite grid plus bracketed refinement is not, by itself, a global-profile proof.
5. **Error construction.** The sources, combination, and validation of asymptotic, profiling, optimization, discretization, and floating-point error are not specified.
6. **Threshold interval.** The protocol gives tolerance families but not the interval arithmetic required when `J_min` and `J_inf` are themselves bounded quantities.
7. **Global topology.** No root-isolation or adaptive interval algorithm is named; no rule addresses disconnected near-optimal sets, tangencies, or components adjoining infinity.
8. **Response shoulder.** The derivative aggregation across conditions, inventory profiling treatment, threshold values, crossing rule, and no-crossing disposition are unspecified.
9. **Headline rule across groups.** “Most groups” appears in the branch logic but is not a frozen numeric aggregation rule for H1.
10. **Inconclusive branch.** Boundary-indeterminate is defined locally, but the programme-level consequence of mixed, threshold-dependent, or numerically unresolved groups is not fully enumerated.

These are not cosmetic details. Each can alter whether a group is classified as `tail_included`, `tail_excluded`, or `boundary_indeterminate`, and whether H1 leads the paper.

### Required disposition

No production-data P0-G8 run, archive generation, partial-output inspection, or threshold tuning is authorized until the exact contract in §7 below is frozen.

---

## B3 — P0-G0’s declared prerequisites are still open

**Severity:** critical  
**Disposition:** blocks P0-G0 mechanically and scientifically

The manifest currently records:

- `operative_status: candidate`;
- P0-G0: `open`;
- P0-G1a: `open`;
- P0-G3a: `open`;
- P0-G8: `open`, dependent on P0-G0;
- no P0-G0 closure record;
- no frozen content commit;
- no frozen hashes.

The initial ledger, initial scope matrix, and reconciliation exist, but existence is not closure. Their gates require a reviewed closure record with criteria, evidence-unit scope, deliverable hashes, and producer or generation provenance.

### Required disposition

P0-G1a and P0-G3a must close before P0-G0. Their closure records must bind the exact initial artefacts that will serve as the pre-analysis baseline.

---

## B4 — The pre-freeze R0a premise audit has not been made an inspectable prerequisite

**Severity:** critical  
**Disposition:** blocks P0-G0

The plan says R0a occurs **before** the protocol freeze because discovering a missing premise later would force a deviation or second freeze. Yet:

- R0a is not a manifest gate or explicit P0-G0 dependency;
- no R0a deliverable is listed under P0-G0;
- no premise-audit closure record is identified;
- the manifest contains no machine-inspectable premise record.

A prose review round that is mandatory before freeze must be represented by an inspectable artefact and bound into closure.

### Required disposition

Add either:

- a distinct `P0-R0a` gate on which P0-G0 depends; or
- an explicit R0a deliverable and criterion inside P0-G0.

Recommended artefacts:

```text
docs/paper1_resource/PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.md
docs/paper1_resource/PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json
docs/paper1_resource/gates/P0-R0A_CLOSURE.json
```

Every load-bearing premise should be recorded with: claim/premise ID, premise type, evidence or explicit open/scoped disposition, evidence path and locator, affected gate, failure consequence, and reviewer disposition.

---

## B5 — The initial assurance baseline is not yet safe to make immutable

**Severity:** critical  
**Disposition:** blocks P0-G1a/P0-G3a closure

The plan accepts but has not implemented TAX-01 and LED-01/02. The present ledger still uses a single `robustness` field, uses free-text `source_artefact` strings rather than structured path + locator + hash bindings, and does not cleanly separate a falsifying result from a scope-limiting result. The scope matrix uses the same older two-field representation.

At the same time, the initial ledger declares that it **must not be regenerated**. Freezing it now would preserve a schema the operative plan has already judged inadequate; repairing it later would either violate the immutability declaration or require an avoidable baseline exception.

### Required disposition

Implement the accepted taxonomy and ledger schema **before** closing P0-G1a and P0-G3a. Then generate the initial baseline once, bind its hashes, and make that corrected version immutable.

At minimum, separate:

- evidence basis/type;
- validation provenance;
- observed result behavior;
- assurance status;
- claim status;
- falsifier;
- scope limiter;
- evidence path;
- JSON pointer, line locator, or symbol;
- input hash;
- producer hash;
- evidence artefact hash.

---

## B6 — The normative bundle contains stale and contradictory references

**Severity:** major, but freeze-blocking  
**Disposition:** repair before freeze

Current examples include:

- the protocol names V2.2 rather than V2.2.1 as the operative plan;
- the initial claim ledger names V2.2;
- the initial scope matrix names V2.2;
- the plan says gate definitions are authoritative in a YAML manifest although the operative manifest is JSON;
- the plan refers in several places to unsuffixed ledger/matrix paths while the actual baseline paths use `_INITIAL`;
- the reconciliation still describes the removed YAML manifest and the earlier scanner behavior.

A controlled normative bundle cannot be frozen while its members disagree about which plan, manifest, and baseline artefacts are operative.

### Required disposition

Run a fail-closed cross-reference audit across every normative-bundle member. No obsolete V2.2, YAML, or unsuffixed-baseline reference may remain unless explicitly marked historical.

---

## B7 — The two-stage activation design is not yet implementable as written

**Severity:** critical  
**Disposition:** blocks candidate-frozen and operative status

The manifest’s `normative_bundle` includes the manifest itself, while the same manifest contains `activation.frozen_hashes`. The plan requires the freeze commit to record the SHA-256 of **every** bundle member. Adding the manifest’s own hash changes the manifest, which changes the hash. There is no ordinary byte-level fixed point.

This is a distinct self-reference from the commit-SHA problem V2.2.1 correctly identified.

### Required disposition

Use one of these designs:

#### Preferred: separate immutable freeze record

1. Keep the mutable status manifest outside the content set it hashes.
2. Create `PAPER_A_NORMATIVE_FREEZE_RECORD_V1.json`.
3. The freeze record enumerates and hashes every normative content file **except itself** and identifies the freeze schema/version.
4. Freeze commit F contains the final normative files and freeze record.
5. Activation commit A changes only the mutable manifest/status metadata and records F plus the freeze-record hash.
6. Tests read every file from F (`git show F:path`), recompute its hash, compare it with the record, and verify the working tree remains byte-identical.

#### Alternative: canonical manifest projection

Define a canonical serialized projection that excludes activation/status/hash fields, hash that projection, and test the canonicalization adversarially. This is more complex and easier to misunderstand; the separate freeze-record design is preferable.

---

## B8 — `candidate-frozen` and activation identity are weakly enforced

**Severity:** critical  
**Disposition:** blocks activation

The present integrity test:

- validates nonempty hashes only for `operative`, not `candidate-frozen`;
- iterates over whatever entries happen to exist in `frozen_hashes`, rather than requiring exact coverage of the normative bundle;
- checks an operative commit value only as 40 hexadecimal characters;
- does not verify that the commit exists;
- does not compare each recorded file with the tree at F;
- does not establish that activation commit A changed only allowed control metadata;
- does not verify that every bundle path exists at F.

A fabricated SHA, partial hash map, or unhashed bundle member could therefore satisfy the current shape of the control.

### Required disposition

Add tests that require:

1. exact set equality between required content paths and recorded hashes;
2. full 64-hex SHA-256 validation for every content hash;
3. hash verification in both `candidate-frozen` and `operative` states;
4. `git cat-file -e F^{commit}`;
5. `git show F:path` for every frozen path;
6. recomputation of each hash from F’s tree;
7. current-tree equality with F for every normative file;
8. an activation-diff allowlist;
9. activation commit A to have F as its first parent or otherwise explicitly prove ancestry;
10. any post-activation normative change to require a new protocol version and append-only deviation.

---

## B9 — P0-G0’s current pass criterion is too weak

**Severity:** major, but freeze-blocking  
**Disposition:** strengthen before closure

The human-readable gate criterion says essentially that the protocol is committed before the scientific gates and deviations are append-only. The manifest lists only the protocol as a P0-G0 deliverable.

That does not establish:

- protocol completeness;
- closure of all preconditions;
- completion of R0a;
- consistency of the normative bundle;
- exact input and producer bindings;
- successful candidate-freeze and activation;
- absence of a scientific run before activation.

### Required disposition

P0-G0 should pass only when its closure record proves all of the following:

```text
protocol_complete = true
all_required_specification_ids_disposed = true
P0-G1a = passed
P0-G3a = passed
R0a = passed
normative_bundle_cross_references_clean = true
freeze_record_complete = true
candidate_frozen_hash_verification = passed
activation_commit_verification = passed
pre_activation_scientific_run_count = 0
```

---

## 5. Why freezing now would damage the paper

P0-G8 is not a routine computation. It decides whether the paper may say that the upper profile remains operationally acceptable, whether the result is threshold-dependent, or whether the tail is excluded.

The following post-result choices could move that classification:

- using a finite `κ = 500` cap versus the analytical endpoint at infinity;
- choosing one asymptotic-convergence route over another;
- changing the objective tolerance formula;
- treating uncertainty in `J_min` and `J_inf` symmetrically or not;
- assuming profile monotonicity rather than isolating all components;
- using an endpoint, maximum, mean, or weighted norm for the response shoulder;
- selecting the shoulder threshold after seeing where the curve bends;
- deciding how many groups constitute a paper-level “most groups” result;
- suppressing or retaining mixed and threshold-dependent classifications.

The pivot’s central methodological claim is that prediction and kinetic identification must not be conflated. The project must therefore be especially strict about not conflating a result with a result-dependent operational definition of identification.

---

## 6. What may and may not proceed now

### Authorized before freeze

- complete the protocol and accepted specification items;
- derive the asymptotic operator and error bounds symbolically without evaluating campaign outcomes;
- implement unit tests against fixed toy/synthetic fixtures;
- implement archive schemas and dry-run validation;
- complete taxonomy and ledger migration;
- complete R0a;
- repair bundle references and activation controls;
- create producer scaffolding that cannot access production inputs;
- run existing assurance and non-scientific integrity tests.

### Not authorized before freeze

- execute P0-G8 against campaign data;
- generate or update `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json`;
- inspect partial `J_inf`, profile-boundary, or shoulder outputs;
- tune domains, thresholds, root-finding settings, or error budgets using campaign results;
- run P0-G4, P0-G5, P0-G6, P0-G7, or P0-G9;
- draft results, title, abstract, discussion, or contribution bullets;
- silently edit the pre-analysis ledger after a scientific output is viewed.

Existing exploratory archives may remain as historical/exploratory evidence. They must not be used to finish the frozen choices.

---

## 7. Minimum complete P0-G8 protocol contract

The revised protocol should specify each item below exactly. This is the minimum needed to authorize the first scientific gate.

### 7.1 Data and evidence unit

Freeze:

- the exact input files and SHA-256 hashes;
- the included rows and exclusion rules;
- the six variety–solute groups or any different grouping;
- the calibration conditions per group;
- the positivity and missing-value rules;
- the treatment of tied weighted medians;
- the unit of analysis and any paper-level aggregation rule.

No group may be added, removed, merged, or reweighted after output inspection without a deviation.

### 7.2 Parameter domain and endpoint

Recommended definition:

```text
classification domain: κ ∈ [0.15, ∞]
PUB and WIDE: finite diagnostic grids only
κ = ∞: analytical/verified endpoint, not approximated by κ = 500
```

The protocol must state whether the lower bound is merely inherited support or part of the inferential claim. It must not call right-censoring at `κ = 500` unboundedness.

### 7.3 Exact objective definitions

For every group, freeze:

```text
J(κ)    = min over I > 0 of MAPE(y, I f(κ))
J_min   = inf over κ in the declared domain of J(κ)
J_inf   = min over I > 0 of MAPE(y, I f_inf)
```

The minimizing `I` must use the exact weighted-median solution. The protocol must define the returned representative when the minimizing set is an interval, while retaining the entire interval for audit.

### 7.4 Limit construction

Choose one primary method before results:

1. an analytical matrix/operator limit with a derived remainder bound; or
2. a rigorously specified numerical limit procedure with predetermined sequence, norm, tolerance, and stopping/failure rule.

Recommended: use the analytical operator limit as primary and a high-`κ` numerical sequence as a verification control, not as an alternative selected after the result.

Apply and verify the construction at every declared calibration condition and group. The existing centre-condition time-integrator check is supporting control evidence, not a substitute.

### 7.5 Verified intervals

Report intervals, not a scalar plus an informal tolerance:

```text
J_min ∈ [L_min, U_min]
J_inf ∈ [L_inf, U_inf]
T     ∈ [L_T, U_T]
```

For relative tolerance `q`:

```text
T_rel(q) = (1 + q) J_min,  q ∈ {0.05, 0.10, 0.20}
```

For absolute tolerance `a`:

```text
T_abs(a) = J_min + a,  a ∈ {0.10 pp, 0.25 pp}
```

The threshold interval must propagate the `J_min` interval. Recommended classification:

```text
U_inf < L_T  -> tail_included
L_inf > U_T  -> tail_excluded
otherwise    -> boundary_indeterminate
```

This is preferable to constructing one pooled `ε` unless the protocol proves that the pooled bound is conservative.

### 7.6 Error budget

Freeze the decomposition and combination of:

- asymptotic-limit remainder;
- spatial/numerical operator error relevant to P0-G8;
- exact-profile arithmetic/tie handling;
- global minimum/root-isolation tolerance;
- floating-point error;
- any interpolation or derivative error used for the shoulder.

Each component needs a verification test or an explicit conservative bound. Display precision is never an error estimate.

### 7.7 Global profile topology

Do not assume one minimum or monotonic tails. Freeze an adaptive algorithm that:

- works on `log κ` over the finite portion;
- brackets and refines every crossing of `J(κ) - T`;
- checks tangencies and unresolved intervals;
- reports every connected component;
- identifies components touching the lower endpoint;
- represents a component adjoining `κ = ∞` explicitly;
- fails to `topology_unresolved` rather than silently returning one interval.

### 7.8 Response shoulder

The shoulder is descriptive model sensitivity, not the objective-profile boundary. Freeze:

- the derivative definition;
- whether inventory `I` is held fixed or re-profiled;
- aggregation over conditions/outputs;
- the primary threshold and sensitivity family;
- interpolation/root rule;
- no-crossing and multiple-crossing dispositions.

A defensible conservative choice is to use the maximum absolute log sensitivity over declared outputs to identify when **all** outputs are weakly sensitive, with a predeclared threshold family such as `{0.10, 0.05, 0.01}`. This is a recommendation, not permission to choose the member that best aligns with `J_inf`.

### 7.9 Group and programme-level decision rules

Freeze the exact language for:

- all six included;
- five of six included;
- mixed included/excluded;
- any boundary-indeterminate group;
- classification that changes across tolerance conventions;
- numerical failure in one or more groups.

Recommended conservative paper-level rule:

> H1 may lead only if the classification is tail-included for at least five of six groups under both the 10% relative rule and at least one absolute rule, with no tail-excluded group and no unresolved numerical failure. Otherwise report group-specific and threshold-dependent results without the broad headline.

The exact rule can differ, but it must be fixed before the run.

### 7.10 Archive and reproducibility contract

The P0-G8 archive should record:

- protocol version and frozen-content commit;
- producer path and hash;
- executable command;
- environment and package versions;
- all input paths and hashes;
- group definitions;
- full objective/tolerance specification;
- method and error-budget identifiers;
- `J_min`, `J_inf`, thresholds, and intervals;
- all connected components;
- shoulder results;
- per-group classification under every convention;
- failures and warnings;
- branch consequence;
- archive hash;
- a substantive reproduction or byte-verification command.

A file-existence check is not reproduction.

---

## 8. Protocol-wide scientific specifications still required

Even though P0-G8 runs first, the current architecture intentionally freezes all P0-G4…G9 analytical choices before any result. Preserve that protection unless the gate architecture is formally revised.

### P0-G6 / RSI

Freeze:

- exact RSI formula;
- fixed weight convention;
- complete design list;
- all `κ` evaluation locations;
- exact MAPE profile-width definition;
- treatment of right-, left-, and doubly censored profiles;
- named concordance statistic and tie rule;
- minimum effect/admission rule;
- positive-control generator;
- median-switch negative control.

### P0-G9 / target map

Freeze:

- every map family;
- the scored-condition exclusion unit;
- whether upstream conductivity-polynomial fitting also excludes the scored condition;
- raw-support sufficiency rule;
- adaptation counts and placements;
- nested selection procedure;
- uncertainty propagation;
- exact impossibility criterion and H3 demotion branch.

### P0-G5 / estimation policy and propagation

Freeze:

- regularization coordinate (`κ`, `log κ`, or another);
- penalty normalization and objective scaling;
- tuning branch;
- selection data and nesting;
- dominance/no-winner definition;
- operational-profile envelope construction;
- objective-family envelope construction;
- how P0-G8’s result changes H4 wording.

### P0-G7 / observation operators

Freeze:

- synthetic generator and version;
- true `I` and `κ` grids;
- observation schedules;
- covariance matrices and heteroscedastic rules;
- mismatch forms and magnitudes;
- resource-cost vector and units;
- budget levels;
- replicate count and seeds;
- recovery, bias, interval/coverage, and prediction metrics;
- positive-control pass criterion;
- study-level success and inconclusive rules.

### P0-G4 / LOCO-WIDE

Freeze the enumerated factorial:

```text
arms × map protocols × objectives × folds × policy branches
```

Record the exact expected run count, allowed failure states, retry policy, and failure-retention rule.

### Taxonomy and claim ledger

Complete TAX-01, LED-01, and LED-02 before freezing the initial baseline.

---

## 9. Required repair and closure sequence

Do not open a scientific execution cycle yet. Use one focused protocol-completion and activation cycle in this order:

1. **Create the complete protocol revision.** Prefer `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V2.md`; retain V1 as a classified draft/historical record.
2. **Implement TAX-01 and LED-01/02.**
3. **Regenerate the corrected initial ledger and initial scope matrix once.**
4. **Repair all stale cross-references** across plan, protocol, manifest, ledger, matrix, and reconciliation.
5. **Complete R0a** and archive its premise matrix.
6. **Close P0-G1a** with a hash-bound closure record.
7. **Close P0-G3a** with a hash-bound closure record.
8. **Add a protocol-completeness matrix** mapping every PRO-01…08, SCI-01…04, TAX-01, and LED-01/02 item to an exact section, schema field, and test.
9. **Repair activation self-reference** using a separate freeze record.
10. **Strengthen candidate-frozen and operative tests** as described in B8.
11. **Create freeze commit F** with no scientific outputs.
12. **Verify F independently:** exact bundle coverage, hashes, commit existence, tree content, clean scanner, R0a, and prerequisite closures.
13. **Create activation commit A** changing only allowed control metadata.
14. **Close P0-G0** in A with a hash-bound closure record.
15. **Confirm the manifest says `operative`, P0-G0 says `passed`, and P0-G8’s only dependencies are passed.**
16. **Run P0-G8 exactly once under the frozen producer contract.**
17. **Retain every failure and branch outcome.** No silent rerun with revised scientific choices.

---

## 10. Acceptance checklist for a renewed freeze request

P0-G0 may be frozen only when every box is satisfied.

### Scientific completeness

- [ ] PRO-01…08 implemented
- [ ] SCI-01…04 implemented
- [ ] TAX-01 implemented
- [ ] LED-01 and LED-02 implemented
- [ ] P0-G8 domain includes an explicit infinity endpoint
- [ ] `f_inf` construction and verification route fixed
- [ ] `J_min`, `J_inf`, threshold, and interval formulas fixed
- [ ] global topology algorithm fixed
- [ ] response-shoulder definition and thresholds fixed
- [ ] group-level and programme-level branch rules fixed
- [ ] no campaign output inspected while choices remained open

### Pre-freeze assurance

- [ ] R0a complete and inspectable
- [ ] P0-G1a passed with closure record
- [ ] P0-G3a passed with closure record
- [ ] corrected initial ledger declared immutable only after schema completion
- [ ] every claim bound to precise evidence locators and hashes
- [ ] all bundle cross-references point to V2.2.1 or its approved successor
- [ ] no stale YAML reference remains
- [ ] no unsuffixed path ambiguously names an `_INITIAL` artefact

### Activation integrity

- [ ] self-hash problem removed
- [ ] freeze record exact and complete
- [ ] candidate-frozen state enforces all hashes
- [ ] freeze commit exists and contains every normative file
- [ ] hashes recomputed from F’s tree match
- [ ] activation diff is allowlisted
- [ ] current normative content remains byte-identical to F
- [ ] P0-G0 closure binds protocol, premise audit, prerequisite closures, freeze record, and activation evidence
- [ ] manifest records `operative`
- [ ] P0-G8 remains unrun until all of the above pass

---

## 11. Paste-ready implementation directive

```markdown
# PAPER 1 — P0-G0 PROTOCOL COMPLETION AND ACTIVATION REPAIR

## Authority

- Reviewed repository commit: `9c52c94edb27b461b6e7a4d471d29f3cef9d053e`
- Disposition: `PAPER_1_P0_G0_FREEZE_WITHHELD`
- P0-G8 and every other P0 scientific gate remain unauthorized.
- This cycle is protocol/control work only. Do not run production-data analyses or generate P0 result archives.

## Objective

Produce a freeze-ready, internally consistent normative bundle that fully implements
PRO-01…08, SCI-01…04, TAX-01, and LED-01/02; completes R0a; closes P0-G1a and
P0-G3a; and provides an implementable, adversarially tested two-stage freeze/activation
ceremony.

## Mandatory work

1. Supersede the draft protocol with a complete versioned protocol.
2. Fully specify P0-G8:
   - domain including `κ = ∞`;
   - `f_inf` derivation and independent verification;
   - exact `J(κ)`, `J_min`, `J_inf`, and weighted-median tie handling;
   - interval-based threshold classification;
   - complete numerical-error budget;
   - adaptive global-topology/root-isolation algorithm;
   - response-shoulder derivative, aggregation, thresholds, and failure rules;
   - group and programme-level branch rules;
   - archive/reproduction schema.
3. Complete the remaining P0-G4/G5/G6/G7/G9 protocol choices enumerated in plan §12.
4. Implement the accepted taxonomy and structured claim-to-evidence bindings before
   declaring the initial ledger immutable.
5. Complete and archive R0a.
6. Repair every stale plan/version/path/JSON-versus-YAML reference.
7. Replace self-hashing with a separate immutable freeze record.
8. Enforce exact hash coverage in both `candidate-frozen` and `operative` states.
9. Verify freeze commit existence and tree content; restrict activation commit to an
   explicit metadata diff.
10. Add hash-bound closure records for P0-G1a, P0-G3a, R0a, and P0-G0.

## Prohibited

- No P0-G8 campaign run.
- No `J_inf`, profile-boundary, or shoulder output inspection.
- No P0-G4/G5/G6/G7/G9 execution.
- No result narrative, title, abstract, discussion, or contribution drafting.
- No tuning scientific choices against existing or partial P0 outputs.

## Required terminal disposition

Return one of:

- `P0_G0_FREEZE_READY_PR_OPEN` — all work complete in an open, unmerged PR; no
  scientific result generated; provide head/tree, changed paths, tests, closure evidence,
  freeze-record design, and exact residual blockers; or
- `P0_G0_FREEZE_NOT_READY` — identify each unmet acceptance item and leave all
  scientific gates blocked.

Do not set the plan operative and do not mark P0-G0 passed in the implementation PR.
Freeze commit F and activation commit A are separate, subsequent authority-controlled
steps.
```

---

## 12. Final recommendation

Do **not** freeze the current P0-G0 protocol.

Authorize one narrow **protocol-completion and activation-repair cycle**. Once that cycle is reviewed and the two-stage freeze is validly completed, P0-G8 should run first, exactly as the plan intends. No further conceptual pivot is needed before then.
