# Pressure atlas — pre-analysis specification v1 (WP2)

Committed BEFORE inspecting any sanctioned full export. Its hash (`spec_version` +
content) rides in every atlas output; post-hoc threshold changes must create a NEW
explicitly-versioned exploratory spec, not silently edit this one.

**spec_version: `pressure-atlas/v1`**

## 1. Question, population, unit

How well do espresso machines TRACK their commanded pressure, as an ecological
distribution over public shots? Unit of analysis = one shot; population = eligible shots in
a snapshot. Results are **tracking-behaviour distributions, NOT machine-quality rankings**
(source semantics are weak — WP2.8/Gate D).

## 2. Channels

Achieved `pressure__Pa`, commanded `pressure_goal__Pa` (both SI, pooling-safe). Flow is
OUT of scope until quantity kinds resolve (Gate E).

## 3. Time-series semantics (WP2.2)

- Commanded setpoint: **zero-order hold** between samples.
- Achieved: linear only WITHIN a valid contiguous interval.
- **Never interpolate across a gap** `> gap_threshold_s`. Such an interval contributes no
  weight (it is not bridged).
- All error summaries **integrate over TIME**, via trapezoidal node weights
  `w_i = Σ dt/2` over adjacent valid intervals. Sample-count summaries are diagnostics only.

`gap_threshold_s = 2.0`.

## 4. Active brewing interval (WP2.3)

Selection hierarchy: (1) a documented machine/state signal [not available in the public
window]; (2) a documented command phase [not available]; (3) **predeclared pressure-based
fallback** — samples with commanded goal `>= active_goal_bar`; (4) exclude when no valid
active interval exists. `active_goal_bar = 1.0`. Idle pre-roll and post-shot tails
(goal below threshold) get zero weight. The rule used is recorded per shot
(`active_interval_rule`).

## 5. Primary metrics (WP2.6), in bar, over eligible ACTIVE time

- `tw_mae_bar` = ∫|achieved−goal| dt / ∫dt
- `tw_rmse_bar` = sqrt(∫(achieved−goal)² dt / ∫dt)
- `tw_signed_bias_bar` = ∫(achieved−goal) dt / ∫dt
- `frac_time_within_0p5bar`, `frac_time_within_1bar` = ∫[|err|≤tol] dt / ∫dt

Physical-unit metrics are primary. Range-normalized RMSE is NOT primary (undefined/unstable
for constant-goal profiles); reported only as a diagnostic when the goal range is non-trivial.

## 6. Secondary diagnostics

`active_time_s`, `n_goal_transitions`, `command_shape`, `p90_abs_err_bar`,
`max_overshoot_bar`, `sample_rmse_bar` (sample-weighted — regression diagnostic only),
`lag_s` + `lag_corrected_tw_mae_bar`. **The headline uses UNSHIFTED series**; controller lag
is reported separately and never optimized away into an apparent perfect track (WP2.6).

## 7. Command-shape classes (WP2.5)

`constant` (0 transitions) · `single_step` · `single_ramp` · `declining` (monotone down) ·
`multi_step` · `complex`. A transition = `|Δgoal| ≥ transition_amplitude_bar` with a minimum
dwell; `transition_amplitude_bar = 0.5`. (Threshold sensitivity: PR5.)

## 8. Inference (WP2.7 — implemented in PR5)

samples ⊂ shots ⊂ users. Report all-shot descriptive distributions + a DETERMINISTIC
one-shot-per-user sensitivity (seed from snapshot + spec hash — store order must not matter;
PR4 makes the selection store-order-independent by choosing the lexicographically-smallest
shot id per user as a stopgap) + user-cluster bootstrap CIs (PR5). "First encountered shot"
is prohibited.

## 9. Eligibility & exclusions

Every excluded shot carries a stable reason token. Minimum active time
`min_active_time_s = 1.0` (a QC floor that drops degenerate sub-second traces; real espresso
shots are ~20s+, so it rarely binds — a stricter exploratory variant can raise it). Inclusion/
exclusion denominators are a first-class output.

## 10. Claims

Permitted: tracking-distribution description, operating-envelope coverage, ecological
association, hypothesis generation. Prohibited: machine-quality rankings, causal/mechanism
claims, latent-puck validation, source rankings without documented source semantics.

## 11. Provenance

Every final run emits: snapshot id + verification-receipt hash, this spec hash, code commit,
metric definitions, thresholds, inclusion/exclusion table, and a frozen-vs-exploratory mark.
A partial/moving corpus is stamped `EXPLORATORY — NOT A PUBLICATION SNAPSHOT`.
