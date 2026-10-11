# MODEL-GRUDEVA2026-FULL-REFERENCE-010

G2 / NUMERICAL_METHOD_CHANGE; analysis only; related issue #67 remains open.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. This contract precedes coupled implementation.
The owner authorizes one synthetic finite-rate full-equation reference, not a
Figure 5 reconstruction, reduced-model comparison, parameter fit or adoption.
Production modules, defaults, locks and historical 001–009 evidence are immutable.
One isolated branch and draft PR; no merge, auto-merge, EWP write or successor.

## Source and separate identities

Equation source: `GRUDEVA-EJAM-2026-E23-E29`, Grudeva, Moroney & Foster,
“A multiscale model for espresso brewing: Asymptotic analysis and numerical
simulation”, EJAM 37(2), 496–519, DOI
[10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X).
The CC-BY-4.0 article is the mathematical authority. Actually read the retained
article mathematics, Eqs. 2–4, 9–11, 18–29 and surrounding definitions, and
retained supplement B (moving-front pillbox) and C opening (spherical geometry).
Exact consulted file hashes and access limits belong to SOURCE.json. No author
code is an implementation source. This scheme is independently derived here,
not described as the authors' discretization. Article attribution, existing
[written permission](../../permissions/grudeva2025.md), and private supplement
rights are distinct. No supplement, correspondence or private locator is published.

Synthetic case: `SYNTHETIC-GRUDEVA-FINITE-RATE-010-A`.
phi_f=.64, phi_b=.16, phi_l=phi_T=.20, varphi_lb=0; q=1;
s_w(t)=min(t,1); c_f_init=c_b_init=1.388; horizon=8.
Synthetic finite-rate selections: epsilon=.01, D_sb=1, D_sf=100, D_eff=.01,
a_f/a_b=.1, b_f=80/41, b_b=2/41. D_eff/epsilon=1 is a choice, not an
established publication coefficient. No alternate physical cases or epsilon sweep.

Published definitions: b_i*=3 phi_i/a_i*, b_typ*=(b_f*+b_b*)/2;
b_i=b_i*/b_typ*, D_si=D_si* t_w*/a_i*², Q_i=phi_T/(a_i*b_i*).
Algebraic checks: b_f*/b_b*=40, hence b_f+b_b=2 and the specified b_i;
Q_f=5/48, Q_b=5/12; 3 Q_i phi_i/phi_T=1; gamma=phi_l/phi_T=1.
Equal D_sf*=D_sb* gives D_sf/D_sb=(a_b*/a_f*)²=100, consistent.
Initial total soluble inventory is 4*1.388=5.552. Do not use 310/224.

## Published dynamics and deductions

On 0<z<s_w, gamma c_l,t + F_l,z = G_f+G_b,
F_l=q c_l-D_eff c_l,z. For both grain populations at fixed physical z,
c_i,t+(r² F_i),r/r²=0, F_i=-D_si c_i,r, F_i(0)=0,
F_i(1)=Q_i G_i. Surface transfer is signed:
G_i=(b_i/epsilon)*(min(c_i(1),1)-c_l). In dry material G_i=0.
The minimum is the source law, not state clipping. Grains may exceed one.
Newly wetted grains have uniform concentration 1.388; no desaturation clock.
Inlet c_l(0,t)=0. Before t=1, F_l(s_w)-s_w' c_l(s_w)=0;
after t=1, c_l,z(1)=0. Here q=s_w'=gamma=1, so both right boundaries
have zero gradient. At t=1 stop domain motion and start discharge without
resetting any concentration or stored inventory.

Multiplying the grain PDE by 3 r² and integrating gives mean_i,t=-3 Q_i G_i.
With w_i=phi_i/phi_T, w_i mean_i,t=-G_i: signed transfer cancels exactly.
Reynolds transport gives M_l'=int G dz + F_in-F_front+gamma s' c_front.
Wet grain inventory derivative is -int G dz+s' sum(w_i*c_i_init).
Dry inventory derivative is the negative of that admission term. Before drip
F_front=s' c_front and gamma=1, so total stored derivative is F_in.
After drip it is F_in-F_out. Thus
M_l+M_f+M_b+M_dry+J_out-J_in=M0, with each quantity in
phi_T L A c_sat units. J_in integrates signed F_in; a negative value is
inlet loss, not cup delivery. J_out=0 through t=1, then integrates F_out.
M_l=s*gamma*int C_l dxi, M_i=s*w_i*int mean_i dxi;
M_dry=(1-s)*5.552. Means use actual radial states, 3 int c_i r² dr.
Dry liquid is absent; beverage concentration unavailable before discharge.

