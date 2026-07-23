# Model card: Cooper 2021 — moroney2019 replication, errata, and wetting-front IC (Quantitative Café)

**Paper/thesis:** Cooper, M., "Modeling Extraction," Quantitative Café (blog), 2021-11-14. https://quantitativecafe.com/2021/11/14/modeling-extraction/ — with public Jupyter notebook: https://github.com/quantitativecafe/blog/tree/main/tds-vs-ey-model (also runnable on Binder). No DOI. Author credits "indispensable" help from Dr. Kevin Moroney (first author of the replicated paper) — the errata below are author-confirmed, not hobbyist conjecture.
**Stage(s):** extraction · infiltration · observables · **Kind:** calibration (nothing here runs in the shot chain; the deliverables are parameter corrections to a registered card, an executable reference implementation, and an initial-condition recipe)
**Status:** card-only

## Scope and mechanism
Independent replication of the 1-D two-grain linear-driving-force extraction model of Moroney et al. 2019 (PLoS ONE; registry card moroney2019), against the same cylindrical Philips brew-chamber dataset. Three contributions: (1) two errata in the 2019 paper's parameter reporting, discovered during replication and resolved with the original author's help; (2) a sequential-wetting initial-condition modification — fill the dry puck one depth level at a time (dissolving coffee as the front advances) before starting the saturated-flow model — which fixes the unphysical clean-water early transient of the fully-wetted IC; (3) explicit TDS/EY brewing-control-chart trajectory equations mapping the model's exit concentration to standard shot observables. No new physics and no new experimental data; the model equations are exactly moroney2019's Eqs. 17–27 (see that card).

## Governing equations
**Erratum A — species-specific diffusivities (corrects moroney2019 §"1-D reduction").** The 2019 paper indicates a single effective diffusion coefficient D_v for both solid species; the authors actually used two, D_v1 and D_v2, related to the fitted mass-transfer coefficients by (blog, unnumbered; same relation as moroney2019 Eqs. 21–25):

h_sli = D_vi / d_si,  i = 1 (small/fine species), 2 (large/coarse species)

where h_sli is the mass-transfer coefficient and d_si the grain diameter of species i. This resolves the inconsistency flagged in the moroney2019 card ("a single D_v cannot be recovered from the fitted pairs") — there was never a single D_v.

**Erratum B — h_sl scaling (corrects moroney2019 Table 2).** The h_sli values printed in the 2019 paper are the CFD-scaled values (scaled for the ANSYS Fluent setup), accidentally reported in place of the originals. Correction, as stated:

h_sli(true) = h_sli(reported) / ρ_l,  ρ_l = 965.3 kg m⁻³ (water at 90 °C)

i.e., a ~10³ correction. Operational rule only — the blog does not restate Fluent's internal units; the notebook is the executable reference.

**Sequential-wetting initial condition (blog, algorithmic, no equation numbers).** Instead of the fully-wetted IC c_l(z,0)=0, c_s(z,0)=c_s0 (moroney2019 Eq. 27): advance water into the dry bed one discretized depth level at a time, running the phase-transfer kinetics during the fill, until the front reaches the bed exit; the resulting c_l(z), c_si(z) profiles become the initial condition for the standard saturated model. At first drip, liquid near the top is partially depleted of solids while the bed bottom remains at original concentration; the exit concentration then starts high (~300 kg m⁻³) and decays monotonically, rather than starting at zero. The blog does not specify the fill-stage timing/flow bookkeeping in prose — implementation details live in the notebook.

**Observable trajectory (blog, unnumbered).** With Q the volumetric flow rate and c_l(t) the exit concentration:
m_s(t) = Q ∫₀ᵗ c_l(u) du  (mass of solubles in cup)
m_l(t) = Q · ρ_l · t  (mass of liquid in cup)
TDS = 100 · m_s/m_l,  Extraction Yield = 100 · m_s/m_0
with m_0 the dry puck mass. Plotted parametrically in t, this traces the shot's path on the brewing control chart (ticks = shot time).

