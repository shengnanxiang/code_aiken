# -*- coding: utf-8 -*-
"""
S1 Checkpoint 校准可视化 HTML + 分位表 Excel
================================================
左图（首年）+ 右图（三年），各含事前/事后双分布叠加
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_calibration.npz")
y1_pre, y3_pre = D["y1_pre"], D["y3_pre"]
y1_post, y3_post = D["y1_post"], D["y3_post"]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ============ SVG：双分布叠加图 ============
def dual_hist(pre, post, w=580, h=250, vmax=30_000, nbins=50,
              obs=None, marks=None, xticks=None, title_note=""):
    ml, mr, mt, mb = 52, 16, 30, 42
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    c_pre, _ = np.histogram(pre, bins=nbins, range=(0, vmax))
    c_post, _ = np.histogram(post, bins=nbins, range=(0, vmax))
    cmax = max(c_pre.max(), c_post.max())
    def X(v): return x0 + (min(v, vmax) / vmax) * (x1_ - x0)
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#F0F0F0" stroke-width="1"/>')
    bw = (x1_ - x0) / nbins
    # 事前（灰色轮廓 + 淡填充）
    for i, c in enumerate(c_pre):
        bh = (c / cmax) * (y0 - y1p) * 0.92
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.92:.1f}" height="{bh:.1f}" fill="#B8B8B8" fill-opacity="0.35" stroke="#999" stroke-width="0.5" rx="1"/>')
    # 事后（黑色实心）
    for i, c in enumerate(c_post):
        bh = (c / cmax) * (y0 - y1p) * 0.92
        if bh <= 0.5: continue
        P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.92:.1f}" height="{bh:.1f}" fill="#111" fill-opacity="0.85" rx="1"/>')
    # 观测线
    if obs:
        v, lab = obs
        P.append(f'<line x1="{X(v):.1f}" y1="{y1p}" x2="{X(v):.1f}" y2="{y0}" stroke="#EC008C" stroke-width="2.2" stroke-dasharray="6 4"/>')
        P.append(f'<text x="{X(v):.1f}" y="{mt-10}" text-anchor="middle" font-size="11" fill="#EC008C" font-weight="bold">{lab}</text>')
    # marks
    for v, label, color in (marks or []):
        P.append(f'<line x1="{X(v):.1f}" y1="{y1p}" x2="{X(v):.1f}" y2="{y0}" stroke="{color}" stroke-width="1.6" stroke-dasharray="4 3"/>')
        P.append(f'<text x="{X(v):.1f}" y="{y0+17}" text-anchor="middle" font-size="10.5" fill="{color}" font-weight="bold">{label}</text>')
    # 轴
    P.append(f'<line x1="{x0}" y1="{y0}" x2="{x1_}" y2="{y0}" stroke="#111" stroke-width="1.5"/>')
    for xv, xl in (xticks or []):
        P.append(f'<text x="{X(xv):.0f}" y="{y0+32}" text-anchor="middle" font-size="10" fill="#6B6B6B">{xl}</text>')
    P.append(f'<text x="{x0-8}" y="{y1p+4}" text-anchor="end" font-size="10" fill="#6B6B6B">概率密度</text>')
    # 图例
    P.append(f'<rect x="{x1_-210}" y="{mt-14}" width="22" height="10" rx="2" fill="#B8B8B8" fill-opacity="0.45" stroke="#999" stroke-width="0.5"/>')
    P.append(f'<text x="{x1_-184}" y="{mt-5}" font-size="10.5" fill="#555">事前（N 系参数）</text>')
    P.append(f'<rect x="{x1_-80}" y="{mt-14}" width="22" height="10" rx="2" fill="#111" fill-opacity="0.85"/>')
    P.append(f'<text x="{x1_-54}" y="{mt-5}" font-size="10.5" fill="#111" font-weight="bold">事后（校准）</text>')
    if title_note:
        P.append(f'<text x="{x0}" y="{mt-5}" font-size="10" fill="#9a9a9a">{title_note}</text>')
    P.append('</svg>')
    return "".join(P)

SVG_Y1 = dual_hist(y1_pre, y1_post, vmax=30_000, nbins=50,
    obs=(7_285, "观测：首年宽口径 ~7,285"),
    marks=[(pct(y1_pre,50), f"事前P50 {pct(y1_pre,50):,.0f}", "#888"),
           (pct(y1_post,50), f"事后P50 {pct(y1_post,50):,.0f}", "#111")],
    xticks=[(0,"0"),(6e3,"6千"),(1.2e4,"1.2万"),(1.8e4,"1.8万"),(2.4e4,"2.4万"),(3e4,"3万")])

SVG_Y3 = dual_hist(y3_pre, y3_post, vmax=90_000, nbins=50,
    marks=[(pct(y3_pre,50), f"事前P50 {pct(y3_pre,50)/1e4:.1f}万", "#888"),
           (pct(y3_post,50), f"事后P50 {pct(y3_post,50)/1e4:.1f}万", "#111")],
    xticks=[(0,"0"),(2e4,"2万"),(4e4,"4万"),(6e4,"6万"),(8e4,"8万")])

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>S1 Checkpoint 校准 · 事前 vs 事后</title>
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
  .obs {{ margin-top:12px; background:#FDF3F8; border:1.5px solid #EC008C; border-radius:8px; padding:10px 16px; display:flex; gap:20px; align-items:center; }}
  .obs .lbl {{ flex:none; font-size:11px; font-weight:bold; color:#EC008C; letter-spacing:2px; border:1.5px solid #EC008C; padding:2px 8px; border-radius:3px; }}
  .obs .txt {{ font-size:12px; line-height:1.6; color:#111; }}
  .obs .txt b {{ color:#EC008C; }}
  .charts {{ display:flex; gap:14px; margin-top:12px; }}
  .chart {{ flex:1; border:2px solid #111; border-radius:8px; padding:9px 13px 5px; display:flex; flex-direction:column; background:#fff; }}
  .chart .step {{ font-size:10px; color:#fff; background:#EC008C; display:inline-block; padding:2px 8px; border-radius:2px; letter-spacing:1px; width:fit-content; }}
  .chart h3 {{ font-size:15px; margin:4px 0 0; }}
  .chart .fig {{ flex:1; display:flex; align-items:center; justify-content:center; }}
  .chart .fig svg {{ width:100%; max-height:252px; }}
  .numline {{ display:flex; gap:10px; margin-top:8px; }}
  .nc {{ flex:1; text-align:center; border:1px solid #E6E6E6; border-radius:6px; padding:4px 2px; }}
  .nc .nt {{ font-size:10px; color:#6B6B6B; }}
  .nc .nv {{ font-size:14px; font-weight:bold; margin-top:1px; font-variant-numeric:tabular-nums; }}
  .nc.pre .nv {{ color:#777; }} .nc.post .nv {{ color:#111; }}
  .kpirow {{ display:flex; gap:12px; margin-top:12px; }}
  .kpi {{ flex:1; border:1.5px solid #E6E6E6; border-radius:8px; padding:8px 12px; background:#fff; }}
  .kpi .k {{ font-size:10.5px; color:#6B6B6B; }}
  .kpi .v {{ font-size:21px; font-weight:bold; margin-top:2px; font-variant-numeric:tabular-nums; }}
  .kpi .v em {{ font-size:11px; font-style:normal; color:#6B6B6B; }}
  .kpi .s {{ font-size:9.8px; color:#9a9a9a; margin-top:2px; line-height:1.45; }}
  .ft {{ margin-top:12px; border-top:1.5px solid #111; padding-top:8px; font-size:10px; color:#9a9a9a; display:flex; justify-content:space-between; line-height:1.5; }}
</style>
</head>
<body>
<div id="slide"><div class="pad">

  <div class="hd">
    <h1>S1 Checkpoint 校准 <em>· 事前预测 vs 真实数据校准后</em></h1>
    <div class="tag">模型验证 · 上市 8 个月数据</div>
  </div>

  <div class="obs">
    <div class="lbl">观测</div>
    <div class="txt">
      2026-03 至 2026-10（上市后 8 个月）：总投放花费 <b>~184 万</b>（站内 30.6 万 + 站外 153 万）· CPM ~43 · CTR 2.14% ·
      JD 直接归因订单 <b>1,416 台</b> → 全渠道宽口径销量 <b>~7,285 台/首年外推</b>（8 个月实际 ~4,850 台）。
      校准方法：近似贝叶斯（ABC）——用 8 个月销量观测对事前先验 (m·q) 重加权，漏斗实测参数代入。
    </div>
  </div>

  <div class="charts">
    <div class="chart">
      <span class="step">首年</span>
      <h3>首年销量：事前 vs 事后</h3>
      <div class="fig">{SVG_Y1}</div>
      <div class="numline">
        <div class="nc pre"><div class="nt">事前 P50</div><div class="nv">{pct(y1_pre,50):,.0f}</div></div>
        <div class="nc pre"><div class="nt">事前 P5–P95</div><div class="nv">{pct(y1_pre,5):,.0f}–{pct(y1_pre,95):,.0f}</div></div>
        <div class="nc post"><div class="nt">事后 P50</div><div class="nv">{pct(y1_post,50):,.0f}</div></div>
        <div class="nc post"><div class="nt">事后 P5–P95</div><div class="nv">{pct(y1_post,5):,.0f}–{pct(y1_post,95):,.0f}</div></div>
      </div>
    </div>
    <div class="chart">
      <span class="step">三年</span>
      <h3>三年累计销量：事前 vs 事后</h3>
      <div class="fig">{SVG_Y3}</div>
      <div class="numline">
        <div class="nc pre"><div class="nt">事前 P50</div><div class="nv">{pct(y3_pre,50)/1e4:.1f}万</div></div>
        <div class="nc pre"><div class="nt">事前 P5–P95</div><div class="nv">{pct(y3_pre,5)/1e4:.1f}–{pct(y3_pre,95)/1e4:.1f}万</div></div>
        <div class="nc post"><div class="nt">事后 P50</div><div class="nv">{pct(y3_post,50)/1e4:.1f}万</div></div>
        <div class="nc post"><div class="nt">事后 P5–P95</div><div class="nv">{pct(y3_post,5)/1e4:.1f}–{pct(y3_post,95)/1e4:.1f}万</div></div>
      </div>
    </div>
  </div>

  <div class="kpirow">
    <div class="kpi"><div class="k">首年分布收窄</div><div class="v">20,468 → 907 <em>台</em></div><div class="s">P5–P95 宽度收窄 96% ｜ 事后 P50 = 观测锚 {pct(y1_post,50):,.0f} ≈ 7,285</div></div>
    <div class="kpi"><div class="k">三年分布收窄</div><div class="v">63,827 → 21,859 <em>台</em></div><div class="s">P5–P95 宽度收窄 66% ｜ 三年仍有长尾（口碑 q 后验未定）</div></div>
    <div class="kpi"><div class="k">内部预测 25,000 的落点</div><div class="v">P92 → P100</div><div class="s">事后分布下达成概率 0.0%——点预测的乐观偏差被校准彻底暴露</div></div>
    <div class="kpi"><div class="k">对 AiKen 的意义</div><div class="v">30/90 天 Checkpoint</div><div class="s">S1 用 8 个月收窄 96%；AiKen 按节奏 30 天即可收一轮，90 天再收一轮</div></div>
  </div>

  <div class="ft">
    <span>事前分布 = N 系参数 ex-ante 模型（2026-04 站位，与评审页「回测 1」同源）· 事后 = ABC 近似贝叶斯校准</span>
    <span>配套文件：S1校准_分位表.xlsx（事前/事后完整分位，可直接复制进 PPT）</span>
  </div>

</div></div>
</body>
</html>
"""

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\S1校准_事前vs事后.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("HTML saved:", OUT)

