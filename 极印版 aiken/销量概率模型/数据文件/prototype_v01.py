# -*- coding: utf-8 -*-
"""
AiKen 销量概率分布模型 · 原型 v0.1（演示用）
三层架构演示：RCF（参数先验） → Bass（结构骨架） → Monte Carlo（分布输出）
杠杆层（投流漏斗）在 v0.2 接入
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

rng = np.random.default_rng(42)

N_SIM = 5000          # 模拟次数
T_HORIZON = 36        # 月份，3 年
YEARS = [12, 24, 36]  # 输出三个时点

# ---------------------------------------------------------------
# 层 1 · RCF 参照类预测——给 Bass 三参数定"先验分布"
#    参照类：国内情感科技硬件首发周期（示意值，正式版将替换为
#    DJI Pocket / instax / 汉印 / Kodak Mini Shot / Flashback 等真实数据）
# ---------------------------------------------------------------
m_prior = rng.lognormal(mean=np.log(60_000), sigma=0.9, size=N_SIM)   # 市场潜力：P50≈6万台，长右尾到百万级
p_prior = np.clip(rng.normal(0.010, 0.004, size=N_SIM), 0.003, 0.03)  # 创新系数：投放驱动，电子消费品典型带
q_prior = np.clip(rng.normal(0.38, 0.12, size=N_SIM), 0.10, 0.75)     # 模仿系数：口碑驱动，社交货币品类典型带

print("=== 层1 · RCF 先验（示意） ===")
print(f"m 市场潜力  : P10={np.percentile(m_prior,10)/1e4:.1f}万  P50={np.percentile(m_prior,50)/1e4:.1f}万  P90={np.percentile(m_prior,90)/1e4:.1f}万")
print(f"p 创新系数  : P10={np.percentile(p_prior,10):.4f}  P50={np.percentile(p_prior,50):.4f}  P90={np.percentile(p_prior,90):.4f}")
print(f"q 模仿系数  : P10={np.percentile(q_prior,10):.2f}  P50={np.percentile(q_prior,50):.2f}  P90={np.percentile(q_prior,90):.2f}")

# ---------------------------------------------------------------
# 层 2 · Bass 扩散——结构骨架
#    N(t) = m · (1 - e^-(p+q)t) / (1 + (q/p)·e^-(p+q)t)
# ---------------------------------------------------------------
def bass_cumulative(m, p, q, t):
    """t 为月份数组，返回累计采纳人数/台数"""
    t = np.atleast_1d(t).astype(float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

# ---------------------------------------------------------------
# 层 3 · Monte Carlo——抽样 5000 次，每次跑一条 Bass 曲线
# ---------------------------------------------------------------
t = np.arange(1, T_HORIZON + 1)
# 形状 (N_SIM, T_HORIZON)
paths = bass_cumulative(m_prior[:, None], p_prior[:, None], q_prior[:, None], t[None, :])

print("\n=== 层2+3 · Bass + Monte Carlo 结果（36 个月累计销量分布） ===")
for yr, months in zip(["第1年", "第2年", "第3年"], YEARS):
    col = paths[:, months - 1]
    print(f"{yr}: P5={np.percentile(col,5)/1e4:.2f}万  P25={np.percentile(col,25)/1e4:.2f}万  "
          f"P50={np.percentile(col,50)/1e4:.2f}万  P75={np.percentile(col,75)/1e4:.2f}万  P95={np.percentile(col,95)/1e4:.2f}万")

# 三档场景对应关系
y1 = paths[:, 11]
print("\n=== 三档场景映射（第 1 年） ===")
print(f"Worst  ≈ P5   : {np.percentile(y1, 5)/1e4:.2f} 万台（红线，原口径月销500→年6000台附近）")
print(f"Normal ≈ P50  : {np.percentile(y1, 50)/1e4:.2f} 万台（原口径月销1000→年1.2万台附近）")
print(f"Best   ≈ P95  : {np.percentile(y1, 95)/1e4:.2f} 万台（原口径月销3000→年3.6万台附近）")

# 关键概率问答——Sean 要的那种读法
print("\n=== 关键概率（第 1 年） ===")
for threshold in [5_000, 10_000, 30_000, 50_000, 100_000]:
    prob = (y1 >= threshold).mean()
    print(f"P(首年销量 ≥ {threshold/1e4:.0f} 万台) = {prob*100:.1f}%")

# 杠杆演示：投放加码（p 提升 50%）对分布的影响
p_boost = np.clip(p_prior * 1.5, 0.003, 0.04)
paths_boost = bass_cumulative(m_prior[:, None], p_boost[:, None], q_prior[:, None], t[None, :])
y1_boost = paths_boost[:, 11]
print("\n=== 杠杆演示：投放加码 → p ×1.5（第 1 年） ===")
print(f"P50: {np.percentile(y1,50)/1e4:.2f}万 → {np.percentile(y1_boost,50)/1e4:.2f}万")
print(f"P(≥10万台): {(y1>=100_000).mean()*100:.1f}% → {(y1_boost>=100_000).mean()*100:.1f}%")
print(f"P(≥3.6万台 Best线): {(y1>=36_000).mean()*100:.1f}% → {(y1_boost>=36_000).mean()*100:.1f}%")
