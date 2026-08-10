# RP-D-LC-001b — pre-execution errata

```
APPEND-ONLY. Each erratum supersedes part of the frozen preflight; nothing above an
erratum line is rewritten, and no superseded value is deleted.
PRE-EXECUTION THROUGHOUT — no RP-D-LC-001b lattice-Boltzmann solve has run at any point
in this lineage, before or after any erratum here.
```

Effective correction version: **`PREFLIGHT-C3`** (see PE-22). Generated artifacts under
`generated/` carry `correction_version` so a machine-readable record can never be mistaken for
a superseded one. Lineage: **C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) → **C3**.

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


---

# PE-13 — exact-head RE-REVIEW at `2cf0b63` was NOT APPROVED; C2 correction record

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REREVIEW_NOT_APPROVED_C2_AND_PREFREEZE_EXECUTOR_REQUIRED`

**Reviewed head:** `2cf0b63ba2670de423a39f9563822563a3cb59b5`
**Reviewed tree:** `c8a22d140b75142cdbd5db03dea55f20382bb079`

## C1 outcomes ACCEPTED and preserved unchanged

The common-mode-port apparatus (accepted in principle); RP-D-LC-001 closed and immutable; exactly
nine unique axial conservation planes; distinct inverse **volume** flux and conservation **mass**
flux; strict non-finite rejection; the full-vector fluid-node Mach control; full pre-freeze forcing
ladders; candidate-specific blocked-mirror contrast intervals; the expanded bridge feature model;
two-sided reachable-set admission; phase-specific authorization with an **empty** allowlist; no
Route B; no solver-component change; no open mirror case before P3.

## Superseded C1 machine-readable artifacts

Retained so anything bound to them stays traceable. **These supersede the C0 hashes in PE-0; both
generations are kept.**

| artifact | superseded C1 SHA-256 (`2cf0b63`) |
|---|---|
| `generated/protocol.json` | `9b60b4d511d6153d92da14c7f7235f335536fa937958cc035eb4a9d6f163ea11` |
| `generated/fixture_spec.json` | `11f1798c420373daf4ceff6d71cacf58318852cf01f55b3af85ab562acae0fec` |
| `generated/execution_matrix.json` | `5d246088a1404ddb2ead1acfa4bc7074de9a8244688d28aca7c698e7d0e3193e` |
| `generated/preflight_status.json` | `5bc0d5779218554b74106b38dcdcd73901a7502e10dfcec866d1f51891f834e1` |

Superseded C1 counts: **407** adaptive maximum, **82** mandatory, **325** refused,
`N_FROZEN_BRIDGES = 5`, Arm J **20** solves. No bridge freeze existed at `2cf0b63` and none exists
now, so no freeze is invalidated.

## C2 blockers

| id | blocker | superseded C1 form | effective C2 form |
|---|---|---|---|
| PE-14 | **zero-driver magnitude false-green** | the zero-driver gate tested only `max−min` plane consistency, so four **equal, materially nonzero** transverse mass fluxes passed | the verdict requires **both** a magnitude gate on `max|q_mass|/axial_mass_scale` **and** the consistency gate on the plane range, each against `TOL_BRIDGE_LEAKAGE_REL` |
| PE-15 | **the lateral pressure gap was never measured** | `y_face1`/`y_face2` existed in the frozen metadata and nothing read them; a geometry label alone certified "zero lateral driver" | compact pressure-face records on both faces over the exact bridge footprint, `Δp_lateral` adjudicated against a frozen tolerance, and `Δp/g` and `q_lat/g` retained for the componentwise checks |
| PE-16 | **the "continuation" did not force a longer run** | the wrapper raised `max_steps` while leaving `min_steps = 2000`, so the solver could stop at its original convergence point and the audit could be a no-op | a true **fixed-step re-execution**: `min_steps = max_steps = target`, `target = CHECK·⌈1.5·base_steps/CHECK⌉`, with `FIXED_STEP_REEXECUTION_1P5X` naming and distinct run-mode statuses |
| PE-17 | **numerical-discrepancy coverage was extrapolated** | the bound was measured on the smallest and largest bridge and applied to all twelve, with no proved monotonic envelope | fixed-step evidence for **every selection-bearing case**: each candidate × {blocked, open} × {S=2, S=3} × {low, central, high}, plus the coupon and blocked-mirror rows that build `Ξ` and `c` |
| PE-18 | **case, manifest and freeze lineage were weak** | a manifest passed on a *nonempty* `completed_cases` list; `build_freeze` accepted free-form candidate dicts, envelopes and record hashes | immutable atomic case records keyed to `case_id` and row hash; validated phase ledgers that reopen and rehash every cited record; `assemble_p2b_from_runs` derives everything from records |
| PE-19 | **there was no phase runner** | the driver refused, and there was nothing behind the refusal | a real deterministic pre-freeze executor for P0/P1a/P1b/P2a and arithmetic P2b, source-controlled and unreachable because the allowlist is empty |
| PE-20 | **the freeze required an above-window slot** | five slots: one below, three inside, **one above** — but the corrected two-sided reachable-set gate can make an above-window candidate inadmissible under its own safety requirement | **four** slots: one below, three inside. "Above" is retained as an optional **diagnostic** category. The safety margin is unchanged and is not tunable to fill a slot |
| PE-21 | **exact forcing identity stopped at the constant** | `G_REF_EXACT` was exact, but rows, records, manifests and freezes carried only the runtime float, and 12-dp JSON rounding became the de-facto identity | every forcing-bearing row and record carries `forcing_exact = {numerator, denominator}` derived from `G_REF_EXACT`, the float is derived **from** it, and the exact form enters `case_id` and row hashing |

## The reviewer's four-slot decision, recorded (PE-20)

C1's own `PRE_EXECUTION_REVIEW.md` §11.6 raised the tension and put three responses to the
reviewer. **The reviewer chose option 2: re-freeze the rule at four slots.** The rationale is
recorded here so it is not re-litigated:

- decision clause 2 requires **≥3 in-window cases at each resolution** — the in-window slots carry
  it, and an above-window candidate contributes nothing to that count;
- decision clause 5 requires **monotonicity across the frozen family** — one below plus three
  inside supplies four ordered points, which is sufficient to test monotonicity;
- the corrected two-sided reachable-set gate can make an above-window candidate **inadmissible
  under its own safety requirement**, so requiring one would be requiring a candidate the gate is
  designed to exclude;
- **the `0.10·K` safety margin is unchanged and is not tunable to fill a slot.**

`NO_UNAMBIGUOUS_ABOVE_CANDIDATE` is removed as a required-selection stop.
`NO_UNAMBIGUOUS_BELOW_CANDIDATE` and `INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES` are preserved,
as is exact-four-or-stop.

## What did NOT change in C2

The Stage-A question · the apparatus and the whole geometry · `ARTIFACT_BUDGET_R_ABS = 1.0e-3` ·
`TOL_LINEARITY_REL = 1.0e-4` · `TOL_MASS_REL = 1.0e-3` · `TOL_BRIDGE_LEAKAGE_REL = 1.0e-3` · the
forcing law and both ladders · the `0.10·K` reachable-set margin and its conditioning
justification · the Route-A observable contract (**Route B remains unauthorized**) · **no solver
change** · the claim ceiling · **RP-D-LC-001 byte-unchanged and historically immutable** ·
`AUTHORISED_SOLVING_PHASES = ()`.

---

# PE-14 — the zero-driver transverse gate could pass a materially nonzero flux

**Superseded.** For an expected-zero-driver case the verdict was
`|max(q) − min(q)| / axial_mass_scale ≤ TOL_BRIDGE_LEAKAGE_REL`.

**Why that was unsafe.** That statistic tests whether the four planes **agree**, not whether the
flux is **zero**. Four *equal* transverse mass fluxes have a range of exactly zero and passed at any
magnitude — so a fixture leaking a large, perfectly consistent lateral current through the bridge
with no lateral driver would have returned a green negative control. The control exists to
establish that opening the bridge creates no flow when nothing drives it; consistency alone cannot
establish that.

**Effective form.** The expected-zero-driver verdict requires **both**, each against
`TOL_BRIDGE_LEAKAGE_REL = 1e-3` (unchanged, and not loosened):

```
magnitude:    max_i |q_mass_i| / axial_mass_scale   ≤  TOL_BRIDGE_LEAKAGE_REL
consistency:  |max_i q_mass_i − min_i q_mass_i| / axial_mass_scale ≤ TOL_BRIDGE_LEAKAGE_REL
```

and the record retains, separately and all finite: the four `q_mass_i` and `q_volume_i`;
`axial_mass_scale`; `max_abs_lateral_mass_flux` and its relative form; `mean_lateral_mass_flux` and
`|mean|` relative; `plane_range_mass` and its relative form; the signed entry/exit balance;
both tolerances; and **separate verdicts** for magnitude and consistency.

**The magnitude requirement is NOT applied to a genuinely driven bridge**, where a nonzero lateral
flux is the physics under test. The driven case keeps the hybrid rule and records the physical
lateral-flow magnitude, the plane-to-plane consistency and the relative-gate applicability as three
distinct things.

---

# PE-15 — the lateral pressure gap was declared in metadata and never measured

**Superseded.** `fixture_meta` froze `y_face1` and `y_face2`; nothing read them. The
identical-path control's "zero lateral driver" was asserted from the **geometry label**
(`variant == "identical"`), and `case_record` passed that label straight into the transverse gate.

**Why that was unsafe.** The cross-product gap vanishing *analytically* for an identical-path
network is a statement about the two-node model, not a measurement of the discretised fixture. A
voxelised fixture with junction effects, an asymmetric solver residual or a construction error can
carry a nonzero measured mid-face pressure difference while still being labelled identical. A
label may not certify a physical condition that the fixture can be interrogated for directly —
especially when that condition is the premise of the decisive negative control.

**Effective form.** Compact pressure-face records on both frozen faces, over the **exact bridge
`(x, z)` footprint**, using the same effective-pressure convention as the axial records —
`p_eff = ρ/3 − g·x`, evaluated **nodewise before averaging**, so the body-force potential is
subtracted correctly across a multi-`x` footprint. Each face retains `plane_id`, orientation, index,
footprint bounds, `n_fluid`, `rho_mean`/`rho_sd`, `p_mean`/`p_sd`, `p_min`/`p_max`, the sign
convention and the mask identity. Every bridge-carrying case then derives `p_face1`, `p_face2`,
`delta_p_lateral`, `delta_p_lateral_over_g`, an axial pressure-normalisation scale, the normalised
gap, a conservative face uncertainty, `expected_zero_driver`, `measured_zero_driver_pass`, the
tolerance and a reason.

`TOL_LATERAL_DRIVER_REL` is frozen **before output** at the programme's 0.1 % nuisance scale
applied to the normalised gap. **For an identical-path control, execution validity now requires the
MEASURED gap to clear it** — the geometry label supplies only the *expectation*.

`q_lat/g` and `delta_p_lateral/g` are retained so the already-frozen componentwise forcing checks
can be evaluated on them. No large field arrays are retained.

---

# PE-16 — the "continuation" audit did not force a longer run

**Superseded.** The audit raised `max_steps` while leaving `min_steps = 2000`, so the solver's own
convergence test could stop it at the original step count and the audit could return the base
result. An audit that can be a no-op is not evidence.

**Effective form.** A deterministic **fixed-step re-execution**, with no change to the solver core:

```
target_steps = CHECK · ⌈ CONVERGENCE_AUDIT_FACTOR · base_completed_steps / CHECK ⌉
min_steps = max_steps = target_steps
```

Required and checked: the base case actually converged before its normal maximum;
`target_steps > base_completed_steps`; `target_steps` is an exact multiple of `CHECK`; a frozen
`MAX_STEPS_AUDIT` large enough for the 1.5× rule; and the audit's actual completed steps equal
`target_steps` **exactly**.

Named `FIXED_STEP_REEXECUTION_1P5X` in machine-readable records — **not** "continuation", because
the solver does not resume from saved state.

`converged = steps < MAX_STEPS` is no longer used for audits. Four distinct run statuses:
`NORMAL_CONVERGED`, `NORMAL_UNCONVERGED`, `FIXED_STEP_AUDIT_COMPLETED`,
`FIXED_STEP_AUDIT_INCOMPLETE`. **An unconverged normal case stops its phase under the frozen
UNCONVERGED semantics; an audit may never rescue it.**

Retained: base `case_id` and record hash, base completed steps and convergence status, audit target
and actual steps, audit completion status, base and audit observables, the discrepancy terms and
both exact solver configurations.

---

# PE-17 — numerical-discrepancy evidence was extrapolated across candidates

**Superseded.** Eight audit runs on the smallest and largest bridge, with the worst applied to all
twelve candidates. No monotonic envelope was proved, and geometric extremes are not a proof.

**Effective form.** Fixed-step evidence for **every selection-bearing case** — each candidate ×
{blocked, open} × {S = 2, S = 3} × {low, central, high} for the identical-path artifact, plus the
axial-coupon, bridge-coupon and candidate-blocked-mirror rows that build `Ξ` and `c`. The artifact
gate `|R_identical − 1| + u_R ≤ 1e-3` must pass at **every** required combination.

**P1a is demoted to a triage screen.** It may **reject** a candidate when the point estimate alone
(or an already-established valid lower bound) makes success mathematically impossible, because
every omitted uncertainty term is non-negative. It may **not admit** a candidate, and it may not
call a central result a final artifact upper bound before the fixed-step evidence exists.

The P2b record states, for every uncertainty term: source case IDs, source record hashes, method,
point estimate, uncertainty, interval, whether it overlaps another term, and its final use in
artifact, `c` or `Ξ` admission. **No placeholder or caller-supplied uncertainty may enter a
freeze.**

---

# PE-18 — case, manifest and freeze lineage were too weak to bind a decision

**Superseded.** `require_phase_manifests` accepted any manifest carrying a **nonempty**
`completed_cases` list with matching configuration hashes; `build_freeze` accepted free-form
candidate dictionaries, `xi_envelope` values, eligibility booleans and `record_hashes`, checking
only that the cited hashes appeared *somewhere* in a manifest.

**Why that was unsafe.** A manifest could claim a phase was complete while omitting rows; one
record hash could be cited for several physically distinct candidates; and the freeze's scientific
content was whatever the caller passed in. That is a freeze bound to assertions, not to evidence.

**Effective form.** Three layers, each validated:

- **Immutable case records** — one per solve, written atomically (temp file + rename), never
  overwritten, filename deterministically derived from `case_id`, carrying the schema and
  correction versions, phase, `case_id`, the canonical row and its SHA-256, the exact forcing
  rational and the runtime float, geometry and mask identity, source commit/tree, the
  execution-authority hash, the configuration hashes, backend and dependencies, solver
  configuration, predecessor-manifest hashes, run mode and status, every required compact
  scientific record, no large fields and no non-finite values. A resume verifies the existing file
  and its hash and authority and reuses it **only** on an exact match, otherwise fails closed.
- **Strong phase manifests** — a validated ledger, not a list: expected mandatory and conditionally
  eligible case IDs, completed/refused/failed ledgers, per-record paths and hashes, per-row hashes,
  adaptive-decision inputs and result, terminal status and stop reason, and counts reconciled to
  the planned phase. Validation reopens every cited record, recomputes its hash, checks its
  `case_id`, row hash, source commit/tree and authority, rejects missing, duplicate and extra
  rows, rejects a record reused for a different case or a hash cited for two physically distinct
  rows, validates predecessor manifest hashes, and recomputes adaptive eligibility and refusal from
  predecessor records. For P1b and P2a the expected rows are **derived mechanically** from
  validated predecessor decisions, never supplied by a caller.
- **Record-derived P2b** — `assemble_p2b_from_runs(runs_dir, …)` supersedes
  `build_freeze(selection, manifests, instantiated_rows)`. It validates the P0/P1a/P1b/P2a
  manifests, loads every record itself, and **recomputes** the forcing-invariance,
  resolution-consistency, zero-driver transverse, measured lateral-pressure-gap, numerical
  discrepancy, artifact upper bound, blocked-mirror `c` interval, coupon `Ξ` envelope and
  reachable-set admission before applying the four-slot rule. It accepts no free-form selection,
  envelope, interval, eligibility flag or hash list. Every candidate quantity in the proposed
  freeze cites its exact contributing case IDs and record hashes, and a single record hash cannot
  bind two candidate geometries.

**P3 and P4 remain unauthorized even after a syntactically valid proposed freeze exists.**

---

# PE-19 — the refusal had nothing behind it

**Superseded.** The driver refused every phase and contained no runner, so nothing established
that the refused work was implementable, deterministic or correctly ordered.

**Effective form.** A real pre-freeze executor for P0, P1a, P1b, P2a and arithmetic P2b:
validate the phase → validate authorization → resolve the exact execution authority → validate
predecessor manifests → derive the exact phase rows → apply the frozen adaptive decisions → resolve
each row to exactly one fixture or coupon → call the single guarded solver call site → build the
compact record → validate it → write it atomically → build and validate the phase manifest → stop
on any invalid or unconverged decision-bearing case.

`jobs = 1`; deterministic matrix ordering; no hidden exploratory rows; no overwrite; exact resume;
no fallback backend; no looser retry; no automatic margin or tolerance adjustment; no open mirror
case before P3; and **P2b makes no solver call**.

Orchestration is factored so a unit test may inject a fake result provider. **The user-facing CLI
exposes no option that accepts an arbitrary solver callback.** At this head every solving phase
still refuses, because `AUTHORISED_SOLVING_PHASES = ()`, and the tests assert that the real
`lb_reference.solve` was never reached.

---

# PE-20 — the freeze required an above-window slot the gate can exclude

Superseded: `N_FROZEN_BRIDGES = 5` (one below, three inside, one above) and
`NO_UNAMBIGUOUS_ABOVE_CANDIDATE` as a required-selection stop. Effective: **four** slots (one
below, three inside), "above" retained as an optional diagnostic category, that stop code removed
from the required set. Rationale and the reviewer's decision: PE-13 above. All P3/P4 templates,
Arm J and every count regenerate from four; **no C1 count is preserved for cosmetic continuity.**

---

# PE-21 — exact forcing identity stopped at the constant

**Superseded.** `G_REF_EXACT = Fraction(1, 500_000)` was exact, but `forcing_central` and
`forcing_ladder` returned floats and every downstream artifact carried only that float. With
records rounded to twelve decimals, the *scientific identity* of a forcing level had become a
rounded decimal.

**Effective form.** `forcing_exact(S, level)` returns an exact `Fraction` derived from
`G_REF_EXACT`, `S` and the frozen factor. Every forcing-bearing matrix row and case record carries
`forcing_exact = {"numerator": …, "denominator": …}` alongside the runtime float; the float is
**derived from** the rational and is verified to equal `float(Fraction(n, d))`; the exact
representation enters `case_id` and row hashing; and the rational is never reconstructed from a
binary float.


---

# PE-22 — exact-head review at `c666707` was NOT APPROVED; C3 correction record

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C3_EXECUTOR_AND_ASSEMBLER_CORRECTION_REQUIRED`

