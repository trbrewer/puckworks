# Paper 1 — Detailed Review, Round 8

**Reviewer:** Detailed Review  
**Review target:** commit [`21b138a1fa8866db0b65c59b541b766498e63ed4`](https://github.com/trbrewer/puckworks/tree/21b138a1fa8866db0b65c59b541b766498e63ed4)  
**Primary manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`  
**Figures and captions:** `docs/submission/figures/`, `docs/figures/paper_a/`, and `docs/figures/PAPER_A_CAPTIONS.md`  
**Review brief:** `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md`

## Executive verdict

**Not ready for submission.**

Round 8 has corrected the three central scientific-contract defects identified in Round 7 in the main manuscript: the Reynolds definition is now consistent with the executable model, the collection endpoint is correctly expressed in grams, and the headline transfer benchmark now uses the complete coarse/fine corpus. The paper is consequently much closer to a defensible submission.

However, the reviewed commit still contains **three submission-blocking propagation or method-description failures**:

1. the separately submitted Figure 3 caption still reports the superseded 108-point benchmark and its old values;
2. the general Methods section still declares the superseded within-solute cluster as the **primary** resampling unit, contradicting the Results, Table 5, producer and archived analysis; and
3. the submission package and release-time consistency gate still encode the retired mL endpoint contract, with the gate looking for an obsolete JSON key and therefore unable to validate the corrected endpoint artifact.

The most important substantive issue below those blockers is the treatment of dependence and the knife-edge clustered range. The selected primary resampling unit is a defensible conservative sensitivity choice, but the manuscript overstates it as the experiment's demonstrated “actual dependence structure.” Eight of the 26 condition clusters contain one held-out grind, not both, and C and F at the same temperature and pressure are separate espresso samples rather than a single experimental unit. The paper also says both secondary ranges are narrower than the primary, but the whole-group range is actually wider. These are not reasons to discard the analysis; they are reasons to name it more accurately and stop drawing inferential conclusions from a deliberately non-calibrated sensitivity range.

I do **not** find persuasive evidence that the authors are hiding a material real effect behind rounding. The point estimate is consistently small and in the same direction across endpoint and fitting-loss sensitivities. But the present chain also cannot support the categorical language “not robustly distinguishable from zero”: the primary 40 g upper quantile is negative at full precision (`−0.0004 pp`), the decision flag is made only after rounding it to displayed zero, a reasonable alternative fitting loss moves the displayed bound to `−0.002 pp`, and the range is explicitly not a calibrated confidence interval. The correct conclusion is descriptive and practical, not hypothesis-testing: **the mechanistic model shows at most a small incremental advantage over the level-only comparator, and the sign of a fourth-decimal resampling boundary is not scientifically dispositive.**

### Finding count

| Priority | Count | Submission effect |
|---|---:|---|
| **P0 — submission-blocking** | **3** | Must be corrected before a journal package is assembled |
| **P1 — major** | **5** | Must be corrected or explicitly adjudicated before submission |
| **P2 — editorial/governance** | **2** | Correct in the same revision |
| **Confirmed stale-number findings** | **2** | Figure 3 caption; Round 8 brief coverage count |

---

## Scope, evidence and execution status

The review followed the Round 8 brief's requested adversarial emphasis: semantic mismatches not caught by the new contracts; prose contradicted by the corpus; evidence tiers exceeding the design; figure geometry; producer/documentation divergence; and the `−0.394 pp` knife-edge.

I inspected the commit-pinned manuscript, supplement, caption file, submission-package record, semantic-contract tests, consistency gate, slow-lane binding definitions, transfer and endpoint artifacts, the Angeloni corpus, and the supplied figures. I also performed independent static checks of:

- all 66 Angeloni condition records and the complete 44-record C/F subset;
- the membership and size of each `(variety, T, p)` cluster;
- the widths of all three archived clustered ranges;
- the regular expression used by the interval-precision contract; and
- the relationship among the endpoint artifact's schema, the release gate's expected schema and the submission package's prose.

### Requested command status

A complete repository checkout could not be obtained in the execution environment because outbound GitHub access from the container failed at DNS resolution. Therefore, I **did not rerun** the five commands requested by the brief and do not represent them as passing or failing here.

| Requested command | Status in this review |
|---|---|
| `python -m puckworks.paper_a.slow_lane_bindings` | **Not rerun**; inspected binding source and generated audit instead |
| `python tools/paper_a_consistency.py verify` | **Not rerun**; inspected the exact consistency source |
| `python tools/claim_binding_audit.py` | **Not rerun**; inspected the generated audit and its source |
| `python -m pytest tests/test_paper_a_model_contract.py -q` | **Not rerun**; inspected all relevant test definitions and adversarially evaluated their predicates |
| `python -m pytest tests/test_cross_paper_number_audit.py -q` | **Not rerun**; Papers B2 and 3 otherwise remained out of scope |

The P0 findings below do not depend on a test run: they are direct contradictions within the commit. The acceptance criteria require the repository's own full command suite to be rerun after correction.

---

## Findings at a glance

| ID | Priority | Finding | Stale number? |
|---|---|---|---|
| P0-1 | P0 | Separately submitted Figure 3 caption still describes the superseded 108-point benchmark | **Yes** |
| P0-2 | P0 | General Methods names the wrong primary resampling unit and omits the third scheme | No |
| P0-3 | P0 | Submission package and release gate still encode 38/40/42 mL and an obsolete `v_targets` schema | No — stale unit/schema |
| P1-1 | P1 | Primary dependence unit is overstated as the demonstrated design unit; corpus is unbalanced and cross-grind pairing is not a sample-level dependency | No |
| P1-2 | P1 | Knife-edge classification is made after rounding and supports no calibrated “distinguishable” conclusion | No |
| P1-3 | P1 | Interval-precision semantic contract does not inspect the primary interval it claims to bind | No |
| P1-4 | P1 | Corpus semantic contract does not compare manuscript claims with the emitted sample-ID manifest | No |
| P1-5 | P1 | Figure 1's arrow geometry serializes two analyses that use different calibrations and are not upstream/downstream | No |
| P2-1 | P2 | Round 8 brief says 11 of 95 slow-lane values are unbound; generated audit says 6 | **Yes** |
| P2-2 | P2 | Supplementary Figure S3 has overlapping panel titles and is not publication-ready | No |

---

# P0 — Submission-blocking findings

## P0-1. The separately submitted Figure 3 caption is stale and describes the superseded 108-point benchmark

### Finding

The current manuscript and archived complete-corpus analysis report:

- **132** held-out observations;
- model pooled MAPE **8.44 %**;
- level-only comparator MAPE **8.83 %**; and
- model worse on **62 of 132** observations.

The actual transfer figure also displays the complete-corpus result. But the separately submitted caption still says:

- **108** observations;
- model MAPE **8.2 %**;
- comparator MAPE **8.6 %**; and
- model worse on **50 of 108** observations.

Those are the old matched-on-grid-subset values, not the adopted complete-corpus headline. The journal package explicitly says captions are supplied separately, so a correct plotted image and correct manuscript do not cure a stale caption.

### Evidence relied on

- [`PAPER_A_CAPTIONS.md`, Figure 3](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/figures/PAPER_A_CAPTIONS.md): 108, 8.2 %, 8.6 %, 50/108.
- [`PAPER_A_JFE_MANUSCRIPT.md`, principal benchmark](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): 132, 8.44 %, 8.83 %, 62/132 and explicit complete-corpus membership.
- [`PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json): complete-corpus artifact with 44 C/F records and 132 named-solute observations.
- Visual inspection of the committed transfer figure: the figure itself carries the updated complete-corpus values.

