# scripts/stats_effects_robust.py  (robust MWU + Cliff's δ + bootstrap, multi-root)
import glob, os, json, argparse, warnings
import numpy as np, pandas as pd
from itertools import combinations
from scipy.stats import mannwhitneyu

warnings.filterwarnings("ignore", category=RuntimeWarning)

def cliffs_delta(a,b):
    a=np.asarray(a); b=np.asarray(b)
    gt=0; lt=0
    for x in a:
        gt += np.sum(x>b)
        lt += np.sum(x<b)
    n1=len(a); n2=len(b)
    return (gt-lt)/(n1*n2) if n1>0 and n2>0 else np.nan

def bootstrap_ci(x,y,stat=np.mean, B=10000, alpha=0.05, seed=123):
    rng=np.random.default_rng(seed)
    x=np.asarray(x); y=np.asarray(y)
    diffs=[]
    for _ in range(B):
        xb=rng.choice(x, size=len(x), replace=True)
        yb=rng.choice(y, size=len(y), replace=True)
        diffs.append(stat(xb)-stat(yb))
    lo, hi = np.quantile(diffs, [alpha/2, 1-alpha/2])
    return float(lo), float(hi)

def holm_bonferroni(pvals):
    if len(pvals)==0: return []
    order=np.argsort(pvals); m=len(pvals); adj=np.empty(m)
    cur=0.0
    for i,idx in enumerate(order):
        adj_p=(m-i)*pvals[idx]
        cur=max(cur, adj_p) if i>0 else adj_p
        adj[idx]=min(cur,1.0)
    return adj

def load_metric_from_agg(run_dir, key):
    p=os.path.join(run_dir,"aggregate.json")
    if not os.path.isfile(p): return None
    try:
        agg=json.load(open(p,"r",encoding="utf-8"))
    except Exception:
        return None
    for k in (f"{key}_samples", key, f"{key}_mean"):
        if k in agg:
            v=agg[k]
            if isinstance(v, list):
                arr=np.array(v, dtype=float); 
                if arr.size: return arr
            else:
                return np.array([float(v)])
    return None

def collect_groups(roots, metric):
    groups={}
    for root in roots:
        for p in glob.glob(os.path.join(root,"**","aggregate.json"), recursive=True):
            run_dir=os.path.dirname(p)
            label=os.path.relpath(run_dir, start=root).split(os.sep)[0]  # أول مجلد (algo/exp)
            vals=load_metric_from_agg(run_dir, metric)
            if vals is None: 
                continue
            groups.setdefault(label, []).append(float(np.mean(vals)))
    # إلى مصفوفات
    for k in list(groups.keys()):
        groups[k]=np.array(groups[k], dtype=float)
    return groups

def write_md(df, out_md):
    try:
        md = ["# Robust effects (MWU + Cliff's δ + bootstrap CI)", df.to_markdown(index=False)]
    except Exception:
        # Fallback نصي بسيط إن لم تتوفر tabulate
        header = "| " + " | ".join(df.columns) + " |"
        sep    = "| " + " | ".join(["---"]*len(df.columns)) + " |"
        lines  = [header, sep]
        for _,row in df.iterrows():
            lines.append("| " + " | ".join(str(x) for x in row.values) + " |")
        md = ["# Robust effects (fallback table)", *lines]
    with open(out_md,"w",encoding="utf-8") as f: f.write("\n".join(md))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["runs"], help="one or more roots, e.g., runs baselines")
    ap.add_argument("--metric", default="efficiency", choices=["efficiency","fairness","satisfaction"])
    ap.add_argument("--out_csv", default="reports/stats_effects_robust.csv")
    ap.add_argument("--out_md",  default="reports/stats_effects_robust.md")
    args=ap.parse_args()

    groups=collect_groups(args.roots, args.metric)
    labels=sorted(groups.keys())
    rows=[]
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            x=groups.get(a, np.array([])); y=groups.get(b, np.array([]))
            if len(x)<2 or len(y)<2:
                p=np.nan; test="insufficient-n"
            else:
                p=float(mannwhitneyu(x,y, alternative="two-sided", method="auto").pvalue); test="MWU"
            d=cliffs_delta(x,y)
            lo,hi = (bootstrap_ci(x,y) if len(x)>0 and len(y)>0 else (np.nan,np.nan))
            rows.append(dict(metric=args.metric, A=a, B=b, nA=len(x), nB=len(y),
                             A_mean=(np.mean(x) if len(x) else np.nan),
                             B_mean=(np.mean(y) if len(y) else np.nan),
                             cliffs_delta=d, boot_CI_lo=lo, boot_CI_hi=hi, p_raw=p, test=test))
    df=pd.DataFrame(rows)
    if not df.empty:
        df["p_holm"]=holm_bonferroni(df["p_raw"].fillna(1.0).values)
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    write_md(df, args.out_md)
    print(f"Wrote {args.out_csv} / {args.out_md}")
if __name__=="__main__":
    main()
