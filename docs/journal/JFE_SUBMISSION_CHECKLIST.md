# Journal of Food Engineering — Paper A submission checklist

**Target (handoff §3.1): Journal of Food Engineering (JFE).** Best fit for the actual
contribution — a food-engineering mechanism/observation problem, a mechanistic model,
experimental-data integration, validation/transfer, and quantitative implications for
how extraction experiments should be designed. *Not* Chemometrics & Intelligent Lab
Systems (needs a NEW general method, not an application) or Transport in Porous Media
(needs a new general porous-media transport result).
Guide: <https://www.sciencedirect.com/journal/journal-of-food-engineering/publish/guide-for-authors>

Encode every requirement as a checked **release gate**, not memory.

## JFE format requirements (verify against the live guide before submission)
- [ ] Abstract ≤ 250 words.
- [ ] 1–7 keywords.
- [ ] 3–5 highlights, each ≤ 85 characters incl. spaces (write these only AFTER final results are frozen).
- [ ] Quantitative, substantiated claims; clear mechanism; replicable methods.
- [ ] Validated mathematical model; SI units; separate legible figures.
- [ ] Data Availability statement.
- [ ] Code Availability statement.
- [ ] CRediT contributor roles.
- [ ] Standard research-integrity declarations (competing interests, funding).

## Terminology (handoff §4 — bound into the manuscript)
- [ ] "practical identifiability" (design/domain/objective-bounded), never "structural" without a proof.
- [ ] "profiled MAPE objective" / "profiled objective surface", never "profile likelihood".
- [ ] Evidence terms: calibration/reconstruction · internal holdout/prediction · external / cross-dataset prediction · failed external prediction · in-sample verification / objective localization. **No "negative validation".**
- [ ] TDS/TS = "aggregate-solids proxy", never a fourth named solute.
- [ ] "no satisfactory shared calibration was found over the tested parameter domain" (not "no shared calibration exists").
- [ ] Novelty stated as "to our knowledge, following a documented scoping search" — case study + model/data observation, NOT a new general method.

## Scientific content gates (must be true before submission)
- [ ] Matched-beverage-mass endpoint used everywhere (B1). ✅ done
- [ ] Named-solute headline; TDS reported separately (M5). ✅ done
- [ ] Exact weighted-median level; rate profiled over a stated grid (B3/B6). ✅ done
- [ ] Uncertainty: leave-one-condition-out CV + shot-level bootstrap + loss sensitivity (M4/M6). ✅ done
- [ ] Geometry sensitivity across the fitted grinds (B5). ✅ done
- [ ] §6: in-sample verification + independent external TDS test (Waszkiewicz 2026), interval flow-weighted operator, declared time-offset sensitivity, no first-bin imputation.
- [ ] Six figures generated from machine-readable outputs (no hand-typed numbers).
- [ ] Related-work scoping search archived; DB search executed at submission (M9).
- [ ] Abstract/highlights written from the FINAL frozen results.
- [ ] Reproducibility snapshot `paper-a-v1.0.0` created + archived (see `docs/reproducibility/PAPER_A_RELEASE_CHECKLIST.md`).
