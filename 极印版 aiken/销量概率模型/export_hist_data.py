# -*- coding: utf-8 -*-
"""导出四张分布图的直方图数据到 Excel（供 PPT 直接生成图表）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 载入数据
D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz")
y1, y3 = D["y1"], D["y3"]
B = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_backtest.npz")
s1_y1 = B["y1"]
rng_d = np.random.default_rng(7)
m_dji = rng_d.lognormal(mean=np.log(600_000), sigma=1.15, size=200_000)

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# 四张图的配置（与 HTML 页面一致）
charts = [
    {
        "sheet": "首年销量分布",
        "data": y1, "vmax": 45_000, "nbins": 46,
        "marks": [(10, "Worst 锚 P10"), (50, "Normal 锚 P50"), (90, "Best 锚 P90")],
        "shade": pct(y1, 90), "shade_label": "P(≥Best)=10%",
        "stats": [("P5", 5), ("P10", 10), ("P25", 25), ("P50", 50), ("P75", 75), ("P90", 90), ("P95", 95)],
        "unit": "台",
    },
    {
        "sheet": "三年累计分布",
        "data": y3, "vmax": 140_000, "nbins": 46,
        "marks": [(10, "P10"), (50, "P50"), (90, "P90")],
        "shade": 100_000, "shade_label": f"P(≥10万)={prob(y3,100_000)*100:.0f}%",
        "stats": [("P5", 5), ("P10", 10), ("P25", 25), ("P50", 50), ("P75", 75), ("P90", 90), ("P95", 95)],
        "unit": "台",
    },
    {
        "sheet": "S1回测分布",
        "data": s1_y1, "vmax": 30_000, "nbins": 56,
        "marks": [(92, None)],  # 特殊：内部预测线在 P92
        "extra_lines": [(25_000, "内部预测 25,000（P92 · 仅8%概率可达成）", "B8860B"),
                        (7_285, "实际（宽口径 ~7,300）落在 P5 以下", "EC008C")],
        "shade": 7_285, "shade_label": "实际落点",
        "stats": [("P5", 5), ("P10", 10), ("P25", 25), ("P50", 50), ("P75", 75), ("P90", 90), ("P95", 95)],
        "unit": "台",
    },
    {
        "sheet": "DJI回测分布",
        "data": m_dji, "vmax": 12_000_000, "nbins": 70,
        "marks": [],
        "extra_lines": [(350_000, "大疆内部预期 30–40万（P27–P36）", "6B6B6B"),
                        (1_000_000, "上调 100万（P67）", "B8860B"),
                        (5_000_000, "2024 实售 500万（P96.7）", "EC008C"),
                        (10_000_000, "累计 1000万+（P99.3 · 右尾保留 0.7%）", "EC008C")],
        "shade": 10_000_000, "shade_label": "右尾保留区",
        "stats": [("P50", 50), ("P90", 90), ("P95", 95), ("P99", 99)],
        "unit": "台",
    },
]

wb = openpyxl.Workbook()
wb.remove(wb.active)

HDR_FILL = PatternFill("solid", fgColor="111111")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
MARK_FILL = PatternFill("solid", fgColor="FDF3F8")
thin = Side(style="thin", color="CCCCCC")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

for cfg in charts:
    ws = wb.create_sheet(cfg["sheet"])
    counts, edges = np.histogram(cfg["data"], bins=cfg["nbins"], range=(0, cfg["vmax"]))
    data = cfg["data"]

    # 标题
    ws.cell(1, 1, f"AiKen 销量概率分布 · {cfg['sheet']} · 直方图数据（v0.4 · 8,000 次模拟）").font = Font(bold=True, size=13)
    ws.cell(2, 1, "用法：A 列为区间下界（含上界在右相邻行），B 列为落在该区间的模拟次数。在 PPT 中插入直方图/柱状图，X 轴取 A 列，Y 轴取 B 列。").font = Font(size=10, color="666666")

    # 表头
    ws.cell(4, 1, "区间下界").fill = HDR_FILL; ws.cell(4, 1).font = HDR_FONT
    ws.cell(4, 2, "模拟次数（频数）").fill = HDR_FILL; ws.cell(4, 2).font = HDR_FONT
    ws.cell(4, 3, "区间上界").fill = HDR_FILL; ws.cell(4, 3).font = HDR_FONT
    ws.cell(4, 4, "区间占比").fill = HDR_FILL; ws.cell(4, 4).font = HDR_FONT
    for c in range(1, 5):
        ws.cell(4, c).border = BORDER
        ws.cell(4, c).alignment = Alignment(horizontal="center")

    # 直方图数据
    n_total = len(data)
    r = 5
    for i, c in enumerate(counts):
        lo, hi = edges[i], edges[i+1]
        ws.cell(r, 1, int(lo)).border = BORDER
        ws.cell(r, 2, int(c)).border = BORDER
        ws.cell(r, 3, int(hi)).border = BORDER
        ws.cell(r, 4, c / n_total).number_format = "0.00%"
        ws.cell(r, 4).border = BORDER
        r += 1

    # 分位统计
    r += 1
    ws.cell(r, 1, "分位统计").font = Font(bold=True, size=11)
    r += 1
    ws.cell(r, 1, "分位").fill = HDR_FILL; ws.cell(r, 1).font = HDR_FONT
    ws.cell(r, 2, f"销量（{cfg['unit']}）").fill = HDR_FILL; ws.cell(r, 2).font = HDR_FONT
    r += 1
    for name, q_ in cfg["stats"]:
        ws.cell(r, 1, name).border = BORDER
        v = pct(data, q_)
        ws.cell(r, 2, round(v)).border = BORDER
        ws.cell(r, 2).number_format = "#,##0"
        r += 1

    # 锚线/参考线
    r += 1
    ws.cell(r, 1, "参考线（画在图上）").font = Font(bold=True, size=11)
    r += 1
    ws.cell(r, 1, "数值").fill = HDR_FILL; ws.cell(r, 1).font = HDR_FONT
    ws.cell(r, 2, "标注").fill = HDR_FILL; ws.cell(r, 2).font = HDR_FONT
    r += 1
    for q_, label in cfg["marks"]:
        if label:
            ws.cell(r, 1, round(pct(data, q_))).border = BORDER
            ws.cell(r, 1).number_format = "#,##0"
            ws.cell(r, 2, label).border = BORDER
            r += 1
    for v, label, _color in cfg.get("extra_lines", []):
        ws.cell(r, 1, round(v)).border = BORDER
        ws.cell(r, 1).number_format = "#,##0"
        ws.cell(r, 2, label).border = BORDER
        r += 1

    # 阴影区
    if cfg.get("shade"):
        r += 1
        ws.cell(r, 1, f"阴影区：从 {round(cfg['shade']):,} 到图右端（{cfg.get('shade_label','')}）").font = Font(size=10, color="EC008C")

    # 列宽
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 12

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen四图直方图数据_PPT用.xlsx"
wb.save(OUT)
print("written:", OUT)
for cfg in charts:
    d = cfg["data"]
    print(f"  {cfg['sheet']}: {cfg['nbins']} bins, 0–{cfg['vmax']:,}, P50={pct(d,50):,.0f}")
