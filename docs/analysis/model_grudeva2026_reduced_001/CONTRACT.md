# MODEL-GRUDEVA2026-REDUCED-001 contract

Frozen before coupled implementation, 2026-10-02. G2 / NUMERICAL_METHOD_CHANGE:
new standalone numerical component; no EWP production equation, dependency,
existing Grudeva/Cameron implementation or default changes. Issue #67;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No protected holdout or fitting.

## Source and availability preflight

Grudeva, Moroney & Foster, EJAM 37(2), 496–519 (2026), online 2025-05-27,
[DOI 10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X).
Article is CC-BY-4.0. Article mathematics and independently extracted figure
coordinates are the implementation/reference sources. The old permissioned
port and upstream implementation are not read, imported, wrapped or translated
as implementation sources. Existing registration, cards and permission metadata
are read. Regression execution of existing components is not implementation
provenance. This records actual equation-based development, not an assertion
about every implementer's historical exposure.

The public article PDF and figure images were retrieved. The public supplement
URL returned HTTP 403; an existing local supplement was located in the declared
publication collection. It is consulted only for mathematics/reference settings;
its text, code and tables are not redistributed. Article CC-BY, upstream written
permission (unchanged docs/permissions/grudeva2025.md), and supplement rights
remain separate. No private correspondence or workbook is published.

Scoped data check: MANIFEST and AVAILABLE_DATA_REGISTER, ESPRESSO_DATA_GUIDE,
local grudeva2025 family (parameter transcription, exp13 summary, provenance),
and publication PDF locations inspected. These existing datasets are not
Figures 3–5 numerical arrays. No chemistry corpus access or exhaustion claim.
A filename search also encountered old clock-task checkout names; their solver
contents were not inspected. Figure references are public comparison data,
never calibration or protected targets. Full-model spatial arrays, exact
D_eff/epsilon coefficient and authors' scoring grid must be qualified before
Figure 5 can pass; an error-curve digitization alone cannot pass it.

Task-selection gate: NEW_INFORMATION is an independent mathematical derivation,
new executable and spatial/temporal numerical verification. Positive results
qualify this standalone component; numerical failure blocks its qualification;
reference shortage limits only reference claims and keeps #67 incomplete.
GRINDER_TO_CUP_LINK is verified native fixed-flow wetting/extraction capacity,
without a common-scenario adapter. REPEATED_BLOCKER: not another attempt at the
absolute-chemistry/measurement bottleneck; this is the owner's explicit bounded
component task. LOWER_COST_ALTERNATIVE: preserve the old port and use it only
for unchanged-baseline execution; it cannot supply independent verification.

## Mathematics and compatibility

Pages 504–505, Eqs. 18–29: phi_T=phi_l+phi_b*varphi_lb,
Q_i=phi_T/(a_i*b_i)=phi_T/(3*phi_i), gamma=phi_l/phi_T,
beta=1/(3Q_f), delta=1/(3Q_b), a=gamma+beta. Fixed q=1 only.
All grain concentrations are per total grain volume, including internal pores;
external liquid concentrations are per external liquid volume. No Cameron
1/phi_s correction: its current C_S0=118 kg/m^3 is already grain-volume based.
Volume conversion alone establishes no population or scenario equivalence.

Pages 508–511, Eqs. 35–39, 60, 65–67: ahead of desaturation but behind
wetting, c_l=1, c_f=c_f_init, c_b=c_b0=c_b_init+varphi_lb. Behind desaturation,
c_f=c_l=C and a*C_t+C_z=G_b. Dry grains do not extract. The clocks differ:
t_wet(z)=z; t_desat(z)=s_d^{-1}(z). Eq. 69 initializes grain diffusion at
t_desat, not wetting. The loose sentence calling t_desat the first wetting time
on p.511 is not adopted.

Page 512, Eqs. 68–70: set u=r*(c_b-C). Then u_t=D*u_rr-r*C_t,
u(0)=u(1)=0. Expand r in sine modes 2*(-1)^(n+1)/(n*pi).
Writing u=sum 2*(-1)^(n+1)/(n*pi)*h_n*sin(n*pi*r) gives
h_n'=-lambda_n*h_n-C_t, lambda_n=n^2*pi^2*D, h_n(t0)=c_b0-C(t0).
At r=1, -D*c_b,r=2D*sum(h_n); hence G_b=2D/Q_b*sum(h_n).
Volume averaging gives B=C+sum 6/(n*pi)^2*h_n and B_t=-3Q_b*G_b.
Duhamel's formula uses exp[-lambda_n*(t-u)] inside the convolution.
This explicitly corrects the absolute/elapsed-time mismatch in printed Eq.71.
The forcing derivative is at fixed z, not along a liquid characteristic.

Page 512, Eq.74:

    s_d'= (1-C_front)/(gamma*(1-C_front)+beta*(c_f_init-C_front)).

The concentration ratio multiplies only beta. With c_f_init>1, C_front=1
has the explicit limit zero. A zero jump/zero denominator is degenerate and
must be rejected or handled by a separately proved limit, never a floor.
Supported domain: positive fractions summing to one, 0<=varphi_lb<1,
D>0, c_f_init>1 and c_b0>=1, aqueous 0<=C<=1, s_d<=s_w before exit.
Other valid inputs that lose the saturated layer return UNSUPPORTED_REGIME.
At s_d=1 use a localized event and continue the whole-bed transport problem.

Page 513, Eq.75: no-outflow concentration convention 0 before t=1, saturation
plateau 1 until desaturation exit, then C(1,t). First drip=1 is model-derived
under prescribed flow. Censored events are unavailable with reasons.

