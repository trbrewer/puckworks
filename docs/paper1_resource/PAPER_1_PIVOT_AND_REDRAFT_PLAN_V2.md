# Paper 1 — pivot and redraft plan, revision 2

**Prepared:** 1 August 2026
**Supersedes:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN.md` (v1), which is retained for the audit trail but
is **not operative**
**Actions:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md`
**Status:** proposal for review. No manuscript file has been modified, and none will be until the
P0 gates in §7 close.

---

## 0. Disposition of the review

**Every checkable claim in the review was verified against the archives before this revision was
written. All of them hold.** The review is accepted essentially in full; the four findings below are
accepted as *defects in my work*, not as differences of emphasis.

| # | Review finding | Verified? | Disposition |
|---|---|---|---|
| 3.1 | Numerical verification presented as physical verification | yes — v1 says "the saturation is physical", "H1's mechanism is verified", "against truth" | **Accepted.** H1 rescoped; G3 renamed and restated |
| 3.2 | Fold/group unit-of-analysis conflation ("the exception is Arabica caffeine") | yes — the +0.010 pp fold is the one omitting 93.4 °C/6 bar; Arabica caffeine is a *group* result | **Accepted. My error.** Both statements separated; the causal link withdrawn |
| 3.3 | Pooled figures conceal opposite coarse/fine directions | yes — reproduced exactly from the archive (§2) | **Accepted. The most serious finding.** H3 and H4 rewritten |
| 3.4 | H4 is a universal rule the evidence does not support | yes | **Accepted.** H4 replaced |
| 3.5 | det(G) ≠ profiled curvature; "all local information" unqualified | yes — Schur complement is `W·Var_w(s)`, det is `W²·Var_w(s)` | **Accepted.** H2 restated, module docstring to be corrected |
| 3.6 | "Two conditions beat all nine" is false on total information | yes — `corners_2` RSI_total 0.0185 vs `full_grid_9` 0.0340; the grid carries **1.8× more** | **Accepted.** Claim withdrawn |
| 3.7 | Full-fit, fold-median and widened-domain estimands mixed | yes | **Accepted.** Estimand tags adopted |
| 3.8 | "Unbounded", "6 of 6 unidentified", "<0.05 %" overstated | yes — archive says **0.0526 %**, not <0.05 % | **Accepted.** Terminology fixed |
| 3.9 | H3 cannot exclude particle geometry | yes — geometry was frozen, not varied | **Accepted.** Exclusion clause removed |
| 3.10 | Novelty framing must narrow | yes | **Accepted.** G5 remains blocking for title/abstract |
| 4.4 | The prior-bug match is not independent confirmation | yes — same model, data and scoring code | **Accepted.** Recast as a regression cross-check |

### Two defects have been corrected in artefacts already

1. **`PAPER_A_INFORMATION_PARITY.json` carried a wrong causal label.** `M0_to_M2` was described as
   the "combined value of rate recalibration **and target-grind hydraulics**". M0 and M2 both
   receive the target-grind map; the contrast is **rate recalibration alone**. Corrected, and an
   explicit `hydraulic_map_by_arm` field added so the confusion cannot recur. `M0_to_M1` is now
   labelled as confounding two changes rather than isolating either.
2. **The refit archive now emits the coarse/fine disaggregation and a `pooling_warning`**, so the
   pooled figure cannot be read from the artefact without its decomposition.

### The one thing I want to say plainly

v1 contained a drafting rule — *"no pooled number without its disaggregation on the same page"* —
written specifically because the original paper had hidden a coarse/fine reversal behind a pooled
mean for five rounds. **I then built v1's two headline claims on pooled means that hide coarse/fine
reversals.** The rule was correct and I violated it in the document that introduced it. That is the
finding I take most seriously, and §7's P0-G2 is designed so it cannot happen a third time.

---

## 1. What the corrected evidence actually shows

Reproduced from `PAPER_A_ABLATION_REFIT_STABILITY.json`, nine leave-one-condition-out folds:

