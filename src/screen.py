import numpy as np

def find_closest_approach(pos_A, pos_B):
    diff = pos_A - pos_B
    distances = np.linalg.norm(diff, axis=1)
    valid = ~np.isnan(distances)
    if not np.any(valid):
        return None, np.inf
    min_idx = np.nanargmin(distances)
    min_dist = distances[min_idx]
    return int(min_idx), float(min_dist)

def screen_candidates(candidate_pairs, all_positions, conjunction_threshold_km=5):
    conjunctions = []
    total = len(candidate_pairs)
    print(f"Fine screening {total} candidate pairs...")
    for i, pair in enumerate(candidate_pairs):
        name_A = pair["object_A"]
        name_B = pair["object_B"]
        pos_A = all_positions[name_A]["positions"]
        pos_B = all_positions[name_B]["positions"]
        time_idx, miss_dist = find_closest_approach(pos_A, pos_B)
        if miss_dist < conjunction_threshold_km:
            conjunctions.append({
                "object_A": name_A,
                "object_B": name_B,
                "miss_distance": round(miss_dist, 4),
                "time_index": time_idx,
                "time_minutes": time_idx,
                "moid_km": pair["moid_km"]
            })
        if (i + 1) % 100 == 0:
            print(f"  Screened {i+1}/{total}...")
    conjunctions.sort(key=lambda x: x["miss_distance"])
    print(f"Found {len(conjunctions)} conjunctions")
    return conjunctions

if __name__ == "__main__":
    from parse_tles import parse_tle_file
    from propagate import propagate_all
    from moid import filter_by_moid
    from astropy.time import Time
    sats = parse_tle_file("data/catalog.txt", limit=50)
    data = propagate_all(sats, Time.now())
    candidates = filter_by_moid(data, moid_threshold_km=50)
    conjunctions = screen_candidates(candidates, data, conjunction_threshold_km=50)
    print(f"\nTop conjunctions:")
    for c in conjunctions[:5]:
        print(f"  {c['object_A']} vs {c['object_B']} — {c['miss_distance']} km")