# Pre-freeze coordinate conversion correction

After FIT-only development and before any PRED outcome attachment, source query
verification found one supported fraction-3 start smaller than m1_kg+m2_kg by
one floating-point ulp (1.734723475976807e-18 kg). The original source converts
a cumulative gram sum to kg; conditioning converts each measured vial to kg and
then sums. These represent the same measured boundary.

The source adapter now reconciles fraction 3 only to the anchor when their
difference is at most four ulps, recording both original coordinate and actual
integration start. Any larger discrepancy fails. Twice the absolute difference
is added to the solute allowance, covering integral and average-width effects.
The public runtime continues to reject every before-anchor query strictly.
No support slot is removed, inferred prefix is supplied, domain is enlarged,
source value is changed, or fit/selection/scoring threshold is modified.

The initial prediction/status, state and execution files remain private under
explicit superseded pre-freeze names. Corrected predictions are produced before
the sole freeze/audit/score; zero PRED suffix outcomes were accessed. All 549
FIT optimization starts, selected lambdas and coefficient bytes are reused.
This is a bounded source-coordinate floating-arithmetic correction, not a new
model, fitting attempt or outcome-informed scientific replay.
