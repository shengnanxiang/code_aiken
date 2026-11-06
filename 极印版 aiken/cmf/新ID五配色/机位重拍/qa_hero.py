# -*- coding: utf-8 -*-
"""hero 机位图最终 QA：对照 baseline_data.json 做 5 项检测
1. 俯侧视角特征（顶面可见性=主体高度增长 & 上部明度带）
2. 双圆件 Hough 检出 + r/机身高比对比
3. 接地投影存在性（主体底部下方暗带检测）
4. 透视漂移量化（body aspect / bbox 填充 / 圆件归一位置偏移）
5. 蒙皮占比 + 主色对比（hex 距离）
"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
import json

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色\机位重拍")
BL = json.load(open(BASE / "baseline" / "baseline_data.json", encoding="utf-8"))

TARGETS = [
    ("close", "newid-低奢金-c_hero.png"),
    ("close", "newid-低奢金-c_hero_alt.png"),
    ("open", "newid-低奢金-open_hero.png"),
    ("open", "newid-低奢金-open_hero_alt.png"),
]

def hexdist(h1, h2):
    a = np.array([int(h1[i:i+2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i:i+2], 16) for i in (1, 3, 5)], float)
    d = a - b
    return float(np.sqrt(float(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)))

results = []
for tag, fname in TARGETS:
    path = BASE / fname
    if not path.exists():
        print(f"MISSING: {fname}")
        continue
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    bl = BL[tag]

    # ---- 主体掩膜 ----
    corners = np.array([img_np[2, 2], img_np[2, W - 3], img_np[H - 3, 2], img_np[H - 3, W - 3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    fg = (dist > 30).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    main = cc == (1 + int(np.argmax(areas)))
    x0, y0, w0, h0 = st[1 + int(np.argmax(areas)), :4]
    fill = main.sum() / (w0 * h0)

    # ---- 1) 俯侧视角: 顶面可见性 ----
    # 俯视时主体高/宽比增大(顶带可见), 且主体上部出现水平走向亮带(顶面受光)
    aspect = w0 / h0
    bl_aspect = bl["body_aspect"]
    top_band = main[y0:y0 + int(h0 * 0.25), :]
    top_L = gray[y0:y0 + int(h0 * 0.25), :][main[y0:y0 + int(h0 * 0.25), :]].mean() if top_band.any() else 0
    mid_L = gray[y0 + int(h0 * 0.4):y0 + int(h0 * 0.6), :][main[y0 + int(h0 * 0.4):y0 + int(h0 * 0.6), :]].mean()

    # ---- 2) 双圆件 Hough ----
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=50,
                               param1=90, param2=42, minRadius=int(h0 * 0.08), maxRadius=int(h0 * 0.45))
    found = []
    if circles is not None:
        for c in circles[0][:12]:
            cx, cy, r = c
            if main[int(np.clip(cy, 0, H - 1)), int(np.clip(cx, 0, W - 1))]:
                found.append((float(cx), float(cy), float(r)))
    # 与基线圆匹配（按 r/h0 比例 + 归一位置就近）
    match_report = []
    for bc in bl["circles"]:
        best = None
        for (cx, cy, r) in found:
            d = np.hypot(cx / W - bc["cx_rel"], cy / H - bc["cy_rel"])
            rr = r / h0
            if d < 0.25 and abs(rr - bc["r_rel_bodyH"]) < 0.15:
                score = d + abs(rr - bc["r_rel_bodyH"])
                if best is None or score < best[0]:
                    best = (score, cx, cy, r, d, rr)
        if best:
            _, cx, cy, r, d, rr = best
            match_report.append({
                "ref": bc["id"], "found": [round(cx), round(cy), round(r)],
                "pos_offset_rel": round(float(d), 4),
                "r_ratio_found": round(float(rr), 4), "r_ratio_base": bc["r_rel_bodyH"],
            })
        else:
            match_report.append({"ref": bc["id"], "found": None})

    # ---- 3) 接地投影 ----
    # 主体底部下方 5-15% 高度带, 检测暗于背景的横向连续区域
    yb = y0 + h0
    shadow_band = gray[min(H - 1, int(yb + h0 * 0.03)):min(H - 1, int(yb + h0 * 0.15)), :]
    bg_L = np.percentile(np.concatenate([gray[:40, :].ravel(), gray[-40:, :].ravel(), gray[:, :40].ravel(), gray[:, -40:].ravel()]), 50)
    shadow_dark_frac = float(np.mean(shadow_band < bg_L - 18)) if shadow_band.size else 0.0
    # 接触区左右扩展阴影(产品落地特征: 阴影宽度 > 主体宽的 60%)
    if shadow_band.size:
        dark_cols = np.where((shadow_band < bg_L - 18).mean(axis=0) > 0.3)[0]
        shadow_w_frac = (dark_cols.max() - dark_cols.min()) / w0 if len(dark_cols) > 10 else 0.0
    else:
        shadow_w_frac = 0.0

    # ---- 4) 透视漂移 ----
    aspect_dev = (aspect / bl_aspect - 1) * 100
    fill_dev = (fill / bl["body_fill"] - 1) * 100

    # ---- 5) 蒙皮占比 + 主色 ----
    lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
    local_std = cv2.blur(lap ** 2, (15, 15)) ** 0.5
    leather = (gray < 125) & (local_std > 4) & main
    leather = cv2.morphologyEx(leather.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    leather_frac = leather.sum() / main.sum()

    lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    Z = lab.reshape(-1, 3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _r, labels, centers = cv2.kmeans(Z, 8, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    labels = labels.reshape(H, W)
    rows = []
    for k in range(8):
        m = (labels == k) & main
        if m.sum() < 500:
            continue
        rgb_m = img_np[m].mean(axis=0)
        rows.append((m.sum() / main.sum(), "#{:02X}{:02X}{:02X}".format(*[int(v) for v in rgb_m])))
    rows.sort(key=lambda t: -t[0])
    # 每个基线主色找最近生成色
    color_match = []
    for bc in bl["colors"][:4]:
        best = min(rows, key=lambda t: hexdist(t[1], bc["hex"]))
        color_match.append({"base": bc["hex"], "base_frac": bc["frac_of_body"],
                            "nearest_found": best[1], "found_frac": round(best[0], 3),
                            "hex_dist": round(hexdist(best[1], bc["hex"]), 1)})

    qa = {
        "file": fname, "tag": tag, "size": [W, H],
        "view": {"aspect": round(aspect, 3), "base_aspect": bl_aspect, "aspect_dev_pct": round(aspect_dev, 1),
                 "top_L": round(float(top_L), 1), "mid_L": round(float(mid_L), 1)},
        "circles": match_report,
        "shadow": {"shadow_dark_frac": round(shadow_dark_frac, 3), "shadow_w_frac": round(float(shadow_w_frac), 3),
                   "bg_L": round(float(bg_L), 1)},
        "drift": {"fill": round(float(fill), 3), "fill_dev_pct": round(fill_dev, 1)},
        "leather_frac": round(float(leather_frac), 3), "leather_base": bl["leather_frac_of_body"],
        "colors": color_match,
    }
    results.append(qa)
    print(f"\n=== {fname} ({W}x{H}) ===")
    print(f" aspect={aspect} (base {bl_aspect}, dev {aspect_dev:+.1f}%) top_L={top_L:.0f} vs mid_L={mid_L:.0f}")
    for mr in match_report:
        print(f" circle {mr['ref']}: {mr}")
    print(f" shadow: dark_frac={shadow_dark_frac:.2f} w_frac={shadow_w_frac:.2f} (bg_L={bg_L:.0f})")
    print(f" leather: {leather_frac:.3f} (base {bl['leather_frac_of_body']})")
    for cm in color_match:
        print(f" color {cm['base']}({cm['base_frac']*100:.0f}%) -> {cm['nearest_found']}({cm['found_frac']*100:.0f}%) dist={cm['hex_dist']}")

with open(BASE / "qa_final.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\nsaved qa_final.json")
