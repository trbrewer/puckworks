# RP-D-LC-001b — pre-execution scientific review

```
PRE-EXECUTION AUDIT — decides whether computation may begin; produces no scientific result
NO RP-D-LC-001b LATTICE-BOLTZMANN SOLVE HAS RUN
```

This is the audit the freeze exists to be checked against: apparatus, similarity law, conserved
quantities and negative controls, examined **before** any computation. It states what I believe is
correct, what remains a genuine risk, and my explicit recommendation.

> ## ⚠ TWO REVIEWS HAVE HAPPENED, AND BOTH RETURNED **NOT APPROVED**
>
> §11 audits the first (`bbf2304`, C0 → C1); **§12 audits the second (`2cf0b63`, C1 → C2) and
> supersedes §11 where they differ.**
>
> Exact-head review at `bbf2304665d09cb78c117353947ce8c6cf2e5d24`:
> **`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_CORRECTION_REQUIRED`**.
>
> **The common-mode-port apparatus — the design decision §3 flagged for adversarial attention —
> was ACCEPTED IN PRINCIPLE.** Twelve other blockers were not. They are corrected under
> `PREFLIGHT-C1`; see `PREFLIGHT_ERRATA.md` for each superseded clause and why it was unsafe, and
> `PROTOCOL.md` §19 for the effective protocol. **§10 below is superseded by §11.**

---

## 1. Audit — the conserved quantity

**Finding: the defect is closed, and closing it required no solver change.**

001's control measured `Σ u_x`. In a weakly compressible LB solver the conserved quantity is
`Σ ρ u_x`, and the `ρ` fields needed to form it were never retained, so `mass_conservation` was
`NOT_EVALUATED` and fail-closed (erratum E4b). The frozen proxy separately **failed** at `S = 3`
(1.028e-3 against 1e-3).

001b retains both at every required plane. Three things make this a real closure rather than a
rename:

1. **It is measurable with the existing component.** `lb_reference.solve` already exports
   `rho`, `uy`, `uz` (RP-D.1, proven bit-identical). `Σ ρ u_x` needs `rho` and `ux`; `Σ ρ u_y`
   needs `rho` and `uy`. **No solver change, no new component, no card, no registry entry.** I
   checked this against the live implementation rather than assuming it.
2. **The two are separated by role, not by wording.** `sum_rho_ux` is `adjudicative_conservation`;
   `sum_ux` is `diagnostic_and_inverse_input`. The decision reads the mass form. The volume form is
   retained for continuity with 001 and can never, on its own, decide an execution — asserted by
   test.
3. **The inverse contract is untouched.** `R` and `s` are still built from pressure-normalised
   **volume** flux. Silently swapping in mass flux would have changed the quantity WP6's inverse was
   verified against; that is not done, and no Route-B or new pressure component appears.

A unit test makes the distinction bite rather than merely declaring it: a uniform velocity field
with a density ramp conserves volume flux **exactly** while the mass flux drifts. The volume proxy
passes; the mass control fails. That is 001's failure mode in miniature, and the new control sees
what the old one could not.

**Residual limitation.** `Σ ρ u_x` is a *plane sum of node quantities*, not a flux integral through
a curved surface; on a flat lattice plane with a frozen fluid-node set the two coincide, but this is
a lattice-level conservation statement, not a continuum one. Recorded as such.

## 2. Audit — dimensionless similarity

**Finding: the law is correct, exactly representable, and testable before output.**

For a Stokes slot `u ~ g L²/ν` and `Re ~ g L³/ν²`, so at fixed lattice `g` and `ν` with `L ∝ S`,
`Re(S=3)/Re(S=2) = 3.375` — 001's E5 finding, reproduced here as a test on 001's own constants so
the contrast is demonstrated rather than asserted. `g(S) = g_ref (S_ref/S)³` makes
`Re_design = g L³/ν²` invariant, and it is invariant **exactly** in floating point:
`4.096e-3` at both resolutions.

- **`ν = 0.5` is confirmed, not assumed.** The test reads
  `nu = (tau_plus - 0.5) / 3.0` out of `lb_reference.solve`'s source and checks it against
  `TAU_PLUS = 2.0`.
- **The ladders are exact.** Constructed as rationals, so `5.925925925925926e-7` and
  `1.1851851851851852e-6` are the true `float` values of `2.0e-6 · 8/27` and its double, not rounded
  literals that would drift apart.
- **The reduction is ×10 at `S = 2` and ×33.75 at `S = 3`**, inside the ×8–10 guidance and
  strongest exactly where 001 failed hardest.

**Ex-ante prediction, offered as a prediction and not as a result.** If the observed drift is
first-order in the forcing, then 001's worst componentwise spreads scale to

