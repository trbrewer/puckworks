---
schema_version: 1
title: "What puckworks is for"
subtitle: "A research workspace for comparing espresso models without pretending they already form one validated answer."
slug: what-puckworks-is-for
archetype: behind_model
status: human_review
created_at: "2026-08-28T18:01:53Z"
updated_at: "2026-08-28T18:01:53Z"
author: Tim Brewer
primary_platform: substack
target_platforms:
  - substack
  - medium
target_length_words:
  minimum: 1500
  preferred: 1900
  maximum: 2400
source_event:
  trigger_id: PW-PUB-2026-002
  repository: puckworks
  event_type: public_explainer
  identifier: commit:dfe0bdc761574e3327fa96f1d84e8199e156c192
claim_ceiling:
  repository: puckworks
  path: docs/publishing/PUBLISHING_SYSTEM.md
  commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
  exact_status: "H1 is not a standing conclusion and has not been confirmed; no universal whole-process physical validation has been established."
source_artifacts:
  - evidence_id: E1
    repository: puckworks
    path: docs/publishing/PUBLISHING_SYSTEM.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the publication purpose, H1 wording, current-state precedence, evidence rules, non-commercial boundary, and human-publication boundary
    does_not_establish: that H1 is true, that any model is physically validated, or that an article has been approved
  - evidence_id: E2
    repository: puckworks
    path: README.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: Puckworks as an open research toolkit that keeps models as separate testable modules
    does_not_establish: arbitrary model compatibility, universal validation, or scientific correctness of every component
  - evidence_id: E3
    repository: puckworks
    path: docs/PAPER_3_PUCKWORKS_DRAFT.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the typed-contract, provenance, evidence-relation, selected-composition, and refusal architecture, including implemented-versus-intended limitations
    does_not_establish: peer-reviewed acceptance, detection of every semantic error, or universal valid composition
  - evidence_id: E4
    repository: puckworks
    path: docs/status/current.json
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the canonical machine-readable project state at the cited commit
    does_not_establish: physical validation merely because an implementation, test, or release state is complete
  - evidence_id: E5
    repository: puckworks
    path: docs/CURRENT.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: which current artifacts control project claims and status
    does_not_establish: any scientific result independently of those controlling artifacts
  - evidence_id: E6
    repository: puckworks
    path: content/schedule.yml
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the planned article identity, archetype, owner, platform sequence, and dates
    does_not_establish: human approval or publication
  - evidence_id: E7
    repository: espresso-whole-pull
    path: README.md
    commit_sha: 3874865e124dba0340ca93626b9bbf80f1385664
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the repository's actual current role in model development, simulation, and evidence generation
    does_not_establish: a completed grinder-to-cup model or validation of H1
  - evidence_id: E8
    repository: espresso-whole-pull
    path: docs/validation/sci_ed_002/RESULT.json
    commit_sha: 3874865e124dba0340ca93626b9bbf80f1385664
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: the exact current commissioning blocker and prohibited downstream claims
    does_not_establish: that H1 is false or that the proposed experiment would necessarily resolve every model ambiguity
  - evidence_id: E9
    repository: puckworks
    path: docs/public/README.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    issue_number: null
    pull_request_number: null
    release_tag: null
    run_id: null
    sha256: null
    paper_citation: null
    evidence_level: descriptive
    establishes: that the public layer presents producer-bound claims and evidence without becoming a physics model
    does_not_establish: additional scientific validation
