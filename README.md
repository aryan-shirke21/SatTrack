# SatTrack
## Autonomous Satellite Collision/Conjunction Risk Analysis Program

An SSA system that automatically filters through thousands of TLE objects to determine the likelihood of conjunctions, calculates the collision probability using the Alfano approach along with the Monte Carlo technique, and produces ranked conjunction reports with three-dimensional visualization.

## Motivation

More than 27,000 objects have been observed in Earth’s orbit at speeds of around 
28,000 kilometers per hour. One collision between any two such objects creates many new debris particles that might collide with other particles in turn, creating what is called Kessler Syndrome. This process starts with automated conjunction screening which is the first step towards dealing with the problem. The SatTrack software uses the screening methodology similar to that of NASA’s CARA and ESA’s Space Debris office, modified for rapid prototyping and experimentation.


## Pipeline Architecture

TLE Catalog (Space-Track.org) -> TLE Parser + Age Filter (only TLEs < 30 days old) -> SGP4 Orbit Propagation -> (7-day position tables, 1-min steps) -> MOID Pre-filter (geometric orbit intersection distance) -> Fine Conjunction Screening (KDTree nearest-neighbor, minute-resolution) -> Collision Probability (Alfano method + Monte Carlo) -> Conjunction Report + Visualizations (CSV + 3D plots + distance-time plots)

## Key Features

- **MOID-based pre-filtering** industry standard technique which identifies crossing orbits
  with very different inclinations and eccentricity.
- **SGP4 propagation** via the sgp4 library for all-catalog screening
- **Alfano collision probability** — industry-standard Pc computation used operationally by
  NASA and ESA
- **Monte Carlo uncertainty quantification** — independent Pc verification via 1000-sample   
  stochastic simulation
- **TLE age filtering** — automatically discards stale TLEs older than 30 days, ensuring 
  physically meaningful results **3D orbital visualizations** with closest approach marking
- **Ranked conjunction reports** exported as CSV

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| sgp4 | SGP4/SDP4 orbit propagation |
| astropy | Time handling, units |
| numpy | Vectorized position math |
| scipy | KDTree spatial indexing, numerical integration |
| matplotlib | 3D orbit plots, distance-time plots |
| pandas | CSV report generation |
| GMAT R2022a | Independent verification of top conjunction events |
| Git | Version control |

## Results

Running on 500 recently-updated TLE objects from Space-Track.org:

- Objects propagated: 500
- MOID candidate pairs: 8,096 / 122,760 total pairs
- Conjunctions flagged (<5km): 130
- HIGH risk events (Pc > 1e-4): 103
- MONITOR events (1e-6 < Pc < 1e-4): 27
- Notable: CYGNUS NG-24 / PROGRESS MS-33 docking exclusion case identified
- Cross-operator conjunctions: Kuiper vs Starlink flagged
- Top Pc (excluding docked): 5.64e-3 (STARLINK-37109 vs STARLINK-37171)

## Visualization

SatTrack produces plots for the highest risk 3 conjunction events automatically. It is because there are over 130 conjunction events detected each time, and producing all plots will result in over 260 files.

To change how many conjunctions are visualized, edit this line in `main.py`:

```python
for top in results[:3]:  # change 3 to any number you want
```

| Value | Effect |
|---|---|
| `results[:3]` | Top 3 only — default, fastest |
| `results[:10]` | Top 10 — good balance |
| `results` | All conjunctions — slow, 260+ files |

Each conjunction generates two plots:
- **3D orbit plot** — both orbital paths around Earth with closest approach marked
- **Distance over time** — 7-day distance profile with closest approach and threshold marked

All plots are saved to the `outputs/` folder.



## Installation

```bash
git clone https://github.com/yourusername/SatTrack
cd SatTrack
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```
## Usage

**Download TLE catalog** from Space-Track.org (free account required):
- Login → Bulk Data → Full Catalog → 3LE format
- Save as `data/catalog.txt`

**Run the pipeline:**
```bash
python main.py
```

**Outputs generated in `outputs/`:**
- `conjunction_report.csv` — full ranked conjunction table
- `3d_*.png` — 3D orbit plots for top conjunctions
- `dist_*.png` — distance-over-time plots

## Configuration

In `main.py`, adjust these parameters:

| Parameter | Default | Effect |
|---|---|---|
| `limit` | 1000 | Number of satellites to screen |
| `max_age_days` | 30 | Maximum TLE age in days |
| `moid_threshold_km` | 10 | MOID pre-filter threshold |
| `conjunction_threshold_km` | 5 | Fine screening threshold |

