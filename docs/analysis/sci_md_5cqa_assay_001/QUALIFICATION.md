# Qualification record

SCI-MD-5CQA-ASSAY-001 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
Source, numerical, software, review and scientific adequacy are distinct statuses.

The unchanged base db6f509d20ea089b6649d9eb9c3270cef8edc7a2 is recorded exactly in
BASELINE.json. All eight original source
and ten registered export bindings remain exact. First-fraction source projection
reconciled 45 FIT and 24 PRED 5CQA values with original unrounded cAlcaloids(:,3),
mE and the corresponding HPLC calibration/dilution formulas. The public export
rounding tolerances are not assay uncertainty. Fraction-2 HPLC spills never enter
first-assay inputs. The 180 original FIT suffix values/formulas reconcile; 177
have measured mass prefixes. All 45 shots and 15 designs remain. The single approved score stage also reconciled
all 96 PRED suffix assays and HPLC formulas; there was one outcome join and no refit.

The unsupported FIT intervals are FIT-E01-R3 fractions 7/10 and FIT-E06-R3
fraction 10. Held-fold support totals 176/180: FIT-C06 also retains one endpoint
beyond that fold's training-only domain. No lambda changes support. The final
PRED support is 48/48 primary, 24/24 temperature and 23/24 flow. PRED-E07-R1
fraction 10 lies beyond the hard mass domain; it is retained unsupported.
C08 retains m2 extrapolation. New-arm q1 extrapolation affects nine of twelve
primary shots: 3/3 C01, 3/3 C02, 2/3 C05 and 1/3 C06. No clipping or favorable
exclusion occurs. Supported extrapolation is not in-domain validation.

All 183 real starts converged, with no boundary hits or failed starts. Actual
residual accounting includes 31,600 calls, of which 30,080 are numerical-Jacobian
calls; maximum 211/start. Fitting wall span was 9.341158 seconds, optimizer wall
sum 6.621649 seconds, peak RSS 85,744 KiB. One worker/one BLAS thread, 12 GiB
address-space cap, 5 GiB task evidence limit and the fresh six-hour task clock
apply. E0/D0/A1 global fits are zero. All four lambdas qualified; L1 selected
0.0001 using the fixed balanced held-design rule and numerical bounds. This is
FIT-only selection, not independent validation. A1 has no held-design score.

Frozen numerical qualification uses 64/128-point knot-split quadrature, independent
adaptive integration (epsabs 1e-14 kg, epsrel 2e-13, limit 200), conservative
roundoff and original shared-anchor allowances. Maximum frozen mass allowance is
2.039772317662399e-16 kg, below the unchanged 1e-9 kg ceiling. These are integration
allowances, not analytical uncertainty or confidence intervals. R and absolute
bias bounds are propagated before threshold decisions. All 380 supported records
are qualified; four unsupported records preserve the original 384 denominator.

Focused source-free tests cover species/SI conversion, zero/invalid assays,
source identities/formulas and fraction-2 exclusions, strict feature rejection,
whole-shot/design separation, training-only transforms/domain, analytical A1
normalization versus a point assay, independent tiny-interval references, additivity,
constant curves, exact D0 objective/geometry reduction, bounds/extrapolation,
immutable serialization/tampering and source/optimizer/network-free saved inference.
Synthetic poisoned later PRED chemistry, q2 and other analytes leave fitted models
and predictions unchanged; changing permitted q1 affects only new-arm predictions.
Synthetic score tests exercise original denominators, absolute-before-average bias,
numerical decision overlap and the single-score guard. The focused/predecessor
run passed 108 tests. Real optimizer start accounting excludes explicitly synthetic
QA tests, whose receipts live only in pytest temporary directories.

Read-only verify replayed all 384 predictions/states exactly, with zero optimizer
calls, outcome joins or score calls. Public saved models support the source-free
example in REPRODUCE.md. Runtime requires no training module, corpus workbook,
private execution directory or network. Review and one-score receipts are separate
from general QA and hosted CI. Final QA details and skips are in QA.json and
HANDOFF.md; skips and the existing optional-Taichi acknowledged exception are not
passes. No protected scoring entry point or native EWP run is part of generic QA.

Original source data, predecessor science/models/protocols/results, production
registry/defaults/dependency locks, manuscripts and EWP remain unchanged. Physical
validation and analytical uncertainty are NOT_ESTABLISHED. Pannusch/Schmieder,
Mendeley 10.17632/y2tz67f6ry.1; source-derived artifacts retain CC-BY-NC-3.0 separately
from first-party software licensing.
