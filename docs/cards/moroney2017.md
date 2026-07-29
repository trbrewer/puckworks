# Model card: Moroney 2017 well-mixed suspension kinetics

**Paper/thesis:** Moroney, Lee, O'Brien, Suijver, Marra, "Coffee extraction kinetics in a well mixed system," J. Math. Industry 7:3 (2016/2017). DOI 10.1186/s13362-016-0024-6. Open access, CC-BY 4.0. (Published online 30 Jun 2016; the article PDF header prints "(2017) 7:3" while Springer metadata and most citations say 2016 — citekey follows the printed header to avoid collision with `moroney2016.md`, the SIAM packed-bed sibling.)
**Stage(s):** extraction · **Kind:** calibration (grain-kinetics surrogate for a zero-flow geometry; there is no espresso runtime slot for a well-mixed suspension)
**Status:** card-only

## Scope and mechanism
ODE reduction and matched-asymptotic solution of the Moroney 2015 (Chem. Eng. Sci. 137:216–234, their [5]) double-porosity model for the *dilute-suspension* experiment in [5]: 60 g of grind stirred into 0.5 L of hot water, average concentration measured over time. Because the h-phase is well mixed, all spatial transport (advection, diffusion, dispersion, Darcy flow) drops out, isolating pure grain kinetics: fast surface dissolution from fines/broken surface cells (timescale t_s) in series with slow diffusion out of intragranular pores (timescale t_d). The small parameter ε = t_s/t_d yields an inner (surface-dissolution) layer and an outer (kernel-diffusion) region; composite closed-form solutions to O(ε²) describe the full extraction curve. This is the flow-free complement to the packed-bed asymptotics in `moroney2016.md`: same physics family, transport stripped away.

## Governing equations
Implementation target is the reduced dimensional 3-ODE system, Eqs. (18)–(20), with ICs (16)–(17); or equivalently the dimensionless system (25)–(28) plus composite solutions (95)–(97).

Dimensional reduced system (after φ*_v ≈ φ_v^∞, kernel solids pre-dissolved ψ*_v ≡ 0, volume-correction term dropped):

- (18) dc*_h/dt* = −α* [(1−φ_h)/φ_h] φ_v^∞{4/3} D_v [6/(k_sv2 l_l)] (c*_h − c*_v) + β* [(1−φ_h)/φ_h] [12 D_h φ_cd/(k_sv1 m)] (c_sat − c*_h) ψ*_s
- (19) dc*_v/dt* = α* φ_v^∞{1/3} D_v [6/(k_sv2 l_l)] (c*_h − c*_v)
- (20) dψ*_s/dt* = −β* [12 D_h φ_cd/(k_sv1 m)] [(c_sat − c*_h)/c_s] r_s ψ*_s
- (16)–(17) ICs: c*_h(0) = 0, c*_v(0) = (φ_s,bd/φ_v^∞) c_s, ψ*_s(0) = 1, ψ*_v(0) = 0.

Scales and dimensionless groups:
- (21)–(22) c*_h ~ c_sat φ_v^∞ (1−φ_h)/φ_h; c*_v ~ c_sat; t* ~ t_d = k_sv2 l_l / (6 α* φ_v^∞{1/3} D_v); ψ*_s ~ 1. Inner scales (57)–(58): c*_h ~ [c_s(1−φ_h)/(r_s φ_h)] c_sat; t* ~ t_s = c_s k_sv1 m / (12 β* c_sat D_h φ_cd r_s).
- (23) ε = α* D_v k_sv1 m φ_v^∞{1/3} c_s / (2 β* D_h k_sv2 l_l φ_cd c_sat r_s)   [= t_s/t_d]
- (24) b₁ = 2 β* D_h k_sv2 l_l φ_cd φ_v^∞{2/3} (1−φ_h) c_sat r_s / (α* D_v k_sv1 m φ_h c_s); b₂ = 2 β* D_h k_sv2 l_l φ_cd (1−φ_h) / (α* D_v k_sv1 m φ_h φ_v^∞{1/3})

Dimensionless system on the outer (diffusion) timescale τ:
- (25) ε dC_h/dτ = −ε b₂ C_h Ψ_s + (b₂/b₁) Ψ_s − ε² b₁ C_h + ε C_v
- (26) dC_v/dτ = ε b₁ C_h − C_v
- (27) ε dΨ_s/dτ = ε b₁ C_h Ψ_s − Ψ_s
- (28) C_h(0) = 0, C_v(0) = γ₁, Ψ_s(0) = 1   (γ₁ = dimensionless initial intragranular concentration)

