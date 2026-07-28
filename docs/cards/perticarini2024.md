# Model card: Perticarini 2024 reduced percolation (multi-species, interacting)

**Thesis:** Perticarini, A. "Predictive Models in Espresso Coffee Percolation." Ph.D. thesis, Università degli Studi di Camerino, School of Advanced Studies, Materials Sciences, XXXVI cycle. Supervisor P. Maponi, co-supervisor J. Giacomini. PDF dated Nov 2023, deposited/discussed 28 Feb 2024. No DOI. Chapter 2 §2.4 + Chapter 4 §4.1.
**Underlying publications:** the single-species model and FD scheme are Egidi/Giacomini/Maponi et al., *Comput. Appl. Math.* **41**:229 (2022) [thesis ref 55]; the **multi-species generalisation with species interaction** is Giacomini, Maponi, Perticarini, *J. Math. Chem.* (2022) [ref 21]; the RBF scheme is the registered egidi2024 [ref 84]. Physico-chemical constants trace to Cameron 2020 [ref 19] and Moroney 2015 [ref 22].
**Stage(s):** extraction · **Kind:** runtime
**Status:** card-only

## Scope and mechanism
1D saturated two-population (fines/boulders) espresso extraction, generalised to an
arbitrary number N_{l-s} of named chemical species. Liquid-phase advection–diffusion
along the bed axis is coupled, at every depth level, to spherical intra-grain diffusion
in each grain class; a nonlinear surface dissolution term moves solubles from grain to
liquid. The **new element relative to everything registered** is the reaction closure
(their Eq. 2.82): the dissolution flux of species *i* is multiplied by a product over all
other species *j* of `max(c_j^l − c_dis^{i,j}, 0)`, so species *i* cannot dissolve until
every other tracked species has exceeded its own threshold in the surrounding liquid.
Imbibition is discarded (bed fully wet at t = 0); Darcy flux q is a prescribed constant,
**fitted per grind**, not computed from pressure or permeability; temperature and pressure
never appear in the equations. Two demonstrations: N_{l-s} = 1 for EY (Modœtia + Cibao
Altura, five grind levels) and N_{l-s} = 2 for caffeine + total CQAs.

## Governing equations
Liquid phase, their Eq. (2.80), for i = 1…N_{l-s}, z ∈ (0, L), t ∈ (0, τ):
1. (1 − φ) ∂c_i^l/∂t = D ∂²c_i^l/∂z² − q ∂c_i^l/∂z + b_f G_i^f(c^l, c^f, z, t) + b_b G_i^b(c^l, c^b, z, t)
   BCs: −D ∂c_i^l/∂z(0,t) + q c_i^l(0,t) = 0 (no soluble flux at inlet);
   −D ∂c_i^l/∂z(L,t) = 0 (no diffusive flux at outlet); IC c_i^l(z,0) = 0.
   Note the advective term is written on the RHS with a minus sign, i.e. identical to
   egidi2024's Eq. (1) after transposition; no discrepancy.

Solid fractions (their §2.4, unnumbered):
2. φ = φ_f + φ_b, φ_f = b_f a_f/3, φ_b = b_b a_b/3.
   **Conflict flag:** the registered egidi2024 card records this closure as φ_s = b_s a_s³.
   Only `φ_s = b_s a_s/3` is dimensionally consistent with b_s being a BET specific surface
   per unit bed volume [m²/m³ = 1/m], which is also what makes `b_s G_s` in (1) come out as
   kg m⁻³ s⁻¹ and what makes b_s/(4π a_s²) in (5) a number density. The thesis form is the
   correct one; the egidi2024 entry should be corrected, not silently merged.

Solid phase, per grain class s = f, b at each z, their Eq. (2.81), r ∈ (0, a_s):
3. ∂c_i^s/∂t = (D_i^f/r²) ∂/∂r (r² ∂c_i^s/∂r)
   BCs: −D_i^f ∂c_i^s/∂r(0,z,t) = 0 (symmetry); −D_i^f ∂c_i^s/∂r(a_s,z,t) = G_i^s(z,t);
   IC c_i^s(r,z,0) = c_{0i}. At r = 0 the De L'Hôpital limit ∂c_i^s/∂t = 3 D_i^f ∂²c_i^s/∂r²
   is used (their Eq. 4.6). D_i^f is assumed independent of particle size.

