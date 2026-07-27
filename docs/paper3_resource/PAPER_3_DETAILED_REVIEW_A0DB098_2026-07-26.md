# Detailed Review of PAPER 3 — Revision at `a0db098`

## Manuscript and review boundary

**Manuscript:** *Puckworks: an executable, provenance-aware evidence registry for espresso process models*  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Manuscript file:** [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/PAPER_3_PUCKWORKS_DRAFT.md)  
**Current review snapshot:** [`a0db098e0e5e99a1275a11f05676d46036a6c438`](https://github.com/trbrewer/puckworks/commit/a0db098e0e5e99a1275a11f05676d46036a6c438)  
**Previous reviewed snapshot:** [`d9ee264f85b15633f56d540b44066e681979a5fc`](https://github.com/trbrewer/puckworks/commit/d9ee264f85b15633f56d540b44066e681979a5fc)  
**Comparison:** [`d9ee264…a0db098`](https://github.com/trbrewer/puckworks/compare/d9ee264f85b15633f56d540b44066e681979a5fc...a0db098e0e5e99a1275a11f05676d46036a6c438)  
**Review date:** 26 July 2026  
**Overall recommendation:** **Major revision before external preprint circulation, formal peer review, or journal submission**  
**Recommended publication genre:** methods/resource article, not a general espresso-physics review and not yet a conventional software paper  
**Confidence:** high for manuscript/source-code consistency, schema, equation, provenance, and reporting findings; moderate for runtime behavior not independently re-executed from a clean archived environment.

This is a new standalone review of the current Paper 3 manuscript. It supersedes my review of the `d9ee264` revision. The manuscript and repository have improved substantially, and several former blockers are now closed. The remaining problems are narrower but more fundamental: they concern whether claim-scoped evidence is actually selected rather than merely attached, whether public evidence badges are genuinely derived, whether the new mutation benchmark measures what its reported percentage implies, and whether the manuscript accurately distinguishes averaged-trace reconstruction from shot-level predictive performance.

---

## 1. Executive assessment

Paper 3 is now much closer to a publishable methods/resource article. The central thesis is strong, timely, and unusually well demonstrated: **published process models do not become scientifically composable merely because variables share names, units, or mathematical forms; observable meaning, state identity, parameter lineage, evaluation design, and composition assumptions must be represented and tested explicitly.** The manuscript is at its best when it preserves an invalid comparison, a failed composition, an unresolved pressure node, or an unavailable experiment rather than manufacturing a complete-looking end-to-end model.

The revision since `d9ee264` contains genuine scientific and software progress. It corrects the Forchheimer-number equation; expands the registry to 27 components and the manifest to 107 records; removes the strongest-gate ranking from the evidence-graph implementation; adds identified public-claim dependencies and scoped evidence records; generates the named-shot scorecard and figures; unifies the headline composition RMSE values; corrects the shared-porosity sign convention; adds a deliberate defect-injection suite; ingests 57 per-brew flow traces; produces shot-level temporal-ladder results; adds a transitive environment lock and deterministic release archive; and wires the Maille and Roman-Corrochano citations. These are substantial improvements, not editorial rearrangements.

The paper is nevertheless not ready for submission. Its main remaining blockers are now concentrated in the architecture claimed as the contribution:

1. **Evidence records are scoped but not claim-selected.** Every evidence record attached to a component is copied into a public claim or scorecard stage, whether or not it matches that claim’s observable, domain, dataset, or configuration. Scope labels survive, but no executable selector prevents unrelated evidence from being presented as part of the claim’s support profile.
2. **The manuscript says public badges are derived and never authored, but the public claim schema requires authors to supply them.** Validation only checks that the supplied badge belongs to a four-item vocabulary.
3. **The evidence-ordering account is self-contradictory.** One paragraph still says a conservative relation ordering remains and scoped evidence is an open design decision; the next section says all ordering has been removed and scoped vectors are implemented. Tests deliberately preserve both assertions.
4. **The claim-ownership table says the named-shot scorecard is hand-maintained with no producer, while the repository now generates and CI-checks it.** This is exactly the kind of provenance drift the paper claims to prevent.
5. **The manuscript alternates between contract schema versions 0.6 and 0.7, and its state-carrier table omits the new fines-provenance fields that motivated the version bump.**
6. **The headline temporal and composition RMSEs are scores against a preprocessed mean trace, not shot-level prediction errors.** New shot-level results materially change the absolute errors and weaken the “near-flexible-floor” interpretation, but the manuscript has not incorporated them.
7. **The reported 67% guardrail “detection rate” is not a defensible coverage estimate.** One of the 18 entries is a valid control rather than a defect, several misses are hard-coded outcomes rather than end-to-end mutations, and structurally dependent cases are counted as independent defects.
8. **The pressure-node defect analysis rests on a false premise.** `MachineState` already contains named pressure-node fields; the actual gap is that legacy recorded traces and adapters do not carry or enforce a structured node identity.
9. **Appendix B overstates coverage and derivation.** It claims every manuscript-facing quantitative result is exportable through the public-claim schema even though many tables, figures, benchmark numbers, and scientific results use separate producers and schemas.
10. **Submission-readiness claims and front matter remain internally inconsistent.** The draft note says figures are not embedded while the figures section says all seven are generated; the readiness table denies a pinned environment despite the new transitive lock; author, contribution, funding, conflict, acknowledgment, DOI, and archival-release fields remain placeholders.

These issues do not invalidate the project. They show that the manuscript’s conceptual architecture has again advanced slightly ahead of the concrete schema and release object. The effective next step is not another broad prose expansion. It is a focused convergence pass: implement claim-specific evidence selection, truly derive badges, make the mutation suite an honest development challenge corpus, integrate the per-shot analysis, generate the ownership and contract tables from one source of truth, and then freeze a release candidate.

My recommendation remains **major revision**, with a favorable expectation after those items are completed.

---

## 2. Review scope, method, and limitations

I reviewed the current manuscript at the pinned commit and compared it with the previous review boundary. The audit covered:

- the full Paper 3 manuscript and its changes since `d9ee264`;
- the component registry, generated component/manifest counts, and contract schema;
- the Paper 3 evidence graph and component evidence-vector construction;
- the outward `PublicClaim`, `Dependency`, `ScopedEvidenceRef`, and `Producer` schema;
- seeded public claims and their badge/evidence/dependency construction;
- the generated named-shot scorecard;
- the deliberate defect-injection corpus and its reported summary metrics;
- the claim-ownership documentation;
- the temporal-ladder mean-trace and newly ingested per-shot results;
- the shared-porosity composition and Forchheimer diagnostic;
- figure, release, citation, and readiness statements; and
- the status of all major findings in the previous review.

I inspected the relevant source files and generated artifacts directly at the pinned repository state. I also examined the merged change history through PRs #186–#188. The repository reports a full suite of 1,848 passing tests and one skipped test for the principal revision merged in PR #186, with 65 passing registry gates and one acknowledged exception. I did **not** independently clone and execute the complete suite from a clean archived environment in this review runtime. Accordingly, code-structure, manuscript, schema, equation, and static consistency findings are direct findings; repository-reported runtime/test results should still be independently reproduced for the final release.

### 2.1 Snapshot metrics

| Metric | Previous reviewed snapshot `d9ee264` | Current snapshot `a0db098` | Change |
|---|---:|---:|---:|
| Physical lines | 712 | 1,109 | +397 |
| Whitespace-delimited words | 12,973 | 19,296 | +6,323 |
| Bytes | 93,844 | 135,292 | +41,448 |
| SHA-256 | `273a5af2774907e7dd915298b4f5f14fcc7d011c4f1c194635a52af06db3fa62` | `5b1660cf117acb205df19a625ae6f3c3a0d7664b7b3934cc5b5ed12789361f9a` | changed |

The revision is large. It adds architecture-status and claim-ownership tables, evidence-vector machinery, a framework-evaluation section, generated figure documentation, more detailed limitations/readiness material, expanded appendices, and new scientific analyses. The added volume is mostly substantive, but it has also created duplicate and contradictory descriptions that now require consolidation.

### 2.2 Main changes since the previous review

| Change | Assessment |
|---|---|
| Forchheimer formula corrected and pinned to implementation | **Resolved former blocker** |
| Registry expanded to 27 components; manifest expanded to 107 rows | Accurate at review boundary |
| Strongest-gate ranking removed; set-membership probe added | Correct direction, but manuscript still contains the old account |
| Scoped component evidence vectors added | Important advance; claim-specific selection remains absent |
| Public claims now identify component/producer/dataset dependencies | Important advance; only one level deep and indiscriminate for component evidence |
| Named-shot scorecard generated from producers | Major improvement; claim-ownership prose/tests remain stale |
| Composition numbers unified and sign convention corrected | Resolved former blockers |
| Defect-injection corpus added | Valuable evaluation start; percentage and corpus design need reframing |
| 57 per-brew flow traces ingested and verified against published means | Strong scientific/reproducibility advance; manuscript not yet updated |
| Seven figures, source CSVs, and alt text generated | Strong release advance; draft-status prose still says they are not embedded |
| Deterministic archive and transitive lock added | Strong reproducibility advance; readiness table still says no pinned environment |
| Maille and Roman-Corrochano references wired | Resolved; references 7–9 remain explicitly uncited |
| Genre selected as methods/resource article | Appropriate and should now guide compression and emphasis |

---

## 3. Principal strengths of the current revision

### 3.1 The paper’s central scientific argument is clear and defensible

The manuscript now consistently rejects the idea that a single scalar “validation level” can authorize arbitrary reuse. It distinguishes source reproduction, same-data reconstruction, within-campaign holdout, independent comparison, compatibility checks, exploratory synthesis, and proposed experiments. That conceptual separation is the paper’s most important contribution.

### 3.2 The Forchheimer diagnostic is now physically and dimensionally correct

Section 4.4 now uses

\[
Fo_F=\frac{\rho k|q|}{\mu k_I},
\]

with `q` explicitly identified as superficial Darcy velocity and with the implemented momentum law written beside it. The manuscript also states that the earlier expression was a transcription error and that a test now binds prose and implementation. This resolves the most serious equation defect from the prior review.

### 3.3 The failed composition is preserved and better explained

The paper now explains why the extraction-plus-swelling composition becomes identical to the static branch: the selected shared-porosity rule drives the dissolved-mass proxy to its floor throughout the scored interval, so the closure returns its zero-porosity-change limit. This is much more informative than merely saying the RMSE worsened. The discussion also lists multiple possible causes rather than attributing the result solely to a transferred scale parameter.

### 3.4 The repository has become more producer-driven

The registry counts, component appendix, figures, scorecard, source-data exports, and multiple manuscript numbers are now generated and CI-guarded. The withdrawal of the unsupported “approximately 6.6%” ramp effect is exemplary: the project found that no producer emitted the number and removed it rather than reconstructing a justification after the fact.

### 3.5 The new per-brew intake is scientifically valuable

Recovering all 57 individual traces, re-aggregating them to reproduce the published means on all 11,000 pressure–time rows, and then using the shot as the analysis unit is a major improvement. It reveals which conclusions survive averaging and which do not. This is exactly the kind of evidence-sensitive correction the paper advocates.

### 3.6 The mutation suite makes the framework falsifiable

Even though the present summary metric is not yet defensible, adding explicit injected failures is a major methodological step. The paper no longer relies only on selected success stories. It openly records guards that miss plausible errors, including physically wrong but dimensionally valid values and consistently regenerated wrong outputs.

### 3.7 Rights, privacy, and provenance treatment remains unusually candid

The external corpus is correctly described as pseudonymized rather than anonymous; restricted data are not promised as redistributable; source licenses are separated from code licenses; and the paper acknowledges that deterministic regeneration proves freshness and consistency, not scientific correctness. This candor strengthens the resource.

### 3.8 The paper has a plausible publication identity

The decision to present the work as a methods/resource article is correct. The strongest contribution is not the number of espresso models or a complete simulator. It is a practical architecture for executable literature synthesis under semantic incompatibility and heterogeneous evidence.

---

## 4. Publication-blocking comments

## P0-1 — Claim-scoped evidence is attached, but not selected or enforced

This is the most important remaining architectural issue.

The manuscript correctly states that evidence belongs to an observable and domain, not to a component in the abstract. The implementation now stores records of the form `(relation, scope, gate, outcome)`. However, the outward claim and scorecard paths do not select the evidence records that actually support the claim being made.

`component_evidence_vector(component_id)` returns **every** evidence link associated with the component. `_dep()` then copies that complete vector into every public claim that depends on the component. `PublicClaim.evidence_profile()` flattens all copied records into the claim profile. The named-shot scorecard likewise converts every relation found for a selected component into its stage status. No selector matches evidence against the claim’s observable, pressure/temperature/domain, reference dataset, model output, use, or specific configuration.

This is not the old “strongest-gate” laundering defect, because the records are no longer collapsed to one maximum. It is a subtler form of **scope aggregation**: unrelated evidence remains visibly scoped, but its presence inside a claim or stage profile can still imply that it supports that claim. A component with code verification on one output, source-curve reproduction on another, and a compatibility check on a third will contribute all three labels to any public claim that names it. The reader is left to infer which record is load-bearing.

The public `ScopedEvidenceRef` also drops fields that could help filter the evidence: `paper3_use`, support status, source datasets, fit/evaluation relationship, domain, and reference-artifact role. The result is a useful evidence inventory, not yet a claim-support relation.

### Why this matters

The paper’s novelty claim is not merely that evidence records exist. It is that they constrain what may be asserted. That requires an executable link between a claim and the exact evidence records that license the claim’s observable and verb. Carrying every component record into a claim does not provide that constraint.

### Required action

Introduce an explicit claim-evidence selection object, for example:

```python
@dataclass(frozen=True)
class ClaimEvidenceSelection:
    dependency_ref: str
    evidence_link_ids: tuple[str, ...]
    claim_observable: str
    claim_domain: str
    role_in_claim: str
```

Each public claim and each generated scorecard stage should identify the exact `EvidenceLink` IDs it relies upon. CI should then enforce that:

1. every selected link exists and belongs to the declared dependency;
2. its observable and domain match the claim or have an explicit adapter;
3. its support status and outcome permit the verb/badge used;
4. a claim does not silently inherit unselected evidence;
5. an unrelated strong record cannot alter the claim’s public badge or stage status; and
6. a selected record whose source, gate, or scope changes makes the claim fail closed.

Add mutation tests that attach an independent result for the wrong observable, wrong pressure node, wrong campaign, and wrong model output. Each must be rejected rather than merely displayed with a scope label.

### Acceptance criterion

For every manuscript-facing claim, a machine-readable export should answer: **which exact evidence-link IDs support this sentence, why are their observables/domains commensurate with the sentence, and what weaker or unrelated component evidence was deliberately excluded?**

---

## P0-2 — Public badges are authored even though the manuscript says they are derived

Section 5.1 says the public badge is computed deterministically from three authored evidence fields and “is never authored on its own.” Appendix B repeats that outcome, artifact role, and scope are recorded alongside the evidence relation and that the badge is derived.

The implementation does not do this. `PublicClaim` requires a `badge` constructor argument, seeded public claims hard-code values such as `OBSERVED`, `RECONSTRUCTED`, and `EXPLORATORY_SIMULATION`, and `validate()` only checks membership in the four-item badge vocabulary. There is no `derive_badge()` function that computes the badge from selected evidence, outcome, artifact role, or fit/evaluation relation. The Appendix B generator can label the field “derived,” but that declaration does not make it derived.

A second inconsistency is that the manuscript names **artifact/model role** as one of the three authored axes, while the public claim schema has no authoritative top-level field for that axis. `Dependency.role` describes what the dependency contributes to the claim; it is not the role of the comparison reference as measured system, source-published curve, or own fitted output.

### Required action

Either implement the architecture described in the paper or rewrite the paper to describe the current authored badge accurately. Implementation is preferable.

A defensible path is:

1. Add an explicit comparison-reference or artifact-role field to each selected evidence record.
2. Remove `badge` from authored `PublicClaim` inputs, or make it an optional cached value that must equal `derive_badge()`.
3. Define a deterministic, documented derivation table from selected relation(s), outcome, artifact role, fit/evaluation design, and claim type.
4. Fail on ambiguous combinations rather than selecting the most favorable badge.
5. Export the derivation trace so readers can see why a badge was assigned.
6. Test every derivation branch and include negative mutations that attempt to author a stronger badge.

The legacy public relation `negative validation` should be migrated out of the active vocabulary. Although new validation rejects it as a compound relation/outcome, retaining it beside valid relations keeps the conceptual error alive.

### Acceptance criterion

Constructing a public claim without supplying any badge should produce the same badge on every run from its selected evidence records. Supplying or editing a badge manually should be impossible or should fail verification.

---

## P0-3 — Sections 5.1 and 5.2 give mutually exclusive accounts of the implemented evidence architecture

The current manuscript contains a direct contradiction:

- Section 5.1 says the release checker still applies a conservative ordering over evidence relations, that the strongest-gate roll-up can launder scope, and that replacing it with a scoped profile is an **open design decision**.
- Section 5.2 says **there is no ordering anywhere in the implementation**, the strongest-gate check has already been replaced by set membership, and scoped evidence vectors are implemented and enforced.
- Figure 2’s caption repeats that no ordering is used anywhere.

The code agrees with Section 5.2: the rank was removed and `_scope_membership_probe()` uses set membership. However, the source still contains a dangling comment beginning “EVIDENCE_STRENGTHS is authored in DESCENDING strength order” immediately before a comment saying there is no ordering. More concerningly, the test suite reportedly preserves both manuscript statements: one test requires the old “release heuristic/launder” wording while another asserts that ordering has been removed.

This is not a minor stale paragraph. The paper’s central argument depends on whether evidence relations form a scale, and the two descriptions imply different software behavior.

### Required action

1. Delete the obsolete ordering paragraph in §5.1.
2. Replace it with a short historical note, if needed: an earlier implementation used a rank; the current implementation does not.
3. Remove the dangling source comment and all tests requiring the obsolete wording.
4. Add a test that rejects manuscript language claiming a current evidence ordering.
5. Distinguish the implemented component-level set-membership summary from the still-unimplemented **claim-specific selection** identified in P0-1.

### Suggested replacement

> Earlier development versions compared a component’s declared summary relation with an ordered “strongest gate.” That design was removed because the relations answer different questions and do not form one scientific scale. The current component check is set membership: a declared summary relation must be demonstrated by at least one scoped gate or documented as a conservative summary. Claims do not inherit that component summary; they must select the evidence records matching their own observable and domain. Claim-specific selection is the remaining implementation gap.

### Acceptance criterion

A repository-wide search should find no statement that current evidence relations are ranked, strongest, or weakest, except within clearly marked historical discussion or a mutation fixture.

---

## P0-4 — The claim-ownership table falsely states that the scorecard has no producer

The claim-ownership table lists `P3-SCORECARD` with canonical producer “none — hand-maintained,” and the following paragraph emphasizes that this deliberate absence exposes a provenance gap. Elsewhere in the same manuscript, the implementation-status table says the scorecard is generated and gated by `puckworks.paper3.named_shot_scorecard`; Table 6 is labeled generated; and Figure 7 is rendered from `paper3.named_shot_scorecard.scorecard`.

The source module explicitly says it was created because the table had previously been hand-maintained, and now derives statuses from evidence vectors and numbers from named producers. A stale test reportedly still requires the phrase “hand-maintained.” The manuscript therefore preserves a historical defect as though it were current while simultaneously claiming it has been fixed.

There is also a deeper source-of-truth problem. The manuscript says the ownership table is reproduced from `docs/CLAIM_OWNERSHIP.md`, but the current document does not contain the same columns or full rows. The manuscript table is a separate hand-maintained structure that can drift from the document it claims to reproduce.

### Required action

1. Change the canonical producer for `P3-SCORECARD` to `puckworks.paper3.named_shot_scorecard.scorecard`.
2. Distinguish the **declared configuration**—stage chain and component selection—from the **generated claims**—status, evidence records, and numerical diagnostics.
3. Remove the stale “none/hand-maintained” paragraph and test.
4. Create one structured claim-ownership registry, preferably YAML/JSON/Python data, from which both `CLAIM_OWNERSHIP.md` and the manuscript table are generated.
5. Include claim ID, owning paper, role in Paper 3, producer, figure/table, selected evidence IDs, dataset IDs, release status, and permitted reuse.

### Acceptance criterion

Editing the ownership record in one source should regenerate both the repository document and the manuscript table; manual divergence should fail CI.

---

## P0-5 — Contract schema version and state-carrier descriptions are inconsistent

Section 4.1 says the current contract schema is version **0.6**. Table 7 says the public API is at contract schema **0.7**. `puckworks/contracts.py` sets `SCHEMA_VERSION = "0.7"`.

The change to 0.7 is not trivial. `GrindState` now includes:

- `fines_threshold_um`;
- `fines_dispersion_method`; and
- `fines_basis`.

These fields were added specifically to prevent comparison of fines fractions defined by different thresholds, dispersion methods, or bases. Yet Table 2a lists only setting, fines fraction, and particle radii, omitting the new provenance fields. The manuscript therefore understates one of its best examples of semantic contract improvement.

### Required action

1. Use version 0.7 consistently throughout the manuscript, appendix, release metadata, and examples.
2. Generate Table 2a from dataclass field metadata or a structured contract dictionary rather than maintaining it manually.
3. Add the fines threshold, dispersion method, and basis fields explicitly.
4. Explain that these are **declarations, not conversion formulas**: mismatch or missing convention blocks comparison; the registry does not invent an adapter.
5. Clarify all version namespaces: package release, contract schema, registry schema, evidence-graph schema, public-claim schema, and archive format should have distinct names and values.

### Acceptance criterion

A CI test should compare every contract version and table field against the live schema and fail on omissions or mismatched version strings.

---

## P0-6 — Reframe the headline RMSEs as mean-trace reconstruction and integrate the shot-level results

The abstract and §§8–9 report the central temporal/composition comparison as though it were based on one measured 9-bar trace:

- best constant: 0.573 g s⁻¹;
- static branch: 0.648 g s⁻¹;
- imported temporal branch: 0.116 g s⁻¹; and
- flexible cubic: 0.096 g s⁻¹.

These values are scores against the **preprocessed mean of five 9-bar shots** over 15–95 s, not errors on individual shots. The distinction is scientifically important because averaging suppresses shot-to-shot variability that the models were never required to predict.

The newly ingested per-brew data now permit the shot to be used as the analysis unit. For the five 9-bar shots, the repository reports:

| Model/rung | Per-shot RMSE, mean ± SD (g s⁻¹) |
|---|---:|
| Best-in-window constant | 0.580 ± 0.054 |
| Published static `κ(P)` | 0.661 ± 0.100 |
| Poroelastic temporal `Φ(t)` | 0.189 ± 0.061 |
| Flexible cubic | 0.107 ± 0.016 |
| Shot-to-shot scale/noise floor | 0.149 |

The primary ordering is strengthened: the temporal branch beats the best-in-window constant on all five shots. However, the absolute temporal error rises from 0.116 on the average trace to 0.189 on individual shots. The 0.083 g s⁻¹ per-shot temporal-versus-cubic gap lies inside the reported 0.149 g s⁻¹ shot-to-shot scale and is not resolvable with five shots. Thus the former interpretation that the temporal branch “nearly reaches” the flexible floor is not supported at shot level.

This affects more than §8. The 0.648 versus 0.116 composition comparison in the abstract and §9 is also a **mean-trace reconstruction comparison**. It is still valuable, especially because the composition structurally removes the temporal signal, but it is not a shot-prediction result.

### Required action

1. Label every occurrence of 0.573, 0.648, 0.116, and 0.096 as a score on the preprocessed mean 9-bar trace over 15–95 s.
2. Add a per-shot table or figure with the five-shot results and shot as the unit of replication.
3. State two conclusions separately:
   - the temporal-versus-constant ordering survives all five individual shots;
   - the absolute mean-trace RMSE is not shot-level predictive accuracy.
4. Remove or narrow any statement that the temporal branch nearly reaches the cubic/flexibility floor.
5. Interpret differences relative to the 0.149 g s⁻¹ shot-to-shot scale.
6. Report paired per-shot differences and a suitably cautious interval or permutation/bootstrap summary, explicitly noting `n=5`.
7. Add a producer-backed Paper 3 claim record for the per-shot result, rather than leaving it only in a pull-request narrative or a companion analysis.
8. Clarify why a fully held-out temporal prediction remains blocked: the TDS replicates used to construct `Φ(t)` are not shot-matched to the five flow traces.

### Acceptance criterion

No reader should be able to interpret a mean-curve reconstruction error as the expected error on a future shot. Every table, caption, abstract sentence, and public claim must name the observational unit and preprocessing basis.

---

## P0-7 — Recast the defect benchmark as a development mutation suite, not a 67% coverage estimate

Adding §10 is a major improvement, but the current headline—18 defects, 12 detected, 67%—overstates what the corpus supports.

### 1. One of the 18 entries is not a defect

`D04` is explicitly named `CONTROL: valid SI permeability`. It is a valid-control case proving that the range guard does not reject everything. It is counted as a caught defect in `n_defects`, `n_detected`, class totals, and the detection-rate denominator. If it is removed, the table contains 17 actual defect candidates and 11 catches, or approximately 64.7%. Even that recalculation should not be presented as a general detection rate for the reasons below.

### 2. Several misses are not end-to-end injections

Some nominal mutations simply return `False` or contain a hard-coded `and False`, rather than changing a real repository artifact and asking the current guardrails to process it. Examples include the unenforced changelog rule, wrong-producer case, and physically wrong constant. These are useful documented limitations, but they are not equivalent to executable mutations that traverse the production path.

### 3. Cases are not independent

`D01` and `D02` are two scale factors for the same structural failure of a broad range guard. Several prose and provenance cases likewise share mechanisms. Counting each row equally gives an impression of sample size and coverage that the corpus design does not justify.

### 4. The corpus is constructed from known failures

The suite is deliberately drawn from errors already encountered or discussed by the project. That is excellent for regression protection but creates selection bias. There is no held-out challenge set, independent authoring, severity weighting, or sampling frame from which a coverage probability could be estimated.

### 5. Specificity is not reported

A valid control is present but mixed into the defect denominator. A guardrail framework also needs to show that it does not block scientifically valid inputs. Sensitivity to mutations and specificity on controls should be reported separately.

### 6. Some tests target literal manuscript phrases rather than general architecture

Phrase guards and stale-number checks are valuable regression sentinels, but they should be separated from generic semantic, schema, and provenance guardrails. Otherwise the benchmark risks measuring how well the repository detects the exact examples it was written to detect.

### Required action

Rename the current artifact to **development mutation suite**, **guardrail challenge corpus**, or equivalent. Use a schema such as:

```python
@dataclass(frozen=True)
class MutationCase:
    case_id: str
    family: str
    severity: str
    is_control: bool
    independence_group: str
    injection_target: str
    mutation_fn: Callable
    expected_guard: str | None
    expected_outcome: str
    holdout: bool = False
```

Report:

- true positives among injected defects;
- false negatives by defect family;
- false positives among valid controls;
- results by independent mechanism group;
- which cases are true end-to-end mutations versus documented structural impossibilities;
- severity and scientific consequence;
- held-out challenge-set performance when available; and
- no single “coverage” percentage unless a defensible sampling frame is defined.

Add valid controls for each major guard family. Have a second reviewer or contributor author a blinded/held-out set of mutations after the guards are frozen. Ensure a vacuous benchmark that always returns “caught” fails the controls.

### Suggested manuscript wording

> We maintain a development mutation suite of representative errors and valid controls. It is a regression and gap-discovery tool, not a statistical estimate of all possible failures. In the current suite, the guards catch several representational and provenance defects while deliberately retained misses expose untyped semantics and errors that consistent regeneration cannot detect. Controls are reported separately from defects, and related mutations are grouped by structural cause.

### Acceptance criterion

The benchmark output must distinguish defects from controls and must not call controls “detected defects.” Every counted mutation should actually perturb a production input or artifact and execute the relevant production guard, unless explicitly classified as a non-executable limitation analysis.

---

## P0-8 — Correct the pressure-node diagnosis and test the real interface gap

The manuscript says the pressure-node substitution is undetectable because pressure-node identity “is not a field any contract carries.” Figure 3 and the scorecard repeat a version of this claim. The defect implementation checks whether any `MachineState` field name contains the literal substring `node`, finds none, and concludes that node identity is untyped.

That premise is false. `MachineState` contains explicit fields for:

- pump outlet pressure `p_p`;
- headspace/bed-top pressure `p_h`;
- basket pressure `P_basket`; and
- wet-bed pressure drop `dP_bed`.

The actual weakness is narrower and more useful:

- legacy `P_of_t` and `profile_p` traces carry no structured node identifier;
- the pressure fields are all same-typed Python callables or arrays, so values can still be swapped;
- adapters may accept a generic recorded trace without enforcing which node it represents; and
- one DE1 fixture’s source-node identity remains unresolved.

The current mutation uses a field-name heuristic rather than exercising a real adapter. It therefore reports a miss for the wrong reason.

### Required action

1. Rewrite the manuscript to say node-specific contract slots exist, but generic recorded traces and adapter boundaries do not yet carry or enforce node identity.
2. Replace the field-name heuristic with an end-to-end mutation: pass a basket-pressure trace into an adapter that requires pump pressure, or vice versa, and test whether the adapter rejects it.
3. Add a structured pressure-trace object, for example:

```python
class PressureNode(Enum):
    PUMP_OUTLET = "pump_outlet"
    HEADSPACE = "headspace"
    BASKET_GAUGE = "basket_gauge"
    BED_DROP = "bed_drop"

@dataclass(frozen=True)
class PressureTrace:
    node: PressureNode
    values: np.ndarray
    time_s: np.ndarray
    unit: str
    reference: str
```

4. Require explicit conversion/adaptation between nodes; never infer it from file names or prose.
5. Update Table 2: named fields make a wrong-slot use visible and testable, but Python dataclasses do not statically prevent swapping values of the same type.

### Acceptance criterion

A wrong-node trace presented to a node-specific adapter must fail for a node mismatch, while a valid trace at the correct node must pass. The mutation must exercise this actual boundary rather than inspect field names.

---

## P0-9 — Appendix B overstates both schema semantics and manuscript claim coverage

Appendix B says that every manuscript-facing quantitative claim is exportable as the displayed public-claim record. That is not true at the current snapshot.

The public claim registry appears to contain a small set of public-value claims. Many Paper 3 quantitative statements are produced elsewhere, including:

- component and manifest counts;
- timescale-portability tables;
- composition and temporal-ladder values;
- scorecard statuses and Forchheimer values;
- the 18/12 mutation-suite summary;
- corpus and release counts;
- per-shot results; and
- implementation/readiness tables.

These use separate producers, generated Markdown, or hand-authored manuscript text. They are not all instances of `PublicClaim` and are not all covered by its validation.

The schema example also has several technical problems:

- it labels `badge` as derived even though the constructor requires it;
- it says artifact role is recorded alongside the evidence relation although no authoritative top-level artifact-role field exists;
- it shows the deprecated free-text `components` list rather than authoritative dependencies and selected evidence links;
- the examples are visibly truncated (`primary_caveat` ends mid-word); and
- it claims a universal quantitative-claim rule without providing a coverage audit mapping every sentence/table/figure to a record.

### Required action

Create a manuscript claim manifest with one row per quantitative or testable scientific assertion:

| Field | Purpose |
|---|---|
| `claim_id` | stable identifier |
| `location` | section/table/figure/caption |
| `text_fingerprint` | identifies the rendered assertion |
| `producer` | executable function or generated artifact |
| `result_path` | exact field used |
| `observable_basis` | mean trace, individual shot, source curve, etc. |
| `datasets` | manifest IDs |
| `selected_evidence_links` | exact support records |
| `outcome` | supported/negative/indeterminate |
| `badge` | derived value |
| `release_artifact` | path/hash in frozen archive |

Then either:

- broaden the canonical claim schema so every Paper 3 result uses it; or
- narrow Appendix B’s language to “PublicClaim-managed public-value claims” and document the other generated claim classes separately.

Replace the YAML examples with complete, non-truncated exports showing `dependencies`, selected evidence links, observable basis, outcome, and badge derivation.

### Acceptance criterion

A coverage audit should enumerate every manuscript-facing number and report zero unaccounted items. “Unaccounted” should include values copied from a generated table into prose without a bound producer path.

---

## P0-10 — Reconcile submission-readiness claims, figures, environment, and placeholders

The current draft contains several mutually inconsistent readiness statements:

- The front-matter draft note says demonstration figures are specified but not embedded.
- The figures section says all seven figures are generated, with source CSVs and alt text.
- The readiness table says only unpinned minimum dependencies exist and that a dependency lock is required.
- The merged revision reports that a transitive lock pinned to the producing environment has already been added to the deterministic archive.
- The PR narrative calls the archival DOI the only remaining Paper 3 submission gap.
- The manuscript itself still contains unresolved evidence architecture, quantitative framing, metadata, and governance issues.

The front matter remains a working draft dated 25 July 2026, with author and corresponding-author placeholders. Author contributions, funding, competing interests, and acknowledgments are incomplete. Reference 1 lacks a version, archive DOI, and access date. The main paper links to a moving repository rather than a frozen archival object.

### Required action

1. Update the draft date and explicitly pin the manuscript to a release candidate or commit.
2. Embed the generated figures in the submission manuscript and verify captions against source data.
3. Update the readiness table from generated release metadata, including the actual lock file and its hash.
4. Distinguish what is present in released `v0.3.0` from post-release `dev-main` functionality.
5. Complete authorship, affiliations, corresponding author, CRediT contributions, funding, competing interests, and acknowledgments.
6. Resolve the external-corpus ethics/governance decision before reporting corpus-derived results.
7. Create an archival release and DOI containing the exact manuscript inputs, generated outputs, environment lock, source data, checksums, and license ledger.
8. Arrange one clean-room reproduction by someone outside the originating implementation path, or accurately state that reproducibility remains self-attested.
9. Replace “only remaining submission gap is DOI” with a generated checklist whose status is demonstrably current.

### Acceptance criterion

A reviewer should be able to install the archived artifact, regenerate every Paper 3 table and figure from the lock, verify all hashes, and map the paper to a single immutable release—without relying on `main`, a PR narrative, private files, or author memory.

---

## 5. Major comments requiring revision

## P1-1 — Remove “negative validation” from the manuscript and active public vocabulary

Section 5 correctly says a negative result is an outcome on a relation, not a relation of its own. Section 9.2 nevertheless calls the failed composition “negative validation of that configuration.” The public schema also retains `negative validation` in `EVIDENCE_STRENGTHS` as a legacy compound, even though new validation rejects its use.

Use wording such as:

> The configuration produced a negative outcome on an exploratory-synthesis check.

Migrate old artifacts to separate `relation` and `outcome` fields, then remove the compound term from the active relation vocabulary. A compatibility reader may translate historical records, but new exports should never advertise it as a valid relation.

## P1-2 — Scorecard statuses concatenate all component relations without claim relevance

The generated scorecard is a real improvement, but `_status_for()` gathers every distinct relation in the component vector and joins their lay statuses. The flow-law row consequently displays code verification, compatibility, and source-curve reconstruction together. That is an inventory of the component’s evidence, not necessarily the evidence supporting the named-shot diagnostic.

After implementing P0-1, derive each stage’s status from the selected evidence links for that stage and configuration. A stage may show multiple relations, but each must be explicitly relevant. Preserve unselected evidence in a drill-down appendix rather than the headline status.

## P1-3 — Public claim PV-05 still overdiagnoses a “mis-scale”

The public claim’s uncertainty/sensitivity text reportedly describes a diagnosed mis-scale. The manuscript now correctly lists multiple possible causes: transferred parameters, reference-volume mismatch, fixed-height geometry, initial state, control mode, double counting, normalization, or the composition rule.

Replace causal language with:

> A diagnosed failure of this selected composition; the responsible state mapping, parameter transfer, geometry, boundary condition, or coupling assumption is unresolved.

## P1-4 — The public evidence mapping erases distinctions the manuscript treats as load-bearing

`REGISTRY_TO_PUBLIC` maps both `controlled_independent` and `within_campaign_held_out` to `independent`. It also maps `source_curve_reproduction` and `post_fit_reconstruction` to the same phrase. These many-to-one mappings make the outward label easier to read but erase distinctions that Paper 3 repeatedly argues must constrain scientific verbs.

At minimum, distinguish:

- independent external comparison;
- held out within the same campaign;
- same-data reconstruction; and
- source-curve reproduction.

A public surface may be concise without calling held-out same-campaign evidence “independent.” If coarse labels are retained, never derive a `PREDICTED` badge from the word `independent` alone; use the underlying selected registry relation.

## P1-5 — Outcome derivation in `component_evidence_vector()` is too crude

The code appears to classify a record as negative only when `support_status == "context_only"` and `claim_not_supported` is nonempty; otherwise it marks it supported. This does not cover `unsupported`, `blocked_missing`, `proposed_not_run`, `needs_adjudication`, or genuinely indeterminate records. It may therefore turn unresolved or blocked links into supported outcomes.

Use an explicit, exhaustive mapping from authoritative support/adjudication status to outcome, and fail on unhandled values. Prefer storing outcome directly in the curated evidence link if it is a scientific judgment rather than inferring it from prose fields.

## P1-6 — Two evidence axes share the literal `code_verification`

The evidence graph’s `RELATIONSHIPS` vocabulary and registry `EVIDENCE_STRENGTHS` both contain `code_verification`, despite the manuscript presenting them as distinct semantic axes. This invites accidental comparison and makes field names such as `relationship` and `evidence_strength` difficult to interpret.

Rename the axes to reflect their meanings, for example:

- `comparison_relation`: source reproduction, post-fit reconstruction, held-out transfer, etc.;
- `fit_evaluation_relationship`: same data, same campaign held out, independent external, not empirical; and
- `reference_artifact_role`: measured system, source curve, synthetic fixture, own fit.

Avoid overlapping literals unless they genuinely represent the same concept.

## P1-7 — Generate the claim-ownership map from one structured source

The current `CLAIM_OWNERSHIP.md` and the manuscript table do not share an identical schema. This is a predictable drift source. Create a canonical claim map and generate:

- the repository ownership document;
- the manuscript table;
- companion-paper reuse checks;
- citation/cross-reference checks; and
- the claim coverage manifest.

This would turn claim ownership from policy prose into part of the executable architecture.

## P1-8 — Resolve the citation-audit ambiguity for references 7–9

The latest citation work explicitly records references 7–9 as uncited pending exemptions because their published ports appear only as component IDs. Yet §7.3 contains a numeric range `[6–9]`, which a reader may reasonably interpret as citing all four references.

This reveals either that the citation checker does not expand ranges or that the generic range is not considered a substantive citation. Both possibilities require resolution. Add a clear sentence explaining the relevance of Moroney 2016, Grudeva 2026, and Lee 2023 to the registry, or remove them from the reference list. Citation exemptions should be temporary, explicit, and eliminated before submission.

## P1-9 — Separate architectural mutation tests from manuscript-specific regression sentinels

The defect corpus mixes:

- generic contract/unit/observable mutations;
- evidence-schema mutations;
- producer/provenance mutations;
- manuscript phrase and stale-cross-reference guards; and
- documented process gaps.

All are useful, but they answer different evaluation questions. Report them in separate families:

1. semantic contract enforcement;
2. evidence/claim enforcement;
3. provenance and regeneration;
4. manuscript regression sentinels; and
5. process-policy enforcement.

This will prevent literal phrase guards from being interpreted as general architecture coverage.

## P1-10 — Add dependence-aware uncertainty to the temporal and composition comparisons

The models are compared on the same shots or same averaged trace, so errors are paired and share observation noise. Point RMSEs and separate mean±SD summaries do not quantify uncertainty in model differences.

Report paired shot-level differences for temporal versus constant, temporal versus static, and temporal versus cubic. With only five shots, emphasize effect sizes, all-shot direction, and exact/permutation or bootstrap intervals rather than asymptotic significance. Do not divide the number of time samples into an apparent sample size; the shot is the unit.

## P1-11 — The timescale-portability example is improved but should expose model-selection diagnostics

Section 7.5 now correctly says:

- three Cameron settings are effectively single-exponential-like under the chosen protocol;
- the coarsest returns separated constants of approximately 23.6 and 40.0 s;
- the Roman-Corrochano weight and slow/fast ratio are shape-invariant while absolute times scale with diffusion time; and
- the available Roman calculation covers a 20 µm-radius fine class, not an unpublished coarse class.

This is a strong example. Strengthen it by reporting the fitting window, optimizer/multistart design, parameter bounds, identifiability diagnostics, one- versus two-timescale model-selection criterion, uncertainty, and sensitivity to endpoint normalization. Avoid any summary that calls the entire Cameron model one-regime. Keep the phrase “one physical diffusion process,” which is more accurate than “single diffusion mode.”

## P1-12 — Table 2 overstates what named Python fields catch

The table says named typed fields catch a wrong quantity supplied to the wrong slot. They can make wrong-slot use visible and testable, but same-typed callables, arrays, and floats can still be swapped, especially through positional construction or generic adapters.

Revise the row to:

> Named fields reduce ambiguity and permit field-specific validation; they do not statically prevent a validly typed but semantically wrong value from being assigned.

## P1-13 — Resolve the legacy bar-gauge versus SI pressure callback

`MachineState.P_of_t` and `profile_p` use bar gauge, while explicit node callables use pascals. The manuscript acknowledges this, but it remains a central example of the interface problem. A submission-ready resource should either normalize runtime pressure to SI or require a typed unit wrapper and explicit conversion at ingestion. Leaving the mismatch in the core state carrier weakens the claim that contracts operationalize units.

## P1-14 — Distinguish public availability from independent reproducibility

Five public Colab notebooks and packaged artifacts demonstrate accessibility. They do not establish independent reproduction. The readiness table is commendably candid on this point; keep the distinction clear throughout the paper. “Publicly runnable,” “self-reproduced in CI,” and “independently reproduced by another group” should be separate statuses.

## P1-15 — Keep the external corpus as governance architecture unless results are actually reported

The corpus governance discussion is strong, but the paper should not imply a scientific contribution from data that are unavailable for reviewer inspection and not yet governed by a completed ethics determination. If no corpus-derived statistic is central to Paper 3, retain the section as a governance case and move operational details to the supplement. If statistics are reported, freeze the query, aggregation, attribution, privacy review, and permissible outputs.

## P1-16 — Correct Figure 2’s absolute claim that no ordering is used anywhere

The caption is accurate for the current evidence-graph code but conflicts with §5.1 and stale tests. After P0-3, retain a narrower statement:

> The current evidence-vector and membership implementation does not rank relations.

Avoid “anywhere” unless repository-wide tests prove it across public badge derivation, UI sorting, documentation, and release tooling.

## P1-17 — Narrow the abstract’s claim about evidence-linked outputs

The abstract says claim records link outputs to declared components, datasets, producers, caveats, and evidence labels. It does acknowledge the absence of a transitive closure, which is good. It should also acknowledge that component evidence is currently attached at one level and not yet claim-selected by observable/domain.

Until P0-1 is implemented, use wording such as:

> Claim records identify first-level dependencies and attach their declared evidence records; claim-specific evidence selection and transitive closure remain incomplete.

## P1-18 — Treat component-level `evidence_strength` as navigation metadata, not validation of all outputs

The set-membership probe ensures that some gate demonstrates the component’s declared summary relation, or that a conservative exception is documented. It does not show that the relation applies to every output, transient, condition, or composition produced by the component.

The manuscript should call this field a **declared component summary relation** and prohibit its use as a claim badge. The scoped claim links, not the component summary, should license claim language.

## P1-19 — Remove review-scaffolding labels from production source comments

Source comments such as “Paper 3 review P0-4 option b” and “step 0” are useful during a revision sprint but should not become durable architecture documentation. Replace them with stable design rationale or architecture decision record references. Review IDs are not meaningful to future contributors or external users.

## P1-20 — Freeze test and gate results as release artifacts, not PR prose

The repository reports 1,848 passed tests, one skipped test, 65 passing gates, and one acknowledged exception in the PR discussion. The manuscript should cite a machine-readable release record stored in the frozen archive, with command, environment, timestamp, commit, and hashes. PR descriptions are valuable development history but are not archival scientific evidence.

---

## 6. Cross-schema and manuscript consistency audit

The following matrix summarizes the most important claims about the architecture and the corresponding implementation state.

| Topic | Manuscript claim | Current implementation | Assessment |
|---|---|---|---|
| Evidence relation ordering | §5.1 says conservative ordering remains; §5.2 says no ordering exists | Evidence graph uses set membership; source has a stale “descending strength” fragment | **Contradictory prose; implementation follows §5.2** |
| Scoped component evidence | Every component carries `(relation, scope, gate, outcome)` records | Implemented by `component_evidence_vector()` | **Implemented, with coarse outcome inference** |
| Claim-scoped evidence | Claims use evidence matching their observable/domain | Claims receive every component evidence record; no selector | **Not implemented** |
| Transitive evidence closure | Explicitly not yet emitted | One dependency level only | **Accurately disclosed** |
| Public badge | Derived deterministically; never authored | Required constructor field; only vocabulary-checked | **Not implemented as described** |
| Artifact/model role | One of three authored evidence axes | No authoritative public-claim field; partially implicit in evidence graph/source roles | **Incomplete** |
| Negative result | Outcome, not relation | `outcome` exists, but legacy `negative validation` remains in vocabulary and manuscript | **Partial migration** |
| Public relation mapping | Lay rendering of registry relation | Many-to-one mapping collapses independent/held-out and reproduction/reconstruction | **Potential evidence inflation/ambiguity** |
| Scorecard producer | Claim-ownership table says none/hand-maintained | Generated by `named_shot_scorecard.scorecard` | **Direct contradiction** |
| Scorecard status | Derived from scoped evidence | Derived from all component evidence records, not stage-selected records | **Partially implemented** |
| Contract schema | §4.1 says 0.6; Table 7 says 0.7 | `contracts.py` is 0.7 | **Direct contradiction** |
| Pressure-node typing | Manuscript says nodes stored separately, then says no contract carries identity | Named node fields exist; generic recorded trace lacks structured identity | **Diagnosis needs correction** |
| Every manuscript number producer-bound | Appendix B implies yes | Several producer systems and hand-authored summaries; no universal coverage manifest | **Overstated** |
| Figures | Draft note says specified/not embedded | Seven figures generated with CSV/alt text | **Stale front matter** |
| Environment pinning | Readiness table says no pinned environment | Revision reports transitive lock in archive | **Stale readiness table** |
| Guardrail rate | 18 defects, 12 caught, 67% | 17 defects + 1 control; some rows are non-executable limitation declarations | **Mischaracterized metric** |
| Mean-trace RMSE | Presented as one measured trace | Scores on preprocessed average of five shots | **Observable/unit-of-analysis omission** |
| Shot-level RMSE | Not reported | Producer-backed results exist for five shots | **Important evidence omitted** |

### Conclusion from the audit

The project has moved from a largely aspirational evidence architecture to a genuinely executable one, but the manuscript currently combines three development generations:

1. the former ordered component-summary design;
2. the current scoped component-vector design; and
3. the desired claim-selected evidence design.

The paper should describe these as history, current state, and next requirement respectively—not as simultaneous current behavior. The strongest final article will be one in which the current state is also the desired claim-selected design.

---

## 7. Quantitative and scientific consistency audit

### 7.1 Registry and manifest inventory

| Quantity | Current manuscript | Generated/current repository | Assessment |
|---|---:|---:|---|
| Registered components | 27 | 27 | aligned |
| Runtime components | 12 | 12 | aligned |
| Calibration components | 15 | 15 | aligned |
| Manifest records | 107 | 107 | aligned |
| Registry stages | 8 including empty Observables | 8 | aligned |

The former count drift is resolved. Keep the counts generated and bind the final manuscript to a frozen release rather than `main`.

### 7.2 Forchheimer equation

Current manuscript and implementation now agree:

\[
\nabla p=-\frac{\mu}{k}q-\frac{\rho}{k_I}|q|q,
\qquad
Fo_F=\frac{\rho k|q|}{\mu k_I}.
\]

This is resolved, subject to final regeneration of the named-shot range and explicit input provenance.

### 7.3 Mean-trace versus shot-level temporal results

| Observable basis | Constant | Static | Temporal `Φ(t)` | Cubic | Interpretation |
|---|---:|---:|---:|---:|---|
| Preprocessed mean 9-bar trace, 15–95 s | 0.573 | 0.648 | 0.116 | 0.096 | descriptive reconstruction of an average trace |
| Five individual 9-bar shots, mean ± SD | 0.580 ± 0.054 | 0.661 ± 0.100 | 0.189 ± 0.061 | 0.107 ± 0.016 | shot-level reconstruction; shot is unit |

All values are in g s⁻¹. The reported shot-to-shot scale is 0.149 g s⁻¹.

The correct interpretation is:

- the temporal branch’s superiority to the best constant is not an averaging artifact; it holds for 5/5 shots;
- mean-trace RMSEs are materially lower than individual-shot RMSEs and must not be called shot-prediction accuracy;
- the temporal-versus-cubic difference is not resolved relative to shot-to-shot variability at `n=5`; and
- the temporal trajectory still uses donor/same-campaign information and is not an independent prediction.

### 7.4 Shared-porosity composition

The current three mean-trace values are internally consistent:

- best constant: approximately 0.573 g s⁻¹;
- extraction-only temporal: approximately 0.116 g s⁻¹; and
- extraction-plus-swelling composite/static limit: approximately 0.648 g s⁻¹.

The most important result is structural, not the ratio of errors: under the selected rule, swelling drives the proxy to its floor for the complete scored interval, and the composite becomes the static branch to numerical precision. That claim should be accompanied by the exact reduction/floor tests and a clear statement that it diagnoses the selected composition only.

Avoid the phrase “worsens from 0.116 to 0.648” without saying “on the preprocessed mean 9-bar trace.” Also avoid implying that 0.116 is a parameter-free out-of-sample prediction; the more accurate statement is that no coefficients were refitted directly to that scored flow trace, while same-campaign/donor information remains.

### 7.5 Timescale-portability example

The revised table is much improved. The remaining quantitative presentation should include:

- confidence/identifiability intervals or profile information for the fitted constants and weight;
- one- versus two-timescale model-selection diagnostics for all Cameron settings;
- the exact fit window and endpoint-normalization rule;
- optimizer bounds and multistart strategy;
- Roman-Corrochano radius and diffusion-time formula;
- explicit statement that only a fine class is represented because the coarse-class radius is unavailable; and
- protocol sensitivity for both ratio and absolute constants.

The manuscript should not convert the current protocol-dependent results into universal physical timescales.

### 7.6 Named-shot Forchheimer range

The scorecard’s 0.86 to 5.7 range is described as a spread across two `k_I` closures for the same shot, not a measurement interval. That is correct. The table should provide or link the exact numerical inputs and mark the closure source as extrapolated from ceramics rather than coffee-calibrated. The status should remain a model-derived regime warning, not validation of a non-Darcy correction.

### 7.7 Mutation-suite count

Current rendering:

- entries: 18;
- caught: 12;
- uncaught: 6;
- displayed rate: 0.667.

Correct categorical accounting:

- actual defect candidates: 17;
- valid controls: 1 (`D04`);
- caught defect candidates: apparently 11;
- uncaught defect candidates: 6;
- raw defect sensitivity within this selected corpus: 11/17 ≈ 0.647;
- control specificity cannot be estimated from one control and should not be merged into sensitivity.

The report should not substitute 64.7% for 67% and then retain the same interpretation. The central correction is conceptual: neither number estimates general architecture coverage.

---

## 8. Detailed audit of the deliberate defect-injection suite

### 8.1 What the suite does well

The suite has four important virtues:

1. It records misses rather than only successes.
2. It includes errors from units, observables, evidence, provenance, prose drift, and physical values.
3. It demonstrates the distinction among determinism, freshness, consistency, and correctness.
4. It creates regression fixtures from defects already encountered in project development.

These are strong foundations for a framework-evaluation section.

### 8.2 Case-by-case classification concerns

| Case | Current label | Reviewer classification | Comment |
|---|---|---|---|
| D01/D02 | separate unit defects | one structural family with two scale factors | Count as related variants, not independent evidence |
| D03 | gross unit defect | executable positive mutation | Appropriate |
| D04 | defect/control | valid control | Exclude from defect denominator |
| D05/D06 | observable semantics | executable contract mutations | Strong cases |
| D07–D10 | prose/evidence/provenance | repository-specific regression sentinels | Valuable, but separate from generic architecture tests |
| D11/D12 | numeric/provenance drift | executable consistency mutations | Strong cases |
| D13/D14 | evidence inflation/orphan | evidence-schema mutations | Strong cases, though claim-scope mutation is still missing |
| D15 | evidence promotion without changelog | policy gap declaration | Replace hard-coded miss with a real diff/CI mutation or classify non-executable |
| D16 | wrong physical constant | structural limitation declaration | Useful, but current unrelated permeability call is not the mutation path |
| D17 | wrong producer regenerated consistently | epistemic limitation | Cannot be “caught” by provenance alone; test via independent reference where available |
| D18 | wrong pressure node | flawed mutation implementation | Replace field-name heuristic with real adapter/node mismatch |

### 8.3 Missing high-value mutations

The suite should add mutations directly targeted at the paper’s claimed novelty:

- attach independent evidence for the wrong observable to a claim;
- attach same-campaign evidence but render an “independent” badge;
- attach a negative-outcome record but render a supported claim;
- swap source-curve reproduction and post-fit reconstruction;
- remove the selected evidence link while retaining the component dependency;
- add an unrelated strong gate to a component and test that claim status does not change;
- pass a dataset with the correct units but wrong inventory basis;
- pass the correct pressure unit at the wrong pressure node;
- use the right model with a configuration outside its validity domain;
- regenerate a number from the right producer but wrong preprocessing basis (mean trace versus shot);
- copy a result from a dev-main producer into a released-version claim;
- edit a public badge directly and ensure derivation rejects it;
- omit a load-bearing adapter from dependency closure; and
- change a source manifest row/license after claim generation and require re-verification.

### 8.4 Recommended benchmark design

Use four partitions:

1. **Regression suite:** known historical defects; may be visible to implementers.
2. **Synthetic challenge suite:** systematic variations around each guard family.
3. **Valid controls:** inputs that should pass, including boundary and atypical but valid cases.
4. **Held-out review suite:** mutations authored after the guard implementation is frozen, ideally by another person.

Report results by independent structural family and severity. A useful table would be:

| Guard family | Defect TPs | Defect FNs | Valid controls | False positives | Held-out? | Principal open gap |
|---|---:|---:|---:|---:|---|---|

Do not reduce the framework to one score. The scientifically useful output is the map of which error classes are executable and which remain epistemically or semantically outside the guards.

---

## 9. Review of the scientific demonstrations

## 9.1 Observable and unit linting

### Strengths

- The three saturation concentrations are kept separate rather than averaged.
- Pressure nodes are distinguished conceptually.
- Named-solute masses are not mixed with aggregate TDS without an observation map.
- Raw grinder cells and fitted response-surface objects are separated.
- The two “fast fractions” are shown to share a trend but differ materially in definition and magnitude.

### Required improvements

- Correct the pressure-contract statement as described in P0-8.
- For each incompatibility, provide a machine-readable conflict record with the two observable definitions, units, bases, and reason no adapter is authorized.
- Clearly distinguish “cannot be compared” from “can be compared after an explicit mapping whose uncertainty is propagated.”
- Do not imply that a broad numeric range guard is a unit system.
- Add at least one valid-control comparison showing that compatible observables pass, so refusal is not the only demonstrated behavior.

## 9.2 Null-first temporal-flow workflow

### Strengths

- Capacity, constant, static, temporal, flexible, and held-out rungs are separated.
- Parameter provenance and fit/evaluation design are foregrounded.
- Cross-pressure holdout is correctly labeled within-campaign rather than independent.
- The public narrative avoids treating model complexity as evidence.

### Required improvements

- Integrate the per-shot analysis and state the observational unit.
- Remove the near-flexible-floor claim.
- Provide paired shot-level differences and uncertainty.
- Explain which temporal inputs are donor, same-campaign, measured, fitted, or fixed.
- Keep the physical conclusions owned by the companion temporal paper; Paper 3 should use the ladder primarily to demonstrate evidence-aware comparison architecture.

## 9.3 Fast/slow semantic portability

### Strengths

- Shared functional form is correctly separated from shared mechanism.
- Cameron, Maille, and Roman-Corrochano outputs are not treated as interchangeable constants.
- Non-identifiability and protocol dependence are acknowledged.
- Unpublished coarse-class information is not fabricated.

### Required improvements

- Add model-selection and uncertainty diagnostics.
- Show the radius-squared scaling explicitly.
- Keep the coarsest Cameron result distinct from the three single-exponential-like settings.
- Ensure the evidence record says model-generated/qualitative semantic analysis, not empirical validation.
- Cite each source directly and eliminate pending uncited-reference exemptions.

## 9.4 Failed shared-porosity composition

### Strengths

- Exact neutral-swelling reduction is tested.
- The constant-output mechanism is exposed.
- The negative result is retained rather than tuned away.
- Multiple plausible failure sources are acknowledged.
- The paper states that component validity does not transfer automatically to a new composition.

### Required improvements

- Replace “negative validation” with negative outcome on exploratory synthesis.
- Label all RMSEs as mean-trace reconstruction.
- Add an explicit state/volume/boundary-condition ledger for the two components and their adapter.
- Separate “no coefficients refit to scored flow” from “parameter-free.”
- Add alternative composition controls: additive signed porosity, bounded multiplicative state, variable-height geometry, and a no-double-counting formulation, without using them to tune away the failed baseline.
- State which experiment would distinguish parameter-transfer failure from state-identification failure.

## 9.5 Named-shot scorecard

### Strengths

- The scorecard refuses to manufacture a final cup prediction.
- Open grinder mapping and pressure-node identity are visible.
- The unsupported ramp number has been withdrawn.
- Infiltration is correctly labeled a same-shot compatibility check.
- The Forchheimer range is framed as closure spread, not a measurement range.

### Required improvements

- Correct ownership/provenance status.
- Select evidence specific to each stage rather than concatenate every component relation.
- Change the machine-boundary status to something like “recorded trace; node unresolved” rather than simply “observed.”
- Correct the statement that node identity is absent from every contract.
- Distinguish configuration selection, recorded input, calibrated parameter, generated status, and produced number.
- Export exact evidence-link IDs and producer result paths per row.

---

## 10. Section-by-section review

## Title

The title is strong. “Executable,” “provenance-aware,” and “evidence registry” accurately identify the methodological contribution. Retain “espresso process models,” which keeps the domain clear without implying a complete brewing simulator.

Consider whether “registry” is sufficient for readers unfamiliar with the project. A subtitle could emphasize composition and comparison, for example:

> **Puckworks: an executable, provenance-aware evidence registry for comparing and composing espresso process models**

This is optional; the current title is defensible.

## Front matter and draft-status note

The note is now stale. It says figures are specified but not embedded, while the figures section says they are generated. Replace the long internal-development note with a concise submission-state statement or remove it from the journal manuscript. Internal paths such as `docs/paper3_resource/generated/` belong in a reproducibility appendix or software-availability section, not the first page.

The working date, author names, affiliations, and correspondence details must be completed. Do not circulate a nominal submission draft with these placeholders.

## Abstract

The abstract is conceptually strong but overfull. It currently tries to summarize the architecture, limitations, inventory counts, all three demonstrations, the scorecard, and the general contribution in one dense paragraph.

Required corrections:

- identify the 0.116 and 0.648 g s⁻¹ values as mean-trace reconstruction scores;
- incorporate the shot-level temporal-versus-constant result or avoid implying shot-level performance;
- state that evidence dependencies are first-level and not yet claim-selected by observable/domain if P0-1 remains open;
- remove any implication that the evidence graph itself fully prevents scope laundering;
- avoid “supported by 107 dataset-manifest records,” which can sound like 107 validation datasets; use “described by 107 provenance-manifest records”; and
- keep the named-shot result framed as an evidentiary ledger, not a model output.

The abstract will improve if reduced to: problem, architecture, one semantic-linting example, one failed-composition example, one framework-evaluation statement, and the methodological contribution.

## Section 1 — Introduction

The introduction is effective and accessible. The list of pressure nodes, concentration meanings, grinder settings, and evidence designs gives concrete motivation without excessive jargon.

Two refinements:

1. The final sentence of paragraph 3 generalizes to several domains. Keep the explicit caveat that only espresso is demonstrated.
2. When stating that public claims carry evidence labels, avoid implying that current claim-level evidence selection is complete.

## Section 2 — Scope and corpus construction

The curated-versus-systematic distinction is excellent. Keep the explicit statement that prevalence/completeness claims are premature.

The generated registry counts are now credible. The claim-ownership subsection, however, is not submission-ready because of the scorecard contradiction and the mismatch between the manuscript table and `CLAIM_OWNERSHIP.md`. Generate this table.

The section may be shortened. Detailed search-protocol requirements can move to Supplement S1. The main paper needs enough to establish that the corpus is curated, how items entered, what is excluded, and what no completeness claim is made.

## Section 3 — Registry architecture

The “configuration is the unit of simulation” framing is strong and should remain prominent. The architecture avoids the common misconception that a registry should instantiate every available component.

The implementation-status table is useful and unusually candid. It should be generated from a capability register and release metadata. Clearly distinguish:

- architectural intent;
- implemented in dev-main;
- present in the cited release;
- publicly demonstrated;
- gated; and
- independently reproduced.

The current table already moves in this direction. The remaining risk is that manually marked checkboxes will become another drift surface.

## Section 4 — Typed contract architecture

This section is central and should become more precise rather than longer.

Required changes:

- correct schema 0.6 to 0.7;
- generate the field inventory;
- include fines-definition provenance;
- correct the pressure-node diagnosis;
- narrow what named dataclass fields “catch”;
- resolve the bar/Pa legacy field; and
- distinguish semantic contracts from dimensional typing.

The Forchheimer paragraph is now correct but overlong. The historical error, test name, symbol disambiguation, and caveat can be compressed in the main text and moved to a reproducibility note. A journal reader needs the equation, variable definitions, velocity convention, and evidentiary interpretation—not the full revision history inside the paragraph.

The fast-fraction and fast/slow examples are valuable but currently blur §4 interface design with §7 demonstration. Consider keeping the concise definitional conflict in §4 and moving all fitted-number detail to §7.5.

## Section 5 — Evidence taxonomy

This is the manuscript’s most important section and currently its least internally coherent.

Rewrite it around four explicit levels:

1. **Evidence record:** relation, outcome, reference artifact, fit/evaluation relationship, observable, domain, source set, gate, and caveat.
2. **Component evidence inventory:** all records attached to a component; useful for navigation but not a claim.
3. **Claim evidence selection:** the subset of records that supports one claim’s observable/domain.
4. **Public presentation:** badge and allowed verb derived from the selected records.

Then state exactly what is implemented. Delete the obsolete conservative-ordering paragraph. Do not call fields orthogonal unless the term is carefully defined; “semantically distinct” is clearer and less likely to be mistaken for statistical independence.

Table 3 is useful. Add columns or an accompanying table for reference-artifact role and fit/evaluation relationship, because relation names alone cannot distinguish all cases.

## Section 6 — Provenance and reproducibility

This section is a major strength. The distinction among determinism, freshness, provenance, and correctness should be retained and perhaps highlighted in a boxed statement.

Required refinements:

- cite a frozen machine-readable release record rather than PR-reported test counts;
- clarify that source cards and manifest records do not themselves establish correctness;
- explain how a claim selects evidence records rather than merely resolving a component;
- separate restricted-source reproducibility from redistributable release reproducibility; and
- keep external corpus privacy and governance concise in the main paper, with operational detail in the supplement.

## Section 7 — Observable linting and semantic portability

This is one of the manuscript’s strongest scientific sections. It shows why a registry is more than packaging.

Required changes:

- directly cite references 7–9 or remove them;
- provide generated conflict-record identifiers for each example;
- add uncertainty/model-selection detail for the fast/slow fits;
- preserve the fine-class limitation for Roman-Corrochano; and
- avoid using a high fit quality as evidence of semantic equivalence.

The section should distinguish three outcomes clearly:

- **compatible:** same observable/domain and adapter verified;
- **comparable with caveat:** explicit mapping exists but introduces uncertainty; and
- **incommensurate:** no defensible mapping is authorized.

## Section 8 — Null-first comparison

Integrate the per-shot results. The mean-trace values can remain because they support the visual/model-ladder demonstration, but they should be subordinate to the shot-level analysis when discussing reproducibility or predictive performance.

The physical inference should remain owned by the companion temporal paper. Paper 3’s primary claim is that the architecture preserves fit design, baseline class, and evidence relation.

## Section 9 — Failed composition

This section is conceptually strong. Keep the exact structural explanation and negative-result preservation.

Required changes:

- label the trace basis;
- replace “negative validation”;
- ensure the public claim does not diagnose a unique mis-scale;
- provide a compact component/adapter contract ledger; and
- identify a discriminating experiment or alternative composition that could resolve the failure source.

## Section 10 — Deliberate defect injection

Rename and redesign as described in P0-7. The section should not present 67% in the opening sentence. Lead with what the suite is for and the categories of caught/missed errors. A revised result might say:

> In a development suite of known and synthetic cases, the current guards reliably catch several representation, provenance, and drift defects. Valid controls and structural misses show that they do not establish physical correctness or complete semantic coverage.

Then report defect/control counts separately.

## Section 11 — Experiment design

The principle is excellent: unresolved model disagreement should produce a measurement recommendation. This section could be strengthened by showing one complete worked chain:

1. surviving models;
2. predictions under candidate interventions;
3. selected observable;
4. expected discrimination;
5. required precision/sample size;
6. preregistered decision rule; and
7. evidence promotion that would follow each outcome.

The current campaign table is useful but should distinguish proposed experiments from funded, in-progress, completed, and evidence-linked experiments.

## Section 12 — Named-shot scorecard

Retain the scorecard, but describe it as a generated evidence ledger for a declared configuration. Correct the source/provenance and pressure-node statements. Stage status should derive from selected evidence links, not all component evidence. Keep the final exact cup open.

## Section 13 — Related work and novelty

The section is now credible and appropriately modest. The comparison with FAIR, PROV, RO-Crate, model cards, datasheets, reproducible practice, and interchange standards is useful.

Consider adding a concise feature matrix with rows such as:

- observable semantics;
- component contracts;
- evidence relation;
- outcome polarity;
- producer-bound claims;
- failed-composition records;
- claim-scoped evidence;
- release-frozen regeneration; and
- model-discriminating experiment outputs.

This would make the joint novelty more concrete than prose alone. Avoid implying that adjacent standards never support these capabilities; phrase the comparison as what Puckworks operationalizes in this domain and workflow.

## Section 14 — Discussion

The discussion is thoughtful. “Composition creates a new model” is a key principle and should remain.

The phrase “labels evidence at the claim level” in the conclusion/discussion should be qualified until claim-specific selection is implemented. The generalization section is appropriately hypothetical.

## Section 15 — Limitations and readiness

The limitations are commendably candid but require current facts. Correct environment-lock and figure status. Add the absence of claim-specific evidence selection and true badge derivation as explicit limitations if they remain unresolved.

The readiness table should be generated. Separate four dimensions:

- scientific-method readiness;
- software/release readiness;
- data/rights readiness; and
- manuscript/editorial readiness.

A DOI is not the only remaining submission gap.

## Conclusions

The conclusion is strong but slightly ahead of implementation when it says the registry labels evidence at claim level and requires all manuscript numbers to be regenerated. Narrow these claims or complete P0-1/P0-9.

The final sentence is excellent:

> Puckworks should not be judged by the number of models it can run, but by whether it prevents an invalid comparison from looking scientifically complete.

Retain it.

## Software and data availability

Replace the moving repository reference with an archived release DOI and exact tag/commit. List which datasets are redistributed, retrieved, restricted, transformed, or represented only by metadata. Include one fully open example requiring no private files.

## Figures

The generated-figure system is a major strength. The final paper should embed the figures rather than list their intended files only. Verify that every data-bearing figure has:

- source CSV;
- producer and result path;
- units;
- observable basis;
- evidence relation/outcome;
- color-accessible rendering;
- text alternative; and
- release hash.

Figure 2 and Figure 7 need semantic corrections from P0-1/P0-3/P0-4. Figures 4 and 5 need mean-trace labels and shot-level context.

## Appendix A

The generated component catalog is appropriate. At submission, use the frozen generated artifact rather than saying the inline copy “will be replaced.” Include the release tag and hash.

## Appendix B

Substantially revise as described in P0-2 and P0-9. The appendix should document the actual canonical schema, not a desired interpretation layered over an authored badge and incomplete coverage. Remove truncated examples.

## References

Complete the archival citation for Puckworks. Directly cite or remove references 7–9. Verify that numeric citation ranges are parsed correctly by the citation audit. Retain the careful redaction note for Maille only if necessary and journal-appropriate; a concise data-access statement may be cleaner.

---

## 11. Line-level and editorial comments

Line numbers below refer to the raw manuscript at `a0db098`; rendered GitHub line positions may differ.

| Approx. line(s) | Comment |
|---:|---|
| 3–7 | Update draft date, authors, correspondence, and stale figure-status note. |
| 11 | Add “preprocessed mean 9-bar trace” before the 0.116→0.648 comparison; consider adding the 5-shot ordering. |
| 11 | “Supported by 107 dataset-manifest records” should not imply 107 independent datasets. |
| 11 | Narrow evidence-graph claim until claim-specific selection is implemented. |
| 33 | Good generated-count statement; pin final count to archived release rather than current source. |
| 146–179 | Generate ownership table; correct `P3-SCORECARD` producer and remove historical hand-maintained claim. |
| 183–185 | “Any quantitative value shared between papers is produced by the same named producer” is too universal unless covered by a cross-paper claim audit. |
| 320–332 | Generate implementation-status table; distinguish released versus dev-main more visibly. |
| 346 | Change contract schema 0.6 to 0.7. |
| 354 | Rephrase named-field protection; fields do not prevent same-typed semantic swaps. |
| 366–376 | Add fines threshold, dispersion method, and basis to `GrindState`. |
| 387 | “Requires an adapter to declare the source node” should be backed by a structured field and test. |
| 389 | Resolve bar-gauge/Pa mismatch before stable release. |
| 401 | Correct equation is now strong; compress revision-history/test-name parenthetical. |
| 409–411 | Maille and Roman citations now correctly wired. |
| 427–436 | Rewrite entire evidence-model account; badge derivation is not implemented and old ordering paragraph is stale. |
| 452 | Exact enum mapping is useful; mention public mapping is coarser and potentially lossy. |
| 465–488 | Replace “claim evidence profile is the union” with claim-selected evidence, not all dependency records. |
| 473–479 | Correct current implementation, but conflicts with lines 436 and tests. |
| 495–498 | “Badges derived” is false in current schema. |
| 620–630 | Stronger than prior draft; add model-selection and uncertainty details. |
| 634–638 | Identify averaged trace; integrate five-shot results. |
| 648 | Identify mean-trace basis. |
| 654 | Replace “negative validation.” |
| 660–716 | Reframe as development mutation suite; separate controls; remove 67% coverage framing. |
| 670 | “18 defects” is false because D04 is a control. |
| 700–705 | Correct pressure-node premise; named fields exist. |
| 714–716 | Good caveat, but percentage still invites coverage interpretation. Prefer no headline rate. |
| 759–776 | Scorecard is generated; ownership section must agree. |
| 765 | Replace “node identity is not a typed contract field” with “legacy trace lacks structured node metadata and same-typed node fields can be swapped.” |
| 768 | Derive status from selected evidence for this diagnostic, not entire component vector. |
| 786–810 | Related-work section is good; consider a compact feature matrix. |
| 854 | Add claim-selection and badge-derivation limitations. |
| 867 | Correct elsewhere to schema 0.7. |
| 875–886 | Reconcile with transitive lock; do not call DOI sole meaningful remaining gap. |
| 900 | Replace moving repository URL with archive DOI/tag. |
| 906–920 | Complete all placeholders. |
| 924 | Contradicts line 7; figures should be embedded in final manuscript. |
| 940 | Remove absolute “no ordering anywhere” until all contradictory prose/tests are fixed. |
| 950 | “Derived from scoped evidence records” should become “derived from claim/stage-selected evidence records.” |
| 1000–1077 | Appendix B needs complete actual exports, not aspirational/truncated examples. |
| 1031 | Badge is not currently derived. |
| 1049/1072 | `components` examples use deprecated field rather than authoritative dependencies. |
| 1051/1074 | Truncated caveats are not publication-ready. |
| 1082 | Complete archive DOI/version/access date. |
| 1088–1090 | Directly cite or remove references 7–9. |

### General editorial comments

- Use “source-curve reproduction,” “same-data reconstruction,” “within-campaign held-out comparison,” and “independent external comparison” consistently.
- Reserve “prediction” for a declared fit/evaluation split and frozen inputs.
- Avoid “validation” without an object: validation of which observable, domain, system, and configuration?
- Distinguish “component,” “configuration,” “composition,” “claim,” “gate,” and “evidence record” consistently.
- Reduce parenthetical revision history in the main text; preserve it in changelog/architecture records.
- Use `g s⁻¹`, `kg m⁻³`, and other units consistently in text, tables, and code exports.
- Avoid all-caps emphasis except controlled badge/status labels.
- Replace internal review IDs and sprint terminology with stable architectural language before submission.

---

## 12. Status of the previous review’s major findings

| Previous issue at `d9ee264` | Current status | Current assessment |
|---|---|---|
| Incorrect Forchheimer-number equation | **Resolved** | Correct formula, velocity convention, and implementation-binding test now stated |
| Evidence schemas incompatible | **Partially resolved** | Identified dependencies and scoped records added; badge/artifact-role/claim selection remain inconsistent |
| Evidence relations ranked by strongest gate | **Implementation resolved; manuscript not resolved** | Rank removed, but stale paragraph/comment/tests remain |
| Composition producer paths disagreed | **Resolved** | Headline mean-trace RMSE values now agree |
| Shared-porosity sign contract inconsistent | **Resolved** | Code/documentation now use a consistent signed convention |
| Failed-composition cause overdiagnosed | **Mostly resolved** | Multiple causes acknowledged; public “mis-scale” language and “negative validation” remain |
| Abstract overstated transitive evidence | **Improved** | One-level limit disclosed; claim-specific selection still absent |
| Framework not directly evaluated | **Partially resolved** | Mutation suite added; design/metric need major revision |
| Readiness table stale | **Improved but still stale** | Packaging/notebooks/CI updated; environment lock and remaining blockers conflict |
| Figures absent | **Producer resolved; manuscript packaging incomplete** | Figures/source CSV/alt text generated; draft says not embedded |
| Missing primary references | **Improved** | Maille/Roman wired; refs 7–9 remain uncited pending exemptions |
| Fast/slow portability overclaimed | **Substantially resolved** | Fine-class, protocol dependence, and Cameron distinctions now present |
| Quantitative uncertainty inadequate | **Evidence produced, manuscript not updated** | Shot-level analysis exists but is omitted from Paper 3 |
| Claim ownership undefined | **Partially resolved** | Ownership table added, but not generated and contains false scorecard row |
| Public claim provenance ambiguous | **Improved** | Generated and last-verified commits separated |
| Appendix schema aspirational | **Still open** | Now generated but still describes derived badge/coverage not implemented |
| Publication genre unclear | **Resolved** | Methods/resource route selected |
| External corpus governance incomplete | **Improved but open** | Responsible pseudonymization/rights framing; ethics determination remains |

### Net assessment of progress

The revision closes several high-risk physics and numerical-consistency issues and adds real evaluation machinery. The overall recommendation remains major revision because the remaining blockers affect the truth of the architecture claims rather than only presentation. However, the direction of travel is clearly positive: the paper has moved from broad architecture description toward an auditable research object.

---

## 13. Recommended canonical evidence and claim architecture

A clean final architecture should avoid trying to make one field serve component navigation, scientific evidence, and public presentation simultaneously.

### 13.1 Canonical evidence record

```python
@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    component_ref: str
    claim_or_gate_ref: str

    # What comparison was made?
    comparison_relation: str
    outcome: str

    # Against what and under what evaluation design?
    reference_artifact_role: str
    fit_evaluation_relationship: str

    # What exactly was tested?
    observable: str
    domain: str
    conditions: dict

    # Provenance
    gate_ref: str
    source_refs: tuple[str, ...]
    fit_dataset_refs: tuple[str, ...]
    evaluation_dataset_refs: tuple[str, ...]
    adapter_refs: tuple[str, ...]

    # Interpretation
    support_status: str
    licensed_verbs: tuple[str, ...]
    caveat: str
```

Important design rules:

- `comparison_relation` and `outcome` are separate.
- `reference_artifact_role` distinguishes measured system, source model curve, synthetic fixture, own fitted data, and proposed experiment.
- `fit_evaluation_relationship` distinguishes same data, same campaign held out, and independent external data.
- observable/domain/conditions are mandatory for reality-facing evidence.
- adapters are first-class dependencies where they define the observation map.
- no ranking is required.

### 13.2 Claim evidence selection

```python
@dataclass(frozen=True)
class ClaimEvidenceSelection:
    dependency_ref: str
    evidence_ids: tuple[str, ...]
    claim_observable: str
    claim_domain: str
    role_in_claim: str
```

A claim should not ingest a whole component evidence vector. It should select the records that license its own assertion.

### 13.3 Canonical claim

```python
@dataclass(frozen=True)
class ScientificClaim:
    claim_id: str
    statement: str
    claim_type: str
    numeric_result: dict
    units: dict
    observable_basis: str

    producer: Producer
    dependencies: tuple[Dependency, ...]
    evidence_selections: tuple[ClaimEvidenceSelection, ...]
    outcome: str

    validity_domain: str
    primary_caveat: str
    generated_from_commit: str
    last_verified_against_commit: str

    @property
    def badge(self) -> str:
        return derive_badge(self)
```

### 13.4 Badge derivation

Do not derive a badge from a single coarsened public relation. Use the selected evidence records and claim type. A conservative example:

- `OBSERVED`: the claim reports a directly measured value and does not attribute it to model prediction.
- `RECONSTRUCTED`: model output is scored on fit data, source-generated curves, or same-campaign information without a qualifying held-out design.
- `PREDICTED`: every load-bearing model dependency has evidence selected for the claim’s observable/domain under a declared held-out or independent evaluation design; no load-bearing adapter is unverified; outcome supported.
- `EXPLORATORY_SIMULATION`: composition or model-generated output without sufficient empirical evaluation for the claim.

Ambiguous combinations should fail rather than receive the strongest compatible badge. The derivation should also return a rationale and the limiting dependency.

### 13.5 Component summary

Retain `component.evidence_strength` only as a curated navigation summary. Rename it if necessary to `declared_summary_relation`. It must not determine claim badges or support all component outputs. Its only enforceable rule should be that it corresponds to at least one scoped evidence record or carries a documented conservative-summary rationale.

### 13.6 Claim coverage

Generate a claim manifest for the paper. Every number, table row, figure annotation, and testable sentence should have a stable claim ID and producer path. This does not mean every sentence needs the public-value `PublicClaim` schema; it means the archive needs one coverage registry across all claim classes.

---

## 14. Prioritized revision plan

## P0 — Complete before the next external manuscript review

### P0.1 Implement claim-specific evidence selection

**Tasks**

- Add stable evidence-link IDs to public and scorecard records.
- Add claim observable/domain and selected evidence IDs.
- Filter scorecard status and public evidence profile through those selections.
- Preserve complete component evidence inventories separately.
- Add wrong-observable, wrong-domain, wrong-dataset, and unrelated-strong-gate mutations.

**Acceptance tests**

- `test_claim_rejects_evidence_for_wrong_observable`
- `test_claim_rejects_evidence_for_wrong_domain`
- `test_unrelated_component_gate_does_not_change_claim_badge`
- `test_scorecard_stage_uses_only_selected_evidence_links`
- `test_selected_evidence_link_must_belong_to_dependency`

### P0.2 Make badges genuinely derived

**Tasks**

- Add reference-artifact role and fit/evaluation relationship to selected evidence.
- Implement `derive_badge()`.
- Remove hard-coded badges from claim constructors or verify cached badges exactly.
- Migrate/remove `negative validation`.

**Acceptance tests**

- `test_public_badge_cannot_be_authored_stronger_than_evidence`
- `test_badge_is_deterministic_from_selected_evidence`
- `test_negative_outcome_does_not_become_evidence_relation`
- `test_ambiguous_badge_derivation_fails_closed`

### P0.3 Remove evidence-ordering contradictions

**Tasks**

- Rewrite §5.1–5.2 as current-state architecture.
- Remove stale source comment and test.
- Add a historical note only if useful.

**Acceptance tests**

- `test_manuscript_does_not_claim_current_relation_ordering`
- `test_evidence_graph_contains_no_rank_map`

### P0.4 Generate claim ownership and contract tables

**Tasks**

- Create a canonical claim ownership data source.
- Generate manuscript and repository tables.
- Correct scorecard producer.
- Generate contract schema/version/field table.

**Acceptance tests**

- `test_claim_ownership_tables_match_canonical_map`
- `test_scorecard_claim_has_live_producer`
- `test_contract_schema_version_matches_manuscript`
- `test_contract_table_lists_all_semantically_required_fields`

### P0.5 Integrate shot-level results

**Tasks**

- Add per-shot producer/claim/table/figure.
- Label mean-trace values everywhere.
- Remove near-flexible-floor claim.
- Add paired shot-level differences and cautious uncertainty.

**Acceptance tests**

- `test_mean_trace_metrics_are_labelled_as_mean_trace`
- `test_per_shot_claim_uses_shot_as_unit`
- `test_temporal_beats_constant_on_all_recorded_9bar_shots`
- `test_cubic_floor_claim_is_not_present_without_support`

### P0.6 Redesign mutation-suite reporting

**Tasks**

- Add `is_control`, independence group, severity, and execution type.
- Exclude controls from defect count.
- Replace hard-coded misses with real mutations or classify them as limitation analyses.
- Add valid controls by guard family.
- Remove headline coverage percentage.

**Acceptance tests**

- `test_controls_are_not_counted_as_defects`
- `test_always_caught_benchmark_fails_valid_controls`
- `test_each_executable_mutation_changes_a_real_input_or_artifact`
- `test_related_mutations_share_an_independence_group`

### P0.7 Correct pressure-node architecture and mutation

**Tasks**

- Add structured pressure trace/node identity.
- Require node-specific adapters.
- Replace D18 heuristic.
- Correct manuscript/table/figure text.

**Acceptance tests**

- `test_wrong_pressure_node_rejected_at_adapter_boundary`
- `test_correct_pressure_node_passes`
- `test_legacy_generic_trace_requires_explicit_node_declaration`

### P0.8 Create a universal manuscript claim coverage audit

**Tasks**

- Map every quantitative assertion to producer/result path/observable basis/evidence selection.
- Generate Appendix B or narrow its scope.
- Remove truncated examples.

**Acceptance tests**

- `test_all_manuscript_numbers_are_accounted_for`
- `test_all_figure_annotations_are_producer_bound`
- `test_all_claim_examples_are_complete_exports`

### P0.9 Reconcile release/readiness statements

**Tasks**

- Update front matter, figures, lock status, schema version, and release/dev-main distinctions.
- Complete all metadata and disclosures.
- Create archival DOI/release candidate.

**Acceptance tests**

- `test_readiness_table_is_generated_from_release_record`
- `test_manuscript_commit_and_archive_commit_match`
- `test_embedded_figures_match_archived_hashes`
- `test_no_submission_placeholders_remain`

## P1 — Complete before journal submission

1. Add model-selection and uncertainty diagnostics to the timescale example.
2. Distinguish public evidence labels rather than mapping held-out same-campaign to “independent.”
3. Normalize or wrap pressure units in the runtime contract.
4. Add an external clean-room reproduction.
5. Resolve references 7–9 and verify citation-range parsing.
6. Add a feature matrix for related work.
7. Move detailed corpus-governance operations to a supplement and complete ethics determination.
8. Remove sprint/review scaffolding from production comments.
9. Store full test/gate/release reports in the archive.
10. Add one end-to-end worked experiment-design example.

## P2 — Editorial and presentation pass

- Compress long parentheticals.
- Reduce the abstract and architecture-history detail.
- Standardize terminology and units.
- Embed all figures and verify accessibility.
- Complete figure/table cross-references.
- Remove moving paths where archived identifiers are available.
- Ensure all examples are complete and non-truncated.
- Copyedit for line length, punctuation, and journal style.

### Recommended order of work

1. Evidence schema and claim selection.
2. Badge derivation and public mapping.
3. Generated claim ownership/contracts/coverage.
4. Shot-level scientific reporting.
5. Mutation-suite redesign.
6. Pressure-node typed interface.
7. Manuscript architecture rewrite.
8. Frozen release and clean-room reproduction.
9. Final editorial/venue conversion.

This order minimizes repeated prose revisions because the manuscript can be regenerated after the underlying architecture is stable.

---

## 15. Suggested replacement passages

### 15.1 Suggested revised abstract

> Published espresso models describe different process stages using incompatible state variables, observable definitions, pressure locations, inventory bases, parameter lineages, and evaluation designs. Matching similarly named quantities can therefore produce numerically plausible but scientifically invalid comparisons and compositions. We present Puckworks, an executable registry that represents literature models as stage-specific components linked by typed state contracts, source and dataset records, scoped evidence links, explicit configurations, and producer-bound scientific claims. The resource is not a monolithic digital twin: a simulation is a declared selection of components and adapters, and a new composition requires its own evidence. In the frozen snapshot, the registry contains 27 components and 107 provenance-manifest records. Worked examples show the architecture refusing incompatible saturation concentrations, pressure nodes, inventory bases, grinder coordinates, and fast/slow parameters. On a preprocessed mean 9-bar trace, an extraction-linked temporal trajectory reconstructs flow with RMSE 0.116 g s⁻¹, whereas adding one imported swelling branch collapses the selected shared-porosity closure to its static limit and gives 0.648 g s⁻¹. Analysis of five individual 9-bar shots preserves the temporal-versus-constant ordering but shows that mean-trace errors are not shot-level predictive errors. A generated named-shot ledger exposes observed, reconstructed, verified, extrapolated, and open stages rather than producing an unsupported final cup. A development mutation suite identifies both caught representational defects and structural misses; it is used as a regression and gap-discovery tool rather than a general coverage estimate. Puckworks demonstrates a methods pattern for executable review of coupled process models: operationalize observable meaning and parameter provenance, select evidence at the claim’s scope, preserve failed compositions and negative outcomes, and convert unresolved disagreement into discriminating experiments.

This version assumes P0-1 has been implemented. If not, change “select evidence at the claim’s scope” to “records scoped component evidence while claim-specific selection remains future work.”

### 15.2 Suggested replacement for §5 evidence architecture

> An evidence record is not a scalar validation level. It records a comparison relation, outcome, reference-artifact role, fit/evaluation relationship, observable, domain, sources, gate, and caveat. These fields answer different questions: whether code was verified, whether a source curve was reproduced, whether data used for fitting were reused for scoring, whether an evaluation condition was held out, whether the reference was a measured system, and whether the declared check supported or contradicted the claim.
>
> A component may have many evidence records on different outputs. The complete component vector is therefore an inventory, not a claim. A manuscript or public claim explicitly selects the evidence-link IDs whose observables and domains match that claim. CI rejects a nonexistent link, a link belonging to another dependency, a scope mismatch without an adapter, or a public verb/badge not licensed by the selected records. Unselected component evidence remains visible in the component card but cannot strengthen the claim.
>
> The relations are not ranked. Earlier development versions used a strongest-gate roll-up; that design was removed because code verification, source reproduction, reconstruction, held-out transfer, and independent comparison answer different questions rather than occupying one universal scale. The current component summary is a conservative navigation field, while claim language is determined only by selected scoped evidence.

### 15.3 Suggested replacement for the badge paragraph

> Public badges are presentation fields derived from the selected evidence records and claim type. Authors do not assign them directly. `OBSERVED` denotes a directly measured result without a model-prediction claim; `RECONSTRUCTED` denotes a same-data or source-curve reconstruction; `PREDICTED` requires a declared held-out or independent evaluation for every load-bearing model and adapter at the claim’s observable/domain; and `EXPLORATORY_SIMULATION` denotes an unevaluated composition or model-generated scenario. Ambiguous or mixed support fails closed and reports the limiting dependency rather than choosing the strongest label.

### 15.4 Suggested replacement for the temporal/composition result

> The values 0.573, 0.648, 0.116, and 0.096 g s⁻¹ are reconstruction errors on the preprocessed mean of five 9-bar traces over 15–95 s. They are not errors on a future shot. When the five individual shots are scored separately, the best constant, static branch, temporal trajectory, and cubic have RMSEs of 0.580±0.054, 0.661±0.100, 0.189±0.061, and 0.107±0.016 g s⁻¹, respectively. The temporal trajectory beats the best-in-window constant on all five shots, so the principal ordering is not created by averaging. However, the temporal-versus-cubic difference is unresolved relative to the 0.149 g s⁻¹ shot-to-shot scale at this sample size. The shared-porosity extraction-plus-swelling composition is evaluated on the mean trace and returns the same 0.648 g s⁻¹ error as the static branch because the selected closure collapses to that branch throughout the interval. This is a negative outcome for the selected composition, not evidence that swelling is absent.

### 15.5 Suggested replacement for the mutation-suite opening

> To evaluate the guardrails beyond selected demonstrations, we maintain a development mutation suite containing executable defects, valid controls, and explicitly classified structural limitations. The suite is a regression and gap-discovery instrument, not a statistical sample of all possible scientific errors. Results are reported separately for injected defects and valid controls and grouped by structural cause. Current guards catch several gross-unit, observable-definition, evidence-inflation, provenance, and manuscript-drift errors. They do not establish physical correctness when a wrong value remains dimensionally plausible or when a wrong producer is regenerated consistently. Those misses identify where independent data, typed semantics, or additional process controls are required.

### 15.6 Suggested replacement for the scorecard ownership text

> The named-shot scorecard is generated by `puckworks.paper3.named_shot_scorecard.scorecard`. The stage chain and selected components are declared configuration choices. Stage evidence statuses are derived from claim-selected evidence links, and numerical diagnostics are executed from named producers. Stages without a registered component retain explicitly declared statuses such as specified, recorded, or open. The generator reports an unbacked number rather than printing it; this mechanism caused the former “approximately 6.6%” ramp claim to be withdrawn when no producer could be found.

### 15.7 Suggested replacement for the readiness conclusion

> The resource is substantially implemented and publicly runnable, but submission readiness requires more than a DOI. The remaining gates are: convergence of the claim/evidence schema with the manuscript; integration of shot-level results; a mutation suite that separates defects from controls; a frozen archive with the exact environment and generated outputs; completed authorship, governance, and data-rights statements; and at least one clean-room reproduction. The final paper will cite one immutable release and regenerate all tables, figures, claims, and readiness statuses from that release.

---

## 16. Recommended final manuscript structure

The current manuscript is comprehensive but can be made more focused. A suggested structure is:

1. **Introduction** — the semantic-composition problem and contribution.
2. **Resource scope and corpus** — curated status, inventory, inclusion method.
3. **Executable registry architecture** — components, configurations, adapters, contracts.
4. **Evidence and claim architecture** — canonical evidence record, claim selection, badge derivation, provenance.
5. **Reproducibility and release object** — producers, claim coverage, deterministic archive, limitations of reproducibility.
6. **Demonstration 1: semantic linting** — concentration, pressure, inventory, grinder, fast fraction/timescale.
7. **Demonstration 2: null-first comparison** — mean and per-shot results, with science attributed to companion paper.
8. **Demonstration 3: failed composition** — reduction, negative outcome, experiment needed.
9. **Framework evaluation** — mutation suite with controls, structural gaps, held-out plan.
10. **Named-shot evidence ledger and experiment design** — end-to-end gap exposure.
11. **Related work and novelty** — concise feature comparison.
12. **Discussion, limitations, and transfer hypothesis**.
13. **Software/data availability and frozen release**.
14. **Conclusions**.

Move detailed capability/readiness tables, full component catalogs, schema dictionaries, corpus governance, mutation case descriptions, and release manifests to supplements. This would shorten the main paper while retaining full auditability.

---

## 17. Reviewer’s overall recommendation

**Recommendation: major revision.**

The manuscript is scientifically and methodologically promising. Its core idea is strong, its negative-result discipline is exemplary, and the repository has advanced substantially since the previous review. The corrected physics, generated artifacts, evidence vectors, scorecard producer, per-shot intake, and mutation suite show a project willing to test its own claims rather than merely document intentions.

The remaining blockers are not reasons to abandon or radically redirect the paper. They are the final convergence problems expected when a methods manuscript is used to audit the software that supports it. The most consequential issue is that scoped evidence is still aggregated at component level rather than selected for each claim. Closely related are the authored badge presented as derived, stale evidence-ordering prose, and the scorecard/claim-ownership contradiction. The scientific reporting must also incorporate the per-shot results and stop presenting mean-trace reconstruction as shot-level accuracy. Finally, the mutation suite should be framed as a development challenge corpus rather than a 67% coverage estimate.

After those corrections, Paper 3 should be a strong methods/resource article. Its most valuable contribution is not a claim that Puckworks already detects every semantic error. It is a demonstrable architecture—and an unusually honest development record—for making such errors visible, testable, and difficult to publish as complete science.

---

## 18. Source ledger for this review

All repository sources below are pinned to the reviewed commit unless otherwise noted.

### Manuscript and revision state

- [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/PAPER_3_PUCKWORKS_DRAFT.md)
- [Current commit `a0db098`](https://github.com/trbrewer/puckworks/commit/a0db098e0e5e99a1275a11f05676d46036a6c438)
- [Comparison from previous review boundary](https://github.com/trbrewer/puckworks/compare/d9ee264f85b15633f56d540b44066e681979a5fc...a0db098e0e5e99a1275a11f05676d46036a6c438)
- [PR #186: principal Paper 1/2/3 revision and frozen-release work](https://github.com/trbrewer/puckworks/pull/186)

### Evidence and public claims

- [`puckworks/paper3/evidence_graph.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/paper3/evidence_graph.py)
- [`puckworks/public/schema.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/public/schema.py)
- [`puckworks/public/claims.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/public/claims.py)
- [`puckworks/paper3/EVIDENCE_LINKS.json`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/paper3/EVIDENCE_LINKS.json)

### Contracts, scorecard, and claim ownership

- [`puckworks/contracts.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/contracts.py)
- [`puckworks/paper3/named_shot_scorecard.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/paper3/named_shot_scorecard.py)
- [`docs/CLAIM_OWNERSHIP.md`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/CLAIM_OWNERSHIP.md)

### Framework evaluation

- [`puckworks/paper3/defect_injection.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/paper3/defect_injection.py)

### Scientific producers and release evidence

- [`puckworks/models/brewer2026/coupled_kappa_t.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/models/brewer2026/coupled_kappa_t.py)
- [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/harness.py)
- [`puckworks/paper3/archive.py`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/paper3/archive.py)
- [`REPRODUCIBILITY.md`](https://github.com/trbrewer/puckworks/blob/a0db098e0e5e99a1275a11f05676d46036a6c438/REPRODUCIBILITY.md)

---

## Final disposition in one sentence

**Paper 3 has become a strong, potentially publishable methods/resource manuscript, but it should not be submitted until claim-specific evidence selection, true badge derivation, shot-level reporting, honest mutation-suite accounting, and a single frozen claim/release source of truth are implemented and reflected consistently throughout the paper.**
