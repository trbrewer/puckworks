# Same-session independent-method mathematical review

Disposition: **PASS for the bounded necessary-shape aggregation result**.
This is one compact same-session independent-method review, not a separate human
or external audit. Accepted #364 source recovery/helper qualification is reused;
no repeated PDF/source audit. [review.json](review.json) binds original inputs,
solver, independent checker, focused tests, unchanged transform helper and results.
[artifact_sha256.json](artifact_sha256.json) binds the scientific packet, without
a self-referential commit-hash requirement. Operational documentation can change
without invalidating unchanged scientific bytes.

The finite-window integration is correct, including k=0. Fixed positive weights
produce positive, nonincreasing C_n, and the paired expansion of
C_n*C_(n+2)−C_(n+1)^2 is a sum of nonnegative terms. Therefore convexity of
log10 C_n is necessary. The equality counterexample (100,10,1,1) confirms that
the converse fails; the implementation never fits mixtures or claims otherwise.

The prefix minimum step is justified by nonincrease, and the convex minorant
maximality follows by bounding any candidate at each pair of hull anchors and
then along their chord. Since prefix minima are nonincreasing, all hull slopes
are nonpositive. Uniform expansion translates the greatest sequence, giving
the exact half-gap formula. Earliest prefix ties, collinear endpoint retention,
single-anchor controls and repeated prefix sources are deterministic. Certificate
weights use anchor coordinates, not prefix-source coordinates. Empty/single/two
point and nonuniform/gapped support cases retain their appropriate meanings.

Independent method: `matias2023_aggregation_check.py` reads original observations
and checks rational primal feasibility plus an equal rational lower bound. It
imports neither the hull producer nor its optimizer. For every source layer,
10 original interval checks, 9 nonincrease checks and 8 secant checks pass; its
maximum signed-distance magnitude is exactly the reported objective. The unique
source control is F02 against F01–F04 with weights 2/3,1/3. Inserting original
CSV bounds in l_F02−(2/3)u_F01−(1/3)u_F04 gives exactly twice each reported
objective. This proves optimality without numerical LP tolerances.

The separate epigraph LP specifies every y as unbounded in sign. HiGHS agreement
on all four source layers differs from exact rational values by at most
1.95e−16 dex; focused nonuniform, increasing/mixed-upper, negative-log, collinear
and tied-control fixtures also agree. LP tolerance is QA only. The exact
checker rejects mutated witnesses, weights, anchor coordinates, prefix sources,
bounds and omitted tied controls.

Transformation review reuses #364's correctly rounded Decimal ln/exp helper with
adjacent representable bounds, directed division/products and outward decimal
quantization. A 90-digit independent evaluation agrees for every source result;
the exact rational cube fixture checks M and reciprocal enclosures without any
transcendental approximation. Plain mg/L conversions remain approximate displays.

Uncertainty review: G/P are rectangular relaxations of shared calibration.
Set inclusion proves the relaxed outer/realized/inner bracket, while mixture
containment provides only a lower bound on mixture discrepancy. Inner positivity
alone is not universal exclusion. The positive outer result is decisive here.
P_outer's 0/8 local exclusions coexist with positive global cost; N/G have 5/8
and P_inner 1/8. All ten means/four extractions are the existing cohort; no
statistical significance, practical threshold or independent validation is claimed.

The semilog figure was visually inspected. All ten means, true-scale G bands,
descriptive SE and N/P_outer relaxed representatives are distinguished. The
annotation explains the controlling chord; caps are display marks, horizontal
source segments have no invented meaning, and connections do not imply an
instantaneous law. Source-derived attribution is separate from MIT code.

The result closes only the specified nominal equal-volume, fixed-weight
aggregation question. It does not identify failing shots/assumptions, physical
nonexponential kinetics, diffusion or rejection of the full Matias continuum
model. Uncontrolled temperature, separate Soxhlet inventory, absent time/mass
mapping and NOT_ESTABLISHED unequal-volume robustness remain. PHYSICAL_VALIDATION
is NOT_ESTABLISHED. No production/EWP changes, merge or successor.
