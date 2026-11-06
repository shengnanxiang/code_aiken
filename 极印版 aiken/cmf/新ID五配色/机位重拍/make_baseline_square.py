# -*- coding: utf-8 -*-
"""square-layout 基线数据包:
A. 枪灰.png 版式基准(fill/质心/机位/光影/背景/投影形态)
B. 香槟-开.png 产品基准(双圆件/CMF/构图)
输出: baseline_square\layout_gunmetal.json / product_champagne.json + 掩膜 + 人读报告
"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
import json

UP = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf")
OUT = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色\机位重拍\baseline_square")
OUT.mkdir(parents=True, exist_ok=True)

# 任务给的 uploads\ 路径在仓库中不存在; 按文件特征定位同源文件:
# 枪灰 3840x3840 方形 4K = cmf\new id\枪灰修正-4k.png
# 香槟-开 1927x1018 横幅 = cmf\新ID五配色\newid-低奢金-open.png (低奢金/香槟金 open 态)
GUNMETAL = UP / "new id" / "枪灰修正-4k.png"
CHAMPAGNE = UP / "新ID五配色" / "newid-低奢金-open.png"

def body_mask(img_np):
    H, W = img_np.shape[:2]
    corners = np.array([img_np[2, 2], img_np[2, W - 3], img_np[H - 3, 2], img_np[H - 3, W - 3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    fg = (dist > 30).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    i0 = 1 + int(np.argmax(areas))
    return cc == i0, st[i0], bg

def analyze_layout(name, path, save_prefix):
    """版式基准: fill/质心/机位/光影/背景/投影"""
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    main, st, bg = body_mask(img_np)
    x0, y0, w0, h0, area = st
    data = {
        "file": str(path), "size": [W, H],
        "body_bbox": [int(x0), int(y0), int(w0), int(h0)],
        "fill_of_canvas": round(float(area / (W * H)), 4),
        "fill_of_bbox": round(float(area / (w0 * h0)), 4),
        "bbox_w_frac": round(float(w0 / W), 4),
        "bbox_h_frac": round(float(h0 / H), 4),
        "aspect": round(float(w0 / h0), 3),
    }
    # 质心
    ys_, xs_ = np.where(main)
    data["centroid_rel"] = [round(float(xs_.mean() / W), 4), round(float(ys_.mean() / H), 4)]
    # 背景色
    data["bg_hex"] = "#{:02X}{:02X}{:02X}".format(*[int(v) for v in bg])
    # 背景梯度(环境光)
    l, r, t, b = gray[:, :40].mean(), gray[:, -40:].mean(), gray[:40, :].mean(), gray[-40:, :].mean()
    data["bg_gradient"] = {"L": round(float(l), 1), "R": round(float(r), 1), "T": round(float(t), 1), "B": round(float(b), 1)}
    # 象限亮度(机位: 顶面受光?)
    y_mid, x_mid = y0 + h0 * 0.5, x0 + w0 * 0.5
    yy, xx = np.mgrid[0:H, 0:W]
    quads = {}
    for nm, (yl, yh, xl, xh) in {"UL": (0, int(y_mid), 0, int(x_mid)), "UR": (0, int(y_mid), int(x_mid), W),
                                  "LL": (int(y_mid), H, 0, int(x_mid)), "LR": (int(y_mid), H, int(x_mid), W)}.items():
        m = main & (yy >= yl) & (yy < yh) & (xx >= xl) & (xx < xh)
        if m.sum() > 500:
            quads[nm] = round(float(gray[m].mean()), 1)
    data["quadrant_L"] = quads
    # 接地投影: 主体底部下方暗带
    yb = y0 + h0
    shadow = {}
    if yb < H - 5:
        strip = gray[min(H - 1, int(yb + h0 * 0.02)):min(H - 1, int(yb + h0 * 0.12)), x0:x0 + w0]
        if strip.size:
            bgL = float(np.median([l, r, t, b]))
            shadow = {"dark_frac": round(float(np.mean(strip < bgL - 12)), 3),
                      "strip_minL": round(float(strip.min()), 1)}
    data["contact_shadow"] = shadow
    # 圆件(Hough, 机位参照)
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=60,
                               param1=90, param2=42, minRadius=int(h0 * 0.08), maxRadius=int(h0 * 0.5))
    cl = []
    if circles is not None:
        for c in circles[0][:8]:
            cx, cy, r = c
            if main[int(np.clip(cy, 0, H - 1)), int(np.clip(cx, 0, W - 1))]:
                cl.append({"cx_rel": round(float(cx / W), 4), "cy_rel": round(float(cy / H), 4),
                           "r_frac_H": round(float(r / H), 4), "r_frac_bodyH": round(float(r / h0), 4)})
    cl.sort(key=lambda c: -c["r_frac_bodyH"])
    data["circles"] = cl[:3]
    Image.fromarray((main * 255).astype(np.uint8)).save(OUT / f"mask_{save_prefix}.png")
    return data

def analyze_product(name, path):
    """产品基准: 双圆件/CMF 色/蒙皮占比"""
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    main, st, bg = body_mask(img_np)
    x0, y0, w0, h0, area = st
    data = {"file": str(path), "size": [W, H], "body_bbox": [int(x0), int(y0), int(w0), int(h0)]}
    # 圆件
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=50,
                               param1=90, param2=44, minRadius=int(H * 0.04), maxRadius=int(H * 0.2))
    cl = []
    if circles is not None:
        for c in circles[0][:12]:
            cx, cy, r = c
            if main[int(np.clip(cy, 0, H - 1)), int(np.clip(cx, 0, W - 1))]:
                rr = np.hypot(*np.mgrid[0:H, 0:W]) * 0  # placeholder
                yy, xx = np.mgrid[0:H, 0:W]
                rr = np.hypot(xx - cx, yy - cy)
                disk = rr < r
                rgb_m = img_np[disk].mean(axis=0)
                cl.append({"cx": int(cx), "cy": int(cy), "r": int(r),
                           "cx_rel": round(float(cx / W), 4), "cy_rel": round(float(cy / H), 4),
                           "r_rel_bodyH": round(float(r / h0), 4),
                           "disk_hex": "#{:02X}{:02X}{:02X}".format(*[int(v) for v in rgb_m]),
                           "disk_L": round(float(gray[disk].mean()), 1)})
    # 聚合相近圆
    merged = []
    for c in cl:
        placed = False
        for m in merged:
            if abs(c["cx_rel"] - m["cx_rel"]) < 0.06 and abs(c["cy_rel"] - m["cy_rel"]) < 0.06:
                if c["r"] > m["r"]:
                    m.update(c)
                placed = True
                break
        if not placed:
            merged.append(dict(c))
    merged.sort(key=lambda m: -m["r_rel_bodyH"])
    data["circles"] = merged[:3]
    # CMF 色表
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
        rows.append({"frac_of_body": round(float(m.sum() / main.sum()), 4),
                     "hex": "#{:02X}{:02X}{:02X}".format(*[int(v) for v in rgb_m]),
                     "L": round(float(gray[m].mean()), 1)})
    rows.sort(key=lambda t: -t["frac_of_body"])
    data["colors"] = rows
    # 蒙皮占比
    lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
    local_std = cv2.blur(lap ** 2, (15, 15)) ** 0.5
    leather = (gray < 125) & (local_std > 4) & main
    leather = cv2.morphologyEx(leather.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    data["leather_frac"] = round(float(leather.sum() / main.sum()), 3)
    return data

print("==== A. 枪灰 版式基准 ====")
lay = analyze_layout("gunmetal", GUNMETAL, "gunmetal")
print(json.dumps(lay, ensure_ascii=False, indent=1))
print("\n==== B. 香槟-开 产品基准 ====")
prod = analyze_product("champagne", CHAMPAGNE)
print(json.dumps(prod, ensure_ascii=False, indent=1))

json.dump(lay, open(OUT / "layout_gunmetal.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(prod, open(OUT / "product_champagne.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 人读报告
lines = ["# square-layout 基线数据包", "",
         "## A. 枪灰.png 版式基准（生成目标）",
         f"- 画幅 {lay['size'][0]}×{lay['size'][1]}（方形）",
         f"- 相机 bbox 占画幅: 宽 {lay['bbox_w_frac']*100:.1f}% × 高 {lay['bbox_h_frac']*100:.1f}%; fill_of_canvas={lay['fill_of_canvas']*100:.1f}%",
         f"- 质心(归一): ({lay['centroid_rel'][0]}, {lay['centroid_rel'][1]})",
         f"- 主体 aspect={lay['aspect']}  背景色 {lay['bg_hex']}  背景梯度 {lay['bg_gradient']}",
         f"- 象限亮度 {lay['quadrant_L']}",
         f"- 接地投影 {lay['contact_shadow']}",
         f"- 圆件(参照): {[(c['cx_rel'], c['cy_rel'], c['r_frac_bodyH']) for c in lay['circles']]}", "",
         "## B. 香槟-开.png 产品基准（保真对象）",
         f"- 原尺寸 {prod['size'][0]}×{prod['size'][1]}  bbox {prod['body_bbox']}",
         f"- 圆件: {[(c['cx_rel'], c['cy_rel'], c['r_rel_bodyH'], c['disk_hex']) for c in prod['circles']]}",
         f"- 主色: {[(r['hex'], r['frac_of_body']) for r in prod['colors'][:5]]}",
         f"- 蒙皮占比: {prod['leather_frac']}", "",
         "## QA 判据（生成图收口用）",
         "1. 版式: fill_of_canvas 偏差 ≤±15% 相对枪灰; 质心偏差 ≤0.08(归一); 画幅方形",
         "2. 产品: 双圆件 r_rel_bodyH 偏差 ≤±15%; 主色 hex 距离 中浅色≤20; 蒙皮占比偏差 ≤±20%",
         "3. 偏差如实标注"]
open(OUT / "baseline_square_report.md", "w", encoding="utf-8").write("\n".join(lines))
print("\nsaved:", OUT)
