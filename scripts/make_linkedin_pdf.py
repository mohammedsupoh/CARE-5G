#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

CANDIDATES = [
  "figs/banner_ar.png",
  "figs/pareto.png",
  "figs/conv_efficiency.png",
  "figs/conv_fairness.png",
  "figs/conv_satisfaction.png",
  "posts/table_ar.png"
]

imgs = [Path(p) for p in CANDIDATES if Path(p).exists()]
if not imgs:
    raise SystemExit("No input images found.\nExpected any of:\n" + "\n".join(CANDIDATES))

def to_rgb(p): return Image.open(p).convert("RGB")

pages = [to_rgb(str(p)) for p in imgs]
Path("posts").mkdir(exist_ok=True)
out = Path("posts/LinkedIn_CARE-5G_AR.pdf")
pages[0].save(out, save_all=True, append_images=pages[1:])
print(f"[OK] saved -> {out.resolve()}")
