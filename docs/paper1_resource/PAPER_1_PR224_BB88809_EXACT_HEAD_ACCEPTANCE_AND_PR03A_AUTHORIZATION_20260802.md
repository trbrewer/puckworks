# Paper 1 — PR #224 exact-head acceptance and PR-03a formal-assurance authorization

**Date:** 2 August 2026  
**Repository:** `trbrewer/puckworks`  
**Pull request:** #224, open and unmerged  
**Reviewed head:** `bb88809bdf8bc477093ccbe14bb59b4232cafff9`  
**Reviewed tree:** `019deca72f6d97c7794611cb618ff789c5ff9252`  
**Parent:** `e8b98598ee666a2e00b9880f00f1a6bfecb35d86`  
**Review mode:** exact-head, read-only

---

## 1. Disposition

```text
P0_G8_WIDE_REFERENCE_ARCHITECTURE_EXACT_HEAD_ACCEPTED
P0_G8_ARCHIVE_CONTRACT_EXACT_HEAD_ACCEPTED
WIDE_REFERENCE_SCOPE_CLOSED_NO_FURTHER_ARCHITECTURE_ADDITIONS
EXACT_HEAD_BB88809_ACCEPTED_AS_NEXT_CYCLE_BASE
PR_224_CONTINUE_OPEN_AND_UNMERGED
NEXT_BOUNDED_CYCLE_PR03A_FORMAL_ASSURANCE_AUTHORIZED
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
NO_CAMPAIGN_OBJECTIVE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **The WIDE-referenced P0-G8 architecture is accepted at exact head `bb88809`.**
>
> No further WIDE-reference architecture defect or addition will be introduced in the next cycle.
> The next cycle is restricted to PR-03a formal assurance and the minimum normative/evidence updates
> necessary to bind that assurance.

This accepts:

- the `FULL-WIDE-ENDPOINT` estimand;
- `D_WIDE = [0.15,500]`;
- separate `J_ref` and `J_inf`;
- the relative and absolute threshold families;
- quantity-specific numerical budgets;
- finite-WIDE minimization/topology;
- endpoint, eventual-upper, onset, and intermediate-domain separation;
- the `unresolved | assured | failed` precondition vocabulary;
- the frozen H1 group and programme rules;
- the archive contract and its group-derived `programme_result`.

It does **not** pass P0-G0, authorize P0-G8, merge PR #224, create freeze commit F, or create activation commit A.

---

## 2. Exact-head findings

## 2.1 The programme result is now a derived result

The exact-head validator now:

1. requires exactly six group records;
2. requires unique, nonblank identifiers;
3. validates every group and every convention;
4. reconstructs the group outcome from the archived endpoint classifications;
5. derives the programme result from the six group outcomes; and
6. rejects any declared programme label that disagrees.

The former fail-open states are closed:

```text
zero groups + H1_STRONG
six excluded groups + H1_STRONG
five successes + one exception + H1_STRONG
```

The archive can no longer treat `programme_result` as an independent disposition.

## 2.2 The two group-coherence rules are correct

The exact head correctly enforces:

### Endpoint-construction failure is group-wide

```text
limit_construction_failed
```

is a property of the group's endpoint construction, not a threshold convention. It must therefore
apply to every convention or none.

### An unresolved reference minimum permits no endpoint comparison

When:

```text
reference_minimum_status = unresolved
```

the threshold is unresolved. The only coherent classification is:

```text
endpoint_indeterminate
```

unless the endpoint construction itself failed under every convention.

## 2.3 Failed eventual-upper premise remains correctly separated from endpoint classification

The fixed-positive-time proposition concerns the inference from a numerical endpoint comparison to
eventual finite-κ behavior. It does not alter the endpoint interval comparison itself.

Therefore the exact-head behavior is accepted:

```text
precondition = failed
endpoint_classification = retained
eventual_upper_status = upper_status_indeterminate
programme_result = still derived from endpoint classifications
```

The machine result does not silently become reader-facing eventual-upper prose while the premise is
unresolved or failed.

## 2.4 Test coverage is adequate for this architecture scope

The added rejection and acceptance cases directly exercise the archive entry point rather than only
testing helper functions. The prior separation between “correct rule” and “validator that never calls
it” is removed.

The reported validations are accepted:

```text
focused WIDE-reference tests: 60 passed
full suite: 3463 passed, 1 skipped
remote checks: 24 passed, 0 failed, 0 pending
```

No scientific gate was run, and the P0-G8 result archive remains absent.

---

## 3. Scope closure

The WIDE-reference work package is now closed.

The following must **not** be reopened in the PR-03a cycle:

- `D_WIDE`;
- `J_ref`;
- `J_inf`;
- `FULL-WIDE-ENDPOINT`;
- threshold families;
- threshold interval rules;
- endpoint-classification rules;
- H1 group/programme rules;
- nested grid sizes;
- finite-domain topology rules;
- numerical tolerances;
- error-budget allocation;
- eventual-upper status vocabulary;
- tail-onset and intermediate-domain dispositions;
- the six-group archive evidence unit;
- programme-result derivation.

A later change to any of these requires a separately identified protocol amendment and renewed
authority. It cannot enter incidentally through PR-03a.

---

## 4. Next bounded cycle: PR-03a formal assurance

## 4.1 Objective

Establish and bind the proposition that, for the declared semi-discrete system and every declared
operator-distinct cell, the stable null-basis endpoint is the fixed-positive-time large-κ limit:

```text
exp((A0 + κ A1) T) z0
    -> N exp((L^T A0 N) T) L^T z0
