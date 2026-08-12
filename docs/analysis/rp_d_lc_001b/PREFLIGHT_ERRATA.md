# RP-D-LC-001b — pre-execution errata

```
APPEND-ONLY. Each erratum supersedes part of the frozen preflight; nothing above an
erratum line is rewritten, and no superseded value is deleted.
PRE-EXECUTION THROUGHOUT — no RP-D-LC-001b lattice-Boltzmann solve has run at any point
in this lineage, before or after any erratum here.
```

Effective correction version: **`PREFLIGHT-C9`** (see PE-114 … PE-126). Generated artifacts under
`generated/` carry `correction_version` so a machine-readable record can never be mistaken for
a superseded one. Lineage: **C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) →
**C3** (`39533ad`) → **C4** (`e455c67`) → **C5** (`acb4f6a`) → **C6** (`76e5669`) →
**C7** (`b5eb378`) → **C8** (`67c8c23`) → **C9**. Where earlier text conflicts with the effective
C9 sections, **C9 governs**; no earlier erratum is altered or erased. **PE-66 is accepted and
unchanged**, as are both C7 judgment calls and **PE-113**'s correction of the historical
`preflight_status.json` hash.

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


---

# PE-40 — exact-head review at `39533ad` was NOT APPROVED; C4 correction record

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C4_INTEGRATION_AND_AUTHORITY_CORRECTION_REQUIRED`

**Reviewed head:** `39533ade0fd74dc5fa10470710ec672041e62526`
**Reviewed tree:** `1a8594340299cfc80e340012fcc4cda481cd491f`

## Scientific decisions ACCEPTED and preserved unchanged

The common-mode-port apparatus and its blind pockets; no identical-path subtraction and no fitted
or post-hoc artifact correction; exactly nine axial conservation planes; the distinct volume-flux
inverse and mass-flux conservation contracts; the full-vector fluid-node Mach control; `g ∝ S⁻³`
and the exact ladders; `TOL_LINEARITY_REL = 1e-4`; `ARTIFACT_BUDGET_R_ABS = 1e-3`;
`TOL_BRIDGE_LEAKAGE_REL = 1e-3`; `TOL_LATERAL_DRIVER_REL = 1e-3`; true fixed-step re-execution at
`1.5 ×` the base step count; separate discrepancy families for `R`, `c` and `Ξ`;
candidate-specific blocked-mirror contrast; the corrected critical-feature model in principle;
two-sided reachable-set admission and the **unchanged `0.10·K` margin**; exactly four frozen
bridges (one below, three inside) with no required above-window slot; the additive Arm J plenum
obstruction; separate solving and assembly authorization; no Route B; no solver-core modification;
no open mirror before P3; RP-D-LC-001 immutable and `INVALID_EXECUTION`.

**None is weakened, retuned or redesigned here.**

## Superseded C3 machine-readable artifacts

Retained alongside the C0, C1 and C2 sets; **all four generations are kept.**

| artifact | superseded C3 SHA-256 (`39533ad`) |
|---|---|
| `generated/protocol.json` | `e46395b63bcc9d493365a74767475247d640096d834119cc76a35fb2a031e1f8` |
| `generated/fixture_spec.json` | `833f1d5edf8c1b4a54c1b3977ede4d2f14f92196a53738c0ced8c0e1c6d05023` |
| `generated/execution_matrix.json` | `71371972b8553a81b3db98555ccec8b86acfc86108325ff23eee77662a4bb914` |
| `generated/preflight_status.json` | `61214acee1fdcf846eacd6f6a0ede6a04ef5ec77c45fdb6df5afdd0b63003c16` |

Superseded C3 counts: **847** rows = **383** normal + **320** audits + **144** pressure-plane
diagnostic *rows*; **112** mandatory, **735** refused. **No C3 total is preserved.**

## What C3 got wrong

C3 fixed the C2 assembler and the adaptive ledgers, and in doing so introduced two errors of its
own — both in the term it had just created to close PE-32:

- **the "node-offset" quantity is not `R`.** `_pressure_plane_scientific` computed
  `R_at_node_offsets = [C_j / C_0]` **within a single state**, and
  `artifact_evidence_from_records` then compared those numbers against the **open/blocked** ratio
  `R`. A same-state normalised conductance and a cross-state ratio are different quantities; the
  difference between them is not a node-offset sensitivity of `R`. The uncertainty term built from
  it was therefore not measuring what its name claimed;
- **the diagnostic rows called the solver.** The frozen node-surface offsets are re-reads of a
  field that has already been computed. C3 scheduled 144 *rows*, each of which went through the
  result provider, so the planned solve budget was overstated by 144 and the same physics was
  computed twice.

Both are corrected here by extracting the offsets from the field that is already in memory, and
by forming the ratio only from an exactly paired open/blocked pair.

## C4 blockers

| id | blocker | superseded C3 form | effective C4 form |
|---|---|---|---|
| PE-41 | **diagnostic rows made solver calls** | 144 `pressure_plane_diagnostic` rows, each invoking the result provider | a compact node-offset summary retained in the *same* case record, from the field already in memory; **no separate provider call** |
| PE-42 | **same-state normalisation called `R`** | `R_at_node_offsets = C_j/C_0` within one state, compared against the open/blocked `R` | `R_offset_j = C_open_offset_j / C_blocked_offset_j`, formed only after exact open/blocked pairing |
| PE-43 | **face masks were intersected, not paired** | `both = m1 & m2`, silently discarding unmatched nodes | exact elementwise mask equality, equal counts, identical bounds and shape; fail closed |
| PE-44 | **a spatial standard error was adjudicative** | `sd/√n` over spatially correlated LB nodes used as the face uncertainty | retained as `SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND`; the bound comes from fixed-step evidence |
| PE-45 | **no maximum paired-gap control** | only the mean gap was gated, so alternating differences with a zero mean passed | separate `mean_gap_upper_rel` **and** `max_gap_upper_rel`, both required |
| PE-46 | **no fixed-step discrepancy for the pressure gap** | the gap had no audit-derived uncertainty at all | `u_mean_gap` and `u_max_gap` from each normal record's own fixed-step audit |
| PE-47 | **incomplete boundary forcing gates** | `R`, `s`, `A1`, `A2` and actual `Ξ` were never adjudicated | the exact required quantity set is asserted present, not merely intersected |
| PE-48 | **a mass-flux zero gate normalised by volume flux** | `q_lat_mass` scaled by a `Q_volume`-derived quantity | mass quantities use an **axial mass-flux** scale; mass and volume are never mixed in one ratio |
| PE-49 | **raw `G_bridge` gated under the name `Xi`** | the resolution gate compared `G_bridge_coupon` and labelled the verdict `Xi_coupon` | actual `Ξ = G_bridge·(1/A1 + 1/A2)` from exactly matched coupon and blocked-mirror evidence |
| PE-50 | **the successful P2b branch was never exercised** | the synthetic pipeline reached only the design-block branch, and the success path sat under `pragma: no cover` | a nondegenerate synthetic pipeline that selects one below and three inside and writes all four artifacts |
| PE-51 | **P2b schema mismatch** | the writer stored `content_sha256`; the freeze gate required `instantiated_matrix_sha256` | one canonical schema — `rows_sha256` and `instantiated_matrix_file_sha256` — used by writer, validator, freeze gate and executor alike |
| PE-52 | **persisted ≠ returned P2b manifest** | `artifacts_written` was mutated **after** the file was written | no in-memory mutation after persistence; the persisted and returned documents are identical |
| PE-53 | **weak P2b predecessor validation** | `require_phase_manifests` checked only `correction_version` and `terminal_status` for P2b | a dedicated `validate_p2b_manifest()` reopening the manifest, ledger, freeze, instantiated matrix and every predecessor hash |
| PE-54 | **P3/P4 would have executed templates** | the executor's universe was `phase_universe()`, i.e. the *template* rows | P3/P4 consume the **validated instantiated matrix** from `runs_dir` |
| PE-55 | **P3 fixed-step audits were unbound** | created directly, with `audit_of_case_id = None` | generated from their exact primary normal row through the same audited-row constructor |
| PE-56 | **`runs_dir` was ignored by the freeze gate** | `require_freeze` resolved against the repository default | `require_freeze(stage, runs_dir, …)`; every artifact path resolves beneath the directory actually in use |
| PE-57 | **`PROTOCOL.md` still declared C2 effective** | the banner named C1 and C2; §20 was the last effective section | the banner names C0…C4 with precedence, and §21 (C3) and §22 (C4) are appended |
| PE-58 | **manifest validation did not recompute scientific status** | it rehashed records but never re-derived pass/fail, so a manifest could relabel a failed case as completed | one shared `case_decision_verdict()` used by both the executor and the validator, which recomputes and compares |
| PE-59 | **replicate binding was inferred** | the base was found by searching for the first row sharing `S`, state, variant, forcing level and run mode | an explicit `replicate_of_case_id` frozen in the matrix, with full configuration agreement validated |

## What did NOT change in C4

Every accepted scientific decision listed above · the Route-A observable contract · **no
solver-core change** · the claim ceiling · **RP-D-LC-001 byte-unchanged** · and every phase,
solving and assembly alike, **unauthorized**: `AUTHORISED_SOLVING_PHASES = ()` and
`AUTHORISED_ASSEMBLY_PHASES = ()`.


---

# PE-60 … PE-76 — exact-head review at `e455c67` was NOT APPROVED; C5 decision-path and lineage correction

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C5_DECISION_PATH_AND_LINEAGE_CORRECTION_REQUIRED`

**Reviewed head:** `e455c678a2fdd511ce9a30f1d15164f73b9a4481`
**Reviewed tree:** `72eda81e3ddea54ad4714f10c6bb4b347cd6a15a`

