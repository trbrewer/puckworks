# SCI-H1-PANNUSCH-EQUILIBRIUM-LIMIT-001 protocol and derivation

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. User-authorized continuation
of R-03, dated 2026-10-19. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
This is a derived limit of the frozen source equations, not a new closure.
Puckworks base 6f7e95fc5fe8aa7bc6fa0984e77d558cd3af7dbf; read-only EWP base
7c025527da7e07982428d4c78a3e79bfa29a76ac. Both refreshed and exact-task and
Pannusch/equilibrium issues/PRs searched before branch creation; no duplicate.
EWP #104 retains its separate shared-versus-species production-law question.

## Question and evidence privileges

Does removal of finite-rate exchange change normalized six-vial prediction error
for this common source parameterization, initial state, clocks and observer?
The new information is the analytical-limit observable and its matched contrast;
favorable finite rate would support retaining transfer in this frozen model,
favorable equilibrium would support simplification on this observable, and an
unresolved/blocked result would leave this contrast undecided. None selects a
production successor. Grinder-to-cup relevance is fraction allocation under a
specified grind and prescribed flow. No missing-inventory rescue is attempted:
linearity removes a common scale for this question only.

Primary conditions are PRED-C01/C02/C05/C06; physical runs R1/R2/R3 in each,
caffeine and trigonelline paired, source fraction IDs 1,2,3,5,7,10 in order.
144 scalar observations, 24 profiles, 12 physical shots, four conditions.
TDS and 5-CQA, other coffees/campaigns and ramps are excluded. Existing MASS,
chemistry, rheology, window, flow-authority and mapping results remain historical.
March is SOURCE_INTERNAL / CAMPAIGN_SEPARATED / TARGET_EXPOSED, never a protected
holdout. Angeloni is excluded. New choices use source/observer information and
synthetic numerics, never new target-dependent scores. No fits or target assays
enter either mechanistic state. Common source parameters were fitted under the
finite-rate model; this asymmetry limits any physical interpretation.

Reuse PANNUSCH-RAW-REPRO-001, the corrected EWP multimodel C1 contracts and freeze,
OBS-PANNUSCH-FRACTION-WINDOW-001, flow-history and input-mapping decisions. Inspect
only the named original-source hashes and retained primary records through
PUCKWORKS_EXTERNAL_DATA_ROOT or data_sources.json. No new corpus census.
Retained C1 paired shot/analyte reference errors may be joined after their exact
identity, support and matching observable are verified. They are enough for the
paired loss comparison; no empirical retraining or invented reference profiles.
If missing, report reference unavailable rather than substituting aggregate context.

## Frozen model, bases and clocks

Use solver.py and closures.py source constants and Table 2 helpers unchanged:
alpha_l=.17, Dbed=.058 m, L=.015 m, d1=24e-6 m, phi_v2=.4; grind 1.7 with
psi=.23, d2=330e-6 m, d32=1/(psi/d1+(1-psi)/d2).
alpha_s1=(1-alpha_l)*psi; alpha_s2=(1-alpha_l)*(1-psi).
Caffeine (A1,B1,A2,B2,K_ref,gamma,c_s0)=(.00792,.36,.0311,1.13,.81,-371,10.80);
trigonelline=(.00333,.06,.0206,.77,1.36,-431,4.19).
c_s0 mg/mL is numerically kg/m3 on the implemented solid bases. These are fitted
model parameters, not measured production inventories. Original source roles distinguish published-fit experiments 9,10,11,14,15
from the ten other fit-campaign conditions used for source-nonfit reconstruction.
March is source-designated prediction, campaign-separated and already exposed;
none of these roles is upgraded to independent evidence.
K(T)=K_ref*exp(gamma*(1/T_ref-1/T)) with T_ref=360.15 K from the helper.
Closure water density and viscosity are evaluated as implemented; the flow
conversion constant is a separate object.

