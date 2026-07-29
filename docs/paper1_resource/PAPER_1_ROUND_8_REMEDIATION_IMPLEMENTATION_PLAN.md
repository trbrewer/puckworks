# Paper 1 — Round 8 Remediation and Implementation Plan

**Purpose:** Convert every finding in the Round 8 detailed review into an implementation-ready correction protocol.  
**Review target:** [`21b138a1fa8866db0b65c59b541b766498e63ed4`](https://github.com/trbrewer/puckworks/tree/21b138a1fa8866db0b65c59b541b766498e63ed4)  
**Source review:** `PAPER_1_ROUND_8_DETAILED_REVIEW.md`  
**Primary manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Intended users:** paper authors, scientific-code maintainers, reviewers, and the person approving the final submission package  
**Recommended status until completion:** **Not submission-ready**

---

## 1. Executive implementation decision

The Round 8 findings should **not** be addressed as ten unrelated text edits. They expose one cross-cutting failure mode: scientific results are represented independently in the producer, JSON artifacts, manuscript, standalone captions, package records, figures, tests, and release gate. Several of those representations have drifted even though others are correct.

The most reliable correction is therefore to rebuild the chain in this order:

1. **Freeze and audit the scientific source data and analysis configuration.**
2. **Correct the producer and machine-readable contracts**, including the endpoint schema, corpus manifest, resampling design, and full-precision interval representation.
3. **Regenerate the analysis artifacts** from one deterministic command.
4. **Generate the data-bearing parts of the manuscript, captions, package record, and supplementary manifest from those artifacts.**
5. **Correct the figure dependency graph and layout.**
6. **Replace weak or mis-targeted tests with source-to-artifact and artifact-to-publication contracts.**
7. **Run the complete science gate, submission gate, full test suite, and rendered-package audit.**

This order matters. Editing the manuscript before the producer and artifacts are settled would create another round of manual propagation and could hard-code values that change when the analysis is corrected.

### 1.1 Required end state

The correction is complete only when all of the following are true:

- the adopted transfer estimand is the complete 44-record / 132-observation C/F corpus, including all eight off-grid records;
- every submission-facing representation reports the same corpus, benchmark values, endpoint unit, method, and interpretation;
- the resampling design is explicit, auditable, and described as a sensitivity design rather than a uniquely identified experimental hierarchy;
- analytical interval classification uses full-precision signed bounds, while display rounding is handled separately;
- no claim of statistical distinguishability, equivalence, or population-level superiority is made from an explicitly non-calibrated fixed-predictor sensitivity range;
- tests fail when any count, sample membership, unit, method, interval, caption, figure edge, or package statement drifts;
- ordinary `verify` mode catches science-contract defects, while `submission` mode adds final metadata and packaging checks rather than containing otherwise untested scientific checks;
- the final rendered manuscript, supplement, captions, and figures have been inspected at journal-relevant size.

### 1.2 Stop conditions

Implementation should stop for scientific adjudication rather than silently propagating outputs if any of the following occurs:

- regenerating the current analysis does not reproduce the committed 44 records / 132 observations;
- the currently expected pooled MAPE values, worse-count, or point difference change beyond the declared numerical tolerance;
- the new sample-record sensitivity changes the direction of the point comparison or produces a materially different interpretation;
- a high-repetition Monte Carlo audit shows that a reported percentile bound is unstable at the paper's chosen display precision;
- source data do not establish the sample, replicate, or grind hierarchy assumed by the proposed resampling implementation;
- the new schema cannot be consumed by another active paper component without an explicit migration;
- figure regeneration changes plotted data, rather than only dependency geometry or layout, without a corresponding artifact change;
- a test passes only because it searches for a value somewhere in a file rather than in the intended semantic block.

---

## 2. Source-of-truth architecture

### 2.1 Required hierarchy

The corrected repository should use the following one-way dependency chain:

```text
source data + explicit analysis configuration
                    ↓
          executable scientific producer
                    ↓
 schema-versioned canonical artifacts and manifests
                    ↓
     shared formatters + generated marked blocks
                    ↓
 manuscript / supplement / captions / package / figures
                    ↓
 source→artifact tests + artifact→publication tests
                    ↓
       rendered package and final release audit
```

No lower layer should independently redefine a value or scientific method owned by a higher layer. In particular:

- prose must not contain manually retyped headline values when a generated block can supply them;
- tests must not define a second independent copy of the expected current values;
- display formatting must not determine analytical flags;
- package-status text must not define endpoint units or schemas;
- historical review briefs must not be dynamically tied to a later live repository state.

### 2.2 Recommended shared implementation module

Add a small module such as:

```text
puckworks/paper_a/transfer_contract.py
```

It should own pure, unit-testable functions and typed records for:

- endpoint quantity, unit, and target values;
- complete-corpus manifest construction;
- canonical sample and cluster keys;
- resampling-scheme definitions and membership;
- full-precision interval classification;
- display formatting for percentages and percentage-point ranges;
- deterministic canonical JSON and manifest hashing;
- artifact schema validation.

The producer may continue to perform the numerical work in `puckworks/validation/slow/angeloni_bracket.py`, but it should import the contract definitions rather than re-expressing them in docstrings, local literals, or bespoke output structures.

### 2.3 Recommended deterministic artifact writer

Add one explicit command, for example:

```text
tools/paper_a_transfer_artifacts.py
```

with the interface:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_artifacts.py --write
```

The command should:

1. load the source data;
2. validate the source schema and sample identities;
3. build the complete-corpus manifest;
4. run the endpoint, comparator-loss, and resampling analyses;
5. validate all outputs before writing;
6. write all related artifacts to temporary files;
7. replace the committed files atomically only after every artifact validates; and
8. in `--check` mode, regenerate in memory and fail on any byte-level or normalized-object difference.

The command should update, or deliberately replace with a consolidated schema, these current artifacts:

- `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`;
- `docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`; and
- `docs/paper1_resource/PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json`.

A timestamp should not be allowed to make an otherwise deterministic artifact change on every run. Provenance should be expressed through stable fields such as source-file hash, producer/configuration version, random-generator name, seed, repetition count, and schema version. A human-readable generation timestamp may be kept outside the normalized scientific payload if operationally necessary.

### 2.4 Recommended generated publication blocks

Add a second command, for example:

```text
tools/paper_a_transfer_text.py
```

with the same `--check` and `--write` pattern. It should update only bounded marked blocks, following the existing front-matter splicing pattern rather than rewriting entire author-edited sections.

Recommended markers include:

```html
<!-- paper-a:transfer-methods:begin -->
...
<!-- paper-a:transfer-methods:end -->

<!-- paper-a:transfer-results:begin -->
...
<!-- paper-a:transfer-results:end -->

<!-- paper-a:transfer-caption:begin -->
...
<!-- paper-a:transfer-caption:end -->

<!-- paper-a:transfer-corpus-manifest:begin -->
...
<!-- paper-a:transfer-corpus-manifest:end -->
```

The generated text should include a source comment containing the schema version and canonical manifest hash. The visible prose should remain readable and journal-appropriate; the hash is a source-level assurance device, not text intended for publication.

### 2.5 Two independent contract layers

The corrected tests must deliberately separate two questions:

1. **Does the artifact faithfully represent the source data and producer?**
2. **Do the manuscript, caption, package, and figures faithfully represent the artifact?**

Deriving both sides of every assertion from the same JSON file would merely prove internal consistency and could certify a wrong artifact. At minimum:

- source-to-artifact tests must independently load `bioactives.csv` and reconstruct counts, IDs, cluster membership, and hashes;
- producer-to-artifact checks must recompute outputs under the committed configuration;
- artifact-to-publication tests must parse the intended marked block or figure payload and compare it with the artifact;
- release checks must run the same validators against the committed package.

---

## 3. Change-control and implementation sequence

### 3.1 Baseline capture

Before editing:

1. Create a dedicated branch from the reviewed or current approved baseline.
2. Record the starting commit, tree, Python version, package lock state, and source-data hashes.
3. Run every currently available Paper 1 command and save the complete output, including failures.
4. Copy the three current transfer artifacts into a temporary comparison directory outside the tracked tree.
5. Render the current manuscript figures and retain the images for before/after comparison.
6. Record the expected current headline values as **comparison expectations**, not as hard-coded future truth:
   - 44 C/F records;
   - 132 named-solute observations;
   - pooled MAPE 8.44% versus 8.83%;
   - model worse on 62/132 observations;
   - observed pooled difference approximately −0.394 percentage points;
   - current displayed primary range `[−0.825, +0.000] pp`.

If the baseline cannot be executed, the implementation record must say so explicitly and distinguish static corrections from regenerated scientific results.

### 3.2 Recommended commit sequence

Use small, reviewable commits in this order:

| Commit | Content | Scientific outputs permitted to change? |
|---|---|---:|
| 1 | Contract module, schema validators, canonical hashing, tests | No committed result change yet |
| 2 | Producer/resampling/precision corrections and artifact writer | Yes; changes must be explained |
| 3 | Regenerated JSON artifacts and supplementary manifest | Yes; artifact diff is the evidence |
| 4 | Generated Methods, Results, caption, package and interpretation text | Only propagated values/wording |
| 5 | Figure 1 geometry and S3 layout corrections | Geometry/layout only unless separately justified |
| 6 | Consistency-gate split, semantic/mutation tests and brief snapshot fix | No unexplained result change |
| 7 | Final rendered-package corrections and verification record | No scientific result change |

Do not combine a changed numerical analysis with broad editorial rewrites in one opaque commit. Reviewers should be able to identify exactly which values changed because the method changed and which files merely propagated the new contract.

### 3.3 Finding dependency map

| Finding | Depends on | Blocks |
|---|---|---|
| P0-1 stale transfer caption | final corpus/result artifact and formatter | final caption/package |
| P0-2 wrong Methods scheme | P1-1 final resampling design | reproducible Methods |
| P0-3 stale endpoint gate/schema | endpoint contract and release-gate split | routine verification/submission |
| P1-1 dependence overstatement | explicit source hierarchy and cluster manifest | final Methods/Results interpretation |
| P1-2 rounding/inference | interval schema and Monte Carlo audit | final Results/Table language |
| P1-3 mis-targeted interval test | shared formatter and marked blocks | reliable CI assurance |
| P1-4 weak corpus contract | canonical corpus manifest/hash | caption/manuscript/package assurance |
| P1-5 Figure 1 geometry | final study-design semantics | publication figure |
| P2-1 stale brief count | commit-pinned audit snapshot | review-governance accuracy |
| P2-2 S3 overlap | final caption/title allocation | publication-quality supplement |

---

## 4. Summary action matrix

| ID | Objective | Primary implementation action | Required verification |
|---|---|---|---|
| P0-1 | Make the transfer caption describe the adopted complete corpus | Generate caption values and corpus wording from the canonical artifact | Artifact-to-caption test, stale-tuple mutation, rendered inspection |
| P0-2 | Make Methods reproduce the actual producer | Generate a complete resampling-method block from a machine-readable design | Producer/design equivalence test and independent Methods review |
| P0-3 | Remove the retired volume endpoint from all active control layers | Introduce a gram-based endpoint schema and move science checks into routine `verify` | Negative `v_targets`/mL tests and direct CLI tests |
| P1-1 | Describe dependence honestly and bracket plausible structures | Archive membership, retain conservative primary transparently, add sample-record sensitivity | Cluster census, point-estimate invariance, sensitivity table |
| P1-2 | Separate analysis precision from display precision and eliminate unsupported inference | Store signed full bounds, run Monte Carlo stability audit, revise interpretation | Boundary mutation tests, multi-seed/batch audit, wording scan |
| P1-3 | Ensure the interval test actually binds the primary range | Replace broad regex with artifact-driven marked-block assertions | Required-occurrence and mutation tests |
| P1-4 | Bind the declared estimand to exact sample membership | Canonical manifest, stable hashes, supplementary membership table, generated metadata | Source-to-manifest and manifest-to-publication tests |
| P1-5 | Make Figure 1 arrows represent real dependency | Define data-driven graph nodes/edges and branch LOCO/C/F analyses correctly | Edge-set unit test and rendered review |
| P2-1 | Correct the brief without making history drift | Generate a commit-pinned coverage snapshot/block | Reconciliation arithmetic and commit-match test |
| P2-2 | Produce a legible S3 at publication size | Shorten titles, move explanation to caption, adjust layout | Bounding-box test and print-width visual audit |

---
# 5. Detailed remediation protocols

## 5.1 P0-1 — Stale standalone transfer-figure caption

### Objective

Ensure that the standalone caption supplied to the journal describes the same **complete held-out C/F corpus**, numerical comparison, and estimand as the plotted figure, manuscript, supplement, and canonical analysis artifact.

### Correct scientific end state

At the current reviewed result state, the caption should identify:

- 44 held-out C/F sample records;
- three named solutes per record;
- 132 observations in total;
- inclusion of the eight off-grid records;
- pooled model MAPE of 8.44%;
- pooled level-only-comparator MAPE of 8.83%; and
- the model being worse on 62 of 132 observations.

The 108-observation result may appear only if it is explicitly labelled as the **matched-grid sensitivity** on which the same-`(T,p)` lookup comparator is defined. It must not be allowed to read as the plotted headline corpus.

### Files and components to inspect

Primary expected changes:

- `docs/figures/PAPER_A_CAPTIONS.md`;
- the transfer-figure rendering code in `puckworks/figures_paper_a.py` or its current successor;
- `tools/paper_a_transfer_text.py` proposed above;
- `tests/test_paper_a_model_contract.py`, preferably split into narrower contract files;
- any journal-conversion source that duplicates standalone captions.

Also search active, submission-facing paths for the stale tuple or parts of it:

```bash
rg -n '108|8\.2\s*%|8\.6\s*%|50\s*(of|/)\s*108' \
  docs/submission docs/figures puckworks tools tests
```

The search output must be adjudicated rather than globally replaced. The number 108 remains legitimate for the explicitly matched-grid lookup-comparator support.

### Method

#### Step 1 — Identify the caption by a stable semantic identifier

Do not update “the third caption” by ordinal alone. Give the transfer caption a stable identifier, for example `transfer_complete_corpus`, in the figure metadata or generated-block configuration. This prevents a later figure reorder from making the generator update the wrong caption.

#### Step 2 — Read the complete-corpus summary from the canonical artifact

The caption generator should read fields such as:

```text
corpus.n_held_out_records
corpus.n_observations
corpus.include_off_grid
corpus.n_off_grid_records
headline.model_mape_pct
headline.comparator_mape_pct
headline.model_worse_count
headline.model_worse_denominator
corpus.manifest_sha256
```

It should not independently recompute some values while copying others. The source-to-artifact test, not the caption generator, is responsible for proving that the artifact is correct.

#### Step 3 — Render through shared formatters

Use the same percentage and integer formatters as the Results table. Define the intended precision centrally—for example, two decimal places for pooled MAPE and integer counts for worse/total. Do not use one-decimal values merely because the old caption did.

#### Step 4 — Generate a bounded caption block

Recommended current rendering, subject to the regenerated artifact:

> **Transfer benchmark.** The mechanistic model and O-trained level-only comparator were evaluated without C/F response refitting on the complete held-out coarse/fine corpus: 44 sample records × three named solutes = 132 observations, including the eight off-grid records. Pooled MAPE was 8.44% for the mechanistic model and 8.83% for the comparator; the mechanistic model had the larger absolute percentage error for 62 of 132 observations. The displayed uncertainty summaries are fixed-predictor clustered sensitivity ranges, not calibrated confidence intervals.

If the figure contains additional panels, preserve the necessary panel-specific explanation around this generated core. Do not force every editorial sentence into generated text.

#### Step 5 — Add a manifest stamp to the source

Within the marked source block, include an invisible comment such as:

```html
<!-- paper-a:transfer-corpus-schema=2 manifest_sha256=<canonical hash> -->
```

This allows exact membership assurance without printing all 44 IDs in a journal caption.

#### Step 6 — Reconcile every copy

Compare the standalone caption with:

- the caption embedded in or adjacent to the manuscript;
- the figure title and annotations;
- the Results paragraph;
- the supplement's corpus description; and
- any submission-system caption export.

Where the journal requires captions in a separate document, generate both the manuscript caption and standalone caption from the same block or maintain one canonical caption source that is included in both outputs.

### Potential pitfalls, errors, and oversights

1. **Confusing records and observations.** Forty-four records become 132 observations because three named solutes are evaluated per record. The caption must not call 132 “samples.”
2. **Silently excluding off-grid records.** A complete count can still be wrong if membership changes. Bind the manifest hash and not only the count.
3. **Erasing the legitimate 108-point sensitivity.** A blind search-and-replace could corrupt the matched-grid comparison. Keep it, but label it unambiguously.
4. **Using inconsistent MAPE precision.** The old one-decimal caption and current two-decimal Results create apparent disagreement even if derived from the same unrounded values.
5. **Using a different comparator definition.** Confirm that the caption says “O-trained level-only comparator” and does not imply a statistical null or same-condition lookup comparator.
6. **Failing to update figure annotations.** The current figure was reported as correct, but regeneration could reintroduce old annotations if figure code contains stale literals.
7. **Updating Markdown but not the converted journal file.** The final PDF/DOCX or submission portal may retain a copied caption. Inspect the actual export.
8. **Circular assurance.** A caption and test both reading the same incorrect artifact are internally consistent. Preserve the independent source-to-artifact test described under P1-4.
9. **Ordinal drift.** Referring only to “Figure 3” can become ambiguous after reordering. Tests should use a semantic figure ID.
10. **Tie handling in the worse-count.** Confirm whether ties exist and that `model_worse_count` uses the same strict comparison as the producer. Do not derive 62 by subtracting a “better” count unless ties are explicitly handled.

### Automated checks

Add or replace tests with the following responsibilities:

```text
test_complete_transfer_caption_matches_artifact
test_complete_transfer_caption_contains_manifest_stamp
test_transfer_caption_uses_record_and_observation_terms_correctly
test_matched_grid_108_is_labelled_secondary_where_present
test_transfer_caption_rejects_stale_round7_tuple
test_transfer_figure_annotations_match_artifact
```

The main caption test should:

1. load the canonical artifact;
2. render the expected generated block using the production formatter;
3. extract the exact marked caption block;
4. assert exact normalized equality; and
5. assert that the block occurs in every required export source.

Mutation cases must include:

- changing 132 to 108;
- changing 62 to 50;
- changing either MAPE while preserving the other values;
- removing “including the eight off-grid records” or its generated equivalent;
- replacing “observations” with “samples”; and
- preserving the visible count but substituting a different manifest hash.

### Manual checks

- View the figure and standalone caption together at the size likely to be seen by a reviewer.
- Verify that the caption remains intelligible without reading the manuscript.
- Verify that the complete corpus and matched-grid sensitivity cannot be confused.
- Compare the rendered percentage precision with the relevant Results table.
- Inspect the final journal export, not merely the Markdown source.

### Definition of done and evidence to retain

P0-1 is closed only when:

- the generated caption reports the current complete-corpus values;
- all caption and annotation tests pass, including mutations;
- no active submission-facing stale tuple remains;
- the 108-point result, if retained, is visibly secondary;
- the rendered caption has been manually approved; and
- the pull request includes an artifact-to-caption diff and before/after rendering.

---

## 5.2 P0-2 — General Methods describes the wrong primary resampling scheme

### Objective

Make the general Methods section a faithful, reproducible description of the implemented fixed-predictor resampling analysis, including the final set of primary and secondary dependence sensitivities, exact cluster keys, cluster counts, unequal cluster sizes, stratification, repetition count, random seed, and the fact that model fitting is not repeated inside the resampling.

### Important sequencing requirement

Do **not** finalize this paragraph until P1-1 has settled the resampling design. P0-2 and P1-1 should be implemented in one scientific workstream: first establish the defensible design and regenerated artifacts, then generate the Methods description from that design.

### Correct scientific end state

At minimum, the Methods must identify the three currently implemented schemes:

1. primary `cond_in_variety`: `(variety, temperature, pressure)` condition clusters resampled within variety;
2. secondary `cond_in_group`: condition clusters within variety × solute; and
3. secondary `group`: whole variety × solute groups.

The recommended P1-1 correction adds a fourth, design-aligned sensitivity:

4. `sample_in_variety_grind`: each C/F sample record is one cluster containing its three co-measured solutes, resampled within variety × grind.

The Methods must distinguish the **predeclared primary sensitivity choice** from the sample hierarchy actually demonstrated by the source. It must not call the primary cluster the uniquely “actual” experimental unit.

### Files and components to inspect

- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`, especially §2.5;
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`;
- `puckworks/validation/slow/angeloni_bracket.py`;
- the proposed `puckworks/paper_a/transfer_contract.py`;
- `PAPER_A_ENDPOINT_PROPAGATION.json`;
- `PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`;
- `PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json`;
- Table 5 and any nearby Results text;
- tests that mention “primary,” “two schemes,” `cond_in_variety`, or `cond_in_group`.

### Method

#### Step 1 — Represent the design as data rather than prose

Create a schema-owned resampling design object. An illustrative structure is:

```json
{
  "resampling_design": {
    "estimand": "mean paired model-minus-comparator loss over the complete C/F observation corpus",
    "predictors_refit_inside_resampling": false,
    "interval_kind": "fixed_predictor_clustered_percentile_sensitivity_range",
    "primary_scheme": "cond_in_variety",
    "schemes": {
      "cond_in_variety": {
        "role": "primary_conservative_sensitivity",
        "strata": ["variety"],
        "cluster_key": ["variety", "temperature_degC", "pressure_bar"],
        "n_clusters": 26,
        "cluster_size_distribution": {"3": 8, "6": 18}
      },
      "sample_in_variety_grind": {
        "role": "design_aligned_secondary_sensitivity",
        "strata": ["variety", "grind"],
        "cluster_key": ["sample_id"],
        "n_clusters": 44,
        "cluster_size_distribution": {"3": 44}
      },
      "cond_in_group": {
        "role": "secondary_sensitivity",
        "strata": ["variety", "solute"],
        "cluster_key": ["variety", "solute", "temperature_degC", "pressure_bar"],
        "n_clusters": 78
      },
      "group": {
        "role": "secondary_coarse_sensitivity",
        "strata": [],
        "cluster_key": ["variety", "solute"],
        "n_clusters": 6
      }
    }
  }
}
```

The final names and exact implementation must follow the code, but the object must make every material choice inspectable.

#### Step 2 — Validate the cluster census from the source

Before running the bootstrap, construct and archive membership tables. The expected current primary census is:

- 26 `(variety,T,p)` clusters;
- 18 clusters with both C and F and six named-solute observations;
- eight off-grid one-grind clusters with three observations;
- no omitted C/F record.

For the proposed sample-record scheme, the expected census is 44 clusters of three observations.

#### Step 3 — Define the resampled estimand precisely

The code and Methods must answer:

- Is the summary the observation-weighted mean of paired loss differences?
- When unequal-size clusters are resampled, are all observations in a selected cluster retained?
- Does a cluster drawn twice contribute twice?
- Are the same sampled indices applied to both model and comparator losses?
- Is the original point estimate calculated over all 132 observations independently of the resampling scheme?
- Are clusters sampled within strata while preserving the original number of clusters per stratum?

Recommended answer: calculate one paired loss difference per observation; sample whole clusters with replacement within the declared strata; retain every observation in each selected cluster; preserve model/comparator pairing; calculate the resample statistic as the observation-weighted mean over selected observations; and report the common full-corpus point estimate separately from scheme-specific sensitivity ranges.

If the producer instead uses a cluster-weighted mean, say so explicitly and assess whether that changes the estimand.

#### Step 4 — State the non-refitting contract

The Methods must say that both predictors are fixed before the C/F loss differences are resampled and that no nonlinear model, level parameter, or comparator is refitted inside each draw. This is why the output is called a fixed-predictor sensitivity range rather than a calibrated model-fitting confidence interval.

#### Step 5 — Generate the Methods block

Recommended current template, with values filled from the final artifact:

> For each held-out C/F solute observation, we formed the paired loss difference between the frozen mechanistic prediction and the frozen O-trained level-only comparator. Neither predictor was refitted inside resampling. We report fixed-predictor clustered percentile sensitivity ranges rather than calibrated confidence intervals. The predeclared primary scheme resampled `(variety, temperature, pressure)` clusters with replacement within variety. The complete corpus contains 26 such clusters: 18 contain both C and F sample records for all three named solutes (six observations), while eight off-grid clusters contain one grind and three solute observations. This scheme deliberately keeps same-condition cross-solute outcomes together and, where both grinds exist, additionally moves the distinct C and F sample records together; it is treated as a conservative dependence sensitivity rather than the uniquely identified experimental sampling unit. Secondary analyses resampled individual sample-record clusters within variety × grind, conditions within variety × solute, and whole variety × solute groups. Each scheme used the archived repetition count, random seed, and cluster membership, and the common point estimate was calculated on all 132 observations.

The final paragraph should include `B`, the seed, percentile levels, random generator, and any relevant stratified-cluster details either in the main Methods or supplement.

#### Step 6 — Generate a machine-readable method table

The supplement should contain a compact table with one row per scheme:

| Scheme | Role | Strata | Cluster key | Number of clusters | Cluster-size distribution | Refitting? |
|---|---|---|---|---:|---|---|

Generate the table from the design object. This makes the prose easier to read while preserving exact reproducibility.

#### Step 7 — Remove stale producer documentation

Update docstrings and comments in `angeloni_bracket.py` that say every condition has both grinds or call the primary unit the “actual dependence structure.” Producer documentation must be generated from, or at least validated against, the same design object.

### Potential pitfalls, errors, and oversights

1. **Fixing Methods before adding the sample-record sensitivity.** This creates immediate second-order drift.
2. **Calling a sensitivity range a confidence interval.** The no-refit procedure does not acquire calibrated coverage merely because it uses bootstrap resampling.
3. **Leaving the primary scheme outcome-selected.** Do not choose the primary based on which range reaches or excludes zero. Retain or change it only for a pre-specified design reason, with the decision recorded.
4. **Misstating the 26-cluster composition.** Eight clusters contain one grind only; avoid a universal six-observation statement.
5. **Ignoring unequal cluster sizes.** The treatment of 3- and 6-observation clusters can alter weighting and must be explicit.
6. **Breaking pairing.** Model and comparator losses for the same observation must always be resampled together.
7. **Conflating sample records with extraction replicates.** If the CSV contains means over duplicated extractions rather than replicate rows, those unavailable replicates cannot be bootstrapped.
8. **Using non-unique condition keys.** Every key must include variety; otherwise Arabica and Robusta conditions may collide.
9. **Under-describing the six-group scheme.** Six whole groups produce a coarse, highly discrete sensitivity distribution and should not be framed as a high-resolution inferential analysis.
10. **Assuming every secondary range is narrower.** Generate widths and comparisons from the artifact; do not describe them generically.
11. **Allowing a table and paragraph to diverge.** Both should be generated from one design object.
12. **Changing the point estimate by cluster scheme.** Scheme-specific resampling should change the range, not the observed full-corpus mean. A point-estimate change signals a weighting or subset bug unless explicitly intended.

### Automated checks

Required tests include:

```text
test_resampling_design_schema_is_complete
test_primary_scheme_matches_producer_default
test_resampling_membership_matches_source_corpus
test_primary_cluster_size_distribution_is_18x6_plus_8x3
test_sample_record_scheme_has_44_clusters_of_3
test_all_schemes_cover_exactly_the_complete_corpus
test_model_and_comparator_indices_are_paired
test_point_estimate_is_scheme_invariant
test_methods_block_matches_resampling_design
test_supplementary_method_table_matches_resampling_design
test_no_active_docstring_claims_every_condition_has_both_grinds
```

Add negative tests for:

- declaring `cond_in_group` primary while the artifact says `cond_in_variety`;
- omitting one scheme from the Methods table;
- changing one cluster's membership without changing the count;
- dropping an off-grid record;
- changing the no-refit flag;
- reporting 26 clusters but a membership list containing 25 or 27; and
- changing the resample point estimate between schemes.

### Manual checks

- Have a scientifically informed reviewer read only the Methods and write down how they would reproduce the resampling. Compare their interpretation with the code.
- Confirm that “primary” is explained as a declared sensitivity choice rather than a discovered truth about the experiment.
- Verify that the supplement provides enough detail to reconstruct every cluster.
- Review the source paper or source-data documentation for the distinction among coffee sample, extraction duplicate, grind, condition, and solute outcome.

### Definition of done and evidence to retain

P0-2 is closed only when:

- the design object, producer, artifacts, Methods, Results, and supplement name the same primary and secondary schemes;
- exact cluster keys, counts, size distributions, stratification, `B`, seed, and no-refit status are stated;
- a source-derived membership table exists and validates;
- the old two-scheme/wrong-primary paragraph and producer docstring are removed;
- all method-contract and mutation tests pass; and
- an independent reviewer can reproduce the implemented hierarchy from the paper.

---

## 5.3 P0-3 — Submission package and release gate retain the retired mL endpoint contract

### Objective

Remove the obsolete volume-endpoint contract from every active scientific, build, package, test, and release path; replace it with one schema-versioned collected-mass endpoint contract; and ensure ordinary verification exercises the scientific endpoint check.

### Correct scientific end state

The active contract must state:

```text
endpoint quantity: collected mass
symbol/key family: m_target
unit: g
required targets: 38.0, 40.0, 42.0
```

The release gate must validate both the target array and every row's target field. No active code should expect `v_targets` or describe the sweep as mL.

### Files and components to inspect

Known primary locations:

- `docs/submission/PAPER_A_JFE_PACKAGE.md`;
- `tools/paper_a_consistency.py`, especially `_release_state()` and mode dispatch;
- `docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json`;
- `puckworks/paper_a/build.py`;
- `puckworks/paper_a/claim_coverage.py`;
- tests for package, consistency, build, and claim coverage;
- any generated audit or claim label containing endpoint units.

The Round 8 implementation should explicitly inspect the additional stale active references identified during remediation planning:

- `puckworks/paper_a/build.py` contains wording equivalent to “Endpoint-mass sensitivity (38/40/42 mL)” and 38/42 mL claim labels;
- `puckworks/paper_a/claim_coverage.py` describes 38/42 as endpoint-mass targets in mL.

Search active paths with a targeted command:

```bash
rg -n '(38/40/42\s*mL|38\s*mL|40\s*mL|42\s*mL|v_targets|endpoint[^\n]*mL|m_target[^\n]*mL)' \
  docs/submission docs/figures puckworks tools tests
```

Historical review files and changelog records may legitimately describe the old defect. Use a reviewed allow-list rather than globally editing historical evidence.

### Method

#### Step 1 — Replace loose endpoint fields with a typed schema

Prefer an explicit nested endpoint object over a bare `m_targets` array. For example:

```json
{
  "schema_version": 2,
  "endpoint": {
    "quantity": "collected_mass",
    "symbol": "m_target",
    "unit": "g",
    "targets": [38.0, 40.0, 42.0]
  },
  "rows": [
    {"m_target_g": 38.0},
    {"m_target_g": 40.0},
    {"m_target_g": 42.0}
  ]
}
```

For compatibility, a transitional reader may accept the current `m_targets` key while the writer emits the new schema. It must **not** silently translate `v_targets`, because that would conceal a unit error. An old-volume schema should raise a clear validation failure requiring explicit migration.

#### Step 2 — Add strict validation

The validator should require:

- supported `schema_version`;
- `quantity == "collected_mass"`;
- `unit == "g"`;
- exact target set and order `[38.0, 40.0, 42.0]`;
- one and only one row for each target;
- row key `m_target_g` consistent with the endpoint object;
- no `v_targets`, `v_target_ml`, or volume-endpoint alias in an active artifact;
- finite numeric result fields for every endpoint; and
- the declared interpretation flags to reconcile with the endpoint rows.

#### Step 3 — Correct the package record

Replace the stale package statement with generated text such as:

> Endpoint-mass propagation at collected-mass targets of 38, 40, and 42 g has been regenerated and validated against the committed endpoint artifact.

Avoid repeating detailed conclusions in a status checklist. The package record should identify completion and the artifact/version, not become another independent Results section.

#### Step 4 — Refactor the consistency modes

Split `paper_a_consistency.py` checks conceptually into:

```text
science/content checks       → always run in verify and submission
submission metadata checks   → run only in submission
render/export checks          → run in submission or an explicit render mode
```

Move endpoint schema, target, artifact-to-text, and interpretation checks into the routine science/content set. `verify` should catch a stale `v_targets` expectation even while author metadata or a final DOI remains incomplete.

`submission` should call all `verify` checks and then add final-only requirements. It should never be the only path that exercises a central scientific contract.

#### Step 5 — Replace the magic-phrase gate

Remove the requirement for the literal phrase “not endpoint-invariant.” Instead, represent the interpretation in the artifact, for example:

```json
{
  "endpoint_sensitivity": {
    "point_difference_sign_stable": true,
    "range_boundary_classification_stable": false,
    "interpretation_code": "small_sign_stable_effect_boundary_not_stable"
  }
}
```

Generate the corresponding interpretation sentence in the manuscript or compare a structured marked block with the artifact. The gate should test the meaning, not one exact editorial phrase.

#### Step 6 — Update claim labels and build metadata

Change active claim names and headings in `build.py` and `claim_coverage.py` to gram-based wording. Better still, derive the label from the endpoint object:

```text
Endpoint-mass sensitivity (38/40/42 g)
```

Do not retain a claim identifier whose human-readable name encodes mL even if its numerical value is correct.

#### Step 7 — Add a deliberate schema migration note

Record in an appropriate technical changelog or artifact schema history:

- old active key: `v_targets` or volume-oriented expectation;
- corrected key: collected-mass endpoint schema / `m_target_g` rows;
- reason: endpoint is defined by collected mass, not volume;
- migration behavior: old volume schema is rejected, not silently coerced.

This prevents a future maintainer from “restoring” the old key after seeing historical references.

### Potential pitfalls, errors, and oversights

1. **Changing only the package line.** The release gate, build labels, and claim coverage would remain stale.
2. **Accepting both g and mL silently.** This converts a scientific unit defect into an ambiguous compatibility layer.
3. **Banning every occurrence of mL globally.** Volume is a legitimate unit elsewhere in espresso science. Restrict the prohibition to the collected-endpoint contract and active Paper 1 claims.
4. **Treating `m` as unambiguous.** Use `m_target_g` or a typed endpoint object; a bare `m_targets` array still relies on context for its unit.
5. **Checking only the target array.** Rows could retain a wrong key or unit. Validate both top-level declaration and row-level representation.
6. **Leaving science checks in submission-only mode.** Routine CI would continue to miss the defect.
7. **Making `submission` unusable because draft metadata is incomplete.** Separate metadata from science rather than removing science from CI.
8. **Retaining a literal phrase test.** Editorial rewording should not create a false release failure when the scientific interpretation is unchanged.
9. **Updating JSON without a schema version.** Consumers cannot know whether `m_targets` is a corrected mass array or an untyped legacy field.
10. **Editing historical review evidence.** Old reviews should continue to document that mL was once wrong; only active contracts must be corrected.
11. **Failing to check generated claim audits.** A stale label may survive even after source code changes if audits are not regenerated.
12. **Converting values numerically.** The correction is not a 1:1 mL-to-g conversion operation; the endpoint was analytically defined in mass and should be represented directly as such.

### Automated checks

Required tests:

```text
test_endpoint_schema_declares_collected_mass_in_grams
test_endpoint_targets_are_exactly_38_40_42_g
test_endpoint_rows_use_m_target_g
test_legacy_v_targets_is_rejected
test_package_endpoint_statement_is_generated_from_artifact
test_verify_mode_executes_endpoint_science_checks
test_submission_mode_is_verify_plus_final_checks
test_endpoint_interpretation_uses_structured_state_not_magic_phrase
test_active_claim_labels_use_grams
test_no_active_endpoint_volume_contract_remains
```

CLI tests should invoke the actual commands in a temporary repository fixture:

```bash
python tools/paper_a_consistency.py verify
python tools/paper_a_consistency.py submission
```

Mutation tests must show failures when:

- `m_targets` or `endpoint.targets` is renamed to `v_targets`;
- `unit` is changed from `g` to `mL`;
- one row uses `v_target_ml`;
- the 42 g row is missing or duplicated;
- package text says mL while the artifact says g;
- `conclusion_stable` or its replacement changes without regenerated interpretation text; and
- the endpoint check is removed from `verify` while remaining in `submission`.

### Manual checks

- Inspect every targeted search result and document why any remaining mL occurrence is legitimate.
- Read the package record as a submission coordinator would; confirm that it cannot be understood as a volume sweep.
- Inspect the endpoint rows and Table/Results headings for explicit gram units.
- Confirm that conversion to the journal format preserves “g” and does not substitute an old copied caption or table.

### Definition of done and evidence to retain

P0-3 is closed only when:

- all active endpoint representations use collected mass in grams;
- the artifact schema is versioned and validates strictly;
- `v_targets` and endpoint-specific mL mutations fail;
- routine `verify` exercises the endpoint science contract;
- the package, build labels, claim coverage, manuscript, supplement, and artifacts agree;
- historical references are deliberately allow-listed rather than accidentally retained; and
- both consistency CLI modes are run and their outputs archived.

---
## 5.4 P1-1 — Dependence unit is overstated and the corpus is unbalanced

### Objective

Represent the observed sample hierarchy accurately, disclose the unequal composition of the primary clusters, justify the primary scheme as a conservative sensitivity choice rather than a uniquely identified experimental unit, add a sample-record-based alternative, and report the behavior of each sensitivity without outcome-driven selection.

### Correct scientific end state

The paper and producer should state all of the following:

- the C/F corpus contains 44 separate sample records and 132 named-solute observations;
- each sample record contributes three co-measured solute outcomes;
- the primary `(variety,T,p)` construction contains 26 clusters;
- 18 primary clusters contain both C and F sample records and therefore six observations;
- eight off-grid primary clusters contain one grind only and therefore three observations;
- the eight one-grind clusters are `A21`, `A22`, `A32`, `A33`, `R21`, `R22`, `R32`, and `R33`;
- coupling C and F at a shared nominal condition is a deliberate conservative dependence sensitivity, not a source-established identity of experimental units;
- the sample-record scheme preserves the clearest demonstrated dependency—the three solute measurements from one coffee sample;
- the current secondary ranges do not both narrow the primary range: the within-solute condition range is narrower, while the whole-group range is wider; and
- none of the schemes is selected or discarded because its range does or does not touch zero.

### Files and components to inspect

- `puckworks/data/angeloni2023/bioactives.csv` and any source-data documentation;
- `puckworks/validation/slow/angeloni_bracket.py`;
- proposed `puckworks/paper_a/transfer_contract.py`;
- endpoint, corpus, and comparator robustness artifacts;
- manuscript Methods, Results, Table 5, and surrounding interpretation;
- supplement method and corpus descriptions;
- Figure captions if they describe clustering;
- source-paper notes concerning espresso-coffee samples and duplicate extractions.

### Method

#### Step 1 — Build an explicit observation and sample table

Create a normalized internal table with one row per evaluated solute observation and at least these columns:

```text
sample_id
variety
grind
temperature_degC
pressure_bar
solute
observed_response
model_prediction
comparator_prediction
model_loss
comparator_loss
paired_loss_difference
on_grid
lookup_defined
```

Before resampling, validate that:

- each included sample ID is unique at the sample-record level;
- each included sample record has exactly the expected three named solutes;
- every observation has one model and one comparator loss;
- no O response enters the held-out C/F evaluation set;
- all eight off-grid C/F records are included in the headline corpus; and
- no missing or duplicated row is concealed by a count that still totals 132.

#### Step 2 — Determine what the source actually identifies

Document, with a source citation or data dictionary, the status of:

- nominal `(T,p)` condition;
- grind-specific coffee sample;
- solute outcomes measured from that sample;
- extraction duplicates mentioned in the source methods; and
- whether the repository contains replicate-level measurements or only aggregate values.

If duplicate extractions are already averaged in the source table and no replicate ID exists, the analysis must not imply that extraction-level variation has been resampled. State that the available unit is the reported sample record.

#### Step 3 — Archive exact membership for every scheme

For each scheme, create a stable member list. Example for the primary scheme:

```json
{
  "cluster_id": "Arabica|89|10",
  "variety": "Arabica",
  "temperature_degC": 89,
  "pressure_bar": 10,
  "sample_ids": ["A21"],
  "grinds": ["C"],
  "observation_ids": [
    "A21|solute_1",
    "A21|solute_2",
    "A21|solute_3"
  ],
  "n_observations": 3
}
```

Use actual solute names in the artifact. Sort members canonically and hash the complete membership object.

The artifact should report, not merely imply:

```text
primary cluster-size distribution: 18 × 6, 8 × 3
sample-record distribution: 44 × 3
condition-within-group cluster count: 78
whole-group cluster count: 6
```

#### Step 4 — Add the sample-record sensitivity

Recommended implementation:

- cluster key: `sample_id`;
- each cluster contains the three named-solute observations for that sample;
- strata: `(variety, grind)`;
- number of clusters drawn per stratum: the original count in that stratum;
- resample statistic: observation-weighted mean of paired loss differences across selected records;
- no predictor refitting.

Stratifying within variety × grind preserves the broad held-out design composition and prevents a bootstrap draw from accidentally omitting an entire variety or grind. If a different stratification is chosen, justify it and archive it.

#### Step 5 — Retain or change the primary only by design rationale

The safest current course is normally to retain `cond_in_variety` as the declared primary because it has already been adopted and is conservative, while correcting its rationale and adding the sample-record result as a prominent sensitivity. This avoids selecting a new primary after observing whether its range reaches zero.

A primary change may still be scientifically justified, but it requires:

1. a written design argument made without reference to the resulting range;
2. explicit disclosure that the primary changed after earlier analyses;
3. simultaneous reporting of the old and new primary results; and
4. a reviewer-approved decision record.

#### Step 6 — Recompute all schemes under identical numerical settings

Use the same paired loss vector, endpoint, repetition count, random-number generator, seed policy, and percentile levels. Only cluster membership/stratification should vary. Archive:

- point estimate;
- full-precision lower and upper bounds;
- display interval;
- width;
- signed nearest bound to zero;
- number and size distribution of clusters;
- Monte Carlo stability diagnostics; and
- manifest hash.

The common point estimate should be identical across schemes if all use the same 132 observations and observation-weighted estimand. Treat any difference as a potential bug until explained.

#### Step 7 — Correct the width interpretation

At the reviewed artifact state:

| Scheme | Displayed range | Width | Correct description |
|---|---:|---:|---|
| `(variety,T,p)` primary | `[−0.825, 0.000]` | 0.825 pp | reference |
| condition within variety × solute | `[−0.742, −0.044]` | 0.698 pp | narrower |
| whole variety × solute group | `[−0.883, −0.024]` | 0.859 pp | wider |
| sample record within variety × grind | **regenerate** | **regenerate** | report without outcome-based label |

Generate widths from full-precision bounds and display them at an appropriate precision. Do not infer a universal “dropping dependence manufactures precision” story from schemes that behave differently.

#### Step 8 — Revise the interpretation

Recommended prose:

> The `(variety,T,p)` primary scheme is deliberately conservative: it keeps all three co-measured solutes together and, at the 18 on-grid conditions, also moves the distinct C and F sample records together. Eight off-grid clusters contain only one grind, so the primary design comprises 18 six-observation and eight three-observation clusters. The source establishes shared-sample dependence among the three solutes more directly than it establishes C/F pairing at a common nominal condition. We therefore report a sample-record bootstrap and two additional coarser/finer cluster constructions as dependence sensitivities. Their differences describe sensitivity to plausible grouping assumptions; they are not used to select a favorable binary conclusion.

#### Step 9 — Put the membership audit in the supplement

Add a supplementary table or machine-generated appendix listing, for all 44 sample records:

- sample ID;
- variety;
- grind;
- temperature;
- pressure;
- on/off-grid status;
- primary cluster ID; and
- sample-record cluster ID.

This is more useful than making readers reverse-engineer cluster membership from the source CSV.

### Potential pitfalls, errors, and oversights

1. **Post-hoc primary selection.** The strongest risk is choosing the scheme whose interval best supports the desired narrative.
2. **Assuming nominally identical conditions imply one sample.** C and F records at the same `(T,p)` are distinct sample records unless the source says otherwise.
3. **Losing cross-solute dependence.** Resampling solutes independently ignores the clearest shared-sample structure.
4. **Treating averaged duplicates as observed replicates.** Do not fabricate unavailable replicate-level information.
5. **Cluster-ID collision.** Keys must include variety and normalized numeric condition values.
6. **Floating-point key instability.** Canonicalize temperature and pressure from source fields before constructing IDs; avoid raw float-string artifacts.
7. **Unequal-size cluster weighting.** State whether the target is observation-weighted or cluster-weighted and test the implementation.
8. **Variable resample size.** Uniformly drawing unequal clusters can produce varying observation counts. This is acceptable only if deliberate and documented.
9. **Off-grid attrition.** A helper that assumes paired C/F conditions may drop the eight singleton-grind clusters.
10. **Using the lookup comparator outside its support.** The sample-record sensitivity for the headline level-only comparator can use all 132 observations; the lookup comparator remains limited to its defined matched-grid subset.
11. **Equating wider with more correct.** Width alone does not identify the true dependence structure.
12. **Overinterpreting six whole groups.** Percentile behavior with only six coarse clusters is discrete and should be described as a stress test.
13. **Changing the common point estimate.** This usually indicates a subset or weighting change, not a legitimate consequence of clustering.
14. **Reporting rounded widths as evidence.** Use full-precision bounds for width and classification; round only for display.
15. **Failing to regenerate downstream text.** Adding a fourth scheme without updating Methods, table headings, Results, supplement, and tests recreates P0-2.

### Automated checks

Source and membership checks:

```text
test_complete_cf_observation_table_has_44_records_and_132_rows
test_each_sample_has_exactly_three_named_solutes
test_expected_off_grid_ids_are_present
test_primary_clusters_have_expected_membership_and_size_distribution
test_sample_record_clusters_have_expected_membership
test_cluster_keys_are_unique_and_canonical
test_all_schemes_cover_the_same_observation_ids
test_no_scheme_includes_optimal_grind_responses
```

Resampling checks:

```text
test_resampling_preserves_paired_losses
test_sample_record_resampling_is_stratified_as_declared
test_primary_resampling_handles_3_and_6_observation_clusters
test_common_point_estimate_is_identical_across_schemes
test_reported_width_equals_full_precision_upper_minus_lower
test_primary_is_not_selected_by_zero_crossing
test_seeded_runs_are_deterministic
```

Publication checks:

```text
test_methods_reports_18_six_and_8_three_observation_clusters
test_results_does_not_say_every_condition_has_both_grinds
test_results_does_not_say_both_secondary_ranges_are_narrower
test_supplement_membership_table_matches_manifest
test_all_reported_scheme_names_and_roles_match_artifact
```

Mutation tests must remove an off-grid record, move one sample to the wrong condition, split one sample's solutes among clusters, collide two condition IDs, and swap the primary role. Each mutation should fail for the intended reason.

### Manual checks

- Review the source-paper methods and repository data dictionary specifically for sample and replicate hierarchy.
- Inspect the eight off-grid records individually.
- Compare the membership table with the source CSV rather than relying only on aggregate counts.
- Review the primary-design rationale without viewing the resulting intervals, where practicable.
- Examine the resampling distributions, not only the 2.5th and 97.5th percentiles, for discreteness or multimodality.
- Confirm that the prose treats every scheme as a sensitivity and does not imply that one has been empirically proven correct.

### Definition of done and evidence to retain

P1-1 is closed only when:

- exact source-derived membership is archived and hashed;
- the primary census is correctly stated as 18 × 6 plus 8 × 3;
- the sample-record scheme is implemented or a documented scientific adjudication explains why not;
- all schemes cover the same complete corpus and preserve pairing;
- the primary role is design-justified and not outcome-selected;
- range widths and descriptions are generated correctly;
- producer docstrings, Methods, Results, table, and supplement agree; and
- the pull request includes the membership table, resampling output comparison, and decision record.

---

## 5.5 P1-2 — Rounding controls the knife-edge classification and the prose overstates inference

### Objective

Separate full-precision analytical results from display formatting, quantify Monte Carlo stability of the percentile boundary, preserve signed boundary information, and replace unsupported inferential language with a descriptive practical interpretation.

### Correct scientific end state

The artifact and paper should make four distinct facts visible:

1. the observed pooled model-minus-comparator difference is small and favorable to the mechanistic model, approximately −0.394 percentage points at 40 g;
2. the primary full-precision upper percentile bound at the reviewed state is slightly negative, approximately −0.0004 percentage points;
3. that bound displays as `+0.000` or `0.000` at three decimals after negative-zero normalization; and
4. because the range is a fixed-predictor clustered sensitivity range rather than a calibrated confidence interval, neither full-precision exclusion nor rounded contact with zero establishes statistical superiority or non-superiority.

### Files and components to inspect

- `paired_clustered_bootstrap` and related functions in `angeloni_bracket.py`;
- endpoint and comparator-loss robustness artifact schemas;
- Results text, Table 5, supplement, and captions;
- tests for `excludes_zero`, endpoint invariance, range formatting, and conclusion flags;
- any public-value or package text that uses “distinguishable,” “significant,” “inferential,” “resolvable,” “excludes zero,” or “reaches zero.”

### Method

#### Step 1 — Compute and retain full-precision bounds

Calculate the requested percentile bounds from the unrounded bootstrap statistics. Store signed values before any display conversion. Do not use rounded values to construct analytical flags.

Recommended result object:

```json
{
  "interval": {
    "kind": "fixed_predictor_clustered_percentile_sensitivity_range",
    "quantile_probabilities": [0.025, 0.975],
    "B": 200000,
    "rng": "PCG64",
    "seed": 0,
    "full_precision_pp": {
      "lower": "<serialized full-precision lower>",
      "upper": "<serialized full-precision upper>"
    },
    "contains_zero_full_precision": false,
    "excludes_zero_full_precision": true,
    "signed_nearest_bound_to_zero_pp": -0.0004,
    "display": {
      "digits": 3,
      "lower": -0.825,
      "upper": 0.000,
      "text": "[−0.825, +0.000]",
      "touches_zero": true
    }
  }
}
```

The example is structural. The final full-precision lower bound and all exact values must come from regeneration.

#### Step 2 — Separate analytical flags from display flags

Use full precision for:

```python
contains_zero_full_precision = lower <= 0.0 <= upper
excludes_zero_full_precision = not contains_zero_full_precision
signed_nearest_bound_to_zero = upper if upper < 0 else lower if lower > 0 else 0.0
```

Use formatted values only for:

```text
display.lower
display.upper
display.text
display.touches_zero
```

Do not derive `excludes_zero` from `round(lower, 3)` or `round(upper, 3)`.

#### Step 3 — Centralize display rounding and negative-zero handling

Use one formatter for all publication surfaces. A robust approach is decimal quantization with an explicit rounding rule, followed by display-only zero normalization. For example:

```python
from decimal import Decimal, ROUND_HALF_UP


def quantize_for_display(value: float, digits: int) -> Decimal:
    quantum = Decimal(1).scaleb(-digits)
    out = Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)
    return abs(out) if out == 0 else out
