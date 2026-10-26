**Retain empirical decay B for this conditional prediction use.** V is slightly worse: its loss exceeds B by **0.003621 bar**, paired 95% CI **[0.002547, 0.004736]**. V therefore does not earn further development on this comparison. This is a resolved, small predictive disadvantage under the stated assumptions, not a refutation of viscosity physics or an application-adequacy judgment.

**Plain-English summary (87 words):** We built a new pressure predictor and tested each of eleven shots using parameters fitted to the other shots. Every predictor received the same early pressure readings and measured flow and temperature. Both fitted responses improved on carrying forward constant resistance, but ordinary exponential decay narrowly beat the viscosity-shaped response. Flow-sensor drift substantially changed the size of the improvement. These results favor the simpler response for further conditional prediction work. They do not reveal what caused the pressure decline or establish accuracy on another coffee or session.

Primary losses, **sqrt(mean of shot time-weighted MSE)**, are **V 0.794766, B 0.791146, N 0.918321, W 0.964404 bar**. These predict the absolute level of machine gauge pressure, not thermodynamic absolute pressure.

| Pair | Loss difference, bar [paired 95% CI] | Gain, % [paired 95% CI] | CI bands |
|---|---|---|---|
| V/B | 0.003621 [0.002547, 0.004736] | −0.458 [−0.624, −0.323] | worse |
| V/N | −0.123555 [−0.166906, −0.086575] | 13.454 [8.752, 18.796] | small, moderate |
| B/N | −0.127176 [−0.171653, −0.088973] | 13.849 [9.041, 19.291] | small, moderate |
| V/W | −0.169638 [−0.222487, −0.125335] | 17.590 [12.095, 23.556] | moderate |
| B/W | −0.173259 [−0.226850, −0.127931] | 17.965 [12.357, 24.019] | moderate |
| W/N | 0.046083 [0.037431, 0.056415] | −5.018 [−6.577, −3.704] | worse |

Coverage is **11/11 physical shots**, each with 24 anchor samples at 42≤t<47 and 134 evaluation samples at 47≤t≤75: 264/1,474 observations, statistical **n=11**. Native midpoint-cell quadrature spans each complete window; no pressure interpolation, future-maximum selection, grinder inference or outcome mask occurs. Late measured Q/T make this conditional replay, not autonomous machine forecasting. All eleven accessible external copies match tracked SHA-256s; original sensor calibration/custody is not authenticated. Published logs have no explicit redistribution license; only code and aggregates are added.

All Gagné shots and used prior means are **TARGET_EXPOSED**; this split is retrospective, never blind. Q is showerhead mL/s, its integral logged volume, and P/Q apparent machine resistance, not permeability. Basket °C is converted to K. No independent TDS(t) exists; historical EY is percent dry dose, and ±0.03/0.01 TDS-pp assay errors are not pressure errors. Telis-Romero is fitted industrial-extract evidence: Xw uses mass percent, domain 76–90%, 295–365 K. All selected temperatures (365.44–370.00 K) extrapolate; allowed dilute tails also extrapolate. Latent C is never measured TDS.

All **1,000** seed-20261026 shot-weight bootstrap replicates completed, with **14,426** independent dynamic refits and **zero invalid replicates**. Every copy of the evaluated identity was excluded. These approximate same-session, shot-exchangeability intervals condition on observed anchors/Q/T and omit unknown sensor systematics; they are not calibrated for another coffee, operator, grinder or session. [Shot scores](SHOT_SCORES.csv) include MAE, signed bias, worst error, normalized resistance error and conditional training-refit uncertainty; [comparisons](COMPARISONS.json) include influence and all nine boundary combinations. V/B remains worse under every classification; deleting any one shot only from the score reduction preserves that ordering.

Both coordinates remain fitted in every fold: base-512 jaxgsa ST estimates exceed 0.01, with bootstrap intervals reported. Every primary fit reaches the lower a bound; this is not physical identifiability. Bounds were not expanded. Coherent −20%/+20% Q drift changes B/N gain to **1.539%/29.126%**; B still beats V. Setting h=1 for both fitted families retains that ranking (V/B −0.326%); W retains its definition. These are systematic scenarios, not additional datasets/CIs.

The tighter optimizer changes aggregate loss by at most **3.71e−11 bar**, below the frozen 0.001-bar target and recorded 0.01-bar increment; independent reduction agrees. This is not sensor accuracy. Numerical executions took **249 seconds**: 131 corrected, 118 preserved superseded. One review-driven correction repaired jaxgsa's base-size argument, an input guard and sensitivity-control reporting; no model search occurred.

Reproduce numeric aggregates from the source checkout with research-only `jaxgsa==1.3.1` (Python ≥3.12): `python tools/gagne_conditional_pressure.py --private-output OUTSIDE_REPO --output NEW_BUNDLE`. [PLAN.json](PLAN.json) fixes input hashes and methods; detailed arrays remain private.

**One next task:** authenticate one existing transfer cohort using retained VIS-EWP-PLAY-002 `COHORT_DEFINITIONS.json` and `COHORT_MEMBERSHIP_PLAY_002.parquet`, specifically native Q/basket-T semantics and 42–75-s support, before freezing B-versus-N transfer. Both records are accessible and hash-verified; a compatible named campaign is not yet authenticated. No new experiments or same-data tuning are proposed. No viscosity causation, latent chemistry, EWP validation or P1 blind-TDS closure follows; **P1 remains OPEN**.
