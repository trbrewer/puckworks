# Source and measurement qualifications

[The source](https://doi.org/10.1016/j.jfoodeng.2014.11.006) was inspected in the
mounted collection. [Intake provenance](../../../puckworks/data/romancorrochano2015/fig10_shape/PROVENANCE.md)
and [contract](../../../puckworks/data/romancorrochano2015/fig10_shape/contract.json)
identify the exact PDF/native figure; [overlay](READING_OVERLAY.png) makes the
reading reviewable. Source and adapted overlay: CC BY 3.0. Figure 10/Table 2 are
printed113/PDF9. This is the existing Corrochano/Melrose campaign, not new beds.
The PDF container differs from the earlier intake, but **Fig.6 XObject264 and
Fig.13 XObject380 match the earlier intake byte for byte**. Existing Fig.6b
consolidation readings can therefore be reused with their original qualifications.

| Quantity | Source fact and adopted treatment |
|---|---|
| Coffee/preparation | Medium-dark Arabica from Central America/Brazil; Dalla Corte grinder, distributions A–D, initial density 360/400/480 kg/m³. Three independently prepared beds per series. These are not Waszkiewicz coefficients or universal coffee properties. |
| Geometry | Chamber diameter 0.037 m, initial length 0.0185 m (p.108). The bed consolidates; Eq.8a/b separately measure height reduction and removed-bed height, Eq.8c averages their consolidation fractions. Fig.6b reports that average. |
| State/protocol | 600 s hydration at nominal 80°C; source calls beds fully extracted. Tank hydration pressures 2.5/3.0/4.5 bar by initial density. Descending tank steps 4.5→0.5 bar, 60 s per step, last 30 s averaged (pp.109–112). Pressure, elapsed time, flushing and loading history change together. Recovery constant over the sweep is a transfer assumption, not a measured history-free state. |
| Q | Ultrasonic USC-731 upstream of heaters/cell (Fig.1/p.108); recorded with pressure/temperature at 10 Hz. We retain inlet-meter volume indication. The local/standard volume reference, meter temperature/density correction and correspondence to downstream volume are not specified. No density conversion or corrected outlet volume is invented. |
| ΔP | Before-cell transducer indication minus previously measured showerhead/bottom-filter losses (p.108). Plotted corrected bed pressure is retained; tank settings are not its coordinates. Outlet/reference and correction uncertainty are not numerically specified. No second subtraction. |
| Spread/aggregation | Fig.10 means and SDs over three beds. Individual trajectories and cross-step covariance are unavailable. Table2 averages permeabilities fitted separately to beds, whereas this analysis fits plotted mean coordinates. |
| Fitting direction | Source rearranges Darcy with Q independent (Fig.8/10 captions). All five present fits minimize equal-weight squared Q residuals conditional on the recovered P points. No orientation-dependent R² is used to decide shape. |

## Pressure correction: what transfers from the thesis audit

The [earlier audit](../../analysis/sci_md_corrochano_pressure_flow_001/SOURCE_RECONCILIATION.md)
inspected thesis p.64/PDF89, whose printed calibration
`h(Q)=1.8e14 Q²+5.3e8 Q+1.9e3 Pa` disagrees with its plotted curve: at
Q=1e-5 m³/s the expression gives 25200 Pa versus approximately 21000 Pa.
Its six measured calibration levels cover approximately 3.2e-6–1.66e-5 m³/s,
with graphical endpoint enclosures [3.0,3.4]e-6 and [1.60,1.70]e-5.
The same rig lineage, upstream meter and loss-subtraction procedure apply to the
journal. **Exact reuse of that calibration in Fig.10 is not authenticated.**
The discrepancy is therefore an unresolved applicability limitation, not proof
that the journal used the erroneous expression. `CALIBRATION_SUPPORT.csv` compares
each reading enclosure with those conditional support endpoints; below-support
points do not authorize polynomial extrapolation. No correction coefficients,
uncertainty budget or repair is inferred. Because the correction itself depends
on Q, physical Q/ΔP errors may be correlated. Independent pixel perturbations
cannot settle that issue.

Against that **conditional** calibration support, 68 recovered Q enclosures are
within, 32 below and eight ambiguous; none is wholly above. These counts do not
authenticate the journal's correction or supply its extrapolation uncertainty.

## Table 2 normalization check

`TABLE2_CHECK.csv` uses L0's G in m³/(s·Pa), A=π(0.037 m)²/4 and the **consolidated**
reconstruction L=0.0185(1−λ_average) m from the authenticated earlier Fig.6b
readings. This uses the source's consolidation convention; the individual beds'
L_actual inputs and the exact geometry used in their Table2 regressions cannot
be recovered. Initial height is never substituted for consolidated height.

The journal defines viscosity but provides no numerical value/correlation in the
inspected text; corresponding thesis Eq.3.20/p.87–88 calls it water viscosity,
also without a number. Nominal 80°C alone is not an authenticated numerical input.
Consequently we report the fully recoverable coefficient **k/μ=GL/A**, the
published k±SD, and the viscosity **μ_implied=k_Table2/(GL/A)** needed to equate them.
Absolute reconstructed k stays explicitly unavailable. This inverse normalization
is not an estimate of physical viscosity, a fitted viscosity correction, or a
validation. Reading, averaging, regression orientation and unrecovered individual
geometry can all contribute to discrepancies. No new consistency gate applies.

## Claim limits

R(M) is omitted/absorbed into each series amplitude, assuming constant recovery
through an extracted-bed sweep. D0 line pressure is replaced by corrected bed ΔP.
An amplitude cannot correct a coordinate mismatch. A poor FA fit rejects transfer
of **this frozen D0 shape under these mappings**, not every form A parameterization
or opening mechanism. Different coffee, preparation, coordinates and measurement
systems remain competing explanations. No fresh-bed entry mechanism, intrinsic
pressure-only permeability, or population confidence follows from the figure.
