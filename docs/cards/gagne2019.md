# Model card: Gagné 2019 — extraction-yield measurement kernel (percolation / immersion / mixed, from TDS)

**Paper/thesis:** J. Gagné (Coffee ad Astra), "Measuring and Reporting Extraction Yield," blog post, 17 Feb 2019 (follow-up noted 25 Mar 2019). No DOI; not peer-reviewed. Cheat-sheet PDF and a general-case derivation PDF linked in the post; a companion web calculator by Mitch Hale is linked for the mixed-phase form.
**Stage(s):** observables · **Kind:** calibration (measurement/convention kernel; nothing runtime)
**Status:** **propagated 2026-07-25 (documentation, per this card's own Implementation estimate — no runtime code, no gate, no data ingest).** ROADMAP §5.10 now records **P7 `EY = C·B/D`** as the canonical espresso (percolation) EY kernel, together with the three cautions this card supplies: the `1/(1−C)` term is **9–14 % relative** at espresso `C ≈ 0.08–0.12` (not the sub-0.5 % it is for filter, so prefer the measured-`B` form); the espresso liquid-retained ratio is **L ≈ 0.49** (foster2025's fitted `W_dead` 8.8 g on an 18 g dose; bed-capacity bracket gives 0.42–0.78), **not** the filter `L ≈ 2`; and the load-bearing `M_ret ≈ 0` assumption is disputed in-source and weakest exactly at espresso conditions — flagged, not resolved. The moisture/CO₂ **≈1 pt EY** offset is now a P1 cross-source comparability hazard row. Not registered as a component: it has **no dataset**, so no gate could be wired to real data (architecture rule 1).

## Scope and mechanism
Not a forward model. A definitional/algebra reference deriving average extraction yield E (fraction of dry dose dissolved) from a refractometer TDS reading C, dose D, brew-water mass W, beverage mass B, and the liquid-retained ratio L (LRR, g water retained per g dry coffee). It gives three closed forms — percolation, immersion, and a general mixed-phase equation — plus the small-correction bookkeeping (the 1/(1−C) solids-in-beverage term) and cross-source normalization caveats (moisture/CO₂ in the bean; reporting precision). Espresso is explicitly classified as a **percolation** brew (pump-driven, but fresh water on top), so only the percolation forms are in-scope for the registry; the immersion and mixed forms are carried for completeness and to formalize the retained-liquid corrections the section-EY cards use. All quantities are fractional throughout (1.4 % TDS = 0.014).

## Governing equations
Transcribed as written; the post numbers nothing, so labels P#/I#/M# are assigned here. Faithful to the source, no terms dropped except where the source itself drops them (noted).

**Percolation (espresso-relevant):**
1. (P1) `C = M_bev / B` — TDS is dissolved-solids mass in the beverage over total beverage mass.
2. (P2) `B = W − L·D + M_bev` — beverage mass = poured water − water retained in spent bed + dissolved solids. Source ignores CO₂/moisture here.
3. (P3) `E = (M_bev + M_ret) / D`, with **M_ret ≈ 0** asserted for percolation (retained water carries negligible solids at end of a fresh-water percolation). This is the *definition*; the naive `E = M_bev/D` is flagged by the author as "kind of right" and superseded by P3.
4. (P4) `C = M_bev / (W − L·D + M_bev)` — P1 with P2 substituted.
5. (P5) `M_bev = C/(1−C) · (W − L·D)` — P4 inverted.
6. (P6) `E = C/(1−C) · (W/D − L)` — **LRR-based** percolation yield (needs an assumed L).
7. (P7) `E = C·B/D` — **exact** percolation yield from a *measured* beverage mass B; no LRR assumption, no 1/(1−C) term. Author's recommended form.

**Immersion (out of espresso scope; carried for the retention kernel):**
8. (I1) `C = M_ret / (L·D + M_ret)` — at brew end, retained-water TDS equals cup TDS.
9. (I2) `M_ret = C·L·D / (1−C)` — I1 inverted.
10. (I3) `E = C/(1−C) · (W/D)` — L cancels entirely; no beverage weighing or L assumption needed.