For every shot use constant T=temperature_start_C+273.15 and
Q=flow_start_mL_s/1000/980 m3/s EXACTLY. This source arithmetic is the prescribed
mathematical throughput; the physical meaning of the label remains unresolved.
No measured-inlet, beverage-derivative, pressure mapping or flow-label*1e-6 claim.
Use t0=min(all supplied assayed boundaries), as in the historical solver; it is
not automatically physical shot onset. End at the latest assayed endpoint.
Retain source-rounded qualified intervals and unassayed gaps exactly. No shift,
front alignment or boundary adjustment. Source start is uniform equilibrium:
cl=K*c_s0, cs1=cs2=c_s0 in the entire bed; clean inlet is a face condition.

## Derivation

Write k1=6*h1/d1 and k2=6*h2/(phi_v2*d2). The implemented equations are

    alpha_l*cl_t + (Q/A)*cl_z = alpha_s1*k1*(K*cs1-cl)
                               + phi_v2*alpha_s2*k2*(K*cs2-cl)
    cs1_t = -k1*(K*cs1-cl)
    cs2_t = -k2*(K*cs2-cl)

Multiply solid equations by alpha_s1 and phi_v2*alpha_s2 and add. Exchange
cancels, giving conservation of alpha_l*cl+alpha_s1*cs1+phi_v2*alpha_s2*cs2.
For positive exchange tending to infinity, cs1=cs2=cl/K. Thus
S=alpha_s1+phi_v2*alpha_s2 and H=alpha_l+S/K, giving

    d(H*cl)/dt + (Q/A)*d(cl)/dz = 0.

At constant Q,T the characteristic speed is Q/(A*H). Uniform source-equilibrium
initial cl=K*c_s0 is displaced by the clean-inlet characteristic. At the outlet,
cl(t)=K*c_s0 for t0 <= t < tf=t0+A*L*H/Q, and zero thereafter (the point value
at tf has no effect on integrals). For [a,b] inside modeled support,

    cbar = K*c_s0 * max(0, min(b,tf)-max(a,t0))/(b-a).

This is the primary equilibrium predictor, including front-crossing intervals.
Initial inventory M0=A*L*(alpha_l*K+S)*c_s0=A*L*H*K*c_s0 includes liquid,
fine and coarse inventories. Q*K*c_s0*(tf-t0)=M0 exactly. No first-cell inventory
is removed. The inlet at z=0 and the positive interior initial field are distinct.

## Common observation and scaling

For a modeled fraction-average concentration cbar_j [kg/m3] and measured vial
liquid mass m_j [kg], conditional predicted solute is m_j/rho_common*cbar_j [kg].
Take rho_common=980 kg/m3 as a unit conversion convention, not a measured liquid
property. Its common factor cancels. Normalize over precisely six assayed vials.
Observed shares normalize retained derived assay masses over these same six.
Neither normalization represents a complete cup or exhausted inventory. Conserved
model delivery is Q*integral(cl dt); conditional vial quantity uses measured m_j
and is not the model inventory ledger.

Both finite-rate equations and initial state are homogeneous linear in c_s0.
For any lambda>0, state, outlet integrals and conditional quantities multiply by
lambda, while their normalized vector is unchanged. The same follows explicitly
from equilibrium amplitude; tf does not contain c_s0. A common density cancels
too. K, capacities, Q, t0 and windows remain. This is not proof that M0 is known,
and does not extend to EWP's inventory dependence (SCI-MD-008/009).
Zero/nonfinite/unresolved denominators are unavailable. Negative predictions are
not clipped and pseudocounts are prohibited. All tail fractions remain.

## Numerical plan fixed before new scores

Use the existing 002 cell-centered upwind FV mass generator (_System in
 temperature_history_fv.py), unmodified coefficients, capacities and initial
constructor. At constant forcing its exponential semigroup is autonomous; the
research adapter applies scipy expm_multiply between requested boundaries, with
a local outlet accumulator reset to zero for each interval. This is the same
constant-generator numerical backend, with no coefficient-freezing time error.
Gaps are propagated as full intervals. It is a new realization of the existing
law, not an exact historical nodal replay. Historical nodal profiles are reused
from the qualified observer bundle and compared without rerunning or changing it.

