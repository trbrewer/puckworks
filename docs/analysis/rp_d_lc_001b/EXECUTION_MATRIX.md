# RP-D-LC-001b — planned execution matrix

```
VERSION PREFLIGHT-C8 (supersedes bbf2304, 2cf0b63, c666707, 39533ad, e455c67,
acb4f6a, 76e5669 and b5eb378)
NO ROW IN THIS DOCUMENT HAS BEEN EXECUTED
solves_executed: 0     lb_solver_invoked: false     AUTHORISED_SOLVING_PHASES: ()
AUTHORISED_ASSEMBLY_PHASES: ()      POST_FREEZE_EXECUTOR_READY: False
```

Machine-readable and authoritative: `generated/execution_matrix.json`, produced by
`rp_d_lc_001b_virtual_fixture.execution_matrix()`. **Every number below is generated from that
one authority and asserted against it by test** — no total is independently typed here. The
superseded C1 matrix (407 rows, five bridges, 20 Arm-J solves) is retained in
`PREFLIGHT_ERRATA.md` PE-13.

## 1. Every row is uniquely executable, and carries an EXACT forcing

Each row carries a stable unique `case_id` — which now includes the **exact forcing rational** —
plus `phase · kind · S · forcing_level · forcing_exact · forcing_repr · tau_plus · state ·
variant · bridge · coupon_level · coupon_orientation · swapped · perturbation · obstructed ·
run_mode · audit_of_case_id · audit_mode · backend · record_schema · prerequisite · class`.

`forcing_exact = {numerator, denominator}` is derived from `G_REF_EXACT`; the runtime float comes
from it through `row_forcing()` and is never independently written. A bare float could not be the
identity: the canonical writer rounds to twelve **decimal places**, which keeps only about six
significant digits of a `1e-7` forcing (erratum PE-21).

## 2. Ordering and early stops

```
P0 → P1a → P1b → P2a → P2b (freeze, STOP for review) → P3 → P4
```

| point | early-stop behaviour |
|---|---|
| **P1a** | a **TRIAGE** screen. It may REJECT a candidate when the point estimate alone exceeds the budget — every omitted uncertainty term is non-negative, so nothing can rescue it — but it may **never admit**, and a central result is never a final artifact upper bound |
| **P1b** | if **no** candidate meets `\|R−1\| + u_R ≤ 1e-3` at every required combination with its own fixed-step evidence → `DESIGN_BLOCKED_PRE_EXECUTION`. **591 rows are then refused** |
| **P2a** | a candidate failing forcing invariance or resolution consistency is not eligible |
| **P2b** | if the frozen rule cannot fill **4** unique slots from unambiguous candidates → `DESIGN_BLOCKED_PRE_EXECUTION` with a frozen reason code. No improvised slot, no reselection |
| **P3** | any run reaching `max_steps` is `UNCONVERGED` and stops the phase; **an audit may never rescue it** |
| **P4** | a breached Route-A isolation bound gives `INVALID_EXECUTION` |

## 3. Counts

| class | rows |
|---|---|
| planned **normal** solves | **383** |
| planned **fixed-step audits** | **320** |
| mandatory minimum (P0 + P1a, incl. replicates) | **112** |
| conditional on P1a (P1b) | 240 |
| conditional on P1b (P2a) | 288 |
| conditional on the freeze (P3) | 46 |
| conditional on P3 (P4) | 16 |
| diagnostic replicates | 3 |
| **adaptive maximum** | **703** |
| refused after the earliest stop | **591** |

| phase | rows | content |
|---|---|---|
| P0 | 63 | reference-blocked ladder + axial coupons (both orientations, full ladder) + the scheduled `tau = 1.2` cross-check + one replicate, each selection-bearing row paired with its own audit |
| P1a | 49 | central identical-path triage, all candidates, both resolutions, + one replicate |
| P1b | 240 | `×0.5`/`×2` extensions **and one fixed-step audit per artifact combination** |
| P2a | 288 | bridge-coupon ladders + candidate blocked-mirror characterisation, each paired with its own audit |
| P2b | 0 | arithmetic only — **no solver call** |
| P3 | 47 | templates until instantiation, for **4** frozen bridges |
| P4 | 16 | Arm J, for **4** frozen bridges |

P1b and P2a are **adaptive** and are emitted at their maximum; rows for rejected candidates are
refused, not run.

## 4. Fixed-step audits, not continuations

```
target = CHECK · ⌈1.5 · base_steps / CHECK⌉      min_steps = max_steps = target
```

