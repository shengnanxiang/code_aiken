# -*- coding: utf-8 -*-
"""三价位对比 v2（v0.4 口径）：Excel 分位表 + HTML 对比页"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

d = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\price3_results.npz")
y1s = {599: d["y1_599"], 699: d["y1_699"], 749: d["y1_749"]}
y3s = {599: d["y3_599"], 699: d["y3_699"], 749: d["y3_749"]}

# 敏感性重算（v0.4 参数）
rng = np.random.default_rng(20261022)
N_SIM = 8000
m_prior = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR0 = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)
clicks = (B_budget / CPM * 1000) * CTR
t_year = np.arange(1, 37) / 12.0

def bass_cum_year(m, p, q, t):
    t = np.asarray(t, dtype=float)
    return m * (1 - np.exp(-(p + q) * t)) / (1 + (q / p) * np.exp(-(p + q) * t))

def solve_p(m, q, s6t):
    lo = np.full_like(m, 1e-5); hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        small = bass_cum_year(m, mid, q, 0.5) < s6t
        lo = np.where(small, mid, lo); hi = np.where(small, hi, mid)
    return 0.5 * (lo + hi)

def run(mult):
    cvr = np.clip(CVR0 * mult, 0.004, 0.026)
    s6 = np.minimum(clicks * cvr, m_prior * 0.55)
    p = solve_p(m_prior, q_prior, s6)
    paths = bass_cum_year(m_prior[:, None], p[:, None], q_prior[:, None], t_year[None, :])
    return paths[:, 11], paths[:, 35]

sens = {}
for price, elast in [(699, -1.0), (699, -1.8), (749, -1.0), (749, -1.8)]:
    sens[(price, elast)] = run((price / 599.0) ** elast)

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())
W = lambda v: f"{v/1e4:.2f}"

CH, SR, NRE = 0.25, 0.08, 6_300_000
def fin(price, bom, y1, y3):
    unit = price * (1 - CH - SR) - bom
    return dict(unit=unit, cm1=pct(y1*unit,50), cm3=pct(y3*unit,50),
                pt=prob(y3*unit-NRE,0), pn=prob(y1*unit,0.6*NRE), rev3=pct(y3*price,50))

FIN = {(599,250): fin(599,250,y1s[599],y3s[599]),
       (699,250): fin(699,250,y1s[699],y3s[699]),
       (699,280): fin(699,280,y1s[699],y3s[699]),
       (749,280): fin(749,280,y1s[749],y3s[749])}

# ============ Excel ============
wb = Workbook()
HDR_FILL = PatternFill("solid", fgColor="111111")
HL_FILL = PatternFill("solid", fgColor="FFF6D9")
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

ws = wb.active
ws.title = "三价位分位表"
ws["A1"] = "AiKen 销量概率分布 · 三价位对比（v0.4 校准口径）"
ws["A1"].font = Font(name="微软雅黑", size=13, bold=True)
ws["A2"] = "先验与 prototype_v04 一致（m: lognormal P50=11万 σ=0.85；预算 80/155/240万·6个月；CPM 38/45/65；CTR 1.8/2.3/3.0%；CVR 0.9/1.4/2.2%）· 弹性-1.5：699→×0.80，749→×0.72 · BOM：599/250、699/250、749/280"
ws["A2"].font = S_FONT

QUANTILES = [5, 10, 25, 50, 75, 90, 95]
r = 4
ws.cell(row=r, column=1, value="【首年销量分布 · 万台】").font = B_FONT; r += 1
for j, h in enumerate(["分位", "¥599", "¥699", "¥749"], 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
for qn in QUANTILES:
    ws.cell(row=r, column=1, value=f"P{qn}")
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=round(pct(y1s[p], qn) / 1e4, 2))
    style_row(ws, r, range(1, 5))
    if qn == 50:
        for j in range(1, 5): ws.cell(row=r, column=j).font = B_FONT
    r += 1

r += 1
ws.cell(row=r, column=1, value="【三年累计销量分布 · 万台】").font = B_FONT; r += 1
for j, h in enumerate(["分位", "¥599", "¥699", "¥749"], 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
for qn in QUANTILES:
    ws.cell(row=r, column=1, value=f"P{qn}")
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=round(pct(y3s[p], qn) / 1e4, 2))
    style_row(ws, r, range(1, 5))
    if qn == 50:
        for j in range(1, 5): ws.cell(row=r, column=j).font = B_FONT
    r += 1

r += 1
ws.cell(row=r, column=1, value="【关键概率 · 首年】").font = B_FONT; r += 1
for j, h in enumerate(["事件", "¥599", "¥699", "¥749"], 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
for label, th in [("P(≥2.2万 · v0.4 Normal)", 22_000), ("P(≥3.21万 · v0.4 Best)", 32_139)]:
    ws.cell(row=r, column=1, value=label)
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=f"{prob(y1s[p], th)*100:.0f}%")
    style_row(ws, r, range(1, 5)); r += 1

r += 1
ws.cell(row=r, column=1, value="【财务对比】渠道25% + 销售费用8% · NRE 630万").font = B_FONT; r += 1
for j, h in enumerate(["指标", "¥599 (BOM250)", "¥699 (BOM250)", "¥749 (BOM280)"], 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
fin_rows = [
    ("单台净贡献（元）", lambda f: round(f["unit"])),
    ("首年净贡献 P50（万元）", lambda f: round(f["cm1"] / 1e4)),
    ("三年累计净贡献 P50（万元）", lambda f: round(f["cm3"] / 1e4)),
    ("三年收入 P50（亿元）", lambda f: round(f["rev3"] / 1e8, 2)),
    ("P(三年累计转正)", lambda f: f"{round(f['pt']*100)}%"),
    ("P(首年NRE覆盖≥60%)", lambda f: f"{round(f['pn']*100)}%"),
]
for label, fn in fin_rows:
    ws.cell(row=r, column=1, value=label)
    for j, key in enumerate([(599,250), (699,250), (749,280)], 2):
        ws.cell(row=r, column=j, value=fn(FIN[key]))
    style_row(ws, r, range(1, 5)); r += 1

for col, w_ in zip("ABCD", [30, 15, 15, 15]):
    ws.column_dimensions[col].width = w_

# Sheet2 敏感性
ws2 = wb.create_sheet("弹性与BOM敏感性")
ws2["A1"] = "敏感性：转化弹性（-1.0 / -1.5 主口径 / -1.8）与 699 BOM（250/280）"
ws2["A1"].font = Font(name="微软雅黑", size=13, bold=True)
r = 3
for j, h in enumerate(["情景", "首年P50(万)", "三年P50(万)", "备注"], 1):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
rows_sens = [
    ("¥699 弹性-1.0（CVR×0.86）", *sens[(699, -1.0)], "刚性：涨价几乎不伤转化"),
    ("¥699 弹性-1.5（主口径 CVR×0.80）", y1s[699], y3s[699], "主口径"),
    ("¥699 弹性-1.8（CVR×0.75）", *sens[(699, -1.8)], "保守"),
    ("¥749 弹性-1.0（CVR×0.80）", *sens[(749, -1.0)], "刚性"),
    ("¥749 弹性-1.5（主口径 CVR×0.72）", y1s[749], y3s[749], "主口径"),
    ("¥749 弹性-1.8（CVR×0.66）", *sens[(749, -1.8)], "保守"),
]
for label, a, b, note in rows_sens:
    ws2.cell(row=r, column=1, value=label)
    ws2.cell(row=r, column=2, value=round(pct(a, 50) / 1e4, 2))
    ws2.cell(row=r, column=3, value=round(pct(b, 50) / 1e4, 2))
    ws2.cell(row=r, column=4, value=note)
    style_row(ws2, r, range(1, 5))
    if "主口径" in label:
        for j in range(1, 5): ws2.cell(row=r, column=j).fill = HL_FILL
    r += 1

r += 1
ws2.cell(row=r, column=1, value="699 的 BOM 敏感性（弹性 -1.5）").font = B_FONT; r += 1
for j, h in enumerate(["BOM", "单台净贡献(元)", "P(三年转正)", "P(首年NRE≥60%)"], 1):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(1, 5), HDR_FONT, HDR_FILL); r += 1
for bom in (250, 280):
    f = FIN[(699, bom)]
    ws2.cell(row=r, column=1, value=bom)
    ws2.cell(row=r, column=2, value=round(f["unit"]))
    ws2.cell(row=r, column=3, value=f"{round(f['pt']*100)}%")
    ws2.cell(row=r, column=4, value=f"{round(f['pn']*100)}%")
    style_row(ws2, r, range(1, 5)); r += 1

for col, w_ in zip("ABCD", [34, 14, 14, 26]):
    ws2.column_dimensions[col].width = w_

XLSX = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen三价位销量概率分布_分位表.xlsx"
wb.save(XLSX)
print("Excel saved (v0.4 口径)")

# ============ HTML ============
COLORS = {599: "#111111", 699: "#00A5A5", 749: "#EC008C"}

def overlay_hist(data_dict, w=560, h=212, nbins=46, vmax=55_000, xticks=None, ymax_adj=1.28):
    ml, mr, mt, mb = 44, 14, 22, 38
    x0, x1_ = ml, w - mr; y0, y1p = h - mb, mt
    P = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei">']
    for gy in np.linspace(y0, y1p, 4):
        P.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1_}" y2="{gy:.0f}" stroke="#F0F0F0" stroke-width="1"/>')
    hists = {p: np.histogram(dd, bins=nbins, range=(0, vmax))[0] for p, dd in data_dict.items()}
    cmax_all = max(h.max() for h in hists.values())
    bw = (x1_ - x0) / nbins
    for price, counts in hists.items():
        for i, c in enumerate(counts):
            bh = (c / cmax_all) * (y0 - y1p) / ymax_adj
            if bh <= 0.5: continue
            P.append(f'<rect x="{x0+i*bw:.1f}" y="{y0-bh:.1f}" width="{bw*0.94:.1f}" height="{bh:.1f}" fill="{COLORS[price]}" fill-opacity="0.30" rx="1"/>')
    for price, data in data_dict.items():
        v = pct(data, 50)
        sx = x0 + (min(v, vmax) / vmax) * (x1_ - x0)
        P.append(f'<line x1="{sx:.1f}" y1="{y1p}" x2="{sx:.1f}" y2="{y0}" stroke="{COLORS[price]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        P.append(f'<text x="{sx:.1f}" y="{y0+15}" text-anchor="middle" font-size="10.5" fill="{COLORS[price]}" font-weight="bold">{W(v)}万</text>')
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
    for price, label in [(599, "¥599（BOM 250）"), (699, "¥699（BOM 250）"), (749, "¥749（BOM 280）")]:
        P.append(f'<rect x="{lx}" y="9" width="24" height="10" rx="2" fill="{COLORS[price]}" fill-opacity="0.45"/>')
        P.append(f'<line x1="{lx}" y1="24" x2="{lx+24}" y2="24" stroke="{COLORS[price]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        P.append(f'<text x="{lx+30}" y="18" font-size="10.5" fill="#333">{label}</text>')
        lx += 30 + len(label) * 11.5 + 26
    P.append(f'<text x="{w-6}" y="18" text-anchor="end" font-size="9.5" fill="#9a9a9a">虚线 = P50</text>')
    P.append('</svg>')
    return "".join(P)

SVG_Y1 = overlay_hist(y1s, vmax=55_000, xticks=[(0,"0"),(1.4e4,"1.4万"),(2.2e4,"2.2万"),(3.2e4,"3.2万"),(4.4e4,"4.4万"),(5.5e4,"5.5万")])
SVG_Y3 = overlay_hist(y3s, vmax=140_000, xticks=[(0,"0"),(3.5e4,"3.5万"),(6.3e4,"6.3万"),(1e5,"10万"),(1.4e5,"14万")])
SVG_LEG = legend_svg()

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AiKen 销量概率分布 · 三价位对比（v0.4 口径）</title>
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
    <div class="tag">v0.4 校准口径 · ¥599 / ¥699 / ¥749</div>
  </div>

  <div class="note">
    先验与 v0.4 一致（市场部数据校准后）：m P50=11万 σ=0.85 ｜ 媒介预算 80–240万（P50=155万/6个月）｜ CPM 38/45/65 ｜ CTR 1.8/2.3/3.0%（S1 实测 2.14%）｜ CVR 0.9/1.4/2.2%（S1 0.98%+回测余量）。涨价走 <b>CVR 通道</b>（弹性 −1.5 主口径）：¥699→×0.80，¥749→×0.72；预算与 CPM/CTR 不变。<b>BOM</b>：599→250 ｜ 699→250 ｜ 749→280。弹性/BOM 敏感性见 Excel 第二页。
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
      <tr><td>P(首年≥2.2万 · v0.4 Normal)</td><td class="c599">{prob(y1s[599],22000)*100:.0f}%</td><td class="c699">{prob(y1s[699],22000)*100:.0f}%</td><td class="c749">{prob(y1s[749],22000)*100:.0f}%</td></tr>
      <tr><td>P(首年≥3.21万 · v0.4 Best)</td><td class="c599">{prob(y1s[599],32139)*100:.0f}%</td><td class="c699">{prob(y1s[699],32139)*100:.0f}%</td><td class="c749">{prob(y1s[749],32139)*100:.0f}%</td></tr>
      <tr><td>单台净贡献（渠道25%+销8%）</td><td class="c599">{FIN[(599,250)]['unit']:.0f} 元</td><td class="c699">{FIN[(699,250)]['unit']:.0f} 元</td><td class="c749">{FIN[(749,280)]['unit']:.0f} 元</td></tr>
      <tr><td>三年累计净贡献 P50</td><td class="c599">{FIN[(599,250)]['cm3']/1e4:.0f} 万</td><td class="c699">{FIN[(699,250)]['cm3']/1e4:.0f} 万</td><td class="c749">{FIN[(749,280)]['cm3']/1e4:.0f} 万</td></tr>
      <tr><td>P(三年累计转正)</td><td class="c599">{FIN[(599,250)]['pt']*100:.0f}%</td><td class="c699">{FIN[(699,250)]['pt']*100:.0f}%</td><td class="c749">{FIN[(749,280)]['pt']*100:.0f}%</td></tr>
    </table>
  </div>

  <div class="ft">
    <span>模型：RCF + Bass + 蒙特卡洛（种子 20261022）· v0.4 校准口径（S1 漏斗实测 + 市场部预算区间）</span>
    <span>配套：AiKen三价位销量概率分布_分位表.xlsx（含弹性/BOM 敏感性）</span>
  </div>

</div></div>
</body>
</html>
"""

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen三价位销量概率分布对比页.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("HTML saved (v0.4 口径)")
