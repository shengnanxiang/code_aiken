# -*- coding: utf-8 -*-
"""查 JY 财务表里的 CMF 相关成本口径 + Budget sheet 里的模具/治具结构"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from openpyxl import load_workbook

wb = load_workbook(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\AiKen JY 699 Finance P20_261028.xlsx", data_only=True)
for sn in wb.sheetnames:
    ws = wb[sn]
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 45)):
        for c in row:
            if c.value and isinstance(c.value, str) and ("CMF" in c.value or "cmf" in c.value or "模具" in c.value or "治具" in c.value or "外观" in c.value):
                # 打印同行关键数值
                vals = []
                for cc in row:
                    if cc.value is not None:
                        vals.append(f"{cc.coordinate}={cc.value}")
                print(f"[{sn}] " + " | ".join(vals[:6]))
