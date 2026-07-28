# Detailed Review of PAPER 3 — Revision at `352dacd`

## Manuscript and review boundary

- **Manuscript reviewed:** `docs/PAPER_3_PUCKWORKS_DRAFT.md`
- **Repository:** `trbrewer/puckworks`
- **Reviewed revision:** `352dacd51015d95a3b5a5b3e1a8fb331419d78b0`
- **Previous detailed-review boundary:** `a0db098e0e5e99a1275a11f05676d46036a6c438`
- **Review date:** 27 July 2026
- **Recommendation:** **Major revision before external preprint circulation, formal peer review, or journal submission**

The revision is a serious and productive response to the preceding review. It introduces exact evidence-link identifiers, a claim-selection object, a conservative badge-derivation function, structured pressure-node traces, separate defect and control accounting, shot-level temporal results, corrected implementation-status language, and substantially better disclosure of what remains open. The central paper is now much closer to a publishable methods contribution.

The remaining problems are nevertheless material. Several are not matters of polish; they concern whether the implementation actually enforces the claims the manuscript makes for it. Most importantly, the new evidence-selection layer verifies that a selected identifier exists and belongs to the named dependency, but it does **not** verify that the evidence and claim concern the same observable, domain, dataset, campaign, pressure node, unit convention, or observation operator. The manuscript currently presents that semantic match as executable. It is still an authored assertion.

Two new regressions are especially instructive because they occur in the very classes of error the paper says it prevents:

1. the inline Appendix A contains **25** component rows while the generated catalog contains **27**, omitting `maille2024.two_regime` and `maille2024.phi_closure`; and
2. the manuscript's defect-class table reports stale class totals even though the benchmark result object now separates defects and controls correctly.

These are valuable findings rather than reasons to abandon the paper. They expose the exact boundary between the architecture already implemented and the architecture the manuscript sometimes describes prospectively. Correcting that boundary should make the paper considerably stronger.

---

## 1. Executive assessment

### 1.1 Overall recommendation

**Major revision.** The central proposition is strong: a coupled-model repository should make observable semantics, provenance, validation design, claim scope, and negative composition results executable rather than leaving them implicit in prose. Puckworks is an unusually rich case study for that proposition. The manuscript now contains enough implemented architecture and enough scientifically meaningful demonstrations to justify a methods paper.

I would not yet circulate this version as a preprint advertised as an implemented claim-constraining evidence registry. The principal reason is that the strongest novelty statement is ahead of the code: exact evidence identifiers are selected, but semantic commensurability is not mechanically established. A second reason is that the manuscript's own generated sections have demonstrably drifted from their canonical artifacts, while the prose says CI prevents that outcome. A third is that the public export layer still preserves authored numeric snapshots and authored presentation fields while describing them as generated or derived.

### 1.2 Publication-blocking findings

The following issues should be treated as P0:

1. **The inline generated artifacts have drifted.** Appendix A lists 25 of 27 components, and Table 6a misreports the current defect-class totals.
2. **Evidence selection is identity-checked but not semantics-checked.** An exact evidence ID can license a claim about an unrelated observable and campaign without a validation error.
3. **An empty evidence selection still falls back to the component's entire evidence inventory.** A component-dependent claim can validate with no claim-scoped selection.
4. **The public scalar `evidence_strength` remains authored and can contradict the selected evidence.** The many-to-one public mapping also collapses distinctions the manuscript treats as important.
5. **The badge remains a required authored field, and badge derivation conflates evaluation mode with outcome.** Export does not call `validate()` before writing.
6. **Selected evidence is not joined to its dataset and campaign lineage.** Source-level dataset roles are dropped before the public claim layer.
7. **Public numeric values are authored snapshots checked within tolerance, not values emitted from the producer.** This contradicts repeated “never hand-entered” statements.
8. **Commit provenance is not immutable across independent export processes, and the committed public claim artifact was last generated and verified at `99ea79f`, not the reviewed `352dacd` state.**
9. **The named-shot scorecard still summarizes each component's whole evidence vector rather than stage-selected claim evidence, and it retains a stale pressure-node caveat.**
10. **Appendix B still overstates universal claim coverage and misdescribes several fields and examples.**
11. **The public CSV and Markdown cards discard the selected-evidence and outcome information that constitutes the paper's novelty.**
12. **The mutation-suite narrative is improved, but its class table is wrong and several “production guard” cases are actually manuscript sentinels or locally recreated predicates.**

### 1.3 Principal strengths

The manuscript and repository now have several notable strengths:

- The distinction between a component's **evidence inventory** and a claim's **selected evidence** is conceptually correct and important.
- Evidence links now have stable identifiers, enabling precise reference rather than free-text attribution.
- The badge-derivation function is conservative and explicitly fails closed on some ambiguous states.
- The pressure-node correction is scientifically sound: the real gap was not an absence of pressure fields but untyped recorded traces and unchecked adapter boundaries.
- The temporal-flow section now distinguishes mean-trace diagnostics from per-shot results and no longer presents the flexible in-sample curve as a mechanistic victory.
- The failed shared-porosity composition remains visible and is framed as evidence about the composition rather than proof against swelling itself.
- The defect corpus now separates valid controls from defects and no longer reports a misleading coverage percentage.
- Rights, availability, curated-corpus status, unresolved metadata, and release limitations remain unusually candid.
- The paper's negative thesis—component validity does not imply composition validity—is both scientifically useful and broadly relevant.

---

## 2. Review scope, method, and limitations

### 2.1 Materials inspected

This review examined the current manuscript together with the implementation and generated artifacts most directly supporting its claims:

- `docs/PAPER_3_PUCKWORKS_DRAFT.md`
- `docs/paper3_resource/PAPER_3_ROUND_3_ACTION_TRACKER.md`
- `docs/paper3_resource/generated/appendixA_component_catalog.md`
- `docs/paper3_resource/generated/registry_counts.json`
- `docs/public/generated/claims.json`, `claims.csv`, and `claims.md`
- `puckworks/public/schema.py`
- `puckworks/public/claims.py`
- `puckworks/public/export.py`
- `puckworks/paper3/evidence_graph.py`
- `puckworks/paper3/registry_artifacts.py`
- `puckworks/paper3/appendix_b.py`
- `puckworks/paper3/defect_injection.py`
- `puckworks/paper3/named_shot_scorecard.py`
- `puckworks/contracts.py`
- the principal Paper 3 consistency, public-claim, and defect-injection tests.

The current merge commit changes 86 files relative to its two parents and records 11,032 additions and 1,050 deletions across the combined papers and card intake. The Paper 3 manuscript itself changed by 167 additions and 51 deletions relative to the preceding reviewed state.

### 2.2 Verification boundary

The merged PR reports **2,080 tests passed, one skipped, and no failures**, together with **65 passing gates and one acknowledged exception**, and zero unaccounted claims in the three paper-coverage audits. I inspected the relevant code, tests, manuscript blocks, and generated artifacts, but I did **not** independently rerun the full clean-environment suite. The reported project-wide test result should therefore be understood as the repository's merge record, not as an independently reproduced result of this review.

I did perform targeted local schema counterexamples against the reviewed `PublicClaim` implementation. These were deliberately minimal and did not require the full repository:

| Counterexample | Expected under the manuscript's stated architecture | Actual `validate()` result |
|---|---|---|
| A component-dependent claim with no `evidence_selections` | reject as unscoped | accepted |
| Select a real evidence ID about pump-outlet pressure for a claim about outlet caffeine concentration in an unrelated campaign | reject as semantically incommensurate | accepted |
| Set top-level public `evidence_strength="independent"` while selecting only code-verification evidence | reject or derive the public relation from the selection | accepted |

The first case also returned the component's entire evidence inventory from `evidence_profile()`, confirming that the old inheritance behavior survives as a fallback.

### 2.3 Interpretation of “implemented” in this review

I distinguish four states that the manuscript occasionally merges:

1. **represented:** a field exists;
2. **identified:** a stable ID joins two records;
3. **validated:** a machine-executable rule tests the relation between them; and
4. **scientifically established:** the rule itself has been evaluated on meaningful positive and negative cases.

The current revision has moved claim evidence from state 1 toward state 2. It has not yet fully reached state 3 for semantic commensurability, and the mutation suite is an initial state-4 exercise rather than comprehensive evaluation.

---

## 3. Change audit against the preceding review

### 3.1 What has been corrected well

The revision directly addresses much of the preceding review:

- `ClaimEvidenceSelection` now identifies a dependency and exact evidence-link IDs, records a claim observable and domain, assigns a role in the claim, and includes a rationale.
- The component evidence inventory remains available for drill-down while selected evidence is exposed separately.
- `derive_badge()` now exists, returns a badge, rationale, and limiting dependency, and is tested against deliberate badge inflation.
- The former evidence-ordering contradiction has largely been removed.
- The scorecard's producer is now named in the ownership table.
- Contract schema references are aligned to schema 0.8, and fines-provenance fields are included.
- Mean-trace and shot-level temporal metrics are separated.
- Defects and controls are separated, and the invalid 67% coverage claim is withdrawn.
- `PressureNode`, `PressureTrace`, and `require_node` address the real recorded-trace boundary problem.
- The manuscript is clearer about a direct-version environment lock, absent DOI, remaining metadata, ethics determination, archival release, and clean-room reproduction.
- Blocked and proposed evidence states now map to indeterminate outcomes rather than silently becoming supported.

