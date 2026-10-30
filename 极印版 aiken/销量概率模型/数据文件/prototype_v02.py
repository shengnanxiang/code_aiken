# -*- coding: utf-8 -*-
"""
AiKen 销量概率分布模型 v0.2
================================
模块：
  [1] RCF 参照类先验（公开数据校准 + 极印基线占位）
  [2] 投流漏斗层（前 6 个月，预算驱动）
  [3] Bass 扩散（拼接：漏斗钉住冷启动 p，Bass 管尾部）
  [4] 蒙特卡洛 → 销量分布
  [5] 财务输出层（毛利 / NRE 覆盖 / 亏损概率）
  [6] Checkpoint 贝叶斯更新演示（30 天数据进来后分布如何收窄）

依赖：numpy（无需 scipy）
用法：python prototype_v02.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

rng = np.random.default_rng(20261022)

N_SIM = 8000
T_MONTHS = 36

# =================================================================
# [1] RCF 参照类先验
# -----------------------------------------------------------------
# 公开参照数据（调研于 2026-10-22）：
#   · DJI Osmo Pocket 3 (¥3499)：发布前内部预期 30–40 万台，
#     上市后上调至 100 万，2024 实际售出 ~500 万台，累计破千万
#     ——「预期被实际打穿 10 倍+」的品类爆冷案例 → 支撑右尾保留
#   · 富士 instax：全球年销从 2004 年 10 万台增长至 2019 年 1000 万台
#     ——品类天花板参照（AiKen 若成「instax 平替」，中国盘 100 万级）
#   · Flashback One35 (¥749)：Kickstarter 众筹 $80 万（约 6-7 千台首单），
#     三年全球累计拍摄 1000 万张照片（估算用户 5–10 万）
#     ——最接近 AiKen 的直接对标，小众存活的基准带
#   · Kodak Mini Shot 3 Retro (¥1269)：国内电商年销约 1–3 万台
#     ——授权品牌中游带的基准
#   · CCD 复古潮：小红书相关笔记 165 万+条，抖音复古摄影器材年销
#     7500 万元 (+170% YoY)；撕拉片单张炒到 ¥400+
#     ——需求侧信号：该品类口碑传染系数 q 偏高，m 有爆发的文化土壤
#   · 极印自有基线（占位，待市场部数据校准）：
#     薇娅直播 6600 台/5min（2020，口碑脉冲证据）；
#     Perella 双十一 4 小时 200+ 台；打印机线年销约 2–3 万台
# =================================================================

# --- m 市场潜力（36 个月中国累计，台）---
# lognormal：P50=12万，sigma=0.9 → P(≥100万)≈1.7%（Sean 的上限以小概率显式保留）
m_prior = rng.lognormal(mean=np.log(120_000), sigma=0.90, size=N_SIM)

# --- q 模仿/口碑系数（年口径）---
# 品类典型带 0.28–0.55；CCD/instax 型社交传染支持中高位
q_prior = np.clip(rng.normal(0.42, 0.10, size=N_SIM), 0.18, 0.68)

# =================================================================
# [2] 投流漏斗层（前 6 个月）
# =================================================================
# 预算（6 个月媒介，万元）——占位：120–280 万，待市场部确认
B_budget = rng.uniform(120, 280, size=N_SIM) * 10_000          # 元
CPM = rng.triangular(45, 60, 75, size=N_SIM)                   # 元/千次曝光
CTR = rng.triangular(0.015, 0.022, 0.035, size=N_SIM)          # 点击率
CVR = rng.triangular(0.012, 0.018, 0.028, size=N_SIM)          # 落地页转化率

exposure = B_budget / CPM * 1000                                # 曝光次数
clicks = exposure * CTR
s6_raw = clicks * CVR                                           # 前 6 个月漏斗销量（未设上限）

# 潜力上限约束：前 6 个月最多吃掉 m 的 55%（认知渗透的物理约束）
s6 = np.minimum(s6_raw, m_prior * 0.55)

# =================================================================
# [3] Bass 扩散（漏斗钉住冷启动）
# =================================================================
def bass_cum_year(m, p, q, t_year):
    """Bass 累计采纳（t 单位：年）。m/p/q 同形状数组或标量。"""
    t = np.asarray(t_year, dtype=float)
    denom = 1 + (q / p) * np.exp(-(p + q) * t)
    return m * (1 - np.exp(-(p + q) * t)) / denom

def solve_p(m, q, s6_target):
    """二分法解 p：使 Bass 累计(0.5 年) = s6_target。逐样本向量化。"""
    lo = np.full_like(m, 1e-5)
    hi = np.full_like(m, 1.2)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        val = bass_cum_year(m, mid, q, 0.5)
        too_small = val < s6_target
        lo = np.where(too_small, mid, lo)
        hi = np.where(too_small, hi, mid)
    return 0.5 * (lo + hi)

p_solved = solve_p(m_prior, q_prior, s6)

# 完整 36 个月轨迹（月 → 年 = /12）
t_year = np.arange(1, T_MONTHS + 1) / 12.0
paths = bass_cum_year(m_prior[:, None], p_solved[:, None], q_prior[:, None], t_year[None, :])

y1 = paths[:, 11]    # 首年累计
y3 = paths[:, 35]    # 三年累计

# =================================================================
# [4] 分布统计
# =================================================================
pct = lambda a, q_: float(np.percentile(a, q_))
prob = lambda a, th: float((a >= th).mean())

print("=" * 64)
print("AiKen 销量概率分布模型 v0.2 · 蒙特卡洛结果（%d 次模拟）" % N_SIM)
print("=" * 64)

print("\n【参照类先验】")
print(f"  m 市场潜力(3年): P10={pct(m_prior,10)/1e4:.1f}万  P50={pct(m_prior,50)/1e4:.1f}万  P90={pct(m_prior,90)/1e4:.1f}万  P(≥100万)={prob(m_prior,1_000_000)*100:.1f}%")
print(f"  q 口碑系数(年) : P10={pct(q_prior,10):.2f}  P50={pct(q_prior,50):.2f}  P90={pct(q_prior,90):.2f}")
print(f"  漏斗(6个月)    : 预算P50={pct(B_budget,50)/1e4:.0f}万  曝光P50={pct(exposure,50)/1e6:.0f}M  点击P50={pct(clicks,50)/1e4:.0f}万  S6销量P50={pct(s6,50)/1e4:.2f}万")

print("\n【首年销量分布】")
print(f"  P5 ={pct(y1,5)/1e4:.2f}万   P25={pct(y1,25)/1e4:.2f}万   P50={pct(y1,50)/1e4:.2f}万   P75={pct(y1,75)/1e4:.2f}万   P95={pct(y1,95)/1e4:.2f}万")

print("\n【会议三档场景在新分布中的位置】")
for name, v in [("Worst 月销500→年6000", 6_000), ("Normal 月销1000→年1.2万", 12_000), ("Best 月销3000→年3.6万", 36_000)]:
    pos = pct(y1, 0)  # placeholder
    cdf = float((y1 <= v).mean()) * 100
    print(f"  {name}: 位于 P{cdf:.0f} 分位")

print("\n【关键概率（首年）】")
for th in [5_000, 12_000, 36_000, 100_000, 1_000_000]:
    print(f"  P(首年 ≥ {th/1e4:.0f}万) = {prob(y1, th)*100:.1f}%")

print("\n【三年累计销量】")
print(f"  P5={pct(y3,5)/1e4:.2f}万  P50={pct(y3,50)/1e4:.2f}万  P95={pct(y3,95)/1e4:.2f}万")

# =================================================================
# [5] 财务输出层（占位参数，待市场部/财务确认）
# =================================================================
PRICE = 599.0          # 定价
BOM = 250.0            # BOM+加工（MOQ 3000 批次口径）
CH_RATE = 0.25         # 渠道费用率（含平台扣点+物流，占售价）
SALES_RATE = 0.08      # 销售费用率占位（会上说 2% 不够，待 Maggie/方明）
NRE_REMAIN = 6_300_000 # 剩余 NRE（660 万 - 30 万已发生沉没）

gm_unit = PRICE - BOM                      # 出厂毛利 349
cm_unit = PRICE * (1 - CH_RATE - SALES_RATE) - BOM   # 净贡献/台 ≈ 151

y1_gm = y1 * gm_unit
y1_cm = y1 * cm_unit
nre_cov_y1 = y1_cm / NRE_REMAIN            # 首年 NRE 覆盖进度
y3_cm = y3 * cm_unit
cum_pnl_3y = y3_cm - NRE_REMAIN            # 三年累计净贡献（不含沉没）

print("\n【财务层（占位参数）】")
print(f"  单台出厂毛利 {gm_unit:.0f} 元 ｜ 单台净贡献(扣渠道+销售费用) {cm_unit:.0f} 元")
print(f"  首年净贡献: P5={pct(y1_cm,5)/1e4:.0f}万  P50={pct(y1_cm,50)/1e4:.0f}万  P95={pct(y1_cm,95)/1e4:.0f}万")
print(f"  首年 NRE 覆盖进度: P5={pct(nre_cov_y1,5)*100:.0f}%  P50={pct(nre_cov_y1,50)*100:.0f}%  P95={pct(nre_cov_y1,95)*100:.0f}%  （策略文档目标: 12个月 ≥60%）")
print(f"  P(首年 NRE 覆盖 ≥60%) = {prob(nre_cov_y1, 0.60)*100:.1f}%")
print(f"  三年累计净贡献(不含沉没): P5={pct(cum_pnl_3y,5)/1e4:.0f}万  P50={pct(cum_pnl_3y,50)/1e4:.0f}万  P95={pct(cum_pnl_3y,95)/1e4:.0f}万")
print(f"  P(三年累计转正) = {prob(cum_pnl_3y, 0)*100:.1f}%")
print(f"  P(三年累计亏损 > 200万) = {float((cum_pnl_3y < -2_000_000).mean())*100:.1f}%")
print("  ⚠ 对齐待办：会议口径 Worst/Normal/Best 毛利 0.05/0.88/4.41（单位与是否含")
print("    耗材生态待确认）——需拿到现有财务测算表后对表校准。")

# =================================================================
# [6] Checkpoint 贝叶斯更新演示（30 天数据进来后）
# =================================================================
print("\n【Checkpoint 演示：上市 30 天真实数据 → 分布收窄】")
# 假设 30 天实际销量（演示值：Normal 附近，月销 1100 台）
s30_obs = 1_100

# 网格贝叶斯更新 m（p/q 取后验中位数近似）
p_hat, q_hat = pct(p_solved, 50), pct(q_prior, 50)
m_grid = np.linspace(20_000, 400_000, 300)
f1 = bass_cum_year(1.0, p_hat, q_hat, 1.0 / 12.0)  # 首月采纳比例（标量）
mu = m_grid * f1
like = np.exp(-0.5 * ((s30_obs - mu) / (0.35 * mu + 30)) ** 2)
prior_pdf = np.exp(-0.5 * (np.log(m_grid / 120_000) / 0.90) ** 2) / m_grid
post = prior_pdf * like
post /= np.trapezoid(post, m_grid)
prior_n = prior_pdf / np.trapezoid(prior_pdf, m_grid)

def grid_stats(pdf, g):
    cdf = np.cumsum(pdf) * (g[1] - g[0])
    cdf /= cdf[-1]
    def qv(q_):
        return float(g[np.searchsorted(cdf, q_)])
    return qv(0.05), qv(0.5), qv(0.95)

pre = grid_stats(prior_n, m_grid)
post_s = grid_stats(post, m_grid)
print(f"  观测：首月销量 {s30_obs} 台（≈Normal 场景）")
print(f"  m 先验   : P5={pre[0]/1e4:.1f}万  P50={pre[1]/1e4:.1f}万  P95={pre[2]/1e4:.1f}万  （宽度 {(pre[2]-pre[0])/1e4:.0f}万）")
print(f"  m 后验   : P5={post_s[0]/1e4:.1f}万  P50={post_s[1]/1e4:.1f}万  P95={post_s[2]/1e4:.1f}万  （宽度 {(post_s[2]-post_s[0])/1e4:.0f}万）")
print(f"  → 不确定性宽度收窄 {(1-(post_s[2]-post_s[0])/(pre[2]-pre[0]))*100:.0f}%；90 天 checkpoint 同理再收一轮")

# =================================================================
# 保存关键结果供图表脚本使用
# =================================================================
np.savez(
    r"C:\Users\Nan\Documents\GitHub\code_aiken\极印版 aiken\销量概率模型\v02_results.npz",
    y1=y1, y3=y3, paths=paths, m_prior=m_prior, q_prior=q_prior,
    p_solved=p_solved, s6=s6, y1_cm=y1_cm, nre_cov_y1=nre_cov_y1, cum_pnl_3y=cum_pnl_3y,
    m_grid=m_grid, prior_n=prior_n, post=post, s30_obs=s30_obs,
)
print("\n[Saved] v02_results.npz")
