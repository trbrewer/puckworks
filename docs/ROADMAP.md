# puckworks — docs/ROADMAP.md (rev. 2, incorporating review)

Synthesized from REGISTRY_STATE.md (v0.1.0, July 2026) and the 26 model cards on
file. Every claim traces to a named card or to REGISTRY_STATE; statements
sourced *only* from REGISTRY_STATE (registered-component status, held datasets,
DE1 fixture A κ=1.196, backlog items) are tagged **[RS]** so the document is
auditable without the registry file open. Card disagreements are surfaced, not
resolved. Living document — see §7.

Card corpus (VERDICT · effort): foster2025_2 (implement-now · M; supersedes
foster2025.md — **do not cite foster2025.md except as historical**) ·
wadsworth2026_inertial (implement-now · S) · wadsworth2026_grindmap
(calibration-provider · S) · waszkiewicz2025 (implement-now · S) · pannusch2024
(implement-now · M) · grudeva2023 (implement-now · M) · grudeva2026
(implement-later · M) / grudeva2026_2 (implement-now · M) **[same paper,
conflicting verdicts — §5.1]** · mo2023 (calibration-provider · S) · mo2023_2
(implement-later · M) · fasano2000_partI (implement-later · M) ·
fasano2000_partII (implement-later · M) · fasano2000_partIII (skip · L) ·
lee2023 (implement-later · S) · romancorrochano2017_extraction
(implement-later · M) · romancorrochano2017_permeability (data-only · S) ·
moroney2016 (calibration-provider · S) · liang2021 (calibration-provider · S) ·
egidi2024 (data-only · S) · schmieder2023 (data-only · S) · bruno2026
(data-only · S) · ellero2019 (skip · L) · hendon2020 (skip · S) · cameron2020,
wadsworth2026 = already-registered components' cards of record **[RS]**.

---

## 0. STATUS AND VALIDATION-STRENGTH GLOSSARY

Status labels (VERDICT lines + registry lifecycle):

| Label | Meaning | May enter runtime chain? | Required evidence |
|---|---|---|---|
| `gated` | Implemented and passed registry gates against accepted data | yes | independent or accepted regression gate |
| `verification-gated` | Numerically reproduced / internally checked (model-vs-model, mass budget), no experimental validation | limited: experimental/verification configs only, labelled as such | model-vs-model or budget gates, cited |
| `gated + data` | `gated` with an independent (non-circular) dataset behind at least one gate | yes | named dataset + gate script |
| `implement-now` | Roadmap action item (card verdict) | not until its gate passes | phase-specific gate in §3 |
| `implement-later` | Worth keeping; blocked by data, adapters, or a harness | no | stated trigger condition |
| `calibration-provider` | Supplies priors/parameters/reference relations offline | no, unless wrapped by a runtime component | transcribed data + provenance |
| `data-only` | Data valuable, equations not adopted | no | data intake + manifest (§3 Phase 0) |
| `skip` | No implementation or data value beyond a recorded pointer | no | — |

Validation-strength vocabulary used throughout (§2, §6):
**independent** (data not used in fitting the thing being tested) ·
**post-fit reconstruction** (model reproduces the dataset its parameters were
fitted to — a consistency check, not validation) · **verification**
(model-vs-model / asymptotic / budget) · **qualitative** (shape/mechanism only,
no error metrics). Never promote a lower rung to a higher one when quoting a
card — house rule **[RS]**.

Status promotions (e.g. `verification-gated` → `gated`) require a §7.1
changelog entry citing the dataset and gate script.

---

## 1. PROCESS MAP

Stage-by-model matrix. **Bold** = registered component **[RS]**.
Kind: R = runtime slot candidate · C-prior = offline calibration consumed by a
runtime component · C-gate = gate/reference data or analytic check ·
C-obs = observables/measurement kernel.

| Stage | Component / card | Kind | Fidelity notes |
|---|---|---|---|
| grind | **cameron2020** microstructure tables | C-prior | measured, EK43 dial 1.1–2.3 only |
| grind | wadsworth2026_grindmap ⟨R⟩=βG+R₀ + 22 PSDs | C-prior | Mahlkönig-specific, G 1–11; card forbids porting dials without refit; PSD zip published |
| grind | schmieder2023 d₃₂ / liang2021 S1 PSDs / waszkiewicz2025 PSD | C-gate | third/fourth/fifth grinder reference points, data only |
| packing | **wadsworth2026.permeability** k(⟨R⟩,φ_p) | C-prior | validated untamped φ_p 0.37–0.67; tamped = extrapolation |
| packing | **brewer2026.pack_generator** | C-prior | Boolean spheres, columnar heterogeneity |
| packing | romancorrochano2017_permeability (K–C ×2) | C-gate | equations are poor blind predictors (fitted per-grind n); Table 6.1 tamped κ is the asset |
| packing | mo2023 (real-geometry k, ε, τ) | C-gate | ε anchored circularly to cameron2020's 0.17 |
| machine | foster2025_2 Eqs. 2–7 (pump + headspace) | R | the named "machine mode" source **[RS]**; not yet implemented; pump curve is nominal |
| machine | waszkiewicz2025 brewer quadratic (Fig. 2B) | C-prior | pump→basket pressure-drop adapter data, one rig |
| infiltration | **foster2025.infiltration** (recorded-pressure form) | R | gated parameter-free; fine grind only, coarse front non-uniform |
| infiltration | grudeva2023 / grudeva2026 sharp front | R | deliberately trivial front; exists to feed extraction (nests under Foster, P5) |
| flow | **brewer2026.lb_reference / lb_taichi** | C-gate | Stokes-regime verification twins only |
| flow | wadsworth2026_inertial (Forchheimer) | R | closed-form wrapper on Darcy; γ from ceramics fit, never coffee-calibrated; strict-SI k input |
| flow | mo2023 Forchheimer (k, k₁) pairs | C-prior | 24 real-geometry pairs; k₁ units internally inconsistent (§5.3) |
| flow | fasano2000_partI flux quadrature (8.25) | R | inside the fines-migration model, not standalone |
| extraction | **cameron2020.extraction_bdf** | R | gated workhorse; saturated bed, single lumped solute, EY ceiling 29.6% |
| extraction | grudeva2023/2026 reduced model | R | adds dry-bed start + saturated plateau; ~100× cheaper; verification only (2026) / post-fit vial reconstruction (2023) |
| extraction | pannusch2024 two-grain multi-solute | R | 4 named solutes, T & flow constitutive laws; consumes Q(t)+T(t), not pressure; constant porosity |
| extraction | romancorrochano2017_extraction | R | MW-resolved Deff, parameter-free grind→Deff chain; lumped bed |
| extraction | egidi2024 RBF ADR | R (not adopted) | duplicates cameron lineage, prescribed q; verdict data-only |
| extraction | mo2023_2 swelling extraction core | R | Cameron lineage at lower solute fidelity; value is the swelling machinery |
| extraction | moroney2016 composite asymptotics | C-prior / C-gate | closed-form surrogate/fitter; constant-ΔP baked in |
| extraction | liang2021 equilibrium desorption | C-gate | immersion endpoint K·E_max; long-time ceiling check |
| bed_dynamics | **brewer2026.streamtube** | R | static lognormal heterogeneity; σ closure on 3 points |
| bed_dynamics | waszkiewicz2025 poroelastic κ(P, Φ(t)) | R | closed-form; public rig dataset; quantitative only at high P; constants per rig/coffee/grind |
| bed_dynamics | mo2023_2 swelling → ε_b(t) → k(t) | R | headline fixed-ΔP claims unvalidated |
| bed_dynamics | fasano2000_partI fines migration (3-state + free boundary) | R | **LANDED** `fasano2000_partI.fines_migration` — fasano-STRUCTURED (our closures, zero identified params in source); reproduces the mechanism (mass balance 8.33, Lemma 8.1/8.3, nonmonotone q∞(p₀)), not their curve |
| bed_dynamics | fasano2000_partII porosity law (8.69) | R | **DEFERRED (no port possible)** — existence/uniqueness theory, ZERO numeric constitutive functions (δᵢ,g,h,ξ,ε_*,ε*,K all "not provided"). Serves as the STRUCTURAL template for the compaction/strain branch of κ(t)=κ₀f(P,ε,E); any Eq. 8.69 implementation is a NEW fasano-STRUCTURED closure (our chosen forms, cited for structure only), entering by its own gate when this κ(t) item is picked up |
| bed_dynamics | lee2023 two-pathway instability | R | **LANDED** `lee2023.feedback` — extraction→ε→κ feedback branch; reproduces the paper's behaviour + negative result (decline needs unphysical ρ_c=798; ρ_c=399 plateaus). Real payoff still the N-tube graft onto streamtube |
| observables | liang2021 oven-drying/retention kernel (Eqs. 18–24) | C-obs | ready-made measurement kernel |
| observables | grudeva2023 vial-splitting kernel (6.15–6.16) | C-obs | fraction-resolved measurement adapter |
| observables | schmieder2023 fraction/exponential kernel | C-obs / C-gate | empirical; per-solute λ, c₀ |

### Parallel clusters

**P1 — extraction runtime (COMPETE → comparison harness).**
cameron2020 vs grudeva2023/2026 vs pannusch2024 vs romancorrochano2017 vs
egidi2024 vs mo2023_2's core. All two-population saturated-diffusion lineage
(Melrose/Moroney/Cameron per the cards) but with incompatible conventions. The
harness (item 2.1) must run all on matched inputs against the shared gate
datasets; moroney2016 and liang2021 sit alongside as analytic/endpoint sanity
gates, not competitors. **Normalization hazards — never merged silently:**

| Quantity | cameron2020 | grudeva | egidi2024 | pannusch2024 | required adapter |
|---|---|---|---|---|---|
| soluble inventory reference | per bed volume, c_s0=118/φ_s | per grain volume incl. internal pores | c₀=200 kg/m³ per grain | per-solute c_s0 | inventory normalization (ledger A5) |
| dissolution kinetics | nonlinear surface dissolution | linear capped transfer | quadratic-in-surface | Sherwood-correlated linear | none — report per-law, do not map |
| flow input | pressure / flux table | fixed q or P-derived q | prescribed constant q | measured Q(t)+T(t) | flow provider (ledger A2) |
| c_sat | 212.4 kg m⁻³ | 170 (2023) / 224 (2026) | 212.4 | per-solute K(T) | config field, no silent merge (§5.4) |
| output | EY/TDS | outlet trace / per-vial | EY | per-solute traces | observable adapter (ledger A3, §5.10) |

**P2 — κ(t)/bed_dynamics mechanism (COMPETE → discrimination harness).**
Five mechanisms claim the same flow-history residuals: (a) dissolution-driven
poroelastic Φ(t) (waszkiewicz2025, rising flow at 9 bar), (b) swelling
(mo2023_2 — predicts *falling* flow at fixed ΔP; enters the rising-flow question
with the wrong sign, per its card), (c) fines migration + compact layer
(fasano2000_partI; ellero2019 cites independent support), (d) flow-induced
compaction/elastic recovery (fasano2000_partII), (e) extraction→κ feedback
(lee2023). **Null-first testing ladder** (every challenger must beat the rung
below it on the same traces before claiming a residual):

1. Recorded-pressure Darcy, constant κ (RC-1 floor).
2. foster2025_2 pump/headspace null — reproduces a mid-shot flow minimum with
   *no* bed mechanism (no extraction, degassing, swelling, or rearrangement).
3. waszkiewicz2025 equilibrium poroelastic curve only (static κ(P)).
4. waszkiewicz2025 time-dependent Φ(t) with its own empirical m_d(t) sigmoid.
5. Challengers: mo2023_2 swelling, fasano I migration, fasano II compaction,
   lee2023 feedback — and the Cameron-coupled Waszkiewicz variant (RC-3b),
   which is a **new coupled model, not validated by the Waszkiewicz paper**.

Discriminating observables named on the cards: Fasano Fig. 8.4 flow-reversal
replay (migration vs compaction), pressure-step protocols (partII/III endpoint
result), on/off rebrewing without dissolution (waszkiewicz Fig. 10
delamination), post-extraction bottom-high porosity gradient (mo2023 Figs.
6/14/16).

**P3 — fine-grind EY dip hypotheses (COMPETE — hypothesis registry, not a slot).**

| Hypothesis | Card | Required observable | Expected signature |
|---|---|---|---|
| static channeling σ(φ₁) | **streamtube** | fitted σ vs fines/grind | monotone σ(φ₁) relation |
| incomplete wetting, tubes at k→0 | foster2025_2 | per-grind first-drip timing; CT saturation | delayed/partial wetting at fine grinds |
| dissolution–flow instability + saturation ceiling | lee2023 | pathway-resolved depletion | fast pathway saturates/depletes first |
| size-exclusion entrapment | romancorrochano2017_extraction | y₀(grind) | extractable inventory falls with coarseness |
| flow inhomogeneity + pressure | pannusch2024 | flow+pressure at fixed grind | qualitative only — pannusch is a no-channeling constant-porosity model; this is a pointer, not a mechanism |

schmieder2023's non-monotonic cup mass at fixed flow with pressure(grind) is a
shared external constraint on all five.

**P4 — permeability closures (TIER + one shared gap).**
**wadsworth2026.permeability** (percolation, top tier untamped) over
Carman–Kozeny variants (romancorrochano2017_permeability, waszkiewicz2025
Eq. 8, mo2023_2 internal, moroney2016 κ=3.1). A fidelity ladder, not a race —
**use the Roman-Corrochano K–C equations only as explanatory diagnostics; the
actual asset is Table 6.1** (poor blind predictors, agreement only via fitted
per-grind n, per the card). All closures are unvalidated tamped; three cards
independently point at outlet/screen resistance — promoted to gap **G9**.
Tiering: wadsworth2026 prior → per-rig fitted κ (DE1 fixture A κ=1.196 **[RS]**)
→ K–C forms as diagnostics only.

**P5 — infiltration (TIER).** foster2025_2 (pump/headspace/capillary, CT-gated)
over grudeva sharp fronts (trivial by design). The cards state these nest:
Foster front supplies t₀(z) to Grudeva's extraction. Not a competition.

**P6 — flow inertia (TIER with an internal conflict).** wadsworth2026_inertial
(runtime closure) tiers over mo2023 (data provider) and both over the LB twins
(Stokes-only). Regime estimates conflict — §5.2. Notation rule adopted:
**Fo_F = Forchheimer number** (wadsworth2026_inertial Eq. 5.2b);
**Fo_diff = Fourier diffusion number** (pannusch2024 thesis framing: fines
Fo_diff>1, coarse <1). Bare "Fo" is banned in registry code and docs.

---

## 1A. CONTRACT / ADAPTER LEDGER

Every schema change or adapter named on a card, in one place. Contracts are
v0.1 **[RS]**: GrindState, BedState, MachineState, ShotResultState.

