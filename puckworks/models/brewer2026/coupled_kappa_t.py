"""coupled_kappa_t.py — brewer2026 coupled kappa(t) porosity-evolution synthesis.

Card: docs/cards/brewer2026_coupled_kappa_t.md. A SYNTHESIS component (no external
paper): one shared porosity state eps(t) that every registered bed-evolution
mechanism reads and writes, replacing the earlier multiplicative harness closure
kappa = f1*f2*f3*f4 (which double-counts pore volume because the factors never
see each other). The four branches compose ADDITIVELY on the shared porosity:

    eps(t) = eps0 * (1 + Phi_ext(t) + Phi_swell(t) + Phi_comp(t) + Phi_fines(t))

    SIGN CONTRACT (Paper 3 review P0-7 -- adopt ONE convention and enforce it). Every branch
    Phi_i is a SIGNED RELATIVE POROSITY INCREMENT, d(eps)/eps0, and branches ADD. It is NOT a
    non-negative "closure magnitude" to be subtracted. So:
        Phi_extraction >= 0   dissolution OPENS pore space
        Phi_swelling   <= 0   swelling CLOSES it   (returns eps_b/eps0 - 1, which is negative)
        Phi_compaction <= 0   compaction CLOSES it (structural stub)
        Phi_fines      <= 0   deposition CLOSES it (structural stub)
    An earlier docstring wrote this subtractively (`- Phi_swell`), which implied a non-negative
    magnitude and contradicted the code, which adds a negative. The numbers were right either way;
    the CONTRACT was ambiguous, and a downstream consumer could not tell which was meant. Signed
    increments are used because they compose without per-branch sign bookkeeping.
    clamped to [eps_min, eps_max]  (a clamp hit is a DOCUMENTED regime edge)

Branches (each inherits its donor component's law; this card fixes only signs/
units/coupling):
  extraction  (+, opens): waszkiewicz2025 m_d(t)/dose  (== its Phi(t))
  swelling    (-, closes): mo2023_2.swelling eps_b(t)   (fixed-dP, UNVALIDATED)
  compaction  (-, closes): fasano2000_partII (8.69)     (params UNIDENTIFIED -> stub)
  fines       (-, closes): fasano2000_partI             (params UNIDENTIFIED -> stub)

Flow closure -- POROELASTIC (card Eq.2, corrected 2026-07-11 to match this code):
the flow is driven through waszkiewicz's poroelastic closure with the composite
porosity as an effective m_d, so extraction-only reduces to rung 4 exactly. This
closure is REQUIRED, not Kozeny-Carman: the 9-bar flow rises 14x (0.14->2.0 g/s)
on a small porosity change (Phi 0.03->0.12) because the bed is near-choke, where
kappa is hypersensitive to eps -- CK is far too gentle (RMSE ~1.5 vs 0.116).
kappa_CK(eps) is retained as an AUXILIARY/illustrative cross-reference only (gentle
non-choke regime), never the operative closure. (The card's first draft printed
CK as Eq.2; it was corrected card-side in the same lineage as this note.)

Framework-level validity only: as sound as its shakiest branch (three donors carry
unidentified/unvalidated params). Label 'coupled kappa(t) FRAMEWORK; branch
fidelity inherited', never 'validated kappa(t) law'.
"""
import numpy as np

from puckworks import data as _d
from puckworks.models.waszkiewicz2025 import poroelastic as _wz

EPS0_DEFAULT = 0.17
EPS_MIN, EPS_MAX = 0.02, 0.95        # regime clamp (card: assumed bounds)


def _ck(eps, eps0):
    """Kozeny-Carman permeability ratio kappa/kappa0 (card Eq.2, auxiliary)."""
    return (eps ** 3 / (1.0 - eps) ** 2) / (eps0 ** 3 / (1.0 - eps0) ** 2)


def _phi_extraction(t, dose):
    """Extraction porosity fraction = waszkiewicz m_d(t)/dose (its own Phi)."""
    k, l, m = _wz._solids_params()
    return _wz.solids_sigmoid(t, k, l, m) / dose


def _phi_swelling(t, powder="M", eps0=EPS0_DEFAULT):
    """Swelling porosity fraction (<=0) from mo2023_2 eps_b(t): eps_b/eps0 - 1.
    NOTE fixed-dP, unvalidated (donor card); over-closes on a saturated pre-wet
    rig -- the composition residual below diagnoses exactly that."""
    from puckworks.models.mo2023_2 import swelling as sw
    fd = sw.flow_decay(powder, np.clip(np.asarray(t, float), 1e-4, None), eps_b0=eps0)
    return fd["eps_b"] / eps0 - 1.0


