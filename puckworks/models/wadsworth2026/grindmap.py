"""grindmap.py — Wadsworth et al. 2026 grinder transfer function (grind stage).

Card: docs/cards/wadsworth2026_grindmap.md (ROADMAP item 1.5). Same paper as
wadsworth2026.permeability (R. Soc. Open Sci. 13, 252031; confirmed one paper).
CALIBRATION provider: an offline map from a Mahlkonig dial setting G to the mean
grain radius <R> (their Eq. 1, linear from burr-gap physics) plus the observed
polydispersivity S(G). Feeds GrindState.mean_radius_m / porosity priors; no
runtime coupling.

    <R> = beta*G + R0                     (Eq. 1)
    S   = <R><R^2>/<R^3>   in (0,1]       (Eq. 2; 1 = monodisperse)

Data: data/wadsworth2026/wadsworth2026_table1_full.csv (22 samples = two coffees
x 11 settings), supplied 2026-07-10.

CARD CORRECTION (2026-07-11, resolved): the card previously printed
beta = 4.3505e-5, R0 = 1.0160e-4 — a transcription typo (confirmed by Tim). An
OLS refit of Table 1 <R> vs G (22 samples) gives beta = 5.8050e-5,
R0 = 1.3797e-4 (R^2 = 0.994); the old slope was ~1.33x too shallow to span the
measured 192-818 um range. The card of record now carries the corrected values,
which match the operative constants below. Moment columns are self-consistent
(S = <R><R^2>/<R^3> reproduces the reported S).

Validity (card): Mahlkonig, this burr set + calibration ONLY; G 1-11,
<R> ~145-818 um; below G=1 (espresso-fine) unsupported and R0 is an extrapolation
artifact, not a physical floor. Grinder-specific — NEVER port dials to another
grinder (e.g. Cameron EK43) without refitting (ledger A9; CLAUDE.md rule 9).
"""
from dataclasses import dataclass

import numpy as np

from puckworks import data as _d

# Operative constants: OLS refit of Table 1 <R> vs G (R^2=0.994).
BETA_FIT = 5.8050e-5     # m per setting
R0_FIT = 1.3797e-4       # m
# Corrected card values (2026-07-11) — now agree with the refit; the gate keeps
# checking card == data as a regression. (Pre-correction typo: 4.3505e-5/1.016e-4.)
BETA_CARD = 5.8050e-5
R0_CARD = 1.3797e-4


def fit_grind_map(rows=None):
    """OLS refit of <R> = beta*G + R0 over Table 1. Returns (beta, R0, stats)."""
    rows = rows or _d.wadsworth_grindmap_table1()
    G = np.array([r["G"] for r in rows], float)
    R = np.array([r["R_mean_m"] for r in rows], float)
    A = np.vstack([G, np.ones_like(G)]).T
    (beta, R0), *_ = np.linalg.lstsq(A, R, rcond=None)
    resid = R - (beta*G + R0)
    r2 = 1.0 - np.sum(resid**2)/np.sum((R - R.mean())**2)
    return beta, R0, dict(r2=float(r2), n=len(G),
                          rms_resid_m=float(np.sqrt(np.mean(resid**2))))


def mean_radius(G, beta=BETA_FIT, R0=R0_FIT):
    """<R> [m] from dial setting G (Eq. 1). Grinder-specific; see GrindMap."""
    return beta*np.asarray(G, float) + R0


def polydispersity(R1, R2, R3):
    """S = <R><R^2>/<R^3> (Eq. 2). S->1 monodisperse, S->0 highly polydisperse."""
    return np.asarray(R1, float)*np.asarray(R2, float)/np.asarray(R3, float)


# --- A9 dial-space adapter stub (ledger A9) ------------------------------
@dataclass(frozen=True)
class GrindMap:
    """A per-grinder dial->radius map. Refuses to evaluate outside its
    calibrated setting range and cannot be applied to another grinder's dial
    (ledger A9 / CLAUDE.md rule 9: dial spaces are non-portable)."""
    grinder: str
    beta: float
    R0: float
    G_min: float
    G_max: float

    def mean_radius_m(self, G, strict=True):
        G = np.asarray(G, float)
        if strict and (np.any(G < self.G_min) or np.any(G > self.G_max)):
            raise ValueError(
                f"G outside calibrated range [{self.G_min}, {self.G_max}] for "
                f"grinder '{self.grinder}'; extrapolation is unsupported (card).")
        return self.beta*G + self.R0


#: The only calibrated map on file. Its dial numbers are NOT interchangeable
#: with cameron2020's EK43 dial or schmieder2023's E65S dial (G5).
WADSWORTH_MAHLKONIG = GrindMap("wadsworth_mahlkonig", BETA_FIT, R0_FIT, 1.0, 11.0)


def port_dial(*_args, **_kwargs):
    """A9 guard: cross-grinder dial porting is not implemented and must never be
    faked. A real adapter requires an explicit refit on the target grinder."""
    raise NotImplementedError(
        "Cross-grinder dial porting requires an explicit refit adapter (ledger "
        "A9). Dial maps are grinder/burr/calibration-specific and non-portable.")