These changes are substantive. They should be retained.

### 3.2 Where the implementation remains partial

The action tracker describes several items as fully implemented where a narrower description would be more accurate:

| Previous item | Current status after re-audit |
|---|---|
| Claim-scoped evidence selection | **Partly implemented.** Exact IDs and dependency ownership are checked; observable/domain/campaign/dataset compatibility is not. Empty selections still fall back to inventory. |
| Badges derived, not authored | **Partly implemented.** A derivation exists and mismatch is rejected by `validate()`, but `badge` remains a required constructor field and export does not enforce validation. |
| Mutation benchmark recast | **Conceptually improved, reporting regression remains.** Defects and controls are separate in the result object; the manuscript class table is stale. |
| Pressure-node correction | **Core local contract added.** The scorecard text is stale and legacy generic trace paths remain untyped unless callers opt into `PressureTrace`. |
| Appendix B narrowed | **Partly implemented.** The block still states that every manuscript-facing quantitative claim is exportable and still misstates numeric generation and derived fields. |
| Readiness reconciled | **Improved but incomplete.** The manuscript still has placeholders, stale generated content, and a “four blockers” sentence followed by five items. |

### 3.3 New defects introduced or exposed by the revision

The current revision also exposes several new issues:

- the inline Appendix A did not receive the two Maille components present in the generated catalog;
- the defect class table was not generated from the revised benchmark result;
- the public generated claim artifact remains stamped at an intermediate commit;
- the newly added claim-observable and claim-domain strings create an appearance of semantic validation without a corresponding compatibility rule;
- public exports now contain rich JSON selections but the more visible Markdown and CSV surfaces omit them.

These should be presented in the paper as useful evidence from continued self-application of the architecture.

---

## 4. Publication-blocking comments

## P0-1 — The manuscript's “producer-generated and CI-guarded” sections have demonstrably drifted

### Finding

The manuscript states that Table 1 and Appendix A are producer-generated and that CI fails on drift. The generated catalog correctly states that the registry contains 27 components. The inline Appendix A contains only 25 rows and omits:

- `maille2024.two_regime`
- `maille2024.phi_closure`

The defect-injection class table is also stale. The current benchmark metadata imply the following defect-only table:

| defect class | detected | injected |
|---|---:|---:|
| evidence | 2 | 3 |
| numeric consistency | 1 | 1 |
| observable semantics | 4 | 4 |
| physical value | 0 | 1 |
| prose drift | 2 | 2 |
| provenance | 3 | 4 |
| unit | 1 | 3 |
| **Total** | **13** | **18** |

The manuscript instead reports observable semantics as 2/3 and unit as 2/4. The latter reintroduces exactly the denominator problem the text says was corrected: a valid unit control is still represented as though it were an injected unit defect.

### Cause

`registry_artifacts.verify()` checks the files under `docs/paper3_resource/generated/`; it does not splice or compare the inline manuscript Appendix A. The manuscript consistency tests bind headline counts and selected prose claims, but not the exact ordered membership of Table A1. The defect tests bind aggregate totals but do not bind the manuscript's per-class table.

### Why this matters

This is not a minor copy-edit. Drift prevention is a principal empirical claim of the paper. A reviewer can point to the manuscript itself as a counterexample. The correct response is not to hide the incident but to use it as a strong demonstration of why duplicated generated material needs a single build path.

### Required action

1. Put the inline Appendix A inside explicit generated markers and splice it from the live registry, or remove the duplicate inline table and include the generated file at manuscript build time.
2. Generate Table 6a from `run_benchmark()`; do not hand-maintain its cells.
3. Add an exact-set test:
   - `set(inline_appendix_ids) == set(live_registry_ids)`;
   - preserve deterministic order if order is claimed.
4. Add a test that parses Table 6a and compares each row with `by_family`, excluding controls from the injected denominator.
5. Add deliberate regression tests: register a synthetic component and alter one defect's class, then prove both manuscript blocks fail verification until regenerated.
6. Disclose this drift episode in the manuscript's self-evaluation section. It is valuable evidence.

### Acceptance criterion

A single command regenerates the live registry artifacts, inline Table 1, inline Appendix A, defect summary table, and any associated counts; a clean verification command compares every generated block byte-for-byte or semantically; adding a component or changing a defect classification makes CI fail until all affected blocks are regenerated.

---

## P0-2 — Evidence selection proves identity, not scientific commensurability

### Finding

`ClaimEvidenceSelection` records `claim_observable`, `claim_domain`, and a rationale, but its own validator checks only that the strings are non-empty and that the role is in a controlled vocabulary. `PublicClaim.validate()` verifies that an evidence ID exists and belongs to the named dependency. It does not compare:

- claim observable with evidence scope;
- quantity kind or species basis;
- units or reference volume;
- pressure node or reference location;
- dataset or experimental campaign;
- fit and evaluation dataset roles;
- observation operator;
- time window;
- validity range; or
- required adapters.

A targeted counterexample selected a real code-verification record scoped to “pressure at pump outlet” for a claim whose observable was “caffeine concentration at outlet” and whose domain was an unrelated campaign. `validate()` returned no errors.

### Why this matters

The abstract says that a claim “selects the records whose observable and domain match its own assertion.” In the current implementation, the author writes that the observable and domain match. The architecture checks that the chosen ID is real; it does not check the match. That is still useful provenance, but it is not the executable semantic constraint claimed by the paper.

### Required action

Introduce a structured support edge rather than free-text semantic declarations. At minimum, the selected evidence record should expose or reference:

```yaml
evidence_id: component::gate
observable_id: mass_flow.outlet
quantity_kind: mass_flow_rate
species_basis: total_beverage
unit: kg/s
reference_location: basket_outlet
pressure_node: null
campaign_ids: [waszkiewicz2025_9bar]
fit_dataset_ids: [...]
evaluation_dataset_ids: [...]
time_window_s: [15, 95]
observation_operator_id: beverage_mass_derivative_v1
domain_contract_id: ...
```

The claim support edge should then declare its claim-side values and either:

- pass an exact/compatible comparison, or
- name an explicit typed adapter that transforms one representation to the other.

Free-text rationale should remain as explanation, not as the mechanism of enforcement.

### Required tests

Add failing cases for:

1. correct evidence ID, wrong observable;
2. correct observable name, wrong quantity kind;
3. correct quantity, wrong species or concentration basis;
4. correct pressure magnitude, wrong pressure node;
5. correct observable, wrong campaign or evaluation dataset;
6. fit data misrepresented as held-out evaluation data;
7. correct dataset, incompatible time window;
8. compatible values connected through a declared adapter; and
9. semantically compatible evidence with different harmless prose wording.

### Acceptance criterion

The counterexample above fails because of a structured incompatibility, not because a string differs. A compatible selection passes even when its prose rationale is reworded. The manuscript distinguishes exact identity from semantic compatibility and claims only the checks actually implemented.

---

## P0-3 — Empty selections preserve the old whole-inventory inheritance path

### Finding

`evidence_profile()` returns selected evidence when selections exist and otherwise returns the full component evidence inventory. `PublicClaim.validate()` validates individual selections only inside `if self.evidence_selections`; it does not reject a component-dependent claim with no selections. A minimal component-dependent claim with a correctly mapped numeric producer, no selections, and an exploratory badge validated cleanly and exposed the entire component evidence inventory as its profile.

This contradicts both the schema comment—“empty means the claim has not yet been scoped, which `validate()` reports”—and the manuscript's central assertion that a claim does not inherit a component's whole evidence inventory.

### Required action

1. Remove the implicit fallback:
   - `evidence_inventory()` returns inventory;
   - `selected_evidence()` returns selection;
   - `evidence_profile()` should either mean selection only or be removed as an ambiguous alias.
2. Require a selection for every component dependency whose role is:
   - `produces_reported_value`,
   - `diagnosed_subject`, or
   - `comparator_context` when the comparator supports an interpretation.
3. Permit no selection only for genuinely dataset-only or producer-only observed claims, with that state explicit.
4. Treat an unscoped component dependency as a validation error, not merely as a reason to derive an exploratory badge.
5. Add a migration state if needed, such as `scope_status: unresolved`, but do not silently expose inventory as claim support.

### Acceptance criterion

A component-dependent claim with an empty selection fails validation; serializing it cannot emit the component inventory under a field called `evidence_profile`; and no public badge or public evidence summary can be produced until the selection is resolved or the dependency is explicitly marked context-only and non-licensing.

---

## P0-4 — The public `evidence_strength` field remains authored, ungrounded, and semantically lossy

### Finding

`PublicClaim.evidence_strength` remains a mandatory authored string. Validation checks vocabulary membership but does not derive it from selected evidence or reject contradiction with selected records. A targeted counterexample set the public field to `independent` while selecting only a `code_verification` record; validation returned no error.

The public mapping also collapses scientifically material distinctions:

- `controlled_independent` and `within_campaign_held_out` both become `independent`;
- `post_fit_reconstruction` and `source_curve_reproduction` both become `post-fit reconstruction`.

The manuscript repeatedly argues that these distinctions should remain visible. A single public scalar reverses that design at the final presentation layer.

### Required action

Replace the authored scalar with one of the following:

- a derived set of selected evidence relations and evaluation designs; or
- a deliberately named `public_relation_summary` computed from selected evidence, with an explicit lossy mapping and a visible detail record.

At minimum, distinguish:

