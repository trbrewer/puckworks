# Model card: visualizer.coffee shot corpus (data-only)

**Source:** visualizer.coffee public shot database + REST API (`openapi.yaml`
v1.13.0, base `https://visualizer.coffee/api`), Miha Rekar. A user-contributed
archive of espresso shots logged by Decent DE1, Meticulous, Beanconqueror,
Gaggiuino/GaggiMate and other machines; public read endpoints expose per-shot
hydraulic time series plus user-entered outcomes.
**Stage(s):** machine · flow · bed_dynamics (observational, cross-machine) ·
**Kind:** data-only (no model) · **Status:** data-only (intake ROADMAP 0.13)

## What the corpus is
A LARGE but UNCONTROLLED, self-selected population of real espresso shots. Each
public shot carries a shared `timeframe` vector with machine-logged
`espresso_pressure`, `espresso_flow`, `espresso_flow_weight`, `espresso_weight`,
temperature channels and their `*_goal` commanded companions, plus scalar
context (dose, drink weight, grinder model/setting, profile, roast) and,
optionally, user-entered `drink_tds` / `drink_ey` / sensory sliders. The
source-native payload is preserved under `brewdata`.

This is **not a controlled dataset**: shots are self-selected (showcase +
diagnostic skew), machines and sensors are uncalibrated across users, and there
is no independent groundtruth. It is harvested by
`puckworks/lib/visualizer_harvest.py` into a gitignored two-tier store
(`puckworks/data/visualizer/`, see its `PROVENANCE.md`). No physics is adopted
from it — there is no model here to run.

## Two evidence tiers (kept SEPARATE per ROADMAP §0; never merged)
1. **hydraulic time series** — machine-logged P(t)/Q(t)/weight(t)/T(t).
   Strength: **measured (machine-logged) but uncontrolled / self-selected →
   reference-strength POPULATION data**, NOT a controlled dataset. Commanded
   (`*_goal`) and achieved channels are separated; pressure node identity per
   §5.9; `espresso_flow` volumetric-vs-mass ambiguity flagged
   (`espresso_flow_weight` is the trustworthier channel).
2. **user outcomes** — user-entered TDS / EY / sensory ints. Strength:
   **user-entered, uncalibrated across users (unknown refractometer / sampling
   protocol) → NOT groundtruth**; hypothesis / cross-reference only.

## What it CAN serve (population / ecological, label rides along)
- **G3 pump-characteristic population** — an *ecological* achieved P(t)/Q(t)/
  weight envelope across many DE1 + non-Decent machines (not a single bench
  curve). Complements, does not replace, a controlled DE1 bench pull (G3 target).
- **P2 harness ecological hydraulic variability** — the spread of real achieved
  flow/pressure trajectories against which the κ(t)-ladder / cross-pressure
  fingerprints can be sanity-checked at population scale.
- **P6 Fo_F population** — a large sample for the Forchheimer-number distribution
  across real shots (reference-strength).
- **A PV / public "at-scale reality" companion** — the ecological backdrop for
  PV-06 (cross-pressure fingerprint) and PV-17 (pump-curve bench); a
  reference-strength companion whose label never upgrades a controlled result.

## What it CANNOT do (hard limits)
- **No groundtruth EY/TDS** — user outcomes are uncalibrated and sparse; they
  must never gate an extraction outcome (contrast the controlled Schmieder /
  Angeloni / Egidi sets).
- **No PSD / grind microstructure** — grinder *setting* is a non-portable dial
  (rule 9 / ledger A9/G5), not a particle-size distribution.
- **No basket geometry / bed state** — nothing measures the puck itself.
- **Selection bias** — public self-selected shots (showcase + diagnostic skew);
  a controlled bench tie-point (G3) is needed to calibrate the bias.

## Equations adopted
None. Data-only; no constitutive law or model is taken from this source.

## Overlaps and conflicts
- **foster2025_2 / waszkiewicz2025 brewer quadratic (machine stage):** those are
  single-rig *controlled* pump/pressure-drop closures; this corpus is their
  ecological population companion (many machines, uncontrolled) — it does not
  replace either and cannot be fitted as a machine closure without a controlled
  tie-point (G3). Commanded vs achieved must be separated.
- **DE1 fixture A (`de1_fixtureA`, held [RS]):** a single named DE1 trace; this
  corpus is the population that fixture is one draw from.
- **PV-06 / PV-17:** this is their at-scale ecological face; the evidence label
  rides along UNCHANGED (reference-strength, selection-biased).

Cross-links: ROADMAP §6 (validation data plan), §4 gap **G3**, §1 machine-stage
C-gate row, §5.8 (Miha Rekar correspondence — redistribution posture).

## Implementation estimate
No component. Intake is the harvester tool + gitignored two-tier store + the two
MANIFEST rows + the DERIVED `aggregate_stats.csv` — effort S (tooling, done at
0.13). No gate: a self-selected uncontrolled corpus is reference-strength
population data, not a validation set.

VERDICT: data-only — a large uncontrolled public shot corpus whose machine-logged
hydraulics are a valuable reference-strength ECOLOGICAL population (G3/P2/P6 envelope,
PV companion) but whose user-entered outcomes are not groundtruth and whose
selection bias, absent PSD/geometry, and commanded-vs-achieved split forbid any
promotion to a controlled validation — effort S (tooling only; no component, no gate).
