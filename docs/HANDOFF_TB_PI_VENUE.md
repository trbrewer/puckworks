# Handoff — TB / PI / VENUE tasks (Paper A + Paper B)

Durable, actionable record of the review actions that **cannot be completed
in-repo by a Claude Code session** and are owned by a human: **TB** (Tim —
infrastructure, experiments, correspondence), **PI** (systematic literature /
novelty search — licensed database access), **VENUE** (journal manuscript
conversion — depends on the chosen target journal).

Source reviews: `docs/PAPER_A_FOURTH_DETAILED_REVIEW.md`,
`docs/PAPER_B_FIFTH_DETAILED_REVIEW.md`. The *definite unblocked* defects from both
are already actioned (ROADMAP §7.1, 2026-07-13); the classified remainder lives in
`docs/REVIEW_BACKLOG.md`. This file expands only the human-owned items.

Legend for "handoff line": what a CC session can pick up once the human step is
done — so work can be delegated back.

---

## TB — infrastructure, experiments, correspondence

### TB-1 · Frozen release tags + pinned environment
- **IDs:** A4-15, B5-01, B5-02, A-AR14/MAJ20, B-release
- **What:** cut `paper-a-v1.0.0` and `paper-b-v1.0.0` on a clean tree where
  manuscript, code, input data, result bundle, source-data exports, and all
  figures resolve to ONE commit; add a lockfile (`uv.lock` / `poetry.lock` or a
  container digest) recording Python + numpy/scipy/matplotlib versions.
- **Acceptance (review):** a fresh environment reproduces every table/figure and
  the exact result hashes within declared deterministic tolerances; the release
  build exits zero only when the tree is clean and `HEAD == manifest.source_commit
  == bundle.source_commit`.
- **Already built:** both `puckworks/paper_{a,b}/build.py` expose a strict
  `release` command that fails on a dirty/stale tree and records
  `release_fresh` / `bundle_matches_head` in the manifest. Run
  `python -m puckworks.paper_a.build release` and the Paper B equivalent
  immediately before tagging — each must exit 0.
- **Note (chicken-and-egg):** recomputing stamps the bundle with the current HEAD,
  but committing the bundle advances HEAD, so a committed bundle reads "one commit
  stale". This only matters at the tag cut; the routine (non-strict) verify stays
  green day-to-day.
- **First step:** recompute both bundles on a clean checkout
  (`build full` — Paper B ≈1 min, Paper A ≈25–30 min of PDE solves), commit, then
  `build release`, then tag + archive (e.g. Zenodo DOI).
- **Handoff line:** *CC can do the recompute (Paper B foreground, Paper A
  backgrounded) and generate the lockfile on request; the tag + DOI are yours.*

### TB-2 · Replicate-level measurement uncertainty
- **IDs:** A4-25 / §10.11, A-MAJ22, A2-08, B5-16, B5-25
- **What:** recover per-replicate / RSD values from the Angeloni campaign (analyte
  RSD up to ≈19.7 %) and Schmieder, so the RSM / transfer / baseline-skill / joint
  analyses can be re-run under a heteroscedastic (weighted) error model instead of
  central values only. Also enables propagating the source's first-stage
  fraction→cup integration uncertainty (B5-16).
- **Why TB:** the repo holds condition-level **means**; the replicate tables need a
  source re-intake. Angeloni is MDPI/Cloudflare-blocked to a CC session (see the
  `data-host-reachability` memo) — needs a Tim drop.
- **Acceptance:** report whether model–baseline differences are large relative to
  measurement variation; profile / skill / LOCO / joint conclusions reported under
  plausible measurement-error models.
- **First step:** drop the Angeloni replicate/RSD table into
  `puckworks/data/angeloni2023/` (same pattern as the earlier xlsx drops) + a
  MANIFEST row.
- **Handoff line:** *once the replicate table is on disk, CC wires the
  weighted-objective sensitivity + heteroscedastic reruns.*

### TB-3 · Bundle recompute (optional, removes the freshness flag)
- **What:** the Paper A precision change (A4-06) shifts `overall_mape_blind` by
  sub-0.1 pp; the Paper B audit added `min_jensen_gap_EYpt`. Both cached bundles
  are therefore one commit stale (flagged only by strict `release`, not by the
  green routine tests).
- **Handoff line:** *CC can run both recomputes now (Paper B ≈1 min; Paper A
  ≈30 min background job that self-notifies). Not a correctness blocker — 139 fast
  tests are green — so it can also wait for the TB-1 tag cut.*

