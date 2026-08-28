# Puckworks publishing system

**Status:** Governing editorial and automation specification

**Primary publication:** puckworks on Substack

**Secondary platform:** puckworks on Medium

**Owner and final publisher:** Tim Brewer

**Timezone:** `America/Chicago`

**Source of record:** Substack

**Automation boundary:** evidence assembly, drafting, scheduling, and reminders only—never publication.

## Purpose and scientific ceiling

This system converts explicitly eligible scientific and repository events into evidence-bound public
drafts for a free science-of-espresso publication. It covers findings, limitations, negative results,
corrections, testable beliefs, physical plausibility, practical controls, unsupported optimization,
and provenance-documented data and figures.

The central hypothesis is **H1: Water reaches chemical equilibrium with the extractable soluble
material before it is flushed from the puck.** H1 is a hypothesis, not a standing conclusion. It may
be described as confirmed only when a controlling repository record says so and the exact evidence
passes all scientific and publication gates. Any implication that hydraulic variables and the
collected-mass endpoint dominate extraction kinetics remains conditional on that evidence.

The current checked-out repository state controls. Before drafting, inspect where present the claim
ceiling, project/current state, `puckworks/data/MANIFEST.csv`, relevant model cards and result reports,
source manifests, the triggering issue/PR/release/run, and corrections, exceptions, or adverse
invocations. A current claim ceiling overrides titles, schedules, old drafts, README prose, and memory.

## Non-negotiable rules

The publication is strictly non-commercial: no paid tier, affiliate, sponsorship, endorsement,
ranking, or purchasing advice. Repositories remain free and open. Every quantitative claim traces to
an exact repository artifact (path plus full commit, and where relevant run/issue/release and SHA-256)
or a complete paper citation. Uncertainty, limitations, null results, errors, and corrections remain
visible. AI drafting is disclosed. Criticism addresses evidence, never people.

Never claim taste, flavor, preference, or sensory prediction. Never convert verification, calibration,
post-fit reconstruction, descriptive reproduction, in-sample fit, test passes, reviews, merges, or
releases into independent physical validation. Never generalize beyond tested coffee, grinder,
machine, basket, pressure programme, laboratory, or campaign without an explicit transferability
basis. Never average competing model branches for a convenient answer. Never infer a conclusion from
a title, branch, commit message, or attractive plot. Never publish automatically.

## Trigger contract

Eligible event types are `tagged_release`, `milestone_closed`, `dataset_added`,
`validation_completed`, `hypothesis_updated`, `correction`, `blocked_result`, and
`public_explainer`. Each needs its governing result bundle and explicit disposition. Formatting,
dependencies, refactoring, test counts, CI maintenance, branch creation, issue opening, draft PRs,
unreviewed exploration, ungoverned plots, and reader-irrelevant releases are ineligible by themselves.

Activation requires exactly recorded machine-readable authority: a `publication-candidate` label, a
valid `content/triggers/*.yml` manifest, or `publication_trigger: true` in the final artifact. Free
text is not authority. Trigger manifests use schema version 1 and record:

- a `PW-PUB-YYYY-NNN` ID and `publication_trigger: true`;
- repository, eligible event type, resolvable identifier/URL, and detection timestamp;
- exact disposition, claim-ceiling and project-state paths, evidence level, hypotheses, and whether
  the claim ceiling changed;
- archetype, provisional title, public value, urgency, and target platforms;
- every artifact's repository, path, full 40-character SHA, optional issue/PR/release/run/checksum,
  and precise purpose;
- fatal `stop_reasons` and owner notes.

Every path must exist at its stated commit. Disposition must match its controlling artifact. A changed
claim ceiling must itself be listed. Missing artifacts, ambiguous disposition, stale ceilings, or stop
reasons produce diagnostics and no substitute prose.

## Draft and evidence contract

Masters live only in `content/drafts/YYYY-MM-DD-slug.md`; platform variants live in
`content/variants/`. Draft prose never enters scientific result directories. YAML frontmatter schema
version 1 records identity/status, author, platforms, length, source event, exact claim ceiling, source
artifacts, figures, claims, uncertainty, practical implications, AI roles and human checks,
cross-posting, and review gates.

Each evidence item states what it establishes and does not establish and labels its level as
`independent`, `post_fit`, `calibration`, `verification`, `descriptive`, `exploratory`, `qualitative`,
or `mixed`. Each claim has an ID, exact text, evidence IDs, conditions, evidence level,
applicability, caveat, and quantitative flag. Every number in prose, subtitle, caption, callout, or
table belongs to a quantitative claim row or is directly identified in the evidence box.

Every master uses this order: result/question in one sentence; why it matters; hypothesis; evidence
box; method; result; interpretation; what it does not show; uncertainty and limitations; practical
implication only if supported; evidence that would change the conclusion; reproduction/inspection;
claims-to-evidence table; AI disclosure; and a removable agent self-review.

The evidence box names repository, full commit, run/result, primary artifact, figure source, evidence
level, and exact claim ceiling. The claims table has claim ID, exact claim, evidence IDs, evidence
level, applicability/conditions, and caveat.

## Archetypes and verdicts