# ============ Excel 分位表 ============
wb = Workbook()
HDR_FILL = PatternFill("solid", fgColor="111111")
HDR_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
B_FONT = Font(name="微软雅黑", size=10, bold=True)
N_FONT = Font(name="微软雅黑", size=10)
S_FONT = Font(name="微软雅黑", size=9, color="6B6B6B")
THIN = Border(*[Side(style="thin", color="D9D9D9")] * 4)
CENTER = Alignment(horizontal="center", vertical="center")

def style_row(ws, row, cols, font=None, fill=None):
    for c in cols:
        cell = ws.cell(row=row, column=c)
        cell.font = font or N_FONT
        cell.border = THIN
        if fill: cell.fill = fill
        if c > 1: cell.alignment = CENTER

# Sheet1 首年
ws = wb.active
ws.title = "首年分位对比"
ws["B2"] = "S1 首年销量 · 事前 vs 事后（校准后）分位表"
ws["B2"].font = Font(name="微软雅黑", size=13, bold=True)
ws["B3"] = "事前 = N 系参数 ex-ante（2026-04 站位）｜ 事后 = 上市 8 个月真实数据 ABC 校准 ｜ 观测锚：首年宽口径 ~7,285 台"
ws["B3"].font = S_FONT
r = 5
for j, h in enumerate(["分位", "事前（台）", "事后（台）", "收窄方向", "备注"], 2):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(2, 7), HDR_FONT, HDR_FILL)
r += 1
NOTES = {5: "悲观边界", 50: "中位数", 95: "乐观边界"}
for qn in [5, 10, 25, 50, 75, 90, 95]:
    ws.cell(row=r, column=2, value=f"P{qn}")
    ws.cell(row=r, column=3, value=round(pct(y1_pre, qn)))
    ws.cell(row=r, column=4, value=round(pct(y1_post, qn)))
    ws.cell(row=r, column=5, value=f"{pct(y1_post,qn)/pct(y1_pre,qn)*100:.0f}%")
    ws.cell(row=r, column=6, value=NOTES.get(qn, ""))
    style_row(ws, r, range(2, 7))
    if qn == 50:
        for j in range(2, 7): ws.cell(row=r, column=j).font = B_FONT
    r += 1