**Reviewed head:** `c66670770d6b34b355fe29dba384102fc59827d7`
**Reviewed tree:** `002f7bae2d5a6c0f890b6144ae515b4af73d97ed`

## C2 outcomes ACCEPTED and preserved unchanged

The common-mode-port apparatus; common-mode blind ports in both fixtures; no identical-path
subtraction and no post-hoc artifact correction; zero-driver lateral flux gated on **magnitude
and** consistency; measured lateral pressure faces; full-vector fluid-node Mach; the exact
nine-plane axial conservation set; strict finite canonical serialisation; exact rational forcing
identity; `g ∝ S⁻³`; both-resolution three-level pre-freeze ladders; the fixed-step re-execution
**concept**; candidate-specific blocked-mirror contrast; the corrected bridge feature model **in
principle**; **four** frozen bridges (one below, three inside) with no required above-window slot;
the **`0.10·K` reachable-set margin unchanged**; Stage B and Paper 4 unauthorized; RP-D-LC-001
closed, immutable and `INVALID_EXECUTION`; no Route B; no solver-core change; no open mirror
result before P3.

**None of those is redesigned or relaxed here.**

## Superseded C2 machine-readable artifacts

Retained alongside the C0 and C1 sets; **all three generations are kept.**

| artifact | superseded C2 SHA-256 (`c666707`) |
|---|---|
| `generated/protocol.json` | `ae52600c5d2d8ce0a8b86d31545b6fc40b92228fc805542dc3a9ee8ac645a21f` |
| `generated/fixture_spec.json` | `d931b3616948995a45237c7c781503dc5fc25618ae04be015f4b03b03fceb074` |
| `generated/execution_matrix.json` | `6e6140a1b07b2fbf13e69a12044d5927e3a6f3c10cca91356316dbd85410f81c` |
| `generated/preflight_status.json` | `5d8cf61abdac1f4399de1f282441c5fd139b8d3f1e44c7b3c7ac5d1a0708ec73` |