The superseded audit raised `max_steps` while leaving `min_steps = 2000`, so the solver could stop
at the base step count and the audit could be a **no-op**. Preconditions: the base case converged
normally; the target exceeds the base count and is aligned to `CHECK`; `MAX_STEPS_AUDIT` bounds it.
Statuses are `NORMAL_CONVERGED` / `NORMAL_UNCONVERGED` / `FIXED_STEP_AUDIT_COMPLETED` /
`FIXED_STEP_AUDIT_INCOMPLETE` — `converged = steps < MAX_STEPS` is never used for an audit.

**Coverage is candidate-specific.** Every candidate × {blocked, open} × {S=2, S=3} × {low,
central, high} has its own evidence, as do the coupon and blocked-mirror rows that build `Ξ` and
`c`. The superseded two-extremes extrapolation is gone.

## 5. Records, manifests and the freeze

Every solve writes one **immutable** compact case record, atomically (temp + rename), never
overwritten, its filename derived from `case_id`. A resume verifies and reuses an **exact** match
and otherwise fails closed. Each phase writes a validated **ledger** — expected/completed/refused/
failed, per-record paths and hashes, per-row hashes, adaptive inputs and result, terminal status —
and validation reopens and rehashes every cited record. P1b and P2a expectations are **derived**
from validated predecessor decisions, never supplied.

**P2b derives the freeze from records**: `assemble_p2b_from_runs(runs_dir)` recomputes the
artifact from each pair's own records and audits, the `c` interval from `field_contrast()` over
the blocked-mirror records, and `Ξ` from the coupon conductance combined with those same records'
lane areas — then applies the four-slot rule, instantiates and hashes the P3/P4 matrix, and stops
with `PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW`. It accepts no free-form candidate, envelope,
interval, eligibility flag or hash list, and one record hash may never bind two geometries.

## 6. Compute

**Planning information only, not an admission criterion.** No wall-time estimate is claimed. The
S=2 domain is 112 × 48 × 16 lattice nodes and the S=3 domain 168 × 72 × 24, on a float64 NumPy
D3Q19 TRT kernel. Heavy execution stays in `puckworks/validation/slow/` and never enters normal CI.

## 7. What is refused right now

**Every row.** `AUTHORISED_SOLVING_PHASES = ()`, so all six solving phases raise
`ExecutionNotAuthorised`; P3 and P4 additionally raise `FreezeMissing`; every phase after P0
raises `ManifestMissing`. The freeze and manifest gates are checked **before** the allowlist, so
neither is shadowed by it. All are asserted by test, alongside an instrumentation assertion that
`lb_reference.solve` is never reached.


---

## 8. CORRECTION `PREFLIGHT-C3` — recomputed counts and the new row family

Every number here is produced by `execution_matrix()` and asserted against it by test. The C2
totals (703 = 383 + 320, 112 mandatory, 591 refused) are **superseded** and survive only in
`PREFLIGHT_ERRATA.md` PE-22.

**New row family: pressure-plane diagnostics.** Erratum PE-32 found a named `u_node_offset_R`
term that was always exactly zero because the assembler never passed any evidence. The frozen
node-surface offsets need **no extra solve** — they are different planes of one solution — but
they do need a *record*, so a diagnostic row is scheduled for every artifact combination and a
missing one now **fails** the evidence instead of contributing zero.

| class | rows |
|---|---|
| planned **normal solves** | **383** |
| planned **fixed-step audits** | **320** |
| planned **pressure-plane diagnostics** (no extra solve) | **144** |
| **adaptive maximum** | **847** |
| mandatory minimum (P0 + P1a) | **112** |
| refused after the earliest stop | **735** |
| determinism replicates | **3** |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 384 / 288 / 47 / 16 |

P3 and P4 are templates for **4** frozen bridges and are instantiated only by P2b.

## 9. What P2b writes, and what it refuses to write

An authorised P2b atomically produces `candidate_ledger.json`, `instantiated_p3_p4_matrix.json`,
`proposed_bridge_freeze.json` and `manifest_P2b.json` — with the freeze written **only** when the
four slots fill. A failed selection still writes a durable decision and manifest with
`PHASE_STOPPED_DESIGN_BLOCKED` and a frozen reason code, and **no proposed scientific freeze**.
All four use canonical strict-finite serialisation, temp-file + atomic rename, deterministic
filenames, no overwrite and exact-match resume.