## Parameters
No new measured or fitted parameters. Corrected values below are derived here by applying Errata A–B to the moroney2019 Table 2 values (registry-side computation; verify against the notebook before use):

| quantity | Fine: single | Fine: 2G small | Fine: 2G large | Coarse: single | Coarse: 2G small | Coarse: 2G large | units | source |
|---|---|---|---|---|---|---|---|---|
| h_sl (corrected = reported/965.3) | 4.471×10⁻⁷ | 5.305×10⁻⁷ | 1.481×10⁻⁶ | 9.871×10⁻⁷ | 1.721×10⁻⁷ | 3.005×10⁻⁷ | m s⁻¹ | derived (Erratum B on fitted values) |
| D_vi = h_sli·d_si | 1.423×10⁻¹¹ | 1.335×10⁻¹¹ | 8.34×10⁻¹⁰ | 4.52×10⁻¹¹ | 6.08×10⁻¹² | 2.78×10⁻¹⁰ | m² s⁻¹ | derived (Erratum A) |

| symbol | value | units | source |
|---|---|---|---|
| ρ_l | 965.3 | kg m⁻³ | nominal (water, 90 °C) |
| all bed/grind/flow parameters | — | — | inherited unchanged from moroney2019 Table 2 |

Sanity check (registry-side): corrected small-species diffusivities ~10⁻¹²–10⁻¹¹ m² s⁻¹ are physically sensible for hindered diffusion in a porous grain; the *uncorrected* values would imply D ~ 10⁻⁸ m² s⁻¹, exceeding free aqueous diffusion — independent support for Erratum B beyond author confirmation.

## Calibration and validation offered by the source
- With both errata applied, the replicated 1-D two-grain model gives what the author calls an excellent match to moroney2019 Fig. 6(b) (fine grind exit concentration, ~0–250 s) — shown as an overlay plot; no RMSE quoted. This is a *replication check against the original fit*, not new validation: same data, same fitted parameters.
- With the sequential-wetting IC and *unmodified* h_sl values, the fit to the same experimental points remains good ("quite a good fit"), now with a physically sensible high-concentration first drop (~300 kg m⁻³ at t=0⁺) instead of the original model's near-zero early prediction. Author explicitly notes the h_sl were fitted under the old IC and refitting would likely improve this — not done in this post.
- TDS/EY trajectory and depth-resolved fine/coarse concentration profiles are model outputs only; no measured trajectory exists (author proposes measuring TDS at varying shot times as a cheap parameter-estimation route — an idea, not an experiment).
- Overall: post-fit reconstruction inherited from moroney2019, plus a qualitative-only IC improvement. Nothing here is independent experimental validation.

