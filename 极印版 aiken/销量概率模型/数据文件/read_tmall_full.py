# -*- coding: utf-8 -*-
"""提取天猫 S1 全部月度行（表格按产品分块，S1 块在文件后段）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from openpyxl import load_workbook

PATH = r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\Tmall 4-9月推广单品数据_站内投放.xlsx"
wb = load_workbook(PATH, data_only=True)
ws = wb["Sheet1"]

# 扫描全部行：找 "S1" 块标题行，然后收集后续数据行
rows = list(ws.iter_rows(values_only=True))
current_model = None
s1_rows = []
for r in rows:
    if r is None: continue
    first = str(r[0]).strip() if r[0] is not None else ""
    if first in ("N1", "N2", "N3", "S1"):
        current_model = first
        continue
    if first and ("月" in first or first.replace("月","").strip().isdigit()):
        if current_model == "S1":
            s1_rows.append(r)

print(f"S1 天猫数据行数: {len(s1_rows)}")
print(f"{'月份':<6}{'花费':>10}{'展现':>10}{'点击':>8}{'购物车':>8}{'成交金额':>12}{'CPM':>8}{'CTR':>7}{'CVR':>7}{'投产比':>7}")
tot = [0.0]*5
def fnum(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0
for r in s1_rows:
    month = str(r[0]).strip()
    spend, exp, clk, cart, gmv = [fnum(x) for x in (r[1], r[2], r[3], r[4], r[5])]
    cpm, ctr, cvr, roi = [fnum(x) for x in (r[6], r[7], r[9], r[12])]
    print(f"{month:<6}{spend:>10,.0f}{exp:>10,.0f}{clk:>8,.0f}{cart:>8,.0f}{gmv:>12,.0f}{cpm:>8.1f}{ctr*100:>6.2f}%{cvr*100:>6.2f}%{roi:>7.2f}")
    tot[0] += spend; tot[1] += exp; tot[2] += clk; tot[3] += cart; tot[4] += gmv
print(f"{'合计':<6}{tot[0]:>10,.0f}{tot[1]:>10,.0f}{tot[2]:>8,.0f}{tot[3]:>8,.0f}{tot[4]:>12,.0f}")

# S1 天猫成交台数估算：成交金额 / 1799
PRICE = 1799.0
units_tm = tot[4] / PRICE
print(f"\n天猫 S1 站内投放成交（{len(s1_rows)} 个月）: GMV {tot[4]:,.0f} 元 → ~{units_tm:,.0f} 台（按 ¥1,799）")
print(f"注意：这是「站内推广归因」的成交，含自然流量的全店成交会更高")

# ===== 拼完整观测口径（4-9 月 + 10 月锚）=====
# JD 站内（3-10 月 8 个月）：1,416 台（直接 893 + 间接 523）
# 天猫站内推广（4-9 月 6 个月）：~GMV/1799 台
# 10 月（Maggie 口径）：S1 净销售 ~152 台/10月20日单日峰值，月估 ~1,500-2,500 台（双十一切割）
#   ——保守处理：10 月按 10-20 前日均 ~60-100 台 + 20 日后大促日 ~150-300/日 → 月 ~2,000-4,000？
#   Maggie 说「10月20日那天152台，主要靠双十一收割」→ 用保守月估 ~1,800 台（未含完整大促）
# 站外（小红书+抖音 153 万花费）：按天猫+JD 加权 ROI 折算
print("\n===== 完整观测口径拼图 =====")
jd_total = 1416
print(f"JD 站内（3-10月，8个月）: {jd_total} 台")
print(f"天猫站内推广（4-9月，6个月）: ~{units_tm:,.0f} 台（站内归因口径）")
# 天猫站内 ROI = GMV/花费
tm_roi = tot[4] / tot[0] if tot[0] else 0
print(f"天猫站内 ROI: {tm_roi:.2f}（vs JD 8.25）")
# 站外花费 153 万，用两渠道 ROI 中位数折算
OUT_SPEND = 626_289.4 + 904_104.0
jd_roi = 8.254
for eff_label, eff in [("站外=JD效率100%", jd_roi), ("站外=两渠道均值", (jd_roi+tm_roi)/2), ("站外=50%效率", jd_roi*0.5)]:
    out_units = OUT_SPEND * eff / PRICE
    print(f"  站外折算（{eff_label} ROI={eff:.1f}）: ~{out_units:,.0f} 台")