| contrast | coarse | fine | pooled |
|---|---|---|---|
| **M1 − M2** *(common map vs target map)* | **+1.234** median, [+0.613, +2.190], **9/9 positive** | **−0.037** median, [−0.671, +0.086], **7/9 NEGATIVE** | +0.524, 9/9 positive |
| **M0 − M2** *(freeze rate vs fit it)* | **−0.483** median, [−1.012, −0.155], **9/9 negative** | **+0.155** median, [−0.587, +0.400], **6/9 POSITIVE** | −0.205, 8/9 negative |

Both pooled numbers are means of two opposite results.

- Supplying the **target-grind hydraulic map** helps coarse prediction enormously and slightly
  **hurts** fine prediction.
- **Freezing the rate** helps coarse prediction consistently and mostly **hurts** fine prediction.

The pooled +0.524 pp is not evidence of a uniform hydraulic benefit; it is evidence that a large
stable coarse effect dominates a small opposite fine effect. And the asymmetry is more interesting
than the pooled result: *why is the optimal-grind map so inadequate for coarse targets while the
target-grind map fails to help — and slightly harms — fine targets?* That question is now a first-
class part of the paper rather than a footnote.

---

## 2. Revised hypotheses

Adopted essentially as the review's §5, with the scope boundaries made explicit.

### H1 — model limit and campaign placement

> **Within the declared two-grain extraction model, the matched whole-cup response approaches a
> finite high-transfer limit.** When a calibration profile extends into that plateau, the rate
> multiplier becomes weakly or one-sidedly localised after profiling the extractable-inventory
> level. In this campaign, five of six 10 %-near-optimal rate sets remain **right-censored at
> k = 500**; one is finite.

**Scope boundary, stated in the paper:** the high-transfer limit is a structural property of the
declared model. Whether real espresso occupies that regime is an empirical question this work does
not answer. v1's sentence *"this is a claim about espresso, not about statistics"* is withdrawn.

### H2 — exact local geometry

> For `ŷ_i = I·f_i(k)`, the weighted two-column log-sensitivity Gram determinant is exactly
> `(Σw)²·Var_w(s)`. Under the corresponding local weighted least-squares geometry, profiling the
> level leaves log-rate curvature `Σw·Var_w(s)` — the Schur complement, **not** the determinant.
> The sensitivity spread therefore provides a **local, model-based screen** conditional on the
> nominal rate, the weights, and the observation operator.

Three quantities are now distinguished, and the module docstring's "all local information" is
withdrawn: the determinant `W²Var_w(s)`, the profiled curvature `W·Var_w(s)`, and the per-
observation normalisation `RSI = sqrt(Var_w(s))`. No Fisher-information language, because the
calibration loss is MAPE and no likelihood has been declared.

### H3 — grind-specific hydraulic attribution

> In this campaign, supplying **target-side hydraulic metadata** gives a large, refit-stable
> improvement for **coarse-grind** prediction (+1.234 pp median, 9/9 folds). **Fine-grind effects
> are small and usually opposite** (−0.037 pp median, 7/9 negative). The pooled benefit is
> coarse-driven, not uniform. **Particle geometry and other grind-dependent physics were held
> fixed and were therefore not tested as competing explanations.**

"Not particle geometry" is withdrawn — geometry was frozen, not varied, so it cannot be excluded.
"Transfers" is replaced by "supplied at prediction time": the target flow map is target-side
covariate information, not a learned source quantity carried across.

### H4 — estimation consequence

> When whole-cup data do not localise the rate multiplier, **its fitted value should not be
> interpreted as a learned kinetic quantity.** It should instead be independently constrained,
> regularised, fixed with sensitivity analysis, or propagated over its acceptable profile. In this
> campaign, fixing it at the inherited normalisation improves coarse-grind transfer and is
> competitive pooled, **but is not uniformly superior and generally worsens fine-grind prediction.**

v1's "freeze rather than fit" is withdrawn as a universal rule. The inherited value is a
normalisation from the source model, not an externally validated constant.

### Unifying thesis

> **Whole-cup prediction and kinetic identification are different achievements.** This campaign
> shows how a model can transfer useful composition predictions through target-side hydraulic
> information while its fitted rate multiplier remains weakly localised by the whole-cup
> observation operator.

---

