# PR #318: retained temporal-failure diagnostic and hosted-CI scope

This is a G0 documentation addendum to the existing G2 task,
`NO_GOVERNING_PHYSICS_CHANGE`. **IMPLEMENTED_QUALIFICATION_INCOMPLETE** and the
failed `resolved_temporal_decrease` gate remain unchanged. This explanation is
not a new espresso-model qualification or a reinterpretation of failure as PASS.
**RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED; runtime accuracy=NOT_ASSESSED.**

Analyzed PR/local head: `4b2fae76365d9cd3231c9a694307e5451321034a`.
Live main/base: `58b6cd2f29af3fa4372119ba59f8a6a1446369cc`.
Original qualification producer: `d691b055e8900f6547d4a5d4e5ec9f58f093bc8c`.
No material drift was found. The prior [independent nonhuman exact-head review
receipt](https://github.com/trbrewer/puckworks/pull/318#issuecomment-5983949960)
accepted an incomplete handoff, not numerical promotion or merge.

Only this note and [DIAGNOSTIC.json](DIAGNOSTIC.json) are added. Runtime code,
source parameters, checkpoint semantics, CONTRACT/CASES, RESULTS, HANDOFF,
resource receipts and EVIDENCE_REUSE remain byte-identical. All 28 original
receipt/array hashes and retained checkpoint hashes were rechecked against the
existing reuse manifest; corrected source-file identities also match. The
archive is attributed to its original producer, not to this documentation head.
The existing scoped data preflight is reused: no new original-source inspection,
corpus audit, assay access or protected-target access. Pannusch attribution and
source-derived CC-BY-NC-3.0 treatment remain separate from first-party licensing.

## Independent schedule calculation

Read History L and the unchanged fraction directly from CASES.json. The union
of forcing knots is `[0, 11.3, 17.2, 30]` s. Independently apply
`ceil((right-left)/h_max)` and `linspace` on each segment, then use each primary
step's midpoint for both Q and T. No candidate scheduling/helper function is
called. The reconstructed complete endpoint arrays equal the archives exactly.
Independent affine Q/T interpolation differs from archived values by at most
`8.48e-22 m^3/s` / `5.69e-14 K` over the full schedules; Q at the three owning
midpoints agrees exactly. These are floating-point arithmetic differences.

| h_max (s) | Segment step counts; total | Owning primary step (s) | Frozen Q/T sample time (s) |
|---|---|---|---|
| .04 | 283 / 148 / 320; 751 | [2.7151943462897528, 2.755123674911661] | 2.735159010600707 |
| .02 | 565 / 295 / 640; 1500 | [2.72, 2.74] | 2.7300000000000004 |
| .01 | 1130 / 590 / 1280; 3000 | [2.73, 2.74] | 2.7350000000000003 |

The fixed fraction `[a,b] = [2.737002188183808, 2.74]` s lies entirely in one
primary step at each level. Its midpoint is `2.7385010940919043` s and duration
is `0.0029978118161921863` s. In the first flow segment,

```
Q(t) = 1.2e-6 + ((2.8e-6 - 1.2e-6)/17.2)*t  [m^3/s]
Q_mean = Q((a+b)/2) = 1.4547442878225027e-6 m^3/s
V = (b-a)*Q_mean = 4.361049615572386e-9 m^3
```

The volume was also checked with exact rational arithmetic on the stored
binary64 inputs. The calculation is analytic and local, without subtracting
two shot-scale cumulative volumes.

| h_max (s) | Frozen Q (m^3/s) | Frozen T (K) | Q_frozen / Q_mean - 1 |
|---|---:|---:|---:|
| .04 | 1.4544333963349495e-6 | 356.78074204946995 | -2.1370868416925592e-4 |
| .02 | 1.453953488372093e-6 | 356.77389380530974 | -5.436003131474854e-4 |
| .01 | 1.4544186046511627e-6 | 356.7805309734513 | -2.2387657684330708e-4 |

For illustration only, let the outlet concentration be an exactly known
constant C throughout the window. The prescribed-volume fraction uses the
unchanged frozen-flow solute numerator, so

```
C_hat_h = Q_frozen_h * C * (b-a) / V
C_hat_h / C = Q_frozen_h / Q_mean_fraction.
```

Even with exact concentration fields, its absolute errors are nonmonotonic:
the .04 midpoint happens to be closer to the fraction midpoint than either
finer level's midpoint. The .02/.01 fraction ends at a primary boundary, while
the .04 fraction occupies a different position within its step. The grids do
not supply monotonic alignment with this short fixed window. This closed-form
illustration proves a mechanism, not a general convergence or accuracy claim.

Minimal independent reproduction of the schedule arithmetic (run from repo
root; no model imports, ODE solve or exponential action):

```python
import json, math
import numpy as np
from pathlib import Path
c = json.loads(Path("docs/analysis/model_pannusch2024_stateful_fv_004/CASES.json").read_text())
L = c["histories"]["L"]
knots = sorted(set(L["flow"]["times_s"] + L["temperature_C"]["times_s"]))
a, b = c["fraction_windows_s"][2]
q = L["flow"]["values"]
slope = (q[1] - q[0]) / L["flow"]["times_s"][1]
mean = q[0] + slope * ((a + b) / 2)
for h in c["reference_primary_h_s"]:
    for left, right in zip(knots, knots[1:]):
        edges = np.linspace(left, right, math.ceil((right-left)/h) + 1)
        for lo, hi in zip(edges, edges[1:]):
            if lo <= a < b <= hi:
                mid = (lo + hi) / 2
                print(h, lo, hi, mid, (b-a)*mean, mean,
                      (q[0] + slope*mid)/mean - 1)
```

## What retained numerical evidence establishes

Fixed scales remain `C*=9.172575 kg/m^3` and
`M*=9.434668779863144e-5 kg`. The following unchanged maxima were independently
recomputed from hash-checked archives, with exact timestamp intersections and
no interpolation. They match RESULTS.json exactly. Each level includes all
86 common observations and respectively 752/1501/3001 primary endpoints.
Phase/outlet/fraction errors use C*; accumulated mass uses M*.

| h_max (s) | Liquid | Fine | Coarse | Outlet | Accumulated mass | Fraction / aggregate |
|---|---:|---:|---:|---:|---:|---:|
| .04 | 6.72621e-5 | 1.73608e-6 | 2.49068e-7 | 1.12138e-6 | 7.77520e-7 | 7.990427627844573e-5 |
| .02 | 1.74297e-5 | 3.90519e-7 | 5.31831e-8 | 2.91680e-7 | 1.93186e-7 | 2.0291026776343948e-4 |
| .01 | 4.03240e-6 | 9.03053e-8 | 9.34535e-9 | 6.72980e-8 | 4.45797e-8 | 8.355956142298384e-5 |

The phase, outlet and accumulated-mass maxima decrease; the controlling tiny
fraction does not. All individual errors are below `5e-4`, but the aggregate
fails the separate decreasing-error requirement above `1e-10`. These facts
coexist; neither permits dropping the fraction or changing the aggregate.

The archive retains GL4/GL8 panels from the owning primary step's start to each
window endpoint, with both frozen-Q and actual-Q fluxes using the same candidate
concentration samples. Subtracting these two **step-local panel sums**, then
dividing by the same analytic volume, gives diagnostic values N_h and A_h:
N_h uses frozen Q; A_h uses actual Q. This is arithmetic on previously saved
samples, not new quadrature evaluation or a replacement public numerator.
The saved reference fraction is R=`3.4231492373694943 kg/m^3`.

| h_max (s) | Public fraction minus R / C* | (N_h - A_h) / C*, GL8 | (A_h - R) / C*, GL8 |
|---|---:|---:|---:|
| .04 | -7.99042763e-5 | -7.97547897e-5 | -1.49486615e-7 |
| .02 | -2.02910268e-4 | -2.02868350e-4 | -4.19181946e-8 |
| .01 | -8.35595614e-5 | -8.35494151e-5 | -1.01463450e-8 |

N_h agrees with the saved public fraction within `3.4e-16 C*` using GL8.
GL8/GL4 differences in either diagnostic are at most `1.36e-15 C*`.
The frozen-versus-actual weighting term accounts for about 99.81%, 99.98% and
99.99% of the signed discrepancies. Using R as the constant C in the illustrative
formula predicts `-7.97547820e-5 / -2.02868333e-4 / -8.35493777e-5 C*`.
Thus both the schedule calculation and the saved flux evidence strongly support
flow weighting as the dominant explanation on this window.

The remainder is **not a fully isolated chemical-evolution error**. Only the
two window endpoints are shared candidate/reference diagnostic timestamps
inside this window. Candidate outlet errors there are respectively
`[-1.491e-7,-1.501e-7]`, `[-4.044e-8,-4.359e-8]`, and
`[-9.587e-9,-1.090e-8] C*`, consistent with the decreasing remainder.
There are zero exact saved reference matches at the candidate GL panel nodes.
Radau's dense interpolant was not serialized. Original direct fraction
`window_parts` were not separately serialized either; the public fractions and
flux panels were. No missing reference values were interpolated or regenerated.
The remainder therefore combines chemical-evolution differences, reference
error and diagnostic quadrature error; their complete separation is unavailable.

No reporting or cancellation defect is demonstrated by this evidence. The
reference fraction is reproduced from its saved endpoint masses
`1.3252985729225271e-5` and `1.3267914252890948e-5 kg`, giving
`1.4928523665677136e-8 kg` delivery. Their binary64 subtraction is exact relative
to those stored values; a one-ULP perturbation of each endpoint contributes at
most `8.47e-14 C*`. This bounds representation sensitivity, **not Radau integration
or dense-output error**. The diagnostic panel subtraction condition ratios are
below 15.55 and the GL4/GL8 agreement is retained above. There is no evidence to
reclassify the failed gate as a reporting/reference defect, nor proof that every
possible reference error is absent.

Continuation and branching remain separate, already passing results: genuine
S/L stop/resume retains exact schedules and bitwise primary masses, and the
branch/reference worst normalized difference remains `4.68656135e-14`. This
diagnosis does not weaken or extend those claims.

## Hosted-CI and merge readiness

**HOSTED_CI_BLOCKED_BY_SCOPE.** Live API inspection on 2026-10-04 found zero
runs at the analyzed head and an empty PR check rollup. No workflow was launched.
The enforced main ruleset is `19053322`; the legacy branch-protection endpoint's
404 does not mean no rules apply. It requires an up-to-date PR and these GitHub
Actions contexts:

- `quick (3.10)` and `quick (3.12)`;
- `verify-generated`;
- `paper3-scope-strict` and `all-scope-strict`.

It also prohibits deletion/non-fast-forward updates. Required approval count is
zero and code-owner approval is not enforced by this ruleset; those settings do
not supply owner merge authorization. The PR remains draft and unmerged with
auto-merge disabled.

`gates.yml` runs on main pushes and PRs, has no `workflow_dispatch`/call input,
and selects `not slow and not live and not gpu and not external_data` for quick,
minimum-dependency and coverage jobs. That selector does not exclude
`protected_target_integrity`. `generated-artifacts.yml` likewise has no manual
trigger. `paper3-evidence.yml` does have manual dispatch, but can supply only its
two strict contexts. Its existence is not a route to the missing quick/generated
checks. The manual slow-science backstop selects protected tests and broader
science; packaging/security/other manual workflows do not supply the missing
required contexts. Rerunning another head would not check this code, and there
is no existing run at this head to rerun selectively.

Skip-CI markers remain necessary under current scope. GitHub documents that
they suppress push/PR runs and leave required checks pending; manual dispatch is
a distinct trigger ([GitHub documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)).
No skip marker was removed, selector or threshold changed, status manufactured,
ruleset bypassed, or protected test executed.

**Smallest concrete proposed remedy, not implemented:** owner authorization for
a task-scoped manual CI mode in the existing workflows. Add manual dispatch to
`gates.yml` and `generated-artifacts.yml`; in the explicit unprotected manual
mode, append `and not protected_target_integrity` to every pytest invocation in
the dispatched gates workflow, preserving the existing default mode, job names,
Python matrix, lint, mypy, coverage floor and timeouts. Pin/check the selected PR
head and identify the mode in its real run artifacts. Then dispatch those two
workflows plus the existing `paper3-evidence.yml` at the final head, retaining
skip-CI protection on automatic events. The owner must explicitly authorize
both that narrow trigger/selection change and the resulting unprotected hosted
QA as the required-context evidence for this PR. This proposal does not waive
protected QA globally, authorize its execution, guarantee CI passes, or authorize
merge. No such workflow modification is authorized by this closeout.

## Closeout and validation

New integrations: **zero**. Retained campaign: **28**, charged numerical work
**781.1377453766763 s**, **four unused correction slots**. The qualification
ledger and all historical result/identity artifacts are unchanged; saved-array
inspection and elementary diagnostic arithmetic do not constitute another
campaign. The diagnostic calculation imports no candidate/reference module.

Proportionate checks cover strict finite JSON, independent full schedule/forcing
comparison, archived receipt/array identities, exact reproduction of the
retained comparison maxima, analytic volume arithmetic, Markdown links,
private-path/secret checks, and a diff restricted to these two new files. The
calculation script and live API snapshots remain outside Git with hashes in
DIAGNOSTIC.json. A bounded independent nonhuman addendum for this interpretation
and the exact documentation head is recorded on PR #318; it does not reopen the
full implementation review. EWP and owner worktrees remain unchanged. No issue,
successor, release, merge or new numerical campaign is started.
