# Model card: Cunha 2017 Mocoffee capsule CFD

**Paper/thesis:** Cunha, M. P. R. da. "Computational Fluid Dynamics (CFD) Analysis of Mocoffee's Single-Serve Coffee Capsule System." MSc dissertation, Universidade Nova de Lisboa, Faculdade de Ciência e Tecnologia, Sept 2017. No DOI; RUN (NOVA) repository. Supervisors: P. Lisboa, P. Simões.
**Stage(s):** flow, packing (informs BedState.k priors only) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Geometry-resolved 3D RANS (k-ω) CFD in ANSYS Fluent 16.0 of the Monodor/Mocoffee
single-serve capsule extraction chamber (patent US8875617): injector head with 19
perforating spikes, deformable top film with puncture holes, polypropylene capsule,
and an 18-spike bottom filter plate. The coffee bed is a homogeneous isotropic Ergun
porous zone; solute transport and extraction kinetics are explicitly NOT modelled.
Only the quasi-steady phase of the shot (phases 4–5 of the capsule cycle) is
simulated — perforation, film deformation, and bed expansion/consolidation are
excluded. Validation target is a custom JIG replicating the Bossa machine hydraulics
(Ulka EP4 pump, 0–25 bar transducer at inlet, load cell at outlet, type-K
thermocouples). This is capsule geometry, not a portafilter puck.

## Governing equations
Thesis equation numbers. What would actually be re-implemented is only the porous
closure (2.8–2.14); the rest is stock Fluent (incompressible RANS continuity 2.3,
momentum 2.4–2.5, energy 2.7, Reynolds decomposition 2.15–2.18) and is not
transcribed further here.

- (2.8) Ergun: ΔP/L = [150 μ (1−ε)² / (Dp² ε³)] υs + [1.75 ρ (1−ε) / (Dp ε³)] υs²
- (2.9) Blake–Kozeny (laminar limit, inertial term dropped): ΔP/L = [150 μ (1−ε)² / (Dp² ε³)] υs
- (2.11) Bed bulk porosity: ε_bed = 1 − ρb/ρp
- (2.12) Permeability: α = Dp² φ² ε³ / [150 (1−ε)²]
- (2.13) Fluent viscous resistance (=1/α): Rv = 150 (1−ε)² / (Dp² φ² ε³)
- (2.14) Fluent inertial resistance: Ri = 3.5 (1−ε) / (Dp φ ε³)

Symbols: ΔP/L pressure gradient (Pa/m); μ dynamic viscosity; ρ fluid density;
υs superficial velocity; ε (= ε_bed) bed porosity; Dp particle diameter; φ particle
sphericity; ρb bed bulk density; ρp roasted-particle density; α permeability (m²);
Rv viscous resistance (1/m²); Ri inertial resistance (1/m). Note the sphericity φ
appears in (2.12)–(2.14) but not in the (2.8) form as printed — the implemented
resistances are the φ-corrected ones. Turbulence BC helper relations (4.1)–(4.5)
(trapezoid hydraulic diameter, I = 0.16 Re^{−1/8}, k, ε, ω estimates) are setup
utilities, not model content.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| ρb | 400 | kg/m³ | nominal (Mocoffee spec) |
| ρp | 1200 | kg/m³ | nominal (Mocoffee spec) |
| ε_bed (via 2.11) | 0.67 | – | nominal (derived from the two above) |
| Dp (Ristretto) | 300 | µm | nominal (Mocoffee spec; Lungo 400 µm noted) |
| φ | 0.75 | – | assumed ("average value... representative") |
| Rv theoretical (via 2.13) | 1.11×10⁹ | 1/m² | nominal (computed; α ≈ 9.0×10⁻¹⁰ m²) |
| Ri theoretical (via 2.14) | 1.75×10⁴ | 1/m | nominal (computed) |
| Rv fitted | 5.9×10¹⁰ | 1/m² | fitted (to match measured inlet pressure; implied effective α ≈ 1.7×10⁻¹¹ m²) |
| Inlet velocity BC | 0.17 | m/s | assumed (fixes mass flow at incompressible density) |
| Outlet pressure BC | 1.01325 | bar abs | nominal (atmospheric) |
| Water temperature | 80 | °C | measured (JIG steady inlet/outlet, Ristretto cycles) |
| Dose per capsule | 6.5 ± 0.2 | g | measured |
| Turbulent intensity BC | 5–10 | % | assumed |
| Bed depth L, bed area | not provided | m, m² | – (geometry proprietary; not reported numerically) |

The fitted Rv is ~53× the theoretical value. It is an EFFECTIVE system resistance:
because only the porous zone was tuned, it lumps in film-puncture-hole restriction,
headspace/bypass effects, and any wet-bed consolidation — it is not a clean bed
permeability.

