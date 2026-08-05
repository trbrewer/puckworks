# I-045 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

For every consumer of `foster2025_2/fig12_14_curves`, does the consumer's actual assertion depend
on independent evidence, verification evidence, both, or neither?

**`independent` and `verification` are not ordinal here.** They are different evidentiary
functions — a provenance statement and an implementation statement — and a consumer may
legitimately rely on both. Nothing below ranks them.

## Evidence unit

The repository's own source: MANIFEST row 29, `docs/cards/foster2025_2.md` (the **controlling**
card — `docs/cards/foster2025.md` is a different card and its `TEMPLATE_DEVIATION` is neither
used nor inherited), `puckworks/data/__init__.py`, `puckworks/validation/gates.py`,
`puckworks/models/__init__.py`, `puckworks/public/claims.py`,
`puckworks/paper3/EVIDENCE_LINKS.json`, the paper3 generated evidence graph and Fig-2 vector, and
`tests/test_data_loaders.py`. No experimental datum is scored.

MANIFEST `validation_strength`, verbatim:

```
independent (CT data) / verification (fitted curves)
```

## Method

Four layers — over-approximating static enumeration, column-level access tracing, manual
reconciliation, hand-read attribution — plus an adversarial text scan and a structural-field
read. Full method in [`README.md`](README.md).

## Result

**7 consumers attributed. Coverage complete. 0 arm-(a) findings. The wording risk does not
propagate.**

### The halves are different columns, so attribution is observed

| half | columns | rows |
|---|---|---|
| verification (fitted curves) | `s_fit_mm`, `w_fit_mm`, `H_fit_mm` | 461 |
| independent (CT data) | `s_data_mm`, `H_data_mm`, `w_data_mm` + `*_err_mm` | 8 |
| time base | `t_s` | 461 |

Traced columns for `gate_foster_ct_trajectory`: `t_s`, `s_fit_mm`, `H_fit_mm`, `s_data_mm`,
`s_data_err_mm`, `H_data_mm`, `H_data_err_mm` — **both halves, as attributed.**

### Attribution table

| consumer | location | assertion | indep? | verif? | class |
|---|---|---|---|---|---|
| `gate_foster_ct_trajectory` | `gates.py:1125` | (a) port matches the source's fitted ODE to <0.2 mm RMSE; (b) port brackets ≥4 of 8 CT points within max(err, 0.5 mm) | ✔ | ✔ | **BOTH** |
| `EVIDENCE_LINKS …::gate_foster_ct_trajectory` | `paper3/EVIDENCE_LINKS.json` | records the claim and adjudicates it `source_curve_reproduction` / `same_campaign_not_held_out` / `reality_facing: false` / `context_only` | ✘ | ✔ | VERIFICATION |
| paper3 evidence graph (generated) | `docs/paper3_resource/generated/` | renders the same adjudication | ✘ | ✔ | VERIFICATION |
| paper3 Fig-2 evidence vector (generated) | `docs/figures/paper3/source_data/` | relation `source_curve_reproduction`, outcome **`negative`** | ✘ | ✔ | VERIFICATION |
| registry `foster2025.machine_mode` | `models/__init__.py:328` | registers the gate; component strength `source_curve_reproduction` | ✘ | ✘ | NEITHER |
| PV-02 evidence selection | `public/claims.py:208` | **excludes** the gate "on its own merits" | ✘ | ✘ | NEITHER |
| loader smoke test | `tests/test_data_loaders.py:131` | a non-empty `s_data_mm` exists — a parse check | ✘ | ✘ | NEITHER |

**No consumer relies on the independent half alone.**

## Primary figure

[`figures/primary.png`](figures/primary.png) — the two halves drawn as equal columns, then each
consumer with the columns it reads and the function actually load-bearing.

## Adversarial check

The scan covered `independent`, `independently`, `verification`, `verified`, `validation` across
five consuming surfaces. **6 hits, 0 unclassified**, each read in context:

| # | token | surface | classification |
|---|---|---|---|
| 1 | independent | gate docstring | **AMBIGUOUS_MEASUREMENT_SENSE** |
| 2 | validation | controlling card | SOURCE_CARD_SECTION_HEADING |
| 3 | validation | controlling card | OTHER_DATASET (describes Figs 6/8 — separate manifest rows) |
| 4 | independent | MANIFEST row | THE_TARGET_CELL |
| 5 | verification | MANIFEST row | THE_TARGET_CELL |
| 6 | validation | MANIFEST row | GATE_USE_FIELD_NOT_AN_EVIDENCE_CLAIM |

**Two defects in the scan itself were found and fixed before it was allowed to conclude** — and
both would have produced a confident, wrong reading:

1. The manifest scan used a character window that **bled into adjacent dataset rows**, attributing
   `independent (parameter-free triangle)` (de1_fixtureA), `independent (SPH-derived…)`
   (mo2023) and `verification (model curve)` (fig15_flow_pressure) to this audit. Now clipped to
   the target row.