- independent external evaluation;
- held-out data from the same campaign;
- same-campaign but non-held-out evaluation;
- post-fit reconstruction;
- source-curve reproduction;
- code verification; and
- non-empirical or qualitative compatibility.

Do not call same-campaign holdout “independent” without the qualifier “held out within the same campaign.”

### Acceptance criterion

Editing a public relation to a stronger term cannot pass validation; the relation summary is recomputed from selected evidence; and the public output preserves the evaluation-design distinction on which the badge and scientific verb depend.

---

## P0-5 — Badge derivation is useful but is not yet genuinely non-authored or orthogonal to outcome

### Finding

The new `derive_badge()` function is a real improvement, but two problems remain.

First, `badge` is still a required `PublicClaim` constructor field. The seeded claims hard-code it, and `validate()` checks whether the authored value agrees with the derived value. This is a consistency check, not a derived field in the normal data-model sense. More importantly, `export()` does not call `validate()` before writing; an invalid authored badge can therefore be serialized by the exporter.

Second, the derivation collapses outcome into generation/evaluation mode. Any selected negative or indeterminate evidence causes `EXPLORATORY_SIMULATION`. A failed held-out prediction is still a **prediction** with a **negative outcome**. Reclassifying it as an exploratory simulation removes the failure from the category in which it occurred. The manuscript otherwise insists that outcome is orthogonal to relation.

### Required action

1. Remove `badge` from authored claim initialization. Make it a computed property or serializer output.
2. Separate at least:
   - **value origin / generation mode:** observed, reconstructed, predicted, exploratory simulation;
   - **evaluation outcome:** supported, negative, indeterminate; and
   - **evaluation design:** fit data, same campaign, held out same campaign, independent external, verification, non-empirical.
3. Do not let a negative outcome change the value-origin badge.
4. Require `validate()` before every JSON, CSV, Markdown, figure, and Appendix B export.
5. Include derivation rationale and limiting dependency in all public records.

### Acceptance criterion

A negative held-out prediction serializes as, for example, `mode: PREDICTED` and `outcome: NEGATIVE`; no caller can supply a badge independently; and every export path refuses an invalid claim before writing files.

---

## P0-6 — Dataset and campaign lineage are present upstream but lost before claim validation

### Finding

The evidence graph's source records carry structured dataset IDs, evidence roles, source independence, and fit/evaluation relationships. `ScopedEvidence` and `ScopedEvidenceRef` reduce these records to relation, scope, gate, outcome, fit/evaluation label, and a reality-facing flag. Dataset IDs and their roles are not carried into the public selection.

Consequently, `dataset_manifest_ids` is only checked for existence. The architecture cannot prove that:

- the selected evidence was evaluated on a dataset listed by the claim;
- the claim's “held-out” dataset was not also a fit input;
- the selected campaign matches the claimed domain; or
- a named source dataset actually participates in the producer path.

The public claim definitions also show mismatches between `dataset_manifest_ids` and authoritative dependencies. For example, the measured cup-mass basis of the response-surface claim is listed among dataset IDs but is not represented as a load-bearing dependency in the same way as the response-surface coefficient dataset.

### Required action

1. Preserve source-edge information on the public evidence reference:
   - dataset ID;
   - role (`fit`, `eval`, `reference`, `context`);
   - campaign ID;
   - source independence;
   - transform/observation-operator ID.
2. Make `dataset_manifest_ids` derived from dependencies and selected evidence rather than an independent list.
3. Validate that every claim dataset is connected to either:
   - a producer input;
   - a selected evidence source; or
   - an explicitly context-only dependency.
4. Reject a held-out label when fit and evaluation source sets overlap unless the design explicitly permits it.
5. Add a graph audit for orphan claim datasets and undeclared producer inputs.

### Acceptance criterion

The public record can answer, mechanically, “which dataset produced the number, which dataset evaluated it, whether those datasets overlap, and which transformation connected them.” Changing an evaluation dataset to an unrelated manifest row fails validation even though the row exists.

---

## P0-7 — Numeric results are authored snapshots verified within tolerance, not producer-emitted values

### Finding

The manuscript and source comments repeatedly state that numeric results are producer-generated and never hand-entered. In the actual export path:

1. each claim contains a hard-coded `numeric_result` snapshot;
2. the producer is executed;
3. numeric live values are compared with the snapshot using `max(1e-3, 0.5% of snapshot)`;
4. only larger differences are recorded as drift; and
5. the exporter deliberately retains and writes the authored numeric snapshot.

This is a reasonable display-snapshot verification design, but it is not what the manuscript says. The tolerance is also not tied to declared display precision. A condition number recorded as 1,927 can differ by roughly 9.6 before the generic 0.5% guard reports drift, even though the displayed integer may have changed materially depending on rounding policy.

### Required action

Choose and document one of two honest designs:

**Preferred design: producer is canonical.**

- producer output is the stored value;
- formatting and rounding occur only at render time;
- each numeric key declares display precision or significant figures;
- snapshots are generated artifacts, not source literals.

**Alternative design: snapshot is canonical presentation.**

- call it an authored, display-rounded snapshot;
- verify it against live producer output with a key-specific precision contract;
- remove “never hand-entered” and “every number is generated” claims.

In either design, use absolute/relative tolerances derived from the stated precision, not a global 0.5% heuristic.

### Acceptance criterion

For every numeric key, a reviewer can identify the canonical live value, display transformation, precision, and allowable comparison error. Editing a snapshot within an arbitrary 0.5% window cannot silently change the public number.

---

## P0-8 — Commit provenance is not persistent or current

### Finding

`generated_from_commit` is described as immutable and `last_verified_against_commit` as mutable. In memory, the exporter stamps `generated_from_commit` only when it is `None`. However, claims are reconstructed from source with `None` in each fresh process; the previous artifact is not read to preserve its original generation commit. “Immutable” therefore applies only during one Python object lifetime unless another process supplies persisted metadata.

The committed `docs/public/generated/claims.json` is stamped:

- `generated_from_commit = 99ea79f...`
- `last_verified_against_commit = 99ea79f...`

The reviewed repository state is `352dacd...`. The artifact may contain numerically unchanged values, but it has not recorded verification against the reviewed merge state.

### Required action

1. Persist provenance independently of reconstructed source objects.
2. Give each exported payload a content hash and producer-input hash.
3. On verification, read the prior artifact:
   - preserve its generation commit only if payload identity is unchanged;
   - update the verification commit after all checks pass;
   - create a new generation commit when the payload changes.
4. Regenerate or verify all public artifacts at the frozen manuscript commit.
5. Include a release manifest that binds manuscript, claims, figures, tables, environment lock, and code commit.
6. Refuse export from a dirty tree unless explicitly producing an unreleaseable development artifact.

### Acceptance criterion

A fresh process cannot reset historical provenance accidentally; the committed public artifacts record `last_verified_against_commit = 352dacd...` or the final frozen release commit; and payload hashes make generation and later verification independently auditable.

---

## P0-9 — The named-shot scorecard still performs component-level evidence roll-up

### Finding

The scorecard is now producer-generated, which corrects a prior ownership error. However, `_status_for()` still obtains the whole scoped evidence vector for a component and concatenates its relation labels. It does not select records for the scorecard row's exact observable, dataset, conditions, pressure node, or intended use. Outcomes are present in the hidden evidence payload but are not clearly represented in the displayed status.

The machine-boundary caveat is also stale. It says node identity “is documented in prose but is not a typed contract field.” Schema 0.8 now contains `PressureNode`, `PressureTrace`, and `require_node`. The actual shot-specific problem is that the recorded trace's node has not yet been established or wrapped with that typed identity.

The count of open stages is also fragile because it counts only statuses exactly equal to `open`; a combined status string that contains an unresolved record can escape the open count.

### Required action

1. Treat each scorecard row as a claim-support record with:
   - stage observable;
   - selected component/input;
   - exact evidence IDs;
   - dataset/campaign IDs;
   - node and unit contracts;
   - relation, design, and outcome separately;
   - explicit exclusions;
   - open requirements.
2. Derive displayed status from the row's selected evidence, not the component inventory.
3. Replace the machine caveat with: the contract type exists, but the source trace's node identity remains unresolved.
4. Model open state as a structured boolean/enum rather than parsing a presentation string.
5. If two extraction branches are deliberately listed, describe them as separate observables or sub-stages rather than violating the stated one-component-per-stage rule.

### Acceptance criterion

Adding an unrelated strong evidence record to a scorecard component cannot alter any stage status. A wrong-node trace fails before scoring. Every displayed status links to exact selected evidence and exposes negative or indeterminate outcome rather than flattening it into a relation string.

---

## P0-10 — Appendix B still overclaims schema coverage and misrepresents the exported record

### Finding

The generated Appendix B still opens with “Every manuscript-facing quantitative claim is exportable as the record below.” Later readiness text says selection has not been extended to every generated claim class and that no unified cross-class coverage registry exists. Both statements cannot be true.

Additional problems include:

- `numeric_result` is described as producer-generated and never hand-entered, contrary to the snapshot export path;
- `badge` is described as derived even though it is required in the authored object;
- `generated_from_commit` is described as immutable despite the process-local behavior described above;
- “outcome, artifact role and scope are recorded” is not accurate because no explicit authoritative artifact/model-role field appears on `ScopedEvidenceRef`;
- the table caption calls the fields a “stage contract” although the object is a public claim record;
- the examples omit the newly important dependencies, selections, outcome, derived rationale, and limiting dependency;
- example caveats are truncated mid-word;
- the negative example selector searches the legacy evidence relation rather than the new `outcome` field and succeeds only by list ordering when no match is found.

