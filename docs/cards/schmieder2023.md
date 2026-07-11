# Model card: Schmieder 2023 extraction-kinetics DoE

**Paper/thesis:** Schmieder, Pannusch, Vannieuwenhuyse, Briesen, Minceva,
"Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction
Kinetics." *Foods* 12, 2871 (2023). DOI 10.3390/foods12152871 (open access, CC BY)
**Stage(s):** extraction · observables · **Kind:** calibration (empirical data provider; no runtime physics)
**Status:** card-only (data-only verdict — nothing to implement as a component)

## Scope and mechanism
Empirical, phenomenological description of espresso extraction on a Decent DE1
Pro, flow-controlled. For each of trigonelline, caffeine, 5-CQA, and TDS, the
outlet concentration is modelled as a single exponential decay in *cumulative
extracted EC mass* (not time), fit per experiment to six sampled fractions.
Integrating that curve gives component mass in the cup at three brew ratios.
Cup masses are then regressed on flow rate, grinder dial, and temperature by a
full-quadratic response surface (RSM). There is no transport, dissolution, or
bed mechanism: the exponential is a curve, the RSM is a grinder/machine-specific
regression. The scientific payload is the dataset and its trends, not a solver.

## Governing equations
**(Eq. 1) Sample-mass assignment.** Cumulative EC mass assigned to fraction *n*,
placed at the fraction mass-midpoint:

  m_Σ(n) = 0.5·m_n + Σ_{i=1}^{n−1} m_i

m_n = mass of fraction *n* (g); m_Σ(n) = cumulative extracted EC mass (g). (Paper
writes the sum index sloppily as m_n; it is the sum over prior fractions.)

**(Eq. 2) Extraction kinetics (the "model").**

  c(m_Σ) = c₀ · exp(−m_Σ / λ)

c = outlet concentration (mg g⁻¹ EC; g g⁻¹ for TDS); m_Σ = cumulative EC mass (g);
c₀ = fitted start concentration (mg g⁻¹); λ = fitted decay constant (g),
interpretable as a time constant under flow control (m_Σ ∝ t). Fit per experiment
per component.

**(Eq. 3) Cup mass by brew ratio.**

  m_cup^BR = m_Frak.1·c_Frak.1 + ∫_{m_Frak.1}^{20 g/BR} c(m_Σ) dm_Σ,  BR ∈ {1/1, 1/2, 1/3}

First term = measured component mass in fraction 1 (kept discrete because the
exponential is known to misfit the earliest brew); integral accumulates Eq. 2
from m_Frak.1 to the target beverage mass 20 g/BR (= 20/40/60 g).

**(Eq. 4) Response surface (all terms transcribed; eliminated terms → 0 in Table 3).**

  m_cup = β₀ + β₁x_flow + β₂x_grind + β₃x_temp + β₄x_flow² + β₅x_grind² + β₆x_temp²
       + β₇x_flow·x_grind + β₈x_flow·x_temp + β₉x_grind·x_temp

x_flow (mL s⁻¹), x_grind (dimensionless E65S dial), x_temp (°C). β₀ intercept,
β₁–β₃ linear, β₄–β₆ quadratic, β₇–β₉ interaction; fitted by OLS with backward
elimination (α = 0.05) separately for each component × brew ratio.

## Parameters
Eq. 2 fits are per-experiment (15 × 4 components); Eq. 4 coefficients are
per-component × BR. Representative DoE central-point (Exp. 7: F 2.0 mL s⁻¹,
GL 1.7, 89 °C) values below; full sets in the paper's tables.

| symbol | value (central point) | units | source |
| --- | --- | --- | --- |
| c₀ trigonelline | 6.70 | mg g⁻¹ | fitted (Table A1) |
| λ trigonelline | 16.09 | g | fitted (Table A1) |
| c₀ caffeine | 9.71 | mg g⁻¹ | fitted (Table A1) |
| λ caffeine | 23.09 | g | fitted (Table A1) |
| c₀ 5-CQA | 6.79 | mg g⁻¹ | fitted (Table A1) |
| λ 5-CQA | 20.77 | g | fitted (Table A1) |
| c₀ TDS | 0.248 | g g⁻¹ | fitted (Table A1) |
| λ TDS | 17.47 | g | fitted (Table A1) |
| β₀…β₉ (Eq. 4) | per Table 3 | mixed | fitted (Table 3) |
| brew pressure vs grind @ F 2.0 | 9.3 / 7.4 / 3.8 (GL 1.4 / 1.7 / 2.0) | bar | measured |
| Sauter d₃₂ | 28.3 / 26.9 / 29.2 (GL 1.4 / 1.7 / 2.0) | µm | measured |
| De Brouckère vol. mean | 273 / 277 / 295 (GL 1.4 / 1.7 / 2.0) | µm | measured |
| dose | 20.00 | g | nominal (fixed) |
| tamp force | 25 (kg-equiv) | — | nominal (fixed) |

λ ordering (caffeine largest → slowest decay; trigonelline/TDS smallest → fastest)
tracks the paper's polarity argument. No value is invented; where the paper gives
none, none is listed.

