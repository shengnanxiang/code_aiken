# -*- coding: utf-8 -*-
"""生成方法论说明页 HTML：三层+杠杆层架构图解（自包含单文件 slide）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

rng = np.random.default_rng(42)
N_SIM = 5000
T = 36

# ---------- 与 v0.1 相同的示意先验 ----------
m_prior = rng.lognormal(mean=np.log(60_000), sigma=0.9, size=N_SIM)
p_prior = np.clip(rng.normal(0.010, 0.004, size=N_SIM), 0.003, 0.03)
q_prior = np.clip(rng.normal(0.38, 0.12, size=N_SIM), 0.10, 0.75)

def bass_cum(m, p, q, t):
    t = np.atleast_1d(t).astype(float)
    return m * (1 - np.exp(-(p + q) * t)) / (1 + (q / p) * np.exp(-(p + q) * t))

t = np.arange(1, T + 1)
paths = bass_cum(m_prior[:, None], p_prior[:, None], q_prior[:, None], t[None, :])
y1 = paths[:, 11]
y1_boost = bass_cum(m_prior[:, None], np.clip(p_prior*1.5, 0.003, 0.04)[:, None], q_prior[:, None], t[None, :])[:, 11]

# ---------- 关键统计 ----------
def pct(a, q): return float(np.percentile(a, q))
P5, P50, P95 = pct(y1, 5), pct(y1, 50), pct(y1, 95)
P10K = float((y1 >= 100_000).mean())
P10K_B = float((y1_boost >= 100_000).mean())
P50_B = pct(y1_boost, 50)
# 老三档在新分布中的位置
from scipy import stats as _s  # may not exist; fallback
try:
    old_w = float((_s.percentileofscore(y1, 6_000)))
    old_n = float((_s.percentileofscore(y1, 12_000)))
    old_b = float((_s.percentileofscore(y1, 36_000)))
except Exception:
    old_w = float((y1 < 6_000).mean() * 100)
    old_n = float((y1 < 12_000).mean() * 100)
    old_b = float((y1 < 36_000).mean() * 100)

# ---------- SVG 工具 ----------
def sx_v(v, vmax, w, x0, x1):  # value -> x pixel
    return x0 + (min(v, vmax) / vmax) * (x1 - x0)

def hist_svg(data, boost=None, w=520, h=230, nbins=48, vmax=250_000,
             marks=None, shade_from=None):
    """直方图 SVG；marks: [(value,label,color,dash)]"""
    ml, mr, mt, mb = 46, 16, 14, 30
    x0, x1 = ml, w - mr
    y0, y1_ = h - mb, mt
    counts, edges = np.histogram(data, bins=nbins, range=(0, vmax))
    cmax = counts.max()
    parts = []
    parts.append(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">')
    # gridlines y
    for gy in np.linspace(y0, y1_, 4):
        parts.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1}" y2="{gy:.0f}" stroke="#E6E6E6" stroke-width="1"/>')
    # bars
    bw = (x1 - x0) / nbins
    for i, c in enumerate(counts):
        bh = (c / cmax) * (y0 - y1_)
        if bh <= 0: continue
        bx = x0 + i * bw
        parts.append(f'<rect x="{bx:.1f}" y="{(y0-bh):.1f}" width="{bw*0.88:.1f}" height="{bh:.1f}" fill="#111111" fill-opacity="0.82" rx="1"/>')
    if boost is not None:
        counts2, _ = np.histogram(boost, bins=nbins, range=(0, vmax))
        cmax2 = max(counts2.max(), cmax)
        # rescale factor differs; redraw both to common max? keep simple: outline top of boost
        pts = []
        for i, c in enumerate(counts2):
            bh = (c / cmax) * (y0 - y1_)
            bx = x0 + i * bw + bw * 0.5
            pts.append(f"{bx:.1f},{(y0-bh):.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#EC008C" stroke-width="2.5" stroke-linejoin="round" opacity="0.9"/>')
    # shade region (>=10万台)
    if shade_from:
        sx = sx_v(shade_from, vmax, w, x0, x1)
        parts.append(f'<rect x="{sx:.1f}" y="{y1_}" width="{x1-sx:.1f}" height="{y0-y1_}" fill="#EC008C" fill-opacity="0.10"/>')
        parts.append(f'<line x1="{sx:.1f}" y1="{y1_}" x2="{sx:.1f}" y2="{y0}" stroke="#EC008C" stroke-width="1.5" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{(sx+x1)/2:.0f}" y="{y1_+16}" text-anchor="middle" font-size="11.5" fill="#EC008C" font-weight="bold">P(≥10万)={P10K*100:.0f}%</text>')
    # marks
    for v, label, color, dash in (marks or []):
        sx = sx_v(v, vmax, w, x0, x1)
        parts.append(f'<line x1="{sx:.1f}" y1="{y1_}" x2="{sx:.1f}" y2="{y0}" stroke="{color}" stroke-width="1.8" stroke-dasharray="{dash}"/>')
        parts.append(f'<text x="{sx:.1f}" y="{y0+14}" text-anchor="middle" font-size="11" fill="{color}" font-weight="bold">{label}</text>')
    # axes
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#111111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"), (50_000,"5万"), (100_000,"10万"), (150_000,"15万"), (200_000,"20万"), (250_000,"25万")]:
        sx = sx_v(xv, vmax, w, x0, x1)
        parts.append(f'<text x="{sx:.0f}" y="{y0+26}" text-anchor="middle" font-size="10.5" fill="#6B6B6B">{xl}</text>')
    parts.append(f'<text x="{x0-8}" y="{y1_+4}" text-anchor="end" font-size="10.5" fill="#6B6B6B">概率</text>')
    parts.append(f'<text x="{x0-8}" y="{y0+4}" text-anchor="end" font-size="10.5" fill="#6B6B6B">密度</text>')
    parts.append('</svg>')
    return "".join(parts)

def s_curve_svg(w=250, h=160):
    m, p, q = 60_000, 0.010, 0.38
    ml, mr, mt, mb = 34, 12, 12, 24
    x0, x1 = ml, w - mr
    y0, y1_ = h - mb, mt
    cum = bass_cum(m, p, q, np.arange(0, T + 1))
    vmax_t, vmax_v = T, m * 1.08
    pts = [f"{x0 + (tt/vmax_t)*(x1-x0):.1f},{y0 - (v/vmax_v)*(y0-y1_):.1f}" for tt, v in enumerate(cum)]
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    # m line
    my = y0 - (m / vmax_v) * (y0 - y1_)
    parts.append(f'<line x1="{x0}" y1="{my:.1f}" x2="{x1}" y2="{my:.1f}" stroke="#FFC400" stroke-width="1.4" stroke-dasharray="5 4"/>')
    parts.append(f'<text x="{x1-4}" y="{my-5:.1f}" text-anchor="end" font-size="10.5" fill="#B8860B" font-weight="bold">m 市场潜力</text>')
    parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111111" stroke-width="2.4" stroke-linejoin="round"/>')
    # p zone (前6个月) q zone
    px = x0 + (6 / vmax_t) * (x1 - x0)
    parts.append(f'<rect x="{x0}" y="{y1_}" width="{px-x0:.1f}" height="{y0-y1_}" fill="#00C2C2" fill-opacity="0.10"/>')
    parts.append(f'<text x="{(x0+px)/2:.0f}" y="{y0-8}" text-anchor="middle" font-size="10" fill="#007C7C" font-weight="bold">p 投放驱动</text>')
    parts.append(f'<text x="{(px+x1)/2:.0f}" y="{y0-8}" text-anchor="middle" font-size="10" fill="#7A4FA0" font-weight="bold">q 口碑驱动</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#111111" stroke-width="1.2"/>')
    for tt, xl in [(0,"0"), (12,"12月"), (24,"24月"), (36,"36月")]:
        sx = x0 + (tt / vmax_t) * (x1 - x0)
        parts.append(f'<text x="{sx:.0f}" y="{y0+16}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    parts.append('</svg>')
    return "".join(parts)

def fan_svg(w=250, h=160, n_samples=14):
    ml, mr, mt, mb = 34, 12, 12, 24
    x0, x1 = ml, w - mr
    y0, y1_ = h - mb, mt
    vmax_v = 260_000
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    # sample gray paths
    idx = rng.choice(N_SIM, n_samples, replace=False)
    for i in idx:
        pts = [f"{x0 + (tt/T)*(x1-x0):.1f},{y0 - (min(v,vmax_v)/vmax_v)*(y0-y1_):.1f}" for tt, v in enumerate(paths[i])]
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#B0B0B0" stroke-width="1" opacity="0.55"/>')
    # percentile bands
    for lo, hi, opac in [(5, 95, 0.10), (25, 75, 0.16)]:
        plo = np.percentile(paths, lo, axis=0); phi = np.percentile(paths, hi, axis=0)
        band = [f"{x0 + (tt/T)*(x1-x0):.1f},{y0 - (min(v,vmax_v)/vmax_v)*(y0-y1_):.1f}" for tt, v in enumerate(phi)]
        band += [f"{x0 + (tt/T)*(x1-x0):.1f},{y0 - (min(v,vmax_v)/vmax_v)*(y0-y1_):.1f}" for tt, v in reversed(list(enumerate(plo)))]
        parts.append(f'<polygon points="{" ".join(band)}" fill="#00C2C2" fill-opacity="{opac}" stroke="none"/>')
    p50 = np.percentile(paths, 50, axis=0)
    pts = [f"{x0 + (tt/T)*(x1-x0):.1f},{y0 - (min(v,vmax_v)/vmax_v)*(y0-y1_):.1f}" for tt, v in enumerate(p50)]
    parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111111" stroke-width="2.2"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#111111" stroke-width="1.2"/>')
    for tt, xl in [(0,"0"), (12,"12月"), (24,"24月"), (36,"36月")]:
        sx = x0 + (tt / T) * (x1 - x0)
        parts.append(f'<text x="{sx:.0f}" y="{y0+16}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    parts.append(f'<text x="{x1-4}" y="{y1_+12}" text-anchor="end" font-size="10" fill="#6B6B6B">5000 条模拟轨迹</text>')
    parts.append('</svg>')
    return "".join(parts)

def prior_bars_svg(w=230, h=150):
    """层1: m/p/q 先验区间条"""
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    rows = [
        ("m 市场潜力", "1.8万", "6.0万", "18.5万", 0.12, 0.30, 0.78, "台"),
        ("p 创新系数", "0.005", "0.010", "0.015", 0.15, 0.33, 0.80, ""),
        ("q 模仿系数", "0.23", "0.38", "0.54", 0.13, 0.31, 0.79, ""),
    ]
    y = 26
    for name, lo, mid, hi, f_lo, f_mid, f_hi, unit in rows:
        x0, x1 = 86, w - 44
        parts.append(f'<text x="8" y="{y+4}" font-size="11" fill="#111111" font-weight="bold">{name}</text>')
        parts.append(f'<rect x="{x0}" y="{y-6}" width="{x1-x0}" height="12" rx="6" fill="#E6E6E6"/>')
        parts.append(f'<rect x="{x0 + f_lo*(x1-x0):.0f}" y="{y-6}" width="{(f_hi-f_lo)*(x1-x0):.0f}" height="12" rx="6" fill="#00C2C2" fill-opacity="0.35"/>')
        parts.append(f'<circle cx="{x0 + f_mid*(x1-x0):.0f}" cy="{y}" r="4.5" fill="#EC008C"/>')
        parts.append(f'<text x="{x0-6}" y="{y+4}" text-anchor="end" font-size="9.5" fill="#6B6B6B">{lo}</text>')
        parts.append(f'<text x="{x1+6}" y="{y+4}" font-size="9.5" fill="#6B6B6B">{hi}</text>')
        y += 40
    parts.append(f'<text x="8" y="{h-8}" font-size="9.5" fill="#6B6B6B">● P50 ｜ 条带 = P10–P90 区间（示意）</text>')
    parts.append('</svg>')
    return "".join(parts)

SVG_HIST = hist_svg(
    y1, boost=y1_boost, w=520, h=238, vmax=250_000,
    marks=[(P5, "Worst≈P5", "#C0392B", "4 3"), (P50, "Normal≈P50", "#111111", "4 3"), (P95, "Best≈P95", "#7A4FA0", "4 3")],
    shade_from=100_000,
)
SVG_SCURVE = s_curve_svg()
SVG_FAN = fan_svg()
SVG_PRIOR = prior_bars_svg()

fmt = lambda v: f"{v/1e4:.2f}"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布模型 · 方法论说明</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ background:#3a3a3a; height:100%; overflow:hidden; }}
  body {{ display:flex; align-items:center; justify-content:center; }}
  #slide {{ width:1280px; height:720px; background:#FFFFFF; font-family:"Microsoft YaHei",sans-serif;
            color:#111111; position:relative; flex:none; box-shadow:0 8px 40px rgba(0,0,0,.45); }}
  .pad {{ padding:26px 34px 18px; height:100%; display:flex; flex-direction:column; }}
  /* header */
  .hd {{ display:flex; align-items:flex-end; justify-content:space-between; border-bottom:2.5px solid #111; padding-bottom:10px; }}
  .hd h1 {{ font-size:26px; letter-spacing:.5px; }}
  .hd h1 em {{ color:#EC008C; font-style:normal; }}
  .hd .sub {{ font-size:13px; color:#6B6B6B; margin-top:4px; }}
  .hd .tag {{ font-size:11px; color:#fff; background:#111; padding:4px 10px; border-radius:3px; letter-spacing:1px; }}
  /* background strip */
  .bg {{ background:#F7F7F7; border-left:4px solid #EC008C; padding:10px 16px; margin-top:14px; display:flex; gap:26px; align-items:center; }}
  .bg .lbl {{ font-size:13px; font-weight:bold; color:#EC008C; writing-mode:vertical-lr; letter-spacing:6px; flex:none; }}
  .bg ul {{ list-style:none; display:flex; gap:24px; flex:1; }}
  .bg li {{ font-size:12.5px; line-height:1.55; color:#111; flex:1; }}
  .bg li b {{ color:#EC008C; }}
  /* flow */
  .flow {{ display:flex; gap:0; align-items:stretch; margin-top:14px; flex:1; }}
  .layer {{ flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:10px 12px 8px; display:flex; flex-direction:column; background:#fff; }}
  .layer.hot {{ border-color:#111; border-width:2px; }}
  .layer .step {{ font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }}
  .layer.hot .step {{ background:#EC008C; }}
  .layer h3 {{ font-size:15.5px; margin:6px 0 1px; }}
  .layer .q {{ font-size:11px; color:#EC008C; font-weight:bold; margin-bottom:4px; }}
  .layer .desc {{ font-size:11px; color:#6B6B6B; line-height:1.5; }}
  .layer .chart {{ flex:1; display:flex; align-items:center; justify-content:center; margin-top:4px; }}
  .layer .chart svg {{ width:100%; height:100%; max-height:150px; }}
  .arrow {{ display:flex; align-items:center; justify-content:center; width:26px; flex:none; color:#111; font-size:20px; font-weight:bold; }}
  /* leverage */
  .lev {{ margin-top:12px; border:1.5px solid #111; border-radius:8px; padding:10px 14px; display:flex; gap:18px; align-items:center; background:#F7F7F7; }}
  .lev .t {{ flex:none; width:120px; }}
  .lev .t .st {{ font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; }}
  .lev .t h4 {{ font-size:14.5px; margin-top:4px; }}
  .lev .t p {{ font-size:10.5px; color:#6B6B6B; margin-top:2px; line-height:1.45; }}
  .lev table {{ border-collapse:collapse; flex:1; }}
  .lev th,.lev td {{ font-size:11px; padding:4.5px 8px; border-bottom:1px solid #E6E6E6; text-align:left; }}
  .lev th {{ color:#6B6B6B; font-weight:normal; border-bottom:1.5px solid #111; }}
  .lev td.k {{ font-weight:bold; }}
  .lev td.v {{ color:#EC008C; font-weight:bold; }}
  .lev .mchart {{ flex:none; width:300px; }}
  /* footer */
  .ft {{ margin-top:12px; display:flex; justify-content:space-between; align-items:center; border-top:1.5px solid #111; padding-top:9px; }}
  .ft .loop {{ font-size:12px; display:flex; align-items:center; gap:8px; }}
  .ft .loop b {{ color:#EC008C; }}
  .ft .loop .arr {{ color:#EC008C; font-weight:bold; }}
  .ft .note {{ font-size:10px; color:#6B6B6B; text-align:right; line-height:1.5; }}
  .num {{ font-variant-numeric:tabular-nums; }}
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <div>
      <h1>AiKen 销量概率分布模型 <em>· 三层架构 + 杠杆层</em></h1>
      <div class="sub">把「争论三个点」换成「管理一条曲线」—— 每个运营动作，都在把销量分布往右推</div>
    </div>
    <div class="tag">SI / COA 校准会 · 模型方法论</div>
  </div>

  <div class="bg">
    <div class="lbl">背景</div>
    <ul>
      <li><b>① 不考核利润</b>：项目定位「品牌投资型」，财务测算允许亏损，worst 场景即红线。</li>
      <li><b>② 不许丢掉 100 万台</b>：财务按当前能力测算，但品类上限（百万台级）的概率必须显式保留在模型里。</li>
      <li><b>③ 动作 = 推曲线</b>：所有运营动作的目标只有一个——提升高销量发生的概率，而非预测单一数字。</li>
    </ul>
  </div>

  <div class="flow">
    <div class="layer">
      <span class="step">层 1 · RCF</span>
      <h3>参照类预测</h3>
      <div class="q">参数从哪来？</div>
      <div class="desc">收集同类情感科技硬件（DJI Pocket、instax、汉印、Flashback One35…）首发真实销量分布，提炼三参数的<b>先验区间</b>——不拍脑袋。</div>
      <div class="chart">{SVG_PRIOR}</div>
    </div>
    <div class="arrow">→</div>
    <div class="layer">
      <span class="step">层 2 · Bass 扩散</span>
      <h3>S 曲线结构</h3>
      <div class="q">曲线长什么样？</div>
      <div class="desc">Bass (1969) 耐用品扩散经典模型。三个参数各管一段：<b>m</b>=市场潜力（曲线上限）、<b>p</b>=投放驱动（冷启动）、<b>q</b>=口碑驱动（起飞斜率）。</div>
      <div class="chart">{SVG_SCURVE}</div>
    </div>
    <div class="arrow">→</div>
    <div class="layer">
      <span class="step">层 3 · 蒙特卡洛</span>
      <h3>5000 次模拟</h3>
      <div class="q">不确定性有多大？</div>
      <div class="desc">参数不取单点，按层1区间随机抽 5000 组 → 跑出 5000 条 S 曲线 → 统计成年销量<b>概率分布</b>。</div>
      <div class="chart">{SVG_FAN}</div>
    </div>
    <div class="arrow">→</div>
    <div class="layer hot" style="flex:1.35">
      <span class="step">输出 · 管理层视图</span>
      <h3>首年销量概率分布</h3>
      <div class="q">决策看什么？</div>
      <div class="chart">{SVG_HIST}</div>
      <div class="desc num" style="margin-top:2px">Worst≈P5 <b>{fmt(P5)}万</b> ｜ Normal≈P50 <b>{fmt(P50)}万</b> ｜ Best≈P95 <b>{fmt(P95)}万</b> ｜ <b style="color:#EC008C">P(≥10万台)={P10K*100:.0f}%</b>　<span style="color:#6B6B6B">（m 先验右尾延伸至 100 万台级 → Sean 的上限始终在模型内）</span></div>
    </div>
  </div>

  <div class="lev">
    <div class="t">
      <span class="st">杠杆层</span>
      <h4>动作 → 参数 → 右移</h4>
      <p>每个运营动作显式映射到参数，花钱买「概率增量」明码标价。</p>
    </div>
    <table>
      <tr><th>运营动作</th><th>作用参数</th><th>曲线变化</th></tr>
      <tr><td class="k">投放预算 ↑（无自然流量，80–90% 靠投流）</td><td class="v">p ↑</td><td>冷启动更陡：P50 {fmt(P50)}万→{fmt(P50_B)}万，P(≥10万) {P10K*100:.0f}%→{P10K_B*100:.0f}%</td></tr>
      <tr><td class="k">KOC 种草 / UGC 密度 ↑</td><td class="v">q ↑</td><td>起飞更早更快，右尾显著增厚</td></tr>
      <tr><td class="k">品类破圈（礼赠 / 旅行场景）</td><td class="v">m ↑</td><td>整条曲线上限抬高，向 100 万台延伸</td></tr>
    </table>
    <div class="mchart">
      <svg viewBox="0 0 300 96" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">
        <rect x="0" y="0" width="300" height="96" fill="#FFFFFF" rx="6"/>
        <text x="12" y="18" font-size="10.5" fill="#6B6B6B">示意：投放加码后分布右移</text>
        <rect x="24" y="30" width="150" height="34" rx="4" fill="#111111" fill-opacity="0.78"/>
        <rect x="86" y="34" width="150" height="34" rx="4" fill="#EC008C" fill-opacity="0.75"/>
        <text x="96" y="66" font-size="10" fill="#EC008C" font-weight="bold">→ 分布右移</text>
        <text x="24" y="88" font-size="9.5" fill="#6B6B6B">黑=当前动作 ｜ 粉=加码后</text>
      </svg>
    </div>
  </div>

  <div class="ft">
    <div class="loop">
      <b>闭环</b>：上市 30 / 90 天 Checkpoint 真实数据 <span class="arr">→</span> 贝叶斯更新收窄 m·p·q <span class="arr">→</span> 分布图变窄变高 <span class="arr">→</span> 下一轮动作决策 <span class="arr">↺</span>
    </div>
    <div class="note">v0.1 示意参数（参照类数据待 v0.2 校准）· 模型脚本：prototype_v01.py<br>RCF=参照类预测(Flyvbjerg) · Bass=扩散模型(1969, Management Science) · MC=蒙特卡洛模拟</div>
  </div>

</div></div>
<script>
  function fit() {{
    var s = document.getElementById('slide');
    var k = Math.min(innerWidth/1280, innerHeight/720);
    s.style.transform = 'scale(' + k + ')';
  }}
  addEventListener('resize', fit); fit();
</script>
</body>
</html>
"""

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率模型_方法论说明页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("written:", OUT)
print(f"key numbers: P5={fmt(P5)}万 P50={fmt(P50)}万 P95={fmt(P95)}万 P10K={P10K*100:.1f}% P10K_boost={P10K_B*100:.1f}% P50_boost={fmt(P50_B)}万")
print(f"old scenarios as percentiles: worst6000台=P{old_w:.0f} normal12000台=P{old_n:.0f} best36000台=P{old_b:.0f}")
