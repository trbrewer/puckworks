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
CORRECTION_VERSION = "PREFLIGHT-C8"
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
    {
        "correction_version": "PREFLIGHT-C4",
        "reviewed_head": "e455c678a2fdd511ce9a30f1d15164f73b9a4481",
        "reviewed_tree": "72eda81e3ddea54ad4714f10c6bb4b347cd6a15a",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C5_DECISION_"
                        "PATH_AND_LINEAGE_CORRECTION_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(60, 77)],
        "superseded_artifact_sha256": {
            "protocol.json":
                "9d1853b841067896562bd5fbdb3a590dcbbfe0a9f0cca5af01b00f0d08764292",
            "fixture_spec.json":
                "c50521a10059fbc8af37c6b6a60fcc32f6e916b5be182c6d92a1f8d9eed75bf0",
            "execution_matrix.json":
                "734e6fadf972f9454928a66578aa626f71d8ba00e0a6c4dcce0e5b63647d1220",
            "preflight_status.json":
                "f3ecfd3afef8517bbff831bf2cac1c8740d02a43a6c5cfe972eca12ce1f44752",
        },
        "superseded_counts": {"adaptive_maximum": 703, "planned_normal_solves": 383,
                              "planned_fixed_step_audits": 320,
                              "planned_pressure_plane_diagnostic_rows": 0,
                              "mandatory_minimum": 112, "refused_after_earliest_stop": 591},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
    },
    {
        "correction_version": "PREFLIGHT-C5",
        "reviewed_head": "acb4f6a77c65378fcef7ed3d0a03af8620880bcb",
        "reviewed_tree": "4c53c4b2acb83079037667f78c471fb16b8f938f",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C6_ENDPOINT_"
                        "RECOMPUTATION_AND_DIAGNOSTIC_SEMANTICS_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(78, 89)],
        "superseded_artifact_sha256": {
            "protocol.json":
                "2ac2b2a18a56552aedefee5f4c013869c64a885347ac06d71aa12411ba2e9a54",
            "fixture_spec.json":
                "a803545ee8976975c063c255530af052b0a796db65c1b3fdf4a89576629b3dc3",
            "execution_matrix.json":
                "1a57d2ee54cd29ad662783dcbc52741fc1c0d65c3aa73a85d6aac2d3249cf81f",
            "preflight_status.json":
                "2ce0e09a572cf0d915d1c1fe38bda397c5e0c35c0f02f2fc7ed53f52bad7fc8b",
        },
        "superseded_counts": {"adaptive_maximum": 703, "planned_normal_solves": 383,
                              "planned_fixed_step_audits": 320,
                              "mandatory_minimum": 112, "refused_after_earliest_stop": 591,
                              "rows_classed_diagnostic_only": 3},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
        "accepted_without_change": "PE-66 resolution comparison coordinate value / S**n",
    },
    {
        "correction_version": "PREFLIGHT-C6",
        "reviewed_head": "76e5669670213f33c6496b98cc4d2cdfc9711b35",
        "reviewed_tree": "489af8f01d2bcf6009dbfa1dbd8a0cc82fd205e7",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C7_DIAGNOSTIC_"
                        "ATTEMPT_AND_EXECUTION_AUTHORITY_LINEAGE_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(89, 101)],
        "superseded_artifact_sha256": {
            "protocol.json":
                "ae6b61e0c36f4817652fba10d1961087babecf52084a2cce51261da7fcbb96d0",
            "fixture_spec.json":
                "45746921faf3fe5534f7d493ee0fb84633145142be821d9f6829e33704380225",
            "execution_matrix.json":
                "c4b4c77d5171d522e433ebdca42d1ee027d537ab307f0f43316a475a9efca0f0",
            "preflight_status.json":
                "75a1c65b67c65abf56bb558177c57d41f48155b2c9e9173f591fc6eaf6496311",
        },
        "superseded_counts": {"adaptive_maximum": 703, "decision_bearing_rows": 698,
                              "tau_diagnostic_rows": 2, "execution_assurance_rows": 3,
                              "mandatory_minimum": 110, "refused_after_earliest_stop": 591},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
        "accepted_without_change": ("PE-66 resolution comparison coordinate value / S**n; the "
                                    "mandatory-minimum change from 112 to 110"),
    },
    {
        "correction_version": "PREFLIGHT-C7",
        "reviewed_head": "b5eb3786a71514ceb937e0772144e050e461a3fc",
        "reviewed_tree": "d11331486b36f20e421835ce7bd16dd87a7782db",
        "disposition": ("RP_D_LC_001B_PREFLIGHT_EXACT_HEAD_REVIEW_NOT_APPROVED_C8_AUTHORIZATION_"
                        "PROOF_AND_PREDECESSOR_LINEAGE_REQUIRED"),
        "errata": ["PE-%d" % i for i in range(101, 114)],
        "superseded_artifact_sha256": {
            "protocol.json":
                "d35eec46569c9b599eb353598579e55d35af2a2646d0198b1612cf044c57fdbd",
            "fixture_spec.json":
                "9d31df49694d294f152553574953ecdadc0cdfa483709cfa5aef9400031286e0",
            "execution_matrix.json":
                "ff452a49b9d15430c0fa8c2fc03789fb3b6ea401b2c4b10bffae966bf217580d",
            # erratum PE-113: the ACTUAL committed hash. The C7 commit message quotes
            # 07cf090f..., computed before the final documentation edits moved
            # input_file_sha256; that message is history and is not amended.
            "preflight_status.json":
                "b9e74571d45acc3b84412a161bd64d860870b654df972e1957b372de6989fe86",
        },
        "superseded_counts": {"adaptive_maximum": 703, "decision_bearing_rows": 698,
                              "tau_diagnostic_rows": 2, "execution_assurance_rows": 3,
                              "mandatory_minimum": 110, "refused_after_earliest_stop": 591},
        "apparatus_accepted_in_principle":
            "common_mode_port_blind_pocket_off_on_comparison",
        "accepted_without_change": ("PE-66; the 112 to 110 mandatory minimum; and both C7 "
                                    "judgment calls - measured-historical dependency, clean-tree "
                                    "and seed fields, and source-commit tracked-file hashing"),
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
    # erratum PE-88: each statistic gets the serialisation term appropriate to ITSELF. C5 derived
    # both from the MEAN, so with abs(mean) << max_abs the maximum bound carried a term too small
    # for its own statistic.
    u_ser_mean = 10.0 ** (-_RECORD_DP) * (1.0 + abs(mean_pt))
    u_ser_max = 10.0 ** (-_RECORD_DP) * (1.0 + abs(max_pt))
    out = {
        "axial_pressure_scale": scale,
        "mean_delta_p": mean_pt, "abs_mean_delta_p": abs(mean_pt), "max_abs_delta_p": max_pt,
        "spatial_sd_delta_p": normal_delta["spatial_sd_delta_p"],
        "spatial_sd_role": normal_delta["spatial_sd_role"],
        "safety_factor": sf,
        "u_mean_gap": u_mean, "u_max_gap": u_max,
        "u_serialization_mean": u_ser_mean, "u_serialization_max": u_ser_max,
        "serialization_rule": ("10**(-RECORD_DP) * (1 + abs(statistic)), taken from EACH "
                               "statistic's own magnitude; the maximum bound never borrows the "
                               "mean's term (erratum PE-88)"),
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
    out["mean_gap_upper_rel"] = _finite((abs(mean_pt) + u_mean + u_ser_mean) / scale,
                                        "mean_gap_upper_rel")
    out["max_gap_upper_rel"] = _finite((max_pt + u_max + u_ser_max) / scale,
                                       "max_gap_upper_rel")
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
        # erratum PE-87: the three RAW terms, explicitly named. The safety factor is applied
        # ONCE, to their sum, and never to a term individually.
        "delta_R_fixed_step_raw": u_cont,
        "delta_R_node_offset_raw": u_offset,
        "u_serialization_R_raw": u_serial,
        "u_continuation_R_abs": u_cont,
        "u_node_offset_R_abs": u_offset,
        "u_serialisation_R_abs": u_serial,
        "safety_factor": float(safety),
        "composition": ("u_artifact_R = safety_factor * (delta_R_fixed_step_raw + "
                        "delta_R_node_offset_raw + u_serialization_R_raw)"),
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


def _carry_sources(sample):
    """The fields a resolution gate needs from a derived sample, lineage included (PE-85)."""
    out = {"value": sample["value"], "case_id": sample["case_id"],
           "record_sha256": sample["record_sha256"]}
    for k in SAMPLE_SOURCE_FIELDS:
        if k in sample:
            out[k] = list(sample[k])
    for k in ("area_case_id", "area_record_sha256", "quantity_definition"):
        if k in sample:
            out[k] = sample[k]
    return out


def _sample_sources(row):
    """The complete ordered lineage of one sample, tolerating a pre-C6 single-source row."""
    ids = row.get("source_case_ids") or [row["case_id"]]
    hashes = row.get("source_record_sha256") or [row["record_sha256"]]
    roles = row.get("source_roles") or ["primary"]
    return list(zip(roles, ids, hashes))


def _per_level_sources(rows):
    out = {}
    for r in sorted(rows, key=lambda x: str(x.get("forcing_level"))):
        out[r["forcing_level"]] = [
            {"role": role, "case_id": cid, "record_sha256": h}
            for role, cid, h in _sample_sources(r)]
    return out


def _union_source_ids(rows):
    ids = []
    for r in rows:
        for _role, cid, _h in _sample_sources(r):
            if cid not in ids:
                ids.append(cid)
    return assert_flat_id_list(sorted(ids), "gate source case ids")


def _union_source_hashes(rows):
    hs = []
    for r in rows:
        for _role, _cid, h in _sample_sources(r):
            if h not in hs:
                hs.append(h)
    return assert_flat_hash_list(sorted(hs), "gate source hashes")


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
        # erratum PE-85: the COMPLETE lineage — every record behind every level, unioned, plus
        # the per-level breakdown. `case_ids` above remains the convenience primary set.
        "per_level_sources": _per_level_sources(rows),
        "source_case_ids": _union_source_ids(rows),
        "source_record_sha256": _union_source_hashes(rows),
        "source_roles": sorted({role for r in rows for role in r.get("source_roles", [])}),
        "quantity_definition": next((r["quantity_definition"] for r in rows
                                     if r.get("quantity_definition")), None),
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
        # erratum PE-85: the COMPLETE lineage at BOTH resolutions — open and blocked for R,
        # coupon and area for actual Xi — in the generic schema.
        "per_resolution_sources": {
            "S%d" % S_COARSE: [{"role": role, "case_id": cid, "record_sha256": h}
                               for role, cid, h in _sample_sources(coarse)],
            "S%d" % S_FINE: [{"role": role, "case_id": cid, "record_sha256": h}
                             for role, cid, h in _sample_sources(fine)]},
        "source_case_ids": _union_source_ids([coarse, fine]),
        "source_record_sha256": _union_source_hashes([coarse, fine]),
        "source_roles": sorted({role for r in (coarse, fine)
                                for role in (r.get("source_roles") or ["primary"])}),
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
        "class": None, "adaptive": False, "scientific_role": None,
    }
    row.update(kw)
    # erratum PE-80: the frozen scientific role is EXPLICIT on every row, so the generic
    # "diagnostic_only" class string can never carry two incompatible meanings again.
    if row["scientific_role"] is None:
        row["scientific_role"] = row_scientific_role(row)
    elif row["scientific_role"] not in ROW_SCIENTIFIC_ROLES:
        raise ValueError("unknown scientific role %r" % (row["scientific_role"],))
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
    # The SCHEDULED tau cross-check (PE-12), NON-ADJUDICATIVE since PE-65 and now labelled to
    # match (erratum PE-78). It is a planned solver invocation and NOT a decision-bearing row:
    # it may not alter admission, uncertainty, classification, selection, any gate verdict or any
    # disposition, and its failure may not stop P0 (erratum PE-79).
    for S in SCIENTIFIC_RESOLUTIONS:
        rows.append(_row(phase="P0", kind="tau_cross_check", S=S, forcing_level="central",
                         tau_plus=TAU_CROSS_CHECK, state="reference_blocked", variant="mirror",
                         record_schema="full_case", **{"class": "diagnostic_only"},
                         scientific_role="TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"))
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
    # erratum PE-78: the tau rows leave the mandatory minimum. It counts decision-bearing
    # mandatory rows plus the pre-freeze execution-assurance replicates, which ARE adjudicative.
    mandatory_with_replicates = mandatory + sum(
        1 for r in rows
        if row_scientific_role(r) == "EXECUTION_ASSURANCE_REPLICATE"
        and r["phase"] in ("P0", "P1a"))
    # every count below is DERIVED from the row set in this one place (erratum PE-74 §15); no
    # number is preserved cosmetically and none is written by hand.
    pre_rows = [r for r in rows if r["phase"] in ("P0", "P1a", "P1b", "P2a")]
    pre_normal = sum(1 for r in pre_rows if r["run_mode"] == "NORMAL")
    pre_audit = len(pre_rows) - pre_normal
    coupon_kinds = ("axial_coupon", "bridge_coupon")
    n_node_offset = sum(1 for r in rows if r["kind"] not in coupon_kinds)
    # ---- role-resolved counts (errata PE-78 … PE-80) -------------------------------------
    by_role = {}
    for r in rows:
        role = row_scientific_role(r)
        by_role[role] = by_role.get(role, 0) + 1
    decision_rows = [r for r in rows if row_scientific_role(r) == "DECISION_BEARING"]
    tau_rows = [r for r in rows
                if row_scientific_role(r) == "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"]
    assurance_rows = [r for r in rows
                      if row_scientific_role(r) == "EXECUTION_ASSURANCE_REPLICATE"]
    dec_audit = sum(1 for r in decision_rows
                    if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X")
    mandatory_decision = sum(1 for r in decision_rows if r["class"] == "mandatory")
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
        "same_field_node_offset_summaries": n_node_offset,
        # ---- role-resolved counts, DERIVED here and nowhere else (errata PE-78 … PE-80) ------
        "by_scientific_role": by_role,
        "scientific_roles": {k: dict(v) for k, v in ROW_SCIENTIFIC_ROLES.items()},
        "decision_bearing_rows": len(decision_rows),
        "decision_bearing_normal_solves": len(decision_rows) - dec_audit,
        "decision_bearing_fixed_step_audits": dec_audit,
        "tau_diagnostic_rows": len(tau_rows),
        "execution_assurance_rows": len(assurance_rows),
        "mandatory_decision_bearing_rows": mandatory_decision,
        "diagnostic_row_policy": (
            "a tau_plus = 1.2 row is a planned solver invocation and NOT a decision-bearing row: "
            "it may alter nothing and its failure may not stop a phase (errata PE-65, PE-78, "
            "PE-79). A determinism replicate is an EXECUTION_ASSURANCE_REPLICATE whose payload "
            "equality is enforced and whose failure semantics are unchanged (erratum PE-80)."),
        "node_offset_policy": ("node-offset summaries are extracted from the SAME field as their "
                               "case and never increment the provider-call count (PE-41)"),
        # ---- provider-call accounting, DERIVED here and nowhere else (erratum PE-74) ---------
        "pre_freeze_rows": len(pre_rows),
        "pre_freeze_normal_rows": pre_normal,
        "pre_freeze_fixed_step_rows": pre_audit,
        "provider_calls_fresh_full_pre_freeze_run": pre_normal + pre_audit,
        "provider_calls_on_exact_resume": 0,
        "provider_call_rule": ("observed_provider_calls == newly_executed_rows in every phase; a "
                               "resumed phase legitimately has FEWER provider calls than "
                               "completed rows, and an exact manifest resume has none at all "
                               "(errata PE-74, PE-75)"),
        "arithmetic_only_phases": ["P2b"],
        "arithmetic_only_solver_calls": 0,
        "p3_p4_planning_template_rows": len(post),
        "row_scientific_roles": {k: dict(v) for k, v in ROW_SCIENTIFIC_ROLES.items()},
        "phase_ledgers": list(PHASE_LEDGERS),
        "diagnostic_semantics": {
            "tau_plus_1p2_role": "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE",
            "tau_plus_1p2_effect": "RECORD_DIAGNOSTIC_AND_CONTINUE",
            "tau_evidence_structure": "diagnostic_evidence['tau_plus_1p2']",
            "tau_in_common_reference_evidence": False,
            "determinism_role": "EXECUTION_ASSURANCE_REPLICATE",
            "determinism_semantics_unchanged": True,
            "erratum": "PE-78/PE-79/PE-80/PE-81",
        },
        "p2b_endpoint_recomputation": {
            "builder": "build_p2b_decision_payload",
            "consumed_by": ["assemble_p2b_from_runs", "_test_only_assemble_p2b_from_runs",
                            "validate_p2b_manifest"],
            "payload_hash_field": "scientific_decision_payload_sha256",
            "payload_hash_source": ("the INDEPENDENTLY constructed scientific payload, never the "
                                    "persisted candidate ledger"),
            "erratum": "PE-82/PE-83/PE-84",
        },
        "sample_source_fields": list(SAMPLE_SOURCE_FIELDS),
        "multi_source_quantities": {
            "R_identical": ["open", "blocked"],
            "Xi_actual": ["bridge_coupon", "candidate_blocked_area"],
        },
        "artifact_uncertainty_composition": (
            "u_artifact_R = NUMERICAL_DISCREPANCY_SAFETY_FACTOR * (delta_R_fixed_step_raw + "
            "delta_R_node_offset_raw + u_serialization_R_raw); the factor is applied ONCE, to "
            "the full sum (erratum PE-87)"),
        "pressure_serialization": (
            "u_serialization_mean from abs(mean_delta_p) and u_serialization_max from "
            "abs(max_abs_delta_p); the maximum bound never borrows the mean's term (PE-88)"),
        "execution_authority_schema": {
            "schema_version": EXECUTION_AUTHORITY_SCHEMA_VERSION,
            "fields": list(EXECUTION_AUTHORITY_FIELDS),
            "measured_historical_fields": list(MEASURED_HISTORICAL_AUTHORITY_FIELDS),
            "hash_field": "execution_authority_sha256",
            "hash_source": "record_hash(execution_authority), computed OUTSIDE the object",
            "persisted_in": "every phase manifest, complete; and nested in the P2b assembly "
                            "authority",
            "historical_validation": ("the recorded Git commit and tree, and every tracked input "
                                      "file, document and committed generated artifact read AT "
                                      "that commit — never from the current checkout"),
            "erratum": "PE-93/PE-95/PE-96/PE-99",
        },
        "diagnostic_attempt_failure": {
            "eligible_roles": list(DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES),
            "failure_codes": list(DIAGNOSTIC_FAILURE_CODES),
            "failure_stages": list(DIAGNOSTIC_FAILURE_STAGES),
            "schema_version": DIAGNOSTIC_FAILURE_SCHEMA_VERSION,
            "status": DIAGNOSTIC_ATTEMPT_STATUS,
            "evidence_status": "NON_ADJUDICATIVE_NOT_SCIENTIFIC_EVIDENCE",
            "never_caught": [c.__name__ for c in DIAGNOSTIC_NEVER_CAUGHT],
            "coexistence": ("a normal case record and a diagnostic-attempt failure envelope may "
                            "never coexist for one case ID"),
            "erratum": "PE-89/PE-90/PE-91/PE-92",
        },
        "p2b_assembly_authority_fields": list(P2B_ASSEMBLY_AUTHORITY_FIELDS),
        "source_authorization_schema": {
            "fields": list(SOURCE_AUTHORIZATION_FIELDS),
            "driver_path": DRIVER_REL,
            "constants": sorted(AUTHORIZATION_CONSTANTS),
            "stage_gate_kind": dict(STAGE_GATE_KIND),
            "parsed_from": ("the TRACKED driver source AT source_commit, by module-level AST "
                            "literal assignment; never a runtime object, an environment "
                            "variable, a caller list or the validating checkout"),
            "authority_provenance": list(AUTHORITY_PROVENANCE),
            "erratum": "PE-101/PE-102/PE-103/PE-104",
        },
        "phase_authority_artifact": {
            "schema_version": PHASE_AUTHORITY_SCHEMA_VERSION,
            "filename": "%s<phase>.json" % PHASE_AUTHORITY_PREFIX,
            "written": "BEFORE the first provider call, atomically and immutably",
            "bound_by": ["phase manifest", "every case record",
                         "every diagnostic-failure envelope"],
            "erratum": "PE-105",
        },
        "diagnostic_failure_fields": list(DIAGNOSTIC_FAILURE_FIELDS),
        "post_freeze_historical_version_boundary": (
            "DEFERRED P3/P4 PREREQUISITE: every validator requires equality with the CURRENT "
            "correction version, which suffices for P0-P2b under one reviewed authority version "
            "but NOT for a later P3/P4 review commit validating historical C8-era authorities. "
            "C8 does not implement the dispatcher and does not claim otherwise."),
        "post_freeze_executor_ready": False,
        "post_freeze_deferral": ("P3/P4 orchestration still derives its universe from these "
                                 "templates; the approved instantiated-matrix loader has not "
                                 "passed exact-head review and P3/P4 are hard-refused "
                                 "(erratum PE-76)"),
        "pressure_diagnostic_rows_policy": ("no separate pressure-diagnostic row exists or may "
                                            "return; the pressure control is formed from the "
                                            "SAME record as its case (errata PE-41, PE-60)"),
        "mandatory_minimum": mandatory_with_replicates,
        "conditional_minimum": 0,
        "adaptive_maximum": total,
        "diagnostic_replicates": len(assurance_rows),
        "replicate_placement": (
            "three replicates, in P0, P1a and P3 — the three phases producing decision-bearing "
            "records from DISTINCT fixture families (reference-blocked, identical-path, mirror). "
            "P2a re-uses those families and P4 re-uses P3's fixtures with an obstruction, so a "
            "fourth would add no independent evidence. Each replicate repeats a case its own "
            "phase already runs, so P1a's is identical-path and cannot reveal a mirror "
            "observable."),
        "refused_after_earliest_stop": total - mandatory_with_replicates - len(tau_rows),
        "refused_after_earliest_stop_rule": (
            "every row that is neither a mandatory decision-bearing row, nor a pre-freeze "
            "execution-assurance replicate, nor a non-adjudicative tau diagnostic. The tau rows "
            "are excluded because they are neither decision-bearing nor refused: they run and "
            "report, and nothing consumes them (erratum PE-78)."),
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
        "tau_cross_check_disposition": dict(TAU_CROSS_CHECK_DISPOSITION),
        "pressure_decision_path": {
            "point_verdict": "measured_zero_driver_point_pass",
            "point_role": "PRELIMINARY_POINT_ESTIMATE_SCREEN_MAY_REJECT_NEVER_ADMITS",
            "final_verdict": "measured_zero_driver_upper_bound_pass",
            "final_rule": ("BOTH mean_gap_upper_rel and max_gap_upper_rel <= "
                           "TOL_LATERAL_DRIVER_REL at every required resolution and forcing "
                           "level, from each normal record's OWN exact fixed-step audit"),
            "erratum": "PE-60/PE-61",
        },
        "required_quantity_sets": {
            "p0_reference_forcing": list(P0_REFERENCE_FORCING_QUANTITIES),
            "p0_coupon_forcing": list(P0_COUPON_FORCING_QUANTITIES),
            "p0_reference_resolution": list(P0_REFERENCE_RESOLUTION_QUANTITIES),
            "p0_coupon_resolution": list(P0_COUPON_RESOLUTION_QUANTITIES),
            "p0_reference_contrast": list(P0_REFERENCE_CONTRAST_QUANTITIES),
            "p0_reference_contrast_applicability": P0_REFERENCE_CONTRAST_APPLICABILITY,
            "candidate_component_forcing": list(CANDIDATE_COMPONENT_FORCING_QUANTITIES),
            "candidate_boundary_forcing": list(CANDIDATE_BOUNDARY_FORCING_QUANTITIES),
            "candidate_resolution": list(CANDIDATE_RESOLUTION_QUANTITIES),
            "aggregate_area_definitions": dict(AGGREGATE_AREA_DEFINITIONS),
            "actual_xi_definition": ACTUAL_XI_DEFINITION,
            "artifact_point_estimate_coverage": ARTIFACT_POINT_ESTIMATE_COVERAGE,
            "exactness_rule": ("the adjudicated set must EQUAL the required set; a nonempty "
                               "intersection, a subset, a two-level ladder, a single-resolution "
                               "gate and a similarly named surrogate are failures"),
        },
        "resolution_comparison_coordinate": {
            "form": "value / S**n",
            "exponents": dict(RESOLUTION_SCALING_EXPONENT),
            "provenance": RESOLUTION_SCALING_PROVENANCE,
        },
        "p2b_assembly_authority_fields": list(P2B_ASSEMBLY_AUTHORITY_FIELDS),
        "resume": {
            "order": ("resolve -> derive the record path -> reuse an EXACT match with NO "
                      "provider call -> fail closed on any difference -> only then call the "
                      "guarded provider"),
            "accounting": list(EXECUTION_COUNT_FIELDS),
            "invariant": "n_provider_calls == n_newly_executed",
            "erratum": "PE-74/PE-75",
        },
        "post_freeze_executor_ready": False,
        "post_freeze_deferral": (
            "P3/P4 orchestration still derives its universe from the planning templates; the "
            "approved instantiated-matrix loader has not passed exact-head review and P3/P4 are "
            "hard-refused independently of the solving allowlist (erratum PE-76)"),
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
        "post_freeze_executor_ready": False,
        "authorised_solving_phases": [],
        "authorised_assembly_phases": [],
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


#: The canonical execution-authority schema (erratum PE-93/PE-96).
#:
#: C6 persisted only ``execution_authority_sha256`` and a handful of convenience fields; the
#: complete object — every input-file hash, the protocol/geometry/errata document hashes, the
#: stage, the prerequisites, the dependency identity, the clean-tree proof — lived only in
#: transient Python memory, so nothing downstream could reconstruct it.
#:
#: The object itself carries NO self-referential hash. ``execution_authority_sha256`` is
#: computed separately as ``record_hash(execution_authority)``.
EXECUTION_AUTHORITY_SCHEMA_VERSION = 1
EXECUTION_AUTHORITY_FIELDS = (
    "schema_version", "stage", "tranche", "correction_version",
    "source_commit", "source_tree", "working_tree_clean", "clean_tree_required",
    "base_commit", "base_tree",
    "protocol_sha256", "geometry_spec_sha256", "errata_sha256", "input_file_sha256",
    "protocol_config_sha256", "fixture_spec_sha256", "execution_matrix_sha256",
    "backend", "dependencies", "seed", "solver_config", "prerequisites",
    # errata PE-101/PE-102: the committed authorization snapshot is part of the AUTHORITY, and
    # therefore inside execution_authority_sha256. Changing any part of it moves every record,
    # envelope, manifest and P2b artifact bound to that hash.
    "source_authorization", "authority_provenance",
)
#: An authority is PRODUCTION only when the committed driver authorized its stage. TEST_ONLY is
#: the private synthetic provenance and is rejected by every production validator (PE-103).
AUTHORITY_PROVENANCE = ("PRODUCTION", "TEST_ONLY")
#: The documents whose hashes the authority records, and the field each is recorded under.
AUTHORITY_DOCUMENT_FIELDS = {
    "protocol_sha256": PROTOCOL_PATH,
    "geometry_spec_sha256": BUNDLE_REL + "/VIRTUAL_FIXTURE_SPEC.md",
    "errata_sha256": ERRATA_PATH,
}
#: The generated artifacts whose canonical hashes the three configuration fields must equal.
AUTHORITY_CONFIG_ARTIFACTS = {
    "protocol_config_sha256": BUNDLE_REL + "/generated/protocol.json",
    "fixture_spec_sha256": BUNDLE_REL + "/generated/fixture_spec.json",
    "execution_matrix_sha256": BUNDLE_REL + "/generated/execution_matrix.json",
}


#: MEASURED HISTORICAL CLAIMS. These three cannot be re-derived from Git by any later process:
#: the clean-tree status was observed once, the dependency identity is the interpreter and
#: library versions that were present, and the seed is a declaration that no RNG was used. Their
#: integrity rests on being BOUND INSIDE the authority hash, which every case record, every
#: diagnostic envelope, every phase manifest and every P2b artifact cites. Validation checks
#: their schema and their internal consistency and does not pretend to reproduce them.
MEASURED_HISTORICAL_AUTHORITY_FIELDS = ("working_tree_clean", "dependencies", "seed")
_VERSION_RE = __import__("re").compile(r"^[0-9]+(\.[0-9]+)*([a-zA-Z0-9._+-]*)$")


# ---- the COMMITTED source-controlled authorization snapshot (errata PE-101 … PE-103) --------
# C7's authority proved that ``source_commit`` exists, that its tree matches and that every
# tracked file hashes as recorded. It never asked the one question an execution record must
# answer: DID THAT COMMIT AUTHORIZE THIS PHASE? The runtime gate reads the allowlists from the
# LIVE import, so a historical record proved nothing about the allowlists at its own commit.
#
# The snapshot below is parsed from the TRACKED driver source AT ``source_commit`` — never from a
# monkeypatched runtime object, an environment variable, a caller-supplied list, or the
# validating checkout.

DRIVER_REL = "puckworks/validation/slow/rp_d_lc_001b.py"
#: The three literal constants the driver must declare, and the type each must have.
AUTHORIZATION_CONSTANTS = {
    "AUTHORISED_SOLVING_PHASES": tuple,
    "AUTHORISED_ASSEMBLY_PHASES": tuple,
    "POST_FREEZE_EXECUTOR_READY": bool,
}
#: Which committed allowlist authorizes which stage, and what else that stage additionally needs.
STAGE_GATE_KIND = {
    "P0": "SOLVING", "P1a": "SOLVING", "P1b": "SOLVING", "P2a": "SOLVING",
    "P2b": "ASSEMBLY",
    "P3": "POST_FREEZE_SOLVING", "P4": "POST_FREEZE_SOLVING",
}
SOURCE_AUTHORIZATION_FIELDS = (
    "driver_path", "driver_file_sha256", "authorised_solving_phases",
    "authorised_assembly_phases", "post_freeze_executor_ready",
    "stage", "required_gate", "stage_authorised",
)


class SourceAuthorizationError(ExecutionAuthorityError):
    """The committed driver does not authorize the stage, or cannot be parsed strictly."""


def _literal_tuple_or_bool(node, name):
    """A STRICT literal reader. Anything computed, aliased or environment-dependent is
    rejected outright — an authorization constant may never be inferred (erratum PE-101)."""
    import ast
    try:
        value = ast.literal_eval(node)
    except (ValueError, SyntaxError, TypeError):
        raise SourceAuthorizationError(
            "%s is not a literal assignment in the committed driver; an authorization constant "
            "may never be computed, aliased or environment-dependent" % name)
    want = AUTHORIZATION_CONSTANTS[name]
    if want is tuple:
        if not isinstance(value, tuple):
            raise SourceAuthorizationError("%s must be a literal tuple, got %s"
                                           % (name, type(value).__name__))
        if not all(isinstance(v, str) for v in value):
            raise SourceAuthorizationError("%s must contain only phase names" % name)
        return tuple(value)
    if not isinstance(value, bool):
        raise SourceAuthorizationError("%s must be a literal bool, got %s"
                                       % (name, type(value).__name__))
    return value


def parse_committed_authorization(driver_source, driver_path=DRIVER_REL):
    """Parse the three authorization constants from committed driver SOURCE, by AST.

    An AST walk over module-level assignments cannot confuse a comment, a docstring or a string
    literal with code, which an unconstrained regex can. A duplicate assignment is rejected: two
    values for one constant means the effective value depends on evaluation order, which is not
    an authorization anyone reviewed.
    """
    import ast
    try:
        tree = ast.parse(driver_source, filename=driver_path)
    except SyntaxError as exc:
        raise SourceAuthorizationError("the committed driver %r does not parse: %s"
                                       % (driver_path, exc))
    found = {}
    for node in tree.body:                      # MODULE LEVEL only: no conditional redefinition
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name) or target.id not in AUTHORIZATION_CONSTANTS:
                continue
            if target.id in found:
                raise SourceAuthorizationError(
                    "the committed driver assigns %s more than once; the effective value would "
                    "depend on evaluation order" % target.id)
            found[target.id] = _literal_tuple_or_bool(node.value, target.id)
    missing = sorted(set(AUTHORIZATION_CONSTANTS) - set(found))
    if missing:
        raise SourceAuthorizationError(
            "the committed driver %r declares no module-level literal %r" % (driver_path,
                                                                             missing))
    for name in ("AUTHORISED_SOLVING_PHASES", "AUTHORISED_ASSEMBLY_PHASES"):
        for phase in found[name]:
            if phase not in PHASE_PREREQUISITES:
                raise SourceAuthorizationError("%s names an unknown phase %r" % (name, phase))
    for phase in found["AUTHORISED_SOLVING_PHASES"]:
        if STAGE_GATE_KIND[phase] == "ASSEMBLY":
            raise SourceAuthorizationError(
                "phase %r is an ARITHMETIC assembly phase and may never appear in "
                "AUTHORISED_SOLVING_PHASES" % (phase,))
    for phase in found["AUTHORISED_ASSEMBLY_PHASES"]:
        if STAGE_GATE_KIND[phase] != "ASSEMBLY":
            raise SourceAuthorizationError(
                "phase %r is a SOLVING phase and may never appear in "
                "AUTHORISED_ASSEMBLY_PHASES" % (phase,))
    return found


def source_authorization_snapshot(stage, driver_source, driver_path=DRIVER_REL):
    """The canonical authorization snapshot for one stage, from committed driver source."""
    if stage not in STAGE_GATE_KIND:
        raise SourceAuthorizationError("unknown stage %r" % (stage,))
    parsed = parse_committed_authorization(driver_source, driver_path=driver_path)
    gate = STAGE_GATE_KIND[stage]
    solving = list(parsed["AUTHORISED_SOLVING_PHASES"])
    assembly = list(parsed["AUTHORISED_ASSEMBLY_PHASES"])
    ready = parsed["POST_FREEZE_EXECUTOR_READY"]
    if gate == "SOLVING":
        authorised = stage in solving
    elif gate == "ASSEMBLY":
        authorised = stage in assembly
    else:                                        # POST_FREEZE_SOLVING needs BOTH
        authorised = bool(stage in solving and ready)
    return {
        "driver_path": driver_path,
        "driver_file_sha256": hashlib.sha256(driver_source.encode("utf-8")).hexdigest(),
        "authorised_solving_phases": solving,
        "authorised_assembly_phases": assembly,
        "post_freeze_executor_ready": bool(ready),
        "stage": stage,
        "required_gate": gate,
        "stage_authorised": bool(authorised),
    }


def committed_source_authorization(stage, commit, driver_path=DRIVER_REL):
    """The snapshot as it was AT ``commit`` — read through Git, never from the checkout."""
    raw = _git_object_bytes(commit, driver_path)
    return source_authorization_snapshot(stage, raw.decode("utf-8"), driver_path=driver_path)


class ExecutionNotAuthorised(RuntimeError):
    """A phase is not authorized by the committed source constants (erratum PE-104).

    Defined here, beside the parser, so the driver and the assembler share ONE implementation
    rather than two copies that can drift. The driver re-exports it.
    """


def assert_stage_authorised(stage, driver_source=None):
    """The one shared source-controlled gate (erratum PE-104).

    Reads the LIVE committed driver by default — the runtime gate's job — and refuses unless the
    frozen constants authorize the stage. Historical proof that a PAST commit authorized a stage
    is the authority's ``source_authorization`` snapshot; this is the complementary check that
    the CURRENT source authorizes the call about to be made.
    """
    if driver_source is None:
        path = REPO_ROOT / DRIVER_REL
        if not path.exists():                     # pragma: no cover - the driver is tracked
            raise ExecutionAuthorityError("the driver %r is missing" % (DRIVER_REL,))
        driver_source = path.read_text()
    snap = source_authorization_snapshot(stage, driver_source)
    if not snap["stage_authorised"]:
        raise ExecutionNotAuthorised(
            "phase %r is NOT AUTHORISED by the source-controlled constants: "
            "AUTHORISED_SOLVING_PHASES = %r, AUTHORISED_ASSEMBLY_PHASES = %r, "
            "POST_FREEZE_EXECUTOR_READY = %r. Its %s gate must name it, and adding it is its own "
            "reviewed source commit (erratum PE-104)."
            % (stage, tuple(snap["authorised_solving_phases"]),
               tuple(snap["authorised_assembly_phases"]),
               snap["post_freeze_executor_ready"], snap["required_gate"]))
    return snap


def execution_authority_sha256(authority) -> str:
    """``record_hash`` of the complete authority object, computed OUTSIDE it (PE-93)."""
    return record_hash(authority)


def _git_object_bytes(commit, rel):
    """Read a tracked file AS IT WAS at ``commit`` — never from the current working tree."""
    import subprocess
    try:
        out = subprocess.run(["git", "show", "%s:%s" % (commit, rel)], cwd=REPO_ROOT,
                             capture_output=True, check=True).stdout
    except Exception as exc:
        raise ExecutionAuthorityError(
            "the historical authority names %r at commit %s, which cannot be read from the "
            "repository (%s)" % (rel, commit, exc))
    return out


def _git_commit_exists(commit) -> bool:
    import subprocess
    r = subprocess.run(["git", "cat-file", "-e", "%s^{commit}" % commit], cwd=REPO_ROOT,
                       capture_output=True)
    return r.returncode == 0


def execution_authority(stage: str, backend: str = "reference", require_clean: bool = True):
    """The PRODUCTION execution authority. Everything a future stage must record so its output
    can never be attributed to a head that did not produce it — and it FAILS CLOSED (PE-11).

    It raises ``ExecutionAuthorityError`` rather than returning ``None`` for: an unusable git
    identity, a dirty working tree, a missing input file, an unsupported backend, an unknown
    stage, or — since erratum PE-103 — **a source commit whose committed allowlists do not
    authorize the stage**. A partial authority record is never returned.

    There is no public provenance or authorization override. The private synthetic path is
    :func:`_test_only_execution_authority`, whose output every production validator rejects.
    """
    return _build_execution_authority(stage, backend=backend, require_clean=require_clean,
                                      authority_provenance="PRODUCTION")


def _test_only_execution_authority(stage: str, backend: str = "reference",
                                   require_clean: bool = False):
    """PRIVATE synthetic authority (erratum PE-103).

    Synthetic pipelines need a historical-looking authority while the real allowlists remain
    empty. This one carries ``authority_provenance = "TEST_ONLY"`` and the ACTUAL committed
    authorization snapshot, including ``stage_authorised = False``. Production validation rejects
    it, and it cannot be handed to the public production execution or assembly APIs.
    """
    return _build_execution_authority(stage, backend=backend, require_clean=require_clean,
                                      authority_provenance="TEST_ONLY")


def _build_execution_authority(stage: str, backend: str = "reference",
                               require_clean: bool = True,
                               authority_provenance: str = "PRODUCTION"):
    """The shared builder. Private: the provenance argument is never publicly reachable."""
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
    # erratum PE-99: an authority BINDS A COMMITTED HEAD, so every tracked hash it records is
    # the hash of the content AT ``commit``, not of whatever happens to be in the working tree.
    # ``working_tree_clean`` separately records whether the two agreed when it was built, and a
    # production authority requires that they did.
    files = {}
    for rel in INPUT_FILES:
        if _sha_file(rel) is None:
            raise ExecutionAuthorityError(
                "input file %r is missing; an authority may not record a null hash" % rel)
        files[rel] = hashlib.sha256(_git_object_bytes(commit, rel)).hexdigest()
    docs = {}
    for field, rel in sorted(AUTHORITY_DOCUMENT_FIELDS.items()):
        if _sha_file(rel) is None:
            raise ExecutionAuthorityError("the %s document is missing" % rel)
        docs[field] = hashlib.sha256(_git_object_bytes(commit, rel)).hexdigest()
    protocol_sha = docs["protocol_sha256"]
    geometry_sha = docs["geometry_spec_sha256"]
    errata_sha = docs["errata_sha256"]
    try:
        import scipy
        scipy_v = scipy.__version__
    except Exception as exc:                                 # pragma: no cover - env limit
        raise ExecutionAuthorityError("scipy is required for the geometry audits (%s)" % exc)
    # erratum PE-103: the committed driver must AUTHORIZE this stage. A production authority is
    # not constructible at a source commit whose allowlists do not name it.
    authz = committed_source_authorization(stage, commit)
    if authority_provenance not in AUTHORITY_PROVENANCE:
        raise ExecutionAuthorityError("unknown authority provenance %r" % (authority_provenance,))
    if authority_provenance == "PRODUCTION" and not authz["stage_authorised"]:
        raise SourceAuthorizationError(
            "source commit %s does not authorize stage %r: %s = %r, %s = %r, "
            "POST_FREEZE_EXECUTOR_READY = %r. A production execution authority may only be built "
            "at a commit whose reviewed source constants name the stage (erratum PE-103)."
            % (commit, stage, "AUTHORISED_SOLVING_PHASES", authz["authorised_solving_phases"],
               "AUTHORISED_ASSEMBLY_PHASES", authz["authorised_assembly_phases"],
               authz["post_freeze_executor_ready"]))
    out = {
        "schema_version": EXECUTION_AUTHORITY_SCHEMA_VERSION,
        "stage": stage,
        "tranche": TRANCHE_ID,
        "source_authorization": authz,
        "authority_provenance": authority_provenance,
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
    # the three configuration hashes are likewise those of the COMMITTED generated artifacts
    for field, rel in sorted(AUTHORITY_CONFIG_ARTIFACTS.items()):
        raw = _git_object_bytes(commit, rel).decode("utf-8")
        try:
            out[field] = record_hash(json.loads(raw))
        except Exception as exc:                          # pragma: no cover - committed artifact
            raise ExecutionAuthorityError("the committed %r is not readable JSON: %s"
                                          % (rel, exc))
    return out


def validate_execution_authority(authority, expected_stage=None, expected_current_authority=None,
                                 require_production=True):
    """Validate a HISTORICAL execution authority independently (errata PE-95, PE-96, PE-99).

    C6 validated 40-character strings. This asks Git whether ``source_commit`` is a real commit,
    whether ``rev-parse <commit>^{tree}`` equals ``source_tree``, and reads every tracked input
    file, document and generated artifact **from that commit** to recompute its hash.

    ``expected_current_authority`` is for EXACT same-phase resume only: when supplied, the whole
    object must be canonically equal. Downstream historical validation supplies none and
    validates the embedded object on its own terms — a later phase's authority may NEVER stand in
    for an earlier phase's, because that would rewrite execution history.
    """
    if not isinstance(authority, dict):
        raise ExecutionAuthorityError("no execution authority was persisted")
    missing = [k for k in EXECUTION_AUTHORITY_FIELDS if k not in authority]
    if missing:
        raise ExecutionAuthorityError("the execution authority is missing %r" % (missing,))
    extra = sorted(set(authority) - set(EXECUTION_AUTHORITY_FIELDS))
    if extra:
        raise ExecutionAuthorityError("the execution authority carries unknown field(s) %r"
                                      % (extra,))
    canonical_json(authority)                 # strict: canonical and finite, or it is not bound
    if authority["schema_version"] != EXECUTION_AUTHORITY_SCHEMA_VERSION:
        raise ExecutionAuthorityError("execution-authority schema version %r, expected %r"
                                      % (authority["schema_version"],
                                         EXECUTION_AUTHORITY_SCHEMA_VERSION))
    if authority["tranche"] != TRANCHE_ID:
        raise ExecutionAuthorityError("the authority binds tranche %r" % (authority["tranche"],))
    if authority["correction_version"] != CORRECTION_VERSION:
        raise ExecutionAuthorityError("the authority is from a superseded correction version %r"
                                      % (authority["correction_version"],))
    stage = authority["stage"]
    if stage not in PHASE_PREREQUISITES:
        raise ExecutionAuthorityError("the authority declares an unknown stage %r" % (stage,))
    if expected_stage is not None and stage != expected_stage:
        raise ExecutionAuthorityError("the authority declares stage %r, expected %r"
                                      % (stage, expected_stage))
    if list(authority["prerequisites"]) != list(PHASE_PREREQUISITES[stage]):
        raise ExecutionAuthorityError(
            "the authority declares prerequisites %r; stage %r requires exactly %r"
            % (authority["prerequisites"], stage, list(PHASE_PREREQUISITES[stage])))
    if authority["backend"] not in SUPPORTED_BACKENDS:
        raise ExecutionAuthorityError("the authority names an unsupported backend %r"
                                      % (authority["backend"],))
    if require_production:
        if authority["clean_tree_required"] is not True:
            raise ExecutionAuthorityError("a production authority must require a clean tree")
        if authority["working_tree_clean"] is not True:
            raise ExecutionAuthorityError("a production authority records a dirty working tree")
    if authority["seed"] is not None:
        raise ExecutionAuthorityError("this programme uses no RNG; seed must be null")
    prov = authority["authority_provenance"]
    if prov not in AUTHORITY_PROVENANCE:
        raise ExecutionAuthorityError("unknown authority provenance %r" % (prov,))
    if require_production and prov != "PRODUCTION":
        raise ExecutionAuthorityError(
            "the authority carries authority_provenance=%r; production validation accepts "
            "PRODUCTION only (erratum PE-103)" % (prov,))
    want_solver = {"tau_plus": TAU_PLUS, "nu": NU, "rtol": RTOL, "check": CHECK,
                   "min_steps": MIN_STEPS, "max_steps": MAX_STEPS}
    if authority["solver_config"] != want_solver:
        raise ExecutionAuthorityError("the authority's baseline solver configuration is not the "
                                      "frozen one")
    deps = authority["dependencies"]
    if not isinstance(deps, dict) or sorted(deps) != ["numpy", "python", "scipy"]:
        raise ExecutionAuthorityError("the authority's dependency identity is malformed")
    for name, v in sorted(deps.items()):
        if not isinstance(v, str) or not v:
            raise ExecutionAuthorityError("the authority's dependency identity is malformed")
        if not _VERSION_RE.match(v):
            raise ExecutionAuthorityError(
                "the authority records %r = %r, which is not a version string" % (name, v))
    if (authority["base_commit"], authority["base_tree"]) != (BASE_COMMIT, BASE_TREE):
        raise ExecutionAuthorityError("the authority records a different base commit/tree")

    # ---- the historical Git identity, established against the repository, not a string ------
    commit, tree = authority["source_commit"], authority["source_tree"]
    for name, v in (("source_commit", commit), ("source_tree", tree)):
        if not isinstance(v, str) or len(v) != 40 or set(v) - set("0123456789abcdef"):
            raise ExecutionAuthorityError("the authority's %s is not a git object name" % name)
    if not _git_commit_exists(commit):
        raise ExecutionAuthorityError(
            "the authority names source_commit %s, which is not a commit in this repository "
            "(erratum PE-99)" % commit)
    actual_tree = _git("rev-parse", "%s^{tree}" % commit)
    if actual_tree != tree:
        raise ExecutionAuthorityError(
            "the authority pairs source_commit %s with source_tree %s; that commit's tree is %s "
            "(erratum PE-99)" % (commit, tree, actual_tree))
    if not _git_commit_exists(BASE_COMMIT):                # pragma: no cover - base is reachable
        raise ExecutionAuthorityError("the recorded base commit is not in this repository")
    if _git("rev-parse", "%s^{tree}" % BASE_COMMIT) != BASE_TREE:
        raise ExecutionAuthorityError(          # pragma: no cover - base is frozen
            "the recorded base commit/tree relationship does not hold")

    # ---- every tracked input file, document and generated artifact, AT that commit -----------
    files = authority["input_file_sha256"]
    if not isinstance(files, dict) or sorted(files) != sorted(INPUT_FILES):
        raise ExecutionAuthorityError(
            "the authority's input-file map is not the exact frozen set; got %r"
            % (sorted(files) if isinstance(files, dict) else type(files).__name__,))
    for rel, want in sorted(files.items()):
        got = hashlib.sha256(_git_object_bytes(commit, rel)).hexdigest()
        if got != want:
            raise ExecutionAuthorityError(
                "the authority records %s for input file %r; at commit %s it hashes to %s"
                % (want, rel, commit, got))
    for field, rel in sorted(AUTHORITY_DOCUMENT_FIELDS.items()):
        got = hashlib.sha256(_git_object_bytes(commit, rel)).hexdigest()
        if authority[field] != got:
            raise ExecutionAuthorityError(
                "the authority records %s = %s; %r at commit %s hashes to %s"
                % (field, authority[field], rel, commit, got))
    for field, rel in sorted(AUTHORITY_CONFIG_ARTIFACTS.items()):
        raw = _git_object_bytes(commit, rel).decode("utf-8")
        try:
            doc = json.loads(raw)
        except Exception as exc:                          # pragma: no cover - committed artifact
            raise ExecutionAuthorityError("the committed %r is not readable JSON: %s"
                                          % (rel, exc))
        got = record_hash(doc)
        if authority[field] != got:
            raise ExecutionAuthorityError(
                "the authority records %s = %s; the committed %r canonically hashes to %s "
                "(erratum PE-99)" % (field, authority[field], rel, got))

    # ---- errata PE-101 … PE-103: the committed driver must AUTHORIZE the recorded stage -----
    # Recomputed from the driver AS IT WAS at source_commit, and compared exactly.
    persisted = authority["source_authorization"]
    if not isinstance(persisted, dict):
        raise ExecutionAuthorityError("the authority carries no source-authorization snapshot")
    missing_authz = [k for k in SOURCE_AUTHORIZATION_FIELDS if k not in persisted]
    if missing_authz:
        raise ExecutionAuthorityError("the source-authorization snapshot is missing %r"
                                      % (missing_authz,))
    extra_authz = sorted(set(persisted) - set(SOURCE_AUTHORIZATION_FIELDS))
    if extra_authz:
        raise ExecutionAuthorityError("the source-authorization snapshot carries unknown "
                                      "field(s) %r" % (extra_authz,))
    driver_path = persisted["driver_path"]
    if driver_path != DRIVER_REL:
        raise ExecutionAuthorityError("the snapshot names driver %r; the frozen driver is %r"
                                      % (driver_path, DRIVER_REL))
    rebuilt = committed_source_authorization(stage, commit, driver_path=driver_path)
    if record_hash(rebuilt) != record_hash(persisted):
        bad = sorted(k for k in SOURCE_AUTHORIZATION_FIELDS if rebuilt[k] != persisted[k])
        raise SourceAuthorizationError(
            "the persisted source-authorization snapshot does not recompute from the driver at "
            "commit %s; differing field(s): %r (erratum PE-101)" % (commit, bad))
    if require_production and not rebuilt["stage_authorised"]:
        raise SourceAuthorizationError(
            "source commit %s does not authorize stage %r (%s gate); a production authority may "
            "not stand on an unauthorized commit (erratum PE-103)"
            % (commit, stage, rebuilt["required_gate"]))
    if not rebuilt["stage_authorised"] and prov != "TEST_ONLY":
        raise SourceAuthorizationError(   # pragma: no cover - unreachable while both are checked
            "an unauthorized stage may only be carried by an explicitly TEST_ONLY authority")

    if expected_current_authority is not None:
        if record_hash(authority) != record_hash(expected_current_authority):
            raise ExecutionAuthorityError(
                "the persisted authority is not the one this resume was invoked under; exact "
                "same-phase resume requires canonical equality of the complete object")
    return authority


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
                     scientific_payload_sha256=None, phase_authority_file_sha256=None):
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
        "execution_authority_sha256": execution_authority_sha256(authority),
        # erratum PE-105: the artifact that holds the authority's PREIMAGE, so a partial record
        # set is independently interpretable before the final manifest exists.
        "phase_authority_file_sha256": phase_authority_file_sha256,
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


def validate_case_record(rec, row=None, authority=None, phase=None,
                        expected_predecessors=None, phase_authority_file_sha256=None):
    """Fail-closed structural validation. Raises with the first defect found."""
    for k in ("schema_version", "correction_version", "phase", "case_id", "row_sha256", "row",
              "forcing_exact", "forcing_repr", "source_commit", "source_tree",
              "execution_authority_sha256", "phase_authority_file_sha256",
              "predecessor_manifest_sha256", "run_mode", "completed_steps", "status",
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
    if rec["schema_version"] != CASE_RECORD_SCHEMA_VERSION:
        raise ValueError("case record declares schema version %r, expected %r"
                         % (rec["schema_version"], CASE_RECORD_SCHEMA_VERSION))
    if authority is not None:
        # erratum PE-94: the authority HASH is load-bearing. C6 compared a few fragments and
        # never looked at execution_authority_sha256 at all, so a record could cite an authority
        # it did not match.
        if rec.get("execution_authority_sha256") != execution_authority_sha256(authority):
            raise ValueError(
                "case record %r cites execution_authority_sha256 %r; its phase authority hashes "
                "to %r (erratum PE-94)"
                % (rec.get("case_id"), rec.get("execution_authority_sha256"),
                   execution_authority_sha256(authority)))
        for k in ("source_commit", "source_tree"):
            if rec[k] != authority[k]:
                raise ValueError("case record %s %r does not match the authority %r"
                                 % (k, rec[k], authority[k]))
        for k in ("protocol_config_sha256", "fixture_spec_sha256", "execution_matrix_sha256"):
            if rec.get(k) != authority[k]:
                raise ValueError("case record %s does not bind this configuration" % (k,))
        if rec.get("backend") != authority["backend"]:
            raise ValueError("case record backend does not match the authority")
        if rec.get("dependencies") != authority["dependencies"]:
            raise ValueError("case record dependency identity does not match the authority")
        if rec.get("correction_version") != authority["correction_version"]:
            raise ValueError(   # pragma: no cover - both checked against CORRECTION_VERSION
                "case record correction version does not match the authority")
        if phase is not None and authority["stage"] != phase:
            raise ValueError(   # pragma: no cover - the validator pins the stage first
                "case record phase %r is validated against a stage-%r authority"
                % (phase, authority["stage"]))
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
    # erratum PE-106: the predecessor map is compared at FINAL validation, not only on resume
    if expected_predecessors is not None:
        if dict(rec.get("predecessor_manifest_sha256") or {}) != dict(expected_predecessors):
            raise ValueError(
                "case record %r cites predecessor manifests %r; its phase manifest cites %r "
                "(erratum PE-106)" % (rec.get("case_id"),
                                      sorted((rec.get("predecessor_manifest_sha256") or {})),
                                      sorted(expected_predecessors)))
    # erratum PE-105: the record is bound to the artifact holding the authority's preimage
    if phase_authority_file_sha256 is not None:
        if rec.get("phase_authority_file_sha256") != phase_authority_file_sha256:
            raise ValueError(
                "case record %r cites phase-authority file hash %r; the persisted artifact "
                "hashes to %r (erratum PE-105)"
                % (rec.get("case_id"), rec.get("phase_authority_file_sha256"),
                   phase_authority_file_sha256))
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


#: The per-phase execution accounting a resume must report (erratum PE-74).
EXECUTION_COUNT_FIELDS = ("n_new_case_records", "n_new_diagnostic_failure_envelopes",
                          "n_reused_case_records", "n_reused_diagnostic_failure_envelopes",
                          "n_newly_executed", "n_reused", "n_provider_calls", "n_completed",
                          "n_failed", "n_refused", "n_diagnostic_completed",
                          "n_diagnostic_failed")


# ---- ONE pure, no-solver row-identity resolver (erratum PE-110 §8.4) ------------------------
# The driver resolves a row to a fixture or coupon in order to SOLVE it. Validation needs the
# same identity without a solver and without duplicating any coordinate logic, so both go
# through this one function.

def row_geometry_identity(row):
    """Deterministically derive one row's geometry identity. NO solver, NO provider, NO field.

    Returns the geometry kind, shape, candidate bridge identity, fixture state and variant,
    obstruction status and mask SHA-256 — everything a record or an envelope claims about the
    geometry it was built on.
    """
    kind = row["kind"]
    if isinstance(row.get("bridge"), str):
        raise ValueError("row %r still carries an UNRESOLVED placeholder bridge %r"
                         % (row["case_id"], row["bridge"]))
    if kind == "axial_coupon":
        mask, meta = build_axial_coupon(row["S"], row["coupon_level"],
                                        row["coupon_orientation"])
        geom_kind = "coupon"
    elif kind == "bridge_coupon":
        b = row["bridge"]
        mask, meta = build_bridge_coupon(row["S"], b["w"], b["kz"])
        geom_kind = "coupon"
    else:
        variant = row["variant"] if row["variant"] in ("mirror", "identical") else "mirror"
        bridge = row["bridge"] if isinstance(row["bridge"], dict) else None
        if kind in ("reference_blocked_ladder", "tau_cross_check"):
            bridge = None
        mask, meta = build_fixture(row["S"], bridge=bridge,
                                   connected=(row["state"] == "open"), variant=variant,
                                   swapped=bool(row["swapped"]),
                                   perturbation=row["perturbation"],
                                   obstructed=bool(row["obstructed"]))
        geom_kind = "fixture"
    return {
        "kind": geom_kind,
        "mask_sha256": meta["mask_sha256"],
        "S": row["S"],
        "shape": list(meta.get("shape") or mask.shape),
        "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
        "state": row["state"],
        "variant": row["variant"],
        "obstructed": bool(meta.get("obstructed")),
    }


def _envelope_audit_plan(row, doc):
    """The audit plan a fixed-step row's persisted solver configuration implies.

    An envelope records the configuration it was invoked under; for a fixed-step row that pins
    ``min_steps == max_steps == target``, which is exactly what the stored configuration states.
    Reconstructing it from the stored target lets the solver configuration be RECOMPUTED rather
    than trusted, without needing the base record the attempt never produced.
    """
    if row["run_mode"] != "FIXED_STEP_REEXECUTION_1P5X":
        return None
    cfg = doc.get("solver_config") or {}
    target = cfg.get("fixed_step_target")
    if target is None:
        raise ValueError("a fixed-step diagnostic envelope records no fixed-step target")
    return {"target_steps": int(target)}


# ---- the DURABLE per-phase authority artifact (erratum PE-105) ------------------------------
# C7's complete authority reached disk only inside the FINAL phase manifest, so an interrupted
# phase left records citing an opaque hash whose preimage existed only in transient memory. The
# artifact below is written atomically BEFORE the first provider call and is the identity
# available during a partial phase.

PHASE_AUTHORITY_SCHEMA_VERSION = 1
PHASE_AUTHORITY_PREFIX = "execution_authority_"


def phase_authority_filename(phase: str) -> str:
    """Deterministic, one per phase. Never a counter, a timestamp or an ordering."""
    if phase not in PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r" % (phase,))
    return "%s%s.json" % (PHASE_AUTHORITY_PREFIX, phase)


def make_phase_authority_document(phase, authority, predecessor_manifest_sha256,
                                  provenance_mode="PRODUCTION"):
    """The immutable per-phase authority document (erratum PE-105).

    It deliberately carries NO self-referential file hash; the caller or manifest computes the
    file's SHA-256 after writing.
    """
    if authority.get("stage") != phase:
        raise ValueError("a stage-%r authority may not be persisted for phase %r"
                         % (authority.get("stage"), phase))
    doc = {
        "schema_version": PHASE_AUTHORITY_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": phase,
        "provenance_mode": provenance_mode,
        "execution_authority": dict(authority),
        "execution_authority_sha256": execution_authority_sha256(authority),
        "source_authorization": dict(authority["source_authorization"]),
        "predecessor_manifest_sha256": dict(predecessor_manifest_sha256),
        "authority_filename": phase_authority_filename(phase),
        "authorises": ("EXACTLY ONE PHASE: this document authorises %r and no other. It is "
                       "written BEFORE the first provider call, so a partial phase's records "
                       "remain independently interpretable (erratum PE-105)." % (phase,)),
    }
    canonical_json(doc)                      # strict: canonical and finite, or it is not bound
    return doc


def write_phase_authority(runs_dir, doc, allow_resume=True):
    """Atomic, immutable, no-overwrite, exact-match resume — as for a case record."""
    base = pathlib.Path(runs_dir)
    base.mkdir(parents=True, exist_ok=True)
    path = base / doc["authority_filename"]
    payload = canonical_json(doc) + "\n"
    if path.exists():
        if not allow_resume:                            # pragma: no cover - guarded by caller
            raise FileExistsError("phase authority %s exists and overwrite is refused" % path)
        if path.read_text() != payload:
            raise ResumeMismatch(
                "a phase-authority artifact already exists at %s and differs from the authority "
                "this run was invoked under; a partial phase may only be resumed under its EXACT "
                "authority (erratum PE-105)" % path)
        return path, "REUSED_EXACT_MATCH"
    tmp = base / (path.name + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)
    return path, "WRITTEN"


def read_phase_authority(runs_dir, phase):
    """Reopen the persisted phase authority and return ``(doc, path, file_sha256)``."""
    path = pathlib.Path(runs_dir) / phase_authority_filename(phase)
    if not path.exists():
        raise ManifestMissing("the %s phase-authority artifact does not exist at %s"
                              % (phase, path))
    raw = path.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    if raw.decode("utf-8") != canonical_json(doc) + "\n":
        raise ManifestMissing("the %s phase-authority artifact is not canonically serialised"
                              % (phase,))
    return doc, path, hashlib.sha256(raw).hexdigest()


def validate_phase_authority_document(doc, phase, require_production=True,
                                      expected_current_authority=None,
                                      expected_predecessors=None):
    """Validate a persisted phase-authority artifact and the authority inside it."""
    for k in ("schema_version", "correction_version", "phase", "provenance_mode",
              "execution_authority", "execution_authority_sha256", "source_authorization",
              "predecessor_manifest_sha256", "authority_filename"):
        if k not in doc:
            raise ManifestMissing("the phase-authority artifact is missing %r" % (k,))
    if doc["schema_version"] != PHASE_AUTHORITY_SCHEMA_VERSION:
        raise ManifestMissing("phase-authority schema version %r, expected %r"
                              % (doc["schema_version"], PHASE_AUTHORITY_SCHEMA_VERSION))
    if doc["correction_version"] != CORRECTION_VERSION:
        raise ManifestMissing("the phase-authority artifact is from a superseded correction "
                              "version")
    if doc["phase"] != phase:
        raise ManifestMissing("the phase-authority artifact declares phase %r, expected %r"
                              % (doc["phase"], phase))
    if doc["authority_filename"] != phase_authority_filename(phase):
        raise ManifestMissing("the phase-authority artifact names the wrong file")
    if require_production and doc["provenance_mode"] != "PRODUCTION":
        raise ManifestMissing("the %s phase authority carries provenance_mode=%r; production "
                              "validation accepts PRODUCTION only" % (phase,
                                                                      doc["provenance_mode"]))
    try:
        auth = validate_execution_authority(
            doc["execution_authority"], expected_stage=phase,
            expected_current_authority=expected_current_authority,
            require_production=require_production)
    except ExecutionAuthorityError as exc:
        raise ManifestMissing("the %s phase authority is invalid: %s" % (phase, exc))
    if doc["execution_authority_sha256"] != execution_authority_sha256(auth):
        raise ManifestMissing("the %s phase-authority artifact cites a stale authority hash"
                              % (phase,))
    if doc["source_authorization"] != auth["source_authorization"]:
        raise ManifestMissing("the %s phase-authority artifact's authorization snapshot differs "
                              "from the authority it carries" % (phase,))
    if expected_predecessors is not None:
        if dict(doc["predecessor_manifest_sha256"]) != dict(expected_predecessors):
            raise ManifestMissing(
                "the %s phase-authority artifact cites predecessor manifests that differ from "
                "the phase manifest's (erratum PE-107)" % (phase,))
    return auth


class ResumeMismatch(ValueError):
    """An existing case record differs from the one this row requires. FAIL CLOSED: never
    overwrite it, and never call the provider to find out (erratum PE-74)."""


def load_resumable_case_record(runs_dir, row, authority, phase, predecessor_manifest_sha256,
                              geometry, provenance_mode="PRODUCTION", audit=None,
                              phase_authority_file_sha256=None):
    """Discover, reopen and fully validate an existing case record BEFORE any provider call.

    Returns ``(record, path)`` for an EXACT match, or ``None`` when no record exists. Anything
    else raises :class:`ResumeMismatch` — the record is not overwritten and the provider is not
    called (erratum PE-74).

    C4's executor resolved the row, called the provider, built the record and only then
    discovered an exact match and reported ``REUSED_EXACT_MATCH``. That is not a resume: every
    solve had already been paid for.
    """
    base = pathlib.Path(runs_dir)
    path = base / case_record_filename(row["case_id"])
    if not path.exists():
        return None
    raw = path.read_text()
    try:
        rec = json.loads(raw)
    except Exception as exc:
        raise ResumeMismatch("the existing record at %s is not readable JSON: %s" % (path, exc))
    if raw != canonical_json(rec) + "\n":
        raise ResumeMismatch("the existing record at %s is not canonically serialised" % path)
    if rec.get("case_id") != row["case_id"]:
        raise ResumeMismatch("the record file for %r carries case_id %r"
                             % (row["case_id"], rec.get("case_id")))
    try:
        validate_case_record(rec, row=row, authority=authority, phase=phase,
                             expected_predecessors=predecessor_manifest_sha256,
                             phase_authority_file_sha256=phase_authority_file_sha256)
    except ValueError as exc:
        raise ResumeMismatch("the existing record for %r does not validate against its row, "
                             "authority or configuration: %s" % (row["case_id"], exc))
    checks = (
        ("execution_authority_sha256", rec.get("execution_authority_sha256"),
         record_hash(authority)),
        ("predecessor_manifest_sha256", rec.get("predecessor_manifest_sha256"),
         dict(predecessor_manifest_sha256)),
        ("geometry", rec.get("geometry"), dict(geometry)),
        ("mask_sha256", rec.get("mask_sha256"), geometry.get("mask_sha256")),
        ("provenance_mode", rec.get("provenance_mode"), provenance_mode),
        ("backend", rec.get("backend"), authority["backend"]),
        ("run_mode", rec.get("run_mode"), row["run_mode"]),
        ("audit", rec.get("audit"), (None if audit is None else dict(audit))),
    )
    for name, got, want in checks:
        if got != want:
            raise ResumeMismatch(
                "the existing record for %r differs on %r; a resume reuses an EXACT match and "
                "otherwise fails closed WITHOUT calling the provider (erratum PE-74)"
                % (row["case_id"], name))
    want_status = run_status(rec["run_mode"], rec["completed_steps"],
                             target_steps=(None if audit is None else int(audit["target_steps"])))
    if rec.get("status") != want_status:
        raise ResumeMismatch(
            "the existing record for %r carries status %r; its own step count and audit plan "
            "recompute as %r" % (row["case_id"], rec.get("status"), want_status))
    want_payload = scientific_payload_hash(
        effective_solver_config(row, backend=authority["backend"], audit=audit),
        rec.get("scientific"), geometry.get("mask_sha256"))
    if rec.get("scientific_payload_sha256") != want_payload:
        raise ResumeMismatch("the existing record for %r carries a scientific payload hash that "
                             "does not recompute from its own contents" % (row["case_id"],))
    return rec, path


# ---- the NON-ADJUDICATIVE diagnostic-attempt failure envelope (errata PE-89 … PE-92) --------
# C6 made a tau diagnostic that PRODUCED a record and then failed a scientific check nonblocking.
# It did not make a tau ATTEMPT nonblocking: the role-aware classifier is reached only after the
# provider call, the compact extraction, the record construction and the record write have all
# succeeded, so a provider exception or a malformed result aborted P0 before ``diagnostic_failed``
# could exist. A diagnostic whose attempt can kill the phase is not a diagnostic.
#
# The scope is NARROW and explicit. Only the TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE role is
# eligible, only the categories below are caught, and authority, repository, persistence and
# orchestration failures remain FATAL.

DIAGNOSTIC_FAILURE_SCHEMA_VERSION = 1
DIAGNOSTIC_FAILURE_PREFIX = "diagnostic_failure_"
DIAGNOSTIC_ATTEMPT_STATUS = "DIAGNOSTIC_ATTEMPT_FAILED"

#: The frozen failure codes a diagnostic-attempt envelope may carry (erratum PE-90/PE-91).
DIAGNOSTIC_FAILURE_CODES = (
    "DIAGNOSTIC_PROVIDER_EXCEPTION",          # the provider raised during THIS diagnostic call
    "DIAGNOSTIC_RESULT_CONTRACT_INVALID",     # a missing field, wrong shape, incompatible array
    "DIAGNOSTIC_RESULT_NONFINITE",            # a non-finite value rejected during extraction
    "DIAGNOSTIC_SCIENTIFIC_EXTRACTION_FAILED",  # the compact science could not be formed
)

#: The stage of the attempt at which the failure occurred.
DIAGNOSTIC_FAILURE_STAGES = ("PROVIDER_CALL", "RESULT_CONTRACT", "SCIENTIFIC_EXTRACTION",
                             "RECORD_CONSTRUCTION")

#: Roles for which a diagnostic-attempt failure envelope may be written AT ALL. Everything else
#: keeps its existing fatal or phase-stopping semantics (erratum PE-89 §5.1).
DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES = ("TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE",)

#: Exceptions that are NEVER converted into a diagnostic result, whatever the row's role. An
#: interrupt, an authority failure, a persistence failure or a broken executor invariant means
#: the executor itself is not trustworthy (erratum PE-90 §5.2).
DIAGNOSTIC_NEVER_CAUGHT = (KeyboardInterrupt, SystemExit, ExecutionAuthorityError,
                           FreezeMissing, ManifestMissing, OSError, MemoryError)

#: The longest sanitised failure message retained. A bounded message keeps the envelope
#: canonical and strict-finite; the full traceback is retained only as a SHA-256.
DIAGNOSTIC_MESSAGE_MAX = 400


class DiagnosticAttemptFailed(RuntimeError):
    """A row-local failure of a NON-ADJUDICATIVE diagnostic attempt (erratum PE-89).

    Raised only for an eligible role and only for a frozen failure code. It is never raised for
    an adjudicative row, and never for an authority, repository, persistence or orchestration
    failure.
    """

    def __init__(self, code, stage, exc=None, detail=None):
        if code not in DIAGNOSTIC_FAILURE_CODES:
            raise ValueError("unknown diagnostic failure code %r" % (code,))
        if stage not in DIAGNOSTIC_FAILURE_STAGES:
            raise ValueError("unknown diagnostic failure stage %r" % (stage,))
        self.code = code
        self.stage = stage
        self.exc = exc
        self.detail = detail
        super().__init__("%s at %s: %s" % (code, stage, detail or exc))


def sanitise_failure_message(text):
    """A bounded, single-line, ASCII-safe message. Never a path, never unbounded output."""
    t = " ".join(str(text or "").split())
    t = t.encode("ascii", "replace").decode("ascii")
    if len(t) > DIAGNOSTIC_MESSAGE_MAX:
        t = t[:DIAGNOSTIC_MESSAGE_MAX - 3] + "..."
    return t


def diagnostic_failure_filename(case_id: str) -> str:
    """Deterministically derived from ``case_id``, exactly as a case record's name is."""
    return "%s%s.json" % (DIAGNOSTIC_FAILURE_PREFIX,
                          hashlib.sha256(case_id.encode("utf-8")).hexdigest())


#: The EXACT envelope key set (erratum PE-110). Missing or unknown keys are both refused.
DIAGNOSTIC_FAILURE_FIELDS = (
    "schema_version", "correction_version", "provenance_mode", "phase", "case_id", "row",
    "row_sha256", "scientific_role", "source_commit", "source_tree",
    "execution_authority_sha256", "phase_authority_file_sha256", "predecessor_manifest_sha256",
    "geometry_kind", "mask_sha256", "forcing_exact", "forcing_repr", "solver_config", "backend",
    "provider_called", "failure_stage", "failure_code", "exception_class",
    "result_contract_class", "message", "traceback_sha256", "status", "scientific",
    "evidence_status", "declaration",
)


def make_diagnostic_failure_envelope(row, authority, predecessor_manifest_sha256, geometry,
                                     failure, provenance_mode="PRODUCTION", audit=None,
                                     traceback_text=None, phase_authority_file_sha256=None):
    """The immutable record of a NON-ADJUDICATIVE diagnostic attempt that produced no result.

    It fabricates NO scientific value, carries no NaN or infinity, and declares itself
    ``NON_ADJUDICATIVE_NOT_SCIENTIFIC_EVIDENCE`` so nothing downstream can mistake it for
    evidence (erratum PE-92).
    """
    role = row_scientific_role(row)
    if role not in DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES:
        raise ValueError(
            "row %r carries the role %r; a diagnostic-attempt failure envelope may be written "
            "only for %r (erratum PE-89)"
            % (row["case_id"], role, list(DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES)))
    if failure.code not in DIAGNOSTIC_FAILURE_CODES:          # pragma: no cover - guarded above
        raise ValueError("unknown diagnostic failure code %r" % (failure.code,))
    exc = failure.exc
    doc = {
        "schema_version": DIAGNOSTIC_FAILURE_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "provenance_mode": provenance_mode,
        "phase": row["phase"],
        "case_id": row["case_id"],
        "row": dict(row),
        "row_sha256": row_sha256(row),
        "scientific_role": role,
        "source_commit": authority["source_commit"],
        "source_tree": authority["source_tree"],
        "execution_authority_sha256": execution_authority_sha256(authority),
        "phase_authority_file_sha256": phase_authority_file_sha256,
        "predecessor_manifest_sha256": dict(predecessor_manifest_sha256),
        "geometry_kind": geometry.get("kind"),
        "mask_sha256": geometry.get("mask_sha256"),
        "forcing_exact": dict(row["forcing_exact"]),
        "forcing_repr": row["forcing_repr"],
        "solver_config": effective_solver_config(row, backend=authority["backend"], audit=audit),
        "backend": authority["backend"],
        "provider_called": True,
        "failure_stage": failure.stage,
        "failure_code": failure.code,
        "exception_class": (None if exc is None else type(exc).__name__),
        "result_contract_class": failure.detail if exc is None else None,
        "message": sanitise_failure_message(failure.detail or exc),
        "traceback_sha256": (None if not traceback_text
                             else hashlib.sha256(traceback_text.encode("utf-8")).hexdigest()),
        "status": DIAGNOSTIC_ATTEMPT_STATUS,
        "scientific": None,
        "evidence_status": "NON_ADJUDICATIVE_NOT_SCIENTIFIC_EVIDENCE",
        "declaration": (
            "this document records that a NON-ADJUDICATIVE diagnostic attempt produced no "
            "result. It fabricates no scientific value, enters no aggregate truth, no gate, no "
            "uncertainty, no candidate evidence, no common_reference_evidence and no P2b "
            "decision, and its presence does not stop the phase (errata PE-65, PE-89 … PE-92)."),
    }
    missing = [k for k in DIAGNOSTIC_FAILURE_FIELDS if k not in doc]
    if missing:                                # pragma: no cover - constructed complete above
        raise ValueError("diagnostic failure envelope is missing %r" % (missing,))
    canonical_json(doc)                       # strict: no NaN/Inf anywhere in a bound envelope
    return doc


def validate_diagnostic_failure_envelope(doc, row=None, authority=None, phase=None,
                                         provenance_mode=None, expected_predecessors=None,
                                         phase_authority_file_sha256=None):
    """Fail-closed validation of a diagnostic-attempt failure envelope (errata PE-109, PE-110).

    C7 compared the SEPARATELY STORED ``row_sha256`` against the external planned row and left
    the EMBEDDED ``doc["row"]`` unchecked, so a modified embedded row with an unchanged stored
    hash passed. It also checked forcing, solver, mask and predecessor identity on resume only.
    Both are closed here, so the envelope is self-authenticating wherever it is validated.
    """
    missing = [k for k in DIAGNOSTIC_FAILURE_FIELDS if k not in doc]
    if missing:
        raise ValueError("diagnostic failure envelope is missing %r" % (missing,))
    extra = sorted(set(doc) - set(DIAGNOSTIC_FAILURE_FIELDS))
    if extra:
        raise ValueError("diagnostic failure envelope carries unknown field(s) %r" % (extra,))
    if doc["schema_version"] != DIAGNOSTIC_FAILURE_SCHEMA_VERSION:
        raise ValueError("diagnostic failure envelope schema version %r, expected %r"
                         % (doc["schema_version"], DIAGNOSTIC_FAILURE_SCHEMA_VERSION))
    if doc["correction_version"] != CORRECTION_VERSION:
        raise ValueError("diagnostic failure envelope is from a superseded correction version")
    if doc["status"] != DIAGNOSTIC_ATTEMPT_STATUS:
        raise ValueError("diagnostic failure envelope carries status %r" % (doc["status"],))
    if doc["evidence_status"] != "NON_ADJUDICATIVE_NOT_SCIENTIFIC_EVIDENCE":
        raise ValueError("a diagnostic failure envelope must declare itself non-adjudicative")
    if doc["failure_code"] not in DIAGNOSTIC_FAILURE_CODES:
        raise ValueError("unknown diagnostic failure code %r" % (doc["failure_code"],))
    if doc["failure_stage"] not in DIAGNOSTIC_FAILURE_STAGES:
        raise ValueError("unknown diagnostic failure stage %r" % (doc["failure_stage"],))
    if doc["scientific_role"] not in DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES:
        raise ValueError(
            "a diagnostic failure envelope may not be written for the role %r; an adjudicative "
            "failure is never a diagnostic (erratum PE-89)" % (doc["scientific_role"],))
    if doc.get("scientific") is not None:
        raise ValueError("a diagnostic failure envelope may fabricate no scientific value")
    if doc["provider_called"] is not True:
        raise ValueError("a diagnostic failure envelope records a provider attempt")
    # erratum PE-109: the EMBEDDED row must hash to the stored value, so a modified embedded row
    # cannot hide behind an unchanged external comparison.
    if row_sha256(doc["row"]) != doc["row_sha256"]:
        raise ValueError(
            "diagnostic failure envelope %r embeds a row that does not hash to its own recorded "
            "row_sha256 (erratum PE-109)" % (doc["case_id"],))
    embedded = doc["row"]
    if embedded.get("case_id") != doc["case_id"]:
        raise ValueError("diagnostic failure envelope %r embeds a row for a different case"
                         % (doc["case_id"],))
    if embedded.get("phase") != doc["phase"]:
        raise ValueError("diagnostic failure envelope %r embeds a row from a different phase"
                         % (doc["case_id"],))
    if row_scientific_role(embedded) != doc["scientific_role"]:
        raise ValueError("diagnostic failure envelope %r embeds a row of a different role"
                         % (doc["case_id"],))
    # erratum PE-110: every row-derived field is recomputed and compared, wherever validated
    if dict(embedded["forcing_exact"]) != dict(doc["forcing_exact"]):
        raise ValueError("diagnostic failure envelope %r records a forcing rational that is not "
                         "its own row's" % (doc["case_id"],))
    if embedded["forcing_repr"] != doc["forcing_repr"]:
        raise ValueError("diagnostic failure envelope %r records a forcing repr that is not its "
                         "own row's" % (doc["case_id"],))
    want_cfg = effective_solver_config(embedded, backend=doc["backend"],
                                       audit=_envelope_audit_plan(embedded, doc))
    if doc["solver_config"] != want_cfg:
        raise ValueError(
            "diagnostic failure envelope %r records a solver configuration that is not the one "
            "its canonical row requires (erratum PE-110)" % (doc["case_id"],))
    want_geom = row_geometry_identity(embedded)
    if doc["geometry_kind"] != want_geom["kind"] or doc["mask_sha256"] != want_geom["mask_sha256"]:
        raise ValueError(
            "diagnostic failure envelope %r records a geometry or mask identity that its own row "
            "does not resolve to (erratum PE-110)" % (doc["case_id"],))
    if expected_predecessors is not None:
        if dict(doc["predecessor_manifest_sha256"]) != dict(expected_predecessors):
            raise ValueError(
                "diagnostic failure envelope %r cites predecessor manifests %r; its phase "
                "manifest cites %r (erratum PE-110)"
                % (doc["case_id"], sorted(doc["predecessor_manifest_sha256"]),
                   sorted(expected_predecessors)))
    if phase_authority_file_sha256 is not None:
        if doc.get("phase_authority_file_sha256") != phase_authority_file_sha256:
            raise ValueError(
                "diagnostic failure envelope %r cites phase-authority file hash %r; the "
                "persisted artifact hashes to %r (erratum PE-105)"
                % (doc["case_id"], doc.get("phase_authority_file_sha256"),
                   phase_authority_file_sha256))
    if row is not None:
        if doc["case_id"] != row["case_id"] or doc["row_sha256"] != row_sha256(row):
            raise ValueError("diagnostic failure envelope %r was cited for row %r"
                             % (doc["case_id"], row["case_id"]))
        if dict(embedded) != dict(row):
            raise ValueError(
                "diagnostic failure envelope %r embeds a row that is not the canonical planned "
                "row (erratum PE-109)" % (doc["case_id"],))
    if phase is not None and doc["phase"] != phase:
        raise ValueError("diagnostic failure envelope belongs to phase %r, not %r"
                         % (doc["phase"], phase))
    if provenance_mode is not None and doc["provenance_mode"] != provenance_mode:
        raise ValueError("diagnostic failure envelope provenance %r, expected %r"
                         % (doc["provenance_mode"], provenance_mode))
    if authority is not None:
        if doc["execution_authority_sha256"] != execution_authority_sha256(authority):
            raise ValueError("diagnostic failure envelope does not bind the phase authority")
        for k in ("source_commit", "source_tree"):
            if doc[k] != authority[k]:
                raise ValueError("diagnostic failure envelope %s does not match the authority"
                                 % (k,))
        if doc.get("backend") != authority["backend"]:
            raise ValueError("diagnostic failure envelope backend does not match the authority")
    canonical_json(doc)
    return doc


def write_diagnostic_failure_envelope(runs_dir, doc, allow_resume=True):
    """Atomic, immutable, no-overwrite, exact-match resume — as for a case record."""
    validate_diagnostic_failure_envelope(doc)
    base = pathlib.Path(runs_dir)
    base.mkdir(parents=True, exist_ok=True)
    path = base / diagnostic_failure_filename(doc["case_id"])
    rec_path = base / case_record_filename(doc["case_id"])
    if rec_path.exists():
        raise ValueError(
            "case %r already has a normal case record; a record and a diagnostic-attempt "
            "failure envelope may never coexist (erratum PE-92)" % (doc["case_id"],))
    payload = canonical_json(doc) + "\n"
    if path.exists():
        if not allow_resume:                              # pragma: no cover - guarded by caller
            raise FileExistsError("envelope %s already exists and overwrite is refused" % path)
        if path.read_text() != payload:
            raise ValueError(
                "a diagnostic failure envelope already exists at %s and differs from the one "
                "just produced; it is immutable (erratum PE-92)" % path)
        return path, "REUSED_EXACT_MATCH"
    tmp = base / (path.name + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)
    return path, "WRITTEN"


def read_diagnostic_failure_envelope(runs_dir, case_id):
    path = pathlib.Path(runs_dir) / diagnostic_failure_filename(case_id)
    if not path.exists():
        raise ManifestMissing("diagnostic failure envelope for %r does not exist at %s"
                              % (case_id, path))
    doc = json.loads(path.read_text())
    if doc.get("case_id") != case_id:
        raise ValueError("the envelope file for %r carries case_id %r"
                         % (case_id, doc.get("case_id")))
    return doc, path


def assert_no_coexisting_artifacts(runs_dir, case_id):
    """A normal case record and a diagnostic-failure envelope may never coexist (PE-92)."""
    base = pathlib.Path(runs_dir)
    rec = base / case_record_filename(case_id)
    env = base / diagnostic_failure_filename(case_id)
    if rec.exists() and env.exists():
        raise ResumeMismatch(
            "case %r has BOTH a normal case record and a diagnostic-attempt failure envelope; "
            "exactly one may exist and this fails closed (erratum PE-92)" % (case_id,))
    return rec.exists(), env.exists()


def load_resumable_diagnostic_failure(runs_dir, row, authority, phase,
                                      predecessor_manifest_sha256, geometry,
                                      provenance_mode="PRODUCTION", audit=None,
                                      phase_authority_file_sha256=None):
    """Discover, reopen and fully validate an existing envelope BEFORE any provider call.

    Returns ``(doc, path)`` for an EXACT match, ``None`` when none exists, and raises
    :class:`ResumeMismatch` on any difference.
    """
    base = pathlib.Path(runs_dir)
    path = base / diagnostic_failure_filename(row["case_id"])
    if not path.exists():
        return None
    raw = path.read_text()
    try:
        doc = json.loads(raw)
    except Exception as exc:                              # pragma: no cover - corrupt file
        raise ResumeMismatch("the existing envelope at %s is not readable JSON: %s"
                             % (path, exc))
    if raw != canonical_json(doc) + "\n":
        raise ResumeMismatch("the existing envelope at %s is not canonically serialised" % path)
    try:
        validate_diagnostic_failure_envelope(
            doc, row=row, authority=authority, phase=phase, provenance_mode=provenance_mode,
            expected_predecessors=predecessor_manifest_sha256,
            phase_authority_file_sha256=phase_authority_file_sha256)
    except ValueError as exc:
        raise ResumeMismatch("the existing envelope for %r does not validate: %s"
                             % (row["case_id"], exc))
    checks = (
        ("predecessor_manifest_sha256", doc.get("predecessor_manifest_sha256"),
         dict(predecessor_manifest_sha256)),
        ("mask_sha256", doc.get("mask_sha256"), geometry.get("mask_sha256")),
        ("geometry_kind", doc.get("geometry_kind"), geometry.get("kind")),
        ("backend", doc.get("backend"), authority["backend"]),
        ("solver_config", doc.get("solver_config"),
         effective_solver_config(row, backend=authority["backend"], audit=audit)),
    )
    for name, got, want in checks:
        if got != want:
            raise ResumeMismatch(
                "the existing envelope for %r differs on %r; a resume reuses an EXACT match and "
                "otherwise fails closed WITHOUT calling the provider (errata PE-74, PE-92)"
                % (row["case_id"], name))
    return doc, path


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
        # erratum PE-87: the RAW movement is the adjudicative term. The scaled value below is a
        # CONVENIENCE DIAGNOSTIC and must never be fed into a second composition.
        "max_abs_movement_raw": movement,
        "max_abs_movement": movement,
        "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
        "u_pressure_plane_R": NUMERICAL_DISCREPANCY_SAFETY_FACTOR * movement,
        "u_pressure_plane_R_role": ("CONVENIENCE_SCALED_DIAGNOSTIC_NOT_A_COMPOSER_INPUT; the "
                                    "adjudicative composer consumes max_abs_movement_raw "
                                    "(erratum PE-87)"),
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
        a_ids, a_h = [], []
        pair_audits = {}
        for st in ("blocked", "open"):
            for cid, a in audits.items():
                if a["row"].get("audit_of_case_id") == states[st]["case_id"]:
                    pair_audits[st] = a
        have_audits = set(pair_audits) == {"blocked", "open"}
        if have_audits:
            a_ids = [pair_audits["blocked"]["case_id"], pair_audits["open"]["case_id"]]
            a_h = [record_hash(pair_audits["blocked"]), record_hash(pair_audits["open"])]
        # PE-42: the node-offset ratio is formed ONLY from the exactly paired open/blocked
        # records. A same-state C_j/C_0 is not R, and a missing summary FAILS the evidence.
        p_ids, p_h, offs = [], [], None
        try:
            offs = node_offset_R(states["open"], states["blocked"])
        except (ValueError, NonFiniteValue):
            offs = None
        if offs is not None:
            p_ids = [offs["blocked_case_id"], offs["open_case_id"]]
            p_h = [offs["blocked_record_sha256"], offs["open_record_sha256"]]
        # ---- erratum PE-87: ONE canonical composer, RAW terms in, safety factor applied ONCE --
        # C5 summed u_fixed_step_R + u_pressure_plane_R + u_serialization_R where the first two
        # were ALREADY safety-scaled and the third was not, giving 2a + 2b + c instead of the
        # frozen 2*(a + b + c). numerical_discrepancy_R consumes the RAW conductances and the RAW
        # R-offset sequence and applies the factor exactly once to the full sum.
        complete = have_audits and offs is not None
        disc = None
        if complete:
            disc = numerical_discrepancy_R(
                R, Co, Cb, _conductance(pair_audits["open"]),
                _conductance(pair_audits["blocked"]),
                R_node_offsets=[r["R_offset"] for r in offs["R_offsets"]])
        u_fs_raw = None if disc is None else disc["u_continuation_R_abs"]
        u_pp_raw = None if disc is None else disc["u_node_offset_R_abs"]
        u_ser_raw = (10.0 ** (-_RECORD_DP) * (1.0 + abs(R)) if disc is None
                     else disc["u_serialisation_R_abs"])
        u_total = None if disc is None else disc["u_R_abs"]
        upper = (None if u_total is None else abs(R - 1.0) + u_total)
        ev = {
            "candidate_id": "w%d_kz%d" % bridge_key,
            "resolution": S, "forcing_level": level,
            "normal_case_ids": sorted(n_ids), "normal_record_sha256": sorted(n_h),
            "audit_case_ids": sorted(a_ids), "audit_record_sha256": sorted(a_h),
            "pressure_plane_case_ids": sorted(p_ids),
            "pressure_plane_record_sha256": sorted(p_h),
            "R_point": R,
            # the RAW component movements, before the frozen safety factor
            "delta_R_fixed_step_raw": (0.0 if u_fs_raw is None else u_fs_raw),
            "delta_R_node_offset_raw": (0.0 if u_pp_raw is None else u_pp_raw),
            "u_serialization_R_raw": u_ser_raw,
            "safety_factor": NUMERICAL_DISCREPANCY_SAFETY_FACTOR,
            "numerical_discrepancy_R": disc,
            # retained under their C5 names; each is now the RAW term times the factor, and the
            # three no longer sum to u_artifact_R because the factor is applied to the SUM.
            "u_fixed_step_R": (0.0 if u_fs_raw is None
                               else NUMERICAL_DISCREPANCY_SAFETY_FACTOR * u_fs_raw),
            "u_pressure_plane_R": (0.0 if u_pp_raw is None
                                   else NUMERICAL_DISCREPANCY_SAFETY_FACTOR * u_pp_raw),
            "node_offset_R": offs,
            "u_serialization_R": u_ser_raw,
            "u_artifact_R": (0.0 if u_total is None else u_total),
            "u_artifact_R_formula": (
                "NUMERICAL_DISCREPANCY_SAFETY_FACTOR * (delta_R_fixed_step_raw + "
                "delta_R_node_offset_raw + u_serialization_R_raw); the factor is applied ONCE, "
                "to the full sum (erratum PE-87)"),
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
                [s for s, ok in (("no fixed-step audit pair", have_audits),
                                 ("no paired node-offset evidence", offs is not None))
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


#: The frozen SCIENTIFIC ROLE of every row kind (errata PE-78 … PE-80).
#:
#: C5 used one string, ``class = "diagnostic_only"``, for two incompatible things — the
#: determinism replicates, whose payload equality IS enforced and whose failure IS a defect, and
#: (per PE-65) the ``tau_plus = 1.2`` rows, which may alter nothing at all. And the tau rows were
#: emitted ``class = "mandatory"`` anyway, so a diagnostic that PE-65 says may alter nothing could
#: terminate P0. One explicit role per row settles both.
ROW_SCIENTIFIC_ROLES = {
    "DECISION_BEARING": {
        "adjudicative": True,
        "enters_aggregate_truth": True,
        "enters_common_reference_evidence": True,
        "failure_effect": "STOPS_THE_PHASE",
        "ledger_on_pass": "completed",
        "ledger_on_fail": "failed",
        "description": ("an execution-authority row whose output feeds admission, uncertainty, "
                        "classification, selection or a disposition"),
    },
    "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE": {
        "adjudicative": False,
        "enters_aggregate_truth": False,
        "enters_common_reference_evidence": False,
        "failure_effect": "RECORD_DIAGNOSTIC_AND_CONTINUE",
        "ledger_on_pass": "diagnostic_completed",
        "ledger_on_fail": "diagnostic_failed",
        "description": ("erratum PE-65: no frozen assembled-fixture comparison quantity and no "
                        "tolerance exist, so this row may not alter admission, uncertainty, "
                        "classification, selection, any gate verdict or any disposition. It may "
                        "be absent, unconverged, invalid or otherwise failed without changing "
                        "P0's scientific terminal status (erratum PE-79)."),
    },
    "EXECUTION_ASSURANCE_REPLICATE": {
        "adjudicative": True,
        "enters_aggregate_truth": False,
        "enters_common_reference_evidence": False,
        "failure_effect": "STOPS_THE_PHASE",
        "ledger_on_pass": "completed",
        "ledger_on_fail": "failed",
        "description": ("a determinism replicate. Its scientific-payload equality with its "
                        "explicitly named base is separately enforced by the manifest validator "
                        "(erratum PE-37) and its currently frozen failure semantics are "
                        "UNCHANGED by C6; only the role name is made explicit (erratum PE-80)."),
    },
}

#: Kinds whose rows are non-adjudicative diagnostics.
DIAGNOSTIC_ONLY_KINDS = ("tau_cross_check",)
#: Kinds whose rows are execution-assurance controls.
EXECUTION_ASSURANCE_KINDS = ("determinism_replicate",)


def row_scientific_role(row):
    """The frozen scientific role of one canonical matrix row (erratum PE-80).

    Read from the row's own explicit ``scientific_role`` where the matrix carries one, and
    otherwise derived from the frozen kind so a record written before C6 still classifies.
    """
    declared = (row or {}).get("scientific_role")
    if declared:
        if declared not in ROW_SCIENTIFIC_ROLES:
            raise ValueError("unknown scientific role %r on row %r"
                             % (declared, (row or {}).get("case_id")))
        return declared
    kind = (row or {}).get("kind")
    if kind in DIAGNOSTIC_ONLY_KINDS:
        return "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"
    if kind in EXECUTION_ASSURANCE_KINDS:
        return "EXECUTION_ASSURANCE_REPLICATE"
    return "DECISION_BEARING"


def case_decision_verdict(row, scientific, execution_status):
    """The ONE role-aware case-level scientific classification (errata PE-58, PE-79).

    Used by the executor when it builds its ledgers AND by ``validate_phase_manifest`` after it
    reopens each record, so a manifest cannot relabel a scientifically failed case as completed,
    invent a different failure reason, relabel a diagnostic failure as a diagnostic success, or
    relabel an adjudicative failure as a diagnostic. Phase-level forcing, resolution and candidate
    gates are aggregate controls and are deliberately NOT evaluated here.

    It returns BOTH the case validity and the EFFECT appropriate to the row's frozen scientific
    role. A non-adjudicative diagnostic never stops a phase, whether or not the diagnostic itself
    is valid: PE-65 says it may alter nothing, and terminating the phase is an alteration.
    """
    role = row_scientific_role(row)
    spec = ROW_SCIENTIFIC_ROLES[role]
    verdict = _case_validity(scientific, execution_status)
    verdict["scientific_role"] = role
    verdict["adjudicative"] = spec["adjudicative"]
    verdict["enters_aggregate_truth"] = spec["enters_aggregate_truth"]
    if verdict["pass"]:
        verdict["effect"] = "NONE"
        verdict["ledger"] = spec["ledger_on_pass"]
    else:
        verdict["effect"] = spec["failure_effect"]
        verdict["ledger"] = spec["ledger_on_fail"]
    return verdict


def _case_validity(scientific, execution_status):
    """Pure case VALIDITY, independent of the row's role. The role decides the effect."""
    sci = scientific or {}
    if execution_status == "NORMAL_UNCONVERGED":
        return {"pass": False, "reason": "NORMAL_UNCONVERGED", "applicability": "always"}
    if execution_status == "FIXED_STEP_AUDIT_INCOMPLETE":
        return {"pass": False, "reason": "FIXED_STEP_AUDIT_INCOMPLETE", "applicability": "audit"}
    mach = sci.get("mach") or {}
    if mach and not mach.get("pass"):
        return {"pass": False, "reason": "LOW_MACH_FAILED", "applicability": "every solved case"}
    cons = sci.get("conservation")
    if cons and not cons.get("mass_conservation_pass"):
        return {"pass": False, "reason": "MASS_CONSERVATION_FAILED",
                "applicability": "fixture cases"}
    tc = sci.get("transverse_conservation")
    if tc and tc.get("pass") is False:
        return {"pass": False, "reason": "TRANSVERSE_CONTROL_FAILED",
                "applicability": "bridge-carrying cases"}
    lp = sci.get("lateral_pressure")
    if lp:
        if lp.get("masks_pair_exactly") is False:
            return {"pass": False, "reason": "PRESSURE_FACES_DO_NOT_PAIR",
                    "applicability": "bridge-carrying cases"}
        # Erratum PE-61: the case-level screen consumes the POINT estimate, which may only
        # REJECT. The final admission verdict is the paired normal/audit upper bound and is
        # formed at P1b/P2b, never here — a case record has no access to its own audit.
        if lp.get("measured_zero_driver_point_pass") is False:
            return {"pass": False, "reason": "MEASURED_LATERAL_DRIVER_NONZERO",
                    "applicability": "expected-zero-driver cases"}
    no = sci.get("node_offsets")
    if no is not None and not no.get("all_finite"):
        return {"pass": False, "reason": "NODE_OFFSET_SUMMARY_INCOMPLETE",
                "applicability": "fixture cases"}
    return {"pass": True, "reason": None,
            "applicability": "case-level execution validity"}


#: The five frozen phase ledgers (erratum PE-79). ``diagnostic_completed`` and
#: ``diagnostic_failed`` hold NON-ADJUDICATIVE rows only, so a failed diagnostic is never
#: disguised as a scientifically completed case and never stops the phase.
PHASE_LEDGERS = ("completed", "failed", "diagnostic_completed", "diagnostic_failed", "refused")
EXECUTED_LEDGERS = ("completed", "failed", "diagnostic_completed", "diagnostic_failed")


def make_phase_manifest(phase, universe_rows, eligible_rows, completed, refused, failed,
                        authority, predecessor_manifests, adaptive, terminal_status,
                        terminal_stop_reason=None, provenance_mode="PRODUCTION",
                        replicates=(), phase_science=None, execution_counts=None,
                        diagnostic_completed=(), diagnostic_failed=(),
                        phase_authority_file_sha256=None):
    """A validated phase LEDGER over the FULL phase universe.

    ``phase_science`` carries the phase's durable AGGREGATE scientific verdict (erratum PE-64).
    For P0 it is :func:`p0_aggregate_science`, and the validator recomputes it from the records
    rather than taking the manifest's word for it.

    ``execution_counts`` carries the resume accounting (erratum PE-74): newly executed rows,
    reused rows, provider calls, completed, failed and refused. A resumed phase may have FEWER
    provider calls than completed rows, and ``n_provider_calls`` must equal ``n_newly_executed``.

    ``diagnostic_completed`` / ``diagnostic_failed`` are the NON-ADJUDICATIVE ledgers (erratum
    PE-79). The five ledgers together must be an exact, pairwise-disjoint partition of the full
    phase universe, and a phase carrying only diagnostic failures may still terminate
    ``PHASE_COMPLETE``.
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
        "backend": authority["backend"],
        # erratum PE-93: the COMPLETE canonical authority, not only its hash. Every convenience
        # field above and below must equal this object exactly.
        "execution_authority": dict(authority),
        "execution_authority_sha256": execution_authority_sha256(authority),
        # erratum PE-105: the artifact written BEFORE the first provider call
        "phase_authority_path": phase_authority_filename(phase),
        "phase_authority_file_sha256": phase_authority_file_sha256,
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
        # erratum PE-79: diagnostic rows have their OWN ledgers. A diagnostic failure is retained
        # prominently and does not stop the phase.
        "diagnostic_completed": [dict(c) for c in diagnostic_completed],
        "diagnostic_failed": [dict(c) for c in diagnostic_failed],
        "ledger_names": list(PHASE_LEDGERS),
        "row_scientific_roles": {r["case_id"]: row_scientific_role(r) for r in uni},
        "replicates": [dict(r) for r in replicates],
        "adaptive": dict(adaptive),
        "execution_counts": (None if execution_counts is None else dict(execution_counts)),
        "phase_science": (None if phase_science is None else dict(phase_science)),
        "phase_science_sha256": (None if phase_science is None else record_hash(phase_science)),
        "terminal_status": terminal_status,
        "terminal_stop_reason": terminal_stop_reason,
        "counts": {"universe": len(uni), "eligible": len(elig), "completed": len(completed),
                   "refused": len(refused), "failed": len(failed),
                   "diagnostic_completed": len(diagnostic_completed),
                   "diagnostic_failed": len(diagnostic_failed)},
        # erratum PE-100: each list is formed from the EXACT role. C6 built the
        # decision-bearing list by excluding tau, so the execution-assurance replicates landed
        # in a field named decision-bearing while role-resolved reporting counted them apart.
        "decision_bearing_case_ids": [r["case_id"] for r in uni
                                      if row_scientific_role(r) == "DECISION_BEARING"],
        "execution_assurance_case_ids": [r["case_id"] for r in uni
                                         if row_scientific_role(r) ==
                                         "EXECUTION_ASSURANCE_REPLICATE"],
        "diagnostic_case_ids": [r["case_id"] for r in uni
                                if row_scientific_role(r) ==
                                "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"],
        "adjudicative_case_ids": [r["case_id"] for r in uni
                                  if ROW_SCIENTIFIC_ROLES[row_scientific_role(r)][
                                      "adjudicative"]],
    }
    doc.update(config_hashes())
    return doc


#: Phases that must publish a durable AGGREGATE scientific verdict (erratum PE-64). The validator
#: recomputes each from the reopened records; a later phase refuses on anything but a complete,
#: passing verdict.
PHASE_AGGREGATE_SCIENCE = {"P0": lambda recs: p0_aggregate_science(recs)}


def validate_predecessor_identity(phase, runs_dir, doc):
    """The EXACT predecessor-manifest identity of one phase (errata PE-107, PE-108).

    Requires the exact ``PHASE_PREREQUISITES[phase]`` key set, each cited manifest to exist, and
    each file to rehash exactly. P0 must carry the exact empty map. Extra, missing, stale and
    duplicate identities are each refused, and this runs on EVERY manifest validation — not only
    when a later phase happens to ask.
    """
    base = pathlib.Path(runs_dir)
    cited = doc.get("predecessor_manifests")
    if not isinstance(cited, dict):
        raise ManifestMissing("the %s manifest carries no predecessor-manifest map" % (phase,))
    want_keys = set(PHASE_PREREQUISITES[phase])
    if set(cited) != want_keys:
        raise ManifestMissing(
            "the %s manifest cites predecessor manifests %r; the exact required set is %r "
            "(erratum PE-107)" % (phase, sorted(cited), sorted(want_keys)))
    out = {}
    for k in sorted(cited):
        f = base / ("manifest_%s.json" % k)
        if not f.exists():
            raise ManifestMissing("the %s manifest cites a missing predecessor %s" % (phase, k))
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        if cited[k] != actual:
            raise ManifestMissing(
                "the %s manifest cites predecessor %s hash %r; the file hashes to %r "
                "(erratum PE-107)" % (phase, k, cited[k], actual))
        out[k] = actual
    return out


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
    if doc.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ManifestMissing("the %s manifest declares schema version %r, expected %r"
                              % (phase, doc.get("schema_version"), MANIFEST_SCHEMA_VERSION))
    # ---- errata PE-93, PE-95, PE-96: ALWAYS load and independently validate the embedded
    # complete historical authority. ``authority=None`` no longer means "skip"; an external
    # authority only STRENGTHENS the check, for exact same-phase resume.
    try:
        phase_authority = validate_execution_authority(
            doc.get("execution_authority"), expected_stage=phase,
            expected_current_authority=authority,
            require_production=require_production)
    except ExecutionAuthorityError as exc:
        raise ManifestMissing("the %s manifest's execution authority is invalid: %s"
                              % (phase, exc))
    if doc.get("execution_authority_sha256") != execution_authority_sha256(phase_authority):
        raise ManifestMissing("the %s manifest cites a stale execution-authority hash" % (phase,))
    # erratum PE-105: the separate artifact holding the authority's PREIMAGE is reopened,
    # rehashed and required to carry the identical authority.
    if doc.get("phase_authority_path") != phase_authority_filename(phase):
        raise ManifestMissing("the %s manifest names the wrong phase-authority artifact"
                              % (phase,))
    pa_doc, _pa_path, pa_sha = read_phase_authority(base, phase)
    if doc.get("phase_authority_file_sha256") != pa_sha:
        raise ManifestMissing(
            "the %s manifest cites phase-authority file hash %r; the artifact hashes to %r "
            "(erratum PE-105)" % (phase, doc.get("phase_authority_file_sha256"), pa_sha))
    validate_phase_authority_document(pa_doc, phase, require_production=require_production)
    if record_hash(pa_doc["execution_authority"]) != execution_authority_sha256(phase_authority):
        raise ManifestMissing(
            "the %s phase-authority artifact and the manifest's embedded authority differ; the "
            "two copies may never drift (erratum PE-105)" % (phase,))

    # ---- errata PE-107/PE-108: the predecessor identity is INTRINSIC to this validator -------
    # C7 compared predecessor manifest files only in require_phase_manifests, so validating a
    # phase in isolation established nothing about its predecessors and the P2b recursive walk
    # inherited that gap for the internal P0->P1a->P1b->P2a chain.
    expected_predecessors = validate_predecessor_identity(phase, base, doc)
    if dict(pa_doc["predecessor_manifest_sha256"]) != dict(expected_predecessors):
        raise ManifestMissing(
            "the %s phase-authority artifact cites predecessor manifests that differ from the "
            "manifest's (erratum PE-107)" % (phase,))
    for k in ("source_commit", "source_tree", "backend", "correction_version"):
        if doc.get(k) != phase_authority[k]:
            raise ManifestMissing(
                "the %s manifest's %r does not equal its own embedded authority (erratum PE-93)"
                % (phase, k))
    # from here on the PHASE authority is the one every record is bound to
    authority = phase_authority
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
    # erratum PE-79: FIVE ledgers, and the partition must be exact and pairwise disjoint over all
    # five. A failed diagnostic lives in its own ledger and is never disguised as a completed case.
    ledger_lists = {name: doc.get(name, []) for name in PHASE_LEDGERS}
    ledgers = {name: {c["case_id"]: c for c in seq} for name, seq in ledger_lists.items()}
    for name in PHASE_LEDGERS:
        if len(ledger_lists[name]) != len(ledgers[name]):
            raise ManifestMissing("the %s manifest lists a %s case twice" % (phase, name))
    completed, failed, refused = ledgers["completed"], ledgers["failed"], ledgers["refused"]
    diag_ok, diag_bad = ledgers["diagnostic_completed"], ledgers["diagnostic_failed"]
    names = list(PHASE_LEDGERS)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = set(ledgers[a]) & set(ledgers[b])
            if both:
                raise ManifestMissing("the %s manifest places %r in both %s and %s"
                                      % (phase, sorted(both)[:5], a, b))
    union = set().union(*(set(ledgers[n]) for n in names))
    extra = sorted(union - set(by_row))
    if extra:
        raise ManifestMissing("the %s manifest carries cases outside its phase universe: %r"
                              % (phase, extra[:5]))
    missing = sorted(set(by_row) - union)
    if missing:
        raise ManifestMissing("the %s manifest leaves %d universe rows unaccounted for: %r"
                              % (phase, len(missing), missing[:5]))
    # a diagnostic ledger may hold NON-ADJUDICATIVE rows only, and an adjudicative row may never
    # be filed as a diagnostic
    for name in ("diagnostic_completed", "diagnostic_failed"):
        for cid in ledgers[name]:
            role = row_scientific_role(by_row[cid])
            if ROW_SCIENTIFIC_ROLES[role]["adjudicative"]:
                raise ManifestMissing(
                    "case %r carries the adjudicative role %r but is filed in %s; an adjudicative "
                    "failure may never be relabelled a diagnostic (erratum PE-79)"
                    % (cid, role, name))
    for name in ("completed", "failed"):
        for cid in ledgers[name]:
            role = row_scientific_role(by_row[cid])
            if not ROW_SCIENTIFIC_ROLES[role]["adjudicative"]:
                raise ManifestMissing(
                    "case %r carries the non-adjudicative role %r but is filed in %s; it belongs "
                    "in a diagnostic ledger (erratum PE-79)" % (cid, role, name))
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
    executed_ids = set().union(*(set(ledgers[n]) for n in EXECUTED_LEDGERS))
    for cid in executed_ids:
        if cid not in elig_ids:
            raise ManifestMissing("case %r was executed although the derived plan excludes it"
                                  % (cid,))

    records, diagnostic_records, diagnostic_failures, seen_hash = {}, {}, {}, {}
    for cid in sorted(executed_ids):
        entry = next(ledgers[n][cid] for n in EXECUTED_LEDGERS if cid in ledgers[n])
        # PE-92: a diagnostic_failed entry may cite EITHER a normal record whose role-aware
        # verdict failed OR a diagnostic-attempt failure envelope. It must say which.
        kind_cited = entry.get("artifact_kind", "CASE_RECORD")
        if kind_cited not in ("CASE_RECORD", "DIAGNOSTIC_FAILURE_ENVELOPE"):
            raise ManifestMissing("case %r cites an unknown artifact kind %r"
                                  % (cid, kind_cited))
        has_rec, has_env = assert_no_coexisting_artifacts(base, cid)
        if kind_cited == "DIAGNOSTIC_FAILURE_ENVELOPE":
            if cid not in ledgers["diagnostic_failed"]:
                raise ManifestMissing(
                    "case %r cites a diagnostic-attempt failure envelope but is filed in %s; an "
                    "envelope may only appear in diagnostic_failed (erratum PE-92)"
                    % (cid, next(n for n in EXECUTED_LEDGERS if cid in ledgers[n])))
            role = row_scientific_role(by_row[cid])
            if role not in DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES:
                raise ManifestMissing(
                    "case %r carries the role %r; a diagnostic-attempt failure envelope may "
                    "never stand for an adjudicative row (erratum PE-89)" % (cid, role))
            env, epath = read_diagnostic_failure_envelope(base, cid)
            raw = pathlib.Path(epath).read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            if entry.get("record_sha256") != actual:
                raise ManifestMissing(
                    "the %s manifest cites envelope hash %r for %r; the file hashes to %r"
                    % (phase, entry.get("record_sha256"), cid, actual))
            if raw.decode() != canonical_json(env) + "\n":
                raise ManifestMissing("diagnostic envelope %r is not canonically serialised"
                                      % (cid,))
            validate_diagnostic_failure_envelope(
                env, row=by_row[cid], authority=phase_authority, phase=phase,
                provenance_mode=doc.get("provenance_mode"),
                expected_predecessors=expected_predecessors,
                phase_authority_file_sha256=pa_sha)
            if entry.get("row_sha256") != row_sha256(by_row[cid]):
                raise ManifestMissing("the %s manifest cites the wrong row hash for %r"
                                      % (phase, cid))
            if entry.get("reason") != env["failure_code"]:
                raise ManifestMissing(
                    "case %r records failure code %r; the envelope carries %r"
                    % (cid, entry.get("reason"), env["failure_code"]))
            if entry.get("failure_stage") != env["failure_stage"]:
                raise ManifestMissing("case %r records the wrong failure stage" % (cid,))
            # kept OUT of _records, out of _diagnostic_records and out of every downstream use
            diagnostic_failures[cid] = env
            continue
        if has_env:                                       # pragma: no cover - guarded above
            raise ManifestMissing("case %r cites a case record while an envelope exists" % (cid,))
        rec, path = read_case_record(base, cid)
        raw = pathlib.Path(path).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if entry.get("record_sha256") != actual:
            raise ManifestMissing("the %s manifest cites record hash %r for %r; the file hashes "
                                  "to %r" % (phase, entry.get("record_sha256"), cid, actual))
        if raw.decode() != canonical_json(rec) + "\n":
            raise ManifestMissing("case record %r is not canonically serialised" % (cid,))
        validate_case_record(rec, row=by_row[cid], authority=phase_authority, phase=phase,
                             expected_predecessors=expected_predecessors,
                             phase_authority_file_sha256=pa_sha)
        # erratum PE-110 §8.4: the geometry identity is RECOMPUTED from the canonical row, for
        # normal records as well as envelopes, at FINAL validation and not only on resume.
        want_geom = row_geometry_identity(by_row[cid])
        got_geom = rec.get("geometry") or {}
        for gk in ("kind", "mask_sha256", "S", "bridge", "state", "variant", "obstructed"):
            if got_geom.get(gk) != want_geom[gk]:
                raise ManifestMissing(
                    "case record %r records geometry %s=%r; its canonical row resolves to %r "
                    "(erratum PE-110)" % (cid, gk, got_geom.get(gk), want_geom[gk]))
        if rec.get("mask_sha256") != want_geom["mask_sha256"]:
            raise ManifestMissing("case record %r records a mask its row does not resolve to"
                                  % (cid,))
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
        # errata PE-58, PE-79: recompute the ROLE-AWARE verdict and require the ledger the
        # manifest filed the case under to be exactly the one the verdict names.
        verdict = case_decision_verdict(by_row[cid], rec.get("scientific"), rec["status"])
        want_ledger = verdict["ledger"]
        got_ledger = next(n for n in EXECUTED_LEDGERS if cid in ledgers[n])
        if got_ledger != want_ledger:
            raise ManifestMissing(
                "case %r is filed in %s but recomputes as %s (%s); a manifest may not relabel a "
                "failed case, invent a failure, or move a case between the adjudicative and "
                "diagnostic ledgers (errata PE-58, PE-79)"
                % (cid, got_ledger, want_ledger, verdict["reason"]))
        if not verdict["pass"] and entry.get("reason") != verdict["reason"]:
            raise ManifestMissing(
                "case %r records failure reason %r; it recomputes as %r"
                % (cid, entry.get("reason"), verdict["reason"]))
        # PE-79/PE-81: a NON-ADJUDICATIVE record never enters the record set the aggregate
        # science, the candidate gates and every downstream phase consume. Adjudicative rows —
        # decision-bearing and execution-assurance replicates alike — are unchanged from C5.
        if verdict["pass"]:
            (records if verdict["adjudicative"] else diagnostic_records)[cid] = rec

    if doc.get("terminal_status") not in TERMINAL_PHASE_STATUSES:
        raise ManifestMissing("the %s manifest has no valid terminal status" % (phase,))
    # PE-74: the resume accounting must be present and must reconcile
    ec = doc.get("execution_counts")
    if ec is None:
        raise ManifestMissing("the %s manifest carries no execution accounting (erratum PE-74)"
                              % (phase,))
    missing_counts = [k for k in EXECUTION_COUNT_FIELDS if k not in ec]
    if missing_counts:
        raise ManifestMissing("the %s manifest's execution accounting is missing %r"
                              % (phase, missing_counts))
    # PE-74/PE-92: every provider call constructs exactly ONE new artifact -- a case record, or
    # (for the non-adjudicative tau role only) a diagnostic-attempt failure envelope.
    if ec["n_newly_executed"] != (ec["n_new_case_records"]
                                  + ec["n_new_diagnostic_failure_envelopes"]):
        raise ManifestMissing(
            "the %s manifest's n_newly_executed is not the sum of its new case records and new "
            "diagnostic envelopes (erratum PE-92)" % (phase,))
    if ec["n_reused"] != (ec["n_reused_case_records"]
                          + ec["n_reused_diagnostic_failure_envelopes"]):
        raise ManifestMissing(
            "the %s manifest's n_reused is not the sum of its reused case records and reused "
            "diagnostic envelopes (erratum PE-92)" % (phase,))
    if ec["n_provider_calls"] != ec["n_newly_executed"]:
        raise ManifestMissing(
            "the %s manifest reports %d provider calls for %d newly persisted artifacts; a "
            "provider call may only ever construct a NEW artifact (errata PE-74, PE-92)"
            % (phase, ec["n_provider_calls"], ec["n_newly_executed"]))
    if ec["n_newly_executed"] + ec["n_reused"] != len(executed_ids):
        raise ManifestMissing(
            "the %s manifest's newly-executed plus reused rows do not reconcile to its executed "
            "ledgers" % (phase,))
    if (ec["n_completed"], ec["n_failed"], ec["n_refused"], ec["n_diagnostic_completed"],
            ec["n_diagnostic_failed"]) != (len(completed), len(failed), len(refused),
                                           len(diag_ok), len(diag_bad)):
        raise ManifestMissing("the %s manifest's execution accounting does not reconcile to its "
                              "five ledgers" % (phase,))
    counts = doc.get("counts") or {}
    if (counts.get("universe") != len(uni) or counts.get("completed") != len(completed)
            or counts.get("refused") != len(refused) or counts.get("failed") != len(failed)
            or counts.get("diagnostic_completed") != len(diag_ok)
            or counts.get("diagnostic_failed") != len(diag_bad)):
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
    doc["_diagnostic_records"] = diagnostic_records
    doc["_diagnostic_failures"] = diagnostic_failures
    doc["_execution_authority"] = phase_authority
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

    # erratum PE-105 §10.7: the P2b phase-authority artifact is reopened and validated first
    if doc.get("phase_authority_path") != phase_authority_filename("P2b"):
        raise ManifestMissing("the P2b manifest names the wrong phase-authority artifact")
    p2b_pa, _p2b_path, p2b_pa_sha = read_phase_authority(base, "P2b")
    if doc.get("phase_authority_file_sha256") != p2b_pa_sha:
        raise ManifestMissing("the P2b manifest cites a stale phase-authority file hash")
    validate_phase_authority_document(p2b_pa, "P2b", require_production=require_production)
    # the assembly authority is load-bearing, not an unused parameter (erratum PE-73)
    doc["_assembly_authority"] = validate_p2b_assembly_authority(
        doc.get("assembly_authority"), base, require_production=require_production,
        expected_assembly_authority_sha256=expected_assembly_authority_sha256)
    if doc.get("assembly_authority_sha256") != doc["_assembly_authority"][
            "assembly_authority_sha256"]:
        raise ManifestMissing("the P2b manifest cites a stale assembly-authority hash")

    # ---- erratum PE-82: INDEPENDENTLY rebuild the scientific endpoint ---------------------
    # C5 compared the persisted ledger against the manifest's own record of its hash, which is a
    # self-consistency check: a coordinated edit that also updated the outer hashes passed. The
    # SAME pure builder now reconstructs the decision from the reopened predecessor records, and
    # every persisted artifact is compared against that reconstruction field by field.
    expected = build_p2b_decision_payload(pre_docs, pre_records, doc["_assembly_authority"],
                                          provenance_mode=doc.get("provenance_mode"))
    doc["_expected_payload"] = expected
    if doc.get("scientific_decision_payload_sha256") != expected[
            "scientific_decision_payload_sha256"]:
        raise ManifestMissing(
            "the P2b manifest's scientific decision does not recompute from its own validated "
            "predecessor records: persisted %r, rebuilt %r (erratum PE-82)"
            % (doc.get("scientific_decision_payload_sha256"),
               expected["scientific_decision_payload_sha256"]))

    ledger_path = base / "candidate_ledger.json"
    if not ledger_path.exists():
        raise ManifestMissing("P2b wrote no candidate ledger")
    ledger = json.loads(ledger_path.read_text())
    if doc.get("candidate_ledger_sha256") != record_hash(ledger):
        raise ManifestMissing("the P2b manifest cites a different candidate ledger")
    # ... and the ledger's SCIENCE must equal the rebuilt science, not merely its own hash
    if ledger.get("scientific_decision_payload_sha256") != expected[
            "scientific_decision_payload_sha256"]:
        raise ManifestMissing("the candidate ledger cites a different scientific decision")
    got_ledger = _scientific_subset(ledger, P2B_LEDGER_SCIENTIFIC_KEYS, "candidate ledger")
    if record_hash(got_ledger) != record_hash(expected["candidate_ledger"]):
        bad = sorted(k for k in P2B_LEDGER_SCIENTIFIC_KEYS
                     if record_hash(got_ledger[k]) != record_hash(
                         expected["candidate_ledger"][k]))
        raise ManifestMissing(
            "the persisted candidate ledger does not recompute from the validated predecessor "
            "records; differing scientific field(s): %r (erratum PE-83)" % (bad,))
    got_manifest = _scientific_subset(doc, P2B_MANIFEST_SCIENTIFIC_KEYS, "P2b manifest")
    if record_hash(got_manifest) != record_hash(expected["manifest"]):
        bad = sorted(k for k in P2B_MANIFEST_SCIENTIFIC_KEYS
                     if got_manifest[k] != expected["manifest"][k])
        raise ManifestMissing(
            "the persisted P2b manifest's decision does not recompute; differing field(s): %r "
            "(erratum PE-84)" % (bad,))
    if doc.get("n_declared_candidates") != ledger.get("n_declared"):
        raise ManifestMissing("the P2b manifest and its ledger disagree on the candidate count")
    if doc.get("n_eligible_candidates") != ledger.get("n_eligible"):
        raise ManifestMissing("the P2b manifest and its ledger disagree on the eligible count")
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
        # erratum PE-84: the design-block endpoint is REBUILT, so the exact reason and the
        # absence of both artifacts are properties of the records, not of the persisted file.
        if expected["manifest"]["selection_status"] != "DESIGN_BLOCKED":
            raise ManifestMissing(
                "the persisted P2b reports DESIGN_BLOCKED but the records recompute as %r"
                % (expected["manifest"]["selection_status"],))
        if doc.get("terminal_stop_reason") != expected["manifest"]["terminal_stop_reason"]:
            raise ManifestMissing(
                "the persisted design-block reason %r does not recompute; the records give %r"
                % (doc.get("terminal_stop_reason"),
                   expected["manifest"]["terminal_stop_reason"]))
        if expected["proposed_freeze"] is not None or expected["instantiated_matrix"] is not None:
            raise ManifestMissing(                       # pragma: no cover - guarded above
                "a design-blocked rebuild produced a freeze or an instantiated matrix")
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
    # erratum PE-84: the SELECTED endpoint is rebuilt too — the exact candidates, slot
    # assignment, categories, order, target provenance, Xi envelopes, evidence sets and the
    # instantiated rows all come from the records, not from the persisted files.
    if expected["proposed_freeze"] is None:
        raise ManifestMissing(
            "the persisted P2b reports SELECTED but the records recompute as %r"
            % (expected["manifest"]["selection_status"],))
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
    for name, persisted, keys, want in (
            ("proposed freeze", freeze, P2B_FREEZE_SCIENTIFIC_KEYS, expected["proposed_freeze"]),
            ("instantiated matrix", inst, P2B_INSTANTIATED_SCIENTIFIC_KEYS,
             expected["instantiated_matrix"])):
        if persisted.get("scientific_decision_payload_sha256") != expected[
                "scientific_decision_payload_sha256"]:
            raise ManifestMissing("the %s cites a different scientific decision" % name)
        got = _scientific_subset(persisted, keys, name)
        if record_hash(got) != record_hash(want):
            bad = sorted(k for k in keys if record_hash(got[k]) != record_hash(want[k]))
            raise ManifestMissing(
                "the persisted %s does not recompute from the validated predecessor records; "
                "differing scientific field(s): %r (erratum PE-84)" % (name, bad))

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
        # erratum PE-95: each predecessor is validated against its OWN persisted historical
        # authority. Pushing the CURRENT phase's authority at an earlier phase would assert that
        # the later commit produced the earlier record, which rewrites execution history.
        doc = validate_phase_manifest(pre, base, authority=None, matrix_rows=rows,
                                      predecessor_records=dict(records),
                                      require_production=require_production)
        # PE-27: a stopped, failed, unconverged, invalid or design-blocked predecessor may NOT
        # satisfy the next phase. The superseded check never looked at terminal_status at all.
        if doc.get("terminal_status") != "PHASE_COMPLETE":
            raise ManifestMissing(
                "the %s manifest terminated %r; a phase may consume a predecessor only at "
                "PHASE_COMPLETE (erratum PE-27)" % (pre, doc.get("terminal_status")))
        # erratum PE-107: validate_phase_manifest has ALREADY established this phase's exact
        # predecessor identity. One implementation, not two that can drift.
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
        # where the programme requires the phases to share a reviewed source identity, compare
        # those EXPLICIT common fields AFTER each historical authority has validated on its own.
        pre_auth = doc["_execution_authority"]
        if authority is not None:
            for k in ("source_commit", "source_tree", "correction_version", "backend"):
                if pre_auth[k] != authority[k]:
                    raise ManifestMissing(
                        "the %s authority's %r (%r) differs from the %r authority's (%r); a "
                        "phase may consume only a predecessor sharing its reviewed source "
                        "identity (erratum PE-95)"
                        % (pre, k, pre_auth[k], phase, authority[k]))
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


#: The canonical MULTI-SOURCE fields every derived sample carries (erratum PE-85).
#:
#: C5 assumed one derived sample had one source, and put a second source in ad-hoc keys outside
#: the generic schema — ``paired_blocked_*`` for ``R_identical``, ``area_*`` for actual ``Xi`` —
#: which the gates and the source-to-derived mapping never read. Downstream code must not have to
#: know that such a field exists.
SAMPLE_SOURCE_FIELDS = ("source_case_ids", "source_record_sha256", "source_roles")


def _sample(value, level, g, S, sources, definition=None, **extra):
    """One derived sample with its COMPLETE lineage.

    ``sources`` is an ordered sequence of ``(role, record)`` pairs. A direct single-record
    quantity carries one; ``R_identical`` carries ``open`` and ``blocked``; actual ``Xi`` carries
    ``bridge_coupon`` and ``candidate_blocked_area``.
    """
    ids = [r["case_id"] for _role, r in sources]
    hashes = [record_hash(r) for _role, r in sources]
    row = {
        "forcing_level": level, "g": g, "value": value, "S": S,
        "source_case_ids": assert_flat_id_list(ids, "sample source case ids"),
        "source_record_sha256": assert_flat_hash_list(hashes, "sample source hashes"),
        "source_roles": [role for role, _r in sources],
        # a CONVENIENCE primary, never the complete lineage
        "case_id": ids[0], "record_sha256": hashes[0],
    }
    if definition:
        row["quantity_definition"] = definition
    row.update(extra)
    return row


def _samples(records, kind, key, state, quantity, extractor, role=None):
    """NORMAL records only, grouped into a forcing ladder for one fixed configuration."""
    out = []
    for r in sorted(_normal_only(records, kind, key).values(), key=lambda x: x["case_id"]):
        if state is not None and r["row"]["state"] != state:
            continue
        v = extractor(r)
        if v is None:
            continue
        out.append(_sample(v, r["row"]["forcing_level"], row_forcing(r["row"]), r["row"]["S"],
                           [(role or kind, r)]))
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


def _outlet_share(rec):
    """The exact frozen outlet share ``s = q1/(q1+q2)``, RECOMPUTED from the record's own lane
    fluxes rather than read from the stored scalar (erratum PE-62)."""
    sci = rec.get("scientific") or {}
    q1, q2 = sci.get("q1_volume"), sci.get("q2_volume")
    if q1 is None or q2 is None:
        return None
    tot = _finite(q1, "q1_volume") + _finite(q2, "q2_volume")
    if tot == 0.0:                                            # pragma: no cover - degenerate
        return None
    return float(q1) / tot


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
        "s_reference_blocked": _outlet_share,
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
                by_S[s["S"]] = _carry_sources(s)
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
                        by_S[s["S"]] = _carry_sources(s)
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
                _outlet_share) if s["S"] == S],
            "s_open": [s for s in _samples(
                records, "identical_path_control", key, "open", "s_open",
                _outlet_share) if s["S"] == S],
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
        # erratum PE-85: R = C_open / C_blocked, so BOTH records are its lineage, in the
        # generic schema rather than in an ad-hoc paired_blocked_* key.
        out.append(_sample(Co / Cb, level, row_forcing(states["open"]["row"]), S,
                           [("open", states["open"]), ("blocked", states["blocked"])],
                           definition="R_identical = C_open / C_blocked"))
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
        # erratum PE-86: Xi = G_bridge * (1/A1 + 1/A2), so the coupon AND the area record are
        # its lineage, in the generic schema rather than in an ad-hoc area_* key.
        out.append(_sample(
            float(gb) * inv, k2[1], row_forcing(r["row"]), k2[0],
            [("bridge_coupon", r), ("candidate_blocked_area", arec)],
            definition=ACTUAL_XI_DEFINITION,
            G_bridge_coupon=float(gb), A_series_inverse=inv,
            area_case_id=arec["case_id"], area_record_sha256=record_hash(arec)))
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
                got[r["row"]["S"]] = _carry_sources(
                    _sample(v, r["row"]["forcing_level"], row_forcing(r["row"]),
                            r["row"]["S"], [(kind, r)]))
        return got

    for q in ("c_field", "A1", "A2", "A_field", "A_series_inverse"):
        extra = ({"quantity_definition": AGGREGATE_AREA_DEFINITIONS[q]}
                 if q in AGGREGATE_AREA_DEFINITIONS else None)
        add(q, pick("candidate_blocked_mirror", "blocked",
                    lambda r, _q=q: _area_quantity(r, _q)), extra)
    add("C_blocked", pick("candidate_blocked_mirror", "blocked",
                          lambda r: (_conductance(r)
                                     if (r.get("scientific") or {}).get("dP") else None)))
    add("s_blocked", pick("identical_path_control", "blocked", _outlet_share))
    add("s_open", pick("identical_path_control", "open", _outlet_share))
    add("C_open", pick("identical_path_control", "open",
                       lambda r: (_conductance(r)
                                  if (r.get("scientific") or {}).get("dP") else None)))
    add("G_bridge_coupon", pick("bridge_coupon", None,
                                lambda r: (r.get("scientific") or {}).get("G_bridge_coupon")))
    r_by_S = {}
    for S in SCIENTIFIC_RESOLUTIONS:
        for s in _identical_R_samples(records, key, S):
            if s["forcing_level"] == "central":
                r_by_S[S] = _carry_sources(s)      # PE-85: open AND blocked
    add("R_identical", r_by_S,
        {"artifact_point_estimate_coverage": ARTIFACT_POINT_ESTIMATE_COVERAGE})
    xi_by_S = {}
    for s in actual_xi_samples(records, key):
        if s["forcing_level"] == "central":
            xi_by_S[s["S"]] = _carry_sources(s)    # PE-86: coupon AND area
    if S_COARSE in xi_by_S and S_FINE in xi_by_S:
        g = resolution_consistency_gate("Xi_actual", xi_by_S[S_COARSE], xi_by_S[S_FINE], bridge)
        g["quantity_definition"] = ACTUAL_XI_DEFINITION
        # retained under their C5 names AND now present in the generic multi-source schema
        g["area_case_ids"] = [xi_by_S[S]["area_case_id"] for S in (S_COARSE, S_FINE)]
        g["area_record_sha256"] = assert_flat_hash_list(
            [xi_by_S[S]["area_record_sha256"] for S in (S_COARSE, S_FINE)],
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
#:
#: Erratum PE-81: ``tau_cross_check`` is REMOVED. A row that PE-65 says may alter nothing must
#: not sit in the structure every candidate cites as shared scientific truth. Its records move to
#: ``diagnostic_evidence["tau_plus_1p2"]``.
COMMON_REFERENCE_KINDS = ("reference_blocked_ladder", "axial_coupon")
#: Kinds whose records are NON-ADJUDICATIVE diagnostics, bound separately and never as truth.
DIAGNOSTIC_EVIDENCE_KINDS = ("tau_cross_check",)


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
        "excludes": ("non-adjudicative diagnostics. tau_plus = 1.2 records are bound in "
                     "diagnostic_evidence and are NOT common scientific truth (erratum PE-81)"),
    }


def diagnostic_evidence(records):
    """NON-ADJUDICATIVE diagnostic records, bound separately from scientific truth (PE-81).

    C5 placed the ``tau_plus = 1.2`` records in ``common_reference_evidence`` — the structure
    every candidate cites as shared truth — while PE-65 says those rows may alter nothing. They
    are bound here instead, with an explicit declaration of what they may and may not do, so a
    reader and a validator can both see that nothing downstream consumes them.
    """
    tau = {"case_ids": [], "record_sha256": [], "records": {}}
    for cid, r in sorted(records.items()):
        if r.get("kind") not in DIAGNOSTIC_EVIDENCE_KINDS:
            continue
        sci = r.get("scientific") or {}
        tau["case_ids"].append(cid)
        tau["record_sha256"].append(record_hash(r))
        tau["records"][cid] = {
            "S": r["row"]["S"], "tau_plus": r["row"]["tau_plus"],
            "run_status": r.get("status"),
            "converged": r.get("status") == "NORMAL_CONVERGED",
            "max_mach": (sci.get("mach") or {}).get("max_mach"),
            "mach_pass": (sci.get("mach") or {}).get("pass"),
            "mass_conservation_pass": (sci.get("conservation") or {}).get(
                "mass_conservation_pass"),
            "Q_volume": sci.get("Q_volume"), "dP": sci.get("dP"),
            "case_validity": _case_validity(sci, r.get("status")),
        }
    tau["case_ids"] = assert_flat_id_list(sorted(tau["case_ids"]), "tau diagnostic case ids")
    tau["record_sha256"] = assert_flat_hash_list(sorted(set(tau["record_sha256"])),
                                                 "tau diagnostic hashes")
    tau["n_records"] = len(tau["case_ids"])
    tau["scientific_role"] = "TAU_RELAXATION_DIAGNOSTIC_NON_ADJUDICATIVE"
    tau["disposition"] = dict(TAU_CROSS_CHECK_DISPOSITION)
    tau["declaration"] = (
        "NON-ADJUDICATIVE. These records may report completion, convergence, Mach, conservation "
        "and the compact observables, as qualitative comparison metadata only. They enter NO P0 "
        "aggregate truth, NO reference conductance, outlet share, contrast or area, NO forcing or "
        "resolution gate, NO uncertainty, NO candidate admission, NO candidate evidence, NO "
        "common_reference_evidence, NO P2b decision and NO disposition (errata PE-65, PE-81).")
    return {
        "tau_plus_1p2": tau,
        "role_names": ["tau_plus_1p2"],
        "rule": ("diagnostic evidence is bound separately from scientific truth and is consumed "
                 "by nothing downstream (erratum PE-81)"),
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
    # erratum PE-85/PE-86: the mapping is built from the COMPLETE multi-source gate fields, so
    # a gate on R carries its blocked partner and a gate on actual Xi carries its area record.
    forcing_h = _cited([h for g in forcing["gates"]
                        for h in (g.get("source_record_sha256") or g["record_sha256"])])
    res_h = _cited([h for g in resolution["gates"]
                    for h in (g.get("source_record_sha256") or g["record_sha256"])])
    forcing_by_quantity = {g["quantity"]: {
        "source_case_ids": list(g.get("source_case_ids") or g["case_ids"]),
        "source_record_sha256": list(g.get("source_record_sha256") or g["record_sha256"]),
        "source_roles": list(g.get("source_roles") or []),
    } for g in forcing["gates"]}
    resolution_by_quantity = {g["quantity"]: {
        "source_case_ids": list(g.get("source_case_ids") or g["case_ids"]),
        "source_record_sha256": list(g.get("source_record_sha256") or g["record_sha256"]),
        "source_roles": list(g.get("source_roles") or []),
    } for g in resolution["gates"]}
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
        "forcing_gates": {"record_sha256": forcing_h, "derived": ["forcing_invariance"],
                          "by_quantity": forcing_by_quantity},
        "resolution_gates": {"record_sha256": res_h, "derived": ["resolution_consistency"],
                             "by_quantity": resolution_by_quantity},
        "node_offset_summaries": {
            "record_sha256": [], "derived": ["u_pressure_plane_R"],
            "note": ("same-field summaries are bound through their OWNING record hashes, which "
                     "are the identical-path normals already listed under artifact_R")},
    }
    unbound = sorted(set(art_h + press_h + xi_h + c_h + forcing_h + res_h) - set(cs_h))
    common = {h for h in unbound}
    # erratum PE-85/PE-86: a record may be present in candidate_specific_record_sha256 and still
    # be MISSING from a particular source-to-derived mapping. Both conditions are checked, so a
    # broad evidence set cannot mask a defective detailed mapping.
    incomplete_maps = sorted(
        q for q, m in list(forcing_by_quantity.items()) + list(resolution_by_quantity.items())
        if len(m["source_record_sha256"]) != len(m["source_case_ids"])
        or not m["source_record_sha256"])
    return {
        "candidate_id": "w%d_kz%d" % key,
        "by_role": by_role,
        "candidate_specific_case_ids": cs_ids,
        "candidate_specific_record_sha256": cs_h,
        "common_reference_roles": sorted(
            {"reference_blocked_ladder", "axial_coupon"}) if common else [],
        "source_to_derived_quantity": mapping,
        "unbound_cited_hashes": unbound,
        "incomplete_source_mappings": incomplete_maps,
        "multi_source_quantities": sorted(
            q for q, m in list(forcing_by_quantity.items()) + list(resolution_by_quantity.items())
            if len(m["source_roles"]) > 1),
        "complete": bool(not unbound and not incomplete_maps),
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
    # errata PE-97/PE-98: the COMPLETE nested execution authority and its hash are load-bearing
    # identity and belong INSIDE the canonical set the assembly hash is taken over. C6 wrote
    # execution_authority_sha256 into the document and left it out of the hash, so changing it
    # did not change assembly_authority_sha256.
    "execution_authority", "execution_authority_sha256",
    # erratum PE-101 §10: the committed authorization snapshot is load-bearing here too, and
    # therefore inside assembly_authority_sha256.
    "source_authorization", "authority_provenance",
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
        "execution_authority": dict(execution_auth),
        "execution_authority_sha256": execution_authority_sha256(execution_auth),
        "source_authorization": dict(execution_auth["source_authorization"]),
        "authority_provenance": execution_auth["authority_provenance"],
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
    if require_production and not (doc.get("source_authorization") or {}).get(
            "stage_authorised"):
        raise ManifestMissing(
            "the P2b assembly authority records stage_authorised=%r; a production assembly may "
            "only stand on a commit whose AUTHORISED_ASSEMBLY_PHASES names P2b (erratum PE-101)"
            % ((doc.get("source_authorization") or {}).get("stage_authorised"),))
    if doc["backend"] not in SUPPORTED_BACKENDS:
        raise ManifestMissing("the assembly authority names an unsupported backend")
    if require_production and not doc["working_tree_clean"]:
        raise ManifestMissing("the assembly authority records a dirty working tree")
    # NOTE: the Git identity itself is established by validate_execution_authority below, from
    # the repository rather than from the string's shape (erratum PE-99).
    # NOTE: the assembly authority's three configuration hashes are those of the artifacts
    # COMMITTED at its own source commit, and validate_execution_authority establishes them
    # against that commit. Binding the CURRENT configuration is the P2b manifest's job and is
    # checked there; asserting it here would demand that a historical authority match a later
    # checkout, which is exactly the rewriting of execution history PE-95 forbids. (On a clean
    # production tree the committed and live hashes are identical by construction.)
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
    # errata PE-97/PE-98: validate the NESTED complete P2b execution authority independently,
    # against the recorded Git commit and tracked content, and require every duplicated outer
    # field to equal it.
    try:
        nested = validate_execution_authority(
            doc.get("execution_authority"), expected_stage="P2b",
            require_production=require_production)
    except ExecutionAuthorityError as exc:
        raise ManifestMissing("the P2b assembly authority's execution authority is invalid: %s"
                              % exc)
    if doc.get("execution_authority_sha256") != execution_authority_sha256(nested):
        raise ManifestMissing("the assembly authority cites a stale execution-authority hash")
    for k in ("source_commit", "source_tree", "working_tree_clean", "clean_tree_required",
              "correction_version", "backend", "dependencies", "protocol_config_sha256",
              "fixture_spec_sha256", "execution_matrix_sha256", "source_authorization",
              "authority_provenance"):
        if doc.get(k) != nested[k]:
            raise ManifestMissing(
                "the assembly authority's %r does not equal its own nested execution authority "
                "(erratum PE-98)" % (k,))
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
    # erratum PE-104: the assembly gate is applied HERE, at the public boundary, BEFORE any
    # record is validated, any authority is created or any artifact is written. C7 relied on the
    # driver's require_assembly_authorisation having been called by the caller, so a direct call
    # bypassed it entirely. One shared source-controlled gate, not two drifting copies.
    assert_stage_authorised("P2b")
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


#: The scientific keys of each persisted P2b artifact, i.e. exactly the fields the pure builder
#: reconstructs. Anything not listed is persistence metadata (erratum PE-84).
P2B_DECISION_PAYLOAD_SCHEMA_VERSION = 1
P2B_LEDGER_SCIENTIFIC_KEYS = ("candidates", "common_reference_evidence", "diagnostic_evidence",
                              "n_declared", "n_eligible")
P2B_FREEZE_SCIENTIFIC_KEYS = ("freeze_rule", "n_frozen_bridges", "frozen_bridges",
                              "common_reference_evidence", "above_window_diagnostics",
                              "rows_sha256", "status", "p3_p4_authorised")
P2B_INSTANTIATED_SCIENTIFIC_KEYS = ("rows", "n_rows", "rows_sha256")
P2B_MANIFEST_SCIENTIFIC_KEYS = ("selection_status", "terminal_status", "terminal_stop_reason",
                                "n_declared_candidates", "n_eligible_candidates")


def build_p2b_decision_payload(manifests, records, assembly_authority,
                               provenance_mode="PRODUCTION"):
    """The PURE P2b decision core, shared by the two wrappers with non-overlapping provenance.

    Recomputes, in order: lineage · forcing ladders · componentwise invariance · boundary
    stability · resolution consistency · zero-driver transverse · measured lateral pressure gap ·
    normal/audit pairing · artifact point estimates and uncertainty · complete candidate
    admission · candidate ``c`` intervals · actual-``Xi`` envelopes · reachable-set admission ·
    categories · the exact four-slot selection · the instantiated P3/P4 rows · the durable
    ledger, proposed freeze and P2b manifest. It performs **no solve**.
    """
    assembly_auth = dict(assembly_authority)

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

    # ---- the canonical SCIENTIFIC payload, from the records alone (errata PE-82 … PE-84) -----
    # Persistence metadata — file paths, file hashes, the manifests' own SHAs — is deliberately
    # OUTSIDE this payload: a scientific decision may not be authenticated by a hash of itself.
    stop_reason, freeze_sci, inst_sci = None, None, None
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
        inst_sci = {"rows": inst, "n_rows": len(inst), "rows_sha256": record_hash(inst)}
        freeze_sci = {
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
            "common_reference_evidence": common_reference_evidence(records),
            "above_window_diagnostics": above_window_diagnostics(admitted),
            "rows_sha256": inst_sci["rows_sha256"],
            "status": "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW",
            "p3_p4_authorised": False,
        }

    payload = {
        "schema_version": P2B_DECISION_PAYLOAD_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": "P2b",
        "provenance_mode": provenance_mode,
        "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
        "predecessor_phases": sorted(manifests),
        "candidate_ledger": {
            "candidates": ledger,
            "common_reference_evidence": common_reference_evidence(records),
            # erratum PE-81: bound SEPARATELY, consumed by nothing. Empty by construction,
            # because a non-adjudicative record never reaches the validated record set.
            "diagnostic_evidence": diagnostic_evidence(records),
            "n_declared": len(ledger),
            "n_eligible": len(admitted),
        },
        "proposed_freeze": freeze_sci,
        "instantiated_matrix": inst_sci,
        "manifest": {
            "selection_status": ("SELECTED" if selection is not None else "DESIGN_BLOCKED"),
            "terminal_status": ("PHASE_COMPLETE" if selection is not None
                                else "PHASE_STOPPED_DESIGN_BLOCKED"),
            "terminal_stop_reason": stop_reason,
            "n_declared_candidates": len(ledger),
            "n_eligible_candidates": len(admitted),
        },
        "rule": ("the deterministic scientific endpoint, rebuilt from the validated predecessor "
                 "records alone. It consumes no persisted candidate ledger, freeze or "
                 "instantiated matrix, accepts no caller-supplied verdict, selection or "
                 "uncertainty, performs no solve and writes no file (errata PE-82 … PE-84)."),
    }
    payload["scientific_decision_payload_sha256"] = record_hash(payload)
    return payload


def _scientific_subset(doc, keys, what):
    missing = [k for k in keys if k not in (doc or {})]
    if missing:
        raise ManifestMissing("the persisted %s is missing scientific field(s) %r" % (what,
                                                                                      missing))
    return {k: doc[k] for k in keys}


def _p2b_decision_core(base, auth, manifests, records, provenance_mode="PRODUCTION"):
    """PERSIST the pure scientific decision under one provenance (errata PE-82 … PE-84).

    The science lives in :func:`build_p2b_decision_payload` and nowhere else: this wrapper adds
    the source authority, the assembly authority, file paths and hashes, the provenance mode and
    the atomic no-overwrite / exact-match persistence, and nothing scientific.
    """
    base = pathlib.Path(base)
    assembly_auth = p2b_assembly_authority(base, auth, manifests,
                                           provenance_mode=provenance_mode)
    # erratum PE-105 §10.6: the P2b authority is persisted BEFORE any candidate ledger, freeze
    # or instantiated matrix, and an exact resume reopens and validates it first.
    pre_sha_p2b = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
                   for k in manifests}
    pa_doc = make_phase_authority_document("P2b", auth, pre_sha_p2b,
                                           provenance_mode=provenance_mode)
    pa_path, _pa_mode = write_phase_authority(base, pa_doc)
    pa_sha = hashlib.sha256(pa_path.read_bytes()).hexdigest()
    validate_phase_authority_document(
        pa_doc, "P2b", require_production=(provenance_mode == "PRODUCTION"),
        expected_current_authority=auth, expected_predecessors=pre_sha_p2b)
    payload = build_p2b_decision_payload(manifests, records, assembly_auth,
                                         provenance_mode=provenance_mode)
    sci_sha = payload["scientific_decision_payload_sha256"]
    pre_sha = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
               for k in manifests}

    ledger_doc = dict(payload["candidate_ledger"])
    ledger_doc.update({
        "tranche": TRANCHE_ID, "correction_version": CORRECTION_VERSION, "phase": "P2b",
        "provenance_mode": provenance_mode,
        "scientific_decision_payload_sha256": sci_sha,
        "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
        "execution_authority_sha256": record_hash(auth),
        "assembly_authority": dict(assembly_auth),
        "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
    })
    ledger_doc.update(config_hashes())
    written = {}
    written["candidate_ledger.json"] = _atomic_write_json(base / "candidate_ledger.json",
                                                          ledger_doc)[0].name

    freeze_doc, inst_file_sha = None, None
    if payload["instantiated_matrix"] is not None:
        inst_doc = dict(payload["instantiated_matrix"])
        inst_doc.update({"schema_version": 1, "tranche": TRANCHE_ID,
                         "correction_version": CORRECTION_VERSION,
                         "provenance_mode": provenance_mode,
                         "scientific_decision_payload_sha256": sci_sha,
                         "assembly_authority_sha256":
                             assembly_auth["assembly_authority_sha256"]})
        inst_doc.update(config_hashes())
        inst_path = _atomic_write_json(base / "instantiated_p3_p4_matrix.json", inst_doc)[0]
        inst_file_sha = hashlib.sha256(inst_path.read_bytes()).hexdigest()
        written["instantiated_p3_p4_matrix.json"] = inst_path.name
        freeze_doc = dict(payload["proposed_freeze"])
        freeze_doc.update({
            "tranche": TRANCHE_ID, "correction_version": CORRECTION_VERSION,
            "scientific_decision_payload_sha256": sci_sha,
            "candidate_ledger_sha256": record_hash(ledger_doc),
            "phase_manifest_sha256": dict(pre_sha),
            "instantiated_matrix_file_sha256": inst_file_sha,
            "provenance_mode": provenance_mode,
            "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
            "execution_authority_sha256": record_hash(auth),
            "assembly_authority": dict(assembly_auth),
            "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
            "note": ("P3 and P4 remain unauthorized even with this artifact present: a freeze is "
                     "necessary, never sufficient, and it requires its own reviewed "
                     "authorization commit."),
        })
        freeze_doc.update(config_hashes())
        written["proposed_bridge_freeze.json"] = _atomic_write_json(
            base / "proposed_bridge_freeze.json", freeze_doc)[0].name

    manifest = dict(payload["manifest"])
    manifest.update({
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "correction_version": CORRECTION_VERSION,
        "phase": "P2b", "provenance_mode": provenance_mode,
        "phase_kind": "ARITHMETIC_ASSEMBLY_NO_SOLVER_CALL",
        "scientific_decision_payload_sha256": sci_sha,
        "source_commit": auth["source_commit"], "source_tree": auth["source_tree"],
        "execution_authority_sha256": execution_authority_sha256(auth),
        "phase_authority_path": phase_authority_filename("P2b"),
        "phase_authority_file_sha256": pa_sha,
        "assembly_authority": dict(assembly_auth),
        "assembly_authority_sha256": assembly_auth["assembly_authority_sha256"],
        "full_matrix_sha256": record_hash(execution_matrix()),
        "predecessor_manifests": dict(pre_sha),
        "candidate_ledger_sha256": record_hash(ledger_doc),
        "proposed_freeze_sha256": (None if freeze_doc is None else record_hash(freeze_doc)),
        "rows_sha256": (None if payload["instantiated_matrix"] is None
                        else payload["instantiated_matrix"]["rows_sha256"]),
        "instantiated_matrix_file_sha256": inst_file_sha,
        "artifacts_written": dict(written),
        "solver_records": [],
    })
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