```

The scientific payload retains the original signed float or a stable high-precision decimal string. Only the rendered display changes `−0.000` to `+0.000` or `0.000` according to the paper's chosen style.

Add an explicit typography decision:

- use the Unicode minus sign `−` in publication text;
- decide whether zero upper bounds show `+0.000` or `0.000`;
- use the same convention in text, tables, and captions.

#### Step 4 — Increase the canonical repetition count

Because the predictors are fixed and the corpus is small, the resampling itself should be inexpensive relative to nonlinear model fitting. Use a substantially larger final `B` than the current low-thousands setting. A defensible default is:

```text
canonical final run: B = 200,000, one declared seed
stability audit: 20 independent seeds × 50,000 draws, or 20 equal batches of a large canonical run
```

The exact values may be adjusted after measuring runtime, but the design must resolve whether a fourth-decimal boundary is Monte Carlo noise. Archive the random generator, seeds, and batch/seed summaries.

Do not claim that multiple seeds turn the sensitivity range into a calibrated confidence interval. This audit measures numerical Monte Carlo stability only.

#### Step 5 — Quantify Monte Carlo uncertainty of the percentile estimate

For each scheme and endpoint, report at least:

- canonical lower and upper percentiles;
- across-seed or across-batch mean of each percentile;
- standard deviation and min/max of each percentile estimate;
- whether the upper-bound sign changes across independent runs;
- whether the displayed three-decimal interval changes.

If the sign of the fourth-decimal upper bound changes across reasonable runs, the artifact should say that directly. If it does not, the interpretation remains non-inferential because the procedure itself lacks calibrated coverage.

#### Step 6 — Preserve endpoint and fitting-loss sensitivities without binary collapse

For 38, 40, and 42 g, and for each comparator fitting loss, archive:

- point difference;
- full-precision range;
- display range;
- width;
- signed nearest boundary;
- full-precision zero classification;
- display zero classification; and
- Monte Carlo stability.

Replace a single ambiguous `conclusion_stable` Boolean with explicit dimensions such as:

```text
point_difference_sign_stable
point_difference_magnitude_range_pp
range_contains_zero_classification_stable
range_display_touches_zero_stable
interpretation_code
```

A Boolean called `conclusion_stable` hides which conclusion is being tested.

#### Step 7 — Remove inferential language

Search active paper and package text:

```bash
rg -ni '(distinguish|inferential|significant|significance|resolvable|confidence interval|excludes zero|reaches zero|crosses zero|equivalence|superior)' \
  docs/submission docs/figures puckworks/paper_a tools