## Calibration and validation offered by the source
Weak, and the authors say so. The exponential fits are good as *curve fits*
(adj. R² 0.94–0.996) but that is in-sample fitting, not predictive validation.
The RSM adj. R² is low: 0.41–0.75 overall and only 0.41–0.50 for caffeine; the
authors explicitly restrict conclusions to *qualitative* trends and recommend
mechanistic modelling for quantitative work. No held-out prediction, no external
model comparison, no cross-validation. Reproducibility is good: mean RSD of cup
masses 2.5% (max 8.5%). Cross-study concentration comparison to Angeloni et al.
is order-of-magnitude only (different bean/roast/machine). Treat the RSM as a
data summary of one bean on one machine, not a validated model.

## Assumptions and validity range
- Single system: Colombia Suprema Huila 100% washed Arabica, one roast
  (180→212 °C, first crack 190 °C, ~10 min), 20 g dose, DE1 Pro + IMS basket/screen,
  Acqua Panna water, Mahlkönig E65S. Coefficients are non-transferable off this box.
- Flow-controlled only (1.0–3.0 mL s⁻¹, achieved 0.96/1.9/2.8); fixed 7 mL s⁻¹
  preinfusion until >2.5 bar. GL 1.4–2.0 (only ~7.5% of the E65S scale → near-identical
  PSDs). T 80–98 °C.
- Single exponential in cumulative mass; earliest brew (m < m_Frak.1) known to
  deviate and handled discretely.
- **Silent on:** pressure-controlled brewing; channeling / spatial non-uniformity
  (cited via Lee et al. but not modelled); pre-infusion transient; grinds/doses/beans/
  roasts outside the box; extraction beyond ~60 g (BR 1/3). x_grind is a dial number,
  not a physical PSD.
- **Failure modes:** any extrapolation outside the DoE cube; caffeine RSM barely
  explanatory; no mechanism, so no transfer to other beans/machines/grinders.

## Interface mapping
Not a runtime component. As a calibration/validation source:
Inputs (as labels) ← MachineState (constant flow ~1–3 mL s⁻¹, measured P 2.6–9.3 bar),
GrindState (dial + measured d₃₂), temperature; grind→BedState only qualitatively
via measured pressure. Outputs (as data) → ShotResultState.traces (concentration
vs cumulative mass, Eq. 2) and per-BR component masses / TDS (Eq. 3). Coupling:
offline data ingest only — no adapter into the shot chain is warranted; forcing
Eq. 4 to runtime would be the mega-model failure mode REGISTRY_STATE warns against.

## Extractable data
- **Table A1** → `data/schmieder2023_kinetics.csv`: c₀, λ + SE for 15 exp × 4
  components (done-able directly from the PDF).
- **Table 2** → `data/schmieder2023_cupmass.csv`: cup masses (trig/caff/5-CQA mg,
  TDS g) × 15 exp × 3 BR with RSD, plus measured F/T/pressure per run.
- **Table 3** → `data/schmieder2023_rsm.csv`: β₀–β₉ + adj. R² per component × BR.
- Scalars: pressure(grind) 9.3/7.4/3.8 bar; flow→pressure at GL 1.4 (2.9→8.0 bar)
  and GL 2.0 (2.8→3.6 bar); Sauter/De Brouckère diameters.
- **Supplementary S1** (raw fraction concentrations, all replicates, fractions
  1/2/3/5/7/10) and S2–S4 (fit params, OriginPro ANOVA): downloadable from MDPI
  (CC BY). Fig. A2 DE1 flow/temp traces. Raw/segmented data otherwise "from
  corresponding author on request."

## Overlaps and conflicts
- **cameron2020.extraction_bdf** — complements, does not compete: much lower
  fidelity, no mechanism, but an independent multi-solute DE1 dataset. Directly
  corroborates Cameron's clogging/"reassembling yield" hypothesis [their ref 43]:
  cup mass peaks at GL 1.7 (non-monotonic in grind) and finer grind drives much
  higher pressure at fixed flow despite near-identical PSD.
- **Backlog → extraction: multi-class solute chemistry** — strongest fit. Four
  tracked solutes with distinct λ give per-species, fraction-resolved kinetics to
  parameterize/test a multi-class model and make sensory-adjacent claims checkable.
- **Backlog → bed_dynamics: pressure/history-dependent permeability**, and the
  Wadsworth↔Cameron tamped-regime reconciliation — the pressure(grind, flow) points
  at fixed 20 g dose are a clean external constraint on kappa(P) / clogging.
- **DE1 fixture A** (registry data) — additional independent DE1 Pro flow/temp
  traces (Fig. A2); complementary fixture.
- **Backlog → observables: temperature effects** — useful *negative* datum: 80→98 °C
  changes the individual kinetics negligibly (confidence bands overlap), with an
  apparent temperature effect appearing only through the flow×temp interaction.

## Implementation estimate
No solver work. Effort is table transcription (A1, 2, 3) plus a handful of scalars
into `puckworks/data/`; open-access CC BY, supplementary downloadable. If Eq. 2 is
ever wanted as a cheap outlet-concentration surrogate, gate on reproducing Table A1
λ within SE and Table 2 cup masses within RSD — but that is a convenience surrogate,
not a physical model. Dependencies: none.

VERDICT: data-only — no transferable mechanism (empirical exponential + machine/grinder-specific RSM), but a clean multi-solute, fraction-resolved DE1 dataset that directly feeds the multi-class-extraction and pressure(grind) backlogs — effort S.
