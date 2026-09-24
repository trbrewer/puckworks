# SCI-MD-MORONEY-TRANSFER-001 — pre-scoring protocol

Status: PREPARATION; no calibration, transfer prediction freeze or target scoring
has executed. Original Figure 11 object confirmation remains pending. The owner
has explicitly authorized this research solver and bounded comparison, subject
to independent pre-scoring review. This document and `protocol.json` together
are the contract; `freeze.json` binds their exact bytes and dependencies.

## Scope, authority and decision consequence

Puckworks: **G2 research numerical-method implementation**, **G1 data contract /
pre-scoring freeze**, then **G3 retrospective holdout scoring**. Scientific change:
NUMERICAL_METHOD_CHANGE in an analysis-only implementation of carded equations.
EWP: G1 scientific decision consumption, NO_GOVERNING_PHYSICS_CHANGE. No production
solver, default, interface, registry, status, lock, OpenFOAM or laboratory change.
Actual live bases and source hashes are in `identities.json`; unrelated open work
is not a prerequisite. Isolated worktrees preserve original checkouts.

NEW_INFORMATION: an untested same-source JK depth/dose transfer, with cumulative
pot delivery, explicit startup budgets and two mass-bounded transfer hypotheses.
POSITIVE: retain spatial storage as a candidate for separately authorized EWP
integration; do not transfer fitted constants. NEGATIVE: deprioritize the tested
combined transport/startup formulation. ADEQUATE WITHOUT GAIN: prefer empirical
parsimony. STARTUP/PARAMETER LIMITED: identify the consequential state/parameter,
without pretending it identifies wetting physics. CALIBRATION INADEQUATE: no
transfer inference. SOURCE/NUMERIC LIMITED: preserve qualified subsets and name
the actual issue. These are distinct choices, not automatic experiments.
GRINDER_TO_CUP_LINK: test whether spatial extraction/storage earns complexity.
REPEATED_BLOCKER: this is not another species-inventory or hydraulic-closure task.
LOWER_COST_ALTERNATIVE: the two empirical cumulative models are the comparators.

This is retrospective same-source model development. Target curves have been
publicly visible, including during figure qualification. Not blind validation,
independent replication, unique mechanism identification, population inference,
or espresso physical validation. EWP PHYSICAL_VALIDATION remains NOT_ESTABLISHED.
No automatic successor, merge, author contact or new measurement is authorized.

## Source and observation contract

FILES_INSPECTED: cards 2015/2016/2019; 2015 manifests, tables, selected Fig3/7/11
CSVs, existing batch/LDF solvers and gates; repository guide/register entries;
EWP state, claim ceiling, policies, programme and ledger. The configured private
inventory was queried for Moroney 2015 only. It holds the CSV family but no PDF.
Other external families are CATALOG_ONLY and outside scope. Public author text
of DOI 10.1016/j.ces.2015.06.003 was inspected; author/publisher PDF requests
returned HTTP 403/400. A local similarly named PDF proved to be Moroney 2017
and was rejected. Original page/object verification is still required.

`qualified_rows.csv` is a view over immutable source hashes with one-based data
row identities (comments/header excluded). Primary deep: Fig3 panels a/b only,
22 pot and 22 outlet points. Primary shallow: Fig11 panels a/b, 14 pot and 14
outlet candidate points. Four proposed legend exclusions are data rows 7, 33,
45, 71 (coordinates specified in owner request). These are pending until original
page 233 visual and coordinate evidence is recorded. Never exclude by residual.
Fig11's other 44 blue points are duplicates of deep Fig3. Fig7's model lines are
reproduction references and its observations duplicate Fig3. Cimbali, Fig8,
Fig12 duplicate curves and later papers are not additional folds. Tables retain
measured/derived/fitted/nominal roles despite the manifest word MEASURED: that
word denotes plotted-coordinate extraction, not experimental precision.

Accepted outlet concentrations remain in mg/g, beverage mass in g. Negative
near-zero readouts remain signed; there is no clipping or censoring. No point
bootstrap, fictitious replicate count or independent pot/outlet experiment.

