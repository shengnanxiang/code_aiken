# -*- coding: utf-8 -*-
"""五套 CMF 参考图 + 低奢金 + 关键历史探索 程序化对比读图"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf")
RECOLORS = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\aiken-recolors")

TARGETS = [
    ("灰绿-v1", BASE / "灰绿-v1.png"),
    ("石墨灰-v1", BASE / "石墨灰-v1.png"),
    ("岩石白-v1", BASE / "岩石白-v1.png"),
    ("熊猫-v2", BASE / "熊猫-v2.png"),
    ("低奢蓝-v4", BASE / "低奢蓝-v4.png"),
    ("newid-低奢金-c(用户自合成)", BASE / "新ID五配色" / "newid-低奢金-c.png"),
    # 历史潮向参照
    ("panda-cream(历史)", RECOLORS / "aiken-panda-cream.png"),
    ("panda-pink(历史)", RECOLORS / "aiken-panda-pink.png"),
    ("panda-navy(历史)", RECOLORS / "aiken-panda-navy.png"),
    ("panda-gold(历史)", RECOLORS / "aiken-panda-gold.png"),
]

print(f"{'name':32s} {'size':12s} clusters(top-5 by area)")
for name, path in TARGETS:
    if not path.exists():
        print(f"{name:32s} MISSING: {path}")
        continue
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    Z = lab.reshape(-1, 3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _r, labels, centers = cv2.kmeans(Z, 8, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    labels = labels.reshape(H, W)
    rows = []
    for k in range(8):
        m = labels == k
        frac = m.mean()
        rgb_m = img_np[m].mean(axis=0)
        hsv = cv2.cvtColor(np.array([[[int(rgb_m[0]), int(rgb_m[1]), int(rgb_m[2])]]], np.uint8), cv2.COLOR_RGB2HSV)[0, 0]
        rows.append((frac, rgb_m, hsv))
    rows.sort(key=lambda t: -t[0])
    print(f"\n{name}  {W}x{H}")
    for frac, rgb_m, hsv in rows[:6]:
        if frac < 0.01:
            continue
        print(f"  {frac*100:5.1f}%  #{int(rgb_m[0]):02X}{int(rgb_m[1]):02X}{int(rgb_m[2]):02X}  "
              f"H={int(hsv[0]):3d} S={int(hsv[1]):3d} V={int(hsv[2]):3d}")

# ---- 整体年龄语言指标: 饱和度分布(主体) ----
print("\n\n==== saturation / value stats (body = all non-bg clusters) ====")
for name, path in TARGETS[:6]:
    if not path.exists():
        continue
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    hsv = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    # 主体 = 距四角背景色远的像素
    corners = np.array([img_np[2,2], img_np[2,W-3], img_np[H-3,2], img_np[H-3,W-3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    body = dist > 40
    if body.sum() < 1000:
        continue
    s = hsv[:, :, 1][body] / 255
    v = hsv[:, :, 2][body] / 255
    # 彩色像素占比(S>0.15) 与高饱和占比(S>0.35)
    print(f"{name:32s} S_mean={s.mean():.3f} S_p90={np.percentile(s,90):.3f} "
          f"colored(S>0.15)={np.mean(s>0.15)*100:4.1f}% vivid(S>0.35)={np.mean(s>0.35)*100:4.1f}% "
          f"V_mean={v.mean():.3f} dark(V<0.25)={np.mean(v<0.25)*100:4.1f}%")

# ---- 新 ID 玻璃圆件特征提取(close): 圆(873,489)r~94 区域 vs 周围蒙皮 ----
print("\n\n==== new id close: circular glass component region stats ====")
img = Image.open(BASE / "new id close.png").convert("RGB")
img_np = np.asarray(img).astype(np.float32)
gray = np.asarray(Image.open(BASE / "new id close.png").convert("L")).astype(np.float32)
for (cx, cy, r) in [(873, 489, 88), (809, 484, 80)]:
    yy, xx = np.mgrid[0:gray.shape[0], 0:gray.shape[1]]
    disk = ((xx - cx) ** 2 + (yy - cy) ** 2) < r ** 2
    ring = (((xx - cx) ** 2 + (yy - cy) ** 2) < (r + 55) ** 2) & (((xx - cx) ** 2 + (yy - cy) ** 2) > (r + 12) ** 2)
    if disk.sum() > 100:
        rgb_m = img_np[disk].mean(axis=0)
        hsv = cv2.cvtColor(np.array([[[int(rgb_m[0]), int(rgb_m[1]), int(rgb_m[2])]]], np.uint8), cv2.COLOR_RGB2HSV)[0, 0]
        lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F)
        print(f"disk({cx},{cy},r{r}): n={disk.sum()} hex=#{int(rgb_m[0]):02X}{int(rgb_m[1]):02X}{int(rgb_m[2]):02X} "
              f"H={int(hsv[0])} S={int(hsv[1])} L={gray[disk].mean():.0f} Lsd={gray[disk].std():.1f} tex={lap[disk].std():.1f}")
    if ring.sum() > 100:
        rgb_r = img_np[ring].mean(axis=0)
        print(f"  ring around: hex=#{int(rgb_r[0]):02X}{int(rgb_r[1]):02X}{int(rgb_r[2]):02X} L={gray[ring].mean():.0f}")

# ---- 新 ID logo 区(缩小后) 与旧版尺寸对比 ----
print("\n==== logo size: new id vs old close ====")
old = np.asarray(Image.open(Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\design\aiken close.png")).convert("L")).astype(np.float32)
new = gray
# 旧 logo 区(首轮分析): x[798-1000]y[636-673] on 1373x826 -> 归一 (0.581-0.728, 0.770-0.814)
for nm, g, W_, H_ in [("old(1373x826)", old, old.shape[1], old.shape[0]), ("new(1810x978)", new, new.shape[1], new.shape[0])]:
    x0_, x1_ = int(0.56 * W_), int(0.76 * W_)
    y0_, y1_ = int(0.74 * H_), int(0.86 * H_)
    reg = g[y0_:y1_, x0_:x1_]
    lo = np.percentile(reg, 30)
    dark_logo = (reg < lo - 8)
    n_, cc_, st_, _ = cv2.connectedComponentsWithStats((dark_logo.astype(np.uint8)) * 255, 8)
    big = [(st_[i, 4], st_[i, 0] + x0_, st_[i, 1] + y0_, st_[i, 2], st_[i, 3]) for i in range(1, n_) if st_[i, 4] > 200]
    big.sort(reverse=True)
    print(f"{nm}: dark marks top3 = {[(a, f'({x},{y},{w},{h})') for a, x, y, w, h in big[:3]]}")
