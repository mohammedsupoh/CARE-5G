#!/usr/bin/env python3
# Aggregate multi-seed results with 95% confidence intervals

import json, math
import numpy as np
from pathlib import Path

try:
    from scipy import stats
except Exception:
    stats = None

def _read_results(runs_dir="runs"):
    results, seeds, bad = [], [], []
    for seed_dir in sorted(Path(runs_dir).glob("seed_*")):
        f = seed_dir / "metrics.json"
        if not f.exists() or f.stat().st_size == 0:
            bad.append((str(f), "missing/empty"))
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception as e:
            bad.append((str(f), f"json error: {e}"))
            continue
        if "final" not in data:
            bad.append((str(f), "missing 'final' key"))
            continue

        results.append(data["final"])
        try:
            seeds.append(int(seed_dir.name.split("_")[1]))
        except Exception:
            seeds.append(seed_dir.name)

    if bad:
        print("\n[WARN] Skipped files:")
        for path, reason in bad:
            print(f" - {path}: {reason}")

    return results, seeds

def _ci95_t(data):
    data = np.asarray(data, dtype=float)
    n = len(data)
    mean = float(np.mean(data))
    if n < 2 or np.std(data, ddof=1) == 0 or stats is None:
        return mean, (mean, mean)
    sem = float(np.std(data, ddof=1) / np.sqrt(n))
    lo, hi = stats.t.interval(0.95, n-1, loc=mean, scale=sem)
    return mean, (float(lo), float(hi))

def _ci95_bootstrap(data, n_boot=10000, seed=0):
    rng = np.random.default_rng(seed)
    data = np.asarray(data, dtype=float)
    if len(data) == 0:
        return math.nan, (math.nan, math.nan)
    boots = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(n_boot)]
    mean = float(np.mean(data))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return mean, (float(lo), float(hi))

def _safe_ci(data):
    mean_t, (lo_t, hi_t) = _ci95_t(data)
    if lo_t == hi_t:  # insufficient samples/variance or no scipy
        mean_b, (lo_b, hi_b) = _ci95_bootstrap(data)
        return mean_b, (lo_b, hi_b)
    return mean_t, (lo_t, hi_t)

def aggregate_results(runs_dir="runs"):
    results, seeds = _read_results(runs_dir)
    if not results:
        print("No results found! Expected runs/seed_*/metrics.json")
        return None

    eff = [r["efficiency"] for r in results if "efficiency" in r]
    fair = [r["fairness"]   for r in results if "fairness"   in r]
    satv = [r.get("satisfaction", float('nan')) for r in results]
    conv = [bool(r.get("converged", False)) for r in results]

    eff_mean, eff_ci = _safe_ci(eff)
    fair_mean, fair_ci = _safe_ci(fair)

    sat_clean = [x for x in satv if not (x is None or math.isnan(x))]
    if sat_clean:
        sat_mean, sat_ci = _safe_ci(sat_clean)
    else:
        sat_mean, sat_ci = math.nan, (math.nan, math.nan)

    aggregate = {
        "context": "SCARCITY",
        "agents": 60,
        "episodes": 150,
        "seeds": sorted(seeds),
        "n_seeds": len(seeds),
        "aggregate": {
            "efficiency_mean": round(eff_mean, 4),
            "efficiency_ci95": [round(eff_ci[0], 4), round(eff_ci[1], 4)],
            "fairness_mean": round(fair_mean, 4),
            "fairness_ci95": [round(fair_ci[0], 4), round(fair_ci[1], 4)],
            "satisfaction_mean": None if math.isnan(sat_mean) else round(sat_mean, 4),
            "satisfaction_ci95": None if (math.isnan(sat_ci[0]) or math.isnan(sat_ci[1])) else [round(sat_ci[0], 4), round(sat_ci[1], 4)],
            "converged_rate": float(sum(conv)) / len(conv) if conv else 0.0
        },
        "per_seed": results
    }

    with open("aggregate.json", "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)

    print(f"\nAGGREGATE RESULTS ({len(seeds)} seeds)")
    print("="*50)
    print(f"Efficiency: {eff_mean:.1%} [{eff_ci[0]:.1%}, {eff_ci[1]:.1%}]")
    print(f"Fairness  : {fair_mean:.1%} [{fair_ci[0]:.1%}, {fair_ci[1]:.1%}]")
    if not math.isnan(sat_mean):
        print(f"Satisfaction: {sat_mean:.1%}")
    print(f"Convergence Rate: {aggregate['aggregate']['converged_rate']:.0%}")
    print("="*50)

    if eff_ci[0] >= 0.80 and fair_ci[0] >= 0.70:
        print("SUCCESS: Both targets achieved with 95% confidence.")
    elif eff_mean >= 0.80 and fair_mean >= 0.70:
        print("PARTIAL: Means OK but CI needs improvement.")
    else:
        print("NEEDS IMPROVEMENT: Targets not achieved.")
    return aggregate

if __name__ == "__main__":
    aggregate_results()
