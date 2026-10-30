# -*- coding: utf-8 -*-
"""
生成评审整页：AiKen 销量概率分布（¥699 · v0.4 校准）+ S1 回测 + DJI 回测
更新版：数据源 s699_v04_full_results.npz（699 定价 · 漏斗不打折 · 含预算杠杆）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261027)

# ============ 载入 699 结果与 S1 回测数据 ============
D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s699_v04_full_results.npz")
y1, y3 = D["y1"], D["y3"]
y1_b = D["y1_b"]
B = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_backtest.npz")
s1_y1 = B["y1"]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# DJI 回测分布（与方法论页一致）
rng_d = np.random.default_rng(7)
m_dji = rng_d.lognormal(mean=np.log(600_000), sigma=1.15, size=200_000)

# ============ SVG：首年分布 ============
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
    marks=[(pct(y1,20), "P20·Worst", "#C0392B", "4 3"),
           (pct(y1,50), "P50·Normal", "#111", "4 3"),
           (pct(y1,90), "P90·Best", "#7A4FA0", "4 3")],
    shade=(pct(y1,90), f"P(≥P90) = 10%"),
    xticks=[(0,"0"),(1e4,"1万"),(2e4,"2万"),(3e4,"3万"),(4e4,"4万")])

SVG_Y3 = hist_svg(y3, vmax=140_000,
    marks=[(pct(y3,20), "P20·Worst", "#C0392B", "4 3"),
           (pct(y3,50), "P50·Normal", "#111", "4 3"),
           (pct(y3,90), "P90·Best", "#7A4FA0", "4 3")],
    shade=(100_000, f"P(≥10万) = {prob(y3,100_000)*100:.0f}%"),
    xticks=[(0,"0"),(3e4,"3万"),(6e4,"6万"),(9e4,"9万"),(12e4,"12万")])

# ============ SVG：S1 回测图（不变） ============
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
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.82:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.80" rx="1"/>')
    P.append(f'<line x1="{X(25000):.1f}" y1="{y1p}" x2="{X(25000):.1f}" y2="{y0}" stroke="#B8860B" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<text x="{X(25000):.0f}" y="{y1p+38}" text-anchor="middle" font-size="10.5" fill="#B8860B" font-weight="bold">内部预测 25,000</text>')
    P.append(f'<text x="{X(25000):.0f}" y="{y1p+52}" text-anchor="middle" font-size="9.5" fill="#B8860B">P92</text>')
    P.append(f'<line x1="{X(7285):.1f}" y1="{y1p}" x2="{X(7285):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2"/>')
    P.append(f'<text x="{X(7285):.0f}" y="{y1p+38}" text-anchor="middle" font-size="10.5" fill="#EC008C" font-weight="bold">实际宽口径 7,285</text>')
    P.append(f'<text x="{X(7285):.0f}" y="{y1p+52}" text-anchor="middle" font-size="9.5" fill="#EC008C">P5 以下</text>')
    P.append(f'<rect x="{x0:.1f}" y="{y1p}" width="{X(7285)-x0:.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.08"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"),(6000,"6千"),(1.2e4,"1.2万"),(1.8e4,"1.8万"),(2.4e4,"2.4万"),(3e4,"3万")]:
        P.append(f'<text x="{X(xv):.0f}" y="{y0+18}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x1_}" y="{y1p+38}" text-anchor="end" font-size="10" fill="#6B6B6B">参照 N 系先验</text>')
    P.append(f'<text x="{x1_}" y="{y1p+52}" text-anchor="end" font-size="10" fill="#6B6B6B">（已留育产品类）</text>')
    P.append('</svg>')
    return "".join(P)

# ============ SVG：DJI 回测图（不变） ============
def dji_svg(w=560, h=268):
    ml, mr, mt, mb = 42, 14, 14, 96
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
    P.append(f'<rect x="{X(3e5):.1f}" y="{y1p}" width="{X(4e5)-X(3e5):.1f}" height="{y0-y1p}" fill="#6B6B6B" fill-opacity="0.25"/>')
    P.append(f'<line x1="{X(1e6):.1f}" y1="{y1p}" x2="{X(1e6):.1f}" y2="{y0}" stroke="#B8860B" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(5e6):.1f}" y1="{y1p}" x2="{X(5e6):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="1.8" stroke-dasharray="5 4"/>')
    P.append(f'<line x1="{X(1e7):.1f}" y1="{y1p}" x2="{X(1e7):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2.2"/>')
    P.append(f'<rect x="{X(1e7):.1f}" y="{y1p}" width="{x1_-X(1e7):.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.10"/>')
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in [(0,"0"),(2e6,"200万"),(4e6,"400万"),(6e6,"600万"),(8e6,"800万"),(1e7,"1000万")]:
        P.append(f'<text x="{X(xv):.0f}" y="{y0+18}" text-anchor="middle" font-size="9.5" fill="#6B6B6B">{xl}</text>')
    # 图例行
    ly1 = y0 + 40
    for color, style, label, lx in [
        ("#6B6B6B", "rect", "内部预期 30–40万", x0),
        ("#B8860B", "dash", "上调 100万", x0 + 150),
        ("#EC008C", "dash", "2024 实售 500万", x0 + 255),
        ("#EC008C", "solid", "累计 1000万+", x0 + 395),
    ]:
        if style == "rect":
            P.append(f'<rect x="{lx:.0f}" y="{ly1-7}" width="18" height="9" fill="{color}" fill-opacity="0.3"/>')
        elif style == "dash":
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2" stroke-dasharray="5 3"/>')
        else:
            P.append(f'<line x1="{lx:.0f}" y1="{ly1-3}" x2="{lx+18:.0f}" y2="{ly1-3}" stroke="{color}" stroke-width="2.4"/>')
        P.append(f'<text x="{lx+23:.0f}" y="{ly1}" font-size="9.8" fill="#333">{label}</text>')
    ly2 = y0 + 58
    P.append(f'<text x="{x0:.0f}" y="{ly2}" font-size="9.5" fill="#6B6B6B">事前概率分布：参照前代 Pocket 2（对数正态）·  1000万+ 位于 P99.3 右尾（保留概率 0.7%）</text>')
    P.append('</svg>')
    return "".join(P)

SVG_S1 = s1_svg()
SVG_DJI = dji_svg()

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布 · 评审页（¥699 · v0.4）</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { background:#3a3a3a; }
  body { margin:0; }
  #slide { width:1280px; max-width:96vw; margin:24px auto; background:#FFF; font-family:"Microsoft YaHei",sans-serif;
           color:#111; box-shadow:0 8px 40px rgba(0,0,0,.45); }
  .pad { padding:22px 32px 14px; display:flex; flex-direction:column; }
  .hd { display:flex; align-items:flex-end; justify-content:space-between; border-bottom:2.5px solid #111; padding-bottom:8px; }
  .hd h1 { font-size:25px; }
  .hd h1 em { color:#EC008C; font-style:normal; }
  .hd .tag { font-size:11px; color:#fff; background:#111; padding:4px 10px; border-radius:3px; letter-spacing:1px; }
  .sec { margin-top:14px; display:flex; align-items:center; gap:10px; }
  .sec .bar { width:5px; height:20px; background:#EC008C; border-radius:2px; }
  .sec h2 { font-size:17px; letter-spacing:1px; }
  .sec .n { font-size:10.5px; color:#9a9a9a; margin-left:2px; }
  .outrow { display:flex; gap:14px; margin-top:8px; }
  .out { flex:1; border:2px solid #111; border-radius:8px; padding:8px 12px 4px; display:flex; flex-direction:column; background:#fff; }
  .out .step { font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }
  .out h3 { font-size:15px; margin:4px 0 0; }
  .out .nums { font-size:12px; margin-top:2px; font-variant-numeric:tabular-nums; }
  .out .nums b { color:#111; }
  .out .chart { flex:1; display:flex; align-items:center; justify-content:center; }
  .out .chart svg { width:100%; max-height:200px; }
  .kpirow { display:flex; gap:12px; margin-top:10px; }
  .kpi { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:8px 12px; background:#fff; }
  .kpi .k { font-size:10.5px; color:#6B6B6B; }
  .kpi .v { font-size:22px; font-weight:bold; margin-top:2px; font-variant-numeric:tabular-nums; }
  .kpi .v em { font-size:11px; font-style:normal; color:#6B6B6B; }
  .kpi .s { font-size:9.8px; color:#9a9a9a; margin-top:2px; line-height:1.45; }
  .btrow { display:flex; gap:14px; margin-top:10px; }
  .bt { flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:8px 12px; background:#fff; }
  .bt .step { font-size:10px; color:#fff; background:#111; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; }
  .bt h4 { font-size:13.5px; margin:4px 0 2px; }
  .bt .fig svg { width:100%; max-height:250px; }
  .bt .cc { font-size:10.5px; line-height:1.55; color:#333; margin-top:4px; }
  .bt .cc b { color:#EC008C; }
  .ft { margin-top:12px; border-top:1.5px solid #111; padding-top:8px; display:flex; justify-content:space-between; }
  .ft .loop { font-size:11.5px; }
  .ft .loop b { color:#EC008C; }
  .ft .note { font-size:9.5px; color:#9a9a9a; text-align:right; line-height:1.5; }
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>AiKen 销量概率分布 <em>· ¥699（v0.4 实测校准）</em></h1>
    <div class="tag">SI/COA 评审 · 第④部分</div>
  </div>

  <div class="sec"><div class="bar"></div><h2>首年与三年销量概率分布</h2><span class="n">8,000 次蒙特卡洛 · 漏斗参数 S1 实测原样（¥1799 高价品参照，对 ¥699 偏保守）· 三档锚 = P20（Worst）/ P50（Normal）/ P90（Best）</span></div>
  <div class="outrow">
    <div class="out">
      <span class="step">首年</span>
      <h3>首年销量概率分布</h3>
      <div class="nums">P20·Worst <b>__Y1_P20__</b> ｜ P50·Normal <b>__Y1_P50__</b> ｜ P90·Best <b>__Y1_P90__</b></div>
      <div class="chart">__SVG_Y1__</div>
    </div>
    <div class="out">
      <span class="step">三年</span>
      <h3>三年累计销量概率分布</h3>
      <div class="nums">P20·Worst <b>__Y3_P20__</b> ｜ P50·Normal <b>__Y3_P50__</b> ｜ P90·Best <b>__Y3_P90__</b></div>
      <div class="chart">__SVG_Y3__</div>
    </div>
  </div>

  <div class="kpirow">
    <div class="kpi"><div class="k">Worst 锚（P20）</div><div class="v">__Y1_P20__<em> 台</em></div><div class="s">首年平均月销 ~__M_P20__ ｜ 跌破概率 20%（80% 置信守线）</div></div>
    <div class="kpi"><div class="k">Normal 锚（P50）</div><div class="v">__Y1_P50__<em> 台</em></div><div class="s">首年平均月销 ~__M_NORMAL__ ｜ 财务测算基准</div></div>
    <div class="kpi"><div class="k">Best 锚（P90）</div><div class="v">__Y1_P90__<em> 台</em></div><div class="s">首年平均月销 ~__M_BEST__ ｜ 冲刺带</div></div>
    <div class="kpi"><div class="k">预算杠杆 ×1.5</div><div class="v">P50 → __Y1B_P50__</div><div class="s">P(≥P90 Best) 10%→__BOOST_P90__ ｜ P(≥Worst P20) 80%→__BOOST_W20__ ｜ 花钱买概率增量</div></div>
  </div>

  <div class="btrow">
    <div class="bt">
      <span class="step">回测 1 · 内部</span>
      <h4>S1 贴纸一体机（¥1,799 · 2026-04 上市）</h4>
      <div class="fig">__SVG_S1__</div>
      <div class="cc">用 AiKen 同套方法，站在 S1 上市前「（仅用 N 系数据）」建模：<b>内部点预测 25,000 位于事前分布 P92——即模型当时就会预警「仅 8% 概率可达成」</b>；实际（宽口径 ~7,300）落在 P5 以下，验证悲观。偏差根源：N 系（已留育产品类）参数对 S1（需教育品类）系统性高估约 2 倍——<b>这直接决定了 AiKen 锚 S1 而非 N 系</b>，并已转化为 v0.4 参数余量。</div>
    </div>
    <div class="bt">
      <span class="step">回测 2 · 外部</span>
      <h4>DJI Osmo Pocket 3（¥3,499 · 2023-10 发布）</h4>
      <div class="fig">__SVG_DJI__</div>
      <div class="cc">事前分布（参照前代 Pocket 2）P50=60 万，与大疆内部预期（30–40万，P27–P36）同水平；实际 2024 实售 <b>500 万（P96.7）</b>、累计破 <b>1000 万（P99.3 右尾）</b>。没有人能预知爆发——大疆自己也 miss 了 25 倍——但分布右尾以 0.7% 概率保留了千万级结果，<b>点预测会直接排除它，分布不会</b>。</div>
    </div>
  </div>

  <div class="sec"><div class="bar"></div><h2>财务与 Checkpoint</h2><span class="n">¥699 口径 · 单台净贡献 102.25 元</span></div>
  <div class="kpirow">
    <div class="kpi"><div class="k">单台净贡献（30% 费用口径）</div><div class="v">102.25 <em>元</em></div><div class="s">ASP 不含税 503.22 × 70% − BOM 250 ｜ ASP 链：699 → 含税 618.58 → 扣渠道 568.64 → 不含税 503.22</div></div>
    <div class="kpi"><div class="k">首年净贡献（P50）</div><div class="v">__FIN_Y1__<em> 万元</em></div><div class="s">= 22,123 台 × 102.25 元 ｜ 三年累计 P50 = __FIN_Y3__ 万元</div></div>
    <div class="kpi"><div class="k">首年投入覆盖（P50）</div><div class="v">__COVER__<em>%</em></div><div class="s">投入 474.1 万（新 Budget 表 477.4 万口径）｜ 品牌投资型定位（非回本导向）</div></div>
    <div class="kpi"><div class="k">P(三年累计 ≥10万台)</div><div class="v">__P3_10W__<em>%</em></div><div class="s">三年 P50 = __Y3_P50__ 台</div></div>
  </div>

  <div class="ft">
    <div class="loop"><b>Checkpoint 闭环</b>：上市 30 / 90 天真实数据 → 更新 m·p·q → 分布收窄 → 预算/动作再决策 ↺</div>
    <div class="note">v0.4 参数：CPM 三角(38,45,65) ｜ CTR 三角(1.8%,2.3%,3.0%) ｜ CVR 三角(0.9%,1.4%,2.2%)（S1 实测+回测余量）<br>参照类：instax mini / Flashback One35 / Kodak / Paper Shoot（同价位带）+ S1（新品类锚）· Bass (1969) · 8,000 次蒙特卡洛 · 定价 ¥699 / BOM 250</div>
  </div>

</div></div>
</body>
</html>
"""

