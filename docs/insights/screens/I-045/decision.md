# I-045 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-05 after exact-head review — disposition changed from RETIRE to SURVIVE.**
> The first version read the manifest's "independent (CT data)" as an independent *measurement
> modality*. That is not the repository's definition. **ROADMAP §0** defines *independent* as
> **data not used in fitting the thing being tested**, and the controlling card records that
> `k` and `φ_T` were fitted to the very s/H curves the CT columns hold. The CT arm is therefore
> **post-fit, same campaign** — and `gate_foster_ct_trajectory` calling it "independent" is a
> materially incorrect evidence-type attribution, which is the finding.

## Question

For every consumer of `foster2025_2/fig12_14_curves`, does the consumer's actual assertion depend
on independent evidence, verification evidence, both, or neither?

**The controlling vocabulary is ROADMAP §0**, read at run time by the screen:

| term | definition |
|---|---|
| **independent** | data **not used in fitting** the thing being tested |
| **post-fit reconstruction** | model reproduces the dataset its parameters were fitted to |
| **verification** | model-vs-model / asymptotic / budget |

Neither arm of this dataset is independent under that definition.

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

**7 consumers attributed. Coverage complete. 1 misattribution finding.**

### The halves are different columns, so attribution is observed

| arm | columns | rows | evidence type under ROADMAP §0 | manifest wording correct? |
|---|---|---|---|---|
| fitted curves | `s_fit_mm`, `w_fit_mm`, `H_fit_mm` | 461 | **verification** | ✔ |
| CT observations | `s_data_mm`, `H_data_mm`, `w_data_mm` + `*_err_mm` | 8 | **post-fit reconstruction (same campaign, not held out)** | ✘ — the cell says "independent" |
| time base | `t_s` | 461 | none | ✔ |

Traced columns for `gate_foster_ct_trajectory`: `t_s`, `s_fit_mm`, `H_fit_mm`, `s_data_mm`,
`s_data_err_mm`, `H_data_mm`, `H_data_err_mm` — **both arms, as attributed.**

### Why the CT arm is not independent

`docs/cards/foster2025_2.md`, verbatim:

> Note the circularity: k and φ_T are fitted to the same s/H curves being reproduced, so the
> source validates model FORM, not parameter-free prediction.

The parameters were fitted to these curves. Under ROADMAP §0 that makes the arm **post-fit**, not
independent. The distinction is not pedantic: an independent rung licenses a claim about
out-of-sample behaviour, and this arm cannot support one.

### Attribution table

| consumer | location | assertion | verif? | post-fit? | claims independent? | class |
|---|---|---|---|---|---|---|
| `gate_foster_ct_trajectory` | `gates.py:1125` | (a) port matches the source's fitted ODE to <0.2 mm RMSE; (b) port brackets ≥4 of 8 CT points within max(err, 0.5 mm) | ✔ | ✔ | **✘ YES — the finding** | **VERIFICATION_AND_POST_FIT_SAME_CAMPAIGN** |
| `EVIDENCE_LINKS …::gate_foster_ct_trajectory` | `paper3/EVIDENCE_LINKS.json` | adjudicates `source_curve_reproduction` / `same_campaign_not_held_out` / `reality_facing: false` / `context_only` | ✔ | — | no | VERIFICATION |
| paper3 evidence graph (generated) | `docs/paper3_resource/generated/` | renders the same adjudication | ✔ | — | no | VERIFICATION |
| paper3 Fig-2 evidence vector (generated) | `docs/figures/paper3/source_data/` | relation `source_curve_reproduction`, outcome **`negative`** | ✔ | — | no | VERIFICATION |
| registry `foster2025.machine_mode` | `models/__init__.py:328` | registers the gate; component strength `source_curve_reproduction` | — | — | no | NEITHER |
| PV-02 evidence selection | `public/claims.py:208` | **excludes** the gate "on its own merits" | — | — | no | NEITHER |
| loader smoke test | `tests/test_data_loaders.py:131` | a non-empty `s_data_mm` exists — a parse check | — | — | no | NEITHER |

