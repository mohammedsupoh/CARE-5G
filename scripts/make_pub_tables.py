# scripts/make_pub_tables.py
import pandas as pd, numpy as np, os

def pct(x):
    return "—" if pd.isna(x) else f"{100*float(x):.1f}%"

def load_ci():
    df = pd.read_csv("reports/agg_ci.csv")
    df["Efficiency"]  = df.apply(lambda r: f"{pct(r.eff_mean)} [{pct(r.eff_lo)}, {pct(r.eff_hi)}]", axis=1)
    df["Fairness"]    = df.apply(lambda r: f"{pct(r.fair_mean)} [{pct(r.fair_lo)}, {pct(r.fair_hi)}]", axis=1)
    df["Satisfaction"]= df.apply(lambda r: f"{pct(r.sat_mean)} [{pct(r.sat_lo)}, {pct(r.sat_hi)}]", axis=1)
    df["Group"] = (df["group"].str.replace("^baselines:", "BL:", regex=True)
                             .str.replace("^runs:", "", regex=True))
    return df[["Group","n","Efficiency","Fairness","Satisfaction"]]

def load_fairness():
    # نحاول قراءة أكثر من ملف لو موجود (runs/baselines) ونجمعهم
    candidates = [p for p in [
        "reports/fairness_metrics.csv",
        "reports/fairness_runs.csv",
        "reports/fairness_baselines.csv",
    ] if os.path.isfile(p)]
    if not candidates:
        return pd.DataFrame()
    dfs = [pd.read_csv(p) for p in candidates]
    df = pd.concat(dfs, ignore_index=True)
    # اسم المجموعة = أول جزء قبل /seed_*
    grp = df["run"].astype(str).str.replace(r"[\\/].*$","", regex=True)
    df["Group"] = grp
    agg = df.groupby("Group", as_index=False).agg(
        n=("n","sum"),
        Jain=("jain","mean"),
        Gini=("gini","mean"),
        P5=("p5","mean")
    )
    agg["Jain"] = agg["Jain"].map(lambda v: f"{v:.3f}")
    agg["Gini"] = agg["Gini"].map(lambda v: f"{v:.3f}")
    agg["P5"]   = agg["P5"].map(lambda v: f"{v:.3f}")
    return agg[["Group","n","Jain","Gini","P5"]]

def write_tex_md(df, tex_path, md_path, caption, label):
    os.makedirs(os.path.dirname(tex_path), exist_ok=True)
    # Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {caption}\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n")
    # LaTeX (booktabs) — انتبه للأقواس المعقوفة
    cols = " ".join(["l"] + ["c"]*(df.shape[1]-1))
    lines = [
        r"\begin{table}[!t]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{" + cols + r"}",   # ← لا نستخدم f-string حول \begin{tabular}
        r"\toprule",
    ]
    lines.append(" & ".join(df.columns) + r" \\")
    lines.append(r"\midrule")
    for _,row in df.iterrows():
        lines.append(" & ".join(map(str,row.values)) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    ci = load_ci()
    write_tex_md(ci, "reports/table_agg_ci.tex", "reports/table_agg_ci.md",
                 "Aggregate across seeds (mean and 95\\% CI).", "tab:agg_ci")

    fair = load_fairness()
    if not fair.empty:
        write_tex_md(fair, "reports/table_fairness.tex", "reports/table_fairness.md",
                     "Fairness metrics per group (Jain, Gini, P5).", "tab:fairness")
    else:
        # أنشئ ملف MD فارغ للتوضيح إن لم تتوفر بيانات
        open("reports/table_fairness.md","w",encoding="utf-8").write("# Fairness metrics (no data)\n")

if __name__ == "__main__":
    main()
