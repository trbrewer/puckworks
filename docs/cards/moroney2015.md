# Model card: Moroney 2015 double-porosity extraction (parent paper + primary dataset)

**Paper/thesis:** Moroney, Lee, O'Brien, Suijver, Marra, "Modelling of coffee extraction during brewing using multiscale methods: An experimentally validated model," Chem. Eng. Sci. 137, 216–234 (2015). DOI 10.1016/j.ces.2015.06.003
**Stage(s):** extraction · **Kind:** calibration (the runtime extraction slot is held by cameron2020; this system is the numerical parent of the registered moroney2016 surrogate, and its distinct registry value is the primary Philips experimental dataset)
**Status:** card-only

## Scope and mechanism
The original formulation of the Limerick/Philips double-porosity extraction model: a static, saturated coffee bed treated as three overlapping continua (intergranular pores h, intragranular pores v, solid coffee s), with macroscale equations derived by volume averaging over two REVs (cell→grain, grain→bed; Appendices A–B). Extraction proceeds by two mechanisms motivated by the bimodal PSD and batch data: fast dissolution from broken surface cells/fines directly into the h-phase (ψ_s inventory, driven by c_sat − c̃_h), and slow diffusion of kernel solubles from the v-phase into the h-phase (driven by c̃_v − c̃_h; kernel dissolution s→v assumed already complete at saturation). Flow is Darcy with Kozeny–Carman permeability. Only the saturated steady-state stage is modelled — filling and draining are explicitly excluded and initial conditions after saturation are assumed. The full seven-PDE macroscale system (45)–(51) is reduced to a well-mixed ODE system for French-press-type batch extraction and a 1-D advection system for the pressure-driven cylindrical brew chamber; both are fitted to the Philips experiments.

## Governing equations
**Full macroscale system:** their Eqs. (45)–(51) — h-phase advection–diffusion–dispersion with three transfer sinks/sources, Darcy pressure Eq. (46), v-phase balance (47), porosity evolution (48)–(49), surface/kernel inventories (50)–(51). Constitutive pieces: Darcy (21); tortuosity τ = φ_h^{1/3} (Millington) in diffusive flux (25); isotropic dispersion tensor (27); v→h transfer f̃_{v→h} = α_vh(c̃_v − c̃_h) with α_vh = (1−φ_h)φ_v^{4/3} D_v S*_hl/Δ_l (28)–(29); surface dissolution f̃_{s→h} = (1−φ_h)(1−φ_v) D_h (S*_hl/Δ_s)(c_sat − c̃_h) (30); s→v dissolution (31); h↔v fluid transfer via grain-permeability Darcy term (32)–(34); S*_hl = 6/k_sv (36); k_h Kozeny–Carman (38)–(39); k_v Kozeny–Carman with 180 = 36κ, κ = 5 (40); inventory ODEs (43)–(44).

**What would actually be implemented** are the two fitted reductions (all spatial-diffusion/dispersion terms dropped — justified a posteriori in Appendix E: advection/dispersion ~10², advection/diffusion ~10⁶, Eqs. (171), (174); p̃_h = p̃_v so all pressure-transfer terms vanish; ψ_v kernel dissolution dropped, kernel coffee pre-dissolved into v-phase):

*Batch (well-mixed, French-press type), Eqs. (52)–(56):*
- (52) φ_h dc̃_h/dt = α*(1−φ_h)φ_v^{4/3} D_v (6/(k_sv2 l_l))(c̃_v − c̃_h) + β*(1−φ_h)(12 D_h φ_c0/(k_sv1 m))(c_sat − c̃_h)ψ_s
  [transcribed with the v→h term written as (c̃_v − c̃_h); the paper prints −(c̃_h − c̃_v), same thing]
- (53) d(φ_v c̃_v)/dt = −α* φ_v^{4/3} D_v (6/(k_sv2 l_l))(c̃_h − c̃_v) — note sign convention as printed; this is the v-phase losing solute to h
- (54) dφ_v/dt = −(1/r_s) ∂ψ_s/∂t
- (55) dψ_s/dt = −β*(12 D_h φ_c0/(k_sv1 m))((c_sat − c̃_h)/c̃_s) r_s ψ_s
- ICs (56): c̃_h(0) = 0, c̃_v(0) = c_v0, φ_v(0) = φ_v0, ψ_s(0) = 1.