### Why this matters

This is a direct contradiction in the submission-facing package. It can cause a reviewer to infer that the figure excludes the eight off-grid validation records even though the manuscript now makes their inclusion a central methodological correction. It also demonstrates that the new corpus assurance does not reach every submission component.

### Minimum acceptance criterion

1. Regenerate the Figure 3 caption from the same complete-corpus artifact as the figure and manuscript.
2. State **132 observations, 8.44 %, 8.83 %, and 62/132** at the paper's chosen display precision.
3. If the 108-point matched-grid result is retained in the caption, label it explicitly as a **secondary on-grid sensitivity**, not as the plotted headline corpus.
4. Add captions to the corpus semantic contract and bind the count and sample-set fingerprint, not just a phrase.
5. Rerun the submission consistency suite and inspect the rendered caption file.

### Stale-number status

**Confirmed stale-number finding.** I compared the caption with the current complete-corpus producer artifact, current manuscript and plotted figure.

---

## P0-2. The general Methods section still declares the superseded resampling method

### Finding

The general Methods section says the model-versus-comparator analysis uses **two** clustering schemes and identifies “conditions within a solute × variety group” as the **primary** unit. That is the Round 7 method.

The current producer, endpoint artifact, Results and Table 5 instead use **three** schemes:

1. **Primary:** `(variety, temperature, pressure)` condition, implemented as `cond_in_variety`;
2. Secondary: condition within variety × solute, `cond_in_group`; and
3. Secondary: whole variety × solute group, `group`.

The contradiction is not a harmless terminology difference. A reader implementing the Methods as written will reproduce the secondary range `[−0.742, −0.044]`, not the primary headline range `[−0.825, +0.000]`.

### Evidence relied on