```

for each fixed `T > 0`.

The cycle must distinguish:

1. the mathematical limit proposition;
2. verification of its assumptions;
3. numerical construction of the endpoint;
4. finite-κ numerical diagnostics; and
5. complete declared-cell coverage.

Finite-κ diagnostics must not serve as the proof.

---

## 4.2 Required theorem artefact

Create a dedicated artefact, preferably:

```text
docs/paper1_resource/PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md
```

It must define:

```text
A(κ) = A0 + κ A1
P = N L^T
Q = I - P
L^T N = I
A_s = L^T A0 N
```

and state the assumptions:

1. `A0` and `A1` are finite-dimensional and fixed for the declared cell.
2. Zero is a semisimple eigenvalue of `A1`.
3. Every nonzero eigenvalue of `A1` lies strictly in the open left half-plane.
4. `N` spans `ker(A1)`.
5. `L` spans `ker(A1^T)` and is normalized by `L^T N = I`.
6. `T > 0` is fixed.

Under those assumptions, prove:

```text
lim_{κ->∞} exp((A0 + κA1)T)
    = N exp((L^T A0 N)T) L^T
```

in the sense required for the declared state/output.

### Permitted proof routes

A finite-dimensional block decomposition, spectral projection/group-inverse argument, or
variation-of-constants argument is acceptable.

A useful block form is:

```text
x_s' = A_ss x_s + A_sf x_f
x_f' = A_fs x_s + (κ A_ff + A_ff0) x_f
```

with `A_ff` Hurwitz.

The proof must account for:

- the initial fast component `Q z0`;
- the initial layer;
- slow–fast and fast–slow coupling through `A0`;
- the distinction between fixed-positive-time convergence and uniform convergence at `t=0`.

### Required qualification

For off-manifold initial data:

```text
zκ(0) - Pz0 = Qz0
```

does not tend to zero. Therefore do not claim a uniform `O(1/κ)` state bound on `[0,T]`.

Permitted formulations are:

- convergence for every fixed `T > 0`; or
- uniform convergence on `[δ,T]` for every `δ > 0`.

A qualitative fixed-time estimate may be stated in a form such as:

```text
||rκ(T)|| <= C_T/κ + M_T exp(-c κ T)||Qz0||
```

for sufficiently large `κ`, provided every term is derived rather than fitted to observed output
errors. A sharp constant is not required because this protocol does not estimate finite tail onset.

---

## 4.3 Assumption verification at every operator-distinct cell

For all 27 operator-distinct cells, archive:

### Index-one / semisimplicity

At minimum:

```text
rank(A1) = rank(A1^2)
```

under frozen rank tolerances, or an equivalent semisimplicity test.

Record:

- rank;
- nullity;
- rank tolerance;
- sensitivity to the declared tolerance family.

### Fast-spectrum stability

Verify all nonzero modes lie strictly in the left half-plane.

Record:

```text
max_real_fast_eigenvalue
fast_mode_count
spectral_method
spectral_tolerance
```

Use an ordered Schur or equivalently stable method where practical. The SVD rank-separation ratio is
not the fast spectral decay gap.

### Slow projector

Record:

```text
||A1 N||
||L^T A1||
||L^T N - I||
||P^2 - P||
||A1 P||
||P A1||
cond(L^T N) before normalization
cond(L)
```

`cond(N)=1` for an orthonormal SVD basis may be recorded but must not be treated as an independent
operator-conditioning result.

### Endpoint output

Require every endpoint output to be:

```text
finite
real within declared tolerance
strictly positive
```

Record the endpoint construction and output mapping for each cell.

### Coverage

Retain:

```text
27 operator-distinct cells
54 declared variety–solute–condition cells
```

with the explicit variety-deduplication proof.

No cell may be removed because of an inconvenient assumption result.

---

## 4.4 Evidence schema

Replace the single overloaded status with:

```text
algebraic_limit_status:
  assured | not_assured

