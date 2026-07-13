# Paper A figures (review §7)

Eight figures (six main + two condition-structure diagnostics, Fig 7–8) for
`docs/PAPER_A_DRAFT.md`, rendered from the **corrected matched-mass**
analysis. Because Paper A's analysis is slow (PDE solves), the figures render from a
cached `results.json` that one command regenerates:

```bash
python -m puckworks.figures_paper_a compute   # ~20-30 min slow; -> results.json
python -m puckworks.figures_paper_a render    # fast; -> this directory
# or: python -m puckworks.figures_paper_a all
```

`compute` runs every slow analysis function **once** (no hand-typed numbers) and
records the source commit in `results.json`; `render` draws the figures from it.
matplotlib is the optional `[figures]` extra (the module imports without it).

| file | shows |
|---|---|
| `fig1_design.png` | study & evidence design: calibration → O fit → held-out CV → frozen C/F transfer → Table 7 tie-breaker → in-sample verification, arrows colour-coded by evidence type |
| `fig2_objective_surface.png` | inventory–rate SSE surface (caffeine, trigonelline): the flat valley, the profiled path, the Table 7 inventory line, the condition number |
| `fig3_holdouts.png` | every leave-one-condition-out held-out point (observed vs predicted) by solute × variety — the distribution the pooled mean hides |
| `fig4_transfer.png` | frozen O→C/F transfer at matched 40 g cups: observed vs predicted per condition, grinds C and F |
| `fig5_joint_residual.png` | joint shared-(c_s0, rate) fit residual by variety × solute × grind; cost-of-sharing; rate-boundary flags |
| `fig6_fraction_vs_endpoint.png` | rate profiles: fraction scoring (sharp) vs sampled aggregate and the exact-integral whole cup (flat) |

The figures track the corrected findings — single-grind non-identifiability is strong
(Fig 2), yet predictive transfer **works** at matched mass (Figs 3–5), and the cup
loses the rate for a true whole cup, not just a sampled aggregate (Fig 6):
identifiability ≠ transfer.

`results.json` is the cached analysis output (regenerable, provenance-stamped); do
not hand-edit.
