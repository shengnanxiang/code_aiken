# -*- coding: utf-8 -*-
"""用户新上传图 (微信图片_20261119120100_8963_486.jpg, 4336x3804) 程序化分析"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

SRC = Path(r"C:\Users\Nan\.jiuwenswarm\agent\sessions\web_1a13db569b6_ccb2c0c0ee76\uploads\微信图片_20261119120100_8963_486.jpg")
OUT = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\design\ID\渲染图\石墨灰")

img = Image.open(SRC).convert("RGB")
W, H = img.size
img_np = np.asarray(img).astype(np.float32)
gray = np.asarray(Image.open(SRC).convert("L")).astype(np.float32)
print(f"size={W}x{H}  aspect={W/H:.3f}")

# ---- 亮度 ASCII 总览 (step=48) ----
def ascii_map(m, step, chars=" .:-=+*#%@"):
    hh, ww = m.shape
    for y in range(0, hh - step + 1, step):
        row = ""
        for x in range(0, ww - step + 1, step):
            v = m[y:y+step, x:x+step].mean() / 255
            row += chars[min(int(v * (len(chars)-1) + 0.5), len(chars)-1)]
        print(row)

print("\n=== luminance ASCII (step=48, 4336x3804 -> 90x79) ===")
ascii_map(gray, 48)

# ---- 色彩聚类 (k=8) ----
small = cv2.resize(img_np.astype(np.uint8), (W//4, H//4), interpolation=cv2.INTER_AREA)
lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
Z = lab.reshape(-1, 3)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
_ret, labels, centers = cv2.kmeans(Z, 8, None, crit, 6, cv2.KMEANS_PP_CENTERS)
labels = labels.reshape(small.shape[:2])
order = []
for k in range(8):
    m = labels == k
    rgb_mean = small[m].mean(axis=0)
    order.append((k, m.mean(), rgb_mean, m))
order.sort(key=lambda t: -t[1])
print("\n=== k-means 8 clusters ===")
for k, frac, rgb_mean, m in order:
    print(f"cluster {k}: frac={frac:.4f} hex=#{int(rgb_mean[0]):02X}{int(rgb_mean[1]):02X}{int(rgb_mean[2]):02X}")

# ---- 每象限色值 ----
print("\n=== quadrant mean hex ===")
for name, (ys, yh, xs_, xh) in {
    "top-left": (0, H//2, 0, W//2), "top-right": (0, H//2, W//2, W),
    "bottom-left": (H//2, H, 0, W//2), "bottom-right": (H//2, H, W//2, W),
    "center": (int(H*0.3), int(H*0.7), int(W*0.3), int(W*0.7))}.items():
    r = img_np[ys:yh, xs_:xh].mean(axis=(0,1))
    print(f"{name}: #{int(r[0]):02X}{int(r[1]):02X}{int(r[2]):02X}")

# ---- 聚类掩膜 ASCII (top 4 大簇) ----
print("\n=== top-4 cluster masks ASCII ===")
for k, frac, rgb, m in order[:4]:
    print(f"\n-- cluster {k} hex=#{int(rgb[0]):02X}{int(rgb[1]):02X}{int(rgb[2]):02X} frac={frac:.3f} --")
    m8 = (cv2.resize(m.astype(np.uint8), (W//4, H//4)) * 255)
    hh, ww = m8.shape
    step = 32
    for y in range(0, hh - step + 1, step):
        row = ""
        for x in range(0, ww - step + 1, step):
            v = m8[y:y+step, x:x+step].mean() / 255
            row += " .:-=+*#%@"[min(int(v * 9 + 0.5), 9)]
        print(row)

# ---- 边缘密度分布 ----
edges = cv2.Canny(np.asarray(gray, np.uint8), 40, 120)
print(f"\nCanny edge density = {edges.mean()/255:.5f}")
