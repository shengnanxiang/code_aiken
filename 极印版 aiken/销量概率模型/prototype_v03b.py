# -*- coding: utf-8 -*-
"""
v0.3b：财务层修正重跑
  [1] NRE 口径修正：剩余投入 4,138,050 元（Budget sheet H8，验证过）
     —— 替代原「630 万剩余 NRE」的错误口径
  [2] 三档场景重新锚定：以 v0.3 分布的 P10 / P50 / P90 为准（用户裁决 2026-10-26）
     —— 替代会议纪要的 500/1000/3000 月销口径
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

d = np.load(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v03_results.npz")
y1 = d["y1"]; y3 = d["y3"]; y1_b = d["y1_b"]; y3_b = d["y3_b"]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ================= [1] 新三档（分布分位锚） =================
W = pct(y1, 10)   # P10
N = pct(y1, 50)   # P50
B = pct(y1, 90)   # P90

print("=" * 66)
print("【新三档场景 = v0.3 分布分位（用户裁决）】")
print(f"  Worst  = P10 = {W:,.0f} 台/首年（月销 ≈ {W/12:,.0f}）")
print(f"  Normal = P50 = {N:,.0f} 台/首年（月销 ≈ {N/12:,.0f}）")
print(f"  Best   = P90 = {B:,.0f} 台/首年（月销 ≈ {B/12:,.0f}）")
print(f"  三年累计同分位：P10={pct(y3,10):,.0f}  P50={pct(y3,50):,.0f}  P90={pct(y3,90):,.0f}")

# ================= [2] 财务层（新 NRE 口径 413.8 万） =================
PRICE, BOM = 599.0, 250.0
CH_RATE, SALES_RATE = 0.25, 0.08
INVEST = 4_138_050.0   # Budget sheet H8：继续投入（模具60+治具71.5+NRE48.125+测试15.9+认证15+人力203.28）

cm_unit = PRICE * (1 - CH_RATE - SALES_RATE) - BOM   # 151.4 元/台净贡献（占位口径）
print()
print("【财务层 · 新口径】")
print(f"  单台净贡献（占位：渠道25%+销售费8%）: {cm_unit:.1f} 元")

for name, vol in [("Worst(P10)", W), ("Normal(P50)", N), ("Best(P90)", B)]:
    cm = vol * cm_unit
    cov = cm / INVEST
    print(f"  {name}: 首年销量 {vol/1e4:.2f}万 · 净贡献 {cm/1e4:.0f}万 · 投入覆盖 {cov*100:.0f}%")

# 全分布财务读数
y1_cm = y1 * cm_unit
y3_cm = y3 * cm_unit
pnl1 = y1_cm - INVEST
pnl3 = y3_cm - INVEST
print()
print("【全分布财务读数（投入 413.8 万）】")
print(f"  首年: 净贡献 P5={pct(y1_cm,5)/1e4:.0f}万 P50={pct(y1_cm,50)/1e4:.0f}万 P95={pct(y1_cm,95)/1e4:.0f}万")
print(f"  P(首年投入覆盖≥100%) = {prob(y1_cm, INVEST)*100:.1f}%")
print(f"  P(首年投入覆盖≥60%)  = {prob(y1_cm, INVEST*0.6)*100:.1f}%")
print(f"  三年累计: P5={pct(pnl3,5)/1e4:.0f}万 P50={pct(pnl3,50)/1e4:.0f}万 P95={pct(pnl3,95)/1e4:.0f}万（相对投入的净盈亏）")
print(f"  P(三年累计转正) = {prob(pnl3, 0)*100:.1f}%")
print(f"  P(三年净贡献覆盖投入 2 倍) = {prob(y3_cm, INVEST*2)*100:.1f}%")

# 预算杠杆（新口径）
print()
print("【预算杠杆 ×1.5（新口径）】")
print(f"  首年 P50 {pct(y1,50)/1e4:.2f}万→{pct(y1_b,50)/1e4:.2f}万")
print(f"  P(≥Best线 P90={B/1e4:.2f}万): {prob(y1,B)*100:.0f}%→{prob(y1_b,B)*100:.0f}%")
print(f"  P(三年净贡献覆盖投入): {prob(y3_cm, INVEST)*100:.0f}%→{prob(y3_b*cm_unit, INVEST)*100:.0f}%")

# 保存
np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v03b_finance.npz",
    W=W, N=N, B=B, y1_cm=y1_cm, y3_cm=y3_cm, pnl1=pnl1, pnl3=pnl3,
)
print("\n[Saved] v03b_finance.npz")
