"""Register all founding components."""
from puckworks.registry import Component, register
from puckworks.validation import gates as G

register(Component(
    name="cameron2020.extraction_bdf", stage="extraction", kind="runtime",
    paper="Cameron et al., Matter 2, 631-648 (2020)", doi="10.1016/j.matt.2019.12.019",
    module="puckworks.models.cameron2020.extraction_bdf",
    gates=[G.gate_cameron_conservation],
    assumptions="saturated bed from t=0; homogeneous 1D flow; single solute pool; "
                "per-bed-volume soluble inventory (EY ceiling 29.6%)",
    valid_range="EK43 dial 1.1-2.3; 20 g in / 40 g out class recipes",
    notes="mass-conservative FV + scipy BDF; ~0.15-pt default-grid bias (per the paper's SI convergence); gated on the built-in EY==EY_solid mass budget"))

register(Component(
    name="brewer2026.streamtube", stage="bed_dynamics", kind="runtime",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.streamtube",
    gates=[G.gate_streamtube_heldout],
    assumptions="parallel non-exchanging tubes; unit-mean lognormal k; "
                "sigma(phi1) is an EMPIRICAL closure over the calibrated domain",
    valid_range="calibrated at dial 1.1-1.5; LOO-interpolated, not externally validated",
    notes="Rung B fines migration is hypothesis-generating"))

register(Component(
    name="brewer2026.pack_generator", stage="packing", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.pack_generator",
    gates=[G.gate_pack_generator_admissible],
    assumptions="overlapping (Boolean) spheres - Wadsworth model class; fines sub-voxel, "
                "represented via columnar heterogeneity field (w_floor >= 0.25)",
    valid_range="grain radius >= 10 voxels; columns >= 5 grain diameters for sigma"))

register(Component(
    name="brewer2026.lb_reference", stage="flow", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.lb_reference",
    gates=[G.gate_lb_channel],
    assumptions="D3Q19 TRT (magic 3/16), full-way bounce-back, Stokes regime",
    valid_range="verification twin; production runs use lb_taichi",
    notes="channel exact to 0.03-0.05%; sphere drag -7% at r=8.5 lu (staircase)"))

register(Component(
    name="brewer2026.lb_taichi", stage="flow", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.lb_taichi",
    assumptions="same physics as lb_reference (cross-checked to 0.003%); "
                "f32 needs g >= ~1e-5 signal; heterogeneous packs need g ~ 3e-6 (Mach)",
    valid_range="CPU/GPU; optional dependency taichi",
    notes="Colab production solver"))

register(Component(
    name="wadsworth2026.permeability", stage="packing", kind="calibration",
    paper="Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026)", doi="10.1098/rsos.252031",
    module="puckworks.models.wadsworth2026.permeability",
    gates=[G.gate_wadsworth_collapse],
    assumptions="percolation k(phi_p) with phi_c=0; angularity via exp(alpha R); "
                "validated at phi_p 0.37-0.67 UNTAMPED - tamped regime is extrapolation",
    valid_range="<R> 145-818 um, two arabica roasts",
    notes="reconciling with Cameron flux implies phi_c~0.11 or series screen resistance"))

register(Component(
    name="pannusch2024.solver", stage="extraction", kind="runtime",
    paper="Pannusch et al., J. Food Eng. 367, 111887 (2024)", doi="10.1016/j.jfoodeng.2023.111887",
    module="puckworks.models.pannusch2024.solver",
    gates=[G.gate_pannusch_solver_mape],
    assumptions="1D two-grain (fine/coarse) saturated extraction; first-order "
                "interphase transfer with Sherwood(Re,Sc) closure; van't Hoff K(T); "
                "constant porosity; method-of-lines 5-pt biased upwind + BDF; "
                "faithful port of the released MATLAB; measured-flow driven (Q,T)",
    valid_range="T 80-98 C, Q 1-3 mL/s, EK43-type grind 1.4-2.0; centre-grind (1.7) "
                "used for all exps (per-exp grind in opaque source list); flow-"
                "prediction regime (MAPE 18%) + CGA roast confound quarantined (card)",
    notes="reproduces fit MAPEs vs Schmieder kinetics: TDS 6.7/caffeine 6.4/"
          "trigonelline 10.2/CGA 7.2% (published 6.07/4.59/7.85/4.98; post-fit). "
          "Creates RC-4a. Consumes pannusch2024.closures. Full run ~13 s"))