| S | 001 `Q/g` spread at `g = 2e-5` | scaled to the 001b central forcing | tolerance |
|---|---|---|---|
| 2 | `2.38e-4` | `2.4e-5` | `1e-4` |
| 3 | `3.96e-4` | `1.2e-5` | `1e-4` |

— margins of ~4× and ~8×. **This must be demonstrated by 001b's own ladder.** If the drift is not
first-order in `g`, the prediction fails and the execution is invalid; that is the point of running
the ladder rather than assuming the scaling.

The same reduction shrinks the total pressure drop, hence the density variation, hence the
volume-versus-mass discrepancy — the shared remedy 001 identified for E2 and E4. Again: predicted,
not claimed.

**Residual limitation.** Holding `Re_design` fixed does **not** hold the Mach number fixed (it falls
as `1/S`) and does not hold the element-level discretisation error fixed (that is what §5 is for).
Similarity here means *one* dimensionless group, chosen because it is the one 001 failed to hold and
the one the creeping-flow assumption depends on.

## 3. Audit — negative-control physics

**Finding: the geometry is the right kind of fix, and its adequacy is measured, not asserted.**

The honest statement of what topology can and cannot do:

- **Topology can prove** there is no through-conduit: the bridge occupies a bounded `x` interval
  whose neighbours are solid across the entire divider cross-section. That is proven on the mask.
- **Topology cannot prove** the absence of a *parallel detour* conductance. 001's aperture already
  had solid axial end caps; end caps were never the problem. The problem was that the void was open
  to both lanes **along its whole length**, so it acted as extra channel in parallel with the lanes.

001b attacks the actual mechanism in two ways:

1. **The connection is recessed.** The divider is a three-layer structure; the duct that joins the
   lanes sits behind the lane-facing ports rather than being them. An axial detour into a port must
   turn around and leave through the same port, which in Stokes flow is a very high-resistance path
   compared with a pocket that is open along its length.
2. **The ports are common-mode.** They exist in the blocked fixture too, so the blocked/open
   difference is exactly the connecting duct. `R` therefore compares the *same axial network* with
   `G_lat` off and on — which is what the two-node model's `R` *means*.

**Is (2) identical-path subtraction in disguise? No, and the distinction matters.** Subtraction
would take a defective geometry's output and correct it arithmetically. Here nothing is subtracted,
fitted or post-processed: a physically constructible reference apparatus (a fixture with two blind
pockets) is built for a physically constructible open apparatus (the pockets joined). Every
observable is measured on a real fixture. The 001 decision's prohibition — *"identical-path
subtraction is not an equivalent safe option"* — is about correcting a defect after the fact, and it
is respected. **This is the single design decision I most want a reviewer to challenge**, and it is
flagged in the PR for that reason.

**Both port and duct dimensions are still small compared with the lane**, so I expect the residual
artifact to be well under 001's `1.4e-2`. I do **not** claim it will be under `1e-3`. That is what
P1 measures, on 48 solves, per candidate, at both resolutions, before any mirror case is run —
and a candidate that misses is rejected. If **every** candidate misses, the tranche stops as
`DESIGN_BLOCKED_PRE_EXECUTION` rather than proceeding.

### Artifact-budget derivation

`ARTIFACT_BUDGET_R_ABS = 1.0e-3`, taken from the repository's established **0.1 % observable-level
nuisance scale** — numerically identical to `TOL_RETURN_PATH_R_REL`, frozen in 001 erratum E1 for
the Route-A isolation gate, itself derived from the programme authorization's 0.1 % criterion
applied to the observables the WP6 inverse consumes. **It is not chosen by looking at any 001b
output**, and it is used as a **ceiling**: smaller is strictly better, and every candidate's
measured artifact is reported whether or not it passes.

Its scientific cost is bounded before execution. With `K = c²/(1−c²)` and `ε = (R−1)/K`, the inverse
gives `Ξ = ε/(1−ε)`, so a `1e-3` artifact perturbs `Ξ̂` by

| window end | `Ξ` | signal `R−1` | amplification `1/(1−ε)` | relative bias in `Ξ̂` |
|---|---|---|---|---|
| low | `0.241134` | `0.02003` | `1.241` | **6.2 %** |
| high | `3.945980` | `0.08225` | `4.946` | **6.0 %** |

Under a tenth of the factor-of-two criterion, across the whole transition window. For scale: 001's
measured artifact of `1.428e-2` would have biased `Ξ̂` by ~85–90 % — comparable to the criterion
itself. **A looser budget is not adopted and would need a fully pre-output justification and an
explicit review flag; none is offered because none is needed.**

## 4. Audit — the reachable-set margin

**Finding: correct, conservative, and it admits the whole target window.**

