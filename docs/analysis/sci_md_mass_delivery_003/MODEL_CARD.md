# One-fraction-anchored remaining-delivery model

SCI-MD-MASS-DELIVERY-003. G1 / NO_GOVERNING_PHYSICS_CHANGE.
Written before implementation and before extracting anchor values.

For the unchanged base concentration q0(b) in kg/kg at beverage mass b in kg,
I0(u,v)=integral q0(b) db. For measured fraction 1 [a0,a1], mA=a1-a0,
qA=TDS_anchor_percent/100, SA=mA*qA, alpha=SA/I0(a0,a1).
Future S(u,v)=alpha*I0(u,v); TDS_percent=100*S/(v-u).
Remaining_solute(B)=alpha*I0(a1,B), B>=a1.
Sensitivity d(TDS_future)/d(TDS_anchor)=mA*I0(u,v)/((v-u)*I0(a0,a1)).
This sensitivity is not a confidence interval or sensor specification.

Exactly one analytical amplitude update. No shape/offset/shrinkage changes,
bounds fitted to alpha, second anchor, later chemistry, inventory inference,
new fitting, optimization, hyperparameter search or candidate selection.
MASS and BOUNDARY_AWARE_EMPIRICAL are frozen 001 artifacts;
SETTING_AWARE_EMPIRICAL is the frozen 002 artifact with its existing constant
nominal temperature/source-design-code semantics and design diamond.

Information roles: inherited FIT artifacts are fixed curves; only fraction-1
measured mass and mass-basis percent TDS are anchor input; future intervals are
coordinate-only queries; later TDS belongs only to the audited scorer.
Measured future mass windows are an explicit evaluation privilege. These
predictions are conditional on supplied windows, not forecasts of their masses,
collection times or final attained mass. All intervening collected vials advance b.

Anchor requires finite mass-basis TDS in [0,100], positive measured width and
supported endpoints. I0 must be positive with allowance dI<I0 and dI/I0<=1e-6.
Zero observed TDS permits alpha=0; a zero/unresolved denominator is never repaired.
Use inherited exact linear-hat integration or compact quadrature with refinement
and independent adaptive integration split at empirical knots. Ratio interval
SA/[I0+dI,I0-dI] and future integral interval [max(0,I-dI),I+dI]
propagate into solute allowances, then metrics and every decision. Required final
allowance <=1e-9 kg on nonzero-width queries. Include floating arithmetic allowance.
No clipping/extrapolation. Compact curves are monotone, so the maximum on the
claimed anchored domain [a0,base_max] is at a0; linear profiles attain extrema at
endpoints and knots (including nonmonotone profiles). Verify alpha*qmax<=1;
if numerical bounds cross 1 the state is unresolved. Future domain is
[a1,base_max]. Zero width gives S=0 and explicitly undefined average TDS.
Nonfinite, negative, reversed, earlier-than-anchor or unsupported queries fail.

Immutable state binds exact base artifact bytes/hash, model identity, typed
anchor identity/interval/basis/TDS, alpha/allowance, support, source/rights/claims.
Strict deserialization revalidates the mathematics and bindings. No complete
chemistry-bearing records accepted by the prediction API. Real states stay private.

SOURCE_INTERNAL; TARGET_EXPOSED;
RETROSPECTIVE_EARLY_ASSAY_CONDITIONED_COMPARISON.
Not recipe-only prediction; alpha is not identified soluble inventory. Success
does not identify the cause of campaign errors; failure rejects only this frozen
update, not every amplitude/assimilation strategy. No time/pressure/flow/mass-
attainment prediction, real-time assay or controller performance established.
Assayed suffix delivery is not measured whole-cup delivery. Conditional adequacy
is not physical validation. Source-derived states/results retain Pannusch/Schmieder
attribution and CC-BY-NC-3.0, DOI 10.17632/y2tz67f6ry.1; software licensing separate.
No production defaults/lock changes, native EWP runs, laboratory work, merge or successor.
