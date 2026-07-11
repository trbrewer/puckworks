"""Pannusch solver slow ladder — NOT run in CI (see this dir's README).

The quick gate (gate_pannusch_solver_mape) runs the full 15-experiment MAPE at
nz=200 in ~13 s. This ladder adds the per-experiment breakdown and a grid
resolution check.

Run:  python -m puckworks.validation.slow.pannusch_mape
"""
import numpy as np

from puckworks.models.pannusch2024 import solver as ps

PUB = {"caffeine": 4.59, "trigonelline": 7.85, "5CQA": 4.98, "tds": 6.07}


def per_experiment_breakdown():
    exps = ps._exp_kinetics(); params = ps._solute_params()
    print(f"{'exp':>4} " + " ".join(f"{s[:4]:>7}" for s in PUB))
    for eid, rows in sorted(exps.items()):
        line = f"{eid:>4} "
        for s in PUB:
            m = ps.mape_for_experiment(rows, s, params[s])
            line += f"{('' if m is None else f'{m:6.2f}'):>7} "
        print(line)
    res = ps.mape_all()
    print("mean " + " ".join(f"{res[s]:6.2f} " for s in PUB))
    print("pub  " + " ".join(f"{PUB[s]:6.2f} " for s in PUB))


def resolution_check(grids=(120, 200, 300)):
    """Centre-grind MAPE (caffeine) vs axial grid resolution."""
    exps = ps._exp_kinetics(); params = ps._solute_params()
    orig = ps.NZ
    try:
        for nz in grids:
            ps.NZ = nz; ps._jac_sparsity.cache_clear()
            vals = [ps.mape_for_experiment(r, "caffeine", params["caffeine"])
                    for r in exps.values()]
            print(f"nz={nz:4d}: caffeine MAPE = {np.mean([v for v in vals if v]):.3f}%")
    finally:
        ps.NZ = orig; ps._jac_sparsity.cache_clear()


if __name__ == "__main__":
    print("== per-experiment MAPE (%) ==")
    per_experiment_breakdown()
    print("\n== axial resolution check ==")
    resolution_check()
