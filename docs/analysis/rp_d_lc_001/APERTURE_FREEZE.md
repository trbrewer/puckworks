# RP-D-LC-001 — APERTURE FREEZE (step 2 of the blinded design)

```
SELECTED FROM COUPON OUTPUT ONLY
NO FULL-FIXTURE R, s OR Xi-hat WAS INSPECTED BEFORE THIS FILE WAS COMMITTED
```

The rule below was declared in the driver before the coupon sweep ran and is applied
mechanically; the driver refuses to re-select once this file exists, and refuses to run
`--mode primary` until it does.

## Rule

> From the coupon-predicted Xi at S_COARSE, over candidates with kz >= 2 (kz = 1 is a 2-lattice-unit feature at S_COARSE, ~12 % element error under the measured 50/h^2 law): take the candidate with the LARGEST Xi_coupon strictly below XI_WINDOW_LO; the candidate with the SMALLEST Xi_coupon strictly above XI_WINDOW_HI; and, inside the window, the candidates nearest to three log-spaced targets between XI_WINDOW_LO and XI_WINDOW_HI (geometric quartiles), deduplicated. Ties break on smaller kx then smaller kz. Selection is sorted by Xi_coupon ascending.

## Coupon calibration (S = 2)

| quantity | value |
|---|---|
| `a_coupon` (high segment) | 62.688422 |
| `b_coupon` (low segment) | 23.641142 |
| `c_coupon` | 0.452305 |
| window | 0.241134 … 3.945980 |

## Selected apertures

| kx | kz | `G_bridge_coupon` | `Xi_coupon` | in window | why |
|---|---|---|---|---|---|
| 3 | 2 | 6.045357 | 0.140053 | no | largest coupon-predicted Xi strictly BELOW the window |
| 3 | 4 | 20.310732 | 0.470539 | yes | nearest coupon-predicted Xi to log-target 1 (0.4850) INSIDE the window |
| 5 | 4 | 50.705593 | 1.174698 | yes | nearest coupon-predicted Xi to log-target 2 (0.9755) INSIDE the window |
| 9 | 3 | 78.339162 | 1.814886 | yes | nearest coupon-predicted Xi to log-target 3 (1.9619) INSIDE the window |
| 9 | 4 | 174.546264 | 4.043719 | no | smallest coupon-predicted Xi strictly ABOVE the window |

Coupon-predicted cases inside the window: **3**.

If the assembled fixture then misses the target, the disposition is
`DESIGN_MISSED_TARGET` — a second post-hoc aperture set is **not** selected in
this frozen execution.

## All candidates considered (kz >= 2)

| kx | kz | `Xi_coupon` |
|---|---|---|
| 1 | 2 | 0.020515 |
| 1 | 3 | 0.035497 |
| 1 | 4 | 0.049470 |
| 3 | 2 | 0.140053 |
| 5 | 2 | 0.282107 |
| 3 | 3 | 0.305511 |
| 7 | 2 | 0.438854 |
| 3 | 4 | 0.470539 |
| 9 | 2 | 0.611860 |
| 5 | 3 | 0.693420 |
| 5 | 4 | 1.174698 |
| 7 | 3 | 1.183622 |
| 9 | 3 | 1.814886 |
| 7 | 4 | 2.247862 |
| 9 | 4 | 4.043719 |
