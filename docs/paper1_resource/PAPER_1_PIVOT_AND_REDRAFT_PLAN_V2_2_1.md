# Paper 1 — pivot and redraft plan, revision 2.2.1

**Prepared:** 2 August 2026
**Status:** proposal for review. **Gate and artefact status is recorded in `PAPER_A_PLAN_MANIFEST_V1.json` and nowhere else — the manifest is the only status source**, so prose here never asserts that a gate has passed. Activation is two-stage (§7.4).
**Supersedes:** v1, v2, v2.1, v2.2 — all retained with banners, all classified `historical`.
**Actions:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_REVIEW_20260802.md`
**No manuscript file has been modified and the redraft has not started.**

This document is the **human-readable member of a controlled normative bundle**.
`PAPER_A_PLAN_MANIFEST_V1.json` enumerates the authoritative plan, protocol, initial claim ledger,
scope matrix, reconciliation, gate definitions and subsequently generated gate artefacts, each with
an immutable content hash. Operative authority attaches only to the frozen content commit and the
recorded hashes — not to a filename. Every gate, round, estimand, vocabulary and decision rule is
defined here or in a bundle member; nothing normative is delegated to a superseded plan or to a
review document.

---

## 0a. Disposition of the fourth review

Every checkable claim was verified against the repository before acceptance. All hold.

| id | finding | verified | disposition |
|---|---|---|---|
| GOV-01 | `importorskip` let the fail-closed control skip | yes | **Accepted.** Manifest is JSON; no optional parser; a test parses this module and fails on any skip call |
| GOV-02 | no discovery; the protocol was classified as neither active nor historical | yes — **81 of 100** candidates were unclassified | **Accepted.** Discovery globs; every candidate must be classified |
| GOV-03 | blanket quote stripping defeats JSON/Python rules | yes — `{"verdict": "PHYSICAL"}` became `{ :  }`; two rules could never fire | **Accepted.** Format-aware scanner: JSON parsed, Python via `ast`+`tokenize`, prose keeps mention-vs-assert |
| GOV-04 | gate closure bound only to file existence | yes | **Accepted.** Closure records with criteria, evidence scope, and deliverable + producer hashes |
| GOV-05 | initial and final ledgers shared a path | yes | **Accepted.** `_INITIAL` / `_FINAL` / `_DIFF` split; the baseline declares itself immutable |
| GOV-06 | `operative_commit` was not an implementable pin | yes — a commit cannot contain its own SHA | **Accepted.** Two-stage freeze/activation (§7.4) |
| REC-01…05 | active producers and archives still asserted withdrawn claims | yes — 20 findings once the scanner could read | **Accepted.** Fixed at source and regenerated; `--check` renamed `--exists` |
| DOC-01 | assurance overclaim, and a stale artefact count | yes | **Accepted.** Both replaced |
| SEQ-01 | R0 sequenced after drafting | yes | **Accepted.** Split R0a (pre-freeze) / R0b (pre-drafting) |
| NOV-01 | P0-G10 was a deadlock with no owner or package | yes | **Accepted.** Protocol and handoff artefacts are now gate deliverables |
| TAX-01, LED-01/02 | taxonomy and ledger semantics | yes | **Accepted in principle — NOT yet implemented.** See §12 |
| PRO-01…08, SCI-01…04 | the protocol is not yet genuinely frozen | yes | **Accepted — NOT yet implemented.** See §12 |

### What I take from this round

The control I described as fail-closed could skip, covered 14 % of the surfaces it claimed, and had
deleted the content two of its rules were written to inspect. I found that out because the review
ran the probes I had not. Before believing this round's clean scan, I ran seven adversarial probes —
and one of them failed, exposing a second-order version of the same bug: once JSON was parsed
structurally, a `"key": "value"` rule stopped matching because key and value had become separate
strings. That is now a test.

---

## 0b. Disposition of the third review

Every checkable claim was verified against the repository before acceptance. All hold.

| § | finding | verified | disposition |
|---|---|---|---|
| 3.1 | Plan not self-contained — §9.1–9.6 "carried from v2", `R0–R5` undefined, architecture deferred to a review | yes | **Accepted.** This revision is self-contained |
| 3.2 | `P0-G1` says "from the start" but the sequence postpones it | yes | **Accepted.** Split into `P0-G1a`/`P0-G1b`, `P0-G3a`/`P0-G3b` |
| 3.3 | The integrity test does not implement the checks §9.7 advertises | yes — `saturation` and `physical verification` absent from the ban list, reference→definition only, one literal count check, hard-coded path, `pytest.skip` on absence, no cross-file scan | **Accepted.** Replaced with a manifest-driven fail-closed control |
| 3.4 | Active artefacts still assert withdrawn claims | yes — all eight confirmed | **Accepted.** Reconciled before the freeze |
| 3.5 | H1 needs a complete three-way tail rule | yes | **Accepted** |
| 3.6 | H2 should use the exact production-MAPE structure, not only validate a surrogate | yes | **Accepted.** Now a three-part result |
| 3.7 | H3 cannot become prospective by re-slicing the same campaign | yes | **Accepted.** Three evidential levels; cross-fitting mandatory |
| 3.8 | H4 mixes point estimators with uncertainty propagation | yes | **Accepted.** Two-axis design |
| 3.9 | The synthetic study is underspecified and overinterpreted | yes | **Accepted.** Five stages; "either outcome is publishable" removed |
| 3.10 | Thesis contains "competitive", a causal "because", and an ambiguous "source-calibrated" | yes | **Accepted.** Rewritten |
| 3.11 | P0-G0 controls future flexibility but does not erase same-data post-selection | yes | **Accepted.** Labels declared |
| 3.12 | The four-class evidence taxonomy cannot represent the plan's own hierarchy | yes | **Accepted.** Eight types × nine robustness statuses |
| — | "Three ambiguities" above a five-row table | yes | **Accepted.** Count checked mechanically now |
| — | V2.1 asserted "Response saturation is a model property" while banning unqualified "saturation" | yes | **Accepted** |

### What I take from this round

I built a control that checked literals and described it as a control that enforces the plan — a
claim about assurance that outran its evidence, which is the same species of error as the scientific
overclaims this pivot exists to fix.

**And I did it again in v2.2.** The replacement was described as fail-closed while obtaining its
manifest through `pytest.importorskip`, so it skipped on any lane without PyYAML; it was described
as scanning every active surface while iterating over 14 hand-listed paths out of 100 candidates;
and it stripped every quoted span before matching, which in JSON and Python deletes precisely the
content the rules were written to read. Two of the rules could never fire.

The replacement control is designed and adversarially tested against the enumerated failure classes.
It reduces recurrence of those failures; **it does not establish that unanticipated control defects
are impossible.**

---

## 1. Terminology

| use exactly | never write | why |
|---|---|---|
| **mass-transfer-rate multiplier**, symbol `κ` | "extraction rate", "the rate" | it multiplies `A1`/`A2`, the Sherwood prefactors in `Sh = A·Re^B·Sc^⅓`, giving `h = Sh·D/d₃₂`. Not a flow rate, not a validated constant |
| **large-mass-transfer-coefficient limit** | "saturation" unqualified | reads as a physical claim about espresso |
| **cross-grind prediction** | "transfer" for evaluation | |
| **target-grind flow-map substitution** | "hydraulic transfer", "hydraulic attribution" | supplied at prediction time, not carried across |
| **operational near-optimal set** | "confidence interval" | a declared tolerance convention |
| **input ablation** | "attribution" | geometry was frozen, never varied |

`κ = 1` is the inherited source normalisation, not an externally validated value.

---

## 2. Hypotheses

### H1 — model response limit and conditional tail classification

> Within the declared two-grain model, matched whole-cup predictions approach finite limits as `κ`
> increases. For each group the production MAPE profile is formed by **exact weighted-median
> profiling** of the inventory level. Let `J_inf` be the asymptotic profiled objective and `T` a
> predeclared tolerance. If `J_inf < T − ε` an accepted upper tail is eventually present; if
> `J_inf > T + ε` it is eventually excluded; if `|J_inf − T| ≤ ε` the classification is
> **boundary-indeterminate** and requires approach direction and global profile topology. Under the
> 10 %-relative rule and a finite scan to `κ = 500`, five of six profiles are right-censored and one
> is finite. **`J_inf` has not been computed; the classification is provisional.**

`ε` comes from verified asymptotic and profiling error, not display precision. Equality is **not** a
trivial accepted case. Whether real espresso occupies this regime is untested.

### H2 — exact geometry, exact MAPE profile, and a tested diagnostic

Three separate results, not one:

1. **Weighted-L2 identity.** `det(G) = W²·Var_w(s)`; the scale-profiled Schur complement is
   `W·Var_w(s)`.
2. **Exact production-MAPE profile.** For `y_i, f_i > 0`,
   `J(I,κ) = mean_i w_i(κ)·|I − r_i(κ)|` with `w_i = f_i/y_i`, `r_i = y_i/f_i`; any weighted median
   of `r` with weights `w` minimises the level exactly, and the minimiser may be an **interval**.
3. **Diagnostic test.** Whether the sensitivity spread provides useful ordinal ranking against
   *actual* MAPE profile behaviour, under the frozen criterion in the protocol.

(1) is not the curvature of (2). (2) removes optimiser uncertainty from the profile, gives an exact
construction of `J_inf` once `f_inf` is known, and exposes the median-switch kinks where the
surrogate is most likely to disagree — which is why it bridges H1 and H2 rather than being an
implementation detail.

### H3 — grind-specific target-flow-map substitution

> Under the current campaign-conditioned map protocol, substituting the target-grind flow map for
> the O-grind map gives a **coarse**-target M1−M2 contrast of **+1.234 pp**, positive in 9 of 9
> folds, and a **fine**-target contrast of **−0.037 pp**, range −0.671 to +0.086, negative in 7 of 9:
> **near-zero in median, heterogeneous in magnitude, and usually opposite in direction.** This is a
> descriptive **input ablation** within the declared model. Particle geometry and other
> grind-dependent physics were held fixed and were not tested as competing explanations.

Within each fold the pooled contrast is the equal-weight mean of the coarse and fine contrasts. The
reported pooled **median** is the median of those fold averages and **must not** be reconstructed
from the component medians: (1.234 − 0.037)/2 = **0.5985**, whereas the archived pooled median is
**0.524**. Median is not linear, and the pooled figure is coarse-driven.

Three evidential levels, never conflated:

1. **retrospective campaign-conditioned** — the current result;
2. **cross-fitted prospective-protocol emulation** — scored condition excluded from map
   construction, same campaign;
3. **genuinely prospective empirical test** — data collected after the freeze. **None exists.**

### H4 — estimation policy, on two axes

> **If P0-G8 establishes weak or one-sided practical localisation** under the declared operational
> near-optimal set, the fitted `κ` cannot be read as uniquely learned from matched whole-cup
> endpoints. **Independently of that outcome — including if the profile turns out to be finite —
> interpreting `κ` as a transferable physical kinetic constant remains unsupported without external
> validation and model-discrepancy analysis.** **Point-estimation rules** — free, fixed, regularised,
> independently constrained — are compared under calibration-only selection. **Profile propagation**
> is reported **separately** as an operational sensitivity analysis, never ranked against a point
> estimator. Any preference is scoped to this campaign and is grind-specific.

A point prediction scored by MAPE and an envelope with no coverage interpretation are different
objects. What must be independent of evaluation-target **chemical outcomes** is policy and
hyperparameter selection; declared target **hydraulic** covariates are permitted by H3's protocol.

### Unifying thesis

> **Whole-cup predictive performance and localisation of a model-specific mass-transfer-rate
> multiplier are distinct achievements.** This study evaluates predictions fitted on optimal-grind
> chemical data and conditioned on explicitly declared target-grind hydraulic information,
> separately from the ability of the endpoint observation operator to localise the multiplier.
> Temporal chemical observations and target-side hydraulic measurements are tested as different
> information channels. All conclusions remain conditional on the model, objective, map protocol,
> campaign and external-validation boundary.

"Competitive", the causal "because", and "source-calibrated" are removed. The three calibration
layers are named explicitly in `PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md` §5.

### Narrative spine

1. the source model was calibrated against time-resolved fractionated kinetics;
2. this paper uses matched whole-cup endpoints, which compress that information;
3. under that operator, inventory and `κ` can compensate near the large-coefficient limit;
4. prediction may nevertheless remain stable given declared target-side flow information;
5. the information supporting prediction need not be the information identifying kinetics;
6. prospective measurements should be chosen according to which is wanted.

---

## 3. Corrections carried from v2.1

| v2.1 said | corrected |
|---|---|
| "Response saturation is a model property" | "The response limit is a property of the declared model" — unqualified "saturation" is banned by this plan's own terminology table |
| "Three ambiguities" above a five-row table | count checked mechanically; the table stands at five |
| §9.1–9.6 "carried from v2 unchanged" | reproduced here (§7, §8) |
| architecture "per the review's §12" | reproduced here (§9) |
| `R0–R5` used but undefined | defined in §8.3 |
| `P0-G1`/`P0-G3` required "from the start" but sequenced last | split `a`/`b`; the `a` phases precede P0-G0 |
| P0-G9 variants "where feasible" | mandatory minimum plus an explicit impossibility branch that demotes H3 |
| P0-G5 "preferably nested" | mandatory: nested, or a frozen no-tuning grid with all candidates reported |
| P0-G6 "tracks" | a frozen numeric admission criterion (protocol §3.2) |
| P0-G7 equal-budget vs equal-count | resource-equated budgets in physical units; equal counts explicitly rejected |
| "Either outcome is publishable" | removed; publication value is conditional on P0-G10 |
| four-class evidence taxonomy | eight evidence types × nine robustness statuses |

---

## 4. Evidence framework

Two independent fields. Neither is a scalar tier.

**Evidence type:** algebraic · numerical-model-structural · empirical-descriptive ·
operational-convention · inferential · prospective-model-based · physical-external ·
exploratory-oracle

**Robustness:** established-under-assumptions · verified-within-numerical-scope · refit-stable ·
heterogeneous · sensitivity-only · cross-fitted · externally-replicated · unresolved · withdrawn

Full assignment: `PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md`. Per-claim records:
`PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json`.

### Estimand tags

Every reported number carries exactly one; none migrates without a like-for-like re-run.

| tag | meaning |
|---|---|
| **FULL-PUB** | full calibration support, published `κ` domain |
| **FULL-WIDE** | full calibration support, widened `κ` domain |
| **LOCO-PUB** | leave-one-condition-out refit, published domain |
| **LOCO-WIDE** | leave-one-condition-out refit, widened domain |
| **NUM-FULL** | full-support numerical envelope |

---

## 5. What we are not claiming

1. That real espresso reaches the large-mass-transfer-coefficient regime.
2. That `κ` is a physical kinetic constant, or `κ = 1` externally validated.
3. That the acceptable set is unbounded — only right-censored at `κ = 500`.
4. That hydraulics are the unique or causal mechanism of cross-grind prediction.
5. That particle geometry is excluded — it was frozen, never varied.
6. That freezing is universally preferable to fitting.
7. That the target map is available in a zero-target-data workflow.
8. That the weighted-L2 geometry predicts MAPE profile behaviour — untested.
9. Structural non-identifiability.
10. Any "first" or "to our knowledge" claim, until P0-G10 — which cannot close in this environment.
11. **Symmetrically:** that the effect is absent, or that fitting is harmful.
12. That same-campaign cross-fitting is independent prospective validation.

---

## 6. Gates

Definitions and dependencies are authoritative in `PAPER_A_PLAN_MANIFEST_V1.json`; this table is the
human-readable view. All `blocks_drafting` gates block the results narrative, title, abstract,
discussion and contribution list.

| gate | question | pass criterion |
|---|---|---|
| **NUM-TIME-01** | plateau: BDF artefact or structural to the declared model? | **passed**, numerical-model-structural only; physical generalisation untested |
| **NUM-ENV-01** | do FULL-SUPPORT contrasts survive mesh/tolerance change? | **passed**, full-support only; not fold medians |
| **P0-R0a** | pre-freeze premise audit — does every load-bearing premise have assurance matched to its type? | every premise recorded with evidence or an explicit open/scoped disposition. **Its purpose is to surface blockers before the freeze; finding them is a pass, and keeps P0-G0 shut** |
| **P0-G0** | are the next analyses protected from target-driven tuning? | complete protocol committed before P0-G4…G9; **P0-R0a, P0-G1a and P0-G3a closed**; bundle cross-references clean; freeze record complete; deviations append-only |
| **P0-G1a** | initial claim ledger | every candidate and active headline recorded before any new run |
| **P0-G1b** | final reconciliation | ledger regenerated from final artefacts; every bound number matches its hash |
| **P0-G2** | disaggregation | every pooled headline shown with components and weighting rule; homogeneity **not** required |
| **P0-G3a** | initial scope matrix | every claim tagged type × robustness before runs |
| **P0-G3b** | final scope reconciliation | regenerated; no model-structural check described as physical validation |
| **P0-G4** | LOCO-WIDE | every fold refit on the frozen wide domain with diagnostics and failure logs; no sign outcome required |
| **P0-G5** | policy comparison | nested or frozen-grid tuning; axes separate; pass = completed, even with no winner |
| **P0-G6** | H2 | both propositions proved; RSI judged against the frozen criterion; both controls present |
| **P0-G7** | observation operators | positive controls, resource-equated budgets, multiple true `κ`, noise covariance, declared mismatch |
| **P0-G8** | asymptotics | `J_inf` computed; three-way classification with error band; components and shoulder reported separately |
| **P0-G9** | target map | provenance and timing per row; cross-fitted variant mandatory; impossibility demotes H3 |
| **P0-G10** | novelty | search log and closest-work matrix; pass = bounded statement supportable **or** claims narrowed/split/terminated |

---

## 7. Premise assurance

Evidence matched to premise type. A physical premise that cannot be tested with available data is
marked **open or scoped**, never forced into a repository test that merely restates the model.

| premise type | assurance |
|---|---|
| algebraic | proof plus symbolic/numerical check |
| numerical | convergence, alternate path, **patch-effect controls** |
| data/provenance | source reconciliation, transcription check, lineage |
| inferential | estimand clarity, resampling unit, negative controls |
| physical | independent measurement, external literature, or an explicitly flagged unvalidated assumption |
| novelty | documented indexed search |

---

### 7.4 Activation ceremony

A commit cannot contain its own SHA, so a single self-pinning field is not implementable. Activation
is two-stage:

1. **Freeze commit F** — carries the final normative bundle; manifest `operative_status:
   candidate-frozen`; `activation.frozen_hashes` records the SHA-256 of every bundle member.
2. **Activation commit A** — changes control metadata only; sets `operative_status: operative` and
   `activation.frozen_content_commit: F`.

At A and every descendant the control verifies each bundle member's current hash against the value
recorded at F. Any normative change after activation requires a versioned amendment and a deviation
record. A non-null string is not a pin.

---

## 8. Review programme

### 8.1 Claim–premise–test matrix

For every headline: exact wording; evidence type; robustness; data and observation unit; calibration
and target information supplied; estimand tag; resampling unit; model and numerical configuration;
supporting artefact and hash; **alternative explanation**; external-validity boundary; **falsifying
result**. Held in `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json`.

### 8.2 Termination rule

A round closes when: no unresolved critical or major finding remains in scope; every finding has a
documented disposition; the claim–premise–evidence chain is internally consistent; **the contribution
remains non-trivial and relevant**; and required changes are verified in artefacts. "No defect found"
is not an acceptance criterion.

### 8.3 Rounds

| round | reviewer | scope | acceptance |
|---|---|---|---|
| **R0a** | internal, **before the protocol freeze** | premise audit — every load-bearing assumption gets evidence matched to its type | each premise has assurance appropriate to its type, or is marked open/scoped. Running this before the freeze is the point: a missing premise found afterwards forces an unplanned deviation or a second freeze |
| **R0b** | internal, after outputs are frozen | convergence premise audit | results introduced no new unassured premise |
| **R1** | numerical / scientific computing | NUM-TIME-01, NUM-ENV-01, P0-G8 asymptotics, the exact-MAPE proposition | no unresolved critical/major finding in the linear-operator argument, the error band, or the controls |
| **R2** | inverse problems / parameter estimation | H1, H2, estimand discipline, profile topology | no local result overextended to a global claim; no Fisher or coverage language absent a declared likelihood |
| **R3** | espresso experimentalist / food-process engineer | H3, H4, design recommendations, omitted physics | recommendations are explicitly prospective and model-based; claims scoped to this machine and campaign; no cross-machine generalisation |
| **R4** | skeptical statistician | every claim against its evidence type and robustness | no claim stated above its record; post-selection labels correct; dependent folds not treated as independent |
| **R5** | editorial | prose, figures, tables, length | closed checklist. **A reviewer may always flag a factual or scientific error**; the rule bars reopening settled preferences, not corrections |

R1 runs first among the external rounds: the linear-operator argument is the single point on which
H1's verification rests, and if it falls the later rounds are wasted.

---

## 9. Manuscript architecture

1. Introduction — prediction is not parameter identification
2. Data, **three calibration layers**, model, and information available at prediction time
3. Exact factorisation and production-MAPE profiling
4. Large-mass-transfer-coefficient response and objective limits *(response shoulder and profile
   boundary kept separate)*
5. What observation operators preserve and discard *(positive controls; resource-equated comparison)*
6. Conditional cross-grind prediction and flow-map ablations — **leading with coarse/fine**, with
   retrospective, cross-fitted and prospective evidence separated
7. Estimation policy and prediction sensitivity — point policies first, propagation separately
8. Prospective experimental and adaptation implications
9. Discussion — model structure, campaign evidence, physical assumptions, post-selection, mismatch,
   external validity
10. Conclusions — only the branch supported by P0-G6 … P0-G10

The −0.394 pp comparison is a secondary historical benchmark. It appears in no title, abstract, or
contribution bullet.

### Title

> **Separating Prediction from Mass-Transfer-Rate Identification in Whole-Cup Espresso Modeling**
>
> *subtitle:* **Large Mass-Transfer-Coefficient Limits, Sensitivity Geometry, and Grind-Specific
> Flow Inputs**

If H3 remains retrospective, hydraulics leave the title. Finalised after P0-G8, P0-G9 and P0-G10;
H4 wording after P0-G5.

### Branch decision tree

| outcome | consequence |
|---|---|
| `J_inf` supports an accepted tail for most groups, threshold-robust | H1 may lead |
| `J_inf` excludes the tail, or classification is threshold-dependent | lead with the response limit and threshold dependence; remove the broad weak-localisation headline |
| RSI meets its criterion | retain the design contribution |
| RSI fails or is regime-specific | retain algebra and exact profiling; remove the global design recommendation |
| cross-fitted map retains the coarse benefit | H3 as cross-fitted protocol emulation |
| only the full campaign-conditioned map retains it | H3 retrospective secondary; hydraulics out of the title |
| time-resolved operator improves recovery under controls | integrated narrative strengthened |
| it does not | branch to structural compensation or design adequacy; do not force the story |
| P0-G10 finds the contribution too narrow | split or terminate the weaker branch |

**Conservative branch, assumed until P0-G7 and P0-G9 close:** primary paper is prediction versus
identification, exact profiling, the large-coefficient limit, and the observation-operator analysis;
H3 is a secondary case study.

---

## 10. Risks

| risk | severity | mitigation |
|---|---|---|
| ~~plateau is a BDF artefact~~ | ~~fatal~~ | retired — NUM-TIME-01 |
| **real espresso does not occupy the large-coefficient regime** | **high** | scope every statement; state the external-validation gap |
| `J_inf` above tolerance, or within `ε` of it | **high — could reverse H1** | three-way rule; P0-G8 first |
| weighted-L2 geometry does not predict MAPE profiles | high | P0-G6 frozen criterion, both controls |
| the 10 % threshold drives the 5/6 classification | high | threshold family, absolute and relative |
| **post-selection on the same campaign** | **high** | P0-G0 freeze **plus** explicit labels; a freeze is not confirmation |
| target map unavailable prospectively | high | P0-G9 provenance, timing, cross-fitting |
| fine reversal is error cancellation or extrapolation | high | condition-level residual and perturbation analysis |
| dependent folds read as independent | high | descriptive language only |
| static map hides dynamic hydraulics | high | map-form sensitivity; explicit scope |
| profile propagation compared as a point estimator | high | two-axis design |
| nested tuning unstable with nine conditions | moderate | report the instability; frozen grid alternative |
| synthetic study commits an inverse crime | high | positive controls plus declared mismatch |
| fractions treated as independent | high | within-shot covariance; resource budgets |
| MAPE unstable near zero | moderate | predeclared positivity rule |
| adjectives without comparators | moderate | report numbers |
| **integrity control gives false assurance** | **high** | manifest-driven, fail-closed, active-surface scan |
| artefacts diverge from prose again | high | reconciliation before the freeze, enforced by test |
| H1/H2/H4 and H3 do not form one paper | high | the §2 spine; branch after P0-G9 |
| novelty overstated | reputational | P0-G10 blocks title and contributions |

---

## 11. Sequence

**Step 0A — plan integrity.** This document; the manifest; the fail-closed control. *(done)*

**Step 0B — initial assurance artefacts.** `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json`;
`PAPER_A_MODEL_SCOPE_MATRIX_V1_INITIAL.md`; `PAPER_A_ACTIVE_CLAIM_RECONCILIATION.md`; preliminary P0-G10 memo.
*(ledger, matrix and reconciliation done; novelty memo blocked — see §12)*

**Step 0C — protocol freeze.** `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V2.md`. *(drafted; freezes on
approval)*

Then, in parallel:

| workstream | contents |
|---|---|
| **A — positioning** | P0-G10, from day one |
| **B — mathematics** | P0-G8 (`J_inf`, tail classification, shoulder) → P0-G6 (both propositions, RSI admission) |
| **C — target information** | P0-G9 → P0-G4 → P0-G5 |
| **D — prospective design** | P0-G7, after B defines the diagnostics |

**Convergence:** freeze all outputs and hashes → P0-G1b, P0-G2, P0-G3b → final P0-G10 → branch,
title, contribution → draft per §9 → R0 … R5.

**P0-G8 is first among the analyses**: `J_inf` can reverse H1's headline, and it is now cheap — the
operator is linear and the exact-in-time path exists.

### Drafting rule

**May proceed now:** methods source notes, data provenance, derivations, numerical appendix — as
standalone controlled artefacts, **not** manuscript sections.
**May not proceed:** results narrative, title, abstract, discussion, contribution list — until every
blocking gate closes, **P0-G10 included**.

---

## 12. What this revision does NOT do

Recorded plainly, because a patch that silently drops half its action register is exactly the
failure mode these four reviews have been correcting.

**Implemented in this revision (Phase A of the review's §9):** GOV-01 … GOV-06, REC-01 … REC-05,
DOC-01, SEQ-01's split, and the adversarial probe suite.

**Accepted but NOT implemented — these block P0-G0, and therefore block every scientific gate:**

| id | outstanding work |
|---|---|
| PRO-01, PRO-02, SCI-01 | P0-G8's `κ` domain, threshold formulas, verified error intervals, global-topology algorithm, response-shoulder threshold family, and the derivation extending the limit beyond one centre condition |
| PRO-03, SCI-02 | P0-G6's exact RSI formula, weight convention, design list, `κ` locations, profile-width definition, censoring rule, named concordance statistic, minimum effect, and both controls |
| PRO-04 | P0-G9's map families, scored-condition exclusion unit *including upstream fitted polynomials*, adaptation counts, placements, and the impossibility criterion |
| PRO-05, PRO-06 | P0-G5's regularisation coordinate, objective scaling, tuning branch, dominance definition, and envelope construction |
| PRO-07 | P0-G7's generator, true parameter grid, noise covariance, mismatch magnitudes, resource-cost vector, replicates and success criterion |
| PRO-08 | P0-G4's enumerated factorial and expected run count |
| TAX-01, LED-01, LED-02 | splitting `robustness` into evidence basis / validation provenance / result behaviour / assurance / claim status; separating falsifier from scope-limiter; binding every claim to path + JSON pointer + hashes |
| SCI-03, SCI-04 | map-uncertainty propagation; branch-specific H4 text generated from the gate outcome |

Each requires scientific specification rather than control repair, and several are load-bearing
choices that could change a result — which is exactly why they must be frozen *before* P0-G0 passes
rather than selected afterwards.

---

## 13. Environment limit

P0-G10 requires indexed databases (Scopus, Web of Science, Engineering Village). They need
subscriptions unavailable here, and MDPI and Royal Society hosts are Cloudflare-blocked from this
network. **P0-G10 cannot be closed in this environment**, and because it blocks drafting, the
programme cannot reach the manuscript without someone with database access completing it. No "first"
or "to our knowledge" phrasing may rest on anything done here.

This is recorded as a limit, not a task. It is the one gate no amount of local work closes.