### Required action

1. State the precise covered population, for example: “Every claim in `PUBLIC_CLAIMS` is exportable; other manuscript claim classes use separate producers and coverage audits.”
2. Generate a cross-class coverage table listing each manuscript quantitative claim, producer, schema, artifact, and audit status.
3. Correct field obligations to match implementation.
4. Render complete examples, including:
   - dependencies;
   - selected evidence IDs;
   - claim observable/domain;
   - outcome;
   - derived badge rationale;
   - limiting dependency;
   - generation and verification commits.
5. Select the negative example by `outcome == "negative"`, not by a legacy compound relation or fallback ordering.
6. Remove arbitrary string truncation from a normative schema example.

### Acceptance criterion

Appendix B can be generated from the current schema without false universal claims, truncation, or omitted load-bearing fields, and its coverage statement agrees with the readiness section and claim-coverage audits.

---

## P0-11 — The most visible public exports discard the evidence-selection architecture

### Finding

The JSON export contains dependencies, evidence inventories, selections, and outcomes. The CSV and Markdown claim cards retain only a top-level evidence-strength string and badge. They omit:

- exact selected evidence IDs;
- claim observable and domain;
- relation and evaluation design per selected record;
- outcome;
- deliberate exclusions;
- badge rationale;
- limiting dependency;
- distinction between generation and verification commits.

The Markdown preamble also says evidence-strength labels are carried “UNCHANGED,” although the schema documents a many-to-one mapping from registry relations to public labels.

### Why this matters

For most readers, the Markdown cards or CSV will be the public surface. Those surfaces currently erase the paper's main methodological contribution and recreate the single-label presentation the paper criticizes.

### Required action

1. Add one row per claim–evidence selection to a normalized CSV.
2. Render a compact evidence table on every Markdown claim card.
3. Show mode, outcome, evaluation design, and limiting dependency separately.
4. Link to full evidence inventory without allowing it to count as claim support.
5. Correct the “unchanged” statement to describe the explicit lossy mapping.
6. Include both generation and verification provenance.

### Acceptance criterion

A reader using only the generated Markdown or CSV can identify exactly which evidence licenses a claim and which evidence is merely contextual. The public surface no longer depends on one scalar evidence label.

---

## P0-12 — Correct the mutation-suite class table and narrow the “production guard” claim

### Finding

The benchmark result structure is substantially better than before, but the manuscript's class table is wrong. The current case metadata yield:

| class | true positives | defects | controls | false positives |
|---|---:|---:|---:|---:|
| evidence | 2 | 3 | 0 | 0 |
| numeric consistency | 1 | 1 | 0 | 0 |
| observable semantics | 4 | 4 | 1 | 0 |
| physical value | 0 | 1 | 0 | 0 |
| prose drift | 2 | 2 | 0 | 0 |
| provenance | 3 | 4 | 0 | 0 |
| unit | 1 | 3 | 1 | 0 |

The total remains 13 of 18 defects caught, with two controls correctly accepted.

The phrase “15 executable mutations that perturb a real input and run the production guard” is also too broad. Several cases are useful but are not end-to-end production mutations:

- manuscript phrase or cross-reference sentinels;
- manually recreated vocabulary predicates;
- direct string comparisons between manuscript and generated values; and
- policy/consistency checks that do not traverse the same public export or validation path a real defect would traverse.

Finally, the nine “independent structural groups” are author-assigned group labels. They are a reasonable de-duplication device, but independence has not been demonstrated statistically or causally.

### Required action

1. Generate the class table directly from the result object.
2. Use categories such as:
   - `production_path_mutation`;
   - `integration_regression_sentinel`;
   - `static_manuscript_check`;
   - `limitation_analysis`;
   - `valid_control`.
3. Replace “independent structural groups” with “declared structural families” unless independence is established.
4. Report control coverage by family; two controls do not establish general specificity.
5. Add a held-out mutation set designed by someone other than the guard author.
6. Mutate actual stored records and invoke the actual public validation/export path for claim-semantic cases.

### Acceptance criterion

Every table cell is generated from the benchmark object; execution types describe the path actually exercised; controls are never included in defect denominators; and claims about production-path detection are limited to cases that traverse production code.

---

## 5. Additional major comments

## P1-1 — The manuscript names an artifact/model-role axis that is not represented as one authoritative field

Section 5 describes evidence relation, outcome, and artifact/model role as three authored axes. The public evidence record contains `fit_evaluation` and `reality_facing`, but no explicit controlled artifact/model-role field matching the prose. `role_in_claim` belongs to the claim–dependency edge and answers a different question. Either add the advertised axis or rewrite the manuscript to describe the fields actually present.

## P1-2 — `sign_or_compatibility` is semantically overloaded

The relation is used for positive sign checks, compatibility checks, and sometimes negative outcomes. Its definition should make clear that it is a comparison design whose outcome can be supported, negative, or indeterminate. Do not define it only through failure language.

## P1-3 — Claim ownership contradicts the statement that Paper 3 asserts only methodological claims

The claim-ownership table assigns Paper 3 primary responsibility for several scientific results, including timescale portability and composition behavior. Later prose says the paper asserts only methodological claims. Decide between:

- a methods paper that uses scientific results strictly as demonstrations and sends substantive interpretation to companion papers; or
- a methods-and-domain paper that owns selected scientific results.

The current hybrid creates citation and novelty ambiguity.

## P1-4 — “One component per occupied runtime stage” is not true of the named configuration

The scorecard contains two extraction branches because they address different extraction observables. That can be scientifically defensible, but it is not one component per stage. Replace the cardinality rule with a rule over **stage–observable slots** or explicitly allow parallel diagnostic branches.

## P1-5 — The pressure-node migration is local rather than universal

`PressureTrace` and `require_node` are good additions. Legacy `MachineState` callbacks and bare arrays remain available, so the architecture still depends on callers choosing the typed path. Document the migration boundary, deprecate ambiguous public APIs, and add adapter-level enforcement at every node-specific consumer.

## P1-6 — “Beyond reconstruction” implies an evidence ordering the manuscript rejects

The corpus denominator describes 9 of 27 components as having evidence “beyond reconstruction.” This reads as an ordinal hierarchy, while the evidence section argues that relations answer different questions. Use explicit categories: externally evaluated, held-out same campaign, reconstructed, reproduced, verified, qualitative, proposed, or unresolved.

## P1-7 — Dataset-source counts should not be read as independent campaigns

A count of manifest sources or rows is not a count of independent experiments. Distinguish logical manifest records, unique source documents, experimental campaigns, rigs, coffees, and genuinely independent evaluation datasets.

## P1-8 — Generate claim ownership from one structured source

The ownership table has improved, but it remains a manually synchronized interpretive table. Represent claim owner, manuscript use, producer, and destination in a structured registry and generate both manuscript and repository views. This is particularly important because the paper itself uses claim ownership to delimit companion-paper overlap.

## P1-9 — Add a related-work feature matrix

The related-work prose is thoughtful but still lacks a compact comparison with model registries, workflow/provenance systems, model cards, executable papers, semantic data standards, and validation frameworks. A feature matrix would clarify the novelty: not generic provenance, but claim-scoped scientific evidence with negative composition results and typed observable boundaries.

## P1-10 — Complete the reference audit for model lineages 7–9

The current paper cites foundational and imported models, but the relationship among source publication, thesis, later paper, digitized curves, and repository port should be explicit. Each demonstration should identify the primary source for equations, source for parameters, and source for evaluation data separately.

## P1-11 — The fast/slow portability demonstration still needs identifiability and radius sensitivity

The revised interpretation is better, but publication-quality treatment should show:

- the fitting objective and time window;
- parameter uncertainty or profile likelihood;
- one- versus two-constant model comparison;
- sensitivity to particle radius, especially because diffusion times scale approximately with radius squared;
- results for the coarse class as well as the selected 20 μm-radius fine class; and
- the distinct Cameron coarsest-setting fit, which returns two separated constants rather than a universal one-regime result.

Use “one physical diffusion process” rather than “single diffusion mode”; a spherical diffusion solution contains multiple mathematical modes.

## P1-12 — Keep the temporal-flow inference within the demonstrated domain

The shot-level result is useful: the temporal branch beats the constant baseline on all five shots. It does not show superiority to the flexible cubic reference and does not establish external generalization beyond the one campaign. Report paired per-shot differences and uncertainty, avoid treating five correlated shots as five independent external validations, and keep the mechanism claim at “time variation is needed under this observation model.”

## P1-13 — The composition failure does not isolate the cause

The failed shared-porosity composition is a strong negative result for that declared configuration. It does not isolate parameter scaling from initial-state mapping, reference-volume normalization, boundary conditions, observation operator, or coupling rule. Replace causal language with a list of plausible failure locations and, ideally, an ablation matrix.

## P1-14 — Distinguish availability from independent reproducibility

A public repository, runnable notebook, direct-version lock, and generated artifacts improve accessibility. They do not by themselves establish independent reproduction. Retain separate labels for available, executable by maintainers, clean-checkout verified, independently reproduced, and archived.

## P1-15 — Freeze project-wide test and gate evidence as release artifacts

