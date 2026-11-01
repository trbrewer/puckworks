# PRESSURE-PEAK: consolidated findings

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** This note consolidates existing results; it adds no analysis.

## The observation

Across 56 brews, flow peaks near 6 bar of measured line pressure. Above 9 bar, the measured decline is −0.0655 g/s per bar, with a wholly negative 95% interval of [−0.0880, −0.0403].[^observation] Stopping and restarting raises flow from 1.82 to 3.23–4.31 g/s; the cause remains unexplained.[^restart]

## What was ruled out

Strictly local, instantaneous compaction cannot produce the downturn: raising pressure adds non-negative permeability contributions to the flow integral, so flow cannot decrease.[^local] Tested swelling left the peak at too high a pressure. Trapped air reduced low-pressure error but made the decline too steep, and its flow and timing fits disagreed. Neither was a sufficient stand-alone explanation in the tested framework; other forms were not ruled out.[^mechanisms]

## Wetting

Observed first drip is fastest near 3.5 bar and generally gets slower above about 4 bar. The solver's simple Darcy wetting gives overlapping observed and simulated ranges at 1–2 bar, but its paired median first drip is 15.6 s too early at 13 bar. Both use time since stable pressure; observed onset also includes transport and detection lag.[^wetting]

## The best current explanation

C0's strongest working lead combines a threshold around 1 bar with whole-bed compaction on a pressure scale around 5–6 bar. It reduces low-pressure overprediction; its flow-only fit met or nearly met every scored criterion.[^c0] The joint constant-pressure peak remains at 7.00 bar against the observed continuous estimate of 6.1 bar: roughly a 1-bar offset. Fitted separately, flow peaks at 7.05 bar (fold range 6.80–7.20) and wetting is fastest at 4.55 bar (2.35–5.05); the single compaction law forces both to one pressure, which is why the joint fit compromises.[^c0-separated] Its onset curve is nearly flat. The shape limitation is structural: the same exponential compaction law ties the flow peak and onset minimum to the same pressure, although the observations place them apart.[^shape]

C1 found a lower-objective onset-only fit (4.870 vs 6.014), but it places P0 (1.294 bar) above the early pressure of four of the five 1-bar brews, so their onset is set by the fixed 0.01-bar denominator floor rather than by the onset law. C0's onset-only values are therefore not superseded by a better physical fit. See PRESSURE_PEAK_STAGE_C1/SUMMARY.md.

The threshold is the firmest new result: its 95% interval excludes zero in every fit (flow-only 1.163 [0.894, 1.339] bar; onset-only 0.542 [0.147, 0.759]; joint 1.296 [0.709, 1.323]).[^c0-threshold]

![Observed flow and onset with separate and joint C0 fits; reused without alteration](PRESSURE_PEAK_STAGE_C0/FIGURE.png)[^attribution]

Stage C2 (feasible onset threshold) gives a two-scale fit with a consistent local scale: flow peak 6.90 bar and onset minimum 4.55 bar, a separation close to the observed one but about 1 bar high at both ends. Flow and onset need different thresholds (about 1.3 vs below 0.9 bar), so the flow threshold is not a simple wetting-entry pressure; see PRESSURE_PEAK_STAGE_C2/SUMMARY.md.

## What C3a and C3b add

At 1 bar, the detector's 0.1 g/s flow criterion fires last in 4/5 brews, compared with 0/51 elsewhere. Halving the detection thresholds moves the fitted onset scale Pd from 3.98 to 3.65 bar and the plug-in flow peak about 0.25 bar lower. That peak keeps the saved flow parameters; it isn't a flow refit. The slow 1-bar onset is partly a detector effect, but most of its slowness remains.[^c3-detector]

Smoothing the hard flow threshold with an exponential threshold distribution makes every in-sample screen worse. All three versions over-predict flow at 1, 2 and 3.5 bar.[^c3-smooth]

Applying the detector to the model's own flow (T3-O) leaves 4/5 held-out 1-bar onsets censored at the record end: the fitted flow threshold, 1.10 bar, exceeds their usual line pressure. Including the 1-bar onsets in the fit lowers the threshold to about 0.74 bar, but held-out 2-bar flow is over-predicted by +0.38 g/s. The open problem is the low-pressure flow law: the 1-bar brews flow at roughly 0.1 g/s below thresholds that fit 2 bar and above. C3b's other fits had unstable finite-difference Jacobians, so its 6.45-bar peak isn't an established result.[^c3-observer]

A single lagging whole-bed state isn't supported by these checks. The traces want no resolvable lag, and no tau in the tested range gives more than about 1.25 times the initial restart flow, against the observed 1.75–2.35 times. Flow ratchets up after each restart, and pause flow rises from about 0.10 to 0.20 g/s across successive pauses. That points toward an irreversible change, but it's one qualitative record. The replay's zero flow during pauses is a simplification.[^c3-restart]

## The CFD demonstration

The E1 mechanism was reproduced in the fluid-flow solver. At nominal constant pressures, after accounting for wetting delay, its largest endpoint difference from Python is about 2.4×10⁻⁵ g/s; its peak remains at 7.714 bar.[^cfd] The solver added the wetting front, geometry and measured pressure histories, exposing the first-drip mismatch; it did not remove the misplaced peak.[^cfd]

## Limits

This is one rig and one coffee protocol, fitted and assessed retrospectively. Run order and dates are unavailable, so drift cannot be tested. Good retrospective capability is not independent validation or proof of a physical cause.[^limits]

## Open questions

