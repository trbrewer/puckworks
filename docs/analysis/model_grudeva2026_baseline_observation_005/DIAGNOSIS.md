# 005 archive diagnosis: inlet and grain readout

**OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED remains
unchanged.** G1 / NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
This is diagnosis only: zero solver calls, full trajectories or recaptures.

The evidence supports an approximation limitation on the prescribed exact-average
family and differences already present in common-support stored grain means.
No implementation error in the declared three-cell reconstruction is demonstrated
at these points. Attribution to spatial evolution, modal truncation, temporal
error or a production implementation defect remains unresolved. Combined is a
finite numerical representation, not continuum truth. No correction is selected
or implemented, and this diagnosis does not authorize further execution.

## Unchanged qualification and exact inputs

Starting head/tree: `63cde4ca35af74c7b4998c9a3ef2209fd8911c50` /
`7082e059abf24febad7c76784155593882fb699f`; clean, same branch and draft PR #327.
Live main remains `45f594b92e6bed01f254158fa002ef82519fd5a6`. All 25 starting-head
hosted checks passed. The earlier CONTRACT, MATRIX, RESULTS, HANDOFF and
PERSISTENCE_SOURCE_DELTA are preserved byte-for-byte, as are the observer,
reporter, controller, runner and all 50 protected production/001–004 paths.

Only the successful normal-persistence and combined-persistence captures were
read. Their original metadata SHA256 values are respectively
`ed7f2963894fc1de625b181efa88f71a8f224eeb8e05cc18c47f85ed3779ff0e` and
`55994bcce4081171aa81c4a0c394cdaa01e9eb55082d97c55bd16addffe01a3b`.
All six original segment file/array identities and receipt bindings pass current
safe-reader validation. No historical corrupt segment was opened or combined
with another execution. Its historical cause remains UNRESOLVED.

The three original failures remain exactly:

| Requirement | Original maximum | Unchanged allowance | Location |
|---|---:|---:|---|
| Normal inlet | 2.046100506994386e-5 | 2e-5 | t=.2, z=0 |
| Normal/combined grain profile | 6.000191780015651e-4 | 2.3e-4 | t=6.51, z=.995 |
| Normal/combined grain history | 4.323872501288406e-4 | 2.3e-4 | t=5.875, z=.9 |

The other nine normal/combined refinement families and every original support
count are retained in [RESULTS.md](RESULTS.md) and [DIAGNOSIS.json](DIAGNOSIS.json).
They do not qualify the missing matrix. Normal/control neutrality and the normal
repeat remain unavailable. The earlier combined public-Result equality remains
repeat consistency only.

## Direct archive readout and independent implementation check

The unchanged observer evaluates both runs at identical absolute t and physical
z. No front or clock alignment is used. Full external output retains both fronts,
activation times, ages, segment provenance, cell/stencil indices, physical faces
and widths, reconstruction weights, all modal states/weights/rates/contributions,
and grain means. Compact stencil and arithmetic records are in DIAGNOSIS.json.

| Point | Normal grain mean | Combined grain mean | Normal age | Combined age |
|---|---:|---:|---:|---:|
| Inlet | .11727169323746728 | .11728664118209468 | .2 | .2 |
| Profile | .7963197196343996 | .7957197004563982 | .038450729357796476 | .038453647175098915 |
| History | .8978040998027808 | .8973717125526521 | .025888861110055394 | .02588758731724461 |

The inlet residual is negative; both grain comparison residuals are positive.
Independent grouping of the inlet sum and single-point versus original batched
readout produces last-bit differences: direct inlet residual
-2.046100506995774e-5, profile +6.000191780014541e-4, history
+4.3238725012861856e-4. These do not replace the original recorded maxima.
The original gates and masks are untouched.

The inlet and profile point meet the original grain-profile spatial/age mask.
The history point meets its original age-only history mask; it is inside the
profile's .008 front exclusion. This distinction is preserved, not used to
exclude its failing history. At the history time the fronts are
.9039513188596577 and .9039511501179931; neither is projected onto the other.

