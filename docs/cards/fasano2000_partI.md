# Model card: Fasano 2000 Part I — fines migration with compact-layer free boundary

**Paper/thesis:** Fasano A., Talamucci F., Petracco M., "The Espresso Coffee Problem," ch. 8 in A. Fasano (ed.), *Complex Flows in Industrial Processes*, Springer Science+Business Media New York, pp. 241–280 (2000). DOI not printed in the scan. Underlying analysis in their refs [16], [20], [22] (Fasano & Primicerio; Fasano & Talamucci).
**Stage(s):** bed_dynamics, flow · **Kind:** runtime
**Status:** Fasano-structured implementation with project-chosen closures; faithful source port and physical validation not established.

## Scope and mechanism
1D saturated cold-water percolation through a rigid coffee cake containing a single species of fine particles. Fines bound to the matrix (concentration b) detach when b exceeds a flow-dependent threshold β(q), advect with the flow (concentration m), and repack against the outlet paper filter as a growing low-conductivity compact layer whose top is a free boundary x = s(t). The model was built to explain two illycaffè observations that contradict plain Darcy p = Rq (their Eq. 8.1, Fig. 8.1): (1) exponential decay of discharge at constant injection pressure, and (2) nonmonotone dependence of the *asymptotic* discharge on injection pressure. Dissolution deliberately excluded (cold-water experiments isolate the mechanical effect). Initial dry-bed wetting explicitly out of scope (the authors point to the imbibition literature and suggest chaining initial conditions — i.e., a foster2025-style stage upstream).

## Governing equations
Nondimensional system, their (8.15)–(8.22) with flux closure (8.25); bars dropped as in the source. Scalings: x by bed depth L, b and m by b₀, t by 1/(γq₀), q by q₀ = K₀p₀/L, p by p₀; μ = αL/(εγ).

1. Mobile-fines mass balance (8.15): ∂m/∂t + μ q(t) ∂m/∂x = −∂b/∂t, on 0 < x < s(t). Valid in conservation form because b₀ is assumed constant (their assumption (c)), giving ∂(m+b)/∂t + μq ∂(m+b)/∂x = 0 (8.23).
2. Release kinetics (8.16): ∂b/∂t = −q(t)[b − β(q)]⁺, with β continuously differentiable, β′(q) ≤ 0 (8.14), and β(1) < 1 (8.35) to exclude the trivial no-release solution.
3. Darcy, active zone (8.17): q = −K(b,m) ∂p/∂x, 0 < x < s(t).
4. Darcy, compact layer (8.18): q = −K_c ∂p/∂x, s(t) < x < 1, with K_c ≪ K(b,m).
5. Free-boundary growth (8.19): (M − (m(s⁻,t) + b(s⁻,t))) ṡ(t) = μ q(t) m(s⁻,t); M = fines concentration at maximum packing (given constant, M > b₀ + m₀).
6. Interface conditions (8.20): [[−K ∂p/∂x]] = 0, [[p]] = 0 at x = s(t) (exact jump condition would be [[q − εṡ]] = 0; ε|ṡ|/q taken small).
7. IC/BC (8.21–8.22): b(x,0) = 1, m(x,0) = m₀, s(0) = 1; p(0,t) = 1, p(1,t) = 0, m(0,t) = 0.
8. Flux closure (8.25): q(t) = ( ∫₀^{s(t)} R(b,m) dx + R_c(1 − s(t)) )⁻¹, with resistivity R = 1/K, 0 < R_m ≤ R ≤ R_M < R_c (8.26).

Symbols: m, b = mobile/bound fines concentration (mass per unit total volume, scaled); q = volumetric flux; p = pressure; s(t) = compact-layer top; β(q) = removal threshold; γ = release-rate coefficient; α ∈ (0,1] = particle slowing factor (V_m = αV, 8.4); ε = porosity (constant here); K, K_c = hydraulic conductivities; M = packing concentration.

