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

Both control paths must be closed by exactly one listed artifact from the source repository. A
draft's claim-ceiling repository, path, and full commit must exactly match that trigger artifact and
resolve through Git. The source identifier must likewise be closed by a listed commit SHA, release
tag, issue number, or run ID; syntactically valid but unbound identifiers are ineligible.

## Two-layer draft and evidence contract

Masters live only in `content/drafts/YYYY-MM-DD-slug.md`; platform variants live in
`content/variants/`. Master frontmatter schema version 2 records identity and status, author,
platforms, length, a reader contract, source event, exact claim ceiling, source artifacts, figures,
claims, uncertainty, practical implications, AI roles and human checks, cross-posting, and review
gates.

The **internal evidence package** remains mandatory: publication trigger, exact source artifacts,
evidence ledger, claim inventory, evidence levels, conditions and applicability, quantitative-claim
closure, uncertainty inventory, figure provenance, full commits and paths, human scientific checks,
and the no-automated-publication boundary. It supports evidence assembly, review, auditability,
correction, reproducibility, and resistance to claim inflation. It is not automatically public copy.

The **public narrative** normally contains a recognizable espresso question or experience; an early,
narrow answer; a plain-language explanation of the physical mechanism; the important measurement,
model comparison, or failed explanation; a useful takeaway where justified; a short account of the
material limits; sources and technical notes; and the required AI disclosure. Authors choose natural
headings for the story. The only required public heading is `Sources and technical notes`.

Each evidence item states what it establishes and does not establish and labels its level as
`independent`, `post_fit`, `calibration`, `verification`, `descriptive`, `exploratory`, `qualitative`,
or `mixed`. Each claim has an ID, exact text, evidence IDs, conditions, evidence level,
applicability, caveat, and quantitative flag. Every scientific number in reader-facing prose belongs
to a quantitative claim. Every reviewed claim sentence appears in the narrative, while claim IDs and
evidence IDs stay backstage.

The public article does not have to display an evidence box, claims table, full commits, trigger IDs,
repository paths, validation commands, reproduction tutorial, internal disposition, or agent
self-review. Its reader contract records the promised question, exact early answer, and useful
takeaway. When a practical implication is supported, that implication and the takeaway are identical.

A mechanically valid article may still fail human review because it is dull, inward-looking,
over-technical, poorly framed, or offers no reader value.

Evidence-supported practical guidance is permitted when the outcome is measurable, sources and
conditions are explicit, the advice does not outrun the evidence, it is framed as a bounded
diagnostic or experiment, and confounders are stated. Recording first-drip time or interpreting a
pressure reading at its physical location can be useful under repeated conditions; neither is a
universal quality target. Affiliate or sponsored recommendations, product rankings, endorsements,
purchasing instructions, objectively best recipes, unsupported taste or flavor predictions,
chemical-to-preference translation, and universal grinder, pressure, or shot-time settings remain
prohibited.

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
three review gate flags true, record `human_approved: true`, and include `approved_at`.
`style_gate_passed` is Tim Brewer's human editorial decision. Automated tools may check mechanical
hazards but cannot set or imply that the title, voice, pacing, framing, or usefulness is right. Only a
human may set `published`, record public URLs, approve corrections or claim-ceiling changes, send email,
submit to Medium, or press Publish.

## Figures, notes, and short form

Prefer verified SVG line art or PNG at least 1,600 pixels wide, plus 1,200×630 previews where needed.
Record generating script, committed source data, output checksum, run, applicability, and limitation.
Alt text names chart type, axes and units, groups, trend, uncertainty encoding, and the visual
conclusion. Figures are never manually altered, selectively cropped, or stripped of uncertainty.
Static fallbacks accompany interactive material. Code excerpts are at most 20 lines and link to exact
files/commits.

Every figure output must exist and match its SHA-256. Figure evidence IDs must resolve. Its generating
script must be a safe repository-relative regular file in the checked-out puckworks repository. Each
source-data path must either be a checked-out regular file or match a cited evidence artifact already
validated at its exact repository commit. Absolute paths, parent traversal, missing output, dangling
IDs, uncited historical inputs, unbound sources, and checksum mismatches are fatal. Draft evidence,
claim, and figure IDs and evidence-ledger evidence and claim IDs must each be unique.

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
A Medium variant cannot validate as `ready` unless Tim's gates pass and
`substantive_human_rewrite_medium: true` is explicitly recorded.

Reminder synchronization is credential-free and dry-run by default. `--issues-json PATH` supplies a
local issue-state array; without it, planning uses an empty list and warns that remote deduplication
was not evaluated. Applying mutations requires explicit `--apply` and GitHub credentials, or the
workflow's enabled scheduled apply path. Once the earliest reminder threshold is reached, a
nonterminal item remains due even after its draft and publication dates. Schedule issues use the exact
`<!-- publishing-schedule-id: ID -->` marker; digests use
`<!-- publishing-editorial-digest: YYYY-MM-DD -->`. Automation owns only the exact unkeyed
`<!-- publishing-managed:start -->` through `<!-- publishing-managed:end -->` region. Updates preserve
human text outside it and suppress PATCH requests when governed content, labels, title, and state are
unchanged. Dry runs perform no network access or writes.

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

