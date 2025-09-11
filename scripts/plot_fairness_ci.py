# scripts/plot_fairness_ci.py
import os, glob, json, numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

GROUPS = [
  ("CARE-5G (BALANCE)", "runs/care_balance"),
  ("CARE-5G (ABUND.)",  "runs/care_abundance"),
  ("No Admission",      "runs/ablation/no_admission"),
  ("No Fairness Term",  "runs/ablation/no_fairness_term"),
  ("Two Stage",         "runs/ablation/two_stage"),
  ("QMIX",              "baselines/qmix"),
  ("VDN",               "baselines/vdn"),
  ("IQL",               "baselines/iql"),
  ("PF",                "baselines/pf"),
]

def pick(d, *paths):
    for p in paths:
        cur=d; ok=True
        for k in p:
            if isinstance(cur, dict) and k in cur: cur=cur[k]
            else: ok=False; break
        if ok and isinstance(cur,(int,float)): return float(cur)
    return float("nan")

def ci95(xs):
    xs=np.array(xs, float); n=len(xs)
    if n<=1: m=float(xs.mean()) if n==1 else np.nan; return m, m, m
    m=xs.mean(); sd=xs.std(ddof=1); se=sd/np.sqrt(n)
    t=2.776 if n==5 else 2.086
    return m, m-t*se, m+t*se

def collect_mean_ci(root):
    vals=[]
    for p in glob.glob(os.path.join(root,"seed_*","aggregate.json")):
        try:
            with open(p,"r",encoding="utf-8") as f: d=json.load(f)
        except Exception: continue
        fair = pick(d, ['mean','fairness'], ['metrics','mean','fairness'],
                       ['fairness_mean'], ['final','fairness'])
        if not np.isnan(fair): vals.append(fair)
    return ci95(vals), len(vals)

def main():
    rows=[]
    for label, root in GROUPS:
        (m,lo,hi), n = collect_mean_ci(root)
        if n==0: continue
        rows.append((label, m, lo, hi, n))
    # فرز تنازليًا حسب العدالة
    rows.sort(key=lambda x: x[1], reverse=True)

    labels=[r[0] for r in rows]
    means =[r[1]*100 for r in rows]
    err_lo=[(r[1]-r[2])*100 for r in rows]
    err_hi=[(r[3]-r[1])*100 for r in rows]
    errs=[err_lo, err_hi]

    plt.figure(figsize=(9.5,5.2))
    bars=plt.bar(range(len(rows)), means, yerr=errs, capsize=4)
    # تمييز CARE
    for i,l in enumerate(labels):
        if l.startswith("CARE-5G"): bars[i].set_hatch("//")
    plt.xticks(range(len(rows)), labels, rotation=20, ha='right')
    plt.ylabel("Fairness (%)")
    plt.title("Fairness (mean ± 95% CI) across groups")
    plt.tight_layout()
    Path("figs").mkdir(exist_ok=True)
    plt.savefig("figs/fairness_ci.png", dpi=300, bbox_inches="tight")
    plt.savefig("figs/fairness_ci.pdf", bbox_inches="tight")
    print("Saved figs/fairness_ci.png / .pdf")

if __name__=="__main__":
    main()
