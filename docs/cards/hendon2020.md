# Model card: Hendon 2020 Backstory (Chemistry and Coffee)

**Paper/thesis:** Hendon, C. H., "Chemistry and Coffee" (Backstory), Matter 2, 514–518 (2020). DOI 10.1016/j.matt.2020.02.010
**Stage(s):** none (nearest: observables) · **Kind:** n/a
**Status:** proposed → skip

## Scope and mechanism
This is a first-person editorial ("Backstory") accompanying Cameron et al. 2020 in the same issue of Matter — the paper already registered as `cameron2020.extraction_bdf`. It narrates the author's path into coffee science: the water-chemistry work with Colonna-Dashwood (2014–2015), the *Water For Coffee* book, barista competitions, and the origin of the Cameron collaboration. It contains no governing equations, no new measurements, and no model. The only quantitative artifact is Figure 2, an empirical "ideal/acceptable water" region on a plane of divalent cation concentration ([Ca²⁺]+[Mg²⁺], ~0–2 mmol/L) vs. bicarbonate ([HCO₃⁻], ~0–75+ mg/L), reproduced from the 2015 book; the region boundaries are drawn, not tabulated, and no functional form is given.

## Governing equations
None. The essay states the qualitative mechanism only: HCO₃⁻ buffers aqueous pH and thereby suppresses perceived acidity; divalent cations are held to affect extraction via ionic strength (citing Hendon et al., J. Agric. Food Chem. 62, 4947–4950, 2014 — the actual model paper, not uploaded here).

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
|---|---|---|---|
| [Ca²⁺]+[Mg²⁺] "ideal" band | not provided (chart region only, roughly 0.4–1.8) | mmol/L | nominal (empirical chart, boundaries not tabulated) |
| [HCO₃⁻] "ideal" band | not provided (chart region only, roughly <75) | mg/L | nominal (empirical chart) |
| Sulfate benignity threshold | < 250 | mg/L | nominal (asserted, no citation) |

## Calibration and validation offered by the source
None. The chart's success is described sociologically (community adoption, competition results), explicitly framed as identifying a *range* outside which cups are "less desirable" — sensory judgment, no measurements, no error bars. Any validation would live in the cited JAFC 2014 paper (DFT binding energies of flavor compounds to cations), not here.

## Assumptions and validity range
Not applicable — no model is stated. Note the author's own caveat that the *Water For Coffee* first edition contained errors and was withdrawn from print in 2017.

## Interface mapping
Inputs consumed: none · Outputs produced: none.
Water chemistry as a whole would enter puckworks through the extraction stage (dissolution rate constants as functions of ionic strength/alkalinity) or as an observables/sensory kernel — neither is on the current backlog, and this essay provides nothing transcribable toward either.

## Extractable data
Nothing worth transcribing. Figure 2 is a hand-drawn region without tabulated boundaries. Useful pointer only: Hendon, Colonna-Dashwood & Colonna-Dashwood, J. Agric. Food Chem. 62, 4947–4950 (2014) is the primary source if a water-chemistry calibration component is ever wanted.

## Overlaps and conflicts
Companion editorial to `cameron2020.extraction_bdf`; confirms the paper's provenance (Uman et al. Sci. Rep. 6, 24483 grinder PSD data fed the model; Foster adapted the mathematics) but adds no content the registered card lacks. Does not touch any open backlog item. The water-chemistry theme is orthogonal to every registered stage.

## Implementation estimate
Nothing to implement. If water chemistry is ever added to the backlog, start from the JAFC 2014 paper and SCA water standards, not this essay.

VERDICT: skip — editorial companion to the already-registered Cameron 2020 with no equations, no data, and no model; retain only the JAFC 2014 citation as a lead for a hypothetical future water-chemistry component — effort S