PR prose is not a durable scientific record. Store machine-readable test/gate summaries, environment metadata, commit, timestamps, hashes, and acknowledged exceptions in the release bundle. The manuscript should cite that artifact rather than a moving pull request description.

## P1-16 — The environment lock should be described exactly

The action tracker correctly calls `requirements-paper-release.lock` a direct-version lock, not a transitive lock or container digest. Preserve that precision everywhere. For a citable release, add either a fully resolved lock with hashes or a container/environment digest and test it in a clean environment.

## P1-17 — The abstract is too long and carries implementation detail better placed in the methods

The current abstract is approximately 500 words. It contains valuable nuance, but the central contribution is obscured by schema qualifications and multiple result bases. Target the selected journal's limit, likely 200–300 words, and retain only:

- the interoperability problem;
- the executable-registry method;
- three demonstrations;
- the negative composition result; and
- the bounded contribution.

## P1-18 — The manuscript is long for its present publication identity

At roughly 20,000 words before a final submission package, the draft reads partly as a paper, partly as a repository audit, and partly as a release dossier. Move complete component catalogs, implementation matrices, mutation case details, claim-schema examples, and release checklists to supplements. Keep the main paper focused on architecture, evaluation, and scientific demonstrations.

## P1-19 — Resolve remaining front-matter and readiness placeholders

Authors, affiliations, corresponding author, release version, archive DOI, access date, ethics determination, and citation metadata remain unresolved. The draft date also remains 25 July despite substantive 27 July changes. These are appropriately listed as blockers, but the manuscript should not approach external circulation until the front matter identifies the work unambiguously.

## P1-20 — Correct “four blockers” followed by five enumerated items

The readiness section introduces four remaining blockers and then lists five. This is small but conspicuous in a paper about executable consistency. Generate the count from the list or avoid a numeric count.

## P1-21 — `outcome` needs a precise subject

It is unclear whether claim-level `outcome` describes the truth status of the public claim, the result of an evidence check, or the result of the model evaluation. Evidence-link outcomes and claim outcomes may differ. Define subjects explicitly, for example `evidence_check_outcome`, `claim_assertion_status`, and `evaluation_result`.

## P1-22 — The public mapping should be presented as a view, not an evidence model

The registry relation, fit/evaluation design, outcome, role, and source independence are the evidence model. A lay-facing mapped phrase is a presentation view. Presenting `evidence_strength` as a primary claim field encourages consumers to treat it as authoritative when it is the least detailed representation.

## P1-23 — Complete the migration away from `negative validation` as an evidence relation

The public evidence vocabulary still includes `negative validation` even though the same module correctly describes it as a legacy compound of relation and outcome and new validation rejects it. An entry should not simultaneously be advertised as an allowed evidence strength and prohibited for new claims. Decide an artifact-migration policy, convert legacy records to a relation plus `outcome: negative`, version the public schema, and remove the compound term from the active vocabulary.

---

## 6. Cross-layer consistency audit

| Layer | What it represents well | Remaining loss or contradiction | Required correction |
|---|---|---|---|
| Registry component | stage, execution role, provenance class, component evidence category, gates | component-level label can still be over-read as applying to every output | describe as navigation metadata; do not use as claim evidence without scoped links |
| Evidence-link source record | dataset IDs, source roles, independence, relationship, claim, observable, caveat | rich structure is not fully propagated to public claims | preserve structured source lineage on the support edge |
| `ScopedEvidence` / `ScopedEvidenceRef` | stable ID, relation, scope, gate, outcome, evaluation design | drops source datasets, roles, campaign, quantity kind, units, node, operator | extend record or reference a canonical evidence object |
| `ClaimEvidenceSelection` | exact dependency and evidence IDs, claim-side text, role, rationale | observable/domain are unchecked prose; empty selection permitted | validate structured compatibility and require selection |
| `PublicClaim` | producer identity, numbers, units, caveat, validity, dependencies | authored scalar relation, authored badge, independent dataset list, snapshot numbers | derive presentation fields; derive dataset list; make live output canonical |
| Badge derivation | conservative handling of missing and non-empirical evidence | negative outcome changes generation-mode badge | keep mode and outcome orthogonal |
| Public JSON | exposes most dependency and selection details | can serialize without global validation; provenance stale | validate before export; persist provenance |
| Public CSV/Markdown | accessible human-facing views | omits selections, outcomes, rationale, limiting dependency | render normalized support edges and derivation |
| Named-shot scorecard | generated row and executed values | status uses whole component inventory | make each row a claim-scoped support record |
| Manuscript generated blocks | clear reader-facing summaries | Appendix A and Table 6a have drifted | one build source and exact block verification |
| Defect benchmark | separate controls, defects, limitations, families | stale class table; mixed execution types; no holdout | generate reporting and add independent challenge set |

The most important conclusion is that Puckworks now has a strong **evidence inventory and exact-ID join**, but not yet a complete **claim–evidence compatibility relation**. The paper should use those terms consistently.

---

## 7. Quantitative and scientific consistency audit

### 7.1 Registry and manifest inventory

The headline registry count of 27 components and manifest count of 107 logical records are consistent with the current generated summary. The execution-role framing is improved and no longer treats synthesis as an execution role. The inline Appendix A membership, however, is inconsistent with the same 27-component count and must be regenerated.

### 7.2 Mean-trace and shot-level temporal results

The manuscript now correctly distinguishes two estimands:

- scores against a preprocessed mean trace over 15–95 s; and
- scores obtained by applying the same branches to the five individual shots.

The scientific conclusion supported by the current evidence is:

- a time-varying branch improves over the constant baseline on all five shots in this campaign;
- absolute shot-level errors are larger than the mean-trace diagnostic error; and
- the flexible cubic remains an important non-mechanistic comparator.

The result does **not** yet establish external prediction, causal identification of a bed mechanism, or superiority over the cubic comparator.

### 7.3 Shared-porosity composition

The central negative result remains coherent: adding the imported swelling branch to the declared shared-porosity composition worsens reconstruction of the selected mean trace relative to the extraction-only branch and the constant baseline. The correct inference is that the **declared composition fails under the selected mapping and observation operator**. The result neither invalidates swelling nor proves the extraction-only branch mechanistically correct.

The paper would benefit from a small ablation table covering:

- sign convention;
- initial porosity;
- saturation/pre-wet state;
- reference volume;
- mapping from swelling state to shared porosity;
- boundary condition;
- observation operator; and
- parameter refitting versus no refitting.

### 7.4 Fast/slow portability

Retain the demonstration, but present it as a semantic and identifiability example rather than a resolved physical comparison. Absolute time constants vary across grind settings; only selected ratios or weights may remain stable under the fitted protocol. The selected fine-particle radius is load-bearing because of radius-squared diffusion scaling. The coarse-class comparison and fit uncertainty should be reported before using the example as a general statement about model incompatibility.

### 7.5 Forchheimer and named-shot interpretation

The corrected Forchheimer-number expression from the previous revision should remain. The named-shot use must continue to be described as a same-shot compatibility calculation using measured pressure and fitted permeability, not an independent prediction. The pressure node of every input trace should be established before the result is used quantitatively.

### 7.6 Defect-suite totals

The aggregate total—13 of 18 defects caught, two controls accepted—is internally consistent with the current case metadata. The manuscript's per-class decomposition is not. Because the paper emphasizes class-specific gaps rather than a single rate, the class table is at least as important as the aggregate total and must be canonical.

---

## 8. Detailed assessment of the defect-injection suite

### 8.1 What the suite does well

- It keeps missed cases rather than reporting only successful guards.
- It distinguishes valid controls from defects.
- It records why a miss occurs and what architectural change would be required.
- It identifies a genuine limitation of broad numeric range checks for unit errors.
- It includes semantic errors, provenance drift, physical-value errors, and manuscript drift rather than only software exceptions.
- It no longer reports a pseudo-statistical coverage percentage.
- It creates a practical regression corpus from errors encountered during development.

### 8.2 Case-family interpretation

**Unit family.** D01 and D02 are two scale factors of the same broad-range-guard limitation. D03 is a gross-unit case the guard catches. D04 is a valid control. The family therefore contains three defects, one caught, and one accepted control—not four injected defects and two catches.

**Observable-semantics family.** The fines-threshold cases and pressure-node cases are distinct subfamilies but all concern semantic compatibility. D18 and D20 are now caught, and D19 is a valid pressure-node control. The current defect total is four of four caught, with one control accepted.

**Prose-drift and numeric-consistency families.** These are valuable release regressions. They should be labelled as manuscript/build sentinels rather than universal evidence-architecture tests.

**Evidence and provenance families.** Some cases invoke actual repository reconciliation; others reproduce a condition locally. The benchmark should distinguish those execution paths.

**Physical-value family.** The missed plausible-but-wrong porosity is the most important open scientific limitation. Dimensional and range validity cannot establish source correctness. Closing it requires source-bound parameter provenance, not merely tighter generic contracts.

### 8.3 Missing high-value mutations

Add at least the following:

