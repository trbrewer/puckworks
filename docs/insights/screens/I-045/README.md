# I-045 — foster2025_2 evidence-half audit

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## What was run

**Question** (generated, verbatim from the candidate):

> For the 1 datasets whose validation_strength names both independent + verification, which of
> those strengths does each consuming gate actually rely on?

Dataset: `foster2025_2/fig12_14_curves`.

## How to re-run

```
python -m puckworks.analysis.screen_i045_evidence_halves
```

Writes `result.json` and `figures/primary.png`. ~15 s.

Focused test: `pytest tests/test_screen_i045.py -v`

## Source authority

**Controlling card: `docs/cards/foster2025_2.md`.** It resolves, and it carries **no**
`TEMPLATE_DEVIATION` — the deviation the candidate card flagged as a prerequisite belongs to
`docs/cards/foster2025.md`, which is a *different* card. This screen does not use or inherit it.
Prerequisite confirmed, recorded in `result.json → source_card_note`.

MANIFEST `validation_strength`, copied byte-identical and never paraphrased:

```
independent (CT data) / verification (fitted curves)
```

MANIFEST caveat, byte-identical:

```
s_fit/H_fit = paper ODE (0.02s grid); s_data/H_data = pixel-digitized CT (5-line mean);
Fig8 -H differs from Fig14 H (do not mix)
```

## The two halves are not ranked — and they are different columns

`independent` and `verification` here are **different evidentiary functions**, not two strengths
of one kind. Nothing in this screen orders them, and *"uses both"* is a correct outcome rather
than a promotion.

| half | columns | rows | function |
|---|---|---|---|
| **verification (fitted curves)** | `s_fit_mm`, `w_fit_mm`, `H_fit_mm` | 461 | does our port reproduce the **source's own** fitted ODE output? A statement about the implementation |
| **independent (CT data)** | `s_data_mm`, `H_data_mm`, `w_data_mm` + `*_err_mm` | 8 | does the trajectory sit on the **measured** micro-CT points? A statement about a measurement |
| *(time base)* | `t_s` | 461 | shared abscissa; carries no evidentiary function |

Because the halves are **different columns of one file**, attribution can be *observed* rather
than inferred — which is what layer 2 does.

### The sense of "independent" is settled by the card, not the manifest

The manifest word is ambiguous between *independent measurement modality* and *held out from the
fit*. The controlling card settles it, verbatim:

> Note the circularity: k and φ_T are fitted to the same s/H curves being reproduced, so the
> source validates model FORM, not parameter-free prediction.

So the CT half is an independent **measurement**, and is **not** held out in the ROADMAP §0 sense.

## Method — the accepted I-040 four-layer pattern, reused without importing its outcome

1. **Static enumeration**, deliberately over-approximating: every reference to the loader, the
   dataset id, or the consuming gate across source, tests, docs and generated evidence records.
   **64 references across 19 files; 2 loader call sites.**
2. **Column-level access tracing** — the second, independent enumeration. The loader is wrapped
   so each row records which *keys* are read, and the candidate consumer is executed. Used
   solely to establish which evidence fields are read; nothing is fitted or scored.
3. **Manual reconciliation** of the union. Coverage `complete: true`.
4. **Human attribution** — 7 consumers, each with file/function, source row and columns read,
   the exact assertion, whether independence is load-bearing, whether verification reproduction
   is load-bearing, whether both are legitimately required, whether neither is, any misleading
   wording, and the classification with rationale.
5. **Adversarial text scan** for `independent` / `independently` / `verification` / `verified` /
   `validation` across every consuming surface, each hit read **in context**.

### Two scan defects found and fixed during the screen

- The manifest scan used a character window and **bled into neighbouring dataset rows**
  (`de1_fixtureA`, `mo2023`, `foster2025_2/fig15_flow_pressure`). It is now clipped to the target
  row exactly, and an `OTHER_ROW_MARKERS` backstop remains.
- Fragment matching was first-match-wins, which **mislabelled the docstring's `independent` hit**
  with the neighbouring `verifying the port`. Rules now pair a token with a fragment that must
  contain that token.

**6 hits, 0 unclassified** after the fix.

### A surface that prose cannot cover

`EVIDENCE_LINKS.json` contains **none** of the five scanned tokens — it states independence in a
machine-readable `independence` field per source role rather than in sentences. A text scan alone
would have reported a silent surface and missed the strongest statement in the audit, so
`structural_independence_fields()` reads the fields directly.

## Result — **RETIRE**

| classification | consumers |
|---|---|
| **BOTH load-bearing** (legitimately) | `gate_foster_ct_trajectory` |
| **VERIFICATION load-bearing** | `EVIDENCE_LINKS …::gate_foster_ct_trajectory`; paper3 evidence graph (generated); paper3 Fig 2 evidence vector (generated) |
| **INDEPENDENT load-bearing alone** | *none* |
| **NEITHER** | registry entry `foster2025.machine_mode`; PV-02 evidence selection (exclusion); `tests/test_data_loaders.py` loader smoke |

The gate makes **two** assertions and needs **both** halves — the legitimate case the candidate's
own alternative explanation anticipated. Traced columns confirm it: `s_fit_mm`, `H_fit_mm`, `t_s`
across all 461 rows, and `s_data_mm`, `s_data_err_mm`, `H_data_mm`, `H_data_err_mm` on the 8 CT
rows.

### One wording risk, recorded and contained

The gate docstring labels the CT arm `(independent, 'qualitative-good')` — copying the manifest
word without the card's circularity qualifier. Read in the ROADMAP §0 held-out sense it would be
wrong.

**It does not propagate.** Every downstream consumer independently refuses the strong reading:

| surface | what it records |
|---|---|
| `EVIDENCE_LINKS.json` | the same dataset **twice** — `eval`/`same_campaign` **and** `fit`/`fit_input` |
| | `relationship: same_campaign_not_held_out` · `reality_facing: false` · `support_status: context_only` |
| | `claim_not_supported`: "does not establish parameter-free or out-of-sample prediction" |
| | caveat carries the card's circularity verbatim |
| paper3 graph + Fig-2 vector | render the same adjudication; Fig-2 outcome is **`negative`** |
| registry | `source_curve_reproduction` |
| PV-02 | **excludes** the gate outright |

`structural_independence_fields.asserts_independence: false`.

## Figure

`figures/primary.png` — dataset → the two halves (drawn as **equal columns**, not a ladder) →
consumer → columns read → the function actually load-bearing, with the wording risk flagged.

Bundle-local screen evidence. **Not** registered in `puckworks/viz/registry.py` or the generated
gallery: it is evidence-lineage bookkeeping, not a mechanism render with a fidelity ceiling.

## Scope — what this screen did NOT do

- No model campaign. The one execution is the traced gate run, used solely to observe which
  columns are read.
- It did **not** change any evidence label, public badge, validation rung, model verdict or
  physical-science conclusion.
- It did **not** touch `docs/cards/foster2025.md` or the candidate-readiness lane.
- It did **not** execute any candidate other than I-045.