## Repository layout

```text
content/
├── drafts/YYYY-MM-DD-slug.md
├── variants/YYYY-MM-DD-slug.{substack,medium}.md
├── notes/YYYY-Www.md
├── evidence/YYYY-MM-DD-slug.yml
├── triggers/TRIGGER-ID.yml
├── published/YYYY-MM-DD-slug.yml
└── schedule.yml
docs/publishing/{PUBLISHING_SYSTEM.md,STYLE_GUIDE.md,PLATFORM_CHECKLIST.md,README.md}
tools/publishing/{scan_triggers.py,validate_draft.py,validate_evidence.py,
validate_schedule.py,build_variants.py,generate_editorial_digest.py,
check_canonical.py,sync_editorial_issues.py}
.github/workflows/editorial-reminders.yml
```

## Complete trigger schema

```yaml
schema_version: 1
trigger_id: PW-PUB-YYYY-NNN
publication_trigger: true
source:
  repository: puckworks | espresso-whole-pull
  event_type: tagged_release | milestone_closed | dataset_added | validation_completed | hypothesis_updated | correction | blocked_result | public_explainer
  identifier: "release:v0.0.0 | issue:#123 | run:RUN-ID | commit:FULL_SHA"
  source_url: null
  detected_at: "YYYY-MM-DDTHH:MM:SSZ"
scientific_state:
  disposition: "EXACT_CONTROLLING_DISPOSITION"
  claim_ceiling_path: "relative/path/to/claim/ceiling"
  project_state_path: "relative/path/to/project/state"
  evidence_level: independent | post_fit | calibration | verification | descriptive | exploratory | qualitative | mixed
  hypothesis_ids: []
  changes_claim_ceiling: false
recommended_content:
  archetype: finding_report | myth_check | innovation_review | practical_guide | behind_model | data_release | correction
  provisional_title: ""
  public_value_summary: ""
  urgency: routine | timely | correction
  target_platforms: [substack, medium]
artifacts:
  - repository: puckworks
    path: "relative/path"
    commit_sha: "FULL_40_CHARACTER_SHA"
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    purpose: "What this artifact establishes"
stop_reasons: []
owner_notes: ""
```

## Complete master frontmatter schema

```yaml
---
schema_version: 2
title: ""
subtitle: ""
slug: ""
archetype: finding_report | myth_check | innovation_review | practical_guide | behind_model | data_release | correction
status: draft | evidence_review | human_review | ready | published | withdrawn
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
author: "Tim Brewer"
target_platforms: [substack, medium]
primary_platform: substack
target_length_words: {minimum: 1200, preferred: 1500, maximum: 1800}
reader_contract:
  question: ""
  answer: ""
  takeaway: ""
source_event:
  trigger_id: "PW-PUB-YYYY-NNN"
  repository: puckworks | espresso-whole-pull
  event_type: ""
  identifier: ""
claim_ceiling:
  repository: ""
  path: ""
  commit_sha: "FULL_40_CHARACTER_SHA"
  exact_status: ""
source_artifacts:
  - evidence_id: E1
    repository: puckworks | espresso-whole-pull | external-paper
    path: null
    commit_sha: null
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: independent | post_fit | calibration | verification | descriptive | exploratory | qualitative | mixed
    establishes: ""
    does_not_establish: ""
figures:
  - figure_id: F1
    source_script: ""
    source_data: [""]
    output_path: ""
    output_sha256: ""
    caption: ""
    alt_text: ""
    evidence_ids: [E1]
    regenerated_at: ""
    hand_edited: false
claims:
  - claim_id: C1
    text: ""
    evidence_ids: [E1]
    conditions: ""
    evidence_level: ""
    applicability: ""
    caveat: ""
    quantitative: false
uncertainty:
  numerical: ""
  measurement: ""
  parameter: ""
  model_form: ""
  identifiability: ""
  external_validity: ""
  largest_remaining_uncertainty: ""
  next_discriminating_measurement: ""
practical_implication:
  supported: false
  text: ""
  conditions: ""
  prohibited_overreach: ""
ai_assistance:
  used: true
  tool_role: [evidence_assembly, outline, draft, copy_edit]
  human_reviewer: null
  scientific_claims_checked: false
  numbers_checked: false
  citations_checked: false
  figures_checked: false
  substantive_human_rewrite_medium: false
  disclosure_substack: "Drafting note: I used AI assistance to prepare and edit this article from the linked repository materials. I checked every scientific claim, number, citation, and figure before publication."
  disclosure_medium: "Disclosure: I used an AI writing tool to help draft and edit this article from the linked repository materials. I personally checked every scientific claim, number, citation, and figure."
cross_posting:
  substack: {planned: true, send_email: true, publication_date: null, url: null}
  medium: {planned: true, publication_name: null, publication_date: null, publish_not_before: null, url: null}
  canonical_url: null
  canonical_verified: false
review:
  evidence_gate_passed: false
  style_gate_passed: false
  platform_gate_passed: false
  human_approved: false
  approved_at: null
---
```

