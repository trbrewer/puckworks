# Prescribed-temperature capability: qualification INCOMPLETE

MODEL-PANNUSCH2024-TEMP-HISTORY-001, issue #313. G2 /
NUMERICAL_METHOD_CHANGE. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The additive API is implemented, but the frozen full capability qualification
is **INCOMPLETE**. All 27 planned executions terminated successfully; successful
integration is separate from meeting the numerical allowances. Positivity,
three independent step-state comparisons, and the fixed discrete-budget
quadrature check fail. No threshold, parameter, grid, forcing, observer or
numerical setting was changed after these outcomes. No further full-bed run
was launched to rescue a pass.

## Separate numerical dispositions

All errors below use the frozen, fixed C*=c_s0, M*=continuum M0 and V*=Q*30 s.
Complete case/channel values, signed residuals, source/code/configuration
identities and execution receipts are in [RESULTS.json](RESULTS.json).

| Channel | Disposition | Worst relevant normalized value / allowance |
|---|---|---|
| Additive capability implementation | IMPLEMENTED; bounded small-mesh tests pass | New physical-state/segmented BDF path; both legacy APIs unchanged |
| Constant versus legacy fractions, four species | PASS | 2.39522e-6 / 1e-4 of C* |
| Steps versus independent ordered matrix exponential | INCOMPLETE | liquid: 1.57614e-6 / 1e-6 of C*; three species fail |
| Ramp fine/finer temporal agreement, both directions | PASS | 8.21549e-7 / 1e-6 of C* |
| Ramps versus independently assembled Radau | PASS | 8.39257e-7 / 1e-6 of C* |
| Physical continuum inventory residual, every new case/grid | PASS | 1.18777e-3 / 5e-3 of M* |
| Finest-grid fraction change, 200→400 | PASS | 4.58084e-10 / 5e-3 of C* |
| Independent outlet-flux temporal quadrature | PASS | 3.14776e-7 / 1e-6 of M* |
| Independent discrete weighted-budget quadrature | FAIL | 3.76480e-5 / 1e-6 of M* |
| Sampled physical concentration positivity | FAIL | liquid minimum -0.226906 C* versus -1e-6 C* |
| Hydraulic volume / repeatability / retained observers | PASS | Exact prescribed volume; repeated numerical arrays identical |
| Domain, clocks, units, partial/failure behavior | PASS in focused tests | Supported prefixes retained; unsupported/unresolved observers null |
| Software QA, hosted CI, independent exact-head review | SEPARATE | [Handoff](HANDOFF.md) and draft PR receipts |

For step liquid states: caffeine 8.41515e-7 (PASS), trigonelline 1.57614e-6
(FAIL), 5CQA 1.03882e-6 (FAIL), tds 1.37675e-6 (FAIL), against 1e-6 C*.
The step grain, mass, volume and fraction channels pass individually; the
largest step fraction discrepancy is 6.36438e-10 C*. These do not override
failed liquid-state agreement. Coarse temporal differences are diagnostic only,
as frozen; no default setting was selected after outcomes. The public default
remains the declared fine setting, whose full qualification is incomplete.

## What the accounting and positivity establish

The global continuum budget passes while local liquid positivity fails. The
worst recorded liquid value is -0.950734 kg/m³ for trigonelline at about
0.0546303 s, physical node 1. It is not the eliminated artificial inlet coordinate:
cl[0] is reconstructed as zero. Negative interior liquid states also occur in
the independent exponential and Radau solutions of the specified spatial
operator. No clipping or monotonicization was applied. Fine/coarse grain
concentrations remain positive on the checked samples.

These are adverse diagnostics of this declared source discretization/initial
condition, not an adjudication that historical Pannusch evidence is invalid.
The authorized scope preserves the source stencil. No conservative rewrite,
kinetic refit, state reset or corrective inventory flux was attempted.

The continuum initial inventory includes retained liquid. The trapezoidal
initial offset is recorded independently, never normalized away. For rising
caffeine at nz=200: M0cont=2.49896701897e-4 kg,
M0h=2.49749038454e-4 kg, offset=-1.47663443253e-7 kg.
Its maximum incremental residual is 7.81928e-4 M*, while the continuum
residual spans [-5.90898e-4, +1.91029e-4] M* and finishes at
+1.96055e-7 M*. Both initial and evolving terms therefore remain visible.

The independently derived weighted budget separates inherited transport/stencil
and pinned-inlet grain exchange. For that same case the final quadrature
contributions are +5.82221976481e-7 kg and -4.34633654997e-7 kg. Their
fixed temporal quadrature does not resolve the budget to the predeclared
1e-6 M* allowance; the finest-grid discrepancy reaches 3.76480e-5 M*.
The algebraic identity passes small-mesh random-state tests, but that does not
turn the failed full-trajectory quadrature diagnostic into PASS. The separate
outlet-flux integral and its prescribed sampling refinement pass.

Checks use accepted internal steps and quarter-step/refined dense samples for
production BDF, accepted Radau steps plus the fixed observation grid for Radau,
and exact-time observation samples for the exponential propagator. The 23
nonlegacy executions retain between 2,405 and 28,676 diagnostic samples each,
all on 0–30 s. Fixed 0.025/0.0125 s minima and knot-neighborhood observations
are retained. These are sampled checks, not all-time positivity certificates.
Unchanged legacy API diagnostics only cover its requested output times.

## Scope and evidence

Temperatures are caller-prescribed and spatially uniform, never a solved or
measured thermal field. Q=2e-6 m³/s is prescribed; the legacy equivalent is
1.96/1000.0/980.0, with the original operation order. The numerical flow domain
does not resolve the source's experimental flow convention or EWP mapping.
All fitted source parameters, grind entries, geometry and closures are fixed.
There is no new source fitting, experimental scoring, effect-size decision,
empirical prediction improvement, taste/yield claim or native-MATLAB equivalence.

Parameters/source equations are sufficient for this numerical capability;
experimental outcomes are not its inputs. Only the recorded MATLAB/source
material was read; original PDFs, archives, workbooks and observation rows are
not redistributed. Source-derived reports: Pannusch et al., J. Food Eng. 367,
111887, DOI 10.1016/j.jfoodeng.2023.111887; author repository DOI
10.17632/y2tz67f6ry.1, **CC-BY-NC-3.0**, separate from first-party software
licensing. Existing prediction targets remain source-internal and exposed.

No merge, auto-merge, release, adoption, EWP modification/native execution,
lock/default change, Foster/Grudeva/Cameron change, frozen scientific-result
restamp, laboratory work, author contact, acquisition campaign or successor.
