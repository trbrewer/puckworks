# Detailed Review of PAPER 3

## Manuscript reviewed

**Title:** *Puckworks: an executable, provenance-aware evidence registry for espresso process models*  
**Repository:** `trbrewer/puckworks`  
**Review date:** 25 July 2026  
**Audit boundary:** commit [`93358f8e4d7d5c214470d82195d852f455651ff9`](https://github.com/trbrewer/puckworks/commit/93358f8e4d7d5c214470d82195d852f455651ff9)  
**Manuscript file:** [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/PAPER_3_PUCKWORKS_DRAFT.md)  
**Recommendation:** **Major revision before preprint circulation or journal submission**  
**Confidence:** High on repository/manuscript consistency findings; moderate on venue fit until a target journal is selected.

---

## 1. Review scope and method

This review treats Paper 3 as both a scientific manuscript and a description of a live research-software resource. I therefore checked four things in parallel:

1. whether the manuscript presents a coherent, sufficiently novel scholarly contribution;
2. whether its scientific claims are stated at the evidence level supported by the repository;
3. whether its descriptions, counts, schemas, readiness statements, and examples agree with the frozen repository snapshot; and
4. whether the paper is shaped appropriately for a software paper, resource paper, or full methods article.

The audit included the manuscript, registry schema, generated registry tables, component catalog, dataset manifest, Paper 3 evidence matrix, README, release information, public-access documentation, rights notes, and manuscript-facing claim architecture. The manifest count was independently parsed from the pinned CSV with Python's standard `csv.DictReader`.

This was a **static documentary and code-structure audit**. I did not independently rerun the full test suite, refit the statistical models, or reproduce all numerical outputs from raw source data. Numerical comments below therefore focus on traceability, evidence classification, reporting sufficiency, and consistency with the repository's own generated evidence records. A clean-room computational reproduction remains an important pre-submission task.

Because the repository was changing during the review, all comments are tied to the commit above. Later changes to `main` may already address individual points, but they do not alter the need for a frozen, reproducible manuscript build.

---

## 2. Executive assessment

Paper 3 has a strong and genuinely useful central argument: espresso models cannot safely be compared or connected merely because they use similar variable names, and an executable review should preserve the meaning, provenance, scope, and evidentiary status of each component and each claim. The manuscript is at its best when it demonstrates **scientific restraint as a software feature**—for example, retaining an unresolved pressure-node identity, refusing to substitute total roasted-bean chemistry for extractable inventory, preserving a composition that performs worse than a simple baseline, and ending an illustrative chain with “measurement required” rather than inventing a complete cup prediction.

The repository also contains unusually thoughtful infrastructure for an early-stage scientific modeling project: component and source cards, typed metadata axes, evidence-qualified gates, claim producers, release provenance, generated inventory tables, public notebooks, explicit caveats, and rights controls. These are substantive strengths. The paper is not merely documenting a collection of equations; it is attempting to formalize how heterogeneous model literature should be interrogated before comparison and composition.

However, the current manuscript is not yet submission-ready. The most immediate problem is that it claims its generated manuscript tables cannot silently drift from the code, while the manuscript's own Table 1 and Appendix A have in fact drifted from the generated artifacts. The paper reports 11 runtime components, 13 calibration components, and one synthesis component, whereas the authoritative generated registry reports 12 runtime and 13 calibration components; “project synthesis” is a provenance class, not an execution role. The manuscript also continues to foreground the deprecated `kind` field and says adapters and diagnostics are not first-class enum values, while schema v2 already defines them as execution-role values. This is more than a routine stale count: it directly tests the paper's principal claim that manuscript-facing metadata are producer-generated and CI-guarded.

The data-manifest count is likewise stale. The manuscript repeatedly reports 70 records, but the pinned manifest contains **104 logical data rows**. The paper should never manually type this count again; it should be generated from the frozen artifact in the same build that produces the PDF or submitted Markdown.

A second substantive issue is evidence-language calibration. The named-shot table calls the infiltration result “independently gated,” but the repository's own priority evidence matrix states that the pressure trace, fitted permeability, and evaluation observable come from the same DE1 shot. It classifies the result as `sign_or_compatibility / same_campaign_not_held_out` and explicitly says it is a wide-bracket, in-sample compatibility check—not a parameter-free or independent prediction. This wording must be corrected everywhere, including captions, public claims, and any abstract or graphical scorecard.

A third issue is that the manuscript currently occupies an unstable middle ground between three publication genres. It is far too long and scientifically detailed for a conventional short software paper, but it does not yet provide the systematic evaluation, related-work positioning, methods detail, or complete figures expected of a full methods/resource article. At 9,923 words before embedded figures and supplements, it is approximately six times the current upper length guidance for a JOSS paper and well above the 3,000–4,000-word guidance of the Journal of Open Research Software. A venue decision is therefore not an administrative afterthought; it determines the structure of the revision.

A fourth issue is missing evaluation of the framework itself. The three demonstrations are persuasive anecdotes, but they do not yet establish how reliably the architecture detects semantic errors, prevents provenance drift, calibrates evidence language, supports reproducibility, or improves reviewer/user decisions. The paper should formulate explicit research questions and evaluate them with a predeclared defect set, mutation tests, clean-room reproduction, and—ideally—independent evidence-label adjudication or an external user workflow.

A fifth issue is novelty positioning. The reference list is almost entirely espresso-domain literature. A paper whose central contribution is provenance-aware, evidence-qualified, executable review must engage with research-software provenance, FAIR and FAIR4RS, W3C PROV, RO-Crate/research compendia, software citation, model cards/datasheets, scientific workflow systems, reproducible computational practice, and verification/validation terminology. The novelty is not that the repository has cards, metadata, or reproducible scripts in isolation. The likely novel contribution is the **joint operationalization** of observable semantics, model-interface compatibility, parameter provenance, evidence relation, claim-producing functions, and negative-composition records for a coupled process-model literature. That distinction needs to be argued rather than assumed.

My overall judgment is therefore positive but firm: **the paper should be revised, not abandoned**. Its strongest contribution is worth publishing. The next draft should be shorter, frozen to a release, generated from authoritative artifacts, explicit about what is implemented versus planned, more rigorous about evidence dimensions, and supported by an evaluation designed to test the framework rather than only illustrate it.

---

## 3. Principal strengths to preserve

### 3.1 A compelling scientific problem

The manuscript identifies a real failure mode in multidisciplinary model integration: two quantities can share a name while differing in physical location, inventory basis, conditioning variables, or measurement operator. The pressure-node, concentration, permeability, grinder-dial, and chemistry examples make this problem tangible rather than abstract.

### 3.2 Refusal to equate executability with validity

The paper repeatedly distinguishes code verification, source-curve reproduction, post-fit reconstruction, within-campaign transfer, and independent empirical evidence. This is one of its strongest features. Many scientific-software papers stop at “tests pass”; Paper 3 asks what each passing test actually supports.

### 3.3 Preservation of negative and blocked outcomes

The failed extraction-plus-swelling composition is an excellent demonstration of why a more complicated model is not automatically a better or more valid one. Retaining the failure, reduction test, parameter lineage, and caveat is scientifically valuable and aligns well with the repository's broader evidence-first ethos.

### 3.4 Distinction between component validity and composition validity

The statement that connecting two individually useful components creates a new model with new assumptions is both correct and important. It is probably the manuscript's most generalizable conceptual contribution. This principle should remain central, but it should be supported by a more formal evaluation and related-work discussion.

### 3.5 Claim producers and release identity

The requirement that manuscript-facing values map to named producers, result paths, units, datasets, components, caveats, and source commits is strong practice. The release identity condition—source tag, manifest commit, and result-bundle commit agreeing—is especially valuable.

### 3.6 Honest limits in the named configuration

The scorecard's decision to leave the exact final cup open is commendable. The paper should retain this example, after correcting the infiltration evidence wording and generating the table directly from a machine-readable record.

### 3.7 Corpus honesty

The manuscript explicitly calls the corpus curated rather than systematic. This is preferable to overstating coverage. The proposed systematic-search upgrade is sensible, although the current paper still needs a reproducible account of how the curated set was assembled.

### 3.8 Generally strong prose and conceptual clarity

The manuscript is thoughtful and unusually candid. It explains difficult distinctions in accessible language, and the examples are relevant to both domain scientists and scientific-software readers. The revision should preserve that clarity while removing repetition and internal project jargon.

---

## 4. Repository-to-manuscript consistency audit

The following items should be corrected before any scientific restructuring, because they affect the factual integrity of the manuscript.

| Item | Manuscript statement | Frozen repository evidence | Assessment and required action |
|---|---|---|---|
| Component total | 25 registered components | Generated count is 25 | **Consistent.** Retain, but generate it at build time and bind it to a release. |
| Manifest total | 70 records in the abstract, §2.1, §6.2, and Table 7 | Pinned `MANIFEST.csv` contains **104** logical data rows | **Stale.** Replace every manual count with generated metadata. Include a test that the manuscript count equals the parsed manifest. |
| Execution roles | Table 1: 11 runtime, 13 calibration, 1 synthesis | Generated table: **12 runtime, 13 calibration, 0 adapters, 0 diagnostics** | **Incorrect.** “Synthesis” is not an execution role in schema v2. Regenerate Table 1 and remove the inline stale copy. |
| Synthesis classification | One component is assigned the role `synthesis` | `brewer2026.coupled_kappa_t` has `execution_role=runtime`, `provenance_class=project_synthesis` | **Incorrect axis.** Explain that the component runs at runtime but originates as a project synthesis. |
| Registry schema | §3.2 foregrounds `kind` as the operational class | Schema v2 marks `kind` as **deprecated** and makes `execution_role`, `provenance_class`, and `evidence_strength` authoritative | **Stale architecture description.** Rewrite §3.2 around the three authoritative axes; mention `kind` only as a compatibility field scheduled for removal. |
| Adapter/diagnostic roles | §3.3 says not all roles are first-class enum values | `observational_adapter` and `diagnostic` are already valid `EXECUTION_ROLES`; there are simply no registered instances | **Incorrect.** Say “schema-supported but currently uninstantiated,” not “not first-class.” |
| Evidence taxonomy | Table 3 includes “Independent external” and “Negative validation” as categories | Code enum uses `controlled_independent`; there is no `negative_validation` evidence-strength value | **Schema mismatch and conceptual mixing.** Align terminology and separate evidence relation from outcome polarity. |
| Generated-table control | Draft status and Appendix A say inline tables are producer-generated and CI-checked so they cannot silently diverge | Inline Table 1 and Appendix A disagree with generated artifacts | **Critical process failure.** Fix the manuscript build/test so this exact drift is impossible, or stop claiming the inline copy is guarded. |
| Infiltration evidence | Table 6: “independently gated” | Evidence matrix: same shot supplies pressure, fitted permeability, and evaluation; classified as `same_campaign_not_held_out` compatibility | **Scientifically overclaimed.** Replace with “same-shot compatibility check across a predeclared porosity bracket.” |
| Installation/readiness | Table 7 says editable install only and packaged release still required | Public `v0.3.0` wheel and source distribution exist; install, API, and supported interpreters are documented | **Stale.** Distinguish the released `v0.3.0` capability from unreleased `0.4.0.dev0` main. |
| Tutorials | Table 7 says internal workflows are referenced and public tutorials are required | Multiple public Colab paths and tutorials are linked from the README | **Stale.** Mark as achieved, while separately recording signed-out acceptance/public-hosting limitations. |
| Governance | Table 7 says contribution guide, issue templates, changelog, and code of conduct are required | `CONTRIBUTING.md`, issue-template infrastructure, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `AUTHORS.md` exist | **Stale.** Replace with remaining governance tasks, not already-completed ones. |
| Public API | Table 7 implies the public API is not yet documented/stable | The release documents `puckworks.__all__`, API guidance, support matrix, and deprecation/stability boundaries | **Partly stale.** State precisely what is stable in `v0.3.0` and what remains development-only. |
| Executability | Title/abstract can be read as implying the full registered corpus is openly executable | The registry has 25 components, while rights, data, scientific-admissibility, release, and public-hosting status differ by component/path; one named component is explicitly rights-blocked | **Needs qualification.** Define separate availability dimensions and avoid one binary “executable” label. |
| Figures | Seven figures are specified but not embedded | No submitted figures to inspect | **Submission blocker.** Central demonstrations cannot be peer reviewed in their intended form. |
| Release snapshot | Manuscript is dated 15 July and describes “current” state | Audit commit is 25 July and includes later scientific and infrastructure changes | **Needs freeze.** Cite a dedicated release/archive and generate the manuscript from it. |

### Reproduction of the manifest count

The pinned manifest count can be reproduced with:

```python
import csv

with open("puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as handle:
    n_records = sum(1 for _ in csv.DictReader(handle))

assert n_records == 104
```

The manuscript should not contain the literal `104` as a hand-maintained fact either. It should consume the generated count from the release artifact so the next corpus addition cannot recreate the same problem.

---

## 5. Major comments

## Major comment 1 — Decide the publication genre before rewriting

The manuscript presently combines:

- a software/resource description;
- a methods proposal for executable evidence review;
- several domain-science results;
- a negative multiphysics composition study;
- an experiment-design agenda;
- a data-governance discussion; and
- a release-readiness assessment.

That breadth is intellectually interesting, but it prevents the paper from satisfying a clear journal contract.

### Route A: short software paper

For JOSS or a similar venue, the paper would need to be a short description of the software's purpose, research application, functionality, scholarly significance, and availability. The current JOSS paper guidance is 750–1,750 words, and the review emphasizes sustained public development, installation, documentation, tests, community significance, and research use. The detailed scientific demonstrations should live in companion papers, documentation, or a technical report. The repository's public history and external engagement should also be assessed against current screening guidance before submission.

### Route B: research-software/resource article

For the Journal of Open Research Software, the manuscript would still require substantial reduction toward its 3,000–4,000-word guidance. It could retain one or two demonstrations, but not the current full scientific narrative.

### Route C: full methods/resource paper

This is the most natural fit for the current intellectual ambition. Under this route, the paper may retain the scientific cases, but it must add:

- a rigorous related-work section;
- explicit research questions;
- a systematic evaluation of the architecture;
- a reproducible corpus-construction method;
- complete figures and source-data bundles;
- stronger statistical reporting;
- a frozen release and archive; and
- a clearer distinction between current implementation, demonstrated behavior, and roadmap.

**Recommendation:** Treat the current manuscript as the basis of a full methods/resource paper and create a separate short software paper later. The framework's most interesting contribution—the evidentiary discipline required before model composition—would be cramped or lost in a 1,750-word format.

---

## Major comment 2 — Repair the manuscript-generation pipeline before relying on it as evidence

The manuscript's central methodological promise is that tables and claims are generated from authoritative sources and cannot silently drift. Yet its own Table 1 and Appendix A are stale. This is a valuable discovery, because it reveals exactly the kind of failure the system is intended to prevent.

Do not treat this as a cosmetic count correction. Treat it as a failed acceptance test for the Paper 3 publication pipeline.

### Required fix

1. Make generated tables single-source inclusions rather than manually copied Markdown. For example, render the paper through a build step that inserts `table1_registry_overview.md` and `appendixA_component_catalog.md` directly.
2. If the source format cannot include files, add a parser that extracts the manuscript table and compares a normalized representation with the generated artifact.
3. Add a CI test for every manuscript-facing generated object, including counts in prose and the abstract.
4. Expose the manuscript-build command in the release runbook.
5. Archive the resulting manuscript source, tables, figures, data, environment record, and checksums under one commit/DOI.
6. Add a regression test using the exact `synthesis`→`runtime/project_synthesis` change that produced this drift.

The paper could even report this as a development finding: the first version guarded generated artifacts but not their copied representation in prose. That would strengthen, rather than weaken, the paper if presented transparently and fixed.

---

## Major comment 3 — Rewrite the registry architecture around schema v2

Sections 2.1, 3.2, 3.3, Table 1, and Appendix A mix the legacy `kind` field with the new typed axes. The authoritative model is now:

- `execution_role`: what the component does when used;
- `provenance_class`: where the component comes from; and
- `evidence_strength`: the strongest/default evidence class assigned to the component, without automatically upgrading individual claims.

The legacy `kind` remains only for backward compatibility. A synthesis component maps to runtime execution while carrying `project_synthesis` provenance. Adapters and diagnostics are legal execution roles even though the current generated table contains zero registered instances.

### Required rewrite

- Replace the field table in §3.2 with the actual schema v2 fields.
- State explicitly that `kind` is deprecated and not authoritative.
- Replace the five-role prose taxonomy with the exact code enum plus a separate provenance taxonomy.
- Explain that no adapter or diagnostic component is currently registered; adapter logic remains partly embedded in analyses/harnesses.
- Generate all role/provenance counts from code.
- Clarify whether `evidence_strength` on a component is a default summary, while each gate and claim can carry a different relationship. The paper currently risks suggesting one component-wide label controls every claim.
- State the planned removal/version policy for `kind`, or avoid promising its removal until a public API version is chosen.

This change will also make the paper's architecture more conceptually coherent: “synthesis” answers where the composition originated, not necessarily what it does at runtime.

---

## Major comment 4 — Separate evidence relation, result outcome, artifact role, and public badge

The paper correctly rejects a single scalar validation score, but its current taxonomy still combines unlike concepts in one table.

For example:

- `code_verification`, `source_curve_reproduction`, and `within_campaign_held_out` describe an **evidence relationship**;
- “negative validation” describes an **outcome or interpretation**;
- `proposed_experiment` describes a **planned artifact/status**, not evidence already obtained;
- `exploratory_synthesis` partly describes the **origin/role of a model**;
- `OBSERVED`, `RECONSTRUCTED`, `PREDICTED`, and `EXPLORATORY_SIMULATION` are **public communication badges**.

These dimensions should not occupy one flat hierarchy.

### Suggested normalized model

| Axis | Example values | Question answered |
|---|---|---|
| Evidence relationship | code verification; source reproduction; same-data reconstruction; within-campaign held out; controlled independent; sign/compatibility | How is the claim related to the data or specification? |
| Outcome | pass; fail; inconclusive; acknowledged exception | What happened in the declared check? |
| Artifact/model role | published port; project model; project synthesis; proposed experiment | What kind of object produced or motivates the claim? |
| Claim badge | observed; reconstructed; predicted; exploratory simulation | How may the result be communicated visually? |
| Independence metadata | same data as fit; same campaign; held out condition; external system | What information is shared between fit and evaluation? |
| Scope/caveat | explicit text and validity range | What must the reader not infer? |

Under this structure, the failed swelling composition would be:

- evidence relationship: post-fit/same-data diagnostic;
- model role/provenance: project synthesis;
- outcome: failed declared performance check, while reduction bookkeeping passes;
- badge: exploratory simulation;
- interpretation: this composition degrades the fit; swelling itself is not disproved.

Replace “negative validation” with **“negative result,” “failed declared check,”** or a similarly unambiguous term. “Negative validation” can sound as though failure itself validates a universal negative claim.

Also align the paper vocabulary exactly with the code. The code uses `controlled_independent`, whereas Table 3 says “Independent external.” Either rename the enum through a versioned migration or use the code term in the manuscript and define it clearly.

---

## Major comment 5 — Resolve the contradiction between evidence vectors and the “weakest link” statement

The abstract says each output retains the evidence status of “the weakest load-bearing link.” Section 5 then correctly says evidence is not one scalar score and that multiple evidence entries should coexist rather than collapse to a strongest or weakest badge.

Those positions are not automatically compatible. A weakest-link rule requires an ordering across unlike evidence dimensions; the manuscript elsewhere rejects such a universal ordering.

### Suggested correction

Replace the weakest-link sentence with something such as:

> Each claim retains the provenance, evidence relationship, and caveats of every dependency on which it relies. The scorecard may identify the limiting caveat for a specified use, but the underlying evidence is not reduced to one universal rank.

This preserves the useful engineering intuition—one unresolved interface can block a particular end-to-end claim—without implying that source reproduction, code verification, held-out prediction, and rights status can be ordered on one scale.

---

## Major comment 6 — Correct the infiltration overclaim immediately

The manuscript's Table 6 describes the Foster sharp-front infiltration adapter as “independently gated on first-drop/dead-volume bracket for the fixture.” The generated evidence matrix says otherwise:

- the measured pressure trace comes from the same DE1 shot;
- permeability comes from `kappa_fitted=1.196`, fitted to that same shot's flow;
- fit and evaluation both use `de1_fixtureA`;
- only the porosity-bracket endpoints are a priori;
- the bracket is wide; and
- the formal classification is `sign_or_compatibility / same_campaign_not_held_out`.

The repository explicitly states that the result does **not** demonstrate a parameter-free prediction independent of the evaluated data.

### Required replacement

Use wording such as:

> Same-shot compatibility check: a sharp-front calculation driven by the shot's measured pressure and a permeability inferred from that shot brackets the observed first-drip time across a predeclared porosity range. This is not an independent prediction.

Then audit all figures, captions, claim records, notebooks, and public explanations for the phrases “independent,” “parameter-free,” or “validation” in connection with this gate.

This correction is particularly important because the paper's central contribution is calibrated evidence language. An overclaim in its showcase scorecard would undermine reviewer trust disproportionately.

---

## Major comment 7 — Define what “executable” means at each layer

The title and abstract use “executable” as a defining property, but the repository contains several different notions of availability:

1. registered in the metadata catalog;
2. importable/resolvable in a development checkout;
3. numerically executable with available dependencies and data;
4. scientifically admissible for a stated configuration;
5. legally permitted for local/private use;
6. redistributable in an archive;
7. cleared for public hosted execution; and
8. included in the latest stable release.

These are not equivalent. The rights-blocked `grudeva2025.reduced` entry is an obvious example, while public-hosting preflights create additional distinctions. The released `v0.3.0` Guided Pull and unreleased `0.4.0.dev0` Laboratory also expose different capabilities.

### Required action

Add a machine-readable availability matrix with fields such as:

```text
registered
importable
runnable_local
required_data_available
scientifically_eligible
redistribution_license_status
public_hosting_status
included_in_release
blocking_reason
```

Report counts for each dimension rather than saying simply that all 25 components are executable. In the title, “executable review” may be safer and more accurate than “executable registry,” because the review machinery can execute even when an individual model remains blocked or reference-only.

---

## Major comment 8 — Distinguish implemented capability from architectural intent

The manuscript sometimes describes a mature component-composition platform, while the README appropriately emphasizes that the models are not fused into a universal coupled simulation, the Espresso Model Relay is assumption-rich and educational, and the released Guided Pull uses a narrower model path.

The paper needs an implementation-status table that separates:

- **specified in the architecture**;
- **implemented in code**;
- **covered by tests/gates**;
- **used in a manuscript demonstration**;
- **available in the stable release**;
- **available only on development `main`**; and
- **publicly hosted/rights-cleared**.

Examples requiring this distinction include first-class adapters, the empty observables stage, arbitrary multi-stage configuration, unit-aware typing, the named-shot scorecard, and the community-corpus workflow.

Avoid sentences that imply arbitrary safe composition is already automated. Puckworks currently makes incompatibilities visible and supports selected explicit configurations; it does not appear to prove compatibility or automatically synthesize any chosen component set. That limitation is acceptable and scientifically honest, but it must be clear.

---

## Major comment 9 — Add a rigorous related-work and novelty section

The paper currently cites the espresso sources it registers but almost no literature on the methods it claims to advance. This is the largest scholarly-positioning gap.

At minimum, compare Puckworks with the following traditions:

| Related area | Questions Paper 3 should answer |
|---|---|
| FAIR data and FAIR4RS | Which findability, accessibility, interoperability, and reusability principles are implemented, and where does evidence qualification go beyond them? |
| W3C PROV and provenance ontologies | Why use the current claim/source/component schema rather than—or in addition to—a standard provenance representation? Can exports map to PROV entities, activities, and agents? |
| RO-Crate and research compendia | How does the release bundle relate to established packaging of code, data, workflows, metadata, and outputs? |
| Software citation principles | How are software versions, contributors, releases, dependencies, and derived artifacts cited? |
| Model cards and datasheets | What is new about Puckworks cards? Is the distinctive feature their binding to executable gates and claim verbs? |
| Scientific workflow systems | How is the framework different from workflow DAGs such as CWL, Snakemake, Nextflow, or Galaxy? Is the novelty semantic/evidentiary rather than orchestration? |
| Unit-aware and schema-aware scientific computing | Why are named dataclasses sufficient at present, and what errors remain because dimensions are documented rather than statically enforced? |
| Verification, validation, and uncertainty-quantification frameworks | How does the evidence taxonomy relate to established V&V terminology? |
| Reproducible computational-research practice | Which existing principles are implemented through producers, locks, hashes, frozen environments, and source-data exports? |
| Interchange standards for models | What can be learned from SBML/FMI-like explicit interfaces, even if those standards are not directly applicable to espresso physics? |

Useful starting references include:

- Wilkinson et al., “The FAIR Guiding Principles for scientific data management and stewardship,” *Scientific Data* (2016), DOI `10.1038/sdata.2016.18`.
- Chue Hong et al., *FAIR Principles for Research Software (FAIR4RS Principles)* (2022), DOI `10.15497/RDA00068`.
- Barker et al., “Introducing the FAIR Principles for research software,” *Scientific Data* (2022), DOI `10.1038/s41597-022-01710-x`.
- W3C, *PROV Overview* and the associated PROV recommendations.
- Soiland-Reyes et al., “Packaging research artefacts with RO-Crate,” *Data Science* (2022), DOI `10.3233/DS-210053`.
- Smith, Katz, and Niemeyer, “Software citation principles,” *PeerJ Computer Science* (2016), DOI `10.7717/peerj-cs.86`.
- Mitchell et al., “Model Cards for Model Reporting,” FAT* (2019), DOI `10.1145/3287560.3287596`.
- Gebru et al., “Datasheets for Datasets,” *Communications of the ACM* (2021), DOI `10.1145/3458723`.
- Sandve et al., “Ten Simple Rules for Reproducible Computational Research,” *PLOS Computational Biology* (2013), DOI `10.1371/journal.pcbi.1003285`.
- Wilson et al., “Good Enough Practices in Scientific Computing,” *PLOS Computational Biology* (2017), DOI `10.1371/journal.pcbi.1005510`.

The novelty claim should then be narrowed and sharpened. A defensible formulation may be:

> Puckworks operationalizes, in one coupled-process modeling resource, semantic observable contracts, parameter-level provenance, evidence-qualified gates, producer-bound manuscript claims, and explicit records of failed or blocked compositions.

That is stronger than a broad claim to have invented executable reviews in general.

---

## Major comment 10 — Evaluate the framework, not only the espresso models

The demonstrations show that the framework can represent important problems, but they do not quantify whether it reliably catches them. Add an evaluation section organized around explicit research questions.

### Suggested research questions

**RQ1 — Semantic defect detection.** Can the contracts and adapters detect predefined unit, node, basis, and missing-observable errors before analysis?

**RQ2 — Provenance and manuscript drift.** Can the release/claim machinery detect stale counts, stale result bundles, mismatched commits, hard-coded values, missing source-data identifiers, and dirty builds?

**RQ3 — Evidence-language calibration.** Do independent reviewers assign the same evidence relationship and permitted verb when given the decision guide?

**RQ4 — Composition safety.** Do reduction, conservation, state-identity, and baseline tests detect deliberately introduced coupling errors?

**RQ5 — Reproducibility and usability.** Can an external user install a frozen release, regenerate the claim bundle and figures, and obtain matching hashes without local/private files?

### Suggested evaluation design

Create a predeclared defect corpus containing, for example:

- pump pressure substituted for bed pressure drop;
- bar supplied to a pascal field;
- permeability supplied in µm² to an SI closure;
- total roasted content substituted for extractable inventory;
- named-solute mass averaged with TDS mass;
- grinder dial matched across devices without an adapter;
- missing time base coerced to zero;
- source-curve reproduction mislabeled independent validation;
- same-data reconstruction mislabeled held-out prediction;
- a hard-coded manuscript number without a producer;
- stale `source_commit` in a result bundle;
- a broken exact-reduction limit in the synthesis component;
- double counting of porosity change; and
- a rights-blocked component routed to public hosted execution.

Report the number detected, where detection occurs, false positives, false negatives, and which defects remain outside the current type system. A mutation-testing approach would be especially persuasive because it evaluates the guards themselves rather than merely reporting that the unmutated suite passes.

For evidence labels, have at least two people independently classify a sample of claims using the decision guide, report agreement, and publish adjudications. If only one curator currently assigns labels, say so and frame the taxonomy as a versioned expert judgment rather than an objective ground truth.

For reproducibility, commission a clean-room run from a fresh environment and publish:

- operating system and interpreter;
- installation command;
- exact release asset hash;
- command to regenerate Paper 3 artifacts;
- runtime and resource requirements;
- expected exclusions caused by rights/data restrictions;
- resulting artifact hashes; and
- any manual steps.

This evaluation would transform the paper from a persuasive project narrative into a testable methods contribution.

---

## Major comment 11 — Keep the scientific demonstrations, but reduce duplication with companion papers

The null-first temporal section contains detailed RMSE values, held-out comparisons, and scientific interpretation that apparently belong primarily to the companion temporal-inference paper. Paper 3 should demonstrate how Puckworks records the comparison without becoming a second full presentation of the same science.

### Recommended ownership split

**Paper 3 should own:**

- the comparison schema;
- observable matching;
- fit/evaluation provenance;
- evidence labels and permitted verbs;
- producer-bound claim output;
- one compact representative result; and
- the lesson that error tables without provenance invite overinterpretation.

**The companion paper should own:**

- detailed temporal-model derivations;
- full pressure-by-pressure results;
- residual analyses;
- uncertainty calculations;
- mechanistic interpretation; and
- the primary scientific conclusion.

Likewise, the response-surface result, permeability disagreement, fast-fraction comparison, and swelling composition should each have an explicit claim owner. Paper 3 may use them as method demonstrations, but it should not accumulate every precise scientific result produced by the repository.

Add a claim-ownership table to the supplement, and make the strict release gate fail if the same headline is asserted as a primary claim in two manuscripts without an explicit cross-reference.

---

## Major comment 12 — Complete and consolidate the figures

Seven figures are specified but absent. This prevents a full review because several central claims depend on visual comparison, residual shape, and evidence-chain structure.

I recommend four main figures rather than seven:

### Figure 1 — Architecture and status layers

Show two linked graphs:

- the physical process/component graph; and
- the evidence/provenance graph connecting components, datasets, gates, claims, producers, and release artifacts.

Use visual distinctions for implemented, planned, blocked, development-only, and released elements.

### Figure 2 — Semantic-defect detection

Combine the pressure-node, inventory, unit, and missing-time-base cases into a before/after contract-linting figure. Include at least one deliberately mutated input and the exact failure message.

### Figure 3 — Evidence-qualified comparison and failed composition

Panel A can show the null-first ladder with evidence relations. Panel B can show the extraction-only, constant, and composite traces/RMSEs. The figure must state that the comparison is same-data/post-fit and that the negative result applies only to the tested composition.

### Figure 4 — Generated illustrative scorecard and experiment promotion path

Generate the entire figure from the machine-readable scorecard. Show each stage's component, data source, evidence relation, availability/rights status, caveat, and next measurement. Correct the infiltration cell.

Move the detailed response-surface plot, corpus diagram, full component catalog, and extended disagreement-to-experiment matrix to the supplement unless the target journal permits a longer figure set.

Every figure should ship with:

- machine-readable source data;
- a named producer;
- source commit;
- environment metadata;
- vector and raster export;
- alt text;
- a caption that states fit/evaluation relationships and what is not supported; and
- a test that headline values in the caption match the producer output.

---

## Major comment 13 — Strengthen quantitative and statistical reporting

The manuscript often gives precise values without enough information for a reader to assess their uncertainty or reproduce the calculation from the paper alone.

### Mixed-unit chemistry example

For the 18.27%, 19.38%, and 19.62% cell means and Welch interval, report:

- sample size in each cell;
- the observational unit and whether shots/replicates are independent;
- the exact conditioning rule for the “central operating cells”;
- whether the cell selection was specified before looking at the result;
- the extraction-yield formula and dose convention;
- variance estimates, degrees of freedom, and exact confidence-interval method;
- treatment of repeated measurements or campaign clustering; and
- the producer and manifest identifiers.

A Welch interval may be mathematically computable while still overstating independence if replicates share preparation batches, instruments, or fitted preprocessing.

### Response-surface vertex

For the adjusted `R²≈0.64` and vertex near 1.74, report:

- full model formula;
- retained terms and model-selection rule;
- coefficient estimates and uncertainty;
- achieved versus commanded covariates;
- location of the vertex relative to the design boundary;
- sensitivity to influential observations and alternative specifications; and
- a confidence region or bootstrap distribution for the vertex.

The manuscript correctly says the vertex is conditional; the quantitative presentation should make that conditionality visible.

### Temporal RMSEs

For the 0.573, 0.648, 0.116, and 0.096 g s⁻¹ values, report:

- number and cadence of scored observations;
- interpolation/resampling method;
- exact 15–95 s interval rationale;
- handling of missing points and startup transients;
- parameter fitting for each branch;
- residual autocorrelation;
- uncertainty or sensitivity of the ranking; and
- whether the “best constant” value in text, evidence matrix, and figure is identical. The evidence matrix currently refers to a flat null around 0.603 in one claim while the manuscript reports approximately 0.573; reconcile the definitions, datasets, or intervals rather than letting two baselines appear interchangeable.

### Tamped-permeability disagreement

For the ~13–31× range and median ~20×, report:

- matched operating points;
- exact equations and parameter values;
- porosity range;
- viscosity convention;
- dimensional conversions;
- uncertainty propagation; and
- why the comparison is informative despite both closures being outside or near the edge of their evidence domains.

### Fast-extracting-fraction comparison

For the newly added 5–9× magnitude difference, define both quantities mathematically and report:

- PSD basis and normalization;
- fines cutoff;
- shell-thickness rule and discretization dependence;
- measurement/digitization uncertainty;
- range over which the source closure was calibrated;
- where the cross-model application extrapolates; and
- whether the result is a semantic comparison, qualitative trend check, or empirical test.

This is a valuable example, but the paper must not turn a cross-model extrapolation into a validation claim.

### Ingestion incident

For the “roughly eleven thousand” discarded records, either freeze and cite the exact ingestion snapshot or use a public synthetic fixture reproducing the schema error. The current paper says corpus-derived numbers are not reported, then reports an approximate corpus count in the defect narrative. Resolve that tension.

---

## Major comment 14 — Reconsider the external community-corpus section

The external corpus introduces a substantial ethical, privacy, licensing, governance, and reproducibility burden but contributes no frozen result to the current paper. It also pulls attention away from the manuscript's core model-review contribution.

### Preferred option

Move §6.6 to a supplement or future-work/data-governance paper. Retain the ingestion-contract bug as a public synthetic regression case that does not require access to the underlying human-contributed records.

### If the corpus remains in the main paper

Document at least:

- the exact data-owner agreement and permitted research/publication uses;
- whether contributors consented to research use or what lawful/ethical basis applies;
- whether an institutional ethics/IRB review or formal determination was required and obtained;
- data minimization and retention period;
- who can access raw and normalized records;
- deletion/withdrawal handling;
- small-cell and linkage/reidentification controls;
- whether free text is ever processed before deletion;
- the threat model for the retained hashed identifier;
- incident response;
- snapshot/version provenance; and
- aggregate disclosure rules.

Use **“pseudonymized”** rather than implying anonymization. A salted one-way hash retained for repeated-shot cohorting is still a persistent linkage key. Do not describe owner permission and attribution as if they alone resolve all participant-privacy or research-ethics questions.

The phrase “privacy-preserving aggregate summaries” should be replaced with a more precise description of the disclosure controls actually applied.

---

## Major comment 15 — Make the curated-corpus method reproducible now

It is appropriate not to call the corpus systematic. Nevertheless, “curated” cannot mean undocumented or irreproducibly selected.

Add a current corpus-construction method containing:

- seed papers and why they were selected;
- databases, repositories, and grey-literature sources searched;
- search dates;
- search strings, even if exploratory;
- backward and forward citation tracing;
- inclusion and exclusion rules;
- handling of derivative models and duplicate datasets;
- language limits;
- treatment of inaccessible or rights-blocked sources;
- how project-created components are distinguished from published ports; and
- how the search changed in response to identified interface gaps.

Also report more informative denominators than component count alone:

- unique source publications;
- unique model lineages;
- unique empirical campaigns;
- unique datasets/manifest records;
- components by provenance class;
- components by evidence relation;
- components with independent data;
- rights/data-blocked components; and
- components used only as calibration/reference objects.

Twenty-five components do not represent 25 independent studies or 25 independent bodies of evidence. The generated summary should make this impossible to misread.

---

## Major comment 16 — Clarify the scope and limitations of typed contracts

The manuscript acknowledges that Python dataclasses with comments are not a full dimensional type system. That caveat should be more prominent because “typed contracts” can suggest stronger guarantees than the implementation provides.

State explicitly which failures are caught by:

- field naming;
- enum/schema validation;
- runtime range checks;
- adapter assertions;
- manifest metadata;
- static type checking, if any;
- unit libraries, if any; and
- human review only.

Then report known residual risks, such as:

- a plausible pascal value supplied to the wrong pressure-node field;
- a quantity with correct dimensions but wrong physical basis;
- a scalar representing the wrong spatial average;
- a value within a broad guard range but in the wrong unit scale;
- source metadata incorrectly curated; and
- two semantically incompatible objects that satisfy the same Python type.

The permeability guard `10⁻18 < k < 10⁻6 m²` is useful as a coarse sanity check, but it is not proof that the value uses the correct unit, closure, material, or regime. Phrase it accordingly.

A mutation-test table showing which defects each layer catches would turn this limitation into a strength.

---

## Major comment 17 — Generate the named-shot scorecard and rename it more carefully

“Named shot” suggests a uniquely identified, reproducible empirical event. The current configuration appears to combine an illustrative DE1 fixture, nominal dial, dose/beverage ratio, chemistry lineage, and temperature range, with open grinder and pressure-node lineage.

Until a frozen shot record and exact lineage are supplied, call it an **“illustrative configuration evidence ledger”** or **“illustrative shot configuration.”**

Generate Table 6 and Figure 4 from one machine-readable record containing:

- configuration ID and source commit;
- actual shot/dataset identifiers where applicable;
- each stage/component;
- parameter sources;
- fit and evaluation datasets;
- evidence relationship;
- outcome;
- validity range;
- rights/data availability;
- released/development status;
- caveat;
- required adapter; and
- promotion measurement.

The final row should remain open. That is one of the paper's most persuasive choices.

Also define the Forchheimer diagnostic and the meaning of `Fo_F≈0.86–5.7`, including how the onset criterion is chosen and whether it is a regime flag rather than a validated correction.

---

## Major comment 18 — Temper cross-domain generalization

Section 12.4 says the architecture applies to drying, filtration, chromatography, fermentation, reactive transport, battery electrodes, and biomedical perfusion. The pattern plausibly transfers, but the paper demonstrates it only in espresso.

Use one of two approaches:

1. change the claim to “a proposed transferable pattern demonstrated in espresso”; or
2. include a compact external-domain mapping showing how one non-espresso case would populate stages, observable contracts, evidence relationships, and composition checks.

Do not imply empirical generalization across domains from a single-domain case study. The general argument is conceptual, not yet evaluated across fields.

---

## 6. Section-by-section comments

## Title

The current title is accurate in topic but slightly awkward in emphasis. “Executable registry” can be misread as meaning every registered model is openly runnable, and “evidence registry” is not yet anchored to established terminology.

Recommended title:

> **Puckworks: a provenance-aware component registry for executable review of espresso process models**

Other viable options:

- **Puckworks: typed interfaces and evidence provenance for comparing espresso process models**
- **Puckworks: executable evidence review for heterogeneous espresso process models**
- **Puckworks: preventing invalid comparison and composition in espresso process modeling**

The first is the best balance of accuracy, accessibility, and continuity with the project.

## Draft-status block

The block is admirably candid, but it currently makes a false operational claim: the inline generated tables have drifted. Update the draft date, link the exact frozen commit, state whether the counts are release-generated, and do not claim CI protection until the manuscript representation is actually tested.

## Abstract

The abstract is too dense and contains too many exact scientific values for a framework/resource paper. It also includes the weakest-link contradiction and stale manifest count.

Required changes:

- generate the component and manifest counts from the frozen release;
- replace “weakest load-bearing link” with dependency-preserving evidence language;
- qualify “general method” as a demonstrated/proposed workflow unless broader evaluation is added;
- reduce the number of numerical examples;
- distinguish registered from runnable/redistributable components;
- avoid implying that all adapters/configurations are implemented; and
- state the formal evaluation, once added.

A suggested replacement abstract appears in §9 below.

## Introduction

The introduction explains the domain problem well. Add citations for the broader claims about coupled-process model integration, provenance, and scientific-software validation. End with explicit contributions, preferably four numbered items:

1. a versioned component/evidence/provenance schema;
2. executable semantic and composition checks;
3. producer-bound claim and release infrastructure; and
4. an evaluation showing what defects the system catches and what remains uncaught.

Avoid saying the same problem occurs in many other domains without references or a narrower formulation.

## Section 2 — Scope and corpus construction

The distinction between curated and systematic is good. Correct the counts and role totals, and add a reproducible account of current curation rather than deferring all search rigor to future work.

Table 1 should be inserted directly from the generated artifact. Add provenance-class and evidence-strength summaries, perhaps in the supplement. Clarify that the empty observables stage is architectural intent rather than current functionality.

## Section 3 — Registry architecture

Rewrite around schema v2. Define the difference between a component, a configuration, a calibration chain, an adapter, a harness, and a synthesis. Readers need to know which objects are formal code entities and which are conceptual terms.

The “one component per occupied runtime stage” description may be too restrictive or too abstract for feedback loops and parallel mechanisms. Consider expressing configurations as a typed dependency graph with explicit input/output contracts and cardinality rules. If that graph is not yet implemented, say so.

## Section 4 — Typed contracts

This section is conceptually strong. Add a formal schema excerpt, a version-migration example, and a test matrix showing enforcement. Correct any mismatch between contract schema 0.6 and registry schema v2 by naming them as separate versioned schemas.

The pressure callback's bar-gauge/Pa split should either be resolved before submission or presented as a deliberately retained migration case with an executable deprecation path. A high-risk unresolved unit inconsistency in the paper's own core contracts deserves a tracked deadline.

The fast-fraction paragraph is useful but newly dense. Consider moving the detailed 5–9× result to a boxed example or supplement and retaining only the semantic point in the main text.

## Section 5 — Evidence taxonomy

This section requires the axis separation described above. Replace “Negative validation,” align terms with code, and show how component-level evidence differs from gate-level and claim-level evidence.

Add a decision tree or worked examples. For every category, specify:

- required metadata;
- allowed verbs;
- prohibited verbs;
- fit/evaluation independence requirements; and
- how an outcome is represented.

## Section 6 — Provenance and reproducibility

This section is one of the manuscript's strongest. Update the manifest count, distinguish the stable release from development main, and generate environment versions rather than typing them manually.

A complete transitive lock or container digest should be a submission requirement, not merely a recommendation, if the paper's reproducibility claims depend on exact numerical regeneration.

The community-corpus subsection should move unless the paper reports a frozen, ethically and legally documented result. The ingestion bug can be preserved through a synthetic fixture.

## Section 7 — Observable and unit linting

This is a good demonstration. It needs a formal defect/test design and complete statistical reporting. The diffusivity erratum should cite the correction record or author correspondence appropriately and distinguish the original authors' correction from Puckworks' verification contribution.

The ingestion example should not report an approximate corpus number while §6.6 says corpus-derived numbers are not reported. Freeze it or make it synthetic.

## Section 8 — Null-first comparison

Condense this section and transfer the detailed science to the companion manuscript. Paper 3 should show the evidence metadata attached to each row, not reproduce the complete scientific narrative.

Reconcile the constant-baseline RMSE values and provide a compact table with fit source, evaluation source, free parameters, evidence relation, and permitted interpretation.

## Section 9 — Failed composition

This is an excellent centerpiece. Replace “negative validation” with “failed composition check” or “negative result.” Show the reduction test and the new coupling assumptions explicitly.

The manuscript should say whether the composite's poor RMSE was known before the configuration/evaluation metric was fixed. If the example was selected after observing the result, that is acceptable for a case study but should not be framed as a prospective validation experiment.

## Section 10 — Experiment design

The disagreement-to-measurement map is valuable, but some rows are still expert proposals rather than generated optimization results. Clarify whether “rank experiments by discrimination, feasibility, and required new parameters” is currently implemented or a proposed workflow.

For each recommendation, link the directional prediction to a producer and identify whether the competing models truly make opposite predictions under a matched configuration. Where they only differ in magnitude, state the minimum measurement precision required to discriminate them.

## Section 11 — Illustrative scorecard

Rename and generate it. Correct the infiltration row. Add availability/rights/release status, because an occupied registry slot is not the same as an executable public stage.

Retain the open final cup and the distinction between per-shot refitting and frozen-parameter prediction.

## Section 12 — Discussion

The three principal lessons are strong but repetitive. Consolidate:

1. semantics must precede comparison;
2. evidence does not transfer automatically through composition; and
3. executable reviews should produce blocked claims and discriminating experiments, not only fitted outputs.

Temper the cross-domain claim or add a non-espresso mapping.

## Section 13 — Limitations and readiness

Table 7 must be completely regenerated. Separate:

- achieved in stable `v0.3.0`;
- achieved only on development main;
- verified by CI;
- awaiting signed-out/public acceptance;
- rights/data blocked;
- required for Paper 3 release; and
- route-specific journal requirements.

The current table lists several already-completed items as missing, which makes the paper look less mature while also obscuring the real gaps: DOI/archive, paper figures, independent reproduction, framework evaluation, rights audit, corpus method, and external adoption.

## Conclusion

The conclusion is effective but should say “demonstrations illustrate” rather than implying the selected cases fully validate the general method. Add one sentence on the framework evaluation and one on remaining limitations after those sections are completed.

## Software/data availability and back matter

The placeholders for authors, correspondence, contributions, funding, competing interests, and acknowledgments are submission blockers. Align authorship and software citation across the manuscript, `AUTHORS.md`, `CITATION.cff`, release metadata, and eventual archive, using the target journal's authorship and CRediT policies.

Do not infer authorship solely from commits; document substantive contributions. Include a software-use and generative-AI disclosure if required by the selected journal.

The availability statement should cite an immutable archive DOI, not only GitHub, and should enumerate which source datasets are redistributed, retrieved, hashed, derived, or unavailable.

## Figure specifications and supplements

Convert specifications into actual producer-generated figures. The supplement plan is strong but too expansive unless automated. Prioritize the minimum set needed to independently reproduce every main claim.

## Appendix A

Remove the inline hand-copied catalog. Include or render the generated catalog directly. The current mismatch is evidence that a copied appendix defeats the purpose of generation.

## Appendix B

The minimal claim record is useful. Add:

- evidence relationship;
- fit datasets;
- evaluation datasets;
- independence relationship;
- outcome;
- uncertainty method;
- parameter provenance;
- transformation/adapter identifiers;
- availability/rights status;
- producer version/hash; and
- parent claims/dependencies.

A `source_commit` alone is insufficient if source data, external APIs, or environments can change independently.

## References

Expand substantially beyond espresso literature. Use consistent bibliographic formatting, include DOIs where available, cite the exact software release/archive, and replace the companion-paper placeholder with a stable preprint or clearly label it as unpublished material that cannot independently support a claim.

---

## 7. Quantitative claim reporting checklist

Before submission, each headline should have the following minimum record.

| Claim/example | Minimum additions required | Current principal risk |
|---|---|---|
| 25 components | generated count, release version, role/provenance breakdown | component count mistaken for independent evidence breadth |
| 104 manifest records | generated count, manifest hash, record definition | stale manual count and ambiguity between rows, datasets, and observations |
| 170/212.4/224 kg m⁻³ saturation values | exact source/configuration and semantic definitions | readers may still interpret them as competing estimates of one parameter |
| Fast fraction differs 5–9× | formulas, PSD basis, calibration range, extrapolation caveat, uncertainty | cross-model semantic experiment mistaken for empirical validation |
| Raw EY means and Welch interval | n, unit of analysis, conditioning, df, dependence, producer | apparently precise inference without enough design context |
| Response-surface vertex 1.74 | formula, coefficients, uncertainty, boundary/sensitivity | fitted feature mistaken for observed optimum |
| Ingestion failure around 11,000 records | frozen snapshot or synthetic fixture, exact producer, ethics scope | unfrozen human-data count and non-reproducible anecdote |
| Temporal RMSE ladder | sample count, interval, preprocessing, fit/eval provenance, uncertainty | in-sample and transferred models compared as if epistemically equivalent |
| LOPO RMSEs | exact holdout definition and reused information | “held out” read as external validation |
| Composite RMSE 0.648 | exact baseline definition, predeclared metric, same-data label | failure generalized from one composition to swelling broadly |
| Tamped permeability 13–31× | shared points, equations, viscosity, uncertainty, domain limits | comparison outside validated domains interpreted as adjudication |
| Infiltration first-drop bracket | same-shot inputs, porosity bracket, observed threshold, no independence claim | current text explicitly overstates independence |
| `Fo_F≈0.86–5.7` | definition, derivation, threshold, sensitivity | regime flag mistaken for validated inertial correction |
| Ramp sensitivity ≈6.6% | adapter definition, baseline, producer, uncertainty | software-adapter sensitivity read as observed physical effect |

---

## 8. Suggested framework-evaluation table for the revised paper

A concise main-text evaluation could look like this once the tests are implemented:

| Evaluation family | Predeclared cases | Detected | Missed | False positives | Evidence produced |
|---|---:|---:|---:|---:|---|
| Unit and scale defects | TBD | TBD | TBD | TBD | contract failures and mutation report |
| Observable/node/basis defects | TBD | TBD | TBD | TBD | adapter/semantic-lint report |
| Provenance/commit drift | TBD | TBD | TBD | TBD | release-gate report |
| Hard-coded/stale manuscript values | TBD | TBD | TBD | TBD | claim-producer and manuscript-build report |
| Evidence-label misstatements | TBD | TBD | TBD | TBD | dual-reviewer adjudication |
| Composition/reduction defects | TBD | TBD | TBD | TBD | reduction, conservation, and baseline tests |
| Rights/publication-routing defects | TBD | TBD | TBD | TBD | rights-preflight report |
| Clean-room reproduction | one or more environments | pass/fail | — | — | hashes, logs, runtime, exclusions |

Do not populate this with retrospective success-only examples. Define the defect set first, include cases the current framework cannot catch, and report those limitations.

---

## 9. Suggested revised abstract

The following is a possible replacement for a full methods/resource-paper route. Counts must still be generated from the final frozen release.

> Published espresso models describe different stages of brewing using state variables, units, pressure locations, inventory bases, measurement operators, and validation designs that are not automatically compatible. Connecting models by matching similarly named quantities can therefore produce a numerically smooth but scientifically incoherent calculation. We present Puckworks, a provenance-aware component registry and executable-review framework for espresso process models. The framework represents models, calibration relations, datasets, adapters, checks, and manuscript claims as versioned objects with explicit assumptions, validity ranges, parameter sources, fit/evaluation relationships, and reproducible producers. It does not treat passing tests as a single validation score: code verification, source reproduction, same-data reconstruction, held-out evaluation, compatibility checks, and controlled independent evidence remain distinct. In the frozen development snapshot reviewed here, Puckworks registers 25 components and 104 dataset-manifest records; availability, rights, and scientific admissibility are reported separately from registration. We evaluate the framework using predefined semantic, provenance, evidence-label, and composition defects, and demonstrate it in espresso cases involving pressure-node identity, incompatible concentration and inventory definitions, a mixed-unit chemistry aggregation, null-first temporal comparison, and a coupled extraction–swelling configuration that performs worse than a simple baseline. A generated illustrative-configuration ledger shows which stages are observed, calibrated, verified, reconstructed, extrapolated, blocked, or still require measurement. Puckworks' contribution is a practical method for making literature-model integration auditable: preserve semantic meaning at interfaces, bind quantitative claims to executable provenance, prevent evidence language from outrunning the evaluation design, and treat failed or blocked compositions as informative results rather than gaps to conceal.

This version is intentionally less numeric. Detailed results belong in the results section and companion papers, while the abstract emphasizes the framework, evaluation, and limits.

---

## 10. Recommended revised structure

For a full methods/resource paper of roughly 6,000–7,500 words plus references:

1. **Introduction and statement of need**  
   Domain problem, broader relevance, explicit contributions.

2. **Related work and novelty**  
   FAIR4RS, provenance, research objects, cards, workflows, V&V, reproducible computational practice.

3. **Frozen corpus and resource boundary**  
   Curated-search method, release version, generated counts, unique source/lineage statistics, rights and availability dimensions.

4. **Architecture**  
   Components, schema v2 axes, contracts, adapters, gates, claims, producers, release graph, implemented-versus-planned table.

5. **Evaluation methods**  
   Research questions, defect corpus, mutation tests, evidence-label adjudication, clean-room reproduction.

6. **Evaluation results**  
   Detection matrix, false negatives, reproducibility, user/adjudicator findings.

7. **Selected espresso demonstrations**  
   One semantic-linting case, one evidence-qualified comparison, one failed composition. Keep scientific detail compact and point to companion papers/supplements.

8. **Illustrative configuration and experiment promotion**  
   Generated ledger, corrected infiltration status, open final measurement.

9. **Discussion**  
   What the framework prevents, what it cannot detect, component versus composition validity, transferability as a hypothesis.

10. **Limitations, ethics, rights, and availability**  
    Corpus limits, curator judgment, human-data governance if retained, frozen DOI, reproducibility package.

11. **Conclusion**

For a JOSS paper, create a separate 1,200–1,700-word manuscript with only statement of need, functionality, research use, scholarly significance, references, and availability. The current scientific demonstrations should not be compressed into that format.

---

## 11. Prioritized revision plan

## P0 — Correct before the next internal manuscript review

1. Pin the manuscript to a dedicated commit/release and update the draft date.
2. Replace 70 manifest records with a generated count; current pinned value is 104.
3. Regenerate Table 1: 12 runtime, 13 calibration; no synthesis execution role.
4. Replace the inline Appendix A with the generated catalog.
5. Rewrite §§2.1, 3.2, and 3.3 around schema v2 and deprecated `kind`.
6. Correct Table 6 infiltration from “independently gated” to same-shot compatibility.
7. Align Table 3 with the code taxonomy and remove “negative validation.”
8. Replace the weakest-link statement with non-scalar dependency evidence.
9. Completely rewrite Table 7 against the current release/development state.
10. Insert actual figures or mark the draft explicitly incomplete and do not circulate as submission-ready.
11. Distinguish stable `v0.3.0` from development `0.4.0.dev0` throughout.
12. Add an automated test that would fail on every discrepancy identified above.

## P1 — Complete before public preprint

1. Select the target publication route.
2. Add the related-work and novelty section.
3. Define and run the framework evaluation, including mutation tests.
4. Complete quantitative reporting and reconcile baseline-value discrepancies.
5. Generate all manuscript tables/figures from machine-readable records.
6. Create a frozen claim bundle with source data, hashes, environment lock/container, and reproduction command.
7. Add a reproducible curated-corpus search/construction record.
8. Add the availability/rights/release-status matrix.
9. Reduce duplication with companion papers and assign claim ownership.
10. Resolve the external-corpus ethics/governance decision: move it, remove it, or document it fully.
11. Complete authorship, CRediT, funding, conflicts, acknowledgments, and software citation.
12. Obtain one clean-room reproduction by a person/environment outside the primary development workflow.

## P2 — Complete before journal submission

1. Archive the exact software, manuscript source, figures, source data, lock/container, and checksums with a DOI.
2. Ensure the DOI/tag commit matches all result bundles and manuscript metadata.
3. Run the target journal's full checklist and word/figure limits.
4. Confirm every rights-blocked or non-redistributable source is handled correctly in the archive.
5. Publish the evidence-label decision guide and adjudication record.
6. Add external-use/adoption evidence where required by the selected software venue.
7. Perform final statistical and domain-expert review of every scientific headline.
8. Verify that public notebooks install the cited release rather than moving `main`.
9. Run accessibility checks on figures, alt text, color use, and notebook instructions.
10. Perform a final stale-claim scan from a clean checkout and reject the release if any manuscript value is not producer-bound.

---

## 12. Venue-specific observations

### JOSS

The current manuscript is not a JOSS-shaped paper. JOSS currently asks for a paper of approximately 750–1,750 words and reviews software quality, research application, significance, installation, documentation, tests, open development, and sustained project history. Its current checklist treats months of open development—often at least six months for a recent public repository—as an important signal. A JOSS submission would therefore require a separate short paper and an honest assessment of public-development history and external engagement at the submission date.

Official guidance:

- <https://joss.readthedocs.io/en/latest/paper.html>
- <https://joss.readthedocs.io/en/latest/submitting.html>
- <https://joss.readthedocs.io/en/latest/review_checklist.html>
- <https://joss.readthedocs.io/en/latest/review_criteria.html>

### Journal of Open Research Software

JORS currently advises approximately 3,000–4,000 words. The current 9,923-word manuscript would need substantial reduction even for this route.

Official guidance:

- <https://openresearchsoftware.metajnl.com/about/submissions>

### Full methods/resource venue

This route best matches the manuscript's current ambition. The paper would need the formal framework evaluation and related-work additions described above, but it would allow the evidence taxonomy, failed composition, and experiment-design contribution to be treated as scholarship rather than compressed documentation.

---

## 13. Detailed line-level and editorial comments

Line references below refer to the pinned manuscript at commit `93358f8e4d7d5c214470d82195d852f455651ff9`.

1. **Lines 3–5:** Update the draft date and complete author/corresponding-author placeholders before external circulation. Align with repository authorship metadata.
2. **Line 7:** The claim that Table 1 and Appendix A cannot silently diverge is contradicted by the current inline tables. Revise only after fixing the pipeline.
3. **Line 11:** Replace 70 with a generated count; remove weakest-link wording; qualify “general method”; distinguish registered from runnable/redistributable.
4. **Line 17:** “Espresso brewing has become a compact testbed” needs a citation or should be phrased as the authors' framing.
5. **Lines 21–23:** Add related-work citations for provenance, executable review, and coupled-model integration. The repository itself cannot be the only support for the method's novelty.
6. **Line 25:** Add formal evaluation to the paper roadmap, not only demonstrations.
7. **Lines 31–33:** Good honesty about curated scope. Add current search/construction details and correct the manifest count.
8. **Lines 33 and 542:** Do not maintain duplicate inline/generated tables.
9. **Line 47:** Correct to 12 runtime and 13 calibration.
10. **Line 49:** Delete the claim that synthesis is unresolved execution-role schema debt. The current schema maps it to runtime and represents project synthesis as provenance.
11. **Lines 91–103:** Replace `kind` with the three authoritative axes. Mention `kind` only as deprecated compatibility metadata.
12. **Lines 109–117:** Adapters and diagnostics are enum values already. Say they have zero registered instances. Separate synthesis provenance from execution role.
13. **Line 123:** Clarify that contract schema 0.6 and registry schema v2 are different versioned systems.
14. **Lines 131–139:** Add exact units and machine-readable schema links; “selected fields” alone is insufficient for a technical resource description.
15. **Line 139:** The `ShotResultState` roadmap note may now be stale; verify against the pinned code and release, then generate this table too.
16. **Line 150:** Strong example. Identify the exact open fixture record and ensure no downstream headline assumes a resolved node.
17. **Line 152:** Either resolve the bar/Pa split before submission or make it a documented migration case with tests and deprecation date.
18. **Lines 156–162:** Call the permeability assertion a coarse scale guard, not dimensional proof.
19. **Lines 166–170:** Define every saturation/fast-fraction quantity with source lineage and mathematical basis. The 5–9× result needs uncertainty and extrapolation status.
20. **Lines 184–200:** Refactor evidence taxonomy into separate axes. “Negative validation” and “proposed experiment” do not belong on the same evidence-strength dimension as code verification.
21. **Line 194:** Align “Independent external” with code's `controlled_independent` or version the terminology consistently.
22. **Lines 203–207:** Good emphasis on claim-level evidence. Add an example where a component's default evidence differs from a particular claim's evidence.
23. **Lines 219–231:** Correct the manifest count and define whether a record is a dataset, extraction, curve, table, campaign, or transformation.
24. **Lines 241–243:** Add a concrete example of a claim invalidated by upstream drift and show the CI failure output.
25. **Line 253:** Generate environment versions and include the lock/container hash. Explain why the paper workflow uses Python 3.13 while the release's primary interpreter is 3.12.
26. **Line 255:** Good separation of automated checks and human release actions. Preserve.
27. **Lines 257–267:** Move or greatly expand governance/ethics detail. “Research-use grant” is not a complete ethics statement.
28. **Line 263:** Use “pseudonymized”; describe reidentification and linkage controls.
29. **Line 267:** Contradicted in spirit by the later approximate 11,000-record statement. Freeze or remove the count.
30. **Lines 275–286:** Strong table. Add an explicit source/producer column and distinguish author-confirmed erratum evidence from registry verification.
31. **Lines 290–294:** Add sample sizes, selection rules, dependency structure, model formula, and uncertainty details.
32. **Lines 304–308:** Excellent semantic example but currently not independently reproducible. Publish a synthetic fixture and exact contract test.
33. **Lines 312–318:** Condense and refer detailed science to the companion paper. Reconcile 0.573 versus the evidence matrix's ~0.603 flat-null reference.
34. **Lines 324–332:** Strong section. Replace “negative validation” with “negative result for this composition.” State whether the metric/configuration was predeclared.
35. **Lines 340–356:** Mark which experiment recommendations are generated by code and which are expert-authored. Give required measurement resolution where possible.
36. **Lines 354–356:** Provide complete derivation and uncertainty for the permeability factor range.
37. **Line 367:** “Provides a reproducible prediction matrix” should be supported with a generated artifact and command.
38. **Lines 373–375:** Rename “named shot” until exact frozen shot lineage exists.
39. **Line 385:** Replace “independently gated” immediately.
40. **Lines 386–391:** Every value/status should be generated from the scorecard record. Define `Fo_F` and the 6.6% adapter audit.
41. **Line 392:** Preserve the open final cup. This is a strength.
42. **Lines 410–412:** Add citations to established V&V terminology and clarify how Puckworks' taxonomy maps to it.
43. **Lines 416–418:** Excellent core principle. Consider elevating it to the end of the Introduction and title/subtitle.
44. **Lines 420–432:** Temper cross-domain generalization or add one external mapping.
45. **Lines 438–442:** Add limits of curator subjectivity, same-lineage dependence, rights blocking, and residual semantic errors that types cannot catch.
46. **Lines 448–461:** Replace Table 7 entirely with a generated release/development/readiness matrix.
47. **Line 463:** Venue criteria should be cited and moved to a publication-strategy note if no target venue is chosen.
48. **Lines 467–471:** Use “illustrate” rather than implying framework validation; include evaluation results when available.
49. **Lines 475–479:** Cite a DOI before submission and provide a per-artifact redistribution/access table.
50. **Lines 481–495:** Complete all placeholders. Keep the attribution requirement only if corpus-derived material remains.
51. **Lines 497–525:** Figures must be produced; specifications are not substitutes for results.
52. **Lines 527–538:** Prioritize supplements and automate them. Ten supplements may be excessive unless generated and clearly indexed.
53. **Lines 540–570:** Remove the inline appendix and use the generated file directly.
54. **Lines 572–597:** Expand the claim schema with fit/eval datasets, independence, outcome, transformation IDs, uncertainty method, and rights status.
55. **Lines 599–613:** Add methods/software/provenance references and replace moving/in-preparation citations where they bear substantive weight.
56. **Lines 615–617:** Good recognition that moving paths must be frozen. Make this an enforced release criterion.

### Style and terminology

- Define “gate” at first use as an executable declared check; consider using “check” in lay-facing prose.
- Define “claim producer” with one concrete example before using the term repeatedly.
- Avoid using “validation” as a generic noun when the actual relation is source reproduction or same-data reconstruction.
- Reserve “independent” for a precisely defined data/parameter relationship.
- Use “model lineage” consistently and explain how derivative implementations are counted.
- Prefer “illustrative configuration” to “named shot” until exact lineage is frozen.
- Prefer “negative result” or “failed check” to “negative validation.”
- Reduce repeated formulations of “plausible number with invalid interpretation” and “component validity does not imply composition validity”; state each principle once strongly and then refer back.
- Expand acronyms at first use, including TDS, EY, RMSE, LOPO, PSD, DE1, and any Forchheimer number.
- Keep units typographically consistent and define gauge versus absolute pressure.
- Distinguish “evidence strength” from “evidence type/relationship” if the revised schema adopts multiple axes.

---

## 14. Final assessment

Paper 3 contains a publishable idea and a repository with unusually strong scientific-integrity instincts. Its central message—that model interfaces, parameter provenance, observable definitions, and validation relationships must be made executable before heterogeneous process models are compared or composed—is important well beyond espresso.

The manuscript's present weaknesses are repairable, but several are foundational rather than cosmetic. The paper must demonstrate that its own publication pipeline satisfies the controls it advocates; correct schema and evidence-language drift; stop overstating the infiltration result; distinguish registration, execution, rights, release, and scientific admissibility; position itself against existing research-software and provenance practice; and evaluate the framework with predefined defects and clean-room reproduction.

The best next draft would be **shorter but more rigorous**. It should contain fewer scientific headlines, stronger ownership of those it retains, complete generated figures, a formal framework evaluation, and one immutable release boundary. With those changes, Paper 3 could become the methodological anchor for the Puckworks program: not a claim that a unified espresso mega-model already exists, but a defensible account of the infrastructure and evidentiary discipline required before one can be assembled honestly.

---

## 15. Frozen repository sources used in this review

- Audit commit: <https://github.com/trbrewer/puckworks/commit/93358f8e4d7d5c214470d82195d852f455651ff9>
- Paper 3 manuscript: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/PAPER_3_PUCKWORKS_DRAFT.md>
- Registry schema: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/puckworks/registry.py>
- Generated registry counts: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/paper3_resource/generated/registry_counts.json>
- Generated Table 1: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/paper3_resource/generated/table1_registry_overview.md>
- Generated component catalog: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/paper3_resource/generated/appendixA_component_catalog.md>
- Paper 3 priority evidence matrix: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/paper3_resource/generated/paper3_priority_evidence_matrix.md>
- Dataset manifest: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/puckworks/data/MANIFEST.csv>
- README/release and access status: <https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/README.md>

