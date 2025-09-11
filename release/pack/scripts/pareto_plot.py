# scripts/pareto_plot.py — robust skip
import json, math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

ALGOS = {
  "CARE": ("runs",),
  "QMIX": ("baselines","qmix","runs"),
  "VDN" : ("baselines","vdn","runs"),
  "IQL" : ("baselines","iql","runs"),
  "PF"  : ("baselines","pf","runs"),
}

def ci95(x):
    x = np.asarray(x, dtype=float)
    n = len(x); m = float(np.mean(x)) if n else float("nan")
    if n < 2 or np.std(x, ddof=1) == 0:
        return m, (m, m)
    sem = np.std(x, ddof=1)/np.sqrt(n)
    lo, hi = stats.t.interval(0.95, n-1, loc=m, scale=sem)
    return m, (float(lo), float(hi))

def load_metric(root: Path):
    vals=[]
    for f in root.glob("seed_*/metrics.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
            vals.append(d["final"])
        except Exception:
            continue
    if not vals: return None
    eff=[a["efficiency"] for a in vals if "efficiency" in a]
    fair=[a["fairness"]   for a in vals if "fairness"   in a]
    if not eff or not fair: return None
    (me, (le, he)) = ci95(eff); (mf, (lf, hf)) = ci95(fair)
    return (me, le, he), (mf, lf, hf)

if __name__=="__main__":
    plotted = 0
    plt.figure(figsize=(6,4))
    for name, parts in ALGOS.items():
        root = Path(*parts)
        if not root.exists(): 
            print(f"[WARN] missing: {root}")
            continue
        lm = load_metric(root)
        if lm is None:
            print(f"[WARN] no valid data in: {root}")
            continue
        (me, le, he), (mf, lf, hf) = lm
        plt.errorbar(me, mf, xerr=[[me-le],[he-me]], yerr=[[mf-lf],[hf-mf]], fmt='o', label=name)
        plotted += 1

    if plotted == 0:
        print("[ERROR] No points to plot.")
    else:
        plt.xlabel("Efficiency"); plt.ylabel("Fairness"); plt.title("Pareto: Efficiency vs Fairness (95% CI)")
        plt.grid(True, alpha=0.3); plt.legend()
        Path("figs").mkdir(exist_ok=True)
        out = Path("figs/pareto.png")
        plt.tight_layout(); plt.savefig(out, dpi=200)
        print(f"[OK] saved -> {out}")