- [`PAPER_A_JFE_MANUSCRIPT.md`, Methods §2.5](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): two schemes; within-solute condition cluster labelled primary.
- [`PAPER_A_JFE_MANUSCRIPT.md`, Results](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): `(variety,T,p)` declared primary, followed by two secondary schemes.
- [`angeloni_bracket.py`, `paired_clustered_bootstrap`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/puckworks/validation/slow/angeloni_bracket.py): three units and `cond_in_variety` default/primary.
- [`PAPER_A_ENDPOINT_PROPAGATION.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json): `"primary_cluster": "cond_in_variety"`.
- [`PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json): 26, 78 and 6 clusters for the three schemes and their distinct ranges.

### Why this matters

The resampling method underpins the paper's principal comparative claim and the “reaches zero” interpretation. Reproducibility requires one unambiguous primary unit in the Methods, Results, supplement, producer and artifact. A method contradiction at this boundary is submission-blocking even when the printed numbers happen to match the producer.

### Minimum acceptance criterion

1. Rewrite §2.5 to describe all three schemes and name `cond_in_variety` as primary.
2. State the exact cluster keys, number of clusters and handling of unbalanced cluster sizes.
3. Explain that the predictors are fixed and are **not refitted** inside this resampling.
4. Generate the Methods summary or a machine-readable method table from the producer configuration so a later priority change cannot leave the general Methods stale.
5. Add a semantic contract that parses or otherwise binds the Methods statement—not only a synthetic test of the producer's behavior.

### Stale-number status

Not a stale number. This is a stale **method description** that would reproduce a different current number.

---

## P0-3. The submission package and release-time gate still encode the retired mL endpoint contract

### Finding

The main manuscript, supplement and caption prose correctly use 38/40/42 **g**, and the endpoint artifact correctly stores an `m_targets` array and `m_target_g` rows. Yet two control-plane components remain on the retired volume contract:

- `docs/submission/PAPER_A_JFE_PACKAGE.md` says the “38/40/42 mL endpoint propagation” is complete.
- `tools/paper_a_consistency.py` checks the artifact for `v_targets` and emits mL-specific failure messages.

Because the actual artifact uses `m_targets`, the release-time `submission` mode cannot validate the corrected artifact as written; it will diagnose a missing 38/40/42 mL sweep even when the correct gram-based sweep is present. The regular `verify` mode does not include `_release_state`, so this stale contract can coexist with a green ordinary consistency run.

A second brittle condition in the same gate requires the literal phrase “not endpoint-invariant” when `conclusion_stable` is false. The manuscript communicates the endpoint behavior numerically and in other wording, while that exact phrase appears in the supplement rather than necessarily in the conversion. A release gate should bind the declared endpoint interpretation semantically, not demand one magic string.

### Evidence relied on