figures: []
claims:
  - claim_id: C1
    text: "Puckworks is an open research toolkit that keeps published espresso models as separate, inspectable components rather than forcing them into one all-purpose model."
    evidence_ids: [E2, E3]
    conditions: current architecture, registry, and source descriptions at the cited Puckworks commit
    evidence_level: descriptive
    applicability: the current Puckworks architecture and registered components at the cited commit
    caveat: registration does not itself establish correctness, compatibility, rights clearance, or validation.
    quantitative: false
  - claim_id: C2
    text: "Puckworks records assumptions, observable meanings, units, applicability, provenance, and evidence relations so that model comparisons and selected compositions can be inspected."
    evidence_ids: [E2, E3, E9]
    conditions: current contracts, model and source cards, evidence records, and public claim layer
    evidence_level: descriptive
    applicability: implemented current contracts and explicitly supported configurations
    caveat: the architecture does not guarantee detection of every semantic error and does not synthesize arbitrary component combinations.
    quantitative: false
  - claim_id: C3
    text: "A scientifically unsupported composition may be refused or preserved as a blocked result rather than converted into a convenient combined answer."
    evidence_ids: [E3, E4]
    conditions: use of the current contract, evidence, and selected-composition machinery
    evidence_level: descriptive
    applicability: configurations evaluated through the current contract and evidence machinery
    caveat: refusal by the software is not proof that no scientifically valid formulation could ever exist.
    quantitative: false
  - claim_id: C4
    text: "H1 is the programme's central hypothesis, but it is not a standing conclusion and has not been confirmed by the current controlling record."
    evidence_ids: [E1, E4, E8]
    conditions: no superseding controlling authority beyond the exact cited commits
    evidence_level: descriptive
    applicability: the exact current Puckworks and espresso-whole-pull authority cited by the article
    caveat: absence of confirmation is not evidence that H1 is false.
    quantitative: false
  - claim_id: C5
    text: "Puckworks and espresso-whole-pull have complementary roles: the former organizes models and evidence contracts, while the latter develops and tests mechanisms and the measurements needed to discriminate them."
    evidence_ids: [E2, E3, E7, E8]
    conditions: current documented scopes and the present blocked measurement lane
    evidence_level: descriptive
    applicability: the current scope of both repositories
    caveat: neither repository currently establishes a universally validated grinder-to-cup model.
    quantitative: false
  - claim_id: C6
    text: "The current espresso-whole-pull commissioning lane remains blocked because its reference-extractability stopping rule has not been defensibly frozen."
    evidence_ids: [E8]
    conditions: the exact current machine-readable SCI-ED-002 result
    evidence_level: descriptive
    applicability: the exact current SCI-ED-002 authority
    caveat: the blocker prevents the authorized commissioning and downstream claims; it does not adjudicate H1.
    quantitative: false
  - claim_id: C7
    text: "The linked demonstrations and public interfaces are explanatory research tools, not evidence of a universally validated coupled espresso simulation."
    evidence_ids: [E2, E3, E4, E9]
    conditions: current public experiences, selected compositions, and producer-bound public claims
    evidence_level: descriptive
    applicability: current public experiences and supported configurations
    caveat: individual components retain distinct evidence levels and applicability limits.
    quantitative: false
  - claim_id: C8
    text: "The Puckworks publication is free and non-commercial and does not provide taste prediction, product ranking, purchasing advice, or endorsement."
    evidence_ids: [E1]
    conditions: the governing publication system remains controlling
    evidence_level: descriptive
    applicability: the governing publication system
    caveat: future articles may discuss physical controls only within their evidence and applicability limits.
    quantitative: false
  - claim_id: C9
    text: "This launch article reports no new simulation, experiment, parameter estimate, calibration, or physical-validation result."
    evidence_ids: [E1, E4, E6]
    conditions: the bounded PW-PUB-002 content task and its exact-commit repository review method
    evidence_level: descriptive
    applicability: PW-PUB-002
    caveat: it describes the current evidence system and programme state rather than resolving the open scientific questions.
    quantitative: false
uncertainty:
  numerical: no new numerical result is reported
  measurement: no new measurement is reported
  parameter: no new parameter estimate is reported
  model_form: individual registered models retain their own model-form limitations
  identifiability: H1 and competing mechanisms remain insufficiently discriminated
  external_validity: model and evidence applicability remains bounded by the recorded conditions
  largest_remaining_uncertainty: lack of eligible discriminating experimental evidence
  next_discriminating_measurement: a defensibly commissioned measurement programme with a frozen reference-extractability stopping rule and prespecified observables
practical_implication:
  supported: false
  text: no new practical recommendation is made
  conditions: none; this article is descriptive
  prohibited_overreach: no recipe, taste, ranking, purchasing, or endorsement claim
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
  evidence_gate_passed: true
  style_gate_passed: true
  platform_gate_passed: false
  human_approved: false
  approved_at: null
---

## Result or question in one sentence

Puckworks is for keeping espresso models, evidence, assumptions, and limits connected closely enough that a useful comparison can be inspected—and an invalid one can be refused.

## Why this matters

Espresso looks like one event at the cup, but it is governed by several physical processes happening together. Grinding sets a distribution of particle sizes. Water wets an initially dry porous bed, finds routes through it, and carries soluble material away while the puck itself can swell, compact, or rearrange. What reaches the cup is the accumulated consequence of all those overlapping processes.

Published models usually examine only part of that chain. That is sensible: a model becomes useful by leaving things out deliberately. The difficulty begins when two models leave out different things, define their outputs differently, or place their boundaries at different physical locations.

Two curves can look remarkably compatible while describing different observables. A pressure may refer to the pump outlet, the space above the puck, or the drop across the wet coffee bed. An extraction quantity may use total roasted content, operationally extractable material, or a model-specific inventory as its basis. Matching units and tidy file formats do not make those meanings interchangeable.

