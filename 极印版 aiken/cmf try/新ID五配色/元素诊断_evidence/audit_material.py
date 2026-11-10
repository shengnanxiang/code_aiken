# -*- coding: utf-8 -*-
"""最终精查: 材质纹理区分(蒙皮vs玻璃vs壳体)、右圆件、logo 定位、明度对比结构"""
import numpy as np
from PIL import Image
from pathlib import Path
import cv2

BASE = Path(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\cmf")
img_np = np.asarray(Image.open(BASE / "new id close.png").convert("RGB")).astype(np.float32)
gray = np.asarray(Image.open(BASE / "new id close.png").convert("L")).astype(np.float32)
H, W = gray.shape
lap = cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.2), cv2.CV_32F, ksize=3)
yy, xx = np.mgrid[0:H, 0:W]

def region(name, mask):
    if mask.sum() < 200:
        print(f"{name}: n<200 skip")
        return
    rgb_m = img_np[mask].mean(axis=0)
    print(f"{name}: n={int(mask.sum())} hex=#{int(rgb_m[0]):02X}{int(rgb_m[1]):02X}{int(rgb_m[2]):02X} "
          f"L={gray[mask].mean():.0f} Lsd={gray[mask].std():.1f} tex(Lap)={lap[mask].std():.1f}")

print("==== material regions (new id close) ====")
# 左侧深色面板(排除圆件): 深色且距圆心>110
r_c = np.hypot(xx - 843, yy - 487)
circle = r_c < 95
panel_dark = (gray < 110) & (r_c > 115) & (xx < 1050) & (yy > 330) & (yy < 650)
region("left dark panel (excl. circle)", panel_dark)
region("circular glass (r<95 @843,487)", circle & (gray < 999))
# 圆件外环
ring = (r_c > 98) & (r_c < 115)
region("glass ring (98-115)", ring)
# 右侧亮壳
region("right light shell (x1100-1500,y300-600 gray>150)", (xx > 1100) & (xx < 1500) & (yy > 300) & (yy < 600) & (gray > 150))
# 右侧圆件 (1141,406) r50
r_r = np.hypot(xx - 1141, yy - 406)
region("right circle (r<48 @1141,406)", r_r < 48)
region("right circle ring (52-70)", (r_r > 52) & (r_r < 70))
# 顶带
region("top band (y210-280, x750-1400, gray>150)", (yy > 210) & (yy < 280) & (xx > 750) & (xx < 1400) & (gray > 150))
# 底带
region("bottom band (y620-690, x800-1400, gray>140)", (yy > 620) & (yy < 690) & (xx > 800) & (xx < 1400) & (gray > 140))

# logo 候选: (1345,630,41,24) (1374,647,42,24) + 附近搜索更细
print("\n==== logo candidates detail ====")
for (x0, y0, w, h) in [(1345, 630, 41, 24), (1374, 647, 42, 24)]:
    reg = gray[y0-4:y0+h+4, x0-4:x0+w+4]
    m = np.zeros(gray.shape, bool); m[y0:y0+h, x0:x0+w] = True
    rgb_m = img_np[m].mean(axis=0)
    print(f"mark({x0},{y0},{w},{h}): hex=#{int(rgb_m[0]):02X}{int(rgb_m[1]):02X}{int(rgb_m[2]):02X} "
          f"L={gray[m].mean():.0f} contrast_vs_local={gray[y0-20:y0+h+20, x0-60:x0+w+60].mean()-gray[m].mean():.0f}")

# 右侧圆件放大 ASCII
print("\n==== ZOOM right circle (x1080-1210, y340-480) step=5 ====")
reg = gray[340:480, 1080:1210]
lo, hi = np.percentile(reg, 2), np.percentile(reg, 98)
norm = np.clip((reg - lo) / max(hi - lo, 1), 0, 1)
for y in range(0, reg.shape[0] - 5, 5):
    row = ""
    for x in range(0, reg.shape[1] - 5, 5):
        row += "0123456789"[min(int(norm[y:y+5, x:x+5].mean() * 9.99), 9)]
    print(f"{340+y:4d} {row}")

# 主体内明度结构: 左右对比
print("\n==== luminance structure ====")
body = np.zeros(gray.shape, bool)
# 用近似: 非背景
bg = np.array([234, 234, 234], np.float32)
dist = np.linalg.norm(img_np - bg[None, None, :], axis=2)
body = dist > 30
left_half = body & (xx < 1050)
right_half = body & (xx >= 1050)
print(f"left half:  frac={left_half.mean():.3f} L={gray[left_half].mean():.0f}")
print(f"right half: frac={right_half.mean():.3f} L={gray[right_half].mean():.0f}")
# 明度直方图(主体)
gb = gray[body]
print(f"body L: p10={np.percentile(gb,10):.0f} p50={np.percentile(gb,50):.0f} p90={np.percentile(gb,90):.0f}")
dark_frac = np.mean(gb < 120)
print(f"body dark(L<120) frac: {dark_frac:.3f}")

# open 图同参数
img_o = np.asarray(Image.open(BASE / "new id open.png").convert("RGB")).astype(np.float32)
gray_o = np.asarray(Image.open(BASE / "new id open.png").convert("L")).astype(np.float32)
dist_o = np.linalg.norm(img_o - bg[None, None, :], axis=2)
body_o = dist_o > 30
print(f"\nopen body L: p10={np.percentile(gray_o[body_o],10):.0f} p50={np.percentile(gray_o[body_o],50):.0f} p90={np.percentile(gray_o[body_o],90):.0f}")
hsv_o = cv2.cvtColor(img_o.astype(np.uint8), cv2.COLOR_RGB2HSV)
s_o = hsv_o[:, :, 1][body_o] / 255
print(f"open body sat: mean={s_o.mean():.3f} colored(>0.15)={np.mean(s_o>0.15)*100:.1f}%")
hsv_c = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2HSV)
s_c = hsv_c[:, :, 1][body] / 255
v_c = hsv_c[:, :, 2][body] / 255
print(f"close body sat: mean={s_c.mean():.3f} colored(>0.15)={np.mean(s_c>0.15)*100:.1f}% vivid(>0.35)={np.mean(s_c>0.35)*100:.1f}%")
print(f"close body dark(V<0.25): {np.mean(v_c<0.25)*100:.1f}%")
