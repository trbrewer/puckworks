# Model card: Cameron 2020 extraction model

**Paper:** Cameron et al., "Systematically improving espresso," Matter 2, 631-648 (2020). DOI 10.1016/j.matt.2019.12.019
**Stages:** grind (microstructure tables), packing (flux table), extraction · **Kind:** runtime
**Status:** gated (reimplementation validated; three reproducibility findings documented)

## Scope
Two-population (fines/boulders) 1D saturated extraction: liquid advection + intragrain
diffusion + nonlinear surface dissolution. Grind enters via measured microstructure
and Darcy-flux tables (EK43 dial 1.1-2.3).

## Key implementation notes
Per-BED-volume soluble inventory c_s0 = 118/phi_s (EY ceiling 29.6%); paper value
k = 6e-7 (released code differs: 1e-9); fines a1 = 12 um (SI surface-area table
self-inconsistent). paper_mode replication is import-order sensitive - kept in the
paper repo only, NOT in this package.

## Interface mapping
grind.setting -> GrindState; flux table + kappa -> BedState.k; extraction consumes
BedState + MachineState.P_of_t -> ShotResultState.

## Validation
Closed mass budget; browser/BDF parity <=0.03 pts matched grids; convergence study
bounds default-grid bias ~0.15 pts. See paper SI Tables S1–S5 (transcribed in
`extraction_bdf.py`) and Fig. 5 (EY-vs-grind curve). [corrected 2026-07-11: the
earlier "Tables 2, 7, 8" do not exist in the paper.]
