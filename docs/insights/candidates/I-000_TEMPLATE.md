# I-000 — Template (not a candidate)

The shape of a candidate card, per blueprint §10.2. Cards exist for **shortlisted** candidates
only. To materialise one from the generated portfolio:

```
python -m puckworks.insights card I-007
```

Then edit it — the generated text is a starting point, not a result. Writing a card by hand is
fine; copy the sections below.

The three fields that make a candidate a candidate rather than a topic are **Question**,
**Cheap scientific screen**, and **Stop condition**. A card missing any of them is a wish.

---

## Question

One falsifiable sentence. Not "investigate X" — a question a result can answer no to.

## Insight type

model disagreement · equivalence · closure portability · data lineage · regime transition ·
negative result · experiment design · public story · corpus hygiene

## Target audiences

public · practitioner · technical · academic · methods. Public value and academic value are
separate axes — do not collapse them (blueprint §3.6).

## Why it may matter

What changes if it is true? If nothing changes either way, retire it now.

## Why it may be surprising

What expectation does it challenge? "Nobody has checked" is not a surprise.

## Models, datasets, and other entities

Exact identifiers — `model:cameron2020.extraction_bdf`, `dataset:waszkiewicz2025/tds_fractions`,
`card:foster2025`. A candidate that cannot name its entities cannot be screened.

## Tension rows

The `T-xxxx` rows this came from, so a reader can re-derive it.

## Existing evidence

Only current, source-bound evidence, with each label quoted **verbatim** from its authority.
Never restate a validation rung in your own words.

## Strongest alternative explanation

The explanation most likely to kill the candidate. Write this before the screen, not after.

## Cheap scientific screen

One bounded calculation or source audit. Budget: one focused working day, one script, one figure,
one adversarial check, one decision. Not the whole paper.

## Minimum viable figure

The single figure that would make the result legible.

## Decision rule

- **SURVIVE if** …
- **RETIRE if** …
- **INCONCLUSIVE if** …

Written before the screen runs, and applied without revision afterwards.

## Stop condition

What result ends the thread? A candidate with no stop condition runs forever.

## Possible outputs

Public story · technical note · academic paper · experiment proposal · solver backlog · nothing.
"Nothing" is a legitimate outcome.

## External novelty search terms

Run only **after** the candidate survives its cheap screen (blueprint §13.4). A research-radar hit
is metadata for human review, never evidence.

## Status

`SEED`. Transitions append a one-line reason here. The lifecycle is in
`puckworks/insights/schema.py` (`CANDIDATE_STATUSES`); a generator may only ever emit `SEED`.
