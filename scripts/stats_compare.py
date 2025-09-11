# scripts/stats_compare.py  — label fix + markdown summary
import argparse, json, csv
from pathlib import Path
import numpy as np
from scipy import stats

def load_vals(root: Path):
    vals, bad = [], []
    for f in root.glob("seed_*/metrics.json"):
        try:
            text = f.read_text(encoding="utf-8-sig")
            if not text.strip():
                bad.append((str(f), "empty file")); continue
            data = json.loads(text)
            if "final" not in data:
                bad.append((str(f), "missing 'final' key")); continue
            vals.append(data["final"])
        except Exception as e:
            bad.append((str(f), f"json error: {e}"))
    return vals, bad

def metric(list_of_dicts, key):
    return [d[key] for d in list_of_dicts if key in d]

def summarize(dir_path: Path):
    rows, bad = load_vals(dir_path)
    if bad:
        print(f"\n[WARN] Skipped in {dir_path}:")
        for p, r in bad:
            print(f" - {p}: {r}")
    if not rows:
        return None
    eff = metric(rows, "efficiency"); fair = metric(rows, "fairness")
    def mean_std(x):
        if len(x) == 0:
            return float("nan"), float("nan"), 0
        m = float(np.mean(x))
        s = float(np.std(x, ddof=1)) if len(x) > 1 else 0.0
        return m, s, len(x)
    eff_m, eff_s, n1 = mean_std(eff)
    fair_m, fair_s, n2 = mean_std(fair)
    return {"eff_mean":eff_m, "eff_std":eff_s, "fair_mean":fair_m, "fair_std":fair_s, "n":min(n1,n2)}

def algo_from_runs_path(p: Path) -> str:
    # Expect baselines/<algo>/runs  -> return <ALGO>
    # Or any */<algo>/runs
    if p.name.lower() == "runs":
        return p.parent.name.upper()
    return p.stem.upper()

def test_vs(care_dir: Path, base_dir: Path):
    C, _ = load_vals(care_dir); B, _ = load_vals(base_dir)
    out = {}
    for key in ["efficiency","fairness"]:
        A = [r[key] for r in C if key in r]
        D = [r[key] for r in B if key in r]
        if len(A) == 0 or len(D) == 0:
            out[key] = {"MWU_p": None, "WelchT_p": None}
            continue
        u, p_u = stats.mannwhitneyu(A, D, alternative="two-sided")
        t, p_t = stats.ttest_ind(A, D, equal_var=False)
        out[key] = {"MWU_p": p_u, "WelchT_p": p_t}
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--care", default="runs", help="CARE runs dir (default: runs)")
    ap.add_argument("--baselines", default="baselines/qmix/runs,baselines/vdn/runs,baselines/iql/runs,baselines/pf/runs")
    ap.add_argument("--out", default="stats.csv")
    ap.add_argument("--md", default="stats.md")
    args = ap.parse_args()

    care_dir = Path(args.care)
    baselines = [Path(p.strip()) for p in args.baselines.split(",")]

    care_sum = summarize(care_dir)
    if care_sum is None:
        print(f"[ERROR] No valid CARE results found in {care_dir}."); raise SystemExit(1)

    rows = []
    md_lines = [
        "# Baselines vs CARE — Statistical Summary\n",
        f"- CARE: efficiency={care_sum['eff_mean']:.3f}, fairness={care_sum['fair_mean']:.3f}, n={care_sum['n']}\n",
        "| Baseline | eff_mean | fair_mean | MWU_p_eff | WelchT_p_eff | MWU_p_fair | WelchT_p_fair | n_care | n_base |",
        "|-|-:|-:|-:|-:|-:|-:|-:|-:|",
    ]

    for b in baselines:
        if not b.exists():
            print(f"[WARN] Baseline path not found: {b}")
            continue
        base_sum = summarize(b)
        if base_sum is None:
            print(f"[WARN] No valid baseline results in: {b}")
            continue
        tests = test_vs(care_dir, b)
        algo = algo_from_runs_path(b)
        rows.append({
            "baseline": algo,
            "care_eff_mean": care_sum["eff_mean"],
            "base_eff_mean": base_sum["eff_mean"],
            "MWU_p_eff": tests["efficiency"]["MWU_p"],
            "WelchT_p_eff": tests["efficiency"]["WelchT_p"],
            "care_fair_mean": care_sum["fair_mean"],
            "base_fair_mean": base_sum["fair_mean"],
            "MWU_p_fair": tests["fairness"]["MWU_p"],
            "WelchT_p_fair": tests["fairness"]["WelchT_p"],
            "n_care": care_sum["n"], "n_base": base_sum["n"]
        })
        md_lines.append(
            f"| {algo} | {base_sum['eff_mean']:.3f} | {base_sum['fair_mean']:.3f} | "
            f"{tests['efficiency']['MWU_p']:.3g} | {tests['efficiency']['WelchT_p']:.3g} | "
            f"{tests['fairness']['MWU_p']:.3g} | {tests['fairness']['WelchT_p']:.3g} | "
            f"{care_sum['n']} | {base_sum['n']} |"
        )

    if not rows:
        print("[ERROR] No baseline rows to write. Make sure baseline runs exist and contain valid metrics."); raise SystemExit(1)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    Path(args.md).write_text("\n".join(md_lines), encoding="utf-8-sig")
    print(f"[OK] stats saved -> {args.out}")
    print(f"[OK] markdown -> {args.md}")
