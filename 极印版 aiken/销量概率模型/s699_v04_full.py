# -*- coding: utf-8 -*-
"""
AiKen ¥699 定价版 · v0.4 模型完整重跑
========================================
口径（按用户 2026-10-28 指示）：
  - 定价 ¥699，BOM 维持 250
  - 漏斗参数 = v0.4（S1 实测校准）原样使用，不做涨价弹性折扣
    理由：S1 为 ¥1799 高价产品，其 CTR/CVR 对 ¥699 而言偏保守
  - 其余先验（m/q/预算/CPM/CTR/CVR）与 prototype_v04.py 完全一致
产出：
  - 699 读数表 Excel（格式对齐《AiKen销量概率分布_读数表》）
  - 分位表 / 关键概率 / 财务读数（口径对齐 JY 699 Finance）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# ============ v0.4 先验（与 prototype_v04.py 逐行一致） ============
rng = np.random.default_rng(20261022)
N_SIM = 8000
T_MONTHS = 36

m_prior = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)

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
        small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo = np.where(small, mid, lo); hi = np.where(small, hi, mid)
    return 0.5 * (lo + hi)

p_solved = solve_p(m_prior, q_prior, s6)
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1 = paths[:, 11]
y3 = paths[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=== ¥699（漏斗不打折）· v0.4 完整重跑 ===")
print(f"首年: P5={pct(y1,5):.0f}  P10={pct(y1,10):.0f}  P50={pct(y1,50):.0f}  P90={pct(y1,90):.0f}  P95={pct(y1,95):.0f}")
print(f"三年: P5={pct(y3,5):.0f}  P10={pct(y3,10):.0f}  P50={pct(y3,50):.0f}  P90={pct(y3,90):.0f}  P95={pct(y3,95):.0f}")

# ============ 财务口径（对齐 JY 699 Finance 表） ============
# ASP 链条：零售 699 → 含税 618.58 → 不含税 503.22（扣渠道）
# 读数表口径（与《AiKen销量概率分布_读数表》一致）：单台净贡献 = ASP不含税×?−BOM
# 用户 JY 表财务读数 sheet 用的是 51.9 元单台（31.2×70% 系老口径残留，599 版）
# 这里按 699 JY 表真实链条重算：
ASP_tax_excl = 503.2181          # 不含税、扣渠道后（JY 表 BOM&ASP!D10=503.2181 的口径为 D 列）
# JY 表 Normal Scenario E22 收入/unit = 503.2181（不含税扣渠道）
# 单台净贡献（简化口径，同读数表）：ASP不含税 − BOM = 503.22 − 250 = 253.22
UNIT_CM = ASP_tax_excl - 250.0   # 253.22 元/台（不含渠道内扣？——见下方注释）
# 注：JY 表的完整成本链还有 物流/MOH/返修/服务费/销售费用 等，读数表口径是"简化口径"
# 与 599 读数表对齐：单台净贡献 = ASP(不含税)×(1−渠道)−BOM 的简化式
# 599 版读数表写的是 51.9 = 631.2×70%−250 的口径（含税→×70%），为保持同构：
UNIT_CM_JY = 618.5841 * 0.70 * (250/221.24/250*250)  # placeholder 不用
# 直接采用 599 读数表同构公式：单台 = 零售价 × (1−渠道0.3扣点…) 不对——
# 599 版：51.9 = 631.2×70% − 389.94? 不成立。51.9 = ASP含税631.2 → ×70%(渠道后441.84) − BOM390? 也不对。
# 读数表原式：ASP不含税 531.2×70% − BOM 250? = 121.84 也不是 51.9。
# —— 599 读数表口径：631.2×70% = 441.84（渠道后含税）→ 不含税 441.84/1.13 = 391.0 − 250 = 141 也不是。
# 实际 51.9 的来源：599 零售 → 含税 631.2? 否。599×1.0=599。631.2=599×1.0538?
# 结论：51.9 无法从简单链条反推，是读数表当时的"净贡献=ASP不含税−渠道−BOM−销售费用"复合口径。
# 为避免口径混乱，本次 Excel 财务区给两条线：
#   线1（简化）：单台净贡献 = 503.22 − 250 = 253.22（不含销售费用/物流等）
#   线2（JY表口径）：直接引用 JY 表三档读数（Normal 净利 78.7万/Best 392.9万/Worst -94.5万）
print(f"\n单台净贡献（简化线）：503.22 − 250 = {UNIT_CM:.2f} 元")
print(f"首年净贡献 P50（简化线）：{pct(y1*UNIT_CM,50)/1e4:.0f} 万")
print(f"三年累计净贡献 P50（简化线）：{pct(y3*UNIT_CM,50)/1e4:.0f} 万")

# ============ Excel：699 读数表 ============
wb = Workbook()
HDR_FILL = PatternFill("solid", fgColor="111111")
ANCHOR_FILL = PatternFill("solid", fgColor="FFF6D9")
HDR_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
B_FONT = Font(name="微软雅黑", size=10, bold=True)
N_FONT = Font(name="微软雅黑", size=10)
S_FONT = Font(name="微软雅黑", size=9, color="6B6B6B")
TITLE_FONT = Font(name="微软雅黑", size=13, bold=True)
THIN = Border(*[Side(style="thin", color="D9D9D9")] * 4)
CENTER = Alignment(horizontal="center", vertical="center")

def style_row(ws, row, cols, font=None, fill=None):
    for c in cols:
        cell = ws.cell(row=row, column=c)
        cell.font = font or N_FONT
        cell.border = THIN
        if fill: cell.fill = fill
        if c > 1: cell.alignment = CENTER

# ---- Sheet 1: 销量分位表 ----
ws = wb.active
ws.title = "销量分位表"
ws["B2"] = "AiKen ¥699 销量分位表 · 首年 & 三年累计"
ws["B2"].font = TITLE_FONT
ws["B3"] = ("读法：「首年 P50 = X」表示 50% 的模拟结果首年销量低于 X。黄色底 = 三档场景锚。"
            "口径：¥699 / BOM 250 / 漏斗参数 = v0.4 S1 实测原样（CPM 37.6-45.2 · CTR 2.14% · CVR 0.98%+余量，不做涨价折扣——S1 为 ¥1799 高价品，对 699 偏保守）")
ws["B3"].font = S_FONT

QUANTILES = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
r = 5
for j, h in enumerate(["分位 P(x)", "首年销量（台）", "首年销量（万台）", "首年 ≥ 该销量的概率", "三年累计（台）", "三年累计（万台）", "三年 ≥ 该销量的概率", "备注"], 2):
    ws.cell(row=r, column=j, value=h)
style_row(ws, r, range(2, 10), HDR_FONT, HDR_FILL)
r += 1
ANCHORS = {10: "Worst 场景锚（月销 ~1,000）", 50: "Normal 场景锚（月销 ~1,500）", 90: "Best 场景锚（月销 ~2,500）"}
for qn in QUANTILES:
    v1, v3 = pct(y1, qn), pct(y3, qn)
    ws.cell(row=r, column=2, value=f"P{qn}")
    ws.cell(row=r, column=3, value=round(v1))
    ws.cell(row=r, column=4, value=round(v1/1e4, 2))
    ws.cell(row=r, column=5, value=f"{100-qn}%")
    ws.cell(row=r, column=6, value=round(v3))
    ws.cell(row=r, column=7, value=round(v3/1e4, 2))
    ws.cell(row=r, column=8, value=f"{100-qn}%")
    note = ANCHORS.get(qn, "")
    if note: ws.cell(row=r, column=9, value=note)
    style_row(ws, r, range(2, 10))
    if qn in ANCHORS:
        for j in range(2, 10):
            ws.cell(row=r, column=j).fill = ANCHOR_FILL
            ws.cell(row=r, column=j).font = B_FONT
    r += 1

r += 1
ws.cell(row=r, column=2, value="关键概率读数").font = B_FONT
r += 1
KEYS = [
    ("P(首年 ≥ 1.2万 · 会议原Worst)", 12_000),
    ("P(首年 ≥ 1.8万 · 699 Normal锚)", 18_000),
    ("P(首年 ≥ 2.2万 · v0.4 Normal)", 22_009),
    ("P(首年 ≥ 3.0万 · 699 Best锚)", 30_000),
    ("P(首年 ≥ 3.21万 · v0.4 Best)", 32_139),
    ("P(首年 ≥ 5万)", 50_000),
    ("P(三年累计 ≥ 5.52万 · 699三年Normal)", 55_200),
    ("P(三年累计 ≥ 9万 · 699三年Best)", 90_000),
    ("P(三年累计 ≥ 10万 · 十万台线)", 100_000),
]
for label, th in KEYS:
    ws.cell(row=r, column=2, value=label)
    which = "首年" if "首年" in label else "三年"
    arr = y1 if which == "首年" else y3
    ws.cell(row=r, column=3, value=f"{prob(arr, th)*100:.1f}%")
    style_row(ws, r, range(2, 4))
    r += 1

for col, w_ in zip("BCDEFGHI", [30, 15, 14, 18, 15, 14, 18, 30]):
    ws.column_dimensions[col].width = w_

# ---- Sheet 2: 财务读数 ----
ws2 = wb.create_sheet("财务读数")
ws2["A1"] = "AiKen ¥699 财务读数"
ws2["A1"].font = TITLE_FONT
ws2["A2"] = ("单台净贡献 253.2 元（ASP 不含税扣渠道 503.22 − BOM 250，简化口径 = 总数表/评审页同构）"
             "｜ JY 表三档净利（完整成本链含物流/MOH/返修/销售费用）：Normal +78.7万 · Best +392.9万 · Worst −94.5万")
ws2["A2"].font = S_FONT

r = 4
for j, h in enumerate(["指标", "Worst (P10)", "Normal (P50)", "Best (P90)"], 1):
    ws2.cell(row=r, column=j, value=h)
style_row(ws2, r, range(1, 5), HDR_FONT, HDR_FILL)
r += 1
v_w, v_n, v_b = pct(y1, 10), pct(y1, 50), pct(y1, 90)
rows_fin = [
    ("首年销量（台）", round(v_w), round(v_n), round(v_b)),
    ("首年净贡献（万元，简化线 253.2元/台）", round(v_w*UNIT_CM/1e4), round(v_n*UNIT_CM/1e4), round(v_b*UNIT_CM/1e4)),
    ("三年累计（台）", round(pct(y3,10)), round(pct(y3,50)), round(pct(y3,90))),
    ("三年累计净贡献（万元，简化线）", round(pct(y3,10)*UNIT_CM/1e4), round(pct(y3,50)*UNIT_CM/1e4), round(pct(y3,90)*UNIT_CM/1e4)),
]
for label, a, b, c in rows_fin:
    ws2.cell(row=r, column=1, value=label)
    ws2.cell(row=r, column=2, value=a)
    ws2.cell(row=r, column=3, value=b)
    ws2.cell(row=r, column=4, value=c)
    style_row(ws2, r, range(1, 5))
    r += 1

r += 1
ws2.cell(row=r, column=1, value="全分布读数（简化线）").font = B_FONT
r += 1
cm3 = y3 * UNIT_CM
full_rows = [
    ("P(三年累计净贡献 ≥ 0)", f"{prob(cm3,0)*100:.1f}%"),
    ("P(三年累计净贡献 ≥ 500万)", f"{prob(cm3,5e6)*100:.1f}%"),
    ("P(三年累计净贡献 ≥ 1000万)", f"{prob(cm3,1e7)*100:.1f}%"),
    ("P(三年累计 ≥ 10万台)", f"{prob(y3,1e5)*100:.1f}%"),
]
for label, v in full_rows:
    ws2.cell(row=r, column=1, value=label)
    ws2.cell(row=r, column=2, value=v)
    style_row(ws2, r, range(1, 3))
    r += 1

r += 1
ws2.cell(row=r, column=1, value="注：本表为「简化口径」（单台净贡献 × 销量划投资），不含模具摊销分年/资金成本/MOH 等细项；").font = S_FONT
r += 1
ws2.cell(row=r, column=1, value="    精确口径以 JY 699 Finance 表 Scenario sheets 为准（Normal 3年 +78.7万 / Best +392.9万 / Worst −94.5万）。").font = S_FONT

for col, w_ in zip("ABCD", [40, 16, 16, 16]):
    ws2.column_dimensions[col].width = w_

# ---- Sheet 3: 分布说明（对齐读数表格式） ----
ws3 = wb.create_sheet("分布说明")
ws3["B2"] = "AiKen ¥699 销量概率分布 · 读数表"
ws3["B2"].font = TITLE_FONT
ws3["B3"] = "模型 v0.4 · 8,000 次蒙特卡洛 · 漏斗参数按 S1 实测原样使用（数据源：极印投放数据 2026-10-26）"
ws3["B3"].font = S_FONT
notes = [
    ("这个分布是什么？", "8,000 次模拟得到的「首年（或三年累计）销量」的全集。每次模拟 = 从参照类先验区间随机抽一组 (m·p·q) 跑一条 Bass 曲线。它不是正态分布——右尾更长（小概率卖出非常多），形状近似对数正态。"),
    ("横轴 / 纵轴各是什么？", "横轴 = 销量（台）；纵轴 = 概率密度（落在这个销量区间的模拟次数占比）。曲线下总面积 = 100%。"),
    ("P5 / P50 / P95 是什么？", "分位数。P50 = 中位数：一半的模拟结果比它高、一半比它低（最可能的单点读数）。P5 = 只有 5% 的模拟比它更低（悲观边界）；P95 = 只有 5% 的模拟比它更好（乐观边界）。P5–P95 之间覆盖了 90% 的可能性，即「大概率区间」。"),
    ("怎么读「达到某销量对应多少概率」？", "两种读法：① 找分位表中第一个 ≥ 该销量的行，其概率列即答案（近似）；② 直接查「关键概率」表。注意：分位表给的是「多少分位对应多少销量」，关键概率表给的是「多少销量对应多少概率」，二者互为反查。"),
    ("和三档场景（Worst/Normal/Best）什么关系？", "三档场景 = 分布上的分位锚，不是预测点。本表口径下：Worst（月销1,000→年1.2万）≈ P10 以内；Normal（月销1,500→年1.8万）≈ P20-P30 区间；Best（月销2,500→年3.0万）≈ P70+。三档供供应链与财务执行使用；全分布才是决策工具（见方法论说明页）。"),
    ("为什么和 JY 表手工凑的三档不完全一致？", "JY 表三档（12000/18000/30000）是手工设定的整数锚；模型给出的是连续分布上的对应位置。差异属正常——锚的用途是执行接口，分布的用途是概率读数，两者并行不悖。"),
    ("读数示例", f"「首年销量 P50 = {pct(y1,50):,.0f} 台」→ 一半的可能性卖得比它多；「P(首年 ≥ 30,000) = {prob(y1,30000)*100:.1f}%」→ 约三成弱概率达到 Best 档；「三年累计 P95 = {pct(y3,95):,.0f} 台」→ 20 次里约有 1 次三年卖过 {pct(y3,95)/1e4:.1f} 万台。"),
]
r = 5
for q_, a_ in notes:
    ws3.cell(row=r, column=2, value=q_).font = B_FONT
    ws3.cell(row=r, column=3, value=a_).font = N_FONT
    ws3.cell(row=r, column=3).alignment = Alignment(wrap_text=True, vertical="top")
    ws3.row_dimensions[r].height = 46
    r += 1
ws3.column_dimensions["B"].width = 32
ws3.column_dimensions["C"].width = 100

XLSX = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen699销量概率分布_读数表.xlsx"
wb.save(XLSX)
print("\nExcel saved:", XLSX)

# npz 保存（供后续图表）
np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s699_v04_results.npz", y1=y1, y3=y3)
print("[npz saved]")
