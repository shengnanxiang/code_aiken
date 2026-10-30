# -*- coding: utf-8 -*-
"""
S1 回测检验 —— 用 AiKen 同款方法论「事前预测」S1，对照实际结果
================================================================
严格 ex-ante 设计（避免循环论证）：
  · 站位时间：2026 年 4 月底 S1 上市前夜
  · 漏斗先验：仅用 N 系数据（JD 表 2026 年 1-2 月，S1 上市前窗口）
      - N 系站内 CPM：N1 42.95 / N3 115.2 / N2 161.6 → 三角(43, 115, 162)
      - N 系站内 CTR：3.77% / 4.13% / 6.38% → 三角(3.8%, 4.5%, 6.4%)
      - N 系站内 CVR：1.32% / 2.80% / 3.27% → 三角(1.3%, 2.5%, 3.3%)
  · m 先验：¥1799 高价新品类参照带（外部对标，中心 6 万台/3 年）
  · 预算先验：N 系 YTD 月均（约 9.6 万/月）→ 6 个月 30-120 万
  · q 先验：品类文献带 0.42（同 AiKen 主模型）

对照的实际结果：
  · JD 站内直接归因：YTD 1,416 单（4-10 月约 7 个月 → 月均 ~202 台）
  · 全渠道换算情景：1×（仅 JD 归因）/ 2× / 3×（Maggie：天猫晚一周、后程收割更好）
  · 内部点预测（当时）：首年 25,000 台
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20260426)  # 站位 2026-04-26（S1 上市前夜）

N_SIM = 8000
T_MONTHS = 36

# ============ 事前先验（只用 S1 上市前可得信息） ============
# m：¥1799 高价新品类，3 年市场潜力
m_prior = rng.lognormal(mean=np.log(60_000), sigma=0.80, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

# 漏斗：N 系事前口径（已教育品类的参数带）
B_budget = rng.triangular(300_000, 650_000, 1_200_000, size=N_SIM)   # 6 个月
CPM = rng.triangular(43, 115, 162, size=N_SIM)
CTR = rng.triangular(0.038, 0.045, 0.064, size=N_SIM)
CVR = rng.triangular(0.013, 0.025, 0.033, size=N_SIM)

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

# ============ Bass 拼接（同主模型） ============
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
y1 = paths[:, 11]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

# ============ 实际结果 ============
JD_ATTRIBUTED_YTD = 1_416          # JD 站内直接归因（约 7 个月）
jd_monthly = JD_ATTRIBUTED_YTD / 7  # ~202/月
# 首年（12 个月）换算情景
scenarios = {
    "1× 仅 JD 归因":    jd_monthly * 12,           # 2,428
    "2× JD+天猫均衡":   jd_monthly * 12 * 2,       # 4,856
    "3× 全渠道（含自然）": jd_monthly * 12 * 3,     # 7,285
}
INTERNAL_FORECAST = 25_000

print("=" * 66)
print("S1 回测 · 事前分布（N 系参数，2026-04 前夜视角）")
print("=" * 66)
print(f"\n【事前漏斗参数（N 系已教育品类带）】")
print(f"  CPM: P50={pct(CPM,50):.0f}（N1 43 / N3 115 / N2 162）")
print(f"  CTR: P50={pct(CTR,50)*100:.2f}%（N1 3.8% / N3 4.1% / N2 6.4%）")
print(f"  CVR: P50={pct(CVR,50)*100:.2f}%（N1 1.3% / N3 2.8% / N2 3.3%）")
print(f"  预算(6月): P5={pct(B_budget,5)/1e4:.0f}万 P50={pct(B_budget,50)/1e4:.0f}万 P95={pct(B_budget,95)/1e4:.0f}万")
print(f"  m 先验: P10={pct(m_prior,10)/1e4:.1f}万 P50={pct(m_prior,50)/1e4:.1f}万 P90={pct(m_prior,90)/1e4:.1f}万")

print(f"\n【S1 首年销量 · 事前分布】")
print(f"  P5={pct(y1,5):,.0f}  P10={pct(y1,10):,.0f}  P25={pct(y1,25):,.0f}  P50={pct(y1,50):,.0f}  P75={pct(y1,75):,.0f}  P90={pct(y1,90):,.0f}  P95={pct(y1,95):,.0f}")

print(f"\n【实际 vs 事前分布】")
for name, actual in scenarios.items():
    cdf = float((y1 <= actual).mean()) * 100
    print(f"  实际 {name:14s} ≈ {actual:>6,} 台/首年 → 落在事前分布 P{cdf:.0f}")

cdf_int = float((y1 <= INTERNAL_FORECAST).mean()) * 100
print(f"\n  内部点预测 25,000 台 → 落在事前分布 P{cdf_int:.0f}")
print(f"  P(实际 ≥ 25,000) = {prob(y1, INTERNAL_FORECAST)*100:.1f}%")
print(f"  P(实际 ≥ 10,000) = {prob(y1, 10_000)*100:.1f}%")
print(f"  P(实际 ≥ 7,285)  = {prob(y1, 7_285)*100:.1f}%")

# ============ 结论提炼 ============
print("\n" + "=" * 66)
print("回测结论")
print("=" * 66)
p10 = pct(y1, 10)
print(f"""
1. 【分布方法的价值实证】内部点预测 25,000 台位于事前分布 P{cdf_int:.0f}——
   模型当时就会预警「该目标仅 {prob(y1,25000)*100:.0f}% 概率可达成」。
   实际结果（宽口径 ~7,300 台）落在 P{float((y1<=7285).mean())*100:.0f} 以下，验证了分布的怀疑。
   → 若当时用分布方法，25,000 的乐观倾向会被当场暴露。
2. 【参照类教训】N 系参数（已教育品类）对 S1（需教育品类）系统性高估约
   {pct(y1,50)/7285:.1f} 倍（P50 {pct(y1,50):,.0f} vs 实际宽口径 ~7,285）。
3. 偏差主因分解（S1 实测 vs N 系事前）：
   · CVR：N 系事前带 1.3-3.3% → S1 实际 0.98%（低于事前带下界）
   · CTR：N 系事前 3.8-6.4% → S1 实际 2.14%（低 40-60%）
   · CPM：N 系 43-162 → S1 实际 45.2（在带内，非偏差来源）
   → 高估来自「已教育品类 → 需教育品类」的漏斗效率断层，非单一参数。
4. 方法论结论（已吸收进 AiKen 模型）：
   · 参照类必须匹配品类教育状态（Maggie 判断的量化证据）
   · AiKen 锚 S1 而非 N 系 → 漏斗参数已按需教育品类口径取值
   · 概率分布方法有效：它当时就能预警点预测的乐观偏差；
     且 S1 教训（CVR 低于参照带下界）提示 AiKen 模型的 CVR 下界要留足余量
""")

np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_backtest.npz",
    y1=y1, m_prior=m_prior, p_solved=p_solved, q_prior=q_prior,
    scenarios=np.array(list(scenarios.values())),
)
print("[Saved] s1_backtest.npz")
