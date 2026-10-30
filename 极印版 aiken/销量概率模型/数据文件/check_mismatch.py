# -*- coding: utf-8 -*-
"""对比读数表 vs v0.4 的数字，确认哪边过期"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import openpyxl

# v0.4 真实分位
D = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz")
y1, y3 = D["y1"], D["y3"]
pct = lambda a, q_: float(np.percentile(a, q_))
print("=== v0.4 权威数字（prototype_v04.py 跑出） ===")
print(f"首年: P10={pct(y1,10):,.0f}  P50={pct(y1,50):,.0f}  P90={pct(y1,90):,.0f}")
print(f"     月销折算: {pct(y1,10)/12:,.0f} / {pct(y1,50)/12:,.0f} / {pct(y1,90)/12:,.0f}")
print(f"三年: P10={pct(y3,10):,.0f}  P50={pct(y3,50):,.0f}  P90={pct(y3,90):,.0f}")

# 读数表现状
wb = openpyxl.load_workbook(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\AiKen销量概率分布_读数表.xlsx", data_only=True)
print("\n=== 读数表（AiKen销量概率分布_读数表.xlsx）当前内容 ===")
for ws in wb.worksheets:
    print(f"\n--- sheet: {ws.title} ---")
    n = 0
    for row in ws.iter_rows(values_only=True):
        if all(v is None for v in row): continue
        vals = [str(v)[:36] if v is not None else "" for v in row]
        while vals and vals[-1] == "": vals.pop()
        print(" | ".join(vals))
        n += 1
        if n > 30: print("...(截断)"); break