## 3. Corrected statements of fact

Carried here so the corrections are auditable rather than silently absorbed.

| v1 said | corrected |
|---|---|
| "the saturation is physical" | the plateau is a structural property of the declared semi-discrete model and is not a BDF artefact |
| "H1's mechanism is verified" | the high-rate asymptote is verified **within the declared model**; physical generalisation is untested |
| "measure BDF's error against truth" | against the **exact-in-time solution of the same semi-discrete system** |
| "an independent integrator" | an **independent temporal-integration path**; the spatial operator, equations, parameters and omitted physics are shared |
| "the single exception is Arabica caffeine" | *(two separate statements)* across six groups M0 is better in five, the exception being Arabica caffeine; across nine folds the pooled contrast is negative in eight, the positive fold being the one that omits **93.4 °C, 6 bar** |
| "…and why the single exception is…" *(causal)* | **withdrawn** — no fold × group contribution analysis has been run |
| "a tenfold change moves the prediction by <0.05 %" | **≤ 0.053 %** (archived worst case 0.0526 %) |
| "the rate is unbounded above" | the acceptable profile is **right-censored at k = 500**; unboundedness requires the asymptotic objective |
| "6 of 6 groups saturate ⇒ unidentified" | 6/6 show a high-rate model asymptote; **5/6** profiles are right-censored under the 10 % criterion, one is finite |
| "two well-chosen conditions beat all nine" | the two corners have greater spread **per observation**; on total spread the nine-point grid carries **1.8×** more |
| "the endpoint is the strongest lever available" | within the tested prospective perturbations and the declared model, varying the endpoint gives the largest **per-observation** spread **at the nominal rate** |
| "widening the domain moves this to −0.183 pp" | −0.183 pp is a **full-support** contrast; the refit-aware −0.205 pp is a **fold median**. Not like-for-like |
| "two unrelated code paths, same number" | a **regression cross-check** between two rate-free constructions sharing model, data and scoring code |
| "no numerical objection to the redraft remains open" | the **BDF-artefact** objection is retired; physical validity and the estimand issues remain open |
| G2 "PASSED with a caveat" | **FAILED sign stability**; retained at a lower evidential tier |

---

## 4. Evidence hierarchy

Adopting the review's §9. "Near-deterministic" is removed for empirical conclusions.

| tier | claim | basis and caveat |
|---|---|---|
| **A — algebraic** | `det(G) = (Σw)²Var_w(s)`; profiled curvature `Σw·Var_w(s)` | proof under declared coordinates and weights |
| **A — model-structural** | the high-rate plateau exists in the tested semi-discrete model and is not a BDF artefact | exact-in-time temporal reference; same model and discretisation; **not** physical validation |
| **B — refit-stable descriptive** | target-side hydraulic map strongly improves **coarse**-grind prediction | +1.234 pp, 9/9 folds; dependent folds |
| **C — heterogeneous descriptive** | **fine**-grind target-map effect is small and usually opposite | −0.037 pp, 7/9 negative |
| **B/C — practical profile result** | 5 of 6 profiles right-censored at k = 500 under the 10 % criterion | model-, objective-, threshold- and dataset-specific |
| **C — treatment comparison** | fixing k = 1 improves coarse transfer, competitive pooled, worsens fine | needs anchor/regularisation sensitivity (P0-G5) |
| **D — local design screen** | pressure and endpoint variation raise nominal per-observation spread | prospective; k-dependent; budget issue unresolved |
| **D — quarantined oracle** | a target-selected empirical flow form has a numerically similar score | selection on target; supplementary only |
| **E — historical secondary** | the original model-vs-constant advantage | weak refit stability; not a thesis |

---

## 5. What we are not claiming

1. That real espresso reaches local equilibrium before displacement.
2. That the fitted multiplier is a physical kinetic constant.
3. That the shoulder location transfers to other machines, roasts, recipes, or model structures.
4. That whole-cup designs are uninformative in general.
5. That freezing is universally preferable to fitting.
6. That particle geometry has been excluded as a transfer mechanism.
7. That the near-optimal set is mathematically unbounded.
8. Structural non-identifiability — reserved for a proof of exact non-uniqueness.
9. Any "first" or "to our knowledge" claim, until G5 closes.
10. **Symmetrically**: that the advantage is absent, or that fitting is harmful. The P0 acceptance
    criterion still binds and its live risk has reversed direction.

