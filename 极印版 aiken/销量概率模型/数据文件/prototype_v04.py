# -*- coding: utf-8 -*-
"""
AiKen 销量概率分布模型 v0.4 —— 评审定稿版
==========================================
v0.3b → v0.4 变更（2026-10-27 用户三项拍板）：
  [1] CPM 加宽带宽：三角(38, 45, 65)——覆盖 AiKen 早期投放低效溢价（方案A）
  [2] m 先验保持外部参照（S1 对比作现实检验展示，不混入先验）
  [3] CVR 下界留余量：三角(0.009, 0.014, 0.022)——S1 回测教训（CVR 可低于参照带下界）
财务口径：销售费用率 30%（Maggie 对齐）；投资 413.8 万；ASP 按渠道混合 487.3（含税）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261027)
N_SIM = 8000
T_MONTHS = 36

# ============ [1] RCF + 实测先验（v0.4 口径） ============
m_prior = rng.lognormal(mean=np.log(110_000), sigma=0.85, size=N_SIM)
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

B_budget = rng.triangular(800_000, 1_550_000, 2_400_000, size=N_SIM)  # 6 个月
CPM = rng.triangular(38, 45, 65, size=N_SIM)          # 加宽带宽（S1 站外 37.6 / 站内 45.2 / 低效溢价余量）
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM) # S1 实测 2.14%
CVR = rng.triangular(0.009, 0.014, 0.022, size=N_SIM) # S1 0.98% + 回测余量

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

# ============ [2] Bass 拼接 ============
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
print("AiKen 销量概率分布模型 v0.4（评审定稿）· %d 次模拟" % N_SIM)
print("=" * 66)
print(f"\n【漏斗参数 v0.4】")
print(f"  CPM: 三角(38,45,65) P50={pct(CPM,50):.0f}  ← 加宽带宽")
print(f"  CVR: 三角(0.9%,1.4%,2.2%) P50={pct(CVR,50)*100:.2f}%  ← S1 回测余量")
print(f"  CTR: 三角(1.8%,2.3%,3.0%) P50={pct(CTR,50)*100:.2f}%")
print(f"  预算(6月): P50={pct(B_budget,50)/1e4:.0f}万")

print(f"\n【首年销量分布】")
print(f"  P5={pct(y1,5):,.0f}  P10={pct(y1,10):,.0f}  P25={pct(y1,25):,.0f}  P50={pct(y1,50):,.0f}  P75={pct(y1,75):,.0f}  P90={pct(y1,90):,.0f}  P95={pct(y1,95):,.0f}")
print(f"\n【三年累计】")
print(f"  P5={pct(y3,5):,.0f}  P10={pct(y3,10):,.0f}  P50={pct(y3,50):,.0f}  P90={pct(y3,90):,.0f}  P95={pct(y3,95):,.0f}")

print(f"\n【三档锚（P10/P50/P90）】")
print(f"  Worst=P10: 首年 {pct(y1,10):,.0f}（月销≈{pct(y1,10)/12:,.0f}）")
print(f"  Normal=P50: 首年 {pct(y1,50):,.0f}（月销≈{pct(y1,50)/12:,.0f}）")
print(f"  Best=P90: 首年 {pct(y1,90):,.0f}（月销≈{pct(y1,90)/12:,.0f}）")

print(f"\n【关键概率】")
for th in [10_000, 26_400, 37_200, 50_000, 100_000]:
    print(f"  P(首年≥{th/1e4:.1f}万)={prob(y1,th)*100:.1f}%   P(三年≥{th/1e4:.0f}万)={prob(y3,th)*100:.1f}%")

# ============ [3] 财务层（30% 销售费用 + 413.8 万投资 + 渠道混合 ASP） ============
# ASP：线上官旗 65%×0.85折 + 线上渠道 30%×0.75折 + 线下 5%×0.72折 = 487.29（含税）
ASP_TAXINC = 487.29
BOM = 250.0
SALES_RATE = 0.30
# 不含税口径：487.29/1.13 ≈ 431.22（Excel BOM&ASP sheet 验证一致）
ASP_NOTAX = ASP_TAXINC / 1.13
# 净贡献/台（不含税口径，扣 BOM + 销售费用；渠道折扣已含在 ASP 混合中）
cm_unit = ASP_NOTAX * (1 - SALES_RATE) - BOM
INVEST = 4_138_050

y1_cm = y1 * cm_unit
inv_cov = y1_cm / INVEST
y3_cm = y3 * cm_unit
pnl3 = y3_cm - INVEST

print(f"\n【财务层 v0.4（销售费用 30% · 投资 413.8 万 · 混合 ASP）】")
print(f"  单台净贡献: {cm_unit:.1f} 元（ASP不含税 {ASP_NOTAX:.1f} × 70% - BOM 250）")
print(f"  三档投入覆盖: Worst {pct(inv_cov,10)*100:.0f}% | Normal {pct(inv_cov,50)*100:.0f}% | Best {pct(inv_cov,90)*100:.0f}%")
print(f"  P(首年覆盖≥100%)={prob(inv_cov,1.0)*100:.1f}%  P(三年转正)={prob(pnl3,0)*100:.1f}%")

# ============ [4] 杠杆（预算 ×1.5） ============
s6_b = np.minimum(s6_raw * 1.5, m_prior * 0.55)
p_b = solve_p(m_prior, q_prior, s6_b)
paths_b = bass_cum_year(m_prior[:, None], p_b[:, None], q_prior[:, None], t_year[None, :])
y1_b = paths_b[:, 11]; y3_b = paths_b[:, 35]
best_line = pct(y1, 90)
print(f"\n【杠杆：预算 ×1.5（P50 155万→230万）】")
print(f"  首年 P50 {pct(y1,50):,.0f}→{pct(y1_b,50):,.0f}  P(≥Best {best_line:,.0f}) {prob(y1,best_line)*100:.0f}%→{prob(y1_b,best_line)*100:.0f}%")

# v0.3b 对照
print(f"\n【v0.3b → v0.4】")
print(f"  首年 P50: 26,348 → {pct(y1,50):,.0f}")
print(f"  首年 P10: 17,513 → {pct(y1,10):,.0f}")
print(f"  首年 P90: 37,643 → {pct(y1,90):,.0f}")
print(f"  三年 P50: 71,179 → {pct(y3,50):,.0f}")

# ============ [5] Checkpoint 演示 ============
print(f"\n【Checkpoint 收窄演示（30 天观测 = Normal 月销）】")
s30_obs = pct(y1, 50) / 12
p_hat, q_hat = pct(p_solved, 50), pct(q_prior, 50)
m_grid = np.linspace(30_000, 400_000, 300)
f1 = bass_cum_year(1.0, p_hat, q_hat, 1.0 / 12.0)
mu = m_grid * f1
like = np.exp(-0.5 * ((s30_obs - mu) / (0.35 * mu + 30)) ** 2)
prior_pdf = np.exp(-0.5 * (np.log(m_grid / 110_000) / 0.85) ** 2) / m_grid
post = prior_pdf * like
post /= np.trapezoid(post, m_grid)
prior_n = prior_pdf / np.trapezoid(prior_pdf, m_grid)

def grid_stats(pdf, g):
    cdf = np.cumsum(pdf) * (g[1] - g[0])
    cdf /= cdf[-1]
    qv = lambda q_: float(g[np.searchsorted(cdf, q_)])
    return qv(0.10), qv(0.5), qv(0.90)

pre = grid_stats(prior_n, m_grid)
post_s = grid_stats(post, m_grid)
print(f"  观测首月 {s30_obs:,.0f} 台 → m 区间 P10-P90: {pre[0]/1e4:.1f}万-{pre[2]/1e4:.1f}万 → {post_s[0]/1e4:.1f}万-{post_s[2]/1e4:.1f}万（宽度收窄 {(1-(post_s[2]-post_s[0])/(pre[2]-pre[0]))*100:.0f}%）")

np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v04_results.npz",
    y1=y1, y3=y3, paths=paths, m_prior=m_prior, q_prior=q_prior, p_solved=p_solved,
    s6=s6, y1_b=y1_b, y3_b=y3_b, inv_cov=inv_cov, pnl3=pnl3,
    cm_unit=cm_unit, best_line=best_line,
)
print("\n[Saved] v04_results.npz")