- [`PAPER_A_JFE_PACKAGE.md`, line 15](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_PACKAGE.md): retired 38/40/42 mL wording.
- [`paper_a_consistency.py`, `_release_state`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tools/paper_a_consistency.py): searches for `v_targets`, emits mL messages and checks a literal phrase.
- [`paper_a_consistency.py`, modes](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tools/paper_a_consistency.py): release checks run only in `submission`, not `verify`.
- [`PAPER_A_ENDPOINT_PROPAGATION.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json): correct `m_targets` schema; rows use `m_target_g`.

### Why this matters

This reopens the settled endpoint issue only in the **submission-control layer**, not in the corrected science. It creates both kinds of assurance failure:

- a false negative at release time, because the gate rejects the correct schema; and
- a false sense of coverage in normal development, because the command named in the brief is `verify`, which omits the stale release check.

The package itself is submission-facing and must not reintroduce the exact unit error the Round 7 correction was intended to remove.

### Minimum acceptance criterion

1. Change the package record to **38/40/42 g**.
2. Change `_release_state` to require `m_targets == [38.0, 40.0, 42.0]` and `m_target_g` rows.
3. Replace every mL-specific gate message with gram-specific wording.
4. Replace the literal-phrase requirement with an artifact-bound semantic check, for example confirming that the manuscript reports the three endpoint rows and does not claim invariant zero-crossing when the artifact says otherwise.
5. Add a test that exercises `paper_a_consistency.py submission` against the actual committed artifact.
6. Make the release-state test part of the routine CI suite even if unresolved author metadata is separately allow-listed during development.

### Stale-number status

The numbers 38/40/42 are current; their **unit and schema are stale**. This is not counted as a stale-number finding.

---

# P1 — Major findings

## P1-1. The primary cluster is a conservative sensitivity choice, not the demonstrated “actual dependence structure”

### Finding

The Results and producer docstring say every `(variety,T,p)` condition is observed for all three solutes at both held-out grinds and that moving those six observations together represents the design's “actual dependence structure.” The first part is contradicted by the corpus, and the second is stronger than the experimental design establishes.

An independent audit of `bioactives.csv` gives:

| Corpus property | Audited value |
|---|---:|
| C/F condition-level records | 44 |
| Named-solute observations | 132 |
| Distinct `(variety,T,p)` clusters | 26 |
| Clusters containing both C and F | 18 |
| Observations in each two-grind cluster | 6 |
| Clusters containing one grind only | 8 |
| Observations in each one-grind cluster | 3 |

The eight singleton-grind clusters are `A21`, `A22`, `A32`, `A33`, `R21`, `R22`, `R32`, and `R33`. The manuscript eventually acknowledges that the off-grid records exist at one grind only, but this directly contradicts the immediately preceding universal statement that every condition has both grinds.

More importantly, the source describes 33 separate espresso-coffee samples per variety: 27 grid samples plus six additional samples, with all extractions duplicated. The three solutes measured from one sample have a clear shared-sample dependency. C and F observations at the same nominal `(T,p)` are separate EC samples and are not identified as paired replicates of one experimental unit. Shared coffee, machine and campaign may create correlation across them, but the design does not identify the cross-grind `(variety,T,p)` cluster as uniquely “actual.” It is better presented as a deliberately conservative campaign-structure sensitivity.

The manuscript also says both secondary ranges are narrower than the primary. The archived widths are:

| Unit | Range | Width (pp) | Relative to primary |
|---|---:|---:|---|
| `(variety,T,p)` primary | `[−0.825, 0.000]` | **0.825** | — |
| condition within variety × solute | `[−0.742, −0.044]` | **0.698** | narrower |
| whole variety × solute group | `[−0.883, −0.024]` | **0.859** | **wider**, not narrower |

Accordingly, the proposed explanatory sentence—dropping a real dependence manufactures precision—does not explain the whole-group result and should not be attached to both sensitivities.

### Evidence relied on

- [`PAPER_A_JFE_MANUSCRIPT.md`, Results](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): universal both-grind claim, “actual dependence structure,” ranges and “both narrower.”
- [`angeloni_bracket.py`, docstring and implementation](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/puckworks/validation/slow/angeloni_bracket.py): repeats the universal and “actual” claims; implementation permits unbalanced clusters.
- [`PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`, resampling block](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json): ranges and cluster counts.
- `puckworks/data/angeloni2023/bioactives.csv`: manual membership audit described above.
- Angeloni et al. source methods: 27 grid EC samples plus six additional EC samples per variety; extractions performed in duplicate.

### Why this matters

The range touching zero is driven by the selected cluster structure. That makes the rationale for the unit part of the scientific claim, not implementation detail. Overstating an assumed conservative unit as the observed experimental unit makes the central interpretation look more statistically grounded than it is.

### Minimum acceptance criterion

1. Replace the universal six-observation statement with the actual cluster composition: 18 six-observation clusters and eight three-observation clusters.
2. Describe `cond_in_variety` as a **predeclared conservative sensitivity unit** that keeps same-condition cross-solute outcomes together and additionally couples same-condition C/F samples where both exist.
3. Remove “actual dependence structure” unless a source-level sampling hierarchy establishes it.
4. Correct “both are narrower”: report the actual widths and explain each sensitivity separately.
5. Add at least one sample-record-based or grind-within-condition alternative, or provide a clear design argument for why the current three units adequately bracket plausible dependencies.
6. Archive the cluster membership—not merely the cluster count—so the resampling design is auditable.

### Stale-number status

No. The archived ranges are current; the prose description and interpretation of their units are wrong.

---

## P1-2. The knife-edge is classified after rounding, while the prose uses inferential language the procedure cannot support

### Finding

At 40 g, the primary range is printed as `[−0.825, +0.000] pp`, but the Round 8 brief records the full-precision upper quantile as **`−0.0004 pp`**. The producer intentionally rounds both endpoints to three decimals **before** setting `excludes_zero`; it then archives only the rounded interval plus an unsigned distance to zero.

This design avoids a printed `−0.000`/boolean contradiction, but it mixes presentation precision with analytical classification. The underlying full-precision range does not reach zero at 40 g; the displayed range does. At 42 g, the artifact stores a displayed upper bound of zero and an unsigned nearest-bound distance of `0.0003 pp`, but not the signed full-precision bound needed to reconstruct what occurred. The endpoint artifact itself says:

- sign of the point difference is stable;
- the primary range does **not** cross zero at every endpoint; and
- the overall conclusion flag is not stable.

The fitting-loss robustness artifact reinforces that the zero boundary is not a stable analytical result: the primary fit gives `[−0.825, 0.000]`, while the alternative fit gives `[−0.827, −0.002]`; the point estimate barely changes (`−0.394` to `−0.393 pp`), but the displayed zero-crossing flips.

The manuscript correctly insists these are not calibrated confidence intervals, yet then says the advantage is “not robustly distinguishable from zero” and gives an “inferential reading.” “Distinguishable” ordinarily implies an inferential standard. A fixed-predictor clustered percentile sensitivity range with no fitted-model repetition and no calibrated coverage cannot establish either statistical distinguishability or statistical non-distinguishability.

### Adjudication requested by the brief

I do **not** conclude that a meaningful effect is being hidden. The evidence supports a smaller and more precise statement:

- the point difference is consistently favorable to the mechanistic model but small in magnitude;
- it remains around `−0.4 pp` across endpoint and fitting-loss choices;
- the location of a resampling percentile boundary relative to zero is unstable at the third/fourth decimal and depends on clustering and fitting loss; and
- no population-level or repeated-sampling inference follows from the chosen sensitivity range.

A suitable replacement could be:

> At 40 g, the full-precision upper clustered bootstrap quantile was −0.0004 percentage points, displayed as 0.000 at the reporting precision. Because this is a fixed-predictor clustered sensitivity range rather than a calibrated confidence interval, neither the sign of its fourth decimal nor its rounded contact with zero is treated as inferential evidence. The mechanistic model's observed advantage was small (−0.394 percentage points) and stable in sign across the 38–42 g endpoint sweep, but no claim of material incremental skill is made.

### Evidence relied on

- [`PAPER_1_REVIEW_BRIEF_ROUND_8.md`, knife-edge](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md): full-precision `−0.0004 pp` and requested adjudication.
- [`angeloni_bracket.py`, rounding and decision](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/puckworks/validation/slow/angeloni_bracket.py): decision made from `rlo/rhi` after rounding.
- [`PAPER_A_ENDPOINT_PROPAGATION.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json): endpoint rows and `sign_is_stable`, `primary_range_crosses_zero_at_every_endpoint`, `conclusion_stable` flags.
- [`PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json`](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json): zero-crossing changes under alternative fitting loss while point estimate is stable.
- [`PAPER_A_JFE_MANUSCRIPT.md`, comparison interpretation](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): “not robustly distinguishable” and explicit non-CI caveat.

