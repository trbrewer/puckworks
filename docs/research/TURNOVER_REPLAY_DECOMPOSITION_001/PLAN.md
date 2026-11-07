# Frozen-output decomposition

Base: `4c5ebab5df79929813949df7113c21290dde40cc`, fetched 2026-11-06.
Governance: G0 postprocessing of fixed, already exposed predictions and
observations; no new operator, fitted parameter, simulation or decision threshold.
The owner requests one fresh read-only review and required CI. No successor.

Read #424 at `ec82d1f019da3a5fcd9ff8748c29926c763d7bcc` and #423 at
`c4b4a07e110a3ede5013fd876a02a58ee6456eab`; neither must be merged. The 224
retained arrays were inspected and hash-checked: each contains `liquid_g`,
`solute_g` and `beverage_g` separately. In the inherited producer, `solute_g`
is cumulative discharged solute; `stored_solute_g` is a different internal
inventory and is not used. The historical definition is beverage = liquid +
discharged solute. This does not measure the real puck's water/solids split.

[INPUT_MANIFEST.json](INPUT_MANIFEST.json) records the pinned public sources,
retained private replay-index identity and each original per-array hash. The
retained index's plan/code/input/window identities must match #424's public
receipt. Its complete file hash is frozen here; #424 did not separately publish
that index file hash. No historical files are rewritten. Waszkiewicz
`traces_per_brew`, Zenodo 18046315, CC-BY-4.0, is the relevant registered source;
the actual retained arrays and native files are inspected, not just metadata.

Copy #423/#424's observation module byte-identically. The new runner's mass
observer must have exactly the same function source as #424's
`beverage_observer`, authenticated before use. Apply it separately to saved
liquid mass, discharged solute and total beverage mass: interpolation onto the
frozen clean native timestamps, gradient, 31-sample order-one Savitzky–Golay
filter, then the unchanged paired 2-s centered window. Native terminal masking,
observed-onset anchoring, support and window-mean achieved pressure are unchanged.
No fitting/simulation runner is called. Stable centers remain 10/20/30/40/60/100 s;
observed-onset centers remain 10/20/30/40 s. Detector non-detections cannot change
eligibility. Missing signals, support or reconstruction stop the decomposition.

Before interpretation, require liquid + solute = saved beverage mass and the
separate window contributions = every #424 beverage-window flow, with inherited
`rtol=atol=1e-12`. Recompute the saved total with the same operator as a separate
check. Record maximum absolute residuals and every attempted window. Verify
condition-mean and slope reconstruction against the public #424 tables too.

Aggregate equally across the same brews within each nominal condition. Report
all conditions, times, clocks, two models and both scopes. The unweighted slope
across nominal 9/11/13 conditions uses their frozen achieved window pressure;
use that same pressure for liquid, solute, total and observed flow. LOCO combines
different held-condition fits; DESCRIPTIVE_ALL remains a common in-sample vector.

Retain the three stable-clock phase increments (10→40, 40→60, 60→100 s) for
9/11/13 bar beside observed changes. For 60→100 s, subtract identically indexed
whole-brew draws and give inherited nearest-rank pointwise 95% intervals for
liquid, solute, total and observed increments. Reuse the exact 1,000-draw bank,
seed 20261106; verify brew order and hash, not only seed. No refit bootstrap.
Describe relative magnitudes and signs continuously; introduce no adequacy grade.

Figure: one 4×3 panel figure, model/scope rows and nominal 9/11/13-bar columns;
stable-clock liquid/solute flow contributions stacked, with observed beverage
flow overlaid. Both clocks remain in tables. Bind it to a task-local VizSpec.
New private per-window receipts stay outside Git. Measure CPU core-hours for
authentication/postprocessing/reporting; verification and CI are separately noted.
EWP, #424 artifacts, production defaults and historical results remain read-only.
