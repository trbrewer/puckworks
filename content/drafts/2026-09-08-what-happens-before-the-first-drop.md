---
schema_version: 2
title: "What happens before the first drop of espresso?"
subtitle: "That quiet pause is when water is filling the puck, compressing trapped air, and finding a path to the cup."
slug: what-happens-before-the-first-drop
archetype: finding_report
status: ready
created_at: "2026-08-28T19:36:41Z"
updated_at: "2026-08-28T20:24:44Z"
author: Tim Brewer
primary_platform: substack
target_platforms: [substack, medium]
target_length_words:
  minimum: 900
  preferred: 1150
  maximum: 1400
reader_contract:
  question: "What happens inside the puck before the first drop of espresso appears?"
  answer: "Before the first drop appears, water is invading an initially dry puck, filling connected pore space, and building a path to the basket."
  takeaway: "Record time to first drip as a diagnostic of puck filling under repeated conditions, not as a universal target for taste or extraction."
source_event:
  trigger_id: PW-PUB-2026-002
  repository: puckworks
  event_type: public_explainer
  identifier: commit:40246bb3a5dbee3be2b539251c5191584666ecdd
claim_ceiling:
  repository: puckworks
  path: docs/publishing/PUBLISHING_SYSTEM.md
  commit_sha: 40246bb3a5dbee3be2b539251c5191584666ecdd
  exact_status: "The article may explain the cited wetting and first-drip evidence within its stated conditions; it does not establish a universal first-drip target, taste outcome, or universally validated whole-process espresso model."
source_artifacts:
  - evidence_id: E1
    repository: external-paper
    path: null
    commit_sha: null
    paper_citation: "J. Foster, W. Lee, K. Moroney, D. Prjamkov, M. Salamon, A. Smith, J. Petrassem-de-Sousa, and M. Vynnycky, ‘Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling,’ Physics of Fluids 37, 013383 (2025). DOI: 10.1063/5.0245167."
    evidence_level: mixed
    establishes: direct time-resolved observation of infiltration in the stated configurations, fine-grind wetting-front behavior, coarse-grind non-uniformity, and the source model and its calibration
    does_not_establish: a universal wetting pattern, parameter-free validation of the fitted source model, a universal first-drip target, taste, or extraction quality
  - evidence_id: E2
    repository: puckworks
    path: docs/cards/foster2025_2.md
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    paper_citation: null
    evidence_level: mixed
    establishes: the implementation scope, source assumptions, current status, fine/coarse observations, fitted-model interpretation, first-drip reference, and current limits
    does_not_establish: peer review of the Puckworks implementation, universal physical validation, coarse-grind applicability of the sharp-front model, or a taste optimum
  - evidence_id: E3
    repository: puckworks
    path: puckworks/validation/gates.py
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    paper_citation: null
    evidence_level: verification
    establishes: the executable first-drip gate computation, explicit observed crossing, predicted bracket construction, stated porosity endpoints, and pass criterion
    does_not_establish: independence from the evaluated shot, portability to another fixture, an ideal first-drip time, or taste quality
  - evidence_id: E4
    repository: puckworks
    path: docs/publishing/PUBLISHING_SYSTEM.md
    commit_sha: 40246bb3a5dbee3be2b539251c5191584666ecdd
    paper_citation: null
    evidence_level: descriptive
    establishes: the reader-first public-copy rules, internal evidence requirements, practical-guidance boundary, and human editorial gate
    does_not_establish: any wetting physics independently
  - evidence_id: E5
    repository: puckworks
    path: puckworks/data/de1_fixtureA.json
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    paper_citation: null
    evidence_level: post_fit
    establishes: the exact fixture inputs, recorded pressure and weight traces, fitted permeability multiplier, and observation context consumed by the first-drip gate
    does_not_establish: a held-out or universally transferable first-drip prediction
  - evidence_id: E6
    repository: puckworks
    path: puckworks/paper3/EVIDENCE_LINKS.json
    commit_sha: dfe0bdc761574e3327fa96f1d84e8199e156c192
    paper_citation: null
    evidence_level: mixed
    establishes: the adjudicated same-campaign compatibility classification and that no parameter was tuned specifically to hit first-drip time
    does_not_establish: an independent parameter-free prediction because permeability and pressure came from the same evaluated shot
