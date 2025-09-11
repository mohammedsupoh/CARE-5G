#!/usr/bin/env python3
# scripts/make_banner.py
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def load_font(size):
    # نحاول خطوطًا شائعة، وإلا الخط الافتراضي
    for name in ["Arial.ttf", "arial.ttf", "DejaVuSans.ttf"]:
        try: return ImageFont.truetype(name, size)
        except: pass
    return ImageFont.load_default()

def make_banner(src, out, title, subtitle):
    img = Image.open(src).convert("RGBA")
    W, H = img.size

    # شريط غامق شفاف أسفل الصورة
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    bar_h = int(H*0.28)
    draw.rectangle([(0, H-bar_h), (W, H)], fill=(0,0,0,180))

    # نصوص
    title_font    = load_font(int(H*0.065))
    subtitle_font = load_font(int(H*0.038))

    # التفاف بسيط للسطر
    def draw_text_block(x, y, text, font, max_w, line_space=8):
        words = text.split()
        line = ""
        for w in words:
            test = (line+" "+w).strip()
            w_, h_ = draw.textbbox((0,0), test, font=font)[2:]
            if w_ > max_w and line:
                draw.text((x, y), line, font=font, fill=(255,255,255,230))
                y += h_ + line_space
                line = w
            else:
                line = test
        if line:
            draw.text((x, y), line, font=font, fill=(255,255,255,230))
        return y + h_

    pad = int(W*0.05)
    y0 = H - bar_h + int(bar_h*0.18)
    maxw = W - 2*pad

    # عنوان
    y1 = draw_text_block(pad, y0, title, title_font, maxw, line_space=10)
    # سطر فرعي
    draw_text_block(pad, y1+10, subtitle, subtitle_font, maxw, line_space=6)

    out.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(img, overlay).convert("RGB").save(out, quality=95)
    print(f"[OK] saved -> {out}")

if __name__ == "__main__":
    src = Path("figs/pareto.png")
    if not src.exists():
        raise SystemExit("ERROR: figs/pareto.png not found.")
    make_banner(
        src, Path("figs/banner_en.png"),
        "CARE-5G: Higher Fairness at High Efficiency",
        "Scientific Validation (n=5 seeds) • Pareto with 95% CI"
    )
    make_banner(
        src, Path("figs/banner_ar.png"),
        "CARE-5G: عدالة أعلى بكفاءة مرتفعة",
        "توثيق علمي (n=5 بذور) • Pareto مع 95% CI"
    )