A linked simulation can therefore look cleaner as it becomes less defensible. The arithmetic may run while the scientific hand-off has quietly failed. Puckworks exists to make those hand-offs inspectable.

## Question or hypothesis

Water reaches chemical equilibrium with the extractable soluble material before it is flushed from the puck.

That is H1, the programme's central hypothesis. It is a hypothesis, not a result.

If sufficiently supported, H1 would change how I interpret the relationship between hydraulic controls and extraction kinetics. A pressure or flow change might alter what is collected mainly by changing flushing and inventory access, rather than by controlling a slow approach to chemical equilibrium. But several mechanisms can produce similar whole-cup observations. Without measurements designed to distinguish them, a plausible explanation remains one explanation among others.

The current record has neither confirmed nor rejected H1. That open status is not coyness. It is the scientifically useful answer available now.

## Evidence box

- Puckworks repository: `https://github.com/trbrewer/puckworks.git`
- Puckworks commit: `dfe0bdc761574e3327fa96f1d84e8199e156c192`
- espresso-whole-pull repository: `https://github.com/trbrewer/espresso-whole-pull.git`
- espresso-whole-pull commit: `3874865e124dba0340ca93626b9bbf80f1385664` (`origin/main` at review)
- Publication trigger: `content/triggers/PW-PUB-2026-002.yml`
- Primary claim ceiling: `docs/publishing/PUBLISHING_SYSTEM.md`
- Current project state: `docs/status/current.json`
- Current blocker artifact: `docs/validation/sci_ed_002/RESULT.json`
- Current blocker: `SCI_ED_002_PROTOCOL_INCOMPLETE_COMMISSIONING_BLOCKED_REFERENCE_EXTRACTABILITY_STOPPING_RULE_NOT_DEFENSIBLY_FROZEN`
- Evidence level: descriptive
- Figures: none
- New scientific execution: none

## Method

I prepared this article as an exact-commit repository and evidence review. I first resolved the current authority in each repository. I then identified their stated scope and limitations, mapped each public claim to a cited artifact, and checked the wording against the governing claim ceiling.

The review treats adverse, blocked, and unresolved states as evidence about the boundary of what may be said. It does not turn a completed implementation, a passing software test, or an attractive demonstration into physical validation.

I ran no new numerical experiment, data analysis, model fit, or validation run for this article. Its result is a bounded description of the research system and its current scientific state.

## Result

Puckworks is a model library and research toolkit, not one universal espresso model. It keeps separately defined components available as alternatives, references, or selected parts of explicit configurations. Each component can retain its own assumptions, applicable conditions, source history, evidence relationship, and limitations.

The practical core is a set of typed meanings and boundaries. Here, “typed” means that a hand-off names what a value represents rather than treating every compatible-looking number as the same thing. Provenance records where a value or model came from. Evidence labels record what kind of comparison supports a claim. Applicability records where that support can reasonably travel.

Pressure gives a simple example. Two pressure values may carry the same units but refer to different physical locations. Subtracting a pipe loss from a basket-pressure measurement as though it were a pump-outlet measurement can count the same resistance twice. Puckworks provides named pressure locations and can refuse a hand-off when location identity is absent or wrong. It cannot guarantee that a human or an adapter has never assigned a plausible value to the wrong named field.

The same caution applies to soluble inventory. Total material present in roasted coffee is not automatically the material extractable by a defined procedure, and neither is automatically the initial inventory required by a simulation. A unit conversion cannot supply the missing physical relationship.

Selected links between components can be written, reviewed, and run. Unsupported links can remain blocked. Competing branches are kept separate rather than averaged into a smoother answer. Public claim records can then expose the producer, evidence relation, conditions, and caveat behind an explanation without turning the presentation layer into another physics model.

## Interpretation

The system is useful because it makes disagreement and missing information visible. That may sound less exciting than a single grinder-to-cup prediction. It is also much harder to fool with a polished curve.

A blocked composition can be more informative than an unsupported prediction. It identifies the definition, adapter, measurement, or evidence relationship that is missing. A negative result can rule out one particular formulation without pretending to rule out the entire physical mechanism. Preserving both outcomes narrows the space in which a better explanation must live.

Provenance and evidence classification do different jobs. Provenance answers where a value, dataset, model, or transformation came from. Evidence classification answers what relationship it has to an equation, a fitted dataset, a held-out condition, or an independent measurement. A value can have impeccable provenance and still be weak evidence for the claim at hand. A promising measurement can be scientifically relevant but unusable if its definition or lineage is unclear. I need both records.

