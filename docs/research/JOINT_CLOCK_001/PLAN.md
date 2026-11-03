# PW-JOINT-CLOCK-001 — joint flow, breakthrough and scale clocks

**Owner-approved execution, including low-weight and scoring-step amendments.** G1 retrospective capability study; TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED. Does joint calibration improve held-out detector onset while retaining useful flow accuracy versus a same-objective no-delay control? Python only; no CFD, new bands or gates.

**Evidence/folds.** Reuse [D0](../PRESSURE_PEAK_STAGE_D0/PLAN.md), [screen #411](https://github.com/trbrewer/puckworks/pull/411) and FORM_A's authenticated `waszkiewicz2025/traces_per_brew`: 56 brews/eleven conditions, Zenodo 18046315 (CC-BY-4.0). Planning reads artifacts/helpers; underlying source/native files were inspected in #411. Each ordinary LOCO fold excludes condition h entirely; one vector plus fixed-bank training-derived Mc_h serves every training/held-out brew. DESCRIPTIVE_ALL stays separate. No held-out mass/TDS drives predictions.

**Models/clocks.** With P=max(raw line pressure,0) in bar, a in g/s/bar, masses in g and times in s:

$$
C_A(P)=aP_d[1-e^{-(P/P_d)^n}]e^{-P/P_\star},\quad R(M)=e^{-e^{-M/M_c}};
\quad M=q_{bed}=0\ (t<t_b),\quad \dot M=q_{bed}=C_A(P)R(M)\ (t\ge t_b),\ M(t_b)=0.
$$

| Model | Fitted parameters and wetting |
|---|---|
| D0 replication | Replay saved flow-only fits/Mc with original conventions, M(0)=0; no refits. Historical endpoint/trace 0.153001/0.254185 g/s; separate FORM_A-primary trace ≈0.267630. |
| J0 joint control | Four: a, Pstar, n, Pd; t_b=0, fresh fully wet bed, zero dissolved solute. Same joint objective as J1/J2. |
| J1 | Five: four flow parameters plus τ0=t_b. Chosen W1 trajectory x_f/L=√(t/τ0), capped at 1; τ0=0 uses J0's initial state. |
| J2 | Seven: four flow parameters plus k_w0, Pw, t_s; front defined below. |

$$
\frac{x_f^2(t)}{L^2}=\min\!\left(1,\frac{2}{\phi\mu L^2}\int_0^t k_{w0}e^{-P(s)/P_w}10^5P(s)\,ds\right),\qquad
\int_0^{t_b}k_{w0}e^{-P(s)/P_w}10^5P(s)\,ds=\phi\mu L^2/2.
$$

Use #411's fixed 1D R0 release/storage/transport (0.15/s, 180 kg/m³, diffusivity 10⁻⁹ m²/s, unchanged inventory/geometry/viscosity); carry dissolved mass/inventory through breakthrough. Chemistry retains engineering assumptions. B_bed=M+M_solute,out. J2: B_scale(t)=B_bed(t−t_s), q_scale,liq(t)=q_bed(t−t_s), both zero before the delayed signal; other arms t_s=0. Pressure/wetting/chemistry/recovery retain original absolute times; detector/scored flow use scale signals. t_s is a **fitted scale lag; physical mechanism unidentified**; delaying water arrival/bed outflow is a different model. D0's added beverage observer uses J0's fresh-bed convention, separate from historical replication.

**Joint criterion/support.** For training condition groups I_c, with fixed masks m_ij:

$$
J_\lambda=\frac1{N_c}\sum_c\frac1{|I_c|}\sum_{i\in I_c}\left[\frac{\sum_jm_{ij}(q_{scale,ij}-q^{obs}_{ij})^2/\sum_jm_{ij}}{0.437^2}+\lambda\frac{\ell_i}{4.534^2}\right].
$$

Primary λ=1; predeclare/fit/report 0.05, 0.5 and 2, without held-out weight selection. A censored 1-bar brew contributes ≈258 before λ, versus flow terms ≈0.05–1; λ=0.05 exposes this tradeoff. Flow uses D0's observed-onset+2-s through clean-end support, 0.5-s grid, duration normalization; masks never use predicted onset. Composite criterion on shared histories, not independent likelihoods; sigmas normalize, not estimate noise. SUMMARY reports both loss components by pressure for each weight and whether 1-bar detection changed.

Detector: original timestamps, stable-pressure baseline, beverage-mass differentiation/B0c 31-sample filter; strict mass>0.5 g/flow>0.1 g/s sustained ≥2 s, interval-start onset, 0–100 s window. Detected ℓ_i=(pred−obs)²; valid non-detection ℓ_i=max(0,c_i−obs)², c_i=latest original t_j with T_last−t_j≥2 s. Cover fixed flow/detector support; missing coverage stays unavailable, never shortening censoring or extending terminal mass. Retain intended/available/detected counts and all-brew medians/bounds.

**Search/compute.** Domains: a∈[0.001,20], Pstar∈[0.5,100], n≥1, Pd∈[0.1,100]; k_w0∈[10⁻¹⁶,10⁻¹²] m², Pw∈[0.5,30] bar, τ0,t_s∈[0,100] s. Powell multistart in log positive scales, n and time/100 handles sampled/partly flat loss. Use matching-fold historical flow/timing combinations plus 16 deterministic space-filling starts (seed 20261103; n starts [1,8], no upper fit bound); no cross-fold/full-cohort seeds. Freeze before scoring; retain competing solutions, boundaries, detections and weakly identified delay/flow tradeoffs. **3 models × 4 weights × 12 training sets =144 fits plus D0 replay, no D0 refits.** Use 256 cells, 0.02-s fitting; all reported scores use frozen parameters re-evaluated at 0.005 s. Show 0.02-s scores alongside, largest detector-onset and flow-RMSE changes. Estimate tens–hundreds of core-hours; record actuals, no runtime caps.

**Outputs/interpretation.** One-page numbers-first SUMMARY; per-brew/pressure endpoint/primary/companion flow RMSE on FORM_A masks, onset RMSE/bounds, signed detector-median errors/counts (1/2 bar separately), supplementary 3.5–13-bar median RMS suppressing within-condition variation. Re-score B1, D0, W0/W1/W2/W2T and joint models together. J2 bed/scale diagnostics; fold fits/identifiability, losses, verification, figures, hashes/core-hours. Reuse bands, mean-of-condition-RMSE aggregation and 1,000 identical condition/brew draws (seed 20261103): J1−J0, J2−J0, J2−J1, separate D0 contrasts; intervals conditional on fitted parameters/fixed Mc, bound differences labeled; no refit bootstrap. Per model/weight: one DESCRIPTIVE_ALL 23-pressure/100-s sweep, separate front/detector/finite-time-flow extrema, grid ties/boundaries/unidentified minima; Pw is not the detector minimum. Success supports only “this coupled model improves held-out flow/onset capability on the same retrospective cohort.” Scale lag stays observational. “Remaining low-pressure failure would show that this coupled model, under its fixed recovery and observation assumptions, still does not explain the cohort.”
