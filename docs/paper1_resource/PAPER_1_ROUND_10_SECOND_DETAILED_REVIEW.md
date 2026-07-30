# Paper 1 — Detailed Review, Round 10

**Review date:** 30 July 2026  
**Review target:** commit [`3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5`](https://github.com/trbrewer/puckworks/tree/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5) on `main`  
**Governing brief:** [`PAPER_1_REVIEW_BRIEF_ROUND_10.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_10.md)  
**Primary manuscript:** [`docs/submission/PAPER_A_JFE_MANUSCRIPT.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)  
**Supplement:** [`docs/submission/PAPER_A_JFE_SUPPLEMENT.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)

---

## Executive verdict

**Not ready for submission on the scientific wording alone.** I found **1 P0 submission blocker, 2 P1 major assurance defects, and 3 P2 minor/editorial or assurance-hardening defects**.

The Round 10 remediation is nevertheless a substantial improvement over Round 9. The trinary interval semantics, exact audit key, separate lower/upper Monte Carlo errors, source-derived grouping oracle, expanded process-language scan, and corrected figures all address real defects. I found **no stale headline number** and no recurrence of the Round 9 statements that two zero-containing ranges were on the same side of zero, that a positive upper bound “reached” zero, or that an upper bound represented the model’s greatest advantage.

The remaining blocker is a new interpretive overreach created around otherwise current values. The abstract, Results, endpoint reading, supplement, editor-significance statement, and generated cover letter conclude that the benchmark shows **“no resolvable skill”** or is **“unresolved throughout the declared tolerance.”** No operational definition of *resolvable* is supplied. At the same time, the manuscript and archived artifact explicitly state that these are fixed-predictor sensitivity ranges without calibrated coverage and that neither crossing nor non-crossing zero is evidence of superiority or non-superiority. The paper may conclude that the evidence **does not establish transferable mechanistic skill**. It cannot, without a declared practical or inferential decision criterion, convert that absence of establishment into a positive finding of **no resolvable skill**.

This distinction matters because the observed result is not numerically null: the mechanistic predictor has lower pooled MAPE at all three endpoints; the primary range is wholly negative at 38 g; and all three secondary-scheme ranges are wholly negative at 38, 40, and 42 g. Those facts do not establish calibrated superiority, but they also prevent an unqualified global “unresolved” verdict from following automatically from the ranges.

### Finding count

| Severity | Count | Consequence |
|---|---:|---|
| **P0** | **1** | Central submission-facing conclusion must be corrected or operationally justified |
| **P1** | **2** | Correct before relying on the new semantics/oracle architecture as the claimed assurance chain |
| **P2** | **3** | Correct in the same revision; no scientific recomputation is required |
| **Total** | **6** | — |

### Findings at a glance

| ID | Finding | Stale number? |
|---|---|---|
| **P0-1** | “No resolvable skill” is not licensed by a declared criterion and conflicts with the paper’s own no-inference rule | **No** — current numbers, unsupported verdict |
| **P1-1** | A central renderer still derives zero geometry from the archived Boolean rather than the typed semantics layer | **No** |
| **P1-2** | The independent oracle rebuilds grouping but hard-codes the three-observation universe; its “exact” comparison also omits declared metadata | **No** |
| **P2-1** | Table S6 says it contains membership for every scheme although it contains only scheme definitions and census summaries | **No** |
| **P2-2** | Table S6’s audit prose says “The bound’s sign” after discussing both bounds; the flag concerns the upper bound only | **No** |
| **P2-3** | Adjacent validation/lookup entry points can raise implementation exceptions on malformed or non-finite input rather than returning named failures | **No** |

---

## Scope, method, and execution status

### Scope followed

I reviewed the exact commit required by the brief rather than a moving `main` branch. The review covered:

- the JFE manuscript, supplement, front-matter source, generated cover-letter logic, and standalone caption map;
- the endpoint-propagation artifact and its full-precision interval and audit records;
- `transfer_semantics.py`, `transfer_contract.py`, `source_resampling_oracle.py`, `paper_a_transfer_text.py`, and relevant consistency/test sources;
- the source `bioactives.csv` structure used to define the held-out corpus;
- Supplementary Tables S3, S6, and S7;
- rendered Figure 1 and Figure S3;
- the Round 9 review and Round 10 brief, to distinguish closed findings from adjacent regressions.

I did **not** re-report the out-of-scope metadata, the three explicitly known open items, Papers B2/3, or the settled Reynolds/flow/end-point questions. I found no new evidence that required reopening those settled items.

### Independent checks performed

1. **Full-precision numerical reconciliation.** Publication values were compared against the endpoint artifact, including all three endpoints, all four resampling schemes at 40 g, and the exact Monte Carlo audit target.
2. **Rendered-prose audit.** Generated sentences were read against the meaning of the artifact rather than merely checked for matching numerals or approved phrases.
3. **Semantics-path audit.** Renderer source was inspected for local geometry/favourability inference that bypasses `transfer_semantics.py`.
4. **Oracle common-mode audit.** The source parser, observation-ID construction, cluster reconstruction, exact comparison, corpus manifest, and validator were inspected as two implementations that may still share assumptions.
5. **Focused mutation tests.** I executed standalone mutations against the exact Round 10 modules. These included removing all three scored-solute columns from the CSV, altering archived `grinds`, altering census scalars, replacing canonical solute labels while refreshing the manifest hash, and supplying non-finite/malformed validator inputs.
6. **Supplement structure audit.** Table S7 was parsed as 44 data rows and eight columns; S6/S7 captions and actual columns were compared.
7. **Figure semantics audit.** Figure 1’s dependency graph and categorical encodings, and Figure S3’s neutral correlation encoding and zero line, were checked visually.
8. **Process-language scan.** Visible manuscript and supplement text was searched for the Round 10 retired process phrases, excluding the brief’s expressly permitted metadata/availability contexts.

### Execution limitation

This was an exact-commit static, artifact-reconciliation, and focused-mutation audit. A complete executable repository checkout was not available in the review environment, so I did **not** claim to have run the advertised full `pytest` suite, the complete consistency command chain, or the approximately 25-minute PDE regeneration. The findings below do not depend on a re-solve: they are established from committed artifacts, publication text, generator logic, and pure validation/oracle mutations. The current numerical values were adjudicated against the committed artifact rather than independently re-solved from the PDE model.

---

## Independent numerical adjudication

The principal publication values agree with the committed endpoint artifact:

| Endpoint | Model MAPE | Comparator MAPE | Model − comparator | Primary full-precision range | Correct zero relation | Model worse on |
|---:|---:|---:|---:|---|---|---:|
| 38 g | 8.39% | 8.83% | −0.447 pp | `[−0.8843868833, −0.0424325436]` | excludes zero below zero | 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | `[−0.8290522506, +0.0037905184]` | contains zero | 62/132 |
| 42 g | 8.41% | 8.83% | −0.425 pp | `[−0.8912505494, +0.0058444686]` | contains zero | 60/132 |

At 40 g, the three declared secondary sensitivity ranges are also current:

| Scheme | Full-precision range | Zero relation |
|---|---|---|
| `sample_in_variety_grind` | `[−0.7424227544, −0.0530514529]` | excludes zero below zero |
| `cond_in_group` | `[−0.7402068662, −0.0386665772]` | excludes zero below zero |
| `group` | `[−0.8634184737, −0.0244927331]` | excludes zero below zero |

The exact audit is correctly scoped to **40 g + `cond_in_variety` + primary fitting loss**. It records 20 seeds at `B = 200,000`, canonical `B = 1,000,000`, lower-bound Monte Carlo SE `0.0005201594 pp`, upper-bound Monte Carlo SE `0.0004655904 pp`, and stable positive upper-bound sign across seeds. The third displayed decimal is therefore accompanied by an honest numerical-resolution caveat; this audit supplies no coverage interpretation.

### Stale-number category

**Checked and empty.** I found no stale-number regression in:

- 8.44% / 8.83%;
- −0.394 pp;
- 62/132;
- the 38/40/42 g primary ranges;
- the three 40 g secondary ranges;
- the 0.000520 / 0.000466 pp audit errors;
- the 44-record / 132-observation corpus count;
- the 26/44/78/6 cluster census;
- the fitting-loss comparison quoted in the manuscript.

---

# P0 — Submission-blocking finding

## P0-1. The central “no resolvable skill” verdict has no declared resolving criterion and contradicts the paper’s own inferential discipline

### Finding

The same conclusion is propagated across multiple submission-facing surfaces:

- the abstract says the comparison shows “no resolvable skill beyond a transferred level” ([manuscript line 24](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L20-L25));
- the principal quantitative Results paragraph says acceptable endpoint accuracy “did not supply resolvable skill” ([lines 803–807](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L803-L807));
- the endpoint reading states “No row supports a claim of resolvable skill” and calls the benchmark “unresolved throughout the declared tolerance” ([lines 884–894](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L884-L894));
- Supplementary Table S3 reaches the same global verdict ([supplement lines 327–335](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L327-L335));
- the front-matter source says the model adds “no resolvable skill” in both the abstract and editor-significance statement ([YAML lines 44–64 and 85–94](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/paper_a_front_matter.yaml#L44-L64));
- the generated cover-letter logic states that the endpoint result “did not establish resolvable mechanistic skill” ([`paper_a_front_matter.py` lines 189–198](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_front_matter.py#L189-L198));
- the standalone caption map labels Figure 3 as the finding of “no resolvable gain” ([caption-map lines 6–15](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/figures/PAPER_A_CAPTIONS.md#L6-L15)).

No numerical, practical, decision-theoretic, or calibrated inferential criterion defining *resolvable* is given. The text instead argues from three observations:

1. the point difference is small in absolute percentage points;
2. the model is worse on roughly half of individual observations;
3. the primary sensitivity range contains zero at 40 and 42 g.

Those observations support a cautious description of a **small and uneven observed advantage**. They do not by themselves define a boundary between resolved and unresolved skill.

### Internal contradiction

The manuscript correctly states that these ranges are not calibrated confidence intervals and explicitly makes **no claim of distinguishability, non-distinguishability, or equivalence** ([manuscript lines 845–857](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L845-L857)). The artifact is even clearer: neither crossing nor non-crossing zero is evidence of statistical superiority or non-superiority ([endpoint artifact lines 4376–4394](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json#L4376-L4394)).

The global “unresolved” verdict nevertheless treats the range geometry as if it supported a no-skill conclusion. That is the same inferential move under softer wording:

- when the primary range contains zero at 40/42 g, the paper reads this as conceding no advantage;
- when the primary range is wholly negative at 38 g, and when every secondary range is wholly negative at all three endpoints, the paper says those outcomes are non-inferential and therefore do not support skill;
- it then combines these asymmetric readings into “unresolved throughout.”

The paper is correct that the wholly negative ranges do **not** establish calibrated superiority. But by the paper’s own rule, the zero-containing ranges also do **not** establish non-superiority. A criterion-free analysis cannot use one side of that symmetry to carry the conclusion and dismiss the other.

### Why comparison with the 8.4% arm errors does not close the gap

The endpoint reading emphasizes that the possible model advantage is below one percentage point while each arm’s MAPE is about 8.4%. This is descriptive context, not a materiality rule. A `0.394 pp` absolute reduction from `8.83%` to `8.44%` is about a **4.5% relative reduction in MAPE**; the artifact itself reports `skill_vs_const = 0.045` at 40 g. Whether that is trivial, useful, or practically material depends on the intended decision, measurement precision, cost, and application. None is converted into a pre-declared margin.

Likewise, “model worse on 62 of 132” is valuable and should remain, but it does not negate a lower pooled loss: magnitude and sign frequency answer different questions. A predictor can improve the mean through fewer but larger improvements while losing marginally on more cases. Calling the aggregate gain unresolvable requires a stated rule for weighing those facts.

### Scientifically defensible conclusion available from the current evidence

The current evidence supports a strong but different conclusion:

> The mechanistic model showed a small observed pooled-error advantage over the trained level-only comparator, but the fixed-predictor sensitivity analyses and available measurement information do not provide a calibrated basis for a claim of statistical superiority, equivalence, or practical materiality. Acceptable held-out endpoint error therefore does not establish transferable mechanistic skill.

That preserves the paper’s central thesis. It distinguishes **failure to establish mechanism transfer** from **establishing an absence of predictive skill**.

### Why this is P0

This is not local wording. It is the declared principal quantitative result and is repeated in the abstract, Results, supplement, editor significance, cover letter, and caption map. It changes the scientific proposition presented to the editor and reader. The current values can remain; the conclusion drawn from them must be corrected before submission.

### Minimum acceptance criterion

Choose and implement one of the following paths consistently across every generated and manual surface.

#### Path A — criterion-free descriptive conclusion

1. Remove or replace all unqualified forms of:
   - “no resolvable skill”;
   - “no resolvable gain”;
   - “unresolved throughout the declared tolerance”;
   - “adding no resolvable skill.”
2. State the observed result directly: model and comparator errors, paired difference, model-worse count, and sensitivity ranges.
3. Use the epistemically correct conclusion: the analysis **does not establish** transferable mechanistic skill, calibrated superiority, equivalence, or practical materiality.
4. Preserve the distinction between:
   - small observed incremental performance;
   - mechanism transfer;
   - inferential evidence;
   - practical relevance.

#### Path B — operationalize “resolvable”

1. Define a pre-specified practical relevance/equivalence margin or a calibrated inferential procedure.
2. Justify it from measurement uncertainty, use-case consequences, or an external decision standard rather than from the observed result.
3. Apply it symmetrically to every endpoint/scheme being summarized.
4. Report the conclusion using the procedure’s actual scope and limitations.

Under either path:

- update `paper_a_front_matter.yaml`, `paper_a_transfer_text.py`, the caption-map state label, and any generated cover/package surfaces;
- regenerate all derived files;
- add a semantic test preventing uncalibrated sensitivity ranges from being rendered as proof of superiority, non-superiority, equivalence, or absence of skill without a declared decision rule;
- do not replace the current wording with “not statistically significant,” “equivalent,” or “no difference,” because none is established by the present procedure.

### Stale-number status

**Not a stale-number finding.** The numerical inputs are current; the central verdict is not licensed by a declared criterion.

---

# P1 — Major findings

## P1-1. The endpoint-reading renderer still bypasses the typed semantics layer for zero geometry

### Finding

The new semantics module is conceptually well designed, but it is **not yet the single point of failure for every geometry claim**, as the brief states.

The endpoint table correctly derives its zero-relation prose through `TS.from_interval_record(interval)` and `sem.relation.prose` ([`paper_a_transfer_text.py` lines 286–307](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py#L286-L307)). In contrast, `block_endpoint_reading` builds the endpoint lists by reading the archived Boolean directly:

```python
contains = [m for m, r in sorted(rows.items())
            if scheme_interval(r, TC.PRIMARY_SCHEME)["contains_zero_full_precision"]]
excludes = [m for m, r in sorted(rows.items())
            if not scheme_interval(r, TC.PRIMARY_SCHEME)["contains_zero_full_precision"]]
```

See [lines 310–327](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py#L310-L327). The same function then constructs `prim_sem` for favourability, showing that the typed objects are already available but are not used for this geometry sentence.

### Why this matters

Round 9’s central failure arose because a Boolean was allowed to carry more semantic meaning than it possessed. The Round 10 architecture correctly introduces a trinary relation derived from full-precision bounds. Retaining a direct Boolean branch in a principal publication renderer recreates two sources of truth:

- bounds → typed `ZeroRelation`;
- cached `contains_zero_full_precision` → endpoint prose.

The contract currently validates that the cached Boolean agrees with bounds, so the committed artifact is internally consistent. That reduces immediate risk, but it does not satisfy the claimed architecture. A renderer called on an unvalidated or mutated object can still publish geometry contrary to the bounds, and future changes can modify one path without the other.

The issue is especially relevant because the brief expressly asks whether any renderer still infers geometry locally. The answer is **yes**.

### Correct design

The endpoint lists should be derived from the already-created typed semantics:

```python
pairs = [(m, TS.from_interval_record(scheme_interval(r, TC.PRIMARY_SCHEME)))
         for m, r in sorted(rows.items())]
contains = [m for m, sem in pairs if sem.relation is TS.ZeroRelation.CONTAINS]
excludes = [m for m, sem in pairs if sem.relation.excludes_zero]
```

If prose needs the side of exclusion, it should inspect `sem.relation`, not infer it from negated containment.

### Minimum acceptance criterion

1. Remove direct publication-renderer reads of `contains_zero_full_precision` and `excludes_zero_full_precision`.
2. Derive all geometry/favourability prose through `transfer_semantics.py` objects.
3. Add a static or AST-level test that prohibits those archived Boolean fields in publication renderers; allow them only in artifact construction/validation and compatibility code.
4. Add a contradiction mutation in which bounds and cached Boolean disagree; the renderer must follow the full-precision typed relation or refuse to render.
5. Add endpoint-reading tests for `BELOW`, `CONTAINS`, `ABOVE`, and a mixed sweep—not only the current 38/40/42 geometry.

### Stale-number status

**Not a stale-number finding.** The current bounds and Boolean agree; the defect is duplicated semantic authority.

---

## P1-2. The “independent” oracle does not independently establish the scored observation universe, and its exact comparison is incomplete

### Finding

The oracle independently reconstructs **grouping**, but it does not independently reconstruct which analyte observations actually exist and are scoreable in the source CSV.

`source_resampling_oracle.py` declares:

```python
SOLUTES = ("caffeine", "trigonelline", "5CQA")
REQUIRED_COLUMNS = ("sample", "variety", "T_degC", "p_bar", "granulometry", "on_grid")
```

The required-column set omits the three scored source fields (`CF`, `TR`, `5CQA`), and `observation_ids()` unconditionally emits three observation IDs for every retained sample record ([oracle lines 35–42 and 59–92](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py#L35-L42)).

The production corpus manifest shares the same assumption: it injects the canonical solute list into every retained row rather than deriving it from validated analyte cells ([`transfer_contract.py` lines 357–434](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L357-L434)). Its structural validator then checks only that each record’s solute-list **length** equals `n_solutes`, not that the labels are the canonical set ([lines 437–462](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L437-L462)).

### Reproduced common-mode failure

I removed `CF`, `TR`, and `5CQA` completely from a copy of `bioactives.csv` and passed that source to the oracle. It did not raise. It returned:

```json
{
  "n_records": 44,
  "n_observations_primary": 132,
  "raised": false
}
```

Thus the oracle can certify 132 named-solute observations from a CSV that contains **none of the three scored columns**. This is a partition error both implementations can make because both treat “three solutes per row” as an axiom rather than an independently verified property of the source.

The committed CSV is currently complete: it has `CF`, `TR`, and `5CQA`, and all 44 held-out values in each field are non-empty and finite. I therefore found no evidence that the **current** 132-observation artifact is wrong. The defect is in the claimed source-to-artifact assurance.

### The “exact” comparison also omits fields it normalizes or documents

The oracle normalizes `grinds` for each artifact cluster ([oracle lines 159–168](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py#L159-L168)) but `compare_design()` compares only:

- observation IDs;
- stratum ID;
- sample IDs.

It does not compare `grinds` ([lines 170–218](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py#L170-L218)). A mutation replacing a cluster’s archived grind metadata with `['X']` returned an empty problem list.

Likewise, `EXPECTED_CENSUS` documents `n_strata`, but the source-census check compares only `n_clusters` and cluster-size distribution. Mutating artifact census scalars did not produce an oracle problem. Some of those scalars may be caught by the production validator elsewhere in the full command chain, but the oracle’s own docstring overstates what its empty result proves when it says the artifact partition is exactly the source-implied one “cluster by cluster.”

### Why this is P1

The Round 10 brief specifically asks whether there is a partition error both implementations would make. This is one. The grouping algorithms are independent, but their observation universe is a shared hard-coded assumption. A source schema change, missing analyte column, blank/non-finite analyte block, or analyte rename could leave the oracle certifying phantom observations—or could force the producer to fail for a reason the source→artifact checker does not identify.

This does not invalidate the current numeric result, because the current source fields are present. It does invalidate the stronger assurance claim that the full scored partition is reconstructed from the CSV independently.

### Minimum acceptance criterion

1. In the oracle, independently map canonical analytes to source fields, for example:
   - `caffeine` → `CF`;
   - `trigonelline` → `TR`;
   - `5CQA` → `5CQA`.
2. Require those columns in `REQUIRED_COLUMNS`.
3. For every retained held-out row, validate that each scored value is present, numeric, and finite.
4. Derive observation IDs only from validated scoreable cells, or compare against an independently generated observation-level ledger that contains source field, sample ID, analyte label, and value-presence status.
5. Make the corpus manifest validator compare the exact canonical solute labels/set, not only list length.
6. Compare `grinds` if it remains part of the normalized exact representation, or remove it from the claim/shape and state that only partition-defining fields are checked.
7. Either compare the documented census fields (`n_strata`, `n_observations`, and artifact scalars) or stop implying the oracle itself verifies them.
8. Add mutations for:
   - missing `CF`, `TR`, or `5CQA` column;
   - blank analyte cell;
   - non-numeric/NaN/infinite analyte value;
   - renamed or duplicated analyte label;
   - wrong cluster grind metadata;
   - wrong `n_strata`/`n_observations` scalar;
   - current five membership mutations.
9. The top-level `paper_a_transfer_artifacts.py --check` command must report a named source-observation defect for each mutation.

### Stale-number status

**Not a stale-number finding.** The committed source currently supports 44 × 3 = 132 observations; the assurance chain does not independently prove that fact under mutation.

---

# P2 — Minor/editorial and assurance-hardening findings

## P2-1. Supplementary Table S6 claims to contain membership that it does not display

### Finding

The Table S6 caption says:

> “Cluster keys, strata and membership for every declared scheme …”

See [supplement lines 437–451](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L437-L451) and the generator at [`paper_a_transfer_text.py` lines 570–591](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py#L570-L591).

The table contains eight columns for scheme, role, strata, cluster key, cluster count, cluster-size distribution, range, and width. It contains no member identifiers or cluster-by-cluster membership. Table S7 displays the 44 sample records and their **primary** cluster only; it does not display membership for all four schemes. Exact all-scheme membership exists in the JSON artifact, not in S6.

### Minimum acceptance criterion

Either:

- revise the caption to “Cluster keys, strata, census, ranges and widths for every declared scheme,” and add a direct statement that exact per-scheme membership is in the archived JSON; or
- add actual membership for all schemes in a machine-readable supplementary table/file and cite it precisely.

The manuscript, supplement, and availability statement must distinguish human-readable design summaries from exact machine-readable membership.

### Stale-number status

**Not a stale-number finding.** This is a false description of table content.

---

## P2-2. “The bound’s sign is stable” is grammatically ambiguous; only the upper-bound sign was audited

### Finding

Table S6’s audit paragraph reports an upper-bound mean and range, then a lower-bound mean, and then states:

> “The bound’s sign is stable across seeds.”

See [supplement line 451](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L451-L451) and the generator at [`paper_a_transfer_text.py` lines 592–604](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py#L592-L604).

The archived flag is specifically `upper_bound_sign_is_stable`. Because both bounds have just been named, singular “the bound” can refer to the lower bound or to the interval generically.

### Minimum acceptance criterion

Render:

> “The **upper bound’s** sign is stable across seeds.”

Preferably derive the noun phrase from the audited flag or target schema so a future lower-bound audit cannot inherit the wrong wording.

### Stale-number status

**Not a stale-number finding.** The flag and values are current; the referent is ambiguous.

---

## P2-3. The endpoint-row fix is clean, but adjacent validators are not total on malformed/non-finite input

### Finding

The 14 named endpoint-row mutations appear to be handled as intended: missing, empty, non-list, keyless, duplicate, extra, non-dict, non-numeric, and non-finite row targets produce named problems. I found no recurrence of the Round 9 false-green row gate.

However, adjacent public validation/lookup paths do not consistently follow the same “report, never raise” discipline:

1. `validate_endpoint_contract()` performs `[float(t) for t in (targets or [])]` without catching conversion errors. A top-level target value of `"not-a-number"` raises `ValueError` instead of returning a named contract problem ([`transfer_contract.py` lines 80–120](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L80-L120)).
2. `interval_semantics()` accepts infinite bounds because it checks only order, while `validate_interval_record()` can then raise `decimal.InvalidOperation` when display quantization is attempted ([`transfer_semantics.py` lines 71–95](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_semantics.py#L71-L95); [`transfer_contract.py` lines 286–303](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L286-L303)).
3. `find_exact_audit()` assumes every list element is a mapping. A malformed integer element raises `AttributeError` at `a.get(...)` rather than the documented lookup failure type or a named validation problem ([`transfer_semantics.py` lines 187–206](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_semantics.py#L187-L206)).

### Reproduced outcomes

```json
{
  "infinite_interval_validator": {
    "raised": true,
    "exception": "InvalidOperation"
  },
  "nonnumeric_endpoint_target": {
    "raised": true,
    "exception": "ValueError"
  },
  "malformed_audit_element": {
    "raised": true,
    "exception": "AttributeError"
  },
  "semantics_negative_infinity": {
    "raised": false,
    "relation": "below_zero"
  },
  "semantics_positive_infinity": {
    "raised": false,
    "relation": "above_zero"
  }
}
```

### Why this is P2 rather than P1

These paths fail loudly rather than returning false greens, so malformed artifacts are unlikely to pass CI silently. The defect is robustness, error quality, and contract consistency—not a demonstrated scientific false pass. It should still be closed because the brief and module documentation emphasize fail-closed named diagnostics.

### Minimum acceptance criterion

1. Reject non-finite bounds with `math.isfinite()` before classification or display formatting.
2. Catch top-level endpoint-target conversion errors and return a named problem identifying index/value.
3. Type-check every audit-list element before `.get()`; return a controlled `KeyError`/validation problem naming the malformed element.
4. Add fuzz-style or parameterized tests covering `None`, strings, mappings/lists in the wrong place, NaN, ±infinity, and booleans where numeric values are expected.
5. Define and test which functions are validators returning problem lists and which are strict accessors raising controlled exceptions.

### Stale-number status

**Not a stale-number finding.** This concerns malformed-input behavior.

---

# Requested focus areas — adjudication including checked-clean sections

## A. Semantics layer itself

### Checked and sound

- **Trinary zero relation is the correct geometry decomposition.** `BELOW`, `CONTAINS`, and `ABOVE` capture the three mutually exclusive interval positions relative to zero. A fourth geometry state is unnecessary once exact contact is represented separately.
- **Closed-interval containment is appropriate.** A bound exactly equal to zero should count as containing zero, with `touches_zero_at_lower` / `touches_zero_at_upper` preserving the more specific contact fact.
- **Favourability is correctly separated from geometry.** The estimand declaration states model loss minus comparator loss and negative favours the model; `favourable_extremes()` therefore selects the most negative lower bound as most favourable and the largest upper bound as least favourable.
- **Reader-checkable direction.** The manuscript tables and endpoint reading explicitly state that negative values favour the mechanistic model. The direction is not hidden solely in code.
- **Round 9 false phrases are retired in the rendered manuscript.** I found no active claim that the two loss ranges are on the same side of zero, no claim that `+0.0038 pp` “reaches zero,” and no attribution of greatest advantage to an upper bound.

### Not clean

- **P1-1:** one central renderer still reads the cached containment Boolean directly rather than asking the typed semantics layer.

## B. Audit-scope discipline

### Checked and clean

- The retained multi-seed audit is keyed to exactly one target: 40 g, `cond_in_variety`, primary fitting loss, both bounds.
- The manuscript dagger note limits the two Monte Carlo SEs to the 40 g row.
- The Results and supplement state that 38/42 g, the three secondary schemes, and alternative fitting loss are not separately audited.
- I found no sentence that imports the `0.000520` / `0.000466 pp` errors into another endpoint or scheme.
- Reporting three decimals is defensible **as display**, because the paper explicitly says the third decimal is resolved only within the quoted Monte Carlo approximation error and does not give it coverage meaning. Coarsening to two decimals would hide the observed relation change and is not required.
- The distinction between numerical sign stability and inferential resolution is now correctly stated for the audited bound.

### Qualification

The audit-scope correction does not cure P0-1. Honest scope of numerical approximation is separate from the undeclared criterion behind “resolvable skill.”

## C. Oracle independence

### Checked and sound

- The oracle does not import `transfer_contract` or call the production grouping functions named in the brief.
- Each of the four scheme definitions is written independently.
- The current source sample/condition records reproduce the documented 26/44/78/6 cluster census and current exact observation memberships.
- The hard-coded census is appropriately treated as a diagnostic cross-check rather than the membership authority; a legitimate source change should force adjudication rather than automatic artifact editing.

### Not clean

- **P1-2:** both implementations assume, rather than independently verify, that every held-out source row contributes all three scored analytes.
- The exact-comparison claim is broader than the fields actually compared (`grinds` and some census metadata are omitted).

## D. Generated prose read as prose

### Checked and improved

- Relation prose is grammatically correct for current endpoint and loss ranges.
- “Most favourable” and “least favourable” bounds follow the estimand direction.
- The audit scope and numerical/inferential distinction are much clearer.
- The process-language cleanup reached the manuscript and supplement.

### Not clean

- **P0-1:** “no resolvable skill” remains a generated scientific verdict without a resolving criterion.
- **P2-1/P2-2:** S6’s caption and audit referent are inaccurate or ambiguous.

## E. Figures

### Figure 1 — checked and clean for scientific semantics

The rendered graph correctly shows:

- source calibration feeding the analysis branches;
- target recalibration feeding LOCO and cross-grind holdout as parallel branches;
- no LOCO → cross-grind dependency;
- the inventory assay as a comparison, not a fitted dependency;
- the external Waszkiewicz branch as independent of the Angeloni recalibration;
- seven evidence categories with visibly differentiated colour/style combinations and a legend that exposes line/patch style.

The fine-print footer and left-side contextual labels should still be proofed at the venue’s final width, but I did not demonstrate a semantic or overlap defect in the current render.

### Figure S3 — checked and clean for the Round 9 issue

- Panel (b) uses a single neutral bar colour and an explicit zero line.
- No undocumented `r > 0.4` / `r < 0` categorical threshold remains.
- Panel titles are separated and readable in the current image.
- Caption caveats correctly identify the correlations as descriptive cross-condition associations, not temporal trajectories or held-out skill.

## F. Supplementary Table S7

### Checked and structurally clean

- 44 data rows are present.
- The Markdown parses as eight columns when escaped pipe characters in cluster IDs are handled correctly.
- The eight off-grid records are marked consistently as lookup undefined.
- No held-out record is omitted.

### Production proof still required

The table has not been demonstrated at the journal’s final column/page width. This is a known production risk rather than a proven content defect. Before submission, render the actual Elsevier/JFE conversion and either use landscape/full-width placement or move the table to a CSV/XLSX supplement if it becomes illegible. This is not counted as a formal finding because no target-width failure was reproduced.

## G. Process language

### Checked and clean within the Round 10 scope

I found no visible manuscript/supplement recurrence of:

- “earlier draft” / “previous draft” narration;
- Round-number identifiers;
- “already in repo” location narration;
- internal review-ticket IDs;
- generator self-description in reader-facing prose.

The remaining backticked `docs/` paths occur in the expressly out-of-scope metadata/figure-caption scaffolding that the brief says is stripped or permitted at submission. I did not report those.

## H. Known open, out-of-scope, and settled items

### Not re-reported

- fraction-versus-measured-cup rate-profile contrast;
- 11/104 unbound registered slow-lane values;
- approximately 255 hand-declared design settings;
- author/affiliation/ORCID and declarations metadata;
- novelty search;
- release DOI/tag;
- working-draft/internal-review scaffolding.

### Settled items not reopened

I found no new contrary evidence on:

- Reynolds number using superficial velocity;
- source `flow` being consumed as mass flow;
- 38/40/42 g collected-mass endpoints.

---

## Recommended remediation order

1. **Resolve P0-1 first.** Decide whether the paper will remain criterion-free or will define a practical/inferential resolving rule. This changes multiple generated surfaces and should be settled before editorial polishing.
2. **Close P1-1.** Make the typed semantics module the actual sole source of geometry/favourability prose.
3. **Close P1-2.** Extend the oracle from source-record grouping to source-observation validation and complete its exact-comparison contract.
4. **Correct P2-1 and P2-2** in the same text-generator edit.
5. **Harden malformed-input behavior** and add targeted tests.
6. Regenerate all publication surfaces and run the full advertised command chain, including the complete test suite.
7. Render the final manuscript/supplement at venue dimensions and proof Figure 1, Figure S3, and Table S7.

### Minimum merge/re-review package

A focused Round 10 correction should provide:

- a before/after list of every “resolvable/unresolved skill” surface;
- the chosen decision rule or criterion-free replacement language;
- a test demonstrating that uncalibrated ranges cannot generate an unsupported no-skill conclusion;
- an AST/static test showing publication renderers do not read archived containment Booleans;
- oracle mutations for missing/blank/non-finite analyte fields and wrong grind/census metadata;
- full command outputs from the brief’s check chain;
- final-width PDF or image proofs for S7 and the changed figures/tables.

---

# Appendix A — Focused mutation audit

The following mutations were executed against the exact Round 10 modules in isolation:

```json
{
  "infinite_interval_validator": {
    "exception": "InvalidOperation",
    "message": "[<class 'decimal.InvalidOperation'>]",
    "raised": true
  },
  "malformed_audit_element": {
    "exception": "AttributeError",
    "message": "'int' object has no attribute 'get'",
    "raised": true
  },
  "manifest_wrong_solute_labels": {
    "problems": []
  },
  "nonnumeric_endpoint_target": {
    "exception": "ValueError",
    "message": "could not convert string to float: 'not-a-number'",
    "raised": true
  },
  "oracle_ignores_artifact_census_scalars": {
    "problems": []
  },
  "oracle_ignores_grinds": {
    "problems": []
  },
  "oracle_missing_solute_columns": {
    "n_observations_primary": 132,
    "n_records": 44,
    "raised": false
  },
  "semantics_negative_infinity": {
    "lower": "-inf",
    "raised": false,
    "relation": "below_zero",
    "upper": "-1.0"
  },
  "semantics_positive_infinity": {
    "lower": "1.0",
    "raised": false,
    "relation": "above_zero",
    "upper": "inf"
  }
}
```

Interpretation:

- missing source analyte columns, wrong manifest solute labels, wrong grind metadata, and altered census scalars are false negatives for the specific functions tested;
- malformed/non-finite validator inputs are loud exceptions rather than false greens;
- no mutation demonstrated that the current committed headline values are numerically stale or wrong.

---

# Appendix B — Exact source observations relevant to P1-2

The committed CSV header contains:

```text
sample,variety,T_degC,p_bar,granulometry,on_grid,TR,TA,AA,CA,3CQA,5CQA,CF,FA,3_5diCQA,totCQA,totOA
```

At the reviewed commit:

- total condition-level rows: 66;
- held-out coarse/fine rows: 44;
- held-out `CF` cells: 44 present, numeric, finite;
- held-out `TR` cells: 44 present, numeric, finite;
- held-out `5CQA` cells: 44 present, numeric, finite.

Thus P1-2 is an assurance/common-mode defect, not evidence that the present 132-observation result used missing source values.

---

# Appendix C — Final disposition by review-brief section

| Brief section | Disposition |
|---|---|
| Semantics decomposition | **Conceptually clean; implementation not fully centralized (P1-1)** |
| Closed-interval convention | **Clean** |
| Estimand direction | **Clean and reader-checkable** |
| Audit scope | **Clean** |
| Three-decimal display | **Acceptable with current caveat** |
| Oracle grouping independence | **Clean** |
| Oracle observation-universe independence | **Not clean (P1-2)** |
| Generated interval prose | **Improved; current geometry/favourability wording clean** |
| Generated scientific conclusion | **Submission blocker (P0-1)** |
| Figure 1 semantics | **Clean; final-width proof pending** |
| Figure S3 semantics | **Clean** |
| S7 structure | **Clean; final-width proof pending** |
| S6 content description | **Not clean (P2-1/P2-2)** |
| Process-language cleanup | **Clean within stated scope** |
| Stale-number category | **Checked and empty** |
| Known open/out-of-scope items | **Not re-reported** |
| Settled Re/flow/endpoints | **Not reopened; no contrary evidence** |

