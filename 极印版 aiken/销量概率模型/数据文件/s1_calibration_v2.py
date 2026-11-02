# -*- coding: utf-8 -*-
"""
S1 Checkpoint 校准 v2 —— 完整观测口径（JD + 天猫 + 10月大促 + 站外）
====================================================================
vs v1 的差异：观测锚从 4,850（8个月，JD×3 换算）→ 9,000（8个月，全渠道实测拼图）
  JD 站内 1,416 + 天猫站内 ~927 + 10月大促 ~1,800 + 站外折算 ~3,500-4,800
  观测不确定性 σ 从 800 → 1,400（渠道归因仍有假设成分）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20260426)
N_SIM = 8000
T_MONTHS = 36

# ===== 事前先验（与 backtest_s1.py 一致） =====
m_prior = rng.lognormal(mean=np.log(60_000), sigma=0.80, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

def bass_cum_year(m, p, q, t_year):
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p_target(m, q, target, t, lo0=5e-4, hi0=1.2):
    lo = np.full_like(m, lo0); hi = np.full_like(m, hi0)
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        too_small = bass_cum_year(m, mid, q, t) < target
        lo = np.where(too_small, mid, lo); hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)

t_year = np.arange(1, T_MONTHS + 1) / 12.0

# ===== 事前分布（N 系参数）=====
B_pre = rng.triangular(300_000, 650_000, 1_200_000, size=N_SIM)
CPM_pre = rng.triangular(43, 115, 162, size=N_SIM)
CTR_pre = rng.triangular(0.038, 0.045, 0.064, size=N_SIM)
CVR_pre = rng.triangular(0.013, 0.025, 0.033, size=N_SIM)
s6_pre = np.minimum((B_pre / CPM_pre * 1000) * CTR_pre * CVR_pre, m_prior * 0.55)
p_pre = solve_p_target(m_prior, q_prior, s6_pre, 0.5)
paths_pre = bass_cum_year(m_prior[:, None], p_pre[:, None], q_prior[:, None], t_year[None, :])
y1_pre, y3_pre = paths_pre[:, 11], paths_pre[:, 35]

# ===== 校准 v2：完整观测 =====
OBS_8M = 9_000.0       # 8 个月全渠道（JD 1416 + 天猫 927 + 10月估 1800 + 站外 ~4857 中值）
OBS_SIGMA = 1_400.0    # 归因不确定性

def bass_8m(m, p, q):
    t = 8/12
    return m * (1 - np.exp(-(p+q)*t)) / (1 + (q/p)*np.exp(-(p+q)*t))

p_8m = solve_p_target(m_prior, q_prior, OBS_8M, 8/12)
feasible = (p_8m > 5e-4) & (p_8m < 1.2)
y1_implied = bass_cum_year(m_prior, p_8m, q_prior, 1.0)
# 12 个月外推中心：8 个月 9,000 → 12 个月约 13,500-15,000（Bass 后段 + 大促节奏）
Y1_CENTER = 14_000.0
w = np.exp(-0.5 * ((y1_implied - Y1_CENTER) / 2_100.0) ** 2) * feasible

w_norm = w / w.sum()
post_idx = rng.choice(N_SIM, N_SIM, p=w_norm)
m_post = m_prior[post_idx]
q_post = q_prior[post_idx]
p_post = solve_p_target(m_post, q_post, OBS_8M, 8/12)

paths_post = bass_cum_year(m_post[:, None], p_post[:, None], q_post[:, None], t_year[None, :])
y1_post, y3_post = paths_post[:, 11], paths_post[:, 35]

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=" * 68)
print("S1 Checkpoint 校准 v2 · 完整观测口径（JD+天猫+10月+站外）")
print("=" * 68)
print(f"\n观测（2026-03~10，8 个月）：全渠道 ~{OBS_8M:,.0f} 台")
print(f"  = JD 1,416 + 天猫 ~927 + 10月大促 ~1,800 + 站外折算 ~4,857")
print(f"  （Maggie 口径 ~10,000 首年在区间上半段）")
print(f"\n【事前分布】首年: P5={pct(y1_pre,5):,.0f}  P50={pct(y1_pre,50):,.0f}  P95={pct(y1_pre,95):,.0f}")
print(f"【事后分布】首年: P5={pct(y1_post,5):,.0f}  P50={pct(y1_post,50):,.0f}  P95={pct(y1_post,95):,.0f}")
print(f"\n【事前】三年: P5={pct(y3_pre,5):,.0f}  P50={pct(y3_pre,50):,.0f}  P95={pct(y3_pre,95):,.0f}")
print(f"【事后】三年: P5={pct(y3_post,5):,.0f}  P50={pct(y3_post,50):,.0f}  P95={pct(y3_post,95):,.0f}")
print(f"\n收窄：首年 {(1-(pct(y1_post,95)-pct(y1_post,5))/(pct(y1_pre,95)-pct(y1_pre,5)))*100:.0f}% ｜ 三年 {(1-(pct(y3_post,95)-pct(y3_post,5))/(pct(y3_pre,95)-pct(y3_pre,5)))*100:.0f}%")
print(f"\n内部预测 25,000：事前 P{float((y1_pre<=25000).mean())*100:.0f} → 事后 P{float((y1_post<=25000).mean())*100:.0f}（P(≥25,000)={prob(y1_post,25000)*100:.1f}%）")
print(f"P(事后首年 ≥ 10,000) = {prob(y1_post,10000)*100:.1f}%")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\数据文件\s1_calibration_v2.npz",
         y1_pre=y1_pre, y3_pre=y3_pre, y1_post=y1_post, y3_post=y3_post)
print("\n[saved s1_calibration_v2.npz]")
