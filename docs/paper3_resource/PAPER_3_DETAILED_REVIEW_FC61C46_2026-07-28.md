# Detailed Review of PAPER 3 — Merged Revision at `fc61c46`

## Review boundary

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Manuscript:** [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/fc61c46/docs/PAPER_3_PUCKWORKS_DRAFT.md)  
**Repository state reviewed:** merge commit [`fc61c46`](https://github.com/trbrewer/puckworks/commit/fc61c46), which merged [PR #190](https://github.com/trbrewer/puckworks/pull/190) on 28 July 2026  
**Substantive Paper 3 head incorporated by the merge:** [`f0d836c`](https://github.com/trbrewer/puckworks/commit/f0d836c5b237adac9733d0e39bff69b532fdfcef)  
**Previous detailed-review boundary:** `f0d836c`, while PR #190 was still open  
**Review date:** 28 July 2026, America/Chicago  
**Recommendation:** **Major revision before the manuscript claims that claim-level scientific compatibility is executable, and before formal journal submission**

> **Boundary note.** No substantive Paper 3 source change was found between the previously reviewed PR head (`f0d836c`) and the merged tree (`fc61c46`). This is therefore not a review of a new scientific revision. It is an independent, deeper post-merge audit of the now-authoritative repository state. It concentrates on actual seeded-claim failures and schema invariants that were not fully exposed in the preceding report.

---

## 1. Executive assessment

### 1.1 Overall judgment

PAPER 3 has developed into a serious and potentially valuable methods/resource paper. Its strongest contribution is not another espresso model. It is the proposition that heterogeneous process models should be represented as explicit components with typed interfaces, scoped evidence, declared compatibility limits, provenance, negative results, and reproducible claim producers rather than being assembled into a universal “mega-model” by matching similar variable names.

That contribution remains compelling. The present revision has also improved materially over earlier drafts:

- registry counts and Appendix A are generated or spliced rather than copied through an unguarded second authoring path;
- evidence-link identities are stable and claim selections name exact records;
- the evidence inventory and the evidence selected for one public claim are now separated;
- same-campaign holdout evidence is no longer publicly called independent;
- public badges have a deterministic derivation function and an authored mismatch is rejected;
- the mutation-suite narrative is more candid about its development-set nature;
- the named-shot scorecard is generated and its numerical diagnostics come from named producers;
- the paper reports its own guard failures rather than quietly repairing them; and
- the scientific demonstrations are generally more carefully caveated than in the earlier versions.

The post-merge audit nevertheless finds that the paper’s central architectural assertion is not yet true end to end. The abstract says a public claim selects evidence “whose observable and domain match its own assertion.” The implementation requires only non-empty free-text descriptions and an evidence identifier belonging to the named component. It performs no comparison of observable, domain, units, dataset, pressure node, transformation, observation operator, boundary conditions, or fit/evaluation role.

More importantly, this is not merely a hypothetical validator weakness. Several of the five seeded public claims pass validation while selecting evidence for a materially different observable, experimental design, or conclusion. In the clearest example, PV-02 asserts that a machine-and-wetting model reproduces a flow dip, selects a gate that reproduces two scalar times, and deliberately excludes the gate that actually evaluates the normalized flow-minimum curve because that direct gate has a negative outcome. PV-01 selects an extraction-yield conservation gate to support a diffusion-timescale comparator. PV-03’s public numbers concern identifiability and held-out transfer, but the selected component evidence concerns same-data source reconstruction. PV-05 selects a fixed-flow, end-of-shot yield diagnostic to support the imported swelling branch’s role in a dynamic 9-bar shared-porosity composition.

The result is a particularly important finding for the paper itself: **exact evidence identity prevents accidental whole-component inheritance, but it does not prevent evidence cherry-picking or scope laundering**. The current system makes the author explain the choice, but it cannot determine whether the explanation is scientifically valid.

The appropriate disposition remains **major revision**, not rejection. The paper’s conceptual direction is strong; the remaining issues are concentrated around the public claim/evidence layer, scorecard, export contract, and release provenance. Fixing those areas would materially strengthen both the paper and the repository.

### 1.2 Principal publication blockers

| Priority | Finding | Why it is load-bearing |
|---|---|---|
| **P0-1** | Four seeded public claims contain clause-to-evidence mismatches | The architecture currently validates its own non-commensurate support selections. |
| **P0-2** | Commensurability is authored prose, not an executable predicate | Exact IDs establish identity and ownership, not scientific applicability. |
| **P0-3** | Dataset and producer dependencies are neither resolved nor evidence-typed | Fictitious references pass validation and dataset-only claims become `OBSERVED` automatically. |
| **P0-4** | The supposedly authoritative dependency graph is incomplete | Five declared manifest inputs are missing from dependency edges, and two claims omit their actual top-level producer. |
| **P0-5** | Relation aggregation uses the strongest selected support edge | A strong dependency can mask a weak load-bearing dependency, contradicting the paper’s non-ordinal evidence argument. |
| **P0-6** | Claim outcome, evidence outcome, and result polarity are conflated | A supported public claim may select negative evidence, and PV-03 is `negative` while its only selected evidence is `supported`. |
| **P0-7** | Badge derivation has unguarded order and role pathologies | Duplicate selections make the badge order-dependent; comparator evidence can alter the badge despite not capping the relation. |
| **P0-8** | “Producer-generated; never hand-entered” is false | Numeric values remain authored snapshots; the producer is used as a tolerance-based drift detector and the snapshot is retained. |
| **P0-9** | Public export and provenance are incomplete and stale | `result_map` is discarded, support derivations are omitted, and committed claims remain last-verified at `352dacd`. |
| **P0-10** | The named-shot scorecard aggregates complete component vectors and discards outcomes | Negative or unrelated evidence can appear as an apparently positive stage status. |
| **P0-11** | Appendix B materially overstates the implemented contract | It calls dependencies authoritative, badges derived, values never hand-entered, and all quantitative claims exportable when those statements are not accurate. |
| **P0-12** | The framework evaluation does not cover the failures now present in its own seed claims | The mutation suite is useful but does not test semantic mismatch, missing lineage edges, outcome contradiction, order dependence, stale verification stamps, or lossy export. |

### 1.3 Strengths that should be retained

1. **The scientific interoperability problem is well chosen.** Espresso models provide concrete, consequential examples of incompatible pressure nodes, inventories, units, concentration definitions, model stages, and validation regimes.
2. **The configuration-over-mega-model position is persuasive.** A declared configuration with explicit adapters is a more defensible unit of computation than a universal integrated model.
3. **Negative composition is treated as evidence.** The shared-porosity failure is one of the paper’s best examples because it resists tuning away an inconvenient result.
4. **The paper distinguishes reconstruction from prediction more carefully.** Mean-trace, per-shot, source-reproduction, held-out, and independent designs are increasingly separated.
5. **The paper is unusually candid about infrastructure failures.** The Appendix A drift incident, denominator failures, vacuous gates, and numeral-audit limitation make the methods argument more credible when converted into stronger controls.
6. **Generated figures, source data, alt text, release tooling, cards, and contracts provide a substantial resource-paper foundation.**
7. **The current limitations section is materially honest.** It explicitly states that the corpus is curated, the named shot is not a validated end-to-end prediction, several adapters remain embedded, and external reproduction is absent.

---

## 2. Scope, method, and limitations of this review

### 2.1 Principal artifacts inspected

The audit covered the merged versions of:

- [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/fc61c46/docs/PAPER_3_PUCKWORKS_DRAFT.md)
- [`puckworks/public/schema.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/public/schema.py)
- [`puckworks/public/claims.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/public/claims.py)
- [`puckworks/public/export.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/public/export.py)
- [`docs/public/generated/claims.json`](https://github.com/trbrewer/puckworks/blob/fc61c46/docs/public/generated/claims.json)
- [`docs/public/generated/claims.csv`](https://github.com/trbrewer/puckworks/blob/fc61c46/docs/public/generated/claims.csv)
- [`docs/public/generated/claims.md`](https://github.com/trbrewer/puckworks/blob/fc61c46/docs/public/generated/claims.md)
- [`puckworks/paper3/EVIDENCE_LINKS.json`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/EVIDENCE_LINKS.json)
- [`puckworks/paper3/evidence_graph.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/evidence_graph.py)
- [`puckworks/paper3/named_shot_scorecard.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/named_shot_scorecard.py)
- [`puckworks/paper3/appendix_b.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/appendix_b.py)
- [`puckworks/paper3/corpus.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/corpus.py)
- [`puckworks/paper3/claim_coverage.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/claim_coverage.py)
- [`puckworks/paper3/defect_injection.py`](https://github.com/trbrewer/puckworks/blob/fc61c46/puckworks/paper3/defect_injection.py)
- PR #190’s change narrative, reported verification, unresolved-item list, and merge record.

### 2.2 Verification performed

The review included:

- a post-merge source audit against `fc61c46`;
- comparison with the preceding `f0d836c` review boundary;
- tracing every seeded public claim through its dependencies, selected evidence IDs, generated claim artifact, and evidence-link scope;
- comparison of each compound public statement with what its selected gates actually test;
- inspection of dependency resolution, badge derivation, relation aggregation, outcome handling, export behavior, scorecard construction, corpus counting, and Appendix B generation;
- focused executable probes against the merged `schema.py`; and
- static comparison of `dataset_manifest_ids`, typed dataset dependencies, the main `Producer`, and declared producer dependencies.

### 2.3 Focused executable probes

The following probes used the merged `schema.py` in isolation. They did not require modification of the repository and did not purport to replace the project’s complete test suite.

```text
FAKE_REFS []
  -> fictitious dataset and producer refs validate; badge derives OBSERVED

STRONG_MASKS_WEAK []
  -> independent + code-verification load-bearing edges validate with
     supported_cap='independent'

COMPARATOR_CONTAMINATION []
  -> a negative comparator changes the badge to EXPLORATORY_SIMULATION
     even though comparator_context does not cap the public relation

OUTCOME_CONTRADICTION []
  -> claim outcome='supported' with selected negative evidence validates

BLANK_ID []
  -> a blank evidence_id validates when both dependency and selection use ''

ORDER_DEP ['produces_reported_value', 'comparator_context'] [] -> OBSERVED
ORDER_DEP ['comparator_context', 'produces_reported_value'] [] -> PREDICTED
  -> identical duplicate selections derive different badges solely from order

RESULT_MAP_IN_EXPORT? False
  -> PublicClaim.to_dict() omits Producer.result_map
```

These are not speculative design objections; they are accepted states under the current validator.

### 2.4 Verification not repeated

PR #190 reports **2,117 tests passed, one skipped, no failures**, `ruff` clean, clean Paper 3 registry/manuscript/release/numeral checks, and 28 passing merge checks. I inspected the relevant implementation and generated artifacts but did **not** independently rerun the complete clean-environment suite. This review therefore does not certify that test total or the CI environment. It independently reproduces the focused schema behaviors above.

### 2.5 Severity convention

- **P0 — publication blocker:** resolve in implementation or narrow the manuscript claim before submission.
- **P1 — major:** materially affects rigor, interpretation, traceability, or reproducibility.
- **P2 — editorial/release:** presentation, wording, metadata, or submission polish.

---

## 3. What changed since the previous review

### 3.1 Repository status changed; substantive Paper 3 code did not

The preceding report reviewed `f0d836c` while PR #190 was open. PR #190 has now been merged as `fc61c46`. The merge record reports 28 passing checks. No later Paper 3 source revision was identified in the merged state.

This matters because several items listed by the PR itself as still open are now present on `main`, including:

- claim/evidence commensurability;
- lineage;
- producer-emitted numerics;
- per-row scorecard records; and
- selection-aware export.

The current review therefore treats those as merged limitations rather than pending branch work.

### 3.2 New emphasis in this review

The previous review established that the architecture *could* accept semantic mismatches. This audit goes further and asks whether the repository’s own seeded claims already exhibit them. They do.

The most important new conclusions are:

1. **PV-01, PV-02, PV-03, and PV-05 contain actual support-scope mismatches.**
2. **PV-04 demonstrates that dataset-only claims can receive `OBSERVED` and authored `independent` status without any typed observation evidence.**
3. **Five manifest inputs listed by claims are missing from the dependency graph that Appendix B calls authoritative.**
4. **Two claims’ top-level numeric producer is absent from their typed producer dependencies.**
5. **Claim outcome and evidence outcome are already contradictory in PV-03.**
6. **The committed claim bundle remains last-verified at `352dacd`, despite the merged `fc61c46` state and the PR’s clean verification report.**
7. **The scorecard does not merely aggregate unrelated evidence; it discards evidence outcome when constructing the status string.**

---

# 4. Publication-blocking findings

## P0-1 — The seeded claim registry contains material clause-to-evidence mismatches

### Finding

Four of the five public claim records combine assertions that are not fully licensed by the evidence records selected for them. Because all four records validate and are committed as generated public artifacts, this is the most consequential result of the review.

### PV-01: conservation evidence is used to license a diffusion-timescale comparator

PV-01 reports a measured early-to-peak TDS ratio and includes a 23.1 s “boulder diffusion timescale” comparator. Its only selected component evidence is:

```text
cameron2020.extraction_bdf::gate_cameron_conservation
```

The evidence record’s scope is extraction yield calculated through two internal accounting routes plus an inventory upper bound. It is a code-verification record and is not reality-facing. It does not establish the particle-scale diffusion timescale, the particle radius, the bath condition, or the mathematical route by which 23.1 s is produced.

The selection rationale says the conservation gate “licenses using its internal accounting for that timescale.” That is not what the gate tests. Conservation of the model’s mass accounting and correctness of a characteristic diffusion timescale are distinct properties.

**Required correction:** either:

- create a separate evidence link that directly verifies the diffusion-timescale calculation, its radius, diffusion coefficient, geometry, and bath assumptions; or
- remove the timescale from PV-01’s tracked result and keep it as explicitly unlicensed context outside the claim.

The measured 97% result itself should be represented by typed observation evidence, not by assigning `independent` manually to a dataset-only finding.

### PV-02: scalar timing evidence is used to support a flow-dip shape assertion

PV-02 says a machine-and-wetting model “can reproduce a dip-and-recovery.” Its selected Foster record is:

```text
foster2025.machine_mode::gate_foster_machine_tp_ts
```

That gate reproduces two scalar quantities: ponding time and saturation time. The component’s evidence inventory also contains the directly relevant normalized flow-minimum record:

```text
foster2025.machine_mode::gate_foster_fig15_flowmin
```

The direct flow-curve record has a **negative** outcome and is deliberately excluded. The rationale argues that the scalar times support the model’s capacity to generate the dip. They do not establish the asserted dip-and-recovery morphology. A model may reproduce transition times while missing the normalized flow shape.

This is exactly the failure mode the paper claims to prevent: evidence for a related but different observable is selected because the directly relevant evidence is unfavorable.

**Required correction:** split PV-02 into at least two atomic claims:

1. a Foster-source claim about ponding and saturation times; and
2. a separate claim about whether the modeled normalized flow curve reproduces a dip-and-recovery.

The second claim must select the direct flow-minimum evidence and carry its negative outcome, or the prose must be weakened to a purely structural capacity statement that does not say the observed curve is reproduced.

### PV-03: source-reconstruction evidence does not license the public identifiability and held-out-transfer results

PV-03 reports:

- an objective-surface condition number;
- inverse-curvature coupling;
- a near-optimal-grid fraction;
- held-out model and constant-baseline MAPE;
- the number of held-out points on which the model is worse;
- skill versus the constant null; and
- an implied timed-fraction rate.

Its only selected component evidence is the Pannusch same-data source reconstruction gate, scoped to per-solute fraction-concentration MAPE over the source campaign’s 15 experiments × 6 windows.

The actual identifiability panel and cross-grind transfer calculations are producer dependencies with empty evidence collections. The held-out result is therefore outside the typed evidence selection. The selected source-reconstruction record supports implementation fidelity to a source campaign, not the identifiability surface or the cross-campaign/held-out comparison produced elsewhere.

The claim is also marked `outcome="negative"`, while its only selected evidence record is `outcome="supported"`. That reveals that “outcome” is being used for different concepts at different layers.

**Required correction:** atomize PV-03 into at least:

- a same-data source-reconstruction claim;
- an identifiability/profile claim;
- a held-out transfer-versus-null claim; and
- a timed-fraction information claim.

Each needs its own result producer, dataset/fit/evaluation lineage, evidence relationship, support status, and caveat.

### PV-05: fixed-flow yield evidence is used for a dynamic fixed-pressure composition

PV-05’s primary composition evidence is appropriately scoped to the 9-bar mean-trace shared-porosity diagnostic. However, the imported `mo2023_2.swelling` branch is licensed with:

```text
mo2023_2.swelling::gate_mo2_swelling_insensitivity
```

That gate concerns end-of-shot yield with swelling on/off at fixed flows of 2, 3, and 4 mL s⁻¹, contrasted with a fixed-pressure Carman–Kozeny flow-decay ratio. It is non-empirical code verification. The public claim concerns a dynamic 9-bar trace, a particular imported parameterization, a shared-porosity coupling, and a specific observation operator.

The selected gate may establish that the source port implements one fixed-flow calculation, but it does not license compatibility of that branch when transferred into the dynamic fixed-pressure composition. The current record confuses **source-port verification** with **composition-edge compatibility**.

**Required correction:** add a distinct typed composition edge recording:

- source component and target composition;
- transferred parameters and units;
- state-variable mapping;
- control mode;
- initial and boundary conditions;
- observation operator;
- whether any parameters were refit;
- compatibility tests performed; and
- the negative composition result.

The Mo source gate may remain as implementation provenance, but it should not be treated as evidence for the target composition’s scientific admissibility.

### Why this blocks publication

PAPER 3’s novelty claim is that evidence is connected to the exact assertion it licenses. The committed seed registry demonstrates that exact identity and authored rationale are insufficient. Until these live examples are corrected, the paper should not state that the architecture prevents scope laundering.

---

## P0-2 — Commensurability is not executable

### Finding

`ClaimEvidenceSelection.validate()` checks only that:

- at least one evidence ID is supplied;
- `claim_observable`, `claim_domain`, and `role_in_claim` are non-empty; and
- the role belongs to a small vocabulary.

`PublicClaim.validate()` then checks that the selected evidence ID belongs to the named dependency. It does not compare the claim target with the evidence target.

The following scientifically load-bearing fields are absent or unvalidated:

- canonical observable identity;
- dimensions and unit;
- denominator/inventory basis;
- species versus aggregate definition;
- pressure node;
- control mode;
- campaign and dataset identity;
- fit/evaluation split;
- preprocessing and transformation chain;
- observation operator;
- initial and boundary conditions;
- state mapping or adapter;
- population/material/coffee domain; and
- support status/admissibility.

The manuscript’s abstract says the selected records’ observable and domain “match” the claim. In the implementation, those fields are merely prose that an author may write inconsistently with the selected evidence scope.

### Required architecture

Create a structured target on both the claim clause and evidence link, for example:

```yaml
observable:
  id: mass_flow_rate
  quantity_kind: mass_rate
  unit: g/s
  basis: beverage_outlet
  pressure_node: null
  species: aggregate_tds
  observation_operator: de1_scale_to_mass_flow_v1

domain:
  campaign_id: waszkiewicz2025_fixtureA
  dataset_ids:
    - waszkiewicz2025/traces_time_dependent
  pressure_control: nominal_9bar
  time_window_s: [15, 95]
  preprocessing_ids:
    - waszkiewicz_mean_trace_v2
  initial_condition_id: saturated_prewet
  boundary_condition_id: measured_pressure_trace
```

Then implement a compatibility result:

```text
EXACT_MATCH
MATCH_WITH_DECLARED_ADAPTER
CONTEXT_ONLY
INCOMPATIBLE
INDETERMINATE_MISSING_METADATA
```

A claim should fail closed when a licensing edge is incompatible or indeterminate. A human rationale may explain a deliberate adapter, but it must not replace the machine-checkable comparison.

### Minimum acceptance test

The four current seeded mismatches in P0-1 must fail before correction. A generic synthetic test is not enough; the repository’s live claims should be test fixtures.

---

## P0-3 — Dataset and producer dependencies bypass identity and evidence validation

### Finding

`Dependency.validate()` checks the dependency kind and that its role is non-empty. It does not verify that:

- a component ref exists in the registry;
- a dataset ref exists in `MANIFEST.csv`;
- a producer ref imports and resolves;
- a producer is the same producer named by `PublicClaim.producer`;
- evidence IDs are non-empty and unique;
- `public_relation` agrees with the registry-to-public mapping; or
- the evidence outcome and fit/evaluation values belong to controlled vocabularies.

A focused probe created fictitious dataset and producer references. The claim validated with no errors and derived `OBSERVED` because it had no component dependency.

```text
FAKE_REFS []
('OBSERVED', 'no component dependency ...', None)
```

This means `OBSERVED` currently means “no component dependency,” not “a resolved observation with a recorded measurement method, campaign, sampling design, and transformation lineage.”

PV-04 is the live example. It has no component dependency and no evidence selection, yet carries:

```text
evidence_strength = independent
badge = OBSERVED
```

The schema accepts this without any object defining what “independent” is independent of, whether the cell means are direct measurements or derived quantities, which raw replicate dataset is used, how the TDS-to-EY conversion was performed, or how the Welch interval was produced.

### Required action

1. Resolve every `Dependency.ref` against an authoritative namespace.
2. Add typed evidence/lineage objects for datasets and producers rather than assuming only components can carry evidence.
3. Introduce a direct-observation relation such as `direct_measurement`, separate from model-evaluation relations such as `independent_external`.
4. Require a dataset-only claim to identify:
   - raw dataset IDs;
   - campaign ID;
   - sampling unit and replicate structure;
   - measurement method and units;
   - preprocessing/derivation chain;
   - statistic and uncertainty method; and
   - producer result paths.
5. Derive `OBSERVED` only when all required observation lineage is resolved.

---

## P0-4 — The declared authoritative dependency graph is incomplete and internally inconsistent

### Finding

Appendix B states that `dependencies` is the authoritative list. Static comparison with each claim’s `dataset_manifest_ids` finds five declared manifest inputs that are not represented as dataset dependency edges:

| Claim | Manifest ID listed on claim but absent from `dependencies` |
|---|---|
| PV-04 | `schmieder2023/cup_masses` |
| PV-05 | `waszkiewicz2025/constants` |
| PV-03 | `angeloni2023/total_solids` |
| PV-03 | `angeloni2023/inventories` |
| PV-03 | `pannusch2024/table2_params` |

The top-level numeric producer is also absent from the typed producer dependencies for two claims:

| Claim | `PublicClaim.producer` | Producer dependencies actually listed |
|---|---|---|
| PV-04 | `puckworks.public.analysis_autopsy.pv04_values` | three underlying harness functions, but not the top-level producer |
| PV-03 | `puckworks.public.flat_valley.pv03_values` | two analysis functions, but not the top-level producer |

This is not a demand for full transitive closure. These are explicitly declared top-level manifest inputs and the exact top-level function that exports the claim’s numbers. The current two parallel lists disagree.

### Consequences

- a consumer cannot treat `dependencies` as authoritative;
- the payload hash can bind one dependency list while the human-readable manifest list names another;
- selection-aware exports cannot reconstruct the full source path;
- a dependency can disappear from one surface without failing the other; and
- the paper’s assertion that public claims link outputs to declared datasets and producers is only partly true.

### Required action

Enforce these invariants:

```text
set(dataset_manifest_ids)
  == set(d.ref for d in dependencies if d.kind == 'dataset')

producer.ref()
  in set(d.ref for d in dependencies if d.kind == 'producer')
```

If underlying producers are also important, represent them as upstream edges beneath the top-level producer, not as a substitute for it. Deprecate the parallel `dataset_manifest_ids` field once migration is complete, or derive it from the dependency graph.

---

## P0-5 — Multi-dependency evidence is aggregated in the wrong direction

### Finding

The evidence graph explicitly says its relations are non-ordinal because they answer different questions. The public schema reintroduces a total order and computes the supported public relation with `max(...)` over the selected licensing evidence.

That rule permits a strong dependency to mask a weak load-bearing dependency. The focused probe combined:

- one `controlled_independent` edge; and
- one `code_verification` edge;

both in `produces_reported_value` roles. A public claim labelled `independent` validated cleanly because the cap was the strongest selected relation.

```text
STRONG_MASKS_WEAK []
supported_cap = independent
```

Badge derivation noticed the weak code-verification design and returned `RECONSTRUCTED`, but relation validation still allowed `independent`. The public relation and badge therefore tell conflicting stories about the same support graph.

### Why `min(...)` is not a complete fix

Taking the weakest ordinal relation would be more conservative, but the paper is right that these are not one-dimensional grades. Code verification, source reproduction, independent evaluation, and compatibility address different propositions. The correct operation is not necessarily `min` or `max`; it is the intersection of assertion verbs licensed by every necessary edge.

For example:

```text
code verification -> may say “implementation reproduces specification”
independent external -> may say “output agrees on this external observable/domain”
compatibility -> may say “sign or range is compatible under these conditions”
```

A composite claim can use only the verbs supported by **all load-bearing edges**. Comparator/context edges should be attached to the clause they contextualize and should not upgrade or downgrade unrelated clauses.

### Required action

Replace `strongest_supported_relation()` with a clause-level admissibility calculation:

1. classify each edge as load-bearing, comparator, diagnostic subject, or context;
2. map each evidence record to a set of licensed assertion verbs;
3. intersect the licensed verb sets across necessary edges;
4. reject the authored claim verb if it is outside the intersection; and
5. export the limiting edge and the reason.

---

## P0-6 — The outcome model conflates three different concepts

### Finding

The repository currently uses “outcome” for at least three distinct things:

1. **gate execution/evidence outcome:** did a specified comparison support, refute, or fail to resolve the tested proposition?
2. **claim support status:** is the public sentence supported by its selected evidence?
3. **scientific result polarity:** is the scientific finding itself positive, negative, null, or mixed?

These are not interchangeable.

PV-03 illustrates the problem. Its public claim is `outcome="negative"`, apparently because the scientific finding is an identifiability failure or weak mechanism result. Its only selected evidence record is `outcome="supported"`, because the source-reconstruction gate passed. Both can be true, but they refer to different axes.

The validator does not relate them. A focused probe showed that a public claim marked `supported` can select a negative evidence record and still validate. Badge derivation may become exploratory, but the contradictory public support field remains accepted.

### Required action

Replace the overloaded field with separate typed axes:

```yaml
claim_support_status: supported | partially_supported | unsupported | indeterminate
scientific_result_polarity: positive | negative | null | mixed | not_applicable
```

Keep `evidence_outcome` on each support edge. Then define explicit consistency rules, for example:

- a `supported` claim cannot depend solely on `unsupported` or `indeterminate` licensing edges;
- a negative scientific result may be strongly supported;
- a gate may pass because it correctly detects a model failure;
- comparator evidence must not determine support for a different clause; and
- a compound claim with mixed support must be split or marked partially supported.

---

## P0-7 — Badge derivation is not invariant to selection ordering or comparator role

### Finding 1: duplicate selections are order-dependent

`derive_badge()` builds:

```python
roles = {s.dependency_ref: s.role_in_claim for s in claim.evidence_selections}
```

Two selections for the same dependency overwrite each other. The validator does not reject duplicate dependency selections or conflicting roles.

The focused probe used the same evidence record twice, once as `produces_reported_value` and once as `comparator_context`:

```text
['produces_reported_value', 'comparator_context'] -> OBSERVED
['comparator_context', 'produces_reported_value'] -> PREDICTED
```

Both validate. The only difference is tuple order.

### Finding 2: comparator evidence can contaminate the badge

Relation capping excludes `comparator_context`, but `derive_badge()` evaluates all selected evidence for negative and indeterminate outcomes before narrowing to producing dependencies. A negative comparator can therefore force an otherwise held-out claim to `EXPLORATORY_SIMULATION`.

This is the opposite of the stated principle that a comparator should not turn a measured finding into a model output.

### Finding 3: blank evidence IDs validate

`ScopedEvidenceRef.evidence_id` defaults to an empty string. If both the dependency inventory and the selection use the empty string, the selection validates.

### Required action

- require non-empty, globally unique evidence IDs;
- require at most one selection object per `(claim_clause_id, dependency_ref)`;
- reject conflicting roles;
- make badge derivation operate only on load-bearing edges for the clause whose badge is being derived;
- separately expose comparator limitations without allowing them to alter the producing-result badge; and
- add permutation-invariance tests.

---

## P0-8 — Public numeric values are authored snapshots, not producer-emitted values

### Finding

The manuscript and Appendix B repeatedly say that numeric results are producer-generated and “NEVER hand-entered.” The exporter actually:

1. computes the live producer value;
2. compares it with the authored `numeric_result` snapshot;
3. applies a generic tolerance `max(1e-3, 0.5% of the snapshot)`;
4. records drift only if the difference exceeds that tolerance; and
5. deliberately keeps the authored numeric snapshot in the exported claim.

The producer is therefore a **drift checker**, not the canonical emitter of the exported number.

This distinction is material:

- a hand-entered value within tolerance remains the public value;
- the same generic relative/absolute tolerance is applied to quantities with different scales and meanings;
- rounding precision is not declared per field;
- integer counts, ratios, RMSE, porosity, times, and interval bounds share one generic policy;
- `bool` is a subclass of `int`, so `swelling_closes_shared_state=True` resides in `numeric_result` and follows numeric handling despite being categorical; and
- a slow producer skipped without `--slow` is not actually marked `stale-unchecked` in the exported schema, despite the module documentation saying it is.

### Required action

Make the producer’s returned value canonical:

```text
live_raw_value -> typed rounding policy -> exported display value
```

The source declaration should store only:

- result path;
- unit;
- statistic type;
- display precision or significant-figure rule;
- uncertainty metadata; and
- optional expected regression value for a test, clearly distinguished from the exported result.

Field-specific acceptance rules should be explicit. A boolean should be exported as a typed categorical result, not a numeric result with unit “boolean.”

### Required wording if implementation is not changed

Replace “producer-generated; never hand-entered” with:

> “Values are authored display snapshots that are recomputed by named producers and rejected when drift exceeds a declared tolerance.”

That wording is less ambitious but accurate.

---

## P0-9 — Exported provenance is lossy, non-recomputable, and stale at the merged commit

### Finding 1: `result_map` is discarded

`Producer` declares that `result_map` maps each claim key to a path in the producer return value. `PublicClaim.to_dict()` exports only:

```text
ref
slow
kwargs
```

It omits `result_map`. Appendix B nevertheless says the producer field contains the result path.

A consumer cannot determine which producer output generated each public number, and cannot independently rerun the mapping described by the schema.

### Finding 2: the public relation and badge derivations are not exported

The JSON contains the authored scalar `evidence_strength` and `badge`, but does not export a canonical object containing:

- all public and registry relation details;
- the calculated cap/admissible verbs;
- the derived badge rationale;
- the limiting dependency;
- clause-level support status; or
- a compatibility verdict.

CSV and Markdown discard even more: they omit selected evidence IDs, support roles, outcomes, evaluation designs, scope, and deliberate exclusions.

### Finding 3: the committed artifact is not verified against the merged state

Every current claim in `docs/public/generated/claims.json` records:

```text
generated_from_commit = 352dacd...
last_verified_against_commit = 352dacd...
```

The repository is now at `fc61c46`, and PR #190 reported clean Paper 3 release recomputation. If the claims were successfully verified during that work, `last_verified_against_commit` should have advanced. If they were not verified, the clean report should not imply that they were.

This is a concrete failure of the distinction Appendix B explains between immutable generation provenance and mutable last-verification provenance.

### Finding 4: payload hash cannot be independently reconstructed from the export

`payload_hash()` hashes the in-memory dataclass, including `Producer.result_map`, while `to_dict()` omits that field. A consumer of the committed JSON cannot reconstruct and verify the payload hash from the serialized artifact alone.

The hash also does not bind:

- producer source-code blobs;
- imported module code;
- input dataset checksums;
- transform code and versions;
- environment digest; or
- output files/source-data tables.

It is a declarative claim-payload hash, not scientific result lineage. The manuscript should name it accordingly.

### Required action

- export the complete producer contract including `result_map`;
- export derived relation/badge/support details and their rationale;
- regenerate or verify the claim bundle at the final merge/release commit;
- make a release gate require `last_verified_against_commit == release_commit`;
- allow `generated_from_commit` to remain earlier only when the full serialized payload and result lineage are unchanged;
- include code/data/environment hashes in a separate `result_lineage` object; and
- make the payload hash reproducible from the serialized JSON.

---

## P0-10 — The named-shot scorecard aggregates whole component inventories and ignores outcomes

### Finding

`named_shot_scorecard._status_for()`:

1. obtains the complete evidence vector for the selected component;
2. deduplicates relation names;
3. maps each relation to a positive-sounding status phrase; and
4. joins the phrases.

It carries each evidence record’s outcome into the machine-readable row, but **does not use outcome when constructing the displayed stage status**.

This creates misleading rows. For example:

- `cameron2020.extraction_bdf` is shown as “verified (code only) + compatibility check,” even though its independent-external morphology comparison is negative and the row caveat says absolute yield reads low;
- `wadsworth2026.inertial` concatenates verification, compatibility, and source-reconstruction relations across different scopes without stating which exact record licenses the named-shot regime statement; and
- the evidence may concern source curves or different observables rather than the named fixture’s exact stage assertion.

The scorecard is therefore generated, but it is not claim-scoped or row-scoped. It reproduces at the stage level the whole-inventory inheritance that the public claim schema was revised to remove.

### Required action

Give each scorecard row a typed record containing:

```yaml
row_claim_id:
claim_observable:
claim_domain:
selected_evidence_ids:
support_roles:
compatibility_verdicts:
evidence_outcomes:
derived_status:
status_rationale:
limiting_edge:
numeric_result_refs:
```

Derive the human status from the exact selected records and their outcomes. A negative comparison should print as negative or limiting, not merely as the relation name. If no record matches the named-shot observable/domain, the stage should be `OPEN` or `CONTEXT ONLY`.

---

## P0-11 — Appendix B overstates the public claim contract

### Finding

Appendix B is generated from the schema, so its inaccuracies are reproducible rather than accidental. Several statements should be corrected:

1. **“Every manuscript-facing quantitative claim is exportable.”** Only five seeded `PublicClaim` records exist. Many manuscript numbers are covered by other producers, generated tables, or a prose numeral audit rather than by this record type.
2. **`numeric_result` is “producer-generated; NEVER hand-entered.”** The values are authored snapshots retained after a tolerance check.
3. **`badge` is “derived.”** The dataclass still requires an authored badge; validation checks it against a derived value. That is authored-and-validated, not a non-authored derived field.
4. **`dependencies` is authoritative.** It disagrees with `dataset_manifest_ids` and omits the top-level producer in two claims.
5. **`producer` contains the result path.** `to_dict()` omits `result_map`.
6. **Evidence scope and role are recorded alongside the public relation.** The examples omit the dependency and evidence-selection structures that carry the paper’s main methodological contribution.
7. **The “negative outcome” example is selected by searching the legacy scalar evidence string for “negative.”** Because the new model separates relation from outcome, that search finds nothing and falls back positionally to the final claim.
8. **Examples truncate caveats at 96 characters.** The generated manuscript visibly ends caveats mid-word, removing part of the exact limitation that the contract is supposed to preserve.

### Required action

Rewrite Appendix B to distinguish:

- fields authored in source;
- fields computed and stored;
- fields computed at export only;
- fields validated against a computation;
- fields omitted from outward exports; and
- coverage of this schema versus other manuscript claim mechanisms.

The examples should show one complete atomic claim clause, including its selected evidence IDs, result paths, support status, compatibility verdicts, and untruncated primary caveat.

---

## P0-12 — The guardrail evaluation does not test the architecture’s current failures

### Finding

The defect-injection suite is now framed appropriately as a development mutation suite rather than a statistical coverage estimate. That is a strong improvement. However, it does not include the defects that this post-merge audit found in the live claim registry:

- evidence selected for a different observable;
- evidence selected for a different experimental domain/control mode;
- direct relevant negative evidence excluded in favor of related scalar evidence;
- fictitious dataset or producer dependency refs;
- missing top-level dataset dependency edges;
- main producer not represented in dependencies;
- strongest evidence masking a weak load-bearing edge;
- claim support status contradicting evidence outcome;
- duplicate selection order changing the badge;
- blank evidence IDs;
- comparator outcome contaminating the producing-result badge;
- `result_map` lost during export;
- last-verification commit stale after a clean verification report; and
- scorecard status discarding evidence outcome.

A methods paper about executable evidence constraints should demonstrate that its guards catch the failure modes present in its own public examples.

### Required action

Add the current seeded claims as regression fixtures and mutation-test each corrected defect. Report results by structural family and execution path, with controls. Do not report a single percentage as architectural coverage; report the matrix of what is and is not guarded.

---

# 5. Claim-by-claim audit

## 5.1 PV-01 — “The first liquid … was already about 97% as concentrated as the peak”

### What is supported

- The early/peak ratio is a direct calculation from a named fraction dataset.
- The caveat correctly states that the first fraction has one replicate and that this is not a universal law.
- The claim appropriately separates wetting delay from chemical concentration of the emerging liquid.

### What is not yet supported through the claim architecture

- `independent` is authored without a typed direct-observation evidence relation.
- The 23.1 s comparator is bundled into the same result record as the measured TDS values.
- The selected conservation gate does not establish the diffusion-timescale value.
- The dataset and producer have no typed evidence/lineage object beyond identity strings.
- The statement that early concentration “beats” the comparator requires a precise definition of what event/time is compared with what timescale.

### Recommended refactor

Create:

- **PV-01A:** measured early/peak TDS ratio, `OBSERVED`, direct-measurement evidence;
- **PV-01B:** Cameron characteristic diffusion timescale, `EXPLORATORY_SIMULATION` or `VERIFIED_MODEL_QUANTITY`, with a dedicated timescale gate; and
- **PV-01C:** a cautious cross-object comparison, explicitly marked as interpretive and not a validation result.

## 5.2 PV-02 — machine/wetting dip and temporal bed reconstruction

### What is supported

- The 9-bar mean-trace temporal branch is clearly described as post-fit reconstruction.
- The caveat acknowledges the flexible cubic and avoids identifying a unique bed mechanism.
- The machine/wetting and bed-side examples are described as separate datasets/contexts.

### What is not supported

- scalar ponding/saturation times do not license the assertion that the normalized flow dip-and-recovery is reproduced;
- the directly relevant negative flow-shape gate is excluded;
- two different scientific examples are combined under one claim ID, one relation label, one badge, and one support status; and
- the headline’s first clause is stronger than the selected evidence.

### Recommended refactor

Split into:

- **PV-02A:** Foster scalar transition-time reproduction;
- **PV-02B:** Foster flow-shape result, carrying the direct negative gate;
- **PV-02C:** Waszkiewicz 9-bar mean-trace null ladder; and
- **PV-02D:** interpretation that a curve shape alone is not uniquely diagnostic, supported by a deliberately scoped synthesis of A–C.

## 5.3 PV-03 — endpoint identifiability and held-out transfer

### What is supported

- The prose carefully distinguishes practical from structural identifiability.
- It disclaims a likelihood/noise model and identifies right censoring of the tested rate range.
- It compares the mechanistic model with a level-only null rather than relying on absolute fit alone.

### What is not supported through the selected evidence

- the objective-surface metrics are producer outputs with no typed evidence record;
- the held-out MAPE and pointwise comparison are producer outputs with no typed evaluation edge;
- the only selected evidence concerns source-campaign reconstruction;
- the claim-level negative outcome is not connected to the selected supported evidence; and
- four manifest inputs are listed, but only one appears as a dataset dependency.

### Recommended refactor

Create atomic claim records for source fidelity, profile geometry, held-out transfer, null comparison, and timed-fraction implication. Give the held-out record explicit fit and evaluation dataset IDs and define the experimental unit used in the holdout.

## 5.4 PV-04 — unit audit and raw replicate result

### What is supported

- The corrected TDS-derived EY means and Welch interval are clearly presented.
- The grinder-dial portability caveat is strong.
- The claim distinguishes observed data from model capacity.

### What is not represented

- the raw `cup_masses` dataset is absent from the authoritative dependency list;
- the top-level `pv04_values` producer is absent from producer dependencies;
- no direct-observation evidence object records sample sizes, measurement method, replicate unit, derivation from TDS to EY, or Welch assumptions;
- `independent` has no defined referent for a direct data summary; and
- the public compound finding also discusses channeling-model capacity, while `numeric_result` was deliberately restricted to observed quantities.

### Statistical reporting recommendation

Report, per dial cell:

- `n` shots;
- mean and standard deviation;
- the exact contrast definition;
- Welch degrees of freedom;
- confidence level and method;
- whether the shots are independent experimental units;
- whether multiple contrasts were prespecified; and
- the derivation equation for TDS-based EY.

## 5.5 PV-05 — negative shared-porosity composition

### What is supported

- The primary composition diagnostic is well matched to the 9-bar mean trace and correctly framed as a negative result for one composition.
- The prose does not reject swelling in general.
- The baseline remains visible.

### What remains problematic

- the imported swelling source-port gate does not establish compatibility in the target control mode and coupling;
- `waszkiewicz2025/constants` is absent from typed dependencies;
- the boolean state-closure flag is stored as a numeric result;
- the claim bundles source implementation fidelity, composition behavior, RMSE comparison, and state-limit diagnosis into one record; and
- the support status is `supported`, while the scientific result is negative and the badge is exploratory—three different concepts that need explicit names.

### Recommended refactor

Represent the composition as a typed graph with separate edges for parameter import, state mapping, control-mode translation, observation operator, source-port verification, and target diagnostic. The negative composition claim should be one atomic, strongly supported negative result, not an “exploratory” label caused by ambiguous outcome semantics.

---

# 6. Additional major comments (P1)

## P1-1 — `evidence_strength` remains authored even though relation detail is derivable

The validator only rejects an authored relation if it is stronger than the computed cap. It allows weaker, inconsistent, or semantically inappropriate labels. The canonical outward relation should be computed from clause support, with any deliberate conservative wording represented separately.

## P1-2 — `badge` remains a constructor field

A truly derived badge should not be accepted as an independent source argument. Store it only in the exported/result object or expose it as a property. The current pattern permits duplicate authoring and requires a consistency check that would be unnecessary if only one source existed.

## P1-3 — controlled vocabularies are incompletely enforced

`Dependency.validate()` does not validate:

- `outcome`;
- `fit_evaluation`;
- `public_relation` against `REGISTRY_TO_PUBLIC`;
- evidence ID non-emptiness/uniqueness; or
- gate identity against the evidence graph.

These should be contract checks.

## P1-4 — the public vocabulary contains a value that new claims are forbidden to use

`EVIDENCE_STRENGTHS` includes `negative validation`, while validation rejects it as a legacy compound. Retain it only in a migration parser or explicit legacy namespace, not in the allowed vocabulary for new records.

## P1-5 — `proposed_experiment` maps to `reference`

A proposed but unrun experiment is not a reference relation. It should be represented as a plan/proposal state with no support verb, otherwise the public relation layer obscures whether data exist.

## P1-6 — result values need typed per-value provenance

A single mapping plus one free-text uncertainty paragraph cannot express the heterogeneity of PV-03 or PV-05. Each result should carry:

```yaml
value:
unit:
quantity_kind:
statistic:
sample_n:
aggregation_level:
uncertainty_type:
interval_level:
interval:
producer_ref:
result_path:
dataset_ids:
transform_ids:
rounding_policy:
```

## P1-7 — one generic tolerance is not a scientific contract

Counts should normally match exactly. Booleans should match exactly. Ratios and RMSE may have declared display rounding. Confidence bounds should be regenerated from raw precision. Define per-field tolerances or compare canonical rounded values.

## P1-8 — skipped slow producers are not marked as documented

`export.py` says a skipped slow producer is marked stale-unchecked, but the loop simply continues and no status is written. Add `verification_status`, `verified_at_commit`, and `producer_executed` fields.

## P1-9 — payload provenance should not be called result provenance

The current hash binds an authored declarative object, not the computation’s code/data/environment. Rename it `claim_payload_sha256` and add a separate result-lineage digest or RO-Crate/PROV record.

## P1-10 — CSV and Markdown claim exports are not selection-aware

They present a single evidence label and badge while omitting the exact selected records and outcomes. Either enrich them or call them summary views and point unambiguously to the complete JSON support graph.

## P1-11 — public Markdown still says labels are carried unchanged

The header says evidence labels are carried “UNCHANGED” from scientific analyses, but the schema maps a registry vocabulary to a coarser public vocabulary and may author a conservative scalar label. Update the generated wording at source.

## P1-12 — the source module says “four P0 stories” but contains five claims

This is minor in isolation but revealing in a provenance-focused module. Derive or remove the count.

## P1-13 — duplicate dependency refs are not rejected

`by_ref = {d.ref: d ...}` silently overwrites duplicate dependencies. Require unique `(kind, ref)` pairs.

## P1-14 — a claim can name a component as context-only without evidence-selection coverage

That may be legitimate, but the role should be attached to a specific clause and should not be available as a blanket escape hatch. Require a reason and ensure the component is not referenced in the headline or reported-value derivation.

## P1-15 — atomize compound claims

All five public records combine multiple propositions. A claim/evidence architecture should operate at the smallest sentence clause that can be true or false under one observable, domain, and evidence design. Public-facing cards may group clauses after each has its own support record.

## P1-16 — scorecard status terms are relation names, not verdicts

“Verified + compatibility check + reconstructed” describes methods used, not whether the named-shot stage is supported, unsupported, open, or extrapolated. Report relation, outcome, applicability, and final stage verdict separately.

## P1-17 — corpus card count is environment-sensitive

`corpus.py` and `claim_coverage.py` count `docs/cards/*.md` from the filesystem. PR #190 records two actual denominator changes caused by whether an untracked card was present. Count tracked files (`git ls-files`) or, preferably, use an explicit card inventory generated from the release manifest.

## P1-18 — “unique dataset sources (empirical campaigns)” is inferred from an ID prefix

A dataset-ID prefix is not necessarily one empirical campaign, and one campaign can create multiple source namespaces. Add an explicit `campaign_id` field to the manifest.

## P1-19 — the numeral audit remains context-insensitive

The manuscript candidly notes that numeral dispositions are keyed by value, allowing “25 components” to be explained as a date. Replace token-value matching with a contextual claim ID, line anchor, AST-like span, or explicit inline marker.

## P1-20 — generated/spliced/checked terminology should be precise

The paper should consistently distinguish:

- generated from source;
- spliced into manuscript;
- recomputed;
- consistency-checked against another source; and
- editorial text with checked numeric cells.

This distinction is central to the paper’s own duplicate-authoring lesson.

## P1-21 — rights readiness is a major release constraint

The manuscript reports that only one component is cleared for hosted execution and 25 of 27 have no rights review recorded. This should appear in the abstract-level resource limitations or release-readiness summary, not only deep in the architecture section.

## P1-22 — final release readiness remains incomplete

The manuscript correctly lists many of these items, but they remain real submission gates:

- author names and affiliations;
- corresponding author;
- contributions;
- funding;
- competing interests;
- acknowledgments;
- frozen version and archival DOI;
- complete transitive lock or container digest;
- external reproduction;
- indexed/systematic search record;
- final embedded figure renderings; and
- release-frozen claim and corpus artifacts.

## P1-23 — figures should expose the distinction between evidence relation and evidence outcome

Figure 2 and Figure 7 are natural places to show this visually. A relationship type should not appear as a positive status when its outcome is negative.

## P1-24 — PV-04’s statistical inferential unit should be explicit

The Welch interval is interpretable only if the replicate unit and independence assumptions are clear. State whether replicates are shots, fractions, technical repetitions, or model-derived cells.

## P1-25 — companion-paper ownership should be clause-level

PAPER 3 appropriately borrows temporal results from the companion paper, but ownership is currently tracked at a coarse claim/result level. Shared clauses should carry a canonical producer and an assertion owner so that the same number is not interpreted as independent corroboration across manuscripts.

---

# 7. Cross-layer consistency audit

| Topic | Manuscript claim | Implementation/artifact | Assessment |
|---|---|---|---|
| Evidence matching | selected observable/domain match claim | free text only; no comparison | **Contradiction** |
| Whole-inventory inheritance | public claims select exact records | true for component selections | **Improved, but insufficient** |
| Public relation | graph avoids strongest/weakest collapse | public schema orders relations and takes strongest | **Contradiction** |
| Badge | derived, not authored | required authored field checked against derivation | **Partly true** |
| Numeric values | producer-generated, never hand-entered | authored snapshots retained within tolerance | **Contradiction** |
| Producer contract | includes result path | `to_dict()` omits `result_map` | **Contradiction** |
| Dependencies | authoritative | missing five manifest edges and two main producers | **Contradiction** |
| Dataset-only evidence | observed/independent claim | no typed observation evidence; auto-OBSERVED | **Gap** |
| Outcome | separate from relation | claim and evidence outcomes not reconciled; polarity conflated | **Gap** |
| Scorecard | scoped evidence status per stage | whole component vector; outcome ignored in status | **Contradiction** |
| Claim bundle verification | mutable last-verified stamp | committed artifact remains at `352dacd` | **Stale** |
| Slow-producer status | marked stale-unchecked | no field is written | **Contradiction** |
| Corpus count | snapshot of committed corpus | filesystem glob includes ambient untracked files | **Non-deterministic** |
| Every quantitative claim | exportable as `PublicClaim` | only five records; other claim systems exist | **Overstatement** |
| Release reproducibility | not yet complete | DOI, full lock, external reproduction absent | **Correctly disclosed** |

---

# 8. Recommended canonical claim–evidence design

## 8.1 Separate public cards from atomic scientific clauses

A public card may group related findings for readability, but each load-bearing proposition should be an atomic `ClaimClause`:

```yaml
claim_card_id: PV-02
clauses:
  - clause_id: PV-02A
    assertion: Foster model reproduces ponding and saturation times...
  - clause_id: PV-02B
    assertion: Foster model reproduces the normalized dip-and-recovery curve...
  - clause_id: PV-02C
    assertion: A temporal porosity trajectory reduces mean-trace RMSE...
```

Each clause should have one target observable/domain and one support verdict.

## 8.2 Typed result object

```yaml
result:
  result_id: PV-02C.dynamic_rmse
  value: 0.116
  unit: g/s
  statistic: RMSE
  aggregation: preprocessed_mean_trace
  sample_n: 5
  evaluation_window_s: [15, 95]
  producer:
    ref: puckworks.harness.kappa_t_ladder
    result_path: rungs.phi.rmse
    kwargs: {}
  datasets:
    - waszkiewicz2025/traces_time_dependent
  transforms:
    - waszkiewicz_mean_trace_v2
  rounding:
    decimals: 3
```

## 8.3 Typed support edge

```yaml
support_edge:
  dependency_ref: waszkiewicz2025.poroelastic
  dependency_kind: component
  role: produces_reported_value
  evidence_ids:
    - waszkiewicz2025.poroelastic::gate_waszkiewicz_dynamic_9bar
  target_match:
    observable: exact
    unit: exact
    domain: exact
    dataset: exact
    observation_operator: exact
    overall: exact_match
  evidence_outcome: supported
  claim_support_effect: licensing
```

## 8.4 Direct observation evidence

Datasets should not be assumed evidentiary merely because they exist. A direct observation record should identify:

- campaign;
- sample/replicate unit;
- measurement method;
- instrument/calibration;
- raw and derived observable;
- transformation chain;
- missingness/exclusions;
- uncertainty/statistic; and
- whether the dataset is independent of any model fit being evaluated.

## 8.5 No total evidence ranking

Replace scalar “strongest relation” with:

- relation types;
- evaluation design;
- evidence outcome;
- applicability match;
- licensed verbs; and
- clause support status.

The public summary may render a concise badge, but it should be computed from those dimensions and should expose the limiting edge.

## 8.6 Distinguish result polarity from support

```yaml
claim_support_status: supported
scientific_result_polarity: negative
```

This correctly describes a strongly supported negative composition result.

## 8.7 Reproducible lineage

Export both:

1. `claim_payload_sha256` — hash of the serialized assertion and support graph; and
2. `result_lineage` — code blobs, producer/result paths, input manifest checksums, transform versions, environment digest, output values, and release commit.

The first is a content identity; the second is computational provenance.

---

# 9. Required acceptance tests

The following tests should pass before the manuscript makes its present central claims.

## 9.1 Semantic compatibility

1. PV-01 conservation evidence cannot license the diffusion-timescale result.
2. PV-02 scalar timing evidence cannot license a normalized flow-shape claim.
3. PV-05 fixed-flow yield evidence cannot license dynamic fixed-pressure composition compatibility.
4. A claim/evidence observable mismatch fails.
5. A unit/basis mismatch fails.
6. A pressure-node mismatch fails.
7. A dataset/campaign mismatch fails unless an explicit allowed adapter or transfer design exists.
8. An indeterminate target due to missing metadata fails closed.

## 9.2 Dependency integrity

9. Every component ref resolves.
10. Every dataset ref resolves in the frozen manifest.
11. Every producer ref imports and resolves.
12. `dataset_manifest_ids` equals dataset dependencies during migration.
13. `producer.ref()` is present as a producer dependency.
14. Dependency refs are unique.
15. Evidence IDs are non-empty and unique.
16. Every selected evidence ID belongs to exactly one declared dependency.

## 9.3 Relation, outcome, and badge invariants

17. A weak load-bearing edge cannot be masked by a strong edge.
18. Reordering selections cannot change any derived result.
19. Duplicate/conflicting selection roles fail.
20. Comparator evidence does not alter the producing-result badge unless the claim clause is explicitly about the comparator.
21. A supported claim cannot rely only on negative/indeterminate licensing evidence.
22. Negative scientific result polarity can coexist with strong support.
23. `public_relation` must equal the mapping from the registry relation.
24. `fit_evaluation` and evidence outcome must belong to controlled vocabularies.

## 9.4 Numeric and export integrity

25. The exported number equals the producer result after the declared rounding rule.
26. Counts and booleans match exactly.
27. Every numeric/result key exports its result path.
28. `payload_sha256` is reproducible from the serialized artifact.
29. A skipped slow producer emits `verification_status=stale_unchecked`.
30. JSON, CSV, and Markdown either carry selection-aware support details or explicitly identify themselves as lossy summaries.
31. `last_verified_against_commit` equals the final release commit.

## 9.5 Scorecard and corpus integrity

32. Every generated scorecard row has exact selected evidence IDs.
33. Negative evidence changes the displayed stage verdict.
34. Unrelated component evidence cannot enter a row.
35. A stage without matching evidence is `OPEN`, not a concatenation of inventory relations.
36. Corpus card count is based on the tracked release inventory, not ambient files.
37. Dataset campaigns are counted from explicit campaign IDs.

## 9.6 Mutation suite

38. Each corrected live defect above is re-injected and caught.
39. Valid controls are included for specificity.
40. Results are reported by structural family and execution path, not as an unqualified coverage percentage.

---

# 10. Suggested manuscript revisions

## 10.1 Abstract — current wording should be narrowed until implementation changes

### Current claim at issue

The abstract says a claim selects records “whose observable and domain match its own assertion” and derives its badge from that selection.

### Interim replacement

> A public-value claim selects exact evidence-link identifiers from declared component dependencies and records, in authored fields, the claim observable, asserted domain, role, rationale, and deliberate exclusions. The current release verifies evidence identity and dependency ownership but does not yet execute a complete semantic commensurability predicate across observable, unit, campaign, transformation, and observation-operator metadata. Public badges are computed from selected evidence and checked against the stored summary label; unresolved combinations fail closed.

This is less ambitious but accurately describes the merged code.

## 10.2 Evidence section — add a distinction between identity and applicability

Suggested paragraph:

> Exact evidence identity is necessary but not sufficient. An identifier can prove that a claim selected a real record owned by a declared component while the selected record still concerns a different observable, domain, dataset, control mode, or observation operator. The current implementation enforces identity and ownership and records an authored commensurability rationale; a fully typed applicability predicate remains future work. The public claims in this release should therefore be read as curated support graphs rather than automatically adjudicated scientific entailments.

## 10.3 Public relation language

Replace statements implying a strongest/weakest scalar evidence grade with:

> Evidence relations answer different questions and are not collapsed into a universal rank. For a compound claim, every load-bearing edge must license the assertion verb used for its own clause. Comparator and context edges are reported separately.

Then change the implementation accordingly.

## 10.4 Numeric-producer language

### If implementation is fixed

> Every exported result value is taken from a named producer and transformed only by a declared field-specific rounding rule.

### If implementation remains unchanged

> Every stored display value is recomputed by a named producer and checked for drift against a declared tolerance; the authored display snapshot remains the exported value.

## 10.5 Named-shot scorecard caption

Suggested replacement:

> **Table 6. Named-shot evidence ledger.** The configuration and non-component statuses are declared. For component stages, the current release summarizes each component’s complete scoped evidence inventory; the relation names do not by themselves indicate positive outcome or applicability to the named shot. Until row-specific evidence selections are implemented, the table is an inventory-ledger illustration rather than a claim-level support adjudication.

After row-specific records land, the stronger current wording can be restored.

## 10.6 Appendix B opening

Suggested replacement:

> The `PublicClaim` schema covers the five seeded public-value cards. Other manuscript numbers are tracked through generated tables, figure producers, cross-paper bundles, and a prose numeral audit; there is not yet one claim registry covering every quantitative assertion. The fields below include authored values, computed summaries, and provenance stamps. Their exact status is stated per field.

## 10.7 Conclusions

The conclusion should say that Puckworks **records and exposes** support selections and incompatibilities, not yet that it fully **enforces** scientific commensurability. The paper can still make a strong contribution by being explicit that the present release is an executable identity/provenance framework with a planned semantic compatibility layer.

---

# 11. Section-by-section comments

## Title

The title is clear and appropriately methods-oriented. “Evidence registry” is justified, but “executable” will invite reviewers to test which semantic assertions are actually executable. The revised paper should either close the P0 items or qualify the title/abstract to distinguish executable identity/provenance from executable scientific entailment.

## Abstract

- Strong motivation and clear rejection of the digital-twin/mega-model framing.
- The claim-selection sentence overstates semantic validation.
- The statement that the graph does not collapse evidence to a strongest/weakest badge conflicts with the public schema’s ordered relation cap.
- Mention that the corpus is curated and that only a small portion of components have rights clearance for public hosting.
- Distinguish the framework’s method demonstrations from independent validation of Puckworks itself.

## Sections 1–2: motivation and corpus

- The distinction between curated and systematic is now responsible.
- Keep the denominator table; it prevents component count being misread as study count.
- Make card and campaign counts release-deterministic.
- Consider moving the most important corpus limitations earlier: English-only, search adapted to interface gaps, and rights-blocked sources.

## Section 3: registry architecture

- The stage/component/configuration framing is one of the strongest sections.
- Table 1h’s distinction between implemented capability and architectural intent is valuable.
- The rights matrix is sobering and should influence availability claims.
- “All 27 importable” should never be conflated with publicly executable or redistributable.

## Section 4: typed contracts

- The pressure-node correction and Forchheimer equation are now clear.
- The paper appropriately admits that dataclasses are not a dimensional type system.
- The broad permeability range guard cannot identify plausible wrong units; the mutation result should be used to motivate tagged quantities rather than broad-range assertions.
- The fast-fraction semantic example remains an excellent demonstration.

## Section 5: evidence architecture

- This is the manuscript’s load-bearing section and needs the most revision.
- Separate evidence identity, applicability, support status, result polarity, and public rendering.
- Remove any suggestion that a total relation order is scientifically meaningful.
- Introduce atomic claim clauses and direct observation evidence.
- Use the current seeded mismatches as candid worked examples, as the manuscript did with Appendix A drift.

## Section 6: provenance and corpus governance

- The distinction between raw external corpus, aggregate outputs, rights, and attribution is thoughtful.
- Complete the ethics determination before reporting corpus-derived findings.
- Freeze retrieval and serializer/normalizer versions before paper-grade corpus statistics.

## Section 7: observable and unit linting

- Strong worked examples.
- Ensure each corrected constant/erratum claim is linked to the original author confirmation or an auditable source record.
- Keep the distinction between a definitional mismatch and a physical disagreement.

## Section 8: temporal/null-first workflow

- Mean-trace versus shot-level wording is much improved.
- Avoid borrowing a compound public claim that merges machine-source behavior with the Waszkiewicz ladder.
- Keep the flexible cubic as a non-mechanistic null.

## Section 9: composition

- The negative result is publication-worthy as a methods demonstration.
- Define the composition edge explicitly rather than relying on source-component evidence.
- Keep “no parameters were refit” rather than “parameter-free.”
- State that failure may arise from state mapping, parameter transfer, control mode, boundary conditions, initial conditions, or observation operator—not only scale mismatch.

## Section 10: defect injection

- The revised framing as a development mutation suite is appropriate.
- Add the live claim-schema failures found here.
- Continue to separate controls and structural families.
- Report which cases traverse production code and which are static sentinels.

## Section 11: experiment design

- This is a strong and practical section.
- Link each proposed experiment to the exact competing configurations and target observable.
- Add expected information gain or a simpler discrimination score where feasible.

## Section 12: named shot

- The ledger framing is correct.
- Row status must become outcome- and applicability-aware.
- The pressure-node gap is honestly reported.
- Do not let a per-shot fitted multiplier and the same shot’s evaluation be summarized in a way that resembles independent prediction.

## Sections 13–15: related work, discussion, limitations, readiness

- Related-work positioning is now adequate for a draft.
- The limitations section is candid and should be retained.
- Add the claim/evidence semantic mismatch as an explicit limitation if it is not fixed.
- The readiness table should include a fresh claim-bundle verification stamp and deterministic card inventory.
- The list says “Four” blockers and then enumerates five; correct the count.

## Appendix A

- The spliced registry catalog is now structurally much stronger.
- Preserve the generated markers and release freeze.

## Appendix B

- Requires the substantive rewrite described in P0-11.
- Show the actual support graph, not only headline/numbers/producer.
- Do not truncate the primary caveat.
- Distinguish author-entered, computed, checked, and stamped fields.

## References and front matter

- Replace author and corresponding-author placeholders.
- Complete contributions, funding, interests, and acknowledgments.
- Insert the frozen release/version/DOI/access date.
- Ensure the companion-paper reference has stable author/title/status information appropriate to the target venue.

---

# 12. Prioritized revision plan

## P0 phase — required before strong framework claims or journal submission

1. Split compound public cards into atomic claim clauses.
2. Correct PV-01, PV-02, PV-03, and PV-05 support selections.
3. Implement typed claim/evidence target compatibility.
4. Add direct-observation evidence for dataset-derived claims.
5. Resolve all component/dataset/producer dependency refs.
6. Make the dependency graph complete and canonical.
7. Replace strongest-relation aggregation with clause-level licensed-verb intersection.
8. Separate evidence outcome, claim support, and result polarity.
9. Make badge derivation order-invariant and reject duplicate/blank selections.
10. Export producer-emitted values with typed rounding policies.
11. Export `result_map`, derived support details, and complete lineage.
12. Regenerate/verify the claims artifact at the final release commit.
13. Convert scorecard rows to exact evidence selections with outcome-aware verdicts.
14. Rewrite Appendix B to describe the actual contract.
15. Add all corrected live defects to the mutation suite.

## P1 phase — major rigor and release work

1. Type uncertainty and per-value provenance.
2. Add campaign IDs to the manifest.
3. Make corpus counts release-inventory-based.
4. Replace context-insensitive numeral dispositions.
5. Make CSV/Markdown selection-aware or explicitly lossy.
6. Complete rights review for release-facing components and data.
7. Produce a full transitive environment lock or container digest.
8. Obtain one external reproduction.
9. Complete the indexed search/screening record.
10. Freeze and archive all generated artifacts.

## P2 phase — submission and editorial work

1. Complete authorship and declarations.
2. Embed final figures and verify captions/alt text/source data.
3. Standardize generated/spliced/checked terminology.
4. Correct stale counts in comments and headings, including “four P0 stories” and “Four blockers.”
5. Copy-edit generated examples to avoid mid-word truncation.
6. Select a target venue and conform article structure, data/software statements, and supplementary package.

---

# 13. Proposed final decision language

> **Recommendation: major revision.** The manuscript presents a strong and potentially publishable architecture for representing heterogeneous espresso-process models, provenance, evidence relations, and negative composition results. The revised repository has meaningfully improved exact evidence identity, generated manuscript content, badge checking, defect-suite reporting, and release engineering. However, the central claim that evidence selection constrains assertions at the claim’s own observable and domain is not yet implemented: the validator checks identity and ownership but not scientific commensurability, and several committed seed claims select evidence for a different observable or experimental design. Dataset and producer lineage remain partially outside the typed evidence system; multi-dependency relation aggregation is non-conservative; outcomes are semantically conflated; numeric exports retain authored snapshots; the public claim bundle is stale relative to the merged commit; and the named-shot scorecard aggregates whole evidence inventories without using outcomes in its status. These issues are concentrated and repairable. Resolving them would convert a compelling conceptual framework into the executable scientific-support architecture the manuscript presently describes.

---

## 14. Bottom line

PAPER 3 is substantially stronger than its earliest drafts and remains worth pursuing. Its most valuable next move is not to add more demonstrations or more prose. It is to use the four failing seeded claim examples as the next self-audit case study:

1. show exactly how exact IDs still permitted non-commensurate support;
2. implement the typed applicability and atomic-claim layer;
3. re-inject the failures as mutations; and
4. report what the strengthened system now refuses.

That would be a powerful continuation of the manuscript’s best methodological principle: **a green gate is evidence only after it has been shown to fail on the defect it claims to prevent.**
