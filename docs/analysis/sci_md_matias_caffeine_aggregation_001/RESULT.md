# SCI-MD-MATIAS-CAFFEINE-AGGREGATION-001 — result

No fixed positive mixture of nonincreasing exponentials, including four
extraction-specific exponentials, represents the ten aggregate fractions exactly
within the declared nominal, graphical or reported-SE outer bands. This follows
from a positive exact optimum over the larger nonincreasing log-convex shape
family, conditional on equal nominal 5 mL windows and fixed aggregation weights.

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING. Selected after exploratory
calculations on exposed data, not preregistered or independent predictive validation.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

All four layers are COMPLETE: all ten original slots F01–F10 at x=0,...,9,
10 centers, 20 vertical endpoints; the same four physical extractions. No new
observation or cohort. Qualified covered/clipped features remain supported.

| Layer | Exact epsilon_LC (dex) | Approx. dex | Certified M_LC enclosure | Certified 1/M_LC enclosure |
|---|---|---:|---|---|
| N | 9949/331638 | 0.029999577853 | [1.071518263689, 1.071518263690] | [0.933255207948, 0.933255207949] |
| G | 474287960807/16082359097354 | 0.029491193297 | [1.070264679667, 1.070264679668] | [0.934348314952, 0.934348314953] |
| P_outer | 2571083096567/168864770522217 | 0.015225692657 | [1.035680245588, 1.035680245589] | [0.965548975429, 0.965548975430] |
| P_inner | 2742769138607/168864770522217 | 0.016242399940 | [1.038107670299, 1.038107670300] | [0.963291215940, 0.963291215941] |

These are exact relaxed objectives, not exact mixture optima. For a mixture
under the same bands, its minimum log discrepancy is at least epsilon_LC and
its multiplicative factor is at least M_LC. For every admissible endpoint
realization, epsilon_LC,Pouter <= epsilon_LC,realized <= epsilon_LC,Pinner and
epsilon_mixture,realized >= epsilon_LC,realized >= epsilon_LC,Pouter.
The inner relaxed optimum is NOT a mixture upper bound. Its positivity alone
would not exclude mixtures for every realization. Here the outer bound is
positive, supplying that exclusion throughout the declared endpoint contract.

G/P use the accepted rectangular relaxation of shared graphical calibration;
favorable marginal readings need not be jointly realizable source geometry.
Graphical allowance, reported SE and unknown assay error are distinct. SE is
only descriptive sensitivity: no confidence rejection, equivalence test,
practical-adequacy threshold or independent replication.

## Simultaneous certificates and witnesses

All layers discover the same unique controlling relation from the full ten-point
calculation: F02 versus the F01–F04 hull chord, with weights 2/3 and 1/3.
Those anchors supply their own prefix minima here. The certificate is

```
2 epsilon >= l_F02 − (2/3) u_F01 − (1/3) u_F04.
```

The right side equals twice the exact objective in each row above.
Every relaxed representative is y=h+epsilon, where h is the greatest convex
minorant of prefix upper minima. All ten original expanded interval constraints,
nine nonincrease inequalities, eight secant-convexity inequalities and exact
maximum interval distance pass independently in every layer. The full rational
witnesses, approximate mg/L, prediction-minus-center residuals, nearest permitted
readings, signed distances and shape slacks are in [witness_residuals.csv](witness_residuals.csv).
[prefix_hull.csv](prefix_hull.csv) gives hull slopes/weights and prefix provenance;
[certificates.csv](certificates.csv) retains every tied control.
[results.json](results.json) separates relaxed objectives from mixture discrepancy
lower bounds. Center residuals in G/P can exceed the interval objective.

The [independent checker receipt](review.json) proves each optimum by exact
original-constraint primal feasibility and an equal valid lower bound, without
calling the hull producer. Separate numerical LP agreement is QA, not the
exact certificate. See [method and proofs](METHOD.md) and [review](REVIEW.md).

## Local versus global

| Layer | Locally excluding original triples | Simultaneous optimum |
|---|---:|---|
| N | 5/8 | Positive |
| G | 5/8 | Positive |
| P_outer | 0/8 | Positive |
| P_inner | 1/8 | Positive |

All eight triples per layer are in [local_curvatures.csv](local_curvatures.csv).
No adjacent check excludes P_outer, yet the full system is infeasible without
positive expansion. Shared readings needed by overlapping triples can conflict;
these diagnostics are not independent experiments. The small exact local/global
fixture in METHOD.md separately demonstrates the distinction. The (100,10,1,1)
concentration counterexample demonstrates that zero relaxed cost is necessary-only
compatibility, not evidence that aggregation explains a sequence.

[Semilog comparison](comparison.png) shows all ten means, graphical bands at
true scale, descriptive SE and N/P_outer relaxed representatives. The annotation
identifies the controlling chord. Display caps are not uncertainty; connecting
segments are not an instantaneous law. No shots or mixture components are drawn.
The [VizSpec](VIZ_SPEC.json) binds evidence, mapping and limits.

## Consequence and limits

This closes #364's unresolved fixed-positive-weight, extraction-specific constant
exponential aggregation question on the accepted observation contract. #364's
[one-rate result](../sci_md_matias_caffeine_fraction_shape_001/RESULT.md) remains
accepted and unchanged. The difference between its cost and this relaxed cost
is not an amount explained by aggregation: the relaxed family is strictly larger.

The exclusion does not identify which extraction or assumption fails, reconstruct
individual shots, establish physical nonexponential kinetics, select diffusion,
reject the full Matias continuum model or independently validate physical behavior.
Rates are in collected volume; time-domain claims require an authenticated
volume-to-time map. Horizontal semantics remain undocumented and actual unequal-volume
robustness NOT_ESTABLISHED. Temperature was uncontrolled; one-capsule Soxhlet
context is separate, with no common 70 mg normalization. No practical adequacy
conclusion, production adoption, EWP change or successor is introduced.

Offline reproduction:

```bash
python -m puckworks.analysis.matias2023_caffeine_aggregation \
  --output /tmp/matias-caffeine-aggregation --plot
python -m puckworks.analysis.matias2023_aggregation_check \
  --results /tmp/matias-caffeine-aggregation/results.json \
  --output /tmp/matias-aggregation-review.json --lp
```

Source-derived results/replot: Matias et al. (2023), CC BY 4.0, with attribution
and unchanged input identities in [SOURCE_NOTES.md](SOURCE_NOTES.md).
First-party code: MIT. Physical validation remains NOT_ESTABLISHED.
