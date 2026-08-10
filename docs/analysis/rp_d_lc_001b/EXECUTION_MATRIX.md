# RP-D-LC-001b — planned execution matrix

```
VERSION PREFLIGHT-C1 (corrected; supersedes the version at bbf2304)
NO ROW IN THIS DOCUMENT HAS BEEN EXECUTED
solves_executed: 0     lb_solver_invoked: false
```

Machine-readable and authoritative: `generated/execution_matrix.json`, produced by
`rp_d_lc_001b_virtual_fixture.execution_matrix()`. This document is its human-readable face; where
they could disagree, the generated file wins and the tests bind the two. Every count below is
**computed**, never transcribed — the superseded 195-row matrix and its inconsistent 131-vs-133
refused-row figures are recorded in `PREFLIGHT_ERRATA.md` (PE-10, PE-12).

## 1. Every row is uniquely executable

Each row carries a stable unique `case_id` built from its own configuration, plus:

`phase · kind · S · forcing_level · forcing · tau_plus · state · variant · bridge ·
coupon_level · coupon_orientation · swapped · perturbation · obstructed · audit_mode ·
backend · record_schema · prerequisite · class`

`_row()` refuses an under-specified row, and tests assert `case_id` uniqueness, the absence of
duplicate canonical rows once `case_id` is removed, that both coupon orientations appear
distinctly, that every conditional row declares a prerequisite, and that every row resolves to
exactly one fixture and solver configuration.

## 2. Ordering and early stops

```
P0 → P1a → P1b → P2a → P2b (freeze, STOP for a second exact-head review) → P3 → P4
```

| point | early-stop behaviour |
|---|---|
| **P1a** | a candidate whose central identical-path artifact **upper bound** already exceeds `1e-3` at either resolution is rejected; its P1b and P2a rows are refused |
| **P1b** | if **no** candidate meets the budget across all three forcing levels at both resolutions → `DESIGN_BLOCKED_PRE_EXECUTION` / `NO_CANDIDATE_WITHIN_ARTIFACT_BUDGET`. **325 rows are then refused** |
| **P2a** | a candidate failing forcing invariance or resolution consistency is not eligible for selection |
| **P2b** | if the frozen rule cannot fill all 5 unique slots from unambiguous candidates → `DESIGN_BLOCKED_PRE_EXECUTION` with a frozen reason code. **Do not improvise a slot and do not re-select** |
| **P3** | any run reaching `max_steps` is `UNCONVERGED` and stops the phase; no retry at a looser tolerance |
| **P4** | a breached Route-A isolation bound gives `INVALID_EXECUTION` — never a relaxed second tolerance, never a switch to Route B |

**Replicate policy, stated as a rule rather than an exception.** Three determinism replicates, in
**P0, P1a and P3** — the three phases producing decision-bearing records from *distinct fixture
families* (reference-blocked, identical-path, mirror). P2a re-uses those families and P4 re-uses
P3's fixtures with an obstruction, so a fourth would add no independent evidence. Each replicate
repeats a case its **own** phase already runs, so P1a's is identical-path and cannot reveal a
mirror observable. There are no statistical replicates: every case is deterministic with no RNG.

**Reuse policy.** P3 re-uses P2a's candidate blocked-mirror records for the frozen bridges rather
than re-solving them — identical mask, identical forcing, identical solver configuration, and the
solver is deterministic. The reuse is recorded per case, never silent.

## 3. Counts

| class | rows |
|---|---|
| **mandatory minimum** (P0 + P1a, incl. their replicates) | **82** |
| conditional on P1a (P1b) | 104 |
| conditional on P1b (P2a) | 144 |
| conditional on the freeze (P3) | 56 |
| conditional on P3 (P4) | 20 |
| diagnostic replicates | 3 |
| **adaptive maximum** | **407** |
| refused after the earliest stop | **325** |

| phase | rows |
|---|---|
| P0 | 33 |
| P1a | 49 |
| P1b | 104 |
| P2a | 144 |
| P2b | 0 (arithmetic only — no solve) |
| P3 | 57 (templates until instantiation) |
| P4 | 20 (templates until instantiation) |

P1b and P2a are **adaptive**: they are emitted at their maximum, with every declared scientific
candidate surviving. Rows for rejected candidates are refused, not run.

## 4. The phases

### P0 — common blocked characterisation · 33 rows · MANDATORY

- **reference-blocked mirror ladder** — both resolutions × all three forcing levels (6);
- **axial coupons** — both resolutions × all three forcing levels × {high, low} × **both lattice
  orientations** (24). The superseded matrix ran coupons at central forcing only and omitted the
  orientation field entirely;
- **`tau_plus = 1.2` cross-check** — both resolutions at central forcing (2), scheduled rather
  than merely asserted;
- one determinism replicate.