Superseded C2 counts: **703** adaptive maximum (**383** normal + **320** audits), **112**
mandatory, **591** refused. **No C2 total is preserved for continuity**; every count is recomputed
by the corrected generator and verified by test.

## What the C2 head actually was

C2 shipped a great deal of correct machinery and a **P2b assembler that could not run**. The two
findings that matter most are not tolerance questions but implementation facts:

- **the assembler raised on its first candidate.** `artifact_from_pair()` returns `case_ids` and
  `record_sha256` (both plural, both lists); the assembler read `v["case_id"]` (singular) and then
  called `set()` over lists of lists. `KeyError`, then `TypeError: unhashable type: 'list'`. No
  proposed freeze could ever have been produced;
- **the executor and its validator disagreed about what a phase is.** The executor recorded
  adaptively ineligible rows as `refused`; the validator built its row universe from the *eligible*
  subset only and rejected anything outside it as "cases that are not in its plan". Any adaptive
  phase would have written a manifest that its own validator refused.

Neither could be caught by the C2 tests, because no test drove the assembler on real records or
ran an adaptive phase end to end. **C3 adds exactly that test** (§19 of the brief), which is why
the remaining fifteen defects below were found at all.

## C3 blockers

| id | blocker | superseded C2 form | effective C3 form |
|---|---|---|---|
| PE-23 | **P2b singular/plural evidence keys** | assembler read `v["case_id"]`; `artifact_from_pair` returns `case_ids` | one validated canonical evidence schema, plural throughout |
| PE-24 | **nested record-hash lists** | `sorted(v["record_sha256"] …)` over lists, then `set()` over lists | flat ordered `list[str]` of canonical lowercase SHA-256, unique within role |
| PE-25 | **P2b persisted nothing** | returned an in-memory dict | durable atomic `candidate_ledger.json`, `proposed_bridge_freeze.json`, `instantiated_p3_p4_matrix.json`, `manifest_P2b.json` |
| PE-26 | **adaptive ledger/validator contradiction** | executor refused ineligible rows; validator's universe was the eligible subset | an explicit **full phase universe** with a mutually exclusive `completed ⊎ failed ⊎ refused` partition |
| PE-27 | **predecessor success unenforced** | any manifest with matching hashes satisfied the next phase | a predecessor satisfies a phase only at `terminal_status == PHASE_COMPLETE`, with the exact required key set and recursive hash validation |
| PE-28 | **no forcing-invariance adjudication** | the ladder existed in the matrix and in prose; nothing evaluated it | executable componentwise and boundary-level gates; a failure makes the candidate **unavailable** |
| PE-29 | **no resolution-consistency adjudication** | the tolerance was only ever an additive widening | an explicit S=2/S=3 pass/fail gate; a failure makes the candidate **unavailable** |
| PE-30 | **normal and audit records mixed** | coupon selection matched on `kind`, so audits entered `Ξ` estimates as independent observations | audits are **paired discrepancy evidence only**; point estimates use NORMAL records exclusively |
| PE-31 | **artifact `u_R` reused for `c` and `Ξ`** | one `u_num_c` from the artifact combinations widened both | three separate uncertainty families, each from its own normal/audit pairs |
| PE-32 | **node-offset term silently zero** | `numerical_discrepancy_R` accepted offsets; the assembler never passed any | superseded and replaced by a **measured pressure-plane discrepancy** from scheduled diagnostic rows |
| PE-33 | **candidate-blocked used the lane-only feature family** | `c_field` tolerance ignored the ports the blocked fixture actually has | five governing-feature families, with `candidate_blocked_common_mode_ports` for the blocked candidate |
| PE-34 | **production injection** | `execute_phase(..., result_provider=None, authority=None)` | the production signature is `(phase, runs_dir, backend="reference")`; the test seam is private and writes `provenance_mode = TEST_ONLY`, which production validators reject |
| PE-35 | **per-case solver configuration was global** | the record copied the authority's `tau_plus = 2.0` into a `tau_plus = 1.2` cross-check row | the effective configuration is recomputed from the canonical row and required to match exactly |
| PE-36 | **Arm J was not physically resolvable** | P4 rows carried `obstructed = true`; the resolver ignored it | an additive 001b plenum-obstruction transform, applied iff `obstructed`, with its own specification and mask hash |
| PE-37 | **the replicate claim was unenforced** | three replicate rows, and nothing compared anything | a canonical `scientific_payload_sha256` bound to the base case and required equal |
| PE-38 | **CLI contract defects** | `--output` ignored, `--jobs` accepted and unused, P2b printed a solve count | `--output` is the runs directory, `--jobs` accepts only 1, P2b reports arithmetic status |
| PE-39 | **P2b shared the solving gate** | `AUTHORISED_SOLVING_PHASES` governed P2b | separate `AUTHORISED_ASSEMBLY_PHASES`; both empty at this head |