## Independently chosen numerical method

Let xi=z/s. Conservative liquid amount obeys
(s gamma C_l),t + [(q-gamma xi s') C_l-D_eff C_l,xi/s],xi=s sum G_i.
Each radial grain state obeys
(s C_i),t + [-xi s' C_i],xi=s R_i(C_i,G_i).
The latter geometric transport preserves physical-position grain histories;
it is not physical grain advection. Right admission uses c_i_init, center flux
zero, and the same shared grain flux on both sides of each axial face.
Finite volumes on uniform xi cells; graded radial faces r_j=1-(1-j/N)^3
resolve the analytically expected short-age surface layer. Conservative shells use exact
shell volumes (r_right³-r_left³)/3; representative radii are shell midpoints.
The states are shell-volume averages; centered radial differences at those
representatives are a numerical approximation verified against continuum shell
averages. Interior radial flux is centered diffusion.
The surface value is eliminated with the half-shell diffusive resistance:
J=h*(c_last-c_surface)=Q*k*(min(c_surface,1)-C_l), k=b/epsilon,
h=D/(1-r_last). Select the saturated branch only if its resulting surface
value is >=1; otherwise solve the linear Robin branch. No clipping of J.
Liquid faces use centered advection and diffusion (grid Peclet verified);
zero inlet via the quadratic cell-average derivative (7*C0-C1)/(2*dz),
zero right gradient and quadratic outlet trace (7*C_last-C_prev)/6. Grain geometric
faces use a conservative second-order monotone linear upwind reconstruction.
Integrate amounts U=s*C as the BDF state, reconstructing concentrations U/s
only at t>0. Thus inventory plus signed integrals and linear dry admission is
a linear invariant of the time discretization (up to solver/roundoff error).
SciPy BDF, sparse finite-difference Jacobian structure; temporal tolerances and
maximum step are distinct recorded controls. Segment exactly at t=1.

At zero wetted volume there is no liquid state to observe. A declared startup
time tau regularizes the collapsing coordinate system, without changing s=t.
Let K=k_f+k_b=200. For t<=tau the leading liquid solution is
C_l(z,t)=K*(t*z-z²/2)/D_eff (instantaneous diffusion balance).
For grains use the independently assembled shell diffusion propagator with
constant outward flux Q_i*k_i and wetting age t-z. Its radial integral is
c_i_init-3 Q_i*k_i*(t-z). Eight-point Gauss integration admits all wetting cohorts in each axial cell;
it integrates that linear radial mean exactly. J_in=-K*t²/2, J_out=0. Therefore the leading
stored-balance residual is M_l=K*t³/(3 D_eff), with exact initial axial polynomial averages; no inventory correction is applied.
Neglected liquid terms are relative O(t/D_eff) and transfer feedback O(t²/D_eff).
Startup is an additional numerical error source: three tau levels are mandatory.
These formulas also provide requested observations below tau, labelled startup
approximation rather than integrated states. Wetting-side grains use exactly
the initial state; left/dry liquid remains absent. Continuation starts with these
states and signed integrals, not a concealed empty-state offset.

## Focused development controls before matrix freeze

A. Spherical Robin diffusion: independent continuum eigenfunctions solving
lambda*cot(lambda)=1-Bi, radial integrals, surface flux and early ages; reverse
and zero transfer; constant-flux saturated branch and transition consistency.
B. Liquid manufactured polynomial on fixed and moving domains, with zero inlet,
zero right derivative and negative nonzero inlet diffusive flux. Check flux
signs and spatial refinement against exact cell integrals, not another integrator.
C. Closed paired transfer with phase weights: unsaturated equal equilibrium,
and saturated liquid with grains above one; transfer cancellation independently
summed. D. Grain memory manufactured at fixed z, geometric constant preservation,
dry admission, startup and t=1 continuity. E. Analytic radial means, observation
support, boundary quadrature, non-invasive capture and safe archive round trip.
Failed controls and corrections stay in DEVELOPMENT.json, with fixture counts.
No full-case horizon-8 run before the freeze and independent pre-campaign review.

## Qualification policy (prospective; exact rows frozen after controls)

One shared fine anchor, two coarsenings each for time, axial, fines radial,
boulder radial and startup, two combined coarsenings and one identical repeat:
14 scientific rows. MATRIX.json fixes integers, controls, exact observations,
source/dependency hashes and all comparisons before execution. No search or
replacement of inconvenient rows. Correction of a demonstrated defect requires
an explicit revision record and affected reruns, preserving original evidence.

All coordinates are physical and independent of results. Include t=0, startup,
short ages, wetting one-sided states, t=1 and its neighbors, profiles through the
entire finite transition layer, full outlet interval, fixed-z grain histories,
radial profiles including center/surface, separate inventories and both fluxes.
No 009 publication masks. A requested dry liquid or pre-drip beverage is
structurally unavailable, with a reason; these are not required wet observations.
Missing required wet states fail. Report all requested/available/unavailable counts.
Native accepted-state extrema are additional to common-grid extrema.

| Requirement | Limit, support and purpose |
|---|---|
| Conservation | max absolute residual <=1e-6 on native + required times, normalized mass units; also residual/M0 separately. Independent actual-state quadrature plus independent flux integrals, not accumulator-only. |
| Aqueous states | [-1e-8,1+1e-8], all native and required wet values; engineering boundedness with roundoff allowance. |
| Grains/inventories | minimum >=-1e-8; no grain upper cap. |
| Liquid profiles/outlet | max required refinement change <=1e-3 in concentration ratio units. |
| Grain means/radial profiles/histories | max required change <=2.3e-4 in grain concentration ratio units, including short ages. |
| Cup integral | max required change <=5e-5 in normalized mass units. |
| Each phase and signed inlet integral | max required change <=5e-5 normalized mass; prevents apparently cancelling reservoir errors. |
| Independent inventory quadrature | difference <=1e-11*max(1,sum absolute contributions); exact FV-volume sum checked with separate numerical quadrature. |
| Independent boundary integration | Gauss 3 versus 5 points per accepted dense interval and evolved integrals each <=2e-7 absolute mass; both signs and t=1 split audited. |
| Archive interpolant evaluation | <=256 machine epsilon*max(1,max absolute participating terms); byte/state hashes exact, unrelated floating-point evaluations not bitwise. |
| Observation reconstruction | exact constant/linear/polynomial manufactured fixtures <=1e-11 scale-aware arithmetic error; spatial reconstruction differences included in refinement, no claim they are roundoff. |

These limits are owner's numerical engineering requirements, not assay precision,
publication reproduction allowances or empirical model adequacy. Every adjacent
coarse/medium and medium/fine change is reported; the required precision gate is
medium/fine for each isolated axis and the combined pair. Three-level decreasing
trend requires a resolvable decline above reference/temporal/evaluation floors;
otherwise report resolved stability or unestablished trend, not forced monotonicity.
Combined change and sum of isolated fine changes must each meet the output limit;
several individually passing axes cannot each consume the whole budget.
An optional uncertainty estimate assumes the observed asymptotic order persists;
never call a refinement difference or Richardson estimate a rigorous continuum bound.
Failed gates preserve values and worst-case coordinates; output-specific passes
cannot promote an incomplete full-reference qualification.

## Archive and execution

Use safe numeric NPY/NPZ (allow_pickle=False) and JSON, SHA256 file and array
identities, exclusive new directories and a serial execution lock. Retain complete
accepted times/amount states and explicit concentrations, xi and radial faces/centers, physical coordinates, startup
and t=1 metadata, numerical controls, BDF interpolation coefficients, observations,
actual inventories, signed fluxes/integrals, diagnostics and environment/source
identities. Complete start/end/failure accounting and raw logs stay external.
No paid compute, arbitrary task wall-time quota or altered OS limits. Check disk,
host/cgroup memory and concurrent activity before scientific execution.
Ordinary QA is separate; small solver fixtures in tests are counted honestly.
Final exact-candidate independent nonhuman review follows actual results.

Full success only if all mathematical, numerical and archive gates pass:
FULL_REFERENCE_NUMERICALLY_QUALIFIED_ON_DECLARED_SYNTHETIC_CASE.
Otherwise retain bounded partial evidence and exact unresolved requirements.
Preserve CORROBORATED_PUBLICATION_DISCREPANCY, FIG5_REFERENCE_INCOMPLETE,
and PHYSICAL_VALIDATION=NOT_ESTABLISHED; none is adjudicated by this task.