| # | Needed adapter / schema change | Required by | Why it matters |
|---|---|---|---|
| A1 | Pressure-node model: pump outlet p_p / headspace p_h / basket gauge P_basket / bed drop ΔP_bed as distinct fields | foster2025_2, waszkiewicz2025, RC-3 | prevents double-counting pipe/headspace/brewer losses; see RC-3 node table and §5.9 |
| A2 | Flow-rate trace Q(t) (+ T(t)) provider on MachineState | pannusch2024, mo2023_2 fixed-q mode, RC-4 | pannusch consumes flow and temperature, not P_of_t |
| A3 | Per-solute outputs on ShotResultState | pannusch2024, bruno2026 linkage, RC-4 | current contract is TDS/EY-centric |
| A4 | SoluteInventory object (per-species initial chemistry) | bruno2026 → pannusch2024 / romancorrochano2017 | Bruno provides inventory, not kinetics; no contract carries species today |
| A5 | Inventory reference-volume normalization (per-bed ↔ per-grain ↔ per-solute) | P1 harness, grudeva ↔ cameron | see P1 hazards table |
| A6 | Fines-radius / PSD-moment fields on GrindState | grudeva, wadsworth2026_grindmap, romancorrochano2017, mo2023_2 (100 µm split) | several models need more than mean radius + fines fraction |
| A7 | Forchheimer coefficient / FlowLaw object (k_I) + strict κ→SI-k unit adapter | wadsworth2026_inertial, mo2023 | contracts carry no inertial permeability; exp(γ₂k^τ) silently fails off-SI |
| A8 | Spatial (per-depth-cell) porosity and bound/mobile fines inventory on BedState | fasano I/II, mo2023_2, waszkiewicz-coupled variants | scalar BedState.kappa cannot host dynamic bed mechanisms |
| A9 | Grinder dial-space adapter (per-grinder maps, no cross-porting) | wadsworth2026_grindmap ↔ cameron2020 ↔ schmieder2023 | dial maps are grinder/burr/calibration-specific (G5) |
| A10 | Observable-convention adapters (oven-dry EY, vial masses, fraction cup masses, per-solute yield) | liang2021, grudeva2023, schmieder2023 | see §5.10 |

---

## 2. REFERENCE CONFIGURATIONS

Standing regression scenarios. Each names one component per stage
(— = passthrough/none), its validation dataset(s), and the **validation
strength** of each gate per the §0 vocabulary.

### RC-1 `baseline-shot` (exists today; the regression floor)
| stage | component |
|---|---|
| grind | cameron2020 microstructure tables (EK43 dial) |
| packing | wadsworth2026.permeability prior → fitted κ (DE1 fixture A, κ=1.196 **[RS]**) |
| machine | recorded P(t) (DE1 fixture A; which pressure node this trace reports is open — §5.9) |
| infiltration | foster2025.infiltration, recorded-pressure form |
| flow | Darcy (+ Fo_F diagnostic once wadsworth2026_inertial lands) |
| extraction | cameron2020.extraction_bdf |
| bed_dynamics | — (constant κ) |
| observables | EY/TDS per ShotResultState |

Validation: Cameron SI Tables S1–S5 + Fig. 5 EY curve (independent/gated **[RS]**); DE1 fixture A
first-drip 7.0 s / W_dead 8.8 g triangle (independent, parameter-free **[RS]**);
egidi2024 Table 2 as an independent 12-condition **EY/TDS range bracket only —
not a pressure or temperature response test** (the egidi card: p and T never
enter the model; they are absorbed into measured q, τ, geometry).

### RC-2 `early-transient-shot` (early TDS / blonding physics) — **verification-gated**
| stage | component |
|---|---|
| grind / packing / machine | as RC-1 |
| infiltration | **front source:** foster2025.infiltration s_w(t) |
| extraction | **extraction source:** grudeva reduced model consuming t₀(z)=s_w⁻¹(z) (saturated-plateau + no-saturation branch) |
| observables | grudeva2023 vial-splitting kernel |

Validation: grudeva2023 13-shot per-vial dataset — **post-fit reconstruction**
(parameters fitted to the same dataset, per the card); grudeva2026 Fig. 4/5
ε-convergence (verification); DE1 fixture A first-drip cross-check via Grudeva
Eq. 6.14 (independent, weak). **Independent validation blocked** on the
forthcoming Grudeva experimental companion (both 2026 cards); RC-2 stays
verification-gated until then.

### RC-3 `compliant-bed-shot` (κ(t) physics + machine mode) — two variants
| stage | RC-3a `compliant-bed-empirical` | RC-3b `compliant-bed-coupled` |
|---|---|---|
| grind / packing | as RC-1 (Waszkiewicz rig PSD when using their data) | same |
| machine | foster2025_2 pump/headspace Eqs. 2–7 + waszkiewicz2025 brewer quadratic adapter | same |
| infiltration | foster2025.infiltration | same |
| flow | Darcy + Fo_F flag | same |
| extraction | cameron2020.extraction_bdf (observables only) | cameron2020.extraction_bdf **supplying m_d(t)** |
| bed_dynamics | waszkiewicz2025 κ(P, Φ(t)) with **its own empirical m_d(t) sigmoid** | waszkiewicz2025 κ(P, Φ(t)) with Φ(t)=m_d(t)/m₀ from Cameron |

RC-3a reproduces the published model; its gates inherit the paper's validation.
RC-3b is a **new coupled model not validated by the Waszkiewicz paper** — it
enters through the P2 harness (ladder rung 5), not by inheritance.
P2 challengers swap into the bed_dynamics slot of RC-3b via the harness.

**Pressure-node convention for RC-3** (implements ledger A1; do not apply two
pressure-drop corrections to the same segment):

| Symbol / trace | Physical node | Provider | Consumer |
|---|---|---|---|
| p_p(t) | pump outlet | foster2025_2 Eq. 2 (pump characteristic) | pipe resistance Eq. 3 |
| p_h(t) | headspace / bed top | foster2025_2 Eqs. 4–5 | infiltration (bed-top BC) |
| P_basket(t) | basket gauge / puck pressure | waszkiewicz2025 brewer-quadratic adapter, or measured trace | poroelastic κ model |
| ΔP_bed(t) | drop across wet bed | machine chain + bed geometry | Darcy / Forchheimer / infiltration |

Transition rule RC-1 → RC-3: RC-1 uses a recorded trace directly (node
identity per §5.9); RC-3 generates the node set from machine mode and must
reproduce the recorded trace at the corresponding node as a gate.

Validation: waszkiewicz2025 Zenodo set — 11-pressure equilibrium curve
(Q_c=1.90 g/s, P_c=12 bar; independent within-rig, rig-specific constants),
9-bar Q(t) Fig. 8A (independent-ish; soft circularity via m_d from same rig,
per the card), 5-s TDS fractions; foster2025_2 t_p=0.823 s / t_s=6.669 s /
Fig. 15 flow-minimum null (post-fit reconstruction: k, φ_T, t_shift fitted to
the same CT curves — the card's parameter-free DE1 triangle is the independent
gate); DE1 fixture A traces (independent).

### RC-4 `flavor-shot` (multi-solute chemistry) — **measured-flow first**
| stage | component |
|---|---|
| grind | pannusch2024 fitted ψ/d_s2 table (offline calibration adapter) |
| machine | **RC-4a:** measured Q(t)+T(t) trace (Schmieder/DE1). **RC-4b (later):** RC-3 machine mode output via ledger A2 |
| infiltration | — (assumed complete; preinfusion per pannusch2024) |
| extraction | pannusch2024 two-grain, 4 solutes (TDS/caffeine/trigonelline/CGA) |
| observables | per-solute traces (ledger A3); schmieder fraction kernel |

Validation: Schmieder/Pannusch public Mendeley kinetics
(DOI 10.17632/y2tz67f6ry.1) — reproduce fit MAPEs (TDS 6.07%, caffeine 4.59%,
trigonelline 7.85%, CGA 4.98%): **post-fit reconstruction**; the temperature
prediction set (avg MAPE 4.71% caffeine) is **independent**; quarantine the
flow-rate prediction regime (MAPE 18.23%) and the CGA roast-batch confound per
the card; schmieder2023 Table 2 cup masses within RSD (independent of the
kinetics fit, same apparatus).

---

## 3. DEVELOPMENT SEQUENCE

Ordering rule: value-per-effort with data first (value ceiling = validation
data **[RS]**), then dependency (what unblocks a reference configuration or a
harness).

### Phase 0 — Data intake (all effort S, no code dependencies; do immediately)

**Manifest rule:** every Phase 0 item lands with a machine-readable manifest
row: source card · source artifact (table/figure/repo) · extraction method
(transcription / digitization / repository pull) · units as published · units
in registry · uncertainty retained (y/n) · license/access · gate use ·
validation strength (§0 vocabulary). Mandatory for anything digitized and for
the known-hazard items (mo2023 k₁, wadsworth k_I SI-only, grudeva P_app typo).

| item | card | into data/ | unblocks |
|---|---|---|---|
| 0.1 | schmieder2023 | Tables A1, 2, 3 + S1 raw fractions (open CC-BY / Mendeley) | RC-4 gates |
| 0.2 | waszkiewicz2025 | Zenodo pulls: P/Q/mass traces ×11 pressures, TDS fractions, Fig. 6 curve, brewer quadratic, PSD | RC-3 gates; P2 harness |
| 0.3 | egidi2024 | Tables 1–3 (12-condition EY/TDS) | RC-1 bracket gate |
| 0.4 | mo2023 | Tables 1–5, Fig. 8a digitized, **k₁-units caveat column mandatory** | P6 calibration; §5.3 |
| 0.5 | romancorrochano2017 | Table 6.1 tamped κ; Tables 4.9/4.10 (Deff map, K(T)) | G9 test; 3.5 |
| 0.6 | wadsworth2026_grindmap | 22-sample PSD zip (open access); record the 8.1×10⁻¹⁷ m² erratum | pack_generator inputs; grind stage |
| 0.7 | grudeva2023/2026 | Table 3.1/3.2 + Table 1/2 param sets (flag P_app typo); check GitHub repo for vial raw data before digitizing Figs. 2.3–2.4 | RC-2 gates; 1.7a |
| 0.8 | bruno2026 | Table 2 four-origin roasted chemistry | A4 / G6 seed |
| 0.9 | liang2021 | Figs. 3–5 digitized; Table 1 protocol | extraction ceiling gate |
| 0.10 | moroney2016 | Table 1 parameter set | surrogate gate |
| 0.11 | foster2025_2 | Table I/II params; Figs. 6/8, 12–15 digitized | RC-3 machine-mode gates |
| 0.12 | fasano2000_partI | Figs. 8.1, 8.4 digitized (low fidelity, flagged qualitative) | P2 discrimination targets |

### Phase 1 — Implement-now components

Dependency note: 1.8a depends only on Phase 0 data; it does **not** wait for
1.6 (machine mode is needed for machine-driven Q(t), not for reproducing the
Pannusch/Schmieder gates).

| # | card | stage | effort | depends on | gate sketch | upgrades |
|---|---|---|---|---|---|---|
| 1.1 | wadsworth2026_inertial | flow | S | A7; 0.4 | reproduce their Fo_F band 0.0161–0.0639 from stated inputs; Darcy recovery as k_I→∞; shared-dimensional audit on DE1 fixture A (§5.2) | RC-1, RC-3 (Fo_F flag) |
| 1.2 | waszkiewicz2025 | bed_dynamics | S | 0.2 | refit (Q_c, P_c)=(1.90 g/s, 12 bar) on their 11-point curve; reproduce 9-bar Q(t) with zero extra parameters (RC-3a scope only) | RC-3a |
| 1.3 | liang2021 kernels | extraction C-gate + observables | S | 0.9 | refit K·E_max=0.215±0.002 from digitized Fig. 3; Eq. 23 E_oven curve with measured R_ret, R_vol; long-time cameron2020 EY limit check (~30% vs ~21%) | RC-1 sanity gate; A10 |
| 1.4 | moroney2016 surrogate | extraction C | S | 0.10 | reproduce Fig. 6 exit curve from Table 1; mutual-validation vs cameron2020 BDF at matched two-population limit | P1 harness anchor |
| 1.5 | wadsworth2026_grindmap | grind C | S | 0.6; A9 | refit β, R₀ from Table 1; S(G) monotonicity | grind priors for all RCs |
| 1.6 | foster2025_2 machine mode | machine | M | A1 (MachineState pump/headspace fields); 0.11 | reproduce t_p=0.823 s, t_s=6.669 s, Fig. 15 flow-minimum shape (post-fit reconstruction); re-run DE1 first-drip triangle (independent) | RC-3; supplies Q(t) to RC-4b |
| 1.7a | **Grudeva card-of-record reconciliation** | — (intake QA) | S | 0.7 | resolve against the CUP open-access source: (i) Eq. 74 bracket structure; (ii) thesis-vs-paper parameter-set identity (L* 12.43 vs 8.4 mm, c_sat 170 vs 224, D_s, k, q_app — same experiment refit, or different experiments?); (iii) are thesis vial data and paper verification runs separate configs; (iv) rule on whether φ_lb=0 verification parameters may inform any physical config; merge into one card of record | blocks 1.7b; resolves §5.1 |
| 1.7b | grudeva reduced model | infiltration+extraction | M | 1.7a; A5, A6, P_of_t→q adapter | (i) mass budget closed (verification); (ii) reproduce grudeva2026 Fig. 4/5 ε-convergence at Eq. 76–77 params, φ_lb=0 (verification); (iii) **post-fit reconstruction:** per-vial masses within 1 SD at thesis Table 3.1 parameters — independent validation blocked on companion dataset; (iv) first-drip consistency vs foster2025 on fixture A (independent, weak) | RC-2 (creates it, verification-gated) |
| 1.8a | pannusch2024 measured-flow solver | extraction | M | 0.1; A3, A6 | reproduce fit MAPEs against Mendeley kinetics (post-fit reconstruction) + temperature-set prediction MAPE (independent); schmieder Table 2 cup masses within RSD; quarantine flow-prediction regime and CGA confound per card | RC-4a (creates it) |
| 1.8b | pannusch2024 machine-driven adapter | extraction | S | 1.8a; 1.6 or measured DE1 Q(t) (A2) | compare production Q(t)-driven predictions vs RC-4a on matched shots | RC-4b |

