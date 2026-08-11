"""RP-D-LC-001b — corrected lateral-only virtual fixture: geometry, frozen configuration,
observable contract, admission gates and decision semantics.

PRE-EXECUTION. No lattice-Boltzmann solve is performed anywhere in this module, and none has
been performed for this tranche. Everything here is design: deterministic geometry, the frozen
forcing law, the plane/record contract, the negative-control and reachable-set admission
arithmetic, and the decision ordering. The slow driver that will eventually consume it is
``puckworks/validation/slow/rp_d_lc_001b.py`` and it refuses to run until an approved freeze
artifact exists.

RP-D-LC-001 (``docs/analysis/rp_d_lc_001/``) is CLOSED and IMMUTABLE: disposition
``INVALID_EXECUTION``, cross-model transfer UNADJUDICATED (not negative). Nothing in this module
reads, rewrites, repairs or reinterprets that bundle. 001b asks the SAME Stage-A question with a
corrected virtual apparatus; it is not a new question, not Stage B, not a Foundry screen, not a
new evidence rung, not a new registered component, and it authorizes neither Paper 4 nor any
wider RP-D work.

Two defects of the 001 execution are remedied here, and only those two:

  D1  the two resolutions were not the same dimensionless problem (001 erratum E5), and the
      forcing was high enough that the internal fields failed their own forcing-independence
      requirement (E2).  ->  a resolution-dependent forcing law g(S) = g_ref (S_ref/S)^3 that
      holds the design Reynolds number invariant, at a tenfold reduced reference forcing.

  D2  the bridge aperture was a hole through a thin divider, so opening it WIDENED THE AXIAL
      CHANNEL as well as creating a lateral path: with zero lateral driver the identical-path
      control still measured ``observed R - network R = 0.014277334586`` (001 erratum E7).
      ->  a lateral-only bridge whose lane-facing ports are present in the blocked fixture too,
      so the blocked/open difference is EXACTLY the connecting duct and nothing else.

and one measurement defect is closed: 001 recorded only ``sum(u_x)`` and could not evaluate mass
conservation at all (E4/E4b). Here every required plane retains BOTH ``sum(u_x)`` (the volume
flux the inverse consumes) and ``sum(rho*u_x)`` (the conserved mass flux), never conflated.
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
from fractions import Fraction

import numpy as np

from puckworks.analysis import rp_d_lc_virtual_fixture as vf001

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class NonFiniteValue(ValueError):
    """A quantity that must be finite was NaN or infinite (erratum PE-3). Raised rather than
    serialised, hashed or adjudicated."""


_SHA256_CHARS = set("0123456789abcdef")


def assert_flat_hash_list(values, what):
    """A flat, ordered, unique list of canonical lowercase SHA-256 strings (erratum PE-24).

    The superseded assembler built lists OF LISTS and then applied ``set()`` to them. Nesting is
    rejected here rather than discovered as an unhashable-type error three calls later.
    """
    if not isinstance(values, (list, tuple)):
        raise ValueError("%s must be a flat list of hashes, got %r" % (what, type(values)))
    out = []
    for v in values:
        if isinstance(v, (list, tuple, set, dict)):
            raise ValueError("%s contains a nested value %r; hash lists must be flat" % (what, v))
        if not isinstance(v, str) or len(v) != 64 or not set(v) <= _SHA256_CHARS:
            raise ValueError("%s contains %r, which is not a canonical lowercase SHA-256"
                             % (what, v))
        out.append(v)
    if len(set(out)) != len(out):
        raise ValueError("%s contains a duplicate hash" % (what,))
    return out


def assert_flat_id_list(values, what):
    """A flat, ordered, unique list of case IDs."""
    if not isinstance(values, (list, tuple)):
        raise ValueError("%s must be a flat list of case IDs, got %r" % (what, type(values)))
    out = []
    for v in values:
        if not isinstance(v, str) or not v:
            raise ValueError("%s contains %r, which is not a case ID" % (what, v))
        out.append(v)
    if len(set(out)) != len(out):
        raise ValueError("%s contains a duplicate case ID" % (what,))
    return out


class ExecutionAuthorityError(RuntimeError):
    """The execution authority could not be established. Always fail closed: never return a
    partial or None-valued authority record (erratum PE-11)."""

PROGRAM_ID = "RP-D-LATERAL-CROSS-MODEL"
TRANCHE_ID = "RP-D-LC-001B"
SCHEMA_VERSION = 1

#: The effective pre-execution correction version. Every generated artifact carries it, so a
#: machine-readable record can never be mistaken for a superseded one. Lineage and the exact
#: superseded hashes: docs/analysis/rp_d_lc_001b/PREFLIGHT_ERRATA.md.
CORRECTION_VERSION = "PREFLIGHT-C4"
ERRATA_PATH = "docs/analysis/rp_d_lc_001b/PREFLIGHT_ERRATA.md"
#: The exact-head reviews that required each correction, oldest first. Every generation's hashes
#: are kept so anything bound to a superseded artifact stays traceable.
SUPERSEDED_REVIEWS = (
    {
        "correction_version": "PREFLIGHT-C0",
        "reviewed_head": "bbf2304665d09cb78c117353947ce8c6cf2e5d24",
        "reviewed_tree": "c028f652b85b9b8670f9be03f8093e6bdae9d276",
        "disposition": "RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_CORRECTION_REQUIRED",
        "errata": ["PE-%d" % i for i in range(1, 13)],
        "superseded_artifact_sha256": {
            "protocol.json": "047d55f4dcd222b79f20f3d08e04b8de0dd13e7ddb8438cb74bf35ee6461cbe7",
            "fixture_spec.json": "c8592643b861150b534f6f823336a1e14b1d082e9f8c5bcf25957a4417d9fc2f",
            "execution_matrix.json": "1ff57d57c77eb56017628c52b80f1e70da549132a84b98e07e1ef300ec30fa74",
            "preflight_status.json": "01244d1c9b129aa22681ec84391adddc14c20a169acf903cfad99ee75fb642f3",
        },
    },
    {
        "correction_version": "PREFLIGHT-C1",
        "reviewed_head": "2cf0b63ba2670de423a39f9563822563a3cb59b5",
        "reviewed_tree": "c8a22d140b75142cdbd5db03dea55f20382bb079",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REREVIEW_NOT_APPROVED_C2_AND_"
                        "PREFREEZE_EXECUTOR_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(13, 22)],
        "superseded_artifact_sha256": {
            "protocol.json": "9b60b4d511d6153d92da14c7f7235f335536fa937958cc035eb4a9d6f163ea11",
            "fixture_spec.json": "11f1798c420373daf4ceff6d71cacf58318852cf01f55b3af85ab562acae0fec",
            "execution_matrix.json": "5d246088a1404ddb2ead1acfa4bc7074de9a8244688d28aca7c698e7d0e3193e",
            "preflight_status.json": "5bc0d5779218554b74106b38dcdcd73901a7502e10dfcec866d1f51891f834e1",
        },
        "superseded_counts": {"adaptive_maximum": 407, "mandatory_minimum": 82,
                              "refused_after_earliest_stop": 325, "n_frozen_bridges": 5,
                              "arm_j_planned_solves": 20},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
    },
    {
        "correction_version": "PREFLIGHT-C2",
        "reviewed_head": "c66670770d6b34b355fe29dba384102fc59827d7",
        "reviewed_tree": "002f7bae2d5a6c0f890b6144ae515b4af73d97ed",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C3_EXECUTOR_AND_"
                        "ASSEMBLER_CORRECTION_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(22, 40)],
        "superseded_artifact_sha256": {
            "protocol.json": "ae52600c5d2d8ce0a8b86d31545b6fc40b92228fc805542dc3a9ee8ac645a21f",
            "fixture_spec.json": "d931b3616948995a45237c7c781503dc5fc25618ae04be015f4b03b03fceb074",
            "execution_matrix.json":
                "6e6140a1b07b2fbf13e69a12044d5927e3a6f3c10cca91356316dbd85410f81c",
            "preflight_status.json":
                "5d8cf61abdac1f4399de1f282441c5fd139b8d3f1e44c7b3c7ac5d1a0708ec73",
        },
        "superseded_counts": {"adaptive_maximum": 703, "planned_normal_solves": 383,
                              "planned_fixed_step_audits": 320, "mandatory_minimum": 112,
                              "refused_after_earliest_stop": 591},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
    },
    {
        "correction_version": "PREFLIGHT-C3",
        "reviewed_head": "39533ade0fd74dc5fa10470710ec672041e62526",
        "reviewed_tree": "1a8594340299cfc80e340012fcc4cda481cd491f",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C4_INTEGRATION_"
                        "AND_AUTHORITY_CORRECTION_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(40, 60)],
        "superseded_artifact_sha256": {
            "protocol.json": "e46395b63bcc9d493365a74767475247d640096d834119cc76a35fb2a031e1f8",
            "fixture_spec.json": "833f1d5edf8c1b4a54c1b3977ede4d2f14f92196a53738c0ced8c0e1c6d05023",
            "execution_matrix.json":
                "71371972b8553a81b3db98555ccec8b86acfc86108325ff23eee77662a4bb914",
            "preflight_status.json":
                "61214acee1fdcf846eacd6f6a0ede6a04ef5ec77c45fdb6df5afdd0b63003c16",
        },
        "superseded_counts": {"adaptive_maximum": 847, "planned_normal_solves": 383,
                              "planned_fixed_step_audits": 320,
                              "planned_pressure_plane_diagnostic_rows": 144,
                              "mandatory_minimum": 112, "refused_after_earliest_stop": 735},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
    },
)
#: Backwards-compatible alias for the most recent superseded review.
SUPERSEDED_REVIEW = SUPERSEDED_REVIEWS[-1]

#: The exact authority this tranche was branched from. Verified by test, never inferred from HEAD.
BASE_COMMIT = "7d656811e6bf99d447dcd4f6eac04cac233a99f4"
BASE_TREE = "e31dc057a3e4d933ca71888b39e8b4d27ee6970d"

#: The closed predecessor. Its record is immutable and its failure is part of the durable
#: scientific record; this tranche re-executes the question, it does not repair that bundle.
PREDECESSOR = {
    "tranche": "RP-D-LC-001",
    "bundle": "docs/analysis/rp_d_lc_001",
    "disposition": "INVALID_EXECUTION",
    "cross_model_transfer_adjudicated": False,
    "evidence_use": "DIAGNOSTIC_ONLY_INVALID_EXECUTION",
    "axial_artifact_at_zero_lateral_driver": 0.014277334586,
    "note": "unadjudicated, NOT negative; field-derived truth insufficiently invariant with forcing",
}

BUNDLE_REL = "docs/analysis/rp_d_lc_001b"
PROTOCOL_PATH = BUNDLE_REL + "/PROTOCOL.md"
RUNS_REL = BUNDLE_REL + "/runs"
FREEZE_REL = RUNS_REL + "/bridge_freeze.json"

INPUT_FILES = (
    PROTOCOL_PATH,
    BUNDLE_REL + "/VIRTUAL_FIXTURE_SPEC.md",
    BUNDLE_REL + "/EXECUTION_MATRIX.md",
    "puckworks/analysis/rp_d_lc_001b_virtual_fixture.py",
    "puckworks/validation/slow/rp_d_lc_001b.py",
    "puckworks/models/brewer2026/lb_reference.py",
    "puckworks/analysis/screen_wp6_lateral_identifiability.py",
    "puckworks/analysis/rp_d_lc_virtual_fixture.py",
    "puckworks/models/lateral_coupling.py",
)

#: Copied BYTE-IDENTICAL from the 001 tranche. The claim ceiling is not renegotiated by a
#: re-execution; a test asserts the two tuples are equal.
CLAIM_CEILING = tuple(vf001.CLAIM_CEILING)

#: The Stage-A question, unchanged from 001. This tranche asks it again with a corrected
#: apparatus; it does not ask a new one.
QUESTION = (
    "When the ground truth is generated by an independently implemented, spatially resolved 3D "
    "creeping-flow solver rather than by model1_two_path, does the WP6-LC-IDENT boundary inverse "
    "recover the virtual fixture's independently field-derived effective lateral-coupling "
    "number Xi?"
)


# ==========================================================================================
# 1. FROZEN BASE GEOMETRY TEMPLATE — the corrected LATERAL-ONLY bridge
# ==========================================================================================
# All lengths are BASE VOXELS; a fixture at resolution S replicates every base voxel into an
# S^3 block, so two resolutions are EXACTLY geometrically similar. Flow is +x. The box is
# periodic in x (the common plenum wraps) and closed by solid no-slip walls on both y and both
# z faces, so no periodic lateral bypass can exist.
#
# The x layout is unchanged from 001. The y layout is NOT: the divider is thickened from 2 to 6
# base voxels and given an internal three-layer structure
#
#       lane 1 | port row A | duct row | port row B | lane 2
#        1..8      9..10       11..12      13..14      15..22
#
# The BLOCKED fixture opens port rows A and B over the bridge footprint but leaves the duct row
# SOLID. The OPEN fixture additionally opens the duct row. Consequently:
#
#   * the blocked/open difference is EXACTLY the duct-row footprint — the intended lateral
#     connection and nothing else;
#   * the lane-facing recesses (the ports) are common-mode: they exist in the denominator of
#     R as well as the numerator, so R compares the SAME axial network with the lateral
#     connection off and on. That is precisely what the two-node model's R means, and it is
#     what 001's blocked fixture did not provide;
#   * both ports sit at the SAME x footprint, so traversing the bridge produces no axial
#     displacement;
#   * the divider is fully solid in x immediately outside the footprint, so the bridge is
#     axially end-capped and no route through it connects two different x stations.

BASE = {
    # ---- x: [common plenum] [upstream segment] [transition] [downstream segment] -> wrap ----
    "nx": 56,
    "plenum_half": 4,                      # plenum = {x : min(x, nx - x) < 4} = {53,54,55,0,1,2,3}
    "lane_lo": 4, "lane_hi": 52,
    "seg_top_lo": 4, "seg_top_hi": 23,     # 20 base voxels
    "trans_lo": 24, "trans_hi": 32,        # 9 base voxels, both lanes at h_low, hosts the bridge
    "seg_bot_lo": 33, "seg_bot_hi": 52,    # 20 base voxels
    "bridge_centre": 28,
    # ---- y: wall | lane 1 | port A | duct | port B | lane 2 | wall ----
    "ny": 24,
    "lane1_lo": 1, "lane1_hi": 8,
    "portA_lo": 9, "portA_hi": 10,
    "duct_lo": 11, "duct_hi": 12,
    "portB_lo": 13, "portB_hi": 14,
    "lane2_lo": 15, "lane2_hi": 22,
    # ---- z: wall | fluid | wall ; the conductance contrast is the slot height ----
    "nz": 8,
    "z_lo": 1,
    "h_high": 6, "h_low": 4,
}

#: Predeclared bridge CANDIDATE family. ``w`` (the footprint's x extent, base voxels) must be odd
#: so the bridge is centred on the mirror plane x = bridge_centre; ``kz`` counts base voxels
#: upward from z_lo. w = 9 fills the transition band exactly.
BRIDGE_CANDIDATES = tuple(
    {"w": w, "kz": kz} for w in (3, 5, 7, 9) for kz in (1, 2, 3, 4)
)

#: Minimum resolved feature, in LATTICE voxels, carried over unchanged from 001 where it was
#: justified by the measured plane-channel law error(%) = 50/h^2. kz = 1 is 2 lattice voxels at
#: S_COARSE (a ~12 % element error) and is therefore excluded from the scientific subset; it
#: remains a declared candidate so the exclusion is visible rather than silent.
MIN_FEATURE_VOX = 4
CHANNEL_ERR_LAW_PCT = "50/h^2"

S_SMOKE = 1
S_COARSE = 2
S_FINE = 3
SCIENTIFIC_RESOLUTIONS = (S_COARSE, S_FINE)

#: The scientific bridge subset: every candidate whose smallest feature is resolved at S_COARSE.
SCIENTIFIC_BRIDGE_CANDIDATES = tuple(
    b for b in BRIDGE_CANDIDATES
    if b["kz"] * S_COARSE >= MIN_FEATURE_VOX and b["w"] * S_COARSE >= MIN_FEATURE_VOX
)

#: Predeclared one-voxel adversarial perturbations (carried over from 001, retargeted to this
#: template's lane-1 downstream segment). Coordinates are BASE voxels; each flips exactly one
#: lattice voxel (plug) or one lattice-voxel-thick slab at any S.
PERTURBATIONS = {
    "one_voxel_plug": {"kind": "plug", "base": (40, 4, 2)},
    "one_voxel_slab": {"kind": "slab", "base_x": 23, "lane": 1},
}


def _base_is_plenum(x: int) -> bool:
    return min(x, BASE["nx"] - x) < BASE["plenum_half"]


def _base_lane_height(x: int, lane: int) -> int:
    """Slot height (base voxels, counted up from z_lo) of ``lane`` at base station ``x``."""
    if BASE["seg_top_lo"] <= x <= BASE["seg_top_hi"]:
        return BASE["h_high"] if lane == 1 else BASE["h_low"]
    if BASE["seg_bot_lo"] <= x <= BASE["seg_bot_hi"]:
        return BASE["h_low"] if lane == 1 else BASE["h_high"]
    return BASE["h_low"]                       # the transition band: both lanes low


def bridge_x_range(w: int):
    """Inclusive base-voxel x range of a bridge of footprint width ``w``."""
    w = int(w)
    if w % 2 != 1:
        raise ValueError("bridge w must be odd so the footprint is centred on the mirror plane, "
                         "got %r" % (w,))
    half = (w - 1) // 2
    lo, hi = BASE["bridge_centre"] - half, BASE["bridge_centre"] + half
    if lo < BASE["trans_lo"] or hi > BASE["trans_hi"]:
        raise ValueError("bridge w=%r does not fit the transition band" % (w,))
    return lo, hi


def _validate_bridge(bridge):
    w, kz = int(bridge["w"]), int(bridge["kz"])
    bridge_x_range(w)
    if not 1 <= kz <= BASE["h_low"]:
        raise ValueError("bridge kz must lie in 1..%d, got %r" % (BASE["h_low"], kz))
    return w, kz


def base_mask(bridge=None, connected=False, variant="mirror"):
    """The frozen base template as a boolean SOLID mask of shape (nx, ny, nz).

    ``bridge`` None  -> the REFERENCE fixture: the divider is continuous, there is no bridge
                        structure at all. Used only for the common blocked characterisation.
    ``bridge`` dict  -> a bridge of footprint ``{w, kz}``. ``connected`` False opens the two
                        lane-facing PORT rows only (the BLOCKED fixture); True additionally opens
                        the DUCT row that joins them (the OPEN fixture).
    ``variant``      -> 'mirror' (lane 2 carries the reversed segment order) or 'identical'
                        (both lanes ordered like lane 1 — the negative control, for which the
                        cross-product gap X = g1t*g2b - g2t*g1b vanishes exactly and no lateral
                        pressure difference drives the bridge at any conductance).
    """
    if variant not in ("mirror", "identical"):
        raise ValueError("variant must be 'mirror' or 'identical', got %r" % (variant,))
    if bridge is None and connected:
        raise ValueError("connected=True requires a bridge footprint")
    nx, ny, nz = BASE["nx"], BASE["ny"], BASE["nz"]
    solid = np.ones((nx, ny, nz), dtype=bool)
    z_lo, z_hi_full = BASE["z_lo"], BASE["z_lo"] + BASE["h_high"] - 1
    for x in range(nx):
        if _base_is_plenum(x):
            solid[x, 1:ny - 1, z_lo:z_hi_full + 1] = False      # one common, full-section node
            continue
        for lane, (ylo, yhi) in ((1, (BASE["lane1_lo"], BASE["lane1_hi"])),
                                 (2, (BASE["lane2_lo"], BASE["lane2_hi"]))):
            h = _base_lane_height(x, 1 if variant == "identical" else lane)
            solid[x, ylo:yhi + 1, z_lo:z_lo + h] = False
    if bridge is not None:
        w, kz = _validate_bridge(bridge)
        xlo, xhi = bridge_x_range(w)
        rows = [(BASE["portA_lo"], BASE["portA_hi"]), (BASE["portB_lo"], BASE["portB_hi"])]
        if connected:
            rows.append((BASE["duct_lo"], BASE["duct_hi"]))
        for ylo, yhi in rows:
            solid[xlo:xhi + 1, ylo:yhi + 1, z_lo:z_lo + kz] = False
    return solid


def scale(mask_b, S: int):
    """Replicate a base mask S times on every axis — exact geometric similarity."""
    if not isinstance(S, int) or isinstance(S, bool) or S < 1:
        raise ValueError("S must be a positive int, got %r" % (S,))
    return np.repeat(np.repeat(np.repeat(mask_b, S, axis=0), S, axis=1), S, axis=2)


def mirror_x(mask, S: int):
    """The exact voxel-index x reflection about the mirror planes x = 0 and x = bridge_centre."""
    return np.roll(np.flip(mask, axis=0), S, axis=0)


def swap_paths(mask):
    """The exact path swap: reflect y about the divider mid-plane, exchanging lane 1 and lane 2.
    An index transformation of the SAME array — the swapped fixture is never rebuilt. The y
    layout is palindromic (wall|8|2|2|2|8|wall), so the flip maps port row A onto port row B and
    the duct row onto itself."""
    return np.flip(mask, axis=1)


def _apply_perturbation(mask, S: int, name: str):
    spec = PERTURBATIONS[name]
    out = mask.copy()
    if spec["kind"] == "plug":
        bx, by, bz = spec["base"]
        out[bx * S, by * S, bz * S] = True                      # exactly one lattice voxel
    elif spec["kind"] == "slab":
        x = (spec["base_x"] + 1) * S - 1
        ylo, yhi = BASE["lane1_lo"] * S, (BASE["lane1_hi"] + 1) * S - 1
        zlo = (BASE["z_lo"] + BASE["h_low"]) * S
        zhi = (BASE["z_lo"] + BASE["h_high"]) * S - 1
        out[x, ylo:yhi + 1, zlo:zhi + 1] = True
    else:                                                        # pragma: no cover - frozen set
        raise ValueError("unknown perturbation kind %r" % (spec["kind"],))
    return out


#: The three fixture states. Named so a record can never be ambiguous about which one produced it.
FIXTURE_STATES = ("reference_blocked", "blocked", "open")


def fixture_state(bridge, connected) -> str:
    if bridge is None:
        return "reference_blocked"
    return "open" if connected else "blocked"


#: The RP-D-LC-001b plenum obstruction (erratum PE-36). ADDITIVE: it changes nothing in
#: RP-D-LC-001, its fixture module, its driver or lb_reference. It acts ONLY inside the common
#: plenum, touches no lane, port, duct or divider voxel, and is placed symmetrically about the
#: x = 0 mirror plane so the fixture's mirror relationship survives.
OBSTRUCTION = {
    "kind": "PLENUM_SLAB_001B",
    "base_x": (55, 0, 1),            # inside the plenum; EXACTLY symmetric under b -> (56-b)%56
    "base_y": (6, 17),               # inclusive band, centred on the full-section plenum
    "base_z": (2, 4),                # inclusive band, inside the plenum's fluid height
    "note": ("obstructs the common return path only; preserves every lane, port, duct and "
             "divider solid, and is symmetric about the x = 0 mirror plane"),
}


def apply_obstruction(mask, S: int):
    """Return a NEW mask with the frozen plenum obstruction applied (erratum PE-36).

    Raises if the obstruction cannot be constructed exactly — if any target voxel is already
    solid, the geometry is not the one the specification describes.
    """
    out = mask.copy()
    ylo, yhi = OBSTRUCTION["base_y"]
    zlo, zhi = OBSTRUCTION["base_z"]
    ys, ye = ylo * S, (yhi + 1) * S
    zs, ze = zlo * S, (zhi + 1) * S
    touched = 0
    for bx in OBSTRUCTION["base_x"]:
        if not _base_is_plenum(bx):                          # pragma: no cover - frozen spec
            raise ValueError("obstruction base station %r is not in the plenum" % (bx,))
        xs, xe = bx * S, (bx + 1) * S
        block = out[xs:xe, ys:ye, zs:ze]
        if block.any():
            raise ValueError("the obstruction footprint at base x=%d is not entirely fluid; the "
                             "geometry is not the one the specification describes" % bx)
        out[xs:xe, ys:ye, zs:ze] = True
        touched += block.size
    if touched == 0:                                          # pragma: no cover - frozen spec
        raise ValueError("the obstruction changed nothing")
    return out


def obstruction_report(mask, obstructed, meta):
    """Compact proof that the obstruction is confined to the plenum and changes nothing else."""
    diff = np.argwhere(mask != obstructed)
    S = meta["S"]
    lane_x = meta["lane_x"]
    return {
        "specification": dict(OBSTRUCTION),
        "n_changed_voxels": int(diff.shape[0]),
        "changed_x_range": (int(diff[:, 0].min()), int(diff[:, 0].max())) if diff.size else None,
        "all_changes_in_plenum": bool(all(
            not (lane_x[0] <= int(x) < lane_x[1]) for x in diff[:, 0])),
        "lane_and_bridge_unchanged": bool(np.array_equal(mask[lane_x[0]:lane_x[1]],
                                                         obstructed[lane_x[0]:lane_x[1]])),
        # The obstruction must PRESERVE whatever relationship the nominal fixture has: the
        # mirror variant is mirror-symmetric, the identical-path variant is swap-invariant.
        # It may not create or destroy either.
        "nominal_mirror_symmetric": bool(is_mirror_symmetric(mask, S)),
        "obstructed_mirror_symmetric": bool(is_mirror_symmetric(obstructed, S)),
        "nominal_swap_invariant": bool(np.array_equal(swap_paths(mask), mask)),
        "obstructed_swap_invariant": bool(np.array_equal(swap_paths(obstructed), obstructed)),
        "relationship_preserved": bool(
            is_mirror_symmetric(mask, S) == is_mirror_symmetric(obstructed, S)
            and np.array_equal(swap_paths(mask), mask)
            == np.array_equal(swap_paths(obstructed), obstructed)),
        "mask_sha256": mask_hash(obstructed),
        "differs_from_nominal": bool(mask_hash(mask) != mask_hash(obstructed)),
    }


def build_fixture(S: int, bridge=None, connected=False, variant="mirror", swapped=False,
                  perturbation=None, obstructed=False):
    """The full virtual fixture at resolution S, with its frozen region and plane indices."""
    mask = scale(base_mask(bridge=bridge, connected=connected, variant=variant), S)
    if swapped:
        mask = swap_paths(mask)
    if perturbation is not None:
        mask = _apply_perturbation(mask, S, perturbation)
    if obstructed:
        mask = apply_obstruction(mask, S)
    meta = fixture_meta(S, bridge=bridge, connected=connected, variant=variant,
                        swapped=swapped, perturbation=perturbation, mask=mask)
    meta["obstructed"] = bool(obstructed)
    if obstructed:
        meta["obstruction"] = dict(OBSTRUCTION)
    return mask, meta


def fixture_meta(S, bridge=None, connected=False, variant="mirror", swapped=False,
                 perturbation=None, mask=None):
    """Every frozen index the observable calculation is allowed to use. Nothing here is fitted."""
    nx, ny, nz = BASE["nx"] * S, BASE["ny"] * S, BASE["nz"] * S
    meta = {
        "S": S, "variant": variant, "swapped": bool(swapped), "perturbation": perturbation,
        "bridge": None if bridge is None else {"w": int(bridge["w"]), "kz": int(bridge["kz"])},
        "connected": bool(connected),
        "state": fixture_state(bridge, connected),
        "shape": (nx, ny, nz),
        "lane1_y": (BASE["lane1_lo"] * S, (BASE["lane1_hi"] + 1) * S),
        "lane2_y": (BASE["lane2_lo"] * S, (BASE["lane2_hi"] + 1) * S),
        "divider_y": (BASE["portA_lo"] * S, (BASE["portB_hi"] + 1) * S),
        "duct_y": (BASE["duct_lo"] * S, (BASE["duct_hi"] + 1) * S),
        "lane_x": (BASE["lane_lo"] * S, (BASE["lane_hi"] + 1) * S),
        # ---- node surfaces: plenum planes abutting the lane ends, the only planes whose
        # cross-section is ONE connected common region, i.e. a genuine network node ----
        "x_node_in": BASE["lane_lo"] * S - 1,
        "x_node_out": (BASE["lane_hi"] + 1) * S,
        "node_offsets": (1, 2),
        # ---- outlet-flux measurement planes ----
        "x_meas_a": (BASE["lane_hi"] + 1) * S - 1,       # primary, immediately before the plenum
        "x_meas_b": 48 * S,                               # second frozen plane (plane invariance)
        "x_meas_in": BASE["lane_lo"] * S,                 # lane inlet plane
        # ---- transverse (bridge) instrumentation ----
        "y_face1": BASE["portA_lo"] * S - 1,              # last lane-1 row before the divider
        "y_face2": BASE["lane2_lo"] * S,                  # first lane-2 row after the divider
        "y_portA_in": BASE["portA_lo"] * S,               # first port-A row
        "y_duct_a": BASE["duct_lo"] * S,                  # first duct row
        "y_duct_b": (BASE["duct_hi"] + 1) * S - 1,        # last duct row
        "y_portB_out": (BASE["portB_hi"] + 1) * S - 1,    # last port-B row
        "axial_conservation_planes": axial_conservation_planes(S),
    }
    if bridge is not None:
        w, kz = _validate_bridge(bridge)
        xlo, xhi = bridge_x_range(w)
        meta["bridge_x"] = (xlo * S, (xhi + 1) * S)
        meta["bridge_z"] = (BASE["z_lo"] * S, (BASE["z_lo"] + kz) * S)
    else:
        meta["bridge_x"] = None
        meta["bridge_z"] = None
    if mask is not None:
        meta["mask_sha256"] = mask_hash(mask)
        meta["n_solid"] = int(mask.sum())
        meta["n_fluid"] = int((~mask).sum())
    return meta


#: Frozen axial conservation planes, in BASE stations. Spread over the whole lane traverse and
#: deliberately including one inside the transition band: the bridge is transverse, so the TOTAL
#: axial flux is conserved across it even where the per-lane split is not.
AXIAL_CONSERVATION_BASE = (4, 10, 16, 22, 28, 34, 40, 46)

#: The NINE adjudicative axial conservation plane IDs, in frozen order (erratum PE-1). Only
#: records carrying exactly these IDs, in this order, may enter the mass-conservation verdict.
#: The named measurement records (x_node_*, x_meas_*, lane records) are reported separately and
#: are NEVER admitted here: a min/max spread is decided by its extremes, so admitting a duplicate
#: of an extreme plane would move an adjudicative residual with no physics changing.
CONSERVATION_PLANE_IDS = tuple("cons_%d" % i for i in range(len(AXIAL_CONSERVATION_BASE) + 1))
N_CONSERVATION_PLANES = len(CONSERVATION_PLANE_IDS)


def axial_conservation_planes(S: int):
    """Lattice x indices of the frozen axial conservation plane set (the primary outlet plane
    is included so the conservation set and the observable plane cannot drift apart)."""
    planes = tuple(b * S for b in AXIAL_CONSERVATION_BASE) + ((BASE["lane_hi"] + 1) * S - 1,)
    if len(set(planes)) != len(planes):                      # pragma: no cover - frozen geometry
        raise ValueError("axial conservation planes are not unique at S=%r: %r" % (S, planes))
    return planes


def mask_hash(mask) -> str:
    """SHA-256 of the packed boolean mask plus its shape — the geometry's identity."""
    h = hashlib.sha256()
    h.update(("%d,%d,%d|" % mask.shape).encode())
    h.update(np.packbits(np.ascontiguousarray(mask, dtype=bool)).tobytes())
    return h.hexdigest()


def is_mirror_symmetric(mask, S: int) -> bool:
    """Exact voxel-index mirror test: swap_paths(mirror_x(mask)) == mask."""
    return bool(np.array_equal(swap_paths(mirror_x(mask, S)), mask))


def _periodic_x_components(fluid):
    from scipy import ndimage
    nx = fluid.shape[0]
    lab, n_raw = ndimage.label(np.concatenate([fluid, fluid], axis=0))
    a, b = lab[:nx], lab[nx:]
    parent = {}

    def find(k):
        parent.setdefault(k, k)
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for u, v in set(zip(a[fluid].ravel().tolist(), b[fluid].ravel().tolist())):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    return int(n_raw), {find(int(v)) for v in np.unique(a[fluid])}


def connectivity(mask, meta):
    """Connected-component audit: the fluid space must form ONE component under x-periodic /
    y,z-walled connectivity, and no fluid may touch a y or z face (no periodic lateral bypass)."""
    fluid = ~mask
    n_raw, comps = _periodic_x_components(fluid)
    y_face = bool(fluid[:, 0, :].any() or fluid[:, -1, :].any())
    z_face = bool(fluid[:, :, 0].any() or fluid[:, :, -1].any())
    return {"n_components_raw": n_raw, "n_components_periodic": len(comps),
            "fluid_on_y_face": y_face, "fluid_on_z_face": z_face,
            "single_connected": len(comps) == 1,
            "no_lateral_bypass": not (y_face or z_face)}


def lane_connection(mask, meta):
    """Is there a lateral connection between the lanes INSIDE the lane region?

    Global connectivity cannot answer this — the common plenum joins the lanes at both ends by
    design. The question is answered on the lane traverse alone, with the plenum excluded: the
    lanes must be joined in the OPEN fixture and separate in the blocked and reference ones.
    """
    from scipy import ndimage
    S = meta["S"]
    xlo, xhi = meta["lane_x"]
    sub = mask[xlo:xhi]
    lab, _ = ndimage.label(~sub)
    l1lo, l1hi = meta["lane1_y"]
    l2lo, l2hi = meta["lane2_y"]
    c1 = set(np.unique(lab[:, l1lo:l1hi, :]).tolist()) - {0}
    c2 = set(np.unique(lab[:, l2lo:l2hi, :]).tolist()) - {0}
    return {"lane1_components": len(c1), "lane2_components": len(c2),
            "lanes_joined_in_lane_region": bool(c1 & c2)}


def bridge_topology(mask, meta):
    """Structural audit of the bridge itself, on the mask alone.

    ``axial_end_caps_solid``  — the divider cross-section immediately outside the footprint in
                                x is fully solid on both sides, so no route through the bridge
                                connects two different x stations;
    ``bridge_x_span``         — the observed x extent of divider-band fluid inside the lane
                                region, which must equal the footprint exactly;
    ``ports_present``         — both lane-facing port rows carry fluid over the footprint;
    ``duct_present``          — the connecting duct row carries fluid (open fixture only).
    """
    S = meta["S"]
    dlo, dhi = meta["divider_y"]
    lxlo, lxhi = meta["lane_x"]
    band = mask[lxlo:lxhi, dlo:dhi, :]
    idx = np.argwhere(~band)
    out = {"divider_band_fluid_voxels": int(idx.shape[0])}
    if meta["bridge"] is None:
        out.update(bridge_x_span=None, axial_end_caps_solid=True, ports_present=False,
                   duct_present=False, bridge_x_expected=None)
        return out
    bxlo, bxhi = meta["bridge_x"]
    bzlo, bzhi = meta["bridge_z"]
    span = (int(idx[:, 0].min()) + lxlo, int(idx[:, 0].max()) + lxlo) if idx.size else None
    caps = bool(mask[bxlo - 1, dlo:dhi, :].all() and mask[bxhi, dlo:dhi, :].all())
    pA = (BASE["portA_lo"] * S, (BASE["portA_hi"] + 1) * S)
    pB = (BASE["portB_lo"] * S, (BASE["portB_hi"] + 1) * S)
    du = meta["duct_y"]
    ports = bool((~mask[bxlo:bxhi, pA[0]:pA[1], bzlo:bzhi]).all()
                 and (~mask[bxlo:bxhi, pB[0]:pB[1], bzlo:bzhi]).all())
    duct = bool((~mask[bxlo:bxhi, du[0]:du[1], bzlo:bzhi]).all())
    out.update(bridge_x_span=span, bridge_x_expected=(bxlo, bxhi - 1),
               axial_end_caps_solid=caps, ports_present=ports, duct_present=duct)
    return out


def blocked_open_delta(S: int, bridge, variant="mirror"):
    """The exact voxel difference between the blocked and open fixtures. It must be the duct-row
    footprint and nothing else — this is the whole point of the corrected apparatus."""
    blk, meta = build_fixture(S, bridge=bridge, connected=False, variant=variant)
    opn, _ = build_fixture(S, bridge=bridge, connected=True, variant=variant)
    diff = np.argwhere(blk != opn)
    bxlo, bxhi = meta["bridge_x"]
    dylo, dyhi = meta["duct_y"]
    bzlo, bzhi = meta["bridge_z"]
    expected = {"x": set(range(bxlo, bxhi)), "y": set(range(dylo, dyhi)),
                "z": set(range(bzlo, bzhi))}
    got = {"x": set(diff[:, 0].tolist()), "y": set(diff[:, 1].tolist()),
           "z": set(diff[:, 2].tolist())}
    n_expected = len(expected["x"]) * len(expected["y"]) * len(expected["z"])
    return {
        "n_differing_voxels": int(diff.shape[0]),
        "n_expected": n_expected,
        "is_exactly_the_duct_footprint": bool(diff.shape[0] == n_expected and got == expected),
        "solid_in_blocked_fluid_in_open": bool(diff.size and blk[tuple(diff.T)].all()
                                               and not opn[tuple(diff.T)].any()),
    }


def minimum_feature_report(S: int, bridge):
    """Every critical feature's size in LATTICE voxels, and whether it clears MIN_FEATURE_VOX."""
    w, kz = _validate_bridge(bridge)
    feats = {
        "lane_width": (BASE["lane1_hi"] - BASE["lane1_lo"] + 1) * S,
        "slot_height_low": BASE["h_low"] * S,
        "slot_height_high": BASE["h_high"] * S,
        "port_row_depth": (BASE["portA_hi"] - BASE["portA_lo"] + 1) * S,
        "duct_row_depth": (BASE["duct_hi"] - BASE["duct_lo"] + 1) * S,
        "bridge_transverse_length": (BASE["portB_hi"] - BASE["portA_lo"] + 1) * S,
        "bridge_footprint_x": w * S,
        "bridge_height_kz": kz * S,
    }
    return {"features_vox": feats, "min_feature_vox": MIN_FEATURE_VOX,
            "all_resolved": all(v >= MIN_FEATURE_VOX for v in feats.values()),
            "under_resolved": sorted(k for k, v in feats.items() if v < MIN_FEATURE_VOX)}


# ==========================================================================================
# 2. COUPON GEOMETRY
# ==========================================================================================

def build_axial_coupon(S: int, level: str, orientation: str = "x"):
    """A straight x-periodic duct coupon reproducing one axial segment: same slot height, same
    lane width, same length and the same wall treatment (a 1-base outer wall on one side, the
    6-base divider on the other), cropped so the y wrap joins solid to solid. ``orientation``
    'y' rotates the CROSS-SECTION (not the flow axis, which must stay +x) so the same duct is
    calibrated in two lattice orientations and anisotropy is reported rather than assumed away.
    """
    if level not in ("high", "low"):
        raise ValueError("level must be 'high' or 'low', got %r" % (level,))
    if orientation not in ("x", "y"):
        raise ValueError("orientation must be 'x' or 'y', got %r" % (orientation,))
    h = BASE["h_high"] if level == "high" else BASE["h_low"]
    lx = BASE["seg_top_hi"] - BASE["seg_top_lo"] + 1                  # 20 base voxels
    ny_b = BASE["portB_hi"] + 1                                       # wall + lane 1 + divider
    solid_b = np.ones((lx, ny_b, BASE["nz"]), dtype=bool)
    solid_b[:, BASE["lane1_lo"]:BASE["lane1_hi"] + 1, BASE["z_lo"]:BASE["z_lo"] + h] = False
    mask = scale(solid_b, S)
    if orientation == "y":
        mask = np.ascontiguousarray(np.swapaxes(mask, 1, 2))
    meta = {"S": S, "kind": "axial_coupon", "level": level, "orientation": orientation,
            "length_vox": lx * S, "shape": tuple(int(v) for v in mask.shape),
            "mask_sha256": mask_hash(mask), "n_fluid": int((~mask).sum())}
    return mask, meta


#: Bridge-coupon geometry, frozen and NOT tuned against any assembled-fixture output. ``divider``
#: is the full transverse traverse (port A + duct + port B); ``plenum`` is the depth of the
#: reservoir on each side; ``span`` is the walled extent perpendicular to both.
BRIDGE_COUPON = {"plenum": 6, "span": 13, "divider": 6}


def build_bridge_coupon(S: int, w: int, kz: int):
    """AXIS-ROTATED bridge coupon: the whole three-layer divider traverse (port A -> duct ->
    port B) rebuilt so the transverse bridge axis lies along the solver's +x lattice direction.
    The existing x-directed kernel therefore measures the transverse conductance directly, with
    no invented anisotropy correction. Plena of the transition-band slot height sit on both
    sides and join through the x wrap, exactly as the fixture's common node does.

    Only the CONNECTED bridge has a coupon: the blocked bridge conducts nothing by construction.
    """
    w, kz = _validate_bridge({"w": w, "kz": kz})
    p, span, div = BRIDGE_COUPON["plenum"], BRIDGE_COUPON["span"], BRIDGE_COUPON["divider"]
    nx_b = 2 * p + div                       # flow axis == the fixture's transverse (y) axis
    ny_b = span                              # the fixture's x axis, walled
    nz_b = BASE["nz"]
    solid_b = np.ones((nx_b, ny_b, nz_b), dtype=bool)
    # plena: full transition-band slot height, walled in the span direction
    solid_b[:p, 1:span - 1, BASE["z_lo"]:BASE["z_lo"] + BASE["h_low"]] = False
    solid_b[p + div:, 1:span - 1, BASE["z_lo"]:BASE["z_lo"] + BASE["h_low"]] = False
    # the bridge traverse itself: footprint w centred in the span, height kz
    c = span // 2
    lo, hi = c - (w - 1) // 2, c + (w - 1) // 2
    solid_b[p:p + div, lo:hi + 1, BASE["z_lo"]:BASE["z_lo"] + kz] = False
    mask = scale(solid_b, S)
    meta = {"S": S, "kind": "bridge_coupon", "w": w, "kz": kz,
            "length_vox": div * S, "shape": tuple(int(v) for v in mask.shape),
            "mask_sha256": mask_hash(mask), "n_fluid": int((~mask).sum()),
            "geometry": dict(BRIDGE_COUPON)}
    return mask, meta


# ==========================================================================================
# 3. FROZEN SOLVER CONFIGURATION AND THE DIMENSIONLESS SIMILARITY LAW
# ==========================================================================================
# 001 ran S = 2 and S = 3 at IDENTICAL lattice g and nu with every length proportional to S. For
# a Stokes slot, u ~ g L^2 / nu and Re ~ g L^3 / nu^2, so that comparison spanned a factor
# (3/2)^3 = 3.375 in Reynolds number: two different dimensionless problems (001 erratum E5).
#
# 001b holds the design Reynolds number invariant by scaling the forcing with resolution:
#
#       g(S) = G_REF * (S_REF / S)^3
#
# At S_REF = 2 the central forcing is 2.0e-6, a TENFOLD reduction from 001's 2.0e-5 — inside the
# x8-x10 reduction the 001 decision recorded as design guidance. At S = 3 the reduction is
# x33.75. The reduction is a PREDICTION to be tested by this protocol's own forcing ladder; it
# is never assumed, and it may not be used to rescue the 001 execution.

TAU_PLUS = 2.0
TAU_CROSS_CHECK = 1.2
NU = (TAU_PLUS - 0.5) / 3.0                  # = 0.5 exactly, matching lb_reference.solve

#: The scientific status of the two ``tau_plus = 1.2`` rows, RESOLVED (erratum PE-65).
#:
#: The controlling historical authority is RP-D-LC-001 PROTOCOL.md §5 and
#: ``rp_d_lc_virtual_fixture.TAU_CROSS_CHECK``. It freezes an ANALYTIC PLANE-CHANNEL observation
#: (permeability error +0.05203 % at tau_plus = 1.2, 2.0 and 3.0, identical to five significant
#: figures) and the intent to re-run one assembled fixture case at 1.2. It freezes NO compared
#: quantity for the assembled fixture, NO tolerance, and NO treatment of the viscosity change.
#: That omission is material: nu = (tau_plus - 0.5)/3, so 1.2 -> nu = 0.2333 against 2.0 -> 0.5,
#: a pressure-normalised conductance scales as 1/nu, and 001 handled this for the channel by
#: scaling g with nu. The 001b rows run at the SAME central g as their tau_plus = 2.0
#: counterparts, so the two are not the same dimensionless problem and a raw comparison of C, R
#: or s between them would compare a viscosity ratio, not a discretisation independence.
#:
#: Since no exact pre-existing rule exists, C5 does NOT invent one.
TAU_CROSS_CHECK_DISPOSITION = {
    "status": "DIAGNOSTIC_ONLY",
    "authority": ("docs/analysis/rp_d_lc_001/PROTOCOL.md §5; "
                  "puckworks/analysis/rp_d_lc_virtual_fixture.py TAU_CROSS_CHECK"),
    "exact_frozen_rule_exists": False,
    "frozen_by_the_authority": ("an analytic plane-channel observation and the intent to re-run "
                                "one assembled fixture case at tau_plus = 1.2"),
    "not_frozen_by_the_authority": ["compared quantity for the assembled fixture",
                                    "tolerance", "viscosity / dynamic-similarity accounting"],
    "viscosity_note": ("nu = (tau_plus - 0.5)/3, so tau_plus = 1.2 gives nu = 0.2333 against 0.5 "
                       "at tau_plus = 2.0; the 001b rows keep the same central g, so the two are "
                       "not the same dimensionless problem"),
    "may_show": ("that the assembled 3D fixture solves, converges and stays in the low-Mach "
                 "regime at a second relaxation rate, with no gross qualitative change"),
    "may_not_show": ("agreement, viscosity independence, or a bound of any kind"),
    "may_alter": [],
    "may_not_alter": ["admission", "uncertainty", "classification", "selection", "any gate "
                      "verdict", "any disposition"],
    "tolerance": None,
    "tolerance_policy": "NOT_INVENTED_HERE_A_LATER_CORRECTION_MAY_FREEZE_ONE_BEFORE_ANY_OUTPUT",
    "retained_in_matrix": True,
    "erratum": "PE-65",
}
S_REF = 2
#: The reference forcing as an EXACT rational (erratum PE-12). Fraction(2.0e-6) would have been
#: the exact rational of an already-rounded binary float, which is not the same number and is not
#: the frozen design value. ``G_REF`` is derived from it, never the source of truth.
G_REF_EXACT = Fraction(1, 500_000)
G_REF = float(G_REF_EXACT)
FORCING_FACTORS = (Fraction(1, 2), Fraction(1), Fraction(2))
FORCING_LEVELS = ("low", "central", "high")

RTOL = 1.0e-7
CHECK = 200
MIN_STEPS = 2000
MAX_STEPS = 60000
CONVERGENCE_AUDIT_FACTOR = 1.5

#: Characteristic length for the design Reynolds number: the LOW slot height, the smallest
#: flow-carrying feature common to every configuration, in lattice voxels.
SIMILARITY_LENGTH_BASE = BASE["h_low"]


#: Run modes and statuses. ``converged = steps < MAX_STEPS`` is NOT used for audits (PE-16).
RUN_MODES = ("NORMAL", "FIXED_STEP_REEXECUTION_1P5X")
RUN_STATUSES = ("NORMAL_CONVERGED", "NORMAL_UNCONVERGED",
                "FIXED_STEP_AUDIT_COMPLETED", "FIXED_STEP_AUDIT_INCOMPLETE")

#: Frozen audit maximum, large enough for the 1.5x rule against the normal maximum and aligned
#: to CHECK. An audit pins min_steps = max_steps = target, so this is a guard, not a stopping rule.
MAX_STEPS_AUDIT = CHECK * -(-int(CONVERGENCE_AUDIT_FACTOR * MAX_STEPS) // CHECK)


def fixed_step_audit_target(base_completed_steps: int) -> int:
    """The exact step count a fixed-step re-execution must complete (erratum PE-16).

        target = CHECK * ceil(CONVERGENCE_AUDIT_FACTOR * base_steps / CHECK)

    The superseded audit raised ``max_steps`` while leaving ``min_steps = 2000``, so the solver's
    own convergence test could stop it at the base step count and the audit could be a NO-OP. An
    audit that can return the base result is not evidence.
    """
    b = int(base_completed_steps)
    if b <= 0:
        raise ValueError("base_completed_steps must be positive, got %r" % (base_completed_steps,))
    target = CHECK * -(-int(math.ceil(CONVERGENCE_AUDIT_FACTOR * b)) // CHECK)
    if target <= b:                                          # pragma: no cover - factor > 1
        target = CHECK * ((b // CHECK) + 1)
    if target % CHECK:                                       # pragma: no cover - by construction
        raise ValueError("audit target %r is not aligned to CHECK" % (target,))
    if target > MAX_STEPS_AUDIT:
        raise ValueError("audit target %d exceeds the frozen audit maximum %d"
                         % (target, MAX_STEPS_AUDIT))
    return target


def fixed_step_audit_plan(base_steps, base_status):
    """The frozen solver configuration for a fixed-step re-execution, with its preconditions."""
    if base_status != "NORMAL_CONVERGED":
        raise ValueError(
            "a fixed-step audit requires a base case that actually converged before its normal "
            "maximum; got %r. An audit may never rescue an UNCONVERGED case (erratum PE-16)."
            % (base_status,))
    target = fixed_step_audit_target(base_steps)
    return {
        "run_mode": "FIXED_STEP_REEXECUTION_1P5X",
        "base_completed_steps": int(base_steps),
        "base_status": base_status,
        "target_steps": target,
        "min_steps": target, "max_steps": target,       # pinned: the solver cannot stop early
        "check": CHECK,
        "aligned_to_check": True,
        "exceeds_base": target > int(base_steps),
        "naming_note": ("named FIXED_STEP_REEXECUTION_1P5X, not 'continuation': the solver does "
                        "not resume from saved state, it re-runs for a pinned longer step count"),
    }


def run_status(run_mode, completed_steps, target_steps=None):
    """The four distinct statuses (erratum PE-16). Normal convergence and audit completion are
    different facts and are never conflated."""
    if run_mode not in RUN_MODES:
        raise ValueError("unknown run mode %r" % (run_mode,))
    n = int(completed_steps)
    if run_mode == "NORMAL":
        return "NORMAL_CONVERGED" if n < MAX_STEPS else "NORMAL_UNCONVERGED"
    if target_steps is None:
        raise ValueError("a fixed-step audit status needs its target step count")
    return ("FIXED_STEP_AUDIT_COMPLETED" if n == int(target_steps)
            else "FIXED_STEP_AUDIT_INCOMPLETE")


def forcing_exact(S: int, level: str = "central") -> Fraction:
    """The forcing as an EXACT rational, derived from G_REF_EXACT (erratum PE-21).

    This — not the runtime float — is the scientific identity of a forcing level. The float is
    derived FROM it, and the rational is never reconstructed from a binary float.
    """
    if not isinstance(S, int) or isinstance(S, bool) or S < 1:
        raise ValueError("S must be a positive int, got %r" % (S,))
    if level not in FORCING_LEVELS:
        raise ValueError("unknown forcing level %r; expected one of %r" % (level, FORCING_LEVELS))
    factor = dict(zip(FORCING_LEVELS, FORCING_FACTORS))[level]
    return G_REF_EXACT * Fraction(S_REF ** 3, S ** 3) * factor


def forcing_exact_dict(S: int, level: str = "central"):
    """The canonical serialisable form of the exact rational, carried by every forcing-bearing
    matrix row and case record."""
    f = forcing_exact(S, level)
    return {"numerator": int(f.numerator), "denominator": int(f.denominator)}


def forcing_from_exact(exact) -> float:
    """The runtime float, derived from the exact rational and never independently written."""
    f = Fraction(int(exact["numerator"]), int(exact["denominator"]))
    return float(f)


def row_forcing(row) -> float:
    """The runtime forcing of a row, ALWAYS derived from its exact rational.

    A bare float is not stored in any hashed artifact: the canonical writer rounds to
    ``_RECORD_DP = 12`` decimals, and `5.925925925925926e-7` rounds to `0.0` there — which is
    precisely why twelve-decimal JSON rounding may not be the scientific identity of a forcing
    level (erratum PE-21). Rows and records carry ``forcing_exact`` plus a lossless
    ``forcing_repr`` string; this helper is the only way to obtain the float.
    """
    return forcing_from_exact(row["forcing_exact"])


def forcing_central(S: int) -> float:
    """The frozen central body force at resolution ``S``. Constructed as an exact rational so
    the two resolutions carry no rounded duplicate literals."""
    if not isinstance(S, int) or isinstance(S, bool) or S < 1:
        raise ValueError("S must be a positive int, got %r" % (S,))
    return float(G_REF_EXACT * Fraction(S_REF ** 3, S ** 3))


def forcing_ladder(S: int):
    """The componentwise x0.5 / x1 / x2 forcing ladder at resolution ``S``, exact by rational
    construction around that resolution's own central forcing."""
    g0 = G_REF_EXACT * Fraction(S_REF ** 3, S ** 3)          # exact, never via a binary float
    return {name: float(g0 * f) for name, f in zip(FORCING_LEVELS, FORCING_FACTORS)}


def design_reynolds(S: int, g=None) -> float:
    """The dimensionless group held invariant across resolutions:

        Re_design = g * L^3 / nu^2,     L = SIMILARITY_LENGTH_BASE * S   (lattice voxels)

    It is computed from FROZEN DESIGN INPUTS ONLY — no solver output enters it — so it can be
    and is asserted equal at S = 2 and S = 3 before any run exists.
    """
    g = forcing_central(S) if g is None else float(g)
    L = SIMILARITY_LENGTH_BASE * S
    return g * L ** 3 / NU ** 2


def design_mach_scale(S: int, g=None) -> float:
    """A PRE-EXECUTION PLANNING ESTIMATE of the lattice-velocity scale, u ~ g L^2 / nu, times
    sqrt(3). It is deliberately NOT held invariant (it falls as 1/S under the frozen law); low
    Mach is a numerical admissibility condition, not a similarity parameter, and 001 erratum E2
    records that the two are related but not interchangeable.

    **It is not the low-Mach control.** That is ``mach_record``, which measures the actual maximum
    of the FULL velocity vector over fluid nodes (erratum PE-4). This function estimates a mean
    scale a priori; the control needs the measured maximum.
    """
    g = forcing_central(S) if g is None else float(g)
    L = SIMILARITY_LENGTH_BASE * S
    return float(np.sqrt(3.0)) * g * L ** 2 / NU


# ---- frozen tolerances (software/discretisation, NOT experimental uncertainties) ----------
TOL_MASS_REL = 1.0e-3          # mass-flux (rho*u) plane-to-plane spread — ADJUDICATIVE
TOL_VOLUME_FLUX_REL = 1.0e-3   # volume-flux (u) plane-to-plane spread — DIAGNOSTIC continuity
TOL_LINEARITY_REL = 1.0e-4     # componentwise forcing invariance of every truth component
TOL_MACH = 0.03
TOL_CONVERGENCE_REL = 1.0e-4
TOL_PLANE_REL = 5.0e-3
TOL_SWAP_R_REL = 5.0e-3
TOL_SWAP_XI_REL = 5.0e-2
TOL_RETURN_PATH_R_REL = 1.0e-3      # Arm J, carried over unchanged from 001 erratum E1
TOL_RETURN_PATH_S_ABS = 5.0e-4
TOL_NODE_OFFSET_R_REL = 5.0e-3
_RECORD_DP = 12


# ---- resolution consistency (NOT an asymptotic convergence-order estimate) -----------------
# Two resolutions can support a frozen CONSISTENCY test and nothing stronger. Its tolerance is
# derived BEFORE any 001b output from the discretisation law Arm A of the 001 tranche measured
# on the canonical plane channel — error(%) = 50/h^2, i.e. a fractional element error
#
#       delta(h) = 0.5 / h^2
#
# for a slot of height h lattice voxels. Between S_COARSE and S_FINE each governing feature's
# element error changes by |delta(h_coarse) - delta(h_fine)|; the tolerance is KAPPA_RES times
# the sum over the features that govern the quantity. Nothing about 001b agreement enters it.
KAPPA_RES = 2.0
RESOLUTION_CONSISTENCY_PROVENANCE = (
    "docs/analysis/rp_d_lc_001/VIRTUAL_FIXTURE_SPEC.md §5 — measured plane-channel law "
    "error(%) = 50/h^2 over h = 3..31 lattice units (Arm A of the closed RP-D-LC-001 tranche)"
)

#: An explicit extra copy of the WORST single feature's error movement, standing for junction and
#: end effects the single-slot channel law does not describe. Declared as a factor rather than
#: hidden inside a fitted constant (erratum PE-8).
JUNCTION_ALLOWANCE = 1.0

#: Two feature families (erratum PE-8). The superseded model governed every bridge quantity by
#: ``bridge_kz`` ALONE — but the footprint width ``w`` is a resolved feature in its own right and
#: is SMALLER than ``kz`` over part of the family (w = 3 against kz = 4), so the smallest feature
#: governing the bridge conductance could be omitted entirely. Port depth and duct traverse were
#: absent, and ``R``/``s`` did not distinguish a lane-only fixture from a bridge-carrying one.
#: FIVE governing-feature families (erratum PE-33). The superseded model had two, and classified
#: the CANDIDATE blocked fixture as lane-only — but that fixture carries the common-mode blind
#: ports, which are a resolved feature of the very geometry whose contrast is being measured.
FEATURE_FAMILIES = {
    "reference_blocked_lane_only": ("h_low", "h_high"),
    "candidate_blocked_common_mode_ports": ("h_low", "h_high", "bridge_w", "bridge_kz",
                                            "port_depth", "duct_traverse"),
    "open_bridge_carrying": ("h_low", "h_high", "bridge_w", "bridge_kz", "port_depth",
                             "duct_traverse"),
    "axial_coupon": ("h_low", "h_high"),
    "bridge_coupon": ("bridge_w", "bridge_kz", "duct_traverse"),
    # erratum PE-67: actual Xi = G_bridge*(1/A1 + 1/A2) is derived from BOTH the bridge coupon
    # (G_bridge) and the candidate blocked mirror (A1, A2), so its envelope is the union of the
    # two governing families. The union is conservative and is not a new feature model.
    "actual_xi_derived": ("h_low", "h_high", "bridge_w", "bridge_kz", "port_depth",
                          "duct_traverse"),
}
LANE_ONLY_FEATURES = FEATURE_FAMILIES["reference_blocked_lane_only"]
BRIDGE_CARRYING_FEATURES = FEATURE_FAMILIES["open_bridge_carrying"]

#: Which family governs which decision-bearing quantity. A candidate-blocked quantity uses the
#: common-mode-ports family; only the bridge-free REFERENCE fixture is lane-only.
RESOLUTION_GOVERNING_FAMILY = {
    "R_reference_blocked": "reference_blocked_lane_only",
    "s_reference_blocked": "reference_blocked_lane_only",
    "C_reference_blocked": "reference_blocked_lane_only",
    "Q_reference_blocked": "reference_blocked_lane_only",
    "Q_mass_reference_blocked": "reference_blocked_lane_only",
    "dP_reference_blocked": "reference_blocked_lane_only",
    "R_blocked": "candidate_blocked_common_mode_ports",
    "s_blocked": "candidate_blocked_common_mode_ports",
    "C_blocked": "candidate_blocked_common_mode_ports",
    "c_field": "candidate_blocked_common_mode_ports",
    "A_field": "candidate_blocked_common_mode_ports",
    "A1": "candidate_blocked_common_mode_ports",
    "A2": "candidate_blocked_common_mode_ports",
    "A_series_inverse": "candidate_blocked_common_mode_ports",
    "R_open": "open_bridge_carrying",
    "R_identical": "open_bridge_carrying",
    "s_open": "open_bridge_carrying",
    "C_open": "open_bridge_carrying",
    "G_lat_field": "open_bridge_carrying",
    "Xi_field": "open_bridge_carrying",
    "Xi_hat": "open_bridge_carrying",
    "Xi_coupon": "bridge_coupon",
    "G_bridge_coupon": "bridge_coupon",
    "Xi_actual": "actual_xi_derived",
    "G_axial_coupon": "axial_coupon",
    "C_axial_coupon": "axial_coupon",
    "Q_axial_coupon": "axial_coupon",
    "dP_axial_coupon": "axial_coupon",
}
RESOLUTION_GOVERNING_FEATURES = {q: FEATURE_FAMILIES[f]
                                 for q, f in RESOLUTION_GOVERNING_FAMILY.items()}
#: Quantities whose tolerance depends on the candidate geometry and therefore require a bridge.
BRIDGE_DEPENDENT_QUANTITIES = tuple(
    q for q, f in RESOLUTION_GOVERNING_FAMILY.items()
    if any(x.startswith("bridge_") for x in FEATURE_FAMILIES[f]))

# ---- the frozen resolution COMPARISON COORDINATE (erratum PE-66) ----------------------------
# A two-resolution consistency test needs a coordinate in which the two resolutions are
# comparable at all. C4 compared raw lattice values, which is correct only for a dimensionless
# quantity: an extensive lattice quantity moves with S by a factor fixed by the frozen forcing law
# and exact geometric similarity, and that movement is not a discretisation error.
#
# The exponents are DERIVED, not chosen. With every base voxel replicated into an S^3 block and
# the frozen law g(S) = G_REF (S_REF/S)^3:
#
#   lattice velocity        u  ~ g L^2 / nu,  L ~ S            ->  u  ~ g S^2
#   plane fluid-node count                    ~ S^2
#   plane volume flux       Q  = sum(u_x)                      ->  Q  ~ g S^4        ( ~ S^1 at g(S) )
#   node-to-node drop       dP ~ g * (lattice length)          ->  dP ~ g S          ( ~ S^-2 )
#   conductance             C  = Q / dP                        ->  C  ~ S^3
#   lane conductance A1, A2, coupon G_bridge, G_axial          ->      S^3
#   1/A1 + 1/A2                                                ->      S^-3
#   Xi = G_bridge * (1/A1 + 1/A2), R = C_open/C_blocked, s, c   ->      S^0
#
# The comparison coordinate is ``value / S**exponent``. For every dimensionless quantity the
# exponent is 0 and the coordinate is the value itself, so no previously frozen dimensionless
# comparison changes. Nothing here is fitted and nothing is tunable: each exponent follows from
# the already-frozen forcing law and the already-frozen geometric similarity.
RESOLUTION_SCALING_PROVENANCE = (
    "derived from the frozen forcing law g(S) = G_REF (S_REF/S)^3 and exact geometric similarity "
    "(every base voxel replicated into an S^3 block); not fitted, not tunable, and 0 for every "
    "dimensionless quantity so no previously frozen comparison is altered"
)
RESOLUTION_SCALING_EXPONENT = {
    # dimensionless — compared directly, exactly as before
    "R_reference_blocked": 0, "s_reference_blocked": 0,
    "R_blocked": 0, "s_blocked": 0, "c_field": 0,
    "R_open": 0, "s_open": 0, "R_identical": 0,
    "Xi_field": 0, "Xi_hat": 0, "Xi_coupon": 0, "Xi_actual": 0,
    # conductances
    "C_reference_blocked": 3, "C_blocked": 3, "C_open": 3,
    "A_field": 3, "A1": 3, "A2": 3, "G_lat_field": 3,
    "G_bridge_coupon": 3, "G_axial_coupon": 3, "C_axial_coupon": 3,
    # the exact aggregate that multiplies G_bridge to form Xi
    "A_series_inverse": -3,
    # volume and mass fluxes
    "Q_reference_blocked": 1, "Q_mass_reference_blocked": 1, "Q_axial_coupon": 1,
    # node-to-node pressure drops
    "dP_reference_blocked": -2, "dP_axial_coupon": -2,
}


def resolution_comparison_coordinate(quantity, value, S):
    """``value / S**n`` — the frozen coordinate in which S_COARSE and S_FINE are comparable."""
    if quantity not in RESOLUTION_SCALING_EXPONENT:
        raise KeyError("no frozen resolution comparison coordinate for %r" % (quantity,))
    n = RESOLUTION_SCALING_EXPONENT[quantity]
    return _finite(value, "%s at S=%r" % (quantity, S)) / (float(S) ** n)


def element_error(h_vox: float) -> float:
    """Fractional element-level discretisation error of a slot of height ``h_vox`` lattice
    voxels, from the measured plane-channel law error(%) = 50/h^2."""
    if h_vox <= 0:
        raise ValueError("h_vox must be positive, got %r" % (h_vox,))
    return 0.5 / float(h_vox) ** 2


def _feature_base_size(name, bridge):
    if name == "h_low":
        return BASE["h_low"]
    if name == "h_high":
        return BASE["h_high"]
    if name == "port_depth":
        return BASE["portA_hi"] - BASE["portA_lo"] + 1
    if name == "duct_traverse":
        return BASE["portB_hi"] - BASE["portA_lo"] + 1
    if bridge is None:
        raise ValueError("feature %r needs a bridge footprint" % (name,))
    if name == "bridge_w":
        return int(bridge["w"])
    if name == "bridge_kz":
        return int(bridge["kz"])
    raise KeyError(name)                                          # pragma: no cover - frozen set


def resolution_consistency_tolerance(quantity: str, bridge=None) -> float:
    """The frozen relative tolerance for the S_COARSE / S_FINE consistency test of ``quantity``.

    A CONSERVATIVE FEATURE ENVELOPE: the sum over every critical discrete feature that can govern
    the error, plus one extra copy of the worst of them as an explicit junction/end allowance.

        tol = KAPPA_RES * ( sum_f dd(f) + JUNCTION_ALLOWANCE * max_f dd(f) )
        dd(f) = |delta(f*S_COARSE) - delta(f*S_FINE)|,   delta(h) = 0.5/h^2

    Derived ex ante from the measured discretisation law and the frozen geometry only — never
    from observed agreement between the 001b results, which do not exist. Two resolutions support
    a CONSISTENCY test and nothing stronger; this is not a convergence-order estimate.
    """
    feats = RESOLUTION_GOVERNING_FEATURES[quantity]
    dd = []
    for f in feats:
        b = _feature_base_size(f, bridge)
        dd.append(abs(element_error(b * S_COARSE) - element_error(b * S_FINE)))
    return KAPPA_RES * (sum(dd) + JUNCTION_ALLOWANCE * max(dd))


def resolution_consistency_table(bridge):
    """Every frozen tolerance for one candidate, for the record and for review."""
    out = {}
    for q in sorted(RESOLUTION_GOVERNING_FAMILY):
        needs_bridge = q in BRIDGE_DEPENDENT_QUANTITIES
        out[q] = {
            "features": list(RESOLUTION_GOVERNING_FEATURES[q]),
            "family": RESOLUTION_GOVERNING_FAMILY[q],
            "tolerance": resolution_consistency_tolerance(q, bridge if needs_bridge else None),
        }
    return out


# ==========================================================================================
# 4. THE OBSERVABLE / CONSERVATION CONTRACT
# ==========================================================================================
# The INVERSE observable and the CONSERVATION diagnostic are different quantities and are kept
# explicitly separate. 001 conflated them: its "mass conservation" control measured sum(u_x),
# a VOLUME-flux proxy, and the rho fields needed to form sum(rho*u_x) were never retained, so
# actual mass conservation could not be evaluated at all (errata E4 / E4b).
#
#   * the WP6 / Route-A inverse consumes PRESSURE-NORMALISED VOLUME FLUX — unchanged:
#         R = (Q/dP)_open / (Q0/dP0)_blocked          s = q1 / (q1 + q2)
#     with Q, q1, q2 formed from sum(u_x). This contract is preserved; it is NOT replaced by
#     mass flux, and no new pressure component or Route-B formulation is introduced.
#
#   * CONSERVATION is evaluated on the DENSITY-WEIGHTED flux sum(rho*u_x), which is what a
#     weakly compressible solver actually conserves.
#
# sum(u) is never called a mass flux, and successful mass conservation is never inferred from
# cancellation in a ratio.

#: Frozen compact-record field names for an axial measurement plane. Every reported normalised
#: observable must be reproducible from these alone.
AXIAL_PLANE_FIELDS = (
    "plane_id",        # frozen name of the plane
    "orientation",     # 'x' — the plane's normal
    "index",           # lattice index along the normal
    "n_fluid",         # fluid-node count on the plane (its area in lattice cells)
    "sum_ux",          # SUM of u_x over fluid nodes — VOLUME flux, lattice units, +x positive
    "sum_rho_ux",      # SUM of rho*u_x over the SAME nodes — MASS flux, lattice units
    "rho_mean", "rho_sd",
    "p_mean", "p_sd",  # p = rho/3 - g*x, fluid-area averaged; sd reports nonuniformity
)

#: Frozen compact-record field names for a transverse (bridge-control) plane.
TRANSVERSE_PLANE_FIELDS = (
    "plane_id",
    "orientation",     # 'y'
    "index",
    "n_fluid",
    "sum_uy",          # SUM of u_y over the footprint — VOLUME flux, +y positive = lane1 -> lane2
    "sum_rho_uy",      # SUM of rho*u_y over the SAME nodes — MASS flux
    "footprint_x", "footprint_z",
    "sign_convention",
)

SIGN_CONVENTION_AXIAL = "positive_is_plus_x_downstream"
SIGN_CONVENTION_TRANSVERSE = "positive_is_lane1_to_lane2_along_plus_y"

#: How each retained quantity is used. Adjudicative quantities can fail an execution; diagnostic
#: ones are reported and never converted into a verdict.
QUANTITY_ROLES = {
    "sum_ux": "diagnostic_and_inverse_input",
    "sum_rho_ux": "adjudicative_conservation",
    "sum_uy": "diagnostic_and_truth_input",
    "sum_rho_uy": "adjudicative_conservation_state_aware",
    "p_mean": "inverse_input_and_truth_input",
    "p_sd": "diagnostic_nonuniformity",
    "rho_mean": "diagnostic",
    "rho_sd": "diagnostic",
    "max_mach": "adjudicative_low_mach",
    "max_speed_fluid": "adjudicative_low_mach",
    "design_mach_scale": "planning_estimate_not_a_control",
}


def axial_plane_record(plane_id, x, ux, rho, mask, g, y_slice=None):
    """The frozen compact record for one axial plane.

    ``ux`` is the solver's returned ux array, which already carries the +g/2 force half-shift;
    solid nodes are excluded here because the kernel leaves g/2 there rather than 0. No
    normalisation is applied: raw sums plus ``n_fluid`` are retained so any area-averaged or
    normalised quantity downstream is exactly reproducible.
    """
    fl = ~mask[x]
    if y_slice is not None:
        fl = fl.copy()
        fl[:y_slice[0]] = False
        fl[y_slice[1]:] = False
    u = ux[x][fl]
    r = rho[x][fl]
    p = r / 3.0 - g * x
    return {
        "plane_id": plane_id, "orientation": "x", "index": int(x), "n_fluid": int(fl.sum()),
        "sum_ux": float(u.sum()), "sum_rho_ux": float((r * u).sum()),
        "rho_mean": float(r.mean()) if r.size else float("nan"),
        "rho_sd": float(r.std()) if r.size else float("nan"),
        "p_mean": float(p.mean()) if p.size else float("nan"),
        "p_sd": float(p.std()) if p.size else float("nan"),
    }


def transverse_plane_record(plane_id, y, uy, rho, mask, footprint_x, footprint_z):
    """The frozen compact record for one transverse bridge-control plane."""
    xs, xe = footprint_x
    zs, ze = footprint_z
    sub_mask = mask[xs:xe, y, zs:ze]
    fl = ~sub_mask
    u = uy[xs:xe, y, zs:ze][fl]
    r = rho[xs:xe, y, zs:ze][fl]
    return {
        "plane_id": plane_id, "orientation": "y", "index": int(y), "n_fluid": int(fl.sum()),
        "sum_uy": float(u.sum()), "sum_rho_uy": float((r * u).sum()),
        "footprint_x": (int(xs), int(xe)), "footprint_z": (int(zs), int(ze)),
        "sign_convention": SIGN_CONVENTION_TRANSVERSE,
    }


def _finite(x, what):
    v = float(x)
    if not np.isfinite(v):
        raise NonFiniteValue("%s is not finite: %r" % (what, v))
    return v


def _spread(values):
    """Relative min–max spread about the mean. Only ever applied where the mean is guaranteed
    nonzero by construction — see ``transverse_conservation`` for why a mean-normalised statistic
    must never be the sole metric for the transverse control (erratum PE-2)."""
    v = [float(x) for x in values]
    if not v:
        raise ValueError("_spread requires at least one value")
    m = sum(v) / len(v)
    if m == 0.0:
        raise ZeroDivisionError("_spread called on a set whose mean is exactly zero; a zero-safe "
                                "absolute metric is required here (erratum PE-2)")
    return (max(v) - min(v)) / abs(m)


def assert_conservation_records(records):
    """Admit ONLY the nine frozen adjudicative axial conservation records (erratum PE-1).

    Raises unless there are exactly nine, their plane IDs are the frozen nine in the frozen
    order, and their intended coordinates are nine distinct values. Named measurement records —
    ``x_node_in``/``x_node_out`` (plenum planes kept for PRESSURE) and ``x_meas_*`` /lane records
    (kept for the observables) — can therefore never be double-weighted into a conservation
    verdict, whatever a caller passes.
    """
    recs = list(records)
    if len(recs) != N_CONSERVATION_PLANES:
        raise ValueError("mass conservation requires exactly %d adjudicative records, got %d"
                         % (N_CONSERVATION_PLANES, len(recs)))
    ids = tuple(r["plane_id"] for r in recs)
    if ids != CONSERVATION_PLANE_IDS:
        raise ValueError("mass conservation admits only %r in that frozen order; got %r"
                         % (list(CONSERVATION_PLANE_IDS), list(ids)))
    if len(set(ids)) != N_CONSERVATION_PLANES:               # pragma: no cover - implied above
        raise ValueError("duplicate conservation plane IDs: %r" % (list(ids),))
    idx = tuple(int(r["index"]) for r in recs)
    if len(set(idx)) != N_CONSERVATION_PLANES:
        raise ValueError("conservation planes must sit at %d distinct coordinates, got %r"
                         % (N_CONSERVATION_PLANES, list(idx)))
    if any(r["orientation"] != "x" for r in recs):
        raise ValueError("conservation records must all be axial ('x') planes")
    return recs


def conservation_residuals(conservation_records, named_plane_records=()):
    """Axial plane-to-plane residuals from the NINE adjudicative records only.

    ``mass_flux_residual`` (from ``sum_rho_ux``) is ADJUDICATIVE against ``TOL_MASS_REL``.
    ``volume_flux_residual`` (from ``sum_ux``) is the 001-compatible DIAGNOSTIC proxy and can
    never on its own decide an execution — nor can a small mass residual be inferred from it.

    ``named_plane_records`` are REPORTED, never admitted to either statistic.
    """
    recs = assert_conservation_records(conservation_records)
    out = {
        "n_adjudicative_planes": len(recs),
        "adjudicative_plane_ids": list(CONSERVATION_PLANE_IDS),
        "adjudicative_plane_indices": [int(r["index"]) for r in recs],
        "mass_flux_residual": _finite(_spread(r["sum_rho_ux"] for r in recs),
                                      "mass_flux_residual"),
        "volume_flux_residual": _finite(_spread(r["sum_ux"] for r in recs),
                                        "volume_flux_residual"),
        "tol_mass_rel": TOL_MASS_REL,
        "tol_volume_flux_rel": TOL_VOLUME_FLUX_REL,
        "mass_flux_residual_role": "adjudicative",
        "volume_flux_residual_role": "diagnostic",
        "named_plane_records_reported": [r["plane_id"] for r in named_plane_records],
        "named_plane_records_admitted_to_verdict": False,
    }
    out["mass_conservation_pass"] = bool(out["mass_flux_residual"] <= TOL_MASS_REL)
    out["volume_flux_uniformity_pass"] = bool(out["volume_flux_residual"] <= TOL_VOLUME_FLUX_REL)
    return out


# ---- transverse (bridge) conservation: state-aware and zero-safe (erratum PE-2) -------------
# The DEFINING negative-control case is the identical-path open fixture at exactly zero lateral
# driver, where the correct physical answer is zero net transverse mass flux. A statistic that
# divides by its own mean is undefined there and ill-conditioned near it, so a mean-normalised
# spread must never be the sole metric — it could report a spurious FAILURE precisely because the
# physics was right. Four states are frozen, each with its own applicability and metric.

TRANSVERSE_STATUS = (
    "NOT_APPLICABLE_NO_BRIDGE",
    "NOT_APPLICABLE_BLOCKED_CONNECTION",
    "EVALUATED_ZERO_SAFE_ABSOLUTE",
    "EVALUATED_HYBRID",
)

#: Absolute transverse leakage/imbalance ceiling, normalised by the case's own AXIAL mass flux.
#: This is the programme's established 0.1 % observable nuisance scale applied to a normalised
#: observable — the same number as ARTIFACT_BUDGET_R_ABS and TOL_RETURN_PATH_R_REL, not a new one.
#: It is a CEILING: at the zero-driver control the expected value is orders of magnitude smaller.
TOL_BRIDGE_LEAKAGE_REL = 1.0e-3

#: The relative four-plane statistic is admitted ONLY when the mean lateral mass flux exceeds the
#: absolute leakage ceiling by this factor — i.e. only when the signal is an order of magnitude
#: above the noise the absolute gate already tolerates. Derived before output; not tunable.
LATERAL_FLUX_FLOOR_FACTOR = 10.0

#: The transverse control planes that must carry the THROUGH-bridge flux when the connection is
#: open, and must be structurally solid when it is blocked.
DUCT_CONTROL_PLANE_IDS = ("y_duct_a", "y_duct_b")
PORT_CONTROL_PLANE_IDS = ("y_portA_in", "y_portB_out")


def transverse_conservation(state, transverse_records, axial_mass_scale,
                            lateral_driver_is_zero=False):
    """State-aware, zero-safe transverse conservation.

    ``state``               one of FIXTURE_STATES.
    ``transverse_records``  the four frozen transverse plane records (may be empty when the
                            fixture carries no bridge).
    ``axial_mass_scale``    a frozen, NONZERO axial mass-flux scale — the case's own
                            ``sum_rho_ux`` at the primary outlet plane. Never mean ``q_lat``.
    ``lateral_driver_is_zero``  True for the identical-path negative control, where the
                            cross-product gap X is zero EXACTLY and no lateral pressure
                            difference exists at any bridge conductance.

    Every adjudicative numeric value is checked finite.
    """
    if state not in FIXTURE_STATES:
        raise ValueError("unknown fixture state %r" % (state,))
    out = {
        "state": state,
        "tol_leakage_rel": TOL_BRIDGE_LEAKAGE_REL,
        "tol_relative": TOL_MASS_REL,
        "sign_convention": SIGN_CONVENTION_TRANSVERSE,
        "normalisation_scale": None,
        "normalisation_scale_source": "sum_rho_ux at x_meas_a (axial mass flux)",
        "plane_sums_mass": None,
        "plane_sums_volume": None,
        "signed_balance": None,
        "absolute_imbalance": None,
        "absolute_imbalance_normalised": None,
        "plane_range_mass": None,
        "plane_range_mass_rel": None,
        "max_abs_lateral_mass_flux": None,
        "max_abs_lateral_mass_flux_rel": None,
        "mean_lateral_mass_flux": None,
        "abs_mean_lateral_mass_flux_rel": None,
        "relative_imbalance": None,
        "relative_gate_applicable": False,
        "lateral_flux_floor": None,
        "expected_zero_driver": bool(lateral_driver_is_zero),
        "magnitude_pass": None,
        "consistency_pass": None,
        "port_pocket_diagnostics": None,
        "pass": None,
    }

    if state == "reference_blocked":
        out.update(status="NOT_APPLICABLE_NO_BRIDGE",
                   reason="the reference fixture carries no bridge structure, so there is no "
                          "transverse connection whose conservation could be evaluated")
        return out

    by_id = {r["plane_id"]: r for r in transverse_records}

    if state == "blocked":
        missing = [p for p in DUCT_CONTROL_PLANE_IDS if p not in by_id]
        solid = all(int(by_id[p]["n_fluid"]) == 0 for p in DUCT_CONTROL_PLANE_IDS
                    if p in by_id)
        if missing and not solid:
            solid = True                      # planes absent because the duct row is solid
        out["duct_planes_structurally_solid"] = bool(solid and not
                                                     any(int(by_id[p]["n_fluid"]) for p in
                                                         DUCT_CONTROL_PLANE_IDS if p in by_id))
        # blind-pocket records are retained as DIAGNOSTICS: they are recirculation inside a
        # dead-end pocket, not through-flow, and they carry no conservation verdict.
        pocket = {p: {"sum_rho_uy": by_id[p]["sum_rho_uy"], "sum_uy": by_id[p]["sum_uy"],
                      "n_fluid": int(by_id[p]["n_fluid"])}
                  for p in PORT_CONTROL_PLANE_IDS if p in by_id}
        out["port_pocket_diagnostics"] = {
            "records": pocket,
            "interpretation": "BLIND_POCKET_RECIRCULATION_NOT_THROUGH_FLOW",
        }
        if not out["duct_planes_structurally_solid"]:
            out.update(status="NOT_APPLICABLE_BLOCKED_CONNECTION", **{"pass": False},
                       reason="a blocked candidate must have structurally SOLID duct-control "
                              "planes; fluid was found there, so the geometry is not the "
                              "blocked fixture it claims to be")
            return out
        out.update(status="NOT_APPLICABLE_BLOCKED_CONNECTION",
                   reason="the connecting duct is solid, so there is no through-bridge flux to "
                          "be consistent about; the port pockets are blind and their records "
                          "are retained as recirculation diagnostics only")
        return out

    # ---- open ------------------------------------------------------------------------------
    scale = abs(_finite(axial_mass_scale, "axial_mass_scale"))
    if scale == 0.0:
        raise ValueError("the axial mass-flux normalisation scale must be nonzero")
    out["normalisation_scale"] = scale
    missing = [p for p in DUCT_CONTROL_PLANE_IDS + PORT_CONTROL_PLANE_IDS if p not in by_id]
    if missing:
        raise ValueError("open fixture is missing transverse control planes %r" % (missing,))
    order = PORT_CONTROL_PLANE_IDS[:1] + DUCT_CONTROL_PLANE_IDS + PORT_CONTROL_PLANE_IDS[1:]
    mass = [_finite(by_id[p]["sum_rho_uy"], "sum_rho_uy[%s]" % p) for p in order]
    vol = [_finite(by_id[p]["sum_uy"], "sum_uy[%s]" % p) for p in order]
    out["plane_sums_mass"] = dict(zip(order, mass))
    out["plane_sums_volume"] = dict(zip(order, vol))
    rng = max(mass) - min(mass)
    out["signed_balance"] = mass[0] - mass[-1]           # entry plane minus exit plane
    out["plane_range_mass"] = rng
    out["plane_range_mass_rel"] = _finite(abs(rng) / scale, "plane_range_mass_rel")
    out["absolute_imbalance"] = abs(rng)                  # retained under its C1 name
    out["absolute_imbalance_normalised"] = out["plane_range_mass_rel"]
    max_abs = max(abs(v) for v in mass)
    out["max_abs_lateral_mass_flux"] = max_abs
    out["max_abs_lateral_mass_flux_rel"] = _finite(max_abs / scale,
                                                   "max_abs_lateral_mass_flux_rel")
    mean_lat = sum(mass) / len(mass)
    out["mean_lateral_mass_flux"] = mean_lat
    out["abs_mean_lateral_mass_flux_rel"] = _finite(abs(mean_lat) / scale,
                                                    "abs_mean_lateral_mass_flux_rel")
    floor = LATERAL_FLUX_FLOOR_FACTOR * TOL_BRIDGE_LEAKAGE_REL * scale
    out["lateral_flux_floor"] = floor

    consistency_pass = out["plane_range_mass_rel"] <= TOL_BRIDGE_LEAKAGE_REL
    out["consistency_pass"] = bool(consistency_pass)

    if lateral_driver_is_zero:
        # Erratum PE-14: consistency alone cannot establish ZERO. Four EQUAL, materially nonzero
        # fluxes have a range of exactly zero and passed the superseded gate at any magnitude.
        magnitude_pass = out["max_abs_lateral_mass_flux_rel"] <= TOL_BRIDGE_LEAKAGE_REL
        out["magnitude_pass"] = bool(magnitude_pass)
        out.update(status="EVALUATED_ZERO_SAFE_ABSOLUTE",
                   relative_gate_applicable=False,
                   reason="expected-zero-driver control: the verdict requires BOTH that the "
                          "largest lateral mass flux is negligible against the axial mass flux "
                          "(magnitude) AND that the four planes agree (consistency). A "
                          "consistency test alone would pass four equal, materially nonzero "
                          "fluxes.")
        out["pass"] = bool(magnitude_pass and consistency_pass)
        return out

    # A DRIVEN bridge must NOT be required to carry zero lateral flux — that is the physics under
    # test. Magnitude is recorded as a physical quantity, not as a gate.
    out["magnitude_pass"] = None
    applicable = abs(mean_lat) >= floor
    out["relative_gate_applicable"] = bool(applicable)
    if applicable:
        out["relative_imbalance"] = _finite(abs(rng) / abs(mean_lat), "relative_imbalance")
        rel_pass = out["relative_imbalance"] <= TOL_MASS_REL
        reason = ("driven bridge: mean lateral mass flux is above the frozen floor, so both the "
                  "absolute consistency gate and the relative gate apply. The magnitude is "
                  "recorded as the physical lateral-flow signal, NOT as a gate.")
    else:
        rel_pass = True
        reason = ("driven bridge, but the mean lateral mass flux is below the frozen floor, so "
                  "the relative statistic is not admitted and the absolute consistency gate "
                  "alone decides. The magnitude is recorded, not gated.")
    out.update(status="EVALUATED_HYBRID", reason=reason)
    out["pass"] = bool(consistency_pass and rel_pass)
    return out


# ---- lateral pressure faces: the MEASURED zero-driver control (erratum PE-15) ---------------
# y_face1 and y_face2 were frozen in fixture_meta and never read; "zero lateral driver" was
# asserted from the geometry label alone. The cross-product gap vanishing ANALYTICALLY for a
# two-node network is not a measurement of a discretised fixture, and a label may not certify the
# premise of the decisive negative control.

PRESSURE_FACE_IDS = ("y_face1", "y_face2")
SIGN_CONVENTION_LATERAL_PRESSURE = (
    "delta_p_lateral = p_face1 - p_face2; POSITIVE drives lane1 -> lane2 along +y, matching "
    "lateral_coupling.model1_two_path's canonical q_lat_1to2 = G_lat*(p1 - p2)")

#: Frozen compact-record field names for a lateral pressure face.
PRESSURE_FACE_FIELDS = (
    "plane_id", "orientation", "index", "footprint_x", "footprint_z", "n_fluid",
    "rho_mean", "rho_sd", "p_mean", "p_sd", "p_min", "p_max",
    "sign_convention", "mask_sha256",
)

#: Measured zero-driver tolerance on the normalised lateral pressure gap. Frozen BEFORE any 001b
#: output, at the programme's established 0.1 % observable nuisance scale applied to the gap
#: normalised by the axial node-to-node pressure drop — the same number as ARTIFACT_BUDGET_R_ABS
#: and TOL_RETURN_PATH_R_REL, not a new one, and not tuned from any 001b result.
TOL_LATERAL_DRIVER_REL = 1.0e-3

def lateral_pressure_delta_record(rho, mask, meta, g):
    """EXACTLY PAIRED face-to-face effective-pressure difference over the bridge footprint.

    Erratum PE-43: the superseded implementation used ``both = m1 & m2``, silently discarding
    every node present on one face and not the other. An intersection is not a pairing, and a
    control that quietly drops the nodes that disagree cannot establish that the faces agree.
    Identical bounds, identical shape, elementwise-equal masks and equal counts are now
    ADJUDICATIVE PREREQUISITES, and anything else fails closed.

    Erratum PE-44: the spatial standard deviation is retained as a nonuniformity DIAGNOSTIC. It
    is not a numerical error bound — LB face nodes are not established independent samples — and
    ``sd/sqrt(n)`` is no longer used adjudicatively anywhere.
    """
    fx, fz = meta["bridge_x"], meta["bridge_z"]
    xs, xe = fx
    zs, ze = fz
    y1, y2 = meta["y_face1"], meta["y_face2"]
    m1 = ~mask[xs:xe, y1, zs:ze]
    m2 = ~mask[xs:xe, y2, zs:ze]
    if m1.shape != m2.shape:
        raise ValueError("the two lateral pressure faces have different shapes: %r vs %r"
                         % (m1.shape, m2.shape))
    masks_pair_exactly = bool(np.array_equal(m1, m2))
    n1, n2 = int(m1.sum()), int(m2.sum())
    if not masks_pair_exactly or n1 != n2:
        raise ValueError(
            "the lateral pressure faces do not pair exactly over the bridge footprint "
            "(elementwise equal: %s; counts %d vs %d). An intersection is not a pairing "
            "(erratum PE-43)." % (masks_pair_exactly, n1, n2))
    if n1 == 0:
        raise ValueError("the paired lateral pressure faces carry no fluid node")
    r = np.asarray(rho)
    xcoord = np.arange(xs, xe, dtype=float)[:, None]
    p1 = r[xs:xe, y1, zs:ze] / 3.0 - g * xcoord      # nodewise, BEFORE pairing or averaging
    p2 = r[xs:xe, y2, zs:ze] / 3.0 - g * xcoord
    d = (p1 - p2)[m1]
    if not np.isfinite(d).all():
        raise NonFiniteValue("a paired lateral pressure difference is not finite")
    return {
        "faces_share_footprint": True,
        "masks_pair_exactly": True,
        "n_fluid_face1": n1, "n_fluid_face2": n2, "n_paired_fluid": n1,
        "paired_mask_sha256": hashlib.sha256(
            np.packbits(np.ascontiguousarray(m1, dtype=bool)).tobytes()
            + ("%d,%d" % m1.shape).encode()).hexdigest(),
        "mean_delta_p": float(d.mean()),
        "abs_mean_delta_p": float(abs(d.mean())),
        "max_abs_delta_p": float(np.abs(d).max()),
        "min_delta_p": float(d.min()), "max_delta_p": float(d.max()),
        "spatial_sd_delta_p": float(d.std()),
        "spatial_sd_role": "SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND",
        "footprint_x": (int(xs), int(xe)), "footprint_z": (int(zs), int(ze)),
        "method": "EXACT_PAIRED_FACE_DIFFERENCE_COMMON_AXIAL_GRADIENT_CANCELS_EXACTLY",
        "sign_convention": SIGN_CONVENTION_LATERAL_PRESSURE,
        "all_finite": True,
    }


def lateral_pressure_upper_bounds(normal_delta, axial_pressure_scale,
                                  audit_delta=None, expected_zero_driver=False):
    """Mean AND maximum paired-gap upper bounds (errata PE-45, PE-46).

    The superseded control gated only the mean, so alternating positive and negative paired
    differences with a zero mean passed however large the individual differences were. Both
    statistics are now bounded, and each bound takes its uncertainty from the record's OWN
    fixed-step audit — never from a spatial standard error.
    """
    scale = abs(_finite(axial_pressure_scale, "axial_pressure_scale"))
    if scale == 0.0:
        raise ValueError("the axial pressure normalisation scale must be nonzero")
    mean_pt = _finite(normal_delta["mean_delta_p"], "mean_delta_p")
    max_pt = _finite(normal_delta["max_abs_delta_p"], "max_abs_delta_p")
    sf = NUMERICAL_DISCREPANCY_SAFETY_FACTOR
    if audit_delta is None:
        u_mean = u_max = None
    else:
        u_mean = sf * abs(_finite(audit_delta["mean_delta_p"], "audit mean_delta_p") - mean_pt)
        u_max = sf * abs(_finite(audit_delta["max_abs_delta_p"], "audit max_abs_delta_p")
                         - max_pt)
    u_ser = 10.0 ** (-_RECORD_DP) * (1.0 + abs(mean_pt))
    out = {
        "axial_pressure_scale": scale,
        "mean_delta_p": mean_pt, "abs_mean_delta_p": abs(mean_pt), "max_abs_delta_p": max_pt,
        "spatial_sd_delta_p": normal_delta["spatial_sd_delta_p"],
        "spatial_sd_role": normal_delta["spatial_sd_role"],
        "safety_factor": sf,
        "u_mean_gap": u_mean, "u_max_gap": u_max,
        "u_serialization_mean": u_ser, "u_serialization_max": u_ser,
        "tolerance": TOL_LATERAL_DRIVER_REL,
        "expected_zero_driver": bool(expected_zero_driver),
        "evidence_complete": bool(audit_delta is not None),
        "overlaps": ("u_mean_gap and u_max_gap come from the same fixed-step pair but bound "
                     "different statistics; neither is added to the other"),
    }
    if audit_delta is None:
        out.update(mean_gap_upper_rel=None, max_gap_upper_rel=None,
                   mean_pass=None, max_pass=None, **{"pass": None},
                   reason=("no fixed-step evidence for the pressure gap; an upper-bound verdict "
                           "cannot be formed (erratum PE-46)"))
        return out
    out["mean_gap_upper_rel"] = _finite((abs(mean_pt) + u_mean + u_ser) / scale,
                                        "mean_gap_upper_rel")
    out["max_gap_upper_rel"] = _finite((max_pt + u_max + u_ser) / scale, "max_gap_upper_rel")
    if expected_zero_driver:
        out["mean_pass"] = bool(out["mean_gap_upper_rel"] <= TOL_LATERAL_DRIVER_REL)
        out["max_pass"] = bool(out["max_gap_upper_rel"] <= TOL_LATERAL_DRIVER_REL)
        out["pass"] = bool(out["mean_pass"] and out["max_pass"])
        out["reason"] = ("expected-zero-driver control: BOTH the mean and the maximum paired gap "
                         "must clear the tolerance. A zero mean produced by cancellation cannot "
                         "pass while the maximum paired difference is excessive (erratum PE-45).")
    else:
        out.update(mean_pass=None, max_pass=None, **{"pass": None},
                   reason=("driven bridge: a nonzero lateral gap is the physics under test, so "
                           "no zero-driver verdict applies"))
    return out


def pressure_face_record(plane_id, y, rho, mask, g, footprint_x, footprint_z):
    """The frozen compact record for one lateral pressure face.

    The effective pressure is the SAME convention the axial records use,
    ``p_eff = rho/3 - g*x``, evaluated **nodewise before averaging**, so the body-force potential
    is subtracted correctly across a multi-``x`` footprint. Fluid nodes only; solids excluded,
    never counted as zero.
    """
    xs, xe = footprint_x
    zs, ze = footprint_z
    sub_mask = mask[xs:xe, y, zs:ze]
    fl = ~sub_mask
    if not fl.any():
        raise ValueError("pressure face %r has no fluid node over the bridge footprint"
                         % (plane_id,))
    r = np.asarray(rho)[xs:xe, y, zs:ze]
    xcoord = np.arange(xs, xe, dtype=float)[:, None]
    p_eff = r / 3.0 - g * xcoord                     # nodewise, BEFORE averaging
    vals = p_eff[fl]
    if not np.isfinite(vals).all():
        raise NonFiniteValue("pressure face %r carries a non-finite effective pressure"
                             % (plane_id,))
    rv = r[fl]
    return {
        "plane_id": plane_id, "orientation": "y", "index": int(y),
        "footprint_x": (int(xs), int(xe)), "footprint_z": (int(zs), int(ze)),
        "n_fluid": int(fl.sum()),
        "rho_mean": float(rv.mean()), "rho_sd": float(rv.std()),
        "p_mean": float(vals.mean()), "p_sd": float(vals.std()),
        "p_min": float(vals.min()), "p_max": float(vals.max()),
        "sign_convention": SIGN_CONVENTION_LATERAL_PRESSURE,
        "mask_sha256": mask_hash(mask),
    }


def lateral_pressure_gap(face_records, delta_record, axial_pressure_scale, g, q_lat_mass=None,
                         expected_zero_driver=False):
    """The MEASURED lateral driving-pressure difference and its adjudication (erratum PE-15).

    ``axial_pressure_scale`` is the case's own node-to-node axial pressure drop — a frozen,
    nonzero normalisation that is never the lateral gap itself.

    For an expected-zero-driver control the geometry supplies only the EXPECTATION; execution
    validity additionally requires the MEASURED gap to clear ``TOL_LATERAL_DRIVER_REL``.
    """
    by_id = {r["plane_id"]: r for r in face_records}
    missing = [p for p in PRESSURE_FACE_IDS if p not in by_id]
    if missing:
        raise ValueError("lateral pressure gap needs both faces; missing %r" % (missing,))
    f1, f2 = by_id["y_face1"], by_id["y_face2"]
    scale = abs(_finite(axial_pressure_scale, "axial_pressure_scale"))
    if scale == 0.0:
        raise ValueError("the axial pressure normalisation scale must be nonzero")
    gv = _finite(g, "g")
    if gv == 0.0:
        raise ValueError("the body force must be nonzero to form delta_p/g")
    gap = _finite(delta_record["mean_delta_p"], "mean_delta_p")
    rel = _finite(abs(gap) / scale, "delta_p_lateral_rel")
    out = {
        "p_face1": f1["p_mean"], "p_face2": f2["p_mean"],
        "p_face1_sd": f1["p_sd"], "p_face2_sd": f2["p_sd"],
        "face_nonuniformity_rel": _finite((f1["p_sd"] + f2["p_sd"]) / scale,
                                          "face_nonuniformity_rel"),
        "face_nonuniformity_role": "SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND",
        "max_abs_delta_p": delta_record["max_abs_delta_p"],
        "masks_pair_exactly": delta_record["masks_pair_exactly"],
        "n_paired_fluid": delta_record["n_paired_fluid"],
        "delta_p_lateral": gap,
        "delta_p_lateral_from_face_means": _finite(f1["p_mean"] - f2["p_mean"],
                                                   "delta_from_means"),
        "delta_p_lateral_over_g": _finite(gap / gv, "delta_p_lateral_over_g"),
        "delta_pointwise": dict(delta_record),
        "axial_pressure_scale": scale,
        "axial_pressure_scale_source": "p_mean(x_node_in) - p_mean(x_node_out)",
        "delta_p_lateral_rel": rel,
        "upper_bound_source": ("lateral_pressure_upper_bounds(), from this record's own "
                               "fixed-step audit; a spatial standard error is never used "
                               "adjudicatively (erratum PE-44)"),
        "sign_convention": SIGN_CONVENTION_LATERAL_PRESSURE,
        "tolerance": TOL_LATERAL_DRIVER_REL,
        "expected_zero_driver": bool(expected_zero_driver),
        "q_lat_mass": (None if q_lat_mass is None else _finite(q_lat_mass, "q_lat_mass")),
        "q_lat_mass_over_g": (None if q_lat_mass is None
                              else _finite(float(q_lat_mass) / gv, "q_lat_mass_over_g")),
    }
    if expected_zero_driver:
        # Erratum PE-61: the POINT estimate is an EARLY SCREEN, never the final verdict. It may
        # REJECT — every omitted uncertainty term is non-negative, so a point failure cannot be
        # rescued — and it may NEVER ADMIT. The adjudicative verdict is
        # ``measured_zero_driver_upper_bound_pass``, formed only where this record's OWN exact
        # fixed-step audit is available, which is at assembly and not at case construction.
        out["measured_zero_driver_point_pass"] = bool(rel <= TOL_LATERAL_DRIVER_REL)
        out["measured_zero_driver_point_role"] = (
            "PRELIMINARY_POINT_ESTIMATE_SCREEN_MAY_REJECT_NEVER_ADMITS")
        out["measured_zero_driver_upper_bound_pass"] = None
        out["measured_zero_driver_pass"] = None
        out["measured_zero_driver_status"] = "INCOMPLETE_PENDING_FIXED_STEP_AUDIT"
        out["final_verdict_source"] = (
            "lateral_pressure_evidence_from_records() -> lateral_pressure_upper_bounds(), paired "
            "with this case's EXACT fixed-step audit; BOTH mean_gap_upper_rel and "
            "max_gap_upper_rel must clear TOL_LATERAL_DRIVER_REL (erratum PE-61)")
        out["reason"] = ("identical-path control: the geometry supplies the EXPECTATION of a zero "
                         "lateral driver, and the measured mid-face pressure gap must confirm it. "
                         "A geometry label alone may never certify the premise of the negative "
                         "control (erratum PE-15). This record carries only the PRELIMINARY point "
                         "screen; the final paired normal/audit upper-bound verdict is formed "
                         "where the fixed-step audit exists (erratum PE-61).")
    else:
        out["measured_zero_driver_point_pass"] = None
        out["measured_zero_driver_point_role"] = "NOT_APPLICABLE_DRIVEN_BRIDGE"
        out["measured_zero_driver_upper_bound_pass"] = None
        out["measured_zero_driver_pass"] = None
        out["measured_zero_driver_status"] = "NOT_APPLICABLE_DRIVEN_BRIDGE"
        out["final_verdict_source"] = None
        out["reason"] = ("driven bridge: a nonzero lateral pressure gap is the physics under "
                         "test, so no zero-driver verdict applies. The gap and delta_p/g are "
                         "retained for the frozen componentwise forcing checks.")
    return out


# ---- low-Mach validity: the FULL velocity vector over fluid nodes only (erratum PE-4) -------

def mach_record(ux, uy, uz, mask):
    """Maximum lattice speed and Mach number over FLUID NODES ONLY, from all three components.

    ``design_mach_scale`` is an a-priori planning estimate of the mean lattice velocity; this is
    the measured maximum the control actually needs. ``uz`` is NOT assumed to vanish from nominal
    symmetry — the bridge, the ports and the junctions all break that picture, and 001 recorded
    that low Mach and low Reynolds are related but not interchangeable.
    """
    for name, arr in (("ux", ux), ("uy", uy), ("uz", uz)):
        if arr is None:
            raise ValueError("mach_record requires %s; the solve must request "
                             "return_fields covering rho, uy and uz" % name)
        if not np.isfinite(np.asarray(arr)[~mask]).all():
            raise NonFiniteValue("%s contains a non-finite value at a fluid node" % name)
    fluid = ~mask
    if not fluid.any():                                      # pragma: no cover - degenerate mask
        raise ValueError("mach_record needs at least one fluid node")
    sx, sy, sz = np.asarray(ux), np.asarray(uy), np.asarray(uz)
    speed = np.sqrt(sx * sx + sy * sy + sz * sz)
    speed = np.where(fluid, speed, -np.inf)                  # solids excluded, never counted
    flat = int(np.argmax(speed))
    idx = tuple(int(v) for v in np.unravel_index(flat, speed.shape))
    max_speed = _finite(speed[idx], "max_speed_fluid")
    max_mach = float(np.sqrt(3.0)) * max_speed
    return {
        "max_speed_fluid": max_speed,
        "max_mach": max_mach,
        "argmax_flat_index": flat,
        "argmax_index": idx,
        "ux_at_max": _finite(sx[idx], "ux_at_max"),
        "uy_at_max": _finite(sy[idx], "uy_at_max"),
        "uz_at_max": _finite(sz[idx], "uz_at_max"),
        "n_fluid": int(fluid.sum()),
        "tol_mach": TOL_MACH,
        "pass": bool(max_mach <= TOL_MACH),
        "components_used": ["ux", "uy", "uz"],
        "solid_nodes_excluded": True,
    }


# ==========================================================================================
# 5. BOUNDARY-ONLY INFERENCE — imported, never re-derived
# ==========================================================================================
# The anti-circularity boundary is the 001 contract, unchanged and IMPORTED rather than copied,
# so the two tranches cannot drift apart: infer_from_boundary accepts exactly BOUNDARY_KEYS and
# raises on anything else, and it delegates to the existing verified WP6 inverse.

BOUNDARY_KEYS = tuple(vf001.BOUNDARY_KEYS)
infer_from_boundary = vf001.infer_from_boundary

#: Keys that must NEVER appear in a boundary record. Named explicitly so the allowlist test can
#: demonstrate rejection rather than merely assert a set equality.
FORBIDDEN_BOUNDARY_KEYS = (
    "c_field", "c_truth", "Xi_field", "Xi_truth", "G_lat_field", "G_lat_coupon",
    "q_lat", "p_face1_open", "p_face2_open", "bridge", "w", "kz",
    "sum_rho_ux", "sum_rho_uy", "aperture", "mask_sha256",
)


def assert_boundary_record(record):
    """Validate a boundary record against the frozen allowlist BEFORE it reaches the inverse."""
    keys = tuple(sorted(record))
    if keys != tuple(sorted(BOUNDARY_KEYS)):
        raise ValueError(
            "boundary record must carry exactly %r; got %r — the anti-circularity contract "
            "forbids passing any truth-side quantity to the inverse." % (sorted(BOUNDARY_KEYS),
                                                                         list(keys)))
    return dict(record)


# ==========================================================================================
# 6. NEGATIVE-CONTROL ARTIFACT METRICS AND THE ARTIFACT BUDGET
# ==========================================================================================
# The decisive pre-execution control: with the two lanes IDENTICAL the cross-product gap
# X = g1t*g2b - g2t*g1b is exactly zero, so no lateral pressure difference drives the bridge at
# any conductance and the two-node network predicts R = 1 and s = 1/2 for ANY positive G_lat.
# Opening the bridge must therefore leave the axial conductance materially unchanged. In 001 it
# did not: the residual was R - 1 = 0.014277334586.
#
# The budget is set BEFORE any 001b output, from the repository's established 0.1 % observable
# nuisance scale (the Route-A isolation bound of 001 erratum E1, TOL_RETURN_PATH_R_REL = 1e-3)
# applied to the same observable the inverse consumes. Its consequence for the science is
# bounded ex ante in ``artifact_budget_justification()``: across the whole WP6 transition window
# a 1e-3 artifact biases Xi_hat by under ~6 %, far inside the factor-of-two recovery criterion.

ARTIFACT_BUDGET_R_ABS = 1.0e-3
ARTIFACT_BUDGET_PROVENANCE = (
    "programme 0.1 % observable-level nuisance scale; identical to TOL_RETURN_PATH_R_REL frozen "
    "in RP-D-LC-001 erratum E1 for the Route-A isolation gate"
)

# ---- the R-specific numerical-discrepancy method (erratum PE-6) ----------------------------
# SUPERSEDED: NUMERICAL_UNCERTAINTY_R_ABS = TOL_MASS_REL. A plane-to-plane mass-flux residual and
# the numerical discrepancy of a pressure-normalised conductance RATIO are different quantities;
# equating them was presented as conservative but was simply unrelated, and it happened to equal
# the entire artifact budget.
#
# What is frozen here is a METHOD, evaluated per case, deliberately not a constant and
# deliberately NOT called a rigorous error bound. It is a CONSERVATIVE NUMERICAL-DISCREPANCY
# BOUND assembled from three separately measurable contributions:
#
#   |dR|_continuation  re-run at CONVERGENCE_AUDIT_FACTOR x the converged step count, separately
#                      for the OPEN and BLOCKED members of the pair, propagated through the ratio
#                      as a linear (not quadrature) sum, which is the conservative composition;
#   |dR|_node_offset   the largest movement of R across the frozen node-surface offsets. Needs NO
#                      extra solve: the offsets are different planes of the same solution;
#   u_serialisation    10^-_RECORD_DP * (1 + |R|) — negligible, but declared rather than assumed.
#
# times a frozen safety factor.
NUMERICAL_DISCREPANCY_SAFETY_FACTOR = 2.0
NUMERICAL_DISCREPANCY_METHOD = (
    "u_R = SAFETY * ( |dR|_continuation + |dR|_node_offset + u_serialisation ); continuation from "
    "a forced re-run at CONVERGENCE_AUDIT_FACTOR x the converged step count with the open and "
    "blocked contributions propagated separately through the conductance ratio; node-offset from "
    "the frozen surface offsets, which need no extra solve; serialisation from the frozen record "
    "precision. A CONSERVATIVE NUMERICAL-DISCREPANCY BOUND, not a rigorous error bound."
)


def _rel(a, b):
    """|a/b - 1| with a finite check — the relative movement of a continuation run."""
    b = _finite(b, "reference value")
    if b == 0.0:
        raise ZeroDivisionError("cannot form a relative discrepancy against zero")
    return abs(_finite(a, "continuation value") / b - 1.0)


def numerical_discrepancy_R(R, C_open, C_blocked, C_open_continued, C_blocked_continued,
                            R_node_offsets=(), safety=NUMERICAL_DISCREPANCY_SAFETY_FACTOR):
    """The frozen R-specific numerical-discrepancy bound, with every term reported separately.

    ``C_*_continued`` are the conductances from the forced-step continuation runs.
    ``R_node_offsets`` are the values of R obtained on the frozen node-surface offsets (offset 0
    is the primary and is ``R`` itself). Non-finite inputs fail closed.
    """
    R = _finite(R, "R")
    u_open = _rel(C_open_continued, C_open)
    u_blocked = _rel(C_blocked_continued, C_blocked)
    # R = C_open / C_blocked, so relative errors add through the ratio; linear sum, not quadrature
    u_cont = abs(R) * (u_open + u_blocked)
    offs = [_finite(v, "R at a node offset") for v in R_node_offsets]
    u_offset = max((abs(v - R) for v in offs), default=0.0)
    u_serial = 10.0 ** (-_RECORD_DP) * (1.0 + abs(R))
    total = float(safety) * (u_cont + u_offset + u_serial)
    return {
        "method": NUMERICAL_DISCREPANCY_METHOD,
        "kind": "CONSERVATIVE_NUMERICAL_DISCREPANCY_BOUND_NOT_A_RIGOROUS_ERROR_BOUND",
        "R": R,
        "u_continuation_open_rel": u_open,
        "u_continuation_blocked_rel": u_blocked,
        "u_continuation_R_abs": u_cont,
        "u_node_offset_R_abs": u_offset,
        "u_serialisation_R_abs": u_serial,
        "safety_factor": float(safety),
        "u_R_abs": _finite(total, "u_R_abs"),
    }


def artifact_metrics(C_open, C_blocked, R_identical, R_identical_mass=None,
                     numerical_uncertainty=None):
    """Every required form of the zero-lateral-driver axial artifact, physical and normalised.

    The ADJUDICATIVE metric is ``pressure_normalised_R_change`` = ``R_identical - 1``: it is the
    quantity the inverse consumes, in the pressure-normalised form Route A requires. The
    mass-flux form is retained as a separate DIAGNOSTIC and is never substituted for it.

    The gate is an UPPER-BOUND form (erratum PE-6):

        abs(R_identical - 1) + u_artifact_R  <=  ARTIFACT_BUDGET_R_ABS

    with the point estimate, the uncertainty term, the upper bound and the verdict reported
    separately. ``numerical_uncertainty`` is the ``u_R_abs`` of ``numerical_discrepancy_R`` and is
    REQUIRED: there is no default, because a default would silently reintroduce a borrowed
    constant. A non-finite uncertainty fails closed.
    """
    if numerical_uncertainty is None:
        raise ValueError(
            "artifact_metrics requires an explicit R-specific numerical uncertainty from "
            "numerical_discrepancy_R(); the superseded default borrowed TOL_MASS_REL, which is a "
            "different quantity (erratum PE-6)")
    u = _finite(numerical_uncertainty, "numerical_uncertainty")
    if u < 0.0:
        raise ValueError("numerical uncertainty must be non-negative, got %r" % (u,))
    signed = _finite(C_open, "C_open") - _finite(C_blocked, "C_blocked")
    point = _finite(R_identical, "R_identical") - 1.0
    upper = abs(point) + u
    return {
        "signed_conductance_change": signed,
        "absolute_conductance_change": abs(signed),
        "relative_conductance_change": signed / _finite(C_blocked, "C_blocked"),
        "pressure_normalised_R_change": point,
        "pressure_normalised_R_change_abs": abs(point),
        "mass_flux_R_change": (None if R_identical_mass is None
                               else _finite(R_identical_mass, "R_identical_mass") - 1.0),
        "numerical_uncertainty_R_abs": u,
        "artifact_upper_bound": upper,
        "adjudicative_metric": "abs(pressure_normalised_R_change) + numerical_uncertainty_R_abs",
        "budget_R_abs": ARTIFACT_BUDGET_R_ABS,
        "within_budget": bool(upper <= ARTIFACT_BUDGET_R_ABS),
    }


# ==========================================================================================
# 7. REACHABLE-SET PROTECTION
# ==========================================================================================
# The two-node mirror network's forward map is exact (WP6-LC-IDENT DECISIVE_EXPERIMENT.md §7):
#
#       R - 1 = [c^2 / (1 - c^2)] * [Xi / (1 + Xi)]
#
# so as Xi -> infinity, R - 1 approaches the hard ceiling c^2/(1-c^2) from below. An observation
# above that ceiling is reproducible by NO (c, Xi) pair: the inverse absorbs the excess by
# inflating c_hat, which is exactly what happened at 001's largest aperture (observed
# R - 1 = 0.1338 against a ceiling of 0.1155 at c_field = 0.3218).
#
# SUPERSEDED (erratum PE-7): a fixed 5 % allowance applied to the REFERENCE-blocked c_field and
# described as "strictly conservative". The reduction of the ceiling is monotone in c, so the
# allowance WOULD be conservative if the true candidate contrast were within 5 % — but nothing
# established that, and the supporting argument was first-order symmetry, which is not a bound.
#
# Effective: candidate-specific BLOCKED MIRROR characterisation in P2a (which exposes no open
# coupling-recovery observable) yields a measured conservative interval [c_lower, c_upper]. The
# signal is taken at the UPPER end of the contrast and Xi envelopes and the ceiling at the LOWER
# end, so the inequality is conservative on both sides rather than on one.

#: Safety margin as a fraction of the ceiling. Justified by conditioning, not by taste: with
#: eps = (R-1)/K the inverse gives Xi = eps/(1-eps), so the RELATIVE error amplification is
#: d(ln Xi)/d(ln eps) = 1/(1-eps). Requiring eps <= 0.90 caps that amplification at 10x.
REACHABLE_SAFETY_MARGIN_FRACTION = 0.10
REACHABLE_MARGIN_JUSTIFICATION = (
    "eps = (R-1)/K, Xi = eps/(1-eps), d(ln Xi)/d(ln eps) = 1/(1-eps); the frozen margin caps the "
    "inverse's relative-error amplification at 10x"
)


def reachable_ceiling(c: float) -> float:
    """The two-node model's hard ceiling on R - 1 at the given signed axial contrast."""
    c = float(c)
    if not -1.0 < c < 1.0:
        raise ValueError("contrast c must lie strictly in (-1, 1), got %r" % (c,))
    return c * c / (1.0 - c * c)


def predicted_R_minus_1(c: float, Xi: float) -> float:
    """The exact forward map R - 1 = [c^2/(1-c^2)] * [Xi/(1+Xi)]."""
    Xi = float(Xi)
    if Xi < 0.0:
        raise ValueError("Xi must be non-negative, got %r" % (Xi,))
    return reachable_ceiling(c) * (Xi / (1.0 + Xi))


def candidate_c_bounds(c_measurements, resolution_tolerance, numerical_rel,
                       surface_rel=0.0):
    """A conservative measured interval for a candidate's blocked-mirror axial contrast.

    ``c_measurements``        every |c_field| measured on that candidate's BLOCKED MIRROR fixture,
                              across BOTH resolutions and the full forcing ladder. No open mirror
                              case may contribute.
    ``resolution_tolerance``  the ex-ante resolution-consistency tolerance for ``c_field``.
    ``numerical_rel``         the relative numerical-discrepancy term.
    ``surface_rel``           documented plane/surface variability, relative.

    Replaces the superseded fixed 5 % allowance (erratum PE-7).
    """
    vals = [abs(_finite(v, "c measurement")) for v in c_measurements]
    if not vals:
        raise ValueError("candidate_c_bounds requires at least one blocked-mirror measurement of "
                         "|c_field|; the superseded fixed allowance is removed (erratum PE-7)")
    u_rel = (_finite(resolution_tolerance, "resolution_tolerance")
             + _finite(numerical_rel, "numerical_rel") + _finite(surface_rel, "surface_rel"))
    if u_rel < 0.0:
        raise ValueError("uncertainty terms must be non-negative")
    lo = min(vals) * (1.0 - u_rel)
    hi = max(vals) * (1.0 + u_rel)
    if not 0.0 < lo < 1.0 or not 0.0 < hi < 1.0:
        raise ValueError("the derived contrast interval [%r, %r] leaves the physical range "
                         "(0, 1); the candidate cannot be admitted" % (lo, hi))
    return {
        "n_measurements": len(vals),
        "c_measurements": sorted(vals),
        "resolution_tolerance": float(resolution_tolerance),
        "numerical_rel": float(numerical_rel),
        "surface_rel": float(surface_rel),
        "u_rel_total": u_rel,
        "c_lower": lo, "c_upper": hi,
        "source": "candidate BLOCKED MIRROR characterisation only; no open mirror case",
    }


def max_admissible_Xi(c_lower, artifact_upper, other_numerical_upper=0.0,
                      margin_fraction=REACHABLE_SAFETY_MARGIN_FRACTION, c_upper=None):
    """The largest Xi that can satisfy the admission inequality, or 0.0 if the artifact and
    numerical bounds already consume the whole margin."""
    K_lo = reachable_ceiling(c_lower)
    K_hi = reachable_ceiling(c_lower if c_upper is None else c_upper)
    headroom = K_lo * (1.0 - margin_fraction) - float(artifact_upper) - float(
        other_numerical_upper)
    if headroom <= 0.0:
        return 0.0
    frac = headroom / K_hi
    if frac >= 1.0:
        return float("inf")
    return frac / (1.0 - frac)


def reachable_set_admission(c_lower, c_upper, Xi_upper, artifact_upper,
                            other_numerical_upper=0.0,
                            margin_fraction=REACHABLE_SAFETY_MARGIN_FRACTION):
    """The frozen admission test (erratum PE-7):

        predicted_signal_upper(c_upper, Xi_upper) + artifact_upper
            + other_nonoverlapping_numerical_upper
        <  reachable_ceiling(c_lower) - frozen_safety_margin

    The four terms are kept STRICTLY SEPARATE so no uncertainty is counted twice:

      * ``artifact_upper`` already contains the R-specific numerical discrepancy
        (``artifact_metrics``'s ``artifact_upper_bound``);
      * the candidate-c uncertainty is folded into ``[c_lower, c_upper]`` and is never added
        again;
      * the predicted-signal/coupon uncertainty is carried by ``Xi_upper``;
      * ``other_numerical_upper`` is any additional NON-OVERLAPPING term, zero by construction
        unless one is introduced and declared.

    ``c_lower``/``c_upper`` come from ``candidate_c_bounds`` on the candidate's BLOCKED MIRROR
    fixture. No open mirror result may enter this gate.
    """
    c_lo, c_hi = abs(_finite(c_lower, "c_lower")), abs(_finite(c_upper, "c_upper"))
    if c_hi < c_lo:
        raise ValueError("c_upper must not be below c_lower, got %r < %r" % (c_hi, c_lo))
    K_lo = reachable_ceiling(c_lo)
    K_hi = reachable_ceiling(c_hi)
    margin = margin_fraction * K_lo
    signal = predicted_R_minus_1(c_hi, Xi_upper)         # signal at the UPPER contrast/Xi
    art = _finite(artifact_upper, "artifact_upper")
    oth = _finite(other_numerical_upper, "other_numerical_upper")
    if art < 0.0 or oth < 0.0:
        raise ValueError("uncertainty upper bounds must be non-negative")
    lhs = signal + art + oth
    rhs = K_lo - margin                                   # ceiling at the LOWER contrast
    return {
        "c_lower": c_lo, "c_upper": c_hi,
        "reachable_ceiling": K_lo,
        "reachable_ceiling_at_c_upper": K_hi,
        "safety_margin": margin,
        "safety_margin_fraction": float(margin_fraction),
        "safety_margin_justification": REACHABLE_MARGIN_JUSTIFICATION,
        "Xi_upper": float(Xi_upper),
        "predicted_signal_upper": signal,
        "artifact_upper": art,
        "other_nonoverlapping_numerical_upper": oth,
        "double_counting_prohibited": (
            "artifact_upper already contains u_R; candidate-c uncertainty is inside "
            "[c_lower, c_upper]; coupon uncertainty is inside Xi_upper"),
        "lhs": lhs, "rhs": rhs,
        "headroom": rhs - lhs,
        "admitted": bool(lhs < rhs),
        "max_admissible_Xi": max_admissible_Xi(c_lo, art, oth, margin_fraction, c_upper=c_hi),
    }


def artifact_budget_justification(c_gate, Xi_lo=vf001.XI_WINDOW_LO, Xi_hi=vf001.XI_WINDOW_HI,
                                  artifact=ARTIFACT_BUDGET_R_ABS):
    """Bound, ex ante, what the artifact budget costs the science: the relative bias it can
    induce in Xi_hat at each end of the WP6 transition window. Derived from the exact forward map
    and the frozen budget only — no 001b output exists or is consulted."""
    c = abs(_finite(c_gate, "c_gate"))
    K = reachable_ceiling(c)
    out = {"c_gate": c, "reachable_ceiling": K, "artifact": float(artifact), "ends": {}}
    for name, Xi in (("window_lo", float(Xi_lo)), ("window_hi", float(Xi_hi))):
        eps = Xi / (1.0 + Xi)
        d_eps_rel = (artifact / K) / eps
        out["ends"][name] = {
            "Xi": Xi, "signal_R_minus_1": K * eps,
            "relative_signal_perturbation": d_eps_rel,
            "amplification": 1.0 / (1.0 - eps),
            "relative_Xi_bias": d_eps_rel / (1.0 - eps),
        }
    out["max_relative_Xi_bias"] = max(v["relative_Xi_bias"] for v in out["ends"].values())
    out["factor_of_two_criterion"] = 1.0
    out["well_inside_factor_of_two"] = bool(out["max_relative_Xi_bias"] < 0.25)
    return out


# ==========================================================================================
# 8. DETERMINISTIC CANDIDATE SELECTION (the bridge freeze rule)
# ==========================================================================================
# Committed BEFORE any coupon output exists and applied MECHANICALLY. It reads coupon-predicted
# Xi and the P1 artifact bound only — never a mirror full-fixture observable.

XI_WINDOW_LO = vf001.XI_WINDOW_LO
XI_WINDOW_HI = vf001.XI_WINDOW_HI
XI_WINDOW_PROVENANCE = vf001.XI_WINDOW_PROVENANCE
N_LOG_TARGETS = 3
#: The freeze requires EXACTLY this many unique candidates: one below plus three inside
#: (erratum PE-20). An ABOVE-window slot is NOT required: clause 2 needs three IN-window cases and
#: an above-window candidate contributes nothing to that count, clause 5's monotonicity is served
#: by four ordered points, and the corrected two-sided reachable-set gate can make an above-window
#: candidate inadmissible under its own safety requirement. The 0.10*K margin is unchanged and is
#: NOT tunable to fill a slot.
N_FROZEN_BRIDGES = N_LOG_TARGETS + 1

#: Category of a candidate, decided on its WHOLE conservative envelope (erratum PE-9).
XI_CATEGORIES = ("below", "inside", "above", "boundary_ambiguous")

#: Frozen reason codes for a pre-execution design stop. A missing categorical slot is a STOP,
#: never an improvisation: no P3 slot is ever populated by anything but the frozen rule.
DESIGN_BLOCKED_REASONS = (
    "NO_CANDIDATE_WITHIN_ARTIFACT_BUDGET",
    "NO_CANDIDATE_ADMITTED_BY_REACHABLE_SET",
    "INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES",
    "NO_UNAMBIGUOUS_BELOW_CANDIDATE",
    "SELECTION_UNDERFILLED_AFTER_DEDUPLICATION",
)
#: Retired as a required-selection stop by erratum PE-20. Retained by name so a record that cited
#: it under C1 stays interpretable; it may never be raised by the C2 selection rule.
RETIRED_DESIGN_BLOCKED_REASONS = ("NO_UNAMBIGUOUS_ABOVE_CANDIDATE",)

FREEZE_RULE = (
    "Eligibility first: a candidate must pass its forcing-invariance and resolution-consistency "
    "gates, then the identical-path axial-artifact UPPER-BOUND gate at BOTH scientific "
    "resolutions and ALL THREE forcing levels with its own fixed-step evidence, then the "
    "reachable-set admission test built on its own measured blocked-mirror contrast interval. "
    "Then, from the eligible set: Xi_select is the GEOMETRIC MEAN of every valid positive coupon "
    "estimate across both resolutions and all three forcing levels; the complete conservative "
    "envelope [Xi_lower, Xi_upper] is retained; category is decided on the WHOLE envelope "
    "(below/inside/above only if the entire envelope lies there, otherwise boundary_ambiguous and "
    "unavailable for a categorical slot); the BELOW slot takes the largest Xi_select among "
    "unambiguous 'below' candidates, and three INSIDE slots take the candidates nearest three "
    "log-spaced in-window targets by Xi_select. An ABOVE-window slot is NOT required and 'above' "
    "is retained only as a diagnostic category. Deduplicate preserving order, then emit in "
    "ASCENDING Xi_select. Ties break on smaller w, then smaller kz. EXACTLY four unique "
    "candidates are required; any shortfall is a DESIGN_BLOCKED_PRE_EXECUTION stop with a frozen "
    "reason code, never an improvised slot and never a post-hoc reselection. The rule reads "
    "coupon output, the identical-path artifact and blocked-mirror characterisation ONLY; no "
    "mirror OPEN full-fixture R, s or Xi_hat may be inspected before the freeze exists."
)


def log_targets(lo=None, hi=None, n=N_LOG_TARGETS):
    lo = XI_WINDOW_LO if lo is None else lo
    hi = XI_WINDOW_HI if hi is None else hi
    return [float(np.exp(t)) for t in np.linspace(np.log(lo), np.log(hi), n + 2)[1:-1]]


def _cand_key(c):
    return (int(c["w"]), int(c["kz"]))


def xi_envelope(estimates, uncertainty_rel):
    """Collapse a candidate's coupon estimates to ONE deterministic selection coordinate and a
    conservative envelope (erratum PE-9).

    ``estimates`` is an iterable of dicts with ``S``, ``forcing_level``, ``coupon_source`` and
    ``Xi``. Every valid positive estimate across BOTH resolutions and ALL three forcing levels
    contributes; the selection coordinate is their GEOMETRIC MEAN, which is the natural centre
    for a quantity compared against log-spaced targets and spanning more than a decade.
    """
    rows = [dict(e) for e in estimates]
    if not rows:
        raise ValueError("a candidate must carry at least one coupon Xi estimate")
    for r in rows:
        for k in ("S", "forcing_level", "coupon_source", "Xi"):
            if k not in r:
                raise ValueError("coupon estimate is missing %r: %r" % (k, r))
    valid = [r for r in rows if math.isfinite(float(r["Xi"])) and float(r["Xi"]) > 0.0]
    if not valid:
        raise ValueError("no valid positive coupon Xi estimate for this candidate")
    u = _finite(uncertainty_rel, "uncertainty_rel")
    if u < 0.0:
        raise ValueError("uncertainty_rel must be non-negative")
    vals = [float(r["Xi"]) for r in valid]
    xi_select = float(np.exp(np.mean(np.log(vals))))
    lower = min(vals) * (1.0 - u)
    upper = max(vals) * (1.0 + u)
    resolutions = sorted({int(r["S"]) for r in valid})
    levels = sorted({str(r["forcing_level"]) for r in valid})
    if upper < XI_WINDOW_LO:
        cat = "below"
    elif lower > XI_WINDOW_HI:
        cat = "above"
    elif lower >= XI_WINDOW_LO and upper <= XI_WINDOW_HI:
        cat = "inside"
    else:
        cat = "boundary_ambiguous"
    return {
        "estimates": sorted(valid, key=lambda r: (int(r["S"]), str(r["forcing_level"]),
                                                  str(r["coupon_source"]))),
        "n_estimates": len(valid),
        "resolutions": resolutions,
        "forcing_levels": levels,
        "uncertainty_rel": u,
        "Xi_select": xi_select,
        "Xi_lower": max(lower, 0.0),
        "Xi_upper": upper,
        "category": cat,
        "categorically_usable": cat in ("below", "inside", "above"),
        "selection_coordinate": "geometric_mean_of_valid_positive_coupon_estimates",
    }


class DesignBlocked(RuntimeError):
    """A pre-execution design stop. NOT a scientific disposition: the primary experiment did not
    run and nothing is adjudicated."""

    def __init__(self, reason, detail=""):
        if reason not in DESIGN_BLOCKED_REASONS:
            raise ValueError("unknown design-blocked reason %r" % (reason,))
        self.reason = reason
        self.detail = detail
        super().__init__("%s: %s" % (reason, detail) if detail else reason)


def select_bridges(candidates, strict=True):
    """Apply FREEZE_RULE mechanically. Deterministic: no RNG, and every tie resolves on the
    integer geometry.

    Each candidate is a dict with ``w``, ``kz``, ``eligible`` and an ``xi_envelope`` mapping as
    returned by :func:`xi_envelope`. With ``strict`` (the default) a shortfall raises
    ``DesignBlocked`` with a frozen reason code rather than returning an underfilled selection.

    Four slots: one BELOW plus three INSIDE (erratum PE-20). The result is emitted in ASCENDING
    ``Xi_select`` so the frozen family is an ordered ladder for the monotonicity clause.
    """
    cands = [dict(c) for c in candidates]
    eligible = [c for c in cands if c.get("eligible")]
    if not eligible and strict:
        raise DesignBlocked("NO_CANDIDATE_ADMITTED_BY_REACHABLE_SET",
                            "no candidate survived the artifact and reachable-set gates")
    by_cat = {k: [c for c in eligible if c["xi_envelope"]["category"] == k]
              for k in XI_CATEGORIES}
    picked, seen = [], set()

    def take(sub, key, slot, provenance):
        if not sub:
            return False
        best = sorted(sub, key=key)[0]
        k = _cand_key(best)
        if k in seen:
            return False
        seen.add(k)
        row = dict(best)
        row["slot"] = slot
        row["slot_provenance"] = provenance
        row["category"] = best["xi_envelope"]["category"]
        picked.append(row)
        return True

    below_ok = take(by_cat["below"], lambda c: (-c["xi_envelope"]["Xi_select"], _cand_key(c)),
                    "below", "largest Xi_select whose whole envelope lies below the window")
    if strict and not below_ok:
        raise DesignBlocked("NO_UNAMBIGUOUS_BELOW_CANDIDATE",
                            "no eligible candidate's whole envelope lies below the window")
    inside = by_cat["inside"]
    if strict and len({_cand_key(c) for c in inside}) < N_LOG_TARGETS:
        raise DesignBlocked("INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES",
                            "%d unambiguous in-window candidates, %d required"
                            % (len({_cand_key(c) for c in inside}), N_LOG_TARGETS))
    for i, target in enumerate(log_targets()):
        take(inside, lambda c, t=target: (abs(math.log(c["xi_envelope"]["Xi_select"])
                                              - math.log(t)), _cand_key(c)),
             "inside_%d" % i, "nearest log-spaced in-window target %.9g" % target)
    if strict and len(picked) != N_FROZEN_BRIDGES:
        raise DesignBlocked("SELECTION_UNDERFILLED_AFTER_DEDUPLICATION",
                            "selected %d unique candidates, exactly %d required"
                            % (len(picked), N_FROZEN_BRIDGES))
    # ascending Xi_select, ties on the integer geometry — an ordered ladder for clause 5
    picked.sort(key=lambda c: (c["xi_envelope"]["Xi_select"], _cand_key(c)))
    for i, c in enumerate(picked):
        c["freeze_order"] = i
    # "above" survives only as a diagnostic
    diagnostics = [dict(c, category="above") for c in by_cat["above"]]
    if diagnostics:
        picked[0].setdefault("_diagnostics", {})
    return picked


def above_window_diagnostics(candidates):
    """Above-window candidates, retained as a DIAGNOSTIC category only (erratum PE-20). They fill
    no slot and cannot be selected."""
    return [{"w": int(c["w"]), "kz": int(c["kz"]),
             "Xi_select": c["xi_envelope"]["Xi_select"],
             "eligible": bool(c.get("eligible")),
             "role": "DIAGNOSTIC_ABOVE_WINDOW_NOT_A_SELECTION_SLOT"}
            for c in candidates if c.get("xi_envelope", {}).get("category") == "above"]


# ==========================================================================================
# 8b. EXECUTABLE FORCING-INVARIANCE AND RESOLUTION-CONSISTENCY GATES (errata PE-28, PE-29)
# ==========================================================================================
# Superseded: the x0.5/x1/x2 ladder was scheduled in the matrix and described in the protocol,
# and NOTHING EVALUATED IT; the resolution tolerance was used only to widen an interval. This is
# the control whose failure produced INVALID_EXECUTION in RP-D-LC-001, so scheduling the rows
# without adjudicating them would have reproduced the 001 failure mode one level up.
#
# A FAILED GATE MAKES THE CANDIDATE UNAVAILABLE. It never widens an envelope.

#: The frozen componentwise quantities and the expected-zero subset are declared with the rest of
#: the family-specific required sets below (errata PE-62 … PE-64), so one set can never change
#: meaning by phase.
#:
#: The boundary-level quantities whose forcing stability must be established BEFORE any of them
#: informs artifact admission, a c interval, a Xi envelope, admission, a category or a selection.
#: Superseded by CANDIDATE_BOUNDARY_FORCING_QUANTITIES, which names each form exactly: C4 declared
#: this abstract four-name list and then adjudicated c_field alone (erratum PE-62).
BOUNDARY_STABILITY_QUANTITIES = ("R", "s", "c_field", "Xi")

FORCING_GATE_STATUS = ("PASS", "FAIL", "NOT_APPLICABLE", "INCOMPLETE")


def _reduced(value, g):
    return _finite(value, "value") / _finite(g, "g")


def componentwise_forcing_gate(quantity, samples, expected_zero=False, zero_scale=None,
                               tol=TOL_LINEARITY_REL, zero_tol=None,
                               forcing_independent=False):
    """Adjudicate one quantity across a forcing ladder.

    ``samples`` is an iterable of ``{"forcing_level", "g", "value", "case_id", "record_sha256"}``
    from **NORMAL** records only. Fixed-step audits are never observations (erratum PE-30).

    For a Stokes-proportional quantity the verdict is the exact frozen componentwise relative
    spread of ``value/g``. For an expected-zero quantity the mean is not a denominator: magnitude
    and consistency are judged against ``zero_scale`` with ``zero_tol``.

    ``forcing_independent`` (erratum PE-62) selects the frozen DIRECT relative-spread rule for a
    dimensionless or forcing-independent quantity — ``R``, ``s``, ``c``, a conductance, an area or
    actual ``Xi``. Such a quantity is compared as measured and is never divided by ``g``; dividing
    it would manufacture a spread out of the ladder itself.
    """
    rows = [dict(s) for s in samples]
    out = {
        "quantity": quantity, "expected_zero": bool(expected_zero),
        "forcing_independent": bool(forcing_independent),
        "reduction_rule": ("FROZEN_DIRECT_RELATIVE_SPREAD_NOT_DIVIDED_BY_g"
                           if forcing_independent else "VALUE_DIVIDED_BY_g"),
        "tolerance": (zero_tol if expected_zero else tol),
        "levels": sorted({r["forcing_level"] for r in rows}),
        "missing_levels": [lv for lv in FORCING_LEVELS
                           if lv not in {r["forcing_level"] for r in rows}],
        "case_ids": assert_flat_id_list([r["case_id"] for r in rows], "forcing gate case_ids"),
        "record_sha256": assert_flat_hash_list([r["record_sha256"] for r in rows],
                                               "forcing gate record hashes"),
        "reduced": None, "spread": None, "max_abs": None, "range": None,
        "status": "INCOMPLETE", "pass": None, "reason": None,
    }
    if forcing_independent and expected_zero:            # pragma: no cover - guarded by callers
        raise ValueError("a forcing-independent quantity cannot also be an expected-zero one")
    missing = out["missing_levels"]
    if missing:
        out["reason"] = "missing forcing level(s) %r; the ladder is incomplete" % (missing,)
        out["pass"] = False
        return out
    reduced = {}
    for r in rows:
        reduced[r["forcing_level"]] = (
            _finite(r["value"], "%s at %s" % (quantity, r["forcing_level"]))
            if forcing_independent
            else _finite(_reduced(r["value"], r["g"]),
                         "%s/g at %s" % (quantity, r["forcing_level"])))
    out["reduced"] = reduced
    vals = [reduced[lv] for lv in FORCING_LEVELS]
    if expected_zero:
        scale = abs(_finite(zero_scale, "zero_scale"))
        if scale == 0.0:
            raise ValueError("an expected-zero forcing gate needs a nonzero absolute scale")
        if zero_tol is None:
            raise ValueError("an expected-zero forcing gate needs its frozen zero tolerance")
        out["max_abs"] = max(abs(v) for v in vals)
        out["range"] = max(vals) - min(vals)
        out["zero_scale"] = scale
        out["magnitude_pass"] = bool(out["max_abs"] / scale <= zero_tol)
        out["consistency_pass"] = bool(abs(out["range"]) / scale <= zero_tol)
        out["pass"] = bool(out["magnitude_pass"] and out["consistency_pass"])
        out["status"] = "PASS" if out["pass"] else "FAIL"
        out["reason"] = ("expected-zero quantity: judged on the frozen absolute scale with "
                         "separate magnitude and consistency verdicts; never divided by its own "
                         "mean")
        return out
    mean = sum(vals) / len(vals)
    if mean == 0.0:
        out["pass"] = False
        out["status"] = "FAIL"
        out["reason"] = ("a nonzero Stokes-proportional quantity reduced to a zero mean; it "
                         "cannot be adjudicated by a relative spread and is not admitted")
        return out
    out["spread"] = _finite((max(vals) - min(vals)) / abs(mean), "%s spread" % quantity)
    out["pass"] = bool(out["spread"] <= tol)
    out["status"] = "PASS" if out["pass"] else "FAIL"
    out["reason"] = ("exact frozen %s relative spread of %s across the ladder, against "
                     "TOL_LINEARITY_REL"
                     % (("direct" if forcing_independent else "componentwise"),
                        quantity if forcing_independent else quantity + "/g"))
    return out


# ---- family-specific REQUIRED SETS (errata PE-62, PE-63, PE-64, PE-66) -----------------------
# One set whose meaning changes by phase is how C4 lost R, s, A1, A2 and actual Xi: PE-47 declared
# them required, and the only boundary gate ever built was c_field. Each family below names its
# own exact set, and ``exact_set_verdict`` asserts EQUALITY between required and adjudicated —
# never a nonempty intersection and never a subset.

#: P0, reference-blocked family. Volume flux, the conservation-supporting mass-flux diagnostic,
#: the node-to-node pressure drop, the conductance and the exact frozen outlet share.
P0_REFERENCE_FORCING_QUANTITIES = ("Q_reference_blocked", "Q_mass_reference_blocked",
                                   "dP_reference_blocked", "C_reference_blocked",
                                   "s_reference_blocked")
#: P0, axial-coupon family, per level and orientation.
P0_COUPON_FORCING_QUANTITIES = ("Q_axial_coupon", "dP_axial_coupon", "C_axial_coupon")
P0_COUPON_LEVELS = ("high", "low")
P0_COUPON_ORIENTATIONS = ("x", "y")

#: The reference-blocked fixture carries NO bridge and therefore NO lateral pressure faces, so no
#: field-contrast or area quantity is defined on it. The contrast and areas that later supply
#: candidate truth come from the candidate BLOCKED MIRROR and are adjudicated in the candidate
#: boundary set. Declared explicitly so the empty set is a recorded fact, not an omission.
P0_REFERENCE_CONTRAST_QUANTITIES = ()
P0_REFERENCE_CONTRAST_APPLICABILITY = (
    "the reference-blocked fixture has no bridge, hence no y_face1/y_face2 pressure faces and no "
    "field_contrast; A1, A2, A_field and c_field are candidate-blocked-mirror quantities and are "
    "adjudicated in CANDIDATE_BOUNDARY_FORCING_QUANTITIES"
)

#: P0 resolution set: the reference-blocked quantities and every axial-coupon conductance.
P0_REFERENCE_RESOLUTION_QUANTITIES = ("Q_reference_blocked", "dP_reference_blocked",
                                      "C_reference_blocked", "s_reference_blocked")
P0_COUPON_RESOLUTION_QUANTITIES = ("C_axial_coupon",)

#: The exact CANDIDATE COMPONENT set (erratum PE-62 §6.2). Each member is Stokes-proportional and
#: is divided by g. ``q_lat_mass`` uses an axial MASS-flux scale and never Q_volume (PE-48).
CANDIDATE_COMPONENT_FORCING_QUANTITIES = ("Q_open", "Q_blocked", "dP_open", "dP_blocked",
                                          "q_lat_mass", "delta_p_lateral")
#: Retained under its C4 name so a record bound to the superseded set stays interpretable.
COMPONENTWISE_QUANTITIES = CANDIDATE_COMPONENT_FORCING_QUANTITIES
EXPECTED_ZERO_QUANTITIES = ("q_lat_mass", "delta_p_lateral")

#: The exact CANDIDATE BOUNDARY set (erratum PE-62 §6.3). Every member is dimensionless or
#: forcing-independent and is judged by the frozen DIRECT relative-spread rule.
CANDIDATE_BOUNDARY_FORCING_QUANTITIES = ("R_identical", "s_blocked", "s_open", "c_field",
                                         "A1", "A2", "A_field", "A_series_inverse", "Xi_actual")
#: Exact frozen definitions of the two aggregate area quantities, so neither can be met by a
#: similarly named surrogate.
AGGREGATE_AREA_DEFINITIONS = {
    "A_field": "A1 + A2 — the declared aggregate of the frozen resolution table",
    "A_series_inverse": ("1/A1 + 1/A2 — the exact aggregate that multiplies G_bridge_coupon to "
                         "form actual Xi"),
}
ACTUAL_XI_DEFINITION = ("Xi = G_bridge_coupon * (1/A1 + 1/A2), built from EXACTLY matched "
                        "candidate, resolution and forcing records. Raw G_bridge is never gated "
                        "under the name Xi (errata PE-49, PE-62).")

#: The exact CANDIDATE RESOLUTION set (erratum PE-66 §7.2).
CANDIDATE_RESOLUTION_QUANTITIES = ("R_identical", "s_blocked", "s_open", "c_field",
                                   "A1", "A2", "A_field", "A_series_inverse",
                                   "C_blocked", "C_open", "G_bridge_coupon", "Xi_actual")
#: The artifact point estimate is |R_identical - 1|, a monotone function of a gated quantity, so
#: it is covered by the ``R_identical`` gate rather than declared again as a surrogate.
ARTIFACT_POINT_ESTIMATE_COVERAGE = (
    "the selected artifact point estimate is |R_identical - 1| and is therefore adjudicated by "
    "the R_identical forcing and resolution gates; it is not a distinct decision quantity and is "
    "not re-declared as one")

#: Retained under its C4 name. Its C4 value is superseded by the family-specific sets above.
REQUIRED_FORCING_QUANTITIES = CANDIDATE_COMPONENT_FORCING_QUANTITIES


def _base_quantity(name):
    return name.split("@")[0]


def exact_set_verdict(gates, required, resolutions=SCIENTIFIC_RESOLUTIONS, family=None,
                      kind="forcing"):
    """EXACT completeness (erratum PE-64 §6.4).

    Asserts EQUALITY between the required quantity set and the actually adjudicated set. A
    nonempty intersection, a subset, a quantity present at only one or two forcing levels, a gate
    at only one resolution and a similarly named surrogate are all failures.
    """
    gs = [dict(g) for g in gates]
    want = sorted(set(required))
    present = sorted({_base_quantity(g["quantity"]) for g in gs})
    missing = sorted(set(want) - set(present))
    unexpected = sorted(set(present) - set(want))
    per_res, missing_levels = {}, {}
    for S in resolutions:
        have = {_base_quantity(g["quantity"]) for g in gs
                if g["quantity"].endswith("@S%d" % S)}
        per_res["S%d" % S] = sorted(set(want) - have)
    missing_res = sorted({q for v in per_res.values() for q in v})
    for g in gs:
        lv = g.get("missing_levels") or []
        if lv:
            missing_levels[g["quantity"]] = list(lv)
    failed = sorted(g["quantity"] for g in gs if g["pass"] is not True)
    complete = not missing and not unexpected and not missing_res and not missing_levels
    return {
        "family": family, "kind": kind,
        "n_gates": len(gs), "gates": gs,
        "required_quantities": want,
        "present_quantities": present,
        "missing_quantities": missing,
        "unexpected_quantities": unexpected,
        "missing_per_resolution": per_res,
        "missing_resolutions": missing_res,
        "missing_levels": missing_levels,
        "failed_quantities": failed,
        "complete": bool(complete),
        "pass": bool(gs) and complete and not failed,
        "rule": ("the adjudicated set must EQUAL the required set at EVERY resolution, every "
                 "quantity must carry all three forcing levels where a ladder applies, and every "
                 "gate must pass on its own. A nonempty intersection, a subset, a single-"
                 "resolution gate and a similarly named surrogate are failures (errata PE-28, "
                 "PE-47, PE-62, PE-64)"),
    }


def forcing_invariance_verdict(gates, required=None, resolutions=SCIENTIFIC_RESOLUTIONS,
                               family=None):
    """Aggregate componentwise gates. Every component must pass on its own: an aggregate that
    cancels while one component drifts is NOT a pass."""
    if required is None:
        required = CANDIDATE_COMPONENT_FORCING_QUANTITIES
    return exact_set_verdict(gates, required, resolutions=resolutions, family=family,
                             kind="forcing")


def resolution_consistency_gate(quantity, coarse, fine, bridge=None):
    """Adjudicate one quantity across S_COARSE and S_FINE as an explicit PASS/FAIL.

    ``coarse``/``fine`` are ``{"value", "case_id", "record_sha256"}`` from NORMAL records. The two
    values are first mapped into the frozen COMPARISON COORDINATE ``value / S**n`` (erratum
    PE-66), whose exponent is derived from the frozen forcing law and exact geometric similarity
    and is 0 for every dimensionless quantity. The tolerance is the ex-ante feature envelope for
    the quantity's own governing family. A failure makes the candidate UNAVAILABLE; it is never
    absorbed into a wider interval (erratum PE-29).

    This remains a TWO-RESOLUTION CONSISTENCY TEST, not a convergence-order estimate.
    """
    family = RESOLUTION_GOVERNING_FAMILY[quantity]
    needs_bridge = quantity in BRIDGE_DEPENDENT_QUANTITIES
    tol = resolution_consistency_tolerance(quantity, bridge if needs_bridge else None)
    raw_a = _finite(coarse["value"], "%s at S_COARSE" % quantity)
    raw_b = _finite(fine["value"], "%s at S_FINE" % quantity)
    a = resolution_comparison_coordinate(quantity, raw_a, S_COARSE)
    b = resolution_comparison_coordinate(quantity, raw_b, S_FINE)
    denom = (abs(a) + abs(b)) / 2.0
    out = {
        "quantity": quantity, "family": family,
        "features": list(RESOLUTION_GOVERNING_FEATURES[quantity]),
        "S_coarse": S_COARSE, "S_fine": S_FINE,
        "raw_value_coarse": raw_a, "raw_value_fine": raw_b,
        "scaling_exponent": RESOLUTION_SCALING_EXPONENT[quantity],
        "comparison_coordinate": "value / S**%d" % RESOLUTION_SCALING_EXPONENT[quantity],
        "comparison_coordinate_provenance": RESOLUTION_SCALING_PROVENANCE,
        "value_coarse": a, "value_fine": b,
        "tolerance": tol,
        "case_ids": assert_flat_id_list([coarse["case_id"], fine["case_id"]],
                                        "resolution gate case_ids"),
        "record_sha256": assert_flat_hash_list([coarse["record_sha256"], fine["record_sha256"]],
                                               "resolution gate record hashes"),
        "kind": "TWO_RESOLUTION_CONSISTENCY_TEST_NOT_A_CONVERGENCE_ORDER_ESTIMATE",
    }
    if denom == 0.0:
        out.update(discrepancy=None, **{"pass": False}, status="FAIL",
                   reason="both resolutions returned zero; the quantity cannot be adjudicated")
        return out
    out["discrepancy"] = _finite(abs(a - b) / denom, "%s resolution discrepancy" % quantity)
    out["pass"] = bool(out["discrepancy"] <= tol)
    out["status"] = "PASS" if out["pass"] else "FAIL"
    out["reason"] = ("symmetric relative discrepancy in the frozen comparison coordinate, against "
                     "the ex-ante feature envelope for family %r" % family)
    return out


def resolution_consistency_verdict(gates, required=None, family=None):
    """Aggregate resolution gates with EXACT completeness (erratum PE-66)."""
    if required is None:
        required = CANDIDATE_RESOLUTION_QUANTITIES
    out = exact_set_verdict(gates, required, resolutions=(), family=family, kind="resolution")
    out["rule"] = ("the adjudicated set must EQUAL the required set, and a failed consistency "
                   "gate makes the candidate UNAVAILABLE — it is never absorbed into a wider "
                   "interval, replaced by the uncertainty envelope, or reported only as a "
                   "post-selection diagnostic (errata PE-29, PE-66)")
    return out


# ==========================================================================================
# 9. DECISION SEMANTICS — carried forward from 001, fail-closed
# ==========================================================================================
# Execution validity is the first gate and it dominates. If any clause-1 control fails, the
# disposition is INVALID_EXECUTION, clauses 2-7 are NOT REACHED (adjudicative: false), the
# cross-model transfer question stays UNADJUDICATED, and no negative cross-model claim may be
# made. Recovery numbers may be reported only as clearly labelled diagnostics.

DISPOSITIONS = (
    "CROSS_MODEL_RECOVERY",
    "MECHANISM_ONLY",
    "NO_CROSS_MODEL_TRANSFER",
    "INVALID_EXECUTION",
    "DESIGN_MISSED_TARGET",
)

#: A pre-execution stop, NOT a scientific disposition: no solve of the primary experiment ran.
DESIGN_BLOCKED = "DESIGN_BLOCKED_PRE_EXECUTION"

#: Execution-validity controls, in evaluation order. ``required`` controls roll into clause 1.
VALIDITY_CONTROLS = (
    ("convergence", True, "every scientific run converges before MAX_STEPS"),
    ("low_mach_regime", True,
     "measured max ||u|| over FLUID NODES ONLY from ux, uy AND uz gives max Mach <= TOL_MACH "
     "(a Mach condition ONLY — not a Re condition); the a-priori design scale is not this control"),
    ("componentwise_creeping_flow_control", True,
     "every Stokes-proportional component divided by g has relative spread <= TOL_LINEARITY_REL "
     "across the resolution's own x0.5/x1/x2 ladder"),
    ("mass_conservation", True,
     "plane-to-plane sum(rho*u_x) spread over EXACTLY the nine adjudicative planes cons_0..cons_8 "
     "<= TOL_MASS_REL — MEASURED, not proxied, and never weighted by a named measurement plane"),
    ("bridge_mass_flux_consistency", True,
     "state-aware and zero-safe: NOT_APPLICABLE with no bridge or a blocked connection; absolute "
     "imbalance normalised by the axial mass flux at zero lateral driver; a hybrid absolute + "
     "relative gate for a driven bridge, the relative part admitted only above the frozen floor"),
    ("topology", True,
     "exact mirror symmetry, one connected fluid domain, no periodic lateral bypass, axial end "
     "caps solid, blocked/open delta exactly the duct footprint, lanes joined in the lane region "
     "only when open"),
    ("negative_control_axial_artifact", True,
     "identical-path |R - 1| <= ARTIFACT_BUDGET_R_ABS at both resolutions for the frozen bridge"),
    ("reachable_set_admission", True,
     "the frozen bridge satisfies the admission inequality with the frozen safety margin"),
    ("measurement_plane_invariance", True, "|s(x_meas_a) - s(x_meas_b)| <= TOL_PLANE_REL"),
    ("resolution_consistency", True,
     "S_COARSE vs S_FINE agreement within the ex-ante derived per-quantity tolerance — a frozen "
     "CONSISTENCY test, NOT an asymptotic convergence-order estimate"),
    ("route_a_isolation_gate", True,
     "Arm J: |R_obstructed/R_nominal - 1| <= TOL_RETURN_PATH_R_REL and |ds| <= "
     "TOL_RETURN_PATH_S_ABS in every decision-carrying case"),
    ("coarse_graining_surface_stability", True,
     "the frozen node-surface offsets do not change window membership, factor-of-two status or "
     "the classification"),
    ("boundary_inference_forcing_stability", True,
     "R, s, c_hat, Xi_hat stable across the forcing ladder within TOL_LINEARITY_REL"),
    ("volume_flux_uniformity", False,
     "DIAGNOSTIC continuity with 001's frozen proxy; never decides an execution"),
    ("backend_cross_check", False,
     "reference/Taichi where available; absent -> NOT PERFORMED, never 'passed'"),
    ("determinism", True, "an identical configuration reproduces the compact record exactly"),
)

#: The seven decision clauses, in execution order. Clause 1 is execution validity and dominates.
DECISION_CLAUSES = (
    {"n": 1, "name": "execution_valid",
     "inputs": "every required VALIDITY_CONTROLS entry",
     "tolerance": "each control's own frozen tolerance",
     "authority": "PROTOCOL.md §9-§10",
     "fail": "INVALID_EXECUTION; clauses 2-7 NOT REACHED",
     "later_clauses_adjudicative_after_failure": False},
    {"n": 2, "name": "window_population",
     "inputs": "Xi_field per frozen bridge, per resolution",
     "tolerance": ">=3 cases with XI_WINDOW_LO <= Xi_field <= XI_WINDOW_HI at EACH resolution",
     "authority": "WP6-LC-IDENT post-hoc 1 % continuous window, copied not restated",
     "fail": "DESIGN_MISSED_TARGET",
     "later_clauses_adjudicative_after_failure": False},
    {"n": 3, "name": "factor_of_two_recovery",
     "inputs": "Xi_hat, Xi_field for every window case",
     "tolerance": "inverse status == 'ok' and 0.5 <= Xi_hat/Xi_field <= 2.0",
     "authority": "PROTOCOL.md §10", "fail": "MECHANISM_ONLY or NO_CROSS_MODEL_TRANSFER",
     "later_clauses_adjudicative_after_failure": True},
    {"n": 4, "name": "contrast_recovery",
     "inputs": "c_hat, c_field for every window case",
     "tolerance": "sign(c_hat) == sign(c_field) and |c_hat - c_field| <= 0.10",
     "authority": "PROTOCOL.md §10", "fail": "MECHANISM_ONLY or NO_CROSS_MODEL_TRANSFER",
     "later_clauses_adjudicative_after_failure": True},
    {"n": 5, "name": "monotonicity",
     "inputs": "Xi_hat vs Xi_field over the frozen bridge family, per resolution",
     "tolerance": "strictly monotone", "authority": "PROTOCOL.md §10",
     "fail": "NO_CROSS_MODEL_TRANSFER",
     "later_clauses_adjudicative_after_failure": True},
    {"n": 6, "name": "path_swap",
     "inputs": "R, s, c_field, c_hat, Xi_field, Xi_hat under the exact swap transform",
     "tolerance": "sign of (s - 1/2), c_field and c_hat reversed; R, Xi_field, Xi_hat preserved "
                  "within TOL_SWAP_R_REL / TOL_SWAP_XI_REL",
     "authority": "PROTOCOL.md §10", "fail": "NO_CROSS_MODEL_TRANSFER",
     "later_clauses_adjudicative_after_failure": True},
    {"n": 7, "name": "resolution_stability_of_classification",
     "inputs": "the clause-2..6 classification at S_COARSE and S_FINE",
     "tolerance": "identical classification", "authority": "PROTOCOL.md §10",
     "fail": "NO_CROSS_MODEL_TRANSFER",
     "later_clauses_adjudicative_after_failure": True},
)


def decide(controls, clauses):
    """Frozen decision, fail-closed.

    ``controls`` maps a VALIDITY_CONTROLS name to True (pass), False (fail) or None
    (NOT_EVALUATED). ``clauses`` maps clause numbers 2..7 to computed booleans. A required
    control that is None is fail-closed: it cannot pass an execution.
    """
    required = [n for n, req, _ in VALIDITY_CONTROLS if req]
    failed = [n for n in required if controls.get(n) is False]
    not_eval = [n for n in required if controls.get(n) is None]
    valid = not failed and not not_eval
    out = {
        "execution_valid": valid,
        "failed_controls": failed,
        "not_evaluated_required_controls": not_eval,
        "primary_cause": (failed[0] if failed else (not_eval[0] if not_eval else None)),
        "clauses": [],
        "cross_model_transfer_adjudicated": False,
    }
    if not valid:
        out["disposition"] = "INVALID_EXECUTION"
        out["evidence_use"] = "DIAGNOSTIC_ONLY_INVALID_EXECUTION"
        for spec in DECISION_CLAUSES:
            n = spec["n"]
            if n == 1:
                out["clauses"].append({"n": 1, "name": spec["name"], "pass": False,
                                       "adjudicative": True, "status": "FAILED"})
                continue
            out["clauses"].append({
                "n": n, "name": spec["name"], "pass": None, "adjudicative": False,
                "status": "DIAGNOSTIC_ONLY_NOT_REACHED",
                "diagnostic_computed_pass": (None if clauses.get(n) is None
                                             else bool(clauses.get(n))),
            })
        return out

    out["clauses"].append({"n": 1, "name": "execution_valid", "pass": True,
                           "adjudicative": True, "status": "PASSED"})
    stop = False
    for spec in DECISION_CLAUSES[1:]:
        n = spec["n"]
        got = clauses.get(n)
        if stop:
            out["clauses"].append({"n": n, "name": spec["name"], "pass": None,
                                   "adjudicative": False,
                                   "status": "DIAGNOSTIC_ONLY_NOT_REACHED",
                                   "diagnostic_computed_pass": (None if got is None
                                                                else bool(got))})
            continue
        ok = bool(got)
        out["clauses"].append({"n": n, "name": spec["name"], "pass": ok, "adjudicative": True,
                               "status": "PASSED" if ok else "FAILED"})
        if not ok and not spec["later_clauses_adjudicative_after_failure"]:
            stop = True
    passes = {c["n"]: c["pass"] for c in out["clauses"]}
    if passes.get(2) is False:
        out["disposition"] = "DESIGN_MISSED_TARGET"
    elif all(passes.get(n) for n in range(1, 8)):
        out["disposition"] = "CROSS_MODEL_RECOVERY"
        out["cross_model_transfer_adjudicated"] = True
    elif passes.get(5) and passes.get(6) and passes.get(7) and not (passes.get(3)
                                                                    and passes.get(4)):
        out["disposition"] = "MECHANISM_ONLY"
        out["cross_model_transfer_adjudicated"] = True
    else:
        out["disposition"] = "NO_CROSS_MODEL_TRANSFER"
        out["cross_model_transfer_adjudicated"] = True
    out["evidence_use"] = ("ADJUDICATED" if out["cross_model_transfer_adjudicated"]
                           else "DIAGNOSTIC_ONLY")
    return out


# ==========================================================================================
# 10. EXECUTION PHASES AND THE PLANNED MATRIX
# ==========================================================================================

EXECUTION_PHASES = (
    {"id": "P0", "name": "common blocked characterisation",
     "purpose": "the reference-blocked mirror fixture over the FULL forcing ladder at both "
                "resolutions, the axial coupons over the full ladder in both lattice "
                "orientations, and the scheduled tau cross-check",
     "reveals": "reference-blocked internals and coupon conductances only",
     "prerequisite": None, "authorised_now": False},
    {"id": "P1a", "name": "central identical-path screen",
     "purpose": "central identical-path blocked/open pairs for ALL declared scientific "
                "candidates at both resolutions",
     "reveals": "identical-path observables only; NO mirror recovery case is run or inspected",
     "prerequisite": "P0", "authorised_now": False},
    {"id": "P1b", "name": "identical-path forcing extension and continuation",
     "purpose": "reject obvious central failures, then run the x0.5 and x2 extensions for every "
                "candidate that could still be selected, plus the frozen continuation runs the "
                "numerical-discrepancy method needs. FINAL artifact admission uses all three "
                "forcing levels at both resolutions",
     "reveals": "identical-path observables only",
     "prerequisite": "P1a", "authorised_now": False},
    {"id": "P2a", "name": "coupon ladders and candidate blocked-mirror characterisation",
     "purpose": "full forcing ladders for the bridge coupons of surviving candidates, and "
                "candidate-specific BLOCKED MIRROR characterisation over the same "
                "forcing/resolution set — the measured basis for the contrast interval",
     "reveals": "bridge coupon conductances and blocked-mirror internals. NO candidate OPEN "
                "mirror recovery case is run",
     "prerequisite": "P1b", "authorised_now": False},
    {"id": "P2b", "name": "admissibility, selection and proposed freeze",
     "purpose": "apply every forcing, resolution, artifact, reachability and selection rule; "
                "produce the proposed bridge freeze and the INSTANTIATED P3/P4 matrix; stop for "
                "a second exact-head review",
     "reveals": "nothing new — no solve; arithmetic over P0/P1/P2a records only",
     "prerequisite": "P2a", "authorised_now": False},
    {"id": "P3", "name": "primary mirror / path-swap experiment",
     "purpose": "the experiment the tranche exists to perform",
     "reveals": "the primary observables — may execute only from an expressly approved frozen "
                "head, after the second review",
     "prerequisite": "P2b", "authorised_now": False},
    {"id": "P4", "name": "Arm J return-path nuisance isolation",
     "purpose": "repeat the plenum obstruction for every decision-carrying case and gate Route-A "
                "isolation on R and s",
     "reveals": "obstructed counterparts of the primary cases",
     "prerequisite": "P3", "authorised_now": False},
)

PHASE_IDS = tuple(p["id"] for p in EXECUTION_PHASES)
SOLVING_PHASE_IDS = ("P0", "P1a", "P1b", "P2a", "P3", "P4")     # P2b does no solving

#: Arm J, preserved from the 001 programme and NOT silently dropped to shrink the matrix.
ARM_J = {
    "purpose": "isolate the common-return-plenum nuisance: 001 erratum E1 showed the ABSOLUTE "
               "lane conductance is not separable from the plenum (-1.84 % / -1.88 % under an "
               "extreme obstruction) while the pressure-normalised ratio R moved only 3.7e-4. "
               "Arm J converts that single smoke-scale probe into a gated control.",
    "relationship_to_corrected_geometry": "unchanged by the bridge redesign — the obstruction "
               "touches only plenum voxels and preserves both fixture symmetries. The corrected "
               "blocked reference makes it STRICTER, because the ports are now common-mode and "
               "cannot mask a return-path movement.",
    "status": "decision_bearing",
    "gate": {"R_rel": TOL_RETURN_PATH_R_REL, "s_abs": TOL_RETURN_PATH_S_ABS},
    "fail_semantics": "INVALID_EXECUTION — never a relaxed second tolerance and never a switch "
                      "to Route B, which remains unauthorized",
    "ordering": "after P3's nominal cases, before adjudication",
    "planned_solves": N_FROZEN_BRIDGES * 2 * len(SCIENTIFIC_RESOLUTIONS),
    "matrix": "each frozen bridge x {blocked, open} x {S=2, S=3}, central forcing, obstructed",
}

#: Retained-record schemas, named so a row states exactly what it must produce.
RECORD_SCHEMAS = {
    "full_case": "named axial planes + the nine conservation planes + lane planes + transverse "
                 "planes + conservation + transverse_conservation + mach + observables",
    "coupon": "duct conductance Q/(g L) with its plane records and mach",
    "case_plus_boundary_and_truth": "full_case, then the six-key boundary record, then field "
                                    "truth — built and recorded in that order",
    "fixed_step_audit": "full_case from a FIXED-STEP re-execution with min_steps = max_steps = "
                        "CHECK*ceil(1.5*base_steps/CHECK), plus the base linkage and both solver "
                        "configurations",

    "obstructed": "full_case plus the induced movements in R, s, c_hat and Xi_hat",
}


#: Kinds whose output can decide admission, classification or selection. Every such row is paired
#: with its OWN fixed-step audit row (erratum PE-17): a bound measured on two geometric extremes
#: and applied to twelve candidates was an extrapolation, not a proof.
SELECTION_BEARING_KINDS = ("axial_coupon", "identical_path_control", "bridge_coupon",
                           "candidate_blocked_mirror", "reference_blocked_ladder")


def _case_id(row):
    """A stable, unique identifier built from the row's own configuration, INCLUDING the exact
    forcing rational (erratum PE-21). Deterministic and order-independent: two rows with the same
    id would denote the same run."""
    parts = [row["phase"], row["kind"], "S%d" % row["S"], row["forcing_level"]]
    fe = row.get("forcing_exact")
    if fe:
        parts.append("g%dov%d" % (fe["numerator"], fe["denominator"]))
    parts += ["tau%s" % ("%g" % row["tau_plus"]).replace(".", "p"), row["state"], row["variant"]]
    b = row.get("bridge")
    if isinstance(b, dict):
        parts.append("w%dkz%d" % (b["w"], b["kz"]))
    elif b:
        parts.append(str(b))
    for key, pre in (("coupon_level", "lvl"), ("coupon_orientation", "or"),
                     ("perturbation", "pert"), ("audit_mode", "audit")):
        if row.get(key):
            parts.append("%s-%s" % (pre, row[key]))
    if row.get("swapped"):
        parts.append("swapped")
    if row.get("obstructed"):
        parts.append("obstructed")
    if row.get("run_mode") == "FIXED_STEP_REEXECUTION_1P5X":
        parts.append("fixedstep")
    return ".".join(parts)


def _row(**kw):
    """One fully specified, uniquely executable matrix row (errata PE-10, PE-21)."""
    row = {
        "phase": None, "kind": None, "S": None, "forcing_level": None,
        "forcing_repr": None, "forcing_exact": None,
        "tau_plus": TAU_PLUS, "state": None, "variant": None, "bridge": None,
        "coupon_level": None, "coupon_orientation": None, "swapped": False,
        "perturbation": None, "obstructed": False, "audit_mode": None,
        "run_mode": "NORMAL", "audit_of_case_id": None, "replicate_of_case_id": None,
        "backend": "reference", "record_schema": None, "prerequisite": None,
        "class": None, "adaptive": False,
    }
    row.update(kw)
    S, level = row["S"], row["forcing_level"]
    if S is not None and level in FORCING_LEVELS:
        exact = forcing_exact_dict(S, level)
        if row["forcing_exact"] is None:
            row["forcing_exact"] = exact
        elif row["forcing_exact"] != exact:                  # pragma: no cover - guarded
            raise ValueError("row carries a forcing rational inconsistent with (S, level)")
        derived = repr(forcing_from_exact(row["forcing_exact"]))
        if row["forcing_repr"] is None:
            row["forcing_repr"] = derived                    # ALWAYS derived from the rational
        elif row["forcing_repr"] != derived:
            raise ValueError("row forcing_repr %r != repr(float(Fraction(%r)))"
                             % (row["forcing_repr"], row["forcing_exact"]))
    missing = [k for k in ("phase", "kind", "S", "forcing_level", "forcing_repr",
                           "forcing_exact", "state", "variant", "record_schema",
                           "class") if row[k] is None]
    if missing:
        raise ValueError("matrix row is under-specified, missing %r: %r" % (missing, row))
    row["case_id"] = _case_id(row)
    return row


def _audit_row(base):
    """The fixed-step re-execution paired with one selection-bearing row (erratum PE-16/PE-17)."""
    kw = {k: v for k, v in base.items() if k not in ("case_id", "class", "record_schema",
                                                     "run_mode", "audit_mode", "audit_of_case_id",
                                                     "prerequisite", "adaptive",
                                                     "forcing_repr")}
    return _row(audit_mode="fixed_step_1p5x", run_mode="FIXED_STEP_REEXECUTION_1P5X",
                audit_of_case_id=base["case_id"], record_schema="fixed_step_audit",
                prerequisite=base["phase"], adaptive=base["adaptive"],
                **{"class": base["class"] if base["class"] == "mandatory"
                   else base["class"]}, **kw)


def _with_audits(rows, audit_phase=None):
    """Emit each row followed by its own fixed-step audit where the row is selection-bearing."""
    out = []
    for r in rows:
        out.append(r)
        if r["kind"] in SELECTION_BEARING_KINDS and r["run_mode"] == "NORMAL":
            a = _audit_row(r)
            if audit_phase:
                a = dict(a)
                a["phase"] = audit_phase
                a.pop("case_id")
                a["case_id"] = _case_id(a)
            out.append(a)
    return out


def _matrix_rows():
    rows = []
    sci = SCIENTIFIC_BRIDGE_CANDIDATES

    # ---- P0: reference-blocked ladder, axial coupons (full ladder, BOTH orientations), tau ----
    p0 = []
    for S in SCIENTIFIC_RESOLUTIONS:
        for level in FORCING_LEVELS:
            p0.append(_row(phase="P0", kind="reference_blocked_ladder", S=S,
                           forcing_level=level, state="reference_blocked", variant="mirror",
                           record_schema="full_case", **{"class": "mandatory"}))
    for S in SCIENTIFIC_RESOLUTIONS:
        for level in FORCING_LEVELS:
            for coupon_level in ("high", "low"):
                for orient in ("x", "y"):
                    p0.append(_row(phase="P0", kind="axial_coupon", S=S, forcing_level=level,
                                   state="coupon", variant="axial_coupon",
                                   coupon_level=coupon_level, coupon_orientation=orient,
                                   record_schema="coupon", **{"class": "mandatory"}))
    rows += _with_audits(p0)
    for S in SCIENTIFIC_RESOLUTIONS:                    # the SCHEDULED tau cross-check (PE-12)
        rows.append(_row(phase="P0", kind="tau_cross_check", S=S, forcing_level="central",
                         tau_plus=TAU_CROSS_CHECK, state="reference_blocked", variant="mirror",
                         record_schema="full_case", **{"class": "mandatory"}))
    p0_base = next(r for r in rows if r["kind"] == "reference_blocked_ladder"
                   and r["S"] == S_COARSE and r["forcing_level"] == "central"
                   and r["run_mode"] == "NORMAL")
    rows.append(_row(phase="P0", kind="determinism_replicate", S=S_COARSE,
                     forcing_level="central", state="reference_blocked", variant="mirror",
                     replicate_of_case_id=p0_base["case_id"],
                     record_schema="full_case", **{"class": "diagnostic_only"}))

    # ---- P1a: central identical-path TRIAGE screen, ALL declared scientific candidates --------
    # P1a may REJECT (the point estimate alone can make success impossible, because every omitted
    # uncertainty term is non-negative) but may NEVER ADMIT: the final artifact upper bound needs
    # the fixed-step evidence that arrives in P1b (erratum PE-17).
    central = []
    for b in sci:
        for S in SCIENTIFIC_RESOLUTIONS:
            for connected in (False, True):
                central.append(_row(phase="P1a", kind="identical_path_control", S=S,
                                    forcing_level="central",
                                    state="open" if connected else "blocked",
                                    variant="identical", bridge=dict(b),
                                    record_schema="full_case", prerequisite="P0",
                                    **{"class": "mandatory"}))
    rows += central
    p1a_base = next(r for r in central if r["S"] == S_COARSE and r["state"] == "blocked"
                    and tuple(sorted(r["bridge"].items())) == tuple(sorted(dict(sci[0]).items())))
    rows.append(_row(phase="P1a", kind="determinism_replicate", S=S_COARSE,
                     forcing_level="central", state="blocked", variant="identical",
                     bridge=dict(sci[0]), replicate_of_case_id=p1a_base["case_id"],
                     record_schema="full_case", prerequisite="P0",
                     **{"class": "diagnostic_only"}))

    # ---- P1b: forcing extension, plus a fixed-step audit for EVERY artifact combination -------
    ext = []
    for b in sci:
        for S in SCIENTIFIC_RESOLUTIONS:
            for level in ("low", "high"):
                for connected in (False, True):
                    ext.append(_row(phase="P1b", kind="identical_path_control", S=S,
                                    forcing_level=level,
                                    state="open" if connected else "blocked",
                                    variant="identical", bridge=dict(b),
                                    record_schema="full_case", prerequisite="P1a",
                                    adaptive=True, **{"class": "conditional_on_P1a"}))
    rows += ext
    # every candidate x {blocked, open} x {S=2, S=3} x {low, central, high} gets its OWN evidence
    for base in central + ext:
        a = dict(_audit_row(base))
        a["phase"] = "P1b"
        a["prerequisite"] = "P1a"
        a["adaptive"] = True
        a["class"] = "conditional_on_P1a"
        a.pop("case_id")
        a["case_id"] = _case_id(a)
        rows.append(a)

    # ---- P2a: bridge coupon ladders + candidate BLOCKED MIRROR characterisation --------------
    p2a = []
    for b in sci:
        for S in SCIENTIFIC_RESOLUTIONS:
            for level in FORCING_LEVELS:
                p2a.append(_row(phase="P2a", kind="bridge_coupon", S=S, forcing_level=level,
                                state="coupon", variant="bridge_coupon", bridge=dict(b),
                                record_schema="coupon", prerequisite="P1b", adaptive=True,
                                **{"class": "conditional_on_P1b"}))
    for b in sci:
        for S in SCIENTIFIC_RESOLUTIONS:
            for level in FORCING_LEVELS:
                p2a.append(_row(phase="P2a", kind="candidate_blocked_mirror", S=S,
                                forcing_level=level, state="blocked", variant="mirror",
                                bridge=dict(b), record_schema="full_case", prerequisite="P1b",
                                adaptive=True, **{"class": "conditional_on_P1b"}))
    rows += _with_audits(p2a)
    return rows


def post_freeze_row_templates():
    """P3/P4 TEMPLATES. The real rows are instantiated only after the bridge selection is known
    (erratum PE-10) — see :func:`instantiate_post_freeze_matrix`."""
    rows = []
    slots = ["frozen_slot_%d" % i for i in range(N_FROZEN_BRIDGES)]
    for slot in slots:
        for S in SCIENTIFIC_RESOLUTIONS:
            for level in FORCING_LEVELS:
                rows.append(_row(phase="P3", kind="primary_mirror_open", S=S,
                                 forcing_level=level,
                                 state="open", variant="mirror", bridge=slot,
                                 record_schema="case_plus_boundary_and_truth",
                                 prerequisite="P2b", **{"class": "conditional_on_freeze"}))
    for slot in slots:
        for S in SCIENTIFIC_RESOLUTIONS:
            for connected in (False, True):
                rows.append(_row(phase="P3", kind="path_swap_control", S=S,
                                 forcing_level="central",
                                 state="open" if connected else "blocked", variant="mirror",
                                 swapped=True, bridge=slot, record_schema="full_case",
                                 prerequisite="P2b", **{"class": "conditional_on_freeze"}))
    for pert in sorted(PERTURBATIONS):
        for connected in (False, True):
            rows.append(_row(phase="P3", kind="adversarial_perturbation", S=S_FINE,
                             forcing_level="central",
                             state="open" if connected else "blocked", variant="mirror",
                             perturbation=pert, bridge=slots[0], record_schema="full_case",
                             prerequisite="P2b", **{"class": "conditional_on_freeze"}))
    # erratum PE-55: generated FROM the exact primary normal row, through the same audited-row
    # constructor used pre-freeze, so audit_of_case_id is never null.
    for S in SCIENTIFIC_RESOLUTIONS:
        base = next(r for r in rows if r["phase"] == "P3" and r["kind"] == "primary_mirror_open"
                    and r["S"] == S and r["forcing_level"] == "central"
                    and r["bridge"] == slots[0])
        a = dict(_audit_row(base))
        a["prerequisite"] = "P2b"
        a["class"] = "conditional_on_freeze"
        a.pop("case_id")
        a["case_id"] = _case_id(a)
        rows.append(a)
    p3_base = next(r for r in rows if r["phase"] == "P3" and r["kind"] == "primary_mirror_open"
                   and r["S"] == S_COARSE and r["forcing_level"] == "central"
                   and r["bridge"] == slots[0] and r["run_mode"] == "NORMAL")
    rows.append(_row(phase="P3", kind="determinism_replicate", S=S_COARSE,
                     forcing_level="central",
                     state="open", variant="mirror", bridge=slots[0],
                     replicate_of_case_id=p3_base["case_id"],
                     record_schema="full_case", prerequisite="P2b",
                     **{"class": "diagnostic_only"}))
    for slot in slots:
        for S in SCIENTIFIC_RESOLUTIONS:
            for connected in (False, True):
                rows.append(_row(phase="P4", kind="arm_j_return_path", S=S,
                                 forcing_level="central",
                                 state="open" if connected else "blocked", variant="mirror",
                                 obstructed=True, bridge=slot, record_schema="obstructed",
                                 prerequisite="P3", **{"class": "conditional_on_P3"}))
    return rows


def instantiate_post_freeze_matrix(frozen_bridges):
    """Bind the P3/P4 templates to the ACTUAL frozen bridges. Refuses unless exactly
    ``N_FROZEN_BRIDGES`` unique candidates are supplied — a missing slot is a design stop, never
    an improvised row. The result is hashed into the proposed freeze artifact."""
    bridges = [dict(b) for b in frozen_bridges]
    keys = [(int(b["w"]), int(b["kz"])) for b in bridges]
    if len(bridges) != N_FROZEN_BRIDGES or len(set(keys)) != N_FROZEN_BRIDGES:
        raise DesignBlocked("SELECTION_UNDERFILLED_AFTER_DEDUPLICATION",
                            "instantiation needs exactly %d unique frozen bridges, got %r"
                            % (N_FROZEN_BRIDGES, keys))
    slot_map = {"frozen_slot_%d" % i: bridges[i] for i in range(N_FROZEN_BRIDGES)}
    tpls = post_freeze_row_templates()
    remap = {}
    out = []
    for tpl in tpls:
        row = dict(tpl)
        row["bridge"] = dict(slot_map[row["bridge"]])
        row["bridge_slot"] = tpl["bridge"]
        row.pop("case_id")
        row["case_id"] = _case_id(row)
        remap[tpl["case_id"]] = row["case_id"]
        out.append(row)
    # rebind audit/replicate references to the INSTANTIATED case ids (errata PE-55, PE-59)
    for row in out:
        for k in ("audit_of_case_id", "replicate_of_case_id"):
            if row.get(k):
                if row[k] not in remap:
                    raise ValueError("row %r names %s=%r, which is not a template row"
                                     % (row["case_id"], k, row[k]))
                row[k] = remap[row[k]]
        row.pop("case_id")
        row["case_id"] = _case_id(row)
    ids = [r["case_id"] for r in out]
    if len(set(ids)) != len(ids):                            # pragma: no cover - guarded above
        raise ValueError("instantiated P3/P4 matrix has duplicate case ids")
    return out


def execution_matrix():
    """The complete PLANNED matrix with exact solve counts. NOTHING here has been executed.

    P0/P1a are unconditional; P1b/P2a are adaptive and are emitted at their MAXIMUM (every
    declared scientific candidate surviving); P3/P4 are TEMPLATES until the bridge selection is
    known, at which point ``instantiate_post_freeze_matrix`` binds them and the result is hashed
    into the proposed freeze artifact.
    """
    pre = _matrix_rows()
    post = post_freeze_row_templates()
    rows = pre + post
    ids = [r["case_id"] for r in rows]
    if len(set(ids)) != len(ids):                            # pragma: no cover - tested directly
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError("duplicate case ids in the planned matrix: %r" % (dup,))
    by_phase, by_class, by_kind = {}, {}, {}
    for r in rows:
        by_phase[r["phase"]] = by_phase.get(r["phase"], 0) + 1
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    mandatory = by_class.get("mandatory", 0)
    diagnostic = by_class.get("diagnostic_only", 0)
    total = len(rows)
    n_audit = sum(1 for r in rows if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X")
    # pressure-plane diagnostics re-read the frozen node-surface offsets of the SAME solution and
    # need no extra solve; they are counted separately so a solve budget is never overstated.
    # erratum PE-41: node-offset summaries are extracted from fields already computed, so there
    # is no diagnostic ROW and no provider call. Every row is either a normal solve or an audit.
    n_diag = 0
    n_normal = total - n_audit
    mandatory_with_replicates = mandatory + sum(
        1 for r in rows if r["class"] == "diagnostic_only" and r["phase"] in ("P0", "P1a"))
    return {
        "tranche": TRANCHE_ID,
        "correction_version": CORRECTION_VERSION,
        "solves_executed": 0,
        "rows": rows,
        "n_rows": total,
        "by_phase": by_phase,
        "by_class": by_class,
        "by_kind": by_kind,
        "planned_normal_solves": n_normal,
        "planned_fixed_step_audits": n_audit,
        "planned_pressure_plane_diagnostic_rows": n_diag,
        "planned_solver_invocations": n_normal + n_audit,
        "node_offset_policy": ("node-offset summaries are extracted from the SAME field as their "
                               "case and never increment the provider-call count (PE-41)"),
        "mandatory_minimum": mandatory_with_replicates,
        "conditional_minimum": 0,
        "adaptive_maximum": total,
        "diagnostic_replicates": diagnostic,
        "replicate_placement": (
            "three replicates, in P0, P1a and P3 — the three phases producing decision-bearing "
            "records from DISTINCT fixture families (reference-blocked, identical-path, mirror). "
            "P2a re-uses those families and P4 re-uses P3's fixtures with an obstruction, so a "
            "fourth would add no independent evidence. Each replicate repeats a case its own "
            "phase already runs, so P1a's is identical-path and cannot reveal a mirror "
            "observable."),
        "refused_after_earliest_stop": total - mandatory_with_replicates,
        "post_freeze_rows_are_templates": True,
        "n_post_freeze_template_rows": len(post),
        "ordering": "P0 -> P1a -> P1b -> P2a -> P2b (freeze, STOP for review) -> P3 -> P4; "
                    "within a phase, rows in the order emitted here",
        "early_stop": {
            "P1a": "a candidate whose central identical-path artifact upper bound already "
                   "exceeds ARTIFACT_BUDGET_R_ABS at either resolution is rejected and its P1b "
                   "and P2a rows are refused",
            "P1b": "if NO candidate meets the artifact budget across all three forcing levels at "
                   "both resolutions, stop with DESIGN_BLOCKED_PRE_EXECUTION "
                   "(NO_CANDIDATE_WITHIN_ARTIFACT_BUDGET)",
            "P2a": "a candidate failing forcing invariance or resolution consistency is not "
                   "eligible for selection",
            "P2b": "if the frozen rule cannot fill all %d unique slots from unambiguous "
                   "candidates, stop with a frozen DESIGN_BLOCKED reason code; do NOT improvise "
                   "a slot and do NOT re-select" % N_FROZEN_BRIDGES,
            "P3": "any run reaching MAX_STEPS is UNCONVERGED and stops the phase; no retry at a "
                  "looser tolerance",
            "P4": "a breached Route-A isolation bound gives INVALID_EXECUTION, never a relaxed "
                  "second tolerance",
        },
        "rerun_policy": "no statistical replicates — every case is deterministic with no RNG; the "
                        "three replicates exist solely to demonstrate byte-identical reproduction",
        "reuse_policy": "P3 re-uses P2a's candidate blocked-mirror records for the frozen "
                        "bridges rather than re-solving them: identical mask, identical forcing, "
                        "identical solver configuration, and the solver is deterministic. The "
                        "reuse is recorded per case, never silent.",
        "compute_note": "PLANNING INFORMATION ONLY, not an admission criterion: no wall-time "
                        "estimate is asserted, because none has been measured for this geometry",
    }


# ==========================================================================================
# 11. CANONICAL SERIALISATION, HASHING AND THE EXECUTION AUTHORITY
# ==========================================================================================

def _round(o, nd=_RECORD_DP, path="$"):
    if isinstance(o, bool):
        return o
    if isinstance(o, float):
        if not math.isfinite(o):
            raise NonFiniteValue(
                "refusing to serialise a non-finite number at %s: %r. A hashed artifact must "
                "not contain NaN or Infinity — scientific non-applicability is an explicit "
                "status string with null numeric fields (erratum PE-3)." % (path, o))
        return round(o, nd)
    if isinstance(o, dict):
        return {k: _round(v, nd, "%s.%s" % (path, k)) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round(v, nd, "%s[%d]" % (path, i)) for i, v in enumerate(o)]
    return o


def canonical_json(obj) -> str:
    """The one serialisation used for every hashed artifact: sorted keys, no insignificant
    whitespace, ASCII-escaped, floats rounded to a frozen precision so a record hash cannot move
    on a platform's last binary digit — and STRICTLY FINITE.

    ``NaN`` is not valid JSON, is not a number, and hashes to a stable digest for a value that
    carries no scientific content; a record could then be bound, verified and reproduced while
    containing a quantity that was never computed. Both this writer and ``json.dumps`` refuse it
    (erratum PE-3).
    """
    return json.dumps(_round(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def record_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _sha_file(rel):
    p = REPO_ROOT / rel
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def protocol_config():
    """The frozen machine-readable configuration. Hashing this is how a future stage proves it
    executed the configuration that was reviewed."""
    return {
        "schema_version": SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "errata": ERRATA_PATH,
        "superseded_reviews": [dict(r) for r in SUPERSEDED_REVIEWS],
        "program_id": PROGRAM_ID, "tranche_id": TRANCHE_ID,
        "question": QUESTION,
        "base_commit": BASE_COMMIT, "base_tree": BASE_TREE,
        "predecessor": PREDECESSOR,
        "claim_ceiling": list(CLAIM_CEILING),
        "solver": {"kernel": "brewer2026.lb_reference", "backend": "reference",
                   "tau_plus": TAU_PLUS, "tau_cross_check": TAU_CROSS_CHECK, "nu": NU,
                   "rtol": RTOL, "check": CHECK, "min_steps": MIN_STEPS, "max_steps": MAX_STEPS,
                   "convergence_audit_factor": CONVERGENCE_AUDIT_FACTOR,
                   "pressure_definition": "p = rho/3 - g*x, fluid-area averaged",
                   "boundary_mode": "ROUTE_A periodic body force + resolved common plenum",
                   "seed": None, "rng": "none"},
        "forcing": {
            "law": "g(S) = G_REF * (S_REF/S)^3",
            "S_ref": S_REF, "g_ref": G_REF,
            "central": {str(S): forcing_central(S) for S in SCIENTIFIC_RESOLUTIONS},
            "ladder": {str(S): forcing_ladder(S) for S in SCIENTIFIC_RESOLUTIONS},
            "factors": [str(f) for f in FORCING_FACTORS],
            "similarity": {
                "held_invariant": "Re_design = g L^3 / nu^2 with L = h_low * S",
                "value": {str(S): design_reynolds(S) for S in SCIENTIFIC_RESOLUTIONS},
                "diagnostic_mach_scale": {str(S): design_mach_scale(S)
                                          for S in SCIENTIFIC_RESOLUTIONS},
            },
            "reduction_vs_001": {"S2": vf001.G_PRIMARY / forcing_central(2),
                                 "S3": vf001.G_PRIMARY / forcing_central(3)},
        },
        "tolerances": {
            "TOL_MASS_REL": TOL_MASS_REL, "TOL_VOLUME_FLUX_REL": TOL_VOLUME_FLUX_REL,
            "TOL_LINEARITY_REL": TOL_LINEARITY_REL, "TOL_MACH": TOL_MACH,
            "TOL_CONVERGENCE_REL": TOL_CONVERGENCE_REL, "TOL_PLANE_REL": TOL_PLANE_REL,
            "TOL_SWAP_R_REL": TOL_SWAP_R_REL, "TOL_SWAP_XI_REL": TOL_SWAP_XI_REL,
            "TOL_RETURN_PATH_R_REL": TOL_RETURN_PATH_R_REL,
            "TOL_RETURN_PATH_S_ABS": TOL_RETURN_PATH_S_ABS,
            "TOL_NODE_OFFSET_R_REL": TOL_NODE_OFFSET_R_REL,
            "ARTIFACT_BUDGET_R_ABS": ARTIFACT_BUDGET_R_ABS,
            "NUMERICAL_DISCREPANCY_SAFETY_FACTOR": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
            "TOL_BRIDGE_LEAKAGE_REL": TOL_BRIDGE_LEAKAGE_REL,
            "LATERAL_FLUX_FLOOR_FACTOR": LATERAL_FLUX_FLOOR_FACTOR,
            "JUNCTION_ALLOWANCE": JUNCTION_ALLOWANCE,
            "REACHABLE_SAFETY_MARGIN_FRACTION": REACHABLE_SAFETY_MARGIN_FRACTION,
            "KAPPA_RES": KAPPA_RES,
        },
        "resolution_consistency": {
            "kind": "FROZEN_RESOLUTION_CONSISTENCY_TEST_NOT_A_CONVERGENCE_ORDER_ESTIMATE",
            "law": CHANNEL_ERR_LAW_PCT, "kappa": KAPPA_RES,
            "provenance": RESOLUTION_CONSISTENCY_PROVENANCE,
            "junction_allowance": JUNCTION_ALLOWANCE,
            "composition": "conservative feature envelope: sum over every governing feature, "
                           "plus one extra copy of the worst as a junction/end allowance",
            "governing_features": {k: list(v) for k, v in RESOLUTION_GOVERNING_FEATURES.items()},
            "lane_only_features": list(LANE_ONLY_FEATURES),
            "bridge_carrying_features": list(BRIDGE_CARRYING_FEATURES),
            "tolerances_by_candidate": {
                "w%d_kz%d" % (b["w"], b["kz"]): resolution_consistency_table(b)
                for b in SCIENTIFIC_BRIDGE_CANDIDATES
            },
        },
        "observables": {
            "inverse_consumes": "PRESSURE_NORMALISED_VOLUME_FLUX",
            "R": "(Q/dP)_open / (Q0/dP0)_blocked with Q from sum(u_x)",
            "s": "q1/(q1+q2) with q from sum(u_x)",
            "conservation_evaluated_on": "DENSITY_WEIGHTED_MASS_FLUX sum(rho*u_x)",
            "axial_plane_fields": list(AXIAL_PLANE_FIELDS),
            "transverse_plane_fields": list(TRANSVERSE_PLANE_FIELDS),
            "adjudicative_conservation_plane_ids": list(CONSERVATION_PLANE_IDS),
            "named_measurement_planes_admitted_to_conservation": False,
            "transverse_status_vocabulary": list(TRANSVERSE_STATUS),
            "tol_bridge_leakage_rel": TOL_BRIDGE_LEAKAGE_REL,
            "lateral_flux_floor_factor": LATERAL_FLUX_FLOOR_FACTOR,
            "mach_control": {
                "definition": "max over FLUID NODES of sqrt(ux^2+uy^2+uz^2), times sqrt(3)",
                "components": ["ux", "uy", "uz"],
                "solid_nodes_excluded": True,
                "retained": ["max_speed_fluid", "max_mach", "argmax_flat_index", "argmax_index",
                             "ux_at_max", "uy_at_max", "uz_at_max", "tol_mach", "pass"],
                "design_scale_role": "planning_estimate_not_a_control",
            },
            "sign_convention_axial": SIGN_CONVENTION_AXIAL,
            "sign_convention_transverse": SIGN_CONVENTION_TRANSVERSE,
            "roles": dict(QUANTITY_ROLES),
            "record_decimal_places": _RECORD_DP,
        },
        "numerical_discrepancy": {
            "method": NUMERICAL_DISCREPANCY_METHOD,
            "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
            "kind": "CONSERVATIVE_NUMERICAL_DISCREPANCY_BOUND_NOT_A_RIGOROUS_ERROR_BOUND",
            "artifact_gate": "abs(R_identical - 1) + u_R_abs <= ARTIFACT_BUDGET_R_ABS",
        },
        "reachable_set": {
            "forward_map": "R - 1 = [c^2/(1-c^2)] * [Xi/(1+Xi)]",
            "admission": "predicted_signal_upper(c_upper, Xi_upper) + artifact_upper + "
                         "other_nonoverlapping_numerical_upper < ceiling(c_lower) - margin",
            "c_source": "candidate BLOCKED MIRROR characterisation in P2a; no open mirror case",
            "double_counting_prohibited": True,
        },
        "boundary_keys": list(BOUNDARY_KEYS),
        "forbidden_boundary_keys": list(FORBIDDEN_BOUNDARY_KEYS),
        "freeze_rule": FREEZE_RULE,
        "xi_window": {"lo": XI_WINDOW_LO, "hi": XI_WINDOW_HI,
                      "provenance": XI_WINDOW_PROVENANCE},
        "validity_controls": [{"name": n, "required": r, "requirement": d}
                              for n, r, d in VALIDITY_CONTROLS],
        "decision_clauses": [dict(c) for c in DECISION_CLAUSES],
        "dispositions": list(DISPOSITIONS),
        "design_blocked_stop": DESIGN_BLOCKED,
        "arm_j": ARM_J,
        "phases": [dict(p) for p in EXECUTION_PHASES],
    }


def fixture_spec_config():
    """The machine-readable geometry specification, including the topology invariants a reviewer
    can check without running anything."""
    out = {
        "schema_version": SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "base_template": dict(BASE),
        "resolutions": {"smoke": S_SMOKE, "coarse": S_COARSE, "fine": S_FINE,
                        "scientific": list(SCIENTIFIC_RESOLUTIONS)},
        "bridge_candidates": [dict(b) for b in BRIDGE_CANDIDATES],
        "scientific_bridge_candidates": [dict(b) for b in SCIENTIFIC_BRIDGE_CANDIDATES],
        "min_feature_vox": MIN_FEATURE_VOX,
        "channel_error_law_pct": CHANNEL_ERR_LAW_PCT,
        "fixture_states": list(FIXTURE_STATES),
        "perturbations": {k: dict(v) for k, v in PERTURBATIONS.items()},
        "coupons": {"axial_length_base": BASE["seg_top_hi"] - BASE["seg_top_lo"] + 1,
                    "bridge": dict(BRIDGE_COUPON)},
        "mirror_transform": "swap_paths(mirror_x(mask, S)) == mask, exact array equality",
        "path_swap_transform": "flip(mask, axis=1) — an index map on the SAME array",
        "geometries": {},
    }
    for S in SCIENTIFIC_RESOLUTIONS:
        for b in SCIENTIFIC_BRIDGE_CANDIDATES:
            key = "S%d_w%d_kz%d" % (S, b["w"], b["kz"])
            entry = {}
            for state, connected in (("blocked", False), ("open", True)):
                mask, meta = build_fixture(S, bridge=b, connected=connected)
                entry[state] = {
                    "mask_sha256": meta["mask_sha256"], "n_fluid": meta["n_fluid"],
                    "mirror_symmetric": is_mirror_symmetric(mask, S),
                    "connectivity": connectivity(mask, meta),
                    "lane_connection": lane_connection(mask, meta),
                    "bridge_topology": bridge_topology(mask, meta),
                }
            entry["delta"] = blocked_open_delta(S, b)
            entry["min_feature"] = minimum_feature_report(S, b)
            entry["planes"] = {k: v for k, v in
                               build_fixture(S, bridge=b, connected=True)[1].items()
                               if k.startswith(("x_", "y_")) or k == "axial_conservation_planes"}
            out["geometries"][key] = entry
    for S in SCIENTIFIC_RESOLUTIONS:
        mask, meta = build_fixture(S, bridge=None)
        out["geometries"]["S%d_reference_blocked" % S] = {
            "mask_sha256": meta["mask_sha256"], "n_fluid": meta["n_fluid"],
            "mirror_symmetric": is_mirror_symmetric(mask, S),
            "connectivity": connectivity(mask, meta),
            "lane_connection": lane_connection(mask, meta),
            "bridge_topology": bridge_topology(mask, meta),
        }
    return out


def preflight_status():
    """The status artifact. Deliberately NOT named result.json or decision.md: nothing here is
    an executed result."""
    return {
        "schema_version": SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "errata": ERRATA_PATH,
        "superseded_reviews": [dict(r) for r in SUPERSEDED_REVIEWS],
        "tranche": TRANCHE_ID,
        "status": "PRE_EXECUTION_PREFLIGHT_FROZEN_PENDING_EXACT_HEAD_REVIEW",
        "solves_executed": 0,
        "lb_solver_invoked": False,
        "disposition": None,
        "cross_model_transfer_adjudicated": False,
        "predecessor": PREDECESSOR,
        "claim_ceiling": list(CLAIM_CEILING),
        "protocol_config_sha256": record_hash(protocol_config()),
        "fixture_spec_sha256": record_hash(fixture_spec_config()),
        "execution_matrix_sha256": record_hash(execution_matrix()),
        "input_file_sha256": {f: _sha_file(f) for f in INPUT_FILES},
        "stage_b_authorised": False,
        "paper_4_authorised": False,
        "card_box_5": "OPEN",
        "card_box_6": "closed on its existing mathematical result",
    }


#: The only backend that exists. A backend ARGUMENT is never accepted and then silently routed
#: to the reference solver under a different label (erratum PE-11): a different backend would
#: need to be implemented, validated and separately reviewed first.
SUPPORTED_BACKENDS = ("reference",)

#: What each solving phase requires to have completed before it may run.
PHASE_PREREQUISITES = {
    "P0": (),
    "P1a": ("P0",),
    "P1b": ("P0", "P1a"),
    "P2a": ("P0", "P1a", "P1b"),
    "P2b": ("P0", "P1a", "P1b", "P2a"),
    "P3": ("P0", "P1a", "P1b", "P2a", "P2b"),
    "P4": ("P0", "P1a", "P1b", "P2a", "P2b", "P3"),
}

#: Phases whose start additionally requires the reviewed bridge freeze AND the reviewed
#: instantiated P3/P4 matrix.
FREEZE_GATED_PHASES = ("P3", "P4")

INSTANTIATED_MATRIX_REL = RUNS_REL + "/instantiated_p3_p4_matrix.json"


def phase_manifest_rel(phase: str) -> str:
    return "%s/manifest_%s.json" % (RUNS_REL, phase)


def _git(*args):
    import subprocess
    try:
        out = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True,
                             check=True).stdout
    except Exception as exc:                                 # pragma: no cover - env limit
        raise ExecutionAuthorityError("git is not usable here (%s); an execution authority "
                                      "cannot be established" % exc)
    return out.strip()


def config_hashes():
    """The three configuration hashes every record and manifest binds."""
    return {
        "protocol_config_sha256": record_hash(protocol_config()),
        "fixture_spec_sha256": record_hash(fixture_spec_config()),
        "execution_matrix_sha256": record_hash(execution_matrix()),
    }


def execution_authority(stage: str, backend: str = "reference", require_clean: bool = True):
    """Everything a future stage must record so its output can never be attributed to a head
    that did not produce it — and it FAILS CLOSED (erratum PE-11).

    It raises ``ExecutionAuthorityError`` rather than returning ``None`` for: an unusable git
    identity, a dirty working tree, a missing input file, an unsupported backend, or an unknown
    stage. A partial authority record is never returned.
    """
    import platform

    if stage not in PHASE_PREREQUISITES:
        raise ExecutionAuthorityError(
            "unknown stage %r; expected one of %r" % (stage, sorted(PHASE_PREREQUISITES)))
    if backend not in SUPPORTED_BACKENDS:
        raise ExecutionAuthorityError(
            "backend %r is not supported; only %r exists. A backend argument is never accepted "
            "and then silently routed to the reference solver." % (backend, SUPPORTED_BACKENDS))
    commit = _git("rev-parse", "HEAD")
    tree = _git("rev-parse", "HEAD^{tree}")
    if not commit or not tree:                               # pragma: no cover - env limit
        raise ExecutionAuthorityError("git returned no commit/tree; cannot establish authority")
    porcelain = _git("status", "--porcelain")
    if require_clean and porcelain:
        raise ExecutionAuthorityError(
            "the working tree is dirty; an execution authority must bind a committed head:\n%s"
            % porcelain)
    files = {}
    for rel in INPUT_FILES:
        h = _sha_file(rel)
        if h is None:
            raise ExecutionAuthorityError(
                "input file %r is missing; an authority may not record a null hash" % rel)
        files[rel] = h
    protocol_sha = _sha_file(PROTOCOL_PATH)
    geometry_sha = _sha_file(BUNDLE_REL + "/VIRTUAL_FIXTURE_SPEC.md")
    errata_sha = _sha_file(ERRATA_PATH)
    for name, val in (("protocol", protocol_sha), ("geometry spec", geometry_sha),
                      ("errata", errata_sha)):
        if val is None:
            raise ExecutionAuthorityError("the %s document is missing" % name)
    try:
        import scipy
        scipy_v = scipy.__version__
    except Exception as exc:                                 # pragma: no cover - env limit
        raise ExecutionAuthorityError("scipy is required for the geometry audits (%s)" % exc)
    out = {
        "stage": stage,
        "tranche": TRANCHE_ID,
        "correction_version": CORRECTION_VERSION,
        "source_commit": commit, "source_tree": tree,
        "working_tree_clean": not porcelain,        # recorded as MEASURED, never assumed
        "clean_tree_required": bool(require_clean),
        "base_commit": BASE_COMMIT, "base_tree": BASE_TREE,
        "protocol_sha256": protocol_sha,
        "geometry_spec_sha256": geometry_sha,
        "errata_sha256": errata_sha,
        "input_file_sha256": files,
        "backend": backend,
        "dependencies": {"python": platform.python_version(), "numpy": np.__version__,
                         "scipy": scipy_v},
        "seed": None,
        "solver_config": {"tau_plus": TAU_PLUS, "nu": NU, "rtol": RTOL, "check": CHECK,
                          "min_steps": MIN_STEPS, "max_steps": MAX_STEPS},
        "prerequisites": list(PHASE_PREREQUISITES[stage]),
    }
    out.update(config_hashes())
    return out


class FreezeMissing(RuntimeError):
    """Raised when a stage that requires the bridge freeze is invoked without a matching one."""


class ManifestMissing(RuntimeError):
    """Raised when a phase is invoked without a valid completion manifest for a predecessor."""


def _load_json(path, what):
    p = pathlib.Path(path)
    if not p.exists():
        raise ManifestMissing("%s does not exist at %s" % (what, p))
    try:
        return json.loads(p.read_text())
    except Exception as exc:
        raise ManifestMissing("%s at %s is not readable JSON: %s" % (what, p, exc))


def require_freeze(stage: str, runs_dir=None, path=None, matrix_path=None):
    """Fail-closed freeze gate. A primary stage refuses to execute when the freeze artifact is
    absent, malformed, empty, bound to a different configuration, or unaccompanied by the
    reviewed INSTANTIATED P3/P4 matrix it authorises."""
    base = (pathlib.Path(runs_dir) if runs_dir is not None else (REPO_ROOT / RUNS_REL))
    p = pathlib.Path(path) if path is not None else (base / "bridge_freeze.json")
    if not p.exists():
        raise FreezeMissing(
            "stage %r requires the bridge freeze artifact at %s, which does not exist. The "
            "candidate and aperture must be frozen — and reviewed — before any primary mirror "
            "output is generated." % (stage, p))
    try:
        doc = json.loads(p.read_text())
    except Exception as exc:
        raise FreezeMissing("bridge freeze artifact %s is not readable JSON: %s" % (p, exc))
    want = config_hashes()
    bad = {k: (doc.get(k), v) for k, v in want.items() if doc.get(k) != v}
    if bad:
        raise FreezeMissing(
            "bridge freeze artifact does not match the execution authority for stage %r: %s. "
            "A freeze binds a specific configuration; re-freezing after review is a new "
            "decision, not a repair." % (stage, sorted(bad)))
    if doc.get("correction_version") != CORRECTION_VERSION:
        raise FreezeMissing("the freeze was produced under correction version %r, not %r"
                            % (doc.get("correction_version"), CORRECTION_VERSION))
    bridges = doc.get("frozen_bridges")
    if not bridges:
        raise FreezeMissing("bridge freeze artifact carries no frozen_bridges")
    if len(bridges) != N_FROZEN_BRIDGES:
        raise FreezeMissing("the freeze carries %d bridges; exactly %d are required"
                            % (len(bridges), N_FROZEN_BRIDGES))
    mp = pathlib.Path(matrix_path) if matrix_path is not None else (
        base / "instantiated_p3_p4_matrix.json")
    if not mp.exists():
        raise FreezeMissing(
            "stage %r also requires the reviewed instantiated P3/P4 matrix at %s; a freeze "
            "without it does not say which cases it authorises" % (stage, INSTANTIATED_MATRIX_REL))
    inst = json.loads(mp.read_text())
    # PE-51: ONE canonical schema, used by writer, validator, freeze gate and executor alike
    if inst.get("rows_sha256") != doc.get("rows_sha256"):
        raise FreezeMissing("the instantiated P3/P4 matrix is not the one this freeze hashed "
                            "(rows_sha256 mismatch)")
    actual = hashlib.sha256(mp.read_bytes()).hexdigest()
    if doc.get("instantiated_matrix_file_sha256") != actual:
        raise FreezeMissing("the instantiated P3/P4 matrix FILE hash does not match the freeze")
    if doc.get("status") != "APPROVED_BY_EXACT_HEAD_REVIEW":
        raise FreezeMissing(
            "the freeze at %s carries status %r; P3/P4 require an APPROVED freeze produced by "
            "the promotion contract, and a PROPOSED freeze authorises nothing (PE-40 §13)"
            % (p, doc.get("status")))
    if doc.get("provenance_mode") != "PRODUCTION":
        raise FreezeMissing("a TEST_ONLY freeze may never satisfy a production gate")
    return doc


APPROVED_FREEZE_STATUS = "APPROVED_BY_EXACT_HEAD_REVIEW"


def make_approved_freeze(runs_dir, review_commit, review_tree, provenance_mode="PRODUCTION"):
    """The proposed-to-approved promotion wrapper (PE-40 §13). IMPLEMENTED, NOT EXERCISED.

    A small reviewed authority wrapper that binds the exact file hashes of the proposed freeze,
    the P2b manifest, the candidate ledger and the instantiated matrix. **It changes no scientific
    value**: any change to candidates or evidence requires a new P2b assembly, never an edit here.
    It does not itself authorize P3 or P4.
    """
    base = pathlib.Path(runs_dir)
    files = {}
    for name in ("proposed_bridge_freeze.json", "manifest_P2b.json", "candidate_ledger.json",
                 "instantiated_p3_p4_matrix.json"):
        f = base / name
        if not f.exists():
            raise FreezeMissing("promotion requires %s" % name)
        files[name] = hashlib.sha256(f.read_bytes()).hexdigest()
    proposed = json.loads((base / "proposed_bridge_freeze.json").read_text())
    inst = json.loads((base / "instantiated_p3_p4_matrix.json").read_text())
    if proposed.get("status") != "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW":
        raise FreezeMissing("only a PROPOSED freeze may be promoted")
    doc = {
        "schema_version": 1, "correction_version": CORRECTION_VERSION,
        "provenance_mode": provenance_mode,
        "status": APPROVED_FREEZE_STATUS,
        "proposed_bridge_freeze_file_sha256": files["proposed_bridge_freeze.json"],
        "manifest_P2b_file_sha256": files["manifest_P2b.json"],
        "candidate_ledger_file_sha256": files["candidate_ledger.json"],
        "instantiated_matrix_file_sha256": files["instantiated_p3_p4_matrix.json"],
        "rows_sha256": inst["rows_sha256"],
        "frozen_bridges": [{"w": b["w"], "kz": b["kz"], "slot": b["slot"]}
                           for b in proposed["frozen_bridges"]],
        "review_commit": review_commit, "review_tree": review_tree,
        "authorises_p3_p4": False,
        "note": ("an approval wrapper binds evidence; it does NOT authorize P3 or P4, which need "
                 "their own reviewed source commit adding them to AUTHORISED_SOLVING_PHASES"),
    }
    doc.update(config_hashes())
    return doc


# ==========================================================================================
# 11b. IMMUTABLE CASE RECORDS, STRONG PHASE MANIFESTS, RECORD-DERIVED FREEZE (erratum PE-18)
# ==========================================================================================
# Superseded: a manifest passed on a NONEMPTY completed_cases list, and build_freeze() accepted
# free-form candidate dicts, envelopes, eligibility flags and record hashes, checking only that a
# cited hash appeared somewhere. A manifest could claim a phase complete while omitting rows, one
# hash could bind several physically distinct candidates, and the freeze's scientific content was
# whatever the caller passed in. That is a freeze bound to assertions, not to evidence.

CASE_RECORD_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1
CASE_RECORD_PREFIX = "case_"
TERMINAL_PHASE_STATUSES = ("PHASE_COMPLETE", "PHASE_STOPPED_DESIGN_BLOCKED",
                           "PHASE_STOPPED_UNCONVERGED", "PHASE_STOPPED_INVALID_CASE")


def row_sha256(row) -> str:
    """The canonical SHA-256 of one matrix row. The exact forcing rational is part of it, so a
    row whose rational changed is a different row (erratum PE-21)."""
    return record_hash(row)


def case_record_filename(case_id: str) -> str:
    """Deterministically derived from ``case_id`` — never from a counter, a timestamp or an
    ordering, so a resume finds exactly the record that belongs to a row."""
    return "%s%s.json" % (CASE_RECORD_PREFIX,
                          hashlib.sha256(case_id.encode("utf-8")).hexdigest())


#: The macroscopic fields every solve requests. Recorded per case so the record states what was
#: actually asked for (erratum PE-35).
RETURN_FIELDS = ("rho", "uy", "uz")


def effective_solver_config(row, backend="reference", audit=None):
    """The configuration ACTUALLY passed to the solver for this row (erratum PE-35).

    The superseded record copied the authority's GLOBAL solver_config, so a ``tau_plus = 1.2``
    cross-check row recorded ``tau_plus = 2.0``. This is recomputed from the canonical row and the
    validator requires exact equality with the record.
    """
    if row["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X":
        if audit is None:
            raise ValueError("a fixed-step row needs its audit plan to state min/max steps")
        min_steps = max_steps = int(audit["target_steps"])
    else:
        min_steps, max_steps = MIN_STEPS, MAX_STEPS
    return {
        "tau_plus": float(row["tau_plus"]),
        "forcing_exact": dict(row["forcing_exact"]),
        "forcing_repr": row["forcing_repr"],
        "rtol": RTOL, "check": CHECK,
        "min_steps": min_steps, "max_steps": max_steps,
        "run_mode": row["run_mode"],
        "fixed_step_target": (None if audit is None else int(audit["target_steps"])),
        "return_fields": list(RETURN_FIELDS),
        "backend": backend,
    }


def make_case_record(row, authority, predecessor_manifest_sha256, geometry, scientific,
                     completed_steps, run_mode="NORMAL", audit=None, provenance_mode="PRODUCTION",
                     scientific_payload_sha256=None):
    """One immutable compact case record. No large fields; no non-finite values (the canonical
    writer enforces both)."""
    if run_mode not in RUN_MODES:
        raise ValueError("unknown run mode %r" % (run_mode,))
    target = None if audit is None else int(audit["target_steps"])
    status = run_status(run_mode, completed_steps, target_steps=target)
    if row["forcing_repr"] != repr(forcing_from_exact(row["forcing_exact"])):
        raise ValueError("case record forcing_repr is not the float of its own exact rational")
    return {
        "schema_version": CASE_RECORD_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": row["phase"],
        "case_id": row["case_id"],
        "row_sha256": row_sha256(row),
        "row": dict(row),
        "forcing_exact": dict(row["forcing_exact"]),
        "forcing_repr": row["forcing_repr"],
        "kind": row["kind"],
        "geometry": dict(geometry),
        "mask_sha256": geometry.get("mask_sha256"),
        "source_commit": authority["source_commit"],
        "source_tree": authority["source_tree"],
        "execution_authority_sha256": record_hash(authority),
        "protocol_config_sha256": authority["protocol_config_sha256"],
        "fixture_spec_sha256": authority["fixture_spec_sha256"],
        "execution_matrix_sha256": authority["execution_matrix_sha256"],
        "backend": authority["backend"],
        "dependencies": dict(authority["dependencies"]),
        "solver_config": effective_solver_config(row, backend=authority["backend"], audit=audit),
        "fixture_dimensions": list(geometry.get("shape") or ()),
        "provenance_mode": provenance_mode,
        "scientific_payload_sha256": scientific_payload_sha256,
        "predecessor_manifest_sha256": dict(predecessor_manifest_sha256),
        "run_mode": run_mode,
        "completed_steps": int(completed_steps),
        "status": status,
        "audit": (None if audit is None else dict(audit)),
        "scientific": scientific,
    }


def validate_case_record(rec, row=None, authority=None, phase=None):
    """Fail-closed structural validation. Raises with the first defect found."""
    for k in ("schema_version", "correction_version", "phase", "case_id", "row_sha256", "row",
              "forcing_exact", "forcing_repr", "source_commit", "source_tree",
              "execution_authority_sha256", "run_mode", "completed_steps", "status",
              "scientific", "solver_config", "provenance_mode"):
        if k not in rec:
            raise ValueError("case record is missing %r" % (k,))
    if rec["correction_version"] != CORRECTION_VERSION:
        raise ValueError("case record was produced under correction version %r, not %r"
                         % (rec["correction_version"], CORRECTION_VERSION))
    if rec["status"] not in RUN_STATUSES:
        raise ValueError("unknown run status %r" % (rec["status"],))
    if rec["row"].get("case_id") != rec["case_id"]:
        raise ValueError("case record's row does not carry its own case_id")
    if row_sha256(rec["row"]) != rec["row_sha256"]:
        raise ValueError("case record's row hash does not match its row")
    if float(rec["forcing_repr"]) != forcing_from_exact(rec["forcing_exact"]):
        raise ValueError("case record forcing_repr is not float(Fraction(numerator, "
                         "denominator))")
    if phase is not None and rec["phase"] != phase:
        raise ValueError("case record belongs to phase %r, not %r" % (rec["phase"], phase))
    if row is not None:
        if rec["case_id"] != row["case_id"]:
            raise ValueError("case record %r was cited for row %r"
                             % (rec["case_id"], row["case_id"]))
        if rec["row_sha256"] != row_sha256(row):
            raise ValueError("case record row hash does not match the planned row")
    if authority is not None:
        for k in ("source_commit", "source_tree"):
            if rec[k] != authority[k]:
                raise ValueError("case record %s %r does not match the authority %r"
                                 % (k, rec[k], authority[k]))
        for k in ("protocol_config_sha256", "fixture_spec_sha256", "execution_matrix_sha256"):
            if rec.get(k) != authority[k]:
                raise ValueError("case record %s does not bind this configuration" % (k,))
    if rec["provenance_mode"] not in ("PRODUCTION", "TEST_ONLY"):
        raise ValueError("unknown provenance_mode %r" % (rec["provenance_mode"],))
    if row is not None:
        want = effective_solver_config(row, backend=rec["backend"],
                                       audit=rec.get("audit"))
        if rec["solver_config"] != want:
            raise ValueError(
                "the record's effective solver configuration is not the one the canonical row "
                "requires (erratum PE-35): recorded %r, required %r"
                % (rec["solver_config"], want))
    canonical_json(rec)                       # strict: no NaN/Inf anywhere in a bound record
    return rec


def assert_production_record(rec):
    """Production manifests and freezes accept PRODUCTION records only (erratum PE-34)."""
    if rec.get("provenance_mode") != "PRODUCTION":
        raise ManifestMissing(
            "case record %r carries provenance_mode=%r; a production manifest or freeze accepts "
            "PRODUCTION records only" % (rec.get("case_id"), rec.get("provenance_mode")))
    return rec


#: Keys stripped from the scientific payload before hashing: they carry CASE IDENTITY or file
#: metadata, which differ between a base case and its replicate by construction (erratum PE-37).
PAYLOAD_IDENTITY_KEYS = ("source_case_id", "case_id", "base_case_id", "audit_of_case_id",
                         "replicate_of_case_id", "record_path", "record_sha256")


def _strip_identity(o):
    if isinstance(o, dict):
        return {k: _strip_identity(v) for k, v in o.items() if k not in PAYLOAD_IDENTITY_KEYS}
    if isinstance(o, (list, tuple)):
        return [_strip_identity(v) for v in o]
    return o


def scientific_payload_hash(effective_config, scientific, mask_sha256):
    """The canonical payload identity a determinism replicate must reproduce (erratum PE-37).

    Deliberately EXCLUDES case identity, file paths and anything else that differs between a base
    case and its replicate by construction.
    """
    return record_hash({"effective_config": _strip_identity(effective_config),
                        "scientific": _strip_identity(scientific),
                        "mask_sha256": mask_sha256})


def write_case_record(runs_dir, rec, allow_resume=True):
    """Atomic temp-file + rename. NEVER overwrites: on an existing file the record is verified and
    reused only when it is an EXACT match, otherwise it fails closed."""
    validate_case_record(rec)
    base = pathlib.Path(runs_dir)
    base.mkdir(parents=True, exist_ok=True)
    path = base / case_record_filename(rec["case_id"])
    payload = canonical_json(rec) + "\n"
    if path.exists():
        if not allow_resume:
            raise FileExistsError("case record %s already exists and overwrite is refused" % path)
        if path.read_text() != payload:
            raise ValueError(
                "a case record already exists at %s and differs from the one just produced. A "
                "record is immutable: a resume reuses an EXACT match and otherwise fails closed "
                "(erratum PE-18)." % path)
        return path, "REUSED_EXACT_MATCH"
    tmp = base / (path.name + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)                          # atomic within the same directory
    return path, "WRITTEN"


def read_case_record(runs_dir, case_id):
    path = pathlib.Path(runs_dir) / case_record_filename(case_id)
    if not path.exists():
        raise ManifestMissing("case record for %r does not exist at %s" % (case_id, path))
    rec = json.loads(path.read_text())
    if rec.get("case_id") != case_id:
        raise ValueError("the record file for %r carries case_id %r"
                         % (case_id, rec.get("case_id")))
    return rec, path


# ---- adaptive derivation: what each phase is EXPECTED to run, derived from predecessors -------

NODE_OFFSET_SCHEMA_VERSION = 1


def node_offset_summary(ux, rho, mask, meta, g, case_id=None):
    """A compact per-state node-offset summary, extracted from a field ALREADY COMPUTED.

    Erratum PE-41: C3 scheduled 144 separate rows that each went through the result provider, so
    the same physics was solved twice and the planned budget was overstated. The frozen offsets
    are re-reads of one solution; this function is called while that solution is in memory and
    makes **no** provider call.

    Erratum PE-42: the per-offset quantity retained here is a CONDUCTANCE, never a ratio. The
    same-state quantity ``C_j/C_0`` is NOT ``R``, and forming ``R`` is P2b's job, only after it
    has paired an exact open and blocked record — see :func:`node_offset_R`.
    """
    offsets = (0,) + tuple(meta["node_offsets"])
    rows = []
    for off in offsets:
        xin, xout = meta["x_node_in"] - off, meta["x_node_out"] + off
        p_in = axial_plane_record("x_node_in_off%d" % off, xin, ux, rho, mask, g)
        p_out = axial_plane_record("x_node_out_off%d" % off, xout, ux, rho, mask, g)
        q = axial_plane_record("x_meas_a", meta["x_meas_a"], ux, rho, mask, g)
        dP = p_in["p_mean"] - p_out["p_mean"]
        finite = all(math.isfinite(v) for v in (p_in["p_mean"], p_out["p_mean"], q["sum_ux"], dP))
        rows.append({
            "offset": int(off),
            "inlet_plane_id": p_in["plane_id"], "inlet_index": int(xin),
            "outlet_plane_id": p_out["plane_id"], "outlet_index": int(xout),
            "flux_plane_id": q["plane_id"], "flux_index": int(meta["x_meas_a"]),
            "Q_volume": q["sum_ux"], "p_in": p_in["p_mean"], "p_out": p_out["p_mean"],
            "delta_P": dP,
            "conductance": (q["sum_ux"] / dP if (finite and dP != 0.0) else None),
            "n_fluid_inlet": p_in["n_fluid"], "n_fluid_outlet": p_out["n_fluid"],
            "n_fluid_flux": q["n_fluid"],
            "finite": bool(finite), "delta_P_nonzero": bool(dP != 0.0),
        })
    return {
        "node_offset_schema_version": NODE_OFFSET_SCHEMA_VERSION,
        "offsets": [int(o) for o in offsets],
        "per_offset": rows,
        "source_case_id": case_id,
        "mask_sha256": meta["mask_sha256"],
        "state": meta["state"], "S": meta["S"], "bridge": meta.get("bridge"),
        "quantity": "CONDUCTANCE_PER_OFFSET_NOT_A_RATIO",
        "note": ("extracted from a field already computed for this case; it is NOT a separate "
                 "solve and must never increment the provider-call count (erratum PE-41)"),
        "all_finite": all(r["finite"] and r["delta_P_nonzero"] for r in rows),
    }


#: The configuration fields an open and a blocked record must agree on before their node-offset
#: conductances may be divided (erratum PE-42).
NODE_OFFSET_PAIR_FIELDS = ("S", "forcing_level", "tau_plus", "variant", "perturbation",
                           "obstructed", "swapped", "run_mode", "coupon_orientation")


def node_offset_R(open_rec, blocked_rec):
    """``R_offset_j = C_open_offset_j / C_blocked_offset_j`` and the resulting uncertainty.

    The two records must describe the SAME configuration in every respect except the state, and
    must carry identical offset sets and identical plane definitions. Anything else fails closed:
    an open offset paired with a different blocked configuration is not a node-offset sensitivity
    of ``R``.
    """
    for f in NODE_OFFSET_PAIR_FIELDS:
        if open_rec["row"].get(f) != blocked_rec["row"].get(f):
            raise ValueError("node-offset pairing mismatch on %r: %r vs %r"
                             % (f, open_rec["row"].get(f), blocked_rec["row"].get(f)))
    if _bridge_key(open_rec) != _bridge_key(blocked_rec):
        raise ValueError("node-offset pairing mismatch on the candidate geometry")
    if open_rec["row"]["state"] != "open" or blocked_rec["row"]["state"] != "blocked":
        raise ValueError("node_offset_R needs exactly one open and one blocked record")
    o = (open_rec.get("scientific") or {}).get("node_offsets")
    b = (blocked_rec.get("scientific") or {}).get("node_offsets")
    if not o or not b:
        raise ValueError("both records must carry a node-offset summary; a missing one FAILS the "
                         "evidence and may never contribute zero (erratum PE-32)")
    if o["offsets"] != b["offsets"]:
        raise ValueError("node-offset sets differ: %r vs %r" % (o["offsets"], b["offsets"]))
    ratios = []
    for ro, rb in zip(o["per_offset"], b["per_offset"]):
        for k in ("inlet_plane_id", "outlet_plane_id", "flux_plane_id", "inlet_index",
                  "outlet_index", "flux_index"):
            if ro[k] != rb[k]:
                raise ValueError("node-offset plane definitions differ at offset %r on %r"
                                 % (ro["offset"], k))
        if ro["conductance"] is None or rb["conductance"] is None:
            raise ValueError("a node-offset conductance is unavailable at offset %r"
                             % (ro["offset"],))
        if rb["conductance"] == 0.0:
            raise ValueError("a blocked node-offset conductance is zero at offset %r"
                             % (ro["offset"],))
        ratios.append({"offset": ro["offset"],
                       "R_offset": _finite(ro["conductance"] / rb["conductance"],
                                           "R at offset %r" % ro["offset"])})
    nominal = ratios[0]["R_offset"]
    movement = max(abs(r["R_offset"] - nominal) for r in ratios)
    return {
        "offsets": o["offsets"],
        "R_offsets": ratios,
        "R_nominal": nominal,
        "max_abs_movement": movement,
        "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
        "u_pressure_plane_R": NUMERICAL_DISCREPANCY_SAFETY_FACTOR * movement,
        "open_case_id": open_rec["case_id"], "blocked_case_id": blocked_rec["case_id"],
        "open_record_sha256": record_hash(open_rec),
        "blocked_record_sha256": record_hash(blocked_rec),
        "method": ("R_offset_j = C_open_offset_j / C_blocked_offset_j, formed only after exact "
                   "open/blocked pairing; a same-state C_j/C_0 is NOT R (erratum PE-42)"),
    }


def field_contrast(sci):
    """The blocked-side four-conductance coarse-graining, from a compact record's own scalars.

    Carried over unchanged in form from the 001 in-situ construction, evaluated on 001b's frozen
    planes: the node pressures, the two mid-face pressures and the two lane fluxes are all already
    in the compact record, so nothing is recomputed from a field array.
    """
    pin, pout = _finite(sci["p_node_in"], "p_node_in"), _finite(sci["p_node_out"], "p_node_out")
    p1, p2 = _finite(sci["p_face1"], "p_face1"), _finite(sci["p_face2"], "p_face2")
    q1, q2 = _finite(sci["q1_volume"], "q1_volume"), _finite(sci["q2_volume"], "q2_volume")
    for name, den in (("pin-p1", pin - p1), ("p1-pout", p1 - pout),
                      ("pin-p2", pin - p2), ("p2-pout", p2 - pout)):
        if den == 0.0:
            raise ValueError("degenerate segment pressure drop %s" % name)
    g1t, g1b = q1 / (pin - p1), q1 / (p1 - pout)
    g2t, g2b = q2 / (pin - p2), q2 / (p2 - pout)
    A1, A2 = g1t + g1b, g2t + g2b
    if A1 == 0.0 or A2 == 0.0:
        raise ValueError("degenerate lane conductance")
    return {
        "g1_top": g1t, "g1_bot": g1b, "g2_top": g2t, "g2_bot": g2b,
        "A1": A1, "A2": A2,
        "c_field": (g1t - g1b) / A1,
        "c_field_lane2": (g2b - g2t) / A2,
        "X_cross_product": g1t * g2b - g2t * g1b,
    }


def _pair_key(rec):
    """(bridge, S, forcing level) — the identity of an identical-path blocked/open PAIR. The
    artifact is a property of the pair, never of one member."""
    k = _bridge_key(rec)
    if k is None:
        return None
    return (k, rec["row"]["S"], rec["row"]["forcing_level"])


def _conductance(rec):
    sci = rec.get("scientific") or {}
    Q, dP = _finite(sci["Q_volume"], "Q_volume"), _finite(sci["dP"], "dP")
    if dP == 0.0:
        raise ValueError("a case record carries a zero node-to-node pressure drop")
    return Q / dP


def identical_path_pairs(records_by_case, phases=None):
    """Group identical-path records into blocked/open pairs and their fixed-step audits."""
    pairs = {}
    for rec in records_by_case.values():
        if rec.get("kind") != "identical_path_control":
            continue
        if phases and rec["row"]["phase"] not in phases:
            continue
        key = _pair_key(rec)
        if key is None:
            continue
        slot = ("audit_" if rec["run_mode"] != "NORMAL" else "") + rec["row"]["state"]
        pairs.setdefault(key, {})[slot] = rec
    return pairs


def artifact_from_pair(pair):
    """Recompute R_identical, its numerical-discrepancy bound and the artifact upper bound from a
    pair's OWN records and its OWN fixed-step audits (errata PE-6, PE-16, PE-17)."""
    for slot in ("blocked", "open"):
        if slot not in pair:
            return None
    Cb, Co = _conductance(pair["blocked"]), _conductance(pair["open"])
    if Cb == 0.0:
        raise ValueError("a blocked identical-path case has zero conductance")
    R = Co / Cb
    ab, ao = pair.get("audit_blocked"), pair.get("audit_open")
    if not (ab and ao):
        return {"R_identical": R, "point": abs(R - 1.0), "fixed_step_case_ids": None,
                "u_R": None, "upper": None, "within_budget": None,
                "reason": "no fixed-step evidence yet; a point estimate may only REJECT"}
    disc = numerical_discrepancy_R(R, Co, Cb, _conductance(ao), _conductance(ab))
    m = artifact_metrics(Co, Cb, R, numerical_uncertainty=disc["u_R_abs"])
    return {
        "R_identical": R, "point": abs(R - 1.0),
        "fixed_step_case_ids": [ab["case_id"], ao["case_id"]],
        "fixed_step_record_sha256": [record_hash(ab), record_hash(ao)],
        "u_R": disc["u_R_abs"], "discrepancy": disc,
        "upper": m["artifact_upper_bound"], "within_budget": bool(m["within_budget"]),
        "case_ids": [pair["blocked"]["case_id"], pair["open"]["case_id"]],
        "record_sha256": [record_hash(pair["blocked"]), record_hash(pair["open"])],
        "method": "artifact recomputed from the pair's own records and its own fixed-step audits",
    }


def _bridge_key(rec_or_row):
    row = rec_or_row.get("row", rec_or_row)
    b = row.get("bridge")
    if not isinstance(b, dict):
        return None
    return (int(b["w"]), int(b["kz"]))


# ---- P2b: the freeze is DERIVED from records, never supplied (errata PE-23 … PE-25, PE-30, PE-31)

#: The one canonical artifact-evidence schema. Plural throughout, flat throughout (erratum PE-23).
ARTIFACT_EVIDENCE_FIELDS = (
    "candidate_id", "resolution", "forcing_level",
    "normal_case_ids", "normal_record_sha256",
    "audit_case_ids", "audit_record_sha256",
    "pressure_plane_case_ids", "pressure_plane_record_sha256",
    "R_point", "u_fixed_step_R", "u_pressure_plane_R", "u_serialization_R", "u_artifact_R",
    "artifact_upper", "pass", "lineage",
)


def assert_artifact_evidence(ev):
    """Validate the evidence schema BEFORE any scientific use (erratum PE-23)."""
    missing = [k for k in ARTIFACT_EVIDENCE_FIELDS if k not in ev]
    if missing:
        raise ValueError("artifact evidence is missing %r" % (missing,))
    for k in ("normal_case_ids", "audit_case_ids", "pressure_plane_case_ids"):
        assert_flat_id_list(ev[k], "artifact evidence %s" % k)
    for k in ("normal_record_sha256", "audit_record_sha256", "pressure_plane_record_sha256"):
        assert_flat_hash_list(ev[k], "artifact evidence %s" % k)
    if len(ev["normal_case_ids"]) != len(ev["normal_record_sha256"]):
        raise ValueError("artifact evidence normal ids and hashes are not paired")
    if len(ev["audit_case_ids"]) != len(ev["audit_record_sha256"]):
        raise ValueError("artifact evidence audit ids and hashes are not paired")
    if set(ev["normal_case_ids"]) & set(ev["audit_case_ids"]):
        raise ValueError("a case is cited as both normal and audit evidence")
    for k in ("R_point", "u_fixed_step_R", "u_pressure_plane_R", "u_serialization_R",
              "u_artifact_R", "artifact_upper"):
        _finite(ev[k], "artifact evidence %s" % k)
    return ev


def _normal_only(records, kind, key=None):
    """NORMAL records only. Audits are paired discrepancy evidence, never observations
    (erratum PE-30): the superseded selection matched on ``kind``, which is identical for a row
    and its audit, so re-runs of the same configuration entered estimates as new observations."""
    return {cid: r for cid, r in records.items()
            if r.get("kind") == kind and r["run_mode"] == "NORMAL"
            and (key is None or _bridge_key(r) == key)}


def _audits_for(records, kind, key=None):
    return {cid: r for cid, r in records.items()
            if r.get("kind") == kind and r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"
            and (key is None or _bridge_key(r) == key)}


def _pair_normal_with_audit(normals, audits):
    """Pair each audit with its EXACT normal base via ``audit_of_case_id`` (erratum PE-30)."""
    pairs = {}
    for cid, a in audits.items():
        base_id = a["row"].get("audit_of_case_id")
        if base_id is None or base_id not in normals:
            continue
        pairs[base_id] = {"normal": normals[base_id], "audit": a}
    return pairs


def fixed_step_discrepancy(pairs, value_of, what):
    """The relative fixed-step discrepancy of a quantity, from a family's OWN normal/audit pairs.

    ``value_of(record)`` extracts the quantity. Returns the worst relative movement, times the
    frozen safety factor, with full lineage. Never the artifact's ``u_R`` (erratum PE-31).
    """
    terms, n_ids, a_ids, n_h, a_h = [], [], [], [], []
    for base_id, pr in sorted(pairs.items()):
        base, aud = value_of(pr["normal"]), value_of(pr["audit"])
        if base is None or aud is None:
            continue
        b = _finite(base, "%s base" % what)
        if b == 0.0:
            continue
        terms.append(abs(_finite(aud, "%s audit" % what) / b - 1.0))
        n_ids.append(pr["normal"]["case_id"])
        a_ids.append(pr["audit"]["case_id"])
        n_h.append(record_hash(pr["normal"]))
        a_h.append(record_hash(pr["audit"]))
    worst = max(terms) if terms else None
    return {
        "quantity": what,
        "method": ("worst relative movement between each NORMAL record and its own fixed-step "
                   "re-execution, times the frozen safety factor"),
        "normal_case_ids": assert_flat_id_list(n_ids, "%s normal ids" % what),
        "audit_case_ids": assert_flat_id_list(a_ids, "%s audit ids" % what),
        "normal_record_sha256": assert_flat_hash_list(n_h, "%s normal hashes" % what),
        "audit_record_sha256": assert_flat_hash_list(a_h, "%s audit hashes" % what),
        "n_pairs": len(terms),
        "worst_relative_movement": worst,
        "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
        "value": (None if worst is None else NUMERICAL_DISCREPANCY_SAFETY_FACTOR * worst),
        "overlaps": "none; this family's own pairs only",
    }


def artifact_evidence_from_records(records, bridge_key):
    """Build validated artifact evidence for one candidate, per (resolution, forcing level).

    The artifact is a property of the blocked/open PAIR. Its uncertainty comes from that pair's
    OWN fixed-step audits and its OWN pressure-plane diagnostics — never from a borrowed term and
    never with a silently-zero contribution (errata PE-31, PE-32).
    """
    out = {}
    normals = _normal_only(records, "identical_path_control", bridge_key)
    audits = _audits_for(records, "identical_path_control", bridge_key)
    planes = {cid: r for cid, r in records.items()
              if r.get("kind") == "pressure_plane_diagnostic" and _bridge_key(r) == bridge_key}
    by_combo = {}
    for cid, r in normals.items():
        by_combo.setdefault((r["row"]["S"], r["row"]["forcing_level"]), {})[r["row"]["state"]] = r
    for (S, level), states in sorted(by_combo.items()):
        if set(states) != {"blocked", "open"}:
            continue
        Cb, Co = _conductance(states["blocked"]), _conductance(states["open"])
        if Cb == 0.0:
            raise ValueError("a blocked identical-path case has zero conductance")
        R = Co / Cb
        n_ids = [states["blocked"]["case_id"], states["open"]["case_id"]]
        n_h = [record_hash(states["blocked"]), record_hash(states["open"])]
        a_ids, a_h, u_fs = [], [], None
        pair_audits = {}
        for st in ("blocked", "open"):
            for cid, a in audits.items():
                if a["row"].get("audit_of_case_id") == states[st]["case_id"]:
                    pair_audits[st] = a
        if set(pair_audits) == {"blocked", "open"}:
            disc = numerical_discrepancy_R(R, Co, Cb,
                                           _conductance(pair_audits["open"]),
                                           _conductance(pair_audits["blocked"]))
            u_fs = disc["u_continuation_R_abs"] * NUMERICAL_DISCREPANCY_SAFETY_FACTOR
            a_ids = [pair_audits["blocked"]["case_id"], pair_audits["open"]["case_id"]]
            a_h = [record_hash(pair_audits["blocked"]), record_hash(pair_audits["open"])]
        # PE-42: the node-offset ratio is formed ONLY from the exactly paired open/blocked
        # records. A same-state C_j/C_0 is not R, and a missing summary FAILS the evidence.
        p_ids, p_h, u_pp, offs = [], [], None, None
        try:
            offs = node_offset_R(states["open"], states["blocked"])
        except (ValueError, NonFiniteValue):
            offs = None
        if offs is not None:
            u_pp = offs["u_pressure_plane_R"]
            p_ids = [offs["blocked_case_id"], offs["open_case_id"]]
            p_h = [offs["blocked_record_sha256"], offs["open_record_sha256"]]
        u_ser = 10.0 ** (-_RECORD_DP) * (1.0 + abs(R))
        complete = u_fs is not None and u_pp is not None
        u_total = (None if not complete else u_fs + u_pp + u_ser)
        upper = (None if u_total is None else abs(R - 1.0) + u_total)
        ev = {
            "candidate_id": "w%d_kz%d" % bridge_key,
            "resolution": S, "forcing_level": level,
            "normal_case_ids": sorted(n_ids), "normal_record_sha256": sorted(n_h),
            "audit_case_ids": sorted(a_ids), "audit_record_sha256": sorted(a_h),
            "pressure_plane_case_ids": sorted(p_ids),
            "pressure_plane_record_sha256": sorted(p_h),
            "R_point": R,
            "u_fixed_step_R": (0.0 if u_fs is None else u_fs),
            "u_pressure_plane_R": (0.0 if u_pp is None else u_pp),
            "node_offset_R": offs,
            "u_serialization_R": u_ser,
            "u_artifact_R": (0.0 if u_total is None else u_total),
            "artifact_upper": (abs(R - 1.0) if upper is None else upper),
            "pass": bool(complete and upper <= ARTIFACT_BUDGET_R_ABS),
            "evidence_complete": bool(complete),
            "lineage": {
                "R_point": "NORMAL blocked/open pair only",
                "u_fixed_step_R": "this pair's own fixed-step audits",
                "u_pressure_plane_R": ("R_offset_j = C_open_offset_j / C_blocked_offset_j from "
                                       "this pair's OWN exactly paired records; a missing or "
                                       "unpairable summary FAILS the evidence rather than "
                                       "contributing zero (errata PE-32, PE-42)"),
                "u_serialization_R": "frozen record precision",
                "overlaps": "no term appears in more than one sum",
                "used_in": "artifact admission and the reachable-set inequality",
            },
        }
        if not complete:
            ev["reason"] = ("incomplete: %s" % ", ".join(
                [s for s, ok in (("no fixed-step audit pair", u_fs is not None),
                                 ("no paired node-offset evidence", u_pp is not None))
                 if not ok]))
        out["%d.%s" % (S, level)] = assert_artifact_evidence(ev)
    return out


# ---- the FINAL audit-adjusted zero-driver pressure verdict (errata PE-60, PE-61) --------------
# C4 implemented lateral_pressure_upper_bounds() and no production caller invoked it: P1b
# admission, P2a eligibility and the P2b ledger all decided without it, while a point mean-gap
# screen carried the name of the final verdict. Everything below puts that calculation ON the
# decision path, with its full normal/audit lineage retained.

#: Every field a pressure verdict must retain (erratum PE-60 §5.4).
PRESSURE_EVIDENCE_FIELDS = (
    "candidate_id", "resolution", "forcing_level",
    "normal_case_id", "normal_record_sha256", "audit_case_id", "audit_record_sha256",
    "face_ids", "paired_mask_sha256", "face_indices", "footprint_x", "footprint_z",
    "fixture_mask_sha256",
    "normal_mean_delta_p", "normal_max_abs_delta_p",
    "audit_mean_delta_p", "audit_max_abs_delta_p",
    "u_mean_gap", "u_max_gap", "u_serialization_mean", "u_serialization_max",
    "axial_pressure_scale", "mean_gap_upper_rel", "max_gap_upper_rel",
    "tolerance", "mean_pass", "max_pass", "pass", "reason", "overlaps",
    "evidence_complete", "point_pass", "spatial_sd_delta_p", "spatial_sd_role",
)


def assert_pressure_evidence(ev):
    """Validate the pressure-evidence schema BEFORE any scientific use (erratum PE-60)."""
    missing = [k for k in PRESSURE_EVIDENCE_FIELDS if k not in ev]
    if missing:
        raise ValueError("pressure evidence is missing %r" % (missing,))
    if ev["normal_case_id"] is not None and ev["normal_case_id"] == ev["audit_case_id"]:
        raise ValueError("a case is cited as both the normal and the audit pressure record")
    for k in ("normal_record_sha256", "audit_record_sha256"):
        if ev[k] is not None:
            assert_flat_hash_list([ev[k]], "pressure evidence %s" % k)
    return ev


def _pressure_delta_of(rec):
    """The exact paired face-difference record retained inside a case record."""
    lp = (rec.get("scientific") or {}).get("lateral_pressure")
    if not lp:
        return None
    d = lp.get("delta_pointwise")
    return dict(d) if d else None


def _pressure_face_fingerprint(rec):
    """The exact face footprints and mask hashes a normal and its audit must share."""
    faces = (rec.get("scientific") or {}).get("pressure_faces") or []
    by = {f["plane_id"]: f for f in faces}
    if set(by) != set(PRESSURE_FACE_IDS):
        return None
    return {
        "face_ids": list(PRESSURE_FACE_IDS),
        "face_indices": [int(by[p]["index"]) for p in PRESSURE_FACE_IDS],
        "footprint_x": [list(by[p]["footprint_x"]) for p in PRESSURE_FACE_IDS],
        "footprint_z": [list(by[p]["footprint_z"]) for p in PRESSURE_FACE_IDS],
        "fixture_mask_sha256": sorted({by[p]["mask_sha256"] for p in PRESSURE_FACE_IDS}),
    }


def _incomplete_pressure_evidence(key, S, level, reason, **kw):
    ev = {k: None for k in PRESSURE_EVIDENCE_FIELDS}
    ev.update(candidate_id="w%d_kz%d" % key, resolution=S, forcing_level=level,
              tolerance=TOL_LATERAL_DRIVER_REL, evidence_complete=False,
              reason=reason, overlaps=("u_mean_gap and u_max_gap come from the same fixed-step "
                                       "pair but bound different statistics; neither is added to "
                                       "the other"),
              spatial_sd_role="SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND")
    ev["pass"] = False
    ev.update(kw)
    return assert_pressure_evidence(ev)


def lateral_pressure_evidence_from_records(records, bridge_key):
    """The FINAL zero-driver pressure verdict for one candidate, per (resolution, forcing level).

    For every identical-path OPEN control record this loads the NORMAL record, locates its EXACT
    fixed-step audit through ``audit_of_case_id``, validates audit/base compatibility and exact
    pressure-face footprints and mask hashes in both, then calls
    :func:`lateral_pressure_upper_bounds` with the normal's own axial pressure scale.

    The verdict requires BOTH ``mean_gap_upper_rel <= TOL_LATERAL_DRIVER_REL`` AND
    ``max_gap_upper_rel <= TOL_LATERAL_DRIVER_REL``. Missing audit evidence, mismatched faces, a
    non-finite value, an incomplete upper bound or either failed inequality makes the combination
    unavailable. The spatial standard deviation stays diagnostic (erratum PE-44).
    """
    out = {}
    normals = {cid: r for cid, r in _normal_only(records, "identical_path_control",
                                                 bridge_key).items()
               if r["row"]["state"] == "open"}
    audits = _audits_for(records, "identical_path_control", bridge_key)
    by_base = {}
    for cid, a in audits.items():
        base_id = a["row"].get("audit_of_case_id")
        if base_id is not None:
            by_base[base_id] = a
    for cid, nrec in sorted(normals.items()):
        S, level = nrec["row"]["S"], nrec["row"]["forcing_level"]
        combo = "%d.%s" % (S, level)
        n_delta = _pressure_delta_of(nrec)
        n_face = _pressure_face_fingerprint(nrec)
        n_sci = nrec.get("scientific") or {}
        lp = n_sci.get("lateral_pressure") or {}
        if n_delta is None or n_face is None:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "the normal record carries no paired lateral pressure evidence",
                normal_case_id=cid, normal_record_sha256=record_hash(nrec))
            continue
        arec = by_base.get(cid)
        base_fields = dict(n_face, normal_case_id=cid,
                           normal_record_sha256=record_hash(nrec),
                           normal_mean_delta_p=n_delta["mean_delta_p"],
                           normal_max_abs_delta_p=n_delta["max_abs_delta_p"],
                           paired_mask_sha256=n_delta["paired_mask_sha256"],
                           spatial_sd_delta_p=n_delta["spatial_sd_delta_p"],
                           point_pass=lp.get("measured_zero_driver_point_pass"))
        if arec is None:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "no fixed-step audit names this normal case; an upper-bound verdict cannot be "
                "formed and the combination is unavailable (erratum PE-46)", **base_fields)
            continue
        try:
            assert_audit_compatible(arec["row"], nrec["row"])
        except ValueError as exc:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "the cited fixed-step audit is not compatible with its base: %s" % exc,
                audit_case_id=arec["case_id"], audit_record_sha256=record_hash(arec),
                **base_fields)
            continue
        a_delta = _pressure_delta_of(arec)
        a_face = _pressure_face_fingerprint(arec)
        if a_delta is None or a_face is None:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "the fixed-step audit carries no paired lateral pressure evidence",
                audit_case_id=arec["case_id"], audit_record_sha256=record_hash(arec),
                **base_fields)
            continue
        if a_face != n_face or a_delta["paired_mask_sha256"] != n_delta["paired_mask_sha256"]:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "the audit's pressure-face footprints or mask hashes differ from its base; an "
                "upper bound may never be formed across two different faces",
                audit_case_id=arec["case_id"], audit_record_sha256=record_hash(arec),
                audit_mean_delta_p=a_delta["mean_delta_p"],
                audit_max_abs_delta_p=a_delta["max_abs_delta_p"], **base_fields)
            continue
        scale = n_sci.get("dP")
        try:
            ub = lateral_pressure_upper_bounds(n_delta, scale, audit_delta=a_delta,
                                               expected_zero_driver=True)
        except (ValueError, NonFiniteValue, TypeError) as exc:
            out[combo] = _incomplete_pressure_evidence(
                bridge_key, S, level,
                "the pressure upper bound could not be formed: %s" % exc,
                audit_case_id=arec["case_id"], audit_record_sha256=record_hash(arec),
                audit_mean_delta_p=a_delta["mean_delta_p"],
                audit_max_abs_delta_p=a_delta["max_abs_delta_p"], **base_fields)
            continue
        ev = dict(base_fields)
        ev.update(
            candidate_id="w%d_kz%d" % bridge_key, resolution=S, forcing_level=level,
            audit_case_id=arec["case_id"], audit_record_sha256=record_hash(arec),
            audit_mean_delta_p=a_delta["mean_delta_p"],
            audit_max_abs_delta_p=a_delta["max_abs_delta_p"],
            u_mean_gap=ub["u_mean_gap"], u_max_gap=ub["u_max_gap"],
            u_serialization_mean=ub["u_serialization_mean"],
            u_serialization_max=ub["u_serialization_max"],
            axial_pressure_scale=ub["axial_pressure_scale"],
            mean_gap_upper_rel=ub["mean_gap_upper_rel"],
            max_gap_upper_rel=ub["max_gap_upper_rel"],
            tolerance=ub["tolerance"], mean_pass=ub["mean_pass"], max_pass=ub["max_pass"],
            spatial_sd_role=ub["spatial_sd_role"], overlaps=ub["overlaps"],
            evidence_complete=True, reason=ub["reason"])
        ev["pass"] = bool(ub["pass"])
        ev["upper_bound"] = ub
        out[combo] = assert_pressure_evidence(ev)
    return out


def zero_driver_mass_flux_from_records(records, bridge_key):
    """The zero-driver lateral MASS-FLUX verdict per (resolution, forcing level).

    Recomputed from the identical-path OPEN records' own transverse controls rather than trusted
    from a stored eligibility flag (erratum PE-60 §5.3).
    """
    out = {}
    normals = {cid: r for cid, r in _normal_only(records, "identical_path_control",
                                                 bridge_key).items()
               if r["row"]["state"] == "open"}
    for cid, rec in sorted(normals.items()):
        S, level = rec["row"]["S"], rec["row"]["forcing_level"]
        tc = (rec.get("scientific") or {}).get("transverse_conservation") or {}
        entry = {
            "candidate_id": "w%d_kz%d" % bridge_key, "resolution": S, "forcing_level": level,
            "case_id": cid, "record_sha256": record_hash(rec),
            "status": tc.get("status"),
            "expected_zero_driver": tc.get("expected_zero_driver"),
            "magnitude_pass": tc.get("magnitude_pass"),
            "consistency_pass": tc.get("consistency_pass"),
            "max_abs_lateral_mass_flux_rel": tc.get("max_abs_lateral_mass_flux_rel"),
            "plane_range_mass_rel": tc.get("plane_range_mass_rel"),
            "tolerance": TOL_BRIDGE_LEAKAGE_REL,
        }
        entry["pass"] = bool(tc.get("expected_zero_driver") and tc.get("pass") is True)
        if not entry["pass"]:
            entry["reason"] = ("the identical-path open control did not return a passing "
                               "expected-zero-driver transverse verdict")
        out["%d.%s" % (S, level)] = entry
    return out


def candidate_admission_from_records(records_by_case):
    """The COMPLETE P1b candidate verdict (erratum PE-60 §5.3).

    Final artifact admission requires, at EVERY required (resolution, forcing level):

      * complete blocked/open R evidence;
      * the artifact upper-bound pass;
      * the zero-driver lateral mass-flux pass;
      * the final pressure MEAN upper-bound pass;
      * the final pressure MAXIMUM upper-bound pass;
      * exact audit lineage for all of the above.

    P2a eligibility is derived from this verdict; no stored eligibility boolean is trusted.
    """
    artifact = artifact_admission_from_records(records_by_case)
    want = sorted({"%d.%s" % (S, lv) for S in SCIENTIFIC_RESOLUTIONS for lv in FORCING_LEVELS})
    out = {}
    for key, art in sorted(artifact.items()):
        press = lateral_pressure_evidence_from_records(records_by_case, key)
        mass = zero_driver_mass_flux_from_records(records_by_case, key)
        missing = {
            "artifact": sorted(set(want) - set(art["combinations"])),
            "pressure": sorted(set(want) - set(press)),
            "lateral_mass_flux": sorted(set(want) - set(mass)),
        }
        failed = {
            "artifact": sorted(c for c, v in art["combinations"].items() if not v["pass"]),
            "pressure_mean": sorted(c for c, v in press.items() if v.get("mean_pass") is not True),
            "pressure_max": sorted(c for c, v in press.items() if v.get("max_pass") is not True),
            "lateral_mass_flux": sorted(c for c, v in mass.items() if not v["pass"]),
        }
        entry = {
            "w": key[0], "kz": key[1], "candidate_id": "w%d_kz%d" % key,
            "required_combinations": want,
            "artifact": art, "pressure": press, "lateral_mass_flux": mass,
            "missing": missing, "failed": failed,
            "rule": ("P1b final artifact admission = complete blocked/open R evidence AND the "
                     "artifact upper bound AND the zero-driver lateral mass flux AND BOTH "
                     "pressure upper bounds, each with exact audit lineage, at EVERY required "
                     "resolution and forcing level (erratum PE-60)"),
        }
        entry["admitted"] = bool(
            not any(missing.values()) and not any(failed.values()) and art["admitted"])
        if not entry["admitted"]:
            parts = ["missing %s %r" % (k, v) for k, v in sorted(missing.items()) if v]
            parts += ["failed %s %r" % (k, v) for k, v in sorted(failed.items()) if v]
            entry["reason"] = "; ".join(parts) or (art["reason"] or "artifact not admitted")
        else:
            entry["reason"] = None
        out[key] = entry
    return out


def artifact_admission_from_records(records_by_case):
    """Recompute the artifact upper bound for every candidate from its OWN evidence, at every
    required (resolution, forcing level) combination."""
    keys = sorted({_bridge_key(r) for r in records_by_case.values()
                   if r.get("kind") == "identical_path_control" and _bridge_key(r)})
    want = {"%d.%s" % (S, lv) for S in SCIENTIFIC_RESOLUTIONS for lv in FORCING_LEVELS}
    per = {}
    for key in keys:
        ev = artifact_evidence_from_records(records_by_case, key)
        e = {"w": key[0], "kz": key[1], "combinations": ev,
             "required_combinations": sorted(want),
             "missing": sorted(want - set(ev)), "admitted": False, "reason": None}
        e["admitted"] = bool(not e["missing"] and all(v["pass"] for v in ev.values()))
        if not e["admitted"]:
            e["reason"] = ("missing required combinations %r" % (e["missing"],) if e["missing"]
                           else "; ".join(sorted({v.get("reason") or "exceeds the artifact budget"
                                                  for v in ev.values() if not v["pass"]})))
        per[key] = e
    return per


def p1a_triage(records_by_case):
    """P1a is a TRIAGE SCREEN (erratum PE-17). It may REJECT — the point estimate alone can make
    success impossible, every omitted term being non-negative — but it may NEVER ADMIT."""
    verdicts = {}
    normals = _normal_only(records_by_case, "identical_path_control")
    by = {}
    for r in normals.values():
        if r["row"]["phase"] != "P1a":
            continue
        key = _bridge_key(r)
        if key:
            by.setdefault((key, r["row"]["S"], r["row"]["forcing_level"]), {})[
                r["row"]["state"]] = r
    for (key, S, level), states in sorted(by.items()):
        v = verdicts.setdefault(key, {"w": key[0], "kz": key[1], "point_estimates": [],
                                      "rejected": False, "reason": None,
                                      "verdict": "CONTINUE_PENDING_FIXED_STEP_EVIDENCE",
                                      "may_admit": False})
        if set(states) != {"blocked", "open"}:
            continue
        Cb, Co = _conductance(states["blocked"]), _conductance(states["open"])
        if Cb == 0.0:
            continue
        pt = abs(Co / Cb - 1.0)
        v["point_estimates"].append(pt)
        if pt > ARTIFACT_BUDGET_R_ABS:
            v["rejected"] = True
            v["verdict"] = "REJECTED_POINT_ESTIMATE_ALONE_EXCEEDS_BUDGET"
            v["reason"] = ("|R-1| = %.6g at S=%d already exceeds ARTIFACT_BUDGET_R_ABS = %.6g, "
                           "and every omitted uncertainty term is non-negative, so no additional "
                           "evidence can rescue it" % (pt, S, ARTIFACT_BUDGET_R_ABS))
    for v in verdicts.values():
        v["point_estimates"].sort()
    return verdicts


def derive_expected_rows(phase, matrix_rows, predecessor_records=None):
    """The exact rows a phase must run, DERIVED mechanically (erratum PE-18) — never supplied by
    a caller. P0/P1a are unconditional; P1b and P2a follow from validated predecessor decisions."""
    rows = [r for r in matrix_rows if r["phase"] == phase]
    if phase in ("P0", "P1a"):
        return rows, {"rule": "unconditional"}
    recs = predecessor_records or {}
    if phase == "P1b":
        triage = p1a_triage(recs)
        surviving = {k for k, v in triage.items() if not v["rejected"]}
        keep = [r for r in rows if _bridge_key(r) is None or _bridge_key(r) in surviving]
        return keep, {"rule": "candidates surviving the P1a triage screen",
                      "surviving": sorted(surviving),
                      "triage": {"%d_%d" % k: v for k, v in sorted(triage.items())}}
    if phase == "P2a":
        # erratum PE-60: P2a eligibility is derived from the COMPLETE P1b candidate verdict —
        # artifact upper bound AND zero-driver lateral mass flux AND both pressure upper bounds —
        # never from the artifact alone and never from a stored eligibility boolean.
        admitted = candidate_admission_from_records(recs)
        keep_keys = {k for k, v in admitted.items() if v["admitted"]}
        keep = [r for r in rows if _bridge_key(r) is None or _bridge_key(r) in keep_keys]
        return keep, {"rule": "candidates whose COMPLETE P1b verdict — artifact upper bound, "
                              "zero-driver lateral mass flux and BOTH pressure upper bounds — "
                              "passes at EVERY required combination with exact audit lineage",
                      "admitted": sorted(keep_keys),
                      "candidate_admission": {"%d_%d" % k: v
                                              for k, v in sorted(admitted.items())}}
    return rows, {"rule": "unconditional"}


# ---- phase manifests --------------------------------------------------------------------------

#: Frozen refusal reasons. Every refused row carries exactly one (erratum PE-26).
REFUSAL_REASONS = (
    "ADAPTIVELY_INELIGIBLE",          # a member of the universe that the derived plan excludes
    "REFUSED_AFTER_PHASE_STOP",       # eligible, but the phase had already stopped
)


def phase_universe(phase, matrix_rows):
    """EVERY canonical row belonging to a phase. Adaptively ineligible rows remain members
    (erratum PE-26): the superseded executor refused them while the validator built its universe
    from the eligible subset and then rejected them as extra."""
    return [r for r in matrix_rows if r["phase"] == phase]


#: Fields a replicate or a fixed-step audit must share EXACTLY with its base (erratum PE-59).
#: The superseded executor inferred the base by searching for the first row that shared only S,
#: state, variant, forcing level and run mode.
BASE_BINDING_FIELDS = ("kind", "S", "forcing_level", "forcing_exact", "tau_plus", "state",
                       "variant", "bridge", "coupon_level", "coupon_orientation", "swapped",
                       "perturbation", "obstructed", "backend")


def assert_replicate_compatible(replicate_row, base_row):
    """A replicate must be the SAME configuration as its explicitly named base."""
    if replicate_row.get("replicate_of_case_id") != base_row["case_id"]:
        raise ValueError("replicate %r does not name base %r"
                         % (replicate_row["case_id"], base_row["case_id"]))
    if base_row["kind"] == "determinism_replicate":
        raise ValueError("a replicate may not name another replicate as its base")
    for f in BASE_BINDING_FIELDS:
        if f == "kind":
            continue
        if replicate_row.get(f) != base_row.get(f):
            raise ValueError("replicate %r differs from its base on %r: %r vs %r"
                             % (replicate_row["case_id"], f, replicate_row.get(f),
                                base_row.get(f)))
    if replicate_row["run_mode"] != base_row["run_mode"]:
        raise ValueError("a replicate must share its base's run mode")
    return True


def assert_audit_compatible(audit_row, base_row):
    """A fixed-step audit must be the same configuration as its explicitly named normal base,
    differing only in the fields fixed-step mode deliberately changes."""
    if audit_row.get("audit_of_case_id") != base_row["case_id"]:
        raise ValueError("audit %r does not name base %r"
                         % (audit_row["case_id"], base_row["case_id"]))
    if base_row["run_mode"] != "NORMAL":
        raise ValueError("a fixed-step audit must name a NORMAL base")
    for f in BASE_BINDING_FIELDS:
        if audit_row.get(f) != base_row.get(f):
            raise ValueError("audit %r differs from its base on %r" % (audit_row["case_id"], f))
    return True


#: Frozen case-level failure reasons, in evaluation order.
CASE_FAILURE_REASONS = ("NORMAL_UNCONVERGED", "FIXED_STEP_AUDIT_INCOMPLETE", "LOW_MACH_FAILED",
                        "MASS_CONSERVATION_FAILED", "TRANSVERSE_CONTROL_FAILED",
                        "MEASURED_LATERAL_DRIVER_NONZERO", "PRESSURE_FACES_DO_NOT_PAIR",
                        "NODE_OFFSET_SUMMARY_INCOMPLETE")


def case_decision_verdict(row, scientific, execution_status):
    """The ONE case-level scientific classification (erratum PE-58).

    Used by the executor when it builds its ledgers AND by ``validate_phase_manifest`` after it
    reopens each record, so a manifest cannot relabel a scientifically failed case as completed or
    invent a different failure reason. Phase-level forcing, resolution and candidate gates are
    aggregate controls and are deliberately NOT evaluated here.
    """
    sci = scientific or {}
    if execution_status == "NORMAL_UNCONVERGED":
        return {"pass": False, "reason": "NORMAL_UNCONVERGED", "applicability": "always",
                "effect": "STOPS_THE_PHASE"}
    if execution_status == "FIXED_STEP_AUDIT_INCOMPLETE":
        return {"pass": False, "reason": "FIXED_STEP_AUDIT_INCOMPLETE", "applicability": "audit",
                "effect": "STOPS_THE_PHASE"}
    mach = sci.get("mach") or {}
    if mach and not mach.get("pass"):
        return {"pass": False, "reason": "LOW_MACH_FAILED", "applicability": "every solved case",
                "effect": "STOPS_THE_PHASE"}
    cons = sci.get("conservation")
    if cons and not cons.get("mass_conservation_pass"):
        return {"pass": False, "reason": "MASS_CONSERVATION_FAILED",
                "applicability": "fixture cases", "effect": "STOPS_THE_PHASE"}
    tc = sci.get("transverse_conservation")
    if tc and tc.get("pass") is False:
        return {"pass": False, "reason": "TRANSVERSE_CONTROL_FAILED",
                "applicability": "bridge-carrying cases", "effect": "STOPS_THE_PHASE"}
    lp = sci.get("lateral_pressure")
    if lp:
        if lp.get("masks_pair_exactly") is False:
            return {"pass": False, "reason": "PRESSURE_FACES_DO_NOT_PAIR",
                    "applicability": "bridge-carrying cases", "effect": "STOPS_THE_PHASE"}
        # Erratum PE-61: the case-level screen consumes the POINT estimate, which may only
        # REJECT. The final admission verdict is the paired normal/audit upper bound and is
        # formed at P1b/P2b, never here — a case record has no access to its own audit.
        if lp.get("measured_zero_driver_point_pass") is False:
            return {"pass": False, "reason": "MEASURED_LATERAL_DRIVER_NONZERO",
                    "applicability": "expected-zero-driver cases", "effect": "STOPS_THE_PHASE"}
    no = sci.get("node_offsets")
    if no is not None and not no.get("all_finite"):
        return {"pass": False, "reason": "NODE_OFFSET_SUMMARY_INCOMPLETE",
                "applicability": "fixture cases", "effect": "STOPS_THE_PHASE"}
    return {"pass": True, "reason": None, "applicability": "case-level execution validity",
            "effect": "NONE"}


def make_phase_manifest(phase, universe_rows, eligible_rows, completed, refused, failed,
                        authority, predecessor_manifests, adaptive, terminal_status,
                        terminal_stop_reason=None, provenance_mode="PRODUCTION",
                        replicates=(), phase_science=None):
    """A validated phase LEDGER over the FULL phase universe.

    ``phase_science`` carries the phase's durable AGGREGATE scientific verdict (erratum PE-64).
    For P0 it is :func:`p0_aggregate_science`, and the validator recomputes it from the records
    rather than taking the manifest's word for it.
    """
    if terminal_status not in TERMINAL_PHASE_STATUSES:
        raise ValueError("unknown terminal phase status %r" % (terminal_status,))
    uni = [dict(r) for r in universe_rows]
    elig = [dict(r) for r in eligible_rows]
    elig_ids = [r["case_id"] for r in elig]
    uni_ids = [r["case_id"] for r in uni]
    doc = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": phase,
        "provenance_mode": provenance_mode,
        "source_commit": authority["source_commit"],
        "source_tree": authority["source_tree"],
        "execution_authority_sha256": record_hash(authority),
        "full_matrix_sha256": record_hash(execution_matrix()),
        "phase_universe_sha256": record_hash(uni),
        "phase_plan_sha256": record_hash(elig),
        "phase_universe_case_ids": uni_ids,
        "mandatory_case_ids": [r["case_id"] for r in uni if r["class"] == "mandatory"],
        "conditionally_eligible_case_ids": [i for i in elig_ids
                                            if i in set(uni_ids)],
        "adaptively_ineligible_case_ids": [i for i in uni_ids if i not in set(elig_ids)],
        "expected_row_sha256": {r["case_id"]: row_sha256(r) for r in uni},
        "predecessor_manifests": dict(predecessor_manifests),
        "completed": [dict(c) for c in completed],
        "refused": [dict(c) for c in refused],
        "failed": [dict(c) for c in failed],
        "replicates": [dict(r) for r in replicates],
        "adaptive": dict(adaptive),
        "phase_science": (None if phase_science is None else dict(phase_science)),
        "phase_science_sha256": (None if phase_science is None else record_hash(phase_science)),
        "terminal_status": terminal_status,
        "terminal_stop_reason": terminal_stop_reason,
        "counts": {"universe": len(uni), "eligible": len(elig), "completed": len(completed),
                   "refused": len(refused), "failed": len(failed)},
    }
    doc.update(config_hashes())
    return doc


#: Phases that must publish a durable AGGREGATE scientific verdict (erratum PE-64). The validator
#: recomputes each from the reopened records; a later phase refuses on anything but a complete,
#: passing verdict.
PHASE_AGGREGATE_SCIENCE = {"P0": lambda recs: p0_aggregate_science(recs)}


def validate_phase_manifest(phase, runs_dir, authority=None, matrix_rows=None,
                            predecessor_records=None, require_production=True):
    """Reopen and rehash EVERYTHING, over the FULL phase universe (errata PE-18, PE-26)."""
    base = pathlib.Path(runs_dir)
    doc = _load_json(base / ("manifest_%s.json" % phase), "the %s completion manifest" % phase)
    if doc.get("phase") != phase:
        raise ManifestMissing("the %s manifest declares phase %r" % (phase, doc.get("phase")))
    if doc.get("correction_version") != CORRECTION_VERSION:
        raise ManifestMissing("the %s manifest was produced under correction version %r, not %r"
                              % (phase, doc.get("correction_version"), CORRECTION_VERSION))
    if require_production and doc.get("provenance_mode") != "PRODUCTION":
        raise ManifestMissing(
            "the %s manifest carries provenance_mode=%r; production validation accepts PRODUCTION "
            "manifests only (erratum PE-34)" % (phase, doc.get("provenance_mode")))
    want = config_hashes()
    bad = {k: (doc.get(k), v) for k, v in want.items() if doc.get(k) != v}
    if bad:
        raise ManifestMissing("the %s manifest is bound to a different configuration: %s"
                              % (phase, sorted(bad)))
    if doc.get("full_matrix_sha256") != record_hash(execution_matrix()):
        raise ManifestMissing("the %s manifest cites a different full matrix" % (phase,))

    rows = matrix_rows if matrix_rows is not None else execution_matrix()["rows"]
    uni = phase_universe(phase, rows)
    eligible, adaptive = derive_expected_rows(phase, rows,
                                              predecessor_records=predecessor_records)
    if doc.get("phase_universe_sha256") != record_hash([dict(r) for r in uni]):
        raise ManifestMissing("the %s manifest's universe is not the canonical phase universe"
                              % (phase,))
    if doc.get("phase_plan_sha256") != record_hash([dict(r) for r in eligible]):
        raise ManifestMissing(
            "the %s manifest's eligible plan does not match the plan derived mechanically from "
            "the matrix and its validated predecessors (erratum PE-18)" % (phase,))
    if doc.get("adaptive", {}).get("rule") != adaptive.get("rule"):
        raise ManifestMissing("the %s manifest's adaptive rule is not the derived one" % (phase,))

    by_row = {r["case_id"]: r for r in uni}
    elig_ids = {r["case_id"] for r in eligible}
    comp_list, ref_list, fail_list = (doc.get("completed", []), doc.get("refused", []),
                                      doc.get("failed", []))
    completed = {c["case_id"]: c for c in comp_list}
    refused = {c["case_id"]: c for c in ref_list}
    failed = {c["case_id"]: c for c in fail_list}
    for name, seq, uniq in (("completed", comp_list, completed), ("refused", ref_list, refused),
                            ("failed", fail_list, failed)):
        if len(seq) != len(uniq):
            raise ManifestMissing("the %s manifest lists a %s case twice" % (phase, name))
    # EXACT, mutually exclusive partition of the full universe
    overlaps = ((set(completed) & set(refused)) | (set(completed) & set(failed))
                | (set(refused) & set(failed)))
    if overlaps:
        raise ManifestMissing("the %s manifest places %r in more than one ledger"
                              % (phase, sorted(overlaps)[:5]))
    union = set(completed) | set(refused) | set(failed)
    extra = sorted(union - set(by_row))
    if extra:
        raise ManifestMissing("the %s manifest carries cases outside its phase universe: %r"
                              % (phase, extra[:5]))
    missing = sorted(set(by_row) - union)
    if missing:
        raise ManifestMissing("the %s manifest leaves %d universe rows unaccounted for: %r"
                              % (phase, len(missing), missing[:5]))
    # refusals must be justified, and adaptive refusal is RECOMPUTED, never taken on trust
    for cid, entry in refused.items():
        reason = entry.get("reason")
        if reason not in REFUSAL_REASONS:
            raise ManifestMissing("refused case %r carries an unknown reason %r" % (cid, reason))
        if entry.get("row_sha256") != row_sha256(by_row[cid]):
            raise ManifestMissing("refused case %r cites the wrong matrix-row hash" % (cid,))
        if reason == "ADAPTIVELY_INELIGIBLE" and cid in elig_ids:
            raise ManifestMissing("case %r is eligible under the derived plan but was refused as "
                                  "adaptively ineligible" % (cid,))
        if reason == "REFUSED_AFTER_PHASE_STOP" and doc["terminal_status"] == "PHASE_COMPLETE":
            raise ManifestMissing("case %r was refused after a phase stop, but the phase reports "
                                  "PHASE_COMPLETE" % (cid,))
    ineligible = {r["case_id"] for r in uni} - elig_ids
    not_refused = sorted(ineligible - set(refused))
    if not_refused:
        raise ManifestMissing("adaptively ineligible rows %r are not recorded as refused"
                              % (not_refused[:5],))
    for cid in set(completed) | set(failed):
        if cid not in elig_ids:
            raise ManifestMissing("case %r was executed although the derived plan excludes it"
                                  % (cid,))

    records, seen_hash = {}, {}
    for cid in sorted(set(completed) | set(failed)):
        entry = completed.get(cid) or failed[cid]
        rec, path = read_case_record(base, cid)
        raw = pathlib.Path(path).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if entry.get("record_sha256") != actual:
            raise ManifestMissing("the %s manifest cites record hash %r for %r; the file hashes "
                                  "to %r" % (phase, entry.get("record_sha256"), cid, actual))
        if raw.decode() != canonical_json(rec) + "\n":
            raise ManifestMissing("case record %r is not canonically serialised" % (cid,))
        validate_case_record(rec, row=by_row[cid], authority=authority, phase=phase)
        if require_production:
            assert_production_record(rec)
        if entry.get("row_sha256") != row_sha256(by_row[cid]):
            raise ManifestMissing("the %s manifest cites the wrong row hash for %r"
                                  % (phase, cid))
        prev = seen_hash.get(actual)
        if prev is not None and row_sha256(by_row[prev]) != row_sha256(by_row[cid]):
            raise ManifestMissing(
                "record hash %r is cited for two physically distinct rows (%r and %r); one hash "
                "may never bind two different cases" % (actual, prev, cid))
        seen_hash[actual] = cid
        # erratum PE-58: recompute the scientific verdict and require the ledger to agree
        verdict = case_decision_verdict(by_row[cid], rec.get("scientific"), rec["status"])
        if cid in completed and not verdict["pass"]:
            raise ManifestMissing(
                "case %r is listed as COMPLETED but recomputes as failed (%s); a manifest may "
                "not relabel a scientifically failed case (erratum PE-58)"
                % (cid, verdict["reason"]))
        if cid in failed:
            if verdict["pass"]:
                raise ManifestMissing(
                    "case %r is listed as FAILED but recomputes as passing; a manifest may not "
                    "invent a failure (erratum PE-58)" % (cid,))
            if entry.get("reason") != verdict["reason"]:
                raise ManifestMissing(
                    "case %r records failure reason %r; it recomputes as %r"
                    % (cid, entry.get("reason"), verdict["reason"]))
        if cid in completed:
            records[cid] = rec

    if doc.get("terminal_status") not in TERMINAL_PHASE_STATUSES:
        raise ManifestMissing("the %s manifest has no valid terminal status" % (phase,))
    counts = doc.get("counts") or {}
    if (counts.get("universe") != len(uni) or counts.get("completed") != len(completed)
            or counts.get("refused") != len(refused) or counts.get("failed") != len(failed)):
        raise ManifestMissing("the %s manifest's counts do not reconcile to its universe"
                              % (phase,))
    # PE-37: a claimed determinism replicate must actually reproduce its base payload
    for rep in doc.get("replicates", []):
        base_id, rep_id = rep.get("base_case_id"), rep.get("replicate_case_id")
        for cid in (base_id, rep_id):
            if cid not in records:
                raise ManifestMissing("replicate cites %r, which is not a completed case" % (cid,))
        if (records[base_id].get("scientific_payload_sha256")
                != records[rep_id].get("scientific_payload_sha256")):
            raise ManifestMissing(
                "replicate %r does not reproduce the scientific payload of its base %r; the "
                "byte-identical claim is not enforced by assertion (erratum PE-37)"
                % (rep_id, base_id))
        if rep.get("pass") is not True:
            raise ManifestMissing("replicate %r is not recorded as passing" % (rep_id,))
    # PE-64: the phase's durable AGGREGATE scientific verdict is RECOMPUTED from the reopened
    # records and must match the manifest exactly. A manifest may not assert a P0 verdict its own
    # records do not support, and it may not omit one.
    if phase in PHASE_AGGREGATE_SCIENCE:
        want_sci = PHASE_AGGREGATE_SCIENCE[phase](records)
        got_sci = doc.get("phase_science")
        if got_sci is None:
            raise ManifestMissing(
                "the %s manifest carries no aggregate scientific verdict; %s must produce one "
                "before a later phase may consume it (erratum PE-64)" % (phase, phase))
        if record_hash(got_sci) != record_hash(want_sci):
            raise ManifestMissing(
                "the %s manifest's aggregate scientific verdict does not recompute from its own "
                "records (erratum PE-64)" % (phase,))
        if doc.get("phase_science_sha256") != record_hash(want_sci):
            raise ManifestMissing("the %s manifest cites a stale phase_science hash" % (phase,))
        doc["_phase_science"] = want_sci
    doc["_records"] = records
    return doc


def validate_p2b_manifest(runs_dir, require_production=True,
                          expected_assembly_authority_sha256=None, matrix_rows=None):
    """Reopen and validate the whole P2b artifact set (errata PE-53, PE-70, PE-72, PE-73).

    C4 checked predecessor manifest FILE HASHES only, so a P2b manifest citing a correct hash for
    an internally invalid P0 passed; it also carried an ``authority`` parameter it never read.
    Both are corrected here:

      * every predecessor is RECURSIVELY revalidated with the strong phase validator, in exact
        dependency order — reopening each manifest, rehashing each record, recomputing every
        case-level verdict and the P0 aggregate controls, checking the full-universe partition
        and the adaptive decisions, and requiring PHASE_COMPLETE and PRODUCTION provenance;
      * the embedded P2b assembly authority is reconstructed and validated, and
        ``expected_assembly_authority_sha256`` is load-bearing when supplied.
    """
    base = pathlib.Path(runs_dir)
    doc = _load_json(base / "manifest_P2b.json", "the P2b assembly manifest")
    if doc.get("correction_version") != CORRECTION_VERSION:
        raise ManifestMissing("the P2b manifest is from a superseded correction version")
    if require_production and doc.get("provenance_mode") != "PRODUCTION":
        raise ManifestMissing("the P2b manifest carries provenance_mode=%r; production "
                              "validation accepts PRODUCTION only" % (doc.get("provenance_mode"),))
    if doc.get("provenance_mode") not in ("PRODUCTION", "TEST_ONLY"):
        raise ManifestMissing("the P2b manifest declares an unknown provenance mode %r"
                              % (doc.get("provenance_mode"),))
    if doc.get("phase") != "P2b" or doc.get("phase_kind") != "ARITHMETIC_ASSEMBLY_NO_SOLVER_CALL":
        raise ManifestMissing("the P2b manifest does not declare an arithmetic assembly phase")
    if doc.get("solver_records"):
        raise ManifestMissing("the P2b manifest cites solver records; P2b never calls the solver")
    want = config_hashes()
    bad = {k: (doc.get(k), v) for k, v in want.items() if doc.get(k) != v}
    if bad:
        raise ManifestMissing("the P2b manifest binds a different configuration: %s"
                              % (sorted(bad),))
    if doc.get("full_matrix_sha256") != record_hash(execution_matrix()):
        raise ManifestMissing("the P2b manifest cites a different full matrix")

    # every predecessor, by exact key set and exact FILE hash ...
    want_keys = set(PHASE_PREREQUISITES["P2b"])
    cited = dict(doc.get("predecessor_manifests") or {})
    if set(cited) != want_keys:
        raise ManifestMissing("the P2b manifest cites predecessors %r; the exact required set is "
                              "%r" % (sorted(cited), sorted(want_keys)))
    for k, sha in cited.items():
        f = base / ("manifest_%s.json" % k)
        if not f.exists():
            raise ManifestMissing("the P2b manifest cites a missing predecessor %s" % k)
        if hashlib.sha256(f.read_bytes()).hexdigest() != sha:
            raise ManifestMissing("the P2b manifest cites a stale hash for predecessor %s" % k)
    # ... and then RECURSIVELY, with the strong phase validator, in exact dependency order.
    # A file hash proves only that the file has not moved; it proves nothing about what is in it
    # (erratum PE-72).
    rows = matrix_rows if matrix_rows is not None else execution_matrix()["rows"]
    pre_records, pre_docs = {}, {}
    for pre in PHASE_PREREQUISITES["P2b"]:
        pdoc = validate_phase_manifest(pre, base, matrix_rows=rows,
                                       predecessor_records=dict(pre_records),
                                       require_production=require_production)
        if pdoc.get("terminal_status") != "PHASE_COMPLETE":
            raise ManifestMissing(
                "the %s manifest terminated %r; P2b may consume a predecessor only at "
                "PHASE_COMPLETE (errata PE-27, PE-72)" % (pre, pdoc.get("terminal_status")))
        if pre in PHASE_AGGREGATE_SCIENCE:
            sci = pdoc.get("_phase_science") or {}
            if not (sci.get("complete") and sci.get("pass")):
                raise ManifestMissing(
                    "the %s aggregate scientific verdict is not complete and passing; P2b may "
                    "not consume it (errata PE-64, PE-72)" % (pre,))
        pre_records.update(pdoc.pop("_records", {}))
        pre_docs[pre] = pdoc
    doc["_predecessor_manifests"] = pre_docs
    doc["_predecessor_records"] = pre_records

    # the assembly authority is load-bearing, not an unused parameter (erratum PE-73)
    doc["_assembly_authority"] = validate_p2b_assembly_authority(
        doc.get("assembly_authority"), base, require_production=require_production,
        expected_assembly_authority_sha256=expected_assembly_authority_sha256)
    if doc.get("assembly_authority_sha256") != doc["_assembly_authority"][
            "assembly_authority_sha256"]:
        raise ManifestMissing("the P2b manifest cites a stale assembly-authority hash")

    ledger_path = base / "candidate_ledger.json"
    if not ledger_path.exists():
        raise ManifestMissing("P2b wrote no candidate ledger")
    ledger = json.loads(ledger_path.read_text())
    if doc.get("candidate_ledger_sha256") != record_hash(ledger):
        raise ManifestMissing("the P2b manifest cites a different candidate ledger")
    if doc.get("n_declared_candidates") != ledger.get("n_declared"):
        raise ManifestMissing("the P2b manifest and its ledger disagree on the candidate count")
    if ledger.get("provenance_mode") != doc.get("provenance_mode"):
        raise ManifestMissing("the candidate ledger and the P2b manifest disagree on provenance")
    if require_production and ledger.get("provenance_mode") != "PRODUCTION":
        raise ManifestMissing("a TEST_ONLY candidate ledger may never satisfy a production gate")

    status = doc.get("selection_status")
    freeze_path = base / "proposed_bridge_freeze.json"
    inst_path = base / "instantiated_p3_p4_matrix.json"
    if status == "DESIGN_BLOCKED":
        if doc.get("terminal_status") != "PHASE_STOPPED_DESIGN_BLOCKED":
            raise ManifestMissing("a design-blocked P2b must terminate PHASE_STOPPED_DESIGN_BLOCKED")
        if doc.get("terminal_stop_reason") not in DESIGN_BLOCKED_REASONS:
            raise ManifestMissing("a design-blocked P2b must carry a frozen reason code")
        for f in (freeze_path, inst_path):
            if f.exists():
                raise ManifestMissing("a design-blocked P2b must write no %s" % f.name)
        doc["_ledger"] = ledger
        return doc
    if status != "SELECTED":
        raise ManifestMissing("unknown P2b selection status %r" % (status,))
    if doc.get("terminal_status") != "PHASE_COMPLETE":
        raise ManifestMissing("a selected P2b must terminate PHASE_COMPLETE")
    for f in (freeze_path, inst_path):
        if not f.exists():
            raise ManifestMissing("a selected P2b must write %s" % f.name)
    freeze = json.loads(freeze_path.read_text())
    inst = json.loads(inst_path.read_text())
    if freeze.get("status") != "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW":
        raise ManifestMissing("P2b may only write a PROPOSED freeze")
    if freeze.get("p3_p4_authorised") is not False:
        raise ManifestMissing("a proposed freeze may never claim P3/P4 authorization")
    for name, art in (("proposed freeze", freeze), ("instantiated matrix", inst)):
        if art.get("provenance_mode") != doc.get("provenance_mode"):
            raise ManifestMissing("the %s and the P2b manifest disagree on provenance" % name)
        if require_production and art.get("provenance_mode") != "PRODUCTION":
            raise ManifestMissing("a TEST_ONLY %s may never satisfy a production gate "
                                  "(erratum PE-71)" % name)
        if art.get("assembly_authority_sha256") != doc.get("assembly_authority_sha256"):
            raise ManifestMissing("the %s binds a different P2b assembly authority" % name)
    # erratum PE-70: the superseded line was a CHAINED comparison,
    #   freeze != inst != recomputed  ==  (freeze != inst) and (inst != recomputed)
    # which passes whenever freeze equals the recomputed value while the file's own key differs.
    # Two independent requirements, so each mismatch pattern is caught on its own.
    if (freeze.get("rows_sha256") != inst.get("rows_sha256")
            or inst.get("rows_sha256") != record_hash(inst["rows"])):
        raise ManifestMissing(
            "the proposed freeze and the instantiated matrix disagree: freeze=%r, matrix key=%r, "
            "recomputed rows=%r" % (freeze.get("rows_sha256"), inst.get("rows_sha256"),
                                    record_hash(inst["rows"])))
    if freeze.get("instantiated_matrix_file_sha256") != hashlib.sha256(
            inst_path.read_bytes()).hexdigest():
        raise ManifestMissing("the proposed freeze cites a stale instantiated-matrix file hash")
    if doc.get("proposed_freeze_sha256") != record_hash(freeze):
        raise ManifestMissing("the P2b manifest cites a different proposed freeze")
    bridges = freeze.get("frozen_bridges") or []
    if len(bridges) != N_FROZEN_BRIDGES:
        raise ManifestMissing("the proposed freeze carries %d bridges; exactly %d are required"
                              % (len(bridges), N_FROZEN_BRIDGES))
    keys = [(b["w"], b["kz"]) for b in bridges]
    if len(set(keys)) != len(keys):
        raise ManifestMissing("the proposed freeze selects a candidate twice")
    seen = {}
    for b in bridges:
        hs = assert_flat_hash_list(b.get("record_hashes") or [], "frozen bridge hashes")
        if not hs:
            raise ManifestMissing("a frozen bridge cites no evidence")
        for h in hs:
            prev = seen.get(h)
            if prev is not None and prev != (b["w"], b["kz"]):
                raise ManifestMissing("record hash %r binds two candidate geometries" % (h,))
            seen[h] = (b["w"], b["kz"])
    for row in inst["rows"]:
        if isinstance(row.get("bridge"), str):
            raise ManifestMissing("the instantiated matrix still carries a placeholder bridge")
        if (row["w"] if "w" in row else row["bridge"]["w"], row["bridge"]["kz"]) not in set(keys):
            raise ManifestMissing("an instantiated row cites a candidate that was not selected")
    doc["_ledger"] = ledger
    doc["_freeze"] = freeze
    doc["_instantiated"] = inst
    return doc


def require_phase_manifests(phase: str, runs_dir=None, authority=None,
                           require_production=True):
    """Every predecessor phase must have a VALIDATED completion manifest bound to this
    configuration, checked in dependency order so each is validated against the one before it."""
    if phase not in PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r" % (phase,))
    base = pathlib.Path(runs_dir) if runs_dir is not None else (REPO_ROOT / RUNS_REL)
    rows = execution_matrix()["rows"]
    got, records = {}, {}
    required = set(PHASE_PREREQUISITES[phase])
    for pre in PHASE_PREREQUISITES[phase]:
        if pre == "P2b":
            doc = validate_p2b_manifest(base, require_production=require_production,
                                        matrix_rows=rows)
            if doc.get("terminal_status") != "PHASE_COMPLETE":
                raise ManifestMissing("the P2b manifest is %r, not PHASE_COMPLETE"
                                      % (doc.get("terminal_status"),))
            got[pre] = doc
            continue
        doc = validate_phase_manifest(pre, base, authority=authority, matrix_rows=rows,
                                      predecessor_records=dict(records),
                                      require_production=require_production)
        # PE-27: a stopped, failed, unconverged, invalid or design-blocked predecessor may NOT
        # satisfy the next phase. The superseded check never looked at terminal_status at all.
        if doc.get("terminal_status") != "PHASE_COMPLETE":
            raise ManifestMissing(
                "the %s manifest terminated %r; a phase may consume a predecessor only at "
                "PHASE_COMPLETE (erratum PE-27)" % (pre, doc.get("terminal_status")))
        cited = set(doc.get("predecessor_manifests") or {})
        want_keys = set(PHASE_PREREQUISITES[pre])
        if cited != want_keys:
            raise ManifestMissing(
                "the %s manifest cites predecessor manifests %r; the exact required set is %r "
                "(erratum PE-27)" % (pre, sorted(cited), sorted(want_keys)))
        for k, sha in (doc.get("predecessor_manifests") or {}).items():
            path = base / ("manifest_%s.json" % k)
            if not path.exists():
                raise ManifestMissing("the %s manifest cites a missing predecessor %s" % (pre, k))
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != sha:
                raise ManifestMissing("the %s manifest cites predecessor %s hash %r; the file "
                                      "hashes to %r" % (pre, k, sha, actual))
        # PE-64: a predecessor that publishes an aggregate scientific verdict may satisfy the
        # next phase only when that verdict is COMPLETE and PASSING. P1a refuses on anything else.
        if pre in PHASE_AGGREGATE_SCIENCE:
            sci = doc.get("_phase_science") or {}
            if not (sci.get("complete") and sci.get("pass")):
                raise ManifestMissing(
                    "the %s aggregate scientific verdict is not complete and passing "
                    "(complete=%r, pass=%r, failed=%r); phase %r may not consume it "
                    "(erratum PE-64)" % (pre, sci.get("complete"), sci.get("pass"),
                                         sci.get("failed_families"), phase))
        records.update(doc.pop("_records", {}))
        got[pre] = doc
    if set(got) != required:                                 # pragma: no cover - loop is exact
        raise ManifestMissing("phase %r requires exactly %r" % (phase, sorted(required)))
    return got, records


# ---- P2b: the freeze is DERIVED from records, never supplied ---------------------------------

def _terms_from_records(records, kind, key=None):
    return {cid: r for cid, r in records.items()
            if r.get("kind") == kind and (key is None or _bridge_key(r) == key)}


P2B_ARTIFACTS = ("candidate_ledger.json", "proposed_bridge_freeze.json",
                 "instantiated_p3_p4_matrix.json", "manifest_P2b.json")


def _atomic_write_json(path, doc):
    """Canonical, strict-finite, atomic, no-overwrite, exact-match resume (erratum PE-25)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(doc) + "\n"
    if path.exists():
        if path.read_text() != payload:
            raise ValueError("%s already exists and differs from the document just produced; a "
                             "P2b artifact is immutable (erratum PE-25)" % path)
        return path, "REUSED_EXACT_MATCH"
    tmp = path.parent / (path.name + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)
    return path, "WRITTEN"


def _samples(records, kind, key, state, quantity, extractor):
    """NORMAL records only, grouped into a forcing ladder for one fixed configuration."""
    out = []
    for r in sorted(_normal_only(records, kind, key).values(), key=lambda x: x["case_id"]):
        if state is not None and r["row"]["state"] != state:
            continue
        v = extractor(r)
        if v is None:
            continue
        out.append({"forcing_level": r["row"]["forcing_level"],
                    "g": row_forcing(r["row"]), "value": v,
                    "case_id": r["case_id"], "record_sha256": record_hash(r),
                    "S": r["row"]["S"]})
    return out


def _fc(rec):
    """``field_contrast`` of a record, or None where the record cannot supply it."""
    sci = rec.get("scientific")
    if not sci or "p_face1" not in sci:
        return None
    try:
        return field_contrast(sci)
    except (ValueError, KeyError, NonFiniteValue):                # pragma: no cover - degenerate
        return None


def _area_quantity(rec, which):
    fc = _fc(rec)
    if fc is None:
        return None
    if which == "A1":
        return fc["A1"]
    if which == "A2":
        return fc["A2"]
    if which == "A_field":
        return fc["A1"] + fc["A2"]
    if which == "A_series_inverse":
        if fc["A1"] == 0.0 or fc["A2"] == 0.0:                    # pragma: no cover - guarded
            return None
        return 1.0 / fc["A1"] + 1.0 / fc["A2"]
    if which == "c_field":
        return fc["c_field"]
    raise KeyError(which)                                         # pragma: no cover - frozen set


def _phase_samples(records, kind, state, quantity, extractor, key=None):
    """A forcing ladder for one configuration, NORMAL records only, tagged with S."""
    return _samples(records, kind, key, state, quantity, extractor)


def _coupon_samples(records, level, orientation, extractor):
    out = []
    for r in sorted(_normal_only(records, "axial_coupon").values(), key=lambda x: x["case_id"]):
        if r["row"]["coupon_level"] != level or r["row"]["coupon_orientation"] != orientation:
            continue
        v = extractor(r)
        if v is None:
            continue
        out.append({"forcing_level": r["row"]["forcing_level"], "g": row_forcing(r["row"]),
                    "value": v, "case_id": r["case_id"], "record_sha256": record_hash(r),
                    "S": r["row"]["S"]})
    return out


def _coupon_dP(r):
    """A uniform x-periodic duct drops exactly ``g*L``; the coupon record retains L, so this is a
    DERIVED ANALYTIC IDENTITY, labelled as such and never presented as a measurement."""
    sci = r.get("scientific") or {}
    L = sci.get("length_vox")
    if L is None:
        return None
    return row_forcing(r["row"]) * float(L)


def p0_aggregate_science(records):
    """The DURABLE P0 aggregate scientific verdict (erratum PE-64 §6.1).

    C4 wrote P0 records and adjudicated nothing in aggregate, so P1a's only prerequisite was
    ``PHASE_COMPLETE``. This produces the verdict P1a must consume: componentwise forcing
    invariance and two-resolution consistency for the reference-blocked family and for every
    axial coupon, over the complete low/central/high ladder at BOTH resolutions.

    It is stored in the P0 manifest and RECOMPUTED from records by the validator, so a manifest
    can never assert a P0 verdict its own records do not support.
    """
    ref_extract = {
        "Q_reference_blocked": lambda r: (r.get("scientific") or {}).get("Q_volume"),
        "Q_mass_reference_blocked": lambda r: (r.get("scientific") or {}).get(
            "Q_mass_diagnostic"),
        "dP_reference_blocked": lambda r: (r.get("scientific") or {}).get("dP"),
        "C_reference_blocked": lambda r: (_conductance(r)
                                          if (r.get("scientific") or {}).get("dP") else None),
        "s_reference_blocked": lambda r: (r.get("scientific") or {}).get("s_outlet_share_a"),
    }
    #: forcing-independent members of the reference family
    ref_independent = {"C_reference_blocked", "s_reference_blocked"}
    ref_gates = []
    for S in SCIENTIFIC_RESOLUTIONS:
        for q in P0_REFERENCE_FORCING_QUANTITIES:
            sm = [s for s in _phase_samples(records, "reference_blocked_ladder",
                                            "reference_blocked", q, ref_extract[q])
                  if s["S"] == S]
            if sm:
                ref_gates.append(componentwise_forcing_gate(
                    "%s@S%d" % (q, S), sm,
                    forcing_independent=(q in ref_independent)))
    ref_forcing = exact_set_verdict(ref_gates, P0_REFERENCE_FORCING_QUANTITIES,
                                    family="reference_blocked", kind="forcing")

    coupon_extract = {
        "Q_axial_coupon": lambda r: (r.get("scientific") or {}).get("Q_volume"),
        "dP_axial_coupon": _coupon_dP,
        "C_axial_coupon": lambda r: (r.get("scientific") or {}).get("conductance"),
    }
    coupon_forcing, coupon_resolution = {}, {}
    for level in P0_COUPON_LEVELS:
        for orient in P0_COUPON_ORIENTATIONS:
            gates = []
            for S in SCIENTIFIC_RESOLUTIONS:
                for q in P0_COUPON_FORCING_QUANTITIES:
                    sm = [s for s in _coupon_samples(records, level, orient, coupon_extract[q])
                          if s["S"] == S]
                    if sm:
                        g = componentwise_forcing_gate(
                            "%s@S%d" % (q, S), sm,
                            forcing_independent=(q == "C_axial_coupon"))
                        if q == "dP_axial_coupon":
                            g["quantity_role"] = (
                                "DERIVED_ANALYTIC_IDENTITY_dP_EQUALS_g_TIMES_L_"
                                "NOT_AN_INDEPENDENT_MEASUREMENT")
                        gates.append(g)
            coupon_forcing["%s.%s" % (level, orient)] = exact_set_verdict(
                gates, P0_COUPON_FORCING_QUANTITIES,
                family="axial_coupon[%s,%s]" % (level, orient), kind="forcing")

    def _res_gate(quantity, by_S, gates):
        if S_COARSE in by_S and S_FINE in by_S:
            gates.append(resolution_consistency_gate(quantity, by_S[S_COARSE], by_S[S_FINE]))

    ref_res_gates = []
    for q in P0_REFERENCE_RESOLUTION_QUANTITIES:
        by_S = {}
        for s in _phase_samples(records, "reference_blocked_ladder", "reference_blocked", q,
                                ref_extract[q]):
            if s["forcing_level"] == "central":
                by_S[s["S"]] = {"value": s["value"], "case_id": s["case_id"],
                                "record_sha256": s["record_sha256"]}
        _res_gate(q, by_S, ref_res_gates)
    ref_resolution = exact_set_verdict(ref_res_gates, P0_REFERENCE_RESOLUTION_QUANTITIES,
                                       resolutions=(), family="reference_blocked",
                                       kind="resolution")

    for level in P0_COUPON_LEVELS:
        for orient in P0_COUPON_ORIENTATIONS:
            gates = []
            for q in P0_COUPON_RESOLUTION_QUANTITIES:
                by_S = {}
                for s in _coupon_samples(records, level, orient, coupon_extract[q]):
                    if s["forcing_level"] == "central":
                        by_S[s["S"]] = {"value": s["value"], "case_id": s["case_id"],
                                        "record_sha256": s["record_sha256"]}
                _res_gate(q, by_S, gates)
            coupon_resolution["%s.%s" % (level, orient)] = exact_set_verdict(
                gates, P0_COUPON_RESOLUTION_QUANTITIES, resolutions=(),
                family="axial_coupon[%s,%s]" % (level, orient), kind="resolution")

    families = ([ref_forcing, ref_resolution] + list(coupon_forcing.values())
                + list(coupon_resolution.values()))
    out = {
        "phase": "P0",
        "schema_version": 1,
        "reference_blocked_forcing": ref_forcing,
        "reference_blocked_resolution": ref_resolution,
        "axial_coupon_forcing": coupon_forcing,
        "axial_coupon_resolution": coupon_resolution,
        "reference_contrast_quantities": list(P0_REFERENCE_CONTRAST_QUANTITIES),
        "reference_contrast_applicability": P0_REFERENCE_CONTRAST_APPLICABILITY,
        "tau_cross_check": dict(TAU_CROSS_CHECK_DISPOSITION),
        "required_families": (["reference_blocked_forcing", "reference_blocked_resolution"]
                              + ["axial_coupon_forcing[%s]" % k
                                 for k in sorted(coupon_forcing)]
                              + ["axial_coupon_resolution[%s]" % k
                                 for k in sorted(coupon_resolution)]),
        "n_families": len(families),
        "complete": bool(families) and all(f["complete"] for f in families),
        "rule": ("P0 must produce a durable aggregate scientific verdict before P1a can consume "
                 "it: componentwise forcing invariance over the complete low/central/high ladder "
                 "and two-resolution consistency, for the reference-blocked family and for every "
                 "axial coupon level and orientation, with EXACT set equality (erratum PE-64)"),
    }
    expected_families = (2 + len(P0_COUPON_LEVELS) * len(P0_COUPON_ORIENTATIONS) * 2)
    out["expected_families"] = expected_families
    out["pass"] = bool(len(families) == expected_families and out["complete"]
                       and all(f["pass"] for f in families))
    out["failed_families"] = sorted(
        ("%s:%s" % (f["kind"], f["family"])) for f in families if not f["pass"])
    return out


def candidate_forcing_gates(records, key):
    """Adjudicate the exact candidate COMPONENT and BOUNDARY sets for one candidate.

    Component quantities (errata PE-28, PE-48) are Stokes-proportional and are divided by ``g``.
    Boundary quantities (erratum PE-62) are dimensionless or forcing-independent and use the
    frozen DIRECT relative-spread rule. Every group must pass on its own, and the adjudicated set
    must EQUAL the required set at BOTH resolutions across the whole ladder.
    """
    comp_gates, bound_gates = [], []
    press = lateral_pressure_evidence_from_records(records, key)
    for S in SCIENTIFIC_RESOLUTIONS:
        for state, qname in (("blocked", "Q_blocked"), ("open", "Q_open")):
            sm = [s for s in _samples(records, "identical_path_control", key, state, qname,
                                      lambda r: (r.get("scientific") or {}).get("Q_volume"))
                  if s["S"] == S]
            if sm:
                comp_gates.append(componentwise_forcing_gate(qname + "@S%d" % S, sm))
            dp = [s for s in _samples(records, "identical_path_control", key, state, "dP",
                                      lambda r: (r.get("scientific") or {}).get("dP"))
                  if s["S"] == S]
            if dp:
                comp_gates.append(componentwise_forcing_gate(
                    ("dP_blocked" if state == "blocked" else "dP_open") + "@S%d" % S, dp))
        zs = [s for s in _samples(
            records, "identical_path_control", key, "open", "q_lat_mass",
            lambda r: ((r.get("scientific") or {}).get("lateral_pressure") or {}).get(
                "q_lat_mass")) if s["S"] == S]
        if zs:
            # erratum PE-48: q_lat_mass is a MASS flux, so its scale must be an axial MASS flux.
            # Mass and volume are never mixed in one ratio.
            mass_scale = [abs(s["value"] / s["g"]) for s in _samples(
                records, "identical_path_control", key, "open", "Q_mass",
                lambda r: (r.get("scientific") or {}).get("Q_mass_diagnostic"))
                if s["S"] == S]
            if mass_scale:
                g = componentwise_forcing_gate(
                    "q_lat_mass@S%d" % S, zs, expected_zero=True, zero_scale=max(mass_scale),
                    zero_tol=TOL_BRIDGE_LEAKAGE_REL)
                g["zero_scale_source"] = "axial MASS flux sum(rho*u_x)/g; never Q_volume (PE-48)"
                comp_gates.append(g)
        ps = [s for s in _samples(
            records, "identical_path_control", key, "open", "delta_p_lateral",
            lambda r: ((r.get("scientific") or {}).get("lateral_pressure") or {}).get(
                "delta_p_lateral")) if s["S"] == S]
        if ps:
            pscale = [abs(s["value"] / s["g"]) for s in _samples(
                records, "identical_path_control", key, "open", "dP",
                lambda r: (r.get("scientific") or {}).get("dP")) if s["S"] == S]
            if pscale:
                g = componentwise_forcing_gate(
                    "delta_p_lateral@S%d" % S, ps, expected_zero=True, zero_scale=max(pscale),
                    zero_tol=TOL_LATERAL_DRIVER_REL)
                # erratum PE-62 §6.2: three small point means may NEVER substitute for a failed
                # maximum or audit-adjusted bound. The final paired normal/audit upper bounds are
                # a PREREQUISITE of this component gate.
                need = ["%d.%s" % (S, lv) for lv in FORCING_LEVELS]
                bad = [c for c in need
                       if press.get(c) is None or press[c].get("pass") is not True]
                g["pressure_upper_bound_prerequisite"] = {
                    "required_combinations": need, "failed_or_missing": bad,
                    "rule": ("the final paired normal/audit mean AND maximum upper bounds must "
                             "pass at every level before the point-mean component gate may pass "
                             "(erratum PE-60)")}
                if bad:
                    g["pass"] = False
                    g["status"] = "FAIL"
                    g["reason"] = ("the final paired normal/audit pressure upper bound is absent "
                                   "or failing at %r; a small point mean cannot substitute for it"
                                   % (bad,))
                comp_gates.append(g)

    # ---- boundary level: dimensionless / forcing-independent, direct relative spread ----------
    xi_rows = actual_xi_samples(records, key)
    for S in SCIENTIFIC_RESOLUTIONS:
        bound = {
            "R_identical": _identical_R_samples(records, key, S),
            "s_blocked": [s for s in _samples(
                records, "identical_path_control", key, "blocked", "s_blocked",
                lambda r: (r.get("scientific") or {}).get("s_outlet_share_a"))
                if s["S"] == S],
            "s_open": [s for s in _samples(
                records, "identical_path_control", key, "open", "s_open",
                lambda r: (r.get("scientific") or {}).get("s_outlet_share_a"))
                if s["S"] == S],
        }
        for q in ("c_field", "A1", "A2", "A_field", "A_series_inverse"):
            bound[q] = [s for s in _samples(
                records, "candidate_blocked_mirror", key, "blocked", q,
                lambda r, _q=q: _area_quantity(r, _q)) if s["S"] == S]
        bound["Xi_actual"] = [s for s in xi_rows if s["S"] == S]
        for q in CANDIDATE_BOUNDARY_FORCING_QUANTITIES:
            sm = bound.get(q) or []
            if not sm:
                continue
            g = componentwise_forcing_gate("%s@S%d" % (q, S), sm, forcing_independent=True)
            if q in AGGREGATE_AREA_DEFINITIONS:
                g["quantity_definition"] = AGGREGATE_AREA_DEFINITIONS[q]
            if q == "Xi_actual":
                g["quantity_definition"] = ACTUAL_XI_DEFINITION
            bound_gates.append(g)

    component = forcing_invariance_verdict(comp_gates, CANDIDATE_COMPONENT_FORCING_QUANTITIES,
                                           family="candidate_component")
    boundary = forcing_invariance_verdict(bound_gates, CANDIDATE_BOUNDARY_FORCING_QUANTITIES,
                                          family="candidate_boundary")
    out = {
        "component": component, "boundary": boundary,
        "n_gates": component["n_gates"] + boundary["n_gates"],
        "gates": component["gates"] + boundary["gates"],
        "failed_quantities": component["failed_quantities"] + boundary["failed_quantities"],
        "complete": bool(component["complete"] and boundary["complete"]),
        "pass": bool(component["pass"] and boundary["pass"]),
        "rule": ("two family-specific required sets, each asserted EQUAL to the set actually "
                 "adjudicated; one failed component can never be cancelled by another (errata "
                 "PE-62, PE-64)"),
    }
    return out


def _identical_R_samples(records, key, S):
    """``R_identical = C_open / C_blocked`` per forcing level, from EXACTLY paired records."""
    by = {}
    for r in sorted(_normal_only(records, "identical_path_control", key).values(),
                    key=lambda x: x["case_id"]):
        if r["row"]["S"] != S:
            continue
        by.setdefault(r["row"]["forcing_level"], {})[r["row"]["state"]] = r
    out = []
    for level, states in sorted(by.items()):
        if set(states) != {"blocked", "open"}:
            continue
        try:
            Cb, Co = _conductance(states["blocked"]), _conductance(states["open"])
        except (ValueError, KeyError, NonFiniteValue):            # pragma: no cover - degenerate
            continue
        if Cb == 0.0:                                             # pragma: no cover - guarded
            continue
        out.append({"forcing_level": level, "g": row_forcing(states["open"]["row"]),
                    "value": Co / Cb, "S": S,
                    "case_id": states["open"]["case_id"],
                    "record_sha256": record_hash(states["open"]),
                    "paired_blocked_case_id": states["blocked"]["case_id"],
                    "paired_blocked_record_sha256": record_hash(states["blocked"])})
    return out


def actual_xi_samples(records, key):
    """Actual ``Xi = G_bridge_coupon * (1/A1 + 1/A2)`` from EXACTLY matched NORMAL records.

    Matched on candidate, resolution and forcing level. Raw ``G_bridge`` is never returned under
    the name ``Xi`` (errata PE-49, PE-62).
    """
    areas = {}
    for r in _normal_only(records, "candidate_blocked_mirror", key).values():
        inv = _area_quantity(r, "A_series_inverse")
        if inv is None:
            continue
        areas[(r["row"]["S"], r["row"]["forcing_level"])] = (inv, r)
    out = []
    for r in sorted(_normal_only(records, "bridge_coupon", key).values(),
                    key=lambda x: x["case_id"]):
        gb = (r.get("scientific") or {}).get("G_bridge_coupon")
        k2 = (r["row"]["S"], r["row"]["forcing_level"])
        if gb is None or k2 not in areas:
            continue
        inv, arec = areas[k2]
        out.append({
            "forcing_level": k2[1], "g": row_forcing(r["row"]), "S": k2[0],
            "value": float(gb) * inv,
            "G_bridge_coupon": float(gb), "A_series_inverse": inv,
            "case_id": r["case_id"], "record_sha256": record_hash(r),
            "area_case_id": arec["case_id"], "area_record_sha256": record_hash(arec),
            "definition": ACTUAL_XI_DEFINITION,
        })
    return out


# ---- the ACTUAL-Xi numerical discrepancy (erratum PE-67) -------------------------------------
# C4's point estimate used actual Xi = G_bridge * (1/A1 + 1/A2) while ``u_fixed_step_Xi`` moved
# G_bridge alone, so an area movement between a normal record and its audit was invisible to the
# uncertainty of the quantity that actually decides. The pairing below is on the DERIVED quantity.

#: Fields a coupon or blocked-mirror record and its audit must match on before their derived Xi
#: values may be differenced (erratum PE-67).
ACTUAL_XI_MATCH_FIELDS = ("S", "forcing_level", "tau_plus", "coupon_orientation", "variant",
                          "swapped", "perturbation", "obstructed", "backend")


def _xi_pair_fields(rec):
    return {f: rec["row"].get(f) for f in ACTUAL_XI_MATCH_FIELDS}


def _exact_audit_of(records, kind, key, base_case_id):
    for cid, a in _audits_for(records, kind, key).items():
        if a["row"].get("audit_of_case_id") == base_case_id:
            return a
    return None


def actual_xi_discrepancy(records, key):
    """The PRIMARY ``u_fixed_step_Xi``: the frozen safety-factor-adjusted discrepancy between
    ``Xi_normal`` and ``Xi_audit``, each formed from its own four exactly matched records.

    Missing any one of the four records makes that Xi combination INCOMPLETE. Decomposed ``G``
    and area movements are retained as DIAGNOSTICS and are never added again — the derived-Xi
    discrepancy already contains them.
    """
    coupons = _normal_only(records, "bridge_coupon", key)
    mirrors = _normal_only(records, "candidate_blocked_mirror", key)
    by_combo = {}
    for cid, m in mirrors.items():
        by_combo[(m["row"]["S"], m["row"]["forcing_level"])] = m
    combos, terms, incomplete = {}, [], {}
    for cid, crec in sorted(coupons.items()):
        S, level = crec["row"]["S"], crec["row"]["forcing_level"]
        combo = "%d.%s" % (S, level)
        mrec = by_combo.get((S, level))
        entry = {"candidate_id": "w%d_kz%d" % key, "resolution": S, "forcing_level": level,
                 "coupon_normal_case_id": cid, "coupon_normal_record_sha256": record_hash(crec),
                 "match_fields": list(ACTUAL_XI_MATCH_FIELDS),
                 "definition": ACTUAL_XI_DEFINITION,
                 "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
                 "overlaps": ("the derived-Xi discrepancy already contains both the G movement "
                              "and the area movement; the decomposed terms are DIAGNOSTIC and "
                              "are never added to it (erratum PE-67)"),
                 "complete": False, "reason": None}
        if mrec is None:
            entry["reason"] = "no NORMAL candidate-blocked mirror supplies A1/A2 at %s" % combo
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        entry["blocked_mirror_normal_case_id"] = mrec["case_id"]
        entry["blocked_mirror_normal_record_sha256"] = record_hash(mrec)
        caud = _exact_audit_of(records, "bridge_coupon", key, cid)
        maud = _exact_audit_of(records, "candidate_blocked_mirror", key, mrec["case_id"])
        missing = [n for n, v in (("bridge-coupon audit", caud),
                                  ("blocked-mirror audit", maud)) if v is None]
        if missing:
            entry["reason"] = "missing %s" % " and ".join(missing)
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        entry["coupon_audit_case_id"] = caud["case_id"]
        entry["coupon_audit_record_sha256"] = record_hash(caud)
        entry["blocked_mirror_audit_case_id"] = maud["case_id"]
        entry["blocked_mirror_audit_record_sha256"] = record_hash(maud)
        try:
            assert_audit_compatible(caud["row"], crec["row"])
            assert_audit_compatible(maud["row"], mrec["row"])
        except ValueError as exc:
            entry["reason"] = "an audit is not compatible with its base: %s" % exc
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        want = _xi_pair_fields(crec)
        for name, r in (("blocked-mirror normal", mrec), ("bridge-coupon audit", caud),
                        ("blocked-mirror audit", maud)):
            got = _xi_pair_fields(r)
            bad = {f: (want[f], got[f]) for f in ("S", "forcing_level", "tau_plus", "backend")
                   if want[f] != got[f]}
            if bad:
                entry["reason"] = "%s does not match the coupon normal on %r" % (name,
                                                                                 sorted(bad))
                break
        if entry["reason"]:
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        for name, a, b in (("coupon", crec, caud), ("mirror", mrec, maud)):
            if (a["source_commit"], a["backend"]) != (b["source_commit"], b["backend"]):
                entry["reason"] = ("the %s audit was produced under a different run authority"
                                   % name)
        if entry["reason"]:                                # pragma: no cover - guarded upstream
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        g_n = (crec.get("scientific") or {}).get("G_bridge_coupon")
        g_a = (caud.get("scientific") or {}).get("G_bridge_coupon")
        fc_n, fc_a = _fc(mrec), _fc(maud)
        if g_n is None or g_a is None or fc_n is None or fc_a is None:
            entry["reason"] = "a record does not carry G_bridge_coupon or A1/A2"
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        inv_n = 1.0 / fc_n["A1"] + 1.0 / fc_n["A2"]
        inv_a = 1.0 / fc_a["A1"] + 1.0 / fc_a["A2"]
        xi_n = _finite(float(g_n) * inv_n, "Xi_normal")
        xi_a = _finite(float(g_a) * inv_a, "Xi_audit")
        entry.update(
            G_bridge_normal=float(g_n), G_bridge_audit=float(g_a),
            A1_normal=fc_n["A1"], A2_normal=fc_n["A2"],
            A1_audit=fc_a["A1"], A2_audit=fc_a["A2"],
            A_series_inverse_normal=inv_n, A_series_inverse_audit=inv_a,
            Xi_normal=xi_n, Xi_audit=xi_a, complete=True)
        if xi_n == 0.0:                                    # pragma: no cover - degenerate
            entry["complete"] = False
            entry["reason"] = "Xi_normal is exactly zero; no relative discrepancy exists"
            combos[combo] = entry
            incomplete[combo] = entry["reason"]
            continue
        rel = abs(xi_a / xi_n - 1.0)
        entry["relative_movement"] = rel
        entry["u_fixed_step_Xi"] = NUMERICAL_DISCREPANCY_SAFETY_FACTOR * rel
        entry["diagnostic_decomposition"] = {
            "G_relative_movement": abs(float(g_a) / float(g_n) - 1.0) if g_n else None,
            "A_series_inverse_relative_movement": (abs(inv_a / inv_n - 1.0) if inv_n else None),
            "role": "DIAGNOSTIC_ONLY_ALREADY_CONTAINED_IN_THE_DERIVED_XI_DISCREPANCY",
        }
        terms.append(rel)
        combos[combo] = entry
    want_combos = sorted({"%d.%s" % (S, lv) for S in SCIENTIFIC_RESOLUTIONS
                          for lv in FORCING_LEVELS})
    worst = max(terms) if terms else None
    return {
        "candidate_id": "w%d_kz%d" % key,
        "quantity": "Xi_actual",
        "definition": ACTUAL_XI_DEFINITION,
        "method": ("worst relative movement of the DERIVED quantity Xi between each NORMAL "
                   "combination and its own fixed-step audits, times the frozen safety factor "
                   "(erratum PE-67)"),
        "combinations": combos,
        "required_combinations": want_combos,
        "missing_combinations": sorted(set(want_combos) - set(combos)),
        "incomplete_combinations": incomplete,
        "n_pairs": len(terms),
        "worst_relative_movement": worst,
        "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
        "value": (None if worst is None else NUMERICAL_DISCREPANCY_SAFETY_FACTOR * worst),
        "complete": bool(not (set(want_combos) - set(combos)) and not incomplete and terms),
        "overlaps": ("this family's own normal/audit pairs only; the decomposed G and area "
                     "movements are diagnostics and are never added again"),
        "fixed_step_records_are_never_independent_estimates": True,
    }


def candidate_resolution_gates(records, key, bridge):
    """Adjudicate S=2 vs S=3 for the EXACT candidate resolution set (errata PE-29, PE-66).

    Each quantity uses its own governing feature family and the frozen comparison coordinate.
    Candidate-blocked quantities use the common-mode-port family, which includes the lane
    heights, the bridge footprint width and height, the port depth and the divider traverse.
    """
    gates = []

    def add(quantity, by_S, extra=None):
        if S_COARSE in by_S and S_FINE in by_S:
            g = resolution_consistency_gate(quantity, by_S[S_COARSE], by_S[S_FINE], bridge)
            if extra:
                g.update(extra)
            gates.append(g)

    def pick(kind, state, extractor, level="central"):
        got = {}
        for r in sorted(_normal_only(records, kind, key).values(), key=lambda x: x["case_id"]):
            if state is not None and r["row"]["state"] != state:
                continue
            if r["row"]["forcing_level"] != level:
                continue
            v = extractor(r)
            if v is not None:
                got[r["row"]["S"]] = {"value": v, "case_id": r["case_id"],
                                      "record_sha256": record_hash(r)}
        return got

    for q in ("c_field", "A1", "A2", "A_field", "A_series_inverse"):
        extra = ({"quantity_definition": AGGREGATE_AREA_DEFINITIONS[q]}
                 if q in AGGREGATE_AREA_DEFINITIONS else None)
        add(q, pick("candidate_blocked_mirror", "blocked",
                    lambda r, _q=q: _area_quantity(r, _q)), extra)
    add("C_blocked", pick("candidate_blocked_mirror", "blocked",
                          lambda r: (_conductance(r)
                                     if (r.get("scientific") or {}).get("dP") else None)))
    add("s_blocked", pick("identical_path_control", "blocked",
                          lambda r: (r.get("scientific") or {}).get("s_outlet_share_a")))
    add("s_open", pick("identical_path_control", "open",
                       lambda r: (r.get("scientific") or {}).get("s_outlet_share_a")))
    add("C_open", pick("identical_path_control", "open",
                       lambda r: (_conductance(r)
                                  if (r.get("scientific") or {}).get("dP") else None)))
    add("G_bridge_coupon", pick("bridge_coupon", None,
                                lambda r: (r.get("scientific") or {}).get("G_bridge_coupon")))
    r_by_S = {}
    for S in SCIENTIFIC_RESOLUTIONS:
        for s in _identical_R_samples(records, key, S):
            if s["forcing_level"] == "central":
                r_by_S[S] = {"value": s["value"], "case_id": s["case_id"],
                             "record_sha256": s["record_sha256"]}
    add("R_identical", r_by_S,
        {"artifact_point_estimate_coverage": ARTIFACT_POINT_ESTIMATE_COVERAGE})
    xi_by_S = {}
    for s in actual_xi_samples(records, key):
        if s["forcing_level"] == "central":
            xi_by_S[s["S"]] = {"value": s["value"], "case_id": s["case_id"],
                               "record_sha256": s["record_sha256"],
                               "area_case_id": s["area_case_id"],
                               "area_record_sha256": s["area_record_sha256"]}
    if S_COARSE in xi_by_S and S_FINE in xi_by_S:
        g = resolution_consistency_gate("Xi_actual", xi_by_S[S_COARSE], xi_by_S[S_FINE], bridge)
        g["quantity_definition"] = ACTUAL_XI_DEFINITION
        g["area_case_ids"] = [xi_by_S[S_COARSE]["area_case_id"], xi_by_S[S_FINE]["area_case_id"]]
        g["area_record_sha256"] = assert_flat_hash_list(
            [xi_by_S[S_COARSE]["area_record_sha256"], xi_by_S[S_FINE]["area_record_sha256"]],
            "Xi area record hashes")
        gates.append(g)
    return resolution_consistency_verdict(gates, CANDIDATE_RESOLUTION_QUANTITIES,
                                          family="candidate")


# ---- complete candidate and COMMON-REFERENCE evidence binding (erratum PE-68) ----------------
# C4 bound a selected bridge's normals and its artifact-combination audits, and omitted the c, Xi
# and pressure audits whose discrepancies the same ledger reported. Everything used to decide a
# candidate is bound here, and genuinely shared P0 evidence is separated rather than duplicated
# into every candidate's hash set — duplicating it would weaken the distinct-candidate rule that
# exists to stop one hash binding two geometries.

#: Kinds whose records belong to ONE candidate.
CANDIDATE_SPECIFIC_KINDS = ("identical_path_control", "bridge_coupon",
                            "candidate_blocked_mirror")
#: Kinds whose records are COMMON reference truth shared by every candidate.
COMMON_REFERENCE_KINDS = ("reference_blocked_ladder", "axial_coupon", "tau_cross_check")


def common_reference_evidence(records):
    """Validated P0 reference and axial-coupon evidence shared by EVERY candidate.

    Kept in one top-level structure, named by role. It is never duplicated into a candidate's own
    hash set, so ``candidate_specific_record_sha256`` stays a genuinely distinguishing set.
    """
    roles, ids, hashes = {}, [], []
    for cid, r in sorted(records.items()):
        kind = r.get("kind")
        if kind not in COMMON_REFERENCE_KINDS:
            continue
        role = kind
        if kind == "axial_coupon":
            role = "axial_coupon[%s,%s]" % (r["row"]["coupon_level"],
                                            r["row"]["coupon_orientation"])
        h = record_hash(r)
        roles.setdefault(role, {"case_ids": [], "record_sha256": []})
        roles[role]["case_ids"].append(cid)
        roles[role]["record_sha256"].append(h)
        ids.append(cid)
        hashes.append(h)
    for role in roles.values():
        role["case_ids"] = assert_flat_id_list(sorted(role["case_ids"]),
                                               "common reference case ids")
        role["record_sha256"] = assert_flat_hash_list(sorted(set(role["record_sha256"])),
                                                      "common reference hashes")
    return {
        "roles": roles,
        "role_names": sorted(roles),
        "case_ids": assert_flat_id_list(sorted(ids), "common reference case ids"),
        "record_sha256": assert_flat_hash_list(sorted(set(hashes)), "common reference hashes"),
        "rule": ("common reference evidence is shared by construction and is bound ONCE at top "
                 "level; it is never copied into a candidate-specific hash set (erratum PE-68)"),
    }


def candidate_evidence_binding(records, key, artifact, pressure, u_c, u_xi, forcing, resolution):
    """Every record used to decide ONE candidate, with a complete source-to-derived mapping."""
    ids, hashes, by_role = [], [], {}

    def add(role, cid, h):
        by_role.setdefault(role, {"case_ids": [], "record_sha256": []})
        by_role[role]["case_ids"].append(cid)
        by_role[role]["record_sha256"].append(h)
        ids.append(cid)
        hashes.append(h)

    for cid, r in sorted(records.items()):
        if r.get("kind") not in CANDIDATE_SPECIFIC_KINDS or _bridge_key(r) != key:
            continue
        normal = r["run_mode"] == "NORMAL"
        role = "%s_%s" % (r["kind"], "normal" if normal else "fixed_step_audit")
        add(role, cid, record_hash(r))
    # node-offset summaries are bound through their OWNING record hashes, which are already in
    # the identical-path sets above; the mapping records that explicitly.
    for role in by_role.values():
        role["case_ids"] = assert_flat_id_list(sorted(role["case_ids"]), "candidate case ids")
        role["record_sha256"] = assert_flat_hash_list(sorted(set(role["record_sha256"])),
                                                      "candidate hashes")
    cs_ids = assert_flat_id_list(sorted(set(ids)), "candidate_specific_case_ids")
    cs_h = assert_flat_hash_list(sorted(set(hashes)), "candidate_specific_record_sha256")

    def _cited(*groups):
        out = []
        for grp in groups:
            out.extend([h for h in grp if h])
        return sorted(set(out))

    art_h = _cited(*[list(v["normal_record_sha256"]) + list(v["audit_record_sha256"])
                     + list(v["pressure_plane_record_sha256"])
                     for v in artifact["combinations"].values()])
    press_h = _cited([e.get("normal_record_sha256") for e in pressure.values()],
                     [e.get("audit_record_sha256") for e in pressure.values()])
    xi_h = _cited([c.get("coupon_normal_record_sha256") for c in u_xi["combinations"].values()],
                  [c.get("coupon_audit_record_sha256") for c in u_xi["combinations"].values()],
                  [c.get("blocked_mirror_normal_record_sha256")
                   for c in u_xi["combinations"].values()],
                  [c.get("blocked_mirror_audit_record_sha256")
                   for c in u_xi["combinations"].values()])
    c_h = _cited(list(u_c["normal_record_sha256"]), list(u_c["audit_record_sha256"]))
    forcing_h = _cited([h for g in forcing["gates"] for h in g["record_sha256"]])
    res_h = _cited([h for g in resolution["gates"] for h in g["record_sha256"]]
                   + [h for g in resolution["gates"] for h in (g.get("area_record_sha256") or [])])
    mapping = {
        "artifact_R": {"record_sha256": art_h,
                       "derived": ["R_point", "u_fixed_step_R", "u_pressure_plane_R",
                                   "artifact_upper"]},
        "pressure_gap": {"record_sha256": press_h,
                         "derived": ["mean_gap_upper_rel", "max_gap_upper_rel"]},
        "candidate_c": {"record_sha256": c_h,
                        "derived": ["c_lower", "c_upper", "u_fixed_step_c"]},
        "actual_Xi": {"record_sha256": xi_h,
                      "derived": ["Xi_normal", "Xi_audit", "u_fixed_step_Xi", "Xi_select",
                                  "Xi_lower", "Xi_upper", "category"]},
        "forcing_gates": {"record_sha256": forcing_h, "derived": ["forcing_invariance"]},
        "resolution_gates": {"record_sha256": res_h, "derived": ["resolution_consistency"]},
        "node_offset_summaries": {
            "record_sha256": [], "derived": ["u_pressure_plane_R"],
            "note": ("same-field summaries are bound through their OWNING record hashes, which "
                     "are the identical-path normals already listed under artifact_R")},
    }
    unbound = sorted(set(art_h + press_h + xi_h + c_h + forcing_h + res_h) - set(cs_h))
    common = {h for h in unbound}
    return {
        "candidate_id": "w%d_kz%d" % key,
        "by_role": by_role,
        "candidate_specific_case_ids": cs_ids,
        "candidate_specific_record_sha256": cs_h,
        "common_reference_roles": sorted(
            {"reference_blocked_ladder", "axial_coupon"}) if common else [],
        "source_to_derived_quantity": mapping,
        "unbound_cited_hashes": unbound,
        "complete": bool(not unbound),
        "rule": ("every record used to decide this candidate is bound, audits included; common "
                 "reference evidence lives once at top level and is never duplicated here "
                 "(erratum PE-68)"),
    }


# ---- the P2b ASSEMBLY AUTHORITY (erratum PE-73) ----------------------------------------------
# C4's validator took an ``authority`` parameter and never read it. Every P2b artifact now binds
# one complete assembly-authority document, and the validator reconstructs and validates it.
#
# The configuration-bound fields are checked against the CURRENT configuration; the historical
# identity fields (source commit, source tree, clean-tree proof) are validated for shape and
# self-consistency but are NOT required to equal the validating head. That is deliberate: a later
# P3 review wrapper must be able to bind the historical P2b authority without pretending its own
# review commit was the P2b execution commit.

P2B_ASSEMBLY_AUTHORITY_FIELDS = (
    "phase", "correction_version", "source_commit", "source_tree", "working_tree_clean",
    "clean_tree_required", "protocol_config_sha256", "fixture_spec_sha256",
    "execution_matrix_sha256", "pre_freeze_matrix_sha256", "predecessor_manifest_file_sha256",
    "backend", "dependencies", "provenance_mode",
)


def pre_freeze_matrix_sha256():
    """The hash of the PRE-FREEZE rows alone — the rows P0…P2a actually execute."""
    rows = [r for r in execution_matrix()["rows"] if r["phase"] in ("P0", "P1a", "P1b", "P2a")]
    return record_hash(rows)


def p2b_assembly_authority(runs_dir, execution_auth, manifest_keys,
                           provenance_mode="PRODUCTION"):
    """The complete assembly-authority document every P2b artifact binds (erratum PE-73)."""
    base = pathlib.Path(runs_dir)
    doc = {
        "phase": "P2b",
        "correction_version": CORRECTION_VERSION,
        "source_commit": execution_auth["source_commit"],
        "source_tree": execution_auth["source_tree"],
        "working_tree_clean": execution_auth["working_tree_clean"],
        "clean_tree_required": execution_auth["clean_tree_required"],
        "protocol_config_sha256": execution_auth["protocol_config_sha256"],
        "fixture_spec_sha256": execution_auth["fixture_spec_sha256"],
        "execution_matrix_sha256": execution_auth["execution_matrix_sha256"],
        "pre_freeze_matrix_sha256": pre_freeze_matrix_sha256(),
        "predecessor_manifest_file_sha256": {
            k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
            for k in sorted(manifest_keys)},
        "backend": execution_auth["backend"],
        "dependencies": dict(execution_auth["dependencies"]),
        "provenance_mode": provenance_mode,
        "execution_authority_sha256": record_hash(execution_auth),
        "note": ("binds the exact configuration and predecessor files this assembly consumed; a "
                 "later review wrapper may cite it without claiming its own commit produced it"),
    }
    doc["assembly_authority_sha256"] = record_hash(
        {k: doc[k] for k in P2B_ASSEMBLY_AUTHORITY_FIELDS})
    return doc


def validate_p2b_assembly_authority(doc, runs_dir, require_production=True,
                                    expected_assembly_authority_sha256=None):
    """Reconstruct and validate an embedded P2b assembly authority (erratum PE-73)."""
    base = pathlib.Path(runs_dir)
    if not isinstance(doc, dict):
        raise ManifestMissing("the P2b manifest carries no assembly authority")
    missing = [k for k in P2B_ASSEMBLY_AUTHORITY_FIELDS if k not in doc]
    if missing:
        raise ManifestMissing("the P2b assembly authority is missing %r" % (missing,))
    if doc["phase"] != "P2b":
        raise ManifestMissing("the assembly authority declares phase %r" % (doc["phase"],))
    if doc["correction_version"] != CORRECTION_VERSION:
        raise ManifestMissing("the assembly authority is from a superseded correction version")
    if require_production and doc["provenance_mode"] != "PRODUCTION":
        raise ManifestMissing("a TEST_ONLY assembly authority may never satisfy a production "
                              "gate (erratum PE-71)")
    if doc["backend"] not in SUPPORTED_BACKENDS:
        raise ManifestMissing("the assembly authority names an unsupported backend")
    if require_production and not doc["working_tree_clean"]:
        raise ManifestMissing("the assembly authority records a dirty working tree")
    for k in ("source_commit", "source_tree"):
        v = doc[k]
        if not isinstance(v, str) or len(v) != 40:
            raise ManifestMissing("the assembly authority's %s is not a git object name" % k)
    want = config_hashes()
    for k, v in want.items():
        if doc.get(k) != v:
            raise ManifestMissing("the assembly authority binds a different %s" % k)
    if doc["pre_freeze_matrix_sha256"] != pre_freeze_matrix_sha256():
        raise ManifestMissing("the assembly authority binds a different pre-freeze matrix")
    cited = dict(doc["predecessor_manifest_file_sha256"])
    if set(cited) != set(PHASE_PREREQUISITES["P2b"]):
        raise ManifestMissing("the assembly authority cites predecessors %r; the exact required "
                              "set is %r" % (sorted(cited), sorted(PHASE_PREREQUISITES["P2b"])))
    for k, sha in sorted(cited.items()):
        f = base / ("manifest_%s.json" % k)
        if not f.exists():
            raise ManifestMissing("the assembly authority cites a missing predecessor %s" % k)
        if hashlib.sha256(f.read_bytes()).hexdigest() != sha:
            raise ManifestMissing("the assembly authority cites a stale hash for predecessor %s"
                                  % k)
    recomputed = record_hash({k: doc[k] for k in P2B_ASSEMBLY_AUTHORITY_FIELDS})
    if doc.get("assembly_authority_sha256") != recomputed:
        raise ManifestMissing("the assembly authority's own SHA-256 does not recompute")
    if (expected_assembly_authority_sha256 is not None
            and expected_assembly_authority_sha256 != recomputed):
        raise ManifestMissing("the P2b assembly authority is not the expected one: %r vs %r"
                              % (expected_assembly_authority_sha256, recomputed))
    return doc


def assemble_p2b_from_runs(runs_dir, backend="reference"):
    """The PRODUCTION P2b wrapper. Derives the PROPOSED bridge freeze from validated production
    records alone, and PERSISTS it.

    It obtains the real source-controlled assembly authority ITSELF, recursively validates P0,
    P1a, P1b and P2a as PRODUCTION, reopens and validates every cited production record, passes
    those validated records to the pure decision core, and writes PRODUCTION artifacts only.

    It exposes **no** provenance override, **no** authority override, **no** manifest-validation
    override and **no** caller-supplied candidate value (errata PE-18, PE-71). It accepts no
    selection, candidate dictionary, ``c`` or ``Xi`` value, uncertainty, eligibility flag, record
    hash or externally instantiated P3/P4 matrix, and it performs **no solve**.

    The synthetic harness has its own private wrapper (:func:`_test_only_assemble_p2b_from_runs`)
    and never reaches this function by monkeypatching its guards.
    """
    base = pathlib.Path(runs_dir)
    auth = execution_authority("P2b", backend=backend)
    manifests, records = require_phase_manifests("P2b", runs_dir=base, authority=auth,
                                                 require_production=True)
    for rec in records.values():
        assert_production_record(rec)
    return _p2b_decision_core(base, auth, manifests, records, provenance_mode="PRODUCTION")


def _test_only_assemble_p2b_from_runs(runs_dir, authority, backend="reference"):
    """PRIVATE TEST_ONLY P2b wrapper (erratum PE-71).

    It consumes validated TEST_ONLY predecessor manifests and records, and every artifact it
    writes carries ``provenance_mode = "TEST_ONLY"`` — the candidate ledger, the proposed freeze,
    the instantiated matrix, the P2b manifest and the assembly-authority record alike. Production
    validation rejects every one of them.

    It never calls the production wrapper and never monkeypatches a production guard.
    """
    base = pathlib.Path(runs_dir)
    manifests, records = require_phase_manifests("P2b", runs_dir=base, authority=authority,
                                                 require_production=False)
    return _p2b_decision_core(base, authority, manifests, records, provenance_mode="TEST_ONLY")


def _p2b_decision_core(base, auth, manifests, records, provenance_mode="PRODUCTION"):
    """The PURE P2b decision core, shared by the two wrappers with non-overlapping provenance.

    Recomputes, in order: lineage · forcing ladders · componentwise invariance · boundary
    stability · resolution consistency · zero-driver transverse · measured lateral pressure gap ·
    normal/audit pairing · artifact point estimates and uncertainty · complete candidate
    admission · candidate ``c`` intervals · actual-``Xi`` envelopes · reachable-set admission ·
    categories · the exact four-slot selection · the instantiated P3/P4 rows · the durable
    ledger, proposed freeze and P2b manifest. It performs **no solve**.
    """
    base = pathlib.Path(base)
    assembly_auth = p2b_assembly_authority(base, auth, manifests,
                                           provenance_mode=provenance_mode)

    # erratum PE-60: P2b INDEPENDENTLY recomputes every pressure upper bound from the validated
    # records and retains it. No stored eligibility boolean is trusted anywhere below.
    admission = candidate_admission_from_records(records)
    ledger, admitted = {}, []
    for key, adm_entry in sorted(admission.items()):
        art = adm_entry["artifact"]
        w, kz = key
        bridge = {"w": w, "kz": kz}
        cid = "w%d_kz%d" % key
        entry = {"candidate_id": cid, "w": w, "kz": kz, "artifact": art,
                 "pressure_upper_bounds": adm_entry["pressure"],
                 "zero_driver_lateral_mass_flux": adm_entry["lateral_mass_flux"],
                 "p1b_candidate_admission": {k: v for k, v in adm_entry.items()
                                             if k not in ("artifact", "pressure",
                                                          "lateral_mass_flux")},
                 "eligible": False, "rejection_reason": None}

        # --- gates first: a failure makes the candidate UNAVAILABLE (errata PE-28, PE-29) ---
        forcing = candidate_forcing_gates(records, key)
        entry["forcing_invariance"] = forcing
        resolution = candidate_resolution_gates(records, key, bridge)
        entry["resolution_consistency"] = resolution
        if not forcing["pass"]:
            entry["rejection_reason"] = "FORCING_INVARIANCE: %r" % (forcing["failed_quantities"],)
            ledger[cid] = entry
            continue
        if not resolution["pass"]:
            entry["rejection_reason"] = ("RESOLUTION_CONSISTENCY: %r"
                                         % (resolution["failed_quantities"],))
            ledger[cid] = entry
            continue
        if not adm_entry["admitted"]:
            entry["rejection_reason"] = "P1B_CANDIDATE_ADMISSION: %s" % adm_entry["reason"]
            ledger[cid] = entry
            continue

        # --- candidate c, from its OWN blocked-mirror normals and its OWN audits (PE-31) ---
        blocked = _normal_only(records, "candidate_blocked_mirror", key)
        b_pairs = _pair_normal_with_audit(
            blocked, _audits_for(records, "candidate_blocked_mirror", key))
        contrasts, areas = [], {}
        for r in sorted(blocked.values(), key=lambda x: x["case_id"]):
            fc = field_contrast(r["scientific"])          # RECOMPUTED, never taken on trust
            contrasts.append(abs(fc["c_field"]))
            areas[(r["row"]["S"], r["row"]["forcing_level"])] = (fc["A1"], fc["A2"])
        if not contrasts:
            entry["rejection_reason"] = "NO_BLOCKED_MIRROR_CONTRAST_EVIDENCE"
            ledger[cid] = entry
            continue
        u_c = fixed_step_discrepancy(
            b_pairs, lambda r: (field_contrast(r["scientific"])["c_field"]
                                if r.get("scientific") else None), "c_field")
        if u_c["value"] is None:
            entry["rejection_reason"] = "NO_FIXED_STEP_EVIDENCE_FOR_c_field"
            ledger[cid] = entry
            continue
        cb = candidate_c_bounds(
            contrasts,
            resolution_tolerance=resolution_consistency_tolerance("c_field", bridge),
            numerical_rel=u_c["value"])
        entry["c_bounds"] = cb
        entry["u_fixed_step_c"] = u_c

        # --- candidate Xi: ACTUAL Xi throughout, point estimate and uncertainty alike (PE-67) ---
        coupons = _normal_only(records, "bridge_coupon", key)
        u_xi = actual_xi_discrepancy(records, key)
        if not u_xi["complete"] or u_xi["value"] is None:
            entry["u_fixed_step_Xi"] = u_xi
            entry["rejection_reason"] = ("INCOMPLETE_ACTUAL_XI_DISCREPANCY: %r"
                                         % (u_xi["incomplete_combinations"]
                                            or u_xi["missing_combinations"],))
            ledger[cid] = entry
            continue
        xi_rows, xi_ids, xi_h = [], [], []
        for s in actual_xi_samples(records, key):
            xi_rows.append({"S": s["S"], "forcing_level": s["forcing_level"],
                            "coupon_source": "bridge_coupon", "Xi": s["value"]})
            xi_ids.append(s["case_id"])
            xi_h.append(s["record_sha256"])
        if not xi_rows:                                # pragma: no cover - guarded by u_xi above
            entry["rejection_reason"] = "NO_BRIDGE_COUPON_XI_EVIDENCE"
            ledger[cid] = entry
            continue
        env = xi_envelope(xi_rows,
                          resolution_consistency_tolerance("Xi_actual", bridge) + u_xi["value"])
        entry["xi_envelope"] = env
        entry["u_fixed_step_Xi"] = u_xi
        entry["xi_case_ids"] = assert_flat_id_list(sorted(set(xi_ids)), "Xi case ids")
        entry["xi_record_sha256"] = assert_flat_hash_list(sorted(set(xi_h)), "Xi record hashes")

        art_upper = max(v["artifact_upper"] for v in art["combinations"].values())
        adm = reachable_set_admission(cb["c_lower"], cb["c_upper"], env["Xi_upper"], art_upper)
        entry["reachable_set"] = adm
        entry["category"] = env["category"]
        entry["eligible"] = bool(adm["admitted"])
        entry["uncertainty_lineage"] = {
            "artifact_R": {"value": art_upper, "family": "identical-path pairs",
                           "overlaps": "contains u_fixed_step_R, u_pressure_plane_R and "
                                       "u_serialization_R; never added again",
                           "used_in": "artifact admission and the reachable-set inequality"},
            "candidate_c": {"interval": [cb["c_lower"], cb["c_upper"]],
                            "family": "blocked-mirror pairs", "u_fixed_step": u_c,
                            "overlaps": "folded into the interval; never added separately",
                            "used_in": "the reachable ceiling and the signal upper bound"},
            "coupon_Xi": {"envelope": [env["Xi_lower"], env["Xi_upper"]],
                          "family": "bridge-coupon pairs", "u_fixed_step": u_xi,
                          "overlaps": "carried inside Xi_upper",
                          "used_in": "the predicted-signal upper bound and the category"},
        }
        if not entry["eligible"]:
            entry["rejection_reason"] = "REACHABLE_SET: headroom %.6g" % adm["headroom"]
        else:
            # erratum PE-68: bind EVERY record used to decide this candidate, not only the
            # normals whose audit-derived uncertainties the ledger reports.
            ev = candidate_evidence_binding(records, key, art, adm_entry["pressure"],
                                            u_c, u_xi, forcing, resolution)
            entry["evidence"] = ev
            admitted.append({"w": w, "kz": kz, "eligible": True, "xi_envelope": env,
                             "candidate_specific_case_ids": ev["candidate_specific_case_ids"],
                             "candidate_specific_record_sha256":
                                 ev["candidate_specific_record_sha256"],
                             "common_reference_roles": ev["common_reference_roles"],
                             "source_to_derived_quantity": ev["source_to_derived_quantity"],
                             "record_hashes": ev["candidate_specific_record_sha256"]})
        ledger[cid] = entry

    ledger_doc = {
        "tranche": TRANCHE_ID, "correction_version": CORRECTION_VERSION,
        "phase": "P2b", "candidates": ledger,
        "common_reference_evidence": common_reference_evidence(records),
        "n_declared": len(ledger), "n_eligible": len(admitted),
        "provenance_mode": provenance_mode,
        "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
        "execution_authority_sha256": record_hash(auth),
        "assembly_authority": dict(assembly_auth),
        "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
    }
    ledger_doc.update(config_hashes())
    written = {}
    written["candidate_ledger.json"] = _atomic_write_json(base / "candidate_ledger.json",
                                                          ledger_doc)[0].name

    stop_reason, freeze_doc, inst = None, None, None
    try:
        selection = select_bridges(admitted)
    except DesignBlocked as exc:
        selection, stop_reason = None, exc.reason

    if selection is not None:
        seen = {}
        for c in selection:
            for h in c["record_hashes"]:
                prev = seen.get(h)
                if prev is not None and prev != (c["w"], c["kz"]):
                    raise ManifestMissing(
                        "record hash %r binds two candidate geometries %r and %r without a "
                        "declared common-reference role" % (h, prev, (c["w"], c["kz"])))
                seen[h] = (c["w"], c["kz"])
        inst = instantiate_post_freeze_matrix([{"w": c["w"], "kz": c["kz"]} for c in selection])
        inst_doc = {"schema_version": 1, "tranche": TRANCHE_ID,
                    "correction_version": CORRECTION_VERSION,
                    "provenance_mode": provenance_mode,
                    "assembly_authority_sha256":
                        assembly_auth["assembly_authority_sha256"],
                    "rows": inst, "n_rows": len(inst),
                    "rows_sha256": record_hash(inst)}          # PE-51: ONE canonical key
        inst_doc.update(config_hashes())
        inst_path = _atomic_write_json(base / "instantiated_p3_p4_matrix.json", inst_doc)[0]
        inst_file_sha = hashlib.sha256(inst_path.read_bytes()).hexdigest()
        written["instantiated_p3_p4_matrix.json"] = inst_path.name
        freeze_doc = {
            "tranche": TRANCHE_ID, "correction_version": CORRECTION_VERSION,
            "freeze_rule": FREEZE_RULE, "n_frozen_bridges": N_FROZEN_BRIDGES,
            "frozen_bridges": [{"w": c["w"], "kz": c["kz"], "slot": c["slot"],
                                "slot_provenance": c["slot_provenance"],
                                "category": c["category"],
                                "freeze_order": c["freeze_order"],
                                "xi_envelope": c["xi_envelope"],
                                "candidate_specific_case_ids":
                                    c["candidate_specific_case_ids"],
                                "candidate_specific_record_sha256":
                                    c["candidate_specific_record_sha256"],
                                "common_reference_roles": c["common_reference_roles"],
                                "source_to_derived_quantity":
                                    c["source_to_derived_quantity"],
                                "record_hashes": c["record_hashes"]} for c in selection],
            "common_reference_evidence": ledger_doc["common_reference_evidence"],
            "above_window_diagnostics": above_window_diagnostics(admitted),
            "candidate_ledger_sha256": record_hash(ledger_doc),
            "phase_manifest_sha256": {
                k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
                for k in manifests},
            "rows_sha256": record_hash(inst),
            "instantiated_matrix_file_sha256": inst_file_sha,
            "provenance_mode": provenance_mode,
            "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
            "execution_authority_sha256": record_hash(auth),
            "assembly_authority": dict(assembly_auth),
            "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
            "status": "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW",
            "p3_p4_authorised": False,
            "note": ("P3 and P4 remain unauthorized even with this artifact present: a freeze is "
                     "necessary, never sufficient, and it requires its own reviewed "
                     "authorization commit."),
        }
        freeze_doc.update(config_hashes())
        written["proposed_bridge_freeze.json"] = _atomic_write_json(
            base / "proposed_bridge_freeze.json", freeze_doc)[0].name

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": "P2b", "provenance_mode": provenance_mode,
        "phase_kind": "ARITHMETIC_ASSEMBLY_NO_SOLVER_CALL",
        "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
        "execution_authority_sha256": record_hash(auth),
        "assembly_authority": dict(assembly_auth),
        "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
        "full_matrix_sha256": record_hash(execution_matrix()),
        "predecessor_manifests": {
            k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
            for k in manifests},
        "candidate_ledger_sha256": record_hash(ledger_doc),
        "proposed_freeze_sha256": (None if freeze_doc is None else record_hash(freeze_doc)),
        "rows_sha256": (None if inst is None else record_hash(inst)),
        "instantiated_matrix_file_sha256": (None if inst is None else inst_file_sha),
        "artifacts_written": dict(written),
        "n_declared_candidates": len(ledger),
        "n_eligible_candidates": len(admitted),
        "selection_status": ("SELECTED" if selection is not None else "DESIGN_BLOCKED"),
        "terminal_status": ("PHASE_COMPLETE" if selection is not None
                            else "PHASE_STOPPED_DESIGN_BLOCKED"),
        "terminal_stop_reason": stop_reason,
        "solver_records": [],
    }
    manifest.update(config_hashes())
    # PE-52: no in-memory mutation after persistence -- the persisted and returned documents are
    # byte-identical. The manifest names its own deterministic path but never claims its own SHA.
    manifest["manifest_path"] = "manifest_P2b.json"
    _atomic_write_json(base / "manifest_P2b.json", manifest)
    return manifest


_GENERATED = (
    ("protocol.json", protocol_config),
    ("fixture_spec.json", fixture_spec_config),
    ("execution_matrix.json", execution_matrix),
    ("preflight_status.json", preflight_status),
)


GENERATED_DIR = REPO_ROOT / BUNDLE_REL / "generated"


def _gen_path(name):
    return GENERATED_DIR / name


def write():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fn in _GENERATED:
        p = _gen_path(name)
        p.write_text(canonical_json(fn()) + "\n")
        written.append(str(p.relative_to(REPO_ROOT)))
    return written


def verify():
    """Regenerate and compare. Any drift between the module and the committed artifacts is an
    error, exactly as in the 001 bundle."""
    bad = []
    for name, fn in _GENERATED:
        p = _gen_path(name)
        if not p.exists():
            bad.append((name, "MISSING"))
            continue
        if p.read_text() != canonical_json(fn()) + "\n":
            bad.append((name, "DRIFT"))
    return {"ok": not bad, "problems": bad}


def main(argv=None):                                             # pragma: no cover - thin CLI
    import argparse
    ap = argparse.ArgumentParser(description="RP-D-LC-001b preflight artifacts (no solver runs)")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        for p in write():
            print("wrote", p)
    if a.verify:
        r = verify()
        print("verify:", "OK" if r["ok"] else r["problems"])
        return 0 if r["ok"] else 1
    return 0


if __name__ == "__main__":                                       # pragma: no cover
    raise SystemExit(main())
