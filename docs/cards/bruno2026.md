# Model card: Bruno 2026 coffee-roasting kinetics

**Paper:** Bruno, Egidi, Fatone, Giacomini, Maponi, Sagratini, Santanatoglia & Trebović,
"A preliminary model to establish a digital twin for coffee roasting,"
Sci. Rep. 16, 15857 (2026). DOI 10.1038/s41598-026-43923-9
**Stage(s):** none native — roasting is UPSTREAM of the registry; nearest touch-point is
the extraction solute inventory (offline provider only) · **Kind:** calibration (would-be provider)
**Status:** card-only (out of registry scope as a runtime component; the chemistry table
is the only piece worth ingesting)

## Scope and mechanism
Bean-averaged chemical-kinetic model of coffee *roasting* (not brewing). Tracks 12 species
plus an OTH sink through a connected reaction network (their Fig. 1): thermal degradation,
sucrose inversion, caramelisation, Maillard and Strecker reactions. Each unimolecular step is
first-order, each bimolecular step second-order, with all 15 rate constants temperature-driven
by an Arrhenius law over a prescribed bean-temperature profile Tb(t). The network is deliberately
mass-conserving via OTH: only two measured precursor→product couplings are physical
(SUC→FRU+GLC, CGA→FA) and one Maillard product is broken out (AA); everything else drains to
the sink. Calibrated to end-of-roast composition of four single-origin coffees; produces the
whole-roast concentration trajectory. It is the pre-grind chemistry step, and does not model
grind, packing, flow, or extraction.

## Governing equations
State vector (their notation): CF caffeine, TA tartaric, AA acetic, CA citric, TR trigonelline,
CGA chlorogenic-acid pool, FA ferulic, LP lipids, SUC sucrose, FRU fructose, GLC glucose,
FAM free amino acids, OTH sink. ODE system on I=[0,τ] in seconds (Eqs. 15–27), transcribed:

```
(15) d[CF]/dt  = -k1[CF]
(16) d[TA]/dt  = -k2[TA]
(17) d[SUC]/dt = -(k3+k4)[SUC]
(18) d[FRU]/dt =  k3[SUC] - k5[FRU][FAM] - k6[FRU] - k7[FRU][FAM]
(19) d[GLC]/dt =  k4[SUC] - k8[GLC][FAM] - k9[GLC] - k10[GLC][FAM]
(20) d[AA]/dt  = 2k7[FRU][FAM] + 2k10[GLC][FAM]
(21) d[CA]/dt  = -k11[CA]
(22) d[TR]/dt  = -k12[TR]
(23) d[CGA]/dt = -k13[CGA]
(24) d[FA]/dt  =  k13[CGA] - k14[FA]
(25) d[LP]/dt  = -k15[LP][FAM]
(26) d[FAM]/dt = -k5[FRU][FAM] - k7[FRU][FAM] - k8[GLC][FAM] - k10[GLC][FAM] - k15[LP][FAM]
(27) d[OTH]/dt =  k1[CF] + k2[TA] + 2k5[FRU][FAM] + k6[FRU] + 2k8[GLC][FAM]
                + k9[GLC] + k11[CA] + k12[TR] + k14[FA] + 2k15[LP][FAM]
```

Temperature dependence, Arrhenius (Eq. 29) and the reparametrised form actually integrated
(Eq. 36):

```
(29) k_i(T)   = α_i · exp(-Ea,i / (R·T))
(36) k_i(T)   = kref_i · exp[ -(Ea,i/R)·(1/T - 1/Tref) ],   α_i = kref_i · exp(Ea,i/(R·Tref))  (37)
```

with T = Tb(t). Mass conservation is exact by construction: dMtot/dt = 0 (Eq. 28), Mtot(0)=100.
The factors of 2 in Eqs. (20), (27) are the authors' own words "introduced solely for mass-balance"
— they are stoichiometric bookkeeping to close OTH, not measured stoichiometry. Note (26) omits
k6, k9 because caramelisation (FRU/GLC→OTH) consumes no FAM.

