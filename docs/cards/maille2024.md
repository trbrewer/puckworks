# Model card: Maille 2024 two-regime batch extraction kinetics

**Paper/thesis:** Maille, M.J. "Measuring Coffee Extraction Kinetics at Early Time Scales."
PhD thesis, Dept. of Chemical and Biological Engineering, University of Sheffield, May 2024
(supervisor J.D. Litster; sponsor Keurig Dr Pepper Inc.). No DOI in the document; expect
White Rose eTheses Online. **Source used here is the REDACTED release**
(`..._Final_012825_Redacted_V1.pdf`, 225 pp.) — the proprietary-treatment material
(§3.2.5, §5.4, §5.5, Tables 5.5/5.6/5.8/5.12–5.18, Table 6.6, Figs. 5.9–5.11, 5.16–5.17,
6.3–6.5, 6.9–6.12, 6.16–6.17, and most of §6.2.3) is blanked. Every gap noted below is a
redaction artifact, not an omission by the author.
**Stage(s):** extraction, grind (the φ closure is a PSD→fast-fraction map) · **Kind:** calibration
**Status:** data-intaken (tables, 2026-07-25) — 14 thesis tables digitized (Tim drop, incl. the
unredacted 5.6/5.9) → `puckworks/data/maille2024/` + PROVENANCE + 11 loaders + 10 MANIFEST rows +
README ref; three discriminating computations landed in `puckworks/analysis/maille2024.py`
(CI-tested): **the Eq-6.9 shell-depth (E1) is RESOLVED to two cell layers** (two-layer reproduces
Table 6.3 θ_v,coarse to mean |err| 0.018 vs 0.207 one-layer, D[4,3] approximation), the **φ closure
is internally consistent** (φ = fines + coarse exactly; θ_v,fines tracks the Table-5.4 <186 µm
fraction to 0.003), and the **two E5 impossible-CI rows are flagged** (ΩT/3-CQA, ΩL/quinic).
The extraction **figures** (Figs 4.6–4.10, material ΩA) and **Cameron's Fig-2 PSD** were then
digitized (Tim drop) — unblocking the last two computations: the **two-regime Eq-6.2 reproduction**
(tabulated φ/λ reproduce the digitized ΩA curves to MAPE 4–10%, ≈ the model's own MPE) and the
headline **φ-split-vs-Cameron** gate — maille's φ closure on Cameron's binned PSD gives φ ≈ 0.85–0.94
(an extrapolation above maille's own 0.36–0.65) and **both** maille's φ and Cameron's fitted fines
fraction **decrease as grind coarsens (sign agreement)**, but they differ ~5–9× because maille's
"fast" (fines < 186 µm + coarse-particle shells) and Cameron's "fast" (the 12 µm fines class) are
**not commensurable** — a registry-surfaced observable-semantics disagreement, not a validation of
either. **Nothing further owed on the card**; **gate 4** (cross-model timescale portability) has since landed
in full as a **qualitative** non-portability probe — **both** halves. `cross_model_timescale_cameron()`:
no fitted λ_fast enters maille's fast band; cameron's model-generated curve is single-exponential-like
in 3 of 4 settings (the coarsest returns two separated constants, left to model selection).
`cross_model_timescale_roman()`: on Roman's genuine well-mixed stirred vessel the fit has a universal
*dimensionless* shape (weight φ ≈ 0.32, ratio ≈ 12.3 grind-invariant; absolute constants vary with
diffusivity) — one physical-diffusion-process signature, not maille's two-*pool* split — at
sub-maille timescales for the *selected 20 µm fine class* (coarse class not evaluated). The conclusion
is **semantic**: a shared bi-exponential form is not a shared construct; maille's decomposition ports
to **neither** under the tested mappings. (The roman half is a research computation; the product #100
rights deferral gates only the public Laboratory product lens, not internal validation.) See gate 4 below.

## Scope and mechanism
Time-resolved extraction kinetics of five identified solutes — caffeine, chlorogenic acid
(3-CQA), citric acid, malic acid, quinic acid — from roast-and-ground coffee in a stirred,
dilute, atmospheric **well-mixed batch reactor** (WMBR), sampled at 1.88 s intervals so that
~80 % of each curve lies under 35 s. The measurement method is the thesis's primary
contribution: an air-over-water pump draws a continuous extract stream that a rotary sample
splitter fractionates into 16 early aliquots (plus 60/180/300/600 s points), giving a dozen-plus
points below 30 s where prior work had one or two. The data show two distinct regimes — a rapid
"washing" phase from fines and coarse-particle surfaces, then a slow diffusion-limited phase —
and are fitted with a sum of two first-order exponentials weighted by φ, the fraction of solute
inventory available to the fast regime. φ is **not fitted**: it is predicted a priori from the
measured particle size distribution as (fines volume fraction below 186 µm) + (a two-coffee-cell
outer shell on every coarse particle), leaving a two-parameter regression in the time constants
λ_fast and λ_slow. There is no bed, no pressure, no flow, and no EY/TDS anywhere in the work.

## Governing equations

**Extraction model.** Two-regime empirical form (Eqn 6.1), and the delay-shifted form actually
used for caffeine and 3-CQA (Eqn 6.2):

- (6.1) C_t/C_∞ = φ(1 − e^(−t/λ₁)) + (1 − φ)(1 − e^(−t/λ₂))
- (6.2) C_t/C_∞ = φ(1 − e^(−(t−τ)/λ₁)) + (1 − φ)(1 − e^(−(t−τ)/λ₂))

**φ closure, predicted from PSD** (Eqns 6.7–6.9). The Malvern Mastersizer's native 100-bin
scale is assumed throughout; bin 75 has a mean diameter of ≈186 µm and is the fines/coarse cut:

- (6.7) φ = θ_v,fines + ϑ_v,coarse
- (6.8) θ_v,fines = Σ_{i=1..75} v_i,liquid
- (6.9) ϑ_v,coarse = Σ_{i=76..100} v_i,air · (1 − ((x̄_i − 2d_c)³ / x̄_i³))

**Hybrid PSD construction** (Eqns 5.1–5.3), spliced from the liquid-dispersion measurement
below 186 µm and the air-dispersion measurement above:

- (5.1) θ_hybrid,j = Σ_{i=1..j} v_i,liquid for j ≤ 75;
  = θ_fines(liquid) + Σ_{i=76..j} v_i,air(1 − θ_fines(liquid)) for 76 ≤ j < 100;
  = θ_fines(liquid) + θ_coarse(air) = 1 for j = 100
- (5.2) θ_fines(liquid) = Σ_{i=1..75} v_i,liquid
- (5.3) θ_coarse(air) = Σ_{i=76..100} v_i,air (1 − θ_fines(liquid))

**Supporting estimates** (used to justify assumptions, not to produce outputs):

- (6.3) h = √( γ_lv R_pore cos(θ_d) / (2 μ_f) · t )  — Lucas–Washburn hydration-time check
- (6.4) Bi_m = k R_p / D_eff   (6.5) k = D_soln / δ   (6.6) Fo_m = D_eff t / R_p²
  — used to set the 186 µm fines threshold
- (5.4) SSA = 6 / (ρ_s D[3,2]_dry) — theoretical specific surface area for spheres
- (4.1) τ_p = (ρ_t − ρ_f) d_p² / (18 μ_f) — particle relaxation time, justifying stir-speed
  independence
- (2.2) ln(C_∞/(C_∞ − C)) = k_obs t + a — the Spiro & Selwood (1984) long-time first-order
  approximation, retained here only as the **null model that fails**: the semi-log data break
  into two straight segments rather than one (Fig. 4.12), and that break defines φ

**Symbols.** C_t concentration at time t (kg L⁻¹); C_∞ bulk concentration at infinite time,
operationally the maximum observed value at 300 or 600 s; φ fraction of total extractable
concentration released in the rapid regime (–); λ₁ ≡ λ_fast, λ₂ ≡ λ_slow time constants of the
rapid and slow regimes (s); τ observed extraction delay time (s); θ_v,fines total volume
fraction of particles below 186 µm (–); ϑ_v,coarse volume fraction of coarse-particle surface
shell contributing to fast extraction (–); v_i,liquid, v_i,air class-bin volume fractions from
liquid- and air-dispersion laser diffraction (–); x̄_i arithmetic mean of the upper and lower
diameters of bin i (m); d_c coffee cell diameter (m); θ_hybrid,j cumulative volume fraction of
the hybrid PSD (–); h capillary penetration distance (m); γ_lv liquid surface tension (N m⁻¹);
R_pore effective capillary pore radius (m); θ_d dynamic contact angle (°); μ_f fluid viscosity
(Pa s — see erratum E4); Bi_m mass-transfer Biot number (–); Fo_m mass-transfer Fourier number
(–); k mass-transfer coefficient (m s⁻¹); D_soln bulk-solution diffusivity (m² s⁻¹); D_eff
effective intraparticle diffusivity (m² s⁻¹); δ boundary-layer thickness (m); R_p particle
radius (m); SSA specific surface area (m² kg⁻¹); ρ_s particle density (kg m⁻³); D[3,2]_dry
Sauter mean diameter, air dispersion (m); τ_p particle relaxation time (s); ρ_t true density,
ρ_f fluid density (kg m⁻³); d_p particle diameter (m); k_obs observed mass-transfer rate
constant (s⁻¹); a dimensionless intercept.

**Errata and internal inconsistencies — flagged, not corrected:**

- **E1 (material).** Eqn 6.9 as printed subtracts 2d_c from x̄_i where x̄_i is a **diameter**,
  i.e. it removes **one** cell layer of depth (d_c per side). The surrounding text states the
  intent explicitly — "the volume fraction of the first **two** layers in each sphere," citing
  Fiori et al. (2009)'s double-shell result. The published Table 6.3 values follow the *intent*,
  not the printed equation: evaluating the shell kernel at each material's air-dispersion D[4,3]
  gives mean |error| vs Table 6.3 of **0.028 for a two-layer depth (4d_c off the diameter)**
  versus **0.194 for the printed one-layer form**. Implement the two-layer depth; record the
  printed form as a typo. This matters — it roughly doubles φ.
- **E2.** Table 6.1's hydration times cannot be reproduced from its own printed inputs. With the
  tabulated values, Eqn 6.3 gives 9.02 s for the ΩA radius (7.7×10⁻⁴ m) and 1.80 s for the ΩJ
  radius (3.44×10⁻⁴ m); the text reports 1.78 s for ΩA and 0.79 s for ΩJ — i.e. the reproducible
  number is attached to the wrong material, and the two reported times scale as h¹ rather than
  the h² required by Eqn 6.3.
- **E3.** γ_lv = 6.082×10⁻³ N m⁻¹ (Table 6.1) is an order of magnitude low for water; the value
  at ~90 °C is 6.082×10⁻² N m⁻¹ — an exponent typo in an otherwise correctly sourced number.
- **E4.** μ_f = 9.0×10⁻⁵ Pa s (Table 6.1) is ~3.5× below water at 90 °C (≈3.15×10⁻⁴ Pa s); §4.2.4
  also calls μ_f "kinematic viscosity" while the variable list and Eqn 4.1's dimensions require
  dynamic. With correct water properties Eqn 6.3 gives ≈3.2 s for ΩA — see assumption A2 below.
- **E5.** Table 6.4, ΩT / 3-CQA: λ_fast = 12.2 s with an upper 95 % CI of 11.9 s (below the
  estimate). Table 6.5, ΩL / quinic: λ_slow = 44 s with lower CI 65 and upper 54. Both rows are
  internally impossible; treat those CIs as unusable.
- **E6.** Bi_m and Fo_m reproduce exactly from Table 6.2 (3.00 and 1.42 vs "≈3" and "1.4") — no
  issue, recorded as a positive check that the 186 µm threshold is traceable.

## Parameters

Model parameters are per-material, per-compound; the tables below give the ranges and the
fixed constants. Full per-material values are the transcription targets listed later.

| symbol | value | units | source |
|---|---|---|---|
| λ_fast (caffeine) | 2.9 – 19.1 (17 materials) | s | fitted |
| λ_slow (caffeine) | 27 – 109 | s | fitted |
| λ_fast (3-CQA) | 3.7 – 18.3; mean 9.8 | s | fitted |
| λ_slow (3-CQA) | 35 – 158 | s | fitted |
| λ_fast (citric) | 2.7 – 10.0; 3.0 (ΩA/E/H/K cohort), 6.7 (others) | s | fitted |
| λ_slow (citric) | 20 – 65 | s | fitted |
| λ_fast (malic) | 2.2 – 9.8 | s | fitted |
| λ_slow (malic) | 13 – 44 | s | fitted |
| λ_fast (quinic) | 5.3 – 14.7 | s | fitted |
| λ_slow (quinic) | 18 – 90 | s | fitted |
| φ | 0.356 – 0.648 (17 materials, Table 6.3) | – | derived from measured PSD |
| θ_v,fines | 0.025 – 0.154 | – | measured (liquid-dispersion PSD) |
| ϑ_v,coarse | 0.332 – 0.568 | – | derived from measured PSD |
| τ | **not provided** — no table anywhere; text gives ~4 s (caffeine), ~3 s (3-CQA) by visual inspection, 0 for the three acids | s | not reported |
| d_c (coffee cell diameter) | 45 | µm | assumed (SEM range 20–60 µm, §5.2.2) |
| fines/coarse threshold | 186 (Malvern bin 75) | µm | derived (Bi_m ≈ 3, Fo_m ≈ 1.4) |
| D_soln | 2.3×10⁻⁹ | m² s⁻¹ | nominal (Spiro et al. 1989) |
| D_eff | 7.67×10⁻¹⁰ | m² s⁻¹ | nominal (estimated from Roman-Corrochano 2017) |
| δ | 9.0×10⁻⁵ (set equal to R_p) | m | assumed |
| R_p (for Bi/Fo estimate) | 9.0×10⁻⁵ | m | assumed |
| t (transition point, for Fo) | 15 | s | measured (observed transition) |
| θ_d | 80 | ° | estimated (from Roman-Corrochano 2017) |
| R_pore | 1.12×10⁻⁸ | m | nominal (plasmodesmata, Schenker et al. 2000) |
| γ_lv | 6.082×10⁻³ (see E3) | N m⁻¹ | nominal (Vargaftik et al. 1983) |
| μ_f | 9.0×10⁻⁵ (see E4) | Pa s | nominal (Kestin et al. 1978) |
| brew temperature | 91.5 ± 1 (water preheated to 95, hotplate 100) | °C | measured |
| coffee : water | 100 ± 0.5 g : 3625 ± 50 mL = 0.028 | g mL⁻¹ | measured |
| headspace pressure | 7–30 (10 ± 1 operating) | kPa | measured (sampling pump only) |
| aliquot interval / volume | 1.88 / 35 ± 5 | s / mL | measured |
| sampling | 16 splitter aliquots + 60, 180, 300, 600 s | s | measured |
| filter screen cut | 40 (100 + 400 US mesh) | µm | nominal |
| light roast | 225 °C end, 9:50, 13.8 ± 0.6 % loss, Agtron 42.5 ± 1.2 | — | measured |
| dark roast | 235 °C end, 11:15, 17.3 ± 0.3 % loss, Agtron 27.9 ± 0.5 | — | measured |
| green coffee | single 70 kg lot, washed, Antioquia Colombia, 1600–2200 m, 7.7 % Mw | — | measured |
| grinder | Mahlkönig VTA-6-SW, setting 9; RoTap sieved (16/18/25/30 mesh) | — | nominal |
| sieve classes | 1180–1000, 1000–710, 710–600 µm; plus 5 full-PSD materials | µm | nominal |
| D[4,3] hybrid (all materials) | 537 – 1540 | µm | measured (Table 5.4) |
| D[3,2] hybrid | 44 – 460 | µm | measured (Table 5.4) |
| vol. fraction < 186 µm (hybrid) | 0.02 – 0.34 | – | measured (Table 5.4) |
| SSA (measured, Kr adsorption) | 61 (ΩA), 82 (ΩB), 98 (ΩC), 85 (ΩD), 116 (ΩV); text cites a 60–185 range across all materials | cm² g⁻¹ | measured (Table 5.7 survives; Table 5.6 redacted) |
| particle porosity ε_p | 0.447 (ΩA), 0.442 (ΩB), 0.501 (ΩC); whole bean 0.443 light / 0.568 dark | – | measured (Hg intrusion, Table 5.9, partial) |
| ε_closed / ε_open | 0.176/0.271 (ΩA), 0.162/0.279 (ΩB), 0.176/0.325 (ΩC) | – | derived (Hg + He) |
| corrected envelope density | 0.702, 0.709, 0.634 (ΩA–ΩC); 0.708 / 0.549 whole bean light / dark | g cm⁻³ | measured |
| particle density (Hg) | 0.78, 0.81, 0.83 (ΩA–ΩC) | g cm⁻³ | measured |
| particle density (He, micro-ground ΩW/ΩX) | 1.27 | g cm⁻³ | measured |
| whole-bean mesopore mode | 23 (light), 32 (dark) | nm | measured |
| loose bulk density, all materials | **not available** (Table 5.5 redacted) | kg m⁻³ | — |

## Calibration and validation offered by the source

**What is fitted.** λ_fast and λ_slow, by nonlinear regression, independently for each of ~79
material × compound combinations (17 materials × caffeine and 3-CQA; 16 × three acids, minus
three unreported quinic fits). φ is fixed in advance from the PSD; τ is applied to caffeine and
3-CQA but its values are never tabulated.

**Fit quality.** R² 0.85–0.99 for caffeine and 3-CQA; 0.47–0.98 for the organic acids, with the
weak tail concentrated in quinic acid (ΩU 0.47, ΩP 0.70, ΩB 0.76) and malic ΩF (0.61). Mean
percent error averages 6 % (3-CQA) and 4 % (citric), spanning 2.3–16.8 % overall; the worst rows
are caffeine ΩB (16.0 %) and quinic ΩB (16.8 %). This is in-sample fit quality on two free
parameters, not prediction.

**The one genuinely predictive claim** is φ. The PSD-derived value was overlaid on the semi-log
transition point of each data set: "in a majority of the cases, the predicted value is well
within 5 % of the actual value," with an example at ~10 % (ΩA, Fig. 6.7). This is a real,
parameter-free structural prediction and it is the most valuable thing in the chapter — but it is
assessed **graphically, per material, with no aggregate error statistic**, so it cannot be scored
from the document.

**Structural consistency checks the author reports.** λ_fast should be independent of particle
structure (it describes fines and surfaces): borne out for 3-CQA (mean 9.8 s, no trend against
D[4,3] or SSA). For citric acid the claim required splitting the materials into two cohorts post
hoc — ΩA/ΩE/ΩH/ΩK averaging 3.0 s versus 6.7 s for the rest — which is a regrouping after seeing
the residuals and should be read as weak. λ_slow should track structure: it does, falling >60 %
(3-CQA) and >50 % (citric) as D[4,3] drops 1550→~700 µm and SSA rises 60→185 cm² g⁻¹.

**Measurement reproducibility (strong, and the thesis's real asset).** For ΩA, replicates 1 and 2
were time-aligned to within thousandths of a second; malic acid concentrations agree within 0.01
normalized units in 9 of 16 early clusters, with the worst caffeine spread 0.10 at ~15 s. Stir
speed had no measurable effect (Fig. 4.3), consistent with τ_p = O(0.05 s) and with Spiro & Page
(1984). Equilibrium: the 300 s and 600 s points differ by ≤5 % on average, supporting C_∞ at 600 s.

**External plausibility, not validation.** Table 4.4 normalizes to 100 g L⁻¹ and places the WMBR
at 1255 mg L⁻¹ caffeine / 595 mg L⁻¹ 3-CQA at 180 s against literature pour-over and French-press
values of 970–1430 and 460–852. Different method, bean, and temperature — an order-of-magnitude
sanity check only.

**Weaknesses the author states plainly, and which should not be softened.** The 95 % confidence
bands are too narrow because PSD measurement error is not propagated into the fixed φ — several
data points fall outside them, and the author attributes this and a slight citric-acid
overestimate to exactly that. λ_fast and λ_slow carry a correlation of estimates averaging
0.40–0.60, so they are not independently identified. No held-out material, no cross-validation,
no second coffee origin, no second temperature.

## Assumptions and validity range

The author's five stated model assumptions, with the registry's reading:

- **A1. Spherical particles.** Contradicted by the thesis's own Table 5.3: measured aspect ratios
  1.02–1.85. Enters both Eqn 6.9's shell geometry and Eqn 5.4's SSA.
- **A2. Hydration is instantaneous; all particles saturate simultaneously.** Justified via Eqn 6.3,
  but see E2–E4: with correct water properties the same equation returns ≈3.2 s for the largest
  particles — the same order as the 3–4 s delay τ that the model introduces as a *separate*
  parameter, and the same order as foster2025.infiltration's front-passage times. The claim
  "hydration is smaller than the ability to measure any coffee extraction" does not survive the
  corrected numbers. **This is the assumption most likely to be doing hidden work in τ.**
- **A3. Dilute bulk (partition coefficient assumed = 1).** Deliberately engineered: 0.028 g mL⁻¹
  in a 4 L vessel. Valid here; explicitly *not* valid for espresso, where the liquid approaches
  saturation.
- **A4. Complete extraction, no re-adsorption.** No solute inventory or saturation ceiling exists
  anywhere in the model — C_∞ is measured, never predicted.
- **A5. Constant, averaged effective diffusivity; no time or position dependence.** This is what
  licenses a sharp two-regime split; it also means all treatment effects are absorbed into λ_slow
  by construction.

Regime boundaries and silences:

- **Batch, stirred, atmospheric.** No bed, no packing, no pressure gradient, no flow, no
  permeability, no channeling. Nothing in this thesis bears on the flow, packing, or bed_dynamics
  stages, and it must not be read as doing so.
- **Grind range is coarse.** Sieved fractions 600–1180 µm, hybrid D[4,3] 537–1540 µm. Espresso
  grinds (D[4,3] ≈ 200–400 µm, fines 15–31 %) sit at or below the bottom edge; only the five
  full-PSD materials (ΩQ–ΩU, D[4,3] 537–951 µm, fines 0.11–0.34) come close, and even those are
  drip-coarse. **Any use at espresso grind is extrapolation.**
- **Single origin, single lot, two roast levels, one temperature (91.5 °C).** No T-dependence, so
  nothing for the observables "temperature effects" backlog.
- **Time window 5–600 s**, with the first ~4 s unobserved — which is precisely where τ lives. The
  author concedes the delay may be a detection-limit artifact: "without data during the first five
  seconds… it is possible that these compounds are extracting at very low concentrations."
- **Five species, no TDS, no EY.** The model produces normalized per-species curves and nothing
  else; it cannot yield a yield.
- **Instrument-specific φ.** Eqns 6.8–6.9 assume the Malvern 100-bin scale with bin 75 ≈ 186 µm,
  a liquid/air splice, and d_c = 45 µm. φ computed from any other PSD representation is a
  different quantity.
- Silent on: swelling, CO₂/degassing during brew, fines migration, temperature transients,
  compaction, and every pressure-related phenomenon.

## Interface mapping

**Inputs consumed:** `GrindState` — but not as the contract currently expresses it. Eqns 6.8–6.9
need the **full binned PSD**, twice (liquid dispersion below 186 µm, air dispersion above), not
the scalars `fines_fraction` / `mean_radius_m` / `boulder_radius_m`. `fines_fraction` is also
threshold-incompatible: 186 µm here versus 100 µm in smrke2024 and khamitova2020, versus radius
moments in wadsworth2026_grindmap.

**Outputs produced:** none of `ShotResultState`. The model emits normalized per-species C_t/C_∞;
`EY_pct` and `tds_pct` are unreachable because there is no solute inventory and no total-solids
measurement. Per-species concentration has **no home in contracts v0.1** — the same gap
bruno2026's card flagged: there is no `SoluteInventory` field, and adding one is the precondition
for the multi-class-chemistry backlog item to land anywhere.

**Couplings:** offline calibration chain only, in two distinct roles:

1. **φ as a grind→extraction closure.** A PSD-driven prediction of the fast-extracting fraction,
   consumable as a prior on cameron2020.extraction_bdf's two-population split. This is the piece
   with runtime-adjacent value, and it needs a PSD-binning adapter plus a decision on the E1
   shell depth.
2. **λ_fast/λ_slow as per-species timescale priors and as a validation gate** on any extraction
   component run in a well-mixed configuration.

Runtime coupling is not available and should not be forced: the model has no pressure, flow, or
bed variable to couple through, and the dilute/K=1 assumption is violated in espresso.

**Kind justification.** Tagged `calibration` per REGISTRY_STATE's rule — the only way to make this
runtime would be to graft a batch model onto a column it never saw, which is the mega-model
failure mode the registry exists to avoid.

## Extractable data

Nothing is published as raw data or code; everything below is transcription or digitization from
the redacted PDF. Ordered by value.

**Tabulated, transcribe now:**

- **Table 6.4 → `data/maille2024_lambda_caffeine_3cqa.csv`** — 17 materials × {λ_fast, λ_slow with
  lower/upper 95 % CI, R², MPE} for caffeine and 3-CQA. Carry the E5 flags on ΩT.
- **Table 6.5 → `data/maille2024_lambda_organic_acids.csv`** — 16 materials × same fields for
  citric, malic, quinic (ΩC/ΩM/ΩO quinic unreported). Carry the E5 flag on ΩL.
- **Table 6.3 → `data/maille2024_phi.csv`** — 17 materials × {θ_v,fines, ϑ_v,coarse, φ}. The
  single most reusable artifact here; store with the E1 note attached.
- **Table 5.2 → `data/maille2024_psd_dispersion_methods.csv`** — 24 materials × 2 dispersion
  methods × {Dx50, D[4,3], D[3,2], volume fraction < 186 µm}. **High registry value beyond this
  card**: it is a direct, same-material, same-instrument measurement of how much the fines
  fraction moves with dispersion method (ΩQ 0.31 liquid vs 0.17 air; ΩA 0.02 vs 0.00). See
  Overlaps.
- **Table 5.4 → `data/maille2024_psd_hybrid.csv`** — 21 materials × {D[4,3], D[3,2], fines
  fraction} for the spliced distribution actually used.
- **Table 5.11 → `data/maille2024_equilibrium_concentrations.csv`** — 21 materials × 5 compounds ×
  {180, 300, 600 s} mean ± SD in mg L⁻¹. The per-species equilibrium inventory at a known brew
  ratio; pairs naturally with bruno2026's roasted-bean composition table.
- **Table 5.10 → `data/maille2024_normalized_vs_time.csv`** — 5 compounds × 3 sieve fractions ×
  {10, 15, 20, 25, 30, 60, 180 s} normalized concentrations. The only place where early-time
  curve values appear as numbers rather than plotted points.
- **Tables 4.2/4.3/4.5/4.6** — ΩA replicate-level absolutes and equilibrium convergence.
- **Table 5.9 (partial)** — ε_p, ε_open, ε_closed, envelope and particle densities for ΩA–ΩC and
  both whole-bean references. Small but rare: particle-scale porosity split by open/closed.
- **Table 5.7** — measured vs Eqn 5.4 SSA for five materials (agreement 0.4–6.5 %).
- **Table 3.2** — 35 roast batches with mass, time, end temperature, % loss, Agtron. Useful as a
  roast-reproducibility reference.
- **Tables 4.1, 6.1, 6.2** — compound properties (MW, solubility, functional groups) and the
  dimensionless-estimate inputs.

**Figures, digitization required (the actual contribution):** Figs. 4.6–4.10 (ΩA, five compounds,
3 replicates × 20 points each), 5.18–5.22 (ΩA–ΩC), 5.23–5.32 (sieve-fraction comparisons), and the
model-overlay plots 6.8 onward. This is ~60 extraction events at ~20 points each. Scoping honestly:
digitizing the ΩA set and the three-sieve-fraction comparison (Figs. 4.6–4.10 and 5.18–5.22) is the
80/20 and is worth doing; the full set is not, given how much of the material context is redacted.

**Permanently unavailable in this release:** loose bulk and particle density for all materials
(Table 5.5), SSA for all materials (Table 5.6), the treatment-effect tables (5.12–5.18, 6.6), and
the parameter-sensitivity figures (6.3–6.5). If the unredacted thesis becomes available through
White Rose, Tables 5.5, 5.6 and 5.9 are the acquisition targets — they would complete a
PSD→SSA→porosity→λ_slow chain that is currently broken at two links.

## Overlaps and conflicts

- **cameron2020.extraction_bdf** (extraction, runtime) — **complements, and offers a closure it
  currently lacks.** Same two-population architecture (fast surface/fines, slow interior), but
  Cameron *fits* the split while Maille *predicts* it geometrically from PSD. The discriminating
  computation is named below. Conflict to record: Cameron's EY ceiling derives from a
  per-bed-volume soluble inventory (29.6 %); Maille has no inventory concept at all, so the two
  cannot be merged without an explicit convention decision — no silent merge.
- **romancorrochano2017_extraction** (extraction/grind/bed_dynamics, runtime) — **competes
  directly, at the same experimental scale**, and wins on transferability. Corrochano's stirred
  vessel with Fickian intraparticle diffusion and per-MW-class D_eff achieves MPE 5–8 % with a
  *material property* (D_eff from microstructure, Table 4.9), whereas Maille's λ are per-material
  per-compound curve fits that transfer nowhere. Maille wins on two axes only: genuine sub-30 s
  resolution, and real chemical species rather than MW proxies. **Provenance is not independent** —
  Maille takes D_eff = 7.67×10⁻¹⁰ m² s⁻¹ and θ_d = 80° from Corrochano 2017, so the Bi/Fo argument
  setting the 186 µm threshold inherits Corrochano's assumptions.
- **pannusch2024** (extraction, runtime) — competes on multi-species coverage with a runtime
  espresso column, two size classes, T-dependence and fitted Sherwood correlations. Complementary
  in data: Pannusch's per-species information is fraction-resolved along a shot; Maille's is
  time-resolved below 30 s in a bed-free system where flow cannot confound the kinetics.
- **angeloni2023** and **khamitova2020** (data-only) — complement. Those supply end-of-shot
  per-species amounts across wide condition matrices (8 species / 66 shots; 4 species / 36
  conditions); Maille supplies the time axis those lack. Angeloni remains the richer dataset for
  the backlog item overall; Maille is strictly better resolved in time and strictly worse in
  condition coverage.
- **schmieder2023** — complements: per-species exponential decay in the cumulative-beverage-mass
  domain, versus Maille's in the time domain. λ ordering by compound is comparable in principle
  between the two and would make a cheap consistency check.
- **moroney2016** — same two-timescale structure, derived by matched asymptotics rather than
  posited. Maille's λ_fast/λ_slow are the empirical analogues of Moroney's t_s and t_d; the
  registry now holds a derived and a measured version of the same decomposition, which is
  worth exploiting.
- **bruno2026** — complements across the roast/brew boundary: bruno gives per-species roasted-bean
  inventory (mg kg⁻¹), Maille gives what fraction of it leaves and how fast. Both cards are blocked
  by the same missing `SoluteInventory` contract.
- **Backlog "extraction: multi-class solute chemistry" — direct hit, and the best early-time entry
  in the registry.** But it lands as a *calibration and gate provider*, not as the runtime
  chemistry: batch, dilute, bed-free, coarse-grind, five species, no EY.
- **Backlog "grind: PSD models beyond bimodal" / ROADMAP §P1 normalization hazards — a real
  contribution independent of the extraction model.** Table 5.2 measures the *same materials* by
  liquid and air dispersion and shows the fines fraction is method-dependent by up to ~2× (ΩQ 0.31
  vs 0.17; ΩR 0.33 vs 0.16; ΩS 0.34 vs 0.16), with the gap widening as material fineness rises.
  Maille's response — the Eqn 5.1–5.3 hybrid splice, liquid below 186 µm and air above, justified
  by particle-orientation effects in laminar versus turbulent dispersion — is a documented method
  for reconciling them. `GrindState.fines_fraction` is currently method-blind and
  threshold-ambiguous across the registry (186 µm here, 100 µm in smrke2024 and khamitova2020,
  radius moments in wadsworth2026_grindmap, sub-voxel treatment in brewer2026.pack_generator).
  **Recommend adding a row to the P1 hazards table on dispersion-method dependence, citing Table
  5.2 as the measurement.**
- **foster2025.infiltration** (infiltration, runtime) — tension worth recording. Maille asserts
  instantaneous hydration to license a common t = 0; the corrected Eqn 6.3 estimate (~3 s, E2–E4)
  is the same order as both his own unexplained τ and Foster's front-passage times. The registry's
  open "infiltration↔extraction coupling" item predicts exactly this: a wetting delay masquerading
  as an extraction delay. Maille's τ is a candidate observable for that coupling — and, notably,
  it appears for caffeine and 3-CQA but not the three acids, which a purely hydrodynamic wetting
  delay would not explain.
- **No bearing on:** wadsworth2026.permeability, brewer2026.streamtube/lb_reference/lb_taichi, the
  Forchheimer/inertial item, κ(t) compaction, or the machine-mode item. There is no bed here.

## Implementation estimate

**Code: S.** Eqn 6.2 is two exponentials; the φ closure is a weighted sum over PSD bins. Perhaps
50 lines plus a PSD-binning adapter. No dependencies beyond numpy.

**Data: M, and it dominates.** Ten tables to transcribe, plus the E1/E5 flags to carry, plus the
optional figure digitization scoped above.

**Blocker to state up front:** the per-bin PSD arrays (v_i,liquid, v_i,air) are **not published** —
only summary statistics in Tables 5.2 and 5.4. So Eqns 6.8–6.9 **cannot be reproduced end-to-end
from the thesis alone.** Any attempt to regenerate Table 6.3 from a fitted lognormal would be a
registry-side construction `[RS]`, not a reproduction, and must be labelled as such.

**Gates, in order of discriminating power:**

1. **φ-split gate (the reason to register this at all).** Compute φ from Cameron 2020's EK43 PSDs
   using Eqns 6.7–6.9 at the E1 two-layer depth, and compare against the fast-population fraction
   cameron2020.extraction_bdf currently fits. Agreement would mean the fast fraction is
   geometrically predictable from PSD and Cameron gains a parameter-free closure; disagreement
   would quantify how much of Cameron's fitted split is doing work the geometry does not support.
   Either outcome is informative. Note the extrapolation: Maille's materials are 2–4× coarser than
   Cameron's, and the shell fraction is strongly size-dependent (0.83 at 200 µm falling to 0.16 at
   1550 µm), so this gate probes the closure exactly where it is least tested.
2. **E1 resolution gate (prerequisite to gate 1).** Recompute ϑ_v,coarse at both one- and two-layer
   depths against Table 6.3. The evidence above already points decisively at two layers
   (mean |error| 0.028 vs 0.194); this gate just makes it reproducible and pins the convention in
   the changelog before φ is used anywhere.
3. **θ_v,fines consistency gate (cheap, executable today).** Table 6.3's θ_v,fines should equal
   Table 5.4's volume-fraction-below-186 µm column. Spot checks agree (ΩA 0.025 vs 0.02; ΩG 0.148
   vs 0.15; ΩU 0.154 vs 0.15). Run it across all 17 rows as a transcription check.
4. **Cross-model timescale gate — BOTH halves LANDED (qualitative); both a "miss".** Fit Eqn 6.2 to
   an independent rig's extraction curve and check whether λ_fast lands in 2.2–19.1 s and λ_slow in
   13–158 s; a miss indicates the two-regime decomposition is not portable off Maille's rig.
   - **cameron half** (`analysis.maille2024.cross_model_timescale_cameron()`): fitting Eqn 6.2 to
     cameron's **model-generated** extraction curve, **no** fitted λ_fast enters Maille's fast band
     (2.2–19.1 s) in any of the four EK43 grinds. The three **finer** settings (gs 1.0/1.5/2.0) are
     single-exponential-like (the constants coincide and a second exponential buys ≈ 0 R² — the
     bi-exponential is non-identifiable); the **coarsest** (gs 2.5) returns **two separated**
     constants (≈ 23.6 / 40.0 s) and is left to formal model selection, **not** asserted
     single-timescale (review comment U5 — the earlier "effectively one-regime" wording was an
     overstatement). Three caveats: cameron has **no well-mixed configuration** (flowing percolation
     bed, so the fit target is its cup curve); it is run to **exhaustion (~400 s), past its ~30 s
     recipe**, to expose λ_slow; and it lumps one solute (one (λ_fast, λ_slow) pair, τ = 0) where
     Maille resolves five.
   - **Roman-Corrochano half** (`cross_model_timescale_roman()`) — the **genuine well-mixed**
     (stirred-vessel) config cameron lacked. **Not rights-blocked for this research use:**
     romancorrochano2017.extraction is the same `published_port`/`NOT_REVIEWED` class as cameron2020
     (which this module already runs); the product #100 deferral gates only the **public Laboratory
     product lens**, not internal validation. Roman's raw curves were never published, so the curve
     is model-generated by its Crank-verified `stirred_vessel` solver (single lumped medium-MW
     species, fine size class R ≈ 20 µm). Finding is two-fold: **(a)** the fit has a **universal
     dimensionless shape** — the fitted **weight** φ ≈ 0.32 and **slow/fast ratio** ≈ 12.3 are
     grind-invariant, while the **absolute** constants scale with the diffusion time (R²/D_eff) and
     vary ~1.9× across the seven grinds (review comment U2 — only the *shape* is invariant, not the
     absolute constants) — the early/late-time signature of **one physical diffusion process** in one
     particle/species class (not a "single mathematical mode", U4), two-regime-*shaped* (R² ≈ 0.999
     vs ≈ 0.95 for one exponential) but **not** Maille's material-varying two-*pool* (fines +
     coarse-shell) construct; **(b)** for the **selected 20 µm fine class** the timescales are
     sub-second, below Maille's bands — a **fine-class-specific**, not universal-numeric, result:
     Roman's coarse class d[4,3] is not published in-repo (larger radii raise τ ∝ R² and could enter
     Maille's bands), so it is **not fabricated** and **not evaluated** (review comment U3). Same word
     "two-regime", different construct — echoes the φ-split semantics gap.

   **Verdict:** the defensible conclusion is **semantic** — a shared bi-exponential form is not a
   shared physical construct. Maille's two-regime decomposition does not port to **either** rig under
   the tested mappings: cameron's flowing bed is single-exponential-like in 3 of 4 settings (coarsest
   pending model selection) with no fast-band match, and Roman's well-mixed diffusion yields one
   physical-process shape at sub-Maille fine-class timescales. Both halves **qualitative**
   (model-generated curves; not a validation of any model).

**Dependencies:** a PSD-binning adapter; a decision on `GrindState.fines_fraction` threshold
semantics (blocks gate 1); and, for anything beyond calibration use, a `SoluteInventory` contract
that does not yet exist.

VERDICT: calibration-provider — the best early-time (<30 s) per-species extraction dataset in the registry and a parameter-free PSD→fast-fraction closure that cameron2020's fitted two-population split currently lacks, but it is a bed-free, flow-free, coarse-grind batch model whose λ are per-material curve fits and which cannot produce EY or TDS — effort M