register(Component(
    name="pannusch2024.closures", stage="extraction", kind="calibration",
    paper="Pannusch et al., J. Food Eng. 367, 111887 (2024)", doi="10.1016/j.jfoodeng.2023.111887",
    module="puckworks.models.pannusch2024.closures",
    gates=[G.gate_pannusch_closures],
    assumptions="temperature/flow constitutive closures ONLY (Wilke-Chang D(T), "
                "VDI water μ/ρ, Sherwood Sh=A Re^B Sc^(1/3), van't Hoff K(T)); "
                "faithful port of the released MATLAB; full 4-solute PDE solver "
                "+ fit-MAPE reproduction (RC-4a) DEFERRED",
    valid_range="T 80-98 C, Q 1-3 mL/s; fitted Sherwood params lack generality; "
                "Wilke-Chang over-predicts absolute D but is the model's own law",
    notes="de-risking slice of 1.8a: μ@90C=3.13e-4 (card 3.15e-4), ρ@90C=959; "
          "K(Tref)=Kref, weak T-dependence; Table 2 params in data/pannusch2024/"))

register(Component(
    name="grudeva2025.reduced", stage="extraction", kind="runtime",
    paper="Grudeva PhD thesis (Portsmouth 2023) + Grudeva, Moroney & Foster, EJAM 37, 496 (2026)",
    doi="10.1017/S095679252500018X",
    module="puckworks.models.grudeva2025.reduced",
    gates=[G.gate_grudeva_no_eps_kappa, G.gate_grudeva_reduced_solver],
    assumptions="sharp wetting front + two-population (fines/boulder) extraction; "
                "matched asymptotics -> saturation front s_d(t) + boulder-limited "
                "inlet; adjudicated NO-ε capacitance (LOG 1); faithful port of the "
                "released reference solver (github YoanaGrudeva/espresso-model)",
    valid_range="ε<<1 saturated-fines regime; prescribed flow (Darcy pre-drip + "
                "empirical post-drip); constant μ,ρ; single solute; RC-2 verification-"
                "gated (post-fit vial reconstruction) until companion dataset lands",
    notes="RIGHTS: code RIGHTS_BLOCKED (#73) -- self-documented port of the unlicensed upstream "
          "solver; see puckworks.rights + docs/cards/grudeva2025.md; not for new Lab execution / "
          "runners / adapters / release. s_d^{-1}(1)=6.40 == published; per-vial masses reproduce C1 "
          "(14-shot total 2.9g, 9/13 within 1 SD); κ Eq6.14@9.2bar=2.27e-15 confirms decade "
          "adjudication. Resolution study is a slow ladder. Creates RC-2"))

register(Component(
    name="liang2021.desorption", stage="extraction", kind="calibration",
    paper="Liang, Chan & Ristenpart, Sci. Rep. 11, 6904 (2021)", doi="10.1038/s41598-021-85787-1",
    module="puckworks.models.liang2021.desorption",
    gates=[G.gate_liang_kemax_refit, G.gate_liang_eoven_ceiling],
    assumptions="full-immersion pseudo-equilibrium; single lumped species; "
                "K*E_max fixed dissolved fraction; E_max=0.30 ASSUMED; endpoints "
                "only (no kinetics) — NOT a flow/espresso extraction model",
    valid_range="R_brew>=3 (fails at 2); 80-99 C immersion; supplies equilibrium "
                "ceiling + oven-dry/retention observable kernel only",
    notes="K*E_max refit 0.219 from Fig3 (card 0.215); §5.5: equilibrium ceiling "
          "< cameron inventory ceiling (K<1); E_oven kernel tracks Fig 4"))

register(Component(
    name="moroney2016.surrogate", stage="extraction", kind="calibration",
    paper="Moroney et al., SIAM J. Appl. Math. 76(6), 2196 (2016)", doi="10.1137/15M1036658",
    module="puckworks.models.moroney2016.surrogate",
    gates=[G.gate_moroney_fig6_washthrough],
    assumptions="matched-asymptotic constant-dP two-population reduction; "
                "leading-order composite (Eq 3.45) only — outer bulk-diffusion "
                "tail (3.61-3.62) and O(eps) correction not on card, not modeled",
    valid_range="saturated bed; eps=0.127 (~13% truncation); Fig 6 reproduction "
                "QUALITATIVE (plateau + wash-through timing, not the tail)",
    notes="closed-form surrogate; mutual-validation vs cameron2020 BDF at matched "
          "two-population limit is a DEFERRED future gate (card gate design 2)"))

