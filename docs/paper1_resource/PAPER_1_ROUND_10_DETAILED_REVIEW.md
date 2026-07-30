# Paper 1 — Detailed Review, Round 10

**Review date:** 29 July 2026  
**Review brief:** [`PAPER_1_REVIEW_BRIEF_ROUND_10.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_10.md)  
**Repository snapshot reviewed:** [`3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5`](https://github.com/trbrewer/puckworks/commit/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5)  
**Primary manuscript:** [`docs/submission/PAPER_A_JFE_MANUSCRIPT.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)  
**Canonical working draft:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/PAPER_A_DRAFT.md)  
**Supplement:** [`docs/submission/PAPER_A_JFE_SUPPLEMENT.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)

---

## Executive verdict

**NOT READY FOR SUBMISSION — MAJOR REVISION REQUIRED.**

Round 10 is materially better than Round 9. I found **no stale headline value**, and the Round 9 defects involving interval geometry, bound favourability, audit-scope leakage, endpoint-row deletion, source-membership swaps, and figure colour semantics are substantially corrected.

One submission-blocking issue nevertheless remains. The manuscript's central editor-facing conclusion — that the model supplies “no resolvable skill” — is not identified by the analysis the paper actually declares. The paper expressly says its ranges have no calibrated coverage and support no claim of distinguishability, non-distinguishability, or equivalence. It also supplies no practical-equivalence margin or other decision rule. The analysis can support the narrower conclusion that the observed advantage is small and **does not establish useful mechanistic transfer**; it cannot support a categorical property-level statement that the model adds no resolvable skill.

I also found three major assurance defects. The canonical and submission manuscripts are not held in material scientific agreement despite the brief's description; estimand direction and resampling-design semantics are duplicated rather than contract-bound; and the interval-record validator accepts contradictory or malformed semantic fields. A remaining editorial false green lets active review-history prose and repository/test narration survive in files described as submission-ready.

### Finding count

| severity | count | disposition |
|---|---:|---|
| **P0 — submission-blocking** | **1** | Central scientific inference must be corrected or supported by a declared decision analysis. |
| **P1 — major** | **3** | Canonical/submission agreement and two load-bearing assurance contracts require repair. |
| **P2 — editorial** | **1** | Publication-process leakage and its false-green scanner remain. |
| **Stale-number findings** | **0** | **Checked clean.** |

### Findings at a glance

| ID | finding | principal risk |
|---|---|---|
| **P0-1** | “No resolvable skill” is not licensed by an uncalibrated sensitivity analysis with no practical decision margin | The abstract, Results, significance paragraph, cover letter, and captions state a stronger negative conclusion than the declared analysis can determine. |
| **P1-1** | The canonical draft and venue manuscript are not in material scientific agreement, and CI does not enforce such agreement | Repository audits can certify one version while an editor receives another; future edits can re-seed retired claims. |
| **P1-2** | Estimand direction and resampling-design semantics are not contract-bound | A reversed estimand or false design metadata can pass the named contract/oracle layers and silently invert or misdescribe generated prose. |
| **P1-3** | The interval semantic/record contract accepts invalid inputs and contradictory stored facts | The assurance layer that is meant to prevent Round 9's false sentences can itself return false greens. |
| **P2-1** | The process-language gate is still line-wrap- and vocabulary-sensitive | Active draft history and internal producer/test narration remain in submission-facing files while the scanner reports zero problems. |

---

## 1. Scope, method, and execution status

### 1.1 Scope followed

I followed the Round 10 brief's single-paper scope. Papers B2 and 3 were not reviewed. I did not report the explicitly excluded author metadata, affiliations, ORCIDs, CRediT roles, funding, competing-interest statement, generative-AI declaration, novelty-search completion, DOI/tag, or working-draft date. I did not re-report the three known open items: the fraction-versus-measured-cup rate-profile contrast, the 11 unbound slow-lane values, or the approximately 255 hand-sourced design settings.

I did not reopen the settled Reynolds-number or collected-mass endpoint definitions because I found no contrary evidence.

### 1.2 Materials inspected

The review covered the manuscript, canonical draft, supplement, package, cover letter, highlights, front-matter source, standalone captions, Round 9 review and remediation plan, source CSV, transfer contract, transfer semantics, source-resampling oracle, consistency checker, artifact checker, generated-text checker, relevant test sources, and the re-rendered Figure 1 and Figure S3.

The load-bearing code inspected included:

- [`puckworks/paper_a/transfer_contract.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py);
- [`puckworks/paper_a/transfer_semantics.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_semantics.py);
- [`puckworks/paper_a/source_resampling_oracle.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py);
- [`tools/paper_a_transfer_artifacts.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_artifacts.py);
- [`tools/paper_a_transfer_text.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py); and
- [`tools/paper_a_consistency.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_consistency.py).

### 1.3 Independent checks performed

I independently reconstructed the held-out source census from `bioactives.csv`:

| scheme | clusters | strata | cluster-size distribution | observations |
|---|---:|---:|---|---:|
| `cond_in_variety` | 26 | 2 | 3×8, 6×18 | 132 |
| `sample_in_variety_grind` | 44 | 4 | 3×44 | 132 |
| `cond_in_group` | 78 | 6 | 1×24, 2×54 | 132 |
| `group` | 6 | 1 | 22×6 | 132 |

I then executed focused mutations against the exact-commit `transfer_contract`, `transfer_semantics`, `source_resampling_oracle`, and process-language checker. The transcript and runnable script accompany this review:

- `PAPER_1_ROUND_10_FOCUSED_MUTATION_AUDIT.txt`
- `PAPER_1_ROUND_10_FOCUSED_MUTATION_AUDIT.py`

I also read the rendered publication prose against the full-precision bounds and inspected the exact-commit Figure 1 and Figure S3 images rather than relying on generator descriptions.

### 1.4 Execution limitation

I was unable to obtain a complete executable clone in the review environment, so I did **not** run the full approximately 15-minute test suite or the approximately 25-minute PDE regeneration. I also did not execute the complete `paper_a_transfer_artifacts.py --check` command end to end. The focused mutations therefore distinguish carefully between:

1. defects reproduced in locally available exact-commit modules;
2. defects established by direct source inspection of the complete checker/generator; and
3. claims I do **not** make — for example, changing `primary_scheme` is caught by a separate explicit guard in the full artifact checker, even though the lower-level validator accepts any declared scheme.

The findings below do not depend on re-running the slow science producers. They concern current published inference, current file disagreement, and directly reproduced false-green contract behavior.

---

## 2. Independent numerical adjudication

### 2.1 Headline and endpoint values

The manuscript and supplement agree on the following values, and I found no stale numerical rendering:

| endpoint | model pooled MAPE | comparator MAPE | model − comparator | primary full-precision range | primary zero relation | model worse on |
|---:|---:|---:|---:|---|---|---:|
| 38 g | 8.39% | 8.83% | −0.447 pp | [−0.8843868833, −0.0424325436] | excludes zero, negative side | 61/132 |
| 40 g | 8.44% | 8.83% | −0.394 pp | [−0.8290522506, +0.0037905184] | contains zero | 62/132 |
| 42 g | 8.41% | 8.83% | −0.425 pp | [−0.8912505494, +0.0058444686] | contains zero | 60/132 |

These agree with [Table 4a](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L869-L877) and [Supplementary Table S3](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_SUPPLEMENT.md#L327-L335).

The sign convention is also correct in the current publication files: the estimand is model loss minus comparator loss, so negative values favour the mechanistic model.

### 2.2 Secondary sensitivity schemes

All three secondary ranges are wholly negative at every endpoint:

| endpoint | sample-record scheme | condition-in-group scheme | whole-group scheme |
|---:|---|---|---|
| 38 g | [−0.802, −0.097] | [−0.798, −0.085] | [−0.940, −0.060] |
| 40 g | [−0.742, −0.053] | [−0.740, −0.039] | [−0.863, −0.024] |
| 42 g | [−0.804, −0.053] | [−0.792, −0.051] | [−0.883, −0.035] |

These ranges are not calibrated confidence intervals and do not prove superiority. They do, however, matter when judging whether the categorical phrase “no resolvable skill” is an identified result rather than a chosen interpretation.

### 2.3 Monte Carlo audit

The audit is now correctly scoped to one exact target: 40 g, `cond_in_variety`, primary fitting loss. The retained lower- and upper-bound Monte Carlo standard errors are approximately 0.000520 and 0.000466 pp. The +0.0037905 pp canonical upper bound is therefore numerically on the positive side by roughly eight estimated Monte Carlo standard errors. The paper correctly distinguishes this numerical sign stability from inferential coverage.

The final displayed third decimal is not seed-invariant, and the paper now says so. No separate precision audit is claimed for 38 g, 42 g, the secondary schemes, or the alternative fitting loss. This part of the Round 9 remediation is checked clean.

---

# P0 — Submission-blocking finding

## P0-1. The central “no resolvable skill” conclusion is not licensed by the declared analysis

### Finding

The manuscript turns a small observed improvement and an uncalibrated sensitivity analysis into a categorical negative conclusion that the model supplies “no resolvable skill.” The declared analysis does not identify that proposition.

The relevant surfaces include:

- the [abstract](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L20-L25): “no resolvable skill beyond a transferred level”;
- the [principal Results headline](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L803-L807): “did not supply resolvable skill”;
- the [endpoint interpretation](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L884-L894): “No row supports a claim of resolvable skill” and “unresolved throughout”;
- the [cover letter](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_COVER_LETTER.md#L9-L22): “adding no resolvable skill” and “did not establish resolvable mechanistic skill”;
- the [front-matter significance paragraph](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/paper_a_front_matter.yaml#L90-L99); and
- the standalone caption map's description of Figure 3 as “no resolvable gain” in [`PAPER_A_CAPTIONS.md`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/figures/PAPER_A_CAPTIONS.md#L9-L18).

The paper simultaneously states that:

1. the ranges are **fixed-predictor clustered sensitivity ranges**, not calibrated confidence intervals ([Methods](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L561-L568));
2. no calibrated confidence procedure is specified; and
3. the authors make **“no claim of statistical distinguishability, non-distinguishability or equivalence”** from those ranges ([Results](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L845-L856)).

No predeclared practical-equivalence margin, minimum useful improvement, superiority criterion, non-inferiority criterion, or calibrated decision rule is supplied anywhere in the transfer analysis.

### Why the inference does not follow

The numerical result is:

\[
\Delta = \mathrm{MAPE}_{model}-\mathrm{MAPE}_{comparator}=-0.394\ \mathrm{pp},
\]

so the point estimate favours the mechanistic model. The model's observed relative MAPE reduction is approximately 4.5%, although the supplement's `skill` column does not define that quantity explicitly. The primary range contains zero at 40 g and 42 g, excludes it on the favourable side at 38 g, and every secondary scheme is wholly negative at all three endpoints.

None of that proves that the model has reproducible or practically useful incremental skill. But the converse is equally important: an uncalibrated range cannot establish that the model has **no** such skill, is equivalent to the comparator, is non-distinguishable from it, or is practically negligible. The manuscript itself correctly disclaims those inferential interpretations.

The problem is therefore not that the paper should claim superiority. It should not. The problem is that it replaces “this analysis does not establish useful skill” with a property-level negative statement, “no resolvable skill,” without defining what “resolvable” means or how that verdict is obtained.

This is especially visible at 38 g and under the source-established sample-record scheme: if range position is not inferential evidence, those negative ranges cannot establish skill; but they also cannot be ignored as though the analysis positively establishes no skill. The defensible conclusion is epistemic and analysis-limited, not categorical.

### Why this is P0

The wording appears in the abstract, editor significance paragraph, primary Results headline, endpoint synthesis, cover letter, and caption architecture. It is presented as the paper's principal quantitative result and as the reason the paper is a useful “negative” study. Correcting it changes the central scientific claim an editor and reviewer are asked to evaluate.

The manuscript's final conclusion is already closer to the defensible form: acceptable holdout error “does not by itself establish useful transfer” ([Conclusion](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1221-L1223)). That formulation should govern the other surfaces.

### Minimum acceptance criterion

Choose one of the following paths.

#### Path A — Correct the claim to match the current analysis

Replace every categorical “no resolvable skill,” “adding no resolvable skill,” and “unresolved throughout” formulation with wording that attaches the limitation to the evidence. A suitable core statement is:

> The mechanistic model showed a small observed advantage over the O-trained level-only comparator (−0.394 percentage points in pooled MAPE). The present fixed-predictor sensitivity analyses do not establish whether that advantage is reproducible, statistically distinguishable, or practically useful; acceptable cross-grind endpoint error therefore does not by itself establish mechanistic transfer.

At minimum:

1. regenerate the abstract, significance paragraph, manuscript headline, endpoint reading, supplement reading, cover letter, package, and caption map from the corrected claim;
2. define or remove Supplementary Table S3's unexplained `skill` column — preferably rename it “relative MAPE reduction” and state its formula if retained;
3. reserve “no skill,” “equivalent,” “non-distinguishable,” and similar decision language for analyses that actually define those decisions; and
4. add a consistency guard that rejects categorical absence/equivalence language when the artifact declares `not_calibrated`, has no decision margin, and has no calibrated decision result.

#### Path B — Add an analysis capable of supporting the stronger claim

If the authors wish to retain a conclusion about absence of practically meaningful skill, they must predeclare and justify a practical margin and use an appropriate calibrated procedure. The analysis should state:

- the exact estimand and sign convention;
- a scientifically justified smallest useful improvement or equivalence margin in percentage points;
- the dependence unit and whether predictors are refitted inside each draw;
- the confidence/coverage target and decision rule; and
- sensitivity to plausible clustering choices and endpoint tolerance.

The manuscript would then need to distinguish superiority, non-inferiority, and equivalence rather than treating “contains zero” or “small relative to 8.4% error” as a substitute for those decisions.

### Required checks

- Mutation-test the inferential-status object: removing the margin or changing the analysis to `sensitivity_only` must make categorical no-skill/equivalence prose impossible to generate.
- Search all submission surfaces for `no resolvable`, `no skill`, `equivalent`, `non-distinguishable`, `unresolved throughout`, and `adding no`.
- Read the resulting abstract, Results headline, endpoint paragraph, conclusion, cover letter, and caption map as a continuous argument.
- Verify that the revised text neither overclaims skill nor overclaims absence of skill.

### Stale-number status

**Not a stale-number finding.** The numbers are current; the inference attached to them is too strong.

---

# P1 — Major findings

## P1-1. The canonical draft and submission manuscript are not in material scientific agreement, and CI does not enforce the claimed agreement

### Finding

The Round 10 brief describes `docs/PAPER_A_DRAFT.md` as the canonical working draft and says it is held in content agreement with the venue manuscript by CI. The active scientific abstracts are materially different.

The [canonical abstract](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/PAPER_A_DRAFT.md#L30-L83) says, among other things, that:

- the rate is “not separately estimable” and the parameters are “not identifiable”;
- the model has “incremental skill of only ≈4.5% relative (0.394 pp absolute)”;
- the kinetic structure “adds little”; and
- the abstract narrates correction of an earlier version.

The [submission abstract](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L20-L25) instead uses the more qualified “weakly separated” language and the different central conclusion “no resolvable skill beyond a transferred level.”

This finding does **not** report the working-draft date or a designated repository-history note, both of which the brief excludes. It concerns active abstract-level scientific claims and interpretations in the file described as canonical.

The current consistency checker does not establish whole-document or central-claim agreement. Its `_phrase_drift()` function tests a curated set of required and banned phrases after whitespace normalization; it is not a semantic or text-equivalence contract ([`paper_a_consistency.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_consistency.py#L195-L224)). The front-matter YAML generates the submission abstract, package, significance paragraph, highlights, and cover letter, but the canonical abstract remains a separate copy.

The mismatch is additionally consequential because [`claim_coverage.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/claim_coverage.py#L32-L35) defaults to auditing the canonical draft and audits the venue conversion only when explicitly invoked with `--conversion` ([lines 374–377](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/claim_coverage.py#L374-L377)). A green default claim audit can therefore describe a different active abstract from the one sent to a journal.

### Why this is major

A repository may legitimately keep a longer canonical manuscript and a venue-specific conversion. It may not describe them as content-aligned while their central claims differ and the assurance layer checks only selected phrases. This creates two failure paths:

1. a correction made to the venue manuscript does not reach the file treated as canonical; and
2. a later conversion or edit reintroduces retired wording from the canonical source.

It also makes review provenance ambiguous: a reviewer can be told that a claim is bound in the canonical manuscript while the submission abstract says something else.

### Minimum acceptance criterion

1. Designate one authoritative source for every active scientific block, including the abstract and central transfer conclusion.
2. Generate both the canonical and venue-specific renderings from that source, allowing only explicit venue transformations such as length, headings, and formatting.
3. Replace the current curated-phrase claim of “content agreement” with a structural contract over named blocks. At minimum compare normalized abstract, generated transfer blocks, conclusion, and figure captions, with an explicit map for approved venue-specific differences.
4. Run claim coverage against **both** active manuscripts by default and fail if either exceeds the accepted baseline or if a load-bearing claim appears in only one.
5. Bring the current canonical abstract into scientific agreement with the accepted P0-1 wording. Internal history may remain in HTML comments, review resources, or a clearly excluded repository note, not in the active abstract.
6. Add a mutation test that changes the central conclusion in either file and requires CI to fail.

### Stale-number status

**Not a stale-number finding.** The 0.394 pp and approximately 4.5% relative reduction are mathematically current; the active claim surfaces are not semantically aligned.

---

## P1-2. Estimand direction and resampling-design semantics are duplicated rather than contract-bound

### Finding

The Round 9 remediation correctly recognized that favourability cannot be inferred from an interval and proposed one structured estimand object. The implemented architecture instead has two independent declarations:

1. a free-text `RESAMPLING_ESTIMAND` serialized into the artifact in [`transfer_contract.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L469-L475); and
2. a separate hard-coded `PAIRED_LOSS_DIFFERENCE` direction object in [`transfer_semantics.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_semantics.py#L134-L167).

The text generator calls `TS.favourable_extremes(prim_sem)` without passing a direction derived from the artifact, so it receives the module-level default. The adjacent prose then hard-codes “model loss minus comparator loss, negative values favour the mechanistic model” ([`paper_a_transfer_text.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_text.py#L310-L365)).

The current publication is correct because the two declarations presently agree. The assurance chain does not require them to agree.

The same problem extends to the resampling design. `resampling_design()` serializes:

- nested schema version;
- estimand text;
- predictor-refit status;
- interval kind;
- primary scheme;
- scheme order; and
- each scheme's role, label, rationale, strata, cluster key, cluster count, size distribution, stratum count, membership hash, and exact membership

([`transfer_contract.py` lines 639–668](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L639-L668)).

`validate_resampling_design()` checks only that the primary is a declared name, predictors are not marked as refitted, observation coverage is complete and nonduplicated, every scheme covers the same observation IDs, `n_clusters` matches the membership length, and the self-hash matches ([lines 671–700](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L671-L700)). It does not validate the nested schema, estimand, interval kind, scheme order, role, label, rationale, strata declaration, cluster-key declaration, `n_strata`, or size-distribution field.

The independent source oracle is a real improvement. It rebuilds exact cluster IDs, observation IDs, strata, and sample membership from the CSV. However, its final comparison omits `grinds` and does not validate the top-level or scheme-spec metadata ([`source_resampling_oracle.py` lines 180–245](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py#L180-L245)). Although `EXPECTED_CENSUS` records `n_strata`, the source-census check compares only cluster count and size distribution ([lines 51–60 and 209–218](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/source_resampling_oracle.py#L51-L60)).

This falls short of the Round 9 remediation plan's explicit acceptance requirement to compare role, declared strata, cluster-key fields, exact sample lists and grinds, per-cluster counts, cluster and stratum counts, size distribution, and hash ([remediation plan, Step 4](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/paper1_resource/PAPER_1_ROUND_9_REMEDIATION_IMPLEMENTATION_PLAN.md#L1268-L1285)).

### Reproduced mutations

The focused audit changed each item below while preserving exact observation membership. Both `validate_resampling_design()` and `source_resampling_oracle.compare_design()` returned an empty problem list:

- reversed estimand text;
- changed interval kind to “calibrated 95% confidence interval”;
- nested schema version changed to 999;
- reversed scheme order;
- wrong scheme role;
- wrong scheme label;
- wrong declared strata;
- wrong declared cluster key;
- wrong `n_strata`;
- wrong cluster-size distribution;
- wrong rationale; and
- wrong archived `grinds` with a refreshed self-hash.

The full artifact checker separately pins the primary scheme, so this report does not claim that a primary-scheme change passes the entire chain. No equivalent explicit guard was found for the mutations listed above.

### Why this is major

The Round 9 failure was not a bad number; it was correct numbers rendered with inverted scientific meaning. The current design can recreate that class of failure:

- artifact estimand says comparator minus model;
- semantic default still says model minus comparator;
- the validator and oracle remain green; and
- generated prose continues to say negative favours the model.

Similarly, false role/strata/key metadata can propagate into Methods, Table 5, and Supplementary Table S6 while the exact membership oracle remains green. A source-membership oracle and a scientific-design contract answer different questions; the present checker implements the former but describes a broader assurance than it performs.

### Minimum acceptance criterion

1. Replace the free-text estimand and separate default direction with one structured, typed object, for example:

   ```json
   {
     "id": "pooled_mape_model_minus_level_only_pp",
     "metric": "MAPE",
     "left_operand": "mechanistic_model",
     "right_operand": "o_trained_level_only_comparator",
     "operation": "left_minus_right",
     "units": "percentage_points",
     "negative_values_favour": "mechanistic_model",
     "zero_means": "equal pooled MAPE under the stated scoring rule"
   }
   ```

2. Derive renderer direction from that validated object. Remove the default direction from publication-facing calls; a missing or unknown direction must fail rather than silently choose one.
3. Rebuild the canonical resampling design from the source and exact contract definitions, then compare all declared and derived fields: schema, estimand, interval kind, predictor-refit flag, primary scheme, order, name, role, label, rationale, strata, cluster key, `n_clusters`, `n_strata`, size distribution, membership, sample IDs, grinds, per-cluster observation count, and hashes.
4. Keep the independent source implementation, but compare the complete normalized scientific object rather than only selected membership fields.
5. Add full-checker mutation tests for every mutation listed above. Each must produce a named failure from `paper_a_transfer_artifacts.py --check`.
6. Add a renderer mutation test: reversing the structured operation or favourable sign must either fail validation or deliberately reverse every favourability sentence. It must never leave the current prose unchanged.

### Stale-number status

**Not a stale-number finding.** Current direction and current outputs agree; the contract does not guarantee that agreement.

---

## P1-3. The interval semantic/record contract accepts invalid inputs and contradictory stored facts

### Finding

`interval_record()` stores a rich semantic object:

- `kind`;
- full-precision bounds;
- contains/excludes-zero flags;
- signed nearest bound to zero;
- width;
- display digits;
- display lower and upper values;
- display text; and
- display zero-contact status

([`transfer_contract.py` lines 239–278](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L239-L278)).

`validate_interval_record()` checks only:

1. that usable full-precision bounds can be converted;
2. that upper is not below lower;
3. the two containment booleans, using `bool(...)` coercion; and
4. the formatted display text

([lines 286–303](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_contract.py#L286-L303)).

The artifact checker recursively delegates every interval record to this validator ([`paper_a_transfer_artifacts.py`](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_transfer_artifacts.py#L116-L135)).

### Reproduced false greens

Starting from the correct 40 g interval, the validator returned an empty problem list after each of these mutations:

- `kind` changed to “calibrated 95% confidence interval”;
- `width_pp` changed to 999;
- `signed_nearest_bound_to_zero_pp` changed to −999;
- `display.lower` changed to 999;
- `display.upper` changed to 999;
- `display.touches_zero` changed to false;
- `excludes_zero_full_precision` deleted from a zero-containing interval;
- `contains_zero_full_precision` deleted from a zero-excluding interval; and
- `contains_zero_full_precision` replaced by the string `"false"` on a containing interval.

The missing-field and string cases pass because `bool(None)` and `bool("false")` are used rather than exact type/value validation.

The semantic classifier itself also accepts inputs the Round 9 remediation plan explicitly required it to reject. `interval_semantics(True, 1.0)`, string bounds such as `"0.1"`, and positive infinity are all converted and classified rather than rejected. The implemented function is at [`transfer_semantics.py` lines 80–106](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/puckworks/paper_a/transfer_semantics.py#L80-L106); the prior plan required finite floats and rejection of booleans, strings, NaN, and infinities ([remediation plan lines 161–173](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/paper1_resource/PAPER_1_ROUND_9_REMEDIATION_IMPLEMENTATION_PLAN.md#L161-L173)).

### Current-publication adjudication

The committed interval values and rendered prose are correct. This finding does not assert a current wrong range. It asserts that the named semantic assurance layer can accept a record whose labels, width, contact status, or derived facts contradict its bounds — exactly the class of condition the new layer exists to prevent.

### Why this is major

The manuscript now relies on stored semantic duplication to keep prose safe. Duplicated fields are useful only if they are exact-validated or never trusted. The current implementation does neither consistently: some consumers derive from bounds, while the artifact retains unchecked semantic fields that can be used by other renderers and can falsely advertise a calibrated interval.

The validator's docstring says it reconciles an interval's display fields with full precision, and the artifact checker says it reconciles every interval record. That assurance is materially broader than the checks performed.

### Minimum acceptance criterion

1. Define an exact interval-record schema with required keys, accepted types, and no silent defaults for stored semantic fields.
2. Reject booleans, strings, NaN, and infinities before classification. Accept only finite real numbers, explicitly excluding `bool`.
3. Rebuild a canonical record from validated bounds and display precision, then exact-compare every derived field: `kind`, both booleans, signed-nearest bound, width, display digits/lower/upper/text/contact.
4. Reject missing or unexpected fields unless schema evolution explicitly permits them.
5. Replace `bool(value)` coercion with `isinstance(value, bool)` plus exact equality.
6. Make malformed records produce named validation problems rather than uncaught formatting/decimal exceptions.
7. Either remove duplicated fields that consumers do not need or require all consumers to accept only a validated typed object.
8. Add mutations for every reproduced false green, including field deletion, strings in boolean fields, booleans as bounds, numeric strings, NaN, and infinities.

### Stale-number status

**Not a stale-number finding.** The current bounds and display strings are correct; the validator is incomplete.

---

# P2 — Editorial finding

## P2-1. Publication-process leakage remains, and the process-language gate reports a false green

### Finding

The submission manuscript still contains active draft-history narration:

> “An”  
> “earlier version of this paragraph stated that an empirical whole-cup comparison was unavailable,”  
> “two sentences after using one; that was wrong.”

The phrase is split across [manuscript lines 1025–1027](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/submission/PAPER_A_JFE_MANUSCRIPT.md#L1022-L1031). The process-language pattern explicitly contains `an earlier version`, but `_placeholders_and_process_language()` scans each visible line independently ([`paper_a_consistency.py` lines 157–173 and 267–318](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/tools/paper_a_consistency.py#L157-L173)). The exact-commit scanner returned **zero problems**, while whitespace-normalizing the visible manuscript reveals the prohibited phrase.

The standalone file titled “submission-ready figure captions” also begins with reader-inappropriate process and repository narration:

- “The second review asked…”;
- “presentation numbers differ from the producer identifiers”;
- “rendered images previously carried…”;
- producer/module identifiers; and
- `tests/test_figure_exports.py`

([`PAPER_A_CAPTIONS.md` lines 1–18](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/figures/PAPER_A_CAPTIONS.md#L1-L18)).

The captions may need an internal mapping file, but that mapping is not a journal caption deliverable. Calling the file submission-ready while retaining review and test history creates a direct upload risk.

The implementation also falls short of the prior remediation plan, which required:

- inclusion of the canonical draft;
- paragraph-visible scanning;
- internal path patterns covering `docs/`, `tools/`, `tests/`, `puckworks/`, and `.github/`; and
- tests injecting violations into every publication surface

([remediation plan lines 1503–1511 and 1531–1568](https://github.com/trbrewer/puckworks/blob/3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5/docs/paper1_resource/PAPER_1_ROUND_9_REMEDIATION_IMPLEMENTATION_PLAN.md#L1503-L1568)). The current internal-path rule covers only back-ticked `docs/` paths and is applied only to the manuscript and supplement, not the standalone captions.

### Minimum acceptance criterion

1. Replace the manuscript history sentence with the current scientific fact only. For example:

   > Measured complete-cup concentrations are available across all 15 experiments and are the reference for the 27.8/38.3/30.7% sampled-aggregate audit. The full fraction-versus-measured-cup rate-profile contrast has not yet been run.

2. Split `PAPER_A_CAPTIONS.md` into:
   - an internal figure-number/producer mapping retained in repository documentation; and
   - an upload-ready caption file containing only the captions an editor should receive.
3. Strip HTML comments while preserving line positions, then scan normalized visible paragraphs rather than isolated physical lines. Maintain a mapping back to the first source line for diagnostics.
4. Include the canonical draft and all source templates that can regenerate reader-facing prose.
5. Expand internal-path detection to `docs/`, `tools/`, `tests/`, `puckworks/`, and `.github/`, with narrow section-aware allowances for genuine data/code availability text.
6. Add patterns/tests for `second review`, `third review`, `previously carried`, producer identifiers, and test paths in submission-ready caption preambles.
7. Add a line-wrap mutation test in which each prohibited phrase is split at every token boundary and must still fail.

### Stale-number status

**Not a stale-number finding.** This is publication-process and assurance leakage.

---

## 3. Round 10 requested adjudications

### 3.1 (a) The semantics layer itself

**Current interval geometry: checked clean.**

The trinary `BELOW / CONTAINS / ABOVE` relation is the correct minimum decomposition for the present zero-relation prose. A fourth geometric fact — exact contact — is correctly kept separate through lower/upper touch flags. I do not see a required fifth interval-position category for the current publication statements.

The closed-interval convention is appropriate: an exact zero bound belongs to the interval, while “touches zero at its upper/lower bound” remains a separate fact. The current 40 g upper bound is positive, not exact contact; the manuscript no longer calls it “reaching zero at its upper bound.”

The rendered current favourability statements are also correct: the smallest lower bound is the most favourable extreme and the largest upper bound is the least favourable extreme for model-minus-comparator loss.

**Not clean:** estimand direction is a declaration duplicated in two places rather than a property validated from one contract. This is P1-2.

**Not clean:** the semantic classifier and record validator accept invalid/contradictory inputs. This is P1-3.

### 3.2 (b) Audit-scope discipline

**Checked clean.**

The manuscript now states precisely that the multi-seed audit covers only 40 g, `cond_in_variety`, primary fitting loss. It reports lower and upper standard errors separately. Table 4a carries a row-specific dagger, and the supplement explicitly says the other endpoints, secondary schemes, and alternative loss do not inherit this audit.

Retaining three displayed decimals is defensible with the current caveat. The third decimal distinguishes exact contact from a small signed value in the canonical run, while the text states that the final digit is not seed-invariant and carries no coverage meaning. I would not coarsen all values to two decimals, because that would visually turn +0.0038 into exact zero and recreate the contact error.

The lack of separate 38 g/42 g audits means their Monte Carlo approximation uncertainty is unknown. The paper is honest about that and does not need those extra audits merely to report the canonical ranges. It must not, however, use those uncalibrated ranges to support the categorical P0-1 conclusion.

### 3.3 (c) Oracle independence

**Exact source membership: checked clean and materially improved.**

The oracle independently parses the CSV with `csv.DictReader`, implements the four grouping branches separately, and reconstructs the 44-record/132-observation census. Exact observation membership, cluster IDs, stratum IDs, and sample IDs are compared. The Round 9 solute-swap and wrong-condition-cluster defects are closed.

The hard-coded `EXPECTED_CENSUS` is acceptable as a secondary alarm if exact source-derived membership remains authoritative. The diagnostic should include the stored `n_strata`, and a legitimate data change should require explicit adjudication rather than silently editing the expected constant.

**Not clean:** the oracle does not compare the full declared design metadata or `grinds`; this is P1-2. That is not a failure of implementation independence, but it is a scope gap in what the oracle is claimed to certify.

### 3.4 (d) Generated prose read as prose

**Round 9 geometry/favourability sentences: checked clean.**

The former “same side of zero,” exact-contact, wrong-bound, duplicated “both,” symmetric `±0.0005`, and signless “advantage is −0.394 pp” defects are corrected in the current rendered files.

**Not clean:** the central “no resolvable skill” synthesis is stronger than the declared analysis. This is P0-1.

**Not clean:** an active “earlier version…that was wrong” sentence remains, and the standalone caption deliverable narrates review/producer/test history. This is P2-1.

---

## 4. Prior-round closure matrix

| Round 9 item | Round 10 adjudication |
|---|---|
| P0-1 interval geometry and favourability | **Closed for current outputs.** Trinary relation, exact-contact flags, and bound direction render correctly. Residual contract gaps are new P1-2/P1-3 assurance findings, not a current numerical sentence error. |
| P0-2 abstract versus Monte Carlo sign audit | **Closed.** Numerical sign stability, endpoint sensitivity, and lack of calibrated coverage are now separated. |
| P1-1 audit scope | **Closed.** One exact target; separate lower/upper errors; no inheritance. |
| P1-2 endpoint rows fail closed | **Closed.** Missing, empty, malformed, keyless, duplicate, extra, non-finite, non-numeric, and retired-key mutations are explicitly covered. |
| P1-3 source membership independently bound | **Closed for exact membership.** The original swap defect is fixed. Full design-semantic binding remains incomplete and is P1-2 here. |
| P2-1 process leakage | **Partly closed, not accepted.** Supplement/captions are in the scan set, but line wrapping, canonical omission, limited path patterns, and caption preamble vocabulary still produce false greens. |
| P2-2 Figure 1 and Figure S3 visual semantics | **Closed.** Figure 1 uses distinct colour/style combinations; Figure S3 panel (b) uses neutral bars plus the zero line rather than undocumented threshold classes. |

---

## 5. Additional sections checked clean

### 5.1 Stale-number chain

**Checked clean.** I found no stale headline value in the manuscript, supplement, cover letter, front matter, or caption descriptions. The 8.44%, 8.83%, −0.394 pp, 62/132 count, endpoint sweep, full-precision primary ranges, and audit standard errors agree across the relevant surfaces.

### 5.2 Corpus completeness

**Checked clean.** The benchmark includes all 44 held-out coarse/fine records and all three named solutes, yielding 132 observations. The eight off-grid records are retained. Supplementary Table S7 contains 44 data rows and correctly escapes pipe-delimited primary cluster IDs for Markdown.

### 5.3 Endpoint quantity and units

**Checked clean.** The active submission surfaces consistently describe 38/40/42 **g** collected-mass endpoints. I found no active 38/40/42 mL regression. The settled flow/mass interpretation was not reopened.

### 5.4 Endpoint-row contract

**Checked clean.** The validator is now fail-closed over the row collection and reports malformed shapes rather than silently skipping validation. This correction is materially stronger than the Round 8 implementation.

### 5.5 Fitting-loss comparison

**Checked clean for current wording and numbers.** The primary and alternative point differences are nearly identical, their ranges both contain zero at the canonical draw count, and the current prose uses the typed relation rather than “same side” shorthand.

### 5.6 Figure semantics

**Checked clean.** Figure 1's evidence categories are distinguishable by both colour and line style, including in grayscale. Figure S3 panel (b) no longer assigns undocumented significance-like colours to correlation values. I did not identify a new figure-level scientific defect.

### 5.7 Table S7 width

The 44-row table parses cleanly as eight columns. I did not treat the unproofed journal-width layout as a defect because the brief identifies it as lower priority and the clean typeset source is explicitly pre-submission work.

### 5.8 Known-open and out-of-scope items

**Not re-reported.** Nothing in this review changes the status of the fraction-versus-measured-cup contrast, slow-lane coverage, hand-sourced design settings, author metadata, novelty search, DOI/tag, or final typesetting.

---

## 6. Stale-number assessment

**STALE-NUMBER CATEGORY: EMPTY.**

This is the second consecutive round in which the numerical values themselves are not the problem. The remaining risks are semantic and architectural:

- a central inference stronger than the declared analysis;
- two active manuscript versions with different central wording;
- unbound scientific meaning duplicated across artifact and renderer; and
- validators/scanners that certify only a subset of the facts their descriptions imply.

No finding in this report should be actioned by changing a headline number unless a new calibrated decision analysis is deliberately added under P0-1 Path B.

---

## 7. Ordered minimum acceptance checklist

### Gate 1 — Correct the central claim

- [ ] Select P0-1 Path A or Path B.
- [ ] Regenerate every editor/reviewer-facing surface from one accepted claim.
- [ ] Define or remove Supplementary Table S3's `skill` column.
- [ ] Add an inferential-status/decision-language guard.
- [ ] Read the abstract, headline, endpoint synthesis, conclusion, cover letter, and caption map continuously.

### Gate 2 — Restore one scientific source of truth

- [ ] Make canonical and venue abstracts materially agree.
- [ ] Generate both from one source or enforce normalized block parity.
- [ ] Run claim coverage against both by default.
- [ ] Add a central-claim drift mutation.

### Gate 3 — Bind the estimand and full design

- [ ] Introduce one structured estimand object with operands, operation, units, and favourable sign.
- [ ] Remove publication renderer defaults for favourability.
- [ ] Exact-validate all design/spec/derived/membership fields.
- [ ] Compare sample IDs, grinds, per-cluster counts, strata, size distributions, and hashes.
- [ ] Add full-checker mutations for all reproduced design false greens.

### Gate 4 — Make interval validation exact and typed

- [ ] Reject booleans, strings, NaN, and infinities.
- [ ] Require every semantic/display field and exact type.
- [ ] Rebuild and deep-compare the canonical interval record.
- [ ] Remove `bool(...)` coercion.
- [ ] Convert malformed records to named failures.
- [ ] Add field-deletion, contradictory-field, and invalid-bound mutations.

### Gate 5 — Remove process leakage and close scanner bypasses

- [ ] Replace the active “earlier version…was wrong” passage.
- [ ] Separate internal figure mapping from upload-ready captions.
- [ ] Scan normalized visible paragraphs with line mapping.
- [ ] Include canonical/source templates.
- [ ] Expand internal-path and review-history patterns.
- [ ] Add token-boundary line-wrap mutations.

### Gate 6 — Final verification

Run the brief's complete command chain after the corrections:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_consistency.py verify
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_model_contract.py \
                 tests/test_paper_a_figure_semantics.py -q
python -m pytest -q
```

Then perform a manual review of the rendered files. A green generator/text/consistency chain is necessary but not sufficient: Round 9 and this round both demonstrate false-green paths in assurance code.

---

## Appendix A — Focused mutation audit summary

The complete transcript is provided separately. The key reproduced results were:

```text
DESIGN VALIDATOR / SOURCE ORACLE
baseline: contract=[]; oracle=[]
estimand_reversed: contract=[]; oracle=[]
interval_kind_calibrated_CI: contract=[]; oracle=[]
nested_schema_version_999: contract=[]; oracle=[]
scheme_order_reversed: contract=[]; oracle=[]
scheme_role_wrong: contract=[]; oracle=[]
scheme_label_wrong: contract=[]; oracle=[]
scheme_strata_wrong: contract=[]; oracle=[]
scheme_cluster_key_wrong: contract=[]; oracle=[]
scheme_n_strata_wrong: contract=[]; oracle=[]
scheme_cluster_size_distribution_wrong: contract=[]; oracle=[]
scheme_rationale_wrong: contract=[]; oracle=[]
membership_grinds_wrong_with_refreshed_hash: contract=[]; oracle=[]

INTERVAL RECORD VALIDATOR
wrong_kind: []
wrong_width_pp: []
wrong_signed_nearest_bound_to_zero_pp: []
wrong_display_lower: []
wrong_display_upper: []
wrong_display_touches_zero: []
missing_excludes_on_containing_interval: []
missing_contains_on_excluding_interval: []
string_false_in_boolean_field: []
semantics_boolean_bound: ACCEPTED
semantics_string_bounds: ACCEPTED
semantics_positive_infinity: ACCEPTED

PROCESS-LANGUAGE SCANNER
scanner_problem_count=0
actual_visible_phrase_present_after_whitespace_collapse=True
```

The design results above are for the lower-level contract and independent oracle. The full artifact checker adds a separate exact-primary-scheme guard; no claim is made that changing the primary scheme passes that full checker.

---

## Appendix B — Suggested acceptance-oriented contract shape

A compact way to prevent the current duplication is to make the publication renderer consume one validated transfer-analysis object:

```json
{
  "schema_version": 4,
  "estimand": {
    "id": "pooled_mape_model_minus_level_only_pp",
    "metric": "MAPE",
    "left_operand": "mechanistic_model",
    "right_operand": "o_trained_level_only_comparator",
    "operation": "left_minus_right",
    "units": "percentage_points",
    "negative_values_favour": "mechanistic_model",
    "zero_means": "equal pooled MAPE"
  },
  "inferential_status": {
    "kind": "fixed_predictor_clustered_sensitivity",
    "calibrated_coverage": false,
    "supports_superiority_decision": false,
    "supports_equivalence_decision": false,
    "practical_margin_pp": null
  },
  "resampling_design": {
    "primary_scheme": "cond_in_variety",
    "scheme_order": [
      "cond_in_variety",
      "sample_in_variety_grind",
      "cond_in_group",
      "group"
    ],
    "schemes": "exact source-derived typed scheme objects"
  }
}
```

Publication helpers should accept this validated object rather than importing a separate default sign convention. Claim helpers can then enforce rules such as:

```python
if not status["supports_equivalence_decision"]:
    prohibit("equivalent", "no skill", "non-distinguishable")

if status["practical_margin_pp"] is None:
    prohibit("practically negligible", "no useful improvement")
```

The purpose is not to make prose robotic. It is to ensure that a sentence carrying a scientific decision cannot be generated from an artifact that explicitly says no such decision was performed.

---

## Final recommendation

The manuscript should not be submitted at commit `3b7fe7e10ee9989b380c70e40894d74b8ca2d8a5`.

The numerical and geometrical corrections are strong, and the paper's core methodological contribution remains viable. The quickest defensible route is P0-1 Path A: make the central conclusion explicitly evidence-limited — small observed incremental advantage, no established useful mechanistic transfer — while retaining the transparent uncalibrated sensitivity results. In parallel, close the three assurance gaps so the next round cannot again pass contradictory scientific meaning through a green chain.

After those changes, a focused re-review should concentrate on five questions only:

1. Does every central surface use the analysis-limited conclusion rather than categorical absence-of-skill language?
2. Are canonical and venue manuscripts materially aligned?
3. Can a reversed estimand or false design metadata still pass the full artifact/text chain?
4. Can any contradictory interval field or invalid bound still pass validation?
5. Does the publication scan catch line-wrapped history and internal paths in every upload-facing file?

If all five are closed without moving the verified numbers, the Round 10 science and assurance blockers will be resolved.
