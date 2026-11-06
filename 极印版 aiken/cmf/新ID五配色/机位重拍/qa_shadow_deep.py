# -*- coding: utf-8 -*-
"""深入检测: 接地投影逐行暗度 + 底部轮廓内收 + 环境光梯度"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf\新ID五配色\机位重拍")

for fname in ["newid-低奢金-c_hero.png", "newid-低奢金-c_hero_alt.png",
              "newid-低奢金-open_hero.png", "newid-低奢金-open_hero_alt.png"]:
    img = Image.open(BASE / fname).convert("RGB")
    W, H = img.size
    gray = np.asarray(Image.open(BASE / fname).convert("L")).astype(np.float32)
    img_np = np.asarray(img).astype(np.float32)
    corners = np.array([img_np[2, 2], img_np[2, W - 3], img_np[H - 3, 2], img_np[H - 3, W - 3]], np.float32)
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
    fg = (dist > 30).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    i0 = 1 + int(np.argmax(areas))
    x0, y0, w0, h0 = st[i0, :4]
    yb = y0 + h0
    print(f"\n=== {fname} body y {y0}-{yb} x {x0}-{x0+w0} ===")
    for band in range(6):
        ya = int(yb + band * h0 * 0.02)
        yz = int(ya + h0 * 0.02)
        if yz >= H:
            break
        strip = gray[ya:yz, x0:x0 + w0]
        bg_side_L = np.percentile(np.concatenate([gray[:30, :].ravel(), gray[:, :30].ravel(), gray[:, -30:].ravel()]), 50)
        print(f" y{ya}-{yz}: strip_L={strip.mean():.0f} min={strip.min():.0f} bg_side={bg_side_L:.0f} "
              f"darker_frac={np.mean(strip < bg_side_L - 12):.2f}")
    for y in range(yb - 1, y0, -2):
        xs_ = np.where((cc == i0)[y])[0]
        if len(xs_) > 30:
            bot_w = xs_.max() - xs_.min()
            bot_y = y
            break
    mid_y = (y0 + yb) // 2
    xs_mid = np.where((cc == i0)[mid_y])[0]
    mid_w = xs_mid.max() - xs_mid.min() if len(xs_mid) else 0
    print(f" bottom row y={bot_y} w={bot_w} vs mid w={mid_w} ratio={bot_w/max(mid_w,1):.2f}")
    left_bg = gray[:, :30].mean()
    right_bg = gray[:, -30:].mean()
    top_bg = gray[:30, :].mean()
    bot_bg = gray[-30:, :].mean()
    print(f" bg gradient: L={left_bg:.0f} R={right_bg:.0f} T={top_bg:.0f} B={bot_bg:.0f} "
          f"(span={max(left_bg,right_bg,top_bg,bot_bg)-min(left_bg,right_bg,top_bg,bot_bg):.0f})")