register(Component(
    name="brewer2026.coupled_kappa_t", stage="bed_dynamics", kind="synthesis",
    paper="This project (puckworks) — SYNTHESIS card, no external paper",
    doi="",
    module="puckworks.models.brewer2026.coupled_kappa_t",
    gates=[G.gate_kappa_t_degeneracy, G.gate_kappa_t_composition_diagnostic],
    assumptions="one shared porosity eps(t); four branches compose ADDITIVELY (fixes "
                "the multiplicative harness double-counting): extraction + (waszkiewicz "
                "m_d/dose), swelling - (mo2023_2, fixed-dP UNVALIDATED), compaction - "
                "(fasano II, params UNIDENTIFIED -> stub), fines - (fasano I, "
                "UNIDENTIFIED -> stub); clamp [0.02,0.95] as regime edges; NO new free "
                "params. FLOW via waszkiewicz poroelastic closure (near-choke)",
    valid_range="FRAMEWORK-level only; as sound as its shakiest branch (3 donors "
                "unidentified/unvalidated). Degeneracy: extraction-only == poroelastic "
                "rung 4 EXACTLY (RMSE 0.116). Composition residual 0.648 (worse than "
                "flat null) DIAGNOSES mo2023_2 swelling mis-scaled for the saturated rig "
                "-- reported, not tuned. Flow closure = waszkiewicz POROELASTIC (card "
                "Eq.2, corrected 2026-07-11 from CK to match this code): required for "
                "the 14x near-choke rise (CK too gentle, RMSE ~1.5 vs 0.116); CK "
                "retained as auxiliary/illustrative only",
    notes="the physically-coupled (ODE) form of the kappa(t)=kappa0 f(P,eps,E) backlog "
          "item; generalizes waszkiewicz2025.poroelastic (its extraction-only special "
          "case, exact-reduction gated). compaction/fines branches are structural stubs "
          "(donor params unidentified). Register kind=synthesis so no reader hunts for "
          "a paper. Never label 'validated kappa(t) law'"))

register(Component(
    name="fasano2000_partI.fines_migration", stage="bed_dynamics", kind="calibration",
    paper="Fasano, Talamucci & Petracco, 'The Espresso Coffee Problem,' ch.8 in "
          "Complex Flows in Industrial Processes, Springer (2000)", doi="",
    module="puckworks.models.fasano2000_partI.fines_migration",
    gates=[G.gate_fasano_freeboundary, G.gate_fasano_cor82_nonmonotone,
           G.gate_fasano_reversal_signature],
    assumptions="fasano-STRUCTURED (NOT a port): the paper leaves K(b,m), M, gamma "
                "unpublished, so OUR closures are used (R(u)=1+u, M=5, R_c=50, mu=0.5) "
                "with the digitized Fig 8.7 beta(q). 1D saturated free-boundary "
                "fines migration: release (8.16) -> advection (8.23) -> compact-layer "
                "growth (8.19) -> Darcy flux closure (8.25); Landau-mapped MOL",
    valid_range="MECHANISM demonstration / verification strength ONLY (the card's own "
                "level for the source). Reproduces the STRUCTURE: mass balance 8.33 "
                "closed <1%, q(t) monotone-nonincreasing (Lemma 8.3), s>=s_m (Lemma "
                "8.1), nonmonotone q_inf(p0) with interior peak (Fig 8.6 shape). Does "
                "NOT reproduce their exact curve (closures unpublished); enters by GATE "
                "not inheritance, like RC-3b. No espresso-data fit possible",
    notes="the compaction/counter-migration branch of the kappa(t) backlog (complements "
          "mo2023_2 swelling + lee2023 extraction branches). q_inf(p0) peaks at p0~0.6 "
          "from release->compaction->resistance feedback. Fig 8.6 peak-tracks-beta-knee "
          "(Cor 8.2) verified at DATA level by gate_fasano_cor82_nonmonotone"))

