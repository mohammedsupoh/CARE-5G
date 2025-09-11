# scripts/heatmap_sensitivity.py
import argparse, os, re, glob, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from metrics_utils import jain_index

def parse_lr_eps(path):
    # Accept .../lr_0.001/eps_0.995 or .../eps_0.995/lr_0.001
    m1 = re.search(r"lr_([-\deE\.]+)", path.replace("\\","/"))
    m2 = re.search(r"eps_([-\deE\.]+)", path.replace("\\","/"))
    if not (m1 and m2): 
        return None
    return float(m1.group(1)), float(m2.group(1))

def read_metric_files(d):
    # Try aggregate.json then stats.csv
    agg = os.path.join(d, "aggregate.json")
    if os.path.isfile(agg):
        try:
            with open(agg, "r", encoding="utf-8") as fh:
                obj = json.load(fh)
            eff = obj.get("efficiency_mean", obj.get("efficiency", np.nan))
            fair = obj.get("fairness_mean", obj.get("fairness", np.nan))
            return eff, fair, obj
        except Exception:
            pass
    for cand in ["stats.csv","stats_summary.csv"]:
        p = os.path.join(d, cand)
        if os.path.isfile(p):
            try:
                df = pd.read_csv(p)
                # try common column names
                eff = None; fair = None
                for c in df.columns:
                    lc = c.lower()
                    if eff is None and ("efficiency" in lc or lc == "eff"):
                        eff = pd.to_numeric(df[c], errors="coerce").mean()
                    if fair is None and ("fairness" in lc or "jain" in lc):
                        fair = pd.to_numeric(df[c], errors="coerce").mean()
                return eff, fair, None
            except Exception:
                pass
    return np.nan, np.nan, None

def maybe_compute_fairness_from_agents(d):
    # try to find per-agent satisfaction to compute Jain
    for pat in ["*per_agent*.csv","*agent*metrics*.csv","*per_user*.csv","*allocations*.csv"]:
        for f in glob.glob(os.path.join(d, "**", pat), recursive=True):
            try:
                df = pd.read_csv(f)
            except Exception:
                continue
            cand = None
            for c in df.columns:
                if "satisf" in c.lower():
                    cand = c; break
            if cand is not None:
                vals = pd.to_numeric(df[cand], errors="coerce").dropna().values
                if len(vals) > 0:
                    return jain_index(vals)
    return np.nan

def plot_heat(df_pivot, title, out_png):
    fig = plt.figure(figsize=(7, 5))
    data = df_pivot.values
    plt.imshow(data, origin="lower", aspect="auto")
    plt.xticks(range(df_pivot.shape[1]), [f"{c:g}" for c in df_pivot.columns], rotation=45, ha="right")
    plt.yticks(range(df_pivot.shape[0]), [f"{r:g}" for r in df_pivot.index])
    plt.xlabel("epsilon-decay"); plt.ylabel("learning rate")
    plt.title(title)
    # annotate cells
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isnan(val):
                plt.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)
    plt.colorbar()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="runs/sensitivity")
    ap.add_argument("--out_dir", default="reports")
    ap.add_argument("--fig_dir", default="figs")
    args = ap.parse_args()

    rows = []
    for d in glob.glob(os.path.join(args.root, "**"), recursive=True):
        if not os.path.isdir(d): 
            continue
        parsed = parse_lr_eps(d)
        if not parsed: 
            continue
        lr, eps = parsed
        eff, fair, obj = read_metric_files(d)
        if (np.isnan(fair) or fair is None):
            fair = maybe_compute_fairness_from_agents(d)
        rows.append(dict(lr=lr, eps=eps, efficiency=eff, fairness=fair, path=d))

    if not rows:
        print("No sensitivity folders found. Expect structure like runs/sensitivity/lr_0.001/eps_0.995/...")
        return

    df = pd.DataFrame(rows)
    # Pivots
    piv_eff  = df.pivot_table(index="lr", columns="eps", values="efficiency", aggfunc="mean")
    piv_fair = df.pivot_table(index="lr", columns="eps", values="fairness",  aggfunc="mean")

    os.makedirs(args.out_dir, exist_ok=True)
    piv_eff.to_csv(os.path.join(args.out_dir, "sensitivity_efficiency.csv"))
    piv_fair.to_csv(os.path.join(args.out_dir, "sensitivity_fairness.csv"))

    os.makedirs(args.fig_dir, exist_ok=True)
    plot_heat(piv_eff,  "Efficiency Heatmap (lr × eps-decay)", os.path.join(args.fig_dir, "sensitivity_efficiency.png"))
    plot_heat(piv_fair, "Fairness (Jain) Heatmap (lr × eps-decay)", os.path.join(args.fig_dir, "sensitivity_fairness.png"))

    print("Done. CSVs in reports/, PNGs in figs/.")
if __name__ == "__main__":
    main()
