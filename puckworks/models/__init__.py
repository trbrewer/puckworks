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
    name="foster2025.infiltration", stage="infiltration", kind="runtime",
    paper="Foster et al., Phys. Fluids 37, 013383 (2025)", doi="10.1063/5.0245167",
    module="puckworks.models.foster2025.infiltration",
    gates=[G.gate_infiltration_triangle],
    assumptions="sharp uniform 1D front; binary saturation; pc ~ 0.1 bar "
                "(2% of flat shot, 50% of blooming pause)",
    valid_range="validated on 59 mm basket, 10 g dose, time-resolved CT",
    notes="closed form under recorded P(t); pump/headspace model = backlog"))