1. correct evidence ID selected for the wrong observable;
2. correct evidence ID and observable selected for the wrong campaign;
3. fit dataset relabelled as held-out evaluation;
4. claim dataset exists but is disconnected from producer and evidence;
5. correct pressure node but wrong gauge/absolute pressure convention;
6. concentration matched across incompatible reference volumes;
7. named-solute yield aggregated with total dissolved solids;
8. negative held-out prediction relabelled exploratory, testing outcome/mode separation;
9. component-dependent claim with empty selection;
10. stale `generated_from_commit` and verification commit;
11. numeric snapshot changed within the current 0.5% tolerance;
12. inline Appendix membership drift while headline count remains correct;
13. scorecard status strengthened by adding unrelated component evidence; and
14. a valid semantically compatible adapter case to test specificity.

### 8.4 Recommended benchmark design

Use three sets:

- **Development regression corpus:** known defects, openly authored and grouped.
- **Independent challenge corpus:** mutations authored or reviewed by someone who did not implement the guard.
- **Valid controls:** matched positive cases for each major guard family.

Report, per family:

- defects caught / defects injected;
- controls accepted / controls supplied;
- production-path versus sentinel execution;
- whether the mutation was known before the guard was designed;
- structural family; and
- remaining open mechanism.

Do not calculate one global performance percentage unless the challenge corpus has a defensible sampling frame.

---

## 9. Review of the scientific demonstrations

## 9.1 Observable and unit linting

### Strengths

- It gives concrete examples of quantities sharing names but not meanings.
- It separates saturation concentration, pressure location, named solutes, and total dissolved solids.
- It demonstrates that numerical plausibility is not semantic compatibility.
- It is highly accessible to readers outside espresso modeling.

### Required improvements

- Show the exact typed quantity contracts and the failing adapter messages.
- Distinguish unit conversion from quantity-kind conversion.
- Add a valid adapter control for each invalid example.
- Avoid implying that named Python fields alone guarantee semantic correctness.

## 9.2 Null-first temporal-flow workflow

### Strengths

- Retains a constant baseline.
- Distinguishes machine-only capacity from bed-mechanism inference.
- Separates flexible descriptive curves from mechanistic candidates.
- Now reports per-shot behavior rather than relying only on a smoothed mean.

### Required improvements

- Present the paired shot-level differences and uncertainty.
- State whether parameters are re-estimated per shot or held fixed.
- Keep the cubic comparator visible.
- Avoid external-prediction language.
- Describe the observation operator and preprocessing as part of the estimand.

## 9.3 Fast/slow semantic portability

### Strengths

- Demonstrates that similarly named “fast” and “slow” constants are not automatically interchangeable.
- Connects model semantics to fitted behavior rather than relying on symbol names.
- Is well suited to the paper's interoperability thesis.

### Required improvements

- Report fit uncertainty and model selection.
- Include coarse and fine radius classes.
- Show fitting-window sensitivity.
- State that the Cameron coarsest setting is not one-regime under the current fit.
- Use “one physical diffusion process,” not “single diffusion mode.”

## 9.4 Failed shared-porosity composition

### Strengths

- Preserves a negative result.
- Shows that successful components can fail when coupled through an unjustified shared state.
- Keeps the simple baseline visible.
- Avoids treating complexity as intrinsically better.

### Required improvements

- Do not isolate a single causal failure without ablations.
- Clarify which parameters were not refit and which mappings were newly introduced.
- Record the composition's exact state contract and observation operator.
- Retain the negative evaluation outcome separately from the exploratory generation mode.

## 9.5 Named-shot scorecard

### Strengths

- Makes missing evidence and open stages visible.
- Avoids claiming a complete end-to-end digital twin.
- Separates declared preparation from executed model outputs.
- Has a real producer and machine-readable output.

### Required improvements

- Move from component inventory to stage-selected evidence.
- Correct the pressure-node caveat.
- Represent open state structurally.
- Distinguish the two extraction branches by observable.
- Expose source datasets, fit/evaluation role, and stage outcome.

---

## 10. Section-by-section review

## Title

The title is strong. It is specific, sober, and accurately foregrounds the software/methods contribution. “Evidence registry” is more defensible than “validation framework” at the current state. Retain “espresso process models” to keep the domain clear.

## Front matter and draft-status note

The status note is unusually informative but too long for final front matter. Move build instructions and figure-freeze details to a reproducibility statement or supplement. Update the draft date. Resolve authorship, affiliation, corresponding author, release version, and archive citation before external circulation.

## Abstract

The abstract contains the right ideas but overstates two implementation points:

- semantic observable/domain matching is not enforced; and
- the badge is not literally non-authored in the schema.

It is also too long. Reduce implementation qualifications, retain the three demonstrations, and make the bounded claim: the current system identifies and links evidence precisely but only partially validates semantic commensurability.

## Section 1 — Introduction

The motivating examples are excellent. Add one sentence distinguishing the paper from generic workflow provenance: the central object is a scientifically scoped claim-support edge, not merely a record that code and data were used.

## Section 2 — Scope and corpus construction

The curated/not-systematic distinction is correct. Avoid “beyond reconstruction” and distinguish manifest rows from unique campaigns. State inclusion criteria for the current 27 components and explain how a new source is screened, skipped, quarantined, or registered.

## Section 3 — Registry architecture

The execution-role/provenance separation is improved. Revise “one component per occupied runtime stage” to accommodate stage–observable branches. Make clear that component evidence labels are summaries for navigation, not licenses for every component output.

## Section 4 — Typed contracts

The pressure-node correction and missing-value discussion are strong. Add a migration diagram showing typed and legacy paths. A typed field prevents some substitutions only when all consumers require it; document remaining bypasses.

## Section 5 — Evidence taxonomy

This is the manuscript's core and needs the largest revision. Separate:

- canonical evidence relation;
- evaluation design;
- source/data role;
- evidence-check outcome;
- claim-support role;
- value-origin mode; and
- public presentation summary.

State explicitly which compatibility checks are executable and which remain authored review judgments.

## Section 6 — Provenance and reproducibility

The generation/verification distinction is valuable. Recast numeric snapshots honestly, fix persistent commit provenance, and bind release evidence into one manifest. Do not call a direct-version lock transitive.

## Section 7 — Observable linting and semantic portability

Keep the examples. Add valid controls and explicit adapters. Ensure the demonstration tests the actual contract machinery rather than only reporting known mismatches.

## Section 8 — Null-first comparison

The scientific framing is strong. Add per-shot paired results and specify fit reuse. Keep claims on causal mechanisms modest.

## Section 9 — Failed composition

Retain the section as a major strength. Add an ablation plan and separate generation mode from negative outcome.

## Section 10 — Deliberate defect injection

Replace the stale class table, narrow execution-type language, and disclose that the current review found two manuscript drift defects not caught by the reported green suite. That disclosure would materially strengthen the section.

## Section 11 — Experiment design

This section is valuable and connects disagreement to useful data collection. Tie each proposed experiment to a precise evidence gap and the claim whose badge or status could change if the experiment succeeds.

## Section 12 — Named-shot scorecard

Regenerate stage statuses from selected evidence. Correct the machine-node row. Define stage–observable slots and open-state logic.

## Section 13 — Related work and novelty

Add a feature matrix. Avoid broad cross-domain claims not demonstrated empirically. Frame transfer to other domains as a design hypothesis supported by structural analogy.

## Section 14 — Discussion

The discussion should foreground the boundary discovered here: typed fields and exact IDs are necessary but not sufficient; semantic compatibility itself needs a schema, adapters, and tests. This is a more interesting conclusion than presenting the architecture as complete.

## Section 15 — Limitations and readiness

The section is candid. Correct the blocker count, add the current inline-generated-block drift, and make the public claim artifact's intermediate commit explicit. Separate manuscript readiness, software release readiness, data rights, and scientific validation readiness.

## Conclusions

The conclusions should claim an implemented provenance-and-selection framework with partial semantic enforcement, not a fully executable evidence-licensing system. After the P0 work, the stronger wording will be justified.

## Software and data availability

Add the frozen tag, DOI, license, environment artifact, release manifest, and precise rights status. Distinguish public metadata from redistributable data.

## Figures

The seven generated figures are an asset. Ensure each figure has a visible claim ID, data source, producer, evidence mode, outcome, and caveat where appropriate. Freeze raster/vector renderings and source data in the release bundle.

## Appendix A

Regenerate from the 27-component catalog or include it directly. Do not maintain a separate reduced inline representation while claiming exact synchronization.

## Appendix B

Rewrite as an honest schema view for `PUBLIC_CLAIMS`, show complete support edges, and remove universal coverage language until a cross-class registry exists.

## References

Complete the archive/software reference and verify source lineage for every scientific demonstration. Where a thesis and later journal paper share a lineage, state which supplied equations, parameter values, and evaluation data.

---

## 11. Line-level and editorial comments

Line numbers refer to the locally inspected 1,225-line Markdown rendering of commit `352dacd`; GitHub's raw-line wrapping may differ.

