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
| bed_dynamics | fasano2000_partI fines migration (3-state + free boundary) | R | best-developed mobile-fines skeleton; zero identified parameters |
| bed_dynamics | fasano2000_partII porosity law (8.69) | R | the named κ(t)=κ₀f(P,ε,E) closure **[RS]** in PDE form; zero data |
| bed_dynamics | lee2023 two-pathway instability | R | extraction→ε→κ feedback branch; needs unphysical ρ_c for headline trend |
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

Validation: Cameron Tables 2/7/8 (independent/gated **[RS]**); DE1 fixture A
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
| 2.1 | Extraction harness (P1) | M | 1.4, 1.7b, 1.8a, Phase 0 gate data; A5 | run cameron2020 / grudeva / pannusch(TDS channel) on matched inputs against Cameron Tables, egidi2024 Table 2 bracket, Schmieder kinetics, Grudeva vials (post-fit — label as such in reports), Waszkiewicz TDS fractions; report per-dataset residuals with validation-strength tags; explicitly test waszkiewicz's "near-instant dissolution" claim vs Cameron's diffusion-limited boulders (§5.6) |
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

**G4 — Temperature.** pannusch2024 supplies van 't Hoff K(T) + Wilke–Chang and
concludes effects above 80 °C are small; schmieder2023 provides the matching
negative datum. Nothing models in-puck thermal transients or T-dependence of
wetting/swelling (foster2025_2 flags the latter as open). Targets:
heat-transfer puck models; TU Munich (Briesen/Minceva) follow-ups.

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

**G10 — Concentration-dependent liquid properties / coffee-liquor rheology.**
Every flow-coupled model on file uses pure-water μ, ρ (foster2025_2,
waszkiewicz2025, grudeva, moroney2016, cameron lineage), yet grudeva2026
explicitly flags that viscosity rises with concentration and the early-shot
liquid sits near saturation — exactly where her plateau prediction lives.
Matters: a shared systematic bias across RC-2 and RC-3 early-shot gates.
Targets: coffee-extract viscosity/density vs TDS and temperature measurements;
food-process rheology literature.

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
| Schmieder/Pannusch | raw/segmented data beyond supplementary | not sent | — | none (Mendeley public) | Mendeley set |
| Egidi group | ρ and φ_s definitions in Eq. 4 | not sent | — | quantitative EY-gate use of Eq. 4 | infer from ref [10], flag |
| Fasano-era illy / ASIC | Eq. 8.2 a,b,c; 1993/1997 transient-discharge data | not sent | long shot | G2 validation target | digitized Figs. 8.1/8.4 (qualitative) |

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
| Cameron Tables 2/7/8 | cameron2020 | held **[RS]** | RC-1 | existing gated regression | held |
| egidi2024 Table 2 (12-condition EY/TDS) | egidi2024 | transcribe from PDF | RC-1 | independent EY/TDS **bracket**; not a pressure/T response test | **2** |
| Grudeva 13-shot vial TDS + flow | grudeva2023 | repo-check, else digitize/request | RC-2 | **post-fit reconstruction** unless companion provides holdout | **2** — RC-2 has no other experimental gate |
| romancorrochano Table 6.1 (tamped κ) + Table 4.9 (Deff map) | romancorrochano2017_* | transcribe | G9 test, 3.5 | tamped permeability *data*; not a K–C validation | **2** |
| foster2025_2 Table I/II + Figs. 6/8/15 | foster2025_2 | transcribe/digitize | RC-3 machine gates | CT fit = post-fit; DE1 first-drip triangle = independent | **2** |
| mo2023 Tables 1–5 + Fig. 8a | mo2023 | transcribe (k₁ caveat) | P6, 1.1 | simulation-derived; literature-anchored; ε circular to cameron | **2** |
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
| (none yet) | | | |
