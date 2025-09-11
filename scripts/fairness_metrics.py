# scripts/fairness_metrics.py
import argparse, os, re, glob, json
import pandas as pd
import numpy as np
from metrics_utils import jain_index, gini_coefficient, p5_percentile

CANDIDATE_PATTERNS = [
    "*per_agent*.csv", "*agent*metrics*.csv", "*per_user*.csv", "*allocations*.csv"
]
SAT_COL_CANDIDATES = ["satisfaction","sat","user_satisfaction","agent_satisfaction"]

def find_satisfaction_series(run_dir):
    # 1) CSVs with per-agent/-user satisfaction
    for pat in CANDIDATE_PATTERNS:
        for f in glob.glob(os.path.join(run_dir, "**", pat), recursive=True):
            try:
                df = pd.read_csv(f)
            except Exception:
                continue
            # pick a satisfaction column
            sat_col = None
            for c in df.columns:
                if c.strip().lower() in SAT_COL_CANDIDATES:
                    sat_col = c; break
            if sat_col is None:
                # try fuzzy match
                for c in df.columns:
                    if "satisf" in c.lower():
                        sat_col = c; break
            if sat_col is not None:
                vals = pd.to_numeric(df[sat_col], errors="coerce").dropna().values
                if len(vals) > 0:
                    return vals, f
    # 2) Try aggregate.json for embedded samples
    agg_json = os.path.join(run_dir, "aggregate.json")
    if os.path.isfile(agg_json):
        try:
            with open(agg_json, "r", encoding="utf-8") as fh:
                obj = json.load(fh)
            for key in ["satisfaction_samples","agent_satisfaction","per_agent_satisfaction"]:
                if key in obj and isinstance(obj[key], (list, tuple)):
                    vals = pd.to_numeric(pd.Series(obj[key]), errors="coerce").dropna().values
                    if len(vals) > 0:
                        return vals, agg_json
        except Exception:
            pass
    return np.array([]), None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="runs", help="Root directory to scan for runs")
    ap.add_argument("--out_csv", default="reports/fairness_metrics.csv")
    ap.add_argument("--out_md",  default="reports/fairness_metrics.md")
    args = ap.parse_args()

    rows = []
    for run_dir in sorted({os.path.dirname(p) for p in glob.glob(os.path.join(args.root, "**", "aggregate.json"), recursive=True)} 
                          | set(glob.glob(os.path.join(args.root, "*")))):
        if not os.path.isdir(run_dir): 
            continue
        vals, src = find_satisfaction_series(run_dir)
        run_id = os.path.relpath(run_dir, start=args.root)
        if len(vals) == 0:
            continue
        row = dict(
            run=run_id,
            n=len(vals),
            jain=jain_index(vals),
            gini=gini_coefficient(vals),
            p5=p5_percentile(vals),
            source=os.path.relpath(src, start=run_dir) if src else "N/A",
        )
        rows.append(row)

    if not rows:
        print("No satisfaction distributions found. Ensure per-agent CSVs or samples exist.")
        return

    df = pd.DataFrame(rows).sort_values(["run"])
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    df.to_csv(args.out_csv, index=False)

    # Markdown summary
    md = ["# Fairness Metrics (Jain, Gini, P5)",
          "",
          f"Total runs: **{len(df)}**",
          "",
          df.to_markdown(index=False)]
    with open(args.out_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))

    print(f"Wrote {args.out_csv}")
    print(f"Wrote {args.out_md}")

if __name__ == "__main__":
    main()
