# PUCKWORKS — STATE OF TRUTH

Canonical status queue (WP0.2). Supersedes stale backlog checkboxes where they
conflict with code/tests/manuscripts. Last verified commit: **19919c4** (2026-07-16).

State vocabulary: **implemented** (code+tests exist) · **validated** (scientifically
checked/gated) · **release-ready** (clean-build/archive verified) · **submitted**.

---

## 0. PRIMARY-LANE DECISION — **RESOLVED 2026-07-16: publication-integrity first, then product**

PI decision: drive the **NEXT_STEP_PLAN** publication-integrity + release
convergence lane now (real freeze lifecycle + pressure-atlas v2 + Paper A RC +
Paper 3 evidence graph), THEN pivot to the **PRODUCT_FIRST** vertical slice on a
trustworthy spine. Converge/ship first; build the product second.

Consequence: the freeze-lifecycle rebuild (WP1) IS in scope now (Doc 1 would have
deferred it). Both docs still defer further G10 work. Merge sequence = Doc 2's
PR0→PR12.

---

## 1. REALITY RECONCILIATION (what is actually true at 19919c4)

| item | state | proof | note |
|---|---|---|---|
| G10 coffee-liquor rheology | **validated / CLOSED** | `gate_g10_*` (7 gates), `analysis.g10_viscosity_sensitivity`, ROADMAP §4 ✅ | NOT an active engineering track. Only optional upgrade: independent espresso-TDS measurement |
| Paper A baseline-relative transfer skill | **validated** | task #45; handoff M-series; producer bundle | do NOT reimplement; needs the RELEASE-CANDIDATE wrapping (WP3), not new modeling |
| Registry schema v2 (execution_role/provenance_class/evidence_strength) | **implemented** | `puckworks/models/__init__.py`; `paper3.registry_artifacts` | evidence is component-level; gate-level graph (WP4) NOT yet built |
| Paper 3 generated artifacts + staleness guard | **implemented** | `docs/paper3_resource/generated/*`; `test_registry_artifacts`, `test_paper3_build` | `bundle` is manifest/path-level, NOT a real archive (WP4.6) |
| Visualizer harvester + Bronze store + census + controller atlas + corpus_bundle | **implemented** | `puckworks/lib/visualizer_harvest.py`, `analysis/{visualizer_census,controller_atlas,corpus_bundle}.py` | corpus-freeze is a MANIFEST op, not a verified immutable snapshot (WP1) |
| Live-contract canary + CI lanes (quick-pr / generated-artifacts / slow-science / live-contract / release) | **implemented** | `.github/workflows/*`, `puckworks/lib/visualizer_canary.py` | lanes not yet operationally DISTINCT by marker (WP5) |
| Clean v6 crawl (`crawl_v6_20260715`) | **running** | pid 17148, ~2.9k shots, reconcile ok, 100% bronze | **EXPLORATORY public-updated window, NOT a coherent export** — see §2 |

---

## 2. OPERATIONAL CORRECTION — crawl freeze classification

**The running v6 crawl must NOT be frozen as `publication-freeze`.** Per
NEXT_STEP_PLAN WP1.5 / WP7, a publication snapshot requires a *sanctioned coherent
export* with an export cutoff; a moving recent-activity public window is exactly
what the publication gate must REJECT. When the crawl exhausts the window:

- freeze it as **`current-state`** (or `exploratory-window`) — an inspectable
  reference snapshot, clearly marked `EXPLORATORY — NOT A PUBLICATION SNAPSHOT`;
- do **not** run `build_bundle(require_freeze=True)` against it;
- the real publication freeze waits on WP7 (a Miha-side bulk export/token, still
  pending — memory `harvest-corpus-access-blocker`).

This revises the earlier "freeze automatically as publication-freeze" plan.

---

## 3. COMPACT ACTIVE QUEUE (≤5; pending the §0 lane decision)

| # | outcome | owner | blocking dependency | proof-of-done |
|---|---|---|---|---|
| Q1 | ~~Decide the primary lane~~ **DONE** — publication-integrity first, then product | PI | — | §0 resolved |
| Q2 | ~~B2 APS DFD abstract~~ **CLOSED — not submitting** (PI, 2026-07-16); recorded, no further action | PI | — | Gate A resolved: no-submit |
| Q3 | Freeze the v6 crawl as `current-state` when it exits (NOT publication) | code | crawl exhausts window (monitor armed) | `current-state` snapshot manifest + EXPLORATORY mark |
| Q4 | **PR1 — logical-version selection correctness** (WP1.1): deterministic max(updated_at)+sequence tie-break; equal-ts conflicts visible; as_of + shard-order regression tests; replace touched registry asserts | code | — (in progress) | conflict/shard/as_of tests green |
| Q5 | PR2 — real freeze lifecycle (rehearse/materialize/verify; derived PublicationSnapshot; immutable canonical view; negative publication-gate tests) | code | Q4 | WP1 acceptance criteria |
| Q6 | (opportunistic) sanctioned corpus export runbook | maintainer | Miha export/token (external) | WP7 pilot on real export |

Then PR3 export contract → PR4 pressure-atlas spec+time engine → PR5 hierarchical
inference → PR6 Paper A RC → PR7 evidence graph → PR8 Paper 3 RC → PR9 CI lanes →
PR10 lateral-coupling feasibility. Product lane (Doc 1) follows this convergence.

**Deprioritized / not active:** further G10 viscosity work; broad registry growth;
generic data intake for count's sake; the product build (deferred to after
convergence, per the lane decision).

---

## 4. DEADLINE FLAG

**B2 APS DFD abstract — CLOSED (PI decision 2026-07-16: not submitting).** No
calendar-bound items remain. Recorded here per WP0.1 acceptance ("submitted, or a
recorded explicit decision not to"); no rehearsal-corpus metric was published; the
broader B2 manuscript scope remains review-stable and untouched.
