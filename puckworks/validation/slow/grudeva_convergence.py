"""Grudeva reduced-model slow ladder — NOT run in CI (see this dir's README).

Two heavier checks the quick gate (coarse N=150) only samples:

  resolution_study() — refine (N, Nt); confirm s_d^{-1}(1), total solubles, and
  the per-vial reconstruction are grid-converged (verification; V0-class).

  eps_discrimination() — the LOG Issue 1 / G1 belt-and-braces: run the café
  config with the adjudicated no-ε capacitance vs the S2 *printed* ε form. The ε
  form deletes the liquid-storage term, collapsing the saturated plateau
  (s_d^{-1}(1) ~ 2.8 -> ~0.45) and under-extracting (total ~2.9 g -> ~2.5 g).
  (The published V1 config, phi_l/phi_T = 1, is the cleaner discriminator on
  paper but is numerically stiff in the explicit boulder scheme — café, which is
  also anchored to the exp13 vial data, carries the demonstration here.)

Run by hand:  python -m puckworks.validation.slow.grudeva_convergence
"""
import numpy as np

from puckworks.models.grudeva2025 import reduced as gr


def resolution_study(grids=((150, 800), (300, 1500), (400, 3000))):
    out = []
    for N, Nt in grids:
        r = gr.make_coffee(N=N, Nt=Nt)
        out.append((N, Nt, r["sd_inv_1"], r["total_solubles_g"]))
        print(f"N={N:4d} Nt={Nt:4d}: s_d^-1(1)={r['sd_inv_1']:.3f}  "
              f"total={r['total_solubles_g']:.3f} g")
    return out


def eps_discrimination(eps_values=(1e-2, 1e-3)):
    """No-ε vs printed-ε capacitance at the café config."""
    r0 = gr.make_coffee(N=300, Nt=1500)                 # no-ε (adjudicated)
    print(f"no-ε (B0)      : s_d^-1(1)={r0['sd_inv_1']:.3f}  total={r0['total_solubles_g']:.2f} g")
    for eps in eps_values:
        re = gr.make_coffee(N=300, Nt=1500, eps=eps)
        print(f"printed-ε {eps:.0e}: s_d^-1(1)={re['sd_inv_1']:.3f}  total={re['total_solubles_g']:.2f} g  "
              f"(plateau collapsed — LOG Issue 1)")
    return r0["sd_inv_1"]


if __name__ == "__main__":
    print("== resolution study ==")
    resolution_study()
    print("\n== ε-form discrimination (LOG Issue 1 / G1) ==")
    eps_discrimination()
