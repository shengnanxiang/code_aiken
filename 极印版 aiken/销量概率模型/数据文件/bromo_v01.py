# -*- coding: utf-8 -*-
"""
Bromo 销量概率分布模型 v0.1 —— 移植自 AiKen prototype_v04.py（评审定稿版）
==========================================================
移植原则（2026-11-04，任务 bromo-sales-model）：
  [1] 结构严格忠于 prototype_v04.py 五段：RCF+漏斗先验 → Bass 拼接 → 财务层 → 杠杆 → Checkpoint
  [2] 漏斗参数（CPM/CTR/CVR）整体继承 v0.4（同一投放团队、同类受众，S1 ¥1799 实测锚定）
  [3] Bromo 参数调整仅四处：m 先验（价位渗透）、q 中心上移、预算下修、财务层重构（BOM/NRE 分布化 + 双费用率口径）
  [4] 每处偏离 v0.4 的参数均有业务依据，详见《bromo_v01_结果摘要.md》参数审计表
财务口径：
  ASP = 1299 × 0.975 = 1266.5（含税，渠道混合折算，同 AiKen 487.3/499 之法）
  BOM = 三角(339, 380, 432) = AiKen 250 + 供应链增量 89-182（v03-af-lens §4.1 合计口径，
        含 AF 子系统 10-18：VCM 4-7 + 驱动 IC 1.5-3 + 合焦 LED/声 1-2 + 装配校准 3-6）
  销售费用率双口径：30%（AiKen 对照）vs 25%（Bromo 财务拐点新口径【假设】）
  NRE = 三角(75, 177.06, 216) 万（模式 B 区间，模式点锚 Budget.xlsx estimate-261104；
        镜头 NRE 因 AF 上修为 25-55 万，含于总口径，财务层不单列）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

rng = np.random.default_rng(20261104)
N_SIM = 8000
T_MONTHS = 36

# ============ [1] RCF + 实测先验（Bromo v0.1 口径） ============
# m：价位渗透比推算——1299 vs AiKen 499 客单 2.6 倍，渗透比取 0.41（Instax mini 高低价款
#    分层 + 松典白牌 1000-1500 档年销带 1.5-4 万交叉）；σ 沿用（上探需求 vs 人群收窄方向均不确定）
m_prior = rng.lognormal(mean=np.log(45_000), sigma=0.85, size=N_SIM)
# q：中心 0.42→0.46（社媒晒点更强 + AiKen 先行品类认知），σ 0.10→0.11，clip 同比例上移
q_prior = np.clip(rng.normal(0.46, 0.11, size=N_SIM), 0.20, 0.72)

# 预算：财务拐点纪律 + 阵列联合投放摊薄 → P50 155万→120万（-23%）【假设】
B_budget = rng.triangular(600_000, 1_200_000, 2_000_000, size=N_SIM)  # 6 个月
# 漏斗三参数整体继承 v0.4（同一投放团队/同类受众；S1 ¥1799 实测对 ¥1299 品仍偏保守方向）
CPM = rng.triangular(38, 45, 65, size=N_SIM)
CTR = rng.triangular(0.018, 0.023, 0.030, size=N_SIM)
CVR = rng.triangular(0.009, 0.014, 0.022, size=N_SIM)

exposure = B_budget / CPM * 1000
clicks = exposure * CTR
s6_raw = clicks * CVR
s6 = np.minimum(s6_raw, m_prior * 0.55)

# ============ [2] Bass 拼接（结构同 v0.4） ============
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
print("Bromo 销量概率分布模型 v0.1（1299 定价）· %d 次模拟" % N_SIM)
print("=" * 66)
print(f"\n【漏斗参数 v0.1（继承 v0.4）】")
print(f"  CPM: 三角(38,45,65) P50={pct(CPM,50):.0f}  ← 继承 v0.4（同投放团队/受众）")
print(f"  CTR: 三角(1.8%,2.3%,3.0%) P50={pct(CTR,50)*100:.2f}%  ← 继承")
print(f"  CVR: 三角(0.9%,1.4%,2.2%) P50={pct(CVR,50)*100:.2f}%  ← 继承（S1 ¥1799 实测锚定对 1299 仍保守）")
print(f"  预算(6月): 三角(60,120,200)万 P50={pct(B_budget,50)/1e4:.0f}万  ← 财务拐点纪律下修 23%【假设】")
print(f"  m 先验: lognormal(4.5万, σ0.85)  ← AiKen 11万 × 渗透比 0.41【假设】")
print(f"  q 先验: N(0.46,0.11) clip[0.20,0.72]  ← v0.4 中心 +0.04【假设】")

print(f"\n【首年销量分布】")
print(f"  P5={pct(y1,5):,.0f}  P10={pct(y1,10):,.0f}  P25={pct(y1,25):,.0f}  P50={pct(y1,50):,.0f}  P75={pct(y1,75):,.0f}  P90={pct(y1,90):,.0f}  P95={pct(y1,95):,.0f}")
print(f"\n【三年累计】")
print(f"  P5={pct(y3,5):,.0f}  P10={pct(y3,10):,.0f}  P25={pct(y3,25):,.0f}  P50={pct(y3,50):,.0f}  P75={pct(y3,75):,.0f}  P90={pct(y3,90):,.0f}  P95={pct(y3,95):,.0f}")

print(f"\n【三档锚（P10/P50/P90）】")
print(f"  Worst=P10: 首年 {pct(y1,10):,.0f}（月销≈{pct(y1,10)/12:,.0f}）  三年 {pct(y3,10):,.0f}")
print(f"  Normal=P50: 首年 {pct(y1,50):,.0f}（月销≈{pct(y1,50)/12:,.0f}）  三年 {pct(y3,50):,.0f}")
print(f"  Best=P90: 首年 {pct(y1,90):,.0f}（月销≈{pct(y1,90)/12:,.0f}）  三年 {pct(y3,90):,.0f}")

print(f"\n【关键概率】")
for th in [5_000, 10_000, 30_000]:
    print(f"  P(首年≥{th:,})={prob(y1,th)*100:.1f}%")
for th in [30_000, 50_000, 100_000]:
    print(f"  P(三年≥{th:,})={prob(y3,th)*100:.1f}%")

# ============ [3] 财务层（双口径：30% 对照 vs 25% 财务拐点） ============
ASP_TAXINC = 1266.5          # 1299 × 0.975（官旗/渠道/线下混合折算，同 AiKen 487.3/499 之法）
ASP_NOTAX = ASP_TAXINC / 1.13
# BOM 分布：AiKen 250 + 供应链增量 89-182（v03-af-lens §4.1 合计口径；AF 子系统 10-18：
#           VCM 开环 4-7 + 驱动 IC 1.5-3 + 合焦 LED/声 1-2 + 装配校准测试 3-6，
#           产品负责人 2026-11-04 拍板 AF + 单一等效 35mm 焦段）→ 三角(339, 380, 432)
BOM_TRI = rng.triangular(339.0, 380.0, 432.0, size=N_SIM)
# NRE 分布：【假设】模式 B 区间 75-216 万（任务口径 75-470 万弹性区间按模式 B 下限建模），
#           模式点锚 Budget.xlsx 177.06 万（estimate-261104）；镜头 NRE 因 AF 上修 25-55 万（v03-af-lens），含于总口径
NRE_TRI = rng.triangular(750_000.0, 1_770_600.0, 2_160_000.0, size=N_SIM)

cm_a = ASP_NOTAX * (1 - 0.30) - BOM_TRI   # 口径 A：AiKen 30% 对照
cm_b = ASP_NOTAX * (1 - 0.25) - BOM_TRI   # 口径 B：Bromo 财务拐点 25%【假设】

print(f"\n【财务层 v0.1（ASP 含税 1266.5 / 不含税 {ASP_NOTAX:.1f} · BOM 三角(339,380,432)（v03-af-lens §4.1：增量 89-182 含 AF 10-18）· NRE 三角(75,177,216)万【假设】）】")
for tag, cm in [("口径A·30%费用率（AiKen 对照）", cm_a), ("口径B·25%费用率（财务拐点）【假设】", cm_b)]:
    y1_cm = y1 * cm; inv_cov = y1_cm / NRE_TRI
    y3_cm = y3 * cm; pnl3 = y3_cm - NRE_TRI
    print(f"\n  -- {tag} --")
    print(f"  单台净贡献: P50={pct(cm,50):.0f} 元（P10-P90: {pct(cm,10):.0f} ~ {pct(cm,90):.0f}）")
    print(f"  首年NRE覆盖率三档: Worst {pct(inv_cov,10)*100:.0f}% | Normal {pct(inv_cov,50)*100:.0f}% | Best {pct(inv_cov,90)*100:.0f}%")
    print(f"  P(首年覆盖≥100%)={prob(inv_cov,1.0)*100:.1f}%  P(三年转正)={prob(pnl3,0)*100:.1f}%")

# BOM 敏感性（v03-af-lens §4.1 增量下限 89 vs 上限 182；任务口径 79-164 vs 164（164=供应链 79-164 上限）对照）
print(f"\n【BOM 敏感性（增量下限 vs 上限）】")
for tag, bom_lo, bom_hi in [("供应链v0.2口径(不含AF): 329 / 414", 329.0, 414.0), ("v03-af-lens口径(含AF): 339 / 432", 339.0, 432.0)]:
    print(f"  {tag}")
    print(f"    30%口径: 单台净贡献 {ASP_NOTAX*0.70-bom_lo:.0f} ~ {ASP_NOTAX*0.70-bom_hi:.0f} 元")
    print(f"    25%口径: 单台净贡献 {ASP_NOTAX*0.75-bom_lo:.0f} ~ {ASP_NOTAX*0.75-bom_hi:.0f} 元")

# ============ [4] 杠杆（预算 ×1.5） ============
s6_b = np.minimum(s6_raw * 1.5, m_prior * 0.55)
p_b = solve_p(m_prior, q_prior, s6_b)
paths_b = bass_cum_year(m_prior[:, None], p_b[:, None], q_prior[:, None], t_year[None, :])
y1_b = paths_b[:, 11]; y3_b = paths_b[:, 35]
best_line = pct(y1, 90)
print(f"\n【杠杆：预算 ×1.5（P50 120万→180万）】")
print(f"  首年 P50 {pct(y1,50):,.0f}→{pct(y1_b,50):,.0f}  P(≥Best {best_line:,.0f}) {prob(y1,best_line)*100:.0f}%→{prob(y1_b,best_line)*100:.0f}%")
print(f"  P(首年≥1万) {prob(y1,10_000)*100:.0f}%→{prob(y1_b,10_000)*100:.0f}%  P(三年≥5万) {prob(y3,50_000)*100:.0f}%→{prob(y3_b,50_000)*100:.0f}%")

# 与 AiKen v0.4 对照
print(f"\n【AiKen v0.4 对照】")
print(f"  首年 P50: 22,009 → {pct(y1,50):,.0f}（{pct(y1,50)/22009:.2f}×）")
print(f"  首年 P10: 14,300 → {pct(y1,10):,.0f}（{pct(y1,10)/14300:.2f}×）")
print(f"  首年 P90: 32,139 → {pct(y1,90):,.0f}（{pct(y1,90)/32139:.2f}×）")
print(f"  三年 P50: 63,130 → {pct(y3,50):,.0f}（{pct(y3,50)/63130:.2f}×）")

# ============ [5] Checkpoint 演示 ============
print(f"\n【Checkpoint 收窄演示（30 天观测 = Normal 月销）】")
s30_obs = pct(y1, 50) / 12
p_hat, q_hat = pct(p_solved, 50), pct(q_prior, 50)
m_grid = np.linspace(10_000, 200_000, 300)
f1 = bass_cum_year(1.0, p_hat, q_hat, 1.0 / 12.0)
mu = m_grid * f1
like = np.exp(-0.5 * ((s30_obs - mu) / (0.35 * mu + 30)) ** 2)
prior_pdf = np.exp(-0.5 * (np.log(m_grid / 45_000) / 0.85) ** 2) / m_grid
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
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\bromo_v01_results.npz",
    y1=y1, y3=y3, paths=paths, m_prior=m_prior, q_prior=q_prior, p_solved=p_solved,
    s6=s6, y1_b=y1_b, y3_b=y3_b, BOM_TRI=BOM_TRI, NRE_TRI=NRE_TRI,
    cm_a=cm_a, cm_b=cm_b, best_line=best_line,
)
print("\n[Saved] bromo_v01_results.npz")
