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
4. `docs/ANALYSIS_P2.md`, `docs/P3_hypotheses.md`, and `docs/ANALYSIS_transfer.md`
   — the standing analysis verdicts (extraction harness, κ(t) discrimination, the
   fine-grind-dip scoreboard, and the pannusch→angeloni cross-dataset transfer /
   inventory–kinetics identifiability limit). Read these before reopening any of
   those threads.
5. `docs/PAPER_OUTLINE.md` — the paper-assembly plan and readiness audit: two
   papers (A extraction/identifiability = `docs/PAPER_A_DRAFT.md`, converted from
   the `ANALYSIS_transfer` analysis; B flow/
   bed-dynamics = P3 verdict + κ(t) ladder + N-tube instability) + a possible
   methods note. Read before starting any manuscript work so you don't rebuild a
   result that is already gated and ready.
6. `docs/PUBLIC_VALUE.md` — the **public-value track** (a parallel workstream to
   the scientific ROADMAP): how the repo's data, disagreements, nulls, and
   negative results become material a non-specialist can use (tasks PV-00–PV-18).
   Its §3 communication guardrails are binding on that track exactly as the
   standing caveats are binding on science threads — **a session working any PV
   task reads §3 first.** The public track consumes results; it never softens an
   evidence-strength label. Sequencing/status lives in `docs/SPRINTS.md`
   "Public-value track (PV)".
7. `docs/SUBMISSION_TARGETS.md` — the **live submission/venue schedule** (ranked,
   date-verified venues for Papers A/B; a front-edge deadline ledger at its top).
   **DEADLINE-BEARING and decaying** — recheck each portal before submitting; mark
   a passed deadline PASSED, never delete. Nearest: **APS DFD 2026-07-24**. Anyone
   working a paper/publication task reads its **§15 publication-ethics cautions
   first** (distinct abstracts per venue; no concurrent journal submission; EFFoST
   forbids previously-presented abstracts; SDCC ISBN-proceedings disclosure). Status
   tracked in `docs/SPRINTS.md` "Submission track".

**For any VISUALIZATION work:** `puckworks/viz/` (the evidence-bound viz layer,
ROADMAP §8) and `docs/figures/viz/GALLERY.md` (the honesty index — every visual,
its badge, evidence, and fidelity ceiling) are the entry point. Do not add a
figure outside a VizSpec.

**For an EXTERNAL REVIEW of Paper A / Paper B:** hand the reviewer
`docs/REVIEWER_BRIEF_PAPER_A.md` / `docs/REVIEWER_BRIEF_PAPER_B.md` — reviewer-facing
disclosure registers (known/scoped limitations + max defensible claim per result +
the review ask) so a fresh reviewer does not re-flag already-known/blocked items.

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
- **PV (public-value track):** a distinct workstream, not a venue of its own — a
  CHAT/CC/TB session *can* pick up a PV task, but whoever does reads
  `docs/PUBLIC_VALUE.md` §3 guardrails first and keeps evidence-strength labels
  intact. PV status is tracked in `docs/SPRINTS.md` "Public-value track (PV)".
  Nothing in the PV track is built yet — it is spec + backlog only.

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
- pannusch2024 is the carded multi-solute runtime; angeloni2023 is data-only.
  The transfer harness HAS now spoken (`ANALYSIS_transfer.md`): pannusch does NOT
  transfer to angeloni across grind, and the single-grind whole-cup refit is a
  NON-IDENTIFIABLE curve fit (inventory ↔ kinetics trade off — the flat valley),
  not a validated calibration. Do NOT read the wide-envelope bracket as "it
  transfers"; the fraction-vs-cup identifiability result (gap **G6**) is why. Keep
  them data-vs-model.
- **brewer2026.coupled_kappa_t is a SYNTHESIS component** (`kind=synthesis`, no
  external paper — do not hunt for one). It is the coupled-porosity-ODE κ(t)
  closure; label it "framework; branch fidelity inherited," never "validated
  κ(t) law" (three of its four donor branches carry unidentified/unvalidated
  params). Its flow closure is the **poroelastic** one, NOT Kozeny–Carman (card
  Eq. 2 was corrected card-side; CK is auxiliary/illustrative only). Do not
  re-adjudicate that.
- **mo2023_2 has two extraction implementations, both kept on purpose:**
  `mo2023_2.coupled_bed` (depth-resolved + filling front, the Fig-8 model,
  supersedes for fidelity) and `mo2023_2.extraction` (reduced lumped, retained
  for the fixed-q swelling-insensitivity gate). Do not merge or retire either.
  The coupled bed's M_c=20 over-prediction is CONVERGED/genuine (the card's own
  "overestimates beyond M_c~30 g"), not a bug to chase.
- G1 (unsaturated flow) is blocked on CONSTITUTIVE data (coffee retention
  curves), not on solver choice; egidi2018 is skip. The wetting-atom probe is
  an analysis tool, not a registered component.
- **G4 (temperature) extraction-chemistry part is PARTIALLY resolved:** two
  independent K(T) closures (romancorrochano Arrhenius, pannusch van't Hoff) +
  schmieder's 80/89/98 °C data all agree the extraction-chemistry T-effect is
  SMALL (`gate_g4_temperature_sensitivity`). The two closures DISAGREE on the
  SIGN of dK/dT (partition-convention difference — surfaced, not merged; do not
  average them). In-puck thermal transients + wetting/swelling-T remain OPEN.
- **G-lat is a new gap:** in the TESTED near-choke config, dynamic per-tube
  channeling-κ(t) strongly concentrates flow (N_eff→1) without lateral coupling
  (ANALYSIS_P2 §2.4) — an exploratory finding, NOT a proven unconditional
  instability (no sweep/theorem). The static streamtube is the right tool for the
  time-averaged response; the dynamic union is diagnostic only. Also note the P3
  verdict was DOWNGRADED to model-capacity (2026-07-12) — see P3_hypotheses
  CORRECTION box; the schmieder "peak" target was dimensionally invalid.
- **G9 (basket/screen resistance) is RESOLVED for a clean basket:** the screen
  resistance from schulman2011 geometry is ~5–6 orders below the puck →
  negligible; the earlier fitted-vs-measured κ gap is coffee/grind, not screen.
  The only open piece is fines CLOGGING mid-shot (unmeasured). Do not reopen G9
  as "screen matters."

- **visualizer.coffee is a data-only intake** (card `visualizer_coffee.md`): a
  LARGE but UNCONTROLLED, self-selected public shot corpus. Its machine-logged
  hydraulics are reference-strength POPULATION data (G3/P2/P6 ecological
  envelope); its user-entered TDS/EY/sensory are NOT groundtruth and must never
  gate an extraction outcome. The corpus is gitignored and NOT redistributed
  (license posture §5.8) — run the harvester to populate it
  (`python -m puckworks.lib.visualizer_harvest full`); tests use a committed
  fixture, never the API. Hydraulic and outcome tiers are stored SEPARATELY;
  never merge them.

- **Visualization is a CONSUMING layer** (`puckworks/viz/`, ROADMAP §8), not a
  component. Every visual binds to a producer and carries a public badge +
  evidence-strength label + a fidelity ceiling; a render may NOT depict a
  mechanism above its source component's validity (fines transport =
  fasano-STRUCTURED verification-only; N-tube concentration = one-config
  exploratory; `coupled_kappa_t` = framework). Beautiful is allowed; over-claiming
  is not. Heavy renders are gitignored; thumbs + `GALLERY.md` + `data.json` are
  tracked.

If in doubt: read the changelog, run the gates, ask one clarifying question.
