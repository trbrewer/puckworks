# Paper B — related-work scaffold and novelty positioning

**Status: SCAFFOLD. Novelty is NOT asserted here.** This document assembles the prior
work already cited on the in-repo model cards into a claim→prior-art matrix, states the
*candidate* contributions, and specifies the systematic search that would establish
novelty. That systematic database search is **owed PI-execution** (no bibliographic
database access in this environment) — exactly the stance the Paper A draft took before
its dedicated literature handoff. Do not upgrade "candidate contribution" to "novel"
until the §3 search runs.

Every reference below is drawn from an **on-file model card**; no citation is invented.
DOIs are carried with the card's verification status — two are flagged UNVERIFIED and
must be checked against the publisher record before the manuscript cites them.

## 1. Prior-art register (card-sourced only)

| key | citation | DOI | status |
|---|---|---|---|
| cameron2020 | Cameron et al., "Systematically improving espresso," *Matter* 2, 631–648 (2020) | 10.1016/j.matt.2019.12.019 | verified (card) |
| moroney2016 | Moroney, Lee, O'Brien, Suijver, Marra, "Asymptotic analysis of the dominant mechanisms in the coffee extraction process," *SIAM J. Appl. Math.* 76(6), 2196–2217 (2016) | 10.1137/15M1036658 | verified (card) |
| foster2025 | Foster, Lee, Moroney, Prjamkov, Salamon, Smith, Petrassem-de-Sousa, Vynnycky, "Dynamics of liquid infiltration into an espresso bed using time-resolved micro-CT," *Phys. Fluids* 37, 013383 (2025) | 10.1063/5.0245167 | verified (card) |
| waszkiewicz2025 | Waszkiewicz et al., "Under pressure: poroelastic regulation of flow in espresso brewing," arXiv:2512.21528 [physics.flu-dyn] (Dec 2025) | — (arXiv) / published *Phys. Fluids* 38, 063113 · 10.1063/5.0319611 | **VERIFY published vol/DOI** (card gives arXiv; the external-test module cites the Phys. Fluids version) |
| mo2023 | Mo, Navarini, Suggi Liverani, Ellero, "Modelling swelling effects in real espresso extraction using a 1-D coarse-grained model," *J. Food Eng.* (2023) | 10.1016/j.jfoodeng.2023.111843 | verified (card) |
| fasano2000 | Fasano, Talamucci, Petracco, "The Espresso Coffee Problem," ch. 8 in *Complex Flows in Industrial Processes* (A. Fasano, ed.), Springer, pp. 241–280 (2000) | — (book chapter, no DOI in scan) | verified (card); no DOI |
| lee2023 | Lee, Smith & Arshad, "Uneven extraction in coffee brewing," *Phys. Fluids* 35, 054110 (2023) *(believed)* | 10.1063/5.0138998 | **UNVERIFIED** — card: "verify before registry entry" |
| schmieder2023 | Schmieder, Pannusch, Vannieuwenhuyse, Briesen, Minceva, "Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics," *Foods* 12, 2871 (2023) | 10.3390/foods12152871 | verified (card, open access) |
| liang2021 | Liang, Chan & Ristenpart, "An equilibrium desorption model for the strength and extraction yield of full immersion brewed coffee," *Sci. Rep.* 11, 6904 (2021) | 10.1038/s41598-021-85787-1 | verified (card) |

This register is the *known* prior art from the components already in the registry — it is
**not** a systematic literature survey and cannot by itself establish novelty (see §3).

## 2. Claim → prior-art matrix

| Paper B result | Nearest prior art | Relationship |
|---|---|---|
| **R1 — model-capacity discrimination on the fine-grind response** (inventory/kinetics/channeling all fit the cup EY) | cameron2020 (fine-grind EY turnover + reduced-participating-area); lee2023 (dissolution–flow instability + saturation reinterpretation); moroney2016 (dominant-mechanism asymptotics) | We do not add a mechanism; we show the integrated EY does not *discriminate* among the existing ones — a capacity/identifiability statement about the observable, complementary to each source's mechanism claim. |
| **R2 — null-first κ(t) ladder for the rising-flow residual** | waszkiewicz2025 (poroelastic Φ(t)); foster2025 (machine/infiltration null); fasano2000 I/II (fines migration / compaction); mo2023 (swelling); cameron2020 (dissolution) | We rank these as *nested nulls* on one trace: constant → static-κ(P) → dissolution-Φ(t) → mechanism challengers, and refute the matrix-resistance branches (swelling, fines) **by sign**. The individual mechanisms are the sources'; the null-first ranking + sign refutation is the contribution candidate. |
| **R2 cross-pressure** — within-rig held-out transfer across 11 pressures | waszkiewicz2025 (the 11-pressure campaign + static calibration) | We reuse their campaign and calibration and add a leave-one-pressure-out held-out test of the *discrimination*, not just the static curve. |
| **R3 — streamtube channeling / dynamic heterogeneity (exploratory)** | lee2023 (dynamic ε→κ heterogeneity growth); (streamtube ensemble is repo-native) | Positioned as an exploratory finite-time concentration result, explicitly downgraded from a stability claim; lee2023 is the nearest dynamic-heterogeneity precedent. |
| **Method — evidence-strength discipline + null-first testing ladder** | — | The candidate methodological contribution: every rung must beat the rung below on the same data before a residual is claimed; challengers refuted by *sign/shape* where fit-quality ties. Whether this framing is novel vs the broader model-selection / identifiability literature is exactly what §3 must check. |

## 3. Owed systematic search (PI-execution)

To establish (or retract) the novelty claims above, run a systematic search — the same
protocol Paper A uses (`docs/literature_search/SEARCH_PROTOCOL.md`), retargeted:

- **Databases:** Scopus, Web of Science, Google Scholar; arXiv physics.flu-dyn; the food-
  engineering and applied-math venues (J. Food Eng., Phys. Fluids, Matter, SIAM J. Appl.
  Math., Foods, Sci. Rep.).
- **Query axes:** (espresso OR "coffee extraction" OR "porous bed") × (flow rate OR
  permeability OR "poroelastic" OR "fines migration" OR compaction OR swelling OR
  channeling) × (model OR identifiability OR "mechanism discrimination" OR "null model").
- **Screen for:** any prior null-first / nested-baseline ladder applied to espresso flow;
  any prior sign-based refutation of a bed mechanism; any prior cross-pressure held-out
  test of a κ(t) model. A hit against any of these narrows the corresponding candidate
  contribution — record it in an evidence matrix (claim → citation → supports/contradicts).
- **Verify first:** the two flagged DOIs (lee2023, waszkiewicz2025 published version)
  against the publisher record before any citation.

Until this runs, the manuscript should keep the R2 methodology and sign-refutation framed
as *"to our knowledge"* at most, and preferably as a clearly-scoped positioning against
the card-cited work only.

## Cross-references
- `PAPER_B_DRAFT.md` §7 (related-work / novelty owed) and the Results sections.
- `docs/literature_search/SEARCH_PROTOCOL.md` — the Paper A protocol to retarget.
- Model cards for every reference above (the source of every citation and DOI here).
