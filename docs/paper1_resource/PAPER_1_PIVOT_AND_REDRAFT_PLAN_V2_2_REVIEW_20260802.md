# Review of `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md`

**Review date:** 2 August 2026 (America/Chicago)  
**Document reviewed:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md)  
**Immutable reviewed snapshot:** [`dac4e3ca2070a773606875b1e2755e05f8169cf9`](https://github.com/trbrewer/puckworks/commit/dac4e3ca2070a773606875b1e2755e05f8169cf9)  
**Prior review:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1_REVIEW_20260801.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1_REVIEW_20260801.md)  
**Recommended disposition:** **APPROVE THE SCIENTIFIC DIRECTION; WITHHOLD OPERATIVE STATUS PENDING A NARROW V2.2.1 CONTROL-AND-PROTOCOL PATCH. DO NOT YET FREEZE P0-G0 OR START P0-G4–P0-G9.**

---

## 1. Executive assessment

V2.2 is a major improvement and, scientifically, is close to the plan that should govern the redraft. It accepts the prior review's substantive corrections rather than merely changing tone. In particular, it now:

- separates a finite large-`κ` **model-response limit** from the data- and tolerance-dependent classification of the profiled objective;
- gives H1 the necessary included/excluded/boundary-indeterminate upper-tail branches;
- elevates the exact weighted-median solution of the production-MAPE level profile from an implementation detail to a formal result;
- keeps the weighted-`L2` sensitivity identity separate from the nonsmooth MAPE objective;
- preserves the coarse/fine reversal in the target-flow-map ablation;
- distinguishes retrospective campaign evidence, same-campaign cross-fitted protocol emulation, and genuinely prospective data;
- separates point-estimation policy from uncertainty or sensitivity propagation;
- places initial claim and scope controls before the proposed analysis freeze;
- adopts a conservative paper branch if the hydraulic or observation-operator results do not survive; and
- states the physical-validation and novelty boundaries much more honestly than the earlier plans.

The central scientific proposition is now compelling and appropriately bounded:

> **Predictive performance of matched whole-cup espresso endpoints and localisation of a model-specific mass-transfer-rate multiplier are different achievements, supported by potentially different information channels.**

I do **not** recommend another conceptual pivot. I also do not recommend returning to the original pooled −0.394 percentage-point headline. The remaining defects are concentrated in two areas:

1. **The new assurance system still claims more than it mechanically enforces.** The integrity test is not fully fail-closed, does not discover unclassified claim surfaces, and strips the exact JSON and Python string content that several banned-assertion rules are meant to inspect.
2. **The proposed “frozen” protocol still leaves load-bearing analytical choices unresolved.** The RSI metric, censored-profile treatment, regularisation form, policy-selection branch, target-map adaptation design, synthetic noise/mismatch matrix, resource costs, success metrics, and several asymptotic details remain selectable after approval.

These are correctable without changing the paper's scientific focus. A focused V2.2.1 should repair the control surface, complete the protocol, reconcile the remaining active assertions, and then activate the plan through an immutable two-stage freeze.

### 1.1 Decision summary

| dimension | disposition |
|---|---|
| scientific pivot | **approve** |
| H1/H2 conceptual structure | **approve with specified analytical refinements** |
| H3 evidential framing | **approve; keep secondary until P0-G9** |
| H4 two-axis framing | **approve; make conditional on P0-G8 and define policies fully** |
| manuscript architecture | **approve provisionally** |
| title | **retain as a working title only, pending P0-G8–P0-G10** |
| manifest and integrity control | **not yet adequate for operative status** |
| P0-G0 protocol | **draft, not yet genuinely frozen** |
| new P0-G4–P0-G9 runs | **hold until V2.2.1 and activation** |
| substantive manuscript drafting | **continue to prohibit** |

### 1.2 Blocking findings at a glance

| ID | finding | severity | required before operative status? |
|---|---|---:|---:|
| GOV-01 | `pytest.importorskip("yaml")` permits the supposedly fail-closed control to skip | critical | yes |
| GOV-02 | no exhaustive discovery of claim surfaces; the active protocol is not classified | critical | yes |
| GOV-03 | blanket quote stripping makes generic JSON/Python banned-assertion checks ineffective | critical | yes |
| GOV-04 | gate closure is bound only to file existence, not immutable content, schema, producer or evidence hash | critical | yes |
| GOV-05 | initial and final ledgers/matrices use the same paths, so final regeneration can erase the baseline | critical | yes |
| GOV-06 | `operative_commit` has no implementable self-pinning ceremony and is not validated | major | yes |
| REC-01 | active producer/archive assertions remain inconsistent with V2.2's current position | major | yes |
| PRO-01 | P0-G0 leaves important analytical choices open | critical | yes |
| SCI-01 | H1 needs an exact domain, threshold interval and complete numerical-error construction | major | before P0-G8 |
| SCI-02 | RSI is not defined or frozen sufficiently for P0-G6 | major | before P0-G0 |
| SCI-03 | P0-G9's map families, exclusion unit, adaptation counts and placement rules are not frozen | major | before P0-G0 |
| SCI-04 | P0-G5's regulariser, tuning branch, comparison metrics and propagation construction are incomplete | major | before P0-G0 |
| SCI-05 | P0-G7 remains a study outline rather than an executable frozen simulation protocol | major | before P0-G0 |
| TAX-01 | “robustness” mixes provenance, result pattern, assurance and claim status in one mutually exclusive field | major | before P0-G1a passes |
| SEQ-01 | premise audit R0 occurs too late and P0-G10 lacks an executable external handoff | major | before activation |

---

## 2. What V2.2 gets right and should be retained

## 2.1 H1 now has the correct logical structure

The most important scientific correction is complete in concept. V2.2 no longer infers weak localisation merely from a finite response limit. It states that the asymptotic objective `J_inf` must be compared with a predeclared operational threshold, with a genuine boundary-indeterminate branch. It also states that the finite scan to `κ = 500` is provisional and that real espresso's occupancy of this regime is untested.

Retain:

- the separation of response shoulder, objective boundary and physical interpretation;
- the exact weighted-median level profile;
- the three-way asymptotic decision;
- threshold sensitivity across relative and absolute conventions;
- reporting of all connected components rather than a single interval; and
- the prohibition on calling a finite-domain right-censored result “unbounded.”

## 2.2 The exact MAPE result provides a real analytical contribution

For positive observations and positive model factors,

\[
\operatorname{MAPE}(I,\kappa)
= \frac{100}{n}\sum_i \frac{f_i(\kappa)}{y_i}
\left|I-\frac{y_i}{f_i(\kappa)}\right|,
\]

