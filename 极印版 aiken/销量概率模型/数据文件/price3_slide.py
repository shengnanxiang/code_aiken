# -*- coding: utf-8 -*-
"""三价位对比 HTML 生成：599 / 699 / 749 同图分色直方图"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

d = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\price3_results.npz")
y1s = {599: d["y1_599"], 699: d["y1_699"], 749: d["y1_749"]}
y3s = {599: d["y3_599"], 699: d["y3_699"], 749: d["y3_749"]}

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())
W = lambda v: f"{v/1e4:.2f}"

COLORS = {599: "#111111", 699: "#00A5A5", 749: "#EC008C"}

def overlay_hist(data_dict, w=560, h=210, nbins=46, vmax=80_000, unit=1e4,
                 marks=("P50",), shade=None, xticks=None, ymax_adj=1.28):
    """三价位叠加直方图：色块半透明 + P50 竖线"""
    ml, mr, mt, mb = 44, 14, 22, 38
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#F0F0F0" stroke-width="1"/>')
    # 各价位直方（半透明叠加）
    bw = (x1_ - x0) / nbins
    for price, data in data_dict.items():
        counts, _ = np.histogram(data, bins=nbins, range=(0, vmax))
        cmax_all = max(np.histogram(dd, bins=nbins, range=(0, vmax))[0].max() for dd in data_dict.values())
        for i, c in enumerate(counts):
            bh = (c / cmax_all) * (y0 - y1p) / ymax_adj
            if bh <= 0.5: continue
            P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.94:.1f}" height="{bh:.1f}" '
                     f'fill="{COLORS[price]}" fill-opacity="0.30" rx="1"/>')
    # P50 竖线
    for price, data in data_dict.items():
        v = pct(data, 50)
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<line x1="{sx:.1f}" y1="{y1p}" x2="{sx:.1f}" y2="{y0}" stroke="{COLORS[price]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        P.append(f'<text x="{sx:.1f}" y="{y0+15}" text-anchor="middle" font-size="10.5" fill="{COLORS[price]}" font-weight="bold">{W(v)}万</text>')
    # shade
    if shade:
        v, lab = shade
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<rect x="{sx:.1f}" y="{y1p}" width="{x1_-sx:.1f}" height="{y0-y1p}" fill="#EC008C" fill-opacity="0.06"/>')
    # 轴
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in (xticks or []):
        sx = x0 + (xv / vmax) * (x1_ - x0)
        P.append(f'<text x="{sx:.0f}" y="{y0+30}" text-anchor="middle" font-size="10" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x0-8}" y="{y1p+4}" text-anchor="end" font-size="10" fill="#6B6B6B">概率密度</text>')
    P.append('</svg>')
    return "".join(P)

def legend_svg(w=560, h=30):
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    lx = 8
    items = [(599, "¥599（BOM 250）"), (699, "¥699（BOM 250）"), (749, "¥749（BOM 280）")]
    for price, label in items:
        P.append(f'<rect x="{lx}" y="9" width="24" height="10" rx="2" fill="{COLORS[price]}" fill-opacity="0.45"/>')
        P.append(f'<line x1="{lx}" y1="24" x2="{lx+24}" y2="24" stroke="{COLORS[price]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        P.append(f'<text x="{lx+30}" y="18" font-size="10.5" fill="#333">{label}</text>')
        lx += 30 + len(label) * 11.5 + 26
    P.append(f'<text x="{w-6}" y="18" text-anchor="end" font-size="9.5" fill="#9a9a9a">虚线 = P50</text>')
    P.append('</svg>')
    return "".join(P)

SVG_Y1 = overlay_hist(y1s, w=560, h=212, vmax=80_000,
    shade=(36_000, "Best"),
    xticks=[(0,"0"),(2e4,"2万"),(4e4,"4万"),(6e4,"6万"),(8e4,"8万")])
SVG_Y3 = overlay_hist(y3s, w=560, h=212, vmax=200_000,
    xticks=[(0,"0"),(5e4,"5万"),(1e5,"10万"),(1.5e5,"15万"),(2e5,"20万")])
SVG_LEG = legend_svg()

def nums_row(titles, vals):
    cells = ""
    for t, v in zip(titles, vals):
        cells += f'<div class="nc"><div class="nt">{t}</div><div class="nv">{v}</div></div>'
    return cells

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布 · 三价位对比</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ background:#3a3a3a; }}
  body {{ margin:0; }}
  #slide {{ width:1280px; max-width:96vw; margin:24px auto; background:#FFF; font-family:"Microsoft YaHei",sans-serif;
           color:#111; box-shadow:0 8px 40px rgba(0,0,0,.45); }}
  .pad {{ padding:24px 34px 16px; display:flex; flex-direction:column; }}
  .hd {{ display:flex; align-items:flex-end; justify-content:space-between; border-bottom:2.5px solid #111; padding-bottom:8px; }}
  .hd h1 {{ font-size:25px; }}
  .hd h1 em {{ color:#EC008C; font-style:normal; }}
  .hd .tag {{ font-size:11px; color:#fff; background:#111; padding:4px 10px; border-radius:3px; letter-spacing:1px; }}
  .note {{ margin-top:10px; font-size:11px; color:#444; background:#F7F7F7; border-radius:6px; padding:7px 14px; line-height:1.55; }}
  .note b {{ color:#111; }}
  .outrow {{ display:flex; gap:14px; margin-top:12px; }}
  .out {{ flex:1; border:2px solid #111; border-radius:8px; padding:9px 13px 5px; display:flex; flex-direction:column; background:#fff; }}
  .out .step {{ font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }}
  .out h3 {{ font-size:15.5px; margin:4px 0 0; }}
  .out .chart {{ flex:1; display:flex; flex-direction:column; align-items:center; margin-top:2px; }}
  .out .chart svg {{ width:100%; max-height:214px; }}
  .numline {{ display:flex; gap:10px; margin-top:8px; }}
  .nc {{ flex:1; text-align:center; border:1px solid #E6E6E6; border-radius:6px; padding:4px 2px; }}
  .nc .nt {{ font-size:10px; color:#6B6B6B; }}
  .nc .nv {{ font-size:14px; font-weight:bold; margin-top:1px; font-variant-numeric:tabular-nums; }}
  .nc.c599 .nv {{ color:#111; }} .nc.c699 .nv {{ color:#00A5A5; }} .nc.c749 .nv {{ color:#EC008C; }}
  .tbl {{ margin-top:14px; border:1.5px solid #111; border-radius:8px; padding:10px 16px 12px; }}
  .tbl h4 {{ font-size:14px; margin-bottom:6px; }}
  .tbl table {{ border-collapse:collapse; width:100%; }}
  .tbl th {{ font-size:10.5px; color:#fff; background:#111; padding:4px 10px; text-align:center; font-weight:normal; }}
  .tbl th:first-child {{ text-align:left; border-radius:3px 0 0 0; }}
  .tbl th:last-child {{ border-radius:0 3px 0 0; }}
  .tbl td {{ font-size:11.5px; padding:4px 10px; border-bottom:1px solid #E6E6E6; text-align:center; font-variant-numeric:tabular-nums; }}
  .tbl td:first-child {{ text-align:left; font-weight:bold; }}
  .tbl tr:last-child td {{ border-bottom:none; }}
  .tbl td.c599 {{ border-left:3px solid #111; }} .tbl td.c699 {{ border-left:3px solid #00A5A5; }} .tbl td.c749 {{ border-left:3px solid #EC008C; }}
  .ft {{ margin-top:12px; border-top:1.5px solid #111; padding-top:8px; font-size:10px; color:#9a9a9a; display:flex; justify-content:space-between; line-height:1.5; }}
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>AiKen 销量概率分布 <em>· 三价位对比</em></h1>
    <div class="tag">¥599 / ¥699 / ¥749</div>
  </div>

  <div class="note">
    涨价对销量的影响走<b>转化率（CVR）通道</b>，恒定弹性约 −1.5（PSM 证据中档）：¥699 → CVR × 0.80，¥749 → CVR × 0.72；投放预算、CPM、CTR 不变（8000 次蒙特卡洛，与 v0.2 同种子）。<b>BOM</b>：¥599→250 ｜ ¥699→250 ｜ ¥749→280。弹性敏感性见 Excel 分位表第二页。
  </div>

  <div class="outrow">
    <div class="out">
      <span class="step">首年</span>
      <h3>首年销量概率分布</h3>
      <div class="chart">{SVG_Y1}</div>
      <div class="numline">
        <div class="nc c599"><div class="nt">¥599 P50</div><div class="nv">{W(pct(y1s[599],50))}万</div></div>
        <div class="nc c699"><div class="nt">¥699 P50</div><div class="nv">{W(pct(y1s[699],50))}万</div></div>
        <div class="nc c749"><div class="nt">¥749 P50</div><div class="nv">{W(pct(y1s[749],50))}万</div></div>
      </div>
    </div>
    <div class="out">
      <span class="step">三年</span>
      <h3>三年累计销量概率分布</h3>
      <div class="chart">{SVG_Y3}</div>
      <div class="numline">
        <div class="nc c599"><div class="nt">¥599 P50</div><div class="nv">{W(pct(y3s[599],50))}万</div></div>
        <div class="nc c699"><div class="nt">¥699 P50</div><div class="nv">{W(pct(y3s[699],50))}万</div></div>
        <div class="nc c749"><div class="nt">¥749 P50</div><div class="nv">{W(pct(y3s[749],50))}万</div></div>
      </div>
    </div>
  </div>

  <div style="margin-top:8px; margin-left:6px;">{SVG_LEG}</div>

  <div class="tbl">
    <h4>三价位对照表（P5 / P50 / P95，万台）</h4>
    <table>
      <tr><th>指标</th><th>¥599</th><th>¥699</th><th>¥749</th></tr>
      <tr><td>首年销量</td><td class="c599">{W(pct(y1s[599],5))} / {W(pct(y1s[599],50))} / {W(pct(y1s[599],95))}</td><td class="c699">{W(pct(y1s[699],5))} / {W(pct(y1s[699],50))} / {W(pct(y1s[699],95))}</td><td class="c749">{W(pct(y1s[749],5))} / {W(pct(y1s[749],50))} / {W(pct(y1s[749],95))}</td></tr>
      <tr><td>三年累计销量</td><td class="c599">{W(pct(y3s[599],5))} / {W(pct(y3s[599],50))} / {W(pct(y3s[599],95))}</td><td class="c699">{W(pct(y3s[699],5))} / {W(pct(y3s[699],50))} / {W(pct(y3s[699],95))}</td><td class="c749">{W(pct(y3s[749],5))} / {W(pct(y3s[749],50))} / {W(pct(y3s[749],95))}</td></tr>
      <tr><td>P(首年≥会议Normal 1.2万)</td><td class="c599">{prob(y1s[599],12000)*100:.0f}%</td><td class="c699">{prob(y1s[699],12000)*100:.0f}%</td><td class="c749">{prob(y1s[749],12000)*100:.0f}%</td></tr>
      <tr><td>P(首年≥会议Best 3.6万)</td><td class="c599">{prob(y1s[599],36000)*100:.0f}%</td><td class="c699">{prob(y1s[699],36000)*100:.0f}%</td><td class="c749">{prob(y1s[749],36000)*100:.0f}%</td></tr>
    </table>
  </div>

  <div class="ft">
    <span>模型：RCF 参照类 + Bass 扩散 + 蒙特卡洛（种子 20261022）· 漏斗参数为行业通带占位，待市场部实测校准</span>
    <span>配套文件：AiKen三价位销量概率分布_分位表.xlsx（含弹性/BOM 敏感性）</span>
  </div>

</div></div>
</body>
</html>
"""

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen三价位销量概率分布对比页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("HTML saved:", OUT)
