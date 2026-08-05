# I-010 — Pannusch closure portability

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-04 — disposition changed from RETIRE to NEEDS_NEW_DATA.** The first
> version used the median total-solids replicate RSD (4.70 %) as the decision authority for all
> four scored outputs, three of which have no retained replicate uncertainty at all. Each output
> is now judged against its own. The path, the frozen configuration, the admissible
> substitutions and the no-refit predictions are unchanged.

## What was run

**Question** (generated, verbatim from the candidate):

> Which registered component, if any, actually consumes pannusch2024.closures's output — and
> does that consuming result change materially when the artifact is swapped for another
> source's or driven outside its declared validity?

Reduced to the operational form the authority set: *does substituting one declared closure at a
time materially change held-out predictions from `pannusch2024.solver`?*

## How to re-run

```
python -m puckworks.analysis.screen_i010_closure_portability
```

Writes `result.json` and `figures/primary.png`. ~2 min — ten 18-condition × 4-species sweeps
(baseline + four swaps, once for the result and once for the figure) at ~0.16 s per PDE solve.

Focused test: `pytest tests/test_screen_i010.py -v`

## Step 1 — the consuming path (established from source, not co-location)

The generated row recorded **same-stage co-location only** and explicitly said no
output-to-input path had been checked. It is real, and it is a direct import:

```
puckworks/models/pannusch2024/solver.py:30
    from puckworks.models.pannusch2024 import closures as pc
```

| closure | how it reaches the consumer | enters the solve as |
|---|---|---|
| `sherwood_h` | direct — `solver.py:101, 102` (and `:189, :190` in the Q(t) adapter) | `h1`, `h2` [m/s] via `m1, m2, f1, f2` |
| `vant_hoff_K` | direct — `solver.py:103, 173` | `K` [-], in the transfer terms **and** the initial condition `c0[1:nz] = K·cs0/cl1` |
| `diffusion_coeff` | transitive, only via `sherwood_h` | `D` — sets `Sc`, and `h ~ Sh·D/d32`, so `h ~ D^(2/3)` |
| `water_viscosity` | transitive, only via `sherwood_h` | `μ` — enters `Re`, `Sc` and Wilke-Chang `D` |
| `water_density` | transitive, only via `sherwood_h` | `ρ` — only through the kinematic viscosity `μ/ρ` |

**The interface is three scalars per solve: `h1`, `h2`, `K`.** All five declared closures reach
the consumer only through those three numbers. That is a structural finding in its own right,
and it is why an insensitive outcome would not be surprising.

This closes the candidate's INCONCLUSIVE branch ("no consuming path can be established").

## Step 2 — the held-out unit

`angeloni2023` (bioactives + total_solids), granulometry O, on-grid conditions, both varieties.
**18 conditions × 4 species = 72 held-out points.**

MANIFEST `validation_strength`, verbatim:

```
independent (different machine/coffee/basket than pannusch fit or cameron calibration)
```

Non-circular by construction: angeloni was never used to fit `pannusch2024.closures`. The
closures' own fit target (the Schmieder kinetics) is **excluded** — scoring against it would be
circular, which is exactly what the candidate's method statement rules out.

## Step 3 — what is frozen

Grid `NZ=200`, five-point biased upwind, BDF, `rtol=atol=1e-6`; Dirichlet `c_l(z=0)=0`; bed
15 mm × 58 mm, `α_l = 0.17`; centre grind `GRIND_17`; measured-flow input `_flow_darcy`
(Darcy `q ~ p/μ(T)`, anchored at 40 g / ~24 s at 9 bar, **not fitted to concentrations**);
inventory basis = pannusch Table 2 `c_s0`, **blind, no refit**; observation operator = the
matched-beverage-mass endpoint at 40 g. Full record in `result.json → frozen`.

**One freeze is load-bearing and was decided before running, not discovered afterwards.** The
p→flow map `_flow_darcy` *itself* calls `pc.water_viscosity`. Left unfrozen, a viscosity swap
would move the boundary condition and the model closure simultaneously and the screen would be
measuring two things at once. **The flow map is held at the baseline viscosity for every swap.**
That the same calibration artifact is consumed twice, on opposite sides of the model boundary,
is itself worth recording.

## Step 4 — the substitutions

One closure at a time, each from a **declared in-repo alternative**. Where the alternative uses
a different convention, only the declared **temperature law** is swapped, anchored so the
alternative reproduces pannusch's own value at pannusch's own `Tref = 360.15 K`. A raw numeric
swap would measure the convention difference rather than portability, and merging the two
conventions is forbidden (CLAUDE.md rule 6).

