from sgp4.api import Satrec
from astropy.time import Time

def parse_tle_file(filepath, limit=500, max_age_days=30):
    now = Time.now()
    
    with open(filepath, "r") as f:
        lines = f.readlines()
    
    lines = [line.strip() for line in lines if line.strip()]
    grouped = [lines[i:i+3] for i in range(0, len(lines)-2, 3)]
    grouped.reverse()
    lines = [line for group in grouped for line in group]
    
    satellites  = []
    total_read  = 0
    skipped_age = 0
    skipped_bad = 0
    
    for i in range(0, len(lines) - 2, 3):
        line0 = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        
        if not (line1.startswith("1") and line2.startswith("2")):
            skipped_bad += 1
            continue
        
        total_read += 1
        
        try:
            satrec = Satrec.twoline2rv(line1, line2)
            
            # check TLE age
            tle_epoch = Time(satrec.jdsatepoch, format="jd")
            age_days  = (now - tle_epoch).to("day").value
            
            if age_days > max_age_days:
                skipped_age += 1
                continue
            
            name = line0[2:].strip() if line0.startswith("0 ") else line0.strip()
            import re
            if re.match(r'^OBJECT\s+[A-Z]$', name.strip()):
                continue
            if "TBA" in name.upper() or "TO BE ASSIGNED" in name.upper():
                continue
            
            satellites.append({
                "name":    name,
                "line1":   line1,
                "line2":   line2,
                "satrec":  satrec,
                "tle_age": round(age_days, 2)
            })
        
        except Exception:
            skipped_bad += 1
            continue
        
        if limit and len(satellites) >= limit:
            break
    
    print(f"TLE parsing complete:")
    print(f"  Total read:       {total_read}")
    print(f"  Skipped (old):    {skipped_age}  (age > {max_age_days} days)")
    print(f"  Skipped (bad):    {skipped_bad}")
    print(f"  Kept:             {len(satellites)}")
    
    return satellites

if __name__ == "__main__":
    sats = parse_tle_file("data/catalog.txt", limit=10, max_age_days=30)
    for s in sats:
        print(f"{s['name']} — TLE age: {s['tle_age']} days")