2. Fragment matching was first-match-wins and **mislabelled the docstring's `independent` hit**
   with the adjacent `verifying the port`, i.e. it reported the one real wording risk as correct
   usage. Rules now require the fragment to contain the token.

**A third gap the token scan structurally could not see.** `EVIDENCE_LINKS.json` contains **none**
of the five tokens: it expresses independence in a machine-readable `independence` field, not in
prose. A prose scan alone would have reported a silent surface and missed the single strongest
statement in the audit. `structural_independence_fields()` reads those fields directly and finds
`same_campaign`, `fit_input`, `same_campaign_not_held_out`, `reality_facing: false`,
`support_status: context_only` — `asserts_independence: false`.

## Strongest alternative explanation

*"The cell is mixed only in wording; both halves support the same assertion equally."*

**Refuted in the useful direction, and it strengthens the retirement.** The halves do *not*
support the same assertion — they support two different ones, and the gate needs both. The RMSE
arm is carried only by `s_fit_mm`/`H_fit_mm`; the bracketing arm only by the CT columns. Neither
substitutes for the other, which is precisely why "uses both" is the correct classification and
not a promotion.

## Decision

**RETIRE.**

The candidate's rule applied without revision: *"RETIRE if every real consumer uses the correct
evidentiary half, legitimately uses both, or does not make an evidentiary-strength claim."*
All seven do. `SURVIVE` requires a consumer presenting or relying on the independent half for an
assertion carried only by verification, or otherwise making a materially incorrect evidence-type
attribution; neither arm fires. `NEEDS_NEW_DATA` would require insufficient source metadata; the
metadata is unusually good — the halves are separate columns and the card states the circularity
explicitly.

## Why

1. **The split is structural, not editorial.** Two different columns, two different row counts,
   two different assertions. There is no way for a consumer to accidentally substitute one for
   the other, and none does.
2. **The evidence layer refuses the strong reading in machine-readable form.** It records the
   same dataset twice — once as `eval`/`same_campaign` and once as `fit`/`fit_input` — which is
   the card's circularity made executable, and it sets `reality_facing: false` and
   `support_status: context_only`.
3. **The only public claim nearby excludes the gate entirely**, with an observable-scope reason.

### One observation recorded, not a finding

The gate docstring's `(independent, 'qualitative-good')` copies the manifest word without the
card's circularity qualifier. In the ROADMAP §0 held-out sense it would be wrong; in the
measurement-modality sense the manifest intends, it is right. It is contained at that docstring
and every downstream consumer refuses the strong reading, so it changes no attribution. Recording
it here is the whole of the action it warrants — and note the direction of travel is favourable:
the gate's own numbers show the verification arm carrying the weight (RMSE 0.002 mm and 0.053 mm
against a 0.2 mm threshold) while the CT arm barely clears its bar (4/8 and 5/8 points, with
error bars widened to `max(err, 0.5 mm)`).

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> As of commit `14c3753`, an enumeration of every in-repository consumer of
> `foster2025_2/fig12_14_curves` found no consumer relying on the independent (CT-measurement)
> half for an assertion carried only by the verification (fitted-curve) half, and none making a
> materially incorrect evidence-type attribution. One gate legitimately requires both halves.

It licenses **nothing** beyond that. In particular it does **not** say:

- that `foster2025.machine_mode` is validated, independently or otherwise. The registry strength
  stays `source_curve_reproduction` and the evidence record stays `reality_facing: false`;
- that the CT data is held out. The controlling card records the opposite;
- anything about `foster2025_2/fig6_front_position`, `fig8_headspace` or `fig15_flow_pressure`,
  which are separate manifest rows this audit deliberately excluded;
- anything about physics. This is bookkeeping.

The ceiling may not exceed the weakest evidence consumed — provenance metadata and source text —
so it is a **statement about attribution**, carrying no physical content.

## Reopen condition

A **new or edited consumer** of this dataset that relies on the independent (CT) half for an
assertion the CT columns do not carry — most plausibly a new gate or claim scoring against the
fitted-curve columns while describing the result as independent or CT-validated. Re-running
`python -m puckworks.analysis.screen_i045_evidence_halves` detects it: the coverage check fails
on any consumer the attribution table does not cover, the column trace shows which half is
actually read, and the structural check fails if any evidence record starts asserting
independence for this dataset.

**Not** reopened by a dispute about the manifest's own word "independent" — that ambiguity is
resolved by the controlling card's circularity note, and re-litigating it would be a question
about the cell rather than about which half a consumer reads.

## Next action

Record the retirement in [`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md).

The docstring wording observation is carried there and no further. Correcting it would be an edit
to a gated component's docstring, which is out of scope for a cheap screen and is not required by
any finding.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i045_evidence_halves
pytest tests/test_screen_i045.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Branch base (Wave-1 merge): `14c3753c6e8dab2995332dbe1c3d1e04c4348051`
- Branch: `insights/if6b-wave2-cheap-screens`
