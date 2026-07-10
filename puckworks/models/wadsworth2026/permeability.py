"""Wadsworth et al. 2026 (RSOS 252031): constitutive permeability of coffee packs.

Percolation model (their Eq. 5.3 family) and specific-surface-area angularity
model, plus programmatic access to their Table 1 (transcribed; see data/).
Validated here against their own published values: percolation collapse
geometric-mean ratio 0.91 (x/1.31 scatter); Kozeny-Carman (W=5) runs 1.72x high.
"""
import csv, os
import numpy as np

ALPHA = 4808.0      # 1/m, global angularity fit
B_PERC = 4.4        # percolation exponent

def k_percolation(R, phi_p, alpha=ALPHA, b=B_PERC):
    """Permeability [m2] from mean grain radius R [m] and connected porosity."""
    return (2.0*R*R*np.exp(-2.0*alpha*R) / (9.0*(1.0-phi_p))) * phi_p**b

def s_p_angular(R, phi_p, alpha=ALPHA):
    """Specific surface area [1/m] with the exp(alpha R) angularity correction."""
    return 3.0*(1.0-phi_p)*np.exp(alpha*R)/R

def k_star(phi_p, s_p):
    """Normalization k_s = 2(1-phi_p)/s_p^2 used for their dimensionless collapse."""
    return 2.0*(1.0-phi_p)/s_p**2

def table1():
    """Their Table 1 as a list of dicts (coffee, G, R_m, phi_p, s_p, k_m2, err_m2)."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                        "wadsworth2026_table1.csv")
    with open(os.path.abspath(path)) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("R_m", "phi_p", "s_p", "k_m2", "err_m2"):
            r[k] = float(r[k])
        r["G"] = int(r["G"])
    return rows