- Could separate pressure scales describe wetting and flowing-bed compaction?
- What irreversible change happens at each pressure cycle?[^c3-restart]
- What low-pressure flow law fits 1 and 2 bar together? Only nine brews constrain it.[^c3-low-pressure]
- Is the threshold pressure a capillary/trapped-air entry effect, and would it change with grind or basket?

Data: Waszkiewicz et al. (2025), CC-BY-4.0. Figure: reused C0 analysis of those data.[^attribution]

[^observation]: [PRESSURE_PEAK_STAGE_A/SUMMARY.md:5](PRESSURE_PEAK_STAGE_A/SUMMARY.md#L5); line-pressure convention in [PRESSURE_PEAK_STAGE_B0/SUMMARY.md:11](PRESSURE_PEAK_STAGE_B0/SUMMARY.md#L11).
[^restart]: [PRESSURE_PEAK_STAGE_A/SUMMARY.md:26](PRESSURE_PEAK_STAGE_A/SUMMARY.md#L26).
[^local]: [PRESSURE_PEAK_STAGE_A/SUMMARY.md:9](PRESSURE_PEAK_STAGE_A/SUMMARY.md#L9).
[^mechanisms]: [PRESSURE_PEAK_STAGE_B0C/SUMMARY.md:45–62](PRESSURE_PEAK_STAGE_B0C/SUMMARY.md#L45-L62); [PRESSURE_PEAK_STAGE_B0D/SUMMARY.md:30–47](PRESSURE_PEAK_STAGE_B0D/SUMMARY.md#L30-L47). These are failures of the tested forms, not general impossibility proofs.
[^wetting]: [PRESSURE_PEAK_STAGE_B0C/SUMMARY.md:3–12](PRESSURE_PEAK_STAGE_B0C/SUMMARY.md#L3-L12); EWP [docs/demonstrations/E1_CAPABILITY/SUMMARY.md:23](https://github.com/trbrewer/espresso-whole-pull/blob/569f3579ffa5ad607e05ec11b405a4771cd3f130/docs/demonstrations/E1_CAPABILITY/SUMMARY.md#L23) and [FIRST_DRIP_BY_PRESSURE.csv:12](https://github.com/trbrewer/espresso-whole-pull/blob/569f3579ffa5ad607e05ec11b405a4771cd3f130/docs/demonstrations/E1_CAPABILITY/FIRST_DRIP_BY_PRESSURE.csv#L12), rounded paired median.
[^c0]: [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:18–34](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L18-L34). The approximate threshold and compaction scale describe the flow-only and joint fits.
[^c0-separated]: [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:36](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L36).
[^c0-threshold]: [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:24–28](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L24-L28).
[^shape]: [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:34–42](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L34-L42).
[^c3-detector]: [PRESSURE_PEAK_STAGE_C3A/SUMMARY.md:5–7](PRESSURE_PEAK_STAGE_C3A/SUMMARY.md#L5-L7); per-condition counts in [RESULT_TABLE.csv:58–68](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L58-L68), saved primary onset Pd and x0.5 point fit/plug-in peak in [RESULT_TABLE.csv:70–71](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L70-L71), and paired 1-bar onset times in [RESULT_TABLE.csv:2–6](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L2-L6).
[^c3-smooth]: [PRESSURE_PEAK_STAGE_C3A/SUMMARY.md:11–20](PRESSURE_PEAK_STAGE_C3A/SUMMARY.md#L11-L20); signed condition residuals for all three screens in [RESULT_TABLE.csv:95–97](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L95-L97).
[^c3-observer]: [PRESSURE_PEAK_STAGE_C3B/SUMMARY.md:9–25](PRESSURE_PEAK_STAGE_C3B/SUMMARY.md#L9-L25); full-cohort, 1-bar and 2-bar fits in [RESULT_TABLE.csv:6–8](PRESSURE_PEAK_STAGE_C3B/RESULT_TABLE.csv#L6-L8), including flow thresholds, held-out endpoint residuals, observed flows and line pressures. The low-pressure conflict describes these tested fits, not an impossibility proof for every flow law.
[^c3-restart]: [PRESSURE_PEAK_STAGE_C3A/SUMMARY.md:22–28](PRESSURE_PEAK_STAGE_C3A/SUMMARY.md#L22-L28); episodes and replay bounds in [RESULT_TABLE.csv:99–113](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L99-L113). The tau search covered 0.1–1000 s under both off-state pressure assumptions.
[^c3-low-pressure]: Five 1-bar brews and four 2-bar brews in [PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv:58–59](PRESSURE_PEAK_STAGE_C3A/RESULT_TABLE.csv#L58-L59).
[^cfd]: EWP [docs/demonstrations/E1_CAPABILITY/SUMMARY.md:6–23](https://github.com/trbrewer/espresso-whole-pull/blob/569f3579ffa5ad607e05ec11b405a4771cd3f130/docs/demonstrations/E1_CAPABILITY/SUMMARY.md#L6-L23).
[^limits]: [docs/cards/waszkiewicz2025.md:54](../cards/waszkiewicz2025.md#L54); [PRESSURE_PEAK_STAGE_A/SUMMARY.md:7](PRESSURE_PEAK_STAGE_A/SUMMARY.md#L7); [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:3](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L3).
[^attribution]: [PRESSURE_PEAK_STAGE_A/SUMMARY.md:28](PRESSURE_PEAK_STAGE_A/SUMMARY.md#L28); [PRESSURE_PEAK_STAGE_C0/SUMMARY.md:32](PRESSURE_PEAK_STAGE_C0/SUMMARY.md#L32). Figure reused from that C0 result, with no changes.

The mechanism search is paused by the owner. No successor stage is authorized.
