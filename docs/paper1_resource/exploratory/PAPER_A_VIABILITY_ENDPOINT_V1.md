# Part A — the analytical endpoint against the WIDE-referenced tolerance

```
EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
NOT_A_FROZEN_P0_GATE_RESULT
```

**gate_binding:** `null` · **date:** 2026-08-03 · **data:** `PAPER_A_VIABILITY_ENDPOINT_V1.json`
**producer:** `tools/paper_a_viability_endpoint.py` · **figures:** `figures/endpoint_*.png`

P0-G8 remains **open**. `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` was neither written nor read. Every
definition, grid, tolerance, threshold family and decision rule is taken unchanged from the accepted
architecture; nothing here was tuned to the result.

---

## The question

For each of the six variety–solute groups, does the analytical `κ = ∞` endpoint stay inside the
operational tolerance referenced to the best finite fit on `D_WIDE = [0.15, 500]`?

```
J(κ)  = min over I > 0 of MAPE(y, I·f(κ))
J_ref = min over κ ∈ D_WIDE of J(κ)
J_inf = min over I > 0 of MAPE(y, I·f_inf)
```

## Results

| group | `J_ref` | `κ_ref` | `J_inf` | `J_inf − J_ref` | `J_inf/J_ref` | 10 % relative |
|---|---|---|---|---|---|---|
| Arabica:caffeine | 2.8319 | 0.764 | 2.9945 | +0.1625 | 1.0574 | **included** |
| Arabica:trigonelline | 2.2431 | 1.700 | 2.2771 | +0.0340 | 1.0152 | **included** |
| Arabica:5CQA | 4.6056 | 1.025 | 5.0944 | +0.4888 | 1.1061 | **excluded** |
| Robusta:caffeine | 4.8934 | 6.312 | 4.8998 | +0.0064 | 1.0013 | **included** |
| Robusta:trigonelline | *unresolved* | — | 3.8630 | — | — | *indeterminate* |
| Robusta:5CQA | *unresolved* | — | 11.7653 | — | — | *indeterminate* |

All values in percentage points. Levels were profiled exactly by weighted median; no minimiser set
was a non-degenerate interval, so every reported `I*` is a point.

### Every threshold-family member

| group | 5 % rel | 10 % rel | 20 % rel | 0.10 pp abs | 0.25 pp abs |
|---|---|---|---|---|---|
| Arabica:caffeine | excluded | included | included | **excluded** | included |
| Arabica:trigonelline | included | included | included | included | included |
| Arabica:5CQA | **excluded** | **excluded** | included | **excluded** | **excluded** |
| Robusta:caffeine | included | included | included | included | included |
| Robusta:trigonelline | indeterminate | indeterminate | indeterminate | indeterminate | indeterminate |
| Robusta:5CQA | indeterminate | indeterminate | indeterminate | indeterminate | indeterminate |

**Programme reading under the accepted group-outcome rule: `H1_DOES_NOT_LEAD`.** Four of six groups
are group-level failures — two on exclusion (Arabica:caffeine under the 0.10 pp absolute convention;
Arabica:5CQA under four of five conventions) and two on an unresolved reference minimum. One failure
suffices; there are four.

## The two unresolved groups are a result, not a defect

Robusta:trigonelline and Robusta:5CQA return `reference_minimum_status = unresolved`, but their
reference-minimum **value** is stable to ~1e-12 across all four nested grids against a 4e-4
tolerance. What moves is the size of the retained argmin set (3→3→8→23 and 3→4→6→14). The objective
is flat to within the retention band over **1.7 and 1.4 decades** of `κ`, running to the domain
edge, and the finite-domain minimum coincides with the analytical endpoint to ~1e-11.

On that support the data do not distinguish a finite rate multiplier from the large-coefficient
limit **at all**. That is the response-limit phenomenon appearing through a criterion failure rather
than through a threshold test. Under a value-only criterion both groups would be included under
every convention and the programme reading would still be `H1_DOES_NOT_LEAD`, carried by the two
Arabica failures.

## Numerical error is not the limiting factor — and that is the problem

The error budget is numerical only: mesh refinement 100/200/400 (worst relative `f` deviation
6.0e-9, ×2 safety), floating point, endpoint construction (3.4e-12), and the search envelope. It
totals **≈1.2e-6 pp**, so no group is boundary-indeterminate on numerical grounds.

But the margins that decide the programme are **0.02–0.06 pp**. Arabica:5CQA misses the 10 %
relative threshold by 0.028 pp on a `J` of 5.09 — a relative margin of 0.6 %. The campaign's own
published repeatability for these analytes is given only as ranges (Arabica 0.3–19.7 %, Robusta
0.1–19.2 %, `n ≈ 2`); per-solute RSDs were never published. The decision is numerically resolved and
empirically arbitrary, and an `ε` that excludes measurement uncertainty is the wrong yardstick for
the comparison it is being asked to settle.

## Plain-language interpretation

Within the declared model, on this nine-condition optimal-grind support, and at this configuration:

- For **four** groups a finite rate multiplier fits better than the infinite-rate limit, but by very
  little — the penalty for going to the limit is 0.006 to 0.16 percentage points for three of them.
- For **Arabica:5CQA** the penalty is real and larger: 0.49 pp, about 11 % relative. That group is
  excluded under four of the five declared conventions and is the clearest case where the endpoint
  is *not* operationally acceptable.
- For the **two Robusta groups** the objective is genuinely flat approaching the limit: the data
  carry no information distinguishing a fast finite rate from an infinite one.
- The verdict moves with the tolerance. Under the 20 % relative convention every evaluable group is
  included; under 5 % relative and the 0.10 pp absolute convention, half are excluded. The
  convention is doing as much work as the data.

**Not claimed.** Nothing here says real espresso reaches the large-coefficient regime (PR-12 is
`OPEN-AND-SCOPED`), that `κ` is a physical constant (PR-14 is assured-by-refusal), that the
acceptable set has no upper limit, or that the effect is structurally non-identifiable. Flatness of
one objective on one nine-condition design is operational, not structural.

## Figures

| file | content |
|---|---|
| `figures/endpoint_summary_six_panel.png` | all six profiles with `J_ref`, both displayed thresholds, and the endpoint marker |
| `figures/endpoint_Arabica_caffeine.png` | per-group profile |
| `figures/endpoint_Arabica_trigonelline.png` | per-group profile |
| `figures/endpoint_Arabica_5CQA.png` | per-group profile — the clearest exclusion |
| `figures/endpoint_Robusta_caffeine.png` | per-group profile |
| `figures/endpoint_Robusta_trigonelline.png` | per-group profile — flat to the domain edge |
| `figures/endpoint_Robusta_5CQA.png` | per-group profile — flat to the domain edge |
