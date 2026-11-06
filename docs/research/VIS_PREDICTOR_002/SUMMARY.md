# PW-VIS-PREDICTOR-002

**455 reset-flagged shots excluded: a post-hoc observation correction motivated
by #421.** The retained **10,231 unflagged shots / 315 users / 159,466 windows**
have unchanged observations and original fold IDs. C0 reproduces **1.2084042519
g/s RMSE / 1.6547408860 NRMSE**, with zero per-window difference from 001's cache.
The original 001 result remains unchanged.

**M0R is the recommended reference predictor:** **0.828045 g/s RMSE / 1.172328
NRMSE**, versus AR 0.828771, L0R 0.960932, R0 0.989432, T0 1.117731 and C0
1.208404 g/s. M0/A without recovery score 1.051583/1.051436 g/s. M0R's five-fold
RMSE range is **0.769–0.983 g/s**. On **2,783 pressure-varying shots / 221 users**,
M0R remains best: **0.975451 g/s / 1.954443 NRMSE**, fold RMSE range **0.844–1.234**.

Paired overall differences, with 95% complete-user bootstrap intervals, are
**M0R−R0 −0.161387 [−0.229560, −0.078129] g/s** and **AR−M0R +0.000726
[−0.001819, +0.004133] g/s**. The downturn adds no aggregate predictive gain here.
M0R−R0 is negative in all overall folds; on pressure-varying shots it averages
−0.166661 [−0.268559, −0.029166], but reverses in one fold. L0R−T0 is −0.156799
[−0.266804, −0.013338]; L0R−R0 is −0.028500 [−0.134301, +0.110353].
[RESULTS.md](RESULTS.md) reports all eight contrasts and fold variation.

On **identical survivors**, 001's full-cohort fits versus 002's filtered fits give
M0R **1.174363→0.828045** and AR **3.086366→0.828771 g/s**. M0R selects n=1,
Pd=3.46–4.29 bar and Mc=4.57–4.77 g, a saturating pressure shape with early mass
progression. AR has three in-range finite peaks, one out-of-range peak and one
exactly monotone fold. Bound contacts describe the curves; they do not disqualify them.

M0R struggles more on rising-pressure windows (1.084 versus falling 0.841 g/s)
and supplied-flow disagreement (1.408 g/s). Direction dependence is not proof of
a time artefact. **6,158 negative-increment shots remain eligible.** Unknown weight
authority, self-selection, residual noise and conditional pressure/mass inputs
limit transfer; these results establish no physical mechanism, puck pressure,
causal law, universal peak or physical validation. The correction is post hoc.

All **35 CV fits + seven deployment refits** are saved; deployment is excluded
from scoring and recommendation. Recorded CPU: **35.499 core-hours**, including
28.713 CV and 5.893 deployment optimization. All numerical audits passed.
Data source: Visualizer; thanks to the contributing public-shot users.
