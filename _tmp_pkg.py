# -*- coding: utf-8 -*-
"""包装合成：AI 包装结构 + 真实枪灰相机嵌入透明腔体"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

PKG = "极印版 aiken/cmf/新ID五配色/产品摄影级电商包装渲染图_一个立式方形透明吸塑包装盒_放置在_2026-11-24T11-09-21.png"


def blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(r))).astype(np.float64)
CAM = "C:/Users/Nan/AppData/Local/CodeBuddyExtension/Data/e3a9f068-87b2-4b24-b808-6ce397663f4e/CodeBuddyIDE/e3a9f068-87b2-4b24-b808-6ce397663f4e/history/bb021b6d806f436afecda455baf3693a/4233e7d5044f4e41b1dc59dd3f790dab/assets/极印 枪灰.da023f6143.jpg"
OUT = "极印版 aiken/cmf/新ID五配色/枪灰-包装效果图.png"

# 透明腔体内假相机的区域（含抗锯齿残边，将被重建为空腔）
FAKE = (294, 316, 714, 634)
# 白色底座乱码区域（实测文字+红块 x 344-561, y 768-824；避开 x≈575 折角）
TEXT = (335, 758, 568, 834)


def seg_camera():
    """从枪灰渲染图抠出相机（RGBA）。"""
    rgb = np.asarray(Image.open(CAM).convert("RGB")).astype(np.float64)
    h, w, _ = rgb.shape
    corners = np.concatenate([rgb[:30, :30].reshape(-1, 3), rgb[:30, -30:].reshape(-1, 3),
                              rgb[-30:, :30].reshape(-1, 3), rgb[-30:, -30:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    dist = np.abs(rgb - bg[None, None, :]).max(axis=2)
    core = ((dist > 12).astype(np.uint8) * 255)
    m = Image.fromarray(core).filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(17))
    f = m.copy(); ImageDraw.floodfill(f, (0, 0), 128, thresh=0)
    solid = (np.asarray(f) != 128)
    # 排除底部投影：投影色差小且位于产品下方
    ys = np.where(solid.any(axis=1))[0]; xs = np.where(solid.any(axis=0))[0]
    a = np.where(dist > 10, solid, False)
    a = a & (np.mgrid[0:h, 0:w][0] < ys.max() - 6)
    edge = np.clip((dist - 4.0) / 6.0, 0, 1)
    alpha = a * edge
    alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.8))).astype(np.float64) / 255.0
    return rgb, alpha, xs.min(), xs.max(), ys.min(), ys.max()


def rebuild_cavity(pkg):
    """擦除假相机：横向插值 + 上下边界差值纵向回填，四边全部无缝。"""
    x0, y0, x1, y1 = FAKE
    a = np.asarray(pkg).astype(np.float64)
    w = x1 - x0
    left = a[y0:y1, x0 - 34:x0 - 4].mean(axis=1, keepdims=True)
    right = a[y0:y1, x1 + 4:x1 + 34].mean(axis=1, keepdims=True)
    t = np.linspace(0, 1, w)[None, :, None]
    base = left * (1 - t) + right * t                      # 横向插值 (h,w,3)

    # 上下真实边界与横向插值的差，沿纵向线性回填
    top_row = a[y0 - 8:y0 - 2, x0:x1].mean(axis=0, keepdims=True)
    bot_row = a[y1 + 2:y1 + 8, x0:x1].mean(axis=0, keepdims=True)
    d_top = top_row - base[0:1]
    d_bot = bot_row - base[-1:]
    # 只保留低频明暗趋势，避免边界纹理被纵向拉伸成条纹
    for d in (d_top, d_bot):
        sm = Image.fromarray(np.clip(d[0] + 128, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(22))
        d[0] = np.asarray(sm).astype(np.float64) - 128.0
    s = np.linspace(0, 1, y1 - y0)[:, None, None]
    fill = base + d_top * (1 - s) + d_bot * s

    # 叠加真实塑料纹理高频：取上方空腔同宽度区域的高通
    h = y1 - y0
    tex = a[y0 - 128:y0 - 8, x0:x1]                     # (120, w, 3)
    tex = np.asarray(Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8))
                     .resize((x1 - x0, h), Image.LANCZOS)).astype(np.float64)
    tex_hp = tex - blur(tex.mean(axis=2), 10)[..., None]
    fill = fill + tex_hp * 0.85

    noise = np.random.default_rng(3).normal(0, 1.0, fill.shape)
    fill = np.clip(fill + noise, 0, 255)

    mask = np.zeros(a.shape[:2], np.float64)
    mask[y0:y1, x0:x1] = 1.0
    mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(6))).astype(np.float64) / 255.0
    canvas = a.copy()
    canvas[y0:y1, x0:x1] = fill
    a = a * (1 - mask[..., None]) + canvas * mask[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    pkg = Image.open(PKG).convert("RGB")
    pkg = rebuild_cavity(pkg)

    rgb, alpha, cx0, cx1, cy0, cy1 = seg_camera()
    cam = rgb[cy0:cy1 + 1, cx0:cx1 + 1]
    al = alpha[cy0:cy1 + 1, cx0:cx1 + 1]

    # 相机贴合腔体：完全收进透明腔内壁
    tw = 340
    th = int(cam.shape[0] * tw / cam.shape[1])
    cam_s = np.asarray(Image.fromarray(cam.astype(np.uint8)).resize((tw, th), Image.LANCZOS)).astype(np.float64)
    al_s = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)).astype(np.float64) / 255.0

    a = np.asarray(pkg).astype(np.float64)
    # 放置：腔体内壁中央（内壁约 x 255~755），略偏下留出卡扣
    px, py = 505 - tw // 2, 395

    # 腔体内投影（相机后下方软阴影）
    sh = np.zeros((th + 30, tw + 40), np.float64)
    sh[24:, 12:-12] = 1.0
    sh_img = Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    sh = np.asarray(sh_img).astype(np.float64) / 255.0 * 0.45
    yy, xx = np.mgrid[py:py + th + 30, px - 20:px + tw + 20]
    region = a[py:py + th + 30, px - 20:px + tw + 20]
    region *= (1 - sh[..., None])
    a[py:py + th + 30, px - 20:px + tw + 20] = region

    # 相机本体：压暗 4%、去饱和 8%，模拟隔着塑料的观感
    gray = cam_s.mean(axis=2, keepdims=True)
    cam_s = cam_s * 0.96 + gray * 0.04
    cam_s = cam_s * 0.96

    reg = a[py:py + th, px:px + tw]
    a[py:py + th, px:px + tw] = reg * (1 - al_s[..., None]) + cam_s * al_s[..., None]

    pkg2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # ---- 底座字标：横向插值重建白卡纸面（保留竖向折角与渐变） ----
    a2 = np.asarray(pkg2).astype(np.float64)
    x0, y0, x1, y1 = TEXT
    left = a2[y0:y1, x0 - 16:x0 - 2].mean(axis=1, keepdims=True)
    right = a2[y0:y1, x1 + 2:x1 + 16].mean(axis=1, keepdims=True)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    fill = np.clip(left * (1 - t) + right * t + np.random.default_rng(5).normal(0, 1.0, (y1 - y0, x1 - x0, 3)), 0, 255)
    mask = np.zeros(a2.shape[:2], np.float64)
    mask[y0:y1, x0:x1] = 1.0
    mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(4))).astype(np.float64) / 255.0
    canvas2 = a2.copy()
    canvas2[y0:y1, x0:x1] = fill
    a2 = a2 * (1 - mask[..., None]) + canvas2 * mask[..., None]
    pkg2 = Image.fromarray(np.clip(a2, 0, 255).astype(np.uint8))

    d = ImageDraw.Draw(pkg2)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 48)
    except OSError:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
    label = "极印"
    bb = d.textbbox((0, 0), label, font=font)
    tw, thh = bb[2] - bb[0], bb[3] - bb[1]
    group_w = tw + 18 + 30                     # 文字 + 间距 + 红块
    gx = 450 - group_w // 2
    tx, ty = gx - bb[0], 796 - thh // 2 - bb[1]
    d.text((tx, ty), label, font=font, fill=(28, 28, 30))
    # 红色装饰块（呼应 Supreme 红盒的点缀）
    bx = tx + tw + 18
    d.rounded_rectangle([bx, ty + 6, bx + 30, ty + 6 + 30], radius=2, fill=(196, 30, 38))

    pkg2.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