register(Component(
    name="mo2023_2.coupled_bed", stage="extraction", kind="runtime",
    paper="Mo, Navarini, Suggi Liverani & Ellero, J. Food Eng. (2023)",
    doi="10.1016/j.jfoodeng.2023.111843",
    module="puckworks.models.mo2023_2.coupled_bed",
    gates=[G.gate_mo2_coupled_bed_fig8],
    assumptions="depth-resolved through-flow bed (Eqs 19-24): clean water down N_z "
                "layers, fine+coarse hindered-diffusion grains per layer (Eqs 9-17) "
                "with the partition surface BC c(R)=c_b/K; fixed-flow; filling front "
                "(Eqs 29-30, fixed-q linear plug-fill dz_f/dt=q/(eps_b A)) with the "
                "cup=pumped-minus-dead-volume correction; swelling off (fixed-q ~ "
                "invisible, gate-4)",
    valid_range="type-M Fig 8 (M_c<30 g): mass-conserving (~0.99, converged), BEATS "
                "the reduced mo2023_2.extraction on both untuned metrics -- within-bars "
                "5/9 (vs 4/9), shape-spread 37% (vs 110%). The M_c=20 over-prediction "
                "is CONVERGED (refinement worsens it) -> genuine model-vs-data, matching "
                "the card's 'overestimates beyond M_c~30 g'; NOT an implementation gap. "
                "Absolute EY needs one inventory scale (max-EY); shape is the signal",
    notes="supersedes mo2023_2.extraction (reduced lumped) for Fig-8 fidelity; the "
          "reduced version stays for the fixed-q swelling-insensitivity gate. Filling "
          "front is the fixed-q analog of foster2025.infiltration's fixed-P sharp front "
          "(infiltration<->extraction coupling, backlog). du->dC flux mass-bug fixed. "
          "Appendix-A.2 numerics not matched -- moot (solution converged)"))

register(Component(
    name="mo2023_2.swelling", stage="bed_dynamics", kind="runtime",
    paper="Mo, Navarini, Suggi Liverani & Ellero, 'Modelling swelling effects in real "
          "espresso extraction using a 1-D coarse-grained model,' J. Food Eng. (2023)",
    doi="10.1016/j.jfoodeng.2023.111843",
    module="puckworks.models.mo2023_2.swelling",
    gates=[G.gate_mo2_swelling_flow_decay, G.gate_mo2_swelling_insensitivity,
           G.gate_mo2_k0_carman_kozeny, G.gate_mo2_fixed_flow_trends],
    assumptions="isotropic grain swelling by NONLINEAR water diffusion (D^w); fixed bed "
                "height so swelling only reduces eps_b (Eq 21); Carman-Kozeny flow at "
                "fixed dP; fine+coarse representative particles swell independently "
                "(tau~R^2/D^w -> boulders partially swell); NO surface dissolution",
    valid_range="fixed-dP flow DECAY (Fig 3a headline) reproduced as a Δp/mu/L-"
                "independent RATIO q(60)/q(0): E/H/M within ~5%, F within ~13%, and "
                "the coarser-throttles-less ordering E<H<M<F; s_m=3.57% (Eq 8) from "
                "C_M=0.1 ASSUMED not measured; fixed-dP swelling claim is unvalidated "
                "in the paper. Solute EXTRACTION coupling (Eqs 9-17, yield/strength "
                "Fig 8, fixed-q insensitivity) is a further layer, NOT built (the "
                "Cameron-duplicating half per card verdict)",
    notes="first concrete kappa(t) backlog candidate: swelling supplies f in "
          "kappa(t)=kappa0 f(eps_b(t)). Nonlinear swelling PDE (u-less spherical MOL) "
          "-> Eq21 porosity -> CK conductivity; reproduces Fig 3a per-powder decay via "
          "the boulder partial-swelling physics (coarse R_c -> slower tau -> less "
          "throttling). t=0 k0 exact (gate_mo2_k0). Distinct from mo2023 arXiv microCT"))