### TB-4 · Second-rig / measured-flow data (deeper, optional)
- **IDs:** A4-23, A4-30, B5-30, B5-22
- **What:** measured Angeloni per-condition flow (vs the inferred pressure→flow
  map) or a second-rig TDS campaign would convert several "conditional on inferred
  flow / single-rig" caveats into genuine tests. No path without new data — a
  correspondence/experiment decision. Related instruments live in `docs/sourcing/`.

---

## PI — systematic novelty / literature search

### PI-1 · Execute + archive the indexed search
- **IDs:** A4-40, A4-50, B5-43, A-AR15/MAJ21, B-AR16/MAJ23
- **What:** run the pre-registered Scopus / Web-of-Science query, screen, and
  archive results **before** finalizing any novelty wording. Both drafts currently
  say "to our knowledge, following a documented scoping search" and defer the
  indexed query to submission.
- **Why PI:** needs licensed database access unavailable to a CC session.
- **Already built:**
  - `docs/literature_search/SEARCH_PROTOCOL.md` — the query strings + inclusion logic;
  - `docs/literature_search/EVIDENCE_MATRIX.csv` — to populate with the hits;
  - `docs/literature_search/references.bib` — the working bibliography;
  - `docs/PAPER_B_RELATED_WORK.md` — the claim→prior-art matrix (2 DOIs flagged
    UNVERIFIED: lee2023 `10.1063/5.0138998`, waszkiewicz2025 published-vs-arXiv).
- **Acceptance:** databases, dates, exact queries, screening method, and inclusion
  logic reported; every citation lands in the reference list; novelty framed as an
  **applied espresso case study**, not a new identifiability method.
- **First step:** execute `SEARCH_PROTOCOL.md`; paste hits into `EVIDENCE_MATRIX.csv`.
- **Handoff line:** *CC then reconciles `references.bib`, verifies the two flagged
  DOIs (B5-32), and rewrites the novelty paragraphs proportionately.*

---

## VENUE — journal manuscript conversion (target-journal-dependent)

### VENUE-1 · Convert both drafts to conventional manuscripts
- **IDs:** A4-14/49 + §7.1–7.23; A4-41; B5-11
- **Remove:** the repository note, review IDs (A4-/B5-/MAJ-/AR-), roadmap/§
  references, function names as prose, "owed / data-blocked" statements, and the
  "Open gaps this paper defines" ledger.
- **Add:** conventional Methods (governing equations, parameter tables, solver +
  tolerances, objective/aggregation definitions), Results, Discussion + a
  consolidated Limitations, a complete References list, and Data-availability /
  Code-availability / Ethics / Competing-interests / Funding / AI-use declarations.
- **Why VENUE:** section structure + required declarations are set by the target
  journal. `docs/SUBMISSION_TARGETS.md` ranks venues — **Paper A → J. Food
  Engineering** (first journal); **Paper B → APS DFD 2026 abstract**, then
  *Transport in Porous Media* / *Physics of Fluids* (held pending reanalysis).
- **Two decisions that unblock CC drafting:** (a) pick the journal (so CC matches
  its section format); (b) finish PI-1 (so novelty is final).
- **Handoff line:** *with (a)+(b) done, CC can draft the submission-branch
  manuscript — internal scaffolding stripped, Methods equations written out,
  reference list assembled — for your scientific review. The blocker is those two
  decisions, not the writing.*

### VENUE-2 · Vector figures + self-contained captions
- **IDs:** A4-37/38, A4-36, B5-45, B5-31
- **What:** SVG/PDF figure exports; colour-blind-safe encoding; self-contained
  captions (sample sizes, train/test split, objective, fitted parameters, endpoint
  operator, uncertainty meaning, evidence tier); neutral figure titles.
- **Status:** **largely unblocked** — this does not truly need the venue; it was
  held only because caption *content* pairs with the manuscript conversion.
- **Handoff line:** *CC can add vector output + caption blocks to both figure
  pipelines now, on request — independent of the journal choice.*

---

## Standing offers a CC session can pick up immediately
1. Recompute both result bundles + generate the env lockfile (TB-1/TB-3).
2. Add vector-figure output + self-contained captions to both papers (VENUE-2).
3. After PI-1: reconcile `references.bib`, verify the flagged DOIs, rewrite novelty.
4. After a journal pick + PI-1: draft both submission-branch manuscripts (VENUE-1).
5. After a TB Angeloni replicate drop: heteroscedastic / weighted reruns (TB-2).

*Nothing here blocks the other, already-completed review fixes; these are the
human-owned remainder only.*
