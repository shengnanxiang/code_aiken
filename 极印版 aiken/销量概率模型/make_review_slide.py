# -*- coding: utf-8 -*-
"""生成评审整页：AiKen 销量概率分布（v0.4）+ S1 回测 + DJI 回测"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261027)

# ============ 载入 v0.4 与 S1 回测数据 ============
D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz")
y1, y3 = D["y1"], D["y3"]
y1_b = D["y1_b"]
B = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_backtest.npz")
s1_y1 = B["y1"]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

W = lambda v: f"{v/1e4:.2f}万"

# DJI 回测分布（与方法论页一致）
rng_d = np.random.default_rng(7)
m_dji = rng_d.lognormal(mean=np.log(600_000), sigma=1.15, size=200_000)

# ============ SVG：首年分布（直方图 + 三档锚 + Best 阴影） ============
def hist_svg(data, w=620, h=210, nbins=46, vmax=45_000,
             marks=None, shade=None, xticks=None):
    ml, mr, mt, mb = 46, 16, 24, 40
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    counts, _ = np.histogram(data, bins=nbins, range=(0, vmax))
    cmax = counts.max()
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#EFEFEF" stroke-width="1"/>')
    bw = (x1_ - x0) / nbins
    for i, c in enumerate(counts):
        bh = (c / cmax) * (y0 - y1p)
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.86:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.82" rx="1"/>')
    if shade:
        v, lab = shade
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<rect x="{sx:.1f}" y="{y1p}" width="{x1_-sx:.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.10"/>')
        P.append(f'<line x1="{sx:.1f}" y1="{y1p}" x2="{sx:.1f}" y2="{y0}" stroke="#EC008C" stroke-width="1.5" stroke-dasharray="5 4"/>')
        P.append(f'<text x="{(sx+x1_)/2:.0f}" y="{mt-8}" text-anchor="middle" font-size="11.5" fill="#EC008C" font-weight="bold">{lab}</text>')
    for v, label, color, dash in (marks or []):
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<line x1="{sx:.1f}" y1="{y1p}" x2="{sx:.1f}" y2="{y0}" stroke="{color}" stroke-width="1.8" stroke-dasharray="{dash}"/>')
        P.append(f'<text x="{sx:.1f}" y="{y0+16}" text-anchor="middle" font-size="11" fill="{color}" font-weight="bold">{label}</text>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in (xticks or []):
        sx = x0 + (xv / vmax) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+30}" text-anchor="middle" font-size="10.5" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x0-6}" y="{y1p+4}" text-anchor="end" font-size="10" fill="#6B6B6B">概率</text>')
    P.append(f'<text x="{x0-6}" y="{y0+4}" text-anchor="end" font-size="10" fill="#6B6B6B">密度</text>')
    P.append('</svg>')
    return "".join(P)

SVG_Y1 = hist_svg(y1, vmax=45_000,
    marks=[(pct(y1,10), "P10", "#C0392B", "4 3"),
           (pct(y1,50), "P50", "#111", "4 3"),
           (pct(y1,90), "P90", "#7A4FA0", "4 3")],
    shade=(pct(y1,90), f"P(≥Best) = 10%"),
    xticks=[(0,"0"),(1e4,"1万"),(2e4,"2万"),(3e4,"3万"),(4e4,"4万")])

SVG_Y3 = hist_svg(y3, vmax=140_000,
    marks=[(pct(y3,10), "P10", "#C0392B", "4 3"),
           (pct(y3,50), "P50", "#111", "4 3"),
           (pct(y3,90), "P90", "#7A4FA0", "4 3")],
    shade=(100_000, f"P(≥10万) = {prob(y3,100_000)*100:.0f}%"),
    xticks=[(0,"0"),(3e4,"3万"),(6e4,"6万"),(9e4,"9万"),(12e4,"12万")])

# ============ SVG：S1 回测图 ============
def s1_svg(w=560, h=268):
    ml, mr, mt, mb = 42, 14, 14, 82
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    vmax = 30_000
    counts, _ = np.histogram(s1_y1, bins=56, range=(0, vmax))
    cmax = counts.max()
    def X(v): return x0 + (min(v, vmax) / vmax) * (x1_ - x0)
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#EFEFEF" stroke-width="1"/>')
    bw = (x1_ - x0) / 56
    for i, c in enumerate(counts):
        bh = (c / cmax) * (y0 - y1p)
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.8:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.78" rx="1"/>')
    # 内部预测 25000
    P.append(f'<line x1="{X(25000):.1f}" y1="{y1p}" x2="{X(25000):.1f}" y2="{y0}" stroke="#B8860B" stroke-width="2" stroke-dasharray="5 4"/>')
    # 实际宽口径 7285
    P.append(f'<line x1="{X(7285):.1f}" y1="{y1p}" x2="{X(7285):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2.2"/>')
    P.append(f'<rect x="{x0}" y="{y1p}" width="{X(7285)-x0:.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.07"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"),(5000,"5千"),(10000,"1万"),(15000,"1.5万"),(20000,"2万"),(25000,"2.5万")]:
        P.append(f'<text x="{X(xv):.0f}" y="{y0+16}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    # 图例行（两行，独立空间确保完整显示）
    ly = y0 + 36
    P.append(f'<line x1="{x0:.0f}" y1="{ly-3}" x2="{x0+20:.0f}" y2="{ly-3}" stroke="#B8860B" stroke-width="2" stroke-dasharray="5 3"/>')
    P.append(f'<text x="{x0+25:.0f}" y="{ly}" font-size="10" fill="#333">内部预测 25,000（P92 · 仅8%概率可达成）</text>')
    ly2 = ly + 17
    P.append(f'<line x1="{x0:.0f}" y1="{ly2-3}" x2="{x0+20:.0f}" y2="{ly2-3}" stroke="#EC008C" stroke-width="2.4"/>')
    P.append(f'<text x="{x0+25:.0f}" y="{ly2}" font-size="10" fill="#333">实际（宽口径 ~7,300）落在 P5 以下</text>')
    P.append(f'<text x="{x1_}" y="{y1p-2}" text-anchor="end" font-size="9.5" fill="#6B6B6B">事前分布：仅用 N 系数据（S1 上市前可得信息）</text>')
    P.append('</svg>')
    return "".join(P)

# ============ SVG：DJI 回测图（图例版，同方法论页） ============
def dji_svg(w=560, h=268):
    ml, mr, mt, mb = 40, 14, 14, 82
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    vmax = 12_000_000
    counts, _ = np.histogram(m_dji, bins=70, range=(0, vmax))
    cmax = counts.max()
    def X(v): return x0 + (min(v, vmax) / vmax) * (x1_ - x0)
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#EFEFEF" stroke-width="1"/>')
    bw = (x1_ - x0) / 70
    for i, c in enumerate(counts):
        bh = (c / cmax) * (y0 - y1p)
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.8:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.78" rx="1"/>')
    P.append(f'<rect x="{X(300000):.1f}" y="{y1p}" width="{X(400000)-X(300000):.1f}" height="{y0-y1p}" fill="#6B6B6B" fill-opacity="0.25"/>')
    P.append(f'<line x1="{X(1e6):.1f}" y1="{y1p}" x2="{X(1e6):.1f}" y2="{y0}" stroke="#B8860B" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(5e6):.1f}" y1="{y1p}" x2="{X(5e6):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(1e7):.1f}" y1="{y1p}" x2="{X(1e7):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2.2"/>')
    P.append(f'<rect x="{X(1e7):.1f}" y="{y1p}" width="{x1_-X(1e7):.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.10"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"),(2e6,"200万"),(4e6,"400万"),(6e6,"600万"),(8e6,"800万"),(1e7,"1000万")]:
        P.append(f'<text x="{X(xv):.0f}" y="{y0+16}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    ly1 = y0 + 36
    items1 = [("#6B6B6B","rect","内部预期 30–40万"), ("#B8860B","dash","上调 100万"), ("#EC008C","dash","2024 实售 500万"), ("#EC008C","solid","累计 1000万+")]
    lx = x0
    for color, style, label in items1:
        if style == "rect":
            P.append(f'<rect x="{lx:.0f}" y="{ly1-7}" width="18" height="9" fill="{color}" fill-opacity="0.3"/>')
        elif style == "dash":
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2" stroke-dasharray="5 3"/>')
        else:
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2.4"/>')
        P.append(f'<text x="{lx+23:.0f}" y="{ly1}" font-size="10" fill="#333">{label}</text>')
        lx += 23 + len(label) * 10.5 + 22
    ly2 = ly1 + 17
    P.append(f'<text x="{x0:.0f}" y="{ly2}" font-size="9.5" fill="#6B6B6B">事前分布：参照前代 Pocket 2（对数正态）·  1000万+ 位于 P99.3 右尾（保留概率 0.7%）</text>')
    P.append('</svg>')
    return "".join(P)

SVG_S1 = s1_svg()
SVG_DJI = dji_svg()

# ============ SVG：三步条小图 ============
def prior_bars_svg(w=280, h=64):
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    rows = [("m", 0.10, 0.30, 0.82), ("q", 0.13, 0.33, 0.83)]
    y = 18
    for name, f_lo, f_mid, f_hi in rows:
        x0, x1_ = 26, w - 30
        P.append(f'<text x="2" y="{y+3}" font-size="10" fill="#111" font-weight="bold">{name}</text>')
        P.append(f'<rect x="{x0}" y="{y-5}" width="{x1_-x0}" height="10" rx="5" fill="#EFEFEF"/>')
        P.append(f'<rect x="{x0+f_lo*(x1_-x0):.0f}" y="{y-5}" width="{(f_hi-f_lo)*(x1_-x0):.0f}" height="10" rx="5" fill="#00C2C2" fill-opacity="0.45"/>')
        P.append(f'<circle cx="{x0+f_mid*(x1_-x0):.0f}" cy="{y}" r="4" fill="#EC008C"/>')
        y += 26
    P.append(f'<text x="2" y="{h-4}" font-size="8.5" fill="#9a9a9a">● P50 ｜ 条带 = P10–P90 先验区间</text>')
    P.append('</svg>')
    return "".join(P)

def s_curve_svg(w=280, h=72):
    m, p, q = 100, 0.06, 0.85
    ml, mr, mt, mb = 24, 8, 8, 14
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    cum = [m*(1-np.exp(-(p+q)*t/12))/(1+(q/p)*np.exp(-(p+q)*t/12)) for t in range(61)]
    vmax_v = m * 1.12
    pts = [f"{x0+(tt/60)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(cum)]
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    my = y0 - (m / vmax_v) * (y0 - y1p)
    P.append(f'<line x1="{x0}" y1="{my:.1f}" x2="{x1_}" y2="{my:.1f}" stroke="#FFC400" stroke-width="1.2" stroke-dasharray="4 3"/>')
    P.append(f'<text x="{x1_-1}" y="{my-3:.1f}" text-anchor="end" font-size="8.5" fill="#B8860B" font-weight="bold">m 天花板</text>')
    P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="2"/>')
    px = x0 + (6 / 60) * (x1_ - x0)
    P.append(f'<rect x="{x0}" y="{y1p}" width="{px-x0:.1f}" height="{y0-y1p}" fill="#00C2C2" fill-opacity="0.10"/>')
    P.append(f'<text x="{(x0+px)/2:.0f}" y="{y0-4}" text-anchor="middle" font-size="8.5" fill="#007C7C" font-weight="bold">投放</text>')
    P.append(f'<text x="{(px+x1_)/2:.0f}" y="{y0-4}" text-anchor="middle" font-size="8.5" fill="#7A4FA0" font-weight="bold">口碑</text>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1"/>')
    for tt, xl in [(0,"0"),(30,"30月"),(60,"60月")]:
        sx = x0 + (tt / 60) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+11}" text-anchor="middle" font-size="8" fill="#6B6B6B">{xl}</text>')
    P.append('</svg>')
    return "".join(P)

def fan_svg(w=280, h=72):
    ml, mr, mt, mb = 24, 8, 8, 14
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    vmax_v = 140_000
    paths = D["paths"]
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    idx = rng.choice(len(paths), 10, replace=False)
    for i in idx:
        pts = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(paths[i])]
        P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#B8B8B8" stroke-width="1" opacity="0.5"/>')
    for lo, hi, op in [(10, 90, 0.12), (25, 75, 0.18)]:
        plo = np.percentile(paths, lo, axis=0); phi = np.percentile(paths, hi, axis=0)
        band = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(phi)]
        band += [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in reversed(list(enumerate(plo)))]
        P.append(f'<polygon points="{" ".join(band)}" fill="#00C2C2" fill-opacity="{op}"/>')
    p50c = np.percentile(paths, 50, axis=0)
    pts = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(p50c)]
    P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="1.8"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1"/>')
    for tt, xl in [(0,"0"),(18,"18月"),(36,"36月")]:
        sx = x0 + (tt / 36) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+11}" text-anchor="middle" font-size="8" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x1_-1}" y="{y1p+8}" text-anchor="end" font-size="8" fill="#6B6B6B">8,000 条轨迹</text>')
    P.append('</svg>')
    return "".join(P)

SVG_PRIOR_MINI = prior_bars_svg()
SVG_SCURVE_MINI = s_curve_svg()
SVG_FAN_MINI = fan_svg()

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布 · 评审页 v0.4</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { background:#3a3a3a; }
  body { margin:0; }
  #slide { width:1280px; max-width:96vw; margin:24px auto; background:#FFF; font-family:"Microsoft YaHei",sans-serif;
           color:#111; box-shadow:0 8px 40px rgba(0,0,0,.45); }
  .pad { padding:22px 32px 16px; display:flex; flex-direction:column; }
  .hd { display:flex; align-items:flex-end; justify-content:space-between; border-bottom:2.5px solid #111; padding-bottom:8px; }
  .hd h1 { font-size:25px; letter-spacing:.5px; }
  .hd h1 em { color:#EC008C; font-style:normal; }
  .hd .tag { font-size:11px; color:#fff; background:#111; padding:4px 10px; border-radius:3px; letter-spacing:1px; }
  .sec { margin-top:14px; display:flex; align-items:center; gap:10px; }
  .sec .bar { width:5px; height:19px; background:#EC008C; border-radius:2px; }
  .sec h2 { font-size:16.5px; letter-spacing:1px; }
  .sec .n { font-size:10.5px; color:#9a9a9a; }
  .outrow { display:flex; gap:14px; margin-top:8px; }
  .out { flex:1; border:2px solid #111; border-radius:8px; padding:8px 12px 4px; display:flex; flex-direction:column; background:#fff; }
  .out .step { font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .out h3 { font-size:15px; margin:4px 0 0; }
  .out .nums { font-size:12px; margin-top:2px; font-variant-numeric:tabular-nums; }
  .out .nums b { color:#111; }
  .out .chart { flex:1; display:flex; align-items:center; justify-content:center; }
  .out .chart svg { width:100%; max-height:200px; }
  .kpirow { display:flex; gap:10px; margin-top:10px; }
  .kpi { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:8px 12px; background:#fff; }
  .kpi .k { font-size:10px; color:#6B6B6B; letter-spacing:.5px; }
  .kpi .v { font-size:17px; font-weight:bold; margin-top:2px; font-variant-numeric:tabular-nums; }
  .kpi .v em { color:#EC008C; font-style:normal; }
  .kpi .s { font-size:9.8px; color:#9a9a9a; margin-top:2px; }
  .btrow { display:flex; gap:14px; margin-top:8px; align-items:stretch; }
  .bt { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:9px 13px; background:#fff; display:flex; flex-direction:column; }
  .bt .step { font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .bt h4 { font-size:14px; margin:4px 0 2px; }
  .bt .fig { margin-top:2px; display:flex; align-items:center; flex:1; }
  .bt .fig svg { width:100%; max-height:268px; }
  .bt .cc { font-size:10.8px; line-height:1.6; color:#333; margin-top:4px; }
  .bt .cc b { color:#EC008C; }
  /* 方法论三步条 */
  .mrow { display:flex; gap:0; margin-top:12px; align-items:stretch; }
  .mstep { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:8px 13px 7px; background:#fff; display:flex; flex-direction:column; }
  .mstep .no { font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .mstep h5 { font-size:13.5px; margin:4px 0 2px; }
  .mstep p { font-size:10.5px; color:#555; line-height:1.5; }
  .mstep p b { color:#111; }
  .mstep .fig { margin:3px 0 1px; display:flex; align-items:center; justify-content:center; }
  .mstep .fig svg { width:100%; max-height:72px; }
  .marrow { display:flex; align-items:center; justify-content:center; width:28px; flex:none; color:#EC008C; font-size:20px; font-weight:bold; }
  .ft { margin-top:12px; border-top:1.5px solid #111; padding-top:8px; display:flex; justify-content:space-between; }
  .ft .loop { font-size:11.5px; }
  .ft .loop b { color:#EC008C; }
  .ft .note { font-size:9.5px; color:#9a9a9a; text-align:right; line-height:1.4; }
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>AiKen 销量概率分布 <em>· v0.4（实测校准）</em></h1>
    <div class="tag">SI-4 · 试点新的销量预测模型</div>
  </div>

  <div class="mrow">
    <div class="mstep">
      <span class="no">步骤 1 · RCF 参照类</span>
      <h5>参数从哪来</h5>
      <div class="fig">__SVG_PRIOR_MINI__</div>
      <p>同价位带（¥400–1,300）同类产品定参数区间：<b>instax mini</b>（¥599 同价位）定市场潜力天花板，<b>Flashback One35</b>（¥749 直接对标）定存活基线；漏斗参数锚 <b>S1 实测</b>（同属需教育市场的新品类）。</p>
    </div>
    <div class="marrow">→</div>
    <div class="mstep">
      <span class="no">步骤 2 · Bass 扩散</span>
      <h5>曲线长什么样</h5>
      <div class="fig">__SVG_SCURVE_MINI__</div>
      <p>耐用品扩散经典模型（Bass 1969）。三参数：**m** 市场潜力（天花板）· **p** 投放驱动（冷启动，由漏斗反解）· **q** 口碑驱动（起飞斜率）。前 6 个月投流漏斗钉住 p，之后口碑接管。</p>
    </div>
    <div class="marrow">→</div>
    <div class="mstep">
      <span class="no">步骤 3 · 8,000 次测算</span>
      <h5>不确定性有多大</h5>
      <div class="fig">__SVG_FAN_MINI__</div>
      <p>参数不取单点，按参照类区间随机抽 <b>8,000 组</b>，各跑一条扩散曲线，统计成销量<b>概率分布</b>。三档场景（Worst / Normal / Best）= 分布上的 <b>P10 / P50 / P90</b> 三个执行锚。</p>
    </div>
  </div>

  <div class="sec"><div class="bar"></div><h2>首年与三年销量概率分布</h2><span class="n">8,000 次蒙特卡洛 · 漏斗参数 S1 实测校准 · 三档锚 = P10 / P50 / P90</span></div>
  <div class="outrow">
    <div class="out">
      <span class="step">首年</span>
      <h3>首年销量概率分布</h3>
      <div class="nums">P10 <b>__Y1_P10__</b> ｜ P50 <b>__Y1_P50__</b> ｜ P90 <b>__Y1_P90__</b></div>
      <div class="chart">__SVG_Y1__</div>
    </div>
    <div class="out">
      <span class="step">三年</span>
      <h3>三年累计销量概率分布</h3>
      <div class="nums">P10 <b>__Y3_P10__</b> ｜ P50 <b>__Y3_P50__</b> ｜ P90 <b>__Y3_P90__</b></div>
      <div class="chart">__SVG_Y3__</div>
    </div>
  </div>

  <div class="kpirow">
    <div class="kpi"><div class="k">Worst 锚（P10）</div><div class="v">__Y1_P10__<em> 台</em></div><div class="s">月销 ≈ __M_WORST__ · 供应链备货下界</div></div>
    <div class="kpi"><div class="k">Normal 锚（P50）</div><div class="v">__Y1_P50__<em> 台</em></div><div class="s">月销 ≈ __M_NORMAL__ · 财务测算基准</div></div>
    <div class="kpi"><div class="k">Best 锚（P90）</div><div class="v">__Y1_P90__<em> 台</em></div><div class="s">月销 ≈ __M_BEST__ · 冲刺带</div></div>
    <div class="kpi"><div class="k">预算杠杆 ×1.5</div><div class="v">P50 → __Y1B_P50__</div><div class="s">P(≥Best) 10%→46% · 花钱买概率增量</div></div>
  </div>

  <div class="sec"><div class="bar"></div><h2>回测检验：方法论的两次实证</h2><span class="n">一次外部爆款 · 一次我们自己</span></div>
  <div class="btrow">
    <div class="bt">
      <span class="step">回测 1 · 内部</span>
      <h4>S1 贴纸一体机（¥1,799 · 2026-04 上市）</h4>
      <div class="fig">__SVG_S1__</div>
      <div class="cc">用 AiKen 同款方法，站在 S1 上市前夜（仅用 N 系数据）建模：<b>内部点预测 25,000 位于事前分布 P92——模型当时就会预警「仅 8% 概率可达成」</b>；实际（宽口径 ~7,300）落在 P5 以下，验证怀疑。偏差根因：N 系（已教育品类）参数对 S1（需教育品类）系统性高估 2 倍——<b>这直接决定了 AiKen 锚 S1 而非 N 系</b>，并已转化为 v0.4 参数余量。</div>
    </div>
    <div class="bt">
      <span class="step">回测 2 · 外部</span>
      <h4>DJI Osmo Pocket 3（¥3,499 · 2023-10 发布）</h4>
      <div class="fig">__SVG_DJI__</div>
      <div class="cc">事前分布（参照前代 Pocket 2）P50=60 万，与大疆内部预期（30–40 万，P27–P36）同水平；实际 2024 实售 <b>500 万（P96.7）</b>、累计破 <b>1000 万（P99.3 右尾）</b>。没有人能预知爆发——大疆自己也 miss 了 25 倍——但分布右尾以 0.7% 概率保留了千万级结果：<b>点预测会直接排除它，分布不会</b>。</div>
    </div>
  </div>

  <div class="sec"><div class="bar"></div><h2>Checkpoint 闭环</h2><span class="n">30 / 90 天真实数据 → 分布收窄 → 再决策</span></div>
  <div class="kpirow">
    <div class="kpi"><div class="k">首月观测 = Normal 月销时</div><div class="v">区间收窄 <em>41%</em></div><div class="s">m 的 P10–P90：4.5万–26.4万 → 8.3万–21.3万</div></div>
    <div class="kpi"><div class="k">单台净贡献（30% 费用口径）</div><div class="v">51.9 <em>元</em></div><div class="s">ASP 不含税 431.2 × 70% − BOM 250</div></div>
    <div class="kpi"><div class="k">首年投入覆盖（P50）</div><div class="v">24<em>%</em></div><div class="s">投入 477.4 万（新 Budget）· 品牌投资型定位（非回本导向）</div></div>
    <div class="kpi"><div class="k">P(三年累计 ≥10万)</div><div class="v">__P3_10W__<em>%</em></div><div class="s">三年 P50 = 63,130 台</div></div>
  </div>

  <div class="ft">
    <div class="loop"><b>Checkpoint 闭环</b>：上市 30 / 90 天真实数据 → 更新 m·p·q → 分布收窄 → 预算/动作再决策 ↺</div>
    <div class="note">v0.4 参数：CPM 三角(38,45,65) · CTR 三角(1.8%,2.3%,3.0%) · CVR 三角(0.9%,1.4%,2.2%)（S1 实测+回测余量）<br>参照类：instax mini / Flashback One35 / Kodak / Paper Shoot（同价位带）+ S1（漏斗锚）· Bass (1969) · 8,000 次蒙特卡洛</div>
  </div>

</div></div>
</body>
</html>
"""

