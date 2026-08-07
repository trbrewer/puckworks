# I-045 Deep Screen Decision (IF-7)

```
DEEP_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> Protocol frozen and committed **before** any analysis:
> [`DEEP_SCREEN_PROTOCOL.md`](DEEP_SCREEN_PROTOCOL.md), commit `a221157`, one file, no result.
> **No model was executed** (stop condition S5 — the lineage question is answered from text).
>
> ```
> cheap screen : SURVIVE          (frozen history, not rewritten)
> deep screen  : CORRECTION_ONLY
> ```

## Question

For `foster2025_2/fig12_14_curves`, do the **primary source's own calibration lineage** and
**ROADMAP §0** together establish that the manifest cell and the gate docstring attach an incorrect
evidence type to the CT arm — and what output class does that earn?

## Evidence unit

The paper (Foster et al., *Phys. Fluids* **37**, 013383, 2025, DOI `10.1063/5.0245167`), read in the
final published version obtained from the University of Limerick repository via Unpaywall after
`pubs.aip.org` refused automated access; plus `docs/cards/foster2025_2.md`,
`puckworks/data/MANIFEST.csv`, `puckworks/data/foster2025_2/*`, `puckworks/validation/gates.py`,
`puckworks/paper3/EVIDENCE_LINKS.json`, and every tracked file in the repository at
`7d81149`. No supplementary material exists; no code or data repository was published.

## Method

The protocol's steps, executed in order: verify §0 verbatim at run time → answer L1–L7 from the
paper → over-approximating needle scan across all tracked files plus the released tags, then hand
attribution of every surface → the frozen parenthesis-aware mixed-strength rule over all 110
manifest rows → A1–A5 challenges → F1–F4 formulations → classification.

---

## Result 1 — the lineage, from the paper

**The CT observations in this dataset are the data the tested parameters were fitted to.**

> **Eq. (39), §III D:** *"Systematic fitting was carried out by minimizing the objective function*
> `L = Σᵢᴺ [(sᵢ − s(tᵢ − t_shift))² + (Hᵢ − H(tᵢ − t_shift))²]`*, where sᵢ and Hᵢ are the
> experimentally determined positions of the wetting front and height of water in the headspace …
> and N is the number of experimental measurement times."*

> **§IV A:** *"The fitting algorithm follows that described in Sec. III D using the **mean locations
> for s(t) and H(t) as the data to fit**."*

| question | answer |
|---|---|
| **L1** what entered the objective | the CT-derived **5-line mean** `sᵢ`, `Hᵢ` — fitting `K` (i.e. `k`), `φ_T`, `t_shift` by `fmincon` interior-point, checked with `MultiStart` |
| **L2** s and H fitted simultaneously | **yes** — one objective, both residual terms |
| **L3** all plotted CT times | **yes** — `i = 1..N`, "N is the number of experimental measurement times"; no subsetting stated |
| **L4** anything held out | **nothing** |
| **L5** error bars | **display only** — they are the standard deviations across the five positions; Eq. (39) carries no weights |
| **L6** roles | squares = **fit input**; curves = **fitted-model output**; crosses = **sub-reduction of the fit data**; `w` = derived; Figs 6–9 = data analysis / assumption check; Fig 15 + App. B = model output |
| **L7** authors' terms | *"best fit"*, *"a good fit to experimental data"*, *"Good agreement"* — and they **do** call the combined tomography-and-modeling approach a technique for *"experimentally validating coffee models"*. They never call the observations independent or held out |

**Every candidate holdout was checked and none survives.** The centre-line crosses are one of the
five positions averaged into the fit data. Figs 6–9 carry no model curve. Fig 15 and Appendix B are
model output. `t_p`/`t_s` are outputs of the fitted solution. The coarse grind was **excluded from
modelling altogether** — *"we will only apply … the corresponding infiltration model to the fine
grind data"* — which is not the same as being reserved as a test.

**What the source does and does not say.** The authors **do** use validation language about this
work: the conclusions state *"The model shows a good fit to experimental data. By demonstrating the
feasibility of combining time-resolved x-ray tomographic measurements with modeling, we have
pioneered a new technique for experimentally validating coffee models."* That second clause is
present tense and describes the **method** as a way of experimentally validating coffee models.
Separately and later, they propose combining tomography with concentration measurements to produce
*"a richer dataset for model validation"* — that one is future work they did not do.

**What they never say is that any observation was independent or held out.** `independent` appears
three times in the paper and never about evidence (a symbols-table heading, "independent of time",
"independent of P_m"), and no passage identifies a held-out subset.

**And the broad usage does not help the label.** "Validating" there is a claim about the
*technique*, not about the evidentiary status of particular observations. ROADMAP §0 fixes
independence by whether data were used in fitting, and Eq. (39) with §IV A establish that these
were. An author calling their own comparison "validation" cannot make fitted data held out.

The controlling card is **confirmed** by the paper on the decisive point (`fmincon` least squares on
s and H simultaneously, MultiStart), so stop condition S2 was not triggered. One imprecision is
recorded, not corrected: the card's *Extractable data* section calls Figs 6/8 "the key validation
series", but Fig. 6 is data analysis and the model is compared against Figs 12–14.

## Result 2 — the blast radius

**13 tracked files carry the attribution; 5 more consume the dataset or gate without containing
either needle and were inspected by path.** Coverage complete.

| exposure class | count |
|---|---|
| `PRESENT_BUT_EXPLICITLY_REJECTED` | 10 |
| `GENERATED_BUT_CORRECTLY_BOUNDED` | 5 |
| `CURRENT_INTERNAL_MISWORDING` | **2** |
| `NO_EXPOSURE` | 2 |
| **`CURRENT_READER_FACING_OVERCLAIM`** | **0** |
| `HISTORICAL_SUPERSEDED` | 0 |

The two internal miswordings are the manifest cell and the gate docstring — the origin and its copy.
Everything downstream refuses the strong reading **independently**: `EVIDENCE_LINKS.json` files the
dataset as *both* `eval/same_campaign` **and** `fit/fit_input` with `reality_facing: false`; the
generated **public** `claims.json` records `same_campaign_not_held_out` and `outcome: negative`;
PV-02 excludes the gate outright; the registry says `source_curve_reproduction`.

Two findings a grep alone would have missed:

- **The GitHub Pages publish root (`docs/public/site`, per `pages.yml`) contains no occurrence.**
  Nothing a website visitor can read carries the attribution.
- **The Foundry's own tension atlas already flagged this cell** — `T-0063`, `lineage_circularity` /
  `mixed_strength_cell`, routed to `I-045`. The corpus's machinery found the row before a human did.

**It is in released source.** `v0.3.0` and the archive tag both carry the manifest cell and the gate
docstring. That is the reason to fix it: not because a reader is currently misled, but because the
next consumer of that cell would inherit it.

## Result 3 — bounded generality

**3 of 110 manifest rows** carry ≥ 2 distinct §0 labels under the frozen rule; 11 more are mixed in
form but not in §0 vocabulary (`reference`, `kernel check`) and were counted, not adjudicated.

**Two different questions, kept apart.** *Scope* asks whether a cell says which assertion or column
each label covers. *Source accuracy* asks whether each stated strength is correct against its
primary source. This screen answered the first for all three rows and the second for **one**.

| dataset | scope stated? | consumer could misattach? | source-strength correctness |
|---|---|---|---|
| `waszkiewicz2025/traces_time_dependent` | ✔ | no — I-040 found 0 promotions in 27 consumers | *not adjudicated* |
| **`foster2025_2/fig12_14_curves`** | ✔ | **yes — the gate does it** | **✘ CONFIRMED WRONG** |
| `romancorrochano2017/y0_extractable` | ✔ | structurally possible | *not adjudicated* |

**No recurring scope failure was found**: every primary-set cell states its scope in a
parenthetical, and the best-scoped one (`independent within-rig (equilibrium) / post-fit (9-bar
Q(t) reproduction)`) names both the strength *and* the assertion each covers.

**But no second wrong strength was confirmed either — and that is not the same as showing there
isn't one.** I-040 established that no *consumer* over-claims relative to the waszkiewicz cell's own
labels; it never went to that paper to check whether "independent within-rig" is correct against its
fit lineage, and neither did this screen. The romancorrochano thesis was not read at all. Reading
either would be executing another candidate.

So: `evidence_strength_generality: NOT_ESTABLISHED_AS_GENERAL`. **This screen does not establish
that the other rows' strengths are correct**, and does not prove corpus-wide isolation.

## Result 4 — alternative explanations

| # | challenge | verdict |
|---|---|---|
| **A1** | the CT observations were not used to fit the tested object | **FAILS** — Eq. (39) and §IV A |
| **A2** | a defensible held-out subset remains | **FAILS** — all N times fitted; the only other series is a sub-reduction of the fit data |
| **A3** | the label is a file-level union, not per-assertion | **FAILS** — the union of {verification, post-fit} still does not contain *independent* |
| **A4** | downstream containment makes the wording inconsequential | **PARTLY SUCCEEDS** |
| **A5** | *independent* means a distinct measurement modality | **FAILS** — under §0 *and* under the source's own usage |

**A4 is why this is not a publication finding.** Containment is real and measured: zero reader-facing
over-claims. It bounds the consequence; it does not make the attribution correct.

## Result 5 — correction formulations, assessed not implemented

| # | wording | verdict |
|---|---|---|
| F1 | `post-fit reconstruction (CT data) / verification (fitted curves)` | correct, minimal; loses the same-campaign detail |
| **F2** | **`post-fit, same-campaign CT observations / verification of fitted trajectories`** | **RECOMMENDED** — most precise, no schema change, matches the downstream record that is already right |
| F3 | split into separately scoped records/views | **REJECTED** — breaks the one-row-per-dataset assumption across loader, gate, evidence keys and generated artifacts; the generality result that would justify it came back negative |
| F4 | one row + an explicit column-to-evidence mapping | a genuinely better *general* convention, but the prose convention already states scope correctly everywhere, so it buys machine-readability, not correctness. Worth a separate proposal **if a second such defect appears** |

## External novelty

[`NOVELTY_REVIEW.md`](NOVELTY_REVIEW.md) — result **`INCREMENTAL`**. The principle is codified
(Verra VMD0053, Climate Action Reserve, ASME V&V terminology, Elmo). Existing leakage-audit tools
(bioLeak, data-use auditing) target a different mechanism — a botched split, not a mislabelled
provenance record. Column-level lineage and model cards are adjacent but track *derivation*, not
*evidentiary rung*. Nothing directly answering was found; that does not make it a contribution.

---

## Decision

# `CORRECTION_ONLY`

The misattribution is **confirmed from the primary source** and **contained** (zero reader-facing
over-claims), **no recurring defect was demonstrated**, and external review shows the underlying
principle is routine. A bounded repository correction is warranted. **No standalone publication
output is earned.**

The classification rests on *"no recurring defect was demonstrated"* — **not** on a claim that
corpus-wide isolation was proved. It was not: one strength was source-adjudicated, and it is the
one that is wrong. Were a second confirmed, the classifier would route to
`TECHNICAL_NOTE_CANDIDATE`; a test asserts that, so the bounded result is not an artefact of how
the decision is wired.

`RETIRE_AFTER_DEEP_SCREEN` was available and is refused on the evidence: the paper's own objective
function settles that the CT observations were fitted, not held out.
`NEEDS_PRIMARY_SOURCE` does not apply — the paper was obtained and every lineage question is settled.
`TECHNICAL_NOTE_CANDIDATE` fails on generality. `METHODS_PAPER_CANDIDATE` fails on three of its five
conditions. `PUBLIC_STORY_CANDIDATE` fails: the practical consequence is internal hygiene, and
"validation is not validation" is exactly the generic message the protocol declares insufficient.

## Strongest supported claim

> In this repository, one MANIFEST cell and the gate docstring that copies it label a set of
> micro-CT observations `independent` when the primary source's own objective function
> (*Phys. Fluids* **37**, 013383, Eq. 39) fitted the tested parameters to exactly those
> observations. Under ROADMAP §0 the arm is post-fit reconstruction, same campaign, not held out.
> The attribution is materially incorrect, it is present in released source, and it reaches **zero**
> reader-facing claim surfaces because every downstream record independently refuses the strong
> reading.

## Strongest claim NOT supported

> That this is a general defect, a novel method, or a publishable finding — **nor that it is
> globally isolated**. The bounded corpus check found no recurring *scope* failure and confirmed no
> second wrong *strength*, but it source-adjudicated only one row: the other two mixed-strength
> cells' strengths are `NOT_SOURCE_ADJUDICATED`, so nothing here says they are correct. The audit
> method is a hand-read of one paper plus a grep, not a reusable instrument; and the underlying
> principle is textbook.

It also does **not** say the gate's numbers are wrong (RMSE 0.002 / 0.053 mm against a 0.2 mm
threshold, bracketing 4/8 and 5/8, all unaffected), that `foster2025.machine_mode` fails anything,
or that the other two mixed-strength cells are mislabelled.

## Exact future correction targets — NAMED, NOT EDITED

| # | target | current | recommended |
|---|---|---|---|
| 1 | `puckworks/data/MANIFEST.csv` — `foster2025_2/fig12_14_curves` `validation_strength` | `independent (CT data) / verification (fitted curves)` | **`post-fit, same-campaign CT observations / verification of fitted trajectories`** |
| 2 | `puckworks/validation/gates.py` — `gate_foster_ct_trajectory` docstring | `…within their error bars (independent, 'qualitative-good')` | `…within their error bars (post-fit reconstruction, same campaign, not held out; 'qualitative-good')` |
| 3 | derived Foundry artifacts that copy the cell byte-identically | `evidence_lineage_index.csv`, `corpus_map.json` | **regenerate** with `python -m puckworks.insights write` after target 1 — never hand-edit |

`puckworks/paper3/EVIDENCE_LINKS.json` is **already correct** and is explicitly not a target.

- **Separate correction PR recommended:** **yes** — it touches an evidence label and a gate, which a
  screen may not do.
- **Further literature review justified:** no.
- **Manuscript work justified:** no.
- **Experimental work justified:** no.

## Claim ceiling

The ceiling may not exceed the weakest evidence consumed. The inputs are a published paper's method
section, provenance metadata, and a text scan — so this is a **statement about attribution**, with
no physical content. It licenses the strongest supported claim above and nothing beyond it.

## Reproduction

```
python -m puckworks.analysis.deep_screen_i045_lineage
pytest tests/test_deep_screen_i045.py -v
```

## Source commit

- Branch base (main, IF-6b merge): `7d8114931c5bafbf3915d9f70b7c4621f8261a22`
- Protocol commit (precedes this result): `a221157`
- Branch: `insights/if7-i045-deep-screen`
- Cheap-screen **scientific disposition**: `SURVIVE`, **not rewritten**.
- Cheap-screen **live snapshot**: **refreshed** under an explicit post-protocol waiver, because
  adding this deep screen's own documents to a deliberately repository-wide, over-approximating
  static inventory advanced it. The frozen protocol predates that waiver and is **not** edited.

| | `n_static_references` | `n_static_reference_files` |
|---|---|---|
| historical IF-6b snapshot (`7d81149`) | 102 | 24 |
| current IF-7 snapshot | 136 | 28 |

  `decision_bearing_fields_changed: false` — verified field by field and asserted by test. The
  historical artifact remains recoverable from git history at the merged IF-6b state.
