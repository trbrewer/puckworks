# PUCKWORKS — STATE OF TRUTH

Canonical status queue (WP0.2). Document index: [`docs/CURRENT.md`](../CURRENT.md).
Supersedes stale backlog checkboxes where they conflict with code/tests/manuscripts.

State vocabulary: **proposed** · **implemented** (code+tests exist) · **CI-verified**
(passes required CI at its committed SHA) · **validated** (scientifically checked/gated) ·
**release-ready** (clean-build/archive verified) · **submitted**. A bare "DONE" is banned —
"implemented locally" is NOT "CI-verified".

> **CI STATUS (2026-07-16).** `quick-pr` was **RED on main** from ~PR7 to `89ca573` — a
> matplotlib-in-quick-lane leak that passed locally (with matplotlib) and failed on CI's
> 3.10/3.12; my earlier "all green / 265 passed" claims were **local-only** and were retracted.
> **Fixed and CI-VERIFIED green** via PR #1 (R0/R1, `acfe9d0`) + PR #2 (R2 lane rigor): quick
> 3.10 + 3.12 pass, generated-artifacts passes, `live-contract` no longer fails at parse.
> Remediation proceeds via branch → PR → CI-verify → merge (guardrail 4). Lesson kept in the
> vocabulary above: *implemented ≠ CI-verified*.

