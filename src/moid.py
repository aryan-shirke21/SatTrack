import numpy as np
from scipy.spatial import KDTree

def estimate_moid(pos_A, pos_B, sample_step=10):
    A = pos_A[::sample_step]
    B = pos_B[::sample_step]
    valid_A = A[~np.any(np.isnan(A), axis=1)]
    valid_B = B[~np.any(np.isnan(B), axis=1)]
    if len(valid_A) == 0 or len(valid_B) == 0:
        return np.inf
    tree = KDTree(valid_B)
    distances, _ = tree.query(valid_A, k=1)
    return float(np.min(distances))

def filter_by_moid(all_positions, moid_threshold_km=10):
    names = list(all_positions.keys())
    n = len(names)
    total_pairs = n * (n - 1) // 2
    print(f"MOID filtering {n} objects ({total_pairs} pairs)...")
    candidates = []
    checked = 0
    for i in range(n):
        for j in range(i + 1, n):
            name_A = names[i]
            name_B = names[j]
            pos_A = all_positions[name_A]["positions"]
            pos_B = all_positions[name_B]["positions"]
            moid = estimate_moid(pos_A, pos_B)
            if moid < moid_threshold_km:
                candidates.append({
                    "object_A": name_A,
                    "object_B": name_B,
                    "moid_km": round(moid, 4)
                })
            checked += 1
            if checked % 5000 == 0:
                pct = 100 * checked / total_pairs
                print(f"  {checked}/{total_pairs} ({pct:.1f}%) — {len(candidates)} candidates")
    print(f"MOID filter complete. Candidates: {len(candidates)}/{total_pairs}")
    return candidates

if __name__ == "__main__":
    from parse_tles import parse_tle_file
    from propagate import propagate_all
    from astropy.time import Time
    sats = parse_tle_file("data/catalog.txt", limit=20)
    data = propagate_all(sats, Time.now())
    candidates = filter_by_moid(data, moid_threshold_km=100)
    print(f"\nCandidate pairs:")
    for c in candidates[:5]:
        print(f"  {c['object_A']} vs {c['object_B']} — MOID: {c['moid_km']} km")