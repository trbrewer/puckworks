# PW-LC-JOINT-TRANSFER-001 — pre-fit specification

Owner-authorized execution through an open, unmerged draft PR. G1 retrospective
capability comparison; TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
PW base: `4c5ebab5df79929813949df7113c21290dde40cc` (fetched main). Since the
reviewed `2e0486c` pin, only the separate cup-time-increment study changed; no
inherited hydraulic, observation, or source artifacts changed. EWP remote main is
`67bead2a25bd7e61c16c4fe2c104d885d8d26dd9`; its FORM_A evidence is read-only.

**Question/expectation.** Does existing LC capacity with J1's unchanged clock,
recovery, chemistry and beverage observer improve held-out low-pressure flow and
detector onset, retain high-pressure response, and reduce COR15 shape mismatch?
Flow-only LC previously worsened 1 bar; D0 sometimes gave near-step openings with
3.5 bar withheld. A negative 1-bar answer is plausible. No rescue model or retuning.

**Models.** P=max(raw line pressure,0) in bar, q in g/s, outlet liquid M in g.
H_n=1−exp(−(P/Pd)^n); C_A=a Pd H_n exp(−P/Pstar);
C_LC=a Pd [(1−f)H_n+f(1−exp(−P/Pd))]exp(−P/Pstar).
Both use x_f/L=min(1,sqrt(t/tau0)), inherited fully wet state at tau0=0,
M=q=0 before breakthrough and dM/dt=C(P)exp(−exp(−M/Mc)) thereafter,
M(tau0)=0. No fitted scale lag. Filling/storage, dissolved carryover, geometry,
viscosity, 256-cell R0 chemistry and observer are unchanged. Inlet water, wetting
and dissolved mass never advance M; pre-outflow recovery stays exp(−1).

Replay the 48 matching saved A-J1 fits without optimization. LC-J1 vector is
**(a,Pstar,n,Pd,f,tau0)**: only a/Pstar/Pd logged, n/f linear, only tau0/100.
Before fitting verify f=0 nesting, f=1 n-redundancy, n=1 f-redundancy and tau0=0
at inherited rtol=1e-12, atol=0. Exact boundary redundancy and practical
identification are distinct; compare capacity curves when n is weakly constrained.

**Data/folds.** Authenticate the same 56 Waszkiewicz brews, eleven conditions,
alias exclusion and all support (Zenodo 18046315, CC-BY-4.0). Ordinary eleven
whole-condition LOCO folds plus DESCRIPTIVE_ALL; no omission twins. Fixed Mc is
the matching inherited C2 T2-F parameters_by_fold value, cross-checked against
every A-J1 FITS.csv row with source hash/key recorded. No Mc refit or pooled seed.
Underlying source files and retained configurations must authenticate before use.

**Objective/search.** Exactly 4 weights (.05,.5,1,2; 1 primary) ×12 =48 new fit
problems. Inherit equal-condition/equal-brew joint objective, flow normalization
.437 g/s, onset normalization 4.534 s, fixed flow masks and detected/censored
losses. These normalizers are not noise estimates; shared histories do not form
independent likelihoods. Inherit timestamps, gradient/31-sample filter, strict
mass>.5 g/flow>.1 g/s for two seconds, clean support and censor horizon.
Missing/corrupt evidence is unavailable. Reproduce A-J1 objectives and frozen
.005-s scores before interpreting differences.

Bounded Powell xtol=1e-4, ftol=1e-7, no iteration/evaluation/time cap;
a [.001,20], Pstar [.5,100], n [1,infinity), Pd [.1,100], f [0,1], tau0 [0,100].
Each fit has 19 ordered starts: matching saved A-J1 at f=0; matching C3E
record_type=fit/candidate=LC/ordinary fold plus A-J1 tau0; same LC with tau0=0;
16 Latin-hypercube starts seed 20261103 in transformed domains, initial n [1,8].
Exclude OMIT-3.5 twins and D0 refits. Same LC seed at every weight; retain
duplicates. Total **912 scheduled starts**. Keep the lowest finite evaluated
objective, including starts. Preserve all failures, starts, boundaries and
competing vectors; selected objective must not exceed its f=0 embedded benchmark.
Use the verified exact-prefix evaluator and one BLAS thread per worker; record
actual CPU hours, including failures/interruptions. Large traces/trials stay external.

