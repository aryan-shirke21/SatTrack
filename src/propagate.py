import numpy as np
from astropy.time import Time
import astropy.units as u

def propagate_satellite(satrec, start_time, duration_days=7, step_minutes=1):
    total_steps = int(duration_days * 24 * 60 / step_minutes)
    positions = np.zeros((total_steps, 3))
    for step in range(total_steps):
        current = start_time + (step * step_minutes) * u.minute
        jd = current.jd1
        jdf = current.jd2
        error, r, v = satrec.sgp4(jd, jdf)
        if error == 0:
            positions[step] = r
        else:
            positions[step] = np.nan
    return positions

def propagate_all(satellites, start_time, duration_days=7):
    results = {}
    total = len(satellites)
    for i, sat in enumerate(satellites):
        if i % 10 == 0:
            print(f"  Propagating {i}/{total}...")
        positions = propagate_satellite(sat["satrec"], start_time, duration_days)
        results[sat["name"]] = {
            "positions": positions,
            "satrec": sat["satrec"],
            "line1": sat["line1"],
            "line2": sat["line2"]
        }
    print(f"Propagated {total} satellites")
    return results

if __name__ == "__main__":
    from parse_tles import parse_tle_file
    sats = parse_tle_file("data/catalog.txt", limit=5)
    start = Time.now()
    data = propagate_all(sats, start)
    first = list(data.keys())[0]
    print(f"\n{first}")
    print(f"First position (km): {data[first]['positions'][0]}")
    print(f"Shape: {data[first]['positions'].shape}")