```

Adjudicate every occurrence. Suitable replacement language is:

> At 40 g, the observed pooled MAPE difference was approximately −0.394 percentage points, a small descriptive advantage for the mechanistic model. The full-precision upper bound of the primary fixed-predictor clustered sensitivity range was slightly negative but displayed as zero at three decimals. Endpoint, clustering, fitting-loss, and Monte Carlo checks show that the position of this boundary relative to zero is sensitive at the third or fourth decimal. Because these ranges do not repeat model fitting and have not been calibrated for coverage, we make no claim of population-level superiority, equivalence, or statistical distinguishability.

Avoid replacing “not distinguishable” with “equivalent.” Absence of calibrated evidence for a difference is not evidence of equivalence.

#### Step 8 — Treat practical importance separately

The manuscript can state that a difference of about 0.4 percentage points in pooled MAPE is small in the context of errors around 8–9%. It should not invent a post-hoc smallest effect size of interest merely to classify the observed result.

If the authors want a practical-effect or equivalence margin, it must be justified independently—for example by measurement repeatability, sensory relevance, process-control tolerances, or a pre-existing domain standard—and disclosed as a new sensitivity, not retrofitted as though predeclared.

#### Step 9 — Optional calibrated-inference path

A calibrated population-inference claim would require a separate method, such as a validated hierarchical model or a resampling procedure that repeats the full relevant fitting hierarchy and has an argued target population and coverage interpretation. That is optional and not necessary to resolve Round 8. The lower-risk correction is to retain the current sensitivity analysis and narrow the claim.

### Potential pitfalls, errors, and oversights

1. **Storing only rounded values.** This makes the result irrecoverable and allows presentation precision to control logic.
2. **Normalizing negative zero before classification.** Preserve the signed full value until all analytical fields are calculated.
3. **Using Python's default `round` inconsistently.** Centralize an explicit display rule.
4. **Calling full-precision exclusion “statistical significance.”** The range has no calibrated coverage claim.
5. **Calling rounded contact with zero “non-significance.”** Display rounding has no inferential meaning.
6. **Increasing `B` but retaining one opaque Boolean.** More draws do not cure an ambiguous interpretation schema.
7. **Confusing Monte Carlo variation with sampling uncertainty.** Across-seed variation only measures numerical approximation of this resampling distribution.
8. **Overwriting the old artifact without schema versioning.** Downstream consumers may read the wrong field semantics.
9. **Using an unsigned nearest-bound distance.** The sign is necessary to reconstruct which side of zero the boundary lies on.
10. **Selecting a seed that gives the preferred sign.** Choose the canonical seed before inspecting results and report the stability audit.
11. **Selecting `B` until the bound stabilizes favorably.** Define the numerical adequacy criterion independently.
12. **Introducing a post-hoc equivalence margin.** This can look outcome-driven and may be less defensible than a descriptive statement.
13. **Changing the point estimate during a precision fix.** That indicates a deeper analysis change and requires separate adjudication.
14. **Failing to update table notes and captions.** Inferential wording often survives in footnotes even after the main paragraph is corrected.
15. **Reporting excessive decimals as scientific precision.** Archive full precision, but display only the precision justified for readers.
16. **Using “robust” without defining the sensitivity dimensions.** Say exactly what is stable: sign of point estimate, magnitude, display interval, or boundary classification.

### Automated checks

Core numerical tests:

```text
test_interval_flags_use_unrounded_bounds
test_display_rounding_does_not_change_analytical_classification
test_signed_nearest_bound_is_preserved
test_negative_zero_is_normalized_only_for_display
test_interval_width_uses_full_precision_bounds
test_endpoint_rows_expose_explicit_stability_dimensions
test_canonical_bootstrap_is_deterministic_for_declared_seed
test_monte_carlo_audit_meets_predeclared_stability_criterion
```

Boundary mutation tests should include synthetic intervals:

| Full-precision interval | Expected analytical state | Expected 3-decimal display behavior |
|---|---|---|
| `[−0.8251, −0.0004]` | excludes zero | upper displays zero |
| `[−0.8251, +0.0004]` | contains zero | upper displays zero |
| `[+0.0004, +0.8251]` | excludes zero | lower displays zero |
| `[−0.8251, 0.0]` | contains zero by closed-interval convention | touches zero |

Publication checks:

```text
test_results_calls_ranges_sensitivity_ranges_not_confidence_intervals
test_no_unqualified_distinguishable_or_inferential_claim_remains
test_table_note_disclaims_population_inference
test_full_precision_and_display_fields_reconcile
test_endpoint_and_loss_sensitivity_text_matches_artifact
```

### Manual checks

- Inspect the full resampling distribution and upper tail near zero.
- Confirm the declared quantile convention used by NumPy or the selected library; quantile interpolation methods can matter at a knife-edge.
- Review across-seed/batch diagnostics before choosing display precision.
- Have a statistical reviewer assess the revised non-inferential wording.
- Ensure the abstract and conclusion do not preserve stronger language than the Results.
- Confirm that the observed effect magnitude is described consistently and without an unsupported practical threshold.

### Definition of done and evidence to retain

P1-2 is closed only when:

- signed full-precision bounds are archived;
- analytical and display classifications are separate;
- the canonical run and stability audit are reproducible and archived;
- no Boolean is derived from display-rounded values;
- endpoint and fitting-loss sensitivities are represented dimensionally rather than by one ambiguous conclusion flag;
- unsupported inferential wording is removed from every active publication surface; and
- the pull request includes the boundary tests, Monte Carlo audit summary, artifact schema diff, and revised interpretation.

---
## 5.6 P1-3 — The interval-precision contract does not bind the primary interval

### Objective

Replace the broad numeric regular expression with an artifact-driven, context-specific contract that proves the **primary** interval is present, correctly formatted, and consistent across every intended publication surface—and that fails when the primary interval is absent even if a secondary 0.7xx interval remains.

### Correct assurance end state

The test should establish all of these facts independently:

- the 40 g primary range is loaded from the current artifact;
- the expected publication string is created by the same formatter used in production;
- the string occurs in each explicitly required semantic block;
- the required blocks are non-empty and unique where uniqueness is expected;
- the primary scheme name and endpoint accompany the interval so an unrelated interval cannot satisfy the assertion;
- approved alternative representations, if any, are explicit rather than regex-permissive; and
- changing a secondary interval cannot mask a missing or malformed primary interval.

### Files and components to inspect

- `tests/test_paper_a_model_contract.py`;
- the current `PROSE` path list and primary-range regex;
- proposed shared formatter in `puckworks/paper_a/transfer_contract.py`;
- proposed marked blocks generated by `tools/paper_a_transfer_text.py`;
- manuscript Results and Table 5;
- supplement sensitivity table;
- standalone captions if the interval is required there;
- package text only if it deliberately repeats the interval.

### Method

#### Step 1 — Define where the primary interval is actually required

Create an explicit mapping rather than scanning arbitrary files:

```python
REQUIRED_PRIMARY_INTERVAL_BLOCKS = {
    "manuscript_results": (
        Path("docs/submission/PAPER_A_JFE_MANUSCRIPT.md"),
        "paper-a:transfer-results",
    ),
    "manuscript_table5": (
        Path("docs/submission/PAPER_A_JFE_MANUSCRIPT.md"),
        "paper-a:transfer-table",
    ),
    "supplement_resampling": (
        Path("docs/submission/PAPER_A_JFE_SUPPLEMENT.md"),
        "paper-a:transfer-resampling-table",
    ),
}
```

Do not require redundant copies merely to make a test pass. If the interval does not belong in the package checklist or caption, remove the duplicate rather than binding it.

#### Step 2 — Load the current primary row semantically

Select the row using structured keys:

```text
endpoint quantity = collected_mass
m_target_g = 40.0
scheme = artifact.resampling_design.primary_scheme
interval kind = fixed_predictor_clustered_percentile_sensitivity_range
```

Do not rely on “the first row,” “the interval beginning with 0.8,” or a hard-coded list position.

#### Step 3 — Use the production formatter

Implement and test a shared function such as:

```python
format_pp_range(lower, upper, digits=3, explicit_plus=True)
```

The generated Results and tests should both call it. The formatter owns Unicode minus, plus-sign, spacing, brackets, unit suffix policy, and negative-zero display normalization.

The test expectation should be the artifact's current **display rendering**, while a separate test proves that the artifact display rendering reconciles with its full-precision values.

#### Step 4 — Parse marked blocks rather than whole files

Write a small robust marker extractor. It must fail when:

- the begin marker is absent;
- the end marker is absent;
- markers are duplicated unexpectedly;
- the block is empty; or
- markers are nested incorrectly.

Then assert, for each required block:

```text
primary scheme label is present
40 g endpoint label is present
exact formatted primary interval is present
occurrence count satisfies the declared cardinality
manifest/schema stamp matches the artifact
```

Exact normalized block equality is preferable for fully generated tables. For mixed editorial/generated paragraphs, assert against a generated sub-block with stable markers.

#### Step 5 — Detect unapproved alternative renderings

Construct a set of common incorrect alternatives from the artifact values:

- wrong digit counts;
- ASCII hyphen instead of Unicode minus, if typography is mandatory;
- missing explicit plus sign;
- reversed bounds;
- rounded-to-two-decimal form;
- full-precision form printed where a display form is required; and
- an old committed primary interval.

Search only the target blocks, not every repository file. Historical reviews and code examples may legitimately contain alternative strings.

#### Step 6 — Add true mutation tests

Use temporary copies or a test fixture to mutate the target block and run the actual validator. Required mutations:

1. `−0.825` changed to `−0.824`;
2. `+0.000` changed to `+0.00`;
3. primary interval removed entirely;
4. primary scheme label changed to a secondary scheme;
5. endpoint changed from 40 g to 38 g while interval remains;
6. secondary interval changed while primary stays correct—test must still pass;
7. secondary interval remains while primary is removed—test must fail; and
8. marker block becomes empty—test must fail.

This directly guards the vacuous-pass defect identified in Round 8.

### Potential pitfalls, errors, and oversights

1. **Using the same broad regex with a different number.** The core defect is semantic targeting, not merely the `0.7` literal.
2. **Allowing zero matches.** Every required-block assertion must explicitly require at least one occurrence.
3. **Scanning entire files.** An unrelated interval in a reference, comment, or secondary table can satisfy the test.
4. **Hard-coding current values in the test.** Load values from the artifact; independently validate the artifact against the producer.
5. **Letting the formatter and parser disagree on Unicode.** Normalize line endings and only the typography explicitly permitted.
6. **Making typography the sole scientific check.** A correctly formatted wrong value must fail.
7. **Accepting multiple primary blocks accidentally.** Duplicate generated sections can create contradictory text while a simple `in` test passes.
8. **Forcing the interval into files where it is editorially unnecessary.** Minimize copies; bind the copies that have a scientific purpose.
9. **Ignoring endpoint context.** The 38, 40, and 42 g rows can have similar values; the test must bind endpoint and interval together.
10. **Ignoring scheme context.** A secondary interval should never satisfy the primary contract.
11. **Testing a helper rather than the CLI/build path.** At least one integration test must run the same checker used in CI.
12. **Silently accepting old and new formats.** If multiple formats are permitted, enumerate and justify them explicitly.

### Automated checks

Recommended test organization:

```text
tests/test_paper_a_transfer_formatting.py
tests/test_paper_a_transfer_publication_blocks.py
tests/test_paper_a_transfer_mutations.py
```

Required tests:

```text
test_primary_40g_interval_is_rendered_by_shared_formatter
test_primary_interval_exists_in_every_required_block
test_primary_interval_occurrence_count_is_nonzero
test_primary_interval_is_bound_to_primary_scheme_and_40g_endpoint
test_generated_blocks_have_unique_well_formed_markers
test_unapproved_primary_renderings_are_absent_from_active_blocks
test_secondary_interval_cannot_satisfy_primary_contract
test_empty_or_missing_block_fails_validation
```

### Manual checks

- Read the relevant blocks and confirm that the exact interval appears in a scientifically intelligible sentence or table row.
- Inspect the journal-rendered typography for minus signs, plus signs, and negative zero.
- Verify that the supplement and manuscript use the same endpoint and scheme labels.
- Confirm that the package is not needlessly repeating the interval.

### Definition of done and evidence to retain

P1-3 is closed only when:

- the old numeric-family regex is removed;
- all expected occurrences are loaded from the artifact and rendered by the production formatter;
- tests are block-specific, non-vacuous, and endpoint/scheme-aware;
- every required mutation produces a failure;
- changing only a secondary range cannot hide a broken primary range; and
- the CI command exercises the same validator used during publication generation.

---

## 5.7 P1-4 — The corpus semantic contract does not bind exact sample membership

### Objective

Establish a canonical, source-derived corpus manifest and bind its estimand, counts, included IDs, excluded IDs, off-grid membership, lookup support, and stable fingerprint to the producer, artifacts, manuscript, supplement, caption, and package.

### Correct assurance end state

The complete-corpus contract should contain and validate at least:

```text
estimand identifier
include_off_grid = true
n_held_out_records = 44
n_observations = 132
three named solutes per included record
sorted included sample IDs
sorted excluded sample IDs = []
sorted off-grid sample IDs
sorted lookup-undefined sample IDs
sample-ID hash
full manifest hash
source-data hash
```

The source-to-artifact test must prove those fields from the source data. Publication-facing files should carry the visible counts/estimand and an invisible stable fingerprint or generated-block stamp.

### Files and components to inspect

- `puckworks/data/angeloni2023/bioactives.csv`;
- `PAPER_A_ENDPOINT_PROPAGATION.json`;
- `PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`;
- `PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json`;
- manuscript and supplement corpus descriptions;
- `docs/figures/PAPER_A_CAPTIONS.md`;
- package status text;
- existing phrase-based tests in `test_paper_a_model_contract.py`;
- lookup-comparator code and support flags.

### Method

#### Step 1 — Build one canonical manifest function

Create one pure function such as:

```python
build_transfer_corpus_manifest(source_rows, include_off_grid=True)
```

It should produce a canonical record for each included C/F sample:

```json
{
  "sample_id": "A21",
  "variety": "Arabica",
  "grind": "C",
  "temperature_degC": 89,
  "pressure_bar": 10,
  "on_grid": false,
  "lookup_defined": false,
  "solutes": ["<solute A>", "<solute B>", "<solute C>"]
}
```

Use actual source solute names and normalized source values. The function should be the sole owner of inclusion logic.

#### Step 2 — Canonicalize before hashing

Sort records by a declared tuple, for example:

```text
(variety, grind, sample_id, temperature_degC, pressure_bar)
```

Sort solute names within each record by the source's declared canonical order. Serialize with stable separators, UTF-8, no timestamp, and no platform-dependent float representation.

Generate at least:

```text
included_sample_ids_sha256
full_manifest_sha256
source_file_sha256
```

A simple reproducible implementation is:

```python
payload = json.dumps(
    manifest_records,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
manifest_sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

The sample-ID hash catches membership drift efficiently; the full-manifest hash also catches changed metadata under unchanged IDs.

#### Step 3 — Choose one canonical home

Avoid maintaining two independently assembled corpus manifests in endpoint and corpus artifacts. Recommended options, in descending preference:

1. maintain a canonical manifest object in `PAPER_A_TRANSFER_CORPUS_CONTRACTS.json` and embed an exact copy plus matching hash in endpoint/robustness artifacts;
2. create a dedicated `PAPER_A_TRANSFER_CORPUS_MANIFEST.json` referenced by hash from all result artifacts; or
3. embed the exact same object in all artifacts and test normalized equality.

Do not merely repeat counts in multiple files.

#### Step 4 — Bind the producer to the manifest

Before analysis, the producer should receive the manifest's observation IDs and fail if:

- a predicted or observed row is absent;
- an extra row appears;
- ordering changes the paired alignment;
- a sample lacks one of the three named solutes;
- an off-grid record is silently filtered; or
- an excluded-ID list is non-empty without an explicit configured reason.

The producer's result artifact should record the manifest hash actually used.

#### Step 5 — Bind visible publication claims

Generate the visible statements:

```text
44 C/F sample records
132 named-solute observations
includes eight off-grid records
complete held-out C/F corpus
```

from the manifest summary.

Add a source-level stamp to each generated block:

```html
<!-- paper-a:transfer-corpus manifest_sha256=<hash> n_records=44 n_observations=132 -->
```

The stamp prevents a different 44-record set from masquerading as the same corpus.

#### Step 6 — Publish the membership in the supplement

Add a generated supplementary corpus table listing all 44 sample records and their design metadata. This gives reviewers an auditable human-readable manifest rather than relying only on an invisible hash or repository JSON.

Recommended columns:

| Sample ID | Variety | Grind | T (°C) | p (bar) | On grid? | Lookup defined? | Primary cluster |
|---|---|---|---:|---:|---|---|---|

The table should state that each record contributes the same three named-solute observations, or list solutes if that assumption can vary.

#### Step 7 — Keep headline and lookup supports distinct

The manifest should expose two explicit support sets:

```text
headline_level_only_comparator_support: all 44 records / 132 observations
same_condition_lookup_support: matched-grid subset / 108 observations
lookup_undefined_ids: the eight off-grid records
```

Do not use one generic `n_observations` field for both analyses. Every result row should reference the support-set identifier it uses.

#### Step 8 — Replace phrase-only tests

Remove reliance on a prohibition such as “do not say all of it.” Such a phrase test may remain as an editorial lint, but it cannot be the corpus contract. Replace it with exact source→manifest and manifest→publication assertions.

### Potential pitfalls, errors, and oversights

1. **Binding only counts.** A different set of 44 records still passes.
2. **Hashing unsorted data.** Harmless row-order changes produce false differences.
3. **Hashing only IDs.** Condition metadata or grind assignment can change under the same IDs.
4. **Using a timestamp in the hashed payload.** Every run becomes non-deterministic.
5. **Duplicating manifest construction.** Endpoint and corpus artifacts can drift while retaining the same summary count.
6. **Conflating sample IDs and observation IDs.** One sample has three solute observations.
7. **Silently dropping a solute with missing data.** Validate exactly which solutes define the estimand.
8. **Treating excluded IDs as harmless.** An exclusion must have an explicit reason and should change the estimand/version.
9. **Forgetting the off-grid lookup limitation.** All 132 belong to the headline level-only comparison, but the lookup comparator is undefined for eight records.
10. **Allowing publication hashes to become stale after source regeneration.** Generated-block check mode must fail.
11. **Relying only on hidden comments.** Publish the human-readable membership table in the supplement.
12. **Making historical documents fail live-manifest tests.** Restrict active publication contracts to current submission paths.
13. **Changing source row normalization without a schema bump.** Canonicalization rules are part of the contract.
14. **Assuming case-insensitive IDs.** Treat source identifiers exactly and validate normalization deliberately.
15. **Letting count text appear outside the generated block.** A stale manual duplicate can contradict the correct block.

### Automated checks

Source-to-manifest tests:

```text
test_manifest_is_reconstructed_from_source_data
test_manifest_has_44_records_and_132_observations
test_manifest_includes_exact_expected_off_grid_ids
test_manifest_has_no_unexplained_exclusions
test_each_record_has_canonical_three_solutes
test_sample_id_and_full_manifest_hashes_are_stable
test_lookup_support_is_108_and_lookup_undefined_ids_are_exact
```

Manifest-to-artifact tests:

```text
test_all_transfer_artifacts_reference_same_manifest_hash
test_embedded_manifest_copies_are_normalized_equal
test_result_observation_ids_equal_manifest_observation_ids
test_no_result_uses_an_undeclared_support_set
```

Manifest-to-publication tests:

```text
test_manuscript_corpus_block_matches_manifest_summary_and_hash
test_supplement_manifest_table_matches_manifest
test_standalone_caption_matches_manifest_summary_and_hash
test_package_does_not_assert_a_conflicting_corpus
test_no_active_108_point_text_is_unlabelled_as_matched_grid
```

Mutation tests:

- remove one off-grid ID;
- replace one included ID while preserving 44 records;
- change 132 to 108 in the caption;
- change a sample's grind or condition while preserving IDs;
- leave the visible count correct but alter the manifest stamp;
- duplicate one solute and omit another;
- add an excluded ID without a reason; and
- point one result artifact to a different manifest hash.

### Manual checks

- Compare the supplementary table line by line with the source CSV for a sample from every variety/grind/on-grid category.
- Inspect all eight off-grid records.
- Read every use of “complete,” “all,” “held-out,” and “matched-grid” in context.
- Confirm that the caption remains correct if detached from the manuscript.
- Verify that the journal supplement includes the membership table or an accessible equivalent.

### Definition of done and evidence to retain

P1-4 is closed only when:

- one canonical source-derived manifest exists;
- all result artifacts reference the same hash;
- the visible corpus claims and source stamps are generated from that manifest;
- exact membership is published in the supplement;
- headline and lookup support sets are distinct;
- phrase-only assurance is no longer treated as the corpus contract;
- all count-, membership-, metadata-, and hash-mutation tests fail correctly; and
- the final package contains no unlabelled 108-observation headline claim.

---

## 5.8 P1-5 — Figure 1 serializes analyses that are actually parallel

### Objective

Redraw Figure 1 so every arrow represents a genuine data or fitted-parameter dependency, explicitly distinguish the fold-specific LOCO calibration from the full-O calibration frozen for C/F transfer, and prevent the incorrect LOCO→C/F dependency from returning.

### Correct scientific end state

The design graph should communicate:

- source kinetics or governing parameters support the relevant prediction branches;
- Angeloni O observations and endpoint/inventory information support two **parallel** within-campaign analyses;
- the LOCO branch repeatedly fits eight of nine O conditions and predicts the omitted O condition;
- the C/F transfer branch fits all nine O conditions once and freezes that calibration before C/F response evaluation;
- C/F transfer does not consume the LOCO output;
- the external Waszkiewicz trajectory is a separate branch with its own data and level profiling, not a child of Angeloni LOCO or C/F validation; and
- arrow style has one documented meaning.

### Files and components to inspect

- Figure 1 generation in `puckworks/figures_paper_a.py`, especially the reviewed `fig1_design` function;
- Figure 1 caption in `docs/figures/PAPER_A_CAPTIONS.md`;
- manuscript study-design section;
- Figure 1 tests or export tests;
- any slide, README, or supplementary diagram derived from the same geometry.

### Method

#### Step 1 — Define the graph as data

Move node and edge semantics out of plotting coordinates. For example:

```python
FIG1_NODES = {
    "source_kinetics": {"label": "Source kinetic structure / governing parameters"},
    "angeloni_o_data": {"label": "Angeloni optimal-grind observations"},
    "inventory_endpoint": {"label": "Inventory assay and matched collected-mass endpoint"},
    "loco_fit": {"label": "LOCO calibration: fit 8/9 O conditions per fold"},
    "loco_holdout": {"label": "Held-out O prediction"},
    "full_o_fit": {"label": "Full O calibration: fit 9/9 O conditions once"},
    "cf_transfer": {"label": "Frozen coarse/fine transfer: 44 records / 132 observations"},
    "external_data": {"label": "Waszkiewicz external trajectory"},
    "external_profile": {"label": "Target-specific external level profile; source kinetics frozen"},
}

FIG1_EDGES = {
    ("source_kinetics", "loco_fit"),
    ("angeloni_o_data", "loco_fit"),
    ("inventory_endpoint", "loco_fit"),
    ("loco_fit", "loco_holdout"),
    ("source_kinetics", "full_o_fit"),
    ("angeloni_o_data", "full_o_fit"),
    ("inventory_endpoint", "full_o_fit"),
    ("full_o_fit", "cf_transfer"),
    ("source_kinetics", "external_profile"),
    ("external_data", "external_profile"),
}
```

This is illustrative; reconcile exact scientific nodes with the implemented model. The critical forbidden edge is:

```python
("loco_holdout", "cf_transfer")
```

or any equivalent LOCO-output→C/F edge.

#### Step 2 — Distinguish data, fit, and evaluation nodes

Use clear node labels rather than relying on color alone. A reader should see where fitting occurs and which parameters are frozen. Recommended branch labels:

```text
LOCO: 8/9 O fit per fold → omitted O prediction
C/F transfer: 9/9 O fit once → freeze → C/F evaluation
```

If different line styles indicate different dependency types, define them in a legend and use them consistently:

- solid: data or fitted-parameter dependency;
- dashed: shared fixed source structure or contextual relationship;
- no arrow: merely adjacent analyses.

Do not use arrow direction to show chronological narration if the caption says arrows show dependency.

#### Step 3 — Place inventory/endpoint information correctly

Inventory assay and target recalibration should feed the relevant calibration/profile operation. They should not appear downstream of held-out prediction. If inventory is used differently across branches, draw separate labelled inputs rather than a vague serial chain.

#### Step 4 — Keep external evidence independent

The external trajectory should branch from the source kinetic structure and its own external measurements/profile fit. It should not visually inherit Angeloni target calibration, LOCO output, or C/F transfer results.

#### Step 5 — Generate the caption from graph semantics

Recommended caption core:

> Arrows denote data or fitted-parameter dependency, not merely analysis order. The Angeloni optimal-grind data support two parallel analyses: fold-specific 8/9-condition calibration for held-out optimal-grind LOCO prediction, and one 9/9-condition calibration frozen before evaluation on the complete C/F corpus. The C/F branch does not use the LOCO output. The Waszkiewicz trajectory is an independent external-data branch with source kinetic structure frozen and target-specific level profiling as described in Methods.

If the final graph uses multiple edge styles, define each in the caption.

#### Step 6 — Add semantic graph tests

Test the node/edge data before rendering:

```text
required nodes exist
required edges exist
forbidden LOCO→C/F edge does not exist
C/F has full-O calibration as an ancestor
LOCO and C/F share appropriate upstream data but neither is ancestor of the other
external branch has no Angeloni-validation ancestor
all rendered edges refer to declared nodes
caption edge semantics match graph metadata
```

A small directed-acyclic-graph utility or `networkx` is optional; this can be tested with plain sets and ancestor traversal.

#### Step 7 — Render at final size and inspect

Render both a full-resolution review version and the journal-intended width. Check:

- branch separation;
- arrowheads;
- label legibility;
- no crossed or ambiguous arrows;
- clear fit/freeze distinction; and
- color-independent interpretation.

### Potential pitfalls, errors, and oversights

1. **Changing labels but leaving the wrong arrow.** Geometry, not wording alone, caused the finding.
2. **Replacing the arrow with an unlabeled shared box that still implies sequence.** Branch explicitly.
3. **Using chronology and dependency interchangeably.** Pick one semantic meaning and state it.
4. **Showing C/F as a child of “held-out validation.”** It is a separate evaluation using a different calibration instance.
5. **Conflating target recalibration with LOCO output.** Show the actual parameter/data flow.
6. **Making external evidence appear downstream of Angeloni calibration.** Preserve independent evidence provenance.
7. **Encoding meaning only by color.** Use labels, line styles, or geometry that remain clear in grayscale.
8. **Letting layout code define semantics.** Keep node/edge data separate from coordinates.
9. **Testing only image existence.** An exported PNG can exist with the wrong scientific graph.
10. **Allowing caption and edge styles to diverge.** Generate or validate caption terminology from graph metadata.
11. **Overcrowding the figure with implementation detail.** Put exact parameter names in Methods; retain only dependency-critical distinctions in the figure.
12. **Failing to update alternate exports.** Regenerate PNG, vector/PDF, manuscript inclusion, and any standalone figure package.

### Automated checks

```text
test_fig1_required_nodes_and_edges
test_fig1_has_no_loco_to_cf_dependency
test_fig1_loco_and_cf_are_parallel_descendants
test_fig1_cf_depends_on_full_o_fit
test_fig1_external_branch_is_independent_of_angeloni_validation
test_fig1_graph_is_acyclic
test_fig1_caption_semantics_match_graph_metadata
test_fig1_all_expected_exports_are_current
```

Mutation tests should add the forbidden edge, remove the full-O→C/F edge, connect external profiling to LOCO, or change an edge style without updating the caption. Each must fail.

### Manual checks

- Ask a reader unfamiliar with the code to explain the graph. They should not say that C/F transfer uses LOCO predictions.
- Compare the graph with the Methods fit/freeze sequence.
- Inspect the figure in grayscale and at journal width.
- Verify every arrow against a concrete data or parameter dependency in code.

### Definition of done and evidence to retain

P1-5 is closed only when:

- LOCO and C/F are parallel branches with explicit 8/9 and 9/9 calibration scopes;
- no direct or implied LOCO→C/F dependency remains;
- external evidence has independent provenance;
- graph semantics are represented as testable data;
- the caption accurately defines arrows and branch logic;
- all image exports are regenerated; and
- before/after figures plus the semantic edge test are included in the pull request.

---
## 5.9 P2-1 — Round 8 brief contains a stale and arithmetically inconsistent coverage count

### Objective

Correct the Round 8 brief to the commit-pinned coverage state—89 bound and 6 unbound out of 95—while preventing future review briefs from drifting either through manual copying or through inappropriate linkage to a later live repository state.

### Correct governance end state

For the reviewed commit, the brief should report:

```text
registered: 95
bound and matching: 89
mismatched: 0
unresolvable: 0
declared unbindable: 0
unbound: 6
```

All categories must reconcile to the registered total under the audit's actual category definitions.

A historical review brief must remain a snapshot of its target commit. It should not change when a later branch binds more claims.

### Files and components to inspect

- `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md`;
- `docs/CLAIM_BINDING_AUDIT.md` and any machine-readable audit output;
- `puckworks/paper_a/slow_lane_bindings.py`;
- `tools/claim_binding_audit.py`;
- any brief-generation or review-resource tool;
- tests for claim-binding arithmetic and brief metadata.

### Method

#### Step 1 — Verify the target-commit snapshot

Regenerate the claim-binding audit at the review target commit or inspect the commit-pinned machine-readable audit. Confirm that the category definitions and counts are exactly those above.

Do not substitute current-main counts if they differ. The brief documents the state reviewed at `21b138a...`.

#### Step 2 — Correct both stale occurrences

The review identified the count in the main coverage statement and in the known-open-item repetition. Update both to 6 of 95, or remove the redundant second copy and link it internally to one generated block.

#### Step 3 — Introduce a commit-pinned coverage snapshot

Preferred implementation:

- have `claim_binding_audit.py` emit a stable JSON summary containing the audited commit/tree and category counts;
- when a review brief is created, copy or reference that exact snapshot under `docs/paper1_resource/`;
- generate a marked coverage block from the snapshot;
- record the target commit in the block.

Illustrative object:

```json
{
  "review_target_commit": "21b138a1fa8866db0b65c59b541b766498e63ed4",
  "registered": 95,
  "bound_matching": 89,
  "mismatched": 0,
  "unresolvable": 0,
  "declared_unbindable": 0,
  "unbound": 6
}
```

Do not point the historical Round 8 brief directly to a live file that will change after later work.

#### Step 4 — Add reconciliation assertions

The audit tool should define one authoritative reconciliation function based on its category model. For the reviewed categories:

```text
registered = bound_matching + mismatched + unresolvable + declared_unbindable + unbound
```

If some categories are subsets rather than disjoint in the actual implementation, encode that explicitly and test the correct relationship. Do not add numbers that happen to look compatible without understanding the audit semantics.

#### Step 5 — Generate future brief blocks

Provide a helper that writes:

- target commit;
- generated audit artifact path/hash;
- coverage counts;
- arithmetic reconciliation; and
- unresolved claim identifiers, if appropriate.

This makes review briefs reproducible while preserving their historical state.

### Potential pitfalls, errors, and oversights

1. **Updating only one occurrence.** The known-open list can remain stale.
2. **Replacing the historical count with current main.** A review brief must describe its target commit.
3. **Dynamically regenerating old briefs in CI.** Later repository progress would rewrite historical evidence.
4. **Assuming categories are disjoint without checking.** Reconciliation must follow the audit's actual model.
5. **Counting declared unbindable values twice.** Determine whether they are included in “bound,” “registered,” or a separate status.
6. **Hard-coding 95 in multiple tools.** Read the registry and calculate the total.
7. **Treating the brief as the source of truth.** The generated audit/snapshot owns the count.
8. **Failing to record the commit.** A correct count without a target state is ambiguous.
9. **Silently editing previous review history.** Commit the correction with a note that the prior brief count was erroneous.
10. **Allowing an arithmetic test to pass on missing categories.** Require all expected keys and validate non-negative integers.

### Automated checks

```text
test_claim_binding_categories_reconcile_to_registered_total
test_round8_snapshot_matches_target_commit_audit
test_round8_brief_coverage_block_matches_snapshot
test_historical_brief_is_not_compared_with_live_main_counts
test_coverage_snapshot_contains_all_required_categories
test_duplicate_stale_11_of_95_text_is_absent
```

Mutation tests should change 6 to 11, change the target commit, omit a category, or make the arithmetic sum 100. Each should fail with a clear message.

### Manual checks

- Confirm the six unbound claim identifiers in the target audit, not only the aggregate count.
- Verify that the brief clearly distinguishes “known open” from “mismatched” or “unresolvable.”
- Ensure the correction does not rewrite the scientific review findings themselves.

### Definition of done and evidence to retain

P2-1 is closed only when:

- every Round 8 brief occurrence reports 6 of 95;
- the count is backed by a commit-pinned snapshot;
- reconciliation tests pass;
- current-main changes cannot mutate the historical brief; and
- the correction commit explains why the previous 11 was wrong.

---

## 5.10 P2-2 — Supplementary Figure S3 panel titles overlap

### Objective

Produce a publication-ready S3 figure whose panel titles, global title, axes, legends, and caption remain legible and non-overlapping at the journal's intended output width.

### Correct presentation end state

Recommended title allocation:

```text
Panel (a): Blind vs inventory-matched MAPE
Panel (b): Cross-condition response correlation
Suptitle: Per-group residual diagnostics at matched 40 g endpoint
```

Move details such as `n = 9`, “not a temporal trajectory,” exact endpoint explanation, and methodological caveats into the caption or panel annotations rather than packing them into title lines.

### Files and components to inspect

- `fig7_per_group_diagnostics` in `puckworks/figures_paper_a.py` or its successor;
- S3 caption in `docs/figures/PAPER_A_CAPTIONS.md` and supplement;
- figure export configuration and dimensions;
- `tests/test_figure_exports.py` and any image-layout tests;
- vector and raster exports.

### Method

#### Step 1 — Define final publication dimensions first

Obtain or select the journal-relevant single- or double-column width and intended font size. Configure the figure in physical units rather than merely increasing pixel count. An image that looks fine full-screen can still overlap when placed at 170 mm or 85 mm width.

#### Step 2 — Shorten title text

Use compact titles with panel letters. Transfer explanation to the caption. Avoid manual line breaks that work only at one font or export width.

#### Step 3 — Adjust layout deliberately

Use either `constrained_layout` from figure creation or explicit `subplots_adjust`, but test the interaction with the suptitle. An illustrative explicit adjustment is:

```python
fig.subplots_adjust(
    left=0.10,
    right=0.98,
    bottom=0.20,
    top=0.80,
    wspace=0.30,
)
```

The final values should come from the actual rendered figure. If `tight_layout` is used, reserve a rectangle for the suptitle; do not call layout functions in an order that later moves titles back into collision.

#### Step 4 — Move explanatory details to the caption

The caption should state:

- what “blind” and “inventory-matched” mean;
- the number and nature of groups/conditions;
- that panel (b) is cross-condition association rather than a temporal trajectory;
- the matched 40 g endpoint; and
- any caution about small group count or interpretive limits.

Do not remove necessary context merely to make the figure fit.

#### Step 5 — Add a render-time bounding-box check

Refactor the figure builder so tests can obtain the `Figure` object before closing. After drawing the canvas:

```python
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
boxes = [title.get_window_extent(renderer) for title in panel_titles]
```

Assert that:

- panel-title bounding boxes do not overlap one another;
- each title remains within the figure canvas;
- titles do not overlap the suptitle;
- legends remain within their assigned region; and
- axes labels are not clipped.

Allow a small pixel margin rather than testing exact coordinates.

#### Step 6 — Export raster and vector versions

Regenerate all committed versions. Inspect the vector/PDF or SVG export as well as PNG because font metrics and clipping can differ.

### Potential pitfalls, errors, and oversights

1. **Increasing DPI without changing layout.** DPI improves resolution, not physical spacing.
2. **Adding manual newline characters only.** A different export width or font can recreate the collision.
3. **Using `tight_layout` after positioning the suptitle.** The title can be clipped or moved unexpectedly.
4. **Shortening away scientific meaning.** Put necessary detail in the caption.
5. **Testing only one backend.** Raster and vector renderers can have different font extents.
6. **Checking at full-screen size only.** Approval must occur at journal placement size.
7. **Allowing long tick labels or legends to create a new collision.** Inspect the whole figure.
8. **Making panel titles inconsistent with caption terminology.** Use shared labels or test them.
9. **Changing data while refactoring layout.** Compare plotted data arrays or image annotations before and after.
10. **Closing the figure before layout tests.** Return or expose the figure object to the test.
11. **Overfitting exact pixel coordinates.** Test non-overlap and containment with tolerances.
12. **Forgetting accessibility.** Ensure panel identity is not conveyed by color alone.

### Automated checks

```text
test_s3_panel_titles_do_not_overlap
test_s3_titles_and_labels_are_inside_canvas
test_s3_suptitle_does_not_overlap_panel_titles
test_s3_required_caption_details_are_present
test_s3_plotted_data_are_unchanged_by_layout_refactor
test_s3_raster_and_vector_exports_exist_and_are_current
```

A lightweight image-dimension check is not sufficient; use artist bounding boxes or an equivalent render-aware method.

### Manual checks

- Print or display S3 at the intended physical width and 100% scale.
- Inspect both raster and vector exports.
- Confirm that panel titles remain distinguishable in grayscale.
- Read the caption independently and verify that moved explanatory details were not lost.
- Compare before/after plots to ensure only presentation changed.

### Definition of done and evidence to retain

P2-2 is closed only when:

- titles no longer overlap at journal width;
- explanation removed from titles appears in the caption;
- automated bounding-box checks pass;
- data and axes remain unchanged except for deliberate presentation adjustments;
- all export formats are regenerated; and
- a before/after figure pair at final size is included in the pull request.

---
# 6. Non-regression guardrails for areas found clean or materially improved

The Round 8 correction must not reopen issues that were found resolved. Add or retain targeted guardrails for the following areas.

## 6.1 Reynolds-number definition

### Preserve

- the superficial-velocity definition;
- the equivalent interstitial-velocity form with the correct porosity factor; and
- consistency between manuscript equation, symbol definitions, and executable model.

### Checks

- symbolic or value-level equivalence test for the two forms;
- manuscript equation token/structured-block check;
- no alternative Reynolds definition introduced in a figure caption or supplement;
- dimensional consistency test where feasible.

### Pitfall

A broad Methods rewrite around the resampling section should not accidentally alter nearby governing-equation text or regenerate an older equation block.

## 6.2 Endpoint mass in the scientific manuscript and supplement

### Preserve

The main scientific content already uses grams. P0-3 should extend that correctness into the package and release layers, not alter the underlying endpoint back to volume or apply a numerical conversion.

### Checks

- manuscript, supplement, Results tables, and captions identify 38/40/42 g;
- any legitimate mL reference elsewhere is contextually unrelated to collected endpoint;
- no “converted from 40 mL” language is introduced without source justification.

## 6.3 Complete corpus and comparator roles

### Preserve

- complete C/F corpus as headline support;
- 108-observation matched-grid support only for the lookup comparator;
- level-only comparator as O-trained, frozen, response-free, and deliberately weak;
- no portrayal of the level-only comparator as a statistical null.

### Checks

- result rows carry support-set IDs;
- comparator configuration is archived;
- no C/F response enters comparator fitting;
- lookup undefined IDs match the eight off-grid records.

## 6.4 Identifiability and objective-family methods

### Preserve

- distinction among ordinary least squares, weighted least squares, and IRLS;
- distinction between profile tolerance sets and confidence regions;
- separation of parameter localization, absolute prediction error, benchmark skill, and evidence tier.

### Checks

- terminology scan for accidental “confidence region” substitution;
- objective-method table remains synchronized with code;
- resampling edits do not imply that tolerance profiles are inferential intervals.

## 6.5 Evidence hierarchy and external trajectory

### Preserve

- C/F benchmark as within-campaign cross-grind holdout, not external validation;
- Waszkiewicz trajectory as a separate rig/coffee and separate evidence branch;
- target-specific level profiling and frozen source kinetics for the external panel;
- limitations concerning one coffee/grind, TDS proxy, high/loss-dependent error, and level refitting.

### Checks

- Figure 1 correction preserves the external branch's independence;
- abstract and conclusion do not upgrade within-campaign evidence to external validation;
- external-panel limitations survive generated-text updates.

## 6.6 Other figure integrity

The review found the current transfer figure numerically concordant and Figures 2, 3/LOCO, 4, S1, S2, and S4 broadly legible. Regeneration must include an image/data regression check so that correcting Figure 1 and S3 does not alter unrelated plotted data.

Recommended checks:

- compare underlying plotted arrays, not only image pixels;
- verify expected figure count and filenames;
- verify raster/vector exports;
- inspect every figure after the final regeneration command.

---

# 7. File-by-file implementation map

This section translates the findings into concrete repository work. Paths should be adjusted only if the repository has since reorganized; the responsibilities should remain.

## 7.1 New: `puckworks/paper_a/transfer_contract.py`

### Add

- endpoint schema constants and validator;
- corpus-manifest builder and canonical hashing;
- support-set definitions;
- resampling-scheme dataclasses or typed dictionaries;
- cluster-membership builder;
- full-precision interval result object;
- display formatter and negative-zero normalization;
- interpretation-state builder;
- validation functions that raise precise, actionable errors.

### Do not add

- manuscript-specific paragraph prose beyond small formatting primitives;
- timestamps in the deterministic scientific payload;
- backward-compatible acceptance of volume endpoint keys;
- outcome-dependent primary-scheme logic.

## 7.2 Modify: `puckworks/validation/slow/angeloni_bracket.py`

### Change

- import contract definitions rather than re-declaring endpoint/resampling semantics;
- construct losses against the canonical manifest observation order;
- add sample-record resampling sensitivity;
- retain signed full-precision interval bounds;
- derive analytical flags before display formatting;
- replace ambiguous `conclusion_stable` with explicit stability dimensions;
- expose deterministic repetition count, RNG, seed, quantile method, and cluster design;
- update docstrings to remove universal both-grind and “actual dependence structure” claims;
- return enough information for one atomic artifact writer.

### Validate

- no refitting occurs within the fixed-predictor sensitivity procedure;
- point estimate remains common across schemes;
- off-grid records remain included;
- lookup comparator remains support-limited.

## 7.3 New: `tools/paper_a_transfer_artifacts.py`

### Add

- `--check` and `--write` modes;
- source-data validation;
- deterministic generation of all transfer-related artifacts;
- atomic multi-file writes;
- normalized object comparison;
- concise diff diagnostics showing path and changed field;
- exit codes suitable for CI.

### Recommended behavior

`--check` must not modify the tree. `--write` must not partially update one artifact if another fails validation.

## 7.4 Modify or consolidate: transfer JSON artifacts

### Required schema content

- `schema_version`;
- source-data and producer/configuration fingerprints;
- collected-mass endpoint object;
- canonical corpus/support manifest and hash reference;
- explicit resampling design and membership hash;
- full-precision and display interval fields;
- RNG, seed, `B`, quantile method;
- explicit stability dimensions;
- support-set identifier per result;
- no ambiguous volume endpoint field.

### Required reconciliation

All artifacts must reference the same corpus manifest and final resampling design. A change in one must make `--check` fail for the others.

## 7.5 New: `tools/paper_a_transfer_text.py`

### Add generated blocks for

- Methods resampling design;
- supplementary method table;
- complete-corpus Results summary;
- endpoint/knife-edge interpretation;
- transfer caption;
- supplementary corpus membership table;
- package endpoint-status line;
- optionally Table 5, if it is currently manually maintained.

### Constraints

- preserve author-written surrounding discussion;
- include schema/manifest stamps in source comments;
- support `--check` and `--write`;
- fail on missing/duplicate markers;
- use shared formatters only.

## 7.6 Modify: `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`

### Required changes

- replace stale two-scheme Methods block;
- state 18 six-observation and eight three-observation primary clusters;
- describe the primary as conservative sensitivity;
- add sample-record sensitivity and final scheme table/result;
- correct the “both narrower” statement;
- replace inferential/distinguishability wording;
- ensure headline corpus values are generated;
- retain clean governing-model, identifiability, and evidence-tier material.

### Audit

Search the entire document, including abstract, table notes, conclusion, and figure callouts—not only the identified Results paragraph.

## 7.7 Modify: `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`

### Required changes

- add exact resampling-design table;
- add 44-record corpus membership table;
- report full-precision versus display-bound semantics as appropriate;
- include Monte Carlo stability summary;
- correct any stale inference language;
- preserve objective-family and profile-tolerance distinctions.

## 7.8 Modify: `docs/figures/PAPER_A_CAPTIONS.md`

### Required changes

- regenerate transfer caption from complete-corpus artifact;
- update Figure 1 caption to define parallel dependency branches;
- update S3 caption with details removed from titles;
- include correct sensitivity-range terminology;
- avoid duplicating values unnecessarily outside generated blocks.

## 7.9 Modify: `docs/submission/PAPER_A_JFE_PACKAGE.md`

### Required changes

- replace 38/40/42 mL with collected-mass targets in grams;
- identify artifact/schema version or completion status;
- remove redundant result claims that belong in manuscript/caption;
- keep final metadata status separate from scientific verification.

## 7.10 Modify: `puckworks/paper_a/build.py`

### Required changes

- correct active mL endpoint labels and comments;
- derive endpoint-mass claim labels from the endpoint contract;
- ensure generated blocks are checked before package build;
- include transfer artifact `--check` and text `--check` in build verification;
- avoid hard-coded 38/40/42 copies where possible.

## 7.11 Modify: `puckworks/paper_a/claim_coverage.py`

### Required changes

- correct endpoint-mass descriptions to grams;
- bind claims to schema fields rather than prose-only labels;
- regenerate claim audit after changes;
- ensure current transfer/corpus/interval claims point to the new artifacts and marked blocks.

## 7.12 Modify: `tools/paper_a_consistency.py`

### Required changes

- validate collected-mass endpoint schema;
- reject `v_targets` and active endpoint mL fields;
- move endpoint and corpus science checks into routine `verify`;
- make `submission` a strict superset of `verify`;
- replace magic-phrase checking with structured state/generated-block checks;
- validate marked-block uniqueness and freshness;
- emit field-specific errors.

## 7.13 Modify: `puckworks/figures_paper_a.py`

### Required changes

- represent Figure 1 nodes/edges as semantic data;
- remove LOCO→C/F edge and branch both from their proper calibration inputs;
- label 8/9 fold fit and 9/9 full fit/freeze explicitly;
- shorten S3 titles and revise layout;
- expose figure objects/data for testing;
- regenerate all figure exports without changing unrelated data.

## 7.14 Modify: `docs/paper1_resource/PAPER_1_REVIEW_BRIEF_ROUND_8.md`

### Required changes

- correct 11 of 95 to 6 of 95 in every occurrence;
- record or link the commit-pinned coverage snapshot;
- do not update the brief to a later live count.

## 7.15 Tests

Recommended focused files:

```text
tests/test_paper_a_transfer_contract.py
tests/test_paper_a_transfer_artifacts.py
tests/test_paper_a_transfer_publication_blocks.py
tests/test_paper_a_transfer_mutations.py
tests/test_paper_a_endpoint_schema.py
tests/test_paper_a_figure_semantics.py
tests/test_paper_a_figure_layout.py
```

Existing broad test files may remain, but the new scientific contracts should not be buried in one long mixed-purpose module.

---

# 8. Integrated verification strategy

## 8.1 Verification layers

| Layer | Question answered | Examples |
|---|---|---|
| Source-schema validation | Is the input data structurally what the analysis assumes? | unique sample IDs, three solutes, C/F support |
| Scientific unit tests | Does the producer implement the declared method? | paired resampling, no refit, full-precision flags |
| Source→artifact contracts | Do committed artifacts represent the source and producer? | counts, IDs, hashes, recomputed outputs |
| Artifact schema checks | Are fields complete, typed, versioned, and internally reconciled? | g endpoint, interval objects, stability dimensions |
| Artifact→publication contracts | Do visible claims match current artifacts? | Methods, Results, caption, tables, package |
| Mutation tests | Would the known failure mode actually be caught? | 132→108, `m_targets`→`v_targets`, empty regex target |
| Figure semantic tests | Does geometry encode the correct study design? | no LOCO→C/F edge |
| Figure layout tests | Is the rendered object publication-ready? | title bounding boxes |
| CLI/build integration | Does the user-facing verification path run all science checks? | `verify`, `submission`, build verify |
| Rendered-package audit | Did conversion preserve the corrected source? | final captions, units, figures, table values |

## 8.2 Finding-to-test traceability matrix

| Test family | P0-1 | P0-2 | P0-3 | P1-1 | P1-2 | P1-3 | P1-4 | P1-5 | P2-1 | P2-2 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Source corpus census | ✓ | ✓ |  | ✓ |  |  | ✓ |  |  |  |
| Artifact regeneration | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |  |
| Generated text blocks | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Endpoint schema negative tests |  |  | ✓ |  |  |  |  |  |  |  |
| Cluster membership tests |  | ✓ |  | ✓ |  |  | ✓ |  |  |  |
| Full/display precision tests |  |  |  |  | ✓ | ✓ |  |  |  |  |
| Mutation tests | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Figure graph tests |  |  |  |  |  |  |  | ✓ |  |  |
| Figure bounding-box tests |  |  |  |  |  |  |  |  |  | ✓ |
| CLI mode tests | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Manual rendered audit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 8.3 Required mutation catalogue

The following mutations should be implemented as durable tests because they reproduce the exact Round 8 assurance failures:

1. Transfer caption changed from 132 to 108 while figure/artifact stay current.
2. Transfer caption changed from 62/132 to 50/108.
3. Methods declares `cond_in_group` primary while artifact declares `cond_in_variety`.
4. Methods omits the whole-group or sample-record sensitivity.
5. Artifact key changed from collected-mass endpoint to `v_targets`.
6. Package uses mL while artifact uses g.
7. Endpoint interpretation artifact changes while a literal phrase remains unchanged.
8. Primary interval removed while a secondary `[−0.7xx, −0.0xx]` remains.
9. Primary interval precision changes from three to two decimals.
10. One off-grid sample is removed while the record count is held at 44 by substituting another ID.
11. Visible corpus count remains 132 while manifest hash changes.
12. One sample's three solutes are split across clusters.
13. LOCO→C/F edge is reintroduced.
14. Figure S3 title strings are lengthened until bounding boxes overlap.
15. Review brief count changed to 11 while total remains 95.
16. A generated block is duplicated or emptied.

A correction is not fully assured until these tests fail for the intended reason and pass when restored.

## 8.4 Numerical tolerances

Use exact equality for:

- sample IDs and membership;
- endpoint targets and units;
- schema keys and versions;
- cluster counts and role names;
- generated display strings;
- deterministic JSON normalized objects, where intended.

Use declared numerical tolerances for:

- recomputed floating-point predictions and losses;
- full-precision percentile values if library/platform differences are possible;
- image artist bounding boxes.

Do not use loose tolerances to hide a changed scientific result. Any tolerance should be justified by deterministic numerical behavior, not chosen after inspecting the diff.

---

# 9. Exact implementation and verification sequence

Commands labelled **proposed** require adding the tools described above. Existing command names are taken from the Round 8 review and should be verified against the current branch before execution.

## 9.1 Baseline

```bash
git status --short
git rev-parse HEAD
git rev-parse HEAD^{tree}
python --version
python -m pip freeze > /tmp/paper1_round8_baseline_pip_freeze.txt
sha256sum puckworks/data/angeloni2023/bioactives.csv
```

Run and retain the current state, even if it fails:

```bash
python -m puckworks.paper_a.slow_lane_bindings
python tools/paper_a_consistency.py verify
python tools/claim_binding_audit.py
python -m pytest tests/test_paper_a_model_contract.py -q
python -m pytest tests/test_cross_paper_number_audit.py -q
```

Also run the final-only path to expose the stale gate before correction:

```bash
python tools/paper_a_consistency.py submission
```

## 9.2 Implement and test the contract layer

```bash
python -m pytest tests/test_paper_a_transfer_contract.py -q
python -m pytest tests/test_paper_a_endpoint_schema.py -q
```

Before writing artifacts, proposed check mode should fail with a controlled “committed artifacts are stale under schema v2” message rather than a traceback:

```bash
python tools/paper_a_transfer_artifacts.py --check
```

## 9.3 Regenerate scientific artifacts

```bash
python tools/paper_a_transfer_artifacts.py --write
python tools/paper_a_transfer_artifacts.py --check
```

Immediately inspect:

```bash
git diff -- \
  docs/paper1_resource/PAPER_A_ENDPOINT_PROPAGATION.json \
  docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json \
  docs/paper1_resource/PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json
```

Run targeted numerical and membership tests before propagating text:

```bash
python -m pytest \
  tests/test_paper_a_transfer_contract.py \
  tests/test_paper_a_transfer_artifacts.py \
  tests/test_paper_a_endpoint_schema.py \
  -q
```

If any expected headline value changes, stop and prepare a scientific-diff note before continuing.

## 9.4 Generate publication blocks

```bash
python tools/paper_a_transfer_text.py --write
python tools/paper_a_transfer_text.py --check
```

Inspect only the intended files and ensure markers did not swallow author prose:

```bash
git diff -- \
  docs/submission/PAPER_A_JFE_MANUSCRIPT.md \
  docs/submission/PAPER_A_JFE_SUPPLEMENT.md \
  docs/figures/PAPER_A_CAPTIONS.md \
  docs/submission/PAPER_A_JFE_PACKAGE.md
```

Run block and mutation tests:

```bash
python -m pytest \
  tests/test_paper_a_transfer_publication_blocks.py \
  tests/test_paper_a_transfer_mutations.py \
  -q
```

## 9.5 Regenerate figures

Using the existing or implemented figure CLI:

```bash
python -m puckworks.figures_paper_a compute
python -m puckworks.figures_paper_a render
```

If `compute` would rerun unrelated expensive science, provide a targeted Figure 1/S3 render mode and verify that plotted data are loaded from current artifacts. Then run:

```bash
python -m pytest \
  tests/test_paper_a_figure_semantics.py \
  tests/test_paper_a_figure_layout.py \
  tests/test_figure_exports.py \
  -q
```

## 9.6 Regenerate governance artifacts

```bash
python -m puckworks.paper_a.slow_lane_bindings
python tools/claim_binding_audit.py --write
python tools/claim_binding_audit.py
```

Correct the Round 8 brief from its commit-pinned snapshot, not the later live total if it differs.

## 9.7 Search for active stale representations

```bash
rg -n '108|8\.2\s*%|8\.6\s*%|50\s*(of|/)\s*108' \
  docs/submission docs/figures puckworks tools tests

rg -n '(38/40/42\s*mL|v_targets|endpoint[^\n]*mL|m_target[^\n]*mL)' \
  docs/submission docs/figures puckworks tools tests

rg -ni '(actual dependence structure|every condition[^\n]*both|both[^\n]*narrower)' \
  docs/submission docs/figures puckworks tools tests

rg -ni '(not robustly distinguishable|inferential reading|resolvable skill)' \
  docs/submission docs/figures puckworks tools tests

rg -n '11\s*(of|/)\s*95' docs/paper1_resource
```

Every surviving match must be classified as current, secondary-but-correct, historical, test-fixture/mutation, or erroneous. Keep a reviewed allow-list for historical and mutation-fixture occurrences.

## 9.8 Run science and submission gates

```bash
python tools/paper_a_consistency.py verify
python tools/paper_a_consistency.py submission
python -m puckworks.paper_a.build verify
```

The exact build command should follow the repository's implemented interface. The build must internally run artifact and generated-block `--check` modes.

## 9.9 Run targeted and full suites

```bash
python -m pytest tests/test_paper_a_model_contract.py -q
python -m pytest tests/test_cross_paper_number_audit.py -q
python -m pytest tests/test_paper_a_front_matter.py -q
python -m pytest tests/test_figure_exports.py -q
python -m pytest -q
```

Then repeat all deterministic check modes to prove the tree is self-consistent after tests/builds:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_consistency.py verify
python tools/claim_binding_audit.py
git diff --check
git status --short
```

## 9.10 Rendered-package audit

Create the actual manuscript/supplement/caption/figure package using the submission workflow. Inspect it manually against a one-page audit sheet containing:

```text
44 records / 132 observations
8 off-grid records included
8.44% versus 8.83%
62/132 worse count
38/40/42 g
primary resampling scheme and 18×6 + 8×3 composition
non-inferential sensitivity-range wording
parallel LOCO and C/F branches
no S3 title overlap
89 bound / 6 unbound at Round 8 target commit
```

Do not approve on source tests alone. Conversion can preserve stale copied captions or introduce layout defects.

---
# 10. Suggested generated text templates

These templates are intended to show the required scientific content and level of precision. The generator should substitute values from the final artifacts; do not paste the current numbers permanently if regeneration changes them.

## 10.1 General Methods — resampling

> For each held-out coarse/fine solute observation, we formed the paired difference between the mechanistic-model loss and the O-trained level-only-comparator loss. Both predictors were frozen before evaluation of the C/F responses and were not refitted inside resampling. We therefore describe the resulting percentile intervals as fixed-predictor clustered sensitivity ranges, not calibrated confidence intervals. The predeclared primary scheme resampled `(variety, temperature, pressure)` clusters with replacement within variety. The complete C/F corpus contains 26 such clusters: 18 contain distinct C and F sample records for all three named solutes (six observations), whereas eight off-grid clusters contain one grind and three solute observations. This construction deliberately keeps same-condition cross-solute outcomes together and additionally couples C/F records where both exist; it is a conservative dependence sensitivity rather than a uniquely identified experimental sampling unit. Secondary schemes resampled individual sample records within variety × grind, conditions within variety × solute, and whole variety × solute groups. All schemes used the archived cluster membership, percentile probabilities, random-number generator, seed, and repetition count, and all summarized the same complete 132-observation point estimand.

Add exact `B`, seed, RNG, quantile convention, and scheme counts in the paragraph or immediately adjacent generated table.

## 10.2 Results — complete corpus and practical interpretation

> On the complete held-out C/F corpus of 44 sample records and 132 named-solute observations, including all eight off-grid records, pooled MAPE was 8.44% for the mechanistic model and 8.83% for the O-trained level-only comparator. The observed model-minus-comparator difference was −0.394 percentage points, and the mechanistic model had the larger absolute percentage error for 62 of 132 observations. Thus the observed pooled advantage was favorable but small relative to the approximately 8–9% error levels of both predictors.

The exact values should be generated from the final 40 g headline row.

## 10.3 Results — dependence and knife-edge interpretation

> Under the predeclared `(variety,T,p)` primary sensitivity, the clustered percentile range was `[−0.825, +0.000]` percentage points at the reporting precision. The full-precision upper bound was slightly negative and rounded to zero for display. The sample-record, within-solute-condition, and whole-group constructions produced the ranges shown in Table 5; one current secondary range was narrower than the primary and the whole-group range was wider. Endpoint, fitting-loss, clustering, and Monte Carlo checks left the sign and approximate magnitude of the point difference broadly stable but changed the location or display of a boundary close to zero. Because these are fixed-predictor sensitivity ranges without calibrated coverage, neither full-precision exclusion nor rounded contact with zero is interpreted as evidence of statistical superiority, non-superiority, or equivalence.

Replace the current primary interval and secondary behavior with regenerated outputs. Do not say the full-precision upper bound is negative unless the final canonical run confirms it.

## 10.4 Standalone transfer caption

> **Transfer benchmark.** The mechanistic model and O-trained level-only comparator were evaluated without C/F response refitting on the complete held-out coarse/fine corpus: 44 sample records × three named solutes = 132 observations, including the eight off-grid records. Pooled MAPE was 8.44% for the mechanistic model and 8.83% for the comparator; the mechanistic model had the larger absolute percentage error for 62 of 132 observations. Any clustered intervals shown are fixed-predictor dependence sensitivities rather than calibrated confidence intervals.

Panel-specific descriptions should surround this generated core where required.

## 10.5 Package status line

> Endpoint-mass propagation at collected-mass targets of 38, 40, and 42 g has been regenerated and validated against the committed schema-versioned endpoint artifact.

Do not add mL, a `v_targets` alias, or a result interpretation to the package checklist.

## 10.6 Figure 1 caption core

> Arrows denote data or fitted-parameter dependency rather than analysis order. Angeloni optimal-grind observations support two parallel within-campaign analyses: fold-specific calibration on 8 of 9 O conditions for held-out O prediction, and one calibration on all 9 O conditions that is frozen before evaluation on the complete C/F corpus. The C/F analysis does not use the LOCO output. The Waszkiewicz trajectory is a separate external-data branch using the source kinetic structure and the target-specific profiling described in Methods.

## 10.7 Supplementary Figure S3 caption core

> **Per-group residual diagnostics at the matched 40 g endpoint.** (a) Blind and inventory-matched MAPE by group. (b) Cross-condition association of the corresponding response summaries; this panel compares conditions and is not a temporal trajectory. The caption should state the number and definition of groups, the matching procedure, and the interpretation limits associated with the small group set.

---

# 11. Decisions requiring explicit scientific adjudication

The following choices must be recorded in a short decision log. They should not be hidden inside code or inferred from the final result.

## 11.1 Primary resampling scheme

Record:

- whether `cond_in_variety` remains primary;
- the design rationale independent of zero crossing;
- why the sample-record scheme is secondary or primary;
- when the decision was made relative to viewing the new results; and
- who approved it.

Recommended default: retain the existing primary as a conservative declared sensitivity, add sample-record clustering prominently, and correct the overstatement.

## 11.2 Observation-weighted versus cluster-weighted statistic

Record exactly how unequal-size primary clusters contribute to the resampled mean. If the target remains the pooled observation-level MAPE difference, observation weighting is the natural direct match, but the bootstrap implementation and interpretation must be consistent with that choice.

## 11.3 Canonical repetition count and stability criterion

Record:

- canonical `B`;
- RNG and seed;
- quantile method;
- stability-audit design; and
- the predeclared adequacy rule, such as no change in the displayed three-decimal interval across independent batches or a specified maximum percentile Monte Carlo variation.

Do not increase repetitions selectively until a preferred boundary sign appears.

## 11.4 Practical-effect margin

Recommended default: do not introduce an equivalence or smallest-effect margin in this correction unless there is independent domain justification. Report the observed approximately 0.4 percentage-point difference descriptively. If a margin is introduced, document its external basis and treat it as a new sensitivity.

## 11.5 Artifact consolidation

Record whether the repository will:

- create one dedicated corpus manifest artifact;
- retain the current artifacts with exact embedded manifest copies; or
- consolidate all transfer results into one schema.

The non-negotiable requirement is one canonical membership object and matching hashes, not a specific file count.

## 11.6 Historical brief behavior

Record that Round 8 is commit-pinned and will remain at 89/95 bound and 6/95 unbound even if later work changes live coverage. Future briefs should receive their own snapshots.

---

# 12. Pull-request evidence package

The remediation pull request should include or link the following evidence. A green test badge alone is insufficient.

## 12.1 Scientific artifact diff

Provide a table showing old and new values for:

| Field | Old | New | Reason for change |
|---|---:|---:|---|
| Corpus records | 44 | regenerated | should remain unless source/estimand changed |
| Corpus observations | 132 | regenerated | should remain unless source/estimand changed |
| Model MAPE | 8.44% | regenerated | numerical regeneration/schema change |
| Comparator MAPE | 8.83% | regenerated | numerical regeneration/schema change |
| Worse count | 62/132 | regenerated | numerical regeneration/schema change |
| Point difference | −0.394 pp | regenerated | numerical regeneration/schema change |
| Primary full range | previously incompletely archived | new signed full bounds | precision correction |
| Primary display range | `[−0.825,+0.000]` | regenerated | formatter/canonical run |
| Sample-record range | absent | new | dependence sensitivity |
| Endpoint schema | `m_targets` plus stale `v_targets` gate | typed collected-mass schema | unit/schema correction |

Explain every changed numerical field. “Regenerated” is not itself an explanation if the value moves materially.

## 12.2 Corpus and cluster evidence

Attach:

- canonical manifest hash;
- source-file hash;
- list of 44 sample IDs;
- list of eight off-grid IDs;
- 18 × 6 plus 8 × 3 primary census;
- 44 × 3 sample-record census;
- no-exclusion assertion; and
- support split for complete versus matched-grid comparisons.

## 12.3 Monte Carlo stability evidence

Attach a compact table for each endpoint and principal scheme showing:

- canonical full-precision bounds;
- displayed bounds;
- across-seed or batch variation;
- whether full-precision zero classification changes;
- whether display changes; and
- confirmation that this is numerical stability, not confidence-interval coverage.

## 12.4 Semantic-contract evidence

Include the mutation-test report showing that all known failures are caught. At minimum, demonstrate the stale caption, wrong primary, `v_targets`, missing off-grid ID, vacuous interval regex, wrong figure edge, and overlapping-title mutations.

## 12.5 Figure evidence

Include:

- Figure 1 before/after at final size;
- S3 before/after at final size;
- graph edge-set summary;
- bounding-box test result; and
- confirmation that unrelated plotted data arrays are unchanged.

## 12.6 Command record

Archive the commands and exit statuses for:

```text
artifact --check
text --check
slow-lane bindings
claim-binding audit
paper consistency verify
paper consistency submission
paper build verify
targeted Paper 1 tests
cross-paper number audit
full pytest suite
```

Include the commit and clean-tree status associated with the run.

## 12.7 Independent review sign-offs

Recommended sign-off roles:

- **scientific-analysis reviewer:** cluster design, estimand, precision, interpretation;
- **manuscript reviewer:** Methods/Results/caption coherence;
- **assurance reviewer:** tests genuinely fail under mutations;
- **figure reviewer:** dependency geometry and publication layout;
- **release approver:** final rendered package and clean verification record.

One person may fill multiple roles, but each question should be explicitly answered.

---

# 13. Final closure checklist

## P0-1 — Transfer caption

- [ ] Caption generated from complete-corpus artifact.
- [ ] 44 records / 132 observations stated correctly.
- [ ] Eight off-grid records explicitly included.
- [ ] 8.44%, 8.83%, and 62/132 reconciled with final artifact.
- [ ] Any 108-observation result clearly labelled matched-grid sensitivity.
- [ ] Caption carries correct manifest stamp.
- [ ] Stale-tuple mutation fails.
- [ ] Final standalone export inspected.

## P0-2 — Methods

- [ ] Final primary and all secondary schemes represented in design object.
- [ ] Exact keys, strata, counts, sizes, `B`, seed, RNG, quantile method, and no-refit status stated.
- [ ] Primary census stated as 18 × 6 plus 8 × 3.
- [ ] Sample-record sensitivity included or omission scientifically adjudicated.
- [ ] Producer, Methods, Results, Table 5, and supplement agree.
- [ ] Wrong-primary and missing-scheme mutations fail.

## P0-3 — Endpoint and release gate

- [ ] Active endpoint contract is collected mass in g.
- [ ] Required targets are 38/40/42 g.
- [ ] Schema version and row-level `m_target_g` validation present.
- [ ] `v_targets` and endpoint-specific mL are rejected.
- [ ] Package, build labels, and claim coverage corrected.
- [ ] Science endpoint check runs in ordinary `verify`.
- [ ] Magic phrase replaced by structured semantic check.
- [ ] Both CLI modes pass in final state.

## P1-1 — Dependence structure

- [ ] Canonical observation table and cluster membership archived.
- [ ] Source hierarchy distinguishes sample, solute, grind, condition, and available replicate information.
- [ ] Primary described as conservative sensitivity, not uniquely actual unit.
- [ ] Sample-record sensitivity implemented or adjudicated.
- [ ] Every scheme covers the same 132 observations.
- [ ] Point estimate is scheme-invariant or any difference is explained.
- [ ] Width statements are generated and correct.
- [ ] No outcome-based scheme selection occurred.

## P1-2 — Knife-edge precision and interpretation

- [ ] Signed full-precision bounds archived.
- [ ] Analytical flags use full precision.
- [ ] Display fields and negative-zero normalization are separate.
- [ ] Canonical high-repetition run completed.
- [ ] Multi-seed or batch stability audit archived.
- [ ] Ambiguous `conclusion_stable` replaced with explicit dimensions.
- [ ] “Distinguishable,” “inferential,” and equivalent unsupported wording removed.
- [ ] No post-hoc practical margin introduced without independent justification.

## P1-3 — Primary interval contract

- [ ] Old `0.7xx` regex removed.
- [ ] Artifact-selected primary 40 g interval used.
- [ ] Shared production formatter used.
- [ ] Required blocks are explicit and non-empty.
- [ ] Scheme and endpoint context are bound.
- [ ] Primary-absent/secondary-present mutation fails.
- [ ] Precision and value mutations fail.

## P1-4 — Corpus semantic contract

- [ ] One canonical source-derived manifest exists.
- [ ] Included/excluded/off-grid/lookup-undefined IDs are explicit.
- [ ] Sample-ID and full-manifest hashes are stable.
- [ ] All artifacts reference the same manifest.
- [ ] Manuscript, supplement, caption, and package agree.
- [ ] Supplement publishes the 44-record membership table.
- [ ] Count-preserving membership mutations fail.

## P1-5 — Figure 1

- [ ] Nodes and edges represented semantically in code.
- [ ] LOCO and C/F branches are parallel.
- [ ] LOCO labelled 8/9 fit per fold.
- [ ] C/F labelled 9/9 fit once and frozen.
- [ ] No LOCO→C/F edge exists.
- [ ] External trajectory has independent provenance.
- [ ] Caption defines arrow semantics.
- [ ] Final raster/vector exports inspected.

## P2-1 — Review-brief coverage

- [ ] Every Round 8 occurrence says 89 bound / 6 unbound of 95.
- [ ] Commit-pinned snapshot exists.
- [ ] Category arithmetic reconciles.
- [ ] Historical brief is not coupled to future live counts.
- [ ] 11/95 mutation fails.

## P2-2 — S3 layout

- [ ] Panel titles shortened.
- [ ] Explanatory detail moved to caption.
- [ ] Layout tuned at final physical width.
- [ ] Bounding-box tests pass.
- [ ] Raster and vector exports inspected.
- [ ] Plotted data unchanged.

## Cross-cutting final gate

- [ ] Source-to-artifact checks pass.
- [ ] Artifact-to-publication checks pass.
- [ ] All mutation tests pass.
- [ ] `paper_a_consistency.py verify` passes.
- [ ] `paper_a_consistency.py submission` passes or reports only deliberately unresolved final metadata before final approval.
- [ ] Paper build verification passes.
- [ ] Targeted and full test suites pass.
- [ ] All deterministic `--check` commands leave the tree unchanged.
- [ ] Final rendered manuscript, supplement, captions, and figures are manually approved.
- [ ] Working tree is clean and the verification record identifies the exact commit/tree.

---

# 14. Completion standard

The Round 8 actions are correctly addressed only when the repository no longer depends on human memory to keep the transfer analysis synchronized. The decisive evidence is not simply that the currently correct numbers have been typed into every file. It is that:

- the source data deterministically produce one auditable corpus and one declared set of sensitivity analyses;
- the artifacts retain the precision and metadata necessary to reconstruct every claim;
- publication text and figures are generated from, or semantically bound to, those artifacts;
- the tests reproduce and reject the exact failure modes found in Round 8; and
- the final rendered package has been inspected independently of the source-level checks.

Until that chain is complete, a corrected caption or paragraph should be treated as provisional rather than as closure of the underlying review action.

---

**Prepared as an implementation companion to:** `PAPER_1_ROUND_8_DETAILED_REVIEW.md`  
**Review target:** `21b138a1fa8866db0b65c59b541b766498e63ed4`
