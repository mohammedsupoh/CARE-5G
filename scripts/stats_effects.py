#!/usr/bin/env python3
# scripts/stats_effects.py
import json, math, csv
from pathlib import Path
import numpy as np
from scipy import stats

BASELINES = [
    ("QMIX","baselines/qmix/runs"),
    ("VDN" ,"baselines/vdn/runs"),
    ("IQL" ,"baselines/iql/runs"),
    ("PF"  ,"baselines/pf/runs"),
]
CARE_DIR = Path("runs")

def load_vals(root: Path):
    vals=[]
    for f in root.glob("seed_*/metrics.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
            vals.append(d["final"])
        except Exception:
            pass
    return vals

def cliff_delta(A, D):
    # robust for small samples; O(n*m)
    n1, n2 = len(A), len(D)
    if n1==0 or n2==0: return math.nan
    n_greater = 0; n_less = 0
    for a in A:
        for b in D:
            if a > b: n_greater += 1
            elif a < b: n_less += 1
    delta = (n_greater - n_less) / (n1*n2)
    return float(delta)

def cohens_d(A, D):
    n1,n2=len(A),len(D)
    if n1<2 or n2<2: return math.nan, math.nan
    m1,m2 = float(np.mean(A)), float(np.mean(D))
    s1,s2 = float(np.std(A, ddof=1)), float(np.std(D, ddof=1))
    if s1==0 and s2==0: return math.nan, math.nan
    # pooled SD (unbiased)
    sp = math.sqrt(((n1-1)*s1*s1 + (n2-1)*s2*s2)/(n1+n2-2)) if (n1+n2-2)>0 else math.nan
    if sp==0 or math.isnan(sp): return math.nan, math.nan
    d = (m1 - m2)/sp
    # Hedges' g correction
    J = 1.0 - (3.0 / (4.0*(n1+n2) - 9.0)) if (n1+n2)>2 else 1.0
    g = d*J
    return float(d), float(g)

def holm_bonferroni(pvals):
    # return adjusted p-values in same order
    m = len(pvals)
    idx = np.argsort(pvals)
    adj = [None]*m
    prev = 0.0
    for rank, i in enumerate(idx, start=1):
        adj_p = pvals[i] * (m - rank + 1)
        adj_p = min(1.0, adj_p)
        # ensure monotonic non-decreasing when mapped back
        adj[i] = adj_p
    # optional monotonic pass
    for k in range(1,m):
        j = idx[k]; i = idx[k-1]
        adj[j] = max(adj[j], adj[i])
    return adj

def main():
    care = load_vals(CARE_DIR)
    if not care:
        print("[ERROR] No CARE runs found in runs/seed_*/metrics.json"); return 1

    out_rows = []
    families = {"eff_mwu":[], "fair_mwu":[], "eff_t":[], "fair_t":[]}

    for algo, path in BASELINES:
        base = load_vals(Path(path))
        if not base: 
            print(f"[WARN] No baseline data in: {path}")
            continue
        for metric, keyfam_mwu, keyfam_t in [("efficiency","eff_mwu","eff_t"), ("fairness","fair_mwu","fair_t")]:
            A = [r[metric] for r in care if metric in r]
            D = [r[metric] for r in base if metric in r]
            if not A or not D: 
                continue
            # tests
            u, p_mwu = stats.mannwhitneyu(A, D, alternative="two-sided")
            p_t = math.nan
            if len(A)>1 and len(D)>1 and (np.std(A, ddof=1)>0 or np.std(D, ddof=1)>0):
                p_t = stats.ttest_ind(A, D, equal_var=False).pvalue
            # effects
            delta = cliff_delta(A, D)
            d, g = cohens_d(A, D)
            out_rows.append({
                "baseline": algo, "metric": metric,
                "MWU_p": p_mwu, "WelchT_p": p_t,
                "Cliffs_delta": delta, "Cohens_d": d, "Hedges_g": g,
                "n_care": len(A), "n_base": len(D)
            })
            families[keyfam_mwu].append(p_mwu)
            if not math.isnan(p_t):
                families[keyfam_t].append(p_t)

    # adjust p-values per family
    fam_adj = {}
    for fam, ps in families.items():
        if ps:
            fam_adj[fam] = holm_bonferroni(ps)
        else:
            fam_adj[fam] = []

    # map adjusted back
    counters = {"eff_mwu":0,"fair_mwu":0,"eff_t":0,"fair_t":0}
    for r in out_rows:
        fam_key_mwu = "eff_mwu" if r["metric"]=="efficiency" else "fair_mwu"
        i = counters[fam_key_mwu]; counters[fam_key_mwu]+=1
        r["MWU_p_adj_holm"] = fam_adj[fam_key_mwu][i] if fam_adj[fam_key_mwu] else ""
        fam_key_t = "eff_t" if r["metric"]=="efficiency" else "fair_t"
        if not math.isnan(r["WelchT_p"]) and fam_adj[fam_key_t]:
            j = counters[fam_key_t]; counters[fam_key_t]+=1
            r["WelchT_p_adj_holm"] = fam_adj[fam_key_t][j]
        else:
            r["WelchT_p_adj_holm"] = ""

    # CSV
    if out_rows:
        with open("stats_effects.csv","w",newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            writer.writeheader(); writer.writerows(out_rows)
        # MD
        lines = ["# Effect sizes and adjusted p-values (Holm–Bonferroni)\n"]
        for r in out_rows:
            lines.append(f"- **{r['baseline']} / {r['metric']}**: MWU p={r['MWU_p']:.3g}"
                         + (f" (adj={r['MWU_p_adj_holm']:.3g})" if r['MWU_p_adj_holm']!="" else "")
                         + (f"; Welch p={r['WelchT_p']:.3g}" if not math.isnan(r['WelchT_p']) else "; Welch n/a")
                         + (f" (adj={r['WelchT_p_adj_holm']:.3g})" if r['WelchT_p_adj_holm']!="" else "")
                         + f"; Cliff's δ={r['Cliffs_delta']:.3f}"
                         + (f"; Cohen's d={r['Cohens_d']:.3f}" if not math.isnan(r['Cohens_d']) else "")
                         + (f" (Hedges' g={r['Hedges_g']:.3f})" if not math.isnan(r['Hedges_g']) else ""))
        Path("stats_effects.md").write_text("\n".join(lines), encoding="utf-8-sig")
        print("[OK] stats_effects.csv / stats_effects.md written.")
    else:
        print("[WARN] No rows produced.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
