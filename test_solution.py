"""Correctness unit test for the circle packing in solve.py.

This test is the FIXED scorer for the problem. It does two jobs at once:

1. Asserts correctness (every circle stays inside the unit square and no two
   circles overlap) so a developer running ``python -m unittest`` sees a normal
   pass/fail.
2. Emits the objective as ``metrics.json`` (validity, sum_radii, combined_score)
   so a Darwin worker can pick up the score without importing Darwin.

The score is the sum of radii, gated by validity: an invalid packing scores 0.
"""

import json
import math
import unittest
from pathlib import Path

from solve import solve

# Geometry tolerances: a circle may touch a wall or another circle, but not
# cross it. The tolerance absorbs floating-point noise without admitting real
# overlaps.
_BOUND_TOL = 1e-6
_OVERLAP_TOL = 1e-6

_METRICS_PATH = Path("metrics.json")


def _out_of_bounds(centers, radii):
    """Return the first circle index that escapes the unit square, else None."""
    for i, ((x, y), r) in enumerate(zip(centers, radii)):
        if r < 0:
            return i
        if (
            x - r < -_BOUND_TOL
            or x + r > 1 + _BOUND_TOL
            or y - r < -_BOUND_TOL
            or y + r > 1 + _BOUND_TOL
        ):
            return i
    return None


def _first_overlap(centers, radii):
    """Return the first overlapping ``(i, j)`` pair, else None."""
    n = len(centers)
    for i in range(n):
        for j in range(i + 1, n):
            (xi, yi), (xj, yj) = centers[i], centers[j]
            dist = math.hypot(xi - xj, yi - yj)
            if dist < radii[i] + radii[j] - _OVERLAP_TOL:
                return (i, j)
    return None


class TestCirclePacking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.centers, cls.radii = solve()
        bounds_bad = _out_of_bounds(cls.centers, cls.radii)
        overlap_bad = _first_overlap(cls.centers, cls.radii)
        valid = bounds_bad is None and overlap_bad is None and len(cls.centers) > 0
        sum_radii = float(sum(cls.radii))
        cls.metrics = {
            "validity": 1.0 if valid else 0.0,
            "sum_radii": sum_radii,
            "combined_score": sum_radii if valid else 0.0,
        }
        # Emit the score before any assertion fires so an invalid packing still
        # produces metrics.json (validity=0) rather than looking like a crash.
        _METRICS_PATH.write_text(json.dumps({"metrics": cls.metrics}), encoding="utf-8")

    def test_has_circles(self):
        self.assertGreater(len(self.centers), 0, "solve() returned no circles")

    def test_radii_match_centers(self):
        self.assertEqual(len(self.centers), len(self.radii), "centers/radii length mismatch")

    def test_all_circles_inside_unit_square(self):
        bad = _out_of_bounds(self.centers, self.radii)
        self.assertIsNone(bad, f"circle {bad} escapes the unit square")

    def test_no_circles_overlap(self):
        pair = _first_overlap(self.centers, self.radii)
        self.assertIsNone(pair, f"circles {pair} overlap")


if __name__ == "__main__":
    unittest.main()