Analytic structure worth encoding as gates: a priori bounds (Lemma 8.1) s(t) ≥ s_m = 1 − (1+m₀)/M and q_m ≤ q ≤ q_M; global mass balance ∫₀^s (m+b) dx + M(1−s) = 1 + m₀ (8.33); with R = R(m+b) satisfying (8.42), q(t) is strictly monotone while mobile particles reach the front and frozen otherwise (Lemma 8.3; the lemma is titled "nonincreasing flux" and the bracket in (8.45) is negative under (8.42) — the sign printed in (8.43) of the scan appears to be an OCR flip); asymptotic limits s∞, b∞, q∞ (Lemma 8.2, Eqs. 8.39–8.40, 8.56); q̃∞ strictly increasing in p̃₀ whenever b − β(q) > 0 for all t (Prop. 8.1), so nonmonotone q∞(p₀) *requires* b − β(q) to vanish in finite time (Cor. 8.2). Well-posedness for general R(m,b): Theorem 8.2. Numerical scheme sketched (retarded-argument method, §8.3.4).

**Interpretation limit (R-05/T06 correction):** this is the retained card's
qualified source interpretation; **original passage not independently rechecked**
for this correction. The necessary condition concerns evolving b − β(q), not
equality of a pressure at a sampled maximum, discharge at that maximum, or a
threshold's steepest-segment flow coordinate. The scaling q₀ = K₀p₀/L depends
on pressure, and the proposition distinguishes q̃∞ and p̃₀. Compatible
normalization of Figs. 8.6/8.7 with those variables has not been established
here. No peak–knee equality or static-figure theorem test follows. Lemma 8.3's
R=R(m+b) and (8.42) restrictions must accompany the temporal-sign argument.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| β(q) | decreasing, β(1)<1; two example shapes in Fig. 8.7 | scaled by b₀ | assumed (functional form only) |
| γ (release rate) | not provided | 1/m (dimensional, so γq is 1/s) | not provided |
| α (slowing factor) | 0 < α ≤ 1 | — | nominal |
| μ = αL/(εγ) | 0.5 in Fig. 8.6 simulations | — | nominal (simulation choice) |
| M (packing conc.) | not provided; constraint M > b₀ + m₀ | scaled by b₀ | not provided |
| K(b,m), K_c | not provided; K_c ≪ K, bounds (8.26) | — | assumed |
| m₀ | ≥ 0 | scaled by b₀ | assumed |
| p₀ (experiments) | 3, 5, 7 bar (Fig. 8.1); 9 bar / 95 °C typical operation | bar | measured (context) |
| dose, particle size | ~7 g illy pod; main body 100–200 μm | g, μm | measured (context) |

No parameter is quantitatively identified against data anywhere in the chapter.

## Calibration and validation offered by the source
Qualitative only. (1) Fig. 8.1: experimental discharge curves at 3/5/7 bar show the transient decay and the nonmonotone asymptote the model targets; the semi-empirical fit q = a + b·e^(−ct) (8.2) "approximates the experimental behavior" but a, b, c values are not reported. (2) Fig. 8.4: reversible-chamber test — after reaching steady state, pressure off/on resumes the same discharge (ordinary porous medium), but *inverting* the chamber replays the exponential decay. This is the authors' key indirect confirmation of fines counter-migration, and it is a genuinely discriminating experiment. (3) Fig. 8.6: numerical simulations (T. Suski, ICM Warsaw; μ = 0.5, thresholds β₁, β₂ of Fig. 8.7) reproduce nonmonotone q∞(p₀). No quantitative fit, no error metrics, no parameter identification. Do not upgrade: this is mechanism plausibility, not validation.

## Assumptions and validity range
- 1D axial flow; saturated from t = 0 (imbibition excluded — chain after an infiltration stage); incompressible liquid.
- Rigid matrix, constant porosity in the active zone (relaxed only in Parts II/III).
- Single fines species; b₀ spatially constant (needed for the conservation form and most qualitative results).
- Cold water: no dissolution, no viscosity/density change of the liquid — hot-shot use is extrapolation.
- Compact layer forms against a retaining paper filter (illy pod geometry); a naked screen with fines loss would break the mass balance (8.33).
- Darcy only; silent on inertial/Forchheimer effects, temperature, grind dependence of β and γ, matrix compaction (competing mechanism, Part II).
- Nonmonotone q∞(p₀) is only *possible* within the model (Cor. 8.2 gives a necessary condition; Fig. 8.6 an example); the model does not predict when it occurs without knowing β(q).

