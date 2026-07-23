# Model card: McKeon Aloe 2023b — critique of Ribes radial-uniformity experiments; wall-channel reinterpretation

**Paper/thesis:** R. McKeon Aloe, "A Critique of Radial Uniformity Experiments in Espresso: Looking back at some data and exploring images," Medium (Coffee Data Science), 11 Jul 2023. No DOI; blog post, not peer-reviewed. Commentary on the two Ribes decks carded as ribes2020 and ribes2021. Filename suffixed `_2` to distinguish from the Feb 2023 post already carded as mckeonaloe2023.
**Stage(s):** bed_dynamics (radial extraction heterogeneity — interpretive) · **Kind:** calibration (at most a commentary/annotation source; nothing runtime)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model. A methodological critique and photographic reinterpretation of the Ribes three-zone radial-EY experiments. Central claim: Ribes's outer-zone deficit is real but mislocated — in Ribes's own spent-puck photos the dark (under-extracted) ring sits **inboard of the rim**, over the unperforated annulus of the basket floor, while the **very outer edge against the basket wall is light**, i.e. extracted comparably to the center via side/wall channeling. If so, Ribes's outer zone (25–29 mm) averages two opposite populations — a soluble-rich ring over the hole-free annulus and a soluble-depleted wall rim — and his design (three annular cuts, edge-inclusive outer zone) cannot resolve it. The author supports this with (a) his own bottom-of-puck photos across baskets (Kim Express tapered single: center channeling, dark ring outside the primary hole area, light ring at the very edge; Wafo Spirit: dark near-edge ring consistent with Ribes but a very-edge ring "lighter than any other area of the puck," attributed to side channeling along the filter wall; staccato and regular shots showing dark soluble streaks running **up the puck sides**), (b) a re-reading of Ribes 2021 puck photos (non-continuous dark ring; edge itself not dark, including up the basket wall), and (c) his earlier grounds-TDS (gTDS) square-grid maps of two spent pucks, where gTDS fell off at the edge (fewer solubles remaining → edge *more* extracted), disagreeing with Ribes's zone EYs. The post closes with a sketched hypothesis — a non-monotone EY(r) at higher radial sampling: dip over the unperforated ring, recovery at the wall — and three protocol fixes (cut the very edge as its own sample; cut the puck vertically; test brew ratios 1:1/2:1/3:1). One incidental axial observation: when the author has cut pucks vertically, the top was mostly extracted and the majority of remaining solubles sat in the bottom.

## Governing equations
None. No equations, no fits, no mass balances. The gTDS protocol (small water addition on grounds directly on the refractometer) is referenced by link, not specified here.

## Parameters
No model parameters. Quantitative content in figures:

