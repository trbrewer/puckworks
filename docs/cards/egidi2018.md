# Model card: Egidi 2018 Richards equation (fixed-point FD scheme)

**Paper:** Egidi, Gioia, Maponi, Spadoni, "A numerical solution of Richards equation: a simple method adaptable in parallel computing," Int. J. Computer Mathematics (2018). DOI 10.1080/00207160.2018.1444160
**Stage(s):** infiltration · **Kind:** runtime (if ever adopted; see mapping)
**Status:** card-only

## Scope and mechanism
3D variably-saturated water flow in soil: Richards equation (Darcy + mass
conservation) with van Genuchten–Mualem closures for water retention θ(ψ) and
hydraulic conductivity K(ψ). The paper's contribution is not physics but
numerics: "Procedure 1," a central-difference FD discretization with
Crank–Nicolson stepping and a linear-system-free fixed-point iteration,
chosen for trivially parallelizable structure (OpenMP), benchmarked against
Picard/multifrontal, Picard/PCG (MODFLOW-VSF), and a FEFLOW Galerkin FEM.
Application domain is gravity-and-capillarity-driven infiltration into soil
(rainfall, landslide hazard via infinite-slope safety factor) — not
pressure-driven flow. Same first author as the registered-adjacent
egidi2024.md, but an unrelated lineage: no coffee content anywhere.

## Governing equations
Richards equation, their Eq. (5), mixed head form, h = ψ + z (Eq. 4):
1. [C(ψ) + Ss·θ(ψ)/n] ∂h/∂t = ∂/∂x[K(ψ)∂h/∂x] + ∂/∂y[K(ψ)∂h/∂y]
   + ∂/∂z[K(ψ)∂h/∂z] + W − ET
   C(ψ) = dθ/dψ specific capillary capacity [1/m]; Ss storage coefficient;
   n porosity (Eq. 3); W recharge (precipitation); ET evapotranspiration;
   h hydraulic head [m], ψ pressure head [m], z elevation [m].

Van Genuchten retention, their Eq. (6):
2. (θ − θr)/(θs − θr) = [1/(1 + |αψ|^n)]^m for ψ < 0; = 1 for ψ ≥ 0,
   with m = 1 − 1/n (Eq. 7). θr, θs residual/saturated water content; α [1/m]
   inverse air-entry head; n, m empirical shape parameters. NOTE: the printed
   Eq. (6) renders as (1 + |αψ|)^n — the standard VG form (1 + |αψ|^n) is
   intended (consistent with their ref [41]); flagged as a typesetting error.

Mualem conductivity, their Eqs. (8)–(9):
3. K(θ) = Ks·Se^(1/2)·[1 − (1 − Se^(1/m))^m]², Se = (θ − θr)/(θs − θr).
   Their ψ-form Eq. (9) prints the prefactor as [1 − (αψ)^n]^(−m/2), which is
   ill-defined for ψ < 0 with non-integer n; it should be [1 + |αψ|^n]^(−m/2).
   Flagged as a sign/absolute-value typo; Eq. (8) is the safe form.

Numerical scheme (their Eqs. 10, 14–17): θ-method time stepping
h^{n+1} = h^n + Δt[(1−λ)F(h^n) + λF(h^{n+1})], λ = 1/2, with fixed-point
iteration h^{n+1,r} = h^n + Δt[(1−λ)F(h^n) + λF(h^{n+1,r−1})], stopping on
‖h^{n+1,r} − h^{n+1,r−1}‖∞ < toll, explicit-Euler initial guess. No linear
solve per iteration — this is the entire method.

Safety-factor application (their Eq. 18, infinite slope model): irrelevant to
puckworks; not transcribed.

## Parameters
All parameters are soil-typology values (their Table 1), not coffee:
| symbol | value | units | source |
|---|---|---|---|
| θr, θs, α, n, Ks | tabulated for 12 soil classes (clay → gravel); e.g. SAND: θr 0.05, θs 0.39, α 3.36 /m, n 2.11, Ks 5.83e−5 m/s | mixed | nominal (literature compilations, their refs [16,24,36,37]) |
| Ss | not provided | 1/m | — (appears in Eq. 5, never valued) |
| Δt | 15 min (÷1000 for coarse sand/gravel) | s | assumed |
| toll | not provided | m | — |
| Coffee-bed VG parameters (θr, θs, α, n) | not provided | — | do not exist in this paper or, to our knowledge, anywhere |

