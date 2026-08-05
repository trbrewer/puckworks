# I-045 Deep Screen — Protocol

```
FROZEN BEFORE ANALYSIS
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **This document is committed alone, before any deep-result-producing commit.** It fixes the
> question, the authorities, the selection rules, the alternatives to be tested and the decision
> rule, so that none of them can be chosen after seeing the answer. A history-order test asserts
> the ordering.
>
> Base: `7d8114931c5bafbf3915d9f70b7c4621f8261a22` (main, IF-6b merge).
> Branch: `insights/if7-i045-deep-screen`.

---

## 0. What is already frozen and is NOT reopened here

I-045's **cheap-screen disposition is SURVIVE** and stays in the record as such
([`decision.md`](decision.md), [`result.json`](result.json), ROADMAP §7.1 2026-08-05). This deep
screen may reach any classification in §8 below — **including one that invalidates the cheap-screen
interpretation** — but it may not rewrite or obscure that history. The standing record must show
both rungs:

```
cheap screen : SURVIVE
deep screen  : <classification from §8>
```

The cheap screen's own artifacts (`result.json`, `figures/primary.png`) are byte-frozen.

---

## 1. The exact deep-screen question

> For the dataset `foster2025_2/fig12_14_curves`, do the **primary source's own calibration and
> evaluation lineage** and the repository's **governing evidentiary vocabulary** together establish
> that the manifest cell `independent (CT data) / verification (fitted curves)` and the gate
> docstring's `(independent, 'qualitative-good')` attach an **incorrect evidence type** to the CT
> arm — and if so, what class of output does that finding earn?

Two sub-questions the cheap screen deliberately did not answer:

- **(Q1) Lineage.** The cheap screen took the *controlling card's* circularity note as its warrant.
  This screen must go to the **paper** and establish which observations actually entered the
  objective that produced `k`, `φ_T` and `t_shift`.
- **(Q2) Consequence.** Is the defect isolated bookkeeping, or does it recur across the corpus's
  mixed-strength cells in a way that earns a reusable method?

**Falsification is explicitly in scope.** If the paper shows the CT observations in Figs 12–14 were
excluded from the fit, the cheap-screen finding is wrong and §8 `RETIRE_AFTER_DEEP_SCREEN` applies.

---

## 2. Governing definitions — ROADMAP §0, verbatim

The screen verifies these against `docs/ROADMAP.md` at run time (reusing the cheap screen's
`verify_glossary` contract) and fails on drift.

| term | definition (verbatim) |
|---|---|
| **independent** | data not used in fitting the thing being tested |
| **post-fit reconstruction** | model reproduces the dataset its parameters were fitted to — a consistency check, not validation |
| **verification** | model-vs-model / asymptotic / budget |
| **qualitative** | shape/mechanism only, no error metrics |

House rule **[RS]**: never promote a lower rung to a higher one when quoting a card.

**`independent` is a statement about the FIT, not about the measurement modality.** A measured CT
observation used in the objective is *not* independent. A measurement-modality reading was tried and
rejected in the cheap screen (`result.json → rejected_reinterpretation`); it is re-tested here as
alternative explanation **A5** and may not be readmitted silently.

---

## 3. Authorities

### 3.1 Primary source (controlling for §4)

> J. Foster, W. Lee, K. Moroney, D. Prjamkov, M. Salamon, A. Smith, J. Petrassem-de-Sousa,
> M. Vynnycky, "Dynamics of liquid infiltration into an espresso bed using time-resolved
> micro-computed tomography: Insights from experiment and modeling," *Physics of Fluids* **37**,
> 013383 (2025). DOI `10.1063/5.0245167`.

Plus any supplementary material. The card records **no code or data repository published**; raw CT
data is "available from the corresponding author on reasonable request".

### 3.2 Repository authorities

| authority | role |
|---|---|
| `docs/cards/foster2025_2.md` | controlling card; carries the circularity note |
| `puckworks/data/MANIFEST.csv` | the cell under audit (row `foster2025_2/fig12_14_curves`) |
| `puckworks/data/foster2025_2/*` | the digitized artifact + `PROVENANCE.md`, `README_digitization.md` |
| `puckworks/validation/gates.py` | `gate_foster_ct_trajectory` |
| `puckworks/paper3/EVIDENCE_LINKS.json` | the downstream adjudication |
| `docs/ROADMAP.md` §0 | the evidentiary vocabulary |

### 3.3 Precedence rule, fixed now

1. For **what was fitted**, the **paper** governs. The card is a repository transcription and may
   itself be wrong; it may not be elevated into primary-source confirmation.
2. For **what an evidence label means**, **ROADMAP §0** governs. The paper's own wording is recorded
   as evidence about author intent, never as a competing definition.
3. Where the paper is inaccessible or silent, that is recorded as such and routes to §8
   `NEEDS_PRIMARY_SOURCE` for the affected sub-question — not filled in from the card.

---

## 4. Source-lineage questions

To be answered **from the paper** (page / section / equation / figure / table cited), with direct
quotation within copyright limits:

- **L1** Which observations entered the objective used to fit `K` (i.e. `k`), `φ_T`, `t_shift`?
- **L2** Were `s(t)` and `H(t)` fitted **simultaneously** (one objective) or separately?
- **L3** Did **all eight** plotted CT observation times enter the fit?
- **L4** Was any observation, time point, trajectory, radial shell or derived quantity **excluded
  from fitting and retained as genuinely held-out evidence**?
- **L5** Did the error bars enter fitting, enter weighting, or serve only visualization?
- **L6** For each figure/column: fit input · fitted-model output · derived quantity · plausibility
  check · independent/held-out evidence (if any).
- **L7** The authors' **own terms** for calibration, fitting, validation, agreement and sensitivity.

**Standing caution.** A datum is not held out merely because it is a measured CT observation
(that is the rejected modality reading). Nor is it fitted merely because it appears in a figure
beside a fitted curve. The determination must rest on the stated objective.

**Candidate held-out material to check explicitly** (named now so a null result is meaningful):
the radial-shell analysis (Figs 7–9), the whole-bed-fit series behind Figs 6/8, the flow-rate
minimum (Fig 15), the sensitivity study (Appendix B), and `t_p` / `t_s`.

---

## 5. Blast-radius surfaces to inspect

Trace `independent (CT data)` — and structural inheritance of the independent-evidence reading —
across, at minimum:

1. current `main` source and documentation;
2. registry entries and model cards;
3. validation reports and gate output;
4. `EVIDENCE_LINKS.json` and generated Paper 3 evidence;
5. `puckworks/public/` claims and generated public artifacts;
6. notebooks and notebook-rendered prose;
7. repository `README` and `docs/`;
8. the latest public release/tag content;
9. GitHub Pages source artifacts tracked in the repository;
10. tests and fixtures;
11. screen bundles and standing documents.

Every occurrence or structural inheritance records: surface · path · direct quotation or structured
value · kind · reader availability · downstream containment · required future correction.

**Exposure classification, fixed now:**

| class | meaning |
|---|---|
| `PRESENT_BUT_EXPLICITLY_REJECTED` | the surface names the reading and refuses it |
| `CURRENT_INTERNAL_MISWORDING` | wrong, but not on a reader-facing surface |
| `CURRENT_READER_FACING_OVERCLAIM` | a reader can take the independent-evidence reading |
| `GENERATED_BUT_CORRECTLY_BOUNDED` | derivative that carries the correct adjudication |
| `HISTORICAL_SUPERSEDED` | superseded text retained for provenance |
| `NO_EXPOSURE` | the surface does not carry the attribution |

**No audited surface is edited.**

---

## 6. Mixed-strength generality-selection rule — deterministic, frozen now

Applied to **all rows of `puckworks/data/MANIFEST.csv` at the branch base**, on the
`validation_strength` cell:

1. Split the cell into segments on the top-level separators `/`, `+`, `;` — **parenthesis-aware**,
   so separators inside `(...)` do not split. This is what prevents prose inside a caveat from being
   read as a second label.
2. A segment's **head label** is the first ROADMAP §0 token it begins with, matched
   case-insensitively on word boundaries, from the frozen set:
   `independent` · `post-fit` (covering *post-fit* and *post-fit reconstruction*) · `verification` ·
   `qualitative`.
3. **PRIMARY SET** — rows with **≥ 2 distinct §0 head labels**. These are the mixed-strength cells.
4. **SECONDARY SET** — rows with ≥ 2 segments where at least one head is a §0 token and at least one
   other segment head is a **non-§0** label (e.g. `reference`, `kernel check`). Recorded and counted,
   **not** adjudicated in depth: they are mixed in form but not in §0 vocabulary.

Rows are reported by `dataset_id` in manifest order. Selection is by rule, never by inspection.

For each PRIMARY-SET row, determine **only**:

- **G1** do multiple labels apply to the **same** evidence unit?
- **G2** do they apply to distinct columns / rows / observables / parameter sets / assertions?
- **G3** does the current wording **identify that scope**?
- **G4** could a consumer reasonably attach the **stronger** label to the wrong assertion?
- **G5** do downstream records contain or propagate that ambiguity?

This is a **generality test of I-045's method**, not execution of another candidate. No other
candidate's disposition is adjudicated; no label, card, retirement record or portfolio entry is
touched. I-040 and I-045 are used as known comparison cases and neither cheap-screen result changes.

---

## 7. Alternative formulations and alternative explanations

### 7.1 Correction formulations — assessed, NOT implemented

| # | formulation |
|---|---|
| **F1** | wording-only in the existing row: `post-fit reconstruction (CT data) / verification (fitted curves)` |
| **F2** | more explicit same-campaign wording: `post-fit, same-campaign CT observations / verification of fitted trajectories` |
| **F3** | split the evidence unit into separately scoped manifest records or views for fitted trajectories · CT observations · shared time base |
| **F4** | retain one row, add an explicit column-to-evidence mapping |

Each assessed on: scientific accuracy · glossary compatibility · fidelity to source wording ·
consumability by current gates and evidence tools · migration cost · risk of implying held-out
validation · generalization to other mixed-strength cells.

**No schema is added, the manifest is not changed, and no split is implemented.**

### 7.2 Alternative explanations — the finding survives only if all fail

| # | challenge |
|---|---|
| **A1** | *Primary-source:* the CT observations were not actually used to fit the tested object. |
| **A2** | *Partial-holdout:* only some trajectories or time points were fitted, leaving a defensible held-out subset. |
| **A3** | *File-level union:* the manifest label describes everything in the artifact, not the evidentiary status of each gate assertion. |
| **A4** | *Harmless wording:* because `EVIDENCE_LINKS` is correctly bounded, the manifest and gate wording are inconsequential. |
| **A5** | *Modality:* `independent` means a distinct measurement modality rather than data not used in fitting. |

ROADMAP §0 is the repository authority for A5, but the screen must report whether any **source
language** genuinely supports any of these — an author's usage is evidence about intent even when it
does not change the repository's definition.

**The finding survives only if the exact fit lineage AND the governing definition continue to
establish a materially incorrect attribution.**

---

## 8. Decision and output-class rules — fixed before the answer

Exactly one classification:

| class | condition |
|---|---|
| `RETIRE_AFTER_DEEP_SCREEN` | primary-source evidence establishes the relevant CT observations were genuinely excluded from fitting or otherwise independent of the fitted object, invalidating the cheap-screen interpretation |
| `NEEDS_PRIMARY_SOURCE` | available source material cannot establish whether the relevant data were fitted or held out |
| `CORRECTION_ONLY` | misattribution confirmed, contained, isolated or nearly isolated, and external review shows the underlying method is routine — a bounded repository correction is warranted, no standalone publication output is earned |
| `TECHNICAL_NOTE_CANDIDATE` | misattribution confirmed **and** the audit reveals a reusable, practically valuable lineage method or a recurring scoped-evidence problem across multiple repository evidence units |
| `METHODS_PAPER_CANDIDATE` | **all** of: systematic not isolated · generalizes beyond puckworks · alternatives and robustness checks succeed · novelty review finds no direct prior answer · a reusable implementation and systematic comparison are justified |
| `PUBLIC_STORY_CANDIDATE` | a defensible practical consequence exists beyond internal repository hygiene; a generic "validation is not validation" message is **insufficient** |

Every classification must state: strongest supported claim · strongest claim **not** supported ·
exact future correction targets · whether a separate correction PR is recommended · whether further
literature review, manuscript work or experimental work is justified.

**The current SURVIVE is not protected from falsification.**

---

## 9. External novelty-search terms

Begun **only after** §2–§4 are frozen in the deep result. Terms fixed now:

```
validation data provenance
circular model validation
calibration and validation on the same data
post-fit reconstruction presented as independent validation
verification versus validation in scientific software
data leakage in mechanistic model validation
column-level evidence provenance
evidence lineage manifests
scientific-software validation metadata
```

Primary papers, standards and official technical guidance preferred. `NOVELTY_REVIEW.md` records
search date · databases/tools · exact queries · inclusion/exclusion logic · directly relevant
sources · adjacent non-answering sources · result (`likely novel` / `incremental` /
`already established` / `unresolved`).

The review must separate:

1. the well-known **general principle** that calibration data are not independent validation;
2. prior **methods** for automatically or structurally auditing that distinction;
3. prior **systems** scoping evidence labels to columns, observables or assertions;
4. the possibly new **puckworks-specific application**.

Metadata hits are discovery aids, not evidence. **No manuscript drafting.**

---

## 10. Stop conditions

Stop and report without completing, rather than proceeding on an assumption, if:

- **S1** the paper and its supplement cannot be obtained → record exactly what was unavailable;
  do not substitute the card. Route the lineage sub-question to `NEEDS_PRIMARY_SOURCE`.
- **S2** the paper contradicts the card on what was fitted → stop and surface it; the card becomes
  a second, separate finding rather than a silently corrected input.
- **S3** any protected surface would have to change to complete a step → stop; the step is out of
  scope by construction (§J of the authorization).
- **S4** the generality check would require executing another candidate, adjudicating its
  disposition, or building a lens/generator → stop; the check is bounded to G1–G5.
- **S5** the deterministic script would need to run a scientific model → stop. No refit or model
  execution is authorized unless a bounded source-lineage reproduction is explicitly justified
  here, and **none is**: the lineage question is answered from text, not from re-running anything.
- **S6** the classification would rest on novelty findings rather than repository evidence → stop;
  external findings live in `NOVELTY_REVIEW.md` and are never fabricated into deterministic output.

## 11. Scope — what this deep screen will NOT do

- Not correct the manifest, gate, `EVIDENCE_LINKS`, generated Paper 3 evidence, registry entries,
  model cards, public claims or released artifacts. It determines what a **later human-owned
  correction** should say.
- Not execute or repair another candidate; not begin IF-6c; not run I-072, I-077, I-079, I-090;
  not alter I-076.
- Not add a Foundry lens, generator, schema, scoring or portfolio machinery, and not implement a
  generalized evidence-provenance framework.
- Not register the figure in `puckworks/viz/` or the generated gallery — it stays bundle-local.
- Not draft a manuscript or build publication-assurance machinery.
- Not merge the IF-7 PR.

---

## 12. Outputs

```
docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md   this document, committed first and alone
docs/insights/screens/I-045/deep_result.json          deterministic, repository-bound
docs/insights/screens/I-045/deep_decision.md          classification and claim ceiling
docs/insights/screens/I-045/NOVELTY_REVIEW.md         external review, kept out of the JSON
docs/insights/screens/I-045/figures/deep_primary.png  bundle-local
puckworks/analysis/deep_screen_i045_lineage.py        the deterministic producer
tests/test_deep_screen_i045.py                        including the history-order test
```

The figure shows: **source fit lineage → manifest evidence wording → gate assertion →
downstream/public surfaces**, plus the bounded generality result — not a full corpus atlas.
