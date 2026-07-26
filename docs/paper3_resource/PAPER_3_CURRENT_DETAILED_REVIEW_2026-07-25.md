# Detailed Review of PAPER 3 — Current Repository Revision

## Manuscript and review boundary

**Manuscript:** *Puckworks: an executable, provenance-aware evidence registry for espresso process models*  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Manuscript file:** [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/PAPER_3_PUCKWORKS_DRAFT.md)  
**Current review snapshot:** [`d9ee264f85b15633f56d540b44066e681979a5fc`](https://github.com/trbrewer/puckworks/commit/d9ee264f85b15633f56d540b44066e681979a5fc)  
**Previous reviewed snapshot:** [`b8c84be3170dc644ef5d15036e9698214896842f`](https://github.com/trbrewer/puckworks/commit/b8c84be3170dc644ef5d15036e9698214896842f)  
**Comparison:** [`b8c84be…d9ee264`](https://github.com/trbrewer/puckworks/compare/b8c84be3170dc644ef5d15036e9698214896842f...d9ee264f85b15633f56d540b44066e681979a5fc)  
**Review date:** 25 July 2026  
**Overall recommendation:** **Major revision before preprint circulation or journal submission**  
**Confidence:** High for the cross-document, source-code, equation, provenance, and manuscript-consistency findings; moderate for runtime behavior that was not re-executed from a complete clean checkout.

This is a standalone review of the current manuscript and supersedes my two earlier Paper 3 reviews. It records what the recent revision has genuinely fixed, identifies remaining and newly exposed problems, and proposes an ordered path to a submission-ready paper.

---

## 1. Executive assessment

Paper 3 has improved substantially. The revised manuscript is more accurate about the registry inventory, clearer about execution role versus provenance, more disciplined about evidence language, better positioned against adjacent work, more cautious about cross-domain generalization, and considerably more responsible in its treatment of the external community corpus. The revision also turns the fast/slow-timescale discussion into a much more useful worked example of semantic non-portability. These are not cosmetic changes; they strengthen the central scholarly argument.

The paper’s core contribution remains strong and publishable: **published process models cannot be compared or composed safely merely because their variables share names, units, or curve forms; observable meaning, parameter lineage, evaluation design, and composition assumptions must be made executable.** Puckworks is unusually good at showing the scientific value of refusing an invalid merge, preserving a failed composition, and distinguishing verification, reconstruction, transfer, and independent comparison.

The manuscript is nevertheless not yet ready for external circulation as a finished research article. The remaining problems are now concentrated in the exact architecture that the paper claims as its novelty:

1. **The Forchheimer-number equation printed in §4.4 is wrong.** It inverts the role of inertial permeability and omits Darcy permeability relative to the implemented momentum law.
2. **The manuscript, component registry, evidence graph, and public-claim API use incompatible evidence schemas.** The paper describes a multi-axis evidence model that the outward claim object cannot encode.
3. **The manuscript says evidence categories do not collapse into an ordered strongest/weakest score, while the evidence-graph implementation explicitly orders them and validates a component against its strongest gate.**
4. **Two nominally authoritative producer paths disagree on the headline composition RMSE values.** The public claim/manuscript reports 0.573, 0.116, and 0.648 g s⁻¹; the generated Paper 3 evidence matrix reports approximately 0.603, 0.113, and 0.650 g s⁻¹.
5. **The shared-porosity composition has a sign-definition inconsistency.** Documentation subtracts a positive swelling-closure term, whereas code returns a negative signed porosity increment and adds it.
6. **The composition narrative over-diagnoses the cause.** The imported swelling parameters are not “parameter-free,” and one failed composition does not isolate parameter scaling from state definition, initial-condition, boundary-condition, observation-operator, or coupling-rule errors.
7. **The abstract overstates transitive per-output evidence provenance.** The current public claim object carries a flat component list and one evidence label rather than the evidence relations of every load-bearing dependency.
8. **The framework itself is still demonstrated through selected examples rather than evaluated systematically.** A methods/resource paper whose central claim is error prevention needs a mutation or error-injection benchmark.
9. **The readiness table is stale relative to the repository.** It understates packaging, public tutorials, CI, contribution documentation, and governance already present, while failing to identify the real remaining blockers.
10. **Figures, final metadata, archival citation, and several primary references remain incomplete.**

These issues are repairable. They do not undermine the underlying project; rather, they show that the manuscript’s conceptual evidence architecture has advanced faster than the implementation and release bundle. The most effective revision is therefore not another prose-only pass. It is a short architecture-convergence cycle: define one canonical evidence object, bind every manuscript number to one result producer, correct the two physics/interface inconsistencies, evaluate the guardrails through deliberate defect injection, and then regenerate the paper and figures from a frozen release.

My recommendation is **major revision**, with the expectation that a strong methods/resource article can emerge after those steps.

---

## 2. Scope and method of this review

I reviewed the current manuscript at the pinned commit above and compared it with the previously reviewed merge snapshot. The audit covered:

- the current Paper 3 manuscript and its diff from the previous review boundary;
- the live registry metadata and generated registry-count artifacts;
- the component-level `evidence_strength` vocabulary;
- the Paper 3 evidence graph and generated priority evidence matrix;
- the public `PublicClaim`/`Producer` schema and seeded claims;
- the PV-05 composition snapshot producer and verification logic;
- the shared-porosity composition implementation;
- the Wadsworth inertial-flow implementation and model card;
- the repository README, package metadata, public-experience paths, and submission-readiness claims; and
- the manuscript’s references, figures, appendices, and internal consistency.

The line references in this review refer to the 712-line manuscript at commit `d9ee264`. I inspected the relevant source and generated artifacts directly. I did **not** rerun the complete repository test suite or every slow scientific producer from a clean cloned environment in this review runtime. Consequently, statements about implementation structure, equations, static outputs, and cross-file consistency are direct findings; statements about what a clean full test run would emit should be confirmed in the release candidate.

### Snapshot metrics

| Metric | Previous reviewed snapshot `b8c84be` | Current snapshot `d9ee264` | Change |
|---|---:|---:|---:|
| Physical lines | 619 | 712 | +93 |
| Whitespace-delimited words | 10,178 | 12,973 | +2,795 |
| Bytes | 73,789 | 93,844 | +20,055 |
| SHA-256 | `fe453e2a9ec4b6379a41c48123b65e3b4a6908c5f54834f4351565ea88b497b3` | `273a5af2774907e7dd915298b4f5f14fcc7d011c4f1c194635a52af06db3fa62` | changed |

The manuscript diff contains approximately 145 added and 52 removed lines, excluding ordinary diff headers. The revision is therefore a material restructuring rather than a narrow edit.

### Main Paper 3 changes since the previous review

| Merge/change | Principal effect | Reviewer assessment |
|---|---|---|
| `81ae291` / PR #176 | Consolidated review findings into the manuscript workstream | Useful coordination step |
| `7681f93` / PR #177 | Corrected registry/manifest counts and bound generated tables to CI | **Substantive improvement; prior count drift resolved** |
| `8172e1b` / PR #178 | Reframed evidence as multiple axes and removed “negative validation” from the manuscript taxonomy | Correct conceptual direction, but implementation remains split |
| `d9840e5` / PR #179 | Added fast/slow-timescale analysis infrastructure | Valuable, but requires stronger identifiability/model-selection reporting |
| `6f56a64` / PR #180 | Added related-work and novelty positioning | Important improvement; still too narrow for the final claim |
| `b67d784` / PR #181 | Expanded §7.5 and condensed the earlier semantic example | Stronger scientific example |
| `bbd949a` / PR #182 | Added contract-scope limits, Forchheimer discussion, and tempered generalization | Mostly constructive; introduced/retained a serious equation error |
| `d9ee264` / PR #185 | Added community-corpus governance and privacy framing | Responsible and unusually candid; publication determinations remain open |

---

## 3. What the revision has now fixed

It is important to distinguish genuine resolution from partial movement. The following earlier defects have been corrected or substantially corrected.

### 3.1 Registry and manifest counts are now aligned

The manuscript now reports 25 registered components, divided into 12 runtime and 13 calibration components, and 104 manifest records. Those figures agree with the generated registry artifacts. The prior 11/13/1 role split and 70-record manifest count have been removed. The paper also correctly describes the manifest as a provenance inventory rather than a count of independent validation datasets.

### 3.2 Execution role is separated from provenance class

The current text correctly explains that `brewer2026.coupled_kappa_t` is a runtime component with `project_synthesis` provenance. “Synthesis” is no longer treated as a third execution role. The manuscript also accurately notes that observational-adapter and diagnostic roles are schema-supported but uninstantiated.

### 3.3 The deprecated `kind` field is no longer the conceptual centre

The architecture description now foregrounds `execution_role`, `provenance_class`, and component-level `evidence_strength`, with `kind` described as deprecated compatibility metadata. This is a substantial improvement over the earlier schema description.

### 3.4 The infiltration evidence has been corrected

The named-shot scorecard no longer presents the infiltration check as an independently gated prediction. It is now framed as a same-shot/same-campaign compatibility result that reuses measured pressure and fitted permeability. That is the scientifically correct language.

### 3.5 The fast/slow discussion is more accurate and useful

The revised §4.5 no longer repeats the strongest overstatements from the previous draft. It names the three models, emphasizes that a shared curve form is not a shared physical contract, acknowledges non-identifiability, and points to a worked analysis. This is now one of the paper’s better conceptual examples, although the statistical reporting still needs strengthening.

### 3.6 Related work and novelty are now explicitly discussed

The manuscript now positions Puckworks relative to FAIR/FAIR4RS, provenance and research objects, model and dataset documentation, reproducible-computing guidance, and interchange standards. It also narrows the novelty claim to joint operationalization rather than claiming invention of the underlying ideas.

### 3.7 Cross-domain generalization has been tempered

The paper now calls the cross-domain extension a proposed transferable pattern demonstrated only in espresso. This resolves the prior overclaim.

### 3.8 External-corpus privacy language is materially better

The manuscript correctly calls persistent hashed-account data **pseudonymized, not anonymized**, limits the corpus to ecological stress testing and operating-envelope analysis, and explicitly keeps ethics/legal determinations open. This is responsible scientific and governance practice.

### 3.9 Generated counts and CI drift guards are a meaningful reproducibility advance

Binding Table 1 and Appendix A to a producer and CI check is exactly the kind of mechanism the paper advocates. The remaining task is to apply the same discipline to every numerical claim, evidence record, and figure—not only the inventory tables.

---

## 4. Publication-blocking comments

## P0-1 — Correct the Forchheimer-number equation and revalidate the scorecard

The manuscript currently defines the inertial-regime indicator as

\[
Fo_F = k_I\,\rho\,|u|/\mu.
\]

That expression is inconsistent with the momentum law implemented by the registered Wadsworth inertial component and documented in its card:

\[
\nabla p = -\frac{\mu}{k}q - \frac{\rho}{k_I}|q|q.
\]

The ratio of inertial to viscous drag from that equation is

\[
Fo_F
= \frac{(\rho/k_I)|q|^2}{(\mu/k)|q|}
= \frac{\rho k |q|}{\mu k_I}.
\]

The manuscript equation therefore both omits Darcy permeability `k` and places inertial permeability `k_I` in the numerator rather than the denominator. This is not a typographic rearrangement. It reverses how the diagnostic changes with the inertial permeability and changes its physical interpretation.

The generated Paper 3 evidence matrix states the correct implemented definition, `rho*k*q/(mu*k_I)`. The reported scorecard range of approximately 0.86–5.7 may therefore have been generated correctly by code while the paper printed the wrong equation. That must be demonstrated rather than assumed.

### Required action

1. Replace the equation in §4.4 with `Fo_F = rho*k*|u|/(mu*k_I)`.
2. Define whether `u`/`q` is superficial or pore velocity and use one symbol consistently across card, code, manuscript, and figure.
3. Add a producer test that compares the manuscript-facing formula with the registered implementation for at least one fixed fixture.
4. Regenerate the named-shot range and record the input `k`, `k_I`, `rho`, `mu`, velocity convention, extrapolation status, and source datasets.
5. Preserve the current caveat: this is a model-derived regime diagnostic using an extrapolated ceramics closure, not empirical validation of inertial espresso flow.

Until this is corrected, the flow-regime argument and its 0.86–5.7 range should not appear in an abstract, conclusion, or scorecard as settled.

---

## P0-2 — Unify the three incompatible evidence vocabularies

The paper’s central architectural claim is evidence typing, but the repository currently has at least three incompatible vocabularies.

### A. Component registry vocabulary

The registry defines nine ordered values:

- `controlled_independent`
- `within_campaign_held_out`
- `post_fit_reconstruction`
- `source_curve_reproduction`
- `code_verification`
- `sign_or_compatibility`
- `qualitative_capacity`
- `exploratory_synthesis`
- `proposed_experiment`

### B. Evidence-graph vocabulary

The evidence graph carries the registry tier plus separate fields such as:

- `relationship`: `independent_external`, `within_campaign_held_out`, `same_campaign_not_held_out`, `post_fit_same_data`, `code_verification`, or `not_empirical`;
- source-level `evidence_role`;
- source-level `independence`;
- `support_status`;
- `adjudication_status`;
- `reality_facing`; and
- `claim_owner`/`paper3_use`.

This is closer to the multi-axis architecture described by the paper.

### C. Public-claim vocabulary

The public schema still accepts one legacy string from:

- `independent`
- `post-fit reconstruction`
- `verification`
- `qualitative`
- `reference`
- `negative validation`

and one badge. `PV-03` still uses `negative validation`, directly contradicting the manuscript’s statement that negative outcome is not an evidence relation.

These are not merely different display labels. They encode different concepts, different cardinalities, and different assumptions about ordering. A public claim cannot currently express the paper’s claimed separation among comparison relation, outcome polarity, reference artifact, fit/evaluation relationship, and public badge.

### Required action

Define one versioned canonical evidence object and make the component registry, evidence graph, public claims, generated manuscript tables, and public site consume it. At minimum, separate:

- **comparison relation**: what comparison was performed;
- **outcome**: pass, fail, mixed, indeterminate, or not run;
- **reference target**: measured system, source-published model curve, analytic result, code identity, synthetic case, or proposed experiment;
- **fit/evaluation relationship**: independent, held out within campaign, same campaign not held out, same data as fit, or not applicable;
- **support/adjudication status**: admissible, context-only, unsupported, blocked, proposed, or pending;
- **scope/domain**: observable, conditions, and validity boundary; and
- **public badge**: a derived presentation field, not an independently authored scientific fact.

Provide a migration for legacy claims, reject `negative validation` as an evidence relation, and add cross-schema tests that fail if any vocabulary drifts.

---

## P0-3 — Replace “four independent axes” with an accurate data model

The manuscript says evidence is recorded along “four independent axes,” but the fourth item—the public badge—is explicitly derived from the first three. It is therefore not independent. Moreover, the implementation does not currently encode all four fields in one object.

The safest formulation is:

> Evidence is represented by three or more orthogonal internal fields, together with a derived public presentation badge.

Even that should be used only after the canonical schema exists. The phrase “independent axes” also risks implying statistical independence, which is not intended.

### Required action

- Replace “four independent axes” with “separate fields” or “orthogonal descriptive dimensions.”
- State which fields are authored and which are derived.
- Define the deterministic badge derivation and test that a badge cannot overstate the underlying relation/outcome/target.
- Do not call the current component-level `evidence_strength` enum the whole evidence object.

---

## P0-4 — Resolve the contradiction between non-ordinal evidence and strongest-gate roll-up

The manuscript correctly argues that code verification, source reproduction, reconstruction, held-out transfer, and independent comparison answer different questions and should not collapse into one scalar score. It explicitly says multiple entries should coexist rather than collapse into a strongest or weakest badge.

The implementation nevertheless treats the registry tuple as **descending strength order**, creates `_STRENGTH_RANK`, and checks whether a component’s declared tier is stronger than the **strongest** tier among its gates. This creates two problems.

First, it contradicts the manuscript’s non-ordinal claim. Second, a strongest-gate roll-up can launder scope: one strong gate on one observable, regime, or output may make a component appear strongly evidenced even though other outputs or domains have only verification or qualitative support.

For example, independent evidence for one scalar output does not automatically validate the component’s other state fields, transient behavior, or use in a new composition.

### Required action

Choose one of two defensible designs:

1. **Vector design:** remove the global strength ordering and store a set of scoped evidence records per component/output/domain; or
2. **Explicit conservative release heuristic:** retain an ordering solely for a narrowly defined release check, rename it as such, document its limitations, and never describe it as the evidence model itself.

My recommendation is the first. A component can expose an **evidence profile** rather than a single tier. Claim-level evidence should select only the records that support that claim’s exact observable and domain.

---

## P0-5 — Reconcile the conflicting composition numbers through one producer

The manuscript, Figure 5 specification, public `PV-05` claim, and packaged public snapshot report approximately:

- constant baseline RMSE: **0.573 g s⁻¹**;
- extraction-only RMSE: **0.116 g s⁻¹**; and
- composite RMSE: **0.648 g s⁻¹**.

The generated Paper 3 evidence matrix reports approximately:

- flat null: **0.603 g s⁻¹**;
- extraction-only: **0.113 g s⁻¹**; and
- composite: **0.650 g s⁻¹**.

The differences are not all rounding differences. In particular, 0.573 versus 0.603 changes the reported composite-over-null ratio and the visual impression of how much the composition loses to the baseline.

The likely cause is architectural: the public claim is producer-bound to one packaged snapshot, while the evidence graph contains separately curated claim prose/numbers. Thus both artifacts can be internally “generated” while disagreeing with one another.

### Required action

1. Designate one quantitative result bundle as the sole source of truth.
2. Make the evidence graph store `producer`, `result_path`, and optional formatting rules—not copied numerical prose.
3. Generate the public claim, manuscript table, figure source data, evidence matrix, website, and abstract values from that bundle.
4. Add a CI test that enumerates all repeated claim IDs and verifies numerical identity within an explicitly declared rounding policy.
5. State the exact baseline definition, window, sample count, missing-value rule, and free-parameter count.
6. Recompute all ratios after choosing the canonical values.

Until this is fixed, the paper should avoid asserting the exact three-value comparison in the abstract.

---

## P0-6 — Make commit provenance mean what readers will think it means

The PV-05 snapshot’s `source_commit` is stamped when exported. Its verifier deliberately rebuilds the payload using the stored commit, so a later repository commit does not make the artifact stale. This preserves byte stability, but it makes `source_commit` ambiguous. A reader may reasonably interpret it as either:

- the commit from which the artifact was generated;
- the commit against which it was most recently verified; or
- the current manuscript/release commit.

Those are different facts. In the current repository, a snapshot can verify successfully on a later commit while still displaying an earlier `source_commit`.

### Required action

Use separate fields:

```yaml
generated_from_commit: <immutable source commit>
last_verified_against_commit: <current verification commit>
producer:
  module: ...
  function: ...
  source_sha256: ...
source_data_sha256: {...}
environment_lock_sha256: ...
schema_version: ...
```

A release should either regenerate the snapshot from the release commit or explicitly record that an unchanged result produced at an earlier commit was reverified at the release commit. The archive manifest should make this lineage unambiguous.

---

## P0-7 — Correct the shared-porosity swelling sign contract

The shared-porosity module documents:

\[
\epsilon(t)=\epsilon_0[1+\Phi_{\mathrm{ext}}-\Phi_{\mathrm{swell}}-\cdots],
\]

and describes swelling as a positive closure magnitude. The implementation’s `_phi_swelling`, however, returns

\[
\Phi_{\mathrm{swell,code}}=\epsilon_b/\epsilon_0-1,
\]

which is negative when swelling closes the pore space. The simulator then **adds** that negative value to the common `phi`. The public presentation text again states the subtractive formula while exposing the signed negative series.

The numerical behavior may be internally consistent, but the interface contract is not. Downstream users cannot know whether `Phi_swelling` means:

- a non-negative closure magnitude that must be subtracted; or
- a signed relative porosity increment that must be added.

This is precisely the kind of semantic ambiguity Paper 3 says typed contracts prevent.

### Required action

Adopt one convention and enforce it everywhere:

- **Magnitude convention:** `phi_swelling_closure >= 0`; compute `epsilon = epsilon0*(1 + phi_extraction - phi_swelling_closure - ...)`; or
- **Signed-increment convention:** `delta_epsilon_swelling_over_epsilon0 <= 0`; compute `epsilon = epsilon0*(1 + delta_extraction + delta_swelling + ...)`.

The signed-increment convention is generally easier to compose, provided names and units are explicit. Add tests for sign, units, monotonic response, exact reduction when the branch is zero, and agreement among code, card, exported JSON, caption, and manuscript equation.

---

## P0-8 — Narrow the causal interpretation of the failed composition

The failed composition is scientifically useful, but the current evidence prose overstates what it diagnoses. The evidence matrix calls the imported swelling branch “parameter-free” and says the result diagnoses that its parameters are mis-scaled. The implementation itself correctly says the parameters are **pre-fitted and not free in this comparison, but not parameter-free**.

More importantly, one failed shared-state mapping cannot identify parameter scaling as the sole cause. Plausible alternatives include:

- a mismatch between fresh-grain and already-swollen initial states;
- fixed-pressure versus the actual rig/control boundary condition;
- a different porosity or reference-volume definition;
- double counting of an already represented volume change;
- an incorrect observation operator from porosity to flow;
- the use of a net shared state where separate internal and intergranular porosities are required;
- an incompatible time origin or wetting history; or
- the additive coupling rule itself.

### Required wording

Replace “parameter-free” with:

> no parameters were refit in this composition test; the branch uses parameters imported from its source configuration.

Replace “diagnoses that the parameters are mis-scaled” with:

> this imported branch is incompatible with the tested shared-state mapping, initial/boundary conditions, and observation operator; the result does not identify which of those assumptions is responsible.

The paper can then propose discriminating experiments or nested alternative compositions to locate the failure.

---

## P0-9 — Bring the abstract back within implemented capability

The abstract says each output carries the provenance and distinct evidence relations of **all** load-bearing components. The current public claim object carries:

- one flat component list;
- one flat dataset list;
- one legacy evidence-strength string; and
- one badge.

That is not a transitive dependency closure or a per-dependency evidence graph. A composition output may depend on model components, adapters, calibration parameters, datasets, transforms, and observation operators with different evidence relations, but the outward claim schema cannot yet represent those distinctions.

### Required action

Either implement and emit a claim dependency DAG/closure, or soften the abstract to something like:

> Claim records link outputs to declared components, datasets, producers, caveats, and evidence labels; the evidence graph records the comparison relations supporting asserted Paper 3 claims.

The stronger “all load-bearing components” statement should return only when completeness is mechanically tested.

The abstract should also avoid exact PV-05 values until the two result paths have been reconciled and should describe the work as a method **demonstrated** in espresso rather than a general method already validated across domains.

---

## P0-10 — Make Appendix B the canonical schema, not an aspirational sketch

Appendix B presents a minimal record containing one `evidence_strength` and one badge. It omits several fields that §6.4 says are load-bearing, including headline, plain-language interpretation, uncertainty/sensitivity, practical implication, and complete provenance. It also fails to encode the multi-axis evidence model introduced in §5.

An appendix advertised as a machine-readable claim record should be generated from the actual schema used by the release—not maintained as parallel prose. At present, it simultaneously understates the public object and overstates its evidence semantics.

### Required action

- Generate Appendix B from a formal JSON Schema, Pydantic model, dataclass schema exporter, or equivalent.
- Include the canonical evidence object proposed above.
- Include producer identity, producer-source hash, source-data hashes, generated/verified commits, schema namespace/version, and dependency links.
- Add an example of both a passing and failed/negative outcome.
- State which fields are mandatory, repeatable, or derived.
- Validate every manuscript claim bundle against this schema in CI.

---

## P0-11 — Evaluate the framework, not only the scientific examples

The paper claims that the architecture prevents invalid comparisons from looking scientifically complete. The demonstrations are persuasive anecdotes, but they do not quantify the framework’s detection capability or burden. The manuscript itself acknowledges that the selected cases are not an estimate of how often semantic errors occur.

For a methods/resource article, the framework should be evaluated directly. A practical route is a mutation benchmark: introduce known defects into a frozen set of components, claims, and artifacts, then record which guardrail detects each defect.

### Minimum defect suite

1. compatible units but wrong observable;
2. pressure-node substitution;
3. grinder-dial transfer without adapter;
4. total-inventory substituted for extractable inventory;
5. zero substituted for missing;
6. sign inversion in a state increment;
7. unit conversion omitted or applied twice;
8. fit and evaluation data mislabeled as independent;
9. source-curve reproduction promoted to external validation;
10. hard-coded manuscript number with no producer;
11. stale generated count;
12. producer result drift while copied evidence prose remains unchanged;
13. source-data hash drift;
14. rights-blocked source included in a release;
15. component with one strong gate overpromoted across unrelated outputs;
16. stale or ambiguous commit provenance.

### Report

- detection rate by layer;
- undetected defects;
- false positives on clean cases;
- time/runtime burden;
- author effort to add a component and claim;
- comparison against simpler baselines such as prose cards only, units only, and producer hashes only; and
- at least one clean-room external reproduction or authoring task.

Without such an evaluation, the paper should frame the architecture as a carefully engineered proposal and demonstration, not as an established general error-prevention method.

---

## P0-12 — Complete the figures, final metadata, and frozen archival object

All seven figures remain specifications rather than embedded reviewable figures. The manuscript also retains placeholders for authors, corresponding author, contributions, funding, competing interests, acknowledgments, archive version/DOI, and companion-paper authorship/citation.

These are not end-stage formatting details because several figures carry the main evidence architecture and quantitative claims. Figure 2 cannot be finalized until the evidence schema is unified; Figure 5 cannot be finalized until PV-05 numbers and sign semantics are reconciled; Figure 7 depends on the corrected Forchheimer calculation and a revised scorecard.

### Required action

Before submission or polished preprint circulation:

- generate all figures from archived source-data bundles;
- include vector and raster versions and accessible alt text;
- add uncertainty/residual panels where appropriate;
- freeze a tagged release and archive DOI;
- replace moving URLs with release permalinks;
- complete all authorship and disclosure fields;
- resolve companion-paper claim ownership; and
- run the manuscript build from a clean release archive, not a working tree.

---

## 5. Major comments requiring revision

## P1-1 — Replace the stale submission-readiness table with an accurate release matrix

Table 7 understates the current repository. It says installation is only an editable-install quickstart, tutorials are internal/referenced, CI separation remains required, and contribution documentation, changelog, and code of conduct remain future governance work. The repository already provides a packaged `v0.3.0` release, wheel/sdist assets, public Colab experiences and a command-line path, a tested Python-version matrix, contribution and conduct documents, a changelog, security guidance, citation metadata, and distinct CI/test workflows. Current development is also clearly marked as `0.4.0.dev0` rather than the public release.

An inaccurate readiness table is especially damaging in a software/resource paper because reviewers may use it to judge maturity.

### Suggested replacement structure

| Area | Released `v0.3.0` | Current `main` / `0.4.0.dev0` | Remaining Paper 3 release requirement |
|---|---|---|---|
| Installation | packaged wheel/sdist and release assets | additional development features | clean install test from the exact archive on declared Python/OS matrix |
| Public use | public Colabs/CLI and guided experiences | expanded workflows | one frozen Paper 3 tutorial with no private files |
| API | documented public paths | evolving development API | identify stable subset and deprecation policy |
| Tests | CI and component gates | added Paper 3 drift/evidence checks | archive slow benchmarks and publish release test report |
| Governance | contribution, conduct, security, changelog, citation files | active issue/PR workflow | no generic gap; focus on release-specific authorship and review |
| Evidence | registry/evidence graph/public claims exist | schemas diverge | canonical schema and migration |
| Reproducibility | producer-backed artifacts and hashes | multiple result paths | one result bundle, lock/container, independent clean-room run |
| Publication | moving manuscript | current draft | figures, metadata, DOI, claim ownership, final rights audit |

This revised table should distinguish what exists from what is stable and archival. “Present” should never mean “available only on `main`,” and “required” should not repeat work already completed.

---

## P1-2 — Correct Table 2’s account of static dimensional typing

The “does not catch” cell for static dimensional typing is shown as an em dash. That implies no residual risk. Dimensional typing cannot detect many of the paper’s central failure modes, including:

- two observables with the same units but different definitions;
- wrong pressure node;
- wrong species or material;
- total versus extractable inventory when units match;
- sign errors;
- wrong reference volume;
- wrong initial condition;
- use outside a model’s validity range; and
- a correct-dimensional but scientifically invalid composition.

This row should be one of the strongest arguments for Puckworks. Fill the residual-risk column explicitly rather than implying that a units package solves semantic interoperability.

---

## P1-3 — Distinguish current harness-level observation mappings from first-class adapters

The manuscript sometimes says observational adapters catch specific errors, while elsewhere correctly stating that the `observational_adapter` execution role is supported but has zero registered instances and that several mappings remain embedded in harnesses.

Use two separate terms:

- **current:** harness-level observation mappings or transforms;
- **target architecture:** first-class registered observational adapters with their own contracts, provenance, gates, and evidence records.

The named-shot scorecard and abstract should not imply the target architecture is already fully instantiated.

---

## P1-4 — Clarify all schema and version namespaces

The draft uses several version numbers that can be confused:

- package/repository development version `0.4.0.dev0`;
- public release `v0.3.0`;
- contract schema `0.6`;
- registry schema `2`;
- evidence-graph schema `2`;
- generated artifact schemas with their own versions; and
- public snapshot schema `1`.

“Schema v2” is therefore ambiguous. Every version reference should name its namespace, for example `registry_schema_version: 2` or `evidence_graph_schema_version: 2`. Add a compatibility table to the supplement and a release-time test that declares which combinations are supported.

---

## P1-5 — Strengthen related work with a feature comparison rather than prose positioning alone

The new related-work section is a substantial improvement, but it is still too short to support the novelty claim. It currently says the paper is positioned against “six strands,” while only five prior-art subsections precede the novelty subsection. More importantly, the comparison remains qualitative.

Add a compact feature matrix comparing Puckworks with representative approaches across:

- research-object/provenance packaging;
- executable workflow provenance;
- model and dataset cards;
- formal units/quantity semantics;
- model interchange/co-simulation;
- evidence relation and fit/evaluation independence;
- negative outcome preservation;
- producer-bound manuscript values;
- composition-specific validation; and
- rights/governance state.

Relevant adjacent traditions include, at minimum:

- W3C PROV, RO-Crate, research compendia, and workflow provenance profiles;
- FAIR4RS and research-software quality guidance;
- Model Cards and Datasheets;
- formal unit and quantity ontologies such as QUDT or equivalent;
- SBML, CellML/COMBINE, and FMI/co-simulation standards;
- scientific workflow systems and executable-paper/reproducible-capsule practice;
- model credibility and verification/validation frameworks; and
- software-paper expectations such as JOSS where the paper discusses that route.

The novelty can remain narrow: the distinctive contribution is the executable combination of observable semantics, scoped evidence relations, provenance, failed-composition records, and producer-bound publication claims for a fragmented process-model literature. A matrix will make that claim more defensible.

---

## P1-6 — Add missing primary references

Several sources central to the revised argument are not in the reference list:

- Maille 2024, used extensively in the fast/slow comparison;
- Roman-Corrochano 2017, also central to that comparison;
- SBML and FMI, named in related work; and
- any formal source used for the community-corpus governance terminology or data-management obligations, if journal style calls for it.

The related-work section should cite official or primary standards rather than rely on unexplained names. The companion-paper placeholder also needs complete authorship/status or should be cited as a repository preprint/draft with a stable identifier if the target journal permits it.

---

## P1-7 — Strengthen the fast/slow analysis with identifiability and model selection

The revised semantic conclusion is sound: a common bi-exponential fit does not establish parameter portability. However, goodness of fit and a heuristic equality threshold are insufficient to decide whether one or two time constants are supported.

The final analysis should report:

- exact fit function and normalization;
- fit interval and sampling grid;
- parameter bounds and ordering convention;
- optimizer, number of starts, and convergence criteria;
- residual structure;
- AICc/BIC or an equivalent penalized comparison with a one-timescale model;
- bootstrap/profile-likelihood intervals or another identifiability diagnostic;
- sensitivity to fit window, normalization, and time-grid weighting; and
- the role of particle radius and diffusivity in the Roman-Corrochano absolute timescales.

The coarsest Cameron case previously produced distinct fitted constants of roughly 23.6 and 40.0 s, unlike the other three near-degenerate cases. Avoid a global statement that the Cameron model is one-regime. The stronger result is that the fitted coefficients are protocol-dependent and cannot be assigned Maille’s physical interpretation without transfer evidence.

For Roman-Corrochano, make clear that the tested fine-class absolute constants are radius-dependent through the diffusion timescale and that the unresolved coarse-class size prevents a whole-model numerical portability conclusion.

Finally, give this analysis a first-class claim/evidence record even if it remains an analysis rather than a registered component gate.

---

## P1-8 — Report dependence-aware uncertainty for the composition comparison

The composition comparison uses an autocorrelated time trace over a selected 15–95 s window. A point RMSE from one trace is not a complete uncertainty analysis. The repository already contains a moving-block/bootstrap and window-sensitivity diagnostic in the harness; the manuscript should use it.

Report:

- number and spacing of evaluated samples;
- handling of missing values and edge points;
- residual autocorrelation or effective sample size;
- moving-block bootstrap interval for RMSE differences or ratios;
- sensitivity to reasonable evaluation-window choices;
- exact constant-null fitting procedure;
- parameter counts for all rungs;
- whether the bootstrap conditions on fixed imported/fitted curves; and
- residual plots, not only scalar bars.

Be explicit that a block bootstrap over fixed predictions is not a full parameter-refit bootstrap and does not propagate all model uncertainty. The scientific point does not require overclaiming: if the composite loses robustly across windows and resamples, that is already a strong negative composition result.

---

## P1-9 — Separate software availability, scientific relation, and legal availability in the named-shot scorecard

The scorecard currently combines several dimensions in one “status/evidence” cell. A stage can be:

- registered but not redistributable;
- executable only with an optional/restricted source;
- verified numerically but not validated empirically;
- calibrated on the same campaign;
- outside its stated regime;
- scientifically blocked by an absent adapter; or
- open because the required measurement does not exist.

Use separate columns for:

1. component/configuration selected;
2. executable/available status;
3. rights/redistribution status;
4. comparison relation;
5. outcome;
6. fit/evaluation independence;
7. validity-domain status;
8. principal boundary/initial-condition assumptions; and
9. next measurement or adapter required.

This will prevent “software slot occupied” from being read as “scientific stage solved.” It will also reconcile the registry’s 25 identifiers with the smaller number of scientifically and legally available components described in public-facing repository material.

---

## P1-10 — Do not let the 104-row manifest become a maturity proxy

The manuscript now correctly calls the manifest a provenance inventory. Preserve that restraint throughout the abstract, figures, and publicity. A useful supplement would break the 104 records down by:

- measured, model-generated, analytic/reference, and contextual source;
- fit, evaluation, and reference role;
- independent, same-campaign, same-data, or not applicable relationship;
- public, restricted, rights-blocked, or retrieval-only status;
- uncertainty retained or absent;
- unique source campaign and publication count; and
- duplicate/derived record relationships.

That breakdown is scientifically more informative than a raw record count and would help readers understand the evidence base without mistaking inventory size for validation depth.

---

## P1-11 — Make the curated-corpus construction reproducible

The paper is commendably honest that the corpus is curated rather than systematic. A methods/resource paper still needs a reproducible account of how the corpus was assembled. The planned supplement should contain:

- databases, repositories, citation trails, community leads, and web sources searched;
- search dates and search strings where applicable;
- inclusion and exclusion criteria;
- duplicate and derivative-publication handling;
- treatment of theses, code repositories, preprints, and non-English sources;
- screening and card-creation workflow;
- update cadence and stopping rule; and
- a log of candidate sources that were excluded, blocked, or deferred and why.

This need not be presented as a systematic review. It should be presented as a transparent resource-construction protocol.

---

## P1-12 — Complete the external-corpus governance determinations before reporting statistics

The new governance section is strong in tone and appropriately cautious. It should not, however, be mistaken for completed governance. Before any corpus-derived statistic appears in the paper or supplement, document:

- the exact data-owner grant and permitted-use scope;
- confirmation regarding contributor terms and downstream research reuse;
- institutional ethics/IRB or exemption determination, where applicable;
- lawful basis and relevant jurisdictional analysis;
- controller/processor roles;
- access-control and audit arrangements;
- retention and deletion schedule;
- withdrawal/deletion propagation into frozen analyses and published aggregates;
- small-cell thresholds and linkage-risk review;
- salt management, rotation, and incident-response procedures;
- a threat model or DPIA-equivalent appropriate to the risk; and
- how reviewers can verify the grant/terms without exposing confidential material.

Because the current manuscript reports no community-corpus result, consider keeping a concise scope/governance statement in the main text and moving the operational detail to a data-management supplement. The paper should not become longer merely to document a dataset not yet used in a result.

---

## P1-13 — Decide the publication genre and edit to it

At nearly 13,000 words before completed figures and supplements, Paper 3 is much broader than a typical short software paper. It contains architecture, literature synthesis, three scientific demonstrations, experiment design, a named-shot audit, data governance, and a proposed general method.

Two coherent routes are available:

### Route A — Methods/resource article

Retain the scientific demonstrations, add formal framework evaluation, complete the evidence architecture, and present Puckworks as a research method plus curated resource. This is the better match to the current ambition.

### Route B — Software paper

Reduce the manuscript substantially, focus on purpose, architecture, installation, API, tests, community use, and availability, and move most scientific demonstrations into companion papers or documentation.

The current draft sits between the two. I recommend Route A. The failed-composition, fast/slow semantic comparison, and named-shot scorecard are too scientifically interesting to compress into a conventional software note; in return, the paper must meet methods-article expectations for evaluation and uncertainty.

---

## P1-14 — Define claim ownership across Paper 3 and companion manuscripts

Paper 3 repeats quantitative temporal-flow and composition results that may also appear in companion papers or public-value articles. The evidence graph has a `claim_owner` field, but the manuscript does not show readers which publication owns each result.

Add a claim-ownership table listing:

- stable claim ID;
- primary publication;
- role in Paper 3: primary result, method demonstration, context, or cross-reference;
- canonical result producer;
- canonical figure/table; and
- permitted abbreviated reuse.

This will prevent duplicated primary claims, inconsistent numbers, and ambiguity over which paper should be cited for the scientific result versus the evidence-registry method.

---

## P1-15 — Explain identifier, publication-year, and rights lineage for restricted ports

The component identifier `grudeva2025.reduced` is paired with a 2026 publication reference, and its availability is affected by upstream licensing/rights status. Explain that the identifier reflects repository/source lineage or initial manuscript year, not necessarily the final publication year. More generally, separate:

- scientific implementation status;
- technical executability;
- source-code licensing;
- data redistribution rights; and
- public-release inclusion.

A component can be scientifically described yet excluded from release execution. This distinction belongs in the component inventory or rights supplement, not only internal governance notes.

---

## P1-16 — Avoid overclaiming producer binding where prose values remain duplicated

The manuscript repeatedly says manuscript-facing values trace to named producers and hard-coded values fail validation. That aspiration is correct, but the current PV-05 drift demonstrates that not all paths are actually producer-bound to one source. The wording should distinguish:

- values governed by `PublicClaim.Producer`;
- values in evidence-link prose;
- generated registry tables;
- figure-caption specifications; and
- values manually repeated in the abstract/manuscript.

The final release gate should enumerate every quantitative string in the manuscript or, more realistically, generate all claim-containing tables/captions from a structured claim bundle. Until then, replace universal statements such as “a graphic or abstract number without this record should be treated as untracked” with an explicit current coverage statement and completion target.

---

## P1-17 — Improve the composition ladder’s scientific controls

The current negative result compares a fitted constant baseline, an extraction-only branch, and an extraction-plus-swelling branch. Add controls that help locate the failure:

- neutral swelling branch, verifying exact reduction;
- scaled-amplitude swelling sensitivity without fitting it to the evaluation trace;
- shifted time-origin sensitivity;
- initial-state sensitivity representing pre-swollen grains;
- separate internal-grain and intergranular porosity states;
- fixed-pressure versus imposed-flow/control-mode variants;
- alternative observation operators from state to flow; and
- a predeclared validation trace or condition not used in the imported parameterization.

These need not rescue the model. Their purpose is to show which interface assumption drives the incompatibility and to convert the negative result into a sharper experiment.

---

## P1-18 — Use calibrated language for “validation,” “prediction,” and “validated correction” throughout

The manuscript is much better than earlier versions, but a few phrases still need discipline:

- a code-verification gate is not validation of a physical closure;
- a source-curve reproduction is not prediction;
- a same-campaign compatibility check is not independent validation;
- a Forchheimer regime diagnostic is not a “validated correction”; and
- a failed exploratory composition is a negative **outcome**, not “negative validation.”

Run a final terminology lint over the manuscript, public claims, figure captions, and evidence matrix. The permitted-verb table is a strong idea; make it executable and fail the release if a claim’s prose uses a stronger verb than its evidence object permits.

---

## 6. Cross-schema consistency audit

The table below summarizes the central architectural mismatch.

| Concept | Manuscript | Component registry | Evidence graph | Public claim API | Status |
|---|---|---|---|---|---|
| Evidence relation | Nine named categories | Nine-value `EVIDENCE_STRENGTHS` | Registry tier plus separate `relationship` | Six legacy free-standing labels | **Inconsistent** |
| Negative result | Outcome polarity, not relation | No outcome field on component | Support/adjudication plus claim prose; gate pass/fail available | `negative validation` remains an allowed evidence string and is used by PV-03 | **Contradiction** |
| Reference artifact/model role | Separate axis | Not represented by component tier | Source role/status and `reality_facing` partially represent it | Not represented | **Incomplete** |
| Fit/evaluation relationship | Conceptually separate | Not represented | Explicit `relationship`/source `independence` | Not represented | **Incomplete** |
| Public badge | Derived from internal evidence | Not represented | Not clearly derived | Manually authored one-of-four value | **Not mechanically derived** |
| Multiple evidence records | Claims/components can carry several | One component-level string | Multiple gate links possible | One string per claim | **Lossy export** |
| Evidence ordering | Categories should not collapse | Tuple order implicitly used as strength | `_STRENGTH_RANK`; strongest-gate roll-up | Flat labels without declared order | **Conceptual conflict** |
| Outcome | Pass/fail/mixed should be distinct | Gate result only | Gate/adjudication/support distributed | No outcome field | **Not unified** |
| Scope to observable/domain | Required in prose | Component `valid_range` only | Claim/caveat/source detail | One claim-level validity string | **Coarse** |
| Producer binding | Every number should trace | Not applicable | Claim prose may copy numbers | Numeric result map is producer-bound | **Partial** |
| Dependency closure | All load-bearing provenance claimed | Component metadata only | Gate/source graph, not per-output transitive closure | Flat component and dataset lists | **Overclaimed in abstract** |

### Conclusion from the audit

The manuscript should not describe the current system as one finished evidence architecture. It is better described as **three partially converged layers**:

1. a component metadata tier;
2. a richer evidence-link graph for Paper 3 adjudication; and
3. an older public-claim presentation schema.

The next release should converge these layers rather than add another translation table.

---

## 7. Quantitative and equation consistency audit

| Claim or quantity | Manuscript/public path | Evidence/code path | Assessment | Required disposition |
|---|---:|---:|---|---|
| Registered components | 25 | generated registry counts: 25 | Consistent | Retain; regenerate at release |
| Execution roles | 12 runtime, 13 calibration | generated counts: 12/13 | Consistent | Retain |
| Manifest records | 104 | live manifest/generated artifacts: 104 | Consistent | Retain; add evidence-role breakdown |
| Constant null RMSE | 0.573 g s⁻¹ | evidence matrix ~0.603 g s⁻¹ | **Material drift** | Choose one canonical producer and regenerate all uses |
| Extraction-only RMSE | 0.116 g s⁻¹ | evidence matrix ~0.113 g s⁻¹ | Drift beyond stated uniform rounding | Reconcile producer/window/rounding |
| Composite RMSE | 0.648 g s⁻¹ | evidence matrix ~0.650 g s⁻¹ | Small but real drift | Reconcile |
| Composite/null ratio | 1.131 using 0.573 | about 1.08 using 0.603/0.650 | **Interpretive impact** | Recompute after canonical values selected |
| Forchheimer number formula | `k_I*rho*u/mu` | implementation/evidence matrix `rho*k*u/(mu*k_I)` | **Scientific equation error** | Correct and regenerate range |
| Forchheimer range | ~0.86–5.7 | model-generated, extrapolated closure | Potentially valid only under correct formula/configuration | Bind inputs and calculation to claim record |
| Swelling contribution | manuscript subtracts positive `Phi_swelling` | code adds negative signed value | **Interface-sign mismatch** | Rename/redefine and test |
| PV-05 “parameter-free” | evidence prose says parameter-free | code says imported pre-fitted; not free here, not parameter-free | **Incorrect wording** | Replace with “no parameters refit” |
| PV-05 source commit | appears as generation provenance | verifier reuses stored commit | Ambiguous | Split generated/verified commit fields |
| Fast/slow portability | qualitative non-portability | model-generated fits | Conceptually sound, statistics incomplete | Add model selection/identifiability/sensitivity |

The corrected counts show that the producer/CI approach works when applied end to end. The RMSE drift shows that “generated” is not sufficient when multiple generated systems maintain separate copies of a claim.

---

## 8. Recommended canonical evidence and claim model

The paper would be much stronger if it presented one concrete schema that the repository actually uses. The following is a suggested direction, not a demand for this exact serialization.

```yaml
claim_id: PV-05
schema:
  claim_schema_version: 2
  evidence_schema_version: 3

question: >-
  Can two individually plausible components be combined safely through one
  shared porosity state?
headline: Adding the imported swelling branch worsened this tested composition.

result:
  values:
    constant_rmse_g_per_s: <producer-bound value>
    extraction_only_rmse_g_per_s: <producer-bound value>
    composite_rmse_g_per_s: <producer-bound value>
  units:
    constant_rmse_g_per_s: g/s
    extraction_only_rmse_g_per_s: g/s
    composite_rmse_g_per_s: g/s
  evaluation_window_s: [15, 95]
  uncertainty:
    method: moving_block_bootstrap_on_fixed_predictions
    block_length: <value>
    interval: <producer-bound values>
    limitations: does not refit imported model parameters

producer:
  module: puckworks.public.model_composition
  function: build_payload
  result_paths: {...}
  producer_source_sha256: <hash>
  generated_from_commit: <sha>
  last_verified_against_commit: <sha>
  environment_lock_sha256: <hash>

inputs:
  datasets:
    - manifest_id: waszkiewicz2025/traces_time_dependent
      role: evaluation
      independence: same_campaign_not_held_out
      sha256: <hash>
    - manifest_id: waszkiewicz2025/static_calibration
      role: fit
      independence: fit_input
  components:
    - id: brewer2026.coupled_kappa_t
      role_in_claim: composition
    - id: mo2023_2.swelling
      role_in_claim: imported_branch
    - id: waszkiewicz2025.poroelastic
      role_in_claim: degenerate_reference
  transforms:
    - id: shared_porosity_observation_operator_v1
      contract_version: <version>

evidence:
  comparison_relation: exploratory_composition_test
  outcome: failed_declared_performance_check
  reference_target: measured_system_trace
  fit_evaluation_relationship: post_fit_same_campaign
  support_status: admissible_negative_result
  observable: mass_flow_rate
  domain:
    pressure_bar: 9
    time_window_s: [15, 95]
    rig: Waszkiewicz source fixture
  claim_supported: >-
    The imported branch is incompatible with this shared-state composition under
    the declared initial/boundary conditions and observation operator.
  claims_not_supported:
    - swelling is absent from real espresso pucks
    - swelling parameters alone caused the failure
    - extraction-only physics is independently validated

public_badge:
  value: EXPLORATORY_SIMULATION
  derived_by: evidence_badge_policy_v1

caveat: >-
  No parameters were refit in this composition test. The imported parameters,
  shared-state definition, initial condition, boundary condition, and observation
  operator are jointly implicated; this test does not identify one as the sole cause.

reproduction:
  command: python -m puckworks.public.model_composition verify
  archive_doi: <doi>
```

### Design principles

1. **Component metadata is not claim evidence.** A component can have many scoped evidence records; it should not be reduced to one global tier.
2. **Outcome is separate from relation.** A failed independent test and a failed exploratory composition are both negative outcomes but have different relations.
3. **Fit/evaluation independence is explicit.** It should not be inferred from words such as “held out” or “external.”
4. **The reference target is explicit.** An analytic identity, source-model curve, measured system, and synthetic benchmark are not interchangeable.
5. **Badges are derived.** Public presentation cannot upgrade the internal evidence.
6. **Every number has one producer path.** Other artifacts point to it rather than copy it.
7. **Every claim states what it does not support.** This is one of Puckworks’ strongest practices and should be retained.
8. **Provenance is immutable and multi-stage.** Generation and later verification are separate events.
9. **Scope is attached to the evidence record.** The same component may have different evidence in different domains and for different observables.
10. **Failure is first-class.** A failed check is retained, citable, and usable for experiment design.

### Migration strategy

A practical migration could proceed in five steps:

1. Introduce the canonical object alongside existing schemas.
2. Write deterministic adapters from registry gates and `EVIDENCE_LINKS` into the canonical representation.
3. Migrate public claims and reject legacy-only evidence strings in new claims.
4. Generate manuscript tables, captions, and public site badges from the canonical bundle.
5. Remove the old vocabularies only after round-trip and archive-compatibility tests pass.

The migration should preserve old public artifacts by version rather than silently reinterpret them.

---

## 9. Recommended framework-evaluation study

A defensible evaluation can be completed without turning Paper 3 into an enormous empirical project. The objective is not to estimate the prevalence of errors in all espresso literature. It is to test whether the proposed guardrails detect representative defects that they claim to detect.

### 9.1 Research questions

- **RQ1:** Which classes of comparison/composition defects are detected by contracts, units, provenance, evidence, producer, and release layers?
- **RQ2:** Which defects remain undetected even when all current guardrails pass?
- **RQ3:** What false-positive and authoring burden do the guardrails impose?
- **RQ4:** Does the integrated architecture detect more scientifically consequential defects than simpler baselines?

### 9.2 Evaluation corpus

Select a frozen subset containing:

- one machine/infiltration chain;
- one Darcy/Forchheimer flow chain;
- two extraction models with incompatible concentration/inventory semantics;
- the shared-porosity composition;
- one source-curve reproduction gate;
- one held-out gate;
- one independent comparison; and
- one rights-restricted or missing-source case.

### 9.3 Mutation classes

Create deterministic mutations at five layers:

| Layer | Example mutations |
|---|---|
| Contract/state | same-unit wrong field; pressure node swap; sign inversion; missing→zero; reference-volume swap |
| Parameter/provenance | wrong grind adapter; total→extractable inventory; stale source hash; unproven parameter substitution |
| Evidence | same-data test relabeled independent; source reproduction called validation; failed outcome omitted; strongest gate applied globally |
| Publication | hard-coded number; stale figure; copied claim value drift; missing caveat; badge overpromotion |
| Release/rights | dirty tree; wrong commit; missing lock; rights-blocked artifact included; archive/source mismatch |

Each mutation should have an oracle stating which layer ought to detect it.

### 9.4 Baselines

Compare:

- prose cards only;
- unit/dimensional checks only;
- producer binding only;
- provenance hashes only; and
- full Puckworks architecture.

This will show the incremental value of semantic contracts and evidence typing rather than attributing all benefits to ordinary CI.

### 9.5 Metrics

- true-positive detection rate by defect class;
- false-positive rate on unmutated cases;
- number of defects detected at more than one layer;
- number and severity of undetected defects;
- runtime overhead;
- lines/fields required to register a new component and claim;
- reviewer time to interpret a claim; and
- inter-rater agreement for curated evidence labels, if multiple reviewers are available.

### 9.6 External usability test

Ask one technically competent contributor who did not author the target component to:

1. install the frozen release;
2. reproduce one figure;
3. add a small documented component or adapter;
4. create one claim record; and
5. interpret one failed evidence record.

Record ambiguities and failures. This would satisfy the manuscript’s stated need for an external workflow far more convincingly than a generic assertion of usability.

### 9.7 Result presentation

A single matrix can summarize the study:

| Defect | Prose card | Units | Producer | Provenance | Evidence graph | Full release gate | Detected? |
|---|---:|---:|---:|---:|---:|---:|---:|
| Wrong pressure node | 0/1 | 0 | 0 | 0 | 1 | 1 | yes |
| Stale numeric caption | 0 | 0 | 1 | 0 | 0/1 | 1 | yes |
| Same-data test relabeled independent | 0/1 | 0 | 0 | 0 | 1 | 1 | yes |
| Same-unit wrong observable | ... | ... | ... | ... | ... | ... | ... |

The actual results, including failures, should be reported. An architecture that openly documents its blind spots will be more credible than one that claims universal prevention.

---

## 10. Review of the scientific demonstrations

## 10.1 Observable and unit linting

### Strengths

- The incompatible saturation concentrations, pressure-node distinctions, inventory bases, and mixed chemistry units provide intuitive examples.
- The manuscript correctly avoids averaging incompatible values or treating a fitted response-surface vertex as a raw observed optimum.
- The “fast fraction” example shows that shared labels can conceal different constructions even when trends agree.

### Required improvements

- State whether each issue was caught automatically, by a reviewer/card, or by an analysis-specific assertion.
- For every example, identify the exact contract field or lint rule that failed.
- Include one same-unit/wrong-observable example to show why dimensional typing alone is insufficient.
- Avoid presenting manually noticed semantic discrepancies as automatically prevented unless the corresponding guard is implemented and tested.
- In Figure 3, visually distinguish measured values, source constants, fitted objects, and derived registry quantities.

## 10.2 Null-first temporal-flow workflow

### Strengths

- The ladder from machine capacity through simple nulls, temporal candidates, flexible in-sample fits, and held-out assessments is methodologically sound.
- The paper correctly distinguishes model capacity from causal identification.
- The proposed experiment-design linkage is valuable.

### Required improvements

- Keep the scientific quantitative claims primarily owned by the companion temporal paper.
- State parameter counts, calibration data, evaluation data, and relationship at every rung.
- Do not use “held out” without specifying what information from the same rig/campaign remains reused.
- Include the simplest level-only and trend-only baselines in the figure, not only more mechanistic candidates.
- Ensure that every rung’s public verb is generated from its evidence record.

## 10.3 Fast/slow semantic portability

### Strengths

- This is an excellent demonstration that a common functional form does not create a common physical interface.
- The revised wording is more accurate than the previous paragraph.
- The example naturally connects observable semantics, parameter provenance, and identifiability.

### Required improvements

- Add formal one- versus two-timescale model selection.
- Report uncertainty and optimizer sensitivity.
- Separate dimensionless shape invariance from absolute timescale variation.
- Restrict Roman-Corrochano numerical statements to the declared particle/species configuration.
- Add primary references and a generated claim/result record.
- Use “one physical diffusion process” rather than “single diffusion mode.”

## 10.4 Failed shared-porosity composition

### Strengths

- Preserving the failed result is one of the manuscript’s most compelling contributions.
- Exact reduction to the extraction-only branch is an appropriate structural test.
- The null baseline prevents complexity from being rewarded merely for existing.
- The manuscript correctly says the result does not disprove swelling.

### Required improvements

- Reconcile the RMSE values.
- Fix the sign contract.
- Remove “parameter-free” and narrow the causal diagnosis.
- Add dependence-aware uncertainty and residual plots.
- Separate the scientific state variables if internal-grain and bed porosity are not demonstrably identical.
- Add nested interface/initial-condition sensitivities to locate the incompatibility.
- Record the failed outcome in the canonical evidence schema rather than as prose attached to a passing diagnostic gate.

## 10.5 Named-shot scorecard

### Strengths

- Ending in an open measurement cell rather than fabricating a complete cup is scientifically excellent.
- The scorecard makes pressure-node, adapter, regime, and measurement gaps visible.
- The corrected infiltration language is now appropriately cautious.

### Required improvements

- Separate executable, legal, evidentiary, and domain statuses.
- Correct and regenerate the Forchheimer diagnostic.
- State which shot data are measured, fitted, imported, or assumed.
- Identify every observation operator.
- Make the final promotion experiment pre-registered enough to distinguish reconstruction from prediction.
- Export the scorecard as a machine-readable claim/dependency object, not only a table.

---

## 11. Section-by-section review

## Title

The title is accurate and professional. “Evidence registry” is defensible only after the public/evidence schemas converge. Until then, “evidence-aware component registry” would be slightly more precise. Once the canonical evidence object is implemented, the current title can be retained.

## Draft-status note

The note is unusually useful, but it should not survive unchanged into a submitted paper. Replace it with a concise version/availability statement. “Figures specified but not embedded” is a drafting warning, not manuscript content.

## Abstract

The abstract is clear and compelling but currently does too much. It includes inventory counts, three demonstrations, exact composition numbers, the named-shot result, and a general-method claim. The main corrections are:

- soften the transitive “all load-bearing components” statement;
- remove or reconcile exact PV-05 numbers;
- avoid claiming a fully non-collapsed evidence system while the implementation retains a strongest-gate rank;
- call the cross-domain method a demonstrated pattern or proposed transferable method; and
- consider removing the 104 manifest count unless its role is explained in one phrase.

## Introduction

The introduction establishes the problem effectively. It would benefit from one explicit research question and one contribution list. For example:

1. How can observable and parameter semantics be represented so incompatible models fail visibly?
2. How can evidence relation and provenance constrain public claims?
3. How can failed compositions be retained and converted into experiments?
4. How well do the resulting guardrails detect seeded defects?

The fourth question is currently missing because the framework is not evaluated.

## Section 2 — Scope and corpus

The corrected counts and curated-corpus caveat are strong. Add a short corpus-construction summary and move full search/screening detail to Supplement S1. Clarify the distinction between registered, executable, redistributable, and independently evidenced components.

## Section 3 — Architecture

The execution-role/provenance split is now clear. Add a diagram of current versus target adapter architecture. Avoid implying that schema-supported roles are operational components. Explain how a configuration is validated before execution and whether contracts are runtime checked, static checked, or both.

## Section 4 — Typed observable and parameter contracts

This section contains some of the best domain examples, but also the incorrect Forchheimer equation. Correct it. Expand the “what static dimensions do not catch” discussion. For each example, state the exact automated guard and residual manual judgment.

## Section 5 — Evidence taxonomy

This is the manuscript’s conceptual centre and its largest unresolved implementation mismatch. Replace “four independent axes,” separate authored versus derived fields, remove the claim that the registry enum alone is the evidence relation architecture, and align the public schema. A diagram should show component metadata, scoped evidence records, claim selection, outcome, and derived badge.

## Section 6 — Provenance and reproducibility

The card/manifest/producer/release discussion is strong. The statement that manuscript values “should trace” to producers is honest, but the surrounding language sometimes implies universal enforcement. Quantify coverage. Separate generation commit from verification commit. Generate Appendix B from code.

The external-corpus section is responsible but long relative to the paper’s current use of the corpus. Condense the main text unless a corpus result is added.

## Section 7 — Demonstrations

The demonstrations are relevant, but methods, results, and interpretation sometimes blend. Each should use a common template:

- question;
- components/data;
- observable contract;
- fit/evaluation design;
- null model;
- producer;
- result with uncertainty;
- evidence relation/outcome;
- supported and unsupported claims; and
- next discriminating measurement.

This repetition would reinforce the framework rather than feel redundant.

## Sections 8–10 — Experiment design and workflow

The disagreement-to-experiment logic is a strong contribution. Make the model predictions directional and predeclared, and specify what observation would discriminate among them. Avoid presenting generic “collect more data” recommendations.

## Section 11 — Named-shot scorecard

Retain this section. It is an effective capstone. Redesign the table as recommended above and fix the flow-regime diagnostic. Make the distinction between a populated software stage and a scientifically supported stage visually unavoidable.

## Section 12 — Related work and novelty

Keep the narrowed novelty claim. Correct “six strands,” add the missing references, and include a feature matrix. Discuss formal semantic/unit systems and model credibility frameworks, not only packaging and interchange.

## Section 13 — Discussion

The discussion is well judged, especially “composition creates a new model.” Add one paragraph on limits of automated semantic checking: ontologies and contracts can encode distinctions, but someone still has to make correct scientific judgments and source mappings.

## Section 14 — Limitations and readiness

The subsection numbering is wrong: `13.1` and `13.2` should be `14.1` and `14.2`. Update the readiness table to reflect the actual repository. Add the evidence-schema split, lack of formal framework evaluation, and unresolved figure/archive work as explicit limitations.

## Conclusions

The conclusion is strong but should not say the registry already “labels evidence at the claim level” without acknowledging the schema split. Once the canonical evidence object is implemented, the current conclusion will be defensible.

## Software and data availability

Replace the moving repository URL with a frozen release and DOI in the final paper. State exactly which components/data are included, optional, rights-blocked, or retrieval-only. Include the license for the software itself and a machine-readable software citation.

## Figure specifications

Convert all specifications into figures before further external review. Captions should be generated or checked against the canonical claim bundle. Figure 5 must use reconciled numbers and Figure 2 must reflect the final evidence object.

## Appendix A

The generated inventory is now a success. At submission, include the generated artifact directly rather than keeping an “inline copy retained for reading” plus a separate generated file. One source should render both.

## Appendix B

Replace with the actual versioned schema as discussed above.

## References

Add Maille, Roman-Corrochano, SBML, FMI, and any missing standards/frameworks. Resolve the companion manuscript placeholder and archive citation. Check whether “Grudeva 2025” identifiers need an explanatory note against the 2026 publication.

---

## 12. Line-level and editorial comments

Line numbers refer to the manuscript at commit `d9ee264` and will move after revision.

| Line(s) | Current issue | Recommended edit |
|---:|---|---|
| 3–7 | Working-draft metadata and process note occupy manuscript front matter | Remove from final article; preserve in repository release notes |
| 11 | “each output carries ... all load-bearing components” exceeds the current flat claim schema | Soften or implement/test transitive dependency closure |
| 11 | Exact PV-05 values conflict with the generated evidence matrix | Remove until reconciled, then generate from one claim bundle |
| 11 | “general method” may imply cross-domain evaluation | Use “method demonstrated on the espresso corpus” until externally evaluated |
| 31–33 | Corpus construction is candid but not reproducible | Add concise search/construction protocol and supplement pointer |
| 33 | “schema” is not namespace-qualified | Use `registry schema version 2` |
| 47 | Role counts are now correct | Retain; generate directly in final build |
| 49 | Project synthesis explanation is accurate | Retain |
| 91–121 | Component metadata architecture is improved | Add distinction between component metadata and scoped claim evidence |
| 131–143 | Contract-layer comparison is useful | Fill residual-risk cell for dimensional typing; identify current versus planned adapters |
| 153 | `k_I` terminology needs dimensional definition | State units and exact closure convention |
| 178–182 | Forchheimer discussion contains the wrong formula | Replace with `rho*k*abs(u)/(mu*k_I)` and regenerate scorecard |
| 182 | “pore scale” may conflict with superficial velocity | Define velocity and scale convention precisely |
| 182 | “values of order unity” is model-specific | Tie threshold to the defined ratio and declared closure, not a universal onset law |
| 190 | Fast-fraction comparison is good | Add producer/result pointer and uncertainty/definition table |
| 192 | Fast/slow paragraph is substantially improved | Add primary references and avoid implying formal two-regime selection from fit quality alone |
| 198–200 | Missing-not-zero and no-repurposing rules are strong | State which are mechanically enforced versus review conventions |
| 208 | “four independent axes” is inaccurate | Use separate internal fields plus derived badge |
| 210 | Calls component `evidence_strength` the evidence relation | Replace with canonical comparison-relation field after schema convergence |
| 211 | Correctly says negative result is outcome, not relation | Update public schema and PV-03 to make this true in code |
| 212 | Artifact/model role is not represented in public claim object | Add field and migration |
| 213 | Badge said to be derived | Implement deterministic derivation; prohibit manual upgrades |
| 229 | Says relation names exactly match the code | True only for registry, not public schema/evidence graph; qualify |
| 233 | “do not collapse into strongest or weakest” conflicts with `_STRENGTH_RANK` roll-up | Remove ordering or narrow/document heuristic |
| 235 | Claims public schema preserves underlying label unchanged | Public schema uses a different legacy vocabulary; correct after migration |
| 263–265 | Producer/result-bundle principle is strong | Quantify current coverage and eliminate copied evidence prose |
| 269 | Lists claim fields not all present in Appendix B/canonical object | Generate Appendix B from actual schema |
| 275–283 | Release contract is useful | Add generated-from versus verified-against commit distinction |
| 281 | Exact environment versions are useful but not a full lock | Retain with lock/container hash in final archive |
| 287–309 | Governance is responsible but lengthy without corpus results | Condense main text or add a scientifically justified corpus analysis after approvals |
| 295–303 | Several governance obligations are stated as process facts | Distinguish implemented controls from planned/required controls with status labels |
| 354–366 | Fast/slow results need formal methods | Add fit protocol, model comparison, intervals, radius/window sensitivity |
| 382–394 | Composition result is important | Reconcile numeric paths, sign semantics, and causal language |
| 390 | Any remaining “negative validation” wording is conceptually wrong | Use “negative outcome under [named relation]” |
| 427–452 | Scorecard is a strong capstone | Split scientific, software, rights, and domain status columns |
| 445 | `Fo_F` range depends on erroneous printed formula and extrapolated closure | Regenerate from corrected producer and state all inputs |
| 458–484 | Related work is improved | Correct “six strands”; add feature matrix and missing citations |
| 480 | SBML/FMI named without references | Cite primary/official specifications |
| 484 | Novelty claim is appropriately narrow | Retain after evidence implementation converges |
| 508–518 | Generalization is now properly tempered | Retain |
| 522 | Subsection number says 13.1 under Section 14 | Change to 14.1 |
| 530 | Subsection number says 13.2 under Section 14 | Change to 14.2 |
| 534–547 | Readiness table is stale | Replace with released/current/remaining matrix |
| 536 | Editable-install-only description is obsolete | Record packaged release and clean-install requirement |
| 538 | Public tutorial description is obsolete | Name current public Colabs/workflows and freeze one for paper |
| 541 | CI separation described as future though lanes exist | State actual current coverage and remaining archive benchmark need |
| 547 | Contribution/changelog/conduct described as future | Remove completed items and identify real release gaps |
| 553–557 | Conclusion is strong but assumes converged evidence layer | Qualify or complete implementation |
| 561 | Moving repository URL only | Replace with DOI/tagged archive in final |
| 565 | Corpus statement should remain conditional until approvals complete | State whether any corpus-derived result is actually included |
| 567–581 | Authorship/disclosure placeholders remain | Complete before circulation as a paper draft |
| 583–611 | Figures remain specifications | Generate and embed; bind captions to claim bundle |
| 603 | Figure 5 values conflict with evidence matrix | Reconcile before rendering |
| 628 | Inline generated-table copy creates duplication | Render directly from generated source in manuscript build |
| 658–683 | Appendix B is not the implemented or proposed canonical evidence object | Replace with generated versioned schema |
| 675–676 | One evidence label plus badge contradicts §5 | Add relation/outcome/target/independence/support fields |
| 680 | `source_commit` is ambiguous | Split generation and verification provenance |
| 687 | Repository citation incomplete | Add release version, DOI, access date, authors, license |
| 699 | Companion paper is a placeholder | Supply stable citation/status or remove from formal references |
| 700–708 | Related-work references are incomplete | Add Maille, Roman-Corrochano, SBML, FMI, and selected framework sources |

### Copy and presentation corrections

- Renumber tables sequentially rather than using “Table 2a” or “Table 4a” unless the target journal explicitly supports lettered sub-tables.
- Change “six strands” to “five strands” or add the missing sixth prior-art category.
- Use one typography convention for units: preferably `g s⁻¹`, `kg m⁻³`, and SI symbols in equations and captions.
- Use one term for the registered object: “component identifier,” not alternately “model,” “component,” and “slot” where the distinction matters.
- Distinguish “source paper,” “source model,” “registered implementation,” “configuration,” “claim,” and “public story.”
- Define every acronym at first use, including TDS, EY, FAIR4RS, SBML, and FMI.
- Avoid “validated correction” for the Forchheimer branch; use “implemented closure” or “model-derived correction,” with evidence status.
- Replace “parameter-free” with “no parameters refit in this test.”
- Use “one physical diffusion process” rather than “single diffusion mode.”
- Where values are approximate, state the rounding policy and ensure all copies derive from the same unrounded value.

---

## 13. Status of the previous review’s major comments

| Previous major comment | Current status | Evidence of progress / remaining work |
|---|---|---|
| 1. Decide publication genre | **Unresolved** | Draft remains between software paper and methods/resource article; length and breadth increased |
| 2. Repair manuscript-generation pipeline | **Partially resolved** | Registry counts now generated/CI-bound; quantitative claim paths still drift |
| 3. Rewrite architecture around schema v2 | **Substantially but not fully resolved** | Component metadata is corrected; public/evidence schemas remain incompatible |
| 4. Separate relation, outcome, target, and badge | **Conceptually improved; implementation unresolved** | Manuscript now makes distinction; public API still uses one legacy string and badge |
| 5. Resolve vector versus strongest/weakest contradiction | **Unresolved** | Manuscript rejects collapse; evidence graph still ranks and rolls up by strongest gate |
| 6. Correct infiltration overclaim | **Resolved** | Same-shot/same-campaign compatibility is now stated |
| 7. Define “executable” at each layer | **Partially resolved** | Roles clearer; scorecard still conflates availability, rights, and evidence |
| 8. Distinguish implemented capability from intent | **Partially resolved** | Limitations are more candid; observational adapters and claim provenance remain overstated in places |
| 9. Add related work and novelty positioning | **Partially resolved** | New section added; needs feature matrix, broader comparators, and missing citations |
| 10. Evaluate the framework itself | **Unresolved** | Still selected demonstrations only; no mutation/error-injection benchmark |
| 11. Reduce companion-paper duplication | **Unresolved** | No visible claim-ownership table in manuscript |
| 12. Complete figures | **Unresolved** | Seven specifications remain, no embedded figures |
| 13. Improve quantitative/statistical reporting | **Partially resolved** | Fast/slow analysis expanded; composition uncertainty and model selection incomplete |
| 14. Resolve external-corpus governance | **Substantially advanced, not complete** | Good governance statement; ethics/legal/operational determinations remain open |
| 15. Make corpus construction reproducible | **Unresolved** | Still curated with no completed search/screening appendix |
| 16. State typed-contract scope and limits | **Partially resolved** | New comparison table helps; dimensional-typing residual risk is understated |
| 17. Generate/rename the named-shot scorecard | **Partially resolved** | Evidence language improved; scorecard remains hand-maintained and dimensionally conflated |
| 18. Temper cross-domain generalization | **Resolved** | Explicitly presented as a hypothesis/pattern demonstrated only in espresso |

### Net assessment of the revision

Of the 18 previous major comments:

- **3 are resolved**: counts/schema-role correction is distributed across comments, infiltration overclaim, and cross-domain generalization;
- **10 are partially or substantially advanced**; and
- **5 remain essentially unresolved**, especially publication genre, framework evaluation, figures, corpus-construction method, and claim ownership.

The current revision is therefore meaningful progress, but it does not yet cross the threshold from strong draft to submission-ready manuscript.

---

## 14. Prioritized revision plan

## P0 — Complete before the next external manuscript review

### P0.1 Correct physics and interface contracts

- Correct the Forchheimer-number equation.
- Verify/regenerate the named-shot range from the correct producer.
- Fix the swelling sign convention and exported labels.
- Add cross-file equation/contract tests.

### P0.2 Converge the evidence architecture

- Define the canonical evidence object.
- Separate relation, outcome, reference target, fit/evaluation relationship, support status, scope, and derived badge.
- Migrate public claims, including PV-03.
- Remove or explicitly narrow the strongest-gate rank heuristic.
- Generate Appendix B and Figure 2 from the canonical schema.

### P0.3 Establish one quantitative source of truth

- Reconcile PV-05 values.
- Replace copied evidence prose numbers with producer/result references.
- Bind abstract, tables, figures, website, evidence matrix, and public claim to one result bundle.
- Split generation commit from verification commit.

### P0.4 Correct scientific interpretation

- Replace “parameter-free” with “no parameters refit.”
- Narrow the composition diagnosis to the tested mapping/configuration.
- Add dependence-aware uncertainty and residuals.
- Strengthen fast/slow identifiability/model-selection reporting.

### P0.5 Evaluate the framework

- Implement the mutation benchmark.
- Report detection coverage, false positives, blind spots, runtime, and author burden.
- Conduct one external clean-room reproduction/contribution task.

### P0.6 Complete the publication object

- Generate figures.
- Freeze the release and archive DOI.
- Complete authorship, contribution, funding, conflict, and acknowledgment fields.
- Add missing references.
- Resolve companion-paper claim ownership.

## P1 — Complete before journal submission

- Replace the readiness table with accurate release/current/remaining status.
- Add the related-work feature matrix.
- Complete the curated-corpus construction supplement.
- Finish corpus governance determinations before using corpus statistics.
- Redesign the named-shot scorecard with separate status dimensions.
- Add schema/version compatibility documentation.
- Document rights and redistribution status per component/data artifact.
- Add a full environment lock or container digest.
- Ensure one complete public example runs from the archive without private files.

## P2 — Editorial and presentation pass

- Fix section and table numbering.
- Standardize notation and unit typography.
- Remove drafting notes and placeholders.
- Tighten repeated explanations across §§4–7 and the appendices.
- Add alt text and accessible figure palettes/layouts.
- Verify every verb against the evidence policy.
- Run reference, DOI, link, and archive-permalink checks.

### Recommended order of work

The most efficient sequence is:

1. canonical evidence schema;
2. equation/sign corrections;
3. quantitative producer convergence;
4. mutation evaluation;
5. scientific-statistical updates;
6. figures and generated manuscript artifacts;
7. readiness/related-work/corpus supplements;
8. release freeze and editorial pass.

Doing figures before schema and numeric convergence would create avoidable rework.

---

## 15. Suggested replacement passages

These are examples of safer wording, not mandatory final prose.

### 15.1 Suggested abstract after the P0 corrections

> Published espresso models describe different parts of brewing with incompatible state variables, observable definitions, parameter lineages, validity domains, and evaluation designs. Combining them by matching similarly named quantities can therefore produce numerically plausible but scientifically invalid results. We present Puckworks, an executable component registry and evidence system for representing published espresso process models through typed state contracts, source and dataset provenance, scoped evidence records, reproducible claim producers, and release checks. In a pinned development snapshot the registry contains 25 components and 104 provenance-manifest records. We demonstrate the method through observable-semantic linting, a null-first temporal-flow comparison, and a failed shared-porosity composition retained as a negative result. The examples show that matching units or curve forms does not establish observable or parameter portability, and that composing individually plausible components creates a new model requiring its own verification and empirical tests. A named-shot scorecard exposes which stages are observed, calibrated, verified, reconstructed, extrapolated, or open rather than filling gaps with an unsupported end-to-end prediction. Puckworks provides a reproducible pattern for making model-comparison assumptions and evidence claims inspectable and testable; its transfer beyond espresso remains to be evaluated.

This version deliberately omits exact PV-05 numbers until the source-of-truth issue is resolved and does not claim complete transitive provenance unless implemented.

### 15.2 Suggested replacement for the evidence-axes paragraph

> Puckworks does not represent evidence with one scalar “validation strength.” Each claim carries separate fields describing (i) the comparison relation, (ii) the outcome of the declared check, (iii) the reference artifact and fit/evaluation relationship, and (iv) the observable and domain to which the result applies. Support and adjudication status are recorded separately. A public badge is then derived from those internal fields under a versioned policy; it is not independently assigned and cannot express a stronger claim than the underlying record permits. A negative result is therefore an outcome—such as a failed exploratory composition or failed independent comparison—not an evidence relation of its own.

### 15.3 Suggested replacement for the Forchheimer paragraph

> For the implemented momentum law, `grad(p) = -(mu/k)q - (rho/k_I)|q|q`, the ratio of inertial to viscous drag is `Fo_F = rho*k*|q|/(mu*k_I)`, where `q` is the declared superficial velocity, `k` is Darcy permeability, and `k_I` is the inertial-permeability parameter used by the closure. We use this quantity only as a model-derived regime diagnostic. Values near or above unity indicate that the inertial term is comparable with the viscous term **within this closure and parameterization**; they do not validate the closure or its extrapolated `k_I(k)` relation for coffee.

### 15.4 Suggested replacement for the composition interpretation

> No parameters were refit when the source-parameterized swelling branch was added to the shared-porosity composition. Under the declared state definition, initial and boundary conditions, and flow observation operator, the branch closed the shared state and worsened reconstruction relative to both the extraction-only branch and the selected constant baseline. This is a negative result for that composition. It does not show that swelling is absent, nor does it isolate parameter scaling as the cause; the imported parameterization, initial-state mapping, reference-volume definition, coupling rule, and observation operator remain jointly implicated.

### 15.5 Suggested replacement for the readiness conclusion

> The repository already provides a packaged public release, public execution paths, automated tests, contribution and governance materials, and generated Paper 3 inventory artifacts. The remaining submission blockers are narrower but more consequential: convergence of the evidence and public-claim schemas, one producer-bound quantitative claim bundle, formal evaluation of the guardrails, completed figures and archival environment, a frozen release/DOI, reproducible corpus-construction documentation, and one independent clean-room reproduction.

---

## 16. Recommended final manuscript structure

A more efficient methods/resource article could use the following structure:

1. **Introduction and research questions**
2. **Corpus construction and scope**
3. **Architecture**
   - components/configurations;
   - observable and parameter contracts;
   - canonical evidence object;
   - provenance/producer/release layers.
4. **Framework evaluation**
   - mutation benchmark;
   - external usability/reproduction.
5. **Scientific demonstrations**
   - observable linting and fast/slow non-portability;
   - null-first comparison;
   - failed composition;
   - named-shot scorecard.
6. **Experiment design from disagreement**
7. **Related work and novelty**
8. **Limitations, governance, and release readiness**
9. **Conclusions**
10. **Availability and archival citation**

Move detailed component inventory, full evidence dictionary, corpus protocol, governance controls, claim schema, and release manifest to supplements. This structure gives the framework evaluation enough prominence and reduces repeated architecture explanations.

---

## 17. Reviewer’s overall recommendation

**Recommendation: Major revision.**

Paper 3 has a credible and valuable central contribution. It is not simply a repository tour. Its strongest insight is that model interoperability is an evidentiary and semantic problem before it is a software-composition problem. The manuscript demonstrates this with unusually honest examples: inconsistent observables are kept separate, flexible fits are not promoted to causal explanations, and an added physical branch is allowed to make the model worse.

The recent revision has fixed several important factual and conceptual defects. In particular, the registry counts, role/provenance distinction, infiltration evidence language, related-work section, fast/slow semantic framing, cross-domain caution, and community-corpus governance are all better.

The remaining blockers, however, sit at the centre of the paper’s novelty. The evidence model is described more coherently than it is implemented; the public claim schema still uses legacy labels; the evidence graph ranks categories the manuscript says should not be ranked; two generated paths disagree on the headline composition values; and the paper currently contains one incorrect physics equation and one ambiguous state-sign contract. Those issues must be resolved before the paper can legitimately hold itself out as an executable evidence architecture.

A successful next revision should therefore prioritize **architecture convergence and empirical evaluation**, not additional narrative breadth. Once one evidence object governs claims, one producer governs numbers, the physics/interface errors are corrected, the guardrails are evaluated through seeded defects, and the figures are generated from a frozen archive, Paper 3 should be a strong candidate for a methods/resource venue.

---

## 18. Source ledger for this review

All repository links below are pinned to the reviewed commit wherever practicable.

### Manuscript and repository state

- [Current Paper 3 manuscript](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/PAPER_3_PUCKWORKS_DRAFT.md)
- [Reviewed commit](https://github.com/trbrewer/puckworks/commit/d9ee264f85b15633f56d540b44066e681979a5fc)
- [Comparison with previous reviewed snapshot](https://github.com/trbrewer/puckworks/compare/b8c84be3170dc644ef5d15036e9698214896842f...d9ee264f85b15633f56d540b44066e681979a5fc)
- [Repository README at reviewed commit](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/README.md)
- [Package metadata at reviewed commit](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/pyproject.toml)

### Registry and generated inventory

- [Component registry](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/registry.py)
- [Generated registry counts](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/paper3_resource/generated/registry_counts.json)
- [Generated Table 1](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/paper3_resource/generated/table1_registry_overview.md)
- [Generated Appendix A component catalogue](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/paper3_resource/generated/appendixA_component_catalog.md)

### Evidence and public claims

- [Evidence graph implementation](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/paper3/evidence_graph.py)
- [Evidence-link source data](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/paper3/EVIDENCE_LINKS.json)
- [Generated Paper 3 priority evidence matrix](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/paper3_resource/generated/paper3_priority_evidence_matrix.md)
- [Public claim schema](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/public/schema.py)
- [Seeded public claims](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/public/claims.py)

### Composition demonstration

- [Shared-porosity component](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/models/brewer2026/coupled_kappa_t.py)
- [PV-05 public result producer](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/public/model_composition.py)
- [Analysis harness](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/harness.py)
- [Packaged PV-05 snapshot](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/public/data/pv05_model_composition.json)

### Inertial-flow diagnostic

- [Wadsworth inertial-flow implementation](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/puckworks/models/wadsworth2026/inertial.py)
- [Wadsworth inertial-flow card](https://github.com/trbrewer/puckworks/blob/d9ee264f85b15633f56d540b44066e681979a5fc/docs/cards/wadsworth2026_inertial.md)

### Standards mentioned in related-work recommendations

- [Functional Mock-up Interface standard](https://fmi-standard.org/)
- [Systems Biology Markup Language](https://sbml.org/)
- [Journal of Open Source Software documentation](https://joss.readthedocs.io/)

---

*End of review.*
