# Swelling prior and source limits

The local originals support a grain-swelling timescale of **tens of seconds**,
but do not measure the conductance-loss timescale in E1–E3. Before hydraulic
fitting, this screen sets the weak bound **10 ≤ τ ≤ 240 s**. This spans the
first analyzed microscopy frame through the reported practical completion
time. It is a deliberately broad proxy bound, not a measured confidence interval
or a claim that diameter growth and pore closure have identical kinetics.

Hargarten, Kuhn and Briesen, *Swelling properties of roasted coffee particles*
(2020), [DOI 10.1002/jsfa.10440](https://doi.org/10.1002/jsfa.10440), Table 2,
reports 30-s progress of 83%, 82%, 71% and 59% for medium/hot, medium/room,
light/hot and light/room preparations. Interpreting each single anchor as
`progress = 1 − exp(−t/τ)` gives descriptive e-fold times of approximately
17–34 s (hot preparations: 17–24 s). This conversion is not a kinetic fit.
The paper interprets swelling as substantially complete by 240 s; its values
above 100% reflect normalization to a noisy 20-minute reference. Measurements
used glued coarse particles, projected diameter, near-ambient pressure and a
cooling hot-water apparatus. They do not establish espresso pore-closure rates.
The prior analysis also found inconsistent graphical transformations/clocks;
this screen uses the printed table, not a pooled fit to those curves.

E1/E2 inherit the delivered-mass relaxation scale Mc from the corresponding
training-fold C4 reference; E3 inherits it from D1. Mc stays fixed while fitting
flow scale, compaction scale and τ. The onset-law coefficients also stay fixed
during each hydraulic fit and use only that fold's training brews. Whole-brew
bootstrap refits repeat these calibration steps to propagate their uncertainty.
Thus each candidate has three free parameters in its hydraulic optimization,
with additional estimated inputs; it is not a claim of three total statistical
degrees of freedom. No held-out onset enters E1/E3's onset-law calibration.

In the primary point fits, E1 reaches the 10-s lower bound in 10/11 folds and
the 240-s upper bound in the remaining fold; E3 reaches those bounds in 9/11
and 1/11 folds respectively. E2's fitted τ spans 29.4–50.7 s. These are
fold-to-fold fitted ranges, not confidence intervals or measured material
properties. The predictive candidates do not identify a stable swelling rate.

**Rights:** Copyright 2020 The Authors, Creative Commons Attribution–NonCommercial
(as printed in the article). The Hargarten-derived facts and conversions in this
noncommercial research note retain that attribution and licence; they are not
relicensed MIT. The authenticated original PDF SHA256 is
`4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0`;
[publisher-author copy at TUM](https://mediatum.ub.tum.de/doc/1580140/document.pdf).
No original PDF, artwork or private source rows are committed.

Mo et al., *Modelling swelling effects in real espresso extraction using a
1-dimensional coarse-grained model* (2023),
[DOI 10.1016/j.jfoodeng.2023.111843](https://doi.org/10.1016/j.jfoodeng.2023.111843),
calibrates its swelling rate to Hargarten. Its model curves are not an independent
swelling measurement. Foster et al., *Dynamics of liquid infiltration into an
espresso bed using time-resolved micro-computed tomography* (2025),
[DOI 10.1063/5.0245167](https://doi.org/10.1063/5.0245167), measures infiltration
and discusses Hargarten and contrasting Maillé evidence. Its front/headspace
times are not grain-swelling rates. The local Maillé evidence does not identify
a geometric-growth time because of optical/entrainment ambiguities. No numerical
prior was taken from those three sources, and their campaigns were not pooled.

The local Waszkiewicz paper also describes swelling accompanying the advancing
wetting front and early percolation. This qualitative observation supports the
question but supplies no independent grain-swelling rate. The operational
onset used here requires accumulated cup mass and sustained measured flow;
it includes transport and detection lag and is not the paper's first visible
drop or an imaged wetting-front breakthrough time.

Useful locations inspected (original PDFs were read, not only catalog entries):

- `/home/tim/.config/puckworks/data_sources.json`, configured root
  `/home/tim/Documents/data`, and its private inventory manifest under
  `/home/tim/Documents/data-corpus-guide-001-private/snapshot-release/` supplied
  source discovery. Home-directory and mounted-drive filename searches supplied
  no additional independent grain-swelling time series.
- `/tmp/hargarten-wet-psd-source/hargarten2020.pdf`; repository
  `puckworks/data/hargarten2020/hargarten2020_swelling_progress.csv`,
  `puckworks/data/hargarten2020/swelling_kinetics_001/PROVENANCE.md`,
  `docs/cards/hargarten2020.md` and the corresponding retained analysis.
- `/home/tim/Documents/data/pdf/06_other_papers/06_other_papers/Modelling-swelling-effects-in-real-espresso-extraction-using-a-1-dimensional-coarse-grained-model.pdf`;
  repository `docs/cards/mo2023_2.md` and `puckworks/data/mo2023_2/`.
- `/home/tim/foster-radial-001-evidence/source.pdf` and the duplicate
  `/home/tim/Documents/data/pdf/06_other_papers/06_other_papers/013383_1_5.0245167.pdf`;
  repository `docs/cards/foster2025_2.md` and `puckworks/data/foster2025_2/`.
- Repository `docs/cards/maille2021.md`,
  `puckworks/data/maille2021/swelling_evidence_001/PROVENANCE.md` and
  `docs/analysis/sci_md_maille_swelling_evidence_001/RESULT.md` supplied the qualified
  Maillé limitation; no new numeric extraction from its permission-limited originals.
- `/home/tim/wasz-terminal-mass-evidence/upstream/measurements_time_dependent/`
  supplied all native Waszkiewicz traces; repository `puckworks/data/waszkiewicz2025/`
  and read-only `/home/tim/espresso-development/espresso-whole-pull` supplied the
  original SCI-MD-010 cohort, folds and endpoint observer. The local paper
  `/home/tim/Documents/data/pdf/06_other_papers/06_other_papers/Under_pressure_poroelastic_regulation_of_flow_in_e.pdf`
  was reopened for the wetting/swelling discussion.

Waszkiewicz aggregates in ONSET.csv and RESULT_TABLE.csv are attributed to
Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315),
**CC-BY-4.0**. Individual onset detections are retained only in the ignored local
`.b0-b0c-onsets.csv`. No source file or historical result was modified.