register(Component(
    name="romancorrochano2017.extraction", stage="extraction", kind="runtime",
    paper="Roman-Corrochano, B. 'Advancing the Engineering Understanding of Coffee "
          "Extraction.' EngD thesis, University of Birmingham (2017)", doi="",
    module="puckworks.models.romancorrochano2017.extraction",
    gates=[G.gate_roman_sphere_solver, G.gate_roman_mw_temperature_trends,
           G.gate_roman_bed_flow_trend, G.gate_roman_tamped_kappa,
           G.gate_roman_bed_mpe_parameter_free, G.gate_roman_y0_ceiling_sizeexclusion],
    assumptions="pure Fickian MW-resolved diffusion out of spherical grains; surface "
                "at partition equilibrium C_s(R)=C_b/K (NO dissolution kinetics, "
                "contrast cameron2020); 4 MW classes independent, summed; stirred "
                "(well-mixed bath) + lumped bed (del Valle linear-axial reduction, "
                "L~2 R_bed); no swelling (S=1), no film resistance, no axial dispersion",
    valid_range="microstructural Deff (Table 4.9, 80C) Stokes-Einstein T-corrected; "
                "K(T) Arrhenius lnK=-657/T+1.4 (Table 4.10); dilute limit; solver "
                "VERIFIED vs Crank analytic; MPE 5-8%/<=14% claims stay DATA gates "
                "(raw curves unpublished); per-grind R not on file -> bed absolute EY "
                "needs a d[3,2] adapter (flow TREND gated, not absolute yield)",
    notes="competes with cameron2020.extraction_bdf (both runtime diffusion extraction; "
          "this is pure-Fickian + MW spectrum + parameter-free microstructural Deff, "
          "cameron adds surface dissolution + resolved column). sphere solver vs Crank "
          "max err 1.2e-4; bed mass-conserving <1%; reproduces slower-q->higher-yield "
          "from diffusion. y0 size-exclusion + nested ceiling gated (§5.5, P3 #4)"))

register(Component(
    name="lee2023.feedback", stage="flow", kind="calibration",
    paper="Lee & Smith, 2023 (extraction->porosity->permeability feedback)",
    doi="",
    module="puckworks.models.lee2023.feedback",
    gates=[G.gate_lee_feedback_negative_result],
    assumptions="two parallel pathways, constant total flow; extraction opens "
                "porosity (Eq.3) -> Kozeny-Carman kappa=eps^3/(1-eps)^2 -> reroutes "
                "flow -> feedback from a delta=0.035 seed; alpha=c_sat/rho_c "
                "(Eq.9; Table I 3.76 is a reciprocal typo, see card Errata); "
                "unimodal PSD, no stratification, dissolution Heaviside-capped at "
                "EY_max=33.8%",
    valid_range="Cameron 2020 EK43 g=1.1-2.3; grinder maps t_shot(g)/S(g) fitted "
                "to Cameron; QUALITATIVE fine-grind-dip hypothesis (c) ONLY. The "
                "DECLINE needs an UNPHYSICAL rho_c=798 (2x measured); the physical "
                "rho_c=399 gives only a PLATEAU (documented negative result). Not a "
                "data-fitting component; brings no new data",
    notes="fine-grind-dip mechanism (c) [streamtube channeling / foster wetting / "
          "lee feedback] in docs/P3_hypotheses.md. Reproduces the paper's own "
          "behaviour + failure mode (verification+qualitative): interior EY(g) peak "
          "with fine-side decline at rho_c=798, plateau at rho_c=399; peak weak "
          "(~0.2pp by design, sign gated not amplitude). Backlog: dynamic (extraction) "
          "branch of kappa(t)=kappa0 f(P,eps,E); real payoff is N-tube graft onto "
          "brewer2026.streamtube (card VERDICT: implement-later, effort S)"))

register(Component(
    name="wadsworth2026.inertial", stage="flow", kind="runtime",
    paper="Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026)", doi="10.1098/rsos.252031",
    module="puckworks.models.wadsworth2026.inertial",
    gates=[G.gate_inertial_fo_band, G.gate_inertial_darcy_recovery,
           G.gate_inertial_de1_audit, G.gate_mo_reynolds_overlay],
    assumptions="Forchheimer grad_p=-(mu/k)q-(rho/k_I)|q|q; k_I(k) closures "
                "zhou (eq2.7, reproduces Fo band) & exp (eq2.8, preferred shape); "
                "strict SI k (A7); steady single-phase; k_I never coffee-calibrated",
    valid_range="Fo_F=rho k q/(mu k_I) regime flag; ceramics-fit k_I extrapolated "
                "at tamped-coffee k (DE1 ~7e-15 below fit support); Fo_F not Re (P6)",
    notes="reproduces card band 0.0161-0.0639 (eq2.7); Darcy recovery k_I->inf; "
          "§5.2: DE1 Fo_F~0.86(exp)/5.7(zhou); Mo Re 0.84-3.86 (mo2023 Fig 8a, SPH "
          "conds) now overlaid -- three diagnostics side by side, NOT interchangeable"))

