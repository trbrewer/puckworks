# I-045 — Preliminary external novelty review

```
PRELIMINARY_EXTERNAL_REVIEW
NOT_A_PUBLICATION_RESULT
NOT_A_SYSTEMATIC_LITERATURE_REVIEW
```

> **Scope and standing.** Authorized because I-045 survived its cheap screen; begun only after the
> internal protocol ([`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md)) and the source-lineage
> result were frozen. **Nothing here enters `deep_result.json`** — protocol stop condition S6
> forbids fabricating external findings into deterministic output. Metadata hits are discovery
> aids, not evidence. **No manuscript drafting was performed.**

- **Search date:** 2026-08-05
- **Searcher:** automated web search (US index) run from this session
- **Reviewer note:** this is a *preliminary* scan sufficient to classify the output. It is **not**
  a systematic review: no database was searched exhaustively, no PRISMA flow was kept, and
  paywalled standards (ASME V&V 10/20) were **not** read in full text.

---

## 1. The question being searched

Not "is calibration data independent validation?" — that is settled and the answer is no. The
question is narrower:

> Is there prior work that **structurally audits, in a repository or model registry, whether an
> evidence-strength label attached to a dataset matches what the primary source actually fitted** —
> and scopes that label to the specific columns or assertions it covers?

## 2. Tools and sources searched

| tool | coverage |
|---|---|
| web search (US index) | peer-reviewed papers, preprints, standards bodies, official technical guidance, OSS project documentation |
| Unpaywall OA-location API | to obtain the primary source itself (succeeded — UL repository copy) |

Not searched: Scopus, Web of Science, ACM DL and IEEE Xplore behind paywalls; ASME V&V standards
full text.

## 3. Exact queries

```
1. "calibration data" "independent validation" circular model validation same data mechanistic model
2. evidence provenance metadata scientific software validation "data lineage" column-level assertion audit tool
3. ASME V&V 10 20 verification validation terminology "not used in calibration" independent data standard guidance
4. "data leakage" mechanistic model validation detection tool automatic audit reproducibility 2024 2025
5. "model cards" OR "datasheets for datasets" validation evidence provenance simulation model registry scientific computing metadata standard
```

## 4. Inclusion / exclusion logic

**Included** if the source (a) states or codifies the calibration-vs-validation independence
requirement, (b) describes a *method* for detecting violations, (c) describes a *system* that
attaches evidentiary or provenance metadata to data at column/assertion granularity, or (d) is an
official standard or guidance document in scope.

**Excluded**: general data-quality marketing content with no method; LLM/benchmark-contamination
work whose mechanism (memorization of test items by a pretrained model) does not transfer to
parameter fitting in a mechanistic ODE model; commercial tool listings with no published method.

---

## 5. Findings, against the protocol's required four-way separation

### 5.1 The general principle — **thoroughly established, not novel**

That parameters fitted to a dataset cannot be independently validated against that same dataset is
textbook, and it is codified in guidance documents:

- **Elmo, "The risk of confusing model calibration and model validation"** (Australian Centre for
  Geomechanics) — states the failure mode directly, including that models "cannot be assumed to be
  mechanistically correct … just because they match observed deformations," and attributes it to
  the deliberate choice not to split available information into calibration and testing data.
- **Verra VCS Module VMD0053** and **Climate Action Reserve, *Model Calibration, Validation, and
  Verification Guidance*** — both require validation data independent of calibration data, with
  Verra requiring that calibration and validation datasets "not overlap in experimental research
  locations and not be taken from the same experimental study, unless independence is demonstrated."
- **ASME V&V 10 / V&V 20** — the standards that fix *verification* vs *validation* terminology for
  computational solid mechanics and CFD. **Not read in full text** (paywalled); cited here as the
  terminological authority the repository's own §0 vocabulary parallels, not as evidence of a
  specific clause.

The puckworks §0 definition of *independent* — "data not used in fitting the thing being tested" —
is a restatement of this standard requirement. **Nothing about the principle is new.**

Note the Verra clause is *stricter* than §0: it would also disqualify a different reduction of the
same experimental campaign. Under that reading the audited cell would be wrong on two counts, not
one. This is recorded as an observation; §0 remains the repository's authority.

### 5.2 Methods for auditing the distinction — **an active field, and it does not cover this case**

Leakage auditing is a live research area, but the mechanism it addresses is different:

- **bioLeak** (R package, 2026) — leakage-aware resampling, train-fold-only preprocessing, and
  *post hoc leakage audits* of fitted models. The closest thing found to an automated audit, but it
  audits **ML resampling pipelines**, where the leak is a preprocessing or split error.
- **"A General Framework for Data-Use Auditing of ML Models"** (ACM CCS 2024) — determines whether a
  data point was used in training. Membership-inference-flavoured; assumes a trained model and a
  candidate record.
- **The data-leakage living survey** — catalogued 648 papers invalidated by leakage across ~30
  fields as of mid-2024, which establishes that the *consequence* is serious and widespread.

**None of these applies here.** In this case nothing leaked and no split was botched: the authors
fitted three parameters to their data, said so plainly, and a *downstream repository* then labelled
those same data "independent". The defect is in **evidence metadata**, not in an estimation
procedure — and no leakage tool inspects a provenance label against a paper's stated objective.

### 5.3 Systems scoping evidence labels to columns / observables / assertions — **partially covered**

- **Column-level data lineage** is mature: OpenLineage, DataHub, Apache Atlas, Marquez, and the
  commercial catalogues all track column-granular flow. But lineage answers *where a column came
  from*, not *what evidentiary strength a claim resting on it may assert*.
- **FAIR Data Pipeline** (arXiv 2110.07117) and **W3C PROV** — provenance-driven data management for
  traceable scientific workflows. Again: derivation history, not evidentiary rung.
- **Model cards / datasheets for datasets**, and the move from free-text to JSON/YAML/RDF for
  "automated auditing … especially for large registries" — the nearest conceptual relative. Model
  cards *do* carry evaluation-data sections and increasingly machine-checkable provenance fields.

**What was not found:** any system that (i) attaches a validation-strength *rung* to an evidence
unit, (ii) scopes that rung to particular columns or assertions, and (iii) checks the rung against
what the *primary source* reports having fitted. Model cards record what the card author asserts;
they do not adjudicate it against the source.

### 5.4 The puckworks-specific application

The combination — a manifest binding an evidence rung to a dataset, gates that consume it and make
claims, and an audit that reconciles the rung against the source's stated objective — was **not
found in the literature searched**. Whether that is genuine novelty or an artefact of a preliminary
search cannot be settled here, and **it does not matter for this deep screen's classification**:
the internal audit found the defect isolated and contained, so no publication output is earned
regardless of how novel the framing is.

---

## 6. Result

**`INCREMENTAL`.**

- The **principle** is established and codified (§5.1) — nothing to claim.
- The **auditing methods** that exist target a different failure mechanism (§5.2), so this is not a
  gap that has been filled; but neither is filling it demonstrated to be valuable here, because the
  audit that found this defect was a hand-read of one paper plus a grep, not a reusable instrument.
- The **scoped-evidence-label idea** is adjacent to model cards and column-level lineage (§5.3) and
  would need a genuine generality result to be worth proposing. **The bounded corpus check found
  none**: scope is already stated correctly in every mixed-strength cell in the manifest.

**This is a documentation correction with a good provenance story, not a contribution.** The
classification `CORRECTION_ONLY` rests on the *internal* evidence — the confirmed lineage, the
measured containment, and the negative generality result — and this review is consistent with it
rather than load-bearing for it.

## 7. What would change this result

1. **A second, independent instance** of a rung contradicting a source's stated fit lineage, found
   in a corpus that is not puckworks. One instance is a typo; a pattern across repositories is a
   finding.
2. **A demonstration that the check can be automated** — e.g. reconciling a manifest rung against a
   structured statement of what a paper fitted. That is a real research question and is *not*
   answered by the hand audit performed here.
3. **Full-text reading of ASME V&V 10/20** and equivalent domain standards, to establish whether any
   already prescribes evidence-scope metadata at this granularity.

None of these is authorized now, and none is recommended: item 1 is the cheap one, and it should
arrive on its own from ordinary work rather than be gone looking for.

## 8. Sources

- [The risk of confusing model calibration and model validation (Elmo, ACG)](https://papers.acg.uwa.edu.au/d/2335_19_Elmo/19_Elmo.pdf)
- [Verra VCS Module VMD0053 — Model Calibration, Validation and Uncertainty Guidance](https://verra.org/wp-content/uploads/2023/05/VMD0053-ALM-Model-Guidance-v2.0.pdf)
- [Climate Action Reserve — Model Calibration, Validation, and Verification Guidance](https://climateactionreserve.org/wp-content/uploads/2020/08/SEP-Model-Cal_Val_Ver-Guidance-for-Public-Comment-August.pdf)
- [ASME — Verification, Validation and Uncertainty Quantification (V&V 10 / V&V 20)](https://www.asme.org/codes-standards/publications-information/verification-validation-uncertainty)
- [bioLeak: Leakage-Aware Modeling and Diagnostics for Machine Learning in R](https://arxiv.org/html/2604.10965v1)
- [A General Framework for Data-Use Auditing of ML Models (ACM CCS 2024)](https://dl.acm.org/doi/10.1145/3658644.3690226)
- [FAIR Data Pipeline: provenance-driven data management for traceable scientific workflows](https://arxiv.org/pdf/2110.07117)
- [Data Lineage: What It Is and Why It Matters (DataHub)](https://datahub.com/blog/data-lineage-what-it-is-and-why-it-matters/)
- [Model Cards for Reporting AI Models](https://www.emergentmind.com/topics/model-cards-for-model-reporting)
- [Datasheets for Datasets](https://www.emergentmind.com/topics/datasheets-for-datasets)
- [Verification and Validation for Trustworthy Scientific Machine Learning](https://arxiv.org/pdf/2502.15496)
- Primary source obtained for §4 of the deep screen: [Foster et al., *Phys. Fluids* **37**, 013383 (2025)](https://doi.org/10.1063/5.0245167) — open-access copy via the [University of Limerick research repository](https://researchrepository.ul.ie/)
