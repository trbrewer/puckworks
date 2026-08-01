# Paper A — claim ledger at the scientific pivot

**Frozen state:** merge commit `eaa3ee7e4930c053e16254ea254fe6073e0032b2`
**Opened:** 1 August 2026, Stage 0 of `paper1_recommended_scientific_pivot_and_revision_plan_20260801.md`
**Purpose:** one page recording what the paper may currently assert and what is open, so that the
rewrite (plan Stage 6) is written against a fixed target rather than against results still moving.

The plan is explicit that the manuscript must not be rewritten before the first analytical gates
close. This ledger is the object the rewrite will be checked against when they do.

---

## 1. Supported now

Each of these is archived, gated, and reproducible from a producer in the repository.

| # | Claim | Basis |
|---|---|---|
| S1 | Extractable inventory is an **exact multiplicative level** in the declared model: `yhat_i = I f_i(k)`. | Algebraic; gated by the unit-inventory scaling tests |
| S2 | Whole-cup calibration on the nine optimal-grind conditions leaves a **broad, often boundary-reaching** inventory–rate profile. | `identifiability_panel`, profiled objectives across SSE / relative-L2 / Huber |
| S3 | Observation-window mismatch **manufactures a large apparent error**; matching the collected-mass endpoint removes it. | Matched-endpoint tests |
| S4 | Held-out coarse/fine endpoint accuracy **coexists with weak localisation** of the inventory–rate split. | Cross-grind transfer errors against the profile width |
| S5 | The pooled mechanistic advantage is **the mean of two opposite results**: coarse −1.02 pp (favours model), fine +0.23 pp (favours the constant). | Corpus contract, reported since the domain-referee round |
| S6 | The advantage is **benchmark-sensitive**: −0.394 pp against a level-only constant, −0.251 pp against an equal-information empirical response. | `empirical_benchmarks.py`; reproduces the referee's independent calculation exactly |
| S7 | The advantage is **not stable to refitting**: median −0.058 pp, range [−0.328, +0.416], favouring the model in 6 of 9 leave-one-condition-out folds. | `paper_a_refit_aware_comparison.py` |
| S8 | The cross-grind test **does not validate a grind mechanism**: particle geometry is frozen; the target grind enters through hydraulics and the endpoint. | Table 2 provenance correction + Table 5a dependency table |
| S9 | **Schmieder's published complete cups are not an independent assay.** They are the closed-form integral of the authors' per-replicate exponential fit to the fractions: 427 of 432 agree to <0.01 %, median 3.2e-5 %, against a reported cup RSD of 2.5 %. | `tools/audit_schmieder_cup_provenance.py` |
| S10 | In this parameterisation, **all local rate information after profiling the level is the weighted variance of the log-rate sensitivities**: `det(G) = (sum w)^2 Var_w(s)`. | `puckworks/paper_a/separability.py`, identity under test |

---

## 2. Open — and what would close it

| # | Question | Status |
|---|---|---|
| O1 | Does time resolution add rate information **over a genuinely independent complete cup**? | **Blocked by S9.** The plan's Stage 1 assumed measured cups were independent. They are not, and no other espresso campaign in `puckworks/data/` pairs an independent cup assay with fractions on the same shots. |
| O2 | Does the mechanistic model retain any advantage against a **hydraulically equal** empirical baseline? | Open. The current empirical arm receives temperature and pressure but not the derived flow/residence time, so −0.251 pp is an upper bound. |
| O3 | How much of the apparent cross-grind skill is **target-grind hydraulics** versus rate recalibration versus the rest of the structure? | Open. Needs the M0/M1/M2 ablation panel. |
| O4 | Does RSI **predict nonlinear profile behaviour** well enough to be a design screen? | Under test — the plan's §5.6 admission criterion, over empirical designs only. |
| O5 | Do discretisation and tolerance changes move the **paired difference** by much less than the effect discussed? | Open. One envelope cell measured at 2,482 s; numerical-Jacobian warnings present and uncharacterised in 5-CQA. |
| O6 | Is the contribution novel against the indexed literature? | Open. Requires database access this environment does not have (see §4). |

---

## 3. Must not be claimed

Carried forward from the plan §3.2 and the frozen assurance layer's P0 criterion.

- Structural non-identifiability of espresso extraction kinetics **in general** — the results are
  local, model-based, and specific to the declared parameterisation.
- That whole-cup experiments **cannot** identify rate parameters. Sufficiently diverse conditions or
  endpoints may; that is what S10 says.
- That time resolution is the **only** route to separation.
- Validation of a **physical grind mechanism** (S8).
- A calibrated confidence interval or equivalence conclusion from nine **dependent** folds.
- That the fitted multiplier is an **intrinsic kinetic constant** — it scales inherited Sherwood
  prefactors and absorbs model discrepancy.
- Symmetrically: that the advantage is **absent**. The P0 acceptance criterion
  (`claim_policy.SURFACE_ASSERTIONS`) requires every load-bearing surface to establish neither that
  the advantage is reproducible/useful **nor** that it is absent. A pivot toward a negative result
  does not license asserting the negative.

---

## 4. Environment limits recorded rather than worked around

- **Indexed literature databases** (Scopus, Web of Science, Engineering Village) require
  subscriptions unavailable here, and MDPI and Royal Society hosts are Cloudflare-blocked from this
  environment. The plan's Stage 5 novelty search cannot be completed here; no "to our knowledge" or
  "first" phrasing may be added on the strength of anything done in this session.
- **Numerical envelope** cost is measured, not estimated: ~41 minutes for the stiffest single cell.
