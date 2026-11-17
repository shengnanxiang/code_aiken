# -*- coding: utf-8 -*-
"""
CMF 限量版 SKU 销量概率模型 v0.1
====================================
场景：AiKen 单 SKU 上市后，追加 2-3 款限量 CMF（配色/材质/联名外观）SKU（1.5 代迭代）

建模口径：
  1. CMF SKU 的经济学特征：增量 NRE 低（复用主板/结构/模具，仅外观件改模/新表面工艺/丝印），
     溢价 10-15%，销量 = 基盘的一部分换色购买 + 一部分增量拉新
  2. 三种需求机制（文献 + 潮玩行业惯例）：
     - 替代效应：部分本会买标准色的用户改买限量款（不增量，贡献溢价）
     - 增量拉新：限量稀缺性触发原本观望人群（对应分布右移）
     - 复购/收藏：小比例用户买第二台（潮玩品类 5-15%）
  3. 先验设定（三档）：
     - 保守：限量款合计 = 基盘的 15%（替代为主，增量≈0）
     - 中性：合计 = 基盘的 30%（替代 20% + 增量 10%）
     - 乐观：合计 = 基盘的 55%（替代 25% + 增量 20% + 复购 10%）——instax mini 季节限定/联名款经验带
  4. 基盘：AiKen 699 口径 v0.4 分布（首年 P50=22,123 / P10=14,560 / P90=32,793）
  5. 增量 NRE（外观件改模+新工艺治具+认证微调+首批MOQ摊薄，2-3 款合计）：
     三档 (120, 250, 430) 万 ——待供应链拍板，先验带
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261111)
N = 200_000

# ===== 基盘：AiKen 699 口径首年分布（由 v0.4 参数重建）=====
rng_b = np.random.default_rng(20261022)
N_SIM = 8000
m = rng_b.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q = np.clip(rng_b.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B = rng_b.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)
CPM = rng_b.triangular(38, 45, 65, size=N_SIM)
CTR = rng_b.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR = rng_b.triangular(0.009, 0.014, 0.022, size=N_SIM)
clicks = (B / CPM * 1000) * CTR

def bass(mt, p, qt, t):
    t = np.asarray(t, dtype=float)
    return mt * (1 - np.exp(-(p + qt) * t)) / (1 + (qt / p) * np.exp(-(p + qt) * t))

def solve_p(mt, qt, s6):
    lo = np.full_like(mt, 1e-5); hi = np.full_like(mt, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        small = bass(mt, mid, qt, 0.5) < s6
        lo = np.where(small, mid, lo); hi = np.where(small, hi, mid)
    return 0.5 * (lo + hi)

ty = np.arange(1, 37) / 12.0
s6 = np.minimum(clicks * CVR, m * 0.55)
p = solve_p(m, q, s6)
paths = bass(m[:, None], p[:, None], q[:, None], ty[None, :])
base_y1 = paths[:, 11]   # 基盘首年

pct = lambda a, x: float(np.percentile(a, x))
prob = lambda a, th: float((a >= th).mean())
print("基盘验证（AiKen 699 v0.4）：P10=%,.0f P50=%,.0f P90=%,.0f" % (pct(base_y1,10), pct(base_y1,50), pct(base_y1,90)) if False else
      f"基盘验证（AiKen 699 v0.4）：P10={pct(base_y1,10):,.0f} P50={pct(base_y1,50):,.0f} P90={pct(base_y1,90):,.0f}")

# ===== CMF SKU 需求机制（蒙特卡洛）=====
# 限量款上市时机：假设在 AiKen 上市后 T_launch 个月推出（先验 4-9 个月），
# 吃基盘剩余周期 + 第二年的窗口

# 机制参数先验
cannibal = rng.triangular(0.10, 0.20, 0.30, size=N)   # 替代比例：限量款销量中抢基盘的部分（占基盘）
incremental = rng.triangular(0.02, 0.12, 0.25, size=N) # 增量拉新（占基盘）
repurchase = rng.triangular(0.01, 0.05, 0.12, size=N)  # 复购/收藏（占基盘）
premium = rng.triangular(0.08, 0.12, 0.18, size=N)     # 限量款溢价（¥699 → 759-799 档）

# 基盘抽样（从 v0.4 分布重抽 200k）
base_idx = rng_b.integers(0, N_SIM, size=N)
base1 = base_y1[base_idx]           # 上市首年基盘
# 限量款生命周期销量（对每条基盘轨迹施加机制参数）
cmf_units = base1 * (cannibal + incremental + repurchase)
# 其中真增量（对品牌总盘）：
cmf_incr = base1 * (incremental + repurchase)
# 总盘（基盘 + 增量部分；替代部分只是换色不计增量）
total_y1_equiv = base1 + cmf_incr

print(f"\n=== CMF SKU（2-3 款合计）销量分布 ===")
for label, arr in [("限量款合计销量", cmf_units), ("品牌总盘增量", cmf_incr), ("总盘（基盘+增量）", total_y1_equiv)]:
    print(f"{label}: P10={pct(arr,10):,.0f}  P50={pct(arr,50):,.0f}  P90={pct(arr,90):,.0f}")

# ===== 财务：增量 NRE 回收 =====
# CMF 款 ASP = 699 × (1+premium)；BOM 与标准款几乎同（+0-10 元表面工艺差），用 250-260
cmf_asp = 699 * (1 + premium)
cmf_bom = 250 + rng.triangular(0, 5, 12, size=N)
cmf_unit_cm = cmf_asp * 0.7 - cmf_bom   # 沿用 30% 费用率口径（ASP不含税×70%−BOM）
# 替代部分的溢价贡献：替代量 × (限量款净贡献 − 标准款净贡献)
std_unit_cm = 503.2181 * 0.7 - 250      # 102.25
cannibal_units = base1 * cannibal
premium_gain = cannibal_units * (cmf_unit_cm - std_unit_cm)
# 限量款总毛贡献 = 全部限量销量 × 限量净贡献（含替代，因为替代那台本来也会卖，用差值更准）
# 准确口径：品牌净增贡献 = 增量销量×限量CM + 替代销量×(限量CM−标准CM)
brand_gain = cmf_incr * cmf_unit_cm + premium_gain

NRE_CMF = rng.triangular(1_200_000, 2_500_000, 4_300_000, size=N)  # 2-3 款合计

print(f"\n=== 增量财务（2-3 款合计）===")
print(f"单台限量净贡献: P10={pct(cmf_unit_cm,10):.0f}  P50={pct(cmf_unit_cm,50):.0f}  P90={pct(cmf_unit_cm,90):.0f} 元（标准款 102）")
print(f"品牌净增贡献: P10={pct(brand_gain,10)/1e4:.0f}万  P50={pct(brand_gain,50)/1e4:.0f}万  P90={pct(brand_gain,90)/1e4:.0f}万")
print(f"增量 NRE: P10={pct(NRE_CMF,10)/1e4:.0f}万  P50={pct(NRE_CMF,50)/1e4:.0f}万  P90={pct(NRE_CMF,90)/1e4:.0f}万")
net = brand_gain - NRE_CMF
print(f"净收益（贡献−NRE）: P10={pct(net,10)/1e4:.0f}万  P50={pct(net,50)/1e4:.0f}万  P90={pct(net,90)/1e4:.0f}万")
print(f"P(净收益>0) = {prob(net,0)*100:.0f}%")
print(f"P(净收益>100万) = {prob(net,1e6)*100:.0f}%")
print(f"P(净收益>300万) = {prob(net,3e6)*100:.0f}%")

# 回本销量（覆盖 NRE 需要的限量款台数）
breakeven_units = NRE_CMF / cmf_unit_cm
print(f"\n回本所需限量款销量: P10={pct(breakeven_units,10):,.0f}  P50={pct(breakeven_units,50):,.0f}  P90={pct(breakeven_units,90):,.0f} 台")
print(f"对照限量款预期销量 P50={pct(cmf_units,50):,.0f} 台 → P(销量>回本线) = {prob(cmf_units - breakeven_units, 0)*100:.0f}%")

# 对总盘的影响
print(f"\n=== 对品牌总盘的影响（首年口径）===")
lift = (total_y1_equiv / base1 - 1)
print(f"总盘提升: P10={pct(lift,10)*100:.0f}%  P50={pct(lift,50)*100:.0f}%  P90={pct(lift,90)*100:.0f}%")
print(f"基盘 P50 {pct(base1,50):,.0f} → 总盘 P50 {pct(total_y1_equiv,50):,.0f}")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\数据文件\cmf_v01_results.npz",
         cmf_units=cmf_units, cmf_incr=cmf_incr, total=total_y1_equiv, base1=base1,
         brand_gain=brand_gain, net=net, NRE_CMF=NRE_CMF, cmf_unit_cm=cmf_unit_cm)
print("\n[saved cmf_v01_results.npz]")
