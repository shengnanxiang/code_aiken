# -*- coding: utf-8 -*-
"""主版 fill-w 超带归因: 产品拉变形 vs 阴影计入 vs 掩膜差异"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色\机位重拍")

for fname in ["newid-香槟-开_square.png", "newid-香槟-开_square_alt.png"]:
    img = Image.open(BASE / fname).convert("RGB")
    W, H = img.size
    img_np = np.asarray(img).astype(np.float32)
    gray = np.asarray(Image.open(BASE / fname).convert("L")).astype(np.float32)

    corners = np.array([img_np[2, 2], img_np[2, W-3], img_np[H-3, 2], img_np[H-3, W-3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    # 阈值敏感性: 30 / 18 / 12
    print(f"\n===== {fname} =====")
    for thr in [30, 18, 12]:
        fg = (dist > thr).astype(np.uint8) * 255
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
        n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
        areas = st[1:, cv2.CC_STAT_AREA]
        i0 = 1 + int(np.argmax(areas))
        x0, y0, w0, h0, area = st[i0]
        print(f" thr={thr}: bbox w_frac={w0/W:.3f} h_frac={h0/H:.3f} aspect={w0/h0:.2f}")

    # 阴影检查: 主体左右两侧的暗带(是否阴影被计入主体)
    thr = 30
    fg = (dist > thr).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    i0 = 1 + int(np.argmax(areas))
    main = cc == i0
    x0, y0, w0, h0 = st[i0, :4]
    # 主体左/右边缘的过渡带宽度(阴影=渐变过渡, 产品边=锐利)
    mid_y = y0 + h0 // 2
    row = main[mid_y]
    xs_ = np.where(row)[0]
    if len(xs_):
        xl, xr = xs_.min(), xs_.max()
        # 左边缘: 从 xl 向左 40px 的亮度剖面
        prof_l = gray[mid_y, max(0, xl - 40):xl + 5]
        prof_r = gray[mid_y, xr - 5:min(W, xr + 40)]
        # 过渡锐度: 相邻 3px 最大差
        def sharpness(p):
            return float(np.max(np.abs(np.diff(p)))) if len(p) > 2 else 0
        print(f" left edge L profile({xl}): {['%.0f' % v for v in prof_l[::6]]} sharp={sharpness(prof_l):.0f}")
        print(f" right edge L profile({xr}): {['%.0f' % v for v in prof_r[::-6]]} sharp={sharpness(prof_r):.0f}")
        # 主体的左边缘列与右边缘列的形状(逐行 x_min/x_max 的分布)
        y_idx = np.where(main.any(axis=1))[0]
        xl_row = [np.where(main[y])[0].min() for y in y_idx[::max(1, len(y_idx)//12)]]
        xr_row = [np.where(main[y])[0].max() for y in y_idx[::max(1, len(y_idx)//12)]]
        print(f" left-boundary per row: {xl_row}")
        print(f" right-boundary per row: {xr_row}")
    # 垂直边缘结构: 主体内是否有竖直暗缝(双圆件的玻璃窗)
    # 圆件横向分布: 主版是否圆件被拉开
    blur_g = cv2.GaussianBlur(np.asarray(gray, np.uint8), (5, 5), 1.5)
    circles = cv2.HoughCircles(blur_g, cv2.HOUGH_GRADIENT, dp=1.3, minDist=60,
                               param1=90, param2=40, minRadius=int(h0*0.10), maxRadius=int(h0*0.5))
    if circles is not None:
        cl = [(int(c[0]), int(c[1]), int(c[2])) for c in circles[0][:10]
              if main[int(np.clip(c[1], 0, H-1)), int(np.clip(c[0], 0, W-1))]]
        cl.sort(key=lambda c: -c[2])
        print(f" circles: {cl[:4]}")
        # 圆件横向间距 / 主体宽
        if len(cl) >= 2:
            spread = max(c[0] for c in cl[:3]) - min(c[0] for c in cl[:3])
            print(f" circle x-spread={spread} / body_w={w0} = {spread/w0:.2f}")
