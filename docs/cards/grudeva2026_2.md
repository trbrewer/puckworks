# Model card: Grudeva EJAM fixed-flow reduced model

Grudeva, Moroney & Foster, “A multiscale model for espresso brewing: Asymptotic
analysis and numerical simulation,” EJAM 37(2), 496–519 (2026; online 27 May
2025), [DOI 10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X).
Article: CC-BY-4.0. Stage: extraction/infiltration; execution role: runtime.
**Status:** implemented — code verification; publication reproduction not qualified.
Task: MODEL-GRUDEVA2026-REDUCED-001 / #67.
Evidence ceiling: code verification / published numerical reference / capacity.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The controlling [source/math/verification contract](../analysis/model_grudeva2026_reduced_001/CONTRACT.md)
records derivations, parameters, numerical method, budgets and source limits.
It corrects this card's previous algebra, clock, provenance and adapter statements.
The permissioned `grudeva2025.reduced` already includes infiltration-coupled
extraction and remains unchanged. This component is an independent equation-based
implementation, not a port/wrapper or a newly introduced physical mechanism.

## Equations and supported scope

Eqs.21,29: phi_T=phi_l+phi_b*varphi_lb, Q_i=phi_T/(3*phi_i), q=1,
s_w=min(t,1). Let gamma=phi_l/phi_T, beta=1/(3Q_f).
Eq.67: (gamma+beta)*C_t+C_z=G_b in 0<z<s_d; C(0,t)=0.
Eq.74: s_d'=(1-C_front)/[gamma*(1-C_front)+beta*(c_f_init-C_front)].
The concentration ratio multiplies only the fines-capacity term.

Eqs.68–70 give lambda_n=n^2*pi^2*D_sb and
h_n(t)=(c_b0-C(t0))*exp[-lambda_n*(t-t0)]
- integral_{t0}^t C_t(u)*exp[-lambda_n*(t-u)]du,
G_b=(2D_sb/Q_b)*sum h_n; c_b0=c_b_init+varphi_lb.
Here t0=t_desat(z)=s_d^{-1}(z), distinct from t_wet(z)=z. Grain histories
are Eulerian. This derived time-invariant convolution corrects printed Eq.71;
it is not an unnoticed literal reproduction. Grain concentrations may exceed 1.

Eq.75 gives no outflow before t=1, concentration 1 until desaturation exit,
then C(1,t). First drip is model-derived under prescribed flow, not an independent
hydraulic prediction. A front failing s_d<=s_w is unsupported; no supplementary
unsaturated branch is silently selected. Whole-bed region-(i) evolution continues
after the desaturation front exits. No variable flow, pressure mode, Foster
coupling, common-scenario execution or cross-model overlay is provided.

## Parameters and reference qualification

Figures 3–5 use phi_f=.64, phi_b=.16, phi_l=.20, varphi_lb=0 (Eq.76),
q=1 and D_sb=1 (Eq.77); Q_f=.20/(3*.64), Q_b=.20/(3*.16).
Use dimensionless Table 2's c_f_init=c_b_init=1.388. Table 1's 310/224
is 1.383928571..., an explicitly recorded inconsistent alternative, not a
parameter to tune. Nominal Table 2 Q/D values do not belong to this case.
Pressure/timescale typos are not inputs. D_sf and epsilon are absent at leading
order. Figure labels are .010, .0075, .0050, .0025, unlike the old issue list
and the prose's lower-limit statement.

Figures 3/4 are public numerical-reference comparisons, not measurements.
Figure 5 is mean squared spatial full/reduced difference at four times; passing
requires qualified full-model profiles/settings and a declared grid. Its plotted
error curve alone cannot verify this implementation. No full-PDE solver is part
of this task. Source material does not establish experimental validation.

## Inventories, units and rights

Grain concentration is per grain volume including internal pores. External
liquid concentration is per its own liquid volume. Inventory sums phase-volume
weighted concentrations; intragranular liquid is counted only inside boulders.
Pore filling transfers existing solute. Current Cameron C_S0=118 kg/m^3 is
already grain-volume based; this card's obsolete 118/phi_s interpretation is
removed. Tested volume conversions do not establish matching populations,
inventories, saturation constants, flow or observation operators.

Dimensionless execution needs no geometry. Dimensional outputs require explicit
A,L,q_app,c_sat and t_w=phi_T*L/q_app. Darcy q_app is m/s; outlet volumetric
flow is A*q_app. EY requires dry coffee mass; mass-percent TDS requires explicit
beverage mass or a stated density approximation. Missing/zero scales or
denominators yield unavailable quantities with reasons.

Article equations/figure-derived fixtures retain CC-BY attribution. Existing
upstream written permission is recorded separately in
[the unchanged permission record](../permissions/grudeva2025.md) and notices;
it is not blanket permission for future material. Private supplement and
correspondence are not redistributed. Implementation provenance uses the
registry's existing `published_port` lineage with an explicit independent
reimplementation note; `published_reimplementation` is not a valid enum.

VERDICT: bounded standalone G2 implementation and verification authorized;
no physical-validation, superiority, production-adoption or successor claim.
