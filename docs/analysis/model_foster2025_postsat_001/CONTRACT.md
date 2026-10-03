# MODEL-FOSTER2025-POSTSAT-001 contract — 2026-10-03

Issue #311. G2 / **GOVERNING_PHYSICS_CHANGE**: replace the implemented constant
post-saturation headspace with the published evolving headspace. No new
constitutive physics. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Scope, identities and preflight

Puckworks baseline 5745f615637dbfe95065b48339c3fe566fa58d66; EWP live main
73ec476ffe6ac626705ca949e28b32935ddf2992. Remote heads match the reviewed brief.
Open PRs, remote model/foster* refs, local branches and worktrees were checked:
no duplicate found. Existing owner checkouts are preserved; this task has one
isolated checkout/branch. EWP checkout, locks, tags and defaults are read-only.
Grudeva #310 and 001/002/003 evidence retain
LOCAL_REPAIR_COUPLED_QUALIFICATION_INCOMPLETE, Figure 3/4 failures, Figure 5
incompleteness and the unexecuted matched baseline; #67 is not reused.

Scoped data preflight: MANIFEST canonical IDs foster2025_2/params,
foster2025_2/fig15_flow, foster2025_2/fig12_14_curves; actual packaged files,
provenance/digitization notes, AVAILABLE_DATA_REGISTER and espresso-data guide
inspected. The mounted external collection contains the source PDF, read
locally (Eqs. 5, 7–10, 16, 18–29, 30–38). No new intake/digitization or PDF
redistribution. Figure 15 is equation-generated verification, already exposed;
Figure 12–14 fitted curves are verification, CT markers are post-fit,
same-campaign observations, not independent/holdout. Figure 8 -H is excluded.
I-045 correction and I-090 retirement stand; no data-exhaustion conclusion or
laboratory recommendation. No task reselection or broad research search.

Decision: the new information is the missing source transient, separate
hydraulic flows and independently accumulated water inventories. Passing earns
bounded equation-completion/verification; numerical failure blocks qualified
completion; source-reference failure stays separately visible; incomplete work
returns a diagnostic draft. This completes a water-balance component relevant
to future integration without authorizing coupling. No repeated missing-data
blocker is being rerun. No fitting, tuning, release, publication, merge,
auto-merge, branch deletion, EWP adoption, laboratory work or successor.

## Mathematical and compatibility contract

All quantities are SI. p_h=p_a H0 beta/(H0-H) is absolute pressure;
a=(p_m-p_a)/Q_m²; a Q_pump²+R_f Q_pump=p_m-p_h, admissible 0<=Q<=Q_m.
f=k/(mu s)[p_h-p_a+p_c+rho g(H+s)] is superficial velocity.
R_f has units Pa s/m³, without a numerical change.

Pre-ponding: H=0, Q_p=Q_pump(0), s=Q_p t/(A phi_T), Q_bed=Q_p,
Q_out=0. Ponding uses source Eqs. 24–25.
Post-ponding: ds/dt=f/phi_T, dH/dt=Q_pump/A-f, Q_bed=A f, Q_out=0.
At localized saturation retain actual H(t_s), fix s=L, then integrate
Eq. 29: dH/dt=Q_pump/A-f(H,L), Q_bed=Q_out=A f(H,L).
p_c remains in the saturated source convention. No outlet-pressure law.

Retain sol (two-state pre-saturation segment), s_p, t_p, t_s, Q_p, p; add a
post segment, explicit status/support/events and observations. t_s is null
when unreached. Analytical ponding may be known but event status says whether
it was reached. Failed solves cannot produce successful observations. Default
requested model horizon is 30 s; actual support never exceeds requested
support. No pre-start, dense-output extrapolation, terminal constant extension
or implicit horizon extension in ANY helper. Early horizons can succeed without
qualifying the tail; zero horizon is supported analytically. Event-at-horizon
uses the localized event only if reached, never empty-array indexing.

Clock: t_reported=t_model+t_shift, once. CSV t_s is reported seconds, not the
saturation event. flow_minimum retains ponding-to-saturation sampling (400
points); response-atlas recovery remains flow AT SATURATION divided by minimum.
Published/frozen analyses and figure artifacts are not regenerated.

Source Eq. 18 remains min(Q_p,A f), with fixed Q_p, including the pump-limited
pre-ponding branch. Reject nonfinite parameters, nonpositive dimensions,
mu/k/rho/g/p_a/Q_m, phi_T outside (0,1), p_m<=p_a, R_f<0, beta<1,
p_c<0, or absent/degenerate ordering (require 0<s_p<L and Q_p>0).
Require physical pump branch H<=H_stop=H0(1-beta p_a/p_m)<H0, root reality
AND 0<=Q<=Q_m. Internal invalid evaluations terminate explicitly, without
clipping H. Roundoff-only boundary checks use 64 machine eps, separately
from integration budgets.

Cap invariance for this supported domain: let B=A f. At B=Q_p with s growing,
dB/dt=B_H*(Q_pump-Q_p)/A+B_s*B/(A phi_T)<0, because B_H>0,
B_s<0, H>=0 and Q_pump(H)<=Q_p. After saturation the second term vanishes
and the first is nonpositive. H=0 is inward-pointing for s>=s_p and
H=H_stop is inward-pointing. Thus the source cap and staged balances agree;
report numerical maximum cap excess too. Other regimes are unsupported.

