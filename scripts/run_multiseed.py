# scripts/run_multiseed.py  — robust wrapper (Windows-friendly)
import argparse, os, sys, subprocess
from datetime import datetime

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--algo", required=True, help="Algorithm name, e.g., qmix/vdn/iql/pf/care")
    ap.add_argument("--agents", type=int, required=True)
    ap.add_argument("--episodes", type=int, required=True)
    ap.add_argument("--seeds", nargs="+", required=True, help="One or more seeds")
    ap.add_argument("--context", default="SCARCITY")
    ap.add_argument("--out", default=None, help="Base output folder")
    # أي وسائط إضافية نعيد تمريرها إلى train.py
    args, extras = ap.parse_known_args()

    py = sys.executable or "python"

    for s in args.seeds:
        seed_str = str(s)
        # مجلد الإخراج لكل seed
        if args.out:
            # لو المستخدم أعطى out لمجموعة Seeds، نضيف seed_<n>
            out_dir = args.out if len(args.seeds) == 1 else os.path.join(args.out, f"seed_{seed_str}")
        else:
            out_dir = os.path.join("runs", args.algo, f"seed_{seed_str}")
        ensure_dir(out_dir)

        # نبني الأمر الكامل لـ train.py مع تمرير algo/context/out
        cmd = [
            py, "train.py",
            "--algo", args.algo,
            "--agents", str(args.agents),
            "--episodes", str(args.episodes),
            "--seed", seed_str,
            "--context", args.context,
            "--out", out_dir,
        ] + extras

        log_path = os.path.join(out_dir, "train_log.txt")
        print(f">>> Running: {' '.join(cmd)}")
        print(f">>> Log   : {log_path}")
        with open(log_path, "w", encoding="utf-8") as log:
            log.write(f"[{datetime.now().isoformat()}] CMD: {' '.join(cmd)}\n")
            log.flush()
            # نستخدم returncode بدل raise لنستمر مع باقي البذور حتى لو فشل واحد
            proc = subprocess.Popen(cmd, stdout=log, stderr=log)
            rc = proc.wait()

        if rc != 0:
            print(f"[WARN] seed={seed_str} failed with rc={rc}. See {log_path}")
        else:
            print(f"[OK]   seed={seed_str} done -> {out_dir}")

if __name__ == "__main__":
    main()
