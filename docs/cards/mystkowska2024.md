# Model card: Mystkowska 2024 — caffeine content by brewing method (narrative review)

**Paper/thesis:** Mystkowska, I.; Dmitrowicz, A.; Sijko-Szpańska, M., "Quantitative Analysis of Caffeine in Roasted Coffee: A Comparison of Brewing Methods," *Appl. Sci.* **14**(23):11395 (2024). DOI: 10.3390/app142311395. Open access (CC BY).
**Stage(s):** none (nominally *observables*, as a secondary-data candidate only) · **Kind:** n/a (would be calibration at best)
**Status:** proposed (card-only)

## Scope and mechanism
A narrative literature review — no model, no experiment, no new measurement. The authors searched PubMed and ScienceDirect (5 July 2024), screened 529 records to 32 included articles (PRISMA-style flow, Fig. 2), and tabulated, for five brewing methods (Cold Brew, Espresso, French Press, AeroPress, Moka), the brewing parameters reported by each primary source alongside its caffeine concentration, re-expressed into a common unit. A parallel strand catalogues the analytical chemistry: HPLC column, mobile phase, gradient, injection volume, flow rate, column temperature, detection wavelength, sample prep (Table 2) and method-validation figures (Table 3). The stated conclusion is methodological rather than physical: brewing parameters and HPLC parameters both vary so widely between studies that no parameter effect can be isolated, and the field needs standardisation. Everything relevant to puckworks is secondary — every number is copied and unit-converted from one of the 32 primary papers.

## Governing equations
**None are printed and none exist.** The review contains no transport, kinetic, or constitutive relation. For faithfulness, the three quantitative operations the authors actually perform on the compiled data are stated below; note that **the review does not write any of them down**, so the reconstructions are inferred from the tables and must be treated as such.

**(R1) Unit normalisation (inferred; §3.3 preamble).** Reported caffeine concentrations were "converted to mg/100 mL or mg/100 g to facilitate comparison within the same unit." No conversion formula, density assumption, or basis is given. The authors explicitly flag the ambiguity themselves: *"Although studies often report caffeine content per 100 g, it remains unclear whether this value refers to the weight of the brewed coffee or the coffee beans."* The mg/100 g and mg/100 mL blocks of every table are therefore **not on a common basis and are not comparable** — the authors say so in Tables 5–9 ("These values reflect distinct measurement approaches and are not directly comparable").

**(R2) Representative range = interquartile range (Fig. 4 caption).** The headline per-method ranges in the abstract and Fig. 4 are the IQR over the pooled per-study values, not min–max:
`range_method = [Q1({c_j}), Q3({c_j})]`, with `c_j` the mg/100 mL value of study *j* under that method. Each study contributes one or more values without weighting by *n*, replication, or method quality. This is why the abstract's espresso range (50.40–965.60 mg/100 mL) differs from the Table 6 span quoted in §3.3.2 (47.30–1210.80); likewise Cold Brew 48.50–179.95 (abstract) vs 48.00–180.10 (§3.3.1) and AeroPress 56.35–120.92 (abstract) vs 46.00–158.73 (Table 8).

**(R3) Serving arithmetic (§3.4, inferred).** `N_servings = 400 mg / (c_min · V_serving)`, with `c_min` the lower IQR bound for the method and `V_serving` a nominal cup volume (200 mL filter/immersion; 30 mL espresso), against the EFSA 400 mg/day adult ceiling. This reproduces the printed "26 servings" for espresso (`400/(0.504 mg mL⁻¹ × 30 mL) = 26.5`). The authors correctly disown the espresso figure as unrealistic.

Symbols: `c` caffeine concentration in the brew (mg/100 mL of beverage, or mg/100 g of unspecified basis); `V_serving` nominal serving volume (mL); Q1/Q3 first and third quartiles over the pooled study set.

## Parameters
No model parameters exist. The table below records the compiled quantities a downstream consumer might mistake for parameters, with the source type of the *review's* handling of them. All values are **secondary** — measured by the primary authors, transcribed and unit-converted here.

| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| c, Espresso (IQR, abstract/Fig. 4) | 50.40–965.60 | mg/100 mL | secondary — measured by primaries, pooled here |
| c, Espresso (Table 6 span) | 47.30–1210.80 | mg/100 mL | secondary |
| c, Espresso (mass basis, Table 6) | 457.00–6379.00 | mg/100 g (basis undefined) | secondary — basis unresolved by the authors |
| c, Cold Brew | 48.50–179.95 (IQR); 605–4080.76 | mg/100 mL; mg/100 g | secondary |
| c, French Press | 52.00–123.90 (IQR); 2971.02 | mg/100 mL; mg/100 g | secondary |
| c, AeroPress | 56.35–120.92 (IQR) | mg/100 mL | secondary |
| c, Moka | 128.00–539.90 (IQR); 3194–6564 | mg/100 mL; mg/100 g | secondary |
| espresso brew time (Table 6) | 8–30 (mean 25.5); n.d. in 6 of 13 rows | s | secondary/nominal |
| espresso water T (Table 6) | 79.1–97 (mean ~92) | °C | secondary |
| espresso pressure | "9–20 bar range" (§3.3.2 prose only) | bar | assumed — **no pressure column exists in Table 6**; not attributed per study |
| espresso dose (Table 6) | 6–20 | g | secondary |
| espresso water volume (Table 6) | 15–53; n.d. in 4 of 13 rows | mL | secondary |
| espresso coffee:water (Table 6) | 14:100–60–100; n.d. in 4 of 13 rows | g/100 mL | secondary/derived |
| grind size / PSD | not provided (any method, any study) | — | — |
| bed geometry, basket, tamp | not provided (except a prose mention of [41] baskets/discs) | — | — |
| EY, TDS, shot mass, flow rate | not provided anywhere in the review | — | — |
| HPLC λ, flow, column T, injection | Table 2, per study (λ 210–280 nm; 0.2–1.5 mL/min; 25–40 °C; 1–100 µL) | mixed | secondary |
| R², LOD, LOQ, RSD | Table 3, per study (R² 0.9881–1.000; LOD/LOQ reported by only 27.6%) | mixed | secondary |

Nothing here is a fitted or nominal *model* parameter; there is no model to parameterise.

## Calibration and validation offered by the source
**None, and none is claimed.** A review validates nothing. The only validation content is the *primaries'* HPLC method validation, re-tabulated (Table 3): R² generally >0.99, but LOD, LOQ and RSD reported in only 27.6% of studies (7 of 29 rows), and 12 rows are entirely "n.d." The review does not re-analyse, re-weight, meta-analyse, or apply any risk-of-bias tool; there is no forest plot, no heterogeneity statistic, no pooled effect size. Reporting the authors' own conclusion verbatim in substance: the number of studies and the spread in both brewing and analytical parameters "prevented a direct comparison of the effects of individual brewing parameters on caffeine content."

The causal statements the review does make are unsupported by its own tables. Two examples, in the review's numbers:

- **AeroPress, §3.3.4.** The claim is that Angeloni [30] "used a longer brewing time than Lapčíková [44], with the same other parameters," so time drives the difference. Table 8 shows [30] at 1.35 min with 16.5 g/250 mL → 78.00 mg/100 mL, and [44] at 1.25 min with **18 g**/250 mL → 49.80–62.90. The doses are not the same, and the *higher*-dose brew gives the *lower* concentration — a 6% time difference is credited with a ~30% concentration difference while a 9% dose difference running the other way is ignored.
- **Espresso, §3.3.2.** Higher caffeine is attributed to studies [34,40,45], but **[40] (Heo 2020) is a cold-brew study and appears nowhere in Table 6**; the intended reference is almost certainly [41] (Khamitova), which is discussed in the same sentence.

**Mass-balance check the review does not perform.** Converting Table 6 rows that give dose, volume and concentration together into caffeine per gram of dry dose (`c × V / m`):

| row | implied mg caffeine per g dose |
| --- | --- |
| [33] Caporaso (25 mL, 7 g) | 8.71 |
| [38] Derossi (25 mL, 7 g) | 8.88 |
| [48] Niseteo (50 mL, 7 g) | 6.98 |
| [41] Khamitova (28 mL from 50:100, 14 g) | 6.23–11.53 (A); 10.11–24.22 (R) |
| [34] Caprioli (25 mL, 7.5 g) | **17.56–19.20 (A); 30.37–34.00 (R)** |
| [56] Severini (25 mL, 7 g nominal) | **11.43–18.62** |
| [50] Salamanca (25 mL, 15 g) | **1.98–4.68** |
| [44] Lapčíková (25 mL, 7 g) | **1.69–1.91** |
| [35] Ciaramelli, mg/100 g read as per 100 g grounds | **28.68–38.71 (A); 48.35–63.79 (R)** |