### Why this matters

The paper's core scientific message is that endpoint fit should not be overinterpreted as mechanistic transfer. That argument is strongest when it does not itself overinterpret a non-calibrated resampling boundary. Keeping full precision, display precision and inferential status separate would make the paper more—not less—skeptical and defensible.

### Minimum acceptance criterion

1. Archive full-precision signed lower and upper quantiles in addition to display-rounded values.
2. Determine all analytical flags from full-precision values; keep a separate `display_touches_zero` field if useful.
3. Report Monte Carlo stability across multiple seeds and/or a larger `B`, especially for the fourth-decimal upper quantile.
4. Remove “inferential reading” and “distinguishable” unless a calibrated inferential procedure is introduced.
5. State the practical effect size directly and, ideally, predeclare a smallest effect size of practical interest or equivalence margin.
6. Treat the endpoint and fitting-loss zero-crossing changes as sensitivity information, not as binary evidence for or against an effect.

### Stale-number status

No. This is a precision, classification and interpretation defect.

---

## P1-3. The interval-precision contract does not inspect the primary interval it claims to bind

### Finding

The semantic test named `test_primary_range_is_rendered_at_one_precision_everywhere` searches for this pattern:

```text
\[[−-]0\.7\d+,\s*[+−-]?0\.0\d+\]
```

That pattern can match lower bounds in the `−0.700` to `−0.799` range. It **cannot match the primary lower bound `−0.825`**. In the reviewed prose it instead matches secondary ranges such as `[−0.742, −0.044]`; if there were no matches, the test would also pass because an empty set produces no mixed precision.

My static evaluation found:

- the primary string `[−0.825, +0.000]` occurs repeatedly in the manuscript;
- the test's pattern matches the secondary `[−0.742, −0.044]` in the manuscript and related 0.7xx intervals in the supplement; and
- the test never proves that the primary interval exists, is sourced from the artifact, or has one precision across the required files.

The brief therefore overstates this contract when it says one interval is bound across manuscript and supplement.

### Evidence relied on

- [`test_paper_a_model_contract.py`, interval test](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tests/test_paper_a_model_contract.py).
- [`PAPER_A_JFE_MANUSCRIPT.md`, primary and secondary ranges](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md).
- Independent regex evaluation against the four paths in the test's `PROSE` tuple.

### Why this matters

This is the precise “false assurance” failure mode the Round 8 brief asks the reviewer to find. A green test named for the primary interval can coexist with arbitrary drift in the primary interval because it is selecting the wrong text.

### Minimum acceptance criterion

1. Load the current primary range from `PAPER_A_ENDPOINT_PROPAGATION.json` rather than hard-coding a numeric regex family.
2. Format the expected range through the production formatter.
3. Require at least one expected occurrence in every file where the interval is supposed to appear.
4. Reject unapproved alternative renderings of that same artifact value.
5. Add mutation tests for:
   - changed primary lower bound;
   - changed upper-bound precision;
   - primary interval removed entirely; and
   - secondary interval changed while primary remains correct.