endpoint_construction_status:
  verified | failed

finite_kappa_validation_status:
  consistent | method_limited | inconsistent

coverage_status:
  complete | incomplete

overall_PR03a_status:
  assured | not_assured
```

`overall_PR03a_status = assured` only when:

```text
algebraic_limit_status = assured
endpoint_construction_status = verified
coverage_status = complete
finite_kappa_validation_status != inconsistent
```

The finite-κ sequence may be `method_limited` without invalidating the theorem.

### Current audit state during the cycle

Until the theorem and assumption bindings are complete, PR-03a must not remain unqualified
`assured`.

Use an append-only transition or temporary state equivalent to:

```text
partially_assured
```

Then set it to `assured` only when the generated evidence meets the complete closure rule.

---

## 4.5 Finite-κ diagnostic

Retain the sequence:

```text
κ = 10^2, 10^3, 10^4, 10^5, 10^6
```

only as a full-state matrix-exponential diagnostic.

Required changes:

- call it a diagnostic, not an independent proof;
- capture numerical warnings in the archive;
- retain the U-shaped/method-limited behavior honestly;
- do not make `TAIL_ABS_CAP` or a ratio rule determine the theorem;
- do not fit any criterion to the 27 observed trajectories;
- remove unsupported universal `O(κ eps)` language, or label it explicitly as a diagnostic
  interpretation rather than a proved error law;
- retain the failed-run nonzero-exit regression test.

Possible diagnostic dispositions:

```text
consistent
method_limited
inconsistent
```

An `inconsistent` diagnostic blocks overall assurance until explained by a separately frozen and
tested method limitation. `method_limited` does not.

---

## 4.6 Producer and archive reproducibility

The producer must support:

```text
python tools/paper_a_endpoint_construction.py --write
python tools/paper_a_endpoint_construction.py --check
```

`--check` must:

1. regenerate canonical output;
2. compare it semantically and/or byte-for-byte under a declared canonical JSON serialization;
3. return nonzero on any mismatch;
4. return nonzero when `overall_PR03a_status != assured`.

Archive:

- protocol version;
- proof artefact path and SHA-256;
- producer path and SHA-256;
- every model/input path and SHA-256;
- command;
- Python, NumPy, SciPy, and platform;
- warnings;
- all assumptions and tolerances;
- 27-cell evidence;
- 54-cell mapping;
- all five status fields;
- failures and exceptions.

The endpoint archive must be generated by the producer. Manual verdict editing is prohibited.

---

## 4.7 Normative updates permitted

Only the following normative updates are authorized:

1. the PR-03a proof artefact;
2. the PR-03a producer and archive;
3. focused PR-03a tests;
4. the PR-03a row and generated summary in the premise audit;
5. the fixed-positive-time precondition status in Protocol V2;
6. the minimal claim-resolution delta needed to record the assurance transition;
7. integrity/source-surface declarations required for those files.

If PR-03a closes:

```text
eventual_upper_precondition_status = assured
```

may replace `unresolved`.

That change must not alter endpoint classifications, H1 rules, or any WIDE-reference formula.

---

## 4.8 Required tests

At minimum:

### Algebraic fixtures

- semisimple zero plus stable fast block: pass;
- defective zero/Jordan block: fail;
- unstable fast eigenvalue: fail;
- zero fast decay margin within tolerance: fail or indeterminate;
- off-manifold initial condition: fixed-positive-time pass, uniform-at-zero claim rejected;
- normal and strongly nonnormal stable fast blocks;
- nontrivial `A0` slow–fast coupling.

### Construction fixtures

- exact left/right null bases;
- nearly ill-conditioned `L^T N`;
- projector residual failure;
- nonpositive endpoint output;
- complex endpoint outside real tolerance;
- incomplete declared-cell coverage.

### Producer behavior

- `NOT_ASSURED` returns nonzero;
- `--check` detects archive drift;
- source/input hash drift is detected;
- warning capture is retained;
- no campaign-data import or P0-G8 result archive;
- the WIDE-reference architecture files and constants remain unchanged.

---

## 5. Prohibited activity

- no P0-G8 execution;
- no campaign `y`, `J`, `J_ref`, `J_inf`, threshold, topology, shoulder, or classification;
- no P0-G8 result archive;
- no PR-03b derivation;
- no changes to the WIDE-reference architecture;
- no PR-07 or PR-09 implementation in this cycle;
- no premise-gating, commit-closure, or activation-ceremony work beyond a minimal reference required
  by PR-03a evidence;
- no manuscript drafting;
- no merge;
- no freeze commit F;
- no activation commit A.

---

## 6. Required terminal disposition

Return:

```text
PR03A_FORMAL_ASSURANCE_COMPLETE_PR_OPEN
```

only when:

- the fixed-positive-time theorem is written and internally checked;
- every theorem assumption is verified at all 27 operator-distinct cells;
- all 54 declared cells remain covered;
- endpoint construction is verified;
- finite-κ diagnostics are correctly separated from the proof;
- all status fields are generated;
- `--check` passes;
- focused, full, lint, scanner, and remote checks pass;
- no scientific gate or campaign objective has run;
- `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` remains absent;
- PR #224 remains open and unmerged.

Otherwise return:

```text
PR03A_FORMAL_ASSURANCE_NOT_READY
```

and list only unmet requirements from this authorization.

---

## 7. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 PR-03A FORMAL-ASSURANCE CYCLE

## Authority

- Exact accepted base: `bb88809bdf8bc477093ccbe14bb59b4232cafff9`
- WIDE-reference architecture is closed and must not change.
- PR #224 remains open and unmerged.
- P0-G0 remains open; plan remains candidate.
- No P0 scientific gate, campaign objective, merge, F, or A is authorized.

## Objective

Formally assure the fixed-positive-time singular limit and bind the stable null-basis endpoint to its
mathematical assumptions across all 27 operator-distinct / 54 declared cells.

## Mandatory work

1. Add `PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md`.
2. Prove for fixed T > 0:

       exp((A0 + kappa A1)T) z0
         -> N exp((L^T A0 N)T) L^T z0

   under semisimple zero and stable nonzero spectrum.
3. Explicitly reject uniform-at-t=0 convergence for off-manifold initial data.
4. Verify at every operator-distinct cell:
   - rank(A1)=rank(A1^2) or equivalent semisimplicity;
   - every fast eigenvalue has negative real part;
   - projector identities and conditioning;
   - finite, real, positive f_inf;
   - complete 54-cell coverage.
5. Split evidence into:
   - algebraic_limit_status;
   - endpoint_construction_status;
   - finite_kappa_validation_status;
   - coverage_status;
   - overall_PR03a_status.
6. Demote the high-kappa sequence to a diagnostic. It must not prove the theorem.
7. Add canonical `--check`, producer/input/proof hashes, environment and warning capture.
8. Update only PR-03a evidence, audit, and the fixed-positive-time precondition status.
9. If and only if every closure criterion passes, set the precondition to `assured`.

## Prohibited

- No change to D_WIDE, J_ref, J_inf, tags, thresholds, H1, grids, topology, tolerances, budgets, or
  archive programme-result logic.
- No campaign result or P0-G8 archive.
- No PR-03b, PR-07, PR-09, manuscript drafting, merge, F, or A.

## Terminal response

Return `PR03A_FORMAL_ASSURANCE_COMPLETE_PR_OPEN` only when the bounded scope is complete and the PR
remains open/unmerged. Otherwise return `PR03A_FORMAL_ASSURANCE_NOT_READY`.
```