*Cylindrical brew chamber (1-D, pressure-driven), Eqs. (57)–(65):*
- (57) φ_h ∂c̃_h/∂t = [k²_sv1 φ³_h/(36κμ(1−φ_h)²)] ∂/∂z[c̃_h(∂p̃_h/∂z + ρg)] − α*(1−φ_h)φ_v^{4/3} D_v (6/(k_sv2 l_l))(c̃_h − c̃_v) + β*(1−φ_h)(12 D_h φ_c0/(k_sv1 m))(c_sat − c̃_h)ψ_s
- (58) ∂²p̃_h/∂z² = 0 (linear pressure profile)
- (59)–(61) as (53)–(55) with ∂/∂t
- BCs/ICs (63)–(65): c̃_h(L,t) = 0, p̃_h(0,t) = 0, p̃_h(L,t) = Δp; JK fine grind c_h0(z) = c_sat; Cimbali #20 c_h0(z) = (c_max/L)(L−z) (linear, extraction during filling assumed partial); c̃_v(z,0) = c_v0 uniform; surface inventory ψ_s0 reduced by the coffee assumed pre-extracted into the h-phase.

Symbols: c̃_h, c̃_v = solute concentration in inter-/intragranular pores [kg m⁻³]; c̃_s = solid coffee concentration (fixed, 1400 kg m⁻³); ψ_s = fraction of initial surface coffee remaining; φ_h, φ_v = inter-/intragranular porosity; φ_c0, φ_s,s0, φ_s,b0 = initial volume fractions of soluble coffee (total / surface / kernel) in dry grains; r_s = 1/φ_s,s0; k_sv1, k_sv2 = Sauter mean diameters (whole PSD; particles > 50 µm, i.e. excluding cell fragments); l_l = volume-weighted mean grain radius; m = coffee cell diameter; D_h = D_v = solute diffusivity; c_sat = solubility; κ = Kozeny–Carman shape factor; μ, ρ = water viscosity, density; α*, β* = fitting coefficients multiplying the kernel-diffusion and surface-dissolution transfer terms; Δp = bed pressure differential; L = bed depth.

Transcription flags (recorded, not corrected): (i) Eq. (39) prints the identical expression twice ("= k²_sv1φ³_h/36κ(1−φ_h)² = k²_sv1φ³_h/36κ(1−φ_h)²") — typo, harmless. (ii) Eq. (34) is labelled f̃^{w*}_{h→l} but carries the same sign/expression as the p̃_h ≥ p̃_v branch of f^{w*}_{l→h} in (33) — direction-label inconsistency, moot once p̃_h = p̃_v is assumed. (iii) κ is used with two different values: 3.1 (measured, bed permeability k_h) and 5 (nominal, grain permeability k_v via the 180 factor) — same symbol, different closures. (iv) Text below (38) says "shape factor κ usually 2–6 … estimated at κ = 3.1", while §4.6.4 says "we have chosen κ = 5" citing Aubertin — the sentence placement is garbled in the original but the usage above is unambiguous from Tables/equations.

## Parameters
Batch experiments (their Table 1):

| symbol | JK drip filter | Cimbali #20 | units | source |
|---|---|---|---|---|
| φ_v0 | 0.6444 | 0.6120 | – | derived (from measured soluble mass; dry-in-air φ_v = 0.56 measured) |
| φ_h | 0.8272 | 0.8272 | – | derived (dilute suspension geometry) |
| k_sv1 | 27.35 | 38.77 | µm | measured (PSD) |
| k_sv2 | 322.49 | 569.45 | µm | measured (PSD, >50 µm) |
| l_l | 282 | 463 | µm | measured (PSD) |
| D_h = D_v | 2.2×10⁻⁹ | 2.2×10⁻⁹ | m² s⁻¹ | nominal (caffeine in water, 80 °C; Jaganyi & Madlala) |
| ρ | 965.3 | 965.3 | kg m⁻³ | nominal (water 90 °C) |
| μ | 0.315×10⁻³ | 0.315×10⁻³ | Pa s | nominal (water 90 °C) |
| m | 30 | 30 | µm | nominal (cell size 25–50 µm) |
| c_sat | 212.4 | 212.4 | kg m⁻³ | estimated (highest observed concentration across the four experiments) |
| c̃_s | 1400 | 1400 | kg m⁻³ | nominal |
| κ (bed) | 3.1 | 3.1 | – | measured (airflow pressure-drop through compacted coffee beds) |
| φ_c0 | 0.143435 | 0.122 | – | measured (max extractable solubles) |
| φ_s,s0 | 0.059 | 0.07 | – | fitted/estimated |
| φ_s,b0 | 0.084435 | 0.052 | – | fitted/estimated (φ_c0 − φ_s,s0) |
| α* | 0.1833 | 0.0881 | – | fitted (joint fit to both batch experiments) |
| β* | 0.0447 | 0.0086 | – | fitted |
| r_s | 16.94 | 14.28 | – | derived (1/φ_s,s0) |
| c_v0 | 183.43 | 118.95 | kg m⁻³ | assumed (all kernel coffee pre-dissolved) |