The forward map `R − 1 = [c²/(1−c²)]·[Ξ/(1+Ξ)]` is the repository's own
(`WP6-LC-IDENT/DECISIVE_EXPERIMENT.md` §7), not a fresh derivation, and the ceiling is its
`Ξ → ∞` limit. A unit test round-trips it through the **verified inverse**: for several `(c, Ξ)`,
the `(R, s)` the map produces invert back to the same `Ξ` — so the gate's arithmetic and the
inverse's arithmetic are demonstrably the same mathematics.

| term | source | value at the expected `c_field ≈ 0.3218` |
|---|---|---|
| `c_gate` | P0 reference-blocked `c_field`, reduced 5 % | `0.30571` |
| ceiling `K` | `c_gate²/(1−c_gate²)` | `0.103094` |
| safety margin | `0.10 · K` | `0.010309` |
| artifact bound | measured in P1 | `≤ 1e-3` by admission |
| numerical uncertainty | `TOL_MASS_REL`, at full value assuming **no** common-mode cancellation | `1e-3` |
| max admissible `Ξ` | | **7.375** |

The WP6 window tops out at `3.946`, so the whole target range is admitted with real headroom — an
**ex-ante demonstration that a credible path to satisfying this gate exists**, which is the
precondition for authorising computation at all.

**Why the margin is `0.10·K` and not a token.** `d(ln Ξ)/d(ln ε) = 1/(1−ε)`, so capping `ε` at
`0.90` caps the inverse's relative-error amplification at **10×**. That is a conditioning statement,
derived, predeclared, and independent of any 001b number. At the window's top the amplification is
already `4.95×`; the margin keeps every admitted candidate below `10×`.

**Non-circularity of `c_field`.** It comes from the P0 **reference-blocked** fixture — no bridge, no
open case, no mirror output. The 5 % allowance is applied because the ports perturb the lane
conductances; since they sit in the transition band, symmetric between lanes and split symmetrically
by the bridge plane, they cancel in the contrast to first order, and a **smaller** `c` gives a
**smaller** ceiling, so the allowance is strictly conservative for admission. The candidate-blocked
`c_field` is recomputed in P3 and reported as a diagnostic; it does not re-open the gate.

**Residual limitation.** The ceiling is a property of the *two-node model*, not of the fixture. A
candidate can be inside the reachable set and still be a poor coarse-graining — that is precisely
what the tranche is testing. The gate prevents one specific, diagnosable failure (the inverse
saturating and inflating `ĉ`); it does not certify the reduction.

## 5. Audit — the resolution-consistency rule

**Finding: derivable ex ante, and correctly labelled.**

Two resolutions cannot support an asymptotic convergence-order estimate, and no surface here claims
one. What they support is a **frozen consistency test**, and its tolerance is derived from the
measured plane-channel law `error(%) = 50/h²` (Arm A of the closed 001 tranche) applied to the
resolved feature sizes:

```
tol(quantity) = κ · Σ_governing_features |δ(f·S_COARSE) − δ(f·S_FINE)|,   δ(h) = 0.5/h²,  κ = 2
```

| quantity | governing features | tolerance |
|---|---|---|
| `R`, `s`, `C`, `c_field`, `A_field` | `h_low = 4`, `h_high = 6` | `1.254e-2` |
| `Ξ_field`, `Ξ̂`, `G_lat_field`, `Ξ_coupon`, `kz = 2` | + bridge `kz` | `4.726e-2` |
| same, `kz = 3` | | `2.797e-2` |
| same, `kz = 4` | | `2.122e-2` |

A less-well-resolved bridge earns a **looser** tolerance because its element error genuinely moves
more between the resolutions. That is a property of the discretisation, declared in advance — not a
concession, and not adjustable after output.

**Independent plausibility remark, which did not enter the derivation:** 001 observed `Ξ_field`
moving up to 5.5 % between its two resolutions (at 3.375× different Reynolds numbers, so not a
clean comparison). The derived `4.7 %` for its smallest scientific bridge sits in the same
neighbourhood. I record this only because a tolerance that came out orders of magnitude away from
prior experience would be a reason to re-derive; it is **not** how the number was obtained, and the
derivation stands on the channel law alone.

**Residual limitation.** `κ = 2` is a safety factor, not a theorem. It is predeclared, it is
applied uniformly, and it is stated as a factor rather than hidden inside a fitted constant.

## 6. Anti-circularity and blindness

- The boundary allowlist is the 001 contract, **imported not copied**, so the two tranches cannot
  drift. `FORBIDDEN_BOUNDARY_KEYS` names 17 specific truth-side quantities — including the new
  mass-flux fields and the bridge geometry — and a test proves each is rejected rather than ignored.
  A *missing* declared key is rejected too.
- The truth pipeline never calls the inverse; the boundary record is built and inverted before field
  truth is evaluated.