## Calibration and validation offered by the source
No validation against measured moisture data at all. The paper compares
Procedure 1's solution to the *other three numerical procedures* on the same
synthetic problem (Table 2, relative 2-norm at end of a 10-day infiltration):
agreement 1e−4–1e−2 for most soils, but RE ≈ 0.54–0.61 for coarse sand, and
outright convergence failure ("breaks down") on the gravel-dominated Bulgarian
test area. Landslide case studies (Italian/Greek/Bulgarian areas) report only
inter-procedure consistency (RE 0.0017–0.00285) and CPU timings; the March
2015 Esino landslide is a motivating narrative, not a quantitative hindcast
gate — no predicted-vs-observed failure comparison is given. This is
verification (code vs code), not validation, and the authors' own results show
the scheme fails precisely where the constitutive nonlinearity is strong
(high Ks, high n).

## Assumptions and validity range
- Gravity/capillarity-driven regime: heads of order metres, K ≤ 5e−3 m/s,
  timescales of days. Espresso is pressure-driven (9 bar ≈ 90 m head across
  ~13 mm) with first-drip in seconds — entirely outside the tested envelope.
- Rigid matrix: no swelling, compaction, or porosity evolution; no solute
  transport; isothermal.
- VG closure assumed valid; parameters per soil texture class, spatially
  uniform per cell.
- Documented failure mode: the fixed-point linearization diverges for highly
  nonlinear media (coarse sand, gravel; Δt must shrink ×1000 or it breaks).
  Under espresso pressure gradients the effective nonlinearity is far harsher,
  so the one thing the paper contributes (the cheap iteration) is the part
  least likely to survive transfer.
- Silent on: hysteresis in θ(ψ), air-phase dynamics/trapped air (relevant to
  the fine-grind incomplete-wetting hypothesis), non-Darcy corrections.

## Interface mapping
If a Richards-based unsaturated-flow component were ever built, it would sit
at infiltration (competing for foster2025.infiltration's slot), consuming
BedState (depth_m, porosity, k_m2 → Ks via μ,ρg adapter) and MachineState
(P(t) → Dirichlet head BC, needing a bar-to-head adapter), producing a
saturation field S(z,t) and front-passage times for the
infiltration↔extraction coupling backlog. But the binding gap is
constitutive, not numerical: coffee θ(ψ)/K(ψ) curves are unmeasured, so any
such component is blocked on data this paper does not have. Nothing here is
usable as a calibration provider either — Table 1 is soils.

## Extractable data
- Table 1 (VG parameters, 12 soil classes): standard literature compilation,
  reproducible from their refs [16,24,36,37]; no coffee relevance — not worth
  transcribing into puckworks/data/.
- Tables 2, 4 (inter-code RE, CPU timings): numerics bookkeeping, no physical
  content.
- Code: not published (FORTRAN + OpenMP described; MODFLOW-VSF and FEFLOW are
  third-party).

## Overlaps and conflicts
- **foster2025.infiltration (competes, loses):** Foster's sharp-front model is
  espresso-specific, parameter-free, and gated against observed first-drip;
  Richards would be the higher-fidelity generalization *if* coffee retention
  curves existed, which they don't. This paper adds no path to them.
- **Backlog "unsaturated flow at fine grinds":** Richards + VG is the natural
  framework for the incomplete-wetting hypothesis (tubes at k→0), so the
  *equation class* is on target — but the useful intake for that slot is a
  paper measuring coffee water-retention/wettability, not a soil numerics
  paper. (Distinct from the Grudeva/Foster "unsaturated" solute-saturation
  sense; no conflation.)
- **egidi2024.md (unrelated):** same author, different model lineage; no
  shared equations or data.
- **brewer2026.lb_reference / lb_taichi:** no overlap; those are saturated
  single-phase verification tools.

## Implementation estimate
Adopting Richards for puckworks would be L regardless of source (constitutive
measurement campaign + pressure-driven BC + stiff nonlinear solve at 90 m
head), and this paper's specific numerical scheme is contraindicated by its
own divergence in strongly nonlinear media. Card retained as a framework
pointer for the unsaturated-flow backlog only.

VERDICT: skip — a soil-hydrology numerics paper with code-vs-code verification only, no coffee-relevant constitutive data, and a linearization scheme that fails exactly in the strong-nonlinearity regime an espresso application would occupy — effort L
