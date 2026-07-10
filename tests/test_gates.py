from puckworks.validation.gates import QUICK

def test_quick_gates():
    for g in QUICK:
        r = g()
        assert r["passed"], (g.__name__, r)