**P2b never calls the solver**, and it has its own authority: `AUTHORISED_ASSEMBLY_PHASES`,
separate from `AUTHORISED_SOLVING_PHASES`. **Both are empty at this head.**

## 10. The full phase universe

Every adaptive phase manifest now carries `phase_universe_case_ids`, `mandatory_case_ids`,
`conditionally_eligible_case_ids` and `adaptively_ineligible_case_ids`, and validation requires an
exact, pairwise-disjoint partition

```
phase universe  =  completed  ⊎  failed  ⊎  refused
```

Adaptively ineligible rows remain **members** of the universe and are refused with a frozen
reason; the superseded executor recorded them as refused while the validator built its universe
from the eligible subset and then rejected them as extra.

---

## 11. CORRECTION `PREFLIGHT-C4` — the diagnostic rows are gone

Erratum PE-41: the 144 `pressure_plane_diagnostic` rows C3 scheduled each went through the result
provider, for offsets that are **re-reads of a field already computed**. They are removed; the
summary is extracted inside the case that produced the field. Erratum PE-42: the per-offset
quantity is a **conductance**, and `R_offset_j = C_open_offset_j / C_blocked_offset_j` is formed
only after an exact open/blocked pairing.

| class | rows |
|---|---|
| planned **normal solves** | **383** |
| planned **fixed-step audits** | **320** |
| planned **solver invocations** | **703** |
| node-offset summaries | 0 rows, 0 provider calls |
| **adaptive maximum** | **703** |
| mandatory / refused / replicates | **112** / **591** / **3** |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 240 / 288 / 47 / 16 |
| **solves executed** | **0** |

The C3 total of 847 is superseded and is retained only in `PREFLIGHT_ERRATA.md` PE-40.



## 12. CORRECTION `PREFLIGHT-C5` — one machine authority, every category distinguished

Errata PE-60 … PE-76. **No solver row is added to repair arithmetic or validation.** Every number
below is derived by `execution_matrix()` from the row set in one place; the total remains **703**
because the generator independently reproduces it, not because it was preserved.

| category | value |
|---|---|
| planned **NORMAL** solves | **383** |
| planned **FIXED_STEP** audits | **320** |
| `planned_solver_invocations` = normal + audits | **703** |
| same-field **node-offset summaries** (extracted, **0** provider calls) | **511** |
| **mandatory** rows | **112** |
| **adaptive** maximum | **703** |
| refused after the earliest stop | **591** |
| **arithmetic-only P2b** solver calls | **0** |
| **P3/P4 planning-template** rows | **63** |
| provider calls, **fresh full pre-freeze run** | **640** |
| provider calls, **exact resume** | **0** |
| `observed_provider_calls` (orchestration) | `= newly_executed_rows` |
| separate **pressure-diagnostic** rows | **0** — and none may return |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 240 / 288 / 47 / 16 |
| **solves actually executed** | **0** |

The identity `planned_solver_invocations = planned_normal_rows + planned_fixed_step_rows` is
retained and asserted by test, as is `observed_provider_calls == newly_executed_rows` for a real
orchestrated phase. A resumed phase legitimately has **fewer** provider calls than completed
rows, and an exact manifest resume has **none**.

**P3/P4 are not execution-ready.** Their 63 rows are planning TEMPLATES whose `bridge` is an
unresolved placeholder; `POST_FREEZE_EXECUTOR_READY = False` refuses them independently of the
solving allowlist (erratum PE-76).


## 13. CORRECTION `PREFLIGHT-C6` — decision-bearing rows separated from diagnostics

Errata PE-78 … PE-88. **No solver row is added or removed.** The two `tau_plus = 1.2` rows remain
planned solver invocations and stop being **decision-bearing**: PE-65 froze them
`DIAGNOSTIC_ONLY` and C5 emitted them `class = mandatory`. The mandatory minimum therefore
**changes**, and 703 survives only because the generator independently reproduces it.

| category | value |
|---|---|
| **decision-bearing** rows | **698** |
| decision-bearing **NORMAL** solves | **378** |
| decision-bearing **FIXED_STEP** audits | **320** |
| **tau diagnostic** solves (non-adjudicative, nonblocking) | **2** |
| **execution-assurance** rows (determinism replicates) | **3** |
| planned **NORMAL** solves, all roles | **383** |
| planned **FIXED_STEP** audits, all roles | **320** |
| `planned_solver_invocations` | **703** |
| same-field **node-offset summaries** (**0** provider calls) | **511** |
| **mandatory decision-bearing** rows | **108** |
| **mandatory minimum** (with pre-freeze assurance replicates) | **110** |
| **adaptive** rows | **703** |
| refused after the earliest stop | **591** |
| provider calls, **fresh** full pre-freeze run | **640** |
| provider calls, **exact resume** | **0** |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 240 / 288 / 47 / 16 |
| **solves actually executed** | **0** |