---

## 6. Title

v1's title is withdrawn — it overstated all three of its nouns.

> **When Whole-Cup Espresso Measurements Cannot Localize Extraction Rate: Saturation, Sensitivity
> Geometry, and Hydraulic Attribution**

To be finalised only after G5.

---

## 7. Gates before substantive drafting

The review's §6 sequence is adopted. **All ten P0 gates block the results narrative, title,
abstract and contribution list.** G3 and G4 are *not* sufficient to start drafting — that was v1's
error.

| gate | question | pass criterion | status |
|---|---|---|---|
| **P0-G1** | Are all units of analysis and numerical claims correct? | fold/group separated; 0.053 %; estimand tags; no "unbounded" | **partly done** — §3; needs the machine-readable claim table |
| **P0-G2** | Does each pooled claim survive coarse/fine decomposition? | H3/H4 match direction and magnitude in each grind | **done for the ablations** (§1); must extend to every headline |
| **P0-G3** | Is every saturation claim correctly scoped? | no statement equates exact-in-time integration with physical validation | **partly done** — §2, §3; needs the model-scope table in the manuscript |
| **P0-G4** | Is the refit-aware freeze result robust to the rate cap? | LOCO-WIDE archive, or the cap-robustness claim removed | **open** |
| **P0-G5** | Is the conclusion specific to fixing k = 1? | fixed anchors, regularised, free, profile-propagated | **open** |
| **P0-G6** | Is H2 connected correctly to curvature and RSI? | determinant / Schur complement / RSI distinguished; proposition and proof | **open** |
| **P0-G7** | Do design rankings survive equal-budget and multi-k analysis? | RSI and RSI_total across k; synthetic recovery | **open** |
| **P0-G8** | Where is the shoulder, objectively? | analytical limit; dimensionless transfer/residence group; groups located | **open** |
| **P0-G9** | What exactly enters M0/M1/M2, and how uncertain is it? | information-flow diagram; map-form sensitivity; fine reversal investigated | **open** |
| **P0-G10** | What is genuinely new? | indexed search log; affirmative novelty statement | **open — cannot be done in this environment** |

**Renamed gates.** G3 becomes *"Is the high-rate plateau a BDF artefact or a structural property of
the declared semi-discrete model?"* — **PASSED for the tested model and numerical envelope;
physical generalisation untested.** G4's scope is limited to **full-support** contrasts.

**May proceed in parallel:** model description, data provenance, the exact-factorisation
derivation, and the numerical-methods appendix. **Must wait:** results narrative, title, abstract,
discussion, contribution list.

### Priority among the open gates

1. **P0-G8** (derive the limit, define the shoulder objectively) — it converts H1 from a plotted
   curve into a model result and removes the arbitrary 2/50/500 thresholds. It also supplies the
   dimensionless group that makes the result transferable.
2. **P0-G9** (hydraulic audit) — the fine-grind reversal is currently unexplained, and map error or
   model-form mismatch is the leading candidate. This is now a central scientific question, not a
   robustness check.
3. **P0-G5** (rate-treatment policies) — decides whether H4 says anything beyond "k = 1 happens to
   win here".
4. **P0-G6**, **P0-G7**, **P0-G4**, then **P0-G1** table, **P0-G10**.

---

## 8. Manuscript structure

Adopting the review's §8. Note the ordering change: the coarse/fine ablation comes **before** any
recommendation about fixing or fitting.

1. Introduction — prediction is not parameter identification
2. Data, model, observation operator, and scope *(including omitted physics and the information-flow
   diagram)*
3. Exact scale–rate sensitivity geometry *(factorisation, determinant, profiled curvature, RSI and
   RSI_total)*
4. High-transfer limit and practical rate localisation *(derived limit, objective shoulder
   definition, profile classification — model-structural and empirical statements kept separate)*