Cylindrical brew chamber, changed/new values only (their Table 2):

| symbol | JK drip filter | Cimbali #20 | units | source |
|---|---|---|---|---|
| φ_v0 | 0.6231 | 0.6218 | – | derived |
| φ_h | 0.2 | 0.25 | – | fitted (chosen to match observed volume flow via Darcy + Kozeny–Carman; not measured — bed compacts under Δp) |
| c_max | – | 82.63 | kg m⁻³ | measured (initial exiting concentration, coarse) |
| φ_s,s0 | 0.11 | 0.07 | – | fitted/estimated |
| φ_s,b0 | 0.033435 | 0.052 | – | fitted/estimated |
| α*, β* | 0.1833 / 0.0447 | 0.0881 / 0.0086 | – | reused unchanged from batch fit |
| r_s | 9.09 | 14.28 | – | derived |
| c_v0 | 78.88 | 78.88 | kg m⁻³ | assumed |
| Δp | 230 000 | 65 000 | Pa | measured (differential across bed) |
| L | 0.0405 | 0.0526 | m | measured (59 mm chamber ID, 60 g dose ≈ 4% moisture) |

## Calibration and validation offered by the source
Graphical agreement only — no error metrics anywhere. Batch: numerical solution of (52)–(55) vs. French-press data (Fig. 6, both grinds), with a single (α*, β*) pair per grind fitted "to fit both experiments equally well." Cylindrical: numerical solution of (57)–(61) vs. flow-through data (Fig. 7, both grinds), reusing the batch (α*, β*) — the strongest claim in the paper, since the transfer coefficients transfer across geometries. But several fitted/assumed quantities were re-adjusted per configuration (φ_s,s0/φ_s,b0 split, r_s, c_v0, initial profiles), so this is not a parameter-free prediction. Circularities to note: c_sat is set from the maximum observed concentration in the same experiments; cylindrical φ_h is chosen to reproduce the observed flow, so the flow side is fitted, not validated; initial conditions (kernel coffee fully pre-dissolved, JK bed at c_sat, Cimbali linear profile) are unverifiable assumptions covering the unmodelled filling stage. Also independently useful: the pressure-invariance experiment (Fig. 12) shows extraction curves at 2.3 vs 9 bar absolute pressure (same 60 g, 250 ml/min) identical to within a few percent — direct evidence that dissolution/diffusion kinetics are substantially independent of absolute pressure and that pressure enters extraction only through flow.

## Assumptions and validity range
- Saturated, static bed only; filling and draining excluded; grain swelling not modelled (assumed absorbed into a PSD shift during filling).
- Isothermal (80–90 °C); single lumped solute (defended via Fig. 8: many components share similar kinetics); liquid density independent of concentration.
- Constant φ_h in time (all porosity change confined to grains ⇒ p̃_h ≥ p̃_v, then p̃_h = p̃_v in the fitted reductions — no h↔v fluid transfer in practice).
- Spherical-particle approximations throughout (Sauter diameters, S* = 6/k_sv, Kozeny–Carman); s-phase specific surface not measurable — folded into the lumped, fitted β*.
- Kernel dissolution assumed much faster than kernel diffusion (all kernel coffee pre-dissolved at t = 0); c̃_s fixed while φ_v evolves.
- Advection-dominated regime required for the reductions (Appendix E: Pe ~ 10⁶ at L ≈ 0.05 m, v_c ≈ 7 mm/s); breaks for very slow flow or steep local gradients.
- Silent on: bed compaction dynamics (acknowledged — φ_h simply re-fitted under pressure), fines migration, channeling/radial heterogeneity, temperature dependence, multi-component chemistry, unsaturated flow, basket/screen exit resistance.
- Regime: drip-filter brew ratio (60 g : 1 L), 0.65–2.3 bar differential (9 bar absolute tested for invariance only) — espresso-adjacent pressures, not espresso ratios.

