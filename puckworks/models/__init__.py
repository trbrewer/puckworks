"""Register all founding components."""
from puckworks.registry import Component, register
from puckworks.validation import gates as G

register(Component(
    name="cameron2020.extraction_bdf", stage="extraction", kind="runtime",
    paper="Cameron et al., Matter 2, 631-648 (2020)", doi="10.1016/j.matt.2019.12.019",
    module="puckworks.models.cameron2020.extraction_bdf",
    assumptions="saturated bed from t=0; homogeneous 1D flow; single solute pool; "
                "per-bed-volume soluble inventory (EY ceiling 29.6%)",
    valid_range="EK43 dial 1.1-2.3; 20 g in / 40 g out class recipes",
    notes="mass-conservative FV + scipy BDF; ~0.15-pt default-grid bias (see paper Table 7)"))

register(Component(
    name="brewer2026.streamtube", stage="bed_dynamics", kind="runtime",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.streamtube",
    assumptions="parallel non-exchanging tubes; unit-mean lognormal k; "
                "sigma(phi1) is an EMPIRICAL closure over the calibrated domain",
    valid_range="calibrated at dial 1.1-1.5; LOO-interpolated, not externally validated",
    notes="Rung B fines migration is hypothesis-generating"))

register(Component(
    name="brewer2026.pack_generator", stage="packing", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.pack_generator",
    assumptions="overlapping (Boolean) spheres - Wadsworth model class; fines sub-voxel, "
                "represented via columnar heterogeneity field (w_floor >= 0.25)",
    valid_range="grain radius >= 10 voxels; columns >= 5 grain diameters for sigma"))

register(Component(
    name="brewer2026.lb_reference", stage="flow", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.lb_reference",
    gates=[G.gate_lb_channel],
    assumptions="D3Q19 TRT (magic 3/16), full-way bounce-back, Stokes regime",
    valid_range="verification twin; production runs use lb_taichi",
    notes="channel exact to 0.03-0.05%; sphere drag -7% at r=8.5 lu (staircase)"))

register(Component(
    name="brewer2026.lb_taichi", stage="flow", kind="calibration",
    paper="Brewer 2026 (this project)", module="puckworks.models.brewer2026.lb_taichi",
    assumptions="same physics as lb_reference (cross-checked to 0.003%); "
                "f32 needs g >= ~1e-5 signal; heterogeneous packs need g ~ 3e-6 (Mach)",
    valid_range="CPU/GPU; optional dependency taichi",
    notes="Colab production solver"))

register(Component(
    name="wadsworth2026.permeability", stage="packing", kind="calibration",
    paper="Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026)", doi="10.1098/rsos.252031",
    module="puckworks.models.wadsworth2026.permeability",
    gates=[G.gate_wadsworth_collapse],
    assumptions="percolation k(phi_p) with phi_c=0; angularity via exp(alpha R); "
                "validated at phi_p 0.37-0.67 UNTAMPED - tamped regime is extrapolation",
    valid_range="<R> 145-818 um, two arabica roasts",
    notes="reconciling with Cameron flux implies phi_c~0.11 or series screen resistance"))

register(Component(
    name="wadsworth2026.grindmap", stage="grind", kind="calibration",
    paper="Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026)", doi="10.1098/rsos.252031",
    module="puckworks.models.wadsworth2026.grindmap",
    gates=[G.gate_grindmap_refit, G.gate_grindmap_polydispersity],
    assumptions="linear dial->radius map <R>=beta*G+R0; S=<R><R2>/<R3>; "
                "OPERATIVE beta/R0 are a Table-1 refit (5.805e-5/1.380e-4) - the "
                "card's printed 4.3505e-5/1.016e-4 do NOT reproduce (flagged)",
    valid_range="Mahlkonig this burr/calibration ONLY; G 1-11, <R> 145-818 um; "
                "grinder-specific, non-portable to EK43/E65S dials (A9/rule 9)",
    notes="one paper with wadsworth2026.permeability; S(G) rises 0.46->0.78; "
          "S formula reconstructs reported S to <3e-3; A9 dial-space adapter stub"))

register(Component(
    name="waszkiewicz2025.poroelastic", stage="bed_dynamics", kind="runtime",
    paper="Waszkiewicz et al., arXiv:2512.21528 (2025)", doi="10.5281/zenodo.18046315",
    module="puckworks.models.waszkiewicz2025.poroelastic",
    gates=[G.gate_waszkiewicz_static_refit, G.gate_waszkiewicz_dynamic_9bar],
    assumptions="quasi-static 1D saturated poroelastic bed; Carman-Kozeny k(phi) + "
                "Hookean strain; Phi(t)=m_d(t)/m0 (all porosity change = dissolution); "
                "empirical m_d(t) sigmoid (RC-3a scope; NOT the RC-3b Cameron coupling)",
    valid_range="Sanremo Zoe rig, one coffee/grind; quantitative only above ~5 bar; "
                "silent on first ~5-10 s; constants per-rig/coffee/grind, not portable",
    notes="static refit == published (P_c,Q_c)=(12.39,1.897); 9-bar Q(t) parameter-free "
          "long-run within ~2% (post-fit: m_d from same rig, soft circularity per card)"))

register(Component(
    name="foster2025.infiltration", stage="infiltration", kind="runtime",
    paper="Foster et al., Phys. Fluids 37, 013383 (2025)", doi="10.1063/5.0245167",
    module="puckworks.models.foster2025.infiltration",
    gates=[G.gate_infiltration_triangle],
    assumptions="sharp uniform 1D front; binary saturation; pc ~ 0.1 bar "
                "(2% of flat shot, 50% of blooming pause)",
    valid_range="validated on 59 mm basket, 10 g dose, time-resolved CT",
    notes="closed form under recorded P(t); pump/headspace model = backlog"))
