"""Initial circle-packing program for n=26 (the evolvable candidate).

Ported from the Darwin circle_packing example
(examples/circle_packing/circle_packing.py): a constructor that places 26
circles and grows each to the largest radius that keeps the packing valid.

This is the ONLY file an evolution loop should mutate; grader.py and
test_solution.py are the fixed problem definition.
"""

import json

import numpy as np

N_CIRCLES = 26


def construct_packing():
    """Construct an arrangement of 26 circles in the unit square.

    A center circle, a ring of 8, and an outer ring of 16, each grown to the
    largest non-overlapping radius. Evolution is expected to improve this.
    """
    n = N_CIRCLES
    centers = np.zeros((n, 2))

    # A large circle in the center.
    centers[0] = [0.5, 0.5]

    # 8 circles in an inner ring.
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[i + 1] = [0.5 + 0.3 * np.cos(angle), 0.5 + 0.3 * np.sin(angle)]

    # 16 circles in an outer ring.
    for i in range(16):
        angle = 2 * np.pi * i / 16
        centers[i + 9] = [0.5 + 0.7 * np.cos(angle), 0.5 + 0.7 * np.sin(angle)]

    # Keep every center strictly inside the unit square.
    centers = np.clip(centers, 0.01, 0.99)

    radii = compute_max_radii(centers)
    return centers, radii


def compute_max_radii(centers):
    """Grow each circle to the largest radius that avoids walls and neighbours."""
    n = centers.shape[0]
    radii = np.ones(n)

    # Limit by distance to the square borders.
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Limit by distance to other circles: a pair at distance d can have summed
    # radii at most d. Scale overlapping pairs down proportionally.
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if radii[i] + radii[j] > dist:
                scale = dist / (radii[i] + radii[j])
                radii[i] *= scale
                radii[j] *= scale

    return radii


def solve():
    """Return ``(centers, radii)`` for the 26-circle packing."""
    centers, radii = construct_packing()
    return centers, radii


if __name__ == "__main__":
    c, r = solve()
    print(json.dumps({"centers": c.tolist(), "radii": r.tolist(), "sum_radii": float(np.sum(r))}))
