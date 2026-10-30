# -*- coding: utf-8 -*-
"""
AiKen 销量概率分布 · 三价位对比版（599 / 699 / 749）
====================================================
产出：
  1. HTML 对比页：首年 + 三年销量概率分布（三价位同图分色）
  2. Excel 分位表：三价位 × 完整分位 + 敏感性对照

模型口径：
  - 基线与 v0.2 完全一致（同种子）
  - 涨价的销量影响走 CVR 通道（恒定弹性约 -1.5，PSM 证据中档）：
      699 → CVR × 0.80；749 → CVR × 0.72
  - BOM：599→250；749→280（委托假设）；699 主口径 250（附 280 敏感性）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ============ 基线（v0.2 同种子） ============
rng = np.random.default_rng(20261022)
N_SIM = 8000
T_MONTHS = 36

m_prior = rng.lognormal(mean=np.log(120_000), sigma=0.90, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B_budget = rng.uniform(120, 280, size=N_SIM) * 10_000
CPM = rng.triangular(45, 60, 75, size=N_SIM)
CTR = rng.triangular(0.015, 0.022, 0.035, size=N_SIM)
CVR0 = rng.triangular(0.012, 0.018, 0.028, size=N_SIM)   # 599 基线 CVR
exposure = B_budget / CPM * 1000
clicks = exposure * CTR

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

t_year = np.arange(1, T_MONTHS + 1) / 12.0

def run_scenario(cvr_mult):
    cvr = np.clip(CVR0 * cvr_mult, 0.005, 0.03)
    s6 = np.minimum(clicks * cvr, m_prior * 0.55)
    p = solve_p(m_prior, q_prior, s6)
    paths = bass_cum_year(m_prior[:, None], p[:, None], q_prior[:, None], t_year[None, :])
    return paths[:, 11], paths[:, 35]

# 三价位（弹性 -1.5 通道）
y1_599, y3_599 = run_scenario(1.00)
y1_699, y3_699 = run_scenario(0.80)
y1_749, y3_749 = run_scenario(0.72)

# 敏感性：弹性更低（-1.0 恒刚性 / -1.8 保守）
def run_elasticity(price, elast):
    cvr_mult = (price / 599.0) ** elast
    return run_scenario(cvr_mult)

sens = {}
for price, elast in [(699, -1.0), (699, -1.8), (749, -1.0), (749, -1.8)]:
    sens[(price, elast)] = run_elasticity(price, elast)

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())
W = lambda v: f"{v/1e4:.2f}"

# ============ 财务 ============
CH, SR, NRE = 0.25, 0.08, 6_300_000
def fin(price, bom, y1, y3):
    unit = price * (1 - CH - SR) - bom
    cm1, cm3 = y1 * unit, y3 * unit
    return dict(unit=unit,
                cm1_p50=pct(cm1, 50), cm3_p50=pct(cm3, 50),
                p_turn3=prob(cm3 - NRE, 0), p_nre60=prob(cm1, 0.60 * NRE),
                rev3_p50=pct(y3 * price, 50))

FIN = {
    599: fin(599, 250, y1_599, y3_599),
    699: fin(699, 250, y1_699, y3_699),
    749: fin(749, 280, y1_749, y3_749),
}

# ============ Excel ============
wb = Workbook()

HDR_FILL = PatternFill("solid", fgColor="111111")
SUB_FILL = PatternFill("solid", fgColor="FDF3F8")
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

# ---- Sheet1 主分位表 ----
ws = wb.active
ws.title = "三价位分位表"
ws["A1"] = "AiKen 销量概率分布 · 三价位对比（弹性 -1.5 主口径）"
ws["A1"].font = Font(name="微软雅黑", size=13, bold=True)
ws["A2"] = "种子 20261022 · 8000 次蒙特卡洛 · 涨价影响走 CVR 通道（699→×0.80，749→×0.72）· BOM：599/250、699/250、749/280"
ws["A2"].font = S_FONT

QUANTILES = [5, 10, 25, 50, 75, 90, 95]

r = 4
ws.cell(row=r, column=1, value="【首年销量分布 · 万台】").font = B_FONT
r += 1
headers = ["分位"] + [f"¥{p}" for p in (599, 699, 749)]
for j, h in enumerate(headers, 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
y1s = {599: y1_599, 699: y1_699, 749: y1_749}
for qn in QUANTILES:
    ws.cell(row=r, column=1, value=f"P{qn}")
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=round(pct(y1s[p], qn) / 1e4, 2))
    style_row(ws, r, range(1, 5))
    if qn == 50:
        for j in range(2, 5): ws.cell(row=r, column=j).font = B_FONT
        ws.cell(row=r, column=1).font = B_FONT
    r += 1

r += 1
ws.cell(row=r, column=1, value="【三年累计销量分布 · 万台】").font = B_FONT
r += 1
for j, h in enumerate(headers, 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
y3s = {599: y3_599, 699: y3_699, 749: y3_749}
for qn in QUANTILES:
    ws.cell(row=r, column=1, value=f"P{qn}")
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=round(pct(y3s[p], qn) / 1e4, 2))
    style_row(ws, r, range(1, 5))
    if qn == 50:
        for j in range(2, 5): ws.cell(row=r, column=j).font = B_FONT
        ws.cell(row=r, column=1).font = B_FONT
    r += 1

r += 1
ws.cell(row=r, column=1, value="【关键概率 · 首年】").font = B_FONT
r += 1
for j, h in enumerate(["事件"] + [f"¥{p}" for p in (599, 699, 749)], 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
for label, th in [("P(≥1.2万 · 会议Normal)", 12_000), ("P(≥3.6万 · 会议Best)", 36_000)]:
    ws.cell(row=r, column=1, value=label)
    for j, p in enumerate((599, 699, 749), 2):
        ws.cell(row=r, column=j, value=round(prob(y1s[p], th) * 100, 1))
    style_row(ws, r, range(1, 5))
    r += 1

r += 1
ws.cell(row=r, column=1, value="【财务对比】渠道25% + 销售费用8% · NRE 630万").font = B_FONT
r += 1
fin_headers = ["指标"] + [f"¥{p}" for p in (599, 699, 749)]
for j, h in enumerate(fin_headers, 1):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
fin_rows = [
    ("单台净贡献（元）", lambda f: round(f["unit"])),
    ("首年净贡献 P50（万元）", lambda f: round(f["cm1_p50"] / 1e4)),
    ("三年累计净贡献 P50（万元）", lambda f: round(f["cm3_p50"] / 1e4)),
    ("三年收入 P50（亿元）", lambda f: round(f["rev3_p50"] / 1e8, 2)),
    ("P(三年累计转正)", lambda f: round(f["p_turn3"] * 100)),
    ("P(首年NRE覆盖≥60%)", lambda f: round(f["p_nre60"] * 100)),
]
for label, fn in fin_rows:
    ws.cell(row=r, column=1, value=label)
    for j, p in enumerate((599, 699, 749), 2):
        v = fn(FIN[p])
        ws.cell(row=r, column=j, value=v if not label.startswith("P(") else f"{v}%")
    style_row(ws, r, range(1, 5))
    r += 1

for col, w_ in zip("ABCD", [30, 13, 13, 13]):
    ws.column_dimensions[col].width = w_

# ---- Sheet2 敏感性 ----
ws2 = wb.create_sheet("弹性与BOM敏感性")
ws2["A1"] = "敏感性分析：转化弹性与 699 BOM"
ws2["A1"].font = Font(name="微软雅黑", size=13, bold=True)
ws2["A2"] = "主口径弹性 -1.5；下表给 -1.0（刚性，涨价几乎不伤转化）与 -1.8（保守）对照；699 的 BOM 给 250/280 两种"
ws2["A2"].font = S_FONT

r = 4
for j, h in enumerate(["情景", "首年P50(万)", "三年P50(万)", "备注"], 1):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
rows_sens = [
    ("¥699 弹性-1.0（CVR×0.86）", *sens[(699, -1.0)], "涨价几乎不影响转化"),
    ("¥699 弹性-1.5（主口径 CVR×0.80）", y1_699, y3_699, "主口径"),
    ("¥699 弹性-1.8（CVR×0.75）", *sens[(699, -1.8)], "保守"),
    ("¥749 弹性-1.0（CVR×0.80）", *sens[(749, -1.0)], "刚性"),
    ("¥749 弹性-1.5（主口径 CVR×0.72）", y1_749, y3_749, "主口径"),
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
ws2.cell(row=r, column=1, value="699 的 BOM 敏感性（弹性 -1.5）").font = B_FONT
r += 1
for j, h in enumerate(["BOM", "单台净贡献(元)", "P(三年转正)", "P(首年NRE≥60%)"], 1):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
for bom in (250, 280):
    f = fin(699, bom, y1_699, y3_699)
    ws2.cell(row=r, column=1, value=bom)
    ws2.cell(row=r, column=2, value=round(f["unit"]))
    ws2.cell(row=r, column=3, value=f"{round(f['p_turn3']*100)}%")
    ws2.cell(row=r, column=4, value=f"{round(f['p_nre60']*100)}%")
    style_row(ws2, r, range(1, 5))
    r += 1

for col, w_ in zip("ABCD", [34, 14, 14, 26]):
    ws2.column_dimensions[col].width = w_

XLSX = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen三价位销量概率分布_分位表.xlsx"
wb.save(XLSX)
print("Excel saved:", XLSX)

# ============ 打印关键数字（供 HTML 与汇报） ============
print("\n=== 首年 P5/P50/P95（万台） ===")
for p in (599, 699, 749):
    print(f"¥{p}: {W(pct(y1s[p],5))} / {W(pct(y1s[p],50))} / {W(pct(y1s[p],95))}")
print("\n=== 三年 P5/P50/P95（万台） ===")
for p in (599, 699, 749):
    print(f"¥{p}: {W(pct(y3s[p],5))} / {W(pct(y3s[p],50))} / {W(pct(y3s[p],95))}")
print("\n=== 财务 ===")
for p in (599, 699, 749):
    f = FIN[p]
    print(f"¥{p}: 单台{f['unit']:.0f}元 三年贡献P50 {f['cm3_p50']/1e4:.0f}万 P(三年转正){f['p_turn3']*100:.0f}% P(NRE60){f['p_nre60']*100:.0f}%")

# 保存数组供 HTML 生成
np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\price3_results.npz",
         y1_599=y1_599, y1_699=y1_699, y1_749=y1_749,
         y3_599=y3_599, y3_699=y3_699, y3_749=y3_749)
print("\n[npz saved]")