Effective correction version from this point: **`PREFLIGHT-C5`**. Lineage:
**C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) → **C3** (`39533ad`) →
**C4** (`e455c67`) → **C5**. Where any earlier text conflicts with the effective C5 sections,
**C5 governs**; nothing above this line is rewritten.

**PRE-EXECUTION THROUGHOUT.** No RP-D-LC-001b lattice-Boltzmann solve has run at any point in
this lineage, including under C5. `AUTHORISED_SOLVING_PHASES = ()` and
`AUTHORISED_ASSEMBLY_PHASES = ()` at the C5 head, and P0, P1a, P1b, P2a, P2b, P3 and P4 all
remain unauthorized.

## What the C5 review ACCEPTED and this correction preserves unchanged

The common-mode-port apparatus; common-mode blind pockets in blocked and open fixtures; no
identical-path subtraction; no fitted or post-hoc artifact correction; the lateral-only bridge
topology; exactly nine adjudicative axial mass-conservation planes; distinct volume-flux inverse
and mass-flux conservation contracts; full-vector fluid-node Mach control; the exact rational
forcing identity; `g ∝ S^-3`; both-resolution three-level forcing ladders;
`TOL_LINEARITY_REL = 1e-4`; `ARTIFACT_BUDGET_R_ABS = 1e-3`; `TOL_BRIDGE_LEAKAGE_REL = 1e-3`;
`TOL_LATERAL_DRIVER_REL = 1e-3`; exact paired lateral pressure faces; same-field node-offset
summaries; `R_offset_j = C_open_offset_j / C_blocked_offset_j`; true fixed-step re-execution;
separate `R`, `c` and `Ξ` discrepancy families in principle; candidate-specific blocked-mirror
contrast; two-sided reachable-set admission; the unchanged `0.10·K` reachable-set safety margin;
exactly four selected bridges (one unambiguously below, three unambiguously inside); no required
above-window bridge; the additive Arm J obstruction; explicit audit and replicate base IDs;
full-universe adaptive manifests; shared case-level scientific reclassification; separate solving
and assembly authorization; no Route B; no solver-core modification; no open mirror case before
P3; RP-D-LC-001 immutable and `INVALID_EXECUTION`.

**None is weakened, retuned or redesigned here.**

## Superseded C4 machine-readable artifacts

Retained alongside the C0, C1, C2 and C3 sets; **all five generations are kept.**

| artifact | superseded C4 SHA-256 (`e455c67`) |
|---|---|
| `generated/protocol.json` | `9d1853b841067896562bd5fbdb3a590dcbbfe0a9f0cca5af01b00f0d08764292` |
| `generated/fixture_spec.json` | `c50521a10059fbc8af37c6b6a60fcc32f6e916b5be182c6d92a1f8d9eed75bf0` |
| `generated/execution_matrix.json` | `734e6fadf972f9454928a66578aa626f71d8ba00e0a6c4dcce0e5b63647d1220` |
| `generated/preflight_status.json` | `f3ecfd3afef8517bbff831bf2cac1c8740d02a43a6c5cfe972eca12ce1f44752` |

Superseded C4 counts: **703** rows = **383** normal + **320** audits, **0** pressure-plane
diagnostic rows; **112** mandatory, **591** refused. **No C4 total is preserved cosmetically** —
every C5 count is regenerated from the machine authority, and 703 survives only because the
generator independently reproduces it.

## What C4 got wrong

C4 corrected the C3 node-offset term, the pressure-face pairing and the P2b schema. It left the
**decision path** and the **evidence lineage** short of what the corrected apparatus needs:

- the audit-adjusted pressure upper bound was **implemented but never called** by the production
  scientific path, and a point mean-gap screen stood in the final verdict's place;
- the boundary-level forcing set had narrowed to `c_field` alone, so `R`, `s`, `A1`, `A2`, the
  aggregate area and actual `Ξ` were never adjudicated at all;
- P0 produced no durable aggregate verdict, so P1a could consume an unadjudicated predecessor;
- `u_fixed_step_Xi` was built from `G_bridge` alone while the point estimate used actual `Ξ`;
- selected-candidate evidence omitted the audit hashes whose discrepancies it reported;
- the **successful** P2b branch had still never executed, so its arithmetic was unverified;
- the production/TEST_ONLY provenance boundary was crossed by monkeypatching production guards;
- the executor called the provider **before** discovering an existing record, so no resume was a
  resume.

Every one of those is a defect of integration and lineage, not of the apparatus.

## C5 blockers

| id | blocker | superseded C4 form | effective C5 form |
|---|---|---|---|
| PE-60 | **the pressure upper bound was off the decision path** | `lateral_pressure_upper_bounds()` existed and was unit-tested, and **no production caller invoked it**: P1b admission, P2a eligibility and the P2b ledger all decided without it | the paired normal/audit upper bound is computed by `lateral_pressure_evidence_from_records()`, consumed by P1b admission, derived P2a eligibility and recomputed in P2b, with a functional regression proving the candidate path reaches the same pure calculation |
| PE-61 | **a point screen served as the final negative-control verdict** | `measured_zero_driver_pass = measured_zero_driver_point_pass` — a single mean-gap point estimate named as the adjudicative zero-driver verdict | `measured_zero_driver_point_pass` is an EARLY screen that may reject and may never admit; `measured_zero_driver_pass` is `null`/`INCOMPLETE` at case construction; the final verdict is `measured_zero_driver_upper_bound_pass`, requiring **both** `mean_gap_upper_rel ≤ TOL_LATERAL_DRIVER_REL` and `max_gap_upper_rel ≤ TOL_LATERAL_DRIVER_REL` at every required resolution and forcing level |
| PE-62 | **the boundary forcing set collapsed to `c` only** | PE-47 declared `R`, `s`, `A1`, `A2` and actual `Ξ` required; `candidate_forcing_gates()` then adjudicated `c_field` and nothing else at boundary level | an explicit `CANDIDATE_BOUNDARY_FORCING_QUANTITIES` set — `R_identical`, `s_blocked`, `s_open`, `c_field`, `A1`, `A2`, `A_field`, `Xi_actual` — every member adjudicated at both resolutions across the whole ladder |
| PE-63 | **no forcing gate for the areas** | `A1`, `A2` and the aggregate `A_field` fed the reachable set and actual `Ξ` with their forcing stability never tested | area quantities carry their own forcing gates under the frozen direct relative-spread rule (they are forcing-independent and are **not** divided by `g`) |
| PE-64 | **P0 adjudicated nothing in aggregate** | P0 wrote records; no aggregate forcing or resolution verdict existed, and P1a's only prerequisite was `PHASE_COMPLETE` | `p0_aggregate_science()` produces a durable aggregate verdict stored in the P0 manifest, recomputed by the validator from records, and **P1a refuses unless it is complete and passing** |
| PE-65 | **the `tau_plus = 1.2` rows were called an adjudicative cross-check with no rule** | scheduled as `tau_cross_check` and described as a cross-check; the controlling 001 authority freezes an analytic-channel observation (`+0.05203 %` at `τ⁺ = 1.2/2.0/3.0`) and **no** compared quantity, **no** tolerance and **no** viscosity/dynamic-similarity accounting for the assembled 3D fixture | classified `DIAGNOSTIC_ONLY`. They may show that the assembled fixture's behaviour is not grossly viscosity-dependent; they may **not** establish agreement, and they may not alter admission, uncertainty, classification or selection. **No tolerance is invented now.** The rows stay visible in the matrix |
| PE-66 | **the resolution quantity set was incomplete** | `c_field`, `C_blocked` and `Xi_coupon` only | explicit P0 and candidate required sets: reference-blocked flux/pressure/conductance and outlet share, contrast and area quantities, every axial-coupon conductance by level and orientation; and per candidate `R_identical`, `s_blocked`, `s_open`, `c_field`, `A1`, `A2`, `A_field`, `C_blocked`, `C_open`, `G_bridge_coupon`, `Xi_actual` |
| PE-67 | **`u_fixed_step_Xi` was a `G`-only movement** | `fixed_step_discrepancy(..., "G_bridge_coupon")` — the point estimate used actual `Ξ = G·(1/A1 + 1/A2)` while its uncertainty moved only `G`, so an area movement between a normal record and its audit was invisible | `actual_xi_discrepancy()` forms `Ξ_normal` and `Ξ_audit` from four exactly matched records (coupon normal, coupon audit, blocked-mirror normal, blocked-mirror audit) and takes the frozen safety-factor-adjusted discrepancy of the **derived** quantity |
| PE-68 | **selected evidence omitted the audit hashes** | a selected bridge's `record_hashes` carried normals and the artifact combinations' audits, but not the `c`, `Ξ` and pressure audits whose discrepancies the ledger reported | every selected bridge binds `candidate_specific_case_ids` and `candidate_specific_record_sha256` covering **every** record used to decide it, with genuinely shared P0 evidence separated into a top-level `common_reference_evidence` and named by role |
| PE-69 | **the successful P2b branch had never executed** | the synthetic pipeline reached only `DESIGN_BLOCKED`; the selected branch sat behind `# pragma: no cover` | a nondegenerate TEST_ONLY record generator drives P0 → P1a → adaptive P1b → adaptive P2a → P2b to a **one-below/three-inside** selection that writes all four artifacts, reopens and revalidates them, and makes zero solver calls |
| PE-70 | **a chained comparison in the P2b validator** | `freeze["rows_sha256"] != inst["rows_sha256"] != record_hash(inst["rows"])` — Python chaining makes this `a != b and b != c`, so `a == c` with `b` different passes | two independent inequalities, with three negative regressions covering each mismatch pattern |
| PE-71 | **TEST_ONLY predecessors could produce PRODUCTION P2b artifacts** | the synthetic harness monkeypatched `validate_phase_manifest`, `assert_production_record` and `execution_authority` and then ran the **production** wrapper, which stamped `provenance_mode = "PRODUCTION"` on the ledger, freeze, instantiated matrix and manifest | the P2b implementation is split into a pure decision core plus two wrappers with non-overlapping provenance: `assemble_p2b_from_runs()` obtains its own authority, validates recursively and writes PRODUCTION only; `_test_only_assemble_p2b_from_runs()` writes `provenance_mode = "TEST_ONLY"` on every artifact and never calls the production wrapper |
| PE-72 | **predecessor manifests were rehashed, not revalidated** | `validate_p2b_manifest` compared predecessor manifest **file hashes** only, so a P2b manifest citing a correct hash for an internally invalid P0 passed | `validate_p2b_manifest(require_production=True)` recursively calls the strong phase validator for P0, P1a, P1b and P2a in dependency order — reopening, rehashing, recomputing case verdicts and the P0 aggregate controls, checking full-universe partitions and adaptive decisions, requiring `PHASE_COMPLETE` and PRODUCTION provenance |
| PE-73 | **an unused authority parameter** | `validate_p2b_manifest(runs_dir, authority=None, …)` accepted `authority` and never read it | P2b binds a complete assembly-authority document (`p2b_assembly_authority()`), and the validator reconstructs and validates it explicitly; the parameter is load-bearing or absent |
| PE-74 | **the provider was called before the record was discovered** | `_orchestrate` resolved the row, called `provider(...)`, built the record and only then found an exact match and reported `REUSED_EXACT_MATCH` — a "resume" that had already paid for every solve | the record path is derived first; an existing record is reopened, fully revalidated and reused **without a provider call**; a differing record fails closed **before** the provider; only a missing record reaches the guarded provider; `n_provider_calls == n_newly_executed` is asserted per phase |
| PE-75 | **the phase manifest was overwritten unconditionally** | `tmp.write_text(...); tmp.replace(mpath)` on every run | manifest resume: an existing final manifest is reopened and fully validated, an exact valid completion returns with zero provider calls, anything else fails closed, and the write uses no-overwrite/exact-match semantics |
| PE-76 | **P3/P4 orchestration still derived its universe from templates** | `phase_universe()` returns the *template* rows for P3/P4, and PE-54's instantiated-matrix loader was described but never implemented | `POST_FREEZE_EXECUTOR_READY = False` — an explicit, source-controlled **hard refusal**. P3 and P4 refuse even if added to `AUTHORISED_SOLVING_PHASES`, no unresolved template can reach the provider, and no document calls P3/P4 execution-ready. Loading the approved instantiated matrix is reserved for a later authorization tranche |

