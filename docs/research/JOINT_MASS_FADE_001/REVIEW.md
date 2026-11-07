# Fresh independent read-only review

The final reviewer was separate from the pre-fit auditor and received a fresh
review context. It found **no remaining actionable defects** in the final code,
frozen outputs or revised claims. It performed no fitting, source edits or EWP
writes. The audited implementation/output hashes are recorded in RUN_RECEIPT.json.

The review independently checked both hydraulic integrations, separate Mc/gamma
adapter and tau0 ordering, exact-prefix behavior, source/fold identities and
shared resample banks. Recorded-pressure positive-gamma cases at 1/2/6/9/13 bar
matched between integration paths and prefix/full observers at rtol=1e-12;
independent liquid-mass residuals were below 1.1e-13 g.

The final audit verified all 456 starts and their trial hashes, 387,062 retained
evaluations, 24 selected winners and 12 exact embedded-control dominance checks.
It reconstructed all 6,720 replay windows from cumulative masses and native
observers (maximum window residual zero), all 286 trajectory/late-comparison
rows, all 288 paired metric contrasts, all 672 per-brew error/detector
evaluations, 402 peak rows, 36 regime/boundary rows and 66 component
decompositions. Source late values and intervals reproduce #423 exactly.
Numerical sensitivity, the rendered figure and all four summary answers were
also checked.

The reviewer confirmed held-out primary score 0.277365→0.256500 g/s, paired
difference −0.020865 [−0.036950, −0.006080], 9/11 late point-discrepancy
improvements in each scope, and the stated direction/catch-up failures.
LOCO onset remains a computed lower bound with 52/56 detections in both arms.
The mixed conclusion and retention of A-J1 as baseline are supported.

The review requested three minor summary corrections: direct rounding of the
9-bar early level to 1.422, stating that both 1- and 3.5-bar observed late
intervals include zero, and labeling the invented 5-bar decline as a point
result. All were applied and rechecked. Final-head hosted CI is checked
separately and linked in the draft PR.

A final serialization-only delta removes Matplotlib SVG trailing blanks. The
reviewer confirmed all 1,527 XML elements and non-whitespace geometry/attribute/
text tokens are unchanged, all 12 CSV hashes match, and fit/evaluation freezes
are unchanged. Both successful report timers are retained and counted. No new
finding resulted from this delta review.
