# Reading visualizer.coffee data: a measurement and evidence guide

A non-specialist guide to what espresso-shot telemetry from visualizer.coffee can and cannot support.
**It contains no empirical corpus statistics** — it is about measurement meaning and evidence limits,
not results. Public aggregate results (when a sanctioned corpus exists) always carry their own
denominators and snapshot identity.

## 1. What a Visualizer record can contain

A shot record may carry a time axis and per-channel series (pressure, flow, mass, temperature),
machine/integration identity, a profile/control setpoint, and optional user-entered outcomes (dose,
yield, TDS, tasting notes). Records vary widely in which channels are present.

## 2. Channel classes (do not conflate)

- **measured** — a sensor reading (e.g. a pressure transducer);
- **commanded / setpoint** — what the machine was told to do (a pressure/flow *goal*);
- **scale-derived** — mass and mass-flow computed from a scale;
- **machine/model estimate** — a value the machine infers rather than measures;
- **ambiguous native proxy** — a vendor channel whose exact quantity/units are not documented;
- **user-entered outcome** — a human-entered dose/yield/TDS/sensory value.

## 3. Pressure node and reference limitations

A "pressure" channel may be **line/pump-side** or **basket** pressure, gauge or absolute, and the node
is frequently undocumented per record. Do not assume a node or reference; treat it as declared-or-unknown.

## 4. Line vs basket vs pressure goal

- **line/pump pressure** — upstream of the puck;
- **basket pressure** — at the puck (often derived, not measured);
- **pressure goal** — the commanded setpoint, not an achieved value.

These are different quantities; comparing them requires knowing which is which.

## 5. Why `flow_reported` is ambiguous

A reported flow channel may be **volumetric** flow, **mass** flow, or a **machine proxy** depending on
the machine/integration. It is not a single physical quantity across the corpus.

## 6. Scale-derived mass flow is separate

Mass and mass-flow from a scale are a distinct measurement path from any machine-reported flow, with
their own latency and noise; keep them separate.

## 7. User TDS / yield / sensory are not population ground truth

User-entered TDS, extraction yield, and tasting notes are self-reported, unevenly present, and
selection-biased. They are hypotheses and context, **not** population ground truth.

## 8. Permitted corpus conclusions

- measurement/channel **availability** (what is present, how often);
- **telemetry quality** (sampling, coverage);
- **operating-envelope coverage** (what regimes are observed);
- **commanded-versus-achieved** behavior where both channels exist;
- **contributor concentration** (how few users dominate);
- **ecological associations** (co-occurrence patterns, explicitly non-causal);
- **hypothesis generation** for controlled follow-up.

## 9. Prohibited conclusions from Visualizer alone

- causal effects; latent puck-mechanism validation; ground-truth channeling; ground-truth
  permeability; machine rankings; flavor prediction; recipe optimization.

## 10. Privacy and redistribution policy

- raw records are **not** published by Puckworks; public outputs are aggregate/derived;
- denominators and snapshot hashes accompany results;
- one-shot-per-user sensitivity is required;
- small-cell suppression (or an equivalent disclosure rule) is applied before any public aggregate.

## Related

- `puckworks/data/visualizer/PROVENANCE.md`
- `docs/analysis/SANCTIONED_EXPORT_SPEC.md`
- `docs/analysis/VISUALIZER_EXPORT_READINESS.md`
- the sanctioned-corpus-export tracking issue