5. Cross-grind ablations — **leading with the coarse/fine decomposition**
6. What follows, and what does not, from weak localisation *(fixed / regularised / free / profile-
   propagated)*
7. Prospective experiments *(equal-budget, multi-k, explicitly model-based)*
8. Discussion
9. Conclusions

The −0.394 pp result goes in a secondary table. It appears in no title, abstract, or contribution
bullet.

---

## 9. Review plan, revised

### 9.1 Premises get evidence matched to their type

v1 required an executable test for every premise. That is wrong for physical premises, which the
repository cannot test — forcing them into a repo test would produce a check that merely restates
the model.

| premise type | appropriate assurance |
|---|---|
| algebraic | proof plus symbolic/numerical sanity check |
| numerical | convergence, alternate path, **patch-effect controls** |
| data/provenance | source reconciliation, transcription check, lineage |
| inferential | estimand clarity, resampling unit, negative controls |
| physical | independent measurement, external literature, or **explicitly flagged unvalidated assumption** |
| novelty | documented indexed search |

A physical premise that cannot be tested is marked **open or scoped**, never forced into a test.

### 9.2 Acceptance and termination

"No defect found" is withdrawn as an acceptance criterion. A round closes when:

1. no unresolved critical or major finding remains in scope;
2. every finding has a documented disposition;
3. the claim–premise–evidence chain is internally consistent;
4. the contribution remains non-trivial and relevant; **and**
5. required changes are verified in the manuscript and artefacts.

Criterion 4 is new and matters: a claim can sit at a low tier and still be irrelevant or non-novel.

### 9.3 Editorial round

v1 forbade scientific comment in R5. Withdrawn. Any reviewer may always flag a factual or scientific
error. The rule prevents reopening **settled preferences**, not load-bearing corrections.

### 9.4 R3 acceptance

v1 asked R3 to establish that recommendations are "not artefacts of one machine" — impossible from
one machine. Replaced with: recommendations are explicitly prospective and model-based, claims are
scoped to this machine and campaign, and no cross-machine generalisation is made.

### 9.5 Claim–premise–test matrix

For every headline claim record: exact wording; tier; data and observation unit; calibration and
target information supplied; estimand; resampling unit; model and numerical configuration;
supporting artefact; **alternative explanation**; external-validity boundary; **falsifying result**.

### 9.6 Estimand tags

Every headline number carries one: **FULL-PUB**, **FULL-WIDE**, **LOCO-PUB**, **LOCO-WIDE**,
**NUM-FULL**. No number moves between tags without an explicit like-for-like run.

---

## 10. Risks

| risk | severity | mitigation |
|---|---|---|
| ~~Saturation is a BDF artefact~~ | ~~fatal~~ | **retired** — G3 |
| **Real espresso does not occupy the plateau regime** | **high — bounds H1's reach** | **un-retired.** Scope every statement to the declared model; state the external-validation gap explicitly |
| Fine-grind reversal is unexplained | high | P0-G9; it may be map error, model-form mismatch, or extrapolation |
| H4 reduces to "k = 1 happens to win" | moderate | P0-G5 tests a policy set, not a single anchor |
| Design screen fails under noise or model mismatch | moderate | P0-G7 synthetic recovery |
| Novelty overstated | reputational | P0-G10 blocks title, abstract and contributions |
| One machine, one campaign, two roasts | inherent | H2 is model-general; H1, H3, H4 are scoped to the campaign |

---

## 11. Sequence

1. **P0-G8** — derive the high-transfer limit; define the shoulder; dimensionless group.
2. **P0-G9** — hydraulic information audit and the fine-grind reversal.
3. **P0-G5** — rate-treatment policy comparison.
4. **P0-G6**, **P0-G7** — H2 proposition; RSI stress-test at equal budget and multiple k.
5. **P0-G4** — LOCO-WIDE, or drop the cap-robustness claim.
6. **P0-G1** — machine-readable claim table; **P0-G2** extended to every headline.
7. **P0-G10** — indexed novelty search *(needs database access this environment lacks)*.
8. **R0 → R5**, then drafting per §8.

Parallel-safe work from §7 may begin now. **Nothing in the results narrative begins before step 6.**