An independent polynomial solves the same three cell-integral constraints using
exact two-node Gaussian polynomial moments about the stencil midpoint. It does
not call cell_reconstruction to generate its expected values. Physical and
normalized coordinates, mode-axis ordering, integral preservation, and
reconstruct-then-weight versus weight-then-reconstruct agree. The largest
arithmetic discrepancy over the six point/stencil checks is
3.774758283725532e-15. Frozen scale/conditioning-aware arithmetic allowances range
from 1.0928108442716092e-12 to 2.984599493910259e-12; these are roundoff checks,
not added scientific error allocations. Fitted cell-center values differ from
input averages, as required for a curved field. Full signed residuals,
coefficients and conditioning are retained externally.

This verifies implementation of the declared local polynomial at these points.
It does not establish adequate approximation of the actual unknown field.

## Exact-average readout diagnostic with captured spectra

[DIAGNOSIS_PLAN.json](DIAGNOSIS_PLAN.json) froze support, sources and allocations
before the only invocation. The normal 128-cell/32-resolved-plus-tail and
combined 256-cell/64-resolved-plus-tail spectra use their actual weights/rates.
The historical three-mode fixture remains an unchanged control, not proof for
these faster spectra.

Prescribed motion is the existing s=min(.2*t,1), activation=z/.2, initial=1.388.
The two boundary families are zero and the existing .07+.1*age+.02*age².
For rate r and age u, the exact modal response is
A exp(-r u)+B+C u+.02 u² for the nonconstant case, with
A=1.388-.07+.1/r-.04/r², B=.07-.1/r+.04/r², C=.1-.04/r.
The zero case is 1.388 exp(-r u). Integrating these expressions gives exact
cell averages; expm1 evaluates exponential differences stably. No evolved
production error enters these averages. The unchanged reconstruction then
estimates the independently known point values.

The frozen 13 times span .01 to 8, including .2, 4.9, 5, 5.0001 and 5.02.
Positions include inlet, fixed interiors, near-front points and ages .001,
.01, .019, .02, .021, .05 and .2 where supported. Each family/mesh has
139 requested points: 84 age>=.02, 55 younger, zero unavailable. This is an
age-stratified fixture diagnostic, not the production comparison's spatial mask.
Literal floating-point support and age classification are retained unchanged.

| Spectrum/mesh | Forcing | Largest signed age-eligible error | Location | Exceedances / 84 |
|---|---|---:|---|---:|
| Normal | zero | +1.5813462830216451e-4 | t=5.0001,z=.99582,age≈.021 | 11 |
| Normal | nonconstant | +1.5032535646730683e-4 | same | 11 |
| Combined | zero | -2.2407707830018886e-5 | t=4.9,z=.9758,age≈.021 | 1 |
| Combined | nonconstant | -2.1299187327850078e-5 | same | 1 |

All are compared with the unchanged 2e-5 analytical/readout allocation. These
failures establish an approximation limitation on this declared family.
Unmasked raw-polynomial front errors at age zero are also retained externally;
the actual profiles function assigns INITIAL at an advancing front. Those raw
polynomial endpoint errors are not presented as failures of that assignment.

An independent adaptive quadrature check covers six predeclared cells/times and
selected resolved/tail modes: 18 modal averages per normal family and 24 per
combined family. Maximum observed discrepancy is 7.327471962526033e-14;
maximum reported quadrature error is 1.5409884563480766e-14. These numerical
uncertainty diagnostics are separate from reconstruction error; they are not
rigorous global error bounds.

At t=.2,z=0 the zero-boundary readout error is +9.129823811682147e-7
(normal) and +1.1309728129016428e-7 (combined): much smaller and opposite in
sign to the archived inlet residuals. The prescribed front at that time is .04,
whereas the archived fronts are about .033776; the interior forcing fields also
differ. Thus this fixture does not explain the canonical inlet discrepancy.
Near-front/just-post-exit fixture errors have relevant ages and comparable scales
to the grain reconstruction contributions below, but do not identify the entire
canonical error or turn combined into an exact reference.

## Decomposition relative to the combined representation

Let F_f be the piecewise quadratic reconstruction of combined weighted grain
cell means. Integrate it over each required normal cell, splitting at actual
fine-cell boundaries, to obtain A_c F_f. No cell-center quadrature, front
projection, inventory complement or renormalization is used. Every required
three-cell normal stencil has valid common-domain support at these three points.