---

# PE-23 — the P2b evidence schema used singular keys against plural producers

**Superseded.** `artifact_from_pair()` returns `case_ids` and `record_sha256` — plural names, list
values. `assemble_p2b_from_runs()` read `v["case_id"]`.

**Why that was unsafe.** It was not merely a crash: the assembler is the one place where the
freeze's scientific content is derived, and it had never been executed against real records. A
schema that two collaborating functions disagree about cannot bind evidence to a decision.

**Effective form.** One canonical, validated artifact-evidence schema, plural throughout, flat:

```
candidate_id · resolution · forcing_level ·
normal_case_ids[] · normal_record_sha256[] ·
audit_case_ids[]  · audit_record_sha256[]  ·
pressure_plane_case_ids[] · pressure_plane_record_sha256[] ·
R_point · u_fixed_step_R · u_pressure_plane_R · u_serialization_R · u_artifact_R ·
artifact_upper · pass · lineage
```

Every hash is a canonical lowercase 64-character SHA-256; every case ID and hash is unique within
its role; normal and audit evidence are distinct; every audit names its exact normal base. The
schema is validated **before** any scientific use, and no `set()` is ever applied to a list-valued
object.

---

# PE-24 — record-hash lists were nested

**Superseded.** `sorted(v["record_sha256"] for v in …)` produced a list **of lists**, which was
then passed to `set()`.

