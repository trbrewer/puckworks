# gloess2013 — data provenance

**Source:** A. N. Gloess, B. Schonbachler, B. Klopprogge, L. D'Ambrosio, K. Chatelain, A. Bongartz,
A. Strittmatter, M. Rast, C. Yeretzian, "Comparison of nine common coffee extraction methods:
instrumental and sensory analysis," *Eur. Food Res. Technol.* **236** (2013) 607-627.
DOI 10.1007/s00217-013-1917-x. **Open Access (CC BY).** Card: `docs/cards/gloess2013.md`.

## What is here, and what is deliberately NOT

The paper compares nine brew methods. **Only ONE is in espresso scope**: `DE`, the Dalla Corte
semi-automatic espresso (16.01 g -> 60 ml, 9 bar, 92 C, 28.7 s). The other eight are lunghi, a moka
percolator, a capsule system, and their sensory profiles -- out of the espresso-simulation domain and
NOT transcribed. Two of the paper's four "espressi" (Bia = moka, NE = capsule) are physically not
pressure espresso and must never be pooled with DE; the capsule sample is also a *different,
unspecified* coffee.

## The precision distinction this file preserves

The card's route to exact numbers is the **Electronic Supplementary Material** (Supp. Tables 2-4).
**The ESM was not retrieved**, so this transcription comes from the card's Parameters table, which
draws on both the article text/tables and figure reads. The `extraction_method` column marks which:

| `extraction_method` | meaning | examples |
|---|---|---|
| `text_table` | an exact value printed in the text or Table 1, with its published uncertainty | dose 16.01 +/- 0.01 g; shot time 28.7 +/- 0.2 s; caffeine 21.0 +/- 0.4 mg |
| `figure_read` | **approximate**, read off a figure; NO published uncertainty | TDS ~5.5 %; EY ~20 %; pH ~5.7; titratable acidity; headspace |

**Do not treat a `figure_read` value as precise**, and do not attach a false uncertainty to one.
Retrieving the ESM would upgrade every `figure_read` row; that is the only outstanding work here.

## Standing caveats on even the exact values

- **Composites, not shots.** Each espresso sample is pooled from **five double shots** (3 samples per
  method, each analysed in triplicate), so the reported spread is *between composites* -- per-shot
  reproducibility is not recoverable from this source.
- **Volume, not mass.** The beverage is specified as 60 ml with no density given, so any
  volume -> `beverage_g` conversion is an assumption, not data.
- **One coffee, one point.** Single Guatemalan Arabica, one roast, one operating point: no dose,
  grind, pressure or temperature sweep, so no parameter dependence can be fitted or tested.
- **Endpoint only.** No EY(t), no TDS(t), no traces, no first-drip.
- **PSD is mode + FWHM only** (400 / 220 um) -- unusable for any distribution model.
- **Esterified** fatty acids only (free acids were retained on the column); this is not total lipids.

## Registry role

A low-priority **cross-check anchor**: an independent Dalla Corte espresso endpoint whose ~20 % EY at
~5.5 % TDS sits comfortably below cameron2020's 29.6 % per-bed-volume inventory ceiling. It is **not**
wired to a gate -- one pooled composite on one coffee is too weak to gate anything, and the headline
EY/TDS values are figure-reads. angeloni2023 dominates this slot for per-species espresso chemistry
(66 shots x 8 species); gloess adds breadth of brew *method*, not depth on espresso.