R_c(B_c)-F_f = R_c(B_c-A_c F_f) + [R_c(A_c F_f)-F_f].

| Point | Total (mean-first arithmetic) | Common-average stored-field term | Re-averaging/reconstruction term | Closure residual |
|---|---:|---:|---:|---:|
| Inlet | -1.4947944627419218e-5 | -1.5738650584922663e-5 | +7.907059575290587e-7 | -2.5614276324970042e-17 |
| Profile | +6.000191780017872e-4 | +4.99151306082243e-4 | +1.0086787191954105e-4 | +3.144186300207963e-18 |
| History | +4.323872501313941e-4 | +3.812686329390881e-4 | +5.1118617192535964e-5 | -2.299592807841755e-16 |

The stored-field term accounts for most of both grain differences. The
reconstruction term is material, but removing it hypothetically would not make
the remaining relative stored-field terms fit 2.3e-4. This is not a proposed
correction or a revised acceptance score. Mean-first versus the original
mode-first total differs by at most 2.7755575615628914e-15.

The first 32 resolved modes share identical weights/rates. Their signed point
differences are -1.493729897618748e-5 (inlet), +5.974613460901832e-4 (profile),
and +4.3149759909035917e-4 (history). Normal tail minus combined additional
resolved modes and tail contributes -1.0645651247504456e-8, +2.5578319113117934e-6,
and +8.896510382602058e-7, respectively. Individual tail states are not equated.
These small direct tail-balance differences do not isolate modal truncation's
coupled effect on the shared evolved modes. Mesh, mode count and temporal
controls all differ; the missing single-axis rows prevent assigning causation.

The inlet gate combines evolved-state and reconstruction error against an
independent zero-inlet analytical value. Its name does not demonstrate an
observer code bug. Likewise a relative stored-field difference does not establish
a governing-physics or production-software defect. The evidence supports mixed
and incomplete attribution, with no specific scientific correction justified.

## Resources, reproduction and QA

One short invocation, grain-archive-diagnosis, completed in 7.108402908022981
seconds. Peak RSS=810110976 bytes; sampled VmPeak=986800128 bytes. Actual
RLIMIT_AS was [8589934592,8589934592]. Original controller, lock, threading,
host/cgroup/inherited-limit/storage preflight and 300-second ceiling were used.
Cumulative accounting is **3 full,20 short,558.8723420479655 numerical seconds**;
all starts are closed. No short slots remain. Old failures and original reserve
consumption are unchanged. No automatic retry or further trajectory is authorized.

The charged full diagnostic JSON (204341 bytes) has SHA256
`465525df7dde87cf3426ea028beb50def49c82c53c8d0e1d210320c0dd5e115c`.
DIAGNOSIS.json is a compact reduction of that saved JSON, with original gate
records and source/artifact/accounting bindings. Full arrays, logs and private
paths stay external. The historical RESULTS accounting is deliberately retained
as historical; current cumulative accounting is in this addendum.

Exact invocation within the existing configured evidence archive (shown for
reproduction only; no remaining short-slot authority):

```sh
"$EVIDENCE/venv/bin/python" "$EVIDENCE/invoke.py" grain-archive-diagnosis short development \
  "$EVIDENCE/venv/bin/python" -m puckworks.analysis.grudeva2026_baseline_observation_005_diagnosis \
  --runs-directory "$EVIDENCE" \
  --plan docs/analysis/model_grudeva2026_baseline_observation_005/DIAGNOSIS_PLAN.json \
  --allocation "$EVIDENCE/grain-diagnosis-allocation.json" \
  --output "$EVIDENCE/grain-diagnosis.json"
```

Exit 0 denotes completed diagnosis, never scientific qualification. Existing
attempt/output names are refused. New execution would require separate owner
resource authority; inspection of saved JSON requires no solver, archived code
or pickle.

Eight small algebra/serialization tests passed at current and supported minimum
dependencies before execution. Configured Ruff and mypy pass. Prior normal QA
and unchanged scientific tests are reused by exact identity; canonical archive
analysis was charged, not hidden in QA. Final-head CI and the existing independent
nonhuman review's diagnosis-only addendum are recorded separately on PR #327.
EWP and its lock remain unchanged; PR stays draft with auto-merge off and #67
open. No matched comparison, rescore, production repair, merge or successor.
