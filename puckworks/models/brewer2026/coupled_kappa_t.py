"""coupled_kappa_t.py — brewer2026 coupled kappa(t) porosity-evolution synthesis.

Card: docs/cards/brewer2026_coupled_kappa_t.md. A SYNTHESIS component (no external
paper): one shared porosity state eps(t) that every registered bed-evolution
mechanism reads and writes, replacing the earlier multiplicative harness closure
kappa = f1*f2*f3*f4 (which double-counts pore volume because the factors never
see each other). The four branches compose ADDITIVELY on the shared porosity:

    eps(t) = eps0 * (1 + Phi_ext(t) - Phi_swell(t) - Phi_comp(t) - Phi_fines(t))
    clamped to [eps_min, eps_max]  (a clamp hit is a DOCUMENTED regime edge)

Branches (each inherits its donor component's law; this card fixes only signs/
units/coupling):
  extraction  (+, opens): waszkiewicz2025 m_d(t)/dose  (== its Phi(t))
  swelling    (-, closes): mo2023_2.swelling eps_b(t)   (fixed-dP, UNVALIDATED)
  compaction  (-, closes): fasano2000_partII (8.69)     (params UNIDENTIFIED -> stub)
  fines       (-, closes): fasano2000_partI             (params UNIDENTIFIED -> stub)

Flow closure -- CARD AMBIGUITY, flagged: card Eq.2 says kappa=Kozeny-Carman(eps),
but its degeneracy gate requires the extraction-only limit to 'reproduce
waszkiewicz2025.poroelastic EXACTLY' and states 'the poroelastic branch alone
already fits (rung 4, RMSE 0.113)'. These are inconsistent: the 9-bar flow rises
14x (0.14->2.0 g/s) on a small porosity change (Phi 0.03->0.12) because the flow
is near-choke, where the poroelastic closure (Eq.18) amplifies tiny porosity
changes -- Kozeny-Carman is far too gentle (RMSE ~1.5, not 0.116). So the FLOW is
driven through waszkiewicz's poroelastic closure with the composite porosity as
an effective m_d (extraction-only -> exact rung 4); kappa_CK(eps) is ALSO reported
per Eq.2 but does NOT reproduce the near-choke flow. -> Tim to reconcile Eq.2.

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
    """Add the swelling branch (parameter-free) and report the residual vs the
    9-bar trace -- do NOT tune it away (card). mo2023_2's fresh-grain swelling
    over-closes an already-swollen saturated rig, so the composite Q collapses ->
    a LARGE residual diagnosing that the swelling branch does not apply here."""
    tr = _d.waszkiewicz_traces()
    t = tr[P_bar]["time__s"]; q = tr[P_bar]["mass_flow_rate__g_per_s"]
    r = simulate(P_bar=P_bar, t=t, branches=("extraction", "swelling"), powder=powder)
    sel = (t >= window[0]) & (t <= window[1])
    rmse = float(np.sqrt(np.nanmean((r["Q"][sel] - q[sel]) ** 2)))
    return dict(rmse=rmse, eps_min_reached=float(np.min(r["eps"])), clamped=r["clamped"],
                swelling_closes=bool(np.min(r["eps"]) < r["eps0"]))