**Mixed phase (immersion-then-percolation: AeroPress, siphon, Clever; out of scope):**
11. (M1) `B = W − W_ret + M_bev` — W_ret is total retained-water mass.
12. (M2) `C_last = M_ret / (M_ret + W_ret)` — spent-bed TDS (measured from last drops).
13. (M3) `E = ((C_bev − C_last)/(1−C_last)) · (B/D) + (C_last/(1−C_last)) · (W/D)` — general form; reduces to I3 when C_last=C_bev and to the percolation form when C_last=0.
14. (M4) `(C_bev − C_last) · ((W − B)/D) < 0.1 %` — adequacy test: if satisfied, the immersion form I3 may be used instead of M3.

Symbols: C beverage TDS (frac); C_bev, C_last beverage / spent-bed TDS (frac); E extraction yield (frac); D dry dose (g); W brew-water mass (g); B beverage mass (g); L liquid-retained ratio (g/g); M_bev dissolved solids in beverage (g); M_ret dissolved solids in retained water (g); W_ret retained-water mass (g).

## Parameters
No fitted model parameters — this is a definitional kernel. The one physical constant it introduces, and the two quantitative error/offset claims:

| symbol / quantity | value | units | source |
|---|---|---|---|
| L (LRR), typical filter/percolation | ≈ 2 | g/g | nominal (author's rule of thumb) |
| 1/(1−C) correction, filter coffee | 0.2–0.4 | % EY | assumed (author estimate, low-C regime) |
| 1/(1−C) correction, immersion | 0.2–0.5 | % EY | assumed (author estimate) |
| moisture+CO₂ (VST app) vs simplified EY offset | ≈ 1 | % EY (simplified reads ~1 pt lower) | measured (author, cross-app comparison) |
| EY reporting precision from 0.1 g dose error | ≈ 0.1 | % EY | measured (error-propagation, attrib. M. Hale) |
| espresso L, non-percolation profiles, temperature/CO₂ functional forms | not provided | — | — |

Note `[RS]`: the "L ≈ 2" value is a **filter/percolation-bed** figure; espresso pucks are compressed and retain far less. This is not an espresso L — see foster2025 cross-link below.

## Calibration and validation offered by the source
Nothing to validate — the derivations are algebra, not empirical claims, and are internally correct (M3 verifiably reduces to I3 and P-forms at the stated limits). The empirical assertions are: (i) M_ret≈0 for percolation is an *assumption* the author flags as the load-bearing approximation, and explicitly notes Scott Rao/Dan Eil dispute it (retained percolation liquid may not be solids-free) — **acknowledged as unsettled**; (ii) the 1/(1−C) magnitudes and the ~1 pt moisture/CO₂ offset are quoted from the author's own comparisons, no dataset shown. Espresso syringe-filter necessity for TDS is cited from Mitch Hale's experiment, not measured here. Grade: **definitionally sound; the percolation-retention assumption is a stated hypothesis, and every numeric magnitude is an uncorroborated author estimate.**

## Assumptions and validity range
- **M_ret ≈ 0 (percolation) is the key assumption** and is contested in the source itself; it fails as C rises late in a shot. For espresso this is the regime that matters most (high C, short bed) — the assumption is weakest exactly where the registry would apply it.
- The 1/(1−C) term is quoted as sub-0.5 % *for filter coffee* (low C). For espresso C ≈ 0.08–0.12 the factor is 1.09–1.14, i.e. a **9–14 % relative** correction — the "small correction" framing does **not** transfer to espresso, and P7 (measured-B, exact) should be used rather than the LRR form P6.
- Moisture/CO₂ neglected in all boxed equations; the ~1 pt offset is a cross-source **normalization hazard**, not a modeled term.
- Mixed-phase (M1–M4) requires measuring spent-bed TDS (C_last) from last drops — a destructive extra measurement; not applicable to straight espresso.
- Silent on: temperature dependence of TDS/refractometry, the physical origin of L, any time resolution (endpoint algebra only), and the espresso-specific value of L.

## Interface mapping
Inputs consumed: `ShotResultState.tds_pct` (→ C), `ShotResultState.beverage_g` (→ B), `BedState.dose_kg` (→ D). Outputs produced: `ShotResultState.EY_pct` (→ E via P7). Couplings: **OFFLINE / observables kernel only — no runtime stage.** This is the reference definition for how EY_pct is computed from tds_pct and beverage_g in the espresso (percolation) path: use **P7 `E = C·B/D`** (exact) as the canonical kernel; P6 is the LRR fallback when only W is known. No adapter needed for espresso. The LRR term `L·D` maps to a *retained-liquid mass*, which links to **foster2025**'s bed capacity / fitted W_dead (retained water ≈ L·D): for an ~18 g dose, foster's W_dead ~8.8 g implies an espresso L ≈ 0.5 g/g — far below the filter L≈2 quoted here, worth recording as the espresso-appropriate value. The mixed/immersion forms (I3, M3) are the correct kernel only for the **section-EY reconstruction** in pocketscience2024 / ribes2020 / ribes2021, where spent-puck solubles are recovered by immersion — those cards' retained-liquid corrections are exactly I1–I2, and this card formalizes the algebra they leave implicit.

## Extractable data
No datasets. Two transcribable artifacts: (a) the cheat-sheet PDF (equations in %-form) and the general-derivation PDF — reference documents, not data, worth archiving to `puckworks/data/refs/` for provenance of the EY kernel; (b) the percolation/immersion **coffee control charts** (TDS vs EY with iso-ratio lines, LRR=2 assumed) — plotting constructions, not measurements; do not digitize (redundant with computing EY from any (C, ratio) pair). No raw data or code beyond the linked calculator. Availability: PDFs and calculator link live in the post; verify at acquisition (2019 vintage).

## Overlaps and conflicts
- **cameron2020.extraction_bdf / all EY-producing components:** COMPLEMENT (foundational) — this is the definition their `EY_pct` output should conform to; P7 is the exact kernel, and the espresso 1/(1−C) magnitude above is a caution against the LRR form at high C.
- **liang2021 (immersion desorption + oven-drying kernel):** COMPLEMENT, same family — liang's retention correction (Eqs. 18–24, R_ret) is the oven-drying analogue of I1–I2; both formalize "spent grounds hold solubles." liang measures R_ret ≈ 2.5 g/g for 1-L immersion; consistent with L≈2 here for water-retention, though liang's is a full mass-balance with volatilization. No conflict; different measurement route to the same quantity.
- **pocketscience2024 / ribes2020 / ribes2021 (section-EY):** COMPLEMENT — those cards back-compute per-zone EY from immersion TDS with an LRR correction they don't write down; I1–I2 here **are** that chain. This card is the citable basis for their mass balance.
- **mckeonaloe2023 (IR construct):** COMPLEMENT — that card calls EY "the standard construction (TDS × beverage mass / dose)"; P7 is precisely that standard construction, now sourced.
- **foster2025.infiltration:** COMPLEMENT — `L·D` = retained-liquid mass ↔ foster's bed capacity / W_dead; provides the espresso-appropriate L (~0.5) that supersedes the filter L≈2 for the registry.
- **gagne2021 (blooming shots):** same author, DIFFERENT work — that card is an 11-shot DE1 dataset + viscosity hypothesis; this is the measurement algebra behind its EY numbers. No overlap beyond shared EY definition; do not merge.
- **ROADMAP normalization-hazards table (P1):** the moisture/CO₂ ~1 pt offset is a new candidate entry (cross-source EY comparability), analogous to the existing pressure-convention hazard.
- **CONFLICT (latent):** the M_ret≈0 percolation assumption is disputed in-source (Rao/Eil) and matches the bed_dynamics open question of whether spent-puck retained liquid is solids-free — flag, don't resolve.

## Implementation estimate
Effort S, and mostly documentation: pin P7 as the canonical espresso EY kernel in the observables layer (likely already implicit), record the espresso 1/(1−C) caution and the espresso L≈0.5 (from foster) vs filter L≈2, add the moisture/CO₂ offset to the P1 hazards table, and cite this card as the mass-balance basis for the section-EY cards. No runtime code, no gate, no data ingest beyond archiving the two reference PDFs.

VERDICT: calibration-provider — the citable reference kernel for computing EY from TDS (exact form P7 for espresso) plus the retained-liquid algebra the section-EY cards leave implicit and a moisture/CO₂ normalization-hazard flag; no new data and the espresso-relevant equation is already in use, so value is definitional/consistency, not capability — effort S.
