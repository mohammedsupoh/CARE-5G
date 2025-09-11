#!/usr/bin/env python3
# scripts/make_latex_tables.py
import json, csv
from pathlib import Path

ALGOS = [("CARE","aggregate.json"),
         ("QMIX","baselines/qmix/aggregate.json"),
         ("VDN","baselines/vdn/aggregate.json"),
         ("IQL","baselines/iql/aggregate.json"),
         ("PF" ,"baselines/pf/aggregate.json")]

def load_agg(path):
    p = Path(path)
    if not p.exists(): return None
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    a = d.get("aggregate", d.get("aggregate", {}))
    return {
        "eff_m": a.get("efficiency_mean"),
        "eff_ci": a.get("efficiency_ci95"),
        "fair_m": a.get("fairness_mean"),
        "fair_ci": a.get("fairness_ci95"),
        "sat_m": a.get("satisfaction_mean"),
        "sat_ci": a.get("satisfaction_ci95"),
        "n": d.get("n_seeds")
    }

def fmt_ci(m, ci):
    if m is None or ci is None: return "--"
    return f"{m:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"

def make_table(rows):
    lines = []
    lines += [r"\begin{table}[t]", r"\centering", r"\caption{CARE vs. baselines under \textsc{Scarcity} (5 seeds). Means with 95\% CI.}",
              r"\label{tab:care_vs_baselines}",
              r"\begin{tabular}{lccc}", r"\toprule",
              r"\textbf{Algorithm} & \textbf{Efficiency} & \textbf{Fairness} & \textbf{Satisfaction} \\",
              r"\midrule"]
    for r in rows:
        lines += [fr"{r['algo']} & {fmt_ci(r['eff_m'], r['eff_ci'])} & {fmt_ci(r['fair_m'], r['fair_ci'])} & {fmt_ci(r['sat_m'], r['sat_ci'])} \\"]
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)

def make_summary_care(care):
    return "\n".join([
        r"\begin{tcolorbox}[colback=gray!3,colframe=gray!60,title=CARE Aggregate (5 seeds)]",
        fr"Efficiency = {fmt_ci(care['eff_m'], care['eff_ci'])}\\",
        fr"Fairness   = {fmt_ci(care['fair_m'], care['fair_ci'])}\\",
        fr"Satisfaction = {fmt_ci(care['sat_m'], care['sat_ci'])}",
        r"\end{tcolorbox}"
    ])

def make_caption_pareto():
    return r"""
\captionof{figure}{\textbf{Pareto: Efficiency vs. Fairness (95\% CI).} CARE sustains high efficiency while delivering substantially higher fairness than QMIX. PF attains borderline fairness with lower efficiency; VDN/IQL are dominated.}
"""

def read_stats_csv(path="stats.csv"):
    p = Path(path)
    if not p.exists(): return []
    rows=[]
    with p.open(encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        for row in r: rows.append(row)
    return rows

if __name__ == "__main__":
    rows=[]
    for name, path in ALGOS:
        agg = load_agg(path)
        if agg:
            agg["algo"] = name
            rows.append(agg)

    Path("tables").mkdir(exist_ok=True)
    if rows:
        Path("tables/comparison.tex").write_text(make_table(rows), encoding="utf-8")
        care = next((r for r in rows if r["algo"]=="CARE"), None)
        if care:
            Path("tables/metrics_summary.tex").write_text(make_summary_care(care), encoding="utf-8")
        Path("tables/pareto_caption.tex").write_text(make_caption_pareto(), encoding="utf-8")

    # (اختياري) اطبع ملخص p-values من stats.csv داخل الكونسول
    stats_rows = read_stats_csv()
    if stats_rows:
        print("\nP-values (MWU / Welch):")
        for r in stats_rows:
            print(f"- {r['baseline']}: eff {r['MWU_p_eff']} / {r['WelchT_p_eff']}, fair {r['MWU_p_fair']} / {r['WelchT_p_fair']}")
