import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

RESULTS = Path(__file__).resolve().parent.parent / "results"

GAP_LABEL = "Average gap to best found (CP-SAT 60s) (%)"
COLORS = {"Rule": "#8C8C8C", "RL": "#4C78A8", "CP-SAT": "#E45756", "Hybrid (RL + CP-SAT)": "#8E5BB5"}


def _family(method):
    if method.startswith("CPSAT"):
        return "CP-SAT"
    if method.startswith("HYBRID"):
        return "Hybrid (RL + CP-SAT)"
    if method.startswith("RL"):
        return "RL"
    return "Rule"


def _summary(csv):
    df = pd.read_csv(csv)
    s = df.groupby("method").agg(gap=("gap", "mean"), time=("solve_time", "mean")).reset_index()
    s["family"] = s["method"].map(_family)
    return s


def bar_gap(csv, out=None):
    s = _summary(csv).sort_values("gap")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar(s["method"], s["gap"], color=[COLORS[f] for f in s["family"]])
    ax.bar_label(bars, fmt="%.1f%%", fontsize=9)
    ax.set_ylabel(GAP_LABEL)
    ax.set_title("Solution quality by method (lower is better)")
    ax.legend(handles=[Patch(color=c, label=f) for f, c in COLORS.items()], loc="upper left")
    plt.xticks(rotation=30, ha="right")
    fig.text(0.99, 0.01, "CPSAT@60s is the reference, so its gap is ~0 by construction",
             ha="right", va="bottom", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = Path(out) if out else RESULTS / "bar_gap.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out

_OFFSETS = {
    "FIFO": (8, 4), "SPT": (8, -12), "MWKR": (8, 6), "RL": (-6, 9),
    "RL-best20": (-10, -16), "CPSAT@0.25s": (6, 8), "CPSAT@0.5s": (6, 8),
    "CPSAT@1s": (8, 6), "CPSAT@5s": (6, 8), "CPSAT@10s": (6, 8), "CPSAT@60s": (-30, 10),
    "HYBRID@0.5s": (-82, -4), "HYBRID@1s": (8, -14), "HYBRID@5s": (-82, -4),
    "HYBRID@10s": (8, -14),
}


def gap_vs_time(csv, out=None):
    s = _summary(csv)
    s["time"] = s["time"].clip(lower=1e-3)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for fam, marker, line in (("CP-SAT", "o", True), ("Hybrid (RL + CP-SAT)", "s", True),
                              ("RL", "D", False), ("Rule", "o", False)):
        g = s[s["family"] == fam].sort_values("time")
        if g.empty:
            continue
        label = {"CP-SAT": "CP-SAT (0.25s to 60s)", "Hybrid (RL + CP-SAT)": "Hybrid: RL then CP-SAT (0.5s to 10s)",
                 "RL": "RL (greedy / best of 20)", "Rule": "Dispatch rules (SPT, MWKR, FIFO)"}[fam]
        if line:
            ax.plot(g["time"], g["gap"], marker + "-", color=COLORS[fam], label=label,
                    markersize=7, linewidth=1.6, zorder=3)
        else:
            ax.scatter(g["time"], g["gap"], s=70, marker=marker, color=COLORS[fam],
                       label=label, zorder=4)
    for _, r in s.iterrows():
        ax.annotate(r["method"], (r["time"], r["gap"]), textcoords="offset points",
                    xytext=_OFFSETS.get(r["method"], (6, 6)), fontsize=8.5)
    ax.set_xscale("log")
    ax.set_xlabel("Computation time per instance (seconds, log scale)")
    ax.set_ylabel(GAP_LABEL)
    ax.set_title("Quality vs time: lower-left is better")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    out = Path(out) if out else RESULTS / "gap_vs_time.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else max(RESULTS.glob("benchmark_*.csv"))
    print(bar_gap(csv))
    print(gap_vs_time(csv))