### Stale-number status

No. The displayed value is current; the contract is mis-targeted.

---

## P1-4. The corpus semantic contract does not bind the manuscript to the emitted sample-ID manifest

### Finding

The Round 8 brief says the new contracts bind “the declared corpus against the sample-ID manifest the producer emits.” The reviewed test file does establish that eight off-grid C/F records exist and that they have no optimal-grind counterparts. But the manuscript-facing corpus test only scans sentences containing “coarse/fine” and forbids the phrase “all of it.”

It does **not**:

- load the current complete-corpus artifact;
- compare the manuscript's stated count with `n_observations`;
- compare included or excluded sample IDs;
- require the complete-corpus estimand; or
- inspect the separate caption that is in fact stale.

The old 108-point failure could recur with different prose and still pass. The current stale Figure 3 caption is a live demonstration of the gap.

### Evidence relied on

- [`test_paper_a_model_contract.py`, corpus tests](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tests/test_paper_a_model_contract.py): record-existence checks followed by a phrase-only manuscript check.
- [`PAPER_A_ENDPOINT_PROPAGATION.json`, corpus manifest](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json): explicit held-out IDs, excluded IDs, counts and lookup-undefined IDs.
- P0-1 above: stale caption passes outside the claimed corpus binding.

### Why this matters

The semantic layer was introduced specifically because value-level checks can certify a correct number for an undeclared subset. A phrase prohibition does not bind the estimand or its membership and therefore does not close that failure mode.

### Minimum acceptance criterion

1. Read the committed corpus artifact in the test.
2. Bind at least:
   - estimand name;
   - `include_off_grid`;
   - `n_held_out_records`;
   - `n_observations`;
   - sorted included sample IDs; and
   - sorted excluded sample IDs.
3. Require all submission-facing files, including captions and package text, to agree with the adopted corpus.
4. Add mutation tests that remove one off-grid ID, change 132 to 108, or alter the included/excluded sets while preserving counts.

### Stale-number status

No. This is an assurance-coverage defect exposed by a separate stale caption.

---

## P1-5. Figure 1's plotted dependency geometry is inconsistent with the analyses it depicts

### Finding

The Figure 1 caption says arrows show actual data and parameter dependency rather than merely analysis order. The figure then draws a serial path:

`Angeloni optimal-grind target recalibration` → `held-out optimal-grind LOCO` → `coarse/fine cross-grind holdout`.

That geometry implies the cross-grind holdout depends on the output of the LOCO analysis. It does not:

- LOCO repeatedly fits on eight of nine O conditions and predicts the omitted O condition.
- The C/F transfer benchmark fits once on all nine O conditions and freezes that full calibration for C/F prediction.

They are parallel children of the Angeloni O dataset/target-recalibration procedure, with different calibration instances. The cross-grind holdout must not descend from the held-out-LOCO box if arrows are claimed to encode actual dependency.

### Evidence relied on

- [`PAPER_A_CAPTIONS.md`, Figure 1](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/figures/PAPER_A_CAPTIONS.md): explicitly says arrows show actual dependency.
- Visual inspection of `docs/figures/paper_a/fig1_design.png`: serial arrow from target recalibration through LOCO to C/F holdout.
- [`PAPER_A_JFE_MANUSCRIPT.md`, transfer contract](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): C/F prediction uses target-specific O calibration and frozen parameters.
- [`PAPER_A_JFE_MANUSCRIPT.md`, Table 5 and LOCO discussion](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md): LOCO/refit and fixed-predictor transfer are distinct estimands.

### Why this matters

The figure is the paper's study-design map and is likely to be the first object many readers use to understand evidence flow. The current geometry can make the within-campaign evidence look like a sequential validation pipeline when the analyses are parallel and share data context.

### Minimum acceptance criterion

1. Branch LOCO and C/F transfer separately from the Angeloni O dataset/recalibration node.
2. Label the LOCO branch “8/9 O fit per fold” and the C/F branch “9/9 O fit once; frozen for C/F.”
3. Retain the external trajectory as a separate branch from source kinetics, not from Angeloni target calibration.
4. Add a figure-structure assertion at the source-data level if the diagram is generated programmatically; at minimum, review the rendered geometry manually as a release checklist item.

### Stale-number status

No. This is a figure-geometry defect.

---

# P2 — Editorial and governance findings

## P2-1. The Round 8 brief's slow-lane count is stale and internally inconsistent

### Finding

The brief reports **89 bound** and **11 of 95 unbound**. The generated claim-binding audit at the same commit reports:

- 95 registered;
- 89 bound and matching;
- 0 mismatched;
- 0 unresolvable;
- 0 declared unbindable; and
- **6 still unbound**.

