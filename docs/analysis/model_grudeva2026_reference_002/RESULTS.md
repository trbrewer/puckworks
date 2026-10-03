# MODEL-GRUDEVA2026-REFERENCE-002 results

**COMPARATOR_QUALIFICATION_INCOMPLETE.** G2 / NUMERICAL_METHOD_CHANGE.
The modified reference route does not qualify as an independent oracle. No
merged-solver or reference-extraction defect was demonstrated; neither is changed.
The publication discrepancy remains unresolved. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

| Question | Result |
|---|---|
| Specified equations and source contract | Defined and source-audited; fixed flow, effective legacy coefficients, correct front grouping and fixed-z desaturation activation |
| Radial/front analytical qualification | PASS on declared fixtures; distinct from coupled qualification |
| Coupled D=0 front-passage limit | PASS; arrival 5.4416, relative error 4.66e-15, conservation 3.04e-15 |
| Alternate coupled canonical qualification | FAIL conservation, bed/time refinement; observation qualification incomplete |
| Baseline numerical qualification | Prior #308 bounded result reused after source and all six raw-result hash checks |
| Inter-backend agreement / earliest divergence | NOT ADJUDICATED; main comparison blocked by alternate qualification failure |
| Figure 3 / Figure 4 | Original baseline reproduction FAIL / FAIL, reproduced by offline scoring of unchanged saved runs |
| Figure 5 | FIG5_REFERENCE_INCOMPLETE |
| Software / hosted / independent review | Separate statuses in HANDOFF and exact-head PR receipt |

## What this adds beyond #308

The actual supplement E.2 was read, including E26–E33 and its fixed-z grain
grid / moving liquid grid interpolation. Its explicit radial method is not
implicitly qualified at D=1 by café-case success. The legacy effective
coefficients were verified: bf/(3Qf)=3.2 and bb/Qb=2.4, despite different bare
Q symbols. Its varying flow, dimensional clock, 32-second horizon and fitted
initial inventories are excluded from this canonical analysis adaptation.
Table 1's 310/224 remains separate from Table 2's 1.388; no alternative was run.

Conservative radial finite volumes with implicit time integration solve the
independent grain fixtures: at 3200 shells the worst flux/mean errors are
1.60048e-4 / 6.75608e-7, against 2e-4 / 2e-5. The 800/1600/3200 shell
sequence shows decreasing errors; time translation, uptake and equilibrium
pass. A manufactured moving-liquid profile tests the coordinate transform and
upwind transport algebra. Shell transfer balance in canonical runs is near
1e-15. Those checks do **not** qualify the coupled interpolation/transport route.

## Bounded coupled results

These are unqualified diagnostic computations, not alternative author results.
All use the same canonical physical inputs. Refinement comparisons use identical
physical times and exclude the whole interval between displaced outlet jumps,
with the unchanged .025 margin. None uses published pixels as a resolution target.

| Control change from 128 bed / 64 shells / dt=.001 | Max smooth outlet change | Arrival change | Outlet/event gate |
|---|---:|---:|---|
| Bed 256 | .0688874 | .00436563 | FAIL |
| Shells 128 | .000268512 | .0000889944 | PASS (these two observables only) |
| dt=.0005 | .00614770 | .00151419 | FAIL |
| Combined 512 / 128 / .0005 | .131527 | .0126793 | FAIL |

Normalized conservation residuals are .0117148 (normal), .00858353 (bed),
.0116983 (radial), .0113855 (time), .00593596 (combined), all above 1e-6.
The liquid/fines/boulder inventories are recomputed from saved actual liquid
nodes and fixed-z shell-weighted grain means, including untouched grain volumes.
This agrees exactly with the run observer. The integrals are exact for the
piecewise-linear nodal representation; their continuum quadrature error is
**not qualified**. They must not be described as exact conservative bed-cell
volumes. Cup quadrature differences are 1.20e-4–2.43e-4, also not qualified to
the prospective phase/cup budgets. No inventory is defined as M0 minus cup.

