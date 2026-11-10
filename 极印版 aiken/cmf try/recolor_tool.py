# -*- coding: utf-8 -*-
"""算法换色 v3：基于 白黑-v1.png 像素级换色。
- 暗金金属件（快门+镜头圈）：暖色且相对饱和度高 → 银白 #efefef
- 中性暗部连通域，且环带邻接「奶油色亮机身」≥30% → 森林绿 #18542a（保颗粒纹理）
  · 镜头玻璃（被金环包围，环带非亮机身）自动保留深色
  · 地面阴影（邻接灰色背景）自动排除
- 亮部偏暖机身 → 奶油色 #f3e8cc
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, sys.path[0])
from logo_flatten_tool import fill_holes


def label_components(mask: np.ndarray):
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur = 0
    for y0 in range(h):
        for x0 in range(w):
            if mask[y0, x0] and labels[y0, x0] == 0:
                cur += 1
                stack = [(y0, x0)]
                labels[y0, x0] = cur
                while stack:
                    y, x = stack.pop()
                    for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = cur
                            stack.append((ny, nx))
    return labels, cur


def dilate(mask: np.ndarray, size: int) -> np.ndarray:
    m = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(m.filter(ImageFilter.MaxFilter(size))) > 127


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    region = np.asarray(im).astype(np.float64)
    h, w, _ = region.shape
    R, G, B = region[..., 0], region[..., 1], region[..., 2]
    lum = region.mean(axis=2)

    corners = np.concatenate([
        region[:40, :40].reshape(-1, 3), region[:40, -40:].reshape(-1, 3),
        region[-40:, :40].reshape(-1, 3), region[-40:, -40:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    product = fill_holes(dilate(np.abs(region - bg[None, None, :]).max(axis=2) > 16, 9))
    tight_core = np.abs(region - bg[None, None, :]).max(axis=2) > 24  # 未膨胀的产品实体
    tight = dilate(tight_core, 5)

    rel_warm = (R - B) / np.clip(lum, 1, None)
    gold_raw = (rel_warm > 0.22) & (lum < 210) & product          # 暗金金属候选
    neutral_dark = ((lum < 120) & (np.abs(R - B) <= 25)) & product
    cream_light = (lum > 150) & ((R - B) > 4)                 # 奶油色亮机身

    def annulus_cream_frac(comp):
        annulus = dilate(comp, 15) & ~dilate(comp, 5)
        total = int(annulus.sum())
        if total == 0:
            return 0.0
        return float((cream_light & annulus).sum()) / total

    # 金色件 = 紧凑的块状组件（快门椭圆、镜头圆环），排除边缘细长暖色条纹
    gold = np.zeros_like(gold_raw)
    g_l, g_n = label_components(gold_raw)
    for i in range(1, g_n + 1):
        comp = g_l == i
        s = int(comp.sum())
        if s < 800:
            continue
        ys, xs = np.where(comp)
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        fill_ratio = s / float(bw * bh)
        if fill_ratio >= 0.28 and float(tight[ys, xs].mean()) >= 0.5:
            gold |= comp

    # 中性暗部组件的环带邻接判定
    green_mask = np.zeros_like(neutral_dark)
    nd_l, nd_n = label_components(neutral_dark)
    for i in range(1, nd_n + 1):
        comp = nd_l == i
        if comp.sum() < 60:
            continue
        if annulus_cream_frac(comp) >= 0.25:
            green_mask |= comp

    # 1) 机身 → 奶油色
    cream_ratio = np.array([243.0 / 247.0, 232.0 / 236.0, 204.0 / 230.0])
    w_body = np.clip((lum - 150) / 30, 0, 1) * ((R - B) > 4) * product * (~gold)
    out = region * (1 - w_body[..., None]) + np.clip(region * cream_ratio[None, None, :], 0, 255) * w_body[..., None]

    # 2) 暗金 → 银白 #efefef
    if gold.any():
        L_gold = np.median(lum[gold])
        r_gold = np.clip(lum / max(L_gold, 1), 0.45, 1.6) ** 0.9
        silver = np.clip(239.0 * r_gold[..., None], 0, 255)
        w_gold = np.clip((208 - lum) / 25, 0, 1) * gold
        out = out * (1 - w_gold[..., None]) + silver * w_gold[..., None]

    # 3) 中性暗部 → 森林绿 #18542a
    if green_mask.any():
        L_med = np.median(lum[green_mask])
        r_green = np.clip(lum / max(L_med, 1), 0.4, 1.6) ** 0.9
        green = np.array([24.0, 84.0, 42.0])
        green_out = np.clip(green[None, None, :] * r_green[..., None], 0, 255)
        w_green = np.clip((135 - lum) / 25, 0, 1) * green_mask * tight_core
        out = out * (1 - w_green[..., None]) + green_out * w_green[..., None]

    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    res.save(dst)
    print(f"gold_px={int(gold.sum())} green_px={int(green_mask.sum())} saved: {dst}")


if __name__ == "__main__":
    main()