| quantity | value | units | source |
|---|---|---|---|
| gTDS grid, puck 1 (square grid over ~58 mm puck, ~32 legible cells) | ≈ 0.02–3.91, most cells 0.1–0.7, edge cells low | % gTDS | measured (author, prior post; re-shown) |
| gTDS grid, puck 2 (~33 legible cells) | ≈ 0.12–4.28, interior cells to ≈ 2.9–4.3, edge cells mostly < 0.5 | % gTDS | measured (same provenance) |
| grid cell size, dose, grind, basket, machine, shot recipe for the gTDS pucks | not provided | — | — |
| n (pucks per basket type in the photo evidence) | not provided; single exemplar photos | — | — |
| Ribes zone EYs quoted (3/2/11/24/25/16% deficits/yields figure) | reproduction of ribes2020 chart | % | secondary (already carded at source on ribes2020) |
| hypothesized EY(r) curve ("suspected EY pattern at a higher sampling") | dashed sketch, no values | — | assumed (author's hypothesis) |

The gTDS values are protocol-specific (undiluted-slurry refractometry on grounds), with no stated mapping to zone EY; do not compare in absolute terms against Ribes or pocketscience2024 numbers.

## Calibration and validation offered by the source
None. The wall-channel claim rests on visual darkness of spent-puck surfaces in photographs — uncontrolled lighting, single exemplars per basket, no colorimetry, no gTDS or immersion measurement taken *on the disputed rim itself*. The author is explicit that this is a pre-experiment discussion ("Before I went down that path of experimentation, I wanted to have this discussion using Stéphane's data") — i.e. the reinterpretation is proposed, not tested. The gTDS grids come from a different machine and equipment than Ribes's shots (the author says so), so the gTDS-vs-Ribes disagreement is confounded by shot style and cannot arbitrate the hypothesis. Puck-surface darkness as an extraction proxy is itself unvalidated here (darkness also tracks moisture, fines accumulation, and roast oils).

## Assumptions and validity range
- Assumes surface darkness of a spent puck is a monotone proxy for remaining solubles; never calibrated in this post.
- Assumes lateral soluble movement is negligible for Ribes's zone method (the author flags this assumption and notes a radially-cut shot splitter would test it) — but the wall-channel mechanism he proposes is *itself* lateral/vertical soluble transport along the wall, in tension with that assumption.
- Photo evidence spans mixed baskets (tapered Kim Express single, Wafo Spirit, Ribes's VST/Pullman) and mixed shot styles (staccato layered, regular); no single controlled configuration.
- The non-monotone EY(r) sketch is offered for pucks in traditional baskets with an unperforated outer annulus; silent on full-coverage-hole baskets (where the dip ring should shrink or vanish — an implicit, untested prediction).
- Axial claim (top extracted, bottom soluble-rich) is anecdotal, uncounted, and un-illustrated in this post.
- Silent on: pressure/flow, grind, dose, temperature, replicate variability, any mechanism sizing (how wide is the wall channel; what fraction of dose sits in the rim).

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1. Offline uses only:
- **Gate-design annotation for the radial-EY datasets (the real payload):** any future radially resolved bed_dynamics/extraction variant gated on pocketscience2024 with ribes2020/ribes2021 as secondary targets should treat Ribes's outer-zone EY as a possible **mixture** of an unperforated-ring deficit and a wall-channel rim. Concretely: the zone-level criteria on the ribes cards (outer/center ≈ 0.5–0.7 without screen) stand, but a model predicting non-monotone EY(r) — dip over the hole-free annulus, partial recovery in the last ~1–2 mm at the wall — should not be failed against the three-zone data, which cannot distinguish it from a monotone profile. Amend both ribes cards' gate-design paragraphs accordingly on next revision.
- **brewer2026.streamtube:** the wall channel is a candidate physical identity for a persistent high-conductance tube pinned at the boundary — a spatially structured atom the exchangeable lognormal does not represent; same caution class as the inlet/outlet boundary effects on the sibling cards.
- Axial anecdote aligns qualitatively with the axial extraction gradient runtime models predict (fresh water enters at top); no numbers to gate on.
Coupling: none; no adapters; prose annotation only.

## Extractable data
- gTDS grids (two pucks, ~65 legible cells total): transcribable in principle, **not recommended** — no shot metadata, protocol-specific units with no EY mapping, different equipment from any registry dataset, square grid over a circular puck. Revisit only if a gTDS-based lateral-map gate is ever specified.
- Puck photos and the dashed EY(r) sketch: qualitative; nothing to transcribe.
- Raw data/code: not published. The author's photo archive and gTDS logs exist and are plausibly available-on-request; the decisive measurement (edge-resolved sampling per his own proposal #1) apparently does not exist yet as of the post.

## Overlaps and conflicts
- **ribes2020 / ribes2021 (direct commentary — modifies their use, adds no data):** does not dispute the zone numbers; disputes their spatial interpretation and the "expand the perforated area" recommendation built on them (ribes2020 slide 5), since under the wall-channel reading the deficit is over the existing unperforated annulus, not uniformly "the edge." Also independently corroborates the ribes2021 puck-release caveat (pucks not coming out cleanly).
- **pocketscience2024 (complements, cautions):** the primary radial dataset also uses edge-inclusive outer sampling; the same mixture caveat applies to its edge zone when used as a gate. Its full-coverage-basket result (reduced edge loss) is consistent with either interpretation and does not discriminate.
- **mckeonaloe2022 / schulman2011 / gap G9 (weak complement):** the dark-ring-over-unperforated-annulus observation ties radial EY structure to basket floor hole coverage — motivational for a hole-layout-aware exit boundary, no numbers.
- **brewer2026.streamtube (cautions):** as above — boundary-pinned channel vs exchangeable heterogeneity.
- **mckeonaloe2021 / mckeonaloe2023 (same author, no contact):** different topics; shares the provenance class (hobbyist, figure-only, no raw data).
- No registered component is competed with or superseded; nothing here models anything.

## Implementation estimate
Nothing to implement. Effort S to carry the payload: one-paragraph amendments to ribes2020/ribes2021 (and a one-line note on pocketscience2024) marking the outer zone as a possible deficit-ring/wall-rim mixture and relaxing the monotonicity expectation in their gate designs. The decisive experiment (edge-cut-separately radial sectioning) is named by the author but not performed; if it ever appears, that source would be the data card, not this one.

VERDICT: skip — commentary with no model and no usable data, but its wall-channel mixture caveat is worth folding into the ribes and pocketscience gate designs as an annotation — effort S