Puckworks and espresso-whole-pull play complementary roles. Puckworks organizes models, their interfaces, and evidence-bearing claims. Espresso-whole-pull develops and tests whole-puck mechanisms and the measurement programmes needed to discriminate them. The boundary is not a claim that all ideas live neatly in one repository. It describes their current documented emphases and how evidence can move between them without being upgraded in transit.

## What this does not show

This work does not establish H1. It does not establish a universal whole-process model, independent physical validation of every registered component, or automatic compatibility among components. A registration entry says that a model can be identified and inspected; it does not certify correctness.

The linked demonstrations and public interfaces are explanatory research tools. They are not a validated coupled espresso simulator. They do not predict taste, flavor, preference, or product quality. They do not identify a best recipe, translate a grinder dial reliably between grinders, or support a purchasing decision or commercial endorsement.

The software gates also do not detect every possible semantic error. They make specified errors visible and testable. Human scientific judgment remains part of deciding whether two quantities, models, and evidence records can support the same claim.

## Uncertainty and limitations

No new numerical, measurement, or parameter uncertainty was evaluated here because no new scientific result was produced. That is different from saying those uncertainties are zero. Each registered component retains its own numerical behavior, parameter provenance, model-form limits, and experimental domain.

Some semantic and evidence judgments remain human-curated. Rights add a separate boundary: permission to execute code publicly and permission to publish its outputs can differ. Evidence strength is uneven across process stages, and a strong result for one observable does not automatically support another.

Identifiability remains a central limitation. Different mechanisms can be observationally equivalent when only the collected endpoint is measured. External validity is bounded by the coffee, apparatus, conditions, and measurement definitions actually represented in the evidence.

The current commissioning lane is blocked because the operational reference-extractability stopping rule has not been defensibly frozen. Consequently there are no authorized commissioning measurements, no trained or accepted predictor, no replay of the dependent inventory analysis, no established `c_s0` mapping, and no physical-validation claim from that lane. This blocker does not decide H1.

The largest remaining uncertainty is the lack of eligible, discriminating experimental evidence. Better prose cannot substitute for it.

## What evidence would change the conclusion

Stronger claims would begin with a defensibly frozen reference-extractability protocol, including prespecified observables and stopping rules. That protocol would need successful commissioning and independently interpretable measurements whose definitions close against the model quantities being compared.

Competing models should make explicit predictions before those measurements are opened for comparison. The comparison must remain eligible under its frozen rules, including adverse or null outcomes. Repeatability would show whether the result survives repetition within its setting. Transferability evidence would be needed before moving beyond that setting.

Stronger claims about linked models would also require explicit compatible multi-stage configurations and validation directed at those configurations. Validation of individual parts does not simply accumulate into validation of their composition.

Such evidence could strengthen, weaken, or reject particular hypotheses. I do not know in advance which outcome it will support. That is the point of making the measurement discriminating.

## How to reproduce or inspect the result

The following commands inspect the exact evidence states without credentials or platform access:

```bash
git clone https://github.com/trbrewer/puckworks.git
git -C puckworks checkout dfe0bdc761574e3327fa96f1d84e8199e156c192
git -C puckworks show dfe0bdc761574e3327fa96f1d84e8199e156c192:docs/publishing/PUBLISHING_SYSTEM.md
git -C puckworks show dfe0bdc761574e3327fa96f1d84e8199e156c192:docs/status/current.json

git clone https://github.com/trbrewer/espresso-whole-pull.git
git -C espresso-whole-pull checkout 3874865e124dba0340ca93626b9bbf80f1385664
git -C espresso-whole-pull show 3874865e124dba0340ca93626b9bbf80f1385664:docs/validation/sci_ed_002/RESULT.json
```

After checking out the article branch, these commands inspect and validate the publication artifacts:

```bash
git -C puckworks show content/pw-pub-002-what-puckworks-is-for:content/triggers/PW-PUB-2026-002.yml
git -C puckworks show content/pw-pub-002-what-puckworks-is-for:content/evidence/2026-09-08-what-puckworks-is-for.yml
cd puckworks
python -m tools.publishing.validate_evidence --espresso-repo ../espresso-whole-pull content/triggers/PW-PUB-2026-002.yml content/evidence/2026-09-08-what-puckworks-is-for.yml
python -m tools.publishing.validate_draft --espresso-repo ../espresso-whole-pull content/drafts/2026-09-08-what-puckworks-is-for.md
python -m tools.publishing.validate_schedule content/schedule.yml
```

## Claims-to-evidence table