## Known Limitations

These limitations are honestly documented and represent areas for future work:

**1. Simplified Alfano implementation**
Current implementation of Pc calculation uses a 1D Gaussian integral to approximate the 2D Alfano integration approach. To do that correctly, one needs to project the covariance matrix to the conjunction plane and integrate within a circular collision region. This may lead to a considerable underestimation of Pc values for some scenarios.

**2. Constant covariance assumption**
All objects are uniformly allocated a position uncertainty σ of 1.0 km irrespective of the age of the TLE, the quality of tracking, and orbit characteristics. Actual covariance matrices are anisotropic (radial uncertainties significantly smaller than along-track) and unique to each object.

**3. SGP4 accuracy degradation**
The SGP4 position error increases linearly with time since epoch, being around 1 km after one day and reaching 10-20 km after seven days. Late conjunctions identified within the seven-day period need to be regarded with less certainty. Higher-fidelity numerical propagation models are utilized in operations for further analysis of identified conjunctions.

**4. Monte Carlo sample size**
Monte Carlo Pc estimation takes into account 1000 samples. For real-life conjunctions in which Pc is less than 1e-4, this is not enough samples to accurately estimate Pc – there will be fewer than 0.1 collision samples on average. In order to accurately estimate Pc via Monte Carlo, more than 10^6 samples must be used.

**5. No relative velocity weighting**
Both Pc and impact outcome depend on the relative velocity of closest approach. High relative velocity (collision head-on, ∼15 km/s) creates more debris than low relative velocity (collision co-orbiting, ∼0.1 km/s). In this work, only Pc is calculated from positional data, without weighting for impact consequences.

## Project Structure

```
SatTrack/
├── data/
│   └── catalog.txt          # TLE catalog from Space-Track.org
├── src/
│   ├── init.py
│   ├── fetch_tles.py        # CelesTrak TLE downloader
│   ├── parse_tles.py        # TLE parser with age filter
│   ├── propagate.py         # SGP4 7-day orbit propagation
│   ├── moid.py              # MOID-based conjunction pre-filter
│   ├── screen.py            # Fine conjunction screening
│   ├── probability.py       # Alfano Pc + Monte Carlo
│   ├── visualize.py         # 3D plots + distance-time plots
│   └── report.py            # CSV report generator
├── gmat/
│   └── verify.script        # GMAT verification script
├── outputs/                 # Generated plots and reports
├── main.py                  # Pipeline runner
├── requirements.txt         # Python dependencies
└── README.md

```
## Background — Key Concepts

**TLE (Two-Line Element):** A standardized format for encoding a satellite's 
orbital state. Published by US Space Command via Space-Track.org. Accuracy 
degrades with age as unmodeled forces accumulate.

**SGP4:** Simplified General Perturbations 4. An analytical orbit propagator 
that accounts for Earth's oblateness, atmospheric drag, and solar/lunar 
perturbations via mathematical approximations. Standard for catalog-scale 
screening.

**MOID (Minimum Orbit Intersection Distance):** The minimum geometric 
distance between two orbital ellipses, independent of timing. Used as a 
pre-filter to eliminate pairs whose orbits can never come close.

**Conjunction:** An event where two space objects pass within a defined 
proximity threshold. Not necessarily a collision — depends on timing and 
position uncertainty.

**Pc (Collision Probability):** The probability that two objects physically 
collide given their nominal trajectories and position uncertainties. Standard 
maneuver threshold is 1×10⁻⁴ (NASA/ESA).

**Kessler Syndrome:** A cascading collision scenario where debris density in 
a given orbital regime becomes self-sustaining — each collision generates 
enough new debris to cause further collisions.

## References

- Alfano, S. (2005). *A Numerical Implementation of Spherical Object 
  Collision Probability*. Journal of the Astronautical Sciences.
- Vallado, D. (2013). *Fundamentals of Astrodynamics and Applications*. 
  Microcosm Press.
- Space-Track.org. https://www.space-track.org
- NASA CARA (Conjunction Assessment Risk Analysis). 
  https://cara.gsfc.nasa.gov

## Author

**Aryan Shirke**  
B.Tech Aerospace Engineering, KIIT University  
aryanshirke19@gmail.com  
linkedin.com/in/aryan-shirke-aeroeng