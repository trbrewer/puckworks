# Model card: Barbro 2025 — vendor CFD visualization of puck flow

**Paper/thesis:** Barbro Coffee, "How water flows through the puck: pressure and speed," vendor blog post, 21 Feb 2025. No DOI; not peer-reviewed; marketing content for the Barbro tamper and a "variable, perfectly cylindrical sieve" product.
**Stage(s):** flow (qualitative only) · **Kind:** calibration (nominally; in practice neither — nothing transferable)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model in any implementable sense. A prose-and-pictures summary of an unnamed CFD simulation of single-phase water flow through an espresso puck with perfectly homogeneous porosity, homogeneous inflow from above, and a standard basket hole pattern (holes ringed inside the screen perimeter). Three qualitative claims: (1) the axial pressure drops from 10 bar absolute at the puck top to atmospheric at the filter exit, so most of the bed sees far less than gauge pressure; (2) "dead zones" of weak flow form at the outer corners of the basket because the hole ring is smaller in diameter than the screen, and these cannot be removed by preparation; (3) an annular ("donut") high-velocity flow concentrates at the outermost hole ring, with the same local acceleration pattern repeating between individual holes. A closing paragraph notes that CO₂ outgassing in the low-pressure lower puck accelerates real flow fields beyond what the simulation captures.

## Governing equations
None stated. No solver, mesh, porous-medium closure (Darcy vs. Forchheimer vs. resolved), permeability value, boundary-condition specification, or software named. The figures (axial pressure field 0–10 bar colormap, velocity-vector slice near the exit, plan-view velocity field showing the edge deficit) are renderings without axes, scales beyond the pressure colorbar, or extractable profiles. Nothing to transcribe or implement.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| inlet pressure (absolute) | 10 | bar | nominal (implies 9 bar gauge) |
| outlet pressure | atmospheric | — | nominal |
| puck permeability / porosity | not provided | — | — |
| puck dimensions, basket hole geometry | not provided | — | — |
| flow rate / velocity scale | not provided | — | — |

## Calibration and validation offered by the source
None. No comparison to measurement of any kind; the post itself concedes the simulation is an "ideal case" and that real flow (CO₂-laden, two-phase in the lower puck) is "very difficult to depict with models." All claims are simulation-internal and uncheckable from the material given.

## Assumptions and validity range
- Perfectly homogeneous porosity, homogeneous top inflow, presumably rigid bed, single-phase water — the post states these explicitly as idealizations.
- Silent on everything quantitative: puck depth, dose, grind, permeability, flow rate, temperature, transient vs. steady state, whether consolidation or saturation is modeled.
- The 10-bar-absolute vs. 9-bar-gauge distinction is stated correctly but is exactly the pressure-node convention hazard already tracked in the ROADMAP convention table; the post adds no new resolution.
- The "dead zones cannot be prevented by tamping or any other type of preparation" claim is a strong universal drawn from one idealized simulation; ribes2020's bottom-paper-filter intervention (outer-zone EY 13 → 22%) empirically contradicts its absoluteness — outlet-side interventions do mitigate the edge deficit.

## Interface mapping
Inputs consumed: none. Outputs produced: none. No contract fields populated; no adapter meaningful. The physical claim it gestures at — exit-boundary hole layout shaping the radial flow/extraction field — is the G9/outlet-boundary thread, but this source supplies neither geometry nor resistance numbers for it.

## Extractable data
Nothing. No tables; figures are unscaled renderings not worth digitizing. No code, no data, no simulation details available; vendor is unlikely to release the CFD setup (available-on-request not offered).

## Overlaps and conflicts
- **ribes2020 / ribes2021 / pocketscience2024 (superseded qualitatively by them):** the edge-deficit / outer-ring under-extraction picture is already on file with actual radial EY measurements; this post adds only an unquantified CFD illustration of the same mechanism, minus the empirical caveat that outlet-side interventions flatten the profile.
- **schulman2011_baskets / mckeonaloe2022 (complemented by them, not vice versa):** those cards carry the real basket exit-geometry data (hole ring diameter vs. screen diameter is exactly the quantity behind claim 2); this post has none.
- **gap G9 (motivational only):** restates the exit-boundary-matters framing already established; no resistance or geometry contribution.
- **perticarini2024_3d §4.3 (compete, both weak):** that solver is the shape a real G9/outlet-flow component would take; this post is a rendering of the same physics with even less to extract.
- **ROADMAP pressure-node convention table (consistent):** absolute-vs-gauge statement matches the existing convention entry; no conflict.

## Implementation estimate
Nothing to implement, transcribe, or gate. If ever cited, cite only as a qualitative illustration of exit-hole-ring flow concentration, with the ribes2020 counterexample attached to its "unpreventable dead zones" claim.

VERDICT: skip — vendor marketing prose around an unspecified, unvalidated CFD run whose every qualitative claim is already on file with quantitative backing (ribes/pocketscience for the edge deficit, schulman/mckeonaloe for exit geometry), and with zero extractable numbers — effort S.