Dissolution / coupling, their Eq. (2.82) — **the multi-species closure**:
4. G_i^s(c^l, c^s, z, t) = k_r^i · c_i^s(a_s,z,t)
     · max(c_i^s(a_s,z,t) − c_i^l(z,t), 0)
     · max(c_sat^i − c_i^l(z,t), 0)
     · ∏_{j≠i} max(c_j^l(z,t) − c_dis^{i,j}, 0),   s = f, b.
   c_sat^i saturation concentration of species i; k_r^i reaction rate; c_dis^{i,j} the
   threshold above which dissolved j influences the dissolution of i.
   *Transcription note:* the printed Eq. (2.82) has `max(c_j^l(, t) − c_dis^{i,j}, 0)` —
   the z argument is dropped; the discrete form (4.3) confirms it is `c_{j,n}^{l,k}` at the
   same node, i.e. a local, not depth-averaged, quantity.
   **Dimensional inconsistency, flagged:** with three concentration factors, G [kg m⁻² s⁻¹]
   forces k_r in m⁷ kg⁻² **s⁻¹** (the published units omit the s⁻¹; egidi2024 inherits the
   same omission). With the interaction product and I = 2 there is a *fourth* concentration
   factor, so k_r must be m¹⁰ kg⁻³ s⁻¹ — yet Table 4.9 still lists m⁷/kg² for both caffeine
   and CQAs. The multi-species rate constants therefore cannot be used as printed without
   deciding what basis they were fitted on.

Smoothed max used in both schemes, their Eq. (4.4), p > 0 small:
5. f_p(x) = exp(x/p + log p − 1) for x ≤ p;  f_p(x) = x for x > p.
   C¹ at x = p, and **strictly positive for all x**. This matters physically, not just
   numerically — see the deadlock note under Assumptions.

Mass bookkeeping, their Eqs. (2.83)–(2.88) (used for the conservation check, not required
at runtime): M^l = πR₀² ∫₀^L (1−φ) c^l dz; M^s = πR₀² ∫₀^L [b_s/(4π a_s²)] ∫₀^{a_s} 4π c^s r² dr dz;
dM^cup/dt = πR₀² q c^l|_{z=L}.

Observable, their Eqs. (2.89)–(2.90):
6. M_in = φ ρ π R₀² L;  EY = M̄^cup/M_in = q/(φ ρ L) ∫₀^τ c^l(L,t) dt
   (trapezoidal quadrature). ρ = coffee grain density — **defined in the text but never
   given a value anywhere in the thesis**, exactly the gap already flagged on egidi2024.

Symbols: c_i^l liquid concentration of species i [kg m⁻³]; c_i^s solid concentration in
class s; φ total solid volume fraction; b_f, b_b BET specific-surface parameters [1/m];
a_f, a_b fine/boulder radii; D effective liquid diffusivity; D_i^f intra-grain diffusivity;
q Darcy flux [m/s]; L bed depth; R₀ basket inner radius; τ shot time; ρ grain density.

