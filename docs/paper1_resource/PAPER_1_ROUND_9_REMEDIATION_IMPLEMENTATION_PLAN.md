# Paper 1 — Round 9 Remediation and Verification Implementation Plan

**Prepared:** 29 July 2026  
**Applies to reviewed baseline:** [`45e753a5f37ede66cd99a016a6b8902fdbadebdf`](https://github.com/trbrewer/puckworks/tree/45e753a5f37ede66cd99a016a6b8902fdbadebdf)  
**Governing review:** `PAPER_1_ROUND_9_DETAILED_REVIEW.md`  
**Purpose:** convert every Round 9 finding into a precise implementation, mutation-testing, regeneration, and acceptance plan  
**Status:** implementation specification; completion of this document is **not** evidence that the repository has been remediated

---

## 1. Executive implementation decision

The Round 9 defects should be addressed as one coordinated assurance change rather than as seven unrelated text edits. The central failure mode is that correct numerical values can pass through structurally valid artifacts and still be rendered into scientifically false sentences. The remediation therefore needs four distinct assurance layers:

1. **Numerical artifact integrity:** source data, producer settings, endpoint rows, interval bounds, and audit results are present and internally valid.
2. **Scientific semantic integrity:** interval geometry, estimand direction, favourable/unfavourable extremes, audit scope, and numerical stability are represented as typed concepts rather than inferred from loosely related booleans.
3. **Source independence:** the resampling design is compared with an independently reconstructed source-derived partition, not merely with itself or with aggregate counts.
4. **Publication-surface integrity:** every generated manuscript, supplement, abstract, package, cover letter, caption, and figure uses the same typed facts and is checked for process leakage and visual-semantic ambiguity.

### 1.1 Recommended decisions

| Decision | Recommendation | Reason |
|---|---|---|
| Interval semantics | Add a shared pure module, proposed as `puckworks/paper_a/transfer_semantics.py` | Prevent every renderer from inventing its own interpretation |
| Zero relation | Use a full-precision trinary relation: `below_zero`, `contains_zero`, `above_zero` | A `contains_zero` boolean cannot distinguish the two excluding sides |
| Exact zero contact | Record separately from containment and derive only from full-precision bounds | Display rounding to `+0.000` must never become scientific contact with zero |
| Estimand direction | Declare `model loss − comparator loss`, with negative values favouring the model | Required to identify the most and least favourable bounds correctly |
| Monte Carlo remediation | **Scope the existing audit** to 40 g, `cond_in_variety`, primary/default fitting loss; do not invent universal precision | This closes P1-1 without an unnecessary new multi-endpoint campaign |
| Audit representation | Add an exact target key and bump the transfer artifact schema once, in a coordinated update | Prevent an audit value from leaking to another endpoint, scheme, loss, or scoring rule |
| Endpoint rows | Make validation fail closed and require the exact three complete rows | Deletion or malformed rows must be a named contract failure |
| Resampling provenance | Add an independent CSV-derived membership oracle for all four schemes | Counts and self-hashes cannot detect scientifically wrong partitions |
| Process-language scan | Scan manuscript, canonical draft, package, cover letter, highlights, supplement, and standalone captions after stripping comments | Current scan omits reader-facing surfaces |
| Figure 1 | Keep related blue family if desired, but distinguish `in-sample` and `within-campaign holdout` by a second channel such as line style; test the complete encoding tuple | Distinct categories need decodable encodings, including in grayscale |
| Figure S3 panel (b) | Remove the arbitrary categorical colours and use one neutral bar colour plus a zero line | Signed bar length already conveys the data; this avoids implying unreported classes |
| Numerical recomputation | Update code and tests first, then perform one final producer-backed `--write` after the schema change | Avoid repeated expensive runs while retaining genuine producer provenance |

### 1.2 Expected submission conclusion after remediation

The corrected paper should say, consistently, that:

- the paired model-minus-comparator differences remain small and negative across the 38–42 g endpoint sweep;
- the primary sensitivity range excludes zero below zero at 38 g and contains zero at 40 and 42 g;
- the primary and alternative fitting-loss ranges at 40 g both contain zero;
- negative values favour the mechanistic model, so lower bounds are the favourable extremes and upper bounds are the unfavourable extremes;
- the 40 g primary/default-loss upper-bound sign is numerically stable under the archived multi-seed audit;
- that audit does not establish coverage, statistical superiority, equivalence, or non-inferiority and does not automatically apply to 38 g, 42 g, secondary schemes, or the alternative fitting loss.

---

## 2. Scope control and non-negotiable invariants

### 2.1 Findings covered

This plan addresses exactly the seven Round 9 findings:

- **P0-1:** incorrect interval geometry and bound favourability in generated prose;
- **P0-2:** contradiction between the abstract/S3 and the archived sign-stability audit;
- **P1-1:** overgeneralization of the `≈0.0005 pp` Monte Carlo error;
- **P1-2:** endpoint validator false greens when result rows are deleted or malformed;
- **P1-3:** resampling membership is not independently bound to source data;
- **P2-1:** publication-process language remains in reader-facing prose and the scanner omits the supplement;
- **P2-2:** Figure 1 and Figure S3 have ambiguous or undocumented colour semantics.

### 2.2 Verified facts that must not be disturbed

The implementation must preserve the following already-correct results and decisions unless a genuine producer rerun proves otherwise:

| Invariant | Required retained value/meaning |
|---|---|
| Reviewed support | Complete held-out coarse/fine corpus: 44 sample records and 132 named-solute observations |
| Endpoint targets | Collected mass at 38.0, 40.0, and 42.0 g, in canonical order |
| Primary scheme | `cond_in_variety`, retained for the declared design rationale rather than selected by relation to zero |
| Secondary schemes | `sample_in_variety_grind`, `cond_in_group`, and `group` all remain reported |
| Primary 38 g relation | Full-precision primary interval is below zero and excludes zero |
| Primary 40 g relation | Full-precision primary interval contains zero; upper bound is approximately `+0.0037905 pp` |
| Primary 42 g relation | Full-precision primary interval contains zero; upper bound is approximately `+0.005844 pp` |
| Loss robustness | Both 40 g loss-specific primary intervals contain zero; the point estimates are approximately `−0.394` and `−0.393 pp` |
| Estimand | Model loss minus comparator loss; negative values favour the mechanistic model |
| Audit scope | Existing retained multi-seed audit is 40 g, primary `cond_in_variety`, primary/default fitting loss |
| Audit interpretation | Numerical approximation/sign stability only; no calibrated coverage or inferential status |
| Display precision | Retain three decimals for reported ranges, with explicit numerical-resolution qualification |
| Resampling design census | 26 / 44 / 78 / 6 clusters for the four schemes, with the established size distributions |
| Figure 1 graph | LOCO and C/F transfer remain parallel children of Angeloni recalibration; external branch remains independent; Table 7 remains lateral |
| Figure S3 layout | Existing title-collision correction, NA handling, and panel labels remain intact |
| Supplement S6/S7 | Existing scientific content and corpus census remain; only process-language wording changes |

### 2.3 Out of scope for this remediation

Do not mix the known-open/out-of-scope matters from the review brief into this implementation. In particular, this plan does not authorize changes to unresolved author metadata, novelty-search status, release DOI/tagging, other papers, unrun rate-profile contrasts, or separately enumerated slow-lane items. Mixing those matters into the same patch would make scientific-diff review unnecessarily difficult.

---

## 3. Change architecture

### 3.1 Proposed shared semantic module

Create:

```text
puckworks/paper_a/transfer_semantics.py
```

This module should be pure Python, deterministic, free of plotting or YAML dependencies, and usable by producers, renderers, front matter, consistency checks, and unit tests. It should own only scientific meaning, not manuscript-specific prose layout.

Recommended public objects:

```python
from dataclasses import dataclass
from enum import Enum

class ZeroRelation(str, Enum):
    BELOW_ZERO = "below_zero"
    CONTAINS_ZERO = "contains_zero"
    ABOVE_ZERO = "above_zero"

class FavourDirection(str, Enum):
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"

@dataclass(frozen=True)
class IntervalSemantics:
    lower: float
    upper: float
    zero_relation: ZeroRelation
    touches_zero_at_lower: bool
    touches_zero_at_upper: bool

@dataclass(frozen=True)
class EstimandSpec:
    id: str
    label: str
    favour_direction: FavourDirection
    zero_meaning: str

@dataclass(frozen=True)
class AuditKey:
    endpoint_quantity: str
    endpoint_value: float
    endpoint_unit: str
    support_set: str
    scheme: str
    fitting_loss_id: str
    scoring_rule_id: str
    interval_kind: str
    quantile_probabilities: tuple[float, float]
```

Core functions:

```python
def classify_interval(lower: float, upper: float) -> IntervalSemantics: ...
def validate_interval_semantics(record: dict) -> list[str]: ...
def relation_phrase(relation: ZeroRelation) -> str: ...
def compare_interval_relations(a: IntervalSemantics, b: IntervalSemantics) -> str: ...
def favourable_extreme(intervals, estimand: EstimandSpec): ...
def least_favourable_extreme(intervals, estimand: EstimandSpec): ...
def audit_key(record: dict) -> AuditKey: ...
def find_exact_audit(artifact: dict, key: AuditKey) -> dict: ...
```

### 3.2 Full-precision classification rules

The classifier must:

1. convert inputs to finite floats and reject booleans, strings, NaN, and infinities;
2. reject `lower > upper`;
3. normalize `-0.0` to `0.0` for contact flags;
4. classify **before** any display rounding:
   - `upper < 0.0` → `below_zero`;
   - `lower > 0.0` → `above_zero`;
   - otherwise → `contains_zero`;
5. set exact-contact flags only when the corresponding full-precision bound equals `0.0` under the archived numeric representation;
6. never infer exact contact from a display string such as `+0.000`.

### 3.3 Estimand direction rules

Declare one canonical comparator estimand:

```python
MODEL_MINUS_COMPARATOR_LOSS = EstimandSpec(
    id="model_minus_comparator_loss_pp",
    label="model loss minus comparator loss",
    favour_direction=FavourDirection.LOWER_IS_BETTER,
    zero_meaning="equal loss under the stated scoring rule",
)
```

For this estimand:

- the most favourable observed endpoint point estimate is the minimum point estimate;
- the most favourable range extreme is the minimum lower bound;
- the least favourable range extreme is the maximum upper bound;
- a negative value favours the mechanistic model;
- a positive value favours the comparator;
- a range containing zero admits both signs and must not be described as lying on one side;
- exact zero contact is not equivalent to a small rounded value.

### 3.4 Artifact schema strategy

Because the audit needs an exact target identity rather than an implicit top-level meaning, use one coordinated transfer-artifact schema bump from version 2 to version 3. Do not bump repeatedly for each finding.

Recommended new endpoint-artifact structure:

```json
{
  "schema_version": 3,
  "estimand": {
    "id": "model_minus_comparator_loss_pp",
    "formula": "model_loss_pp - comparator_loss_pp",
    "negative_values_favour": "mechanistic_model",
    "positive_values_favour": "level_only_comparator"
  },
  "stability_audits": [
    {
      "audit_id": "m40__complete132__cond_in_variety__mape_level__mape_score__q2.5_97.5",
      "target": {
        "endpoint_quantity": "collected_mass",
        "endpoint_value": 40.0,
        "endpoint_unit": "g",
        "support_set": "complete_cf_corpus_132",
        "scheme": "cond_in_variety",
        "fitting_loss_id": "mape_optimal_level_both_predictors",
        "scoring_rule_id": "mape_both_arms",
        "interval_kind": "fixed_predictor_clustered_percentile_sensitivity_range",
        "quantile_probabilities": [2.5, 97.5]
      },
      "B_per_seed": 200000,
      "canonical_B": 1000000,
      "seeds": [0, 1, 2],
      "lower_monte_carlo_se_at_canonical_B_pp": 0.0005201594273814796,
      "upper_monte_carlo_se_at_canonical_B_pp": 0.00046559035360477143,
      "upper_bound_sign_is_stable": true,
      "coverage_calibrated": false
    }
  ]
}
```

The example seed list above is abbreviated only for readability; the retained artifact must continue to carry all 20 actual seeds.

Do not retain a silently ambiguous top-level `stability_audit` as a fallback. Either migrate it to `stability_audits` or reject it under schema version 3. A compatibility reader may provide a clear migration error for version 2, but publication generation must not guess.

### 3.5 Producer and regeneration implications

Update the producer in `puckworks/validation/slow/angeloni_bracket.py` so the new semantic and audit-target fields are emitted by the real producer, not post-hoc patched into JSON. Then perform a single final:

```bash
python tools/paper_a_transfer_artifacts.py --write
```

Because that command re-runs the slow producers, first finish and test all code against fixtures. After the final write, compare every pre-existing numeric leaf with the reviewed baseline and require equality or a documented deterministic reason for any movement. The expected scientific numbers should not change merely because their meaning is now typed.

---

# 4. P0-1 — Correct interval geometry and bound favourability

## 4.1 Objective

Ensure that every active publication surface describes the full-precision interval relation and the direction of the model-minus-comparator estimand correctly. Eliminate all prose derived from equality of `contains_zero` booleans or from a hard-coded assumption that an upper bound is favourable.

## 4.2 Root cause to remove

The current generator effectively treats:

```python
base.contains_zero == alternative.contains_zero
```

as proof that the intervals lie on the same side of zero. That is invalid for both `True == True` and `False == False`. A separate generator also refers to the largest model advantage using upper bounds even though lower values favour the model.

The remediation must remove the faulty abstraction, not merely replace the current sentence.

## 4.3 Affected source and output surfaces

### Source code

- `puckworks/paper_a/transfer_contract.py`
- new `puckworks/paper_a/transfer_semantics.py`
- `tools/paper_a_transfer_text.py`
- `tools/paper_a_front_matter.py`
- `docs/submission/paper_a_front_matter.yaml`
- `tools/paper_a_consistency.py`

### Generated/publication outputs

- `docs/PAPER_A_DRAFT.md`
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/submission/PAPER_A_JFE_SUPPLEMENT.md`
- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `docs/submission/PAPER_A_JFE_COVER_LETTER.md`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`, even if unchanged, must be regenerated/checked

### Tests

- add `tests/test_paper_a_transfer_semantics.py`
- extend `tests/test_paper_a_transfer_contract.py`
- extend `tests/test_paper_a_submission_contract.py`
- extend `tests/test_paper_a_front_matter.py`

## 4.4 Method

### Step 1 — Add the trinary classifier

Implement `classify_interval()` exactly as specified in §3.2. Keep it independent of display formatting.

Expected examples:

| Lower | Upper | Relation | Exact contact |
|---:|---:|---|---|
| −0.829052 | +0.003791 | `contains_zero` | neither bound |
| −0.884387 | −0.042433 | `below_zero` | none |
| +0.0001 | +0.5 | `above_zero` | none |
| −0.5 | 0.0 | `contains_zero` | upper |
| 0.0 | +0.5 | `contains_zero` | lower |
| −0.5 | −0.0004, displayed as `+0.000` | `below_zero` | none |

### Step 2 — Add semantic fields to interval records

Update `interval_record()` so each new schema-v3 record carries:

```json
{
  "zero_relation_full_precision": "contains_zero",
  "touches_zero_at_lower_full_precision": false,
  "touches_zero_at_upper_full_precision": false
}
```

Retain `contains_zero_full_precision` and `excludes_zero_full_precision` during the schema-v3 transition only if other code still consumes them, but validate that all representations agree. Plan their later removal rather than allowing three independent sources of meaning indefinitely.

### Step 3 — Centralize relation wording

Provide relation renderers that return controlled phrases:

| Relation | Preferred phrase |
|---|---|
| `below_zero` | “excluded zero on the negative side” |
| `contains_zero` | “contained zero” |
| `above_zero` | “excluded zero on the positive side” |

For two intervals, use a complete decision table rather than a boolean shortcut:

| A | B | Required comparison wording |
|---|---|---|
| contains | contains | “both ranges contained zero” |
| below | below | “both ranges excluded zero on the negative side” |
| above | above | “both ranges excluded zero on the positive side” |
| below | above | describe each; never “same classification” without stating opposite sides |
| contains | below/above | describe each relation explicitly |
| below/above | contains | describe each relation explicitly |

“Same containment classification” may be used only as a secondary machine-readable property; it is not a substitute for the actual relation phrase.

### Step 4 — Derive favourable extremes from the estimand

Replace hand-coded `min`/`max` descriptions with functions that take `EstimandSpec`.

For `LOWER_IS_BETTER`:

```python
most_favourable = min((interval.lower, context) for interval in intervals)
least_favourable = max((interval.upper, context) for interval in intervals)
```

For `HIGHER_IS_BETTER`, reverse these operations. Include the endpoint and scheme in the returned context so prose cannot quote a value without identifying where it came from.

### Step 5 — Replace every affected sentence at the generator source

Do not hand-edit generated manuscript blocks. Change the generating functions and then regenerate.

Recommended fitting-loss paragraph:

> Refitting both the mechanistic model and the level-only comparator under the alternative log/relative-error level fit changed the paired model-minus-comparator difference from **−0.394 pp** to **−0.393 pp**. The corresponding primary clustered percentile sensitivity ranges were **[−0.829, +0.004] pp** and **[−0.826, +0.004] pp**; both contained zero at full precision. The fitting loss therefore did not materially change the point estimate, the zero-containment classification, or the practical reading. These descriptive ranges have no calibrated coverage interpretation.

Recommended endpoint-sweep interpretation:

> Across the 38–42 g endpoint sweep, the most favourable lower bound was **−0.891 pp** and the least favourable upper bound was **+0.006 pp**. Negative model-minus-comparator values favour the mechanistic model; the positive upper bounds at 40 and 42 g admit a small comparator-favouring end of the descriptive sensitivity range.

Recommended conclusion/cover-letter clause:

> …a paired difference of **−0.394 percentage points** whose primary clustered percentile sensitivity range **[−0.829, +0.004] pp contained zero**.

Replace “moves neither the magnitude” with one of:

- “did not materially change the point estimate”; or
- “changed the point estimate by 0.001 pp, without changing the practical reading.”

The second is more explicit and is preferred where space permits.

### Step 6 — Remove independent hard-coded central-result prose

Refactor the cover letter so its result paragraph is generated from the same semantic summary used by the manuscript. A safe pattern is:

```python
def cover_letter(fm: dict, claims: TransferClaims) -> str:
    ...
```

where `TransferClaims` is built from validated artifacts. Do not import `tools.paper_a_transfer_text` into `paper_a_front_matter.py` if that creates a circular dependency. Put the shared factual summary builder in the pure semantics/claims module.

For the abstract, keep editorial text in YAML but replace the endpoint-result tail with a controlled placeholder, for example:

```yaml
abstract: >-
  ... Matched endpoints are therefore necessary but insufficient.
  {{endpoint_sensitivity_abstract_sentence}}
```

The front-matter renderer should allow only a declared placeholder set, require each factual placeholder exactly once, and fail on an unresolved or duplicated placeholder. This preserves a single editable abstract while preventing the principal endpoint sentence from drifting away from the artifact.

### Step 7 — Add semantic consistency checks

`paper_a_consistency.py verify` should compare exact generated blocks rather than search for a single magic phrase. It should also reject retired false wording in active publication outputs:

- “same side of zero” when referring to the two 40 g fitting-loss ranges;
- “reaches zero at its upper bound” for the current 40 g interval;
- “largest advantage” attached to an upper bound for a lower-is-better estimand;
- “moves neither the magnitude.”

Retired-phrase checks are a backstop, not the primary semantic proof.

## 4.5 Potential pitfalls, errors, and oversights

1. **Classifying rounded values.** Using `display.lower`/`display.upper` recreates the defect. Classification must use `full_precision_pp` only.
2. **Treating `+0.000` as exact zero.** The display formatter intentionally normalizes negative zero. Exact contact needs a separate full-precision flag.
3. **Assuming every loss is lower-is-better.** The current estimand is lower-is-better, but the helper should require an explicit `EstimandSpec` so future metrics cannot inherit this silently.
4. **Replacing one false phrase with another.** “Both have the same zero-crossing status” is technically narrower but still opaque. State that both contain zero.
5. **Dropping the direction clause.** “Most favourable” is not self-explanatory unless the text states that negative values favour the model.
6. **Calling containment inferential.** A range containing zero does not establish equivalence or non-distinguishability; keep the no-coverage qualification.
7. **Duplicating facts in YAML and Python.** The placeholder should replace, not supplement, a hand-written copy of the same endpoint sentence.
8. **Circular imports.** Keep semantic dataclasses and render-neutral helpers in the package module; tools may import the package, not each other cyclically.
9. **Word-limit drift.** The corrected abstract clause may be longer. Re-run the venue word-count test and tighten surrounding prose without deleting qualifications.
10. **Historical review files.** Repository-wide phrase searches must exclude archived reviews/briefs or clearly distinguish active submission files, otherwise legitimate historical quotations will cause noise.

## 4.6 Required checks

### Unit tests

Parameterize the full relation matrix:

```python
@pytest.mark.parametrize("a,b,expected", [
    ((-1.0, 0.1), (-0.8, 0.2), "both_contain_zero"),
    ((-1.0, -0.1), (-0.8, -0.2), "both_below_zero"),
    ((0.1, 1.0), (0.2, 0.8), "both_above_zero"),
    ((-1.0, -0.1), (0.1, 1.0), "opposite_excluding_sides"),
    ((-1.0, 0.1), (-0.8, -0.2), "mixed"),
])
```

Also test:

- exact zero at lower and upper bounds;
- rounded-to-zero but full-precision negative/positive bounds;
- `lower > upper`, NaN, infinity, string, and boolean rejection;
- favourable extremes for both lower-is-better and higher-is-better estimands;
- the current artifacts produce `contains_zero` for both loss rows;
- the current endpoint sweep yields the expected favourable lower and least-favourable upper endpoints.

### Mutation tests

Each of the following must fail a semantic check:

- flip `zero_relation_full_precision` while retaining the bounds;
- flip `contains_zero_full_precision` while retaining the bounds;
- set exact-contact flag true when upper bound is `+0.0037905`;
- change estimand direction to higher-is-better without changing generated prose;
- mutate one loss range to entirely positive while leaving a “both contain zero” block;
- mutate the cover-letter generated clause independently from the manuscript block.

### Integration checks

```bash
python tools/paper_a_transfer_text.py --check
python tools/paper_a_front_matter.py
python tools/paper_a_consistency.py verify
python -m pytest tests/test_paper_a_transfer_semantics.py -q
python -m pytest tests/test_paper_a_transfer_contract.py -q
python -m pytest tests/test_paper_a_front_matter.py -q
python -m pytest tests/test_paper_a_submission_contract.py -q
```

### Manual review

Search the active outputs after regeneration:

```bash
rg -n -i \
  'same side of zero|reaches zero at its upper bound|largest advantage.*upper bound|moves neither.*magnitude' \
  docs/PAPER_A_DRAFT.md docs/submission docs/figures/PAPER_A_CAPTIONS.md
```

Expected result: no active false statement. Historical review resources may still contain the phrases as quotations.

## 4.7 Acceptance evidence

P0-1 is closed only when the remediation PR contains:

- the typed semantic implementation;
- the relation/favourability test matrix;
- regenerated manuscript, supplement, package, and cover letter;
- a clean retired-phrase scan on active outputs;
- a short before/after evidence note showing that both 40 g fitting-loss intervals are rendered as containing zero and that lower/upper favourability is correctly oriented.

---

# 5. P0-2 — Reconcile the abstract and S3 with the sign-stability audit

## 5.1 Objective

Make every publication surface distinguish three separate concepts:

1. **numerical sign stability** of the audited 40 g primary/default-loss upper bound;
2. **endpoint sensitivity** of the full-precision zero-containment classification across 38, 40, and 42 g;
3. **absence of calibrated coverage or inferential meaning** for the descriptive ranges.

The corrected text must neither understate the numerical audit nor overstate its statistical meaning.

## 5.2 Affected surfaces

- `docs/submission/paper_a_front_matter.yaml`
- `tools/paper_a_front_matter.py`
- `tools/paper_a_transfer_text.py`
- `tools/paper_a_consistency.py`
- generated manuscript abstract
- generated package abstract
- generated Supplementary Table S3 interpretation
- any conclusion or cover-letter sentence that discusses numerical resolution
- tests for front matter, transfer text, and submission contract

## 5.3 Method

### Step 1 — Introduce an explicit audit target

Implement the schema-v3 `stability_audits` representation in §3.4. The target key must identify all dimensions needed to prevent leakage:

- endpoint quantity/value/unit;
- support set;
- resampling scheme;
- fitting-loss identity;
- scoring-rule identity;
- interval kind;
- quantile probabilities;
- canonical draw count and RNG/quantile convention in the audit body.

### Step 2 — Validate the audit against the exact 40 g interval

The artifact checker should locate the unique row and resampling interval identified by the audit key, then verify:

- exactly one matching row exists;
- its scheme exists;
- its support set matches;
- its interval kind and quantiles match;
- its canonical `B` matches;
- the canonical upper bound used in prose is the matching row's full-precision upper bound;
- `upper_bound_sign_is_stable` agrees with the seed extrema:
  - stable positive requires every audited upper bound to be `> 0`;
  - stable negative requires every audited upper bound to be `< 0`;
  - any zero contact or mixed signs requires `false` unless a separately documented convention applies;
- lower/upper MCSE values are finite and positive;
- `coverage_calibrated` is explicitly false.

Do not infer the audited target merely because the current upper bound numerically resembles a stored mean.

### Step 3 — Generate one audit-aware claim object

Recommended internal representation:

```python
@dataclass(frozen=True)
class NumericalStabilityClaim:
    audit_key: AuditKey
    bound: str
    canonical_value_pp: float
    monte_carlo_se_pp: float
    se_distance_from_zero: float
    sign_stable: bool
    seed_min_pp: float
    seed_max_pp: float
    n_runs: int
    coverage_calibrated: bool
```

The builder should calculate `se_distance_from_zero` from the canonical bound and matching bound MCSE. For the reviewed result, it should be approximately 8.14. Do not archive a rounded “8” as a separate truth unless needed for display; derive it.

### Step 4 — Generate the abstract endpoint sentence

Preferred concise wording:

> Across 38–42 g, the paired difference remained **−0.447 to −0.394 pp**. The primary range excluded zero at 38 g and contained it at 40 and 42 g; for the audited 40 g primary/default-loss result, the upper-bound sign was numerically stable. These descriptive ranges have no calibrated coverage or inferential interpretation.

A shorter alternative, if required by the abstract word limit:

> Across 38–42 g, the difference remained **−0.447 to −0.394 pp**; the audited 40 g upper-bound sign was numerically stable, while zero containment changed with endpoint and carried no calibrated inferential meaning.

The generated sentence must explicitly contain “audited 40 g” or equivalent scope. Do not say “the bounds were stable” in the plural unless both bounds and all referenced targets are actually being described.

### Step 5 — Correct the S3 interpretation

Recommended S3 reading:

> The primary range excluded zero below zero at 38 g and contained zero at 40 and 42 g. The retained multi-seed Monte Carlo audit applies only to the 40 g `cond_in_variety` range under the primary/default fitting loss. For that target, the lower- and upper-bound Monte Carlo standard errors at the canonical draw count were approximately **0.000520** and **0.000466 pp**, and all 20 audited upper bounds were positive. The upper-bound sign is therefore numerically stable for that target. These values quantify Monte Carlo approximation only; the ranges are not calibrated confidence intervals and do not support superiority, equivalence, or non-inferiority claims.

### Step 6 — Add contradiction prevention

The strongest prevention is generation from the structured claim. Add a semantic guard as a second layer:

- when `sign_stable is True`, a generated claim may not contain “sign unresolved,” “side of zero unresolved,” or equivalent active wording;
- when `sign_stable is False`, a generated claim may not say “sign settled/stable”;
- any sign-stability statement must carry the audit target's endpoint/scheme/loss scope in the same sentence or immediately preceding sentence;
- every generated claim must include or be adjacent to the no-coverage qualification.

Do not implement this only as broad regex policing of arbitrary prose. The primary output should come from controlled renderers; the regex guard catches accidental manual text.

## 5.4 Potential pitfalls, errors, and oversights

1. **Conflating sign stability with containment stability.** The 40 g upper bound can be stably positive while the interval still contains zero because the lower bound is negative.
2. **Conflating endpoint sensitivity with Monte Carlo noise.** The 38/40/42 classifications are different canonical endpoint results; the 40 g audit only addresses numerical variability at 40 g.
3. **Conflating numerical and inferential resolution.** A stable bound sign does not make the range a confidence interval.
4. **Using the upper-bound audit to qualify the lower bound.** The artifact stores separate lower and upper MCSEs; use the correct one.
5. **Applying the audit to alternative fitting loss.** No alternative-loss multi-seed audit is retained under the recommended Path A.
6. **Using “all bounds” or “each bound.”** Such wording silently expands scope.
7. **Hard-coding 8.1 SE.** Derive it from the exact canonical bound and exact matching MCSE so future artifact changes propagate.
8. **Ignoring seed-level sign convention.** A bound exactly equal to zero needs an explicit convention; do not treat it as positive.
9. **Abstract word-count breach.** Preserve all three concepts while staying inside the 250-word venue limit and the repository's safety band.
10. **Contradictory editor-facing text.** The cover letter and significance paragraph must be checked even if they do not currently repeat the “unresolved” wording.

## 5.5 Required checks

### Unit tests

- build a stable-positive audit fixture and require “numerically stable,” not “unresolved”;
- build a mixed-sign seed fixture and require the stable flag to fail validation;
- build a stable-negative fixture and confirm correct negative sign wording;
- set canonical bound/MCSE to yield a known ratio and confirm derived distance;
- confirm no-coverage language appears for both stable and unstable cases;
- confirm audit scope appears in the rendered sentence;
- confirm missing or duplicate exact audit keys fail rather than select the first record.

### Mutation tests

- flip `upper_bound_sign_is_stable` to false while all seed bounds remain positive;
- insert one negative seed upper bound while leaving the stable flag true;
- change target endpoint from 40 to 42 g without adding a 42 g audit;
- change scheme from `cond_in_variety` to `sample_in_variety_grind`;
- change fitting loss to alternative while retaining the same MCSE;
- change quantiles or canonical `B`;
- manually restore “unresolved at the precision this resampling attains” in the YAML or generated supplement.

Every mutation must cause a named failure at either artifact validation, exact-audit lookup, generated-block comparison, or publication consistency.

### Integration checks

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_front_matter.py
python tools/paper_a_consistency.py verify
python -m pytest tests/test_paper_a_transfer_semantics.py -q
python -m pytest tests/test_paper_a_front_matter.py -q
python -m pytest tests/test_paper_a_submission_contract.py -q
```

### Manual checks

- read the abstract, endpoint Results, S3 interpretation, conclusion, and cover letter consecutively;
- confirm they make the same scoped numerical claim;
- confirm none calls the 40 g sign unresolved;
- confirm none describes the 38/40/42 endpoint classification changes as Monte Carlo instability;
- confirm none upgrades the range to confidence-interval status.

## 5.6 Acceptance evidence

P0-2 is closed only when:

- the exact audit key exists in the producer-generated artifact;
- the artifact checker binds it to the 40 g primary/default interval;
- the abstract and S3 are generated from the audit-aware claim;
- stable/unstable contradiction mutations fail;
- all active surfaces retain the no-coverage qualification;
- the abstract remains within its tested word limit.

---
# 6. P1-1 — Scope the Monte Carlo precision to the target actually audited

## 6.1 Objective

Prevent the lower/upper Monte Carlo standard errors from being presented as universal properties of every endpoint, resampling scheme, or fitting loss. Under the recommended remediation, retain the existing audit and state its exact scope rather than commissioning additional audits solely to support broad wording.

## 6.2 Chosen path

Adopt **Path A — scope the existing audit**.

This is the scientifically conservative and operationally efficient remedy because:

- the existing audit already answers the question needed for the 40 g primary/default-loss near-zero upper bound;
- no current central conclusion requires endpoint-specific MCSEs for 38 or 42 g;
- no current central conclusion requires multi-seed precision for secondary schemes or the alternative fitting loss;
- adding numerical audits merely to preserve an overbroad sentence would invert the proper relationship between analysis and reporting.

Future extension remains possible because the proposed `stability_audits` collection is keyed by target.

## 6.3 Affected surfaces

- producer output in `puckworks/validation/slow/angeloni_bracket.py`;
- transfer schema and audit lookup;
- `tools/paper_a_transfer_artifacts.py`;
- `tools/paper_a_transfer_text.py`, especially Table 4a and S3;
- abstract/Methods/Results language where Monte Carlo precision is described;
- endpoint and comparator-loss tests;
- generated manuscript and supplement.

## 6.4 Method

### Step 1 — Represent one exact audit, not a universal scalar

Use the schema-v3 keyed audit described in §3.4. The audit must be discoverable only by an exact `AuditKey`. Remove code such as:

```python
ep["stability_audit"]["upper_monte_carlo_se_at_canonical_B_pp"]
```

from generic table or paragraph renderers. Replace it with:

```python
audit = find_exact_audit(ep, EXPECTED_40G_PRIMARY_DEFAULT_AUDIT_KEY)
```

The lookup function must:

- return exactly one audit;
- fail on zero matches;
- fail on multiple matches;
- never use a partial match;
- never fall back to the first/top-level audit.

### Step 2 — Use separate lower and upper values

For the audited target, retain the actual values:

- lower-bound MCSE at canonical `B`: approximately `0.0005201594 pp`;
- upper-bound MCSE at canonical `B`: approximately `0.0004655904 pp`.

Where compact prose is necessary, it is acceptable to say “both approximately `0.0005 pp`,” but do not attach a symmetric `±0.0005 pp` to the range as though one scalar described both bound estimators exactly. Preferred wording is “lower- and upper-bound Monte Carlo standard errors were approximately 0.000520 and 0.000466 pp.”

### Step 3 — Correct Table 4a

Remove the current caption statement that the Monte Carlo standard error “on each bound” is the same for all endpoint rows.

Preferred table design:

| Endpoint | Model MAPE | Comparator MAPE | Paired difference | Primary range | Zero relation | MC audit |
|---|---:|---:|---:|---:|---|---|
| 38 g | … | … | … | … | below zero | not separately audited |
| 40 g | … | … | … | … | contains zero | lower/upper MCSE 0.000520/0.000466 pp |
| 42 g | … | … | … | … | contains zero | not separately audited |

If an extra column makes the table too wide, use a dagger on the 40 g row and a scoped note immediately below:

> † The retained multi-seed Monte Carlo audit applies only to the 40 g `cond_in_variety` range under the primary/default fitting loss. At the canonical draw count, the lower- and upper-bound Monte Carlo standard errors were approximately 0.000520 and 0.000466 pp. The 38 and 42 g bounds were not separately audited.

Do not put “not audited” in a way that implies the underlying canonical range was not computed; only the multi-seed Monte Carlo precision audit is absent.

### Step 4 — Correct S3

S3 spans all endpoints and schemes, so the MC audit note must be visibly scoped. Use the wording in §5.3 and make clear that:

- all displayed ranges use the canonical draw count;
- the **multi-seed estimate of Monte Carlo variability** exists only for one target;
- no secondary scheme or alternative fitting loss inherits that value.

### Step 5 — Correct Methods and Results references

Review every occurrence of:

- “each bound”;
- “the bounds near zero”;
- “the Monte Carlo error is…”;
- plural “bounds were stable”;
- `±0.0005 pp`.

Each occurrence must identify the 40 g primary/default target or be removed. The Methods may explain the audit procedure generally, but its reported numerical result must remain scoped.

### Step 6 — Preserve three-decimal display with the correct qualification

Retain three decimals in the publication tables. Add a scoped statement such as:

> Three decimals are retained to distinguish a small positive bound from exact contact with zero. For the audited 40 g primary/default range, seed-to-seed variation implies numerical resolution of approximately `±0.001 pp` at the displayed precision; the exact final displayed digit should not be treated as seed-invariant.

This avoids the two opposite errors:

- coarsening to two decimals and falsely making the bound look exactly zero;
- presenting the third decimal as perfectly repeatable.

### Step 7 — Make audit-scope leakage a contract failure

Add `validate_stability_audits()` to the artifact contract. It should verify:

- schema and required fields;
- exact target key;
- uniqueness of keys and `audit_id`;
- finite MCSEs;
- consistent `n_runs == len(seeds)`;
- seed uniqueness;
- correct canonical/seed draw counts;
- target interval existence;
- seed extrema and sign-stability consistency;
- no claim of calibrated coverage.

The transfer-text renderer should not accept a raw numeric MCSE. It should accept an already validated `NumericalStabilityClaim` tied to an `AuditKey`.

## 6.5 Potential pitfalls, errors, and oversights

1. **Calling unaudited endpoints numerically unstable.** Absence of a multi-seed audit means “not separately audited,” not “unstable.”
2. **Using one MCSE for both bounds.** The values are close but distinct.
3. **Using `±` carelessly.** MCSE is a standard error estimate for a bound estimator, not an interval half-width around the published range.
4. **Auditing by endpoint only.** Scheme, loss, scoring rule, quantiles, support, `B`, RNG, and interval kind are part of the target.
5. **Partial-key lookup.** A lookup that ignores loss or scheme recreates the leakage.
6. **Silent fallback.** Missing audit keys must fail rendering, not produce prose without a warning.
7. **Overloaded “default loss.”** Give the fitting loss a stable machine ID; do not use a display label as the key.
8. **Confusing canonical seed with multi-seed audit.** The canonical interval can use seed 0 at `B=1,000,000` while the stability audit uses 20 seeds at `B=200,000` and scales the SD. Preserve that distinction.
9. **Claiming all digits stable.** The artifact says the display interval varies across seeds; sign stability and display-string stability are different.
10. **Accidentally extending the claim to comparator-loss sensitivity.** The alternative-loss range has no retained multi-seed audit under Path A.

## 6.6 Required checks

### Unit tests

- exact audit lookup succeeds for the canonical 40 g key;
- lookup fails when endpoint, scheme, loss, score, support, quantiles, or interval kind differs;
- duplicate keys fail;
- lower and upper render with their own MCSE;
- table renderer marks only 40 g as audited;
- 38 and 42 g render as “not separately audited,” not “unstable”;
- alternative fitting loss does not receive an MCSE;
- third-decimal explanation remains present and no coverage wording appears.

### Mutation tests

| Mutation | Required failure |
|---|---|
| Change audit endpoint to 42 g | exact target interval/audit binding failure |
| Change scheme to `sample_in_variety_grind` | missing exact target or mismatch |
| Change fitting loss ID | missing exact audit |
| Change scoring rule | missing exact audit |
| Copy the 40 g audit onto 38/42 g table rows | rendered-block/semantic test failure |
| Replace lower MCSE with upper MCSE | bound-specific assertion failure |
| Remove `coverage_calibrated: false` | schema/contract failure |
| Add “each bound” to Table 4a caption | publication-contract failure |

### Integration and review

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_consistency.py verify
python -m pytest tests/test_paper_a_transfer_semantics.py \
                 tests/test_paper_a_transfer_contract.py \
                 tests/test_paper_a_submission_contract.py -q
```

Then inspect Table 4a and S3 in rendered Markdown/PDF form to ensure the scoped footnote is visibly associated with the 40 g row.

## 6.7 Acceptance evidence

P1-1 is closed when:

- the artifact has an exact keyed 40 g audit;
- no generic renderer reads a top-level scalar MCSE;
- no active publication surface attaches `0.0005 pp` to 38 g, 42 g, secondary schemes, or alternative loss;
- target-leakage mutations fail;
- three-decimal display and the no-coverage qualification are retained.

---

# 7. P1-2 — Make the endpoint contract fail closed

## 7.1 Objective

Require the endpoint artifact to contain exactly the declared 38/40/42 g result rows, in valid form, and make missing, empty, malformed, duplicate, extra, non-finite, or retired-key rows fail both the artifact checker and routine `verify` command with explicit diagnostics.

## 7.2 Affected code

- `puckworks/paper_a/transfer_contract.py`
- `tools/paper_a_transfer_artifacts.py`
- `tools/paper_a_consistency.py`
- `tests/test_paper_a_transfer_contract.py`
- `tests/test_paper_a_submission_contract.py`
- optionally a new reusable mutation fixture module under `tests/fixtures/`

## 7.3 Method

### Step 1 — Remove the conditional validation gate

Delete the pattern that validates rows only when they are already a non-empty list with the key in the first row. Validation must start from a sentinel that distinguishes a missing property from a property whose value is `None`.

Recommended fail-closed structure:

```python
_MISSING = object()


def validate_endpoint_contract(artifact: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(artifact, dict):
        return ["artefact is not a dictionary"]

    # Validate top-level retired keys and typed endpoint object.
    ...

    rows = artifact.get("rows", _MISSING)
    if rows is _MISSING:
        problems.append("artefact omits required endpoint `rows`")
        return problems
    if not isinstance(rows, list):
        problems.append("endpoint `rows` must be a list")
        return problems
    if len(rows) != len(ENDPOINT_TARGETS):
        problems.append(
            f"endpoint `rows` has {len(rows)} entries; expected {len(ENDPOINT_TARGETS)}"
        )

    parsed_targets: list[float] = []
    for index, row in enumerate(rows):
        prefix = f"endpoint rows[{index}]"
        if not isinstance(row, dict):
            problems.append(f"{prefix} must be a dictionary")
            continue

        for retired in RETIRED_ENDPOINT_KEYS:
            if retired in row:
                problems.append(f"{prefix} carries retired key {retired!r}")

        if ENDPOINT_ROW_KEY not in row:
            problems.append(f"{prefix} omits required key {ENDPOINT_ROW_KEY!r}")
            continue

        raw = row[ENDPOINT_ROW_KEY]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            problems.append(f"{prefix}.{ENDPOINT_ROW_KEY} must be numeric")
            continue
        value = float(raw)
        if not math.isfinite(value):
            problems.append(f"{prefix}.{ENDPOINT_ROW_KEY} must be finite")
            continue
        parsed_targets.append(value)

        problems.extend(validate_endpoint_result_row(row, index=index))

    expected = [float(v) for v in ENDPOINT_TARGETS]
    if parsed_targets != expected:
        problems.append(
            f"endpoint rows cover/order {parsed_targets!r}; expected {expected!r}"
        )
    return problems
```

### Step 2 — Require canonical order deliberately

The existing top-level endpoint contract already states “exact set and order.” Apply the same rule to rows: `[38.0, 40.0, 42.0]` in that order. This supports deterministic artifact diffs and table generation.

If maintainers prefer set-only semantics, that choice must be explicit and the renderer must sort. The recommended approach is canonical order because the artifact is generated, not manually assembled.

### Step 3 — Validate row fields used by publication generation

A row containing only `m_target_g` is sufficient for a narrow endpoint-key unit fixture, but a real endpoint propagation artifact should require the fields its scientific claims consume. Add an artifact-specific validator, separate from the generic endpoint declaration validator if necessary:

```python
REQUIRED_ENDPOINT_RESULT_FIELDS = (
    "m_target_g",
    "support_set",
    "pooled_model_mape",
    "pooled_const_mape",
    "paired_difference_pp",
    "paired_median_pp",
    "n_points",
    "n_model_worse_than_const",
    "skill_vs_const",
    "resampling",
)
```

For each row:

- require all fields;
- reject booleans where numeric values are expected;
- require finite numerical values;
- require `n_points == corpus.n_observations` for the support set;
- require `0 <= n_model_worse_than_const <= n_points`;
- require every declared scheme exactly once in `resampling`;
- validate every interval record;
- require each scheme's `observed_mean_delta_pp` to agree with `paired_difference_pp` within the producer's declared precision/tolerance;
- require scheme `B`, seed, RNG, quantiles, and interval kind;
- reject unknown/retired endpoint keys anywhere in the row.

Do not overburden `validate_endpoint_contract()` with every endpoint-science rule if it is intended for comparator-loss artifacts too. A clean split is:

```python
validate_endpoint_declaration_and_rows(...)
validate_endpoint_propagation_artifact(...)
validate_comparator_loss_artifact(...)
```

Both specialized validators call the shared declaration/row-key validator.

### Step 4 — Make downstream checkers robust to malformed rows

After the central validator reports a malformed row, downstream loops must not crash while trying to produce additional diagnostics. Use defensive guards:

```python
if not isinstance(rows, list):
    rows = []
for index, row in enumerate(rows):
    if not isinstance(row, dict):
        continue
    ...
```

A malformed artifact should produce a clear list of validation failures, not a traceback that hides the root defect.

### Step 5 — Make both assurance paths exercise the strict validator

Confirm:

- `paper_a_transfer_artifacts.py --check` invokes the specialized endpoint-artifact validator;
- `paper_a_consistency.py verify` invokes the same strict validation or the artifact checker itself;
- neither path uses `ep.get("rows") or []` as a substitute for presence validation;
- the CLI exits non-zero for every row mutation.

### Step 6 — Improve diagnostics

Messages should identify:

- artifact label;
- row index;
- endpoint value when available;
- missing/invalid field;
- expected value/set/order.

Examples:

```text
endpoint: artefact omits required endpoint `rows`
endpoint: endpoint `rows` has 0 entries; expected 3
endpoint: endpoint rows[1] omits required key `m_target_g`
endpoint: endpoint rows cover/order [38.0, 42.0, 42.0]; expected [38.0, 40.0, 42.0]
endpoint: endpoint rows[2].m_target_g is non-finite (nan)
```

## 7.4 Potential pitfalls, errors, and oversights

1. **Returning early too soon.** It is reasonable to stop row traversal when `rows` is not a list, but still report top-level endpoint defects collected before that point.
2. **`bool` as `int`.** In Python, `True` is an `int`; explicitly reject booleans.
3. **NaN set behavior.** Do not rely on set comparison for finite validation or duplicates.
4. **Float coercion of arbitrary strings.** Reject strings rather than silently accepting `"40"` unless the schema explicitly permits them.
5. **First-row-only retired-key scan.** Check every row.
6. **Duplicate 42 g row masking missing 40 g.** Compare ordered list and/or `Counter`, and report both duplicate and missing values where useful.
7. **Malformed row crashes.** Continue validation after a non-dict row.
8. **Generic fixture mismatch.** Update the “valid minimal artifact” test to reflect the precise layer being tested; do not weaken production validation to preserve an overly minimal fixture.
9. **Comparator-loss artifact shape.** Its rows are fitting-loss rows rather than endpoint rows. The shared endpoint declaration validator must not incorrectly require `m_target_g` in those rows unless the comparator-loss schema is updated to carry an explicit endpoint value. Prefer adding `endpoint_value_g: 40.0` to comparator-loss rows or validating that artifact under a dedicated contract.
10. **Schema compatibility.** Version-2 artifacts should produce a clear migration error, not pass under relaxed compatibility logic.

## 7.5 Required mutation matrix

At minimum, implement the following table as parameterized tests:

| Mutation | Expected diagnostic class |
|---|---|
| Delete `rows` | required property missing |
| `rows = None` | wrong type |
| `rows = "..."` | wrong type |
| `rows = []` | wrong length |
| Remove 38, 40, or 42 row | wrong length/set/order |
| Duplicate any row | duplicate/missing target |
| Add 44 g row | extra target/wrong length |
| Replace a row with `None`, list, string | row not dictionary |
| Remove target key from first/middle/last row | required key missing |
| Target `None`, string, `True`, NaN, `+inf`, `-inf` | invalid numeric target |
| Reverse row order | order mismatch |
| Insert retired key into first/middle/last row | retired key failure |
| Delete `resampling` from a real result row | required result field missing |
| Delete a declared scheme | specialized endpoint validator failure |
| Change `n_points` away from 132 | corpus/row mismatch |

### CLI-level tests

For representative mutations, write a temporary artifact and monkeypatch the path, then assert:

- `paper_a_transfer_artifacts.check()` returns a named problem;
- `paper_a_consistency.check_paper_a(include_release=False)` or its endpoint subcheck returns a named problem;
- CLI return code is non-zero;
- no traceback is emitted.

## 7.6 Checks

```bash
python -m pytest tests/test_paper_a_transfer_contract.py -q
python -m pytest tests/test_paper_a_submission_contract.py -q
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_consistency.py verify
```

Re-run the original independent mutations and require non-empty diagnostics for all five previously false-green cases.

## 7.7 Acceptance evidence

P1-2 is closed when:

- every missing/empty/keyless mutation from the Round 9 audit fails;
- the expanded malformed-row matrix fails with explicit diagnostics;
- both named assurance layers fail the representative mutations;
- the valid current schema-v3 artifact passes;
- validation reports problems rather than crashing.

---

# 8. P1-3 — Independently bind resampling membership to the source CSV

## 8.1 Objective

Verify that every observation is assigned to the scientifically correct stratum and cluster under each declared resampling scheme, using an implementation independent of the artifact membership and preferably independent of the production grouping functions.

The source oracle must detect wrong partitions even when observation count, cluster count, cluster-size distribution, complete observation set, and refreshed self-hash are unchanged.

## 8.2 Proposed architecture

Create a dedicated source-check module:

```text
puckworks/paper_a/source_resampling_oracle.py
```

or keep it checker-local if package exposure is undesirable. The module should:

- parse `puckworks/data/angeloni2023/bioactives.csv` directly with `csv.DictReader`;
- ignore comment lines beginning with `#`;
- select the held-out coarse/fine records (`granulometry` in `C`, `F`);
- derive the three observation IDs per sample from the declared named solutes;
- construct all four scheme memberships from source fields;
- emit a canonical normalized design for comparison;
- never read artifact membership while constructing expected membership;
- not call `TC.cluster_membership()`, `TC.scheme_design()`, `TC.resampling_design()`, `TC.cluster_key_of()`, or `TC.stratum_key_of()`.

Using a separate implementation is intentional duplication: the production grouping code and the verification oracle must be able to disagree.

## 8.3 Source-derived scientific specification

The oracle should encode and document the four schemes directly.

### Scheme A — `cond_in_variety` (primary)

- **Stratum:** variety (`Arabica` or `Robusta`).
- **Cluster key:** `variety | temperature | pressure`.
- **Members:** every named-solute observation for all held-out C/F sample records at that variety/condition.
- **Expected size:** six observations when both C and F records exist at the condition; three for off-grid conditions represented by one held-out record.
- **Expected census:** 26 clusters: 18 of size 6 and 8 of size 3.

### Scheme B — `sample_in_variety_grind`

- **Stratum:** `variety | grind`.
- **Cluster key:** sample ID.
- **Members:** the three co-measured named-solute observations for that sample.
- **Expected census:** 44 clusters, all size 3, across four strata.

### Scheme C — `cond_in_group`

- **Stratum:** `variety | solute`.
- **Cluster key:** `variety | solute | temperature | pressure`.
- **Members:** C and F observations for that solute at the same condition when both exist; one observation at off-grid conditions represented by one record.
- **Expected census:** 78 clusters: 54 of size 2 and 24 of size 1, across six strata.

### Scheme D — `group`

- **Stratum:** none / one global stratum.
- **Cluster key:** `variety | solute`.
- **Members:** all 22 held-out sample observations for that variety/solute.
- **Expected census:** six clusters, all size 22.

### Observation identity

Use one canonical format everywhere:

```text
{sample_id}|{solute_id}
```

The oracle must verify that:

- sample IDs are unique in the held-out source rows;
- each selected sample yields exactly the declared three observation IDs;
- the total is 132 unique IDs;
- no observation ID contains an unexpected delimiter or empty part;
- temperature and pressure keys are formatted canonically so `9` and `9.0` do not become separate clusters.

## 8.4 Canonical representation

Normalize both expected and artifact designs before comparison. Suggested normalized scheme object:

```python
{
    "scheme": "cond_in_variety",
    "role": "primary conservative dependence sensitivity",
    "strata_fields": ["variety"],
    "cluster_key_fields": ["variety", "temperature_degC", "pressure_bar"],
    "clusters": [
        {
            "stratum_id": "Arabica",
            "cluster_id": "Arabica|88|6",
            "sample_ids": ["A20", "A31"],
            "grinds": ["C", "F"],
            "observation_ids": [
                "A20|5CQA", "A20|caffeine", "A20|trigonelline",
                "A31|5CQA", "A31|caffeine", "A31|trigonelline"
            ]
        }
    ]
}
```

Canonicalization rules:

- sort schemes by declared scheme order;
- sort clusters by `(stratum_id, cluster_id)`;
- sort `sample_ids`, `grinds`, and `observation_ids` lexically;
- normalize numeric condition components through one source-oracle formatter;
- derive `n_observations`, `n_clusters`, `n_strata`, and cluster-size distribution from the normalized clusters;
- compute a source-oracle hash only after canonicalization.

The artifact's self-hash may remain useful for tamper detection, but source correctness is established by exact normalized comparison.

## 8.5 Method

### Step 1 — Parse the CSV independently

Use `csv.DictReader` rather than the production data loader for the oracle. Validate required columns:

```text
sample, variety, T_degC, p_bar, granulometry, on_grid
```

The named solutes are scientifically declared as `caffeine`, `trigonelline`, and `5CQA`; map source columns as needed without depending on the production observation-expansion function. Document any mapping such as caffeine concentration source column separately from the observation label.

The oracle is validating partition identity, so it does not need model errors or PDE results.

### Step 2 — Construct expected observation records

For each held-out C/F source row and each named solute, create:

```python
{
    "observation_id": f"{sample}|{solute}",
    "sample_id": sample,
    "variety": variety,
    "grind": granulometry,
    "temperature_degC": parsed_T,
    "pressure_bar": parsed_p,
    "solute": solute,
    "on_grid": parsed_bool,
}
```

Validate 44 source samples × 3 solutes = 132 observations before grouping.

### Step 3 — Implement each grouping branch explicitly

Do not parameterize the oracle through the same `SCHEMES` metadata or cluster-key functions that production uses. Four explicit branches are easier to audit and reduce common-mode failure. Shared low-level utilities such as canonical number formatting may be used if independently tested.

### Step 4 — Compare exact scheme metadata and membership

For every scheme, compare:

- role;
- strata field declaration;
- cluster-key field declaration;
- realized stratum IDs;
- realized cluster IDs;
- exact observation list in every cluster;
- exact sample list and grinds, if archived;
- per-cluster `n_observations`;
- total observation set;
- number of clusters and strata;
- size distribution;
- canonical membership hash.

The exact membership comparison is primary. Aggregate census comparisons are derived diagnostics, not the oracle.

### Step 5 — Produce concise, actionable diffs

When membership differs, report the first several discrepancies plus totals. Example:

```text
endpoint: scheme 'sample_in_variety_grind' membership differs from source oracle
  cluster 'A12': missing ['A12|5CQA']; unexpected ['A13|5CQA']
  cluster 'A13': missing ['A13|5CQA']; unexpected ['A12|5CQA']
  2 clusters differ; counts and size distribution happen to remain unchanged
```

For a primary-condition swap:

```text
endpoint: scheme 'cond_in_variety' cluster 'Arabica|88|12'
  missing ['A19|5CQA']; unexpected ['A20|5CQA']
```

Cap verbose output while retaining a machine-readable complete diff option if useful.

### Step 6 — Derive census assertions from the oracle

Replace hard-coded checker maps such as `26/44/78/6` and the primary `{"3": 8, "6": 18}` as the primary source of truth. The checker may retain explicit expected scientific census tests, but it should calculate the artifact-comparison expectations from the source oracle.

This yields two independent checks:

1. source oracle produces the scientifically expected census;
2. artifact exactly equals the source oracle.

### Step 7 — Verify artifact hashes correctly

Maintain two distinct hashes if needed:

- `membership_sha256`: canonical hash stored inside the artifact;
- source-oracle hash recomputed from CSV.

Require equality, but do not stop at hash equality. Exact structural comparison gives intelligible diagnostics and protects against accidental hash-input differences. The hash is a compact provenance marker, not the sole proof.

## 8.6 Potential pitfalls, errors, and oversights

1. **Reusing production grouping functions.** This is the most important pitfall; it would let a common bug certify itself.
2. **Reusing artifact metadata to decide expected grouping.** Scheme names may select one of four independently coded branches, but artifact `strata` or `cluster_key` values must not drive the oracle.
3. **Parsing comments as CSV rows.** The source has a leading comment line.
4. **Incorrect solute mapping.** Partition labels use the declared named solutes; verify exact labels and source-column mapping.
5. **Condition formatting drift.** `93.4`, `9`, and `9.0` must canonicalize consistently without merging distinct values.
6. **Pairing by row order.** C/F condition pairing must use source fields, never adjacent row position.
7. **Off-grid assumptions.** Off-grid records yield single-record clusters under condition-based schemes; do not force C/F pairs where none exist.
8. **Sample ID/variety inference.** Use the explicit `variety` column rather than deriving variety only from the first character of sample ID.
9. **Ignoring strata.** Two designs can have identical clusters but different resampling strata; compare both.
10. **Comparing sets only.** Set equality loses cluster ownership and duplicates.
11. **Hash-refresh mutation.** Tests must recompute the artifact self-hash after mutation so they prove the source oracle, not stale-hash detection, catches the error.
12. **Overly brittle order comparison.** Canonicalize before comparing so harmless JSON ordering does not fail.
13. **Oracle drift without review.** Put scheme definitions in one readable, heavily tested module and require deliberate updates when scheme science changes.
14. **Using only current sample examples.** Add generic synthetic fixtures as well as current-source tests so the oracle logic is not merely a snapshot.

## 8.7 Required mutation tests

Every mutation below must preserve the total observation set, relevant counts, cluster-size distribution, and refreshed artifact membership hash:

| Mutation | Scientific violation |
|---|---|
| Swap `A12|5CQA` and `A13|5CQA` in sample scheme | splits co-measured solutes across wrong samples |
| Swap `A19|5CQA` and `A20|5CQA` in primary scheme | assigns observations to wrong T/p clusters |
| Change one cluster's `stratum_id` but keep members | wrong resampling stratum |
| Change cluster ID while keeping membership | wrong declared key/provenance |
| Move one C observation into the matching F sample cluster | sample ownership violation |
| Pair C and F records from different pressure or temperature | wrong condition dependence |
| Move an off-grid observation into an on-grid condition cluster | false condition pairing |
| Swap same-size whole clusters between varieties | wrong variety stratum while census remains identical |
| Remove one observation and duplicate another | complete count can remain 132 but identity is wrong |
| Change scheme role or strata-field declaration | metadata/design mismatch |

For each, assert that:

- `TC.validate_resampling_design()` may still check internal form, but the new source-oracle comparison fails;
- `paper_a_transfer_artifacts.py --check` fails;
- the diagnostic names the scheme and cluster/observation mismatch;
- refreshing the self-hash does not clear the failure.

## 8.8 Additional positive tests

- source oracle returns 44 held-out C/F samples and 132 observations;
- each sample has exactly three named-solute observations;
- current expected census and size distributions match;
- reversing CSV row order leaves canonical oracle output/hash unchanged;
- harmless JSON membership ordering changes do not fail after canonicalization;
- a genuine source-field change changes the oracle output and causes artifact mismatch;
- all four schemes cover the identical 132-observation set exactly once.

## 8.9 Checks

```bash
python -m pytest tests/test_paper_a_transfer_contract.py -q
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_consistency.py verify
```

Add a dedicated retained mutation-audit command or test selection, for example:

```bash
python -m pytest tests/test_paper_a_transfer_contract.py \
  -k 'source_oracle or wrong_membership or refreshed_hash' -q
```

## 8.10 Acceptance evidence

P1-3 is closed when:

- the independent source oracle is visibly separate from production grouping code;
- exact membership and strata are compared for all four schemes;
- hard-coded aggregate counts are no longer the primary membership proof;
- both original Round 9 swaps fail even after self-hash refresh;
- the full mutation matrix fails with actionable diagnostics;
- the unmodified current artifact passes against the CSV-derived oracle.

---
# 9. P2-1 — Remove publication-process leakage and expand the scanner

## 9.1 Objective

Ensure that journal readers encounter scientific rationale, evidence, and conventional references rather than repository history, review-ticket identifiers, generator self-congratulation, or internal working paths. Expand automated scanning to every visible publication surface while preserving legitimate data/code availability references and ignoring hidden generation comments.

## 9.2 Affected surfaces

### Reader-facing text requiring revision

- dimensional-audit discussion containing “An earlier draft promised one…”;
- Results passages citing internal `docs/paper1_resource/...` files;
- external-data wording containing “already in the repo as…”;
- Supplementary Table S5 interpretation containing `(round-7 P1-4)`;
- Supplementary Table S6 caption saying it was generated so it “cannot disagree”;
- corresponding canonical-draft copies where generated or manually mirrored.

### Scanner and tests

- `tools/paper_a_consistency.py`;
- `tests/test_paper_a_submission_contract.py`;
- possibly `tests/test_paper_a_supplement.py` if separated;
- `docs/figures/PAPER_A_CAPTIONS.md` as a newly scanned publication surface.

## 9.3 Method

### Step 1 — Rewrite each identified passage scientifically

Use direct scientific wording rather than describing prior drafts or repository state.

#### Dimensional-audit passage

Replace process narration such as:

> An earlier draft promised one…

with a direct result and rationale, for example:

> No quantitative intersection is reported because the solid-inventory assay and the model inventory are not demonstrably commensurate on a common volumetric basis. The assay is retained as an orthogonal same-campaign comparison, with the plausible basis sensitivity shown in Supplementary Table [appropriate number].

#### Internal result paths

Replace visible paths such as:

```text
docs/paper1_resource/PAPER_A_OBJECTIVE_FAMILY_PANELS.json
```

with one of:

- a numbered main-text or supplementary table/figure reference;
- a conventional citation;
- an archival DOI/repository citation in the Data and Code Availability section.

A journal reader should not need the repository tree to follow a Results paragraph.

#### External data description

Replace:

> already in the repo as…

with conventional scientific identification, for example:

> The external dissolved-solids trajectory from Waszkiewicz et al. was evaluated as an independent cross-context shape test…

Use the normal reference system and identify any archived machine-readable transcription in Data and Code Availability, not in the Results narrative.

#### Review ticket

Delete `(round-7 P1-4)` entirely. If it was carrying scientific qualification, replace the qualification in ordinary language.

#### S6 caption

Replace generator self-praise:

> Generated from the archived design object, so the Methods paragraph and this table cannot disagree.

with scientific content:

> The four schemes use the same 132 held-out observations but impose different dependence units and strata. The primary `cond_in_variety` scheme preserves condition-level dependence within variety; the three secondary schemes show sensitivity to alternative defensible dependence assumptions.

Generation provenance belongs in an HTML comment, code documentation, or reproducibility record, not the visible caption.

### Step 2 — Define the complete publication scan set

Replace the misleading narrow tuple with explicit groups:

```python
CAPTIONS = _REPO / "docs" / "figures" / "PAPER_A_CAPTIONS.md"

REVIEWER_FACING_FILES = (
    CONVERSION,
    PACKAGE,
    HIGHLIGHTS,
    COVER_LETTER,
    SUPPLEMENT,
    CAPTIONS,
)

AUTHORITATIVE_PUBLICATION_FILES = (
    CANONICAL,
    *REVIEWER_FACING_FILES,
)
```

Use the authoritative set for process-language scanning. The canonical draft may not be sent directly, but it can feed or mirror submission text and should not retain active process narration outside an explicitly designated review-history section.

Update the test sandbox so it patches and copies **all** scanned files, including supplement and captions. Do not leave a test fixture that silently redefines the tuple without them.

### Step 3 — Strip hidden comments while preserving line numbers

Implement a helper that replaces every non-newline character inside an HTML comment with a space, preserving newlines and string length:

```python
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def visible_markdown(text: str) -> str:
    def blank(match: re.Match[str]) -> str:
        return "".join("\n" if c == "\n" else " " for c in match.group(0))
    return _HTML_COMMENT.sub(blank, text)
```

This prevents hidden generation comments from triggering the scan and preserves accurate line numbers.

Do not simply delete comments because line diagnostics would shift.

### Step 4 — Add section-aware handling of legitimate paths

Internal/repository paths can be legitimate in a Data and Code Availability section. Avoid a blanket allowlist that permits them everywhere.

Recommended approach:

1. split visible Markdown into heading-defined sections while retaining line spans;
2. normalize heading text;
3. allow repository paths only under headings matching a small set such as:
   - `Data and code availability`;
   - `Data availability`;
   - `Code availability`;
   - `Availability of data and materials`;
4. optionally allow the reproducibility supplement section if the journal package deliberately includes it;
5. outside those sections, flag back-ticked or plain internal paths beginning with `docs/`, `tools/`, `tests/`, `puckworks/`, or `.github/`.

Keep the allowlist narrow and test it both positively and negatively.

### Step 5 — Expand process-language patterns

Add targeted patterns with clear reasons:

```python
_PROCESS_WORDS = [
    ...existing patterns...,
    (re.compile(r"\bearlier drafts?\b", re.I), "draft-history narration"),
    (re.compile(r"\bround[- ]?\d+\b", re.I), "internal review-round identifier"),
    (re.compile(r"\balready in (?:the )?repo(?:sitory)?\b", re.I),
     "repository-state narration"),
    (re.compile(r"\b(?:P0|P1|P2|MC|MAJ|MIN)-?\d+(?:\.\d+)?\b", re.I),
     "internal review ticket ID"),
]

_INTERNAL_PATH = re.compile(
    r"`?(?:docs|tools|tests|puckworks|\.github)/[^\s`),;]+`?",
    re.I,
)
```

Be careful not to flag ordinary scientific uses of “round” such as “round particles” or “round-robin.” The pattern should require a review-number form.

### Step 6 — Scan placeholders and process language in visible text

Use `visible_markdown()` before both placeholder and process scans. The current placeholder checks should also cover the supplement and captions. Continue to report filename, line number, matched text, and reason.

### Step 7 — Keep internal history in appropriate places

Do not delete valuable provenance from source comments or review resources. Move implementation history to:

- Python docstrings/comments;
- HTML comments in generated Markdown;
- `docs/paper1_resource/` review/remediation records;
- changelog/PR descriptions;
- reproducibility metadata.

The requirement is to remove it from active scientific exposition, not erase project history.

## 9.4 Potential pitfalls, errors, and oversights

1. **Scanning hidden comments.** This creates false positives from useful generator instructions.
2. **Deleting comments and shifting line numbers.** Preserve newline positions.
3. **Overbroad `round` pattern.** Require a numeric review form.
4. **Overbroad path ban.** Data/Code Availability legitimately names repository paths.
5. **Global path allowlist.** A path allowed once in Availability should not become allowed in Results.
6. **Omitting captions again.** Standalone captions can be supplied to a journal separately.
7. **Omitting the canonical draft.** It can re-seed process language into generated submission text later.
8. **Only scanning generated outputs.** Source templates/YAML should also be tested where visible text originates.
9. **Removing scientific qualification with the ticket.** Convert the qualification into reader-facing language before deleting the ticket ID.
10. **Replacing a path with an unavailable supplement reference.** Verify that the numbered item exists and is cited correctly.
11. **Visible generator claims in tables.** Captions and table notes count as reader-facing prose.
12. **Fenced code blocks.** A Data/Code Availability code block may legitimately show commands/paths; handle it under the same section-aware rule rather than globally ignoring all code.

## 9.5 Required tests

### Scanner inclusion tests

Inject each prohibited phrase separately into:

- manuscript;
- package;
- cover letter;
- supplement;
- standalone captions;
- canonical draft.

Require a failure with the correct file and line.

### Phrase tests

At minimum:

- `An earlier draft promised one`;
- `round-7`;
- `P1-4`;
- `already in the repo as`;
- back-ticked `docs/paper1_resource/example.json` in Results;
- `tools/example.py` in a supplement caption;
- existing `PI action` and backlog-language patterns.

### Allowlist tests

- a repository path in `## Data and code availability` passes;
- the same path in `## Results` fails;
- a path in an HTML comment passes because it is invisible;
- a ticket ID in an HTML comment passes;
- a visible unresolved placeholder in the supplement fails;
- a visible unresolved placeholder in captions fails.

### Structural tests

- test sandbox includes all scanned files;
- deleting supplement or caption path from the scan tuple causes a non-vacuity test to fail;
- line numbers remain correct after multiline comments preceding a violation.

## 9.6 Checks

```bash
python tools/paper_a_consistency.py verify
python -m pytest tests/test_paper_a_submission_contract.py -q
rg -n -i 'earlier draft|round-[0-9]+|already in (the )?repo|`docs/' \
  docs/PAPER_A_DRAFT.md docs/submission docs/figures/PAPER_A_CAPTIONS.md
```

Review any remaining matches manually. Matches inside designated availability sections or hidden comments may be legitimate; active Results/Discussion/Supplement captions are not.

## 9.7 Acceptance evidence

P2-1 is closed when:

- all five identified active passages are rewritten scientifically;
- supplement and captions are in the scanner and test sandbox;
- comment stripping and section-aware path handling are tested;
- every injected process phrase fails outside allowed sections;
- the active publication files are clean without deleting useful internal provenance from source comments/resources.

---

# 10. P2-2 — Repair figure visual semantics

## 10.1 Objective

Make Figure 1 evidence categories and Figure S3 panel (b) interpretable without guessing, including in grayscale and at final publication size, while preserving the already-correct dependency graph and layout.

## 10.2 Chosen design

### Figure 1

Retain the conceptual relationship between `in-sample localization` and `within-campaign holdout` if desired by using the same colour family, but give them distinct **complete encodings**:

- `in-sample localization`: blue, solid border;
- `within-campaign holdout`: blue, dashed border;

Other categories retain distinct colours/styles. The legend must display both colour and line style. This makes the categories related but not identical and remains decodable in grayscale.

### Figure S3 panel (b)

Remove the `r > 0.4` / `r < 0` categorical colour rule. Draw every finite correlation bar in one neutral colour, retain the signed horizontal bar length and zero reference line, and mark missing values as `NA` if any. The caption should state that correlations are descriptive and no threshold or significance class is encoded.

## 10.3 Affected code and outputs

- `puckworks/figures_paper_a.py`;
- `tests/test_paper_a_figure_semantics.py`;
- possibly `tests/test_paper_a_figure_layout.py`;
- `docs/figures/PAPER_A_CAPTIONS.md`;
- rendered Figure 1 PNG and any vector form;
- rendered Figure S3 PNG and any vector form;
- manuscript/supplement image copies if duplicated.

## 10.4 Method — Figure 1

### Step 1 — Move style declarations to module-level semantic data

Replace the local colour-only `CAT` mapping with a declared module-level mapping:

```python
FIG1_EVIDENCE_STYLES = {
    "source": {
        "label": "source calibration",
        "edgecolor": NULL,
        "linestyle": "-",
        "linewidth": 2.4,
    },
    "insample": {
        "label": "in-sample localization",
        "edgecolor": GOOD,
        "linestyle": "-",
        "linewidth": 2.4,
    },
    "within": {
        "label": "within-campaign holdout",
        "edgecolor": GOOD,
        "linestyle": "--",
        "linewidth": 2.4,
    },
    ...
}

FIG1_STYLE_ALIASES = {}
```

Use an explicit alias map only when two labels are intentionally the same visual category. For the chosen design, `insample` and `within` are not aliases.

### Step 2 — Render from the style object

The rectangle and legend handle should both consume the same style object. Do not rebuild legend handles from colour alone.

```python
style = FIG1_EVIDENCE_STYLES[spec["cat"]]
ax.add_patch(Rectangle(...,
    edgecolor=style["edgecolor"],
    linestyle=style["linestyle"],
    linewidth=style["linewidth"],
))
```

Legend handles should preserve line style and width so the distinction survives monochrome conversion.

### Step 3 — Keep graph semantics untouched

Do not change:

- `FIG1_NODES` dependency meanings;
- `FIG1_EDGES`;
- `FIG1_LATERAL`;
- forbidden-edge assertions;
- branch calibration-scope labels.

This is a style-semantic repair only.

### Step 4 — Update the caption minimally

Add a compact decoding sentence if the legend is not fully self-evident:

> Border colour and line style identify evidence use; the solid and dashed blue borders distinguish in-sample localization from within-campaign holdout, respectively. Arrows retain the dependency meaning described below.

Avoid burdening the caption if the legend already shows the distinction clearly, but ensure standalone interpretation is possible.

## 10.5 Method — Figure S3 panel (b)

### Step 1 — Remove threshold classification

Replace:

```python
cols = [GOOD if v > 0.4 else BAD if v < 0 else NULL for v in sh]
```

with one declared policy:

```python
S3_SHAPE_CORRELATION_STYLE = {
    "bar_color": NULL,
    "zero_line_color": INK,
    "zero_line_width": 0.8,
    "encodes_threshold_classes": False,
}
```

Then:

```python
finite = ~np.isnan(sh)
ax.barh(idx[finite], sh[finite], color=S3_SHAPE_CORRELATION_STYLE["bar_color"])
for i in np.where(~finite)[0]:
    ax.text(0.0, i, "NA", ...)
ax.axvline(0.0, ...)
```

### Step 2 — Update the caption

Add:

> Panel (b) shows signed model–data shape correlations using a common neutral bar colour; bar direction and length carry the information. No colour threshold, significance class, or inferential category is applied.

Preserve the existing statement that the correlations are descriptive and the panel is not a temporal trajectory.

### Step 3 — Preserve layout fixes

Do not disturb:

- constrained layout;
- panel-title length limits;
- suptitle spacing;
- existing zero line and axis limits unless a render check shows a problem;
- panel (a) NA and better/worse annotations.

## 10.6 Potential pitfalls, errors, and oversights

1. **Testing colour only.** Figure 1 needs tests for the complete encoding tuple: colour, line style, marker/hatch if used, and width where semantically relevant.
2. **Legend/render mismatch.** The legend must consume the same style map as the nodes.
3. **Creating too many colours.** The chosen line-style distinction avoids unnecessary palette expansion.
4. **Dashed lines rendered poorly at small size.** Use a sufficiently thick border and inspect the journal-sized output.
5. **Relying on hue in grayscale.** The style distinction must remain without colour.
6. **Keeping undocumented thresholds in code.** Remove the threshold logic, not just its colours.
7. **Neutral colour conflated with missing data.** Missing correlations should be explicitly `NA`, not zero-length neutral bars that resemble zero correlation.
8. **Accidentally changing graph structure.** Style refactoring must not touch edge data.
9. **Brittle exact-RGB tests.** Test semantic style identity/difference and renderer use; permit palette updates without invalidating scientific tests.
10. **Raster-only review.** Prefer retaining a vector output for publication and check both PNG and vector if the workflow supports it.
11. **Colour-vision accessibility only.** Grayscale and low-resolution print are also relevant.
12. **Caption drift.** Standalone caption and supplement caption must remain synchronized if stored separately.

## 10.7 Required tests

### Figure 1 semantic-style tests

```python
def encoding(style):
    return (
        style["edgecolor"],
        style["linestyle"],
        style.get("hatch"),
        style.get("marker"),
    )


def test_distinct_fig1_categories_have_distinct_encodings_unless_aliased():
    ...
```

Specifically assert:

- `encoding(insample) != encoding(within)`;
- any duplicate encoding is listed in `FIG1_STYLE_ALIASES` with an explanation;
- all node category IDs have a style;
- every legend entry comes from the declared map;
- forbidden dependency-edge tests still pass.

### Figure S3 tests

- `encodes_threshold_classes` is false;
- all finite panel-(b) bars have one face-colour encoding;
- no code constant or caption contains `r > 0.4` / `r < 0` as colour classes;
- a negative, near-zero, and positive synthetic correlation render with the same bar colour;
- missing value renders as `NA`, not as zero;
- existing layout tests still pass;
- caption states no threshold/significance class is encoded.

### Render inspections

Generate:

- normal-colour publication-size Figure 1;
- grayscale Figure 1;
- normal-colour publication-size Figure S3;
- grayscale Figure S3.

Manual checks:

- the two blue Figure 1 categories are distinguishable without reading node text;
- dashed borders remain visible at final size;
- legend samples match node borders;
- S3 bar sign/length remains obvious;
- no reader could infer statistical classes from colour;
- titles and labels remain unclipped.

## 10.8 Checks

```bash
python -m pytest tests/test_paper_a_figure_semantics.py -q
python -m pytest tests/test_paper_a_figure_layout.py -q
# Run the repository's normal Paper A figure-generation command.
python tools/paper_a_consistency.py verify
```

Also compare image hashes only after confirming the semantic changes visually; an expected image-hash change is not itself proof of correctness.

## 10.9 Acceptance evidence

P2-2 is closed when:

- Figure 1's `insample` and `within` categories have different complete encodings;
- duplicate-encoding tests pass with no undeclared alias;
- Figure S3 uses one neutral bar encoding and no threshold categories;
- captions explain the final encoding accurately;
- colour and grayscale final-size renders have been manually approved;
- all existing graph/layout semantics remain green.

---

# 11. Ordered implementation sequence

The order below avoids regenerating slow artifacts repeatedly and prevents hand-edited outputs from being overwritten later.

## Phase 0 — Freeze and snapshot the baseline

1. Create a remediation branch from the intended implementation baseline.
2. Confirm the reviewed commit ancestry and record the actual starting commit.
3. Retain copies or hashes of:
   - the three transfer JSON artifacts;
   - all generated manuscript/supplement/front-matter outputs;
   - Figure 1 and Figure S3;
   - targeted test output;
   - the Round 9 mutation audit.
4. Extract a machine-readable numeric snapshot of all pre-existing scientific leaves in the transfer artifacts. This will support a no-unintended-numerical-drift comparison after schema-v3 regeneration.
5. Run the existing fast checks before changing code and retain their output.

Suggested snapshot command pattern:

```bash
git rev-parse HEAD > /tmp/paper1_round9_start_commit.txt
sha256sum docs/paper1_resource/PAPER_A_*JSON \
          docs/submission/PAPER_A_JFE_* \
          docs/figures/paper_a/fig1_design.png \
          docs/submission/figures/fig7_per_group_diagnostics.png \
  > /tmp/paper1_round9_baseline_sha256.txt
```

## Phase 1 — Add semantic types and tests

1. Add `transfer_semantics.py`.
2. Add full unit-test matrix for interval relation and estimand direction.
3. Update interval-record generation/validation for schema v3.
4. Add audit-key and exact-lookup types against fixtures.
5. Keep tests green without yet regenerating final publication outputs by using explicit test fixtures.

## Phase 2 — Update producer schema and strict validators

1. Update slow producer output to include:
   - estimand direction;
   - explicit interval semantic fields;
   - keyed `stability_audits` collection;
   - audit target identity and no-coverage flag.
2. Harden endpoint row validation.
3. Add specialized endpoint-propagation and comparator-loss validators.
4. Add the independent source-resampling oracle.
5. Replace aggregate-only membership checks with exact source-oracle comparison.
6. Complete all mutation tests before the slow write.

## Phase 3 — Update all text generators

1. Replace relation and favourability wording in `paper_a_transfer_text.py`.
2. Scope Table 4a and S3 audit wording.
3. Add generated abstract endpoint placeholder.
4. Refactor cover-letter central-result prose to consume the shared claim summary.
5. Update consistency checks for semantic blocks and retired false phrases.
6. Regenerate transfer text and front matter against test fixtures or temporary migrated artifacts as appropriate.

## Phase 4 — Remove process leakage

1. Rewrite identified manuscript and supplement passages at their authoritative source.
2. Add canonical draft, supplement, and captions to the scan set.
3. Add comment stripping and section-aware path handling.
4. Update the sandbox fixture and injection tests.
5. Run scan and inspect all remaining matches.

## Phase 5 — Repair figure semantics

1. Move Figure 1 style metadata to module-level declared data.
2. distinguish `insample` and `within` by line style;
3. remove S3 correlation threshold colours;
4. update captions and tests;
5. render colour/grayscale previews and inspect them.

## Phase 6 — Perform one producer-backed schema-v3 write

After all code and fixture tests pass:

```bash
python tools/paper_a_transfer_artifacts.py --write
```

Then immediately:

1. validate the newly written artifacts;
2. compare pre-existing numeric leaves with the baseline snapshot;
3. investigate any unexpected numerical movement before generating text;
4. retain logs and artifact hashes.

## Phase 7 — Regenerate every dependent output

Use the repository's normal generation order. At minimum:

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --write
python tools/paper_a_front_matter.py --write
python tools/paper_a_supplement.py --write
# Run the normal Paper A figure-generation entry point.
```

If transfer text and supplement generation have a different established order, follow the dependency graph in code and then run all `--check` modes. Do not manually edit generated blocks after this phase.

## Phase 8 — Full verification and submission-surface review

Run targeted tests first, then the full suite. Conduct a final human read of the principal result from abstract through conclusion and supplement, and a visual review of the figures.

---

# 12. File-by-file change map

| File | Required change | Findings |
|---|---|---|
| `puckworks/paper_a/transfer_semantics.py` | New typed interval, estimand, audit-key, and claim logic | P0-1, P0-2, P1-1 |
| `puckworks/paper_a/transfer_contract.py` | Schema v3; interval semantic validation; fail-closed endpoint rows; audit validation | P0-1, P0-2, P1-1, P1-2 |
| `puckworks/paper_a/source_resampling_oracle.py` | New independent CSV-derived partition oracle | P1-3 |
| `puckworks/validation/slow/angeloni_bracket.py` | Emit semantic/estimand fields and keyed audit target from producer | P0-1, P0-2, P1-1 |
| `tools/paper_a_transfer_artifacts.py` | Exact audit binding; strict endpoint validator; exact source-oracle membership comparison | P0-2, P1-1, P1-2, P1-3 |
| `tools/paper_a_transfer_text.py` | Relation-aware prose; correct favourable extremes; scoped MC audit; S3 rewrite | P0-1, P0-2, P1-1 |
| `tools/paper_a_front_matter.py` | Expand controlled abstract placeholder; generate cover-letter central result from claims | P0-1, P0-2 |
| `docs/submission/paper_a_front_matter.yaml` | Replace free endpoint tail with controlled placeholder; maintain word limit | P0-2 |
| `tools/paper_a_supplement.py` | Ensure updated generated S3/S6 content is used | P0-1, P0-2, P1-1, P2-1 |
| `tools/paper_a_consistency.py` | Semantic contradiction checks; complete process scan; comment stripping; section allowlist | all text findings, especially P2-1 |
| `puckworks/figures_paper_a.py` | Declared Figure 1 style tuples; neutral S3 correlation bars | P2-2 |
| `docs/figures/PAPER_A_CAPTIONS.md` | Explain final visual encoding; remove process leakage if present | P2-1, P2-2 |
| `tests/test_paper_a_transfer_semantics.py` | New full relation/audit/favourability matrix | P0-1, P0-2, P1-1 |
| `tests/test_paper_a_transfer_contract.py` | Endpoint deletion/malformed mutations; source-oracle mutations | P1-2, P1-3 |
| `tests/test_paper_a_front_matter.py` | Controlled abstract placeholder and cover-letter claim binding | P0-1, P0-2 |
| `tests/test_paper_a_submission_contract.py` | All-file scanner sandbox; contradiction and process-language mutations | P0-1, P0-2, P2-1 |
| `tests/test_paper_a_figure_semantics.py` | Encoding uniqueness/alias tests; neutral S3 policy | P2-2 |
| Transfer JSON artifacts | Schema-v3 producer output, no unexplained numeric changes | P0-1, P0-2, P1-1, P1-3 |
| Generated manuscript/package/supplement/letter | Regenerate; do not hand-edit generated blocks | P0/P1 text findings, P2-1 |
| Figure outputs | Re-render and visually approve | P2-2 |

---

# 13. Cross-finding test and mutation matrix

| Test/mutation | P0-1 | P0-2 | P1-1 | P1-2 | P1-3 | P2-1 | P2-2 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Both ranges contain zero | ✓ |  |  |  |  |  |  |
| Excluding ranges on opposite sides | ✓ |  |  |  |  |  |  |
| Exact vs display-rounded zero contact | ✓ |  |  |  |  |  |  |
| Reverse estimand favour direction | ✓ |  |  |  |  |  |  |
| Stable flag contradicts seed signs |  | ✓ | ✓ |  |  |  |  |
| Audit target endpoint/scheme/loss mutation |  | ✓ | ✓ |  |  |  |  |
| Universal “each bound” prose injection |  |  | ✓ |  |  |  |  |
| Delete/empty/keyless rows |  |  |  | ✓ |  |  |  |
| NaN/non-dict/duplicate/extra endpoint row |  |  |  | ✓ |  |  |  |
| Refresh-hash wrong sample membership |  |  |  |  | ✓ |  |  |
| Refresh-hash wrong condition membership |  |  |  |  | ✓ |  |  |
| Wrong stratum/cluster key with same counts |  |  |  |  | ✓ |  |  |
| Process phrase in supplement/caption |  |  |  |  |  | ✓ |  |
| Internal path in Results vs Availability |  |  |  |  |  | ✓ |  |
| Duplicate Figure 1 encoding |  |  |  |  |  |  | ✓ |
| S3 threshold colour reintroduced |  |  |  |  |  |  | ✓ |
| Grayscale final-size inspection |  |  |  |  |  |  | ✓ |

Every row in this matrix should correspond to an executable test or a retained manual-review record. Do not mark a finding closed solely because its present-day sentence looks correct.

---

# 14. Numerical no-drift comparison after regeneration

Because the recommended schema update requires a real producer-backed artifact write, distinguish expected structural changes from unexpected scientific changes.

## 14.1 Expected changes

- `schema_version: 2` → `3`;
- new `estimand` object;
- new interval semantic fields derived exactly from bounds;
- `stability_audit` migrated to keyed `stability_audits`;
- explicit audit target fields and `coverage_calibrated: false`;
- hashes that necessarily include changed schema content;
- generated prose and figure image hashes.

## 14.2 Values expected not to change

Unless the producer run reveals a genuine prior nondeterminism or code change, require equality for:

- corpus record membership and source hash;
- endpoint point estimates;
- pooled model/comparator MAPEs;
- all full-precision interval bounds;
- cluster counts, strata, and exact memberships;
- canonical `B`, seed, RNG, and quantile settings;
- loss-robustness point estimates and ranges;
- audit seed list, seed extrema, SDs, and derived MCSEs;
- 38/40/42 zero relations as derived from unchanged bounds.

## 14.3 Comparison implementation

Write a small test/helper that recursively compares old and new JSON after excluding only approved schema paths. Do not use a broad ignore of all metadata.

Pseudo-interface:

```python
APPROVED_STRUCTURAL_DIFF_PATHS = {
    "schema_version",
    "estimand",
    "stability_audits",
    # old `stability_audit` migration path handled explicitly
    "rows[*].resampling[*].interval.zero_relation_full_precision",
    "rows[*].resampling[*].interval.touches_zero_at_lower_full_precision",
    "rows[*].resampling[*].interval.touches_zero_at_upper_full_precision",
}

compare_scientific_payload(old, new, approved_paths=...)
```

The comparator should report every unexpected path/value change and fail the integration test. Preserve the pre-change artifacts in test fixtures or a commit-pinned snapshot rather than relying on a moving branch.

## 14.4 Pitfall

A blanket “all numbers unchanged” assertion may incorrectly reject regenerated provenance hashes or derived schema fields. Conversely, ignoring entire subtrees could hide changed interval bounds. Use path-level approval.

---

# 15. Recommended verification command sequence

Run from repository root in a clean environment with the required development extras.

## 15.1 Fast structural and semantic checks

```bash
python tools/paper_a_transfer_artifacts.py --check
python tools/paper_a_transfer_text.py --check
python tools/paper_a_front_matter.py
python tools/paper_a_supplement.py
python tools/paper_a_consistency.py verify
```

At the reviewed baseline, `paper_a_supplement.py` uses its no-argument mode as the non-writing drift check and exits non-zero when the generated supplement is stale. Do not suppress that exit status.

## 15.2 Targeted tests

```bash
python -m pytest \
  tests/test_paper_a_transfer_semantics.py \
  tests/test_paper_a_transfer_contract.py \
  tests/test_paper_a_front_matter.py \
  tests/test_paper_a_submission_contract.py \
  tests/test_paper_a_figure_semantics.py \
  tests/test_paper_a_figure_layout.py \
  -q
```

## 15.3 Focused mutation selection

```bash
python -m pytest \
  tests/test_paper_a_transfer_semantics.py \
  tests/test_paper_a_transfer_contract.py \
  tests/test_paper_a_submission_contract.py \
  -k 'mutation or wrong_membership or refreshed_hash or audit_scope or endpoint_rows or contradiction' \
  -q
```

Test names should be chosen so this selector is reliable; otherwise retain an explicit test-node list.

## 15.4 Full suite

```bash
python -m pytest -q
```

## 15.5 Final slow reproducibility run

After the code is stable and before final sign-off:

```bash
python tools/paper_a_transfer_artifacts.py --recompute
```

If `--write` was already used to produce schema-v3 artifacts, `--recompute` should independently confirm the retained artifacts. Preserve stdout/stderr, exit code, environment lock/hash, and resulting artifact hashes.

## 15.6 Repository searches

```bash
rg -n -i \
  'same side of zero|reaches zero at its upper bound|largest advantage.*upper bound|moves neither.*magnitude|unresolved at the precision this resampling attains' \
  docs/PAPER_A_DRAFT.md docs/submission docs/figures/PAPER_A_CAPTIONS.md

rg -n -i \
  'earlier draft|round-[0-9]+|already in (the )?repo|`(?:docs|tools|tests|puckworks)/' \
  docs/PAPER_A_DRAFT.md docs/submission docs/figures/PAPER_A_CAPTIONS.md
```

Adjudicate matches by visibility and section. Expected active scientific-text matches: none, except legitimate paths in explicitly allowed availability sections.

## 15.7 Clean-tree and diff review

```bash
git status --short
git diff --check
git diff --stat
git diff -- docs/submission/PAPER_A_JFE_MANUSCRIPT.md \
             docs/submission/PAPER_A_JFE_SUPPLEMENT.md \
             docs/submission/PAPER_A_JFE_COVER_LETTER.md \
             docs/figures/PAPER_A_CAPTIONS.md
```

Review generated JSON with a semantic diff, not only a line diff.

---

# 16. Manual scientific review protocol

Automated checks are necessary but not sufficient for publication prose. Perform the following read-through after all generation is complete.

## 16.1 Principal-result continuity read

Read, in order:

1. abstract;
2. Methods description of the comparator range and audit;
3. endpoint Results paragraph;
4. Table 4a and note;
5. fitting-loss robustness paragraph;
6. conclusion;
7. cover-letter central-result paragraph;
8. Supplementary Table S3 and interpretation;
9. Supplementary Table S6.

For each, answer:

- What is the estimand?
- Which sign favours which model?
- Does the range contain or exclude zero at full precision?
- Is exact zero contact claimed?
- Which endpoint/scheme/loss does the MC audit cover?
- Is the numerical statement separated from inference?
- Are any words stronger than the artifact supports?

Every answer should be consistent without relying on repository knowledge.

## 16.2 Table audit

For Table 4a and S3:

- independently recompute relation labels from full-precision bounds;
- verify rounded values against the production formatter;
- verify 40 g is the only row with multi-seed MC precision under Path A;
- verify lower/upper MCSEs are not swapped;
- verify “not separately audited” does not imply missing canonical computation;
- confirm no footnote marker is orphaned after conversion/typesetting.

## 16.3 Figure audit

At final size and in grayscale:

- Figure 1 category encoding is decodable;
- legend exactly matches node borders;
- arrows retain dependency semantics;
- Figure S3 uses no hidden threshold categories;
- negative/positive correlations are read from direction, not colour;
- all titles, labels, and NA marks are visible.

## 16.4 Publication-process audit

Read the visible supplement captions and table notes, not only the manuscript. Confirm no reader-facing text says:

- earlier draft;
- review round/ticket;
- already in the repo;
- generated so it cannot disagree;
- internal path outside Availability.

---

# 17. Acceptance checklist by finding

## P0-1 — Interval semantics and favourability

- [ ] Shared full-precision trinary classifier exists.
- [ ] Exact zero contact is separate from display rounding.
- [ ] Estimand direction is explicit and validated.
- [ ] Both fitting-loss ranges render as containing zero.
- [ ] Most/least favourable bounds are derived from estimand direction.
- [ ] “Moves neither magnitude” wording is replaced with quantified/material wording.
- [ ] Cover letter and abstract factual clauses are generated from shared claims.
- [ ] Relation and direction mutation matrix passes.
- [ ] Active false-phrase scan is clean.

## P0-2 — Audit contradiction

- [ ] Audit has exact target identity.
- [ ] Seed extrema and stable flag reconcile.
- [ ] Abstract says the audited 40 g sign is numerically stable.
- [ ] S3 says the audited 40 g sign is numerically stable.
- [ ] Endpoint sensitivity is distinguished from MC variability.
- [ ] No-coverage/non-inferential qualification remains.
- [ ] Stable/unstable contradiction mutations fail.
- [ ] Abstract word count remains within the safety band.

## P1-1 — Audit scope

- [ ] Existing audit is explicitly scoped to 40 g / complete 132 / `cond_in_variety` / primary/default loss / MAPE score.
- [ ] Separate lower and upper MCSEs are used.
- [ ] 38 and 42 g are not assigned the 40 g MCSE.
- [ ] Secondary schemes and alternative loss are not assigned the 40 g MCSE.
- [ ] Exact-key lookup has no fallback.
- [ ] Target-leakage mutations fail.
- [ ] Three-decimal display is retained with numerical-resolution qualification.

## P1-2 — Endpoint rows

- [ ] Missing, null, non-list, and empty rows fail.
- [ ] Exactly 38/40/42 g rows are required in canonical order.
- [ ] Non-dict, keyless, non-numeric, boolean, NaN, and infinite targets fail.
- [ ] Duplicate, missing, and extra endpoints fail.
- [ ] Retired keys are checked in every row.
- [ ] Required result fields and schemes are validated.
- [ ] Artifact checker and routine `verify` both fail representative mutations.
- [ ] Malformed artifacts produce diagnostics rather than tracebacks.

## P1-3 — Source membership

- [ ] Independent oracle parses the CSV directly.
- [ ] Oracle does not call production grouping functions.
- [ ] Exact strata, cluster IDs, observation lists, sample IDs, and grinds are compared.
- [ ] Census values derive from oracle output.
- [ ] Refreshed-hash A12/A13 and A19/A20 mutations fail.
- [ ] Wrong stratum/key/pairing mutations fail.
- [ ] Diagnostics identify scheme and mismatched cluster/observations.
- [ ] Current artifact passes the source oracle.

## P2-1 — Process leakage

- [ ] All identified passages are rewritten as scientific prose.
- [ ] Canonical draft, supplement, and captions are scanned.
- [ ] Hidden HTML comments are excluded without shifting line numbers.
- [ ] Internal paths are allowed only in designated availability sections.
- [ ] New process-language patterns are tested on every surface.
- [ ] Scanner sandbox includes every production file.
- [ ] No active process-language match remains.

## P2-2 — Figure semantics

- [ ] Figure 1 style map is declared as semantic data.
- [ ] `insample` and `within` have distinct complete encodings.
- [ ] Duplicate encodings require an explicit alias declaration.
- [ ] S3 threshold colour logic is removed.
- [ ] S3 finite bars use a common neutral colour.
- [ ] Missing correlations display as NA.
- [ ] Captions explain the final encoding.
- [ ] Colour and grayscale final-size renders are approved.
- [ ] Existing dependency and layout tests remain green.

---

# 18. Risk register

| Risk | Likelihood without control | Consequence | Control/check |
|---|---|---|---|
| Prose fixed manually but generator restores error | High | P0 recurs | edit generator; exact generated-block checks |
| Relation derived from rounded bounds | Medium | false zero contact/side | full-precision typed classifier |
| Audit scope remains implicit | High | MCSE leaks again | exact `AuditKey`; schema v3; no fallback |
| Schema bump changes scientific numbers unnoticed | Medium | hidden numerical regression | path-level old/new payload comparison |
| Endpoint validator crashes on malformed row | Medium | poor diagnostics/CI ambiguity | defensive iteration and mutation tests |
| Source oracle shares production bug | High if code reused | false assurance | direct CSV parse and independent grouping branches |
| Hard-coded census passes wrong membership | High under current design | scientifically wrong resampling | exact normalized partition comparison |
| Process scanner becomes noisy | Medium | maintainers disable/ignore it | visible-text and section-aware scanning, precise regexes |
| Abstract exceeds venue limit | Medium | submission formatting failure | word-count test after generated clause |
| Corrected wording overclaims inference | Medium | new scientific defect | mandatory no-coverage claim object and read-through |
| Figure line style vanishes at final size | Medium | category ambiguity remains | final-size/grayscale human inspection |
| S3 NA is drawn as zero | Medium | false data | explicit finite mask and NA test |
| Generated output order is wrong | Medium | stale blocks or overwrite | documented generation dependency order and all checks |
| Slow write is repeated unnecessarily | Medium | wasted compute/time | fixtures first; one coordinated final `--write` |
| Current main has moved since reviewed commit | High | line references stale/conflicts | rebase carefully; preserve semantic acceptance tests rather than line-number assumptions |

---

# 19. Recommended commit/PR structure

Use one remediation PR with reviewable, green commits, or a tightly ordered stack. Suggested commits:

1. **`test: reproduce round-9 semantic and assurance failures`**  
   Add fixtures/mutations together with the minimal helper scaffolding needed to keep the commit green only if policy permits. Prefer not to merge a deliberately failing commit to shared main.
2. **`fix: type transfer interval and estimand semantics`**  
   Add `transfer_semantics.py`, relation/direction tests, and schema fields.
3. **`fix: scope and bind endpoint Monte Carlo audit`**  
   Add keyed audit, producer changes, exact lookup, and scoped rendering tests.
4. **`fix: harden endpoint rows and source-bind resampling membership`**  
   Add strict row validation, independent oracle, and refreshed-hash mutations.
5. **`fix: regenerate Paper 1 endpoint claims`**  
   Update transfer text, abstract placeholder, cover letter, manuscript, supplement, and package.
6. **`fix: remove publication-process leakage`**  
   Rewrite prose and expand scanner/tests.
7. **`fix: clarify Paper 1 figure encodings`**  
   Update Figure 1/S3 styles, captions, outputs, and tests.
8. **`chore: retain final Paper 1 Round 9 verification evidence`**  
   Add/update the appropriate verification record with commands, hashes, and results.

Every commit should state whether it changes scientific numbers. The expected answer for commits 2–7 is “no,” except the schema-v3 producer regeneration changes representation and hashes.

---

# 20. Final sign-off record template

Create a concise retained verification record after implementation, for example:

```markdown
# Paper 1 Round 9 remediation verification

- Implementation baseline: `<commit>`
- Final commit: `<commit>`
- Transfer schema: 3
- Working tree: clean / dirty
- Review findings closed: P0-1, P0-2, P1-1, P1-2, P1-3, P2-1, P2-2

## Artifact verification

- `paper_a_transfer_artifacts.py --check`: PASS
- `paper_a_transfer_artifacts.py --recompute`: PASS
- source-oracle exact membership: PASS for 4/4 schemes
- endpoint row mutation matrix: PASS
- audit target-leakage matrix: PASS
- semantic relation matrix: PASS

## Numerical invariance

- Pre-existing scientific numeric leaves changed unexpectedly: 0
- Approved schema/derived-field changes: `<list>`
- Endpoint artifact SHA-256: `<hash>`
- Comparator-loss artifact SHA-256: `<hash>`
- Corpus-contract artifact SHA-256: `<hash>`

## Publication outputs

- transfer text current: PASS
- front matter current: PASS
- supplement current: PASS
- consistency verify: PASS
- process-language scan: PASS
- retired false-phrase scan: PASS
- abstract word count: `<n>` / 250

## Figures

- Figure 1 semantic-style tests: PASS
- Figure S3 neutral-colour tests: PASS
- colour final-size inspection: PASS, reviewer `<name/date>`
- grayscale final-size inspection: PASS, reviewer `<name/date>`

## Tests

- targeted suite: `<n> passed`
- full suite: `<n> passed, n skipped>`

## Remaining submission blockers outside Round 9 remediation

- `<explicitly list only genuine remaining metadata/release matters>`
```

Do not state “ready for submission” merely because the seven findings are closed. Apply the repository's separate submission-readiness gate for metadata, release state, and known out-of-scope requirements.

---

# Appendix A — Suggested semantic helper skeleton

```python
"""Scientific semantics for Paper A transfer/comparator claims.

This module contains no Markdown layout, YAML, plotting, file IO, or slow producer calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Iterable


class ZeroRelation(str, Enum):
    BELOW_ZERO = "below_zero"
    CONTAINS_ZERO = "contains_zero"
    ABOVE_ZERO = "above_zero"


class FavourDirection(str, Enum):
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


@dataclass(frozen=True)
class IntervalSemantics:
    lower: float
    upper: float
    zero_relation: ZeroRelation
    touches_zero_at_lower: bool
    touches_zero_at_upper: bool


@dataclass(frozen=True)
class EstimandSpec:
    id: str
    label: str
    favour_direction: FavourDirection


MODEL_MINUS_COMPARATOR_LOSS = EstimandSpec(
    id="model_minus_comparator_loss_pp",
    label="model loss minus comparator loss",
    favour_direction=FavourDirection.LOWER_IS_BETTER,
)


def _finite_number(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real numeric value, got {type(value).__name__}")
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite, got {out!r}")
    return 0.0 if out == 0.0 else out


def classify_interval(lower: object, upper: object) -> IntervalSemantics:
    lo = _finite_number(lower, name="lower")
    hi = _finite_number(upper, name="upper")
    if lo > hi:
        raise ValueError(f"lower bound {lo!r} exceeds upper bound {hi!r}")
    if hi < 0.0:
        relation = ZeroRelation.BELOW_ZERO
    elif lo > 0.0:
        relation = ZeroRelation.ABOVE_ZERO
    else:
        relation = ZeroRelation.CONTAINS_ZERO
    return IntervalSemantics(
        lower=lo,
        upper=hi,
        zero_relation=relation,
        touches_zero_at_lower=(lo == 0.0),
        touches_zero_at_upper=(hi == 0.0),
    )


def relation_phrase(relation: ZeroRelation) -> str:
    return {
        ZeroRelation.BELOW_ZERO: "excluded zero on the negative side",
        ZeroRelation.CONTAINS_ZERO: "contained zero",
        ZeroRelation.ABOVE_ZERO: "excluded zero on the positive side",
    }[relation]


def most_favourable_interval_extreme(
    intervals: Iterable[tuple[str, IntervalSemantics]],
    estimand: EstimandSpec,
) -> tuple[str, float]:
    values = list(intervals)
    if not values:
        raise ValueError("at least one interval is required")
    if estimand.favour_direction is FavourDirection.LOWER_IS_BETTER:
        return min(((label, interval.lower) for label, interval in values), key=lambda x: x[1])
    return max(((label, interval.upper) for label, interval in values), key=lambda x: x[1])


def least_favourable_interval_extreme(
    intervals: Iterable[tuple[str, IntervalSemantics]],
    estimand: EstimandSpec,
) -> tuple[str, float]:
    values = list(intervals)
    if not values:
        raise ValueError("at least one interval is required")
    if estimand.favour_direction is FavourDirection.LOWER_IS_BETTER:
        return max(((label, interval.upper) for label, interval in values), key=lambda x: x[1])
    return min(((label, interval.lower) for label, interval in values), key=lambda x: x[1])
```

The production implementation should add audit-key types and validation, but keep this separation of scientific meaning from display formatting.

---

# Appendix B — Suggested exact source-oracle pseudocode

```python
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

SOLUTES = ("caffeine", "trigonelline", "5CQA")
HELD_OUT_GRINDS = {"C", "F"}


def read_source_observations(csv_path: Path) -> list[dict]:
    lines = [line for line in csv_path.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    rows = list(csv.DictReader(lines))
    source = []
    seen_samples = set()
    for row in rows:
        if row["granulometry"] not in HELD_OUT_GRINDS:
            continue
        sample = row["sample"].strip()
        if sample in seen_samples:
            raise ValueError(f"duplicate held-out sample ID {sample!r}")
        seen_samples.add(sample)
        base = {
            "sample_id": sample,
            "variety": row["variety"].strip(),
            "grind": row["granulometry"].strip(),
            "temperature_degC": float(row["T_degC"]),
            "pressure_bar": float(row["p_bar"]),
            "on_grid": row["on_grid"].strip().lower() == "true",
        }
        for solute in SOLUTES:
            source.append({
                **base,
                "solute": solute,
                "observation_id": f"{sample}|{solute}",
            })
    if len(seen_samples) != 44 or len(source) != 132:
        raise ValueError(
            f"source census is {len(seen_samples)} samples/{len(source)} observations; expected 44/132"
        )
    return source


def build_scheme(observations: list[dict], scheme: str) -> dict:
    grouped = defaultdict(list)
    for obs in observations:
        if scheme == "cond_in_variety":
            stratum = obs["variety"]
            cluster = f"{obs['variety']}|{fmt(obs['temperature_degC'])}|{fmt(obs['pressure_bar'])}"
        elif scheme == "sample_in_variety_grind":
            stratum = f"{obs['variety']}|{obs['grind']}"
            cluster = obs["sample_id"]
        elif scheme == "cond_in_group":
            stratum = f"{obs['variety']}|{obs['solute']}"
            cluster = (
                f"{obs['variety']}|{obs['solute']}|"
                f"{fmt(obs['temperature_degC'])}|{fmt(obs['pressure_bar'])}"
            )
        elif scheme == "group":
            stratum = ""
            cluster = f"{obs['variety']}|{obs['solute']}"
        else:
            raise ValueError(f"unknown scheme {scheme!r}")
        grouped[(stratum, cluster)].append(obs)
    return canonicalize(grouped, scheme=scheme)
```

The actual oracle should include complete metadata and diagnostics, but must retain the independent explicit branching.

---

# Appendix C — Exact replacement prose set

These sentences are recommendations, not a license to bypass generator binding.

## C.1 Fitting-loss robustness

> Refitting both the mechanistic model and the level-only comparator under the alternative log/relative-error level fit changed the paired model-minus-comparator difference from **−0.394 pp** to **−0.393 pp**. The corresponding primary clustered percentile sensitivity ranges were **[−0.829, +0.004] pp** and **[−0.826, +0.004] pp**; both contained zero at full precision. The fitting loss therefore did not materially change the point estimate, the zero-containment classification, or the practical reading. These descriptive ranges have no calibrated coverage interpretation.

## C.2 Endpoint sweep

> Across the 38–42 g endpoint sweep, the paired difference remained between **−0.447 and −0.394 pp**. The primary range excluded zero on the negative side at 38 g and contained zero at 40 and 42 g. Across endpoints, the most favourable lower bound was **−0.891 pp** and the least favourable upper bound was **+0.006 pp**; negative values favour the mechanistic model.

## C.3 Audit scope

> The retained multi-seed Monte Carlo audit applies only to the **40 g**, complete-corpus, primary `cond_in_variety` range under the primary/default fitting loss. At the canonical draw count, the lower- and upper-bound Monte Carlo standard errors were approximately **0.000520** and **0.000466 pp**, respectively, and all 20 audited upper bounds were positive. This establishes numerical sign stability for that bound, not calibrated coverage or an inferential conclusion.

## C.4 Abstract tail

> Across 38–42 g, the difference remained **−0.447 to −0.394 pp**; the audited 40 g upper-bound sign was numerically stable, while zero containment changed with endpoint and carried no calibrated inferential meaning.

## C.5 Conclusion/cover letter

> The mechanistic model's complete-corpus error was close to that of the trained level-only comparator: the paired difference was **−0.394 percentage points**, and its primary clustered percentile sensitivity range **[−0.829, +0.004] pp contained zero**. Acceptable endpoint accuracy therefore did not establish resolvable incremental mechanistic skill.

## C.6 S6 caption

> The four resampling schemes use the same 132 held-out observations but impose different dependence units and strata. The pre-declared primary `cond_in_variety` scheme preserves condition-level dependence within variety; the three secondary schemes show sensitivity to alternative defensible dependence assumptions.

## C.7 Figure S3 caption addition

> In panel (b), all finite correlations use a common neutral bar colour; signed bar direction and length carry the information. No colour threshold, significance class, or inferential category is applied.

---

# Appendix D — Definition of done

The Round 9 remediation is complete only when all of the following are true simultaneously:

1. **Scientific text:** every central result sentence is true under full-precision interval geometry, explicit estimand direction, and exact audit scope.
2. **Artifacts:** schema-v3 artifacts are producer-generated, source-bound, strictly validated, and numerically unchanged except for approved representation changes.
3. **False-green closure:** every endpoint-row and wrong-membership mutation demonstrated in Round 9 now fails, including after self-hash refresh.
4. **Publication consistency:** manuscript, canonical draft, supplement, package, abstract, cover letter, highlights, and captions are current and process-language clean.
5. **Figures:** the final visual encodings are explicit, testable, and legible in colour and grayscale.
6. **Verification:** targeted tests, full tests, artifact checks, recomputation, searches, clean-tree checks, and human scientific read-through are retained as evidence.
7. **Scope discipline:** no out-of-scope submission-readiness issue is silently claimed closed by this work.

A passing test suite without the manual semantic read and figure inspection is insufficient. Conversely, correct-looking prose without the mutation tests and source oracle is insufficient. Closure requires both.
