# PW-COR15-SHAPE-001 — frozen D0 shape on extracted beds

**Owner-approved execution plan, amended before evaluation.** Twelve descriptive series; no shared amplitude. Illustrative conductance ratios are model predictions, not observations.

**Readings.** [Corrochano 2015](https://doi.org/10.1016/j.jfoodeng.2014.11.006), CC BY 3.0: three density panels × four grinds. Fig.10 is PDF p.9/printed p.113 in the mounted copy; inspect native raster/vector objects. Follow P2 provenance: source/figure hashes, coordinates, shared calibration, units, identities, reading bounds and missing/ambiguous coverage, checked by overlay. Read mean markers and recoverable SD bars only, never fitted lines or invented hidden points. Axes: horizontal Q, vertical corrected ΔP. SD describes three independent beds; trajectories/cross-step covariance are unavailable. Never reconstruct beds or treat steps as independent beds. Separate experimental SD, graphical uncertainty and unresolved instrument uncertainty. Perturb readings within enclosures with shared panel calibration; refit all models on identical realizations. These are reading-uncertainty intervals, not population confidence intervals.

**Measurement.** Journal methods confirm upstream metering, apparatus-loss subtraction and last-30-of-60-s averages. Never subtract losses again. Check applicability of the [thesis audit's](../../analysis/sci_md_corrochano_pressure_flow_001/SOURCE_RECONCILIATION.md) printed/plotted correction discrepancy, finite calibration support and inlet-meter reference. Exact calibration reuse in Fig.10 remains unauthenticated; record unresolved limits without invented coefficients/error budgets. Flow-dependent correction can correlate pressure/flow errors. Descending tank settings 4.5→0.5 bar, 60 s each after 600 s hydration, also change time, flushing and loading history. Use plotted bed pressures, not tank settings.

**Models.** P=corrected ΔP in Pa; P_bar=P/100000; Q in m³/s. Minimize equally weighted squared Q residuals separately per series, unlike the source's ΔP-on-Q regression. No inverse-SD weighting or independent-error likelihood. G>0 in m³/(s·Pa), Qref>0 in m³/s, c>0 in m³/(s·bar); Pref=100000 Pa.

| Model | Law | Free parameters / domain |
|---|---|---|
| L0 | Q=GP | 1 amplitude per series |
| L1 | Q=G(P−P0)+ | 2: G, P0∈(−∞,max P); P0≥0 **not** enforced |
| L2 | Q=Qref(P/Pref)^m | 2: Qref, m≥0 |
| FA, primary | Q=c Pd_bar[1−exp(−(P_bar/Pd_bar)^n)]exp(−P_bar/Pstar_bar) | 1 amplitude per series |
| FA-S, separate sensitivity | Same law, Pstar free | 2: c, 1/Pstar≥0, including Pstar=∞ |

Freeze [D0's A/DESCRIPTIVE_ALL `point_replay` tuple](../PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv): **n=2.4709360685491837, Pd=3.5633704054718103 bar, Pstar=24.396659674282887 bar**. Profile amplitudes analytically; search remaining coordinates deterministically, retaining competing/boundary limits and unidentified parameters. R(M) is absorbed into c, assuming constant recovery, not absence of history effects. Substituting bed pressure for D0 line pressure is a separate transfer assumption; c cannot repair coordinate mismatch.

**Headline: FA versus L0, 12 separate fits each.** Report dimensional per-series RMSE, signed predicted-minus-observed residuals (especially lowest steps), and all twelve contrasts. Fix S_s²=mean_i(Q_obs,s,i²) from central readings. Report D=mean_s[(MSE_FA,s−MSE_L0,s)/S_s²], negative favoring FA; normalization affects reporting only. Compute D inside each matched reading realization on identical retained points, never by subtracting marginal interval endpoints. Report its reading-uncertainty interval. L1/L2/FA-S are diagnostics with parameter counts; negative P0 is an offset, not entry pressure. L1/L2 contain L0; lower residual alone establishes no new law. No significance test/acceptance threshold.

**Exponent reference.** Fit Q_FA(P_i)≈A(P_i/Pref)^m_FA using L2's identical objective, weights and m_FA≥0, with A free. Recompute on every perturbed pressure grid and pair any m−m_FA within that realization. m_FA summarizes the retained grid, not a constant form-A exponent; 1 and m_FA are references, not bounds or grades. FA remains frozen.

**Table 2.** Compute k=GμL/A from L0 in SI, using source viscosity/geometry and **consolidated** height, never initial depth. Recover/authenticate that convention; missing inputs leave k unresolved. Compare with averaged individual-bed permeabilities, reporting aggregation, orientation, geometry and digitization differences. Internal normalization check only, not validation or a gate.

**Interpretation and outputs.** Near-linear at recovered resolution: this D0 curvature does not transfer under this protocol, motivating state/history questions, not a Waszkiewicz fresh-bed entry mechanism. Resolved curvature: the sweep needs explanation, not necessarily pressure-only intrinsic permeability. Unresolved: observations/qualifications cannot distinguish shapes. Poor FA fit rejects this mapped shape, not every form A parameterization/opening mechanism; coffee, preparation, coordinates and measurement systems remain competing explanations. Deliver digitized CSV/provenance, per-series model table, one twelve-panel figure (markers, SD bars, five curves; original axes), and one-page numbers-first SUMMARY. Python only; no Waszkiewicz refitting, CFD, new gates or wall-clock limits.
