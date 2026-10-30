# -*- coding: utf-8 -*-
"""
生成 PPT 直方图原始数据列（每行一个模拟值，可直接复制粘贴进 PPT）
================================================================
两种用法二选一（sheet 内有说明）：
  A. 「原始数据」sheet：单列展开数据（箱中值×频数），PPT 插入→直方图 直接出图
  B. 「分箱频数」sheet（备用）：若用普通柱状图，X=区间下界、Y=频数，间隙宽度调 0%
两种方法画出来的图与 HTML 评审页视觉一致（同一分箱边界）。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz")
y1, y3 = D["y1"], D["y3"]
B = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_backtest.npz")
s1_y1 = B["y1"]
rng_d = np.random.default_rng(7)
m_dji = rng_d.lognormal(mean=np.log(600_000), sigma=1.15, size=200_000)

pct = lambda a, q_: float(np.percentile(a, q_))

charts = [
    {"sheet": "首年销量分布", "data": y1, "vmax": 45_000, "nbins": 46,
     "ref": "参考线：P10=14,300 / P50=22,009 / P90=32,139；Best 阴影从 32,139 起"},
    {"sheet": "三年累计分布", "data": y3, "vmax": 140_000, "nbins": 46,
     "ref": "参考线：P10=32,985 / P50=63,130 / P90=103,850；10万 阴影从 100,000 起"},
    {"sheet": "S1回测分布", "data": s1_y1, "vmax": 30_000, "nbins": 56,
     "ref": "参考线：内部预测 25,000（P92）/ 实际宽口径 7,285（P5 以下）；阴影到 7,285 止"},
    {"sheet": "DJI回测分布", "data": m_dji, "vmax": 12_000_000, "nbins": 70,
     "ref": "参考线：内部预期 30-40万 / 上调 100万 / 实售 500万 / 累计 1000万；右尾阴影从 1000万 起"},
]

wb = openpyxl.Workbook()
wb.remove(wb.active)

HDR_FILL = PatternFill("solid", fgColor="111111")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
thin = Side(style="thin", color="CCCCCC")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

for cfg in charts:
    data, vmax, nbins = cfg["data"], cfg["vmax"], cfg["nbins"]
    counts, edges = np.histogram(data, bins=nbins, range=(0, vmax))
    bin_width = vmax / nbins

    # ===== Sheet A：原始数据列（PPT 直方图直接吃） =====
    ws = wb.create_sheet(cfg["sheet"])
    ws.cell(1, 1, f"{cfg['sheet']} · 原始数据列（PPT 直方图用）").font = Font(bold=True, size=13)
    ws.cell(2, 1, "步骤：① 选 A7 到列尾整列复制 ② PPT 插入→图表→直方图 ③ 粘贴覆盖示例数据").font = Font(size=10, color="666666")
    ws.cell(3, 1, f"④ 右键横轴→设置坐标轴格式→箱→宽度填 {bin_width:,.0f}（与本图分箱对齐）⑤ 参考线用手动线条画").font = Font(size=10, color="EC008C")
    ws.cell(4, 1, cfg["ref"]).font = Font(size=10, bold=True)
    ws.cell(5, 1, f"数据点 {int(counts.sum()):,} 个 = {nbins} 箱 × 频数展开（箱中值代表该箱）").font = Font(size=9, color="9a9a9a")
    ws.cell(6, 1, "销量(台)").fill = HDR_FILL
    ws.cell(6, 1).font = HDR_FONT

    r = 7
    for i, c in enumerate(counts):
        mid = int(round((edges[i] + edges[i+1]) / 2))
        for _ in range(int(c)):
            ws.cell(r, 1, mid)
            r += 1
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 30
    print(f"[{cfg['sheet']}] 原始数据 {r-7:,} 行")

    # ===== Sheet B：分箱频数（普通柱状图用，备用） =====
    ws2 = wb.create_sheet(cfg["sheet"] + "_分箱频数")
    ws2.cell(1, 1, f"{cfg['sheet']} · 分箱频数（普通柱状图用 · 备用方案）").font = Font(bold=True, size=13)
    ws2.cell(2, 1, "步骤：① 选中 A5:B 起两列数据 ② PPT 插入→簇状柱状图 ③ 粘贴 ④ 选中柱→间隙宽度调 0% ⑤ X 轴标签会显示区间下界").font = Font(size=10, color="666666")
    ws2.cell(3, 1, "两法画出的图形一致；本表优点是数据量小（几十行），缺点是要调间隙宽度。").font = Font(size=10, color="666666")
    ws2.cell(4, 1, cfg["ref"]).font = Font(size=10, bold=True)
    for c, h in [("A", "区间下界"), ("B", "模拟次数")]:
        ws2.cell(5, {"A":1,"B":2}[c], h).fill = HDR_FILL
        ws2.cell(5, {"A":1,"B":2}[c], h).font = HDR_FONT
        ws2.cell(5, {"A":1,"B":2}[c], h).border = BORDER
    r2 = 6
    for i, c in enumerate(counts):
        ws2.cell(r2, 1, int(edges[i])).border = BORDER
        ws2.cell(r2, 2, int(c)).border = BORDER
        r2 += 1
    ws2.column_dimensions["A"].width = 12
    ws2.column_dimensions["B"].width = 12

OUT = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen四图直方图数据_PPT用.xlsx"
wb.save(OUT)
print("written:", OUT)
