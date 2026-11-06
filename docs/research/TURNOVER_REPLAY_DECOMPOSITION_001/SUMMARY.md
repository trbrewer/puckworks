# Retained liquid/solute decomposition

**All four model/scope combinations have liquid-dominated late increases:
stable +60→100-s liquid contributions rise by +0.109 to +0.260 g/s, while
discharged-solute contributions fall by −0.0195 to −0.00235 g/s.**

Ranges below span the nominal 9/11/13-bar condition means; each cell is a
change in window flow, in g/s.

| Model / scope | Liquid change | Solute change | Total change |
|---|---:|---:|---:|
| A-J1 λ=1 / LOCO | +0.2082 to +0.2442 | −0.01788 to −0.01112 | +0.1971 to +0.2263 |
| A-J1 λ=1 / DESCRIPTIVE_ALL | +0.2122 to +0.2598 | −0.01948 to −0.01129 | +0.2009 to +0.2403 |
| D0 diagnostic / LOCO | +0.1085 to +0.1474 | −0.004404 to −0.002351 | +0.1062 to +0.1430 |
| D0 diagnostic / DESCRIPTIVE_ALL | +0.1105 to +0.1544 | −0.004405 to −0.002352 | +0.1082 to +0.1500 |

Observed beverage changes are **−0.1170, −0.1268 and −0.06561 g/s**, respectively.
For A-J1 LOCO at 13 bar, the liquid change is **+0.2442 [0.2397, 0.2495]** and
the solute change **−0.01788 [−0.01796, −0.01776] g/s**. All twelve late
component pairs retain positive liquid and negative solute pointwise intervals.
The 1,000 paired whole-brew draws are conditional on frozen parameters.

Solute matters more earlier: at 13 bar, LOCO solute contributions to 10→40-s
growth are **+0.1470 / −0.06522 g/s** (A-J1 / D0), then **−0.1291 / −0.06373**
for 40→60 s. The tables retain every condition/time/clock, all three phase splits
and the corresponding pressure-slope decomposition.

All **224 arrays / 2,240 windows** reconstruct #424; maximum window residual is
**3.60×10⁻¹⁴ g/s** against `rtol=atol=1e-12`. No fit or simulation was run.
LOCO combines held-condition fits; DESCRIPTIVE_ALL remains in-sample.

These values favor prioritizing the liquid-flow trajectory in a later model
plan, while retaining solute for earlier phases. They describe the frozen
predictors only: Waszkiewicz beverage observations do not separate the real
puck's water/solids contributions. No mechanism or validation claim follows.
No successor is started.

Data: Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0.