Observer: S_out[g] = M[g] c_pot[mg/g]/1000. This is delivered solute, not total
extraction, remaining solid, retained liquid or inventory. Model pot is 1000 S/M;
undefined at M=0. Model outlet is 1000 C_h/rho. Source Table1 rho=965.3 kg/m³
is used consistently in concentration and M=1000 rho Q t, Q=250e-6/60 m³/s;
mass flow=4.02208333 g/s. Time zero is modeled **first outflow/post-fill**,
not pump-on/first-contact. No unknown delay or target-fitted shift is invented.
There is no line from zero to the first outlet observation. Pot points provide
the cumulative constraint directly at their own masses.

Fig3/Fig7 selected paired markers have a best zero-intercept conversion density
of 969.286 kg/m³ and maximum disagreement 0.5842 kg/m³ under Table1's 965.3.
This is an audit of duplicate plotted representations, not a new measured
density. The README's approximate 1.033 factor is not an exact Table1 identity.
Primary Fig3 native units are retained; rho is not fitted to shallow data.
Original axes must be confirmed and the discrepancy treated as source readout
sensitivity, not silently corrected. Source concentrations were refractometric
with evaporative calibration (1 Brix = 8.25 g/L); no replicate errors recovered.

Dose is as received with approximately 4% moisture; m_dry=0.96 dose, i.e.
57.6 and 12.0 g. Table1 phi_c0=.143435 is per dry grain envelope volume;
phi_dry=.56 and c_s=1400 give Ymax=.143435/.44=0.325988636 dry mass fraction
(31.2949% of as-received dose). Inventory is 18.77695 and 3.91186 g respectively
(rounding only here; executable computes exact values). It is a source-qualified
inventory constraint, not a shallow yield fit. 28–32% source discussion is not
substituted for a new inventory parameter.

## Equations and volume reconciliation

Carded Moroney-2015 Eqs57–61, source advection-dominated saturated reduction;
clean inlet, constant prescribed Q, no diffusion/dispersion, no new pressure
kinetics, filling, swelling, channeling or capillary law. Source pressure is used
only for the explicitly conditional hydraulic volume branch. Existing batch
solver supplies conservative exchange sign and grain/mobile volume factors.
Moroney-2019 LDF equations and zero-liquid initial states are not substituted.

In a cell: Vg=grain envelope volume; Vh=mobile volume; Mh,V,S are respectively
mobile, internal-pore dissolved and remaining surface-soluble masses [kg].
Inventory I=Ymax m_dry/N. Ch=Mh/Vh, phi_v=phi_d+(I-S)/(c_s Vg), Cv=V/(Vg phi_v).
All kernel solute has dissolved before model time zero; kernel solid is exactly
zero. With psi=S/(f I), fc=I/(c_s Vg):

```
E = Vg alpha phi_v^(4/3) D 6/(ksv2*l_l) (Cv-Ch)
R = Vg beta 12 D fc/(ksv1*m) (csat-Ch) psi
Mh' = Q(Ch_up-Ch) + E + R
V'  = -E
S'  = -R
S_out' = Q Ch_out
```

Upwind finite volumes telescope exactly, including outlet accumulation. This
also implements phi_v'=-S'/(c_s Vg), equivalent to source Eq60. D=2.2e-9,
ksv1=27.35e-6, ksv2=322.49e-6, l_l=282e-6, m=30e-6 SI. Nominal csat=212.4
was estimated from this source; it is not independent evidence. alpha/beta
are fitted transfer multipliers, not measured molecular diffusivities.

Reported 59 mm diameter and L=.0405/.0112 m give bed volumes 110.726/30.620 mL.
Copied phi_h=.2 plus the dose does not preserve dry phi=.56. Two distinctly
labelled conditional formulations resolve this instead of a hidden multiplier:

- **dose**: Vg=m_dry/[c_s(1-.56)], Vh=AL-Vg; phi_h=.15551/.36381.
  Q remains prescribed; no permeability-law test is claimed.
