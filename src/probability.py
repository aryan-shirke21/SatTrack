import numpy as np
from scipy import integrate

HBR = 0.010
SIGMA_KM = 1.0

def alfano_pc(miss_distance_km, sigma=SIGMA_KM, hbr=HBR):
    if miss_distance_km <= 0:
        return 1.0
    combined_sigma = np.sqrt(2) * sigma
    lower = (miss_distance_km - hbr) / combined_sigma
    upper = (miss_distance_km + hbr) / combined_sigma
    def gaussian(x):
        return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)
    Pc, _ = integrate.quad(gaussian, lower, upper)
    return max(float(Pc), 0.0)

def monte_carlo_pc(pos_A, pos_B, time_idx, n_samples=1000, sigma=SIGMA_KM, hbr=HBR):
    r_A = pos_A[time_idx]
    r_B = pos_B[time_idx]
    if np.any(np.isnan(r_A)) or np.any(np.isnan(r_B)):
        return 0.0
    collision_count = 0
    for _ in range(n_samples):
        perturbed_A = r_A + np.random.normal(0, sigma, size=3)
        perturbed_B = r_B + np.random.normal(0, sigma, size=3)
        distance = np.linalg.norm(perturbed_A - perturbed_B)
        if distance < hbr:
            collision_count += 1
    return collision_count / n_samples

def compute_all_probabilities(conjunctions, all_positions):
    results = []
    total = len(conjunctions)
    for i, c in enumerate(conjunctions):
        print(f"  Computing Pc {i+1}/{total}: {c['object_A']} vs {c['object_B']}")
        pos_A = all_positions[c["object_A"]]["positions"]
        pos_B = all_positions[c["object_B"]]["positions"]
        pc_alfano = alfano_pc(c["miss_distance"])
        pc_mc = monte_carlo_pc(pos_A, pos_B, c["time_index"])
        risk = "HIGH" if pc_alfano > 1e-4 else "MONITOR" if pc_alfano > 1e-6 else "LOW"
        results.append({
            **c,
            "Pc_alfano": pc_alfano,
            "Pc_monte_carlo": pc_mc,
            "risk_level": risk
        })
    results.sort(key=lambda x: x["Pc_alfano"], reverse=True)
    return results

if __name__ == "__main__":
    from parse_tles import parse_tle_file
    from propagate import propagate_all
    from moid import filter_by_moid
    from screen import screen_candidates
    from astropy.time import Time
    sats = parse_tle_file("data/catalog.txt", limit=50)
    data = propagate_all(sats, Time.now())
    candidates = filter_by_moid(data, moid_threshold_km=50)
    conjunctions = screen_candidates(candidates, data, conjunction_threshold_km=50)
    results = compute_all_probabilities(conjunctions, data)
    print(f"\nResults:")
    for r in results:
        print(f"  {r['object_A']} vs {r['object_B']}")
        print(f"  Miss: {r['miss_distance']} km")
        print(f"  Pc Alfano:      {r['Pc_alfano']:.4e}")
        print(f"  Pc Monte Carlo: {r['Pc_monte_carlo']:.4e}")
        print(f"  Risk: {r['risk_level']}")