## The `tau_plus = 1.2` disposition, resolved

The controlling historical authority is RP-D-LC-001 `PROTOCOL.md` §5 and
`rp_d_lc_virtual_fixture.TAU_CROSS_CHECK`. It freezes:

- an **analytic plane-channel** observation — the permeability error is `+0.05203 %` at
  `τ⁺ = 1.2`, `2.0` and `3.0`, identical to five significant figures;
- the intent that "Arm A re-runs one assembled fixture case at `tau_plus = 1.2` to confirm the
  independence holds for the assembled 3D geometry".

It freezes **no** compared quantity for the assembled fixture, **no** tolerance, and **no**
treatment of the viscosity change. That last omission is material: `ν = (τ⁺ − 0.5)/3`, so
`τ⁺ = 1.2 → ν = 0.2333` against `τ⁺ = 2.0 → ν = 0.5`. A pressure-normalised conductance
`C = Q/ΔP` scales as `1/ν`, and 001 handled this for the channel by scaling `g` with `ν`; the
001b `tau_cross_check` rows run at the **same** central `g` as their `τ⁺ = 2.0` counterparts, so
the two are not the same dimensionless problem and a raw comparison of `C`, `R` or `s` between
them would compare a viscosity ratio, not a discretisation independence.

Since no exact pre-existing rule exists, C5 **does not invent one**. The two rows are
`DIAGNOSTIC_ONLY`:

- **they may** record that the assembled 3D fixture solves, converges and stays in the low-Mach
  regime at a second relaxation rate, and that no gross qualitative change appears;
- **they may not** establish agreement, viscosity independence, or a bound of any kind;
- **they may not** alter admission, uncertainty, classification, selection, any gate verdict or
  any disposition.

They remain visible in the matrix, at their existing count, so the omission is recorded rather
than removed. Freezing an adjudicative `τ⁺` comparison — its quantity, its similarity scaling and
its tolerance — is available to a later correction that does so **before** any output exists.

## What did NOT change in C5

Every accepted scientific decision listed above · the Route-A observable contract · **no
solver-core change** · the claim ceiling · the `0.10·K` reachable-set margin · the four frozen
tolerances · the four-slot rule · **RP-D-LC-001 byte-unchanged** · and every phase, solving and
assembly alike, **unauthorized**: `AUTHORISED_SOLVING_PHASES = ()` and
`AUTHORISED_ASSEMBLY_PHASES = ()`. No LB solve ran to produce this correction.

## PE-66 supplement — the frozen resolution COMPARISON COORDINATE

Appended while implementing PE-66; nothing above is altered.

Completing the resolution set exposed a defect in the C4 gate itself, not only in its coverage.
C4 compared the two resolutions' **raw lattice values**. That is correct for a dimensionless
quantity and wrong for an extensive one: under the frozen forcing law `g(S) = G_REF (S_REF/S)^3`
and exact geometric similarity, a plane volume flux, a node-to-node pressure drop and a
conductance each move with `S` by a factor that is **fixed by the frozen configuration** and is
not a discretisation error. C4's set (`c_field`, `C_blocked`, `Xi_coupon`) hid this because two of
the three are dimensionless; `C_blocked` was already wrong and would have failed by a factor of
`(3/2)^3` on real fields.

The coordinate is `value / S**n`, and every exponent is **derived, not chosen**:

| step | relation | consequence |
|---|---|---|
| lattice velocity | `u ~ g L^2 / nu`, `L ~ S` | `u ~ g S^2` |
| plane fluid-node count | geometric similarity | `~ S^2` |
| plane volume flux | `Q = sum(u_x)` | `Q ~ g S^4` (i.e. `~ S^1` at `g(S)`) |
| node-to-node drop | `dP ~ g * (lattice length)` | `dP ~ g S` (i.e. `~ S^-2`) |
| conductance | `C = Q/dP` | `C ~ S^3` |
| lane areas `A1`, `A2`, coupon `G_bridge`, `G_axial` | conductances | `~ S^3` |
| `1/A1 + 1/A2` | reciprocal | `~ S^-3` |
| `Xi`, `R`, `s`, `c` | ratios of the above | `~ S^0` |

The exponent is `0` for every dimensionless quantity, so **no previously frozen dimensionless
comparison changes**, and nothing here is fitted or tunable: each exponent follows from the
already-frozen forcing law and the already-frozen geometric similarity. This remains a
**two-resolution consistency test**, not a convergence-order estimate.


## PE-77 — the documented `--mode plan` command raised `KeyError`

Found by RUNNING the documented verification command at the C5 head, not by reading it.

`main()` printed `res["planned_pressure_plane_diagnostics"]` — a key the execution matrix has
**never** carried; the matrix key is `planned_pressure_plane_diagnostic_rows`. The whole CLI body
sat under `# pragma: no cover - thin CLI`, so no test ever executed the line and the documented
command was broken from C4 onward.

Corrected by moving the summary out of the pragma into a covered `plan_summary(matrix)` that
reads every key from the matrix and raises on a key the matrix does not carry, with a regression
that calls it. The summary now also reports `planned_solver_invocations`, the same-field
node-offset summaries, the fresh-run and exact-resume provider-call counts, the P3/P4 template
row count, `post_freeze_executor_ready` and both authorization allowlists.

This is a reader-facing surface defect, not a gate defect: no scientific value, tolerance, count
or authorization changes.

---

