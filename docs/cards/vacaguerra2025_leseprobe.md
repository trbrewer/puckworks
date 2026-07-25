# Model card: Vaca Guerra (attrib.) dissertation — Ch. 1 Leseprobe (fundamentals excerpt)

**Paper/thesis:** Untitled monograph, ISBN 978-3-689-52688-7, publisher's *Leseprobe*
(reading sample), PDF built 2025-07-29. **The excerpt contains no title page, author,
year, affiliation, or DOI** — only book pp. 5–14 (Chapter 1, "Introduction"), truncated
mid-sentence in §1.7.1.
**Attribution (inferred, NOT printed):** the chapter is almost certainly the introduction
to Mauricio Vaca Guerra's cumulative dissertation (TUHH Hamburg, Institute of Solids Process
Engineering and Particle Technology, adv. S. Heinrich; industrial partner Nestlé —
Harshe, Fries, Palzer). Basis: the stated programme (fully-automated bean-to-cup machine →
PSD → tamping → percolation → per-component kinetics), Rosin–Rammler fitted only to the
coarse fraction, the surface-lipid-vs-milling-degree study, and citation of Fries (2021),
Pannusch et al. (2023) and de Vivo et al. (2022) all match the Vaca Guerra *J. Food Eng.*
2023a/b/c series exactly. **Confirm before the citekey is used in the registry.**
**Stage(s):** grind, packing, flow, extraction (all nominal — nothing in the excerpt is
implementable) · **Kind:** calibration (nominal; nothing to run)
**Status:** card-only

## Scope and mechanism
A literature-review "fundamentals" chapter, not a model. It states the thesis programme —
correlate grinder PSD and tamping compression with percolation conditions and the final
cup profile, for fully-automated machines — and then transcribes eighteen numbered
equations, **every one of which is adopted from a cited third party** (Vesilind 1980;
Corrochano et al. 2015; Crank 1975; Millington 1959; Moroney et al. 2015; Verhoff &
Furjanic 1983; Darcy). No new closure is proposed, no parameter is fitted, no experiment
is reported, and no figure carries data (Figs. 1.1 and 1.2 are schematics of the machine
workflow and the portafilter force balance). The excerpt ends mid-sentence at §1.7.1
before any results chapter begins. Its entire registry value is (a) as a pointer to the
underlying papers and (b) as a transcription-error ledger for equations the registry
already holds in better form.

## Governing equations
Transcribed as printed, with the source each is adopted from, and inline flags. **None of
these should be implemented from this document** — the registry already holds higher-fidelity
versions of 1.2, 1.6–1.8, 1.13 (see Overlaps).

**Grind / PSD**
- (1.1) `Q₃(x) = 1 − exp[ −(x/η)^γ ]` — Rosin–Rammler, after Vesilind (1980); fitted **only
  to the coarse fraction d_p > 100 µm** of a bimodal PSD, with "fines" defined as the volume
  fraction below 100 µm. *Symbol-collision flag:* the published Vaca Guerra 2023a abstract
  calls the same two parameters α (mean size) and β (uniformity); in this chapter η and γ.
  Worse, α and β are simultaneously used in Eqs. 1.6/1.7 as mass-transfer coefficients.

**Particle / bed density bookkeeping**
- (1.2) `ρ_part = ρ_solid (1 − ε_part)` — after Corrochano et al. (2015).
- (1.8) `ρ_bulk = ρ_part (1 − ε_bed)`.

**Intra-particle transport**
- (1.3) `J = D_b (∂C/∂x)` — Fick I. **Sign error: the minus sign is dropped as printed.**
- (1.4) `∂C_s/∂t = D_eff [ ∂²C_s/∂r² + (2/r) ∂C_s/∂r ]` — Fick II, spherical.
- (1.5) `Θ = (ε_part)^(−1/3)` — tortuosity, after Millington (1959).

