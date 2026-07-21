"""No cross-model global-state mutation (post-merge stabilization, §5).

Importing or running one model must not rewrite another model's module-level scientific constant.
Regression for the streamtube->Cameron C_S0 import-time mutation that made Cameron import-order dependent
and polluted the Full Laboratory Tour (Cameron EY read 17.06 % instead of its own 14.11 %).
"""
import subprocess
import sys
import textwrap

import pytest


def _run(code: str) -> str:
    """Run a snippet in a FRESH interpreter and return its stdout (import-order isolation)."""
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout.strip().splitlines()[-1]


def test_importing_streamtube_does_not_mutate_cameron_c_s0():
    out = _run("""
        from puckworks.models.cameron2020 import extraction_bdf as cam
        before = cam.C_S0
        import puckworks.models.brewer2026.streamtube  # noqa
        print(before == cam.C_S0 == 118.0)
    """)
    assert out == "True"


@pytest.mark.parametrize("preamble", [
    "",                                                       # Cameron first
    "import puckworks.models.brewer2026.streamtube",          # streamtube imported first
    "from puckworks.product.linked_pull import execute_illustrative_linked_pull, RelayRequest;"
    "execute_illustrative_linked_pull(RelayRequest(mode='fast'))",   # a full relay run first
])
@pytest.mark.slow
def test_cameron_output_is_import_order_invariant(preamble):
    out = _run(f"""
        {preamble}
        from puckworks.models.cameron2020 import extraction_bdf as cam
        r = cam.simulate_shot(1.7, p_bar=9.0, m_in=0.020, m_out=0.040)
        print(round(r.EY, 4))
    """)
    assert out == "14.106"                                    # Cameron's own C_S0=118 basis, always


def test_streamtube_uses_its_own_basis_regardless_of_import_order():
    # streamtube's homogeneous EY reflects its calibrated 118/PHI_S basis (~17.06), never Cameron's 118
    for preamble in ("", "import puckworks.models.cameron2020.extraction_bdf"):
        out = _run(f"""
            {preamble}
            from puckworks.models.brewer2026 import streamtube as st
            resp = st.EYResponse(gs=1.7, p_bar=9.0, m_in=0.020, m_out=0.040)
            print(round(float(resp.ey_of_k(1.0)), 3))
        """)
        assert out == "17.058"


@pytest.mark.slow
def test_relay_run_leaves_cameron_c_s0_unchanged():
    out = _run("""
        from puckworks.models.cameron2020 import extraction_bdf as cam
        before = cam.C_S0
        from puckworks.product.linked_pull import execute_illustrative_linked_pull, RelayRequest
        execute_illustrative_linked_pull(RelayRequest(mode='fast'))
        print(before == cam.C_S0 == 118.0)
    """)
    assert out == "True"


@pytest.mark.slow
def test_relay_does_not_pin_or_restore_cameron_globals():
    # the stabilization removed the C_S0 repair machinery entirely
    import inspect

    from puckworks.product import linked_pull
    src = inspect.getsource(linked_pull)
    assert "_pin_cameron_c_s0" not in src
    assert "C_S0" not in src or "no longer touches" in src        # only the explanatory comment may mention it


@pytest.mark.slow
def test_full_tour_hash_is_import_order_invariant():
    def tour_hash(preamble):
        return _run(f"""
            {preamble}
            from puckworks.product import lab, lab_tour
            t = lab_tour.execute_laboratory_tour(lab.ScenarioRequest('pv19_named'),
                                                 execution_context='LOCAL_PRIVATE').to_dict()
            print(t['tour_scientific_hash'])
        """)
    clean = tour_hash("")
    streamtube_first = tour_hash("import puckworks.models.brewer2026.streamtube")
    relay_first = tour_hash("from puckworks.product.linked_pull import execute_illustrative_linked_pull, "
                            "RelayRequest; execute_illustrative_linked_pull(RelayRequest(mode='fast'))")
    assert clean == streamtube_first == relay_first
