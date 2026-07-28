# Paper 2 — figure text alternatives

Each entry states what the figure shows and what the reader should take from it, so no finding is reachable only through the image.

## `fig1_machine_nonuniqueness`

Three panels on machine-side non-uniqueness. Panel a is a schematic of the Foster machine path: pump outlet, pipe resistance, trapped-air headspace, ponding height, wetting front and porous bed, with the four pressure nodes labelled explicitly. Panel b shows the reconstructed Foster normalised flow curve, which dips to a mid-shot minimum and recovers with no extraction-driven bed mechanism -- the bed state that does evolve is the wetted fraction, through sharp-front infiltration. Panel c shows the measured Waszkiewicz 9-bar rising-flow trace on its own axes, included only to establish that it is a separate evidence object that the Foster parameterisation does not fit. The take-away is that a machine-and-wetting system can generate a non-monotone flow shape, so a shape alone does not identify an extraction-driven bed mechanism.

## `fig2_null_first_ladder`

Four panels on the null-first temporal ladder over the 15 to 95 second scoring window. Panel a shows the measured 9-bar flow trace with the predictions of the best constant, the static pressure-dependent branch, the empirical temporal trajectory and the flexible cubic overlaid. Panel b is a horizontal bar chart of reconstruction error by branch, each bar annotated with how many free parameters were fitted to the scored trace; the temporal trajectory fits none. Panel c shows residual against time for every branch on the declared one-second grid, with the pointwise between-shot band drawn behind so residuals can be read against shot-to-shot variability. Panel d shows conditional moving-block intervals for the temporal branch minus the best constant, which excludes zero, and minus the cubic, which does not. The cubic is labelled a same-trace descriptive comparator, not a predictive model.

## `fig3_cross_pressure`

Four panels on cross-pressure assessment. Panel a shows per-pressure reconstruction error for the static, temporal and RC-3b branches against nominal pressure, with the band containing the primary 9-bar analysis marked; the best branch changes three times across the range. Panel b compares leave-one-pressure-out held-out errors, drawn with open markers, against shared-calibration errors for the same branches. Panel c shows the fitted equilibrium parameters when each pressure is omitted in turn, showing the calibration drift is small. Panel d shows the nominal setting against the recorded basket pressure at each condition, which is below nominal everywhere. The assessment is within-rig and conditional on a fixed dissolved-mass trajectory.

## `fig4_residual_structure`

Three panels showing that every branch leaves coherent low-frequency lack of fit. Panel a shows the autocorrelation of each branch's residual across twenty lags, decaying slowly for every branch. Panel b shows the share of residual power in the lowest-frequency quarter of the spectrum, above 0.95 for all four branches. Panel c shows where each residual spectrum peaks: the two static branches at the first nonzero Fourier period of the window, eighty seconds, and both temporal branches at the second, forty seconds. Those two values are properties of the eighty-point window rather than measured timescales, and the paper withdraws the earlier reading of them as physical periodicities. The take-away is that the residual power sits at the lowest frequencies the window can express, for every branch.

## `fig5_perturbation_matrix`

A declared prediction matrix with five candidate contributions as rows — machine and headspace response, dissolution-linked opening, fines migration and deposition, compaction and elastic recovery, and particle swelling — and five experimental perturbations as columns. Each cell states a directional or hysteresis expectation only. The figure is explicitly labelled as qualitative and conditional on the cited model structures: the repository contains no data from any of these protocols, so nothing here is a result.