## Numerical design (verification required)

Conservative front-fitted finite volumes in xi=z/s_d while s_d<1, then fixed
physical cells. Grain states advect in xi at -xi*s_d'/s_d, representing memory
fixed in z. Liquid flux speed is 1-a*xi*s_d'. Both phase fluxes share faces;
new grains enter the moving right boundary at c_b0. Integrate with implicit BDF,
explicit sparse structure and root-localized front exit; first drip is an exact
segment boundary. At t=0 use the analytic limiting derivative, without a hidden
positive time offset. Convergence must cover spatial, temporal and grain modes
separately. No clipping or mass correction.

For stable modes use x_n=C+h_n, x_n'=-lambda_n*(x_n-C), weights
w_n=6/(n*pi)^2. Resolve N modes and represent the remaining positive tail by
one relaxation mode with exact remaining weight and rate equal to tail weight
/divided by sum_{n>N}(w_n/lambda_n). This preserves initial and equilibrium
inventory and the integrated tail relaxation; it regularizes the integrable
short-age flux singularity explicitly. Demonstrate tail refinement; never
claim a finite series has exact instantaneous flux at age zero.

Normalized inventory unit is phi_T*L*A*c_sat. Integrate gamma*C (external
liquid), beta*c_f (fines), delta*B (boulders) over physical bed depth, including
dry and saturated regions. Pore refill contributes delta*varphi_lb in wet
boulders exactly once; it is transferred from mobile solute, not added as a
source. Initial inventory=beta*c_f_init+delta*c_b_init. Cumulative discharge
is zero until first drip; thereafter integrate the exit concentration.

## Publication parameters (separate from nominal Table 2 case)

| Quantity | Figures 3–5 case | Authority |
|---|---:|---|
| phi_f, phi_b, phi_l, varphi_lb | .64, .16, .20, 0 | Eq.76, p.513 |
| q, D_sb | 1, 1 | Eqs.29,77 |
| Q_f, Q_b | .20/(3*.64), .20/(3*.16) | Eq.21 + Eq.76 |
| c_f_init, c_b_init | 1.388, 1.388 | explicit dimensionless Table 2, p.507 |
| epsilon figure identities | .010, .0075, .0050, .0025 | labels Figs.3–5 |

Table 1's 310/224=1.383928571... is inconsistent with 1.388 beyond ordinary
rounding at the displayed precision. Preserve both identities; use the explicit
dimensionless table for the named numerical reference, never tune to 6.4.
Nominal Q/D values must not be combined with Eq.76 fractions. Pressure typo and
nominal t_w/L/q inconsistencies are not fixed-flow calibration inputs.
The old issue epsilon list and prose lower-limit wording conflict with figure
labels. D_sf is absent at leading order; there is no epsilon or fine-D knob.

Dimensional reporting requires explicit L [m], A [m^2], Darcy q_app [m/s] and
c_sat [kg/m^3], with t_w=phi_T*L/q_app. Q_exit=A*q_app after first drip.
EY=100*M_solute/M_dry_coffee, TDS mass percent=100*M_solute/M_beverage.
Beverage mass is explicit or computed from an explicitly supplied density.
Missing/zero denominators return None and reasons. No invented geometry.

## Frozen budgets and gates

These are engineering verification limits, not experimental accuracy.

| Gate | Acceptance |
|---|---|
| Front analytic constant C | relative speed/arrival error <=1e-12 |
| Kernel independent analytic series | flux <=2e-4, average <=2e-5 absolute; selected positive ages; varying-boundary/time-shift/equilibrium tests |
| Phase transfer/global conservation | normalized residual <=1e-6, including varphi_lb>0 |
| Bounds | aqueous [-1e-8,1+1e-8], grain/inventory >=-1e-8; no upper cap on grain concentration |
| Spatial/time/modal refinement | each max outlet change <=1e-3 away from jumps and event change <=1e-3; report actual grids/tolerances |
| Figure 3 | max concentration error <=.015 away from jumps; front-location error <=.008; extraction uncertainty recorded separately |
| Figure 4 | max concentration error <=.015 away from jumps; event error <=.025; extraction uncertainty separate |
| Figure 5 | all four times/epsilons; qualified full profiles/grid/settings; mean squared spatial error (not RMSE); otherwise FIG5_REFERENCE_INCOMPLETE |
| Software | finite canonical serialization, packaging/rights/card/link checks, native isolation, unchanged old results, relevant regression and hosted checks |
| Review | one independent review of exact candidate head and actual numerical/source evidence |

Quick gates execute bounded checks against independent reference fixtures.
Expensive refinement/reference work is an explicit reproduction command outside
quick CI. Any proposed numerical contract amendment is recorded before claiming
acceptance. Missing source support never constitutes rejection of the physics.

## Numerical development record

The initial uniform front-fitted mesh passed conservation but the 512/1024-cell
outlet difference was .00284424 at t=6.53, outside the frozen .025 exclusion and
above the unchanged .001 budget. It is retained as a failed refinement attempt.
The front has an integrable spatial grain-age boundary layer. Ordinary debugging
therefore replaces the uniform xi mesh with explicit face spacing
xi=1-(1-u)^p (default p=2), conservative nonuniform face reconstruction and
volume-weighted inventory. This concentrates resolution near newly activated
grains without a time offset, mass clipping, changed equations, source parameter
or acceptance budget. Spatial and modal refinement must be repeated for this
numerical change. The uniform controls remain reproducible with p=1.
