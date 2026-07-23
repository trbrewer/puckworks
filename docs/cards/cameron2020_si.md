# Model card: Cameron 2020 (SI re-intake — duplicate of registered component)

**Paper/thesis:** Cameron, Morisco, Hofstetter, Uman, Wilkinson, Kennedy, Fontenot, Lee, Hendon & Foster, "Systematically Improving Espresso: Insights from Mathematical Modeling and Experiment," *Matter* 2, 631–648 (2020). DOI 10.1016/j.matt.2019.12.019. Upload = main text + Supplemental Information (mmc2.pdf). Code: github.com/jamiemfoster/Espresso.
**Stage(s):** grind, packing, extraction · **Kind:** runtime
**Status:** card-only — the card of record is `cameron2020.md`; component `cameron2020.extraction_bdf` is already registered and gated. This card exists solely to log the SI re-intake and its deltas.

## Scope and mechanism
Identical to the registered component: two-population (fines a₁ = 12 µm, boulders a₂ from Table S2) 1D saturated advection–extraction with intragranular spherical diffusion (Eq. 21) and cubic surface dissolution rate Γᵢ = k·c_si(c_si − c_l*)(c_sat − c_l*) (Eq. 16), Darcy flow with grind-indexed flux table (Eq. 26, Table S3), EY via Eq. 24. No new model appears anywhere in the upload; the SI is homogenization summary, parameter tables, numerics (control-volume in r, finite differences in z, ode15s), and two supplementary figures.

## Governing equations
Already transcribed in the registered implementation (paper Eqs. 16–26; SI Eqs. 1–13). Not repeated here — no equation in the upload differs from what is implemented. Known discrepancies (paper k = 6×10⁻⁷ vs released code 1×10⁻⁹; SI Table S2 surface-area self-inconsistency) are already documented in the card of record.

## Parameters
No new parameters. Table S1 provenance confirmed: c_sat = 212.4 kg/m³, c_s0 = 118.0 kg/m³, φ_s = 0.8272 all from Moroney 2016 thesis (registered as moroney2016); µ = 3.15×10⁻⁴ Pa·s (Kestin 1978); ρ_grounds = 330 kg/m³ (Franca 2005).

**One convention finding not in the card of record:** Table S1/S3/S5 use pump *overpressures* of 3/5/7/9 bar while main-text Figures 3B and 4 label the same conditions 4/6/8/10 bar and "6 bar." The consistent 1-bar offset indicates figure labels are absolute pressure and the model's P_tot is gauge overpressure (P_abs − 1). Relevant to the ROADMAP pressure-node convention tables and to MachineState (which is defined as bar gauge overpressure): Cameron "6 bar" experimental conditions map to MachineState P = 5 bar.

## Calibration and validation offered by the source
As documented in the card of record: D_s = 6.25×10⁻¹⁰ m²/s and k fitted to the GS-vs-EY sweep at 20 g in / 40 g out; model matches experiment only in the standard-flow regime (GS ≥ 1.7); the partially clogged branch is recovered *empirically* by reducing accessible surface area until EY matches (13.1/6.1/2.6 % EY gap at GS 1.1/1.3/1.5). Post-fit reconstruction, not independent validation.

## Assumptions and validity range
Unchanged from the card of record (saturated bed, isothermal, spherical dense grains, constant φ_s and bed depth per dose, Darcy flow, homogeneous flow regime only). SI Fig. S1 adds one supporting datum: N₂ physisorption at GS 2.5 shows minimal uptake at P/P₀ < 0.3 — no microporosity, no BET fit possible — buttressing the dense-sphere grain assumption.

## Interface mapping
Unchanged: GrindState ← dial; flux table + κ → BedState; extraction consumes BedState + MachineState.P_of_t → ShotResultState. New note: apply the −1 bar absolute→gauge conversion when ingesting Cameron pressure labels into MachineState.

## Extractable data
Registry already holds the microstructure (Table S2) and 5-bar flux (Table S3) tables. Residual items, all marginal:
- **Fig. S2** (shot time vs tamp force, 98–290 N, at {6, 9 bar} × {GS 1.3, 1.5}, with error bars; ~16 points, digitizable): the only experimental data in the upload not already held. Documents tamp-force insensitivity of shot time and machine choking at 9 bar/fine grind. Mild relevance to packing and to G9's clogging framing; transcribe only if a tamp-sensitivity question arises.
- **Table S5** (flux at 3/7/9 bar): *derived*, not measured — linear q ∝ P_tot scaling of the 5-bar column. Do not transcribe as data.
- **Table S4** (bed depth vs dose): trivial recomputation via Eq. 25; not data.

## Overlaps and conflicts
- `cameron2020.extraction_bdf` — this *is* that component's source; supersedes nothing, adds nothing to implement.
- `moroney2016` — confirmed as the provenance for c_sat, c_s0, φ_s.
- `wadsworth2026.permeability` — the absolute-vs-gauge finding slightly sharpens the Cameron-flux reconciliation inputs (fluxes correspond to 5 bar gauge, not 6).
- `schmieder2023`, `pocketscience2024` — unaffected.

## Implementation estimate
Nothing to implement. Optional actions: (1) append the absolute/gauge pressure-convention note to the card of record and the ROADMAP pressure-node table; (2) optionally digitize Fig. S2 if tamp force ever becomes a live question. Both S.

VERDICT: skip — exact duplicate of the registered and gated cameron2020.extraction_bdf source; only deltas are a 1-bar absolute-vs-gauge pressure-label convention (worth propagating to the card of record) and a marginal tamp-force figure — effort S
