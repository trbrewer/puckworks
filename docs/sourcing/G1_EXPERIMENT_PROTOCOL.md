# G1 experimental acquisition protocol

## Purpose

Measure the constitutive data required by the repository's Richards-type coffee-bed model:
a saturation-resolved water-retention relation, θ(ψ) or S_e(ψ), and preferably a relative-
permeability relation K_r(S_e) or unsaturated hydraulic conductivity K(S_e).

This protocol is designed to satisfy the acceptance criteria in
[https://github.com/trbrewer/puckworks/blob/main/docs/cards/g1_retention_search_target.md](https://github.com/trbrewer/puckworks/blob/main/docs/cards/g1_retention_search_target.md). A wetting-front-position trace alone is not sufficient.

## Minimum viable design

1. Prepare tamped roasted-and-ground coffee beds at an espresso-relevant PSD and record
   origin/species, roast, age, grinder, grind setting, PSD, dose, bed dimensions, dry bulk
   density and porosity.
2. Measure both a wetting branch and a drainage branch when feasible. Use at least seven
   suction levels spanning near saturation to the dry range, for example 0, 1, 3, 10, 30,
   100 and 300 kPa. Select the final range after a pilot so that θ_r and θ_s are constrained.
3. Use a pressure plate, controlled centrifuge, tensiometer/WP4C combination, or another
   method that reports real suction units. Record equilibrium criteria and equilibration time.
4. Measure gravimetric water content at each state and convert to volumetric water content
   using measured dry bulk density. Preserve the raw masses.
5. Use at least three independently prepared beds per condition. Report uncertainty for both
   suction and water content.
6. Measure saturated hydraulic conductivity on the same bed condition. Prefer direct
   unsaturated conductivity measurements; if K_r is inferred with a Mualem or Burdine closure,
   label it as model-derived rather than measured.
7. Fit van Genuchten and/or Brooks–Corey parameters only after preserving the raw points.
   Report parameter covariance or bootstrap intervals and goodness of fit.

## Required metadata

Use `g1_retention_measurement_template.csv`. The critical fields are PSD, bulk density,
porosity, roast, water temperature, suction units, branch, replicate and method.

## Acceptance test

The data qualify as an independent coffee prior only when there are multiple real-unit
(ψ, θ) points on a roasted coffee bed with enough metadata to recreate the bed. A particle-
matched inert analog can be useful as a qualitative prior but must not be labeled coffee validation.

## Current literature status

The 2025 infiltration study explicitly used a binary wet/dry sharp-front model and states
that continuous saturation would require permeability–saturation and capillary-pressure–
saturation measurements not then available:
https://pubs.aip.org/aip/pof/article/37/1/013383/3332668/Dynamics-of-liquid-infiltration-into-an-espresso