| closure | alternative | admissible? |
|---|---|---|
| `vant_hoff_K` | `romancorrochano2017.extraction.K_of_T` Arrhenius T-law, anchored | **yes** |
| `diffusion_coeff` | romancorrochano Stokes-Einstein `D ~ T` T-law, anchored | **yes** |
| `water_density` | `telisromero_density_kgm3` at `X_w = 1` | **yes** |
| `water_viscosity` | TR2001 Eq (10) at `X_w = 100 %` | **no — bound only** |
| `sherwood_h` | *none exists* | **unsubstitutable** |

Two exclusions, both recorded rather than worked around:

- **`water_viscosity`.** TR2001 Eq (10) is declared over `X_w` 76–90 % (coffee extract); at
  `X_w = 100 %` it returns ~0.56× the VDI water value, i.e. it is being driven far outside *its
  own* range. Running it measures TR2001's extrapolation error, not pannusch's portability, so
  it is excluded from the decision and reported as a labelled bound. **The corpus holds no
  second pure-water viscosity correlation declared over 88–98 °C.** That absence is a finding.
- **`sherwood_h`.** No second Sherwood correlation is registered or carded. The fitted `(A, B)`
  are per-solute in Table 2 and the card itself says they "lack physical meaning and
  generality"; moving one solute's pair onto another is a misuse, not a source swap, and was
  not performed.

## Step 6 — retained uncertainty, PER OUTPUT

This is what the correction changed, and it is the whole of the change.

| output | retained uncertainty | authority used |
|---|---|---|
| `tds` | **measured per-condition RSD** (`angeloni2023/total_solids`, RSD_pct column) — median **5.30 %** over these 18 conditions | a real threshold; a real answer follows |
| `caffeine` | **none per cell** | declared range 0.3–19.7 %, evaluated at both ends |
| `trigonelline` | **none per cell** | declared range 0.3–19.7 %, evaluated at both ends |
| `5CQA` | **none per cell** | declared range 0.3–19.7 %, evaluated at both ends |

Sources, verbatim: `angeloni2023/bioactives` uncertainty cell reads `%RSD 0.3-19.7 (in card, not
per-cell)`; `angeloni2023/total_solids_lipids_rsd` records `caffeine/trigonelline/CGA
solute-specific RSD NOT recovered (Tables 4-5 give only global ranges 0.3-19.7%); raw replicates
still owed`.

**The 4.70 % figure is retained but demoted.** It is the campaign-wide median total-solids RSD
over all 66 shots — the number the superseded version used as the authority for everything. It
now appears only as `uncertainty.proxy_U_pct`, labelled a proxy sensitivity, and `_classify()`
never reads it. Note it is not even the right total-solids figure for this screen: the 18
held-out conditions have their own median, **5.30 %**, which is what governs `tds` here.

**Numerical uncertainty** is 0.0001 % (max, `NZ=200/1e-6` vs `NZ=400/1e-8` across all 72 points)
— negligible against every threshold above, and it changes no classification.

### The effect statistic (unchanged) and how it is applied (changed)

The statistic is still the **median absolute relative change** in the held-out prediction across
the 18 conditions. It is now computed and classified **separately per output**; analytes with
different uncertainty authority are never pooled into one decisive median. Pooled figures are
still written to `result.json` (`pooled_*`) purely so the correction is auditable against the
first version — nothing reads them.

### Fixed classification

Per (substitution, output):

- `MATERIAL_THROUGHOUT` — median effect exceeds the threshold everywhere in the applicable range
- `IMMATERIAL_THROUGHOUT` — median effect is below it everywhere
- `CHANGES_WITHIN_RANGE` — material at one end of the declared range, immaterial at the other

Candidate level, in this precedence:

- **SURVIVE** — ≥1 admissible swap `MATERIAL_THROUGHOUT` for ≥1 output, **or** the artifact is
  consumed outside its declared range
- **RETIRE** — every admissible swap `IMMATERIAL_THROUGHOUT` for every output, **and** inside the
  declared range
- **NEEDS_NEW_DATA** — materiality changes within the retained range, with solute-specific
  replicate RSD named as the missing evidence

## Result — **NEEDS_NEW_DATA**

Median (max) absolute relative change, per output:

