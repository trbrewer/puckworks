# Paper A — documented scoping search protocol (M9)

**This is a documented systematic *scoping* search, NOT a PRISMA-complete
systematic review.** A web/publisher search identifies strong prior art but cannot
establish exhaustive absence. The manuscript therefore says *"to our knowledge,
following a documented scoping search,"* and does **not** assert categorical
priority. Seeded from `docs/PAPER_A_M9_external_dataset_and_decisions_handoff.md` §1.

## Research questions
1. How do prior studies distinguish structural and practical identifiability?
2. Which methods are recommended for nonlinear practical-identifiability assessment?
3. How are sloppiness, model manifolds, and compensating parameters related to identifiability?
4. What confounding patterns are reported in reaction, transport, mass-transfer, dissolution models?
5. Which experimental designs improve kinetic-parameter identification?
6. What is known about endpoint/integral vs time-resolved observation designs?
7. Which coffee studies use fractions, inventories, named solutes, TDS, multiple grinds/PSDs, or cross-condition fits?
8. Has an espresso study already made the same specific inventory–rate identifiability and transfer claim?

## Sources (to search + archive at submission)
Scopus · Web of Science Core Collection · Crossref/DOI + publisher pages ·
PubMed/PLOS where relevant · institutional repositories/theses · backward +
forward citation snowballing · Zenodo/Mendeley Data · GitHub (code/data provenance
only, never sole bibliographic source).

## Search strings (title/abstract/keyword where supported)
```text
1. ("structural identifiability" OR "practical identifiability") AND (ODE OR PDE OR "mechanistic model")
2. "profile likelihood" AND identifiability
3. (sloppiness OR "model manifold" OR "compensating parameter*" OR "parameter confounding") AND identifiability
4. identifiability AND ("reaction-advection-diffusion" OR "reactive transport" OR dissolution OR "mass transfer" OR "packed bed")
5. ("optimal experimental design" OR OED) AND (kinetic OR "parameter estimation" OR identifiability)
6. (endpoint OR integral OR cumulative OR "time-resolved" OR fraction*) AND (identifiability OR "parameter estimation")
7. (espresso OR "coffee extraction") AND ("time-resolved" OR fraction* OR caffeine OR trigonelline OR chlorogenic OR "5-CQA" OR TDS OR model*)
8. ("coffee extraction") AND (inventory OR "initial concentration" OR multi-grind OR "particle size distribution" OR transfer OR identifiability)
```

## Screening rules
**Include** if it contributes ≥1 of: a structural/practical-identifiability
definition or method; profile likelihood or nonlinear uncertainty;
sloppiness/manifold/compensation theory; identifiability in a reaction/transport/
dissolution/packed-bed model; experimental design for kinetic identification;
empirical or modelled coffee extraction with time resolution, fractions, named
solutes, TDS, inventories, or multiple PSDs/grinds.

**Exclude:** purely sensory coffee studies with no extraction/model relevance;
papers using "identification" only as classification; generic optimization with no
parameter-identification content; coffee-chemistry papers with only one final-cup
measurement (unless needed for analyte-definition context); duplicate conference
abstracts when a full paper exists.

## Files in this directory
- `SEARCH_PROTOCOL.md` (this file)
- `references.bib` — the verified core references (methods + coffee lineage)
- `EVIDENCE_MATRIX.csv` — one row per screened record (header seeded; populate at submission)
- `SEARCH_LOG.csv`, `SCREENING.csv` — created when the databases are queried at submission
- `README.md`

## Submission gate (M9 complete only when)
- [ ] exact search dates, databases, fields, and query strings archived
- [ ] RIS/BibTeX/CSV exports retained; duplicates removed
- [ ] title/abstract + full-text screening recorded, with exclusion reasons
- [ ] backward + forward snowballing documented
- [ ] novelty wording checked against the final included set
- [ ] manuscript says "to our knowledge, following a documented scoping search"
- [ ] source list and manuscript bibliography agree; no unverified placeholder citation
