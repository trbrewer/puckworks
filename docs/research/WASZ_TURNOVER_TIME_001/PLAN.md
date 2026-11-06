# PW-WASZ-TURNOVER-TIME-001 — frozen descriptive plan

Frozen before computing new observations or outcomes, 2026-11-05. Base:
`4c5ebab5df79929813949df7113c21290dde40cc` (fetched main). This is one bounded,
no-fit description, authorized through a draft, unmerged PR. No successor,
production change, historical-result change, EWP write, or model fitting.

## Inputs and observations

The underlying originals were inspected and their hashes authenticated against
FORM_A's retained source-input file and manifest. [INPUT_MANIFEST.json](INPUT_MANIFEST.json)
freezes those identities, the normalized Stage A inputs, inherited code and
read-only EWP references. Same 56 distinct brews and eleven nominal conditions
as Stage A / JOINT_CLOCK / FORM_A; exclude only the existing `12-8-6_alt` alias.
Counts at nominal 1, 2, 3.5, 4, 5, 6, 7, 8, 9, 11, 13 bar are respectively
5, 4, 3, 10, 5, 6, 4, 4, 5, 4, 6. No new exclusions or relabeling.

Attribution: Waszkiewicz, Myck, Białas, Puciata-Mroczyńska, Dzikowski, Szymczak
and Lisicki (2025), Zenodo [18046315](https://doi.org/10.5281/zenodo.18046315),
CC-BY-4.0 data. Use existing independent Puckworks reduction code; do not import
the deposit's GPL programs. These openly licensed brew summaries may be released.
No chemistry or sensory data enter this check.

Reuse `pressure_peak_stage_b0.raw_trace`, `clean_course`, and `sustained_onset`.
Stable pressure starts at the sample after the last out-of-band pressure sample
among the first 501; tolerance is median pressure ± min(10%, 0.5 bar).
`clean_course` retains native samples from that origin through the sample before
the inherited first post-100-s pressure departure (> max(0.5 bar, 10%)) or mass
drop >5 g. It then differentiates mass with `np.gradient(mass, t)` and applies
the inherited 31-sample, first-order Savitzky–Golay filter. No new filtering.
Target is measured beverage-mass-derived flow, with **line pressure** from the
same recorded interval; no basket/puck-pressure reconstruction.

The mass baseline is median mass at stable-pressure −2 to 0 s (first mass only
if that interval has no samples). Waszkiewicz onset is the **start** of the
first native-sample interval with baseline-relative mass >0.5 g AND smoothed
flow >0.1 g/s sustained ≥2 s. Replay FORM_A's saved onsets exactly. An undetected
onset remains unavailable, never imputed. This differs from the Visualizer
predictor's first reported weight >1 g onset.

## Fixed clocks, support and averaging

- Stable-pressure times: **10, 20, 30, 40, 60, 100 s**.
- Detected-onset times: **10, 20, 30, 40 s**.
- Every observation averages a **2-s window centered on its declared time**.
  Use the time integral of piecewise-linear native filtered flow divided by
  2 s, and the identical operator on native line pressure. Interpolate the two
  window boundaries only inside genuine recorded support, never extrapolate.
- Native times must be finite and strictly increasing. The entire bracketing
  sample span must have finite, unmasked flow and pressure. Reject unavailable
  windows explicitly; do not turn course-loader padding into observations.
  Use native courses directly, not the padded course arrays or fitting masks.
- Stable-pressure windows retain supported pre-onset data. No onset+2-s cut,
  flow flatness, positive-flow selection or new pressure/flow threshold.
- Report all 56 × 10 attempted brew windows and all 11 × 10 availability cells,
  including missingness reasons and counts; compute means from available brews
  at each time. The cohort remains 56 even if a window lacks support.

## Exact reference prerequisite

Before producing time-series outcomes, use Stage A's unchanged `load_brews`
with its normalized `endpoint_100s` target and final normalized line pressure.
Reproduce the eleven historical observed condition means/achieved pressures,
the unweighted 9/11/13-bar slope and observed maximum, checking against the
committed Stage A table and EWP SCI-MD-010 diagnostics (absolute tolerance
1e-10, relative tolerance zero). Reproduce the historical Stage A descriptive
bootstrap using its original seed 20261029 separately. **Stop on mismatch**.
This reference is a single endpoint, not the new 99–101-s mean; equality of
those two different observation operators is neither expected nor required.

## Descriptive statistics and uncertainty

Within each nominal condition, average paired window flow and achieved line
pressure over the same available brews. The high-pressure slope is the
unweighted OLS slope across the **three condition means** at nominal 9/11/13 bar,
using their matched achieved window pressures. A missing high-pressure condition
makes the slope undefined. Do not use Stage A's final-pressure pairing for the
time series and do not fit a response model.

Report the **observed maximum among condition means**, enumerating exact ties
(no new tolerance), whether it is at an available-range edge, and all missing
conditions. With missing conditions this is explicitly only the maximum among
available condition means, not a complete eleven-condition maximum or located
peak. Ratio = 13-bar condition mean / that maximum; undefined if the numerator
is unavailable or denominator missing/nonpositive.

Generate **1,000 whole-brew-within-condition resamples once, seed 20261106**,
in sorted nominal-condition order and frozen Stage A brew order. Reuse these
same sampled identities for every time on both clocks, keeping each brew's
flow, pressure and onset together. At a window, unavailable sampled identities
remain unavailable; average the remaining sampled occurrences. Never redraw
to replace missing data. Report finite-draw counts; a draw with no samples in a
required group is undefined. Recompute condition means, maxima (including ties),
ratios and slopes within every draw. Record the draw-bank hash and maximum
selection frequencies. Intervals use Stage A's nearest-rank 2.5/97.5 percentiles
over finite draws; these are descriptive, pointwise intervals, not a new grade.

Paired changes use those same draw indices: **later minus earlier** for adjacent
declared times within each clock, and **stable-pressure 100 s minus each time**
on either clock. The latter is a cross-clock reference for onset snapshots:
there is no additional onset-100-s observation. Report both point changes and
intervals; do not subtract independently computed interval bounds. Report
paired condition-flow changes too, to distinguish lower-pressure increases
from 13-bar decreases. No refits, weights, extra times, tuned windows or models.

## Reporting and verification

Publish the requested five CSVs plus per-brew windows, this plan, input hashes,
half-page numbers-first summary, reproduction instructions and one figure:
condition-mean flow versus achieved line pressure, a curve per declared time,
one panel per clock, stable 100 s highlighted. Missing support is explicit;
curves connect observed condition means, not fitted functions. Task-local VizSpec.

Focused tests: exact Stage A reproduction; matched pressure/flow windows;
no masked or padded samples; shared resample identities across clocks/times;
synthetic stable-pressure and onset clocks (interval start, strict thresholds);
availability and undefined maximum/ratio handling. Run required repository CI
and obtain a fresh read-only reviewer check of clocks, pairing, availability
and claims. Record measured analysis CPU core-hours separately from CI.

Interpret slope/maximum evolution and per-condition trajectories together.
Observation time may contribute to the Visualizer difference, but pressure
node, coffee, machine and brew style also differ. Preserve B0b's distinction
between a cross-pressure decline and flow declining within a brew. No common
mechanism, compaction, causal-law, universal-peak or validation claims. Limit
inference to these brews and declared snapshots. No successor is started.