- **The freeze is blind by construction.** P1 runs identical-path cases only. `FREEZE_RULE` reads
  coupon-predicted `Ξ` and the identical-path artifact; a source-level test asserts the selector
  mentions no mirror observable. The driver refuses `--mode p3` unless the freeze artifact exists
  **and** its recorded protocol / fixture-spec / matrix hashes match the configuration about to run.
- Execution authority records source commit and tree, four configuration hashes, every input file's
  hash, backend and dependency identity, stage identity, seed (`None`) and solver configuration.

## 7. Unresolved risks

Stated plainly, because a false-green preflight is worse than a design-blocked stop.

1. **The artifact may not clear `1e-3`.** *(highest)* The recessed-port design is a reasoned
   improvement, not a proof. It is possible that no candidate clears the budget — in which case P1
   returns `DESIGN_BLOCKED_PRE_EXECUTION` after 62 solves and 133 further solves are refused. That
   outcome is a legitimate, informative result and is planned for, not an embarrassment to avoid.
2. **The forcing reduction may not fix the componentwise control.** The `O(g)` scaling is an
   inference from one three-point ladder at one forcing. If the drift has a floor that is not
   proportional to `g` — round-off, or a discretisation term — the tolerance stays out of reach and
   the execution is invalid again. The ladder is what decides.
3. **The thicker divider lowers `Ξ` at a given footprint.** The transverse path is 6 base voxels
   instead of 2, so `G_lat` is smaller for the same `(w, kz)`. The family may land low in — or
   below — the WP6 window, giving `DESIGN_MISSED_TARGET` rather than a recovery verdict. The family
   spans `w ∈ {3,5,7,9} × kz ∈ {2,3,4}`, a wide range, but the mapping to `Ξ` is not known before
   the coupons run.
4. **`c_field` from the reference-blocked fixture is a proxy** for the candidate-blocked value. The
   5 % allowance is an argued bound, not a measured one; the P3 diagnostic will show how good it
   was, after the gate has already been applied.
5. **The node surfaces remain non-equipotential.** 001 measured node nonuniformity at 1.83 % of `ΔP`
   and bridge-face nonuniformity at **7.7 %** of the driving gap. Nothing in this redesign improves
   that, and the `coarse_graining_surface_stability` control can still fail. It is a required
   control precisely because a two-node reduction may simply not be defensible here.
6. **No backend cross-check.** Taichi is absent and its port asserts cubic domains and exports `ux`
   only. This will again be recorded as **NOT PERFORMED**, never as passed.
7. **Return-path contamination is bounded, not eliminated** (001 E1). Arm J's bound comes from a
   deliberately extreme perturbation; it is an upper bound, not a calibration, and it is not
   negligible against a factor-of-two criterion.

## 8. Recommendation

**Ready for review; not ready to execute without it.**

The four things this review exists to check are, in my assessment, correct: the conserved quantity
is measured rather than proxied and does not disturb the inverse's contract; the similarity law is
right, exactly representable and verified against the live solver's own `ν`; the negative control
targets the actual mechanism of the 001 defect and its adequacy is measured before any mirror case
runs; and the reachable-set margin is derived from conditioning, is conservative in `c`, and admits
the entire target window.

The design decision that most deserves adversarial attention is **making the lane-facing ports
common-mode between the blocked and open fixtures** (§3). I believe it is the correct apparatus and
not a disguised correction, and the argument is given above — but it is the load-bearing change, and
if a reviewer disagrees the right response is to revisit the geometry, not to relax the budget.

Subject to that, I recommend authorising **P0, P1 and P2 only** (86 solves, ending at the bridge
freeze), and requiring a second review of the freeze artifact before P3 runs. That preserves the
blindness the whole design depends on: nothing in P0–P2 reveals a mirror recovery observable, so the
selection cannot be contaminated by the result.

**P3 and P4 remain unauthorized.** Stage B remains unauthorized. Paper 4 remains unauthorized. Card
box 5 remains OPEN and box 6 remains closed on its existing mathematical result. RP-D-LC-001 remains
`INVALID_EXECUTION` and its cross-model question remains **unadjudicated, not negative**.


---

# 11. POST-REVIEW AUDIT — CORRECTION `PREFLIGHT-C1`

Supersedes §10. The apparatus is unchanged and still accepted; what follows is my assessment of
the corrected machinery and of one risk the correction itself created.

## 11.1 What the review accepted, and what it did not

**Accepted in principle: the common-mode-port apparatus.** The blocked fixture has two physical
blind pockets, the open fixture joins those same pockets, this is a physical off/on comparison
rather than post-hoc subtraction, topology excludes a bridge-confined axial through-conduit, and
P1 must still *measure* any remaining parallel-detour conductance. Nothing in the correction
reverts to the 001 aperture, introduces identical-path subtraction, fits away an artifact or
relaxes the artifact budget.

**Not accepted: twelve items of machinery.** Two of them would have mattered most:

- **PE-2** — the transverse control divided by its own mean, so it was undefined at the
  zero-lateral-driver identical-path case, *the very case it exists to decide*, and could have
  reported a spurious failure precisely because the physics was right. My §3 argued the negative
  control was the decisive gate and then shipped a metric that could not evaluate it. That is the
  most serious defect in the superseded preflight.
- **PE-5** — P1 and P2 ran central forcing only, so admission, classification and selection would
  have rested on quantities whose forcing-invariance evidence first appeared in P3. A candidate
  chosen on central forcing and validated afterwards is chosen on unvalidated evidence.

## 11.2 Re-audit — conserved quantity

The nine adjudicative planes are now enforced, not assumed. The regression that matters is not
that the count is nine but that **passing the named records, even tripled, cannot move the
verdict**, while the same records *admitted* to the statistic demonstrably do — the test asserts
both. Transverse conservation is state-aware with four frozen semantics and a zero-safe absolute
metric; the superseded statistic is shown to raise `ZeroDivisionError` on the control's own
defining input. Non-finite values can no longer be hashed. **Assessment: closed.**

## 11.3 Re-audit — low-Mach validity

The control is now the measured maximum of the full velocity vector over fluid nodes, with the
argmax and its three components retained, and `uz` is requested rather than assumed to vanish.
The tests show a `uz` contribution alone determining the maximum and a solid node carrying `99.0`
being excluded. `design_mach_scale` is demoted to a planning estimate. **Assessment: closed.**

## 11.4 Re-audit — forcing coverage

Every pre-freeze family — reference-blocked, axial coupons (both orientations), identical-path,
bridge coupons, candidate blocked mirror — now carries the full `×0.5/×1/×2` ladder at both
resolutions, asserted by test. `candidate_blocked_mirror` is confined to P2a, and no open mirror
case is scheduled anywhere before the freeze. `TOL_LINEARITY_REL` is untouched at `1e-4`.
**Assessment: closed.** The cost is real — the pre-freeze budget rises from 86 to ≤ 326 solves —
and that is the honest price of not selecting on unvalidated evidence.

## 11.5 Re-audit — numerical discrepancy and the artifact gate

The borrowed constant is gone. What replaces it is a **method**, not a number, and it is named a
conservative numerical-discrepancy bound rather than a rigorous error bound, because that is what
it is: a linear sum of a measured continuation term, a measured node-offset term and a
serialisation term, times a declared safety factor. The gate is an upper-bound form, and the test
that proves it bites is the one where a `5e-4` point estimate — comfortably inside the budget —
fails on a `1e-3` uncertainty. **Assessment: closed, with one caveat**: the continuation bound is
measured on the smallest and largest bridge only and applied to all. That is declared, and the
worst of the two is used, but it is an assumption rather than a per-candidate measurement.

## 11.6 Re-audit — the contrast bound, and a NEW risk the correction created

The fixed 5 % allowance is gone and replaced by a measured interval from each candidate's own
blocked-mirror characterisation. The admission now takes the signal at the **upper** contrast and
`Ξ` and the ceiling at the **lower** contrast — conservative on both sides instead of one.

**This makes the gate materially tighter, and that is a live design risk.** At an illustrative
±2.5 % contrast interval around 001's measured `c_field = 0.3218`:

| quantity | value |
|---|---|
| ceiling `K(c_lower)` | `0.1094` |
| margin `0.10·K` | `0.0109` |
| max admissible `Ξ` | **≈ 3.91** |
| WP6 window top | `3.946` |

So the *above-window* categorical slot the freeze rule requires may be **unfillable**: a candidate
above the window is, almost by definition, one the reachable-set gate excludes. If that is what
P2a measures, `select_bridges` stops with `NO_UNAMBIGUOUS_ABOVE_CANDIDATE` and the tranche is
design-blocked before any primary computation.

**I have deliberately not resolved this**, because every available resolution is a scientific
judgement that belongs to the reviewer, not to me:

1. **accept a design-blocked outcome** — legitimate, and cheap: it costs the pre-freeze solves and
   nothing more;
2. **change the frozen rule, before execution, to require four slots** (one below, three inside)
   and record the above-window slot as excluded by the reachable set — defensible, because clause
   2 needs three *in-window* cases and the below/above candidates serve monotonicity coverage
   (clause 5), not the window count;
3. **revisit the geometry to raise the contrast** — `K = c²/(1−c²)` rises steeply with `c`, and
   the nominal design contrast from the `h³` ratio is `≈ 0.54` (`K ≈ 0.42`) against the `0.32` the
   in-situ coarse-graining actually measured in 001. The gap between nominal and measured contrast
   is itself worth understanding.

**Tuning the margin is not on that list.** The `0.10·K` margin has a conditioning justification
and is not adjustable to make a candidate fit.

## 11.7 Re-audit — resolution consistency