Use N=400,800,1600; nominal N1600. Repeat N1600 with every propagation split in
half to check temporal/roundoff sensitivity on the actual observables. Independent
physical-concentration Radau integration on a synthetic N40 fixture verifies
phase basis and outlet accounting; it does not certify continuum spatial accuracy.
Bound empirical work at 24*4=96 integrations, no adaptive grid tuning.
Synthetic verification: at most 16 extra integrations (nine finite-rate, three
finite-grid equilibrium references, one N40 finite-rate, one independent Radau,
two N40 inventory-scale replays) plus small algebraic tests. Full qualification
commands have a 30-minute wall cap each; no adaptive campaign extension.
Fast-transfer family uses caffeine, 90 C, source-label 2.0, common source state,
N=50,100,200 and rate multipliers 1,10,100 (verification only). Compare to the
analytical continuum and separately to the finite-grid equilibrium chain, whose
outlet is the Poisson survival sum; report both errors. Do not confuse either
limit. No arbitrary large-rate scientific predictor.

For each actual profile let e_j=2*abs(c1600_j-c800_j)+abs(c1600_j-c1600half_j)
+1e-11*c_s0. Require max norm contraction of 800->1600 versus 400->800 (ratio
<=.8 unless both changes <1e-10*c_s0); report observed ratio. These are empirical
engineering allowances, not rigorous PDE bounds. Propagate e through measured
m_j/rho. With q=sum(q_j), E=sum(e_qj), require q>E and q>64*eps*M0;
share allowance d_j=(e_qj+p_j*E)/(q-E), so RMSE error <=sqrt(mean(d_j**2)).
Require every profile RMSE allowance <=.001 and temporal share max <=1e-8;
positivity, complete support and mass ledger residual <=1e-9*M0. Analytical
allowance is 1e-12 per share. Numerical failure makes the affected full comparison
unqualified; no selective fractions/species/conditions. Numerical loss thresholds
are engineering resolution criteria, not practical performance margins.

## Loss, reductions and interpretation

Per profile loss=sqrt(mean((predicted_share-observed_share)**2)). Report analytes
separately. Combined: equal analytes within shot, equal shots within condition,
equal conditions. gain_finite=RMSE_eq-RMSE_finite; positive favors finite rate.
Add arm loss allowances for paired gain; average allowances by the same hierarchy.
Report both arms versus retained boundary-aware C1 errors, plus each absolute loss.
Residuals by all six positions, early allocation (positions 1+2), tail (5+6), and
cumulative-share RMSE diagnose shape; signed residual sum is zero by construction.

Reuse frozen predictions for baseline, all 12 leave-one-shot-out and all four
leave-one-condition-out reductions. Omit identical identities for both species
and arms and recompute balancing. These 17 cases are one finite sensitivity family;
report signs and numerical resolution, not population confidence or independence
of fraction/species observations. No practical improvement margin is established.
Prediction difference, observed error difference, numerical resolution, deletion
stability, practical value and physical mechanism are separate conclusions.
Source parameter fitting under finite rate limits claims to removing transfer
from this frozen parameterization. Neither favorable arm identifies real espresso
mechanism; unresolved difference is not equivalence. No absolute-bias gates from
MASS/5-CQA, new calibration, protected scoring, production adoption or successor.

## Pre-score bounded implementation correction

The first synthetic attempt completed one N50 grid-limit and one N50 finite-rate
calculation, then failed while constructing its JSON row (duplicate `cells`
keyword). No scientific setting or score changed. Retain its external failure
log; the replay adds exactly two charges, so the synthetic total cap is 18
(16 planned successful integrations plus two failed-at-reporting charges).
The pre-score reviewer also required binding private nonchemical input bytes and
verifying retained evidence hashes. The corrected freeze records the original
numerical freeze identity. The 96 unchanged nominal/accuracy calculations are
reused with unchanged numerical module and input hashes, not repeated for this
wrapper correction. This is a G0 correction within the same G1 analysis.
