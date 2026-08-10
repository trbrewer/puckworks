# RP-D-LC-001b — pre-execution errata

```
APPEND-ONLY. Each erratum supersedes part of the frozen preflight; nothing above an
erratum line is rewritten, and no superseded value is deleted.
PRE-EXECUTION THROUGHOUT — no RP-D-LC-001b lattice-Boltzmann solve has run at any point
in this lineage, before or after any erratum here.
```

Effective correction version: **`PREFLIGHT-C1`** (see PE-0). Generated artifacts under
`generated/` carry `correction_version` so a machine-readable record can never be mistaken for
the superseded one.

---

# PE-0 — exact-head review at `bbf2304` was NOT APPROVED; this is the correction record

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_CORRECTION_REQUIRED`

**Reviewed head:** `bbf2304665d09cb78c117353947ce8c6cf2e5d24`
**Reviewed tree:** `c028f652b85b9b8670f9be03f8093e6bdae9d276`

## What the review ACCEPTED

**The common-mode-port apparatus is accepted in principle**, and is preserved unchanged:

- the blocked fixture has two physical blind pockets;
- the open fixture joins those same pockets;
- this is a physical off/on comparison, **not** post-hoc subtraction;
- topology excludes a bridge-confined axial through-conduit;
- P1 must still **measure** any remaining parallel-detour conductance.

Nothing in this correction reverts to the RP-D-LC-001 aperture, introduces identical-path
subtraction, fits away an artifact, or relaxes the artifact budget. `ARTIFACT_BUDGET_R_ABS`
remains `1.0e-3` and `TOL_LINEARITY_REL` remains `1.0e-4`.

## Superseded machine-readable artifacts

The following hashes were the frozen configuration at `bbf2304`. They are **superseded, not
erased**, and are retained here so any record bound to them remains traceable:

| artifact | superseded SHA-256 (`bbf2304`) |
|---|---|
| `generated/protocol.json` | `047d55f4dcd222b79f20f3d08e04b8de0dd13e7ddb8438cb74bf35ee6461cbe7` |
| `generated/fixture_spec.json` | `c8592643b861150b534f6f823336a1e14b1d082e9f8c5bcf25957a4417d9fc2f` |
| `generated/execution_matrix.json` | `1ff57d57c77eb56017628c52b80f1e70da549132a84b98e07e1ef300ec30fa74` |
| `generated/preflight_status.json` | `01244d1c9b129aa22681ec84391adddc14c20a169acf903cfad99ee75fb642f3` |

No bridge freeze artifact existed at `bbf2304` and none exists now, so no freeze is invalidated
by this correction.

## Blockers, in the order they are corrected

| id | blocker | superseded form | effective form |
|---|---|---|---|
| PE-1 | axial conservation double-weighted planes | `conservation_residuals` consumed whatever list it was given, including the five named measurement records — so `x_meas_in` and `x_meas_a` were weighted twice and two plenum node planes entered a lane-conservation statistic | exactly nine unique adjudicative records `cons_0…cons_8`, validated for count, uniqueness, coordinate uniqueness and frozen order; named records reported separately |
| PE-2 | transverse conservation ill-conditioned at its own defining case | one relative spread about the mean for all states — undefined at the zero-lateral-driver negative control, and evaluated even for a blocked bridge whose duct planes are solid | four frozen state semantics with a zero-safe absolute metric normalised by a frozen axial mass-flux scale, and a relative gate that applies only above a predeclared nonzero floor |
| PE-3 | canonical serialisation admitted non-finite numbers | `allow_nan=True` — a `NaN` could be hashed as though it were a scientific number | strict writer; `NaN`/`Inf` raise `NonFiniteValue`; non-applicability is an explicit status string with `null` numerics |
| PE-4 | low-Mach control was a scalar design estimate | `design_mach_scale`, and a driver requesting only `("rho", "uy")` | full three-component `max‖u‖` over fluid nodes only, from `ux`, `uy`, `uz`, with the argmax location and components retained; `uz` is no longer assumed zero from nominal symmetry |
| PE-5 | selection-bearing quantities validated after selection | P1/P2 ran central forcing only; forcing invariance would first have been demonstrated in P3 | staged `P1a/P1b/P2a/P2b`; **no** quantity may inform admission, classification or selection before its own forcing-invariance evidence exists at both resolutions and all three forcing levels |
| PE-6 | numerical uncertainty in `R` borrowed from mass conservation | `NUMERICAL_UNCERTAINTY_R_ABS = TOL_MASS_REL` — two different quantities equated | a frozen R-specific **numerical-discrepancy method** (continuation + node-offset + serialisation, times a frozen safety factor), evaluated per case; the artifact gate becomes an upper-bound form |
| PE-7 | the 5 % `c_field` allowance was asserted, not bounded | `C_FIELD_GATE_ALLOWANCE = 0.05`, defended by a first-order symmetry argument | removed; replaced by candidate-specific **blocked mirror** characterisation in P2a and a conservative measured `[c_lower, c_upper]` interval |
| PE-8 | resolution-consistency feature model incomplete | bridge quantities governed by `bridge_kz` alone; `R`/`s` did not distinguish lane-only from bridge-carrying | full critical-feature envelope including `w`, `kz`, port depth and duct traverse, plus an explicit junction/end allowance; `R`/`s` split into blocked and open forms |
| PE-9 | cross-resolution `Xi` semantics undefined | `select_bridges` consumed one unspecified `Xi_coupon` per candidate | `Xi` retained by resolution, forcing level and coupon source with an uncertainty envelope; `Xi_select` = geometric mean of valid positive estimates; conservative envelope categories with an explicit `boundary_ambiguous` state |
| PE-10 | matrix rows were not uniquely executable | no `case_id`, missing coupon `orientation`, no prerequisite, no backend or `tau_plus` on the row | stable unique `case_id` and a complete per-row configuration including `orientation`, `tau_plus`, `backend`, `audit_mode`, `record_schema` and `prerequisite` |
| PE-11 | authorization was all-or-nothing | one module-level `EXECUTION_AUTHORISED` boolean | `AUTHORISED_SOLVING_PHASES = ()` plus a fail-closed runtime authority requiring clean tree, real git identity, exact hashes, complete input hashes, supported backend and predecessor manifests |
| PE-12 | assorted consistency defects | `Fraction(2.0e-6)` from a binary float; `tau_plus = 1.2` called "retained as a cross-check" but never scheduled; 131-vs-133 refused-row mismatch; "one replicate per phase" vs replicates in three phases | exact `Fraction(1, 500_000)`; two scheduled `tau` cross-check rows; one computed refused-row count everywhere; an explicit, justified statement of where the three replicates are and why there are three |

## What did NOT change

- the Stage-A scientific question;
- the common-mode-port apparatus and the whole of `VIRTUAL_FIXTURE_SPEC.md` §3–§12 geometry;
- `ARTIFACT_BUDGET_R_ABS = 1.0e-3`;
- `TOL_LINEARITY_REL = 1.0e-4`;
- `TOL_MASS_REL = 1.0e-3`;
- the forcing law `g(S) = g_ref (S_ref/S)³`, `g_ref = 2.0e-6`, `S_ref = 2`, and both ladders;
- the reachable-set safety margin `0.10·K` and its conditioning justification;
- the Route-A observable contract — the inverse still consumes pressure-normalised **volume**
  flux; **Route B remains unauthorized** and no new pressure component is introduced;
- **no solver change**: `lb_reference` is byte-unchanged and only its existing optional field
  export is used (now including `uz`, which it already exports);
- the claim ceiling;
- **RP-D-LC-001 remains byte-unchanged and historically immutable.**

---

# PE-1 — axial conservation admitted duplicate and non-conservation planes

**Superseded.** `conservation_residuals(axial_records, …)` took the spread over every record
handed to it. The driver handed it the five named measurement records **and** the nine
conservation records, so:

- `x_meas_in` (`4S`) duplicated `cons_0` (`4S`);
- `x_meas_a` (`53S − 1`) duplicated `cons_8`;
- `x_node_in` (`4S − 1`) and `x_node_out` (`53S`) — plenum node planes kept for **pressure** —
  entered a lane-flux conservation statistic;
- `x_meas_b` (`48S`) added a tenth, unfrozen, plane.

**Why that was unsafe.** A min/max spread is decided by its extremes, so duplicating a plane
that happens to sit at an extreme changes the adjudicative residual without any physics changing,
and adding or removing a named plane silently re-weights the control. A conservation verdict must
depend on the frozen plane set alone.

**Effective form.** `conservation_residuals` accepts **only** the nine records `cons_0…cons_8` and
raises otherwise. It asserts: exactly nine records; nine unique plane IDs; nine unique intended
coordinates; frozen order. Named measurement records are reported separately as
`named_plane_records` and are never admitted to the adjudicative set. The volume-flux residual
remains **diagnostic**; the density-weighted mass-flux residual remains **adjudicative**.

---

# PE-2 — transverse conservation was ill-conditioned at the case it exists to decide

**Superseded.** One metric — the relative spread of `sum_rho_uy` about its mean across four
transverse planes — applied to every fixture state.

**Why that was unsafe.** The **defining** negative-control case is the identical-path open fixture
with exactly zero lateral driver, where the correct physical answer is zero net transverse mass
flux. A statistic that divides by its own mean is undefined at zero and ill-conditioned near it,
so the control would have been unable to evaluate its own decisive case — and, worse, could have
reported a spurious *failure* precisely because the physics was right. The same metric was also
applied to a **blocked** candidate whose duct-control planes are structurally solid, where there
is no through-flow to be consistent about.

**Effective form — four frozen state semantics.**

| state | status | metric |
|---|---|---|
| `reference_blocked` (no bridge) | `NOT_APPLICABLE_NO_BRIDGE` | no transverse records required |
| candidate `blocked` | `NOT_APPLICABLE_BLOCKED_CONNECTION` | duct-control planes asserted structurally solid; port-pocket records retained as **blind-pocket recirculation diagnostics**, explicitly not through-flow; no relative spread evaluated |
| identical-path `open`, zero lateral driver | `EVALUATED_ZERO_SAFE_ABSOLUTE` | absolute leakage/balance normalised by a frozen nonzero **axial** mass-flux scale — never by mean `q_lat` |
| driven `open` | `EVALUATED_HYBRID` | (a) absolute mismatch normalised by the axial mass-flux scale, always; (b) relative plane-to-plane mismatch **only** when the mean lateral mass flux exceeds a predeclared nonzero floor |

The floor is derived before output and is not tunable: the relative statistic is admitted only
when the mean lateral mass flux is at least `LATERAL_FLUX_FLOOR_FACTOR = 10` times the absolute
leakage ceiling the absolute gate already permits — i.e. only when the signal is an order of
magnitude above the noise the design tolerates.

Every case records applicability status, absolute plane sums, signed balance, normalisation scale,
relative value when applicable, tolerance, pass/fail/`NOT_APPLICABLE` and a reason. **Every
adjudicative numeric value must be finite**, enforced by the strict writer of PE-3.

---

# PE-3 — canonical serialisation admitted `NaN` and infinities

**Superseded.** `canonical_json(..., allow_nan=True)`.

**Why that was unsafe.** `NaN` is not valid JSON, it is not a number, and hashing it produces a
stable digest for a value that carries no scientific content — so a record could be bound,
verified and reproduced while containing a quantity that was never computed. Non-applicability and
non-computation are *statuses*, not numbers.

**Effective form.** A strict canonical writer rejects `NaN` and `±Inf` anywhere in a hashed
artifact, raising `NonFiniteValue` with the offending path. Scientific non-applicability is
represented by an explicit status string with `null` numeric fields. `execution_authority()`
rejects missing files and `None` hashes rather than recording them.

---

# PE-4 — the low-Mach control was a design estimate, not a measured field quantity

**Superseded.** `design_mach_scale(S)`, a scalar `√3·gL²/ν` computed from frozen inputs, and a
driver requesting `return_fields = ("rho", "uy")`.

**Why that was unsafe.** The design scale is an *a priori* estimate of the mean lattice velocity;
the control needs the **maximum speed actually attained**. Requesting only `uy` also meant `uz`
was never retained, so a `uz` contribution could not have been seen at all. Nominal symmetry is
not a proof that `uz` vanishes — the bridge, the ports and the junctions all break the simple
picture, and 001 recorded that low Mach and low Reynolds are not interchangeable.

**Effective form.** Every solved case requests `("rho", "uy", "uz")` and records, over **fluid
nodes only**:

```
max_speed_fluid = max( sqrt(ux² + uy² + uz²) )        max_mach = sqrt(3) · max_speed_fluid
```

with the flat and 3-D index of the maximum, the three velocity components there, `TOL_MACH` and
pass/fail. Solid nodes are excluded (the kernel leaves `g/2` in `ux` there). The record fails
closed on absent or non-finite fields. `design_mach_scale` is retained, renamed in role to a
**pre-execution planning estimate only**, and is not a control.

---

# PE-5 — selection-bearing quantities would have been validated after selection

**Superseded.** P1 and P2 ran central forcing only; the `×0.5/×1/×2` ladders appeared first in P3.

**Why that was unsafe.** Admission, classification and selection would then have rested on
quantities whose forcing-invariance evidence did not yet exist. A candidate chosen on central
forcing and validated afterwards is chosen on unvalidated evidence, and if the later ladder failed
the selection would already have been made. That is the failure the whole tranche exists to avoid.

**Effective form — staged.**

- **P1a** — central identical-path blocked/open pairs for all declared candidates, both
  resolutions.
- **P1b** — reject obvious central failures; run `×0.5` and `×2` identical-path extensions for
  every candidate that could still be selected, plus the frozen continuation runs the PE-6 method
  needs. Final artifact admission uses **all three forcing levels at both resolutions**.
- **P2a** — full forcing ladders for the bridge coupons of surviving candidates, and
  candidate-specific **BLOCKED mirror** characterisation over the same forcing/resolution set.
  **No candidate OPEN mirror recovery case is run.**
- **P2b** — apply every forcing, resolution, artifact, reachability and selection rule; produce
  the proposed bridge freeze and the instantiated P3/P4 matrix; **stop for a second exact-head
  review.**

Zero-signal quantities use the PE-2 zero-safe absolute rule rather than a relative spread about
zero. `TOL_LINEARITY_REL = 1e-4` is unchanged and is not tuned.

---

# PE-6 — numerical uncertainty in `R` was borrowed from the mass-conservation tolerance

**Superseded.** `NUMERICAL_UNCERTAINTY_R_ABS = TOL_MASS_REL = 1.0e-3`.

**Why that was unsafe.** A plane-to-plane mass-flux residual and the numerical discrepancy of a
pressure-normalised conductance ratio are different quantities with different units of meaning.
Equating them was presented as conservative; it is simply unrelated, and it happened to be
numerically equal to the entire artifact budget, which would have made the budget's meaning
ambiguous.

**Effective form.** A frozen **method**, evaluated per case — deliberately *not* a constant, and
deliberately **not** called a rigorous error bound:

```
u_artifact_R = SAFETY_FACTOR · ( |ΔR|_continuation + |ΔR|_node_offset + u_serialisation )
SAFETY_FACTOR = 2.0   (frozen)
```

- `|ΔR|_continuation` — measured by re-running at `CONVERGENCE_AUDIT_FACTOR × ` the converged step
  count, separately for the open and blocked members of the pair, propagated through the ratio;
- `|ΔR|_node_offset` — the largest movement of `R` across the frozen node-surface offsets. It
  needs **no extra solve**: the offsets are different planes of the same solution;
- `u_serialisation` — `10^(−_RECORD_DP)·(1 + |R|)`, negligible but declared.

It is named a **conservative numerical-discrepancy bound**. The identical-path artifact gate
becomes an upper-bound form:

```
abs(R_identical − 1) + u_artifact_R  ≤  ARTIFACT_BUDGET_R_ABS = 1.0e-3
```

with the point estimate, the uncertainty term, the upper bound and the verdict reported
separately. A non-finite uncertainty fails closed. **If the measured uncertainty makes the gate
unachievable, that is a design-blocked stop, not grounds to relax the budget.**

The reachable-set admission must not count the same uncertainty twice. Four terms are kept
strictly separate: the artifact upper bound (which already contains `u_artifact_R`), the
candidate-`c` interval (folded into the ceiling, never added again), the predicted-signal/coupon
envelope, and any additional non-overlapping numerical term (zero by construction unless one is
introduced and declared).

---

# PE-7 — the 5 % `c_field` allowance was asserted, not bounded

**Superseded.** `C_FIELD_GATE_ALLOWANCE = 0.05`, applied to the **reference-blocked** `c_field`
and described as "strictly conservative".

**Why that was unsafe.** The reduction of the ceiling is monotone in `c`, so *if* the true
candidate contrast were within 5 % the allowance would indeed be conservative — but nothing
established that. The supporting argument was first-order symmetry, which is not a bound. The
gate that decides which candidate is frozen must not rest on an unmeasured allowance.

**Effective form.** Candidate-specific **BLOCKED mirror** characterisation for every candidate
that can still be selected, in P2a — permitted, because a blocked mirror fixture exposes no open
coupling-recovery observable. For each candidate a conservative interval `[c_lower, c_upper]` is
derived from both resolutions, the required forcing ladder, the resolution-consistency
uncertainty, the PE-6 numerical-discrepancy uncertainty and the documented plane/surface
variability. The admission form becomes

```
predicted_signal_upper(c_upper, Xi_upper) + artifact_upper + other_nonoverlapping_numerical_upper
      <  reachable_ceiling(c_lower) − frozen_safety_margin