**Effective form.** Flat ordered `list[str]` at every level, validated by
`assert_flat_hash_list()`, which rejects nesting, duplicates, non-strings and anything that is not
a 64-character lowercase hex digest.

---

# PE-25 — P2b produced nothing durable

**Superseded.** `assemble_p2b_from_runs()` returned an in-memory dictionary. Nothing was written,
so nothing could be reviewed, re-opened, re-validated or bound by a later phase.

**Effective form.** A future authorised P2b atomically writes `candidate_ledger.json`,
`proposed_bridge_freeze.json` (**only** when exactly one below and three inside pass),
`instantiated_p3_p4_matrix.json` and `manifest_P2b.json`, with canonical serialisation,
`allow_nan=False`, temp-file + rename, deterministic filenames, **no overwrite**, exact-match
resume and fail-closed on a mismatched existing file. **A failed selection still writes a durable
decision and manifest with a design-block terminal status — but no proposed scientific freeze.**

---

# PE-26 — the executor and its validator disagreed about the phase universe

**Superseded.** The executor wrote adaptively ineligible rows into `refused`; the validator derived
its universe from the *eligible* subset and rejected anything else as an extra case. An adaptive
phase would have produced a manifest its own validator refused.

**Effective form.** An explicit **full phase universe**:

```
phase_universe_case_ids  =  completed ⊎ failed ⊎ refused        (pairwise disjoint, exact)
```

