# -*- coding: utf-8 -*-
"""二轮定向分析: 主体检测/文字区/中心放大 ASCII/与项目调色板比对"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

SRC = Path(r"C:\Users\Nan\.jiuwenswarm\agent\sessions\web_1a13db569b6_ccb2c0c0ee76\uploads\微信图片_20261119120100_8963_486.jpg")
img = Image.open(SRC).convert("RGB")
W, H = img.size
img_np = np.asarray(img).astype(np.float32)
gray = np.asarray(Image.open(SRC).convert("L")).astype(np.float32)

# ---- 1) 显著主体检测 (对比度替代: 局部方差 + 暗亮差) ----
blur = cv2.GaussianBlur(gray, (0, 0), 15)
local_contrast = np.full_like(gray, 20.0)
step = 128
for y in range(0, H - step, step):
    for x in range(0, W - step, step):
        local_contrast[y:y+step, x:x+step] = gray[y:y+step, x:x+step].std()
th = (local_contrast > 45).astype(np.uint8) * 255
n, cc, st, cent = cv2.connectedComponentsWithStats(th, 8)
comps = sorted([tuple(st[i]) + (i,) for i in range(1, n)], key=lambda t: -t[4])
print("=== high-contrast components (x,y,w,h,area) top6 ===")
for c in comps[:6]:
    if c[4] > 5000:
        print(f"  bbox=({c[0]},{c[1]},{c[2]},{c[3]}) area={c[4]} relcenter=({(c[0]+c[2]/2)/W:.2f},{(c[1]+c[3]/2)/H:.2f})")

# ---- 2) 文字/高频小结构检测 (MSER 简化版: 高频局部方差热点) ----
lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.5), cv2.CV_32F)
hot = np.zeros_like(gray, bool)
step = 64
cells = []
for y in range(0, H - step, step):
    for x in range(0, W - step, step):
        v = lap[y:y+step, x:x+step].std()
        cells.append((v, x, y))
cells.sort(reverse=True)
print("\n=== top-12 high-frequency cells (可能文字/logo/细节区) ===")
for v, x, y in cells[:12]:
    print(f"  var={v:6.1f} at ({x},{y}) rel=({x/W:.2f},{y/H:.2f})")

# ---- 3) 中心 3x 放大 ASCII (主体区 1600-2900 x 1200-2600) ----
def zoom_ascii(g, x0, y0, x1, y1, step, levels="0123456789"):
    reg = g[y0:y1, x0:x1]
    lo, hi = np.percentile(reg, 2), np.percentile(reg, 98)
    norm = np.clip((reg - lo) / max(hi - lo, 1), 0, 1)
    hh, ww = norm.shape
    print("     " + "".join(str(((x0 + x) // step // 3) % 10) for x in range(0, ww - step + 1, step)))
    for y in range(0, hh - step + 1, step):
        row = ""
        for x in range(0, ww - step + 1, step):
            v = norm[y:y+step, x:x+step].mean()
            row += levels[min(int(v * (len(levels)-1) + 0.5), len(levels)-1)]
        print(f"{y0+y:4d} {row}")

print("\n=== center zoom (x1500-2900, y1100-2700, step=20) ===")
zoom_ascii(gray, 1500, 1100, 2900, 2700, 20)

# ---- 4) 上带 (y 0-1000) 细看: 是否有文字卡片/标注 ----
print("\n=== top band zoom (x0-4336, y0-900, step=48) ===")
zoom_ascii(gray, 0, 0, 4336, 900, 48)

# ---- 5) 项目调色板比对 (米色#D5D1CA/复古绿#535F3F/石墨灰系) ----
proj_palette = {"beige_D5D1CA": (213,209,202), "green_535F3F": (83,95,64),
                "graphite_1D1E21": (29,30,33), "graphite_585C5F": (88,92,95),
                "graphite_8996A9": (137,150,169)}
small = cv2.resize(img_np.astype(np.uint8), (W//8, H//8), interpolation=cv2.INTER_AREA).reshape(-1, 3).astype(np.float32)
print("\n=== project palette presence (dist<40 counts) ===")
for name, c in proj_palette.items():
    c = np.array(c, np.float32)
    d = np.linalg.norm(small - c[None, :], axis=1)
    print(f"  {name}: frac={float((d < 40).mean()):.4f}")