## Interface mapping
Inputs consumed: BedState (depth_m → L, porosity → φ_h; permeability built internally from Kozeny–Carman (39) with measured κ = 3.1 — supplying BedState.k directly conflicts, same clash flagged on moroney2016), GrindState (adapter needed: contract carries fines_fraction/boulder_radius/mean_radius, model needs k_sv1, k_sv2, l_l from the full PSD — identical adapter gap as moroney2016/moroney2019), MachineState (constant Δp only; Δp here is a measured differential across the bed, so no gauge/absolute ambiguity — cannot consume P_of_t).
Outputs produced: c̃_h(0,t) exit trace → ShotResultState.tds_pct/EY_pct/traces by integration.
Couplings: offline calibration chain only. The registered moroney2016 surrogate is the closed-form of exactly this system; this paper supplies the numerical reference the surrogate's gate (composite vs. numerics) targets, plus the measured parameter provenance behind moroney2016's Table 1.

## Extractable data
This is the paper's principal registry value — the primary Philips dataset that moroney2016, moroney2019, and cooper2021 all borrow from. No raw data or code published; everything below is figure digitization or table transcription.
- Table 1 + Table 2 (above) → data/moroney2015_params.csv — transcribable now; supersedes second-hand parameter provenance in moroney2016.md ("[14]" citations resolve here).
- Fig. 3(a–d): cylindrical brew-chamber c_brew and c_exit vs M_brew (0–1000 g), JK fine AND Cimbali #20 coarse — digitize both; this answers the open question in moroney2019.md ("check whether 2015 includes the coarse grind" — it does, in both pot and exit form).
- Fig. 11: JK at two doses — 12.5 g (L = 1.12 cm, Δp = 0.5 bar) and 60 g (L = 4.05 cm, Δp = 2.3 bar), both 250 ml/min — a *third* permeability anchor beyond moroney2019's two, and a bed-depth-scaling check.
- Fig. 12: JK 60 g at 2.3 vs 9.0 bar absolute — the pressure-invariance result; digitize for the record even though the curves overlap.
- Fig. 2 + Fig. 10: batch extraction curves, five grinds (JK, Cimbali #20, Cimbali #30, DE standard, DE coarse), 0–600 s — grind-size sweep of extraction kinetics.
- Fig. 1 + Fig. 9: bimodal PSDs for four grinds (Mastersizer 2000; Cimbali #30 too coarse to analyze) — feeds the grind-stage PSD ledger.
- Fig. 8: normalized extraction profiles for trigonelline, caffeine, nicotinic acid, formic acid, furfuryl alcohol, acetic acid, lipids (from Booth et al. 2012 ESGI report, freely available online — acquire primary) — directly relevant to the multi-class solute backlog: most species collapse onto similar kinetics; lipids visibly deviate (plateau ~0.2 at 7 mL vs ~0.05–0.1 for the rest).
- Scalars worth a ledger row: max extractable solubles 28% (very fine) – 32% (very coarse) at 90 °C (DE grinds, 5 h stirred; cross-check against cameron2020's 29.6% EY ceiling — consistent); 1 °Brix = 8.25 g/L (drip coffee, evaporative calibration); φ_v = 0.56 dry-in-air; κ = 3.1 measured; cell size 25–50 µm; 50 µm fines threshold for k_sv2.

## Overlaps and conflicts
- **moroney2016** (extraction, calibration — registered card): direct parent–child. This paper is the source of moroney2016's Eqs. (2.12)–(2.17), Table 1, and experimental curves; moroney2016 supersedes it as the *implementable* surrogate (closed-form, fit-in-seconds), while this card supersedes moroney2016's second-hand data provenance. The moroney2016 card's suggested "card/data pass on [14]" is discharged by this card.
- **cameron2020.extraction_bdf** (extraction, runtime): same two-population family; this system competes at runtime only in principle — constant-Δp, saturated-only, drip ratios. Complementary as provenance: the 28–32% max-solubles range independently brackets Cameron's 29.6% EY ceiling.
- **moroney2019** (data-only): child paper, same Philips rig; its Fig. 6 data duplicates Fig. 3 here — once Fig. 3 is digitized, moroney2019 Fig. 6 digitization is redundant (both grinds covered here). The bed heights moroney2019.md flagged as unstated are given here (4.05 / 5.26 cm; 1.12 cm for 12.5 g).
- **cooper2021** (erratum provider): corrects moroney2019's LDF h_sl values; does not touch this paper's α*, β* (different transfer formulation).
- **foster2025.infiltration** (infiltration, runtime): complementary exactly as anticipated — the filling stage this paper refuses to model, and whose assumed post-fill state (pre-dissolved kernels, c_h0 profiles) is the natural handoff target for front-passage initial conditions (backlog: infiltration↔extraction coupling).
- **wadsworth2026.permeability** (packing, calibration): competing permeability closure (Kozeny–Carman, measured κ = 3.1, vs. percolation k(R, φ_p)); the three Δp–Q–L anchors here (0.5/2.3/0.65 bar) extend the gate data moroney2019 provided.
- Backlog "extraction: multi-class solute chemistry": Fig. 8 is the registry's clearest single-figure evidence for when the lumped-solute assumption holds (most species) and when it fails (lipids) — weaker than Angeloni 2023's per-species dataset but earlier and independent.
- Backlog "unsaturated flow at fine grinds": explicitly out of scope here; the filling-stage extraction assumptions (JK bed pre-saturated at c_sat) are exactly the guesswork that backlog item would replace.

## Implementation estimate
No new component: the implementable surrogate (moroney2016) and the runtime slot (cameron2020) are both registered; implementing (57)–(61) numerically would only recreate the reference that moroney2016's existing gate 2 (cross-check vs. cameron2020's BDF in the two-population limit) already provides more usefully. Data work is the deliverable: table transcription S; figure digitization (Figs. 1–3, 8–12 — nine panels-worth, log-x PSDs included) M. Gate design for the data: (1) re-run the batch ODEs (52)–(55) from Table 1 and overlay on digitized Fig. 6 curves as a transcription check; (2) Kozeny–Carman with κ = 3.1 + Table 2 φ_h must reproduce the measured Δp at 250 ml/min for all three anchors (internal consistency of the fitted φ_h).

**LANDED (2026-07-23).** (1) `gate_moroney2015_batch_ode` (solver `puckworks/analysis/moroney2015_batch.py`) reproduces the Fig-6 batch model plateau for both grinds (36.6 JK / 30.5 vs 36.6 / 30.4, ~0.3%). (2) `gate_moroney2015_kappa_anchors` reproduces the Δp anchors within ~5%.

**DERIVED immersion volume bookkeeping (exact reconstruction, not assumed).** The batch equations (52)–(56) are written on the per-suspension-volume basis V_T. From 60 g coffee at 4% moisture (57.6 g dry solids), c̃_s = 1400 kg m⁻³ → V_s = 41.14 cm³; with the **dry-in-air** intragranular porosity φ_v = 0.56 (§5.1 — NOT Table 1's φ_v0 = 0.6444, which is the post-kernel-dissolution state 0.56 + φ_s,b0 = 0.6444) the grain envelope V_l = V_s/(1−0.56) = 93.51 cm³, so **V_T = 500 + 41.14 = 541.1 cm³** and **V_h = V_T − V_l = 447.6 cm³**, giving φ_h = V_h/V_T = **0.8272** — matches Table 1 exactly (four d.p.), confirming the authors' construction. Conversion factors when redimensionalizing between a bed-volume basis and a per-water-charge basis: V_T/V_water = 1.0823, V_h/V_water = 0.8953 (~10.5% of the water is sequestered in intragranular pores at t=0). **The c̃_h / Fig-2/6 brew concentration is a direct liquid concentration and compares with NO factor** — the factors enter only when converting extracted-mass yield ↔ concentration. Cross-checks that close the loop: c_v0 = φ_s,b0·c̃_s/φ_v0 = 183.44 (Table 1: 183.43); total soluble (φ_s,s0+φ_s,b0)·c̃_s·(1−φ_h)·V_T = 18.78 g = 31.3% of dose (consistent with 28–32% extractable); equilibrium c̃_h = 36.6 kg m⁻³ on the Fig-6a plateau (a naive ÷0.5 L gives 37.6, ~3% high — the signature of omitting the dilution bookkeeping). Record V_T = 541.1 cm³ and V_h = 447.6 cm³ as **DERIVED** constants in the P2 baseline metadata.

VERDICT: data-only — the model is already registered in better forms (moroney2016 surrogate, cameron2020 runtime), but this is the primary source for the Philips dataset the registry has been chasing: three permeability anchors, fine+coarse extraction curves, a five-grind batch sweep, the pressure-invariance result, per-species kinetics, and measured κ = 3.1 — effort M
