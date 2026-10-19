# Finite-rate Pannusch versus its equilibrium limit

**FINITE_RATE_LOWER_ERROR_ON_DECLARED_NORMALIZED_FRACTIONS.**
G1 / NO_GOVERNING_PHYSICS_CHANGE / SOURCE_INTERNAL / TARGET_EXPOSED.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Practical materiality is not established.

One matched comparison executed on all four primary March conditions
(PRED-C01/C02/C05/C06), three physical shots each, paired caffeine/trigonelline,
and six original assayed fractions each: 144 scalar observations in 12 shots.
All analytical, numerical, empirical-reference and deletion components completed.
The full source corpus was not rescanned. TDS, 5-CQA, ramps, other campaigns and
coffees were excluded; their historical findings remain unchanged.

## Matched prediction and observed errors

RMSE is in normalized-share units. Analytes are equally weighted within shots,
shots within conditions, and conditions overall. Numerical allowances below
propagate the declared concentration allowances through the six-share denominator
and the RMSE; they are engineering sensitivity allowances, not confidence bounds
or experimental uncertainty.

| Summary | Finite rate | Equilibrium | Boundary-aware empirical | gain_finite | Numerical allowance on gain |
|---|---:|---:|---:|---:|---:|
| Both analytes | 0.01134530 | 0.07804343 | 0.01118680 | +0.06669813 | ±0.00025469 |
| Caffeine | 0.00879575 | 0.06913665 | 0.00922560 | +0.06034091 | ±0.00022203 |
| Trigonelline | 0.01389485 | 0.08695020 | 0.01314801 | +0.07305536 | ±0.00028735 |
| PRED-C01, both | 0.01368434 | 0.08281305 | 0.01385387 | +0.06912871 | ±0.00020922 |
| PRED-C02, both | 0.00973095 | 0.07739619 | 0.00903431 | +0.06766525 | ±0.00036562 |
| PRED-C05, both | 0.01155130 | 0.07415063 | 0.01195374 | +0.06259933 | ±0.00022719 |
| PRED-C06, both | 0.01041460 | 0.07781384 | 0.00990529 | +0.06739923 | ±0.00021672 |

[LOSSES.csv](LOSSES.csv) retains every condition/analyte panel and the reference
contrasts. The balanced RMS difference between the two *predicted* profiles is
0.07319226. The observed-error difference is the distinct +0.06669813 above.
Every individual shot/analyte favors finite rate (smallest gain 0.05126710);
no adverse fraction or species has been omitted.

The C1 boundary-aware reference is **reused paired evidence**, not a new fit.
All 24 retained shot/analyte error identities reproduce the corrected published
condition aggregates; the historical observed six-share vectors, windows and
Pannusch errors also match. Its calibration-only information contract uses
measured vial boundaries/quantities and no March chemical target to fit its
predictor. No empirical profile was reverse-engineered from an aggregate.

Relative to that reference, the finite-rate gain is **−0.00015850 ±0.00025469**;
its small nominal disadvantage is numerically unresolved under this study's
allowance. Caffeine favors finite rate by +0.00042985 ±0.00022203; trigonelline
favors the reference by 0.00074684 ±0.00028735. These are descriptive numerical
comparisons, not sampling significance. Equilibrium's gain against the reference
is **−0.06685663** (frozen equilibrium allowance 1e-12). The retained reference errors are used
as fixed artifacts; their measurement/model uncertainty is unquantified.
Therefore the clear finite-versus-equilibrium ranking does not establish a
unique mechanistic advantage over the empirical comparator. Absolute adequacy
and practical usefulness have no independently justified gate here.

## The finite deletion family

Baseline plus all 12 leave-one-physical-shot-out and four leave-one-condition-out
reductions used the same frozen predictions and paired omissions. Rebalancing
was repeated after every omission, including equal condition weighting when a
condition retained only two shots. There were no new fits or solver campaigns.

| Summary | Minimum gain in 17 cases | Maximum gain | Positive / numerically resolved |
|---|---:|---:|---:|
| Both | 0.06588794 | 0.06806440 | 17/17; 17/17 |
| Caffeine | 0.05940284 | 0.06145662 | 17/17; 17/17 |
| Trigonelline | 0.07163199 | 0.07607361 | 17/17; 17/17 |

[DELETIONS.csv](DELETIONS.csv) contains all reductions, losses, gains and
allowances. No sign changes occurred. This is stability within one finite
sensitivity family, not a population confidence statement or 144 replicates.

## Fraction allocation and historical reconciliation

Balanced signed residuals (prediction minus observation):

| Position (source fraction) | Finite rate | Equilibrium |
|---|---:|---:|
| 1 (1) | +0.00133444 | −0.06488278 |
| 2 (2) | +0.01665998 | +0.05871378 |
| 3 (3) | +0.00523689 | +0.11956050 |
| 4 (5) | −0.00379542 | −0.01323598 |
| 5 (7) | −0.00943631 | −0.06273410 |
| 6 (10) | −0.00999957 | −0.03742142 |

Early allocation error (positions 1+2) is +0.01799442 finite and −0.00616900
equilibrium; tail allocation error (5+6) is −0.01943589 and −0.10015551.
Cumulative-share RMSE is 0.01605034 and 0.07607584. Thus the equilibrium arm's
smaller signed *combined early* error does not imply better profile shape:
early cancellation hides an underallocated first fraction and overallocated
second fraction. The signed residual sum is zero by normalization.
[RESIDUALS.csv](RESIDUALS.csv) retains all positions, both species and finite
share allowances; no absolute-bias gate is imported.