**Mass transfer (both adopted from Moroney et al. 2015)**
- (1.6) `A = α S₁ (ε_part)^(4/3) (C_v − C_h)` — intragranular → intergranular.
  *Flag:* the text justifies the exponent via "D_eff = D/Θ", which alone gives ε^(1/3);
  the printed 4/3 additionally requires the porosity weighting of the volume-averaged flux
  (Millington–Quirk), a step the text does not write down. The exponent is right, the
  derivation as printed is incomplete — and it is grafted onto α, a **film coefficient**
  (m s⁻¹), not a diffusivity, so the tortuosity argument does not strictly apply to it.
- (1.7) `B = β S₂ (C_sat − C_h)` — surface dissolution; the surface soluble inventory is
  named φ_s0 but never enters an equation here.

**Bed compression**
- (1.9) `ε_bed = ε₀ exp(−ω σ)` — after Verhoff & Furjanic Jr (1983).
- (1.10) `ε_bed = ε₀ / (1 + ω σ)` — printed as an "alternative" form.
  **Conflict flag: 1.9 and 1.10 are not equivalent.** They agree only to first order in ωσ,
  and ω is numerically different between them; no criterion for choosing is given. Both send
  ε_bed → 0 as σ → ∞, i.e. **neither has a residual/close-pack porosity floor** — unphysical
  at espresso tamp stresses and fatal for any BedState.porosity(σ) closure built from them
  as printed.

**Bed force balance / flow**
- (1.11) `ΔF = F_f − F_w + F_g`
- (1.12) `F_f = A ΔP = (µ Q / K) Δz`
- (1.13) `Q = (K A / (µ L)) ΔP` — Darcy; stated valid for Re_p < 10 on a pore length scale.
- (1.14) `F_g = A (ρ_s − ρ_w) g Δz` — *flag:* uses the **solid** density with no (1 − ε_bed)
  solid-fraction weighting, so the bed's buoyant weight is overestimated by ≈ 1/(1−ε_bed);
  ρ_s is also never defined in the symbol list (collides with ρ_solid / ρ_part / ρ_bulk).
  Immaterial in practice — the text then neglects F_g.
- (1.15) `F_w = (ν µ_w D_p π / A) F Δz` — Janssen-type wall friction; ν horizontal load
  ratio (Poisson-like), µ_w wall friction coefficient, D_p portafilter diameter, F (N) the
  resultant axial force.
- (1.16) `∂P/∂z = (1/A)(∂F/∂z) = µQ/(K A) − ν µ_m P + (ρ_s − ρ_w) g`
  Four flags on one line: (i) **µ_w silently becomes µ_m** — and µ already denotes viscosity
  in the same equation; (ii) the substitution `F → P·A` needed to get from 1.15 to the
  `−ν µ_m P` term is not stated; (iii) the cross-reference is wrong — the text says "the
  force balance in Equation 1.12", but the force balance is 1.11; (iv) with z = 0 at the bed
  top and downward flow, a pressure *drop* requires ∂P/∂z < 0, yet the Darcy term is printed
  positive — the sign convention is never fixed.
- (1.17) `Eu = ΔP / (ρ_w v²)` — Euler number. *Flag:* Fig. 1.2's caption calls F_f "the
  inertial force from the fluid volume flow", but Eq. 1.12 defines F_f from **Darcy**, i.e.
  a viscous drag. Mislabelling, not a second model.
- (1.18) `v = u / ε_bed` — Dupuit–Forchheimer.

