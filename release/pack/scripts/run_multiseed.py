import subprocess
from pathlib import Path

SEEDS = [42, 123, 7, 2025, 99]
AGENTS = 60
EPISODES = 150

def run_one(seed):
    out = Path(f"runs/seed_{seed}")
    out.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python", "train.py",
        "--agents", str(AGENTS),
        "--episodes", str(EPISODES),
        "--seed", str(seed),
        "--out", str(out)
    ]
    print("▶", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    Path("runs").mkdir(exist_ok=True)
    for s in SEEDS:
        run_one(s)
    subprocess.check_call(["python", "scripts/aggregate.py"])

if __name__ == "__main__":
    main()