# PE-78 … PE-88 — exact-head review at `acb4f6a` was NOT APPROVED; C6 endpoint recomputation and diagnostic semantics

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C6_ENDPOINT_RECOMPUTATION_AND_DIAGNOSTIC_SEMANTICS_REQUIRED`

**Reviewed head:** `acb4f6a77c65378fcef7ed3d0a03af8620880bcb`
**Reviewed tree:** `4c53c4b2acb83079037667f78c471fb16b8f938f`

Effective correction version from this point: **`PREFLIGHT-C6`**. Lineage:
**C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) → **C3** (`39533ad`) →
**C4** (`e455c67`) → **C5** (`acb4f6a`) → **C6**. Where any earlier text conflicts with the
effective C6 sections, **C6 governs**; nothing above this line is rewritten.

**PRE-EXECUTION THROUGHOUT.** No RP-D-LC-001b lattice-Boltzmann solve has run at any point in
this lineage, including under C6. `AUTHORISED_SOLVING_PHASES = ()`,
`AUTHORISED_ASSEMBLY_PHASES = ()` and `POST_FREEZE_EXECUTOR_READY = False` at the C6 head, and
P0, P1a, P1b, P2a, P2b, P3 and P4 all remain unauthorized.

## What the C6 review ACCEPTED and this correction preserves unchanged

The common-mode-port apparatus; common-mode blocked/open blind pockets; the lateral-only bridge
topology; no identical-path subtraction; no fitted or post-hoc artifact correction; exactly nine
axial mass-conservation planes; distinct volume-flux inverse and mass-flux conservation
contracts; full-vector fluid-node Mach control; exact paired pressure faces; the final
normal/audit pressure upper bounds; same-field node-offset summaries; the exact open/blocked
`R`-offset construction; the exact rational forcing identity; `g ∝ S^-3`; both-resolution,
three-level forcing ladders; `TOL_LINEARITY_REL = 1e-4`; `ARTIFACT_BUDGET_R_ABS = 1e-3`;
`TOL_BRIDGE_LEAKAGE_REL = 1e-3`; `TOL_LATERAL_DRIVER_REL = 1e-3`; true fixed-step re-execution;
separate `R`, `c` and actual-`Ξ` discrepancy families; candidate-specific blocked-mirror
contrast; the complete P0 and candidate forcing/resolution quantity sets; the two-sided
reachable-set admission; the unchanged `0.10·K` margin; exactly four selected bridges (one
unambiguously below, three unambiguously inside); no required above-window bridge; full-universe
adaptive ledgers; the successful and design-block TEST_ONLY P2b pipelines; separate production
and TEST_ONLY P2b wrappers; recursive predecessor validation; true pre-solve record and manifest
resume; separate empty solving and assembly allowlists; `POST_FREEZE_EXECUTOR_READY = False`; no
Route B; no solver-core modification; no open mirror case before P3; RP-D-LC-001 immutable and
`INVALID_EXECUTION`.

**PE-66 is ACCEPTED and unchanged.** The resolution comparison coordinate `value / S**n` stands
exactly as frozen — `Q` and the corresponding mass flux at `+1`, node-to-node `ΔP` at `-2`,
conductances and conductance-like areas at `+3`, the inverse-area aggregate at `-3`, and `R`,
`s`, `c` and actual `Ξ` at `0`. It is neither fitted nor tunable, and C6 does not reopen, alter
or rejustify it.

**None of the accepted elements is weakened, retuned or redesigned here.**

## Superseded C5 machine-readable artifacts

Retained alongside the C0, C1, C2, C3 and C4 sets; **all six generations are kept.**

| artifact | superseded C5 SHA-256 (`acb4f6a`) |
|---|---|
| `generated/protocol.json` | `2ac2b2a18a56552aedefee5f4c013869c64a885347ac06d71aa12411ba2e9a54` |
| `generated/fixture_spec.json` | `a803545ee8976975c063c255530af052b0a796db65c1b3fdf4a89576629b3dc3` |
| `generated/execution_matrix.json` | `1a57d2ee54cd29ad662783dcbc52741fc1c0d65c3aa73a85d6aac2d3249cf81f` |
| `generated/preflight_status.json` | `2ce0e09a572cf0d915d1c1fe38bda397c5e0c35c0f02f2fc7ed53f52bad7fc8b` |

Superseded C5 counts: **703** rows = **383** normal + **320** audits; **112** mandatory, **591**
refused, **3** rows classed `diagnostic_only`. **No C5 total is preserved for continuity** —
every C6 count is regenerated from the machine authority, and the mandatory minimum **changes**
because the two `tau_plus = 1.2` rows stop being decision-bearing.

## What C5 got wrong

C5 corrected the decision path and the evidence lineage. It left four things stated rather than
implemented:

- **PE-65 declared the `tau_plus = 1.2` rows `DIAGNOSTIC_ONLY` and the matrix still labelled them
  `mandatory`.** A diagnostic that can stop a phase is not a diagnostic.
- **The P2b validator authenticated the persisted ledger's bytes without rederiving the science.**
  It reopened records, recursively revalidated predecessors, and then compared the ledger against
  its own recorded hash — so a coordinated edit that also updated the outer hashes passed.
- **Some derived gate samples carried one source where two records produced them.** `R_identical`
  is `C_open / C_blocked` and its lineage cited only the open record in the generic schema;
  actual `Ξ` is `G_bridge · (1/A1 + 1/A2)` and its lineage cited only the coupon.
- **The frozen artifact uncertainty was reconstructed by hand in the live assembly path**, so the
  safety factor reached two of its three terms and the pressure maximum bound took a
  serialisation term derived from the mean statistic.

None of that is a defect of the apparatus. All of it is a defect of what the machinery actually
does with the apparatus's output.

## C6 blockers

| id | blocker | superseded C5 form | effective C6 form |
|---|---|---|---|
| PE-78 | **`tau_plus = 1.2` declared diagnostic, labelled mandatory** | PE-65 froze the rows as `DIAGNOSTIC_ONLY` and `_matrix_rows()` emitted them with `class = "mandatory"`, so they counted toward `mandatory_minimum` and were decision-bearing rows of the P0 universe | `class = "diagnostic_only"` with an explicit frozen `scientific_role = "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"`; they are planned solver invocations but not decision-bearing |
| PE-79 | **a tau diagnostic failure could stop P0** | an unconverged, non-finite, failed-Mach or failed-conservation tau row went through `case_decision_verdict` with `effect = "STOPS_THE_PHASE"`, terminating P0 `PHASE_STOPPED_INVALID_CASE` and blocking P1a on a row that may alter nothing | the role-aware classifier returns `effect = "RECORD_DIAGNOSTIC_AND_CONTINUE"` for a tau row whether or not the diagnostic itself is valid; P0 terminates `PHASE_COMPLETE` provided every decision-bearing row passes, and the failure and its reason are retained prominently |
| PE-80 | **`class = diagnostic_only` carried two incompatible meanings** | the same string labelled the determinism replicates, whose scientific-payload equality IS enforced and whose failure IS a defect, and would now also label the nonblocking tau rows | one frozen `scientific_role` per row: `TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE` versus `EXECUTION_ASSURANCE_REPLICATE`, with `ROW_SCIENTIFIC_ROLES` naming each role's adjudicative status, effect and failure semantics. The replicate's existing payload-equality requirement and failure semantics are unchanged |
| PE-81 | **tau evidence sat in common scientific reference evidence** | `COMMON_REFERENCE_KINDS` included `tau_cross_check`, so a row that may alter nothing was bound into `common_reference_evidence` — the structure every candidate cites as shared truth | tau records move to a separate top-level `diagnostic_evidence["tau_plus_1p2"]`, carrying an explicit non-adjudicative declaration; `common_reference_evidence` contains reference-blocked and axial-coupon evidence only |
| PE-82 | **the P2b validator authenticated bytes, not science** | `validate_p2b_manifest` recomputed nothing scientific: it compared `record_hash(ledger)` against the manifest's own `candidate_ledger_sha256`, which is a self-consistency check | after recursively validating P0…P2a and reopening their records, the validator calls the SAME pure builder and compares the independently reconstructed canonical scientific payload against every persisted artifact |
| PE-83 | **coordinated ledger + manifest tampering was undetectable** | changing `n_eligible`, a gate verdict, a `c` interval, a `Ξ` envelope, a category, an eligibility flag or a rejection reason and then updating the cited outer hashes produced a fully self-consistent artifact set that validated | every one of those edits now fails because the scientific payload does not recompute from the predecessor records. The stale-hash checks are retained as separate, weaker checks |
| PE-84 | **neither endpoint was independently reconstructed** | the selected endpoint's slots, order, categories, envelopes and instantiated rows, and the design-block endpoint's reason, were validated against themselves | both endpoints are rebuilt from the validated records and compared field by field, and `scientific_decision_payload_sha256` — the hash of the INDEPENDENTLY constructed payload, never of the persisted ledger — is recomputed and required to match on all four artifacts |
| PE-85 | **the `R` forcing gate's mapping omitted its paired blocked source** | `_identical_R_samples` put the blocked partner in ad-hoc `paired_blocked_*` keys outside the generic sample schema, so `componentwise_forcing_gate` and the candidate source-to-derived mapping recorded the open record alone for a quantity that is `C_open / C_blocked` | a canonical multi-source sample schema — `source_case_ids`, `source_record_sha256`, `source_roles` — carried by every derived sample and unioned into the gate. An `R` gate's complete source set contains three open and three blocked records per resolution |
| PE-86 | **the actual-`Ξ` gate's mapping omitted its area source** | the area evidence lived in ad-hoc `area_case_id` / `area_record_sha256` keys that only the resolution gate knew about; the forcing gate cited the coupon alone | actual `Ξ` carries `bridge_coupon` and `candidate_blocked_area` source roles in the same canonical schema, at every forcing level and both resolutions |
| PE-87 | **the frozen artifact safety factor reached two terms of three** | `artifact_evidence_from_records` composed `u_fixed_step_R + u_pressure_plane_R + u_ser` where the first two were ALREADY safety-scaled and `u_ser` was not, so the live path computed `2·a + 2·b + c` instead of the frozen `2·(a + b + c)` | one canonical composer. `numerical_discrepancy_R()` consumes the RAW conductances and the RAW `R`-offset sequence and applies `NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0` exactly once to the full sum; `node_offset_R()` and the fixed-step routine expose raw movements alongside their scaled diagnostics |
| PE-88 | **the pressure maximum bound used the mean's serialisation term** | `lateral_pressure_upper_bounds` set `u_ser = 10**(-RECORD_DP) * (1 + abs(mean_pt))` and used it for BOTH inequalities, so with `abs(mean) ≪ max_abs` the maximum bound carried a term too small for its own statistic | `u_serialization_mean` from `abs(mean_delta_p)` and `u_serialization_max` from `abs(max_abs_delta_p)`, retained as separate fields and used in their corresponding inequalities. `TOL_LATERAL_DRIVER_REL` is unchanged |

## What did NOT change in C6

Every accepted scientific decision listed above · **PE-66 accepted and unchanged** · the Route-A
observable contract · **no solver-core change** · the claim ceiling · the `0.10·K` reachable-set
margin · `NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0` · all four frozen tolerances · the artifact
budget · the four-slot rule · the candidate family · the similarity law · **RP-D-LC-001
byte-unchanged** · and every phase, solving and assembly alike, **unauthorized**. No LB solve ran
to produce this correction.

---

# PE-89 … PE-100 — exact-head review at `76e5669` was NOT APPROVED; C7 diagnostic-attempt and execution-authority lineage

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C7_DIAGNOSTIC_ATTEMPT_AND_EXECUTION_AUTHORITY_LINEAGE_REQUIRED`

**Reviewed head:** `76e5669670213f33c6496b98cc4d2cdfc9711b35`
**Reviewed tree:** `489af8f01d2bcf6009dbfa1dbd8a0cc82fd205e7`