Symbols: Q₃ cumulative volume fraction (–); x particle size (m); η volumetric mean size (m);
γ uniformity exponent (–); ρ_solid intrinsic solid density, ρ_part particle density,
ρ_bulk bed bulk density, ρ_w water density, ρ_s (undefined; read as ρ_solid) (kg m⁻³);
ε_part particle porosity, ε_bed bed porosity, ε₀ porosity of the powder in repose (–);
J diffusive flux (kg m⁻² s⁻¹); D_b bulk, D_eff effective diffusivity (m² s⁻¹);
C_s intra-solid, C_v intragranular-average, C_h intergranular-average, C_sat saturation
concentration (kg m⁻³); r radial coordinate (m); Θ tortuosity (–); α, β mass-transfer
coefficients (m s⁻¹); S₁, S₂ specific surface areas (m² m⁻³); φ_s0 surface soluble volume
fraction (–); ω intrinsic compression factor (Pa⁻¹); σ bed axial compression stress (Pa);
F_f fluid, F_w wall-friction, F_g gravity force (N); F resultant axial force (N);
A bed cross-section (m²); Δz, L axial increment / bed length (m); ΔP pressure drop (Pa);
µ water viscosity (Pa s); µ_w ≡ µ_m wall friction coefficient (–); ν horizontal load
ratio (–); D_p portafilter diameter (m); K permeability (m²); Q volumetric flow (the text
writes ml s⁻¹ in the nomenclature but m³ s⁻¹ is required for 1.12/1.13 to close);
u superficial, v interstitial velocity (m s⁻¹); Re_p particle Reynolds number (–);
Eu Euler number (–); g gravitational acceleration (m s⁻²).

## Parameters
No parameter is fitted, measured, or reported by this work. Everything numeric in the
excerpt is a literature range quoted from a third party.

| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| η, γ (Rosin–Rammler) | not provided | m, – | — (fitted values are in the results chapters, absent here) |
| ω (compression factor) | not provided | Pa⁻¹ | — (declared "obtained from experimental data"; no value printed) |
| ε₀ (powder in repose) | not provided | – | — |
| ν, µ_w (wall friction pair) | not provided | – | — (both declared material/geometry dependent) |
| α, β, S₁, S₂, C_sat, D_eff | not provided | mixed | — |
| brew water temperature | 90 ± 5 | °C | nominal (Illy & Viani 2005) |
| espresso cup volume | 30–40 | ml | nominal (Parenti et al. 2014) |
| fines cutoff | < 100 | µm | nominal (definitional, this work) |
| espresso PSD span | 20–490 | µm | nominal (Petracco 2005a) |
| tamping stress (60 mm portafilter) | 30×10³ – 70×10³ | Pa | nominal (Petracco 2005a) |
| tamping force (same sentence) | 130 – 200 | N | nominal (Petracco 2005a) |
| intact cell pocket diameter | 25–40 | µm | nominal (Schenker et al. 2000) |
| assumed max intra-particle pore size | 40 | µm | assumed (Corrochano 2015; Melrose 2018) |
| bed permeability range | 3×10⁻¹⁴ – 8×10⁻¹³ | m² | nominal (attributed to Corrochano et al. 2015) |
| Darcy validity bound | Re_p < 10 | – | nominal |
| n (packing exponent), Kozeny–Carman prefactors | not provided | – | — (K–C is named in the abstract of the underlying paper but absent from this chapter) |

**Two numeric flags in the quoted values.**
1. *Tamp pair is internally inconsistent.* On a 60 mm portafilter (A = 2.83×10⁻³ m²),
   70 kPa ↔ 198 N ✓, but 30 kPa ↔ **85 N**, not 130 N (130 N ↔ 46 kPa). The stated range
   endpoints do not correspond. Use the stress, not the force, if either is ever quoted.
2. *Permeability range does not match the registry's record of its own source.* The excerpt
   attributes 3×10⁻¹⁴ – 8×10⁻¹³ m² to Corrochano et al. (2015); `romancorrochano2015.md`
   records that paper's measured Darcy range as 2.59×10⁻¹⁴ – 4.38×10⁻¹³ m². The upper bound
   here is ≈ 1.8× the carded value. The carded figure came from the primary table and should
   be preferred; do not propagate the excerpt's range.

