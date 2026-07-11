# moroney2016 — data provenance

Source card: `docs/cards/moroney2016.md` (ROADMAP items 0.10 / 1.4).

**Origin:** Moroney, Lee, O'Brien, Suijver, Marra, *"Asymptotic analysis of the
dominant mechanisms in the coffee extraction process,"* **SIAM J. Appl. Math.
76(6), 2196–2217 (2016)**, DOI `10.1137/15M1036658`. No code/data published with
the paper; the experimental exit-concentration data originates in Moroney 2015
(Chem. Eng. Sci. 137).

## Files
| file | source | extraction | content |
|---|---|---|---|
| `moroney2016_table1.csv` | card Parameters table | **transcription** | full Table 1 parameter set + dimensionless groups (eps, a1, a2, a3) + timescales (t_a, t_s, t_d). Fine grind. |
| `moroney_fig6_exit_concentration.csv` | Fig 6(a) | **digitization** (Tim, 2026-07-11) | experimental nondimensional exit concentration c_h vs t (JK drip-filter grind). |

## Validation strength / caveats
- Table 1 = transcription (exact); Fig 6 = digitization (plot-reading noise).
- Fig 6 reproduction is **qualitative** (the source states: graphical, no error
  metrics). The leading-order composite (Eq 3.45) reproduces the saturated
  plateau (t<1) and the wash-through midpoint (c=1/2 at t≈3.1, data ≈3.1) but is
  too steep in the long-time tail — the outer bulk-diffusion solution (Eqs
  3.61–3.62) and the O(eps) correction (3.56) are **not on the card** and are not
  modeled. Full-tail reproduction needs the Moroney-2015 paper.