with `mandatory_case_ids`, `conditionally_eligible_case_ids` and `adaptively_ineligible_case_ids`
retained separately. Adaptively ineligible rows remain **members of the universe** and are recorded
as refused with a frozen reason; early-stop rows carry a distinct frozen reason; eligibility is
recomputed from predecessor evidence and is never caller-supplied.

---

# PE-27 — a stopped predecessor could satisfy the next phase

**Superseded.** `require_phase_manifests` checked configuration hashes and a nonempty ledger; it
never looked at `terminal_status`. A phase that stopped `UNCONVERGED`, `INVALID_CASE` or
`DESIGN_BLOCKED` would have satisfied its successor.

**Effective form.** A predecessor satisfies a phase **only** at `terminal_status ==
PHASE_COMPLETE`. The exact required predecessor key set is required per phase — not merely
whatever hashes happen to be present — and predecessor hashes are validated **recursively**.

---

# PE-28 — the frozen forcing-invariance gates were documentation, not code

**Superseded.** The `×0.5/×1/×2` ladder was scheduled in the matrix and described in the protocol.
**Nothing evaluated it.** `TOL_LINEARITY_REL = 1e-4` appeared only in a tolerance table.

**Why that was unsafe.** This is the control whose failure produced `INVALID_EXECUTION` in
RP-D-LC-001. Scheduling the rows without adjudicating them would have reproduced the 001 failure
mode one level up: the evidence would exist and no verdict would be taken from it.

