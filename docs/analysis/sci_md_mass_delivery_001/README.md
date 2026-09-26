# Research beverage-mass delivery

`puckworks.analysis.mass_delivery.Model` predicts interval dissolved-solids kg,
interval average TDS percent, and cumulative modeled delivery conditional on a
requested beverage stopping mass. It predicts no elapsed time, flow or pressure.
The pure kernel needs NumPy/SciPy; study reconstruction additionally needs openpyxl.
Run from an explicit checkout of the producer revision identified by the EWP handoff.

Synthetic example, no external source files:

```bash
python -m puckworks.analysis.mass_delivery --stop-kg 0.04
```

Source-specific model, synthetic requested mass intervals:

```bash
python -m puckworks.analysis.mass_delivery \
  --model docs/analysis/sci_md_mass_delivery_001/models/MASS.json --stop-kg 0.04
```

The fitted model has support 0–0.0635064 kg from the source collection origin.
Queries outside support fail. Zero-width delivery is zero with undefined TDS.
An integral spanning unassayed gaps is modeled; it is not a measured full-cup total.

Authorized source reproduction uses `PUCKWORKS_EXTERNAL_DATA_ROOT` or the existing
`~/.config/puckworks/data_sources.json` source entry. Output must be outside Git:

```bash
python -m puckworks.analysis.pannusch_mass_delivery prepare --output "$EVIDENCE/new-run"
python -m puckworks.analysis.pannusch_mass_delivery freeze --output "$EVIDENCE/new-run"
# Obtain independent exact-freeze pre-score audit before this single-use command:
python -m puckworks.analysis.pannusch_mass_delivery score --output "$EVIDENCE/new-run" \
  --review "$EVIDENCE/independent-review.json"
python -m pytest -q tests/test_mass_delivery.py
```

The study uses existing qualified reconstruction parsers, assay mapping and
shot-specific source prefixes. It never refits registered mechanistic models.
The historical Grudeva implementation is unchanged; only synthetic operator
agreement is tested. Training-only LOCO scores select the empirical baseline and
are development diagnostics. Final predictions for all five declared treatments
freeze together before independent review and a single later-campaign score.

First-party Python and synthetic tests follow repository software licensing.
**SOURCE.json, models/*.json, TRAINING_SELECTION.json and result tables are
Pannusch/Schmieder source-derived artifacts treated as CC-BY-NC-3.0, not MIT.**
Attribution: Pannusch et al., data repository for *Model-Based Kinetic Espresso
Brewing Control Chart for Representative Taste Components*, Mendeley Data v1,
[DOI 10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1),
[CC-BY-NC-3.0](https://creativecommons.org/licenses/by-nc/3.0/).
Artifacts are newly fitted/transformed from the qualified source, not original
source coefficients. Raw workbooks/MAT, analytical rows, predictions and full
optimizer traces remain external; compact manifests bind those private files.

SOURCE_INTERNAL; TARGET_EXPOSED; research only. This direct observational
regression does not resolve historical c_s0-to-inventory or EWP absolute-closure
blockers. Physical validation remains NOT_ESTABLISHED. No automatic successor.