The brief's 89 + 11 also sums to 100 rather than 95. This is not one of the known open items to re-report unchanged: the requested exception applies because the number is **wrong**.

### Evidence relied on

- [`PAPER_1_REVIEW_BRIEF_ROUND_8.md`, coverage](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md) and known-open-item repetition.
- [`CLAIM_BINDING_AUDIT.md`, slow lane](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/CLAIM_BINDING_AUDIT.md): 89 bound, 6 unbound.
- `puckworks/paper_a/slow_lane_bindings.py`: `UNBINDABLE` is empty and comments record the updated state.

### Why this matters

The brief correctly warns that its assurances are fallible; this is another concrete instance. Hard-coded review-brief coverage values are especially likely to drift because the generated audit is updated independently.

### Minimum acceptance criterion

1. Change the brief to **6 of 95** unbound.
2. Generate or splice coverage figures from `binding_coverage()` or `CLAIM_BINDING_AUDIT.md` rather than retyping them.
3. Add an arithmetic assertion that bound + unbound + mismatch/unresolvable categories equal the registered total.

### Stale-number status

**Confirmed stale-number finding.** I compared the brief with the generated audit at the reviewed commit.

---

## P2-2. Supplementary Figure S3 has overlapping panel titles

### Finding

In Supplementary Figure S3 (`fig7_per_group_diagnostics.png`), the long titles for panels (a) and (b) collide across the central margin. The overlap obscures the end of the panel-(a) title and beginning of panel-(b) title. The global title also occupies substantial vertical space, leaving a cramped hierarchy.

### Evidence relied on

- Visual inspection of the committed figure at the target commit.

### Why this matters

The data remain readable, but the layout is below publication quality and makes a complex diagnostic unnecessarily difficult to parse.

### Minimum acceptance criterion

1. Shorten the panel titles and move explanatory detail to the caption.
2. Increase the inter-panel gap or render each panel as a separate image.
3. Recheck at the journal's intended single- or double-column print width, not only full-screen size.

### Stale-number status

No.

---

# Sections checked and found clean or materially improved

The brief asks that “checked and clean” be distinguished from “not reached.” The following areas were reached and did not produce an additional finding, subject to the command-execution limitation stated above.

## Governing-model contract

- **Reynolds definition:** the current manuscript displays the superficial-velocity form and the equivalent interstitial-velocity form with the correct porosity factor. I found no new evidence to reopen the scientific equation itself.
- **Endpoint mass unit in the main scientific package:** manuscript, supplement and caption prose use grams; the remaining defect is confined to the submission-package status line and release gate identified in P0-3.
- **Flow/density source fidelity:** no new evidence contradicts the settled source contract.

## Corpus and comparator

- The headline transfer analysis now uses all **44 C/F records / 132 named-solute observations**, including the eight off-grid records.
- The on-grid and off-grid sensitivities are separately disclosed.
- The same-`(T,p)` lookup comparator is appropriately demoted to the 108-observation matched-grid support on which it is defined; I found no stronger reason to make it the headline comparator.
- The level-only comparator is clearly described as O-trained, frozen, response-free and deliberately weak rather than a statistical null. That framing is adequate once the non-inferential language in P1-2 is corrected.

## Identifiability and objective-family methods

- The supplement now distinguishes ordinary least squares, weighted least squares and IRLS for the objective-specific level optimizers.
- The paper consistently separates profile tolerance sets from confidence regions.
- The distinction among parameter localization, absolute prediction error, benchmark skill and evidence tier is a genuine strength of the manuscript.

## Evidence hierarchy and external trajectory

- The C/F benchmark is correctly labelled a within-campaign cross-grind holdout, not external validation.
- The external Waszkiewicz trajectory is presented as a different rig/coffee with target-specific level profiling and frozen source kinetics.
- Limitations on the external panel—one coffee/grind, TDS as an aggregate proxy, high and loss-dependent error, and level refitting—are stated clearly.
- The known fraction-versus-measured-cup profile contrast remains explicitly deferred; I did not re-report it as a finding.

## Figures

- The current transfer figure is numerically concordant with the complete-corpus artifact; only its separate caption is stale.
- Figures 2, 3 (LOCO plot), 4, S1, S2 and S4 were visually inspected and were broadly legible and consistent with their stated purpose.
- No additional embedded mL endpoint label was observed in the reviewed figure set.

## Scope exclusions respected

I did not report missing author metadata, CRediT roles, funding, competing interests, generative-AI declaration, novelty-search status, release DOI/tag or draft-history prose. Papers B2 and 3 were not substantively reviewed.

---

# Ordered acceptance checklist

The following is the minimum effective path to a submission-ready Round 8 correction.

## Gate A — Correct submission-facing contradictions