## Calibration and validation offered by the source
**None.** No experiment, no fit, no comparison, no error metric, no figure with data appears
anywhere in the excerpt. The opening sentence asserts that the work "provides a verified
method for improving extraction consistency" — that claim is entirely forward-looking to
chapters not included in the sample and must not be recorded as validation of anything.

## Assumptions and validity range
Assumptions stated (all inherited, none tested here):
- Bimodal PSD with a 100 µm fines/coarse split; Rosin–Rammler describes only the coarse tail.
- Largest intra-particle pore ≤ 40 µm; skeletal porosity of small particles contains no
  closed pores.
- Diffusion inside the swollen particle is rate-limiting; external boundary-layer resistance
  negligible (Spiro & Page 1984).
- Surface solubles are already at C_sat an infinitesimal distance from the solid (Moroney).
- Gravity **and** wall friction are both neglected for a portafilter bed — the latter on the
  criterion "bed particle diameter ≥ 5", which is a garbled statement of the bed-to-particle
  *diameter ratio* > 5 rule the same chapter quotes correctly two pages earlier from
  Di Felice & Gibilaro (2004). Note that at d_p ≈ 20–490 µm in a 58–60 mm basket the ratio
  is 10²–10³, so the conclusion holds even though the stated criterion is mangled.
- Darcy-regime flow, Re_p < 10.

Where it breaks / is silent:
- **Silent on everything time-dependent**: no κ(t), no consolidation transient, no swelling,
  no fines migration, no CO₂, no wetting front, no pre-infusion. The bed is implicitly
  saturated and structurally fixed from t = 0.
- **Silent on temperature dependence** despite naming it as a first-order driver in §1.3.
- Compression laws 1.9/1.10 have no porosity floor and are unbounded in σ (see flag).
- No inertial/Forchheimer correction; Eu is defined but never used.
- No chemistry: species are named (caffeine, trigonelline, CQA, lipids) but no per-species
  equation, partition coefficient, or inventory appears.

## Interface mapping
Inputs consumed: nothing, as an excerpt. Had the equations been original they would map as
GrindState(mean_radius_m, fines_fraction) → (1.1); BedState(porosity, sigma) → (1.9/1.10);
BedState(k_m2, depth_m, area_m2) + MachineState(P_of_t) → (1.13).
Outputs produced: none reach any contract from this document.
Couplings: none. There is no runtime component here and no calibration provider — a
calibration provider needs numbers, and this chapter supplies none. **No adapter work is
implied.** The one structurally interesting item for the registry is that 1.9/1.10 is a
BedState.porosity ← BedState.sigma closure of exactly the shape the registry currently
lacks; but it arrives here parameter-free and unbounded, so it is a *pointer*, not a closure.

## Extractable data
**Nothing to transcribe.** No tables, no data figures, no supplementary material, no code or
repository, no data-availability statement (the excerpt contains no front or back matter at
all). Figs. 1.1 and 1.2 are line-art schematics.

The actionable output of this intake is an acquisition list. Note that **no `vacaguerra*` card
currently exists in the project files or in REGISTRY_STATE.md**, so all three of the
underlying journal papers are genuine, un-carded targets — and two of them sit directly on
named backlog items:

1. **Vaca Guerra, Harshe, Fries, Rothberg, Palzer, Heinrich (2023a), *J. Food Eng.* **340**,
   111301**, DOI 10.1016/j.jfoodeng.2022.111301 — "Influence of particle size distribution on
   espresso extraction via packed bed compression." Contains the fitted compression model
   ε_bed(σ; α, β) that Eqs. 1.9/1.10 are the skeleton of, plus a modified Kozeny–Carman
   permeability prediction validated against their own measurements. **Highest-value target**:
   it is the missing σ → porosity → κ chain and a direct competitor to
   `wadsworth2026.permeability` and `romancorrochano2015`. Key reported finding to test:
   lower bed porosity at *lower* size uniformity β even at *larger* mean size α — i.e.
   polydispersity, not fineness, sets the packing floor.
