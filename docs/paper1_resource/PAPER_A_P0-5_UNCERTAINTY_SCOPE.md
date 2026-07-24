# Paper A — P0-5 uncertainty-analysis scope (review MC4)

**Status: SCOPE FOR APPROVAL — no analysis has been run.** This document specifies the uncertainty
reruns the review requires, grounded in what the source data actually supports, so the author can
approve the design (and the decision points at the end) *before* any slow PDE analysis executes.

## Objective

Establish whether Paper A's two load-bearing findings survive the measurement-uncertainty and
dependence structure the current draft sets aside:

1. the **broad inventory–rate valley** (the degeneracy) — does it persist under weighted / relative /
   robust objectives, or is it an artefact of the unweighted concentration-scale SSE?
2. the **small model-vs-null skill** (pooled MAPE 8.2 % vs 8.6 %) — is the 0.4 pp difference
   distinguishable from zero once the 108 held-out points are treated as the *dependent*, clustered
   observations they are (not 108 independent units)?

## The binding data constraint (determines what is possible)

Per `puckworks/data/angeloni2023/MANIFEST_UNCERTAINTY.md` and
`docs/data_intake/ANGELONI_TRANSCRIPTION_AUDIT.md`:

- **Named solutes (caffeine, trigonelline, 5-CQA) — the principal-profile analytes — have NO
  per-cell RSD.** Only *global* ranges are published (Arabica 0.3–19.7 %, Robusta 0.1–19.2 %). A
  solute-specific weighted refit is **blocked without an additional source-data drop** (the raw
  replicates are owed from the Angeloni authors).
- **TS and lipids DO carry per-condition RSD** (Tables 2–3; `angeloni_total_solids` /
  `angeloni_lipids` loaders), with one printed 0.0 % that must take a predeclared variance floor,
  not infinite weight.

**Consequence (review MC4 fallback, adopted):** the principal named-solute analysis cannot yield a
*calibrated inferential* interval now. It is therefore scoped as a **sensitivity analysis across
plausible weighting schemes**, reported descriptively, with the calibrated named-solute interval left
explicitly **owed / blocked** on the replicate drop. The TS channel (which has per-cell RSD) is the
one place a genuinely uncertainty-weighted rerun is possible, and is used as the worked example.

## The three sub-analyses

### (A) Principal profile under multiple objectives — extends `identifiability_panel`

Re-profile the inventory–rate valley (caffeine/TR/CGA, both varieties) under a family of objectives,
holding everything else fixed:

- **O1 unweighted concentration-scale SSE** — the current baseline (already computed).
- **O2 global-RSD sensitivity sweep** — weight each observation by `1/σ²` with σ drawn from the
  *global* RSD range (run at the range endpoints + a mid value, and a per-solute uniform CV), since
  per-cell σ is unavailable. This is a **sweep, not a fit** — it brackets what weighting could do.
- **O3 relative / log-scale objective** — an already-present log-loss variant (the draft reports a
  7.0 % pooled log-loss check); extend it to the full profile.
- **O4 robust / bounded-leverage** — a Huber or trimmed objective (predeclared tuning) that caps any
  single condition's leverage.

**Report:** the normalized profiles **overlaid on one axis** (per MC8), with the near-optimal set at a
**threshold family (2 / 5 / 10 / 20 %)** rather than a single 10 % set; the right-censoring flag
carried on each. **Primary question:** does the valley stay broad and right-censored under all of
O1–O4? (Prior expectation: yes — the degeneracy is *structural* (cup conc. is exactly linear in
`c_s0`), so re-weighting should not close it. If any scheme sharply localizes the rate, that is a
material finding to surface, not suppress.)

### (B) Model-vs-null, paired & clustered — extends `transfer_skill_vs_baselines`

Replace the point "8.2 vs 8.6 % (0.4 pp), worse on 50/108" with a paired, dependence-aware interval:

- **Estimand:** the paired per-observation `ΔMAPE = MAPE_mechanistic − MAPE_null`, and its pooled mean.
- **Cluster structure:** the 108 held-out points are **6 (variety × solute) groups × (grinds C/F ×
  9 conditions)** with shared conditions, varieties, solutes, and fitted groups. The resampling unit
  must be the **cluster** (condition and/or group), not the point.
