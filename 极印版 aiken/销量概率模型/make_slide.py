# -*- coding: utf-8 -*-
"""
方法论说明页 v2 —— 按用户六点意见重构
1. 删废话（副标题口号、背景块、Sean 上限注）
2. 参照类改为「同价位带优先」：DJI 降级为右尾例证
3. 输出层独立成行（不再与层1-3同排）
4. 输出层双图：首年 + 三年
5. 杠杆层删右侧示意图
6. 新增 DJI Pocket 3 回测检验
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261022)
N_SIM = 8000
T_MONTHS = 36

# ============ v0.2 同参数重算 ============
m_prior = rng.lognormal(mean=np.log(120_000), sigma=0.90, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B_budget = rng.uniform(120, 280, size=N_SIM) * 10_000
CPM = rng.triangular(45, 60, 75, size=N_SIM)
CTR = rng.triangular(0.015, 0.022, 0.035, size=N_SIM)
CVR = rng.triangular(0.012, 0.018, 0.028, size=N_SIM)
exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    lo = np.full_like(m, 1e-5); hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        too_small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)

p_solved = solve_p(m_prior, q_prior, s6)
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1 = paths[:, 11]; y3 = paths[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ---- 杠杆演示：预算 x1.5 ----
s6_b = np.minimum(s6_raw * 1.5, m_prior * 0.55)
p_b = solve_p(m_prior, q_prior, s6_b)
paths_b = bass_cum_year(m_prior[:, None], p_b[:, None], q_prior[:, None], t_year[None, :])
y1_b = paths_b[:, 11]; y3_b = paths_b[:, 35]

# ---- 杠杆演示：q x1.15（KOC 种草）----
q_k = np.clip(q_prior * 1.15, 0.18, 0.78)
p_k = solve_p(m_prior, q_k, s6)
paths_k = bass_cum_year(m_prior[:, None], p_k[:, None], q_k[:, None], t_year[None, :])
y1_k = paths_k[:, 11]; y3_k = paths_k[:, 35]

# ---- 杠杆演示：m x1.5（品类破圈）----
paths_m = bass_cum_year((m_prior * 1.5)[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1_m = paths_m[:, 11]; y3_m = paths_m[:, 35]

# ============ DJI Pocket 3 回测 ============
rng_d = np.random.default_rng(7)
m_dji = rng_d.lognormal(mean=np.log(600_000), sigma=1.15, size=200_000)
p_dji_30 = float((m_dji < 300_000).mean() * 100)
p_dji_40 = float((m_dji < 400_000).mean() * 100)
p_dji_100 = float((m_dji < 1_000_000).mean() * 100)
p_dji_5m = float((m_dji < 5_000_000).mean() * 100)
p_dji_10m = float((m_dji < 10_000_000).mean() * 100)

print("=== v0.2 关键数字 ===")
print(f"y1: P5={pct(y1,5)/1e4:.2f} P50={pct(y1,50)/1e4:.2f} P95={pct(y1,95)/1e4:.2f}")
print(f"y3: P5={pct(y3,5)/1e4:.2f} P50={pct(y3,50)/1e4:.2f} P95={pct(y3,95)/1e4:.2f}")
print(f"P(y1>=3.6万)={prob(y1,36000)*100:.1f}%  P(y3>=10万)={prob(y3,100000)*100:.1f}%")
print(f"预算x1.5: y1 P50 {pct(y1,50)/1e4:.2f}->{pct(y1_b,50)/1e4:.2f}  P(>=3.6万) {prob(y1,36000)*100:.0f}%->{prob(y1_b,36000)*100:.0f}%  y3 P50 {pct(y3,50)/1e4:.2f}->{pct(y3_b,50)/1e4:.2f}")
print(f"q x1.15 : y1 P50 {pct(y1,50)/1e4:.2f}->{pct(y1_k,50)/1e4:.2f}  y3 P50 {pct(y3,50)/1e4:.2f}->{pct(y3_k,50)/1e4:.2f}  P(y3>=10万) {prob(y3,100000)*100:.0f}%->{prob(y3_k,100000)*100:.0f}%")
print(f"m x1.5  : y3 P50 {pct(y3,50)/1e4:.2f}->{pct(y3_m,50)/1e4:.2f}")
print("=== DJI 回测 ===")
print(f"内部预期30-40万: P{p_dji_30:.0f}-P{p_dji_40:.0f}  上调100万: P{p_dji_100:.0f}  2024实售500万: P{p_dji_5m:.1f}  累计1000万: P{p_dji_10m:.2f}")
print(f"P(m>=1000万)={100-p_dji_10m:.2f}%")

# ============ SVG 生成 ============
def hist_svg(data, w=560, h=200, nbins=44, vmax=80_000,
             marks=None, shade=None, xticks=None, xlabel="", ylab="概率密度"):
    ml, mr, mt, mb = 42, 14, 26, 40
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    counts, edges = np.histogram(data, bins=nbins, range=(0, vmax))
    cmax = counts.max()
    P = []
    P.append(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">')
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
        # 标签放图外顶部（mt 预留区），避免与柱体重叠
        P.append(f'<text x="{(sx+x1_)/2:.0f}" y="{mt-8}" text-anchor="middle" font-size="11.5" fill="#EC008C" font-weight="bold">{lab}</text>')
    for v, label, color, dash in (marks or []):
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<line x1="{sx:.1f}" y1="{y1p}" x2="{sx:.1f}" y2="{y0}" stroke="{color}" stroke-width="1.8" stroke-dasharray="{dash}"/>')
        P.append(f'<text x="{sx:.1f}" y="{y0+16}" text-anchor="middle" font-size="11" fill="{color}" font-weight="bold">{label}</text>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in (xticks or []):
        sx = x0 + (xv / vmax) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+30}" text-anchor="middle" font-size="10.5" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x1_}" y="{y0+30}" text-anchor="end" font-size="10" fill="#9a9a9a">{xlabel}</text>')
    P.append(f'<text x="{x0-6}" y="{y1p+4}" text-anchor="end" font-size="10" fill="#6B6B6B">{ylab}</text>')
    P.append('</svg>')
    return "".join(P)

def s_curve_svg(w=300, h=132):
    # 品类代表参数展示典型 S 形态：冷启动缓、12–24 月最陡（口碑起飞）、36 月后趋缓。
    # 归一化 m=100（示意，坐标按 60 个月展示完整 S 形），非本项目实参。
    m, p, q = 100, 0.06, 0.85
    T_SHOW = 60  # 展示 60 个月，让 S 形完整呈现
    ml, mr, mt, mb = 30, 10, 10, 20
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    cum = bass_cum_year(m, p, q, np.arange(0, T_SHOW + 1) / 12.0)
    vmax_v = m * 1.12
    pts = [f"{x0+(tt/T_SHOW)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(cum)]
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    my = y0 - (m / vmax_v) * (y0 - y1p)
    P.append(f'<line x1="{x0}" y1="{my:.1f}" x2="{x1_}" y2="{my:.1f}" stroke="#FFC400" stroke-width="1.3" stroke-dasharray="5 4"/>')
    P.append(f'<text x="{x1_-2}" y="{my-4:.1f}" text-anchor="end" font-size="10" fill="#B8860B" font-weight="bold">m 市场潜力</text>')
    P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="2.2"/>')
    px = x0 + (6 / T_SHOW) * (x1_ - x0)
    P.append(f'<rect x="{x0}" y="{y1p}" width="{px-x0:.1f}" height="{y0-y1p}" fill="#00C2C2" fill-opacity="0.10"/>')
    P.append(f'<text x="{(x0+px)/2:.0f}" y="{y0-6}" text-anchor="middle" font-size="9.5" fill="#007C7C" font-weight="bold">投放</text>')
    P.append(f'<text x="{(px+x1_)/2:.0f}" y="{y0-6}" text-anchor="middle" font-size="9.5" fill="#7A4FA0" font-weight="bold">口碑</text>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.2"/>')
    for tt, xl in [(0,"0"),(12,"12月"),(24,"24月"),(36,"36月"),(48,"48月"),(60,"60月")]:
        sx = x0 + (tt / T_SHOW) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+14}" text-anchor="middle" font-size="9" fill="#6B6B6B">{xl}</text>')
    P.append('</svg>')
    return "".join(P)

def fan_svg(w=300, h=132):
    ml, mr, mt, mb = 30, 10, 10, 20
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    vmax_v = 200_000
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    idx = rng.choice(N_SIM, 16, replace=False)
    for i in idx:
        pts = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(paths[i])]
        P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#B8B8B8" stroke-width="1" opacity="0.55"/>')
    for lo, hi, op in [(5, 95, 0.10), (25, 75, 0.17)]:
        plo = np.percentile(paths, lo, axis=0); phi = np.percentile(paths, hi, axis=0)
        band = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(phi)]
        band += [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in reversed(list(enumerate(plo)))]
        P.append(f'<polygon points="{" ".join(band)}" fill="#00C2C2" fill-opacity="{op}"/>')
    p50c = np.percentile(paths, 50, axis=0)
    pts = [f"{x0+(tt/36)*(x1_-x0):.1f},{y0-(min(v,vmax_v)/vmax_v)*(y0-y1p):.1f}" for tt, v in enumerate(p50c)]
    P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="2"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.2"/>')
    for tt, xl in [(0,"0"),(12,"12月"),(24,"24月"),(36,"36月")]:
        sx = x0 + (tt / 36) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+14}" text-anchor="middle" font-size="9" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x1_-2}" y="{y1p+10}" text-anchor="end" font-size="9" fill="#6B6B6B">8000 条轨迹</text>')
    P.append('</svg>')
    return "".join(P)

def prior_bars_svg(w=280, h=126):
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    rows = [
        ("m 市场潜力", "3.9万", "12.1万", "36.8万", 0.12, 0.30, 0.80),
        ("q 口碑系数", "0.29", "0.42", "0.55", 0.14, 0.33, 0.81),
    ]
    y = 22
    for name, lo_, mid, hi, f_lo, f_mid, f_hi in rows:
        # 标签放条带上方一行，值放条带两侧——彻底避免遮挡
        x0, x1_ = 10, w - 34
        P.append(f'<text x="{x0}" y="{y-9}" font-size="10.5" fill="#111" font-weight="bold">{name}</text>')
        P.append(f'<text x="{x1_}" y="{y-9}" text-anchor="end" font-size="9.5" fill="#6B6B6B">P10 {lo_} · P90 {hi}</text>')
        # 灰色底轨（全宽）
        P.append(f'<rect x="{x0}" y="{y-5}" width="{x1_-x0}" height="11" rx="5.5" fill="#EFEFEF"/>')
        # 青绿色 P10–P90 先验区间
        P.append(f'<rect x="{x0+f_lo*(x1_-x0):.0f}" y="{y-5}" width="{(f_hi-f_lo)*(x1_-x0):.0f}" height="11" rx="5.5" fill="#00C2C2" fill-opacity="0.45"/>')
        # 粉色 P50 圆点
        P.append(f'<circle cx="{x0+f_mid*(x1_-x0):.0f}" cy="{y+0.5}" r="4" fill="#EC008C"/>')
        y += 42
    # 三色图例（与条带视觉样式一一对应）
    ly = h - 10
    P.append(f'<rect x="10" y="{ly-8}" width="26" height="8" rx="4" fill="#00C2C2" fill-opacity="0.45"/>')
    P.append(f'<text x="42" y="{ly}" font-size="9.5" fill="#333">P10–P90 先验区间</text>')
    P.append(f'<circle cx="196" cy="{ly-4}" r="4" fill="#EC008C"/>')
    P.append(f'<text x="206" y="{ly}" font-size="9.5" fill="#333">P50 中位数</text>')
    P.append(f'<rect x="272" y="{ly-8}" width="26" height="8" rx="4" fill="#EFEFEF"/>')
    P.append(f'<text x="304" y="{ly}" font-size="9.5" fill="#6B6B6B">取值范围</text>')
    P.append('</svg>')
    return "".join(P)

def dji_svg(w=560, h=210):
    """DJI 回测分布图：图内只画参考线，文字全部放图例行（杜绝遮挡）"""
    ml, mr, mt, mb = 40, 14, 14, 56
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    vmax = 12_000_000
    counts, _ = np.histogram(m_dji, bins=70, range=(0, vmax))
    cmax = counts.max()
    def X(v): return x0 + (min(v, vmax) / vmax) * (x1_ - x0)
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    # 网格线
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#EFEFEF" stroke-width="1"/>')
    # 柱
    bw = (x1_ - x0) / 70
    for i, c in enumerate(counts):
        bh = (c / cmax) * (y0 - y1p)
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.8:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.78" rx="1"/>')
    # 参考线（不带图内文字）
    P.append(f'<rect x="{X(300000):.1f}" y="{y1p}" width="{X(400000)-X(300000):.1f}" height="{y0-y1p}" fill="#6B6B6B" fill-opacity="0.25"/>')
    P.append(f'<line x1="{X(1e6):.1f}" y1="{y1p}" x2="{X(1e6):.1f}" y2="{y0}" stroke="#B8860B" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(5e6):.1f}" y1="{y1p}" x2="{X(5e6):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(1e7):.1f}" y1="{y1p}" x2="{X(1e7):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2.2"/>')
    P.append(f'<rect x="{X(1e7):.1f}" y="{y1p}" width="{x1_-X(1e7):.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.10"/>')
    # 轴
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"),(2e6,"200万"),(4e6,"400万"),(6e6,"600万"),(8e6,"800万"),(1e7,"1000万")]:
        P.append(f'<text x="{X(xv):.0f}" y="{y0+16}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    # 图例行 1：参考线说明
    ly1 = y0 + 34
    items1 = [
        ("#6B6B6B", "0.25", "rect", "内部预期 30–40万"),
        ("#B8860B", "",  "dash", "上调 100万"),
        ("#EC008C", "", "dash", "2024 实售 500万"),
        ("#EC008C", "", "solid", "累计 1000万+"),
    ]
    lx = x0
    for color, opac, style, label in items1:
        if style == "rect":
            P.append(f'<rect x="{lx:.0f}" y="{ly1-7}" width="18" height="9" fill="{color}" fill-opacity="0.3"/>')
        elif style == "dash":
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2" stroke-dasharray="5 3"/>')
        else:
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2.4"/>')
        P.append(f'<text x="{lx+23:.0f}" y="{ly1}" font-size="9.8" fill="#333">{label}</text>')
        lx += 23 + len(label) * 10.5 + 22
    # 图例行 2：分布说明
    ly2 = y0 + 52
    P.append(f'<text x="{x0:.0f}" y="{ly2}" font-size="9.5" fill="#6B6B6B">事前概率分布：参照前代 Pocket 2（对数正态）·  1000万+ 位于 P99.3 右尾（保留概率 0.7%）</text>')
    P.append('</svg>')
    return "".join(P)

W = lambda v: f"{v/1e4:.2f}万"

SVG_Y1 = hist_svg(y1, w=560, h=210, vmax=80_000,
    marks=[(pct(y1,5),"P5",  "#C0392B","4 3"),(pct(y1,50),"P50","#111","4 3"),(pct(y1,95),"P95","#7A4FA0","4 3")],
    shade=(36_000, f"P(≥3.6万 Best线)={prob(y1,36000)*100:.0f}%"),
    xticks=[(0,"0"),(2e4,"2万"),(4e4,"4万"),(6e4,"6万"),(8e4,"8万")])
SVG_Y3 = hist_svg(y3, w=560, h=210, vmax=200_000,
    marks=[(pct(y3,5),"P5","#C0392B","4 3"),(pct(y3,50),"P50","#111","4 3"),(pct(y3,95),"P95","#7A4FA0","4 3")],
    shade=(100_000, f"P(≥10万)={prob(y3,100000)*100:.0f}%"),
    xticks=[(0,"0"),(5e4,"5万"),(1e5,"10万"),(1.5e5,"15万"),(2e5,"20万")])
SVG_SCURVE = s_curve_svg()
SVG_FAN = fan_svg()
SVG_PRIOR = prior_bars_svg()
SVG_DJI = dji_svg()

LEV_BUDGET = f"P50 {W(pct(y1,50))}→{W(pct(y1_b,50))}；P(≥Best线) {prob(y1,36000)*100:.0f}%→{prob(y1_b,36000)*100:.0f}%"
LEV_Q = f"首年影响小、后期放大：三年 P50 {W(pct(y3,50))}→{W(pct(y3_k,50))}；P(三年≥10万) {prob(y3,100000)*100:.0f}%→{prob(y3_k,100000)*100:.0f}%"
LEV_M = f"上限抬高：三年 P50 {W(pct(y3,50))}→{W(pct(y3_m,50))}（首年几乎不变）"

HTML_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布模型 · 3+1 框架</title>
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
  .flow { display:flex; align-items:stretch; margin-top:10px; }
  .layer { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:9px 13px 7px; display:flex; flex-direction:column; background:#fff; min-height:250px; }
  .layer .step { font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .layer h3 { font-size:15.5px; margin:5px 0 1px; }
  .layer .q { font-size:11px; color:#EC008C; font-weight:bold; margin-bottom:3px; }
  .layer .desc { font-size:11.3px; color:#555; line-height:1.5; }
  .layer .chart { flex:1; display:flex; align-items:center; justify-content:center; margin:4px 0; }
  .layer .chart svg { width:100%; max-height:150px; }
  .arrow { display:flex; align-items:center; justify-content:center; width:24px; flex:none; color:#111; font-size:19px; font-weight:bold; }
  .refs { font-size:10px; color:#6B6B6B; line-height:1.5; margin-top:3px; }
  .refs b { color:#111; }
  .outrow { display:flex; gap:14px; margin-top:12px; }
  .out { flex:1; border:2px solid #111; border-radius:8px; padding:8px 12px 6px; display:flex; flex-direction:column; background:#fff; }
  .out .step { font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .out h3 { font-size:15.5px; margin:4px 0 0; }
  .out .nums { font-size:12.3px; margin-top:2px; font-variant-numeric:tabular-nums; }
  .out .nums b { color:#111; }
  .out .chart { flex:1; display:flex; align-items:center; justify-content:center; }
  .out .chart svg { width:100%; max-height:186px; }
  .lev { margin-top:12px; border:1.5px solid #111; border-radius:8px; padding:9px 14px; background:#F7F7F7; display:flex; gap:16px; align-items:center; flex-wrap:wrap; }
  .lev .t { flex:none; width:150px; }
  .lev .t .st { font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; }
  .lev .t h4 { font-size:14px; margin-top:3px; }
  .lev .t p { font-size:10px; color:#6B6B6B; margin-top:1px; line-height:1.4; }
  .lev table { border-collapse:collapse; flex:1; min-width:520px; }
  .lev th,.lev td { font-size:11.3px; padding:4px 8px; border-bottom:1px solid #E6E6E6; text-align:left; }
  .lev th { color:#6B6B6B; font-weight:normal; border-bottom:1.5px solid #111; }
  .lev td.k { font-weight:bold; }
  .lev td.v { color:#EC008C; font-weight:bold; }
  .bt { margin-top:10px; border:1.5px solid #E6E6E6; border-radius:8px; padding:10px 14px; display:flex; gap:18px; align-items:center; background:#fff; flex-wrap:wrap; }
  .bt .t { flex:none; width:132px; }
  .bt .t .st { font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; }
  .bt .t h4 { font-size:14px; margin-top:3px; line-height:1.35; white-space:nowrap; }
  .bt .t p { font-size:10px; color:#6B6B6B; margin-top:2px; white-space:nowrap; }
  .bt .fig { flex:none; width:560px; max-width:100%; display:flex; align-items:center; }
  .bt .fig svg { width:100%; max-height:170px; }
  .bt .cc { flex:1; min-width:340px; font-size:11px; line-height:1.62; color:#333; }
  .bt .cc .nwr { white-space:nowrap; }
  .bt .cc b { color:#EC008C; }
  .bt .cc .src { font-size:9.3px; color:#9a9a9a; }
  .ft { margin-top:9px; border-top:1.5px solid #111; padding-top:7px; display:flex; justify-content:space-between; align-items:center; }
  .ft .loop { font-size:11.5px; }
  .ft .loop b { color:#EC008C; }
  .ft .note { font-size:9.5px; color:#9a9a9a; text-align:right; line-height:1.4; }
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>AiKen 销量概率分布模型 <em>· 三层架构 + 杠杆层</em></h1>
    <div class="tag">SI / COA · 模型方法论</div>
  </div>

  <div class="flow">
    <div class="layer">
      <span class="step">层 1 · RCF 参照类</span>
      <h3>参数从哪来</h3>
      <div class="q">同类 × 同价位带优先</div>
      <div class="desc">核心参照带 ¥400–1,300（与 AiKen ¥599 同档）：instax mini、Flashback One35、Kodak Mini Shot、Paper Shoot；DJI Pocket（¥3,499）仅作右尾例证，不进参数。</div>
      <div class="chart">__SVG_PRIOR__</div>
      <div class="refs"><b>instax mini</b>（¥599 档·年销千万级）定 <b>m</b> 天花板 ｜ <b>Flashback</b>（¥749·众筹 $80 万）定存活基线</div>
    </div>
    <div class="arrow">→</div>
    <div class="layer">
      <span class="step">层 2 · Bass 扩散</span>
      <h3>曲线长什么样</h3>
      <div class="q">三参数各管一段</div>
      <div class="desc"><b>m</b>=市场潜力（上限）｜<b>p</b>=投放驱动（冷启动）｜<b>q</b>=口碑驱动（起飞斜率）。Bass (1969)，耐用消费品采纳预测经典模型。</div>
      <div class="chart">__SVG_SCURVE__</div>
      <div class="refs">前 6 个月由<b>投流漏斗</b>（曝光→点击→转化）钉住 p，之后 Bass 接管</div>
    </div>
    <div class="arrow">→</div>
    <div class="layer">
      <span class="step">层 3 · 蒙特卡洛</span>
      <h3>不确定性有多大</h3>
      <div class="q">8000 次模拟</div>
      <div class="desc">参数不取单点，按层 1 区间随机抽 8000 组 (m·p·q) → 8000 条 S 曲线 → 统计成销量概率分布。</div>
      <div class="chart">__SVG_FAN__</div>
      <div class="refs">Worst / Normal / Best 三档场景 = 分布上的 <b>P5 / P50 / P95</b> 分位</div>
    </div>
  </div>

  <div class="outrow">
    <div class="out">
      <span class="step">管理层视图 · 首年</span>
      <h3>首年销量概率分布</h3>
      <div class="nums">P5 <b>__Y1_P5__</b> ｜ P50 <b>__Y1_P50__</b> ｜ P95 <b>__Y1_P95__</b></div>
      <div class="chart">__SVG_Y1__</div>
    </div>
    <div class="out">
      <span class="step">管理层视图 · 三年</span>
      <h3>三年累计销量概率分布</h3>
      <div class="nums">P5 <b>__Y3_P5__</b> ｜ P50 <b>__Y3_P50__</b> ｜ P95 <b>__Y3_P95__</b></div>
      <div class="chart">__SVG_Y3__</div>
    </div>
  </div>

  <div class="lev">
    <div class="t">
      <span class="st">杠杆层</span>
      <h4>动作 → 参数 → 右移</h4>
      <p>每个运营动作显式映射到参数，花钱买概率增量。</p>
    </div>
    <table>
      <tr><th>运营动作</th><th>作用参数</th><th>曲线变化（模型实算）</th></tr>
      <tr><td class="k">投放预算 ×1.5</td><td class="v">p ↑</td><td>__LEV_BUDGET__</td></tr>
      <tr><td class="k">KOC 种草 / UGC 密度 ×1.15</td><td class="v">q ↑</td><td>__LEV_Q__</td></tr>
      <tr><td class="k">品类破圈（礼赠 / 旅行场景）</td><td class="v">m ↑</td><td>__LEV_M__</td></tr>
    </table>
  </div>

  <div class="bt">
    <div class="t">
      <span class="st">回测检验</span>
      <h4>DJI Osmo Pocket 3</h4>
      <p>用真实爆款检验：分布方法 vs 点预测</p>
    </div>
    <div class="fig">__SVG_DJI__</div>
    <div class="cc">
      假如在 2023 年 10 月发布前，用本框架预测 Pocket 3（参照前代 Pocket 2）：<br>
      · <span class="nwr">事前分布 P50 = <b>60 万台</b></span>——<span class="nwr">大疆内部预期 30–40 万 ≈ 分布 P__DJI_P30__–P__DJI_P40__</span>，与厂商自身判断同水平；<br>
      · <span class="nwr">实际：2024 年实售约 <b>500 万台</b>、累计破 <b>1000 万台</b></span>——落在分布 <b>P99.3 右尾</b>；<br>
      · <b>检验结论</b>：没有人能预知爆发（大疆自己也 miss 了 25 倍），但分布右尾以 0.7% 概率保留了千万级结果——<b>点预测会直接排除它，分布不会</b>；上市后 Checkpoint 快速收窄。<br>
      <span class="src">数据源：雷峰网 / IT之家 2025-09（供应链消息）；发布 ¥3,499</span>
    </div>
  </div>

  <div class="ft">
    <div class="loop"><b>Checkpoint 闭环</b>：上市 30 / 90 天真实数据 → 更新 m·p·q → 分布收窄（演示：一次 30 天收窄约 47%）→ 下一轮动作决策 ↺</div>
    <div class="note">v0.2 参数：参照类已校准，漏斗为行业通带占位（待市场部实测校准）<br>RCF = 参照类预测（Flyvbjerg）· Bass = 扩散模型（1969, Management Science）· MC = 蒙特卡洛</div>
  </div>

</div></div>
</body>
</html>
"""

html = (HTML_TMPL
    .replace("__SVG_PRIOR__", SVG_PRIOR)
    .replace("__SVG_SCURVE__", SVG_SCURVE)
    .replace("__SVG_FAN__", SVG_FAN)
    .replace("__SVG_Y1__", SVG_Y1)
    .replace("__SVG_Y3__", SVG_Y3)
    .replace("__SVG_DJI__", SVG_DJI)
    .replace("__Y1_P5__", W(pct(y1,5))).replace("__Y1_P50__", W(pct(y1,50))).replace("__Y1_P95__", W(pct(y1,95)))
    .replace("__Y3_P5__", W(pct(y3,5))).replace("__Y3_P50__", W(pct(y3,50))).replace("__Y3_P95__", W(pct(y3,95)))
    .replace("__LEV_BUDGET__", LEV_BUDGET)
    .replace("__LEV_Q__", LEV_Q)
    .replace("__LEV_M__", LEV_M)
    .replace("__DJI_P30__", f"{p_dji_30:.0f}").replace("__DJI_P40__", f"{p_dji_40:.0f}")
)

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率模型_方法论说明页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("\nwritten:", OUT)