## Archetype narrative properties

Archetypes guide emphasis rather than impose a heading template. Finding reports lead with what was
observed and distinguish measurement, fitted reproduction, prediction, and inference. Myth checks
state the strongest reasonable claim and one governed verdict. Innovation reviews explain mechanism,
direct evidence, alternatives, the decisive missing experiment, and non-endorsement. Practical guides
define a measurable goal, controls, confounders, and bounded action. Behind-the-model articles explain
one physical idea and its limits without becoming software documentation. Data releases explain
source, rights, quality, permitted uses, and material errors. Corrections identify the old and revised
statements and link both ways. All finish with compact sources and technical notes plus disclosure.

## Automated evidence gate checklist

Source closure requires eligible activation, path-at-commit resolution, full SHAs, resolvable event
identities, complete citations and rights, the current claim ceiling, and absence of superseding
corrections. Traceability requires every quantitative and qualitative conclusion to map to evidence,
units and conditions, value-type distinctions, no validation-label upgrade, and no chemical-to-taste
inference. Titles, subtitles, openings, captions, and takeaways remain within the exact ceiling and H1
stays a hypothesis unless controlling evidence explicitly changes it. Commercial neutrality excludes
affiliate, payment, sponsorship, ranking, endorsement, and purchase language. Limitations name the
largest uncertainty, external validity, next measurement, null/adverse results, and alternatives.
Figures are regenerated from committed inputs, script/data/checksum bound, unedited, accurately
captioned and described, and have static fallbacks. Any failed box is a fatal readiness stop.

## Human sign-off contract

```yaml
status: ready
ai_assistance:
  human_reviewer: "Tim Brewer"
  scientific_claims_checked: true
  numbers_checked: true
  citations_checked: true
  figures_checked: true
review:
  evidence_gate_passed: true
  style_gate_passed: true
  platform_gate_passed: true
  human_approved: true
  approved_at: "YYYY-MM-DDTHH:MM:SSZ"
```

## Figure and Note templates

Figure captions use: `**Figure N. [Plain-language result].** Generated by
path/to/script.py from path/to/data.csv at commit FULL_SHA, run RUN_ID. [Applicability or
limitation.]` Alt text states chart type, both axes and units, compared groups or curves, principal
trend, uncertainty encoding, and key visual conclusion; “plot”, “graph”, or “figure showing results”
alone is never adequate.

A Figure Note is 80–160 words and at most 900 characters before links: one observation, one paragraph
explaining axes/conditions/value, one explicit limitation, and one source. An Observation Note is
60–120 words and at most 700 characters before links, explaining one change, failure, or clarification.
A Reader-question Note is 30–80 words and at most 450 characters, supplies enough context, and asks
exactly one question without treating anecdotes as representative evidence.

## Backstage editorial review questions

Reviewers may use these questions outside the public body:

1. What is the narrowest exact claim this evidence supports?
2. Does the title claim more than the body?
3. Does any sentence turn calibration or reconstruction into validation?
4. Does any number lack a path, commit, run, issue, or paper?
5. Have I confused chemical composition with taste?
6. Have I generalized beyond the tested coffee, grinder, machine, basket, pressure, or laboratory?
7. Have I hidden a null, adverse, or superseded result?
8. Is the principal limitation stated before the reader reaches the end?
9. Could the practical takeaway imply a product endorsement?
10. Have I represented a community belief charitably?
11. Is every figure regenerated and unedited?
12. Does each caption state what the figure does not prove?
13. Is the AI disclosure correct for the platform?
14. Does Medium contain substantive first-hand human reasoning?
15. Can a skeptical researcher locate the evidence without asking?
16. Can a home brewer understand what, if anything, to do differently?
17. What measurement would most efficiently change the conclusion?
18. Is the article worth publishing, or merely evidence that work occurred?

## Platform references

Re-check current platform behavior when material:

- <https://support.substack.com/hc/en-us/articles/14564821756308-Getting-started-on-Substack-Notes>
- <https://support.substack.com/hc/en-us/articles/5036794583828-How-can-I-recommend-other-publications-on-Substack>
- <https://support.substack.com/hc/en-us/articles/360037831771-How-do-I-publish-a-new-post-on-Substack>
- <https://support.substack.com/hc/en-us/articles/50891130623508-How-can-I-detect-AI-on-Substack>
- <https://help.medium.com/hc/en-us/articles/360006362473-Medium-s-Distribution-Guidelines-How-curators-review-stories-for-Boost-General-and-Network-Distribution>
- <https://help.medium.com/hc/en-us/articles/22576852947223-Artificial-Intelligence-AI-content-policy>
- <https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link>
- <https://help.medium.com/hc/en-us/articles/115004747067-Your-profile-page>

Platform documentation never overrides the evidence rules, non-commercial constraint, or
manual-publication boundary.
