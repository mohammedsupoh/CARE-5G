# scripts/plot_convergence.py
import json, math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

METRICS = ["efficiency", "fairness", "satisfaction"]

def load_histories(runs_dir="runs"):
    runs = []
    for f in Path(runs_dir).glob("seed_*/metrics.json"):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8-sig"))
            hist = d.get("history", {})
            # حوّل إلى قوائم float؛ تجاهل المفقود
            cleaned = {k: [float(x) for x in hist.get(k, [])] for k in METRICS}
            runs.append(cleaned)
        except Exception:
            continue
    return runs

def pad_to_same_length(seq_list):
    # بعض الـseeds قد تكون أقصر؛ نستخدم NaN padding ثم نأخذ mean مع nanpolicy
    L = max((len(s) for s in seq_list), default=0)
    out = np.full((len(seq_list), L), np.nan, dtype=float)
    for i, s in enumerate(seq_list):
        n = min(len(s), L); out[i, :n] = s[:n]
    return out  # shape = (n_seeds, L)

def mean_ci95(arr, axis=0):
    # arr يحوي NaN؛ نحسب على العناصر المتاحة فقط
    m = np.nanmean(arr, axis=axis)
    n = np.sum(~np.isnan(arr), axis=axis)
    sd = np.nanstd(arr, axis=axis, ddof=1)
    sem = np.where(n>1, sd/np.sqrt(n), np.nan)
    # t-interval؛ إن لم تتوفر عيّنات كافية، ترجع (m,m)
    lo = np.empty_like(m); hi = np.empty_like(m)
    for i in range(m.shape[0]):
        if n[i] and n[i] > 1 and not np.isnan(sem[i]):
            ci = stats.t.interval(0.95, int(n[i]-1), loc=m[i], scale=sem[i])
            lo[i], hi[i] = ci
        else:
            lo[i] = hi[i] = m[i]
    return m, lo, hi

def plot_metric(runs, metric, out_path):
    series = [r.get(metric, []) for r in runs if r.get(metric)]
    if not series:
        print(f"[WARN] no '{metric}' histories found; skipping")
        return
    arr = pad_to_same_length(series)
    mean, lo, hi = mean_ci95(arr, axis=0)
    x = np.arange(1, mean.shape[0]+1)

    plt.figure(figsize=(6,3.2))
    plt.plot(x, mean, label=f"{metric} (mean)")
    plt.fill_between(x, lo, hi, alpha=0.25, label="95% CI")
    plt.xlabel("Episode"); plt.ylabel(metric.capitalize()); plt.title(f"Convergence: {metric.capitalize()}")
    plt.grid(True, alpha=0.3); plt.legend()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(); plt.savefig(out_path, dpi=200)
    print(f"[OK] saved -> {out_path}")

if __name__ == "__main__":
    runs = load_histories("runs")
    if not runs:
        print("No histories found in runs/seed_*/metrics.json (missing 'history').")
    else:
        plot_metric(runs, "efficiency", "figs/conv_efficiency.png")
        plot_metric(runs, "fairness",   "figs/conv_fairness.png")
        plot_metric(runs, "satisfaction","figs/conv_satisfaction.png")