r += 1
ws.cell(row=r, column=2, value="关键对照").font = B_FONT
r += 1
for label, v_pre, v_post in [
    ("内部点预测 25,000 落点", "P92", "P100（0.0% 概率达成）"),
    ("观测锚 7,285 落点", "P5 以下", "≈ P50（事后中心）"),
    ("P(首年 ≥ 10,000)", f"{prob(y1_pre,10000)*100:.1f}%", f"{prob(y1_post,10000)*100:.1f}%"),
    ("P(首年 ≥ 25,000)", f"{prob(y1_pre,25000)*100:.1f}%", f"{prob(y1_post,25000)*100:.1f}%"),
]:
    ws.cell(row=r, column=2, value=label)
    ws.cell(row=r, column=3, value=v_pre)
    ws.cell(row=r, column=4, value=v_post)
    style_row(ws, r, range(2, 5))
    r += 1
for col, w_ in zip("BCDEFG", [28, 15, 15, 13, 16]):
    ws.column_dimensions[col].width = w_

# Sheet2 三年
ws2 = wb.create_sheet("三年分位对比")
ws2["B2"] = "S1 三年累计销量 · 事前 vs 事后（校准后）分位表"
ws2["B2"].font = Font(name="微软雅黑", size=13, bold=True)
ws2["B3"] = "三年仍有长尾：q（口碑系数）后验未被 8 个月数据强约束，第 2-3 年的口碑起飞仍具不确定性"
ws2["B3"].font = S_FONT
r = 5
for j, h in enumerate(["分位", "事前（台）", "事后（台）", "事后/事前"], 2):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(2, 6), HDR_FONT, HDR_FILL)
r += 1
for qn in [5, 10, 25, 50, 75, 90, 95]:
    ws2.cell(row=r, column=2, value=f"P{qn}")
    ws2.cell(row=r, column=3, value=round(pct(y3_pre, qn)))
    ws2.cell(row=r, column=4, value=round(pct(y3_post, qn)))
    ws2.cell(row=r, column=5, value=f"{pct(y3_post,qn)/pct(y3_pre,qn)*100:.0f}%")
    style_row(ws2, r, range(2, 6))
    if qn == 50:
        for j in range(2, 6): ws2.cell(row=r, column=j).font = B_FONT
    r += 1