Supported archetypes are finding report (1,200–1,800 words), myth check (1,000–1,600), innovation
review (1,200–1,800), practical guide (900–1,400), behind the model (1,500–2,800), digitized-data
release (500–900), and correction (400–900). Myth checks use exactly one verdict: “Supported within
the tested conditions”, “Conditionally true”, “Currently unsupported”, or “Unresolved”. Innovation
reviews use exactly one: “Physically plausible with direct evidence”, “Physically plausible but
unsupported”, “Inconsistent with available evidence”, or “Presently unresolved”, and state they are
not endorsements. Correction posts link both ways with the amended original.

## Evidence and human gates

Moving to `ready` requires source closure; complete traceability; claim-ceiling compliance in title,
subtitle, opening, captions, and takeaway; commercial neutrality; explicit limitations, external
validity, alternatives, largest uncertainty, and next discriminating measurement; regenerated,
unedited figures with scripts, inputs, SHA-256, captions and descriptive alt text; and Tim Brewer's
recorded inspection of all artifacts, claims, numbers, citations, and figures. Medium additionally
requires substantive human rewriting. A failure leaves the draft in draft/evidence/human review with
the exact failure reported. Automation cannot invent, soften, or approve the missing material.

Ready frontmatter must name Tim Brewer, set all four AI-assisted scientific check flags true, set all
three automated gate flags true, record `human_approved: true`, and include `approved_at`. Only a human
may set `published`, record public URLs, approve corrections or claim-ceiling changes, send email,
submit to Medium, or press Publish.

## Figures, notes, and short form

Prefer verified SVG line art or PNG at least 1,600 pixels wide, plus 1,200×630 previews where needed.
Record generating script, committed source data, output checksum, run, applicability, and limitation.
Alt text names chart type, axes and units, groups, trend, uncertainty encoding, and the visual
conclusion. Figures are never manually altered, selectively cropped, or stripped of uncertainty.
Static fallbacks accompany interactive material. Code excerpts are at most 20 lines and link to exact
files/commits.

Generate at most three draft Notes per week in `content/notes/YYYY-Www.md`: Figure Notes are 80–160
words/900 characters before links, Observation Notes 60–120/700, and one-question Reader Notes
30–80/450. Notes supply value without a click, include limitations where required, never solicit
anecdotes as representative validation, and never automate replies, likes, comments, recommendations,
or restacks. Do not place AI-assisted copy where community rules forbid it.

## Schedule, reminders, and publication flow

`content/schedule.yml` is schema version 1 in America/Chicago, with 09:00 default publication time,
drafts due five days before publication, reminders seven and two days before draft/publication dates,
and a seven-day Medium lag. Statuses are planned, drafting, evidence review, human review, ready,
published, cancelled, and withdrawn. Only a human sets published. The initial twelve-item schedule is
committed there as controlling machine-readable data.

The daily 14:05 UTC workflow validates the schedule and uses `ZoneInfo("America/Chicago")`. It creates
or updates a single issue per schedule ID using `<!-- publishing-schedule-id: ID -->`, applies
`editorial` and `publish-reminder`, and closes only terminal items. Monday digests list the next 14
days, overdue/evidence-blocked/human-review drafts, missing URLs, unverified Medium canonicals,
eligible triggers, and failed trigger diagnostics. The workflow has only contents-read/issues-write,
contains no platform credentials, infers no science, generates nothing from unlabeled events, and
cannot publish.

Build order is: validate trigger; assemble evidence; draft master; automated checks; human scientific
review; Substack variant; manual Substack publication; exact URL record; seven-day Medium date;
Medium variant; substantive human rewrite/review; manual Medium publication/submission; canonical
assignment and verification; URL/date record. Variants may alter framing, not scientific claims,
numbers, levels, applicability, verdict, uncertainty, or ceiling. Medium stays outside the paywall,
stands alone, discloses AI in its first two paragraphs, and is never generated as publication-ready.

## AI disclosure and self-review

Global statement: “AI-assisted drafting helps me turn repository artifacts into prose. I edit every
draft and verify every scientific claim, number, citation, and figure against the linked source. The
scientific judgments and final wording are mine.”

Substack ending: “Drafting note: I used AI assistance to prepare and edit this article from the linked
repository materials. I checked every scientific claim, number, citation, and figure before
publication.” Medium first paragraphs use: “Disclosure: I used an AI writing tool to help draft and
edit this article from the linked repository materials. I personally checked every scientific claim,
number, citation, and figure.” Do not use AI-generated cover artwork.

Before presentation, the removable self-review asks whether the narrow claim is exact; title and
captions stay below it; calibration is not called validation; every number resolves; chemistry is not
taste; transfer limits, null/adverse/superseding results, principal limitation, alternatives, figure
provenance, disclosure, Medium human reasoning, practical clarity, and next discriminating measurement
are present; and whether the article is genuinely worth publishing rather than merely evidence of work.

## Explicit non-goals

No platform or community publication, credentials, autonomous engagement, invented data/results/runs/
commits/papers/quotes, hidden corrections, figure alteration, favorable-run selection, marketing,
commerce, brands outside evidence necessity, taste claims, H1 upgrade, mass event-to-draft conversion,
governance-as-science, cross-platform conclusion changes, unverified Medium canonical, or automated
`ready`/`published` state is permitted.
