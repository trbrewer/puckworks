# Model card: Gloess 2013 nine-method extraction comparison (instrumental + sensory)

**Paper/thesis:** A. N. Gloess, B. Schönbächler, B. Klopprogge, L. D'Ambrosio, K. Chatelain, A. Bongartz, A. Strittmatter, M. Rast, C. Yeretzian, "Comparison of nine common coffee extraction methods: instrumental and sensory analysis," *Eur. Food Res. Technol.* **236** (2013) 607–627. DOI 10.1007/s00217-013-1917-x. Open Access (CC BY).
**Stage(s):** observables · extraction · **Kind:** calibration (offline data intake; no physics executed)
**Status:** **data-intaken 2026-07-25 (DE endpoint only).** The single in-scope condition — the Dalla Corte espresso point (16.01 g → 60 ml, 9 bar, 92 °C, 28.7 s) — is transcribed to `puckworks/data/gloess2013/` with a per-quantity `extraction_method` column that keeps the **text-table** values (dose, time, caffeine 21.0 ± 0.4 mg, 3-CQA 5.8 ± 0.2, 5-CQA 2.8 ± 0.2) separate from the **figure-read approximations** (TDS ≈ 5.5 %, EY ≈ 20 %, pH, titratable acidity, headspace) — the ESM tables were not retrieved, so the approximate values must not be treated as precise. Everything else in the paper (lunghi, moka, capsule, sensory) is out of espresso scope. No component and no gate: one pooled composite endpoint on one coffee is too weak to gate anything; it is a low-priority cross-check anchor.

## Scope and mechanism
No model. This is an experimental campaign comparing nine brew methods — four "espressi" (DE = Dalla Corte semi-automatic espresso; SE = Schaerer fully-automatic espresso; NE = Nespresso capsule; Bia = Bialetti moka/percolator) and five "lunghi" (DL, SL semi/full-auto long; Bo French press; KK Karlsbader/percolation; F paper filter) — on a single Guatemalan Arabica, characterized by endpoint chemistry (total solids, °Brix, pH, titratable acidity to pH 6.6 and 8.0, esterified fatty-acid content and composition, caffeine, 3-CQA, 5-CQA, summed-aroma headspace intensity) and an 18-attribute trained-panel sensory profile, then cross-correlated (analytics vs sensory, PCA). For puckworks only the **DE espresso endpoint** is in scope: it is a real Dalla Corte extraction with a fully specified recipe on one coffee. Everything else (lunghi, moka, capsule, and all sensory-of-non-espresso) is out of the espresso-simulation domain. There is no time-resolved data, no trace, no dose/grind/pressure sweep, and no mechanism of any kind.

## Governing equations
None. The paper implements no process model; it reports measured endpoint quantities and Pearson correlations. Two definitional relations used to present the data:

1. Extraction yield = total-solids mass in cup per gram of roast-and-ground (R&G), reported as "TS per g R&G" in Fig. 7a and read directly as EY (dimensionless, %).
2. "Content per gram of R&G" for any measured species k = (species mass in cup) / (dose in g) — the per-gram efficiency panels of Fig. 7 (b–h).

No terms simplified away because none exist.

## Parameters
There are no model parameters. The table records the **DE espresso operating point and its measured endpoints** (the only in-scope condition), plus the espresso-grind PSD.