figures: []
claims:
  - claim_id: C1
    text: "Before the first drop appears, water is invading an initially dry puck, filling connected pore space, and building a path to the basket."
    evidence_ids: [E1, E2]
    conditions: physical description of the initial wetting and filling stage represented by the cited infiltration evidence
    evidence_level: mixed
    applicability: early shot behavior before liquid exits the basket
    caveat: real wetting can be spatially non-uniform, especially outside the cited fine-grind conditions
    quantitative: false
  - claim_id: C2
    text: "In the cited fine-grind experiment, the wetting front was sufficiently uniform for a one-dimensional sharp-front description, while the coarse-grind front was visibly non-uniform."
    evidence_ids: [E1, E2]
    conditions: the source experiment's stated coffee, grind ranges, apparatus, and imaging procedure
    evidence_level: mixed
    applicability: comparison of the source fine- and coarse-grind observations
    caveat: this does not establish that every fine grind wets uniformly or every coarse grind channels
    quantitative: false
  - claim_id: C3
    text: "The source model was calibrated against the same wetting data it reproduced, so the agreement supports the model form but is not a blind prediction."
    evidence_ids: [E1, E2, E6]
    conditions: the source model fit to its own wetting-front and headspace observations
    evidence_level: post_fit
    applicability: interpretation of the source model-data agreement
    caveat: a successful fitted reproduction does not establish parameter portability or independent physical validation
    quantitative: false
  - claim_id: C4
    text: "In a separate Puckworks check, a predicted first-drip window of 6.4–7.8 seconds contained the observed 7.0-second first drip on the stated DE1 fixture; no parameter was tuned to hit first-drip time itself."
    evidence_ids: [E2, E3, E5, E6]
    conditions: the exact fixture, recorded pressure and weight traces, fitted permeability multiplier, observation definition, porosity bracket, and gate rules
    evidence_level: mixed
    applicability: that fixture only
    caveat: permeability and pressure came from the same evaluated shot, so this is a same-campaign compatibility check rather than held-out validation and does not define an ideal time
    quantitative: true
  - claim_id: C5
    text: "Record time to first drip as a diagnostic of puck filling under repeated conditions, not as a universal target for taste or extraction."
    evidence_ids: [E1, E2, E3, E4, E5, E6]
    conditions: repeated shots with the same machine, basket, dose, preparation method, pressure or pre-infusion programme, and temperature as closely as practical
    evidence_level: mixed
    applicability: within-shot-development diagnostics
    caveat: first-drip time alone cannot identify the mechanism responsible for a change
    quantitative: false
  - claim_id: C6
    text: "A change in first-drip time can tell you that the hydraulic state changed, but it cannot by itself identify whether the cause was grind, packing, permeability, trapped air, pump behavior, or another mechanism."
    evidence_ids: [E1, E2, E3, E5, E6]
    conditions: interpretation of first-drip timing without additional spatial or hydraulic measurements
    evidence_level: mixed
    applicability: diagnostic use of first-drip timing
    caveat: identifying the cause requires controlled changes or additional measurements
    quantitative: false
uncertainty:
  numerical: exact timing uncertainty is limited to the cited measurement and gate records
  measurement: source imaging and first-drip definitions are apparatus-specific
  parameter: the source model fitted permeability, porosity, and time alignment; the separate fixture check used a fitted permeability multiplier
  model_form: the sharp-front model excludes non-uniform saturation and several puck-change mechanisms
  identifiability: first-drip time alone does not identify the responsible mechanism
  external_validity: evidence is bounded to the stated coffee, grind, apparatus, fixture, and pressure history
  largest_remaining_uncertainty: portability of the wetting and first-drip relationship across ordinary espresso preparations
  next_discriminating_measurement: synchronized pressure, flow, first-drip, and spatial wetting measurements across controlled grind and preparation changes
practical_implication:
  supported: true
  text: "Record time to first drip as a diagnostic of puck filling under repeated conditions, not as a universal target for taste or extraction."
  conditions: "Use repeated shots with machine, basket, dose, preparation, pressure or pre-infusion programme, and temperature held as consistently as practical."
  prohibited_overreach: "Do not infer an ideal taste, extraction, grind, pressure, or pre-infusion setting from first-drip time alone."
ai_assistance:
  used: true
  tool_role: [evidence_assembly, outline, draft, copy_edit]
  human_reviewer: Tim Brewer
  scientific_claims_checked: true
  numbers_checked: true
  citations_checked: true
  figures_checked: true
  substantive_human_rewrite_medium: false
  disclosure_substack: "Drafting note: I used AI assistance to organize the source material and prepare an initial draft. I reviewed the scientific claims and rewrote the final article before publication."
  disclosure_medium: "Disclosure: I used an AI writing tool to help organize source material and prepare an initial draft. I personally reviewed the scientific claims and rewrote the final article."
cross_posting:
  substack: {planned: true, send_email: true, publication_date: null, url: null}
  medium: {planned: true, publication_name: null, publication_date: null, publish_not_before: 2026-09-15, url: null}
  canonical_url: null
  canonical_verified: false
review:
  evidence_gate_passed: true
  style_gate_passed: true
  platform_gate_passed: true
  human_approved: true
  approved_at: "2026-08-28T20:24:44Z"
---

Press the brew button and the machine becomes noisy, but the cup remains stubbornly empty. That pause can look like dead time: pressure rises, a few seconds pass, and only then does espresso appear beneath the basket. Inside the puck, though, the shot is already under way.

Before the first drop appears, water is invading an initially dry puck, filling connected pore space, and building a path to the basket. The first drip is not the beginning of the shot. It is the first part of that hidden filling process that you can see.