`planned_solver_invocations` equals the number of all planned rows that call the provider;
`observed_provider_calls == newly_executed_rows` in every phase; and the partition is now

```
mandatory_minimum (110) + refused_after_earliest_stop (591) + tau_diagnostic_rows (2) = 703
```

because a tau row is neither decision-bearing nor refused — it runs, it reports, and nothing
consumes it. Same-field node-offset summaries remain **zero** additional provider calls, and no
separate pressure-diagnostic row exists or may return.


## 14. CORRECTION `PREFLIGHT-C7` — counts unchanged, roles and authority made durable

Errata PE-89 … PE-100. **No solver row is added or removed**, and none is added for authority or
diagnostic-envelope bookkeeping. Every count is regenerated from `execution_matrix()`.

| category | value |
|---|---|
| `DECISION_BEARING` normal rows | **378** |
| `DECISION_BEARING` fixed-step audits | **320** |
| **decision-bearing** rows | **698** |
| **tau diagnostic** rows (non-adjudicative, nonblocking) | **2** |
| **execution-assurance** rows (determinism replicates) | **3** |
| total planned provider invocations | **703** |
| **mandatory decision-bearing** rows | **108** |
| **mandatory pre-freeze minimum** | **110** |
| **adaptive** rows | **703** |
| refused after the earliest stop | **591** |
| same-field **node-offset summaries** (**0** provider calls) | **511** |
| provider calls, **fresh** full pre-freeze run | **640** |
| provider calls, **exact resume** | **0** |
| provider calls, **diagnostic-failure-envelope resume** | **0** |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 240 / 288 / 47 / 16 |
| **solves actually executed** | **0** |

```
planned_solver_invocations = all rows that call the provider
provider_calls = new normal case records + new fixed-step case records
                 + new diagnostic-failure envelopes
```

A **diagnostic-failure envelope is not a row.** It is what a tau row leaves behind when its
attempt produces no result: one provider call, one persisted artifact, no scientific value, and
no change to any count above. An exact resumed envelope costs **zero** provider calls.

The role-resolved identities are now distinct in every phase manifest —
`decision_bearing_case_ids`, `execution_assurance_case_ids`, `diagnostic_case_ids` and
`adjudicative_case_ids` — so an execution-assurance replicate is no longer filed under a
decision-bearing name (erratum PE-100). No separate pressure-diagnostic row exists or may return.


## 15. CORRECTION `PREFLIGHT-C8` — counts unchanged; authority artifacts are not rows

Errata PE-101 … PE-113. **No solver row is added or removed**, and none is added for authority,
lineage or envelope validation. Every count is regenerated from `execution_matrix()`.

| category | value |
|---|---|
| `DECISION_BEARING` normal rows | **378** |
| `DECISION_BEARING` fixed-step audits | **320** |
| **decision-bearing** rows | **698** |
| **tau diagnostic** rows | **2** |
| **execution-assurance** rows | **3** |
| total planned provider invocations | **703** |
| **mandatory pre-freeze minimum** | **110** |
| **adaptive** rows | **703** |
| refused after the earliest stop | **591** |
| same-field **node-offset summaries** (**0** provider calls) | **511** |
| **phase-authority files** written per phase | **1** — **0** provider calls |
| new case records / new diagnostic envelopes | provider calls, one each |
| reused records / reused envelopes | **0** provider calls |
| P0 / P1a / P1b / P2a / P3 / P4 | 63 / 49 / 240 / 288 / 47 / 16 |
| **solves actually executed** | **0** |

```
provider_calls = new normal case records + new fixed-step case records
                 + new diagnostic-failure envelopes
```

**An `execution_authority_<phase>.json` is not a row.** It is the durable preimage of the
authority the phase ran under, written once per phase before the first provider call, costing no
provider call and adding no planned invocation. A **diagnostic-failure envelope** likewise
remains what a tau row leaves behind when its attempt produces no result.

**Every production authority construction refuses at this head**, because
`AUTHORISED_SOLVING_PHASES` and `AUTHORISED_ASSEMBLY_PHASES` are both empty and
`POST_FREEZE_EXECUTOR_READY` is false. The counts above are what a future **reviewed
authorization commit** would plan, not what anything has run.
