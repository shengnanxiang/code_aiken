# -*- coding: utf-8 -*-
"""从渲染图中完全去除 Logo：识别墨色区域+投影，用周边机身色扩散填补，
并按机身材质的颗粒强度补微噪点，避免填补区过于光滑而露馅。"""
import sys
import numpy as np
from PIL import Image, ImageFilter

from logo_flatten_tool import fill_holes, dilate, diffusion_fill


def remove_logo(img: Image.Image, box):
    im = img.copy()
    region = np.asarray(im.crop(box)).astype(np.float64)
    h, w, _ = region.shape
    px = region.reshape(-1, 3)
    lum = px.mean(axis=1)

    body_ref = np.median(px[lum > np.percentile(lum, 70)], axis=0)
    dark_ref = np.median(px[lum < np.percentile(lum, 10)], axis=0)
    d_body = np.linalg.norm(region - body_ref, axis=2)
    d_dark = np.linalg.norm(region - dark_ref, axis=2)
    ink = d_dark < d_body
    ink = fill_holes(ink)
    m = Image.fromarray((ink * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3))
    ink = np.asarray(m) > 127

    # 待去除区域 = 墨色（大幅膨胀，连抗锯齿边和高光晕一起盖掉）+ 明暗异常环带
    zone = dilate(ink, 11)
    ring = dilate(ink, 31) & ~zone
    base_lum = np.median(region[~ring].mean(axis=1))
    lum2 = region.mean(axis=2)
    shadow = ring & ((lum2 < base_lum - 10) | (lum2 > base_lum + 7)) & ~ink
    zone = zone | shadow

    # 逐行线性插值填补：每个连续 zone 段向两侧搜索「干净机身窗口」取色渐变过渡
    clean = np.abs(lum2 - base_lum) <= 8  # 亮度正常的机身像素
    clean = clean & ~zone
    filled = region.copy()
    for y in range(h):
        row = zone[y]
        if not row.any():
            continue
        xs = np.where(row)[0]
        splits = np.where(np.diff(xs) > 1)[0]
        starts = [xs[0]] + [xs[s + 1] for s in splits]
        ends = [xs[s] for s in splits] + [xs[-1]]
        for x0, x1 in zip(starts, ends):
            def band_from(x_start, step):
                x = x_start
                while 0 <= x < w:
                    seg = [x + i for i in range(5) if 0 <= x + i < w and clean[y, x + i]]
                    if len(seg) >= 4:
                        return np.median(region[y, seg], axis=0)
                    x += step
                return None
            lcol = band_from(x0 - 8, -1)
            rcol = band_from(x1 + 8, 1)
            if lcol is None:
                lcol = rcol
            if rcol is None:
                rcol = lcol
            if lcol is None:
                continue
            n = x1 - x0 + 1
            t = np.linspace(0, 1, n)[:, None]
            filled[y, x0:x1 + 1] = lcol[None, :] * (1 - t) + rcol[None, :] * t

    # 填补区轻微纵向平滑，避免行间条纹
    sm = np.asarray(Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(1.2))).astype(np.float64)
    zs = dilate(zone, 3)
    filled[zs] = sm[zs]

    # 纹理移植：从邻近干净机身区复制高频颗粒残差，让填补区质感与周围同源
    region_blur = np.stack([
        np.asarray(Image.fromarray(np.clip(region[..., c], 0, 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(3.0))).astype(np.float64)
        for c in range(3)], axis=2)
    residual = region - region_blur
    ys, xs = np.where(zone)
    zh = ys.max() - ys.min() + 1
    transplanted = False
    for dy in (zh + 18, -(zh + 18), zh + 60, -(zh + 60)):
        yy0, yy1 = ys.min() + dy, ys.max() + dy
        if yy0 < 0 or yy1 >= h:
            continue
        src_zone = np.zeros_like(zone)
        src_zone[yy0:yy1 + 1, xs.min():xs.max() + 1] = True
        if (src_zone & zone).any() or ink[yy0:yy1 + 1, xs.min():xs.max() + 1].any():
            continue
        filled[zone] = np.clip(filled[zone] + residual[yy0:yy1 + 1, xs.min():xs.max() + 1][zone], 0, 255)
        transplanted = True
        break
    if not transplanted:  # 兜底：合成颗粒噪点
        smooth = region_blur.mean(axis=2)
        grain_std = max((region.mean(axis=2) - smooth)[~dilate(ink, 25)].std(), 0.6)
        rng = np.random.default_rng(7)
        noise = rng.normal(0, grain_std, filled.shape[:2])[..., None]
        filled[zone] = np.clip(filled[zone] + noise[zone], 0, 255)

    # 边缘轻微羽化过渡
    zone_soft_img = Image.fromarray((zone * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    soft = (np.asarray(zone_soft_img).astype(np.float64) / 255.0)[..., None]
    out = region * (1 - soft) + filled * soft

    patched = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    im.paste(patched, (box[0], box[1]))
    return im, int(zone.sum()), grain_std


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    for b in [(630, 360, 770, 460), (620, 965, 770, 1065)]:
        im, n, g = remove_logo(im, b)
        print(f"box={b} removed_px={n} grain_std={g:.2f}")
    im.save(dst)
    print("saved:", dst)


if __name__ == "__main__":
    main()