1. Regenerate the Figure 3 caption from the complete-corpus artifact.
2. Rewrite the general Methods resampling paragraph to match the producer and Table 5.
3. Correct `PAPER_A_JFE_PACKAGE.md` from mL to g.
4. Correct `_release_state` to read `m_targets`/`m_target_g`, and exercise `submission` mode in CI.

## Gate B — Repair the central resampling interpretation

5. State the actual 26-cluster composition: 18 two-grind clusters and eight one-grind clusters.
6. Reframe the primary unit as a conservative sensitivity assumption, not the uniquely demonstrated experimental unit.
7. Correct the range-width comparison and remove the claim that both secondary ranges are narrower.
8. Archive full-precision signed percentile bounds separately from display-rounded bounds.
9. Remove inferential “distinguishable” language unless a calibrated inference is supplied; report practical effect magnitude and sensitivity instead.

## Gate C — Make the semantic contracts test what their names claim

10. Bind the primary interval directly to the endpoint artifact and require non-empty expected occurrences.
11. Bind corpus count and sample-ID membership across manuscript, supplement, captions and package.
12. Add adversarial mutation tests for the stale-caption, wrong-primary-unit, wrong-endpoint-key, missing-ID and empty-regex cases.

## Gate D — Presentation and final verification

13. Redraw Figure 1 as parallel LOCO and C/F branches with explicit calibration scopes.
14. Fix Supplementary Figure S3 title overlap at publication scale.
15. Regenerate the Round 8 brief's coverage count from the live audit.
16. Run and archive the outputs of all five commands in the brief, plus:

```bash
python tools/paper_a_consistency.py submission
```

17. Perform a final rendered-package audit comparing manuscript, supplement, standalone captions and every figure against the same current artifacts.

---

# Appendix A — Independent corpus audit

Using `puckworks/data/angeloni2023/bioactives.csv`:

| Variety | Temperature (°C) | Pressure (bar) | Grind present | Sample | On grid? |
|---|---:|---:|---|---|---|
| Arabica | 89 | 10 | C only | A21 | No |
| Arabica | 97 | 7 | C only | A22 | No |
| Arabica | 90 | 8 | F only | A32 | No |
| Arabica | 95 | 11 | F only | A33 | No |
| Robusta | 97 | 7 | C only | R21 | No |
| Robusta | 89 | 10 | C only | R22 | No |
| Robusta | 95 | 11 | F only | R32 | No |
| Robusta | 90 | 8 | F only | R33 | No |

All 18 on-grid `(variety,T,p)` clusters contain both C and F. The eight off-grid clusters contain one grind. Consequently, the primary cluster-size distribution is 18 clusters of six named-solute observations and eight clusters of three.

---

# Appendix B — Assurance-layer failure demonstrations

## B1. Interval regex

Current test pattern:

```regex
\[[−-]0\.7\d+,\s*[+−-]?0\.0\d+\]
```

Expected headline interval:

```text
[−0.825, +0.000]
```

The expected lower bound starts `0.8`, so the pattern cannot select it. The test instead selects 0.7xx secondary ranges or passes vacuously if none are present.

## B2. Endpoint schema

Committed artifact:

```json
{
  "m_targets": [38.0, 40.0, 42.0],
  "rows": [{"m_target_g": 38.0}, {"m_target_g": 40.0}, {"m_target_g": 42.0}]
}
```

Release gate expectation:

```python
ep.get("v_targets", []) == [38.0, 40.0, 42.0]
```

The gate is therefore stale by construction.

## B3. Range widths

```text
primary cond_in_variety:  0.000 - (−0.825) = 0.825 pp
secondary cond_in_group: −0.044 - (−0.742) = 0.698 pp
secondary whole group:   −0.024 - (−0.883) = 0.859 pp
```

Only the within-solute condition range is narrower than primary.

---

# Appendix C — Principal repository evidence

- [Round 8 brief](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md)
- [Main manuscript](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)
- [Supplement](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)
- [Standalone captions](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/figures/PAPER_A_CAPTIONS.md)
- [Submission package](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/submission/PAPER_A_JFE_PACKAGE.md)
- [Semantic-contract tests](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tests/test_paper_a_model_contract.py)
- [Consistency gate](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/tools/paper_a_consistency.py)
- [Transfer/endpoint producer](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/puckworks/validation/slow/angeloni_bracket.py)
- [Endpoint propagation artifact](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json)
- [Transfer corpus artifact](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json)
- [Comparator-loss robustness artifact](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/paper1_resource/PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json)
- [Generated claim-binding audit](https://github.com/trbrewer/puckworks/blob/21b138a1fa8866db0b65c59b541b766498e63ed4/docs/CLAIM_BINDING_AUDIT.md)

---

**Detailed Review**  
Round 8 review of Paper 1 at commit `21b138a1fa8866db0b65c59b541b766498e63ed4`
