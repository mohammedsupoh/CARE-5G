import json, sys

TARGET_EFF = 0.80
TARGET_FAIR = 0.70

def main(pth):
    with open(pth, "r", encoding="utf-8") as f:
        data = json.load(f)
    eff = float(data["final"]["efficiency"])
    fair = float(data["final"]["fairness"])
    sat = float(data["final"].get("satisfaction", 0.0))
    conv = bool(data.get("converged", False))

    print("=== CARE Acceptance Check (Scarcity) ===")
    print(f"Efficiency:  {eff:.3f}  (target >= {TARGET_EFF:.2f})")
    print(f"Fairness:    {fair:.3f}  (target >= {TARGET_FAIR:.2f})")
    print(f"Satisfaction:{sat:.3f}  (secondary)")
    print(f"Converged:   {conv}")
    ok = (eff >= TARGET_EFF) and (fair >= TARGET_FAIR)
    print("\nRESULT:", "PASS ✅" if ok else "NEEDS TUNING ⚠️")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/testing_suite.py artifacts\\metrics.json")
        sys.exit(2)
    main(sys.argv[1])
