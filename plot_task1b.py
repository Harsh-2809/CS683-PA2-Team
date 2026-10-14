import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Output directory
os.makedirs("results_task1", exist_ok=True)

# 2. Dataset from simulation logs
traces = ["Trace 1", "Trace 2", "Trace 3"]
x = np.arange(len(traces))
bar_w3 = 0.24  # Width for 3-group bar charts
bar_w2 = 0.30  # Width for 2-group bar charts

data = {
    "Trace": traces,
    # IPC
    "IPC_Baseline": [0.232176, 0.250030, 0.381887],
    "IPC_IP_Stride": [0.233332, 0.250179, 0.382819],
    "IPC_SPP": [0.234064, 0.251873, 0.389720],
    # Speedup
    "Speedup_Baseline": [1.0, 1.0, 1.0],
    "Speedup_IP_Stride": [
        0.233332 / 0.232176,
        0.250179 / 0.250030,
        0.382819 / 0.381887,
    ],
    "Speedup_SPP": [0.234064 / 0.232176, 0.251873 / 0.250030, 0.389720 / 0.381887],
    # L1D Load MPKI
    "MPKI_Baseline": [10.6789, 13.5404, 3.4034],
    "MPKI_IP_Stride": [10.1194, 13.4423, 3.3180],
    "MPKI_SPP": [9.6212, 13.1750, 2.8255],
    # Accuracy (%)
    "Accuracy_IP_Stride": [52.8968, 37.8086, 16.0800],
    "Accuracy_SPP": [52.2808, 43.6667, 39.9623],
    # Coverage (%) = (Misses_Base - Misses_Pref) / Misses_Base * 100
    "Coverage_IP_Stride": [
        (266973 - 252985) / 266973 * 100.0,
        (338509 - 336057) / 338509 * 100.0,
        (85085 - 82949) / 85085 * 100.0,
    ],
    "Coverage_SPP": [
        (266973 - 240530) / 266973 * 100.0,
        (338509 - 329374) / 338509 * 100.0,
        (85085 - 70637) / 85085 * 100.0,
    ],
}

# Save tabular CSV deliverable
df = pd.DataFrame(data)
df.to_csv("task1_results.csv", index=False)
print("Saved task1_results.csv successfully.")

# Styling configuration matching PDF
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1.2,
    }
)

# -------------------------------------------------------------------------
# Plot 1: Speedup of L1D Prefetchers over Baseline (PDF Page 6)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.axhline(
    1.0,
    color="#d9534f",
    linestyle="--",
    linewidth=1.2,
    label="Baseline",
    zorder=2,
)
ax.bar(
    x - bar_w2 / 2,
    df["Speedup_IP_Stride"],
    width=bar_w2,
    label="IP-stride",
    color="#6579bd",
    edgecolor="#3c4e85",
    zorder=3,
)
ax.bar(
    x + bar_w2 / 2,
    df["Speedup_SPP"],
    width=bar_w2,
    label="SPP",
    color="#88a9c3",
    edgecolor="#4b6b85",
    zorder=3,
)

ax.set_title(
    "Speedup of L1D Prefetchers over Baseline (no prefetching)",
    fontsize=12,
    fontweight="bold",
    pad=12,
)
ax.set_ylabel("Speedup", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(traces)
min_y = min(min(df["Speedup_IP_Stride"]), min(df["Speedup_SPP"]))
max_y = max(max(df["Speedup_IP_Stride"]), max(df["Speedup_SPP"]))
ax.set_ylim([max(0.8, np.floor(min_y * 10) / 10), np.ceil(max_y * 1.05 * 10) / 10])
ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
ax.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()
plt.savefig("task1_speedup.png")
plt.close()
print("Generated task1_speedup.png")

# -------------------------------------------------------------------------
# Plot 2: L1D Load MPKI (PDF Page 6)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.bar(
    x - bar_w3,
    df["MPKI_Baseline"],
    width=bar_w3,
    label="Baseline",
    color="#f28e8e",
    edgecolor="#b54f4f",
    zorder=3,
)
ax.bar(
    x,
    df["MPKI_IP_Stride"],
    width=bar_w3,
    label="IP-stride",
    color="#7ec8e3",
    edgecolor="#458da8",
    zorder=3,
)
ax.bar(
    x + bar_w3,
    df["MPKI_SPP"],
    width=bar_w3,
    label="SPP",
    color="#97d897",
    edgecolor="#529952",
    zorder=3,
)

ax.set_title(
    "L1D Load MPKI Comparison", fontsize=12, fontweight="bold", pad=12
)
ax.set_ylabel("L1D MPKI", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(traces)
ax.set_ylim([0, max(df["MPKI_Baseline"]) * 1.15])
ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
ax.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()
plt.savefig("task1_mpki.png")
plt.close()
print("Generated task1_mpki.png")

# -------------------------------------------------------------------------
# Plot 3: Prefetch Accuracy (%) (PDF Page 7)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.bar(
    x - bar_w2 / 2,
    df["Accuracy_IP_Stride"],
    width=bar_w2,
    label="IP-stride",
    color="#6579bd",
    edgecolor="#3c4e85",
    zorder=3,
)
ax.bar(
    x + bar_w2 / 2,
    df["Accuracy_SPP"],
    width=bar_w2,
    label="SPP",
    color="#88a9c3",
    edgecolor="#4b6b85",
    zorder=3,
)

ax.set_title(
    "L1D Prefetch Accuracy (%)", fontsize=12, fontweight="bold", pad=12
)
ax.set_ylabel("L1d Prefetch Accuracy (%)", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(traces)
ax.set_ylim([0, 100])
ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig("task1_accuracy.png")
plt.close()
print("Generated task1_accuracy.png")

# -------------------------------------------------------------------------
# Plot 4: Prefetch Coverage (%) (PDF Page 7)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.bar(
    x - bar_w2 / 2,
    df["Coverage_IP_Stride"],
    width=bar_w2,
    label="IP-stride",
    color="#6579bd",
    edgecolor="#3c4e85",
    zorder=3,
)
ax.bar(
    x + bar_w2 / 2,
    df["Coverage_SPP"],
    width=bar_w2,
    label="SPP",
    color="#88a9c3",
    edgecolor="#4b6b85",
    zorder=3,
)

ax.set_title(
    "L1D Prefetch Coverage (%)", fontsize=12, fontweight="bold", pad=12
)
ax.set_ylabel("L1d Prefetch Coverage (%)", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(traces)
ax.set_ylim([0, max(max(df["Coverage_SPP"]), 20) * 1.25])
ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig("task1_coverage.png")
plt.close()
print("Generated task1_coverage.png")

print(
    "\nAll 4 Task 1B figures and task1_results.csv have been generated successfully!"
)