**Produces:** the reference `c_field`, `A₁`, `A₂`; `a_coupon`, `b_coupon`, `c_coupon`; the
blocked-side componentwise forcing-invariance evidence; and the first true mass-conservation
measurement in the programme's history.

### P1a — central identical-path screen · 49 rows · MANDATORY · DECISION-BEARING

12 scientific candidates × {blocked, open} × {S = 2, S = 3}, central forcing,
`variant = "identical"`, plus one replicate. **No mirror recovery case is run or inspected.**

### P1b — forcing extension and continuation · ≤ 104 rows · CONDITIONAL ON P1a

`×0.5` and `×2` identical-path extensions for every candidate still selectable (≤96), plus 8
continuation runs on the **smallest and largest** bridge at both resolutions and both states. The
worst continuation movement bounds `u_artifact_R` for every candidate — declared, not assumed
away. **Final artifact admission uses all three forcing levels at both resolutions.**

### P2a — coupon ladders and blocked-mirror characterisation · ≤ 144 rows · CONDITIONAL ON P1b

- **bridge coupons** — survivors × both resolutions × all three forcing levels (≤72);
- **candidate blocked mirror** — survivors × both resolutions × all three forcing levels (≤72),
  the measured basis for each candidate's `[c_lower, c_upper]`.

A blocked mirror fixture exposes no open coupling-recovery observable, so this is permitted before
the freeze. **No candidate OPEN mirror case is run.**

### P2b — admissibility, selection and proposed freeze · 0 solves

Apply the artifact upper-bound gate, then the reachable-set admission built on each candidate's own
measured contrast interval, then the forcing-invariance and resolution-consistency gates, then the
frozen selection rule. Write and hash `runs/bridge_freeze.json` **and** the instantiated P3/P4
matrix. **Stop for a second exact-head review.**

### P3 — primary mirror / path-swap experiment · 57 rows · CONDITIONAL ON THE FREEZE

| block | rows | detail |
|---|---|---|
| primary mirror **open** | 30 | 5 frozen bridges × {S=2, S=3} × {×0.5, ×1, ×2}; the blocked counterparts are re-used from P2a |
| path-swap control | 20 | 5 × {S=2, S=3} × {blocked, open}, central forcing, `swapped=True` |
| one-voxel adversarial | 4 | {plug, slab} × {blocked, open} at `S_FINE`, first frozen bridge |
| continuation audit | 2 | one per resolution at `1.5 ×` the converged step count |
| determinism replicate | 1 | |

### P4 — Arm J return-path nuisance isolation · 20 rows · CONDITIONAL ON P3 · DECISION-BEARING

5 frozen bridges × {blocked, open} × {S = 2, S = 3}, central forcing, plenum obstructed. Gate:
`|R_obstructed/R_nominal − 1| ≤ 1e-3` and `|s_obstructed − s_nominal| ≤ 5e-4`, with the induced
changes in `ĉ`, `Ξ̂` and the sign of `s − ½` reported and never fitted. Arm J is **not** silently
omitted to shrink the matrix.

## 5. Positive and negative controls, by name

| control | where | what it proves |
|---|---|---|
| uniform-duct coupon (`ΔP = g·L` exactly) | P0 | the frozen pressure definition is coherent in the periodic body-force formulation — an analytic **positive** control |
| `tau_plus` cross-check | P0 | the frozen relaxation time is a time-step economy, not a physics change |
| identical-path zero-lateral-driver | **P1a/P1b** | opening the bridge does not widen the axial channel — the **negative** control 001 failed |
| continuation audit | P1b, P3 | the convergence criterion is sufficient for the observables, and it bounds `u_artifact_R` |
| candidate blocked mirror | P2a | the contrast interval that sets the reachable ceiling, with no open-case exposure |
| path swap | P3 | the signature reverses where it must and is preserved where it must |
| one-voxel adversarial asymmetry | P3 | how much a sub-1 % construction asymmetry can bias `Ξ̂` |
| plenum obstruction (Arm J) | P4 | the return path is isolated to the programme's 0.1 % scale |
| determinism replicate | P0, P1a, P3 | the record is reproducible byte-for-byte |

## 6. Compute

**Planning information only — clearly separated from every scientific admission criterion, and not
an assertion.** No wall-time estimate is claimed, because none has been measured for this geometry.
What is known: the S=2 domain is 112 × 48 × 16 lattice nodes and the S=3 domain 168 × 72 × 24, on
a float64 NumPy D3Q19 TRT kernel. Heavy execution stays in `puckworks/validation/slow/` or
local/Colab runs and **never** enters normal CI (CLAUDE.md rule 3).

## 7. What is refused right now

**Every row.** `AUTHORISED_SOLVING_PHASES = ()`, so all six solving phases raise
`ExecutionNotAuthorised`; P3 and P4 additionally raise `FreezeMissing`, and every phase after P0
raises `ManifestMissing` for its predecessors. All three refusals are asserted by test.
