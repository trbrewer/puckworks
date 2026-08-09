# I-093 — cross-scale permeability protocol (FROZEN BEFORE EXECUTION)

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This document is committed before the screen module exists**, and it is what the screen is bound
to. Everything below — scenario, metric, uncertainty treatment, thresholds, controls and stop
conditions — is fixed here and is not revised after seeing output.

---

## 1. Authority

| item | value |
|---|---|
| base commit | `892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa` |
| generated candidate source | `docs/insights/generated/candidate_portfolio.{md,json}` at this base |
| candidate ID | **I-093** |
| generated title (verbatim) | *Do the continuum permeability closures preserve the pore-scale trend?* |
| tension row | **T-0174** (lens `scale_mismatch`) |
| candidate status in the generated snapshot | `SEED`, unscored — unchanged by this work |

Prior decision records consulted: `docs/insights/RETIRED_CANDIDATES.md` (I-024, I-040, I-072,
I-090), the Wave-1/2/3 screen bundles, `docs/insights/IF5_HUMAN_TRIAGE_DECISION.md`, and the IF-7
deep screen for I-045. None of them screens or retires I-093.

**Load-bearing input hashes (SHA-256):**

```
puckworks/models/brewer2026/pack_generator.py   864416314c889793684fef0a143cab48f99056b72f715adf1a522298c7d9512b
puckworks/models/brewer2026/lb_reference.py     9a60371d7777d3d91fe7df2ea529db498268f12b08ab6c461ec511190a0a989f
puckworks/models/wadsworth2026/permeability.py  8b4ecd5195d5c35ccb7d5c879cf984a7ff4389ccd61e67f38a667cb2997f9758
docs/cards/wadsworth2026.md                     606abfce68ba40105b4650ee6af2e8c716c60adb2653b87065b5fd2207c25fe8
```

## 2. Candidate-selection record

Five finalists were inspected against the real-tension, scientific-value, tractability and
decisiveness gates. **No score field, ranking, lens or generator change was introduced**, and the
90 candidates were not scored.

| finalist | why it did not win |
|---|---|
| **I-016** — does the published composition failure generalise? | **Disqualified on decisiveness.** Its rule needs ≥3 combinations on a common evidence unit. `brewer2026.coupled_kappa_t` has only **two live branches**: `compaction` and `fines` are literal `np.zeros_like(t)` structural stubs (donor params unidentified, stated in the module). Base and base+swelling are the only combinations that exist, so the candidate returns INCONCLUSIVE by construction. |
| **I-078** — does the ANALYSIS_P2 negative result generalise? | **Weak.** §2.2 is a *"partial verdict by design"*, §2.3 a *"living verdict"*, §2.4's G-lat finding is already labelled exploratory-not-proven, and a floor sensitivity is already run (*"verdict genuinely does not depend on the floor"*). Its own strongest alternative — already correctly scoped, no generalisation claimed — is true on inspection. |
| **I-080** — does the P3_hypotheses negative result generalise? | **Weak, same reason.** The P3 verdict was already **downgraded to model-capacity** (2026-07-12) and the document states it is *"NOT settled"* and not an identification. A second configuration would repeat an existing bounded claim rather than change interpretation. |
| **I-029 / I-030** — can permeability / flow discriminate the models that predict them? | **High blocker risk, low new understanding.** Both span multiple rigs, coffees and grinder dial spaces (gagne2021, grudeva2025, mo2023_2, cameron2020, fasano2000, foster2025). I-076 already died on exactly that cross-grinder blocker, and building the matched domain would be the RP-A response atlas, which is out of scope. I-030 additionally carries `de1_fixtureA`. |

**Why I-093 wins.** It is the one finalist where the matched-domain problem *cannot* arise: both
routes read the **same generated voxel geometry**, so there is no rig, coffee, grinder-dial,
pressure-node or observable-convention mismatch to bridge — the failure mode that killed I-072,
I-076 and I-090 is structurally absent. The two routes are genuinely independent (a pore-scale
lattice-Boltzmann solve of the actual voxel field versus an algebraic constitutive closure), they
produce one observable with one definition (single-phase Darcy permeability, m²), and both are
driven by the same two descriptors (porosity, grain radius) — so the comparison needs **no invented
parameter and no adapter**. Tractability is measured rather than assumed (§6). It is substantive
rather than administrative: it tests whether a continuum closure the registry relies on preserves
the trend of a first-principles solve.

