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
- **Lateral law:** a PHYSICAL transverse Darcy exchange with G_lat = k_lat A_lat / (μ w) set
  by a transverse permeability k_lat and inter-path spacing w. This is explicitly NOT numerical
  diffusion, NOT ad-hoc state mixing, and NOT the proxy regularizer.
- **Canonical sign convention:** `q_lat_1to2 = G_lat·(p1 − p2)` — POSITIVE means physical flow
  FROM path 1 TO path 2. Node balances use this single convention (see the module docstring and
  `test_canonical_transverse_flux_sign`); the earlier `(p_j − p_i)` phrasing was direction-
  ambiguous and is superseded.
- **Conservation:** at each interior node, Σ(axial in) − Σ(axial out) + Σ(lateral) = 0
  (steady). Global: total inflow = total outflow. Reported per node as `node1_residual`,
  `node2_residual`, `global_residual` (all ~0 to machine precision — the 2×2 solve is analytic,
  hence platform-deterministic).
- **BCs:** Dirichlet pressure at inlet/outlet; no transverse flux at the lateral domain edges.
- **Nondimensional group (WP6.3):** Λ = G_lat / g_axial_reference (transverse vs axial
  conductance), where **g_axial_reference = mean of the two uncoupled end-to-end SERIES
  conductances** g_series(g_top,g_bot) = g_top·g_bot/(g_top+g_bot). For the mirror case
  (3,1,1,3) both series conductances are 0.75, so g_axial_reference = 0.75.

Implemented minimally in `puckworks/models/lateral_coupling.py` (Model 0 uncoupled, Model 1
two-path coupled), solved exactly as a steady linear network.

## 2. Limiting cases (executable — see tests/test_lateral_coupling.py)

- **Zero coupling (Λ→0):** Model 1 → Model 0 (paths independent). ✔
- **Strong coupling (Λ→∞):** mid-node pressures equalize (p_1 = p_2) — homogenization. ✔
- **Conservation:** total outflow = total inflow at every Λ (to machine precision). ✔
- **Positivity / admissibility:** the network matrix is symmetric diagonally-dominant → a
  unique physical solution.

## 3. Regime map (WP6.3) — PROVISIONAL pressure-equalization labels

| Λ = G_lat/g_axial_reference | label | pressure behaviour |
|---|---|---|
| < ~0.05 | uncoupled | mid-node pressure gap barely moves |
| ~0.05 – ~5 | **transitional** | lateral flux measurably redistributes mid-node pressure |
| > ~5 | homogenized | mid-node pressures approach equality |

**These 0.05 / 5 labels are PROVISIONAL pressure-equalization descriptors, NOT a proved
proxy-discrimination theorem.** Where the physical model actually diverges from the share proxy
is a SEPARATE question, answered per case by the discrimination harness (§3a) via the
`pressure_gap_class` and `mathematically_distinguishable` columns — the two boundaries do not
coincide for every case (e.g. the mirror case is already distinguishable at Λ = 0.01, well
below the nominal transitional band). The go/no-go question reduces to: **does the espresso puck
sit where physical ≠ proxy, and can any accessible experiment resolve it?** k_lat/k_axial and
inter-path spacing w set Λ; both are presently unmeasured — the decisive unknown.

## 3a. Matched physical-vs-proxy discrimination (WP6.6, this step)

`puckworks/analysis/lateral_coupling_discrimination.py` compares, on six predeclared synthetic
cases over a Λ grid, the PHYSICAL two-node network against a matched **frozen streamtube SHARE
proxy** (`analysis.lateral_proxy.frozen_two_path_proxy`). The proxy is the exact ntube operator
`w ← (1−α)·w + α` on unit-mean relative flows under an *uncoupled completion*: it homogenizes
flow SHARES only, has NO pressure law, retains total flow (Q/Q0 = 1), and carries one share
through a path's whole depth (inlet share = outlet share). Physical quantities a share proxy
cannot produce (p1, p2, mid-depth pressure gap, q_lat, distinct inlet-vs-outlet share, physical
effective conductance) are reported as **None / unavailable — never a fabricated 0**.

- **α and Λ are INDEPENDENT parameters.** No α = f(Λ) mapping is invented or fitted; for each
  physical Λ the harness searches the WHOLE α grid for any proxy that reproduces the observables.
  A case is `mathematically_distinguishable` only when NO α reproduces both the outlet share and
  Q/Q0 to tolerance.
- **Headline (synthetic):** the `isoresistive_mirror` case (3,1,1,3) has EQUAL uncoupled outlet
  shares (0.5/0.5) yet, once coupled, redistributes total flow and transfers share depthwise —
  e.g. at Λ = 0.5 (transitional band): Q/Q0 = 1.053, outlet_share_1 = 0.45 vs the proxy's fixed
  0.5, depthwise transfer = −0.10. The share-only proxy cannot produce ANY of these for the
  mirror, so no α matches — distinguishable. `identical_paths` (3,1,3,1) is the negative control:
  p1 = p2 and q_lat = 0 at every Λ, `pressure_gap_class = not_applicable`, and NOT
  distinguishable. `scaled_mirror` (×10) reproduces the mirror's pressures/shares with 10× flows
  (dimensional-scaling check); path-swap symmetry is asserted in the tests.
- **Distinguishing observables (synthetic effect sizes only):** total-flow ratio Q/Q0
  (equivalently the fixed-flow pressure-drop ratio), depthwise inlet-vs-outlet share transfer
  (identically 0 for the proxy), and outlet-share shift for conductance-asymmetric cases.
- **Regenerate (deterministic, no timestamps):**
  `python -m puckworks.analysis.lateral_coupling_discrimination --write` /
  `--verify`. Outputs: `docs/analysis/generated/lateral_coupling_discrimination.{json,csv,md}`
  (generated — do not hand-edit; the `--verify` mode is wired into the generated-artifacts CI).

## 4. Go / no-go criteria (WP6.6) — all must hold to start Paper 4

- [x] complete physical-operator card (this file)
- [x] conservation + both limiting cases demonstrated with executable tests
- [x] a meaningful nondimensional transition (Λ regime map) exists
- [x] physical vs proxy predictions shown **mathematically / synthetically DISTINGUISHABLE** on
      predeclared synthetic cases: ≥1 nontrivial case (isoresistive_mirror) is not reproducible
      by ANY α within the transitional interval, survives path-swap and ×10 scaling, and is not a
      sign / conservation / boundary-condition artifact (residuals ~0, canonical sign asserted).
      **This is synthetic distinguishability of the MODELS — it does NOT show Λ is measurable or
      that espresso sits in any regime.**
- [ ] at least one accessible experiment/dataset can estimate Λ (needs k_lat and w — **OPEN**)
- [ ] the inference is not structurally non-identifiable (**OPEN**)

**Current verdict:** the operator is well-posed and conservative with the right limits, a real
transition band, and — now — demonstrated *mathematical* distinguishability from the share proxy
on synthetic cases. The two remaining boxes are the blocking unknowns: whether Λ is measurable
(k_lat, w) and whether the inference is identifiable. Both stay OPEN. Paper 4 is **NOT**
authorized: no N-path network, no PDE, no extraction clocks, no experimental fitting, no
α→Λ mapping, no registry promotion follows from this step.

## Overlaps

Complements `brewer2026.streamtube` (Rung-B) and the N-tube union harness (the proxy this must
be distinguished from); does not compete with any registered runtime component.