Useful closed forms:
- Conservation (30): C_h + C_v + (b₂/b₁)Ψ_s = const; equilibrium (34): C_h^eq = (b₁γ₁ + b₂)/[b₁(b₁ε + 1)], C_v^eq = ε(b₁γ₁ + b₂)/(b₁ε + 1) — final brew strength in closed form.
- Matched outer solutions (92)–(94) to O(ε); inner solutions (87)–(89) to O(ε²); composite solutions (95)–(97) on the inner timescale/scale. Note the asymmetric truncation (outer C_h to O(ε), inner to O(ε²)) is as printed; Eq. (95) contains an evident typo "γ1" printed as "γ1" with a dropped subscript separator ("b₁ γ1 t ε") — dimensional set (18)–(20) plus numerical solution is the self-consistent target, with (95)–(97) as the fast surrogate.

Symbols: c*_h, c*_v = solute concentration in inter-/intragranular liquid; ψ*_s = fraction of initial surface-coffee remaining; φ_h = intergranular (suspension) liquid fraction context-adapted from bed porosity; φ_v^∞ = final intragranular porosity; φ_cd, φ_s,sd, φ_s,bd = soluble volume fractions (dry grains: total/surface/kernel); r_s = 1/φ_s,sd; k_sv1, k_sv2 = Sauter mean diameters (whole PSD; grains > 50 µm); l_l = v↔h effective diffusion distance; m = coffee cell diameter; D_h, D_v = solute diffusivities; c_sat = solubility; c_s = solid coffee density; α*, β*, γ* = fitting coefficients (γ* not identifiable — kernel dissolution absorbed into IC).

## Parameters
The paper prints no parameter table; dimensional inputs are inherited from Moroney 2015 [5] and the dimensionless values appear in text and Fig. 4/5 captions.

| symbol | value | units | source |
|---|---|---|---|
| dose / water | 60 / 0.5 | g / L | measured (experiment spec, [5]) |
| ε (fine, JK drip filter) | 0.028 | – | derived from [5] fitted parameters |
| b₁ (fine) | 5.239 | – | derived from [5] fitted parameters |
| b₂ (fine) | 2.897 | – | derived from [5] fitted parameters |
| γ₁ (fine) | 0.70 | – | derived from [5] (IC assumption) |
| t_s, t_d (fine) | 1.184, 42.231 | s | derived |
| ε (coarse, Cimbali #20) | 0.071 | – | derived |
| b₁ (coarse) | 1.99 | – | derived |
| b₂ (coarse) | 1.35 | – | derived |
| γ₁ (coarse) | 0.5 | – | derived |
| t_s, t_d (coarse) | 19.389, 270.493 | s | derived |
| extractable mass fraction | 0.28 (coarse) – 0.32 (fine) | – | measured, 90 °C water [5] |
| α*, β* (suspension fit) | not provided in this paper | – | fitted in [5]; embedded in ε, b₁, b₂ |
| dimensional set (φ_h, φ_v^∞, k_sv1, k_sv2, l_l, m, D, c_sat, c_s, …) | not provided here | – | in [5]; packed-bed analogues tabulated in `moroney2016.md` — **do not reuse those for the suspension**: back-computing γ₁ from the packed-bed volume fractions gives ≈ 0.31, not 0.70, so the suspension parameterization in [5] differs |

## Calibration and validation offered by the source
Composite asymptotic solutions are compared against numerical solutions of (59)–(62) and against experimental suspension concentration data from [5] for two grinds (Fig. 5a fine, 5d coarse). Agreement is graphical only — no error metrics anywhere. c_v(t) and ψ_s(t) panels (5b,c,e,f) are validated against numerics only; no intragranular data exists. The comparison is partly circular: α*, β* were fitted in [5] to this same class of extraction curves, so Fig. 5 demonstrates that the asymptotics reproduce the (already-fitted) numerical model, plus the model's original fit quality. ε = 0.028/0.071 is genuinely small here (much better-conditioned than the packed-bed case's ε = 0.127 in `moroney2016.md`), so the asymptotic truncation itself is trustworthy; the physics validation rests entirely on Moroney 2015.

