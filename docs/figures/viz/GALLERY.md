# docs/figures/viz/GALLERY.md — SEED / ACCEPTANCE TABLE (provisional)

> **STATUS: hand-authored seed, NOT generated.** This table is the acceptance
> target for the VizSpec registry: CC encodes these badges / evidence strengths /
> fidelity ceilings into `puckworks/viz/registry.py`, and the generated gallery
> (`python -m puckworks.viz gallery`) must reproduce them. Any divergence is a
> flag, not a silent edit. Badges from `public.schema.BADGES`; evidence strings
> from `public.schema.EVIDENCE_STRENGTHS` (ROADMAP §0 — labels ride along
> UNCHANGED). Delete this banner only when this file is machine-generated.

| id | class | badge | evidence strength | producer / source component(s) | fidelity ceiling (binding caption content) | outputs | used in |
|---|---|---|---|---|---|---|---|
| process_schematic | 1 | per-stage (see note 1) | reference | `puckworks.registry.components` (registry metadata) | Depicts REGISTRY STRUCTURE (stages, components, kinds), not physics. Each stage lens carries its own badge inline; the diagram asserts nothing about mechanism fidelity. | thumb.png + full PNG/SVG | ONBOARDING orientation; PV-08; PV-09 title card; Paper A/B Fig-1-style design figures |
| shot_metric_frame | 1 | OBSERVED | independent (within-rig) | `data.waszkiewicz_traces` / `data.de1_fixtureA` (visualizer corpus optional, see note 2) | Measured machine traces. Caveats rendered: fixture-A pressure-NODE identity is OPEN (§5.9); Waszkiewicz constants are rig/coffee/grind-specific; TDS fractions 5-s bins, first bin single replicate. | thumb.png + annotated frames + optional video | PV-01, PV-02, PV-19 scorecard; Paper B §3/§4 context panels |
| kappa_t_ladder_fig | 1 | RECONSTRUCTED | post-fit reconstruction | `harness.kappa_t_ladder` (existing Paper-B Fig 3, routed through VizSpec) | One rig, 15–95 s window. Φ(t) rung = "0 additional coefficients fitted to THIS trace" (m_d sigmoid is a same-rig 9-bar TDS calibration — soft circularity); flexible cubic = in-sample flexibility bound; swelling rung 5b = QUALITATIVE cross-rig sign check. Ladder shows "time variation is needed", NOT "a specific bed mechanism is proven". | thumb.png + PNG | Paper B §4 Fig 3; PV-02; PV-06 |
| identifiability_valley_fig | 1 | RECONSTRUCTED | post-fit reconstruction | `validation.slow.angeloni_bracket.identifiability_panel` (existing Paper-A Fig 2, routed through VizSpec) | SSE surface = a LOCAL-CURVATURE DIAGNOSTIC, not a likelihood; the coupling coefficient is NOT a correlation; matched-40 g endpoints; single-grind whole-cup fit — the valley shows NON-IDENTIFIABILITY, it does not localize a "true" rate. | thumb.png + PNG | Paper A §4 Fig 2; PV-03 |
| puck_flow_field | 2 | EXPLORATORY_SIMULATION | verification | `brewer2026.lb_reference` / `lb_taichi` fields | "Computed Stokes-regime flow in a VERIFICATION geometry" — never "the flow in your puck". Stokes only (no inertia; DE1 tamped Fo_F ≈0.86–5.7 says real shots sit at/past inertial onset, §5.2); geometry is Boolean-sphere pack, untamped-validated k only. | thumb.png + hi-res stills + video (gitignored) | PV-09 flow lens; Paper B visual companion / GFM candidate |
| grain_pack_3d | 2 | EXPLORATORY_SIMULATION | qualitative | `brewer2026.pack_generator` (+ `wadsworth2026.permeability` for colouring) | Boolean (overlapping) spheres — an idealization, not imaged coffee. FINES ARE NOT RESOLVED: render the columnar-heterogeneity FIELD and label it as a field, never as particles. Grain radius ≥10 voxels; σ closure calibrated on 3 points. Tamped regime = extrapolation for any permeability colouring. | thumb.png + 3D stills + turntable video (gitignored) | PV-09 grind/pack lens; PV-11; public explainers |
| wetting_front_sweep | 2 | RECONSTRUCTED | independent (parameter-free gate) | `foster2025.infiltration` (+ `foster2025.machine_mode` for P(t)) | Sharp BINARY front — the model says nothing about partial saturation behind the front (that is open gap G1; do not shade a saturation gradient). Fine grind (<300 µm) only; source declines the coarse case. Machine-mode reported times include fitted t_shift (post-fit) — label if shown. | thumb.png + frames + video (gitignored) | PV-01, PV-18 companion; PV-09 infiltration lens; Paper B §2 context |
| channeling_concentration | 2 | EXPLORATORY_SIMULATION | qualitative | `brewer2026.streamtube` + `harness.ntube_kappa_t_union` / `ntube_finite_time_gain` | Static σ(φ₁) is an EMPIRICAL closure (dial 1.1–1.5, LOO-interpolated, not externally validated). Dynamic N-tube collapse is ONE CONFIGURATION (gs 1.1, 9 bar, N=200) — "strong concentration in the tested config", NOT a proven instability (G-lat); the lateral term is a HOMOGENIZING PROXY, not physical coupling (card-blocked; PV-14 constraint). Flow-control-specific — no latch under pressure control; render both if both are shown. | thumb.png + animation (gitignored) | PV-14; Paper B §5 / Fig 5 companion; PV-09 bed-dynamics lens |
| fines_migration_mechanism *(proposed addition)* | 2 | EXPLORATORY_SIMULATION | qualitative | `fasano2000_partI.fines_migration` | MECHANISM ILLUSTRATION ONLY: fasano-STRUCTURED — closures are OURS (paper's K(b,m), M, γ unpublished), zero identified parameters, NO coffee fit. May show release→advection→compact-layer growth and the nonmonotone q∞(p₀) SHAPE; must NOT be rendered as measured fines transport or given real-espresso parameter labels. | thumb.png + animation (gitignored) | PV-09 fines lens (labelled); κ(t)-discrimination protocol explainer; Paper B mechanism figure |
| hidden_puck_movie | 1+2 | per-lens (see note 1) | per-lens (unchanged) | composition of the lenses above via `viz.process_movie` | PV-09 contract verbatim: PARALLEL LABELLED LENSES, NOT a mega-model. The shared shot clock synchronizes DISPLAY only — no cross-lens physical coupling is implied or computed. Every lens keeps its own badge + evidence label on screen for its full duration. | thumb.png + montage video (gitignored) | PV-09; SDCC / GFM / World of Coffee public venues; project trailer |

**Note 1 (composite badges):** `process_schematic` and `hidden_puck_movie` are
composites; the honest unit of labelling is the LENS, not the frame. The VizSpec
badge field for these two should be the strictest badge present (i.e. if any lens
is EXPLORATORY_SIMULATION, the composite's spec-level badge is
EXPLORATORY_SIMULATION), with per-lens badges rendered inline. If `spec.validate()`
can't express that cleanly, CC should flag rather than mint new vocabulary.

**Note 2 (visualizer corpus):** the `shot_metric_frame` may include
visualizer.coffee population overlays ONLY if the corpus is present locally AND the
Miha-correspondence gate (ROADMAP §5.8) has cleared for the intended use; those
overlays are badge OBSERVED but evidence `reference` (selection-biased population),
hydraulics only — never user TDS/EY/sensory.