so an exact weighted median of `r_i = y_i/f_i` with weights `w_i = f_i/y_i` profiles the level. This removes scalar-optimiser uncertainty, makes median-switch kinks explicit, and supplies a transparent route to `J_inf` once the response limit is established.

This is more than a computational convenience. It can anchor the methods section and explain exactly why a smooth weighted-`L2` surrogate may agree in some regimes and fail in others.

## 2.3 H3 now reports the scientifically interesting heterogeneity

V2.2 correctly retains the grind-specific evidence:

- coarse M1−M2 median: **+1.234 pp**, positive in **9/9** folds;
- fine M1−M2 median: **−0.037 pp**, negative in **7/9** folds, with material fold-to-fold variation;
- pooled median: **0.524 pp**, which cannot be reconstructed from the two component medians.

The paper becomes more credible, not less, by showing that the apparent pooled benefit is coarse-driven. The fine result should remain visible wherever the pooled figure is shown.

## 2.4 H4 now distinguishes unlike objects

The plan correctly separates:

- **point-estimation policies:** free, fixed, regularised, independently constrained; and
- **propagation/reporting layers:** point only, operational-profile envelope, objective-family envelope.

This avoids the category error of ranking a prediction interval or sensitivity envelope as though it were another point estimator. Retain this two-axis architecture.

## 2.5 Same-data post-selection is now stated plainly

The protocol's mandatory statement is strong and should be preserved:

> The protocol is frozen after exploratory inspection of the campaign; it limits future analytical flexibility but does not create independent confirmation.

The distinction among post-selection frozen reanalysis, same-campaign cross-fitted protocol emulation, prospective model-based simulation, and genuinely prospective empirical testing is exactly right.

## 2.6 The conservative branch is appropriate

The plan does not require every intended contribution to survive. If RSI fails, the exact algebra and MAPE profiling remain. If the cross-fitted map does not retain the coarse result, H3 becomes a retrospective case study. If time-resolved observations do not improve recovery, the paper is instructed not to force the information-compression narrative.

That branch logic should remain central to execution.

---

## 3. Critical governance and reproducibility findings

## 3.1 The integrity control is still not fail-closed

### Finding

The manifest and test repeatedly describe the control as fail-closed. However, the manifest fixture contains:

```python
yaml = pytest.importorskip("yaml", reason="pyyaml absent on the minimum-dependency lane")
```

If PyYAML is absent, every test depending on the manifest is **skipped**, not failed. This is precisely the failure mode the new control says it has eliminated. The fact that PyYAML happens to be installed in one environment does not make the control fail-closed across supported lanes.

### Recommendation

Use one of these approaches:

1. **Preferred:** make the machine-readable manifest JSON, using only the standard library; or
2. import PyYAML normally and declare it as a required test dependency, so absence fails collection.

Do not use `importorskip` for a dependency required to interpret the authoritative control surface.

### Acceptance tests

- Run the integrity suite in the declared minimum-dependency environment; all 27+ controls must execute, not skip.
- Add a test or CI assertion that the count of skipped Paper 1 integrity tests is exactly zero.
- Treat missing parser support as a red build.

---

## 3.2 “Every active surface” is not enforced

### Finding

The test iterates only over paths already listed in `active_claim_surfaces`. It does not discover candidate claim surfaces and compare them with the classified set. Consequently, a newly added result archive, plan, protocol, producer or paper-facing document can remain unclassified and invisible to the scan.

The test docstring says:

> a new artefact that nobody classified fails rather than passing silently.

The implementation does not do that. A new unlisted file is never inspected.

There is already a concrete omission: `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md` is current, normative and carries operative terminology and decision rules, yet it appears in neither `active_claim_surfaces` nor `historical_exclusions`.

Future gate deliverables are also listed under `gates` but are not automatically required to become classified claim surfaces when created.

### Recommendation

Add an explicit candidate-surface discovery contract. For example:

```yaml
claim_surface_roots:
  - docs/paper1_resource
  - tools
  - puckworks/paper_a
claim_surface_globs:
  - "docs/paper1_resource/PAPER_A_*.json"
  - "docs/paper1_resource/PAPER_A_*.md"
  - "docs/paper1_resource/PAPER_1_*.md"
  - "tools/paper_a_*.py"
  - "puckworks/paper_a/*.py"
nonclaim_exclusions:
  - path: ...
    reason: ...
```

The test should calculate:

```text
candidate surfaces
= active + historical/audit + explicit non-claim exclusions
```

with no unclassified remainder and no overlap.

Also require every claim-bearing gate deliverable to be classified before the gate can pass.

### Acceptance tests

- Add `docs/paper1_resource/PAPER_A_UNCLASSIFIED_RESULT.json` in a temporary test repository and verify failure.
- Remove the protocol from all classifications and verify failure.
- Create a future gate deliverable without classification and verify failure.
- Verify that every current candidate surface is classified with a reason and authority status.

---

## 3.3 Blanket quote stripping defeats the intended JSON and Python checks

### Finding

The scanner removes all text inside straight quotes, curly quotes, backticks and single quotes before applying the banned patterns:

```python
_QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”|`[^`\n]*`|\'[^\'\n]*\'')
```

This is suitable only for a narrow Markdown mention-versus-assert heuristic. Applied to JSON and Python, it removes the semantic content the rules are intended to inspect.

Concrete demonstration using the shipped `_asserted` function:

```text
"verdict": "PHYSICAL"                  -> " :  "
"M0_to_M2": "RATE RECALIBRATION ALONE" -> " :  "
label = "RATE RECALIBRATION ALONE"      -> "label =  "
```

Thus the generic rule for `"verdict": "PHYSICAL"` can never match a normal JSON object after preprocessing, and the rule for `RATE RECALIBRATION ALONE` cannot detect a JSON value or Python output label. One dedicated semantic test happens to inspect the saturation archive, but the general assurance claim remains false.

The blanket single-quote pattern can also remove substantial prose between apostrophes on the same line and does not distinguish historical quotation, code, output labels, comments and active assertions.

### Recommendation

Use file-type-aware inspection:

- **JSON:** parse and recursively inspect keys and scalar string values. Do not strip quotes.
- **YAML:** parse and recursively inspect scalar strings.
- **Python:** use `ast` and `tokenize` to inspect module/class/function docstrings, comments, string constants and output labels; apply explicit exemptions where a string is a historical mention.
- **Markdown:** strip fenced code only; handle quotations through explicit, reviewable exemption metadata rather than a blanket quote rule.

A robust exemption should state `path`, `rule_id`, `location/context`, `reason`, and optional expiry. “Anything in quotes is merely a mention” is not a safe semantic rule for producers and archives.

### Acceptance tests

Adversarial tests must prove that the scanner fails on:

1. `{"verdict": "PHYSICAL"}` in JSON;
2. `label = "RATE RECALIBRATION ALONE"` in Python;
3. the phrase in a Python docstring;
4. an unqualified assertion in Markdown block text; and
5. a permitted historical quotation only when an explicit exemption is present.

---

## 3.4 Gate closure is not evidence-bound

### Finding

A passed gate is currently checked only for existence of its listed deliverables. The test does not verify:

- a closure record;
- the gate-specific pass criteria;
- schema validity of the deliverable;
- the input, producer or output hashes;
- correspondence between the producer and archive;
- a closing commit;
- whether a passed deliverable changed afterwards; or
- whether all load-bearing values in the claim ledger match the archived evidence.

A placeholder file can therefore satisfy the current mechanical definition of a passed gate. A correct archive can also be modified after closure without invalidating the gate.

`P0-G2` is especially weak: it is a drafting-blocking gate with an empty `deliverables` list, so it can be marked passed without any inspectable evidence.

### Recommendation

Every gate should carry a closure object, for example:

```yaml
status: passed
closed_at_commit: <sha>
closure_record: docs/paper1_resource/gates/P0-G8_CLOSURE.json
criteria_version: 1
deliverables:
  - path: docs/paper1_resource/PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json
    sha256: ...
    schema: schemas/paper_a_asymptotic_profile_limits.schema.json