The feature envelope now includes `bridge_w` — which is *smaller* than `kz` for `w = 3, kz = 4`,
so the superseded `kz`-only model could omit the governing feature entirely — plus port depth,
duct traverse and an explicit junction/end allowance, with `R`/`s` split into blocked and open
forms. Tolerances rise from `1.3–4.7e-2` to `2.1e-2` (lane-only) and `9.6–13.6e-2`
(bridge-carrying). **That looseness is the honest consequence of accounting for what actually
varies**, and it remains well inside the factor-of-two criterion it feeds. It is still a
consistency test at two resolutions and is never called a convergence-order estimate.
**Assessment: closed.**

## 11.8 Re-audit — selection and authority

Selection now has one deterministic coordinate (the geometric mean over both resolutions and all
three forcing levels), a conservative envelope, an explicit `boundary_ambiguous` state, and
exactly-five-or-stop with six frozen reason codes. Authorisation is phase-specific and empty, with
the freeze and manifest gates checked *before* the allowlist so neither is shadowed, and a freeze
cannot be assembled from hand-entered candidates. **Assessment: closed.**

## 11.9 Unresolved risks, revised

1. **The above-window slot may be unfillable under the corrected gate.** *(new, highest)* §11.6.
2. **The artifact may still not clear `1e-3`** — now with an uncertainty term added on top, which
   makes the gate strictly harder to pass than in the superseded form. Unchanged in kind from the
   original risk 1, harder in degree.
3. **The forcing reduction may not fix the componentwise control.** Unchanged.
4. **The thicker divider lowers `Ξ` at a given footprint**, which now interacts with risk 1: a
   family that lands low in the window makes an above-window candidate *less* likely, not more.
5. **The continuation bound is measured on two candidates and applied to twelve.** *(new)* §11.5.
6. **The node surfaces remain non-equipotential**, and `coarse_graining_surface_stability` can
   still fail. Unchanged.
7. **No backend cross-check.** Unchanged — recorded as NOT PERFORMED, never as passed.
8. **Return-path contamination is bounded, not eliminated.** Unchanged.

## 11.10 Recommendation, revised

**Ready for a second exact-head review; still not ready to execute.**

The twelve blockers are corrected and each has a regression test that proves the defect cannot
recur — several by demonstrating that the superseded behaviour was wrong. I recommend, unchanged
in shape but not in extent:

- authorise **P0, P1a, P1b and P2a only** (≤ 326 solves, ending before the freeze), by adding
  exactly those phases to `AUTHORISED_SOLVING_PHASES` in a reviewed commit;
- require a **third** review of the proposed freeze artifact and the instantiated P3/P4 matrix
  before P3 is added to the allowlist.

Before authorising even that, the reviewer should settle **§11.6** — whether an unfillable
above-window slot is an acceptable design-blocked outcome, a reason to re-freeze the rule at four
slots, or a reason to revisit the contrast. Answering it after P2a would mean answering it with
results in hand, which is exactly what the blindness of the freeze exists to prevent.

**P3 and P4 remain unauthorized. Stage B remains unauthorized. Paper 4 remains unauthorized. Card
box 5 remains OPEN and box 6 remains closed on its existing mathematical result. RP-D-LC-001
remains `INVALID_EXECUTION` and its cross-model question remains unadjudicated, not negative.**


---

# 12. POST-RE-REVIEW AUDIT — CORRECTION `PREFLIGHT-C2`

Supersedes §11. The apparatus is still unchanged and still accepted.

## 12.1 What the second review found

Eight further blockers (PE-14 … PE-21). Two were defects of substance rather than of machinery,
and both were in controls I had described in §11 as *closed*:

- **PE-14 — the zero-driver gate could return a false green.** §11.2 reported the transverse
  control as closed because it was zero-safe. It was zero-*safe* and not zero-*testing*: the
  verdict was `|max − min| / axial_mass_scale`, which is a **consistency** statistic. Four equal,
  materially nonzero transverse mass fluxes have a range of exactly zero and passed at any
  magnitude. A fixture leaking a large but perfectly consistent lateral current, with nothing
  driving it, would have returned a green negative control. Corrected by requiring magnitude
  **and** consistency, each against the unchanged `1e-3`.

- **PE-15 — the negative control's premise was asserted, not measured.** `y_face1` and `y_face2`
  were frozen in the metadata and **never read**. "Zero lateral driver" came from the geometry
  label `variant == "identical"`, which is a statement about the two-node model's algebra, not a
  measurement of a voxelised fixture with junctions and a finite solver residual. The gap is now
  measured, pointwise so the common axial gradient cancels exactly, and an identical-path case
  whose measured gap is nonzero **fails**.