| substitution | caffeine | trigonelline | 5CQA | tds |
|---|---|---|---|---|
| K(T) → Arrhenius T-law | 3.171 (5.539) `CHANGES` | 3.061 (5.416) `CHANGES` | 3.138 (5.581) `CHANGES` | 1.709 (3.006) **`IMMATERIAL`** |
| D(T) → Stokes-Einstein T-law | 0.946 (1.674) `CHANGES` | 0.663 (1.247) `CHANGES` | 0.899 (1.665) `CHANGES` | 0.770 (1.411) **`IMMATERIAL`** |
| ρ(T) → telisromero2001 | 0.018 (0.055) `IMMATERIAL` | 0.006 (0.020) `IMMATERIAL` | 0.009 (0.030) `IMMATERIAL` | 0.009 (0.030) **`IMMATERIAL`** |
| *μ(T) @ X_w=100 % — excluded* | *13.661 `CHANGES`* | *6.136 `CHANGES`* | *9.691 `CHANGES`* | *7.948 `MATERIAL`* |
| *`sherwood_h` — unsubstitutable* | — | — | — | — |

**Total-solids per-condition exceedances** — the median criterion is what decides, but the
conditionwise counts are not zero and are reported as such:

| swap | median effect | max effect | conditions exceeding their **own** measured RSD |
|---|---|---|---|
| K(T) | 1.7093 % | 3.0055 % | **2 of 18** |
| D(T) | 0.7702 % | 1.4111 % | **1 of 18** |
| ρ(T) | 0.0089 % | 0.0296 % | **0 of 18** |

All three are immaterial for total solids **by the predeclared median-effect vs median-RSD
criterion** (median measured RSD 5.30 %). The machine label is `IMMATERIAL_BY_MEDIAN_CRITERION`
and every record carries a `status_scope` stating that it does not assert zero condition-level
exceedances.

**Validity range:** T 88–98 °C (declared 80–98), Q 1.045–2.344 mL/s (declared 1–3) — strictly
inside. That SURVIVE arm does not fire.

**Recalibration branch:** not triggered (no admissible swap is material throughout).

**What would resolve it:** a solute-specific RSD **above ~3.2 %** retires the candidate; **below
~0.7 %** it survives; between them it splits by substitution.

## Figure

`figures/primary.png` — two panels.

**Top** (the candidate's required minimum figure): held-out concentration per output and
condition under each closure, over the common validity range. Each output's measured points
carry the uncertainty it *actually has* — a measured per-condition bar for total solids, and for
the three bioactives the full declared 0.3–19.7 % range drawn as a band, because no per-cell
value exists. The baseline is a wide pale line so coincident swap curves stay visible.

**Bottom** (the decisive panel): each swap's median and maximum held-out effect per output,
against that output's own authority. The declared bioactive band is drawn over the three solutes
it governs and stops at the total-solids group, which has its own measured threshold.

There is no recalibrated curve to distinguish: the branch was not triggered, so every curve is
no-refit.

Not registered in the viz layer, for the same reason as I-040: it is a screen artifact, not a
mechanism render bound to a VizSpec fidelity ceiling, and the IF-5 decision forbids extending a
governed registry before Wave 1 reports. House print palette; the categorical subset passes the
light-surface colour checks; every series is direct-labelled in the legend.

## Corpus warnings

**None of the 32 build warnings is load-bearing for this screen**, and none was repaired.
`docs/cards/pannusch2024.md` resolves with no `TEMPLATE_DEVIATION`. The alternative closures come
from the **registered component** `romancorrochano2017.extraction` (card
`romancorrochano2017_extraction.md`, which resolves) and from `puckworks.data` accessors — *not*
from the `romancorrochano2017/*` MANIFEST rows that carry warnings 2–11, so those are outside
this screen's evidence path by construction. All 32 deferred; see
[`../../IF5_HUMAN_TRIAGE_DECISION.md`](../../IF5_HUMAN_TRIAGE_DECISION.md) §7.

## Scope — what this screen did NOT do

- It did **not** test inventory matching (substituting angeloni Table 7 `c_s0`). That is a
  different experiment and is already archived in `angeloni_bracket`.
- It did **not** refit anything. The no-refit branch is the whole of the decision.
- It did **not** run a response sweep. That is RP-A's scope (ROADMAP §9).
- It did **not** change any evidence label, badge, validation rung or model verdict.
- It did **not** invent a bioactive replicate RSD, and specifically did not adopt the
  total-solids value, a midpoint, or the best cell as a stand-in for one.
- It did **not** run any candidate outside Wave 1, and did no novelty research.
