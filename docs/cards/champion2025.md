# Model card: Champion 2025 — Decent V2 grouphead design history (headspace, water distribution, materials)

**Paper/thesis:** B. Champion, "Designing the V2 Grouphead parts," Decent Espresso blog, 5 parts, created 2025-02-27 (updated 2026-02-05). No DOI; vendor source (author is Decent's lead product designer); narrative post with photos and two embedded community slides.
**Stage(s):** machine (grouphead geometry/headspace context), observables (anecdotal taste/EY commentary) · **Kind:** calibration (provenance metadata only — no model, no dataset)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model. A design-history narrative of the DE1 grouphead's evolution (v1.0 → v1.1 → "V2"): headspace/protrusion choices, shower water-distribution patterns, and shower/inner-block material selection (brass → Ultem → PPS). Two testing campaigns are described (14 shower variants S1–S14; then 2 grouphead designs × 14 screens over center/mid/outside distribution patterns × 2 headspaces), evaluated almost entirely by taster preference, with the author explicitly noting that shot-to-shot taste variability swamped individual design changes. The one quantitative slide shown (Stéphane Ribes's radial extraction bar charts, 13–25% EY normal puck vs. 22–25% with filter paper) is the ribes2020 dataset, already registered. The mechanism-relevant conclusions are directional: outside-preferential inlet flow chosen (motivated by the Ribes edge-deficit data), E61-equivalent headspace adopted, user-selectable via screen swap.

## Governing equations
None anywhere in the post. The S1–S14 design chart (page 6) is a schematic of protrusion/gap profiles with no legible dimensions; the flow simulations mentioned for the original design are referenced but not shown.

## Parameters
No model parameters. Hardware/provenance scalars transcribed inline (per house rule for vendor sources — no data/ file):

| quantity | value | units | source |
|---|---|---|---|
| V2 protrusion vs. DE1 v1.1 ("current") design | +1 (i.e., −1 mm headspace; stated E61-equivalent) | mm | nominal |
| IMS SI200 vs. CI200 screen protrusion delta | +2.0 (−2 mm headspace) | mm | nominal |
| Absolute V2+CI200 protrusion | not provided here; 9.6 mm for the "S22A Ultem prototype + CI200" per ribes2021 — treating that as the V2 geometry is an `[RS inference]`, plausible (S22A implements the two-screen compatibility) but unconfirmed |  mm | — |
| DE1 v1.0 headspace | "misjudged" (too large); value not provided | — | — |
| Stress-test pressure cycling | ~7,500 cycles/day, 0 → 13 → 0 bar; 935,000 cumulative on test units | cycles, bar | nominal |
| Stress-test thermal cycling | ~750 cycles/day, ~40 → 90 °C | cycles, °C | nominal |
| Blind (no-hole) stainless basket fatigue failure | ~100,000 pressure cycles, edge crack | cycles | measured (anecdotal n=2 shown) |
| Final material | PPS ("technopolymer"); long-term service >200 °C, low water absorption | — | nominal (datasheet claims, values not given) |

Material-selection lineage (all qualitative): brass baseline → Ultem (better taste at identical geometry/headspace `[uncontrolled taste claim]`, stays clean, cracks) → GF-Ultem (warps) → PEEK (fouls) → PTFE (clean-ish, stains, bends) → PPSU (very clean, cracks) → PVDF (written "PDVF" in source — typo flagged; clean, warps) → PPS (clean, dimensionally stable; adopted).

## Calibration and validation offered by the source
Essentially none in a registry sense. Taste panels with self-acknowledged confounds ("natural shot-to-shot variations can overshadow the effects of individual modifications"); no EY tables, no n, no statistics, no pressure/flow traces. Findings reported: no preference winner across the S1–S9 protrusion/gap sweep (testers split between the extremes S1 and S9); S10 experimental design "consistently showed promise"; typical other-machine showers S11/S12 clearly worse than the Decent brass design; outside-preferential distribution preferred by all testers in round 2, consistent with Ribes's radial data; no winner between the two round-2 headspaces; Matrix E61 screen underperformed on the DE1 (author speculates it needs higher flow rates); IMS DR305 ≈ center-screw design; standard E61 screens have a manufacturing flaw (two edge holes → poor initial wetting/edge leakage). Thermal-camera even-heating test: PPS shower surface more uniform in temperature than brass, E61 design best — video frames only, no temperature table.

## Assumptions and validity range
- Single machine platform (DE1), single vendor's design space; all preference results are taste-panel anecdotes with unknown n and no blinding described.
- The headspace conclusions are explicitly unresolved by the source itself ("There may not be an optimal headspace for all users") — do not cite this post as evidence for any headspace–EY relationship.
- Material taste claims (Ultem > brass at identical geometry) are uncontrolled; mechanism unknown (author attributes to temperature accuracy, via a linked video not in this PDF).
- Silent on: every quantity puckworks simulates — no PSD, permeability, pressure, flow, EY, or TDS numbers of its own.

## Interface mapping
Inputs consumed: none. Outputs produced: none. Offline value only:
- **Machine backlog (Foster Eqs. 2–7 headspace term H₀):** the protrusion lineage gives the headspace-volume provenance for DE1 datasets — v1.0 (large headspace), v1.1 (reduced), community spacer kits (further reduced, aftermarket), Ultem prototypes (S22A + CI200 = 9.6 mm protrusion per ribes2021), V2 + CI200 (E61-equivalent), V2 + SI200 (+2 mm). Any cross-dataset comparison of DE1 early-shot transients or W_dead should record which grouphead generation produced the data; the fleet is heterogeneous over 2017–2025.
- **Inlet-distribution context:** V2 hardware bakes in outside-preferential flow; radial-EY findings from pre-V2 hardware (pocketscience2024, ribes2020/2021, all showing outer-ring deficit) describe a boundary condition the current product intentionally altered. A future radially resolved variant validated on those datasets is validating the *old* inlet distribution.
Coupling: none; provenance metadata only.

## Extractable data
Nothing warranting a data/ file. The one quantitative figure is ribes2020's chart, already fully transcribed on that card. The S1–S14 chart has no legible dimensions at source resolution. The linked FDA/PPS test-lab PDF (decentespresso.com) is food-safety compliance, out of scope. Raw preference data: not published, never tabulated.

## Overlaps and conflicts
- **ribes2020 / ribes2021 (data embedded here at lower fidelity):** this post is the design-side narrative around those registered datasets; it confirms their institutional context (Ribes and Costanzo were Decent's testers) and adds the vendor-adjacency note in reverse — the "independent" community decks were part of a vendor R&D program. Worth a one-line provenance amendment on both Ribes cards at next registry-state revision.
- **pocketscience2024 (complements):** same message as above — inlet-distribution hardware is a moving target across DE1 generations.
- **foster2025_2 / machine backlog (complements):** protrusion/headspace lineage is the concrete geometry context for H₀; no numbers usable directly beyond the deltas above.
- **Gap G9 (basket/screen resistance — weak):** the E61-screen edge-leakage flaw and Matrix-screen flow-rate remark are inlet-side anecdotes; no resistance data.
- No conflicts with registered components.

## Implementation estimate
Nothing to implement, nothing to transcribe beyond this card. Optional S-effort follow-ups: (1) amend ribes2020/ribes2021 provenance lines; (2) if machine-mode headspace work begins, confirm the S22A-equals-V2 protrusion inference with the author/community before using 9.6 mm as a V2 anchor.

VERDICT: skip — vendor design-history narrative with no model and no novel dataset (its only quantitative content is the already-registered ribes2020 data); the few protrusion/provenance scalars are captured inline above — effort S