The remaining six are machinery: the audit that could be a no-op (PE-16), the two-extremes
extrapolation (PE-17), the manifest that passed on a nonempty list and the freeze that accepted
free-form input (PE-18), the refusal with nothing behind it (PE-19), the five-slot rule (PE-20),
and the exact rational that stopped at the constant (PE-21).

## 12.2 Re-audit — zero-driver physics

Magnitude and consistency are now separate gates with separate verdicts, and the regression
demonstrates the superseded failure directly: four equal fluxes at five times the ceiling have
`plane_range_mass == 0.0`, pass consistency, and fail magnitude. The driven case is explicitly
**not** subject to the magnitude gate — a nonzero lateral flux there is the physics under test.
**Assessment: closed.**

## 12.3 Re-audit — the measured lateral driver

The pointwise construction is the part I would most want challenged, and I think it is right: both
faces span the same footprint, so the axial pressure gradient across it is common to them and
cancels exactly in a pointwise difference. Attributing the individual faces' spatial spreads to
the gap would charge that common-mode gradient as uncertainty — precisely the thing that cancels —
and would have made the control unpassable for a wide bridge. The face spreads are retained as the
coarse-graining diagnostic 001 reported. **Assessment: closed**, with the construction flagged for
review.

## 12.4 Re-audit — fixed-step audits and their coverage

The audit now pins `min_steps = max_steps = target`, so it cannot return the base result, and
`FIXED_STEP_AUDIT_INCOMPLETE` exists precisely to catch a run that stops early. Coverage is
per-candidate, per-state, per-resolution, per-forcing-level — the two-extremes extrapolation is
gone, and with it the assumption §11.5 flagged as its own caveat. **Assessment: closed.** The cost
is large and is stated: **320** planned fixed-step audits against **383** normal solves.

## 12.5 Re-audit — lineage and the executor

A freeze can no longer be built from assertions. Records are immutable and atomic; manifests are
ledgers that reopen and rehash everything and derive their own expectations; and the assembler
recomputes every scientific quantity from records. The executor makes the refusal meaningful: it
is real, deterministic, and demonstrated end-to-end on a whole P0 phase with a fake provider,
while the instrumentation confirms the kernel is never reached. **Assessment: closed.**

**One defect the new tests caught in my own work:** an intermediate edit had dropped the
reachable-set admission block from the assembler, so no candidate could ever have been marked
eligible. It is restored, with a per-term uncertainty lineage. I record it because a correction
cycle that only finds other people's defects is not being run honestly.

## 12.6 The four-slot decision

§11.6 put three responses to the reviewer and declined to choose. **The reviewer chose option 2**:
four slots, one below plus three inside, no above-window slot required. The rationale is in
`PREFLIGHT_ERRATA.md` PE-13, and the two things I would guard are recorded there too — clause 2
needs three *in-window* cases, and **the `0.10·K` margin was not touched**. That risk is therefore
resolved, not carried.

## 12.7 Unresolved risks, revised

1. **The artifact may still not clear `1e-3`.** *(highest)* Now strictly harder than in C1: the
   gate is an upper bound, and it must hold at **every** one of the six required combinations per
   candidate rather than once.
2. **The measured lateral gap may not clear `TOL_LATERAL_DRIVER_REL`** in the identical-path
   control. *(new)* This is a genuinely new way for the tranche to design-block, and it is the
   right way: if the discretised "identical" fixture has a real lateral driver, the negative
   control's premise is false and no amount of consistency in the flux would have told us.
3. **The forcing reduction may not fix the componentwise control.** Unchanged from C0.
4. **The thicker divider lowers `Ξ`**, which with four slots is now less dangerous — no
   above-window candidate is required — but a family landing entirely below the window would still
   fail `INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES`.
5. **The pre-freeze budget is large**: up to **640** solves before the freeze. That is the
   price of per-case evidence, and it is a resource question for the reviewer, not a scientific
   one.
6. **Node surfaces remain non-equipotential**; `coarse_graining_surface_stability` can still fail.
7. **No backend cross-check.** Recorded as NOT PERFORMED, never as passed.
8. **Return-path contamination is bounded, not eliminated.**

## 12.8 Recommendation

**Ready for another exact-head review; still not ready to execute.**

I recommend authorising **P0, P1a, P1b and P2a only**, by adding exactly those four phases to
`AUTHORISED_SOLVING_PHASES` in a reviewed commit, and requiring a further review of the proposed
freeze and the instantiated P3/P4 matrix before P3 is added. Nothing in P0–P2a exposes an open
mirror recovery observable, so the blindness the design depends on survives that authorisation.

The construction most deserving adversarial attention this round is **§12.3, the pointwise lateral
pressure gap**: it is the measurement that now decides whether the negative control's premise
holds at all.

**P3 and P4 remain unauthorized. Stage B remains unauthorized. Paper 4 remains unauthorized. Card
box 5 remains OPEN and box 6 remains closed. RP-D-LC-001 remains `INVALID_EXECUTION` and its
cross-model question remains unadjudicated, not negative.**