**No consumer is classified INDEPENDENT_LOAD_BEARING**, because nothing in this dataset is
independent evidence.

## Primary figure

[`figures/primary.png`](figures/primary.png) — the two arms with their evidence type under
ROADMAP §0, then each consumer with the columns it reads, the arms load-bearing for it, and the
misattribution flagged.

## Adversarial check

The scan covered `independent`, `independently`, `verification`, `verified`, `validation` across
five consuming surfaces. **6 hits, 0 unclassified.** The decisive one is hit 1: the gate
docstring's `independent` on the CT arm.

The strongest attempt to keep the earlier RETIRE was: **"the manifest says independent, the gate
is only copying it, and everything downstream refuses the strong reading — so nothing is
wrong."** Three ways that fails:

1. **Copying an incorrect label does not make it correct.** The manifest cell is itself one of
   the surfaces this audit was asked to check. Treating it as the authority would make the audit
   circular — a lineage screen cannot use the label under audit to validate itself.
2. **Containment bounds a blast radius; it does not repair an attribution.** The evidence record
   genuinely does refuse the strong reading (`same_campaign`, `fit_input`, `reality_facing:
   false`, `context_only`), and that is why the finding is a wording defect rather than a
   propagated over-claim. But the candidate's SURVIVE arm asks whether a consumer *makes* a
   materially incorrect evidence-type attribution, not whether anyone downstream believed it.
3. **The glossary is the authority and it is unambiguous.** ROADMAP §0: independent means *data
   not used in fitting the thing being tested*. The card records the fit. There is no reading
   under which these CT curves are held out.

**Three defects in the scan instrument were found and fixed before it was allowed to conclude**,
and the second is the reason the earlier version reached the wrong verdict:

1. the manifest scan used a character window that **bled into adjacent dataset rows** — now
   clipped to the target row;
2. fragment matching was first-match-wins and **classified the docstring's `independent` hit
   using the adjacent `verifying the port`**, i.e. it reported the one real misattribution as
   correct usage. Rules now require the fragment to contain the token;
3. `EVIDENCE_LINKS.json` contains **none** of the five tokens — it states independence in a
   machine-readable field, so a prose scan alone reported a silent surface. The fields are now
   read directly.

## Strongest alternative explanation

*"The cell is mixed only in wording; both halves support the same assertion equally."*

**Refuted, and in a way that sharpens the finding.** The two arms support two *different*
assertions and the gate needs both — the RMSE arm only from `s_fit_mm`/`H_fit_mm`, the bracketing
arm only from the CT columns. So "uses both arms" is a correct description of the gate.

But *which* two things it uses is exactly what was mislabelled. It is not `independent +
verification`. It is **verification + post-fit (same campaign)**, and neither arm is independent
evidence of anything.

A second alternative, considered and rejected: *"'independent' here means an independent
measurement modality — a real CT observation as opposed to model output."* That is the reading
the first version of this screen adopted, and it is recorded in `result.json →
rejected_reinterpretation`. It is not the repository's definition, and under it almost any
measurement would qualify as independent, which would empty the rung of content.

## Decision

**SURVIVE.**

The candidate's rule applied without revision: *"SURVIVE — a consumer states `independent` for an
assertion carried only by the `verification` half."* The corrected finding is the same defect in
its more precise form: **`gate_foster_ct_trajectory` states `independent` for an assertion carried
by the post-fit, same-campaign CT arm.** Under ROADMAP §0 that arm is not independent, and the
attribution is materially incorrect.

`RETIRE` would require every consumer to attach an evidence type its columns support. One does
not. `NEEDS_NEW_DATA` would require insufficient source metadata; the metadata is unusually good
— separate columns, and a card that states the circularity in one sentence.

**This concerns evidence attribution, not the numerical gate result.** The gate's RMSE (0.002 mm
and 0.053 mm against a 0.2 mm threshold) and its CT bracketing (4/8 and 5/8) are not in question
and are not changed by anything here.

