# Model card: Cameron 2020 (SI re-intake — duplicate of registered component)

**Paper/thesis:** Cameron, Morisco, Hofstetter, Uman, Wilkinson, Kennedy, Fontenot, Lee, Hendon & Foster, "Systematically Improving Espresso: Insights from Mathematical Modeling and Experiment," *Matter* 2, 631–648 (2020). DOI 10.1016/j.matt.2019.12.019. Earlier intake: combined main text + Supplemental Information (mmc2.pdf). Current S2 extraction: authenticated standalone mmc1.pdf (8 pages; S2 PDF p7 / printed p6); see the source notes below. Code: github.com/jamiemfoster/Espresso.
**Stage(s):** grind, packing, extraction · **Kind:** runtime
**Status:** card-only — the card of record is `cameron2020.md`; component `cameron2020.extraction_bdf` is already registered and gated. This card logs the SI re-intake and the separate `cameron2020/figS2_pressure_tamp` source dataset; no new solver component.

## Scope and mechanism
Identical to the registered component: two-population (fines a₁ = 12 µm, boulders a₂ from Table S2) 1D saturated advection–extraction with intragranular spherical diffusion (Eq. 21) and cubic surface dissolution rate Γᵢ = k·c_si(c_si − c_l*)(c_sat − c_l*) (Eq. 16), Darcy flow with grind-indexed flux table (Eq. 26, Table S3), EY via Eq. 24. No new model appears anywhere in the upload; the SI is homogenization summary, parameter tables, numerics (control-volume in r, finite differences in z, ode15s), and two supplementary figures.

## Governing equations
Already transcribed in the registered implementation (paper Eqs. 16–26; SI Eqs. 1–13). Not repeated here — no equation in the upload differs from what is implemented. Known discrepancies (paper k = 6×10⁻⁷ vs released code 1×10⁻⁹; SI Table S2 surface-area self-inconsistency) are already documented in the card of record.

## Parameters
No new parameters. Table S1 provenance confirmed: c_sat = 212.4 kg/m³, c_s0 = 118.0 kg/m³, φ_s = 0.8272 all from Moroney 2016 thesis (registered as moroney2016); µ = 3.15×10⁻⁴ Pa·s (Kestin 1978); ρ_grounds = 330 kg/m³ (Franca 2005).

**Pressure convention unresolved:** SI Table S1 specifies 5-bar pump overpressure;
main-paper experimental figures use water/static-pressure labels, and S2 labels
6 and 9 bar. Table S5 contains model-scaled overpressure fluxes. The apparent
one-bar difference does not establish gauge reference, instrument node or a
measured pressure-transfer calibration. Preserve native labels; do not subtract
one bar or map S2 directly to MachineState. The earlier automatic conversion
assertion was unsupported; see the [current development guide](../research/ESPRESSO_DEVELOPMENT_GUIDE.md#r1r2-cameron-disclosure-and-the-pressureproduct-contract).

## Calibration and validation offered by the source
As documented in the card of record: D_s = 6.25×10⁻¹⁰ m²/s and k fitted to the GS-vs-EY sweep at 20 g in / 40 g out; model matches experiment only in the standard-flow regime (GS ≥ 1.7); the partially clogged branch is recovered *empirically* by reducing accessible surface area until EY matches (13.1/6.1/2.6 % EY gap at GS 1.1/1.3/1.5). Post-fit reconstruction, not independent validation.

## Assumptions and validity range
Unchanged from the card of record (saturated bed, isothermal, spherical dense grains, constant φ_s and bed depth per dose, Darcy flow, homogeneous flow regime only). SI Fig. S1 adds one supporting datum: N₂ physisorption at GS 2.5 shows minimal uptake at P/P₀ < 0.3 — no microporosity, no BET fit possible — buttressing the dense-sphere grain assumption.

## Interface mapping
Unchanged: GrindState ← dial; flux table + κ → BedState; extraction consumes BedState + MachineState.P_of_t → ShotResultState. S2 is source data only: its nominal pressure labels do not acquire a MachineState or puck pressure-drop mapping.

## Extractable data
Registry already holds the microstructure (Table S2) and 5-bar flux (Table S3) tables.
- **Fig. S2 — intaken:** [qualified numerical result](../analysis/sci_md_cameron_pressure_tamp_001/RESULT.md),
  [source/version and digitization notes](../analysis/sci_md_cameron_pressure_tamp_001/SOURCE_NOTES.md),
  dataset `cameron2020/figS2_pressure_tamp`. All 16 central summaries and their native
  horizontal coordinates are retained in four common nominal force groups F1–F4;
  exact nominal settings remain unresolved. Twelve bars are recovered; four are
  unrecoverable. Per-point n, central statistic and bar semantics remain unresolved.
  Under central reading bounds, 9−6-bar shot-time contrasts are positive at grind
  1.3 and negative at grind 1.5 for every group, with positive additive interactions.
  From F1 to F4 the pressure contrast decreases at both grinds. Displayed-extent
  sensitivity supports three grind-1.3 pressure contrasts and the F1 interaction;
  tamp endpoint conclusions remain unresolved or incomplete in that layer.
  No statistical significance, tamp insensitivity, choking mechanism, measured
  puck-pressure law or physical validation follows. G1 / RESEARCH_ONLY /
  RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING /
  NO_GOVERNING_PHYSICS_CHANGE; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
- **Table S5** (flux at 3/7/9 bar): *derived*, not measured — linear q ∝ P_tot scaling of the 5-bar column. Do not transcribe as data.
- **Table S4** (bed depth vs dose): trivial recomputation via Eq. 25; not data.

## Overlaps and conflicts
- `cameron2020.extraction_bdf` — this *is* that component's source; supersedes nothing, adds nothing to implement.
- `moroney2016` — confirmed as the provenance for c_sat, c_s0, φ_s.
- `wadsworth2026.permeability` — S2 supplies no new permeability input or pressure-convention calibration. The completed consolidated-input comparison is unchanged.
- `schmieder2023`, `pocketscience2024` — unaffected.

## Implementation disposition

No new model implementation. S2's bounded source analysis is complete; the main
paper's general recipe, temperature, mass tolerance, tamper accuracy and sampling
statements are recorded separately from S2-specific evidence. Restricted PDFs and
page renders remain outside Git. Cameron Figure 5, source audit and numerical
evidence are unchanged. No successor or runtime adoption is authorized.

VERDICT: source-data intake complete for S2; duplicate model source adds no new component.