register(Component(
    name="wadsworth2026.grindmap", stage="grind", kind="calibration",
    paper="Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026)", doi="10.1098/rsos.252031",
    module="puckworks.models.wadsworth2026.grindmap",
    gates=[G.gate_grindmap_refit, G.gate_grindmap_polydispersity],
    assumptions="linear dial->radius map <R>=beta*G+R0 (5.805e-5/1.380e-4, "
                "Table-1 refit R2=0.994; card corrected 2026-07-11 from a typo); "
                "S=<R><R2>/<R3>",
    valid_range="Mahlkonig this burr/calibration ONLY; G 1-11, <R> 145-818 um; "
                "grinder-specific, non-portable to EK43/E65S dials (A9/rule 9)",
    notes="one paper with wadsworth2026.permeability; S(G) rises 0.46->0.78; "
          "S formula reconstructs reported S to <3e-3; A9 dial-space adapter stub"))

register(Component(
    name="waszkiewicz2025.poroelastic", stage="bed_dynamics", kind="runtime",
    paper="Waszkiewicz et al., arXiv:2512.21528 (2025)", doi="10.5281/zenodo.18046315",
    module="puckworks.models.waszkiewicz2025.poroelastic",
    gates=[G.gate_waszkiewicz_static_refit, G.gate_waszkiewicz_dynamic_9bar],
    assumptions="quasi-static 1D saturated poroelastic bed; Carman-Kozeny k(phi) + "
                "Hookean strain; Phi(t)=m_d(t)/m0 (all porosity change = dissolution); "
                "empirical m_d(t) sigmoid (RC-3a scope; NOT the RC-3b Cameron coupling)",
    valid_range="Sanremo Zoe rig, one coffee/grind; quantitative only above ~5 bar; "
                "silent on first ~5-10 s; constants per-rig/coffee/grind, not portable",
    notes="static refit == published (P_c,Q_c)=(12.39,1.897); 9-bar Q(t) parameter-free "
          "long-run within ~2% (post-fit: m_d from same rig, soft circularity per card)"))

register(Component(
    name="foster2025.machine_mode", stage="machine", kind="runtime",
    paper="Foster et al., Phys. Fluids 37, 013383 (2025)", doi="10.1063/5.0245167",
    module="puckworks.models.foster2025.machine_mode",
    gates=[G.gate_foster_machine_tp_ts, G.gate_foster_fig15_flowmin,
           G.gate_foster_ct_trajectory],
    assumptions="quadratic pump characteristic + laminar pipe + ideal-gas trapped "
                "headspace; sharp binary front; 3 stages (pre-/post-ponding, post-"
                "saturation); fine grind only; reported times = model + t_shift",
    valid_range="fine grind <300um, DeLonghi EC685 nominal pump; the named A1 "
                "'machine mode' source; validated vs Figs 12-15 CT data",
    notes="t_p=0.823/t_s=6.665; **Fig 15 flow-minimum reproduced** (Q/Qm=0.181 @2s, "
          "RMSE 1e-4) = P2 null baseline; s/H match fitted curves to line width + "
          "bracket 4-5/8 CT points (qualitative-good). Enables RC-3a machine mode"))

register(Component(
    name="foster2025.infiltration", stage="infiltration", kind="runtime",
    paper="Foster et al., Phys. Fluids 37, 013383 (2025)", doi="10.1063/5.0245167",
    module="puckworks.models.foster2025.infiltration",
    gates=[G.gate_infiltration_triangle],
    assumptions="sharp uniform 1D front; binary saturation; pc ~ 0.1 bar "
                "(2% of flat shot, 50% of blooming pause)",
    valid_range="validated on 59 mm basket, 10 g dose, time-resolved CT",
    notes="closed form under recorded P(t); pump/headspace model = backlog"))


# --- G1/G3/G10 reference-strength sourcing (2026-07-12); all calibration,
# reference/qualitative -- NONE closes its gap at independent strength ---
register(Component(
    name="sourcing2026.g1_glassbead_analog", stage="infiltration",
    kind="calibration", paper="Yasuda, Katsuragi, Katsura (2025) arXiv:2501.13361",
    doi="arXiv:2501.13361", module="puckworks.data:glassbead_retention_kr",
    gates=[G.gate_g1_glassbead_closure_sane],
    assumptions="ANALOG spherical glass beads; transfers K_r(S) shape + S_r, NOT "
                "magnitude; valid 0.2<S<0.8",
    valid_range="reference/qualitative; G1 coffee retention search target OPEN",
    notes="Unblocks egidi2018 Richards MACHINERY for P3 hyp#2; validation OPEN."))

