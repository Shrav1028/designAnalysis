"""
Plot gem5 ablation study results from results_summary.csv
Run: python3 plot_results.py
If error try: pip install matplotlib pandas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

df = pd.read_csv("results_summary.csv")
os.makedirs("plots", exist_ok=True)

COLORS = {
    "basicmath": "#4C72B0",
    "fib":       "#DD8452",
}

# ── 1. Core Ablation: IPC bar chart ──────────────────────────────────────────
core_configs = ["baseline", "ras_only", "btb_only", "both"]
core_labels  = ["Baseline\n(no RAS, no BTB)", "RAS only", "BTB only", "Both enabled"]

fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(core_configs))
width = 0.35

for i, (binary, color) in enumerate(COLORS.items()):
    subset = df[df["binary"] == binary].set_index("config")
    ipcs   = [subset.loc[c, "ipc"] if c in subset.index else 0 for c in core_configs]
    bars   = ax.bar([xi + i * width for xi in x], ipcs, width, label=binary, color=color)
    for bar, val in zip(bars, ipcs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=8)

ax.set_xticks([xi + width/2 for xi in x])
ax.set_xticklabels(core_labels, fontsize=9)
ax.set_ylabel("IPC (Instructions Per Cycle)")
ax.set_title("Core Ablation: Impact of RAS and BTB on IPC")
ax.legend(loc="upper left")
ax.set_ylim(0, df["ipc"].max() * 1.15)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/1_core_ablation_ipc.png", dpi=150)
plt.close()
print("Saved plots/1_core_ablation_ipc.png")


# ── 2. Core Ablation: Mispredict rate bar chart ───────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

for i, (binary, color) in enumerate(COLORS.items()):
    subset = df[df["binary"] == binary].set_index("config")
    rates  = [subset.loc[c, "mispredict_rate"] * 100 if c in subset.index else 0
              for c in core_configs]
    bars   = ax.bar([xi + i * width for xi in x], rates, width, label=binary, color=color)
    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

ax.set_xticks([xi + width/2 for xi in x])
ax.set_xticklabels(core_labels, fontsize=9)
ax.set_ylabel("Misprediction Rate (%)")
ax.set_title("Core Ablation: Impact of RAS and BTB on Misprediction Rate")
ax.legend()
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/2_core_ablation_mispredict.png", dpi=150)
plt.close()
print("Saved plots/2_core_ablation_mispredict.png")


# ── 3. BTB Sweep: IPC vs BTB size ────────────────────────────────────────────
btb_configs = ["btb_1", "btb_16", "btb_64", "btb_256", "btb_1024", "btb_4096"]
btb_sizes   = [1, 16, 64, 256, 1024, 4096]

fig, ax = plt.subplots(figsize=(9, 5))

for binary, color in COLORS.items():
    subset = df[df["binary"] == binary].set_index("config")
    ipcs   = [subset.loc[c, "ipc"] if c in subset.index else None for c in btb_configs]
    ax.plot(btb_sizes, ipcs, marker="o", label=binary, color=color, linewidth=2)

ax.set_xscale("log", base=2)
ax.set_xlabel("BTB Entries (log2 scale)")
ax.set_ylabel("IPC")
ax.set_title("BTB Size Sweep: IPC vs Number of BTB Entries (RAS=16)")
ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax.set_xticks(btb_sizes)
ax.legend()
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/3_btb_sweep_ipc.png", dpi=150)
plt.close()
print("Saved plots/3_btb_sweep_ipc.png")


# ── 4. BTB Sweep: Mispredict rate vs BTB size ─────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

for binary, color in COLORS.items():
    subset = df[df["binary"] == binary].set_index("config")
    rates  = [subset.loc[c, "mispredict_rate"] * 100 if c in subset.index else None
              for c in btb_configs]
    ax.plot(btb_sizes, rates, marker="o", label=binary, color=color, linewidth=2)

ax.set_xscale("log", base=2)
ax.set_xlabel("BTB Entries (log2 scale)")
ax.set_ylabel("Misprediction Rate (%)")
ax.set_title("BTB Size Sweep: Misprediction Rate vs BTB Entries (RAS=16)")
ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax.set_xticks(btb_sizes)
ax.legend()
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/4_btb_sweep_mispredict.png", dpi=150)
plt.close()
print("Saved plots/4_btb_sweep_mispredict.png")


# ── 5. RAS Sweep: IPC vs RAS size ────────────────────────────────────────────
ras_configs = ["ras_0", "ras_4", "ras_8", "ras_16", "ras_32"]
ras_sizes   = [0, 4, 8, 16, 32]

fig, ax = plt.subplots(figsize=(9, 5))

for binary, color in COLORS.items():
    subset = df[df["binary"] == binary].set_index("config")
    ipcs   = [subset.loc[c, "ipc"] if c in subset.index else None for c in ras_configs]
    ax.plot(ras_sizes, ipcs, marker="o", label=binary, color=color, linewidth=2)

ax.set_xlabel("RAS Entries")
ax.set_ylabel("IPC")
ax.set_title("RAS Size Sweep: IPC vs Number of RAS Entries (BTB=4096)")
ax.set_xticks(ras_sizes)
ax.legend()
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/5_ras_sweep_ipc.png", dpi=150)
plt.close()
print("Saved plots/5_ras_sweep_ipc.png")


# ── 6. RAS Sweep: Mispredict rate vs RAS size ─────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

for binary, color in COLORS.items():
    subset = df[df["binary"] == binary].set_index("config")
    rates  = [subset.loc[c, "mispredict_rate"] * 100 if c in subset.index else None
              for c in ras_configs]
    ax.plot(ras_sizes, rates, marker="o", label=binary, color=color, linewidth=2)

ax.set_xlabel("RAS Entries")
ax.set_ylabel("Misprediction Rate (%)")
ax.set_title("RAS Size Sweep: Misprediction Rate vs RAS Entries (BTB=4096)")
ax.set_xticks(ras_sizes)
ax.legend()
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/6_ras_sweep_mispredict.png", dpi=150)
plt.close()
print("Saved plots/6_ras_sweep_mispredict.png")


# ── 7. L2 Cache: IPC comparison (both vs with_l2_cache) ──────────────────────
l2_configs = ["both", "with_l2_cache"]
l2_labels  = ["No L2 (L1 only)", "With L2 cache"]

fig, ax = plt.subplots(figsize=(7, 5))

for i, (binary, color) in enumerate(COLORS.items()):
    subset = df[df["binary"] == binary].set_index("config")
    ipcs   = [subset.loc[c, "ipc"] if c in subset.index else 0 for c in l2_configs]
    bars   = ax.bar([xi + i * width for xi in range(len(l2_configs))], ipcs, width, label=binary, color=color)
    for bar, val in zip(bars, ipcs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=8)

ax.set_xticks([xi + width/2 for xi in range(len(l2_configs))])
ax.set_xticklabels(l2_labels, fontsize=9)
ax.set_ylabel("IPC (Instructions Per Cycle)")
ax.set_title("L2 Cache Impact on IPC (RAS=16, BTB=4096)")
ax.legend(loc="upper left")
ax.set_ylim(0, df["ipc"].max() * 1.15)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("plots/7_l2_cache_ipc.png", dpi=150)
plt.close()
print("Saved plots/7_l2_cache_ipc.png")


print("\nAll plots saved to plots/")