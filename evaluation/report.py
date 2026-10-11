import sys
from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).resolve().parent.parent / "results"


def _order(methods):
    def key(m):
        if m.startswith("CPSAT@"):
            return (2, float(m[6:].split("s")[0]))
        if m.startswith("HYBRID@"):
            return (3, float(m[7:].split("s")[0]))
        return (0 if m in ("SPT", "MWKR", "FIFO") else 1, 0)
    return sorted(methods, key=key)


def head_to_head(wide, a, b):
    d = (wide[a] - wide[b]).dropna()
    return int((d < 0).sum()), int((d == 0).sum()), int((d > 0).sum())


def build_report(csv):
    df = pd.read_csv(csv)
    df["size"] = df["n_jobs"].astype(str) + "x" + df["n_machines"].astype(str)
    methods = _order(df["method"].unique())
    rl = next((m for m in methods if m.startswith("RL")), None)
    out = [f"# Benchmark report ({Path(csv).name})\n"]
    if rl and rl.startswith("RL(stub)"):
        out.append("WARNING: 'RL' here is the random STUB, not a trained agent.\n")

    gap = df.pivot_table(index="size", columns="method", values="gap", aggfunc="mean")[methods]
    tim = df.pivot_table(index="size", columns="method", values="solve_time", aggfunc="mean")[methods]
    cnt = df.groupby("size")["instance"].nunique()
    out += ["## Average gap to best known / best found (%)  (lower is better)",
            "```", gap.round(1).to_string(), "```", "(instances per size: "
            + ", ".join(f"{k}={v}" for k, v in cnt.items()) + ")\n",
            "## Average solve time (seconds)", "```", tim.round(3).to_string(), "```\n"]
    wide = df.pivot_table(index=["size", "instance"], columns="method", values="makespan")[methods]
    best = wide.min(axis=1)
    wins = (wide.eq(best, axis=0)).groupby(level="size").sum()
    out += ["## Wins per size (instances where the method matches the best makespan; ties count for all)",
            "```", wins.to_string(), "```\n"]

    if rl:
        flat = wide.reset_index().set_index("instance")
        out.append(f"## Head-to-head: {rl} vs each method (wins / ties / losses for {rl}, by makespan)")
        rows = []
        for size, g in flat.groupby("size"):
            row = {"size": size}
            for m in methods:
                if m != rl:
                    w, t, l = head_to_head(g, rl, m)
                    row[m] = f"{w}/{t}/{l}"
            rows.append(row)
        out += ["```", pd.DataFrame(rows).set_index("size").to_string(), "```\n"]
        cp = [m for m in methods if m.startswith("CPSAT@")]
        hy = [m for m in methods if m.startswith("HYBRID@")]
        if hy and cp:
            out.append("## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)")
            rows = []
            for size, g in flat.groupby("size"):
                tsz = tim.loc[size]
                for h in hy:
                    c = min(cp, key=lambda m: abs(tsz[m] - tsz[h]))    
                    w, t, l = head_to_head(g, h, c)
                    diff = (100 * (g[h] - g[c]) / g[c]).mean()
                    r_w, r_t, r_l = head_to_head(g, h, rl)
                    rows.append({"size": size, "hybrid": h, "avg time": round(tsz[h], 3),
                                 "vs CP-SAT": c, "its time": round(tsz[c], 3),
                                 "W/T/L": f"{w}/{t}/{l}", "mean diff %": round(diff, 2),
                                 "vs RL alone W/T/L": f"{r_w}/{r_t}/{r_l}"})
            out += ["```", pd.DataFrame(rows).set_index("size").to_string(), "```",
                    "(mean diff % < 0 means the hybrid has the shorter makespan)\n"]
        out.append("## Equal-budget reading guide")
        out.append(f"- {rl} average time: {df[df.method == rl]['solve_time'].mean():.3f}s. "
                   f"Compare it with the CP-SAT column whose limit is closest to that time "
                   f"(CP-SAT columns: {', '.join(cp) if cp else 'none - add --cpsat-limits 0.1,1,10,60'}).")
        out.append("- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.")
    return "\n".join(out)


def latest_csv():
    files = sorted(RESULTS.glob("benchmark_*.csv"))
    if not files:
        sys.exit("No benchmark CSV in results/. Run python -m evaluation.benchmark first.")
    return files[-1]


if __name__ == "__main__":
    csv = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_csv()
    text = build_report(csv)
    print(text)
    out = csv.with_name(f"report_{csv.stem}.md")
    out.write_text(text)
    print("\nSaved", out)