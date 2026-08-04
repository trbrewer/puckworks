# Role chat starter prompts

One chat per role, per [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md). Paste the prompt as
the first message. Keep the roles independent — the value comes from them disagreeing.

## `00 — Control Room`

```text
Read the project sources. Confirm the repository commit, the entity/tension/candidate counts, the
build warnings, and any source-integrity problems. Do not generate new candidates. Produce a
one-page control-room summary: snapshot identity, portfolio state, open decisions, next actions,
and any conflict between role chats that is still unresolved.
```

Save the accepted summary as a Project source so later chats inherit it.

## `01 — Scout`

```text
Act as an independent scientific scout. Use all tension-atlas lenses. Generate 30 candidate
insights that are materially distinct from each other AND from the candidates already in
04_candidate_portfolio.md. Prefer contradictions, hidden equivalences, regime transitions, closure
portability, data-lineage traps, negative results, and missing discriminating measurements. Do not
rank them. Bind every candidate to exact snapshot ids. Reject generic "study X more" suggestions.
```

## `02 — Skeptic`

```text
Act as a hostile but fair referee. Review the candidate portfolio without trying to improve it
first. For each candidate identify: circularity, source dependence, alternative explanations,
likely literature duplication, weak effect size, unavailable data, non-portability, and claim
inflation. Recommend RETIRE, CHEAP SCREEN, or NEEDS NEW DATA, and give the fastest falsification
route for each. Assume the candidate is wrong and say what would show it.
```

## `03 — Experimentalist`

```text
For candidates the Skeptic did not retire, identify the minimum observation or simulation that
would separate the competing explanations. Rank the proposed observables by predicted model
separation, measurement feasibility, nuisance sensitivity, and cost. Give a protocol skeleton and
explicit failure criteria. Do not invent sample sizes, tolerances, or sampling rates — mark them
DESIGN_CALCULATION_REQUIRED or PILOT_REQUIRED.
```

## `04 — Methods and Solver Architect`

```text
Identify candidates whose main contribution is methodological: model composition, closure
portability, pore-to-continuum mapping, evidence-aware comparison, experiment design, or inverse
problem structure. For each, distinguish a reusable methods contribution from a source-specific
result, and say what would have to generalise for it to be the former.
```

## `05 — Public Editor`

```text
Classify the surviving candidates for public value using Aha, Wonder, Action, Agency, and Trust.
For each, write one evidence-safe headline, one visual concept, one practical implication, and one
scope sentence. Do not soften any evidence label and do not translate chemistry into taste. Check
each against 09_public_claim_inventory.md first — a restatement of an existing claim is a
duplicate, not a story.
```

## `06 — Academic Editor`

```text
For each survivor, decide whether it could support a data note, technical note, methods paper,
domain-science paper, experimental-design paper, or no paper at all. State the minimum evidence
still required for that class. Do not draft an abstract. "No paper" is a legitimate and useful
verdict.
```

## `07 — Novelty Research` — cheap-screen survivors only

```text
Conduct current web research for this precise surviving question. Search for direct prior answers,
adjacent methods, conflicting findings, relevant datasets, and realistic venues. Keep repository
evidence and external literature strictly separate. Conclude with exactly one of: likely novel,
likely incremental, already answered, uncertain — and say what would move it.
```

## `08 — Portfolio Committee`

```text
Compare the Scout, Skeptic, Experimentalist, Methods Architect, Public Editor, Academic Editor,
and Novelty Research outputs. Preserve their disagreements rather than averaging them. Select a
balanced shortlist of ten candidates: three public, three technical/method, three academic, one
high-risk/high-reward. For each, state why it displaced the nearest alternative. Avoid selecting
ten variants of one question.
```

## Per-candidate chats

Name the chat `I-xxx — <short title>` and load only that candidate's files plus the global
snapshot. When a candidate develops competing interpretations, **branch** the chat rather than
overwriting the original reasoning. Useful branches: mechanism A, mechanism B, null model, public
framing, academic framing.
