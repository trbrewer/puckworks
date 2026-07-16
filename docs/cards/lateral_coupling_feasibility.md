# Feasibility card: physical lateral coupling (WP6 / G-lat, Paper-4 candidate)

**Status:** feasibility phase (card + minimal conservative model). **NOT** a Paper-4 build —
a full model proceeds only after the go/no-go review below passes.
**Stage(s):** flow (transverse pressure coupling between evolving-κ channels) · **Kind:** model

## Why this card exists

The N-tube κ(t) union (`harness.ntube_kappa_t_union`, ROADMAP G-lat) found that once each
streamtube carries an extraction-driven porosity clock, flow-controlled channeling can
concentrate into one effective channel — but that harness used a PROXY homogenizing
regularizer, not a physical transverse-Darcy term. This card asks: is a *physical*
lateral-coupling model well-defined, conservative, and DISTINGUISHABLE from the frozen uncoupled
share-proxy completion — and, separately, is any such difference experimentally resolvable —
enough to justify a Paper-4 implementation?

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

## 3. Pressure-equalization: the EXACT number Ξ (and the legacy nominal Λ)

The mid-node pressure gap has an exact closed form. With per-path axial conductance sums
A₁ = g1_top + g1_bot, A₂ = g2_top + g2_bot, define

    Ξ = G_lat · (1/A₁ + 1/A₂).

Then for **any** nonzero uncoupled gap,

    gap_remaining_fraction = gap / gap₀ = 1 / (1 + Ξ)   (derived analytically; verified numerically).

Ξ — not the axial-conductance ratio Λ — is the physically exact equalization control. Under the
5 % / 95 % gap-reduction cutoffs the pressure classes are exactly:

| class | condition |
|---|---|
| `pressure_gap_unchanged` | Ξ < 0.0526315789… (= 1/0.95 − 1) |
| `pressure_gap_transition` | 0.0526315789… ≤ Ξ < 19 |
| `pressure_gap_homogenized` | Ξ ≥ 19 |

**Λ = G_lat/g_axial_reference is retained only for continuity as a legacy nominal grouping.** Its
0.05 and 5 boundaries are **neither validated nor universal** and are NOT the pressure classifier
— do not describe 0.05–5 as a validated or universal transition band. k_lat/k_axial and
inter-path spacing w set G_lat (hence Ξ); both are presently unmeasured.

## 3a. Matched physical-vs-proxy discrimination (WP6.6, this step)

`puckworks/analysis/lateral_coupling_discrimination.py` compares, on six predeclared synthetic
cases, the PHYSICAL two-node network against a matched **frozen uncoupled share-proxy
completion** (`analysis.lateral_proxy.frozen_two_path_proxy`) — the exact ntube operator
`w ← (1−α)·w + α` on unit-mean relative flows under the uncoupled completion: it homogenizes flow
SHARES only, has NO pressure law, holds total flow at the uncoupled value (Q/Q0 = 1), and carries
one share through a path's whole depth. **This comparator is NOT the complete dynamic streamtube
model** — the result is distinguishability from *this frozen uncoupled completion*, not from every
possible use of the full model. Physical quantities a share proxy cannot produce (p1, p2, gap,
q_lat, distinct inlet-vs-outlet share, physical effective conductance) are reported as
**None / unavailable — never a fabricated 0**.

- **α and Λ/Ξ are INDEPENDENT parameters.** No α = f(Λ) mapping is invented. The outlet-share
  match is solved **exactly in continuous α**: `s_proxy(α) = (1−α)·s₀ + α/2`, so
  `α* = (s_physical − s₀)/(0.5 − s₀)` when s₀ ≠ 0.5. The 0.001 α grid is an **audit sweep only**;
  a "no share match" is NEVER reported merely because the exact α falls between grid points. Both
  `alpha_star_continuous` / `continuous_share_residual` and `alpha_star_grid` / `grid_share_residual`
  are reported.
- **s₀ = 0.5 (mirror structure):** for `isoresistive_mirror` (3,1,1,3) and `scaled_mirror` the
  uncoupled proxy share s₀ is exactly 0.5, so `s_proxy(α) = 0.5` for **every** α — the proxy share
  is α-invariant. Any coupled physical outlet share ≠ 0.5 (e.g. 0.45 at Ξ = 0.1875) is therefore
  unreachable by the proxy at any α. That structural fact — not a grid artifact — is why the
  mirror is a strong share-discrimination case.
- **Joint test:** a case is `mathematically_distinguishable` only when **no continuous α**
  reproduces BOTH the outlet share and Q/Q0. Because the frozen completion holds Q/Q0 = 1, any
  case whose coupling raises total flow is distinguished on the flow signature even where its
  share alone is α-matchable (e.g. `top_contrast_only`). `identical_paths` (3,1,3,1) is the
  negative control: p1 = p2, q_lat = 0, `pressure_gap_class = not_applicable`, NOT distinguishable.
- **Three distinct notions, never conflated:** (i) *representational non-equivalence* — the proxy
  structurally has no pressure law (always true); (ii) *mathematical distinguishability* — the
  joint-match test above; (iii) *practical experimental resolvability* — **OPEN**, requires an
  instrument/noise model not supplied here and never inferred from a nonzero synthetic difference.
- **Regenerate (deterministic, no timestamps):**
  `python -m puckworks.analysis.lateral_coupling_discrimination --write` / `--verify`. Outputs:
  `docs/analysis/generated/lateral_coupling_discrimination.{json,csv,md}` (generated — do not
  hand-edit; `--verify` is wired into the generated-artifacts CI).

## 4. Go / no-go criteria (WP6.6) — all must hold to start Paper 4

- [x] complete physical-operator card (this file)
- [x] conservation + both limiting cases demonstrated with executable tests
- [x] a meaningful nondimensional transition (the exact Ξ pressure-equalization group) exists
- [x] **The minimal physical network is mathematically distinguishable from the frozen uncoupled
      share-proxy completion on predeclared synthetic cases.** ≥1 nontrivial case
      (isoresistive_mirror) is not reproducible by any continuous α, survives path-swap and ×10
      scaling, and is not a sign / conservation / boundary-condition artifact (residuals ~0,
      canonical sign asserted). This is **representational / mathematical** distinguishability of
      the MODELS — it does NOT show Ξ/Λ is measurable, that any effect is experimentally
      resolvable, or that espresso sits in any regime.
- [ ] at least one accessible experiment/dataset can estimate Ξ (needs k_lat and w — **OPEN**)
- [ ] the inference is not structurally non-identifiable (**OPEN**)

**Current verdict:** the operator is well-posed and conservative with the right limits, an exact
Ξ pressure-equalization group, and — now — demonstrated *mathematical* distinguishability from the
**frozen uncoupled share-proxy completion** on synthetic cases. The two remaining boxes are the
blocking unknowns: whether Ξ is measurable (k_lat, w) and whether the inference is identifiable.
Both stay OPEN. Paper 4 is **NOT** authorized: no N-path network, no PDE, no extraction clocks, no
experimental fitting, no transverse-permeability estimate, no α→Λ mapping, no registry promotion
follows from this step.

## Overlaps

Complements `brewer2026.streamtube` (Rung-B) and the N-tube union harness (the proxy this must
be distinguished from); does not compete with any registered runtime component.
