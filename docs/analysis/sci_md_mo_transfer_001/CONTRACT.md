# SCI-MD-MO-TRANSFER-001 — research contract

G1 source/calibration contract; NUMERICAL_METHOD_CHANGE in an analysis-only
reference. No registered equation, historical gate or production behavior changes.
Retrospective source-conditioned development; these data were historically exposed.
The implementation is not a reproduction of swelling, permeability or pressure.
Swelling is frozen, and all candidates share the same axial transport.

## Increment and decision

NEW_INFORMATION: matched PSD-blind release, PSD-informed two-rate release and
resolved spherical diffusion with conserved storage and grouped out-of-fit prediction.
The historical Fig-8 within-bars scale selection is not a transfer test.
POSITIVE: prioritize the representation earning the frozen gain rule.
NEGATIVE: reject only the qualified tested transfer formulation.
NULL: retain the adequate simpler candidate. BLOCKED: name the missing mapping,
retain the verified reference, and do not infer a kinetic winner.
GRINDER_TO_CUP: test predictive use of measured PSD before adding extraction states.
LOWER_COST: common Python bed, no native integrations. REPEATED_BLOCKER: no
new inventory measurement, cross-source join or laboratory programme is proposed.

## Extensive equations, before implementation

Use SI internally. A cell has geometric volume V, mobile capacity W=epsilon V,
and particle population volume V_i=(1-epsilon)V theta_i (whole particle envelope,
not skeletal volume or intraparticle-pore volume). s_ij is particle-shell solute
mass, l_j mobile dissolved mass, and d delivered solute. Initial inventory is
I=f_inventory*dose. Uniform initial particle concentration is I/sum(V_i).

Water: dW_j/dt=Q_in,j-Q_out,j. During dry filling the first nonfull cell receives
Q but has zero outflow; full upstream cells pass Q; downstream cells have zero
flow. Sum(W_j)+W_cup=Q*t. Only full cells extract in the finite-volume wetting
approximation: activation is delayed to the downstream cell face, converging
with axial refinement. Partly filled liquid receives upstream solute but has no
outflow or release; no dry cell supports fictitious advection. This is an
explicit discretization restriction, not a source-measured wetting trajectory.

Solute: ds_i/dt=-J_i; dl_j/dt=Q_in c_up-Q_out c_j+sum_i J_i;
dd/dt=Q_out,last*c_last. Thus sum(s)+sum(l)+d=I exactly in the differential
balance. Clean incoming water contains zero solute. During filling all extracted
solute remains in wet storage. Cup solute and cup liquid are zero before breakthrough.
No concentrations or states are clipped after integration.

S0: J=k V_s max(s/V_s-c_j/K,0), one PSD-blind reservoir.
S2: J_i=k_ref*(100e-6/R_i)^2 V_i max(s_i/V_i-c_j/K,0).
D2: shell volume fractions w_a=x_outer^3-x_inner^3, shell center at radial
midpoint. Interior flux from a to a+1 is
3 V_i D x_face^2/(R_i^2 dx)*(c_a-c_a+1), signed diffusion. Surface flux is
3 V_i D/(R_i^2*(1-x_last))*max(c_last-c_j/K,0). It is subtracted from the
last shell and added to liquid with identical magnitude. Center flux is zero.
All three impose extraction-only external exchange (source Eq16), equilibrium
liquid=K*particle. No other paper's fitted kinetic law or constants are imported.

One inventory scales all states and both observers. For a specified collection
fraction a, m_c=rho*a*W_cup; s_c=a*d; EY=100*s_c/(a*dose), strength=100*s_c/m_c.
The fraction, dose and density must be source-qualified, never optimized. The
kernel requires them explicitly. Evaluations at prescribed mass solve to the
corresponding time; no endpoint-clamped interpolation is permitted.

## Scientific gate

The source register distinguishes observed coordinates from eligible responses.
A source ambiguity blocks only its affected axis. Implementation/synthetic
verification may proceed. Real fitting/scoring require a resolved source contract,
predictor-only numerical qualification and one independent exact-freeze review.
The machine contract contains starts, bounds, objectives, folds and decision
arithmetic. No fitting entry point receives withheld response columns.