That makes the pause useful. It carries information about how readily water entered the bed and found a connected route through it. It does not, by itself, tell you whether the coffee will taste good. Espresso would be much easier if one stopwatch reading could manage that.

## The pause is doing real work

A tamped puck is a porous bed: solid coffee particles threaded by small, connected spaces. At the start, many of those spaces contain air. Water entering from above has to displace or compress that air, wet the coffee surfaces, fill enough of the available space, and establish a route to the holes in the basket.

Several things overlap during this stage. The pump and any pre-infusion programme determine how water is supplied. The puck's permeability—how readily fluid can pass through it—depends on its particle structure and packing. Capillary forces help pull water into small spaces. Pressure develops as the bed resists the incoming flow. The puck may also change as it wets. A quiet cup therefore does not imply an inactive puck.

The useful mental picture is not a reservoir waiting to overflow all at once. It is a connected landscape being occupied. Some routes may fill early while others lag. The first liquid at the basket means at least one outlet route has become effective enough for liquid to escape; it does not certify that every part of the puck has shared the experience equally.

## What the X-rays saw

Foster and colleagues examined this filling stage with time-resolved micro-computed tomography—essentially repeated three-dimensional X-ray imaging. Instead of inferring wetting only from what entered the cup, they could observe where liquid was moving inside an espresso bed over time.

In the cited fine-grind experiment, the wetting front was sufficiently uniform for a one-dimensional sharp-front description, while the coarse-grind front was visibly non-uniform. Here, a “front” is the moving boundary between the wetter region above and the drier region below. A one-dimensional description treats its main motion as downward through the puck rather than trying to represent every sideways variation.

That distinction matters. The neat moving-boundary picture was a defensible simplification for the fine-grind case the researchers modelled. The coarse bed showed liquid advancing unevenly, including different behaviour near the wall. Applying the same tidy picture there would erase the most interesting observation.

## What the model explains

The source model treats the puck as wet above a moving boundary and dry below it. It combines water supply, pressure, trapped-air response, permeability, and pore volume to describe how that boundary advances. This is deliberately simpler than a real puck. Its value is that it turns a plausible physical story into something that can be compared with observations.

The source model was calibrated against the same wetting data it reproduced, so the agreement supports the model form but is not a blind prediction. Some parameters, including permeability, porosity, and a timing alignment, were fitted from those observations. The fit says that this compact description can reproduce important features of that experiment. It does not show that the fitted values will transfer unchanged to another coffee, grind, machine, or basket.

There is also a separate comparison based on an espresso-machine recording rather than the micro-CT experiment. In a separate Puckworks check, a predicted first-drip window of 6.4–7.8 seconds contained the observed 7.0-second first drip on the stated DE1 fixture; no parameter was tuned to hit first-drip time itself. The pressure trace and a fitted permeability multiplier still came from that evaluated shot, so this is a useful same-fixture compatibility check, not a held-out validation or a target for other machines.

## What this means for your next shot

Record time to first drip as a diagnostic of puck filling under repeated conditions, not as a universal target for taste or extraction. If you want the observation to mean anything, keep the machine, basket, dose, preparation, temperature, and pressure or pre-infusion programme as consistent as practical. Then note when the first liquid reaches the cup along with the measurements you already use.

If that timing shifts across otherwise repeated shots, something about filling or hydraulic resistance probably shifted too. The useful next move is not to declare the faster or slower shot better. It is to change one controllable variable at a time and see whether the timing moves consistently with it. Beverage mass, flow, pressure, extraction measurements, and sensory judgement still answer different questions.

A change in first-drip time can tell you that the hydraulic state changed, but it cannot by itself identify whether the cause was grind, packing, permeability, trapped air, pump behavior, or another mechanism. That ambiguity is the important limit. A stopwatch can flag a change; it cannot perform the diagnosis alone.

## Where the simple picture breaks

The strongest spatial evidence here belongs to the stated fine-grind apparatus and coffee. The coarse-grind observation was not adequately represented by a uniform downward front. The source model was fitted to the data it described, and the separate first-drip comparison belongs to one fixture whose pressure and permeability information were not held out.

None of this produces an ideal first-drip time, a taste prediction, or a universal pre-infusion setting. It does give the apparently empty pause a clearer physical meaning. The first drop is not when the shot begins. It is when work already happening inside the puck finally becomes visible.

## Sources and technical notes

J. Foster, W. Lee, K. Moroney, D. Prjamkov, M. Salamon, A. Smith, J. Petrassem-de-Sousa, and M. Vynnycky, “Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling,” *Physics of Fluids* 37, 013383 (2025). [DOI: 10.1063/5.0245167](https://doi.org/10.1063/5.0245167).

The [Foster model and source card](https://github.com/trbrewer/puckworks/blob/main/docs/cards/foster2025_2.md) records the fine-grind scope, fitted-model interpretation, coarse-grind non-uniformity, omitted physics, and the separate fixture-specific first-drip check. The source model and the machine fixture are distinct comparisons.

[PLATFORM DISCLOSURE]
