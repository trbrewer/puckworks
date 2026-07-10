# Model card: Wadsworth 2026 permeability

**Paper:** Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026). DOI 10.1098/rsos.252031
**Stages:** packing · **Kind:** calibration (informs BedState.k / kappa priors)
**Status:** gated (collapse reproduced from their Table 1: GM ratio 0.91, x/1.31)

## Scope
Constitutive k(<R>, phi_p): percolation form phi_p^4.4 with normalization
k_s = 2(1-phi_p)/s_p^2; specific surface area with angularity exp(alpha <R>),
alpha = 4808 /m. Validated by XCT + LBflow on 2 coffees x 11 grinds (untamped).

## Findings from our integration
(1) Reconciling with Cameron's flux table needs phi_c ~ 0.11 or screen resistance
(tamped regime is their acknowledged gap). (2) At fixed porosity their k(R) turns
over at R = 1/alpha ~ 208 um: grind->flow in tamped beds is carried by packing,
not grain size. (3) Sphere-side confirmation: our synthetic-pack offsets grow
exponentially in <R>, implied alpha ~ 3100 /m from the QUICK sweep (R^2 0.86).

## Extractable data
Table 1 -> data/wadsworth2026_table1.csv (done). Segmented XCT volumes: on request
(email sent); loader ready in the Colab notebook.