Water: V_pump and V_out start at zero and accumulate their own flows;
V_storage=A(H+phi_T s). Production uses analytical pre-ponding and 8-point
Gauss-Legendre quadrature on each accepted solver interval, plus partial
interval quadrature for queries, separately across ponding/saturation.
No volume is defined by subtracting another. Independent verification uses
separately coded source flows and adaptive QUADPACK quadrature on dense states,
split at both events, at boundaries and interior times. Also integrate
Q_pump-Q_bed independently on subintervals and compare A delta H.
At saturation continuous H, p_h, Q_pump, Q_bed and both volumes; Q_out has
the correct one-sided jump from zero to Q_bed. Water only, not solute/TDS/EY
or physically validated beverage mass.

## Frozen cases and numerical programme (before corrected scoring)

D: shipped dimensional FosterParams unchanged, including Q_m=317e-6/60.
F: separate rounded fixture case. Fix L=0.009975 m, A=0.002734 m²,
p_a=101325 Pa, mu=0.000315 Pa s, rho=965 kg/m³; set Q_m=A L/5.162,
H0=0.782 L, p_m=14.8038 p_a, R_f=0.0002 p_a/Q_m,
g=0.00093195 p_a/(rho L), p_c=0.0987 p_a,
k=0.0495 mu Q_m L/(A p_a), beta=1.226, phi_T=0.322,
t_shift=0.796 s. This preserves ALL stated fixture dimensionless groups and
scales as a distinct case; none is inferred from output CSV values.
Transforms: P_m=p_m/p_a; R=R_f Q_m/p_a; Hratio=H0/L;
G=rho g L/p_a; P_c=p_c/p_a; K=k A p_a/(mu Q_m L);
time scale=A L/Q_m, length scale=L. Report D/F discrepancies without mixing.

All D refinement levels reach model 30 s using LSODA and dense output:
coarse rtol=1e-7, atol_scale=1e-9, max_step=0.02 s;
fine rtol=1e-9, atol_scale=1e-11, max_step=0.005 s;
finer rtol=1e-11, atol_scale=1e-13, max_step=0.00125 s.
Absolute state tolerances=atol_scale*[L,H0]; post tolerance=atol_scale*H0.
F uses fine. Baseline uses its exact shipped settings/source through saturation.
Common grid: linspace(0,30,601), plus each candidate's ponding and saturation
event and +/-1e-7, +/-1e-4 s where supported. Report every continuous channel:
s/L,H/H0,p_h/p_m,Q_pump/Q_m,Q_bed/Q_m,V_pump/Vscale,V_out/Vscale,
V_storage/Vscale; Vscale=A(H0+phi_T L), Tscale=A L/Q_m.
Fine/finer max norm <=1e-6; baseline/new earlier-stage/event <=1e-6.
Coarse/fine is reported too. Q_out equality excludes ONLY the interval between
separately localized saturation events, with its width/count disclosed; report
both one-sided limits and event-time error separately. No sampling-convergence
claim. Algebraic roundoff is separate.

Independent post trajectory: separately coded source formulas, DOP853,
rtol=2e-12, atol=1e-14*H0, max_step=0.01 s, initialized from localized
finer H_s, integrate to 30; its own pump/outlet quadrature. Continuous-channel
max norms <=1e-6. Independent global balance <=1e-6, with quadrature error
estimates reported; QUADPACK epsabs=1e-14 m³, epsrel=2e-11, limit=200.
Independent equilibrium: bracket root on admissible [0,H_stop), source
F=Q_pump/A-f; evaluate analytic F' from the brief and require F'<0.
Two scalar oracle trajectories: exact equilibrium and +1e-5*H0 perturbation,
through one relaxation time -1/F'. Equilibrium drift/H0<=1e-9;
perturbation decay agrees with linear rate within 1e-3 relative.
30 s endpoint earns finite-horizon equilibrium only if BOTH
abs(H-H_eq)/H0 and abs(Q_pump-Q_bed)/Q_m <=1e-6.

Figure 15: ALL 0.8–10.0 reported timestamps required, including nonempty tail
to 10.0. Frozen masks: reference time <6.667 s is pre, >=6.667 is post
(the fixture README rounded source event); same masks for D and F.
Report candidate event and whether any row classification differs; do not
move masks. For Q_norm=Q_bed/Q_m and p_h_norm=p_h/p_m report counts,
time ranges, RMSE and max absolute error per pre/post/overall window,
separately D and F. Each pre/post channel RMSE<=0.01 and max<=0.02.
Retain existing stricter early-flow/minimum and Figure 12–14 gates/thresholds.
No failed comparison permits tuning parameters, time shift, masks or budgets.

## Execution, QA and review

Ceiling: 12 qualification trajectory executions / 600 aggregate numerical
seconds including failures and independent checks. Initial planned bundle:
1 exact baseline; 3 D levels; 1 F; 1 independent post; 2 equilibrium/rate = 8.
At least 3 slots remain reserved for final-source reruns after corrections.
Reuse trajectories across gates. Ordinary unit/regression QA is separately
logged and cannot be exploratory qualification. No inherited Grudeva budgets.
Simple external append-only execution log; deterministic results exclude
variable timing/host metadata. Bind source/config/observer/data hashes and
dependency versions. No raw arrays, full logs or private paths committed.

Test invalid/nonfinite inputs, pump root/range/domain, numerical failure,
finite JSON, clock/support boundaries, horizons/events and zero pre-drip outlet.
Exercise affected consumers; minimum/current dependency QA; offline regression,
static, packaging, rights/path and hosted CI. Reuse unchanged evidence exactly.
One independent exact-head review with actual results; label nonhuman review.
Separate completion, domain, conservation, accuracy, independent method,
equilibrium, compatibility, reference, QA, CI and review outcomes.
Exit nonzero for failed/incomplete numerical/reference qualification.
Return a diagnostic draft if incomplete; no merge or automatic successor.
