# MODEL-PANNUSCH2024-FLOW-CONSISTENT-OBSERVATION-001

G2 / NUMERICAL_METHOD_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Per-call accuracy NOT_ASSESSED.

## Construction and exact identities

Consume a checked current-source StatefulFVResult without changing it. On each
original interval [a,b], h=b-a, V=integral(Q,a,b), theta(t)=h*integral(Q,a,t)/V.
Use its stored midpoint T,Q and unchanged augmented mass generator A, exact stored
phase masses, and zero only the outlet accumulator. The capacities are
A_cs*(L/N)*[alpha_l, psi*(1-alpha_l), phi_v2*(1-psi)*(1-alpha_l)].
The generator has paired nonnegative off-diagonal transfers, zero column sums,
and a zero outlet column. Therefore its exponential is positive and conservative
in exact arithmetic and resetting that accumulator cannot feed back into chemistry.
Because affine Q is split at all Q/T knots, V=h*Q_mid and theta(b)=h. Primary
endpoint propagation and whole-step delivery are unchanged. The outlet derivative
inside the owning interval is (h*Q_mid/V)*Q(t)*c_liquid,last_tilde(t).
At jumps use the existing interval ownership and one-sided derivative.

This scales the ENTIRE frozen generator, including phase exchange. It is a
numerical continuous extension, not exact physical-time chemistry or a new
physical dependence of kinetic rates. With Q(a+s)=q_a+beta*s,
theta(a+s)-s=beta*s*(s-h)/(2*Q_mid), bounded by abs(beta)*h^2/(8*Q_mid).
For smooth forcing on a fixed spatial mesh this clock perturbation vanishes
quadratically with h; it is neither a mesh-uniform stiff error bound nor proof
of phase accuracy or any qualification gate. Independent physical-time balances
test every phase. Exact constant-Q intervals retain the physical-time path,
including variable T. No zero/reverse-flow extension or fallback is permitted.

Subwindows evolve from their reconstructed left phase state with zero outlet
accumulator for h*integral(Q,l,r)/V. No subtraction of cumulative masses or
clocks. Split only on existing primary boundaries; use stored whole-step masses
and compensated sums of mass and actual volume. Never repair discrepancies.
Exact endpoints and current checkpoints retain their original identity.

## Frozen controls and acceptance

CASES.json preserves 004's exact initial polynomials, S/L histories, species,
86 observations, 17 fractions, normalizations, primary endpoints, .04/.02/.01
levels, .02 default, N800 comparison, checkpoint index 137 and branch schedule.
The first 28 cases are new current-source executions; candidate observers attach
to stateful executions. The 29th is ONE Radau control (rtol=2.5e-13,
scaled_atol=2.5e-15,max_step=.01), compared to original settings
(2e-12,2e-14,.02). No adaptive tightening. Reserve seven correction slots.
Reference concentrations use the independently assembled concentration balances
and physical-time histories in tools/pannusch_flow_temp_fv_reference.py. Record
phase/endpoint samples plus actual-Q flux quadrature, with bounded sampling.
No candidate clock, generator or initialization supplies reference truth.

Reference-resolution rule: every reference channel/control difference must be
<=1e-8 on its original scale AND <=1% of the applicable absolute allowance.
For temporal aggregate ordering, intervals E_h +/- 2*max_control_difference
must strictly separate for resolved errors above 1e-10; otherwise UNRESOLVED.
Two-run differences are resolution controls, not rigorous error certificates.

Floating controls (not exact identities): abs(h*Q-V)/V <=64 epsilon;
clock endpoint relative residual <=64 epsilon; local semigroup/composition mass
residual <=512 epsilon times interval inventory (zero scale requires exact zero).
Record signed residuals without modifying Q,T,A,volume or endpoints. Reject
positive increments lost to underflow/rounding. The actual-Q GL8/direct and
GL8/GL4 local mass criterion is max(2e-11*C_star*V_window,
512 epsilon*abs(M_window)); report absolute kg and concentration/C_star too.
This is a stringent local diagnostic, over seven orders below the known frozen
weighting defect; it cannot be hidden by historical root inventory. Retain the
original 1e-6*M_star full flux/quadrature gate and frozen-Q diagnostics separately.

All original applicable A-F gates remain mandatory: A source-equilibrium/legacy
1e-12 for four species; B U/S independent reference 1e-8 for four species;
C/D genuine prefix/resume and recombination 1e-12 on root/local scales;
D physical-time U/L reference/default-finer <=5e-4 and resolved decreasing
aggregate above 1e-10; D N400/N800 <=.005 with conservative pair averaging and
capacity-weighted fields; E branch reference 1e-8; F repeat numerical arrays.
Independent initial/interval/local/root inventory <=1e-8; signed nonnegativity
>=-1e-10 on fixed scales; analytic volumes <=1e-12. Include every fraction and
phase, both common observations and original endpoint comparison support.
New interior admissibility and actual-Q flux require new execution, not 004 checks.
Analytical and regression tests A-F in the owner brief precede the campaign,
using only N<=12. No full-bed work in ordinary CI.

## Reuse, authority and resources

PW main b9ad38c6ebfe96d90462254dfb664dd789036b31/tree
9f1f93cf0147784055e9e9d2110b66b9e5ed2074 and EWP main
16eec1dda24ebf658965eddcf1a6fffa81903b32 match live intake. No drift.
One isolated feature branch; no dependency on #321. #324 is complete.
The old 004 diagnostic is reused with original producer
d691b055e8900f6547d4a5d4e5ec9f58f093bc8c: frozen/actual weighting explains
approximately 99.81%,99.98%,99.99% of signed controlling-window discrepancies.
Historical 004 remains failed. Its constructor equivalence proof does not
migrate checkpoints or authenticate current results. No historical checkpoint
will be loaded into the current API. Original evidence is only eligible after
receipt, input, source, plan, array and checked-support bindings are verified.
All necessary candidate/reference trajectories here are explicitly new.

Inspected: repository equations, geometry, parameter tables, card, code and
provenance records for pannusch2024/table2_params, experimental_kinetics and
Pannusch Mendeley. Reused: 004's scoped MATLAB/source inspection lineage and
numerical diagnostic. No original experiment/workbook value access or acquisition.
Pannusch et al. DOI 10.1016/j.jfoodeng.2023.111887; source repository
10.17632/y2tz67f6ry.1; Schmieder shared lineage. Source-derived artifacts retain
CC-BY-NC-3.0 separately from first-party code licensing.

Reuse the Git-common-directory reservation pattern with this task identity,
one bound external evidence directory, one worker and one BLAS thread. At most
36 execution slots, 3600 aggregate charged numerical seconds, 120 seconds per
invocation, 2 GiB per process, existing allocation/action limits. Failed launches,
corrections and standalone observer replays count; attached observation time is
charged. Auxiliary verification/reduction is charged. Reserve before launch;
no automatic retries or extension. Exhaustion means incomplete, no successor.

Ordinary software QA, hosted checks and ONE independent exact-head review are
separate dispositions. No historical CI exception. No merge/adoption, EWP/lock or
Guided Pull change, source fitting/scoring, envelope extension or successor.
VERIFIED_ON_DECLARED_CASES requires all mandatory numerical checks; otherwise
IMPLEMENTED_QUALIFICATION_INCOMPLETE or precise failure. Physical accuracy,
measured state, hydraulic prediction, source sensor equivalence and taste remain
unestablished. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