## 3. Exact scientific question

> Over the geometry family `brewer2026.pack_generator` can produce, does the continuum permeability
> closure `wadsworth2026.permeability.k_percolation` reproduce the **trend** of the pore-scale
> permeability computed by `brewer2026.lb_reference`?

- **Observable**: single-phase Darcy permeability `k` [m²], defined identically on both sides —
  the coefficient in `q = −(k/μ)∇p` for creeping single-phase flow through the same porous solid.
- **Physical basis**: the pore-scale route obtains `k` by solving the flow field on the voxel
  geometry (D3Q19 TRT, Stokes regime, full-way bounce-back, periodic box). The continuum route
  evaluates an algebraic closure of `(R, φ)`.
- **Distinction under test**: whether the closure's *shape* in porosity survives, not whether its
  absolute magnitude matches.
- **Domain of the answer**: the synthetic overlapping-sphere family only, at one grain radius, over
  the porosity range where both components are declared.

**What it will explicitly NOT establish**: that the synthetic family is representative of a real
espresso puck; that either component is validated or invalidated; that the closure is right or
wrong *for coffee*; any change to any evidence rung.

## 4. Tension-reality assessment

| check | finding |
|---|---|
| independent routes? | **Yes.** LBM field solve on a voxel geometry vs an algebraic constitutive law. Not aliases, not one implementation behind two names. |
| producer/consumer? | **No.** Neither consumes the other's output. The pack generator feeds the solver; the closure is evaluated independently from the same descriptors. |
| same governing law? | **No.** One integrates a discrete-velocity Boltzmann scheme; the other evaluates `k = (2R²e^{−2αR}/(9(1−φ))) φ^{4.4}`. |
| observable definition | Identical: Darcy `k` [m²], single-phase, steady, creeping. No pressure-node, normalisation or time-basis question arises (both are steady scalars). |
| validity-range intersection | **Non-empty.** `wadsworth2026.permeability`: ⟨R⟩ **145–818 µm**, φ_p **0.37–0.67** (untamped). Scenario R = **310.8 µm**; family φ = **0.40–0.65**. `brewer2026.pack_generator`: grain radius ≥ **10 voxels** — the scenario sets exactly 10. |
| parameter/BC compatibility | Both driven by (φ, R) from the same pack. No grinder-dial translation is required or performed. |
| fit/holdout lineage | **Recorded, and it bounds interpretation.** `docs/cards/wadsworth2026.md`: the closure was *"Validated by XCT + LBflow on 2 coffees × 11 grinds (untamped)"* — i.e. it is itself LB-anchored, on **real coffee** geometry. Agreement here would therefore be partly expected; disagreement isolates geometry (spheres vs coffee) or solver. This is not independent validation of anything and is not claimed as such. |
| uncertainty basis | **Measured, not assumed** — see §6. Solver uncertainty comes from an RVE-size sweep and seed-to-seed variation, both computed in this screen. No uncertainty is imported or invented. |
| replicate misuse risk | None: there is no experimental replicate structure here. Seeds are independent geometry realisations and are labelled as such, never as experimental replicates. |

**Conclusion: the tension is real.** T-0174 is not a bookkeeping artifact.

## 5. Data and model inventory

| asset | entry point | role | units |
|---|---|---|---|
| `brewer2026.pack_generator` | `pack_generator.make_pack(L, voxel_um, gs, phis_target, seed, hetero_amp, verbose)` | geometry | boolean voxel field |
| | `pack_generator.boulder_radius_um(gs)` | grain radius | µm |
| `brewer2026.lb_reference` | `lb_reference.solve(solid, g, tau_plus, max_steps, check, rtol, min_steps)` | pore-scale `k` | lattice units (lu²) |
| | `lb_reference.channel_verification(...)` | positive control | — |
| `wadsworth2026.permeability` | `permeability.k_percolation(R, phi_p, alpha, b)` | continuum `k` | m² |
| Carman–Kozeny | evaluated in the screen module as the secondary comparator | continuum `k` | m² |

**Transformations (the only ones performed, both exact and declared):**

