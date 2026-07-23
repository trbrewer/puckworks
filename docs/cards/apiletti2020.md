# Model card: Apiletti 2020 brewing time-series feature engineering

**Paper/thesis:** D. Apiletti, E. Pastor, R. Callà, E. Baralis, "Evaluating espresso coffee quality by means of time-series feature engineering," Proc. EDBT/ICDT 2020 Joint Conference Workshops, CEUR-WS Vol. 2578. No DOI (CEUR-WS.org/Vol-2578/DARLIAP5.pdf), CC BY 4.0.
**Stage(s):** observables · **Kind:** calibration (offline trace analysis; no physics executed)
**Status:** proposed

## Scope and mechanism
Data-mining paper, not a physics model. From the cumulative-water time series W(t) of a professional-machine double shot (flow-meter pulses at 300 ms), it detects a single "trend point" where the flow rate drops, approximates W(t) as a two-segment polygonal chain, and uses the two segment slopes (s1 = early-phase mean flow, s2 = late-phase mean flow) as quality features. Rectangular thresholds on (s1, s2), learned from labeled shots, classify "true optimal" shots and expose compensation effects (e.g., high dose + coarse grind passing volume/time thresholds) that whole-shot metrics miss. The authors interpret the two segments physically as (1) water being forced into the dry panel before the grounds resist flow and (2) the actual wetted-bed extraction phase — an empirical echo of the infiltration → saturated-flow transition, but with no mechanism modeled.

## Governing equations
All numbering per source.

1. Pulse-to-volume conversion (Eq. 1): q = num_p · pulse_q / num_c
   - num_p — flow-meter pulse count; pulse_q — volume per pulse (0.5 ml, machine datasheet); num_c — coffees per extraction (2; double shots). q is per-cup water volume, ml.
2. Point slope (Eq. 2): s_i = (q_j − q_i)/(t_j − t_i) for consecutive samples — instantaneous flow, ml/s.
3. Window mean slope (Eq. 3): w_k_mean = (1/(W−1)) Σ_{j=1}^{W−1} (q_j − q_{j−1})/(t_j − t_{j−1}) over a window of W samples.
4. Trend-point search (Algorithm 1): slide two consecutive non-overlapping windows [i, i+W), [i+W, i+2W) over all N samples; trend point = the intersection point maximizing trend_diff = w2_mean − w1_mean. Note the sign: it maximizes the *signed* difference, and since flow always decreases after the transient, the located maximum is in practice the most negative-to-positive... the authors do not discuss sign; as written, updateMax on signed trend_diff would find the largest slope *increase*. Given every trace shown decelerates, the intended (and evidently implemented) criterion is maximum slope *variation*; this card flags the pseudocode/text mismatch rather than resolving it.
5. Phase slopes (Eqs. 4–5): s1 = (q_tp − q_0)/(t_tp − t_0); s2 = (q_N − q_tp)/(t_N − t_tp), with p_tp the trend point, p_0 and p_N the trace endpoints.
6. Optimality box (Eqs. 6–7): T_o_min = (min oi_s1, min oi_s2), T_o_max = (max oi_s1, max oi_s2) over the labeled true-optimal set O; a shot is classified optimal iff (s1, s2) falls inside the box. Final fitted box: 5.19 < s1 < 5.48 and 2.64 < s2 < 3.73 (ml/s, this dataset only).

Nothing else is simplified away; there are no physical equations in the source.

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
|---|---|---|---|
| sampling interval | 0.3 | s | nominal (machine data logger) |
| pulse_q | 0.5 | ml/pulse | nominal (machine datasheet) |
| num_c | 2 | — | nominal (double shots) |
| W (window size) | 10 | samples (= 3 s) | assumed (no sensitivity study given) |
| s1 optimal box | (5.19, 5.48) | ml/s | fitted (min/max of labeled optimal set) |
| s2 optimal box | (2.64, 3.73) | ml/s | fitted (min/max of labeled optimal set) |
| corr(s2, avg flow) | 0.95 | — | measured (Pearson, n = 457) |
| corr(s2, brew time) | −0.94 | — | measured |
| domain thresholds (Table 1) | time 20–30 s, volume 20–30 ml, flow 0.67–1.50 ml/s | — | nominal (SCAE / INEI literature) |
| machine model, grind sizes, doses, pressures | not provided | — | — (proprietary; only labels coarse/optimal/fine etc.) |

