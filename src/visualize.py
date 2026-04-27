import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os

os.makedirs("outputs", exist_ok=True)

def plot_conjunction_3d(pos_A, pos_B, name_A, name_B, time_idx):
    fig = plt.figure(figsize=(12, 8))
    ax  = fig.add_subplot(111, projection="3d")
    R   = 6371
    u   = np.linspace(0, 2 * np.pi, 50)
    v   = np.linspace(0, np.pi, 50)
    xe  = R * np.outer(np.cos(u), np.sin(v))
    ye  = R * np.outer(np.sin(u), np.sin(v))
    ze  = R * np.outer(np.ones(50), np.cos(v))
    ax.plot_surface(xe, ye, ze, alpha=0.2, color="deepskyblue")

    def clean(p):
        mask = ~np.any(np.isnan(p), axis=1)
        return p[mask]

    cA = clean(pos_A)
    cB = clean(pos_B)

    ax.plot(cA[:,0], cA[:,1], cA[:,2],
            color="tomato", linewidth=0.8, label=f"{name_A} orbit", alpha=0.8)
    ax.plot(cB[:,0], cB[:,1], cB[:,2],
            color="limegreen", linewidth=0.8, label=f"{name_B} orbit", alpha=0.8)
    
    ax.scatter(*pos_A[time_idx], color="red",   s=80, zorder=5,
               label=f"{name_A} at TCA")
    ax.scatter(*pos_B[time_idx], color="green", s=80, zorder=5,
               label=f"{name_B} at TCA")

    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Z (km)")
    ax.set_title(f"Conjunction: {name_A} vs {name_B}")
    ax.legend(fontsize=8)

    tag  = f"{name_A[:8]}_{name_B[:8]}".replace(" ", "_")
    path = f"outputs/3d_{tag}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {path}")

def plot_distance_over_time(pos_A, pos_B, name_A, name_B, time_idx, threshold_km=5):
    diff      = pos_A - pos_B
    distances = np.linalg.norm(diff, axis=1)
    hours     = np.arange(len(distances)) / 60.0

    plt.figure(figsize=(13, 5))

    # labelled blue line
    plt.plot(hours, distances,
             color="steelblue", linewidth=0.8,
             label=f"Distance between {name_A} and {name_B}")

    plt.axvline(x=time_idx / 60, color="red",
                linestyle="--", label=f"Closest approach ({distances[time_idx]:.2f} km)")
    plt.axhline(y=threshold_km, color="orange",
                linestyle="--", label=f"Conjunction threshold ({threshold_km} km)")

    plt.xlabel("Time (hours from now)")
    plt.ylabel("Distance (km)")
    plt.title(f"Distance over time: {name_A} vs {name_B}")
    plt.legend()
    plt.grid(True, alpha=0.3)

    tag  = f"{name_A[:8]}_{name_B[:8]}".replace(" ", "_")
    path = f"outputs/dist_{tag}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {path}")

def plot_monte_carlo(pc_samples, name_A, name_B):
    plt.figure(figsize=(8, 5))
    plt.hist(pc_samples, bins=30, color="mediumpurple", edgecolor="black", alpha=0.7)
    plt.axvline(x=1e-4, color="red", linestyle="--", label="1e-4 alarm threshold")
    plt.xlabel("Collision Probability (Pc)")
    plt.ylabel("Frequency")
    plt.title(f"Monte Carlo Distribution\n{name_A} vs {name_B}")
    plt.legend()
    tag = f"{name_A[:8]}_{name_B[:8]}".replace(" ", "_")
    path = f"outputs/mc_{tag}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {path}")