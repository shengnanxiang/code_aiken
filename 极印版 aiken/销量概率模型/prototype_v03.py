# -*- coding: utf-8 -*-
"""
AiKen 销量概率分布模型 v0.3 —— 实测校准版
==========================================
校准来源（Maggie 提供，2026-10-26）：
  · 站外《极印投放数据_站外2026YTD1026》：S1 站外种草 CPM 37.6（全线 40.3）
  · 站内《JD26年效果广告分sku_站内》：S1 站内 CTR 2.14% · CVR 0.98% · CPM 45.2
  · 参照产品选择：S1（Maggie 判断：同为新品类需教育市场；N 系列与小米同质化，参照失真）

v0.2 → v0.3 变更：
  [1] 漏斗参数全部换实测（原行业通带）：
      CPM 45-75 → 36-48（S1 站外 37.6 / 站内 45.2）
      CTR 1.5-3.5% → 1.8-3.0%（S1 实测 2.14%；AiKen 素材冲击力强但品牌认知为零）
      CVR 1.2-2.8% → 1.0-2.2%（S1 实测 0.98% 下界；N2 3.27% 印证价位弹性，AiKen 介于其间偏下）
  [2] 媒介预算先验锚定 S1 实投（站内 30.6 万 + 站外 62.6 万 = 93 万 YTD）：
      AiKen 战略新品取 1-2.5 倍加权 → 6 个月 80-240 万（原 120-280 万无锚占位）
  [3] m 先验微调：P50 12万 → 11万，sigma 0.90 → 0.85
      （S1 教育期数据提示新品类爬坡更慢；但 AiKen 价格为 S1 的 1/3 且品类叙事更强，不作大幅下调）
  [4] q 先验维持 0.42（站外 30 天互动数据不足以重估，上市后 Checkpoint 校正）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

rng = np.random.default_rng(20261026)

N_SIM = 8000
T_MONTHS = 36

# ================= [1] RCF + 实测先验 =================
m_prior = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

# 漏斗（实测校准）
B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)  # 6 个月媒介预算（元）
CPM = rng.triangular(36, 42, 48, size=N_SIM)        # S1 站内 45.2 / 站外 37.6
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)   # S1 实测 2.14%
CVR = rng.triangular(0.010, 0.015, 0.022, size=N_SIM)   # S1 0.98% 下界，N2 3.27% 上界参考

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

# ================= [2] Bass 拼接 =================
def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    lo = np.full_like(m, 1e-5); hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        too_small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)

p_solved = solve_p(m_prior, q_prior, s6)
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1 = paths[:, 11]; y3 = paths[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=" * 66)
print("AiKen 销量概率分布模型 v0.3（实测校准）· %d 次模拟" % N_SIM)
print("=" * 66)

print("\n【校准参数（S1 实测口径）】")
print(f"  CPM: P5={pct(CPM,5):.0f} P50={pct(CPM,50):.0f} P95={pct(CPM,95):.0f} 元（S1站外37.6/站内45.2）")
print(f"  CTR: P5={pct(CTR,5)*100:.2f}% P50={pct(CTR,50)*100:.2f}% P95={pct(CTR,95)*100:.2f}%（S1实测2.14%）")
print(f"  CVR: P5={pct(CVR,5)*100:.2f}% P50={pct(CVR,50)*100:.2f}% P95={pct(CVR,95)*100:.2f}%（S1实测0.98%）")
print(f"  媒介预算(6月): P5={pct(B_budget,5)/1e4:.0f}万 P50={pct(B_budget,50)/1e4:.0f}万 P95={pct(B_budget,95)/1e4:.0f}万（锚S1实投93万YTD）")
print(f"  6个月漏斗销量: P5={pct(s6,5)/1e4:.2f}万 P50={pct(s6,50)/1e4:.2f}万 P95={pct(s6,95)/1e4:.2f}万")

print("\n【首年销量分布】")
print(f"  P5 ={pct(y1,5)/1e4:.2f}万  P25={pct(y1,25)/1e4:.2f}万  P50={pct(y1,50)/1e4:.2f}万  P75={pct(y1,75)/1e4:.2f}万  P95={pct(y1,95)/1e4:.2f}万")

print("\n【三年累计】")
print(f"  P5={pct(y3,5)/1e4:.2f}万  P50={pct(y3,50)/1e4:.2f}万  P95={pct(y3,95)/1e4:.2f}万")

print("\n【会议三档在新分布中的分位】")
for name, v in [("Worst 月销500→年6000", 6_000), ("Normal 月销1000→年1.2万", 12_000), ("Best 月销3000→年3.6万", 36_000)]:
    cdf = float((y1 <= v).mean()) * 100
    print(f"  {name}: P{cdf:.0f}")

print("\n【关键概率】")
for th in [6_000, 12_000, 36_000, 100_000]:
    print(f"  P(首年≥{th/1e4:.0f}万)={prob(y1,th)*100:.1f}%   P(三年≥{th/1e4:.0f}万)={prob(y3,th)*100:.1f}%")

# v0.2 对照
print("\n【v0.2 → v0.3 对比】")
print(f"  首年 P50: 2.86万 → {pct(y1,50)/1e4:.2f}万")
print(f"  首年 P95: 5.01万 → {pct(y1,95)/1e4:.2f}万")
print(f"  三年 P50: 7.65万 → {pct(y3,50)/1e4:.2f}万")

# ================= [3] 财务层（参数不变） =================
PRICE, BOM = 599.0, 250.0
CH_RATE, SALES_RATE = 0.25, 0.08
NRE_REMAIN = 6_300_000
cm_unit = PRICE * (1 - CH_RATE - SALES_RATE) - BOM
y1_cm = y1 * cm_unit
nre_cov = y1_cm / NRE_REMAIN
y3_cm = y3 * cm_unit
pnl3 = y3_cm - NRE_REMAIN

print("\n【财务层（占位参数不变）】")
print(f"  P(首年NRE覆盖≥60%)={prob(nre_cov,0.60)*100:.1f}%  P(三年转正)={prob(pnl3,0)*100:.1f}%  P(三年亏>200万)={float((pnl3<-2e6).mean())*100:.1f}%")

# ================= [4] 杠杆演示（预算） =================
s6_b = np.minimum(s6_raw * 1.5, m_prior * 0.55)
p_b = solve_p(m_prior, q_prior, s6_b)
paths_b = bass_cum_year(m_prior[:, None], p_b[:, None], q_prior[:, None], t_year[None, :])
y1_b = paths_b[:, 11]; y3_b = paths_b[:, 35]
print("\n【杠杆：预算×1.5】")
print(f"  首年 P50 {pct(y1,50)/1e4:.2f}万→{pct(y1_b,50)/1e4:.2f}万  P(≥Best线3.6万) {prob(y1,36000)*100:.0f}%→{prob(y1_b,36000)*100:.0f}%")
print(f"  三年 P50 {pct(y3,50)/1e4:.2f}万→{pct(y3_b,50)/1e4:.2f}万  P(三年≥10万) {prob(y3,100000)*100:.0f}%→{prob(y3_b,100000)*100:.0f}%")

# q 杠杆
q_k = np.clip(q_prior * 1.15, 0.18, 0.78)
p_k = solve_p(m_prior, q_k, s6)
paths_k = bass_cum_year(m_prior[:, None], p_k[:, None], q_k[:, None], t_year[None, :])
y3_k = paths_k[:, 35]
print(f"【杠杆：q×1.15】三年 P50 {pct(y3,50)/1e4:.2f}万→{pct(y3_k,50)/1e4:.2f}万  P(三年≥10万) {prob(y3,100000)*100:.0f}%→{prob(y3_k,100000)*100:.0f}%")

# m 杠杆
paths_m = bass_cum_year((m_prior*1.5)[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y3_m = paths_m[:, 35]
print(f"【杠杆：m×1.5】三年 P50 {pct(y3,50)/1e4:.2f}万→{pct(y3_m,50)/1e4:.2f}万")

# ================= [5] S1 直接对标读数（给飞轮页用） =================
print("\n【S1 实测基准读数（¥1799，2026 YTD ~10 个月）】")
print(f"  站内: 展现 676 万 / 点击 14.5 万 / 消费 30.6 万 / 订单行 {1416}")
print(f"  站外: 消费 62.6 万 / 曝光 1,664 万")
print(f"  → S1 站内直接归因月销 ≈ {1416/10:.0f} 台；AiKen(¥599) 价格 1/3，弹性放大")
print(f"  → 若 AiKen 复刻 S1 效率但价格弹性 ×3：月销 ~{1416/10*3:.0f} 台 ≈ 介于 Worst 与 Normal 之间")

np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v03_results.npz",
    y1=y1, y3=y3, paths=paths, m_prior=m_prior, q_prior=q_prior,
    p_solved=p_solved, s6=s6, y1_cm=y1_cm, nre_cov=nre_cov, pnl3=pnl3,
    y1_b=y1_b, y3_b=y3_b, y3_k=y3_k, y3_m=y3_m,
    CPM=CPM, CTR=CTR, CVR=CVR, B_budget=B_budget,
)
print("\n[Saved] v03_results.npz")
