# scripts/sanity_check_seeds.py  (improved seed detection + stats.csv fallback)
import os, json, glob, re
import numpy as np
import pandas as pd

def find_runs(root):
    return [os.path.dirname(p) for p in glob.glob(os.path.join(root, "**", "aggregate.json"), recursive=True)]

def pull_metrics(run_dir):
    # 1) aggregate.json
    agg_p = os.path.join(run_dir, "aggregate.json")
    if os.path.isfile(agg_p):
        try:
            agg = json.load(open(agg_p,"r",encoding="utf-8"))
            eff = next((agg[k] for k in ["efficiency_mean","efficiency","eff"] if k in agg), None)
            fair= next((agg[k] for k in ["fairness_mean","fairness","jain"] if k in agg), None)
            sat = next((agg[k] for k in ["satisfaction_mean","satisfaction","sat"] if k in agg), None)
            return eff, fair, sat
        except Exception:
            pass
    # 2) stats.csv fallback
    for cand in ["stats.csv","stats_summary.csv"]:
        p = os.path.join(run_dir, cand)
        if os.path.isfile(p):
            try:
                df = pd.read_csv(p)
                def pick(cols):
                    for c in df.columns:
                        if any(k in c.lower() for k in cols):
                            v = pd.to_numeric(df[c], errors="coerce").mean()
                            if np.isfinite(v): return float(v)
                    return None
                eff = pick(["efficiency","eff"])
                fair= pick(["fairness","jain"])
                sat = pick(["satisfaction","sat"])
                return eff, fair, sat
            except Exception:
                pass
    return None, None, None

def seed_from(run_dir):
    s=None
    m=re.search(r"(?:^|[/\\])seed[_-]?(\d+)(?:$|[/\\])", run_dir)
    if m: s=m.group(1)
    else:
        agg=os.path.join(run_dir,"aggregate.json")
        if os.path.isfile(agg):
            try:
                obj=json.load(open(agg,"r",encoding="utf-8"))
                for k in ["seed","random_seed","config.seed"]:
                    if k in obj:
                        s=str(obj[k]); break
            except Exception:
                pass
    return s or "UNK"

def main():
    roots = ["runs","baselines","runs/ablation"]
    for rt in roots:
        if not os.path.isdir(rt): 
            continue
        print(f"\n=== ROOT: {rt} ===")
        groups = {}
        for d in find_runs(rt):
            label = os.path.relpath(d, start=rt).split(os.sep)[0]
            eff,fair,sat = pull_metrics(d)
            s = seed_from(d)
            groups.setdefault(label, []).append((s, eff, fair, sat))
        for exp, rows in sorted(groups.items()):
            print(f"\n[EXP] {exp}")
            effs=[r[1] for r in rows if r[1] is not None]
            fairs=[r[2] for r in rows if r[2] is not None]
            sats=[r[3] for r in rows if r[3] is not None]
            for s, e, f, t in rows:
                print(f"  seed={s:>5}  eff={e}  fair={f}  sat={t}")
            def pr(name, vals):
                arr=np.array([v for v in vals if v is not None], dtype=float)
                if arr.size:
                    print(f"  {name}: mean={arr.mean():.6f} std={arr.std(ddof=1):.6f} min={arr.min():.6f} max={arr.max():.6f}")
                else:
                    print(f"  {name}: (no data)")
            pr("efficiency", effs); pr("fairness", fairs); pr("satisfaction", sats)
            if np.size(effs)>1 and np.std(effs, ddof=1)<1e-12:
                print("  [WARN] near-zero variance → تأكّد أنّ كل seed يكتب إلى مجلد مختلف وأنّ التمهيد يُمرَّر فعلياً.")
if __name__ == "__main__":
    main()
