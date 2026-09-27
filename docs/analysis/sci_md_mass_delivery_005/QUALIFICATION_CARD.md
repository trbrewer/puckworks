# Two-assay numerical qualification

G1 / NO_GOVERNING_PHYSICS_CHANGE. Research only. Numerical qualification is not physical validation.

The [model card](MODEL_CARD.md) freezes the strictly decreasing interval-ratio proof, existence/uniqueness, bounds, exact constant/zero degeneracies and sensitivities before conditioning. The implementation integrates entire intervals at the original mass origin. A single bracketed lambda solve uses atol=rtol=1e-12 and at most 100 iterations, followed by one 1e-14 qualification solve. Incompatible ratios never trigger clipping, epsilon denominators, optimizer fallback or bounds expansion.

The established transformed 128-node integral is checked with 256 nodes; the independent p0 reference uses adaptive quadrature. p=1 is checked against a stable analytic exponential integral including k=0. Integral error and bounded inversion uncertainty propagate through amplitude/rate and every forecast. Acceptance requires solute allowance <=1e-9 kg and relative conditioning-denominator allowance <=1e-6. The synthetic ill-conditioned case demonstrates that root convergence alone cannot qualify a forecast.

The two-observation Jacobian is reported in q (kg/kg) versus A (kg/kg), lambda (dimensionless), and k (kg^-1) coordinates where regular. Future-TDS input sensitivities have units pp/pp. Implicit derivatives agree with synthetic finite differences. Constant and zero-delivery boundary cases explicitly distinguish one-sided/singular or unidentified-rate diagnostics. A regular Jacobian does not identify physical kinetics.

The independent reviewer used incomplete-gamma integration and a separate Brent inversion, reproducing all 84 A/k fits inside frozen parameter intervals, all 168 analytical amplitudes, all 966 supported forecasts and sensitivities, and exact legacy first-assay parity. Maximum independent forecast discrepancy / declared allowance was 0.2002058812. No future chemistry was inspected for that audit. See [independent receipt](PRE_SCORE_REVIEW.json) for exact commits, tree identities, freeze and evidence hashes.

All 252 real states qualified; no failed inverse or numerical retries occurred. The 42 unsupported prediction records remain source/domain failures, not numerical failures. Full details and numerical-call counts are in [RESULT.md](RESULT.md), [RESULTS.json](RESULTS.json) and the immutable preparation snapshot [EXECUTION.json](EXECUTION.json).

Export-rounding bounds, numerical allowance and between-shot variability remain distinct. No assay variance model, assay SD or measurement confidence interval is supplied. The first two source observations cannot establish assay robustness or real-time operational feasibility. Source-derived diagnostics: Pannusch/Schmieder, CC-BY-NC-3.0, Mendeley 10.17632/y2tz67f6ry.1.
