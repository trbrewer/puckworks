"""WP5 CI-lane markers. The heavy (science) tests are declared here in ONE place and
auto-marked ``slow`` at collection, so quick-pr can select ``-m "not slow ..."`` and
slow-science selects ``-m slow`` — the two lanes run DIFFERENT sets (not the same suite
under two names). `test_ci_lanes.py` guards this list against staleness.
"""
import socket

import pytest

# R2: the offline lanes must be PROVABLY network-free. Block outbound socket connects to
# anything but loopback for every test that is not explicitly a live/external_data test, so an
# accidental network call fails loudly instead of silently passing (or flaking) in CI.
_LOOPBACK = {"127.0.0.1", "::1", "localhost", "0.0.0.0", ""}


@pytest.fixture(autouse=True)
def _block_network(request):
    if request.node.get_closest_marker("live") or request.node.get_closest_marker("external_data"):
        yield
        return
    real = socket.socket.connect

    def guard(self, address):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if host not in _LOOPBACK:
            raise RuntimeError(
                "network access blocked in an offline lane (mark the test `live` or "
                "`external_data` if it must reach %r)" % (address,))
        return real(self, address)

    socket.socket.connect = guard
    try:
        yield
    finally:
        socket.socket.connect = real


# nodeid suffixes ("<file>::<test>") of tests that take more than ~2 s (see --durations).
SLOW = {
    "test_gates.py::test_quick_gates",
    "test_gates.py::test_g10_closure_robust_to_intersource_spread",
    "test_gates.py::test_g10_viscosity_sensitivity_verdict",
    "test_figure_exports.py::test_paperb_figure_render_is_deterministic",
    "test_figure_exports.py::test_paperb_bootstrap_analyses_are_deterministic",
    "test_public_claims.py::test_fast_producers_regenerate_matching_snapshots",
    "test_analysis.py::test_jensen_audit_uses_evaluated_mean",
    "test_analysis.py::test_ntube_state_classifier_distinguishes_single_channel",
    "test_analysis.py::test_cross_pressure_loco_full_precision",
    "test_analysis.py::test_cross_pressure_full_precision_from_raw",
    "test_harness.py::test_p2_cross_pressure_separation",
    "test_harness.py::test_p2_cross_pressure_loco",
}


def pytest_collection_modifyitems(config, items):
    for it in items:
        if any(it.nodeid.endswith(s) for s in SLOW):
            it.add_marker(pytest.mark.slow)