| symbol | value | units | source (measured/fitted/nominal/assumed) |
|---|---|---|---|
| dose (DE) | 16.01 ± 0.01 | g | measured (Table 1) |
| beverage volume (DE) | 2 × 30 = 60 | ml | nominal (double espresso target) |
| shot time (DE) | 28.7 ± 0.2 | s | measured (Table 1) |
| boiler/inlet temp (DE) | 92 | °C | nominal (Table 1) |
| pressure (DE) | 9 | bar | nominal (Table 1; gauge implied, not stated) |
| roast (DE) | Pt 80 (Colorette 3b) | — | measured |
| grinder / setting (DE) | Ditting KED 640, milling degree 3.0 | — | nominal |
| PSD, KED-3 (espresso grind) | 400 µm (mode), 220 µm FWHM | µm | measured (laser diffraction; mode + FWHM only) |
| TDS (DE, per 10 ml) | ≈ 5.5 (Fig. 4a; text "above 4%") | w-% | measured (gravimetry, figure-read) |
| EY (DE, TS per g R&G) | ≈ 20 (Fig. 7a) | % | measured (figure-read) |
| caffeine (DE, per 10 ml) | 21.0 ± 0.4 | mg | measured (HPLC, text) |
| 3-CQA (DE, per 10 ml) | 5.8 ± 0.2 | mg | measured (HPLC, text; series max) |
| 5-CQA (DE, per 10 ml) | 2.8 ± 0.2 | mg | measured (HPLC, text; series max) |
| esterified fatty acids (all brews) | < 0.2 | w-% | measured (Fig. 4g; DE ≈ 0.13 figure-read) |
| pH (DE) | ≈ 5.7 (Fig. 4c) | — | measured (figure-read; series spanned pH 5.51 NE to 5.92 Bo) |
| titratable acidity (DE, to pH 6.6 / pH 8, per 10 ml) | ≈ 1.15 / ≈ 2.4 (Fig. 4e,f) | ml 0.1 M NaOH | measured (figure-read) |
| headspace intensity (DE, per 10 ml) | ≈ 1.8×10⁷ (Fig. 4d) | area counts | measured (HS-SPME-GC/MS, figure-read) |
| n (per method) | 3 samples, each pooled from 5 double shots (DE); each analyzed in triplicate | — | measured |

Not provided: single-shot statistics (espresso samples are **composites of five double shots** pooled to 300 ml), grind/dose/pressure variation within DE, water density for volume→mass, beverage mass, temperature-resolved anything, full PSD (only mode + FWHM), 4-CQA (not quantifiable with their standards).

## Calibration and validation offered by the source
Nothing to validate — no model. As a dataset, the internal quality controls are: 3 samples/method × triplicate analysis, most on two days; espresso samples pooled from 5 double shots (variance is therefore *between composites*, not between shots). Cross-method chemistry is consistent with prior literature (López-Galilea, Peters, Crozier) by the authors' comparison. The analytics↔sensory correlations (one-sided F test, α = 0.1, Guatemalan coffee only): r²(total solids vs body) = 0.69, r²(headspace vs aroma intensity) = 0.73, r²(caffeine vs aftersensation-bitterness) = 0.69, r²(caffeine vs AS-astringency) = 0.75, r²((3-CQA+5-CQA) vs AS-bitterness) = 0.68, r²(sum-CQA vs AS-astringency) = 0.75; weaker trends r²(caffeine vs flavor-bitterness) = 0.58, r²(sum-CQA vs F-bitterness) = 0.51. The authors state plainly that **neither pH nor titratable acidity correlated with perceived acidity**, and that CQA itself is not bitter (the CQA↔bitterness correlation is a co-extraction proxy, not causal). These are cross-*method* correlations spanning espresso→filter→moka, so they are weak support for any within-espresso observables model. n = 9 method points; no held-out set.

## Assumptions and validity range
- One coffee (Guatemala Antigua "La Ceiba"), one roast per beverage class (Pt 80 espresso / Pt 86 lungo); NE capsule is a *different, unspecified* coffee — its numbers are not on the same material and must not be pooled with DE/SE.
- Espresso endpoints are pooled composites (5 double shots → 300 ml); no per-shot reproducibility recoverable.
- Endpoint-only: no EY(t), no TDS(t), no traces, no first-drip. Silent on all transients.
- Single operating point per method: no dose, grind, pressure, or temperature sweep — cannot fit or test any parameter dependence.
- Volumes, not masses; no density given, so volume→beverage_g conversion is assumed (~1 g/ml).
- Fatty-acid assay captures **esterified** acids only (free acids retained on the Extrelut column); "fatty acids" here ≠ total lipids.
- PSD is mode + FWHM from laser diffraction, no full curve; unusable for a distribution model.
- Failure/omission for espresso use: Bia (moka) and NE (capsule) are labelled "espressi" but are physically a percolator and a capsule system — do not treat as pressure-espresso; only DE (and SE, with an undisclosed grind) resemble the puckworks target.