> **LATERAL + EVIDENCE-GRAPH STATUS (2026-07-16).**
> - **Lateral coupling feasibility** — PR #12 (`b7fb4bd`) landed the two-node physical model +
>   matched frozen-uncoupled-share-proxy discrimination; PR #14 (`6c5eb31`) added the exact Ξ
>   equalization group (`gap/gap0 = 1/(1+Ξ)`), continuous-α share matching, and precise comparator
>   naming. **CI-verified.** Result is **representational/mathematical** distinguishability on
>   synthetic cases only. **Open scientific gates:** measurability of Ξ (needs k_lat, w) and
>   structural identifiability both stay OPEN; practical experimental resolvability is OPEN (no
>   instrument/noise model). **Paper 4 NOT authorized.**
> - **Paper-3 evidence graph** — PR #13 (`5d611df`) landed the v1 infrastructure as
>   **draft-validated** (draft `--reconcile` + `--verify` in the required generated-artifacts
>   lane). **This PR** adds schema v2 (claim_owner / paper3_use / reality_facing / support_status /
>   typed `sources[]` / dataset_status), the scope-aware strict modes, the mechanical guards, and 3
>   semantic corrections. **`--strict --scope paper3` (the release gate) is GREEN** — every
>   asserted Paper-3 claim is admissible. **It is NOT yet a required branch check**: promote it
>   after PR C. **`--strict --scope all` stays manual** (33 of 49 links still `NEEDS_ADJUDICATION`;
>   7 priority gates are PR C's target).
> - **Verified commit at this writing:** `6c5eb31` (main, post PR #14). This PR (evidence-graph
>   v2) is on branch `fix/evidence-graph-scope-and-semantics`, pending CI.

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
| Registry schema v2 (execution_role/provenance_class/evidence_strength) | **implemented** | `puckworks/models/__init__.py`; `paper3.registry_artifacts` | component-level; the gate-level graph (WP2.4) now exists (`paper3.evidence_graph`, v2) |
| Gate-level evidence graph (WP2.4, schema v2) | **CI-verified (draft) + paper3-strict + all-strict green** | `paper3.evidence_graph`; `EVIDENCE_LINKS.json`; `tests/test_evidence_graph.py` | **49/49 adjudicated**; both `--strict --scope paper3` (20 asserted claims) and `--strict --scope all` green in `paper3-evidence.yml`; NEITHER yet a required branch check (user promotes); one open follow-up = the component→gate roll-up policy (infiltration tier) |
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
| Q4 | ~~PR1 — logical-version selection~~ **DONE** (e21a50f): canonical max(updated_at)+append-seq; equal-ts conflict determinism + as_of + shard-order tests | code | — | ✅ committed |
| Q5 | ~~PR2 — real freeze lifecycle~~ **DONE**: `corpus_freeze.{freeze_rehearse,freeze_materialize,freeze_verify}` + `FreezeCandidate`/`PublicationReceipt`; bundle gated on a VERIFIED receipt (not a label); moving window rejected; overwrite/mutation guards; 9 lifecycle tests | code | — | ✅ (pending commit) |
| Q6 | ~~PR3 — sanctioned-export contract + synthetic importer~~ **DONE**: `corpus_export` + `SANCTIONED_EXPORT_SPEC.md` + end-to-end synthetic pipeline | code | — | ✅ committed |
| Q7 | ~~PR4 — pressure-atlas spec + time engine~~ **DONE**: `PRESSURE_ATLAS_SPEC.md` (v1, hashed) + time-weighted/gap-aware/active-phase engine + deterministic one-shot-per-user + 8 analytic fixtures | code | — | ✅ (pending commit) |
| Q8 | ~~PR5 — hierarchical inference~~ **DONE**: user-cluster bootstrap CIs; seeded one-shot-per-user; concentration + exclusion-flow first-class | code | — | ✅ committed |
| Q9 | **PR6 — Paper A submission RC** — code core DONE (`paper_a.build verify`: 27/27 claims match manuscript). **BLOCKED (PI)** on: venue choice, indexed literature-search reconciliation, author order/contributions/conflicts/funding, author approval, clean-tree release build | PI | human sign-off | Gate F |
| Q10 | **PR7 — gate-level evidence graph** — WP4.4 validation-exceptions DONE (survive `python -O`). **BLOCKED (PI/scientific)** on WP4.1/4.5 EvidenceLink authoring: per-gate card+dataset+claim mapping needs adjudication (sourcing2026.*/brewer2026.* don't resolve by prefix; low-confidence tiers flagged earlier need review) | PI+code | claim/card/dataset adjudication | WP4 acceptance |
| Q11 | ~~PR9 — CI lanes~~ **DONE**: pytest markers + conftest auto-mark + policy test; quick-pr selects `not slow...` (13s vs 127s); slow-science runs `-m slow` + artifacts; workflows hardened (permissions/timeouts/concurrency) | code | — | ✅ (pending commit) |
| Q12 | ~~PR10 — lateral-coupling feasibility CARD~~ **DONE**: card (operator/BCs/nondim/regime map/go-no-go) + minimal conservative Model 0/1 (`models/lateral_coupling.py`) + conservation/limit/regime tests | code | — | ✅ (pending commit) |
| Q13 | PR8 — Paper 3 REAL archive (rename bundle→list-bundle; wheel+sdist; checksum; clean-room example) | code | partly environment-constrained (fresh-env install) | WP4.6 |
| Q14 | (opportunistic) sanctioned corpus export runbook | maintainer | Miha export/token (external) | WP7 pilot on real export |

**TRULY-BLOCKED boundary reached.** All cleanly-unblocked lane PRs are done
(PR0–PR5, PR7-WP4.4, PR9, PR10). Remaining work is either **PI-blocked** — PR6 Paper A
submission (author sign-off, literature search, venue) and PR7-full evidence-link
authoring (claim/card/dataset adjudication) — or **environment/packaging-constrained**
(PR8 clean-room wheel/sdist archive) — or **external** (WP7 sanctioned export). The
product lane (Doc 1) is the next major phase once these clear.

**WP1 acceptance now met:** a classification string can no longer create a
publication snapshot (`freeze_snapshot` rejects the label; `build_bundle` requires a
verified receipt); the exploratory moving window is rejected by `freeze_rehearse`;
materialization is immutable + non-overwriting; verification detects source/file
mutation. Remaining WP1.7 (synthetic sanctioned export end-to-end) = PR3.

**Deprioritized / not active:** further G10 viscosity work; broad registry growth;
generic data intake for count's sake; the product build (deferred to after
convergence, per the lane decision).

---

## 4. DEADLINE FLAG

**B2 APS DFD abstract — CLOSED (PI decision 2026-07-16: not submitting).** No
calendar-bound items remain. Recorded here per WP0.1 acceptance ("submitted, or a
recorded explicit decision not to"); no rehearsal-corpus metric was published; the
broader B2 manuscript scope remains review-stable and untouched.

---

## 5. REMEDIATION STATUS (2026-07-16, remediation plan) — all via branch→PR→CI-verify→merge

| item | state | evidence |
|---|---|---|
| R0 quick-CI red (matplotlib in quick lane) | **CI-verified fixed** | PR #1 (`acfe9d0`): quick 3.10+3.12 green; clean `.[dev]`-venv repro |
| R1 invalid live-contract workflow | **CI-verified fixed** | PR #1: `vars`-gated, parses, no 0 s parse-fail |
| R2 CI lane rigor (network-block + partition policy) | **CI-verified** | PR #2 (`5f775d6`) |
| R3 doc-truth (CURRENT index + archive + link check) | **CI-verified** | PR #3 (`540185d`) |
| R4 real release pipeline (wheel/sdist + clean-room) | **CI-verified + locally proven** | PR #4 (`86b1294`); wheel installed in a fresh venv, ran the registry example |
| R5 governance (CODEOWNERS/PR-tmpl/CONTRIBUTING/SECURITY/CHANGELOG) | **CI-verified** | PR #5 |
| R9 ruff lint in CI + hygiene + README | **CI-verified** | PR #6 |
| R8 no-private-corpus guard + retention policy | **CI-verified** | this PR (`test_data_privacy`, PROVENANCE retention §) |

**Blocked / deferred (owner):**
- Branch protection on `main` + a dependency-update service — **repo-admin (PI)**; cannot be set from a PR.
- N2 Paper A submission RC (venue, indexed literature search, author order/conflicts/funding, approval) — **PI**. Claims already verify (27/27).
- N3 / WP4 gate-level evidence graph — **PI/scientific**: per-gate card+dataset+claim adjudication.
- R6 registry/contract tightening (`kind` migration deprecation, typed gate results) — **P2, deliberately deferred** (plan: no broad rewrite; not required by release evidence). F841 unused-locals are the tracked ruff follow-up.
- Sanctioned corpus export pilot (WP7) — **external** (Miha bulk export/token).
- Product vertical slice (Doc 1) — **deferred by the lane decision** until the convergence spine is complete.