Numerics (two schemes, both Crank–Nicolson in time with a nested fixed-point iteration,
their Algorithm 1): §4.1.1 finite differences with first-order upwind advection and a
half-step symmetric radial scheme (Eqs. 4.1, 4.5); §4.1.2 polynomial-augmented polyharmonic
(r³, m = 3) RBF collocation (Eqs. 4.16–4.24) — the latter is the registered egidi2024.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| φ (total solid fraction), I = 1 | 0.8272 | – | nominal (from Cameron 2020 [19]; **fixed across all five grinds**) |
| φ, I = 2 | 0.7 | – | nominal (changed with no justification given — see conflicts) |
| c_0 (lumped solubles) | 200 | kg/m³ | nominal (Moroney 2015 [22]; "extractable mass ≈ 30 % of the bed at 90 °C") |
| c_sat (lumped) | 212.4 | kg/m³ | nominal ([19]) |
| D (liquid) | 1.0e−8 | m²/s | nominal ([19]) |
| D^f (intra-grain, lumped) | 6.25e−10 | m²/s | nominal ([19]) |
| k_r (lumped) | 6.0e−9 | m⁷/kg² (s⁻¹ omitted) | **fitted** ("fitted to the experiments", §4.1.1) |
| k_r caffeine / CQAs | 9.6e−10 / 1.7e−9 | m⁷/kg² (units wrong for I=2) | fitted (Table 4.9) |
| D^f caffeine / CQAs | 9.0e−10 / 1.0e−10 | m²/s | fitted (Table 4.9) |
| c_sat caffeine / CQAs | 212.4 / 75.0 | kg/m³ | nominal/assumed (Table 4.9) |
| c_0 caffeine / CQAs | 16.24 / 37.17 | kg/m³ | measured (R&G HPLC assay, Table 4.4; 1 kg = 1 L assumed) |
| c_dis caffeine / CQAs | 0.5 / 0.1 | kg/m³ | fitted/assumed (Table 4.9; no provenance given) |
| a_f (I = 1) | 16.6 / 15.5 / 16.6 / 16.6 / 15.6 / 16.5 | µm | measured, PSD modes — **convention conflict, see below** (Table 4.6: EF_CA, F_M, O_M, O_CA, C_M, EC_CA) |
| a_b (I = 1) | 187.4 / 200.0 / 227.0 / 213.0 / 227.0 / 242.0 | µm | measured (Table 4.6) |
| φ_f (fraction of φ) | 0.27 / 0.24 / 0.22 / 0.22 / 0.20 / 0.17 | – | measured (Table 4.6, from PSD volume < 100 µm) |
| a_f, a_b, φ_f (I = 2) | 14.63, 227, 0.18 | µm, µm, – | measured (Table 4.10) |
| q (per grind: EF/F/O/C/EC) | 1.5 / 3.0 / 4.5 / 5.3 / 7.0 ×10⁻⁴ | m/s | **fitted** ("obtained from the model calibration", Fig. 4.4) — *not* derived from measured flow; see conflicts |
| τ (per grind) | 75 / 41 / 26 / 28 / 21 / 16 | s | measured (Table 4.6; Table 4.1 gives per-coffee means) |
| L (tamped bed height) | 12.60–14.20 (Table 4.1); 13.88 for I = 2 | mm | measured |
| basket / dose / beverage / tamp | VST Competition, R₀ = 29.25 mm, h = 26 mm, 20 ± 0.1 g → 40 ± 2 g, 20 kgF | – | measured |
| p (smoothing) | 0.1 | kg/m³ | assumed |
| ω (relaxation) | 0.8 at n = 1, else 0.1 (FD); ω_l 0.9 / ω_s 0.75 for n ≤ 15, else 0.1 (RBF) | – | assumed |
| N, M (FD grid) | 4, 5 (checked at 8, 10) | – | assumed |
| N, M^f, M^b (RBF grid) | 100, 4, 40; Chebyshev-half in z | – | assumed |
| tol₁, tol₂ / maxit | 1e−10 / 1000 (FD); 1e−7, 1e−6 / 500 (RBF) | – | assumed |
| ρ (grain density) | **not provided** | kg/m³ | — (required by Eq. 6) |

**a_s convention conflict (affects the registered egidi2024 parameters).** For Extraction
Procedure 1 the thesis states that "as representative radius for boulders and fines … we
choose the two modes" of the PSD; for Extraction Procedure 2 it states "we choose **half**
of the two modes." One of the two campaigns is off by a factor of 2 in a_f and a_b, and it
is Procedure 1 (mode-as-radius) that supplies the a_f/a_b values already registered via
egidi2024. Since intra-grain equilibration time scales as a²/D^f, a factor-2 error in a_b
is a factor-4 error in boulder timescale, partially absorbed by the fitted k_r. Do not
propagate Table 4.6/4.13 radii without resolving this.

## Calibration and validation offered by the source
**I = 1 (EY).** Six simulated extractions (Table 4.7) against the EY ranges of a 90-shot
refractometer campaign (Tables 4.2–4.3; 2 coffees × up to 5 grinds × 2 T × 2–3 p, triplicate).
Three of six land inside the measured range (O_CA 20.92 in 20.34–21.35; C_M 19.36 in
19.09–20.11; EC_CA 18.37 in 18.02–19.14); three fall below it (EF_CA 21.03 vs 21.45–21.80;
F_M 21.79 vs 22.07–22.58; O_M 19.75 vs 20.43–20.87), which the authors report as relative
underestimates of 2.0 %, 1.3 % and 3.3 %. **Every per-grind q was fitted to produce these
numbers**, and T and p do not enter the model, so the 12–18 condition structure of the data
is not predicted — only a grind-averaged EY, against ranges 0.4–1.0 pt wide.

**Scheme-dependence of the validation claim — a hard conflict with the registered
egidi2024.** Same model, same parameters, same fitted q, same three Modœtia samples:

| sample | FD scheme (this thesis, Table 4.7) | RBF scheme (egidi2024 / thesis Table 4.14) | measured range |
|---|---|---|---|
| Fine | 21.79 | 22.53 | 22.07–22.58 |
| Optimal | 19.75 | 20.44 | 20.43–20.87 |
| Coarse | 19.36 | 19.30 | 19.09–20.11 |

