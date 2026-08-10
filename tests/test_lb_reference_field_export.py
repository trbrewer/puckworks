"""RP-D.1 — the optional macroscopic-field export on `brewer2026.lb_reference.solve` is ADDITIVE.

These tests exist because "the change is inert" is a claim, not a fact. They MEASURE it: every
load-bearing standard output is compared between a default call and a field-exporting call on the
same geometry, and the live maximum difference is asserted to be exactly zero.

They also pin the I-093 provenance invariant that made this capability contentious: the frozen
screen must stay bound to the historical blob it ran, so this module asserts the historical digest
is still recoverable from git — see `tests/test_screen_i093.py` for the binding itself.
"""
import hashlib
import pathlib
import subprocess

import numpy as np
import pytest

from puckworks.models.brewer2026 import lb_reference as lb

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The digest `docs/insights/screens/I-093/result.json` records for the solver module, i.e. the
#: source the frozen screen actually executed. It must stay recoverable from git FOREVER; it must
#: NOT constrain what the live module may become.
I093_HISTORICAL_LB_SHA256 = "9a60371d7777d3d91fe7df2ea529db498268f12b08ab6c461ec511190a0a989f"

STANDARD_KEYS = ("q", "k", "phi", "nu", "steps", "seconds", "ux")
#: `seconds` is wall-clock and therefore not reproducible; everything else is load-bearing.
DETERMINISTIC_KEYS = ("q", "k", "phi", "nu", "steps", "ux")

KW = dict(g=1e-6, tau_plus=1.2, max_steps=20000, check=200, rtol=1e-7, min_steps=600,
          verbose=False)


def _channel(Nz=13, N=4):
    solid = np.zeros((N, N, Nz), dtype=bool)
    solid[:, :, 0] = True
    solid[:, :, -1] = True
    return solid


def _fixture_mask():
    """A compact, deterministic, NON-trivial RP-D fixture mask (the smoke resolution): two lanes
    of differing segment order, a divider with an open lateral aperture, walls on y and z."""
    from puckworks.analysis import rp_d_lc_virtual_fixture as vf
    mask, _ = vf.build_fixture(vf.S_SMOKE, aperture={"kx": 5, "kz": 2})
    return mask


CASES = {"plane_channel": _channel, "rp_d_fixture": _fixture_mask}


@pytest.fixture(scope="module", params=sorted(CASES))
def pair(request):
    solid = CASES[request.param]()
    base = lb.solve(solid, **KW)
    both = lb.solve(solid, return_fields=("rho", "uy", "uz"), **KW)
    return request.param, solid, base, both


# --------------------------------------------------------------------------------------------
# the numbers do not move
# --------------------------------------------------------------------------------------------
def test_every_deterministic_standard_output_is_bit_identical(pair):
    name, _solid, base, both = pair
    worst = 0.0
    for k in DETERMINISTIC_KEYS:
        a, b = base[k], both[k]
        if isinstance(a, np.ndarray):
            assert a.shape == b.shape
            assert np.array_equal(a, b), "%s: array output %s moved" % (name, k)
            worst = max(worst, float(np.abs(a - b).max()))
        else:
            assert a == b, "%s: scalar output %s moved: %r -> %r" % (name, k, a, b)
            worst = max(worst, abs(float(a) - float(b)))
    # the live maximum difference, measured rather than asserted in prose
    assert worst == 0.0, "%s: live max |difference| = %r, expected exactly 0" % (name, worst)


def test_convergence_path_is_unchanged(pair):
    name, _solid, base, both = pair
    assert base["steps"] == both["steps"], name
    assert base["steps"] < KW["max_steps"], "%s: control case must converge" % name


def test_default_result_gains_no_new_keys(pair):
    _name, _solid, base, _both = pair
    assert set(base) == set(STANDARD_KEYS)
    for f in lb.EXPORTABLE_FIELDS:
        assert f not in base, "%s leaked into the default result" % f


def test_requesting_a_subset_returns_exactly_that_subset():
    solid = _channel()
    r = lb.solve(solid, return_fields=("rho",), **KW)
    assert set(r) == set(STANDARD_KEYS) | {"rho"}
    r2 = lb.solve(solid, return_fields=("uy", "uz"), **KW)
    assert set(r2) == set(STANDARD_KEYS) | {"uy", "uz"}


# --------------------------------------------------------------------------------------------
# the exported fields are usable and obey the module's stated conventions
# --------------------------------------------------------------------------------------------
def test_exported_fields_have_the_right_shape_and_are_finite(pair):
    name, solid, _base, both = pair
    for f in lb.EXPORTABLE_FIELDS:
        arr = both[f]
        assert arr.shape == solid.shape, "%s: %s shape" % (name, f)
        assert np.isfinite(arr).all(), "%s: %s has non-finite entries" % (name, f)


def test_density_is_a_physical_density_at_fluid_nodes(pair):
    name, solid, _base, both = pair
    rho = both["rho"][~solid]
    assert np.allclose(rho, 1.0, atol=1e-3), "%s: fluid density is not near unity" % name


def test_transverse_velocities_are_zero_at_solid_nodes(pair):
    """`uy`/`uz` follow the same solid-node convention as `ux` inside the loop: exactly zero.
    (`ux` itself is returned with the +g/2 measurement shift, so IT is g/2 in solids — the
    documented asymmetry callers must mask for.)"""
    name, solid, _base, both = pair
    for f in ("uy", "uz"):
        assert np.array_equal(both[f][solid], np.zeros(int(solid.sum()))), "%s: %s" % (name, f)


def test_repeated_field_export_runs_are_deterministic():
    solid = _channel()
    a = lb.solve(solid, return_fields=("rho", "uy", "uz"), **KW)
    b = lb.solve(solid, return_fields=("rho", "uy", "uz"), **KW)
    for k in DETERMINISTIC_KEYS:
        if isinstance(a[k], np.ndarray):
            assert np.array_equal(a[k], b[k]), k
        else:
            assert a[k] == b[k], k
    for f in lb.EXPORTABLE_FIELDS:
        assert np.array_equal(a[f], b[f]), f


# --------------------------------------------------------------------------------------------
# unknown names fail loudly
# --------------------------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [("f",), ("pressure",), ("rho", "ux"), ("RHO",)])
def test_unknown_return_fields_are_rejected_not_ignored(bad):
    with pytest.raises(ValueError, match="unknown return_fields"):
        lb.solve(_channel(), return_fields=bad, **KW)


def test_distribution_functions_are_not_exportable():
    assert "f" not in lb.EXPORTABLE_FIELDS
    assert set(lb.EXPORTABLE_FIELDS) == {"rho", "uy", "uz"}


# --------------------------------------------------------------------------------------------
# the historical source the frozen I-093 screen ran is still recoverable
# --------------------------------------------------------------------------------------------
def test_the_i093_historical_solver_blob_is_still_recoverable_from_git():
    def git(*a):
        return subprocess.run(("git",) + a, cwd=REPO, capture_output=True)

    if git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true":
        pytest.skip("shallow checkout: historical blobs are not observable here")
    commits = git("log", "--format=%H", "--diff-filter=A", "--",
                  "docs/insights/screens/I-093/PROTOCOL.md").stdout.split()
    if not commits:
        pytest.skip("I-093 protocol not committed")
    freeze = commits[-1].decode()
    blob = git("cat-file", "blob", "%s:puckworks/models/brewer2026/lb_reference.py" % freeze)
    if blob.returncode != 0:
        pytest.skip("historical blob absent from this checkout")
    assert hashlib.sha256(blob.stdout).hexdigest() == I093_HISTORICAL_LB_SHA256
