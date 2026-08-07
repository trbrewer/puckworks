# I-045 — evidence-lineage correction: **APPLIED**

```
CURRENT_STATE_RECORD
NOT_A_SCIENTIFIC_RESULT
```

> The human-owned correction that closes the defect found by the I-045 screens. It changes what the
> repository **says** about a piece of evidence. It changes no model verdict, validation rung,
> public badge, physical conclusion or numerical gate result.
>
> Machine-readable companion: [`correction_result.json`](correction_result.json)
> (sha256 `5b28588faf98…`), regenerated with
> `python -m puckworks.analysis.correction_i045_lineage`.

## Authority — quoted, not re-adjudicated

| | |
|---|---|
| IF-7 merge | `6ce8d97db79bc9a189af130c61fd2d9af7c66883` |
| cheap screen | **SURVIVE** |
| deep screen | **CORRECTION_ONLY** |
| novelty | **INCREMENTAL** |

The finding: Eq. (39) of *Phys. Fluids* **37**, 013383 fits `K`, `φ_T` and `t_shift` to the
CT-derived 5-line mean `sᵢ`, `Hᵢ` at every measurement time, and §IV A says so — *"using the mean
locations for s(t) and H(t) as the data to fit."* Nothing was held out. Under ROADMAP §0 the CT arm
is **post-fit reconstruction, same campaign, not held out** — not independent.

## The three source surfaces, corrected

| surface | before | after |
|---|---|---|
| `puckworks/data/MANIFEST.csv` — `foster2025_2/fig12_14_curves` | `independent (CT data) / verification (fitted curves)` | `post-fit, same-campaign CT observations / verification of fitted trajectories` |
| `puckworks/validation/gates.py` — `gate_foster_ct_trajectory` docstring | `(independent, 'qualitative-good')` | `(post-fit reconstruction, same campaign, not held out; 'qualitative-good')` |
| `README.md` — Foster row, *Data used to check the models* | `Independent (CT data) / verification of fitted curves` | `Post-fit, same-campaign CT observations / verification of fitted trajectories` |

The MANIFEST field is CSV-quoted because the new wording contains a comma. Exactly one logical cell
and one line changed; the other 110 rows and all line endings are untouched. The gate change is
**docstring-only** — an AST comparison with the docstring stripped proves the body is identical.

The README row was **hand-edited**: no repository producer owns the `puckworks-data-inventory`
block. `update_readme_pulse.py` owns only `puckworks-pulse`, and `readme_governance.py` verifies
coverage without generating the table.

## Gate numerics — unchanged

```
passed             True
s_fit_rmse_mm      0.002      (threshold < 0.2)
H_fit_rmse_mm      0.053      (threshold < 0.2)
s_data_within_err  4/8        (threshold >= 4)
H_data_within_err  5/8        (threshold >= 4)
```

## Generated Foundry state

Regenerated with `python -m puckworks.insights write`; a second run produces zero diff and
`verify` succeeds.

| | |
|---|---|
| appended tension identity | **`T-0175`** — the only new ID |
| existing ID mappings | **all unchanged**; nothing reassigned or removed |
| live candidate portfolio | **91 → 90** |
| removed | **`I-045` only** |

### Why I-045 leaves the live portfolio

`T-0063` is the tension that *found* this defect — it fired because the cell named more than one
§0 strength. With the cell corrected it no longer fires, so `I-045` is no longer an unresolved
current-state opportunity.

**That means `RESOLVED_BY_CORRECTION`.** It does **not** mean RETIRE, RETRACTED, INVALIDATED or
NEVER_EXISTED.

The live portfolio represents *unresolved current-state opportunities*. It is not required to
duplicate the historical audit log, which is preserved in the cheap-screen bundle, the deep-screen
bundle, the materialised I-045 card, this record, `correction_result.json`, Git history, and the
append-only ID registry — where `T-0063` remains permanently resolvable.

## Already correct — deliberately untouched

`puckworks/paper3/EVIDENCE_LINKS.json` already filed the dataset as *both* `eval/same_campaign`
**and** `fit/fit_input`, with `relationship: same_campaign_not_held_out`, `reality_facing: false`
and `support_status: context_only`. The public claims artifact, the Paper 3 evidence, the registry,
the component cards, `docs/public/site` and `puckworks/viz` are all unchanged.

## Release history

Immutable prior tags — `v0.3.0` and the archive tag — retain the old source wording and are **not**
rewritten. **The correction is not in any public release**, and will not be until a later release
actually contains it.

## Scope

No evidence badge, validation rung, model verdict, public scientific claim or numerical result
changed. No other candidate, MANIFEST row or model was touched. No correction framework, lifecycle
schema, portfolio machinery, Foundry lens, generator or governance mechanism was added.
