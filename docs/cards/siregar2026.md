# Model card: siregar2026 — minimal dimensionless moka-pot thermo–fluid ODEs

**Paper/thesis:** Siregar, S. (2026). *A Minimal Thermo–Fluid Model for Pressure-Driven Extraction in a Moka Pot.* arXiv:2601.03663v1 [physics.flu-dyn], 7 Jan 2026. No DOI (preprint).
**Stage(s):** machine · **Kind:** calibration (would be runtime only in a moka-pot chain, which the registry does not have)
**Status:** card-only

## Scope and mechanism

A lumped-parameter, fully dimensionless 3-ODE model of moka-pot brewing: constant heating raises boiler temperature θ, which drives vapor pressure p toward an exponential (Clausius–Clapeyron-inspired) equilibrium e^θ; once p crosses a threshold, liquid flows through the coffee bed at a rate linear in the overpressure, depleting both pressure and thermal energy (negative feedback). Explicitly pedagogical: the author states the model "is not intended for device-specific optimization." No extraction chemistry, no bed physics beyond a single lumped conductance, no espresso-machine content.

## Governing equations

State variables: θ(τ) dimensionless boiler temperature, p(τ) dimensionless boiler pressure, u(τ) cumulative extracted volume normalized by initial liquid volume; τ = t/t₀ with t₀ a characteristic heating time.

- Eq. (1): dθ/dτ = 1 − Bi·θ − Λ·q — heating (unit source), Newton-type heat loss (Bi), convective/latent energy removal by outflow (Λ·q).
- Eq. (2): dp/dτ = Λ(e^θ − p) − Π·q — relaxation of pressure toward equilibrium vapor pressure e^θ at rate Λ, minus pressure depletion by extraction (Π·q). Note the same Λ appears in (1) and (2) by construction ("shared thermodynamic origin"); this is a modeling choice, not derived.
- Eq. (3): du/dτ = q.
- Eq. (5): q = q_max · max(p − 1, 0) — thresholded linear (Darcy-like) flow law; threshold p = 1 lumps hydrostatic head + bed resistance.
- Eq. (4) (pre-extraction reduction, q = 0): dθ/dτ = 1 − Bi·θ — the only piece confronted with data.
- Eq. (6) initial conditions: θ(0) = 0, p(0) = 1, u(0) = 0. (Note p(0) = 1 sits exactly at the flow threshold; flow stays zero only because e^θ(0) = 1 = p initially — a fragile choice the paper does not discuss.)

Nothing simplified away in this transcription; the model is already minimal.

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| Bi (heat-loss coefficient) | 0.15 | – | nominal (Table I, "representative simulations") |
| Λ (vapor–pressure coupling) | 1.5 | – | nominal (Table I) |
| Π (pressure depletion coeff.) | 0.5 | – | nominal (Table I) |
| q_max (max dimensionless flow rate / effective permeability) | 1.2 | – | nominal (Table I) |
| t₀ (characteristic heating time) | not provided as a number | s | fitted to Gianino (2007) heating-stage temperature data; the fitted value is never stated in the text |
| temperature/pressure scales | not provided | K, Pa | implied by nondimensionalization; never given |

Regime plots (Figs. 2–3) vary Bi and q_max across the three regimes but the specific per-curve values are not tabulated.

## Calibration and validation offered by the source

- Heating stage only: Eq. (4) fitted to published moka-pot temperature–time data from Gianino, *Am. J. Phys.* 75, 43 (2007) (Fig. 4). Agreement is described as "good throughout the heating stage up to the onset of boiling"; no RMSE or fit statistics reported, and the fitted t₀ is not stated.
- Prediction: with temperature so constrained, the pressure trajectory (air compression + vapor) crosses the p = 1 threshold at t ≈ 4.3 × 10² s, presented as a no-additional-parameters prediction of extraction onset. It is called "consistent with experimentally observed heating timescales" — but no measured onset time from Gianino or elsewhere is quoted for comparison, so the onset "validation" is qualitative at best.
- The flow/extraction stage (Eqs. 2, 3, 5 with q > 0) is never compared to any measurement. The three regimes (no/smooth/violent extraction) are simulation-only.

Net: one fitted scalar against one digitized legacy temperature curve; everything downstream is verification-only/illustrative. The authors are candid about this.

## Assumptions and validity range

- Moka pot only: vapor-pressure-driven, ~1–2 bar class, threshold-onset flow. Not applicable to pump-driven espresso (9 bar imposed profile) — the driving physics is inverted (espresso imposes P(t); here P is a state emerging from heating).
- Lumped (0-D): no spatial temperature gradients, no two-phase flow, no bed depth resolution.
- Linearized flow law; permeability constant in time (no compaction, swelling, or fines migration).
- Vapor pressure as e^θ is a leading-order caricature of Clausius–Clapeyron; valid only near the nondimensionalization point.
- No extraction chemistry at all — "extraction" means extracted liquid volume, not solubles; EY/TDS are outside the model's vocabulary.
- p(0) = 1 initial condition is on the flow threshold (see above); behavior near τ = 0 depends on this coincidence.
- Silent on: end-of-shot behavior when the boiler empties (no liquid-inventory state), steam breakthrough/sputter phase (the characteristic end of a moka brew), bed temperature, and any dependence on grind or dose.

## Interface mapping

Inputs consumed: none of the registry contracts map cleanly. The bed appears only as the scalar q_max, a degenerate compression of BedState(k, depth, area) plus hydrostatic head into one lumped conductance.
Outputs produced: nothing a ShotResultState needs — u(τ) is volume, not EY/TDS; p(τ) is boiler pressure of a device the registry does not model.
Couplings: none available. Superficially adjacent to the machine backlog item ("pump characteristic + headspace, Foster Eqs. 2–7"), but foster2025's machine mode models a vibratory pump + compressible headspace feeding an imposed-pressure espresso chain; this models a sealed boiler generating its own pressure by heating. An adapter would amount to writing a different model. No runtime or calibration chain into puckworks exists.

## Extractable data

- None original. Fig. 4's experimental symbols are digitized from Gianino (2007); if a moka stage ever existed, the primary source to transcribe would be Gianino, not this paper. Table I is nominal illustrative parameters, not data.
- No code or data published; no availability statement.

## Overlaps and conflicts

- foster2025.infiltration / foster2025 machine backlog (Eqs. 2–7): different device, different causality (imposed vs. emergent pressure). Not competing, not complementing — orthogonal.
- cameron2020.extraction_bdf, brewer2026.*: no contact; this paper has no extraction kinetics or bed microstructure.
- King (2008) *Am. J. Phys.* 76, 558 — cited by the paper as the dimensional, physically grounded moka-pot analysis this model reduces. If the registry ever wanted moka-pot physics, King 2008 (and Navarini 2009, Appl. Therm. Eng., for measured steam-pressure extraction data) would supersede this card as intake targets.
- No conflicts with any registered component or open backlog item; no backlog gap is addressed.

## Implementation estimate

Trivial to implement (4 ODE lines, SciPy solve_ivp, tolerances stated in the paper) — but there is nothing in the registry for it to connect to, no espresso-relevant parameter it could calibrate, and no original data to hold. Out of device scope.

VERDICT: skip — pedagogical dimensionless moka-pot model with no espresso applicability, no original data (temperature curve is Gianino 2007's), and no contract it can produce or consume — effort S