## Assumptions and validity range
- Well-mixed h-phase: uniform external concentration, no flow, no bed — valid for stirred suspensions (cupping/immersion-style experiments), not for any percolation geometry.
- "Dilute" is the stated regime, but the actual experiment is 120 g/L; saturation is respected only through the (c_sat − c*_h) driving force on surface dissolution. At tighter ratios the equilibrium (34) approaches saturation and the linear kinetics assumptions degrade.
- Kernel solids assumed pre-dissolved into intragranular liquid at t = 0 (ψ*_v ≡ 0, γ* dropped as unidentifiable); c*_v and φ*_v are knowingly wrong at early times.
- φ*_v ≈ φ_v^∞ (requires φ_s,sd + φ_s,bd ≪ φ_v^∞); volume-correction term dropped.
- Infiltration/wetting excluded: model starts saturated; ICs (16)–(17) assume zero dissolution during filling (their "simplest choice"; the packed-bed sibling instead assumed c_h(0) = c_sat — the two papers make opposite filling-stage assumptions).
- Isothermal, single lumped solute, one representative grain population per Sauter diameters (no explicit PSD).
- ε ≪ 1 with b₁, b₂ = O(1); ε grows for coarse grinds (already 0.071 at Cimbali #20) — very coarse grinds push toward asymptotic breakdown.
- Silent on: agitation intensity (perfect mixing assumed), grain settling, multi-component chemistry, temperature drift during steeping.

## Interface mapping
Inputs consumed: GrindState (same PSD → k_sv1, k_sv2, l_l adapter already flagged for `moroney2016.md`); dose and water volume (no contract field — suspension geometry is outside BedState/MachineState entirely). Consumes no MachineState, no BedState, no flow.
Outputs produced: c*_h(t) suspension strength curve; closed-form final strength via (34). Not a ShotResultState producer — the registry role is upstream: fitted (α*, β*) or (ε, b₁, b₂, γ₁) as *flow-free priors on grain-kinetics rate constants* handed to cameron2020.extraction_bdf / grudeva2025.
Couplings: offline calibration chain only. Its distinctive value for Sprint 5: a well-mixed immersion experiment is exactly the discriminating measurement that separates grain-kinetics parameters from flow/κ(t) confounds — this card supplies the ready-made fitting model (seconds per fit, no PDE) for any such bench data, and directly serves the planned profile-likelihood audit of Cameron rate constants by providing an independent, transport-free estimator of the same physical constants.

## Extractable data
- Fig. 5(a),(d): experimental suspension concentration points, fine (JK drip filter) and coarse (Cimbali #20) — digitizable, but this is the Philips suspension dataset whose primary source is Moroney 2015 (already the flagged acquisition target). This paper confirms Moroney 2015 contains *suspension* extraction curves for both grinds in addition to the packed-bed curves — strengthens that acquisition case.
- Dimensionless parameter sets (both grinds) and t_s/t_d values: transcribed in the table above; fold into data/moroney_family_params.csv alongside `moroney2016.md` Table 1 rather than a separate file.
- No code, no raw data published. CC-BY 4.0: figures may be reproduced/digitized freely with attribution.

## Overlaps and conflicts
- **moroney2016** (extraction, calibration): direct sibling — that card covers the packed-bed asymptotics and explicitly excluded this paper; together they complete the Moroney-2015 asymptotic pair. Complementary, not competing: different geometry, different IC convention (noted above), and this one has the better-behaved ε. Registry amendment: update the moroney2016 Overlaps line "well-mixed asymptotics… out of scope" to point at this card.
- **cameron2020.extraction_bdf** (extraction, runtime): same two-population physics family; this is its zero-flow limit in closed form. Complements as an independent prior source for rate constants and as an analytic limit gate (Cameron's solver run with flow off and matched parameters should reproduce (95)–(97) trajectories and the equilibrium (34)).
- **grudeva2025** (infiltration+extraction, runtime): the filling-stage IC ambiguity this paper hand-waves (how much dissolves during wetting) is exactly what Grudeva's infiltration phase computes; the opposite IC choices of the two Moroney siblings bracket the uncertainty Grudeva resolves mechanistically.
- **moroney2019 / cooper2021**: same group/dataset lineage; unaffected numerically (different model, different experiment geometry).
- Backlog "extraction: multi-class solute chemistry": multi-constituent extension named as future work only; nothing usable.
- No bearing on flow, packing, κ(t), or observables backlog items.

## Implementation estimate
Small: (18)–(20) is a 3-ODE stiff-ish system (timescale ratio ~36–14) — any BDF/Radau call; composites (95)–(97) are explicit expressions; a fit wrapper over (ε, b₁, b₂, γ₁) or (α*, β*) is a few dozen lines. Gates: (1) transcription check — reproduce equilibrium (34) values and verify conservation (30) numerically for both printed parameter sets; (2) cross-check composite vs. numerical solution reproduces Fig. 5 panels; (3) mutual-validation gate with cameron2020 in the zero-flow limit (shared with the moroney2016 gate design). No dependencies beyond numpy/scipy.

VERDICT: calibration-provider — closed-form, flow-free grain-kinetics surrogate that turns any immersion/steep experiment into an independent estimator of the extraction-stage rate constants (directly serving the Sprint 5 identifiability audit), with both fine and coarse dimensionless parameter sets supplied — effort S
