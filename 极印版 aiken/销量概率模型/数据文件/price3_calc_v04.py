# -*- coding: utf-8 -*-
"""
AiKen 三价位对比 v2 —— 基于 v0.4 校准参数（市场部实测后口径）
与 prototype_v04.py 完全一致的先验；涨价走 CVR 通道（弹性 -1.5 主口径）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261022)
N_SIM = 8000
T_MONTHS = 36

# ===== v0.4 先验（与 prototype_v04.py 一致）=====
m_prior = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)
B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)  # 6 个月媒介
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR0 = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)   # 599 基线

exposure = B_budget / CPM * 1000
clicks = exposure * CTR

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

def run_scenario(cvr_mult):
    cvr = np.clip(CVR0 * cvr_mult, 0.004, 0.026)
    s6 = np.minimum(clicks * cvr, m_prior * 0.55)
    p = solve_p(m_prior, q_prior, s6)
    paths = bass_cum_year(m_prior[:, None], p[:, None], q_prior[:, None], t_year[None, :])
    return paths[:, 11], paths[:, 35]

# 三价位（弹性 -1.5：699→×0.80, 749→×0.72）
y1_599, y3_599 = run_scenario(1.00)
y1_699, y3_699 = run_scenario(0.80)
y1_749, y3_749 = run_scenario(0.72)

# 敏感性：-1.0 / -1.8
sens = {}
for price, elast in [(699, -1.0), (699, -1.8), (749, -1.0), (749, -1.8)]:
    sens[(price, elast)] = run_elasticity = run_scenario((price / 599.0) ** elast)

pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())
W = lambda v: f"{v/1e4:.2f}"

print("=== v0.4 口径 · 首年 P5/P50/P95（万台） ===")
for p, (a, b) in [(599, (y1_599, y3_599)), (699, (y1_699, y3_699)), (749, (y1_749, y3_749))]:
    print(f"¥{p}: 首年 {W(pct(a,5))}/{W(pct(a,50))}/{W(pct(a,95))}   三年 {W(pct(b,50))}")

print("\n=== 敏感性（首年 P50，万台） ===")
for (price, elast), (a, _) in sens.items():
    print(f"¥{price} 弹性{elast}: {W(pct(a,50))}")

# 财务（v0.4 口径：渠道 25% + 销售费用 8%，NRE 630 万）
CH, SR, NRE = 0.25, 0.08, 6_300_000
print("\n=== 财务 ===")
for price, bom, y1, y3 in [(599, 250, y1_599, y3_599), (699, 250, y1_699, y3_699), (699, 280, y1_699, y3_699), (749, 280, y1_749, y3_749)]:
    unit = price * (1 - CH - SR) - bom
    cm3 = y3 * unit; cm1 = y1 * unit
    print(f"¥{price} BOM{bom}: 单台{unit:.0f}元 | 三年贡献P50 {pct(cm3,50)/1e4:.0f}万 | P(三年转正) {prob(cm3-NRE,0)*100:.0f}% | P(首年NRE≥60%) {prob(cm1,0.60*NRE)*100:.0f}% | P(首年≥Normal 1834台/月) {prob(y1, 22009)*100:.0f}%")

# 关键概率
print("\n=== 关键概率 ===")
for p, y1 in [(599, y1_599), (699, y1_699), (749, y1_749)]:
    print(f"¥{p}: P(首年≥2.2万)={prob(y1,22000)*100:.0f}%  P(首年≥3.2万 Best)={prob(y1,32139)*100:.0f}%")

np.savez(r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\price3_results.npz",
         y1_599=y1_599, y1_699=y1_699, y1_749=y1_749,
         y3_599=y3_599, y3_699=y3_699, y3_749=y3_749)
print("\n[npz saved — 供 HTML 脚本使用]")
