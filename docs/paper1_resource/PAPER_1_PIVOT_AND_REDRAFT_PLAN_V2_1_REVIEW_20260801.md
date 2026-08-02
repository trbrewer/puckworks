# Review of `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md`

**Review date:** 1 August 2026 (America/Chicago)  
**Document reviewed:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md)  
**Immutable reviewed snapshot:** [`66766801639b6338ada2e194e5a2be1d0bd77c59`](https://github.com/trbrewer/puckworks/commit/66766801639b6338ada2e194e5a2be1d0bd77c59)  
**Prior review:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_REVIEW_20260801.md`](https://github.com/trbrewer/puckworks/blob/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_REVIEW_20260801.md)  
**Recommended disposition:** **CONDITIONALLY APPROVE THE SCIENTIFIC DIRECTION, BUT REQUIRE A FOCUSED V2.2 EXECUTION-INTEGRITY PATCH BEFORE V2.1 IS DECLARED OPERATIVE, BEFORE P0-G0 IS FROZEN, AND BEFORE ANY NEW P0-G4–P0-G9 SCIENTIFIC RUNS.**

---

## 1. Executive assessment

V2.1 is a substantial improvement over V2 and is the first version of the pivot plan whose **central scientific direction is essentially right**. It accepts the prior review's load-bearing corrections rather than merely softening their wording. In particular, it:

- makes H1 conditional on the asymptotic profiled objective rather than inferring localisation from a finite response limit;
- separates the exact weighted-L2 sensitivity geometry from the production MAPE objective;
- names the fitted quantity correctly as a **mass-transfer-rate multiplier**;
- recasts H3 as a **target-grind flow-map substitution** rather than hydraulic attribution;
- preserves the coarse/fine reversal instead of hiding it behind pooled summaries;
- treats fixed, free, regularised and constrained approaches as policy candidates rather than announcing a universal freeze rule;
- introduces a protocol-freeze gate to control further analytical flexibility;
- moves novelty assessment to the beginning of the programme;
- replaces the one-dimensional evidence ladder with a type × robustness framework; and
- adds an observation-operator study that could provide a genuine conceptual bridge between prediction and parameter localisation.

Those are important corrections. The paper's best prospective contribution is now clear:

> **Matched whole-cup predictive performance and localisation of a model-specific mass-transfer-rate multiplier are distinct achievements; temporal chemical observations and target-side hydraulic information may support those achievements through different information channels.**

The remaining defects are narrower than those in V2, but several are still **execution-blocking**. The most important are not disagreements about emphasis. They are internal contradictions, incomplete decision rules, and active repository artefacts that still assert claims V2.1 has withdrawn.

### 1.1 Why another focused patch is justified

Before new analyses begin, V2.1 should be patched for seven reasons:

1. **The “from-the-start” controls are not in Step 0.** P0-G1 requires a machine-readable claim ledger from the start, but the immediate sequence postpones P0-G1/P0-G3 reconciliation until after all analyses.
2. **The mechanical integrity test does not implement the checks V2.1 says it implements.** It is hard-coded to V2.1, skips if the operative file is missing, omits several advertised terminology checks, does not test gate definitions “and vice versa,” and does not scan active cross-file claims.
3. **Current active artefacts contradict V2.1.** The saturation archive still returns `"verdict": "PHYSICAL"`; the claim ledger and separability module still use the withdrawn “all local rate information” formulation; and the information-parity producer still labels M0−M2 as “rate recalibration alone.”
4. **H1 needs a complete tail-classification rule.** `J_inf` below, above, or numerically equal to the tolerance boundary lead to different conclusions; connectedness, global profile topology, and near-zero `J_min` also need explicit treatment.
5. **The synthetic observation-operator experiment is underspecified and overinterpreted.** Equal observation counts are not equal resource budgets; a same-model synthetic study risks an inverse crime; and failure of the proposed time-resolved design would not by itself prove the observation-compression explanation “wrong.”
6. **H3 cannot become genuinely prospective merely by re-slicing the existing campaign.** A cross-fitted adaptation curve can emulate a prospective protocol, but a genuinely prospective claim requires data not used to generate the hypothesis or tune the protocol.
7. **H4 currently compares unlike objects.** Fixed/free/regularised approaches are point-estimation policies; profile propagation is an uncertainty or sensitivity-reporting layer. These should be separated rather than ranked in one undifferentiated policy table.

### 1.2 Bottom-line recommendation

Do **not** reverse the pivot. Do **not** return to the original −0.394 percentage-point thesis. The V2.1 scientific direction is stronger and potentially publishable.

However, do not yet label V2.1 operative. Produce a concise V2.2 that:

- is self-contained or uses immutable normative references;
- creates initial claim/scope controls before P0-G0 and before scientific runs;
- replaces the current prose-scanning test with a fail-closed manifest-driven control;
- reconciles active repository claims with the new scope;
- makes P0-G5–P0-G9 pass criteria enforceable rather than discretionary; and
- rewrites the synthetic and adaptation studies so their evidential status is exact.

---

## 2. What V2.1 gets right and should retain

## 2.1 The scientific correction to H1 is real

V2.1 correctly withdraws the implication that a finite model-response limit automatically creates weak or one-sided practical localisation. It now states that localisation depends on the profiled objective, the data, residuals, nuisance profiling, objective and tolerance. This is the correct conceptual separation.

Retain:

- the explicit distinction between a **response limit** and an **objective-profile classification**;
- the statement that real espresso's occupancy of the large-coefficient regime is untested;
- the requirement to compute both `J_inf/J_min` and `J_inf − J_min`; and
- threshold sensitivity rather than a single 10% convention.

## 2.2 H2 now separates exact algebra from production inference

V2.1 correctly identifies the determinant and Schur-complement results as an exact local weighted-L2 geometry, not the Hessian of MAPE. That correction is essential. It also makes direct comparison with actual MAPE profiles a pass condition and requires a failure case.

Retain the algebraic result, but strengthen the production-objective analysis as recommended in §3.6 below.

## 2.3 H3 is now honest about the information protocol

The plan correctly states that the current target map is built from target-grind campaign information and distinguishes:

1. zero-target-data prediction;
2. hydraulic adaptation without target chemistry; and
3. retrospective reconstruction.

It also preserves the grind-specific result:

- **coarse M1−M2:** median **+1.234 pp**, positive in **9/9** folds;
- **fine M1−M2:** median **−0.037 pp**, range **−0.671 to +0.086**, negative in **7/9** folds.

That is the right empirical summary. The pooled result should remain secondary.

## 2.4 H4 is no longer a universal recommendation

V2.1 correctly says that a weakly localised multiplier should not be interpreted as a uniquely learned kinetic quantity and that `κ = 1` is an inherited normalisation, not an externally validated physical value. Retain this boundary.

## 2.5 P0-G0 is necessary

The plan openly acknowledges that the follow-up analyses were designed after seeing the current results. Freezing the candidate analyses, thresholds, map variants, policies, aggregation rules and withdrawal rules before additional runs is the right response.

The freeze does **not** convert reanalysis of the same campaign into independent confirmation; this distinction should be added explicitly, but the gate itself is sound.

## 2.6 The early novelty gate and non-directional closure rules are strong

P0-G10 is now started early and can close by narrowing, splitting or terminating claims rather than requiring a favourable novelty finding. That is a good governance rule. The same is true of the other gates: closure should mean the planned test was completed and the claim followed the evidence, not that the preferred hypothesis survived.

---

## 3. Blocking findings and required corrections

## 3.1 The operative plan is not self-contained

### Finding

V2.1 says that §9.1–§9.6 are “carried from v2 unchanged,” even though V2 is expressly superseded and non-operative. The immediate sequence also says drafting will follow “the architecture in the review's §12,” and it invokes `R0–R5` without defining those rounds in V2.1.

This creates three governance problems:

1. A reader cannot execute the operative plan from the operative file alone.
2. The normative content is split across an operative plan, a superseded plan, and a review document.
3. File-name references are mutable unless the operative version is explicitly bound to an immutable repository snapshot.

### Recommendation

Before operative status, choose one of two approaches:

**Preferred:** reproduce all normative requirements in V2.2, including:

- premise-type assurance rules;
- termination rules;
- R0–R5 definitions;
- the claim–premise–test matrix;
- estimand definitions; and
- manuscript architecture.

**Acceptable alternative:** add a normative-reference table that pins every incorporated section to an immutable commit and states precedence in the event of conflict.

### Required action

Create `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md` with:

- `Status: operative only at commit <SHA>`;
- a complete glossary;
- all gate definitions and dependencies;
- all round definitions;
- all estimand definitions; and
- no dependency on a superseded file for operative meaning.

### Check

A new reader should be able to determine every required run, artefact, gate, dependency, decision branch and drafting restriction from V2.2 plus its immutable machine-readable manifest, without opening V1, V2 or either review.

---

## 3.2 P0-G1 says “from the start,” but the execution sequence postpones it

### Finding

P0-G1 requires a machine-readable claim ledger to exist **from the start** and be regenerated at the end. P0-G3 likewise requires a standalone model-scope matrix. Yet:

- Step 0 is defined as “this document plus P0-G0”; and
- the immediate sequence places P0-G1, P0-G2 and P0-G3 in final reconciliation after P0-G4–P0-G9.

The current repository does contain an older Markdown claim ledger, but it is neither the required machine-readable V2 ledger nor aligned with V2.1. It still includes, among other things:

- a supported claim that prediction “coexists with weak localisation” before `J_inf` is known;
- the old pooled-mechanistic wording;
- an unqualified statement that “all local rate information” is the weighted variance; and
- open questions that the newer ablation work has already addressed.

### Why this matters

A final ledger can reconcile completed work, but it cannot protect the programme from claim drift **during** the analyses. Initial claims, scopes, estimands and withdrawal rules must be recorded before new numerical outputs proliferate.

### Recommendation

Split P0-G1 and P0-G3 into initial and final phases:

- **P0-G1a — initial claim ledger:** before P0-G0 is frozen and before scientific runs;
- **P0-G1b — final claim reconciliation:** after all analytical outputs are frozen;
- **P0-G3a — initial model/evidence scope matrix:** before scientific runs;
- **P0-G3b — final cross-file scope reconciliation:** before drafting.

### Required deliverables before new runs

1. `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json`
2. `PAPER_A_MODEL_SCOPE_MATRIX.md`
3. `PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md`
4. `PAPER_A_PLAN_MANIFEST_V1.yaml` or `.json`

### Check

Every planned headline and every current active headline must have:

- claim ID;
- exact provisional wording;
- evidence type;
- robustness status;
- estimand tag;
- unit of analysis;
- aggregation rule;
- data and map protocol;
- source artefact and hash;
- known alternative explanations;
- external-validity boundary;
- falsifying or withdrawal result; and
- status: `supported`, `provisional`, `open`, `withdrawn`, `superseded`, or `historical-only`.

---

## 3.3 The integrity test creates more assurance than it actually provides

### Finding

Section 9.7 says the test scans the operative plan for:

- deprecated terminology including unqualified “saturation” and physical verification;
- gate IDs referenced but not defined **and vice versa**;
- internal contradictions; and
- count mismatches.

The implementation in `tests/test_paper1_plan_integrity.py` is materially narrower.

| advertised control | actual implementation | consequence |
|---|---|---|
| reject unqualified “saturation” and “physical verification” | neither appears in `DEPRECATED` | the plan itself says “Response saturation is a model property” and the test passes |
| reject gate IDs referenced but not defined, and vice versa | collects every `P0-G*` occurrence, including definitions, and checks for a bold occurrence | no genuine orphan-definition or orphan-reference test |
| validate stated counts against tables | only bans the literal phrase “the four findings below” | “Three ambiguities” above a five-row terminology table passes |
| require grind reversal wherever pooled result appears | only checks that `+1.234` and `−0.037` occur somewhere in the file | no contextual co-location check |
| scan the operative plan | operative filename is hard-coded to V2.1 | a future V2.2 can be ignored unless the test is manually edited |
| fail when operative plan is absent | calls `pytest.skip` | missing governance artefact can produce a non-failing test run |
| cross-file claim consistency | no active-artifact scan | stale `PHYSICAL`, “attribution,” and “all local information” claims remain undetected |
| internal logical consistency | a few literal substring/regex checks | semantic contradictions such as equal-budget vs equal-count are not tested |

### Additional concrete inconsistency

The terminology section says “Three ambiguities” but defines five terminology rules. This is precisely the class of defect §9.7 claims to catch, and the current test does not catch it.

### Recommendation

Replace file-specific prose tests with a **manifest-driven, fail-closed control**.

Suggested manifest fields:

```yaml
schema_version: 1
operative_plan: docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md
operative_commit: <sha>
gates:
  P0-G0:
    status: open
    dependencies: []
    deliverables: [...]
  P0-G1a:
    status: open
    dependencies: [P0-G0]
    deliverables: [...]
normative_references: [...]
active_claim_surfaces: [...]
historical_exclusions: [...]
banned_assertions: [...]
required_estimand_tags: [...]
```

### Required test behaviour

- The manifest and operative plan must exist; absence is a **failure**, not a skip.
- The operative path must be read from the manifest, not hard-coded.
- Gate definition and reference sets must be parsed separately and compared both ways.
- Every gate must have a unique status, dependencies and deliverables.
- Dependencies must form an acyclic graph.
- Every required artefact must exist at closure.
- Active claim surfaces must be scanned repository-wide; historical files must be excluded only through explicit manifest classification.
- Numeric headline records should be generated from the machine-readable claim ledger, not validated only by prose regexes.
- The test should verify that initial ledgers predate scientific result artefacts by commit ancestry or frozen hashes.

### Disposition

Treat the current test as a useful regression smoke test, **not** as proof that the plan is internally self-enforcing.

---

## 3.4 Active repository artefacts still assert withdrawn claims

### Finding

V2.1's prose is more careful than several current active artefacts.

| active artefact | current statement | conflict with V2.1 |
|---|---|---|
| `PAPER_A_SATURATION_VERIFICATION.json` | question asks whether saturation is “physical”; `verdict` is `PHYSICAL` | V2.1 says the check is model-structural and physical generalisation is untested |
| `PAPER_A_CLAIM_LEDGER.md` | S4 says held-out accuracy coexists with weak localisation | final localisation classification requires `J_inf` and threshold sensitivity |
| `PAPER_A_CLAIM_LEDGER.md` | S5 uses an old pooled-mechanistic formulation | V2.1 requires the revised grind-specific ablation wording |
| `PAPER_A_CLAIM_LEDGER.md` | S10 says “all local rate information” is the weighted variance | V2.1 limits this to a declared local weighted-L2 surrogate geometry |
| `puckworks/paper_a/separability.py` | module docstring repeats “all local rate information” | same scope defect as S10 |
| `tools/paper_a_information_parity.py` and its JSON | labels M0−M2 “RATE RECALIBRATION ALONE” | V2.1 correctly calls it an estimation-policy contrast with level re-profiled |
| `tools/paper_a_information_parity.py` | module heading says “mechanistic attribution” | V2.1 withdraws attribution language |
| `PAPER_A_ABLATION_REFIT_STABILITY.json` | question says “freezing the rate transfers better” | pooled sign is not stable and “transfer” is deprecated for evaluation |

Historical ROADMAP/SPRINTS entries also preserve the prior `PHYSICAL` language. Historical records should not be silently rewritten, but they need explicit supersession markers so search results do not appear to represent the current scientific position.

### Recommendation

Perform a **current-claim reconciliation before P0-G0**, not only at the end.

### Required method

1. Inventory every active Paper 1 claim surface: plan, manuscript, claim ledgers, JSON archives, producer docstrings, model cards, ROADMAP, SPRINTS, README/landing pages and tests.
2. Classify each surface as:
   - current normative;
   - current evidential;
   - generated output;
   - historical audit only; or
   - superseded.
3. Preserve numerical evidence and Git history, but revise or supersede interpretive fields.
4. For generated JSON, prefer a schema increment with explicit fields such as:

```json
{
  "evidence_type": "numerical-model-structural",
  "temporal_artifact_status": "not_BDF_artifact",
  "physical_validity": "untested",
  "current_interpretation": "finite response limit within the declared semi-discrete model"
}
```

5. Add `superseded_by`, `scope_version`, and `claim_ids` where appropriate.

### Check

A repository-wide search of current active surfaces must find no unqualified assertion that:

- the large-coefficient behaviour is physically verified;
- M0−M2 is a pure physical rate intervention;
- the weighted-variance identity is the production MAPE curvature or all local information without qualification;
- the target-map result establishes causal hydraulic attribution; or
- the current campaign proves a universally preferable freeze policy.

---

## 3.5 H1 needs a complete asymptotic classification rule

### Finding

V2.1 correctly gives a necessary condition:

> the upper near-optimal set can extend indefinitely only if `J_inf ≤ (1+δ)J_min`.

However, the plan does not state the complete decision rule. Let

\[
T_\delta=(1+\delta)J_{\min}
\]

or, for an absolute convention,

\[
T_\Delta=J_{\min}+\Delta.
\]

Given a rigorously established limit `J(k) → J_inf`:

- if `J_inf < T − ε`, an accepted upper tail is eventually guaranteed;
- if `J_inf > T + ε`, an accepted upper tail is eventually excluded;
- if `|J_inf − T| ≤ ε`, the limit alone is insufficient and the approach direction, numerical uncertainty and profile topology must be examined.

Equality is not a trivial accepted case. A profile can approach the boundary from above without any finite upper tail entering the set.

### Additional issues to predeclare

1. **Near-zero `J_min`:** `J_inf/J_min` is unstable or undefined when `J_min` is zero or very small. This is particularly relevant to noiseless synthetic positive controls.
2. **Globality:** a finite grid minimum is not necessarily the global minimum. Use exact profiling in `I` and a validated global one-dimensional search/profile in `κ`.
3. **Topology:** report all connected components of the operational near-optimal set, not just its first and last grid points.
4. **Censoring:** right-censoring at `κ=500` remains a finite-domain observation until the asymptotic branch is classified.
5. **Objective dependence:** MAPE, relative-L2, SSE and Huber are sensitivity objectives, not interchangeable inferential likelihoods.
6. **Numerical boundary band:** define `ε` from independently verified asymptotic and profiling error, not an arbitrary display precision.

### High-value opportunity: exploit the exact MAPE profile

The repository already implements the exact level minimiser for positive predictions and observations. For

\[
\hat y_i=I f_i(\kappa),\qquad y_i>0,\quad f_i(\kappa)>0,
\]

production MAPE is

\[
J(I,\kappa)=\frac{1}{n}\sum_i\frac{|I f_i(\kappa)-y_i|}{y_i}
=\frac{1}{n}\sum_i w_i(\kappa)|I-r_i(\kappa)|,
\]

where

\[
w_i(\kappa)=\frac{f_i(\kappa)}{y_i},\qquad
r_i(\kappa)=\frac{y_i}{f_i(\kappa)}.
\]

Any weighted median of `r_i(κ)` with weights `w_i(κ)` minimises the level exactly. This should be elevated from an implementation detail to a formal proposition because it:

- removes optimiser uncertainty from the production profile;
- provides an exact construction of `J(κ)` and `J_inf` once `f_i(∞)` is available;
- identifies median-switch kinks that can make the weighted-L2 surrogate disagree with MAPE; and
- creates a clean bridge between H1 and H2.

### Required H1 pass output

For every group and every frozen objective/tolerance:

- `κ_hat`, `I_hat`, `J_min`;
- `f_inf`, `I_inf`, `J_inf`;
- relative and absolute gaps;
- asymptotic numerical error bound;
- response-elasticity shoulder;
- all connected near-optimal components;
- lower/upper censoring status;
- one of `tail_included`, `tail_excluded`, `boundary_indeterminate`;
- objective/tolerance invariance classification; and
- a precise claim branch.

---

## 3.6 H2 should use the exact production-MAPE structure, not only validate a surrogate

### Finding

V2.1 correctly says the Gram/Schur identity is not MAPE curvature, but its gate remains too binary: RSI either “tracks” the MAPE profiles or is downgraded. “Tracks” has no frozen metric or threshold, and a single designed failure case proves only that the diagnostic *can* fail—not that it is useful where it is retained.

The existing `agreement_with_profiles` helper treats any negative Spearman correlation as “consistent with expectation,” irrespective of magnitude, sample count, dependence or uncertainty. That is too weak for a gate that may support a design recommendation.

### Recommendation

Make H2 a three-part result:

1. **Exact weighted-L2 proposition:** determinant, Schur complement and normalisations.
2. **Exact production-MAPE profiling proposition:** weighted-median profiling and its nonsmooth/k-dependent-weight structure.
3. **Empirical/synthetic diagnostic test:** whether RSI provides useful ordinal design screening for actual MAPE profiles under frozen conditions.

### Required validation design

Predeclare:

- candidate designs;
- groups and `κ` locations;
- weight conventions;
- profile-width definition, including censored profiles;
- primary concordance metric;
- minimum evidential criterion for retaining RSI as a practical screen;
- downgrade wording if that criterion is not met; and
- positive and negative controls.

Use at least:

- pairwise ranking concordance between RSI and inverse MAPE-profile width;
- stratified results by group and `κ` rather than one pooled correlation;
- sensitivity to weights and profile thresholds;
- a positive control where the surrogate should work;
- a negative control driven by MAPE median switching or another declared mechanism; and
- full scatterplots/data, not only a sign flag.

### Interpretation rule

- If the predeclared criterion is met robustly, retain RSI as a **model-based ordinal screen**.
- If association is weak or unstable, retain the algebra and exact MAPE profiling but remove practical design-ranking claims.
- If association changes by regime, retain a regime-qualified rule rather than one global conclusion.

---

## 3.7 H3's “prospective” branch needs stricter definitions and mandatory cross-fitting

### Finding

V2.1 says an adaptation curve using zero, one, two, several and full target measurements “would make H3 prospective instead of retrospective.” That is too strong if all points come from the same campaign used to generate the hypothesis and choose the adaptation strategy.

At least three evidential levels should be distinguished:

1. **Retrospective campaign-conditioned map:** current result; may use all target hydraulic support.
2. **Cross-fitted prospective-protocol emulation:** the scored condition and any information derived from it are excluded from map construction; number and placement of adaptation observations are frozen or nested.
3. **Genuinely prospective external test:** protocol frozen before collecting a new target campaign, grind, coffee, recipe or machine dataset.

Only the third is genuinely prospective in the ordinary empirical sense.

### Existing archive suggests a specific diagnostic hypothesis

The current hydraulic-extrapolation archive reports that fine targets occupy substantially more out-of-support residence-time space than coarse targets:

- coarse: about **36.4%** outside the calibration range and maximum gap about **0.28 calibration spans**;
- fine: about **72.7%** outside and maximum gap about **1.551 calibration spans**.

This does not explain the fine reversal by itself, but it gives P0-G9 a concrete predeclared hypothesis: the fine sign reversal may be associated with map extrapolation, map error, or compensating model error.

### Required minimum for P0-G9

The phrase “where feasible” is not enforceable. Replace it with a branch rule:

- **Mandatory:** current map, common O-grind map, and scored-condition-excluded/cross-fitted map wherever raw support permits.
- **Mandatory:** explicit declaration of any variant that cannot be constructed and why.
- **Mandatory consequence:** if a defensible cross-fitted map cannot be constructed, H3 remains retrospective and cannot be promoted to a prospective contribution or title claim.
- **Optional but valuable:** limited-adaptation and physics-only variants.
- **Required for a genuinely prospective claim:** new data collected after protocol freeze.

### Required map protocol

For every scored target condition record:

- which hydraulic observations fitted the map;
- whether the scored condition, pressure, temperature, grind or shot contributed;
- timing of availability: pre-shot, contemporaneous, or post-shot;
- measurement versus fitted/derived status;
- uncertainty and covariance;
- extrapolation distance/leverage;
- map-form alternatives;
- map-selection rule; and
- whether target chemistry or target chemical score influenced any choice.

### Adaptation-curve design

- Freeze candidate counts and placements before scoring.
- If placement is selected, nest selection entirely inside the adaptation/calibration support.
- Report grind-specific results and map error, not only chemical MAPE.
- Propagate map uncertainty through chemical predictions.
- Keep a no-target-data baseline.
- Label a same-campaign cross-fitted result as **prospective-protocol emulation**, not external prospective validation.

---

## 3.8 H4 mixes estimation policies with uncertainty propagation

### Finding

V2.1 lists fixed, regularised, externally constrained, free-fit and profile-propagated treatments as competing estimation policies. The first four can produce point estimators. Profile propagation is different: it describes how uncertainty or sensitivity across `κ` is carried into predictions.

Ranking them together risks comparing:

- a point prediction scored by MAPE; and
- a prediction envelope with no calibrated probability or coverage interpretation.

The phrase “target-independent protocol” is also ambiguous because H3 explicitly permits target hydraulic adaptation. What must be independent is **policy and hyperparameter selection from evaluation-target chemical outcomes and scores**, not necessarily from declared target hydraulic covariates.

### Recommendation: use a two-axis design

**Axis A — point-estimation rule**

- free-wide MAPE fit;
- fixed predeclared anchors;
- regularised fit toward a declared anchor;
- externally constrained fit, only if a genuinely independent constraint exists;
- bounded/constrained fit with bounds justified independently of target scores.

**Axis B — uncertainty/sensitivity propagation**

- point only;
- operational-profile prediction envelope;
- objective-family sensitivity envelope;
- synthetic calibrated interval, only where a probabilistic data-generating model supports one.

### Required tuning rule

“Preferably nested” is too weak for a blocking gate. Require one of:

1. fully nested tuning within calibration support; or
2. a frozen no-tuning grid of penalties/anchors with every candidate reported and no post hoc winner selected.

With only nine calibration conditions, nested selection may be unstable. That instability is itself a result and must be reported; it is not a reason to tune on target scores.

### Required outputs

For point policies:

- calibration objective;
- coarse, fine and pooled target scores;
- fold and group decompositions;
- selected anchor/penalty and selection support;
- policy complexity;
- optimisation failures and boundary hits.

For propagation layers:

- envelope width;
- sensitivity to tolerance/objective;
- empirical containment reported descriptively only;
- no confidence or coverage language unless calibrated in a declared probabilistic synthetic setting.

### Decision rule

H4 may conclude:

- no clear policy winner;
- grind-specific winners;
- a robustly preferred policy within this campaign; or
- insufficient support for a policy recommendation.

It must not claim a generally optimal treatment from the present target campaign alone.

---

## 3.9 The synthetic observation-operator study needs a proper design contract

### Finding

The observation-operator comparison is the most valuable new proposal in V2.1, but the current language overstates what it can establish.

#### Equal counts are not equal budgets

P0-G7 says equal-budget, while §8.1 says equalised observation counts. These are not equivalent. One fractionated shot may yield several correlated fractions; several whole-cup endpoints may require separate shots; assays, aliquots, brewing time and sample preparation differ.

#### Same-model generation risks an inverse crime

If the same equations, parameterisation, flow map and noise-free observation operator generate and fit the data, recovery may be artificially easy. V2.1 mentions mismatch but does not define it.

#### The failure rule is too categorical

If neither tested operator localises `κ`, it does not automatically follow that the observation-compression explanation is “wrong.” Other possibilities include:

- the time-resolved design is itself inadequate;
- noise is too large;
- the common-multiplier parameterisation is structurally compensating;
- the chosen conditions do not excite the responsive regime;
- the fitting code or profile metric is defective; or
- mismatch dominates the information gain.

#### A synthetic result is not automatically “general”

It can support a general **model-based design principle**, but it does not turn a one-model, one-campaign paper into broad empirical validation.

### Required staged design

#### Stage 1 — noiseless positive controls

- Verify code recovery under a rich design known to have full local rank and a finite global profile.
- Include a dense/full-state or deliberately informative upper-bound design.
- Demonstrate that the estimation pipeline can recover `I` and `κ` when the design contains the information.

#### Stage 2 — same-model practical recovery

Compare:

- one whole-cup endpoint per condition;
- multiple collected-mass endpoints from matched independent shots;
- fractionated/time-resolved observations;
- optionally a combined endpoint + fraction design.

Use multiple true `κ` values:

- below the response shoulder;
- near the shoulder;
- in the large-coefficient regime.

Also vary `I`, group/solute and condition design.

#### Stage 3 — correlated and heteroscedastic noise

Model separately:

- shot-to-shot variability;
- within-shot correlated fraction errors;
- assay error;
- flow/endpoint measurement error; and
- map uncertainty.

Avoid MAPE pathologies at zero or near-zero synthetic observations; predeclare the scoring/loss treatment.

#### Stage 4 — declared model mismatch

At minimum test several plausible misspecifications, such as:

- separate fine/coarse multipliers rather than one common `κ`;
- time-varying flow;
- wrong or uncertain flow map;
- grind-dependent geometry;
- dynamic permeability/fines effects represented by a reduced discrepancy term; and
- solute-specific discrepancy or noise.

#### Stage 5 — resource-equated comparison

Define budget in physical units, for example:

- number of shots;
- number of chemical assays/aliquots;
- total beverage/fraction samples;
- operator time or an explicit cost index.

Report a Pareto frontier rather than forcing one arbitrary scalar budget where appropriate.

### Required metrics

- structural/local rank or singular values;
- global profile topology and width;
- `κ` and `I` bias/error;
- boundary/censoring frequency;
- prediction error;
- interval/envelope width where applicable;
- calibrated coverage only in probabilistic synthetic experiments; and
- failure/optimisation rates.

### Revised interpretation rule

- If time-resolved data improve recovery under adequate positive controls and realistic noise/mismatch, the observation-compression explanation is **supported within the tested model class**.
- If they do not, the explanation is **not supported by the tested design**; branch to inadequate design, deeper structural compensation, or mismatch after examining the controls.
- Either result is scientifically informative, but publication value remains conditional on P0-G10 and robustness. Remove “Either outcome is publishable.”

---

## 3.10 The unifying thesis still contains two unsupported shortcuts

### Finding 1 — “numerically competitive” has no declared comparator or margin

The risk table itself recognises this. Until comparator set and practical margin are frozen, the thesis should report exact scores or use neutral wording.

### Finding 2 — “because target-side flow information sets the endpoint residence time” is too causal

The map certainly determines endpoint residence time in the implemented predictor. But the evidence does not yet show that this is *why* prediction remains stable across grinds, especially because the fine effect is near-zero, heterogeneous and usually opposite.

### Finding 3 — “source-calibrated” conflates two calibration layers

The inherited Pannusch solver parameters are a post-fit reconstruction of Schmieder fractionated kinetics. Paper 1 then fits the multiplier and inventory level on Angeloni optimal-grind conditions before coarse/fine scoring. The plan should state both layers rather than compressing them into “source-calibrated predictions.”

### Recommended central question

> **What information do matched whole-cup chemical endpoints and target-side hydraulic measurements contribute separately to (a) conditional cross-grind prediction and (b) localisation of a model-specific mass-transfer-rate multiplier?**

### Recommended unifying thesis wording

> **Whole-cup predictive performance and localisation of a model-specific mass-transfer-rate multiplier are distinct achievements. In this campaign, predictions fitted on optimal-grind chemical data and conditioned on declared target-grind hydraulic information are evaluated separately from the ability of the same endpoint observation operator to localise the multiplier. The target-flow-map effect is grind-specific, and both its prospective value and any kinetic interpretation depend on the information protocol, objective, model structure and external validation.**

This wording avoids “competitive,” avoids an unproven causal “because,” and states the two calibration/information layers accurately.

---

## 3.11 P0-G0 controls future flexibility but does not erase same-data post-selection

### Finding

The protocol freeze is valuable, but every main hypothesis and candidate analysis was generated after inspecting the campaign. Freezing the next runs makes them **prospectively specified relative to those runs**, not independently confirmatory relative to the underlying data.

### Recommendation

The protocol and manuscript should use exact labels:

- **post-selection frozen reanalysis** for P0-G4–P0-G6/P0-G8/P0-G9 using the same campaign;
- **prospective model-based study** for the synthetic P0-G7 work;
- **cross-fitted prospective-protocol emulation** for held-out map construction within the same campaign; and
- **genuinely prospective empirical test** only for data collected after protocol freeze.

### Required protocol statement

> The protocol was frozen after exploratory inspection of the existing campaign. It limits further analytical flexibility and selective reporting but does not provide independent confirmation of hypotheses generated from the same data.

---

## 3.12 P0-G3's evidence taxonomy is incomplete

### Finding

P0-G3 says every claim will be tagged as algebraic, numerical-model-structural, empirical or physical. V2.1's own evidence grid also uses:

- operational profile result;
- prospective model-based result; and
- unresolved/exploratory status.

The four-class gate therefore cannot represent the plan's own evidence hierarchy.

### Recommendation

Use two separate fields:

**Evidence type**

- algebraic;
- numerical-model-structural;
- empirical-descriptive;
- operational/convention-based;
- inferential;
- prospective-model-based;
- physical/external;
- exploratory/oracle.

**Robustness status**

- established under assumptions;
- verified within numerical scope;
- refit-stable;
- heterogeneous;
- sensitivity-only;
- cross-fitted;
- externally replicated;
- unresolved;
- withdrawn.

No evidence type should be treated as a scalar “higher tier” without considering its boundary.

---

## 4. Hypothesis-by-hypothesis disposition

| item | V2.1 assessment | recommendation |
|---|---|---|
| **H1** | Scientifically corrected and appropriately model-scoped, but asymptotic acceptance needs a three-way boundary rule, exact MAPE profiling, global topology and near-zero handling | **Retain after P0-G8 is strengthened** |
| **H2** | Exact weighted-L2 algebra is sound; connection to MAPE remains unresolved | **Retain; add exact weighted-median MAPE proposition and predeclared validation criterion** |
| **H3** | Current retrospective/campaign-conditioned result is accurately described and correctly grind-disaggregated | **Retain as descriptive; promote only after mandatory cross-fitting, and call genuinely prospective only with new data** |
| **H4** | Correct principle that weak localisation forbids unique kinetic interpretation | **Retain after separating point-estimation policy from uncertainty propagation and making tuning rules mandatory** |
| **Unifying thesis** | Strong information-based direction, but “competitive,” “because,” and “source-calibrated” remain too compressed | **Replace with the wording in §3.10** |
| **Synthetic bridge** | Potentially the paper's most valuable new component | **Retain after positive controls, resource-equated budgets, covariance and mismatch are specified** |
| **Title** | Main title is appropriately restrained | **Retain provisionally; revise subtitle to the exact parameter terminology** |

---

## 5. Gate-by-gate review and recommended pass criteria

| gate | V2.1 status | required V2.2 correction |
|---|---|---|
| **P0-G0** | strong and necessary | add same-data post-selection statement; freeze seeds, environment, exclusions, failure handling, primary/secondary outputs and multiplicity/reporting rules |
| **P0-G1** | internally inconsistent with sequence | split into initial `G1a` and final `G1b`; require machine-readable ledger before runs |
| **P0-G2** | sound | retain; generate pooled displays from component records rather than hand-written prose |
| **P0-G3** | taxonomy incomplete | split initial/final; use evidence type × robustness fields including operational, inferential and prospective-model-based |
| **P0-G4** | too underspecified | define exact arm × map × objective × fold matrix, global profile method, failure policy and required archives |
| **P0-G5** | “preferably nested” is unenforceable | require nested tuning or a no-tuning frozen grid; separate estimators from propagation layers |
| **P0-G6** | “tracks” is undefined | freeze diagnostic metrics and admission/downgrade criterion; add positive and negative controls; use exact MAPE profiles |
| **P0-G7** | equal-budget conflicts with equal-count language | define shot/assay/resource budgets, covariance, positive controls, multiple true parameters and explicit mismatch scenarios |
| **P0-G8** | directionally strong | add strict/equality boundary rule, error band, near-zero convention, global topology and exact weighted-median profiling |
| **P0-G9** | key variants are optional “where feasible” | define mandatory minimum, cross-fitted construction, impossibility branch and exact prospective labels |
| **P0-G10** | strong | specify databases, dates, search strings, screening rules, closest-work dimensions and an early/final two-stage output |
| **NUM-TIME-01** | correctly rescoped | retain as numerical-model-structural only; reconcile active `PHYSICAL` artefact fields |
| **NUM-ENV-01** | correctly limited | retain as full-support numerical stability; do not use for fold-median robustness without like-for-like runs |

### 5.1 Suggested replacement gate text

#### P0-G1a — initial claim and estimand control

> Before any new scientific run, a machine-readable ledger records every candidate headline, exact wording, evidence type, robustness status, unit of analysis, estimand, aggregation, data/map protocol, source hash, alternative explanation and withdrawal rule. Existing active claim surfaces are reconciled or marked historical/superseded.

#### P0-G1b — final claim reconciliation

> After all analyses are frozen, the ledger is regenerated from final artefacts; every manuscript-bound number matches its source hash and estimand; all cross-file active-claim tests pass.

#### P0-G3a/G3b — scope control

> An initial model/evidence scope matrix exists before runs and a final version is regenerated after analyses. Every claim carries evidence type and robustness status; model-structural numerical checks are never described as physical validation.

#### P0-G5 — policy comparison

> Point-estimation policies and uncertainty-propagation layers are defined separately. Hyperparameters are selected only through a fully nested calibration-only procedure or a frozen no-tuning grid with all candidates reported. No evaluation-target chemical outcome or score influences policy, anchor, penalty or map selection. Level is re-profiled exactly under each point policy.

#### P0-G6 — H2 admission

> The weighted-L2 identity and exact MAPE weighted-median profile are proved and numerically checked. A frozen concordance criterion compares RSI with actual MAPE profile behaviour across predeclared designs, groups and `κ`, with positive and negative controls. Practical screening claims are retained, regime-limited or removed according to that criterion.

#### P0-G7 — observation-operator study

> Noiseless positive controls, multiple true `κ` regimes, resource-equated operator designs, correlated/heteroscedastic noise and declared mismatch scenarios are run with frozen seeds and replicates. Structural rank, global profile topology, parameter error, boundary frequency and prediction error are all reported. Conclusions are scoped to the tested model class.

#### P0-G8 — asymptotic classification

> The response and exact profiled-objective limits are derived or rigorously computed. For every tolerance, classification uses an explicit numerical error band: tail included, tail excluded or boundary indeterminate. Near-zero `J_min`, all connected profile components and global-search evidence are reported. Response shoulder and operational profile boundary remain separate.

#### P0-G9 — target-map protocol

> Current, common-map and scored-condition-excluded/cross-fitted variants are mandatory where raw support exists. Any infeasible variant is documented and automatically limits H3 to retrospective evidence. Limited-adaptation and physics-only variants are added where supportable. A genuinely prospective claim requires data collected after protocol freeze.

---

## 6. Required action register

## P0-A — V2.2 execution-integrity patch

### P0-A1 — Make the operative plan self-contained

**Objective:** Ensure the plan can be executed and audited without consulting superseded documents.

**Method:** Incorporate §9.1–§9.6, R0–R5, estimand definitions and manuscript architecture directly, or pin them through immutable normative references with a precedence rule.

**Deliverables:**

- `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md`
- operative SHA/version block
- complete glossary and dependency table

**Pitfalls:** copying stale language from V2; retaining undefined shorthand; allowing current-main references to drift.

**Checks:** no undefined gate, round, estimand or external section reference; manifest and plan agree exactly.

### P0-A2 — Create the plan manifest and fail-closed integrity tests

**Objective:** Replace regex reassurance with an enforceable control surface.

**Method:** Add a machine-readable manifest; discover the operative plan from it; validate gate DAG, required artefacts, active/historical surfaces, banned assertions and status transitions.

**Deliverables:**

- `PAPER_A_PLAN_MANIFEST_V1.yaml`
- revised `tests/test_paper1_plan_integrity.py`
- JSON/YAML schema tests

**Pitfalls:** parsing Markdown as the primary source of truth; hard-coded filenames; skipped tests; historical audit files falsely treated as active claims.

**Checks:** deleting/renaming the operative plan fails; adding an orphan gate fails; adding an active `PHYSICAL` verdict fails; updating to V2.3 requires only manifest change, not source-code path edits.

### P0-A3 — Reconcile active claims before scientific work

**Objective:** Prevent old claim surfaces from contaminating the next analytical cycle.

**Method:** Inventory and classify all active/historical surfaces; update interpretive metadata; append supersession notes rather than erasing audit history.

**Deliverables:**

- `PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md`
- `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json`
- `PAPER_A_MODEL_SCOPE_MATRIX.md`
- corrected/superseded saturation, information-parity and ablation artefacts

**Pitfalls:** changing numerical evidence while changing interpretation; silently rewriting history; failing to update producers as well as generated outputs.

**Checks:** producer `--check` modes reproduce current artefacts; active repository scan finds no withdrawn assertions.

### P0-A4 — Freeze the follow-up protocol honestly

**Objective:** Limit further post-selection and selective reporting.

**Method:** Freeze hypotheses, primary/secondary outcomes, policies, maps, thresholds, budgets, seeds, mismatch scenarios, optimisation rules, exclusions, failure handling and decision branches.

**Deliverables:**

- `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md`
- machine-readable companion JSON/YAML
- deviation log template

**Pitfalls:** describing same-data reanalysis as confirmatory; leaving “where feasible,” “preferably,” “adequately” or “tracks” undefined; changing primary outcomes after seeing results.

**Checks:** all later deviations are append-only, dated, justified and accompanied by impact analysis.

---

## P0-B — Exact profile, asymptotic and H2 work

### P0-B1 — Formalise exact MAPE profiling

**Objective:** Remove level-optimiser uncertainty and connect the actual production objective to the paper's mathematics.

**Method:** Prove the weighted-median level solution under positive predictions/observations; define non-unique median intervals; test against the existing implementation and brute-force controls.

**Deliverables:**

- proposition and proof;
- exact profile function;
- unit tests including ties and median switches;
- archived per-group MAPE profiles.

**Pitfalls:** zero/negative observations; selecting one median arbitrarily when an interval exists; treating nonsmooth profile points as Hessian curvature.

**Checks:** exact solution matches exhaustive numerical minimisation to tolerance over random positive cases and every campaign profile point.

### P0-B2 — Compute `J_inf` and classify the upper tail

**Objective:** Determine whether H1's one-sided profile language is actually supported.

**Method:** derive or rigorously compute `f_inf`; profile `I` exactly at the limit; compare against relative and absolute tolerance boundaries with an independently justified error band.

**Deliverables:** `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` plus derivation note.

**Pitfalls:** assuming monotonic convergence; ratio instability near zero; finite-grid aliasing; disconnected acceptable sets.

**Checks:** finite-`κ` solutions converge to the limit; responsive-regime falsification control remains sensitive; all connected components are recovered by grid refinement/global checks.

### P0-B3 — Define the response shoulder separately

**Objective:** Avoid using one arbitrary `κ` threshold for both response dynamics and profile acceptability.

**Method:** freeze a response-elasticity measure, such as `|∂log yhat/∂log κ|`, and report its crossing separately from objective thresholds.

**Deliverables:** group/solute/condition shoulder maps and sensitivity table.

**Pitfalls:** forcing one scalar shoulder across multiple outputs; confusing an output-level shoulder with a profile boundary.

**Checks:** shoulder classification is stable to derivative step and numerical configuration.

### P0-B4 — Validate or demote RSI

**Objective:** Determine whether the exact weighted-L2 geometry is practically useful under MAPE.

**Method:** run frozen positive/negative controls and design rankings across groups and `κ`; compare with exact MAPE profile metrics.

**Deliverables:** `PAPER_A_RSI_MAPE_VALIDATION.json`, full data table and downgrade decision.

**Pitfalls:** using six groups as if independent replicates; declaring success from correlation sign alone; pooling across regimes that reverse.

**Checks:** criterion fixed before results; stratified and pooled outputs both reported; no practical screening claim if criterion fails.

---

## P0-C — Target-map and policy work

### P0-C1 — Build a complete map-provenance and timing audit

**Objective:** Define exactly what M1−M2 measures and when each input would be available.

**Method:** trace shot-time anchors, conductivity fits, viscosity closure, pressure/temperature dependence, condition support and scored-condition reuse.

**Deliverables:**

- `PAPER_A_TARGET_MAP_PROVENANCE.md`
- machine-readable row-level lineage table
- information-flow diagram for M0/M1/M2 and all variants

**Pitfalls:** equating absence of target chemistry with absence of target information; hiding contemporaneous/post-shot measurements; treating fitted map values as direct measurements.

**Checks:** every prediction row has a complete lineage record and leakage/timing classification.

### P0-C2 — Run cross-fitted and limited-adaptation map variants

**Objective:** Test whether the coarse effect survives a defensible operational information protocol.

**Method:** scored-condition exclusion; frozen/nested adaptation counts and placements; no-target baseline; uncertainty propagation; condition-level fine-reversal analysis.

**Deliverables:** `PAPER_A_TARGET_MAP_ADAPTATION_RESULTS.json` and branch decision.

**Pitfalls:** selecting observation placement using target chemistry; calling same-campaign cross-fitting external validation; ignoring extrapolation leverage.

**Checks:** map error and chemical prediction error reported together; coarse/fine separated; automatic retrospective demotion if cross-fitting is infeasible or effect collapses.

### P0-C3 — Run the full LOCO-WIDE matrix

**Objective:** Establish whether policy contrasts depend on the published rate cap.

**Method:** predeclare every arm, map protocol, objective and fold; exact level profiling; global `κ` profile; complete failure logs.

**Deliverables:** `PAPER_A_LOCO_WIDE_RESULTS.json` with fold, grind, group and condition decompositions.

**Pitfalls:** substituting full-support runs for fold estimands; changing map support between arms; dropping failed folds silently.

**Checks:** like-for-like source hashes; all failures retained; pooled outputs generated from component records.

### P0-C4 — Compare point policies and propagation layers separately

**Objective:** Replace the `κ=1` anecdote with a transparent, non-causal policy comparison.

**Method:** nested calibration-only tuning or frozen no-tuning grid; exact level re-profiling; two-axis reporting.

**Deliverables:** `PAPER_A_KAPPA_POLICY_RESULTS.json` and `PAPER_A_PROFILE_PROPAGATION_RESULTS.json`.

**Pitfalls:** evaluation-target tuning; comparing point MAPE with envelope coverage; calling an operational envelope a confidence interval.

**Checks:** full candidate table, grind-specific results, no hidden winner selection, and explicit “no recommendation” branch.

---

## P0-D — Observation-operator and design work

### P0-D1 — Freeze a resource-equated synthetic design

**Objective:** Test the observation-information thesis without an unfair count-based comparison.

**Method:** define shot, assay and sample budgets; freeze operator designs, true parameter grid, seeds, replicates and noise covariance.

**Deliverables:** synthetic design specification and budget table.

**Pitfalls:** treating fractions as independent observations; using MAPE with near-zero values; choosing budgets after seeing which operator wins.

**Checks:** every design has explicit physical resource use and covariance structure.

### P0-D2 — Establish positive controls and recovery pipeline validity

**Objective:** Ensure failure to recover `κ` is scientifically interpretable rather than a code/design failure.

**Method:** noiseless rich-design recovery, local rank checks, global profile checks and a deliberately informative upper-bound design.

**Deliverables:** positive-control archive and pipeline acceptance report.

**Pitfalls:** assuming local rank guarantees global uniqueness; testing only at the inherited `κ=1`.

**Checks:** recovery across below/near/above-shoulder true values; known failure cases behave as expected.

### P0-D3 — Run noise and mismatch scenarios

**Objective:** Determine whether operator conclusions survive plausible experimental and model discrepancy.

**Method:** correlated/heteroscedastic noise; separate multipliers; time-varying flow; map error; geometry/dynamic-hydraulic mismatch.

**Deliverables:** `PAPER_A_OBSERVATION_OPERATOR_RECOVERY.json` and decision matrix.

**Pitfalls:** inverse crime; too many post hoc scenarios; interpreting synthetic coverage as empirical coverage.

**Checks:** every scenario frozen; all results reported; conclusions scoped to tested model classes.

---

## P0-E — Positioning, convergence and drafting

### P0-E1 — Complete P0-G10 in two stages

**Objective:** Avoid completing expensive work for a contribution that is already too narrow.

**Method:** preliminary search before heavy runs; final closest-work matrix after results determine the actual claim.

**Deliverables:** search log, screening table, closest-work matrix and bounded contribution paragraph.

**Pitfalls:** searching only for exact espresso wording; claiming novelty for variable projection/profile methods; using inaccessible database coverage as implied completeness.

**Checks:** dates, databases, search strings, inclusion/exclusion and closest-work distinctions recorded; no “first” language unless supportable.

### P0-E2 — Final claim/scope reconciliation

**Objective:** Ensure manuscript drafting begins from frozen evidence rather than memory.

**Method:** regenerate ledgers and matrices from final artefacts; run active-surface tests; resolve every deviation.

**Deliverables:** P0-G1b/P0-G2/P0-G3b/P0-G10 closeout matrix.

**Pitfalls:** retaining attractive provisional language after a gate fails; updating prose but not producer metadata.

**Checks:** every manuscript-bound statement has one source record and exact scope.

### P0-E3 — Branch the manuscript before drafting

**Objective:** Prevent H3 from being forced into the paper if it remains merely retrospective.

**Method:** apply the decision tree in §9 below; then freeze title, contribution list and manuscript architecture.

**Deliverables:** manuscript branch memo and final title.

**Checks:** no title/abstract/results/discussion drafting before all blocking gates and final P0-G10 close.

---

## 7. Recommended execution sequence

### Step 0A — V2.2 patch

1. Make the plan self-contained.
2. Add the machine-readable manifest and dependency DAG.
3. Correct the integrity test so it is fail-closed and version-independent.
4. Mark V2.1 superseded only after V2.2 passes its own controls.

### Step 0B — initial assurance artefacts

5. Create P0-G1a claim ledger.
6. Create P0-G3a scope matrix.
7. Complete active-claim reconciliation, including the `PHYSICAL` saturation verdict and stale producer docstrings.
8. Produce the preliminary P0-G10 positioning memo.

### Step 0C — protocol freeze

9. Freeze P0-G0, including exact gate decision rules, budgets, seeds, maps, policies, failure handling and same-data post-selection statement.

### Workstream B — first scientific critical path

10. P0-G8: exact MAPE profile, `f_inf`, `J_inf`, tail classification and shoulder.
11. P0-G6: exact weighted-L2 and MAPE mathematics; RSI validation/demotion.

### Workstream C — target information and policy

12. P0-G9: provenance, scored-condition exclusion, cross-fitted map and adaptation protocol.
13. P0-G4: LOCO-WIDE under the settled map protocol.
14. P0-G5: point-policy comparison and separate propagation analysis.

### Workstream D — model-based prospective design

15. P0-G7: positive controls, resource-equated observation operators, noise and mismatch.

### Convergence

16. Freeze all scientific outputs and hashes.
17. Complete P0-G1b, P0-G2 and P0-G3b.
18. Complete final P0-G10.
19. Select manuscript branch, title and contribution statement.
20. Draft, then run R0–R5 as explicitly defined in V2.2.

This sequence preserves V2.1's correct dependency logic—G9 before G4/G5 and G6/G8 before G7—while ensuring the initial controls actually exist before the work they are meant to govern.

---

## 8. Recommended replacement wording

## 8.1 H1

> **Within the declared two-grain model, matched whole-cup predictions approach finite limits as the common mass-transfer-rate multiplier `κ` increases. For each group, the production MAPE profile is formed by exact weighted-median profiling of the inventory level. Let `J_inf` be the resulting asymptotic profiled objective and `T` a predeclared relative or absolute operational threshold. If `J_inf` lies below `T` by more than the verified numerical error, an accepted upper tail is eventually present; if it lies above `T`, the upper tail is eventually excluded; equality within the error band is boundary-indeterminate and requires the approach direction and global profile topology. These classifications are model-, data-, objective- and convention-specific and do not establish that real espresso occupies the large-coefficient regime.**

## 8.2 H2

> **For `ŷ_i=I f_i(κ)` under fixed positive weights and the declared log-sensitivity coordinates, the weighted-L2 Gram determinant is `W² Var_w(s)` and the scale-profiled Schur complement is `W Var_w(s)`. Separately, for positive observations and predictions, the production MAPE level has an exact weighted-median solution with `κ`-dependent ratios and weights. The weighted-L2 sensitivity spread is therefore a local surrogate design diagnostic, not MAPE curvature; its ordinal usefulness is retained only if it meets the frozen validation criterion against exact MAPE profiles.**

## 8.3 H3

> **Under the current campaign-conditioned map protocol, substituting the target-grind flow map for the O-grind map produces a positive coarse-target M1−M2 contrast in all nine refit folds and a near-zero, heterogeneous, usually opposite fine-target contrast. This is a descriptive input-ablation result within the declared model. A scored-condition-excluded analysis can emulate a prospective adaptation protocol within the existing campaign; a genuinely prospective claim requires new target data collected after protocol freeze.**

## 8.4 H4

> **Weak localisation of the mass-transfer-rate multiplier under the declared endpoint objective prevents its fitted value from being interpreted as a uniquely learned kinetic quantity. Point-estimation rules—free, fixed, regularised or independently constrained—are compared under calibration-only selection, while profile propagation is reported separately as an operational sensitivity analysis. Any policy preference is scoped to the campaign and grind-specific results.**

## 8.5 Synthetic observation-operator section

> **Using known parameters, first establish noiseless positive-control designs under which the estimation pipeline can recover the multiplier. Then compare whole-cup, multi-endpoint and fractionated/time-resolved observation operators under resource-equated budgets, multiple true multiplier regimes, correlated/heteroscedastic noise and declared model mismatch. Improvement from time resolution supports an observation-compression explanation within the tested model class. Failure to improve does not by itself falsify that explanation; it triggers a predeclared branch assessing design adequacy, structural compensation and mismatch.**

## 8.6 Adaptation section

> **Estimate how predictive performance changes as predeclared target-grind hydraulic information is added. Within the existing campaign this is a cross-fitted prospective-protocol emulation, not independent prospective validation. The result becomes genuinely prospective only when the frozen adaptation protocol is applied to data not used to formulate or tune it.**

## 8.7 Unifying thesis

> **Whole-cup predictive performance and localisation of a model-specific mass-transfer-rate multiplier are distinct achievements. This study evaluates predictions fitted on optimal-grind chemical data and conditioned on explicitly declared target-grind hydraulic information separately from the ability of the endpoint observation operator to localise the multiplier. Temporal chemical observations and target-side hydraulic measurements are tested as different information channels, and all conclusions remain conditional on the model, objective, map protocol, campaign and external-validation boundary.**

---

## 9. Manuscript branch decision tree

| gate outcome | manuscript consequence |
|---|---|
| `J_inf` supports an accepted upper tail for most groups and result is threshold-robust | H1 may lead, with exact operational scope |
| `J_inf` excludes the tail or classification is threshold-dependent | lead with response limit + threshold-dependent profile behaviour; remove broad weak-localisation headline |
| RSI validates against MAPE | retain sensitivity-guided design contribution |
| RSI fails or is regime-specific | retain algebra and exact MAPE profile; demote/remove global design recommendation |
| cross-fitted map retains coarse benefit | retain H3 as cross-fitted prospective-protocol emulation |
| only full campaign-conditioned map retains benefit | keep H3 as retrospective secondary result; remove hydraulics from title/contribution list |
| new post-freeze data validate adaptation | H3 may become a genuine prospective contribution and potentially title-level |
| time-resolved synthetic operator improves recovery under controls/mismatch | integrated prediction-versus-identification narrative is strengthened |
| time-resolved operator does not improve recovery | branch toward deeper model-structural compensation or inadequate design; do not force the observation-compression story |
| P0-G10 finds integrated novelty too narrow | split H3 from the identifiability paper or terminate the weaker branch |

### Recommended publication branch today

Until P0-G7 and P0-G9 close, plan for the conservative branch:

- primary paper: prediction versus identification, exact production profile, large-coefficient limit and observation-operator analysis;
- H3: empirical case study/secondary section;
- hydraulics promoted only if cross-fitted or new-data adaptation survives.

---

## 10. Risk register additions

| additional risk | severity | mitigation |
|---|---|---|
| Integrity test gives false assurance because it checks literals rather than the declared controls | high governance | manifest-driven fail-closed tests and active-surface scan |
| Initial ledger/scope controls are created only after analyses | high post-selection | split P0-G1/P0-G3 into initial and final phases |
| Same-data freeze is described as independent confirmation | high inference | explicit post-selection reanalysis label; new data for confirmation |
| `J_inf` equals threshold within numerical error | high for H1 classification | three-way boundary rule and approach/topology analysis |
| `J_min≈0` makes relative threshold unstable | moderate/high in synthetic controls | absolute threshold branch and near-zero convention |
| Global profile has multiple/disconnected near-optimal components | high for localisation wording | exact level profiling, global `κ` search and component reporting |
| Exact-MAPE median switches make local weighted-L2 geometry misleading | high for H2 | exact MAPE proposition and negative controls |
| Cross-fitted adaptation is mislabeled genuinely prospective | high for H3 | three-level evidence taxonomy; new-data requirement |
| Fine reversal reflects map extrapolation or error cancellation | high for H3 | leverage/map-error diagnostics and perturbation analysis |
| Target map placement/count selected using target chemistry | high leakage | freeze or nest placement entirely within hydraulic/calibration support |
| Profile propagation is compared as if it were a point estimator | high H4 interpretation | two-axis estimator × propagation design |
| Nested policy tuning is unstable with nine conditions | moderate/high | report instability; frozen no-tuning grid alternative; no target-score tuning |
| Synthetic experiment commits an inverse crime | high design validity | positive controls plus declared model mismatch |
| Fraction observations are treated as independent | high uncertainty | within-shot covariance and resource-based budgets |
| MAPE is unstable for zero/near-zero synthetic observations | moderate/high | predeclared positivity/alternative-loss rule |
| “Competitive” or “useful” appears without comparator/margin | moderate | exact numbers or frozen comparator and practical margin |
| Historical `PHYSICAL`/attribution language remains searchable as current | high claim integrity | explicit supersession metadata and active/historical manifest |

---

## 11. Title and manuscript architecture

## 11.1 Title

The main title is good and should remain the provisional default:

> **Separating Prediction from Mass-Transfer-Rate Identification in Whole-Cup Espresso Modeling**

Recommended subtitle:

> **Large Mass-Transfer-Coefficient Limits, Sensitivity Geometry, and Grind-Specific Flow Inputs**

This is more precise than “Large-Coefficient Limits” and matches the terminology rule.

If H3 remains retrospective, omit hydraulics from the title. If P0-G9 produces only same-campaign cross-fitting, describe it as adaptation/protocol emulation in the paper but do not imply external prospective validation.

## 11.2 Recommended self-contained manuscript architecture

1. **Introduction — prediction is not parameter identification**  
   State the practical espresso problem, exact information question and narrow novelty.

2. **Data, calibration layers, model and information protocol**  
   Distinguish inherited Schmieder/Pannusch parameters, Angeloni O-grind fitting, target hydraulic inputs and target chemical outcomes.

3. **Exact factorisation and production-MAPE profiling**  
   Present `ŷ=I f(κ)`, weighted-median level profiling, Gram determinant and Schur complement with exact scope.

4. **Large-mass-transfer-coefficient response and objective limits**  
   Separate response shoulder, `J_inf`, operational thresholds and global profile topology.

5. **What observation operators preserve and discard**  
   Present positive controls and the resource-equated synthetic comparison.

6. **Conditional cross-grind prediction and flow-map ablations**  
   Lead with coarse/fine decomposition; separate retrospective, cross-fitted and genuinely prospective evidence.

7. **Estimation policy and prediction sensitivity**  
   Point policies first; profile propagation separately.

8. **Prospective experimental and adaptation implications**  
   Distinguish kinetic-information experiments from hydraulic adaptation requirements.

9. **Discussion**  
   Separate model structure, campaign evidence, physical assumptions, post-selection, mismatch and external validity.

10. **Conclusions**  
    State only the branch supported by P0-G6–P0-G10.

The original −0.394 pp comparison should remain a secondary historical benchmark, not a thesis, title or abstract result.

---

## 12. V2.2 acceptance checklist

V2.2 can be declared operative when all of the following are true:

- [ ] It is self-contained or every normative dependency is pinned immutably.
- [ ] `R0–R5`, estimand tags and evidence categories are defined locally.
- [ ] A manifest identifies the operative plan and gate DAG.
- [ ] Missing operative files fail tests rather than skip.
- [ ] Initial claim ledger and scope matrix exist before P0-G0.
- [ ] Current active artefacts are reconciled or explicitly superseded.
- [ ] The `PHYSICAL` saturation verdict is no longer an active current interpretation.
- [ ] M0−M2 is consistently described as an estimation-policy contrast.
- [ ] H1 uses the three-way asymptotic boundary rule.
- [ ] Exact weighted-median MAPE profiling is part of P0-G6/P0-G8.
- [ ] P0-G5 has a mandatory tuning rule.
- [ ] P0-G6 has a frozen admission/downgrade criterion and both controls.
- [ ] P0-G7 defines resource budgets, covariance, positive controls and mismatch.
- [ ] P0-G9 defines mandatory cross-fitting and a demotion branch.
- [ ] Same-campaign cross-fitting is not called genuinely prospective.
- [ ] Point-estimation policy is separated from profile propagation.
- [ ] “Competitive,” causal “because,” and ambiguous “source-calibrated” wording are removed or precisely defined.
- [ ] The terminology count and unqualified “Response saturation” defect are corrected.
- [ ] All integrity tests pass against V2.2 and active claim surfaces.

---

## 13. Final recommendation

V2.1 should be regarded as a **scientifically successful response to the prior review but not yet an executable operative plan**.

The central pivot is now compelling. It can produce a stronger paper than the original benchmark-comparison manuscript, especially if the exact production-MAPE profile is elevated into the mathematics and the observation-operator study is designed rigorously. The target-flow-map result remains interesting because it is asymmetric and information-protocol dependent, not despite those limitations.

The next move should therefore be a **focused V2.2**, not another wholesale conceptual pivot. The patch should concentrate on:

1. initial assurance artefacts;
2. exact and enforceable gate definitions;
3. repository-wide claim reconciliation;
4. exact MAPE/asymptotic analysis;
5. honest prospective labels;
6. resource-equated synthetic design; and
7. separation of estimation policy from sensitivity propagation.

Once those controls are in place, P0-G8 remains the correct first scientific analysis because `J_inf` can materially change H1's headline. P0-G6 should follow immediately and exploit the already implemented exact weighted-median MAPE structure. P0-G9 should then determine whether H3 remains a retrospective case study, becomes a cross-fitted operational result, or justifies a new-data prospective campaign.

---

## 14. Sources reviewed

### Operative plan and review history

- [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md` at the reviewed commit](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md)
- [Commit `66766801639b6338ada2e194e5a2be1d0bd77c59`](https://github.com/trbrewer/puckworks/commit/66766801639b6338ada2e194e5a2be1d0bd77c59)
- [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_REVIEW_20260801.md`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_REVIEW_20260801.md)
- [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md`, superseded](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md)

### Plan controls and current claim surfaces

- [`tests/test_paper1_plan_integrity.py`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/tests/test_paper1_plan_integrity.py)
- [`PAPER_A_CLAIM_LEDGER.md`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_A_CLAIM_LEDGER.md)
- [`PAPER_A_SATURATION_VERIFICATION.json`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_A_SATURATION_VERIFICATION.json)
- [`PAPER_A_INFORMATION_PARITY.json`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_A_INFORMATION_PARITY.json)
- [`PAPER_A_ABLATION_REFIT_STABILITY.json`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/docs/paper1_resource/PAPER_A_ABLATION_REFIT_STABILITY.json)

### Producers and model implementation

- [`puckworks/paper_a/separability.py`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/puckworks/paper_a/separability.py)
- [`tools/paper_a_information_parity.py`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/tools/paper_a_information_parity.py)
- [`puckworks/validation/slow/angeloni_bracket.py`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/puckworks/validation/slow/angeloni_bracket.py)
- [`puckworks/models/pannusch2024/solver.py`](https://raw.githubusercontent.com/trbrewer/puckworks/66766801639b6338ada2e194e5a2be1d0bd77c59/puckworks/models/pannusch2024/solver.py)