## Assumptions and validity range
- Inherits every assumption of moroney2019's 1-D reduction: saturated Darcy flow at fixed Q, static incompressible bed, constant porosity/permeability, LDF kinetics, single lumped solute, isothermal, no consolidation or fines migration.
- The wetting-front stage is kinematic bookkeeping, not hydraulics: no capillarity, no pressure transient, no unsaturated-flow physics (contrast foster2025's sharp-front model, which predicts the *timing*; this recipe assumes the front simply sweeps down and asks what it dissolves). Fill-stage kinetics use the same h_sl as the saturated stage — an assumption, since transfer into a moving partially-saturated front plausibly differs.
- Validated regime is the Philips chamber only: 60 g dose, 59 mm diameter, 40.5 mm depth, 563 µm nominal particles, 250 ml min⁻¹ — the author himself stresses these are not espresso-typical (vs ~18 g, ~200 µm, ~12 mm, ~60 ml min⁻¹) and defers a typical-espresso refit to future work (no such follow-up is claimed in this post).
- Erratum corrections apply to moroney2019 Table 2 h_sl values specifically; whether the 2019 paper's *CFD-side* reported quantities need the same treatment is not addressed.
- Silent on: pressure-driven operation (fixed Q only), multi-species chemistry, temperature, radial structure.

## Interface mapping
Inputs consumed: none at runtime — no runtime component.
Outputs produced, as a calibration/erratum provider: (a) corrected h_sli and species-split D_vi superseding the values currently tabulated in moroney2019.md → **registry action: annotate moroney2019.md Table 2 with Errata A–B before anyone consumes those numbers** (same class of hazard as the grudeva Issue 2a decade-scale unit error — a printed-value error that would silently propagate); (b) TDS/EY trajectory equations are the trivial c_exit(t)→ShotResultState(tds_pct, EY_pct, traces) adapter, already how the registry computes observables — nothing new to build; (c) the sequential-wetting IC is a concrete, minimal design pattern for the open backlog item "infiltration↔extraction coupling: delay extraction per depth cell until front passage" — it demonstrates the coupling can be a *pre-shot pass* handing a modified initial state to any saturated extraction stage (cameron2020.extraction_bdf included), rather than a runtime co-simulation; foster2025.infiltration would supply the front timing the recipe lacks.
Couplings: offline only.

## Extractable data
- No new measurements anywhere in the post; experimental points shown are moroney2019's Fig. 6(b) Philips data (Moroney 2015 remains the flagged primary acquisition target).
- **Code: published and public** — Jupyter notebook on GitHub (quantitativecafe/blog, tds-vs-ey-model/) and Binder. Worth mirroring into puckworks as the executable reference implementation of the moroney2019 1-D two-grain model with errata applied (license unverified — check repo before vendoring).
- Corrected-parameter table above → fold into data/moroney2019_table2.csv as corrected columns with erratum provenance, rather than a separate dataset.
- Comment thread bonus: Mark Al-Shemmeri's pointer to the Roman-Corrochano EngD thesis (already carded: romancorrochano2017_*) and an open offer of contact — a live correspondence channel adjacent to the Moroney group.

## Overlaps and conflicts
- **moroney2019** (data-only): direct target — this post corrects its Table 2 h_sl values and resolves that card's flagged single-D_v inconsistency. Supersedes the printed parameter values; complements everything else. The moroney2019 card's transcription-check gate ("reproduce RMSE 5.81/6.23 kg m⁻³ from Table 2 parameters") must use the *corrected* values or it will fail by construction.
- **moroney2016** (calibration): same group/dataset lineage; unaffected numerically (different model), but the D_v magnitudes above are a useful cross-check against its kernel-fit diffusivities.
- **cameron2020.extraction_bdf** (extraction, runtime): unaffected parameters; the wetting-IC critique applies equally (Cameron also starts saturated), and the pre-shot-pass pattern is the cheapest route to fixing its early TDS transient.
- **foster2025.infiltration** (infiltration, runtime): complementary — foster gives front dynamics with no solute; this gives front-passage dissolution with no dynamics. Their composition is essentially the backlog coupling item.
- **Backlog "infiltration↔extraction coupling"**: this post is the existence proof, at toy fidelity, that the coupling changes the early transient in the right direction while preserving the late-time fit.
- **Backlog "observables"** / mckeonaloe IR finding: the control-chart trajectory formalizes the (TDS, EY, t) path object; consistent with the registry finding that fixed-ratio metrics collapse onto EY — here ratio varies with t, so the trajectory carries real information.

## Implementation estimate
No component to implement. Registry actions: (1) erratum annotation on moroney2019.md + corrected columns in the Table 2 transcription — S; (2) mirror the notebook as reference code — S; (3) if/when the infiltration↔extraction backlog item is designed, cite this as the minimal pattern and pull the fill-stage bookkeeping from the notebook rather than re-deriving — the design work belongs to that item, not this card. Gate for the corrected values: reproduce the blog's Fig. 6(b) overlay from corrected h_sl (the notebook makes this a run-button check).

VERDICT: data-only — no new physics or measurements, but author-confirmed errata that correct a registered card's parameter table (a silent ~10³ error otherwise), a public executable reference implementation, and a working minimal pattern for the open infiltration↔extraction coupling backlog item — effort S