Effective correction version from this point: **`PREFLIGHT-C7`**. Lineage:
**C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) → **C3** (`39533ad`) →
**C4** (`e455c67`) → **C5** (`acb4f6a`) → **C6** (`76e5669`) → **C7**. Where any earlier text
conflicts with the effective C7 sections, **C7 governs**; nothing above this line is rewritten.

**PRE-EXECUTION THROUGHOUT.** No RP-D-LC-001b lattice-Boltzmann solve has run at any point in
this lineage, including under C7. `AUTHORISED_SOLVING_PHASES = ()`,
`AUTHORISED_ASSEMBLY_PHASES = ()` and `POST_FREEZE_EXECUTOR_READY = False` at the C7 head, and
P0, P1a, P1b, P2a, P2b, P3 and P4 all remain unauthorized.

## What the C7 review ACCEPTED and this correction preserves unchanged

The common-mode-port apparatus; common-mode blocked/open blind pockets; the lateral-only bridge
topology; no identical-path subtraction; no fitted or post-hoc artifact correction; exactly nine
axial mass-conservation planes; distinct volume-flux inverse and mass-flux conservation
contracts; full-vector fluid-node Mach control; exact paired pressure faces; the final
normal/audit pressure upper bounds; same-field node-offset summaries; the exact open/blocked
`R`-offset construction; the exact rational forcing identity; `g ∝ S^-3`; both-resolution,
three-level forcing ladders; `TOL_LINEARITY_REL = 1e-4`; `ARTIFACT_BUDGET_R_ABS = 1e-3`;
`TOL_BRIDGE_LEAKAGE_REL = 1e-3`; `TOL_LATERAL_DRIVER_REL = 1e-3`; true fixed-step re-execution;
separate `R`, `c` and actual-`Ξ` discrepancy families; the complete P0 and candidate forcing and
resolution quantity sets; the two-sided reachable-set admission; the unchanged `0.10·K` margin;
exactly four selected bridges (one unambiguously below, three unambiguously inside); no required
above-window bridge; full-universe adaptive ledgers; **independent reconstruction of the selected
and design-block P2b endpoints**; **coordinated scientific-endpoint tamper resistance**;
**complete multi-source `R` and actual-`Ξ` lineage**; the artifact equation
`2.0 * (fixed_step_raw + node_offset_raw + serialization_raw)`; separate pressure mean and
maximum serialisation terms; true pre-solve record and manifest resume; separate empty solving
and assembly allowlists; `POST_FREEZE_EXECUTOR_READY = False`; no Route B; no solver-core
modification; no open mirror result before P3; RP-D-LC-001 immutable and `INVALID_EXECUTION`.

**PE-66 remains ACCEPTED AND UNCHANGED.** The resolution comparison coordinate `value / S**n`
stands exactly as frozen and is not reopened, altered or rejustified.

**The mandatory-minimum change from 112 to 110 is ACCEPTED** as the correct consequence of the
two tau rows becoming non-decision-bearing.

**No accepted scientific choice is reopened or retuned here.**

## Superseded C6 machine-readable artifacts

Retained alongside the C0 … C5 sets; **all seven generations are kept.**

| artifact | superseded C6 SHA-256 (`76e5669`) |
|---|---|
| `generated/protocol.json` | `ae6b61e0c36f4817652fba10d1961087babecf52084a2cce51261da7fcbb96d0` |
| `generated/fixture_spec.json` | `45746921faf3fe5534f7d493ee0fb84633145142be821d9f6829e33704380225` |
| `generated/execution_matrix.json` | `c4b4c77d5171d522e433ebdca42d1ee027d537ab307f0f43316a475a9efca0f0` |
| `generated/preflight_status.json` | `75a1c65b67c65abf56bb558177c57d41f48155b2c9e9173f591fc6eaf6496311` |

Superseded C6 counts: **703** rows = **698** decision-bearing (378 normal + 320 audits) + **2**
tau diagnostic + **3** execution-assurance; **110** mandatory minimum, **591** refused. No C6
total is preserved for continuity — every C7 count is regenerated from the machine authority, and
**no row is added or removed** for authority or diagnostic-envelope bookkeeping.

## What C6 got wrong

C6 made the tau rows non-adjudicative and made the P2b endpoint independently reconstructible.
Two things it did not do:

- **The nonblocking tau semantics only covered a diagnostic that SUCCEEDED at producing a record
  and then failed a scientific check.** The role-aware classifier is reached only after
  `provider(...)`, `_fixture_scientific(...)`, `make_case_record(...)` and `write_case_record(...)`
  have all succeeded. A tau provider that raises, or returns a malformed or non-finite result,
  aborts P0 outright — before `diagnostic_failed` can exist. A diagnostic whose *attempt* can kill
  the phase is not a diagnostic.

- **The execution authority was persisted as an opaque hash, not as a recoverable object.** Phase
  manifests stored `execution_authority_sha256` and a handful of convenience fields; the complete
  authority — every input-file hash, the protocol/geometry/errata document hashes, the stage, the
  prerequisites, the dependency identity, the clean-tree proof — lived only in transient Python
  memory. Nothing downstream could reconstruct it, `authority=None` meant "skip authority
  validation", and what validation there was compared 40-character strings rather than asking Git
  whether the recorded commit and tree exist and what they contain.

Neither is a defect of the apparatus or of any scientific gate.

## C7 blockers

| id | blocker | superseded C6 form | effective C7 form |
|---|---|---|---|
| PE-89 | **the nonblocking classifier is reached only after a record already exists** | `_orchestrate` calls the provider, extracts the compact science, builds and writes the record, and only THEN asks `case_decision_verdict` for the role-aware effect | the provider/result boundary is factored into an explicit attempt step; for the tau role only, a row-local attempt failure produces a canonical **diagnostic-failure envelope** and the phase continues |
| PE-90 | **a tau provider exception aborted P0** | any exception from `provider(...)` on a tau row propagated out of the row loop and terminated the phase before `diagnostic_failed` existed | `DIAGNOSTIC_PROVIDER_EXCEPTION`: caught for the tau role only, recorded with its exception class and a bounded sanitised message, filed in `diagnostic_failed` |
| PE-91 | **a malformed or non-finite tau result aborted before role-aware classification** | a missing `steps`/`rho`/`uy`/`uz`, a wrong-shaped array or a non-finite field raised out of `_fixture_scientific` or `NonFiniteValue` out of the record writer | `DIAGNOSTIC_RESULT_CONTRACT_INVALID`, `DIAGNOSTIC_RESULT_NONFINITE` and `DIAGNOSTIC_SCIENTIFIC_EXTRACTION_FAILED`, each an explicit narrow category with its own failure stage |
| PE-92 | **no durable diagnostic-attempt failure envelope existed** | a failed attempt left nothing on disk, so a resume re-attempted it and no record of the failure survived | `diagnostic_failure_<case_id>.json`: an immutable, canonically serialised, strict-finite, atomically written, no-overwrite, exact-match-resumable document with its own schema, carrying the row, the authority, the failure code and stage, and `NON_ADJUDICATIVE_NOT_SCIENTIFIC_EVIDENCE`. A normal record and an envelope may never coexist for one case ID |
| PE-93 | **phase manifests persisted an opaque authority hash, not its preimage** | `execution_authority_sha256` plus `source_commit`, `source_tree` and the three config hashes; the complete object was never written | every phase manifest embeds the **complete canonical execution authority** and its exact hash, and the convenience fields must equal the embedded object |
| PE-94 | **case validation checked only fragments of the authority** | `validate_case_record` compared `source_commit`, `source_tree` and the three config hashes and never looked at `execution_authority_sha256` at all | every record and envelope is bound to its phase authority by hash, and the validator resolves that hash to the complete authority embedded in the manifest and requires equality on stage, backend, dependencies, provenance and the exact per-row solver configuration |
| PE-95 | **historical predecessor validation ran with `authority=None`** | `validate_p2b_manifest` called `validate_phase_manifest(pre, base, ...)` with no authority, and `authority=None` meant every authority check was skipped | `authority=None` no longer means "skip". The validator ALWAYS loads, independently validates and rehashes the embedded historical authority; an external expected authority only strengthens the check for exact same-phase resume |
| PE-96 | **the full authority was not independently recoverable** | the input-file map, the protocol/geometry/errata hashes, the stage, the prerequisites and the clean-tree proof existed only in memory | all of it is persisted inside the authority object and is recomputed from the recorded commit during validation |
| PE-97 | **`P2B_ASSEMBLY_AUTHORITY_FIELDS` excluded `execution_authority_sha256`** | the field was written into the document and left OUT of the canonical set the assembly hash is taken over, so changing it did not change `assembly_authority_sha256` | both `execution_authority` and `execution_authority_sha256` are inside the canonical field set; no load-bearing identity field sits outside the hash |
| PE-98 | **the P2b assembly authority did not contain its execution authority** | only the hash | the complete nested canonical P2b execution authority, with every duplicated outer field required to equal it |
| PE-99 | **commit/tree validation was string-shape validation** | `len(v) == 40` | `validate_execution_authority` asks Git whether `source_commit` is a real commit object, whether `rev-parse <commit>^{tree}` equals `source_tree`, and reads every tracked input file, document and generated artifact **from that commit** to recompute its hash — not from the current working tree |
| PE-100 | **`decision_bearing_case_ids` included execution-assurance rows** | the field was built by excluding tau, so the determinism replicates landed in a list named decision-bearing while role-resolved reporting counted them separately | `decision_bearing_case_ids`, `execution_assurance_case_ids`, `diagnostic_case_ids` and `adjudicative_case_ids` are each formed from the exact role. The frozen failure semantics of determinism assurance are unchanged |

## What did NOT change in C7