producer:
  path: tools/paper_a_asymptotic_profile_limits.py
  sha256: ...
```

The closure record should state each criterion, evidence pointer, result, caveat and adjudication. The test should recompute hashes and fail if content drifts.

Create a concrete P0-G2 deliverable, such as:

```text
docs/paper1_resource/PAPER_A_DISAGGREGATION_AUDIT.json
```

that enumerates every pooled claim, its component claims, weighting rule, source rows and page-level reporting requirement.

### Acceptance tests

- Mark a gate passed with a missing closure record: fail.
- Change one byte in a passed deliverable: fail.
- Supply an empty placeholder JSON: fail schema validation.
- Mark P0-G2 passed without a disaggregation audit: fail.
- Confirm every ledger number resolves to a path plus hash in a passed deliverable.

---

## 3.5 The initial baseline can be overwritten by the final reconciliation

### Finding

`P0-G1a` and `P0-G1b` both use `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json`. Likewise, `P0-G3a` and `P0-G3b` both use `PAPER_A_MODEL_SCOPE_MATRIX.md`.

The purpose of the initial artefacts is to detect claim and scope drift during execution. If the final step “regenerates” those same paths, the original baseline can be overwritten, defeating the reason for creating it.

### Recommendation

Preserve immutable initial and final states separately:

```text
PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json
PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_FINAL.json
PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_DIFF.json

PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md
PAPER_A_MODEL_SCOPE_MATRIX_V1_FINAL.md
PAPER_A_MODEL_SCOPE_MATRIX_V1_DIFF.json
```

Alternatively, use an append-only ledger with signed/hash-bound revisions, but do not replace the baseline.

### Acceptance tests

- The initial artefact hash remains unchanged from P0-G0 activation through final drafting.
- The final artefact explicitly references the initial hash.
- Every wording, status, evidence, scope and number change appears in a machine-readable diff with rationale.
- No final gate can close if the initial baseline is absent or altered.

---

## 3.6 `operative_commit` needs a feasible activation ceremony

### Finding

The plan says it becomes operative when the manifest sets `operative_status: operative` and pins `operative_commit`. The test checks only that the field is truthy. It does not validate SHA format, object existence, repository relationship or content equality.

There is also a self-reference problem: a commit cannot generally contain its own not-yet-known SHA. Editing the manifest to insert the resulting SHA changes the commit and therefore changes the SHA again.

### Recommendation

Use a two-stage activation:

1. **Freeze commit F:** contains the final normative plan bundle, with status `candidate-frozen` and hashes for all normative artefacts.
2. **Activation commit A:** changes only the control metadata, sets `operative_status: operative`, and records `operative_content_commit: F` plus the normative file hashes from F.

The test at A and descendants must verify that current normative content is byte-identical to F unless a formally versioned amendment is active. A signed tag pointing to F is another viable authority mechanism.

Do not call a bare non-null string an immutable pin.

### Acceptance tests

- Reject malformed or nonexistent SHAs.
- Reject a content commit that is not an ancestor of the current checkout.
- Reject any normative file whose current hash differs from its frozen hash.
- Require a new version/deviation record for any normative modification after activation.

---

## 3.7 Current status statements and manifest status are not reconciled

### Finding

The plan says Step 0A is done and the ledger, matrix and reconciliation are done. The manifest still marks `P0-G1a` and `P0-G3a` open. The protocol exists but P0-G0 is open, which is sensible pending approval; the initial gates' status is less clear.

This may be intentional because the plan is still a proposal, but the wording should distinguish:

- artefact drafted;
- artefact reviewed and hash-frozen;
- gate passed; and
- plan activated.

The integrity test does not compare human-readable status annotations with the manifest.

### Recommendation

Make the manifest the only status source and render the plan's status table from it, or use exact wording such as:

> “Initial artefact drafted; gate remains open until V2.2.1 approval and frozen-hash closure.”

Add a consistency test for any status text retained in the plan.

---

## 4. The active-claim reconciliation is not yet complete

## 4.1 The saturation producer still contains categorical and stale assertions

The active producer begins by calling the observation “the paper's central mechanism — the cup cannot see the kinetics.” That is stronger than V2.2 permits while `J_inf` and the actual MAPE profile classification remain open. It also uses old gate names `G3` and `G4`, even though those identifiers now mean different things or have been replaced.

Publication-facing comments, keys and terminal output still use unqualified “saturation,” including:

- `SATURATION_RATES`;
- `saturation_on_independent_path`;
- “deeply saturated”;
- “verifying the saturation”; and
- “saturation on the expm path.”

Internal legacy filenames may be retained for compatibility, but an active claim-bearing producer should use the current terminology in its docstrings, comments, output schema and interpretation.

### Required correction

Replace the categorical mechanism statement with something like:

> “The tested centre-condition response becomes weakly sensitive to further increases in `κ`; this check determines whether that finite-response behaviour is a BDF time-integration artefact within the declared semi-discrete model.”

Update old gate references and use `large_coefficient_limit`, `large_kappa_rates` or equivalent current names. If a legacy field must remain, mark it explicitly as a schema-compatibility alias.

## 4.2 The active rate-domain archive still uses withdrawn framing

`PAPER_A_RATE_DOMAIN_CHECK.json`, which is listed as an active claim surface, still contains:

- verdict `SATURATING_DEGENERACY` for all six groups;
- a question about whether a “transfer conclusion” survives widening; and
- terminology that predates the exact H1 tail classification.

This archive is useful historical evidence for finite-domain right-censoring, but it should not present the current inferential conclusion. Regenerate or rescope it as a preliminary finite-domain scan, with current terminology and an explicit statement that P0-G8 supersedes its verdict.

## 4.3 The active design archive already “admits” RSI while P0-G6 remains open

`PAPER_A_DESIGN_SEPARABILITY.json` states that RSI “screens designs” and is admitted as a screening tool based on an earlier Spearman analysis. V2.2 now requires a different, stricter P0-G6 evaluation against exact MAPE profiles at nominal and optimum `κ`, with controls. The manifest and claim ledger correctly keep P0-G6/C-PRO-01 open, but the active archive's interpretation is already affirmative.

Required action:

- mark the existing archive `pre_P0_G6_exploratory` and remove its admission verdict; or
- classify it historical and create a new active P0-G6 archive later.

Do not allow an active predecessor archive to decide the result before the frozen test runs.

## 4.4 The producer `--check` assurance is overstated

The reconciliation says producer `--check` modes reproduce regenerated archives. In `paper_a_information_parity.py`, `--check` only verifies that the archive exists and prints “archive present”; it does not recompute and compare the result.

This is not a reproducibility check. Either:

- make `--check` recompute a deterministic result and compare semantically or byte-for-byte; or
- rename it `--exists` and do not cite it as reproduction evidence.

For expensive analyses, create a separate verification mode that checks input hashes, producer hash, expected schema and selected invariant rows, while documenting that full reproduction is hand-run.

## 4.5 Whole-file “historical” exemptions for living ROADMAP/SPRINTS are unsafe

The commit adds new V2.2 status entries to `ROADMAP.md` and `SPRINTS.md`, while the manifest classifies both entire files as historical exclusions. Those new entries make current assurance claims, including that the control is fail-closed and scans every declared active surface.

A living audit log is not the same thing as a frozen historical artefact. Recommended options:

1. classify individual dated entries as historical records and put a prominent current-authority banner at the file top;
2. move immutable historical entries into a dedicated audit log and keep current status in a scanned active surface; or
3. define an `audit-log` class whose historical claim rows are exempt but whose current control statements are still checked.

Do not exempt an entire living file merely because it contains history.

---

## 5. The P0-G0 protocol is not yet sufficiently frozen

V2.2 says previous underspecification has been corrected and that P0-G0 freezes the next analyses. The protocol is much better, but several choices remain unresolved. Those choices are capable of changing the result and therefore must be selected before P0-G0 passes.

## 5.1 P0-G8 — asymptotic classification

### Remaining ambiguities

1. **Exact domain of the profile.** Is the inferential domain `κ ∈ [0.15,∞)`, `κ > 0`, or another physically declared set? The lower tail matters because `T` depends on the global/domain-specific `J_min`.
2. **Definition of `T`.** For relative tolerances, state `T_δ = (1+δ)J_min`; for absolute tolerances, state `T_Δ = J_min + Δ` in MAPE percentage points.
3. **Uncertainty in `T`.** The numerical error band must include uncertainty in `J_min`, not only `J_inf` and the asymptotic response.
4. **Proof of profile convergence.** Establish `f(κ) → f_inf`, positivity, and consequently `J(κ) → J_inf`; do not rely only on a finite sweep.
5. **Global topology algorithm.** Specify the adaptive grid, bracketing/root-finding procedure, lower and upper limits, and how disconnected components are certified.
6. **Response-shoulder threshold.** The protocol says “a declared threshold” but does not give one. Freeze a threshold family or a single primary threshold now.
7. **Boundary interval logic.** Use interval comparisons rather than a single scalar `ε` if `J_min`, `J_inf` and `T` each have verified bounds.
8. **Scope of the existing numerical evidence.** NUM-TIME-01 uses one centre condition and three solutes. Either narrow the passed gate and C-NUM-01 to that unit or derive/verify the limit across all conditions to support generic H1 wording.

### Recommended robust decision rule

For a relative rule `δ`, let verified intervals be:

```text
J_min ∈ [L_min, U_min]
J_inf ∈ [L_inf, U_inf]
T_δ ∈ [(1+δ)L_min, (1+δ)U_min]
```

Then:

```text
U_inf < lower(T_δ)  -> tail included robustly
L_inf > upper(T_δ)  -> tail excluded robustly
otherwise           -> boundary/numerically indeterminate
```

Use the analogous interval for `J_min + Δ`. Report operational uncertainty separately from empirical/model uncertainty; this is not a confidence interval.

## 5.2 P0-G6 — RSI admission

The protocol says designs, groups, `κ` locations, weights and censored-profile treatment are “predeclared,” but it does not actually enumerate or define them. The following must be frozen:

- expansion and formula for **RSI**;
- whether the primary quantity is `sqrt(Var_w(s))`, `W Var_w(s)`, `sqrt(W)·RSI`, or another form;
- fixed weight convention and whether a total-information companion is reported;
- exact design list;
- exact `κ` locations and whether “optimum” is full-support, design-specific or group-specific;
- derivative method and convergence check;
- exact MAPE profile-width definition;
- treatment of right/left/doubly censored and disconnected profiles;
- pairwise metric: Kendall `τ_b`, Spearman `ρ`, concordant-pair fraction or another named statistic;
- treatment of ties, unresolved designs and missing widths;
- minimum practical concordance, not merely “positive”; and
- exact positive and negative controls.

“Positive in 5 of 6 groups” permits a negligible positive value and does not state what happens when a group has too few resolved designs. A stronger prespecified rule could combine sign consistency with a minimum effect and a minimum number of evaluable pairs. Report every group and design regardless of admission.

## 5.3 P0-G9 — target-map protocol

The protocol still leaves the central adaptation design to be frozen later. Before P0-G0 closes, enumerate:

- every map family;
- the raw observations each family uses;
- the scored-condition exclusion unit, including all upstream fitted polynomials and derived quantities;
- candidate adaptation counts;
- candidate observation placements;
- the non-chemical selection rule for placement;
- uncertainty model for measured/fitted/derived hydraulic inputs;
- how extrapolation leverage is quantified;
- what constitutes “raw support permits”; and
- the exact impossibility criterion.

Cross-fitting must rebuild the entire upstream map without the scored condition. Removing only the final shot-time row while retaining a conductivity polynomial fitted with that row would still leak information.

The plan correctly states that same-campaign cross-fitting is not independent prospective validation. Retain that label even if the result survives.

## 5.4 P0-G5 — estimation policies and propagation

The following choices remain load-bearing:

1. **Regulariser form.** Specify whether the penalty is on `κ−1`, `log κ`, or another dimensionless coordinate, and define objective scaling. The same `λ` grid means different things under different parameterisations.
2. **Tuning branch.** “Either nested selection or a frozen no-tuning grid” is still a post-freeze choice. Select one now, or define a non-outcome-based branch rule now.
3. **Evaluation metrics.** Define primary grind-specific metrics, secondary pooled metrics, group-level reporting, stability criteria and any practical-equivalence margin.
4. **Winner definition.** The withdrawal rule says “if no policy wins,” but “wins” is undefined. Define dominance or state that the analysis is descriptive with no winner selection.
5. **Profile envelope.** Define how multiple connected components and weighted-median intervals are propagated into predictions.
6. **Objective-family envelope.** Define the Huber threshold and the exact relative-`L2`/SSE normalisations.
7. **Map uncertainty.** State whether it is fixed, propagated or treated in a separate sensitivity layer.

A defensible default is to report the complete frozen candidate grid with no post hoc winner and to reserve any recommendation for a genuinely nested calibration-only procedure.

## 5.5 P0-G7 — observation-operator study

The five stages are a good architecture, but the protocol is not executable without further choices. Freeze:

- true `κ` and inventory values;
- process conditions and observation times/endpoints;
- number of shots, fractions and assays per design;
- whether the combined operator is included—“optionally combined” must be resolved;
- noise distributions, magnitudes and correlation structures;
- basis for those magnitudes;
- model-mismatch magnitudes, not only mismatch categories;
- resource-cost weights and budget levels in physical units;
- Monte Carlo replicate count and seeds;
- recovery metrics: bias, RMSE, profile width, boundary rate, coverage if a valid interval is constructed, and predictive error;
- success criterion for “improves recovery”;
- adequacy criterion for the positive control; and
- an explicit inconclusive branch.

The resource-equated Pareto approach is preferable to equal observation counts, but a Pareto frontier cannot be reproduced without the cost vector and budget grid.

Use a different generator from the fitted model in the mismatch stages to avoid an inverse crime. The no-mismatch stage is still useful as a pipeline check, but should not carry physical design claims by itself.

## 5.6 P0-G4 — LOCO-WIDE factorial

“Every arm × map protocol × objective × fold predeclared” is a requirement, not yet an enumeration. Add the complete factorial matrix, including:

- arm definitions;
- map variants;
- objective variants;
- fold unit and exclusions;
- multiplier domain and refinement algorithm;
- level-profile tie handling;
- failure classification;
- outputs and aggregation; and
- expected run count.

This prevents accidental omission or selective rerunning of difficult cells.

---

## 6. Scientific comments and recommendations

## 6.1 H1 should distinguish a general model theorem from a centre-condition numerical check

The existing alternate-time-path verification is strong evidence that the observed centre-condition plateau is not a BDF time-integration floor. It is not yet evidence that every group and condition has the same asymptotic structure unless the structure follows analytically from the model.

Recommended route:

1. derive the large-`κ` reduced system or limiting response for the declared semi-discrete equations;
2. prove or numerically certify positivity and finite limits for all calibration conditions and groups;
3. use the matrix-exponential result as a numerical cross-check at representative conditions; and
4. scope NUM-TIME-01 to its actual one-condition, three-solute evidence unit.

Do not let a centre-condition verification silently support a universal sentence.

## 6.2 The exact MAPE proposition should be formal and unit-consistent

State explicitly whether `J` is a fraction or percentage. The factor of 100 does not change the minimiser, but it changes the numerical tolerance units. Include:

- assumptions `y_i > 0`, `f_i(κ) > 0`;
- the complete weighted-median minimiser set;
- deterministic tie/interval reporting;
- proof that the profiled objective is continuous where required;
- handling of zero, below-detection or invalid observations; and
- tests against exhaustive scalar minimisation over adversarial median-switch cases.

## 6.3 H3 should remain secondary until the full information lineage is reconstructed

The present result is a useful input ablation, but it remains conditioned on target-campaign hydraulic information and substantial fine-grind extrapolation. The paper should avoid implying that the map is a universally available pre-shot predictor.

Lead H3 results in this order:

1. per-row information timing and leakage status;
2. cross-fitted or impossibility result;
3. coarse/fine scores and fold rows;
4. map-uncertainty/extrapolation sensitivity; and
5. pooled summary only last.

If the map cannot be defensibly cross-fitted, retain H3 as a transparent retrospective case study and remove hydraulic language from the title/subtitle.

## 6.4 H4 should be conditional and should separate physical interpretation from practical localisation

Current H4 begins by asserting weak localisation while P0-G8 is open. Replace it with conditional wording:

> **If P0-G8 shows that `κ` is weakly or one-sidedly localised under a declared operational near-optimal set, its fitted value cannot be read as uniquely learned from the matched whole-cup endpoints. Independently of that outcome, interpreting `κ` as a transferable physical kinetic constant remains unsupported without external validation and model-discrepancy analysis.**

This preserves the physical caution even if `J_inf` excludes the upper tail and the profile becomes finite.

## 6.5 Avoid equating profile width with statistical uncertainty

The operational near-optimal set is a sensitivity convention. It is not a confidence set, credible interval or coverage-calibrated uncertainty statement. The plan generally respects this distinction. Keep it explicit in every figure legend and avoid words such as “identified with 90% confidence” or “uncertainty interval” unless a justified statistical model is added.

## 6.6 Dependent folds support descriptive stability, not nine independent replications

V2.2 correctly calls the nine leave-one-condition-out folds dependent. Continue to report all fold rows and medians, but do not attach binomial probabilities, standard errors based on `n=9`, or significance language to sign counts such as 9/9 or 7/9.

---

## 7. Evidence taxonomy and claim-ledger corrections

## 7.1 The two-field taxonomy is not actually orthogonal

The “robustness” vocabulary combines at least four different dimensions:

- assurance: `established-under-assumptions`, `verified-within-numerical-scope`;
- result behaviour: `heterogeneous`, `sensitivity-only`, `refit-stable`;
- validation provenance: `cross-fitted`, `externally-replicated`; and
- claim state: `unresolved`, `withdrawn`.

These are not mutually exclusive. A result can be cross-fitted **and** heterogeneous **and** refit-stable. Forcing one value loses information. This is already visible in the ledger: the coarse claim is `refit-stable`, while the fine claim is `heterogeneous`, although both arise from the same refit procedure and both are retrospective.

### Recommendation

Use separate fields or arrays:

```json
{
  "evidence_basis": "empirical-descriptive",
  "validation_provenance": ["same-campaign", "post-selection", "leave-one-condition-out"],
  "result_behaviour": ["refit-stable", "grind-heterogeneous"],
  "assurance": "numerically-reproduced",
  "claim_status": "provisional"
}
```

This is more expressive and reduces category drift.

## 7.2 “Falsifying result” often confuses falsification with scope limitation

Several ledger records describe a result that would not falsify the recorded claim:

- a cross-fitted map losing the coarse benefit does not falsify the retrospective campaign-conditioned arithmetic;
- `J_inf` excluding the tail does not falsify the statement that a finite scan to 500 was right-censored;
- a different spatial discretisation or richer physical model lacking a plateau does not falsify the statement that the declared semi-discrete model has one.

Separate:

- `reproduction_failure` — would show the stated result or calculation is wrong;
- `scope_limiter` — shows it does not generalise;
- `confirmatory_test` — tests a broader prospective claim;
- `withdrawal_rule` — determines manuscript treatment.

This will prevent a descriptive statement from being retroactively treated as a causal or prospective hypothesis.

## 7.3 Add immutable evidence pointers

The plan requires every bound number to match an artefact hash, but the ledger currently stores path strings rather than immutable hashes. Add:

- source path;
- source SHA-256;
- producer path and SHA-256;
- input-data hashes;
- JSON pointer or row key locating the value;
- generation commit; and
- estimand schema version.

Use arrays rather than semicolon-delimited path strings.

## 7.4 Narrow C-NUM-01 or expand its evidence

C-NUM-01's wording is broad, while its recorded unit is one centre condition and three solutes. Either:

- rewrite the claim to that tested condition; or
- support the general wording with the P0-G8 structural derivation and broader verification.

The latter is preferable for the paper, but the initial ledger should not assert it before the derivation exists.

---

## 8. Sequence and programme management

## 8.1 Run a premise audit before the final protocol freeze

The sequence places R0 after drafting. Because R0 asks whether every load-bearing premise has assurance appropriate to its type, it may identify missing analyses or controls. Discovering those after the protocol and draft are complete risks either an unplanned deviation or a second freeze.

Split R0:

- **R0a — pre-freeze premise audit:** before P0-G0 passes; identifies missing assumptions, tests and scope boundaries.
- **R0b — convergence premise audit:** after outputs are frozen and before manuscript drafting; checks that results did not introduce new premises.

Keep the later external rounds R1–R5.

## 8.2 Create an executable P0-G10 external handoff

The environment limitation is honest, but it currently creates a deadlock without an owner, protocol or completion package. Add:

```text
PAPER_A_NOVELTY_SEARCH_PROTOCOL.md
PAPER_A_NOVELTY_SEARCH_HANDOFF.md
PAPER_A_NOVELTY_POSITIONING.md
```

The protocol should freeze:

- databases;
- date ranges;
- query strings and fields;
- espresso, inverse-problem, variable-projection, practical-identifiability and experiment-design terminology;
- inclusion/exclusion rules;
- backward/forward citation searching;
- deduplication;
- closest-work matrix fields; and
- the rule for bounded contribution wording.

Assign a named external operator with database access. Do not leave a network-specific Cloudflare observation as the only execution plan.

## 8.3 Remove the assurance overclaim in §0

The sentence saying that the next failure mode “has to be one nobody has thought of” should be deleted. No finite integrity suite proves that unanticipated defects are excluded, and this review identifies additional specified failure modes.

Use:

> “The replacement control is intended to detect the enumerated failure classes and is tested adversarially. It reduces, but does not eliminate, the possibility of unanticipated assurance failures.”

## 8.4 Correct the “self-contained/four artefacts” statement

The plan is much more self-contained than V2.1, but its operative meaning still depends on the manifest, protocol, claim ledger, scope matrix and reconciliation, and future gate artefacts. It says “four artefacts” while naming more than four.

Use:

> “This plan is the human-readable member of a controlled normative bundle. The manifest enumerates the authoritative plan, protocol, initial claim ledger, scope matrix, reconciliation and subsequent gate artefacts, each with an immutable content hash.”

Avoid a fixed prose count that can become stale.

---

## 9. Recommended revised execution sequence

### Phase A — V2.2.1 control repair

1. Correct the fail-closed dependency issue.
2. implement exhaustive claim-surface discovery and file-type-aware scanning;
3. add adversarial tests;
4. classify the protocol and all current/future gate deliverables;
5. add gate closure records, schemas and hashes;
6. split initial/final ledgers and scope matrices;
7. reconcile the remaining active producer/archive assertions; and
8. define the two-stage activation mechanism.

### Phase B — pre-freeze assurance

9. Run R0a premise audit.
10. Finalise the initial claim ledger and scope matrix.
11. Complete—not merely outline—the P0-G4–P0-G9 protocol specifications.
12. Freeze the novelty-search protocol and external handoff.
13. Review the full protocol for outcome-selectable branches.

### Phase C — activation

14. Create freeze commit F containing the normative bundle and hashes.
15. Review/adjudicate V2.2.1.
16. Create activation commit A pointing to F.
17. Mark P0-G1a, P0-G3a and P0-G0 passed with closure records.

### Phase D — scientific execution

18. Run P0-G8 first because it can reverse the broad H1/H4 premise.
19. Run P0-G6 after the exact profile and asymptotic machinery is established.
20. Run P0-G9 before P0-G4 so the map protocol is fixed.
21. Run P0-G4, then P0-G5.
22. Run P0-G7 after the diagnostics and observation operators are fully defined.
23. Execute P0-G10 externally in parallel.

### Phase E — convergence and drafting

24. Freeze outputs and producer/input hashes.
25. Generate final ledger, scope matrix and machine-readable diffs.
26. Close P0-G2 through a disaggregation audit.
27. Run R0b and final P0-G10 adjudication.
28. Choose the supported paper branch, title and contribution list.
29. Draft the manuscript.
30. Run R1–R5.

---

## 10. Detailed action register

| ID | priority | action and method | objective | principal pitfalls | verification |
|---|---:|---|---|---|---|
| GOV-01 | P0 | remove `pytest.importorskip` for YAML or convert manifest to JSON | make the control genuinely fail-closed | hidden skip on minimum-dependency lane | zero Paper 1 integrity skips in every CI lane |
| GOV-02 | P0 | implement candidate-surface discovery from declared roots/globs | detect unclassified new claim surfaces | overly broad globs or silent exclusions | adversarial unclassified-file test fails |
| GOV-03 | P0 | replace blanket quote stripping with JSON/YAML/Python/Markdown-aware scanners | inspect semantic assertions in archives and producers | false positives from historical mentions | explicit exemption registry plus adversarial tests |
| GOV-04 | P0 | classify the current protocol and automatically require gate deliverables to be classified | close present and future coverage gaps | duplicated classifications | exact candidate = classified-set equality |
| GOV-05 | P0 | add gate closure records, schemas, hashes and producer/input bindings | make “passed” mean more than path existence | expensive full reproduction | tiered verification, with limitations stated |
| GOV-06 | P0 | create `PAPER_A_DISAGGREGATION_AUDIT.json` for P0-G2 | make the gate inspectable | audit generated from prose only | resolve each pooled claim to source rows and components |
| GOV-07 | P0 | split initial/final ledger and scope artefacts; generate diffs | preserve pre-analysis baseline | accidental overwrite | initial hashes immutable through programme |
| GOV-08 | P0 | implement two-stage freeze/activation | create a feasible immutable authority | confusing activation SHA with content SHA | activation commit verifies frozen-content commit and hashes |
| GOV-09 | P1 | validate manifest schema, SHA formats, DAG semantics and status transitions | prevent malformed control metadata | custom schema drift | JSON Schema or equivalent unit tests |
| REC-01 | P0 | rescope saturation producer wording, identifiers, output keys and gate references | align active producer with H1 status | breaking historical consumers | compatibility aliases documented and tested |
| REC-02 | P0 | regenerate/rescope rate-domain archive as preliminary finite-domain evidence | remove stale degeneracy/transfer verdicts | changing numerical evidence unintentionally | values unchanged; only schema/interpretation diff |
| REC-03 | P0 | demote current design-separability admission to exploratory/pre-P0-G6 | prevent pre-adjudication of RSI | losing useful earlier results | archive retained but current claim status open |
| REC-04 | P0 | make information-parity `--check` recompute and compare, or rename it | make reproducibility claim accurate | runtime cost | deliberate archive corruption causes check failure |
| REC-05 | P1 | replace whole-file historical exemption for living roadmap/sprint logs | prevent current assurance claims from escaping scan | historical rows causing false positives | explicit audit-log class and authority banner |
| PRO-01 | P0 | define `κ` profile domain, threshold formulas and interval-error rule | make P0-G8 executable | conflating numerical and empirical uncertainty | synthetic boundary cases exercise all three branches |
| PRO-02 | P0 | freeze response-shoulder threshold(s) and topology algorithm | separate shoulder from profile boundary reproducibly | threshold shopping | threshold family recorded before runs |
| PRO-03 | P0 | define RSI formula, designs, weights, locations, metric, ties and censoring | make P0-G6 unambiguous | rank results driven by censoring choices | positive/negative controls and full design table |
| PRO-04 | P0 | enumerate target-map families, exclusion unit, adaptation counts and placements | prevent H3 leakage and tuning | upstream polynomial leakage | per-row lineage proves scored condition exclusion |
| PRO-05 | P0 | define regularisation coordinate, objective scaling and tuning branch | make policy comparison reproducible | `λ` scale meaningless across coordinates | analytic/unit tests and frozen candidate table |
| PRO-06 | P0 | define policy metrics, dominance/equivalence and propagation construction | make “winner/no winner” meaningful | pooled reversal hidden | grind-specific primary reporting and component audit |
| PRO-07 | P0 | fully specify synthetic generator, noise, mismatch, resources, replicates and metrics | make P0-G7 executable | inverse crime and arbitrary budget weights | positive control recovery plus declared mismatch checks |
| PRO-08 | P0 | enumerate P0-G4 factorial and expected run count | prevent selective cells or reruns | combinatorial runtime | archive row count equals frozen matrix |
| SCI-01 | P0 | derive or certify the large-`κ` limit across the declared condition set | support generic H1 wording | relying on one centre condition | proof plus representative independent numerical checks |
| SCI-02 | P0 | formalise exact MAPE proposition with positivity/tie/units handling | create defensible analytical result | silent median tie resolution | exhaustive scalar-minimisation regression tests |
| SCI-03 | P1 | propagate map uncertainty/extrapolation sensitivity in H3 | assess whether coarse/fine result depends on map error | double-counting adaptation data | separate input-uncertainty sensitivity artefact |
| SCI-04 | P0 | make H4 conditional on P0-G8 and separate physical validation from localisation | prevent premise from being assumed | weak wording after a finite profile result | branch-specific hypothesis text generated from gate outcome |
| TAX-01 | P0 | split evidence basis, validation provenance, result behaviour, assurance and claim status | represent claims without forced category loss | vocabulary proliferation | schema examples cover cross-fitted heterogeneous result |
| LED-01 | P0 | split falsifier, reproduction failure, scope limiter and confirmatory test | preserve exact claim semantics | overly long ledger records | reviewer can trace what each negative result changes |
| LED-02 | P0 | bind every quantitative claim to path, JSON pointer and hashes | prevent number drift | regenerated archives reorder content | semantic hash or canonical JSON |
| SEQ-01 | P0 | add R0a before freeze and R0b before drafting | find missing premises before execution | duplicate review effort | closure records distinguish initial/final audits |
| NOV-01 | P0 | create indexed-search protocol and external handoff with owner | unblock P0-G10 | inaccessible subscriptions and incomplete exports | search log, deduped corpus and closest-work matrix |
| DOC-01 | P0 | replace “next failure mode…” and “four artefacts” assertions | stop assurance claims outrunning evidence | tone becoming overly defensive | wording matches implemented scope exactly |

---

## 11. Proposed replacement language

## 11.1 Opening authority statement

Replace the current self-contained/four-artefact sentence with:

> **This document is the human-readable member of a controlled normative bundle. `PAPER_A_PLAN_MANIFEST_V1` enumerates the authoritative plan, protocol, initial claim ledger, scope matrix, reconciliation, gate definitions and subsequently generated gate artefacts. Operative authority attaches only to the frozen content commit and recorded file hashes.**

## 11.2 Assurance statement

Replace “the next failure mode has to be one nobody has thought of” with:

> **The replacement control is designed and adversarially tested against the enumerated failure classes. It reduces recurrence of those failures; it does not establish that unanticipated control defects are impossible.**

## 11.3 H1 refinement

> **Within the declared model and declared `κ` domain, each positive matched whole-cup response vector is tested for convergence to a finite large-`κ` limit. The inventory level is profiled exactly under MAPE. For each operational threshold, verified intervals for `J_min`, `J_inf` and the threshold are compared: non-overlap below supports an eventually included upper tail; non-overlap above supports eventual exclusion; overlap is boundary-indeterminate. This is an operational profile classification, not a confidence statement or physical validation.**

## 11.4 H4 refinement

> **If P0-G8 establishes weak or one-sided practical localisation under the declared operational set, the fitted mass-transfer-rate multiplier cannot be read as uniquely learned from matched whole-cup endpoints. Point-estimation policies are compared using calibration-only rules; propagation layers are reported separately. Regardless of profile width, physical interpretation and transferability of the multiplier remain unvalidated.**

## 11.5 P0-G6 criterion placeholder to be completed before freeze

> **RSI is defined as [exact formula] using [exact fixed weights]. The primary association metric is [named statistic] between RSI and [exact inverse-width definition], evaluated over [enumerated designs] at [enumerated `κ` locations]. Censored/disconnected profiles are handled by [exact rule]. Admission requires [minimum statistic/evaluable pairs] in at least 5 of 6 groups at both declared regimes, with the predeclared positive and median-switch negative controls behaving as specified.**

The bracketed content must be filled before P0-G0 passes; it should not remain a future choice.

---

## 12. Adversarial integrity tests that should be added

1. **Missing parser:** remove PyYAML from the minimum lane; the suite must fail, not skip—or use JSON and remove the dependency.
2. **Unclassified archive:** add a new `PAPER_A_NEW_RESULT.json`; classification test must fail.
3. **JSON assertion:** inject `"verdict": "PHYSICAL"`; semantic scanner must fail.
4. **Python output label:** inject `label = "RATE RECALIBRATION ALONE"`; scanner must fail.
5. **Docstring assertion:** inject “the cup cannot see the kinetics”; scanner must fail or require an explicit scoped exemption.
6. **Historical quotation:** include a quoted withdrawn phrase with an explicit exemption; scanner should pass and record the exemption.
7. **Future gate output:** create a listed deliverable but omit classification; fail.
8. **Changed passed artefact:** mutate a hash-bound output; fail.
9. **Placeholder deliverable:** provide `{}` for a passed gate; schema validation fails.
10. **Initial baseline overwrite:** alter the initial ledger after P0-G0; fail.
11. **Invalid content commit:** set a malformed/nonexistent `operative_content_commit`; fail.
12. **Stale protocol:** place a banned current assertion in the protocol; fail.
13. **Stale design verdict:** mark RSI admitted while P0-G6 is open; cross-status consistency fails.
14. **Plan/manifest status conflict:** say a gate is done in prose while manifest says open; fail or prohibit duplicated prose status.
15. **Producer/archive mismatch:** change an archive label without changing the producer; reproduction/binding test fails.

---

## 13. Recommended manuscript framing and title

The primary working title remains strong:

> **Separating Prediction from Mass-Transfer-Rate Identification in Whole-Cup Espresso Modeling**

Retain it provisionally, subject to P0-G10. The current subtitle should be conditional:

### If P0-G9 retains a defensible cross-fitted hydraulic result

> **Large Mass-Transfer-Coefficient Limits, Sensitivity Geometry, and Grind-Specific Flow Inputs**

### If H3 remains retrospective or collapses under cross-fitting

> **Large-Coefficient Limits, Exact MAPE Profiling, and Observation-Operator Design**

The conservative paper should lead with:

1. the exact MAPE profile;
2. the large-`κ` response and objective limits;
3. the distinction between prediction and multiplier localisation; and
4. the observation-operator recovery study.

H3 should remain a secondary applied case study until P0-G9 determines its evidential level.

---

## 14. Acceptance checklist for V2.2.1

V2.2.1 may be declared operative only when all of the following are true:

- [ ] no Paper 1 integrity test can skip because an authoritative parser is missing;
- [ ] every candidate claim surface is active, historical/audit or explicitly non-claim;
- [ ] the current protocol is classified and scanned;
- [ ] JSON and Python scalar assertions are inspected semantically;
- [ ] adversarial tests demonstrate the scanner catches the identified regressions;
- [ ] every gate has a closure record, pass criteria, schema and immutable evidence binding;
- [ ] P0-G2 has a concrete disaggregation-audit deliverable;
- [ ] initial and final ledger/scope artefacts are separate and hash-bound;
- [ ] an implementable freeze-commit/activation-commit procedure is defined and tested;
- [ ] plan status statements and manifest status agree;
- [ ] the saturation producer, rate-domain archive and design-separability archive are reconciled;
- [ ] every claimed `--check` mode actually verifies reproducibility or is renamed accurately;
- [ ] the P0-G8 domain, threshold formulas, error intervals, topology and shoulder rule are frozen;
- [ ] the RSI formula, metric, designs, censoring, controls and admission threshold are frozen;
- [ ] the target-map families, exclusion unit, adaptation counts and placement rules are frozen;
- [ ] the regulariser, tuning branch, evaluation metrics and propagation construction are frozen;
- [ ] the synthetic-study generator, noise, mismatch, resources, replicates and success metrics are frozen;
- [ ] the P0-G4 factorial is enumerated;
- [ ] the evidence taxonomy and ledger semantics can represent cross-fitted heterogeneous evidence;
- [ ] R0a is complete;
- [ ] the P0-G10 external handoff has a protocol, owner and completion artefact; and
- [ ] the normative bundle is frozen and activated through immutable content hashes.

---

## 15. Final disposition

V2.2 has solved the major scientific problems identified in V2 and V2.1. The paper now has a coherent and potentially novel analytical centre: exact production-MAPE profiling, large-coefficient response limits, practical multiplier localisation, and observation-operator design, with target-side hydraulic information as a carefully bounded applied case.

The plan should **not** be rejected or conceptually rewritten. It should also **not yet be declared operative**. The current integrity layer still reproduces the same class of failure that V2.2 explicitly seeks to eliminate: an assurance statement that is broader than the implemented control. In parallel, the protocol uses the language of a freeze while leaving several result-sensitive choices unfrozen.

The recommended next step is therefore a **narrow V2.2.1 operative-control patch**, not a fourth scientific pivot. Once the critical control, protocol and reconciliation actions in this review are complete, the programme can proceed to P0-G8 and the remaining scientific gates with a substantially stronger evidential foundation.

---

## Source inventory reviewed

- [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md)
- [`PAPER_A_PLAN_MANIFEST_V1.yaml`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.yaml)
- [`test_paper1_plan_integrity.py`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/tests/test_paper1_plan_integrity.py)
- [`PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md)
- [`PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json)
- [`PAPER_A_MODEL_SCOPE_MATRIX.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_MODEL_SCOPE_MATRIX.md)
- [`PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md)
- [`paper_a_saturation_verification.py`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/tools/paper_a_saturation_verification.py)
- [`PAPER_A_SATURATION_VERIFICATION.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_SATURATION_VERIFICATION.json)
- [`PAPER_A_RATE_DOMAIN_CHECK.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_RATE_DOMAIN_CHECK.json)
- [`PAPER_A_DESIGN_SEPARABILITY.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_DESIGN_SEPARABILITY.json)
- [`paper_a_information_parity.py`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/tools/paper_a_information_parity.py)
- [`PAPER_A_INFORMATION_PARITY.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_INFORMATION_PARITY.json)
- [`PAPER_A_ABLATION_REFIT_STABILITY.json`](https://github.com/trbrewer/puckworks/blob/dac4e3ca2070a773606875b1e2755e05f8169cf9/docs/paper1_resource/PAPER_A_ABLATION_REFIT_STABILITY.json)