Against roasted-bean caffeine inventories the registry already holds — bruno2026 Table 2 (four roasted single origins, mg/kg) and schmieder2023 (`c₀ = 9.71 mg g⁻¹` on a DE1) — arabica at ~10–12 mg/g and robusta ~20–24 mg/g, the bolded rows are outside what the bean can supply (>100% recovery of total caffeine, three-fold for Ciaramelli under either reading of "100 g") or implausibly low (Lapčíková implies <20% recovery at a normal espresso ratio). The review pools all of these into one IQR without a single consistency check. This is the concrete reason the compiled numbers cannot be used as data: the unit basis is unresolved by the authors' own admission (R1), and where it can be tested it fails.

**Citation-integrity defects** (relevant because the review's only potential value is as a pointer index):
- Table 5 attributes a cold-brew row (16 h, 20 °C, 30k mL, 1800 g, 72.00 mg/100 mL) to **[23]**, which is Wikoff et al., a systematic review of caffeine adverse effects containing no brewing experiment. The row's internal arithmetic is consistent (1800/30000 = 6:100), so the data are real but the pointer is wrong.
- Table 3 has **two rows labelled [58]** and none for [59]; the second is presumably [59].
- Table 3's [50] row has three columns where four are expected (misaligned).
- Table 9 (Moka) attributes a row to **[31]**, the Angeloni cold brew/cold drip paper, which does not cover Moka; §3.3.5's prose cites [30] for the same relationship. [30]/[31] appear interchanged.
- Table 2 (HPLC parameters) omits [43], [54] and [55]-adjacent rows inconsistently with the study list; the spectrophotometric and NMR studies are correctly excluded but not flagged in the table.

## Assumptions and validity range
- **A review of secondary data.** Nothing was measured. Validity is bounded by 32 heterogeneous primaries spanning 2000–2024, different beans, roasts, origins, grinders, machines, and analytical methods.
- Inclusion required only a named brewing method plus a caffeine number; no minimum reporting standard, no replication requirement, no bias assessment. Values enter the pool unweighted.
- Roast degree is missing or unstandardised in most primaries (only 25% of studies span ≥2 roast levels; "medium light"/"medium dark" used without definition), so no roast effect is resolvable — the authors state this.
- Origin is confounded with roast, method and analytical technique; the authors show four Colombian-Arabica medium-roast studies differing ~2× in caffeine and correctly decline to attribute it to origin.
- The mg/100 mL and mg/100 g blocks are on different, partly unknown bases (R1) and must never be merged.
- **Silent on everything the registry models.** No grind size or PSD, no fines fraction, no dose-to-bed geometry, no porosity, no permeability, no pressure trace, no flow rate, no tamp, no basket, no infiltration transient, no time-resolved extraction, no TDS, no EY. Espresso pressure is asserted once in prose ("9–20 bar") with no per-study attribution and no column in Table 6.
- Single species (caffeine). No acids, sugars, lipids, or bitter fraction; nothing on solubility, diffusivity, or partitioning.
- **Failure modes already realised inside the paper:** per-dose caffeine yields exceeding the bean inventory (Caprioli, Severini, Ciaramelli) or falling implausibly below it (Lapčíková, Salamanca); IQR ranges in the abstract silently inconsistent with min–max ranges in the body; causal claims about brewing time contradicted by the same table's dose column; at least five reference/label defects.

## Interface mapping
Inputs consumed: **none**. No field of `GrindState`, `BedState`, or `MachineState` appears anywhere in the review — grind, porosity, permeability, and the pressure trace are absent, and the one pressure statement is unattributed prose.
Outputs produced: **none**. Beverage caffeine concentration maps to no `ShotResultState` field (`EY_pct` and `tds_pct` require total dissolved solids from a defined dose and a measured beverage mass; a single-species concentration on an undefined basis supplies neither), and the registry has no per-species solute artifact today — the same gap already recorded on bruno2026, maille2024 and yu2021, where a hypothetical `SoluteInventory` would need a dry-basis mass fraction with provenance. This review cannot supply one: the basis is undefined by the authors and fails mass balance where testable.
Couplings: none, runtime or offline. No adapter is definable, since there is no state to translate.

## Extractable data
**Nothing worth transcribing into `puckworks/data/`.** No repository, no supplementary material, no code; every number is transcribe-from-PDF and every number is already published, with its full experimental context, in a primary source that puckworks would rather read directly.

- **Tables 5–9 (per-method brewing parameters + caffeine)** — the only tempting artifact, and the one to refuse. Values are re-unit-converted with an undisclosed formula onto a basis the authors state is unresolved; 4 of 13 espresso rows lack the water volume needed to compute a ratio, 6 lack brew time; and the rows that *are* complete fail the per-dose mass balance above. **Do not transcribe.**
- **Table 2 (HPLC parameters, 29 studies)** — an analytical-methods catalogue with no registry consumer. **Do not transcribe.**
- **Table 3 (R², LOD, LOQ, RSD)** — 27.6% populated, two mislabelled rows. **Do not transcribe.**
- **Tables 1, 4 (coffee origin/roast; method-by-study matrix)** — presence/absence dot grids, no quantities. **Do not transcribe.**
- **Figures 1–4** — Fig. 1 is a chemical structure diagram; Fig. 2 a PRISMA flow; Fig. 3 a histogram of detection wavelengths; Fig. 4 a bar chart of the IQRs already printed in the abstract. Nothing to digitise.
- **The one residual use is bibliographic.** Table 6 is a compact index of thirteen espresso primaries with their brewing conditions, which is a cheap way to triage acquisition targets. Of those, **khamitova2020 [41] and schmieder2023 [55] are already registered**; the untouched ones worth a look, in rough order of likely value, are **Caprioli 2014** [34] (espresso machine × cultivar, but the source of the worst mass-balance failure above — acquire sceptically), **Ludwig 2014** [45] (9 g and 18 g doses, 15–53 mL volumes — the only dose/volume sweep in the set), **Severini 2016** [56] (8–24 s brew time × 6/7/8 g dose, i.e. an actual parameter sweep), **Salamanca 2017** [50] (temperature-gradient espresso), and **Santanatoglia 2024** [53] (SPE + HPLC-DAD organic acids, chlorogenic acids and caffeine in espresso — the multi-class-solute backlog's shape, from the group behind angeloni2023 and khamitova2020). Fetch those papers; do not fetch their numbers from here.

## Overlaps and conflicts
- **legasmuhammed2021 (skip), yu2021 (skip) — same family, one rung more remote.** Those were skipped as single-endpoint caffeine assays with broken unit chains. This one at least reports its provenance and states its own unit ambiguity, but it adds a layer of removal: it did not measure anything, and it pools sources that disagree by 25× without reconciliation.
- **schmieder2023 (registered) — superseded by it, and directly conflicting.** Schmieder is *inside* this review as [55], re-expressed as "457.00 mg/100 g" with an undefined basis; the registered card carries `c₀ = 9.71 mg g⁻¹`, `λ = 23.09 g` in a cumulative-mass exponential on a DE1 Pro with a known dose, basket, grinder and PSD. The two cannot be reconciled without knowing the review's basis, which is exactly the hazard. Prefer the primary; treat the review's re-expression of any registry-held source as untrusted.
- **angeloni2023 (calibration) — superseded by it.** The 66-shot per-species espresso dataset flagged for the multi-class-solute backlog dominates this on species count, time resolution, replication, and machine control.
- **maille2024 (calibration) — superseded by it.** Maille supplies per-species extraction timescales with CIs; this review has no time axis at all.
- **bruno2026 (data-only) — superseded by it** for bean inventory, and bruno2026 is the reference set that *falsifies* several rows here.
- **pannusch2024, egidi2024, cameron2020.extraction_bdf** — no interaction. Lumped or multi-class extraction kinetics are untouched by pooled endpoint concentrations with no dose basis.
- **Open backlog "extraction: multi-class solute chemistry"** — not addressed. One species, no kinetics, no acids or sugars. The backlog remains where it was: angeloni2023's per-species dataset is still the richest candidate.
- **Open backlog "observables: temperature effects; scale/measurement kernels"** — brushed against and missed. The review documents that HPLC wavelength, gradient and column temperature vary across studies and *may* shift results, but never quantifies the shift; there is no measurement-kernel content, only the assertion that one is needed.
- Competes with nothing registered; complements nothing; supersedes nothing.

## Implementation estimate
Nothing to implement, nothing to gate, no dependencies. Transcribing Tables 5–9 would nominally be effort S, but it should not be done for the reasons in Extractable data — ingesting a secondary compilation on an unresolved unit basis would import the registry's exact anti-pattern (silent merge of conflicting values across sources) at scale. The correct action is to spend the equivalent effort acquiring the five primary espresso papers listed above.

VERDICT: skip — a narrative review with no model, no measurement and no time resolution, whose pooled caffeine table is re-unit-converted onto a basis the authors themselves state is unresolved and which fails a per-dose mass balance in five rows (implying 18–64 mg caffeine per g of dose against ~10–12 mg/g for arabica), carries at least five reference/labelling defects, and is dominated on every axis by the already-registered schmieder2023, angeloni2023, maille2024 and bruno2026; retain only as a bibliographic index to five unacquired espresso primaries — effort S.
