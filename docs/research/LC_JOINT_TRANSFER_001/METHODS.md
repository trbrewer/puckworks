# Interpretation and artifact definitions

This is one retrospective, target-exposed capacity comparison on the already used
Waszkiewicz campaign. The model keeps J1's pressure-independent front clock and
fixed R0 chemistry, storage, recovery and beverage observation assumptions. Neither
the fitted mixture coefficient f nor the fitted front time identifies a pore,
bypass, channel, swelling or compaction mechanism. Physical front arrival has no
separate measured front target here; improved cup detection does not validate it.

The [pre-fit specification](PLAN.md) controls the scientific scope. The LC adapter
subclasses the unchanged J1 prepared evaluator: front construction is independent
of capacity for W1, and only capacity and its liquid-only update are replaced
before chemistry runs. The inherited chemistry, observer, time grid, breakthrough
insertion, masks and censoring are reused. Exact nested boundaries use the original
J1 capacity expression to retain even near-zero diagnostic roundoff; the interior
uses the existing C3E LC helper. This changes no law or numerical tolerance.

Training minimizes the inherited mean of condition-mean squared normalized losses.
Reporting instead uses the inherited mean of within-condition RMSEs. Every
condition and all 56 intended brews contribute. These two aggregations differ.
Endpoint and trace flow remain liquid flow versus scale-derived beverage flow;
the detector differentiates beverage mass. The fixed normalizers are not noise
estimates, and the joint criterion is not an independent-observation likelihood.

An undetected valid history contributes the original squared-error lower bound.
Missing or corrupt histories stop the complete-cohort analysis. A difference of
computed onset bounds is **not** a bound on the unknown difference of true errors.
Detection counts accompany comparisons. Medians retain censored brews rather than
selecting detected histories. Physical front arrival and detector onset remain
separate in tables and figures.

The paired aggregate comparisons reuse exactly 1,000 condition-then-whole-brew
draws, seed 20261103, conditional on fitted parameters and fixed Mc. Pressure
subgroup intervals use the same draws; a pressure absent from a draw has no
subgroup score, and the number of usable draws is reported. There is no refit
uncertainty. The inherited nominal peak and high-pressure grade intervals retain
their original within-condition whole-brew resampling helper. The 9/11/13-bar
out-of-fold slope combines three separately fitted models. A descriptive capacity
slope, global capacity maximum, finite-time flow maximum and front/detector minima
are distinct quantities. The capacity maximum checks all stationary candidates
and both endpoint limits through the inherited C3E helper.

For each of 48 selected vectors, the frozen f=0 diagnostic holds all five common
parameters fixed, at both declared numerical steps. A better feasible A vector
can therefore be exposed without a new A fit. Resolution uses the inherited
1e-6*max(1,Jbest) objective scale and the change in the improvement between .02
and .005 s: a gain that changes sign or whose grid change is at least its size
is unresolved. The selected-versus-zero difference describes the added term at
those common parameters, not globally optimized model families. Exact f=0 can
support retaining A; f=1 removes n and n=1 removes f structurally. Near-boundary
estimates alone establish neither structural redundancy nor optimizer failure.
Sampled alternatives and their capacity curves describe practical stability only
on the stated grid, without a new parameter-identification threshold.

Corrochano's 108 markers and source qualifications are inherited unchanged from
[COR15](../COR15_SHAPE_001/SOURCE_RECONCILIATION.md). Its plotted corrected bed
pressure is divided by 100000 to obtain bar; upstream-meter volume indication
remains m³/s. No apparatus loss is subtracted again and no line-to-bed or
mass-flow conversion is introduced. Only positive amplitudes are target-fitted
in equal-weight Q space. Constant series recovery is absorbed into amplitude as
an assumption; this is neither parameter-free nor blind prediction. No unobserved
mass history, individual-bed trajectory or onset is reconstructed.

Each paired external D uses the original central S² and the same 4,096 shared-
calibration graphical realizations, seed 20261104, with only amplitudes refitted.
Intervals are graphical-reading intervals conditional on frozen Waszkiewicz
shapes, not population confidence, equivalence or noninferiority intervals.
Experimental SD and unresolved instrument/correction uncertainty remain separate.
A-480's lowest point is approximately 1.41 bar versus 0.23–0.42 bar elsewhere;
lowest-point residuals are not a common-pressure comparison. This opening-shape
challenge, over approximately 0.23–4.5 bar, says nothing about the 6-bar flow peak,
high-pressure response or fresh-puck onset. The same Corrochano/Melrose campaign
is reused; independent-campaign counts do not increase.