The first recorded conservation failure is already at t=.01, with s≈.001825
and a residual around -1.7e-5. This locates an **alternate-method accounting
failure at a sampled time**, not an exact first inter-method or publication
divergence. At that time the source integrated on the liquid grid differs
from the observed total boulder loss by about -6.9e-5 in the normal run.
At t=8 that difference is -.0809038. Local radial balance is near roundoff,
while the dual-grid transfer integral and bed balance do not close. This
implicates unresolved spatial transfer/transport and observation errors in the
adapted route. It does not uniquely establish an implementation defect in the
merged solver, the authors' actual run, or even the unmodified legacy port.

For normal at t=8, liquid/fines/boulder inventories are
7.70488e-7 / 2.46556e-6 / 1.37191e-6, totaling 4.60797e-6. Computed cup
inventory is 5.61704 versus M0=5.552: this is a failed numerical balance, not
extra extractable solute. Bed refinement's residual bed inventory is 1.86866e-6.
The final stored time for time_fine and combined is **7.975**, with bed inventory
5.13191e-6 and 1.33230e-6 respectively. Their t=8 observations are unavailable;
no extrapolation, complete-depletion claim or tail correction is made.

The 14-attempt ceiling includes two pilots, the analytical-limit run, four
initial canonical runs, two failed scheduler attempts and five final canonical
runs. Ordinary scheduler debugging stayed in this PR. A subsequent observation
audit fixed the remaining terminal-sample guard in the executable and adds a
small direct regression, but the cap prohibits another coupled run. Therefore
the current executable is **not numerically requalified** after that final fix.
RESULTS.json preserves each executed source identity and does not restamp runs.
Successful coupled execution took 29.87 seconds total; observed peak RSS was
580124 KiB (about 567 MiB), below the 2 GiB ceiling. The two failed attempts were
not individually timed; exact aggregate failed-run wall time is unavailable.
The full logs and source-at-execution copy remain outside Git.

## Publication and baseline preservation

Actual embedded Figures 3/4, axes, legend, jump and gray reduced curve were
inspected. Re-extraction from the configured local article reproduces **every
existing numeric coordinate and uncertainty**, and both embedded image hashes.
The local PDF container SHA differs from the originally used PDF; it is recorded
separately, without rewriting fixture provenance. No transcription or curve-ID
repair is justified. Raster bounds are extraction bounds, not Gaussian SDs.
The approximate 6.4 prose is not an exact arrival target.

Offline baseline scoring uses the unchanged whole-displaced-jump masks:
Figure 3 includes 9/19 concentration samples, excludes 10, unavailable 0;
all 3 declared fronts are scored. Figure 4 includes 5/8, excludes 3,
unavailable 0. The original maximum errors remain .09753/.01345 for Figure 3
concentration/front and .14133/.12085 for Figure 4 concentration/arrival.
Baseline arrival is 6.50430928764; raster arrival is 6.38345864662 with extraction
bound .0100251. This task supplies no new independent numerical reason for that
mismatch and does not reject the model or publication.

All six archived #308 scientific results and current remediation source bindings
match their recorded hashes. Original spatial/time/modal outlet changes remain
1.15501e-4 / 1.4110e-8 / 6.0180e-9; event changes remain
3.15612e-6 / 4.85486e-9 / 1.13366e-8. Summing the archived phase inventories
and cup confirms their original residuals. This is an **arithmetic reuse check**,
not a new independent audit of raw baseline cell states: those states are absent
from its Result archive, and no new instrumented baseline run was authorized
by the exhausted numerical matrix. Full-state cross-backend metrics, qualified
grain-history comparison and earliest inter-method divergence remain unavailable.

No production default, solver, registry, fixture, historical report, EWP file,
lock or tag changes. Issue #67 remains open/incomplete. No next task is selected.
