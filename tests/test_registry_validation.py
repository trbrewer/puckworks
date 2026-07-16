"""WP4.4 — registry metadata validation must be an explicit exception, NOT a Python `assert`,
so enum/stage checks cannot silently disappear under `python -O` (optimized bytecode strips
assert statements). Run the check in a real `-O` subprocess.
"""
import subprocess
import sys


def _run_dash_O(body):
    return subprocess.run([sys.executable, "-O", "-c", body], capture_output=True, text=True)


def test_bad_stage_rejected_under_dash_O():
    body = (
        "from puckworks.registry import register, Component\n"
        "try:\n"
        "    register(Component(name='x.bad_stage', stage='NOT_A_STAGE', kind='calibration', paper='x'))\n"
        "except ValueError:\n"
        "    print('REJECTED')\n"
        "else:\n"
        "    print('LEAKED')\n"
    )
    out = _run_dash_O(body)
    assert out.returncode == 0, out.stderr
    assert "REJECTED" in out.stdout and "LEAKED" not in out.stdout


def test_bad_evidence_strength_rejected_under_dash_O():
    body = (
        "from puckworks.registry import register, Component\n"
        "try:\n"
        "    register(Component(name='x.bad_ev', stage='flow', kind='calibration', paper='x',\n"
        "                       evidence_strength='super_definitely_proven'))\n"
        "except ValueError:\n"
        "    print('REJECTED')\n"
        "else:\n"
        "    print('LEAKED')\n"
    )
    out = _run_dash_O(body)
    assert out.returncode == 0, out.stderr
    assert "REJECTED" in out.stdout and "LEAKED" not in out.stdout
