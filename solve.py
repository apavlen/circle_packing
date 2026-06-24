"""Initial circle-packing program (the evolvable candidate).

`solve()` returns a packing of circles in the unit square as
``(centers, radii)``. This is the ONLY file an evolutionary loop should mutate;
the correctness test (test_solution.py) is part of the fixed problem definition.
"""

import json


def solve():
    """Return ``(centers, radii)`` for a packing of circles in [0, 1]^2.

    Initial program: four mutually-tangent circles, each inscribed in a quadrant
    of the unit square (sum of radii = 1.0).
    """
    centers = [[0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]]
    radii = [0.25, 0.25, 0.25, 0.25]
    return centers, radii


if __name__ == "__main__":
    centers, radii = solve()
    print(json.dumps({"centers": centers, "radii": radii, "sum_radii": sum(radii)}))