2. **Vaca Guerra et al. (2023c), *J. Food Eng.* **354**, 111554** — "Tuning the packed bed
   configuration for selective extraction of espresso non-volatiles based on polarity."
   Per-species (caffeine, trigonelline, chlorogenic acid) HPLC kinetics vs PSD →
   **open backlog item "extraction: multi-class solute chemistry."** Sits alongside
   `angeloni2023`, `schmieder2023`, `pannusch2024` as a candidate for that item.
3. **Vaca Guerra, Harshe, Fries, Payan Lozada, Atxutegi, Palzer, Heinrich (2023b),
   *J. Food Eng.*, S0260877423005113** — "Modeling the extraction of espresso components as
   dispersed flow through a packed bed." Tracer-pulse RTD experiments in a real espresso bed;
   reported Bodenstein number **falling from 16.7 to 9.0 as extraction progresses** — a
   directly measured, time-resolved bed-structure signal, and the first axial-dispersion
   closure in this corner of the registry. Relevant to `bed_dynamics` κ(t) and to
   `brewer2026.streamtube`'s heterogeneity claim.
4. The **full monograph** (ISBN 978-3-689-52688-7), if the surface-lipid-vs-milling-degree
   analysis promised in §1.3.1 is not in any of the three papers. Lower priority; verify
   authorship and title first.

## Overlaps and conflicts
- **`romancorrochano2015` / `romancorrochano2017_permeability` (packing, calibration):**
  Eqs. 1.2 and 1.8 are verbatim their Eqs. 6b and 6a, and the quoted permeability range is
  theirs (mis-quoted — see Parameters flag 2). This excerpt is strictly downstream; it adds
  nothing and conflicts on one number.
- **`moroney2016` (extraction, calibration):** Eqs. 1.6 and 1.7 are Moroney's double-porosity
  transfer terms restated without their surrounding closure, inventory accounting, or
  parameters. Lower fidelity, no new content.
- **`wadsworth2026.permeability` (packing, calibration, registered):** the excerpt offers no
  permeability closure at all, so no competition *here* — but target (1) above would compete
  directly, and on the tamped/compressed regime where Wadsworth is currently extrapolating.
  That is the strongest reason to acquire it.
- **`abedi2025` (packing, calibration):** same gap, opposite failure. Abedi has stress–
  compressibility data on *uncharacterized* grinds; this chapter has a compression *equation*
  with no parameters and no PSD link. Target (1) is what closes both.
- **Backlog "bed_dynamics: κ(t) = κ₀·f(P, ε, E)":** untouched here (the excerpt's bed is
  static), but target (3)'s Bodenstein decline is a candidate observational constraint.
- **Backlog "grind: PSD models beyond bimodal":** Eq. 1.1 is a coarse-tail-only
  Rosin–Rammler, i.e. squarely *inside* the bimodal framing the backlog wants to move beyond.
  Complements `wadsworth2026_grindmap` only as a fitting convention.
- **`lee2023`, `cameron2020.extraction_bdf`:** no interaction; nothing in this excerpt
  addresses porosity–flow feedback or EY accounting.

## Implementation estimate
Zero implementation work; nothing here is implementable. Effort is entirely acquisition:
retrieving the three *J. Food Eng.* papers (all behind Elsevier paywalls except 2023a, which
ResearchGate lists as full-text available) and confirming the monograph's authorship and
title, then a fresh intake session per paper — expect **M** for 2023a (compression +
permeability model with data tables), **M** for 2023b (dispersion model + RTD data),
**S–M** for 2023c (kinetics data, likely data-only). No gate design applies to this card.

VERDICT: skip — a publisher's reading sample containing only a literature-review chapter:
eighteen equations all adopted from sources the registry already holds in higher fidelity,
zero parameters, zero data, zero validation, and a handful of transcription errors — its
only value is as the acquisition pointer to the three Vaca Guerra *J. Food Eng.* 2023 papers
recorded above, two of which sit on named backlog items — effort S.
