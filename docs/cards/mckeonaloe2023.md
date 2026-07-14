# Model card: McKeon Aloe 2023 — TDS/EY control-chart comparison vs public shot data

**Paper/thesis:** R. McKeon Aloe, "Comparing My Espresso to Publicly Available Data: How do other espresso shots look?," Medium (Coffee Data Science), 3 Feb 2023. No DOI; blog post, not peer-reviewed.
**Stage(s):** observables · **Kind:** calibration (at most a data source; nothing runtime)
**Status:** assessed 2026-07-13 → **SKIP** (card retained for the record; raw data unpublished, figure-only points with unnamed sources / no per-point metadata → no transcribable dataset; no manifest row, no data file, no component, no gate — per the verdict below and the `mckeonaloe2021` skip precedent).

## Scope and mechanism
Not a model. A descriptive comparison of the author's espresso shots (a "few hundred" recent shots out of ~2,000 logged, split into "Paper Star" recent vs "Previous Shots") against 1,320 shots aggregated by scraping "roughly 10" unnamed public sources where TDS/EY were reported. Three scatter charts are shown: TDS vs EY (control-chart shading), the same with iso-IR guide arcs, and IR vs EY. The only quantitative construct introduced is a derived observable, the "Intensity Radius." The stated conclusion is that the author's shots occupy a distinctly higher-TDS band than the public data, and an anecdotal taste claim (EY +1–2 pts noticeably improves taste).

## Governing equations
One definition (unnumbered in source):

1. IR = √(TDS² + EY²)
   - TDS — total dissolved solids of the beverage, % (refractometer).
   - EY — extraction yield, % (from TDS × beverage mass / dose, the standard construction; the post states TDS is "combined with the output weight... and the input weight" but does not write the formula).
   - IR — "Intensity Radius," the Euclidean radius from the origin in the (EY, TDS) plane, %. Author's motivation: normalize shot comparison across brew ratio.

Note (registry-side, not from source): IR quadratically sums two percentages of different denominators (beverage mass vs dose); at fixed brew ratio r = beverage/dose, TDS = EY/r exactly, so IR = EY·√(1 + 1/r²) — i.e., IR is a monotone rescaling of EY at fixed ratio and carries no information beyond (EY, r). Nothing else is simplified away; the source contains no further equations.

## Parameters
No model parameters. Dataset descriptors (all from prose; no tables):

| symbol | value | units | source |
|---|---|---|---|
| N, public comparison shots | 1,320 | shots | measured (scraped, ~10 unnamed sources) |
| N, author's total log | ≈ 2,000 | shots | measured (self-logged) |
| N, author's plotted subset | "few hundred" | shots | measured (exact count not provided) |
| brew ratio of most comparison shots | ≈ 2:1 | out:in | nominal (author's characterization) |
| public-data TDS band (from figures) | ≈ 8–12 | % | measured, read off scatter |
| public-data EY band (from figures) | ≈ 16–25 | % | measured, read off scatter |
| author recent-shot band (from figures) | TDS ≈ 12–22 at EY ≈ 16–26 | % | measured, read off scatter |
| per-point metadata (dose, ratio, grind, machine, source) | not provided | — | — |

## Calibration and validation offered by the source
None. This is exploratory plotting, not validation of anything. The comparison pools multiple test series of differing experimental design (the author says so), with no per-point provenance, no source list, no brew-ratio normalization beyond the informal "most were 2:1," and no measurement-uncertainty discussion (refractometer TDS error, filtration practice, etc. are unaddressed). The taste claim (EY +1–2 pts → better taste) is asserted, not tested. The "different range entirely" conclusion is visually plausible in the figures but confounded: at fixed EY, higher TDS just means a tighter brew ratio, and the author's shots are explicitly not pulled at the comparison population's 2:1 ratio — the IR guide-line chart was added precisely because of this, which concedes the populations differ in ratio, not necessarily in extraction quality.

## Assumptions and validity range
- IR treats (TDS, EY) as commensurable axes; no physical basis is offered. At fixed brew ratio it is redundant with EY (see note under equations).
- Aggregated public data: unknown sources, mixed designs, unknown ratios per point — usable only as a coarse "where reported shots land" cloud, not as a controlled population.
- Silent on: everything upstream of the cup (grind, dose, pressure, temperature), time dependence, and any mechanism. There is nothing here that a shot-chain simulation could be gated against beyond "does (EY, TDS) land in a plausible region."
- Failure mode of the headline claim: population difference in brew ratio masquerading as performance difference.

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1 — IR would be a one-line derived field on ShotResultState(EY_pct, tds_pct), and there is no case for adding it: it encodes no information beyond fields already present plus brew ratio. Couplings: none. At most, a digitized public-shot cloud could serve as an offline plausibility envelope for simulated (EY_pct, tds_pct) pairs at ~2:1 ratio — a sanity band, not a gate.

## Extractable data
- Three scatter charts (TDS–EY twice, IR–EY once), ~1,600 points total, digitizable in principle — but with no per-point source, ratio, or preparation metadata, a digitized cloud supports only the crude envelope above. Marginal value; not recommended for puckworks/data/ unless an observables sanity band is ever wanted, in which case digitize the "Other People" series of the first chart only.
- Raw data/code: not published. The author's own 2,000-shot log and the scraped compilation exist (author generated them) and are plausibly available-on-request — the compilation with source labels would be materially more valuable than the figures.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (no competition; weak complement):** cameron2020 predicts EY/TDS trajectories against controlled measurements; this post offers only an uncontrolled population cloud those outputs could be loosely sanity-checked against. It neither tests nor constrains the model.
- **ShotResultState / observables backlog (touches, adds nothing):** the backlog wants measurement kernels (refractometer error, temperature effects); this post uses refractometer TDS but says nothing about its error model.
- **mckeonaloe2021 (same author, no contact):** different topic entirely (imbibition vs cup metrics); shares the provenance class — single-hobbyist, figure-only, no raw data.
- **angeloni2023 (no conflict):** angeloni's species-resolved chemistry is the opposite end of the observables spectrum from a lumped TDS scatter.
- No registered component is competed with or superseded; nothing here models anything.

## Implementation estimate
None warranted. IR is a one-line formula with no registry use case. The only conceivable artifact (digitized 2:1-ratio public-shot envelope) is effort S but currently motivated by no open gate; revisit only if an observables plausibility band is ever specified.

VERDICT: skip — no model, one dimensionally arbitrary derived metric redundant with (EY, ratio), and figure-only aggregated data with unnamed sources and no per-point metadata; nothing fills a named gap — effort S
