# Paper 3 — Puckworks: an executable, provenance-aware evidence registry

*Fork scaffold created 2026-07-14 per `PUBLICATION_STRATEGY_REVIEW.md` §4. This folder is
the **resource-paper home** (§14.3): planning + the RSM/evidence-governance demonstration
material that is no longer a physics headline in the narrow Paper B. Claim ownership is in
`../CLAIM_OWNERSHIP.md`. No analysis code is moved — the whole point is that Puckworks is
the shared registry the other papers draw from.*

**Title (preferred):** *Puckworks: an executable, provenance-aware evidence registry for
espresso process models.* (Alts: *An executable review of espresso process models:
observables, evidence, and discriminating experiments*; *Typed observable contracts and
evidence-aware comparison for coupled food-process models.*)

**Primary contribution (§4.3):** Published espresso models use differing state
definitions, parameter conventions, observables, windows, and evidence standards.
Puckworks represents them as **provenance-tracked components with typed interfaces and
explicit evidence labels**, enabling matched-observable comparison **without silently
merging incompatible quantities**.

## Contents (§4.5)

1. **Corpus & inclusion criteria** — indexed literature search (databases, terms, dates,
   inclusion/exclusion, eligible model/data classes, duplicate handling). *NOT called
   systematic until the search protocol is complete — PI-owned; see `PAPER_B_RELATED_WORK.md`.*
2. **Process-stage taxonomy** — machine/BC → infiltration → packing/geometry → porous
   flow → bed evolution → extraction/transport → observables. Distinguish
   calibration-only / runtime / observational-adapter / diagnostic-exploratory components.
3. **Typed contract architecture** — state vars, units, coordinates, pressure locations,
   concentration + inventory + saturation semantics, missing-data behaviour, rules against
   silent field repurposing (`contracts.py`).
4. **Evidence taxonomy** — code verification · source-curve reproduction · post-fit
   reconstruction · within-campaign held-out prediction · independent external · qualitative
   capacity · sign/compatibility · exploratory synthesis · proposed experiment (ROADMAP §0).
5. **Reproducibility architecture** — model/source cards, data manifests, frozen result
   bundles, claim registries, figure source-data exports, clean release manifests, strict
   verification, artifact hashing.
6. **Demonstration 1 — observable/unit linting** — a mixed-unit / mismatched-observable
   episode (c_sat 170/212/224; pressure-node identity; TDS-proxy vs named solutes) shows an
   invalid result looking plausible until the contract is corrected. *Methodological, not
   autobiographical.*
7. **Demonstration 2 — null-first model comparison** — the temporal flow ladder as a
   **method** (machine null / static null / temporal candidate / flexible null / experiment
   selection). Science cited to Paper B2.
8. **Demonstration 3 — more physics can worsen a reconstruction** — the failed
   extraction+swelling composition: added mechanisms are not automatically explanatory;
   component validity ≠ composition validity; negative results preserved.
9. **Experiment-design output** — incompatible model predictions → recommended
   measurements (fractions, pressure steps, reversals, rebrew, spatial end states,
   control-mode, first-drop).
10. **End-to-end named-shot scorecard** — one named configuration (PV-19) with every stage
    labelled observed / calibrated / verified / reconstructed / independently tested /
    extrapolated / open. *Transparent evidentiary accounting, NOT a "digital twin".*

## Software / resource readiness before submission (§4.6)

Stable versioned public API; install instructions; tutorials; a no-private-files example;
documented "add a model/dataset" path; automated quick tests; separated slow benchmarks;
code+data licensing; clean archived release + DOI; contribution guidelines; issue
templates; changelog + semver; corpus-search protocol; ≥1 external reproduction/user;
explicit verified/calibrated/exploratory component labels; strict clean-build checks.

**Venue routes:** executable-review / methods journal; software journal (JOSS — subject to
feature-completeness, docs, testing, open-development history, community contribution;
<https://joss.theoj.org/about>); SoftwareX; or a domain methods venue.

## Demonstration material that lives here (recut from the broad `PAPER_B_DRAFT.md`)

- Schmieder RSM / grind-response audit (current Paper B Result 1) — resource demo / context.
- Broad mechanism evidence matrix (current Paper B Fig 2) — the evidence-taxonomy figure.
- The extraction+swelling composition failure (current Paper B Fig 4) — Demonstration 3.
