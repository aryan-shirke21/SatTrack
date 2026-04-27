import pandas as pd
import os
from astropy.time import TimeDelta

def export_report(results, start_time):
    os.makedirs("outputs", exist_ok=True)
    rows = []
    
    for r in results:
        tca = start_time + TimeDelta(r["time_minutes"] * 60, format="sec")
        
        rows.append({
            "Object A":           r["object_A"],
            "Object B":           r["object_B"],
            "Miss Distance (km)": round(r["miss_distance"], 4),
            "MOID (km)":          round(r["moid_km"], 4),
            "TCA (UTC)":          tca.iso,
            "Pc Alfano":          f"{r['Pc_alfano']:.3e}",
            "Pc Monte Carlo":     f"{r['Pc_monte_carlo']:.3e}",
            "Risk":               r["risk_level"]
        })
    
    df   = pd.DataFrame(rows)
    path = "outputs/conjunction_report.csv"
    df.to_csv(path, index=False)
    
    print("\n" + "="*70)
    print("SATTRACK CONJUNCTION REPORT")
    print("="*70)
    print(df.to_string(index=False))
    print("="*70)
    print(f"Saved to {path}")
    
    return df