register(Component(
    name="sourcing2026.g3_pump_characteristic", stage="machine",
    kind="calibration", paper="Ulka/Repa catalogue; Decent blog; espressoaf",
    doi="", module="puckworks.data:pump_characteristic_ulka",
    gates=[G.gate_g3_pump_envelope_bounds_quadratic],
    assumptions="Manufacturer endpoints only (+/-15%); concave-droop shape; "
                "120V/60Hz; cold-coil",
    valid_range="reference (endpoints)/qualitative (shape); DE1 firmware closed",
    notes="Does NOT replace waszkiewicz2025/brewer_quadratic; independent DE1 "
          "curve = TB bench pull or Decent request."))

register(Component(
    name="sourcing2026.g10_liquor_rheology", stage="flow",
    kind="calibration", paper="Telis-Romero et al. (2000, 2001)",
    doi="10.1111/j.1745-4530.2001.tb00542.x",
    module="puckworks.data:telisromero_viscosity_pas",
    gates=[G.gate_g10_reference_mu_above_water, G.gate_g10_mu_bias_directional,
           G.gate_g10_telisromero_closure, G.gate_g10_telisromero2000_thermal,
           G.gate_g10_telisromero_full_table, G.gate_g10_viscosity_bulk_negligible,
           G.gate_g10_intersource_spread],
    assumptions="Telis-Romero (2001) Eq (10)/(12)/(13) closures now TRANSCRIBED "
                "(T in K, X_w in %w/w water); soluble-coffee extract, NOT espresso "
                "liquor -> unquantified composition bias; espresso TDS sits at/below "
                "the source's dilute end -> mu EXTRAPOLATED toward water; espresso "
                "Newtonian (power-law domain only >36% solids)",
    valid_range="source_curve_reproduction for the extract rheology (closures reproduce the "
                "FULL digitized Table-1 eta / Table-2 K grids within the authors' stated fit "
                "error); espresso application remains extrapolation/compatibility-strength",
    notes="G10 QUANTITATIVELY CLOSED as negligible-at-shot-TDS (card telisromero2001 "
          "Impl-est ii): driving the measured eta(c,T) through cameron2020's in-pore liquor "
          "field, the constant-water-mu Darcy error is <=~3% shot-integrated across the "
          "espresso envelope (mu peaks <=1.05x water; liquor never reaches the <76% X_w "
          "power-law regime) -> NO runtime mu(c,T) hook warranted "
          "(analysis.g10_viscosity_sensitivity). Bulk shot-TDS mu ~= 1.06x water; the old "
          "~1.3-2x envelope guess belongs to concentrated liquor that espresso does not "
          "reach. Do NOT attribute RC-2/RC-3 early-shot bias to bulk mu. INTER-SOURCE: "
          "khomyakov2020 runs ~+37% above TR2001 in the overlap "
          "(gate_g10_intersource_spread); verdict robust -- doubling the mu excess still "
          "gives <=5.3% shot-integrated, no runtime hook."))


# --- evidence_strength (schema v2, WP2) -----------------------------------
# Assigned card-driven from each component's model-card "Calibration and validation offered
# by the source" section, at the WEAKEST DEFENSIBLE tier (never upgrade a claim). Kept in ONE
# auditable block rather than scattered across registrations so the claim list is reviewable.
# Low-confidence calls (see docs/CORPUS_ANALYSIS_PLAN.md) are open to correction before any
# Paper 3 submission.
from puckworks import registry as _R

