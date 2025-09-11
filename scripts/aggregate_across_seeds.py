# scripts/aggregate_across_seeds.py
import os, glob, json
from pathlib import Path
import numpy as np
import pandas as pd
import argparse

def ci95(xs):
    xs = np.array(xs, dtype=float)
    n = len(xs)
    if n <= 1:
        m = float(xs.mean()) if n==1 else float("nan")
        return (m, m, m)
    m  = xs.mean()
    sd = xs.std(ddof=1)
    se = sd / np.sqrt(n)
    # t-approx; n=5 => 2.776
    t  = 2.776 if n==5 else (2.262 if n==8 else 2.086)
    return (m, m - t*se, m + t*se)

def extract_metrics(d):
    """Try multiple schema shapes for aggregate.json"""
    def pick(*paths):
        for p in paths:
            cur = d
            ok = True
            for k in p:
                if isinstance(cur, dict) and k in cur:
                    cur = cur[k]
                else:
                    ok = False; break
            if ok and isinstance(cur, (int,float)):
                return float(cur)
        return float("nan")

    eff = pick(['mean','efficiency'], ['metrics','mean','efficiency'], ['efficiency_mean'], ['final','efficiency'])
    fair= pick(['mean','fairness'],   ['metrics','mean','fairness'],   ['fairness_mean'],   ['final','fairness'])
    sat = pick(['mean','satisfaction'],['metrics','mean','satisfaction'],['satisfaction'], ['final','satisfaction'])
    return eff, fair, sat

def label_for(root, agg_path):
    rel   = os.path.relpath(os.path.dirname(agg_path), start=root)
    parts = rel.split(os.sep)
    if len(parts)>=2 and parts[0].lower()=='ablation':
        return f"ablation/{parts[1]}"
    return parts[0]

def build_table(roots):
    rows=[]
    for root in roots:
        root   = str(root)
        prefix = Path(root).name  # "runs" | "baselines" | custom
        for p in glob.glob(os.path.join(root, '**', 'aggregate.json'), recursive=True):
            # ✅ الشرط المطلوب: تجاهل أي ملف ليس تحت seed_*
            parent = Path(p).parent.name
            if not parent.startswith("seed_"):
                continue

            try:
                with open(p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
            except Exception:
                continue

            eff, fair, sat = extract_metrics(d)
            group = f"{prefix}:{label_for(root, p)}"
            rows.append(dict(group=group, eff=eff, fair=fair, sat=sat))

    if not rows:
        return pd.DataFrame(columns=['Group','n','Efficiency (mean [CI])','Fairness (mean [CI])','Satisfaction (mean [CI])'])

    df = pd.DataFrame(rows)
    out=[]
    for g, gdf in df.groupby('group'):
        n = len(gdf)
        def fmt(vals):
            vals = vals[~np.isnan(vals)]
            if len(vals)==0:
                return "N/A [N/A, N/A]"
            m, lo, hi = ci95(vals)
            return f"{m*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%]"
        out.append(dict(
            Group=g,
            n=n,
            **{
               'Efficiency (mean [CI])'  : fmt(gdf['eff'].to_numpy()),
               'Fairness (mean [CI])'    : fmt(gdf['fair'].to_numpy()),
               'Satisfaction (mean [CI])': fmt(gdf['sat'].to_numpy()),
            }
        ))
    res = pd.DataFrame(out).sort_values('Group').reset_index(drop=True)
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--roots', nargs='+', default=['runs','baselines'])
    ap.add_argument('--out_csv', default='reports/agg_ci.csv')
    ap.add_argument('--out_md',  default='reports/agg_ci.md')
    args = ap.parse_args()

    Path('reports').mkdir(exist_ok=True)
    res = build_table(args.roots)
    res.to_csv(args.out_csv, index=False)

    with open(args.out_md, 'w', encoding='utf-8') as f:
        f.write("# Aggregate across seeds (95% CI)\n\n")
        f.write(res.to_markdown(index=False))

    print(f"Wrote {args.out_csv}")
    print(f"Wrote {args.out_md}")

if __name__ == '__main__':
    main()