**Effective form.** Executable gates, grouped by scientific family, candidate, state, resolution
and orientation, over **NORMAL** records only:

- componentwise, on `Q_open/g`, `Q_blocked/g`, `ΔP_open/g`, `ΔP_blocked/g`, `q_lat/g`,
  `Δp_lateral/g` where applicable — the exact frozen relative-spread rule against an unchanged
  `TOL_LINEARITY_REL = 1e-4`;
- zero-safe for expected-zero quantities: never divided by their own mean, judged on the frozen
  absolute scale with separate magnitude and consistency verdicts, all values required finite;
- boundary-level stability for `R`, `s`, `c_field` and `Ξ` **before** any of them informs artifact
  admission, a `c` interval, a `Ξ` envelope, reachable-set admission, a category or the selection.

**A failed gate makes the candidate UNAVAILABLE. It does not widen an envelope.**

---

# PE-29 — the resolution-consistency tolerance was only ever an additive widening

**Superseded.** `resolution_consistency_tolerance()` was derived ex ante and then used solely to
inflate the `c` and `Ξ` intervals. A candidate that was *inconsistent* between resolutions was
therefore admitted with a wider interval rather than rejected.

**Effective form.** An explicit S=2 vs S=3 **pass/fail** gate on each decision-bearing quantity,
retaining both estimates, the exact feature envelope, the derived tolerance, the observed
discrepancy, the verdict and the source case IDs and hashes. **A failure makes the candidate
unavailable.** It remains a **two-resolution consistency test, not a convergence-order estimate.**

---

# PE-30 — fixed-step audit records were mixed into scientific estimates

**Superseded.** Coupon and blocked-mirror selection matched on `kind`, which is identical for a
normal row and its audit. Audit records therefore entered the `Ξ` geometric mean and the `c`
measurement set as **independent observations**, roughly doubling the sample with re-runs of the
same configuration.

**Effective form.** Point estimates use **NORMAL records only**. Audits are paired discrepancy
evidence, never observations. Every audit carries `audit_of_case_id`, `base_record_sha256`, both
exact solver configurations, target and actual steps, and `FIXED_STEP_AUDIT_COMPLETED`.

---

# PE-31 — the artifact's `u_R` was reused as the numerical uncertainty for `c` and `Ξ`

**Superseded.** `u_num_c = max(artifact u_R terms)` widened **both** the contrast interval and the
`Ξ` envelope.

**Why that was unsafe.** `u_R` is the discrepancy of a pressure-normalised **conductance ratio**
between an identical-path pair. It is not the discrepancy of a blocked-mirror contrast, nor of a
transverse coupon conductance. Borrowing it is the same class of error as C1's `TOL_MASS_REL`
borrowing (PE-6), one layer further in.

**Effective form.** Three families, each from its **own** normal/audit pairs:

| family | fixed-step term | additional terms |
|---|---|---|
| artifact `R` | `u_fixed_step_R` from the identical-path pairs | pressure-plane, serialisation |
| candidate blocked `c` | `u_fixed_step_c` from the candidate's blocked-mirror pairs | resolution, forcing, non-overlapping pressure/serialisation |
| bridge-coupon `Ξ` | `u_fixed_step_Xi` from the candidate's coupon pairs | resolution, forcing, non-overlapping discretisation/serialisation |

Each term records its method, normal and audit case IDs, record hashes, point estimate,
discrepancy, safety factor, resulting interval, **overlap declaration** and final downstream use.
No term is counted twice across the artifact and reachability sums.

---

# PE-32 — the node-offset term was named but always zero

**Superseded.** `numerical_discrepancy_R(..., R_node_offsets=())` — the parameter existed, the
assembler never supplied it, and `u_node_offset_R` was therefore identically `0.0` while being
reported as a contribution.