- voxel edge length `h = voxel_um × 1e-6` m;
- pore-scale `k_SI = k_lu × h²` — the standard lattice-to-physical conversion for a length², with
  no fitted factor;
- grain radius `R_SI = r_vox × h`, identically the `boulder_radius_um(gs)` value by construction.

`lb_reference` is the **anchor**. `lb_taichi` is not used: it is an optional accelerated backend and
an accelerator does not become its own validation.

**Evidence excluded, and why:** no manifest dataset is used. This screen compares two computational
routes on generated geometry; no measured coffee dataset enters, so none is scored, held out, or
assigned an evidence rung. `de1_fixtureA` is absent — see §10.

## 6. Frozen test

### 6a. Scenario (all values provenance-bound, none invented)

```
gs            = 1.3                    # Cameron grind setting
R             = boulder_radius_um(1.3) = 310.8 um     # inside wadsworth 145-818 um
voxel_um      = R / 10.0               # grain radius EXACTLY 10 voxels (pack admissibility >= 10)
hetero_amp    = 0.0                    # monodisperse overlapping spheres; no columnar heterogeneity
seeds         = (0, 1)                 # independent geometry realisations
phis_target   = 0.35, 0.40, 0.45, 0.50, 0.55, 0.60      # -> porosity 0.65 ... 0.40
LB            = g=1e-6, tau_plus=1.2, rtol=1e-6, min_steps=600, max_steps=20000, check=200
```

Porosity family spans φ = 0.40–0.65, inside the closure's declared φ_p 0.37–0.67.

### 6b. RVE-size sweep — runs FIRST, and can end the screen

At `phis_target = 0.50`, seed 0, `L ∈ {32, 48, 64, 80, 100}` (grain diameter d = 20 voxels, so
L/d = 1.6, 2.4, 3.2, 4.0, **5.0**). The pack card's declared box guidance is **≥ 5 grain
diameters**; L = 100 is the smallest swept size that reaches it.

**Stabilisation criterion (frozen):** the solver is stabilised at `L*` when, for every swept
`L ≥ L*`, `|k(L) − k(L_max)| / k(L_max) ≤ 0.10`, **and** the change between the two largest swept
sizes is ≤ 0.05.

**Three outcomes, distinguished before running:**

1. a stabilised `L*` exists → the family runs at `max(L*, 64)`;
2. no stabilised `L*` exists **and the sweep reached L/d ≥ 5** → *"no RVE size stabilises the
   solver"* → the candidate's **SURVIVE** arm;
3. the sweep could **not** reach L/d ≥ 5 inside the compute budget → **INCONCLUSIVE (compute
   bound)**. This is a computational limit and must never be reported as a missing-measurement
   requirement.

### 6c. Primary metric

For each family point *i*, with both sides in m²:

```
r_i = k_LB,i / k_closure,i
G   = max_i(r_i) / min_i(r_i)          # geometric spread of the ratio across the family
```

`G` measures **trend preservation**: a closure that gets the shape right but the magnitude wrong
gives `r_i` constant and `G → 1`. A closure whose porosity dependence differs gives `G ≫ 1`. This
deliberately does not penalise a pure prefactor offset, because a sphere-vs-coffee prefactor
difference is expected and is not the question.

### 6d. Uncertainty treatment (measured here, never imported)

```
U_seed = max over family of  max(k over seeds) / min(k over seeds)
U_rve  = k(L_chosen) / k(L_max)   , expressed as a factor >= 1
U      = max(U_seed, U_rve)
```

### 6e. Decision threshold (frozen)

```
trends AGREE   if  G <= max(U, 1.31)
trends DIVERGE if  G >  max(U, 1.31)
```

