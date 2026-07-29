# Paper 1 — Detailed Review, Round 9

**Review date:** 29 July 2026  
**Review target:** commit [`45e753a5f37ede66cd99a016a6b8902fdbadebdf`](https://github.com/trbrewer/puckworks/tree/45e753a5f37ede66cd99a016a6b8902fdbadebdf) on `main`  
**Governing brief:** [`PAPER_1_REVIEW_BRIEF_ROUND_9.md`](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_9.md)  
**Primary manuscript:** [`docs/submission/PAPER_A_JFE_MANUSCRIPT.md`](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)  
**Supplement:** [`docs/submission/PAPER_A_JFE_SUPPLEMENT.md`](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)

---

## Executive verdict

**Not ready for submission.** I found **2 P0 submission blockers, 3 P1 major defects, and 2 P2 editorial defects**.

The numerical headline values themselves are substantially better controlled than in Round 8. I found **no stale-number defect** in the current endpoint tables, comparator-loss values, scheme census, corpus count, or standalone Figure 3 caption. The principal failure is instead the one the Round 9 brief asked to attack: **current numbers are being rendered into scientifically false or internally contradictory sentences**.

The two submission blockers are:

1. The manuscript, supplement, conclusion, generated cover letter, and Round 9 brief misdescribe interval geometry and estimand direction. In particular, two intervals that both **contain** zero are said to lie on “the same side of zero”; an interval with upper bound `+0.004 pp` is said to “reach zero at its upper bound”; and an upper bound is described as governing the model's “largest advantage” even though the estimand is model minus comparator and **negative** values favour the model.
2. The abstract and Supplementary Table S3 say the side of zero is numerically unresolved, while the archived audit and the Results section say the 40 g primary/default-loss upper-bound sign is stable across all 20 seeds and about **8.1 Monte Carlo standard errors above zero**.

The new assurance architecture also retains two independently demonstrated false-green paths: the endpoint validator accepts deletion of all endpoint rows, and the resampling-design validator accepts scientifically wrong cluster memberships once their self-hash is refreshed. Those are P1 defects because they undermine the specific source-to-artifact and typed-endpoint assurances claimed in the brief.

### Finding count

| Severity | Count | Submission consequence |
|---|---:|---|
| **P0** | **2** | Must be corrected before submission or external circulation as a submission-ready paper |
| **P1** | **3** | Must be corrected before relying on the new generation/contract system as scientific assurance |
| **P2** | **2** | Should be corrected in the same revision; neither requires numerical recomputation |
| **Total** | **7** | — |

### Findings at a glance

| ID | Finding | Stale number? |
|---|---|---|
| **P0-1** | Generated prose misclassifies interval geometry and reverses bound favourability | **No** — current numbers, wrong semantics |
| **P0-2** | Abstract and supplement contradict the archived Monte Carlo sign-stability audit | **No** — current audit, wrong interpretation |
| **P1-1** | The `±0.0005 pp` Monte Carlo error is applied beyond the 40 g primary/default-loss target actually audited | **No** |
| **P1-2** | The typed endpoint validator silently accepts deleted, empty, or keyless endpoint rows | **No** |
| **P1-3** | Source-to-artifact checking does not independently bind full resampling memberships to the source data | **No** |
| **P2-1** | Active scientific prose still narrates draft/repository history, and the process-language scan excludes the supplement | **No** |
| **P2-2** | Figure 1 and Figure S3 use ambiguous or unexplained categorical colour semantics | **No** |

---

## Scope, method, and execution status

### Scope followed

I followed the brief's exact-commit requirement and reviewed the Round 9 target rather than moving `main`. The review covered:

- the JFE manuscript, canonical draft, supplement, and standalone caption map;
- the endpoint-propagation and comparator-loss artifacts;
- the generated text implementation, front-matter/cover-letter generator, endpoint/resampling contract, artifact checker, consistency checker, and figure source;
- the new S6 and S7 supplementary tables;
- the rendered Figure 1 and Figure S3 images;
- the Round 8 review and remediation plan, to distinguish closed findings from new adjacent defects.

I did **not** re-report the three known open items listed in §6 of the brief, the unresolved metadata listed as out of scope, or Papers B2 and 3.

### Independent checks performed

The review included the following independent checks rather than relying on the brief's assurances:

1. **Interval arithmetic and classification.** I compared the publication prose with the full-precision endpoint and comparator-loss artifacts.
2. **Monte Carlo interpretation.** I calculated the 40 g upper-bound distance from zero as
   `0.0037905184 / 0.0004655904 = 8.14` estimated Monte Carlo standard errors.
3. **Endpoint-contract mutation checks.** I deleted the endpoint rows, replaced them with an empty list, removed the endpoint key from every row, and removed it from the first row only.
4. **Resampling-membership mutation checks.** I moved observations between clusters while preserving the observation set, cluster count, size distribution, and a refreshed self-hash.
5. **Supplement audit.** I checked the S6/S7 numbering, manuscript citations, S7 row count, and membership-table structure.
6. **Figure semantics.** I compared the declared graph and colour rules with the rendered figures.

The focused mutation output is retained separately as `puckworks_round9_mutation_audit.txt` and reproduced in Appendix A.

### Execution limitation

This was an exact-commit static and focused-mutation audit. I did **not** execute the full repository test suite or re-run the expensive PDE producers because a complete executable checkout was not available in the review environment. I therefore do not claim that the repository's advertised commands or full suite pass. The findings below do not depend on a numerical re-solve: they are established from the committed artifacts, publication text, generator logic, and pure contract mutations.

---

## Independent numerical adjudication before the findings

The current publication tables agree with the endpoint artifact on the following rounded values:

| Endpoint | Paired model-minus-comparator difference | Primary full-precision range | Correct zero relation |
|---:|---:|---:|---|
| 38 g | −0.447 pp | approximately `[−0.884387, −0.042433]` | **excludes zero below zero** |
| 40 g | −0.394 pp | `[−0.8290522506, +0.0037905184]` | **contains zero** |
| 42 g | −0.425 pp | approximately `[−0.891251, +0.005844]` | **contains zero** |

For the fitting-loss sensitivity at 40 g:

| Fitting loss | Paired difference | Primary full-precision range | Correct zero relation |
|---|---:|---:|---|
| Primary MAPE-optimal level fit | −0.394 pp | `[−0.8290522506, +0.0037905184]` | **contains zero** |
| Alternative log/relative-error level fit | −0.393 pp | `[−0.8258994487, +0.0043001218]` | **contains zero** |

Thus:

- withdrawing the old claim that the zero-crossing classification changes under fitting loss is correct;
- replacing it with “both lie on the same side of zero” is **not** correct;
- the correct statement is simply that **both ranges contain zero**;
- because the estimand is `model loss − comparator loss`, more-negative values favour the mechanistic model, so **lower bounds are the most favourable bounds** and upper bounds are the least favourable.

The current 40 g Monte Carlo audit records 20 independent seeds at `B = 200,000`, a canonical `B = 1,000,000`, upper bounds from `+0.002230` to `+0.005565 pp`, an upper-bound Monte Carlo standard error of `0.0004656 pp`, and `upper_bound_sign_is_stable = true`. The sign is therefore numerically settled for the audited target even though the range has no calibrated coverage interpretation.

---

# P0 — Submission-blocking findings

## P0-1. Generated prose misclassifies interval geometry and reverses bound favourability

### Finding

Several submission-facing statements are false even though the numbers embedded in them are current. The common cause is that the generators do not represent interval geometry or estimand direction correctly.

The most consequential manifestations are:

1. The endpoint Results paragraph says the alternative fitting loss leaves the primary range “on the same side of zero,” although both primary ranges **straddle/contain zero**. See [manuscript line 889](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L882-L891).
2. The dedicated fitting-loss paragraph says both ranges “lie on the same side of zero.” See [manuscript line 983](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L978-L986).
3. The conclusion says the primary range “reaches zero at its upper bound,” although the full-precision upper bound is `+0.0037905 pp`; zero is **inside** the range, not at its upper bound. See [manuscript line 1221](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1217-L1223).
4. The generated cover letter repeats the same false “reaches zero at its upper bound” formulation. See [`paper_a_front_matter.py` lines 190–196](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_front_matter.py#L190-L196).
5. Supplementary Table S3 says “the largest advantage any upper bound admits” is small. For a model-minus-comparator loss difference, negative values favour the model; the most favourable possible values are governed by the **lower** bounds. The upper bounds are the least favourable ends and, at 40 and 42 g, admit a small model disadvantage. See [supplement line 333](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L327-L334).
6. The fitting-loss paragraph says the loss “moves neither the sign, the magnitude, nor the practical reading” immediately after reporting a point-estimate change from `−0.394` to `−0.393 pp`. The intended claim is evidently “does not materially change,” but the generated absolute wording is literally false.

### Root cause in the generator

The fitting-loss generator defines:

```python
same_side = (
    base["interval"]["contains_zero_full_precision"]
    == alt["interval"]["contains_zero_full_precision"]
)
```

and translates equality of two booleans into “both lie on the same side of zero.” See [`paper_a_transfer_text.py` lines 446–470](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_text.py#L446-L470).

That is a semantic type error. Equal `contains_zero` flags mean only that the two intervals share the same **containment classification**. They do not establish a shared side:

- two intervals that both contain zero produce `True == True`, as here;
- one entirely negative interval and one entirely positive interval both produce `False == False`, which the same code would also misrender as “the same side of zero.”

The supplementary generator separately hard-codes the “largest advantage” to an **upper** bound rather than deriving favourability from the estimand direction. See [`paper_a_transfer_text.py` lines 499–521](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_text.py#L499-L521).

### The Round 9 brief's correction is itself wrong

The brief says that, at `B = 1,000,000`, “both losses put the range on the same side of zero.” That is not what the artifact shows. Both intervals **contain zero**. The artifact's own structured verdict is better: the crossing/containment classification is unchanged. The Round 9 correction therefore overshot in exactly the way the brief asked the reviewer to identify.

### Why this is submission-blocking

These are not stylistic imperfections. They alter the scientific meaning of the principal comparator result in the Results, conclusion, supplement, and cover letter. The errors are systematic and regenerative: hand-editing one occurrence will not close them because the same generator will restore the false wording.

### Minimum acceptance criterion

1. Introduce one shared, full-precision, trinary interval-relation function, for example:

   ```python
   def zero_relation(lower: float, upper: float) -> str:
       if upper < 0:
           return "below_zero"
       if lower > 0:
           return "above_zero"
       return "contains_zero"
   ```

   Exact contact with zero belongs to `contains_zero`; a separate `touches_zero_at_lower/upper` flag may be used only when the corresponding full-precision bound is exactly zero under a declared rule, never because display rounding produced `0.000`.

2. Replace boolean-equality prose with explicit relation-aware rendering:
   - both `contains_zero` → “both ranges contain zero”;
   - both `below_zero` → “both ranges exclude zero on the negative side”;
   - both `above_zero` → “both ranges exclude zero on the positive side”;
   - mixed relations → describe each relation rather than collapsing them.
3. Introduce one estimand-direction contract stating that negative `model − comparator` loss favours the model. Derive:
   - most favourable bound = minimum lower bound;
   - least favourable bound = maximum upper bound.
4. Correct every generated and manually templated surface, including the manuscript, canonical draft, supplement, package/abstract source, conclusion, highlights where relevant, and cover letter.
5. Replace “moves neither the magnitude” with “does not materially change the point estimate or practical reading,” or equivalent quantified wording.
6. Add mutation/parameterized tests for at least:
   - both intervals contain zero;
   - both are negative;
   - both are positive;
   - one contains and one excludes;
   - two excluding intervals on opposite sides;
   - exact contact at the lower and upper bounds;
   - negative-favours-model and positive-favours-model estimands.
7. A repository-wide search must find no active submission-facing instance of the false phrases unless quoted in historical review material.

### Suggested replacement wording

For the fitting-loss result:

> Under the primary and alternative fitting losses, the paired differences were −0.394 and −0.393 pp, respectively, and both primary clustered sensitivity ranges contained zero at the canonical draw count. The fitting loss therefore did not materially change the point estimate, the containment classification, or the practical reading.

For the conclusion/cover letter:

> …a difference of −0.394 percentage points whose primary clustered percentile sensitivity range `[−0.829, +0.004] pp` contained zero.

For the endpoint sweep:

> Across endpoints, the most favourable lower bound was −0.891 pp and the least favourable upper bound was +0.006 pp. Negative values favour the mechanistic model; the ranges are descriptive sensitivity ranges without calibrated coverage.

### Stale-number status

**Not a stale-number finding.** The displayed numbers are current; the generated interpretation is wrong.

---

## P0-2. The abstract and Supplementary Table S3 contradict the archived Monte Carlo sign-stability audit

### Finding

The paper simultaneously makes two incompatible claims about the audited 40 g primary/default-loss upper bound:

- the Results section correctly says its sign is numerically settled, the bound is roughly eight Monte Carlo standard errors from zero, and all 20 seed runs place it above zero; see [manuscript lines 845–851](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L845-L851);
- the abstract says the bound near zero is “unresolved at the precision this resampling attains”; see [abstract line 24](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L20-L25);
- Supplementary Table S3 says the `±0.0005 pp` Monte Carlo error means “which side of zero such a bound lands on is not a resolved quantity”; see [supplement line 333](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L327-L334).

The archived audit records:

- canonical upper bound: `+0.0037905184 pp`;
- upper-bound Monte Carlo SE at `B = 1,000,000`: `0.0004655904 pp`;
- ratio to zero: approximately `8.14` Monte Carlo SE;
- 20-run upper-bound range at `B = 200,000`: `+0.002230` to `+0.005565 pp`;
- `upper_bound_sign_is_stable = true`.

See [`PAPER_A_ENDPOINT_PROPAGATION.json` lines 4309–4365](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json#L4309-L4365).

The sign is therefore numerically resolved for the target actually audited. This does **not** turn the range into a confidence interval, establish statistical superiority, or provide coverage. It means only that the paper must not call the audited 40 g sign numerically unresolved. The canonical 38/40/42 classifications may be reported as endpoint sensitivity, but the 40 g audit cannot by itself certify the Monte Carlo resolution of the unaudited 38 and 42 g bounds.

### Why this is submission-blocking

The contradiction occurs in the abstract and in the supplementary interpretation of a principal result. It also reverses the stated purpose of increasing `B` from 8,000 to 1,000,000. A reader cannot determine whether the endpoint sensitivity is a scientific sensitivity or a numerical artifact when the paper says both.

The front-matter generator only copies the abstract from YAML into each surface; it checks copy consistency, not agreement with the endpoint artifact. See [`paper_a_front_matter.py` lines 96–125](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_front_matter.py#L96-L125). Thus the current generation architecture prevents drift among copies while allowing the same false scientific sentence to be propagated consistently.

### Minimum acceptance criterion

1. Correct the abstract and S3 reading to distinguish:
   - **numerical sign stability** for the audited 40 g primary/default-loss bound;
   - **endpoint sensitivity** of the containment classification across 38/40/42 g;
   - **lack of calibrated coverage/inferential interpretation** for all ranges.
2. Bind the abstract's endpoint sentence and the supplement reading to the structured audit fields, or add a semantic contract that fails when:
   - `upper_bound_sign_is_stable = true`, but active prose says the side/sign is numerically unresolved;
   - `upper_bound_sign_is_stable = false`, but active prose says the sign is settled.
3. Scope the statement explicitly to the audited target; do not imply that the audit covers every endpoint, scheme, or fitting loss unless those audits are added under P1-1.
4. Preserve the non-inferential qualification. The correction must not replace a numerical underclaim with a statistical overclaim.
5. Add a regression test against the current artifact in which the expected phrase is relation-aware and audit-aware, not a magic sentence copied into the test.

### Suggested replacement for the abstract's final sentence

> Propagating the declared ±2 g collection tolerance left the paired difference between −0.447 and −0.394 pp. In the canonical runs the primary range excluded zero at 38 g and contained it at 40 and 42 g; at 40 g, the primary/default-loss upper-bound sign was numerically stable under the Monte Carlo audit. These ranges are not calibrated confidence intervals.

This is longer than the present clause, so the final abstract may need compression elsewhere. A shorter defensible alternative is:

> Across 38–42 g, the difference remained −0.447 to −0.394 pp; the 40 g upper-bound sign was numerically stable, while zero containment changed with endpoint and carried no calibrated inferential meaning.

### Stale-number status

**Not a stale-number finding.** The audit values are current; the abstract and supplement misread them.

---

# P1 — Major findings

## P1-1. The `±0.0005 pp` Monte Carlo error is applied beyond the target actually audited

### Finding

The audit stored in the endpoint artifact is the 40 g, primary `cond_in_variety`, default-loss audit. The manuscript then broadens that result:

- Table 4a states that “the Monte Carlo standard error on **each bound** is ±0.0005 pp” across all three endpoint rows; see [manuscript lines 866–875](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L866-L875).
- Supplementary Table S3 assigns `±0.0005 pp` to “the bounds near zero” while discussing 38, 40, and 42 g collectively; see [supplement lines 327–333](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L327-L333).
- The table generator takes the top-level **upper** MCSE and prints it as the error “on each bound” for every endpoint; see [`paper_a_transfer_text.py` lines 263–284](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_text.py#L263-L284).

Within the audited 40 g target, the lower and upper estimates are `0.0005202` and `0.0004656 pp`, both of which round to `0.0005 pp`; that rounding is not the problem. The problem is **target leakage**: no endpoint-specific audit is stored for 38 or 42 g, no scheme-specific audit is stored for the three secondary schemes, and no multi-seed audit is stored for the alternative fitting loss.

Monte Carlo quantile error depends on the resampling distribution and local tail density. A value audited for one endpoint/loss/scheme cannot simply be treated as a universal property of all related ranges.

### Adjudication of the brief's third-decimal question

For the 40 g primary/default-loss interval, retaining three displayed decimals is defensible **provided the scope and numerical qualification remain explicit**:

- the bound MCSE is about half of one unit in the third decimal;
- the artifact correctly says the third decimal is resolved only to about `±0.001 pp`;
- the exact last displayed digit should not be represented as seed-invariant;
- the sign is nevertheless stable because the upper bound is about 8.1 MCSE above zero.

I therefore do **not** recommend reducing the display to two decimals. That would collapse the informative distinction between a small positive upper bound and exact contact with zero. The correct remedy is scoped precision language, not coarser rounding.

### Minimum acceptance criterion

Choose one of the following defensible paths:

**Path A — scope the existing audit.**

- Table 4a and S3 must state that the stored MCSE applies only to the **40 g primary/default-loss lower and upper bounds**.
- Use the two values separately or state that both round to about `±0.0005 pp`.
- Remove MCSE language from unaudited endpoint/scheme/loss combinations.

**Path B — extend the audits.**

- Store a keyed audit for every combination to which publication prose attaches a numerical MCSE: endpoint, cluster scheme, fitting loss, quantile/bound, `B`, seeds, and RNG/quantile convention.
- The generator must request the exact key and fail if it is absent; it must not fall back to one top-level value.

Under either path:

1. add a mutation test that changes the endpoint, scheme, or loss key while leaving the audit value in place and requires failure;
2. retain “numerical approximation only; no coverage interpretation”;
3. do not use the 40 g audit to support the alternative-loss sign unless an alternative-loss audit is added.

### Stale-number status

**Not a stale-number finding.** The `0.0005 pp` value is valid in its audited scope but is overgeneralized.

---

## P1-2. The typed endpoint validator silently accepts deletion of the endpoint rows

### Finding

The new endpoint contract says it checks both the top-level declaration and row-level representation. Its implementation only enters row validation when all three of the following are already true:

```python
isinstance(rows, list) and rows and ENDPOINT_ROW_KEY in (rows[0] or {})
```

See [`transfer_contract.py` lines 75–118](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/paper_a/transfer_contract.py#L75-L118).

Consequently, the validator returns no problem when:

- the `rows` property is deleted;
- `rows` is an empty list;
- `m_target_g` is removed from every row;
- `m_target_g` is removed from the first row only.

My focused mutation results were:

```text
ENDPOINT CONTRACT MUTATIONS
baseline []
rows_deleted []
rows_empty []
row_keys_deleted_all []
first_row_key_deleted []
```

The artifact checker calls this validator and then iterates over `ep.get("rows") or []`, so missing rows also bypass its downstream per-row checks. See [`paper_a_transfer_artifacts.py` lines 130–185](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_artifacts.py#L130-L185). The routine `verify` endpoint check likewise delegates to this validator. See [`paper_a_consistency.py` lines 321–363](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_consistency.py#L321-L363).

A downstream text generator may crash or produce a mismatch for some of these mutations, but an accidental downstream failure is not a substitute for the typed schema contract that claims to require the rows. At least two named assurance layers can return a false green in isolation.

### Why this is major

The endpoint rows are the actual realization of the 38/40/42 g science. A contract that validates the declared targets while allowing the result rows to disappear has not established the central claim it is named for. This is directly responsive to the brief's question: “which assertions would pass unchanged if the thing it names were deleted?”

### Minimum acceptance criterion

`validate_endpoint_contract()` must require all of the following:

1. `rows` exists and is a list;
2. `len(rows) == 3` for the current exact target contract;
3. every row is a dictionary;
4. every row contains a finite numeric `m_target_g`;
5. the rows contain exactly one each of `38.0`, `40.0`, and `42.0`, with no duplicates, missing values, or extras;
6. every row is free of all retired endpoint keys, regardless of whether the first row is well formed;
7. malformed row types produce validation problems rather than exceptions.

Required mutation tests must cover at least:

- missing `rows`;
- `rows = []`;
- one missing endpoint row;
- duplicate endpoint row;
- extra endpoint row;
- key removed from first, middle, and last row;
- retired key inserted into any row;
- non-finite target and non-dictionary row.

The artifact checker and routine `verify` command must both report these defects explicitly.

### Stale-number status

**Not a stale-number finding.** This is a schema-presence false green.

---

## P1-3. The source-to-artifact checker does not independently bind full resampling memberships to the source data

### Finding

The Round 9 brief says the source-to-artifact layer reconstructs “counts, IDs, cluster membership and hashes from the CSV,” and treats a closed-loop/self-certifying design as P1. The implementation does not perform the claimed full membership comparison.

The internal design validator checks:

- that every scheme covers the same observation set;
- observation count and uniqueness;
- `n_clusters == len(membership)`;
- the membership's stored hash equals a hash of the membership itself.

See [`transfer_contract.py` lines 595–623](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/paper_a/transfer_contract.py#L595-L623).

The artifact checker contains a comment saying membership must match a design rebuilt from the source, but the code that follows checks only hard-coded cluster counts for all schemes and the primary scheme's size distribution. It never compares the complete source-derived observation-to-cluster mapping. See [`paper_a_transfer_artifacts.py` lines 150–174](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_artifacts.py#L150-L174).

I demonstrated two false greens while preserving counts, coverage, size distribution, and refreshing the self-hash:

1. In `sample_in_variety_grind`, I swapped the `5CQA` observations between samples A12 and A13 while leaving their caffeine and trigonelline observations in place. This violates the declared “one sample record carrying its three co-measured solutes” scheme. The validator returned `[]`.
2. In primary `cond_in_variety`, I swapped `A19|5CQA` and `A20|5CQA`, placing those observations under the wrong temperature/pressure condition clusters. The validator returned `[]`.

The focused output was:

```text
MUTATED SAMPLE MEMBERSHIP
A12 observations: ['A12|caffeine', 'A12|trigonelline', 'A13|5CQA']
A13 observations: ['A12|5CQA', 'A13|caffeine', 'A13|trigonelline']
validator: []

MUTATED PRIMARY MEMBERSHIP
swap: A19|5CQA <-> A20|5CQA
validator: []
```

These mutations are scientifically material: clustered percentile ranges depend on which outcomes move together. A wrong partition can change the range while satisfying every current check.

### Why this is major

The primary new assurance claim is not merely that the artifact is internally well formed; it is that its resampling design is bound to the source corpus. A self-hash proves only that the artifact has not changed without updating its hash. It does not prove the partition is scientifically correct.

### Minimum acceptance criterion

1. Build a **genuinely source-derived membership oracle** for every declared scheme directly from the CSV's record fields and the scheme specification.
2. Do not use the artifact membership as an input to the oracle. Preferably, do not call the same production grouping function that generated the artifact; otherwise a shared grouping bug can certify itself.
3. Canonicalize and compare, for every scheme:
   - role;
   - strata fields and realized stratum values;
   - cluster-key fields and realized cluster IDs;
   - exact sorted observation IDs in every cluster;
   - number of clusters and strata;
   - cluster-size distribution;
   - complete observation set.
4. Derive counts and size distributions from the exact source mapping rather than treating hard-coded census values as the primary oracle.
5. Add mutations that preserve all aggregate counts and refresh hashes but alter:
   - one observation's cluster;
   - one cluster's stratum;
   - one cluster key;
   - one co-measured-solute grouping;
   - a C/F condition pairing in the primary scheme.
6. Every mutation above must fail `paper_a_transfer_artifacts.py --check` with a message identifying the scheme and mismatched membership.

### Stale-number status

**Not a stale-number finding.** This is a scientific partition-provenance false green.

---

# P2 — Editorial and presentation findings

## P2-1. Active scientific prose still narrates draft/repository history, and the process-language scan excludes the supplement

### Finding

The brief specifically asks for any place where a journal reader is made to read the repository's changelog. Several such passages remain in active scientific exposition:

- “An earlier draft promised one…” in the dimensional-audit discussion; see [manuscript lines 700–706](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L700-L706).
- Internal repository paths to `docs/paper1_resource/PAPER_A_OBJECTIVE_FAMILY_PANELS.json` and `PAPER_A_P0-5_RESULTS.md` inside the Results narrative; see [manuscript lines 744–755](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L744-L755).
- “already in the repo as…” in the external-data description; see [manuscript lines 1072–1079](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1072-L1079).
- “(round-7 P1-4)” in the Supplementary Table S5 interpretation; see [supplement lines 417–420](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L417-L420).
- “Generated from the archived design object, so the Methods paragraph and this table cannot disagree” in the visible S6 caption; see [supplement lines 435–440](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L435-L440).

I did not report hidden generation comments or the designated working-draft review-history material that the brief explicitly places out of scope. The examples above are in reader-facing analysis, Results, or supplement prose.

The checker declares `SUPPLEMENT` but omits it from `SUBMISSION_FILES`, despite describing that tuple as “Every file a reviewer or editor could receive.” See [`paper_a_consistency.py` lines 54–65](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_consistency.py#L54-L65). Its process patterns also cover selected ticket forms but not phrases such as “earlier draft,” `round-7`, “already in the repo,” or internal `docs/` paths. See [`paper_a_consistency.py` lines 135–143](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_consistency.py#L135-L143) and [lines 213–224](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_consistency.py#L213-L224).

### Minimum acceptance criterion

1. Rewrite the passages as scientific statements:
   - explain directly why no intersection is reported, without narrating an earlier draft;
   - point readers to a numbered supplementary table or deposited data DOI, not an internal working path;
   - cite Waszkiewicz conventionally without “already in the repo”;
   - remove review-ticket identifiers;
   - state the S6 scientific contract directly without generator self-praise.
2. Add the supplement and separately supplied caption file to the process-language scan.
3. Scan visible text after stripping HTML comments, with an allowlist for legitimate paths in the Data/Code Availability section.
4. Add checks for at least `earlier draft`, `round-\d+`, `already in (the )?repo`, internal review-ticket forms, and back-ticked `docs/` paths outside the allowlisted availability section.

### Stale-number status

**Not a stale-number finding.** This is publication-facing process leakage.

---

## P2-2. Figure 1 and Figure S3 use ambiguous or unexplained categorical colour semantics

### Finding

The repaired Figure 1 dependency geometry is scientifically correct, but its legend assigns the same blue border to two separately named categories:

- `in-sample localization` → `GOOD` blue;
- `within-campaign holdout` → `GOOD` blue.

See [`figures_paper_a.py` lines 235–243](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/figures_paper_a.py#L235-L243) and the [rendered Figure 1](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/figures/paper_a/fig1_design.png). Two distinct legend entries with identical encoding are not decodable from the legend itself.

Figure S3 panel (b) applies an undocumented three-colour rule:

- blue when `r > 0.4`;
- orange when `r < 0`;
- grey otherwise.

See [`figures_paper_a.py` lines 732–743](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/figures_paper_a.py#L732-L743) and the [rendered Figure S3](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/figures/fig7_per_group_diagnostics.png). Neither the panel nor its standalone caption states the thresholds or explains that they are descriptive display choices rather than significance classes. The caption correctly says the correlations are descriptive, but a reader still cannot decode why a bar is blue, grey, or orange.

### Minimum acceptance criterion

1. For Figure 1, either:
   - give every separately listed evidence category a unique visual encoding; or
   - intentionally collapse the two blue entries into one category and explain the shared meaning.
2. Add a test that separate legend categories do not accidentally share an identical encoding unless explicitly declared as aliases.
3. For Figure S3, either:
   - use a single neutral colour and let signed bar length carry the information; or
   - add a legend/caption note specifying the exact thresholds and that they are descriptive, not inferential or significance thresholds.
4. Re-render at the intended publication size and inspect both colour and monochrome/grayscale legibility.

### Stale-number status

**Not a stale-number finding.** This concerns visual semantic encoding.

---

# Requested Round 9 adjudications: checked and clean or materially improved

The brief requires an explicit statement when a section was checked and produced no finding. The following items were checked.

## A. Generated numerical values and stale-number risk

**Checked and clean.** I found no stale endpoint/comparator values in the manuscript or supplement. The following agree across current publication surfaces and artifacts:

- complete held-out corpus: 44 records and 132 observations;
- pooled MAPE: 8.44% model versus 8.83% comparator at 40 g;
- paired difference: −0.394 pp;
- model worse on 62 of 132 observations;
- 38/40/42 g point differences and primary intervals;
- primary/default and alternative-loss point estimates and intervals;
- four-scheme 40 g census and range widths;
- 20-seed audit values at their actual 40 g primary/default-loss scope.

The defects are semantic and contractual, not stale numerical copies.

## B. Multi-seed audit design and third-decimal display

**Checked and acceptable within its actual scope.** Twenty independent `B = 200,000` runs, with the between-seed SD scaled by `sqrt(200,000 / 1,000,000)`, are a reasonable direct audit of Monte Carlo quantile approximation at canonical `B = 1,000,000`. Twenty runs leave ordinary uncertainty in the estimated SD, but not enough to make a roughly 8.1-SE positive bound a knife-edge.

Three-decimal reporting is defensible when accompanied by the explicit `≈ ±0.001 pp` numerical-resolution caveat. The paper must not imply that the last digit is seed-invariant, but reducing the intervals to two decimals would obscure rather than improve the near-zero geometry.

The audit measures Monte Carlo approximation only. The manuscript is correct not to assign coverage, confidence, equivalence, superiority, or non-superiority to these ranges.

## C. Withdrawal of the fitting-loss zero-crossing claim

**Substantive withdrawal checked and correct; replacement wording is not.** Both current loss-specific ranges contain zero, so the former claim that fitting loss changes the zero-containment classification should be withdrawn. The correct replacement is “both contain zero,” not “both lie on the same side of zero.” This distinction is captured in P0-1.

## D. Retention and framing of `cond_in_variety` as primary

**Checked and acceptable.** The manuscript now:

- identifies `cond_in_variety` as pre-declared rather than selected after seeing the bounds;
- calls it a conservative dependence assumption, not the uniquely identified experimental unit;
- explicitly acknowledges that C and F are separate espresso sample records;
- reports the design-aligned `sample_in_variety_grind` scheme prominently;
- reports all four schemes on the same 132 observations;
- states that the primary scheme was retained for design rationale rather than its relation to zero;
- correctly reports that the whole-group range is slightly wider than the primary range.

This is an honest sensitivity hierarchy. Reporting a primary scheme does not, by itself, smuggle in post hoc selection when the rationale and all secondary outcomes are visible. The new membership-provenance defect in P1-3 concerns assurance implementation, not the scientific framing of the declared schemes.

## E. Supplementary Table S6

**Scientific content checked and clean, apart from the process-language sentence in P2-1.** The table lists four schemes, roles, strata, cluster keys, cluster counts, size distributions, 40 g ranges, and widths. The census is internally consistent:

- `cond_in_variety`: 26 clusters, `3×8` and `6×18`;
- `sample_in_variety_grind`: 44 clusters, `3×44`;
- `cond_in_group`: 78 clusters, `1×24` and `2×54`;
- `group`: 6 clusters, `22×6`.

The table correctly shows the whole-group width (`0.839 pp`) as slightly wider than the primary width (`0.833 pp`).

## F. Supplementary Table S7

**Checked and clean at source level.** S7:

- is sequentially numbered after S6;
- is cited in the manuscript;
- contains 44 sample rows;
- separates variety, grind, temperature, pressure, on-grid status, lookup status, and primary cluster;
- reconciles to 132 named-solute observations and eight off-grid records.

An eight-column, 44-row table is legible as structured Markdown. Final journal-width legibility cannot be established until the typeset/PDF form exists, so a final landscape/continued-header proof remains prudent, but I found no current numbering, citation, or membership-table defect.

## G. Figure 1 dependency semantics

**Checked and materially corrected.** The declared graph now makes LOCO and cross-grind holdout parallel children of Angeloni recalibration, keeps the external Waszkiewicz branch independent of Angeloni recalibration, and represents Table 7 as a lateral comparison rather than a fitted dependency. See [`FIG1_NODES`, `FIG1_EDGES`, and `FIG1_LATERAL`](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/figures_paper_a.py#L153-L204). I found no remaining dependency-arrow error. P2-2 is limited to legend encoding.

## H. Figure S3 layout and scientific labels

**Title-collision remediation checked and closed.** The rendered title/panel-title collision reported in Round 8 is no longer present. NA baseline handling and “better/worse” arrows in panel (a) are legible. The only current issue is the unexplained colour classification in panel (b), reported as P2-2.

## I. Prior Round 8 blockers

| Round 8 item | Round 9 status |
|---|---|
| P0-1 standalone Figure 3 caption used 108-point tuple | **Closed.** Caption now distinguishes 132-point primary from 108-point matched-grid secondary. |
| P0-2 Methods declared two schemes and wrong primary | **Closed.** Four schemes and `cond_in_variety` primary are stated correctly. |
| P0-3 retired mL endpoint and release-only check | **Substantively closed.** Typed collected-mass schema runs in `verify`; P1-2 is a new row-presence defect, not a return to mL. |
| P1-1 dependence unit/census/width framing | **Closed.** Separate C/F samples and all four censuses are stated; whole-group width corrected. |
| P1-2 rounding-controlled knife-edge | **Numerical remediation closed.** Full-precision flags and high-`B` audit are present; P0-2/P1-1 concern new prose/scope errors introduced around that audit. |
| P1-3 interval contract did not inspect primary interval | **Architecture improved.** Generated blocks bind current values; P0-1 shows that exact-block equality still does not test meaning. |
| P1-4 corpus manifest not bound/published | **Closed for corpus identity and S7 publication.** P1-3 is narrower: exact resampling partition membership is not independently source-bound. |
| P1-5 Figure 1 serialized parallel analyses | **Closed.** Graph semantics are now correct. |
| P2-1 slow-lane count | **Not re-reported.** The Round 9 brief explains the corrected populations. |
| P2-2 Figure S3 title collision | **Closed.** |

## J. Known-open and explicitly out-of-scope items

**Not reported as findings.** I did not re-report:

- the unrun fraction-versus-measured-cup rate-profile contrast;
- the enumerated unbound slow-lane values;
- hand-single-sourced design settings;
- missing author/affiliation/ORCID/CRediT/funding/interest/AI metadata;
- novelty search, release DOI, archival tag, or working-draft review-history block;
- the settled Reynolds definition or collected-mass interpretation;
- Papers B2 and 3.

---

# Ordered acceptance checklist

## Gate 1 — Correct the submission-blocking scientific prose

- [ ] Replace all “same side of zero” claims with exact trinary interval relations.
- [ ] Replace “reaches zero at its upper bound” wherever the full-precision upper bound is positive.
- [ ] Correct upper/lower favourability using the declared `model − comparator` estimand direction.
- [ ] Change absolute “moves neither magnitude” wording to quantified/material wording.
- [ ] Correct the abstract and S3 numerical-resolution claims.
- [ ] Regenerate manuscript, draft, supplement, package/front matter, and cover letter.
- [ ] Search all active submission-facing files for the retired false phrases.

## Gate 2 — Scope or extend the Monte Carlo audit

- [ ] State explicitly that the existing audit is 40 g, primary `cond_in_variety`, default loss.
- [ ] Render lower and upper MCSEs from the correct audit key.
- [ ] Remove universal “each bound” wording unless all bound/endpoint combinations are audited.
- [ ] Add keyed audit lookup and missing-key mutation tests.
- [ ] Retain three decimals with the `≈ ±0.001 pp` qualification and no coverage claim.

## Gate 3 — Close the endpoint schema deletion hole

- [ ] Require exactly three valid endpoint rows.
- [ ] Reject missing, empty, duplicate, extra, keyless, non-finite, and malformed rows.
- [ ] Reject retired keys in every row.
- [ ] Demonstrate that both artifact checking and routine `verify` fail every row mutation.

## Gate 4 — Make resampling membership genuinely source-bound

- [ ] Reconstruct exact membership for all four schemes from source fields.
- [ ] Compare every cluster's stratum, key, and observation list.
- [ ] Derive census values from the exact source oracle.
- [ ] Add same-count/same-size/refreshed-hash wrong-membership mutations.
- [ ] Require `paper_a_transfer_artifacts.py --check` to identify the altered scheme.

## Gate 5 — Remove publication-process leakage and repair figure semantics

- [ ] Remove active “earlier draft,” review-ticket, repository-path, and “already in repo” prose.
- [ ] Include supplement and standalone captions in the process-language scan.
- [ ] Give Figure 1 legend categories unique or explicitly aliased encodings.
- [ ] Explain or remove Figure S3's `r > 0.4` / `r < 0` colour thresholds.
- [ ] Inspect final-size colour and grayscale renders.

## Gate 6 — Final verification

After the changes, retain the outputs of at least:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_consistency.py verify
python -m pytest tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_model_contract.py \
                 tests/test_paper_a_figure_semantics.py -q
python -m pytest -q
```

Add the new semantic and mutation tests to the targeted command. A full PDE recomputation is not required merely to correct these prose and contract defects, provided the numerical producer is unchanged; it remains appropriate as a final retained reproduction if the scientific producer or artifact schema is modified.

---

# Appendix A — Independent focused mutation audit

```text
ENDPOINT CONTRACT MUTATIONS
baseline []
rows_deleted []
rows_empty []
row_keys_deleted_all []
first_row_key_deleted []

BASELINE DESIGN VALIDATION []
scheme census
cond_in_variety 26 {'3': 8, '6': 18} 2 af9c759cd4dba09261d190f1ffc2a534b1a1e232f05639a6764cf664fde3b87b
sample_in_variety_grind 44 {'3': 44} 4 9cfc1167a6632073fe783b948b1075717e6840eea1c1e9b1b8cba527c7cbe94f
cond_in_group 78 {'1': 24, '2': 54} 6 2dfcafd7a929e7f4a1e734276deaf149a4f40f5a38dda76264d631b7c546954d
group 6 {'22': 6} 1 3783889eb520cb2b18b78b34b52e195f9c434575b2a8467cdbccaa703a8b343c

MUTATED SAMPLE MEMBERSHIP
A12 observations: ['A12|caffeine', 'A12|trigonelline', 'A13|5CQA']
A13 observations: ['A12|5CQA', 'A13|caffeine', 'A13|trigonelline']
validator: []

MUTATED PRIMARY MEMBERSHIP
swap: A19|5CQA <-> A20|5CQA
validator: []

SOURCE MANIFEST
n_train_records 18
n_held_out_records 44
n_observations 132
n_off_grid_records 8
n_lookup_observations 108
manifest_sha256 fe46b65becbd5c421e929de3c4847eba0630e82bf08cc0c6856718cdd55907f8
```

---

# Appendix B — Suggested semantic helper contract

A minimal implementation should separate four concepts that are currently conflated:

```python
from dataclasses import dataclass
from enum import Enum

class ZeroRelation(str, Enum):
    BELOW = "below_zero"
    CONTAINS = "contains_zero"
    ABOVE = "above_zero"

@dataclass(frozen=True)
class IntervalSemantics:
    lower: float
    upper: float
    relation: ZeroRelation
    touches_lower: bool
    touches_upper: bool


def interval_semantics(lower: float, upper: float) -> IntervalSemantics:
    if not (lower <= upper):
        raise ValueError("interval lower bound exceeds upper bound")
    if upper < 0.0:
        relation = ZeroRelation.BELOW
    elif lower > 0.0:
        relation = ZeroRelation.ABOVE
    else:
        relation = ZeroRelation.CONTAINS
    return IntervalSemantics(
        lower=lower,
        upper=upper,
        relation=relation,
        touches_lower=(lower == 0.0),
        touches_upper=(upper == 0.0),
    )
```

A separate estimand contract should state which direction is favourable:

```python
@dataclass(frozen=True)
class EstimandDirection:
    label: str
    negative_favours_model: bool


def favourable_extremes(intervals, direction: EstimandDirection):
    lowers = [i.lower for i in intervals]
    uppers = [i.upper for i in intervals]
    if direction.negative_favours_model:
        return min(lowers), max(uppers)  # most favourable, least favourable
    return max(uppers), min(lowers)
```

The important design point is not the exact class structure. It is that **containment, side, boundary contact, and favourability must be represented as different typed facts**. A single boolean cannot safely render all four.

---

# Appendix C — Principal evidence index

- [Round 9 brief](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_9.md)
- [Primary manuscript](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)
- [Supplement](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)
- [Endpoint artifact](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json)
- [Comparator-loss artifact](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/paper1_resource/PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json)
- [Transfer text generator](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_text.py)
- [Front-matter and cover-letter generator](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_front_matter.py)
- [Endpoint/resampling contract](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/paper_a/transfer_contract.py)
- [Source-to-artifact checker](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_transfer_artifacts.py)
- [Submission consistency checker](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/tools/paper_a_consistency.py)
- [Figure source](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/puckworks/figures_paper_a.py)
- [Rendered Figure 1](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/figures/paper_a/fig1_design.png)
- [Rendered Figure S3](https://github.com/trbrewer/puckworks/blob/45e753a5f37ede66cd99a016a6b8902fdbadebdf/docs/submission/figures/fig7_per_group_diagnostics.png)

---

## Final recommendation

Do not submit the current snapshot. Correct P0-1 and P0-2 at the generator/source level, not by hand in individual publication files. Then close the three P1 assurance defects before presenting the Round 9 generation architecture as proof that source, artifact, and prose are scientifically bound. No numerical re-solve appears necessary for the identified corrections unless implementation changes alter the producers; the current numerical artifacts can remain the source of truth while their semantics and validation are repaired.