def simulate(P_bar=9.0, t=None, branches=("extraction",), powder="M",
             eps0=EPS0_DEFAULT, eps_min=EPS_MIN, eps_max=EPS_MAX):
    """Coupled kappa(t): compose the selected branches on ONE shared porosity and
    drive the flow through waszkiewicz's poroelastic closure (see the module
    docstring re: Eq.2). Returns t, eps(t), kappa_ck(t) (Eq.2 auxiliary),
    Q(t) [g/s], the effective m_d, the per-branch Phi, and clamp flags.
    compaction/fines are structural stubs (donor params unidentified -> 0)."""
    tr = _d.waszkiewicz_traces()
    if t is None:
        t = tr[P_bar]["time__s"]
    t = np.asarray(t, float)
    dose = _d.waszkiewicz_constants()["dose__g"]
    phi = np.zeros_like(t)
    parts = {}
    if "extraction" in branches:
        parts["extraction"] = _phi_extraction(t, dose); phi = phi + parts["extraction"]
    if "swelling" in branches:
        parts["swelling"] = _phi_swelling(t, powder, eps0); phi = phi + parts["swelling"]
    # compaction/fines: donor params unidentified -> structural stubs (0), surfaced
    parts["compaction_stub"] = np.zeros_like(t)
    parts["fines_stub"] = np.zeros_like(t)
    eps_raw = eps0 * (1.0 + phi)
    eps = np.clip(eps_raw, eps_min, eps_max)
    clamped = bool(np.any(eps_raw < eps_min) or np.any(eps_raw > eps_max))
    # effective dissolved-mass-equivalent for the poroelastic closure: only the
    # OPENING (eps>eps0) drives the near-choke rise; net-closing -> the un-opened
    # low flow (floored at a tiny Phi so the closure stays defined).
    m_d_eff = np.clip((eps - eps0) / eps0 * dose, dose * 1e-4, None)
    P_c, Q_c = _wz.published_calibration()
    Q = _wz.q_dynamic_from_md(P_bar, P_c, Q_c, m_d_eff, dose)
    return dict(t=t, eps=eps, kappa_ck=_ck(eps, eps0), Q=Q, m_d_eff=m_d_eff,
                phi=parts, clamped=clamped, eps0=eps0)


def degeneracy_rmse(P_bar=9.0, window=(15.0, 95.0)):
    """Extraction-only reduction: RMSE [g/s] of the coupled model's Q(t) vs the
    Waszkiewicz P-bar trace over the saturated window. MUST match rung 4 (the
    poroelastic component alone, ~0.113) -- the card's exact-reduction degeneracy."""
    tr = _d.waszkiewicz_traces()
    t = tr[P_bar]["time__s"]; q = tr[P_bar]["mass_flow_rate__g_per_s"]
    r = simulate(P_bar=P_bar, t=t, branches=("extraction",))
    sel = (t >= window[0]) & (t <= window[1])
    return float(np.sqrt(np.nanmean((r["Q"][sel] - q[sel]) ** 2)))


def composition_residual(P_bar=9.0, powder="M", window=(15.0, 95.0)):
    """Add the swelling branch (imported with mo2023_2's OWN pre-fitted
    parameters -- not free here, not parameter-free either) and report the
    residual vs the 9-bar trace -- do NOT tune it away (card). mo2023_2's fresh-grain swelling
    over-closes an already-swollen saturated rig, so the composite Q collapses ->
    a LARGE residual diagnosing that the swelling branch does not apply here."""
    tr = _d.waszkiewicz_traces()
    t = tr[P_bar]["time__s"]; q = tr[P_bar]["mass_flow_rate__g_per_s"]
    r = simulate(P_bar=P_bar, t=t, branches=("extraction", "swelling"), powder=powder)
    sel = (t >= window[0]) & (t <= window[1])
    rmse = float(np.sqrt(np.nanmean((r["Q"][sel] - q[sel]) ** 2)))

    # HOW the composite fails matters more than that it fails (Paper 3 review MC13 / Paper B2).
    # The imported swelling branch drives eps below eps0 everywhere in the window, so the
    # dissolved-mass proxy m_d_eff sits on its floor, Phi -> ~0, and q_dynamic_from_md reduces
    # to its OWN Phi->0 limit -- the STATIC curve. The composite therefore does not merely score
    # worse than the temporal branch: it emits a CONSTANT and destroys the temporal signal
    # entirely. Reporting the residual alone hides that, and makes the composite RMSE look like
    # an independent number when it is numerically the static branch's RMSE.
    floor = _np_dose_floor(r["m_d_eff"], r["eps0"])
    q_pred = r["Q"][sel]
    spread = float(np.nanmax(q_pred) - np.nanmin(q_pred))
    return dict(rmse=rmse, eps_min_reached=float(np.min(r["eps"])), clamped=r["clamped"],
                swelling_closes=bool(np.min(r["eps"]) < r["eps0"]),
                phi_floor_fraction_in_window=round(float(np.mean(floor[sel])), 4),
                predicted_flow_spread_g_per_s=round(spread, 9),
                reduces_to_static_limit=bool(spread < 1e-9),
                collapse_note=("the swelling branch pushes eps below eps0 across the window, so "
                               "the dissolved-mass proxy is on its floor and the closure returns "
                               "its Phi->0 limit: a CONSTANT flow equal to the static curve. The "
                               "composite RMSE therefore coincides with the static branch's RMSE "
                               "by construction, not by coincidence."))


def _np_dose_floor(m_d_eff, eps0, rtol=1e-9):
    """Boolean mask of where the dissolved-mass proxy sits on its floor (so Phi is not a physical
    dissolved fraction there but a numerical guard keeping the closure defined)."""
    m = np.asarray(m_d_eff, float)
    return np.abs(m - np.nanmin(m)) <= rtol * max(float(np.nanmax(m)), 1.0)