- **hydraulic**: infer phi_h=.20041/.21455 by KC with ksv1, kappa=3.1,
  mu=.315e-3 and Q/A=k(phi_h)(DeltaP/L+rho g)/mu. Then Vg=(1-phi_h)AL,
  phi_d=1-m_dry/(c_s Vg)=.53529/.64361 and fc=Ymax m_dry/(c_s Vg).
  These effective dry voids reconcile the dose and conditioned storage volumes;
  they are not measurements or validation of KC. Grain-volume fc differs from
  Table1 precisely because the volume basis changed; the total mass is unchanged.

Neither branch forces every copied source constant to agree. Their spread is
structural bookkeeping sensitivity, not a statistical confidence interval.

## Startup and calibration

Ten families: each volume basis with uniform amplitudes 0, .5, 1 times csat,
and linear amplitudes .5, 1 times csat. Linear profile is Ch(x)=amplitude csat x,
x=0 inlet, x=1 outlet (reversed source z). Cell means are exact. Same family and
amplitude apply to both conditions. These are fixed conditional amplitude
sensitivities, not shallow initial amplitudes fitted from the first observation.
Uniform zero and linear zero coincide and are counted once.

Initial mobile Mh=Vh Ch is deducted **locally** from fI surface inventory;
internal-pore mass is (1-f)I and deducted from the kernel allocation. Thus
Mh+V+S=I at t=0. Reject negative surface mass, oversaturation or invalid volumes;
no clipping or budget repair. All frozen parameter domains are admissible in
both conditions. This finite family does not exhaust wetting uncertainty.

Material parameters only: alpha [.01,2], beta [.001,.5], f [.65,.95]. Optimize
log alpha, log beta, f with two deterministic starts in protocol.json, maximum
60 function evaluations per start, scipy least_squares tolerances 1e-6,
diff_step=1e-3. Record every failure, termination, active bound, objective,
solver call and solver evaluation. No start expansion after target scoring.

Objective is mass-weighted outlet squared error / 5² plus .25² times weighted
pot-delivery EY squared error / 1². Each observable's trapezoidal weights sum
to one on its own observed support. Outlet is primary; pot is a dependent mass
constraint, not an independently weighted experiment. Training is deep Fig3 only.
Choose minimum successful objective per family from deep only; retain all
successful starts within 5% of minimum + .01 as admitted alternatives. Preserve
failed/boundary solutions even when not admitted. Unsuccessful optimization is
not an adequate calibration. No statistical parameter intervals are claimed.

Empirical cumulative model S=m_dry Y[1-a exp(-M/b1)-(1-a) exp(-M/b2)], with
Y in [0,Ymax], a in [0,1], b1 in [.5,500] g and positive width increment
b2-b1 in [.01,2000] g. Fit deep with the same objective, two starts and policy.
Outlet=1000 dS/dM; pot=1000 S/M. No intercept, independent pot correction or
shift. N_M scales both widths with dry dose; N_T scales widths with beverage
mass-flow ratio (one here), both scale inventory with dry dose. Report target
extrapolation in M/dose for N_M and elapsed outflow time for N_T.

## Numerical/source sensitivity and gates

Three primary meshes 480/960/1920; fit mesh 480. Primary prediction 1920, with
480/960 and tightened 1920 (rtol 1e-9, atol 1e-14 kg) retained. Default BDF
rtol=1e-7, atol=1e-12 kg with sparse Jacobian structure. Accepted numerical
roundoff down to 10 atol is recorded without clipping; larger negatives reject.
Mass residual <=1e-6 of initial inventory. State conservation, zero transfer,
zero dissolved inventory, exact finite-volume pure-advection chain and closed
well-mixed exchange have analytic tests. Representative controls are synthetic,
not fits to shallow concentrations. Refinement differences are empirical
sensitivities, not rigorous continuum bounds. Numerical variation allowances:
0.5 mg/g outlet RMSE and .1 dry-dose EY pp cumulative error on observed support.
Raw pointwise maxima are also reported, especially startup front smearing.