Fit at .02 s; frozen reporting at .005 s with .02-s sensitivity. For every selected
fit also set f exactly zero with common parameters unchanged: 48 frozen diagnostics,
no refit. Report saved A-J1, LC-J1, frozen-zero objectives and selected f together.
Use inherited C3E objective-disagreement scale 1e-6*max(1,Jbest) and the .005−.02
objective change to judge resolution. A frozen-zero improvement can expose a better
feasible A solution; LC versus its frozen zero isolates only a fixed-parameter term
effect, not globally optimized family differences. Preserve unresolved attribution.

**Waszkiewicz reporting.** Both arms/paired changes at each weight: common-mask
endpoint/primary/companion flow RMSE; full-cohort onset RMSE or computed bound;
intended/available/detected counts; per-brew/per-pressure signed errors, all five
1-bar brews and separate 1/2/3.5 results; inherited low-pressure summaries and
within-2-bar ratio (zero denominator undefined), brew 1-2 and 3.5 residuals;
9/11/13 response, slope, peak/trend values and existing per-metric grades.
Keep out-of-fold slopes distinct from descriptive curve slopes, global capacity
maxima (all stationary candidates and endpoint limits), finite-time flow maxima,
front and detector minima. Use 23-pressure/100-s descriptive sweeps per weight;
retain ties/boundaries/multiple extrema. Use identical 1,000 condition-then-whole-
brew resamples, seed 20261103, conditional on frozen fits/fixed Mc. A difference
of computed censor bounds is not a bound on true-error differences; show counts.
D0/B1/prior joint predictions are labelled context on compatible masks.

**Corrochano, outside fitting/selection.** Freeze each weight's descriptive
A-J1 (n,Pd,Pstar) and LC-J1 (n,Pd,Pstar,f) before external calculation. Reuse
COR15's exact 108 means, twelve unequal-length series and reading contract;
P_bar=plotted corrected bed pressure Pa/100000, Q=upstream-meter m³/s. No second
loss subtraction, line-to-bed correction or mass conversion. Only one positive
Q-space least-squares amplitude per series per shape, units m³/(s bar); L0=GP
also retained. D0 FA is historical context, never the primary control. Constant
recovery absorbed in amplitude is an assumption. No history/onset reconstruction.
Use fixed central S_s²=mean(Q²); D(X−Y)=mean_s[(MSE_X−MSE_Y)/S_s²] for
LC−A, LC−L0, A−L0. Identical 4,096 graphical realizations, shared calibration,
seed 20261104; refit amplitudes only, paired arithmetic inside each realization.
Intervals describe graphical readings conditional on shapes, not populations,
equivalence or noninferiority. Report dimensional RMSE/all signed residuals.
A-480's lowest point ~1.41 bar differs from others' .23–.42 bar. All pressures
~.23–4.5 bar: this tests opening shape/Pstar curvature, not peak/high-pressure/onset.

**Closeout.** Answer four primary questions separately (low-pressure flow;
detector timing/detection; high-pressure retention; external improvement against
both A-J1 and L0), with continuous values and existing MEETS/NEAR/MISSES grades,
no overall PASS/new margin. Sensitivity-only gains do not establish primary
success; beating A externally while losing to L0 is partial progress. No causal
meaning for f or physical-validation claim. One hydraulic/onset figure and one
twelve-series COR15 figure; compact fit/Mc/prediction/paired/numerical/provenance
artifacts and commands. Reuse campaigns without increasing campaign counts.
Run focused checks and required CI; obtain a fresh read-only independent review
after completion and fix concrete defects. Stop on essential unavailable evidence
or unreproduced A-J1 rather than substituting. Draft PR stays open, unmerged,
auto-merge disabled. EWP, production defaults and historical results stay unchanged.
