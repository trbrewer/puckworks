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
| `fig8_6_asymptotic_q_vs_p0.csv` | Fig 8.6 | MODEL asymptotic q∞(p₀) for β₁,β₂ (μ=0.5), Suski simulation | verification of digitized model output |
| `fig8_7_thresholds.csv` | Fig 8.7 | the β₁(q), β₂(q) detachment-threshold shapes fed to Fig 8.6 | input |

## Scope note — NOT a model twin
The model's constitutive closures **K(b,m), M, γ are unspecified** in the paper
(card Parameters: "not provided"). Fig 8.6 is Suski's free-boundary simulation
with particular unpublished closure choices. A faithful reproduction of the
curve is therefore impossible without inventing those closures — the same
theory-paper wall as fasano2000_partII (deferred). The full 3.3 free-boundary
component stays **implement-later**; it will require choosing/fitting K, M, γ
(DE1 fixture flow traces are the intended source).

What IS faithfully checkable (and gated): the paper's **Corollary 8.2** proves
nonmonotone q∞(p₀) *requires* the flow to cross the β(q) threshold, so the peak
of q∞(p₀) in Fig 8.6 must sit at the flow where β(q) drops steeply in Fig 8.7.
`gate_fasano_cor82_nonmonotone` verifies exactly that cross-figure structure —
no closures invented.
