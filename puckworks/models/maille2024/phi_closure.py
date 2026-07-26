"""maille2024.phi_closure — the PSD -> fast-extracting-fraction map (card Eqs 6.7-6.9).

    (6.7)  phi          = theta_v,fines + theta_v,coarse
    (6.8)  theta_v,fines  = sum_{i: x_i < 186 um} v_i,liquid
    (6.9)  theta_v,coarse = sum_{i: x_i >= 186 um} v_i,air * (1 - (x_i - depth)^3 / x_i^3)

phi is NOT fitted: it is predicted a priori from the measured particle size distribution, leaving
only lambda_fast/lambda_slow to regress. That is the one genuinely predictive thing in the source
and the reason this component is registered at all.

E1 (RESOLVED, registry convention). Eq 6.9 as PRINTED subtracts 2*d_c from a DIAMETER, i.e. it
removes ONE cell layer. The surrounding text states the intent as "the first TWO layers in each
sphere". The published Table 6.3 follows the intent, not the print: two layers reproduce it to mean
|err| ~0.02 against ~0.2 for one layer. The registry adopts TWO layers (`SHELL_LAYERS = 2`), which
roughly DOUBLES phi versus the printed form; the printed form is recorded as a typo, and
`gate_maille_e1_shell_depth` keeps that adjudication reproducible.

INSTRUMENT-SPECIFIC BY CONSTRUCTION (card "Assumptions"): Eqs 6.8-6.9 assume the Malvern 100-bin
scale with bin 75 ~ 186 um, a liquid-below/air-above splice, and d_c = 45 um. phi computed from any
other PSD representation is a DIFFERENT quantity -- which is why `grind_state_from_psd` stamps the
convention onto the GrindState (contracts A11) instead of emitting a bare scalar.
"""
from puckworks.contracts import GrindState

D_C_M = 45e-6          # coffee cell diameter (card Parameters; SEM range 20-60 um, assumed)
FINES_CUT_UM = 186.0   # fines/coarse threshold = Malvern bin 75 (derived: Bi_m ~ 3, Fo_diff ~ 1.4)
SHELL_LAYERS = 2       # E1-RESOLVED: two cell layers (the printed one-layer form is a typo)

# The A11 convention this closure emits. maille's PSD is the Eq 5.1-5.3 HYBRID splice (liquid
# dispersion below the cut, air above) on a VOLUME basis.
DISPERSION_METHOD = "hybrid"
FINES_BASIS = "volume"

# phi range the source itself observed (Table 6.3, 17 materials). Outside this, phi is an
# EXTRAPOLATION of the closure -- Cameron's espresso-fine PSDs land at ~0.85-0.94.
PHI_SOURCE_RANGE = (0.356, 0.648)


def shell_fraction(diameter_m, n_layers=SHELL_LAYERS):
    """Eq-6.9 kernel: the outer-shell volume fraction of a sphere once `n_layers` coffee-cell layers
    are removed. Depth off the DIAMETER is 2*n_layers*d_c (d_c per side, per layer). Fully consumed
    particles (inner radius <= 0) return 1.0 -- the whole particle is 'fast'."""
    depth = 2.0 * n_layers * D_C_M
    inner = diameter_m - depth
    if inner <= 0:
        return 1.0
    return 1.0 - inner ** 3 / diameter_m ** 3