## Interface mapping
Inputs consumed (as fixed conditions, not read at runtime): **MachineState** (9 bar, 92 °C for DE), **GrindState** (espresso grind mode ≈ 400 µm — but no fines fraction, no full PSD), **BedState** (dose 16.01 g; no depth/area/porosity reported). Outputs produced (measured, offline): **ShotResultState** — tds_pct (DE ≈ 5.5), EY_pct (DE ≈ 20), t_shot_s (28.7), beverage_g (≈ 60), plus per-species cup amounts (caffeine, 3-CQA, 5-CQA, esterified FA) that map to `traces`/derived observables. No adapters needed for intake; **no runtime coupling** — this is an offline endpoint anchor, not a component.

## Extractable data
Priority is narrow. The exact numbers live in the **Electronic Supplementary Material** (open-access): Supp. Table 2 (per-sip / per-10 ml), Supp. Table 3 (per-cup), Supp. Table 4 (per-gram R&G = efficiency/EY), Supp. Table 1 (38 aroma compounds). Main-text figures are the fallback and are digitizable.
- **DE row → data/gloess2013_de_espresso.csv** — the one in-scope endpoint: dose 16.01 g, 60 ml, 28.7 s, 92 °C, 9 bar → TDS, EY, caffeine, 3-CQA, 5-CQA, esterified FA, pH, titratable acidity. A single-point independent Dalla Corte espresso anchor. **The useful deliverable.**
- Supp. Table 4 (per-g R&G) → EY and per-species efficiency for all 9 methods, if a cross-method sanity table is ever wanted (Bia 31.2%, Bo 26%, filter 19% EY are the notable extremes).
- Fig. 5 → esterified FA composition (C16 + C18:2 > 80%); low priority lipid-speciation context.
- Fig. 11 PCA biplots → not transcribable as data (loadings only).
- Availability: article + ESM are open-access (CC BY); **no raw HPLC/GC traces, no code, no repository.** Transcription from ESM tables is the route; digitize figures only if ESM cannot be retrieved.

## Overlaps and conflicts
- **angeloni2023 (data-only, registered card) — thin complement, does not compete.** Angeloni ships 66 shots × 8 species over a 3T×3p×3grind design on Arabica+Robusta; Gloess gives 3 species (+ esterified FA) at *one* espresso point on a *different* Guatemalan Arabica. Same "multi-class solute chemistry" backlog slot, but Angeloni dominates it; Gloess adds only a single independent-coffee cross-check and titratable-acidity/headspace channels Angeloni lacks.
- **egidi2024 / cameron-lineage EY-TDS campaigns — complementary, non-overlapping.** Different coffee, endpoint-only, single point.
- **cameron2020.extraction_bdf (registered runtime) — sanity anchor.** DE's ≈ 20% EY at ≈ 5.5% TDS sits comfortably below Cameron's 29.6% per-bed-volume EY ceiling; a real-machine point consistent with the ceiling, but one pooled composite is weak as a gate.
- **DE1 fixture A (registered dataset) — same machine class (Dalla Corte).** Gloess DE is an *independent* Dalla Corte espresso endpoint (16 g, 60 ml, 9 bar, 92 °C, 28.7 s) but pooled and trace-free; it corroborates the fixture's machine family without supplying comparable P(t)/W(t) data. No conflict.
- **pocketscience2024, mckeonaloe2022/2023, smrke2024, schmieder2023 (observables siblings) — Gloess is cross-*method*, thin per-method.** It contributes breadth of brew type, not depth on espresso.
- **Backlog "observables: temperature effects" — no hit** (one temperature per method).
- **Backlog "multi-class solute chemistry" — partial, low-priority hit**, already better served by angeloni2023.

## Implementation estimate
Data intake only, **S**: transcribe the DE row from Supp. Tables 2–4 into one small CSV as an independent Dalla Corte espresso endpoint (TDS/EY/per-species). Optionally hold the 9-method per-g-R&G EY table as cross-method context. No runtime port (no model), no gate beyond an optional single-point bracket check at matched (T, p, ratio). Retrieving the ESM is the only dependency.

VERDICT: data-only — no model, and the multi-species chemistry is a thin, single-recipe subset of what angeloni2023 already provides, but the paper is open-access and yields one fully-specified, independent Dalla Corte espresso endpoint (16 g → 60 ml, 9 bar, 92 °C: TDS ≈ 5.5%, EY ≈ 20%, resolved caffeine/3-CQA/5-CQA) usable as a low-priority cross-check anchor — effort S