```

— signal from the **upper** end of the contrast and `Xi` envelopes, ceiling from the **lower** end,
which is conservative on both sides rather than on one. No open mirror result may enter this gate.
The fixed 5 % allowance is removed.

---

# PE-8 — the resolution-consistency feature model omitted governing features

**Superseded.** `Xi_field`, `Xi_hat`, `G_lat_field` and `Xi_coupon` governed by
`("h_low", "h_high", "bridge_kz")`; `R`, `s`, `C`, `c_field`, `A_field` governed by
`("h_low", "h_high")` regardless of fixture state.

**Why that was unsafe.** The bridge footprint `w` is a resolved feature in its own right and is
**smaller than `kz` for part of the family** (`w = 3` against `kz = 4`), so the smallest feature
governing the bridge conductance could be omitted entirely. The port depth and the duct traverse
were absent. And `R`/`s` for an **open** fixture carry the bridge, so treating them as lane-only
understated their tolerance.

**Effective form.** Two families, and a conservative envelope:

- **lane-only** (`reference_blocked`, `blocked`): `h_low`, `h_high`;
- **bridge-carrying** (`open`, and every `Xi`/`G_lat` quantity): `h_low`, `h_high`, `bridge_w`,
  `bridge_kz`, `port_depth`, `duct_traverse`.

```
tol = KAPPA_RES · ( Σ_features |δ(f·S₂) − δ(f·S₃)| + JUNCTION_ALLOWANCE · max_f |δ(f·S₂) − δ(f·S₃)| )
δ(h) = 0.5/h²      KAPPA_RES = 2.0      JUNCTION_ALLOWANCE = 1.0
```

The junction/end allowance is an explicit extra copy of the worst single feature, declared as a
factor rather than hidden inside a fitted constant. `R` and `s` are split into `R_blocked`/`s_blocked`
and `R_open`/`s_open`. Derived from the measured `50/h²` channel law and the frozen geometry only;
**no 001b output exists or is consulted.** It remains a **consistency test at two resolutions, not
a formal convergence-order estimate.**

---

# PE-9 — cross-resolution `Xi` semantics were undefined

**Superseded.** `select_bridges` consumed one `Xi_coupon` per candidate with no statement of which
resolution or forcing level produced it.

**Why that was unsafe.** Two resolutions and three forcing levels yield up to six coupon estimates
per candidate. Collapsing them to one unspecified number leaves the selection undefined, and a
candidate whose category differs between resolutions could be placed in a categorical slot it does
not unambiguously occupy.

**Effective form.** The candidate record retains `Xi` by **resolution × forcing level × coupon
source**, each with its uncertainty term. Then, frozen before output:

1. forcing-invariance and resolution-consistency gates are applied **first**; a candidate failing
   either is not eligible;
2. `Xi_select` = the **geometric mean** of all valid positive coupon estimates across both
   resolutions and all three forcing levels;
3. the complete conservative envelope `[Xi_lower, Xi_upper]` is retained;
4. category is decided on the **whole envelope**: `below` only if it lies entirely below the
   window, `above` only if entirely above, `inside` only if entirely inside, otherwise
   **`boundary_ambiguous`** and unavailable for a categorical slot;
5. nearest log target chosen on `Xi_select`; ties broken on smaller `w`, then smaller `kz`.

**Underfill is a stop, not an improvisation.** The freeze requires exactly five unique
candidates — one `below`, one `above`, three `inside`. If any slot cannot be filled from
unambiguous candidates, the tranche stops with `DESIGN_BLOCKED_PRE_EXECUTION` and one of the
frozen reason codes: `NO_CANDIDATE_WITHIN_ARTIFACT_BUDGET`,
`NO_CANDIDATE_ADMITTED_BY_REACHABLE_SET`, `INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES`,
`NO_UNAMBIGUOUS_BELOW_CANDIDATE`, `NO_UNAMBIGUOUS_ABOVE_CANDIDATE`,
`SELECTION_UNDERFILLED_AFTER_DEDUPLICATION`. **No P3 slot is ever populated by improvisation.**

---

# PE-10 — matrix rows were not uniquely executable

**Superseded.** Rows carried no identifier, the axial-coupon rows carried no `orientation`, and no
row carried `tau_plus`, `backend`, an audit mode, a retained-record schema or a prerequisite.

**Why that was unsafe.** Two rows could be canonically identical while denoting different runs, an
executor could not tell which coupon orientation a row meant, and a conditional row did not say
what it was conditional on. A matrix that cannot be executed unambiguously cannot be reviewed
unambiguously either.

**Effective form.** Every row carries a stable unique `case_id` and the complete configuration:
`phase · kind · S · forcing_level · forcing · tau_plus · state · variant · bridge · coupon_level ·
coupon_orientation · swapped · perturbation · obstructed · audit_mode · backend · record_schema ·
prerequisite`. Tests assert `case_id` uniqueness, absence of duplicate canonical rows once
`case_id` is removed, distinct representation of both coupon orientations, complete forcing
ladders, that no selection-bearing case is deferred past the freeze, that every conditional row
declares a prerequisite, and that every row resolves to exactly one fixture/solver configuration.

**Counts are recalculated, not preserved.** The number 195 is superseded and is not retained for
cosmetic continuity. The P3/P4 matrix is **instantiated only after the bridge selection is known**
and is hashed into the proposed freeze artifact.

---

# PE-11 — execution authorization was all-or-nothing

**Superseded.** A single module-level `EXECUTION_AUTHORISED = False`.

**Why that was unsafe.** Flipping one boolean to authorise the pre-freeze phases would have
authorised the primary experiment and Arm J in the same act. The freeze gate protected P3, but a
syntactically valid freeze artifact was the only thing standing between an authorised head and the
primary computation.

**Effective form.** `AUTHORISED_SOLVING_PHASES = ()` — a source-controlled allowlist. At the
corrected head it is empty and **every** solving mode refuses. Authorising `P0/P1/P2` cannot
authorise `P3` or `P4`; `P3` stays hard-refused even when a syntactically valid freeze exists; each
addition to the allowlist is a separate reviewed source commit, and the resulting exact head is the
object reviewed for execution.

Runtime execution additionally requires: a clean working tree; a real git commit and tree; exact
protocol/config/matrix hashes; complete non-null input-file hashes; a supported backend
(`"reference"` only — a backend argument is never accepted and then silently routed to the
reference solver); the exact solver configuration; and valid predecessor phase-completion
manifests (P1 needs P0; P2 needs P0 and P1; P3 needs P0, P1, P2, the reviewed freeze, the reviewed
instantiated matrix and its own authorisation). Freeze generation requires hashed **real** P0/P1/P2
records and refuses hand-entered candidates. `execution_authority()` **fails closed** — it raises
rather than returning `None` for unavailable git identity, missing files, a dirty tree, an
unsupported backend or incomplete dependencies.

---

# PE-12 — remaining consistency defects

| defect | superseded | effective |
|---|---|---|
| `g_ref` built from a binary float | `Fraction(G_REF)` where `G_REF = 2.0e-6` — an exact rational **of an already-rounded float** | `G_REF_EXACT = Fraction(1, 500_000)`; `G_REF = float(G_REF_EXACT)` is derived, never the source of truth |
| `tau_plus = 1.2` | described as "retained as the cross-check value" but scheduled nowhere | **scheduled**: two P0 rows on the reference-blocked mirror fixture at central forcing, both resolutions, compared against their `tau_plus = 2.0` counterparts |
| refused-row count | `EXECUTION_MATRIX.md` said 131, `PRE_EXECUTION_REVIEW.md` said 133 | one **computed** number, emitted by `execution_matrix()` and quoted identically everywhere |
| replicate placement | "one replicate per phase" against replicates in only P0, P1 and P3 | three replicates, in P0, P1a and P3 — the three phases producing decision-bearing records from *distinct fixture families*; P2a re-uses those families and P4 re-uses P3's fixtures with an obstruction, so a fourth would add no independent evidence. Stated as the rule, not as an exception |
| generated artifacts unversioned | no correction marker | every generated artifact carries `correction_version` |

Unchanged by PE-12: **no Route B**, **no new pressure component**, **no solver change**, and
**RP-D-LC-001's files and result remain byte-identical**.
