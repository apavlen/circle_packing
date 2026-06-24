"""Correctness unit test for the n=26 circle packing in solve.py.

This test is the FIXED scorer for the problem. It does two jobs at once:

1. Asserts correctness using the grader ported from Darwin's circle_packing
   example (exactly 26 circles, in bounds, non-overlapping), so a developer
   running ``python -m unittest`` sees a normal pass/fail.
2. Emits the objective as ``metrics.json`` (validity, sum_radii, target_ratio,
   combined_score) so a zero-Darwin worker can pick up the score.

combined_score = (sum_radii / TARGET_VALUE) * validity, matching
examples/circle_packing/evaluator.py — so 1.0 is the AlphaEvolve target and an
invalid packing scores 0.
"""

import json
import unittest
from pathlib import Path

import numpy as np

from grader import N_CIRCLES, score, validate_packing
from solve import solve

_METRICS_PATH = Path("metrics.json")


class TestCirclePacking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        centers, radii = solve()
        cls.centers = np.asarray(centers, dtype=float)
        cls.radii = np.asarray(radii, dtype=float)
        cls.metrics = score(cls.centers, cls.radii)
        # Emit the score before any assertion fires so an invalid packing still
        # produces metrics.json (validity=0) rather than looking like a crash.
        _METRICS_PATH.write_text(json.dumps({"metrics": cls.metrics}), encoding="utf-8")

    def test_exactly_26_circles(self):
        self.assertEqual(self.centers.shape, (N_CIRCLES, 2), "must be exactly 26 centers")
        self.assertEqual(self.radii.shape, (N_CIRCLES,), "must be exactly 26 radii")

    def test_packing_is_valid(self):
        self.assertTrue(
            validate_packing(self.centers, self.radii),
            "packing is invalid: a circle is out of bounds or two circles overlap",
        )


if __name__ == "__main__":
    unittest.main()
