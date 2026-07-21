"""Strict canonical serialization for the Espresso Model Relay (§10, §15.5).

No `default=str`, allow_nan=False, explicit NumPy normalization, unsupported/non-finite rejection, byte
determinism across processes, and CLI/internal serializer agreement.
"""
import dataclasses
import subprocess
import sys
import textwrap
from enum import Enum

import pytest

from puckworks.product import linked_pull_records as R


def test_no_canonical_path_uses_default_str():
    import inspect
    src = inspect.getsource(R)
    # the strict path must never fall back to default=str in an actual json.dumps CALL
    assert ", default=str" not in src and "default=str)" not in src
    assert "allow_nan=False" in src


def test_rejects_nan_and_infinity():
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(R.NonCanonicalValue):
            R.canonical_json_bytes({"x": bad})


def test_rejects_unsupported_objects_and_non_string_keys():
    with pytest.raises(R.NonCanonicalValue):
        R.normalize_for_json(object())
    with pytest.raises(R.NonCanonicalValue):
        R.normalize_for_json({1: "a"})


def test_numpy_scalars_and_arrays_normalize_explicitly():
    import numpy as np
    assert R.normalize_for_json(np.float64(1.5)) == 1.5
    assert R.normalize_for_json(np.int64(3)) == 3
    assert R.normalize_for_json(np.array([[1, 2], [3, 4]])) == [[1, 2], [3, 4]]


def test_dataclass_and_enum_normalize():
    class C(Enum):
        A = "a"

    @dataclasses.dataclass
    class D:
        x: int
        c: C

    assert R.normalize_for_json(D(1, C.A)) == {"x": 1, "c": "a"}


def test_key_order_independence_and_byte_determinism():
    a = R.canonical_json_bytes({"b": 1, "a": 2})
    b = R.canonical_json_bytes({"a": 2, "b": 1})
    assert a == b


def test_pretty_view_has_same_values_as_hash_path():
    import json
    obj = {"z": [1, 2], "a": {"n": 3.5}}
    pretty = json.loads(R.canonical_json_text(obj))
    canonical = json.loads(R.canonical_json_bytes(obj).decode())
    assert pretty == canonical


def test_json_round_trips():
    import json
    obj = {"a": [1, 2.5, "x", True, None], "b": {"c": 3}}
    assert json.loads(R.canonical_json_bytes(obj).decode()) == obj


@pytest.mark.slow
def test_hashes_match_across_two_fresh_processes():
    code = textwrap.dedent("""
        from puckworks.product.linked_pull import execute_illustrative_linked_pull, RelayRequest
        r = execute_illustrative_linked_pull(RelayRequest(mode='fast'))
        print(r['model_output_hash'], r['artifact_hash'])
    """)

    def run():
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr[-2000:]
        return out.stdout.strip().splitlines()[-1]

    assert run() == run()


@pytest.mark.slow
def test_cli_json_uses_the_canonical_serializer(tmp_path):
    out = tmp_path / "relay.json"
    r = subprocess.run([sys.executable, "-m", "puckworks.product.linked_pull", "--mode", "fast",
                        "--format", "json", "--output", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    text = out.read_text()
    assert "NaN" not in text and "Infinity" not in text
    from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull
    res = execute_illustrative_linked_pull(RelayRequest(mode="fast"))
    import json
    assert json.loads(text)["model_output_hash"] == res["model_output_hash"]
