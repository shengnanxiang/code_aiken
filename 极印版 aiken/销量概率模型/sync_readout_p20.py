# -*- coding: utf-8 -*-
"""同步 699 读数表 Excel：锚行从 P10/P50/P90 改为 P20/P50/P90"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

XLSX = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen699销量概率分布_读数表.xlsx"
wb = load_workbook(XLSX)
ws = wb["销量分位表"]

d = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s699_v04_results.npz")
y1, y3 = d["y1"], d["y3"]
pct = lambda a, q_: float(np.percentile(a, q_))

ANCHOR_FILL = PatternFill("solid", fgColor="FFF6D9")
B_FONT = Font(name="微软雅黑", size=10, bold=True)

# 表结构：第5行表头，P5 从第6行起，B 列是分位标签，I 列是备注
row = 6
new_anchors = {
    20: "Worst 场景锚（首年平均月销 ~1,404 ｜ 三年月均 ~1,196）",
    50: "Normal 场景锚（首年平均月销 ~1,844 ｜ 三年月均 ~1,773）",
    90: "Best 场景锚（首年平均月销 ~2,733 ｜ 三年月均 ~2,949）",
}
while row <= ws.max_row:
    b = ws.cell(row=row, column=2).value
    if isinstance(b, str) and b.startswith("P") and b[1:].isdigit():
        qn = int(b[1:])
        # 先清旧锚样式与备注（P10/P50/P90 行）
        if qn in (10, 50, 90):
            for j in range(2, 10):
                ws.cell(row=row, column=j).fill = PatternFill(fill_type=None)
                ws.cell(row=row, column=j).font = Font(name="微软雅黑", size=10)
            if qn != 50:
                ws.cell(row=row, column=9, value="")
        # 打新锚（P20/P50/P90）
        if qn in new_anchors:
            for j in range(2, 10):
                ws.cell(row=row, column=j).fill = ANCHOR_FILL
                ws.cell(row=row, column=j).font = B_FONT
            ws.cell(row=row, column=9, value=new_anchors[qn])
    row += 1

# 同步修改表头注释
ws["B3"] = ("读法：「首年 P50 = X」表示 50% 的模拟结果首年销量低于 X。黄色底 = 三档场景锚（P20 Worst / P50 Normal / P90 Best）。"
            "口径：¥699 / BOM 250 / 漏斗参数 = v0.4 S1 实测原样（CPM 37.6-45.2 · CTR 2.14% · CVR 0.98%+余量，不做涨价折扣——S1 为 ¥1799 高价品，对 699 偏保守）")
ws["B3"].font = Font(name="微软雅黑", size=9, color="6B6B6B")

# 关键概率表区域：锚描述同步（找含 "P10" 的旧行文本并更新）
row = 6
while row <= ws.max_row:
    for col in (2, 3):
        v = ws.cell(row=row, column=col).value
        if isinstance(v, str) and "· v0.4 Normal" in v:
            ws.cell(row=row, column=2, value="P(首年 ≥ 2.21万 · Normal锚 P50)")
        if isinstance(v, str) and "· v0.4 Best" in v:
            ws.cell(row=row, column=2, value="P(首年 ≥ 3.28万 · Best锚 P90)")
    row += 1

# 分布说明 sheet 的锚描述
ws3 = wb["分布说明"]
for row in range(1, ws3.max_row + 1):
    c = ws3.cell(row=row, column=3)
    if isinstance(c.value, str) and "JY 表手工锚" in c.value:
        c.value = c.value.replace(
            "JY 表手工锚（月销1000/1500/2500 → 年销1.2/1.8/3.0万）落在本分布 P4 / P21 / P80 附近；模型 P10/P50/P90 对应首年平均月销 1,213 / 1,844 / 2,733 台",
            "三档场景锚已定：Worst = P20（首年 16,844 · 月均 ~1,404）/ Normal = P50（22,123 · ~1,844）/ Best = P90（32,793 · ~2,733）；对应新 Finance 表 AiKen JY 699 Finance P20_261027"
        )
    if isinstance(c.value, str) and "Worst（月销1,000" in c.value:
        c.value = c.value.replace(
            "Worst（月销500→年6000）≈ P1 以下；Normal（月销1000→年1.2万）≈ P1；Best（月销3000→年3.6万）≈ P75",
            "Worst = P20 / Normal = P50 / Best = P90（2026-10-28 裁定）"
        )

wb.save(XLSX)
print("读数表锚位已同步为 P20/P50/P90")

# 验证
print(f"\n锚位数值：P20={pct(y1,20):,.0f} P50={pct(y1,50):,.0f} P90={pct(y1,90):,.0f}")
print(f"三年锚位：P20={pct(y3,20)/1e4:.1f}万 P50={pct(y3,50)/1e4:.1f}万 P90={pct(y3,90)/1e4:.1f}万")