The two discretisations differ by up to 0.74 EY points — wider than the experimental range
for Optimal — and the "simulated EY falls inside the measured range" claim is **true for the
RBF scheme and false for two of three samples under FD**. The thesis reports this as the RBF
scheme having "improved accuracy"; read instead as an unconverged model whose apparent
validation is a property of the grid. Neither scheme is shown converged: FD varies only
(N, M) = (4,5) → (8,10) with "the same behaviour" and no numbers; RBF varies nothing here.

**I = 2 (caffeine + CQAs).** Simulated 5.78 mg/mL caffeine and 3.48 mg/mL CQAs against the
means of an 18-sample campaign (Table 4.5, 3 T × 3 p, duplicate): measured means 5.85 and
3.46 mg/mL, i.e. −1.2 % and +0.7 %. This is **two scalar targets against at least four fitted
parameters** (k_r and D^f per species, plus the two c_dis thresholds and c_sat^CQA), with the
model containing no T or p dependence at all — so it cannot in principle reproduce the 9-point
(T, p) structure of Table 4.5, and comparing to the pooled mean conceals that. Table 4.12
varies (N, M) = (3,4)/(4,5)/(5,6) with caffeine 5.64/5.78/5.85 — a 0.21 mg/mL drift, larger
than the reported error, and the "best" agreement is at the finest grid tried, so convergence
is not demonstrated. Note also c_0^CQA = 37.17 < c_sat^CQA = 75 and c_0^CF = 16.24 ≪ 212.4:
**the saturation cap is inert for both species**, so the I = 2 demonstration tests nothing
about the c_sat term.

**Mass conservation (FD only).** Table 4.8: M₀ vs M_τ agree within 3.4 % across six samples,
with acknowledged oscillation in the first time steps. Independently reproduced here:
M₀ = c_0 φ A L gives 5.78 g for O_M against the reported 5.9 g. Positivity is maintained by
ad-hoc relaxation, not proved.

## Assumptions and validity range
- Fully wet, saturated bed at t = 0; imbibition discarded. No first-drip transient.
- q constant in z and t and **fitted per grind** — no pressure, permeability, or flow-decline
  coupling; profile shots, channeling, and rising/falling flow are outside the model.
- **Independent mass-balance check on the fitted q (computed here, not in the thesis):
  q·A·τ = 30.2 / 33.1 / 31.5 / 33.9 / 29.9 / 30.1 mL for the six Table 4.7 samples, against a
  40 g beverage (plus ~8–10 g retained). The calibrated Darcy flux is therefore ~25–40 %
  below the superficial velocity the stated brew protocol requires.** q is a fitting knob for
  EY, not a physical flux, and must not be re-used as a flow-stage datum.