## Calibration and validation offered by the source
JIG data: 20 flow extractions (5 each of Crème, Espresso, Lungo, Ristretto blends;
50 ml in ~25 s) plus 20 consecutive Ristretto cycles for thermal warm-up. Steady-phase
averages reported in text: Crème 2.1 g/s at 11.3 bar; Lungo 3.0 g/s at 8.1 bar;
Ristretto 3.1 g/s at 8.2 bar (Espresso blend averages never reported). With nominal
Ergun resistances the steady model predicts inlet pressure < 1 bar vs 8.1–8.2 bar
measured — a decade-scale miss. After raising Rv to 5.9×10¹⁰, the model gives
8.9 bar inlet, 1.3 m/s outlet velocity, 3.1 g/s mass flow vs Ristretto's 8.2 bar /
3.1 g/s. This is one fitted parameter matched to essentially one target (inlet
velocity BC already fixes mass flow), so agreement is circular, not predictive —
post-fit reconstruction at a single operating point, and the author says as much
("reasonable agreement... but only for a coffee bed resistance higher than its
theoretical value"). Velocity fields (eddies around injector spikes, laminar even
flow in the bed), headspace effects, and the RTD comparison (mean residence 2.6 s
with 19 spikes vs 2.3 s with 16) are CFD-only, with no experimental counterpart.
The author further flags that y+ fell outside the valid range for the chosen
turbulence model, degrading near-wall accuracy.

## Assumptions and validity range
- Quasi-steady phase only; perforation, film deformation, pre-infusion, bed
  expansion/consolidation all excluded — precisely the phases the author's own
  data (first ~10 s of P(t)) show to be dynamic.
- Homogeneous isotropic porous bed; single Dp and sphericity; no radial porosity
  variation (acknowledged and waived); no swelling, fines migration, or k(t).
- No solute transport: zero extraction/observables content.
- Incompressible water at fixed 80 °C properties; headspace treated as
  water-filled fluid zone in the variant that includes it (no gas phase).
- Capsule geometry (19-hole membrane inlet, 54-hole spike outlet, collapsing
  bottom) — results do not transfer geometrically to portafilter baskets.
- Nominal ε = 0.67 is derived from spec densities of the dry bed; the wet
  operating porosity is unknown, so the 53× discrepancy conflates parameter error
  with genuine consolidation physics.
- Silent on: temperature dependence of resistance, blend-to-blend PSD differences
  (Crème's 11.3 bar vs Lungo's 8.1 bar left unmodelled), inertial-regime validity
  (Ri never tested independently).

## Interface mapping
Inputs consumed: none of the registry contracts directly; internally uses
(ε, Dp, φ) ≈ GrindState/BedState fragments. Outputs produced: one effective
permeability point (α_eff ≈ 1.7×10⁻¹¹ m² at nominal ε 0.67, Dp 300 µm) usable
only as a weak BedState.k prior for loose high-porosity beds, with the lumping
caveat above. No runtime coupling is sensible: the CFD is Fluent-bound,
geometry-proprietary (Solidworks files not published), and the porous closure it
uses is already in the registry in better form. If ever revisited, an adapter
would have to map MachineState.P_of_t to the inlet-velocity BC (inverted causality:
the thesis prescribes velocity and predicts pressure).

## Extractable data
Thin, and all in-text or in figures — no data tables, no raw data or code
published; availability-on-request unknown (JIG data belongs to a Mocoffee
collaboration).
- Text §5.1: per-blend steady operating points (P_inlet, Q_m) — three points,
  already transcribed in this card; a data/ file is not warranted.
- Fig. 5.1: Lungo P(t) and Q_m(t) traces over one cycle (digitizable; shows ~10 s
  pressure ramp — the only transient information in the thesis).
- Figs. 5.2–5.4: 20-cycle thermal warm-up (inlet start temp 40 °C → 73 °C;
  steady extraction ~80 ± 5 °C despite 90 ± 5 °C boiler setpoint) — a clean
  machine-thermal anecdote, but for a JIG, not a registry machine.

## Overlaps and conflicts
- romancorrochano2017_permeability: supersedes this thesis's porous closure —
  same Kozeny/Ergun family with PSD- and tortuosity-aware corrections and actual
  measured permeabilities. Cunha adds no constitutive content.
- wadsworth2026.permeability / registry theme "nominal PSD-based k overpredicts":
  the 53× Ergun-vs-fitted gap independently corroborates that spec-sheet
  (ε, Dp, φ) grossly overpredict permeability of a real extracting bed — but as a
  confounded single point (film holes lumped in), it cannot discriminate between
  consolidation, fines, or geometry explanations, so it gates nothing.
- foster2025 / machine backlog: JIG P(t) ramp is qualitatively the same
  pump-against-filling-system transient, but capsule perforation dynamics make it
  unusable for pump-characteristic calibration.
- pocketscience2024 candidate gap (radial inlet evenness): the 19-vs-16-spike RTD
  and velocity-field comparison is the same question in spirit (inlet distribution
  → flow uniformity) but unvalidated CFD on capsule injectors; complement in
  motivation only.
- No conflict with any registered component; nothing here contradicts held data.

## Implementation estimate
Nothing to implement. The porous closure is a lower-fidelity duplicate of
registered/carded K–C/Ergun components; the geometry-resolved CFD is
non-reproducible (proprietary CAD, commercial solver, admitted y+ violations) and
off-pipeline (capsule, not puck). The salvageable numbers (three operating points,
α_eff, thermal warm-up summary) are preserved in this card; no data/ transcription
or gate is justified.

VERDICT: skip — duplicates the registry's Ergun/Kozeny–Carman closure at lower fidelity on out-of-scope capsule geometry, with circular single-point validation and no published data; the one useful fact (nominal Ergun resistance underpredicts effective bed resistance ~53×) is captured here as a corroborating anecdote — effort S