The new FV finite-rate mean RMSE differs from the retained historical nodal
0.01137215556 by **−0.0000268585**, smaller than the new aggregate allowance.
The largest individual share difference is **0.0007938935**. This is a new
numerical realization, not exact historical replay. The conservative FV method
uses cell averages, first-order upwind transport and positive initial liquid in
all cells; the old source nodal method uses its biased stencil and a clean inlet
coordinate with the previously documented accounting issue. These distinctions
explain why identity is not required. This study does not separately apportion
the small differences to each numerical choice. Historical predictions and
results remain untouched; the fraction-2 excess and tail deficit persist.

## Analytical and numerical evidence

[PROTOCOL.md](PROTOCOL.md) derives S=alpha_s1+phi_v2*alpha_s2 and H=alpha_l+S/K
from the source equations. The equilibrium outlet is K*c_s0 until
`t_front=t0+A*L*H/Q`, then zero. Exact interval overlaps handle front crossings.
The initial liquid inventory is retained, and the inlet face is not a deleted
first-cell volume. [MODEL_CONSTANTS.json](MODEL_CONSTANTS.json) records actual
partition coefficients, source rates, front times and phase inventories.

Both arms analytically cancel a common positive initial inventory scale in
normalized shares. Synthetic 0.001x/10x replays yield finite share changes below
3.89e-16 and equilibrium changes below 5.56e-17; unnormalized masses scale.
Partition, capacities, flow, start and windows do not cancel. Initial inventory
is a fitted model quantity, not a measured production inventory.

All 96 actual-support FV runs (24 profiles × N400/N800/N1600/N1600 split-time)
qualify: worst profile RMSE allowance 0.000867952 <0.001; spatial change ratios
at most 0.663123; maximum temporal share change 1.7431e-14; phase positivity
passes; maximum independent phase-sum/outlet ledger residual 2.0807e-13.
The independent physical-coordinate Radau check differs by at most 6.2076e-14
in normalized shares and has mass residual 2.2205e-16. Analytical complete
outlet delivery equals initial inventory to relative 2.2205e-16.
These are numerical qualifications on this support, not physical validation
or rigorous continuum error certificates. See [NUMERICS.json](NUMERICS.json)
and [VERIFICATION.json](VERIFICATION.json).

The bounded synthetic rate family 1x/10x/100x, N50/100/200 approaches the
analytical observable as transfer and resolution increase. At N200 its
continuum share RMSE changes 0.06969358 → 0.03482911 → 0.01203005.
At 100x, error versus the *finite-grid equilibrium* reference is 0.00803594;
that grid reference itself is 0.00400004 from the continuum front. These are
separate errors, not an additive identity, and neither is negligible merely
because the rate is large. No claim of attained continuum equilibrium at 100x
is made. [FAST_TRANSFER.csv](FAST_TRANSFER.csv) retains every combination.
The scientific equilibrium predictor is always the analytical front.

Execution accounting: 96 primary-support integrations; 16 successful synthetic
integrations plus two completed calculations lost at a report-assembly failure,
18 charged synthetic integrations total; 17 small algebraic/synthetic tests.
One independent pre-score audit approved the exact corrected freeze; final review
and software checks are reported separately in [HANDOFF.md](HANDOFF.md).

## Interpretation and remaining limitations

The evidence addresses the narrow H1 subclaim that **replacing finite-rate
exchange by local equilibrium preserves normalized fraction predictive
performance for this specified Pannusch parameterization and source-equilibrium
start**. That preservation does not hold on the declared observations: the
analytical equilibrium limit allocates substantially more to middle fractions
and less to the assayed tails, increasing the declared loss. This does not
adjudicate every equilibrium model, all parameterizations, or real espresso's
regime occupancy, and does not uniquely identify intraparticle kinetics.
Shared parameters were fitted under finite-rate equations. No equilibrium
refit is authorized or attempted. No new practical improvement requirement
has been inferred from these results.

The flow-label meaning remains unresolved: both arms use precisely
`flow_start_mL_s/1000/980` as prescribed mathematical SI flow. Neither predicts
hydraulics or uses measured inlet flow. Start is the historical earliest
supplied boundary (0 s here), not an established physical shot-start clock.
Measured vial quantities and source-qualified windows condition predictions;
unassayed intervals remain gaps and the normalization is not complete-cup
mass closure. Assay recovery, LOD/LOQ/censoring and correlated measurement-error
models, mass-fit coefficient covariance/window uncertainty, coffee lot/roast
joins, and independent production M0/initial-state measurements remain unresolved.
Deletion ranges do not replace those uncertainties.

Pannusch's scale cancellation does not overturn SCI-MD-008's EWP inventory-shape
failure (maximum 0.0801141) or SCI-MD-009's nonlinear response qualification
failure (0.0825543 versus 0.02). EWP source, lock, defaults, native cases and
issue #104's shared/species law test are unchanged. No OpenFOAM, acquisition,
protected scoring, author message, new governing closure, adoption, merge or
successor occurred or follows.

Source attribution: Pannusch et al., J. Food Eng. 367, 111887,
DOI 10.1016/j.jfoodeng.2023.111887; author data/code, Mendeley
10.17632/y2tz67f6ry.1. Source-derived aggregates retain CC-BY-NC-3.0 separately
from first-party software. Originals, detailed profiles, logs and private
locators remain external. [INPUT_MANIFEST.json](INPUT_MANIFEST.json) identifies
specific evidence reused and unresolved components.