- No temperature and no pressure anywhere in the equations; the thesis says so explicitly
  ("temperature and pressure are not parameters of the model … their control is indirectly
  allowed by acting on the Darcy's flux").
- **Start-up degeneracy of the multi-species closure (I ≥ 2).** With exact `max(·,0)` and the
  stated IC c^l(z,0) = 0, every interaction factor `max(c_j^l − c_dis^{i,j}, 0)` is zero at
  t = 0, so G_i^s ≡ 0 for all species and **nothing ever dissolves**. The model only starts
  because the smoothing f_p leaks: with p = 0.1, f_p(−c_dis) = 2.5e−4 for caffeine
  (c_dis = 0.5) and 1.35e−2 for CQAs (c_dis = 0.1) — a 54× asymmetry between species that is
  purely an artefact of the regulariser. The early transient, the species ordering, and
  plausibly the fitted k_r all depend on p, which is never varied. This is a structural
  failure mode of Eq. (2.82), not a numerical detail.
- Two monodisperse spherical grain classes; D^f size-independent; no fines migration, no
  swelling, no consolidation, no bed evolution.
- φ fixed at 0.8272 across grinds while L varies 12.60–14.20 mm at a fixed 20 g dose — the
  implied grain density then swings 633–714 kg/m³ (computed here), and the implied EY ceiling
  M₀/M_in swings 28.0–31.6 % with grind. Internally inconsistent; comparable to but not the
  same as cameron2020's 29.6 % ceiling.
- **Porosity conflict inside the thesis:** 1 − φ = 0.173 (I = 1), 0.30 (I = 2), and ε = 0.305
  in the 3D model of the same document. Three values, no reconciliation.
- Validated only at: 20 g VST basket, 1:2 ratio, 20 kgF, τ = 14–81 s, EY 18–23 %, two Arabica
  coffees, one machine (VA388 Black Eagle) and one grinder family (Mythos 1/2). Silent on:
  gushers, chokes, lungo ratios, dose changes, T/p extrapolation, crema, clogging.

## Interface mapping
Inputs consumed: **GrindState** (fines_fraction ↔ φ_f, boulder_radius_m ↔ a_b,
mean_radius_m ↔ a_f); **BedState** (depth_m ↔ L, area_m2 ↔ πR₀², porosity ↔ 1 − φ, dose_kg
↔ M_in); **MachineState** only degenerately — P(t) is unused, and q must be supplied.
Outputs produced: **ShotResultState** (EY_pct per species via Eq. 6; c^l(L,t) → tds/traces;
with I ≥ 2, per-species cup concentrations).
Couplings: a runtime extraction component in the same slot as cameron2020.extraction_bdf.
Adapters needed: (i) BedState/MachineState → constant q, or a q(t) generalisation the model
as published does not support; (ii) a grain-density source for ρ, absent here; (iii) a
per-species inventory adapter mapping an R&G assay (g/kg) to c_{0i} (kg/m³) under the
1 kg = 1 L convention. The interaction thresholds c_dis^{i,j} are an O(I²) parameter surface
with no measurement basis — treat as a calibration layer, not physics. **Do not import the
fitted q as a flow-stage value** (see the mass-balance failure above).

## Extractable data
- **Table 4.2 → `data/perticarini2024_ey_tds_cibao.csv`** — 18 conditions for Cibao Altura
  (T × p × 5 granulometries incl. **extra fine and extra coarse, and the 12 bar points**),
  TDS mean + σ, EY, per-condition τ (14–81 s). **Highest value in the thesis and new to the
  registry**: egidi2024 holds only the Modœtia 12-condition set. This extends the registry's
  grind envelope well past the registered range in both directions.
- **Table 4.3** — the Modœtia 12-condition set; expected to be identical to egidi2024's
  Table 2. Cross-check before storing; do not duplicate.
- **Table 4.1 → same csv** — L and mean τ per granulometry per coffee (5 × 2).
- **Table 4.6 / 4.13 / 4.10** — a_f, a_b, φ_f, τ, q per sample. Store **with the factor-2 a_s
  convention flag** attached.
- **Tables 4.4 + 4.5** — R&G assay (caffeine 16.24, CQAs 37.17 g/kg) and 9-condition cup
  concentrations (mg/40 mL, mg/mL, %RSD) for Cibao Altura at 20 kgF, 88/93/98 °C ×
  7/9/11 bar. **Probable subset of khamitova2020 Tables 5.2–5.3/5.6** — same coffee, same
  grinder (Mythos 2), same machine, same (T, p) grid, and khamitova's tamping levels include
  20 kgF. Verify against the registered khamitova2020 values before transcribing; if they
  match, this is not new data.
- **Table 4.7 → `data/perticarini2024_ey_scheme_comparison.csv`** — FD-vs-RBF-vs-measured EY,
  the dual-variant record for the scheme-dependence conflict above.
- Table 4.8 (mass conservation), Table 4.12 (grid refinement, I = 2) — small, worth keeping
  as the convergence evidence the model does *not* have.
- Figures 4.1–4.3 (PSD curves, Cibao Altura ×3 grinds, Modœtia ×3, Procedure-2 grind) —
  digitisable for the grind backlog; bimodal with a minimum near 100 µm. Low priority, and
  Fig. 4.1's extra-fine/extra-coarse curves are the only ones not already available via
  egidi2024/angeloni2023.
- Figures 4.5, 4.9–4.11 (c^l, c^f, c^b traces at z = L/2) — simulation output, not data.
- Availability: no repository, no code (MATLAB, described only), no raw per-shot values —
  all tables are condition means. Transcription from the thesis is the only route.

## Overlaps and conflicts
- **egidi2024 (registered card; same model, same group) — this supersedes it as the reference
  card for the model family.** egidi2024 is the I = 1 RBF special case of exactly these
  equations. Three corrections this thesis forces on that card, none of which may be merged
  silently: (i) φ_s = b_s a_s/3, not b_s a_s³; (ii) q is **fitted**, not "derived from lab
  flow" — the thesis states it comes from model calibration, and the mass-balance check above
  confirms it is 25–40 % below the physical superficial velocity; (iii) the "simulated EY
  falls in the measured range" claim is discretisation-dependent (FD misses two of three).
- **cameron2020.extraction_bdf (competes; does not supersede).** Same stage. Cameron: lumped
  species, per-bed-volume inventory, 29.6 % ceiling, mechanistic deficit law, flux table.
  This: per-grain-volume inventory with a grind-dependent 28.0–31.6 % ceiling, quadratic-in-
  surface kinetics, prescribed fitted q, and now an optional multi-species interaction term.
  Lower coupling fidelity — no reason to swap runtimes. Note c_sat = 212.4 and c_0 = 200 here
  both descend from Cameron/Moroney, so the two components are *not* independent priors.
- **angeloni2023 (complements).** That card holds the 3D FeFlow multi-species model and the
  66-shot per-species campaign; this is the **composable 1D alternative** for the same
  backlog item, with a different dissolution closure (deficit + cap + interaction product vs
  first-order-in-solid with a fitted α(T,p)). The two closures make *different* predictions
  about species ordering and early transients, which is a usable discriminating test — see
  Implementation estimate. angeloni2023's per-species data is the right gate for this model.
- **Open backlog "extraction: multi-class solute chemistry" — direct hit, model side.** The
  backlog note on egidi2024 flagged "Giacomini 2022, J Math Chem" as the intake candidate for
  this slot; that work is §4.1.1's I = 2 case, and this card is it. It is the only 1D,
  stage-composable multi-species extraction model the registry has seen.
- **khamitova2020 (probable data overlap).** See Extractable data — Tables 4.4/4.5 are very
  likely the 20 kgF slice of khamitova's 36-condition Cibao Altura campaign.
- **foster2025.infiltration (conflicts).** This model assumes away exactly what Foster models;
  the infiltration↔extraction coupling backlog item would supersede the t = 0 wet-bed IC.
- **wadsworth2026.permeability / flow backlog (no conflict, one negative result).** The model
  sidesteps permeability entirely. The fitted q(φ_f) ladder of Fig. 4.4 looks superficially
  like a k(grind) calibration but is not one — it fails mass balance and was tuned on EY.
- **brewer2026.streamtube (no interaction).** 1D homogeneous; no heterogeneity atom.
- **Backlog "unsaturated flow at fine grinds / the EY dip" — a relevant negative datum.** The
  Cibao Altura extra-fine points (τ = 73–81 s, the finest grind in the registry at a 20 g VST
  dose) give EY 21.45–21.80 %, i.e. **flat against, not below, the fine grind's 20.43–21.86 %**.
  At this dose and basket, no EY dip appears down to 81 s shots. Worth carrying as evidence
  against a universal fine-grind dip, with the caveat that these are refractometer means at a
  fixed 1:2 ratio.

## Implementation estimate
Runtime port: **M** — 1D FD or RBF discretisation, nested fixed-point with relaxation, plus
adapters for q and ρ. But at I = 1 it duplicates cameron2020 at lower coupling fidelity, so
the case for implementing rests entirely on the multi-species closure. Before any port, two
cheap discriminating computations are needed, both of which the thesis's own numbers make
possible:
1. **p-sensitivity of the I ≥ 2 start-up.** Re-run the caffeine/CQA case at p = 0.1, 0.01,
   0.001 with c_dis as published. If the cup concentrations move materially, Eq. (2.82) is
   regulariser-dependent and the interaction term should be replaced (e.g. with a smooth
   Hill/saturating coupling) rather than implemented as written. This is the gate.
2. **Independent gate against angeloni2023.** Fit nothing; take c_{0i} from angeloni2023
   Table 7, q from a flow-stage component rather than from Fig. 4.4, and check whether
   per-species cup amounts land inside the angeloni2023 Table 4/5 ranges at matched
   (T, p, grind). The model has no T/p dependence, so the honest expectation is that it
   reproduces the grind axis and fails the T and p axes — that failure is the informative
   result and should be recorded, not fitted away.
Data intake alone: **S** (Tables 4.1, 4.2, 4.6, 4.7, plus the khamitova cross-check).

VERDICT: implement-later — the I = 1 case duplicates the registered egidi2024/cameron2020 at lower fidelity with a fitted q that fails an independent mass balance by 25–40 %, but the multi-species interaction closure (Eq. 2.82) is the only stage-composable multi-class extraction model the registry has and lands squarely on that backlog; gate on the p-sensitivity of its t = 0 start-up degeneracy before porting, and transcribe Table 4.2 now regardless — effort M