- **Method:** a **cluster / hierarchical bootstrap** — resample conditions within group (and,
  reported separately, resample groups) with replacement; recompute pooled ΔMAPE each replicate;
  report the ΔMAPE distribution + a percentile interval, and the paired sign summary as a
  *dependence-aware* statement (not a 50/108 sign test, which assumes independence).
- **Determinism:** fixed seed(s); B ≈ 2 000–10 000 (cheap — this resamples *precomputed* per-point
  errors, no PDE re-solve).
- **Presentation:** a paired group-level ΔMAPE plot (per MC7/Fig 4 comment), absolute MAPE kept to a
  small table.

### (C) LOCO coverage-calibrated interval — extends `loco_cv_refit` (the "owed" item)

The draft already flags its two LOCO intervals as **descriptive** (they resample already-computed fold
errors *without repeating the fit*, and folds overlap). The owed upgrade:

- a resampling scheme that **repeats the fit inside the loop** (refit the level+rate on each resampled
  training set, re-score the held-out condition) → a coverage-calibrated interval.
- **Cost:** this is the expensive piece — `folds × B_outer × PDE solves`. A full nonparametric bootstrap
  is likely prohibitive; propose a **bounded design** (e.g. jackknife-after-bootstrap, or B_outer ≈
  100–200 with a documented cap and a `log()`-style note of what was capped) rather than a silent
  truncation. This sub-analysis is the one to **defer or bound** if cost is a concern (decision below).

## What would / would not change the paper

- **Robust to weighting (expected):** valley persistence and small null-skill are structural; if they
  hold across O1–O4 and the clustered interval, the paper's claims *strengthen* (they survive the
  reviewer's objection) with **no evidence-strength change**.
- **Material if it appears:** a weighting scheme that closes the valley, or a clustered interval on
  ΔMAPE that excludes zero with the mechanistic model *better*, would be a genuine change — to be
  reported plainly, not smoothed. Either outcome is publishable and neither upgrades an evidence tier.

## Reporting posture & discipline

- Results are **descriptive / sensitivity**, not a calibrated named-solute inference (which stays owed).
  No evidence-strength promotion; any status change needs a ROADMAP §7.1 entry.
- New functions live in `puckworks/validation/slow/` (PDE solves; **not** CI), with fast unit tests on
  the pure resampling/objective helpers (seeded, deterministic) that *can* run in CI.
- Manuscript deltas land in the canonical `PAPER_A_DRAFT.md` first, then sync to the JFE conversion; the
  drift guard's phrase list updated if any load-bearing wording changes.

## Decision points for the author (needed before execution)

1. **Proceed now, or wait for the replicate drop?** The named-solute *inferential* interval is blocked;
   the **sensitivity-sweep** framing (A/B) can proceed now and is self-contained. Recommend: proceed
   with A + B now (sweep framing); keep the calibrated named-solute interval owed. **[decision]**
2. **Sub-analysis (C) — run bounded, or defer?** It is the only expensive piece. Recommend: **defer**
   to a separate PR (or run bounded at B_outer ≈ 100 with a documented cap). **[decision]**
3. **Robust objective choice** — Huber (with δ) vs trimmed vs bounded-leverage; pick one primary +
   one supplementary. **[decision]**
4. **Bootstrap unit for (B)** — resample-conditions-within-group as primary, resample-groups as the
   secondary sensitivity (both reported). Confirm this is the intended dependence structure. **[decision]**
5. **Supplement scope** — all six solute × variety profiles for O1–O4 in the supplement (vs a
   representative subset in main text). **[decision]**

## Effort & execution plan (once approved)

- **A + B (sweep + clustered null):** effort **M**. New `validation/slow/` helpers extending
  `identifiability_panel` (objective family) and `transfer_skill_vs_baselines` (cluster bootstrap);
  seeded pure-function unit tests in CI; overlaid-profile + paired-ΔMAPE figures; manuscript §4.2/§4.3
  deltas + a limitations update. One PR.
- **C (coverage-calibrated LOCO):** effort **M–L**, cost-bound; separate PR, or deferred per decision 2.
- No evidence-strength upgrade in either; the named-solute calibrated interval remains owed on the
  Angeloni replicate drop.
