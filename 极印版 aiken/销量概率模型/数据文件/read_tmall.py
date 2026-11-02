# -*- coding: utf-8 -*-
"""读取天猫 S1 数据，拼出完整观测口径"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from openpyxl import load_workbook

PATH = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\Tmall 4-9月推广单品数据_站内投放.xlsx"
wb = load_workbook(PATH, data_only=True)
print("Sheets:", wb.sheetnames)
for sn in wb.sheetnames:
    ws = wb[sn]
    print(f"\n===== {sn} ({ws.max_row}r x {ws.max_column}c) =====")
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 30), max_col=min(ws.max_column, 20)):
        vals = []
        for c in row:
            if c.value is not None:
                v = c.value
                if isinstance(v, float): v = round(v, 3)
                vals.append(str(v)[:20])
        if vals:
            print(" | ".join(vals))
