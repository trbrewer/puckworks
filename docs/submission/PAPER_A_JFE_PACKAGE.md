# Paper A — Journal of Food Engineering submission package

**Conversion status:** venue-selected working package. *Journal of Food Engineering* is the repository’s recommended first journal. The abstract, keywords, highlights, figure-caption file, declarations scaffold, and conversion map are complete. Author metadata, the licensed/indexed novelty search, final weighted-uncertainty reruns, and a clean typeset source remain PI actions.

## Venue limits checked on 2026-07-13

- Abstract: no more than 250 words. This draft is **237 words**.
- Keywords: 1–7. This draft has **7**.
- Highlights: 3–5 bullets, each no more than 85 characters including spaces. Counts appear below.
- Editable manuscript source is required; PDF alone is not an acceptable source.
- Vector drawings should be EPS or PDF with fonts embedded or text converted to graphics.
- Captions are supplied separately and must explain symbols and abbreviations.
- A research-data deposit/link or an explicit reason data cannot be shared is required.

Canonical guide: <https://www.sciencedirect.com/journal/journal-of-food-engineering/publish/guide-for-authors>

## Proposed article type

Research paper / original research article. Confirm the exact Editorial Manager label at upload.

## Proposed title

**Whole-cup measurements can obscure kinetic parameter localization in espresso extraction models**

## Authors and affiliations

> [Insert author names in submission order, affiliations, ORCID identifiers, and corresponding-author email.]

## Abstract (237 words)

Mechanistic food-process models can match integrated product measurements while leaving internal rates weakly constrained. We tested this risk in a multi-solute espresso extraction model calibrated previously to fraction-resolved kinetics and refitted to an independent endpoint campaign. Model output was mapped to the same 40 mL beverage endpoint as the observations. For each solute, a solid-inventory level and a Sherwood mass-transfer rate multiplier were estimated and profiled. The unweighted concentration-scale objective was highly ill-conditioned, and its 10%-above-minimum profile extended from about 0.4 to the upper tested rate boundary, showing strong inventory–rate compensation rather than a uniquely localized rate. A calibration frozen on the optimal grind produced coarse/fine held-out errors of approximately 3–18%, but its pooled mean absolute percentage error was 8.2% versus 8.6% for an optimal-grind level-only constant and it was worse on 50 of 108 held-out points. Thus, acceptable endpoint error added little skill beyond a transferred concentration level. A shared inventory–rate pair reconstructed all grinds with a modest in-sample sharing penalty, but this did not constitute predictive transfer. Fraction-resolved source-campaign data moved the rate objective more strongly than a whole-cup aggregate. An independent second-rig dissolved-solids trajectory also produced a rate minimum, although it was shallow and high-error, whereas the corresponding single-cup objective was algebraically flat after profiling its level. Matching the observation window is therefore necessary but not sufficient: parameter localization, endpoint accuracy, cross-condition prediction, and incremental skill over a null model should be reported separately.

## Keywords

espresso; extraction kinetics; practical identifiability; profile objective; model transfer; experimental design; porous media

## Highlights

- Whole-cup fits leave a broad inventory–kinetics compensation profile **[68 characters]**
- Held-out error adds little skill over an optimal-grind constant baseline **[72 characters]**
- Fraction-resolved observations localize the kinetic rate more strongly **[70 characters]**
- Prediction, localization, benchmark skill, and transfer are kept distinct **[73 characters]**
- All headline values are tied to machine-readable result bundles **[63 characters]**

## Editor-facing significance paragraph

Whole-cup measurements are common in food-process model calibration because they are economical and directly relevant to product quality. This study shows that an apparently accurate integrated endpoint can leave a kinetic rate weakly localized through compensation with extractable inventory. It also demonstrates a practical reporting workflow that separates parameter localization from held-out prediction and from incremental skill over a trained null. The result is directly relevant to experimental design for extraction, leaching, dissolution, and other food processes in which integrated product measurements can conceal internal transport-rate uncertainty.

## Proposed files

| submission item | repository source | action |
|---|---|---|
| main manuscript | `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` | convert to editable `.docx` or Elsevier `elsarticle` `.tex`; remove editorial notes |
| highlights | `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt` | upload as separate editable file |
| figure captions | `docs/figures/PAPER_A_CAPTIONS.md` | upload as separate caption file |
| figures | generated `fig1_design` through `fig8_residuals_vs_conditions` | upload PDF vector siblings; retain PNG for review |
| source data | generated `docs/figures/paper_a/source_data/` | include in repository release and data DOI |
| code/results | frozen Paper A release archive | cite release DOI and commit/tag |
| bibliography | `docs/literature_search/references.bib` | run final cross-reference audit |

## Required declarations scaffold

### CRediT authorship

> [Author initials]: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing – original draft, Writing – review and editing.
>
> [Edit roles author by author; do not retain roles that were not performed.]

### Funding

> This work was supported by [funder, grant number]. / This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

### Declaration of competing interest

> The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### Data availability

> The source datasets are cited in the manuscript. Analysis code, machine-readable result bundles, source data behind the figures, environment specification, and release provenance are available at [repository release DOI]. Data not redistributed because of third-party terms are identified by source DOI with acquisition instructions.

### Generative-AI declaration

> During manuscript preparation, the authors used [tool and purpose, or “no generative-AI or AI-assisted tools”]. The authors reviewed and edited all output and take full responsibility for the article. Confirm the journal’s current wording in Editorial Manager. No generative AI was used to create or alter scientific figures.

## Conversion edits before upload

1. Resolve the licensed Scopus/Web of Science search and replace provisional novelty wording with the archived search result.
2. Complete replicate/measurement-uncertainty sensitivity reruns; update figures, bundle values, abstract, and discussion only if conclusions change.
3. Remove all roadmap/review-ticket language and repository-development commentary from the manuscript body.
4. Collapse the present long Results/Discussion prose by moving audit details to supplementary methods and tables.
5. Use SI units or provide SI equivalents for coffee-specific units.
6. Cite every figure/table in order; move captions to the separate caption file.
7. Ensure the title, abstract, highlights, cover letter, manuscript, and release bundle use the same evidence-tier wording.
8. Deposit the frozen release archive, assign its DOI, and replace all bracketed placeholders.

## Suggested cover-letter core

> Dear Editor,
>
> We submit “Whole-cup measurements can obscure kinetic parameter localization in espresso extraction models” for consideration as an original research article in *Journal of Food Engineering*. The study addresses a common process-engineering inference problem: an integrated product measurement can be predicted accurately while a kinetic parameter remains weakly localized because it compensates with material inventory. Using matched observation operators, parameter profiling, within-campaign holdouts, a trained null benchmark, and an independent time-resolved campaign, we show why endpoint agreement, parameter localization, transfer, and incremental predictive skill must be evaluated separately. The contribution is an applied food-engineering case study and reproducible analysis workflow, not a claim of a new general identifiability method. The manuscript is not under consideration elsewhere, and all authors have approved its submission [confirm before use].
>
> Sincerely,
> [Corresponding author]
