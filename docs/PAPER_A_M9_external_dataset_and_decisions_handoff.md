# Paper A handoff for Claude Code  
## M9 related work and identifiability review, independent fraction data, and project decisions

**Prepared:** 12 July 2026  
**Repository:** [trbrewer/puckworks](https://github.com/trbrewer/puckworks)  
**Manuscript:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md)  
**Recommended target journal:** **Journal of Food Engineering**  
**Status:** This document resolves the requested policy decisions, supplies a verified related-work framework and source list, and identifies an immediately usable independent fraction-resolved TDS dataset. It does **not** turn the present manuscript into a submission-ready paper by itself: the numerical blockers identified in the detailed review still require corrected reruns.

---

> [!IMPORTANT]
> ## What changed relative to the original task description
>
> A public, independently generated, fraction-resolved espresso dataset is available now:
>
> **Waszkiewicz et al. (2026), “Under pressure: Poroelastic regulation of flow in espresso brewing,” Physics of Fluids 38, 063113.**  
> Paper DOI: [10.1063/5.0319611](https://doi.org/10.1063/5.0319611)  
> Data/code repository: [RadostW/espresso](https://github.com/RadostW/espresso)  
> Archived software/data release: [10.5281/zenodo.18046315](https://doi.org/10.5281/zenodo.18046315)
>
> It provides 5-second, replicate-level TDS fractions and matching time-dependent flow measurements from a second espresso rig. It is suitable for an **independent external TDS trajectory test**. It is not a multi-solute or multi-grind dataset, so it does not by itself support the strongest possible version of §6.

---

## 0. Decisions and instructions at a glance

The following decisions should be treated as resolved unless the principal investigator explicitly reverses them.

```yaml
paper_a:
  target_journal: "Journal of Food Engineering"
  contribution_class:
    new_espresso_case_study: "yes, cautiously"
    new_model_data_observation: "yes, conditional on corrected reruns"
    new_general_identifiability_method: "no"
  terminology:
    negative_validation: "do not use"
    preferred:
      - calibration
      - reconstruction
      - internal holdout
      - internal prediction
      - external prediction
      - cross-dataset prediction
      - failed external prediction
      - in-sample verification
      - objective localization
  headline_metric:
    primary: "three named solutes only: caffeine, trigonelline, 5-CQA"
    tds_or_total_solids: "separate aggregate-solids proxy analysis"
    sensitivity: "report named-solute results with and without the proxy"
  section_6:
    pannusch_current_analysis: "in-sample verification / objective localization"
    independent_external_panel: "Waszkiewicz 2026 TDS fractions"
  release:
    tag_now: false
    release_candidate_after_blockers: "paper-a-v1.0.0-rc.1"
    submission_release: "paper-a-v1.0.0"
    archive: "GitHub Release plus Zenodo version DOI"
```

### Immediate Claude Code priorities

1. Replace the related-work placeholder with the insertion-ready material and citations in this document.
2. Change all structural or universal non-identifiability claims to design-, model-, objective-, and domain-bounded **practical identifiability** claims unless a formal structural proof is added.
3. Rename any MAPE-based “profile likelihood” to **profiled MAPE objective**, **profiled error curve**, or **profiled objective surface**. “Profile likelihood” is reserved for an explicitly stated likelihood/noise model.
4. Rename the existing Pannusch fraction exercise **in-sample verification** or **objective localization on calibration data**.
5. Add the Waszkiewicz dataset as a genuinely independent, second-rig TDS fraction test.
6. Exclude TDS/TS from the primary headline average; report it separately.
7. Target Journal of Food Engineering conventions.
8. Do not create the final paper tag until all numerical blockers, figures, data adapters, and release metadata are frozen and reproducible.

---

# 1. M9 — documented related-work and identifiability review

## 1.1 Bottom-line judgment

The current work can credibly claim:

1. **An applied espresso case study:** a systematic practical-identifiability and transfer analysis of an inventory–kinetic-rate compensation problem in a mechanistic espresso extraction model.
2. **A model–data-specific observation:** under the tested whole-cup observation design, rate and inventory can occupy a broad compensating profile, while time-resolved fractions can provide materially stronger rate localization.
3. **A reproducible evaluation workflow:** matched observation operators, explicit profiling, internal holdout, external prediction, and evidence-strength labels.

The work should **not** claim:

- a new general identifiability method;
- a theorem that cup integration always destroys kinetic identifiability;
- structural non-identifiability based only on a finite numerical sweep;
- that “sloppiness” and non-identifiability are synonyms;
- independent physical identification from a refit to the same data used to fit or profile the model;
- novelty against all prior literature without a documented database search.

The defensible novelty category is therefore:

> **New espresso case study + new observation for this model/data pair, using established identifiability methods; not a new general method.**

That distinction should appear in the Introduction, Discussion, Abstract, cover letter, and repository documentation.

---

## 1.2 Required conceptual distinctions

### Structural identifiability

Structural identifiability is a property of the **model equations, admissible inputs, initial conditions, parameterization, and observation map under ideal noise-free observations**. It asks whether two distinct parameter vectors can produce exactly the same ideal output.

A numerical grid, optimizer trace, Hessian, or broad empirical profile does not by itself prove structural non-identifiability. A structural claim requires an analytic or symbolic argument, a recognized structural-identifiability method, or a rigorous model-specific proof.

**Permitted wording without a structural proof:**

> “The rate is weakly practically identifiable over the tested parameter domain under this observation design and objective.”

**Do not write:**

> “The rate is structurally non-identifiable.”

unless the manuscript supplies the proof and all assumptions under which it holds.

### Practical identifiability

Practical identifiability concerns the ability of finite, noisy, imperfectly designed data to localize parameters, conditional on:

- the model and observation operator;
- the experimental design;
- the objective or likelihood;
- the assumed measurement-error model;
- the parameter domain and parameterization;
- numerical accuracy and optimization quality.

This is the correct primary framework for Paper A.

### Profile likelihood versus a profiled error objective

Raue et al. and later profile-likelihood work define profiles in a likelihood framework. A likelihood-ratio confidence threshold is meaningful only when the likelihood and error assumptions are explicit.

If Paper A minimizes MAPE, then the mathematically honest label is:

- **profiled MAPE objective**;
- **profiled prediction-error curve**; or
- **profiled objective surface**.

A MAPE profile may still be highly informative, but it is not automatically a profile likelihood, and arbitrary ratios of edge error to minimum error are not confidence intervals.

Two legitimate routes are available:

1. Keep MAPE for engineering comparability and call the result a **profiled MAPE objective**, supplementing it with bootstrap uncertainty and range-convergence checks.
2. Define an observation-level likelihood, for example on replicate concentrations or log concentrations, and then compute a genuine profile likelihood with likelihood-ratio intervals.

### Sloppiness, compensating manifolds, and identifiability

“Sloppiness” usually refers to a broad spectrum of local sensitivity, Fisher-information, or Hessian eigenvalues under a specified scaling and parameterization. It is related to, but not identical with, non-identifiability.

For Paper A, the safer descriptive terms are:

- **compensating profile valley**;
- **inventory–rate ridge**;
- **weakly curved parameter manifold**;
- **broad practical-equivalence region**.

Use “sloppy” only if the manuscript actually calculates and reports the scaled sensitivity or Hessian/Fisher-information spectrum, including parameter scaling.

### Integral versus time-resolved observations

There is no universal theorem that an integral or endpoint observable is uninformative. The appropriate claim is conditional:

> “For this model, tested parameter domain, observation operator, dataset, and objective, the cup-integrated observable weakly localizes the kinetic-rate multiplier after inventory profiling, whereas the fraction-resolved observations provide materially stronger localization.”

A useful simplified explanation is:

\[
y(t)=I\,g(k,t),
\]

where \(I\) is an inventory/level parameter and \(k\) is a kinetic-rate parameter. A single endpoint or integrated measurement,

\[
Y=I\,A(k),
\]

allows compensation through

\[
I=\frac{Y}{A(k)}
\]

whenever \(A(k)>0\). By contrast, two or more time-resolved observations can form ratios,

\[
\frac{y(t_j)}{y(t_\ell)}
=
\frac{g(k,t_j)}{g(k,t_\ell)},
\]

which eliminate the level \(I\). The rate may then be identifiable if that ratio map is sufficiently sensitive and injective over the relevant domain.

This is an intuition for the inventory–rate mechanism. It is **not** a structural-identifiability theorem for the full PDE model.

### Parameter confounding in reaction, transport, and dissolution models

The relevant general lesson from reaction–transport and dissolution inverse problems is not simply that “kinetics are hard to identify.” Rather:

- reaction rates, diffusivities, mass-transfer coefficients, initial inventories, boundary conditions, and transport parameters can generate similar changes in limited observations;
- local sensitivities can be nearly collinear;
- boundary-limited parameter estimates and asymmetric intervals are common;
- richer excitation and observation design can rotate or separate sensitivity directions;
- independent inventory measurements can be more valuable than adding more observations of the same integrated output.

Paper A should explicitly discuss these points rather than treating the inventory–rate ridge as uniquely coffee-specific.

### Experimental design for kinetic identification

The design principle is to create **non-collinear sensitivity directions**. For this problem, useful additions include:

- early, middle, and late fractions rather than one endpoint;
- multiple flow histories, pressures, temperatures, or grinds;
- independent soluble-inventory measurement;
- named-solute measurements rather than only aggregate TDS;
- a held-out condition not used to tune any parameter;
- sufficient replicates to estimate observation uncertainty.

A Fisher-information or sensitivity calculation can propose designs, but because the present model is nonlinear and profiles may be asymmetric or boundary-limited, candidate designs should be checked with profiles and simulation-based or bootstrap recovery tests.

---

## 1.3 Closest general prior art

The following references are the minimum defensible core. They are not decorative citations: each should support a specific statement in the manuscript.

| Topic | Closest references | What Paper A should take from them |
|---|---|---|
| Structural-identifiability definitions and methods | Chis et al. (2011); Villaverde et al. (2016); Villaverde (2019); Miao et al. (2011) | Separate ideal structural uniqueness from finite-data estimation. Do not infer structural non-identifiability from a numerical sweep. |
| Practical identifiability and profile likelihood | Raue et al. (2009); Kreutz (2013); Wieland et al. (2021); Heinrich et al. (2025); Simpson & Maclaren (2023) | Profiles expose asymmetric, bounded, or effectively unbounded uncertainty better than a local covariance alone. A true profile likelihood requires a likelihood. |
| Sloppiness and model manifolds | Gutenkunst et al. (2007); Transtrum et al. (2011, 2015); Apgar et al. (2010); Tönsing et al. (2014); Chis et al. (2016); White et al. (2016) | Sloppiness is not a synonym for non-identifiability. Compensation appears geometrically as a valley/manifold; experiment design can help but may not fully cure a sloppy model. |
| Practical identifiability in environmental/reaction/transport systems | Brun et al. (2001); Browning et al. (2024); Navarro-Laboulais et al. (2008); Haario et al. (2007) | Transport and kinetic parameters often confound; design and independent observations are needed. Parameter boundaries and model discrepancy matter. |
| Optimal experimental design | Banga & Balsa-Canto (2008); Bandara et al. (2009); Liepe et al. (2013); Lages et al. (2012); Apgar et al. (2010) | Choose sampling times and conditions that maximize parameter-separating information, then verify the design under nonlinear uncertainty. |

### Minimum citations and links

1. Chis, O.-T., Banga, J. R., & Balsa-Canto, E. (2011). Structural identifiability of systems biology models: A critical comparison of methods. *PLOS ONE, 6*, e27755. [https://doi.org/10.1371/journal.pone.0027755](https://doi.org/10.1371/journal.pone.0027755)
2. Raue, A., Kreutz, C., Maiwald, T., et al. (2009). Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood. *Bioinformatics, 25*, 1923–1929. [https://doi.org/10.1093/bioinformatics/btp358](https://doi.org/10.1093/bioinformatics/btp358)
3. Villaverde, A. F., Barreiro, A., & Papachristodoulou, A. (2016). Structural identifiability of dynamic systems biology models. *PLOS Computational Biology, 12*, e1005153. [https://doi.org/10.1371/journal.pcbi.1005153](https://doi.org/10.1371/journal.pcbi.1005153)
4. Villaverde, A. F. (2019). Observability and structural identifiability of nonlinear biological systems. *Complexity*, 8497093. [https://doi.org/10.1155/2019/8497093](https://doi.org/10.1155/2019/8497093)
5. Wieland, F.-G., Hauber, A. L., Rosenblatt, M., Tönsing, C., & Timmer, J. (2021). On structural and practical identifiability. *Current Opinion in Systems Biology, 25*, 60–69. [https://doi.org/10.1016/j.coisb.2021.03.005](https://doi.org/10.1016/j.coisb.2021.03.005)
6. Heinrich, R. et al. (2025). On structural and practical identifiability: Current status and update of results. *Current Opinion in Systems Biology, 41*, 100546. [https://doi.org/10.1016/j.coisb.2025.100546](https://doi.org/10.1016/j.coisb.2025.100546)
7. Simpson, M. J., & Maclaren, O. J. (2023). Profile-Wise Analysis: A profile likelihood-based workflow for identifiability analysis, estimation and prediction for a class of mechanistic models. *PLOS Computational Biology, 19*, e1011515. [https://doi.org/10.1371/journal.pcbi.1011515](https://doi.org/10.1371/journal.pcbi.1011515)
8. Miao, H., Xia, X., Perelson, A. S., & Wu, H. (2011). On identifiability of nonlinear ODE models and applications in viral dynamics. *SIAM Review, 53*, 3–39. [https://doi.org/10.1137/090757009](https://doi.org/10.1137/090757009)
9. Gutenkunst, R. N., Waterfall, J. J., Casey, F. P., et al. (2007). Universally sloppy parameter sensitivities in systems biology models. *PLOS Computational Biology, 3*, e189. [https://doi.org/10.1371/journal.pcbi.0030189](https://doi.org/10.1371/journal.pcbi.0030189)
10. Transtrum, M. K., Machta, B. B., & Sethna, J. P. (2011). Geometry of nonlinear least squares with applications to sloppy models and optimization. *Physical Review E, 83*, 036701. [https://doi.org/10.1103/PhysRevE.83.036701](https://doi.org/10.1103/PhysRevE.83.036701)
11. Transtrum, M. K., Machta, B. B., Brown, K. S., et al. (2015). Perspective: Sloppiness and emergent theories in physics, biology, and beyond. *Journal of Chemical Physics, 143*, 010901. [https://doi.org/10.1063/1.4923066](https://doi.org/10.1063/1.4923066)
12. Apgar, J. F., Witmer, D. K., White, F. M., & Tidor, B. (2010). Sloppy models, parameter uncertainty, and the role of experimental design. *Molecular BioSystems, 6*, 1890–1900. [https://doi.org/10.1039/B918098B](https://doi.org/10.1039/B918098B)
13. Tönsing, C., Timmer, J., & Kreutz, C. (2014). Cause and cure of sloppiness in ordinary differential equation models. *Physical Review E, 90*, 023303. [https://doi.org/10.1103/PhysRevE.90.023303](https://doi.org/10.1103/PhysRevE.90.023303)
14. Chis, O.-T., Villaverde, A. F., Banga, J. R., & Balsa-Canto, E. (2016). On the relationship between sloppiness and identifiability. *Mathematical Biosciences, 282*, 147–161. [https://doi.org/10.1016/j.mbs.2016.10.009](https://doi.org/10.1016/j.mbs.2016.10.009)
15. White, A., Tolman, M., Thames, H. D., Withers, H. R., Mason, K. A., & Transtrum, M. K. (2016). The limitations of model-based experimental design and parameter estimation in sloppy systems. *PLOS Computational Biology, 12*, e1005227. [https://doi.org/10.1371/journal.pcbi.1005227](https://doi.org/10.1371/journal.pcbi.1005227)
16. Brun, R., Reichert, P., & Künsch, H. R. (2001). Practical identifiability analysis of large environmental simulation models. *Water Resources Research, 37*, 1015–1030. [https://doi.org/10.1029/2000WR900350](https://doi.org/10.1029/2000WR900350)
17. Browning, A. P., et al. (2024). Structural identifiability analysis of linear reaction–advection–diffusion processes in mathematical biology. *Proceedings of the Royal Society A, 480*, 20230911. [https://doi.org/10.1098/rspa.2023.0911](https://doi.org/10.1098/rspa.2023.0911)
18. Navarro-Laboulais, J., et al. (2008). Practical identifiability analysis in dynamic gas–liquid reactors: Optimal experimental design for mass-transfer parameters determination. *Computers & Chemical Engineering, 32*, 2382–2394. [https://doi.org/10.1016/j.compchemeng.2007.12.004](https://doi.org/10.1016/j.compchemeng.2007.12.004)
19. Haario, H., Kalachev, L., & Tirronen, V. (2007). Optimal experimental protocol for identification of dissolution parameters in presence of fast reaction. *Chemical Engineering Science, 62*, 929–934. [https://doi.org/10.1016/j.ces.2006.10.023](https://doi.org/10.1016/j.ces.2006.10.023)
20. Banga, J. R., & Balsa-Canto, E. (2008). Parameter estimation and optimal experimental design. *Essays in Biochemistry, 45*, 195–210. [https://doi.org/10.1042/BSE0450195](https://doi.org/10.1042/BSE0450195)
21. Bandara, S., Schlöder, J. P., Eils, R., Bock, H. G., & Meyer, T. (2009). Optimal experimental design for parameter estimation of a cell signaling model. *PLOS Computational Biology, 5*, e1000558. [https://doi.org/10.1371/journal.pcbi.1000558](https://doi.org/10.1371/journal.pcbi.1000558)
22. Liepe, J., Filippi, S., Komorowski, M., & Stumpf, M. P. H. (2013). Maximizing the information content of experiments in systems biology. *PLOS Computational Biology, 9*, e1002888. [https://doi.org/10.1371/journal.pcbi.1002888](https://doi.org/10.1371/journal.pcbi.1002888)
23. Lages, N. F., et al. (2012). Optimization of time-course experiments for kinetic model discrimination. *PLOS ONE, 7*, e32749. [https://doi.org/10.1371/journal.pone.0032749](https://doi.org/10.1371/journal.pone.0032749)
24. Kreutz, C. (2013). Profile likelihood in systems biology. *FEBS Journal, 280*, 2564–2571. [https://doi.org/10.1111/febs.12276](https://doi.org/10.1111/febs.12276)

---

## 1.4 Coffee-extraction lineage and closest domain prior art

### Most relevant empirical fraction studies

| Study | Observation design | Conditions | Relevance to Paper A | Independence/use |
|---|---|---|---|---|
| **Kuhn et al. (2017)** | High-time-resolution caffeine and trigonelline extraction | Commercial espresso machine; three particle-size distributions; two tamping pressures; triplicates | Closest prior art for named-solute, multi-PSD kinetic identification | Strongest raw-data acquisition target; raw machine-readable data not located in the scoped public search |
| **Schmieder et al. (2023)** | Ten consecutive fractions; caffeine, trigonelline, 5-CQA, TDS | Flow, particle size, temperature design | Core fraction lineage already represented in the repo | Not independent of Pannusch; useful for in-sample verification only |
| **Pannusch et al. (2024)** | Model-based kinetic chart using the Schmieder experimental lineage | Representative taste compounds and TDS | Direct model/data lineage | Not an independent external dataset |
| **Vaca Guerra et al. (2024)** | Espresso-component extraction with dispersive packed-bed model and multiple packed-bed/PSD configurations | Named components and TDS; tracer/dispersion measurements | Strong second external acquisition candidate | Article states data available on request |
| **Waszkiewicz et al. (2026)** | Five-second TDS fractions, three replicate shots, time-dependent flow | Second café-grade rig; one coffee and grind | Immediately usable independent external TDS trajectory | Public data and code; not named-solute or multi-grind |
| **Sánchez-López et al. (2014, 2016)** | Online time-resolved volatile extraction by PTR-ToF-MS | Espresso machine | Demonstrates rich time-resolved observation designs | Observation class differs from dissolved named solutes |
| **Maille (2024 thesis)** | Early-time caffeine, 3-CQA, citric, malic, quinic acid trajectories | Well-mixed/batch setup; several sieve fractions | Useful fallback for kinetic-shape and observation-design tests | Not espresso percolation; do not present as an external espresso validation |

### Core coffee modelling lineage

The manuscript should connect its model/data question to, at minimum:

- Moroney et al. (2015): experimentally validated multiscale coffee-extraction model.
- Moroney et al. (2016): asymptotic analysis of dominant extraction mechanisms.
- Moroney et al. (2017): well-mixed extraction kinetics.
- Moroney et al. (2019): extraction non-uniformity in porous coffee beds.
- Melrose et al. (2018): modern brewing-control-chart framing.
- Cameron et al. (2020): systematic espresso modelling and experiment.
- Ellero & Navarini (2019): mesoscopic espresso-extraction simulation.
- Giacomini et al. (2020): water flow and transport in porous media for in-silico espresso.
- Sano et al. (2019): volume-averaged coffee-extraction model.
- Egidi et al. (2022) and Giacomini et al. (2023): advection–diffusion–reaction and reduced percolation models.
- Schmieder et al. (2023), Pannusch et al. (2024), and Vaca Guerra et al. (2024): component-resolved espresso kinetics.
- Kuhn et al. (2017): time-resolved named-solute extraction under varied PSD.
- Waszkiewicz et al. (2026): time-resolved TDS and flow on a second rig.

### Coffee references and links

1. Kuhn, M., Lang, S., Bezold, F., Minceva, M., & Briesen, H. (2017). Time-resolved extraction of caffeine and trigonelline from finely-ground espresso coffee with varying particle sizes and tamping pressures. *Journal of Food Engineering, 206*, 37–47. [https://doi.org/10.1016/j.jfoodeng.2017.03.002](https://doi.org/10.1016/j.jfoodeng.2017.03.002)
2. Schmieder, B. K. L., et al. (2023). Influence of flow rate, particle size, and temperature on espresso extraction kinetics. *Foods, 12*, 2871. [https://doi.org/10.3390/foods12152871](https://doi.org/10.3390/foods12152871)
3. Pannusch, S., et al. (2024). Model-based kinetic espresso brewing control chart for representative taste components. *Journal of Food Engineering, 367*, 111887. [https://doi.org/10.1016/j.jfoodeng.2023.111887](https://doi.org/10.1016/j.jfoodeng.2023.111887)  
   Data archive: [https://doi.org/10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1)
4. Vaca Guerra, M., Harshe, Y. M., Fries, L., et al. (2024). Modeling the extraction of espresso components as dispersed flow through a packed bed. *Journal of Food Engineering, 368*, 111913. [https://doi.org/10.1016/j.jfoodeng.2023.111913](https://doi.org/10.1016/j.jfoodeng.2023.111913)
5. Waszkiewicz, R., Myck, F., Białas, Ł., et al. (2026). Under pressure: Poroelastic regulation of flow in espresso brewing. *Physics of Fluids, 38*, 063113. [https://doi.org/10.1063/5.0319611](https://doi.org/10.1063/5.0319611)
6. Sánchez-López, J. A., et al. (2014). Insight into the time-resolved extraction of aroma compounds during espresso coffee preparation: Online monitoring by PTR-ToF-MS. *Analytical Chemistry, 86*, 11696–11704. [https://doi.org/10.1021/ac502992k](https://doi.org/10.1021/ac502992k)
7. Sánchez-López, J. A., et al. (2016). Extraction kinetics of coffee aroma compounds using a semi-automatic machine: On-line analysis by PTR-ToF-MS. *International Journal of Mass Spectrometry*. [https://doi.org/10.1016/j.ijms.2016.02.015](https://doi.org/10.1016/j.ijms.2016.02.015)
8. Maille, D. (2024). *Measuring Coffee Extraction Kinetics at Early Time Scales* [Doctoral thesis, University of Sheffield]. [https://etheses.whiterose.ac.uk/id/eprint/36281/](https://etheses.whiterose.ac.uk/id/eprint/36281/)
9. Moroney, K. M., Lee, W. T., O’Brien, S. B. G., Suijver, F., & Marra, J. (2015). Modelling of coffee extraction during brewing using multiscale methods: An experimentally validated model. *Chemical Engineering Science, 137*, 216–234. [https://doi.org/10.1016/j.ces.2015.06.003](https://doi.org/10.1016/j.ces.2015.06.003)
10. Moroney, K. M., et al. (2016). Asymptotic analysis of the dominant mechanisms in the coffee extraction process. *SIAM Journal on Applied Mathematics, 76*, 2196–2217. [https://doi.org/10.1137/15M1036658](https://doi.org/10.1137/15M1036658)
11. Moroney, K. M., et al. (2017). Coffee extraction kinetics in a well mixed system. *Journal of Mathematics in Industry, 7*, 3. [https://doi.org/10.1186/s13362-016-0024-6](https://doi.org/10.1186/s13362-016-0024-6)
12. Moroney, K. M., et al. (2019). Analysing extraction uniformity from porous coffee beds using mathematical modelling and computational fluid dynamics approaches. *PLOS ONE, 14*, e0219906. [https://doi.org/10.1371/journal.pone.0219906](https://doi.org/10.1371/journal.pone.0219906)
13. Melrose, J. R., Roman-Corrochano, B., Montoya-Guerra, M., & Bakalis, S. (2018). Toward a new brewing control chart for the 21st century. *Journal of Agricultural and Food Chemistry, 66*, 5301–5309. [https://doi.org/10.1021/acs.jafc.7b04848](https://doi.org/10.1021/acs.jafc.7b04848)
14. Cameron, M. I., et al. (2020). Systematically improving espresso: Insights from mathematical modeling and experiment. *Matter, 2*, 631–648. [https://doi.org/10.1016/j.matt.2019.12.019](https://doi.org/10.1016/j.matt.2019.12.019)
15. Ellero, M., & Navarini, L. (2019). Mesoscopic modelling and simulation of espresso coffee extraction. *Journal of Food Engineering, 263*, 181–194. [https://doi.org/10.1016/j.jfoodeng.2019.05.038](https://doi.org/10.1016/j.jfoodeng.2019.05.038)
16. Giacomini, J., et al. (2020). Water flow and transport in porous media for in-silico espresso coffee. *International Journal of Multiphase Flow, 126*, 103252. [https://doi.org/10.1016/j.ijmultiphaseflow.2020.103252](https://doi.org/10.1016/j.ijmultiphaseflow.2020.103252)
17. Sano, Y., et al. (2019). Mathematical model for coffee extraction based on the volume averaging theory. *Journal of Food Engineering, 263*, 1–12. [https://doi.org/10.1016/j.jfoodeng.2019.05.025](https://doi.org/10.1016/j.jfoodeng.2019.05.025)
18. Egidi, N., et al. (2022). An advection–diffusion–reaction model for coffee percolation. *Computational and Applied Mathematics, 41*. [https://doi.org/10.1007/s40314-022-01929-9](https://doi.org/10.1007/s40314-022-01929-9)
19. Giacomini, J., et al. (2023). CMMSE: A reduced percolation model for espresso coffee. *Journal of Mathematical Chemistry, 61*. [https://doi.org/10.1007/s10910-022-01428-6](https://doi.org/10.1007/s10910-022-01428-6)
20. Smrke, S., Eiermann, A., & Yeretzian, C. (2024). The role of fines in espresso extraction dynamics. *Scientific Reports, 14*. [https://doi.org/10.1038/s41598-024-55831-x](https://doi.org/10.1038/s41598-024-55831-x)
21. Khamitova, G., et al. (2020). Optimization of espresso coffee extraction through variation of particle sizes, perforated disk height and filtration time. *Food Chemistry, 314*, 126220. [https://doi.org/10.1016/j.foodchem.2020.126220](https://doi.org/10.1016/j.foodchem.2020.126220)
22. Estévez-Sánchez, K. H., et al. (2025). Effect of particle size distribution on mass transfer during solid-fluid extraction and its application to coffee brewing. *Journal of Food Engineering*, 112511. [https://doi.org/10.1016/j.jfoodeng.2025.112511](https://doi.org/10.1016/j.jfoodeng.2025.112511)
23. Matias, A. F., Coelho, R. C., Andrade, J. S., Araújo, N. A. M., & Vynnycky, M. (2025). Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling. *Physics of Fluids, 37*, 013383. [https://doi.org/10.1063/5.0245167](https://doi.org/10.1063/5.0245167)

---

## 1.5 Novelty judgment and insertion-ready novelty statement

### Judgment

#### (a) New espresso case study

**Likely yes, with cautious wording.** The scoped search found extensive coffee-extraction modelling, time-resolved fractions, multi-grind studies, and broad identifiability theory. It did not locate a prior espresso paper whose central purpose is a systematic practical-identifiability analysis of inventory–rate compensation combined with internal holdout and independent cross-dataset prediction.

This is not proof of absolute priority. Before submission, the authors should rerun the search in Scopus and Web of Science or an equivalent bibliographic database and archive the results.

#### (b) New observation for this model/data pair

**Yes, provided the result survives the required corrections.** It is publishable to show that:

- the selected cup-level observation weakly localizes the rate after inventory profiling;
- time-resolved fractions materially narrow the practical-equivalence region;
- frozen-parameter cross-dataset or cross-grind prediction is distinguishable from target-data refitting.

This remains contingent on fixing the matched-endpoint, actual-full-cup, exact-profile, uncertainty, and boundary-optimum blockers.

#### (c) New general method

**No.** Profile likelihood/objective profiling, practical-identifiability analysis, sensitivity geometry, and optimal experimental design are established. The contribution is their careful application and operationalization in espresso extraction.

### Insertion-ready novelty paragraph

> Mechanistic coffee-extraction models have developed from well-mixed and multiscale descriptions to porous-bed, dispersion, and component-resolved espresso models, while time-resolved experiments have quantified extraction trajectories across particle sizes and operating conditions. Separately, structural and practical identifiability, profile likelihood, parameter-compensation manifolds, and model-based experimental design are mature inverse-problem tools. To our knowledge, based on a documented scoping search, these lines have not previously been combined in a systematic practical-identifiability study of inventory–rate confounding in a multi-solute espresso-extraction model evaluated with internal holdouts and independent coffee datasets. Our contribution is therefore an espresso case study and a model–data-specific result, not a new general identifiability method: under the tested whole-cup design, inventory and kinetic rate occupy a broad compensating profile, whereas fraction-resolved observations provide substantially stronger localization of the rate.

### Required qualification immediately after that paragraph

> These results do not establish that cup-integrated observations are structurally incapable of identifying extraction kinetics in general. They establish weak practical localization for the tested model, observation map, datasets, parameter domain, and error model.

---

## 1.6 Insertion-ready related-work section

Claude Code may adapt the following four-paragraph structure directly.

### Paragraph 1 — structural and practical identifiability

> Parameter estimation in mechanistic models must distinguish structural identifiability from practical identifiability. Structural identifiability concerns uniqueness under ideal, noise-free observations for a specified model, input, initial condition, parameterization, and observation map, whereas practical identifiability concerns whether finite and noisy data localize the parameters under the actual experimental design and objective. Structural-identifiability methods have been compared and systematized by Chis et al. (2011), Miao et al. (2011), Villaverde et al. (2016), and Villaverde (2019). Raue et al. (2009), Wieland et al. (2021), Heinrich et al. (2025), and Simpson and Maclaren (2023) emphasize that a parameter may be structurally identifiable yet practically weakly constrained, and that nonlinear profiles can reveal asymmetric or effectively unbounded uncertainty that a local covariance approximation misses.

### Paragraph 2 — profiles, sloppiness, and parameter compensation

> Profile-likelihood and profile-wise analyses characterize how the optimum changes when one parameter is fixed and the remaining parameters are re-optimized. This is particularly useful for detecting compensation, boundaries, and asymmetric uncertainty. In parallel, work on “sloppy” models describes broad spectra of parameter sensitivities and a geometric model manifold containing narrow and broad directions (Gutenkunst et al., 2007; Transtrum et al., 2011, 2015). Sloppiness and identifiability are related but not equivalent (Tönsing et al., 2014; Chis et al., 2016), and experimental design may improve some weak directions without guaranteeing that all parameters become well determined (Apgar et al., 2010; White et al., 2016). We therefore use the descriptive term inventory–rate profile valley unless a scaled sensitivity-spectrum analysis is explicitly reported.

### Paragraph 3 — reaction/transport confounding and design

> Similar parameter-confounding problems occur in environmental, reaction–transport, gas–liquid mass-transfer, and dissolution models, where kinetic coefficients, diffusivities, transfer coefficients, inventories, and boundary conditions can induce nearly collinear output changes (Brun et al., 2001; Navarro-Laboulais et al., 2008; Haario et al., 2007; Browning et al., 2024). Optimal experimental-design studies seek inputs, conditions, and sampling times that create distinct sensitivity directions (Banga and Balsa-Canto, 2008; Bandara et al., 2009; Liepe et al., 2013; Lages et al., 2012). For extraction models, this motivates combining early, middle, and late fractions, multiple operating conditions, and independent inventory measurements rather than relying on a single integrated endpoint.

### Paragraph 4 — coffee lineage and gap

> Coffee-extraction modelling includes multiscale and asymptotic formulations (Moroney et al., 2015, 2016), well-mixed kinetics (Moroney et al., 2017), porous-bed non-uniformity (Moroney et al., 2019), brewing-control-chart and espresso optimization studies (Melrose et al., 2018; Cameron et al., 2020), mesoscopic and porous-media simulations (Ellero and Navarini, 2019; Giacomini et al., 2020), and component-resolved or dispersive packed-bed models (Schmieder et al., 2023; Pannusch et al., 2024; Vaca Guerra et al., 2024). Time-resolved experiments have measured caffeine and trigonelline across particle-size distributions (Kuhn et al., 2017), representative nonvolatile solutes and TDS across process conditions (Schmieder et al., 2023), volatile release online (Sánchez-López et al., 2014, 2016), and independent TDS fractions with simultaneous flow measurements (Waszkiewicz et al., 2026). In our documented scoping search, we did not find an espresso study that explicitly profiles inventory–rate compensation and separates in-sample localization, internal holdout, frozen external prediction, and target-data refitting. Paper A addresses that applied gap using established identifiability methods.

---

## 1.7 Search protocol to archive in the repository

### Review label

Call this a **documented systematic scoping search**, not a PRISMA-complete systematic review. A web and publisher search can identify strong prior art but cannot establish exhaustive absence.

### Research questions

1. How do prior studies distinguish structural and practical identifiability?
2. Which methods are recommended for nonlinear practical-identifiability assessment?
3. How are sloppiness, model manifolds, and compensating parameters related to identifiability?
4. What confounding patterns are reported in reaction, transport, mass-transfer, and dissolution models?
5. Which experimental designs improve kinetic-parameter identification?
6. What is known about endpoint/integral versus time-resolved observation designs?
7. Which coffee studies use fractions, inventories, named solutes, TDS, multiple grinds/PSDs, or cross-condition fits?
8. Has an espresso study already made the same specific inventory–rate identifiability and transfer claim?

### Sources

At submission, search at least:

- Scopus;
- Web of Science Core Collection;
- Crossref/DOI and publisher pages;
- PubMed/PLOS where relevant;
- institutional repositories and theses;
- backward and forward citation snowballing;
- data repositories such as Zenodo and Mendeley Data;
- GitHub only for code/data provenance, not as the sole bibliographic source.

### Search strings

Use title/abstract/keyword fields where supported.

```text
1. ("structural identifiability" OR "practical identifiability")
   AND (ODE OR PDE OR "mechanistic model")

2. "profile likelihood" AND identifiability

3. (sloppiness OR "model manifold" OR "compensating parameter*"
   OR "parameter confounding") AND identifiability

4. identifiability AND
   ("reaction-advection-diffusion" OR "reactive transport"
   OR dissolution OR "mass transfer" OR "packed bed")

5. ("optimal experimental design" OR OED)
   AND (kinetic OR "parameter estimation" OR identifiability)

6. (endpoint OR integral OR cumulative OR "time-resolved" OR fraction*)
   AND (identifiability OR "parameter estimation")

7. (espresso OR "coffee extraction")
   AND ("time-resolved" OR fraction* OR caffeine OR trigonelline
   OR chlorogenic OR "5-CQA" OR TDS OR model*)

8. ("coffee extraction")
   AND (inventory OR "initial concentration" OR multi-grind
   OR "particle size distribution" OR transfer OR identifiability)
```

### Screening rules

Include a paper if it contributes at least one of:

- a definition or method directly relevant to structural/practical identifiability;
- profile likelihood or nonlinear uncertainty;
- sloppiness/manifold/compensation theory;
- identifiability in a reaction, transport, dissolution, or packed-bed model;
- experimental design for kinetic identification;
- empirical or modelled coffee extraction with time resolution, fractions, named solutes, TDS, inventories, or multiple PSDs/grinds.

Exclude:

- purely sensory coffee studies with no extraction or model relevance;
- papers that mention “identification” only as classification;
- generic optimization papers with no parameter-identification content;
- coffee chemistry papers with only one final-cup measurement unless needed for analyte-definition context;
- duplicate conference abstracts when a full paper exists.

### Evidence matrix columns

```text
record_id
citation
doi_or_url
year
domain
model_class
observation_type
structural_or_practical
method
likelihood_or_objective
uncertainty_method
parameter_boundaries_reported
experimental_design
integral_vs_time_resolved
coffee_relevance
paper_a_implication
include
exclusion_reason
search_source
search_date
```

### Repository files

```text
docs/literature_search/
├── SEARCH_PROTOCOL.md
├── SEARCH_LOG.csv
├── SCREENING.csv
├── EVIDENCE_MATRIX.csv
├── references.bib
└── README.md
```

### Submission gate for M9

M9 is complete only when:

- [ ] exact search dates, databases, fields, and query strings are archived;
- [ ] RIS/BibTeX/CSV exports are retained;
- [ ] duplicates are removed;
- [ ] title/abstract screening and full-text screening are recorded;
- [ ] exclusions have reasons;
- [ ] backward and forward snowballing is documented;
- [ ] the novelty wording is checked against the final included set;
- [ ] the manuscript says “to our knowledge, following a documented scoping search” rather than asserting categorical priority;
- [ ] the source list and manuscript bibliography agree;
- [ ] no citation is inserted from an unverified placeholder.

---

# 2. Independent fraction-resolved dataset

## 2.1 Dataset available immediately: Waszkiewicz et al. (2026)

### Source

**Article**

Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M., Szymczak, P., & Lisicki, M. (2026). Under pressure: Poroelastic regulation of flow in espresso brewing. *Physics of Fluids, 38*, 063113.  
[https://doi.org/10.1063/5.0319611](https://doi.org/10.1063/5.0319611)

**Repository**

[https://github.com/RadostW/espresso](https://github.com/RadostW/espresso)

**Archived release**

[https://doi.org/10.5281/zenodo.18046315](https://doi.org/10.5281/zenodo.18046315)

**Relevant source files**

- Replicate-level TDS:  
  [measurements_tds_calibration/tds.csv](https://github.com/RadostW/espresso/blob/main/measurements_tds_calibration/tds.csv)
- Formatted mean and standard deviation:  
  [formatted_measurements/tds.csv](https://github.com/RadostW/espresso/blob/main/formatted_measurements/tds.csv)
- Time-dependent pressure, mass, and flow data:  
  [formatted_measurements/time_dependent.csv](https://github.com/RadostW/espresso/blob/main/formatted_measurements/time_dependent.csv)
- Archived code release/tag:  
  [v1.0.1](https://github.com/RadostW/espresso/releases/tag/v1.0.1)

### Experimental characteristics relevant to Paper A

The article reports:

- a café-grade two-group Sanremo Zoe Competition machine;
- an IMS Competizione basket;
- a single-origin Brazil coffee, light to medium-light espresso roast;
- a Fiorenzato F64 EVO grinder at a fixed setting;
- a nominal 18.5 g dry dose;
- a typical 2:1 target of about 37 g beverage around 32 s at 9 bar;
- TDS measured by VST-LAB optical refractometer;
- the espresso divided into 5-second collection intervals;
- three repeated shots, with results averaged;
- simultaneous time-dependent mass/flow and pressure measurements;
- public data and analysis code.

### Raw replicate-level TDS values

The public raw CSV contains:

```csv
time_s,tds_percent_1,tds_percent_2,tds_percent_3
2.5,24.36,,
7.5,28.58,20.62,21.24
12.5,27.68,20.97,26.83333333
17.5,19.28,12.46,18.5
22.5,12.15,6.21,9.246666667
27.5,7.26,3.6,4.48
32.5,4.47,1.91,2.37
37.5,2.84,1.11,1.466666667
42.5,1.99,0.79,0.9
47.5,1.39,0.48,0.5766666667
52.5,0.99,0.25,0.4066666667
57.5,0.99,0.25,0.1966666667
```

The formatted file reports:

```csv
time__s,tds__percent,tds_std__percent
2.5000,24.3600,
7.5000,23.4800,2.5563
12.5000,25.1611,2.1098
17.5000,16.7467,2.1551
22.5000,9.2022,1.7149
27.5000,5.1133,1.1030
32.5000,2.9167,0.7879
37.5000,1.8056,0.5274
42.5000,1.2267,0.3830
47.5000,0.8156,0.2886
52.5000,0.5489,0.2251
57.5000,0.4789,0.2560
```

### What this dataset does and does not unblock

It **does unblock**:

- an independent second-rig fraction-resolved TDS test;
- a frozen external prediction of the TDS trajectory;
- an external comparison of cup-integrated versus fraction-resolved objective localization;
- a test using an observed time-dependent flow trace rather than an assumed constant flow;
- a more honest §6 with at least one genuinely external panel.

It **does not unblock**:

- independent named-solute identification;
- an independent multi-solute headline result;
- independent multi-grind or multi-PSD identification;
- a universal claim about all espresso conditions;
- treating TDS as interchangeable with gravimetric total solids or with any named solute.

### Important provenance discrepancy to resolve before fitting

The paper's Figure 7 describes a shot split into **14 five-second fractions**, including an initial empty tube. The public TDS CSV contains **12 midpoint bins from 2.5 to 57.5 s**. The article also states that brewer activation precedes first drops by a couple of seconds.

Do not silently choose a time origin. Before the external analysis, document:

1. whether the TDS `time_s` values are relative to brewer activation, first liquid at the cup, or vial transitions;
2. whether the 2.5 s row represents the 0–5 s collection bin;
3. why the public file has 12 TDS bins while the figure describes 14 fractions;
4. how the initial empty interval is represented;
5. whether the matching flow trace is aligned to brewer activation, 5 g cup mass, or another reference.

If author clarification is not obtained, run a declared time-offset sensitivity and report the ambiguity as a limitation.

---

## 2.2 Correct observation operator for fraction data

A fraction measurement is not generally a point concentration at the midpoint. It is a concentration averaged over the collected interval, normally weighted by outflow mass or volume.

For fraction \(i\), with interval \([t_i,t_{i+1}]\), use:

\[
\bar C_i^{\mathrm{pred}}
=
\frac{
\int_{t_i}^{t_{i+1}}
\dot m_{\mathrm{out}}(t)\,C_{\mathrm{out}}(t)\,dt
}{
\int_{t_i}^{t_{i+1}}
\dot m_{\mathrm{out}}(t)\,dt
}.
\]

If the model works in volumetric flow and concentration per volume, use the internally consistent volumetric analogue. Do not mix mass and volume without a documented density convention.

For the whole-cup counterpart over \([t_0,t_f]\):

\[
C_{\mathrm{cup}}^{\mathrm{pred}}
=
\frac{
\int_{t_0}^{t_f}
\dot m_{\mathrm{out}}(t)\,C_{\mathrm{out}}(t)\,dt
}{
\int_{t_0}^{t_f}
\dot m_{\mathrm{out}}(t)\,dt
}.
\]

The same simulated trajectory must generate both the fraction and integrated observables. That is the cleanest information-content comparison.

---

## 2.3 Recommended external-analysis design

### Stage A — provenance and adapter only

Create a source card and immutable copy of the archived source data. Record:

- article DOI;
- Zenodo DOI and version;
- GitHub tag and commit;
- file paths and SHA-256 hashes;
- license;
- rig, coffee, dose, grinder, basket, pressure, and measurement method;
- time-origin ambiguity;
- missing first-bin replicates.

Suggested tree:

```text
puckworks/data/waszkiewicz2026/
├── SOURCE.md
├── manifest.json
├── tds_raw.csv
├── tds_formatted.csv
├── flow_9bar.csv
└── adapter.py
```

Keep source values unchanged. Any time shift, filtering, interpolation, or unit conversion must occur in derived output with a logged transformation.

### Stage B — preregister the prediction

Before looking at external-fit results, freeze:

- which Paper A calibration parameter set is being transferred;
- which parameters are fixed;
- which parameters, if any, may be adapted from source metadata without using the target TDS values;
- the flow trace;
- time origin and offset sensitivity;
- interval definitions;
- objective and uncertainty treatment;
- exclusion rules;
- parameter bounds;
- success criteria.

Commit this as a machine-readable configuration, for example:

```yaml
dataset: waszkiewicz2026
source_release: v1.0.1
source_archive_doi: 10.5281/zenodo.18046315
analyte: aggregate_tds_proxy
prediction_mode: frozen_external
fraction_intervals_s:
  - [0, 5]
  - [5, 10]
  - [10, 15]
  - [15, 20]
  - [20, 25]
  - [25, 30]
  - [30, 35]
  - [35, 40]
  - [40, 45]
  - [45, 50]
  - [50, 55]
  - [55, 60]
time_offsets_s: [0, 2, 4]
missing_replicate_policy: "no imputation"
primary_metric: "replicate-aware log-scale or stated weighted objective"
secondary_metrics:
  - MAPE
  - RMSE
  - trajectory correlation
```

### Stage C — frozen external prediction

This is the strongest available test.

- Freeze the kinetic-rate parameters learned elsewhere.
- Freeze the inventory unless it can be supplied independently from source metadata.
- Use the source's measured flow trace and interval operator.
- Predict all reported fractions.
- Report every bin, uncertainty, residual, and cumulative-cup prediction.
- Do not tune a time shift after seeing the fit unless it is explicitly labelled as a sensitivity or nuisance-parameter profile.

Name this:

> **Independent external TDS trajectory prediction**

A poor result is still scientifically useful and should be retained.

### Stage D — constrained external adaptation

A secondary analysis may permit **inventory-only adaptation** while keeping rate fixed, provided this is prespecified and scientifically justified. This asks whether a source-specific inventory level can adapt while the transferred rate preserves trajectory shape.

Name this:

> **External prediction with prespecified inventory adaptation**

It is weaker than a fully frozen prediction and must not be pooled with it.

### Stage E — target-data profile or refit

A full target-data profile or refit can ask whether the external fractions localize the rate, but it is not validation of that fitted rate.

Name this:

> **External-dataset objective localization**  
> or  
> **target-data diagnostic refit**

Do not call it external validation.

### Stage F — fraction versus integral comparison

Using the same external shot trajectory:

1. compute the fraction-resolved objective;
2. integrate those predictions and observations to a cup-level aggregate using the available fraction masses/flow;
3. profile inventory versus rate under each observation design;
4. compare:
   - profile width;
   - bootstrap interval;
   - boundary contact;
   - predictive interval;
   - sensitivity to parameter-domain expansion.

The conclusion must be restricted to this dataset and proxy.

---

## 2.4 Missing-data and uncertainty rules

- The first 2.5 s row has only one observed TDS replicate. Do not manufacture a standard deviation.
- Do not create pseudo-replicates from the reported mean.
- For uncertainty-weighted fitting, either omit that row from the weighted primary fit or use a clearly stated robust/unweighted treatment and include it in a sensitivity analysis.
- Preserve the three raw replicate columns.
- Report between-shot variability, not only standard errors of the mean.
- Treat a time-offset ambiguity as a nuisance sensitivity, not as a free post hoc correction.
- Do not interpolate the observations to the solver grid and then treat interpolated points as independent data.
- Use the source's measured 9-bar flow trace if that is the relevant experimental condition.
- Report results both including and excluding the earliest bin because initial wetting, air displacement, dilution, and collection timing are most uncertain there.

---

## 2.5 Code-level acceptance tests for the adapter

At minimum:

```text
test_source_hashes_match_manifest
test_all_tds_values_and_missingness_preserved
test_fraction_midpoints_map_to_declared_intervals
test_interval_prediction_is_flow_weighted_not_midpoint_sampled
test_time_offset_is_explicit_and_logged
test_missing_first_bin_replicates_are_not_imputed
test_mass_and_volume_units_cannot_be_mixed_silently
test_frozen_external_path_cannot_call_target_fit
test_inventory_only_adapter_cannot_modify_rate
test_target_refit_outputs_are_labelled_diagnostic
test_whole_cup_is_integrated_over_all_available_intervals
test_external_results_record_source_release_and_commit
```

Each result file should carry:

```text
source_dataset
source_release
source_commit
source_file_hashes
puckworks_commit
model_component_versions
parameter_source
parameters_frozen
parameters_adapted
time_origin
time_offset
observation_operator
objective
solver_tolerances
parameter_bounds
boundary_flags
```

---

## 2.6 Language for §6 after adding the dataset

### Recommended section title

> **6. In-sample fraction verification and independent external TDS trajectory test**

### Recommended opening

> The Pannusch fraction data are part of the model's own calibration lineage and therefore provide in-sample verification of objective localization rather than independent identification. To add an external observation class, we separately evaluate the public five-second TDS fractions of Waszkiewicz et al. (2026), collected on a second café-grade rig with matching time-dependent flow measurements.

### Permitted conclusion if supported

> On the independent TDS trajectory, fraction-resolved observations produced a more localized profiled objective than the corresponding cup-integrated aggregate under the tested model, parameter domain, time-alignment assumptions, and aggregate-solids observation operator.

### Strongest permitted cross-study conclusion if supported by both datasets

> Across the in-sample named-solute fractions and an independent second-rig TDS trajectory, retaining temporal resolution consistently reduced inventory–rate compensation relative to an integrated aggregate. The strength of localization and the fitted parameter values remained dataset- and observable-dependent.

### Do not write

> “The independent data prove that fractions identify the kinetic rate.”

The public external dataset is one coffee, one grind, and an aggregate TDS observable.

---

## 2.7 Additional data acquisition priorities

| Priority | Dataset | Why it matters | Availability | Action |
|---|---|---|---|---|
| **A — immediate** | Waszkiewicz et al. 2026 | Second rig, 5 s TDS fractions, 3 shots, measured flow, public archive | Public | Implement now |
| **A — request** | Kuhn et al. 2017 | Caffeine + trigonelline, three PSDs, high time resolution, triplicates | Raw public file not found in scoped search | Request replicate-level data |
| **A — request** | Vaca Guerra et al. 2024 | Component-resolved packed-bed extraction, PSD/bed configurations, tracer/dispersion context | Paper says data available on request | Request raw observations and metadata |
| **B — fallback** | Maille 2024 thesis | Named-solute early-time trajectories and three sieve fractions | Thesis publicly available | Use only for kinetic-shape/observation-design sensitivity; not espresso percolation |
| **C — different observable** | Sánchez-López et al. 2014/2016 | Very high time-resolution volatile trajectories | Article-level access varies | Related-work context; not direct validation of dissolved-solute model |
| **D — last resort** | Digitized figures | May recover approximate trajectories | Depends on figure quality and rights | Use only as explicitly digitized sensitivity with digitization uncertainty |

### Kuhn et al. data-request email

**Subject:** Request for replicate-level time-resolved espresso extraction data from Kuhn et al. (JFE 2017)

> Dear Dr. Kuhn, Dr. Briesen, and co-authors,  
>
> We are conducting a reproducible identifiability study of mechanistic espresso-extraction models and would like to evaluate the model against an independent, fraction-resolved named-solute dataset. Your 2017 Journal of Food Engineering paper on time-resolved caffeine and trigonelline extraction across particle-size distributions is the closest prior dataset for this purpose.
>
> Would you be willing to share the replicate-level data in machine-readable form? The most useful fields would be:
>
> - fraction start/end time or cumulative beverage mass;
> - fraction mass or volume;
> - caffeine and trigonelline concentration, units, and assay method;
> - particle-size distribution or sieve condition;
> - tamping pressure;
> - dose, beverage endpoint, temperature, pressure, and measured flow or shot time;
> - replicate identifiers;
> - calibration, analytical precision, and LOD/LOQ information;
> - any reuse or citation conditions.
>
> We would preserve the source data unchanged, provide full provenance and citation, and can return a cleaned derived table and analysis scripts. The planned use is a frozen external prediction followed by a clearly separated diagnostic identifiability profile; target-data refits would not be described as validation.
>
> Kind regards,  
> [Name / affiliation / contact]

### Vaca Guerra et al. data-request email

**Subject:** Request for time-resolved espresso-component extraction data from Vaca Guerra et al. (JFE 2024)

> Dear Dr. Vaca Guerra, Dr. Heinrich, and co-authors,  
>
> We are preparing a reproducible study of practical identifiability and parameter transfer in mechanistic espresso-extraction models. Your 2024 Journal of Food Engineering article states that data are available on request and appears particularly relevant because it combines component extraction, packed-bed transport, axial dispersion, and varied bed configurations.
>
> Would you be willing to share the raw or replicate-level time-resolved component data and associated metadata? We are especially seeking:
>
> - fraction or sampling interval start/end times;
> - fraction mass/volume or cumulative beverage mass;
> - named-solute and TDS concentrations with units;
> - particle-size distributions and packed-bed configurations;
> - dose, basket geometry, pressure, temperature, flow/shot time;
> - tracer measurements and the mapping to fitted dispersion coefficients;
> - replicate identifiers and analytical uncertainty;
> - the calibration/validation split, if any;
> - reuse and citation conditions.
>
> We would use the data first for frozen external prediction and only secondarily for a clearly labelled diagnostic refit/profile. Source files would be preserved with full provenance, and we would be glad to share cleaned derived data and scripts.
>
> Kind regards,  
> [Name / affiliation / contact]

### Minimum external fraction schema

```text
dataset_id
condition_id
replicate_id
coffee_id
origin
roast
dose_g
machine
basket
pressure_bar
temperature_C
flow_ml_s_or_trace_id
grind_setting
psd_d10_um
psd_d50_um
psd_d90_um
sieve_band
tamp_N
fraction_index
t_start_s
t_end_s
cumulative_beverage_g
fraction_mass_g
analyte
concentration
unit
assay
lod
loq
uncertainty_type
uncertainty_value
source_doi
source_file
source_row
license
```

---

# 3. Project decisions

## 3.1 Journal target: Journal of Food Engineering

### Decision

Target **Journal of Food Engineering (JFE)**.

### Rationale

JFE is the best fit for the manuscript's actual contribution:

- a food-engineering mechanism and observation problem;
- a mechanistic mathematical model;
- experimental-data integration;
- validation and transfer;
- quantitative implications for how extraction experiments should be designed.

JFE explicitly expects physically/chemically grounded models, replicable experimental design, established statistics, validation, broader applicability, substantiated claims, and sufficient detail for repetition.  
Guide: [Journal of Food Engineering — Guide for Authors](https://www.sciencedirect.com/journal/journal-of-food-engineering/publish/guide-for-authors)

### Why not Chemometrics and Intelligent Laboratory Systems as the first target

*C&ILS* prioritizes new statistical, mathematical, or chemometric methods, novel chemometric applications, genuinely new software tools, and benchmark datasets; routine applications of established techniques are not considered.  
Guide: [Chemometrics and Intelligent Laboratory Systems — Guide for Authors](https://www.sciencedirect.com/journal/chemometrics-and-intelligent-laboratory-systems/publish/guide-for-authors)

Paper A uses established profiling and identifiability concepts. It would become a stronger C&ILS candidate only if it introduced a demonstrably new general profiling/experimental-design method, released a broadly useful benchmark, or developed a validated software method beyond the espresso case.

### Why not Transport in Porous Media as the first target

*Transport in Porous Media* emphasizes fundamental, broadly relevant insight into physical, chemical, or biological transport in rigid or deformable porous media, through theory, numerics, laboratory work, or non-routine applications.  
Scope: [Transport in Porous Media — Aims and Scope](https://link.springer.com/journal/11242/aims-and-scope)

Paper A's present center of gravity is parameter identifiability and validation in a food-engineering application, not a new general porous-media transport result. TiPM would become more appropriate if the paper added a formal PDE-identifiability result or a broadly transferable porous-media observation-design theory.

### JFE terminology and structure

Use:

- calibration;
- reconstruction;
- internal holdout;
- internal prediction;
- external prediction;
- cross-dataset prediction;
- failed external prediction;
- target-data refit;
- in-sample verification;
- objective localization.

Do not use the repo-specific phrase **negative validation** in the submitted paper.

### JFE practical preparation points

At the time checked, JFE requires or expects:

- a concise abstract no longer than 250 words;
- 1–7 keywords;
- 3–5 highlights, each no more than 85 characters including spaces;
- quantitative, substantiated claims;
- clear mechanism and replicable methods;
- validated mathematical models;
- a data-availability statement;
- contributor roles and standard research-integrity declarations;
- separate, legible figures and SI units.

Create:

```text
docs/journal/JFE_SUBMISSION_CHECKLIST.md
```

and encode every requirement as a checked release gate rather than relying on memory.

---

## 3.2 M5 decision: remove TDS from the primary headline average

### Decision

The primary headline average should include only:

- caffeine;
- trigonelline;
- 5-CQA.

TDS or total-solids observations should be reported as a separate **aggregate-solids proxy**.

### Reason

The source observables do not have the same analyte semantics:

- the Pannusch-side TDS treatment functions as a modelled aggregate or caffeine-like pseudo-component;
- Angeloni's total solids are a gravimetric total-solids measurement;
- Waszkiewicz TDS is an optical-refractometer observable;
- named-solute concentrations are chemically specific assays.

These are not automatically equivalent analytes, and they need not share the same observation operator, uncertainty, extraction kinetics, or calibration.

Pooling them in one headline average gives an aggregate proxy the same status as chemically named species and can let it dominate the result without scientific equivalence.

### Required reporting

1. Report each named solute separately.
2. Report a macro-average over the three named solutes only, with an explicit formula.
3. Report TDS/TS in its own row or panel.
4. Provide sensitivity summaries:
   - named solutes only;
   - named solutes plus aggregate proxy;
   - aggregate proxy alone.
5. Never write “four solutes” when one is a pseudo-solute or source-specific solids observable.
6. Document the measurement and model semantics for every observable.

### Insertion-ready Methods sentence

> Primary cross-dataset performance is reported for the three named solutes caffeine, trigonelline, and 5-CQA. Source-specific TDS or total-solids measurements are treated as a separate aggregate-solids proxy and are reported in sensitivity analyses because the datasets do not share an equivalent analyte definition or measurement operator.

### Insertion-ready Results sentence

> The headline macro-average excludes the aggregate-solids proxy. Including that proxy is shown separately and does not alter the interpretation unless explicitly stated.

### Figure convention

Use one panel or row for each named solute and a visually separated panel labelled:

> **Aggregate-solids proxy: source-specific TDS/TS observable**

Do not visually group it as a fourth named molecule.

---

## 3.3 M10 decision: release strategy and tag timing

### Decision

Do **not** tag `paper-a-v1` now.

Create a paper release candidate only after the submission-blocking analyses and manuscript wording are frozen. Create the final release at submission.

### Observed repository state on 12 July 2026

- `main` was active and moving.
- Latest observed `main` commit:  
  `db34dc187b38108aed56aa6fe73b97e2007afc10`  
  “A4/G6: implement SoluteInventory contract + bruno provider (inventory<->kinetics carrier)”
- One existing package tag was visible: `v0.1.0`.
- No paper-specific GitHub Release was visible.
- A root-level `CITATION.cff` and manuscript-specific reproducibility manifest were not visible in the reviewed snapshot.

Because this can change, Claude Code should recheck immediately before release.

### Recommended versioning

Keep package and paper namespaces distinct:

```text
v0.1.0                 # package/software version
paper-a-v1.0.0-rc.1    # manuscript reproducibility candidate
paper-a-v1.0.0         # submitted manuscript snapshot
paper-a-v1.0.1         # correction or post-submission patch
```

Do not move or overwrite an existing tag.

### Release sequence

1. Work on a dedicated `paper-a` branch or pull request.
2. Complete the numerical blockers:
   - matched beverage endpoint;
   - actual full-cup observable;
   - exact/validated profiling;
   - uncertainty and range convergence;
   - boundary-optimum resolution;
   - TDS separation;
   - external TDS dataset adapter and analysis.
3. Freeze source data and derived outputs.
4. Add a one-command build and environment lock.
5. Create `paper-a-v1.0.0-rc.1`.
6. Build from a clean clone twice and compare output hashes.
7. Correct any provenance or build failures.
8. At submission, create annotated tag `paper-a-v1.0.0`.
9. Create a GitHub Release from that tag.
10. Archive the release with Zenodo and record the version DOI.
11. Cite the version DOI, tag, and full commit SHA in the manuscript.
12. Never cite moving `main` as the reproducibility snapshot.

GitHub documents that a Zenodo integration can archive each GitHub release and issue a DOI.  
References:

- [GitHub: Referencing and citing content](https://docs.github.com/repositories/archiving-a-github-repository/referencing-and-citing-content)
- [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub: Managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [GitHub: About CITATION files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Zenodo GitHub integration](https://help.zenodo.org/docs/github/)
- [Citation File Format](https://citation-file-format.github.io/)

### Required release files

```text
CITATION.cff
REPRODUCIBILITY.md
paper_a/
├── README.md
├── config/
│   └── submission.yaml
├── manifest.json
├── run_metadata.json
├── checksums.sha256
├── results/
├── figures/
├── tables/
└── logs/
```

Also retain a lock file or fully pinned environment, for example:

```text
uv.lock
```

or an equivalent reproducible environment specification.

### One-command build

The exact command can follow repo conventions, but the release should expose one strict entry point, for example:

```bash
python -m puckworks.paper_a.build --config paper_a/config/submission.yaml --strict
```

The command should:

- validate source hashes;
- run the paper analyses;
- save machine-readable values;
- render all figures and tables;
- update or verify manuscript-linked numbers;
- record solver tolerances and parameter bounds;
- fail on boundary flags that have not been explicitly accepted;
- fail on missing provenance;
- emit a release manifest and checksums.

### Example release commands

```bash
git checkout -b paper-a

git tag -a paper-a-v1.0.0-rc.1 \
  -m "Paper A reproducibility candidate 1"

git push origin paper-a-v1.0.0-rc.1

gh release create paper-a-v1.0.0-rc.1 \
  --prerelease \
  --generate-notes
```

For submission:

```bash
git tag -a paper-a-v1.0.0 \
  -m "Paper A submitted reproducibility snapshot"

git push origin paper-a-v1.0.0

gh release create paper-a-v1.0.0 \
  --title "Paper A v1.0.0 — submitted reproducibility snapshot" \
  --generate-notes
```

### Release gate

Do not create the final tag until all are true:

- [ ] manuscript records the exact tag, full SHA, and archive DOI;
- [ ] clean-clone build succeeds twice;
- [ ] repeated builds have identical machine-readable results or documented deterministic tolerances;
- [ ] source and output hashes are saved;
- [ ] package versions and operating environment are recorded;
- [ ] solver/grid convergence is documented;
- [ ] profile-domain convergence is documented;
- [ ] bootstrap seeds/resamples are saved;
- [ ] all boundary contacts are reported;
- [ ] every table and figure is generated from machine-readable outputs;
- [ ] no manuscript number is manually copied without a source key;
- [ ] source licenses and provenance are documented;
- [ ] the matched beverage endpoint is used;
- [ ] the actual full-cup observable is used;
- [ ] TDS/TS is separated from the named-solute headline;
- [ ] the Waszkiewicz analysis is frozen and labelled correctly;
- [ ] all tests pass;
- [ ] no stale narrative verdict remains embedded in analysis code.

---

# 4. Required manuscript vocabulary changes

| Current or risky phrase | Replace with |
|---|---|
| negative validation | failed external prediction; external stress test; falsifying external test |
| validation after refitting target data | target-data refit; reconstruction; diagnostic refit |
| fraction data identify the rate | fraction data provide stronger practical localization of the rate |
| structurally non-identifiable | weakly practically identifiable under the tested design and domain |
| profile likelihood, when using MAPE | profiled MAPE objective |
| exact profile, when using a finite grid | numerical profile over the stated grid/domain |
| whole cup, for selected non-contiguous windows | sampled-fraction aggregate |
| TDS as a fourth named solute | aggregate-solids proxy |
| no shared calibration exists | no satisfactory shared calibration was found over the tested parameter domain and assumptions |
| not a flow error | not removed by the two tested flow mappings |
| proves cup integration destroys kinetics | shows weak localization for this observation map and dataset |

---

# 5. Claude Code implementation plan

## P0 — submission-blocking

### Literature and prose

- [ ] Add `docs/literature_search/SEARCH_PROTOCOL.md`.
- [ ] Add `SEARCH_LOG.csv`, `SCREENING.csv`, and `EVIDENCE_MATRIX.csv`.
- [ ] Add the verified references to `references.bib`.
- [ ] Replace the related-work placeholder.
- [ ] Insert the novelty statement with its qualification.
- [ ] Remove universal/structural claims not supported by proof.
- [ ] Rename MAPE profiles.
- [ ] Rename the existing Pannusch exercise as in-sample verification/objective localization.
- [ ] Replace “negative validation” throughout manuscript, code output, figures, and docs.

### TDS and result aggregation

- [ ] Define `named_solutes = [caffeine, trigonelline, 5-CQA]`.
- [ ] Move TDS/TS to a separate proxy group.
- [ ] Generate named-only, named-plus-proxy, and proxy-only metrics.
- [ ] Ensure figure labels and prose use the same semantic grouping.

### External dataset

- [ ] Add the Waszkiewicz source card, manifest, source hashes, and immutable data copy.
- [ ] Resolve or explicitly profile the time-origin ambiguity.
- [ ] Implement interval mass/flow-weighted fraction prediction.
- [ ] Use the measured 9-bar flow trace.
- [ ] Add frozen external prediction.
- [ ] Add optional inventory-only adaptation as a separate result.
- [ ] Add target-data profile/refit only as a diagnostic.
- [ ] Generate fraction-versus-integral profiles from the same trajectory.
- [ ] Add all adapter and leakage-prevention tests.

### Existing numerical blockers from the detailed review

- [ ] Replace fixed 25 s cross-grind simulations with matched beverage mass/volume.
- [ ] Replace the non-contiguous sampled-window aggregate with an actual full-cup observable.
- [ ] Replace coarse level grids with an exact MAPE level profile or validated continuous optimization.
- [ ] Add uncertainty, bootstrap, and parameter-domain convergence.
- [ ] Resolve rate estimates that hit a search boundary.
- [ ] Narrow the causal interpretation of cross-grind residuals.

## P1 — reproducibility and journal packaging

- [ ] Add `CITATION.cff`.
- [ ] Add `REPRODUCIBILITY.md`.
- [ ] Add a strict one-command paper build.
- [ ] Add environment lock.
- [ ] Add `paper_a/manifest.json`, run metadata, and checksums.
- [ ] Add `docs/journal/JFE_SUBMISSION_CHECKLIST.md`.
- [ ] Create manuscript highlights only after final results are frozen.
- [ ] Add data availability and code availability statements.
- [ ] Add CRediT contributor roles.

## P2 — stronger external evidence

- [ ] Send the Kuhn et al. and Vaca Guerra et al. requests.
- [ ] On receipt, preserve raw files and licenses.
- [ ] Run frozen named-solute external prediction.
- [ ] Run prespecified inventory adaptation separately.
- [ ] Run practical-identifiability profiles and bootstrap recovery.
- [ ] Hold out at least one PSD or condition from any target-data calibration.
- [ ] Revise the novelty and Abstract only after these results and the corrected main analyses are known.

---

# 6. Suggested repository layout

```text
docs/
├── literature_search/
│   ├── SEARCH_PROTOCOL.md
│   ├── SEARCH_LOG.csv
│   ├── SCREENING.csv
│   ├── EVIDENCE_MATRIX.csv
│   ├── references.bib
│   └── README.md
├── data_requests/
│   ├── kuhn2017_request.md
│   ├── vaca_guerra2024_request.md
│   └── external_fraction_schema.md
├── journal/
│   └── JFE_SUBMISSION_CHECKLIST.md
└── reproducibility/
    └── PAPER_A_RELEASE_CHECKLIST.md

puckworks/
├── data/
│   └── waszkiewicz2026/
│       ├── SOURCE.md
│       ├── manifest.json
│       ├── tds_raw.csv
│       ├── tds_formatted.csv
│       ├── flow_9bar.csv
│       └── adapter.py
└── paper_a/
    ├── build.py
    ├── config/
    │   └── submission.yaml
    ├── external_waszkiewicz.py
    ├── metrics.py
    ├── profiles.py
    └── outputs/

CITATION.cff
REPRODUCIBILITY.md
uv.lock
```

---

# 7. Acceptance criteria for the revised §6

The section is acceptable only when all are true:

- [ ] Pannusch is explicitly described as the model's calibration lineage.
- [ ] The Pannusch fraction analysis is called in-sample verification or objective localization.
- [ ] The endpoint comparator is an actual full-shot observable or a complete, validated reconstruction.
- [ ] The external Waszkiewicz data are sourced from a pinned archived release.
- [ ] The source time origin and interval definitions are documented.
- [ ] External fractions are predicted with an interval-weighted observation operator.
- [ ] The frozen external prediction is shown before any target-data adaptation.
- [ ] Inventory-only adaptation, if used, is separated and prespecified.
- [ ] Full target-data refits are labelled diagnostic.
- [ ] TDS is labelled an aggregate-solids proxy.
- [ ] The earliest missing-replicate bin is handled without imputation.
- [ ] The result is reported with uncertainty and boundary flags.
- [ ] The conclusion is bounded to the tested dataset, model, domain, and objective.
- [ ] No independent named-solute or multi-grind claim is made without additional data.

---

# 8. Recommended final contribution statement

The following is a safe high-level contribution statement for the revised paper, subject to the corrected reruns:

> This study applies established practical-identifiability tools to a component-resolved espresso-extraction model and separates four questions that are often conflated: calibration, in-sample objective localization, internal prediction, and frozen external prediction. For the tested model and data, cup-integrated observations permit substantial compensation between soluble inventory and kinetic rate, while time-resolved fractions provide stronger rate localization. The work does not propose a new general identifiability method; its contributions are an espresso-specific case study, a model–data-specific observation about inventory–rate confounding, and a reproducible workflow for matching observation operators and evidence strength across coffee datasets.

---

# 9. Remaining limitations to state explicitly

Even after this handoff is implemented:

1. The Waszkiewicz external dataset contains TDS, not the three named solutes.
2. It represents one coffee and one grind setting.
3. Optical TDS is a source-specific aggregate observable and is not equivalent to Angeloni gravimetric total solids.
4. The time-origin and 12-versus-14-fraction discrepancy require resolution or sensitivity analysis.
5. A formal database search is still needed before categorical novelty claims.
6. Structural identifiability remains unproved unless a separate analytic analysis is supplied.
7. The paper's central numerical conclusions remain provisional until the endpoint, whole-cup, profiling, uncertainty, and boundary blockers are corrected.
8. Model discrepancy, flow assumptions, geometry, and inventory uncertainty can all contribute to cross-grind residuals; practical non-identifiability is not the sole possible cause.
9. Successful target-data refitting does not establish transfer.
10. A single independent TDS trajectory strengthens §6 but does not replace a named-solute, multi-PSD external dataset.

---

# 10. Final recommendation to Claude Code

Implement the work in this order:

1. **Correct the observation operators and endpoints.**
2. **Make the identifiability terminology mathematically standard.**
3. **Separate named solutes from aggregate solids.**
4. **Add the public Waszkiewicz external TDS trajectory as an independent test.**
5. **Complete and archive the documented literature search.**
6. **Only then revise the Abstract, title, novelty claims, and numerical headline.**
7. **Create the release candidate after all outputs are frozen; create the final tag at submission.**

The manuscript should be framed as a rigorous food-engineering case study showing why endpoint fit, parameter localization, and external prediction are different evidentiary claims. That is a strong and publishable story. It becomes weaker, not stronger, when expressed as a universal theorem or as a new general identifiability method.