p20 = pct(y1, 20)
html = (HTML
    .replace("__SVG_Y1__", SVG_Y1)
    .replace("__SVG_Y3__", SVG_Y3)
    .replace("__SVG_S1__", SVG_S1)
    .replace("__SVG_DJI__", SVG_DJI)
    .replace("__Y1_P10__", f"{pct(y1,10):,.0f}")
    .replace("__Y1_P50__", f"{pct(y1,50):,.0f}")
    .replace("__Y1_P90__", f"{pct(y1,90):,.0f}")
    .replace("__Y1_P20__", f"{p20:,.0f}")
    .replace("__Y3_P20__", f"{pct(y3,20)/1e4:.1f}万")
    .replace("__Y3_P10__", f"{pct(y3,10)/1e4:.1f}万")
    .replace("__Y3_P50__", f"{pct(y3,50)/1e4:.1f}万")
    .replace("__Y3_P90__", f"{pct(y3,90)/1e4:.1f}万")
    .replace("__M_WORST__", f"{pct(y1,10)/12:,.0f}")
    .replace("__M_P20__", f"{p20/12:,.0f}")
    .replace("__M_NORMAL__", f"{pct(y1,50)/12:,.0f}")
    .replace("__M_BEST__", f"{pct(y1,90)/12:,.0f}")
    .replace("__Y1B_P50__", f"{pct(y1_b,50):,.0f}")
    .replace("__BOOST_P90__", f"{prob(y1_b, pct(y1,90))*100:.0f}%")
    .replace("__BOOST_W20__", f"{prob(y1_b, pct(y1,20))*100:.0f}%")
    .replace("__BOOST_BEST__", f"{prob(y1_b, 30000)*100:.0f}%")
    .replace("__FIN_Y1__", f"{pct(y1,50)*102.25/1e4:.0f}")
    .replace("__FIN_Y3__", f"{pct(y3,50)*102.25/1e4:.0f}")
    .replace("__COVER__", f"{pct(y1,50)*102.25/4_740_550*100:.0f}")
    .replace("__P3_10W__", f"{prob(y3,100_000)*100:.0f}")
)

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率分布_评审页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", OUT)
print(f"key: Y1 P10={pct(y1,10):,.0f} P20={p20:,.0f} P50={pct(y1,50):,.0f} P90={pct(y1,90):,.0f} | Y3 P50={pct(y3,50):,.0f} | boost P50={pct(y1_b,50):,.0f}")
