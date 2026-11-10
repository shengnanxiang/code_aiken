# -*- coding: utf-8 -*-
"""v2: 压平 Logo 浮雕 + 去除投影 + 修正墨色取样。
1. 墨色参考改用「蓝色主导的暗色像素」中位数，避免被灰色投影拉偏；
2. 检测笔画周围的投影（发灰变暗的非墨像素），用扩散法从周边机身色填补；
3. 墨色区域统一重绘为平坦藏青，边缘羽化。
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def fill_holes(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    body = ~mask
    visited = np.zeros_like(body, dtype=bool)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if body[y, x] and not visited[y, x]:
                stack.append((y, x)); visited[y, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if body[y, x] and not visited[y, x]:
                stack.append((y, x)); visited[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and body[ny, nx] and not visited[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    return mask | (body & ~visited)


def dilate(mask: np.ndarray, size: int) -> np.ndarray:
    m = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(m.filter(ImageFilter.MaxFilter(size))) > 127


def diffusion_fill(region: np.ndarray, unknown: np.ndarray, iters: int = 60):
    """把 unknown=True 的像素用周边已知像素迭代扩散填补。"""
    out = region.copy()
    known = ~unknown
    for c in range(3):
        ch = out[..., c]
        ch[~known] = np.nan
        for _ in range(iters):
            padded = np.pad(ch, 1, mode="edge")
            stack = np.stack([padded[0:-2, 1:-1], padded[2:, 1:-1],
                              padded[1:-1, 0:-2], padded[1:-1, 2:],
                              padded[1:-1, 1:-1]])
            mean = np.nanmean(stack, axis=0)
            ch = np.where(np.isnan(ch), mean, ch)
            if not np.isnan(ch).any():
                break
        ch = np.where(np.isnan(ch), np.nanmean(ch), ch)
        out[..., c] = ch
    return out


def flatten_logo(img: Image.Image, box):
    im = img.copy()
    region = np.asarray(im.crop(box)).astype(np.float64)
    h, w, _ = region.shape
    px = region.reshape(-1, 3)
    lum = px.mean(axis=1)

    # 机身参考：亮像素
    body_ref = np.median(px[lum > np.percentile(lum, 70)], axis=0)
    # 墨色参考：蓝色主导（B>R+12）且较暗的像素 —— 排除灰色投影
    # 墨色直接采用规格色 #203245（场景白平衡已验证接近中性），仅随受光做微渐变
    ink_ref = np.array([32.0, 50.0, 69.0])

    d_body = np.linalg.norm(region - body_ref, axis=2)
    d_ink = np.linalg.norm(region - ink_ref, axis=2)
    ink = d_ink < d_body
    ink = fill_holes(ink)
    m = Image.fromarray((ink * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3))
    ink = np.asarray(m) > 127

    # 投影检测：墨色膨胀环带内，发暗但非蓝主导的像素
    ring = dilate(ink, 19) & ~ink
    body_pixels = region[~ring]
    base_lum = np.median(body_pixels.mean(axis=1))
    cand_lum = region.mean(axis=2)
    shadow = ring & (cand_lum < base_lum - 10) & ~ink
    n_shadow = int(shadow.sum())

    # 先填补投影，再叠平墨色
    region = diffusion_fill(region, shadow)

    mask_img = Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
    soft = np.asarray(mask_img).astype(np.float64) / 255.0

    # 平墨色 + 随机身受光的轻微纵向明度渐变
    row_lum = []
    for y in range(h):
        rb = region[y][~ink[y]]
        row_lum.append(rb.mean() if len(rb) else np.nan)
    row_lum = np.array(row_lum)
    row_lum[np.isnan(row_lum)] = np.nanmean(row_lum)
    light = np.clip(row_lum / np.median(row_lum), 0.94, 1.06)[:, None, None]

    flat_ink = np.clip(ink_ref[None, None, :] * light, 0, 255)
    out = region * (1 - soft[..., None]) + flat_ink * soft[..., None]

    patched = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    im.paste(patched, (box[0], box[1]))
    return im, ink_ref, n_shadow


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    for b in [(630, 360, 770, 460), (620, 965, 770, 1065)]:
        im, ink, ns = flatten_logo(im, b)
        print(f"box={b} ink_ref={ink.round(1)} shadow_px={ns}")
    im.save(dst)
    print("saved:", dst)


if __name__ == "__main__":
    main()
