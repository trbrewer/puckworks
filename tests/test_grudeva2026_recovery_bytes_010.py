"""Small opaque-byte controls, runnable with -I -S -X faulthandler."""
import hashlib
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile
import unittest

COMMAND = Path(__file__).resolve().parents[1]/'tools/verify_grudeva2026_recovery_bytes_010.py'
d = runpy.run_path(str(COMMAND))


def fixture(dtype, header_size):
    payload = bytes(range(16)) if dtype == '|i1' else bytes(range(128))
    text = ("{'descr': '%s', 'fortran_order': False, 'shape': (16,), }" % dtype).encode()
    text += b' '*(header_size-11-len(text))+b'\n'
    return b'\x93NUMPY\x01\x00'+struct.pack('<H', len(text))+text+payload, payload


class RecoveryBytes(unittest.TestCase):
    def test_both_dtypes_and_nonuniform_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            for dtype, size in [('<f8', 128), ('|i1', 256), ('<f8', 192)]:
                with self.subTest(dtype=dtype, size=size):
                    raw, payload = fixture(dtype, size)
                    path = Path(directory)/f'{size}.npy'
                    path.write_bytes(raw)
                    actual = d['scan'](path)
                    self.assertEqual(actual['header_bytes'], size)
                    self.assertEqual(actual['payload_sha256'], hashlib.sha256(payload).hexdigest())
                    self.assertEqual(actual['member_sha256'], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(actual['dtype'], dtype)
                    self.assertEqual(actual['shape'], [16])
                    self.assertTrue(actual['length_matches_header'])

    def test_unsafe_and_truncated_headers(self):
        raw, _ = fixture('<f8', 128)
        for bad in [raw[:20], raw.replace(b'<f8', b'|O8'), raw.replace(b'False', b'True '),
                    raw.replace(b'(16,)', b'(16) '), raw.replace(b'(16,)', b'(1,,)')]:
            with self.subTest(bad=bad[:40]), self.assertRaises(ValueError):
                d['header'](bad)

    def test_persisted_condition_and_member(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, payload = fixture('|i1', 256)
            for mode in ('truncated', 'mismatched', 'trailing'):
                path = root/(mode+'.npy')
                changed = {'truncated': raw[:-1], 'mismatched': raw[:-1]+b'!', 'trailing': raw+b'!'}[mode]
                path.write_bytes(changed)
                row = {'source': str(path), 'group': 'segment-1', 'member': 'order',
                       'expected': {'dtype': '|i1', 'shape': [16], 'sha256': hashlib.sha256(payload).hexdigest()}}
                evidence = d['helper'].Evidence(root/mode)
                self.assertFalse(d['verify_member'](evidence, row, 0))
                record = json.loads((root/mode/'FIRST_FAILURE.json').read_text())
                self.assertEqual(record['expected'], row)
                self.assertFalse(record['observed']['checks']['numeric_identity'])
                self.assertEqual(record['observed']['checks']['payload_length'], mode == 'mismatched')
                self.assertEqual(evidence.finish({})['status'], 'FAIL')

    def test_isolated_child_and_import_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, payload = fixture('|i1', 256)
            path = root/'order.npy'
            path.write_bytes(raw)
            expected = {'dtype': '|i1', 'shape': [16], 'sha256': hashlib.sha256(payload).hexdigest()}
            commitment = root/'SOURCE_COMMITMENT.json'
            commitment.write_text(json.dumps({'segment-1': {'order': expected}}))
            plan = {'source_commitment': str(commitment),
                    'records': [{'path': str(commitment), 'sha256': d['file_hash'](commitment)}],
                    'members': [{'source': str(path), 'group': 'segment-1', 'member': 'order', 'expected': expected}],
                    'checker_sha256': d['file_hash'](COMMAND), 'helper_sha256': d['HELPER_SHA256'],
                    'executable_sha256': d['file_hash'](sys.executable), 'python': sys.version}
            plan_path = root/'plan.json'
            plan_path.write_text(json.dumps(plan))
            result = subprocess.run([sys.executable, '-I', '-S', '-X', 'faulthandler', str(COMMAND),
                                     '--plan', str(plan_path), '--output', str(root/'result')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads((root/'result/RESULT.json').read_text())
            self.assertEqual(receipt['members_verified'], 1)
            self.assertEqual(receipt['forbidden_imports'], [])
            self.assertEqual(receipt['numeric_library_imports'], [])
            self.assertEqual(receipt['isolated'], 1)
            self.assertEqual(receipt['no_site'], 1)


if __name__ == '__main__':
    unittest.main()
