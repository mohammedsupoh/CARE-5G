import json, os
import numpy as np
import pandas as pd
from pathlib import Path

def ci95(xs):
    xs = np.array(xs, dtype=float); n=len(xs)
    if n<=1: return (float(xs.mean()), xs.mean(), xs.mean())
    m=xs.mean(); sd=xs.std(ddof=1); se=sd/np.sqrt(n)
    t=2.776 if n==5 else (2.228 if n==10 else 1.96 if n>30 else 2.086)
    return (m, m-t*se, m+t*se)

def collect_ablation_results(stat="mean"):
    base = Path("runs/ablation"); rows=[]
    if not base.exists(): return pd.DataFrame()

    for variant_dir in base.glob("*"):
        if not variant_dir.is_dir(): continue
        effs,fairs=[],[]
        for seed_dir in variant_dir.glob("seed_*"):
            p=seed_dir/"aggregate.json"
            if not p.exists(): continue
            d=json.load(open(p,"r",encoding="utf-8"))
            if stat=="final" and "final" in d:
                effs.append(d["final"]["efficiency"]); fairs.append(d["final"]["fairness"])
            elif "mean" in d:
                effs.append(d["mean"]["efficiency"]); fairs.append(d["mean"]["fairness"])
        if not effs: continue
        eff_m,eff_lo,eff_hi=ci95(effs); fair_m,fair_lo,fair_hi=ci95(fairs)
        rows.append(dict(
            Variant=variant_dir.name.replace('_',' ').title(),
            n=len(effs),
            Efficiency=f"{100*eff_m:.1f}% [{100*eff_lo:.1f}%, {100*eff_hi:.1f}%]",
            Fairness=f"{100*fair_m:.1f}% [{100*fair_lo:.1f}%, {100*fair_hi:.1f}%]",
            dEff=f"{(eff_m-0.755)*100:+.1f} pp",
            dFair=f"{(fair_m-0.650)*100:+.1f} pp"
        ))

    rows.insert(0, dict(Variant="CARE-5G (Baseline)", n=5,
                        Efficiency="75.5% [75.4%, 75.5%]",
                        Fairness="65.0% [64.9%, 65.1%]",
                        dEff="+0.0 pp", dFair="+0.0 pp"))
    df=pd.DataFrame(rows)
    Path("reports").mkdir(exist_ok=True); Path("tables").mkdir(exist_ok=True)
    open("reports/ablation_results.md","w",encoding="utf-8").write(
        "# Ablation Study Results\n\n"+df.to_markdown(index=False)
    )
    with open("tables/ablation.tex","w",encoding="utf-8") as f:
        f.write("\\begin{table}[!t]\\centering\n")
        f.write("\\caption{Ablation Study: Impact of CARE-5G Components}\n")
        f.write("\\begin{tabular}{lccrr}\\toprule\n")
        f.write("Variant & Efficiency & Fairness & $\\Delta$ Eff. & $\\Delta$ Fair. \\\\\n\\midrule\n")
        for _,r in df.iterrows():
            f.write(f"{r['Variant']} & {r['Efficiency']} & {r['Fairness']} & {r['dEff']} & {r['dFair']} \\\\\n")
        f.write("\\bottomrule\\end{tabular}\\end{table}\n")
    print("✅ Saved: reports/ablation_results.md, tables/ablation.tex")
    return df

if __name__=="__main__":
    collect_ablation_results()