**Resolution chosen: option A of the brief — schedule the evidence.** A named term that is always
zero because nothing was passed is worse than no term at all: it reports a bound that was never
computed. The frozen node-surface offsets are `(1, 2)`, and evaluating `R` on them requires **no
extra solve** — they are different planes of the same solution — but they do require the plane
records to exist. Dedicated **pressure-plane diagnostic rows** are therefore scheduled, their
records carry `R` at each frozen offset, and the term is renamed `u_pressure_plane_R` to say what
it measures. A missing pressure-plane record now **fails** the artifact evidence rather than
contributing zero.

The execution matrix is regenerated accordingly. **The C2 total of 703 is not preserved.**

---

# PE-33 — the candidate-blocked fixture was classified as lane-only

**Superseded.** `resolution_consistency_tolerance("c_field")` used `LANE_ONLY_FEATURES`.

**Why that was unsafe.** The *candidate* blocked fixture is not the reference fixture: it carries
the common-mode blind ports, which are a resolved feature of the geometry whose contrast is being
measured. Classifying it as lane-only understated its tolerance — and the ports are the very
element the apparatus depends on.

**Effective form.** Five governing-feature families: `reference_blocked_lane_only`,
`candidate_blocked_common_mode_ports` (lane heights, `w`, `kz`, port depth, divider traverse,
junction/end), `open_bridge_carrying`, `axial_coupon` and `bridge_coupon`. Candidate-blocked
`c_field`, `A_field` and `R_blocked` use the common-mode-ports family.

---

# PE-34 … PE-39 — executor, configuration, Arm J, replicates, CLI and authority

| id | superseded | effective |
|---|---|---|
| **PE-34** | `execute_phase(phase, runs_dir, result_provider=None, backend, authority=None)` — the production API accepted a solver callback **and** an authority object, and would run the gate and then use the caller's authority instead of the gate's | production signature `(phase, runs_dir, backend="reference")`; the authority used is exactly the one the gate returns; the test seam is a private helper whose records carry `provenance_mode = "TEST_ONLY"`, which production manifest and freeze validators **reject** |
| **PE-35** | `make_case_record` copied the authority's global `solver_config`, so a `tau_plus = 1.2` cross-check row recorded `tau_plus = 2.0` | the effective per-case configuration (`tau_plus`, exact rational and runtime forcing, `rtol`, `check`, `min_steps`, `max_steps`, run mode, fixed-step target, `return_fields`, fixture dimensions, backend, dependencies) is **recomputed from the canonical row** and required to match the record exactly |
| **PE-36** | P4 rows carried `obstructed = true`; `resolve_row()` ignored it, so an obstructed row resolved to the **nominal** mask — and P2b hashes the instantiated P3/P4 matrix, so a freeze would have bound rows that did not resolve to their declared physical configuration | an additive 001b plenum-obstruction transform, acting only in the plenum, preserving lane and bridge solids and the mirror relationship, with a frozen specification and its own mask hash, applied **iff** `obstructed`; the resolver **rejects** an obstructed row it cannot construct exactly |
| **PE-37** | three replicate rows and no comparison; the matrix nevertheless claimed they "demonstrate byte-identical reproduction" | a canonical `scientific_payload_sha256` over the effective configuration, the compact scientific outputs and the masks — excluding case identity and file metadata — bound to the base case and **required equal**, with the verdict in the phase manifest |
| **PE-38** | `--output` was ignored, `--jobs` was accepted and never used, and P2b printed `n_rows` as if it were a solve count | `--output` is the runs directory actually used; `--jobs` accepts only `1`; a non-`reference` backend fails before execution; unknown phase, row kind and fixture state all fail closed; P2b reports arithmetic status, candidate count, selection status and artifact paths |
| **PE-39** | `AUTHORISED_SOLVING_PHASES` governed P2b, so authorising the solving phases would have authorised the assembly | separate `AUTHORISED_ASSEMBLY_PHASES`; **both empty at this head**. Authorising P0–P2a does not authorise P2b, authorising P2b does not authorise P3/P4, and a proposed freeze alone authorises nothing |

## What did NOT change in C3

The Stage-A question · the apparatus and the geometry · `ARTIFACT_BUDGET_R_ABS = 1.0e-3` ·
`TOL_LINEARITY_REL = 1.0e-4` · `TOL_MASS_REL = 1.0e-3` · `TOL_BRIDGE_LEAKAGE_REL = 1.0e-3` ·
`TOL_LATERAL_DRIVER_REL = 1.0e-3` · the forcing law and both ladders · the `0.10·K` margin · four
frozen bridges, one below and three inside · the Route-A observable contract (**Route B remains
unauthorized**) · **no solver-core change** · the claim ceiling · **RP-D-LC-001 byte-unchanged** ·
and every phase, solving and assembly alike, **unauthorized**.

