# -*- coding: utf-8 -*-
"""生成 AiKen 销量概率分布读数表 Excel（首年 + 三年，P5-P95 分位表 + 关键概率 + 读图说明）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ===== 载入 v0.2 模拟结果 =====
d = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v02_results.npz")
y1 = d["y1"]   # 首年销量
y3 = d["y3"]   # 三年累计
N = len(y1)

pct = lambda a, q: float(np.percentile(a, q))
prob_ge = lambda a, th: float((a >= th).mean())

# ===== 样式定义 =====
F_TITLE  = Font(name="Microsoft YaHei", size=14, bold=True, color="111111")
F_SUB    = Font(name="Microsoft YaHei", size=10, color="6B6B6B")
F_HDR    = Font(name="Microsoft YaHei", size=10.5, bold=True, color="FFFFFF")
F_BODY   = Font(name="Microsoft YaHei", size=10.5, color="111111")
F_BODY_B = Font(name="Microsoft YaHei", size=10.5, bold=True, color="111111")
F_KEY    = Font(name="Microsoft YaHei", size=10.5, bold=True, color="EC008C")
F_NOTE   = Font(name="Microsoft YaHei", size=9.5, color="6B6B6B")
F_SEC    = Font(name="Microsoft YaHei", size=12, bold=True, color="EC008C")

FILL_HDR  = PatternFill("solid", fgColor="111111")
FILL_KEY  = PatternFill("solid", fgColor="FDF3F8")
FILL_ALT  = PatternFill("solid", fgColor="F7F7F7")
FILL_SCN  = PatternFill("solid", fgColor="FFF7E6")   # 场景锚行

THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT   = Alignment(horizontal="left", vertical="center", wrap_text=True)

wb = Workbook()

# ============================================================
# Sheet 1: 读图说明
# ============================================================
ws = wb.active
ws.title = "读图说明"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 22
ws.column_dimensions["C"].width = 86

ws["B2"] = "AiKen 销量概率分布 · 读数表"
ws["B2"].font = F_TITLE
ws["B3"] = "模型 v0.2 · 8,000 次蒙特卡洛 · 参数：参照类已校准，漏斗为行业通带占位（待市场部数据校准）"
ws["B3"].font = F_SUB

rows = [
    ("这个分布是什么？",
     "8,000 次模拟得到的「首年（或三年累计）销量」的全集。每次模拟 = 从参照类先验区间随机抽一组 (m·p·q) 跑一条 Bass 曲线。"
     "它不是正态分布——右尾更长（小概率卖出非常多），形状类似对数正态。"),
    ("横轴 / 纵轴各是什么？",
     "横轴 = 销量（台）；纵轴 = 概率密度（落在这个销量区间的模拟次数占比）。曲线下总面积 = 100%。"),
    ("P5 / P50 / P95 是什么？",
     "分位数。P50 = 中位数：一半的模拟结果比它高、一半比它低（最可能的单点读数）。"
     "P5 = 只有 5% 的模拟比它更差（悲观边界）；P95 = 只有 5% 的模拟比它更好（乐观边界）。"
     "P5–P95 之间覆盖了 90% 的可能性，即「大概率区间」。"),
    ("怎么读「达到某销量对应多少概率」？",
     "两种读法：① 找分位表中第一个 ≥ 该销量的行，其概率列即答案（近似）；② 直接查「关键概率」表——"
     "如 P(首年 ≥ 3.6万) 表示 8,000 次模拟中销量 ≥ 36,000 台的次数占比。"
     "注意：分位表给的是「多少分位对应多少销量」，关键概率表给的是「多少销量对应多少概率」，两者互为反查。"),
    ("和三档场景（Worst/Normal/Best）什么关系？",
     "三档场景 = 分布上的分位锚，不是预测点：Worst（月销500→年6000）≈ P1 以下；Normal（月销1000→年1.2万）≈ P1；"
     "Best（月销3000→年3.6万）≈ P75。三档供供应链与财务执行使用；全分布才是决策工具（详见方法论说明页）。"),
    ("为什么首年 P50（2.86万）比会议 Normal（1.2万）高？",
     "主要差异来自媒介预算假设：模型按上市前 6 个月 120–280 万投放测算（P50≈202万），"
     "而会议 Normal 按 2% 销售费用折算全年仅约 14 万。校准会已确认 2% 不够——预算口径待市场部确认后重跑 v0.3。"),
    ("读数示例",
     "「首年销量 P50 = 28,600 台」→ 一半的可能性卖得比它多；"
     "「P(首年 ≥ 36,000) = 25.8%」→ 约四分之一的概率达到 Best 档；"
     "「三年累计 P95 = 158,000 台」→ 20 次里约有 1 次三年卖过 15.8 万台。"),
]
r = 5
for q, a in rows:
    ws.cell(row=r, column=2, value=q).font = F_BODY_B
    ws.cell(row=r, column=2).alignment = LEFT
    ws.cell(row=r, column=2).fill = FILL_ALT
    c = ws.cell(row=r, column=3, value=a)
    c.font = F_BODY
    c.alignment = LEFT
    for col in (2, 3):
        ws.cell(row=r, column=col).border = BORDER
    ws.row_dimensions[r].height = max(30, 15 * (len(a) // 42 + 1))
    r += 1

# ============================================================
# Sheet 2: 分位表（首年 + 三年）
# ============================================================
ws2 = wb.create_sheet("分位表")
ws2.sheet_view.showGridLines = False
widths = {"A": 4, "B": 10, "C": 15, "D": 15, "E": 13, "F": 15, "G": 15, "H": 13, "I": 30}
for col, w in widths.items():
    ws2.column_dimensions[col].width = w

ws2["B2"] = "销量分位表 · 首年 & 三年累计"
ws2["B2"].font = F_TITLE
ws2["B3"] = "读法：如「首年 P50 = 28,600」表示 50% 的模拟结果首年销量低于 28,600 台。淡黄行 = 会议三档场景锚。"
ws2["B3"].font = F_SUB

headers = ["分位 P(x)", "首年销量（台）", "首年销量（万台）", "首年 ≥ 该销量的概率", "三年累计（台）", "三年累计（万台）", "三年 ≥ 该销量的概率", "备注"]
for i, h in enumerate(headers):
    c = ws2.cell(row=5, column=2 + i, value=h)
    c.font = F_HDR; c.fill = FILL_HDR; c.alignment = CENTER; c.border = BORDER

qs = list(range(5, 100, 5))  # P5, P10, ..., P95
# 场景锚（首年口径）
scn_map = {}
for p in qs:
    v = pct(y1, p)
    if v >= 6000 and "worst" not in scn_map and pct(y1, 5) <= 6000:
        pass
# 手动判断锚行
y1_6000, y1_12000, y1_36000 = 6000, 12000, 36000
worst_p = prob_ge(y1, y1_6000)     # P(≥6000)
normal_p = prob_ge(y1, y1_12000)
best_p = prob_ge(y1, y1_36000)

for i, p in enumerate(qs):
    r = 6 + i
    v1 = pct(y1, p); v3 = pct(y3, p)
    p1_ge = prob_ge(y1, v1); p3_ge = prob_ge(y3, v3)
    vals = [f"P{p}", int(round(v1)), round(v1 / 10000, 2), f"{p1_ge*100:.1f}%",
            int(round(v3)), round(v3 / 10000, 2), f"{p3_ge*100:.1f}%", ""]
    note = ""
    is_anchor = False
    if p == 5 and v1 <= 12000:
        note = "Worst（年6000）在此之下"
    if 10 <= p <= 20 and abs(v1 - 12000) == min(abs(pct(y1, q) - 12000) for q in qs):
        note = "≈ Normal（年1.2万）"
        is_anchor = True
    if 70 <= p <= 80 and abs(v1 - 36000) == min(abs(pct(y1, q) - 36000) for q in qs):
        note = "≈ Best（年3.6万）"
        is_anchor = True
    vals[7] = note
    for j, v in enumerate(vals):
        c = ws2.cell(row=r, column=2 + j, value=v)
        c.font = F_KEY if is_anchor else F_BODY
        c.alignment = CENTER if j != 7 else LEFT
        c.border = BORDER
        if is_anchor:
            c.fill = FILL_SCN
        elif i % 2 == 1:
            c.fill = FILL_ALT

r = 6 + len(qs) + 1
ws2.cell(row=r, column=2, value="关键概率读数").font = F_SEC
kr = r + 1
for i, h in enumerate(["问法", "首年", "三年累计"]):
    c = ws2.cell(row=kr, column=2 + i, value=h)
    c.font = F_HDR; c.fill = FILL_HDR; c.alignment = CENTER; c.border = BORDER
key_rows = [
    ("P(≥ 6,000 台)  — Worst 场景线", prob_ge(y1, 6000), prob_ge(y3, 6000)),
    ("P(≥ 12,000 台) — Normal 场景线", prob_ge(y1, 12000), prob_ge(y3, 12000)),
    ("P(≥ 36,000 台) — Best 场景线", prob_ge(y1, 36000), prob_ge(y3, 36000)),
    ("P(≥ 50,000 台)", prob_ge(y1, 50000), prob_ge(y3, 50000)),
    ("P(≥ 100,000 台) — 十万台线", prob_ge(y1, 100000), prob_ge(y3, 100000)),
    ("P(≥ 200,000 台)", prob_ge(y1, 200000), prob_ge(y3, 200000)),
]
for i, (label, p1, p3) in enumerate(key_rows):
    rr = kr + 1 + i
    c = ws2.cell(row=rr, column=2, value=label); c.font = F_BODY; c.alignment = LEFT; c.border = BORDER
    for j, pv in enumerate([p1, p3]):
        c = ws2.cell(row=rr, column=3 + j, value=f"{pv*100:.1f}%")
        c.font = F_KEY if "场景线" in label else F_BODY
        c.alignment = CENTER; c.border = BORDER
    if i % 2 == 1:
        for col in range(2, 5):
            ws2.cell(row=rr, column=col).fill = FILL_ALT

note_r = kr + len(key_rows) + 2
ws2.cell(row=note_r, column=2, value="注：本表由 v0.2 模拟结果（v02_results.npz）直接计算生成；v0.3 校准后数字将更新。").font = F_NOTE

# ============================================================
# Sheet 3: 直方图数据（首年 & 三年）
# ============================================================
ws3 = wb.create_sheet("直方图数据")
ws3.sheet_view.showGridLines = False
for col, w in {"A": 4, "B": 20, "C": 14, "D": 14, "E": 20, "F": 14, "G": 14}.items():
    ws3.column_dimensions[col].width = w

ws3["B2"] = "直方图原始数据（可选中后插入 Excel 图表）"
ws3["B2"].font = F_TITLE
ws3["B3"] = "区间为左闭右开；「占比」= 落入该区间的模拟次数 / 8,000。"
ws3["B3"].font = F_SUB

# 首年 bins（与 HTML 图一致：0-8万，44 桶）
bins1 = np.linspace(0, 80_000, 45)
cnt1, _ = np.histogram(y1, bins=bins1)
# 三年 bins（0-20万，40 桶）
bins3 = np.linspace(0, 200_000, 41)
cnt3, _ = np.histogram(y3, bins=bins3)

hdr = ["首年区间下限（台）", "首年区间上限（台）", "首年占比"]
for i, h in enumerate(hdr):
    c = ws3.cell(row=5, column=2 + i, value=h)
    c.font = F_HDR; c.fill = FILL_HDR; c.alignment = CENTER; c.border = BORDER
for i in range(44):
    r = 6 + i
    lo, hi, ct = int(bins1[i]), int(bins1[i+1]), cnt1[i]
    for j, v in enumerate([lo, hi, ct / N]):
        c = ws3.cell(row=r, column=2 + j, value=v)
        c.font = F_BODY; c.alignment = CENTER; c.border = BORDER
        if j == 2:
            c.number_format = "0.00%"

base_r = 6 + 44 + 2
hdr3 = ["三年区间下限（台）", "三年区间上限（台）", "三年占比"]
for i, h in enumerate(hdr3):
    c = ws3.cell(row=base_r, column=2 + i, value=h)
    c.font = F_HDR; c.fill = FILL_HDR; c.alignment = CENTER; c.border = BORDER
for i in range(40):
    r = base_r + 1 + i
    lo, hi, ct = int(bins3[i]), int(bins3[i+1]), cnt3[i]
    for j, v in enumerate([lo, hi, ct / N]):
        c = ws3.cell(row=r, column=2 + j, value=v)
        c.font = F_BODY; c.alignment = CENTER; c.border = BORDER
        if j == 2:
            c.number_format = "0.00%"

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率分布_读数表.xlsx"
wb.save(OUT)
print("saved:", OUT)
print(f"y1 P5={pct(y1,5):.0f} P50={pct(y1,50):.0f} P95={pct(y1,95):.0f}")
print(f"y3 P5={pct(y3,5):.0f} P50={pct(y3,50):.0f} P95={pct(y3,95):.0f}")
print(f"key: P(y1>=36000)={prob_ge(y1,36000)*100:.1f}%  P(y3>=100000)={prob_ge(y3,100000)*100:.1f}%")
print(f"anchors: worst6000<=P{np.searchsorted(np.sort(y1),6000)/N*100:.0f} normal12000=P{np.searchsorted(np.sort(y1),12000)/N*100:.0f} best36000=P{np.searchsorted(np.sort(y1),36000)/N*100:.0f}")
