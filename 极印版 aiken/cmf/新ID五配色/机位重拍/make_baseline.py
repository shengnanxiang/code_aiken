# -*- coding: utf-8 -*-
"""低奢金 MASTER 基线数据包生成（供 hero-angle 机位重拍的形态保真对比用）
输出到 机位重拍\baseline\：
- baseline_close.json / baseline_open.json：量化基线（圆件、色值、比例、曲率）
- mask_leather_close/open.png：蒙皮区掩膜
- mask_body_close/open.png：主体掩膜
- baseline_report.md：人读版基线摘要
"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
import json

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色")
OUT = BASE / "机位重拍" / "baseline"
OUT.mkdir(parents=True, exist_ok=True)

MASTERS = [
    ("close", BASE / "newid-低奢金-c.png"),
    ("open", BASE / "newid-低奢金-open.png"),
]

def circle_refine(gray, cx, cy, r0, tol=24):
    """在 (cx,cy) 邻域用径向亮度剖面精修圆心与半径（粗步长，快）"""
    best = (cx, cy, r0, 0)
    yy, xx = np.mgrid[0:gray.shape[0], 0:gray.shape[1]]
    for dy in range(-tol, tol + 1, 12):
        for dx in range(-tol, tol + 1, 12):
            c_x, c_y = cx + dx, cy + dy
            for r in range(max(20, r0 - 24), r0 + 25, 8):
                ring_o = ((xx - c_x) ** 2 + (yy - c_y) ** 2 <= (r + 6) ** 2) & \
                         ((xx - c_x) ** 2 + (yy - c_y) ** 2 > (r + 1) ** 2)
                ring_i = ((xx - c_x) ** 2 + (yy - c_y) ** 2 < (r - 5) ** 2) & \
                         ((xx - c_x) ** 2 + (yy - c_y) ** 2 >= max(0, r - 10) ** 2)
                if ring_o.sum() < 50 or ring_i.sum() < 50:
                    continue
                contrast = gray[ring_o].mean() - gray[ring_i].mean()
                if contrast > best[3]:
                    best = (c_x, c_y, r, contrast)
    return best

def build_baseline(tag, path):
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    data = {"file": str(path), "size": [W, H]}

    # 主体掩膜
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
    data["body_bbox"] = [int(x0), int(y0), int(w0), int(h0)]
    data["body_fill"] = round(float(main.sum() / (w0 * h0)), 3)
    data["body_aspect"] = round(float(w0 / h0), 3)
    Image.fromarray((main * 255).astype(np.uint8)).save(OUT / f"mask_body_{tag}.png")

    # 蒙皮区（深色+高频）
    lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
    local_std = cv2.blur(lap ** 2, (15, 15)) ** 0.5
    leather = (gray < 125) & (local_std > 4) & main
    leather = cv2.morphologyEx(leather.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    data["leather_frac_of_body"] = round(float(leather.sum() / main.sum()), 3)
    Image.fromarray((leather * 255).astype(np.uint8)).save(OUT / f"mask_leather_{tag}.png")

    # 双圆件检测与精修
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=50,
                               param1=90, param2=48, minRadius=int(H * 0.03), maxRadius=int(H * 0.16))
    cands = []
    if circles is not None:
        for c in circles[0][:10]:
            cx, cy, r = c
            if main[int(np.clip(cy, 0, H - 1)), int(np.clip(cx, 0, W - 1))]:
                cands.append((cx, cy, r))
    # 聚合相近圆, 取最大两个
    merged = []
    for cx, cy, r in cands:
        placed = False
        for m in merged:
            if np.hypot(cx - m["cx"], cy - m["cy"]) < m["r"] * 0.6:
                if r > m["r"]:
                    m.update(cx=cx, cy=cy, r=r)
                placed = True
                break
        if not placed:
            merged.append({"cx": float(cx), "cy": float(cy), "r": float(r)})
    merged.sort(key=lambda m: -m["r"])
    circ_out = []
    yy, xx = np.mgrid[0:H, 0:W]
    for i, m in enumerate(merged[:2]):
        cx, cy, r, con = circle_refine(gray, int(m["cx"]), int(m["cy"]), int(m["r"]))
        rr = np.hypot(xx - cx, yy - cy)
        disk = rr < r
        ring = (rr > r + 3) & (rr < r + 18)
        circ = {
            "id": f"circle{i+1}",
            "cx": int(cx), "cy": int(cy), "r": int(r),
            "cx_rel": round(cx / W, 4), "cy_rel": round(cy / H, 4),
            "r_rel_bodyH": round(r / h0, 4),
            "disk_L": round(float(gray[disk].mean()), 1) if disk.sum() > 100 else None,
            "disk_hex": "#{:02X}{:02X}{:02X}".format(*[int(v) for v in img_np[disk].mean(axis=0)]) if disk.sum() > 100 else None,
            "ring_L": round(float(gray[ring].mean()), 1) if ring.sum() > 100 else None,
        }
        circ_out.append(circ)
    data["circles"] = circ_out

    # 色值表（k-means 8 类）
    lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    Z = lab.reshape(-1, 3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _r, labels, centers = cv2.kmeans(Z, 8, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    labels = labels.reshape(H, W)
    rows = []
    for k in range(8):
        m = labels == k & main if False else (labels == k) & main
        if m.sum() < 500:
            continue
        rgb_m = img_np[m].mean(axis=0)
        rows.append({
            "frac_of_body": round(float(m.sum() / main.sum()), 4),
            "hex": "#{:02X}{:02X}{:02X}".format(*[int(v) for v in rgb_m]),
            "L": round(float(gray[m].mean()), 1),
        })
    rows.sort(key=lambda t: -t["frac_of_body"])
    data["colors"] = rows

    # 轮廓曲率特征（上边缘 + 底边缘直线残差）
    edges_feat = {}
    for edge_name, pick in [("top", lambda ys_: ys_.min()), ("bottom", lambda ys_: ys_.max())]:
        pts = []
        for x in range(int(x0 + w0 * 0.12), int(x0 + w0 * 0.88), 6):
            ys_ = np.where(main[:, x])[0]
            if len(ys_):
                pts.append((x, pick(ys_)))
        pts = np.array(pts)
        if len(pts) > 20:
            fit = np.polyval(np.polyfit(pts[:, 0], pts[:, 1], 1), pts[:, 0])
            resid = pts[:, 1] - fit
            edges_feat[edge_name] = {
                "slope": round(float(np.polyfit(pts[:, 0], pts[:, 1], 1)[0]), 4),
                "resid_std_px": round(float(resid.std()), 1),
                "resid_range_px": round(float(resid.max() - resid.min()), 1),
            }
    data["edge_features"] = edges_feat

    # 分区亮度
    y_mid, x_mid = y0 + h0 * 0.5, x0 + w0 * 0.5
    quads = {}
    for nm, (yl, yh, xl, xh) in {
        "UL": (0, int(y_mid), 0, int(x_mid)), "UR": (0, int(y_mid), int(x_mid), W),
        "LL": (int(y_mid), H, 0, int(x_mid)), "LR": (int(y_mid), H, int(x_mid), W)}.items():
        m = main & (yy >= yl) & (yy < yh) & (xx >= xl) & (xx < xh)
        if m.sum() > 500:
            quads[nm] = round(float(gray[m].mean()), 1)
    data["quadrant_L"] = quads
    data["body_L_pct"] = {p: round(float(np.percentile(gray[main], p)), 1) for p in (10, 50, 90)}
    return data

results = {}
for tag, path in MASTERS:
    results[tag] = build_baseline(tag, path)
    print(f"{tag}: circles={[(c['cx'], c['cy'], c['r']) for c in results[tag]['circles']]}")

with open(OUT / "baseline_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("saved:", OUT / "baseline_data.json")

# 人读版摘要
lines = ["# 低奢金 MASTER 基线数据包（hero-angle 形态保真对比基准）", ""]
for tag, d in results.items():
    lines.append(f"## {tag}（{d['size'][0]}×{d['size'][1]}）")
    lines.append(f"- 主体 bbox: {d['body_bbox']}  fill={d['body_fill']}  aspect={d['body_aspect']}")
    lines.append(f"- 蒙皮占比: {d['leather_frac_of_body']}")
    for c in d["circles"]:
        lines.append(f"- {c['id']}: 中心({c['cx']},{c['cy']}) r={c['r']}  归一({c['cx_rel']},{c['cy_rel']}) "
                     f"r/机身高={c['r_rel_bodyH']}  盘内 L={c['disk_L']} {c['disk_hex']}  环 L={c['ring_L']}")
    lines.append(f"- 主色: " + "; ".join(f"{r['hex']}({r['frac_of_body']*100:.1f}%,L{r['L']})" for r in d["colors"][:5]))
    lines.append(f"- 边缘: {d['edge_features']}")
    lines.append(f"- 象限亮度: {d['quadrant_L']}  主体 L 分位: {d['body_L_pct']}")
    lines.append("")
lines.append("用途：机位重拍生成图的形态保真 QA 基准。圆件位置/半径比、蒙皮占比、主色 hex 偏差、象限亮度结构均可用本数据对比。")
with open(OUT / "baseline_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("saved:", OUT / "baseline_report.md")
