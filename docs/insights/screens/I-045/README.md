# I-045 — foster2025_2 evidence-half audit

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-05 after exact-head review — RETIRE → SURVIVE.** The first version read
> the manifest's "independent (CT data)" as an independent *measurement modality*. That is not
> the repository's definition: **ROADMAP §0** defines *independent* as **data not used in fitting
> the thing being tested**, and the controlling card records `k` and `φ_T` as fitted to the very
> s/H curves the CT columns hold. The enumeration, tracing, consumer union and scan are unchanged
> — only the evidence semantics and the verdict.

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

## The controlling vocabulary — ROADMAP §0, verified at run time

| term | definition (verbatim) |
|---|---|
| **independent** | data **not used in fitting** the thing being tested |
| **post-fit reconstruction** | model reproduces the dataset its parameters were fitted to |
| **verification** | model-vs-model / asymptotic / budget |

The screen **reads the authoritative §0 block at run time and verifies verbatim** that the definitions it applies still appear there — it does not parse them out of the document, and it does not restate them from memory. If the authority is reworded, the screen **fails** rather than silently applying a stale definition
(`glossary_binding.method = VERBATIM_RUNTIME_VERIFICATION`).

## The two arms are different columns — and neither is independent

| arm | columns | rows | evidence type under §0 | manifest wording correct? |
|---|---|---|---|---|
| fitted curves | `s_fit_mm`, `w_fit_mm`, `H_fit_mm` | 461 | **verification** | ✔ |
| CT observations | `s_data_mm`, `H_data_mm`, `w_data_mm` + `*_err_mm` | 8 | **post-fit reconstruction (same campaign, not held out)** | ✘ — the cell says "independent" |
| *(time base)* | `t_s` | 461 | none | ✔ |

Because the arms are **different columns of one file**, attribution can be *observed* rather than
inferred — which is what layer 2 does.

### Why the CT arm is post-fit, not independent

`docs/cards/foster2025_2.md`, verbatim:

> Note the circularity: k and φ_T are fitted to the same s/H curves being reproduced, so the
> source validates model FORM, not parameter-free prediction.

The parameters under test were fitted to these curves. Under §0 the arm is post-fit.

**The rejected reinterpretation.** An earlier version read "independent" as an independent
*measurement modality* — a real CT observation as opposed to model output. That is not the
repository's definition, and under it almost any measurement would qualify, emptying the rung of
content. It is recorded in `result.json → rejected_reinterpretation` so it cannot quietly return.

## Method — the accepted I-040 four-layer pattern, reused without importing its outcome

1. **Static enumeration**, deliberately over-approximating: every reference to the loader, the
   dataset id, or the consuming gate across source, tests, docs and generated evidence records.
   The exact raw-reference counts are recorded in `result.json`. The decision-bearing
   reconciliation is **4 statically recoverable loader call sites, 7 attributed consumers,
   and complete coverage**.
2. **Column-level access tracing** — the second, independent enumeration. The loader is wrapped
   so each row records which *keys* are read, and the candidate consumer is executed. Used
   solely to establish which evidence fields are read; nothing is fitted or scored.
3. **Manual reconciliation** of the union. Coverage `complete: true`.
4. **Human attribution** — 7 consumers, each with file/function, source row and columns read,
   the exact assertion, whether the verification arm is load-bearing, whether the post-fit
   same-campaign arm is, whether both are required, whether neither is, **whether the consumer
   claims its evidence is independent**, any misleading wording, and the classification with
   rationale.
5. **Adversarial text scan** for `independent` / `independently` / `verification` / `verified` /
   `validation` across every consuming surface, each hit read **in context**.

### Three defects in the scan instrument, found and fixed before it concluded

- The manifest scan used a character window and **bled into neighbouring dataset rows**
  (`de1_fixtureA`, `mo2023`, `foster2025_2/fig15_flow_pressure`). It is now clipped to the target
  row exactly, and an `OTHER_ROW_MARKERS` backstop remains.
- Fragment matching was first-match-wins, which **classified the docstring's `independent` hit
  using the neighbouring `verifying the port`** — i.e. it reported the one real misattribution as
  correct usage. Rules now pair a token with a fragment that must contain that token.
- The prose scan structurally cannot see `EVIDENCE_LINKS.json` (see below).
- The gate hit was classified `AMBIGUOUS_MEASUREMENT_SENSE`, noted as "true in the
  measurement-modality sense". **That reading is rejected, not a second valid sense**, so the
  classification is now `INCORRECT_INDEPENDENT_ATTRIBUTION`.

**6 hits, 0 unclassified** after the fixes, classified under the §0 meaning **exclusively**:

| hit | classification |
|---|---|
| gate docstring `(independent, 'qualitative-good')` | **`INCORRECT_INDEPENDENT_ATTRIBUTION`** — the finding |
| MANIFEST `independent (CT data)` | **`TARGET_CELL_WITH_INCORRECT_INDEPENDENT_LABEL`** — `POST_FIT_SAME_CAMPAIGN` / `NOT_HELD_OUT` / `NOT_INDEPENDENT` |
| MANIFEST `verification (fitted curves)` | `TARGET_CELL_CORRECT_VERIFICATION_HALF` |
| card `## Calibration and validation offered by the source` | `SOURCE_CARD_SECTION_HEADING` |
| card `the key validation series` | `OTHER_DATASET` |
| MANIFEST `gate_use` `… trajectory validation` | `GATE_USE_FIELD_NOT_AN_EVIDENCE_CLAIM` |

No live rule or generated record carries `AMBIGUOUS_MEASUREMENT_SENSE`, and no live surface calls
the modality reading true — it survives only in `result.json → rejected_reinterpretation`.

### A surface that prose cannot cover

`EVIDENCE_LINKS.json` contains **none** of the five scanned tokens — it states independence in a
machine-readable `independence` field per source role rather than in sentences. A text scan alone
would have reported a silent surface and missed the strongest statement in the audit, so
`structural_independence_fields()` reads the fields directly.

## Result — **SURVIVE**

| classification | consumers |
|---|---|
| **VERIFICATION_AND_POST_FIT_SAME_CAMPAIGN** | `gate_foster_ct_trajectory` |
| **VERIFICATION** | `EVIDENCE_LINKS …::gate_foster_ct_trajectory`; paper3 evidence graph; paper3 Fig-2 evidence vector |
| **POST_FIT alone** | *none* |
| **INDEPENDENT alone** | *none — nothing in this dataset is independent evidence* |
| **NEITHER** | registry entry; PV-02 exclusion; loader smoke test |

The gate makes **two** assertions and needs **both** arms — but the two arms are *verification*
and *post-fit*, not *independent* and *verification*. Traced columns confirm the read-set:
`s_fit_mm`, `H_fit_mm`, `t_s` across all 461 rows, and `s_data_mm`, `s_data_err_mm`, `H_data_mm`,
`H_data_err_mm` on the 8 CT rows.

### The finding

`gate_foster_ct_trajectory` describes the CT arm as `(independent, 'qualitative-good')`. Under
ROADMAP §0 that arm is post-fit, same campaign, not held out. **That is a materially incorrect
evidence-type attribution**, and it is what the candidate's SURVIVE arm asks about.

**It concerns the evidence label, not the numbers.** The gate's RMSE (0.002 mm, 0.053 mm against
a 0.2 mm threshold) and its CT bracketing (4/8, 5/8) are unaffected.

**It does not propagate.** Every downstream consumer refuses the strong reading:

| surface | what it records |
|---|---|
| `EVIDENCE_LINKS.json` | the same dataset **twice** — `eval`/`same_campaign` **and** `fit`/`fit_input` |
| | `relationship: same_campaign_not_held_out` · `reality_facing: false` · `support_status: context_only` |
| paper3 graph + Fig-2 vector | render the same adjudication; Fig-2 outcome is **`negative`** |
| registry | `source_curve_reproduction` |
| PV-02 | **excludes** the gate outright |

Containment bounds the blast radius; it does not make the attribution correct.

## Affected surfaces — named, NOT corrected here

1. `puckworks/data/MANIFEST.csv` — the `validation_strength` cell for this dataset;
2. `puckworks/validation/gates.py` — the `gate_foster_ct_trajectory` docstring;
3. any reader-facing description inheriting the independent-evidence label (none found at this
   head).

`puckworks/paper3/EVIDENCE_LINKS.json` is **already correct** and is explicitly not a target. A
test asserts all four surfaces are byte-unchanged in this PR.

## Figure

`figures/primary.png` — dataset → the two arms with their evidence type under ROADMAP §0 →
consumer → columns read → the arms load-bearing for it, with the misattribution flagged.

Bundle-local screen evidence. **Not** registered in `puckworks/viz/registry.py` or the generated
gallery: it is evidence-lineage bookkeeping, not a mechanism render with a fidelity ceiling.

## Scope — what this screen did NOT do

- No model campaign. The one execution is the traced gate run, used solely to observe which
  columns are read.
- It did **not** change any evidence label, public badge, validation rung, model verdict or
  physical-science conclusion. The three correction targets are **named, not edited**.
- It did **not** touch `docs/cards/foster2025.md` or the candidate-readiness lane.
- It did **not** execute any candidate other than I-045.
