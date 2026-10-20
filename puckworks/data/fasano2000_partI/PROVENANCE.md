# fasano2000_partI — digitized figures (ROADMAP 0.12 / 3.3)

Source: Fasano, Talamucci & Petracco, "The Espresso Coffee Problem," ch. 8 in
A. Fasano (ed.), *Complex Flows in Industrial Processes*, Springer (2000),
pp. 241–280. No DOI; no code or tabulated data published.

All four files are **raster digitizations of schematic book figures** — low
fidelity (the authors' own redrawings of sensor traces / simulation outputs),
suitable for qualitative and structural gates ONLY.

| file | figure | what it is | strength |
|---|---|---|---|
| `fig8_1_discharge_vs_pressure.csv` | Fig 8.1 | EXPERIMENTAL discharge q(t) at 3/5/7 bar (illycaffè) | qualitative (experimental, schematic) |
| `fig8_4_direct_inverse.csv` | Fig 8.4 | direct/inverse chamber discharge, 3 segments (reversal test) | qualitative |
| `fig8_6_asymptotic_q_vs_p0.csv` | Fig 8.6 | MODEL asymptotic q∞(p₀) for β₁,β₂ (μ=0.5), Suski simulation | qualitative source-figure description |
| `fig8_7_thresholds.csv` | Fig 8.7 | the β₁(q), β₂(q) detachment-threshold shapes fed to Fig 8.6 | input |

## Current scope — three separate evidence roles
The model's constitutive closures **K(b,m), M, γ are unspecified** in the paper
(card Parameters: "not provided"). Fig 8.6 is Suski's free-boundary simulation
with particular unpublished closure choices. A faithful reproduction of the
curve is not established with the available constitutive inputs. The historical
proposal was to identify closures from flow traces; that proposal is not a
completed fit. A Fasano-structured free-boundary implementation now exists with
**project-chosen closures**, distinct from the unpublished source parameterization.

- `gate_fasano_cor82_nonmonotone` reduces Fig. 8.6 source-model outputs and
  Fig. 8.7 threshold inputs without executing the solver. Each response has a
  sampled maximum strictly inside the represented pressure range, a lower
  preceding discharge, and a final discharge more than **0.005** below the
  maximum. This inherited descriptive coordinate screen is not an uncertainty
  estimate, theorem requirement, model-accuracy tolerance or physical-admission
  threshold. beta2 peaks at lower represented pressure than beta1; this is an
  observation, not a causal inference from threshold ordering. Tail rebounds
  are allowed (beta2 rises from 0.114 to 0.121 after its maximum of 0.153).
  Threshold nonincrease is checked on every retained interval, with a net drop;
  the steepest-segment bounds and midpoint are reported separately.
- `gate_fasano_freeboundary` executes the existing solver and checks its mass
  balance (<1%), boundary bound, temporal sign and sampled pressure response
  with project-chosen closures. It does not reproduce the source curve.
- `gate_fasano_reversal_signature` reduces the Fig. 8.4 experimental trace;
  it does not simulate chamber reversal.

The gate's `cor82` name is historical: it does **not** verify Corollary 8.2 or
any peak-at-threshold-knee relationship. The card records a necessary finite-time
condition involving the evolving **b − β(q)** and pressure-dependent scaling.
Neither static figure establishes that condition or compatible cross-figure
normalization. A steepest-segment midpoint is sampling-dependent, not an exact
physical transition. These model-output/input tables are not independent
espresso measurements.

Source inspection for this correction: **original passage not independently
rechecked**. The configured family locator supplies these four CSVs and the
retained provenance, not the chapter; the publisher's chapter page offers
subscription access. The card's qualified mathematics is retained.
See [correction and superseding interpretation](../../../docs/analysis/fasano_gate_correction.md)
for identities, arithmetic, source-access limits and the P2 consequence.