## Interface mapping
Inputs consumed: BedState (dose_kg, depth_m, porosity, k → K, kappa), GrindState.fines_fraction (→ b₀, M inventory), MachineState.P_of_t (→ p₀; constant in the analysis, time-dependent pressure enters naturally through 8.25).
Outputs produced: q(t) trace, s(t), time-dependent effective bed resistance → BedState.k(t) modifier and ShotResultState.traces.
Couplings: runtime bed_dynamics component sitting alongside (or inside) the flow stage; would modulate the permeability seen by extraction each step. Adapters needed: a bound/mobile fines inventory on BedState (not in contracts v0.1), and a closure K(b,m) tied to the registry's k/kappa — the paper leaves K unspecified.

## Extractable data
- Fig. 8.1: digitize peak and asymptotic discharge vs pressure (3/5/7 bar) → data/fasano2000_fig8_1.csv. Low fidelity (schematic redrawing of sensor data), but it is the only experimental nonmonotone q∞(p₀) evidence on file and a usable gate target.
- Fig. 8.4: retained direct/inverse discharge trace — the qualitative reversal signature. Its current gate reduces the experimental trace without simulating reversal.
- Fig. 8.6–8.7: retained source-model output and threshold inputs with stated μ and β shapes. They support descriptive finite-table checks, not a verification twin, independent espresso measurements or faithful source-model reproduction without the missing closures.
- No code or tabulated data published; a, b, c of (8.2) "deducible from the data" but never given.

## Overlaps and conflicts
- Direct hit on the open backlog item "mass-conserving 5-state mobile-fines transport": this is a mass-conserving **3-state** model (bound / mobile / compacted) with a free boundary — the natural starting skeleton.
- Complements brewer2026.streamtube Rung B (fines migration is currently hypothesis-generating there); the Fig. 8.4 reversal experiment is the cleanest discriminator for that hypothesis.
- Competes with the backlog kappa(t) = kappa₀·f(P, eps, E) compaction/swelling closure as the explanation for flow-decay/rising-flow residuals (Part II of this same paper supplies that competitor; cite both).
- Complements foster2025.infiltration: explicitly the saturated stage downstream of wetting; the authors themselves propose chaining initial conditions.
- cameron2020.extraction assumes fixed k over the shot; this model, if active, perturbs that assumption — a coupling to quarantine behind a gate, not force.

## Implementation estimate
**Historical proposal and current implementation.** The original proposal was
1D transport, release, free boundary and flux quadrature,
followed by closure identification from flow traces, source-curve reproduction
and a machine-precision mass-budget target. Those proposed targets were not
achieved by reading the figures; no fit or faithful source port is claimed.

The registered `fasano2000_partI.fines_migration` now implements that structure
with project-chosen R(u)=1+u, M=5, R_c=50 and μ=0.5, using a clamped linear
interpolator of digitized Fig. 8.7. Its existing free-boundary gate checks
mass balance **<1%**, the boundary bound, fixed-pressure temporal nonincrease
and a sampled pressure-response maximum in its finite-horizon approximation.
This is bounded numerical behavior, not machine-precision closure, qualification
for all parameter values, a fitted real-puck law or source-curve reproduction.

The separate `gate_fasano_cor82_nonmonotone` retains its historical ID but does
not verify Corollary 8.2. PASS describes Fig. 8.6 sampled maxima strictly inside
the represented pressure ranges, lower preceding discharges, final discharges
more than the inherited 0.005 coordinate screen below their maxima, and beta2's
lower peak pressure. It allows beta2's smaller tail rebound. Fig. 8.7 thresholds
are checked for nonincrease on every retained interval and a net drop; their
steepest-segment locations are reported separately without a cross-figure
relationship. The 0.005 screen is not an uncertainty, theorem, model-accuracy
or physical-admission threshold. The Fig. 8.4 gate is a third, trace-only check.

Current verdict: qualitative mechanism capacity and bounded numerical
verification with chosen closures; source reproduction and physical validation
remain unestablished. See the [correction note](../analysis/fasano_gate_correction.md).