_EVIDENCE_STRENGTH = {
    "cameron2020.extraction_bdf": "code_verification",
    "brewer2026.streamtube": "within_campaign_held_out",
    "brewer2026.pack_generator": "qualitative_capacity",
    # brewer2026.lb_taichi keeps code_verification but carries NO quick gate: per CLAUDE.md rule 3
    # its 0.003% cross-check to lb_reference is out-of-CI (Taichi is an optional dep; code must
    # import without it). It is recorded as an ACKNOWLEDGED zero-gate exception in
    # paper3.evidence_graph (ZERO_GATE_EXCEPTIONS), not a silent gap.
    "brewer2026.lb_taichi": "code_verification",
    "brewer2026.lb_reference": "code_verification",
    "wadsworth2026.permeability": "source_curve_reproduction",
    "pannusch2024.solver": "post_fit_reconstruction",
    "pannusch2024.closures": "code_verification",
    "grudeva2025.reduced": "post_fit_reconstruction",
    "liang2021.desorption": "post_fit_reconstruction",
    "moroney2016.surrogate": "qualitative_capacity",
    "brewer2026.coupled_kappa_t": "exploratory_synthesis",
    "fasano2000_partI.fines_migration": "qualitative_capacity",
    "mo2023_2.coupled_bed": "post_fit_reconstruction",
    "mo2023_2.swelling": "source_curve_reproduction",
    "romancorrochano2017.extraction": "sign_or_compatibility",
    "lee2023.feedback": "qualitative_capacity",
    "wadsworth2026.inertial": "source_curve_reproduction",
    "wadsworth2026.grindmap": "source_curve_reproduction",
    "waszkiewicz2025.poroelastic": "post_fit_reconstruction",
    "foster2025.machine_mode": "source_curve_reproduction",
    # Demoted controlled_independent -> sign_or_compatibility (ROADMAP §7.1, 2026-07-16) under the
    # adopted component->gate roll-up policy: the only wired gate (gate_infiltration_triangle) is
    # gate-level sign_or_compatibility — k is from a kappa fitted to the same DE1 shot and the
    # front is driven by that shot's own pressure trace, so the first-drip bracket is a
    # wide-bracket compatibility check on in-sample data, NOT a parameter-free independent result.
    "foster2025.infiltration": "sign_or_compatibility",
    "sourcing2026.g1_glassbead_analog": "qualitative_capacity",
    "sourcing2026.g3_pump_characteristic": "sign_or_compatibility",
    # Promoted sign_or_compatibility -> source_curve_reproduction on 2001 closure intake
    # (ROADMAP 7.1): Eq (10)/(13) now transcribed and reproduce the authors' own Table-1/
    # Table-2 anchors within stated error. Espresso APPLICATION stays extrapolation-strength
    # (composition + dilute-end caveat) -- the tier describes the extract-rheology reproduction.
    "sourcing2026.g10_liquor_rheology": "source_curve_reproduction",
}

# provenance_class is now EXPLICIT (no name-prefix inference in the registry). One auditable
# table, applied here as the authoritative source. published_port unless it is project work.
_PROVENANCE_CLASS = {
    "brewer2026.coupled_kappa_t": "project_synthesis",
    "brewer2026.lb_reference": "project_model",
    "brewer2026.lb_taichi": "project_model",
    "brewer2026.pack_generator": "project_model",
    "brewer2026.streamtube": "project_model",
    "cameron2020.extraction_bdf": "published_port",
    "fasano2000_partI.fines_migration": "published_port",
    "foster2025.infiltration": "published_port",
    "foster2025.machine_mode": "published_port",
    "grudeva2025.reduced": "published_port",
    "lee2023.feedback": "published_port",
    "liang2021.desorption": "published_port",
    "mo2023_2.coupled_bed": "published_port",
    "mo2023_2.swelling": "published_port",
    "moroney2016.surrogate": "published_port",
    "pannusch2024.closures": "published_port",
    "pannusch2024.solver": "published_port",
    "romancorrochano2017.extraction": "published_port",
    "sourcing2026.g1_glassbead_analog": "reference_only",
    "sourcing2026.g3_pump_characteristic": "reference_only",
    "sourcing2026.g10_liquor_rheology": "reference_only",
    "wadsworth2026.grindmap": "published_port",
    "wadsworth2026.inertial": "published_port",
    "wadsworth2026.permeability": "published_port",
    "waszkiewicz2025.poroelastic": "published_port",
}

_names = {c.name for c in _R.components()}
_missing_ev = _names - set(_EVIDENCE_STRENGTH)
assert not _missing_ev, "components missing evidence_strength: %r" % _missing_ev
_missing_prov = _names - set(_PROVENANCE_CLASS)
assert not _missing_prov, "components missing provenance_class: %r" % _missing_prov
for _name in _names:
    _ev = _EVIDENCE_STRENGTH[_name]
    assert _ev in _R.EVIDENCE_STRENGTHS, (_name, _ev)
    _prov = _PROVENANCE_CLASS[_name]
    assert _prov in _R.PROVENANCE_CLASSES, (_name, _prov)
    _c = _R._mutable(_name)
    _c.evidence_strength = _ev
    _c.provenance_class = _prov
_R.finalize_registry()
