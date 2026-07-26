# Paper 3 — figure text alternatives

Each entry states what the figure shows and what the reader should take from it, so no finding is reachable only through the image.

## `fig1_architecture`

A directed graph of the Puckworks pipeline. Source papers and artifacts feed model and dataset cards; cards feed registered components carrying typed contracts; a configuration selects components; gates and harnesses produce result bundles; claim producers emit public claims; figures and source data export from those bundles to an archived release. A second horizontal band shows the seven process stages. Arrow styles distinguish data provenance, runtime state, calibration and evidence.

## `fig2_stage_evidence_map`

Three panels. Panel a is a stacked bar chart of registered components by process stage, split into runtime and calibration roles. Panel b shows, for every component, which evidence relations its gates demonstrate, as a grid of relation against component; the point is that components hold several different relations at once rather than one score. Panel c is a small component card listing source, assumptions, validity range, gates and caveats.

## `fig3_observable_linting`

Four panels showing observable and unit linting. Panel a lists three incompatible saturation-concentration values, each retained with the sources that use it, rather than merged. Panel b is a schematic of four pressure nodes along the machine-to-bed path, annotated to say that node identity is documented but not a typed contract field. Panel c shows an invalid mixed-unit aggregation of named-solute masses with total dissolved solids, struck through, beside the corrected yield. Panel d shows raw extraction-yield cells ordered across grinder settings with the fitted response-surface vertex marked separately.

## `fig4_null_first_ladder`

A horizontal ladder of model-comparison rungs ordered from the simplest null upward: best in-window constant, long-run constant, static pressure-dependent branch, the dissolution-linked temporal trajectory, and a flexible same-trace cubic. Each rung shows its reconstruction error and how many free parameters were fitted to the scored trace. The figure emphasises comparison architecture; the physical conclusions belong to the companion temporal paper.

## `fig5_negative_composition`

Four panels on a failed composition. Panel a is a component graph in which an extraction branch and a swelling branch share one porosity state. Panel b shows the composite reducing exactly to the extraction-only branch when swelling is neutral. Panel c shows the measured flow trace with the extraction-only prediction tracking it while the composite is flat. Panel d compares reconstruction errors and annotates that the composite value equals the static branch because the composite output is constant.

## `fig6_experiment_map`

A matrix connecting unresolved model comparisons to the measurements that would discriminate them, with each recommendation linked back to the card supplying the directional prediction, and each experiment labelled by its readiness tier.

## `fig7_named_shot_scorecard`

A stage-by-stage horizontal chain for one illustrative shot. Each block names the stage, the selected component or input, and its evidence status, coloured by status. Statuses on stages with a registered component are derived from that component's scoped evidence records. Two blocks are open, and the chain ends in 'measurement required' rather than a predicted cup.
