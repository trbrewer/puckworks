"""Adversarial checks of the documentation snapshot checker; no scientific execution."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_aggregates as check


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.row = next(r for r in check.rows(check.ROOT, "balance/balance_components.csv")
                        if r["run"] == "tight_early" and r["t_hat"] == "1.0"
                        and r["quadrature"] == "simpson")

    def test_complete_supplied_snapshot(self):
        self.assertEqual(check.check(check.ROOT)["arithmetic_rows"],
                         {"balance_components.csv": 27, "timeline.csv": 54,
                          "balance_history.csv": 2616})

    def test_sign_mutation_rejected_without_hash_check(self):
        changed = dict(self.row)
        key = "advection_contribution_mg"
        changed[key] = str(-float(changed[key]))
        with self.assertRaisesRegex(ValueError, "signed component"):
            check.check_budget(changed, True)

    def test_cup_mutation_rejected_without_hash_check(self):
        changed = dict(self.row)
        changed["cup_mg"] = str(float(changed["cup_mg"]) + .1)
        with self.assertRaisesRegex(ValueError, "inventory/cup"):
            check.check_budget(changed, True)

    def test_gram_milligram_mutation_rejected(self):
        changed = dict(self.row)
        changed["initial_mg"] = str(float(changed["initial_mg"]) / 1000)
        with self.assertRaises(ValueError):
            check.check_budget(changed, True)

    def test_file_tampering_rejected(self):
        # Mock only this snapshot's actual component bytes: other files stay real.
        target = check.ROOT / "balance/balance_components.csv"
        original = Path.read_bytes
        def read(path):
            value = original(path)
            return value + b"tampered" if path == target else value
        with patch.object(Path, "read_bytes", read):
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                check.integrity(check.ROOT)

    def test_missing_payload_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SHA256SUMS.txt").write_text("0" * 64 + "  missing.csv\n")
            with self.assertRaises(FileNotFoundError):
                check.integrity(root)


if __name__ == "__main__":
    unittest.main()
