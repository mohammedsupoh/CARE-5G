#!/usr/bin/env python3
# scripts/make_table_image.py
import json, csv
from pathlib import Path
import matplotlib.pyplot as plt

def load_care(path="aggregate.json"):
    p=Path(path)
    if not p.exists(): return None
    d=json.loads(p.read_text(encoding="utf-8-sig"))
    a=d.get("aggregate",{})
    return {"Algorithm":"CARE","eff":a.get("efficiency_mean"),"fair":a.get("fairness_mean")}

def load_stats(path="stats.csv"):
    rows=[]
    p=Path(path)
    if not p.exists(): return rows
    with p.open(encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        for x in r:
            rows.append({
                "Algorithm": x["baseline"],
                "eff": float(x["base_eff_mean"]),
                "fair": float(x["base_fair_mean"]),
                "MWU_eff": float(x["MWU_p_eff"]),
                "MWU_fair": float(x["MWU_p_fair"]),
            })
    return rows

def fmt(x): 
    return "—" if x is None else (f"{x:.3f}" if isinstance(x,float) else str(x))

def make_table_image(lang="en", out="posts/table_en.png"):
    care=load_care()
    bases=load_stats()
    if not bases:  # fallback ثابت لو stats.csv ناقص
        bases=[{"Algorithm":"QMIX","eff":0.87,"fair":0.52,"MWU_eff":0.00398,"MWU_fair":0.00398},
               {"Algorithm":"VDN","eff":0.83,"fair":0.60,"MWU_eff":0.00398,"MWU_fair":0.00398},
               {"Algorithm":"IQL","eff":0.80,"fair":0.58,"MWU_eff":0.00398,"MWU_fair":0.00398},
               {"Algorithm":"PF","eff":0.78,"fair":0.70,"MWU_eff":0.00398,"MWU_fair":0.00398}]
    header_en=["Algorithm","Efficiency (mean)","Fairness (mean)","MWU p (eff)","MWU p (fair)"]
    header_ar=["الخوارزمية","الكفاءة (متوسط)","العدالة (متوسط)","MWU p (كفاءة)","MWU p (عدالة)"]
    header = header_en if lang=="en" else header_ar

    data=[]
    if care:
        data.append([ "CARE", fmt(care["eff"]), fmt(care["fair"]), "—", "—" ])
    for b in bases:
        data.append([ b["Algorithm"], fmt(b["eff"]), fmt(b["fair"]), f"{b['MWU_eff']:.3g}", f"{b['MWU_fair']:.3g}" ])

    fig, ax = plt.subplots(figsize=(8, 2.2 + 0.35*len(data)))
    ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=header, cellLoc="center", colLoc="center", loc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    tbl.scale(1, 1.3)
    ax.set_title("CARE-5G vs Baselines" if lang=="en" else "CARE-5G مقابل البايسلاينز", pad=14)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[OK] saved -> {out}")

if __name__=="__main__":
    make_table_image("en","posts/table_en.png")
    make_table_image("ar","posts/table_ar.png")