`1.31` is **not invented**: it is the closure's own published percolation-collapse scatter recorded
in `puckworks/models/wadsworth2026/permeability.py` (*"percolation collapse geometric-mean ratio
0.91 (x/1.31 scatter)"*). Using the closure's own declared scatter as the floor prevents declaring
divergence tighter than the closure ever claimed.

### 6f. Positive control

`lb_reference.channel_verification()` must reproduce the exact plane-Poiseuille permeability before
any pack is run. If it fails, the screen stops: the solver is not trustworthy and no comparison is
meaningful.

### 6g. Strongest adversarial alternative, and the checks against it

**The alternative** (the candidate's own): *the synthetic geometries are not representative of a
real puck, so neither curve is the reference.* This is accepted as true and is the reason the claim
ceiling is bounded to the synthetic family. It cannot be refuted by this screen and no attempt is
made to refute it.

Checks that must all be run and reported:

- **A1** — sphere-vs-coffee: stated, unrefuted, and used to bound the ceiling.
- **A2** — is any divergence merely the angularity term? Recompute with `alpha = 0` and report `G`.
- **A3** — connected vs total porosity: the LB reports total fluid fraction; the closure's `φ_p` is
  connected porosity. Recompute using both the measured pack porosity and the LB fluid fraction and
  report the sensitivity.
- **A4** — is the finding specific to the percolation form? Repeat the whole metric against
  Carman–Kozeny.
- **A5** — is `G` inside seed noise? Compare `G` against `U_seed` directly.

### 6h. Minimum figure

`figures/primary.png`: `k` versus porosity, pore-scale solver and continuum closure(s) overlaid,
with the RVE size at which the solver stabilises (or fails to) marked.

### 6i. Compute budget (frozen)

**≤ 120 minutes total CPU wall time** on `lb_reference`. Measured costs at the frozen resolution:
L=32 ≈ 18 s, L=48 ≈ 57 s, L=64 ≈ 220 s (under load). If the budget is exceeded, the screen stops
and reports the bounded result already obtained plus the exact domain/grid requirement that
exceeded it.

**This screen does not run in CI.** Heavy execution stays local per CLAUDE.md rule 3; the committed
artifacts and the focused tests over them are what CI sees.

## 7. Decision logic — the candidate's own, unrevised

Copied verbatim from the generated portfolio entry:

- **SURVIVE if** *The closure and solver trends diverge inside the geometry family, or no RVE size
  stabilises the solver.*
- **RETIRE if** *Closure and solver agree within solver uncertainty across the family.*
- **INCONCLUSIVE if** *The solver cannot be run at an RVE size large enough to stabilise.*

**Vocabulary mapping.** The generated vocabulary says `INCONCLUSIVE`; the screen-bundle convention
in `docs/insights/screens/README.md` uses `NEEDS_NEW_DATA` for a data block. These are **not the
same** here: I-093's INCONCLUSIVE is a *computational* limit, not a missing measurement. The bundle
will therefore record `INCONCLUSIVE` verbatim and state explicitly that it is a compute bound and
**not** a data request, rather than relabelling it.

Thresholds in §6e are fixed now and are not selected after observing output.

## 8. Claim ceiling

Whatever the outcome:

- it is a **cheap scientific screen**, not a publication result and not a validation-strength
  promotion;
- it speaks **only** about the synthetic overlapping-sphere family at one grain radius over the
  swept porosity range — it does **not** establish real-puck representativeness;
- it does **not** validate or invalidate `wadsworth2026.permeability`, whose own coffee-XCT
  validation is untouched, and it does **not** adjudicate that validation;
- it does **not** upgrade `brewer2026.lb_reference` beyond `code_verification` or
  `brewer2026.pack_generator` beyond `qualitative_capacity`;
- agreement would be **weak evidence** at best, because the closure is itself LB-anchored;
- divergence would show a closure/solver trend mismatch **on this family**, which is a methods
  finding about closure portability, not a claim about espresso;
- numerical convergence is distinguished from empirical validation throughout, and no result here
  is empirical validation of anything.

## 9. Stop conditions

The screen stops and reports rather than proceeding if:

- the positive control fails;
- the comparability gate fails (§6, G1–G5 in the module);
- a required parameter would have to be invented;
- the compute budget is exceeded;
- the RVE sweep cannot reach L/d ≥ 5;
- the question turns out to be already answered by an existing analysis in the repository.

## 10. Issue #231 disposition

```
issue_231_disposition: NOT_MATERIAL_TO_SELECTED_DECISION
```

`de1_fixtureA` appears nowhere in I-093's entity list, nowhere in this protocol's inputs, and
nowhere in the screen's evidence: this screen consumes **no manifest dataset at all**, so no
evidence rung — contested or otherwise — is load-bearing for its decision or its maximum claim. No
authority associated with Issue #231 is read, edited or relied upon.