| Claim ID | Exact claim | Evidence IDs | Evidence level | Applicability or conditions | Caveat |
|---|---|---|---|---|---|
| C1 | Puckworks is an open research toolkit that keeps published espresso models as separate, inspectable components rather than forcing them into one all-purpose model. | E2, E3 | descriptive | Conditions: current architecture, registry, and source descriptions at the cited Puckworks commit. Applicability: the current Puckworks architecture and registered components at the cited commit. | registration does not itself establish correctness, compatibility, rights clearance, or validation. |
| C2 | Puckworks records assumptions, observable meanings, units, applicability, provenance, and evidence relations so that model comparisons and selected compositions can be inspected. | E2, E3, E9 | descriptive | Conditions: current contracts, model and source cards, evidence records, and public claim layer. Applicability: implemented current contracts and explicitly supported configurations. | the architecture does not guarantee detection of every semantic error and does not synthesize arbitrary component combinations. |
| C3 | A scientifically unsupported composition may be refused or preserved as a blocked result rather than converted into a convenient combined answer. | E3, E4 | descriptive | Conditions: use of the current contract, evidence, and selected-composition machinery. Applicability: configurations evaluated through the current contract and evidence machinery. | refusal by the software is not proof that no scientifically valid formulation could ever exist. |
| C4 | H1 is the programme's central hypothesis, but it is not a standing conclusion and has not been confirmed by the current controlling record. | E1, E4, E8 | descriptive | Conditions: no superseding controlling authority beyond the exact cited commits. Applicability: the exact current Puckworks and espresso-whole-pull authority cited by the article. | absence of confirmation is not evidence that H1 is false. |
| C5 | Puckworks and espresso-whole-pull have complementary roles: the former organizes models and evidence contracts, while the latter develops and tests mechanisms and the measurements needed to discriminate them. | E2, E3, E7, E8 | descriptive | Conditions: current documented scopes and the present blocked measurement lane. Applicability: the current scope of both repositories. | neither repository currently establishes a universally validated grinder-to-cup model. |
| C6 | The current espresso-whole-pull commissioning lane remains blocked because its reference-extractability stopping rule has not been defensibly frozen. | E8 | descriptive | Conditions: the exact current machine-readable SCI-ED-002 result. Applicability: the exact current SCI-ED-002 authority. | the blocker prevents the authorized commissioning and downstream claims; it does not adjudicate H1. |
| C7 | The linked demonstrations and public interfaces are explanatory research tools, not evidence of a universally validated coupled espresso simulation. | E2, E3, E4, E9 | descriptive | Conditions: current public experiences, selected compositions, and producer-bound public claims. Applicability: current public experiences and supported configurations. | individual components retain distinct evidence levels and applicability limits. |
| C8 | The Puckworks publication is free and non-commercial and does not provide taste prediction, product ranking, purchasing advice, or endorsement. | E1 | descriptive | Conditions: the governing publication system remains controlling. Applicability: the governing publication system. | future articles may discuss physical controls only within their evidence and applicability limits. |
| C9 | This launch article reports no new simulation, experiment, parameter estimate, calibration, or physical-validation result. | E1, E4, E6 | descriptive | Conditions: the bounded PW-PUB-002 content task and its exact-commit repository review method. Applicability: PW-PUB-002. | it describes the current evidence system and programme state rather than resolving the open scientific questions. |

## AI-assistance disclosure

Drafting note: I used AI assistance to assemble the cited repository evidence and prepare an initial version of this article. Human scientific review of every claim, citation, and boundary is still required before publication.

## Agent self-review

*Removable editorial section; not publication copy.*

- Every public claim maps to evidence in the ledger and frontmatter: yes, pending Tim's inspection.
- The current claim ceiling is preserved: yes; H1 remains a hypothesis and no universal physical validation is asserted.
- Any unsupported quantitative claim remains: none identified; all governed article claims are non-quantitative.
- The repository roles are distinguished accurately: yes, as complementary current emphases rather than an absolute organizational division.
- The commissioning blocker is preserved: yes, including its downstream prohibitions and its non-adjudication of H1.
- Commercial, taste, ranking, and purchasing language is excluded as advice or prediction: yes; these categories appear only as explicit non-goals.
- Any phrase could be mistaken for universal validation: none identified, but Tim should review the descriptions of selected linking and public interfaces closely.
- Remaining questions for Tim: Does the first-person explanation match your intended public voice? Is the distinction between operational reference extractability and model inventory plain enough? Does the complementary-repository description match how you want future work introduced? Should any technical term be simplified before variant work begins?

Human scientific review is not complete.