## Parameters
Thirty free parameters per coffee (15 kref + 15 Ea), fit separately for each of four origins.

| symbol | value | units | source |
|---|---|---|---|
| kref_i, i∈{1,2,3,4,6,9,11,12,13,14} (1st order) | 1.0e-5 – 8.3e-2 across origins (Table 6) | s⁻¹ | fitted |
| kref_i, i∈{5,7,8,10,15} (2nd order) | 1.0e-6 – 1.0e-3 across origins (Table 6) | (% w/w)⁻¹ s⁻¹ | fitted |
| Ea,i, i=1..15 | 48.12 – 145.86 across origins (Table 7) | kJ/mol | fitted |
| Ea bounds [Emin,Emax] | ~40 – 150 | kJ/mol | nominal (van Boekel, ref. 63) |
| kref bounds (1st order) | (0, 0.1] | s⁻¹ | assumed |
| kref bounds (2nd order) | (0, 0.001] | (% w/w)⁻¹ s⁻¹ | assumed |
| Tref | not provided | K | — |
| R | universal gas constant | J mol⁻¹ K⁻¹ | nominal |
| c0 (initial composition) | Table 1 range means, per Arabica/Robusta | % w/w dry | nominal (literature) |
| Mtot(0) | 100 | % w/w | assumed (normalisation) |
| Tb(0) | 25 | °C | assumed |
| multistart count S | 30 | — | nominal |

Fitted-value flag worth recording: several second-order constants sit *on* their bounds in the
optimum — e.g. kref_8 = 1.0000e-6 (Mexico, Nicaragua) at the lower floor, kref_10 = 1.0000e-3
(Nicaragua) at the upper cap. Boundary solutions plus 30 parameters against 8 data are direct
evidence of the non-identifiability the authors themselves flag.

## Calibration and validation offered by the source
Objective is a scale-invariant sum of squared log-residuals over N=8 end-of-roast measurements
(CF, TA, AA, CA, TR, CGA, FA, LP), Eqs. (32)–(33), minimised by MATLAB `lsqnonlin`
(Levenberg–Marquardt, multistart S=30) with `ode15s` + NonNegative for the forward solve.
Temperature history Tb(t) is fixed (pchip interpolation of five markers, Table 3), not fitted.

The problem is explicitly underdetermined: **30 parameters, 8 measurements** — the authors state
θ "is not uniquely identifiable." Validation reported (Table 5) is the relative error at the final
time between simulated and measured composition — i.e. how well the optimiser reproduced the
same 8 points it was fit to. Most species land 1e-8–1e-1; **lipids are the outlier**: 18.25%
(Mexico), 5.79% (Rwanda), 42.48% (Nicaragua), ~0 (Indonesia), attributed to gravimetric-Soxhlet
variability. Mass conservation holds numerically to ~1e-8 (Table 4).

Stated plainly: this is a **circular fit-quality check, not independent validation**. No held-out
species, no held-out coffee, no intermediate-time data. The full concentration trajectories
(Figs. 4–5) are unconstrained model output the authors correctly label "model-based predictions
rather than experimentally confirmed kinetics." Sugar/FAM channels (SUC, FRU, GLC, FAM) are never
measured — initialised from literature and left unvalidated.

## Assumptions and validity range
- **Upstream of the registry.** Roasting is not a registry stage; the model ends where the
  registry begins (a roasted bean). Only "kinematic" chemistry — no heat/mass-transfer PDE, no
  bean geometry, no spatial gradients (authors defer conduction/diffusion to future work).
- Well-mixed single bean-average; one lumped CGA pool; ferulic acid is the only broken-out
  phenolic product.
- OTH absorbs all volatiles, melanoidins, CO₂, niacin, etc.; the model is **silent on** roast
  colour, weight/moisture loss, crack physics, and any speciation inside OTH.
