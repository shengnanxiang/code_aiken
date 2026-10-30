# -*- coding: utf-8 -*-
"""
S1 Checkpoint 校准：用上市后真实投放数据收窄销量预测分布
==========================================================
事前分布：backtest_s1.py 的 ex-ante 模型（N 系参数，2026-04 站位）——补算 y3
观测数据（JD 站内明细，2026-03 至 2026-10 八个月）：
  展现 6,763,732 · 点击 144,604 · CTR 2.14% · 花费 30.6 万 · CPM 45.2
  直接订单 32.3 · 站外投放（小红书+抖音）金额 ~153 万（S1 归属）
  全渠道销量锚（Maggie 口径）：首年宽口径 ~7,285 台（JD 直接归因 1,416 × ~5 倍）
校准方法（近似贝叶斯 / ABC 拒绝采样）：
  1) 事前先验抽样 8,000 组 (m, q)，漏斗按 S1 真实花费/CPM/CTR
  2) 似然：模拟首 8 个月销量 vs 观测区间（宽口径月销 + 噪声），按吻合度加权
  3) 加权重抽样 → 事后分布 → 重新跑 Bass 得校准后 y1 / y3
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20260426)
N_SIM = 8000
T_MONTHS = 36

# ============ 事前先验（与 backtest_s1.py 完全一致） ============
m_prior = rng.lognormal(mean=np.log(60_000), sigma=0.80, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

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

t_year = np.arange(1, T_MONTHS + 1) / 12.0

def run_paths(m, q, p):
    return bass_cum_year(m[:, None], p[:, None], q[:, None], t_year[None, :])

# ===== 事前漏斗（N 系参数，站前视野）→ 事前 y1/y3 =====
B_pre = rng.triangular(300_000, 650_000, 1_200_000, size=N_SIM)
CPM_pre = rng.triangular(43, 115, 162, size=N_SIM)
CTR_pre = rng.triangular(0.038, 0.045, 0.064, size=N_SIM)
CVR_pre = rng.triangular(0.013, 0.025, 0.033, size=N_SIM)
s6_pre = np.minimum((B_pre / CPM_pre * 1000) * CTR_pre * CVR_pre, m_prior * 0.55)
p_pre = solve_p(m_prior, q_prior, s6_pre)
paths_pre = run_paths(m_prior, q_prior, p_pre)
y1_pre, y3_pre = paths_pre[:, 11], paths_pre[:, 35]

# ===== 校准：S1 真实数据（2026-03 ~ 2026-10，8 个月） =====
# 漏斗实测（JD 站内 + 站外合计的等效口径）
#   站内：花费 30.6万 / 曝光 676万 / 点击 14.5万 / 订单 32.3
#   站外（小红书+抖音，S1 归属金额）：62.6 + 90.4 = 153 万
#   总花费 ≈ 183.6 万（8 个月），等效月均 ~23 万
# 观测销量（宽口径）：
#   JD 直接归因 1,416 台 ÷ 7 个月 ≈ 202/月；宽口径 ×3 ≈ 7,285/首年（8 个月外推 12 个月）
#   8 个月观测宽口径销量 ≈ 202 × 3 × 8 ≈ 4,850 台（区间 3,600 ~ 6,200 覆盖归因不确定性）

# 用真实漏斗重推：总花费 183.6万 / CPM 实测 45.2（站内）~ 40（站外加权） → 用 43
# CTR 实测 2.14% / CVR 实测 0.98%（宽口径 CVR = 订单宽 / 点击 ≈ (202×3)/月点击）
B_obs = 1_836_000.0
CPM_obs = 43.0
CTR_obs = 0.0214
monthly_clicks = B_obs / CPM_obs * 1000 * CTR_obs / 8  # ≈ 11,400 点击/月

# ABC 校准：对每组 (m, q)，用实测漏斗参数解 p，模拟 8 个月累计，与观测比
OBS_8M = 4_850.0        # 8 个月宽口径销量观测（中心）
OBS_SIGMA = 800.0       # 观测不确定性（归因口径 ±）

s6_cal = None  # 不用 6 个月锚，直接对 8 个月
# 对每组 (m,q) 解 p 使 Bass(8/12 年) = 模拟 8 个月销量
# 8 个月销量来自漏斗：月点击 × CVR(未知，需采样) × 8
# CVR 宽口径后验采样：中心 0.98%×3=2.94%? 不对——宽口径销量÷点击
# 直接：月销量宽口径 ≈ 202×3=606/月 → CVR_eff = 606/11400 ≈ 5.3%? 这不对，宽口径包含自然流量
# 更稳妥：直接用销量观测对 (m,q) 做似然，漏斗只约束 p 的存在性
def bass_8m(m, p, q):
    t = 8/12
    return m * (1 - np.exp(-(p+q)*t)) / (1 + (q/p)*np.exp(-(p+q)*t))

# 似然权重：给定 (m, q)，存在 p 使 8 个月销量 = OBS；p 在合理范围 [0.0005, 1.2]
# 对每个 (m,q)：解 p_8m 使 bass_8m = OBS_8M
lo = np.full(N_SIM, 5e-4); hi = np.full(N_SIM, 1.2)
for _ in range(50):
    mid = 0.5 * (lo + hi)
    too_small = bass_8m(m_prior, mid, q_prior) < OBS_8M
    lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
p_8m = 0.5 * (lo + hi)

# p 合理性检查：太小的 p（<0.0005 无法达成，即 m 太小或 q 太大）→ 权重 0
feasible = (p_8m > 5e-4) & (p_8m < 1.2)
# 观测噪声权重：模拟值围绕 OBS 的吻合度（p_8m 解出的 Bass(0.67) 与 OBS 完美匹配，
# 但 m 的后续路径仍由先验决定；真正的不确定性在 m 和 q 的联合后验上）
# 事后权重 ∝ 先验 × 似然；似然用「该 (m,q,p_8m) 下的 12 个月外推 vs 观测带」
y1_implied = bass_cum_year(m_prior, p_8m, q_prior, 1.0)
# 观测对 y1 的约束：8 个月 4,850 → 12 个月外推区间 [5,800, 8,500]（Bass 后段加速）
Y1_LO, Y1_HI = 5_800, 8_500
w = np.exp(-0.5 * ((y1_implied - 7_150) / 1_350.0) ** 2)  # 中心 7,150，σ=1,350
w = w * feasible

# 归一化重抽样（ABC posterior）
w_norm = w / w.sum()
post_idx = rng.choice(N_SIM, N_SIM, p=w_norm)
m_post = m_prior[post_idx]
q_post = q_prior[post_idx]
# p 用 8 个月锚重解（事后 p 分布）
lo = np.full(N_SIM, 5e-4); hi = np.full(N_SIM, 1.2)
for _ in range(50):
    mid = 0.5 * (lo + hi)
    too_small = bass_8m(m_post, mid, q_post) < OBS_8M
    lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
p_post = 0.5 * (lo + hi)

paths_post = run_paths(m_post, q_post, p_post)
y1_post, y3_post = paths_post[:, 11], paths_post[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=" * 68)
print("S1 Checkpoint 校准 · 事前 vs 事后")
print("=" * 68)
print(f"\n观测（2026-03~10，8 个月）：宽口径销量 ~{OBS_8M:,.0f} 台（JD 归因 1,416 × ~3）")
print(f"  花费 {B_obs/1e4:.0f}万 · CPM ~43 · CTR 2.14% · 月点击 ~{monthly_clicks:,.0f}")
print(f"\n【事前分布（N 系参数 ex-ante）】")
print(f"  首年: P5={pct(y1_pre,5):,.0f}  P10={pct(y1_pre,10):,.0f}  P50={pct(y1_pre,50):,.0f}  P90={pct(y1_pre,90):,.0f}  P95={pct(y1_pre,95):,.0f}")
print(f"  三年: P5={pct(y3_pre,5):,.0f}  P50={pct(y3_pre,50):,.0f}  P90={pct(y3_pre,90):,.0f}  P95={pct(y3_pre,95):,.0f}")
print(f"\n【事后分布（8 个月真实数据校准）】")
print(f"  首年: P5={pct(y1_post,5):,.0f}  P10={pct(y1_post,10):,.0f}  P50={pct(y1_post,50):,.0f}  P90={pct(y1_post,90):,.0f}  P95={pct(y1_post,95):,.0f}")
print(f"  三年: P5={pct(y3_post,5):,.0f}  P50={pct(y3_post,50):,.0f}  P90={pct(y3_post,90):,.0f}  P95={pct(y3_post,95):,.0f}")
print(f"\n收窄幅度：")
print(f"  首年 P5-P95 宽度: {pct(y1_pre,95)-pct(y1_pre,5):,.0f} → {pct(y1_post,95)-pct(y1_post,5):,.0f}（收窄 {(1-(pct(y1_post,95)-pct(y1_post,5))/(pct(y1_pre,95)-pct(y1_pre,5)))*100:.0f}%）")
print(f"  三年 P5-P95 宽度: {pct(y3_pre,95)-pct(y3_pre,5):,.0f} → {pct(y3_post,95)-pct(y3_post,5):,.0f}（收窄 {(1-(pct(y3_post,95)-pct(y3_post,5))/(pct(y3_pre,95)-pct(y3_pre,5)))*100:.0f}%）")
print(f"\n内部预测 25,000 落点：事前 P{float((y1_pre<=25000).mean())*100:.0f} → 事后 P{float((y1_post<=25000).mean())*100:.0f}")
print(f"P(事后首年 ≥ 10,000) = {prob(y1_post, 10_000)*100:.1f}%")
print(f"P(事后首年 ≥ 25,000) = {prob(y1_post, 25_000)*100:.2f}%")

# 后验参数
print(f"\nm 先验 vs 后验: P50 {pct(m_prior,50)/1e4:.1f}万 → {pct(m_post,50)/1e4:.1f}万；P10-P90: {pct(m_prior,10)/1e4:.1f}-{pct(m_prior,90)/1e4:.1f}万 → {pct(m_post,10)/1e4:.1f}-{pct(m_post,90)/1e4:.1f}万")
print(f"q 先验 vs 后验: P50 {pct(q_prior,50):.2f} → {pct(q_post,50):.2f}")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\s1_calibration.npz",
         y1_pre=y1_pre, y3_pre=y3_pre, y1_post=y1_post, y3_post=y3_post,
         m_post=m_post, q_post=q_post)
print("\n[saved s1_calibration.npz]")
