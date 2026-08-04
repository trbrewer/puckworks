# I-010 — Pannusch closure portability

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

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

## Step 6 — uncertainty, and the predeclared materiality criterion

**Both components were computed from the baseline alone, before any substitution was run.**

- **Observational:** `obs = 4.70 %` — the median measured per-condition RSD of
  `angeloni2023/total_solids` (n=66). TS is used because it *is* one of the four scored
  observables, is measured on the same shots, and its median sits well inside the source's
  stated global 0.3–19.7 % band for the named bioactives. The campaign does **not** retain
  solute-specific RSD for caffeine/trigonelline/CGA. The lipid median (12.55 %) is carried as
  an upper sensitivity and is not a scored observable.
- **Numerical:** `num = 0.0001 %` — the *maximum* relative change in the held-out prediction
  between `NZ=200 / 1e-6` and `NZ=400 / 1e-8` across all 72 points. Negligible; the budget is
  entirely observational.

> **PREDECLARED MATERIALITY CRITERION.** A substitution is MATERIAL iff the **median** absolute
> relative change in the held-out predicted concentration, across all 72 held-out
> (condition × species) points, exceeds
> **U = √(obs² + num²) = 4.700 %**.
>
> The median — not the mean, not the max — so a single domain-edge condition cannot decide the
> screen. The fraction of points above U and the per-species breakdown are reported and are
> informative, but they are **not** the criterion.

This is derived from retained uncertainty, not from a round percentage, and it was fixed in the
module before any swap was computed.

## Result

| substitution | median abs. rel. change | material vs U = 4.70 % | counts toward decision |
|---|---|---|---|
| `vant_hoff_K` → Arrhenius T-law | **2.968 %** | no | yes |
| `diffusion_coeff` → Stokes-Einstein T-law | **0.831 %** | no | yes |
| `water_density` → TR2001 | **0.012 %** | no | yes |
| `water_viscosity` → TR2001 @ `X_w=100 %` | 8.885 % | *yes* | **no** (out of its own range) |
| `sherwood_h` | — not run — | — | no (unsubstitutable) |

**Validity-range check** (the candidate's second SURVIVE arm, independent of any swap): under
the frozen configuration the consumer drives the artifact at **T 88–98 °C** (declared 80–98)
and **Q 1.045–2.344 mL/s** (declared 1–3). Strictly **inside** its declared range. That arm does
not fire.

**Recalibration branch: not triggered.** No admissible swap was material, and the brief
conditions the branch on a material no-refit effect.

## Figure

`figures/primary.png` — held-out concentration per species and condition under each closure,
with the measured points and their replicate band. Arabica shown; all 18 conditions × 4 species
are in `result.json`. The baseline is drawn as a wide pale line so the swap curves sitting on
top of it are visible — that coincidence *is* the result.

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
- It did **not** run any candidate outside Wave 1, and did no novelty research.