Source sensitivity consists of coherent whole-series axis scales, equal for all
candidates: central; M*.998 and c*.995-.75 mg/g; M*1.002 and c*1.005+.75 mg/g. Deep perturbations
are refitted before predictions freeze; shallow perturbations attach only during
scoring. These small readout probes are motivated by duplicate representation
mismatch/coordinate anchoring; they are not recovered experimental error bounds
and not independent point noise. They do not exhaust calibration uncertainty.
No relaxation after seeing target residuals.

## Review, prediction freeze, scoring and disposition

An independent reviewer must accept the exact freeze, equations, source-object
classification, comparison support and the following engineering tolerances
before real calibration/prediction/scoring. No self-authored independent PASS.
CLI `predict --review ... --output NEW_DIR` requires an approval referencing the
freeze SHA256 and accepted thresholds; it reads deep data and target masses only,
then writes every calibration, admitted prediction and numerical record and
hashes them. `score --output DIR` verifies those hashes, then attaches targets
and refuses to overwrite a prior score. A leakage test mutates shallow values
and proves calibration/prediction invariance. A retrospective protocol does not
turn previously public curves into genuinely blind data.

Primary scores on **full** shallow observed support: trapezoidal beverage-mass-
weighted outlet RMSE [mg/g]; maximum |predicted-delivered minus pot-derived-
delivered|/dry dose *100 [EY percentage points]. Secondary: signed endpoint
error, early and post-wash-through residuals. No trimming difficult regions.
Engineering adequacy budgets: 5 mg/g and 1.0 EY pp, for deep and shallow.
Advantage: >=20% and >=1 mg/g lower outlet RMSE than **each** baseline;
no cumulative regression >.1 EY pp against either. These are decision tolerances,
not measurement uncertainties. Threshold straddling under declared source/
numerical sensitivity => UNRESOLVED; different admissible startup or near-optimal
calibration decisions => INITIALIZATION_OR_PARAMETER_LIMITED. Weak fits do not
establish transfer failure. No global mechanistic claim follows any outcome.

Separate decisions: observation contract, numerics, deep adequacy, shallow
adequacy, gain over N_M, gain over N_T, initialization/parameter sensitivity.
Overall labels and consequences follow the owner request. All numerical/source
allowances must be applied to those decisions, not merely plotted. Three figures
show outlet training/transfer, cumulative delivery and consequential sensitivity,
with observation markers, model lines, native units, evidence stamps and VizSpec.
No shaded prediction envelope is an experimental confidence band.

Reproduce with Python>=3.10 and repository numpy/scipy requirements, pytest and
optional matplotlib. PyMuPDF is only a local source-inspection aid, not a new
runtime dependency. Commands and environment/cost are recorded with artifacts.
Independent final scientific review and normal required CI remain mandatory.
PRs remain open and unmerged.

Pre-review numerical preparation: the exploratory 120/240/480 grids gave a
1.1543 mg/g adjacent-mesh outlet difference for the shallow uniform control
on concentration-free observed mass support. Before any real fitting/scoring,
the primary meshes were therefore raised to 480/960/1920. The original probe
is preserved as verification_observed_support.json; it did not use residuals.

## Independent-review correction (before any real fit)

The initial independent review accepted the engineering tolerances but rejected
scoring readiness. The bounded correction rechecks all frozen source/code bytes
and the exact Python/NumPy/SciPy environment before both prediction and scoring;
includes every transformed deep and shallow coordinate; rejects out-of-support
scoring; evaluates numerical outlet sensitivity on each transformed support;
requires complete baseline perturbation/start/prediction coverage and reports
baseline deep adequacy; distinguishes within-source parameter disagreement from
source/numerical threshold straddling; and requires inspectable original-PDF
identity plus BOTH selected Fig3 and Fig11 audits. Suspicious unconfirmed objects
are labelled suspected_legend, not confirmed legends. Solver failure parameters,
start and cause are retained. Hydraulic diagnostics use hydraulic mobile storage;
empirical diagnostics use the labelled dose-volume reference. A synthetic full
prediction-artifact/score/decision/figure test and analytic closed-exchange
exponential test verify affected paths. None of these fixtures uses real target
concentrations or authorizes scoring. The revised freeze supersedes the initial
rejected freeze; the independent report preserves its exact reviewed identity.