- Two roast profiles only (medium Arabica ~212 °C drop; hard Robusta ~228–230 °C drop),
  four coffees. No coverage of light roasts or other origins.
- Non-identifiable parameter set; boundary-hitting rate constants; end-of-roast-only calibration.
  Parameters are per-coffee curve fits, not transferable constants.

## Interface mapping
Inputs consumed: a roasting temperature profile Tb(t) and a green-bean initial composition —
neither is a registry contract field (MachineState.P_of_t is a *brew* pressure trace, not a roast
thermal history). Outputs produced: an end-of-roast composition vector. No current contract carries
per-species solute chemistry — ShotResultState (EY/TDS/traces) and BedState (k, kappa, porosity)
do not. So there is **no clean interface today**: consuming this would require a new upstream
artifact (a per-species SoluteInventory feeding extraction) that does not exist, and even then the
coupling is an offline calibration chain, never runtime. Adapters needed: essentially a new stage.

## Extractable data
- **Table 2 → INTAKEN 2026-07-12 → `data/bruno2026/bruno2026_roasted_composition.csv`**
  (+ `_wide.csv`), loaders `bruno_roasted_composition` / `_wide`, MANIFEST row
  `bruno2026/roasted_composition`, smoke test. Four roasted single origins
  (Mexico/Rwanda Arabica, Nicaragua/Indonesia Robusta) × {caffeine, 3,5-diCGA, 5-CGA, 3-CGA,
  trigonelline, ferulic, tartaric, citric, acetic [mg/kg]; lipids [% w/w]}, mean ± SD over three
  reps. This is exactly the multi-class acid/alkaloid/lipid inventory the extraction backlog asks
  for, at the roasted-bean level. Data-only (no component); an inventory PRIOR for G6/A4, never
  Bruno-ODE → extraction. **Closes item 0.8.**
- Table 1 → green-coffee literature ranges (Arabica/Robusta) for 12 species (% w/w); secondary
  (not this group's measurements), lower value.
- Table 3 → five roast temperature markers × four coffees; roasting thermal profiles, transcribable
  but not registry-relevant.
- Tables 6–7 → fitted kref, Ea (30 × 4). Low value: coffee-specific, non-identifiable, bound-hitting.
- Availability: "data are available in the manuscript" — no external repository, no released MATLAB
  code. Table 2 is transcribe-from-PDF only.

## Overlaps and conflicts
- **No registered component overlaps** — none of cameron2020, brewer2026.*, wadsworth2026,
  foster2025 touches roasting. This is a genuinely new (and out-of-scope) domain, not a
  lower-fidelity duplicate.
- **Complements, does not compete with, the extraction backlog** ("multi-class solute chemistry
  (acids/sugars/bitter) — makes sensory claims testable"). cameron2020.extraction_bdf uses a single
  lumped per-bed-volume inventory (c_s0 = 118/φ_s); a future multi-class inventory could be *seeded*
  by roasted chemistry like Table 2. But Bruno models solute *formation during roasting*, gives no
  solubility/diffusivity/partitioning, and so cannot by itself parameterise extraction. It is a
  data feeder, not a model to run in the chain.

## Implementation estimate
Do not implement as a component. If ingesting the data: transcribe Table 2 into data/ — effort S,
no dependencies, no gate (it is measured chemistry, self-validating as a reference set). Implementing
the ODE model itself (13-state stiff system + 30-parameter multistart LM fit per coffee) would be
M, but yields a non-identifiable, end-of-roast-only, circularly validated fit with no registry
coupling — not warranted.

VERDICT: data-only — roasting sits upstream of every registry stage and the ODE model is an over-parameterised (30 params / 8 points), author-acknowledged non-identifiable fit validated only against its own endpoints, but Table 2's four-origin multi-class chemistry is transcribable and speaks directly to the extraction multi-class-solute backlog — effort S.