## Calibration and validation offered by the source
Design: 3³ = 27 configurations (grind size × dose × pressure, each low/optimal/high) × 20 double shots = 540 extractions; 457 traces survive cleaning (30 hardware losses, 38 domain-threshold rejects at 10–40 ml / 10–40 s, 15 statistical outliers per their ref. [5]). Ground truth = knowledge of the machine settings, not sensory or chemical measurement. Results, in their numbers: of 67 shots passing classical volume/time/flow thresholds, 20 are true-optimal; the (s1, s2) box keeps all 20 true positives and discards 31/47 false positives (accuracy 76% vs 30%, precision 56% vs 30%); restricted to true-optimal + type-(ii) compensation (high dose + coarse grind), detection is 23/23 ("100%"). Caveats the authors do not dwell on: the box thresholds are the min/max of the training optimals evaluated on the same dataset — no held-out set, no cross-validation, one machine, one blend; the headline "30% → 100%" is on the favorable subset. Qualitative findings (Figs. 3–4): s1 separates cleanly into three clusters by pressure and is insensitive to dose/grind; s2 is insensitive to pressure and decreases with dose and with finer grind.

## Assumptions and validity range
- Exactly one flow break-point per shot; the polygonal chain has two segments by construction. Multi-phase profiles (preinfusion programs, flow profiling, channeling collapse) are outside scope.
- Fixed-volume-target professional machine at nominally constant pump pressure; not applicable to pressure- or flow-profiled shots (e.g., DE1 traces) without rethinking what the trend point means.
- Flow-meter resolution 0.5 ml at 300 ms; no scale (mass) data; volume ≠ beverage mass conversions unaddressed.
- Feature thresholds are machine-, blend-, and recipe-specific min/max envelopes; no transfer claim is made and none should be inferred.
- Silent on: pressure/temperature traces, TDS/EY, puck physics of any kind, single shots (num_c = 1), and the W-sensitivity of the trend point.
- Failure modes: signed-difference ambiguity in Algorithm 1 (see Eq. block); min/max boxes are brittle to a single outlier in the labeled optimal set.

## Interface mapping
Inputs consumed: a flow/volume trace — the `traces` field of ShotResultState (W(t) or flow(t)) suffices; no GrindState/BedState/MachineState fields are read in physical terms (settings enter only as categorical labels). Outputs produced: derived scalar observables (t_tp, s1, s2) and a categorical quality label — none of these is a current ShotResultState field. Couplings: none runtime. At most an offline observables-side trace-segmentation utility: the trend-point split is a cheap, implementable way to separate the fill/infiltration transient from the quasi-steady flow phase in measured traces (e.g., defining which portion of a DE1 fixture-A trace is fair game for fitting kappa or Forchheimer numbers). That is a ~30-line function, not a component; no adapters warranted.

## Extractable data
- Table 1 (domain quality thresholds): public-literature values, trivially re-derivable — not worth a data file.
- Final feature thresholds (s1, s2 boxes): machine-specific, meaningless without the undisclosed hardware — not transcribable.
- Raw dataset (457 traces): proprietary to an undisclosed coffee company; explicitly not published, machine and settings anonymized. Figures 3–6 are scatter plots in feature space without per-point settings values — digitization would recover nothing physical.
- Code: not published.

## Overlaps and conflicts
- **foster2025.infiltration (registered) / machine-mode backlog (Foster Eqs. 2–7):** complementary in narrative only. The observed two-segment trace — early phase governed by pressure (s1), late phase governed by bed resistance via dose and grind (s2) — is independent field-scale corroboration of the infiltration-transient → saturated-Darcy picture and of the pressure-node reasoning in the roadmap. But with no pressures, geometries, or grind sizes disclosed, it cannot serve as a validation dataset for either.
- **pocketscience2024 (registered data) / DE1 fixture A:** competes as trace-derived observables methodology; fixture A already provides higher-quality traces (P(t) and W(t), known machine) on which a trend-point split could be computed directly. This paper contributes the idea, not usable data.
- **cameron2020.extraction_bdf, brewer2026.*, wadsworth2026.*:** no contact — no EY, TDS, permeability, or microstructure anywhere in the paper.
- Backlog "observables: scale/measurement kernels": adjacent in spirit (flow-meter pulse quantization, Eq. 1, is a measurement kernel example) but the paper offers no kernel model.

## Implementation estimate
No component. If the fill/steady trace segmentation ever becomes wanted for fixture-trace preprocessing (e.g., Sprint 5 Forchheimer computation along fixture A), reimplement Algorithm 1 in-house (effort trivial, W-sensitivity check required, resolve the signed-difference ambiguity by taking |trend_diff| or the most negative difference). No gate design applicable — there is nothing physical to gate.

VERDICT: skip — a feature-engineering classifier on proprietary, unpublished traces with no physics, no transferable parameters, and no transcribable data; its one useful idea (two-segment trace segmentation) is a trivial in-house utility, and its qualitative pressure/dose findings only anecdotally corroborate what foster2025 and the machine-mode backlog already frame mechanistically — effort S
