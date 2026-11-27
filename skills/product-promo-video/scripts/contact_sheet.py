"""Tile all t*.png stills in a folder into one contact sheet (sorted by time), keeping their
aspect ratio: 3 per row for landscape, 4 per row for square or vertical frames.
Usage: python contact_sheet.py <stills-dir> [out.png]"""
import sys, glob, os
from PIL import Image
d = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, "sheet.png")
fs = sorted(glob.glob(os.path.join(d, "t*.png")), key=lambda f: float(os.path.basename(f)[1:-4].replace("_", ".")))
if not fs:
    sys.exit(f"No t*.png stills in {d}")
w0, h0 = Image.open(fs[0]).size
cols, gap = (3, 0) if w0 > h0 else (4, 10)
tw = 640 if w0 > h0 else 360
th = round(tw * h0 / w0)
ims = [Image.open(f).resize((tw, th)) for f in fs]
rows = (len(ims) + cols - 1) // cols
W = Image.new("RGB", (cols * tw + (cols - 1) * gap, rows * th + (rows - 1) * gap), "white")
for i, im in enumerate(ims): W.paste(im, ((i % cols) * (tw + gap), (i // cols) * (th + gap)))
W.save(out); print(out)
