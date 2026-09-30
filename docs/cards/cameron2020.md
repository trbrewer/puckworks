# Model card: Cameron 2020 extraction model

**Paper:** Cameron et al., "Systematically improving espresso," Matter 2, 631-648 (2020). DOI 10.1016/j.matt.2019.12.019
**Stages:** grind (microstructure tables), packing (flux table), extraction · **Kind:** runtime
**Status:** gated (code verification; source reproduction remains unresolved)

## Scope
Two-population (fines/boulders) 1D saturated extraction: liquid advection + intragrain
diffusion + nonlinear surface dissolution. Grind enters via measured microstructure
and Darcy-flux tables (EK43 dial 1.1-2.3).

## Key implementation notes
The operative grain field starts at c_s0 = 118 kg/m³ of grain. Initial soluble
mass is V*phi_s*c_s0; with the retained printed Eq. 25 geometry, the ceiling is
`inventory_ceiling_percent()` = 24.467473% of dose. The streamtube caller explicitly
uses 118/phi_s and has a different inventory; it does not change Cameron defaults.
The paper value k = 6e-7 differs from released code (1e-9); fines a1 = 12 um
(SI surface-area table self-inconsistent). paper_mode replication is import-order sensitive - kept in the
paper repo only, NOT in this package.

Measured Table S2 phase fractions and boulder radius are interpolated first;
geometric areas are derived with b_i=3*phi_i/a_i afterward. This preserves one
particle population off the knots and repairs the former inventory gap. The source
labels 330 kg/m³ as bulk density, but Eq. 25 uses V=M_in*phi_s/rho; that conflicts
with the bulk-density identity V=M_in/rho. The released MATLAB EY normalization
also differs by phi_s^-2 relative to the printed geometry. Neither author intent
nor the Fig. 5 generating configuration is established. Physical EY remains
100*cup_solute_mass/actual_dose. See [local audit](../analysis/cameron_local_audit_20260930.md).

## Interface mapping
grind.setting -> GrindState; flux table + kappa -> BedState.k; extraction consumes
BedState + MachineState.P_of_t -> ShotResultState.

## Validation
Closed mass budget; browser/BDF parity <=0.03 pts matched grids; convergence study
bounds default-grid bias ~0.15 pts. See paper SI Tables S1–S5 (transcribed in
`extraction_bdf.py`) and Fig. 5 (EY-vs-grind curve). [corrected 2026-07-11: the
earlier "Tables 2, 7, 8" do not exist in the paper.]