| Approx. line(s) | Current issue | Recommended edit |
|---:|---|---|
| 3–5 | Draft date and author placeholders remain | update date; insert authors, affiliations, corresponding author |
| 7 | says Table 1 and Appendix A are CI-guarded against drift | qualify until exact inline membership is tested; disclose current drift |
| 11 | says selected records' observable/domain match is enforced | change to “records are identified and the match is declared” until P0-2 is implemented |
| 11 | says badge is derived rather than authored | change to “authored badge is checked against a derivation” or alter schema |
| 11 | abstract is ~500 words | reduce to journal limit |
| 33 | says inline Appendix A cannot silently diverge | false in current state; fix generator/test before retaining |
| 74–80 | “beyond reconstruction” | replace with explicit non-ordinal categories |
| 148–201 | Paper 3 owns scientific primary results | reconcile with later “only methodological claims” statement |
| 208 | one component per occupied runtime stage | replace with stage–observable slot rule |
| 390–392 | three authored evidence fields plus one derived field | enumerate exact implemented fields and distinguish claim-edge role |
| 448–450 | artifact/model role described as explicit evidence axis | add field or correct prose |
| 484–523 | exact selection presented as semantic constraint | explain that current validation checks identity/ownership only |
| 530–540 | badge “never authored” | inconsistent with required constructor field |
| 625–632 | “15 executable mutations ... production guard”; “independent groups” | classify actual execution path; use “declared structural families” |
| 644–654 | Table 6a class totals | regenerate: observable semantics 4/4; unit 1/3 |
| 735 | scorecard status derived from scoped vector | specify that it currently uses component inventory, or migrate to row selection |
| 739 | says node identity is not a typed field | replace: typed contract exists; this source trace's node remains unresolved |
| 982–992 | four blockers followed by five | correct count or remove number |
| 905 onward / local 1082 onward | inline Appendix A has 25 rows | add the two Maille components through generator, not manually |
| Appendix B opening | every manuscript-facing quantitative claim exportable | limit to `PUBLIC_CLAIMS` and enumerate other claim systems |
| Table B1 `numeric_result` | “NEVER hand-entered” | describe snapshot verification or make producer value canonical |
| Table B1 `badge` | derived | remove from authored object or say checked against derivation |
| Table B1 commit fields | generation commit immutable | implement persistent provenance before using “immutable” |
| Appendix examples | caveats truncate mid-word | render full normative examples |
| Appendix negative example | does not show outcome/selections | show the fields that make it negative and claim-scoped |
| Reference 1 | version, DOI, access date placeholders | complete at freeze |

### General editorial comments

- Reduce capitalized emphasis (`MUST`, `NEVER`, `SELECTED`, `DELIBERATELY EXCLUDED`) in the narrative. Reserve normative capitalization for a formal specification or schema table.
- Standardize hyphenation: “claim-scoped,” “same-campaign,” “held-out,” “machine-readable,” and “end-to-end.”
- Use one notation for mass-flow units (`g s⁻¹`) in prose and tables.
- Distinguish “validation,” “evaluation,” “verification,” “reproduction,” and “compatibility” consistently.
- Avoid review-history prose in the main article unless the correction itself is an empirical self-test. Detailed review IDs belong in changelogs or supplements.
- Move large implementation-status and catalog tables to supplementary material.

---

## 12. Status of the preceding review's publication blockers

| Previous blocker | Status | Current assessment |
|---|---|---|
| P0-1 claim-scoped evidence selection | **Partly closed** | exact IDs and dependency ownership implemented; semantic matching and required selection remain open |
| P0-2 badges derived, not authored | **Partly closed** | derivation and mismatch test implemented; badge still authored and exporter does not validate |
| P0-3 contradictory evidence ordering | **Largely closed** | obsolete ordering removed; public scalar summary still collapses distinctions |
| P0-4 scorecard producer/ownership | **Closed at prose level** | producer named; ownership table still manual |
| P0-5 schema version and fields | **Closed** | schema 0.8 and pressure/fines fields represented consistently, with legacy path caveat |
| P0-6 mean-trace versus shot-level results | **Closed substantially** | estimands separated; inferential and uncertainty improvements remain P1 |
| P0-7 mutation-suite coverage claim | **Partly closed** | percentage removed and controls separated; class table stale and execution language too broad |
| P0-8 pressure-node diagnosis | **Partly closed** | real typed trace guard added; scorecard stale and migration not universal |
| P0-9 Appendix B coverage | **Not fully closed** | universal wording and schema misstatements remain |
| P0-10 readiness reconciliation | **Improved** | figures/environment clarified; current artifact drift and blocker-count error remain |

### Net progress

The revision closes the easiest interpretation errors and implements meaningful new machinery. The remaining work is more architectural: it requires making the **relationship** between a claim and evidence executable, not merely making both sides identifiable. That is the right next stage for the project.

---

## 13. Recommended canonical claim–evidence architecture

### 13.1 Canonical evidence record

Use one immutable evidence object with structured scientific scope:

```yaml
evidence_id: waszkiewicz2025.poroelastic::gate_dynamic_9bar
component_id: waszkiewicz2025.poroelastic
relation: post_fit_reconstruction
evaluation_design: post_fit_same_data
outcome: supported
observable:
  id: beverage.mass_flow.outlet
  quantity_kind: mass_flow_rate
  unit: kg/s
  location: basket_outlet
  species_basis: total_beverage
  reference_volume: null
  observation_operator: derivative_of_beverage_mass_v1
domain:
  campaign_ids: [waszkiewicz2025_9bar]
  pressure_mode: pressure_controlled
  pressure_node: basket_gauge
  time_window_s: [15, 95]
sources:
  - dataset_id: waszkiewicz2025/traces_time_dependent
    role: fit_and_evaluation
    independence: same_data_as_fit
gate:
  producer: puckworks.validation...
  artifact: ...
  status: PASS
  commit: ...
```

### 13.2 Canonical claim record

```yaml
claim_id: P3-TEMPORAL-01
assertion: A time-varying branch reduces RMSE relative to a constant baseline on all five shots.
reported_values:
  producer: puckworks.analysis.waszkiewicz_shot_level...
  values: generated
  display_precision: {...}
claim_observable: {...same structured contract...}
claim_domain: {...}
dependencies:
  - ref: waszkiewicz2025.poroelastic
    kind: component
    role: produces_reported_value
  - ref: waszkiewicz2025/traces_time_dependent
    kind: dataset
    role: evaluation_data
support_edges:
  - evidence_id: ...
    compatibility: exact
    adapter_id: null
    exclusions: [...]
value_origin: RECONSTRUCTED
evaluation_outcome: supported
public_relation_summary: derived
badge: derived
```

### 13.3 Compatibility engine

A support edge should pass only when:

1. the evidence ID exists and belongs to the dependency;
2. quantity kinds match or a declared adapter exists;
3. units are convertible;
4. species and reference-volume bases match;
5. locations and pressure nodes match;
6. claim domain is contained in or explicitly extrapolates beyond evidence domain;
7. evaluation dataset role supports the requested verb;
8. fit/evaluation overlap is represented honestly; and
9. the evidence outcome supports the claim's wording.

Where full automatic reasoning is impossible, use a controlled adjudication object with reviewer identity, reason, and expiry—not an unconstrained rationale string.

### 13.4 Derived presentation

Derive, never author:

- public relation summary;
- value-origin badge;
- evaluation outcome display;
- limiting dependency;
- claim coverage status;
- dataset list;
- component list; and
- generation/verification provenance view.

### 13.5 Export pipeline

The export transaction should:

1. load the frozen claim registry;
2. compute producer values;
3. validate dependency and semantic support edges;
4. derive presentation fields;
5. render JSON, normalized CSV, Markdown, tables, and figures;
6. verify generated blocks against the manuscript;
7. record environment, commit, hashes, and test/gate artifacts; and
8. fail without writing release artifacts if any check is unresolved.

### 13.6 Scorecard integration

Represent each scorecard row as a claim record or a specialized claim-support edge. Do not invent a second evidence-roll-up system. The scorecard should be a view over the same canonical graph used by public claims.

---

## 14. Prioritized revision plan

## P0 — Complete before the next external manuscript review

### P0.1 Make generated manuscript blocks genuinely single-source

- generate/splice exact Table 1, Appendix A, Table 6a, and scorecard;
- test exact membership and class cells;
- disclose the 25-versus-27 and class-table drift as a self-test finding.

### P0.2 Implement structured semantic compatibility

- extend evidence scope with quantity, unit, location/node, campaign, source-role, and operator IDs;
- validate claim-support edges;
- add wrong-observable/domain/dataset/node/unit tests and valid controls.

### P0.3 Remove empty-selection fallback

- make `evidence_profile` selection-only;
- reject unscoped component dependencies;
- migrate every component-dependent public claim and scorecard stage.

### P0.4 Redesign public evidence summary, badge, and outcome

- remove authored badge;
- derive public summaries from selected evidence;
- preserve value origin and evaluation outcome as separate axes;
- stop mapping same-campaign holdout to unqualified “independent.”

### P0.5 Preserve source and dataset lineage

- carry dataset roles and campaign IDs from evidence graph to public support edges;
- derive dataset lists;
- add overlap and orphan audits.

### P0.6 Make producer values and provenance canonical

- emit live values with explicit display precision;
- persist generation/verification hashes and commits;
- validate before every export;
- regenerate public artifacts at the frozen commit.

### P0.7 Migrate the scorecard

- use exact stage-selected evidence;
- correct pressure-node text;
- represent open state structurally;
- define stage–observable slots.

### P0.8 Rewrite Appendix B and public surfaces

- limit coverage claim to actual schema population;
- show complete support edges;
- normalize CSV;
- include outcome, selection, derivation, and provenance in Markdown.

### P0.9 Correct and strengthen the defect benchmark

- generate class tables;
- classify execution paths honestly;
- use “declared structural families”;
- add semantic claim-selection mutations and controls;
- begin an independent challenge set.

## P1 — Complete before journal submission

