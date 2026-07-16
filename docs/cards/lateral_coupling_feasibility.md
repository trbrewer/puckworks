# Feasibility card: physical lateral coupling (WP6 / G-lat, Paper-4 candidate)

**Status:** feasibility phase (card + minimal conservative model). **NOT** a Paper-4 build —
a full model proceeds only after the go/no-go review below passes.
**Stage(s):** flow (transverse pressure coupling between evolving-κ channels) · **Kind:** model

## Why this card exists

The N-tube κ(t) union (`harness.ntube_kappa_t_union`, ROADMAP G-lat) found that once each
streamtube carries an extraction-driven porosity clock, flow-controlled channeling can
concentrate into one effective channel — but that harness used a PROXY homogenizing
regularizer, not a physical transverse-Darcy term. This card asks: is a *physical*
lateral-coupling model well-defined, conservative, and DISTINGUISHABLE from the proxy over a
measurable regime — enough to justify a Paper-4 implementation?

## 1. Physical operator (WP6.1)

- **Geometry:** two (later N) parallel axial flow paths through the puck depth L, exchanging
  fluid transversely. Minimal realization: each path split into a top and bottom half-segment
  meeting at a mid-depth node.
- **State:** mid-node pressures p_i (one per path); boundary P_in (inlet), P_out = 0 (outlet).
- **Axial constitutive law:** Darcy, conductance g = k A / (μ L_seg) per half-segment.
- **Lateral law:** a PHYSICAL transverse Darcy exchange q_lat = G_lat (p_j − p_i), with
  G_lat = k_lat A_lat / (μ w) set by a transverse permeability k_lat and inter-path spacing w.
  This is explicitly NOT numerical diffusion, NOT ad-hoc state mixing, and NOT the proxy
  regularizer.
- **Conservation:** at each interior node, Σ(axial in) − Σ(axial out) + Σ(lateral) = 0
  (steady). Global: total inflow = total outflow.
- **BCs:** Dirichlet pressure at inlet/outlet; no transverse flux at the lateral domain edges.
- **Nondimensional group (WP6.3):** Λ = G_lat / g_axial (transverse vs axial conductance).

Implemented minimally in `puckworks/models/lateral_coupling.py` (Model 0 uncoupled, Model 1
two-path coupled), solved exactly as a steady linear network.

## 2. Limiting cases (executable — see tests/test_lateral_coupling.py)

- **Zero coupling (Λ→0):** Model 1 → Model 0 (paths independent). ✔
- **Strong coupling (Λ→∞):** mid-node pressures equalize (p_1 = p_2) — homogenization. ✔
- **Conservation:** total outflow = total inflow at every Λ (to machine precision). ✔
- **Positivity / admissibility:** the network matrix is symmetric diagonally-dominant → a
  unique physical solution.

## 3. Regime map (WP6.3)

| Λ = G_lat/g_axial | regime | behaviour |
|---|---|---|
| < ~0.05 | uncoupled | paths independent; the proxy and physical model AGREE (no discriminating power) |
| ~0.05 – ~5 | **transitional** | lateral flux measurably redistributes pressure; the ONLY regime where physical ≠ proxy is testable |
| > ~5 | homogenized | pressures equalize; physical and (a strong) proxy again agree |

The go/no-go question reduces to: **does the espresso puck sit in the transitional band, and
can any accessible experiment resolve it?** k_lat/k_axial and inter-path spacing w set Λ; both
are presently unmeasured — the decisive unknown.

## 4. Go / no-go criteria (WP6.6) — all must hold to start Paper 4

- [x] complete physical-operator card (this file)
- [x] conservation + both limiting cases demonstrated with executable tests
- [x] a meaningful nondimensional transition (Λ regime map) exists
- [ ] physical vs proxy predictions shown DISTINGUISHABLE on synthetic cases in the transition
      band (next feasibility step — a proxy-vs-physical comparison harness)
- [ ] at least one accessible experiment/dataset can estimate Λ (needs k_lat and w — OPEN)
- [ ] the inference is not structurally non-identifiable

**Current verdict:** the operator is well-posed and conservative with the right limits and a
real transition band — the feasibility phase is progressing. The blocking unknown is whether
Λ is measurable (k_lat, w) and whether physical ≠ proxy is experimentally resolvable. Do NOT
begin a full Paper-4 model until the last three boxes are checked.

## Overlaps

Complements `brewer2026.streamtube` (Rung-B) and the N-tube union harness (the proxy this must
be distinguished from); does not compete with any registered runtime component.
