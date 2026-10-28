The scored comparison is complete. A documented reporting-factor difference almost removes the displayed Figure 5 discrepancy algebraically, but does not authenticate the generating configuration or change physical EY. Increasing one shared diffusivity improves the conserved baseline by 43.4%, yet loses decisively to the equally constrained constant control. **Deprioritize D_S-only adjustment within the declared range.** This is exposed, in-sample source reconstruction, not blind prediction, physical validation or a diffusivity measurement.

The unchanged baseline has RMSE 7.1024 EY percentage points (pp). Multiplying its unchanged cup output's reported EY by phi_s^-2 = 1.461433 gives RMSE 0.1013 pp. This is a labelled algebraic diagnostic, not a fitted correction or authorized denominator. Its small residual is not numerically resolved: baseline refinement alone changes individual EY values by up to 0.1753 pp before that multiplication. The actual Figure 5 generating revision, grind sweep and normalization remain unknown.

The released author example differs in fines radius (80 versus 12 µm), surface coefficient (1e-9 versus 6e-7), liquid dispersion and endpoint. It is not established as the Figure 5 generator. [CONFIGURATION.csv](CONFIGURATION.csv) separates all three configurations, including areas, phases, inventory and denominators. Code inspection traces dimensional D_S through D_S*t/a_i², radial diffusion flux and cup-solute integration. Deff_star=1e-6 is liquid dispersion. Physical EY remains 100*cup_solute/0.020 kg; no TDS dataset was manufactured.

The retained October 1 Octave executions were read, not repeated. Their 33.9/339 s endpoints contain 2.623963521/4.797007806 g cup solute and author EY 19.1900517/35.0823581%, implying a 13.67356 g reporting denominator. Their 40/400 g reference-density throughput does not authenticate actual beverage mass or dry dose; endpoints are not a complete trajectory replay package.

Recovery took 405 seconds within the 30-minute cap. Existing September publisher exports, calibration metadata, extraction script, historical checksum receipt and retained article text were inspected; the original publisher file was hash-verified without new reading/digitization. The seven homogeneous-curve ordinates are deterministic targets, not experiments. Seven separate experimental means are also exposed; authenticated physical-shot count and grouping are **UNKNOWN**. The source is Cameron et al., *Matter* 2 (2020), 631–648, DOI 10.1016/j.matt.2019.12.019. Attribution, original hashes and coordinate conventions are retained in [RESULTS.json](RESULTS.json); private originals and locators remain external.

Independent phase-volume reduction gives initial solute 4.893494613 g and ceiling 24.467473% of declared dry dose. Only grind 1.1's target interval [24.518895, 24.578895]% lies wholly above it, excluding exact D_S-only reconstruction under fixed accounting. All seven points were nevertheless scored.

| Arm | Fitted parameters | MAE | RMSE | Maximum absolute error |
|---|---:|---:|---:|---:|
| A: unchanged conserved baseline | 0 | 7.0915 | 7.1024 | 7.6843 |
| D: shared D_S | 1 | 3.8840 | 4.0198 | 5.4721 |
| B: bounded constant | 1 | 0.9829 | 1.2400 | 2.1784 |

All errors are EY pp. D selects the upper endpoint, 6.25e-9 m²/s (10× printed D_S). The bounded optimizer exhausted its 12-call allocation without convergence; the explicitly evaluated endpoint was best among all 15 evaluations. No global optimum is claimed. B=22.679262% lies below the ceiling, so the unrestricted target-mean diagnostic is identical. No pressure, inventory, surface-rate or denominator was fitted.

D's RMSE reduction versus A is 3.0825 pp, gain 0.4340 (**large**); versus B it is −2.7799 pp, gain −2.2418 (**worse**). Combined graphical/numerical sensitivity ranges for gain are [0.3816, 0.4839] and [−2.5263, −1.9684], respectively. All nine independent ±25% boundary combinations retain those classifications, including the adverse result.

Graphical allowance is ±0.03 pp. Coherent common shifts and the retained second reader preserve shared calibration effects; simultaneous outer envelopes assume no independence. Numerical sensitivity uses the sole prescribed refinement, N40/M24 to N160/M48 with tenfold tighter time tolerances. Maximum changes A=0.1753 and D=0.2515 pp both **exceed the 0.05 pp engineering target**. Examined sensitivities preserve ordering and bands; they are not certified continuum-error bounds. Sampling CIs for the theoretical curve are NOT APPLICABLE; no physical D_S CI is claimed.

Separate experimental RMSEs A/D/B are 6.4808/3.2862/1.0275 pp, with no additional fitting. Partially clogged and standard-flow results remain separate in the aggregate output. Available bars are SDs, not mean CIs: four complete, one upper-only, two unquantifiable. Experimental CIs are NOT_ESTIMABLE; unknown assay/systematic errors remain excluded.

All 126 integrations succeeded in 82.57 seconds. Ordinary/override parity was exact; maximum independent mass residual was 3.34e-17 kg. No GSA was run; ST(D_S)≈0.83 and ST(K_RATE)≈0 remain user-reported context with unknown provenance. Reproduce saved reductions using `python tools/cameron_ds_baseline.py score`; `figure` redraws the plot. Fresh `run --private <external-directory>` requires a new receipt directory and enforces the frozen budget. Final check/review receipts are in RESULTS.json.

**Single next action — drafted, not sent:** Please provide the existing Figure 5 generating revision, grind-sweep script, parameter files, numerical ordinates and EY normalization, including the dose/geometry and endpoint conventions. These would establish whether the reporting/configuration differences actually generated the published curve.
