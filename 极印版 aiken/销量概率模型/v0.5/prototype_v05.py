# -*- coding: utf-8 -*-
"""
AiKen 销量概率模型 v0.5 · 核心对标带校准版
===========================================
与 v0.4 的差异（只动 m 和 q 的先验，漏斗/财务口径不变）：
  m 先验：参照带收窄到「核心对标带 ¥500-800」产品群为主
    - instax mini 12（¥599-699，中国市场年销估 25-40 万台）为 m 的 P50 附近证据
    - Flashback One35（¥749，三年用户 5-10 万）为 m 下界证据
    - Paper Shoot（小众存活 2-5 万）为 m 的低分位证据
    - Kodak Mini Shot（¥1,269 观察带）降为仅观察证据，不再进参数
    - 新设定：lognormal(P50=9.5万, σ=0.80)——比 v0.4 (11万/0.85) 收窄且略降：
      · P50 11万→9.5万：核心带对标的水位重心略低于原参照带（原含 Kodak 1-3万
        的中游带拉高了综合；Kodak 移出后，instax mini 中国盘若做「AiKen 直接
        平替」能吃到的份额按保守口径取 25% 折算 ≈ 8-10 万）
      · σ 0.85→0.80：核心带证据密度更高（同价位可比性更强），不确定性略收
  q 先验：不变（CCD/撕拉片/薇娅证据与价格带无关）
  漏斗（S1 实测原样）、财务（单台 102.25 元）不变
锚位更新：Worst = P20（用户裁决），Normal = P50，Best = P90
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261022)
N_SIM = 8000
T_MONTHS = 36

# ===== v0.5 先验 =====
m_prior = rng.lognormal(mean=np.log(95_000), sigma=0.80, size=N_SIM)   # 9.5万 / 0.80
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)      # 不变
B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)   # 不变
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    lo = np.full_like(m, 1e-5); hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        small = bass_cum_year(m, mid, q, 0.5) < s6_target
        lo = np.where(small, mid, lo); hi = np.where(small, hi, mid)
    return 0.5 * (lo + hi)

p_solved = solve_p(m_prior, q_prior, s6)
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])
y1 = paths[:, 11]; y3 = paths[:, 35]

# 预算杠杆
s6_b = np.minimum(s6_raw * 1.5, m_prior * 0.55)
p_b = solve_p(m_prior, q_prior, s6_b)
paths_b = bass_cum_year(m_prior[:, None], p_b[:, None], q_prior[:, None], t_year[None, :])
y1_b = paths_b[:, 11]; y3_b = paths_b[:, 35]

pct = lambda a, x: float(np.percentile(a, x))
prob = lambda a, th: float((a >= th).mean())

print("=== v0.5（核心对标带 ¥500-800 校准）===")
print(f"m 先验: P10={pct(m_prior,10):,.0f}  P50={pct(m_prior,50):,.0f}  P90={pct(m_prior,90):,.0f}  P(>=100万)={float((m_prior>=1e6).mean())*100:.2f}%")
print(f"首年: P10={pct(y1,10):,.0f}  P20={pct(y1,20):,.0f}  P50={pct(y1,50):,.0f}  P80={pct(y1,80):,.0f}  P90={pct(y1,90):,.0f}")
print(f"三年: P10={pct(y3,10):,.0f}  P50={pct(y3,50):,.0f}  P90={pct(y3,90):,.0f}")
print(f"锚(Worst=P20/Normal=P50/Best=P90): {pct(y1,20):,.0f} / {pct(y1,50):,.0f} / {pct(y1,90):,.0f}")
print(f"预算x1.5: P50 {pct(y1,50):,.0f}->{pct(y1_b,50):,.0f}  P(>=P90) {prob(y1,pct(y1,90))*100:.0f}%->{prob(y1_b,pct(y1,90))*100:.0f}%")
print(f"P(三年>=10万): {prob(y3,1e5)*100:.1f}%")

UNIT = 503.2181 * 0.7 - 250
print(f"\n财务（单台 {UNIT:.2f} 元）:")
print(f"首年净贡献 P50: {pct(y1,50)*UNIT/1e4:.0f}万  三年: {pct(y3,50)*UNIT/1e4:.0f}万")
print(f"首年投入覆盖 P50: {pct(y1,50)*UNIT/4_740_550*100:.0f}%")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v0.5\v05_results.npz",
         y1=y1, y3=y3, y1_b=y1_b, y3_b=y3_b, paths=paths,
         m_prior=m_prior, q_prior=q_prior, p_solved=p_solved, s6=s6,
         exposure=exposure, clicks=clicks, B_budget=B_budget)
print("\n[saved v0.5/v05_results.npz]")
