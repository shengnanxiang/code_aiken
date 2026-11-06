# -*- coding: utf-8 -*-
"""新 ID close/open 程序化分析: 配色聚类、蒙皮占比、玻璃组件、logo、缝线、材质、轮廓圆角"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf")
OUT = BASE / "audit_evidence"
OUT.mkdir(exist_ok=True)

def analyze(name, path):
    img = Image.open(path).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    print(f"\n======== {name}: {W}x{H} ========")

    # ---- k-means 10 类 ----
    lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    Z = lab.reshape(-1, 3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
    _r, labels, centers = cv2.kmeans(Z, 10, None, crit, 6, cv2.KMEANS_PP_CENTERS)
    labels = labels.reshape(H, W)
    order = []
    for k in range(10):
        m = labels == k
        rgb_m = img_np[m].mean(axis=0)
        order.append((k, m.mean(), rgb_m, m))
    order.sort(key=lambda t: -t[1])
    print("--- clusters ---")
    for k, frac, rgb_m, m in order:
        hsv = cv2.cvtColor(np.array([[[int(rgb_m[0]), int(rgb_m[1]), int(rgb_m[2])]]], np.uint8), cv2.COLOR_RGB2HSV)[0,0]
        sat = hsv[1]/255; val = hsv[2]/255
        print(f"k{k}: {frac*100:5.1f}% hex=#{int(rgb_m[0]):02X}{int(rgb_m[1]):02X}{int(rgb_m[2]):02X} "
              f"HSV=({int(hsv[0])},{int(hsv[1])},{int(hsv[2])}) sat={sat:.2f} L={gray[m].mean():.0f}")

    # ---- 主体掩膜(非背景) ----
    bg_rgb = order[0][2]
    dist_bg = np.linalg.norm(img_np - bg_rgb[None, None, :], axis=2)
    fg = (dist_bg > 30).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    main = cc == (1 + int(np.argmax(areas)))
    x0, y0, w0, h0 = st[1 + int(np.argmax(areas)), :4]
    print(f"body bbox: ({x0},{y0},{w0},{h0}) fill_in_bbox={main.sum()/(w0*h0):.2f}")

    # ---- ASCII 可视化 ----
    def amap(m, step, chars=" .:-=+*#%@"):
        hh, ww = m.shape
        lines = []
        for y in range(0, hh - step + 1, step):
            row = ""
            for x in range(0, ww - step + 1, step):
                v = m[y:y+step, x:x+step].mean()
                row += chars[min(int(v * (len(chars)-1) + 0.5), len(chars)-1)]
            lines.append(row)
        return "\n".join(lines)

    step = max(H // 48, 8)
    print("--- body mask ASCII ---")
    print(amap(main.astype(np.float32), step))

    # ---- 蒙皮区检测(深色+纹理高频) ----
    lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
    # 蒙皮=深色(L<120)且高频(局部 std>6)
    local_std = cv2.blur((lap ** 2), (15, 15)) ** 0.5
    dark = gray < 125
    leather = dark & (local_std > 4) & main
    leather = cv2.morphologyEx(leather.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    print(f"leather-dark frac of body: {leather.sum()/main.sum():.3f}")
    print("--- leather mask ASCII ---")
    print(amap(leather.astype(np.float32), step))

    # ---- 圆形玻璃组件检测(close 图): Hough 圆 ----
    blur = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, dp=1.3, minDist=50,
                               param1=90, param2=48, minRadius=int(H*0.03), maxRadius=int(H*0.16))
    print("--- Hough circles ---")
    if circles is not None:
        for c in circles[0][:8]:
            cx, cy, r = c
            in_body = main[int(max(0,cy-r)):int(cy+r), int(max(0,cx-r)):int(cx+r)].mean() > 0.4 if main[int(np.clip(cy,0,H-1)), int(np.clip(cx,0,W-1))] else False
            print(f"circle ({cx:.0f},{cy:.0f}) r={r:.0f} in_body={in_body}")

    # ---- 亮度/圆角轮廓: 主体上边缘曲率 ----
    top_edge = []
    for x in range(int(x0 + w0*0.1), int(x0 + w0*0.9), 4):
        ys_ = np.where(main[:, x])[0]
        if len(ys_):
            top_edge.append((x, ys_.min()))
    te = np.array(top_edge)
    if len(te) > 20:
        k_total = np.polyfit(te[:, 0], te[:, 1], 1)[0]
        # 残差: 直线拟合后的弯曲量
        fit = np.polyval(np.polyfit(te[:, 0], te[:, 1], 1), te[:, 0])
        resid = te[:, 1] - fit
        print(f"top edge: slope={k_total:.4f} resid_std={resid.std():.1f}px resid_range={resid.max()-resid.min():.0f}px (大=圆润无面)")

    # ---- 暗色组件(logo/玻璃/缝) ----
    very_dark = ((gray < 100) & main)
    vd = very_dark.astype(np.uint8) * 255
    vd = cv2.morphologyEx(vd, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n2, cc2, st2, cent2 = cv2.connectedComponentsWithStats(vd, 8)
    comps = []
    for i in range(1, n2):
        x, y, w, h, area = st2[i]
        if area > 300:
            comps.append((area, x, y, w, h, cent2[i]))
    comps.sort(reverse=True)
    print("--- dark components (area>300) ---")
    for area, x, y, w, h, c in comps[:12]:
        print(f"area={area:6d} bbox=({x},{y},{w},{h}) rel=({x/W:.3f},{y/H:.3f}) aspect={w/max(h,1):.2f}")

    # ---- 分件缝: 水平/近水平暗线检测 ----
    edges = cv2.Canny(np.asarray(gray, np.uint8), 40, 120)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 360, threshold=80,
                            minLineLength=int(W * 0.2), maxLineGap=10)
    h_lines = []
    if lines is not None:
        for l in lines.reshape(-1, 4):
            x1, y1, x2, y2 = l
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1))) % 180
            if ang < 8 or ang > 172:
                if main[(y1 + y2) // 2, (x1 + x2) // 2]:
                    h_lines.append((min(y1, y2), min(x1, x2), max(x1, x2)))
    print(f"--- horizontal seam lines in body: {len(h_lines)} ---")
    for y, xa, xb in sorted(set(h_lines))[:10]:
        print(f"  y={y} x[{xa}-{xb}]")

    # ---- 高光/材质: 亮像素分布 ----
    bright = (gray > 235) & main
    print(f"specular highlight frac of body: {bright.sum()/main.sum():.4f}")
    # 分区亮度
    y_mid, x_mid = y0 + h0 * 0.5, x0 + w0 * 0.5
    for nm_, (ysl, ysh, xsl, xsh) in {
        "upper-left quadrant": (0, int(y_mid), 0, int(x_mid)),
        "upper-right": (0, int(y_mid), int(x_mid), W),
        "lower-left": (int(y_mid), H, 0, int(x_mid)),
        "lower-right": (int(y_mid), H, int(x_mid), W)}.items():
        m_ = main & (np.mgrid[0:H, 0:W][0] >= ysl) & (np.mgrid[0:H, 0:W][0] < ysh) \
                      & (np.mgrid[0:H, 0:W][1] >= xsl) & (np.mgrid[0:H, 0:W][1] < xsh)
        if m_.sum() > 500:
            print(f"  {nm_}: L_mean={gray[m_].mean():.0f}")

    np.save(OUT / f"{name}_labels.npy", labels)
    Image.fromarray((main * 255).astype(np.uint8)).save(OUT / f"{name}_main.png")
    Image.fromarray((leather * 255).astype(np.uint8)).save(OUT / f"{name}_leather.png")
    return order, main, leather, gray

analyze("newid_close", BASE / "new id close.png")
analyze("newid_open", BASE / "new id open.png")
print("\ndone")
