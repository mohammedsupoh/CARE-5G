# scripts/run_baselines.py
import subprocess
from pathlib import Path

SEEDS = [42, 123, 7, 2025, 99]
AGENTS = 60
EPISODES = 150
ALGOS = ["qmix", "vdn", "iql", "pf"]   # CARE موجود مسبقًا في runs/
ALGO_FLAG = "--algo"                   # غيّره إذا لزم

def run_algo(algo):
    base = Path(f"baselines/{algo}/runs")
    base.mkdir(parents=True, exist_ok=True)
    for s in SEEDS:
        out = base / f"seed_{s}"
        out.mkdir(parents=True, exist_ok=True)
        cmd = ["python", "train.py", ALGO_FLAG, algo.upper(),
               "--agents", str(AGENTS), "--episodes", str(EPISODES),
               "--seed", str(s), "--out", str(out)]
        print("▶", " ".join(cmd))
        subprocess.check_call(cmd)

    # تجميع داخل مجلد البايسلاين (نستدعي aggregate.py مع cwd)
    subprocess.check_call(["python", "../../scripts/aggregate.py"], cwd=base.parent)

def main():
    for algo in ALGOS:
        run_algo(algo)

if __name__ == "__main__":
    main()