## Why

1. **The glossary is unambiguous and the card supplies the fact it needs.** *Independent* = not
   used in fitting; `k` and `φ_T` were fitted to these curves. One sentence in each document
   settles it.
2. **The label is load-bearing in a way the numbers are not.** An independent rung licenses an
   out-of-sample reading. This arm cannot support one, and the card says so explicitly: the
   source "validates model FORM, not parameter-free prediction."
3. **The defect is upstream of the gate.** The manifest cell says "independent (CT data)" and the
   gate copies it. That is why the repair targets below start with the manifest.

## Affected surfaces — the exact future correction targets

**Named here. NOT corrected in this PR** — a cheap screen may identify an attribution defect but
may not edit an evidence label, a gate, or a generated evidence artifact.

| # | target | current | defect |
|---|---|---|---|
| 1 | `puckworks/data/MANIFEST.csv` — `foster2025_2/fig12_14_curves` `validation_strength` | `independent (CT data) / verification (fitted curves)` | "independent" is wrong for the CT arm under ROADMAP §0 — the arm is post-fit, same campaign, not held out |
| 2 | `puckworks/validation/gates.py` — `gate_foster_ct_trajectory` docstring | `… within their error bars (independent, 'qualitative-good')` | attaches the independent rung to the same-campaign CT arm. **The numerical gate is unaffected** |
| 3 | any reader-facing description inheriting the independent-evidence label for this dataset | none found at this head | would inherit the same defect if written |

The exact replacement wording is a **human decision** — a screen may not write an evidence label.

### Already correct, and deliberately NOT a target

`puckworks/paper3/EVIDENCE_LINKS.json` needs no change: it already refuses the held-out and
reality-facing readings, recording the dataset as `eval`/`same_campaign` **and** `fit`/`fit_input`
with `relationship: same_campaign_not_held_out`, `reality_facing: false` and
`support_status: context_only`.

A test asserts all four named source surfaces are **byte-unchanged** in this PR.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> As of `14c3753`, `gate_foster_ct_trajectory` describes its micro-CT bracketing arm as
> "independent" evidence, but the controlling card records that the parameters it tests were
> fitted to those same s/H curves. Under the repository's own glossary that arm is post-fit,
> same-campaign evidence, so the gate's evidence-type attribution is incorrect. The manifest cell
> it copies carries the same defect.

It licenses **nothing** beyond that. In particular it does **not** say:

- that the gate's numerical result is wrong, or that `foster2025.machine_mode` fails anything.
  The gate passes and this screen does not touch it;
- that any evidence label has been changed. None has — the targets above are named, not edited;
- that the defect propagated. It did not: `EVIDENCE_LINKS.json` and every generated artifact
  already refuse the strong reading;
- anything about `foster2025_2/fig6_front_position`, `fig8_headspace` or `fig15_flow_pressure`,
  which are separate manifest rows this audit deliberately excluded;
- anything about physics. This is evidence bookkeeping.

The ceiling may not exceed the weakest evidence consumed — provenance metadata and source text —
so it is a **statement about attribution**, carrying no physical content.

## Next action

**No retirement is recorded.** I-045 is **not** entered in `RETIRED_CANDIDATES.md`.

I-045 enters the **IF-7 deep-screen queue** as the first survivor of the cheap-screen portfolio.
**IF-7 work does not start in this PR.**

The three correction targets above are a separate, human-owned change: editing an evidence label
is outside a screen's authority, and target 1 in particular sets the wording the other two
inherit.

Per triage rule 1, a SURVIVE is what unlocks deep screening and external novelty research — but
neither is performed here.

## Reproduction

```
python -m puckworks.analysis.screen_i045_evidence_halves
pytest tests/test_screen_i045.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Branch base (Wave-1 merge): `14c3753c6e8dab2995332dbe1c3d1e04c4348051`
- Branch: `insights/if6b-wave2-cheap-screens`
