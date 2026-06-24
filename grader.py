"""Scorer for circle packing (n=26), taken from the Darwin circle_packing example.

`validate_packing` and the `combined_score` formula are ported verbatim from
examples/circle_packing/evaluator.py so this repo's self-score matches Darwin's
canonical grader:

    combined_score = (sum_radii / TARGET_VALUE) * validity

with the number of circles fixed at 26. Pure functions, no Darwin imports, so a
zero-Darwin runner can score the candidate.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)

N_CIRCLES = 26
TARGET_VALUE = 2.635  # AlphaEvolve result for n=26


def validate_packing(centers, radii):
    """Validate that circles don't overlap and are inside the unit square.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        radii: np.array of shape (n) with radius of each circle

    Returns:
        True if valid, False otherwise
    """
    n = centers.shape[0]

    # Check for NaN values
    if np.isnan(centers).any():
        logger.warning("NaN values detected in circle centers")
        return False

    if np.isnan(radii).any():
        logger.warning("NaN values detected in circle radii")
        return False

    # Check if radii are nonnegative and not nan
    for i in range(n):
        if radii[i] < 0:
            logger.warning("Circle %d has negative radius %f", i, radii[i])
            return False
        elif np.isnan(radii[i]):
            logger.warning("Circle %d has nan radius", i)
            return False

    # Check if circles are inside the unit square
    for i in range(n):
        x, y = centers[i]
        r = radii[i]
        if x - r < -1e-6 or x + r > 1 + 1e-6 or y - r < -1e-6 or y + r > 1 + 1e-6:
            logger.warning(
                "Circle %d at (%f, %f) with radius %f is outside the unit square", i, x, y, r
            )
            return False

    # Check for overlaps
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if dist < radii[i] + radii[j] - 1e-6:  # Allow for tiny numerical errors
                logger.warning(
                    "Circles %d and %d overlap: dist=%f, r1+r2=%f", i, j, dist, radii[i] + radii[j]
                )
                return False

    return True


def score(centers, radii):
    """Score a packing the way the canonical CirclePackingEvaluator does.

    Returns the metric dict (validity, sum_radii, target_ratio, combined_score).
    A solution that is not exactly 26 circles, out of bounds, or overlapping
    scores 0 — there is no credit for cheating the constraint.
    """
    centers = np.asarray(centers, dtype=float)
    radii = np.asarray(radii, dtype=float)

    shape_valid = centers.shape == (N_CIRCLES, 2) and radii.shape == (N_CIRCLES,)
    valid = shape_valid and validate_packing(centers, radii)

    sum_radii = float(np.sum(radii)) if valid else 0.0
    target_ratio = sum_radii / TARGET_VALUE if valid else 0.0
    validity = 1.0 if valid else 0.0
    combined_score = target_ratio * validity

    return {
        "validity": validity,
        "sum_radii": sum_radii,
        "target_ratio": float(target_ratio),
        "combined_score": float(combined_score),
    }
