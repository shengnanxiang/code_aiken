# -*- coding: utf-8 -*-
"""新 ID 关键区域放大 ASCII（玻璃组件/logo/缝/顶带）"""
import numpy as np
from PIL import Image
from pathlib import Path

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf")
gray = np.asarray(Image.open(BASE / "new id close.png").convert("L")).astype(np.float32)

def zoom(x0, y0, x1, y1, step=8, levels="0123456789"):
    reg = gray[y0:y1, x0:x1]
    lo, hi = np.percentile(reg, 2), np.percentile(reg, 98)
    norm = np.clip((reg - lo) / max(hi - lo, 1), 0, 1)
    print("     " + "".join(str(((x0 + x) // step // 2) % 10) for x in range(0, reg.shape[1] - step + 1, step)))
    for y in range(0, reg.shape[0] - step + 1, step):
        row = ""
        for x in range(0, reg.shape[1] - step + 1, step):
            v = norm[y:y+step, x:x+step].mean()
            row += levels[min(int(v * (len(levels)-1) + 0.5), len(levels)-1)]
        print(f"{y0+y:4d} {row}")

print("=== ZOOM: circular glass component area (x700-1050, y330-660) step=8 ===")
zoom(700, 330, 1050, 660, 8)
print("\n=== ZOOM: logo area new (x980-1420, y700-790) step=8 ===")
zoom(980, 700, 1420, 790, 8)
print("\n=== ZOOM: seam/parting area (x640-1400, y660-740) step=10 ===")
zoom(640, 660, 1400, 740, 10)
print("\n=== ZOOM: top band (x700-1500, y200-280) step=10 ===")
zoom(700, 200, 1500, 280, 10)