- add timescale fit uncertainty, model selection, radius, and window sensitivity;
- add temporal paired-shot uncertainty and fit-reuse details;
- add composition ablations;
- generate claim ownership from structured data;
- add a related-work feature matrix;
- complete reference-lineage audit;
- deprecate or guard legacy untyped trace APIs;
- create a fully resolved environment/container artifact;
- freeze test/gate results in the release bundle;
- distinguish source, campaign, and independence counts;
- move detailed catalogs and mutation cases to supplement.

## P2 — Editorial and presentation pass

- reduce abstract to journal limit;
- reduce main-text length;
- update date and front matter;
- resolve all metadata and archive placeholders;
- standardize terminology and units;
- reduce capitalized emphasis;
- ensure figures and tables carry stable IDs and citations;
- prepare a clean submission manuscript without internal review scaffolding.

### Recommended order

1. Fix generated-block drift and add exact tests.
2. Implement semantic claim-support validation and remove fallback.
3. Redesign mode/outcome/public relation and export validation.
4. Preserve dataset lineage and canonicalize producer values/provenance.
5. Migrate scorecard and Appendix B.
6. Regenerate every artifact at one frozen commit.
7. Run independent clean-room verification.
8. Complete scientific uncertainty/ablation work.
9. Perform journal-length editorial pass.

---

## 15. Suggested replacement passages

### 15.1 Suggested revised abstract

> Published espresso models describe different stages of brewing with incompatible observables, units, pressure locations, concentration bases, experimental domains, and standards of evidence. Puckworks is an executable component and evidence registry designed to make those differences explicit before models are compared or composed. Components are assigned to process stages and connected through typed state carriers; source, dataset, gate, and producer records preserve provenance; and public claims identify the exact evidence records selected for their interpretation. In the present implementation, identity, dependency ownership, units, and several contract boundaries are machine-checked, while complete observable- and domain-compatibility checking remains an active development requirement. Three demonstrations show the value of the approach. Observable linting prevents incompatible concentration, pressure, and inventory quantities from being pooled. A null-first temporal-flow analysis distinguishes machine capacity, constant baselines, time-varying reconstructions, flexible descriptive curves, and shot-level evaluation. A declared shared-porosity composition performs worse than both its extraction-only branch and a constant baseline on a preprocessed mean trace, showing that individually useful components do not automatically form a valid coupled model. A generated named-shot scorecard then exposes observed, reconstructed, verified, extrapolated, and open stages without claiming unsupported end-to-end prediction. Puckworks therefore contributes an executable review method for coupled process models: identify dependencies precisely, preserve negative results, separate verification from empirical evaluation, and convert disagreements into explicit data and experiment requirements.

### 15.2 Suggested replacement for the claim-selection paragraph

> Each component carries a scoped evidence inventory. A public claim does not automatically inherit that inventory. Instead, it names the exact evidence-link identifiers it relies upon and records the claim-side observable, domain, and role of each dependency. The current validator checks evidence identity and dependency ownership and derives presentation fields from the selected records. Complete machine validation of observable, campaign, dataset-role, reference-location, and observation-operator compatibility is not yet implemented; those matches are presently declared and reviewed, and constitute a defined next step rather than an accomplished guardrail.

### 15.3 Suggested replacement for badge/outcome wording

> Public presentation separates how a reported value was produced from how it performed when evaluated. The value-origin mode is one of observed, reconstructed, predicted, or exploratory simulation. Evaluation outcome is separately recorded as supported, negative, or indeterminate. These fields must not be collapsed: a held-out prediction that fails remains a prediction with a negative outcome. In the current code an authored badge is checked against a deterministic derivation; the release architecture will remove the authored field and emit the derived mode directly.

### 15.4 Suggested replacement for the mutation-suite opening

> We evaluate the guardrails with a development mutation corpus containing 18 injected defects, two valid controls, and nine declared structural families. Fifteen defect cases execute code, although the execution paths range from production-path mutations to integration and manuscript sentinels; three cases are explicit limitation analyses. Thirteen defects are caught and five remain open, while both controls are accepted. We report defects and controls separately and do not estimate a global coverage probability because the corpus is constructed from known project failures, lacks a sampling frame, and has no held-out challenge set.

### 15.5 Suggested corrected defect-class table

| defect class | detected / injected defects | valid controls accepted |
|---|---:|---:|
| evidence | 2 / 3 | — |
| numeric consistency | 1 / 1 | — |
| observable semantics | 4 / 4 | 1 / 1 |
| physical value | 0 / 1 | — |
| prose drift | 2 / 2 | — |
| provenance | 3 / 4 | — |
| unit | 1 / 3 | 1 / 1 |

### 15.6 Suggested replacement for the scorecard pressure-node caveat

> Puckworks now provides a typed `PressureTrace` and rejects traces whose declared node does not match the consumer's required node. The recorded trace used for this named shot has not yet been assigned a verified node identity, so the machine-boundary row remains open. The gap is in source-trace identification and migration to the typed contract, not in the absence of a pressure-node type.

### 15.7 Suggested replacement for Appendix B's coverage statement

> The schema below applies to the claims registered in `puckworks.public.claims.PUBLIC_CLAIMS`. Other quantitative statements in the manuscript are produced and audited through separate Paper 3 artifacts. A unified cross-class claim registry has not yet been implemented; the release checklist therefore reports coverage by claim class rather than implying that every manuscript number uses `PublicClaim`.

### 15.8 Suggested readiness statement

> The manuscript is not yet release-ready. Remaining work includes exact regeneration of all inline generated blocks; semantic validation of claim–evidence compatibility; migration of the named-shot scorecard to stage-selected evidence; canonical producer-value and commit provenance; a unified cross-class claim-coverage view; complete authorship and ethics metadata; a frozen archival release with DOI; and independent clean-environment reproduction. The direct-version environment lock improves repeatability but is not a transitive lock or container digest.

---

## 16. Recommended final manuscript structure

1. **Introduction and precise contribution**
2. **Curated corpus and inclusion workflow**
3. **Architecture**
   - component registry
   - typed state and observable contracts
   - evidence records and source roles
   - claim-support edges
   - producers and release provenance
4. **Evaluation of the architecture**
   - semantic/unit contract cases and controls
   - mutation corpus and limitations
5. **Scientific demonstrations**
   - null-first temporal flow
   - timescale semantic portability
   - failed composition
6. **Named-shot evidence ledger**
7. **Related work and novelty matrix**
8. **Limitations and roadmap**
9. **Conclusions**
10. **Supplement**
    - full component catalog
    - claim schema and examples
    - complete mutation cases
    - implementation/readiness tables
    - release manifest and hashes

This structure would reduce the current interleaving of architecture, project history, scientific results, and submission checklist.

---

## 17. Reviewer’s overall recommendation

PAPER 3 has a publishable core and has improved markedly. The repository now embodies several ideas that are uncommon and valuable in scientific software: exact evidence-link identity, explicit evidence inventories, negative composition results, typed pressure traces, producer-linked claims, and a defect corpus that retains misses. The manuscript's strongest contribution is not that every semantic problem has already been solved; it is that the project is turning those problems into explicit, testable objects and is willing to record when the tests fail.

The next revision should lean into that strength. Do not describe free-text claim observable/domain fields as a completed semantic compatibility engine. Do not describe authored snapshots or badges as unambiguously generated. Do not hide the fact that Appendix A and Table 6a drifted despite green checks. Instead, show how those failures exposed missing joins and missing build guards, then correct them. That would provide a compelling self-application result and make the paper more credible than a polished but overstated architecture description.

**Recommendation: major revision, with a favorable expectation after the P0 items are resolved.**

---

## 18. Source ledger for this review

All repository links below are pinned to the reviewed commit unless noted.

### Revision state and review response

- Commit: <https://github.com/trbrewer/puckworks/commit/352dacd51015d95a3b5a5b3e1a8fb331419d78b0>
- Pull request #189: <https://github.com/trbrewer/puckworks/pull/189>
- Manuscript: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/PAPER_3_PUCKWORKS_DRAFT.md>
- Round-3 action tracker: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/paper3_resource/PAPER_3_ROUND_3_ACTION_TRACKER.md>

### Registry and generated artifacts

- Registry artifact producer: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/paper3/registry_artifacts.py>
- Generated 27-component catalog: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/paper3_resource/generated/appendixA_component_catalog.md>
- Generated public claims: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/docs/public/generated/claims.json>

### Evidence and claims

- Public claim schema: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/public/schema.py>
- Seeded public claims: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/public/claims.py>
- Public exporter: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/public/export.py>
- Evidence graph: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/paper3/evidence_graph.py>
- Appendix B producer: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/paper3/appendix_b.py>

### Scorecard, contracts, and evaluation

- Named-shot scorecard: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/paper3/named_shot_scorecard.py>
- Contracts: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/contracts.py>
- Defect-injection suite: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/puckworks/paper3/defect_injection.py>
- Manuscript consistency tests: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/tests/test_paper3_manuscript_consistency.py>
- Defect tests: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/tests/test_defect_injection.py>
- Public claim tests: <https://github.com/trbrewer/puckworks/blob/352dacd51015d95a3b5a5b3e1a8fb331419d78b0/tests/test_public_claims.py>

---

## Final disposition in one sentence

**PAPER 3 is now a strong major-revision manuscript: retain its central architecture and demonstrations, but complete the semantic claim–evidence join, eliminate fallback and authored-presentation ambiguity, repair the generated-artifact regressions, and freeze one internally consistent release before external circulation.**