html = (HTML
    .replace("__SVG_PRIOR_MINI__", SVG_PRIOR_MINI)
    .replace("__SVG_SCURVE_MINI__", SVG_SCURVE_MINI)
    .replace("__SVG_FAN_MINI__", SVG_FAN_MINI)
    .replace("__SVG_Y1__", SVG_Y1)
    .replace("__SVG_Y3__", SVG_Y3)
    .replace("__SVG_S1__", SVG_S1)
    .replace("__SVG_DJI__", SVG_DJI)
    .replace("__Y1_P10__", f"{pct(y1,10):,.0f}")
    .replace("__Y1_P50__", f"{pct(y1,50):,.0f}")
    .replace("__Y1_P90__", f"{pct(y1,90):,.0f}")
    .replace("__Y3_P10__", f"{pct(y3,10)/1e4:.1f}万")
    .replace("__Y3_P50__", f"{pct(y3,50)/1e4:.1f}万")
    .replace("__Y3_P90__", f"{pct(y3,90)/1e4:.1f}万")
    .replace("__M_WORST__", f"{pct(y1,10)/12:,.0f}")
    .replace("__M_NORMAL__", f"{pct(y1,50)/12:,.0f}")
    .replace("__M_BEST__", f"{pct(y1,90)/12:,.0f}")
    .replace("__Y1B_P50__", f"{pct(y1_b,50):,.0f}")
    .replace("__P3_10W__", f"{prob(y3,100_000)*100:.0f}")
)

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率分布_评审页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", OUT)
print(f"key: Y1 P10={pct(y1,10):,.0f} P50={pct(y1,50):,.0f} P90={pct(y1,90):,.0f} | Y3 P50={pct(y3,50):,.0f} | boost P50={pct(y1_b,50):,.0f}")