Verdict-conflict handling for 1.7: grudeva2026 (implement-later, "hold until
experimental companion") vs grudeva2026_2 and grudeva2023 (implement-now).
Sequencing adopted: reconcile first (1.7a), then implement with verification
gates (grudeva2026_2's argument; precedent = lb_reference), mark RC-2
**verification-gated**, and hold `gated + data` status until the companion
dataset lands — which honors grudeva2026's reservation. Both positions
preserved in §5.1.

### Phase 2 — Comparison harnesses (the payoff of the parallel clusters)

| # | item | effort | depends on | design |
|---|---|---|---|---|
| 2.1 | Extraction harness (P1) | M | 1.4, 1.7b, 1.8a, Phase 0 gate data; A5 | run cameron2020 / grudeva / pannusch(TDS channel) on matched inputs against the Cameron Fig. 5 EY curve (SI Tables S1–S5 already in code), egidi2024 Table 2 bracket, Schmieder kinetics, Grudeva vials (post-fit — label as such in reports), Waszkiewicz TDS fractions; report per-dataset residuals with validation-strength tags; explicitly test waszkiewicz's "near-instant dissolution" claim vs Cameron's diffusion-limited boulders (§5.6) |
| 2.2 | κ(t) discrimination harness (P2) | M | 1.2, 1.6; 0.2, 0.12; A8 for challengers | implement the P2 null-first ladder; Waszkiewicz traces + DE1 fixture A; discriminating protocols per cards: flow-reversal replay (Fasano Fig. 8.4), pressure step, on/off rebrew; RC-3b (Cameron-coupled Waszkiewicz) enters here as rung 5, not by inheritance |
| 2.3 | Fine-grind-dip hypothesis file (P3) | S | 2.1, 2.2 partial | not a component: the P3 table maintained with current evidence per hypothesis |

### Phase 3 — Implement-later components (enter via harness, not standalone)

| # | card | stage | effort | trigger / dependency | gate sketch |
|---|---|---|---|---|---|
| 3.1 | mo2023_2 swelling | bed_dynamics | M | 2.2 designed; 0.4-adjacent Table 1 transcribed; A8 | k₀ Table 2 closed-form (verification); Fig. 3(a) flow-decay ratios (verification); Fig. 8 yield/strength within replicate bars for M_c<30 g (post-fit); fixed-q insensitivity |
| 3.2 | fasano2000_partII lifted κ(t) closure | bed_dynamics | S–M | 2.2; DE1 flow traces staged | fit compaction/swelling constants to rising-flow residual; discriminate vs partI via pressure-step |
| 3.3 | fasano2000_partI fines migration | bed_dynamics | M | 2.2; β(q), γ, M, K(b,m) closure fitting; A8 | reproduce Fig. 8.6 nonmonotone q∞(p₀) (verification); fit exponential flow decay with physical params; exact mass budget |
| 3.4 | lee2023 N-tube graft | bed_dynamics | S (2-tube repro) / M (streamtube graft) | streamtube; 2.3 | reproduce Fig. 4 fit AND the documented negative result (plateau at physical ρ_c) |
| 3.5 | romancorrochano2017_extraction | extraction | M | 0.5; A3/A6 from 1.8a | stirred-vessel MPE 5–8% with 4-MW Deff (post-fit); parameter-free bed gate MPE ≤14% (independent); y₀ vs Cameron ceiling cross-check (§5.5) |

Skips stand as recorded: fasano2000_partIII (forced monolith), ellero2019
(intake the J. Food Eng. 263 journal version instead), hendon2020 (editorial).

---

## 4. GAPS

**G1 — Unsaturated flow at fine grinds.** Named by foster2025_2 as the competing
fine-grind-dip mechanism ("tubes at k→0, an atom the lognormal lacks") and by
the backlog **[RS]**, but *no card models it* — Foster's own model is
sharp-front binary saturation and declines the coarse-grind case; Grudeva's
"unsaturated" variant is solute-side only (her cards warn against conflating
the terms). Matters: the only P3 hypothesis without even a skeleton. Targets:
Richards-equation / continuous-saturation imbibition in coffee or fine powders;
two-phase LB in granular beds; the Foster/Vynnycky/Moroney group (Phys. Fluids,
IMA J. Appl. Math.) — foster2025_2 itself says a continuous-saturation model is
"needed" if p_c is large.
  - **PRIMARY SEARCH TARGET — measured retention/relative-permeability curves**
    (carded for the intake project: `docs/cards/g1_retention_search_target.md`).
    G1 is blocked on CONSTITUTIVE DATA, not solver choice, so the specific thing
    to look for is a source that MEASURES the partial-saturation curves, not just
    a wetting-front position: the water-retention curve θ(ψ) (moisture content vs
    capillary suction / matric potential) and the relative permeability K_r(θ) or
    K_r(ψ) for a coffee bed — ideally TAMPED, espresso-relevant, with saturation
    resolution (a full imbibition/drainage curve), not a single √t front trace.
    Van-Genuchten/Brooks–Corey fit parameters (α, n, θ_r, θ_s) would be directly
    ingestible. What does NOT satisfy this (already checked, all sharp-front or
    geometry only): foster2025.infiltration (sharp front), egidi2018 (soil solver,
    no coffee curves), mckeonaloe2021 (n=1 pixel-unit √t, silent on saturation
    behind the front). Method sources to scan: soil-physics porosimetry / tensiometry
    adapted to coffee; NMR/MRI moisture profiling of a wetting puck; X-ray µCT with
    saturation (not just front) segmentation; centrifuge/pressure-plate retention on
    ground coffee. Any such measurement UNBLOCKS the Richards G1 model.
  - **Refinement (egidi2018, card-only, SKIP as runtime):** egidi2018 supplies a
    Richards **solver** (van Genuchten–Mualem, fixed-point FD) but for *soil*, no
    coffee content — the gap is **constitutive, not numerical**. The blocker is
    that coffee θ(ψ)/K(ψ) (wettability/retention) curves are **unmeasured**, so
    the literature target here is *measurements*, not another Richards code. Until
    such data lands, the interim path is the **hypothesis-#2 wetting-atom probe**
    (`validation/slow/hyp2_wetting_atom.py`, commit a4a17a9): a k→0 dry-tube atom
    over streamtube+foster whose discriminating observable is a grind-dependent
    first-drip delay — qualitative, non-component, no retention curve invented.

**G2 — Mass-conserving 5-state mobile-fines transport.** fasano2000_partI is a
3-state skeleton with every parameter unidentified; ellero2019 was skipped.
Targets: Ellero & Navarini, J. Food Eng. 263, 181–194 (2019) (named intake
candidate); Mo et al. Phys. Fluids 33 (2021) erosion and Mo et al. 2022
swelling (named on mo2023); ASIC 1993/1997 Petracco/Bandini transient-discharge
proceedings (named on ellero2019 as the missing validation data).

**G3 — Machine mode with a *measured* pump characteristic.** foster2025_2's
quadratic is nominal (manufacturer spec); waszkiewicz2025 supplies only one
rig's pressure-drop quadratic. Matters: RC-3's machine stage rests on a nominal
closure. Targets: DE1 pump/flow bench characterizations (Decent community
documentation); espresso-machine hydraulics papers.

**G4 — Temperature.** *Extraction-chemistry part now PARTIALLY resolved*
(`harness.g4_temperature_sensitivity`, `gate_g4_temperature_sensitivity`,
2026-07-11). Two INDEPENDENT partition closures — romancorrochano Arrhenius K(T)
and pannusch van 't Hoff K(T) — both move K by <15 % over 80→98 °C, the
propagated extraction-extent shift is ~1.8 pp, and schmieder2023's measured cup
concentration spans a median 3.4 % across its 80/89/98 °C axis at the DoE-center
grind+flow (the matching negative datum): the extraction-chemistry T-effect is
**small and empirically confirmed**. Caveat surfaced, not merged (rule 6): the
two K(T) closures **disagree on the SIGN of dK/dT** (roman +9.4 %, pannusch
−5 %) — a partition-convention difference reported side by side. **REMAINDER
still open:** nothing models in-puck thermal transients or the T-dependence of
wetting/swelling (foster2025_2 flags the latter as open) — the part of G4 that a
small equilibrium K(T)/D(T) sensitivity does NOT settle. Targets: heat-transfer
puck models; TU Munich (Briesen/Minceva) follow-ups.

**G5 — Grinder transfer-function abstraction.** Three incommensurate dial
spaces on file (EK43/cameron2020, Mahlkönig-large/wadsworth2026_grindmap,
E65S/schmieder2023) with no cross-map. **Warning: dial maps are not merely
unaligned — they are not physically portable even within a nominal grinder
family without recalibration**; the grindmap card states the map depends on
"calibration, burr set and manufacturer" and forbids porting to Cameron's EK43
dial range without refitting (ledger A9). Targets: population-balance
burr-grinding models; Uman et al., Sci. Rep. 6, 24483 (grinder PSD source named
on hendon2020/cameron2020); PSD models beyond bimodal **[RS]**.

**G6 — Multi-class inventory ↔ kinetics link.** pannusch2024 gives per-solute
kinetics; bruno2026 gives per-origin roasted inventories; nothing links them
(bruno2026's card: no solubility/diffusivity/partitioning). Explicit data flow:
**Bruno Table 2 → SoluteInventory prior (ledger A4) → pannusch2024 /
romancorrochano2017 kinetics** — never `Bruno ODE model → extraction`; the
roasting model itself stays out of the chain per its card. Targets: per-species
solubility/partition measurements (JAFC-type analytical coffee chemistry);
Giacomini 2022 J. Math. Chem. multi-species extension (named on egidi2024).

**G7 — CO₂ degassing / gas-phase effects.** romancorrochano2017_permeability
names CO₂ expulsion as a driver of the early-shot transient; mo2023's SEM shows
entrapped gas; no card models it. Matters: confound inside every P2
discrimination experiment. Targets: degassing kinetics of fresh grounds;
crema-formation literature.

**G8 — Water chemistry.** hendon2020 is a skip; the pointer stands (Hendon et
al., JAFC 62, 4947–4950, 2014) if ever prioritized. Not on the current backlog.

**G9 — Basket / screen / outlet hydraulic resistance (promoted from P4 note).**
The packing stage currently treats puck permeability as the dominant
resistance, but three cards independently implicate outlet/sieve/screen
effects in the tamped regime: Wadsworth's reconciliation with Cameron flux
requires φ_c ≈ 0.11 **or screen resistance** (wadsworth2026 **[RS]**);
Grudeva's fitted κ = 2.2×10⁻¹⁶ m² sits ~10× below her own K–C bounds,
attributed to sieve resistance (grudeva2023); romancorrochano2017_permeability
Table 6.1 supplies the real tamped/consolidated κ to test against. Action: add
an explicit series-resistance model, initially R_total = R_puck + R_screen +
R_fixture, gated against Table 6.1, Grudeva's fitted κ, the Wadsworth tamped
extrapolation, and DE1 fixture A. Targets: filter/screen hydraulics; basket
manufacturer flow data.
Input revised (1.7a): adjudicated Grudeva κ = 2.2e-15 m² sits inside her
Kozeny-Carman band; the 10x sieve-resistance gap narrative weakens by one order.

**G10 — Concentration-dependent liquid properties / coffee-liquor rheology.**
Every flow-coupled model on file uses pure-water μ, ρ (foster2025_2,
waszkiewicz2025, grudeva, moroney2016, cameron lineage), yet grudeva2026
explicitly flags that viscosity rises with concentration and the early-shot
liquid sits near saturation — exactly where her plateau prediction lives.
Matters: a shared systematic bias across RC-2 and RC-3 early-shot gates.
Targets: coffee-extract viscosity/density vs TDS and temperature measurements;
food-process rheology literature.

**G-lat — Lateral tube coupling / pressure equalization for evolving-κ
channeling.** Surfaced by the N-tube κ(t) union (`harness.ntube_kappa_t_union`,
`gate_ntube_kappa_t_union`; ANALYSIS_P2 §2.4). The static streamtube ensemble
assumes parallel, non-exchanging tubes — admissible when κ is fixed. But once
each tube carries an extraction-driven porosity clock, the near-choke poroelastic
hypersensitivity (the closure P2 proved required) makes flow-controlled channeling
**strongly concentrate in the tested configuration**: flow collapses to a single
effective channel (N_eff→1, max share→1) and EY drops. A homogenizing regularizer
(a PROXY for lateral coupling, not a transverse-Darcy term) suppresses it. This is
an EXPLORATORY finding in one config (gs 1.1, 9 bar, N=200) — NOT a proven
unconditional instability (no parameter sweep, no stability theorem). Whether
lateral coupling is the physical cure is exactly what G-lat must establish.
Matters: it bounds when a per-tube dynamic upgrade of the streamtube is even
well-posed. Targets: a 1-D transverse-Darcy (or reduced network) closure that
lets adjacent tubes exchange flow under a shared local pressure field; the
critical lateral conductance vs the axial near-choke sensitivity sets the
stability boundary. Interim: use the static streamtube for the time-averaged dip
(P3 verdict) and treat the dynamic union as diagnostic only.

---

## 5. OPEN QUESTIONS

**5.1 Grudeva duplicate cards + verdict conflict.** grudeva2026.md
(implement-later) vs grudeva2026_2.md (implement-now), same paper, with
differing transcriptions: Eq. 74 bracket structure differs between cards;
Table 2 dimensionless sets disagree (e.g., Q_f 0.104 vs the thesis's 3.12);
thesis and paper dimensional sets differ materially (L* 12.43 vs 8.4 mm, c_sat
170 vs 224 kg m⁻³, D_s 2.3×10⁻¹⁰ vs 1×10⁻⁹, k 10⁻⁴ vs 10⁻³, q_app). Resolution
path = item 1.7a (card-of-record reconciliation, gating 1.7b). Sequencing
compromise recorded in §3.
**RESOLVED 1.7a** — see `docs/cards/grudeva2025.md` RECONCILIATION LOG;
adjudicated no-ε form; two named parameter configs; emergent finding: κ and
P_app carry decade typos in both sources, adjudicated κ ≈ 2.2e-15 m². (§7.2.)

**5.2 Forchheimer regime disagreement (three-way) → shared-dimensional audit.**
Backlog **[RS]**: Fo_F ≈ 0.3–0.9 at Cameron bed density. wadsworth2026_inertial:
Fo_F 0.0161–0.0639 ("laminar, close to onset"; model-chained estimate, not a
measurement). mo2023: Re 0.84–3.86 at espresso gradients with inertial losses
significant. Adjudication rule (gate 3 of item 1.1): **compute Re and Fo_F from
the same q, k, k_I, μ, ρ, bed depth, and characteristic grain/pore length under
one stated convention (Darcy vs interstitial velocity declared); do not compare
Mo's Re and Wadsworth's Fo_F as interchangeable diagnostics.** Output: one
table of {q, ∇p, k, k_I, Re, Fo_F, length scale} along the DE1 fixture A traces
with fitted κ=1.196.

**5.3 mo2023 k₁ units.** Internal inconsistency ~10⁴ between Fig. 8(b)
annotation and Tables 2–5 headers. Resolve against the standard Forchheimer
β=ρ/k₁ form; author correspondence bundled with the microCT-volume request
(§5.8). Manifest caveat column mandatory until resolved (Phase 0.4).

**5.4 c_sat disagreement.** 212.4 kg m⁻³ (cameron2020, lee2023, moroney2016,
egidi2024 — shared provenance) vs 224 (grudeva2026) vs 170 (grudeva2023).
Config field per P1 hazards table; surface in harness reports; no silent merge.
Partially subsumed by 1.7a(ii).

**5.5 Extraction ceiling disagreement.** Cameron per-bed inventory ceiling
29.6% vs liang2021 immersion equilibrium K·E_max ≈ 21.5–24% vs lee2023 fitted
EY_max=33.8% (its own card: "perhaps a little high") vs romancorrochano y₀
31.7–32.15 falling with coarseness (entrapment). At least two distinct physical
quantities are conflated (soluble inventory vs equilibrium partition endpoint);
the liang-vs-cameron long-time gate (1.3) is the designed probe.

**5.6 Dissolution-speed tension.** waszkiewicz2025: solubles dissolve "almost
instantaneously," TDS timescale set by flow; cameron2020: diffusion-limited
boulder population. Waszkiewicz 5-s TDS fractions are the discriminating
dataset (harness 2.1).

**5.7 Known typos/errata to carry (into manifests).** Grudeva P_app printed
9.2×10⁻⁶ Pa (both cards: evident typo for ~9.2×10⁵ Pa);
wadsworth2026_grindmap §6 swelling example 8.1×10¹⁷ m² (typo for 10⁻¹⁷);
mo2023_2 Figs. 7–9 caption "hindrance factor" mislabels the partition
coefficient, and L_z=12.6 mm vs stated 14.6 mm capsule height unexplained;
egidi2024 Eq. 4's φ_s undefined and ρ never stated; fasano2000_partI Eq. 8.43
sign appears OCR-flipped; lee2023 uses ρ_c=798 kg m⁻³ (2× measured 399), and
its card records the physical-ρ_c negative result as a required gate.

**5.8 Author data / correspondence tracker.**

| owner (target) | request | date sent | status | blocks | fallback |
|---|---|---|---|---|---|
| Wadsworth group | segmented XCT volumes | sent (pre-roadmap **[RS]**) | awaiting reply | pack_generator validation | published PSD zip only |
| Mo / Ellero group | microCT volumes; SPH parameters; **k₁ units clarification** | not sent | draft with §5.3 | 0.4 quantitative use; G2 | use kᴰ only, caveat k₁ |
| Foster group | raw CT time series | not sent | — | none critical (figures digitizable) | digitize Figs. 6/8 |
| Grudeva | vial raw data; forthcoming experimental companion | not sent | check GitHub repo first | RC-2 `gated + data` upgrade | digitize Figs. 2.3–2.4 (post-fit only) |
| Grudeva/Moroney/Foster (EJAM authors) | 1.7a Q(a) ε erratum in Eqs 52/58/67/72/74; (b) κ/P_app decade slip (adjudicated κ≈2.2e-15); (c) S2 Table 1 fit dataset + consistent (q_app,L,t_w) triple; (d) is the GitHub solver the Figs 3–5 code | not sent | **G0 done (Sprint 5): repo diff confirms no-ε capacitance; Q(a)/(b)/(d) internally resolved — only Q(c) fit-dataset still open** | 1.7b `gated + data` (companion dataset) | G0 confirmed code = no-ε form |
| Schmieder/Pannusch | raw/segmented data beyond supplementary | not sent | — | none (Mendeley public) | Mendeley set |
| Egidi group | ρ and φ_s definitions in Eq. 4 | not sent | — | quantitative EY-gate use of Eq. 4 | infer from ref [10], flag |
| Fasano-era illy / ASIC | Eq. 8.2 a,b,c; 1993/1997 transient-discharge data | not sent | long shot | G2 validation target | digitized Figs. 8.1/8.4 (qualitative) |
| Decent Espresso | DE1 pump characteristic Q(P) / firmware model coefficients (country-calibrated, closed ESP32) | not sent | — | G3 independent DE1 curve (reference envelope on disk) | TB bench pull of the DE1 pump curve |
| Telis-Romero et al. | 2000/2001 numeric μ(T,Xw)/ρ(T,Xs) fit-coefficient tables (paywalled Wiley/Tandfonline) | not sent | institutional-access drop | G10 quantitative per-cell μ(T,c) (reference envelope on disk) | reference envelope from abstracts + open 2013 xref |
| Ellero & Navarini (illy) | raw direct/inverse transient-discharge point series behind the 2019 JFE overlay + ASIC 1993/1997 scans | draft in `docs/sourcing/` (not sent) | source located (open PDF), raw data figure-embedded | G2 validation (defined acquisition task now) | digitize the 2019 overlay, labelled `figure_digitized` (never raw) |
| Khomyakov et al. | clarify the density-equation temperature-coefficient sign (`+0.8·T` contradicts the paper's own prose) + the dynamic-viscosity power-law convention | draft in `docs/sourcing/` (not sent) | measured kinematic table on disk; both regressions quarantined | G10 usable density/dynamic-μ closure | keep the measured kinematic table only; use Telis-Romero for density |

**5.9 Pressure-node convention (NEW).** Which node does each dataset report:
pump outlet, headspace, basket gauge, bed inlet, or bed drop? Must be resolved
per dataset before RC-3 gates run — in particular, which node the DE1 fixture A
P(t) trace and the Waszkiewicz "basket pressure" correspond to, and which node
Cameron's "bar gauge overpressure" (MachineState **[RS]**) means. Record the
answer in each data manifest; RC-3's node table (ledger A1) is the target
schema.

**5.10 Observable convention (NEW).** EY, TDS, oven-dry EY, per-vial solubles
mass, fraction cup mass, and per-solute yield are not interchangeable. Kernel
assignments: liang2021 oven-dry/retention kernel for practitioner EY
comparisons; grudeva2023 vial kernel for RC-2 gates; schmieder2023 fraction
kernel for RC-4 gates. Every gate in §2/§3 must name its observable kernel
(ledger A10); harness reports must not mix kernels in one residual column.

---

## 6. VALIDATION DATA PLAN

Held now **[RS]**: Cameron microstructure/flux tables;
wadsworth2026_table1.csv; DE1 fixture A (P(t), W(t), flow, κ=1.196).

| dataset | card | access | serves | validation strength (§0) | priority |
|---|---|---|---|---|---|
| Waszkiewicz full rig set (traces ×11 P, TDS fractions, calib curve, PSD, code) | waszkiewicz2025 | **public** (Zenodo/GitHub) | RC-3, P2, 2.1 | independent within-rig; rig/coffee/grind-specific constants; m_d(t) soft circularity | **1** — only public multi-pressure trace set on file |
| Schmieder/Pannusch multi-solute kinetics | schmieder2023 / pannusch2024 | **public** (Mendeley + CC-BY suppl.) | RC-4, G6 | fit set = post-fit; temperature set = independent; flow set = quarantined | **1** |
| Wadsworth PSD zip (22 samples) | wadsworth2026_grindmap | **public** | grind priors, pack_generator | independent measurement | **1** |
| Cameron SI Tables S1–S5; Fig. 5 EY curve | cameron2020 | held **[RS]** (S1–S5 transcribed in code) | RC-1 | existing gated regression | held |
| egidi2024 Table 2 (12-condition EY/TDS) | egidi2024 | transcribe from PDF | RC-1 | independent EY/TDS **bracket**; not a pressure/T response test | **2** |
| Grudeva 13-shot vial TDS + flow | grudeva2023 | repo-check, else digitize/request | RC-2 | **post-fit reconstruction** unless companion provides holdout | **2** — RC-2 has no other experimental gate |
| romancorrochano Table 6.1 (tamped κ) + Table 4.9 (Deff map) | romancorrochano2017_* | transcribe | G9 test, 3.5 | tamped permeability *data*; not a K–C validation | **2** |
| foster2025_2 Table I/II + Figs. 6/8/15 | foster2025_2 | transcribe/digitize | RC-3 machine gates | CT fit = post-fit; DE1 first-drip triangle = independent | **2** |
| mo2023 Tables 1–5 + Fig. 8a | mo2023 | transcribe (k₁ caveat) | P6, 1.1 | simulation-derived; literature-anchored; ε circular to cameron | **2** |
| angeloni2023 Tables 1–7 (66-shot chemistry + inventories) **(intake DONE; brackets wired)** | angeloni2023 | transcribed from article tables (Tim xlsx drop; no repo) | **INDEPENDENT multi-species validation** for **pannusch2024** (was post-fit only) + cameron TDS | independent (different machine/coffee/basket) | **done** — pannusch brackets all 4 species (CF/TR/5CQA/TDS) in the angeloni envelope; cameron TDS reads low (2nd dataset after egidi). Multi-solute kinetics transfer, lumped does not |
| bruno2026 Table 2 chemistry | bruno2026 | transcribe | G6/A4 seed | independent measured chemistry (reference set) | 3 |
| liang2021 Figs. 3–5 | liang2021 | digitize | 1.3 gate | fit = post-fit; flat-E and E_oven structure = independent | 3 |
| moroney2016 Table 1 (+ Moroney 2015 primary data) | moroney2016 | transcribe; consider Moroney 2015 intake | 1.4; P1 | graphical, partly post-fit | 3 |
| fasano Figs. 8.1/8.4 | fasano2000_partI | digitize (low fidelity) | P2 discrimination | qualitative | 3 |
| ASIC 1993/1997 transient-discharge data | ellero2019 (pointer) | hard to obtain | G2 validation | unknown until sourced | 3 (acquisition project) |

Coverage per reference configuration: RC-1 fully served by held data + 0.3.
RC-3a fully served once 0.2 and 0.11 land; RC-3b requires the 2.2 harness.
RC-4a fully served by 0.1 (public). **RC-2 is the exposed one**: its only
experimental gate is post-fit vial data plus the promised companion — hence
verification-gated status until then. Per the house rule (data = value ceiling
**[RS]**), Phase 0 items 0.1–0.2 outrank any Phase 1 code.

---

## 7. MAINTENANCE

Living document. Update rule: revise this file (i) whenever a component lands
or changes gate status, (ii) whenever a card batch is intaken, (iii) whenever a
§5 open question is resolved (record the resolution, keep the entry per §7.2).
After any material change, regenerate the project-knowledge copy so intake
conversations run against the current plan. Verdict lines in the cards remain
the source of truth for §3; this roadmap orders them, it does not override
them. **Status promotions (`verification-gated` → `gated`, `gated` →
`gated + data`) require a §7.1 entry citing the dataset and the gate script.**

### 7.1 Change log
| date | change | evidence (dataset + gate script) | affected RCs / items |
|---|---|---|---|
| 2026-07-12 | **blocked-intake sourcing bundle processed** (`puckworks_blocked_intake_sourcing/` → tree; two commits). **0.8 bruno2026 CLOSED:** Table 2 (Sci. Rep. 16, 15857, CC BY 4.0; 4 origins × 10 compounds, mean±SD, n=3) → `data/bruno2026/` + loaders + MANIFEST + smoke test; data-only inventory prior for G6/A4 (never Bruno-ODE→extraction) — **the last outstanding transcription item**. **G10 second measured source:** khomyakov2020 MEASURED kinematic viscosity grid (15–70 wt% × 20–80 °C, CC BY 3.0) → `data/g10_liquor_rheology/khomyakov2020_kinematic_viscosity.csv` + loader + smoke test (ν monotone ↓T, ↑solids) + card `khomyakov2020.md`; its density (`+0.8·T` sign conflict vs prose) and dynamic-viscosity power-law (literal eval 5.8–1194× off Table 1) regressions **QUARANTINED** (`*_FLAGGED/_QUARANTINED.csv`, NOT loaded). G10 stays 🟡 — khomyakov's 15 wt% floor is above espresso TDS so espresso stays an extrapolation. **G2 no longer a blind search:** ellero2019 primary source located (open PDF; forcing schedule + τ_v=0.16 s + plotted overlay, raw points figure-embedded) → defined acquisition/digitization task. **Acquisition instruments preserved** under `docs/sourcing/` (G1 experiment protocol + schema + email; G3 bench protocol + schema + Decent request; G2 digitization template + notes; G10 author-clarification; Wadsworth PSD follow-up; Tier-3 leads; sourcing report + manifest). BLOCKED_INTAKE reconciled; §5.8 +2 (Ellero/Navarini, Khomyakov). No component promotion; measured tables reference/qualitative for espresso. | `data/bruno2026/`, `data/g10_liquor_rheology/khomyakov2020_kinematic_viscosity.csv`; MANIFEST rows `bruno2026/roasted_composition`, `g10_liquor_rheology/khomyakov_kinematic_viscosity`; `docs/cards/khomyakov2020.md`; `docs/sourcing/` | 0.8 CLOSED; G10 second source (still 🟡); G2 acquisition-defined; instruments staged |
| 2026-07-12 | **Result-3 (N-tube) DEEPENED: linear stability + flow/pressure regime + phase diagram** (review's Result-3 work list; `harness.ntube_stability_analysis` + `ntube_kappa_t_union(control=...)` + `validation/slow/ntube_stability.py`, ~60 s, NOT CI). (1) **Closed-form linear stability:** a perturbation's amplification is the end-to-start conductance ratio **A = (M(φ_max)/M(φ_0))^(1−lateral)** → poroelastic A≈10¹² (UNSTABLE, M→0 at the near-choke shutoff), Kozeny-Carman A≈1.5 (STABLE); numerics confirm (N_eff→1.0 vs 83). The single-channel latch IS the analytical instability, not an artifact. (2) **Control regime:** added a `control="flow"|"pressure"` mode; the latch is FLOW-control-specific (fixed total → stealing → N_eff→1); under PRESSURE control (independent tubes) there is NO latch (N_eff≈84, max single-tube 0.04) — a pump/flow-controlled (schmieder/DE1) phenomenon. (3) **Phase diagram** (grind × lateral × control): the ONLY latching region is flow-control with zero lateral coupling (closure-driven, grind-independent); any lateral ≥0.3 OR pressure control keeps N_eff ≫ 1. Gap **G-lat** now has an analytical criterion + phase map; a *physical* transverse-Darcy exchange closure is still card-blocked (the lateral term is a homogenizing proxy). ANALYSIS_P2 §2.4 + PAPER_OUTLINE Result 3. Exploratory/qualitative; no promotion. | `validation/slow/ntube_stability.py` (slow) | G-lat: stability criterion + phase map; Result-3 deepened |
| 2026-07-12 | **G10 directional μ-bias consistency check** (the g10 card's suggested gate; `harness.g10_mu_bias_direction` + `gate_g10_mu_bias_directional`, on the g10 component). Darcy Q~1/μ with the reference espresso μ (1.27–1.90× water): swapping it in SUPPRESSES the high-concentration EARLY-shot flow to ~0.53–0.79× the pure-water prediction while leaving the dilute LATE/equilibrium flow UNCHANGED (×1.0) — the two properties the card asks for (reduce the RC-2/RC-3 early-shot bias without breaking equilibrium), IF that bias is early-flow over-prediction (grudeva-flagged). Consistency check, reference/qualitative — NOT a validation (no espresso-TDS flow measured); bounded ~1.3–2×, confirm the real bias is not larger before attributing all of it to viscosity. G10 card updated (gate IMPLEMENTED); g10 component now carries 2 gates. | `gate_g10_mu_bias_directional` | G10 directional check (reference); RC-2/RC-3 early-shot-bias mechanism instrumented |
| 2026-07-12 | **P3 Result-1 magnitude comparison** (`harness.result1_magnitude_comparison`, reported in `validation/slow/channeling_sensitivity.py`). Compares the channeling interior-max bump against the schmieder bump, both in EY-points, on the MEASURED cells. Raw TDS-EY interior bump = **−0.24 EY-pt (monotone; no bump in the data)**, replicate noise floor 0.22 EY-pt; the model channeling bump (0.19 EY-pt at 5 bar, 0.03 at 9 bar) sits **BELOW the noise floor**. **New data-quality finding:** schmieder's fitted RSM OVERPREDICTS absolute cup mass ~1.73× (6.7 vs measured 3.9 g; its β₆·temp² term alone exceeds the whole cup mass) → the RSM is a SHAPE tool (vertex/concavity), NOT absolute-magnitude (matches the schmieder card's own "RSM order-of-magnitude only" caveat), so magnitudes are compared on the raw cells, never the RSM absolute. Conclusion: neither side has a strong peak to match or miss → model-capacity, not identification; title/abstract cannot rest on a channeling peak. Result-1 reanalysis COMPLETE (TDS-EY + sensitivity + magnitude). ANALYSIS_P2 §2.3 + PAPER_OUTLINE Result 1. No promotion. | `validation/slow/channeling_sensitivity.py` (slow) | 2.3 Result-1 magnitude done; reanalysis complete |
| 2026-07-12 | **P3 Result-1 closure-sensitivity sweep** (review's robustness ask; `harness.channeling_interior_max_sensitivity` + `validation/slow/channeling_sensitivity.py`, ~90 s, NOT CI per rule 3). Tests whether the channeling interior grind maximum is robust to the empirical σ(φ₁) closure. Result: it is **real and n_grid-CONVERGED** at the calibrated closure (peak gs≈1.4, prominence 0.19 EY-pt — not a resolution artifact) but **FRAGILE** (interior max in only 10/25 = 40 % of the s_ref × m grid; vanishes for weak channeling / low s_ref) and **WEAK** (median prominence ~0.14 EY-pt; ~0.03 EY-pt — near-flat — at 9 bar, with the peak grind drifting gs 2.0→1.2 across pressure). The model-side fragility mirrors the schmieder target side (weak RSM adj-R² 0.41–0.75 / monotone raw cells) → both support MODEL-CAPACITY, not identification, and the manuscript title/abstract must not rest on a channeling peak. ANALYSIS_P2 §2.3 + PAPER_OUTLINE Result 1 (sensitivity ✅). No status promotion. | `validation/slow/channeling_sensitivity.py` (slow) | 2.3 Result-1 sensitivity done (fragile/weak/converged) |
| 2026-07-12 | **G1/G3/G10 sourcing pass — three Tier-1 needs moved (CHAT→data), all REFERENCE-strength, NONE closes its gap at independent** (calibration components + consistency-check gates; not validations). **G1:** glass-bead retention/K_r analog compiled from arXiv:2501.13361 App. B (cubic K_r, S_r=0.07, linearized-VG slope, Kozeny-Carman K0) → gives egidi2018 Richards machinery a runnable closure so P3 hyp#2 (incomplete wetting) is no longer blocked on MECHANICS. **Confirmed the gap is real:** Foster/Vynnycky/Moroney 2025 (Phys.Fluids 37,013383) is SHARP-FRONT — the search-target's own negative filter — so no coffee theta(psi) exists; `g1_retention_search_target.md` STAYS OPEN. **G3:** Ulka vibe-pump envelope (Q_free~10.8 mL/s, P_deadhead 15 bar, +/-15%) + the load-bearing fact that the P-Q curve is a CONCAVE DROOP not a quadratic; true DE1 model is CLOSED ESP32 firmware (Decent-confirmed, country-calibrated, unpublished) — independent DE1 curve needs a TB bench pull or Decent request; does NOT replace `waszkiewicz2025/brewer_quadratic`. **G10:** Telis-Romero (2000/2001) coffee-extract mu(T,c)/rho(T,c) — espresso TDS (4-12% solids) sits BELOW their dilute end (90% water), so espresso mu is an EXTRAPOLATION toward pure water (~1.3-2x); espresso IS Newtonian (validates single-mu assumption; power-law only >36% solids); primary tables paywalled → quantitative per-cell mu(T,c) is a Tim drop. **All three tagged reference/qualitative (no upgrade without a coffee/DE1/espresso-TDS measurement + a §7.1 entry).** | `gate_g1_glassbead_closure_sane`, `gate_g3_pump_envelope_bounds_quadratic`, `gate_g10_reference_mu_above_water`; MANIFEST rows g1_glassbead_analog/retention_kr, g3_pump_characteristic/ulka_envelope, g10_liquor_rheology/telis_romero_envelope | G1 machinery unblocked (validation OPEN); G3→partial; G10→partial; RC-2/RC-3 early-shot-bias check seeded |
| 2026-07-12 | **BLOCKED_INTAKE reclass + §5.8 additions** (housekeeping, follows the sourcing pass above). G3 and G10 reclassified 🔴→🟡 (reference envelope on disk; independent upgrade owed): G3 needs an independent DE1 P-Q curve (TB bench or Decent); G10 needs the Telis-Romero numeric fit tables (Tim institutional access) for quantitative use + a true espresso-TDS measurement for independent strength. G1 stays 🔴 with a sub-line noting the analog is on disk and the coffee search target is still open. Two §5.8 correspondence lines added: (a) Decent — DE1 pump characteristic / firmware coefficients; (b) Telis-Romero 2000/2001 tables as an institutional-access drop. Still-owed after this pass: G1 coffee retention curve (hardest, may not exist), G2 transient-discharge (ASIC/ellero2019 acquisition), bruno2026 Table 2 (transcription pending host). | `puckworks/data/BLOCKED_INTAKE.md`, ROADMAP §5.8 | ledger reclass G3/G10→🟡; §5.8 x2 |
| 2026-07-12 | **P3 primary target set to TDS-derived EY** (review follow-up). Added `harness.schmieder_tds_ey` (EY = TDS cup mass / 20 g nominal dose · 100 — the yield quantity a model outputs, from schmieder card's fixed 20 g dose) and made it the PRIMARY observable in `schmieder_interior_max_target` (mg solutes now secondary cross-checks). Result: on TDS-EY at the fixed central condition the RSM has an interior vertex at dial 1.75 (adj-R² 0.64) but the raw EY grind response is **monotone increasing (18.3 → 19.4 → 19.6 %)** — the interior max is a weak-model feature, not a raw signal, consistent with the model-capacity verdict. Gate + P3_hypotheses VERDICT table + ANALYSIS_P2 §2.3 lead with TDS-EY. | `gate_p3_schmieder_peak_discrimination` | 2.3 P3 primary target = TDS-EY |
| 2026-07-12 | **N-tube union claims NARROWED + a pressure bug fixed** (same review). (i) `ntube_kappa_t_union` computed the flow dynamics at `P_bar=9` but the ensemble EY at a hardcoded `p_bar=5` — fixed to use P_bar for both (EY now 15.1%→2.4% @9 bar, was the inconsistent 16→2.5). (ii) Added proper concentration metrics — MAX single-tube share and effective channel count N_eff=1/Σsᵢ² — so "single channel" is measured (max→1.0, N_eff→1.0), not inferred from a top-decile. (iii) "unconditionally unstable" → "strong concentration in the TESTED near-choke config" everywhere (one grind/pressure/closure-slope/clock; no sweep, no stability theorem). (iv) the `lateral` term relabelled a HOMOGENIZING REGULARIZER (proxy), not "lateral pressure equalization" (it is not a transverse-Darcy exchange). Gate rewritten to assert the measured collapse + CK-bounded (N_eff~110) + substep-invariance + regularizer-suppresses. ANALYSIS_P2 §2.4 + G-lat gap note narrowed. | `gate_ntube_kappa_t_union` (rewritten) | G-lat scoped; ntube EY bug fixed |
| 2026-07-12 | **P3 verdict CORRECTED/DOWNGRADED after a PAPER_OUTLINE review** (`docs/puckworks_paper_outline_review.md`). The 2026-07-11 verdict ("only static channeling reproduces the schmieder interior peak from physical parameters") rested on a **dimensionally invalid target**: `_schmieder_mass_vs_grind` averaged `mass_in_cup` across component, **unit** (trigonelline/caffeine/5-CQA mg + TDS g), brew ratio, and temperature — a no-coherent-unit aggregate; the gate passed on software reproducibility, not scientific validity. **Fix:** replaced with per-observable, fixed-condition functions — `schmieder_grind_response` (raw cells, single component×BR×T×flow, with a 'no silent observable merge' unit guard) + `schmieder_rsm_grind_curve` / `schmieder_interior_max_target` (schmieder's OWN Eq.4 RSM per observable). Finding: the RSM is concave with an interior grind vertex for all 4 observables **but** weak (adj-R² 0.41–0.75), and the raw cells at the fixed central condition are largely monotone (interior max ≤1/4); GL 1.7 is the FINEST d₃₂ → a DIAL peak, not a particle-size dip. **Downgraded verdict:** MODEL CAPACITY, not identification — static heterogeneity is the only implemented generator that makes an interior max without a doctored constant; σ(φ₁) is itself empirical (partly circular); #2 wetting untested. Docs (P3_hypotheses CORRECTION box + VERDICT, ANALYSIS_P2 §2.3) rewritten; no promotion. | `gate_p3_schmieder_peak_discrimination` (rewritten) | 2.3 P3 verdict corrected (capacity not identification) |
| 2026-07-11 | **G4 (temperature) — extraction-chemistry part PARTIALLY resolved** (`harness.g4_temperature_sensitivity` + `gate_g4_temperature_sensitivity`, QUICK). Two INDEPENDENT partition closures on file (romancorrochano Arrhenius K(T), pannusch van't Hoff K(T)) both move K by <15% over 80→98 °C; propagated extraction-extent shift ~1.8 pp (romancorrochano stirred vessel with K(T),Deff(T)); schmieder2023's measured cup concentration spans a median 3.4% across its 80/89/98 °C axis at the DoE-center grind+flow (per-solute; the matching NEGATIVE datum). → extraction-chemistry T-effect is SMALL and empirically confirmed, cross-validated in MAGNITUDE by two closures + data. **Surfaced, not merged (rule 6):** the two K(T) closures DISAGREE on the sign of dK/dT (roman +9.4%, pannusch −5% for caffeine/trig/5CQA) — a partition-convention difference reported side by side. REMAINDER open: in-puck thermal transients + wetting/swelling-T (no model/data). G4 gap note updated (partial). | `gate_g4_temperature_sensitivity` | G4 extraction-chemistry partial (thermal/wetting-T open) |
| 2026-07-11 | **N-tube κ(t) union — per-tube coupling is unconditionally unstable** (`harness.ntube_kappa_t_union` + `gate_ntube_kappa_t_union`, QUICK; exploratory synthesis, qualitative). Fused the P3 winner (streamtube channeling) with the P2 winner (coupled_kappa_t extraction-opens porosity): each parallel tube gets its own extraction-driven κ(t) clock (σ(gs) from the calibrated streamtube closure, clock from empirical waszkiewicz m_d(t), conductance M(φ) from the poroelastic closure — no invented params). **Under flow control the poroelastic coupling is unconditionally unstable**: flow latches into a SINGLE channel within ~3 s (top-decile share 0.31→~1.0), EY collapses 16%→2.5%. Three controls: (1) the gentle Kozeny-Carman auxiliary closure does NOT run away → it is the near-choke sensitivity (the closure P2 proved required for the 14× whole-bed rise) that destabilizes the ensemble; (2) step-size invariant (2/8/32 substeps) → not an Euler artifact; (3) a lateral pressure-equalization term (≥0.5) regularizes it → the parallel-non-exchanging assumption is what breaks. New gap **G-lat** (lateral tube coupling as a STABILITY requirement for dynamic channeling-κ(t)). ANALYSIS_P2 §2.4. | `gate_ntube_kappa_t_union` | G-lat opened; §2.2 pt-2 per-tube observable delivered |
| 2026-07-11 | **P3 fine-grind-dip VERDICT** (`harness.schmieder_peak_discrimination` + `gate_p3_schmieder_peak_discrimination`, QUICK): the culmination of the P3 cluster. Ran all four instrumented mechanisms against the schmieder2023 cup-mass target (a real but WEAK ~1 g/97 g interior peak at GL 1.7, unambiguous only at the lowest flow — flow 2 is monotone, flow 3 marginal; stated honestly, no flow-washout overclaim). **Only static channeling (#1) reproduces the interior maximum from PHYSICAL parameters** (monotone σ(grind) closure → peaked ensemble EY, peak gs≈1.5, deficit largest at finest grind). Lee (#3) makes the shape only at a doctored ceiling ρ_c=798 (physical ρ_c=399 plateaus); size-exclusion y₀ (#4) and the diffusion/base null are structurally monotone → cannot make a non-monotonic peak. Compares SHAPE not dial location (rule 9). Does NOT exclude #2 (incomplete wetting) — that lives in the open G1 gap and is discriminated by first-drip DELAY, not EY shape. `docs/P3_hypotheses.md` P3 VERDICT section. | `gate_p3_schmieder_peak_discrimination` | 2.3 P3 verdict (fine-grind dip = channeling) |
| 2026-07-11 | **3.1 mo2023_2 extraction layer** (`mo2023_2.extraction`, added to the mo2023_2.swelling component): the swelling-coupled fixed-flow solute extraction (Eqs 9–17, 2-population, reusing romancorrochano bed_lumped). `gate_mo2_swelling_insensitivity` reproduces the card's **gate-4 headline**: at FIXED flow the swelling-on vs swelling-off yield differs by only **1.2–1.4%** (their Fig 2) — swelling raises ε_p (+15% D_p) but grows R (R²+7%), which offset. This is the sharp **contrast** with the fixed-Δp flow decay (~19× throttle): swelling matters enormously at fixed Δp, negligibly at fixed q. Yield rises with beverage mass (Fig 8 trend). The mo2023_2 model is now complete (swelling + extraction). | `gate_mo2_swelling_insensitivity` | 3.1 (extraction layer) |
| 2026-07-11 | added `docs/ONBOARDING.md`: fixed session entry point (access check, read order, live-state verification, standing caveats). Linked from README (top) and CLAUDE.md (Read first, always). | `docs/ONBOARDING.md` | onboarding |
| 2026-07-11 | **κ(t) card Eq.2 corrected card-side to match the code** (Tim patch). The `brewer2026_coupled_kappa_t` card's first draft printed Eq.2 as κ=Kozeny-Carman(ε); the implementation had (correctly) driven the flow through the waszkiewicz **poroelastic** closure, because CK is far too gentle for the near-choke 14× rise (RMSE ~1.5 vs 0.116) and the exact-poroelastic degeneracy gate is unpassable with CK. Card Eq.2 (+ the Assumptions κ(ε) bullet + the degeneracy-gate wording) now specify the poroelastic closure as REQUIRED/operative, with CK retained as auxiliary/illustrative (gentle non-choke regime) only. Code docstring/registration/gate notes reconciled from 'ambiguity flagged' → 'corrected'. Card and code now agree; the record keeps that the first draft disagreed and the code was right. | (card + code notes) | κ(t) Eq.2 reconciled |
| 2026-07-11 | **Blocker 3 UNBLOCKED: G9 largely resolved** (Tim basket cards schulman2011/_baskets, mckeonaloe2022). None measured ΔP/resistance (all geometry only), but the schulman2011 14-basket geometry (A_h, hole diameter) → an [RS] orifice + Poiseuille screen-resistance construction gives R_screen ~6e6 Pa·s/m³, **~5–6 orders below the DE1 total (screen/total 3.7e‑5) → NEGLIGIBLE**. So the clean-basket screen is NOT a co-controlling resistance, and the earlier suggestive fitted-vs-measured κ gap is coffee/grind, not screen (consistent with revised grudeva). `gate_g9_series_resistance` upgraded from suggestive→resolved. Data intaken (`schulman_baskets` + manifest); caveat: clean basket only, clogging unmeasured, [RS] Cd/plate-thickness assumed. | `gate_g9_series_resistance` | G9 resolved (clean basket) |
| 2026-07-11 | **G9 series-resistance model** (`harness.g9_series_resistance` + `gate_g9_series_resistance`): the Darcy decomposition R_total = R_puck + R_series(screen+fixture). R_puck from the independently-measured romancorrochano tamped κ is **3–47 %** of the DE1 fixture-A total resistance, and the FITTED effective κ lineages (DE1 7.4e‑15, grudeva 2.2e‑15) sit **below** the measured tamped κ (≥2.6e‑14) — a fit folds non-puck resistance into an over-dense κ, so a series residual is implied. Independent but **cross-source** (different coffee/grinder) → suggestive, not conclusive; the revised grudeva adjudication (κ inside her K-C band) further weakens the sieve case. **G9 stays open** — closing it needs a matched puck-κ + in-machine total-R measurement. Gap note updated. | `gate_g9_series_resistance` | G9 partly addressed |
| 2026-07-11 | **mo2023_2 Fig 8 within-error-bars — BLOCKED (noted).** Tried closing the card's gate-3 (type-M yield/strength within replicate bars, M_c<30 g) against the reduced `mo2023_2.extraction` lumped-bed model. Best single physical scale lands only **4/9** points inside the tight bars: all M_c=20 g points fit, but the model **under-extracts at low M_c** (5–10 g miss by 2–3 pts) — its yield(M_c) rises too steeply. Root cause: the reduced independent-2-population lumped bed lacks the paper's **depth-resolved coupled bed + fines early-release**; the card's required filling front would only cut early extraction further. The full within-bars gate needs that coupled-bed rebuild (M-effort; card itself calls the fit imperfect, 'good only for M_c<30 g'). Trends + mid-shot level already gated (`gate_mo2_fixed_flow_trends`, `_swelling_insensitivity`). Moved on. | (assessment) | mo2023_2 Fig 8 blocked (coupled bed) |
| 2026-07-11 | **G1 retention-curve need carded as a SEARCH TARGET** for the intake project: `docs/cards/g1_retention_search_target.md`. A card describing what to FIND (a measured coffee-bed water-retention curve θ(ψ) + relative permeability K_r, saturation-resolved, real units; or van-Genuchten/Brooks–Corey params) rather than an existing paper — with acceptance criteria, the negative filter (foster sharp-front / egidi2018 soil solver / mckeonaloe2021 pixel √t do NOT satisfy), and a search strategy (soil-physics porosimetry/tensiometry on coffee, NMR/MRI moisture profiling, µCT saturation segmentation; groups/venues/search terms). When a source is found it replaces the card and its data becomes the constitutive input to a Richards G1 component. | `docs/cards/g1_retention_search_target.md` | G1 search-target card |
| 2026-07-11 | **G1 search target sharpened**: named the specific constitutive data that unblocks the Richards G1 wetting model — a MEASURED water-retention curve θ(ψ) + relative permeability K_r(θ/ψ) for a (ideally tamped) coffee bed with SATURATION resolution (van-Genuchten/Brooks–Corey α,n,θ_r,θ_s directly ingestible), NOT a wetting-front trace. Recorded what does NOT satisfy it (foster sharp-front, egidi2018 soil solver, mckeonaloe2021 pixel √t) and method sources to scan (soil-physics porosimetry/tensiometry on coffee, NMR/MRI moisture profiling, µCT saturation segmentation, centrifuge/pressure-plate retention). §4 G1. | (search target) | G1 data need specified |
| 2026-07-11 | **mckeonaloe2021 intake → SKIP** (card verdict concurred). Pre-wetting capillary-imbibition post: a single uncalibrated n=1 trial of h(t)=C√t (Lucas–Washburn) at ZERO applied pressure in a loose untamped bed, **pixel units with no scale, no dose/grind/temperature metadata** → nothing transcribable. Superseded by `foster2025.infiltration` (contains the capillary term explicitly, reduces to this √t law in the zero-pressure limit, gated on micro-CT). **Does NOT help the G1 wetting-model search:** it is SHARP-FRONT and explicitly silent on partial saturation behind the front — the continuous-saturation constitutive curves G1 is blocked on. Kept the one useful thread: the *pre-wetting ≠ pre-infusion* distinction is the conceptual frame for fine-grind-dip hypothesis #2 (an incompletely pre-wet puck), noted in `docs/P3_hypotheses.md`. No data/loader/component. G1 stays blocked on constitutive data. | (card committed) | mckeonaloe2021 skip; G1 unchanged |
| 2026-07-11 | **ONBOARDING.md refreshed** with the recent components + blocker resolutions: added `ANALYSIS_transfer.md` to the read order; new standing caveats — pannusch↔angeloni does NOT transfer (non-identifiable single-grind refit, G6), `brewer2026.coupled_kappa_t` is a `kind=synthesis` framework with the poroelastic (not CK) closure, mo2023_2's two extraction implementations are both kept on purpose, and G9 is resolved for clean baskets (screen negligible; only clogging open). | `docs/ONBOARDING.md` | onboarding refresh |
| 2026-07-11 | **Blocker 2 UNBLOCKED: `mo2023_2.coupled_bed`** registered (component #22, extraction/runtime), following the (a)→(b)→(c) attack plan. **(a)** killed the normalization bug in isolation (single-cell mass balance): the grain→bed surface flux took du/dξ but the state is u=ξ·C so it needed dC/dξ → ~12× solute loss; fixed (+ dropped a spurious ε_p) → mass conserves to ~0.99 (converged). **(b)** added the card's filling front (Eqs 29-30; checked foster reuse — foster is fixed-P sqrt-front, this is fixed-q *linear* plug-fill, same family/different driving) with the cup = pumped − dead-volume correction → **5/9 within bars (beats reduced 4/9)** and **shape-spread 37% (vs 110%)**, untuned. **(c)** moot: the M_c=20 over-prediction is CONVERGED (refinement worsens it) → genuine model-vs-data, matching the card's 'overestimates beyond M_c~30 g' caveat, not an implementation gap. Both metrics reported, not tuned to win; the coupled bed earns the Fig-8 slot, the reduced stays for the swelling-insensitivity gate. | `gate_mo2_coupled_bed_fig8` | Blocker 2 resolved (coupled bed) |
| 2026-07-11 | **Blocker 2 PARTIAL: mo2023_2 depth-resolved coupled bed** (`mo2023_2.coupled_bed`, WIP, not registered). Built the depth-resolved through-flow bed (Eqs 19-24: clean water down N_z layers, fine+coarse hindered-diffusion grains per layer with the partition BC, vectorized over grains) to fix the reduced lumped model's low-M_c under-extraction. Progress: the yield(M_c) SHAPE consistency improves (implied absolute scale spread narrows ~50-60 → ~91-110 across M_c), and strength lands in the right ballpark. But it does NOT yet pass gate-3 within replicate bars (3/9 vs reduced 4/9) — three items remain: (a) a residual ~2-3× absolute-normalization factor (flux/inventory-units bug), (b) the card's REQUIRED filling front (Eqs 29-30, not implemented), (c) the paper's exact Appendix-A.2 numerics. Preserved as a continuation point; moved on per instruction. | (WIP module) | mo2023_2 coupled bed (partial) |
| 2026-07-11 | **Blocker 1 UNBLOCKED: `brewer2026.coupled_kappa_t`** registered (component #21, `kind=synthesis`, bed_dynamics) against Tim's new card. One shared porosity ε(t), four branches compose **additively** (fixes the multiplicative harness double-counting): extraction+ (waszkiewicz m_d/dose), swelling− (mo2023_2), compaction−/fines− (fasano II/I, params unidentified → structural stubs). **Degeneracy gate EXACT**: extraction-only reduces to `waszkiewicz2025.poroelastic` rung 4 (RMSE 0.116 == 0.113). **Composition diagnostic**: adding the parameter-free swelling branch over-closes the saturated pre-wet rig → residual 0.648 (worse than the flat null 0.603) → diagnoses mo2023_2's fixed-Δp swelling is mis-scaled here (reported, not tuned, per card). **⚠️ CARD AMBIGUITY FLAGGED for Tim:** card Eq.2 (κ=Kozeny-Carman(ε)) is inconsistent with its own exact-poroelastic degeneracy — CK is far too gentle for the near-choke 14× flow rise (RMSE ~1.5 vs 0.116); the flow uses the poroelastic closure, CK is reported as auxiliary. Tim to reconcile Eq.2. | `gate_kappa_t_degeneracy`, `gate_kappa_t_composition_diagnostic` | κ(t) synthesis component (Eq.2 flag) |
| 2026-07-11 | **coupled κ(t) closure** (`harness.coupled_kappa_t` + `gate_coupled_kappa_t`): upgraded the κ(t)=κ₀·f framework from its linear-ramp placeholder to a genuinely COUPLED runtime closure driven by LIVE registered-model outputs — extraction EY(t) from cameron2020's running cup mass, swelling ε_b(t) from mo2023_2 at the real shot times, compaction from waszkiewicz at P. Over a real 9-bar/30-s shot the trajectory is **non-monotone** (κ/κ₀ 0.342 → **min 0.172** as swelling bites → 0.327 as EY→19 % opens porosity): the swelling-closes-then-extraction-opens competition plays out on real curves. **BLOCKER (noted): registering this as a component is card-blocked** — the multiplicative composition is our modeling choice with no card (CLAUDE.md rule 1); it stays a harness runtime closure. Promoting to a registered `bed_dynamics` component needs a card for the κ(t)=κ₀·f composition first. | `gate_coupled_kappa_t` | κ(t) coupled runtime (registry card-blocked) |
| 2026-07-11 | **positive control: fractions resolve the rate** (`validation/slow/identifiability.py`) → completes the transfer identifiability story + **resolves gap G6**. Same pannusch model, same Schmieder shots it was fit to: sweeping the kinetic rate and scoring against the fraction CURVE gives a sharp trough (edge/min ~4×, min at rate ~1) — the rate IS identified — while scoring the SAME shots collapsed to a whole-cup value is flat (edge/min ~1.2–1.3×) — not identified — reproducing the angeloni degeneracy. Holds for caffeine/trigonelline/5-CQA. Confirms the kinetic rate lives in the temporal SHAPE the cup integrates away; inventory↔kinetics (G6) separable only with time-resolved data. `docs/ANALYSIS_transfer.md §6`. | `identifiability.report` (slow) | G6 resolved; transfer story complete |
| 2026-07-11 | **paper-track writeup** `docs/ANALYSIS_transfer.md`: the pannusch→angeloni transfer study written up as an **inventory–kinetics identifiability limit**. Core result: whole-cup concentration ≈ c_s0·φ(rate,…), so a single-grind fit has a flat valley — a 6.25× rate_scale change is absorbed by c_s0 with <3 pp MAPE change (16.2→18.8%); the rate is unidentifiable and only the independent Table 7 inventory breaks the tie. Consequence: the 7% single-grind holdout is a non-identifiable curve fit, not a transfer (fails held-out C/F 25–49%). Methodological lesson for cross-dataset extraction validation (need independent inventory / joint multi-grind / time-resolved fractions). | `docs/ANALYSIS_transfer.md` | transfer identifiability (paper) |
| 2026-07-11 | **refit validated across granulometries C/F → NEGATIVE (tempers the refit)** (`validate_refit_granulometry`, slow, using the card's per-granulometry k_r(p)+τ flow). Two findings: (1) **the O-refit does NOT transfer** — fit on granulometry O then predict held-out C/F gives **~25–49% MAPE** (worst at fine), vs the same-grind O holdout ~7%. (2) The **(rate_scale, c_s0) split is DEGENERATE/flow-confounded**: refitting per grind, caffeine's rate flips 0.4→0.4→**2.5** across O/C/F and c_s0 swings 17.8→20.3→8.8 (a 2.3× spread for a fixed R&G inventory); even at O the fitted c_s0 moved 13.0→17.8 when the flow anchor changed. **Correction:** the earlier 'transfer gap CLOSED, caffeine=inventory / trigonelline=kinetic' reading was OVER-INTERPRETED — the refit is a per-granulometry CURVE FIT (~17–25% post-fit), not a transferable or physically-decomposable calibration. Confirms pannusch should stay a schmieder-fit runtime; angeloni is a transfer TARGET it does not meet across grind. | `validate_refit_granulometry` (slow) | refit tempered (negative validation) |
| 2026-07-11 | **pannusch KINETICS refit to angeloni** (`refit_pannusch_angeloni`, slow): a NEW angeloni calibration (POST-FIT). Per solute/variety, fit c_s0 (inventory LEVEL — analytic, cup is exactly linear in c_s0) + rate_scale (Sherwood-prefactor KINETICS) on the 9 on-grid granulometry-O points; **validate on the 2 held-out off-grid O points**. Mean **holdout MAPE 7.2%** (mostly single-digit) — the ~31% blind / 26% flow-refined transfer gap closes under refit. Clean decomposition: **caffeine rate_scale 1.00** (kinetics already transfer; gap was pure inventory — fitted c_s0 13.0/17.4 RECOVERS angeloni Table 7 12.5/18.6) vs **trigonelline rate_scale 0.40** (a GENUINE kinetic difference: pannusch over-extracts trigonelline for the angeloni coffee). Strength: post-fit on-grid; 2-point holdout = weak independent. Kept in `validation/slow/` (9-point fit, granulometry O only) — NOT registered; promotable to a calibration component if validated across granulometries. | `refit_pannusch_angeloni` (slow) | pannusch transfer gap CLOSED (post-fit) |
| 2026-07-11 | **pannusch↔angeloni flow-map refinement** (`flow_map_refinement`, `_flow_darcy`): replaced the crude linear-τ p→flow map with a **Darcy-consistent q~p/μ(T)** (registered water-viscosity closure; single physical anchor, granulometry O; NOT fitted). The crude map over-attributed flow to high pressure; the refinement cuts overall blind per-condition MAPE **31.3%→26.5% (closes 4.8 pp** of the residence-time gap). Combined with inventory-matching, **caffeine reaches ~14.5–15%** (near angeloni's own ~9%) — the caffeine gap was flow+inventory, both closable. But **trigonelline/5CQA stay 20–47%**: a genuine per-species KINETIC transfer gap, NOT closable by any flow map (only by refitting to the angeloni coffee). Arabica TDS response-shape still transfers (r=0.74). Honest PARTIAL closure; manifest caveat updated. | `flow_map_refinement` (slow) | pannusch transfer gap (partially closed) |
| 2026-07-11 | **pannusch↔angeloni PER-CONDITION** (`gate_pannusch_angeloni_per_condition`, slow): the demanding test the pooled-envelope bracket is not. For granulometry O across the 9 on-grid (T,p) points/variety, pannusch blind forward (p→flow via angeloni's own τ range) scores **overall MAPE 31.3% (22–50% by species)** — FAR above the envelope 'all-in' and angeloni's own ~9–13% model. Decomposition: inventory-matching (angeloni Table 7 C₀_s) HELPS caffeine (Robusta 43.7→20.8%) but HURTS trigonelline (32.8→43.3%) → not pure inventory; the per-species extraction fraction differs. Response-shape correlation is weak per species (0.04–0.39) EXCEPT **Arabica TDS r=0.73** (the total-solids (T,p) response transfers even where individual species don't). Verdict: **the envelope bracket was optimistic — pannusch does NOT predict angeloni per-condition**; cross-machine/coffee transfer is a real gap. Independent, per-condition. | `gate_pannusch_angeloni_per_condition` (slow) | pannusch independent evidence (tempered) |
| 2026-07-11 | **pannusch↔angeloni per-species bracket** (`validation/slow/angeloni_bracket.gate_pannusch_angeloni_species_bracket`): pannusch2024's blind forward cup concentrations (cl1 cancels in the normalized solver, verified) at a matched espresso condition (T=93.4, flow 1.6, grind 1.7) land INSIDE the angeloni measured ranges for **all four species — caffeine 4.56∈[4.4,9.2], trigonelline 2.46∈[2.3,3.9], 5CQA 2.92∈[2.7,6.0], TDS 9.9∈[8.5,12.6] g/L** (near the low edge). Contrast: cameron's single-lumped TDS reads LOW (0/3). So the **multi-solute kinetic model transfers to the independent angeloni dataset where the lumped model does not** — pannusch2024 is no longer post-fit-ONLY, it now has an independent (wide-envelope regime) bracket. Strength: independent (different machine/coffee/basket); NOT per-condition. | `gate_pannusch_angeloni_species_bracket` (slow) | pannusch independent evidence |
| 2026-07-11 | **D4 complete: angeloni2023 full 66-shot intake** (Tim dropped the xlsx Tables 1–7). `bioactives.csv` (66 shots × 11 species TR/TA/AA/CA/3CQA/5CQA/CF/FA/3_5diCQA/totCQA/totOA, joined to the Table 1 T/p/granulometry matrix + on/off-grid flag: 54 calibration + 12 validation), `total_solids.csv`, `lipids.csv`, `inventories.csv` → loaders `angeloni_*` + 4 MANIFEST rows + smoke tests. **`gate_angeloni_multispecies_bracket`** (`validation/slow/`, report-style, not CI): matched-(p,grind) cameron TDS vs the angeloni per-granulometry TS ranges — cameron reproduces the finer→higher ordering but reads **~2–4 TDS points LOW** (0/3 bracketed), the SAME direction as the egidi bracket → **Cameron-reads-low confirmed on a 2nd independent dataset**. Independent strength (different machine/coffee/basket). NOT a FeFlow port. | `gate_angeloni_multispecies_bracket`; `data/angeloni2023/` | D4 done; pannusch independent target |
| 2026-07-11 | **Cards committed + D4 (partial): angeloni2023** (data-only) and **egidi2018** (skip) cards tracked. **D4 intake PARTIAL:** `data/angeloni2023/inventories.csv` (Table 7 — 16 rows, 8 species × 2 varieties C₀_s mg/L) + loader `angeloni_inventories` + MANIFEST row. The 66-shot chemical campaign (Tables 2–5 bioactives/TS/lipids) is **blocked pending a Tim drop** — the values are not in the card and MDPI (Appl. Sci. 13, 2688) is Cloudflare-blocked for fetch; NOT fabricated. angeloni2023 flagged as the first **independent** multi-species validation target for pannusch2024 (§6). The `gate_angeloni_multispecies_bracket` (needs the 66-shot per-condition ranges) is deferred with the drop. **G1 refined** (§4): egidi2018 is a soil Richards *solver* — the gap is constitutive (unmeasured coffee θ(ψ)/K(ψ)); interim path = the a4a17a9 wetting-atom probe. | `data/angeloni2023/`; cards | D4 (partial); G1 refinement |
| 2026-07-11 | **Unified κ(t)=κ₀·f(P,ε,E) closure framework** (`harness.kappa_branches`/`unified_kappa_t` + `gate_unified_kappa_t`) — assembles the four registered κ-perturbing mechanisms as independently-toggleable SIGNED factors, each drawn from its component: compaction f(P)≤1↓ (waszkiewicz), swelling f(t)≤1↓ (mo2023_2), fines f(t)≤1↓ (fasano partI), extraction f(EY)≥1↑ (lee2023, CK pore-opening). The gate pins the load-bearing content — signs/limits (extraction OPPOSES the other three: 1→30× as EY→0.3 vs compaction 0.78→0.24 as P→13 bar) + reduction to unity when neutral. Framework/synthesis; the multiplicative composition is a surfaced modeling choice, not new physics. Closes the bed_dynamics backlog κ(t) item at the framework level. | `gate_unified_kappa_t` | κ(t) backlog (framework) |
| 2026-07-11 | **P3 hyp #1 static channeling** instrumented (`harness.channeling_sigma_sweep` + `gate_p3_channeling_sigma_sweep`): a MONOTONE σ(grind) closure through the fines fraction, via the streamtube EY-deficit, turns the monotone base EY into a PEAKED ensemble EY (peak gs≈1.5, near schmieder GL 1.7) — static channeling alone reproduces the fine-grind dip. Only #2 (wetting, Richards G1, no card) remains un-instrumented. | `gate_p3_channeling_sigma_sweep` | P3 hyp #1 |
| 2026-07-11 | **3.3 fasano2000_partI.fines_migration** built (component #20, bed_dynamics/calibration): a fasano-**STRUCTURED** free-boundary fines-migration model. Since the paper leaves K(b,m), M, γ unpublished (no faithful port possible), it uses OUR closures (R(u)=1+u, M=5, R_c=50, μ=0.5) + the digitized Fig 8.7 β(q), enters by GATE not inheritance (like RC-3b). Landau-mapped MOL solve of release (8.16) → advection (8.23) → compact-layer growth (8.19) → Darcy flux closure (8.25). `gate_fasano_freeboundary` verifies the paper's **analytic structure**: mass balance 8.33 closed <1%, q(t) monotone-nonincreasing (Lemma 8.3), s≥s_m=0.8 (Lemma 8.1), and **nonmonotone q∞(p₀) with an interior peak at p₀≈0.6** (rise→peak→decline, the Fig 8.6 headline) from the release→compaction→resistance feedback. Verification/mechanism strength ONLY — NOT their curve (closures unpublished), matching the card's assigned level. Completes the κ(t) backlog's compaction/counter-migration branch (with mo2023_2 swelling + lee2023 extraction branches). | `gate_fasano_freeboundary` | 3.3 (structured model landed) |
| 2026-07-11 | **3.1 mo2023_2.swelling** built (component #19, bed_dynamics/runtime): the paper's distinctive swelling→porosity→flow-throttling mechanism (the extraction half "duplicates Cameron", not built). Nonlinear swelling PDE ∂c^w/∂t=D^w(1−c^w)Δc^w in fine+coarse representative grains → swollen volume (Eq 42) → ε_b(t) (Eq 21) → Carman-Kozeny conductivity → flow ratio q(t)/q(0) at fixed Δp (Δp/μ/L cancel). `gate_mo2_swelling_flow_decay` reproduces **Fig 3(a)** for all four powders — E 0.047/H 0.051/M 0.054/F 0.102 vs data 0.048/0.053/0.057/0.118 (E/H/M within ~5%, F ~13%) — **including the mechanism's signature ordering E<H<M<F**: coarser boulders (larger ℛ_c, τ∼ℛ²/D^w) only partially swell within the shot, so coarser powders throttle less. Closed-form s_m (Eq 8) = 3.574% at C_M=0.1. First concrete κ(t) backlog candidate (swelling supplies f in κ(t)=κ₀f(ε_b(t))). Solute extraction (Eqs 9–17, Fig 8 yield/strength, fixed-q insensitivity) is a further layer, not built. | `gate_mo2_swelling_flow_decay` (+ existing k₀/trend gates) | 3.1 (swelling model landed) |
| 2026-07-11 | **3.5 romancorrochano2017.extraction** built (component #18, extraction/runtime): the multi-scale MW-resolved Fickian diffusion model. Spherical grain diffusion (method-of-lines, u=rC substitution) → partition-equilibrium surface BC C_s(R)=C_b/K → two coupling modes: stirred vessel (Eqs 3.28–34) and lumped flow-through bed (Eqs 3.35–38, del Valle linear-axial). Verified where checkable WITHOUT the unpublished raw curves: `gate_roman_sphere_solver` reproduces the **Crank analytic release to 1.2e‑4**; `gate_roman_mw_temperature_trends` drives it off the REAL tables (Deff spectrum low>med>high>vhigh, K(T) Arrhenius matches Table 4.10 <0.05, higher Deff → faster t₅₀); `gate_roman_bed_flow_trend` — the bed is mass-conserving (<1%), yield rises monotone, and **slower q → higher yield & strength emerges from the diffusion physics** (matches mo2023_2's trend). The reported MPE 5–8%/≤14% stay DATA gates (raw curves never published); per-grind R not on file → bed **absolute** EY needs a d[3,2] adapter (trend gated, not absolute). Competes with cameron2020 (pure-Fickian+MW-spectrum vs dissolution+resolved-column). | `gate_roman_sphere_solver`, `gate_roman_mw_temperature_trends`, `gate_roman_bed_flow_trend` | 3.5 (model landed) |
| 2026-07-11 | Data intake **0.12 fasano2000_partI** (Tim drop, Figs 8.1/8.4/8.6/8.7 digitized): loaders `fasano_fig8_*` + PROVENANCE + 4 MANIFEST rows + smoke test. **Scope correction:** the Fig 8.6 *model* twin is NOT faithfully buildable — the closures K(b,m), M, γ are unpublished (card "not provided"), same theory-paper wall as partII; reproducing the curve would mean inventing them. Instead `gate_fasano_cor82_nonmonotone` verifies the one faithfully-checkable claim: the paper's **Corollary 8.2** (nonmonotone q∞(p₀) requires the flow to cross the β(q) threshold) predicts the Fig 8.6 peak sits at the Fig 8.7 β steep-drop — confirmed for both thresholds (|peak p₀ − β knee q| = 0.015; β₂ peaks below β₁), a cross-figure structural check with no invented closures. `gate_fasano_reversal_signature` on Fig 8.4 (direct 17.3 / off-on resume 3.4 / inverted 14.4 mL/s — the fines counter-migration replay). Both qualitative/verification-of-digitized. **Full 3.3 free-boundary component stays implement-later** (needs K,M,γ fitted to DE1 flow traces). | `gate_fasano_cor82_nonmonotone`, `gate_fasano_reversal_signature`; `data/fasano2000_partI/` | 0.12 intake (3.3 data staged; twin blocked on unpublished closures) |
| 2026-07-11 | **§5.5 + P3 hyp #4** closed via romancorrochano y₀ (Tim drop, thesis §4.4.1 + Fig 4.19): `roman_y0_extractable` + `gate_roman_y0_ceiling_sizeexclusion`. Two readings from one table: (§5.5) the exhaustively-extractable inventory y₀(ΨA)=**0.317** nests above Cameron's espresso EY ceiling (0.245) above Liang's immersion-equilibrium ceiling (0.215) — three distinct ceilings, y₀ > cameron > liang, no promotion; (P3 #4) y₀ decreases monotonically along the coarsening ladder ΨA→ΨH (31.7→24.3%) — the **size-exclusion entrapment** signal, previously untested, now instrumented. `docs/P3_hypotheses.md` #4 flipped to INSTRUMENTED; only #1 (channeling σ(φ₁)) and #2 (wetting G1) remain un-instrumented. | `gate_roman_y0_ceiling_sizeexclusion` | §5.5 ceiling; P3 hyp #4 |
| 2026-07-11 | Data intake **0.4/3.1 mo2023_2** (Tim drop, *J. Food Eng.* swelling paper — distinct from the mo2023 arXiv microCT paper): 6 datasets (`puckworks.data.mo2_*`) + 6 MANIFEST rows + smoke test. **`gate_mo2_k0_carman_kozeny`** — the t=0 Carman-Kozeny closure `k₀ = ε_b^(3+2n)·d_[3,2]²/(72(1−ε_b)²)` (ε_b⁰=0.17, n=0.5) reproduces **Table 2** (0.97/1.2/2.0/6.8×10⁻¹³ m²) from the **Table 1** Sauter diameter for all 4 powders, max rel err 0.3% — exact closed-form **verification** (flow closure only, not swelling, per authors). **`gate_mo2_fixed_flow_trends`** — the paper's stated fixed-flow trends on Figs 6–9 (independent/qualitative): slower q→higher yield, finer grind→higher yield (E 22.7 > M 21.2 > F 16.6 at q=3), **monotone with NO fine-grind dip** (a fixed-flow machine defeats clogging). Also intaken: Fig 3(a) swelling q(t) decay (model twin target; the headline fixed-Δp claim rests on zero data), Fig 6 K-sweep (caption K-mislabel flagged), Figs 7–9 sim lines. **Full swelling model (Eqs 3–38, two nested FD solvers) is implement-later** (effort M) — build after the κ(t) discrimination is designed. | `gate_mo2_k0_carman_kozeny`, `gate_mo2_fixed_flow_trends`; `data/mo2023_2/` | 0.4/3.1 intake (k₀ verified; Figs 6–9 staged) |
| 2026-07-11 | Data intake **0.5 romancorrochano2017** (Tim drop, Birmingham EngD thesis): 9 datasets loaded (`puckworks.data.roman_*`) + 9 MANIFEST rows + smoke tests. **Table 6.1 tamped κ** (4 grinds × 3 densities) — permeability card is **DATA-ONLY** (K–C closures poorer than `wadsworth2026.inertial`), so this is a validation target / G9, not a component. `gate_roman_tamped_kappa`: κ in the 1e-14–1e-13 m² band, coarser grind→higher κ at all 3 densities (ΨE density-non-monotone, documented, NOT gated). **Fig 7.4** 15-condition parameter-free bed result → `gate_roman_bed_mpe_parameter_free`: non-fitted med-MW Deff gives MPE ≤14.3% (max), mean 10.9%, beating low/high-MW classes — verification of the reported (digitized ~±0.5 pp) result. Also intaken: Deff map (Table 4.9), K(T) (4.10), hindrance (4.8), Db (3.4), stirred-vessel MPE (5.3 + Figs 5.11/5.13). **Still open:** the full 3.5 sphere-diffusion→bed-ODE extraction model (Eqs 3.28–3.38, implement-later) and the §5.5 y₀ vs Cameron-ceiling cross-check (needs y₀=31.7% dropped as data). | `gate_roman_tamped_kappa`, `gate_roman_bed_mpe_parameter_free`; `data/romancorrochano2017/` | 0.5 intake (G9 target; 3.5 data ready) |
| 2026-07-11 | Phase 3 self-contained cluster: **lee2023.feedback** landed (fine-grind-dip hypothesis (c): extraction→ε→Kozeny-Carman κ→flow-reroute feedback). Reviewer unblocked the card (paper in evidence): Eq. 9 α=c_sat/ρ_c is correct — Table I's α=3.76 is a reciprocal typo (recorded in card Errata); EY_tot is solid-depletion mass-weighted; τ_shot nondim'd with M_dose (ρ_c cancels: τ_shot(1.1)=1.12, τ_shot(2.3)=0.48); κ=ε³/(1−ε)². Gate reproduces the paper's behaviour AND its documented **negative result** (verification+qualitative): the δ=0.035 seed amplifies at all g; the imposed ρ_c=798 gives an interior EY(g) peak with a fine-side **decline** (weak, ~0.2 pp by design); the physical ρ_c=399 only **plateaus** (no decline). Sign/shape gated, NOT amplitude and NOT any data fit. **fasano2000_partII DEFERRED** (no numeric constitutive functions exist; it is the structural template for the κ(t) compaction branch, not a port). | `gate_lee_feedback_negative_result` | P3 hypothesis (c) instrumented |
| 2026-07-11 | Phase 3 self-contained cluster: **cross-pressure discrimination harness** (`harness.cross_pressure_discrimination` + `gate_p2_cross_pressure`). One fixed calibration predicts all 11 Waszkiewicz pressures out of sample; the three κ(t) mechanisms **separate by regime** (the discriminator the multi-pressure dataset was built for, ANALYSIS_P2 §2.2): dissolution Φ(t) has the best OOS-mean RMSE (0.356 vs static null 0.512) but is **not** a universal winner — RC-3b (flow-coupled) wins the low-pressure end (0.231 vs Φ 0.473: slow flow → pressure-dependent dissolution matters), and the static null wins mid-range (0.352 vs Φ 0.438: little time structure to explain). Verdict pinned as **no single winner**, tempering the 9-bar-only "Φ(t) is the mechanism" reading. | `gate_p2_cross_pressure` | 2.2 discrimination (cross-pressure) |
| 2026-07-11 | Phase 3 self-contained cluster (start): **RC-3b** Cameron-coupled poroelastic added as **P2 ladder rung 5** (`waszkiewicz2025.poroelastic.q_dynamic_from_md` + harness). Cameron's diffusion-limited extracted mass drives Φ(t) instead of the empirical sigmoid → RMSE 0.39 g/s on the 9-bar trace: **beats the flat nulls (0.603) but is 3.5× worse than the empirical near-instant rung 4 (0.113)** → near-instant dissolution favored, corroborating §5.6. RC-3b is a NEW coupled model (not validated by the Waszkiewicz paper); it enters by the ladder, not inheritance. | `gate_p2_kappa_ladder` (extended, rung 5) | 2.2 discrimination (rung 5 begun) |
| 2026-07-11 | CHAT analysis (items 2.1/2.2/2.3/1.4) → `docs/ANALYSIS_P2.md`. 2.1 extraction workup (strength-tagged; the Cameron-reads-low-vs-egidi finding surfaced). 2.2 κ(t) verdict **partial by design**: a time-dependent bed mechanism is required (rung 4 beats flat nulls 5.4×) and dissolution-Φ(t) is *sufficient* but not *unique* — discrimination pends Phase 3 rung 5; names the cross-pressure test (fit@9bar, predict the other 10 Waszkiewicz traces) as the decisive design. 2.3 fine-grind-dip verdict open, next two computations named (σ(φ₁) sweep; G1 continuous-saturation model). 1.4 **matched-parameter design delivered** (meet in Moroney's ε-valid domain, sweep ε, accept on ε-linear divergence) → now a CC-implementable S task. | `docs/ANALYSIS_P2.md`; numbers reproduce from `puckworks.harness` | 2.1/2.2/2.3/1.4 |
| 2026-07-11 | Data intake **0.4 mo2023** + **0.3 egidi2024** (Tim drop) → closes two Phase-1/2 gaps. **1.1 Mo Re overlay (§5.2):** mo2023 24 microCT (kD,kF,k₁) pairs + Fig 8a + PSD intaken; `gate_mo_reynolds_overlay` reproduces Re 0.85–3.85 from Fig 8a at Mo's SPH conditions (µ=1e-3, ρ=1000, d43) + the Darcy→Forchheimer kD decline → §5.2 now overlays all three diagnostics (NOT interchangeable). **k₁-units caveat (§5.3)** carried in loader + manifest. **2.1 egidi bracket:** egidi Table 2 (12-cond EY/TDS) intaken; `gate_egidi_bracket` + harness — RC-1 EY bracket 19.1–22.6%, cameron reads ~15% (below, documented). | `gate_mo_reynolds_overlay` (wadsworth2026.inertial), `gate_egidi_bracket`; `data/mo2023/`, `data/egidi2024/` | §5.2 (settled 3-way); RC-1 bracket |
| 2026-07-11 | Card fix (Tim-flagged): the "Cameron **Tables 2/7/8**" reference does not exist in Cameron et al. Matter 2020 — corrected to **SI Tables S1–S5** (already transcribed in `extraction_bdf.py`) + **Fig. 5** EY curve, in `cameron2020.md`, `grudeva2026_2.md`, §2/§3/§6, and the registry note. The "cameron-vs-Cameron-tables" data-drop was bogus (no drop needed; cameron is gated on its mass budget); an optional Fig. 5 EY-curve gate remains. | Cameron et al. Matter 2 (2020) SI | RC-1; item 2.1 |
| 2026-07-11 | Phase 1/2 closeout (group A): **1.8b** `simulate_fractions_qt` machine-driven Q(t) adapter (A2) → **RC-4b** (reduces to RC-4a on constant flow, 0.0 rel err; live under a flow ramp). **2.3** `docs/P3_hypotheses.md` fine-grind-dip registry. **cameron2020.extraction_bdf gated** (mass-budget conservation EY==EY_solid, below inventory ceiling — was ungated). **1.4** moroney-vs-cameron mutual-validation determined **regime-blocked** (Cameron ε≈1.6 espresso/clean-IC vs Moroney ε≈0.13 drip/saturated-IC) — needs matched-parameter CHAT alignment, not a mechanical gate; Fig-6 gate stands. | `gate_pannusch_qt_adapter`, `gate_cameron_conservation`; `docs/P3_hypotheses.md` | RC-4b; P3; cameron | 
| 2026-07-11 | Sprint 9 (CC part) item 2.2: ledger **A8** (`BedState.porosity_profile / fines_mobile / fines_bound`; SCHEMA 0.4→0.5) + the **P2 kappa(t) null-first ladder** (`harness.kappa_t_ladder` + `gate_p2_kappa_ladder`). On the Waszkiewicz 9-bar rising-flow trace: rung 4 time-dependent Φ(t) (RMSE 0.113 g/s) **beats the flat constant-κ / static-κ(P) null rungs 1/3 (0.603 g/s) by 5.4×** — a bed mechanism IS required for the rising residual. Rung 2 = foster flow-minimum null (validated separately). **Rung 5 challengers (mo2023_2, fasano I/II, lee2023, RC-3b) are Phase 3.** CHAT "which mechanism survives" is not-CC. | `gate_p2_kappa_ladder`; `tests/test_harness.py` | P2 discrimination (partial) |
| 2026-07-11 | Sprint 7 item 1.6 completed: `foster2025.machine_mode` **data-validated** against the digitized Figs 12-15 (Tim drop). **Fig 15 flow-minimum reproduced** — bed flow Q/Qm = 0.181 at t=2.0 s (RMSE 1e-4 vs the trace) → the **P2 null baseline** (Sprint 9 ladder rung 2). s(t)/H(t) match the paper's fitted ODE curves to line width (RMSE 0.002/0.053 mm) and bracket 4-5/8 CT points (qualitative-good, per the paper). Key: Fig 15 Q_norm = bed flow min(Q_p,f)/Q_m (Eq 18), not pump flow. | `gate_foster_fig15_flowmin`, `gate_foster_ct_trajectory` on `data/foster2025_2/` | RC-3a machine mode; P2 rung 2 |
| 2026-07-11 | Sprint 8 (CC part) item 2.1: P1 extraction comparison harness (`puckworks/harness.py` + `gate_extraction_harness` + `validation/slow/extraction_harness.py`). Surfaces the P1 normalization hazards as config never silently merged — **c_sat {170, 212.4, 224}** (§5.4), per-model soluble-inventory reference (A5). Per-dataset residuals tagged by validation strength: pannusch→Schmieder (post-fit MAPE), grudeva→C1 vials (post-fit), liang→cameron ceiling (§5.5 independent). **§5.6 dissolution-speed settled**: Waszkiewicz TDS early/peak = 0.968 → near-instant dissolution (vs cameron diffusion-limited, τ_boulder ≈ 23 s). CHAT workup (2.3) is not-CC. | `gate_extraction_harness`; `tests/test_harness.py` | P1 comparison; §5.4/§5.6 |
| 2026-07-11 | Sprint 7 (partial) items A1 + 1.6: ledger **A1** (`MachineState` p_p/p_h/P_basket/dP_bed + `PumpHeadspace`; SCHEMA 0.3→0.4) + `foster2025.machine_mode` landed & **verification-gated** (machine, runtime) — pump/headspace/front ODE (Eqs. 2-27) reproducing **t_p=0.823 s, t_s=6.665 s** from Table I/II (the reported times = model + fitted t_shift=0.796 s, caught by checking the published values). §5.9 pressure-node identification recorded in manifests (Waszkiewicz basket_pressure=P_basket; DE1 node open). **Fig 15 flow-minimum shape + Figs 6/8 CT validation PENDING digitized figures; 1.8b deferred.** | `gate_foster_machine_tp_ts`; `data/foster2025_2/foster2025_params.csv` | RC-3a machine mode (enables); P2 null baseline |
| 2026-07-11 | Sprint 6 (complete) item 1.8a: `pannusch2024.solver` landed & **gated** (extraction, runtime) — the full 1D two-grain multi-solute extraction PDE (method of lines, 5-pt biased-upwind advection + BDF with a sparse Jacobian), a **faithful port of the released MATLAB**. Reproduces the authors' fit MAPEs vs the Schmieder kinetics: **TDS 6.72 / caffeine 6.42 / trigonelline 10.18 / CGA 7.22 %** (published 6.07/4.59/7.85/4.98; post-fit reconstruction; centre-grind approx). Experimental kinetics extracted from `ExperimentalData.mat` → `data/pannusch2024/experimental_kinetics.csv`. Constituent-part unit tests (FD exactness to deg 4, Jacobian sparsity, single-exp) + slow ladder. **Creates RC-4a.** | `gate_pannusch_solver_mape`; `tests/test_pannusch_solver.py`; `validation/slow/pannusch_mape.py` | RC-4a (created) |
| 2026-07-11 | Sprint 6 (partial) item 1.8a: `pannusch2024.closures` landed & **gated** (extraction, calibration) — the temperature/flow constitutive slice (Wilke-Chang D, VDI water μ/ρ, Sherwood Sh=A Re^B Sc^(1/3), van't Hoff K(T)) ported faithfully from the released MATLAB. Anchors: μ@90C=3.13e-4 (card 3.15e-4), ρ=959, K(Tref)=Kref, weak T-dependence. Table 2 fitted params transcribed (`data/pannusch2024/table2_*.csv`, git-tracked exceptions). **Full 4-solute PDE forward solver + fit-MAPE reproduction (RC-4a) DEFERRED** (large port, no MATLAB cross-check, experimental data in opaque .mat). | `gate_pannusch_closures` on `data/pannusch2024/` | RC-4a (closures ready; solver pending) |
| 2026-07-11 | Sprint 5 item 1.7b: `grudeva2025.reduced` landed & **verification-gated** (extraction/infiltration, runtime) — a **faithful port of the released reference solver** (github YoanaGrudeva/espresso-model). **G0 confirmed**: the solver's front-ODE + region-(i) capacitance carry NO ε (settles LOG Issue 1). G2 solute budget 2.92 g vs exp 2.95 g; G3 per-vial masses 9/13 within 1 SD (post-fit); G4 κ Eq6.14@9.2bar=2.27e-15 == adjudicated (settles Issue 2a). Slow ladder: resolution-converged + ε-form discrimination (no-ε plateau 2.83 vs printed-ε 0.44). G5-pre: `GrindState.fines_radius_m`, SCHEMA 0.2→0.3. | `gate_grudeva_no_eps_kappa`, `gate_grudeva_reduced_solver` on `data/grudeva2025/`; `validation/slow/grudeva_convergence.py` | **creates RC-2** (verification-gated until companion dataset) |
| 2026-07-11 | 1.7a complete: grudeva2023/2026 cards retired, grudeva2025 card of record added; Eq. 74 ε adjudicated out (strong, tiers 1+2); κ decade error corrected; correspondence Q(a)-(d) drafted, held pending Sprint 5 G0. | `docs/cards/grudeva2025.md` RECONCILIATION LOG; §5.1→§7.2 | 1.7a; unblocks Sprint 5 / 1.7b |
| 2026-07 | rev. 2: added glossary (§0), adapter ledger (§1A), P1 hazards + P2 ladder + P3 table, RC-3a/b split + pressure-node table, 1.7a/b and 1.8a/b splits, G9/G10, §5.9/5.10, validation-strength columns, this section | review pass vs cards | all |
| 2026-07-10 | D1 intake: 0.2 waszkiewicz2025 Zenodo dataset landed (`data/waszkiewicz2025/`: 11-pressure Q(t) traces, TDS fractions, static/TDS/solids calibration, brewer quadratic, Mastersizer PSD) with `puckworks.data` loaders + smoke tests. 0.6 Wadsworth Table 1 manifest row + 8.1e-17 erratum recorded (PSD zip network-blocked). 0.1 Schmieder/Pannusch network-blocked. | Zenodo 10.5281/zenodo.18046315 (CC-BY-4.0); `tests/test_data_loaders.py`; `data/MANIFEST.csv`; blocked items in `data/BLOCKED_INTAKE.md` | RC-3, 1.2; RC-4 (0.1 pending); 1.5 (Table 1 ready, PSD pending) |
| 2026-07-10 | Sprint 1 item 1.2: `waszkiewicz2025.poroelastic` landed & **gated** (bed_dynamics, runtime) — Eq. 16 static + Eq. 18 dynamic. Card-only → gated. | static refit recovers (P_c,Q_c)=(12.39,1.897) == published (independent-within-rig); 9-bar Q(t) parameter-free long-run 1.6% / corr 0.982 (post-fit). `gate_waszkiewicz_static_refit`, `gate_waszkiewicz_dynamic_9bar` on `data/waszkiewicz2025/` | RC-3a (creates the bed_dynamics slot) |
| 2026-07-11 | Sprint 3: items **1.3** `liang2021.desorption` + **1.4** `moroney2016.surrogate` landed & **gated** (both extraction, calibration) after Tim dropped liang Figs 3/4/5 + moroney Fig 6 (Table 1 transcribed). 1.3: K*E_max refit 0.219 (Fig3, card 0.215), E_oven kernel MAPE 0.088 (Fig4), §5.5 equilibrium ceiling 0.215 < cameron inventory 0.245 (K<1, distinct quantities). 1.4: leading-order composite reproduces Fig 6 plateau + wash-through (c=½ at t≈3.1) — qualitative; tail/outer-solution + cameron-BDF mutual-validation deferred (not on card). | `gate_liang_kemax_refit`, `gate_liang_eoven_ceiling`, `gate_moroney_fig6_washthrough` on `data/liang2021/`, `data/moroney2016/` | §5.5 (partial); P1 harness anchors |
| 2026-07-11 | Sprint 2: ledger **A7** (`contracts.FlowLaw` + `assert_si_permeability` + `BedState.k_I_m`; SCHEMA_VERSION 0.1→0.2) + item **1.1** `wadsworth2026.inertial` landed & **gated** (flow, runtime). Fo_F band 0.0161–0.0638 reproduced (eq2.7); Darcy recovery k_I→∞; §5.2 audit on DE1 fixture A. **Settles §5.2:** tamped DE1 Fo_F ≈ 0.86 (eq2.8)/5.7 (eq2.7) ≫ the untamped 0.016–0.064 band → flow sits at/past the inertial onset (backlog 0.3–0.9 side, not laminar). Mo Re overlay deferred (needs 0.4). | `gate_inertial_fo_band`, `gate_inertial_darcy_recovery`, `gate_inertial_de1_audit` on `data/de1_fixtureA.json` | RC-1, RC-3 (Fo_F flag); §5.2 resolved pending Mo overlay |
| 2026-07-11 | Card fix (§5.7-class typo): `wadsworth2026_grindmap.md` β,R₀ corrected 4.3505e-5/1.0160e-4 → 5.8050e-5/1.3797e-4 (Table-1 refit R²=0.994; Tim confirmed typo). Component `BETA_CARD/R0_CARD` synced; `gate_grindmap_refit` now reports `card_reproduces=True`. | `data/wadsworth2026/wadsworth2026_table1_full.csv`; card + PROVENANCE + BLOCKED_INTAKE updated | 1.5 grind priors |
| 2026-07-10 | Sprint 1 item 1.5: `wadsworth2026.grindmap` landed & **gated** (grind, calibration) after Tim dropped the full Table 1 → `data/wadsworth2026/`. <R>=βG+R₀ refit (R²=0.994) + S(G) trend + A9 dial-space adapter stub. Card-only → gated. **⚠ card β,R₀ (4.3505e-5/1.016e-4) do NOT reproduce** — OLS gives 5.805e-5/1.380e-4; operative map uses the refit, card flagged for INTAKE reconciliation. | `gate_grindmap_refit`, `gate_grindmap_polydispersity` on `data/wadsworth2026/wadsworth2026_table1_full.csv`; S=<R><R²>/<R³> reconstructs reported S <5e-3 | grind priors for all RCs (A9) |
| 2026-07-10 | D1 intake (Tim drop): 0.1 Schmieder kinetics landed (`data/schmieder2023/`: Table A1 avg + S2 per-rep fits + S3 cup masses + S1 raw fractions + Table 3 RSM, parsed exact from CC-BY supplementary xlsx + JATS XML; Exp7 == card). Pannusch Mendeley repo on disk (gitignored); Table 2/PSD deferred to 1.8a. 0.6 PSD zip requested from authors (§5.8). grindmap DOI == permeability DOI confirmed = one paper. | Foods 12,2871 DOI 10.3390/foods12152871 (CC-BY); `tests/test_data_loaders.py` (9 pass); `data/MANIFEST.csv` (14 rows) | RC-4 (1.8a); 1.3/1.4 context |

### 7.2 Resolved conflicts
Resolved §5 entries remain listed here for one release cycle with their
resolution and evidence, then move to docs/archive/.
| entry | resolution | evidence | resolved date |
|---|---|---|---|
| 5.1 Grudeva source conflict | resolved 1.7a — see `docs/cards/grudeva2025.md` RECONCILIATION LOG; adjudicated no-ε form; two named parameter configs; emergent finding: κ and P_app carry decade typos in both sources, adjudicated κ ≈ 2.2e-15 m². | `docs/cards/grudeva2025.md` (merged card of record); retired grudeva2023.md + grudeva2026.md | 2026-07-11 |
