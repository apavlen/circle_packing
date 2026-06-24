"""Circle packing candidate: 3x3 grid (sum_radii = 1.5)."""
import json


def solve():
    k = 3
    r = 1.0 / (2 * k)
    centers = [[(i + 0.5) / k, (j + 0.5) / k] for i in range(k) for j in range(k)]
    radii = [r] * (k * k)
    return centers, radii


if __name__ == "__main__":
    c, rr = solve()
    print(json.dumps({"centers": c, "radii": rr, "sum_radii": sum(rr)}))
