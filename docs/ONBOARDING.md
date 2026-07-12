# ONBOARDING — read this first

You are joining an in-progress research-engineering project (puckworks: a
component registry for espresso process models). This file is the fixed entry
point for any new session, human or Claude. Follow it in order.

## 0. Confirm repo access
If you reached this file by cloning `github.com/trbrewer/puckworks`, you have
access — proceed. If a session cannot clone the repo, ask the user to upload
the four orienting files named in step 2; everything below still applies.

## 1. Read the rules before touching anything
`CLAUDE.md` (repo root) — non-negotiable architecture rules: cards before code,
stop-don't-guess on ambiguity, the validation-strength vocabulary, the manifest
rule, no silent constant merges, quick-gates-only in CI. If a request conflicts
with CLAUDE.md, flag it rather than comply.

## 2. Get oriented (read order)
1. `docs/ROADMAP.md` — the plan. §0 status glossary + strength vocabulary;
   §3 development sequence (work items by number); §4 gaps; §5 open questions;
   **§7.1 change log and §7.2 resolved questions — read these to learn what was
   decided and why.** The changelog is the project's memory; trust it over any
   summary.
2. `docs/SPRINTS.md` — sprint breakdown + status log; tells you what is done
   and what is next, with venue tags (CC / INTAKE / CHAT / TB).
3. `docs/cards/` — one card per model; the source of truth for each model's
   physics, parameters, assumptions, and VERDICT. Never implement from memory
   of a paper — implement from its card.
4. `docs/ANALYSIS_P2.md` and `docs/P3_hypotheses.md` — the standing analysis
   verdicts (extraction harness, κ(t) discrimination, the fine-grind-dip
   scoreboard). Read these before reopening any of those threads.

## 3. Verify the state is live, not remembered
```
pip install -e ".[dev]"
pytest -v      # quick gates must pass
python -c "from puckworks.registry import run_all_gates, components; \
print(len(components()),'components'); run_all_gates()"
```
If gates fail on a clean clone, that is the first problem to report — do not
build on a red tree.

## 4. Know the venue you are in
- **Claude Code (in the repo):** implementation, refactors, gates, commits.
  Obeys CLAUDE.md commit style `<item#>: <what>`. Updates ROADMAP §7.1 +
  SPRINTS in the same commit as any component or gate change.
- **Card project (INTAKE):** literature → model cards only, no code.
- **Chat (CHAT):** analysis, synthesis, prioritization, writeups. Produces
  docs (ANALYSIS_*, roadmap edits), not components.
- **TB:** correspondence and physical experiments the user runs.

## 5. What the repo does and does not remember
The repo captures **committed state**: code, cards, roadmap, changelog. It does
NOT capture chat-session reasoning unless that reasoning was written into a doc.
Rule of thumb, and a house discipline: **if a decision matters, it goes in a
doc** — a §7.1 changelog entry (with dataset + gate script cited) or a §7.2
resolution. A new session inherits only what was written down. When continuity
of a specific contested thread matters, read that thread's changelog entries and
ANALYSIS section, not just this file.

## 6. Standing caveats a newcomer must not re-litigate silently
- Validation-strength tags are load-bearing: most extraction agreements are
  post-fit reconstruction, not independent validation. Do not upgrade a tag
  without a §7.1 entry.
- Three c_sat values (170 / 212.4 / 224) and per-lineage soluble inventories
  are surfaced side by side, never merged.
- pannusch2024 is the carded multi-solute runtime; angeloni2023 is data-only
  (independent validation target), NOT a competing runtime. Keep them
  data-vs-model until a harness says otherwise.
- G1 (unsaturated flow) is blocked on CONSTITUTIVE data (coffee retention
  curves), not on solver choice; egidi2018 is skip. The wetting-atom probe is
  an analysis tool, not a registered component.

If in doubt: read the changelog, run the gates, ask one clarifying question.
