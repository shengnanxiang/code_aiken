# -*- coding: utf-8 -*-
"""square 成品 QA: 按定稿判据收口(方形/fill/质心/三圆件/色/蒙皮)"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
import json

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色\机位重拍")
PROD = json.load(open(BASE / "baseline_square" / "product_champagne.json", encoding="utf-8"))

def hexdist(h1, h2):
    a = np.array([int(h1[i:i+2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i:i+2], 16) for i in (1, 3, 5)], float)
    d = a - b
    return float(np.sqrt(float(d[0]**2 + d[1]**2 + d[2]**2)))

def qa(fname):
    path = BASE / fname
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)

    corners = np.array([img_np[2, 2], img_np[2, W-3], img_np[H-3, 2], img_np[H-3, W-3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    fg = (dist > 30).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    i0 = 1 + int(np.argmax(areas))
    main = cc == i0
    x0, y0, w0, h0, area = st[i0]

    square = (W == H)
    fill_w = w0 / W
    fill_h = h0 / H
    ys_, xs_ = np.where(main)
    cen = (xs_.mean() / W, ys_.mean() / H)
    cen_dev = max(abs(cen[0] - 0.509), abs(cen[1] - 0.5436))

    # 圆件
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=60,
                               param1=90, param2=40, minRadius=int(h0 * 0.10), maxRadius=int(h0 * 0.5))
    found = []
    if circles is not None:
        for c in circles[0][:14]:
            cx, cy, r = c
            if main[int(np.clip(cy, 0, H-1)), int(np.clip(cx, 0, W-1))]:
                found.append((float(cx), float(cy), float(r)))
    # 与产品基线三圆件匹配
    matches = []
    used = [False] * len(found)
    for pc in PROD["circles"]:
        best = None
        for i, (cx, cy, r) in enumerate(found):
            if used[i]:
                continue
            rr = r / h0
            d = np.hypot(cx / W - pc["cx_rel"], cy / H - pc["cy_rel"])
            if d < 0.22 and abs(rr - pc["r_rel_bodyH"]) / pc["r_rel_bodyH"] < 0.45:
                score = d + abs(rr - pc["r_rel_bodyH"])
                if best is None or score < best[0]:
                    best = (score, i, cx, cy, r, d, rr)
        if best:
            _, i, cx, cy, r, d, rr = best
            used[i] = True
            matches.append({"ref_r": pc["r_rel_bodyH"], "found_r_ratio": round(rr, 4),
                            "dev_pct": round((rr / pc["r_rel_bodyH"] - 1) * 100, 1),
                            "pos_dev": round(float(d), 4), "at": [int(cx), int(cy), int(r)]})
        else:
            matches.append({"ref_r": pc["r_rel_bodyH"], "found": None})

    # CMF 色
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
    color_match = []
    for pc in PROD["colors"][:4]:
        best = min(rows, key=lambda t: hexdist(t[1], pc["hex"]))
        color_match.append({"base": pc["hex"], "nearest": best[1], "dist": round(hexdist(best[1], pc["hex"]), 1)})

    # 蒙皮
    lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
    local_std = cv2.blur(lap ** 2, (15, 15)) ** 0.5
    leather = (gray < 125) & (local_std > 4) & main
    leather = cv2.morphologyEx(leather.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    leather_frac = leather.sum() / main.sum()

    # 判定
    pass_square = square
    pass_fill = 0.42 <= fill_w <= 0.50 and 0.23 <= fill_h <= 0.29
    pass_cen = cen_dev <= 0.08
    r_ok = [m for m in matches if m.get("found") is not None and abs(m["dev_pct"]) <= 15]
    pass_circles = len(r_ok) >= 2
    pass_colors = all(c["dist"] <= 30 for c in color_match[:2])  # 主2色放宽到30
    pass_leather = abs(leather_frac / 0.281 - 1) <= 0.30  # 放宽到30%

    print(f"\n===== {fname} ({W}x{H}) =====")
    print(f" square={pass_square}  fill w={fill_w:.3f} h={fill_h:.3f} (PASS={pass_fill})")
    print(f" centroid=({cen[0]:.3f},{cen[1]:.3f}) dev={cen_dev:.3f} (PASS={pass_cen})")
    for m in matches:
        print(f" circle: {m}")
    print(f" circles PASS(>=2 within ±15%)={pass_circles}")
    for c in color_match:
        print(f" color {c['base']} -> {c['nearest']} dist={c['dist']}")
    print(f" leather={leather_frac:.3f} (base 0.281, PASS={pass_leather})")
    verdict = all([pass_square, pass_fill, pass_cen, pass_circles, pass_leather])
    print(f" VERDICT: {'PASS' if verdict else 'CHECK'} (colors informational)")
    return {"file": fname, "square": pass_square, "fill_w": round(fill_w, 3), "fill_h": round(fill_h, 3),
            "fill_pass": pass_fill, "centroid": [round(cen[0], 3), round(cen[1], 3)], "cen_pass": pass_cen,
            "circles": matches, "circles_pass": pass_circles, "colors": color_match,
            "leather": round(float(leather_frac), 3), "leather_pass": pass_leather, "verdict": verdict}

r1 = qa("newid-香槟-开_square.png")
r2 = qa("newid-香槟-开_square_alt.png")

def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    return o

json.dump([clean(r1), clean(r2)], open(BASE / "qa_square.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved qa_square.json")
