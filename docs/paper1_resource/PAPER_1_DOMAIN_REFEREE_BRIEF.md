# Paper 1 — domain referee brief

**This is not review round 13.** It is a different kind of review, and the difference is the point.

**Manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
**Supplement:** `docs/submission/PAPER_A_JFE_SUPPLEMENT.md` + `docs/submission/figures/`
**Captions:** `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` (standalone)
**Target venue:** *Journal of Food Engineering*

We are asking you to read this as a **food-engineering referee reading a paper**, not as an auditor
reading a repository.

---

## 1. Why we are asking for something different

Twelve review rounds have examined this manuscript. They were rigorous and they found real defects.
But rounds 10, 11 and 12 converged on one layer — how the paper *words* its central claim, and
whether the machinery that polices that wording has holes — and they reached diminishing returns:

- rounds 11 and 12 added ~4,800 lines of assurance code and **zero** lines of science;
- each round found defects in the *previous round's* gates, a self-sustaining process;
- the largest new mechanism (822 lines binding inferential permission to hashed evidence) guards a
  procedure registry with **zero entries**, because this analysis makes no inferential decision;
- three consecutive rounds reported "stale-number category: empty" — which means the numbers are
  *internally consistent*, i.e. copied correctly from artefact to manuscript to caption. It has
  never meant they are *right*.

The last reviewer also could not run the test suite or regenerate the science — no working checkout
— so the review was necessarily source inspection plus text probes.

**What has never been reviewed is whether the paper is good science.** That is what we want from
you.

## 2. What we have already verified, so you do not spend time on it

| Verified | How |
|---|---|
| Every reported number traces to an archived producer run | `paper_a_numerical_invariants.py`, exact, no tolerance |
| The manuscript, supplement, cover letter, Highlights and captions agree numerically | 0 unaccounted numerals in both manuscripts |
| **The source transcription is correct** | 726 analyte cells and 66 condition rows compared against the article PDF (SHA-256 pinned): **0 mismatches**. See `ANGELONI_TRANSCRIPTION_AUDIT.md` addendum |
| The 44-record / 132-observation corpus is what the source implies | Independent oracle sharing no membership code with production |
| Claim wording carries symmetric non-establishment on all 9 load-bearing surfaces | `claim_policy.SURFACE_ASSERTIONS` |

**Please do not re-report** wording preferences that do not violate the symmetric-non-establishment
criterion, defects in the assurance gates themselves, or missing author metadata / DOI / novelty
search (all known and tracked).

## 3. What we actually want you to judge

### (a) Is the comparator fair? — the highest-value question

The paper's central result is that a mechanistic model achieves **8.44 %** pooled held-out MAPE
against **8.83 %** for an "O-trained level-only constant": one concentration level fitted on the
optimal grind, with no temperature, pressure, flow or kinetic response.

- Is a single fitted constant the **right null** for this claim, or is it a straw comparator that
  makes the mechanistic model look better than a fair baseline would?
- A stronger baseline (per-grind constant, a simple empirical regression on T and p, a
  nearest-condition lookup) might close or reverse the 0.394-point gap. The paper reports an
  in-sample ladder including per-grind constants, and a same-(T,p) lookup comparator on the
  matched-grid subset — **are those the right alternatives, and are they given fair prominence?**
- Conversely: is the comparator *too* strong, making the mechanistic model look worse than it is?

If the comparator is wrong, the headline result is wrong, and no amount of careful wording fixes it.

### (b) Is the corpus the right one?

- The headline uses the **complete 132-observation** coarse/fine corpus including 8 off-grid
  records; a 108-observation matched-grid subset is secondary. Round 7 changed this. Is the complete
  corpus the right primary, or does including conditions with no same-(T,p) optimal-grind counterpart
  make the comparison inhomogeneous?
- Three named solutes (caffeine, trigonelline, 5-CQA) out of eleven measured species. Is that
  selection defensible, or does it invite a selection concern?
- 44 records is small. Is the clustered-percentile sensitivity range the right uncertainty
  treatment, or would you expect something else at this n?

### (c) Does the conclusion follow from the evidence?

The paper claims four properties **dissociate**: parameter identifiability, endpoint accuracy,
predictive skill over a benchmark, and cross-grind transferability.

- Does the evidence actually establish dissociation, or only that all four were measured?
- The paper says an uncalibrated range establishes neither a reproducible/useful advantage nor its
  absence. Is that the correct scientific reading of a fixed-predictor clustered percentile range —
  or is it over-cautious to the point of saying nothing?
- **Is the paper's real contribution the espresso result, or the reporting protocol?** It currently
  claims both. If the protocol is the contribution, is a single worked example enough?

### (d) The physics and the numerics

- The extraction model is a 1-D convection-dominated two-grain balance (Pannusch et al. 2024,
  extending Moroney et al.). Are the constitutive assumptions defensible for espresso at these
  conditions?
- Reynolds is computed from the **superficial** velocity; the source's `flow` column is consumed as
  **mass** flow in g/s while labelled mL/s, making the endpoint a collected mass of 38/40/42 **g**.
  Both are settled against the source and archived — but are they *physically* right?
- The PDE discretisation convergence study is archived (`PAPER_A_NUMERICAL_CONVERGENCE.json`). Is
  the convergence evidence adequate for the claims that rest on it?
- The pressure→flow map is a Darcy refinement `q ~ p/μ(T)` with a single physical anchor, not fitted
  to concentrations. Is that defensible, and is the reported ≤0.6 pp sensitivity to it convincing?

### (e) Would you accept this at JFE?

Plainly: accept, minor, major, or reject — and the single change that would most improve it.

## 4. If you want to run it

```bash
pip install -e ".[dev]"
python tools/paper_a_transfer_artifacts.py --write     # ~26 min, regenerates the science
python -m pytest -q                                    # ~15 min
python tools/audit_angeloni_bioactives.py              # source transcription vs the article PDF
```

## 5. Known open items — please do not re-report

1. Author metadata, CRediT, funding, competing interests, AI declaration — not yet supplied.
2. Licensed indexed novelty search — not yet run.
3. Release DOI and archival tag — not yet minted.
4. The fraction-versus-measured-cup rate-profile contrast — data supports it, analysis owed.
5. The **calibrated named-solute uncertainty interval is blocked**: Tables 4–5 publish only global
   RSD ranges, so a solute-specific weighted refit needs a replicate drop from the Angeloni authors.
   The analysis is scoped as a descriptive sensitivity study and says so.
6. Supplementary Table S7 has not been proofed at journal width.
7. `docs/ANALYSIS_transfer.md`, `docs/PUBLIC_VALUE.md` and the public site carry older phrasing —
   repository/product copy, not submission surfaces.

## 6. Format

Findings as **major / minor / editorial**, each with the evidence relied on. Where you say a
scientific choice is wrong, say what you would have done instead.

**If a section is clean, say so.** After twelve rounds we can no longer distinguish "checked and
sound" from "not reached", and that distinction is now the most useful thing you can give us.

And if you think the paper is fine and we have been polishing it past the point of value — say that
too. It is a live hypothesis on our side.