def phi_from_binned_psd(diameter_um, volume, fines_cut_um=FINES_CUT_UM, n_layers=SHELL_LAYERS):
    """THE PSD ADAPTER (card "Dependencies: a PSD-binning adapter").

    Apply Eqs 6.7-6.9 to any binned PSD -- `diameter_um` bin representative diameters and `volume`
    the per-bin volume in ANY consistent unit (normalized internally). Returns
    dict(phi, theta_v_fines, theta_v_coarse, ...).

    The contract this adapter does NOT satisfy: maille's own theta_v,fines comes from a LIQUID
    dispersion measurement and theta_v,coarse from an AIR one (the Eq 5.1-5.3 splice). A caller
    passing a single-method PSD gets a phi computed on a different measurement basis -- recorded in
    the returned `dispersion_method` rather than silently absorbed. See maille Table 5.2: the same
    material measured both ways differs by up to ~2x in fines fraction."""
    diameter_um = [float(x) for x in diameter_um]
    volume = [float(v) for v in volume]
    if len(diameter_um) != len(volume):
        raise ValueError("phi_from_binned_psd: diameter_um and volume must be the same length")
    if not diameter_um:
        raise ValueError("phi_from_binned_psd: empty PSD")
    if any(x <= 0 for x in diameter_um):
        raise ValueError("phi_from_binned_psd: bin diameters must be positive [um]")
    if any(v < 0 for v in volume):
        raise ValueError("phi_from_binned_psd: bin volumes must be non-negative")
    total = sum(volume)
    if total <= 0:
        raise ValueError("phi_from_binned_psd: PSD volume sums to zero")
    depth_um = 2.0 * n_layers * D_C_M * 1e6
    fines = coarse = 0.0
    for dia, v in zip(diameter_um, volume):
        frac = v / total
        if dia < fines_cut_um:
            fines += frac
        else:
            inner = max(dia - depth_um, 0.0)
            coarse += frac * (1.0 - inner ** 3 / dia ** 3)
    phi = fines + coarse
    lo, hi = PHI_SOURCE_RANGE
    return dict(phi=phi, theta_v_fines=fines, theta_v_coarse=coarse,
                fines_cut_um=float(fines_cut_um), n_layers=int(n_layers),
                n_bins=len(diameter_um), dispersion_method=DISPERSION_METHOD,
                # honesty flag: the closure is being read outside the range the source measured
                extrapolated_beyond_source_phi_range=bool(phi < lo or phi > hi))


def phi_from_d43(d43_um, fines_fraction, n_layers=SHELL_LAYERS):
    """The SINGLE-DIAMETER approximation: evaluate the Eq-6.9 shell kernel once at the hybrid D[4,3]
    instead of bin-by-bin, and take theta_v,fines from the measured sub-186 um volume fraction.

    This is the ONLY route reproducible from the thesis itself -- the per-bin arrays v_i,liquid /
    v_i,air are NOT published, only the Table 5.2/5.4 summary statistics, so Eqs 6.8-6.9 cannot be
    run end-to-end from the source (card "Blocker to state up front"). It is also the approximation
    the E1 evidence rests on. Prefer `phi_from_binned_psd` whenever real bins exist."""
    d43_m = float(d43_um) * 1e-6
    fines = float(fines_fraction)
    coarse = (1.0 - fines) * shell_fraction(d43_m, n_layers)
    return dict(phi=fines + coarse, theta_v_fines=fines, theta_v_coarse=coarse,
                n_layers=int(n_layers), method="d43_single_diameter_approximation")


def grind_state_from_psd(setting, diameter_um, volume, **kw):
    """PSD -> `GrindState`, with maille's fines convention STAMPED ON (contracts A11).

    The card's Interface-mapping complaint made concrete: `GrindState.fines_fraction` is
    threshold-ambiguous (186 um here, 100 um in smrke2024/khamitova2020, radius moments in
    wadsworth2026.grindmap), so this adapter never emits a bare scalar. The declared threshold /
    dispersion method / basis travel with the value, and `contracts.assert_fines_fraction_comparable`
    refuses to merge it with a differently-declared one.

    NOTE `fines_fraction` here is theta_v,fines (the sub-186 um volume fraction) -- NOT phi. phi
    additionally counts coarse-particle outer SHELLS and is a fast-EXTRACTION fraction, not a size
    class; conflating the two is the ~5-9x observable-semantics error the Cameron gate surfaces."""
    r = phi_from_binned_psd(diameter_um, volume, **kw)
    return GrindState(setting=float(setting),
                      fines_fraction=r["theta_v_fines"],
                      fines_threshold_um=r["fines_cut_um"],
                      fines_dispersion_method=DISPERSION_METHOD,
                      fines_basis=FINES_BASIS), r


def table6_3():
    """The source's published phi closure (Table 6.3): 17 materials x theta_v_fines/theta_v_coarse/phi."""
    from puckworks import data as d
    return {r["Sample ID"]: r for r in d.maille_phi()}


def hybrid_psd():
    """The source's hybrid PSD summary (Table 5.4): D[4,3], D[3,2], volume fraction < 186 um."""
    from puckworks import data as d
    return {r["Sample ID"]: r for r in d.maille_psd_hybrid()}