---

# CORRECTION `PREFLIGHT-C6` — what the sixth exact-head review found

Disposition at `acb4f6a` (tree `4c53c4b`):
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C6_ENDPOINT_RECOMPUTATION_AND_DIAGNOSTIC_SEMANTICS_REQUIRED`

**PE-66 is accepted without change.** The C5 apparatus, similarity law, candidate family,
scientific gates, four-slot rule and reachable-set admission are accepted and are not redesigned.

C5's defects were all of the same kind: **something stated and not implemented.**

- **A diagnostic that could stop a phase.** PE-65 froze the two `tau_plus = 1.2` rows
  `DIAGNOSTIC_ONLY` — no frozen assembled-fixture comparison quantity, no tolerance, may alter
  nothing. The matrix emitted them `class = mandatory`, so an unconverged or failed-Mach tau row
  terminated P0 and blocked P1a; and their records sat in `common_reference_evidence`, the
  structure every candidate cites as shared truth. Both are corrected: an explicit frozen
  scientific role per row, five phase ledgers with the diagnostic ones separate, and a
  `diagnostic_evidence` structure nothing downstream consumes.

- **A validator that authenticated bytes rather than science.** `validate_p2b_manifest`
  recursively revalidated the predecessors, reopened every record — and then compared the
  persisted ledger against the manifest's own record of its hash. A coordinated edit that also
  updated the outer hashes validated cleanly. The pure builder now reconstructs the endpoint from
  the records and the validator compares field by field; twelve coordinated-tamper cases fail.

- **Two-record quantities with one-record lineage.** `R_identical` is `C_open / C_blocked` and
  `Xi_actual` is `G_bridge·(1/A1 + 1/A2)`; both cited a single source in the generic schema, with
  the partner in an ad-hoc key the gates never read.

- **A safety factor applied to two terms of three.** The frozen artifact uncertainty is
  `2·(a + b + c)`; the live assembler computed `2a + 2b + c`. And the pressure **maximum** bound
  borrowed the **mean's** serialisation term.

**None of these changes a tolerance, a budget, the safety factor, the candidate family or any
scientific gate.** The mandatory minimum falls from 112 to 110 because two rows stop being
decision-bearing, which is the point of the correction rather than a side effect of it.

**Recommendation is unchanged:** authorise nothing yet. Another exact-head review is required
before P0–P2b, and P3/P4 need a further correction and review of the real pre-freeze artifacts.


---

# CORRECTION `PREFLIGHT-C7` — what the seventh exact-head review found

Disposition at `76e5669` (tree `489af8f`):
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C7_DIAGNOSTIC_ATTEMPT_AND_EXECUTION_AUTHORITY_LINEAGE_REQUIRED`

**All C6 scientific outcomes are accepted. PE-66 remains accepted without change, and so does
the mandatory-minimum change from 112 to 110.** Nothing in the apparatus, the scientific gates,
the similarity law, the uncertainty equations, the candidate family, the four-slot selection or
the claim ceiling is altered.

Two findings, both of the same shape as C6's: **a correct rule applied at the wrong point.**

- **A diagnostic whose attempt could kill the phase.** C6 made the `tau_plus = 1.2` rows
  non-adjudicative, and the role-aware classifier that implements it is reached only *after* the
  provider call, the compact extraction, the record construction and the record write have all
  succeeded. A provider that raises, or returns a result missing `steps` or `rho`, or a
  wrong-shaped or non-finite field, aborted P0 outright — before `diagnostic_failed` could exist,
  and leaving nothing on disk for a resume to find. The correction is narrow by construction:
  four named failure codes, one eligible role, an explicit never-caught list, and no
  undifferentiated `except Exception` anywhere in the row loop.

- **An authority that could not be reconstructed.** Phase manifests persisted
  `execution_authority_sha256` and a few convenience fields. The complete object — every
  input-file hash, the document hashes, the stage, the prerequisites, the dependency identity,
  the clean-tree proof — lived only in transient Python memory. `authority=None` meant *skip*,
  and what validation existed compared 40-character strings rather than asking Git whether the
  recorded commit exists and what it contains. The correction persists the complete object,
  validates it against the recorded commit and its tracked contents, and binds every record to
  it by hash.

**One thing is stated rather than faked.** `working_tree_clean`, `dependencies` and `seed` are
**measured historical claims**. No later process can re-derive them. Their integrity rests on
being bound inside the authority hash that every record, envelope, manifest and P2b artifact
cites, and the code says so in those words rather than pretending to reproduce a `git status`
run that happened once.

**Recommendation is unchanged:** authorise nothing yet. Another exact-head review is required
before P0–P2b, and P3/P4 need a further correction and review of the real pre-freeze artifacts.