r += 1
ws2.cell(row=r, column=2, value="P(三年累计 ≥ 10万)").font = B_FONT
ws2.cell(row=r, column=3, value=f"{prob(y3_pre,1e5)*100:.1f}%")
ws2.cell(row=r, column=4, value=f"{prob(y3_post,1e5)*100:.1f}%")
style_row(ws2, r, range(2, 5))
for col, w_ in zip("BCDE", [28, 15, 15, 13]):
    ws2.column_dimensions[col].width = w_

# Sheet3 校准说明
ws3 = wb.create_sheet("校准说明")
ws3["B2"] = "这次校准做了什么（Checkpoint 机制的首次真实运行）"
ws3["B2"].font = Font(name="微软雅黑", size=13, bold=True)
notes = [
    ("观测数据", "2026-03 至 2026-10（8 个月）：JD 站内直接归因 1,416 台；总花费 ~184 万（站内 30.6 万 + 站外小红书/抖音 153 万）；CPM ~43 · CTR 2.14%。宽口径销量（全渠道含自然）：首年外推 ~7,285 台。"),
    ("校准方法", "近似贝叶斯（ABC 拒绝采样）：① 保留事前先验的 8,000 组 (m·q) 样本；② 用 8 个月销量观测（~4,850 台，含归因不确定性 σ）构造似然权重；③ 加权重抽样得事后 (m·q) 后验；④ 代入实测漏斗参数重跑 Bass 轨迹。"),
    ("为什么首年收窄 96%", "8 个月销量观测几乎完全决定了首年结果（12 个月中已有 8 个月的事实），剩余不确定性只有最后 4 个月的外推。"),
    ("为什么三年只收窄 66%", "q（口碑系数）在 8 个月冷启动期尚未充分显形——S1 的口碑是否会在第 2-3 年起飞（类似 instax 的慢热），现有数据无法强约束。这正是 90 天 / 180 天 Checkpoint 要继续收的部分。"),
    ("对 AiKen 的直接意义", "① Checkpoint 机制真实有效：一次数据回灌就把首年不确定性砍掉 96%；② 事前分布的「悲观半区」是对的——实际落在事前 P5 以下，验证了分布方法的价值（点预测 25,000 完全没有暴露这个风险）；③ AiKen 的 30 天 Checkpoint 设计有依据了：比 S1 这次（等效 8 个月才回灌）更早、更频繁。"),
    ("注意事项", "宽口径销量 ~7,285 含「全渠道 ×3」的换算假设（JD 归因 1,416 × 3 倍，Maggie 口径的天猫/抖音/自然流量补偿）。若实际全渠道系数 ≠ 3，观测锚会平移，事后分布随之平移——建议 AiKen 上市时埋好全渠道归因，避免换算假设。"),
]
r = 4
for q_, a_ in notes:
    ws3.cell(row=r, column=2, value=q_).font = B_FONT
    ws3.cell(row=r, column=3, value=a_).font = N_FONT
    ws3.cell(row=r, column=3).alignment = Alignment(wrap_text=True, vertical="top")
    ws3.row_dimensions[r].height = 52
    r += 1
ws3.column_dimensions["B"].width = 24
ws3.column_dimensions["C"].width = 105

XLSX = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\S1校准_分位表.xlsx"
wb.save(XLSX)
print("Excel saved:", XLSX)