Every accepted scientific decision listed above · **PE-66 accepted and unchanged** · the Route-A
observable contract · **no solver-core change** · the claim ceiling · the `0.10·K` reachable-set
margin · `NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0` · all four frozen tolerances · the artifact
budget and equation · the pressure serialisation split · the four-slot rule · the candidate
family · the similarity law · the mandatory minimum of 110 · **RP-D-LC-001 byte-unchanged** · and
every phase, solving and assembly alike, **unauthorized**. **No solver row is added** for
authority or diagnostic-envelope bookkeeping. No LB solve ran to produce this correction.

---

# PE-101 … PE-113 — exact-head review at `b5eb378` was NOT APPROVED; C8 authorization proof and predecessor lineage

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C8_AUTHORIZATION_PROOF_AND_PREDECESSOR_LINEAGE_REQUIRED`

**Reviewed head:** `b5eb3786a71514ceb937e0772144e050e461a3fc`
**Reviewed tree:** `d11331486b36f20e421835ce7bd16dd87a7782db`

Effective correction version from this point: **`PREFLIGHT-C8`**. Lineage:
**C0** (`bbf2304`) → **C1** (`2cf0b63`) → **C2** (`c666707`) → **C3** (`39533ad`) →
**C4** (`e455c67`) → **C5** (`acb4f6a`) → **C6** (`76e5669`) → **C7** (`b5eb378`) → **C8**.
Where any earlier text conflicts with the effective C8 sections, **C8 governs**; nothing above
this line is rewritten.

**PRE-EXECUTION THROUGHOUT.** No RP-D-LC-001b lattice-Boltzmann solve has run at any point in
this lineage, including under C8. `AUTHORISED_SOLVING_PHASES = ()`,
`AUTHORISED_ASSEMBLY_PHASES = ()` and `POST_FREEZE_EXECUTOR_READY = False` at the C8 head, and
P0, P1a, P1b, P2a, P2b, P3 and P4 all remain unauthorized.

## What the C8 review ACCEPTED and this correction preserves unchanged

All C6 scientific outcomes; **PE-66 unchanged**; common-mode blocked/open blind pockets; the
lateral-only bridge topology; no identical-path subtraction; no fitted or post-hoc correction;
nine axial mass-conservation planes; the volume-flux inverse against mass-flux conservation;
full-vector Mach control; paired pressure-face controls; the normal/audit pressure upper bounds;
same-field node-offset summaries; the exact open/blocked `R`-offset construction; exact rational
forcing; `g ∝ S^-3`; every forcing and resolution gate; every frozen tolerance; separate `R`, `c`
and actual-`Ξ` discrepancy families; two-sided reachable-set admission; the unchanged `0.10·K`
margin; one below plus three inside; independent reconstruction of the selected and design-block
P2b endpoints; coordinated endpoint tamper resistance; complete multi-source scientific lineage;
the exact artifact and pressure uncertainty formulas; role-resolved tau and determinism
semantics; immutable tau diagnostic-failure envelopes in principle; source-commit tracked-content
hashing; the measured-historical treatment of dependency identity, clean-tree status and the
no-RNG declaration; true pre-solve record and manifest resume; the P3/P4 hard refusal; no Route
B; no solver-core change; RP-D-LC-001 immutable and `INVALID_EXECUTION`.

**Both C7 judgment calls are ACCEPTED and are not reopened:**

1. dependency versions, clean-tree state and the seed/no-RNG declaration are **measured
   historical claims**, not facts a later validator can re-observe;
2. tracked-file hashes belong to the **recorded source commit**, not to the validator's later
   working tree.

**No accepted scientific choice is reopened or retuned here.**

## Superseded C7 machine-readable artifacts

Retained alongside the C0 … C6 sets; **all eight generations are kept.**

| artifact | superseded C7 SHA-256 (`b5eb378`) |
|---|---|
| `generated/protocol.json` | `d35eec46569c9b599eb353598579e55d35af2a2646d0198b1612cf044c57fdbd` |
| `generated/fixture_spec.json` | `9d31df49694d294f152553574953ecdadc0cdfa483709cfa5aef9400031286e0` |
| `generated/execution_matrix.json` | `ff452a49b9d15430c0fa8c2fc03789fb3b6ea401b2c4b10bffae966bf217580d` |
| `generated/preflight_status.json` | `b9e74571d45acc3b84412a161bd64d860870b654df972e1957b372de6989fe86` |

Superseded C7 counts: **703** rows = **698** decision-bearing (378 normal + 320 audits) + **2**
tau diagnostic + **3** execution-assurance; **110** mandatory minimum, **591** refused. No C7
total is preserved for continuity, and **no row is added** for authority, lineage or envelope
validation.

## What C7 got wrong

C7 made a failed tau attempt nonblocking and made the execution authority durable. Two things it
did not do:

- **The authority proves the source commit, not that the source commit authorized the stage.**
  `validate_execution_authority` establishes that `source_commit` is a real commit, that its tree
  matches, and that every tracked file hashes as recorded. It never asks the one question that
  matters for an execution record: *did that commit authorize this phase?* The runtime gate reads
  `AUTHORISED_SOLVING_PHASES` from the **live import**, so a historical record proves nothing
  about the allowlists at its own commit, and `execution_authority("P0")` builds a PRODUCTION
  authority happily at a head where every allowlist is empty.

- **Predecessor lineage is checked in one place and bound nowhere.**
  `require_phase_manifests` compares predecessor manifest file hashes; `validate_phase_manifest`
  does not. So validating P1a on its own establishes nothing about P0, the P2b recursive walk
  inherits that gap for the internal P0→P1a→P1b→P2a chain, and the
  `predecessor_manifest_sha256` that every record and envelope carries is compared against the
  phase manifest only on the resume path — never at final validation.

Neither is a defect of the apparatus or of any scientific gate.

## C8 blockers

| id | blocker | superseded C7 form | effective C8 form |
|---|---|---|---|
| PE-101 | **the authority proves the commit, not the authorization** | `validate_execution_authority` establishes the Git identity and every tracked hash, and never establishes that the recorded stage was authorized at that commit | a canonical `source_authorization` snapshot is part of the authority: the driver path and file hash, the parsed solving and assembly allowlists, the parsed post-freeze readiness, the gate type the stage requires, and the `stage_authorised` verdict |
| PE-102 | **the authority schema omitted the committed authorization snapshot** | `EXECUTION_AUTHORITY_FIELDS` carried no authorization field at all, so nothing about it entered `execution_authority_sha256` | `source_authorization` is in the field set and therefore inside the authority hash; changing any part of it moves every record, envelope, manifest and P2b artifact bound to it |
| PE-103 | **`execution_authority(stage)` was constructible for an unauthorized stage** | it validated the backend and the stage NAME against the phase graph, never the allowlists, so a PRODUCTION authority for P0 was constructible at a head where `AUTHORISED_SOLVING_PHASES = ()` | the production builder REFUSES unless the committed allowlist authorizes the stage — solving for P0…P2a, assembly for P2b, and solving **plus** `POST_FREEZE_EXECUTOR_READY` for P3/P4. At this head every production construction refuses |
| PE-104 | **the production P2b wrapper had no gate at its own boundary** | `assemble_p2b_from_runs` went straight to `execution_authority("P2b")` and `require_phase_manifests`; the assembly gate lived only in the driver's `require_assembly_authorisation`, so a direct call bypassed it | the public wrapper applies the shared source-controlled assembly gate FIRST, before validating any record, creating any authority or writing any artifact |
| PE-105 | **the complete authority preimage was not persisted before the first provider call** | it reached disk only inside the FINAL phase manifest, so an interrupted phase left records citing an opaque hash whose preimage existed only in transient memory | an immutable `execution_authority_<phase>.json` is written atomically **before** the first provider call, and is the identity available during a partial phase |
| PE-106 | **records carried a predecessor map final validation never compared** | `predecessor_manifest_sha256` was checked against the phase's map only inside `load_resumable_case_record`; `validate_case_record` never saw it | `validate_case_record` takes the expected map and requires exact equality, and final manifest validation passes it for every record |
| PE-107 | **`validate_phase_manifest` did not validate its own predecessor identity** | only `require_phase_manifests` compared predecessor manifest files, so validating a phase in isolation established nothing about its predecessors | `validate_phase_manifest` always validates its exact `PHASE_PREREQUISITES[P]` key set, requires each cited file to exist and to rehash exactly, and P0 must carry the exact empty map |
| PE-108 | **P2b recursive validation therefore missed the internal chain** | it revalidated each predecessor's contents but never established P1a→P0, P1b→(P0,P1a) or P2a→its exact set | the chain is recovered automatically because `validate_phase_manifest` now checks it, with a validated-manifest cache so the recursion is bounded and no identity check is skipped |
| PE-109 | **envelope validation did not self-hash its embedded row** | it compared the stored `row_sha256` against the EXTERNAL planned row and left `doc["row"]` unchecked, so a modified embedded row with an unchanged stored hash passed | `row_sha256(doc["row"]) == doc["row_sha256"]` is required, and `doc["row"]` must equal the canonical planned row exactly |
| PE-110 | **envelope identity was checked on resume but not downstream** | forcing, solver configuration, mask and predecessor identity were compared inside `load_resumable_diagnostic_failure` and nowhere else | the exact envelope schema, the row-derived fields, the geometry/mask identity and the predecessor map are all required at FINAL manifest validation |
| PE-111 | **incompatible dtypes escaped the named result contract** | `_assert_result_contract` called `np.asarray(...)` and `np.isfinite(...)` unguarded, so an object, string, bytes or complex array raised `TypeError` out of the contract rather than becoming a named diagnostic code | `np.asarray` and `np.isfinite` failures are caught and mapped to `DIAGNOSTIC_RESULT_CONTRACT_INVALID`, and a real numeric dtype is required explicitly |
| PE-112 | **non-integral step values were accepted through `int()`** | the contract did `int(res["steps"])` inside a `try`, so `2000.5` truncated silently to 2000 and `True` became 1 | an exact non-negative integer is required: `bool`, a non-integral float, NaN/infinity, a numeric string, a complex value and any lossy conversion are rejected; a NumPy integer scalar is accepted |
| PE-113 | **the C7 commit message recorded a stale `preflight_status.json` hash** | the message quotes `07cf090f…2d34`, computed before the final documentation edits changed `input_file_sha256`; the artifact actually committed at `b5eb378` hashes to `b9e74571…fe86` | the superseded-artifact table above records the **actual** committed hash. The commit message is history and is not amended; this erratum is the correction of record |

## Deferred: the post-freeze historical-version boundary

The real P0–P2b production records will be created under a **future reviewed authorization
head**, whose `CORRECTION_VERSION` will be whatever that head declares. Every validator in this
bundle currently requires equality with the **current** `CORRECTION_VERSION`.

That is sufficient for P0–P2b, because all pre-freeze phases will share one reviewed authority
version. It is **not** sufficient for a later P3/P4 review commit, which must validate historical
C8-era authorities from a head whose own correction version has moved on.

**This is recorded as a deferred P3/P4 prerequisite, not as a solved problem.** C8 does not
implement the post-freeze historical-version dispatcher, does not claim that
current-`CORRECTION_VERSION` equality suffices for all future review commits, and keeps
`POST_FREEZE_EXECUTOR_READY = False`.

## What did NOT change in C8

Every accepted scientific decision listed above · **PE-66 accepted and unchanged** · both C7
judgment calls accepted · the Route-A observable contract · **no solver-core change** · the claim
ceiling · the `0.10·K` reachable-set margin · `NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0` · all
four frozen tolerances · the artifact and pressure equations · the four-slot rule · the candidate
family · the similarity law · the mandatory minimum of 110 · **the allowlists, which remain
empty** · **RP-D-LC-001 byte-unchanged** · and every phase, solving and assembly alike,
**unauthorized**. **No solver row is added** for authority, lineage or envelope validation, and
an authority file causes no provider call. No LB solve ran to produce this correction.

---

# PE-114 … PE-126 — exact-head review at `67c8c23` was NOT APPROVED

**Review disposition:**
`RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C9_RUNTIME_BUNDLE_AND_RECORD_ASSURANCE_REQUIRED`

**Reviewed head:** `67c8c235bf4bb9327b36f84b047cfd861334afac`
**Reviewed tree:** `123a6bc2ee27a8053d4ffbd1fbc4d386dda49d68`

Ninth review; ninth NOT APPROVED. C9 is a **runtime-bundle, case-record, audit,
replicate-assurance, authorization-cohort and current-documentation** correction. It changes
**execution readiness only**. It alters no apparatus, no geometry, no gate, no tolerance, no safety
factor, no candidate family, no selection rule, no admission and no claim ceiling, and it
authorizes and executes nothing.

Where any earlier text conflicts with the effective C9 sections, **C9 governs**; nothing above
this line is rewritten.

**PRE-EXECUTION THROUGHOUT.** No RP-D-LC-001b lattice-Boltzmann solve has run at any point in
this lineage, including under C9. `AUTHORISED_SOLVING_PHASES = ()`,
`AUTHORISED_ASSEMBLY_PHASES = ()` and `POST_FREEZE_EXECUTOR_READY = False` at the C9 head, and
P0, P1a, P1b, P2a, P2b, P3 and P4 all remain unauthorized.

## What the C9 review ACCEPTED and this correction preserves unchanged

Every accepted C7 scientific outcome; **both C7 judgment calls**; **PE-66 unchanged**;
**PE-113**'s correction of the historical preflight-status hash; committed source-authorization
parsing **by AST**; production refusal at an unauthorized source commit; the separate P2b assembly
gate; complete per-phase execution authorities; authority persistence **before the first provider
call**; intrinsic predecessor-chain validation; records and diagnostic envelopes bound to the
phase-authority file; self-authenticating diagnostic-failure envelopes; the named malformed-tau
result-contract outcomes; selected and design-block P2b reconstruction; coordinated endpoint and
authority tamper resistance; true pre-solve record/envelope/manifest resume; all current solving
and assembly allowlists **empty**; `POST_FREEZE_EXECUTOR_READY = False`; **no Route B**; **no
solver-core change**; no open mirror result before P3; RP-D-LC-001 **immutable** and
`INVALID_EXECUTION`.

**The deferred current-version boundary (§26.8) remains ACCEPTED as a P3/P4 prerequisite.** C9
does **not** implement the post-freeze historical-version dispatcher.

**No accepted scientific choice is reopened or retuned here.**

## Superseded C8 machine-readable artifacts

Retained alongside the C0 … C7 sets; **all nine generations are kept.**

| artifact | superseded C8 SHA-256 (`67c8c23`) |
|---|---|
| `generated/protocol.json` | `49eed608319295135003f04c048349e6acaaa99004d9a0766591e35730b646c0` |
| `generated/fixture_spec.json` | `d9dcfd2d5036aae82e11aafb6e60c7853dc2345e1e4fe295baea026e897d0b39` |
| `generated/execution_matrix.json` | `696fc44d43fc974c9d89c7590912338251c3e9e65dd71528e65a98d4449d1ff0` |
| `generated/preflight_status.json` | `ce6432eb80c86cb7d482dae6f210ca514e277b13aa60ca2136fd2a219d23b657` |

The effective C9 replacements are recorded in **"Effective C9 machine-readable artifacts"** below.

Superseded C8 counts: **703** rows = **698** decision-bearing (378 normal + 320 audits) + **2** tau
diagnostic + **3** execution-assurance; **110** mandatory minimum, **591** refused, **511**
same-field node-offset summaries. **No C8 count changes under C9** — every value is independently
regenerated from one machine authority and retained only because it regenerated, and **no row is
added** for a runtime-path check, a payload recomputation, an audit reconstruction or a cohort
parse.

## What C8 got wrong

C8 proved that the recorded source commit authorized the stage, persisted the complete authority
before the first provider call, and made predecessor lineage intrinsic. Five things it did not do:

- **The production runtime bundle is inside the worktree the authority requires to be clean.**
  `run_phase` falls back to `REPO_ROOT / vf.RUNS_REL` — `docs/analysis/rp_d_lc_001b/runs` — which
  the tracked `.gitignore` does not exclude. So the documented production P0 command writes
  untracked artifacts into the repository, and the very next phase's authority, which requires a
  clean tree, cannot be constructed. The design defeats itself on the first real execution.

- **Final case-record validation is weaker than resume validation.** `load_resumable_case_record`
  recomputes the run status from the record's own step count and audit plan, and recomputes
  `scientific_payload_sha256` from the record's own configuration, payload and mask.
  `validate_case_record` — the validator every FINAL manifest uses — does neither. A record that
  was never resumed is therefore held to a weaker standard than one that was.

- **A fixed-step audit authenticates itself.** The executor validates an audit against its exact
  normal base *before* execution. At final validation the audit's own stored `audit` object is fed
  back into `effective_solver_config`, so the record proves only that it is internally consistent
  with the audit plan it supplied. The base's existence, status, record hash and derived target
  are never reconstructed.

- **The manifest chooses which assurance relationships to report.** `validate_phase_manifest`
  iterates `doc.get("replicates", [])`. It never derives the required set from the canonical
  matrix, so an omitted replicate is invisible; it compares the two records' **stored** payload
  hashes, so a coordinated pair of stale identities passes; and it calls neither
  `assert_replicate_compatible` nor any check on `replicate_of_case_id`.

- **The source says each phase gets its own authorization commit; the code requires one shared
  source identity.** The driver's docstring and `AUTHORISATION_NOTE` both state that each phase is
  added by its own reviewed source commit. `require_phase_manifests` requires every predecessor's
  authority to carry the same `source_commit` and `source_tree`. Under sequential authorization
  commits, P1a could never consume P0.

Alongside those, the current README is stale at the reviewed head: it names §19/§20 (C1/C2) as the
effective protocol and reports superseded C3/C4 counts, and its production P0 command silently
selects the repository-internal runs directory.

None of these is a defect of the apparatus or of any scientific gate.

## C9 blockers

| id | blocker | superseded C8 form | effective C9 form |
|---|---|---|---|
| PE-114 | **the production CLI defaults to a runtime bundle inside the worktree** | `run_phase` falls back to `REPO_ROOT / vf.RUNS_REL` = `docs/analysis/rp_d_lc_001b/runs`, and `--output` is documented as optional with "default: the bundle's `runs/`" | `PRODUCTION_RUNS_DIRECTORY_POLICY = EXPLICIT_ABSOLUTE_PATH_OUTSIDE_REPOSITORY`. Every non-plan production mode — P0, P1a, P1b, P2a, P2b and eventually P3/P4 — REQUIRES an explicit `runs_dir` / `--output`; there is no default. `--mode plan` still needs none |
| PE-115 | **the tracked `.gitignore` does not exclude that bundle** | no rule for `docs/analysis/rp_d_lc_001b/runs` exists in `.gitignore`, so P0 output is untracked-but-visible and `git status` is dirty | the durable fix is the policy above, not an ignore rule. A tracked ignore rule is added as defence in depth only; the validator may **never** rely on `.git/info/exclude`, a global gitignore, an environment-specific rule or an untracked local convention |
| PE-116 | **P0 output therefore made the tree dirty before P1a authority construction** | `_build_execution_authority(require_clean=True)` refuses on a dirty tree; the default P0 output made it dirty, so a real P0→P1a sequence could not proceed | with the runtime bundle outside `REPO_ROOT` the repository stays clean across every phase, and a no-solver integration regression asserts exactly that |
| PE-117 | **final case-record validation did not recompute run status** | `validate_case_record` checked only that `status ∈ RUN_STATUSES`; only `load_resumable_case_record` recomputed it | `validate_case_record` recomputes the status from `run_mode`, `completed_steps` and the reconstructed fixed-step target, requires exact equality with the stored field, and `case_decision_verdict()` is called on the RECOMPUTED status |
| PE-118 | **final case-record validation did not recompute scientific-payload identity** | `scientific_payload_sha256` was recomputed only on the resume path; a record that was never resumed was never checked against its own contents | `scientific_payload_hash(exact effective configuration, compact payload, recomputed mask SHA-256)` is recomputed and required to equal the stored field at FINAL manifest validation. It remains a **consistency identity**, not an external cryptographic signature |
| PE-119 | **resume validation was stronger than completed-manifest validation** | two validation paths of unequal strength, so whether a record was checked depended on whether the phase happened to be interrupted | ONE canonical pure validator is used by initial record construction, pre-solve exact resume, final phase-manifest validation, recursive P2b validation and later freeze validation. The final validator is by construction at least as strong as the resume validator |
| PE-120 | **fixed-step audit base, hash, target and status were not independently reconstructed** | at final validation the audit's own stored `audit` object was fed back into `effective_solver_config`; the base row, base record, base status, base record hash and derived target were never reconstructed | for every executed fixed-step row, final validation requires non-null `audit_of_case_id`, locates that exact base row in the same canonical matrix, calls `assert_audit_compatible`, requires the base record to exist in the completed adjudicative set and to be `NORMAL_CONVERGED`, recomputes the base record's file SHA-256, derives `fixed_step_audit_plan()` from the base's own completed steps and status, and requires the audit's base ID, base record hash, target, min/max steps, run mode, effective configuration, completed steps and status to match that plan exactly. A missing, failed, incompatible or differently hashed base makes the audit **invalid**, and an invalid audit enters no numerical-discrepancy evidence, no forcing or resolution gate, no phase completion and no P2b |
| PE-121 | **the replicate validator accepted whichever replicate list was supplied** | `for rep in doc.get("replicates", [])` — an omitted expected replicate was invisible and an extra entry was unconstrained | the required set is DERIVED from the canonical eligible rows whose `scientific_role` is `EXECUTION_ASSURANCE_REPLICATE`. A `PHASE_COMPLETE` manifest must carry exactly one entry for every such row: none omitted, none extra. A stopped phase represents an unexecuted assurance row through the frozen refusal semantics, never through an invented replicate verdict |
| PE-122 | **replicate equality compared stored rather than recomputed payload hashes** | `records[base].get("scientific_payload_sha256") != records[rep].get(...)` — a coordinated pair of stale stored identities passed | both payload hashes are RECOMPUTED from each record's own effective configuration, compact payload and mask, and the equality verdict uses only the recomputed values. The manifest entry must carry those same recomputed values |
| PE-123 | **final replicate validation did not recheck the base relationship** | neither `replicate_of_case_id` nor `assert_replicate_compatible` was consulted at final validation, and a replicate naming another replicate was unconstrained there | each expected replicate must carry `replicate_of_case_id`, that exact base row must be located, `assert_replicate_compatible` must pass, both records must be completed under the same phase authority and predecessor chain, the manifest `base_case_id` must equal `replicate_of_case_id`, and a replicate may never name another replicate. The frozen execution-assurance failure semantics are unchanged and are applied **before** a final manifest is persisted |
| PE-124 | **source comments described separate per-phase authorization commits** | the driver docstring and `AUTHORISATION_NOTE` state that "each phase must be added to `AUTHORISED_SOLVING_PHASES` by its own reviewed source commit", while `require_phase_manifests` requires every predecessor authority to share this phase's `source_commit` and `source_tree` — so under sequential commits P1a could never consume P0 | the pre-freeze authorization is an ATOMIC SOURCE COHORT: `PREFREEZE_SOLVING_AUTHORIZATION_COHORT = ("P0", "P1a", "P1b", "P2a")` and `PREFREEZE_ASSEMBLY_AUTHORIZATION_COHORT = ("P2b",)`. At a committed head only two states are permitted — no pre-freeze phase authorized, or the complete cohort authorized in canonical order with P2b in the assembly allowlist. Every partial state is rejected. Each phase remains separately gated by its prerequisites, so execution does not become monolithic; P3/P4 require a later source commit and stay blocked by `POST_FREEZE_EXECUTOR_READY = False` |
| PE-125 | **the README retained C1/C2 descriptions and superseded C3/C4 counts** | at the C8 exact head §4 still described `PROTOCOL.md` as "§19 (C1) and §20 (C2) the effective protocol, §20 governing", `PREFLIGHT_ERRATA.md` as "PE-0 … PE-21 across both generations", and §5 reported 383 normal solves, 144 pressure-plane diagnostics, 112 mandatory minimum, 847 adaptive maximum and 735 refused | README.md is a CURRENT guide, not an append-only protocol. It identifies C9 as effective, states the full C0 → … → C9 precedence, and reports only machine-derived current counts. Historical values live in this errata record, not in the current guide |
| PE-126 | **the documented P0 command used the unsafe default output location** | `python -m puckworks.validation.slow.rp_d_lc_001b --mode P0` with no `--output`, which under PE-114 selected the repository-internal runs directory | every documented execution or assembly command carries an explicit external absolute-path placeholder, e.g. `--output /ABSOLUTE/PATH/OUTSIDE/THE/PUCKWORKS/REPOSITORY`. No production P0 command that silently selects a repository-internal directory is provided anywhere in the bundle |

## Effective C9 machine-readable artifacts

Regenerated from one machine authority after every C9 document edit. These are the hashes the C9
head actually carries.

| artifact | effective C9 SHA-256 |
|---|---|
| `generated/protocol.json` | `69358ddf1a38a86a2668fdd2337ef791b6e2d54ec94659b7c303b59889c68118` |
| `generated/fixture_spec.json` | `c73fcd410f69b9f7d1083ce9ad186574467bf09e0fa451d832cc1784a71657b3` |
| `generated/execution_matrix.json` | `6817f79ca3c3cab51b8e500e19f05c7df9c9a3fba9c1e9f96e69250adf92696e` |
| `generated/preflight_status.json` | `5c4d4e3cf668e336f21921accf268ceb7eb0d1c70cb08647e35f078a3c181914` (was `5da7b701a4fce31b67383ffa82f4514562f99eb0957f929443131892c5239d97` before the pre-freeze authorization commit) |

`fixture_spec.json` moved only because it carries `correction_version`; no geometry, mask hash or
topology audit changed. `execution_matrix.json` moved for the same reason plus the derived
post-freeze readiness field; **no row, no `case_id` and no count changed.** `protocol.json`
additionally publishes the frozen runtime-bundle policy, its refusal codes and the pre-freeze
cohorts. `preflight_status.json` carries the derived authorization state and the updated
`input_file_sha256`.

Effective C9 counts, each independently regenerated: **703** rows = **698** decision-bearing (378
normal + 320 audits) + **2** tau diagnostic + **3** execution-assurance; **703** planned provider
invocations; **110** mandatory minimum; **591** refused after the earliest stop; **511** same-field
node-offset summaries; **0** separate pressure-diagnostic rows; **0** solves executed.

### The pre-freeze authorization commit

The separate reviewed authorization commit that §27.5 reserves has since been made, on top of the C9
head. It changes **only** the three source-controlled authorization constants to
`AUTHORISED_SOLVING_PHASES = ("P0", "P1a", "P1b", "P2a")`,
`AUTHORISED_ASSEMBLY_PHASES = ("P2b",)` and `POST_FREEZE_EXECUTOR_READY = False`, giving the committed
state `COMPLETE_PREFREEZE_COHORT_AUTHORIZED`.

**`PREFLIGHT-C9` remains the effective correction version, and this is NOT a new erratum.** The
transition is the expected next step PE-124 and §27.5 already specify, not a defect. Of the four
controlled artifacts only `preflight_status.json` moves, because only it carries the authorization
state and the driver's own file hash; `protocol.json`, `fixture_spec.json` and
`execution_matrix.json` are **byte-identical**, all 703 rows and all 703 `case_id`s are
byte-identical, and every count above is unchanged. **No phase has run:** `solves_executed` remains
**0**, P3 and P4 remain absent from both allowlists and remain hard-refused by
`POST_FREEZE_EXECUTOR_READY = False`, execution still requires an explicit absolute output directory
outside the repository, and another exact-head review is required before P0 begins.

## Not embedded in any scientific hash

The runtime bundle's absolute pathname is a property of one workstation. The durable contract is
the **location class** `OUTSIDE_REPOSITORY` together with the **contents** of the bundle — never a
machine-specific path. No scientific hash, record identity, payload identity, manifest identity or
authority hash contains the resolved runs directory.

## Still deferred, unchanged

The post-freeze historical-version boundary of §26.8 remains a recorded **P3/P4 prerequisite**.
C9 does not implement the dispatcher, does not claim that current-`CORRECTION_VERSION` equality
suffices for all future review commits, and keeps `POST_FREEZE_EXECUTOR_READY = False`.

## What did NOT change in C9

The common-mode-port apparatus · the lateral-only bridge geometry · **PE-66** · every forcing and
resolution gate · every pressure control · the artifact, `c` and actual-`Ξ` uncertainty methods ·
all four frozen tolerances · `NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0` · the `0.10·K`
reachable-set margin · the candidate family · **one below plus three inside** · the reachable-set
admission · the claim ceiling · the similarity law · the Route-A observable contract · **no
solver-core change** · the scientific row set and every row `case_id` · the mandatory minimum of
110 · **the allowlists, which remain empty** · **RP-D-LC-001 byte-unchanged** · and every phase,
solving and assembly alike, **unauthorized**. **No solver row is added** for a runtime-path check,
a payload recomputation, an audit reconstruction or a cohort parse, and none of that work is a
provider invocation. No LB solve ran to produce this correction.
