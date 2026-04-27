from astropy.time import Time

from src.parse_tles  import parse_tle_file
from src.propagate   import propagate_all
from src.moid        import filter_by_moid
from src.screen      import screen_candidates
from src.probability import compute_all_probabilities
from src.visualize   import plot_conjunction_3d, plot_distance_over_time
from src.report      import export_report

def main():
    print("\nParsing TLE catalog")
    satellites = parse_tle_file(
        "data/catalog.txt",
        limit=500,         
        max_age_days=30      
    )

    if not satellites:
        print("No satellites parsed. Check catalog.txt and max_age_days.")
        return

    print("\nPropagating orbits (be patient)")
    start_time    = Time.now()
    all_positions = propagate_all(satellites, start_time, duration_days=7)

    
    print("\nMOID filtering...")
    candidates = filter_by_moid(all_positions, moid_threshold_km=10)

    if not candidates:
        print("No candidates found. Try increasing moid_threshold_km.")
        return

    print("\nFine conjunction screening")
    conjunctions = screen_candidates(
        candidates, all_positions,
        conjunction_threshold_km=5
    )

    if not conjunctions:
        print("No conjunctions found. Try increasing conjunction_threshold_km.")
        return
    
    print("\nComputing collision probabilities")
    results = compute_all_probabilities(conjunctions, all_positions)

    print("\nGenerating report and plots")
    export_report(results, start_time)

    for top in results[:3]:
        pos_A = all_positions[top["object_A"]]["positions"]
        pos_B = all_positions[top["object_B"]]["positions"]
        plot_conjunction_3d(
            pos_A, pos_B,
            top["object_A"], top["object_B"],
            top["time_index"]
        )
        plot_distance_over_time(
            pos_A, pos_B,
            top["object_A"], top["object_B"],
            top["time_index"]
        )
    print("  SatTrack Complete")
    print(f"  Satellites screened:  {len(satellites)}")
    print(f"  MOID candidates:      {len(candidates)}")
    print(f"  Conjunctions found:   {len(conjunctions)}")
    if results:
        print(f"  Top risk: {results[0]['object_A']} vs {results[0]['object_B']}")
        print(f"  Pc (Alfano): {results[0]['Pc_alfano']:.3e}")

if __name__ == "__main__":
    main()