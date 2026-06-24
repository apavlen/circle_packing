"""Circle packing candidate: 5x5 grid + 1 interstitial circle (n=26)."""
import json


def solve():
    centers, radii = [], []
    for j in range(5):
        for i in range(5):
            centers.append([(i + 0.5) / 5, (j + 0.5) / 5])
            radii.append(0.1)
    centers.append([0.2, 0.2])
    radii.append(0.04)
    return centers, radii


if __name__ == "__main__":
    c, rr = solve()
    print(json.dumps({"centers": c, "radii": rr, "sum_radii": sum(rr)}))
