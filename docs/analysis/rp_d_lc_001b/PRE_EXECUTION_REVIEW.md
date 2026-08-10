# RP-D-LC-001b — pre-execution scientific review

```
PRE-EXECUTION AUDIT — decides whether computation may begin; produces no scientific result
NO RP-D-LC-001b LATTICE-BOLTZMANN SOLVE HAS RUN
```

This is the audit the freeze exists to be checked against: apparatus, similarity law, conserved
quantities and negative controls, examined **before** any computation. It states what I believe is
correct, what remains a genuine risk, and my explicit recommendation.

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
