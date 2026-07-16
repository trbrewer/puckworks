# PUCKWORKS — STATE OF TRUTH

Canonical status queue (WP0.2). Supersedes stale backlog checkboxes where they
conflict with code/tests/manuscripts. Last verified commit: **19919c4** (2026-07-16).

State vocabulary: **implemented** (code+tests exist) · **validated** (scientifically
checked/gated) · **release-ready** (clean-build/archive verified) · **submitted**.

---

## 0. PRIMARY-LANE DECISION — **OPEN (blocks sprint selection)**

Two strategic docs were recorded 2026-07-16 with CONFLICTING single-choice picks:

| doc | primary lane | picks |
|---|---|---|
| [PRODUCT_FIRST_REPRIORITIZATION](PRODUCT_FIRST_REPRIORITIZATION.md) | build the consumer product | PV-19 vertical slice → Puck Court (PV-08) shell → PV-00 as content API; papers become derivative |
| [NEXT_STEP_PLAN_2026-07-16](NEXT_STEP_PLAN_2026-07-16.md) | publication-integrity + release convergence | real freeze lifecycle + pressure-atlas v2 + Paper A RC + Paper 3 evidence graph |

They are mutually exclusive as the IMMEDIATE next cycle. **Owner: PI.** Both share
WP0 (this file) and both defer further G10 work. Everything below WP0 is
lane-gated.

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
| Q1 | **Decide the primary lane** (product-first vs publication-integrity) | PI | — | this file §0 resolved |
| Q2 | **B2 APS DFD abstract** submitted or explicit no-submit recorded | PI + code | human metadata (author/APS membership/eligibility); the abstract source | submitted text+hash in ledger, or recorded decline (Gate A) |
| Q3 | Freeze the v6 crawl as `current-state` when it exits (NOT publication) | code | crawl exhausts window (monitor armed) | `current-state` snapshot manifest + EXPLORATORY mark |
| Q4 | (lane-gated) first PR of the chosen lane | code | Q1 | PR1 of the chosen doc's merge sequence |
| Q5 | (opportunistic) sanctioned corpus export runbook | maintainer | Miha export/token (external) | WP7 pilot on real export |

**Deprioritized / not active:** further G10 viscosity work; broad registry growth;
generic data intake for count's sake; publication-grade freeze architecture as a
speculative build (only under the publication-integrity lane); manuscript release
bundles ahead of the lane choice.

---

## 4. DEADLINE FLAG

**B2 APS DFD abstract (Q2)** is the only calendar-bound item and is a *human*
action (author/affiliation/APS membership/presenter eligibility + portal limits);
I can regenerate its quantitative statements from producers and verify against the
claim ceiling, but I cannot submit it. If there is a live deadline, treat Q2 as
the immediate exception per WP0.1 — independent of the lane choice and the corpus.
