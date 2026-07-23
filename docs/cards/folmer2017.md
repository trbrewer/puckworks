# Model card: folmer2017 — crema formation/stabilization/sensation (review)

**Paper/thesis:** Folmer B., Blank I., Hofmann T. (2017). "Crema — Formation, Stabilization, and Sensation." Ch. 17 in *The Craft and Science of Coffee* (B. Folmer, Ed.), pp. 399–417. Elsevier Academic Press. DOI: 10.1016/B978-0-12-803520-7.00017-7
**Stage(s):** observables (nominal; also touches infiltration, bed_dynamics) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
A narrative review of espresso crema: (1) formation — CO₂ degassing plus supersaturation/effervescence as pressurized water depressurizes into the cup, with solid/cell-wall fragments as nucleation sites; (2) stabilization — surface-active species (roast-derived 4-vinylcatechol oligomers over green-coffee sucrose esters), lipid-driven destabilization, and Pickering-type stabilization by particles; (3) destabilization — coalescence, Ostwald ripening, drainage; (4) sensation — crema's effect on visual quality expectation, above-cup aroma release, and in-mouth perception. It is descriptive throughout: the authors state repeatedly that mechanisms are not proven and that systematic physico-chemical studies are lacking. No mathematical model is proposed or fitted in the chapter.

## Governing equations
None original to this chapter. The only closed-form relation shown is a re-plotted empirical fit from a secondary source (Navarini et al. 2006), Fig. 17.3:

**(Fig. 17.3)**  W_foam = 2.3969 · c_CO2 − 0.2001,  R² = 0.9073

- W_foam = foam weight [g] (see erratum note below — caption says "foam volume")
- c_CO2 = CO₂ content per gram of roast-and-ground coffee [mg/g]

This is a single univariate linear regression with no mechanistic content, attributed to Navarini et al. (2006), not derived here. It is not a puckworks-implementable component.

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
| --- | --- | --- | --- |
| slope (Fig. 17.3) | 2.3969 | g per (mg/g) | fitted (Navarini 2006, secondary) |
| intercept (Fig. 17.3) | −0.2001 | g | fitted (Navarini 2006, secondary) |
| R² (Fig. 17.3) | 0.9073 | — | fitted (Navarini 2006, secondary) |
| foam density | 0.30–0.50 | g/mL | measured (Navarini 2006, secondary) |
| crema fraction of espresso | ≥10 | vol % | nominal (Illy & Viani 2005, secondary) |
| crema lifetime | up to 40 | min | measured (Dalla Rosa 1986, secondary) |
| total lipids, Arabica / Robusta (per 25 mL) | 45–146 / 14–119 | mg | measured (Petracco 1989; Maetzu 2001, secondary) |
| bubble diameter (Fig. 17.2) | ~100 | µm | measured (single confocal image) |
| oil droplet size | <10 | µm | nominal (Illy & Viani 2005, secondary) |
| cell-wall fragment size | 2–5 | µm | nominal (Illy & Viani 2005, secondary) |
| bubble-rise length | 1.5–2 | cm | nominal (Illy & Navarini 2011, secondary) |
| pH evolution during brew | 7.0→7.5→5.5–5.0 | — | nominal (Fond 1995, secondary) |
| foam-volume gain at 0.07% roasted caffeic acid | >60 | % | measured (Kornas & Hofmann, unpublished) |

No value in the chapter is a primary measurement by these authors except the two unpublished Kornas & Hofmann foam-scan/spiking datasets, which are cited as "unpublished data" and not tabulated.

## Calibration and validation offered by the source
None in the puckworks sense. The chapter validates nothing quantitatively; it summarizes others' findings and states plainly that "results published so far are largely descriptive without proving mechanisms or their relative importance." The strongest quantitative claims (CO₂↔foam-weight linearity R²=0.9073; >60% foam gain from roasted caffeic acid spiking; with-crema vs without-crema aroma traces) are either secondary citations or unpublished figures without underlying tables. Validation strength: descriptive/anecdotal — below even post-fit reconstruction.

## Assumptions and validity range
- Applies to espresso-style crema (pressurized extraction, Nespresso/high-pressure machines) on Arabica and Robusta; explicitly silent on any predictive regime.
- Formation mechanism (CO₂ supersaturation/effervescence) is offered as hypothesis, not established; the authors note the bubble-formation mechanism "has not been investigated in detail."
- No functional dependence given for crema volume, stability, or lifetime on any controllable process variable (grind, dose, pressure profile, temperature) beyond the single CO₂ correlation.
- Silent on: time-resolved crema evolution, coupling to bed hydraulics or extraction yield, any radial/spatial structure, quantitative surfactant→stability relations.

**Erratum flag:** Fig. 17.3 caption reads "foam volume as a function of carbon dioxide content," but the y-axis is labeled "Foam weight (g)." Caption/axis unit mismatch — if this relation is ever wanted, source it from Navarini et al. (2006) directly and confirm whether the ordinate is mass or volume.

## Interface mapping
Inputs consumed: none (no runtime coupling). Outputs produced: none as implemented. Conceptually it describes a *crema/foam observable* (volume, weight, density, stability, lifetime) that would attach to `ShotResultState` or an extended observables contract — but the registry has no such field today and this chapter provides nothing to populate it. Couplings: none. No adapter buildable; there is no model to wire.

## Extractable data
Nothing primary and transcribable. Candidates, all secondary and better sourced elsewhere:
- Fig. 17.3 (CO₂ vs foam weight) → transcribe from **Navarini et al. 2006** (primary), not from this re-plot; resolve the volume/weight caption ambiguity there.
- Fig. 17.7 (foam volume vs time at 0/0.007/0.035/0.07% roasted caffeic acid) and Fig. 17.11 (above-cup volatile ppbV vs time, with/without crema) are curve-only, from Kornas & Hofmann (unpublished) and Barron/Dold respectively; digitizable but low registry value and not this chapter's data.
No raw data or code published with the chapter; the two most interesting datasets are marked "unpublished."

## Overlaps and conflicts
- **No registered component covers crema/foam** — this is genuinely uncovered territory (registered observables backlog lists only temperature effects and measurement kernels; crema is absent). So the chapter neither competes nor complements any existing card; it is orthogonal.
- Adjacent context only: the "transient phase / effervescence on depressurization" narrative touches **foster2025.infiltration** (wetting front) and the machine backlog (pump/headspace, Foster Eqs. 2–7) thematically, but adds no equations either could consume.
- Overlaps **illy2002** (already filed) as another descriptive espresso-science reference; lower quantitative content than most registry cards.
- Surfaces a *potential new observables gap*: "crema volume/stability as a beverage observable" is unmodeled anywhere in the registry. Worth a one-line backlog note, but this chapter cannot satisfy it.

## Implementation estimate
No implementation possible — no model. Effort to build anything from this chapter alone is undefined; any future crema observable would require primary sources (Navarini 2006 for foam↔CO₂; Nunes/Coimbra 1997–1998 for polysaccharide↔stability; Barron 2012 / Dold 2011 for aroma release). Recommend logging a backlog item "observables: crema/foam volume & stability" pointing at those primary papers rather than this review.

VERDICT: skip — qualitative review with no implementable model and no primary transcribable data; every quantitative figure is a secondary citation, and it neither duplicates nor supersedes any registered component (it does flag an uncovered crema observable for the backlog). — effort S
